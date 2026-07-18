from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from app.services.futures_macro_thermometer import SCORE_DEFINITIONS, ScoreDefinition


PATTERN_WINDOWS: tuple[int, ...] = (1, 5, 20)
PATTERN_FAMILY_KEYS: tuple[str, ...] = (
    "risk_on",
    "growth",
    "rate_pressure",
    "dollar_pressure",
    "safe_haven",
    "inflation_pressure",
)
PATTERN_FEATURE_SUFFIXES: tuple[str, ...] = (
    "1d_z",
    "5d_z",
    "20d_z",
    "5d_slope",
    "20d_slope",
    "acceleration",
    "5d_persistence",
    "20d_persistence",
    "breadth",
    "volatility_ratio",
)
PATTERN_FEATURE_COLUMNS: tuple[str, ...] = tuple(
    f"{family}__{suffix}"
    for family in PATTERN_FAMILY_KEYS
    for suffix in PATTERN_FEATURE_SUFFIXES
)
SCORE_TO_FAMILY_KEY = {
    "Risk-On Score": "risk_on",
    "Growth Score": "growth",
    "Rate Pressure Score": "rate_pressure",
    "Dollar Pressure Score": "dollar_pressure",
    "Safe Haven Score": "safe_haven",
    "Inflation Pressure Score": "inflation_pressure",
}


def _pattern_close_matrix(
    candles: pd.DataFrame,
    selected_symbols: Sequence[str],
) -> pd.DataFrame:
    """Return one close per symbol/date without filling missing observations."""

    if candles.empty or not {"provider_symbol", "Date", "Close"}.issubset(candles.columns):
        return pd.DataFrame()
    selected = [str(symbol).strip().upper() for symbol in selected_symbols if str(symbol).strip()]
    normalized = candles.loc[:, [column for column in ("provider_symbol", "ts", "Date", "Close") if column in candles.columns]].copy()
    normalized["provider_symbol"] = normalized["provider_symbol"].astype(str).str.strip().str.upper()
    normalized = normalized[normalized["provider_symbol"].isin(selected)]
    normalized["Date"] = pd.to_datetime(normalized["Date"], errors="coerce").dt.normalize()
    normalized["Close"] = pd.to_numeric(normalized["Close"], errors="coerce")
    normalized = normalized.dropna(subset=["provider_symbol", "Date", "Close"])
    if normalized.empty:
        return pd.DataFrame()
    sort_columns = ["provider_symbol", "Date"]
    if "ts" in normalized.columns:
        normalized["ts"] = pd.to_datetime(normalized["ts"], errors="coerce")
        sort_columns.append("ts")
    normalized = normalized.sort_values(sort_columns).drop_duplicates(
        subset=["provider_symbol", "Date"],
        keep="last",
    )
    matrix = normalized.pivot(index="Date", columns="provider_symbol", values="Close").sort_index()
    matrix = matrix.reindex(columns=selected)
    matrix.index.name = "Date"
    return matrix


def _daily_symbol_z(close_matrix: pd.DataFrame) -> pd.DataFrame:
    """Scale each daily return by volatility observable on that same date."""

    returns = close_matrix.pct_change(fill_method=None)
    trailing_vol = returns.rolling(60, min_periods=60).std(ddof=0)
    return returns.divide(trailing_vol.where(trailing_vol.abs() > 1e-12))


def _family_daily_z(symbol_z: pd.DataFrame, definition: ScoreDefinition) -> pd.DataFrame:
    members = [symbol for symbol in definition.members if symbol in symbol_z.columns]
    if not members:
        return pd.DataFrame(index=symbol_z.index, columns=["value", "breadth", "coverage"], dtype=float)
    weighted = pd.concat(
        [
            symbol_z[symbol].mul(float(definition.members[symbol])).rename(symbol)
            for symbol in members
        ],
        axis=1,
    )
    coverage = weighted.notna().sum(axis=1)
    return pd.DataFrame(
        {
            "value": weighted.mean(axis=1, skipna=True),
            "breadth": weighted.gt(0).sum(axis=1).divide(coverage.replace(0, pd.NA)),
            "coverage": coverage,
        },
        index=symbol_z.index,
    )


def _dominant_sign_ratio(window: pd.Series) -> float:
    values = pd.to_numeric(window, errors="coerce").dropna()
    positive_count = int((values > 0).sum())
    negative_count = int((values < 0).sum())
    non_zero_count = positive_count + negative_count
    if non_zero_count <= 0:
        return 0.0
    return float(max(positive_count, negative_count) / non_zero_count)


def build_pattern_feature_frame(
    candles: pd.DataFrame,
    *,
    selected_symbols: Sequence[str],
) -> pd.DataFrame:
    """Build point-in-time 1D/5D/20D family features from stored daily closes."""

    close_matrix = _pattern_close_matrix(candles, selected_symbols)
    if close_matrix.empty:
        return pd.DataFrame(columns=[*PATTERN_FEATURE_COLUMNS, "available_symbol_count"]).rename_axis("Date")
    symbol_z = _daily_symbol_z(close_matrix)
    output = pd.DataFrame(index=symbol_z.index)
    for definition in SCORE_DEFINITIONS:
        family = SCORE_TO_FAMILY_KEY[definition.name]
        daily = _family_daily_z(symbol_z, definition)
        output[f"{family}__1d_z"] = daily["value"]
        output[f"{family}__5d_z"] = daily["value"].rolling(5, min_periods=5).sum().divide(5**0.5)
        output[f"{family}__20d_z"] = daily["value"].rolling(20, min_periods=20).sum().divide(20**0.5)
        output[f"{family}__5d_slope"] = daily["value"].sub(daily["value"].shift(4))
        output[f"{family}__20d_slope"] = daily["value"].sub(daily["value"].shift(19))
        output[f"{family}__acceleration"] = daily["value"].rolling(5, min_periods=5).mean().sub(
            daily["value"].shift(5).rolling(5, min_periods=5).mean()
        )
        sign = daily["value"].map(lambda value: 1.0 if value > 0 else (-1.0 if value < 0 else 0.0))
        output[f"{family}__5d_persistence"] = sign.rolling(5, min_periods=5).apply(
            _dominant_sign_ratio,
            raw=False,
        )
        output[f"{family}__20d_persistence"] = sign.rolling(20, min_periods=20).apply(
            _dominant_sign_ratio,
            raw=False,
        )
        output[f"{family}__breadth"] = daily["breadth"]
        output[f"{family}__volatility_ratio"] = daily["value"].rolling(20, min_periods=20).std(ddof=0).divide(
            daily["value"].rolling(60, min_periods=60).std(ddof=0).replace(0, pd.NA)
        )
    output["available_symbol_count"] = close_matrix.notna().sum(axis=1)
    output.index.name = "Date"
    required = [f"{family}__20d_z" for family in PATTERN_FAMILY_KEYS]
    return output.loc[:, [*PATTERN_FEATURE_COLUMNS, "available_symbol_count"]].dropna(
        subset=required,
        how="all",
    )
