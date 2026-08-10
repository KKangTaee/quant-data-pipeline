"""Build a provisional Futures Macro reading from already stored 5-minute bars."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime, timedelta
import math
from typing import Any

import pandas as pd

from app.services.futures_macro_daily_loader import load_futures_macro_daily_rows
from app.services.futures_macro_pattern import (
    PATTERN_FAMILY_KEYS,
    PATTERN_FEATURE_SUFFIXES,
    SCORE_TO_FAMILY_KEY,
    build_current_pattern_snapshot,
    build_pattern_feature_frame,
)
from app.services.futures_macro_sessions import (
    NEW_YORK,
    select_completed_futures_daily_rows,
)
from app.services.futures_macro_thermometer import (
    SCORE_DEFINITIONS,
    _default_query,
    normalize_futures_macro_daily_candles,
)
from finance.data.futures_market import DEFAULT_CORE_FUTURES_SYMBOLS
from finance.data.futures_session_finalization import (
    futures_session_window_utc,
    load_stored_futures_intraday_rows,
)


QueryFn = Callable[
    [str, str, Sequence[Any] | None],
    list[dict[str, Any]],
]
DailyRowsLoader = Callable[..., list[dict[str, Any]]]
IntradayRowsLoader = Callable[..., list[dict[str, Any]]]

INTRADAY_BAR_MINUTES = 5
INTRADAY_FRESHNESS_LIMIT_MINUTES = 30
INTRADAY_MIN_FAMILIES = 4
INTRADAY_DAILY_LOOKBACK_DAYS = 420


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
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _finite_float(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _normalized_symbols(symbols: Sequence[str]) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            str(symbol).strip().upper()
            for symbol in symbols
            if str(symbol).strip()
        )
    )


def _completed_pattern(
    completed_rows: Sequence[dict[str, Any]],
    supplied: Mapping[str, Any] | None,
    *,
    selected_symbols: Sequence[str],
) -> dict[str, Any]:
    if supplied is not None:
        return dict(supplied)
    candles = normalize_futures_macro_daily_candles(completed_rows)
    features = build_pattern_feature_frame(
        candles,
        selected_symbols=selected_symbols,
    )
    return build_current_pattern_snapshot(features)


def _fallback(
    *,
    pattern: Mapping[str, Any],
    session_date: str | None,
    completed_as_of_date: str | None,
    reason: str,
    available_family_count: int = 0,
    freshness_minutes: int | None = None,
) -> dict[str, Any]:
    return {
        "status": "COMPLETED_FALLBACK",
        "observation_mode": "COMPLETED",
        "pattern": dict(pattern),
        "session_date": session_date or completed_as_of_date,
        "completed_as_of_date": completed_as_of_date,
        "observed_at_utc": None,
        "observed_at_et": None,
        "freshness_minutes": freshness_minutes,
        "available_family_count": int(available_family_count),
        "required_family_count": len(PATTERN_FAMILY_KEYS),
        "fallback_reason": reason,
    }


def _closed_session_rows(
    rows: Sequence[dict[str, Any]],
    *,
    selected_symbols: Sequence[str],
    session_start: datetime,
    session_end: datetime,
    evaluation_time: datetime,
) -> list[tuple[datetime, dict[str, Any]]]:
    selected = set(selected_symbols)
    bar_width = timedelta(minutes=INTRADAY_BAR_MINUTES)
    closed: list[tuple[datetime, dict[str, Any]]] = []
    for raw in rows:
        row = dict(raw)
        symbol = str(row.get("provider_symbol") or "").strip().upper()
        started_at = _utc_datetime(row.get("candle_time_utc"))
        if (
            symbol not in selected
            or started_at is None
            or started_at < session_start
            or started_at >= session_end
            or started_at + bar_width > evaluation_time
        ):
            continue
        row["provider_symbol"] = symbol
        closed.append((started_at, row))
    return closed


def _eligible_families(
    latest_bar_by_symbol: Mapping[str, datetime],
) -> dict[str, tuple[str, ...]]:
    eligible: dict[str, tuple[str, ...]] = {}
    for definition in SCORE_DEFINITIONS:
        members = tuple(definition.members)
        if all(symbol in latest_bar_by_symbol for symbol in members):
            eligible[SCORE_TO_FAMILY_KEY[definition.name]] = members
    return eligible


def _aggregate_intraday_rows(
    rows: Sequence[tuple[datetime, dict[str, Any]]],
    *,
    selected_symbols: Sequence[str],
    common_bar_start: datetime,
    session_date: str,
    evaluation_time: datetime,
) -> list[dict[str, Any]]:
    grouped: dict[str, list[tuple[datetime, dict[str, Any]]]] = {
        symbol: [] for symbol in selected_symbols
    }
    for started_at, row in rows:
        symbol = str(row.get("provider_symbol") or "").strip().upper()
        if symbol in grouped and started_at <= common_bar_start:
            grouped[symbol].append((started_at, row))

    aggregates: list[dict[str, Any]] = []
    for symbol in selected_symbols:
        timed = sorted(grouped[symbol], key=lambda item: item[0])
        if not timed:
            continue
        values = [row for _, row in timed]
        close = next(
            (
                value
                for row in reversed(values)
                if (value := _finite_float(row.get("close"))) is not None
            ),
            None,
        )
        if close is None:
            continue
        open_value = next(
            (
                value
                for row in values
                if (value := _finite_float(row.get("open"))) is not None
            ),
            close,
        )
        highs = [
            value
            for row in values
            if (value := _finite_float(row.get("high"))) is not None
        ]
        lows = [
            value
            for row in values
            if (value := _finite_float(row.get("low"))) is not None
        ]
        volumes = [
            value
            for row in values
            if (value := _finite_float(row.get("volume"))) is not None
        ]
        aggregates.append(
            {
                "provider_symbol": symbol,
                "interval_code": "1d",
                "candle_time_utc": f"{session_date} 00:00:00",
                "open": open_value,
                "high": max(highs) if highs else close,
                "low": min(lows) if lows else close,
                "close": close,
                "adj_close": close,
                "volume": sum(volumes) if volumes else None,
                "source": "stored_intraday_5m",
                "provider_status": "provisional",
                "collected_at": evaluation_time.isoformat(),
            }
        )
    return aggregates


def build_futures_macro_intraday_observation(
    *,
    daily_rows: Sequence[dict[str, Any]],
    intraday_rows: Sequence[dict[str, Any]],
    evaluation_time: datetime,
    completed_pattern: Mapping[str, Any] | None = None,
    selected_symbols: Sequence[str] = DEFAULT_CORE_FUTURES_SYMBOLS,
    freshness_limit_minutes: int = INTRADAY_FRESHNESS_LIMIT_MINUTES,
) -> dict[str, Any]:
    """Return a provisional current reading without mutating completed history."""

    evaluated_at = _utc_datetime(evaluation_time)
    if evaluated_at is None:
        raise ValueError("evaluation_time must be a valid datetime")
    selected = _normalized_symbols(selected_symbols)
    completed = select_completed_futures_daily_rows(
        daily_rows,
        evaluation_time=evaluated_at,
    )
    stable_pattern = _completed_pattern(
        completed.rows,
        completed_pattern,
        selected_symbols=selected,
    )
    if completed.pending_session is None:
        return _fallback(
            pattern=stable_pattern,
            session_date=None,
            completed_as_of_date=completed.latest_final_session,
            reason="no_pending_session",
        )

    session_start, session_end = futures_session_window_utc(
        completed.pending_session
    )
    closed_rows = _closed_session_rows(
        intraday_rows,
        selected_symbols=selected,
        session_start=session_start,
        session_end=session_end,
        evaluation_time=evaluated_at,
    )
    latest_by_symbol: dict[str, datetime] = {}
    for started_at, row in closed_rows:
        symbol = str(row.get("provider_symbol") or "").strip().upper()
        current = latest_by_symbol.get(symbol)
        if current is None or started_at > current:
            latest_by_symbol[symbol] = started_at
    eligible_families = _eligible_families(latest_by_symbol)
    available_family_count = len(eligible_families)
    if available_family_count < INTRADAY_MIN_FAMILIES:
        return _fallback(
            pattern=stable_pattern,
            session_date=completed.pending_session,
            completed_as_of_date=completed.latest_final_session,
            reason="insufficient_complete_families",
            available_family_count=available_family_count,
        )

    common_symbols = {
        symbol
        for members in eligible_families.values()
        for symbol in members
    }
    common_bar_start = min(latest_by_symbol[symbol] for symbol in common_symbols)
    observed_at = common_bar_start + timedelta(minutes=INTRADAY_BAR_MINUTES)
    freshness_minutes = max(
        0,
        int((evaluated_at - observed_at).total_seconds() // 60),
    )
    if freshness_minutes > max(0, int(freshness_limit_minutes)):
        return _fallback(
            pattern=stable_pattern,
            session_date=completed.pending_session,
            completed_as_of_date=completed.latest_final_session,
            reason="stale_intraday_bars",
            available_family_count=available_family_count,
            freshness_minutes=freshness_minutes,
        )

    aggregates = _aggregate_intraday_rows(
        closed_rows,
        selected_symbols=selected,
        common_bar_start=common_bar_start,
        session_date=completed.pending_session,
        evaluation_time=evaluated_at,
    )
    candles = normalize_futures_macro_daily_candles(
        [*completed.rows, *aggregates]
    )
    features = build_pattern_feature_frame(
        candles,
        selected_symbols=selected,
    )
    if features.empty:
        return _fallback(
            pattern=stable_pattern,
            session_date=completed.pending_session,
            completed_as_of_date=completed.latest_final_session,
            reason="insufficient_daily_history",
            available_family_count=available_family_count,
            freshness_minutes=freshness_minutes,
        )

    missing_families = set(PATTERN_FAMILY_KEYS) - set(eligible_families)
    latest_index = features.index[-1]
    for family in missing_families:
        for suffix in PATTERN_FEATURE_SUFFIXES:
            features.loc[latest_index, f"{family}__{suffix}"] = pd.NA
    pattern = build_current_pattern_snapshot(features)
    if pattern.get("status") == "UNAVAILABLE":
        return _fallback(
            pattern=stable_pattern,
            session_date=completed.pending_session,
            completed_as_of_date=completed.latest_final_session,
            reason="insufficient_intraday_pattern",
            available_family_count=available_family_count,
            freshness_minutes=freshness_minutes,
        )

    status = (
        "INTRADAY_READY"
        if available_family_count == len(PATTERN_FAMILY_KEYS)
        else "INTRADAY_PARTIAL"
    )
    return {
        "status": status,
        "observation_mode": "INTRADAY_PROVISIONAL",
        "pattern": pattern,
        "session_date": completed.pending_session,
        "completed_as_of_date": completed.latest_final_session,
        "observed_at_utc": observed_at.isoformat(),
        "observed_at_et": observed_at.astimezone(NEW_YORK).isoformat(),
        "freshness_minutes": freshness_minutes,
        "available_family_count": available_family_count,
        "required_family_count": len(PATTERN_FAMILY_KEYS),
        "fallback_reason": None,
    }


def load_overview_futures_macro_intraday_observation(
    *,
    completed_pattern: Mapping[str, Any] | None,
    evaluation_time: datetime | None = None,
    selected_symbols: Sequence[str] = DEFAULT_CORE_FUTURES_SYMBOLS,
    daily_rows_loader: DailyRowsLoader = load_futures_macro_daily_rows,
    intraday_rows_loader: IntradayRowsLoader = load_stored_futures_intraday_rows,
    query_fn: QueryFn | None = None,
) -> dict[str, Any]:
    """Load DB evidence only; provider collection and persistence stay in jobs."""

    evaluated_at = _utc_datetime(evaluation_time or datetime.now(UTC))
    if evaluated_at is None:
        raise ValueError("evaluation_time must be a valid datetime")
    selected = _normalized_symbols(selected_symbols)
    rows = daily_rows_loader(
        query_fn or _default_query,
        symbols=selected,
        lookback_days=INTRADAY_DAILY_LOOKBACK_DAYS,
    )
    completed = select_completed_futures_daily_rows(
        rows,
        evaluation_time=evaluated_at,
    )
    stable_pattern = _completed_pattern(
        completed.rows,
        completed_pattern,
        selected_symbols=selected,
    )
    if completed.pending_session is None:
        return _fallback(
            pattern=stable_pattern,
            session_date=None,
            completed_as_of_date=completed.latest_final_session,
            reason="no_pending_session",
        )
    session_start, session_end = futures_session_window_utc(
        completed.pending_session
    )
    intraday_rows = intraday_rows_loader(
        selected,
        start_utc=session_start,
        end_utc=session_end,
        interval_code="5m",
    )
    return build_futures_macro_intraday_observation(
        daily_rows=rows,
        intraday_rows=intraday_rows,
        evaluation_time=evaluated_at,
        completed_pattern=stable_pattern,
        selected_symbols=selected,
    )
