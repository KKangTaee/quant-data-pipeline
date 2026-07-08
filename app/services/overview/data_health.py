from __future__ import annotations

from collections.abc import Callable, Sequence

from datetime import date

from typing import Any

import pandas as pd

from finance.loaders.sentiment import CORE_SENTIMENT_SERIES

QueryFn = Callable[[str, str, Sequence[Any] | None], list[dict[str, Any]]]

MARKET_INTRADAY_REFRESH_MINUTES = 5

MARKET_INTRADAY_STALE_MINUTES = 15

EVENT_ESTIMATE_STALE_DAYS = 14

OPS_COLUMNS = [
    "Area",
    "Scope",
    "Status",
    "Data Freshness",
    "Last Success",
    "Last Issue",
    "Last Auto Run",
    "Auto Source",
    "Next Auto Due",
    "Last Manual Run",
    "Failure Streak",
    "Rows",
    "Processed",
    "Failed",
    "Duration Sec",
    "Next Action",
    "Message",
]

DATA_HEALTH_DIRECT_MARKET_CONTEXT_SCOPE = "direct_market_context"

DATA_HEALTH_REFERENCE_CONTEXT_SCOPE = "reference_context"

DATA_HEALTH_FUTURES_MACRO_1M_AREA = "Futures Macro 1m OHLCV"

DATA_HEALTH_FUTURES_MACRO_DAILY_AREA = "Futures Macro Daily OHLCV"

DATA_HEALTH_AREA_ALIASES = {
    "Futures Monitor 1m OHLCV": DATA_HEALTH_FUTURES_MACRO_1M_AREA,
    "Futures Monitor Daily OHLCV": DATA_HEALTH_FUTURES_MACRO_DAILY_AREA,
}

def normalize_overview_data_health_area(area: Any) -> str:
    text = str(area or "").strip()
    return DATA_HEALTH_AREA_ALIASES.get(text, text or "Unknown")

DATA_HEALTH_AREA_SCOPES = {
    "S&P 500 Universe": DATA_HEALTH_DIRECT_MARKET_CONTEXT_SCOPE,
    "S&P 500 Daily Snapshot": DATA_HEALTH_DIRECT_MARKET_CONTEXT_SCOPE,
    "Market Sentiment": DATA_HEALTH_DIRECT_MARKET_CONTEXT_SCOPE,
    "FOMC Calendar": DATA_HEALTH_DIRECT_MARKET_CONTEXT_SCOPE,
    "Earnings Calendar": DATA_HEALTH_DIRECT_MARKET_CONTEXT_SCOPE,
    "Macro Calendar": DATA_HEALTH_DIRECT_MARKET_CONTEXT_SCOPE,
    "Top1000 Daily Snapshot": DATA_HEALTH_REFERENCE_CONTEXT_SCOPE,
    "Top2000 Daily Snapshot": DATA_HEALTH_REFERENCE_CONTEXT_SCOPE,
    DATA_HEALTH_FUTURES_MACRO_1M_AREA: DATA_HEALTH_REFERENCE_CONTEXT_SCOPE,
    DATA_HEALTH_FUTURES_MACRO_DAILY_AREA: DATA_HEALTH_REFERENCE_CONTEXT_SCOPE,
}

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

OPS_FUTURES_TARGETS = [
    {
        "area": DATA_HEALTH_FUTURES_MACRO_1M_AREA,
        "job_names": ["collect_futures_ohlcv"],
        "missing_action": "Run Refresh Futures OHLCV from Overview > Futures Macro.",
        "due_action": "Refresh Futures OHLCV before using pre-open futures context.",
    },
]

OPS_SENTIMENT_TARGET = {
    "area": "Market Sentiment",
    "job_names": ["collect_market_sentiment"],
    "missing_action": "Run Refresh Market Sentiment from Overview > Sentiment or Ingestion.",
    "due_action": "Refresh CNN Fear & Greed / AAII sentiment before relying on market sentiment context.",
}

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

OPS_SCHEDULE_CADENCE_MINUTES = {
    "collect_sp500_universe": 24 * 60,
    "collect_sp500_intraday_snapshot": 5,
    "collect_top1000_intraday_snapshot": 15,
    "collect_top2000_intraday_snapshot": 30,
    "collect_futures_ohlcv": 1,
    "collect_market_sentiment": 24 * 60,
    "collect_fomc_calendar": 24 * 60,
    "collect_earnings_calendar": 24 * 60,
    "collect_macro_calendar": 24 * 60,
}

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
            "direct_market_context_count": 0,
            "reference_context_count": 0,
            "direct_market_context_review_count": 0,
            "reference_context_review_count": 0,
            "latest_success_at": None,
            "latest_issue_at": None,
        },
        "warnings": [message] if message else [],
    }

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

def _history_execution_mode(row: dict[str, Any]) -> str:
    metadata = row.get("run_metadata")
    if isinstance(metadata, dict):
        mode = str(metadata.get("execution_mode") or "").strip().lower()
        if mode:
            return mode
    return str(row.get("execution_mode") or "").strip().lower() or "manual"

def _latest_history_item_with_mode(
    history_rows: Sequence[dict[str, Any]],
    job_names: Sequence[str],
    execution_mode: str,
) -> dict[str, Any] | None:
    return _latest_history_item_with_modes(history_rows, job_names, {execution_mode})

def _latest_history_item_with_modes(
    history_rows: Sequence[dict[str, Any]],
    job_names: Sequence[str],
    execution_modes: set[str],
) -> dict[str, Any] | None:
    job_name_set = set(job_names)
    normalized_modes = {str(mode or "").strip().lower() for mode in execution_modes if str(mode or "").strip()}
    matched = [
        row
        for row in history_rows
        if str(row.get("job_name") or "") in job_name_set
        and _history_execution_mode(row) in normalized_modes
    ]
    if not matched:
        return None
    return max(matched, key=lambda row: _timestamp_sort_value(row.get("finished_at") or row.get("started_at")))

def _automation_source_label(row: dict[str, Any] | None) -> str:
    mode = _history_execution_mode(row or {}) if row else ""
    if mode == "browser_auto":
        return "Browser Auto"
    if mode == "scheduled":
        return "Scheduled"
    if not mode:
        return "-"
    return mode.replace("_", " ").title()

def _failure_streak(history_rows: Sequence[dict[str, Any]], job_names: Sequence[str]) -> int:
    job_name_set = set(job_names)
    matched = [
        row for row in history_rows
        if str(row.get("job_name") or "") in job_name_set
    ]
    matched = sorted(
        matched,
        key=lambda row: _timestamp_sort_value(row.get("finished_at") or row.get("started_at")),
        reverse=True,
    )
    streak = 0
    for row in matched:
        status = str(row.get("status") or "").lower()
        if status == "success":
            break
        if status in {"failed", "partial_success"}:
            streak += 1
            continue
        break
    return streak

def _next_auto_due_text(
    latest_auto: dict[str, Any] | None,
    job_names: Sequence[str],
) -> str:
    cadence_values = [
        OPS_SCHEDULE_CADENCE_MINUTES[job_name]
        for job_name in job_names
        if job_name in OPS_SCHEDULE_CADENCE_MINUTES
    ]
    if not cadence_values:
        return "-"
    cadence_minutes = min(cadence_values)
    if latest_auto is None:
        return "Due now"
    raw_time = latest_auto.get("finished_at") or latest_auto.get("started_at")
    if raw_time in (None, ""):
        return "Due now"
    ts = pd.Timestamp(raw_time)
    if pd.isna(ts):
        return "Due now"
    next_time = ts + pd.Timedelta(minutes=cadence_minutes)
    return _display_datetime(next_time) or "Due now"

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
    latest_auto: dict[str, Any] | None,
    latest_manual: dict[str, Any] | None,
    job_names: Sequence[str],
    failure_streak: int,
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
        "Last Auto Run": _display_run_time((latest_auto or {}).get("finished_at") or (latest_auto or {}).get("started_at")),
        "Auto Source": _automation_source_label(latest_auto),
        "Next Auto Due": _next_auto_due_text(latest_auto, job_names),
        "Last Manual Run": _display_run_time((latest_manual or {}).get("finished_at") or (latest_manual or {}).get("started_at")),
        "Failure Streak": failure_streak,
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

def _latest_futures_ops_row(query_fn: QueryFn) -> dict[str, Any] | None:
    try:
        rows = query_fn(
            "finance_price",
            """
            SELECT
                MAX(candle_time_utc) AS latest_candle_time,
                COUNT(DISTINCT provider_symbol) AS active_symbols,
                COUNT(*) AS candle_rows
            FROM futures_ohlcv
            WHERE interval_code = %s
            """,
            ["1m"],
        )
    except Exception:
        return None
    return dict(rows[0]) if rows else None

def _latest_sentiment_ops_row(query_fn: QueryFn) -> dict[str, Any] | None:
    try:
        placeholders = ",".join(["%s"] * len(CORE_SENTIMENT_SERIES))
        rows = query_fn(
            "finance_meta",
            f"""
            SELECT
                MAX(observation_date) AS latest_observation_date,
                MAX(collected_at) AS latest_collected_at,
                COUNT(DISTINCT series_id) AS series_count
            FROM macro_series_observation
            WHERE series_id IN ({placeholders})
              AND source IN (%s, %s)
            """,
            [*CORE_SENTIMENT_SERIES, "cnn_fear_greed", "aaii_sentiment_survey"],
        )
    except Exception:
        return None
    return dict(rows[0]) if rows else None

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

def _futures_ops_status(row: dict[str, Any] | None) -> tuple[str, str, str]:
    if not row or not row.get("latest_candle_time") or int(row.get("active_symbols") or 0) <= 0:
        return "Missing", "No stored 1m futures candles", "Run Refresh Futures OHLCV."
    age = _stale_minutes(row.get("latest_candle_time"))
    if age is None:
        return "Missing", "Futures candle age unknown", "Run Refresh Futures OHLCV."
    active_symbols = int(row.get("active_symbols") or 0)
    if age <= 2:
        return "OK", f"{age}m old; {active_symbols} symbols", "No action needed."
    if age <= 10:
        return "Due", f"{age}m old; {active_symbols} symbols", "Refresh if you need current pre-open context."
    return "Stale", f"{age}m old; {active_symbols} symbols", "Refresh before using futures context."

def _sentiment_ops_status(row: dict[str, Any] | None, *, today: date) -> tuple[str, str, str]:
    series_count = int((row or {}).get("series_count") or 0)
    latest_observation = _iso_date((row or {}).get("latest_observation_date"))
    if not row or not latest_observation or series_count <= 0:
        return "Missing", "No stored CNN / AAII sentiment observations", "Run Refresh Market Sentiment."
    age = _stale_days(latest_observation, today=today)
    if age is None:
        return "Due", f"Latest date unknown; {series_count}/5 series", "Run Refresh Market Sentiment."
    freshness = f"{age}d old; latest {latest_observation}; {series_count}/5 series"
    if series_count < 2:
        return "Due", freshness, "Refresh CNN Fear & Greed and AAII sentiment."
    if age <= 7:
        return "OK", freshness, "No action needed."
    if age <= 14:
        return "Due", freshness, "Refresh sentiment if you need current market context."
    return "Stale", freshness, "Refresh before using sentiment context."

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

def _ops_area_scope(area: str) -> str:
    return DATA_HEALTH_AREA_SCOPES.get(normalize_overview_data_health_area(area), DATA_HEALTH_REFERENCE_CONTEXT_SCOPE)

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
    latest_auto = _latest_history_item_with_modes(history_rows, job_names, {"scheduled", "browser_auto"})
    latest_manual = _latest_history_item_with_mode(history_rows, job_names, "manual")
    failure_streak = _failure_streak(history_rows, job_names)
    status = _history_status_overlay(base_status, latest_run=latest_run, latest_success=latest_success)
    metrics = _history_metrics(
        latest_run=latest_run,
        latest_success=latest_success,
        latest_auto=latest_auto,
        latest_manual=latest_manual,
        job_names=job_names,
        failure_streak=failure_streak,
    )
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
        "Scope": _ops_area_scope(area),
        "Status": status,
        "Data Freshness": data_freshness,
        **metrics,
        "Next Action": action,
    }

def _ops_coverage(rows: list[dict[str, Any]]) -> dict[str, Any]:
    statuses = [str(row.get("Status") or "") for row in rows]
    review_statuses = {"Due", "Stale", "Missing", "Failed", "Partial"}
    scopes = [str(row.get("Scope") or _ops_area_scope(str(row.get("Area") or ""))) for row in rows]
    success_times = [row.get("Last Success") for row in rows if row.get("Last Success") not in (None, "-")]
    issue_times = [row.get("Last Issue") for row in rows if row.get("Last Issue") not in (None, "-")]
    auto_times = [
        row.get("Last Auto Run") for row in rows
        if row.get("Last Auto Run") not in (None, "-")
    ]
    failure_streaks = [
        int(row.get("Failure Streak") or 0) for row in rows
        if str(row.get("Failure Streak") or "").isdigit() or isinstance(row.get("Failure Streak"), int)
    ]
    return {
        "job_count": len(rows),
        "ok_count": statuses.count("OK"),
        "due_count": statuses.count("Due"),
        "stale_count": statuses.count("Stale"),
        "missing_count": statuses.count("Missing"),
        "failed_count": statuses.count("Failed"),
        "partial_count": statuses.count("Partial"),
        "direct_market_context_count": scopes.count(DATA_HEALTH_DIRECT_MARKET_CONTEXT_SCOPE),
        "reference_context_count": scopes.count(DATA_HEALTH_REFERENCE_CONTEXT_SCOPE),
        "direct_market_context_review_count": sum(
            1
            for row in rows
            if str(row.get("Scope") or _ops_area_scope(str(row.get("Area") or "")))
            == DATA_HEALTH_DIRECT_MARKET_CONTEXT_SCOPE
            and str(row.get("Status") or "") in review_statuses
        ),
        "reference_context_review_count": sum(
            1
            for row in rows
            if str(row.get("Scope") or _ops_area_scope(str(row.get("Area") or "")))
            == DATA_HEALTH_REFERENCE_CONTEXT_SCOPE
            and str(row.get("Status") or "") in review_statuses
        ),
        "latest_success_at": max(success_times) if success_times else None,
        "latest_issue_at": max(issue_times) if issue_times else None,
        "latest_auto_at": max(auto_times) if auto_times else None,
        "max_failure_streak": max(failure_streaks) if failure_streaks else 0,
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
        futures_row = _latest_futures_ops_row(query)
        sentiment_row = _latest_sentiment_ops_row(query)
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

    for target in OPS_FUTURES_TARGETS:
        base_status, freshness, default_action = _futures_ops_status(futures_row)
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

    sentiment_status, sentiment_freshness, sentiment_default_action = _sentiment_ops_status(
        sentiment_row,
        today=today_value,
    )
    rows.append(
        _ops_row(
            area=str(OPS_SENTIMENT_TARGET["area"]),
            base_status=sentiment_status,
            data_freshness=sentiment_freshness,
            next_action=str(
                OPS_SENTIMENT_TARGET["missing_action"]
                if sentiment_status == "Missing"
                else OPS_SENTIMENT_TARGET["due_action"] or sentiment_default_action
            ),
            job_names=list(OPS_SENTIMENT_TARGET["job_names"]),
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

def _cockpit_status_text(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("label") or value.get("status") or "").strip()
    return str(value or "").strip()

def _cockpit_status_tone(status: Any) -> str:
    if isinstance(status, dict) and status.get("tone"):
        return str(status.get("tone"))
    normalized = _cockpit_status_text(status).lower()
    if normalized in {"ok", "success", "actual", "high", "fresh"}:
        return "positive"
    if normalized in {"reference_limit", "meta"}:
        return "neutral"
    if normalized in {"failed", "error", "missing", "no_universe", "insufficient_data"}:
        return "danger"
    if normalized in {"review", "due", "stale", "partial", "not_run", "no_data"}:
        return "warning"
    return "neutral"

DATA_HEALTH_HANDOFF_TARGETS: dict[str, dict[str, str]] = {
    "S&P 500 Universe": {
        "owner_surface": "Workspace > Overview bounded action facade",
        "target_surface": "Workspace > Overview > Market Movers > 유니버스 갱신",
        "collection_action": "Run S&P 500 universe refresh through the existing Overview action facade.",
    },
    "S&P 500 Daily Snapshot": {
        "owner_surface": "Workspace > Overview bounded action facade",
        "target_surface": "Workspace > Overview > Market Movers > 일중 스냅샷 갱신",
        "collection_action": "Run the S&P 500 intraday snapshot refresh from Market Movers.",
    },
    "Top1000 Daily Snapshot": {
        "owner_surface": "Workspace > Overview bounded action facade",
        "target_surface": "Workspace > Overview > Market Movers > Top1000 > 일중 스냅샷 갱신",
        "collection_action": "Run the Top1000 intraday snapshot refresh from Market Movers.",
    },
    "Top2000 Daily Snapshot": {
        "owner_surface": "Workspace > Overview bounded action facade",
        "target_surface": "Workspace > Overview > Market Movers > Top2000 > 일중 스냅샷 갱신",
        "collection_action": "Run the Top2000 intraday snapshot refresh from Market Movers.",
    },
    DATA_HEALTH_FUTURES_MACRO_1M_AREA: {
        "owner_surface": "Workspace > Ingestion",
        "target_surface": "Workspace > Ingestion > 일상 운영 / 검증 데이터 > 선물 OHLCV 수집",
        "alternate_surface": "Workspace > Overview > Futures Macro",
        "collection_action": "Run futures OHLCV collection; Overview bounded refresh is also available for Futures Macro.",
    },
    "Market Sentiment": {
        "owner_surface": "Workspace > Ingestion",
        "target_surface": "Workspace > Ingestion > 일상 운영 / 검증 데이터 > 시장 심리 수집",
        "alternate_surface": "Workspace > Overview > Sentiment",
        "collection_action": "Run Market Sentiment collection for CNN Fear & Greed / AAII rows.",
    },
    "FOMC Calendar": {
        "owner_surface": "Workspace > Ingestion",
        "target_surface": "Workspace > Ingestion > 일상 운영 / 검증 데이터 > 시장 이벤트 캘린더 수집 > FOMC 일정",
        "alternate_surface": "Workspace > Overview > Events",
        "collection_action": "Run FOMC calendar collection from the existing market events collector.",
    },
    "Macro Calendar": {
        "owner_surface": "Workspace > Ingestion",
        "target_surface": "Workspace > Ingestion > 일상 운영 / 검증 데이터 > 시장 이벤트 캘린더 수집 > 매크로 발표",
        "alternate_surface": "Workspace > Overview > Events",
        "collection_action": "Run official macro calendar collection or import the BLS .ics file.",
    },
    "Earnings Calendar": {
        "owner_surface": "Workspace > Ingestion",
        "target_surface": "Workspace > Ingestion > 일상 운영 / 검증 데이터 > 시장 이벤트 캘린더 수집 > 실적 발표",
        "alternate_surface": "Workspace > Overview > Events",
        "collection_action": "Run earnings calendar collection with a bounded symbol source.",
    },
}

DATA_HEALTH_HANDOFF_STATUS_ORDER = {
    "FAILED": 0,
    "MISSING": 1,
    "STALE": 2,
    "PARTIAL": 3,
    "DUE": 4,
    "REVIEW": 5,
}

DATA_HEALTH_HANDOFF_SEVERITY = {
    "FAILED": "critical",
    "MISSING": "critical",
    "STALE": "high",
    "PARTIAL": "high",
    "DUE": "medium",
    "REVIEW": "medium",
}

def _handoff_status(value: Any) -> str:
    status = str(value or "").strip()
    return status or "Unknown"

def _handoff_status_rank(status: Any) -> int:
    return DATA_HEALTH_HANDOFF_STATUS_ORDER.get(_handoff_status(status).upper(), 99)

def _handoff_counts(rows: pd.DataFrame) -> dict[str, int]:
    if rows.empty or "Status" not in rows:
        return {}
    counts = rows["Status"].fillna("Unknown").astype(str).value_counts().to_dict()
    return {str(key): int(value) for key, value in counts.items()}

def _handoff_reason(row: dict[str, Any]) -> str:
    parts = [
        _handoff_status(row.get("Status")),
        str(row.get("Data Freshness") or "-"),
    ]
    failure_streak = _cockpit_int(row.get("Failure Streak"))
    failed_count = _cockpit_int(row.get("Failed"))
    last_issue = row.get("Last Issue")
    if failure_streak:
        parts.append(f"Failure streak {failure_streak}")
    if failed_count:
        parts.append(f"{failed_count} failed")
    if last_issue not in (None, "", "-"):
        parts.append(f"Last issue {last_issue}")
    return " · ".join(parts)

def _handoff_target(area: str) -> dict[str, str]:
    target = dict(DATA_HEALTH_HANDOFF_TARGETS.get(normalize_overview_data_health_area(area)) or {})
    if target:
        return target
    return {
        "owner_surface": "Workspace > Ingestion",
        "target_surface": "Workspace > Ingestion > 일상 운영 / 검증 데이터",
        "collection_action": "Open the matching Ingestion collector and rerun a bounded collection.",
    }

def build_overview_data_health_ingestion_handoff(
    collection_ops_snapshot: dict[str, Any] | None = None,
    *,
    limit: int = 5,
) -> dict[str, Any]:
    """Turn Overview Data Health rows into read-only handoff guidance for the owning collection surfaces."""
    snapshot = collection_ops_snapshot or {}
    rows = _cockpit_frame(snapshot)
    counts = _handoff_counts(rows)
    if rows.empty:
        return {
            "schema_version": "overview_data_health_ingestion_handoff_v1",
            "status": "NO_DATA",
            "summary": {
                "headline": "No Data Health handoff available",
                "detail": str(snapshot.get("message") or "No collection ops rows are available yet."),
                "review_count": 0,
                "top_priority": None,
                "next_target_surface": None,
            },
            "counts": counts,
            "priority_items": [],
            "boundary_note": (
                "Read-only handoff: Overview Data Health does not execute collection jobs, write registries, "
                "write saved setup, change DB schema, or fetch providers during render."
            ),
        }

    review_rows = rows[
        ~rows.get("Status", pd.Series(dtype=str)).fillna("").astype(str).str.upper().isin({"OK", "SUCCESS"})
    ].copy()
    if review_rows.empty:
        return {
            "schema_version": "overview_data_health_ingestion_handoff_v1",
            "status": "OK",
            "summary": {
                "headline": "Data Health handoff clear",
                "detail": "All tracked Overview collection targets are currently OK.",
                "review_count": 0,
                "top_priority": None,
                "next_target_surface": None,
            },
            "counts": counts,
            "priority_items": [],
            "boundary_note": (
                "Read-only handoff: Overview Data Health does not execute collection jobs, write registries, "
                "write saved setup, change DB schema, or fetch providers during render."
            ),
        }

    review_rows["_status_rank"] = review_rows["Status"].map(_handoff_status_rank)
    if "Failure Streak" not in review_rows:
        review_rows["Failure Streak"] = 0
    review_rows["_failure_streak"] = review_rows["Failure Streak"].map(_cockpit_int)
    review_rows = review_rows.sort_values(
        by=["_status_rank", "_failure_streak", "Area"],
        ascending=[True, False, True],
        kind="mergesort",
    )

    priority_items: list[dict[str, Any]] = []
    for rank, (_, item_row) in enumerate(review_rows.head(max(1, int(limit or 5))).iterrows(), start=1):
        row = dict(item_row.drop(labels=["_status_rank", "_failure_streak"], errors="ignore").to_dict())
        area = normalize_overview_data_health_area(row.get("Area") or "Unknown")
        status = _handoff_status(row.get("Status"))
        target = _handoff_target(area)
        priority_items.append(
            {
                "rank": rank,
                "area": area,
                "scope": str(row.get("Scope") or _ops_area_scope(area)),
                "status": status,
                "severity": DATA_HEALTH_HANDOFF_SEVERITY.get(status.upper(), "low"),
                "tone": _cockpit_status_tone(status),
                "freshness": str(row.get("Data Freshness") or "-"),
                "reason": _handoff_reason(row),
                "next_action": str(row.get("Next Action") or target.get("collection_action") or "-"),
                "collection_action": target.get("collection_action") or str(row.get("Next Action") or "-"),
                "owner_surface": target.get("owner_surface") or "Workspace > Ingestion",
                "target_surface": target.get("target_surface") or "Workspace > Ingestion",
                "alternate_surface": target.get("alternate_surface"),
                "last_success": row.get("Last Success") or "-",
                "last_issue": row.get("Last Issue") or "-",
            }
        )

    review_count = int(len(review_rows))
    top_item = priority_items[0] if priority_items else {}
    return {
        "schema_version": "overview_data_health_ingestion_handoff_v1",
        "status": "REVIEW" if review_count else "OK",
        "summary": {
            "headline": f"{review_count} Data Health targets need handoff" if review_count else "Data Health handoff clear",
            "detail": (
                "Open the owning collection surface for the highest-priority stale, missing, partial, due, or failed target."
                if review_count
                else "All tracked Overview collection targets are currently OK."
            ),
            "review_count": review_count,
            "top_priority": top_item.get("area"),
            "next_target_surface": top_item.get("target_surface"),
        },
        "counts": counts,
        "priority_items": priority_items,
        "boundary_note": (
            "Read-only handoff: Overview Data Health does not execute collection jobs, write registries, "
            "write saved setup, change DB schema, or fetch providers during render."
        ),
    }

__all__ = [
    "DATA_HEALTH_FUTURES_MACRO_1M_AREA",
    "DATA_HEALTH_FUTURES_MACRO_DAILY_AREA",
    "build_collection_ops_snapshot",
    "build_overview_data_health_ingestion_handoff",
    "normalize_overview_data_health_area",
]
