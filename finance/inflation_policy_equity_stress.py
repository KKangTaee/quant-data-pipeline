"""Point-in-time S&P 500 EPS and multiple stress analysis."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timezone

import numpy as np
import pandas as pd


PANEL_COLUMNS = (
    "origin_date",
    "eps_source_release_date",
    "target_eps_year",
    "current_index_level",
    "forward_eps",
    "forward_multiple",
    "measured_next_year_eps_revision_pct",
    "months_to_year_end",
    "dgs2_pct",
    "dgs10_pct",
    "real_yield_10y_pct",
    "breakeven_10y_pct",
    "policy_repricing_bp",
    "dgs10_change_bp",
    "real_yield_change_bp",
    "breakeven_change_bp",
    "future_index_level",
    "future_forward_eps",
    "future_forward_multiple",
    "eps_change_pct",
    "multiple_change_pct",
    "index_change_pct",
)

EQUITY_FEATURES = (
    "measured_next_year_eps_revision_pct",
    "months_to_year_end",
    "policy_repricing_bp",
    "dgs10_change_bp",
    "real_yield_change_bp",
    "breakeven_change_bp",
)


@dataclass(frozen=True)
class EquityStressValidationReport:
    origin_count: int
    fold_count: int
    index_mae: float | None
    baseline_index_mae: float | None
    eps_mae: float | None
    multiple_mae: float | None
    coverage_80: float | None
    validation_scheme: str
    publication_status: str
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class EquityStressArtifact:
    model_version: str
    eps_response: dict[str, float]
    multiple_response: dict[str, float]
    joint_residuals: tuple[tuple[float, float], ...]
    validation_metrics: dict[str, object]
    trained_through: str | None
    publication_status: str
    reason_codes: tuple[str, ...]
    latest_measured_next_year_eps_revision_pct: float | None
    forecast_horizon: str = "calendar_year_end"


def _timestamp(value: object, *, field: str) -> pd.Timestamp:
    try:
        parsed = pd.Timestamp(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field}: {value!r}") from exc
    if pd.isna(parsed):
        raise ValueError(f"Invalid {field}: {value!r}")
    if parsed.tzinfo is not None:
        parsed = parsed.tz_convert("UTC").tz_localize(None)
    return parsed.normalize()


def _finite(value: object, *, field: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be finite") from exc
    if not math.isfinite(parsed):
        raise ValueError(f"{field} must be finite")
    return parsed


def _price_frame(
    rows: Sequence[Mapping[str, object]], *, as_of: pd.Timestamp
) -> pd.DataFrame:
    normalized: list[dict[str, object]] = []
    for raw in rows:
        date_value = raw.get("Date", raw.get("date", raw.get("observation_date")))
        close_value = raw.get("Close", raw.get("close", raw.get("spx_level")))
        try:
            observed = _timestamp(date_value, field="price date")
            close = _finite(close_value, field="index close")
        except ValueError:
            continue
        if observed > as_of or close <= 0.0:
            continue
        normalized.append({"date": observed, "close": close})
    if not normalized:
        return pd.DataFrame(columns=("date", "close", "month"))
    frame = pd.DataFrame(normalized).sort_values("date")
    frame["month"] = frame["date"].dt.to_period("M")
    return frame.drop_duplicates("date", keep="last").reset_index(drop=True)


def _eps_frame(
    rows: Sequence[Mapping[str, object]], *, as_of: pd.Timestamp
) -> pd.DataFrame:
    normalized: list[dict[str, object]] = []
    for raw in rows:
        if str(raw.get("period_type") or "quarterly").lower() != "quarterly":
            continue
        basis = str(raw.get("earnings_basis") or "").lower()
        if basis not in {"operating", "as_reported"}:
            continue
        status = str(raw.get("value_status") or "estimate").lower()
        if status not in {"actual", "estimate", "mixed"}:
            continue
        try:
            period_end = _timestamp(raw.get("period_end"), field="period_end")
            released = _timestamp(
                raw.get("source_release_date"), field="source_release_date"
            )
            eps = _finite(raw.get("eps"), field="EPS")
        except ValueError:
            continue
        if released > as_of or eps <= 0.0:
            continue
        normalized.append(
            {
                "period_end": period_end,
                "released": released,
                "basis": basis,
                "status": status,
                "eps": eps,
            }
        )
    return pd.DataFrame(normalized)


def _forward_eps_at(
    eps: pd.DataFrame,
    *,
    cutoff: pd.Timestamp,
    target_year: int,
) -> tuple[float, pd.Timestamp, dict[pd.Timestamp, float]] | None:
    if eps.empty:
        return None
    eligible = eps.loc[
        (eps["released"] <= cutoff) & (eps["period_end"].dt.year == target_year)
    ].copy()
    if eligible.empty:
        return None
    expected_periods = {
        pd.Timestamp(date(target_year, month, day))
        for month, day in ((3, 31), (6, 30), (9, 30), (12, 31))
    }
    status_rank = {"estimate": 0, "mixed": 1, "actual": 2}
    eligible["status_rank"] = eligible["status"].map(status_rank).fillna(-1)
    for basis in ("operating", "as_reported"):
        basis_rows = eligible.loc[eligible["basis"] == basis].sort_values(
            ["period_end", "released", "status_rank"]
        )
        if basis_rows.empty:
            continue
        selected = basis_rows.drop_duplicates("period_end", keep="last")
        selected = selected.loc[selected["period_end"].isin(expected_periods)]
        if set(selected["period_end"]) != expected_periods:
            continue
        values = {
            pd.Timestamp(row.period_end): float(row.eps)
            for row in selected.itertuples()
        }
        return (
            float(sum(values.values())),
            pd.Timestamp(selected["released"].max()),
            values,
        )
    return None


def _measured_revision(
    eps: pd.DataFrame,
    *,
    selected: tuple[float, pd.Timestamp, dict[pd.Timestamp, float]],
    target_year: int,
) -> float | None:
    current_value, release, _values = selected
    prior = _forward_eps_at(
        eps,
        cutoff=release - pd.Timedelta(days=1),
        target_year=target_year,
    )
    if prior is None or prior[0] <= 0.0:
        return None
    return (current_value / prior[0] - 1.0) * 100.0


def _yield_series(
    rows: Sequence[Mapping[str, object]], *, as_of: pd.Timestamp
) -> dict[str, pd.DataFrame]:
    by_series: dict[str, list[dict[str, object]]] = {}
    for raw in rows:
        series_id = str(raw.get("series_id") or "").upper()
        if series_id not in {"DGS2", "DGS10", "DFII10", "T10YIE"}:
            continue
        try:
            observed = _timestamp(raw.get("observation_date"), field="yield date")
            released = _timestamp(raw.get("released_at") or observed, field="released_at")
            value = _finite(raw.get("value"), field=series_id)
        except ValueError:
            continue
        if observed > as_of or released > as_of:
            continue
        by_series.setdefault(series_id, []).append(
            {"date": observed, "released": released, "value": value}
        )
    result: dict[str, pd.DataFrame] = {}
    for series_id, values in by_series.items():
        frame = pd.DataFrame(values).sort_values(["date", "released"])
        result[series_id] = frame.drop_duplicates("date", keep="last").reset_index(
            drop=True
        )
    return result


def _yield_at(
    series: dict[str, pd.DataFrame], *, origin: pd.Timestamp
) -> dict[str, float | None]:
    levels: dict[str, float | None] = {}
    changes: dict[str, float | None] = {}
    for series_id in ("DGS2", "DGS10", "DFII10", "T10YIE"):
        frame = series.get(series_id)
        eligible = frame.loc[frame["date"] <= origin] if frame is not None else None
        if eligible is None or eligible.empty:
            levels[series_id] = None
            changes[series_id] = None
            continue
        levels[series_id] = float(eligible.iloc[-1]["value"])
        prior_index = max(0, len(eligible) - 22)
        changes[series_id] = (
            float(eligible.iloc[-1]["value"] - eligible.iloc[prior_index]["value"])
            * 100.0
        )
    return {
        "dgs2_pct": levels["DGS2"],
        "dgs10_pct": levels["DGS10"],
        "real_yield_10y_pct": levels["DFII10"],
        "breakeven_10y_pct": levels["T10YIE"],
        "policy_repricing_bp": changes["DGS2"],
        "dgs10_change_bp": changes["DGS10"],
        "real_yield_change_bp": changes["DFII10"],
        "breakeven_change_bp": changes["T10YIE"],
    }


def _pct_change(future: float | None, current: float) -> float | None:
    if future is None or current <= 0.0:
        return None
    return (future / current - 1.0) * 100.0


def build_equity_calibration_panel(
    *,
    price_rows: Sequence[Mapping[str, object]],
    eps_rows: Sequence[Mapping[str, object]],
    yield_rows: Sequence[Mapping[str, object]],
    as_of_at: str | datetime,
) -> pd.DataFrame:
    """Build monthly origins without exposing later EPS releases to their features."""

    as_of = _timestamp(as_of_at, field="as_of_at")
    prices = _price_frame(price_rows, as_of=as_of)
    eps = _eps_frame(eps_rows, as_of=as_of)
    if prices.empty or eps.empty:
        return pd.DataFrame(columns=PANEL_COLUMNS)
    month_ends = prices.sort_values("date").drop_duplicates("month", keep="last")
    yields = _yield_series(yield_rows, as_of=as_of)
    rows: list[dict[str, object]] = []
    for price in month_ends.itertuples():
        origin = pd.Timestamp(price.date)
        target_year = origin.year + 1
        current_eps = _forward_eps_at(eps, cutoff=origin, target_year=target_year)
        if current_eps is None:
            continue
        current_eps_value, eps_release, _current_quarters = current_eps
        current_index = float(price.close)
        current_multiple = current_index / current_eps_value
        year_prices = prices.loc[prices["date"].dt.year == origin.year]
        endpoint_row = year_prices.iloc[-1] if not year_prices.empty else None
        year_complete = as_of.date() > date(origin.year, 12, 31)
        endpoint_date = (
            pd.Timestamp(endpoint_row["date"])
            if endpoint_row is not None and year_complete
            else None
        )
        future_index = (
            float(endpoint_row["close"])
            if endpoint_row is not None and year_complete and endpoint_date >= origin
            else None
        )
        future_eps_record = (
            _forward_eps_at(eps, cutoff=endpoint_date, target_year=target_year)
            if endpoint_date is not None
            else None
        )
        future_eps = future_eps_record[0] if future_eps_record else None
        future_multiple = (
            future_index / future_eps
            if future_index is not None and future_eps is not None and future_eps > 0.0
            else None
        )
        rows.append(
            {
                "origin_date": origin.strftime("%Y-%m-%d"),
                "eps_source_release_date": eps_release.strftime("%Y-%m-%d"),
                "target_eps_year": target_year,
                "current_index_level": current_index,
                "forward_eps": current_eps_value,
                "forward_multiple": current_multiple,
                "measured_next_year_eps_revision_pct": _measured_revision(
                    eps, selected=current_eps, target_year=target_year
                ),
                "months_to_year_end": 12 - origin.month,
                **_yield_at(yields, origin=origin),
                "future_index_level": future_index,
                "future_forward_eps": future_eps,
                "future_forward_multiple": future_multiple,
                "eps_change_pct": _pct_change(future_eps, current_eps_value),
                "multiple_change_pct": _pct_change(
                    future_multiple, current_multiple
                ),
                "index_change_pct": _pct_change(future_index, current_index),
            }
        )
    return pd.DataFrame(rows, columns=PANEL_COLUMNS)


def _completed_panel(panel: pd.DataFrame) -> pd.DataFrame:
    required = {
        "origin_date",
        *EQUITY_FEATURES,
        "eps_change_pct",
        "multiple_change_pct",
        "index_change_pct",
    }
    if not required.issubset(panel.columns):
        return pd.DataFrame(columns=sorted(required))
    frame = panel.copy()
    frame["origin_date"] = pd.to_datetime(frame["origin_date"], errors="coerce")
    for column in (*EQUITY_FEATURES, "eps_change_pct", "multiple_change_pct", "index_change_pct"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = frame.replace([np.inf, -np.inf], np.nan)
    return (
        frame.dropna(
            subset=("origin_date", "eps_change_pct", "multiple_change_pct", "index_change_pct")
        )
        .sort_values("origin_date")
        .reset_index(drop=True)
    )


def _feature_matrix(frame: pd.DataFrame) -> np.ndarray:
    values = frame.loc[:, EQUITY_FEATURES].to_numpy(dtype=float)
    for column in range(values.shape[1]):
        finite = np.isfinite(values[:, column])
        replacement = float(np.median(values[finite, column])) if finite.any() else 0.0
        values[~finite, column] = replacement
    return values


def _fit_ridge_coefficients(
    frame: pd.DataFrame, *, target: str, ridge_alpha: float
) -> dict[str, float]:
    x = _feature_matrix(frame)
    y = frame[target].to_numpy(dtype=float)
    means = x.mean(axis=0)
    scales = x.std(axis=0)
    scales[scales <= 1e-12] = 1.0
    standardized = (x - means) / scales
    design = np.column_stack((np.ones(len(standardized)), standardized))
    penalty = np.eye(design.shape[1]) * float(ridge_alpha)
    penalty[0, 0] = 0.0
    beta = np.linalg.solve(design.T @ design + penalty, design.T @ y)
    slopes = beta[1:] / scales
    intercept = float(beta[0] - np.dot(slopes, means))
    return {
        "intercept": intercept,
        **{
            feature: float(value)
            for feature, value in zip(EQUITY_FEATURES, slopes, strict=True)
        },
    }


def _predict_response(
    frame: pd.DataFrame, coefficients: Mapping[str, object]
) -> np.ndarray:
    x = _feature_matrix(frame)
    slopes = np.asarray(
        [float(coefficients.get(feature, 0.0)) for feature in EQUITY_FEATURES],
        dtype=float,
    )
    return float(coefficients.get("intercept", 0.0)) + x @ slopes


def _combined_index_change(eps_change: float, multiple_change: float) -> float:
    return ((1.0 + eps_change / 100.0) * (1.0 + multiple_change / 100.0) - 1.0) * 100.0


def rolling_origin_validate_equity_stress(
    panel: pd.DataFrame,
    *,
    minimum_origins: int = 60,
    ridge_alpha: float = 1.0,
) -> EquityStressValidationReport:
    """Evaluate only on origins after their expanding training window."""

    frame = _completed_panel(panel)
    count = len(frame)
    if count < int(minimum_origins):
        return EquityStressValidationReport(
            origin_count=count,
            fold_count=0,
            index_mae=None,
            baseline_index_mae=None,
            eps_mae=None,
            multiple_mae=None,
            coverage_80=None,
            validation_scheme="rolling_origin",
            publication_status="NOT_AVAILABLE",
            reason_codes=("insufficient_origins",),
        )
    minimum_training = max(24, min(36, int(minimum_origins) // 2))
    model_errors: list[float] = []
    baseline_errors: list[float] = []
    eps_errors: list[float] = []
    multiple_errors: list[float] = []
    covered: list[float] = []
    for index in range(minimum_training, count):
        training = frame.iloc[:index]
        evaluation = frame.iloc[[index]]
        eps_coefficients = _fit_ridge_coefficients(
            training, target="eps_change_pct", ridge_alpha=ridge_alpha
        )
        multiple_coefficients = _fit_ridge_coefficients(
            training, target="multiple_change_pct", ridge_alpha=ridge_alpha
        )
        predicted_eps = float(_predict_response(evaluation, eps_coefficients)[0])
        predicted_multiple = float(
            _predict_response(evaluation, multiple_coefficients)[0]
        )
        predicted_index = _combined_index_change(predicted_eps, predicted_multiple)
        actual_eps = float(evaluation.iloc[0]["eps_change_pct"])
        actual_multiple = float(evaluation.iloc[0]["multiple_change_pct"])
        actual_index = float(evaluation.iloc[0]["index_change_pct"])
        baseline_eps = float(training["eps_change_pct"].median())
        baseline_multiple = float(training["multiple_change_pct"].median())
        baseline_index = _combined_index_change(baseline_eps, baseline_multiple)
        model_errors.append(abs(predicted_index - actual_index))
        baseline_errors.append(abs(baseline_index - actual_index))
        eps_errors.append(abs(predicted_eps - actual_eps))
        multiple_errors.append(abs(predicted_multiple - actual_multiple))

        train_eps_predictions = _predict_response(training, eps_coefficients)
        train_multiple_predictions = _predict_response(training, multiple_coefficients)
        train_index_predictions = np.asarray(
            [
                _combined_index_change(eps_value, multiple_value)
                for eps_value, multiple_value in zip(
                    train_eps_predictions, train_multiple_predictions, strict=True
                )
            ]
        )
        residuals = training["index_change_pct"].to_numpy(dtype=float) - train_index_predictions
        lower, upper = np.quantile(residuals, (0.10, 0.90))
        covered.append(
            float(predicted_index + lower <= actual_index <= predicted_index + upper)
        )
    index_mae = float(np.mean(model_errors))
    baseline_mae = float(np.mean(baseline_errors))
    reasons: list[str] = []
    if index_mae >= baseline_mae - 1e-12:
        reasons.append("baseline_not_beaten")
    status = "READY" if not reasons else "LIMITED"
    return EquityStressValidationReport(
        origin_count=count,
        fold_count=len(model_errors),
        index_mae=index_mae,
        baseline_index_mae=baseline_mae,
        eps_mae=float(np.mean(eps_errors)),
        multiple_mae=float(np.mean(multiple_errors)),
        coverage_80=float(np.mean(covered)),
        validation_scheme="rolling_origin",
        publication_status=status,
        reason_codes=tuple(reasons),
    )


def _empty_artifact(
    *,
    frame: pd.DataFrame,
    report: EquityStressValidationReport,
    model_version: str,
) -> EquityStressArtifact:
    latest_revision: float | None = None
    if not frame.empty and "measured_next_year_eps_revision_pct" in frame:
        revisions = pd.to_numeric(
            frame["measured_next_year_eps_revision_pct"], errors="coerce"
        ).dropna()
        latest_revision = float(revisions.iloc[-1]) if not revisions.empty else None
    return EquityStressArtifact(
        model_version=model_version,
        eps_response={},
        multiple_response={},
        joint_residuals=(),
        validation_metrics={
            "origin_count": float(report.origin_count),
            "fold_count": float(report.fold_count),
            "validation_scheme": report.validation_scheme,
        },
        trained_through=(
            pd.Timestamp(frame.iloc[-1]["origin_date"]).strftime("%Y-%m-%d")
            if not frame.empty
            else None
        ),
        publication_status=report.publication_status,
        reason_codes=report.reason_codes,
        latest_measured_next_year_eps_revision_pct=latest_revision,
    )


def fit_equity_stress_model(
    panel: pd.DataFrame,
    *,
    minimum_origins: int = 60,
    ridge_alpha: float = 1.0,
    model_version: str = "equity-stress-year-end-v1",
) -> EquityStressArtifact:
    """Fit paired EPS/multiple responses after a chronological publication gate."""

    frame = _completed_panel(panel)
    report = rolling_origin_validate_equity_stress(
        frame, minimum_origins=minimum_origins, ridge_alpha=ridge_alpha
    )
    if report.publication_status == "NOT_AVAILABLE":
        return _empty_artifact(
            frame=frame, report=report, model_version=str(model_version)
        )
    eps_coefficients = _fit_ridge_coefficients(
        frame, target="eps_change_pct", ridge_alpha=ridge_alpha
    )
    multiple_coefficients = _fit_ridge_coefficients(
        frame, target="multiple_change_pct", ridge_alpha=ridge_alpha
    )
    eps_predictions = _predict_response(frame, eps_coefficients)
    multiple_predictions = _predict_response(frame, multiple_coefficients)
    residuals = tuple(
        (float(actual_eps - predicted_eps), float(actual_multiple - predicted_multiple))
        for actual_eps, predicted_eps, actual_multiple, predicted_multiple in zip(
            frame["eps_change_pct"].to_numpy(dtype=float),
            eps_predictions,
            frame["multiple_change_pct"].to_numpy(dtype=float),
            multiple_predictions,
            strict=True,
        )
    )
    revisions = pd.to_numeric(
        frame["measured_next_year_eps_revision_pct"], errors="coerce"
    ).dropna()
    validation_metrics: dict[str, object] = {
        "origin_count": float(report.origin_count),
        "fold_count": float(report.fold_count),
        "index_mae": float(report.index_mae or 0.0),
        "baseline_index_mae": float(report.baseline_index_mae or 0.0),
        "eps_mae": float(report.eps_mae or 0.0),
        "multiple_mae": float(report.multiple_mae or 0.0),
        "coverage_80": float(report.coverage_80 or 0.0),
        "validation_scheme": report.validation_scheme,
    }
    return EquityStressArtifact(
        model_version=str(model_version),
        eps_response=eps_coefficients,
        multiple_response=multiple_coefficients,
        joint_residuals=residuals,
        validation_metrics=validation_metrics,
        trained_through=pd.Timestamp(frame.iloc[-1]["origin_date"]).strftime(
            "%Y-%m-%d"
        ),
        publication_status=report.publication_status,
        reason_codes=report.reason_codes,
        latest_measured_next_year_eps_revision_pct=(
            float(revisions.iloc[-1]) if not revisions.empty else None
        ),
    )
