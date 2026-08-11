"""Research-only RTDSM long-history state and readiness audit."""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass
from datetime import date

import pandas as pd

from finance.data.philadelphia_rtdsm import get_rtdsm_catalog
from finance.economic_cycle_features import fit_expanding_robust_scale
from finance.economic_cycle_observed_state import (
    ObservedStateResult,
    PHASE_SEQUENCE,
    phase_from_coordinates,
)
from finance.economic_cycle_transition_feasibility import (
    DEFAULT_SAMPLE_GATE,
    TransitionFeasibilityReport,
    TransitionSampleGate,
    evaluate_transition_sample_feasibility,
)


# Kept local so this research module cannot accidentally import the forecast model phases.
APPROVED_PHASES = frozenset(PHASE_SEQUENCE)
LEVEL_SIDE = {
    "recovery": "below",
    "contraction": "below",
    "expansion": "above",
    "slowdown": "above",
}


@dataclass(frozen=True)
class RtdsmParityGate:
    """Minimum common-period equivalence before model experimentation."""

    minimum_overlap_months: int
    minimum_phase_agreement: float
    minimum_kappa: float
    minimum_level_side_agreement: float


DEFAULT_PARITY_GATE = RtdsmParityGate(
    minimum_overlap_months=96,
    minimum_phase_agreement=0.60,
    minimum_kappa=0.40,
    minimum_level_side_agreement=0.75,
)


@dataclass(frozen=True)
class RtdsmParityReport:
    """Common-period comparison with the production observed-state labels."""

    status: str
    reason_codes: tuple[str, ...]
    overlap_months: int
    first_overlap_at: str | None
    last_overlap_at: str | None
    phase_agreement: float
    cohens_kappa: float
    level_side_agreement: float
    confusion_counts: dict[str, int]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class RtdsmReadinessReport:
    """Combined sample and parity decision without publication side effects."""

    status: str
    reason_codes: tuple[str, ...]
    source_complete: bool
    sample_report: TransitionFeasibilityReport
    parity_report: RtdsmParityReport

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "reason_codes": list(self.reason_codes),
            "source_complete": self.source_complete,
            "sample_report": self.sample_report.to_dict(),
            "parity_report": self.parity_report.to_dict(),
        }


def _finite(value: object) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def _annualized_log_change(
    current: float,
    previous: float,
    *,
    months: int,
) -> float | None:
    if current <= 0.0 or previous <= 0.0:
        return None
    return math.expm1(math.log(current / previous) * (12.0 / months)) * 100.0


def _transform_signal(
    transform: str,
    direction: int,
    series: pd.Series,
) -> float | None:
    if series.empty:
        return None
    values = pd.to_numeric(series, errors="coerce").dropna().sort_index()
    if values.empty:
        return None
    current_period = values.index.max()
    current = _finite(values.loc[current_period])
    if current is None:
        return None
    if transform == "annualized_log_change_6m":
        lag = 6
        previous = _finite(values.get(current_period - lag))
        signal = (
            _annualized_log_change(current, previous, months=lag)
            if previous is not None
            else None
        )
    elif transform == "annualized_log_change_3m":
        lag = 3
        previous = _finite(values.get(current_period - lag))
        signal = (
            _annualized_log_change(current, previous, months=lag)
            if previous is not None
            else None
        )
    elif transform == "level_change_3m":
        previous = _finite(values.get(current_period - 3))
        signal = current - previous if previous is not None else None
    else:
        raise ValueError(f"Unsupported RTDSM transform: {transform}")
    return signal * int(direction) if signal is not None else None


def _normalized_origins(
    forecast_origins: Iterable[str | date | pd.Timestamp],
) -> list[pd.Timestamp]:
    origins: list[pd.Timestamp] = []
    for value in forecast_origins:
        parsed = pd.Timestamp(value)
        if parsed.tzinfo is not None:
            parsed = parsed.tz_convert(None)
        origins.append(parsed.normalize())
    return sorted(dict.fromkeys(origins))


def build_rtdsm_monthly_panel(
    vintage_rows: Iterable[dict[str, object]],
    *,
    forecast_origins: Iterable[str | date | pd.Timestamp],
    minimum_history_months: int = 60,
) -> pd.DataFrame:
    """Build the four-indicator origin panel from eligible RTDSM vintages."""

    specs = {item.series_id: item for item in get_rtdsm_catalog()}
    source = pd.DataFrame(list(vintage_rows))
    if source.empty:
        source = pd.DataFrame(
            columns=[
                "series_id",
                "observation_date",
                "realtime_start",
                "realtime_end",
                "value",
            ]
        )
    for column in ("observation_date", "realtime_start", "realtime_end"):
        source[column] = pd.to_datetime(source.get(column), errors="coerce")
    source["series_id"] = source.get("series_id", "").astype(str).str.upper()
    source["value"] = pd.to_numeric(source.get("value"), errors="coerce")
    source = source.dropna(
        subset=["observation_date", "realtime_start", "realtime_end", "value"]
    )

    versions: dict[str, list[tuple[pd.Timestamp, pd.Timestamp, pd.Series]]] = {}
    for series_id, series_frame in source.groupby("series_id", sort=False):
        if series_id not in specs:
            continue
        items: list[tuple[pd.Timestamp, pd.Timestamp, pd.Series]] = []
        for realtime_start, frame in series_frame.groupby(
            "realtime_start", sort=True
        ):
            realtime_end = pd.Timestamp(frame["realtime_end"].max()).normalize()
            deduplicated = frame.sort_values("observation_date").drop_duplicates(
                "observation_date", keep="last"
            )
            indexed = pd.Series(
                deduplicated["value"].to_numpy(),
                index=deduplicated["observation_date"].dt.to_period("M"),
                dtype="float64",
            )
            indexed.index = pd.PeriodIndex(indexed.index, freq="M")
            items.append(
                (pd.Timestamp(realtime_start).normalize(), realtime_end, indexed)
            )
        versions[series_id] = items

    records: list[dict[str, object]] = []
    for origin in _normalized_origins(forecast_origins):
        record: dict[str, object] = {"forecast_origin": origin}
        for series_id, spec in specs.items():
            eligible = [
                item
                for item in versions.get(series_id, [])
                if item[0] <= origin <= item[1]
            ]
            if not eligible:
                record[f"{series_id}_signal"] = None
                record[f"{series_id}_latest_observation_date"] = None
                record[f"{series_id}_stale"] = True
                continue
            realtime_start, _realtime_end, values = max(
                eligible, key=lambda item: item[0]
            )
            allowed = values[values.index <= origin.to_period("M")]
            record[f"{series_id}_signal"] = _transform_signal(
                spec.transform,
                spec.direction,
                allowed,
            )
            if allowed.empty:
                record[f"{series_id}_latest_observation_date"] = None
                record[f"{series_id}_stale"] = True
            else:
                latest_period = allowed.index.max()
                latest_date = latest_period.to_timestamp(how="start").date()
                record[f"{series_id}_latest_observation_date"] = (
                    latest_date.isoformat()
                )
                threshold = 120 if spec.vintage_frequency == "quarterly" else 75
                record[f"{series_id}_stale"] = (
                    origin.date() - latest_date
                ).days > threshold
            record[f"{series_id}_vintage_date"] = realtime_start.date().isoformat()
        records.append(record)

    panel = pd.DataFrame(records)
    for series_id in specs:
        signal_column = f"{series_id}_signal"
        panel[f"{series_id}_z"] = fit_expanding_robust_scale(
            panel.get(signal_column, pd.Series(dtype="float64")).tolist(),
            minimum_history=int(minimum_history_months),
        )
    panel["activity_score"] = panel[["IPT_z", "H_z"]].mean(
        axis=1, skipna=False
    )
    panel["labor_income_score"] = panel[["EMPLOY_z", "RUC_z"]].mean(
        axis=1, skipna=False
    )
    all_z = panel[["IPT_z", "H_z", "EMPLOY_z", "RUC_z"]].notna().all(axis=1)
    any_stale = panel[
        ["IPT_stale", "H_stale", "EMPLOY_stale", "RUC_stale"]
    ].fillna(True).astype(bool).any(axis=1)
    panel["data_status"] = "UNAVAILABLE"
    panel.loc[all_z, "data_status"] = "READY"
    panel.loc[all_z & any_stale, "data_status"] = "LIMITED"
    return panel


def build_rtdsm_observed_history(
    panel: pd.DataFrame,
) -> tuple[ObservedStateResult, ...]:
    """Map the research panel to four quadrants without production writes."""

    if panel.empty:
        return ()
    prepared = panel.copy()
    prepared["forecast_origin"] = pd.to_datetime(
        prepared["forecast_origin"], errors="coerce"
    )
    prepared = prepared.dropna(subset=["forecast_origin"]).sort_values(
        "forecast_origin"
    ).reset_index(drop=True)
    activity = pd.to_numeric(prepared["activity_score"], errors="coerce")
    labor = pd.to_numeric(prepared["labor_income_score"], errors="coerce")
    prepared["_raw_level"] = 0.5 * activity + 0.5 * labor
    prepared["_level"] = prepared["_raw_level"].rolling(3, min_periods=3).mean()
    prepared["_momentum"] = prepared["_level"].diff(3)

    results: list[ObservedStateResult] = []
    for index in prepared.index:
        level = _finite(prepared.at[index, "_level"])
        momentum = _finite(prepared.at[index, "_momentum"])
        base_status = str(prepared.at[index, "data_status"])
        ready = (
            base_status != "UNAVAILABLE"
            and level is not None
            and momentum is not None
        )
        phase = phase_from_coordinates(level, momentum) if ready else None
        status = base_status if ready else "UNAVAILABLE"
        results.append(
            ObservedStateResult(
                observed_state={
                    "as_of_date": prepared.at[
                        index, "forecast_origin"
                    ].date().isoformat(),
                    "phase": phase,
                    "data_status": status,
                    "level": level,
                    "momentum": momentum,
                    "activity_score": _finite(
                        prepared.at[index, "activity_score"]
                    ),
                    "labor_income_score": _finite(
                        prepared.at[index, "labor_income_score"]
                    ),
                    "source": "philadelphia_fed_rtdsm",
                },
                recent_changes=(),
                transition_monitor={},
            )
        )
    return tuple(results)


def _usable_phase_map(
    history: Sequence[ObservedStateResult],
) -> dict[str, str]:
    output: dict[str, str] = {}
    for item in history:
        state = item.observed_state
        phase = str(state.get("phase") or "")
        as_of_date = str(state.get("as_of_date") or "")
        if (
            phase in APPROVED_PHASES
            and as_of_date
            and state.get("data_status") != "UNAVAILABLE"
        ):
            output[as_of_date] = phase
    return output


def evaluate_rtdsm_parity(
    rtdsm_history: Sequence[ObservedStateResult],
    current_history: Sequence[ObservedStateResult],
    *,
    gate: RtdsmParityGate = DEFAULT_PARITY_GATE,
) -> RtdsmParityReport:
    """Compare research and current labels on their common usable months."""

    rtdsm = _usable_phase_map(rtdsm_history)
    current = _usable_phase_map(current_history)
    overlap = sorted(set(rtdsm) & set(current))
    pairs = [(current[item], rtdsm[item]) for item in overlap]
    count = len(pairs)
    exact = sum(left == right for left, right in pairs)
    side = sum(LEVEL_SIDE[left] == LEVEL_SIDE[right] for left, right in pairs)
    phase_agreement = exact / count if count else 0.0
    side_agreement = side / count if count else 0.0

    current_counts = Counter(left for left, _right in pairs)
    rtdsm_counts = Counter(right for _left, right in pairs)
    expected = (
        sum(
            current_counts[phase] * rtdsm_counts[phase]
            for phase in PHASE_SEQUENCE
        )
        / float(count * count)
        if count
        else 0.0
    )
    denominator = 1.0 - expected
    if count and abs(denominator) <= 1e-12:
        kappa = 1.0 if phase_agreement == 1.0 else 0.0
    elif count:
        kappa = (phase_agreement - expected) / denominator
    else:
        kappa = 0.0

    reasons: list[str] = []
    if count < gate.minimum_overlap_months:
        reasons.append("INSUFFICIENT_COMMON_PERIOD")
    if phase_agreement < gate.minimum_phase_agreement:
        reasons.append("LOW_PHASE_AGREEMENT")
    if kappa < gate.minimum_kappa:
        reasons.append("LOW_COHEN_KAPPA")
    if side_agreement < gate.minimum_level_side_agreement:
        reasons.append("LOW_LEVEL_SIDE_AGREEMENT")
    confusion = Counter(f"{left}->{right}" for left, right in pairs)
    return RtdsmParityReport(
        status="NO_GO_PARITY" if reasons else "PASS",
        reason_codes=tuple(reasons),
        overlap_months=count,
        first_overlap_at=overlap[0] if overlap else None,
        last_overlap_at=overlap[-1] if overlap else None,
        phase_agreement=phase_agreement,
        cohens_kappa=kappa,
        level_side_agreement=side_agreement,
        confusion_counts=dict(sorted(confusion.items())),
    )


def evaluate_rtdsm_model_readiness(
    rtdsm_history: Sequence[ObservedStateResult],
    current_history: Sequence[ObservedStateResult],
    *,
    source_complete: bool,
    sample_gate: TransitionSampleGate = DEFAULT_SAMPLE_GATE,
    parity_gate: RtdsmParityGate = DEFAULT_PARITY_GATE,
) -> RtdsmReadinessReport:
    """Combine unchanged sample support with pre-registered label parity."""

    sample = evaluate_transition_sample_feasibility(
        rtdsm_history,
        gate=sample_gate,
    )
    parity = evaluate_rtdsm_parity(
        rtdsm_history,
        current_history,
        gate=parity_gate,
    )
    reasons: list[str] = []
    if not source_complete:
        reasons.append("INCOMPLETE_RTDSM_SOURCE")
    reasons.extend(sample.reason_codes)
    if not source_complete or sample.status != "GO_EXPERIMENT":
        status = "NO_GO_DATA"
    elif parity.status != "PASS":
        status = "NO_GO_PARITY"
        reasons.extend(parity.reason_codes)
    else:
        status = "GO_MODEL_EXPERIMENT"
    return RtdsmReadinessReport(
        status=status,
        reason_codes=tuple(dict.fromkeys(reasons)),
        source_complete=bool(source_complete),
        sample_report=sample,
        parity_report=parity,
    )
