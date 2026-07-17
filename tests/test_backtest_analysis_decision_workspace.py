from __future__ import annotations

from app.services.backtest_analysis_decision_workspace import (
    _deduplicate_reasons,
    build_level1_configuration_fingerprint,
    build_level1_readiness_projection,
    build_level1_strategy_catalog,
    level1_strategy_maturity,
)


def test_level1_catalog_groups_each_strategy_once() -> None:
    groups = build_level1_strategy_catalog()
    options = [item["strategy_choice"] for group in groups for item in group["items"]]

    assert options == [
        "Quality + Value",
        "Quality",
        "Value",
        "GTAA",
        "Global Relative Strength",
        "Dual Momentum",
        "Risk Parity Trend",
        "Equal Weight",
        "Risk-On Momentum 5D",
    ]
    assert len(options) == len(set(options))


def test_risk_on_is_development_not_research() -> None:
    assert level1_strategy_maturity("Risk-On Momentum 5D") == "development"
    assert level1_strategy_maturity("GTAA") == "production"


def test_configuration_fingerprint_is_order_independent_and_sensitive() -> None:
    left = build_level1_configuration_fingerprint(
        workspace_kind="single_strategy",
        selection={"strategy_choice": "GTAA"},
        configuration={"top": 3, "tickers": ["SPY", "TLT"]},
    )
    reordered = build_level1_configuration_fingerprint(
        workspace_kind="single_strategy",
        selection={"strategy_choice": "GTAA"},
        configuration={"tickers": ["SPY", "TLT"], "top": 3},
    )
    changed = build_level1_configuration_fingerprint(
        workspace_kind="single_strategy",
        selection={"strategy_choice": "GTAA"},
        configuration={"top": 2, "tickers": ["SPY", "TLT"]},
    )

    assert left == reordered
    assert left != changed


def test_stale_result_is_preserved_and_handoff_blocked() -> None:
    projection = build_level1_readiness_projection(
        workspace_kind="single_strategy",
        strategy_choice="GTAA",
        result_bundle={"meta": {"strategy_key": "gtaa"}},
        current_configuration_fingerprint="current",
        result_configuration_fingerprint="previous",
        action_handlers={"save_and_move": lambda: None},
    )

    assert projection["result_freshness"] == "stale"
    assert projection["handoff_state"] == "blocked"
    assert projection["result_available"] is True


def test_development_or_missing_handler_has_no_cta() -> None:
    development = build_level1_readiness_projection(
        workspace_kind="single_strategy",
        strategy_choice="Risk-On Momentum 5D",
        result_bundle={"meta": {"strategy_key": "risk_on_momentum_5d"}},
        current_configuration_fingerprint="same",
        result_configuration_fingerprint="same",
        action_handlers={"save_and_move": lambda: None},
    )
    missing = build_level1_readiness_projection(
        workspace_kind="single_strategy",
        strategy_choice="GTAA",
        result_bundle={"meta": {"strategy_key": "gtaa"}},
        current_configuration_fingerprint="same",
        result_configuration_fingerprint="same",
        action_handlers={"save_and_move": None},
    )

    assert "save_and_move" not in development["actions"]
    assert "save_and_move" not in missing["actions"]


def test_duplicate_root_reason_is_counted_once() -> None:
    rows = _deduplicate_reasons(
        [
            {"root_issue_id": "price", "message": "가격 확인"},
            {"root_issue_id": "price", "message": "가격 확인"},
        ]
    )

    assert rows == [{"root_issue_id": "price", "message": "가격 확인"}]
