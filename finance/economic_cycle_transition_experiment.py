"""Read-only RTDSM core-state and transition publication experiment."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from typing import Callable, Mapping, Sequence

import pandas as pd

from finance.economic_cycle_core_state import (
    CoreStateAuditReport,
    build_core_feature_panel,
    evaluate_core_state_gate,
)
from finance.economic_cycle_observed_state import ObservedStateResult
from finance.economic_cycle_realtime_history import (
    build_rtdsm_monthly_panel,
    build_rtdsm_observed_history,
)
from finance.economic_cycle_transition_dataset import build_transition_dataset
from finance.economic_cycle_transition_feasibility import (
    TransitionFeasibilityReport,
    evaluate_transition_sample_feasibility,
)
from finance.economic_cycle_transition_validation import (
    TransitionPublicationDecision,
    TransitionValidationReport,
    evaluate_transition_publication_gate,
    run_transition_validation,
)
from finance.loaders.economic_cycle import load_economic_cycle_vintages
from finance.loaders.economic_cycle_realtime import load_rtdsm_signal_history


RTDSM_SERIES = ("IPT", "H", "EMPLOY", "RUC")
RTDSM_HISTORY_START = pd.Timestamp("1971-09-30")


@dataclass(frozen=True)
class TransitionExperimentReport:
    """Side-effect-free evidence and combined checkpoint decision."""

    status: str
    reason_codes: tuple[str, ...]
    as_of_date: str
    source_counts: dict[str, int]
    sample_report: TransitionFeasibilityReport
    core_state_report: CoreStateAuditReport
    validation_report: TransitionValidationReport | None
    publication_decision: TransitionPublicationDecision | None

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "reason_codes": list(self.reason_codes),
            "as_of_date": self.as_of_date,
            "source_counts": dict(self.source_counts),
            "sample_report": self.sample_report.to_dict(),
            "core_state_report": self.core_state_report.to_dict(),
            "validation_report": (
                self.validation_report.to_dict()
                if self.validation_report is not None
                else None
            ),
            "publication_decision": (
                self.publication_decision.to_dict()
                if self.publication_decision is not None
                else None
            ),
        }


def _default_rtdsm_loader(
    *,
    start_date: str | date,
    end_date: str | date,
    as_of_date: str | date,
) -> list[dict[str, object]]:
    return load_rtdsm_signal_history(
        RTDSM_SERIES,
        start_date=start_date,
        end_date=end_date,
        as_of_date=as_of_date,
    )


def _default_nber_loader(
    *,
    start_date: str | date,
    end_date: str | date,
    as_of_date: str | date,
) -> dict[str, bool]:
    rows = load_economic_cycle_vintages(
        ("USREC",),
        start_date=start_date,
        end_date=end_date,
        as_of_date=as_of_date,
    )
    result: dict[str, bool] = {}
    for row in rows:
        if str(row.get("series_id") or "").upper() != "USREC":
            continue
        observation = pd.to_datetime(row.get("observation_date"), errors="coerce")
        value = pd.to_numeric(row.get("value"), errors="coerce")
        if pd.isna(observation) or pd.isna(value):
            continue
        month = pd.Timestamp(observation).to_period("M").to_timestamp("M")
        result[month.date().isoformat()] = float(value) >= 0.5
    return result


def _source_counts(
    vintage_rows: Sequence[Mapping[str, object]],
    nber_months: Mapping[str, object],
    origins: Sequence[pd.Timestamp],
) -> dict[str, int]:
    counts = Counter(str(row.get("series_id") or "").upper() for row in vintage_rows)
    return {
        **{series_id: int(counts.get(series_id, 0)) for series_id in RTDSM_SERIES},
        "USREC": len(nber_months),
        "forecast_origins": len(origins),
        "rtdsm_rows": len(vintage_rows),
    }


def run_transition_experiment(
    as_of_date: str | date,
    *,
    rtdsm_loader: Callable[..., Sequence[Mapping[str, object]]] = _default_rtdsm_loader,
    nber_loader: Callable[..., Mapping[str, object]] = _default_nber_loader,
    panel_builder: Callable[..., pd.DataFrame] = build_rtdsm_monthly_panel,
    history_builder: Callable[[pd.DataFrame], Sequence[ObservedStateResult]] = build_rtdsm_observed_history,
    sample_evaluator: Callable[[Sequence[ObservedStateResult]], TransitionFeasibilityReport] = evaluate_transition_sample_feasibility,
    core_evaluator: Callable[..., CoreStateAuditReport] = evaluate_core_state_gate,
    validation_runner: Callable[[object], TransitionValidationReport] = run_transition_validation,
) -> TransitionExperimentReport:
    """Run the DB-only checkpoint without accepting any persistence writer."""

    cutoff = pd.Timestamp(as_of_date)
    if cutoff.tzinfo is not None:
        cutoff = cutoff.tz_convert(None)
    cutoff = cutoff.normalize()
    origins = list(pd.date_range(RTDSM_HISTORY_START, cutoff, freq="ME"))
    if not origins:
        raise ValueError("as_of_date must be on or after the RTDSM history start")
    start_text = RTDSM_HISTORY_START.date().isoformat()
    cutoff_text = cutoff.date().isoformat()

    vintage_rows = list(
        rtdsm_loader(
            start_date=start_text,
            end_date=cutoff_text,
            as_of_date=cutoff_text,
        )
    )
    nber_months = dict(
        nber_loader(
            start_date=start_text,
            end_date=cutoff_text,
            as_of_date=cutoff_text,
        )
    )
    source_counts = _source_counts(vintage_rows, nber_months, origins)
    source_complete = all(source_counts[series_id] > 0 for series_id in RTDSM_SERIES)

    realtime_panel = panel_builder(
        vintage_rows,
        forecast_origins=origins,
        vintage_lag_months=0,
    )
    revised_panel = panel_builder(
        vintage_rows,
        forecast_origins=origins,
        vintage_lag_months=3,
    )
    realtime_history = tuple(history_builder(realtime_panel))
    revised_history = tuple(history_builder(revised_panel))
    sample_report = sample_evaluator(realtime_history)
    core_panel = build_core_feature_panel(realtime_panel)
    core_report = core_evaluator(
        core_panel,
        realtime_history,
        revised_history,
        nber_months=nber_months,
        sample_report=sample_report,
    )
    if not source_complete or core_report.status != "READY":
        reasons = list(core_report.reason_codes)
        if not source_complete:
            reasons.insert(0, "INCOMPLETE_RTDSM_SOURCE")
        return TransitionExperimentReport(
            status="NO_GO_CORE_STATE",
            reason_codes=tuple(dict.fromkeys(reasons)),
            as_of_date=cutoff_text,
            source_counts=source_counts,
            sample_report=sample_report,
            core_state_report=core_report,
            validation_report=None,
            publication_decision=None,
        )

    dataset = build_transition_dataset(core_panel, realtime_history)
    validation_report = validation_runner(dataset)
    publication_decision = evaluate_transition_publication_gate(validation_report)
    ready = publication_decision.status == "READY"
    return TransitionExperimentReport(
        status="READY" if ready else "NO_GO_MODEL",
        reason_codes=publication_decision.reason_codes,
        as_of_date=cutoff_text,
        source_counts=source_counts,
        sample_report=sample_report,
        core_state_report=core_report,
        validation_report=validation_report,
        publication_decision=publication_decision,
    )
