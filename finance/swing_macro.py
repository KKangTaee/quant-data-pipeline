from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class MacroEvaluation:
    passed: bool
    reason: str
    snapshot: dict[str, Any]
    penalty_total: float = 0.0


def _safe_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(parsed):
        return None
    return parsed


def _date_key(value: Any) -> pd.Timestamp:
    return pd.Timestamp(value).normalize()


def _threshold(config: Any, name: str, default: float) -> float:
    return float(getattr(config, name, default))


def _pressure_penalties(snapshot: dict[str, Any], config: Any) -> tuple[float, dict[str, float]]:
    rows = [
        ("rate_pressure", "rate_pressure_mean_z", "rate_pressure_max", "rate_pressure_penalty_weight"),
        ("dollar_pressure", "dollar_pressure_mean_z", "dollar_pressure_max", "dollar_pressure_penalty_weight"),
        ("safe_haven", "safe_haven_mean_z", "safe_haven_max", "safe_haven_penalty_weight"),
    ]
    total = 0.0
    details: dict[str, float] = {}
    for label, score_key, threshold_key, weight_key in rows:
        score = snapshot.get(score_key)
        threshold = _threshold(config, threshold_key, 1.0)
        weight = max(_threshold(config, weight_key, 10.0), 0.0)
        excess = max(float(score) - threshold, 0.0) if score is not None else 0.0
        penalty = excess * weight
        details[f"{label}_penalty"] = float(penalty)
        total += penalty
    return float(total), details


def evaluate_macro_snapshot(snapshot: dict[str, Any], config: Any) -> MacroEvaluation:
    if not bool(getattr(config, "macro_filter_enabled", True)) or getattr(config, "macro_filter_mode", "hard_filter") == "off":
        return MacroEvaluation(True, "disabled", dict(snapshot), 0.0)

    required_scores = [
        "risk_on_mean_z",
        "rate_pressure_mean_z",
        "dollar_pressure_mean_z",
        "safe_haven_mean_z",
    ]
    missing = [key for key in required_scores if snapshot.get(key) is None]
    if missing:
        enriched = dict(snapshot)
        enriched["macro_missing_scores"] = missing
        return MacroEvaluation(False, "incomplete_macro_scores", enriched, 0.0)

    risk_on = float(snapshot["risk_on_mean_z"])
    if risk_on <= _threshold(config, "risk_on_min", 0.0):
        return MacroEvaluation(False, "risk_on_failed", dict(snapshot), 0.0)

    mode = str(getattr(config, "macro_filter_mode", "hard_filter") or "hard_filter")
    penalty_total, penalty_details = _pressure_penalties(snapshot, config)
    enriched = dict(snapshot)
    enriched.update(penalty_details)
    enriched["macro_penalty_total"] = penalty_total

    if mode == "ranking_penalty":
        return MacroEvaluation(
            True,
            "ranking_penalty_applied" if penalty_total > 0 else "pass",
            enriched,
            penalty_total,
        )

    checks = [
        float(snapshot["rate_pressure_mean_z"]) <= _threshold(config, "rate_pressure_max", 1.0),
        float(snapshot["dollar_pressure_mean_z"]) <= _threshold(config, "dollar_pressure_max", 1.0),
        float(snapshot["safe_haven_mean_z"]) <= _threshold(config, "safe_haven_max", 1.0),
    ]
    if all(checks):
        return MacroEvaluation(True, "pass", enriched, 0.0)
    return MacroEvaluation(False, "hard_filter_failed", enriched, 0.0)


def build_macro_lookup(macro_scores: pd.DataFrame | None):
    if macro_scores is None or macro_scores.empty:
        dates = pd.DatetimeIndex([])
        frame = pd.DataFrame()
    else:
        frame = macro_scores.copy()
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce").dt.normalize()
        frame = frame.dropna(subset=["date"]).sort_values("date").drop_duplicates(subset=["date"], keep="last")
        dates = pd.DatetimeIndex(frame["date"])

    def lookup(signal_date: pd.Timestamp, config: Any) -> MacroEvaluation:
        if not bool(getattr(config, "macro_filter_enabled", True)) or getattr(config, "macro_filter_mode", "hard_filter") == "off":
            return MacroEvaluation(True, "disabled", {}, 0.0)
        if frame.empty or dates.empty:
            return MacroEvaluation(False, "missing_macro_scores", {}, 0.0)
        index = dates.searchsorted(_date_key(signal_date), side="right") - 1
        if index < 0:
            return MacroEvaluation(False, "missing_macro_scores", {}, 0.0)
        row = frame.iloc[int(index)]
        score_date = _date_key(row["date"])
        staleness = (_date_key(signal_date) - score_date).days
        snapshot = {
            "macro_score_date": score_date.strftime("%Y-%m-%d"),
            "macro_staleness_days": int(staleness),
            "risk_on_mean_z": _safe_float(row.get("risk_on_mean_z")),
            "rate_pressure_mean_z": _safe_float(row.get("rate_pressure_mean_z")),
            "dollar_pressure_mean_z": _safe_float(row.get("dollar_pressure_mean_z")),
            "safe_haven_mean_z": _safe_float(row.get("safe_haven_mean_z")),
            "standardized_symbol_count": int(row.get("standardized_symbol_count") or 0),
        }
        if staleness > int(getattr(config, "macro_max_staleness_days", 5)):
            return MacroEvaluation(False, "stale_macro_scores", snapshot, 0.0)
        return evaluate_macro_snapshot(snapshot, config)

    return lookup
