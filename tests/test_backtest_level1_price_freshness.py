from __future__ import annotations

from app.services.backtest_level1_price_freshness import (
    build_level1_price_freshness_action,
    build_level1_price_refresh_meta,
)


def _freshness(
    *,
    common_latest: str,
    refresh: list[str],
    stale: list[str] | None = None,
    missing: list[str] | None = None,
    classifications: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    return {
        "status": "warning" if refresh else "ok",
        "details": {
            "common_latest_date": common_latest,
            "effective_end_date": "2026-07-21",
            "refresh_symbols_all": refresh,
            "stale_symbols_all": stale or [],
            "missing_symbols_all": missing or [],
            "classification_rows": classifications or [],
        },
    }


def test_single_refresh_meta_includes_all_price_dependent_symbols() -> None:
    bundle = {
        "meta": {
            "tickers": ["spy", "TLT"],
            "cash_ticker": "bil",
            "benchmark_ticker": "SPY",
            "guardrail_reference_ticker": "qqq",
            "market_regime_benchmark": "acwi",
            "defensive_tickers": ["ief", "TLT"],
            "start": "2016-01-01",
            "end": "2026-07-20",
            "actual_result_end": "2026-06-26",
            "price_freshness": _freshness(
                common_latest="2026-06-26",
                refresh=["spy", "BIL"],
                stale=["SPY"],
                missing=["bil"],
                classifications=[
                    {"symbol": "bil", "reason": "provider_no_data"},
                ],
            ),
        }
    }

    meta = build_level1_price_refresh_meta(
        result_bundle=bundle,
        configuration={"start": "2017-01-01", "end": "2026-07-22"},
    )

    assert meta["tickers"] == ["SPY", "TLT", "BIL", "QQQ", "ACWI", "IEF"]
    assert meta["start"] == "2017-01-01"
    assert meta["end"] == "2026-07-22"
    assert meta["actual_result_end"] == "2026-06-26"
    details = meta["price_freshness"]["details"]
    assert details["refresh_symbols_all"] == ["SPY", "BIL"]
    assert details["stale_symbols_all"] == ["SPY"]
    assert details["missing_symbols_all"] == ["BIL"]
    assert details["classification_rows"] == [
        {"symbol": "BIL", "reason": "provider_no_data"}
    ]


def test_mix_refresh_meta_unions_components_and_uses_earliest_common_date() -> None:
    weighted = {
        "meta": {
            "tickers": ["SPY"],
            "start": "2016-01-01",
            "end": "2026-07-18",
            "price_freshness": _freshness(
                common_latest="2026-07-01",
                refresh=["SPY"],
                stale=["SPY"],
            ),
        }
    }
    components = (
        {
            "meta": {
                "tickers": ["SPY", "TLT"],
                "cash_ticker": "BIL",
                "price_freshness": _freshness(
                    common_latest="2026-06-28",
                    refresh=["TLT", "BIL"],
                    stale=["TLT"],
                    missing=["BIL"],
                ),
            }
        },
        {
            "meta": {
                "tickers": ["GLD", "spy"],
                "benchmark_ticker": "QQQ",
                "price_freshness": _freshness(
                    common_latest="2026-06-30",
                    refresh=["gld", "SPY"],
                    stale=["GLD", "SPY"],
                ),
            }
        },
    )

    meta = build_level1_price_refresh_meta(
        result_bundle=weighted,
        component_bundles=components,
        configuration={"start": "2018-01-01", "end": "2026-07-22"},
    )

    assert meta["tickers"] == ["SPY", "TLT", "BIL", "GLD", "QQQ"]
    assert meta["end"] == "2026-07-22"
    assert meta["actual_result_end"] == "2026-06-28"
    details = meta["price_freshness"]["details"]
    assert details["common_latest_date"] == "2026-06-28"
    assert details["refresh_symbols_all"] == ["SPY", "TLT", "BIL", "GLD"]
    assert details["stale_symbols_all"] == ["SPY", "TLT", "GLD"]
    assert details["missing_symbols_all"] == ["BIL"]


def _plan(*, status: str = "refresh_available", eligible: bool = True) -> dict[str, object]:
    return {
        "status": status,
        "eligible": eligible,
        "requested_end": "2026-07-22",
        "target_end": "2026-07-21",
        "current_common_latest": "2026-06-26",
        "source_tickers": ["SPY", "TLT"],
        "ticker_count": 2,
        "provider_gap_symbols": [],
        "summary": "2개 가격 데이터를 최신화할 수 있습니다.",
    }


def test_refresh_available_becomes_one_blocking_manual_action() -> None:
    action = build_level1_price_freshness_action(plan=_plan())

    assert action["state"] == "refresh_required"
    assert action["handoff_blocked"] is True
    assert action["requested_end"] == "2026-07-22"
    assert action["target_trading_end"] == "2026-07-21"
    assert action["current_common_latest"] == "2026-06-26"
    assert action["affected_symbol_count"] == 2
    assert action["affected_symbol_sample"] == ["SPY", "TLT"]
    assert action["primary_action"] == {
        "id": "refresh_prices",
        "label": "종목 데이터 최신화",
        "enabled": True,
    }


def test_written_refresh_rows_require_explicit_backtest_rerun() -> None:
    action = build_level1_price_freshness_action(
        plan=_plan(),
        refresh_result={"status": "success", "rows_written": 12},
        result_requires_rerun=True,
    )

    assert action["state"] == "rerun_required"
    assert action["handoff_blocked"] is True
    assert action["primary_action"] == {
        "id": "rerun_same_configuration",
        "label": "같은 설정으로 다시 백테스트",
        "enabled": True,
    }


def test_zero_row_unresolved_refresh_stops_retry_loop() -> None:
    action = build_level1_price_freshness_action(
        plan=_plan(),
        refresh_result={
            "status": "success",
            "rows_written": 0,
            "details": {"post_refresh_unresolved_symbols": ["SPY"]},
        },
    )

    assert action["state"] == "provider_gap"
    assert action["handoff_blocked"] is True
    assert action["affected_symbol_sample"] == ["SPY"]
    assert action["primary_action"] is None


def test_provider_gap_only_blocks_handoff_without_refresh_retry() -> None:
    plan = _plan(status="provider_gap_only", eligible=False)
    plan["source_tickers"] = []
    plan["ticker_count"] = 0
    plan["provider_gap_symbols"] = ["BK"]

    action = build_level1_price_freshness_action(plan=plan)

    assert action["state"] == "provider_gap"
    assert action["handoff_blocked"] is True
    assert action["affected_symbol_sample"] == ["BK"]
    assert action["primary_action"] is None


def test_up_to_date_plan_keeps_handoff_open() -> None:
    action = build_level1_price_freshness_action(
        plan=_plan(status="up_to_date", eligible=False)
    )

    assert action["state"] == "current"
    assert action["handoff_blocked"] is False
    assert action["primary_action"] is None
