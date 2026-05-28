from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import date, timedelta
from typing import Any

import pandas as pd


QueryFn = Callable[[str, str, Sequence[Any] | None], list[dict[str, Any]]]

VALID_PERIODS = {"daily": 1, "weekly": 5, "monthly": 21, "yearly": 252}
PERIOD_LABELS = {"daily": "Daily", "weekly": "Weekly", "monthly": "Monthly", "yearly": "Yearly"}
VALID_GROUPS = {"sector", "industry"}
MARKET_INTRADAY_REFRESH_MINUTES = 5
MARKET_INTRADAY_STALE_MINUTES = 15
EVENT_ESTIMATE_STALE_DAYS = 14
UNIVERSE_LABELS = {
    "SP500": "S&P 500",
    "TOP1000": "Top 1000 by market cap",
    "TOP2000": "Top 2000 by market cap",
}
MOVERS_COLUMNS = [
    "Rank",
    "Symbol",
    "Name",
    "Return %",
    "Start Price",
    "End Price",
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
    "Equal Weight Return %",
    "Market Cap Weighted Return %",
    "Top Symbol",
    "Top Symbol Return %",
    "Start Date",
    "End Date",
]
EVENT_COLUMNS = [
    "Date",
    "Type",
    "Symbol",
    "Title",
    "Source Type",
    "Validation",
    "Freshness",
    "Quality Action",
    "Event Status",
    "Age Days",
    "Source",
    "Confidence",
    "Collected At",
    "Source URL",
]
OPS_COLUMNS = [
    "Area",
    "Status",
    "Data Freshness",
    "Last Success",
    "Last Issue",
    "Rows",
    "Processed",
    "Failed",
    "Duration Sec",
    "Next Action",
    "Message",
]
OPS_INTRADAY_TARGETS = [
    {
        "area": "S&P 500 Daily Snapshot",
        "universe_code": "SP500",
        "job_names": ["collect_sp500_intraday_snapshot"],
        "missing_action": "Run Update Daily Snapshot for S&P 500.",
        "due_action": "Refresh S&P 500 daily snapshot before using daily movers.",
    },
    {
        "area": "Top1000 Daily Snapshot",
        "universe_code": "TOP1000",
        "job_names": ["collect_top1000_intraday_snapshot"],
        "missing_action": "Run Update Daily Snapshot for Top1000.",
        "due_action": "Refresh Top1000 daily snapshot before using daily movers.",
    },
    {
        "area": "Top2000 Daily Snapshot",
        "universe_code": "TOP2000",
        "job_names": ["collect_top2000_intraday_snapshot"],
        "missing_action": "Run Update Daily Snapshot for Top2000.",
        "due_action": "Refresh Top2000 daily snapshot before using daily movers.",
    },
]
OPS_EVENT_TARGETS = [
    {
        "area": "FOMC Calendar",
        "event_type": "FOMC_MEETING",
        "job_names": ["collect_fomc_calendar"],
        "fresh_days": 30,
        "stale_days": 90,
        "missing_action": "Run Refresh FOMC Calendar.",
        "due_action": "Refresh FOMC Calendar from the official Fed page.",
    },
    {
        "area": "Earnings Calendar",
        "event_type": "EARNINGS",
        "job_names": ["collect_earnings_calendar"],
        "fresh_days": 1,
        "stale_days": EVENT_ESTIMATE_STALE_DAYS,
        "missing_action": "Run Refresh Earnings Calendar for latest movers or a bounded batch.",
        "due_action": "Refresh Earnings Calendar before relying on upcoming dates.",
    },
    {
        "area": "Macro Calendar",
        "event_type": "MACRO",
        "event_types": ["MACRO_CPI", "MACRO_PPI", "MACRO_EMPLOYMENT", "MACRO_GDP"],
        "job_names": ["collect_macro_calendar", "import_bls_macro_calendar_ics"],
        "fresh_days": 7,
        "stale_days": 30,
        "missing_action": "Run Refresh Macro Calendar or import the BLS .ics file.",
        "due_action": "Refresh Macro Calendar from official schedules or import the BLS .ics file.",
    },
]


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
        "missing_rows": pd.DataFrame(columns=MISSING_COLUMNS),
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
    }


def _empty_group_snapshot(
    *,
    status: str,
    group_by: str,
    universe_limit: int,
    top_n: int,
    message: str,
) -> dict[str, Any]:
    return {
        "status": status,
        "group_by": group_by,
        "universe_limit": universe_limit,
        "top_n": top_n,
        "rows": pd.DataFrame(columns=GROUP_COLUMNS),
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


def _empty_events_snapshot(
    *,
    status: str,
    start_date: str,
    end_date: str,
    event_type: str | None,
    message: str,
) -> dict[str, Any]:
    return {
        "status": status,
        "event_type": event_type or "All",
        "rows": pd.DataFrame(columns=EVENT_COLUMNS),
        "date_window": {"start_date": start_date, "end_date": end_date},
        "coverage": {
            "event_count": 0,
            "next_event_date": None,
            "latest_collected_at": None,
            "source_count": 0,
            "official_count": 0,
            "estimate_count": 0,
            "cross_checked_count": 0,
            "not_confirmed_count": 0,
            "stale_estimate_count": 0,
            "superseded_count": 0,
        },
        "warnings": [message] if message else [],
    }


def _empty_ops_snapshot(*, message: str) -> dict[str, Any]:
    return {
        "status": "NO_STATUS",
        "rows": pd.DataFrame(columns=OPS_COLUMNS),
        "coverage": {
            "job_count": 0,
            "ok_count": 0,
            "due_count": 0,
            "stale_count": 0,
            "missing_count": 0,
            "failed_count": 0,
            "partial_count": 0,
            "latest_success_at": None,
            "latest_issue_at": None,
        },
        "warnings": [message] if message else [],
    }


def _query_latest_raw_date(query_fn: QueryFn) -> str | None:
    rows = query_fn(
        "finance_price",
        """
        SELECT MAX(`date`) AS latest_raw_date
        FROM nyse_price_history
        WHERE timeframe = %s
        """,
        ["1d"],
    )
    if not rows:
        return None
    return _iso_date(rows[0].get("latest_raw_date"))


def resolve_effective_market_dates(
    *,
    period: str = "daily",
    min_price_rows: int = 1000,
    today: date | None = None,
    query_fn: QueryFn | None = None,
) -> dict[str, Any]:
    """Resolve the latest usable daily price window for overview market scans."""
    normalized_period = str(period or "daily").strip().lower()
    if normalized_period not in VALID_PERIODS:
        raise ValueError(f"Unsupported period: {period!r}")

    query = query_fn or _default_query
    offset = VALID_PERIODS[normalized_period]
    latest_raw_date = _query_latest_raw_date(query)
    rows = query(
        "finance_price",
        """
        SELECT
            `date`,
            SUM(CASE WHEN COALESCE(adj_close, close) IS NOT NULL THEN 1 ELSE 0 END) AS usable_rows
        FROM nyse_price_history
        WHERE timeframe = %s
        GROUP BY `date`
        HAVING usable_rows >= %s
        ORDER BY `date` DESC
        LIMIT %s
        """,
        ["1d", int(min_price_rows), offset + 1],
    )

    eligible = [
        {
            "date": _iso_date(row.get("date")),
            "usable_rows": int(row.get("usable_rows") or 0),
        }
        for row in rows
        if _iso_date(row.get("date"))
    ]
    if len(eligible) <= offset:
        return {
            "status": "INSUFFICIENT_DATA",
            "period": normalized_period,
            "period_label": PERIOD_LABELS[normalized_period],
            "start_date": None,
            "end_date": eligible[0]["date"] if eligible else None,
            "latest_raw_date": latest_raw_date,
            "effective_end_date": eligible[0]["date"] if eligible else None,
            "eligible_dates": eligible,
            "stale_days": _stale_days(eligible[0]["date"] if eligible else None, today=today),
            "message": "Not enough eligible daily price rows to resolve the requested period.",
        }

    end_row = eligible[0]
    start_row = eligible[offset]
    return {
        "status": "OK",
        "period": normalized_period,
        "period_label": PERIOD_LABELS[normalized_period],
        "start_date": start_row["date"],
        "end_date": end_row["date"],
        "latest_raw_date": latest_raw_date,
        "effective_end_date": end_row["date"],
        "eligible_dates": eligible,
        "stale_days": _stale_days(end_row["date"], today=today),
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
                COALESCE(p.long_name, m.name) AS long_name,
                COALESCE(p.sector, m.sector) AS sector,
                COALESCE(p.industry, m.industry) AS industry,
                p.market_cap,
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
            WHERE m.universe_code = %s
              AND m.active = 1
            ORDER BY COALESCE(p.market_cap, 0) DESC, m.symbol ASC
            """,
            ["stock", "SP500"],
        )
        return _filter_sector(rows, sector)

    return _filter_sector(
        query_fn(
            "finance_meta",
            """
            SELECT
                symbol,
                long_name,
                sector,
                industry,
                market_cap,
                status,
                error_msg,
                last_collected_at,
                NULL AS universe_as_of_date,
                NULL AS universe_collected_at,
                'nyse_asset_profile' AS universe_source,
                NULL AS universe_source_url
            FROM nyse_asset_profile
            WHERE kind = %s
              AND country = %s
              AND market_cap IS NOT NULL
              AND market_cap > 0
              AND (is_spac IS NULL OR is_spac <> 1)
              AND (status IS NULL OR LOWER(status) NOT IN ('dilist', 'delist', 'delisted'))
            ORDER BY market_cap DESC, symbol ASC
            LIMIT %s
            """,
            ["stock", "United States", int(universe_limit)],
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
            COALESCE(adj_close, close) AS price
        FROM nyse_price_history
        WHERE symbol IN ({symbol_placeholders})
          AND timeframe = %s
          AND `date` IN ({date_placeholders})
        """,
        list(symbols) + ["1d"] + list(dates),
    )
    prices: dict[tuple[str, str], float] = {}
    for row in rows:
        symbol = str(row.get("symbol") or "").strip().upper()
        row_date = _iso_date(row.get("date"))
        price = _safe_float(row.get("price"))
        if not symbol or not row_date or price is None:
            continue
        prices[(symbol, row_date)] = price
    return prices


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
    return {
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
    }


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
    start_date: str,
    end_date: str,
    query_fn: QueryFn,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    symbols = [str(row.get("symbol") or "").strip().upper() for row in universe if row.get("symbol")]
    price_map = _load_prices_for_dates(symbols=symbols, dates=[start_date, end_date], query_fn=query_fn)
    latest_dates = _load_latest_price_dates(symbols=symbols, query_fn=query_fn)
    return_rows: list[dict[str, Any]] = []
    missing_rows: list[dict[str, Any]] = []

    for item in universe:
        symbol = str(item.get("symbol") or "").strip().upper()
        start_price = price_map.get((symbol, start_date))
        end_price = price_map.get((symbol, end_date))
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
            missing_rows.append(
                _missing_row(
                    item=item,
                    reason=reason,
                    start_date=start_date,
                    end_date=end_date,
                    start_price=start_price,
                    end_price=end_price,
                    latest_price_date=latest_dates.get(symbol),
                )
            )
            continue
        return_pct = (float(end_price) / float(start_price) - 1.0) * 100.0
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
                "start_date": start_date,
                "end_date": end_date,
                "price_source": "EOD DB",
            }
        )
    return return_rows, missing_rows


def _coverage(
    *,
    universe_count: int,
    returnable_count: int,
    date_window: dict[str, Any],
    price_mode: str = "EOD DB",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    coverage = {
        "universe_count": universe_count,
        "returnable_count": returnable_count,
        "missing_count": max(0, universe_count - returnable_count),
        "failed_count": max(0, universe_count - returnable_count),
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
        refresh_due_in = MARKET_INTRADAY_REFRESH_MINUTES - stale_minutes
        status = "fresh"
        label = "Fresh"
        detail = f"{stale_minutes}m old, next check in {refresh_due_in}m"
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


def _normalize_event_type_value(value: str | None) -> str | None:
    normalized = str(value or "").strip().upper().replace(" ", "_")
    return normalized or None


def _load_market_event_rows(
    *,
    start_date: str,
    end_date: str,
    event_type: str | None,
    limit: int,
    query_fn: QueryFn,
) -> list[dict[str, Any]]:
    conditions = ["event_date >= %s", "event_date <= %s"]
    params: list[Any] = [start_date, end_date]
    normalized_type = _normalize_event_type_value(event_type)
    if normalized_type and normalized_type != "ALL":
        if normalized_type == "MACRO":
            conditions.append("event_type LIKE %s")
            params.append("MACRO_%")
        else:
            conditions.append("event_type = %s")
            params.append(normalized_type)
    bounded_limit = _normalize_limit(limit, default=200, min_value=1, max_value=1000)
    active_conditions = conditions + ["COALESCE(event_status, 'active') <> %s"]
    active_params = params + ["superseded", bounded_limit]
    try:
        return query_fn(
            "finance_meta",
            f"""
            SELECT
                event_date,
                event_type,
                symbol,
                title,
                source,
                source_type,
                validation_status,
                event_status,
                superseded_by_event_key,
                superseded_at,
                source_url,
                confidence,
                collected_at
            FROM market_event_calendar
            WHERE {" AND ".join(active_conditions)}
            ORDER BY event_date ASC, event_type ASC, COALESCE(symbol, '') ASC, title ASC
            LIMIT %s
            """,
            active_params,
        )
    except Exception:
        try:
            return query_fn(
                "finance_meta",
                f"""
                SELECT
                    event_date,
                    event_type,
                    symbol,
                    title,
                    source,
                    source_url,
                    confidence,
                    collected_at
                FROM market_event_calendar
                WHERE {" AND ".join(conditions)}
                ORDER BY event_date ASC, event_type ASC, COALESCE(symbol, '') ASC, title ASC
                LIMIT %s
                """,
                params + [bounded_limit],
            )
        except Exception:
            return []


def _event_source_type(row: dict[str, Any]) -> str:
    persisted = str(row.get("source_type") or "").strip().lower()
    if persisted == "official":
        return "Official"
    if persisted == "provider_estimate":
        return "Provider Estimate"
    if persisted == "unknown":
        return "Unknown"
    event_type = _normalize_event_type_value(row.get("event_type"))
    source = str(row.get("source") or "").strip().lower()
    if source == "federal_reserve_fomc_calendar":
        return "Official"
    if event_type == "EARNINGS":
        if "official" in source or "company" in source:
            return "Official"
        return "Provider Estimate"
    if source:
        return "Provider"
    return "Unknown"


def _event_validation_label(row: dict[str, Any]) -> str:
    status = str(row.get("validation_status") or "").strip().lower()
    if not status and _event_source_type(row) == "Provider Estimate":
        status = "estimate_only"
    labels = {
        "official": "Official",
        "estimate_only": "Estimate only",
        "cross_checked": "Cross-checked",
        "not_confirmed": "Not confirmed",
        "conflict": "Conflict",
        "unknown": "Unknown",
    }
    return labels.get(status, "Unknown" if not status else status.replace("_", " ").title())


def _event_status_label(row: dict[str, Any]) -> str:
    status = str(row.get("event_status") or "active").strip().lower()
    labels = {
        "active": "Active",
        "superseded": "Superseded",
        "stale": "Stale",
    }
    return labels.get(status, status.replace("_", " ").title())


def _event_collected_age_days(row: dict[str, Any], *, today: date) -> int | None:
    value = row.get("collected_at")
    if value in (None, ""):
        return None
    try:
        collected_at = pd.Timestamp(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(collected_at):
        return None
    if collected_at.tzinfo is not None:
        collected_at = collected_at.tz_convert(None)
    age = pd.Timestamp(today).normalize() - collected_at.normalize()
    return max(0, int(age.days))


def _event_freshness(row: dict[str, Any], *, today: date) -> str:
    event_status = str(row.get("event_status") or "active").strip().lower()
    if event_status == "superseded":
        return "Superseded"
    if event_status == "stale":
        return "Stale estimate"
    source_type = _event_source_type(row)
    age_days = _event_collected_age_days(row, today=today)
    if source_type == "Official":
        return "Official"
    if source_type == "Provider Estimate":
        if age_days is None:
            return "Estimate age unknown"
        if age_days > EVENT_ESTIMATE_STALE_DAYS:
            return "Stale estimate"
        return "Current estimate"
    if age_days is None:
        return "Collection age unknown"
    if age_days > EVENT_ESTIMATE_STALE_DAYS:
        return "Stale source"
    return "Current source"


def _event_quality_action(row: dict[str, Any], *, today: date) -> str:
    event_type = _normalize_event_type_value(row.get("event_type"))
    validation = _event_validation_label(row)
    freshness = _event_freshness(row, today=today)
    source_type = _event_source_type(row)
    if freshness == "Stale estimate":
        return "Refresh earnings calendar"
    if event_type == "EARNINGS":
        if validation == "Cross-checked":
            return "No action"
        if validation == "Not confirmed":
            return "Treat as unconfirmed; retry later or inspect source"
        if validation == "Estimate only":
            return "Enable cross-check or refresh closer to date"
        if source_type == "Official":
            return "No action"
        return "Inspect provider source"
    if source_type == "Official":
        return "No action"
    return "Inspect source freshness"


def _event_coverage(rows: list[dict[str, Any]], *, today: date) -> dict[str, Any]:
    source_types = [_event_source_type(row) for row in rows]
    freshness = [_event_freshness(row, today=today) for row in rows]
    validation = [_event_validation_label(row) for row in rows]
    statuses = [_event_status_label(row) for row in rows]
    latest_collected_at = max(
        (_display_datetime(row.get("collected_at")) or "" for row in rows),
        default="",
    ) or None
    return {
        "event_count": len(rows),
        "next_event_date": _iso_date(rows[0].get("event_date")) if rows else None,
        "latest_collected_at": latest_collected_at,
        "source_count": len({str(row.get("source") or "") for row in rows if row.get("source")}),
        "official_count": source_types.count("Official"),
        "estimate_count": source_types.count("Provider Estimate"),
        "estimate_only_count": validation.count("Estimate only"),
        "cross_checked_count": validation.count("Cross-checked"),
        "not_confirmed_count": validation.count("Not confirmed"),
        "stale_estimate_count": freshness.count("Stale estimate"),
        "action_required_count": sum(
            1
            for row in rows
            if _event_quality_action(row, today=today) != "No action"
        ),
        "superseded_count": statuses.count("Superseded"),
    }


def _event_warnings(coverage: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    stale_estimates = int(coverage.get("stale_estimate_count") or 0)
    if stale_estimates > 0:
        warnings.append(
            f"{stale_estimates} earnings estimate row(s) were collected more than "
            f"{EVENT_ESTIMATE_STALE_DAYS} days ago. Refresh Earnings Calendar before acting on those dates."
        )
    not_confirmed = int(coverage.get("not_confirmed_count") or 0)
    if not_confirmed > 0:
        warnings.append(
            f"{not_confirmed} earnings estimate row(s) were not confirmed by the alternate Nasdaq calendar cross-check."
        )
    return warnings


def _event_rows_frame(rows: list[dict[str, Any]], *, today: date) -> pd.DataFrame:
    out = [
        {
            "Date": _iso_date(row.get("event_date")) or "-",
            "Type": row.get("event_type") or "-",
            "Symbol": row.get("symbol") or "-",
            "Title": row.get("title") or "-",
            "Source Type": _event_source_type(row),
            "Validation": _event_validation_label(row),
            "Freshness": _event_freshness(row, today=today),
            "Quality Action": _event_quality_action(row, today=today),
            "Event Status": _event_status_label(row),
            "Age Days": _event_collected_age_days(row, today=today),
            "Source": row.get("source") or "-",
            "Confidence": (
                round(float(row["confidence"]), 2)
                if _safe_float(row.get("confidence")) is not None
                else None
            ),
            "Collected At": _display_datetime(row.get("collected_at")) or "-",
            "Source URL": row.get("source_url") or "-",
        }
        for row in rows
    ]
    return pd.DataFrame(out, columns=EVENT_COLUMNS)


def build_market_events_snapshot(
    *,
    start_date: str | None = None,
    end_date: str | None = None,
    event_type: str | None = "FOMC_MEETING",
    horizon_days: int = 365,
    limit: int = 200,
    today: date | None = None,
    query_fn: QueryFn | None = None,
) -> dict[str, Any]:
    today_value = today or date.today()
    normalized_start = _iso_date(start_date) or today_value.isoformat()
    normalized_end = _iso_date(end_date) or (today_value + timedelta(days=int(horizon_days or 365))).isoformat()
    normalized_type = _normalize_event_type_value(event_type)
    query = query_fn or _default_query
    try:
        rows = _load_market_event_rows(
            start_date=normalized_start,
            end_date=normalized_end,
            event_type=normalized_type,
            limit=limit,
            query_fn=query,
        )
        if not rows:
            return _empty_events_snapshot(
                status="NO_EVENTS",
                start_date=normalized_start,
                end_date=normalized_end,
                event_type=normalized_type,
                message="No stored market events match the selected window. Run a matching event calendar collector first.",
            )
        coverage = _event_coverage(rows, today=today_value)
        return {
            "status": "OK",
            "event_type": normalized_type or "All",
            "rows": _event_rows_frame(rows, today=today_value),
            "date_window": {"start_date": normalized_start, "end_date": normalized_end},
            "coverage": coverage,
            "warnings": _event_warnings(coverage),
        }
    except Exception as exc:
        return _empty_events_snapshot(
            status="ERROR",
            start_date=normalized_start,
            end_date=normalized_end,
            event_type=normalized_type,
            message=f"Market events snapshot failed: {exc}",
        )


def _timestamp_sort_value(value: Any) -> str:
    if value in (None, ""):
        return ""
    try:
        parsed = pd.Timestamp(value)
    except (TypeError, ValueError):
        return str(value)
    if pd.isna(parsed):
        return ""
    return parsed.isoformat()


def _display_run_time(value: Any) -> str:
    return _display_datetime(value) or "-"


def _latest_history_item(history_rows: Sequence[dict[str, Any]], job_names: Sequence[str]) -> dict[str, Any] | None:
    job_name_set = set(job_names)
    matched = [row for row in history_rows if str(row.get("job_name") or "") in job_name_set]
    if not matched:
        return None
    return max(matched, key=lambda row: _timestamp_sort_value(row.get("finished_at") or row.get("started_at")))


def _latest_history_item_with_status(
    history_rows: Sequence[dict[str, Any]],
    job_names: Sequence[str],
    statuses: set[str],
) -> dict[str, Any] | None:
    normalized_statuses = {status.lower() for status in statuses}
    matched = [
        row
        for row in history_rows
        if str(row.get("job_name") or "") in set(job_names)
        and str(row.get("status") or "").lower() in normalized_statuses
    ]
    if not matched:
        return None
    return max(matched, key=lambda row: _timestamp_sort_value(row.get("finished_at") or row.get("started_at")))


def _history_status_overlay(
    base_status: str,
    *,
    latest_run: dict[str, Any] | None,
    latest_success: dict[str, Any] | None,
) -> str:
    if latest_run is None:
        return base_status
    run_status = str(latest_run.get("status") or "").lower()
    if run_status == "failed":
        success_time = _timestamp_sort_value((latest_success or {}).get("finished_at") or (latest_success or {}).get("started_at"))
        run_time = _timestamp_sort_value(latest_run.get("finished_at") or latest_run.get("started_at"))
        if not success_time or run_time >= success_time:
            return "Failed"
    if run_status == "partial_success":
        return "Partial"
    return base_status


def _history_metrics(
    *,
    latest_run: dict[str, Any] | None,
    latest_success: dict[str, Any] | None,
) -> dict[str, Any]:
    source = latest_run or latest_success or {}
    failed_symbols = source.get("failed_symbols") or []
    if not isinstance(failed_symbols, list):
        failed_symbols = []
    return {
        "Last Success": _display_run_time((latest_success or {}).get("finished_at") or (latest_success or {}).get("started_at")),
        "Last Issue": _display_run_time(source.get("finished_at") or source.get("started_at"))
        if str(source.get("status") or "").lower() in {"failed", "partial_success"}
        else "-",
        "Rows": source.get("rows_written") if source else None,
        "Processed": source.get("symbols_processed") if source else None,
        "Failed": len(failed_symbols),
        "Duration Sec": source.get("duration_sec") if source else None,
        "Message": source.get("message") or "-",
    }


def _age_days(value: Any, *, today: date) -> int | None:
    if value in (None, ""):
        return None
    try:
        parsed = pd.Timestamp(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(parsed):
        return None
    if parsed.tzinfo is not None:
        parsed = parsed.tz_convert(None)
    return max(0, int((pd.Timestamp(today).normalize() - parsed.normalize()).days))


def _latest_intraday_ops_rows(query_fn: QueryFn) -> dict[str, dict[str, Any]]:
    try:
        rows = query_fn(
            "finance_price",
            """
            SELECT universe_code, interval_code, MAX(snapshot_time_utc) AS latest_snapshot_time
            FROM market_intraday_snapshot
            WHERE interval_code = %s
            GROUP BY universe_code, interval_code
            """,
            ["5m"],
        )
    except Exception:
        return {}
    return {str(row.get("universe_code") or "").upper(): row for row in rows}


def _latest_universe_ops_rows(query_fn: QueryFn) -> dict[str, dict[str, Any]]:
    try:
        rows = query_fn(
            "finance_meta",
            """
            SELECT
                universe_code,
                COUNT(*) AS active_symbols,
                MAX(collected_at) AS latest_collected_at,
                MAX(as_of_date) AS latest_as_of_date
            FROM market_universe_member
            WHERE active = 1
            GROUP BY universe_code
            """,
            None,
        )
    except Exception:
        return {}
    return {str(row.get("universe_code") or "").upper(): row for row in rows}


def _latest_event_ops_rows(query_fn: QueryFn, *, today: date) -> dict[str, dict[str, Any]]:
    try:
        rows = query_fn(
            "finance_meta",
            """
            SELECT
                event_type,
                COUNT(*) AS active_events,
                SUM(CASE WHEN event_date >= %s THEN 1 ELSE 0 END) AS future_events,
                MIN(CASE WHEN event_date >= %s THEN event_date ELSE NULL END) AS next_event_date,
                MAX(collected_at) AS latest_collected_at
            FROM market_event_calendar
            WHERE COALESCE(event_status, 'active') <> 'superseded'
            GROUP BY event_type
            """,
            [today.isoformat(), today.isoformat()],
        )
    except Exception:
        try:
            rows = query_fn(
                "finance_meta",
                """
                SELECT
                    event_type,
                    COUNT(*) AS active_events,
                    SUM(CASE WHEN event_date >= %s THEN 1 ELSE 0 END) AS future_events,
                    MIN(CASE WHEN event_date >= %s THEN event_date ELSE NULL END) AS next_event_date,
                    MAX(collected_at) AS latest_collected_at
                FROM market_event_calendar
                GROUP BY event_type
                """,
                [today.isoformat(), today.isoformat()],
            )
        except Exception:
            return {}
    return {str(row.get("event_type") or "").upper(): row for row in rows}


def _intraday_ops_status(row: dict[str, Any] | None) -> tuple[str, str, str]:
    if not row or not row.get("latest_snapshot_time"):
        return "Missing", "No stored 5m snapshot", "Run the daily snapshot collector."
    age = _stale_minutes(row.get("latest_snapshot_time"))
    if age is None:
        return "Missing", "Snapshot age unknown", "Run the daily snapshot collector."
    if age <= MARKET_INTRADAY_REFRESH_MINUTES:
        return "OK", f"{age}m old", "No action needed."
    if age <= MARKET_INTRADAY_STALE_MINUTES:
        return "Due", f"{age}m old", "Refresh if you need live daily movers."
    return "Stale", f"{age}m old", "Refresh before using daily movers."


def _days_based_ops_status(
    *,
    latest_collected_at: Any,
    active_count: int,
    fresh_days: int,
    stale_days: int,
    today: date,
    missing_text: str,
) -> tuple[str, str]:
    if active_count <= 0:
        return "Missing", missing_text
    age = _age_days(latest_collected_at, today=today)
    if age is None:
        return "Due", "Collection age unknown"
    if age <= fresh_days:
        return "OK", f"{age}d old"
    if age <= stale_days:
        return "Due", f"{age}d old"
    return "Stale", f"{age}d old"


def _combined_event_ops_row(
    event_rows: dict[str, dict[str, Any]],
    event_types: Sequence[str],
) -> dict[str, Any] | None:
    rows = [event_rows.get(str(event_type).upper()) for event_type in event_types]
    rows = [row for row in rows if row]
    if not rows:
        return None
    covered_event_types = sorted(
        {
            str(row.get("event_type") or "").upper()
            for row in rows
            if row.get("event_type")
        }
    )
    future_events = sum(int(row.get("future_events") or 0) for row in rows)
    active_events = sum(int(row.get("active_events") or 0) for row in rows)
    next_dates = [_iso_date(row.get("next_event_date")) for row in rows if _iso_date(row.get("next_event_date"))]
    collected = [row.get("latest_collected_at") for row in rows if row.get("latest_collected_at")]
    return {
        "future_events": future_events,
        "active_events": active_events,
        "next_event_date": min(next_dates) if next_dates else None,
        "latest_collected_at": max(collected, key=_timestamp_sort_value) if collected else None,
        "covered_event_types": covered_event_types,
    }


def _ops_row(
    *,
    area: str,
    base_status: str,
    data_freshness: str,
    next_action: str,
    job_names: Sequence[str],
    history_rows: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    latest_run = _latest_history_item(history_rows, job_names)
    latest_success = _latest_history_item_with_status(history_rows, job_names, {"success"})
    status = _history_status_overlay(base_status, latest_run=latest_run, latest_success=latest_success)
    metrics = _history_metrics(latest_run=latest_run, latest_success=latest_success)
    if status == "OK":
        action = "No action needed."
    elif status == "Failed":
        action = "Open run history details and rerun after checking the failure message."
    elif status == "Partial":
        action = "Inspect failed symbols, then rerun a bounded collection."
    else:
        action = next_action
    return {
        "Area": area,
        "Status": status,
        "Data Freshness": data_freshness,
        **metrics,
        "Next Action": action,
    }


def _ops_coverage(rows: list[dict[str, Any]]) -> dict[str, Any]:
    statuses = [str(row.get("Status") or "") for row in rows]
    success_times = [row.get("Last Success") for row in rows if row.get("Last Success") not in (None, "-")]
    issue_times = [row.get("Last Issue") for row in rows if row.get("Last Issue") not in (None, "-")]
    return {
        "job_count": len(rows),
        "ok_count": statuses.count("OK"),
        "due_count": statuses.count("Due"),
        "stale_count": statuses.count("Stale"),
        "missing_count": statuses.count("Missing"),
        "failed_count": statuses.count("Failed"),
        "partial_count": statuses.count("Partial"),
        "latest_success_at": max(success_times) if success_times else None,
        "latest_issue_at": max(issue_times) if issue_times else None,
    }


def build_collection_ops_snapshot(
    *,
    history_rows: Sequence[dict[str, Any]] | None = None,
    today: date | None = None,
    query_fn: QueryFn | None = None,
) -> dict[str, Any]:
    """Build the Overview Data Health read model from stored DB freshness and local job history."""
    query = query_fn or _default_query
    today_value = today or date.today()
    history = list(history_rows or [])

    try:
        intraday_rows = _latest_intraday_ops_rows(query)
        universe_rows = _latest_universe_ops_rows(query)
        event_rows = _latest_event_ops_rows(query, today=today_value)
    except Exception as exc:
        return _empty_ops_snapshot(message=f"Collection ops snapshot failed: {exc}")

    rows: list[dict[str, Any]] = []
    sp500_universe = universe_rows.get("SP500")
    universe_status, universe_freshness = _days_based_ops_status(
        latest_collected_at=(sp500_universe or {}).get("latest_collected_at"),
        active_count=int((sp500_universe or {}).get("active_symbols") or 0),
        fresh_days=7,
        stale_days=30,
        today=today_value,
        missing_text="No active S&P 500 universe rows",
    )
    rows.append(
        _ops_row(
            area="S&P 500 Universe",
            base_status=universe_status,
            data_freshness=universe_freshness,
            next_action="Refresh S&P 500 universe membership.",
            job_names=["collect_sp500_universe"],
            history_rows=history,
        )
    )

    for target in OPS_INTRADAY_TARGETS:
        base_status, freshness, default_action = _intraday_ops_status(
            intraday_rows.get(str(target["universe_code"]))
        )
        rows.append(
            _ops_row(
                area=str(target["area"]),
                base_status=base_status,
                data_freshness=freshness,
                next_action=str(target["missing_action"] if base_status == "Missing" else target["due_action"] or default_action),
                job_names=list(target["job_names"]),
                history_rows=history,
            )
        )

    for target in OPS_EVENT_TARGETS:
        target_event_types = list(target.get("event_types") or [target["event_type"]])
        event_row = _combined_event_ops_row(event_rows, target_event_types)
        active_count = int((event_row or {}).get("future_events") or (event_row or {}).get("active_events") or 0)
        base_status, freshness = _days_based_ops_status(
            latest_collected_at=(event_row or {}).get("latest_collected_at"),
            active_count=active_count,
            fresh_days=int(target["fresh_days"]),
            stale_days=int(target["stale_days"]),
            today=today_value,
            missing_text=f"No future {target['event_type']} rows",
        )
        required_event_types = list(target.get("event_types") or [])
        if event_row and required_event_types:
            covered_count = len(event_row.get("covered_event_types") or [])
            required_count = len(required_event_types)
            freshness = f"{freshness}; covered {covered_count}/{required_count}"
            if covered_count < required_count and base_status == "OK":
                base_status = "Due"
        next_event = _iso_date((event_row or {}).get("next_event_date"))
        if next_event and freshness != "No future rows":
            freshness = f"{freshness}; next {next_event}"
        rows.append(
            _ops_row(
                area=str(target["area"]),
                base_status=base_status,
                data_freshness=freshness,
                next_action=str(target["missing_action"] if base_status == "Missing" else target["due_action"]),
                job_names=list(target["job_names"]),
                history_rows=history,
            )
        )

    coverage = _ops_coverage(rows)
    review_count = sum(
        int(coverage.get(key) or 0)
        for key in ("due_count", "stale_count", "missing_count", "failed_count", "partial_count")
    )
    status = "OK" if review_count == 0 else "REVIEW"
    warnings: list[str] = []
    if int(coverage.get("failed_count") or 0) > 0:
        warnings.append("One or more market intelligence collection jobs failed after the last successful run.")
    if int(coverage.get("missing_count") or 0) > 0:
        warnings.append("One or more market intelligence data sets are missing stored rows.")
    if int(coverage.get("stale_count") or 0) > 0:
        warnings.append("One or more market intelligence data sets are stale and should be refreshed.")
    return {
        "status": status,
        "rows": pd.DataFrame(rows, columns=OPS_COLUMNS),
        "coverage": coverage,
        "warnings": warnings,
    }


def _ranked_movers_frame(rows: list[dict[str, Any]], *, top_n: int) -> pd.DataFrame:
    ranked = sorted(rows, key=lambda row: (-float(row["return_pct"]), row["symbol"]))[:top_n]
    out = [
        {
            "Rank": index,
            "Symbol": row["symbol"],
            "Name": row["name"] or "-",
            "Return %": round(float(row["return_pct"]), 2),
            "Start Price": round(float(row["start_price"]), 4),
            "End Price": round(float(row["end_price"]), 4),
            "Sector": row["sector"],
            "Industry": row["industry"],
            "Market Cap": int(row["market_cap"]) if row["market_cap"] else None,
            "Start Date": row["start_date"],
            "End Date": row["end_date"],
            "Price Source": row.get("price_source") or "EOD DB",
        }
        for index, row in enumerate(ranked, start=1)
    ]
    return _rows_frame(out, columns=MOVERS_COLUMNS)


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


def _build_intraday_movers_snapshot(
    *,
    universe: list[dict[str, Any]],
    universe_code: str,
    universe_limit: int,
    period: str,
    top_n: int,
    sector: str | None,
    interval: str,
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
        if row.get("provider_status") != "ok" or previous_close is None or latest_price is None or return_pct is None:
            missing_rows.append(
                _missing_row(
                    item=item,
                    reason=row.get("error_msg") or "missing intraday return",
                    start_date="Previous Close",
                    end_date=_display_datetime(row.get("quote_time_utc")) or snapshot_time,
                    start_price=previous_close,
                    end_price=latest_price,
                    latest_price_date=_iso_date(row.get("quote_time_utc")),
                )
            )
            continue
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
                "start_date": "Previous Close",
                "end_date": _display_datetime(row.get("quote_time_utc")) or snapshot_time,
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
    return {
        "status": "OK",
        "period": period,
        "period_label": PERIOD_LABELS[period],
        "universe_code": universe_code,
        "universe_label": UNIVERSE_LABELS.get(universe_code, universe_code),
        "universe_limit": universe_limit,
        "sector": sector or "All",
        "top_n": top_n,
        "rows": _ranked_movers_frame(return_rows, top_n=top_n),
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
            return _empty_movers_snapshot(
                status="NO_UNIVERSE",
                period=normalized_period,
                universe_code=normalized_universe,
                universe_limit=normalized_limit,
                top_n=normalized_top_n,
                sector=sector,
                message="Selected universe has no symbols. For S&P 500, run the universe refresh first.",
            )

        if normalized_period == "daily" and prefer_intraday:
            intraday_snapshot = _build_intraday_movers_snapshot(
                universe=universe,
                universe_code=normalized_universe,
                universe_limit=normalized_limit,
                period=normalized_period,
                top_n=normalized_top_n,
                sector=sector,
                interval=intraday_interval,
                query_fn=query,
            )
            if intraday_snapshot is not None:
                return intraday_snapshot

        effective_min_rows = min(int(min_price_rows), max(50, int(len(universe) * 0.75)))
        date_window = resolve_effective_market_dates(
            period=normalized_period,
            min_price_rows=effective_min_rows,
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

        return_rows, missing_rows = _build_return_rows(
            universe=universe,
            start_date=str(date_window["start_date"]),
            end_date=str(date_window["end_date"]),
            query_fn=query,
        )
        coverage = _coverage(
            universe_count=len(universe),
            returnable_count=len(return_rows),
            date_window=date_window,
            price_mode="EOD DB",
            extra=_universe_metadata(universe, universe_code=normalized_universe),
        )
        if normalized_period == "daily" and prefer_intraday:
            coverage["refresh_state"] = _intraday_refresh_state(
                snapshot_status="OK",
                period=normalized_period,
                coverage=coverage,
            )
        warnings = _coverage_warnings(coverage, date_window=date_window)
        if normalized_period == "daily" and prefer_intraday:
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
            "rows": _ranked_movers_frame(return_rows, top_n=normalized_top_n),
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


def build_group_leadership_snapshot(
    *,
    universe_limit: int = 2000,
    group_by: str = "sector",
    top_n: int = 10,
    min_group_size: int = 5,
    min_price_rows: int = 1000,
    today: date | None = None,
    query_fn: QueryFn | None = None,
) -> dict[str, Any]:
    normalized_group = str(group_by or "sector").strip().lower()
    if normalized_group not in VALID_GROUPS:
        raise ValueError(f"Unsupported group_by: {group_by!r}")

    normalized_limit = _normalize_limit(universe_limit, default=2000, min_value=100, max_value=3000)
    normalized_top_n = _normalize_limit(top_n, default=10, min_value=5, max_value=100)
    query = query_fn or _default_query

    try:
        universe = _load_universe(universe_code="TOP2000", universe_limit=normalized_limit, query_fn=query)
        date_window = resolve_effective_market_dates(
            period="monthly",
            min_price_rows=min(min_price_rows, max(50, int(len(universe) * 0.75))),
            today=today,
            query_fn=query,
        )
        if date_window.get("status") != "OK":
            snapshot = _empty_group_snapshot(
                status="INSUFFICIENT_DATA",
                group_by=normalized_group,
                universe_limit=normalized_limit,
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
                }
            )
            return snapshot

        return_rows, missing_rows = _build_return_rows(
            universe=universe,
            start_date=str(date_window["start_date"]),
            end_date=str(date_window["end_date"]),
            query_fn=query,
        )

        grouped: dict[str, list[dict[str, Any]]] = {}
        for row in return_rows:
            group_name = str(row.get(normalized_group) or "Unknown").strip() or "Unknown"
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
            group_rows.append(
                {
                    "group": group_name,
                    "group_type": normalized_group.title(),
                    "symbols": len(rows),
                    "equal_weight_return": equal_weight_return,
                    "market_cap_weighted_return": weighted_return,
                    "top_symbol": top_symbol["symbol"],
                    "top_symbol_return": top_symbol["return_pct"],
                    "start_date": date_window["start_date"],
                    "end_date": date_window["end_date"],
                }
            )

        ranked = sorted(
            group_rows,
            key=lambda row: (
                -float(row["market_cap_weighted_return"]),
                -float(row["equal_weight_return"]),
                row["group"],
            ),
        )[:normalized_top_n]
        rows = [
            {
                "Rank": index,
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
            for index, row in enumerate(ranked, start=1)
        ]
        coverage = _coverage(
            universe_count=len(universe),
            returnable_count=len(return_rows),
            date_window=date_window,
        )
        return {
            "status": "OK",
            "group_by": normalized_group,
            "universe_limit": normalized_limit,
            "top_n": normalized_top_n,
            "rows": pd.DataFrame(rows, columns=GROUP_COLUMNS),
            "missing_rows": pd.DataFrame(missing_rows, columns=MISSING_COLUMNS),
            "date_window": date_window,
            "coverage": coverage,
            "warnings": _coverage_warnings(coverage, date_window=date_window),
        }
    except Exception as exc:
        return _empty_group_snapshot(
            status="ERROR",
            group_by=normalized_group,
            universe_limit=normalized_limit,
            top_n=normalized_top_n,
            message=f"Group leadership snapshot failed: {exc}",
        )
