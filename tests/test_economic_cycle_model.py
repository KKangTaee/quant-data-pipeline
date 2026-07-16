from __future__ import annotations

import importlib
import importlib.util
import math
from dataclasses import replace

import pandas as pd

FEATURES = (
    "activity_score",
    "labor_income_score",
    "activity_momentum_3m",
    "labor_income_momentum_3m",
)
PHASES = ("recovery", "expansion", "slowdown", "recession")


def _load_module():
    spec = importlib.util.find_spec("finance.economic_cycle_model")
    assert spec is not None, "economic cycle model module must exist"
    return importlib.import_module("finance.economic_cycle_model")


def _cluster_fixture() -> tuple[pd.DataFrame, pd.Series]:
    centers = {
        "recovery": (-1.0, -1.0, 1.0, 1.0),
        "expansion": (1.0, 1.0, 1.0, 1.0),
        "slowdown": (1.0, 1.0, -1.0, -1.0),
        "recession": (-1.0, -1.0, -1.0, -1.0),
    }
    rows: list[dict[str, float]] = []
    labels: list[str] = []
    for phase, center in centers.items():
        for offset in (-0.1, 0.0, 0.1):
            rows.append(
                {
                    feature: value + offset
                    for feature, value in zip(FEATURES, center, strict=True)
                }
            )
            labels.append(phase)
    return pd.DataFrame(rows), pd.Series(labels)


def test_current_model_identifies_each_synthetic_phase_cluster() -> None:
    module = _load_module()
    features, labels = _cluster_fixture()
    artifact = module.fit_horizon_model(features, labels, horizon_months=0)

    assert artifact.publication_status == "READY"
    for phase, row_index in zip(PHASES, (1, 4, 7, 10), strict=True):
        probabilities = module.predict_phase_probabilities(
            artifact, features.iloc[row_index].to_dict()
        )
        assert max(probabilities, key=probabilities.get) == phase


def test_current_model_rejects_financial_or_inflation_features() -> None:
    module = _load_module()
    features, labels = _cluster_fixture()
    features["financial_leading_score"] = 0.0

    try:
        module.fit_horizon_model(features, labels, horizon_months=0)
    except ValueError as exc:
        assert "horizon 0" in str(exc)
        assert "financial_leading_score" in str(exc)
    else:
        raise AssertionError("horizon 0 must reject financial context features")


def test_absent_phase_support_returns_limited_artifact() -> None:
    module = _load_module()
    features, labels = _cluster_fixture()
    keep = labels != "recession"

    artifact = module.fit_horizon_model(
        features.loc[keep].reset_index(drop=True),
        labels.loc[keep].reset_index(drop=True),
        horizon_months=0,
    )

    assert artifact.publication_status == "LIMITED"
    assert artifact.reason_codes == ("MISSING_PHASE_SUPPORT",)
    assert artifact.phase_support["recession"] == 0


def test_probability_simplex_is_finite_with_constant_features() -> None:
    module = _load_module()
    rows = [{feature: 1.0 for feature in FEATURES} for _ in range(8)]
    labels = pd.Series([phase for phase in PHASES for _ in range(2)])
    artifact = module.fit_horizon_model(
        pd.DataFrame(rows), labels, horizon_months=0, minimum_variance=0.05
    )

    probabilities = module.predict_phase_probabilities(artifact, rows[0])

    assert set(probabilities) == set(PHASES)
    assert all(
        math.isfinite(value) and 0.0 <= value <= 1.0 for value in probabilities.values()
    )
    assert math.isclose(sum(probabilities.values()), 1.0, abs_tol=1e-12)


def test_explanation_contributions_reconcile_winner_runner_feature_log_odds() -> None:
    module = _load_module()
    features, labels = _cluster_fixture()
    artifact = module.fit_horizon_model(features, labels, horizon_months=0)
    row = features.iloc[4].to_dict()

    explanation = module.explain_phase_prediction(artifact, row)

    assert explanation["winner"] == "expansion"
    assert explanation["runner_up"] in set(PHASES) - {"expansion"}
    assert set(explanation["contributions"]) == set(FEATURES)
    assert math.isclose(
        sum(explanation["contributions"].values()),
        explanation["feature_log_odds_difference"],
        abs_tol=1e-12,
    )


def test_transition_prior_prefers_same_and_next_without_zero_probability() -> None:
    module = _load_module()

    matrix = module.estimate_transition_matrix([])

    next_phase = {
        "recovery": "expansion",
        "expansion": "slowdown",
        "slowdown": "recession",
        "recession": "recovery",
    }
    for phase in PHASES:
        row = matrix[phase]
        assert math.isclose(sum(row.values()), 1.0, abs_tol=1e-12)
        assert all(value > 0 for value in row.values())
        skipped = set(PHASES) - {phase, next_phase[phase]}
        assert row[phase] > max(row[target] for target in skipped)
        assert row[next_phase[phase]] > max(row[target] for target in skipped)


def test_forecast_models_use_direct_shifted_targets_for_horizon_two() -> None:
    module = _load_module()
    labels = pd.Series(
        [
            "recovery",
            "expansion",
            "slowdown",
            "recession",
            "expansion",
            "recovery",
            "recession",
            "slowdown",
            "expansion",
            "recovery",
        ]
    )
    panel = pd.DataFrame(
        {
            feature: [float((index % 4) - 1.5) for index in range(len(labels))]
            for feature in FEATURES
        }
    )
    panel["financial_leading_score"] = [float(index) for index in range(len(labels))]
    panel["inflation_policy_score"] = [float(-index) for index in range(len(labels))]

    models = module.fit_forecast_models(panel, labels)

    expected_h2 = labels.shift(-2).dropna().value_counts().to_dict()
    assert models[2].phase_support == {
        phase: int(expected_h2.get(phase, 0)) for phase in PHASES
    }
    assert models[2].feature_names == (
        *FEATURES,
        "financial_leading_score",
        "inflation_policy_score",
    )
    assert models[0].feature_names == FEATURES


def test_financial_context_changes_forecast_but_not_current_distribution() -> None:
    module = _load_module()
    current_features, labels = _cluster_fixture()
    current_artifact = module.fit_horizon_model(
        current_features, labels, horizon_months=0
    )

    forecast_features = current_features.copy()
    financial_centers = {
        "recovery": -3.0,
        "expansion": 3.0,
        "slowdown": 1.0,
        "recession": -1.0,
    }
    forecast_features["financial_leading_score"] = [
        financial_centers[label] for label in labels
    ]
    forecast_features["inflation_policy_score"] = 0.0
    forecast_artifact = module.fit_horizon_model(
        forecast_features, labels, horizon_months=1
    )

    base = current_features.iloc[4].to_dict()
    current_a = module.predict_phase_probabilities(current_artifact, base)
    current_b = module.predict_phase_probabilities(current_artifact, dict(base))
    forecast_a = module.predict_phase_probabilities(
        forecast_artifact,
        {**base, "financial_leading_score": 3.0, "inflation_policy_score": 0.0},
    )
    forecast_b = module.predict_phase_probabilities(
        forecast_artifact,
        {**base, "financial_leading_score": -3.0, "inflation_policy_score": 0.0},
    )

    assert current_a == current_b
    assert forecast_a != forecast_b


def test_log_space_likelihood_transition_blend_returns_simplex() -> None:
    module = _load_module()
    likelihood = {
        "recovery": 1e-200,
        "expansion": 0.7,
        "slowdown": 0.2,
        "recession": 0.1,
    }
    prior = {
        "recovery": 0.4,
        "expansion": 0.4,
        "slowdown": 0.1,
        "recession": 0.1,
    }

    blended = module.blend_likelihood_and_transition(
        likelihood, prior, likelihood_weight=0.7
    )

    assert set(blended) == set(PHASES)
    assert all(math.isfinite(value) and value > 0 for value in blended.values())
    assert math.isclose(sum(blended.values()), 1.0, abs_tol=1e-12)


def _log_loss(rows: list[dict[str, float]], targets: list[str]) -> float:
    return -sum(
        math.log(max(row[target], 1e-15))
        for row, target in zip(rows, targets, strict=True)
    ) / len(targets)


def test_temperature_softens_overconfident_wrong_predictions_and_improves_loss() -> (
    None
):
    module = _load_module()
    targets = list(PHASES)
    rows = []
    for index, _target in enumerate(targets):
        wrong = PHASES[(index + 1) % len(PHASES)]
        rows.append({phase: (0.97 if phase == wrong else 0.01) for phase in PHASES})

    temperature = module.fit_temperature(rows, targets)
    calibrated = [module.apply_temperature(row, temperature) for row in rows]

    assert temperature > 1.0
    assert _log_loss(calibrated, targets) <= _log_loss(rows, targets)


def test_temperature_grid_tie_chooses_smallest_value_deterministically() -> None:
    module = _load_module()
    uniform = [{phase: 0.25 for phase in PHASES} for _ in PHASES]

    first = module.fit_temperature(uniform, list(PHASES))
    second = module.fit_temperature(uniform, list(PHASES))

    assert first == second == 0.5


def test_horizon_artifacts_can_store_different_oof_temperatures() -> None:
    module = _load_module()
    features, labels = _cluster_fixture()
    artifacts = {
        horizon: module.fit_horizon_model(features, labels, horizon_months=horizon)
        for horizon in (0, 1, 2)
    }
    targets = list(PHASES)
    uniform = [{phase: 0.25 for phase in PHASES} for _ in targets]
    wrong = []
    for index in range(len(targets)):
        wrong_phase = PHASES[(index + 1) % len(PHASES)]
        wrong.append(
            {phase: (0.97 if phase == wrong_phase else 0.01) for phase in PHASES}
        )
    temperatures = {
        0: module.fit_temperature(uniform, targets),
        1: module.fit_temperature(wrong, targets),
        2: module.fit_temperature(uniform, targets, grid=(0.8, 1.0, 1.2)),
    }
    calibrated_artifacts = {
        horizon: replace(artifact, temperature=temperatures[horizon])
        for horizon, artifact in artifacts.items()
    }

    assert calibrated_artifacts[0].temperature == 0.5
    assert calibrated_artifacts[1].temperature > 1.0
    assert calibrated_artifacts[2].temperature == 0.8


def test_apply_temperature_preserves_phase_keys_order_and_simplex() -> None:
    module = _load_module()
    probabilities = {
        "recovery": 0.1,
        "expansion": 0.5,
        "slowdown": 0.3,
        "recession": 0.1,
    }

    calibrated = module.apply_temperature(probabilities, 1.7)

    assert tuple(calibrated) == PHASES
    assert max(calibrated, key=calibrated.get) == "expansion"
    assert all(math.isfinite(value) and value > 0 for value in calibrated.values())
    assert math.isclose(sum(calibrated.values()), 1.0, abs_tol=1e-12)
