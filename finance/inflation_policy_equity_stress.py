"""Point-in-time S&P 500 EPS and multiple stress analysis."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime, timezone

import numpy as np
import pandas as pd

from finance.inflation_policy_simulation import SimulationPath


PANEL_COLUMNS = (
    "origin_date",
    "label_available_at",
    "eps_source_release_date",
    "target_eps_year",
    "current_index_level",
    "forward_eps",
    "forward_multiple",
    "measured_next_year_eps_revision_pct",
    "months_to_year_end",
    "q4_core_pce_pct",
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
    "q4_core_pce_pct",
    "policy_repricing_bp",
    "dgs10_change_bp",
    "real_yield_change_bp",
    "breakeven_change_bp",
)

EQUITY_PUBLICATION_CONTRACT_VERSION = "equity-stress-publication-v1"
DEFAULT_MAXIMUM_COVERAGE_80_ERROR = 0.15
MAX_RESIDUAL_DRAWS_PER_PATH = 16
MINIMUM_OOS_INTERVAL_RESIDUALS = 12
EQUITY_RIDGE_ALPHA_CANDIDATES = (1.0, 3.0, 10.0, 30.0, 100.0)
MINIMUM_INNER_RIDGE_TRAINING_ROWS = 18
MINIMUM_INNER_RIDGE_FOLDS = 6


@dataclass(frozen=True)
class EquityStressValidationReport:
    origin_count: int
    fold_count: int
    interval_fold_count: int
    index_mae: float | None
    baseline_index_mae: float | None
    baseline_mae_by_name: dict[str, float]
    eps_mae: float | None
    multiple_mae: float | None
    coverage_80: float | None
    validation_scheme: str
    publication_status: str
    reason_codes: tuple[str, ...]
    joint_oos_residuals: tuple[tuple[float, float], ...]


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
    scenario_feature_values: dict[str, float] = field(default_factory=dict)
    forecast_horizon: str = "calendar_year_end"


@dataclass(frozen=True)
class EquityStressResult:
    as_of_at: str | None
    index_quantiles: dict[str, float]
    eps_quantiles: dict[str, float]
    multiple_quantiles: dict[str, float]
    threshold_probabilities: dict[str, float]
    target_decompositions: dict[str, dict[str, object]]
    measured_next_year_eps_revision_pct: float | None
    user_ai_eps_uplift_pct: float
    publication_status: str
    reason_codes: tuple[str, ...]
    scenario_kind: str
    current_index_level: float
    base_forward_eps: float
    scenario_feature_values: dict[str, float] = field(default_factory=dict)


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


def _instant(value: object, *, field: str, date_only_at_end: bool = False) -> pd.Timestamp:
    try:
        parsed = pd.Timestamp(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field}: {value!r}") from exc
    if pd.isna(parsed):
        raise ValueError(f"Invalid {field}: {value!r}")
    if parsed.tzinfo is not None:
        parsed = parsed.tz_convert("UTC").tz_localize(None)
    date_only = (
        isinstance(value, date)
        and not isinstance(value, datetime)
        or isinstance(value, str)
        and len(value.strip()) == 10
    )
    if date_only_at_end and date_only:
        parsed = parsed.normalize() + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
    return parsed


def _end_of_day(value: pd.Timestamp) -> pd.Timestamp:
    return value.normalize() + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)


def _known_price_cutoff(as_of: pd.Timestamp) -> pd.Timestamp:
    """Conservatively map an exact UTC cutoff to the latest known US close."""

    utc = as_of.tz_localize("UTC") if as_of.tzinfo is None else as_of.tz_convert("UTC")
    eastern = utc.tz_convert("America/New_York")
    cutoff = eastern.normalize()
    if eastern.hour < 16:
        cutoff -= pd.Timedelta(days=1)
    return cutoff.tz_localize(None)


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
    known_close_date = _known_price_cutoff(as_of)
    normalized: list[dict[str, object]] = []
    for raw in rows:
        date_value = raw.get("Date", raw.get("date", raw.get("observation_date")))
        close_value = raw.get("Close", raw.get("close", raw.get("spx_level")))
        try:
            observed = _timestamp(date_value, field="price date")
            close = _finite(close_value, field="index close")
        except ValueError:
            continue
        if observed > known_close_date or close <= 0.0:
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
        period_type = str(raw.get("period_type") or "quarterly").lower()
        if period_type not in {"quarterly", "annual"}:
            continue
        basis = str(raw.get("earnings_basis") or "").lower()
        if basis not in {"operating", "as_reported"}:
            continue
        status = str(raw.get("value_status") or "estimate").lower()
        if status not in {"actual", "estimate", "mixed"}:
            continue
        try:
            period_end = _timestamp(raw.get("period_end"), field="period_end")
            released = _instant(
                raw.get("source_release_date"),
                field="source_release_date",
                date_only_at_end=True,
            )
            eps = _finite(raw.get("eps"), field="EPS")
        except ValueError:
            continue
        if released > as_of or eps <= 0.0:
            continue
        normalized.append(
            {
                "period_end": period_end,
                "period_type": period_type,
                "released": released,
                "basis": basis,
                "status": status,
                "eps": eps,
                "source": str(raw.get("source") or ""),
                "source_ref": str(raw.get("source_ref") or ""),
            }
        )
    return pd.DataFrame(normalized)


def _forward_eps_at(
    eps: pd.DataFrame,
    *,
    cutoff: pd.Timestamp,
    target_year: int,
) -> tuple[
    float,
    pd.Timestamp,
    dict[pd.Timestamp, float],
    str,
    str,
    str,
] | None:
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
    complete: list[
        tuple[int, pd.Timestamp, int, str, str, pd.DataFrame, float]
    ] = []
    for (basis, source, source_ref, released), rows in eligible.groupby(
        ["basis", "source", "source_ref", "released"], dropna=False
    ):
        annual = rows.loc[
            (rows["period_type"] == "annual")
            & (rows["period_end"] == pd.Timestamp(date(target_year, 12, 31)))
        ].sort_values("status_rank")
        if not annual.empty:
            selected_annual = annual.iloc[[-1]]
            complete.append(
                (
                    1 if str(basis) == "operating" else 0,
                    pd.Timestamp(released),
                    1,
                    str(source),
                    str(source_ref),
                    selected_annual,
                    float(selected_annual.iloc[0]["eps"]),
                )
            )
        selected = rows.sort_values(["period_end", "status_rank"]).drop_duplicates(
            "period_end", keep="last"
        )
        selected = selected.loc[
            (selected["period_type"] == "quarterly")
            & selected["period_end"].isin(expected_periods)
        ]
        if set(selected["period_end"]) != expected_periods:
            continue
        complete.append(
            (
                1 if str(basis) == "operating" else 0,
                pd.Timestamp(released),
                0,
                str(source),
                str(source_ref),
                selected,
                float(selected["eps"].sum()),
            )
        )
    if complete:
        _basis_rank, released, _annual_rank, source, source_ref, selected, total = max(
            complete, key=lambda item: (item[1], item[0], item[2], item[3], item[4])
        )
        values = {
            pd.Timestamp(row.period_end): float(row.eps)
            for row in selected.itertuples()
        }
        return (
            total,
            released,
            values,
            str(selected.iloc[0]["basis"]),
            source,
            source_ref,
        )
    return None


def _measured_revision(
    eps: pd.DataFrame,
    *,
    selected: tuple[
        float,
        pd.Timestamp,
        dict[pd.Timestamp, float],
        str,
        str,
        str,
    ],
    target_year: int,
) -> float | None:
    current_value, release, _values, basis, source, _source_ref = selected
    prior = _forward_eps_at(
        eps.loc[(eps["basis"] == basis) & (eps["source"] == source)],
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
        if series_id not in {"DGS2", "DGS10", "DFII10", "T10YIE", "PCEPILFE"}:
            continue
        try:
            observed = _timestamp(raw.get("observation_date"), field="yield date")
            released = _instant(
                raw.get("released_at") or observed,
                field="released_at",
                date_only_at_end=True,
            )
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
        result[series_id] = pd.DataFrame(values).sort_values(
            ["date", "released"]
        ).reset_index(drop=True)
    return result


def _series_value_at(
    frame: pd.DataFrame | None, *, cutoff: pd.Timestamp
) -> float | None:
    if frame is None or frame.empty:
        return None
    eligible = frame.loc[
        (frame["date"] <= cutoff.normalize()) & (frame["released"] <= cutoff)
    ].sort_values(["date", "released"])
    if eligible.empty:
        return None
    selected = eligible.drop_duplicates("date", keep="last")
    return float(selected.iloc[-1]["value"])


def _q4_core_pce_at(
    series: dict[str, pd.DataFrame], *, target_year: int
) -> tuple[float | None, pd.Timestamp | None]:
    frame = series.get("PCEPILFE")
    if frame is None or frame.empty:
        return None, None
    december = frame.loc[
        (frame["date"].dt.year == target_year) & (frame["date"].dt.month == 12)
    ].sort_values("released")
    required = {
        pd.Timestamp(date(year, month, 1))
        for year in (target_year - 1, target_year)
        for month in (10, 11, 12)
    }
    for release in december["released"].drop_duplicates():
        eligible = frame.loc[
            (frame["date"].isin(required)) & (frame["released"] <= release)
        ].sort_values(["date", "released"])
        selected = eligible.drop_duplicates("date", keep="last")
        if set(selected["date"]) != required:
            continue
        values = {pd.Timestamp(row.date): float(row.value) for row in selected.itertuples()}
        prior = sum(values[pd.Timestamp(date(target_year - 1, month, 1))] for month in (10, 11, 12)) / 3.0
        current = sum(values[pd.Timestamp(date(target_year, month, 1))] for month in (10, 11, 12)) / 3.0
        if prior > 0.0:
            return (current / prior - 1.0) * 100.0, pd.Timestamp(release)
    return None, None


def _yield_path_features(
    series: dict[str, pd.DataFrame],
    *,
    origin: pd.Timestamp,
    endpoint: pd.Timestamp | None,
) -> dict[str, float | None]:
    current: dict[str, float | None] = {}
    future: dict[str, float | None] = {}
    origin_cutoff = _end_of_day(origin)
    endpoint_cutoff = _end_of_day(endpoint) if endpoint is not None else None
    for series_id in ("DGS2", "DGS10", "DFII10", "T10YIE"):
        frame = series.get(series_id)
        current[series_id] = _series_value_at(frame, cutoff=origin_cutoff)
        future[series_id] = (
            _series_value_at(frame, cutoff=endpoint_cutoff)
            if endpoint_cutoff is not None
            else None
        )

    def change(series_id: str) -> float | None:
        start = current[series_id]
        end = future[series_id]
        return (end - start) * 100.0 if start is not None and end is not None else None

    return {
        "dgs2_pct": current["DGS2"],
        "dgs10_pct": current["DGS10"],
        "real_yield_10y_pct": current["DFII10"],
        "breakeven_10y_pct": current["T10YIE"],
        "policy_repricing_bp": change("DGS2"),
        "dgs10_change_bp": change("DGS10"),
        "real_yield_change_bp": change("DFII10"),
        "breakeven_change_bp": change("T10YIE"),
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

    as_of = _instant(as_of_at, field="as_of_at", date_only_at_end=True)
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
        current_eps = _forward_eps_at(
            eps, cutoff=_end_of_day(origin), target_year=target_year
        )
        if current_eps is None:
            continue
        (
            current_eps_value,
            eps_release,
            _current_quarters,
            _eps_basis,
            _eps_source,
            _eps_source_ref,
        ) = current_eps
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
            _forward_eps_at(
                eps, cutoff=_end_of_day(endpoint_date), target_year=target_year
            )
            if endpoint_date is not None
            else None
        )
        future_eps = future_eps_record[0] if future_eps_record else None
        future_multiple = (
            future_index / future_eps
            if future_index is not None and future_eps is not None and future_eps > 0.0
            else None
        )
        q4_core_pce_pct, q4_available_at = _q4_core_pce_at(
            yields, target_year=origin.year
        )
        label_available_at = None
        if endpoint_date is not None:
            label_available_at = max(
                _end_of_day(endpoint_date),
                q4_available_at or _end_of_day(endpoint_date),
            )
        rows.append(
            {
                "origin_date": origin.strftime("%Y-%m-%d"),
                "label_available_at": (
                    label_available_at.isoformat() if label_available_at is not None else None
                ),
                "eps_source_release_date": eps_release.date().isoformat(),
                "target_eps_year": target_year,
                "current_index_level": current_index,
                "forward_eps": current_eps_value,
                "forward_multiple": current_multiple,
                "measured_next_year_eps_revision_pct": _measured_revision(
                    eps, selected=current_eps, target_year=target_year
                ),
                "months_to_year_end": 12 - origin.month,
                "q4_core_pce_pct": q4_core_pce_pct,
                **_yield_path_features(
                    yields, origin=origin, endpoint=endpoint_date
                ),
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
        "label_available_at",
        *EQUITY_FEATURES,
        "eps_change_pct",
        "multiple_change_pct",
        "index_change_pct",
    }
    if not required.issubset(panel.columns):
        return pd.DataFrame(columns=sorted(required))
    frame = panel.copy()
    frame["origin_date"] = pd.to_datetime(frame["origin_date"], errors="coerce")
    frame["label_available_at"] = pd.to_datetime(
        frame["label_available_at"], errors="coerce"
    )
    for column in (*EQUITY_FEATURES, "eps_change_pct", "multiple_change_pct", "index_change_pct"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = frame.replace([np.inf, -np.inf], np.nan)
    return (
        frame.dropna(
            subset=(
                "origin_date",
                "label_available_at",
                *EQUITY_FEATURES,
                "eps_change_pct",
                "multiple_change_pct",
                "index_change_pct",
            )
        )
        .sort_values("origin_date")
        .reset_index(drop=True)
    )


def _feature_matrix(frame: pd.DataFrame) -> np.ndarray:
    values = frame.loc[:, EQUITY_FEATURES].to_numpy(dtype=float).copy()
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


def _normalized_ridge_candidates(
    values: Sequence[float] | None,
) -> tuple[float, ...]:
    candidates = tuple(
        sorted(
            {
                float(value)
                for value in (values or ())
                if math.isfinite(float(value)) and float(value) > 0.0
            }
        )
    )
    if values is not None and not candidates:
        raise ValueError("ridge_alpha_candidates require positive finite values")
    return candidates


def _select_ridge_alpha(
    frame: pd.DataFrame,
    *,
    candidates: Sequence[float],
) -> float:
    """Select regularization only from chronological folds inside the caller's training set."""

    resolved = _normalized_ridge_candidates(candidates)
    scores: dict[float, list[float]] = {value: [] for value in resolved}
    for index in range(len(frame)):
        evaluation = frame.iloc[[index]]
        origin = pd.Timestamp(evaluation.iloc[0]["origin_date"])
        training = frame.loc[frame["label_available_at"] <= origin]
        if len(training) < MINIMUM_INNER_RIDGE_TRAINING_ROWS:
            continue
        actual_index = float(evaluation.iloc[0]["index_change_pct"])
        for alpha in resolved:
            eps_response = _fit_ridge_coefficients(
                training, target="eps_change_pct", ridge_alpha=alpha
            )
            multiple_response = _fit_ridge_coefficients(
                training, target="multiple_change_pct", ridge_alpha=alpha
            )
            predicted_index = _combined_index_change(
                float(_predict_response(evaluation, eps_response)[0]),
                float(_predict_response(evaluation, multiple_response)[0]),
            )
            scores[alpha].append(abs(predicted_index - actual_index))
    eligible = [
        (float(np.mean(errors)), -alpha, alpha)
        for alpha, errors in scores.items()
        if len(errors) >= MINIMUM_INNER_RIDGE_FOLDS
    ]
    # Sparse early windows use the strongest predeclared regularization instead
    # of choosing on the outer evaluation target.
    return min(eligible)[2] if eligible else max(resolved)


def rolling_origin_validate_equity_stress(
    panel: pd.DataFrame,
    *,
    minimum_origins: int = 60,
    ridge_alpha: float = 1.0,
    ridge_alpha_candidates: Sequence[float] | None = None,
    maximum_coverage_80_error: float = DEFAULT_MAXIMUM_COVERAGE_80_ERROR,
) -> EquityStressValidationReport:
    """Evaluate only on origins after their expanding training window."""

    frame = _completed_panel(panel)
    candidates = _normalized_ridge_candidates(ridge_alpha_candidates)
    count = len(frame)
    if count < int(minimum_origins):
        return EquityStressValidationReport(
            origin_count=count,
            fold_count=0,
            interval_fold_count=0,
            index_mae=None,
            baseline_index_mae=None,
            baseline_mae_by_name={},
            eps_mae=None,
            multiple_mae=None,
            coverage_80=None,
            validation_scheme="rolling_origin",
            publication_status="NOT_AVAILABLE",
            reason_codes=("insufficient_origins",),
            joint_oos_residuals=(),
        )
    minimum_training = max(24, min(36, int(minimum_origins) // 2))
    model_errors: list[float] = []
    baseline_errors: dict[str, list[float]] = {
        "constant_eps": [],
        "constant_multiple": [],
        "unconditional_index_change": [],
    }
    eps_errors: list[float] = []
    multiple_errors: list[float] = []
    covered: list[float] = []
    prior_oos_residuals: list[float] = []
    joint_oos_residuals: list[tuple[float, float]] = []
    for index in range(count):
        evaluation = frame.iloc[[index]]
        evaluation_origin = pd.Timestamp(evaluation.iloc[0]["origin_date"])
        training = frame.loc[frame["label_available_at"] <= evaluation_origin]
        if len(training) < minimum_training:
            continue
        selected_alpha = (
            _select_ridge_alpha(training, candidates=candidates)
            if candidates
            else float(ridge_alpha)
        )
        eps_coefficients = _fit_ridge_coefficients(
            training, target="eps_change_pct", ridge_alpha=selected_alpha
        )
        multiple_coefficients = _fit_ridge_coefficients(
            training, target="multiple_change_pct", ridge_alpha=selected_alpha
        )
        predicted_eps = float(_predict_response(evaluation, eps_coefficients)[0])
        predicted_multiple = float(
            _predict_response(evaluation, multiple_coefficients)[0]
        )
        predicted_index = _combined_index_change(predicted_eps, predicted_multiple)
        actual_eps = float(evaluation.iloc[0]["eps_change_pct"])
        actual_multiple = float(evaluation.iloc[0]["multiple_change_pct"])
        actual_index = float(evaluation.iloc[0]["index_change_pct"])
        model_errors.append(abs(predicted_index - actual_index))
        baseline_eps = float(training["eps_change_pct"].median())
        baseline_multiple = float(training["multiple_change_pct"].median())
        baseline_errors["constant_eps"].append(
            abs(_combined_index_change(0.0, baseline_multiple) - actual_index)
        )
        baseline_errors["constant_multiple"].append(
            abs(_combined_index_change(baseline_eps, 0.0) - actual_index)
        )
        baseline_errors["unconditional_index_change"].append(
            abs(float(training["index_change_pct"].median()) - actual_index)
        )
        eps_errors.append(abs(predicted_eps - actual_eps))
        multiple_errors.append(abs(predicted_multiple - actual_multiple))

        # In-sample residuals are too narrow after fitting and understated actual
        # year-end uncertainty. Calibrate only from errors produced by earlier,
        # chronologically completed evaluation folds.
        if len(prior_oos_residuals) >= MINIMUM_OOS_INTERVAL_RESIDUALS:
            lower, upper = np.quantile(
                prior_oos_residuals, (0.10, 0.90), method="inverted_cdf"
            )
            covered.append(
                float(predicted_index + lower <= actual_index <= predicted_index + upper)
            )
        prior_oos_residuals.append(actual_index - predicted_index)
        joint_oos_residuals.append(
            (actual_eps - predicted_eps, actual_multiple - predicted_multiple)
        )
    if not model_errors:
        return EquityStressValidationReport(
            origin_count=count,
            fold_count=0,
            interval_fold_count=0,
            index_mae=None,
            baseline_index_mae=None,
            baseline_mae_by_name={},
            eps_mae=None,
            multiple_mae=None,
            coverage_80=None,
            validation_scheme=(
                "rolling_origin_label_available_nested_ridge"
                if candidates
                else "rolling_origin_label_available"
            ),
            publication_status="NOT_AVAILABLE",
            reason_codes=("insufficient_validation_folds",),
            joint_oos_residuals=(),
        )
    index_mae = float(np.mean(model_errors))
    baseline_mae_by_name = {
        name: float(np.mean(errors)) for name, errors in baseline_errors.items()
    }
    baseline_mae = min(baseline_mae_by_name.values())
    coverage_80 = float(np.mean(covered)) if covered else None
    reasons: list[str] = []
    if index_mae >= baseline_mae - 1e-12:
        reasons.append("baseline_not_beaten")
    coverage_error = (
        abs(float(coverage_80) - 0.80) if coverage_80 is not None else math.inf
    )
    if coverage_error > float(maximum_coverage_80_error) + 1e-12:
        reasons.append("coverage_80_miscalibrated")
    status = "READY" if not reasons else "LIMITED"
    return EquityStressValidationReport(
        origin_count=count,
        fold_count=len(model_errors),
        interval_fold_count=len(covered),
        index_mae=index_mae,
        baseline_index_mae=baseline_mae,
        baseline_mae_by_name=baseline_mae_by_name,
        eps_mae=float(np.mean(eps_errors)),
        multiple_mae=float(np.mean(multiple_errors)),
        coverage_80=coverage_80,
        validation_scheme=(
            "rolling_origin_label_available_nested_ridge"
            if candidates
            else "rolling_origin_label_available"
        ),
        publication_status=status,
        reason_codes=tuple(reasons),
        joint_oos_residuals=tuple(joint_oos_residuals),
    )


def _empty_artifact(
    *,
    frame: pd.DataFrame,
    source_panel: pd.DataFrame,
    report: EquityStressValidationReport,
    model_version: str,
) -> EquityStressArtifact:
    latest_revision, scenario_features = _latest_scenario_values(source_panel)
    return EquityStressArtifact(
        model_version=model_version,
        eps_response={},
        multiple_response={},
        joint_residuals=(),
        validation_metrics={
            "training_start_date": (
                pd.Timestamp(frame.iloc[0]["origin_date"]).strftime("%Y-%m-%d")
                if not frame.empty
                else None
            ),
            "origin_count": float(report.origin_count),
            "fold_count": float(report.fold_count),
            "interval_fold_count": float(report.interval_fold_count),
            "interval_calibration_scheme": "prior_oos_residuals",
            "residual_calibration_scheme": "chronological_oos_fold_pairs",
            "validation_scheme": report.validation_scheme,
            "publication_contract_version": EQUITY_PUBLICATION_CONTRACT_VERSION,
            "baseline_mae_by_name": report.baseline_mae_by_name,
        },
        trained_through=(
            pd.Timestamp(frame.iloc[-1]["origin_date"]).strftime("%Y-%m-%d")
            if not frame.empty
            else None
        ),
        publication_status=report.publication_status,
        reason_codes=report.reason_codes,
        latest_measured_next_year_eps_revision_pct=latest_revision,
        scenario_feature_values=scenario_features,
    )


def _latest_scenario_values(
    panel: pd.DataFrame,
) -> tuple[float | None, dict[str, float]]:
    if panel.empty or "origin_date" not in panel:
        return None, {}
    source = panel.copy()
    source["origin_date"] = pd.to_datetime(source["origin_date"], errors="coerce")
    source = source.dropna(subset=("origin_date",)).sort_values("origin_date")
    if source.empty:
        return None, {}
    latest = source.iloc[-1]
    revision_value = pd.to_numeric(
        pd.Series([latest.get("measured_next_year_eps_revision_pct")]),
        errors="coerce",
    ).iloc[0]
    revision = float(revision_value) if not pd.isna(revision_value) else None
    context_fields = {
        "months_to_year_end",
        "dgs2_pct",
        "dgs10_pct",
        "real_yield_10y_pct",
        "breakeven_10y_pct",
    }
    features: dict[str, float] = {}
    for field_name in context_fields:
        value = pd.to_numeric(pd.Series([latest.get(field_name)]), errors="coerce").iloc[0]
        if not pd.isna(value) and math.isfinite(float(value)):
            features[field_name] = float(value)
    return revision, features


def build_equity_scenario_context(
    panel: pd.DataFrame, *, as_of_at: str | datetime
) -> dict[str, object]:
    """Return the latest live PIT inputs separately from completed training labels."""

    if panel.empty or "origin_date" not in panel:
        raise ValueError("equity scenario context requires at least one origin")
    cutoff = _instant(as_of_at, field="as_of_at")
    source = panel.copy()
    source["origin_date"] = pd.to_datetime(source["origin_date"], errors="coerce")
    source = source.loc[
        source["origin_date"].notna()
        & (source["origin_date"] <= cutoff.normalize())
    ].sort_values("origin_date")
    if source.empty:
        raise ValueError("equity scenario context has no eligible origin")
    current = source.iloc[-1]
    current_index = _finite(current.get("current_index_level"), field="current index")
    forward_eps = _finite(current.get("forward_eps"), field="forward EPS")
    if current_index <= 0.0 or forward_eps <= 0.0:
        raise ValueError("equity scenario index and forward EPS must be positive")
    revision, features = _latest_scenario_values(source)
    return {
        "as_of_at": str(as_of_at),
        "origin_date": pd.Timestamp(current["origin_date"]).strftime("%Y-%m-%d"),
        "current_index_level": current_index,
        "base_forward_eps": forward_eps,
        "measured_next_year_eps_revision_pct": revision,
        "scenario_feature_values": features,
    }


def fit_equity_stress_model(
    panel: pd.DataFrame,
    *,
    minimum_origins: int = 60,
    ridge_alpha: float = 1.0,
    ridge_alpha_candidates: Sequence[float] | None = None,
    maximum_coverage_80_error: float = DEFAULT_MAXIMUM_COVERAGE_80_ERROR,
    model_version: str = "equity-stress-year-end-v1",
) -> EquityStressArtifact:
    """Fit paired EPS/multiple responses after a chronological publication gate."""

    frame = _completed_panel(panel)
    report = rolling_origin_validate_equity_stress(
        frame,
        minimum_origins=minimum_origins,
        ridge_alpha=ridge_alpha,
        ridge_alpha_candidates=ridge_alpha_candidates,
        maximum_coverage_80_error=maximum_coverage_80_error,
    )
    if report.publication_status == "NOT_AVAILABLE":
        return _empty_artifact(
            frame=frame,
            source_panel=panel,
            report=report,
            model_version=str(model_version),
        )
    candidates = _normalized_ridge_candidates(ridge_alpha_candidates)
    deployment_alpha = (
        _select_ridge_alpha(frame, candidates=candidates)
        if candidates
        else float(ridge_alpha)
    )
    eps_coefficients = _fit_ridge_coefficients(
        frame, target="eps_change_pct", ridge_alpha=deployment_alpha
    )
    multiple_coefficients = _fit_ridge_coefficients(
        frame, target="multiple_change_pct", ridge_alpha=deployment_alpha
    )
    # The publication gate and the deployed distribution must describe the same
    # forecast errors. Persist only residual pairs generated by chronological OOS
    # folds, never the narrower in-sample errors of the final refit.
    residuals = report.joint_oos_residuals
    latest_revision, scenario_features = _latest_scenario_values(panel)
    validation_metrics: dict[str, object] = {
        "training_start_date": pd.Timestamp(frame.iloc[0]["origin_date"]).strftime(
            "%Y-%m-%d"
        ),
        "origin_count": float(report.origin_count),
        "fold_count": float(report.fold_count),
        "interval_fold_count": float(report.interval_fold_count),
        "interval_calibration_scheme": "prior_oos_residuals",
        "residual_calibration_scheme": "chronological_oos_fold_pairs",
        "index_mae": float(report.index_mae or 0.0),
        "baseline_index_mae": float(report.baseline_index_mae or 0.0),
        "eps_mae": float(report.eps_mae or 0.0),
        "multiple_mae": float(report.multiple_mae or 0.0),
        "coverage_80": float(report.coverage_80 or 0.0),
        "validation_scheme": report.validation_scheme,
        "publication_contract_version": EQUITY_PUBLICATION_CONTRACT_VERSION,
        "ridge_selection_scheme": (
            "nested_chronological_inner_mae" if candidates else "fixed"
        ),
        "ridge_alpha_candidates": list(candidates),
        "deployment_ridge_alpha": deployment_alpha,
        "maximum_coverage_80_error": float(maximum_coverage_80_error),
        "baseline_mae_by_name": report.baseline_mae_by_name,
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
        latest_measured_next_year_eps_revision_pct=latest_revision,
        scenario_feature_values=scenario_features,
    )


def _weighted_quantiles(
    values: Sequence[float], weights: Sequence[float]
) -> dict[str, float]:
    ordered = sorted(zip(values, weights, strict=True), key=lambda item: item[0])
    total = sum(weight for _value, weight in ordered)
    if total <= 0.0:
        raise ValueError("weighted quantiles require positive mass")
    result: dict[str, float] = {}
    for label, probability in (
        ("p05", 0.05),
        ("p20", 0.20),
        ("p50", 0.50),
        ("p80", 0.80),
        ("p95", 0.95),
    ):
        threshold = probability * total
        cumulative = 0.0
        selected = ordered[-1][0]
        for value, weight in ordered:
            cumulative += weight
            if cumulative + 1e-15 >= threshold:
                selected = value
                break
        result[label] = float(selected)
    return result


def _normalized_forward_paths(
    paths: Sequence[SimulationPath],
) -> tuple[tuple[SimulationPath, float], ...]:
    if not paths:
        raise ValueError("forward paths cannot be empty")
    weighted: list[tuple[SimulationPath, float]] = []
    for path in paths:
        weight = _finite(path.weight, field="path weight")
        if weight < 0.0:
            raise ValueError("path weight cannot be negative")
        weighted.append((path, weight))
    weighted.sort(
        key=lambda item: (
            str(item[0].path_id),
            float(item[0].q4_core_pce_pct),
            int(item[0].policy_net_steps),
        )
    )
    total = math.fsum(weight for _path, weight in weighted)
    if total <= 0.0:
        raise ValueError("forward paths require positive probability mass")
    return tuple((path, weight / total) for path, weight in weighted)


def _path_endpoint(path: SimulationPath, instrument: str) -> float | None:
    values = path.rate_paths_pct.get(instrument)
    if not values:
        return None
    return _finite(values[-1], field=f"{instrument} endpoint")


def _scenario_features(
    artifact: EquityStressArtifact,
    path: SimulationPath,
    *,
    scenario_feature_values: Mapping[str, object] | None = None,
) -> dict[str, float]:
    base = {
        **artifact.scenario_feature_values,
        **(dict(scenario_feature_values) if scenario_feature_values is not None else {}),
    }
    current_dgs10 = base.get("dgs10_pct")
    current_dgs2 = base.get("dgs2_pct")
    current_real = base.get("real_yield_10y_pct")
    current_breakeven = base.get("breakeven_10y_pct")
    endpoint_dgs10 = _path_endpoint(path, "DGS10")
    endpoint_dgs2 = _path_endpoint(path, "DGS2")
    endpoint_real = _path_endpoint(path, "DFII10")
    endpoint_breakeven = _path_endpoint(path, "T10YIE")
    return {
        "measured_next_year_eps_revision_pct": _finite(
            base.get("measured_next_year_eps_revision_pct"),
            field="measured next-year EPS revision",
        ),
        "months_to_year_end": _finite(
            base.get("months_to_year_end"), field="months to year end"
        ),
        "q4_core_pce_pct": float(path.q4_core_pce_pct),
        "policy_repricing_bp": (
            (endpoint_dgs2 - current_dgs2) * 100.0
            if endpoint_dgs2 is not None and current_dgs2 is not None
            else _finite(
                base.get("policy_repricing_bp"),
                field="DGS2 origin-to-year-end path change",
            )
        ),
        "dgs10_change_bp": (
            (endpoint_dgs10 - current_dgs10) * 100.0
            if endpoint_dgs10 is not None and current_dgs10 is not None
            else _finite(
                base.get("dgs10_change_bp"), field="DGS10 origin-to-year-end change"
            )
        ),
        "real_yield_change_bp": (
            (endpoint_real - current_real) * 100.0
            if endpoint_real is not None and current_real is not None
            else _finite(
                base.get("real_yield_change_bp"),
                field="real-yield origin-to-year-end change",
            )
        ),
        "breakeven_change_bp": (
            (endpoint_breakeven - current_breakeven) * 100.0
            if endpoint_breakeven is not None and current_breakeven is not None
            else _finite(
                base.get("breakeven_change_bp"),
                field="breakeven origin-to-year-end change",
            )
        ),
    }


def _response_for_features(
    coefficients: Mapping[str, object], features: Mapping[str, float]
) -> float:
    return float(coefficients.get("intercept", 0.0)) + sum(
        float(coefficients.get(feature, 0.0)) * float(features.get(feature, 0.0))
        for feature in EQUITY_FEATURES
    )


def _paired_residual_draws(
    residuals: Sequence[tuple[float, float]],
) -> tuple[tuple[float, float], ...]:
    """Keep a bounded, order-independent quantile sample of paired residuals."""

    ordered = sorted(
        (
            (
                _finite(eps, field="EPS residual"),
                _finite(multiple, field="multiple residual"),
            )
            for eps, multiple in residuals
        ),
        key=lambda item: (item[0], item[1]),
    )
    if len(ordered) <= MAX_RESIDUAL_DRAWS_PER_PATH:
        return tuple(ordered)
    count = MAX_RESIDUAL_DRAWS_PER_PATH
    return tuple(
        ordered[min(len(ordered) - 1, int((index + 0.5) * len(ordered) / count))]
        for index in range(count)
    )


def simulate_equity_stress(
    artifact: EquityStressArtifact,
    forward_paths: Sequence[SimulationPath],
    *,
    current_index: float,
    forward_eps: float,
    user_ai_eps_uplift_pct: float = 0.0,
    target_levels: Sequence[float] = (),
    scenario_feature_values: Mapping[str, object] | None = None,
    measured_next_year_eps_revision_pct: float | None = None,
    as_of_at: str | None = None,
) -> EquityStressResult:
    """Apply paired historical response residuals to auditable macro paths."""

    current_level = _finite(current_index, field="current index")
    base_eps = _finite(forward_eps, field="forward EPS")
    uplift = _finite(user_ai_eps_uplift_pct, field="AI EPS uplift")
    if current_level <= 0.0 or base_eps <= 0.0:
        raise ValueError("current index and forward EPS must be positive")
    if not -30.0 <= uplift <= 50.0:
        raise ValueError("AI EPS uplift must be between -30% and +50%")
    targets = tuple(_finite(value, field="target level") for value in target_levels)
    if any(value <= 0.0 for value in targets):
        raise ValueError("target level must be positive")
    measured_revision = (
        _finite(
            measured_next_year_eps_revision_pct,
            field="measured next-year EPS revision",
        )
        if measured_next_year_eps_revision_pct is not None
        else artifact.latest_measured_next_year_eps_revision_pct
    )
    result_as_of = str(as_of_at) if as_of_at is not None else artifact.trained_through
    scenario_inputs = {
        **artifact.scenario_feature_values,
        **(dict(scenario_feature_values) if scenario_feature_values is not None else {}),
    }
    stored_scenario_features = {
        key: _finite(value, field=f"scenario feature {key}")
        for key, value in scenario_inputs.items()
        if key
        in {
            "months_to_year_end",
            "dgs2_pct",
            "dgs10_pct",
            "real_yield_10y_pct",
            "breakeven_10y_pct",
            "policy_repricing_bp",
            "dgs10_change_bp",
            "real_yield_change_bp",
            "breakeven_change_bp",
        }
    }
    if artifact.publication_status not in {"READY", "LIMITED"}:
        return EquityStressResult(
            as_of_at=result_as_of,
            index_quantiles={},
            eps_quantiles={},
            multiple_quantiles={},
            threshold_probabilities={},
            target_decompositions={},
            measured_next_year_eps_revision_pct=(
                measured_revision
            ),
            user_ai_eps_uplift_pct=uplift,
            publication_status="NOT_AVAILABLE",
            reason_codes=artifact.reason_codes or ("artifact_not_publishable",),
            scenario_kind=(
                "USER_ASSUMPTION" if uplift != 0.0 or targets else "MODEL_BASE"
            ),
            current_index_level=current_level,
            base_forward_eps=base_eps,
            scenario_feature_values=stored_scenario_features,
        )
    if not artifact.joint_residuals:
        return EquityStressResult(
            as_of_at=result_as_of,
            index_quantiles={},
            eps_quantiles={},
            multiple_quantiles={},
            threshold_probabilities={},
            target_decompositions={},
            measured_next_year_eps_revision_pct=(
                measured_revision
            ),
            user_ai_eps_uplift_pct=uplift,
            publication_status="NOT_AVAILABLE",
            reason_codes=("joint_residuals_missing",),
            scenario_kind=(
                "USER_ASSUMPTION" if uplift != 0.0 or targets else "MODEL_BASE"
            ),
            current_index_level=current_level,
            base_forward_eps=base_eps,
            scenario_feature_values=stored_scenario_features,
        )

    missing_context = [
        field_name
        for field_name in (
            "months_to_year_end",
            "dgs2_pct",
            "dgs10_pct",
            "real_yield_10y_pct",
            "breakeven_10y_pct",
        )
        if scenario_inputs.get(field_name) is None
    ]
    if measured_revision is None:
        missing_context.append("measured_next_year_eps_revision_pct")
    for path in forward_paths:
        for instrument in ("DGS2", "DGS10", "DFII10", "T10YIE"):
            values = path.rate_paths_pct.get(instrument)
            if not values:
                missing_context.append(f"path.{path.path_id}.{instrument}_endpoint")
    if missing_context:
        reason = "scenario_context_incomplete:" + ",".join(
            sorted(set(missing_context))
        )
        return EquityStressResult(
            as_of_at=result_as_of,
            index_quantiles={},
            eps_quantiles={},
            multiple_quantiles={},
            threshold_probabilities={},
            target_decompositions={},
            measured_next_year_eps_revision_pct=measured_revision,
            user_ai_eps_uplift_pct=uplift,
            publication_status="NOT_AVAILABLE",
            reason_codes=(reason,),
            scenario_kind=(
                "USER_ASSUMPTION" if uplift != 0.0 or targets else "MODEL_BASE"
            ),
            current_index_level=current_level,
            base_forward_eps=base_eps,
            scenario_feature_values=stored_scenario_features,
        )

    current_multiple = current_level / base_eps
    scenario_inputs["measured_next_year_eps_revision_pct"] = float(
        measured_revision or 0.0
    )
    simulated: list[tuple[float, float, float, float]] = []
    residual_draws = _paired_residual_draws(artifact.joint_residuals)
    residual_weight = 1.0 / len(residual_draws)
    for path, weight in _normalized_forward_paths(forward_paths):
        features = _scenario_features(
            artifact, path, scenario_feature_values=scenario_inputs
        )
        eps_change = _response_for_features(artifact.eps_response, features)
        multiple_change = _response_for_features(artifact.multiple_response, features)
        for residual_eps, residual_multiple in residual_draws:
            eps_level = (
                base_eps
                * (1.0 + (eps_change + residual_eps) / 100.0)
                * (1.0 + uplift / 100.0)
            )
            multiple_level = current_multiple * (
                1.0 + (multiple_change + residual_multiple) / 100.0
            )
            if eps_level <= 0.0 or multiple_level <= 0.0:
                raise ValueError("simulated EPS and multiple must remain positive")
            simulated.append(
                (
                    eps_level * multiple_level,
                    eps_level,
                    multiple_level,
                    weight * residual_weight,
                )
            )
    levels = [row[0] for row in simulated]
    eps_levels = [row[1] for row in simulated]
    multiples = [row[2] for row in simulated]
    weights = [row[3] for row in simulated]
    threshold_probabilities: dict[str, float] = {}
    decompositions: dict[str, dict[str, object]] = {}
    if artifact.publication_status == "READY":
        for target in targets:
            key = f"below_or_equal:{target:.4f}"
            selected = [row for row in simulated if row[0] <= target]
            probability = sum(row[3] for row in selected)
            threshold_probabilities[key] = probability
            decompositions[key] = {
                "target_level": target,
                "probability": probability,
                "eps_quantiles": (
                    _weighted_quantiles(
                        [row[1] for row in selected], [row[3] for row in selected]
                    )
                    if selected
                    else {}
                ),
                "multiple_quantiles": (
                    _weighted_quantiles(
                        [row[2] for row in selected], [row[3] for row in selected]
                    )
                    if selected
                    else {}
                ),
            }
    return EquityStressResult(
        as_of_at=result_as_of,
        index_quantiles=_weighted_quantiles(levels, weights),
        eps_quantiles=_weighted_quantiles(eps_levels, weights),
        multiple_quantiles=_weighted_quantiles(multiples, weights),
        threshold_probabilities=threshold_probabilities,
        target_decompositions=decompositions,
        measured_next_year_eps_revision_pct=(
            measured_revision
        ),
        user_ai_eps_uplift_pct=uplift,
        publication_status=artifact.publication_status,
        reason_codes=artifact.reason_codes,
        scenario_kind=(
            "USER_ASSUMPTION" if uplift != 0.0 or targets else "MODEL_BASE"
        ),
        current_index_level=current_level,
        base_forward_eps=base_eps,
        scenario_feature_values=stored_scenario_features,
    )
