"""Bounded DB input assembly for the Futures Macro tab."""

from datetime import datetime, timedelta, timezone

from finance.loaders.futures import load_futures_intraday_rows, _query_futures_rows
from app.services.overview.events import build_market_events_snapshot
from app.services.futures_macro_windows import (
    SYMBOLS,
    build_cash_session_calendar,
    build_futures_macro_window_snapshot,
    utc,
)


def load_futures_macro_windows(*, evaluation_time=None, query_fn=None):
    now = utc(evaluation_time or datetime.now(timezone.utc))
    query = query_fn or _query_futures_rows
    years = sorted({(now - timedelta(days=16)).year, (now + timedelta(days=2)).year})
    events = [
        build_market_events_snapshot(
            start_date=f"{years[0]}-01-01",
            end_date=f"{years[-1]}-12-31",
            event_type=kind,
            recent_days=0,
            limit=100,
            today=now.date(),
            query_fn=query,
        )
        for kind in ("MARKET_HOLIDAY", "EARLY_CLOSE")
    ]
    try:
        coverage = query(
            "finance_meta",
            """SELECT coverage_key, coverage_status FROM market_event_collection_coverage
            WHERE coverage_key IN ("""
            + ",".join(["%s"] * len(years))
            + ")",
            [f"market_holiday:{year}" for year in years],
        )
    except Exception:
        coverage = []  # The one-hour price window remains usable without calendar storage.
    covered = {
        int(row["coverage_key"].split(":")[-1])
        for row in coverage
        if row["coverage_status"] == "complete"
    }
    statuses = {
        key: "OK"
        if item["status"] in {"OK", "NO_EVENTS"} and set(years).issubset(covered)
        else "LIMITED"
        for key, item in zip(("holiday", "early_close"), events)
    }
    calendar = build_cash_session_calendar(
        evaluation_time=now,
        holiday_rows=events[0].get("rows"),
        early_close_rows=events[1].get("rows"),
        calendar_statuses=statuses,
        covered_years=covered,
    )
    rows = load_futures_intraday_rows(
        SYMBOLS, start_utc=now - timedelta(days=16), end_utc=now, query_fn=query
    )
    return build_futures_macro_window_snapshot(
        rows=rows, evaluation_time=now, calendar=calendar
    )
