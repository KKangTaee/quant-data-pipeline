"""Canonical RTDSM core state features and semantic publication gate."""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass

import pandas as pd

from finance.economic_cycle_observed_state import (
    PHASE_SEQUENCE,
    ObservedStateResult,
    phase_from_coordinates,
)
from finance.economic_cycle_transition_feasibility import (
    TransitionFeasibilityReport,
)


LEVEL_SIDE = {
    "recovery": "below",
    "contraction": "below",
    "expansion": "above",
    "slowdown": "above",
}


@dataclass(frozen=True)
class CoreStateGate:
    """Pre-registered semantic and revision-stability requirements."""

    minimum_phase_occupancy: float = 0.08
    maximum_phase_occupancy: float = 0.50
    maximum_one_month_episode_fraction: float = 0.25
    minimum_revision_overlap: int = 96
    minimum_revision_phase_agreement: float = 0.60
    minimum_revision_level_side_agreement: float = 0.80
    minimum_nber_recession_months: int = 12
    minimum_nber_below_side_fraction: float = 0.65
    minimum_nber_peaks: int = 3
    minimum_nber_peak_capture_rate: float = 0.70
    minimum_nber_troughs: int = 3
    minimum_nber_trough_capture_rate: float = 0.70


DEFAULT_CORE_STATE_GATE = CoreStateGate()


@dataclass(frozen=True)
class CoreStateAuditReport:
    """Auditable decision for using the long state as canonical truth."""

    status: str
    reason_codes: tuple[str, ...]
    usable_origins: int
    phase_origin_counts: dict[str, int]
    phase_occupancy: dict[str, float]
    episode_count: int
    one_month_episode_fraction: float
    revision_overlap: int
    revision_phase_agreement: float
    revision_level_side_agreement: float
    nber_recession_months: int
    nber_below_side_fraction: float
    nber_peak_count: int
    nber_peak_capture_rate: float
    nber_trough_count: int
    nber_trough_capture_rate: float
    sample_status: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _finite(value: object) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def build_core_feature_panel(panel: pd.DataFrame) -> pd.DataFrame:
    """Add canonical level, momentum, changes, breadth, and raw phase."""

    output = panel.copy().reset_index(drop=True)
    output["forecast_origin"] = pd.to_datetime(
        output.get("forecast_origin"), errors="coerce"
    )
    numeric_columns = (
        "IPT_z",
        "H_z",
        "EMPLOY_z",
        "RUC_z",
        "activity_score",
        "labor_income_score",
    )
    for column in numeric_columns:
        output[column] = pd.to_numeric(output.get(column), errors="coerce")
    output["raw_level"] = (
        0.5 * output["activity_score"] + 0.5 * output["labor_income_score"]
    )
    output["level"] = output["raw_level"].rolling(3, min_periods=3).mean()
    output["momentum"] = output["level"].diff(3)
    for lag in (1, 3, 6):
        output[f"level_change_{lag}m"] = output["level"].diff(lag)
        output[f"momentum_change_{lag}m"] = output["momentum"].diff(lag)
    output["activity_labor_dispersion"] = (
        output["activity_score"] - output["labor_income_score"]
    ).abs()
    z_columns = ["IPT_z", "H_z", "EMPLOY_z", "RUC_z"]
    z_values = output[z_columns]
    output["positive_breadth"] = z_values.ge(0.0).mean(axis=1).where(
        z_values.notna().all(axis=1)
    )

    phases: list[str | None] = []
    durations: list[int] = []
    previous_phase: str | None = None
    duration = 0
    for row in output.to_dict(orient="records"):
        level = _finite(row.get("level"))
        momentum = _finite(row.get("momentum"))
        status = str(row.get("data_status") or "UNAVAILABLE")
        phase = (
            phase_from_coordinates(level, momentum)
            if level is not None and momentum is not None and status != "UNAVAILABLE"
            else None
        )
        if phase is not None and phase == previous_phase:
            duration += 1
        elif phase is not None:
            duration = 1
        else:
            duration = 0
        phases.append(phase)
        durations.append(duration)
        previous_phase = phase
    output["phase"] = phases
    output["phase_duration"] = durations
    return output


def _usable_phase_map(
    history: Sequence[ObservedStateResult],
) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in history:
        state = item.observed_state
        phase = str(state.get("phase") or "")
        date_text = str(state.get("as_of_date") or "")
        if (
            phase in PHASE_SEQUENCE
            and date_text
            and state.get("data_status") != "UNAVAILABLE"
        ):
            result[date_text] = phase
    return result


def _episode_lengths(phases: Sequence[str]) -> list[int]:
    lengths: list[int] = []
    previous: str | None = None
    current = 0
    for phase in phases:
        if phase == previous:
            current += 1
        else:
            if current:
                lengths.append(current)
            previous = phase
            current = 1
    if current:
        lengths.append(current)
    return lengths


def _normalized_nber(
    values: Mapping[str, object],
) -> dict[pd.Timestamp, bool]:
    result: dict[pd.Timestamp, bool] = {}
    for raw_date, raw_value in values.items():
        parsed = pd.Timestamp(raw_date)
        result[parsed.to_period("M").to_timestamp("M").normalize()] = bool(raw_value)
    return dict(sorted(result.items()))


def _capture_rate(
    anchors: Sequence[pd.Timestamp],
    phases: Mapping[pd.Timestamp, str],
    *,
    before: int,
    after: int,
    accepted: frozenset[str],
) -> float:
    if not anchors:
        return 0.0
    captured = 0
    for anchor in anchors:
        window = {
            (anchor + pd.offsets.MonthEnd(offset)).normalize()
            for offset in range(-before, after + 1)
        }
        if any(phases.get(month) in accepted for month in window):
            captured += 1
    return captured / len(anchors)


def evaluate_core_state_gate(
    core_panel: pd.DataFrame,
    core_history: Sequence[ObservedStateResult],
    revised_history: Sequence[ObservedStateResult],
    *,
    nber_months: Mapping[str, object],
    sample_report: TransitionFeasibilityReport,
    gate: CoreStateGate = DEFAULT_CORE_STATE_GATE,
) -> CoreStateAuditReport:
    """Evaluate distribution, revision stability, and NBER semantics."""

    core = _usable_phase_map(core_history)
    revised = _usable_phase_map(revised_history)
    ordered_dates = sorted(core)
    ordered_phases = [core[item] for item in ordered_dates]
    counts = Counter(ordered_phases)
    usable = len(ordered_phases)
    phase_counts = {phase: int(counts.get(phase, 0)) for phase in PHASE_SEQUENCE}
    occupancy = {
        phase: (phase_counts[phase] / usable if usable else 0.0)
        for phase in PHASE_SEQUENCE
    }
    episodes = _episode_lengths(ordered_phases)
    one_month_fraction = (
        sum(length == 1 for length in episodes) / len(episodes) if episodes else 0.0
    )

    overlap = sorted(set(core) & set(revised))
    exact = sum(core[item] == revised[item] for item in overlap)
    side = sum(LEVEL_SIDE[core[item]] == LEVEL_SIDE[revised[item]] for item in overlap)
    revision_phase = exact / len(overlap) if overlap else 0.0
    revision_side = side / len(overlap) if overlap else 0.0

    nber = _normalized_nber(nber_months)
    core_by_month = {
        pd.Timestamp(date_text).to_period("M").to_timestamp("M").normalize(): phase
        for date_text, phase in core.items()
    }
    recession_months = [month for month, active in nber.items() if active and month in core_by_month]
    below = sum(
        LEVEL_SIDE[core_by_month[month]] == "below" for month in recession_months
    )
    below_fraction = below / len(recession_months) if recession_months else 0.0
    nber_items = list(nber.items())
    peaks = [
        month
        for index, (month, active) in enumerate(nber_items)
        if index > 0 and active and not nber_items[index - 1][1]
    ]
    troughs = [
        month
        for index, (month, active) in enumerate(nber_items)
        if index > 0 and not active and nber_items[index - 1][1]
    ]
    peak_rate = _capture_rate(
        peaks,
        core_by_month,
        before=6,
        after=3,
        accepted=frozenset({"slowdown", "contraction"}),
    )
    trough_rate = _capture_rate(
        troughs,
        core_by_month,
        before=3,
        after=6,
        accepted=frozenset({"recovery"}),
    )

    reasons: list[str] = []
    latest_ready = (
        not core_panel.empty
        and str(core_panel.iloc[-1].get("data_status") or "UNAVAILABLE")
        != "UNAVAILABLE"
    )
    if not latest_ready:
        reasons.append("INCOMPLETE_SOURCE_COVERAGE")
    if any(
        value < gate.minimum_phase_occupancy
        or value > gate.maximum_phase_occupancy
        for value in occupancy.values()
    ):
        reasons.append("PHASE_OCCUPANCY")
    if one_month_fraction > gate.maximum_one_month_episode_fraction:
        reasons.append("ONE_MONTH_EPISODES")
    if len(overlap) < gate.minimum_revision_overlap:
        reasons.append("INSUFFICIENT_REVISION_OVERLAP")
    if revision_phase < gate.minimum_revision_phase_agreement:
        reasons.append("REVISION_PHASE_INSTABILITY")
    if revision_side < gate.minimum_revision_level_side_agreement:
        reasons.append("REVISION_SIDE_INSTABILITY")
    if len(recession_months) < gate.minimum_nber_recession_months:
        reasons.append("INSUFFICIENT_NBER_RECESSION_MONTHS")
    if below_fraction < gate.minimum_nber_below_side_fraction:
        reasons.append("NBER_RECESSION_SEMANTICS")
    if len(peaks) < gate.minimum_nber_peaks:
        reasons.append("INSUFFICIENT_NBER_PEAKS")
    if peak_rate < gate.minimum_nber_peak_capture_rate:
        reasons.append("NBER_PEAK_CAPTURE")
    if len(troughs) < gate.minimum_nber_troughs:
        reasons.append("INSUFFICIENT_NBER_TROUGHS")
    if trough_rate < gate.minimum_nber_trough_capture_rate:
        reasons.append("NBER_TROUGH_CAPTURE")
    if sample_report.status != "GO_EXPERIMENT":
        reasons.append("SAMPLE_GATE_FAILED")

    return CoreStateAuditReport(
        status="NO_GO_CORE_STATE" if reasons else "READY",
        reason_codes=tuple(reasons),
        usable_origins=usable,
        phase_origin_counts=phase_counts,
        phase_occupancy=occupancy,
        episode_count=len(episodes),
        one_month_episode_fraction=one_month_fraction,
        revision_overlap=len(overlap),
        revision_phase_agreement=revision_phase,
        revision_level_side_agreement=revision_side,
        nber_recession_months=len(recession_months),
        nber_below_side_fraction=below_fraction,
        nber_peak_count=len(peaks),
        nber_peak_capture_rate=peak_rate,
        nber_trough_count=len(troughs),
        nber_trough_capture_rate=trough_rate,
        sample_status=sample_report.status,
    )
