from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def _synthetic_panel(rows: int = 140) -> pd.DataFrame:
    origins = pd.date_range("1989-03-31", periods=rows, freq="QE", tz="UTC")
    result = []
    for index, origin in enumerate(origins):
        cycle = np.sin(index / 6.0)
        target = float(cycle < -0.55)
        values = {
            "unemployment_gap_pct": max(0.0, -cycle),
            "payroll_3m_pct": cycle,
            "claims_yoy_pct": -cycle * 8.0,
            "manufacturing_hours_3m_delta": cycle * 0.2,
            "temp_help_yoy_pct": cycle * 2.0,
            "industrial_production_3m_pct": cycle * 1.5,
            "real_income_6m_pct": cycle,
            "real_consumption_6m_pct": cycle * 0.8,
            "yield_curve_slope_pct": cycle * 0.6,
            "high_yield_oas_3m_delta_pct": -cycle * 0.4,
        }
        result.append(
            {
                "origin_at": origin.isoformat(),
                "target_available_at": (origin + pd.DateOffset(months=36)).isoformat(),
                "target_recession_12m": target,
                "complete_feature_ratio": 1.0,
                **values,
            }
        )
    current = dict(result[-1])
    current.update(
        {
            "origin_at": "2026-08-03T03:15:00Z",
            "target_available_at": None,
            "target_recession_12m": None,
        }
    )
    return pd.DataFrame([*result, current])


def test_recession_model_uses_delayed_chronological_labels_and_beats_baseline() -> None:
    from finance.inflation_policy_recession import (
        fit_recession_risk_model,
        predict_recession_risk,
    )

    artifact = fit_recession_risk_model(
        _synthetic_panel(),
        as_of_at="2026-08-03T03:15:00Z",
        model_version="inflation-policy-hybrid-v1",
        minimum_origins=60,
        minimum_training_rows=36,
        maximum_calibration_error=0.20,
    )
    result = predict_recession_risk(artifact, as_of_at="2026-08-03T03:15:00Z")

    assert artifact.publication_status == "READY"
    assert artifact.validation_metrics["brier"] < artifact.validation_metrics["baseline_brier"]
    assert artifact.validation_metrics["label_delay_months"] == pytest.approx(24.0)
    assert result.publication_status == "READY"
    assert result.probability_12m is not None and 0.0 <= result.probability_12m <= 1.0
    assert len(result.top_drivers) == 5


def test_recession_model_fails_closed_without_independent_origins() -> None:
    from finance.inflation_policy_recession import (
        fit_recession_risk_model,
        predict_recession_risk,
    )

    artifact = fit_recession_risk_model(
        _synthetic_panel(rows=20),
        as_of_at="2026-08-03T03:15:00Z",
        model_version="inflation-policy-hybrid-v1",
        minimum_origins=60,
    )
    result = predict_recession_risk(artifact, as_of_at="2026-08-03T03:15:00Z")

    assert artifact.publication_status == "NOT_AVAILABLE"
    assert result.probability_12m is None
    assert "insufficient_recession_origins" in result.reason_codes


def test_recession_module_never_imports_existing_cycle_results() -> None:
    from pathlib import Path
    import finance.inflation_policy_recession as module

    source = Path(module.__file__).read_text(encoding="utf-8")
    assert "economic_cycle" not in source
    assert "cycle_probability" not in source
