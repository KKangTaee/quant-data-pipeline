"""Resolve provider daily futures rows into conservative completed sessions."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Literal
from zoneinfo import ZoneInfo


FUTURES_DAILY_SESSION_VERSION = "futures_daily_session_v1"
FUTURES_DAILY_FINAL_CUTOFF_ET = time(18, 15)
NEW_YORK = ZoneInfo("America/New_York")


@dataclass(frozen=True)
class FuturesDailySession:
    provider_symbol: str
    raw_candle_date: str
    session_date: str | None
    status: Literal["FINAL", "IN_PROGRESS", "UNKNOWN"]
    reason: str


@dataclass(frozen=True)
class CompletedFuturesInput:
    rows: list[dict[str, object]]
    latest_final_session: str | None
    pending_session: str | None
    excluded_unknown_rows: int


def _datetime_value(value: object) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, time.min)
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def _utc_datetime(value: object) -> datetime | None:
    parsed = _datetime_value(value)
    if parsed is None:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _sort_datetime(value: object) -> datetime:
    return _utc_datetime(value) or datetime.min.replace(tzinfo=timezone.utc)


def futures_session_evaluation_token(evaluation_time: datetime) -> str:
    """Return the cache phase that can change completed-session eligibility."""

    evaluation = evaluation_time
    if evaluation.tzinfo is None:
        evaluation = evaluation.replace(tzinfo=timezone.utc)
    evaluation_et = evaluation.astimezone(NEW_YORK)
    phase = (
        "FINAL"
        if evaluation_et.time() >= FUTURES_DAILY_FINAL_CUTOFF_ET
        else "IN_PROGRESS"
    )
    return f"{evaluation_et.date().isoformat()}:{phase}"


def resolve_futures_daily_session(
    provider_symbol: str,
    candle_time_utc: object,
    collected_at: object,
    evaluation_time: datetime,
) -> FuturesDailySession:
    """Map one provider candle label to a canonical trade date and finality."""

    del collected_at
    candle = _utc_datetime(candle_time_utc)
    symbol = str(provider_symbol or "").strip().upper()
    if candle is None:
        return FuturesDailySession(symbol, "", None, "UNKNOWN", "invalid_provider_timestamp")
    raw_date = candle.date()
    if raw_date.weekday() == 5:
        return FuturesDailySession(
            symbol,
            raw_date.isoformat(),
            None,
            "UNKNOWN",
            "saturday_provider_label",
        )
    session_date = raw_date + timedelta(days=1) if raw_date.weekday() == 6 else raw_date
    evaluation = evaluation_time
    if evaluation.tzinfo is None:
        evaluation = evaluation.replace(tzinfo=timezone.utc)
    evaluation_et = evaluation.astimezone(NEW_YORK)
    if session_date < evaluation_et.date():
        status: Literal["FINAL", "IN_PROGRESS", "UNKNOWN"] = "FINAL"
        reason = "session_precedes_evaluation_date"
    elif session_date == evaluation_et.date() and evaluation_et.time() >= FUTURES_DAILY_FINAL_CUTOFF_ET:
        status = "FINAL"
        reason = "same_date_after_final_cutoff"
    else:
        status = "IN_PROGRESS"
        reason = "same_or_future_session_not_final"
    return FuturesDailySession(
        symbol,
        raw_date.isoformat(),
        session_date.isoformat(),
        status,
        reason,
    )


def select_completed_futures_daily_rows(
    rows: Sequence[dict[str, object]],
    *,
    evaluation_time: datetime,
) -> CompletedFuturesInput:
    """Return deduplicated final rows and compact pending/unknown evidence."""

    selected: dict[tuple[str, str], tuple[dict[str, object], FuturesDailySession]] = {}
    unknown_count = 0
    for raw in rows:
        row = dict(raw)
        resolved = resolve_futures_daily_session(
            str(row.get("provider_symbol") or ""),
            row.get("candle_time_utc"),
            row.get("collected_at"),
            evaluation_time,
        )
        if resolved.status == "UNKNOWN" or resolved.session_date is None:
            unknown_count += 1
            continue
        key = (resolved.provider_symbol, resolved.session_date)
        current = selected.get(key)
        candidate_sort = (
            _sort_datetime(row.get("candle_time_utc")),
            _sort_datetime(row.get("collected_at")),
        )
        if current is not None:
            current_row = current[0]
            current_sort = (
                _sort_datetime(current_row.get("candle_time_utc")),
                _sort_datetime(current_row.get("collected_at")),
            )
            if candidate_sort <= current_sort:
                continue
        selected[key] = (row, resolved)

    final_rows: list[dict[str, object]] = []
    final_dates: list[str] = []
    pending_dates: list[str] = []
    for (_, session_date), (row, resolved) in sorted(selected.items()):
        if resolved.status == "IN_PROGRESS":
            pending_dates.append(session_date)
            continue
        normalized = dict(row)
        normalized["provider_symbol"] = resolved.provider_symbol
        normalized["raw_candle_time_utc"] = row.get("candle_time_utc")
        normalized["candle_time_utc"] = f"{session_date} 00:00:00"
        normalized["Date"] = session_date
        normalized["session_status"] = resolved.status
        normalized["session_reason"] = resolved.reason
        final_rows.append(normalized)
        final_dates.append(session_date)
    return CompletedFuturesInput(
        rows=final_rows,
        latest_final_session=max(final_dates) if final_dates else None,
        pending_session=max(pending_dates) if pending_dates else None,
        excluded_unknown_rows=unknown_count,
    )
