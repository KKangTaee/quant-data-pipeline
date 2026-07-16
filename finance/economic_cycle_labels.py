"""Retrospective real-economy phase labels for model training/evaluation."""

from __future__ import annotations

import math
from datetime import date, datetime

import pandas as pd


PHASES = ("recovery", "expansion", "slowdown", "recession")


def label_phase(
    activity_level: float,
    labor_level: float,
    activity_momentum: float,
    labor_momentum: float,
    recession_flag: float,
) -> str:
    """Map real activity/labor level and momentum into the four approved phases."""

    level = 0.5 * float(activity_level) + 0.5 * float(labor_level)
    momentum = 0.5 * float(activity_momentum) + 0.5 * float(labor_momentum)
    if float(recession_flag) >= 0.5:
        return "recession"
    if level < 0 and momentum >= 0:
        return "recovery"
    if level >= 0 and momentum >= 0:
        return "expansion"
    if level >= 0 and momentum < 0:
        return "slowdown"
    return "recession"


def _reason_for_phase(phase: str, recession_flag: float) -> str:
    if float(recession_flag) >= 0.5:
        return "nber_recession_override"
    return {
        "recovery": "negative_level_positive_momentum",
        "expansion": "positive_level_positive_momentum",
        "slowdown": "positive_level_negative_momentum",
        "recession": "negative_level_negative_momentum",
    }[phase]


def _cutoff_timestamp(value: str | date | datetime | None) -> pd.Timestamp | None:
    if value is None:
        return None
    parsed = pd.Timestamp(value)
    if parsed.tzinfo is not None:
        parsed = parsed.tz_convert(None)
    return parsed.normalize()


def build_phase_label_frame(
    feature_panel: pd.DataFrame,
    *,
    label_as_of_date: str | date | datetime | None = None,
) -> pd.DataFrame:
    """Build phase labels using only origin-eligible real-economy columns."""

    frame = feature_panel.copy()
    for column in ("activity_score", "labor_income_score"):
        if column not in frame:
            frame[column] = None
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    for factor in ("activity", "labor_income"):
        momentum_column = f"{factor}_momentum_3m"
        if momentum_column not in frame:
            frame[momentum_column] = frame[f"{factor}_score"].diff(3)
        frame[momentum_column] = pd.to_numeric(
            frame[momentum_column], errors="coerce"
        )
    if "USREC_signal" not in frame:
        frame["USREC_signal"] = 0.0
    frame["USREC_signal"] = pd.to_numeric(
        frame["USREC_signal"], errors="coerce"
    ).fillna(0.0)

    cutoff = _cutoff_timestamp(label_as_of_date)
    origins = (
        pd.to_datetime(frame["forecast_origin"], errors="coerce")
        if "forecast_origin" in frame
        else pd.Series(pd.NaT, index=frame.index)
    )
    phases: list[str | None] = []
    reasons: list[str | None] = []
    for position, (_, row) in enumerate(frame.iterrows()):
        origin = origins.iloc[position]
        if cutoff is not None and pd.notna(origin) and pd.Timestamp(origin) > cutoff:
            phases.append(None)
            reasons.append("after_label_as_of")
            continue
        values = (
            row.get("activity_score"),
            row.get("labor_income_score"),
            row.get("activity_momentum_3m"),
            row.get("labor_income_momentum_3m"),
        )
        if any(pd.isna(value) or not math.isfinite(float(value)) for value in values):
            phases.append(None)
            reasons.append("missing_real_economy_factor")
            continue
        recession_flag = float(row.get("USREC_signal") or 0.0)
        phase = label_phase(*[float(value) for value in values], recession_flag)
        phases.append(phase)
        reasons.append(_reason_for_phase(phase, recession_flag))

    frame["phase"] = pd.Series(phases, index=frame.index, dtype="object")
    frame["label_reason"] = pd.Series(reasons, index=frame.index, dtype="object")
    if "USREC_latest_observation_date" in frame:
        frame["label_eligible_vintage_date"] = frame[
            "USREC_latest_observation_date"
        ]
    else:
        frame["label_eligible_vintage_date"] = None
    return frame


def build_retrospective_phase_labels(
    feature_panel: pd.DataFrame,
    *,
    label_as_of_date: str | date | datetime | None = None,
) -> pd.Series:
    """Return only the phase series while retaining missing labels explicitly."""

    return build_phase_label_frame(
        feature_panel, label_as_of_date=label_as_of_date
    )["phase"]
