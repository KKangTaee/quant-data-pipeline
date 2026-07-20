from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pandas as pd

from app.services.futures_macro_thermometer import (
    SCORE_DEFINITIONS,
    SIGNAL_Z_THRESHOLD,
    ScoreDefinition,
)


PATTERN_WINDOWS: tuple[int, ...] = (1, 5, 20)
PATTERN_STATE_SCHEMA_VERSION = "futures_macro_state_v2"
OBSERVED_TRAIL_SESSIONS = 30
PATTERN_RIBBON_SESSIONS = 60
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
REGIME_LABELS = {
    "risk_seeking": "위험선호 체제",
    "defensive": "방어적 위험 체제",
    "inflation_rate_pressure": "물가·금리 부담 체제",
    "mixed": "혼재 체제",
}
TRANSITION_LABELS = {
    "broadening": "확산 중",
    "persisting": "지속 중",
    "transition_attempt": "전환 시도",
    "conflicting": "충돌",
    "low_signal": "저신호 / 관망",
    "unavailable": "자료 부족",
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


def _number(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _family_values(row: pd.Series, suffix: str) -> dict[str, float]:
    values: dict[str, float] = {}
    for family in PATTERN_FAMILY_KEYS:
        value = _number(row.get(f"{family}__{suffix}"))
        if value is not None:
            values[family] = value
    return values


def _mean_available(values: dict[str, float], families: Sequence[str]) -> float | None:
    available = [values[family] for family in families if family in values]
    return float(sum(available) / len(available)) if available else None


def _breadth(row: pd.Series, family: str) -> float:
    return float(_number(row.get(f"{family}__breadth")) or 0.0)


def _material(value: float | None) -> bool:
    return value is not None and abs(value) >= SIGNAL_Z_THRESHOLD


def _aligned(left: float | None, right: float | None) -> bool:
    return _material(left) and _material(right) and float(left) * float(right) > 0


def _has_family_conflict(values: dict[str, float]) -> bool:
    risk_on = values.get("risk_on")
    safe_haven = values.get("safe_haven")
    return bool(
        _material(risk_on)
        and _material(safe_haven)
        and float(risk_on) * float(safe_haven) > 0
    )


def _transition_state(
    *,
    one: dict[str, float],
    five: dict[str, float],
    twenty: dict[str, float],
    row: pd.Series,
) -> str:
    if min(len(one), len(five), len(twenty)) < 4:
        return "unavailable"
    all_values = [*one.values(), *five.values(), *twenty.values()]
    if not any(_material(value) for value in all_values):
        return "low_signal"
    if _has_family_conflict(five):
        return "conflicting"
    reversal_count = sum(
        _aligned(one.get(family), five.get(family))
        and _material(twenty.get(family))
        and float(five[family]) * float(twenty[family]) < 0
        for family in PATTERN_FAMILY_KEYS
        if family in five and family in twenty
    )
    if reversal_count > 0:
        return "transition_attempt"
    broadening = any(
        _aligned(five.get(family), twenty.get(family))
        and abs(five[family]) - abs(twenty[family]) >= SIGNAL_Z_THRESHOLD
        and _breadth(row, family) >= 0.6
        for family in PATTERN_FAMILY_KEYS
        if family in five and family in twenty
    )
    if broadening:
        return "broadening"
    if any(
        _aligned(five.get(family), twenty.get(family))
        for family in PATTERN_FAMILY_KEYS
    ):
        return "persisting"
    return "low_signal"


def classify_pattern_state(row: pd.Series) -> dict[str, Any]:
    """Classify the latest observable family state without assigning a forecast."""

    one = _family_values(row, "1d_z")
    five = _family_values(row, "5d_z")
    twenty = _family_values(row, "20d_z")
    macro_pressure = _mean_available(
        five,
        ("rate_pressure", "dollar_pressure", "inflation_pressure"),
    )
    conflict = _has_family_conflict(five)
    risk_on = five.get("risk_on")
    defensive_confirmed = (
        risk_on is not None
        and risk_on <= -SIGNAL_Z_THRESHOLD
        and (
            five.get("safe_haven", 0.0) >= SIGNAL_Z_THRESHOLD
            or five.get("dollar_pressure", 0.0) >= SIGNAL_Z_THRESHOLD
        )
    )
    inflation_confirmations = sum(
        five.get(key, 0.0) >= SIGNAL_Z_THRESHOLD
        for key in ("rate_pressure", "dollar_pressure", "inflation_pressure")
    )
    if conflict:
        regime = "mixed"
    elif inflation_confirmations >= 2 and five.get("risk_on", 0.0) < SIGNAL_Z_THRESHOLD:
        regime = "inflation_rate_pressure"
    elif defensive_confirmed:
        regime = "defensive"
    elif five.get("risk_on", 0.0) >= SIGNAL_Z_THRESHOLD and _breadth(row, "risk_on") >= 0.6:
        regime = "risk_seeking"
    else:
        regime = "mixed"
    transition = _transition_state(one=one, five=five, twenty=twenty, row=row)
    return {
        "regime": regime,
        "transition": transition,
        "macro_pressure": macro_pressure,
    }


def _family_snapshot(row: pd.Series, family: str) -> dict[str, Any]:
    values = {
        "one_day": _number(row.get(f"{family}__1d_z")),
        "five_day": _number(row.get(f"{family}__5d_z")),
        "twenty_day": _number(row.get(f"{family}__20d_z")),
    }
    available = [value for value in values.values() if value is not None]
    return {
        "status": "READY" if len(available) == 3 else "UNAVAILABLE",
        **values,
        "breadth": _number(row.get(f"{family}__breadth")),
        "five_day_persistence": _number(row.get(f"{family}__5d_persistence")),
        "twenty_day_persistence": _number(row.get(f"{family}__20d_persistence")),
    }


def _pattern_status(families: dict[str, dict[str, Any]]) -> str:
    ready_count = sum(item["status"] == "READY" for item in families.values())
    if ready_count == len(PATTERN_FAMILY_KEYS):
        return "READY"
    if ready_count >= 4:
        return "PARTIAL"
    return "UNAVAILABLE"


def _pattern_summary(state: dict[str, Any]) -> str:
    regime = REGIME_LABELS[state["regime"]]
    transition = TRANSITION_LABELS[state["transition"]]
    if state["regime"] == "defensive":
        return f"방어 흐름이 우세하며 현재 패턴은 {transition}입니다."
    if state["regime"] == "risk_seeking":
        return f"위험선호 흐름이 우세하며 현재 패턴은 {transition}입니다."
    if state["regime"] == "inflation_rate_pressure":
        return f"물가·금리 부담이 우세하며 현재 패턴은 {transition}입니다."
    return f"{regime}로 단일 방향 우위가 약하며 현재 패턴은 {transition}입니다."


def _pattern_evidence(state: dict[str, Any], families: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    current = [
        f"현재 체제: {REGIME_LABELS[state['regime']]}",
        f"전환 상태: {TRANSITION_LABELS[state['transition']]}",
    ]
    strongest = sorted(
        (
            (family, abs(item["five_day"]))
            for family, item in families.items()
            if item["five_day"] is not None
        ),
        key=lambda pair: pair[1],
        reverse=True,
    )
    if strongest:
        current.append(f"5D 절대 강도가 가장 큰 family: {strongest[0][0]}")
    return {"current": current, "transition": [TRANSITION_LABELS[state["transition"]]]}


def _change_conditions(state: dict[str, Any]) -> list[str]:
    if state["transition"] == "transition_attempt":
        return [
            "현재 1D 반전이 5D 방향으로 유지되는지 확인합니다.",
            "5D breadth가 0.6 이상 유지되어야 전환 해석이 강화됩니다.",
        ]
    if state["transition"] == "persisting":
        return [
            "1D 방향이 5D 흐름과 반대로 material하게 바뀌는지 확인합니다.",
            "5D persistence가 약해지면 지속 해석을 낮춥니다.",
        ]
    if state["transition"] == "conflicting":
        return ["위험선호와 안전자산 family 중 어느 쪽이 5D breadth를 확보하는지 확인합니다."]
    return ["5D family score가 material threshold를 넘는지 확인합니다."]


def _index_date(value: Any) -> str:
    return pd.Timestamp(value).date().isoformat()


def state_from_feature_row(
    state_date: object,
    row: pd.Series,
) -> dict[str, Any]:
    """Build the canonical coordinate, regime, and transition for one session."""

    state = classify_pattern_state(row)
    five = _family_values(row, "5d_z")
    x = five.get("risk_on")
    pressure_values = {
        family: five[family]
        for family in ("rate_pressure", "dollar_pressure", "inflation_pressure")
        if family in five
    }
    y = _mean_available(
        pressure_values,
        ("rate_pressure", "dollar_pressure", "inflation_pressure"),
    )
    return {
        "date": _index_date(state_date),
        "x": float(x) if x is not None else 0.0,
        "y": float(y) if y is not None else 0.0,
        "regime": state["regime"],
        "regime_label": REGIME_LABELS[state["regime"]],
        "transition": state["transition"],
        "transition_label": TRANSITION_LABELS[state["transition"]],
    }


def build_pattern_state_frame(feature_frame: pd.DataFrame) -> pd.DataFrame:
    """Return one canonical state row per completed feature session."""

    columns = [
        "date",
        "x",
        "y",
        "regime",
        "regime_label",
        "transition",
        "transition_label",
        *[f"{family}__5d_z" for family in PATTERN_FAMILY_KEYS],
    ]
    if feature_frame.empty:
        return pd.DataFrame(columns=columns).rename_axis("Date")
    records: list[dict[str, Any]] = []
    dates: list[pd.Timestamp] = []
    for current_date, row in feature_frame.sort_index().iterrows():
        record = state_from_feature_row(current_date, row)
        for family in PATTERN_FAMILY_KEYS:
            record[f"{family}__5d_z"] = _number(row.get(f"{family}__5d_z"))
        records.append(record)
        dates.append(pd.Timestamp(current_date))
    return pd.DataFrame(records, index=pd.DatetimeIndex(dates, name="Date"), columns=columns)


def _pattern_path(feature_frame: pd.DataFrame) -> list[dict[str, Any]]:
    return [
        state_from_feature_row(current_date, row)
        for current_date, row in feature_frame.iterrows()
    ]


def _empty_pattern_snapshot(reason: str) -> dict[str, Any]:
    return {
        "schema_version": "futures_macro_pattern_v1",
        "state_schema_version": PATTERN_STATE_SCHEMA_VERSION,
        "status": "UNAVAILABLE",
        "as_of_date": None,
        "regime": "mixed",
        "regime_label": REGIME_LABELS["mixed"],
        "transition": "unavailable",
        "transition_label": TRANSITION_LABELS["unavailable"],
        "summary": reason,
        "families": {},
        "evidence": {"current": [], "transition": []},
        "change_conditions": [],
        "path": [],
        "ribbon": [],
        "coverage": {"available_family_count": 0, "required_family_count": len(PATTERN_FAMILY_KEYS)},
    }


def build_current_pattern_snapshot(
    feature_frame: pd.DataFrame,
    *,
    path_limit: int = OBSERVED_TRAIL_SESSIONS,
    ribbon_limit: int = PATTERN_RIBBON_SESSIONS,
) -> dict[str, Any]:
    """Summarize the latest regime, transition, path, and confirmation conditions."""

    if feature_frame.empty:
        return _empty_pattern_snapshot("다중 기간 패턴을 계산할 일봉 이력이 부족합니다.")
    ordered = feature_frame.sort_index()
    latest = ordered.iloc[-1]
    state = classify_pattern_state(latest)
    families = {
        family: _family_snapshot(latest, family)
        for family in PATTERN_FAMILY_KEYS
    }
    path = _pattern_path(ordered.tail(path_limit))
    ribbon_path = _pattern_path(ordered.tail(ribbon_limit))
    return {
        "schema_version": "futures_macro_pattern_v1",
        "state_schema_version": PATTERN_STATE_SCHEMA_VERSION,
        "status": _pattern_status(families),
        "as_of_date": _index_date(ordered.index[-1]),
        **state,
        "regime_label": REGIME_LABELS[state["regime"]],
        "transition_label": TRANSITION_LABELS[state["transition"]],
        "summary": _pattern_summary(state),
        "families": families,
        "evidence": _pattern_evidence(state, families),
        "change_conditions": _change_conditions(state),
        "path": path,
        "ribbon": [
            {
                "date": item["date"],
                "regime": item["regime"],
                "regime_label": item["regime_label"],
                "transition": item["transition"],
                "transition_label": item["transition_label"],
            }
            for item in ribbon_path
        ],
        "coverage": {
            "available_family_count": sum(item["status"] == "READY" for item in families.values()),
            "required_family_count": len(PATTERN_FAMILY_KEYS),
            "available_symbol_count": int(_number(latest.get("available_symbol_count")) or 0),
        },
    }
