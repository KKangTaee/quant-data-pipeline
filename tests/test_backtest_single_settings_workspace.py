from __future__ import annotations

from copy import deepcopy
from datetime import date
from types import SimpleNamespace

import pytest

import app.services.backtest_single_settings_workspace as settings_service
import app.web.backtest_single_settings_workspace as settings_web

from app.services.backtest_single_settings_workspace import (
    ALLOWED_CONTROLS,
    SETTINGS_SCHEMA_VERSION,
    SINGLE_SETTINGS_CONCRETE_KEYS,
    SettingsValidationError,
    build_single_settings_workspace,
    project_single_settings_payload,
    validate_single_settings_draft,
)


EXPECTED_CONCRETE_KEYS = {
    "Equal Weight": (None,),
    "GTAA": (None,),
    "Global Relative Strength": (None,),
    "Risk Parity Trend": (None,),
    "Dual Momentum": (None,),
    "Risk-On Momentum 5D": (None,),
    "Quality": ("Annual", "Quarterly", "Snapshot"),
    "Value": ("Annual", "Quarterly"),
    "Quality + Value": ("Annual", "Quarterly"),
}


RUNTIME_OPTIONS = {
    "presets": {
        "Equal Weight": {
            "Dividend ETFs": ["VIG", "SCHD", "DGRO", "GLD"],
        },
        "GTAA": {
            "GTAA Universe": ["SPY", "IWD", "IWM", "TLT", "GLD"],
        },
        "Global Relative Strength": {
            "Global Relative Strength Core ETF Universe": [
                "SPY",
                "EFA",
                "TLT",
                "GLD",
            ],
        },
        "Risk Parity Trend": {
            "Risk Parity Universe": ["SPY", "TLT", "GLD", "IEF", "LQD"],
        },
        "Dual Momentum": {
            "Dual Momentum Universe": ["QQQ", "SPY", "IWM", "SOXX", "BIL"],
        },
    },
    "tickers": [
        "VIG",
        "SCHD",
        "DGRO",
        "GLD",
        "SPY",
        "IWD",
        "IWM",
        "TLT",
        "EFA",
        "IEF",
        "LQD",
        "QQQ",
        "SOXX",
        "BIL",
    ],
    "benchmarks": ["SPY", "ACWI", "QQQ", "VTI"],
    "score_horizons": [1, 3, 6, 12],
    "market_regime_benchmarks": ["SPY", "QQQ", "VTI", "IWM"],
    "policy_defaults": {
        "promotion_min_benchmark_coverage": 0.95,
        "promotion_min_net_cagr_spread": -0.02,
        "promotion_min_liquidity_clean_coverage": 0.9,
        "promotion_max_underperformance_share": 0.55,
        "promotion_min_worst_rolling_excess_return": -0.15,
        "promotion_max_strategy_drawdown": -0.35,
        "promotion_max_drawdown_gap_vs_benchmark": 0.08,
    },
    "presets_by_strategy_key": {
        "quality_snapshot": {
            "Big Tech Quality Trial": ["AAPL", "MSFT", "GOOG"],
        },
        "quality_snapshot_strict_annual": {
            "US Statement Coverage 100": ["AAPL", "MSFT", "GOOG"],
            "US Statement Coverage 300": ["AAPL", "MSFT", "GOOG", "AMZN"],
        },
        "quality_snapshot_strict_quarterly_prototype": {
            "US Statement Coverage 100": ["AAPL", "MSFT", "GOOG"],
        },
        "value_snapshot_strict_annual": {
            "US Statement Coverage 100": ["AAPL", "MSFT", "GOOG"],
            "US Statement Coverage 300": ["AAPL", "MSFT", "GOOG", "AMZN"],
        },
        "value_snapshot_strict_quarterly_prototype": {
            "US Statement Coverage 100": ["AAPL", "MSFT", "GOOG"],
        },
        "quality_value_snapshot_strict_annual": {
            "US Statement Coverage 100": ["AAPL", "MSFT", "GOOG"],
            "US Statement Coverage 300": ["AAPL", "MSFT", "GOOG", "AMZN"],
        },
        "quality_value_snapshot_strict_quarterly_prototype": {
            "US Statement Coverage 100": ["AAPL", "MSFT", "GOOG"],
        },
    },
    "preset_target_sizes": {
        "US Statement Coverage 100": 100,
        "US Statement Coverage 300": 300,
    },
    "quality_factor_options": [
        "roe",
        "roa",
        "net_margin",
        "asset_turnover",
        "current_ratio",
        "cash_ratio",
        "operating_margin",
        "interest_coverage",
        "ocf_margin",
        "fcf_margin",
        "net_debt_to_equity",
        "debt_to_assets",
        "debt_ratio",
        "gross_margin",
    ],
    "value_factor_options": [
        "book_to_market",
        "earnings_yield",
        "sales_yield",
        "ocf_yield",
        "fcf_yield",
        "operating_income_yield",
        "liquidation_value",
        "per",
        "pbr",
        "psr",
        "pcr",
        "pfcr",
        "ev_ebit",
        "por",
    ],
}


def _fields(workspace: dict[str, object]) -> list[dict[str, object]]:
    return [
        field
        for section in workspace["sections"]
        for field in section["fields"]
    ]


def _visible_draft(workspace: dict[str, object]) -> dict[str, object]:
    values = {field["field_id"]: field["value"] for field in _fields(workspace)}
    return {
        field["field_id"]: field["value"]
        for field in _fields(workspace)
        if not field.get("visible_when")
        or all(
            values.get(dependency) == expected
            for dependency, expected in field["visible_when"].items()
        )
    }


def _field_values(workspace: dict[str, object]) -> dict[str, object]:
    return {field["field_id"]: field["value"] for field in _fields(workspace)}


def _runtime_with_gtaa_evidence_preset() -> dict[str, object]:
    runtime = deepcopy(RUNTIME_OPTIONS)
    runtime["presets"]["GTAA"] = {
        "GTAA Universe": ["SPY", "TLT", "GLD"],
        "GTAA Evidence": ["QQQ", "IEF", "TLT"],
    }
    runtime["preset_parameter_defaults_by_strategy_key"] = {
        "gtaa": {
            "GTAA Evidence": {
                "top": 2,
                "interval": 4,
                "score_lookback_months": [1, 6],
                "defensive_tickers": ["IEF", "TLT"],
            }
        }
    }
    return runtime


PROMOTION_POLICY_KEYS = {
    "promotion_min_benchmark_coverage",
    "promotion_min_net_cagr_spread",
    "promotion_min_liquidity_clean_coverage",
    "promotion_max_underperformance_share",
    "promotion_min_worst_rolling_excess_return",
    "promotion_max_strategy_drawdown",
    "promotion_max_drawdown_gap_vs_benchmark",
}


TACTICAL_EXPECTED_KEYS = {
    "Equal Weight": {
        "strategy_key",
        "tickers",
        "start",
        "end",
        "timeframe",
        "option",
        "rebalance_interval",
        "min_price_filter",
        "transaction_cost_bps",
        "benchmark_ticker",
        "promotion_min_etf_aum_b",
        "promotion_max_bid_ask_spread_pct",
        "universe_mode",
        "preset_name",
    },
    "GTAA": {
        "strategy_key",
        "tickers",
        "start",
        "end",
        "timeframe",
        "option",
        "top",
        "interval",
        "score_lookback_months",
        "score_return_columns",
        "score_weights",
        "trend_filter_window",
        "risk_off_mode",
        "defensive_tickers",
        "market_regime_enabled",
        "market_regime_window",
        "market_regime_benchmark",
        "crash_guardrail_enabled",
        "crash_guardrail_drawdown_threshold",
        "crash_guardrail_lookback_months",
        "min_price_filter",
        "min_avg_dollar_volume_20d_m_filter",
        "transaction_cost_bps",
        "benchmark_ticker",
        "promotion_min_etf_aum_b",
        "promotion_max_bid_ask_spread_pct",
        "underperformance_guardrail_enabled",
        "underperformance_guardrail_window_months",
        "underperformance_guardrail_threshold",
        "drawdown_guardrail_enabled",
        "drawdown_guardrail_window_months",
        "drawdown_guardrail_strategy_threshold",
        "drawdown_guardrail_gap_threshold",
        "universe_mode",
        "preset_name",
    }
    | PROMOTION_POLICY_KEYS,
    "Global Relative Strength": {
        "strategy_key",
        "tickers",
        "cash_ticker",
        "start",
        "end",
        "timeframe",
        "option",
        "top",
        "interval",
        "score_lookback_months",
        "score_return_columns",
        "score_weights",
        "trend_filter_enabled",
        "trend_filter_window",
        "min_price_filter",
        "transaction_cost_bps",
        "benchmark_ticker",
        "promotion_min_etf_aum_b",
        "promotion_max_bid_ask_spread_pct",
        "universe_mode",
        "preset_name",
    }
    | PROMOTION_POLICY_KEYS,
    "Risk Parity Trend": {
        "strategy_key",
        "tickers",
        "start",
        "end",
        "timeframe",
        "option",
        "rebalance_interval",
        "vol_window",
        "min_price_filter",
        "transaction_cost_bps",
        "benchmark_ticker",
        "promotion_min_etf_aum_b",
        "promotion_max_bid_ask_spread_pct",
        "underperformance_guardrail_enabled",
        "underperformance_guardrail_window_months",
        "underperformance_guardrail_threshold",
        "drawdown_guardrail_enabled",
        "drawdown_guardrail_window_months",
        "drawdown_guardrail_strategy_threshold",
        "drawdown_guardrail_gap_threshold",
        "universe_mode",
        "preset_name",
    }
    | PROMOTION_POLICY_KEYS,
    "Dual Momentum": {
        "strategy_key",
        "tickers",
        "start",
        "end",
        "timeframe",
        "option",
        "top",
        "rebalance_interval",
        "min_price_filter",
        "transaction_cost_bps",
        "benchmark_ticker",
        "promotion_min_etf_aum_b",
        "promotion_max_bid_ask_spread_pct",
        "underperformance_guardrail_enabled",
        "underperformance_guardrail_window_months",
        "underperformance_guardrail_threshold",
        "drawdown_guardrail_enabled",
        "drawdown_guardrail_window_months",
        "drawdown_guardrail_strategy_threshold",
        "drawdown_guardrail_gap_threshold",
        "universe_mode",
        "preset_name",
    }
    | PROMOTION_POLICY_KEYS,
    "Risk-On Momentum 5D": {
        "strategy_key",
        "tickers",
        "start",
        "end",
        "timeframe",
        "option",
        "universe_mode",
        "preset_name",
        "universe_limit",
        "start_balance",
        "execution_mode",
        "exit_mode",
        "max_holding_days",
        "stop_loss_pct",
        "take_profit_pct",
        "atr_period",
        "stop_atr_multiple",
        "take_profit_atr_multiple",
        "max_new_positions_per_day",
        "max_total_positions",
        "transaction_cost_bps",
        "slippage_bps",
        "macro_filter_enabled",
        "macro_filter_mode",
        "risk_on_min",
        "rate_pressure_max",
        "dollar_pressure_max",
        "safe_haven_max",
        "rate_pressure_penalty_weight",
        "dollar_pressure_penalty_weight",
        "safe_haven_penalty_weight",
        "min_price",
        "min_avg_dollar_volume_20d",
        "min_avg_volume_20d",
        "random_iterations",
        "scanner_top_n_per_day",
        "run_comparison_suite",
        "run_sensitivity_suite",
    },
}


STRICT_COMMON_KEYS = {
    "strategy_key",
    "tickers",
    "start",
    "end",
    "timeframe",
    "option",
    "top",
    "rebalance_interval",
    "factor_freq",
    "snapshot_mode",
    "trend_filter_enabled",
    "trend_filter_window",
    "weighting_mode",
    "rejected_slot_handling_mode",
    "rejected_slot_fill_enabled",
    "partial_cash_retention_enabled",
    "risk_off_mode",
    "defensive_tickers",
    "market_regime_enabled",
    "market_regime_window",
    "market_regime_benchmark",
    "universe_contract",
    "dynamic_candidate_tickers",
    "dynamic_target_size",
    "universe_mode",
    "preset_name",
}

STRICT_ANNUAL_RISK_KEYS = {
    "min_price_filter",
    "min_history_months_filter",
    "min_avg_dollar_volume_20d_m_filter",
    "transaction_cost_bps",
    "benchmark_contract",
    "benchmark_ticker",
    "guardrail_reference_ticker",
    "promotion_min_benchmark_coverage",
    "promotion_min_net_cagr_spread",
    "promotion_min_liquidity_clean_coverage",
    "promotion_max_underperformance_share",
    "promotion_min_worst_rolling_excess_return",
    "promotion_max_strategy_drawdown",
    "promotion_max_drawdown_gap_vs_benchmark",
    "underperformance_guardrail_enabled",
    "underperformance_guardrail_window_months",
    "underperformance_guardrail_threshold",
    "drawdown_guardrail_enabled",
    "drawdown_guardrail_window_months",
    "drawdown_guardrail_strategy_threshold",
    "drawdown_guardrail_gap_threshold",
}

STRICT_EXPECTED_KEYS = {
    ("Quality", "Snapshot"): {
        "strategy_key",
        "tickers",
        "start",
        "end",
        "timeframe",
        "option",
        "top",
        "factor_freq",
        "rebalance_freq",
        "snapshot_mode",
        "quality_factors",
        "universe_mode",
        "preset_name",
    },
    ("Quality", "Annual"): STRICT_COMMON_KEYS
    | STRICT_ANNUAL_RISK_KEYS
    | {"quality_factors"},
    ("Quality", "Quarterly"): STRICT_COMMON_KEYS | {"quality_factors"},
    ("Value", "Annual"): STRICT_COMMON_KEYS
    | STRICT_ANNUAL_RISK_KEYS
    | {"snapshot_source", "value_factors"},
    ("Value", "Quarterly"): STRICT_COMMON_KEYS
    | {"snapshot_source", "value_factors"},
    ("Quality + Value", "Annual"): STRICT_COMMON_KEYS
    | STRICT_ANNUAL_RISK_KEYS
    | {"snapshot_source", "quality_factors", "value_factors"},
    ("Quality + Value", "Quarterly"): STRICT_COMMON_KEYS
    | {"snapshot_source", "quality_factors", "value_factors"},
}


def test_schema_covers_every_concrete_variant_once() -> None:
    assert SINGLE_SETTINGS_CONCRETE_KEYS == EXPECTED_CONCRETE_KEYS

    projected = []
    for strategy_choice, variants in EXPECTED_CONCRETE_KEYS.items():
        for variant in variants:
            workspace = build_single_settings_workspace(
                strategy_choice,
                variant,
                {},
                runtime_options={},
            )
            projected.append(
                (workspace["strategy_choice"], workspace["variant"]["value"])
            )
            assert workspace["schema_version"] == SETTINGS_SCHEMA_VERSION
            assert [section["section_id"] for section in workspace["sections"]] == [
                "execution",
                "universe",
                "rules",
                "risk",
            ]
            assert workspace["action"]["id"] == "run_single_strategy"

    assert len(projected) == 13
    assert len(set(projected)) == 13


def test_schema_fields_are_unique_supported_and_korean_first() -> None:
    for strategy_choice, variants in EXPECTED_CONCRETE_KEYS.items():
        for variant in variants:
            workspace = build_single_settings_workspace(
                strategy_choice,
                variant,
                {},
                runtime_options={},
            )
            fields = _fields(workspace)
            field_ids = [str(field["field_id"]) for field in fields]
            payload_keys = [str(field["payload_key"]) for field in fields]
            assert len(field_ids) == len(set(field_ids))
            assert len(payload_keys) == len(set(payload_keys))
            assert all(field["control"] in ALLOWED_CONTROLS for field in fields)
            assert all(any("가" <= char <= "힣" for char in field["label"]) for field in fields)
            assert all(any("가" <= char <= "힣" for char in field["help"]) for field in fields)
            assert "<" not in workspace["profile"]["maturity_label"]


def test_workspace_returns_isolated_json_ready_copies() -> None:
    first = build_single_settings_workspace(
        "Equal Weight", None, {}, runtime_options=RUNTIME_OPTIONS
    )
    original = deepcopy(first)
    first["sections"][0]["fields"][0]["value"] = "changed"
    second = build_single_settings_workspace(
        "Equal Weight", None, {}, runtime_options=RUNTIME_OPTIONS
    )

    assert second == original


def test_every_named_preset_has_schema_safe_complete_profile() -> None:
    workspace = build_single_settings_workspace(
        "GTAA",
        None,
        {},
        _runtime_with_gtaa_evidence_preset(),
    )
    field_ids = {field["field_id"] for field in _fields(workspace)}

    assert "preset_profiles" in workspace
    assert set(workspace["preset_profiles"]) == {
        "GTAA Universe",
        "GTAA Evidence",
    }
    assert set(workspace["preset_profiles"]["GTAA Universe"]["values"]) <= field_ids
    assert (
        workspace["preset_profiles"]["GTAA Universe"]["application_kind"]
        == "strategy_default"
    )
    assert (
        workspace["preset_profiles"]["GTAA Evidence"]["application_kind"]
        == "validated_override"
    )
    assert workspace["preset_profiles"]["GTAA Evidence"]["values"]["top"] == 2
    assert workspace["preset_profiles"]["GTAA Evidence"]["values"]["interval"] == 4


@pytest.mark.parametrize(
    ("strategy_choice", "variant"),
    [
        ("Equal Weight", None),
        ("GTAA", None),
        ("Global Relative Strength", None),
        ("Risk Parity Trend", None),
        ("Dual Momentum", None),
        ("Quality", "Annual"),
        ("Quality", "Quarterly"),
        ("Quality", "Snapshot"),
        ("Value", "Annual"),
        ("Value", "Quarterly"),
        ("Quality + Value", "Annual"),
        ("Quality + Value", "Quarterly"),
    ],
)
def test_all_named_preset_families_publish_complete_profiles(
    strategy_choice: str,
    variant: str | None,
) -> None:
    workspace = build_single_settings_workspace(
        strategy_choice,
        variant,
        {},
        RUNTIME_OPTIONS,
    )
    members = workspace["runtime_context"]["preset_members"]

    assert "preset_profiles" in workspace
    assert set(workspace["preset_profiles"]) == set(members)
    assert all(
        profile["values"] for profile in workspace["preset_profiles"].values()
    )


def test_apply_preset_resets_owned_fields_but_preserves_dates_and_manual_tickers() -> None:
    workspace = build_single_settings_workspace(
        "GTAA",
        None,
        {},
        _runtime_with_gtaa_evidence_preset(),
    )

    assert hasattr(settings_service, "apply_single_settings_preset")
    applied = settings_service.apply_single_settings_preset(
        workspace,
        {
            "start": "2020-01-01",
            "end": "2025-12-31",
            "tickers": ["CUSTOM"],
            "top": 9,
            "interval": 9,
            "score_lookback_months": [12],
        },
        "GTAA Evidence",
    )

    assert applied["values"]["start"] == "2020-01-01"
    assert applied["values"]["end"] == "2025-12-31"
    assert applied["values"]["tickers"] == ["CUSTOM"]
    assert applied["values"]["universe_mode"] == "preset"
    assert applied["values"]["preset_name"] == "GTAA Evidence"
    assert applied["values"]["top"] == 2
    assert applied["values"]["interval"] == 4
    assert applied["values"]["score_lookback_months"] == [1, 6]
    assert applied["application"]["application_kind"] == "validated_override"


def test_initial_explicit_prefill_wins_over_selected_preset_profile() -> None:
    workspace = build_single_settings_workspace(
        "GTAA",
        None,
        {
            "preset_name": "GTAA Evidence",
            "top": 5,
            "score_lookback_months": [3, 12],
        },
        _runtime_with_gtaa_evidence_preset(),
    )
    values = _field_values(workspace)

    assert values["preset_name"] == "GTAA Evidence"
    assert values["top"] == 5
    assert values["score_lookback_months"] == [3, 12]
    assert values["interval"] == 4


def test_fallback_preset_callback_preserves_widget_typed_dates_and_manual_tickers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace = build_single_settings_workspace(
        "GTAA",
        None,
        {},
        _runtime_with_gtaa_evidence_preset(),
    )
    key_prefix = "gtaa-draft"
    session_state = {
        f"{key_prefix}:start": date(2020, 1, 1),
        f"{key_prefix}:end": date(2025, 12, 31),
        f"{key_prefix}:tickers": ["CUSTOM"],
        f"{key_prefix}:universe_mode": "preset",
        f"{key_prefix}:preset_name": "GTAA Evidence",
        f"{key_prefix}:top": 9,
        f"{key_prefix}:interval": 9,
    }
    monkeypatch.setattr(
        settings_web,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    settings_web._apply_fallback_preset_profile(workspace, key_prefix)

    assert session_state[f"{key_prefix}:start"] == date(2020, 1, 1)
    assert session_state[f"{key_prefix}:end"] == date(2025, 12, 31)
    assert session_state[f"{key_prefix}:tickers"] == ["CUSTOM"]
    assert session_state[f"{key_prefix}:top"] == 2
    assert session_state[f"{key_prefix}:interval"] == 4
    assert session_state[f"{key_prefix}:preset_application_feedback"] == (
        "검증된 프리셋 설정을 적용했습니다."
    )


@pytest.mark.parametrize(
    ("strategy_choice", "variant"),
    [
        ("Unknown", None),
        ("GTAA", "Annual"),
        ("Quality", "Monthly"),
        ("Quality", None),
    ],
)
def test_schema_rejects_unknown_strategy_or_variant(
    strategy_choice: str,
    variant: str | None,
) -> None:
    with pytest.raises(ValueError, match="전략|variant"):
        build_single_settings_workspace(
            strategy_choice,
            variant,
            {},
            runtime_options=RUNTIME_OPTIONS,
        )


def test_validator_rejects_unknown_hidden_range_and_invalid_option() -> None:
    workspace = build_single_settings_workspace(
        "Equal Weight", None, {}, runtime_options=RUNTIME_OPTIONS
    )
    errors = validate_single_settings_draft(
        workspace,
        {
            "unknown": "x",
            "universe_mode": "preset",
            "tickers": ["VIG"],
            "rebalance_interval": 0,
            "preset_name": "not-allowed",
        },
    )

    assert errors["unknown"] == "허용되지 않은 설정입니다."
    assert errors["tickers"] == "현재 조건에서는 사용할 수 없는 설정입니다."
    assert "최솟값" in errors["rebalance_interval"]
    assert "선택할 수 없는 값" in errors["preset_name"]


@pytest.mark.parametrize(
    ("values", "field_id", "message"),
    [
        ({"start": 20200101}, "start", "날짜"),
        ({"rebalance_interval": True}, "rebalance_interval", "숫자"),
        ({"universe_mode": ["preset"]}, "universe_mode", "선택"),
        ({"transaction_cost_bps": "10"}, "transaction_cost_bps", "숫자"),
        ({"benchmark_ticker": ["SPY"]}, "benchmark_ticker", "선택"),
        (
            {"universe_mode": "manual_tickers", "tickers": "VIG"},
            "tickers",
            "목록",
        ),
        (
            {
                "universe_mode": "manual_tickers",
                "tickers": ["VIG", "VIG"],
            },
            "tickers",
            "중복",
        ),
    ],
)
def test_validator_rejects_control_type_errors(
    values: dict[str, object],
    field_id: str,
    message: str,
) -> None:
    workspace = build_single_settings_workspace(
        "Equal Weight", None, {}, runtime_options=RUNTIME_OPTIONS
    )

    errors = validate_single_settings_draft(workspace, values)

    assert message in errors[field_id]


def test_projector_raises_with_field_errors_before_building_payload() -> None:
    workspace = build_single_settings_workspace(
        "Equal Weight", None, {}, runtime_options=RUNTIME_OPTIONS
    )

    with pytest.raises(SettingsValidationError) as exc_info:
        project_single_settings_payload(
            workspace,
            {"rebalance_interval": 0},
        )

    assert "rebalance_interval" in exc_info.value.errors


def test_projector_uses_only_visible_declared_fields_and_constants() -> None:
    workspace = build_single_settings_workspace(
        "Equal Weight", None, {}, runtime_options=RUNTIME_OPTIONS
    )
    submitted = {
        field["field_id"]: field["value"]
        for field in _fields(workspace)
        if not field.get("visible_when")
        or field["visible_when"].get("universe_mode") == "preset"
    }

    payload = project_single_settings_payload(workspace, submitted)

    assert payload["strategy_key"] == "equal_weight"
    assert payload["option"] == "month_end"
    assert payload["universe_mode"] == "preset"
    assert "unknown" not in payload
    assert payload["tickers"] == ["VIG", "SCHD", "DGRO", "GLD"]


@pytest.mark.parametrize("strategy_choice", tuple(TACTICAL_EXPECTED_KEYS))
def test_tactical_strategy_default_payload_has_exact_legacy_key_set(
    strategy_choice: str,
) -> None:
    workspace = build_single_settings_workspace(
        strategy_choice,
        None,
        {},
        runtime_options=RUNTIME_OPTIONS,
    )

    payload = project_single_settings_payload(workspace, _visible_draft(workspace))

    assert set(payload) == TACTICAL_EXPECTED_KEYS[strategy_choice]


def test_equal_weight_representative_payload_matches_legacy_contract() -> None:
    workspace = build_single_settings_workspace(
        "Equal Weight",
        None,
        {
            "start": "2016-01-01",
            "end": "2026-07-18",
            "rebalance_interval": 12,
            "universe_mode": "preset",
            "preset_name": "Dividend ETFs",
            "min_price_filter": 5.0,
            "transaction_cost_bps": 10.0,
            "benchmark_ticker": "SPY",
            "promotion_min_etf_aum_b": 1.0,
            "promotion_max_bid_ask_spread_pct": 0.005,
        },
        runtime_options=RUNTIME_OPTIONS,
    )

    payload = project_single_settings_payload(workspace, _visible_draft(workspace))

    assert payload == {
        "strategy_key": "equal_weight",
        "tickers": ["VIG", "SCHD", "DGRO", "GLD"],
        "start": "2016-01-01",
        "end": "2026-07-18",
        "timeframe": "1d",
        "option": "month_end",
        "rebalance_interval": 12,
        "min_price_filter": 5.0,
        "transaction_cost_bps": 10.0,
        "benchmark_ticker": "SPY",
        "promotion_min_etf_aum_b": 1.0,
        "promotion_max_bid_ask_spread_pct": 0.005,
        "universe_mode": "preset",
        "preset_name": "Dividend ETFs",
    }


def test_gtaa_projection_derives_score_columns_weights_and_percent_ratios() -> None:
    workspace = build_single_settings_workspace(
        "GTAA",
        None,
        {
            "score_lookback_months": [1, 6],
            "crash_guardrail_drawdown_threshold": 15.0,
            "underperformance_guardrail_threshold": -10.0,
            "drawdown_guardrail_strategy_threshold": -35.0,
            "drawdown_guardrail_gap_threshold": 8.0,
        },
        runtime_options=RUNTIME_OPTIONS,
    )

    payload = project_single_settings_payload(workspace, _visible_draft(workspace))

    assert payload["score_return_columns"] == ["1MReturn", "6MReturn"]
    assert payload["score_weights"] == {"1MReturn": 1.0, "6MReturn": 1.0}
    assert payload["crash_guardrail_drawdown_threshold"] == 0.15
    assert payload["underperformance_guardrail_threshold"] == -0.1
    assert payload["drawdown_guardrail_strategy_threshold"] == -0.35
    assert payload["drawdown_guardrail_gap_threshold"] == 0.08


def test_risk_on_projection_derives_universe_and_dollar_volume_contract() -> None:
    workspace = build_single_settings_workspace(
        "Risk-On Momentum 5D",
        None,
        {
            "universe_mode": "top1000",
            "min_avg_dollar_volume_20d_m": 20.0,
            "macro_filter_mode": "off",
        },
        runtime_options=RUNTIME_OPTIONS,
    )

    payload = project_single_settings_payload(workspace, _visible_draft(workspace))

    assert payload["preset_name"] == "Top1000"
    assert payload["universe_limit"] == 1000
    assert payload["min_avg_dollar_volume_20d"] == 20_000_000.0
    assert payload["macro_filter_enabled"] is False


def test_tactical_default_values_match_current_renderer_defaults() -> None:
    gtaa = build_single_settings_workspace("GTAA", None, {}, RUNTIME_OPTIONS)
    grs = build_single_settings_workspace(
        "Global Relative Strength", None, {}, RUNTIME_OPTIONS
    )
    risk_on = build_single_settings_workspace(
        "Risk-On Momentum 5D", None, {}, RUNTIME_OPTIONS
    )
    gtaa_values = {field["field_id"]: field["value"] for field in _fields(gtaa)}
    grs_values = {field["field_id"]: field["value"] for field in _fields(grs)}
    risk_on_values = {field["field_id"]: field["value"] for field in _fields(risk_on)}

    assert gtaa_values["top"] == 3
    assert gtaa_values["interval"] == 1
    assert gtaa_values["score_lookback_months"] == [1, 3, 6, 12]
    assert gtaa_values["trend_filter_window"] == 200
    assert grs_values["top"] == 4
    assert grs_values["cash_ticker"] == "BIL"
    assert grs_values["trend_filter_window"] == 200
    assert risk_on_values["start"] == "2021-06-01"
    assert risk_on_values["start_balance"] == 10_000.0
    assert risk_on_values["max_holding_days"] == 5


@pytest.mark.parametrize(("strategy_choice", "variant"), tuple(STRICT_EXPECTED_KEYS))
def test_strict_variant_payload_has_exact_legacy_key_set(
    strategy_choice: str,
    variant: str,
) -> None:
    workspace = build_single_settings_workspace(
        strategy_choice,
        variant,
        {},
        runtime_options=RUNTIME_OPTIONS,
    )

    payload = project_single_settings_payload(workspace, _visible_draft(workspace))

    assert set(payload) == STRICT_EXPECTED_KEYS[(strategy_choice, variant)]


@pytest.mark.parametrize(
    ("strategy_choice", "variant", "strategy_key", "factor_freq", "snapshot_mode"),
    [
        (
            "Quality",
            "Annual",
            "quality_snapshot_strict_annual",
            "annual",
            "strict_statement_annual",
        ),
        (
            "Quality",
            "Quarterly",
            "quality_snapshot_strict_quarterly_prototype",
            "quarterly",
            "strict_statement_quarterly",
        ),
        (
            "Value",
            "Annual",
            "value_snapshot_strict_annual",
            "annual",
            "strict_statement_annual",
        ),
        (
            "Value",
            "Quarterly",
            "value_snapshot_strict_quarterly_prototype",
            "quarterly",
            "strict_statement_quarterly",
        ),
        (
            "Quality + Value",
            "Annual",
            "quality_value_snapshot_strict_annual",
            "annual",
            "strict_statement_annual",
        ),
        (
            "Quality + Value",
            "Quarterly",
            "quality_value_snapshot_strict_quarterly_prototype",
            "quarterly",
            "strict_statement_quarterly",
        ),
    ],
)
def test_strict_variant_projects_concrete_frequency_and_snapshot_contract(
    strategy_choice: str,
    variant: str,
    strategy_key: str,
    factor_freq: str,
    snapshot_mode: str,
) -> None:
    workspace = build_single_settings_workspace(
        strategy_choice,
        variant,
        {},
        runtime_options=RUNTIME_OPTIONS,
    )

    payload = project_single_settings_payload(workspace, _visible_draft(workspace))

    assert payload["strategy_key"] == strategy_key
    assert payload["factor_freq"] == factor_freq
    assert payload["snapshot_mode"] == snapshot_mode
    assert payload["universe_contract"] == "pit_monthly_snapshot"
    assert payload["dynamic_candidate_tickers"] == []
    expected_target = 300 if variant == "Annual" else 100
    assert payload["dynamic_target_size"] == expected_target


def test_strict_factor_arrays_and_rejection_mode_survive_projection() -> None:
    workspace = build_single_settings_workspace(
        "Quality + Value",
        "Annual",
        {
            "quality_factors": ["roe", "roa"],
            "value_factors": ["book_to_market", "earnings_yield"],
            "rejected_slot_handling_mode": "fill_then_retain_cash",
            "promotion_min_benchmark_coverage_pct": 95.0,
            "promotion_min_net_cagr_spread_pct": -2.0,
        },
        runtime_options=RUNTIME_OPTIONS,
    )

    payload = project_single_settings_payload(workspace, _visible_draft(workspace))

    assert payload["quality_factors"] == ["roe", "roa"]
    assert payload["value_factors"] == ["book_to_market", "earnings_yield"]
    assert payload["rejected_slot_fill_enabled"] is True
    assert payload["partial_cash_retention_enabled"] is True
    assert payload["promotion_min_benchmark_coverage"] == 0.95
    assert payload["promotion_min_net_cagr_spread"] == -0.02


def test_quality_snapshot_preserves_legacy_broad_replay_contract() -> None:
    workspace = build_single_settings_workspace(
        "Quality",
        "Snapshot",
        {},
        runtime_options=RUNTIME_OPTIONS,
    )

    payload = project_single_settings_payload(workspace, _visible_draft(workspace))

    assert payload["strategy_key"] == "quality_snapshot"
    assert payload["factor_freq"] == "annual"
    assert payload["rebalance_freq"] == "monthly"
    assert payload["snapshot_mode"] == "broad_research"
    assert payload["quality_factors"] == [
        "roe",
        "gross_margin",
        "operating_margin",
        "debt_ratio",
    ]


def test_strict_default_factor_and_overlay_values_match_current_renderers() -> None:
    workspace = build_single_settings_workspace(
        "Quality + Value",
        "Annual",
        {},
        runtime_options=RUNTIME_OPTIONS,
    )
    values = {field["field_id"]: field["value"] for field in _fields(workspace)}

    assert values["start"] == "2021-07-18"
    assert values["top"] == 10
    assert values["rebalance_interval"] == 1
    assert values["quality_factors"] == [
        "roe",
        "roa",
        "net_margin",
        "asset_turnover",
        "current_ratio",
    ]
    assert values["value_factors"] == [
        "book_to_market",
        "earnings_yield",
        "sales_yield",
        "ocf_yield",
        "operating_income_yield",
    ]
    assert values["trend_filter_enabled"] is False
    assert values["trend_filter_window"] == 200
    assert values["weighting_mode"] == "equal_weight"
    assert values["risk_off_mode"] == "cash_only"
