"""Point-in-time transition drivers and model-variant coverage audit."""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from finance.economic_cycle_observed_state import PHASE_SEQUENCE
from finance.economic_cycle_transition_dataset import TransitionDataset


REQUIRED_DRIVER_SERIES = (
    "FEDFUNDS",
    "DGS2",
    "DFII10",
    "PCEPILFE",
    "T10YIE",
    "DGS10",
    "PERMIT",
)

REQUIRED_OBSERVATION_DRIVER_SERIES = ("BAA10Y",)

REQUIRED_DRIVER_FEATURES = (
    "FEDFUNDS_delta_3m",
    "PCEPILFE_gap_2pct",
    "yield_curve_delta_3m",
    "BAA10Y_delta_3m",
    "PERMIT_change_6m_pct",
)

DRIVER_PANEL_FEATURES = tuple(
    dict.fromkeys(
        (
            *(
                feature
                for series_id in (
                    *REQUIRED_DRIVER_SERIES,
                    *REQUIRED_OBSERVATION_DRIVER_SERIES,
                )
                for feature in (
                    f"{series_id}_level",
                    f"{series_id}_delta_1m",
                    f"{series_id}_delta_3m",
                    f"{series_id}_delta_6m",
                )
            ),
            "PCEPILFE_3m_ann",
            "PCEPILFE_gap_2pct",
            "PERMIT_change_6m_pct",
            "yield_curve_10y2y",
            "yield_curve_delta_3m",
        )
    )
)

MARKET_DRIVER_FEATURES = (
    "SP500_return_1m_pct",
    "SP500_return_3m_pct",
    "SP500_return_6m_pct",
    "SP500_drawdown_6m_pct",
    "VIXCLS_level",
    "VIXCLS_delta_3m",
    "GOLD_return_1m_pct",
    "GOLD_return_3m_pct",
    "GOLD_return_6m_pct",
    "DOLLAR_return_1m_pct",
    "DOLLAR_return_3m_pct",
    "DOLLAR_return_6m_pct",
)


@dataclass(frozen=True)
class DriverCoverageGate:
    minimum_usable_origins: int = 180
    minimum_independent_transitions: int = 48
    minimum_destination_events: int = 8
    minimum_holdout_destination_events: int = 2


DEFAULT_DRIVER_COVERAGE_GATE = DriverCoverageGate()


@dataclass(frozen=True)
class DriverCoverageReport:
    status: str
    reason_codes: tuple[str, ...]
    usable_origins: int
    independent_transitions: int
    total_confirmed_transitions: int
    destination_counts: dict[str, int]
    holdout_destination_counts: dict[str, int]
    series_coverage: dict[str, dict[str, object]]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _month_end(value: object) -> pd.Timestamp | None:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    timestamp = pd.Timestamp(parsed)
    if timestamp.tzinfo is not None:
        timestamp = timestamp.tz_convert(None)
    return timestamp.to_period("M").to_timestamp("M").normalize()


def _origin_cutoff(value: pd.Timestamp) -> pd.Timestamp:
    return value.tz_localize("UTC") + pd.Timedelta(days=1) - pd.Timedelta(
        microseconds=1
    )


def _fallback_known_at(value: object) -> pd.Timestamp | None:
    """Treat an ALFRED realtime date as known only after that U.S. day ends."""

    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    timestamp = pd.Timestamp(parsed)
    if timestamp.tzinfo is not None:
        timestamp = timestamp.tz_convert(None)
    return timestamp.normalize().tz_localize("UTC") + pd.Timedelta(
        days=1
    ) - pd.Timedelta(microseconds=1)


def _normalized_vintages(
    rows: Sequence[Mapping[str, object]],
) -> pd.DataFrame:
    frame = pd.DataFrame([dict(row) for row in rows])
    required = {"series_id", "observation_date", "value"}
    if frame.empty or not required.issubset(frame):
        return pd.DataFrame(columns=sorted((*required, "released_at")))
    frame["series_id"] = frame["series_id"].astype(str).str.upper().str.strip()
    frame["observation_date"] = pd.to_datetime(
        frame["observation_date"], errors="coerce"
    ).dt.normalize()
    released = pd.to_datetime(
        frame.get("released_at", pd.Series(index=frame.index, dtype=object)),
        errors="coerce",
        utc=True,
    )
    fallback = frame.get(
        "realtime_start", pd.Series(index=frame.index, dtype=object)
    ).map(_fallback_known_at)
    frame["released_at"] = released.where(released.notna(), fallback)
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    return (
        frame.replace([np.inf, -np.inf], np.nan)
        .dropna(subset=("series_id", "observation_date", "released_at", "value"))
        .loc[lambda value: value["series_id"].isin(REQUIRED_DRIVER_SERIES)]
        .sort_values(["series_id", "observation_date", "released_at"])
        .reset_index(drop=True)
    )


def _normalized_market_rows(
    rows: Sequence[Mapping[str, object]],
) -> pd.DataFrame:
    normalized: list[dict[str, object]] = []
    for raw in rows:
        symbol = str(raw.get("provider_symbol") or raw.get("series_id") or "").upper()
        observed = (
            raw.get("candle_time_utc")
            or raw.get("observation_date")
            or raw.get("date")
        )
        value = raw.get("close") if raw.get("close") is not None else raw.get("value")
        timestamp = pd.to_datetime(observed, errors="coerce")
        numeric = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
        if not symbol or pd.isna(timestamp) or pd.isna(numeric):
            continue
        if pd.Timestamp(timestamp).tzinfo is not None:
            timestamp = pd.Timestamp(timestamp).tz_convert(None)
        normalized.append(
            {
                "symbol": symbol,
                "observation_date": pd.Timestamp(timestamp).normalize(),
                "value": float(numeric),
            }
        )
    return pd.DataFrame(
        normalized,
        columns=("symbol", "observation_date", "value"),
    ).sort_values(["symbol", "observation_date"], ignore_index=True)


def _monthly_series(
    eligible: pd.DataFrame,
    series_id: str,
) -> pd.Series:
    selected = eligible.loc[eligible["series_id"] == series_id]
    if selected.empty:
        return pd.Series(dtype=float)
    latest = selected.drop_duplicates("observation_date", keep="last")
    monthly = (
        latest.set_index("observation_date")["value"]
        .sort_index()
        .resample("ME")
        .last()
    )
    return monthly.dropna()


def _market_series(
    eligible: pd.DataFrame,
    symbol: str,
) -> pd.Series:
    selected = eligible.loc[eligible["symbol"] == symbol]
    if selected.empty:
        return pd.Series(dtype=float)
    return (
        selected.drop_duplicates("observation_date", keep="last")
        .set_index("observation_date")["value"]
        .sort_index()
        .resample("ME")
        .last()
        .dropna()
    )


def _value_at_lag(series: pd.Series, lag: int) -> float | None:
    if series.empty:
        return None
    current_month = pd.Timestamp(series.index[-1]).to_period("M")
    target = (current_month - int(lag)).to_timestamp("M")
    if target not in series.index:
        return None
    value = float(series.loc[target])
    return value if math.isfinite(value) else None


def _level(series: pd.Series) -> float | None:
    if series.empty:
        return None
    value = float(series.iloc[-1])
    return value if math.isfinite(value) else None


def _delta(series: pd.Series, lag: int) -> float | None:
    current = _level(series)
    prior = _value_at_lag(series, lag)
    if current is None or prior is None:
        return None
    return current - prior


def _percent_change(series: pd.Series, lag: int) -> float | None:
    current = _level(series)
    prior = _value_at_lag(series, lag)
    if current is None or prior is None or abs(prior) <= 1e-12:
        return None
    return round((current / prior - 1.0) * 100.0, 12)


def _driver_features(series: Mapping[str, pd.Series]) -> dict[str, float | None]:
    output: dict[str, float | None] = {}
    for series_id in REQUIRED_DRIVER_SERIES:
        values = series.get(series_id, pd.Series(dtype=float))
        output[f"{series_id}_level"] = _level(values)
        for lag in (1, 3, 6):
            output[f"{series_id}_delta_{lag}m"] = _delta(values, lag)

    pce = series.get("PCEPILFE", pd.Series(dtype=float))
    pce_current = _level(pce)
    pce_prior = _value_at_lag(pce, 3)
    output["PCEPILFE_3m_ann"] = (
        ((pce_current / pce_prior) ** 4.0 - 1.0) * 100.0
        if pce_current is not None
        and pce_prior is not None
        and pce_current > 0.0
        and pce_prior > 0.0
        else None
    )
    output["PCEPILFE_gap_2pct"] = (
        output["PCEPILFE_3m_ann"] - 2.0
        if output["PCEPILFE_3m_ann"] is not None
        else None
    )
    output["PERMIT_change_6m_pct"] = _percent_change(
        series.get("PERMIT", pd.Series(dtype=float)),
        6,
    )
    dgs10 = output.get("DGS10_level")
    dgs2 = output.get("DGS2_level")
    curve = (
        float(dgs10) - float(dgs2)
        if dgs10 is not None and dgs2 is not None
        else None
    )
    dgs10_delta = output.get("DGS10_delta_3m")
    dgs2_delta = output.get("DGS2_delta_3m")
    output["yield_curve_10y2y"] = curve
    output["yield_curve_delta_3m"] = (
        float(dgs10_delta) - float(dgs2_delta)
        if dgs10_delta is not None and dgs2_delta is not None
        else None
    )
    return output


def _market_features(series: Mapping[str, pd.Series]) -> dict[str, float | None]:
    sp500 = series.get("^GSPC", pd.Series(dtype=float))
    if sp500.empty:
        sp500 = series.get("SPY", pd.Series(dtype=float))
    gold = series.get("GC=F", pd.Series(dtype=float))
    dollar = series.get("DX-Y.NYB", pd.Series(dtype=float))
    vix = series.get("VIXCLS", pd.Series(dtype=float))
    baa10y = series.get("BAA10Y", pd.Series(dtype=float))
    output = {
        **{
            f"SP500_return_{lag}m_pct": _percent_change(sp500, lag)
            for lag in (1, 3, 6)
        },
        "SP500_drawdown_6m_pct": None,
        "VIXCLS_level": _level(vix),
        "VIXCLS_delta_3m": _delta(vix, 3),
        "BAA10Y_level": _level(baa10y),
        "BAA10Y_delta_1m": _delta(baa10y, 1),
        "BAA10Y_delta_3m": _delta(baa10y, 3),
        "BAA10Y_delta_6m": _delta(baa10y, 6),
        **{
            f"GOLD_return_{lag}m_pct": _percent_change(gold, lag)
            for lag in (1, 3, 6)
        },
        **{
            f"DOLLAR_return_{lag}m_pct": _percent_change(dollar, lag)
            for lag in (1, 3, 6)
        },
    }
    if not sp500.empty:
        window = sp500.iloc[-7:]
        peak = float(window.max())
        current = float(window.iloc[-1])
        if peak > 0.0:
            output["SP500_drawdown_6m_pct"] = round(
                (current / peak - 1.0) * 100.0,
                12,
            )
    return output


def build_transition_driver_panel(
    vintage_rows: Sequence[Mapping[str, object]],
    forecast_origins: Sequence[object],
    *,
    market_rows: Sequence[Mapping[str, object]] = (),
) -> pd.DataFrame:
    """Build origin-by-origin macro and market features without future releases."""

    origins = sorted(
        {
            month
            for value in forecast_origins
            if (month := _month_end(value)) is not None
        }
    )
    vintages = _normalized_vintages(vintage_rows)
    markets = _normalized_market_rows(market_rows)
    output: list[dict[str, object]] = []
    for origin in origins:
        cutoff = _origin_cutoff(origin)
        eligible_vintages = vintages.loc[
            (vintages["released_at"] <= cutoff)
            & (vintages["observation_date"] <= origin)
        ]
        macro_series = {
            series_id: _monthly_series(eligible_vintages, series_id)
            for series_id in REQUIRED_DRIVER_SERIES
        }
        eligible_markets = markets.loc[markets["observation_date"] <= origin]
        market_series = {
            symbol: _market_series(eligible_markets, symbol)
            for symbol in (
                "^GSPC",
                "SPY",
                "VIXCLS",
                "GC=F",
                "DX-Y.NYB",
                *REQUIRED_OBSERVATION_DRIVER_SERIES,
            )
        }
        output.append(
            {
                "forecast_origin": origin,
                **_driver_features(macro_series),
                **_market_features(market_series),
            }
        )
    columns = (
        "forecast_origin",
        *DRIVER_PANEL_FEATURES,
        *MARKET_DRIVER_FEATURES,
    )
    frame = pd.DataFrame(output)
    for column in columns:
        if column not in frame:
            frame[column] = np.nan
    return frame.loc[:, columns]


def _finite(value: object) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def extend_transition_dataset(
    base: TransitionDataset,
    feature_panel: pd.DataFrame,
    feature_names: Sequence[str],
) -> TransitionDataset:
    """Attach one driver variant and preserve every audit origin."""

    selected = tuple(dict.fromkeys(str(item) for item in feature_names))
    if not selected:
        raise ValueError("feature_names cannot be empty")
    features = feature_panel.copy()
    if "forecast_origin" not in features:
        raise ValueError("feature_panel requires forecast_origin")
    features["forecast_origin"] = features["forecast_origin"].map(_month_end)
    for feature in selected:
        if feature not in features:
            features[feature] = np.nan
        features[feature] = pd.to_numeric(features[feature], errors="coerce")
    features = features.drop_duplicates("forecast_origin", keep="last")

    rows = base.rows.copy()
    rows["forecast_origin"] = rows["forecast_origin"].map(_month_end)
    rows = rows.drop(columns=list(selected), errors="ignore").merge(
        features[["forecast_origin", *selected]],
        on="forecast_origin",
        how="left",
        sort=False,
    )
    eligibility: list[bool] = []
    reasons: list[str] = []
    for row in rows.to_dict(orient="records"):
        if not bool(row.get("eligible")):
            eligibility.append(False)
            reasons.append(str(row.get("ineligible_reason") or "MISSING_MODEL_FEATURE"))
        elif not all(_finite(row.get(feature)) for feature in selected):
            eligibility.append(False)
            reasons.append("MISSING_DRIVER_FEATURE")
        else:
            eligibility.append(True)
            reasons.append("")
    rows["eligible"] = eligibility
    rows["ineligible_reason"] = reasons
    rows["episode_weight"] = 0.0
    eligible = rows.loc[rows["eligible"] & rows["episode_id"].notna()]
    for episode_id, size in eligible.groupby("episode_id").size().items():
        rows.loc[
            rows["eligible"] & (rows["episode_id"] == episode_id),
            "episode_weight",
        ] = 1.0 / float(size)
    return TransitionDataset(
        feature_names=tuple((*base.feature_names, *selected)),
        rows=rows,
    )


def _coverage_by_feature(
    rows: pd.DataFrame,
    features: Sequence[str],
) -> dict[str, dict[str, object]]:
    coverage: dict[str, dict[str, object]] = {}
    total = len(rows)
    for feature in features:
        values = pd.to_numeric(rows.get(feature), errors="coerce")
        finite = values.map(_finite) if values is not None else pd.Series(dtype=bool)
        origins = rows.loc[finite, "forecast_origin"] if len(finite) else pd.Series(dtype=object)
        coverage[feature] = {
            "usable_origins": int(finite.sum()) if len(finite) else 0,
            "missing_share": (
                float(1.0 - finite.sum() / total) if total else 1.0
            ),
            "first_usable_at": (
                str(pd.Timestamp(origins.min()).date()) if not origins.empty else None
            ),
            "last_usable_at": (
                str(pd.Timestamp(origins.max()).date()) if not origins.empty else None
            ),
        }
    return coverage


def audit_transition_driver_coverage(
    dataset: TransitionDataset,
    state_frame: pd.DataFrame,
    required_features: Sequence[str],
    *,
    gate: DriverCoverageGate = DEFAULT_DRIVER_COVERAGE_GATE,
) -> DriverCoverageReport:
    """Count eligible origins and independent next-destination episodes."""

    rows = dataset.rows.copy()
    eligible = rows.loc[rows["eligible"].astype(bool)]
    destination_by_episode: dict[int, str] = {}
    for row in eligible.sort_values("forecast_origin").to_dict(orient="records"):
        destination = str(row.get("destination_target") or "")
        episode = row.get("episode_id")
        if destination in PHASE_SEQUENCE and episode is not None and not pd.isna(episode):
            destination_by_episode.setdefault(int(episode), destination)
    ordered = sorted(destination_by_episode)
    holdout_size = int(math.ceil(len(ordered) * 0.25)) if ordered else 0
    holdout = ordered[-holdout_size:] if holdout_size else []
    destination_counts_raw = Counter(destination_by_episode.values())
    holdout_counts_raw = Counter(destination_by_episode[item] for item in holdout)
    destination_counts = {
        phase: int(destination_counts_raw.get(phase, 0)) for phase in PHASE_SEQUENCE
    }
    holdout_counts = {
        phase: int(holdout_counts_raw.get(phase, 0)) for phase in PHASE_SEQUENCE
    }

    reasons: list[str] = []
    if len(eligible) < gate.minimum_usable_origins:
        reasons.append("INSUFFICIENT_DRIVER_ORIGINS")
    if len(destination_by_episode) < gate.minimum_independent_transitions:
        reasons.append("INSUFFICIENT_DRIVER_TRANSITIONS")
    for phase in PHASE_SEQUENCE:
        if destination_counts[phase] < gate.minimum_destination_events:
            reasons.append(f"INSUFFICIENT_DRIVER_DESTINATION_{phase.upper()}")
        if holdout_counts[phase] < gate.minimum_holdout_destination_events:
            reasons.append(f"INSUFFICIENT_DRIVER_HOLDOUT_{phase.upper()}")

    total_confirmed = 0
    if "confirmed_transition_to" in state_frame:
        total_confirmed = int(
            state_frame["confirmed_transition_to"].isin(PHASE_SEQUENCE).sum()
        )
    return DriverCoverageReport(
        status="DRIVER_READY" if not reasons else "SHADOW_ONLY",
        reason_codes=tuple(reasons),
        usable_origins=len(eligible),
        independent_transitions=len(destination_by_episode),
        total_confirmed_transitions=total_confirmed,
        destination_counts=destination_counts,
        holdout_destination_counts=holdout_counts,
        series_coverage=_coverage_by_feature(rows, required_features),
    )
