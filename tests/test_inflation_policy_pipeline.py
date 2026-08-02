from __future__ import annotations

import math
from datetime import date, timedelta


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
