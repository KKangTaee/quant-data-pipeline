from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import pandas as pd

from finance.data.futures_market import DEFAULT_CORE_FUTURES_SYMBOLS


EVALUATED_AT = datetime(2026, 8, 10, 15, 17, tzinfo=UTC)
SESSION_START = datetime(2026, 8, 9, 22, 0, tzinfo=UTC)
COMMON_BAR_START = datetime(2026, 8, 10, 15, 5, tzinfo=UTC)


def _daily_rows(*, include_pending: bool = True) -> list[dict[str, Any]]:
    dates = pd.bdate_range(end="2026-08-07", periods=90)
    rows: list[dict[str, Any]] = []
    for symbol_index, symbol in enumerate(DEFAULT_CORE_FUTURES_SYMBOLS):
        price = 80.0 + symbol_index * 5.0
        for day_index, current_date in enumerate(dates):
            price *= 1.0 + 0.0015 * ((day_index + symbol_index) % 7 - 3)
            rows.append(
                {
                    "provider_symbol": symbol,
                    "interval_code": "1d",
                    "candle_time_utc": f"{current_date.date().isoformat()} 00:00:00",
                    "open": price * 0.998,
                    "high": price * 1.004,
                    "low": price * 0.996,
                    "close": price,
                    "adj_close": price,
                    "volume": 1000.0,
                    "source": "yfinance",
                    "provider_status": "ok",
                    "collected_at": "2026-08-08 00:00:00",
                }
            )
        if include_pending:
            rows.append(
                {
                    "provider_symbol": symbol,
                    "interval_code": "1d",
                    # yfinance can label the Sunday reopen as Sunday. It is the
                    # Monday trade session under the canonical session resolver.
                    "candle_time_utc": "2026-08-09 00:00:00",
                    "open": price,
                    "high": price * 1.01,
                    "low": price * 0.99,
                    "close": price * 1.005,
                    "adj_close": price * 1.005,
                    "volume": 500.0,
                    "source": "yfinance",
                    "provider_status": "ok",
                    "collected_at": "2026-08-10 15:15:00",
                }
            )
    return rows


def _intraday_rows(
    *,
    symbols: tuple[str, ...] = DEFAULT_CORE_FUTURES_SYMBOLS,
    lagging_symbol: str = "ES=F",
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for symbol_index, symbol in enumerate(symbols):
        base = 100.0 + symbol_index * 4.0
        starts = [SESSION_START, COMMON_BAR_START]
        if symbol != lagging_symbol:
            starts.append(COMMON_BAR_START + timedelta(minutes=5))
        # This bar is still open at 15:17 UTC and must never enter the reading.
        starts.append(COMMON_BAR_START + timedelta(minutes=10))
        for index, started_at in enumerate(starts):
            close = base * (1.0 + 0.003 * index)
            if started_at == COMMON_BAR_START + timedelta(minutes=10):
                close = base * 10.0
            rows.append(
                {
                    "provider_symbol": symbol,
                    "candle_time_utc": started_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "open": base,
                    "high": max(base, close) * 1.001,
                    "low": min(base, close) * 0.999,
                    "close": close,
                    "volume": 10.0 + index,
                    "collected_at": "2026-08-10 15:17:00",
                }
            )
    return rows


def _completed_pattern() -> dict[str, Any]:
    return {
        "status": "READY",
        "as_of_date": "2026-08-07",
        "summary": "마지막 완료 세션 관측",
        "families": {},
        "coverage": {
            "available_family_count": 6,
            "required_family_count": 6,
        },
    }


def _finalized_monday_daily_rows() -> list[dict[str, Any]]:
    from finance.data.futures_session_finalization import (
        FUTURES_SESSION_FINALIZATION_BASIS,
    )

    rows = _daily_rows()
    for row in rows:
        if row["candle_time_utc"] != "2026-08-09 00:00:00":
            continue
        for field in ("open", "high", "low", "close", "adj_close", "volume"):
            row[f"final_{field}"] = row[field]
        row["finalization_basis"] = FUTURES_SESSION_FINALIZATION_BASIS
        row["finalized_at"] = "2026-08-10 23:50:00"
    return rows


def _evening_reopen_rows() -> list[dict[str, Any]]:
    starts = (
        datetime(2026, 8, 10, 22, 0, tzinfo=UTC),
        datetime(2026, 8, 10, 23, 35, tzinfo=UTC),
        datetime(2026, 8, 10, 23, 40, tzinfo=UTC),
        datetime(2026, 8, 10, 23, 50, tzinfo=UTC),
    )
    rows: list[dict[str, Any]] = []
    for symbol_index, symbol in enumerate(DEFAULT_CORE_FUTURES_SYMBOLS):
        base = 100.0 + symbol_index * 4.0
        symbol_starts = starts if symbol != "ES=F" else (starts[0], starts[1], starts[3])
        for index, started_at in enumerate(symbol_starts):
            rows.append(
                {
                    "provider_symbol": symbol,
                    "candle_time_utc": started_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "open": base,
                    "high": base * (1.002 + index * 0.001),
                    "low": base * 0.998,
                    "close": base * (1.001 + index * 0.001),
                    "volume": 10.0,
                    "collected_at": "2026-08-10 23:52:00",
                }
            )
    return rows


def test_intraday_observation_uses_one_common_closed_bar_cutoff() -> None:
    from app.services.futures_macro_intraday import (
        build_futures_macro_intraday_observation,
    )

    result = build_futures_macro_intraday_observation(
        daily_rows=_daily_rows(),
        intraday_rows=_intraday_rows(),
        evaluation_time=EVALUATED_AT,
        completed_pattern=_completed_pattern(),
    )

    assert result["status"] == "INTRADAY_READY"
    assert result["observation_mode"] == "INTRADAY_PROVISIONAL"
    assert result["session_date"] == "2026-08-10"
    assert result["completed_as_of_date"] == "2026-08-07"
    assert result["observed_at_utc"] == "2026-08-10T15:10:00+00:00"
    assert result["freshness_minutes"] == 7
    assert result["available_family_count"] == 6
    assert result["pattern"]["as_of_date"] == "2026-08-10"
    assert result["pattern"]["status"] == "READY"


def test_intraday_observation_blanks_only_the_incomplete_family() -> None:
    from app.services.futures_macro_intraday import (
        build_futures_macro_intraday_observation,
    )

    symbols_without_gold = tuple(
        symbol for symbol in DEFAULT_CORE_FUTURES_SYMBOLS if symbol != "GC=F"
    )
    result = build_futures_macro_intraday_observation(
        daily_rows=_daily_rows(),
        intraday_rows=_intraday_rows(symbols=symbols_without_gold),
        evaluation_time=EVALUATED_AT,
        completed_pattern=_completed_pattern(),
    )

    assert result["status"] == "INTRADAY_PARTIAL"
    assert result["available_family_count"] == 5
    assert result["pattern"]["status"] == "PARTIAL"
    assert result["pattern"]["families"]["safe_haven"]["status"] == "UNAVAILABLE"
    assert result["pattern"]["families"]["risk_on"]["status"] == "READY"


def test_intraday_observation_falls_back_below_four_complete_families() -> None:
    from app.services.futures_macro_intraday import (
        build_futures_macro_intraday_observation,
    )

    only_three_families = (
        "ES=F",
        "NQ=F",
        "YM=F",
        "RTY=F",
        "ZN=F",
        "ZB=F",
        "6E=F",
        "6J=F",
        "6B=F",
        "6A=F",
        "6C=F",
    )
    result = build_futures_macro_intraday_observation(
        daily_rows=_daily_rows(),
        intraday_rows=_intraday_rows(symbols=only_three_families),
        evaluation_time=EVALUATED_AT,
        completed_pattern=_completed_pattern(),
    )

    assert result["status"] == "COMPLETED_FALLBACK"
    assert result["observation_mode"] == "COMPLETED"
    assert result["pattern"] == _completed_pattern()
    assert result["fallback_reason"] == "insufficient_complete_families"


def test_intraday_observation_falls_back_when_common_bar_is_stale() -> None:
    from app.services.futures_macro_intraday import (
        build_futures_macro_intraday_observation,
    )

    result = build_futures_macro_intraday_observation(
        daily_rows=_daily_rows(),
        intraday_rows=_intraday_rows(),
        evaluation_time=datetime(2026, 8, 10, 16, 0, tzinfo=UTC),
        completed_pattern=_completed_pattern(),
    )

    assert result["status"] == "COMPLETED_FALLBACK"
    assert result["pattern"] == _completed_pattern()
    assert result["fallback_reason"] == "stale_intraday_bars"


def test_evening_reopen_uses_next_trade_session_without_a_pending_daily_label() -> None:
    from app.services.futures_macro_intraday import (
        build_futures_macro_intraday_observation,
    )

    result = build_futures_macro_intraday_observation(
        daily_rows=_finalized_monday_daily_rows(),
        intraday_rows=_evening_reopen_rows(),
        evaluation_time=datetime(2026, 8, 10, 23, 52, tzinfo=UTC),
        completed_pattern=_completed_pattern(),
    )

    assert result["status"] == "INTRADAY_READY"
    assert result["session_date"] == "2026-08-11"
    assert result["completed_as_of_date"] == "2026-08-10"
    assert result["observed_at_utc"] == "2026-08-10T23:40:00+00:00"
    assert result["pattern"]["as_of_date"] == "2026-08-11"


def test_evening_reopen_fails_closed_when_prior_pending_daily_is_unresolved() -> None:
    from app.services.futures_macro_intraday import (
        build_futures_macro_intraday_observation,
    )

    result = build_futures_macro_intraday_observation(
        daily_rows=_daily_rows(),
        intraday_rows=_evening_reopen_rows(),
        evaluation_time=datetime(2026, 8, 10, 23, 52, tzinfo=UTC),
        completed_pattern=_completed_pattern(),
    )

    assert result["status"] == "COMPLETED_FALLBACK"
    assert result["fallback_reason"] == "prior_session_not_finalized"


def test_loader_does_not_read_intraday_rows_without_a_pending_session() -> None:
    from app.services.futures_macro_intraday import (
        load_overview_futures_macro_intraday_observation,
    )

    calls = {"intraday": 0}

    def daily_loader(query_fn, *, symbols, lookback_days):
        del query_fn, symbols, lookback_days
        return _daily_rows(include_pending=False)

    def intraday_loader(*args, **kwargs):
        del args, kwargs
        calls["intraday"] += 1
        raise AssertionError("completed-only mode must not query intraday rows")

    result = load_overview_futures_macro_intraday_observation(
        completed_pattern=_completed_pattern(),
        evaluation_time=datetime(2026, 8, 10, 21, 30, tzinfo=UTC),
        daily_rows_loader=daily_loader,
        intraday_rows_loader=intraday_loader,
        query_fn=lambda *_args, **_kwargs: [],
    )

    assert calls["intraday"] == 0
    assert result["status"] == "COMPLETED_FALLBACK"
    assert result["fallback_reason"] == "no_active_session"
    assert result["pattern"] == _completed_pattern()
