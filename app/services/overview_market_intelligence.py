from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import date, datetime
from typing import Any

import pandas as pd


QueryFn = Callable[[str, str, Sequence[Any] | None], list[dict[str, Any]]]

VALID_PERIODS = {"daily": 1, "weekly": 5, "monthly": 21}
PERIOD_LABELS = {"daily": "Daily", "weekly": "Weekly", "monthly": "Monthly"}
VALID_GROUPS = {"sector", "industry"}
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


def _stale_days(effective_date: str | None, *, today: date | None = None) -> int | None:
    if not effective_date:
        return None
    today_value = pd.Timestamp(today or date.today()).normalize()
    effective_value = pd.Timestamp(effective_date).normalize()
    if pd.isna(effective_value):
        return None
    return max(0, int((today_value - effective_value).days))


def _empty_movers_snapshot(
    *,
    status: str,
    period: str,
    universe_limit: int,
    top_n: int,
    message: str,
) -> dict[str, Any]:
    return {
        "status": status,
        "period": period,
        "period_label": PERIOD_LABELS.get(period, period),
        "universe_limit": universe_limit,
        "top_n": top_n,
        "rows": pd.DataFrame(columns=MOVERS_COLUMNS),
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


def _normalize_limit(value: int, *, default: int, min_value: int, max_value: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(min_value, min(parsed, max_value))


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


def _load_universe(
    *,
    universe_limit: int,
    query_fn: QueryFn,
) -> list[dict[str, Any]]:
    return query_fn(
        "finance_meta",
        """
        SELECT
            symbol,
            long_name,
            sector,
            industry,
            market_cap
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
    )


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


def _build_return_rows(
    *,
    universe: list[dict[str, Any]],
    start_date: str,
    end_date: str,
    query_fn: QueryFn,
) -> list[dict[str, Any]]:
    symbols = [str(row.get("symbol") or "").strip().upper() for row in universe if row.get("symbol")]
    price_map = _load_prices_for_dates(symbols=symbols, dates=[start_date, end_date], query_fn=query_fn)
    return_rows: list[dict[str, Any]] = []

    for item in universe:
        symbol = str(item.get("symbol") or "").strip().upper()
        start_price = price_map.get((symbol, start_date))
        end_price = price_map.get((symbol, end_date))
        if start_price is None or end_price is None or start_price <= 0:
            continue
        return_pct = (end_price / start_price - 1.0) * 100.0
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
            }
        )
    return return_rows


def _coverage(
    *,
    universe_count: int,
    returnable_count: int,
    date_window: dict[str, Any],
) -> dict[str, Any]:
    return {
        "universe_count": universe_count,
        "returnable_count": returnable_count,
        "missing_count": max(0, universe_count - returnable_count),
        "latest_raw_date": date_window.get("latest_raw_date"),
        "effective_end_date": date_window.get("effective_end_date"),
        "stale_days": date_window.get("stale_days"),
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
    return warnings


def build_market_movers_snapshot(
    *,
    universe_limit: int = 1000,
    period: str = "daily",
    top_n: int = 20,
    min_price_rows: int = 1000,
    today: date | None = None,
    query_fn: QueryFn | None = None,
) -> dict[str, Any]:
    normalized_period = str(period or "daily").strip().lower()
    normalized_limit = _normalize_limit(universe_limit, default=1000, min_value=100, max_value=3000)
    normalized_top_n = _normalize_limit(top_n, default=20, min_value=5, max_value=100)
    query = query_fn or _default_query

    try:
        date_window = resolve_effective_market_dates(
            period=normalized_period,
            min_price_rows=min_price_rows,
            today=today,
            query_fn=query,
        )
        if date_window.get("status") != "OK":
            snapshot = _empty_movers_snapshot(
                status="INSUFFICIENT_DATA",
                period=normalized_period,
                universe_limit=normalized_limit,
                top_n=normalized_top_n,
                message=str(date_window.get("message") or ""),
            )
            snapshot["date_window"] = date_window
            snapshot["coverage"].update(
                {
                    "latest_raw_date": date_window.get("latest_raw_date"),
                    "effective_end_date": date_window.get("effective_end_date"),
                    "stale_days": date_window.get("stale_days"),
                }
            )
            return snapshot

        universe = _load_universe(universe_limit=normalized_limit, query_fn=query)
        return_rows = _build_return_rows(
            universe=universe,
            start_date=str(date_window["start_date"]),
            end_date=str(date_window["end_date"]),
            query_fn=query,
        )
        ranked = sorted(return_rows, key=lambda row: (-float(row["return_pct"]), row["symbol"]))[:normalized_top_n]
        rows = [
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
            "period": normalized_period,
            "period_label": PERIOD_LABELS[normalized_period],
            "universe_limit": normalized_limit,
            "top_n": normalized_top_n,
            "rows": pd.DataFrame(rows, columns=MOVERS_COLUMNS),
            "date_window": date_window,
            "coverage": coverage,
            "warnings": _coverage_warnings(coverage, date_window=date_window),
        }
    except Exception as exc:
        return _empty_movers_snapshot(
            status="ERROR",
            period=normalized_period,
            universe_limit=normalized_limit,
            top_n=normalized_top_n,
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
        date_window = resolve_effective_market_dates(
            period="monthly",
            min_price_rows=min_price_rows,
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
                    "latest_raw_date": date_window.get("latest_raw_date"),
                    "effective_end_date": date_window.get("effective_end_date"),
                    "stale_days": date_window.get("stale_days"),
                }
            )
            return snapshot

        universe = _load_universe(universe_limit=normalized_limit, query_fn=query)
        return_rows = _build_return_rows(
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
