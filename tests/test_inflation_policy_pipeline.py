from __future__ import annotations

import math
from datetime import date, timedelta

import pytest


def _month_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    year, month = 2019, 10
    level = 100.0
    index = 0
    while (year, month) <= (2026, 6):
        if index:
            mom = 0.22 + (0.04 if index % 4 == 0 else -0.02 if index % 3 == 0 else 0.0)
            level *= 1.0 + mom / 100.0
        rows.append(
            {
                "series_id": "PCEPILFE",
                "observation_date": f"{year:04d}-{month:02d}-01",
                "released_at": f"{year:04d}-{month:02d}-28 12:30:00",
                "value": level,
                "coverage_status": "actual",
            }
        )
        index += 1
        month += 1
        if month == 13:
            year += 1
            month = 1
    return rows


def _rate_rows() -> list[dict[str, object]]:
    recent_values = (
        4.10,
        4.20,
        4.35,
        4.55,
        4.30,
        4.18,
        4.25,
        4.40,
        4.60,
        4.42,
        4.30,
        4.38,
        4.50,
        4.62,
        4.58,
    )
    prefix_count = 505
    values = tuple(
        4.00 + 0.002 * (index % 7) for index in range(prefix_count)
    ) + recent_values
    start = date(2026, 7, 1) - timedelta(days=prefix_count)
    rows: list[dict[str, object]] = []
    for series_id, offset in (
        ("DGS10", 0.0),
        ("DGS2", -0.7),
        ("DFII10", -2.2),
        ("T10YIE", -2.0),
    ):
        for index, value in enumerate(values):
            observed = start + timedelta(days=index)
            rows.append(
                {
                    "series_id": series_id,
                    "observation_date": observed.isoformat(),
                    "released_at": f"{observed.isoformat()} 23:59:59",
                    "value": value + offset,
                    "coverage_status": "actual",
                }
            )
    return rows


def _sep_rows() -> list[dict[str, object]]:
    common = {
        "meeting_date": "2026-06-17",
        "released_at": "2026-06-17 18:00:00",
        "target_period": "2026",
    }
    core = [
        {
            **common,
            "variable_name": "core_pce",
            "distribution_kind": "HISTOGRAM",
            "bin_lower_pct": lower,
            "bin_upper_pct": upper,
            "participant_count": count,
        }
        for lower, upper, count in (
            (2.5, 2.6, 1),
            (3.1, 3.2, 3),
            (3.3, 3.4, 10),
            (3.5, 3.6, 4),
        )
    ]
    dots = [
        {
            **common,
            "variable_name": "federal_funds_rate",
            "distribution_kind": "DOT",
            "bin_value_pct": value,
            "participant_count": count,
        }
        for value, count in (
            (3.375, 1),
            (3.625, 8),
            (3.875, 3),
            (4.125, 5),
            (4.375, 1),
        )
    ]
    return core + dots


def _spf_probability_rows() -> list[dict[str, object]]:
    bins = (
        (1, ">=4.0", 4.0, None, 3.0),
        (2, "3.5-3.9", 3.5, 3.9, 23.0),
        (3, "3.0-3.4", 3.0, 3.4, 31.0),
        (4, "2.5-2.9", 2.5, 2.9, 27.0),
        (5, "2.0-2.4", 2.0, 2.4, 11.0),
        (6, "1.5-1.9", 1.5, 1.9, 4.0),
        (7, "1.0-1.4", 1.0, 1.4, 1.0),
        (8, "0.5-0.9", 0.5, 0.9, 0.0),
        (9, "0.0-0.4", 0.0, 0.4, 0.0),
        (10, "decline", None, 0.0, 0.0),
    )
    return [
        {
            "survey_year": 2026,
            "survey_quarter": 2,
            "target_year": 2026,
            "bin_number": number,
            "bin_label": label,
            "bin_lower_pct": lower,
            "bin_upper_pct": upper,
            "mean_probability_pct": probability,
            "released_at": "2026-05-16 03:59:59.999999",
        }
        for number, label, lower, upper, probability in bins
    ]


def _reaction_matrix():
    from finance.inflation_path import INFLATION_STATES
    from finance.policy_path import POLICY_NET_MOVE_BUCKETS

    matrix = {
        state: {bucket: 0.0 for bucket in POLICY_NET_MOVE_BUCKETS}
        for state in INFLATION_STATES
    }
    matrix["rapid_disinflation"].update({"cut_1": 0.6, "hold": 0.4})
    matrix["gradual_disinflation"].update({"cut_1": 0.3, "hold": 0.7})
    matrix["sticky"].update({"hold": 0.8, "hike_1": 0.2})
    matrix["reacceleration"].update({"hold": 0.3, "hike_1": 0.5, "hike_2": 0.2})
    matrix["shock_reacceleration"].update(
        {"hold": 0.2, "hike_1": 0.4, "hike_2": 0.3, "hike_3_plus": 0.1}
    )
    return matrix


def _momentum_artifact(*, publication_status: str = "LIMITED"):
    from finance.inflation_policy_pipeline import CorePCEMomentumArtifact

    return CorePCEMomentumArtifact(
        training_start_date="2019-10-01",
        trained_through_date="2026-06-01",
        trained_cutoff_at="2026-07-29T18:00:00+00:00",
        component_weights={
            "persistence": 1 / 3,
            "recent_3m": 1 / 3,
            "recent_6m": 1 / 3,
        },
        component_errors={
            "persistence": 0.10,
            "recent_3m": 0.10,
            "recent_6m": 0.10,
        },
        predictive_residuals_pct=(-0.10, 0.0, 0.10),
        validation_metrics={"rmse": 0.15, "origin_count": 48.0},
        publication_status=publication_status,
        publication_reasons=("fixture_limited",),
        latest_component_mom_pct={
            "persistence": 0.20,
            "recent_3m": 0.20,
            "recent_6m": 0.20,
        },
    )


def test_core_momentum_artifact_is_rolling_origin_and_baseline_gated() -> None:
    from finance.inflation_policy_pipeline import fit_core_pce_momentum_artifact
    from finance.inflation_policy_validation import PublicationThresholds

    artifact = fit_core_pce_momentum_artifact(
        _month_rows(),
        thresholds=PublicationThresholds(
            minimum_origins=24,
            minimum_complete_feature_ratio=0.95,
            maximum_calibration_error=0.30,
            require_baseline_improvement=True,
        ),
        minimum_history_months=24,
        max_component_weight=0.60,
    )

    assert artifact.training_start_date == "2019-10-01"
    assert artifact.trained_through_date == "2026-06-01"
    assert artifact.validation_metrics["origin_count"] >= 24
    baseline_scores = [
        artifact.validation_metrics["baseline_persistence_crps"],
        artifact.validation_metrics["baseline_rolling_3m_crps"],
        artifact.validation_metrics["baseline_rolling_6m_crps"],
    ]
    assert artifact.validation_metrics["baseline_crps"] == min(baseline_scores)
    assert math.isclose(sum(artifact.component_weights.values()), 1.0)
    assert max(artifact.component_weights.values()) <= 0.60 + 1e-12
    assert artifact.predictive_residuals_pct
    assert abs(sum(artifact.predictive_residuals_pct)) < 1e-12
    assert artifact.publication_status in {"READY", "LIMITED"}


def test_core_validation_does_not_count_same_release_revision_batch_as_origins() -> None:
    from finance.inflation_policy_pipeline import fit_core_pce_momentum_artifact
    from finance.inflation_policy_validation import PublicationThresholds

    revision_batch = [
        {**row, "released_at": "2026-06-25 12:30:00"}
        for row in _month_rows()
    ]

    artifact = fit_core_pce_momentum_artifact(
        revision_batch,
        thresholds=PublicationThresholds(
            minimum_origins=24,
            minimum_complete_feature_ratio=0.95,
            maximum_calibration_error=0.30,
            require_baseline_improvement=True,
        ),
        minimum_history_months=24,
        max_component_weight=0.60,
    )

    assert artifact.publication_status == "LIMITED"
    assert artifact.validation_metrics["origin_count"] == 0.0
    assert "insufficient_origins" in artifact.publication_reasons


def test_pipeline_materializes_compact_limited_snapshot_without_cycle_fallback() -> None:
    from finance.inflation_policy_pipeline import (
        InflationPolicyEngineConfig,
        materialize_inflation_policy_analysis,
    )
    from finance.inflation_policy_validation import PublicationThresholds
    from finance.loaders.inflation_policy import InflationPolicyDataBundle

    bundle = InflationPolicyDataBundle(
        as_of_at="2026-07-29T18:00:00+00:00",
        macro_rows=tuple(_month_rows() + _rate_rows()),
        sep_rows=tuple(_sep_rows()),
        decision_rows=(
            {
                "meeting_date": "2026-07-29",
                "released_at": "2026-07-29 18:00:00",
                "target_lower_before_pct": 3.5,
                "target_upper_before_pct": 3.75,
                "target_lower_after_pct": 3.5,
                "target_upper_after_pct": 3.75,
                "vote_for_count": 9,
                "vote_against_count": 3,
                "dissents_json": """[
                  {"preferred_action":"HIKE_25"},
                  {"preferred_action":"HIKE_25"},
                  {"preferred_action":"HIKE_25"}
                ]""",
            },
        ),
        term_premium_rows=(),
        coverage={
            "catalog_series_missing": [],
            "sep_status": "READY",
            "decision_status": "READY",
            "term_premium_status": "NOT_AVAILABLE",
        },
    )
    config = InflationPolicyEngineConfig(
        model_version="inflation-policy-fixture-v1",
        state_forecast_error_floor_pct=0.20,
        price_stability_target_pct=2.0,
        threshold_levels_pct=(3.4, 3.5, 3.6),
        reaction_matrix=_reaction_matrix(),
        policy_component_weights={"sep": 0.5, "economic": 0.5},
        next_action_component_weights={"committee": 1.0},
        max_component_weight=0.70,
        core_validation_thresholds=PublicationThresholds(
            minimum_origins=24,
            minimum_complete_feature_ratio=0.95,
            maximum_calibration_error=0.30,
            require_baseline_improvement=True,
        ),
    )

    result = materialize_inflation_policy_analysis(
        bundle,
        config=config,
        sample_count=400,
        seed=11,
        core_artifact=_momentum_artifact(),
    )

    assert result.snapshot_row["publication_status"] == "LIMITED"
    inflation = result.inflation
    policy = result.policy
    rates = result.rates
    assert inflation["publication_status"] == "LIMITED"
    assert inflation["reason"] == "q4_path_rolling_origin_validation_not_ready"
    assert math.isclose(sum(inflation["state_probabilities"].values()), 1.0)
    assert math.isclose(sum(policy["net_move_probabilities"].values()), 1.0)
    assert math.isclose(sum(policy["next_meeting_probabilities"].values()), 1.0)
    assert rates["DGS10"]["zones"]
    assert rates["DGS10"]["active_test_zone"] is not None
    assert "selection_reason" in rates["DGS10"]["active_test_zone"]
    if rates["DGS10"]["next_overhead_zone"] is not None:
        assert (
            rates["DGS10"]["next_overhead_zone"]["zone_lower_pct"]
            > rates["DGS10"]["current_value_pct"]
        )
    assert set(rates["instruments"]) == {"DGS2", "DGS10", "DFII10", "T10YIE"}
    assert rates["driver_decomposition"]["dominant_driver"] in {
        "inflation_driven",
        "policy_driven",
        "real_growth_driven",
        "term_premium_driven",
        "mixed",
    }
    assert rates["inflation_confirmation"] == {
        "status": "UNCONFIRMED",
        "reason": "prior_inflation_probability_not_available",
    }
    assert all(
        zone["zone_upper_pct"] != 4.7 or zone["zone_lower_pct"] != 4.7
        for zone in rates["DGS10"]["zones"]
    )
    assert result.reverse == {
        "publication_status": "NOT_AVAILABLE",
        "reason": "joint_rate_path_validation_not_ready",
    }
    assert "recession_model_not_available" in result.warnings
    assert "q4_path_rolling_origin_validation_not_ready" in result.warnings


def test_ready_policy_artifact_publishes_calibrated_next_and_year_end_paths() -> None:
    from finance.inflation_policy_pipeline import (
        build_limited_reference_config,
        materialize_inflation_policy_analysis,
    )
    from finance.loaders.inflation_policy import InflationPolicyDataBundle
    from finance.policy_validation import PolicyPathArtifact

    bundle = InflationPolicyDataBundle(
        as_of_at="2026-07-29T18:00:00+00:00",
        macro_rows=tuple(_month_rows() + _rate_rows()),
        sep_rows=tuple(_sep_rows()),
        decision_rows=(
            {
                "meeting_date": "2026-07-29",
                "released_at": "2026-07-29 18:00:00",
                "target_lower_before_pct": 3.5,
                "target_upper_before_pct": 3.75,
                "target_lower_after_pct": 3.5,
                "target_upper_after_pct": 3.75,
                "vote_for_count": 9,
                "vote_against_count": 3,
                "dissents_json": [
                    {"preferred_action": "HIKE_25"},
                    {"preferred_action": "HIKE_25"},
                    {"preferred_action": "HIKE_25"},
                ],
            },
        ),
        term_premium_rows=(),
        coverage={"term_premium_status": "NOT_AVAILABLE"},
    )
    artifact = PolicyPathArtifact(
        trained_cutoff_at=bundle.as_of_at,
        training_start_decision_date="2021-01-27",
        trained_through_decision_date="2026-07-29",
        next_meeting_smoothing=0.25,
        year_end_smoothing=0.05,
        next_meeting_validation={
            "origin_count": 37,
            "brier_score": 0.36,
            "baseline_brier_score": 0.39,
            "calibration_error": 0.07,
        },
        year_end_validation={
            "origin_count": 13,
            "brier_score": 0.60,
            "baseline_brier_score": 0.88,
            "calibration_error": 0.14,
        },
        publication_status="READY",
        reason_codes=(),
    )

    result = materialize_inflation_policy_analysis(
        bundle,
        config=build_limited_reference_config(model_version="policy-ready-v1"),
        sample_count=200,
        seed=13,
        core_artifact=_momentum_artifact(),
        policy_artifact=artifact,
    )

    assert result.policy["publication_status"] == "READY"
    assert result.policy["reason"] == "policy_rolling_origin_validated"
    assert result.policy["next_meeting_probabilities"] == pytest.approx(
        {"cut": 1 / 12, "hold": 31 / 48, "hike": 13 / 48}
    )
    assert math.isclose(sum(result.policy["net_move_probabilities"].values()), 1.0)
    assert result.policy["validation"]["next_meeting"]["origin_count"] == 37
    assert any(
        row["component"] == "policy_path" for row in result.model_artifact_rows
    )


def test_direct_q4_validation_publishes_spf_monthly_linear_pool() -> None:
    from finance.core_pce_q4 import CorePCEQ4Artifact
    from finance.inflation_policy_pipeline import (
        build_limited_reference_config,
        materialize_inflation_policy_analysis,
    )
    from finance.loaders.inflation_policy import InflationPolicyDataBundle

    bundle = InflationPolicyDataBundle(
        as_of_at="2026-07-29T18:00:00+00:00",
        macro_rows=tuple(_month_rows() + _rate_rows()),
        sep_rows=tuple(_sep_rows()),
        decision_rows=(
            {
                "meeting_date": "2026-07-29",
                "released_at": "2026-07-29 18:00:00",
                "target_lower_before_pct": 3.5,
                "target_upper_before_pct": 3.75,
                "target_lower_after_pct": 3.5,
                "target_upper_after_pct": 3.75,
                "vote_for_count": 12,
                "vote_against_count": 0,
                "dissents_json": "[]",
            },
        ),
        term_premium_rows=(),
        coverage={"spf_core_pce_status": "READY"},
        spf_rows=tuple(_spf_probability_rows()),
    )
    q4_artifact = CorePCEQ4Artifact(
        trained_cutoff_at=bundle.as_of_at,
        training_start_date="2018-01-01",
        trained_through_date="2025-12-31",
        model_weight=0.50,
        spf_weight=0.50,
        validation_metrics={
            "origin_count": 31.0,
            "target_year_count": 8.0,
            "crps": 0.36,
            "baseline_crps": 0.78,
            "calibration_error": 0.05,
        },
        publication_status="READY",
        publication_reasons=(),
    )

    result = materialize_inflation_policy_analysis(
        bundle,
        config=build_limited_reference_config(model_version="q4-ready-v1"),
        sample_count=400,
        seed=11,
        core_artifact=_momentum_artifact(),
        q4_artifact=q4_artifact,
    )

    assert result.inflation["publication_status"] == "READY"
    assert result.inflation["reason"] == "q4_direct_rolling_origin_validated"
    assert result.inflation["q4_component_weights"] == {
        "monthly_model": 0.5,
        "official_spf": 0.5,
    }
    assert result.inflation["validation"]["origin_count"] == 31.0
    assert math.isclose(sum(result.inflation["state_probabilities"].values()), 1.0)
    scenarios = result.inflation["next_release_scenarios"]
    assert [row["mom_pct"] for row in scenarios] == [0.1, 0.2, 0.3, 0.4, 0.5]
    assert all(row["inflation_publication_status"] == "READY" for row in scenarios)
    assert all(row["policy_publication_status"] == "LIMITED" for row in scenarios)
    assert all(row["hike_delta"] is None for row in scenarios)
    assert scenarios[0]["reacceleration_delta"] <= scenarios[-1]["reacceleration_delta"]
    assert "q4_path_rolling_origin_validation_not_ready" not in result.warnings
    assert {row["component"] for row in result.model_artifact_rows} == {
        "core_pce_momentum",
        "core_pce_q4_linear_pool",
    }


def test_ready_joint_paths_publish_reverse_and_policy_next_print_sensitivity() -> None:
    from finance.core_pce_q4 import CorePCEQ4Artifact
    from finance.inflation_policy_pipeline import (
        build_limited_reference_config,
        materialize_inflation_policy_analysis,
    )
    from finance.inflation_policy_simulation import SimulationPath
    from finance.joint_rate_paths import JointRatePathArtifact
    from finance.loaders.inflation_policy import InflationPolicyDataBundle
    from finance.policy_validation import PolicyPathArtifact

    bundle = InflationPolicyDataBundle(
        as_of_at="2026-07-29T18:00:00+00:00",
        macro_rows=tuple(_month_rows() + _rate_rows()),
        sep_rows=tuple(_sep_rows()),
        decision_rows=(
            {
                "meeting_date": "2026-07-29",
                "released_at": "2026-07-29 18:00:00",
                "target_lower_before_pct": 3.5,
                "target_upper_before_pct": 3.75,
                "target_lower_after_pct": 3.5,
                "target_upper_after_pct": 3.75,
                "vote_for_count": 9,
                "vote_against_count": 3,
                "dissents_json": [
                    {"preferred_action": "HIKE_25"},
                    {"preferred_action": "HIKE_25"},
                    {"preferred_action": "HIKE_25"},
                ],
            },
        ),
        term_premium_rows=(),
        coverage={"spf_core_pce_status": "READY"},
        spf_rows=tuple(_spf_probability_rows()),
    )
    q4_artifact = CorePCEQ4Artifact(
        trained_cutoff_at=bundle.as_of_at,
        training_start_date="2018-01-01",
        trained_through_date="2025-12-31",
        model_weight=0.5,
        spf_weight=0.5,
        validation_metrics={"origin_count": 31.0},
        publication_status="READY",
        publication_reasons=(),
    )
    policy_artifact = PolicyPathArtifact(
        trained_cutoff_at=bundle.as_of_at,
        training_start_decision_date="2021-01-27",
        trained_through_decision_date="2026-07-29",
        next_meeting_smoothing=0.25,
        year_end_smoothing=0.05,
        next_meeting_validation={"origin_count": 37},
        year_end_validation={"origin_count": 13},
        publication_status="READY",
        reason_codes=(),
    )
    paths = tuple(
        SimulationPath(
            path_id=f"path-{index}",
            weight=0.25,
            q4_core_pce_pct=3.0 + 0.3 * index,
            remaining_monthly_mom_pct=(0.15 + 0.1 * index,) * 6,
            policy_net_steps=index - 1,
            year_end_policy_midpoint_pct=3.625 + 0.25 * (index - 1),
            rate_paths_pct={
                "DGS2": (3.7, 3.8, 3.9, 4.0, 4.1),
                "DGS10": (4.6, 4.7, 4.8, 4.9, 5.0),
                "DFII10": (2.0, 2.1, 2.2, 2.3, 2.4),
                "T10YIE": (2.6, 2.6, 2.6, 2.6, 2.6),
            },
        )
        for index in range(4)
    )
    joint = JointRatePathArtifact(
        trained_cutoff_at=bundle.as_of_at,
        training_start_date="2016-01-29",
        trained_through_date="2025-12-31",
        current_observation_date="2026-07-29",
        rate_scales={key: 1.0 for key in ("DGS2", "DGS10", "DFII10", "T10YIE")},
        validation_metrics={
            "joint_path_publication_status": "READY",
            "reverse_minimum_supporting_paths": 1,
            "reverse_minimum_effective_paths": 1.0,
        },
        publication_status="READY",
        reason_codes=(),
        paths=paths,
    )

    result = materialize_inflation_policy_analysis(
        bundle,
        config=build_limited_reference_config(model_version="joint-ready-v1"),
        sample_count=200,
        seed=17,
        core_artifact=_momentum_artifact(),
        q4_artifact=q4_artifact,
        policy_artifact=policy_artifact,
        joint_path_builder=lambda **_kwargs: joint,
    )

    assert result.rates["publication_status"] == "READY"
    assert result.reverse["publication_status"] == "READY"
    dgs10 = result.rates["DGS10"]
    selected_zone = dgs10["next_overhead_zone"] or dgs10["active_test_zone"]
    assert selected_zone["breakout_probability"] is not None
    assert all(
        row["policy_publication_status"] == "READY"
        and row["hike_delta"] is not None
        for row in result.inflation["next_release_scenarios"]
    )
    assert any(
        row["component"] == "joint_macro_paths"
        for row in result.model_artifact_rows
    )


def test_equity_failure_is_stored_without_changing_macro_sections() -> None:
    from finance.inflation_policy_pipeline import (
        build_limited_reference_config,
        materialize_inflation_policy_analysis,
    )
    from finance.loaders.inflation_policy import InflationPolicyDataBundle

    bundle = InflationPolicyDataBundle(
        as_of_at="2026-07-29T18:00:00+00:00",
        macro_rows=tuple(_month_rows() + _rate_rows()),
        sep_rows=tuple(_sep_rows()),
        decision_rows=(
            {
                "meeting_date": "2026-07-29",
                "released_at": "2026-07-29 18:00:00",
                "target_lower_before_pct": 3.5,
                "target_upper_before_pct": 3.75,
                "target_lower_after_pct": 3.5,
                "target_upper_after_pct": 3.75,
                "vote_for_count": 12,
                "vote_against_count": 0,
                "dissents_json": "[]",
            },
        ),
        term_premium_rows=(),
        coverage={"term_premium_status": "NOT_AVAILABLE"},
    )
    equity = {
        "publication_status": "FAILED",
        "reason": "equity_component_exception:fixture",
        "index_quantiles": {},
        "eps_quantiles": {},
        "multiple_quantiles": {},
        "threshold_probabilities": {},
    }

    result = materialize_inflation_policy_analysis(
        bundle,
        config=build_limited_reference_config(model_version="equity-isolation-v1"),
        sample_count=100,
        seed=3,
        core_artifact=_momentum_artifact(),
        equity=equity,
        equity_joint_paths_ready=True,
    )

    assert result.inflation["publication_status"] == "LIMITED"
    assert result.policy["publication_status"] == "LIMITED"
    assert result.rates["publication_status"] == "LIMITED"
    assert result.equity == equity
    assert result.snapshot_row["equity_json"] == equity
    assert result.snapshot_row["publication_status"] == "LIMITED"


def test_pipeline_serializes_equity_stress_result_without_adapter() -> None:
    from finance.inflation_policy_equity_stress import EquityStressResult
    from finance.inflation_policy_pipeline import (
        build_limited_reference_config,
        materialize_inflation_policy_analysis,
    )
    from finance.loaders.inflation_policy import InflationPolicyDataBundle

    bundle = InflationPolicyDataBundle(
        as_of_at="2026-07-29T18:00:00+00:00",
        macro_rows=tuple(_month_rows() + _rate_rows()),
        sep_rows=tuple(_sep_rows()),
        decision_rows=(
            {
                "meeting_date": "2026-07-29",
                "released_at": "2026-07-29 18:00:00",
                "target_lower_before_pct": 3.5,
                "target_upper_before_pct": 3.75,
                "target_lower_after_pct": 3.5,
                "target_upper_after_pct": 3.75,
                "vote_for_count": 12,
                "vote_against_count": 0,
                "dissents_json": "[]",
            },
        ),
        term_premium_rows=(),
        coverage={"term_premium_status": "NOT_AVAILABLE"},
    )
    equity = EquityStressResult(
        as_of_at=bundle.as_of_at,
        index_quantiles={"p50": 6400.0},
        eps_quantiles={"p50": 320.0},
        multiple_quantiles={"p50": 20.0},
        threshold_probabilities={"6400": 0.50},
        target_decompositions={},
        measured_next_year_eps_revision_pct=1.5,
        user_ai_eps_uplift_pct=3.0,
        publication_status="READY",
        reason_codes=(),
        scenario_kind="conditional_stress",
        current_index_level=6600.0,
        base_forward_eps=310.0,
    )

    result = materialize_inflation_policy_analysis(
        bundle,
        config=build_limited_reference_config(model_version="equity-result-v1"),
        sample_count=100,
        seed=3,
        core_artifact=_momentum_artifact(),
        equity=equity,
        equity_joint_paths_ready=True,
    )

    assert result.equity["publication_status"] == "READY"
    assert result.equity["index_quantiles"] == {"p50": 6400.0}
    assert result.equity["reason_codes"] == ()
    assert result.snapshot_row["equity_json"] == result.equity


def test_pipeline_downgrades_ready_equity_without_verified_joint_paths() -> None:
    from finance.inflation_policy_equity_stress import EquityStressResult
    from finance.inflation_policy_pipeline import (
        build_limited_reference_config,
        materialize_inflation_policy_analysis,
    )
    from finance.loaders.inflation_policy import InflationPolicyDataBundle

    bundle = InflationPolicyDataBundle(
        as_of_at="2026-07-29T18:00:00+00:00",
        macro_rows=tuple(_month_rows() + _rate_rows()),
        sep_rows=tuple(_sep_rows()),
        decision_rows=(),
        term_premium_rows=(),
        coverage={},
    )
    equity = EquityStressResult(
        as_of_at=bundle.as_of_at,
        index_quantiles={"p50": 6400.0},
        eps_quantiles={"p50": 320.0},
        multiple_quantiles={"p50": 20.0},
        threshold_probabilities={"6400": 0.50},
        target_decompositions={},
        measured_next_year_eps_revision_pct=1.5,
        user_ai_eps_uplift_pct=0.0,
        publication_status="READY",
        reason_codes=(),
        scenario_kind="MODEL_BASE",
        current_index_level=6600.0,
        base_forward_eps=310.0,
    )

    result = materialize_inflation_policy_analysis(
        bundle,
        config=build_limited_reference_config(model_version="equity-gate-v1"),
        sample_count=100,
        seed=3,
        core_artifact=_momentum_artifact(),
        equity=equity,
    )

    assert result.equity["publication_status"] == "NOT_AVAILABLE"
    assert result.equity["index_quantiles"] == {}
    assert result.inflation["publication_status"] == "LIMITED"


def test_pipeline_returns_not_available_without_core_pce_history() -> None:
    from finance.inflation_policy_pipeline import (
        InflationPolicyEngineConfig,
        materialize_inflation_policy_analysis,
    )
    from finance.inflation_policy_validation import PublicationThresholds
    from finance.loaders.inflation_policy import InflationPolicyDataBundle

    config = InflationPolicyEngineConfig(
        model_version="fixture-v1",
        state_forecast_error_floor_pct=0.20,
        price_stability_target_pct=2.0,
        threshold_levels_pct=(3.5,),
        reaction_matrix=_reaction_matrix(),
        policy_component_weights={"sep": 0.5, "economic": 0.5},
        next_action_component_weights={"committee": 1.0},
        max_component_weight=0.70,
        core_validation_thresholds=PublicationThresholds(24, 0.95, 0.30, True),
    )
    bundle = InflationPolicyDataBundle(
        as_of_at="2026-07-29T18:00:00+00:00",
        macro_rows=tuple(_rate_rows()),
        sep_rows=tuple(_sep_rows()),
        decision_rows=(),
        term_premium_rows=(),
        coverage={},
    )

    result = materialize_inflation_policy_analysis(
        bundle,
        config=config,
        sample_count=100,
        seed=1,
        core_artifact=_momentum_artifact(),
    )

    assert result.snapshot_row["publication_status"] == "LIMITED"
    assert result.inflation["publication_status"] == "NOT_AVAILABLE"
    assert result.inflation["reason"] == "core_pce_current_levels_missing"
    assert result.policy["publication_status"] == "NOT_AVAILABLE"
    assert result.rates["publication_status"] == "LIMITED"
    assert result.rates["DGS10"]["zones"]


def test_pipeline_preserves_hybrid_component_evidence_in_model_artifact() -> None:
    from finance.inflation_policy_model import CorePCEHybridArtifact
    from finance.inflation_policy_pipeline import (
        InflationPolicyEngineConfig,
        materialize_inflation_policy_analysis,
    )
    from finance.inflation_policy_validation import PublicationThresholds
    from finance.loaders.inflation_policy import InflationPolicyDataBundle

    hybrid = CorePCEHybridArtifact(
        training_start_date="2017-07-01",
        trained_through_date="2026-06-01",
        trained_cutoff_at="2026-07-29T18:00:00+00:00",
        feature_names=("core_lag_1", "core_cpi_mom"),
        feature_means=(0.2, 0.25),
        feature_scales=(0.1, 0.2),
        ridge_coefficients=(0.2, 0.05, 0.1),
        ridge_alpha=1.0,
        bridge_weights={"core_lag_3_mean": 0.6, "core_cpi_mom": 0.4},
        component_weights={"bridge": 0.4, "ridge": 0.3, "momentum": 0.3},
        component_errors={"bridge": 0.1, "ridge": 0.09, "momentum": 0.12},
        predictive_residuals_pct=(-0.1, 0.0, 0.1),
        validation_metrics={"rmse": 0.15, "origin_count": 48.0},
        publication_status="LIMITED",
        publication_reasons=("calibration_error_too_high",),
        latest_component_mom_pct={"bridge": 0.22, "ridge": 0.24, "momentum": 0.23},
        latest_feature_values={"core_lag_1": 0.2, "core_cpi_mom": 0.1},
    )
    bundle = InflationPolicyDataBundle(
        as_of_at="2026-07-29T18:00:00+00:00",
        macro_rows=tuple(_month_rows() + _rate_rows()),
        sep_rows=tuple(_sep_rows()),
        decision_rows=(
            {
                "meeting_date": "2026-07-29",
                "released_at": "2026-07-29 18:00:00",
                "target_lower_before_pct": 3.5,
                "target_upper_before_pct": 3.75,
                "target_lower_after_pct": 3.5,
                "target_upper_after_pct": 3.75,
                "vote_for_count": 12,
                "vote_against_count": 0,
                "dissents_json": "[]",
            },
        ),
        term_premium_rows=(),
        coverage={"term_premium_status": "NOT_AVAILABLE"},
    )
    config = InflationPolicyEngineConfig(
        model_version="inflation-policy-hybrid-fixture-v1",
        state_forecast_error_floor_pct=0.20,
        price_stability_target_pct=2.0,
        threshold_levels_pct=(3.4, 3.5, 3.6),
        reaction_matrix=_reaction_matrix(),
        policy_component_weights={"sep": 0.5, "economic": 0.5},
        next_action_component_weights={"committee": 1.0},
        max_component_weight=0.70,
        core_validation_thresholds=PublicationThresholds(24, 0.95, 0.30, True),
    )

    result = materialize_inflation_policy_analysis(
        bundle,
        config=config,
        sample_count=400,
        seed=7,
        core_artifact=hybrid,
    )

    assert set(result.inflation["component_weights"]) == {
        "bridge",
        "ridge",
        "momentum",
    }
    stored = result.model_artifact_rows[0]
    assert stored["component"] == "core_pce_hybrid"
    assert stored["trained_cutoff_at"] == hybrid.trained_cutoff_at
    assert stored["feature_schema_version"] == "core-pce-hybrid-features-v1"
    assert stored["forecast_horizon"] == "one_month_core_pce_nowcast"
    assert stored["parameters_json"]["feature_names"] == hybrid.feature_names
    freshness = result.snapshot_row["freshness_json"]
    assert freshness["trained_through_date"] == "2026-06-01"
    assert freshness["macro_series"]["PCEPILFE"]["latest_observation_date"] == (
        "2026-06-01"
    )
    assert freshness["fomc_decisions"]["latest_released_at"] == (
        "2026-07-29T18:00:00+00:00"
    )
    assert freshness["max_released_at"] <= freshness["as_of_at"]


def test_pipeline_rejects_any_bundle_release_after_cutoff() -> None:
    from finance.inflation_policy_pipeline import (
        build_limited_reference_config,
        materialize_inflation_policy_analysis,
    )
    from finance.loaders.inflation_policy import InflationPolicyDataBundle

    future_row = {
        "series_id": "DGS10",
        "observation_date": "2026-07-29",
        "released_at": "2026-07-30 00:00:00",
        "value": 4.7,
    }
    bundle = InflationPolicyDataBundle(
        as_of_at="2026-07-29T18:00:00+00:00",
        macro_rows=tuple(_month_rows() + _rate_rows() + [future_row]),
        sep_rows=tuple(_sep_rows()),
        decision_rows=(),
        term_premium_rows=(),
        coverage={},
    )

    result = materialize_inflation_policy_analysis(
        bundle,
        config=build_limited_reference_config(model_version="future-release-v1"),
        sample_count=100,
        seed=1,
        core_artifact=_momentum_artifact(),
    )

    assert result.snapshot_row["publication_status"] == "NOT_AVAILABLE"
    assert result.inflation["reason"].startswith("freshness_not_available:")


def test_runner_performs_no_write_when_hybrid_training_is_unavailable() -> None:
    from finance.inflation_policy_pipeline import (
        build_limited_reference_config,
        run_inflation_policy_materialization,
    )
    from finance.loaders.inflation_policy import InflationPolicyDataBundle

    saved_artifacts: list[dict[str, object]] = []
    saved_snapshots: list[dict[str, object]] = []
    bundle = InflationPolicyDataBundle(
        as_of_at="2026-07-29T18:00:00+00:00",
        macro_rows=(),
        sep_rows=(),
        decision_rows=(),
        term_premium_rows=(),
        coverage={},
    )

    result = run_inflation_policy_materialization(
        as_of_at=bundle.as_of_at,
        history_start="2015-01-01",
        config=build_limited_reference_config(model_version="runner-test-v1"),
        run_kind="historical_replay",
        persist=True,
        bundle_loader=lambda **_kwargs: bundle,
        vintage_loader=lambda **_kwargs: (),
        artifact_saver=saved_artifacts.append,
        snapshot_saver=saved_snapshots.append,
    )

    assert result.snapshot_row["publication_status"] == "NOT_AVAILABLE"
    assert saved_artifacts == []
    assert saved_snapshots == []


def test_runner_materializes_and_persists_ready_equity_and_recession_components() -> None:
    import pandas as pd

    from finance.inflation_policy_equity_stress import EquityStressArtifact
    from finance.inflation_policy_recession import (
        RECESSION_FEATURES,
        RecessionRiskArtifact,
        RecessionRiskResult,
    )
    from finance.inflation_policy_pipeline import (
        build_limited_reference_config,
        run_inflation_policy_materialization,
    )
    from finance.loaders.inflation_policy import (
        InflationPolicyDataBundle,
        InflationPolicyEquityBundle,
    )

    bundle = InflationPolicyDataBundle(
        as_of_at="2026-07-29T18:00:00+00:00",
        macro_rows=tuple(_month_rows() + _rate_rows()),
        sep_rows=tuple(_sep_rows()),
        decision_rows=(),
        term_premium_rows=(),
        coverage={},
    )
    equity_bundle = InflationPolicyEquityBundle(
        as_of_at=bundle.as_of_at,
        price_rows=(),
        eps_rows=(),
        yield_rows=(),
        coverage={
            "verified_eps_vintage_status": "READY",
            "official_eps_vintage_status": "READY",
            "sp500_price_status": "READY",
            "yield_status": "READY",
        },
    )
    panel = pd.DataFrame(
        [
            {
                "origin_date": "2026-07-29",
                "current_index_level": 6600.0,
                "forward_eps": 300.0,
                "measured_next_year_eps_revision_pct": 1.5,
                "months_to_year_end": 5.0,
                "dgs10_pct": 4.4,
                "real_yield_10y_pct": 2.0,
                "breakeven_10y_pct": 2.4,
            }
        ]
    )
    equity_artifact = EquityStressArtifact(
        model_version="runner-equity-v1",
        eps_response={"intercept": 0.0},
        multiple_response={"intercept": 0.0},
        joint_residuals=((0.0, 0.0),),
        validation_metrics={
            "training_start_date": "2018-01-31",
            "publication_contract_version": "equity-stress-publication-v1",
            "maximum_coverage_80_error": 0.15,
        },
        trained_through="2025-12-31",
        publication_status="READY",
        reason_codes=(),
        latest_measured_next_year_eps_revision_pct=1.5,
        scenario_feature_values={
            "months_to_year_end": 5.0,
            "dgs2_pct": 3.7,
            "dgs10_pct": 4.4,
            "real_yield_10y_pct": 2.0,
            "breakeven_10y_pct": 2.4,
        },
    )
    recession_artifact = RecessionRiskArtifact(
        model_version="runner-equity-v1",
        feature_names=RECESSION_FEATURES,
        feature_means=tuple(0.0 for _ in RECESSION_FEATURES),
        feature_scales=tuple(1.0 for _ in RECESSION_FEATURES),
        coefficients=tuple(0.0 for _ in RECESSION_FEATURES),
        intercept=-1.0,
        validation_metrics={
            "training_start_date": "1989-03-31",
            "brier": 0.14,
            "baseline_brier": 0.16,
        },
        publication_status="READY",
        reason_codes=(),
        trained_through="2023-06-30",
    )
    recession_result = RecessionRiskResult(
        as_of_at=bundle.as_of_at,
        probability_12m=0.23,
        risk_state="WATCH",
        risk_label="관찰",
        horizon_months=12,
        top_drivers=(),
        publication_status="READY",
        reason_codes=(),
        validation_metrics=recession_artifact.validation_metrics,
    )
    joint_artifact = {
        "publication_status": "READY",
        "validation_json": {"joint_path_publication_status": "READY"},
        "parameters_json": {
            "joint_rate_paths": [
                {
                    "path_id": "central",
                    "weight": 1.0,
                    "q4_core_pce_pct": 3.5,
                    "remaining_monthly_mom_pct": [0.2, 0.3],
                    "policy_net_steps": 1,
                    "year_end_policy_midpoint_pct": 4.125,
                    "rate_paths_pct": {
                        "DGS2": [3.7, 3.95],
                        "DGS10": [4.4, 4.7],
                        "DFII10": [2.0, 2.2],
                        "T10YIE": [2.4, 2.5],
                    },
                }
            ]
        },
    }
    saved_artifacts: list[dict[str, object]] = []
    saved_snapshots: list[dict[str, object]] = []
    requested_joint_components: list[str] = []
    artifact_store: dict[tuple[str, str, str], dict[str, object]] = {
        (
            "runner-equity-v1",
            "2026-07-29T18:00:00+00:00",
            "joint_macro_paths",
        ): joint_artifact
    }

    def load_joint_artifact(**kwargs):
        requested_joint_components.append(str(kwargs["component"]))
        return artifact_store.get(
            (
                str(kwargs["model_version"]),
                str(kwargs["trained_cutoff_at"]),
                str(kwargs["component"]),
            )
        )

    def save_artifact(row):
        saved_artifacts.append(dict(row))
        artifact_store[
            (
                str(row["model_version"]),
                str(row["trained_cutoff_at"]),
                str(row["component"]),
            )
        ] = dict(row)

    result = run_inflation_policy_materialization(
        as_of_at=bundle.as_of_at,
        history_start="2015-01-01",
        config=build_limited_reference_config(model_version="runner-equity-v1"),
        run_kind="historical_replay",
        persist=True,
        bundle_loader=lambda **_kwargs: bundle,
        vintage_loader=lambda **_kwargs: (),
        artifact_trainer=lambda *_args, **_kwargs: _momentum_artifact(),
        recession_vintage_loader=lambda **_kwargs: ({"series_id": "USREC"},),
        recession_panel_builder=lambda *_args, **_kwargs: panel,
        recession_artifact_trainer=lambda *_args, **_kwargs: recession_artifact,
        recession_predictor=lambda *_args, **_kwargs: recession_result,
        equity_bundle_loader=lambda **_kwargs: equity_bundle,
        equity_panel_builder=lambda **_kwargs: panel,
        equity_artifact_trainer=lambda *_args, **_kwargs: equity_artifact,
        joint_path_artifact_loader=load_joint_artifact,
        artifact_saver=save_artifact,
        snapshot_saver=saved_snapshots.append,
    )

    repeated = run_inflation_policy_materialization(
        as_of_at=bundle.as_of_at,
        history_start="2015-01-01",
        config=build_limited_reference_config(model_version="runner-equity-v1"),
        run_kind="historical_replay",
        persist=True,
        bundle_loader=lambda **_kwargs: bundle,
        vintage_loader=lambda **_kwargs: (),
        artifact_trainer=lambda *_args, **_kwargs: _momentum_artifact(),
        recession_vintage_loader=lambda **_kwargs: ({"series_id": "USREC"},),
        recession_panel_builder=lambda *_args, **_kwargs: panel,
        recession_artifact_trainer=lambda *_args, **_kwargs: recession_artifact,
        recession_predictor=lambda *_args, **_kwargs: recession_result,
        equity_bundle_loader=lambda **_kwargs: equity_bundle,
        equity_panel_builder=lambda **_kwargs: panel,
        equity_artifact_trainer=lambda *_args, **_kwargs: equity_artifact,
        joint_path_artifact_loader=load_joint_artifact,
        artifact_saver=save_artifact,
        snapshot_saver=saved_snapshots.append,
    )

    assert result.equity["publication_status"] == "READY"
    assert result.equity["as_of_at"] == bundle.as_of_at
    assert result.equity["index_quantiles"]["p50"] == 6600.0
    assert {row["component"] for row in saved_artifacts} == {
        "core_pce_momentum",
        "equity_stress",
        "recession_risk",
    }
    assert repeated.equity["publication_status"] == "READY"
    assert requested_joint_components == ["joint_macro_paths", "joint_macro_paths"]
    assert artifact_store[
        (
            "runner-equity-v1",
            "2026-07-29T18:00:00+00:00",
            "joint_macro_paths",
        )
    ]["parameters_json"]["joint_rate_paths"]
    equity_saved = next(
        row for row in saved_artifacts if row["component"] == "equity_stress"
    )
    assert "current_index_level" not in equity_saved["parameters_json"]
    assert "base_forward_eps" not in equity_saved["parameters_json"]
    assert equity_saved["parameters_json"]["artifact"][
        "scenario_feature_values"
    ] == {}
    assert equity_saved["parameters_json"]["artifact"][
        "latest_measured_next_year_eps_revision_pct"
    ] is None
    assert saved_snapshots[0]["equity_json"]["publication_status"] == "READY"
    assert saved_snapshots[0]["equity_json"]["current_index_level"] == 6600.0
    assert saved_snapshots[0]["equity_json"]["scenario_feature_values"][
        "dgs10_pct"
    ] == 4.4
    assert saved_snapshots[0]["recession_json"]["probability_12m"] == 0.23
    assert result.recession["risk_state"] == "WATCH"


def test_reference_config_is_explicitly_limited_and_contains_no_absolute_yield() -> None:
    from finance.inflation_policy_pipeline import build_limited_reference_config

    config = build_limited_reference_config(model_version="reference-test-v1")

    assert config.model_version == "reference-test-v1"
    assert config.threshold_levels_pct == (3.4, 3.5, 3.6)
    assert all(
        math.isclose(sum(row.values()), 1.0)
        for row in config.reaction_matrix.values()
    )
    assert "4.7" not in repr(config)


def test_pipeline_cli_is_dry_run_unless_persist_is_explicit(monkeypatch, capsys) -> None:
    import finance.inflation_policy_pipeline as module

    captured: dict[str, object] = {}

    def run(**kwargs):
        captured.update(kwargs)
        return module.InflationPolicyMaterialization(
            snapshot_row={
                "as_of_at": kwargs["as_of_at"],
                "model_version": kwargs["config"].model_version,
                "publication_status": "LIMITED",
            },
            model_artifact_rows=(),
            inflation={"publication_status": "LIMITED"},
            policy={"publication_status": "LIMITED"},
            rates={"publication_status": "LIMITED"},
            reverse={"publication_status": "NOT_AVAILABLE"},
            equity={"publication_status": "NOT_AVAILABLE"},
            warnings=("fixture",),
        )

    monkeypatch.setattr(module, "run_inflation_policy_materialization", run)

    exit_code = module.main(
        [
            "--as-of-at",
            "2026-07-29T18:00:00+00:00",
            "--run-kind",
            "historical_replay",
        ]
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert captured["persist"] is False
    assert '"publication_status": "LIMITED"' in output


def test_pipeline_resistance_payload_replays_prior_state(monkeypatch) -> None:
    import finance.inflation_policy_pipeline as module
    from finance.yield_resistance import ResistanceZone

    zone = ResistanceZone(
        zone_lower_pct=4.70,
        zone_upper_pct=4.72,
        tolerance_pct=0.0,
        touch_count=2,
        timeframes=(63,),
        known_at_date="2026-07-01",
        as_of_date="2026-07-06",
        zone_strength=3.0,
    )
    monkeypatch.setattr(
        module,
        "build_dynamic_resistance_zones",
        lambda *_args, **_kwargs: (zone,),
    )
    rows = [
        {"observation_date": f"2026-07-{index + 1:02d}", "value": value}
        for index, value in enumerate((4.70, 4.73, 4.74, 4.75, 4.76, 4.65))
    ]

    payload = module._resistance_payload(rows)

    assert payload["zones"][0]["state"] == "FAILED"


def test_materializer_requires_an_explicit_pit_artifact() -> None:
    from finance.inflation_policy_pipeline import (
        build_limited_reference_config,
        materialize_inflation_policy_analysis,
    )
    from finance.loaders.inflation_policy import InflationPolicyDataBundle

    bundle = InflationPolicyDataBundle(
        as_of_at="2026-07-29T18:00:00+00:00",
        macro_rows=tuple(_month_rows() + _rate_rows()),
        sep_rows=tuple(_sep_rows()),
        decision_rows=(),
        term_premium_rows=(),
        coverage={},
    )

    result = materialize_inflation_policy_analysis(
        bundle,
        config=build_limited_reference_config(model_version="explicit-artifact-v1"),
        sample_count=100,
        seed=1,
    )

    assert result.snapshot_row["publication_status"] == "LIMITED"
    assert result.inflation["reason"] == "core_pce_pit_artifact_required"
    assert result.rates["publication_status"] == "LIMITED"


def test_runner_does_not_persist_a_failed_core_artifact() -> None:
    from finance.inflation_policy_model import CorePCEHybridArtifact
    from finance.inflation_policy_pipeline import (
        build_limited_reference_config,
        run_inflation_policy_materialization,
    )
    from finance.loaders.inflation_policy import InflationPolicyDataBundle

    failed = CorePCEHybridArtifact(
        training_start_date="2017-07-01",
        trained_through_date="2026-06-01",
        trained_cutoff_at="2026-07-29T18:00:00+00:00",
        feature_names=("core_lag_1",),
        feature_means=(0.2,),
        feature_scales=(0.1,),
        ridge_coefficients=(0.2, 0.0),
        ridge_alpha=1.0,
        bridge_weights={"core_lag_1": 1.0},
        component_weights={"bridge": 1 / 3, "ridge": 1 / 3, "momentum": 1 / 3},
        component_errors={"bridge": 0.1, "ridge": 0.1, "momentum": 0.1},
        predictive_residuals_pct=(-0.1, 0.0, 0.1),
        validation_metrics={"rmse": 0.15, "origin_count": 48.0},
        publication_status="FAILED",
        publication_reasons=("invalid_probability_or_metric",),
        latest_component_mom_pct={"bridge": 0.2, "ridge": 0.2, "momentum": 0.2},
        latest_feature_values={"core_lag_1": 0.2},
    )
    bundle = InflationPolicyDataBundle(
        as_of_at="2026-07-29T18:00:00+00:00",
        macro_rows=tuple(_month_rows() + _rate_rows()),
        sep_rows=tuple(_sep_rows()),
        decision_rows=(),
        term_premium_rows=(),
        coverage={},
    )
    saved_artifacts: list[dict[str, object]] = []
    saved_snapshots: list[dict[str, object]] = []

    result = run_inflation_policy_materialization(
        as_of_at=bundle.as_of_at,
        history_start="2015-01-01",
        config=build_limited_reference_config(model_version="failed-artifact-v1"),
        run_kind="historical_replay",
        persist=True,
        bundle_loader=lambda **_kwargs: bundle,
        vintage_loader=lambda **_kwargs: (),
        artifact_trainer=lambda *_args, **_kwargs: failed,
        artifact_saver=saved_artifacts.append,
        snapshot_saver=saved_snapshots.append,
    )

    assert result.snapshot_row["publication_status"] == "LIMITED"
    assert result.inflation["reason"] == "core_pce_artifact_not_publishable:FAILED"
    assert result.rates["publication_status"] == "LIMITED"
    assert saved_artifacts == []
    assert saved_snapshots == []


def test_runner_does_not_persist_an_artifact_trained_after_replay_cutoff() -> None:
    from dataclasses import replace

    from finance.inflation_policy_pipeline import (
        build_limited_reference_config,
        run_inflation_policy_materialization,
    )
    from finance.loaders.inflation_policy import InflationPolicyDataBundle

    future_trained = replace(
        _momentum_artifact(),
        trained_cutoff_at="2026-08-01T00:00:00+00:00",
    )
    bundle = InflationPolicyDataBundle(
        as_of_at="2026-07-29T18:00:00+00:00",
        macro_rows=tuple(_month_rows() + _rate_rows()),
        sep_rows=tuple(_sep_rows()),
        decision_rows=(),
        term_premium_rows=(),
        coverage={},
    )
    saved_artifacts: list[dict[str, object]] = []
    saved_snapshots: list[dict[str, object]] = []

    result = run_inflation_policy_materialization(
        as_of_at=bundle.as_of_at,
        history_start="2015-01-01",
        config=build_limited_reference_config(model_version="future-trained-v1"),
        run_kind="historical_replay",
        persist=True,
        bundle_loader=lambda **_kwargs: bundle,
        vintage_loader=lambda **_kwargs: (),
        artifact_trainer=lambda *_args, **_kwargs: future_trained,
        artifact_saver=saved_artifacts.append,
        snapshot_saver=saved_snapshots.append,
    )

    assert result.snapshot_row["publication_status"] == "LIMITED"
    assert result.inflation["reason"].startswith("freshness_not_available:")
    assert result.rates["publication_status"] == "LIMITED"
    assert saved_artifacts == []
    assert saved_snapshots == []


def test_runner_rejects_artifact_and_bundle_core_month_mismatch() -> None:
    from dataclasses import replace

    from finance.inflation_policy_pipeline import (
        build_limited_reference_config,
        run_inflation_policy_materialization,
    )
    from finance.loaders.inflation_policy import InflationPolicyDataBundle

    stale_artifact = replace(
        _momentum_artifact(),
        trained_through_date="2026-05-01",
    )
    bundle = InflationPolicyDataBundle(
        as_of_at="2026-07-29T18:00:00+00:00",
        macro_rows=tuple(_month_rows() + _rate_rows()),
        sep_rows=tuple(_sep_rows()),
        decision_rows=(),
        term_premium_rows=(),
        coverage={},
    )
    saved_artifacts: list[dict[str, object]] = []
    saved_snapshots: list[dict[str, object]] = []

    result = run_inflation_policy_materialization(
        as_of_at=bundle.as_of_at,
        history_start="2015-01-01",
        config=build_limited_reference_config(model_version="misaligned-artifact-v1"),
        run_kind="historical_replay",
        persist=True,
        bundle_loader=lambda **_kwargs: bundle,
        vintage_loader=lambda **_kwargs: (),
        artifact_trainer=lambda *_args, **_kwargs: stale_artifact,
        artifact_saver=saved_artifacts.append,
        snapshot_saver=saved_snapshots.append,
    )

    assert result.snapshot_row["publication_status"] == "LIMITED"
    assert result.inflation["reason"] == "core_pce_artifact_bundle_month_mismatch"
    assert result.rates["publication_status"] == "LIMITED"
    assert saved_artifacts == []
    assert saved_snapshots == []


def test_materializer_requires_exact_artifact_and_replay_cutoff_identity() -> None:
    from dataclasses import replace

    from finance.inflation_policy_pipeline import (
        build_limited_reference_config,
        materialize_inflation_policy_analysis,
    )
    from finance.loaders.inflation_policy import InflationPolicyDataBundle

    stale_cutoff = replace(
        _momentum_artifact(),
        trained_cutoff_at="2026-07-01T00:00:00+00:00",
    )
    bundle = InflationPolicyDataBundle(
        as_of_at="2026-07-29T18:00:00+00:00",
        macro_rows=tuple(_month_rows() + _rate_rows()),
        sep_rows=tuple(_sep_rows()),
        decision_rows=(),
        term_premium_rows=(),
        coverage={},
    )

    result = materialize_inflation_policy_analysis(
        bundle,
        config=build_limited_reference_config(model_version="stale-cutoff-v1"),
        sample_count=100,
        seed=1,
        core_artifact=stale_cutoff,
    )

    assert result.snapshot_row["publication_status"] == "LIMITED"
    assert result.inflation["reason"].startswith("freshness_not_available:")
    assert result.rates["publication_status"] == "LIMITED"
