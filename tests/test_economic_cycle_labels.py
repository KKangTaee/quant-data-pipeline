from __future__ import annotations

import importlib
import importlib.util

import pandas as pd


def _load_module():
    spec = importlib.util.find_spec("finance.economic_cycle_labels")
    assert spec is not None, "economic cycle label module must exist"
    return importlib.import_module("finance.economic_cycle_labels")


def test_label_phase_covers_quadrants_recession_override_and_zero_ties() -> None:
    module = _load_module()

    assert module.label_phase(-1, -1, 1, 1, 0) == "recovery"
    assert module.label_phase(1, 1, 1, 1, 0) == "expansion"
    assert module.label_phase(1, 1, -1, -1, 0) == "slowdown"
    assert module.label_phase(-1, -1, -1, -1, 0) == "recession"
    assert module.label_phase(1, 1, 1, 1, 1) == "recession"
    assert module.label_phase(0, 0, 0, 0, 0) == "expansion"


def test_financial_and_inflation_context_cannot_change_phase_labels() -> None:
    module = _load_module()
    base = pd.DataFrame(
        [
            {
                "forecast_origin": "2020-01-31",
                "activity_score": 0.8,
                "labor_income_score": 0.6,
                "activity_momentum_3m": -0.4,
                "labor_income_momentum_3m": -0.2,
                "financial_leading_score": 4.0,
                "inflation_policy_score": -4.0,
                "USREC_signal": 0.0,
            }
        ]
    )
    mutated = base.copy()
    mutated["financial_leading_score"] = -4.0
    mutated["inflation_policy_score"] = 4.0

    assert module.build_retrospective_phase_labels(base).tolist() == ["slowdown"]
    assert module.build_retrospective_phase_labels(mutated).tolist() == ["slowdown"]


def test_missing_real_economy_factor_does_not_forward_fill_phase() -> None:
    module = _load_module()
    panel = pd.DataFrame(
        [
            {
                "activity_score": 1.0,
                "labor_income_score": 1.0,
                "activity_momentum_3m": 1.0,
                "labor_income_momentum_3m": 1.0,
                "USREC_signal": 0.0,
            },
            {
                "activity_score": None,
                "labor_income_score": 1.0,
                "activity_momentum_3m": 1.0,
                "labor_income_momentum_3m": 1.0,
                "USREC_signal": 0.0,
            },
        ]
    )

    labels = module.build_retrospective_phase_labels(panel)

    assert labels.iloc[0] == "expansion"
    assert pd.isna(labels.iloc[1])


def test_later_recession_revision_cannot_rewrite_historical_origin_fit_labels() -> None:
    module = _load_module()
    early = {
        "forecast_origin": "2020-03-31",
        "activity_score": 0.5,
        "labor_income_score": 0.5,
        "activity_momentum_3m": -0.2,
        "labor_income_momentum_3m": -0.2,
        "USREC_signal": 0.0,
        "USREC_latest_observation_date": "2020-03-01",
    }
    later_revision = {
        **early,
        "forecast_origin": "2021-01-31",
        "USREC_signal": 1.0,
        "USREC_latest_observation_date": "2020-03-01",
    }

    before = module.build_retrospective_phase_labels(pd.DataFrame([early]))
    after = module.build_retrospective_phase_labels(
        pd.DataFrame([early, later_revision]), label_as_of_date="2020-03-31"
    )

    assert before.iloc[0] == "slowdown"
    assert after.iloc[0] == before.iloc[0]
    assert pd.isna(after.iloc[1])


def test_label_frame_derives_three_month_real_factor_momentum() -> None:
    module = _load_module()
    panel = pd.DataFrame(
        {
            "forecast_origin": pd.date_range("2020-01-31", periods=4, freq="ME"),
            "activity_score": [-1.0, -0.8, -0.6, -0.2],
            "labor_income_score": [-1.0, -0.9, -0.7, -0.3],
            "USREC_signal": [0.0, 0.0, 0.0, 0.0],
        }
    )

    label_frame = module.build_phase_label_frame(panel)

    assert label_frame.loc[3, "activity_momentum_3m"] == 0.8
    assert label_frame.loc[3, "labor_income_momentum_3m"] == 0.7
    assert label_frame.loc[3, "phase"] == "recovery"
    assert label_frame.loc[3, "label_reason"] == "negative_level_positive_momentum"
