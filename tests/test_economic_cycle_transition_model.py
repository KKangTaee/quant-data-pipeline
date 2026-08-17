from __future__ import annotations

import json
import math

import numpy as np
import pandas as pd
import pytest


def _binary_log_loss(probabilities: np.ndarray, labels: np.ndarray) -> float:
    clipped = np.clip(probabilities, 1e-12, 1.0 - 1e-12)
    return float(
        -np.mean(labels * np.log(clipped) + (1.0 - labels) * np.log1p(-clipped))
    )


def _multiclass_log_loss(probabilities: np.ndarray, labels: np.ndarray) -> float:
    return float(-np.mean(np.log(np.clip(probabilities[np.arange(len(labels)), labels], 1e-12, 1.0))))


def test_weighted_binary_fit_is_deterministic_and_ranks_signal() -> None:
    from finance.economic_cycle_transition_model import (
        fit_binary_logit,
        predict_binary_probability,
    )

    rows = pd.DataFrame(
        {
            "signal": [-3.0, -2.0, -1.0, 1.0, 2.0, 3.0],
            "pressure_target": [0.0, 0.0, 0.0, 1.0, 1.0, 1.0],
            "episode_weight": [0.5, 0.5, 1.0, 1.0, 0.5, 0.5],
        }
    )

    first = fit_binary_logit(rows, ("signal",), l2=0.1)
    second = fit_binary_logit(rows, ("signal",), l2=0.1)
    probabilities = predict_binary_probability(first, rows)

    assert first.publication_status == "READY"
    assert probabilities[-1] > probabilities[0]
    assert json.dumps(first.to_dict(), sort_keys=True) == json.dumps(
        second.to_dict(), sort_keys=True
    )


def test_prediction_rejects_missing_required_feature() -> None:
    from finance.economic_cycle_transition_model import (
        ModelNotReadyError,
        fit_binary_logit,
        predict_binary_probability,
    )

    training = pd.DataFrame(
        {
            "signal": [-1.0, 1.0],
            "pressure_target": [0.0, 1.0],
            "episode_weight": [1.0, 1.0],
        }
    )
    artifact = fit_binary_logit(training, ("signal",))

    with pytest.raises(ModelNotReadyError, match="MISSING_MODEL_FEATURE"):
        predict_binary_probability(artifact, pd.DataFrame({"other": [1.0]}))


def test_multinomial_probabilities_are_complete_and_conditioned() -> None:
    from finance.economic_cycle_observed_state import PHASE_SEQUENCE
    from finance.economic_cycle_transition_model import (
        fit_multinomial_logit,
        predict_destination_probabilities,
    )

    centers = {
        "recovery": (-2.0, -2.0),
        "expansion": (2.0, 2.0),
        "slowdown": (2.0, -2.0),
        "contraction": (-2.0, 2.0),
    }
    records: list[dict[str, object]] = []
    for phase, (first, second) in centers.items():
        for offset in (-0.2, 0.0, 0.2):
            records.append(
                {
                    "first": first + offset,
                    "second": second - offset,
                    "destination_target": phase,
                    "episode_weight": 1.0 / 3.0,
                }
            )
    training = pd.DataFrame(records)
    artifact = fit_multinomial_logit(
        training,
        ("first", "second"),
        l2=0.01,
    )

    predictions = predict_destination_probabilities(
        artifact,
        pd.DataFrame({"first": [-2.0], "second": [-2.0]}),
        current_phases=("contraction",),
    )
    distribution = predictions[0]

    assert artifact.publication_status == "READY"
    assert tuple(distribution) == PHASE_SEQUENCE
    assert all(math.isfinite(value) for value in distribution.values())
    assert abs(sum(distribution.values()) - 1.0) < 1e-12
    assert distribution["contraction"] == 0.0
    assert distribution["recovery"] == max(distribution.values())


def test_binary_platt_scaling_does_not_worsen_wrong_overconfidence() -> None:
    from finance.economic_cycle_transition_model import fit_platt_scaler

    probabilities = np.asarray([0.99, 0.95, 0.05, 0.01], dtype=float)
    labels = np.asarray([0.0, 0.0, 1.0, 1.0], dtype=float)

    calibration = fit_platt_scaler(probabilities, labels)
    logits = np.log(probabilities / (1.0 - probabilities))
    calibrated = 1.0 / (
        1.0
        + np.exp(
            -(
                calibration["slope"] * logits
                + calibration["intercept"]
            )
        )
    )

    assert _binary_log_loss(calibrated, labels) <= _binary_log_loss(
        probabilities, labels
    ) + 1e-12


def test_multiclass_temperature_softens_wrong_overconfidence() -> None:
    from finance.economic_cycle_transition_model import fit_multiclass_temperature

    probabilities = np.asarray(
        [
            [0.10, 0.85, 0.03, 0.02],
            [0.02, 0.10, 0.85, 0.03],
            [0.03, 0.02, 0.10, 0.85],
            [0.85, 0.03, 0.02, 0.10],
        ],
        dtype=float,
    )
    labels = np.asarray([0, 1, 2, 3], dtype=int)

    calibration = fit_multiclass_temperature(probabilities, labels)
    temperature = calibration["temperature"]
    logits = np.log(probabilities) / temperature
    logits -= logits.max(axis=1, keepdims=True)
    calibrated = np.exp(logits)
    calibrated /= calibrated.sum(axis=1, keepdims=True)

    assert temperature > 1.0
    assert _multiclass_log_loss(calibrated, labels) <= _multiclass_log_loss(
        probabilities, labels
    ) + 1e-12


def test_missing_class_support_returns_limited_artifact() -> None:
    from finance.economic_cycle_transition_model import fit_multinomial_logit

    rows = pd.DataFrame(
        {
            "signal": [-1.0, 1.0],
            "destination_target": ["recovery", "expansion"],
            "episode_weight": [1.0, 1.0],
        }
    )

    artifact = fit_multinomial_logit(rows, ("signal",))

    assert artifact.publication_status == "LIMITED"
    assert artifact.reason_codes == ("MISSING_CLASS_SUPPORT",)


def test_multiclass_temperature_accepts_conditional_zero_for_current_phase() -> None:
    from finance.economic_cycle_transition_model import fit_multiclass_temperature

    probabilities = np.asarray(
        [
            [0.0, 0.70, 0.20, 0.10],
            [0.15, 0.0, 0.70, 0.15],
            [0.10, 0.15, 0.0, 0.75],
            [0.70, 0.15, 0.15, 0.0],
        ]
    )

    calibration = fit_multiclass_temperature(
        probabilities,
        np.asarray([1, 2, 3, 0]),
    )

    assert calibration["temperature"] > 0.0
