from __future__ import annotations

from dataclasses import dataclass

import pytest


def _save_command(**overrides: object) -> dict[str, object]:
    command: dict[str, object] = {
        "owner": "USER",
        "definition_name": "내 10년물 기준",
        "instrument": "DGS10",
        "zone_lower_pct": 4.68,
        "zone_upper_pct": 4.75,
        "buffer_pct": 0.05,
        "short_lookback_days": 63,
        "long_lookback_days": 504,
        "confirmation_count": 3,
        "confirmation_window": 5,
        "require_breakeven_confirmation": True,
        "exclude_term_premium_only": True,
        "as_of_at": "2026-08-02T00:00:00+00:00",
    }
    command.update(overrides)
    return command


def _reverse_command(**overrides: object) -> dict[str, object]:
    command: dict[str, object] = {
        "instrument": "DGS10",
        "zone_lower_pct": 4.68,
        "zone_upper_pct": 4.75,
        "buffer_pct": 0.05,
        "condition": "CONFIRMED",
        "hold_days": 3,
        "horizon_at": "2026-12-31T23:59:59+00:00",
        "as_of_at": "2026-08-02T00:00:00+00:00",
    }
    command.update(overrides)
    return command


def _snapshot() -> dict[str, object]:
    return {
        "as_of_at": "2026-08-02T00:00:00+00:00",
        "model_version": "inflation-policy-hybrid-v1",
        "publication_status": "READY",
        "freshness_json": {
            "trained_cutoff_at": "2026-08-02T00:00:00+00:00",
        },
        "equity_json": {
            "current_index_level": 6550.0,
            "base_forward_eps": 295.0,
            "measured_next_year_eps_revision_pct": 0.75,
            "scenario_feature_values": {
                "months_to_year_end": 5.0,
                "dgs2_pct": 3.65,
                "dgs10_pct": 4.55,
                "real_yield_10y_pct": 1.95,
                "breakeven_10y_pct": 2.35,
            },
        },
    }


def _artifact(*, path_count: int = 2) -> dict[str, object]:
    return {
        "model_version": "inflation-policy-hybrid-v1",
        "trained_cutoff_at": "2026-08-02T00:00:00+00:00",
                "component": "joint_macro_paths",
        "publication_status": "READY",
        "parameters_json": {
            "joint_rate_paths": [
                {
                    "path_id": f"path-{index}",
                    "weight": 1.0,
                    "q4_core_pce_pct": 3.5 + index * 0.1,
                    "remaining_monthly_mom_pct": [0.2, 0.3],
                    "policy_net_steps": index,
                    "year_end_policy_midpoint_pct": 3.625 + index * 0.25,
                    "rate_paths_pct": {
                        "DGS2": [3.7, 3.7 + index * 0.25],
                        "DGS10": [4.65, 4.70, 4.80],
                        "DFII10": [2.0, 2.1, 2.2],
                        "T10YIE": [2.4, 2.45, 2.5],
                    },
                }
                for index in range(path_count)
            ]
        },
        "validation_json": {
            "joint_path_publication_status": "READY",
            "reverse_minimum_supporting_paths": 1,
            "reverse_minimum_effective_paths": 1.0,
        },
    }


def test_save_command_cannot_claim_auto_owner() -> None:
    from app.services.overview.inflation_policy_commands import (
        save_user_resistance_definition,
    )

    with pytest.raises(ValueError, match="USER"):
        save_user_resistance_definition(_save_command(owner="AUTO"))


def test_save_command_persists_normalized_user_definition() -> None:
    from app.services.overview.inflation_policy_commands import (
        save_user_resistance_definition,
    )

    stored: list[dict[str, object]] = []
    result = save_user_resistance_definition(
        _save_command(),
        result_saver=lambda row: stored.append(dict(row)) or row["definition_id"],
        id_factory=lambda: "11111111-1111-4111-8111-111111111111",
        now_factory=lambda: "2026-08-02T01:00:00+00:00",
    )

    assert result["publication_status"] == "READY"
    assert result["definition"]["owner"] == "USER"
    assert result["definition"]["definition_id"] == "11111111-1111-4111-8111-111111111111"
    assert stored[0]["zone_lower_pct"] == 4.68
    assert stored[0]["zone_upper_pct"] == 4.75
    assert stored[0]["short_lookback_days"] == 63
    assert stored[0]["long_lookback_days"] == 504
    assert stored[0]["confirmation_profile_json"] == {
        "confirmation_count": 3,
        "confirmation_window": 5,
        "require_breakeven_confirmation": True,
        "exclude_term_premium_only": True,
    }


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"zone_lower_pct": 4.8, "zone_upper_pct": 4.7}, "하단"),
        ({"short_lookback_days": 90}, "63"),
        ({"confirmation_count": 6, "confirmation_window": 5}, "확인 횟수"),
    ],
)
def test_save_command_rejects_invalid_criterion(
    overrides: dict[str, object], message: str
) -> None:
    from app.services.overview.inflation_policy_commands import (
        save_user_resistance_definition,
    )

    with pytest.raises(ValueError, match=message):
        save_user_resistance_definition(_save_command(**overrides))


def test_reverse_command_uses_exact_snapshot_model_version_and_bounded_paths() -> None:
    from app.services.overview.inflation_policy_commands import (
        run_reverse_scenario_command,
    )

    artifact_requests: list[dict[str, object]] = []
    runner_inputs: list[dict[str, object]] = []

    def artifact_loader(**kwargs: object) -> dict[str, object]:
        artifact_requests.append(dict(kwargs))
        return _artifact(path_count=50_001)

    def scenario_runner(paths: object, target: object, **kwargs: object) -> dict[str, object]:
        runner_inputs.append(
            {"path_count": len(paths), "condition": target.condition, **kwargs}
        )
        return {
            "status": "AVAILABLE",
            "target_probability": 0.2,
            "supporting_path_count": 10_000,
            "effective_path_count": 8_000.0,
            "q4_core_pce_quantiles_pct": {"p50": 3.6},
            "required_remaining_mom_quantiles_pct": {"p50": 0.28},
            "policy_net_step_probabilities": {"hike_2": 0.8, "hold": 0.2},
            "year_end_policy_target_probabilities": {"4.1250": 0.8, "3.6250": 0.2},
        }

    result = run_reverse_scenario_command(
        _reverse_command(),
        snapshot_loader=lambda **_: _snapshot(),
        artifact_loader=artifact_loader,
        scenario_runner=scenario_runner,
    )

    assert result["publication_status"] == "READY"
    assert result["model_version"] == "inflation-policy-hybrid-v1"
    assert artifact_requests == [
        {
            "model_version": "inflation-policy-hybrid-v1",
            "trained_cutoff_at": "2026-08-02T00:00:00+00:00",
            "component": "joint_macro_paths",
        }
    ]
    assert runner_inputs[0]["path_count"] == 50_000
    assert runner_inputs[0]["condition"] == "BREAK"


def test_reverse_command_fails_closed_without_exact_ready_artifact() -> None:
    from app.services.overview.inflation_policy_commands import (
        run_reverse_scenario_command,
    )

    result = run_reverse_scenario_command(
        _reverse_command(),
        snapshot_loader=lambda **_: _snapshot(),
        artifact_loader=lambda **_: None,
        scenario_runner=lambda *_args, **_kwargs: pytest.fail("runner must not execute"),
    )

    assert result == {
        "publication_status": "NOT_AVAILABLE",
        "reason": "선택한 snapshot과 정확히 일치하는 검증 artifact가 없습니다.",
        "as_of_at": "2026-08-02T00:00:00+00:00",
        "model_version": "inflation-policy-hybrid-v1",
    }


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"condition": "BREAK"}, "REACH"),
        ({"zone_lower_pct": 3.0, "zone_upper_pct": 5.1}, "200bp"),
        ({"horizon_at": "2026-08-01T00:00:00+00:00"}, "horizon"),
    ],
)
def test_reverse_command_rejects_unbounded_or_invalid_target(
    overrides: dict[str, object], message: str
) -> None:
    from app.services.overview.inflation_policy_commands import (
        run_reverse_scenario_command,
    )

    with pytest.raises(ValueError, match=message):
        run_reverse_scenario_command(
            _reverse_command(**overrides),
            snapshot_loader=lambda **_: _snapshot(),
            artifact_loader=lambda **_: _artifact(),
        )


@dataclass(frozen=True)
class _SparseSummary:
    status: str = "NOT_AVAILABLE"
    target_probability: float = 0.01
    supporting_path_count: int = 2
    effective_path_count: float = 1.2
    q4_core_pce_quantiles_pct: None = None
    required_remaining_mom_quantiles_pct: None = None
    policy_net_step_probabilities: None = None
    year_end_policy_target_probabilities: None = None


def test_reverse_command_preserves_sparse_support_as_not_available() -> None:
    from app.services.overview.inflation_policy_commands import (
        run_reverse_scenario_command,
    )

    result = run_reverse_scenario_command(
        _reverse_command(),
        snapshot_loader=lambda **_: _snapshot(),
        artifact_loader=lambda **_: _artifact(),
        scenario_runner=lambda *_args, **_kwargs: _SparseSummary(),
    )

    assert result["publication_status"] == "NOT_AVAILABLE"
    assert result["supporting_path_count"] == 2
    assert result["effective_path_count"] == 1.2
    assert result["q4_core_pce_quantiles_pct"] is None


def test_equity_command_fails_closed_without_exact_ready_artifacts() -> None:
    from app.services.overview.inflation_policy_commands import (
        run_equity_stress_scenario_command,
    )

    snapshot = {
        "as_of_at": "2026-08-03T00:00:00Z",
        "model_version": "inflation-policy-v1",
        "freshness_json": {"trained_cutoff_at": "2026-07-31T00:00:00Z"},
    }

    result = run_equity_stress_scenario_command(
        {"target_level": 6400.0, "user_ai_eps_uplift_pct": 5.0},
        snapshot_loader=lambda **_kwargs: snapshot,
        artifact_loader=lambda **_kwargs: None,
    )

    assert result["publication_status"] == "NOT_AVAILABLE"
    assert "정확히 일치" in str(result["reason"])


def test_equity_command_validates_user_bounds_before_loading_artifacts() -> None:
    from app.services.overview.inflation_policy_commands import (
        run_equity_stress_scenario_command,
    )

    with pytest.raises(ValueError, match="AI EPS uplift"):
        run_equity_stress_scenario_command(
            {"target_level": 6400.0, "user_ai_eps_uplift_pct": 51.0},
            snapshot_loader=lambda **_kwargs: None,
            artifact_loader=lambda **_kwargs: None,
        )


def test_equity_command_requires_ready_joint_path_validation() -> None:
    from app.services.overview.inflation_policy_commands import (
        run_equity_stress_scenario_command,
    )

    snapshot = _snapshot()
    equity_artifact = {
        "model_version": snapshot["model_version"],
        "publication_status": "READY",
        "parameters_json": {
            "current_index_level": 6600.0,
            "base_forward_eps": 300.0,
            "artifact": {
                "eps_response": {"intercept": 0.0},
                "multiple_response": {"intercept": 0.0},
                "joint_residuals": [[0.0, 0.0]],
                "scenario_feature_values": {"months_to_year_end": 4.0},
                "latest_measured_next_year_eps_revision_pct": 1.0,
                "trained_through": "2025-12-31",
            },
        },
        "validation_json": {
            "publication_status": "READY",
            "publication_contract_version": "equity-stress-publication-v1",
        },
    }
    unverified_paths = _artifact()
    unverified_paths["validation_json"] = {
        "joint_path_publication_status": "LIMITED"
    }

    result = run_equity_stress_scenario_command(
        {"target_level": 6400.0, "user_ai_eps_uplift_pct": 5.0},
        snapshot_loader=lambda **_kwargs: snapshot,
        artifact_loader=lambda **kwargs: (
            equity_artifact
            if kwargs["component"] == "equity_stress"
            else unverified_paths
        ),
        scenario_runner=lambda *_args, **_kwargs: pytest.fail(
            "runner must not execute"
        ),
    )

    assert result["publication_status"] == "NOT_AVAILABLE"
    assert "공동 거시경로" in str(result["reason"])


def test_equity_command_runs_only_with_ready_joint_paths_and_live_context() -> None:
    from app.services.overview.inflation_policy_commands import (
        run_equity_stress_scenario_command,
    )

    snapshot = _snapshot()
    equity_artifact = {
        "model_version": snapshot["model_version"],
        "publication_status": "READY",
        "parameters_json": {
            "artifact": {
                "eps_response": {"intercept": 0.0},
                "multiple_response": {"intercept": 0.0},
                "joint_residuals": [[0.0, 0.0]],
                "scenario_feature_values": {},
                "latest_measured_next_year_eps_revision_pct": None,
                "trained_through": "2025-12-31",
            },
        },
        "validation_json": {
            "publication_status": "READY",
            "publication_contract_version": "equity-stress-publication-v1",
        },
    }

    requested_components: list[str] = []
    captured: dict[str, object] = {}

    def load_artifact(**kwargs):
        requested_components.append(str(kwargs["component"]))
        return equity_artifact if kwargs["component"] == "equity_stress" else _artifact(path_count=2)

    def run_scenario(*_args, **kwargs):
        captured.update(kwargs)
        return {
            "publication_status": "READY",
            "user_ai_eps_uplift_pct": kwargs["user_ai_eps_uplift_pct"],
            "threshold_probabilities": {"below_or_equal:6400.0000": 0.25},
        }

    result = run_equity_stress_scenario_command(
        {"target_level": 6400.0, "user_ai_eps_uplift_pct": 5.0},
        snapshot_loader=lambda **_kwargs: snapshot,
        artifact_loader=load_artifact,
        scenario_runner=run_scenario,
    )

    assert result["publication_status"] == "READY"
    assert result["as_of_at"] == snapshot["as_of_at"]
    assert result["user_ai_eps_uplift_pct"] == pytest.approx(5.0)
    assert "below_or_equal:6400.0000" in result["threshold_probabilities"]
    assert requested_components == ["equity_stress", "joint_macro_paths"]
    assert captured["current_index"] == pytest.approx(6550.0)
    assert captured["forward_eps"] == pytest.approx(295.0)
    assert captured["measured_next_year_eps_revision_pct"] == pytest.approx(0.75)
    assert captured["scenario_feature_values"] == snapshot["equity_json"][
        "scenario_feature_values"
    ]
