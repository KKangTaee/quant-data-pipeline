"""DB-only point-in-time reader for official macro event schedules."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime, timezone
from typing import Any

from finance.data.db.mysql import MySQLClient


DB_META = "finance_meta"
TABLE = "market_event_calendar"
QueryFn = Callable[[str, str, tuple[Any, ...]], list[dict[str, Any]]]
OFFICIAL_AUTHORITIES = {
    "BLS",
    "BEA",
    "FEDERAL_RESERVE",
    "FED",
    "CENSUS",
}
OFFICIAL_SOURCES = {
    "federal_reserve_fomc_calendar",
    "bureau_labor_statistics",
    "bureau_economic_analysis",
    "census_bureau",
}


def _date_value(value: object) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value or "").strip()[:10])
    except ValueError:
        return None


def _datetime_value(value: object) -> datetime | None:
    if isinstance(value, datetime):
        parsed = value
    else:
        text = str(value or "").strip()
        if not text:
            return None
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _known_at_value(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _is_official(row: dict[str, object]) -> bool:
    if str(row.get("source_type") or "").strip().lower() == "official":
        return True
    authority = str(row.get("source_authority") or "").strip().upper()
    source = str(row.get("source") or "").strip().lower()
    return authority in OFFICIAL_AUTHORITIES or source in OFFICIAL_SOURCES


def _query(
    sql: str,
    params: tuple[Any, ...],
    *,
    query_fn: QueryFn | None,
) -> list[dict[str, Any]]:
    if query_fn is not None:
        return list(query_fn(DB_META, sql, params))
    db = MySQLClient("localhost", "root", "1234", 3306)
    try:
        db.use_db(DB_META)
        return db.query(sql, params)
    except Exception as exc:
        message = str(exc).lower()
        if TABLE in message and ("doesn't exist" in message or "unknown table" in message):
            return []
        raise
    finally:
        db.close()


def load_official_macro_event_history(
    *,
    start_date: str | date,
    end_date: str | date,
    known_at: datetime,
    query_fn: QueryFn | None = None,
) -> list[dict[str, object]]:
    """Return official, active schedule rows observable by one known-at cutoff."""

    start = _date_value(start_date)
    end = _date_value(end_date)
    if start is None or end is None or start > end:
        raise ValueError("start_date and end_date must form a valid ordered range")
    cutoff = _known_at_value(known_at)
    rows = _query(
        f"""
        SELECT event_key, event_date, event_type, event_family, event_subtype,
               event_datetime_utc, source_authority, source, source_type,
               event_status, collected_at
        FROM {TABLE}
        WHERE event_date >= %s
          AND event_date <= %s
          AND collected_at IS NOT NULL
          AND collected_at <= %s
          AND COALESCE(event_status, 'active') <> 'superseded'
        ORDER BY event_date ASC, event_type ASC, event_key ASC
        """,
        (start.isoformat(), end.isoformat(), cutoff.replace(tzinfo=None)),
        query_fn=query_fn,
    )
    eligible: list[dict[str, object]] = []
    for raw in rows:
        row = dict(raw)
        event_date = _date_value(row.get("event_date"))
        collected = _datetime_value(row.get("collected_at"))
        if event_date is None or collected is None:
            continue
        if not (start <= event_date <= end and collected <= cutoff):
            continue
        if str(row.get("event_status") or "active").lower() == "superseded":
            continue
        if not _is_official(row):
            continue
        event_type = str(row.get("event_type") or "").strip().upper()
        if not (event_type.startswith("MACRO_") or event_type == "FOMC_MEETING"):
            continue
        row["event_date"] = event_date.isoformat()
        row["collected_at"] = collected.isoformat()
        eligible.append(row)
    return sorted(
        eligible,
        key=lambda row: (
            str(row.get("event_date") or ""),
            str(row.get("event_type") or ""),
            str(row.get("event_key") or ""),
        ),
    )
