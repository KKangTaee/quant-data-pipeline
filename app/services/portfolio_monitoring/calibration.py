from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import sqrt
from typing import Any, Mapping, Sequence

import pandas as pd

from .schemas import build_request_fingerprint


CALIBRATION_ALGORITHM_VERSION = "portfolio_monitoring_calibration_v1"


@dataclass(frozen=True)
class ReplayResult:
    train_rows: tuple[dict[str, Any], ...]
    validation_rows: tuple[dict[str, Any], ...]
    rejected: dict[str, str]
    split_dates: dict[str, str]
    embargo_sessions: int
    data_fingerprint: str


@dataclass(frozen=True)
class CalibrationArtifact:
    algorithm_version: str
    algorithm_fingerprint: str
    data_fingerprint: str
    sample_size: int
    positive_count: int
    probability: float | None
    brier_score: float | None
    baseline_brier: float | None
    max_reliability_error: float | None
    reliability_buckets: tuple[dict[str, Any], ...]
    confidence_interval: tuple[float, float]
    integrity_blockers: tuple[str, ...]
    horizon_sessions: int
    event_definition: str
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class PublicationDecision:
    status: str
    reasons: tuple[str, ...]
    probability: float | None
    horizon_sessions: int
    event_definition: str
    sample_size: int
    positive_count: int
    brier_score: float | None
    baseline_brier: float | None
    max_reliability_error: float | None
    limitations: tuple[str, ...]
    algorithm_fingerprint: str
    data_fingerprint: str


def _as_date(value: Any) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def build_historical_replay(
    samples: Sequence[Mapping[str, Any]],
    *,
    split_dates: Mapping[str, Any],
    embargo_sessions: int,
) -> ReplayResult:
    """Create a time-ordered PIT split and reject leakage before calibration."""

    train_end = _as_date(split_dates["train_end"])
    validation_start = _as_date(split_dates["validation_start"])
    validation_end = _as_date(split_dates["validation_end"])
    embargo = max(int(embargo_sessions), 0)
    embargo_cutoff = (pd.Timestamp(validation_start) - pd.offsets.BDay(embargo)).date()
    train: list[dict[str, Any]] = []
    validation: list[dict[str, Any]] = []
    rejected: dict[str, str] = {}
    for index, raw in enumerate(samples):
        row = dict(raw)
        row_id = str(row.get("id") or f"row-{index}")
        try:
            as_of = _as_date(row.get("as_of_date"))
            vintage = _as_date(row.get("macro_vintage_date"))
            outcome_end = _as_date(row.get("outcome_end_date"))
        except (TypeError, ValueError):
            rejected[row_id] = "malformed publication or outcome date"
            continue
        if vintage > as_of:
            rejected[row_id] = "future macro vintage is not point-in-time eligible"
            continue
        if row.get("pit_exposure") is not True:
            rejected[row_id] = "non-PIT exposure snapshot"
            continue
        if as_of <= train_end:
            if outcome_end > embargo_cutoff:
                rejected[row_id] = "outcome horizon overlaps validation embargo"
            else:
                train.append(row)
        elif validation_start <= as_of <= validation_end:
            validation.append(row)
        else:
            rejected[row_id] = "outside configured split dates"
    train.sort(key=lambda row: (str(row.get("as_of_date")), str(row.get("id"))))
    validation.sort(key=lambda row: (str(row.get("as_of_date")), str(row.get("id"))))
    fingerprint = build_request_fingerprint({
        "train": train,
        "validation": validation,
        "rejected": rejected,
        "splits": {key: str(value) for key, value in split_dates.items()},
        "embargo": embargo,
    })
    return ReplayResult(
        train_rows=tuple(train), validation_rows=tuple(validation), rejected=rejected,
        split_dates={key: str(value) for key, value in split_dates.items()},
        embargo_sessions=embargo, data_fingerprint=fingerprint,
    )


def _eligible_rows(rows: Sequence[Mapping[str, Any]]) -> list[tuple[int, float]]:
    eligible: list[tuple[int, float]] = []
    for row in rows:
        try:
            outcome = int(row.get("outcome"))
            probability = float(row.get("predicted_probability"))
        except (TypeError, ValueError):
            continue
        if outcome not in {0, 1} or not 0 <= probability <= 1:
            continue
        eligible.append((outcome, probability))
    return eligible


def _wilson_interval(positives: int, total: int) -> tuple[float, float]:
    if total <= 0:
        return (0.0, 1.0)
    z = 1.96
    proportion = positives / total
    denominator = 1 + z * z / total
    centre = (proportion + z * z / (2 * total)) / denominator
    margin = z * sqrt((proportion * (1 - proportion) + z * z / (4 * total)) / total) / denominator
    return (max(0.0, centre - margin), min(1.0, centre + margin))


def _reliability(rows: list[tuple[int, float]]) -> tuple[tuple[dict[str, Any], ...], float | None]:
    bins: dict[int, list[tuple[int, float]]] = {}
    for outcome, probability in rows:
        index = min(int(probability * 10), 9)
        bins.setdefault(index, []).append((outcome, probability))
    result = []
    errors = []
    for index in sorted(bins):
        values = bins[index]
        predicted = sum(probability for _, probability in values) / len(values)
        observed = sum(outcome for outcome, _ in values) / len(values)
        error = abs(predicted - observed)
        errors.append(error)
        result.append({
            "lower": index / 10,
            "upper": (index + 1) / 10,
            "count": len(values),
            "predicted": predicted,
            "observed": observed,
            "absolute_error": error,
        })
    return tuple(result), max(errors) if errors else None


def calibrate_risk_probability(
    train_rows: Sequence[Mapping[str, Any]],
    validation_rows: Sequence[Mapping[str, Any]],
    *,
    integrity_blockers: Sequence[str] | None = None,
    horizon_sessions: int = 21,
    event_definition: str = "subsequent portfolio drawdown at or below -10%",
) -> CalibrationArtifact:
    """Calculate deterministic OOS calibration evidence; publication is a separate gate."""

    train = _eligible_rows(train_rows)
    validation = _eligible_rows(validation_rows)
    train_rate = sum(outcome for outcome, _ in train) / len(train) if train else 0.0
    if validation:
        brier = sum((probability - outcome) ** 2 for outcome, probability in validation) / len(validation)
        baseline = sum((train_rate - outcome) ** 2 for outcome, _ in validation) / len(validation)
        probability = sum(probability for _, probability in validation) / len(validation)
    else:
        brier = baseline = probability = None
    buckets, max_error = _reliability(validation)
    positives = sum(outcome for outcome, _ in validation)
    algorithm_fingerprint = build_request_fingerprint({
        "algorithm_version": CALIBRATION_ALGORITHM_VERSION,
        "horizon_sessions": horizon_sessions,
        "event_definition": event_definition,
        "reliability_bins": 10,
    })
    data_fingerprint = build_request_fingerprint({
        "train": [dict(row) for row in train_rows],
        "validation": [dict(row) for row in validation_rows],
    })
    limitations = (
        "확률은 정의된 후속 drawdown event에만 해당하며 기대수익률이 아닙니다.",
        "시간순 OOS와 publication integrity gate를 통과한 artifact만 공개합니다.",
    )
    return CalibrationArtifact(
        algorithm_version=CALIBRATION_ALGORITHM_VERSION,
        algorithm_fingerprint=algorithm_fingerprint,
        data_fingerprint=data_fingerprint,
        sample_size=len(validation),
        positive_count=positives,
        probability=probability,
        brier_score=brier,
        baseline_brier=baseline,
        max_reliability_error=max_error,
        reliability_buckets=buckets,
        confidence_interval=_wilson_interval(positives, len(validation)),
        integrity_blockers=tuple(dict.fromkeys(str(value) for value in integrity_blockers or [] if str(value))),
        horizon_sessions=int(horizon_sessions),
        event_definition=event_definition,
        limitations=limitations,
    )


def evaluate_publication_gate(artifact: CalibrationArtifact) -> PublicationDecision:
    reasons: list[str] = []
    suppress = False
    if artifact.sample_size < 250:
        reasons.append("at least 250 eligible OOS observations are required")
        suppress = True
    if artifact.positive_count < 50:
        reasons.append("at least 50 positive outcomes are required")
        suppress = True
    if artifact.integrity_blockers:
        reasons.extend(f"publication integrity blocker: {value}" for value in artifact.integrity_blockers)
        suppress = True
    limited = False
    if artifact.brier_score is None or artifact.baseline_brier is None or artifact.brier_score > artifact.baseline_brier * 0.95:
        reasons.append("OOS Brier score must improve on the naive baseline by at least 5%")
        limited = True
    if artifact.max_reliability_error is None or artifact.max_reliability_error > 0.10 + 1e-12:
        reasons.append("maximum reliability-bin absolute error must be <= 0.10")
        limited = True
    status = "SUPPRESSED" if suppress else "LIMITED" if limited else "READY"
    return PublicationDecision(
        status=status,
        reasons=tuple(reasons),
        probability=artifact.probability if status == "READY" else None,
        horizon_sessions=artifact.horizon_sessions,
        event_definition=artifact.event_definition,
        sample_size=artifact.sample_size,
        positive_count=artifact.positive_count,
        brier_score=artifact.brier_score,
        baseline_brier=artifact.baseline_brier,
        max_reliability_error=artifact.max_reliability_error,
        limitations=artifact.limitations,
        algorithm_fingerprint=artifact.algorithm_fingerprint,
        data_fingerprint=artifact.data_fingerprint,
    )
