from __future__ import annotations

from datetime import datetime, timezone

import pytest


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


def _complete_batch(
    symbols: tuple[str, ...] = ("ES=F", "NQ=F"),
):
    from finance.data.futures_session_finalization import (
        build_session_finalization_batch,
    )

    return build_session_finalization_batch(
        [
            _bar(symbol, "2026-07-23 20:55:00", close=101.0)
            for symbol in symbols
        ],
        session_date="2026-07-23",
        daily_targets={
            symbol: "2026-07-23 00:00:00"
            for symbol in symbols
        },
        required_symbols=symbols,
        finalized_at=datetime(2026, 7, 23, 22, 2, tzinfo=timezone.utc),
    )


class FakeDB:
    def __init__(
        self,
        *,
        query_rows: list[dict[str, object]] | None = None,
        fail_executemany: bool = False,
    ) -> None:
        self.events: list[str] = []
        self.queries: list[tuple[str, object]] = []
        self.query_rows = list(query_rows or [])
        self.fail_executemany = fail_executemany

    def use_db(self, _database: str) -> None:
        self.events.append("use_db")

    def query(self, sql: str, params: object = None) -> list[dict[str, object]]:
        self.queries.append((sql, params))
        return list(self.query_rows)

    def begin(self) -> None:
        self.events.append("begin")

    def executemany(self, _sql: str, rows: list[dict[str, object]]) -> None:
        self.events.append(f"executemany:{len(rows)}")
        if self.fail_executemany:
            raise RuntimeError("write failed")

    def commit(self) -> None:
        self.events.append("commit")

    def rollback(self) -> None:
        self.events.append("rollback")

    def close(self) -> None:
        self.events.append("close")


def test_futures_ohlcv_schema_has_additive_finalization_columns() -> None:
    from finance.data.db.schema import FUTURES_MARKET_SCHEMAS

    schema = FUTURES_MARKET_SCHEMAS["futures_ohlcv"]

    for token in (
        "final_open DOUBLE NULL",
        "final_high DOUBLE NULL",
        "final_low DOUBLE NULL",
        "final_close DOUBLE NULL",
        "final_adj_close DOUBLE NULL",
        "final_volume DOUBLE NULL",
        "finalization_basis VARCHAR(64) NULL",
        "final_source_ref VARCHAR(255) NULL",
        "finalized_at TIMESTAMP NULL",
    ):
        assert token in schema


def test_regular_futures_upsert_does_not_clear_finalization(monkeypatch) -> None:
    from finance.data import futures_market

    fake = FakeDB()
    captured_sql: list[str] = []

    def executemany(sql: str, rows: list[dict[str, object]]) -> None:
        captured_sql.append(sql)
        fake.events.append(f"executemany:{len(rows)}")

    fake.executemany = executemany  # type: ignore[method-assign]
    monkeypatch.setattr(futures_market, "_db", lambda *_args, **_kwargs: fake)
    monkeypatch.setattr(
        futures_market,
        "sync_table_schema",
        lambda *_args, **_kwargs: None,
    )

    futures_market.upsert_futures_ohlcv_rows(
        [
            {
                "provider_symbol": "ES=F",
                "interval_code": "1d",
                "candle_time_utc": "2026-07-23 00:00:00",
                "source": "yfinance",
                "source_ref": "yfinance:ES=F:1d",
                "open": 100.0,
                "high": 102.0,
                "low": 99.0,
                "close": 101.0,
                "adj_close": 101.0,
                "volume": 10.0,
                "provider_status": "ok",
                "collected_at": "2026-07-23 22:02:00",
                "error_msg": None,
            }
        ]
    )

    update_clause = captured_sql[0].split("ON DUPLICATE KEY UPDATE", 1)[1]
    assert "final_open" not in update_clause
    assert "final_close" not in update_clause
    assert "finalization_basis" not in update_clause
    assert "finalized_at" not in update_clause


def test_latest_daily_reader_uses_compact_grouped_query(monkeypatch) -> None:
    from finance.data import futures_session_finalization as finalization

    fake = FakeDB(query_rows=[{"provider_symbol": "ES=F"}])
    monkeypatch.setattr(finalization, "_db", lambda *_args, **_kwargs: fake)

    rows = finalization.load_latest_futures_daily_rows(("ES=F", "NQ=F"))

    sql, params = fake.queries[0]
    assert rows == [{"provider_symbol": "ES=F"}]
    assert "MAX(candle_time_utc)" in sql
    assert "final_close" in sql
    assert "interval_code = %s" in sql
    assert params == ["1d", "yfinance", "ES=F", "NQ=F"]
    assert fake.events == ["use_db", "close"]


def test_intraday_reader_uses_half_open_five_minute_window(monkeypatch) -> None:
    from finance.data import futures_session_finalization as finalization

    fake = FakeDB()
    monkeypatch.setattr(finalization, "_db", lambda *_args, **_kwargs: fake)
    start = datetime(2026, 7, 22, 22, 0, tzinfo=timezone.utc)
    end = datetime(2026, 7, 23, 21, 0, tzinfo=timezone.utc)

    finalization.load_stored_futures_intraday_rows(
        ("ES=F", "NQ=F"),
        start_utc=start,
        end_utc=end,
    )

    sql, params = fake.queries[0]
    assert "candle_time_utc >= %s" in sql
    assert "candle_time_utc < %s" in sql
    assert params == [
        "5m",
        "yfinance",
        "ES=F",
        "NQ=F",
        "2026-07-22 22:00:00",
        "2026-07-23 21:00:00",
    ]


def test_write_finalization_commits_only_complete_required_set(monkeypatch) -> None:
    from finance.data import futures_session_finalization as finalization

    fake = FakeDB()
    monkeypatch.setattr(finalization, "_db", lambda *_args, **_kwargs: fake)
    monkeypatch.setattr(
        finalization,
        "sync_table_schema",
        lambda *_args, **_kwargs: fake.events.append("sync"),
    )

    written = finalization.write_futures_daily_finalization(
        _complete_batch(),
        required_symbols=("ES=F", "NQ=F"),
    )

    assert written == 2
    assert fake.events == [
        "use_db",
        "sync",
        "begin",
        "executemany:2",
        "commit",
        "close",
    ]


def test_write_finalization_rejects_incomplete_batch_without_begin(
    monkeypatch,
) -> None:
    from finance.data import futures_session_finalization as finalization

    batch = finalization.build_session_finalization_batch(
        [_bar("ES=F", "2026-07-23 20:55:00", close=101.0)],
        session_date="2026-07-23",
        daily_targets={
            "ES=F": "2026-07-23 00:00:00",
            "NQ=F": "2026-07-23 00:00:00",
        },
        required_symbols=("ES=F", "NQ=F"),
        finalized_at=datetime(2026, 7, 23, 22, 2, tzinfo=timezone.utc),
    )
    fake = FakeDB()
    monkeypatch.setattr(finalization, "_db", lambda *_args, **_kwargs: fake)

    written = finalization.write_futures_daily_finalization(
        batch,
        required_symbols=("ES=F", "NQ=F"),
    )

    assert written == 0
    assert fake.events == []


def test_write_finalization_rolls_back_on_update_error(monkeypatch) -> None:
    from finance.data import futures_session_finalization as finalization

    fake = FakeDB(fail_executemany=True)
    monkeypatch.setattr(finalization, "_db", lambda *_args, **_kwargs: fake)
    monkeypatch.setattr(
        finalization,
        "sync_table_schema",
        lambda *_args, **_kwargs: fake.events.append("sync"),
    )

    with pytest.raises(RuntimeError, match="write failed"):
        finalization.write_futures_daily_finalization(
            _complete_batch(),
            required_symbols=("ES=F", "NQ=F"),
        )

    assert "rollback" in fake.events
    assert "commit" not in fake.events
    assert fake.events[-1] == "close"
