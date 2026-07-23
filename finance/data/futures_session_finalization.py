"""Build and persist completed futures sessions from stored intraday rows."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
import math
from typing import Any
from zoneinfo import ZoneInfo


FUTURES_SESSION_FINALIZATION_BASIS = "yfinance_5m_session_aggregate_v1"
NEW_YORK = ZoneInfo("America/New_York")


@dataclass(frozen=True)
class SessionFinalizationBatch:
    session_date: str
    window_start_utc: datetime
    window_end_utc: datetime
    rows: tuple[dict[str, object], ...]
    missing_symbols: tuple[str, ...]

    @property
    def complete(self) -> bool:
        return not self.missing_symbols


def _date_value(value: str | date) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value).strip())


def _utc_datetime(value: object) -> datetime | None:
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


def _finite_float(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def futures_session_window_utc(
    session_date: str | date,
) -> tuple[datetime, datetime]:
    """Return the completed futures session as a half-open UTC window."""

    session_day = _date_value(session_date)
    start_et = datetime.combine(
        session_day - timedelta(days=1),
        time(18, 0),
        tzinfo=NEW_YORK,
    )
    end_et = datetime.combine(
        session_day,
        time(17, 0),
        tzinfo=NEW_YORK,
    )
    return (
        start_et.astimezone(timezone.utc),
        end_et.astimezone(timezone.utc),
    )


def _first_finite(
    rows: Sequence[dict[str, Any]],
    field: str,
) -> float | None:
    for row in rows:
        value = _finite_float(row.get(field))
        if value is not None:
            return value
    return None


def _last_finite(
    rows: Sequence[dict[str, Any]],
    field: str,
) -> float | None:
    for row in reversed(rows):
        value = _finite_float(row.get(field))
        if value is not None:
            return value
    return None


def build_session_finalization_batch(
    intraday_rows: Sequence[dict[str, Any]],
    *,
    session_date: str | date,
    daily_targets: Mapping[str, object],
    required_symbols: Sequence[str],
    finalized_at: datetime,
) -> SessionFinalizationBatch:
    """Aggregate stored 5m rows without allowing the next evening session."""

    session_day = _date_value(session_date)
    start_utc, end_utc = futures_session_window_utc(session_day)
    start_et = start_utc.astimezone(NEW_YORK)
    end_et = end_utc.astimezone(NEW_YORK)
    source_ref = (
        f"yfinance:5m:[{start_et.isoformat()},{end_et.isoformat()})"
    )
    finalized_utc = _utc_datetime(finalized_at)
    if finalized_utc is None:
        raise ValueError("finalized_at must be a valid datetime")
    finalized_text = finalized_utc.replace(tzinfo=None).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    required = tuple(
        dict.fromkeys(
            str(symbol).strip().upper()
            for symbol in required_symbols
            if str(symbol).strip()
        )
    )
    targets = {
        str(symbol).strip().upper(): target
        for symbol, target in daily_targets.items()
        if str(symbol).strip()
    }
    grouped: dict[str, list[tuple[datetime, dict[str, Any]]]] = {
        symbol: [] for symbol in required
    }
    for raw in intraday_rows:
        row = dict(raw)
        symbol = str(row.get("provider_symbol") or "").strip().upper()
        if symbol not in grouped:
            continue
        timestamp = _utc_datetime(row.get("candle_time_utc"))
        if timestamp is None or timestamp < start_utc or timestamp >= end_utc:
            continue
        grouped[symbol].append((timestamp, row))

    aggregates: list[dict[str, object]] = []
    missing: list[str] = []
    for symbol in required:
        target = targets.get(symbol)
        timed_rows = sorted(grouped[symbol], key=lambda item: item[0])
        rows = [row for _, row in timed_rows]
        close = _last_finite(rows, "close")
        if target is None or not rows or close is None:
            missing.append(symbol)
            continue
        highs = [
            value
            for row in rows
            if (value := _finite_float(row.get("high"))) is not None
        ]
        lows = [
            value
            for row in rows
            if (value := _finite_float(row.get("low"))) is not None
        ]
        volumes = [
            value
            for row in rows
            if (value := _finite_float(row.get("volume"))) is not None
        ]
        aggregates.append(
            {
                "provider_symbol": symbol,
                "daily_candle_time_utc": target,
                "source": "yfinance",
                "final_open": _first_finite(rows, "open"),
                "final_high": max(highs) if highs else None,
                "final_low": min(lows) if lows else None,
                "final_close": close,
                "final_adj_close": close,
                "final_volume": sum(volumes) if volumes else None,
                "finalization_basis": FUTURES_SESSION_FINALIZATION_BASIS,
                "final_source_ref": source_ref,
                "finalized_at": finalized_text,
            }
        )

    return SessionFinalizationBatch(
        session_date=session_day.isoformat(),
        window_start_utc=start_utc,
        window_end_utc=end_utc,
        rows=tuple(aggregates),
        missing_symbols=tuple(missing),
    )
