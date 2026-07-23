from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from finance.data.futures_market import DEFAULT_CORE_FUTURES_SYMBOLS


def _coverage(*, deficient: str | None = None) -> list[dict[str, Any]]:
    return [
        {
            "provider_symbol": symbol,
            "daily_row_count": 100 if symbol == deficient else 1_200,
            "first_daily_candle": "2021-01-01",
            "latest_daily_candle": "2026-07-22",
        }
        for symbol in DEFAULT_CORE_FUTURES_SYMBOLS
    ]


def _collection_result(symbols: list[str], *, failed: list[str] | None = None) -> dict[str, Any]:
    failures = list(failed or [])
    processed = len(symbols) - len(failures)
    return {
        "job_name": "collect_futures_ohlcv",
        "status": "partial_success" if failures else "success",
        "started_at": "2026-07-23 10:00:00",
        "finished_at": "2026-07-23 10:00:01",
        "duration_sec": 1.0,
        "rows_written": processed * 250,
        "symbols_requested": len(symbols),
        "symbols_processed": processed,
        "failed_symbols": failures,
        "message": "collected",
        "details": {
            "diagnostics": {
                "download_normalize_duration_sec": 0.6,
                "upsert_duration_sec": 0.2,
            }
        },
    }


def _finalization_not_required(**_kwargs: Any) -> dict[str, Any]:
    return {
        "status": "not_required",
        "session_date": None,
        "symbols_required": len(DEFAULT_CORE_FUTURES_SYMBOLS),
        "symbols_finalized": 0,
        "missing_symbols": [],
        "reason": "test_no_pending_session",
    }


def test_complete_core_symbols_use_one_year_overlap() -> None:
    from app.jobs.overview_actions import build_futures_macro_daily_refresh_plan

    plan = build_futures_macro_daily_refresh_plan(_coverage())

    assert plan["routine_symbols"] == list(DEFAULT_CORE_FUTURES_SYMBOLS)
    assert plan["bootstrap_symbols"] == []
    assert plan["routine_period"] == "1y"
    assert plan["bootstrap_period"] == "10y"


def test_only_deficient_symbol_gets_ten_year_bootstrap() -> None:
    from app.jobs.overview_actions import build_futures_macro_daily_refresh_plan

    plan = build_futures_macro_daily_refresh_plan(_coverage(deficient="SI=F"))

    assert plan["bootstrap_symbols"] == ["SI=F"]
    assert "SI=F" not in plan["routine_symbols"]
    assert len(plan["routine_symbols"]) == len(DEFAULT_CORE_FUTURES_SYMBOLS) - 1


def test_split_collection_materializes_once_after_both_groups() -> None:
    from app.jobs.overview_actions import run_overview_futures_daily_ohlcv

    requested: list[dict[str, Any]] = []
    materialized: list[bool] = []

    def collect_runner(**kwargs: Any) -> dict[str, Any]:
        requested.append(dict(kwargs))
        return _collection_result(list(kwargs["symbols"]))

    result = run_overview_futures_daily_ohlcv(
        coverage_loader=lambda symbols: _coverage(deficient="SI=F"),
        collect_runner=collect_runner,
        materialize_fn=lambda: materialized.append(True) or {"status": "materialized"},
        finalization_runner=_finalization_not_required,
    )

    assert [item["period"] for item in requested] == ["1y", "10y"]
    assert all(item["materialize_snapshot"] is False for item in requested)
    assert requested[1]["symbols"] == ["SI=F"]
    assert materialized == [True]
    assert result["details"]["futures_macro_snapshot"]["status"] == "materialized"
    assert result["details"]["collection_timing"]["upsert_duration_sec"] == 0.4


def test_failed_bootstrap_keeps_routine_rows_and_returns_partial_success() -> None:
    from app.jobs.overview_actions import run_overview_futures_daily_ohlcv

    def collect_runner(**kwargs: Any) -> dict[str, Any]:
        symbols = list(kwargs["symbols"])
        failed = symbols if kwargs["period"] == "10y" else []
        return _collection_result(symbols, failed=failed)

    result = run_overview_futures_daily_ohlcv(
        coverage_loader=lambda symbols: _coverage(deficient="SI=F"),
        collect_runner=collect_runner,
        materialize_fn=lambda: {"status": "reused"},
        finalization_runner=_finalization_not_required,
    )

    assert result["status"] == "partial_success"
    assert result["rows_written"] > 0
    assert result["failed_symbols"] == ["SI=F"]
    assert result["details"]["futures_macro_snapshot"]["status"] == "reused"


def test_daily_coverage_loader_uses_grouped_compact_query() -> None:
    from finance.loaders.futures import load_futures_daily_coverage

    captured: dict[str, Any] = {}

    def query(db_name: str, sql: str, params: list[Any]) -> list[dict[str, Any]]:
        captured.update(db_name=db_name, sql=sql, params=params)
        return [{"provider_symbol": "ES=F", "daily_row_count": 1_200}]

    rows = load_futures_daily_coverage(["ES=F", "NQ=F"], query_fn=query)

    assert rows[0]["provider_symbol"] == "ES=F"
    assert captured["db_name"] == "finance_price"
    assert "COUNT(*) AS daily_row_count" in captured["sql"]
    assert "GROUP BY provider_symbol" in captured["sql"]
    assert captured["params"] == ["1d", "ES=F", "NQ=F"]


def test_refresh_duration_includes_snapshot_materialization(monkeypatch) -> None:
    import app.jobs.overview_actions as overview_actions

    ticks = iter([10.0, 11.0, 12.0, 70.0])
    monkeypatch.setattr(overview_actions, "perf_counter", lambda: next(ticks))

    result = overview_actions.run_overview_futures_daily_ohlcv(
        coverage_loader=lambda symbols: _coverage(),
        collect_runner=lambda **kwargs: _collection_result(list(kwargs["symbols"])),
        materialize_fn=lambda: {"status": "materialized"},
        finalization_runner=_finalization_not_required,
    )

    assert result["duration_sec"] == 60.0


def _pending_daily_rows(
    symbols: tuple[str, ...],
    *,
    finalized: bool = False,
) -> list[dict[str, Any]]:
    from finance.data.futures_session_finalization import (
        FUTURES_SESSION_FINALIZATION_BASIS,
    )

    return [
        {
            "provider_symbol": symbol,
            "candle_time_utc": "2026-07-23 00:00:00",
            "collected_at": "2026-07-23 22:02:00",
            "final_close": 101.0 if finalized else None,
            "finalization_basis": (
                FUTURES_SESSION_FINALIZATION_BASIS if finalized else None
            ),
        }
        for symbol in symbols
    ]


def _stored_intraday_rows(
    symbols: tuple[str, ...],
) -> list[dict[str, Any]]:
    return [
        {
            "provider_symbol": symbol,
            "candle_time_utc": "2026-07-23 20:55:00",
            "open": 100.0,
            "high": 102.0,
            "low": 99.0,
            "close": 101.0,
            "volume": 10.0,
        }
        for symbol in symbols
    ]


def test_after_reopen_finalizes_pending_session_from_stored_rows() -> None:
    from app.jobs.futures_macro_daily_finalization import (
        run_pending_futures_daily_finalization,
    )

    events: list[str] = []
    symbols = tuple(DEFAULT_CORE_FUTURES_SYMBOLS)

    def collect_runner(**kwargs: Any) -> dict[str, Any]:
        events.append(f"collect:{kwargs['interval']}")
        return _collection_result(list(kwargs["symbols"]))

    def intraday_loader(**_kwargs: Any) -> list[dict[str, Any]]:
        events.append("load:5m")
        return _stored_intraday_rows(symbols)

    def writer(batch: Any, **_kwargs: Any) -> int:
        events.append(f"write:{len(batch.rows)}")
        return len(batch.rows)

    result = run_pending_futures_daily_finalization(
        symbols=symbols,
        evaluation_time=datetime(
            2026, 7, 23, 22, 2, tzinfo=timezone.utc
        ),
        collect_runner=collect_runner,
        daily_rows_loader=lambda _symbols: _pending_daily_rows(symbols),
        intraday_rows_loader=intraday_loader,
        writer=writer,
    )

    assert events == ["collect:5m", "load:5m", "write:17"]
    assert result["session_date"] == "2026-07-23"
    assert result["status"] == "finalized"
    assert result["symbols_finalized"] == 17


def test_before_settlement_cutoff_does_not_collect_intraday() -> None:
    from app.jobs.futures_macro_daily_finalization import (
        run_pending_futures_daily_finalization,
    )

    symbols = tuple(DEFAULT_CORE_FUTURES_SYMBOLS)

    result = run_pending_futures_daily_finalization(
        symbols=symbols,
        evaluation_time=datetime(
            2026, 7, 23, 21, 14, 59, tzinfo=timezone.utc
        ),
        collect_runner=lambda **_kwargs: (_ for _ in ()).throw(
            AssertionError("5m collection must be skipped")
        ),
        daily_rows_loader=lambda _symbols: _pending_daily_rows(symbols),
    )

    assert result["status"] == "not_due"


def test_prior_new_york_date_uses_raw_daily_without_intraday() -> None:
    from app.jobs.futures_macro_daily_finalization import (
        run_pending_futures_daily_finalization,
    )

    symbols = tuple(DEFAULT_CORE_FUTURES_SYMBOLS)

    result = run_pending_futures_daily_finalization(
        symbols=symbols,
        evaluation_time=datetime(
            2026, 7, 24, 12, 0, tzinfo=timezone.utc
        ),
        collect_runner=lambda **_kwargs: (_ for _ in ()).throw(
            AssertionError("5m collection must be skipped")
        ),
        daily_rows_loader=lambda _symbols: _pending_daily_rows(symbols),
    )

    assert result["status"] == "not_required"
    assert result["session_date"] == "2026-07-23"


def test_existing_explicit_finalization_is_reused() -> None:
    from app.jobs.futures_macro_daily_finalization import (
        run_pending_futures_daily_finalization,
    )

    symbols = tuple(DEFAULT_CORE_FUTURES_SYMBOLS)

    result = run_pending_futures_daily_finalization(
        symbols=symbols,
        evaluation_time=datetime(
            2026, 7, 23, 22, 2, tzinfo=timezone.utc
        ),
        collect_runner=lambda **_kwargs: (_ for _ in ()).throw(
            AssertionError("5m collection must be skipped")
        ),
        daily_rows_loader=lambda _symbols: _pending_daily_rows(
            symbols,
            finalized=True,
        ),
    )

    assert result["status"] == "reused"
    assert result["symbols_finalized"] == 17


def test_incomplete_daily_coverage_does_not_collect_intraday() -> None:
    from app.jobs.futures_macro_daily_finalization import (
        run_pending_futures_daily_finalization,
    )

    symbols = tuple(DEFAULT_CORE_FUTURES_SYMBOLS)

    result = run_pending_futures_daily_finalization(
        symbols=symbols,
        evaluation_time=datetime(
            2026, 7, 23, 22, 2, tzinfo=timezone.utc
        ),
        collect_runner=lambda **_kwargs: (_ for _ in ()).throw(
            AssertionError("5m collection must be skipped")
        ),
        daily_rows_loader=lambda _symbols: _pending_daily_rows(symbols[:-1]),
    )

    assert result["status"] == "incomplete"
    assert result["reason"] == "incomplete_daily_coverage"
    assert result["missing_symbols"] == [symbols[-1]]


def test_intraday_collection_failure_does_not_write() -> None:
    from app.jobs.futures_macro_daily_finalization import (
        run_pending_futures_daily_finalization,
    )

    symbols = tuple(DEFAULT_CORE_FUTURES_SYMBOLS)

    result = run_pending_futures_daily_finalization(
        symbols=symbols,
        evaluation_time=datetime(
            2026, 7, 23, 22, 2, tzinfo=timezone.utc
        ),
        collect_runner=lambda **_kwargs: _collection_result(
            list(symbols),
            failed=[symbols[-1]],
        ),
        daily_rows_loader=lambda _symbols: _pending_daily_rows(symbols),
        writer=lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("writer must be skipped")
        ),
    )

    assert result["status"] == "incomplete"
    assert result["reason"] == "intraday_collection_incomplete"
    assert result["missing_symbols"] == [symbols[-1]]


def test_incomplete_stored_coverage_does_not_write() -> None:
    from app.jobs.futures_macro_daily_finalization import (
        run_pending_futures_daily_finalization,
    )

    symbols = tuple(DEFAULT_CORE_FUTURES_SYMBOLS)

    result = run_pending_futures_daily_finalization(
        symbols=symbols,
        evaluation_time=datetime(
            2026, 7, 23, 22, 2, tzinfo=timezone.utc
        ),
        collect_runner=lambda **_kwargs: _collection_result(list(symbols)),
        daily_rows_loader=lambda _symbols: _pending_daily_rows(symbols),
        intraday_rows_loader=lambda **_kwargs: _stored_intraday_rows(
            symbols[:-1]
        ),
        writer=lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("writer must be skipped")
        ),
    )

    assert result["status"] == "incomplete"
    assert result["reason"] == "stored_intraday_coverage_incomplete"
    assert result["missing_symbols"] == [symbols[-1]]


def test_writer_error_returns_compact_error() -> None:
    from app.jobs.futures_macro_daily_finalization import (
        run_pending_futures_daily_finalization,
    )

    symbols = tuple(DEFAULT_CORE_FUTURES_SYMBOLS)

    def fail_writer(*_args: Any, **_kwargs: Any) -> int:
        raise RuntimeError("database exploded")

    result = run_pending_futures_daily_finalization(
        symbols=symbols,
        evaluation_time=datetime(
            2026, 7, 23, 22, 2, tzinfo=timezone.utc
        ),
        collect_runner=lambda **_kwargs: _collection_result(list(symbols)),
        daily_rows_loader=lambda _symbols: _pending_daily_rows(symbols),
        intraday_rows_loader=lambda **_kwargs: _stored_intraday_rows(symbols),
        writer=fail_writer,
    )

    assert result["status"] == "error"
    assert result["reason"] == "finalization_write_failed"
    assert "traceback" not in result


def test_overview_runs_finalization_before_materialization() -> None:
    from app.jobs.overview_actions import run_overview_futures_daily_ohlcv

    events: list[str] = []

    def collect_runner(**kwargs: Any) -> dict[str, Any]:
        events.append(f"collect:{kwargs['interval']}")
        return _collection_result(list(kwargs["symbols"]))

    result = run_overview_futures_daily_ohlcv(
        coverage_loader=lambda symbols: _coverage(),
        collect_runner=collect_runner,
        evaluation_time=datetime(
            2026, 7, 23, 22, 2, tzinfo=timezone.utc
        ),
        finalization_runner=lambda **_kwargs: events.append("finalize")
        or {
            "status": "finalized",
            "session_date": "2026-07-23",
            "symbols_required": 17,
            "symbols_finalized": 17,
            "missing_symbols": [],
            "reason": "session_aggregate_written",
        },
        materialize_fn=lambda: events.append("materialize")
        or {"status": "materialized"},
    )

    assert events == ["collect:1d", "finalize", "materialize"]
    assert result["details"]["daily_finalization"]["status"] == "finalized"


def test_overview_marks_finalization_failure_as_partial_but_materializes() -> None:
    from app.jobs.overview_actions import run_overview_futures_daily_ohlcv

    materialized: list[bool] = []
    result = run_overview_futures_daily_ohlcv(
        coverage_loader=lambda symbols: _coverage(),
        collect_runner=lambda **kwargs: _collection_result(
            list(kwargs["symbols"])
        ),
        finalization_runner=lambda **_kwargs: {
            "status": "incomplete",
            "session_date": "2026-07-23",
            "symbols_required": 17,
            "symbols_finalized": 0,
            "missing_symbols": ["SI=F"],
            "reason": "stored_intraday_coverage_incomplete",
        },
        materialize_fn=lambda: materialized.append(True)
        or {"status": "reused_pending"},
    )

    assert result["status"] == "partial_success"
    assert materialized == [True]
    assert result["details"]["futures_macro_snapshot"]["status"] == "reused_pending"
