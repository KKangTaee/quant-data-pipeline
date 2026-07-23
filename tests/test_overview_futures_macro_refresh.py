from __future__ import annotations

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
