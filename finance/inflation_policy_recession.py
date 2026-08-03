"""Independent point-in-time probability of an NBER recession within 12 months."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Mapping, Sequence

import numpy as np
import pandas as pd


RECESSION_COMPONENT = "recession_risk"
RECESSION_FEATURE_SCHEMA_VERSION = "recession-pit-features-v1"
RECESSION_VALIDATION_VERSION = "recession-quarterly-oos-v1"
RECESSION_HORIZON_MONTHS = 12
RECESSION_LABEL_DELAY_MONTHS = 24
RECESSION_FEATURES = (
    "unemployment_gap_pct",
    "payroll_3m_pct",
    "claims_yoy_pct",
    "manufacturing_hours_3m_delta",
    "temp_help_yoy_pct",
    "industrial_production_3m_pct",
    "real_income_6m_pct",
    "real_consumption_6m_pct",
    "yield_curve_slope_pct",
    "high_yield_oas_3m_delta_pct",
)
RECESSION_SERIES = (
    "USREC",
    "UNRATE",
    "PAYEMS",
    "ICSA",
    "AWHMAN",
    "TEMPHELPS",
    "INDPRO",
    "W875RX1",
    "PCEC96",
    "DGS2",
    "DGS10",
    "BAMLH0A0HYM2",
)


@dataclass(frozen=True)
class RecessionRiskArtifact:
    model_version: str
    feature_names: tuple[str, ...]
    feature_means: tuple[float, ...]
    feature_scales: tuple[float, ...]
    coefficients: tuple[float, ...]
    intercept: float
    validation_metrics: dict[str, object]
    publication_status: str
    reason_codes: tuple[str, ...]
    trained_through: str | None
    current_feature_values: dict[str, float] = field(default_factory=dict)
    forecast_horizon_months: int = RECESSION_HORIZON_MONTHS


@dataclass(frozen=True)
class RecessionRiskResult:
    as_of_at: str
    probability_12m: float | None
    risk_state: str | None
    risk_label: str | None
    horizon_months: int
    top_drivers: tuple[dict[str, object], ...]
    publication_status: str
    reason_codes: tuple[str, ...]
    validation_metrics: dict[str, object]


def _instant(value: object, *, field: str) -> pd.Timestamp:
    try:
        parsed = pd.Timestamp(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field}: {value!r}") from exc
    if pd.isna(parsed):
        raise ValueError(f"Invalid {field}: {value!r}")
    if parsed.tzinfo is None:
        parsed = parsed.tz_localize("UTC")
    else:
        parsed = parsed.tz_convert("UTC")
    return parsed


def _normalized_rows(rows: Sequence[Mapping[str, object]]) -> pd.DataFrame:
    frame = pd.DataFrame([dict(row) for row in rows])
    required = {"series_id", "observation_date", "released_at", "value"}
    if frame.empty or not required.issubset(frame.columns):
        return pd.DataFrame(columns=sorted(required))
    frame["series_id"] = frame["series_id"].astype(str).str.upper().str.strip()
    frame["observation_date"] = pd.to_datetime(
        frame["observation_date"], errors="coerce"
    ).dt.normalize()
    frame["released_at"] = pd.to_datetime(
        frame["released_at"], errors="coerce", utc=True
    )
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    return (
        frame.replace([np.inf, -np.inf], np.nan)
        .dropna(subset=("series_id", "observation_date", "released_at", "value"))
        .sort_values(["series_id", "observation_date", "released_at"])
        .reset_index(drop=True)
    )


def _final_recession_labels(
    rows: Sequence[Mapping[str, object]], *, as_of_at: object
) -> pd.Series:
    """Return final outcome labels; their use is delayed separately by 24 months."""

    cutoff = _instant(as_of_at, field="as_of_at")
    normalized: list[dict[str, object]] = []
    for raw in rows:
        if str(raw.get("series_id") or "").strip().upper() != "USREC":
            continue
        observed = pd.to_datetime(raw.get("observation_date"), errors="coerce")
        value = pd.to_numeric(pd.Series([raw.get("value")]), errors="coerce").iloc[0]
        if pd.isna(observed) or pd.isna(value) or observed > cutoff.tz_localize(None):
            continue
        normalized.append(
            {"observation_date": pd.Timestamp(observed).normalize(), "value": float(value)}
        )
    if not normalized:
        return pd.Series(dtype=float)
    frame = pd.DataFrame(normalized).sort_values("observation_date")
    return frame.drop_duplicates("observation_date", keep="last").set_index(
        "observation_date"
    )["value"]


def _series_at_origin(
    frame: pd.DataFrame, series_id: str, origin: pd.Timestamp
) -> pd.Series:
    selected = frame.loc[
        (frame["series_id"] == series_id)
        & (frame["released_at"] <= origin)
        & (frame["observation_date"] <= origin.tz_localize(None))
    ]
    if selected.empty:
        return pd.Series(dtype=float)
    return (
        selected.sort_values(["observation_date", "released_at"])
        .drop_duplicates("observation_date", keep="last")
        .set_index("observation_date")["value"]
        .sort_index()
    )


def _change(series: pd.Series, periods: int, *, percent: bool) -> float | None:
    if len(series) <= periods:
        return None
    current = float(series.iloc[-1])
    prior = float(series.iloc[-(periods + 1)])
    if percent:
        if abs(prior) <= 1e-12:
            return None
        return (current / prior - 1.0) * 100.0
    return current - prior


def _feature_row(frame: pd.DataFrame, origin: pd.Timestamp) -> dict[str, float | None]:
    unrate = _series_at_origin(frame, "UNRATE", origin)
    payroll = _series_at_origin(frame, "PAYEMS", origin)
    claims = _series_at_origin(frame, "ICSA", origin)
    hours = _series_at_origin(frame, "AWHMAN", origin)
    temp = _series_at_origin(frame, "TEMPHELPS", origin)
    industrial = _series_at_origin(frame, "INDPRO", origin)
    income = _series_at_origin(frame, "W875RX1", origin)
    consumption = _series_at_origin(frame, "PCEC96", origin)
    dgs2 = _series_at_origin(frame, "DGS2", origin)
    dgs10 = _series_at_origin(frame, "DGS10", origin)
    high_yield = _series_at_origin(frame, "BAMLH0A0HYM2", origin)
    claims_4w = claims.rolling(4, min_periods=4).mean()
    unrate_gap = None
    if len(unrate) >= 12:
        unrate_gap = float(unrate.iloc[-1] - unrate.iloc[-12:].min())
    curve = None
    if not dgs2.empty and not dgs10.empty:
        curve = float(dgs10.iloc[-1] - dgs2.iloc[-1])
    return {
        "unemployment_gap_pct": unrate_gap,
        "payroll_3m_pct": _change(payroll, 3, percent=True),
        "claims_yoy_pct": _change(claims_4w, 52, percent=True),
        "manufacturing_hours_3m_delta": _change(hours, 3, percent=False),
        "temp_help_yoy_pct": _change(temp, 12, percent=True),
        "industrial_production_3m_pct": _change(industrial, 3, percent=True),
        "real_income_6m_pct": _change(income, 6, percent=True),
        "real_consumption_6m_pct": _change(consumption, 6, percent=True),
        "yield_curve_slope_pct": curve,
        "high_yield_oas_3m_delta_pct": _change(high_yield, 63, percent=False),
    }


def build_recession_origin_panel(
    feature_rows: Sequence[Mapping[str, object]],
    label_rows: Sequence[Mapping[str, object]],
    *,
    as_of_at: str | datetime,
    origin_start: str = "1988-03-31",
    horizon_months: int = RECESSION_HORIZON_MONTHS,
    label_delay_months: int = RECESSION_LABEL_DELAY_MONTHS,
) -> pd.DataFrame:
    """Build quarterly PIT origins plus one unlabelled current prediction row."""

    cutoff = _instant(as_of_at, field="as_of_at")
    features = _normalized_rows(feature_rows)
    labels = _final_recession_labels(label_rows, as_of_at=cutoff)
    columns = (
        "origin_at",
        "target_available_at",
        "target_recession_12m",
        "complete_feature_ratio",
        *RECESSION_FEATURES,
    )
    if features.empty or labels.empty:
        return pd.DataFrame(columns=columns)
    start = pd.Timestamp(origin_start, tz="UTC")
    last_completed_quarter = cutoff.tz_localize(None).to_period("Q").start_time.tz_localize(
        "UTC"
    ) - pd.Timedelta(nanoseconds=1)
    quarterly = pd.date_range(start=start, end=last_completed_quarter, freq="QE", tz="UTC")
    origins = [*quarterly, cutoff]
    result: list[dict[str, object]] = []
    latest_label_month = labels.index.max()
    for origin in origins:
        values = _feature_row(features, origin)
        finite_count = sum(
            value is not None and math.isfinite(float(value)) for value in values.values()
        )
        target_end = (
            origin.tz_localize(None).to_period("M") + int(horizon_months)
        ).end_time.normalize()
        target: float | None = None
        target_available: pd.Timestamp | None = None
        if target_end <= latest_label_month:
            future_labels = labels.loc[
                (labels.index > origin.tz_localize(None).normalize())
                & (labels.index <= target_end)
            ]
            if not future_labels.empty:
                target = float((future_labels >= 0.5).any())
                target_available = (
                    target_end + pd.DateOffset(months=int(label_delay_months))
                ).tz_localize("UTC") + pd.Timedelta(hours=23, minutes=59, seconds=59)
        result.append(
            {
                "origin_at": origin.isoformat(),
                "target_available_at": (
                    target_available.isoformat() if target_available is not None else None
                ),
                "target_recession_12m": target,
                "complete_feature_ratio": finite_count / len(RECESSION_FEATURES),
                **values,
            }
        )
    return pd.DataFrame(result, columns=columns)


def _fit_logistic(
    x: np.ndarray, y: np.ndarray, *, ridge_alpha: float
) -> tuple[float, np.ndarray]:
    design = np.column_stack((np.ones(len(x)), x))
    beta = np.zeros(design.shape[1], dtype=float)
    base_rate = min(max(float(np.mean(y)), 1e-4), 1.0 - 1e-4)
    beta[0] = math.log(base_rate / (1.0 - base_rate))
    penalty = np.eye(design.shape[1], dtype=float) * float(ridge_alpha)
    penalty[0, 0] = 0.0
    for _ in range(100):
        linear = np.clip(design @ beta, -30.0, 30.0)
        probability = 1.0 / (1.0 + np.exp(-linear))
        weights = np.clip(probability * (1.0 - probability), 1e-6, None)
        gradient = design.T @ (probability - y) + penalty @ beta
        hessian = design.T @ (weights[:, None] * design) + penalty
        step = np.linalg.solve(hessian, gradient)
        beta -= step
        if float(np.max(np.abs(step))) < 1e-8:
            break
    return float(beta[0]), beta[1:]


def _prepare_training(
    frame: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    x = frame.loc[:, RECESSION_FEATURES].to_numpy(dtype=float)
    means = np.asarray(
        [
            float(np.median(column[np.isfinite(column)]))
            if np.isfinite(column).any()
            else 0.0
            for column in x.T
        ],
        dtype=float,
    )
    missing = ~np.isfinite(x)
    x[missing] = np.take(means, np.where(missing)[1])
    scales = np.nanstd(x, axis=0)
    scales[~np.isfinite(scales) | (scales <= 1e-12)] = 1.0
    y = frame["target_recession_12m"].to_numpy(dtype=float)
    return (x - means) / scales, y, means, scales


def _probability(intercept: float, coefficients: np.ndarray, x: np.ndarray) -> float:
    linear = float(np.clip(intercept + x @ coefficients, -30.0, 30.0))
    return 1.0 / (1.0 + math.exp(-linear))


def _calibration_error(probabilities: Sequence[float], actuals: Sequence[float]) -> float:
    errors = []
    total = len(probabilities)
    for lower in np.linspace(0.0, 0.8, 5):
        upper = lower + 0.2
        members = [
            index
            for index, value in enumerate(probabilities)
            if lower <= value < upper or upper >= 1.0 and value == 1.0
        ]
        if not members:
            continue
        predicted = float(np.mean([probabilities[index] for index in members]))
        observed = float(np.mean([actuals[index] for index in members]))
        errors.append(len(members) / total * abs(predicted - observed))
    return float(sum(errors))


def _episode_count(actuals: Sequence[float]) -> int:
    count = 0
    previous = 0.0
    for value in actuals:
        if value >= 0.5 and previous < 0.5:
            count += 1
        previous = value
    return count


def fit_recession_risk_model(
    panel: pd.DataFrame,
    *,
    as_of_at: str | datetime,
    model_version: str,
    minimum_origins: int = 60,
    minimum_training_rows: int = 40,
    minimum_complete_feature_ratio: float = 0.80,
    maximum_calibration_error: float = 0.15,
    ridge_alpha: float = 10.0,
) -> RecessionRiskArtifact:
    """Fit and gate a quarterly expanding-window logistic recession model."""

    cutoff = _instant(as_of_at, field="as_of_at")
    source = panel.copy()
    required = {"origin_at", "target_available_at", "target_recession_12m", *RECESSION_FEATURES}
    if source.empty or not required.issubset(source.columns):
        return RecessionRiskArtifact(
            model_version=str(model_version), feature_names=RECESSION_FEATURES,
            feature_means=(), feature_scales=(), coefficients=(), intercept=0.0,
            validation_metrics={"origin_count": 0.0}, publication_status="NOT_AVAILABLE",
            reason_codes=("recession_inputs_not_available",), trained_through=None,
        )
    source["origin_at"] = pd.to_datetime(source["origin_at"], errors="coerce", utc=True)
    source["target_available_at"] = pd.to_datetime(
        source["target_available_at"], errors="coerce", utc=True
    )
    for column in (*RECESSION_FEATURES, "target_recession_12m", "complete_feature_ratio"):
        source[column] = pd.to_numeric(source[column], errors="coerce")
    completed = source.loc[
        source["target_recession_12m"].notna()
        & source["target_available_at"].notna()
        & (source["target_available_at"] <= cutoff)
        & (source["complete_feature_ratio"] >= float(minimum_complete_feature_ratio))
    ].sort_values("origin_at").reset_index(drop=True)
    current = source.loc[source["origin_at"] <= cutoff].sort_values("origin_at").tail(1)
    current_values = {
        name: float(value)
        for name, value in (
            (name, pd.to_numeric(current.iloc[0][name], errors="coerce"))
            for name in RECESSION_FEATURES
        )
        if not pd.isna(value) and math.isfinite(float(value))
    } if not current.empty else {}
    current_complete_ratio = len(current_values) / len(RECESSION_FEATURES)
    if len(completed) < int(minimum_origins):
        return RecessionRiskArtifact(
            model_version=str(model_version), feature_names=RECESSION_FEATURES,
            feature_means=(), feature_scales=(), coefficients=(), intercept=0.0,
            validation_metrics={"origin_count": float(len(completed))},
            publication_status="NOT_AVAILABLE", reason_codes=("insufficient_recession_origins",),
            trained_through=None, current_feature_values=current_values,
        )
    predictions: list[float] = []
    actuals: list[float] = []
    baselines: list[float] = []
    for index, evaluation in completed.iterrows():
        origin = evaluation["origin_at"]
        training = completed.loc[
            (completed.index != index) & (completed["target_available_at"] <= origin)
        ]
        if len(training) < int(minimum_training_rows) or training["target_recession_12m"].nunique() < 2:
            continue
        x_train, y_train, means, scales = _prepare_training(training)
        intercept, coefficients = _fit_logistic(x_train, y_train, ridge_alpha=ridge_alpha)
        raw = evaluation.loc[list(RECESSION_FEATURES)].to_numpy(dtype=float)
        raw[~np.isfinite(raw)] = means[~np.isfinite(raw)]
        predictions.append(_probability(intercept, coefficients, (raw - means) / scales))
        actuals.append(float(evaluation["target_recession_12m"]))
        baselines.append(float(np.mean(y_train)))
    reasons: list[str] = []
    if current_complete_ratio < 0.80:
        reasons.append("current_recession_inputs_incomplete")
    if not predictions:
        reasons.append("insufficient_recession_validation_folds")
        brier = baseline_brier = calibration = math.inf
        episodes = 0
    else:
        brier = float(np.mean([(p - y) ** 2 for p, y in zip(predictions, actuals, strict=True)]))
        baseline_brier = float(np.mean([(p - y) ** 2 for p, y in zip(baselines, actuals, strict=True)]))
        calibration = _calibration_error(predictions, actuals)
        episodes = _episode_count(actuals)
        if brier >= baseline_brier - 1e-12:
            reasons.append("recession_baseline_not_beaten")
        if calibration > float(maximum_calibration_error) + 1e-12:
            reasons.append("recession_calibration_not_ready")
        if episodes < 2:
            reasons.append("insufficient_recession_episodes")
    x_all, y_all, means, scales = _prepare_training(completed)
    intercept, coefficients = _fit_logistic(x_all, y_all, ridge_alpha=ridge_alpha)
    metrics: dict[str, object] = {
        "origin_count": float(len(completed)),
        "fold_count": float(len(predictions)),
        "recession_episode_count": float(episodes),
        "brier": None if not math.isfinite(brier) else brier,
        "baseline_brier": None if not math.isfinite(baseline_brier) else baseline_brier,
        "calibration_error": None if not math.isfinite(calibration) else calibration,
        "minimum_complete_feature_ratio": float(minimum_complete_feature_ratio),
        "current_complete_feature_ratio": float(current_complete_ratio),
        "horizon_months": float(RECESSION_HORIZON_MONTHS),
        "label_delay_months": float(RECESSION_LABEL_DELAY_MONTHS),
        "validation_scheme": RECESSION_VALIDATION_VERSION,
        "training_start_date": pd.Timestamp(completed.iloc[0]["origin_at"])
        .date()
        .isoformat(),
    }
    return RecessionRiskArtifact(
        model_version=str(model_version), feature_names=RECESSION_FEATURES,
        feature_means=tuple(float(value) for value in means),
        feature_scales=tuple(float(value) for value in scales),
        coefficients=tuple(float(value) for value in coefficients),
        intercept=float(intercept), validation_metrics=metrics,
        publication_status="READY" if not reasons else "LIMITED",
        reason_codes=tuple(reasons),
        trained_through=pd.Timestamp(completed.iloc[-1]["origin_at"]).date().isoformat(),
        current_feature_values=current_values,
    )


def _risk_state(probability: float) -> tuple[str, str]:
    if probability < 0.15:
        return "LOW", "낮음"
    if probability < 0.30:
        return "WATCH", "관찰"
    if probability < 0.50:
        return "ELEVATED", "상승"
    if probability < 0.70:
        return "HIGH", "높음"
    return "VERY_HIGH", "매우 높음"


def predict_recession_risk(
    artifact: RecessionRiskArtifact, *, as_of_at: str | datetime
) -> RecessionRiskResult:
    """Publish only a model that passed its own independent OOS gate."""

    if (
        artifact.publication_status not in {"READY", "LIMITED"}
        or len(artifact.coefficients) != len(RECESSION_FEATURES)
        or len(artifact.feature_means) != len(RECESSION_FEATURES)
        or len(artifact.feature_scales) != len(RECESSION_FEATURES)
    ):
        return RecessionRiskResult(
            as_of_at=_instant(as_of_at, field="as_of_at").isoformat(),
            probability_12m=None, risk_state=None, risk_label=None,
            horizon_months=RECESSION_HORIZON_MONTHS, top_drivers=(),
            publication_status="NOT_AVAILABLE", reason_codes=artifact.reason_codes or ("recession_model_not_available",),
            validation_metrics=artifact.validation_metrics,
        )
    means = np.asarray(artifact.feature_means, dtype=float)
    scales = np.asarray(artifact.feature_scales, dtype=float)
    raw = np.asarray(
        [artifact.current_feature_values.get(name, means[index]) for index, name in enumerate(RECESSION_FEATURES)],
        dtype=float,
    )
    standardized = (raw - means) / scales
    coefficients = np.asarray(artifact.coefficients, dtype=float)
    probability = _probability(artifact.intercept, coefficients, standardized)
    state, label = _risk_state(probability)
    contributions = standardized * coefficients
    drivers = tuple(
        {
            "feature": RECESSION_FEATURES[index],
            "value": float(raw[index]),
            "contribution": float(contributions[index]),
            "direction": "risk_up" if contributions[index] > 0 else "risk_down",
        }
        for index in sorted(range(len(contributions)), key=lambda item: abs(contributions[item]), reverse=True)[:5]
    )
    return RecessionRiskResult(
        as_of_at=_instant(as_of_at, field="as_of_at").isoformat(),
        probability_12m=probability if artifact.publication_status == "READY" else None,
        risk_state=state if artifact.publication_status == "READY" else None,
        risk_label=label if artifact.publication_status == "READY" else None,
        horizon_months=RECESSION_HORIZON_MONTHS, top_drivers=drivers,
        publication_status=artifact.publication_status,
        reason_codes=artifact.reason_codes,
        validation_metrics=artifact.validation_metrics,
    )
