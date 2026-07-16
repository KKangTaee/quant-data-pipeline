from __future__ import annotations

import importlib
import importlib.util
import math

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
    assert all(math.isfinite(value) and 0.0 <= value <= 1.0 for value in probabilities.values())
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
