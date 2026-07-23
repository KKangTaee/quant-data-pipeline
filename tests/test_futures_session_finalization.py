from __future__ import annotations

from datetime import datetime, timezone


def _bar(
    symbol: str,
    timestamp: str,
    **values: float | None,
) -> dict[str, object]:
    return {
        "provider_symbol": symbol,
        "candle_time_utc": timestamp,
        "open": values.get("open", 100.0),
        "high": values.get("high", 101.0),
        "low": values.get("low", 99.0),
        "close": values.get("close", 100.5),
        "volume": values.get("volume", 10.0),
    }


def test_edt_window_excludes_next_evening_session() -> None:
    from finance.data.futures_session_finalization import (
        build_session_finalization_batch,
    )

    rows = [
        _bar("ES=F", "2026-07-22 21:59:59", close=1.0),
        _bar("ES=F", "2026-07-22 22:00:00", open=100.0, close=100.5),
        _bar(
            "ES=F",
            "2026-07-23 20:55:00",
            high=110.0,
            low=95.0,
            close=108.0,
        ),
        _bar("ES=F", "2026-07-23 21:00:00", close=999.0),
        _bar("ES=F", "2026-07-23 22:00:00", close=777.0),
    ]

    batch = build_session_finalization_batch(
        rows,
        session_date="2026-07-23",
        daily_targets={"ES=F": "2026-07-23 00:00:00"},
        required_symbols=("ES=F",),
        finalized_at=datetime(2026, 7, 23, 22, 2, tzinfo=timezone.utc),
    )

    assert batch.missing_symbols == ()
    assert batch.window_start_utc.isoformat() == "2026-07-22T22:00:00+00:00"
    assert batch.window_end_utc.isoformat() == "2026-07-23T21:00:00+00:00"
    assert batch.rows[0]["final_open"] == 100.0
    assert batch.rows[0]["final_close"] == 108.0
    assert batch.rows[0]["final_high"] == 110.0
    assert batch.rows[0]["final_low"] == 95.0


def test_est_window_uses_new_york_timezone_rules() -> None:
    from finance.data.futures_session_finalization import (
        futures_session_window_utc,
    )

    start, end = futures_session_window_utc("2026-01-15")

    assert start.isoformat() == "2026-01-14T23:00:00+00:00"
    assert end.isoformat() == "2026-01-15T22:00:00+00:00"


def test_aggregate_sums_volume_and_uses_close_as_adjusted_close() -> None:
    from finance.data.futures_session_finalization import (
        FUTURES_SESSION_FINALIZATION_BASIS,
        build_session_finalization_batch,
    )

    batch = build_session_finalization_batch(
        [
            _bar("ES=F", "2026-07-22 22:00:00", volume=10.0, close=100.5),
            _bar("ES=F", "2026-07-23 20:55:00", volume=20.0, close=103.0),
        ],
        session_date="2026-07-23",
        daily_targets={"ES=F": "2026-07-23 00:00:00"},
        required_symbols=("ES=F",),
        finalized_at=datetime(2026, 7, 23, 22, 2, tzinfo=timezone.utc),
    )

    row = batch.rows[0]
    assert row["final_volume"] == 30.0
    assert row["final_adj_close"] == 103.0
    assert row["finalization_basis"] == FUTURES_SESSION_FINALIZATION_BASIS
    assert "yfinance:5m" in str(row["final_source_ref"])
    assert "2026-07-22T18:00:00-04:00" in str(row["final_source_ref"])
    assert "2026-07-23T17:00:00-04:00" in str(row["final_source_ref"])


def test_missing_symbol_blocks_batch_completeness() -> None:
    from finance.data.futures_session_finalization import (
        build_session_finalization_batch,
    )

    batch = build_session_finalization_batch(
        [_bar("ES=F", "2026-07-23 20:55:00", close=103.0)],
        session_date="2026-07-23",
        daily_targets={
            "ES=F": "2026-07-23 00:00:00",
            "NQ=F": "2026-07-23 00:00:00",
        },
        required_symbols=("ES=F", "NQ=F"),
        finalized_at=datetime(2026, 7, 23, 22, 2, tzinfo=timezone.utc),
    )

    assert batch.complete is False
    assert batch.missing_symbols == ("NQ=F",)
    assert [row["provider_symbol"] for row in batch.rows] == ["ES=F"]


def test_symbol_without_finite_close_is_missing() -> None:
    from finance.data.futures_session_finalization import (
        build_session_finalization_batch,
    )

    batch = build_session_finalization_batch(
        [_bar("ES=F", "2026-07-23 20:55:00", close=None)],
        session_date="2026-07-23",
        daily_targets={"ES=F": "2026-07-23 00:00:00"},
        required_symbols=("ES=F",),
        finalized_at=datetime(2026, 7, 23, 22, 2, tzinfo=timezone.utc),
    )

    assert batch.complete is False
    assert batch.rows == ()
    assert batch.missing_symbols == ("ES=F",)
