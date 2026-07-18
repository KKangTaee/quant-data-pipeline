from __future__ import annotations

from copy import deepcopy

import pytest

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
    "Risk Parity": (None,),
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
        }
    },
    "tickers": ["VIG", "SCHD", "DGRO", "GLD", "SPY"],
    "benchmarks": ["SPY", "ACWI"],
}


def _fields(workspace: dict[str, object]) -> list[dict[str, object]]:
    return [
        field
        for section in workspace["sections"]
        for field in section["fields"]
    ]


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
        ({"universe_mode": "manual", "tickers": "VIG"}, "tickers", "목록"),
        (
            {"universe_mode": "manual", "tickers": ["VIG", "VIG"]},
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
    assert payload["option"] == "backtest"
    assert payload["universe_mode"] == "preset"
    assert "unknown" not in payload
    assert "tickers" not in payload
