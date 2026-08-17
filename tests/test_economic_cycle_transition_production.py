from __future__ import annotations

from types import SimpleNamespace

import pandas as pd

from finance.economic_cycle_observed_state import ObservedStateResult, PHASE_SEQUENCE
from finance.economic_cycle_transition_dataset import TransitionDataset
from finance.economic_cycle_transition_production import (
    TRANSITION_FORECAST_CONTRACT_VERSION,
    build_transition_production_forecast,
    publish_transition_production_forecast,
)
from finance.economic_cycle_transition_validation import TransitionPrediction


CORE_FEATURES = (
    "level",
    "momentum",
    "phase_duration",
    "positive_breadth",
    "phase_recovery",
    "phase_expansion",
    "phase_slowdown",
    "phase_contraction",
)
DRIVER_FEATURES = (
    "FEDFUNDS_delta_3m",
    "PCEPILFE_gap_2pct",
    "yield_curve_delta_3m",
    "BAA10Y_delta_3m",
    "PERMIT_change_6m_pct",
)


def _datasets() -> tuple[TransitionDataset, TransitionDataset]:
    rows: list[dict[str, object]] = []
    phases = tuple(PHASE_SEQUENCE)
    for index in range(16):
        current = phases[index % 4]
        destination = phases[(index + 1) % 4]
        row = {
            "forecast_origin": pd.Timestamp("2000-01-31") + pd.offsets.MonthEnd(index),
            "confirmed_phase": current,
            "raw_phase": current,
            "episode_id": index,
            "phase_duration": 1 + (index % 7),
            "level": -0.6 + index * 0.08,
            "momentum": -0.3 + index * 0.04,
            "positive_breadth": 0.30 + index * 0.03,
            "pressure_target": float(index % 3 == 0),
            "destination_target": destination,
            "target_known_at": pd.Timestamp("2001-07-31"),
            "destination_known_at": pd.Timestamp("2001-07-31"),
            "eligible": True,
            "episode_weight": 1.0,
            **{f"phase_{phase}": float(phase == current) for phase in phases},
            "FEDFUNDS_delta_3m": -0.5 + index * 0.08,
            "PCEPILFE_gap_2pct": -0.4 + index * 0.07,
            "yield_curve_delta_3m": 0.3 - index * 0.03,
            "BAA10Y_delta_3m": -0.2 + index * 0.04,
            "PERMIT_change_6m_pct": -4.0 + index * 0.5,
        }
        rows.append(row)
    current = {
        **rows[-1],
        "forecast_origin": pd.Timestamp("2026-07-31"),
        "confirmed_phase": "recovery",
        "raw_phase": "recovery",
        "episode_id": 16,
        "phase_duration": 7,
        "level": -0.25,
        "momentum": 0.12,
        "positive_breadth": 0.625,
        "pressure_target": None,
        "destination_target": None,
        "target_known_at": None,
        "destination_known_at": None,
        **{f"phase_{phase}": float(phase == "recovery") for phase in phases},
    }
    rows.append(current)
    frame = pd.DataFrame(rows)
    return (
        TransitionDataset(CORE_FEATURES, frame.copy()),
        TransitionDataset((*CORE_FEATURES, *DRIVER_FEATURES), frame.copy()),
    )


def _validation(task: str) -> SimpleNamespace:
    records = []
    phases = tuple(PHASE_SEQUENCE)
    for index in range(8):
        actual = float(index % 3 == 0) if task == "pressure" else phases[(index + 1) % 4]
        probabilities = (
            {"transition": 0.65 if actual == 1.0 else 0.25}
            if task == "pressure"
            else {phase: (0.7 if phase == actual else 0.1) for phase in phases}
        )
        records.append(
            TransitionPrediction(
                task=task,
                forecast_origin=pd.Timestamp("2010-01-31") + pd.offsets.MonthEnd(index),
                scoring_episode_id=index,
                training_episode_max=max(index - 1, 0),
                training_target_known_through=pd.Timestamp("2009-12-31"),
                actual=actual,
                model_probabilities=probabilities,
                baseline_probabilities={},
                weight=1.0,
                current_phase=phases[index % 4],
            )
        )
    return SimpleNamespace(
        pressure_predictions=tuple(records if task == "pressure" else ()),
        destination_predictions=tuple(records if task == "destination" else ()),
    )


def _stages() -> tuple[SimpleNamespace, SimpleNamespace, SimpleNamespace]:
    core, extended = _datasets()
    state = SimpleNamespace(
        core_panel=extended.rows.loc[:, [
            "forecast_origin",
            "level",
            "momentum",
        ]].assign(
            activity_score=lambda frame: frame["level"],
            labor_income_score=lambda frame: frame["momentum"],
            IPT_z=lambda frame: frame["level"],
            H_z=lambda frame: frame["level"] + 0.1,
            EMPLOY_z=lambda frame: frame["momentum"],
            RUC_z=lambda frame: frame["momentum"] + 0.1,
        ),
        raw_history=(
            ObservedStateResult(
                observed_state={
                    "as_of_date": "2026-07-31",
                    "phase": "recovery",
                    "level": -0.25,
                    "momentum": 0.12,
                    "data_status": "READY",
                },
                recent_changes=(),
                transition_monitor={},
            ),
        ),
        confirmed_state_frame=pd.DataFrame(
            [
                {
                    "forecast_origin": pd.Timestamp("2026-07-31"),
                    "confirmed_phase": "recovery",
                    "raw_phase": "recovery",
                    "candidate_phase": None,
                    "candidate_streak": 0,
                    "phase_duration": 7,
                }
            ]
        ),
        source_counts={"IPT": 10, "H": 10, "EMPLOY": 10, "RUC": 10},
    )
    driver = SimpleNamespace(core_dataset=core, extended_dataset=extended)
    feasibility = SimpleNamespace(
        status="GO",
        reason_codes=(),
        extended_validation=_validation("pressure"),
        core_validation=_validation("destination"),
    )
    return state, driver, feasibility


def test_build_transition_production_forecast_separates_pressure_and_destination() -> None:
    state, driver, feasibility = _stages()

    result = build_transition_production_forecast(
        "2026-07-31",
        state=state,
        driver=driver,
        feasibility=feasibility,
    )

    assert result.monitor["contract_version"] == TRANSITION_FORECAST_CONTRACT_VERSION
    assert result.monitor["current_phase"] == "recovery"
    assert 0.0 <= result.monitor["pressure"]["probability"] <= 1.0
    assert result.monitor["pressure"]["horizon_releases"] == 3
    probabilities = result.monitor["destination"]["probabilities"]
    assert probabilities["recovery"] == 0.0
    assert abs(sum(probabilities.values()) - 1.0) < 1e-9
    assert result.monitor["destination"]["primary_phase"] != "recovery"
    assert result.monitor["recent_phase_history"][-1]["phase"] == "recovery"
    assert [item["horizon_months"] for item in result.recent_changes] == [1, 3, 6]
    assert {item["driver_id"] for item in result.monitor["drivers"]} >= {
        "level",
        "momentum",
        "phase_duration",
        "positive_breadth",
        "phase_context",
        *DRIVER_FEATURES,
    }
    assert result.artifacts["pressure"]["feature_names"] == [*CORE_FEATURES, *DRIVER_FEATURES]
    assert result.artifacts["destination"]["feature_names"] == [*CORE_FEATURES]


def test_publish_transition_production_forecast_fails_closed_before_writes() -> None:
    state, driver, feasibility = _stages()
    feasibility.status = "NO_GO"
    writes: list[str] = []

    result = publish_transition_production_forecast(
        "2026-07-31",
        state_builder=lambda _: state,
        driver_builder=lambda _cutoff, _state: driver,
        feasibility_runner=lambda _date, **_kwargs: feasibility,
        artifact_writer=lambda _row: writes.append("artifact"),
        snapshot_writer=lambda _rows: writes.append("snapshot"),
    )

    assert result["status"] == "NO_GO"
    assert writes == []
