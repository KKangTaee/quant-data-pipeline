from __future__ import annotations

import json

import os

import re

import urllib.request

from collections.abc import Callable, Sequence

from datetime import date, datetime, timezone, timedelta

from html import unescape

from typing import Any

from urllib.parse import quote, quote_plus, urlencode, urlparse

from xml.etree import ElementTree

import pandas as pd

from finance.loaders.sentiment import (
    CNN_COMPONENT_SERIES,
    CORE_SENTIMENT_SERIES,
    load_market_sentiment_history,
    load_market_sentiment_snapshot,
)

QueryFn = Callable[[str, str, Sequence[Any] | None], list[dict[str, Any]]]

VALID_PERIODS = {"daily": 1, "weekly": 5, "monthly": 21, "yearly": 252}

PERIOD_LABELS = {"daily": "Daily", "weekly": "Weekly", "monthly": "Monthly", "yearly": "Yearly"}

VALID_GROUPS = {"sector", "industry"}

GROUP_TREND_PERIODS = {
    "daily": {"step": 1, "windows": 21, "window_label": "Last 1M"},
    "weekly": {"step": 5, "windows": 13, "window_label": "Last 3M"},
    "monthly": {"step": 21, "windows": 12, "window_label": "Last 12M"},
}

MARKET_INTRADAY_REFRESH_MINUTES = 5

MARKET_INTRADAY_STALE_MINUTES = 15

UNIVERSE_LABELS = {
    "SP500": "S&P 500",
    "TOP1000": "Top 1000 by market cap",
    "TOP2000": "Top 2000 by market cap",
    "NASDAQ": "Nasdaq-listed current snapshot",
}

MOVERS_COLUMNS = [
    "Rank",
    "Symbol",
    "Name",
    "Return %",
    "Previous Return %",
    "Momentum Delta pp",
    "Volume",
    "Dollar Volume",
    "Start Price",
    "End Price",
    "Sector",
    "Industry",
    "Market Cap",
    "Start Date",
    "End Date",
    "Previous Start Date",
    "Previous End Date",
    "Price Source",
]

VOLUME_COLUMNS = [
    "Rank",
    "Symbol",
    "Name",
    "Volume Metric",
    "Volume Basis",
    "Volume",
    "Dollar Volume",
    "Avg Daily Volume",
    "Total Volume",
    "Avg Daily Dollar Volume",
    "Total Dollar Volume",
    "Volume Days",
    "Return %",
    "Sector",
    "Industry",
    "Market Cap",
    "Start Date",
    "End Date",
    "Price Source",
]

UNUSUAL_VOLUME_COLUMNS = [
    "Rank",
    "Symbol",
    "Name",
    "Relative Volume",
    "Current Volume",
    "Avg 10D Volume",
    "Baseline Days",
    "Volume Basis",
    "Return %",
    "Sector",
    "Industry",
    "Market Cap",
    "Start Date",
    "End Date",
    "Price Source",
]

MISSING_COLUMNS = [
    "Symbol",
    "Name",
    "Sector",
    "Industry",
    "Reason",
    "Recommended Action",
    "Likely Cause",
    "Evidence Summary",
    "Next Check",
    "Listing Evidence",
    "Profile Freshness",
    "Market Data Issue",
    "Start Date",
    "End Date",
    "Start Price",
    "End Price",
    "Latest Price Date",
    "Profile Status",
    "Profile Error",
    "Profile Collected At",
]

GROUP_COLUMNS = [
    "Rank",
    "Group",
    "Group Type",
    "Symbols",
    "Positive Symbols",
    "Positive Symbol Share %",
    "Equal Weight Return %",
    "Market Cap Weighted Return %",
    "Cap vs Equal Gap pp",
    "Top 3 Positive Share %",
    "Top Symbol",
    "Top Symbol Return %",
    "Start Date",
    "End Date",
]

GROUP_TREND_COLUMNS = [
    "Date",
    "Group",
    "Group Type",
    "Symbols",
    "Equal Weight Return %",
    "Market Cap Weighted Return %",
    "Top Symbol",
    "Top Symbol Return %",
    "Start Date",
    "End Date",
]

GROUP_TICKER_LEADER_COLUMNS = [
    "Group",
    "Group Type",
    "Rank",
    "Symbol",
    "Name",
    "Return %",
    "Previous Return %",
    "Momentum Delta pp",
    "Positive Return Share %",
    "Sector",
    "Industry",
    "Market Cap",
    "Start Price",
    "End Price",
    "Start Date",
    "End Date",
    "Previous Start Date",
    "Previous End Date",
]

SECTOR_BREADTH_TABLE_COLUMNS = [
    "Rank",
    "Sector",
    "Symbols",
    "Advancers",
    "Decliners",
    "Advancer Share %",
    "Equal Weight Return %",
    "Median Return %",
    "Market Cap Weighted Return %",
    "Market Cap Share %",
    "Top Gainer",
    "Top Gainer Return %",
    "Top Loser",
    "Top Loser Return %",
    "Start Date",
    "End Date",
]

MOVER_VIEW_MODE_ORDER = [
    "top_gainers",
    "top_losers",
    "volume_leaders",
    "unusual_volume",
    "sector_leaders",
]

MOVER_VIEW_LABELS = {
    "top_gainers": "Top Gainers",
    "top_losers": "Top Losers",
    "volume_leaders": "Volume Leaders",
    "unusual_volume": "Unusual Volume",
    "sector_leaders": "Sector Leaders",
}

MOVER_VIEW_BOUNDARY_NOTE = (
    "Context-only ranking view: not a trading signal, recommendation, validation gate, "
    "Final Review decision, or monitoring signal."
)

def _default_query(db_name: str, sql: str, params: Sequence[Any] | None = None) -> list[dict[str, Any]]:
    import pymysql

    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="1234",
        port=3306,
        charset="utf8mb4",
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            cur.execute(f"USE {db_name}")
            cur.execute(sql, params)
            return list(cur.fetchall())
    finally:
        conn.close()

def _safe_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(numeric):
        return None
    return numeric

def _iso_date(value: Any) -> str | None:
    if value in (None, ""):
        return None
    ts = pd.Timestamp(value)
    if pd.isna(ts):
        return None
    return ts.strftime("%Y-%m-%d")

def _display_datetime(value: Any) -> str | None:
    if value in (None, ""):
        return None
    ts = pd.Timestamp(value)
    if pd.isna(ts):
        return None
    return ts.strftime("%Y-%m-%d %H:%M")

def _stale_days(effective_date: str | None, *, today: date | None = None) -> int | None:
    if not effective_date:
        return None
    today_value = pd.Timestamp(today or date.today()).normalize()
    effective_value = pd.Timestamp(effective_date).normalize()
    if pd.isna(effective_value):
        return None
    return max(0, int((today_value - effective_value).days))

def _stale_minutes(snapshot_time: str | None) -> int | None:
    if not snapshot_time:
        return None
    snapshot_value = pd.Timestamp(snapshot_time)
    if pd.isna(snapshot_value):
        return None
    now_value = pd.Timestamp.now(tz="UTC")
    if snapshot_value.tzinfo is None:
        snapshot_value = snapshot_value.tz_localize("UTC")
    else:
        snapshot_value = snapshot_value.tz_convert("UTC")
    return max(0, int((now_value - snapshot_value).total_seconds() // 60))

def _normalize_limit(value: int, *, default: int, min_value: int, max_value: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(min_value, min(parsed, max_value))

def _normalize_universe_code(universe_code: str | None, universe_limit: int) -> str:
    normalized = str(universe_code or "").strip().upper()
    if normalized in UNIVERSE_LABELS:
        return normalized
    return "TOP2000" if int(universe_limit or 1000) >= 2000 else "TOP1000"

def _universe_limit_from_code(universe_code: str, fallback: int) -> int:
    if universe_code == "TOP2000":
        return 2000
    if universe_code == "TOP1000":
        return 1000
    if universe_code == "NASDAQ":
        return max(5000, int(fallback or 0))
    return fallback

def _empty_movers_snapshot(
    *,
    status: str,
    period: str,
    universe_code: str,
    universe_limit: int,
    top_n: int,
    message: str,
    sector: str | None = None,
) -> dict[str, Any]:
    return {
        "status": status,
        "period": period,
        "period_label": PERIOD_LABELS.get(period, period),
        "universe_code": universe_code,
        "universe_label": UNIVERSE_LABELS.get(universe_code, universe_code),
        "universe_limit": universe_limit,
        "sector": sector or "All",
        "top_n": top_n,
        "rows": pd.DataFrame(columns=MOVERS_COLUMNS),
        "volume_rows": pd.DataFrame(columns=VOLUME_COLUMNS),
        "missing_rows": pd.DataFrame(columns=MISSING_COLUMNS),
        "sector_breadth": _empty_market_movers_sector_breadth_model(message=message),
        "date_window": {},
        "coverage": {
            "universe_count": 0,
            "returnable_count": 0,
            "missing_count": 0,
            "latest_raw_date": None,
            "effective_end_date": None,
            "stale_days": None,
            "price_mode": "Unavailable",
        },
        "warnings": [message] if message else [],
        "message": message,
    }

def _empty_group_snapshot(
    *,
    status: str,
    group_by: str,
    universe_code: str,
    universe_limit: int,
    period: str,
    top_n: int,
    message: str,
) -> dict[str, Any]:
    return {
        "status": status,
        "group_by": group_by,
        "universe_code": universe_code,
        "universe_label": UNIVERSE_LABELS.get(universe_code, universe_code),
        "universe_limit": universe_limit,
        "period": period,
        "period_label": PERIOD_LABELS.get(period, period),
        "trend_window_label": GROUP_TREND_PERIODS.get(period, {}).get("window_label"),
        "top_n": top_n,
        "rows": pd.DataFrame(columns=GROUP_COLUMNS),
        "trend_rows": pd.DataFrame(columns=GROUP_TREND_COLUMNS),
        "ticker_leader_rows": pd.DataFrame(columns=GROUP_TICKER_LEADER_COLUMNS),
        "missing_rows": pd.DataFrame(columns=MISSING_COLUMNS),
        "date_window": {},
        "coverage": {
            "universe_count": 0,
            "returnable_count": 0,
            "missing_count": 0,
            "latest_raw_date": None,
            "effective_end_date": None,
            "stale_days": None,
        },
        "warnings": [message] if message else [],
    }

def _query_latest_raw_date(query_fn: QueryFn, *, end_date: str | None = None) -> str | None:
    conditions = ["timeframe = %s"]
    params: list[Any] = ["1d"]
    if end_date:
        conditions.append("`date` <= %s")
        params.append(end_date)
    rows = query_fn(
        "finance_price",
        f"""
        SELECT `date` AS latest_raw_date
        FROM nyse_price_history FORCE INDEX (ix_date)
        WHERE {" AND ".join(conditions)}
        ORDER BY `date` DESC
        LIMIT 1
        """,
        params,
    )
    if not rows:
        return None
    return _iso_date(rows[0].get("latest_raw_date"))

def _eligible_market_dates(
    *,
    min_price_rows: int,
    limit: int,
    query_fn: QueryFn,
    end_date: str | None = None,
) -> tuple[str | None, list[dict[str, Any]]]:
    latest_raw_date = _query_latest_raw_date(query_fn, end_date=end_date)
    bounded_since: str | None = None
    latest_raw_ts = pd.Timestamp(latest_raw_date) if latest_raw_date else pd.NaT
    if not pd.isna(latest_raw_ts):
        lookback_days = max(370, int(limit) * 4)
        bounded_since = (latest_raw_ts.normalize() - pd.Timedelta(days=lookback_days)).strftime("%Y-%m-%d")

    def query_dates(*, since: str | None) -> list[dict[str, Any]]:
        conditions = ["timeframe = %s"]
        params: list[Any] = ["1d"]
        if since:
            conditions.append("`date` >= %s")
            params.append(since)
        if end_date:
            conditions.append("`date` <= %s")
            params.append(end_date)
        params.extend([int(min_price_rows), int(limit)])
        return query_fn(
            "finance_price",
            f"""
        SELECT
            `date`,
            SUM(CASE WHEN COALESCE(adj_close, close) IS NOT NULL THEN 1 ELSE 0 END) AS usable_rows
        FROM nyse_price_history FORCE INDEX (ix_date)
        WHERE {" AND ".join(conditions)}
        GROUP BY `date`
        HAVING usable_rows >= %s
        ORDER BY `date` DESC
        LIMIT %s
        """,
            params,
        )

    rows = query_dates(since=bounded_since)
    if bounded_since and len(rows) < int(limit):
        rows = query_dates(since=None)
    eligible = [
        {
            "date": _iso_date(row.get("date")),
            "usable_rows": int(row.get("usable_rows") or 0),
        }
        for row in rows
        if _iso_date(row.get("date"))
    ]
    return latest_raw_date, eligible

def resolve_effective_market_dates(
    *,
    period: str = "daily",
    min_price_rows: int = 1000,
    as_of_date: str | date | None = None,
    today: date | None = None,
    query_fn: QueryFn | None = None,
) -> dict[str, Any]:
    """Resolve the latest usable daily price window for overview market scans."""
    normalized_period = str(period or "daily").strip().lower()
    if normalized_period not in VALID_PERIODS:
        raise ValueError(f"Unsupported period: {period!r}")

    query = query_fn or _default_query
    offset = VALID_PERIODS[normalized_period]
    requested_as_of = _iso_date(as_of_date)
    latest_raw_date, eligible = _eligible_market_dates(
        min_price_rows=min_price_rows,
        limit=(offset * 2) + 1,
        query_fn=query,
        end_date=requested_as_of,
    )
    if len(eligible) <= offset:
        return {
            "status": "INSUFFICIENT_DATA",
            "period": normalized_period,
            "period_label": PERIOD_LABELS[normalized_period],
            "requested_as_of": requested_as_of,
            "start_date": None,
            "end_date": eligible[0]["date"] if eligible else None,
            "latest_raw_date": latest_raw_date,
            "effective_end_date": eligible[0]["date"] if eligible else None,
            "eligible_dates": eligible,
            "stale_days": _stale_days(eligible[0]["date"] if eligible else None, today=today),
            "message": (
                "Not enough eligible daily price rows to resolve the requested period at or before the selected as-of date."
                if requested_as_of
                else "Not enough eligible daily price rows to resolve the requested period."
            ),
        }

    end_row = eligible[0]
    start_row = eligible[offset]
    return {
        "status": "OK",
        "period": normalized_period,
        "period_label": PERIOD_LABELS[normalized_period],
        "requested_as_of": requested_as_of,
        "start_date": start_row["date"],
        "end_date": end_row["date"],
        "latest_raw_date": latest_raw_date,
        "effective_end_date": end_row["date"],
        "eligible_dates": eligible,
        "stale_days": _stale_days(end_row["date"], today=today),
        "message": "",
    }

def resolve_group_trend_market_dates(
    *,
    period: str = "monthly",
    min_price_rows: int = 1000,
    as_of_date: str | date | None = None,
    today: date | None = None,
    query_fn: QueryFn | None = None,
) -> dict[str, Any]:
    """Resolve non-overlapping windows for sector / industry leadership trends."""
    normalized_period = str(period or "monthly").strip().lower()
    if normalized_period not in GROUP_TREND_PERIODS:
        raise ValueError(f"Unsupported group trend period: {period!r}")

    query = query_fn or _default_query
    spec = GROUP_TREND_PERIODS[normalized_period]
    step = int(spec["step"])
    requested_windows = int(spec["windows"])
    requested_as_of = _iso_date(as_of_date)
    latest_raw_date, eligible = _eligible_market_dates(
        min_price_rows=min_price_rows,
        limit=(step * requested_windows) + 1,
        query_fn=query,
        end_date=requested_as_of,
    )
    available_windows = min(requested_windows, max(0, (len(eligible) - 1) // step))
    if available_windows <= 0:
        return {
            "status": "INSUFFICIENT_DATA",
            "period": normalized_period,
            "period_label": PERIOD_LABELS[normalized_period],
            "trend_window_label": spec["window_label"],
            "requested_as_of": requested_as_of,
            "start_date": None,
            "end_date": eligible[0]["date"] if eligible else None,
            "latest_raw_date": latest_raw_date,
            "effective_end_date": eligible[0]["date"] if eligible else None,
            "eligible_dates": eligible,
            "windows": [],
            "stale_days": _stale_days(eligible[0]["date"] if eligible else None, today=today),
            "message": (
                "Not enough eligible daily price rows to resolve group trend windows at or before the selected as-of date."
                if requested_as_of
                else "Not enough eligible daily price rows to resolve group trend windows."
            ),
        }

    windows: list[dict[str, Any]] = []
    for index in range(available_windows):
        end_row = eligible[index * step]
        start_row = eligible[(index + 1) * step]
        windows.append(
            {
                "start_date": start_row["date"],
                "end_date": end_row["date"],
                "label": end_row["date"],
                "usable_rows": end_row["usable_rows"],
            }
        )
    windows.reverse()
    latest_window = windows[-1]
    return {
        "status": "OK",
        "period": normalized_period,
        "period_label": PERIOD_LABELS[normalized_period],
        "trend_window_label": spec["window_label"],
        "requested_as_of": requested_as_of,
        "start_date": latest_window["start_date"],
        "end_date": latest_window["end_date"],
        "latest_raw_date": latest_raw_date,
        "effective_end_date": latest_window["end_date"],
        "eligible_dates": eligible,
        "windows": windows,
        "stale_days": _stale_days(latest_window["end_date"], today=today),
        "message": "",
    }

def _filter_sector(rows: list[dict[str, Any]], sector: str | None) -> list[dict[str, Any]]:
    normalized = str(sector or "All").strip()
    if not normalized or normalized == "All":
        return rows
    return [row for row in rows if str(row.get("sector") or "Unknown") == normalized]

def _load_universe(
    *,
    universe_code: str,
    universe_limit: int,
    query_fn: QueryFn,
    sector: str | None = None,
) -> list[dict[str, Any]]:
    if universe_code == "SP500":
        rows = query_fn(
            "finance_meta",
            """
            SELECT
                m.symbol,
                COALESCE(NULLIF(p.long_name, ''), NULLIF(m.name, ''), s.name) AS long_name,
                COALESCE(p.sector, m.sector) AS sector,
                COALESCE(p.industry, m.industry) AS industry,
                p.market_cap,
                p.exchange AS profile_exchange,
                p.status,
                p.error_msg,
                p.last_collected_at,
                m.as_of_date AS universe_as_of_date,
                m.collected_at AS universe_collected_at,
                m.source AS universe_source,
                m.source_url AS universe_source_url
            FROM market_universe_member m
            LEFT JOIN nyse_asset_profile p
              ON p.symbol = m.symbol
             AND p.kind = %s
            LEFT JOIN nyse_stock s
              ON s.symbol = m.symbol
            WHERE m.universe_code = %s
              AND m.active = 1
            ORDER BY COALESCE(p.market_cap, 0) DESC, m.symbol ASC
            """,
            ["stock", "SP500"],
        )
        return _filter_sector(rows, sector)

    if universe_code == "NASDAQ":
        rows = query_fn(
            "finance_meta",
            """
            SELECT
                l.symbol,
                COALESCE(NULLIF(p.long_name, ''), NULLIF(l.name, ''), s.name) AS long_name,
                p.sector,
                p.industry,
                p.market_cap,
                p.exchange AS profile_exchange,
                p.status,
                p.error_msg,
                p.last_collected_at,
                l.event_date AS universe_event_date,
                l.collected_at AS universe_collected_at,
                l.source AS universe_source,
                l.source_ref AS universe_source_url,
                l.source_type AS universe_source_type,
                l.coverage_status AS universe_coverage_status,
                l.event_type AS universe_event_type,
                l.listing_status AS universe_listing_status
            FROM nyse_symbol_lifecycle l
            LEFT JOIN nyse_asset_profile p
              ON p.symbol = l.symbol
             AND p.kind = l.kind
            LEFT JOIN nyse_stock s
              ON s.symbol = l.symbol
            WHERE l.source = %s
              AND l.source_type = %s
              AND l.event_type = %s
              AND l.kind = %s
              AND l.listing_status = %s
              AND COALESCE(l.event_date, DATE(l.collected_at)) = (
                    SELECT MAX(COALESCE(event_date, DATE(collected_at)))
                    FROM nyse_symbol_lifecycle
                    WHERE source = %s
                      AND source_type = %s
                      AND event_type = %s
                      AND kind = %s
                      AND listing_status = %s
              )
            ORDER BY COALESCE(p.market_cap, 0) DESC, l.symbol ASC
            """,
            [
                "nasdaq_symdir_nasdaqlisted",
                "current_listing_snapshot",
                "listing_observed",
                "stock",
                "active",
                "nasdaq_symdir_nasdaqlisted",
                "current_listing_snapshot",
                "listing_observed",
                "stock",
                "active",
            ],
        )
        return _filter_sector(rows, sector)

    return _filter_sector(
        query_fn(
            "finance_meta",
            """
            SELECT
                m.symbol,
                COALESCE(NULLIF(p.long_name, ''), NULLIF(m.name, ''), s.name) AS long_name,
                COALESCE(p.sector, m.sector) AS sector,
                COALESCE(p.industry, m.industry) AS industry,
                COALESCE(p.market_cap, m.market_cap) AS market_cap,
                p.exchange AS profile_exchange,
                p.status,
                p.error_msg,
                p.last_collected_at,
                m.rank_position AS universe_rank_position,
                m.avg_dollar_volume_20d,
                m.dollar_volume_days,
                m.ranking_window_start_date,
                m.ranking_end_date AS universe_as_of_date,
                m.generated_at AS universe_collected_at,
                m.ranking_source AS universe_source,
                m.price_source AS universe_price_source,
                m.listing_source AS universe_listing_source,
                m.listing_source_url AS universe_listing_source_url,
                m.listing_source_type AS universe_listing_source_type,
                m.listing_coverage_status AS universe_listing_coverage_status,
                m.listing_event_type AS universe_listing_event_type,
                m.listing_status AS universe_listing_status,
                m.listing_event_date AS universe_listing_event_date
            FROM market_liquidity_universe_member m
            LEFT JOIN nyse_asset_profile p
              ON p.symbol = m.symbol
             AND p.kind = %s
            LEFT JOIN nyse_stock s
              ON s.symbol = m.symbol
            WHERE m.universe_code = %s
              AND m.active = 1
            ORDER BY m.rank_position ASC, m.symbol ASC
            LIMIT %s
            """,
            ["stock", universe_code, int(universe_limit)],
        ),
        sector,
    )

def load_market_mover_sector_options(
    *,
    universe_code: str = "TOP1000",
    universe_limit: int = 1000,
    query_fn: QueryFn | None = None,
) -> list[str]:
    query = query_fn or _default_query
    try:
        normalized = _normalize_universe_code(universe_code, universe_limit)
        limit = _universe_limit_from_code(normalized, universe_limit)
        rows = _load_universe(universe_code=normalized, universe_limit=limit, query_fn=query)
    except Exception:
        return []
    sectors = sorted({str(row.get("sector") or "Unknown") for row in rows})
    return sectors

def _load_prices_for_dates(
    *,
    symbols: list[str],
    dates: list[str],
    query_fn: QueryFn,
) -> dict[tuple[str, str], float]:
    points = _load_price_points_for_dates(symbols=symbols, dates=dates, query_fn=query_fn)
    return {
        key: float(value["price"])
        for key, value in points.items()
        if value.get("price") is not None
    }

def _load_price_points_for_dates(
    *,
    symbols: list[str],
    dates: list[str],
    query_fn: QueryFn,
) -> dict[tuple[str, str], dict[str, float | int | None]]:
    if not symbols or not dates:
        return {}

    symbol_placeholders = ",".join(["%s"] * len(symbols))
    date_placeholders = ",".join(["%s"] * len(dates))
    rows = query_fn(
        "finance_price",
        f"""
        SELECT
            symbol,
            `date`,
            COALESCE(adj_close, close) AS price,
            volume
        FROM nyse_price_history FORCE INDEX (uk_symbol_timeframe_date)
        WHERE symbol IN ({symbol_placeholders})
          AND timeframe = %s
          AND `date` IN ({date_placeholders})
        """,
        list(symbols) + ["1d"] + list(dates),
    )
    points: dict[tuple[str, str], dict[str, float | int | None]] = {}
    for row in rows:
        symbol = str(row.get("symbol") or "").strip().upper()
        row_date = _iso_date(row.get("date"))
        price = _safe_float(row.get("price"))
        if not symbol or not row_date or price is None:
            continue
        volume = _safe_float(row.get("volume"))
        points[(symbol, row_date)] = {
            "price": price,
            "volume": int(volume) if volume is not None else None,
        }
    return points

def _previous_period_window(date_window: dict[str, Any], *, period: str) -> dict[str, str] | None:
    normalized_period = str(period or "daily").strip().lower()
    offset = VALID_PERIODS.get(normalized_period)
    if offset is None:
        return None
    eligible = list(date_window.get("eligible_dates") or [])
    if len(eligible) <= offset * 2:
        return None
    previous_start = _iso_date(eligible[offset * 2].get("date"))
    previous_end = _iso_date(eligible[offset].get("date"))
    if not previous_start or not previous_end:
        return None
    return {
        "previous_start_date": previous_start,
        "previous_end_date": previous_end,
    }

def _return_pct(start_price: float | None, end_price: float | None) -> float | None:
    if start_price is None or end_price is None or start_price <= 0:
        return None
    return (float(end_price) / float(start_price) - 1.0) * 100.0

def _previous_return_context(
    *,
    symbols: list[str],
    date_window: dict[str, Any],
    period: str,
    query_fn: QueryFn,
) -> dict[str, dict[str, Any]]:
    previous_window = _previous_period_window(date_window, period=period)
    if not previous_window:
        return {}
    previous_start = previous_window["previous_start_date"]
    previous_end = previous_window["previous_end_date"]
    points = _load_price_points_for_dates(
        symbols=symbols,
        dates=[previous_start, previous_end],
        query_fn=query_fn,
    )
    context: dict[str, dict[str, Any]] = {}
    for symbol in symbols:
        start_price = _safe_float((points.get((symbol, previous_start)) or {}).get("price"))
        end_price = _safe_float((points.get((symbol, previous_end)) or {}).get("price"))
        previous_return = _return_pct(start_price, end_price)
        if previous_return is None:
            continue
        context[symbol] = {
            "previous_return_pct": previous_return,
            "previous_start_date": previous_start,
            "previous_end_date": previous_end,
        }
    return context

def _load_latest_price_dates(*, symbols: list[str], query_fn: QueryFn) -> dict[str, str]:
    if not symbols:
        return {}
    placeholders = ",".join(["%s"] * len(symbols))
    rows = query_fn(
        "finance_price",
        f"""
        SELECT symbol, MAX(`date`) AS latest_price_date
        FROM nyse_price_history
        WHERE symbol IN ({placeholders})
          AND timeframe = %s
          AND COALESCE(adj_close, close) IS NOT NULL
        GROUP BY symbol
        """,
        list(symbols) + ["1d"],
    )
    return {
        str(row.get("symbol") or "").strip().upper(): _iso_date(row.get("latest_price_date")) or ""
        for row in rows
        if row.get("symbol")
    }

def _profile_collected_at(item: dict[str, Any]) -> str | None:
    return _display_datetime(item.get("last_collected_at"))

def _profile_freshness_summary(row: dict[str, Any]) -> str:
    parts: list[str] = []
    status = str(row.get("Profile Status") or "").strip()
    if status and status != "-":
        parts.append(f"Profile status {status}")
    exchange = str(row.get("Profile Exchange") or row.get("profile_exchange") or "").strip()
    if exchange and exchange != "-":
        parts.append(f"exchange {exchange}")
    collected = str(row.get("Profile Collected At") or "").strip()
    if collected and collected != "-":
        parts.append(f"collected {collected}")
    error = str(row.get("Profile Error") or "").strip()
    if error and error != "-":
        parts.append(f"error: {error}")
    return "; ".join(parts) if parts else "No profile freshness evidence in current read model."

def _format_listing_evidence(evidence: dict[str, Any] | None) -> str:
    if not evidence:
        return "No lifecycle evidence found in DB."
    source = evidence.get("source") or "-"
    source_type = evidence.get("source_type") or "-"
    event_type = evidence.get("event_type") or "-"
    event_date = _iso_date(evidence.get("event_date")) or "-"
    coverage_status = evidence.get("coverage_status") or "-"
    listing_status = evidence.get("listing_status") or "-"
    if str(event_type).lower() == "delisting" or str(source_type).lower() == "delisting_feed":
        return (
            f"{source} {source_type} {event_type} event_date={event_date}; "
            "delisting evidence exists from lifecycle source."
        )
    caveat = ""
    if str(source_type).lower() == "current_listing_snapshot":
        caveat = "; current listing observation only"
    return (
        f"{source} {source_type} {event_type} listing_status={listing_status} "
        f"coverage={coverage_status} event_date={event_date}{caveat}"
    )

def _format_market_data_issue(issue: dict[str, Any] | None) -> str:
    if not issue:
        return "No repeated market data issue row found."
    issue_type = issue.get("issue_type") or "-"
    diagnosis = issue.get("diagnosis") or "-"
    occurrences = issue.get("occurrence_count") or 0
    last_seen = _display_datetime(issue.get("last_seen_at")) or "-"
    evidence = str(issue.get("latest_evidence") or "").strip()
    suffix = f"; {evidence}" if evidence else ""
    return f"{issue_type}: {diagnosis}; occurrences={occurrences}; latest={last_seen}{suffix}"

def _missing_likely_cause(row: dict[str, Any], issue: dict[str, Any] | None) -> str:
    reason = str(row.get("Reason") or "").lower()
    profile_status = str(row.get("Profile Status") or "").lower()
    if issue:
        return "Repeated market data issue evidence; confirm quote and price-history coverage."
    if profile_status in {"error", "not_found", "delisted"}:
        return "Profile metadata needs review alongside price-history coverage."
    if "intraday" in reason or "latest quote" in reason:
        return "Daily quote snapshot gap."
    if "start" in reason or "end price" in reason:
        return "EOD price-history coverage gap."
    return "Price or listing evidence needs review."

def _missing_next_check(row: dict[str, Any], issue: dict[str, Any] | None) -> str:
    profile_status = str(row.get("Profile Status") or "").lower()
    if profile_status in {"error", "not_found", "delisted"}:
        return "Check profile refresh, listing evidence, then refresh daily OHLCV history."
    if issue:
        return "Open quote-gap diagnostics and inspect latest price/profile evidence before retrying refresh."
    reason = str(row.get("Reason") or "").lower()
    if "intraday" in reason or "latest quote" in reason:
        return "Refresh daily snapshot; if repeated, run quote-gap diagnostics."
    return "Refresh daily OHLCV history; if repeated, inspect lifecycle/profile evidence."

def _missing_evidence_fields(
    row: dict[str, Any],
    *,
    listing_evidence: dict[str, Any] | None = None,
    market_data_issue: dict[str, Any] | None = None,
) -> dict[str, str]:
    profile = _profile_freshness_summary(row)
    listing = _format_listing_evidence(listing_evidence)
    issue = _format_market_data_issue(market_data_issue)
    latest_price = str(row.get("Latest Price Date") or "-")
    reason = str(row.get("Reason") or "-")
    evidence_summary = f"{reason}; latest price date {latest_price}; {profile}; {listing}; {issue}"
    return {
        "Likely Cause": _missing_likely_cause(row, market_data_issue),
        "Evidence Summary": evidence_summary,
        "Next Check": _missing_next_check(row, market_data_issue),
        "Listing Evidence": listing,
        "Profile Freshness": profile,
        "Market Data Issue": issue,
    }

def _missing_row(
    *,
    item: dict[str, Any],
    reason: str,
    start_date: str,
    end_date: str,
    start_price: float | None,
    end_price: float | None,
    latest_price_date: str | None,
) -> dict[str, Any]:
    row = {
        "Symbol": str(item.get("symbol") or "").strip().upper(),
        "Name": item.get("long_name") or "-",
        "Sector": item.get("sector") or "Unknown",
        "Industry": item.get("industry") or "Unknown",
        "Reason": reason,
        "Recommended Action": _missing_recommended_action(reason),
        "Start Date": start_date,
        "End Date": end_date,
        "Start Price": round(float(start_price), 4) if start_price is not None else None,
        "End Price": round(float(end_price), 4) if end_price is not None else None,
        "Latest Price Date": latest_price_date,
        "Profile Status": item.get("status") or "-",
        "Profile Error": item.get("error_msg") or "-",
        "Profile Collected At": _profile_collected_at(item) or "-",
        "Profile Exchange": item.get("profile_exchange") or "-",
    }
    row.update(_missing_evidence_fields(row))
    return row

def _load_symbol_lifecycle_evidence(
    *,
    symbols: list[str],
    query_fn: QueryFn,
) -> dict[str, dict[str, Any]]:
    if not symbols:
        return {}
    placeholders = ",".join(["%s"] * len(symbols))
    rows = query_fn(
        "finance_meta",
        f"""
        SELECT
            symbol,
            listing_status,
            source,
            source_type,
            coverage_status,
            event_type,
            event_date,
            collected_at
        FROM nyse_symbol_lifecycle
        WHERE symbol IN ({placeholders})
          AND kind = %s
        ORDER BY
            symbol ASC,
            COALESCE(event_date, DATE(collected_at)) DESC,
            collected_at DESC,
            CASE WHEN event_type = 'delisting' THEN 0 ELSE 1 END
        """,
        list(symbols) + ["stock"],
    )
    evidence: dict[str, dict[str, Any]] = {}
    for row in rows:
        symbol = str(row.get("symbol") or "").strip().upper()
        if symbol and symbol not in evidence:
            evidence[symbol] = row
    return evidence

def _load_market_data_issue_evidence(
    *,
    symbols: list[str],
    universe_code: str,
    query_fn: QueryFn,
) -> dict[str, dict[str, Any]]:
    if not symbols:
        return {}
    placeholders = ",".join(["%s"] * len(symbols))
    rows = query_fn(
        "finance_meta",
        f"""
        SELECT
            symbol,
            issue_type,
            diagnosis,
            occurrence_count,
            last_seen_at,
            latest_evidence
        FROM market_data_issue
        WHERE symbol IN ({placeholders})
          AND universe_code = %s
          AND latest_status = %s
        ORDER BY symbol ASC, occurrence_count DESC, last_seen_at DESC
        """,
        list(symbols) + [universe_code, "active"],
    )
    issues: dict[str, dict[str, Any]] = {}
    for row in rows:
        symbol = str(row.get("symbol") or "").strip().upper()
        if symbol and symbol not in issues:
            issues[symbol] = row
    return issues

def _enrich_missing_rows(
    missing_rows: list[dict[str, Any]],
    *,
    universe_code: str,
    query_fn: QueryFn,
) -> list[dict[str, Any]]:
    symbols = [str(row.get("Symbol") or "").strip().upper() for row in missing_rows if row.get("Symbol")]
    if not symbols:
        return missing_rows
    lifecycle = _load_symbol_lifecycle_evidence(symbols=symbols, query_fn=query_fn)
    issues = _load_market_data_issue_evidence(
        symbols=symbols,
        universe_code=universe_code,
        query_fn=query_fn,
    )
    for row in missing_rows:
        symbol = str(row.get("Symbol") or "").strip().upper()
        row.update(
            _missing_evidence_fields(
                row,
                listing_evidence=lifecycle.get(symbol),
                market_data_issue=issues.get(symbol),
            )
        )
    return missing_rows

def _missing_recommended_action(reason: str) -> str:
    normalized = str(reason or "").lower()
    if "intraday snapshot row" in normalized:
        return "Run Update Daily Snapshot for this coverage."
    if "latest quote" in normalized or "latest price" in normalized or "intraday return" in normalized:
        return "Refresh the daily snapshot; if it persists, inspect provider quote coverage."
    if "previous close" in normalized or "start price" in normalized:
        return "Refresh daily OHLCV history or inspect previous-close coverage."
    if "end price" in normalized:
        return "Refresh daily OHLCV history for the latest market date."
    if "non-positive" in normalized:
        return "Inspect price history for split or corporate action issues."
    return "Inspect provider data, then rerun the relevant refresh."

def _build_return_rows(
    *,
    universe: list[dict[str, Any]],
    universe_code: str,
    start_date: str,
    end_date: str,
    query_fn: QueryFn,
    previous_context: dict[str, dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    symbols = [str(row.get("symbol") or "").strip().upper() for row in universe if row.get("symbol")]
    price_points = _load_price_points_for_dates(symbols=symbols, dates=[start_date, end_date], query_fn=query_fn)
    previous_context = previous_context or {}
    return_rows: list[dict[str, Any]] = []
    missing_candidates: list[dict[str, Any]] = []
    missing_rows: list[dict[str, Any]] = []

    for item in universe:
        symbol = str(item.get("symbol") or "").strip().upper()
        start_point = price_points.get((symbol, start_date)) or {}
        end_point = price_points.get((symbol, end_date)) or {}
        start_price = _safe_float(start_point.get("price"))
        end_price = _safe_float(end_point.get("price"))
        if start_price is None and end_price is None:
            reason = "missing start and end price"
        elif start_price is None:
            reason = "missing start price"
        elif end_price is None:
            reason = "missing end price"
        elif start_price <= 0:
            reason = "non-positive start price"
        else:
            reason = ""
        if reason:
            missing_candidates.append(
                {
                    "item": item,
                    "symbol": symbol,
                    "reason": reason,
                    "start_price": start_price,
                    "end_price": end_price,
                }
            )
            continue
        return_pct = _return_pct(start_price, end_price)
        if return_pct is None:
            continue
        volume = _safe_float(end_point.get("volume"))
        previous = previous_context.get(symbol) or {}
        previous_return = _safe_float(previous.get("previous_return_pct"))
        return_rows.append(
            {
                "symbol": symbol,
                "name": item.get("long_name") or "",
                "sector": item.get("sector") or "Unknown",
                "industry": item.get("industry") or "Unknown",
                "market_cap": _safe_float(item.get("market_cap")) or 0.0,
                "start_price": start_price,
                "end_price": end_price,
                "return_pct": return_pct,
                "previous_return_pct": previous_return,
                "momentum_delta_pp": (return_pct - previous_return) if previous_return is not None else None,
                "volume": int(volume) if volume is not None else None,
                "dollar_volume": (float(end_price) * float(volume)) if volume is not None else None,
                "start_date": start_date,
                "end_date": end_date,
                "previous_start_date": previous.get("previous_start_date"),
                "previous_end_date": previous.get("previous_end_date"),
                "price_source": "EOD DB",
            }
        )
    if missing_candidates:
        latest_dates = _load_latest_price_dates(
            symbols=[str(row["symbol"]) for row in missing_candidates],
            query_fn=query_fn,
        )
        for row in missing_candidates:
            missing_rows.append(
                _missing_row(
                    item=row["item"],
                    reason=str(row["reason"]),
                    start_date=start_date,
                    end_date=end_date,
                    start_price=_safe_float(row.get("start_price")),
                    end_price=_safe_float(row.get("end_price")),
                    latest_price_date=latest_dates.get(str(row["symbol"])),
                )
            )
    return return_rows, _enrich_missing_rows(
        missing_rows,
        universe_code=universe_code,
        query_fn=query_fn,
    )

def _build_return_rows_from_price_map(
    *,
    universe: list[dict[str, Any]],
    start_date: str,
    end_date: str,
    price_map: dict[tuple[str, str], float],
) -> list[dict[str, Any]]:
    return_rows: list[dict[str, Any]] = []
    for item in universe:
        symbol = str(item.get("symbol") or "").strip().upper()
        start_price = price_map.get((symbol, start_date))
        end_price = price_map.get((symbol, end_date))
        if start_price is None or end_price is None or start_price <= 0:
            continue
        return_rows.append(
            {
                "symbol": symbol,
                "name": item.get("long_name") or "",
                "sector": item.get("sector") or "Unknown",
                "industry": item.get("industry") or "Unknown",
                "market_cap": _safe_float(item.get("market_cap")) or 0.0,
                "start_price": start_price,
                "end_price": end_price,
                "return_pct": (float(end_price) / float(start_price) - 1.0) * 100.0,
                "start_date": start_date,
                "end_date": end_date,
                "price_source": "EOD DB",
            }
        )
    return return_rows

def _group_leadership_rows(
    *,
    return_rows: list[dict[str, Any]],
    group_by: str,
    min_group_size: int,
    start_date: str,
    end_date: str,
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in return_rows:
        group_name = str(row.get(group_by) or "Unknown").strip() or "Unknown"
        grouped.setdefault(group_name, []).append(row)

    group_rows: list[dict[str, Any]] = []
    for group_name, rows in grouped.items():
        if len(rows) < int(min_group_size):
            continue
        equal_weight_return = sum(float(row["return_pct"]) for row in rows) / len(rows)
        weighted_denominator = sum(max(float(row.get("market_cap") or 0.0), 0.0) for row in rows)
        if weighted_denominator > 0:
            weighted_return = (
                sum(max(float(row.get("market_cap") or 0.0), 0.0) * float(row["return_pct"]) for row in rows)
                / weighted_denominator
            )
        else:
            weighted_return = equal_weight_return
        top_symbol = max(rows, key=lambda row: float(row["return_pct"]))
        positive_symbols = sum(1 for row in rows if float(row.get("return_pct") or 0.0) > 0)
        positive_symbol_share = (positive_symbols / len(rows)) * 100.0 if rows else 0.0
        positive_returns = sorted(
            [max(float(row.get("return_pct") or 0.0), 0.0) for row in rows],
            reverse=True,
        )
        positive_return_total = sum(positive_returns)
        top3_positive_share = (
            (sum(positive_returns[:3]) / positive_return_total) * 100.0
            if positive_return_total > 0
            else None
        )
        group_rows.append(
            {
                "group": group_name,
                "group_type": group_by.title(),
                "symbols": len(rows),
                "positive_symbols": positive_symbols,
                "positive_symbol_share": positive_symbol_share,
                "equal_weight_return": equal_weight_return,
                "market_cap_weighted_return": weighted_return,
                "cap_vs_equal_gap_pp": weighted_return - equal_weight_return,
                "top3_positive_share": top3_positive_share,
                "top_symbol": top_symbol["symbol"],
                "top_symbol_return": top_symbol["return_pct"],
                "start_date": start_date,
                "end_date": end_date,
            }
        )
    return group_rows

def _rank_group_rows(group_rows: list[dict[str, Any]], *, top_n: int | None = None) -> list[dict[str, Any]]:
    ranked = sorted(
        group_rows,
        key=lambda row: (
            -float(row["market_cap_weighted_return"]),
            -float(row["equal_weight_return"]),
            row["group"],
        ),
    )
    return ranked[:top_n] if top_n is not None else ranked

def _group_rows_frame(group_rows: list[dict[str, Any]]) -> pd.DataFrame:
    rows = [
        {
            "Rank": index,
            "Group": row["group"],
            "Group Type": row["group_type"],
            "Symbols": row["symbols"],
            "Positive Symbols": row.get("positive_symbols"),
            "Positive Symbol Share %": round(float(row.get("positive_symbol_share") or 0.0), 2),
            "Equal Weight Return %": round(float(row["equal_weight_return"]), 2),
            "Market Cap Weighted Return %": round(float(row["market_cap_weighted_return"]), 2),
            "Cap vs Equal Gap pp": round(float(row.get("cap_vs_equal_gap_pp") or 0.0), 2),
            "Top 3 Positive Share %": round(float(row["top3_positive_share"]), 2)
            if row.get("top3_positive_share") is not None
            else None,
            "Top Symbol": row["top_symbol"],
            "Top Symbol Return %": round(float(row["top_symbol_return"]), 2),
            "Start Date": row["start_date"],
            "End Date": row["end_date"],
        }
        for index, row in enumerate(group_rows, start=1)
    ]
    return pd.DataFrame(rows, columns=GROUP_COLUMNS)

def _group_trend_rows_frame(
    *,
    windows: list[dict[str, Any]],
    universe: list[dict[str, Any]],
    groups: set[str],
    group_by: str,
    min_group_size: int,
    query_fn: QueryFn,
) -> pd.DataFrame:
    if not windows or not groups:
        return pd.DataFrame(columns=GROUP_TREND_COLUMNS)
    symbols = [str(row.get("symbol") or "").strip().upper() for row in universe if row.get("symbol")]
    dates = sorted({str(window["start_date"]) for window in windows} | {str(window["end_date"]) for window in windows})
    price_map = _load_prices_for_dates(symbols=symbols, dates=dates, query_fn=query_fn)
    trend_rows: list[dict[str, Any]] = []
    for window in windows:
        return_rows = _build_return_rows_from_price_map(
            universe=universe,
            start_date=str(window["start_date"]),
            end_date=str(window["end_date"]),
            price_map=price_map,
        )
        group_rows = _group_leadership_rows(
            return_rows=return_rows,
            group_by=group_by,
            min_group_size=min_group_size,
            start_date=str(window["start_date"]),
            end_date=str(window["end_date"]),
        )
        for row in group_rows:
            if row["group"] not in groups:
                continue
            trend_rows.append(
                {
                    "Date": window["end_date"],
                    "Group": row["group"],
                    "Group Type": row["group_type"],
                    "Symbols": row["symbols"],
                    "Equal Weight Return %": round(float(row["equal_weight_return"]), 2),
                    "Market Cap Weighted Return %": round(float(row["market_cap_weighted_return"]), 2),
                    "Top Symbol": row["top_symbol"],
                    "Top Symbol Return %": round(float(row["top_symbol_return"]), 2),
                    "Start Date": row["start_date"],
                    "End Date": row["end_date"],
                }
            )
    return pd.DataFrame(trend_rows, columns=GROUP_TREND_COLUMNS)

def _group_trend_rows_from_group_rows(
    *,
    group_rows: list[dict[str, Any]],
    groups: set[str],
    date_value: str,
) -> pd.DataFrame:
    trend_rows = [
        {
            "Date": date_value,
            "Group": row["group"],
            "Group Type": row["group_type"],
            "Symbols": row["symbols"],
            "Equal Weight Return %": round(float(row["equal_weight_return"]), 2),
            "Market Cap Weighted Return %": round(float(row["market_cap_weighted_return"]), 2),
            "Top Symbol": row["top_symbol"],
            "Top Symbol Return %": round(float(row["top_symbol_return"]), 2),
            "Start Date": row["start_date"],
            "End Date": row["end_date"],
        }
        for row in group_rows
        if row["group"] in groups
    ]
    return pd.DataFrame(trend_rows, columns=GROUP_TREND_COLUMNS)

def _group_ticker_leader_rows_frame(
    *,
    return_rows: list[dict[str, Any]],
    positive_groups: set[str],
    group_by: str,
) -> pd.DataFrame:
    if not return_rows or not positive_groups:
        return pd.DataFrame(columns=GROUP_TICKER_LEADER_COLUMNS)

    normalized_groups = {str(group).strip() for group in positive_groups if str(group).strip()}
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in return_rows:
        group_name = str(row.get(group_by) or "Unknown").strip() or "Unknown"
        if group_name not in normalized_groups:
            continue
        return_pct = _safe_float(row.get("return_pct"))
        if return_pct is None or return_pct <= 0:
            continue
        grouped.setdefault(group_name, []).append(row)

    leader_rows: list[dict[str, Any]] = []
    for group_name in sorted(grouped):
        rows = sorted(
            grouped[group_name],
            key=lambda row: (
                -float(row.get("return_pct") or 0.0),
                str(row.get("symbol") or ""),
            ),
        )
        positive_return_total = sum(max(float(row.get("return_pct") or 0.0), 0.0) for row in rows)
        for rank, row in enumerate(rows, start=1):
            return_pct = float(row.get("return_pct") or 0.0)
            previous_return = _safe_float(row.get("previous_return_pct"))
            leader_rows.append(
                {
                    "Group": group_name,
                    "Group Type": group_by.title(),
                    "Rank": rank,
                    "Symbol": str(row.get("symbol") or "").strip().upper(),
                    "Name": row.get("name") or "-",
                    "Return %": round(return_pct, 2),
                    "Previous Return %": round(float(previous_return), 2)
                    if previous_return is not None
                    else None,
                    "Momentum Delta pp": round(float(return_pct - previous_return), 2)
                    if previous_return is not None
                    else None,
                    "Positive Return Share %": round(
                        (return_pct / positive_return_total) * 100.0,
                        2,
                    )
                    if positive_return_total > 0
                    else None,
                    "Sector": row.get("sector") or "Unknown",
                    "Industry": row.get("industry") or "Unknown",
                    "Market Cap": round(float(row.get("market_cap") or 0.0), 2),
                    "Start Price": round(float(row.get("start_price") or 0.0), 4),
                    "End Price": round(float(row.get("end_price") or 0.0), 4),
                    "Start Date": row.get("start_date"),
                    "End Date": row.get("end_date"),
                    "Previous Start Date": row.get("previous_start_date") or "-",
                    "Previous End Date": row.get("previous_end_date") or "-",
                }
            )

    return pd.DataFrame(leader_rows, columns=GROUP_TICKER_LEADER_COLUMNS)

def _coverage(
    *,
    universe_count: int,
    returnable_count: int,
    date_window: dict[str, Any],
    price_mode: str = "EOD DB",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    missing_count = max(0, universe_count - returnable_count)
    returnable_ratio = (returnable_count / universe_count) if universe_count else None
    coverage = {
        "universe_count": universe_count,
        "returnable_count": returnable_count,
        "missing_count": missing_count,
        "failed_count": missing_count,
        "returnable_ratio": round(returnable_ratio, 4) if returnable_ratio is not None else None,
        "returnable_pct": round(returnable_ratio * 100, 2) if returnable_ratio is not None else None,
        "latest_raw_date": date_window.get("latest_raw_date"),
        "effective_end_date": date_window.get("effective_end_date"),
        "stale_days": date_window.get("stale_days"),
        "price_mode": price_mode,
    }
    if extra:
        coverage.update(extra)
    return coverage

def _intraday_refresh_state(
    *,
    snapshot_status: str,
    period: str,
    coverage: dict[str, Any],
) -> dict[str, Any] | None:
    if period != "daily":
        return None
    price_mode = str(coverage.get("price_mode") or "")
    stale_minutes_value = coverage.get("snapshot_stale_minutes")
    stale_minutes = int(stale_minutes_value) if stale_minutes_value is not None else None
    missing_count = int(coverage.get("missing_count") or 0)
    returnable_count = int(coverage.get("returnable_count") or 0)
    universe_count = int(coverage.get("universe_count") or 0)
    returnable_pct = coverage.get("returnable_pct")
    next_due_in = (
        max(0, MARKET_INTRADAY_REFRESH_MINUTES - stale_minutes)
        if stale_minutes is not None
        else None
    )

    if snapshot_status != "OK":
        status = "failed"
        label = "Failed"
        detail = "snapshot build failed"
        action = "Open warnings and rerun the relevant refresh."
    elif price_mode != "Intraday Snapshot":
        status = "failed"
        label = "Snapshot missing"
        detail = "using EOD fallback"
        action = "Run Update Daily Snapshot; refresh S&P 500 universe first if no rows are available."
    elif returnable_count <= 0:
        status = "failed"
        label = "Failed"
        detail = "no returnable symbols"
        action = "Run Update Daily Snapshot and inspect Coverage Diagnostics."
    elif stale_minutes is None:
        status = "due"
        label = "Update due"
        detail = "snapshot age unavailable"
        action = "Run Update Daily Snapshot."
    elif stale_minutes >= MARKET_INTRADAY_STALE_MINUTES:
        status = "stale"
        label = "Stale"
        detail = f"{stale_minutes}m old"
        action = "Run Update Daily Snapshot."
    elif stale_minutes >= MARKET_INTRADAY_REFRESH_MINUTES:
        status = "due"
        label = "Update due"
        detail = f"{stale_minutes}m old"
        action = "Run Update Daily Snapshot."
    elif missing_count:
        status = "partial"
        label = "Partial"
        detail = f"{stale_minutes}m old, {missing_count} missing"
        action = "Open Coverage Diagnostics; rerun refresh if missing count is unexpected."
    else:
        status = "fresh"
        label = "Fresh"
        detail = f"{stale_minutes}m old, next check in {next_due_in}m"
        action = "No action needed yet."

    if status in {"due", "stale", "failed"} and missing_count and "missing" not in detail:
        detail = f"{detail}, {missing_count} missing"

    return {
        "status": status,
        "label": label,
        "detail": detail,
        "recommended_action": action,
        "refresh_due": status in {"due", "stale", "failed"},
        "is_partial": missing_count > 0,
        "stale_minutes": stale_minutes,
        "missing_count": missing_count,
        "returnable_count": returnable_count,
        "universe_count": universe_count,
        "returnable_pct": returnable_pct,
        "next_due_in_minutes": next_due_in,
        "check_interval_minutes": MARKET_INTRADAY_REFRESH_MINUTES,
        "stale_after_minutes": MARKET_INTRADAY_STALE_MINUTES,
        "tone": {
            "fresh": "positive",
            "partial": "warning",
            "due": "warning",
            "stale": "danger",
            "failed": "danger",
        }.get(status, "neutral"),
    }

def _coverage_warnings(coverage: dict[str, Any], *, date_window: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    if coverage.get("latest_raw_date") and coverage.get("effective_end_date"):
        if coverage["latest_raw_date"] != coverage["effective_end_date"]:
            warnings.append(
                "Latest raw price date is sparse or unusable; rankings use the latest effective market date."
            )
    missing_count = int(coverage.get("missing_count") or 0)
    if missing_count:
        warnings.append(f"{missing_count} symbols in the selected universe are missing returnable price rows.")
    if date_window.get("status") != "OK":
        warnings.append(str(date_window.get("message") or "Market date window is unavailable."))
    snapshot_stale = coverage.get("snapshot_stale_minutes")
    if snapshot_stale is not None and int(snapshot_stale) > 15:
        warnings.append(f"Latest intraday snapshot is {snapshot_stale} minutes old.")
    return warnings

COVERAGE_TRUST_GROUP_COLUMNS = [
    "Missing Reason Group",
    "Likely Cause",
    "Suggested Next Action",
    "Affected Count",
    "Sample Tickers",
]

def _coverage_trust_missing_rows(snapshot: dict[str, Any]) -> pd.DataFrame:
    rows = snapshot.get("missing_rows")
    if isinstance(rows, pd.DataFrame):
        return rows.copy()
    if isinstance(rows, list):
        return pd.DataFrame(rows)
    return pd.DataFrame(columns=MISSING_COLUMNS)

def _coverage_trust_safe_text(value: Any, *, fallback: str) -> str:
    text = str(value or "").strip()
    if not text or text == "-":
        return fallback
    lowered = text.lower()
    if any(term in lowered for term in ("delisted", "suspended", "halt", "illegal", "fraud")):
        return "Listing/profile evidence 확인 필요."
    return text

def _coverage_trust_int(value: Any) -> int:
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric):
        return 0
    return int(numeric)

def _coverage_trust_pct(value: Any) -> str:
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric):
        return "-"
    return f"{float(numeric):.1f}%"

def _coverage_trust_timestamp(coverage: dict[str, Any]) -> str:
    return str(
        coverage.get("snapshot_time_utc")
        or coverage.get("effective_end_date")
        or coverage.get("latest_raw_date")
        or "-"
    )

def _coverage_trust_state(
    snapshot: dict[str, Any],
    coverage: dict[str, Any],
    missing_rows: pd.DataFrame,
) -> tuple[str, str]:
    status = str(snapshot.get("status") or "").strip().upper()
    refresh_status = str(dict(coverage.get("refresh_state") or {}).get("status") or "").strip().lower()
    universe_count = _coverage_trust_int(coverage.get("universe_count"))
    returnable_count = _coverage_trust_int(coverage.get("returnable_count"))
    missing_count = max(_coverage_trust_int(coverage.get("missing_count")), len(missing_rows))
    price_mode = str(coverage.get("price_mode") or "")

    if status == "NO_UNIVERSE" or (universe_count <= 0 and returnable_count <= 0):
        return "No Universe", "warning"
    if status in {"ERROR"} or refresh_status == "failed":
        return "Needs Refresh", "danger"
    if status in {"INSUFFICIENT_DATA"} or refresh_status == "due":
        return "Needs Refresh", "warning"
    if refresh_status == "stale":
        return "Stale", "danger"
    if missing_count:
        reason_text = " ".join(missing_rows.get("Reason", pd.Series(dtype=str)).dropna().astype(str).tolist()).lower()
        if price_mode == "Intraday Snapshot" or any(token in reason_text for token in ("quote", "intraday", "latest")):
            return "Missing Quotes", "warning"
        return "Partial", "warning"
    if universe_count and returnable_count < universe_count:
        return "Partial", "warning"
    return "Good", "positive"

def _coverage_trust_headline(
    *,
    state: str,
    snapshot: dict[str, Any],
    coverage: dict[str, Any],
    missing_count: int,
) -> tuple[str, str]:
    universe_code = str(snapshot.get("universe_code") or "")
    universe_label = str(snapshot.get("universe_label") or UNIVERSE_LABELS.get(universe_code, universe_code) or "Coverage")
    refresh_state = dict(coverage.get("refresh_state") or {})
    detail = str(refresh_state.get("detail") or snapshot.get("message") or "")
    if state == "No Universe" and universe_code == "NASDAQ":
        return (
            "Nasdaq Symbol Directory current snapshot이 비어 있습니다.",
            "Nasdaq-listed coverage는 DB의 Symbol Directory current listing snapshot을 먼저 읽습니다.",
        )
    if state == "No Universe":
        return (
            f"{universe_label} universe row가 비어 있습니다.",
            "유니버스 refresh 후 Market Movers snapshot을 다시 읽어야 합니다.",
        )
    if state == "Missing Quotes":
        return (
            f"{universe_label} quote 누락 {missing_count:,}건이 있습니다.",
            detail or "그룹 요약을 먼저 보고 raw row는 필요할 때만 확인하세요.",
        )
    if state == "Partial":
        return (
            f"{universe_label} 일부 row가 ranking에서 제외되었습니다.",
            detail or "가격 history/profile/listing evidence를 함께 확인해야 합니다.",
        )
    if state == "Stale":
        return (
            f"{universe_label} snapshot이 오래되었습니다.",
            detail or "갱신 후 현재 coverage를 다시 확인하세요.",
        )
    if state == "Needs Refresh":
        return (
            f"{universe_label} 자료 갱신이 필요합니다.",
            detail or str(snapshot.get("message") or "현재 선택 조건의 ranking row를 만들기 어렵습니다."),
        )
    return (
        f"{universe_label} coverage가 정상 범위입니다.",
        detail or "현재 read model 기준으로 누락 row가 없습니다.",
    )

def _coverage_trust_grouped_missing_rows(
    snapshot: dict[str, Any],
    missing_rows: pd.DataFrame,
) -> pd.DataFrame:
    status = str(snapshot.get("status") or "").upper()
    universe_code = str(snapshot.get("universe_code") or "")
    if missing_rows.empty:
        if status == "NO_UNIVERSE":
            if universe_code == "NASDAQ":
                return pd.DataFrame(
                    [
                        {
                            "Missing Reason Group": "No universe",
                            "Likely Cause": "Nasdaq Symbol Directory current snapshot is not loaded in DB.",
                            "Suggested Next Action": "Nasdaq 목록 갱신 후 Market Movers를 다시 읽으세요.",
                            "Affected Count": 0,
                            "Sample Tickers": "-",
                        }
                    ],
                    columns=COVERAGE_TRUST_GROUP_COLUMNS,
                )
            return pd.DataFrame(
                [
                    {
                        "Missing Reason Group": "No universe",
                        "Likely Cause": "Selected universe rows are not available in DB.",
                        "Suggested Next Action": "Universe refresh 후 Market Movers를 다시 읽으세요.",
                        "Affected Count": 0,
                        "Sample Tickers": "-",
                    }
                ],
                columns=COVERAGE_TRUST_GROUP_COLUMNS,
            )
        return pd.DataFrame(columns=COVERAGE_TRUST_GROUP_COLUMNS)

    normalized_rows: list[dict[str, Any]] = []
    for row in missing_rows.to_dict(orient="records"):
        reason = _coverage_trust_safe_text(row.get("Reason"), fallback="Unclassified missing row")
        likely = _coverage_trust_safe_text(row.get("Likely Cause"), fallback="Price/listing evidence 확인 필요.")
        action = _coverage_trust_safe_text(
            row.get("Recommended Action") or row.get("Next Check"),
            fallback="Refresh the relevant DB-backed snapshot, then reopen raw diagnostics if the gap repeats.",
        )
        symbol = str(row.get("Symbol") or "").strip().upper()
        normalized_rows.append(
            {
                "Missing Reason Group": reason,
                "Likely Cause": likely,
                "Suggested Next Action": action,
                "Symbol": symbol,
            }
        )

    grouped: list[dict[str, Any]] = []
    frame = pd.DataFrame(normalized_rows)
    group_columns = ["Missing Reason Group", "Likely Cause", "Suggested Next Action"]
    for keys, group in frame.groupby(group_columns, dropna=False, sort=False):
        reason, likely, action = keys
        symbols = [symbol for symbol in group["Symbol"].tolist() if symbol]
        grouped.append(
            {
                "Missing Reason Group": reason,
                "Likely Cause": likely,
                "Suggested Next Action": action,
                "Affected Count": int(len(group)),
                "Sample Tickers": ", ".join(symbols[:8]) if symbols else "-",
            }
        )
    grouped.sort(key=lambda row: int(row["Affected Count"]), reverse=True)
    return pd.DataFrame(grouped, columns=COVERAGE_TRUST_GROUP_COLUMNS)

def _coverage_trust_suggested_action(
    *,
    state: str,
    snapshot: dict[str, Any],
    coverage: dict[str, Any],
) -> dict[str, Any]:
    universe_code = str(snapshot.get("universe_code") or "")
    refresh_state = dict(coverage.get("refresh_state") or {})
    if state == "No Universe" and universe_code == "NASDAQ":
        return {
            "label": "Nasdaq 목록 갱신",
            "action_id": "overview_nasdaq_symbol_directory",
            "result_key": "overview_nasdaq_symbol_directory_result",
            "detail": "기존 Overview action facade를 통해 Symbol Directory current snapshot을 DB에 저장합니다.",
        }
    if state in {"Missing Quotes", "Partial"}:
        return {
            "label": "Open raw diagnostics",
            "action_id": "open_raw_diagnostics",
            "detail": "Grouped summary 아래의 raw diagnostics에서 symbol-level evidence를 확인합니다.",
        }
    if state in {"Stale", "Needs Refresh"}:
        return {
            "label": str(refresh_state.get("recommended_action") or "Refresh current coverage"),
            "action_id": "use_existing_refresh_bar",
            "detail": "상단 데이터 갱신 control을 사용합니다.",
        }
    return {
        "label": "No action needed",
        "action_id": "none",
        "detail": "현재 read model 기준의 보조 신뢰 상태입니다.",
    }

def build_market_movers_coverage_trust_model(snapshot: dict[str, Any]) -> dict[str, Any]:
    coverage = dict(snapshot.get("coverage") or {})
    missing_rows = _coverage_trust_missing_rows(snapshot)
    missing_count = max(_coverage_trust_int(coverage.get("missing_count")), len(missing_rows))
    state, tone = _coverage_trust_state(snapshot, coverage, missing_rows)
    headline, detail = _coverage_trust_headline(
        state=state,
        snapshot=snapshot,
        coverage=coverage,
        missing_count=missing_count,
    )
    universe_count = _coverage_trust_int(coverage.get("universe_count"))
    returnable_count = _coverage_trust_int(coverage.get("returnable_count"))
    return {
        "schema_version": "market_movers_coverage_trust_v1",
        "state": state,
        "tone": tone,
        "headline": headline,
        "detail": detail,
        "items": [
            {"label": "Coverage", "value": str(snapshot.get("universe_label") or "-")},
            {"label": "Freshness", "value": state, "detail": _coverage_trust_timestamp(coverage)},
            {"label": "Universe", "value": f"{universe_count:,}"},
            {
                "label": "Returnable",
                "value": f"{returnable_count:,}",
                "detail": _coverage_trust_pct(coverage.get("returnable_pct")),
            },
            {"label": "Missing", "value": f"{missing_count:,}"},
        ],
        "grouped_missing_rows": _coverage_trust_grouped_missing_rows(snapshot, missing_rows),
        "raw_missing_rows": missing_rows,
        "raw_detail_default_expanded": False,
        "suggested_action": _coverage_trust_suggested_action(
            state=state,
            snapshot=snapshot,
            coverage=coverage,
        ),
        "boundary_note": (
            "Coverage trust is context-only data-quality evidence for the current Market Movers view; "
            "it is not a trading signal, validation gate, Final Review decision, or operations monitoring signal."
        ),
    }

def _universe_metadata(universe: list[dict[str, Any]], *, universe_code: str) -> dict[str, Any]:
    if not universe:
        return {}
    if universe_code == "SP500":
        first = universe[0]
        return {
            "universe_as_of_date": _iso_date(first.get("universe_as_of_date")),
            "universe_collected_at": _display_datetime(first.get("universe_collected_at")),
            "universe_source": first.get("universe_source"),
            "universe_source_url": first.get("universe_source_url"),
            "coverage_basis": "Current S&P 500 constituents",
        }
    if universe_code == "NASDAQ":
        first = universe[0]
        return {
            "universe_event_date": _iso_date(first.get("universe_event_date") or first.get("event_date")),
            "universe_collected_at": _display_datetime(first.get("universe_collected_at")),
            "universe_source": first.get("universe_source"),
            "universe_source_url": first.get("universe_source_url"),
            "universe_source_type": first.get("universe_source_type") or first.get("source_type"),
            "universe_coverage_status": first.get("universe_coverage_status") or first.get("coverage_status"),
            "universe_event_type": first.get("universe_event_type") or first.get("event_type"),
            "universe_listing_status": first.get("universe_listing_status") or first.get("listing_status"),
            "universe_caveat": "Nasdaq Symbol Directory is current listing observation only; not historical membership proof.",
            "coverage_basis": "Nasdaq-listed current snapshot",
        }
    if universe_code in {"TOP1000", "TOP2000"}:
        first = universe[0]
        return {
            "universe_as_of_date": _iso_date(first.get("universe_as_of_date")),
            "universe_collected_at": _display_datetime(first.get("universe_collected_at")),
            "universe_source": first.get("universe_source"),
            "universe_price_source": first.get("universe_price_source"),
            "universe_caveat": "Top universe is ranked by recent 20D average dollar volume, not company size.",
            "coverage_basis": "20D avg dollar volume materialized universe",
        }
    collected = [
        _display_datetime(row.get("last_collected_at"))
        for row in universe
        if _display_datetime(row.get("last_collected_at"))
    ]
    return {
        "profile_collected_at_max": max(collected) if collected else None,
        "coverage_basis": "Latest asset_profile.market_cap snapshot",
    }

def _rows_frame(rows: list[dict[str, Any]], *, columns: list[str]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=columns)

def _cockpit_frame(snapshot: dict[str, Any], key: str = "rows") -> pd.DataFrame:
    rows = snapshot.get(key)
    if isinstance(rows, pd.DataFrame):
        return rows
    if isinstance(rows, list):
        return pd.DataFrame(rows)
    return pd.DataFrame()

def _cockpit_int(value: Any) -> int:
    try:
        if value in (None, ""):
            return 0
        return int(value)
    except (TypeError, ValueError):
        return 0

def _overview_round(value: Any, *, digits: int = 1) -> float | None:
    numeric = _safe_float(value)
    if numeric is None:
        return None
    return round(numeric, digits)

def _overview_percent_label(value: Any, *, digits: int = 0, signed: bool = False) -> str:
    numeric = _safe_float(value)
    if numeric is None:
        return "-"
    sign = "+" if signed else ""
    return f"{numeric:{sign}.{digits}f}%"

def _overview_breadth_participation_label(positive_share: float | None) -> str:
    if positive_share is None:
        return "unknown"
    if positive_share >= 65.0:
        return "broad"
    if positive_share <= 45.0:
        return "narrow"
    return "mixed"

def _overview_breadth_concentration_label(top_share: float | None, cap_equal_gap: float | None) -> str:
    if top_share is None and cap_equal_gap is None:
        return "unknown"
    if (top_share is not None and top_share >= 65.0) or (cap_equal_gap is not None and abs(cap_equal_gap) >= 2.0):
        return "concentrated"
    return "balanced"

def _overview_breadth_row_tone(row: dict[str, Any]) -> str:
    weighted = _safe_float(row.get("Market Cap Weighted Return %"))
    positive_share = _safe_float(row.get("Positive Symbol Share %"))
    if weighted is not None and weighted < 0:
        return "danger"
    if positive_share is not None and positive_share < 45.0:
        return "warning"
    if weighted is not None and weighted > 0:
        return "positive"
    return "neutral"

_OVERVIEW_SECTOR_DISPLAY_ALIASES = {
    "communication services": "Communication Services",
    "communications": "Communication Services",
    "consumer cyclical": "Consumer Cyclical",
    "consumer discretionary": "Consumer Cyclical",
    "consumer defensive": "Consumer Defensive",
    "consumer staples": "Consumer Defensive",
    "energy": "Energy",
    "financials": "Financial Services",
    "financial services": "Financial Services",
    "finance": "Financial Services",
    "healthcare": "Healthcare",
    "health care": "Healthcare",
    "industrials": "Industrials",
    "industrial": "Industrials",
    "basic materials": "Basic Materials",
    "materials": "Basic Materials",
    "real estate": "Real Estate",
    "realestate": "Real Estate",
    "technology": "Technology",
    "information technology": "Technology",
    "tech": "Technology",
    "utilities": "Utilities",
    "utility": "Utilities",
}

def _overview_normalized_label(value: Any) -> str:
    text = str(value or "").strip().lower().replace("&", " and ")
    normalized = "".join(char if char.isalnum() else " " for char in text)
    return " ".join(normalized.split())

def _overview_sector_display_label(value: Any) -> str:
    raw = str(value or "").strip() or "-"
    return _OVERVIEW_SECTOR_DISPLAY_ALIASES.get(_overview_normalized_label(raw), raw)

def _weighted_average(values: list[tuple[float | None, float]]) -> float | None:
    usable = [(float(value), float(weight)) for value, weight in values if value is not None and float(weight) > 0]
    if not usable:
        return None
    weight_sum = sum(weight for _, weight in usable)
    if weight_sum <= 0:
        return None
    return sum(value * weight for value, weight in usable) / weight_sum

def _canonical_sector_rows(rows: pd.DataFrame) -> pd.DataFrame:
    if rows.empty or "Group" not in rows:
        return rows

    grouped: dict[str, list[dict[str, Any]]] = {}
    changed = False
    for _, row_value in rows.iterrows():
        row = dict(row_value.dropna().to_dict())
        original = str(row.get("Group") or "").strip()
        label = _overview_sector_display_label(row.get("Group"))
        changed = changed or bool(original and label != original)
        grouped.setdefault(label, []).append(row)

    if len(grouped) == len(rows) and not changed:
        return rows

    merged_rows: list[dict[str, Any]] = []
    for label, group_rows in grouped.items():
        symbols = sum(_cockpit_int(row.get("Symbols")) for row in group_rows)
        positive_symbols = sum(_cockpit_int(row.get("Positive Symbols")) for row in group_rows)
        weights = [float(_cockpit_int(row.get("Symbols")) or 1) for row in group_rows]
        weighted_return = _weighted_average(
            [(_safe_float(row.get("Market Cap Weighted Return %")), weights[index]) for index, row in enumerate(group_rows)]
        )
        equal_return = _weighted_average(
            [(_safe_float(row.get("Equal Weight Return %")), weights[index]) for index, row in enumerate(group_rows)]
        )
        top_share = _weighted_average(
            [(_safe_float(row.get("Top 3 Positive Share %")), weights[index]) for index, row in enumerate(group_rows)]
        )
        top_row = max(group_rows, key=lambda row: _safe_float(row.get("Top Symbol Return %")) or float("-inf"))
        merged_rows.append(
            {
                **group_rows[0],
                "Group": label,
                "Symbols": symbols or None,
                "Positive Symbols": positive_symbols or None,
                "Positive Symbol Share %": (positive_symbols / symbols * 100.0) if symbols else None,
                "Market Cap Weighted Return %": weighted_return,
                "Equal Weight Return %": equal_return,
                "Top 3 Positive Share %": top_share,
                "Top Symbol": top_row.get("Top Symbol"),
                "Top Symbol Return %": top_row.get("Top Symbol Return %"),
            }
        )

    merged = pd.DataFrame(merged_rows)
    if "Market Cap Weighted Return %" in merged:
        merged = merged.sort_values("Market Cap Weighted Return %", ascending=False, na_position="last", kind="mergesort")
    merged = merged.reset_index(drop=True)
    merged["Rank"] = range(1, len(merged) + 1)
    return merged

def build_overview_breadth_heatmap_summary(
    group_leadership_snapshot: dict[str, Any] | None = None,
    *,
    limit: int | None = None,
) -> dict[str, Any]:
    """Compress an existing group leadership snapshot into a context-only breadth heatmap summary."""
    snapshot = group_leadership_snapshot or {}
    rows = _canonical_sector_rows(_cockpit_frame(snapshot))
    coverage = dict(snapshot.get("coverage") or {})
    date_window = dict(snapshot.get("date_window") or {})
    if rows.empty:
        return {
            "schema_version": "overview_breadth_heatmap_summary_v1",
            "status": "NO_DATA",
            "summary": {
                "headline": "Breadth context unavailable",
                "detail": str(snapshot.get("message") or "No stored group leadership rows are available."),
                "participation_label": "unknown",
                "concentration_label": "unknown",
                "leader": None,
            },
            "coverage": {
                "group_count": 0,
                "returnable_count": coverage.get("returnable_count"),
                "universe_count": coverage.get("universe_count"),
                "price_mode": coverage.get("price_mode"),
                "freshness": coverage.get("snapshot_time_utc") or coverage.get("effective_end_date"),
            },
            "cards": [],
            "heatmap_rows": [],
            "boundary_note": (
                "Context-only breadth summary: not a trading action, not validation, not Final Review, "
                "and not monitoring guidance."
            ),
        }

    numeric_positive = rows.get("Positive Symbol Share %", pd.Series(dtype=float)).map(_safe_float).dropna()
    numeric_weighted = rows.get("Market Cap Weighted Return %", pd.Series(dtype=float)).map(_safe_float).dropna()
    negative_count = int((numeric_weighted < 0).sum()) if not numeric_weighted.empty else 0
    positive_group_count = int((numeric_weighted > 0).sum()) if not numeric_weighted.empty else 0
    average_positive_share = round(float(numeric_positive.mean()), 1) if not numeric_positive.empty else None
    average_weighted_return = round(float(numeric_weighted.mean()), 2) if not numeric_weighted.empty else None
    top_row = dict(rows.iloc[0].dropna().to_dict())
    leader = str(top_row.get("Group") or "-")
    leader_return = _safe_float(top_row.get("Market Cap Weighted Return %"))
    top_share = _safe_float(top_row.get("Top 3 Positive Share %"))
    cap_equal_gap = _safe_float(top_row.get("Cap vs Equal Gap pp"))
    participation_label = _overview_breadth_participation_label(average_positive_share)
    concentration_label = _overview_breadth_concentration_label(top_share, cap_equal_gap)

    heatmap_rows: list[dict[str, Any]] = []
    visible_rows = rows if limit is None else rows.head(max(1, int(limit or 10)))
    for fallback_rank, (_, row_value) in enumerate(visible_rows.iterrows(), start=1):
        row = dict(row_value.dropna().to_dict())
        heatmap_rows.append(
            {
                "rank": _cockpit_int(row.get("Rank")) or fallback_rank,
                "group": str(row.get("Group") or "-"),
                "symbols": _cockpit_int(row.get("Symbols")),
                "positive_symbols": _cockpit_int(row.get("Positive Symbols")),
                "positive_symbol_share_pct": _overview_round(row.get("Positive Symbol Share %")),
                "market_cap_weighted_return_pct": _overview_round(row.get("Market Cap Weighted Return %")),
                "equal_weight_return_pct": _overview_round(row.get("Equal Weight Return %")),
                "top_3_positive_share_pct": _overview_round(row.get("Top 3 Positive Share %")),
                "top_symbol": str(row.get("Top Symbol") or "-"),
                "top_symbol_return_pct": _overview_round(row.get("Top Symbol Return %")),
                "tone": _overview_breadth_row_tone(row),
            }
        )

    group_label = "groups" if len(rows) != 1 else "group"
    cards = [
        {
            "title": "Participation",
            "value": _overview_percent_label(average_positive_share),
            "detail": f"{participation_label} average positive share across {len(rows)} {group_label}",
            "tone": "positive" if participation_label == "broad" else "warning" if participation_label == "narrow" else "neutral",
        },
        {
            "title": "Leadership",
            "value": leader,
            "detail": f"{_overview_percent_label(leader_return, digits=1, signed=True)} cap-weighted return",
            "tone": _overview_breadth_row_tone(top_row),
        },
        {
            "title": "Concentration",
            "value": concentration_label,
            "detail": f"Top 3 positive share {_overview_percent_label(top_share)} · cap/equal gap {_overview_percent_label(cap_equal_gap, digits=1, signed=True)}",
            "tone": "warning" if concentration_label == "concentrated" else "positive" if concentration_label == "balanced" else "neutral",
        },
        {
            "title": "Negative Groups",
            "value": str(negative_count),
            "detail": f"{positive_group_count} positive groups · avg cap-weighted {_overview_percent_label(average_weighted_return, digits=2, signed=True)}",
            "tone": "warning" if negative_count else "positive",
        },
    ]

    return {
        "schema_version": "overview_breadth_heatmap_summary_v1",
        "status": snapshot.get("status") or "OK",
        "summary": {
            "headline": f"{participation_label.title()} participation, {concentration_label} leadership",
            "detail": (
                f"{leader} leads the selected universe; use the heatmap to see whether movement is broad or group-specific."
            ),
            "participation_label": participation_label,
            "concentration_label": concentration_label,
            "leader": leader,
        },
        "coverage": {
            "group_count": int(len(rows)),
            "returnable_count": coverage.get("returnable_count"),
            "universe_count": coverage.get("universe_count"),
            "price_mode": coverage.get("price_mode") or "EOD DB",
            "freshness": coverage.get("snapshot_time_utc")
            or coverage.get("effective_end_date")
            or date_window.get("effective_end_date")
            or date_window.get("end_date"),
        },
        "cards": cards,
        "heatmap_rows": heatmap_rows,
        "boundary_note": (
            "Context-only breadth summary: not a trading action, not validation, not Final Review, "
            "and not monitoring guidance."
        ),
    }

def _empty_market_movers_sector_breadth_model(message: str = "") -> dict[str, Any]:
    return {
        "schema_version": "market_movers_sector_breadth_v1",
        "status": "NO_DATA",
        "summary": {
            "headline": "Sector breadth context unavailable",
            "detail": message or "No returnable sector rows are available for this selection.",
            "participation_label": "unknown",
            "concentration_label": "unknown",
            "leader": None,
        },
        "coverage": {
            "group_count": 0,
            "returnable_count": None,
            "universe_count": None,
            "price_mode": "Unavailable",
            "freshness": None,
        },
        "cards": [],
        "heatmap_rows": [],
        "table_rows": [],
        "table_columns": SECTOR_BREADTH_TABLE_COLUMNS,
        "boundary_note": (
            "Context-only sector breadth: not a trading action, recommendation, validation gate, "
            "Final Review decision, or monitoring guidance."
        ),
    }


def _build_market_movers_sector_breadth_model(
    return_rows: list[dict[str, Any]],
    *,
    coverage: dict[str, Any],
    date_window: dict[str, Any],
) -> dict[str, Any]:
    if not return_rows:
        model = _empty_market_movers_sector_breadth_model()
        model["coverage"].update(
            {
                "returnable_count": coverage.get("returnable_count"),
                "universe_count": coverage.get("universe_count"),
                "price_mode": coverage.get("price_mode") or "Unavailable",
                "freshness": coverage.get("snapshot_time_utc")
                or coverage.get("effective_end_date")
                or date_window.get("effective_end_date"),
            }
        )
        return model

    canonical_rows = [
        {
            **row,
            "sector": _overview_sector_display_label(row.get("sector"))
            if _overview_sector_display_label(row.get("sector")) != "-"
            else "Unknown",
        }
        for row in return_rows
    ]
    start_date = str(canonical_rows[0].get("start_date") or date_window.get("start_date") or "-")
    end_date = str(canonical_rows[0].get("end_date") or date_window.get("end_date") or "-")
    group_rows = _rank_group_rows(
        _group_leadership_rows(
            return_rows=canonical_rows,
            group_by="sector",
            min_group_size=1,
            start_date=start_date,
            end_date=end_date,
        ),
        top_n=None,
    )
    group_frame = _group_rows_frame(group_rows)
    summary_model = build_overview_breadth_heatmap_summary(
        {
            "status": "OK",
            "coverage": coverage,
            "date_window": date_window,
            "rows": group_frame,
        },
        limit=None,
    )

    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in canonical_rows:
        grouped.setdefault(str(row.get("sector") or "Unknown"), []).append(row)
    total_market_cap = sum(max(float(_safe_float(row.get("market_cap")) or 0.0), 0.0) for row in canonical_rows)

    table_rows: list[dict[str, Any]] = []
    for rank, group_row in enumerate(group_rows, start=1):
        sector = str(group_row.get("group") or "Unknown")
        members = grouped.get(sector, [])
        returns = [_safe_float(row.get("return_pct")) for row in members]
        usable_returns = [float(value) for value in returns if value is not None]
        if not usable_returns:
            continue
        top_gainer = max(members, key=lambda row: _safe_float(row.get("return_pct")) or float("-inf"))
        top_loser = min(members, key=lambda row: _safe_float(row.get("return_pct")) or float("inf"))
        advancers = int(group_row.get("positive_symbols") or 0)
        decliners = sum(1 for value in usable_returns if value < 0)
        sector_market_cap = sum(max(float(_safe_float(row.get("market_cap")) or 0.0), 0.0) for row in members)
        table_rows.append(
            {
                "Rank": rank,
                "Sector": sector,
                "Symbols": int(group_row.get("symbols") or len(members)),
                "Advancers": advancers,
                "Decliners": decliners,
                "Advancer Share %": round(float(group_row.get("positive_symbol_share") or 0.0), 2),
                "Equal Weight Return %": round(float(group_row.get("equal_weight_return") or 0.0), 2),
                "Median Return %": round(float(pd.Series(usable_returns).median()), 2),
                "Market Cap Weighted Return %": round(float(group_row.get("market_cap_weighted_return") or 0.0), 2),
                "Market Cap Share %": round((sector_market_cap / total_market_cap) * 100.0, 2)
                if total_market_cap > 0
                else None,
                "Top Gainer": str(top_gainer.get("symbol") or "-"),
                "Top Gainer Return %": round(float(_safe_float(top_gainer.get("return_pct")) or 0.0), 2),
                "Top Loser": str(top_loser.get("symbol") or "-"),
                "Top Loser Return %": round(float(_safe_float(top_loser.get("return_pct")) or 0.0), 2),
                "Start Date": start_date,
                "End Date": end_date,
            }
        )

    table_by_sector = {row["Sector"]: row for row in table_rows}
    heatmap_rows = []
    for row in list(summary_model.get("heatmap_rows") or []):
        enriched = dict(row)
        table_row = table_by_sector.get(str(row.get("group") or ""))
        if table_row:
            enriched.update(
                {
                    "advancers": table_row["Advancers"],
                    "decliners": table_row["Decliners"],
                    "median_return_pct": table_row["Median Return %"],
                    "market_cap_share_pct": table_row["Market Cap Share %"],
                    "top_loser": table_row["Top Loser"],
                    "top_loser_return_pct": table_row["Top Loser Return %"],
                }
            )
        heatmap_rows.append(enriched)

    return {
        **summary_model,
        "schema_version": "market_movers_sector_breadth_v1",
        "status": "OK",
        "heatmap_rows": heatmap_rows,
        "table_rows": table_rows,
        "table_columns": SECTOR_BREADTH_TABLE_COLUMNS,
        "boundary_note": (
            "Context-only sector breadth: not a trading action, recommendation, validation gate, "
            "Final Review decision, or monitoring guidance."
        ),
    }


def _ranked_return_frame(
    rows: list[dict[str, Any]],
    *,
    top_n: int,
    ascending: bool = False,
    negative_only: bool = False,
) -> pd.DataFrame:
    source_rows = [
        row
        for row in rows
        if (not negative_only or (_safe_float(row.get("return_pct")) is not None and float(row["return_pct"]) < 0))
    ]
    ranked = sorted(
        source_rows,
        key=lambda row: (
            float(row["return_pct"]) if ascending else -float(row["return_pct"]),
            row["symbol"],
        ),
    )[:top_n]
    out = [
        {
            "Rank": index,
            "Symbol": row["symbol"],
            "Name": row["name"] or "-",
            "Return %": round(float(row["return_pct"]), 2),
            "Previous Return %": round(float(row["previous_return_pct"]), 2)
            if row.get("previous_return_pct") is not None
            else None,
            "Momentum Delta pp": round(float(row["momentum_delta_pp"]), 2)
            if row.get("momentum_delta_pp") is not None
            else None,
            "Volume": int(row["volume"]) if row.get("volume") is not None else None,
            "Dollar Volume": round(float(row["dollar_volume"]), 2)
            if row.get("dollar_volume") is not None
            else None,
            "Start Price": round(float(row["start_price"]), 4),
            "End Price": round(float(row["end_price"]), 4),
            "Sector": row["sector"],
            "Industry": row["industry"],
            "Market Cap": int(row["market_cap"]) if row["market_cap"] else None,
            "Start Date": row["start_date"],
            "End Date": row["end_date"],
            "Previous Start Date": row.get("previous_start_date") or "-",
            "Previous End Date": row.get("previous_end_date") or "-",
            "Price Source": row.get("price_source") or "EOD DB",
        }
        for index, row in enumerate(ranked, start=1)
    ]
    return _rows_frame(out, columns=MOVERS_COLUMNS)

def _ranked_movers_frame(rows: list[dict[str, Any]], *, top_n: int) -> pd.DataFrame:
    return _ranked_return_frame(rows, top_n=top_n)

def _ranked_losers_frame(rows: list[dict[str, Any]], *, top_n: int) -> pd.DataFrame:
    return _ranked_return_frame(rows, top_n=top_n, ascending=True, negative_only=True)

def _current_period_volume_dates(date_window: dict[str, Any], *, period: str) -> list[str]:
    normalized_period = str(period or "daily").strip().lower()
    offset = VALID_PERIODS.get(normalized_period, 1)
    dates = [
        row_date
        for row in list(date_window.get("eligible_dates") or [])[: max(1, offset)]
        if (row_date := _iso_date(row.get("date")))
    ]
    if dates:
        return dates
    end_date = _iso_date(date_window.get("end_date"))
    return [end_date] if end_date else []

def _load_period_volume_stats(
    *,
    symbols: list[str],
    dates: list[str],
    query_fn: QueryFn,
) -> dict[str, dict[str, Any]]:
    if not symbols or not dates:
        return {}
    symbol_placeholders = ",".join(["%s"] * len(symbols))
    date_placeholders = ",".join(["%s"] * len(dates))
    rows = query_fn(
        "finance_price",
        f"""
        SELECT
            symbol,
            SUM(CASE WHEN volume IS NOT NULL THEN volume ELSE 0 END) AS total_volume,
            AVG(volume) AS avg_daily_volume,
            SUM(
                CASE
                    WHEN volume IS NOT NULL AND COALESCE(adj_close, close) IS NOT NULL
                    THEN COALESCE(adj_close, close) * volume
                    ELSE 0
                END
            ) AS total_dollar_volume,
            AVG(
                CASE
                    WHEN volume IS NOT NULL AND COALESCE(adj_close, close) IS NOT NULL
                    THEN COALESCE(adj_close, close) * volume
                    ELSE NULL
                END
            ) AS avg_daily_dollar_volume,
            COUNT(volume) AS volume_days
        FROM nyse_price_history FORCE INDEX (uk_symbol_timeframe_date)
        WHERE symbol IN ({symbol_placeholders})
          AND timeframe = %s
          AND `date` IN ({date_placeholders})
        GROUP BY symbol
        """,
        list(symbols) + ["1d"] + list(dates),
    )
    stats: dict[str, dict[str, Any]] = {}
    for row in rows:
        symbol = str(row.get("symbol") or "").strip().upper()
        if not symbol:
            continue
        stats[symbol] = {
            "total_volume": _safe_float(row.get("total_volume")),
            "avg_daily_volume": _safe_float(row.get("avg_daily_volume")),
            "total_dollar_volume": _safe_float(row.get("total_dollar_volume")),
            "avg_daily_dollar_volume": _safe_float(row.get("avg_daily_dollar_volume")),
            "volume_days": int(row.get("volume_days") or 0),
        }
    return stats

def _volume_metric(*values: Any) -> float | None:
    for value in values:
        numeric = _safe_float(value)
        if numeric is not None and numeric > 0:
            return numeric
    return None

def _ranked_volume_frame(
    return_rows: list[dict[str, Any]],
    *,
    top_n: int,
    period: str,
    volume_stats: dict[str, dict[str, Any]] | None = None,
) -> pd.DataFrame:
    normalized_period = str(period or "daily").strip().lower()
    volume_stats = volume_stats or {}
    ranked_rows: list[dict[str, Any]] = []
    for row in return_rows:
        symbol = str(row.get("symbol") or "").strip().upper()
        if not symbol:
            continue
        volume = _safe_float(row.get("volume"))
        dollar_volume = _safe_float(row.get("dollar_volume"))
        if normalized_period == "daily":
            avg_daily_volume = volume
            total_volume = volume
            avg_daily_dollar_volume = dollar_volume
            total_dollar_volume = dollar_volume
            volume_days = 1 if volume is not None else 0
            volume_basis = "Daily dollar volume"
            metric = _volume_metric(dollar_volume, volume)
        else:
            stats = volume_stats.get(symbol) or {}
            avg_daily_volume = _safe_float(stats.get("avg_daily_volume"))
            total_volume = _safe_float(stats.get("total_volume"))
            avg_daily_dollar_volume = _safe_float(stats.get("avg_daily_dollar_volume"))
            total_dollar_volume = _safe_float(stats.get("total_dollar_volume"))
            volume_days = int(stats.get("volume_days") or 0)
            volume_basis = "Avg daily dollar volume"
            metric = _volume_metric(
                avg_daily_dollar_volume,
                total_dollar_volume,
                avg_daily_volume,
                total_volume,
            )
        if metric is None:
            continue
        ranked_rows.append(
            {
                "symbol": symbol,
                "name": row.get("name") or "-",
                "volume_metric": metric,
                "volume_basis": volume_basis,
                "volume": avg_daily_volume if normalized_period != "daily" else volume,
                "dollar_volume": avg_daily_dollar_volume if normalized_period != "daily" else dollar_volume,
                "avg_daily_volume": avg_daily_volume,
                "total_volume": total_volume,
                "avg_daily_dollar_volume": avg_daily_dollar_volume,
                "total_dollar_volume": total_dollar_volume,
                "volume_days": volume_days,
                "return_pct": row.get("return_pct"),
                "sector": row.get("sector") or "Unknown",
                "industry": row.get("industry") or "Unknown",
                "market_cap": row.get("market_cap"),
                "start_date": row.get("start_date"),
                "end_date": row.get("end_date"),
                "price_source": row.get("price_source") or "EOD DB",
            }
        )

    ranked = sorted(ranked_rows, key=lambda item: (-float(item["volume_metric"]), item["symbol"]))[:top_n]
    out = [
        {
            "Rank": index,
            "Symbol": row["symbol"],
            "Name": row["name"] or "-",
            "Volume Metric": round(float(row["volume_metric"]), 2),
            "Volume Basis": row["volume_basis"],
            "Volume": int(round(float(row["volume"]))) if row.get("volume") is not None else None,
            "Dollar Volume": round(float(row["dollar_volume"]), 2)
            if row.get("dollar_volume") is not None
            else None,
            "Avg Daily Volume": int(round(float(row["avg_daily_volume"])))
            if row.get("avg_daily_volume") is not None
            else None,
            "Total Volume": int(round(float(row["total_volume"]))) if row.get("total_volume") is not None else None,
            "Avg Daily Dollar Volume": round(float(row["avg_daily_dollar_volume"]), 2)
            if row.get("avg_daily_dollar_volume") is not None
            else None,
            "Total Dollar Volume": round(float(row["total_dollar_volume"]), 2)
            if row.get("total_dollar_volume") is not None
            else None,
            "Volume Days": int(row.get("volume_days") or 0),
            "Return %": round(float(row["return_pct"]), 2) if row.get("return_pct") is not None else None,
            "Sector": row["sector"],
            "Industry": row["industry"],
            "Market Cap": int(row["market_cap"]) if row.get("market_cap") else None,
            "Start Date": row["start_date"],
            "End Date": row["end_date"],
            "Price Source": row["price_source"],
        }
        for index, row in enumerate(ranked, start=1)
    ]
    return _rows_frame(out, columns=VOLUME_COLUMNS)

def _relative_volume_baseline_dates(
    date_window: dict[str, Any],
    *,
    period: str,
    skip_current_period: bool = True,
) -> list[str]:
    normalized_period = str(period or "daily").strip().lower()
    offset = VALID_PERIODS.get(normalized_period, 1)
    start_index = offset if skip_current_period else 0
    dates = [
        row_date
        for row in list(date_window.get("eligible_dates") or [])[start_index : start_index + 10]
        if (row_date := _iso_date(row.get("date")))
    ]
    return dates[:10]

def _load_relative_volume_baselines(
    *,
    symbols: list[str],
    dates: list[str],
    query_fn: QueryFn,
) -> dict[str, dict[str, Any]]:
    if not symbols or not dates:
        return {}
    symbol_placeholders = ",".join(["%s"] * len(symbols))
    date_placeholders = ",".join(["%s"] * len(dates))
    rows = query_fn(
        "finance_price",
        f"""
        SELECT
            symbol,
            AVG(volume) AS avg_10d_volume,
            COUNT(volume) AS baseline_days
        FROM nyse_price_history FORCE INDEX (uk_symbol_timeframe_date)
        WHERE symbol IN ({symbol_placeholders})
          AND timeframe = %s
          AND `date` IN ({date_placeholders})
          AND volume IS NOT NULL
        GROUP BY symbol
        """,
        list(symbols) + ["1d"] + list(dates),
    )
    baselines: dict[str, dict[str, Any]] = {}
    for row in rows:
        symbol = str(row.get("symbol") or "").strip().upper()
        avg_volume = _safe_float(row.get("avg_10d_volume"))
        if not symbol or avg_volume is None or avg_volume <= 0:
            continue
        baselines[symbol] = {
            "avg_10d_volume": avg_volume,
            "baseline_days": int(row.get("baseline_days") or 0),
        }
    return baselines

def _current_volume_for_relative(
    row: dict[str, Any],
    *,
    period: str,
    volume_stats: dict[str, dict[str, Any]],
) -> tuple[float | None, str]:
    normalized_period = str(period or "daily").strip().lower()
    if normalized_period == "daily":
        return _safe_float(row.get("volume")), "Daily share volume"
    symbol = str(row.get("symbol") or "").strip().upper()
    stats = volume_stats.get(symbol) or {}
    avg_daily_volume = _safe_float(stats.get("avg_daily_volume"))
    if avg_daily_volume is not None:
        return avg_daily_volume, "Avg daily share volume"
    return _safe_float(row.get("volume")), "End-date share volume"

def _unusual_volume_frame(
    return_rows: list[dict[str, Any]],
    *,
    top_n: int,
    period: str,
    volume_stats: dict[str, dict[str, Any]] | None = None,
    relative_volume_baselines: dict[str, dict[str, Any]] | None = None,
) -> pd.DataFrame:
    volume_stats = volume_stats or {}
    relative_volume_baselines = relative_volume_baselines or {}
    ranked_rows: list[dict[str, Any]] = []
    for row in return_rows:
        symbol = str(row.get("symbol") or "").strip().upper()
        if not symbol:
            continue
        current_volume, volume_basis = _current_volume_for_relative(
            row,
            period=period,
            volume_stats=volume_stats,
        )
        baseline = relative_volume_baselines.get(symbol) or {}
        avg_10d_volume = _safe_float(baseline.get("avg_10d_volume"))
        if current_volume is None or avg_10d_volume is None or avg_10d_volume <= 0:
            continue
        ranked_rows.append(
            {
                "symbol": symbol,
                "name": row.get("name") or "-",
                "relative_volume": float(current_volume) / float(avg_10d_volume),
                "current_volume": current_volume,
                "avg_10d_volume": avg_10d_volume,
                "baseline_days": int(baseline.get("baseline_days") or 0),
                "volume_basis": volume_basis,
                "return_pct": row.get("return_pct"),
                "sector": row.get("sector") or "Unknown",
                "industry": row.get("industry") or "Unknown",
                "market_cap": row.get("market_cap"),
                "start_date": row.get("start_date"),
                "end_date": row.get("end_date"),
                "price_source": row.get("price_source") or "EOD DB",
            }
        )

    ranked = sorted(
        ranked_rows,
        key=lambda item: (-float(item["relative_volume"]), item["symbol"]),
    )[:top_n]
    out = [
        {
            "Rank": index,
            "Symbol": row["symbol"],
            "Name": row["name"] or "-",
            "Relative Volume": round(float(row["relative_volume"]), 2),
            "Current Volume": int(round(float(row["current_volume"]))),
            "Avg 10D Volume": int(round(float(row["avg_10d_volume"]))),
            "Baseline Days": int(row["baseline_days"]),
            "Volume Basis": row["volume_basis"],
            "Return %": round(float(row["return_pct"]), 2) if row.get("return_pct") is not None else None,
            "Sector": row["sector"],
            "Industry": row["industry"],
            "Market Cap": int(row["market_cap"]) if row.get("market_cap") else None,
            "Start Date": row["start_date"],
            "End Date": row["end_date"],
            "Price Source": row["price_source"],
        }
        for index, row in enumerate(ranked, start=1)
    ]
    return _rows_frame(out, columns=UNUSUAL_VOLUME_COLUMNS)

def _view_status(rows: pd.DataFrame) -> str:
    return "OK" if isinstance(rows, pd.DataFrame) and not rows.empty else "INSUFFICIENT_DATA"

def _mode_model(
    *,
    label: str,
    rows: pd.DataFrame,
    sort_basis: str,
    kind: str,
    empty_reason: str,
) -> dict[str, Any]:
    return {
        "label": label,
        "kind": kind,
        "status": _view_status(rows),
        "sort_basis": sort_basis,
        "empty_reason": "" if _view_status(rows) == "OK" else empty_reason,
        "rows": rows,
        "boundary_note": MOVER_VIEW_BOUNDARY_NOTE,
    }

def _build_market_mover_views(
    return_rows: list[dict[str, Any]],
    *,
    top_n: int,
    period: str,
    volume_stats: dict[str, dict[str, Any]] | None = None,
    relative_volume_baselines: dict[str, dict[str, Any]] | None = None,
) -> dict[str, dict[str, Any]]:
    volume_stats = volume_stats or {}
    top_gainers = _ranked_movers_frame(return_rows, top_n=top_n)
    top_losers = _ranked_losers_frame(return_rows, top_n=top_n)
    volume_leaders = _ranked_volume_frame(
        return_rows,
        top_n=top_n,
        period=period,
        volume_stats=volume_stats,
    )
    unusual_volume = _unusual_volume_frame(
        return_rows,
        top_n=top_n,
        period=period,
        volume_stats=volume_stats,
        relative_volume_baselines=relative_volume_baselines,
    )
    sector_rows = _group_rows_frame(
        _rank_group_rows(
            _group_leadership_rows(
                return_rows=return_rows,
                group_by="sector",
                min_group_size=1,
                start_date=str(return_rows[0].get("start_date") or "-") if return_rows else "-",
                end_date=str(return_rows[0].get("end_date") or "-") if return_rows else "-",
            ),
            top_n=top_n,
        )
    )
    return {
        "top_gainers": _mode_model(
            label=MOVER_VIEW_LABELS["top_gainers"],
            rows=top_gainers,
            sort_basis="Return % descending",
            kind="symbol",
            empty_reason="No returnable rows are available for gainers.",
        ),
        "top_losers": _mode_model(
            label=MOVER_VIEW_LABELS["top_losers"],
            rows=top_losers,
            sort_basis="Negative Return % ascending",
            kind="symbol",
            empty_reason="No negative return rows are available for the selected coverage and period.",
        ),
        "volume_leaders": _mode_model(
            label=MOVER_VIEW_LABELS["volume_leaders"],
            rows=volume_leaders,
            sort_basis="Share / dollar volume descending from stored DB rows",
            kind="symbol",
            empty_reason="No usable volume rows are available for the selected coverage and period.",
        ),
        "unusual_volume": _mode_model(
            label=MOVER_VIEW_LABELS["unusual_volume"],
            rows=unusual_volume,
            sort_basis="Current volume divided by prior 10-day average volume",
            kind="symbol",
            empty_reason="10-day volume baseline is unavailable from stored EOD history for this selection.",
        ),
        "sector_leaders": _mode_model(
            label=MOVER_VIEW_LABELS["sector_leaders"],
            rows=sector_rows,
            sort_basis="Sector market-cap weighted return descending",
            kind="sector",
            empty_reason="No sector rows are available for the selected coverage and period.",
        ),
    }

def _latest_intraday_snapshot_time(
    *,
    universe_code: str,
    interval: str,
    query_fn: QueryFn,
) -> str | None:
    try:
        rows = query_fn(
            "finance_price",
            """
            SELECT MAX(snapshot_time_utc) AS snapshot_time_utc
            FROM market_intraday_snapshot
            WHERE universe_code = %s
              AND interval_code = %s
            """,
            [universe_code, interval],
        )
    except Exception:
        return None
    if not rows:
        return None
    return _display_datetime(rows[0].get("snapshot_time_utc"))

def _load_intraday_snapshot_rows(
    *,
    universe_code: str,
    interval: str,
    snapshot_time: str,
    query_fn: QueryFn,
) -> list[dict[str, Any]]:
    try:
        return query_fn(
            "finance_price",
            """
            SELECT
                s.symbol,
                s.interval_code,
                s.snapshot_time_utc,
                s.quote_time_utc,
                s.previous_close,
                s.latest_price,
                s.return_pct,
                s.volume,
                s.provider_status,
                s.error_msg,
                s.source,
                s.source_ref
            FROM market_intraday_snapshot s
            WHERE s.universe_code = %s
              AND s.interval_code = %s
              AND s.snapshot_time_utc = %s
            """,
            [universe_code, interval, snapshot_time],
        )
    except Exception:
        return []

def _build_intraday_return_payload(
    *,
    universe: list[dict[str, Any]],
    universe_code: str,
    period: str,
    interval: str,
    min_price_rows: int,
    today: date | None,
    query_fn: QueryFn,
) -> dict[str, Any] | None:
    snapshot_time = _latest_intraday_snapshot_time(universe_code=universe_code, interval=interval, query_fn=query_fn)
    if not snapshot_time:
        return None
    rows = _load_intraday_snapshot_rows(
        universe_code=universe_code,
        interval=interval,
        snapshot_time=snapshot_time,
        query_fn=query_fn,
    )
    if not rows:
        return None

    row_map = {str(row.get("symbol") or "").strip().upper(): row for row in rows}
    symbols = [str(item.get("symbol") or "").strip().upper() for item in universe if item.get("symbol")]
    effective_min_rows = min(int(min_price_rows), max(50, int(len(universe) * 0.75)))
    previous_date_window = resolve_effective_market_dates(
        period="daily",
        min_price_rows=effective_min_rows,
        today=today,
        query_fn=query_fn,
    )
    previous_context = (
        _previous_return_context(
            symbols=symbols,
            date_window=previous_date_window,
            period="daily",
            query_fn=query_fn,
        )
        if previous_date_window.get("status") == "OK"
        else {}
    )
    return_rows: list[dict[str, Any]] = []
    missing_rows: list[dict[str, Any]] = []
    for item in universe:
        symbol = str(item.get("symbol") or "").strip().upper()
        row = row_map.get(symbol)
        if not row:
            missing_rows.append(
                _missing_row(
                    item=item,
                    reason="missing intraday snapshot row",
                    start_date="Previous Close",
                    end_date=snapshot_time,
                    start_price=None,
                    end_price=None,
                    latest_price_date=None,
                )
            )
            continue
        previous_close = _safe_float(row.get("previous_close"))
        latest_price = _safe_float(row.get("latest_price"))
        return_pct = _safe_float(row.get("return_pct"))
        volume = _safe_float(row.get("volume"))
        quote_time = _display_datetime(row.get("quote_time_utc")) or snapshot_time
        if row.get("provider_status") != "ok" or previous_close is None or latest_price is None or return_pct is None:
            missing_rows.append(
                _missing_row(
                    item=item,
                    reason=row.get("error_msg") or "missing intraday return",
                    start_date="Previous Close",
                    end_date=quote_time,
                    start_price=previous_close,
                    end_price=latest_price,
                    latest_price_date=_iso_date(row.get("quote_time_utc")),
                )
            )
            continue
        previous = previous_context.get(symbol) or {}
        previous_return = _safe_float(previous.get("previous_return_pct"))
        return_rows.append(
            {
                "symbol": symbol,
                "name": item.get("long_name") or "",
                "sector": item.get("sector") or "Unknown",
                "industry": item.get("industry") or "Unknown",
                "market_cap": _safe_float(item.get("market_cap")) or 0.0,
                "start_price": previous_close,
                "end_price": latest_price,
                "return_pct": return_pct,
                "previous_return_pct": previous_return,
                "momentum_delta_pp": (return_pct - previous_return) if previous_return is not None else None,
                "volume": int(volume) if volume is not None else None,
                "dollar_volume": (float(latest_price) * float(volume)) if volume is not None else None,
                "start_date": "Previous Close",
                "end_date": quote_time,
                "previous_start_date": previous.get("previous_start_date"),
                "previous_end_date": previous.get("previous_end_date"),
                "price_source": "Yahoo Quote" if row.get("source") == "yahoo_quote" else f"Intraday {interval}",
            }
        )

    date_window = {
        "status": "OK",
        "period": period,
        "period_label": PERIOD_LABELS[period],
        "start_date": "Previous Close",
        "end_date": snapshot_time,
        "latest_raw_date": None,
        "effective_end_date": snapshot_time,
        "stale_days": None,
        "message": "",
    }
    coverage = _coverage(
        universe_count=len(universe),
        returnable_count=len(return_rows),
        date_window=date_window,
        price_mode="Intraday Snapshot",
        extra={
            **_universe_metadata(universe, universe_code=universe_code),
            "snapshot_time_utc": snapshot_time,
            "snapshot_stale_minutes": _stale_minutes(snapshot_time),
            "intraday_interval": interval,
        },
    )
    coverage["refresh_state"] = _intraday_refresh_state(
        snapshot_status="OK",
        period=period,
        coverage=coverage,
    )
    missing_rows = _enrich_missing_rows(
        missing_rows,
        universe_code=universe_code,
        query_fn=query_fn,
    )
    relative_volume_dates = (
        _relative_volume_baseline_dates(
            previous_date_window,
            period="daily",
            skip_current_period=False,
        )
        if previous_date_window.get("status") == "OK"
        else []
    )
    relative_volume_baselines = _load_relative_volume_baselines(
        symbols=[str(row.get("symbol") or "").strip().upper() for row in return_rows],
        dates=relative_volume_dates,
        query_fn=query_fn,
    )
    return {
        "snapshot_time": snapshot_time,
        "return_rows": return_rows,
        "missing_rows": missing_rows,
        "relative_volume_baselines": relative_volume_baselines,
        "date_window": date_window,
        "coverage": coverage,
    }

def _build_intraday_movers_snapshot(
    *,
    universe: list[dict[str, Any]],
    universe_code: str,
    universe_limit: int,
    period: str,
    top_n: int,
    sector: str | None,
    min_price_rows: int,
    today: date | None,
    interval: str,
    query_fn: QueryFn,
) -> dict[str, Any] | None:
    payload = _build_intraday_return_payload(
        universe=universe,
        universe_code=universe_code,
        period=period,
        interval=interval,
        min_price_rows=min_price_rows,
        today=today,
        query_fn=query_fn,
    )
    if payload is None:
        return None
    return_rows = list(payload["return_rows"])
    missing_rows = list(payload["missing_rows"])
    mover_views = _build_market_mover_views(
        return_rows,
        top_n=top_n,
        period=period,
        relative_volume_baselines=dict(payload.get("relative_volume_baselines") or {}),
    )
    date_window = dict(payload["date_window"])
    coverage = dict(payload["coverage"])
    sector_breadth = _build_market_movers_sector_breadth_model(
        return_rows,
        coverage=coverage,
        date_window=date_window,
    )
    return {
        "status": "OK",
        "period": period,
        "period_label": PERIOD_LABELS[period],
        "universe_code": universe_code,
        "universe_label": UNIVERSE_LABELS.get(universe_code, universe_code),
        "universe_limit": universe_limit,
        "sector": sector or "All",
        "top_n": top_n,
        "rows": mover_views["top_gainers"]["rows"],
        "volume_rows": mover_views["volume_leaders"]["rows"],
        "mover_views": mover_views,
        "sector_breadth": sector_breadth,
        "missing_rows": _rows_frame(missing_rows, columns=MISSING_COLUMNS),
        "date_window": date_window,
        "coverage": coverage,
        "warnings": _coverage_warnings(coverage, date_window=date_window),
    }

def build_market_movers_snapshot(
    *,
    universe_limit: int = 1000,
    universe_code: str | None = None,
    period: str = "daily",
    top_n: int = 20,
    sector: str | None = None,
    min_price_rows: int = 1000,
    as_of_date: str | date | None = None,
    today: date | None = None,
    prefer_intraday: bool = True,
    intraday_interval: str = "5m",
    query_fn: QueryFn | None = None,
) -> dict[str, Any]:
    normalized_period = str(period or "daily").strip().lower()
    normalized_top_n = _normalize_limit(top_n, default=20, min_value=5, max_value=100)
    normalized_universe = _normalize_universe_code(universe_code, universe_limit)
    normalized_limit = _universe_limit_from_code(
        normalized_universe,
        _normalize_limit(universe_limit, default=1000, min_value=100, max_value=3000),
    )
    requested_as_of = _iso_date(as_of_date)
    query = query_fn or _default_query

    if normalized_period not in VALID_PERIODS:
        raise ValueError(f"Unsupported period: {period!r}")

    try:
        universe = _load_universe(
            universe_code=normalized_universe,
            universe_limit=normalized_limit,
            sector=sector,
            query_fn=query,
        )
        if not universe:
            empty_message = (
                "Nasdaq Symbol Directory refresh is required before Nasdaq-listed current snapshot coverage can render."
                if normalized_universe == "NASDAQ"
                else "Selected universe has no symbols. For S&P 500, run the universe refresh first."
            )
            return _empty_movers_snapshot(
                status="NO_UNIVERSE",
                period=normalized_period,
                universe_code=normalized_universe,
                universe_limit=normalized_limit,
                top_n=normalized_top_n,
                sector=sector,
                message=empty_message,
            )

        if normalized_period == "daily" and prefer_intraday and not requested_as_of:
            intraday_snapshot = _build_intraday_movers_snapshot(
                universe=universe,
                universe_code=normalized_universe,
                universe_limit=normalized_limit,
                period=normalized_period,
                top_n=normalized_top_n,
                sector=sector,
                min_price_rows=min_price_rows,
                today=today,
                interval=intraday_interval,
                query_fn=query,
            )
            if intraday_snapshot is not None:
                return intraday_snapshot

        effective_min_rows = min(int(min_price_rows), max(50, int(len(universe) * 0.75)))
        date_window = resolve_effective_market_dates(
            period=normalized_period,
            min_price_rows=effective_min_rows,
            as_of_date=requested_as_of,
            today=today,
            query_fn=query,
        )
        if date_window.get("status") != "OK":
            snapshot = _empty_movers_snapshot(
                status="INSUFFICIENT_DATA",
                period=normalized_period,
                universe_code=normalized_universe,
                universe_limit=normalized_limit,
                top_n=normalized_top_n,
                sector=sector,
                message=str(date_window.get("message") or ""),
            )
            snapshot["date_window"] = date_window
            snapshot["coverage"].update(
                {
                    "universe_count": len(universe),
                    "latest_raw_date": date_window.get("latest_raw_date"),
                    "effective_end_date": date_window.get("effective_end_date"),
                    "stale_days": date_window.get("stale_days"),
                    **_universe_metadata(universe, universe_code=normalized_universe),
                }
            )
            return snapshot

        previous_context = _previous_return_context(
            symbols=[str(row.get("symbol") or "").strip().upper() for row in universe if row.get("symbol")],
            date_window=date_window,
            period=normalized_period,
            query_fn=query,
        )
        return_rows, missing_rows = _build_return_rows(
            universe=universe,
            universe_code=normalized_universe,
            start_date=str(date_window["start_date"]),
            end_date=str(date_window["end_date"]),
            query_fn=query,
            previous_context=previous_context,
        )
        volume_stats: dict[str, dict[str, Any]] = {}
        if normalized_period != "daily":
            volume_dates = _current_period_volume_dates(date_window, period=normalized_period)
            volume_stats = _load_period_volume_stats(
                symbols=[str(row.get("symbol") or "").strip().upper() for row in return_rows],
                dates=volume_dates,
                query_fn=query,
            )
        relative_volume_dates = _relative_volume_baseline_dates(date_window, period=normalized_period)
        relative_volume_baselines = _load_relative_volume_baselines(
            symbols=[str(row.get("symbol") or "").strip().upper() for row in return_rows],
            dates=relative_volume_dates,
            query_fn=query,
        )
        mover_views = _build_market_mover_views(
            return_rows,
            top_n=normalized_top_n,
            period=normalized_period,
            volume_stats=volume_stats,
            relative_volume_baselines=relative_volume_baselines,
        )
        coverage = _coverage(
            universe_count=len(universe),
            returnable_count=len(return_rows),
            date_window=date_window,
            price_mode="EOD DB",
            extra=_universe_metadata(universe, universe_code=normalized_universe),
        )
        sector_breadth = _build_market_movers_sector_breadth_model(
            return_rows,
            coverage=coverage,
            date_window=date_window,
        )
        if normalized_period == "daily" and prefer_intraday and not requested_as_of:
            coverage["refresh_state"] = _intraday_refresh_state(
                snapshot_status="OK",
                period=normalized_period,
                coverage=coverage,
            )
        warnings = _coverage_warnings(coverage, date_window=date_window)
        if normalized_period == "daily" and prefer_intraday and not requested_as_of:
            warnings.insert(0, "No intraday snapshot found for the selected universe; using daily DB close data.")
        return {
            "status": "OK",
            "period": normalized_period,
            "period_label": PERIOD_LABELS[normalized_period],
            "universe_code": normalized_universe,
            "universe_label": UNIVERSE_LABELS.get(normalized_universe, normalized_universe),
            "universe_limit": normalized_limit,
            "sector": sector or "All",
            "top_n": normalized_top_n,
            "rows": mover_views["top_gainers"]["rows"],
            "volume_rows": mover_views["volume_leaders"]["rows"],
            "mover_views": mover_views,
            "sector_breadth": sector_breadth,
            "missing_rows": _rows_frame(missing_rows, columns=MISSING_COLUMNS),
            "date_window": date_window,
            "coverage": coverage,
            "warnings": warnings,
        }
    except Exception as exc:
        return _empty_movers_snapshot(
            status="ERROR",
            period=normalized_period,
            universe_code=normalized_universe,
            universe_limit=normalized_limit,
            top_n=normalized_top_n,
            sector=sector,
            message=f"Market movers snapshot failed: {exc}",
        )

def _build_intraday_group_leadership_snapshot(
    *,
    universe: list[dict[str, Any]],
    universe_code: str,
    universe_limit: int,
    group_by: str,
    period: str,
    top_n: int,
    min_group_size: int,
    min_price_rows: int,
    today: date | None,
    interval: str,
    trend_groups: Sequence[str] | None,
    query_fn: QueryFn,
) -> dict[str, Any] | None:
    payload = _build_intraday_return_payload(
        universe=universe,
        universe_code=universe_code,
        period=period,
        interval=interval,
        min_price_rows=min_price_rows,
        today=today,
        query_fn=query_fn,
    )
    if payload is None:
        return None

    date_window = dict(payload["date_window"])
    return_rows = list(payload["return_rows"])
    missing_rows = list(payload["missing_rows"])
    group_rows = _group_leadership_rows(
        return_rows=return_rows,
        group_by=group_by,
        min_group_size=min_group_size,
        start_date=str(date_window["start_date"]),
        end_date=str(date_window["end_date"]),
    )
    ranked = _rank_group_rows(group_rows, top_n=top_n)
    top_groups = {str(row["group"]) for row in ranked}
    requested_trend_groups = {str(group).strip() for group in (trend_groups or []) if str(group).strip()}
    trend_group_set = top_groups | requested_trend_groups
    positive_groups = {
        str(row["group"])
        for row in ranked
        if float(row.get("market_cap_weighted_return") or 0.0) > 0
    }

    trend_rows = pd.DataFrame(columns=GROUP_TREND_COLUMNS)
    trend_warnings: list[str] = []
    effective_min_rows = min(int(min_price_rows), max(50, int(len(universe) * 0.75)))
    trend_date_window = resolve_group_trend_market_dates(
        period=period,
        min_price_rows=effective_min_rows,
        today=today,
        query_fn=query_fn,
    )
    if trend_date_window.get("status") == "OK":
        trend_rows = _group_trend_rows_frame(
            windows=list(trend_date_window.get("windows") or []),
            universe=universe,
            groups=trend_group_set,
            group_by=group_by,
            min_group_size=min_group_size,
            query_fn=query_fn,
        )
    else:
        trend_warnings.append(
            str(trend_date_window.get("message") or "Historical daily trend windows are unavailable.")
        )

    current_trend_rows = _group_trend_rows_from_group_rows(
        group_rows=group_rows,
        groups=trend_group_set,
        date_value=str(date_window["end_date"]),
    )
    if not current_trend_rows.empty:
        trend_rows = pd.concat([trend_rows, current_trend_rows], ignore_index=True)

    ticker_leader_rows = _group_ticker_leader_rows_frame(
        return_rows=return_rows,
        positive_groups=positive_groups,
        group_by=group_by,
    )
    coverage = dict(payload["coverage"])
    warnings = _coverage_warnings(coverage, date_window=date_window)
    warnings.extend(trend_warnings)
    return {
        "status": "OK",
        "group_by": group_by,
        "universe_code": universe_code,
        "universe_label": UNIVERSE_LABELS.get(universe_code, universe_code),
        "universe_limit": universe_limit,
        "period": period,
        "period_label": PERIOD_LABELS[period],
        "trend_window_label": GROUP_TREND_PERIODS[period]["window_label"],
        "top_n": top_n,
        "rows": _group_rows_frame(ranked),
        "trend_rows": trend_rows,
        "ticker_leader_rows": ticker_leader_rows,
        "missing_rows": pd.DataFrame(missing_rows, columns=MISSING_COLUMNS),
        "date_window": date_window,
        "coverage": coverage,
        "warnings": warnings,
    }

def build_group_leadership_snapshot(
    *,
    universe_limit: int = 2000,
    universe_code: str | None = None,
    group_by: str = "sector",
    period: str = "monthly",
    top_n: int = 10,
    min_group_size: int = 5,
    min_price_rows: int = 1000,
    as_of_date: str | date | None = None,
    today: date | None = None,
    prefer_intraday: bool = True,
    intraday_interval: str = "5m",
    trend_groups: Sequence[str] | None = None,
    query_fn: QueryFn | None = None,
) -> dict[str, Any]:
    normalized_group = str(group_by or "sector").strip().lower()
    if normalized_group not in VALID_GROUPS:
        raise ValueError(f"Unsupported group_by: {group_by!r}")
    normalized_period = str(period or "monthly").strip().lower()
    if normalized_period not in GROUP_TREND_PERIODS:
        raise ValueError(f"Unsupported group leadership period: {period!r}")

    normalized_universe = _normalize_universe_code(universe_code, universe_limit)
    normalized_limit = _universe_limit_from_code(
        normalized_universe,
        _normalize_limit(universe_limit, default=2000, min_value=100, max_value=3000),
    )
    normalized_top_n = _normalize_limit(top_n, default=10, min_value=5, max_value=100)
    requested_as_of = _iso_date(as_of_date)
    query = query_fn or _default_query

    try:
        universe = _load_universe(
            universe_code=normalized_universe,
            universe_limit=normalized_limit,
            query_fn=query,
        )
        if normalized_period == "daily" and prefer_intraday and not requested_as_of:
            intraday_snapshot = _build_intraday_group_leadership_snapshot(
                universe=universe,
                universe_code=normalized_universe,
                universe_limit=normalized_limit,
                group_by=normalized_group,
                period=normalized_period,
                top_n=normalized_top_n,
                min_group_size=min_group_size,
                min_price_rows=min_price_rows,
                today=today,
                interval=intraday_interval,
                trend_groups=trend_groups,
                query_fn=query,
            )
            if intraday_snapshot is not None:
                return intraday_snapshot

        effective_min_rows = min(int(min_price_rows), max(50, int(len(universe) * 0.75)))
        date_window = resolve_group_trend_market_dates(
            period=normalized_period,
            min_price_rows=effective_min_rows,
            as_of_date=requested_as_of,
            today=today,
            query_fn=query,
        )
        if date_window.get("status") != "OK":
            snapshot = _empty_group_snapshot(
                status="INSUFFICIENT_DATA",
                group_by=normalized_group,
                universe_code=normalized_universe,
                universe_limit=normalized_limit,
                period=normalized_period,
                top_n=normalized_top_n,
                message=str(date_window.get("message") or ""),
            )
            snapshot["date_window"] = date_window
            snapshot["coverage"].update(
                {
                    "universe_count": len(universe),
                    "latest_raw_date": date_window.get("latest_raw_date"),
                    "effective_end_date": date_window.get("effective_end_date"),
                    "stale_days": date_window.get("stale_days"),
                    **_universe_metadata(universe, universe_code=normalized_universe),
                }
            )
            return snapshot

        previous_context = _previous_return_context(
            symbols=[str(row.get("symbol") or "").strip().upper() for row in universe if row.get("symbol")],
            date_window=date_window,
            period=normalized_period,
            query_fn=query,
        )
        return_rows, missing_rows = _build_return_rows(
            universe=universe,
            universe_code=normalized_universe,
            start_date=str(date_window["start_date"]),
            end_date=str(date_window["end_date"]),
            query_fn=query,
            previous_context=previous_context,
        )

        group_rows = _group_leadership_rows(
            return_rows=return_rows,
            group_by=normalized_group,
            min_group_size=min_group_size,
            start_date=str(date_window["start_date"]),
            end_date=str(date_window["end_date"]),
        )
        ranked = _rank_group_rows(group_rows, top_n=normalized_top_n)
        top_groups = {str(row["group"]) for row in ranked}
        requested_trend_groups = {str(group).strip() for group in (trend_groups or []) if str(group).strip()}
        trend_group_set = top_groups | requested_trend_groups
        positive_groups = {
            str(row["group"])
            for row in ranked
            if float(row.get("market_cap_weighted_return") or 0.0) > 0
        }
        trend_rows = _group_trend_rows_frame(
            windows=list(date_window.get("windows") or []),
            universe=universe,
            groups=trend_group_set,
            group_by=normalized_group,
            min_group_size=min_group_size,
            query_fn=query,
        )
        ticker_leader_rows = _group_ticker_leader_rows_frame(
            return_rows=return_rows,
            positive_groups=positive_groups,
            group_by=normalized_group,
        )
        coverage = _coverage(
            universe_count=len(universe),
            returnable_count=len(return_rows),
            date_window=date_window,
            extra=_universe_metadata(universe, universe_code=normalized_universe),
        )
        if normalized_period == "daily" and prefer_intraday and not requested_as_of:
            coverage["refresh_state"] = _intraday_refresh_state(
                snapshot_status="OK",
                period=normalized_period,
                coverage=coverage,
            )
        warnings = _coverage_warnings(coverage, date_window=date_window)
        if normalized_period == "daily" and prefer_intraday and not requested_as_of:
            warnings.insert(0, "No intraday snapshot found for the selected universe; using daily DB close data.")
        return {
            "status": "OK",
            "group_by": normalized_group,
            "universe_code": normalized_universe,
            "universe_label": UNIVERSE_LABELS.get(normalized_universe, normalized_universe),
            "universe_limit": normalized_limit,
            "period": normalized_period,
            "period_label": PERIOD_LABELS[normalized_period],
            "trend_window_label": GROUP_TREND_PERIODS[normalized_period]["window_label"],
            "top_n": normalized_top_n,
            "rows": _group_rows_frame(ranked),
            "trend_rows": trend_rows,
            "ticker_leader_rows": ticker_leader_rows,
            "missing_rows": pd.DataFrame(missing_rows, columns=MISSING_COLUMNS),
            "date_window": date_window,
            "coverage": coverage,
            "warnings": warnings,
        }
    except Exception as exc:
        return _empty_group_snapshot(
            status="ERROR",
            group_by=normalized_group,
            universe_code=normalized_universe,
            universe_limit=normalized_limit,
            period=normalized_period,
            top_n=normalized_top_n,
            message=f"Group leadership snapshot failed: {exc}",
        )

__all__ = [
    "resolve_effective_market_dates",
    "resolve_group_trend_market_dates",
    "load_market_mover_sector_options",
    "build_market_movers_coverage_trust_model",
    "build_market_movers_snapshot",
    "build_group_leadership_snapshot",
    "build_overview_breadth_heatmap_summary",
    "MOVER_VIEW_MODE_ORDER",
    "MOVER_VIEW_LABELS",
]
