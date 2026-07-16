"""Leakage-safe monthly features for the U.S. economic-cycle model."""

from __future__ import annotations

import math
from datetime import date, datetime
from typing import Iterable, Sequence

import pandas as pd

from finance.economic_cycle_catalog import IndicatorSpec, get_economic_cycle_catalog


FACTOR_NAMES = (
    "activity",
    "labor_income",
    "financial_leading",
    "inflation_policy",
)


def aggregate_observations_monthly(
    observations: pd.DataFrame,
    *,
    aggregation: str,
) -> pd.Series:
    """Aggregate eligible source observations without filling missing months."""

    if observations.empty:
        return pd.Series(dtype="float64")
    frame = observations.loc[:, ["observation_date", "value"]].copy()
    frame["observation_date"] = pd.to_datetime(
        frame["observation_date"], errors="coerce"
    )
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    frame = frame.dropna(subset=["observation_date", "value"]).sort_values(
        "observation_date"
    )
    if frame.empty:
        return pd.Series(dtype="float64")
    frame["month"] = frame["observation_date"].dt.to_period("M")
    if aggregation == "monthly_mean":
        result = frame.groupby("month", sort=True)["value"].mean()
    elif aggregation == "month_end":
        result = frame.groupby("month", sort=True)["value"].last()
    else:
        raise ValueError(f"Unsupported monthly aggregation: {aggregation}")
    return result.astype(float)


def _period_value(series: pd.Series, period: pd.Period) -> float | None:
    if period not in series.index:
        return None
    value = series.loc[period]
    if isinstance(value, pd.Series):
        value = value.iloc[-1]
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def _annualized_log_change(current: float, previous: float, months: int) -> float | None:
    if current <= 0 or previous <= 0:
        return None
    return math.expm1(math.log(current / previous) * (12.0 / months)) * 100.0


def transform_monthly_signal(spec: IndicatorSpec, monthly: pd.Series) -> float | None:
    """Apply the catalog transform at the latest available monthly period."""

    if monthly.empty:
        return None
    series = monthly.copy()
    if not isinstance(series.index, pd.PeriodIndex):
        series.index = pd.PeriodIndex(series.index, freq="M")
    series = pd.to_numeric(series, errors="coerce").sort_index()
    current_period = series.index.max()
    current = _period_value(series, current_period)
    if current is None:
        return None

    transform = spec.transform
    signal: float | None
    if transform == "level":
        signal = current
    elif transform == "level_minus_2":
        signal = current - 2.0
    elif transform == "mean_level_3m":
        values = [
            _period_value(series, current_period - offset) for offset in (2, 1, 0)
        ]
        signal = (
            sum(value for value in values if value is not None) / 3.0
            if all(value is not None for value in values)
            else None
        )
    elif transform in {"level_change_3m", "log_change_3m", "cli_gap_and_change_3m"}:
        previous = _period_value(series, current_period - 3)
        if previous is None:
            signal = None
        elif transform == "level_change_3m":
            signal = current - previous
        elif transform == "log_change_3m":
            signal = (
                math.log(current / previous) * 100.0
                if current > 0 and previous > 0
                else None
            )
        else:
            signal = (current - 100.0) + (current - previous)
    elif transform in {
        "annualized_log_change_3m",
        "annualized_log_change_3m_minus_2",
    }:
        previous = _period_value(series, current_period - 3)
        signal = (
            _annualized_log_change(current, previous, 3)
            if previous is not None
            else None
        )
        if signal is not None and transform.endswith("_minus_2"):
            signal -= 2.0
    elif transform == "annualized_log_change_6m":
        previous = _period_value(series, current_period - 6)
        signal = (
            _annualized_log_change(current, previous, 6)
            if previous is not None
            else None
        )
    else:
        raise ValueError(f"Unsupported economic-cycle transform: {transform}")
    return signal * spec.direction if signal is not None else None


def fit_expanding_robust_scale(
    values: Sequence[object],
    *,
    minimum_history: int = 60,
) -> list[float | None]:
    """Scale each observation using only the expanding history available then."""

    if int(minimum_history) < 2:
        minimum_history = 2
    history: list[float] = []
    scaled: list[float | None] = []
    for value in values:
        try:
            current = float(value)
        except (TypeError, ValueError):
            current = math.nan
        if not math.isfinite(current):
            scaled.append(None)
            continue
        history.append(current)
        if len(history) < int(minimum_history):
            scaled.append(None)
            continue
        history_series = pd.Series(history, dtype="float64")
        median = float(history_series.median())
        mad = float((history_series - median).abs().median())
        if not math.isfinite(mad) or mad <= 1e-12:
            scaled.append(None)
            continue
        z_score = (current - median) / (1.4826 * mad)
        scaled.append(max(-4.0, min(4.0, z_score)))
    return scaled


def _as_date(value: object) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def is_series_stale(
    spec: IndicatorSpec,
    latest_observation_date: date | str,
    forecast_origin: date | str,
) -> bool:
    """Apply the approved source-frequency freshness thresholds."""

    latest = _as_date(latest_observation_date)
    origin = _as_date(forecast_origin)
    if spec.series_id == "CFNAI":
        threshold = 100
    elif spec.frequency in {"daily", "weekly"}:
        threshold = 45
    else:
        threshold = 75
    return (origin - latest).days > threshold


def calculate_factor_scores(panel: pd.DataFrame) -> pd.DataFrame:
    """Build equal-weight factor scores with explicit coverage/freshness status."""

    output = panel.copy()
    catalog = [
        item for item in get_economic_cycle_catalog() if item.role != "label_anchor"
    ]
    modeled_count = len(catalog)
    for factor in FACTOR_NAMES:
        factor_specs = [item for item in catalog if item.factor == factor]
        z_columns = [f"{item.series_id}_z" for item in factor_specs]
        stale_columns = [f"{item.series_id}_stale" for item in factor_specs]
        for column in z_columns:
            if column not in output:
                output[column] = None
        for column in stale_columns:
            if column not in output:
                output[column] = False
        numeric = output[z_columns].apply(pd.to_numeric, errors="coerce")
        available = numeric.notna().sum(axis=1)
        output[f"{factor}_available_count"] = available
        output[f"{factor}_score"] = numeric.mean(axis=1).where(available >= 2)
        output[f"{factor}_stale"] = output[stale_columns].fillna(False).astype(bool).any(axis=1)

    all_z_columns = [f"{item.series_id}_z" for item in catalog]
    available_count = (
        output[all_z_columns].apply(pd.to_numeric, errors="coerce").notna().sum(axis=1)
    )
    output["overall_coverage"] = available_count / float(modeled_count)
    required_factor_ready = pd.Series(True, index=output.index)
    stale = pd.Series(False, index=output.index)
    for factor in FACTOR_NAMES:
        required_factor_ready &= output[f"{factor}_score"].notna()
        stale |= output[f"{factor}_stale"].astype(bool)
    output["data_quality_status"] = (
        (output["overall_coverage"] >= 0.75) & required_factor_ready & ~stale
    ).map({True: "READY", False: "LIMITED"})
    return output


def _eligible_rows_for_origin(
    rows: pd.DataFrame,
    *,
    series_id: str,
    origin: pd.Timestamp,
) -> pd.DataFrame:
    subset = rows.loc[rows["series_id"] == series_id].copy()
    if subset.empty:
        return subset
    subset["observation_date"] = pd.to_datetime(
        subset["observation_date"], errors="coerce"
    )
    subset = subset.loc[subset["observation_date"] <= origin]
    if "realtime_start" in subset:
        subset["realtime_start"] = pd.to_datetime(
            subset["realtime_start"], errors="coerce"
        )
        subset = subset.loc[subset["realtime_start"] <= origin]
    if "realtime_end" in subset:
        end_text = subset["realtime_end"].astype(str)
        open_ended = end_text.str.startswith("9999-")
        parsed_end = pd.to_datetime(
            subset["realtime_end"].where(~open_ended), errors="coerce"
        )
        subset = subset.loc[open_ended | (parsed_end >= origin)]
    sort_columns = ["observation_date"]
    if "realtime_start" in subset:
        sort_columns.append("realtime_start")
    subset = subset.sort_values(sort_columns).drop_duplicates(
        subset=["observation_date"], keep="last"
    )
    return subset


def build_monthly_feature_panel(
    vintage_rows: Iterable[dict[str, object]],
    catalog: Iterable[IndicatorSpec] | None,
    *,
    forecast_origins: Iterable[date | str | pd.Timestamp],
) -> pd.DataFrame:
    """Construct origin-by-origin transforms, scales, factor scores, and freshness."""

    specs = tuple(catalog or get_economic_cycle_catalog())
    source = pd.DataFrame(list(vintage_rows))
    if source.empty:
        source = pd.DataFrame(columns=["series_id", "observation_date", "value"])
    if "series_id" not in source:
        source["series_id"] = ""
    source["series_id"] = source["series_id"].astype(str).str.upper()

    records: list[dict[str, object]] = []
    for origin_value in forecast_origins:
        origin = pd.Timestamp(origin_value)
        if origin.tzinfo is not None:
            origin = origin.tz_convert(None)
        origin = origin.normalize()
        record: dict[str, object] = {"forecast_origin": origin}
        for spec in specs:
            eligible = _eligible_rows_for_origin(
                source, series_id=spec.series_id, origin=origin
            )
            monthly = aggregate_observations_monthly(
                eligible, aggregation=spec.aggregation
            )
            record[f"{spec.series_id}_signal"] = transform_monthly_signal(
                spec, monthly
            )
            if eligible.empty:
                record[f"{spec.series_id}_latest_observation_date"] = None
                record[f"{spec.series_id}_stale"] = True
            else:
                latest = pd.Timestamp(eligible["observation_date"].max()).date()
                record[f"{spec.series_id}_latest_observation_date"] = latest.isoformat()
                record[f"{spec.series_id}_stale"] = is_series_stale(
                    spec, latest, origin.date()
                )
        records.append(record)

    panel = pd.DataFrame(records)
    for spec in specs:
        if spec.role == "label_anchor":
            continue
        signal_column = f"{spec.series_id}_signal"
        panel[f"{spec.series_id}_z"] = fit_expanding_robust_scale(
            panel[signal_column].tolist(),
            minimum_history=spec.minimum_history_months,
        )
    return calculate_factor_scores(panel)
