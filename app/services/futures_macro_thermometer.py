from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, date
from time import monotonic
from typing import Any

import pandas as pd

from finance.data.futures_market import DEFAULT_CORE_FUTURES_SYMBOLS, DEFAULT_FUTURES_INSTRUMENTS


QueryFn = Callable[[str, str, Sequence[Any] | None], list[dict[str, Any]]]

DAILY_INTERVAL = "1d"
DEFAULT_LOOKBACK_DAYS = 420
MIN_RECOMMENDED_DAYS = 126
FULL_POSITION_DAYS = 252
SIGNAL_Z_THRESHOLD = 0.5
STRONG_SIGNAL_Z_THRESHOLD = 1.0
OVERVIEW_MACRO_SNAPSHOT_CACHE_TTL_SECONDS = 900
_OVERVIEW_MACRO_SNAPSHOT_CACHE: dict[tuple[Any, ...], tuple[float, dict[str, Any]]] = {}

SYMBOL_ROLE_LABELS = {
    "ES=F": "S&P 500 risk appetite",
    "NQ=F": "growth / technology appetite",
    "YM=F": "blue-chip risk appetite",
    "RTY=F": "small-cap / cyclical breadth",
    "ZN=F": "10Y rate pressure inverse",
    "ZB=F": "30Y rate pressure inverse",
    "CL=F": "oil / inflation impulse",
    "GC=F": "gold safe-haven / real-rate proxy",
    "SI=F": "silver precious metal beta",
    "HG=F": "copper / global growth proxy",
    "NG=F": "natural gas, lower macro weight",
    "6E=F": "euro vs dollar",
    "6J=F": "yen vs dollar / safe haven",
    "6B=F": "sterling vs dollar",
    "6A=F": "aussie dollar / China growth proxy",
    "6C=F": "canadian dollar / oil beta",
}


@dataclass(frozen=True)
class ScoreDefinition:
    name: str
    description: str
    members: dict[str, float]
    positive_label: str
    negative_label: str
    neutral_label: str
    positive_tone: str
    negative_tone: str


SCORE_DEFINITIONS: tuple[ScoreDefinition, ...] = (
    ScoreDefinition(
        name="Risk-On Score",
        description="미국 주가지수 선물 기반 위험선호 점수",
        members={"ES=F": 1.0, "NQ=F": 1.0, "YM=F": 1.0, "RTY=F": 1.0},
        positive_label="Risk-on",
        negative_label="Risk-off",
        neutral_label="Mixed",
        positive_tone="positive",
        negative_tone="danger",
    ),
    ScoreDefinition(
        name="Growth Score",
        description="경기민감 / 글로벌 성장 기대 점수",
        members={"RTY=F": 1.0, "HG=F": 1.0, "CL=F": 1.0, "6A=F": 1.0},
        positive_label="Growth-sensitive bid",
        negative_label="Growth concern",
        neutral_label="Mixed growth",
        positive_tone="positive",
        negative_tone="danger",
    ),
    ScoreDefinition(
        name="Rate Pressure Score",
        description="채권선물 가격 하락을 금리 상승 부담으로 변환한 점수",
        members={"ZN=F": -1.0, "ZB=F": -1.0},
        positive_label="Rate pressure up",
        negative_label="Rate pressure easing",
        neutral_label="Rates mixed",
        positive_tone="danger",
        negative_tone="positive",
    ),
    ScoreDefinition(
        name="Dollar Pressure Score",
        description="주요 FX 선물 하락을 달러 강세 압력으로 변환한 점수",
        members={"6E=F": -1.0, "6J=F": -1.0, "6B=F": -1.0, "6A=F": -1.0, "6C=F": -1.0},
        positive_label="Dollar pressure up",
        negative_label="Dollar pressure easing",
        neutral_label="Dollar mixed",
        positive_tone="danger",
        negative_tone="positive",
    ),
    ScoreDefinition(
        name="Safe Haven Score",
        description="금 / 채권 / 엔 선물 기반 안전자산 선호 점수",
        members={"GC=F": 1.0, "ZN=F": 1.0, "ZB=F": 1.0, "6J=F": 1.0},
        positive_label="Safe haven bid",
        negative_label="Safe haven fading",
        neutral_label="Safe haven mixed",
        positive_tone="warning",
        negative_tone="neutral",
    ),
    ScoreDefinition(
        name="Inflation Pressure Score",
        description="에너지 / 원자재 기반 인플레이션 압력 점수",
        members={"CL=F": 1.0, "NG=F": 0.5, "HG=F": 1.0},
        positive_label="Inflation pressure up",
        negative_label="Inflation pressure easing",
        neutral_label="Inflation mixed",
        positive_tone="warning",
        negative_tone="positive",
    ),
)

CAUTION_LINES = [
    "이 기능은 투자 판단 자동화가 아니라 시장 해석 보조 기능입니다.",
    "선물 가격은 정규장 방향을 확정적으로 예측하지 않습니다.",
    "야간 / 비정규 시간대에는 유동성이 낮아 움직임이 과장될 수 있습니다.",
    "Historical validation은 과거 일관성 평가이며 예측 보장이 아닙니다.",
    "yfinance continuous futures는 실제 roll / 만기 구조와 다를 수 있습니다.",
]


def _default_query(db_name: str, sql: str, params: Sequence[Any] | None = None) -> list[dict[str, Any]]:
    import pymysql

    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="1234",
        port=3306,
        charset="utf8mb4",
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            cur.execute(f"USE {db_name}")
            cur.execute(sql, params)
            return list(cur.fetchall())
    finally:
        conn.close()


def _instrument_rows(query_fn: QueryFn) -> list[dict[str, Any]]:
    try:
        rows = query_fn(
            "finance_meta",
            """
            SELECT provider_symbol, display_name, futures_group, exchange, contract_hint,
                   source, active, sort_order
            FROM futures_instrument
            WHERE active = 1
            ORDER BY sort_order, provider_symbol
            """,
            None,
        )
    except Exception:
        rows = []
    return [dict(row) for row in rows] if rows else [dict(row) for row in DEFAULT_FUTURES_INSTRUMENTS]


def _load_daily_rows(
    query_fn: QueryFn,
    *,
    symbols: Sequence[str],
    lookback_days: int,
) -> list[dict[str, Any]]:
    if not symbols:
        return []
    placeholders = ", ".join(["%s"] * len(symbols))
    params: list[Any] = [DAILY_INTERVAL, *symbols, max(1, int(lookback_days))]
    try:
        return query_fn(
            "finance_price",
            f"""
            SELECT provider_symbol, interval_code, candle_time_utc,
                   open, high, low, close, volume, source, provider_status
            FROM futures_ohlcv
            WHERE interval_code = %s
              AND provider_symbol IN ({placeholders})
              AND candle_time_utc >= DATE_SUB(UTC_TIMESTAMP(), INTERVAL %s DAY)
            ORDER BY provider_symbol, candle_time_utc
            """,
            params,
        )
    except Exception:
        return []


def _to_timestamp(value: Any) -> pd.Timestamp | None:
    if value in (None, ""):
        return None
    ts = pd.Timestamp(value)
    if pd.isna(ts):
        return None
    if ts.tzinfo is None:
        ts = ts.tz_localize(UTC)
    else:
        ts = ts.tz_convert(UTC)
    return ts


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


def _round(value: float | None, digits: int = 2) -> float | None:
    return round(float(value), digits) if value is not None else None


def _pct_return(close: pd.Series, days: int) -> float | None:
    if len(close) <= days:
        return None
    previous = _safe_float(close.iloc[-(days + 1)])
    latest = _safe_float(close.iloc[-1])
    if latest is None or previous in (None, 0):
        return None
    return ((latest / float(previous)) - 1.0) * 100.0


def _direction(value: float | None) -> str:
    if value is None:
        return "-"
    if value >= 0.05:
        return "Up"
    if value <= -0.05:
        return "Down"
    return "Flat"


def _percentile_position(close: pd.Series) -> float | None:
    sample = close.tail(FULL_POSITION_DAYS).dropna().astype(float)
    if len(sample) < 2:
        return None
    latest = sample.iloc[-1]
    return float((sample <= latest).mean() * 100.0)


def _candle_frame(rows: Sequence[dict[str, Any]]) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for row in rows:
        ts = _to_timestamp(row.get("candle_time_utc"))
        close = _safe_float(row.get("close"))
        if ts is None or close is None:
            continue
        records.append(
            {
                "provider_symbol": str(row.get("provider_symbol") or "").strip().upper(),
                "ts": ts,
                "Date": ts.date().isoformat(),
                "Close": close,
                "Open": _safe_float(row.get("open")),
                "High": _safe_float(row.get("high")),
                "Low": _safe_float(row.get("low")),
                "Volume": _safe_float(row.get("volume")),
                "Source": row.get("source") or "yfinance",
                "provider_status": row.get("provider_status") or "ok",
            }
        )
    if not records:
        return pd.DataFrame()
    frame = pd.DataFrame(records).sort_values(["provider_symbol", "ts"])
    return frame.drop_duplicates(subset=["provider_symbol", "Date"], keep="last")


def normalize_futures_macro_daily_candles(rows: Sequence[dict[str, Any]]) -> pd.DataFrame:
    return _candle_frame(rows)


def compute_symbol_metrics(
    candles: pd.DataFrame,
    *,
    instruments: Sequence[dict[str, Any]],
    selected_symbols: Sequence[str],
) -> pd.DataFrame:
    by_symbol = {
        str(row.get("provider_symbol") or "").strip().upper(): row
        for row in instruments
    }
    rows: list[dict[str, Any]] = []
    for symbol in selected_symbols:
        info = by_symbol.get(symbol, {"provider_symbol": symbol, "display_name": symbol, "futures_group": "Other"})
        frame = candles[candles["provider_symbol"] == symbol].sort_values("ts") if not candles.empty else pd.DataFrame()
        if frame.empty:
            rows.append(
                {
                    "Group": info.get("futures_group") or "Other",
                    "Symbol": symbol,
                    "Name": info.get("display_name") or symbol,
                    "Close": None,
                    "Latest Date": None,
                    "1D %": None,
                    "3D %": None,
                    "5D %": None,
                    "20D %": None,
                    "60D %": None,
                    "60D Vol %": None,
                    "Std Move": None,
                    "252D Position %": None,
                    "Data Days": 0,
                    "Direction": "Missing",
                    "Role": SYMBOL_ROLE_LABELS.get(symbol, ""),
                    "Source": info.get("source") or "yfinance",
                }
            )
            continue

        close = frame["Close"].dropna().astype(float)
        returns = close.pct_change().dropna()
        daily_return = _pct_return(close, 1)
        rolling_vol = _safe_float(returns.tail(60).std(ddof=0)) if len(returns) >= 60 else None
        standardized = None
        if daily_return is not None and rolling_vol and rolling_vol > 1e-9:
            standardized = (daily_return / 100.0) / rolling_vol
        latest = frame.iloc[-1]
        rows.append(
            {
                "Group": info.get("futures_group") or "Other",
                "Symbol": symbol,
                "Name": info.get("display_name") or symbol,
                "Close": _round(_safe_float(latest.get("Close")), 4),
                "Latest Date": latest.get("Date"),
                "1D %": _round(daily_return, 2),
                "3D %": _round(_pct_return(close, 3), 2),
                "5D %": _round(_pct_return(close, 5), 2),
                "20D %": _round(_pct_return(close, 20), 2),
                "60D %": _round(_pct_return(close, 60), 2),
                "60D Vol %": _round(rolling_vol * 100.0 if rolling_vol is not None else None, 2),
                "Std Move": _round(standardized, 2),
                "252D Position %": _round(_percentile_position(close), 1),
                "Data Days": int(len(close)),
                "Direction": _direction(daily_return),
                "Role": SYMBOL_ROLE_LABELS.get(symbol, ""),
                "Source": latest.get("Source") or info.get("source") or "yfinance",
            }
        )
    return pd.DataFrame(rows)


def _score_value(mean_z: float | None) -> int | None:
    if mean_z is None:
        return None
    return int(round(max(-100.0, min(100.0, float(mean_z) * 25.0))))


def _score_direction(definition: ScoreDefinition, score: int | None) -> str:
    if score is None:
        return "Missing"
    if score >= 20:
        return definition.positive_label
    if score <= -20:
        return definition.negative_label
    return definition.neutral_label


def _score_tone(definition: ScoreDefinition, score: int | None) -> str:
    if score is None:
        return "neutral"
    if score >= 20:
        return definition.positive_tone
    if score <= -20:
        return definition.negative_tone
    return "neutral"


def compute_macro_scores(symbol_metrics: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    metric_by_symbol = (
        {str(row["Symbol"]): dict(row) for _, row in symbol_metrics.iterrows()}
        if isinstance(symbol_metrics, pd.DataFrame) and not symbol_metrics.empty
        else {}
    )
    score_rows: list[dict[str, Any]] = []
    component_rows: list[dict[str, Any]] = []
    for definition in SCORE_DEFINITIONS:
        weighted_total = 0.0
        weight_total = 0.0
        used = 0
        strong: list[str] = []
        weak: list[str] = []
        missing: list[str] = []
        for symbol, signed_weight in definition.members.items():
            metric = metric_by_symbol.get(symbol, {})
            raw_z = _safe_float(metric.get("Std Move"))
            weight = abs(float(signed_weight))
            score_move = raw_z * (1.0 if signed_weight >= 0 else -1.0) if raw_z is not None else None
            if score_move is None:
                missing.append(symbol)
            else:
                weighted_total += score_move * weight
                weight_total += weight
                used += 1
                label = f"{symbol} {score_move:+.2f}z"
                if abs(score_move) >= STRONG_SIGNAL_Z_THRESHOLD:
                    strong.append(label)
                elif abs(score_move) < SIGNAL_Z_THRESHOLD:
                    weak.append(label)
            component_rows.append(
                {
                    "Score": definition.name,
                    "Symbol": symbol,
                    "Name": metric.get("Name") or symbol,
                    "Raw Std Move": _round(raw_z, 2),
                    "Score Move": _round(score_move, 2),
                    "Weight": weight,
                    "1D %": metric.get("1D %"),
                    "Role": SYMBOL_ROLE_LABELS.get(symbol, ""),
                }
            )
        mean_z = weighted_total / weight_total if weight_total > 0 else None
        score = _score_value(mean_z)
        score_rows.append(
            {
                "Score": definition.name,
                "Value": score,
                "Direction": _score_direction(definition, score),
                "Mean Z": _round(mean_z, 2),
                "Members": ", ".join(definition.members),
                "Strong Evidence": ", ".join(strong[:4]) or "-",
                "Weak Evidence": ", ".join(weak[:4]) or "-",
                "Missing": ", ".join(missing) or "-",
                "Coverage": f"{used}/{len(definition.members)}",
                "Tone": _score_tone(definition, score),
                "Description": definition.description,
            }
        )
    return pd.DataFrame(score_rows), pd.DataFrame(component_rows)


def _value_by_score(scores: pd.DataFrame, score_name: str) -> int | None:
    if scores.empty:
        return None
    matches = scores[scores["Score"] == score_name]
    if matches.empty:
        return None
    value = matches.iloc[0].get("Value")
    return int(value) if value is not None and not pd.isna(value) else None


def _std_by_symbol(symbols: pd.DataFrame, symbol: str) -> float | None:
    if symbols.empty:
        return None
    matches = symbols[symbols["Symbol"] == symbol]
    if matches.empty:
        return None
    return _safe_float(matches.iloc[0].get("Std Move"))


def _component_phrase(symbols: pd.DataFrame, members: Sequence[str], *, positive: bool = True) -> str:
    parts: list[str] = []
    for symbol in members:
        z_value = _std_by_symbol(symbols, symbol)
        if z_value is None:
            continue
        if positive and z_value >= SIGNAL_Z_THRESHOLD:
            parts.append(f"{symbol} {z_value:+.2f}z")
        if not positive and z_value <= -SIGNAL_Z_THRESHOLD:
            parts.append(f"{symbol} {z_value:+.2f}z")
    return ", ".join(parts[:4])


def generate_market_interpretation(scores: pd.DataFrame, symbols: pd.DataFrame) -> dict[str, Any]:
    risk_on = _value_by_score(scores, "Risk-On Score") or 0
    growth = _value_by_score(scores, "Growth Score") or 0
    rate_pressure = _value_by_score(scores, "Rate Pressure Score") or 0
    dollar_pressure = _value_by_score(scores, "Dollar Pressure Score") or 0
    safe_haven = _value_by_score(scores, "Safe Haven Score") or 0
    inflation = _value_by_score(scores, "Inflation Pressure Score") or 0

    es_z = _std_by_symbol(symbols, "ES=F") or 0.0
    nq_z = _std_by_symbol(symbols, "NQ=F") or 0.0
    rty_z = _std_by_symbol(symbols, "RTY=F") or 0.0
    gc_z = _std_by_symbol(symbols, "GC=F") or 0.0
    hg_z = _std_by_symbol(symbols, "HG=F") or 0.0

    scenario = "혼재된 매크로 흐름"
    summary = "현재 선물 일봉 기준 신호가 한 방향으로 강하게 모이지 않아 혼재된 시장 흐름으로 해석됩니다."
    evidence: list[str] = []

    if inflation >= 20 and rate_pressure >= 20 and nq_z <= -SIGNAL_Z_THRESHOLD:
        scenario = "인플레이션 쇼크 가능성"
        summary = "에너지 / 원자재와 금리 상승 압력이 동시에 강해지며 성장주에 부담을 줄 가능성으로 해석됩니다."
        evidence = [
            f"Inflation Pressure Score {inflation:+d}, Rate Pressure Score {rate_pressure:+d}",
            _component_phrase(symbols, ["CL=F", "NG=F", "HG=F"], positive=True),
            f"NQ=F {nq_z:+.2f}z",
        ]
    elif risk_on <= -20 and growth <= -20 and safe_haven >= 20:
        scenario = "경기침체 우려 / risk-off"
        summary = "주식과 경기민감 선물이 약하고 금 / 채권 / 엔 쪽 안전자산 선호가 강화된 risk-off 가능성으로 해석됩니다."
        evidence = [
            f"Risk-On Score {risk_on:+d}, Growth Score {growth:+d}, Safe Haven Score {safe_haven:+d}",
            _component_phrase(symbols, ["ES=F", "RTY=F", "HG=F", "CL=F"], positive=False),
            _component_phrase(symbols, ["GC=F", "ZN=F", "ZB=F", "6J=F"], positive=True),
        ]
    elif dollar_pressure >= 20 and risk_on <= -10 and hg_z <= -SIGNAL_Z_THRESHOLD:
        scenario = "달러 강세 risk-off"
        summary = "주요 FX 선물이 약세이고 지수 / 구리도 눌려 달러 강세가 글로벌 위험자산에 부담을 주는 흐름으로 해석됩니다."
        evidence = [
            f"Dollar Pressure Score {dollar_pressure:+d}, Risk-On Score {risk_on:+d}",
            _component_phrase(symbols, ["6E=F", "6B=F", "6A=F", "6C=F"], positive=False),
            f"HG=F {hg_z:+.2f}z",
        ]
    elif rate_pressure >= 20 and nq_z <= -SIGNAL_Z_THRESHOLD and gc_z <= -SIGNAL_Z_THRESHOLD:
        scenario = "금리 상승 부담"
        summary = "ZN / ZB 가격 하락이 금리 상승 압력으로 해석되고, 나스닥과 금도 약해 성장주 / 금 가격 부담을 보조적으로 볼 수 있습니다."
        evidence = [
            f"Rate Pressure Score {rate_pressure:+d}",
            f"NQ=F {nq_z:+.2f}z, GC=F {gc_z:+.2f}z",
            _component_phrase(symbols, ["ZN=F", "ZB=F"], positive=False),
        ]
    elif nq_z >= SIGNAL_Z_THRESHOLD and es_z >= 0.2 and rty_z <= 0.2 and rate_pressure < 0:
        scenario = "기술주 중심 랠리"
        summary = "나스닥과 S&P 500은 강하지만 러셀2000 확산은 제한적이며, 금리 부담 완화가 기술주 중심으로 반영되는 흐름으로 해석됩니다."
        evidence = [
            f"NQ=F {nq_z:+.2f}z, ES=F {es_z:+.2f}z, RTY=F {rty_z:+.2f}z",
            f"Rate Pressure Score {rate_pressure:+d}",
        ]
    elif risk_on >= 20 and growth >= 15 and rate_pressure <= 20 and dollar_pressure <= 10:
        scenario = "좋은 risk-on"
        summary = "지수 선물과 경기민감 proxy가 함께 강하고 금리 / 달러 부담은 제한적인 risk-on 가능성으로 해석됩니다."
        evidence = [
            f"Risk-On Score {risk_on:+d}, Growth Score {growth:+d}",
            _component_phrase(symbols, ["ES=F", "NQ=F", "RTY=F", "HG=F", "6A=F"], positive=True),
            f"Rate Pressure Score {rate_pressure:+d}, Dollar Pressure Score {dollar_pressure:+d}",
        ]
    elif risk_on <= -20 and safe_haven >= 20:
        scenario = "안전자산 선호 risk-off"
        summary = "지수 선물은 약하고 금 / 채권 / 엔 선물이 강해 안전자산 선호가 커진 흐름으로 해석됩니다."
        evidence = [
            f"Risk-On Score {risk_on:+d}, Safe Haven Score {safe_haven:+d}",
            _component_phrase(symbols, ["GC=F", "ZN=F", "ZB=F", "6J=F"], positive=True),
        ]
    else:
        evidence = [
            f"Risk-On {risk_on:+d}, Growth {growth:+d}, Rate Pressure {rate_pressure:+d}",
            f"Dollar Pressure {dollar_pressure:+d}, Safe Haven {safe_haven:+d}, Inflation {inflation:+d}",
        ]

    cleaned_evidence = [item for item in evidence if item and item != "-"]
    return {
        "scenario": scenario,
        "summary": summary,
        "evidence": cleaned_evidence,
    }


def _score_values(scores: pd.DataFrame) -> dict[str, int]:
    out: dict[str, int] = {}
    if not isinstance(scores, pd.DataFrame) or scores.empty:
        return out
    for _, row in scores.iterrows():
        value = row.get("Value")
        if value is None or pd.isna(value):
            continue
        out[str(row.get("Score") or "")] = int(value)
    return out


def _conflicting_score_evidence(scores: pd.DataFrame) -> list[str]:
    values = _score_values(scores)
    risk_on = values.get("Risk-On Score", 0)
    growth = values.get("Growth Score", 0)
    rate_pressure = values.get("Rate Pressure Score", 0)
    dollar_pressure = values.get("Dollar Pressure Score", 0)
    safe_haven = values.get("Safe Haven Score", 0)
    inflation = values.get("Inflation Pressure Score", 0)
    conflicts: list[str] = []
    if risk_on >= 20 and safe_haven >= 20:
        conflicts.append("Risk-On and Safe Haven scores are both elevated.")
    if risk_on >= 20 and rate_pressure >= 20:
        conflicts.append("Risk-On is elevated while Rate Pressure is also elevated.")
    if risk_on >= 20 and dollar_pressure >= 20:
        conflicts.append("Risk-On is elevated while Dollar Pressure is also elevated.")
    if growth >= 20 and safe_haven >= 20:
        conflicts.append("Growth-sensitive bid and safe-haven bid are both elevated.")
    if risk_on <= -20 and rate_pressure <= -20:
        conflicts.append("Risk-Off price action appears while rate pressure is easing.")
    if risk_on <= -20 and inflation <= -20:
        conflicts.append("Risk-Off price action appears while inflation pressure is easing.")
    return conflicts


def build_current_evidence_groups(scores: pd.DataFrame, components: pd.DataFrame, symbols: pd.DataFrame) -> dict[str, Any]:
    strong: list[str] = []
    weak: list[str] = []
    missing: list[str] = []
    if isinstance(components, pd.DataFrame) and not components.empty:
        for _, row in components.iterrows():
            score_move = _safe_float(row.get("Score Move"))
            symbol = str(row.get("Symbol") or "").strip()
            score = str(row.get("Score") or "").strip()
            if not symbol or score_move is None:
                continue
            label = f"{score} / {symbol} {score_move:+.2f}z"
            if abs(score_move) >= STRONG_SIGNAL_Z_THRESHOLD:
                strong.append(label)
            elif abs(score_move) < SIGNAL_Z_THRESHOLD:
                weak.append(label)
    if isinstance(symbols, pd.DataFrame) and not symbols.empty:
        missing = [
            str(row.get("Symbol") or "").strip()
            for _, row in symbols.iterrows()
            if int(row.get("Data Days") or 0) <= 0
        ]
    return {
        "strong": strong[:12],
        "weak": weak[:12],
        "missing": missing[:12],
        "conflicting": _conflicting_score_evidence(scores),
        "counts": {
            "strong": len(strong),
            "weak": len(weak),
            "missing": len(missing),
            "conflicting": len(_conflicting_score_evidence(scores)),
        },
    }


def build_macro_thermometer_read_model(
    *,
    candles: pd.DataFrame,
    instruments: Sequence[dict[str, Any]],
    selected_symbols: Sequence[str],
    daily_rows: Sequence[dict[str, Any]] | None = None,
    as_of_date: str | None = None,
) -> dict[str, Any]:
    symbol_metrics = compute_symbol_metrics(candles, instruments=instruments, selected_symbols=selected_symbols)
    score_rows, component_rows = compute_macro_scores(symbol_metrics)
    coverage = _coverage(symbol_metrics, daily_rows or [])
    warnings = _warnings(symbol_metrics, coverage)
    interpretation = generate_market_interpretation(score_rows, symbol_metrics)
    evidence_groups = build_current_evidence_groups(score_rows, component_rows, symbol_metrics)
    return {
        "status": _status(coverage, warnings),
        "coverage": coverage,
        "warnings": warnings,
        "scores": score_rows,
        "score_components": component_rows,
        "symbols": symbol_metrics,
        "summary": interpretation,
        "summary_sentences": [interpretation["summary"]],
        "evidence": interpretation["evidence"],
        "evidence_groups": evidence_groups,
        "cautions": list(CAUTION_LINES),
        "source_note": "Uses stored yfinance futures daily OHLCV; scores are standardized by recent 60D daily volatility.",
        "as_of_date": as_of_date or date.today().isoformat(),
    }


def _coverage(symbol_metrics: pd.DataFrame, daily_rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    if symbol_metrics.empty:
        return {
            "symbol_count": 0,
            "returnable_count": 0,
            "standardized_count": 0,
            "min_data_days": 0,
            "max_data_days": 0,
            "latest_daily_date": None,
            "raw_rows": len(daily_rows),
        }
    data_days = [int(value) for value in symbol_metrics["Data Days"].fillna(0).tolist()]
    latest_dates = [str(value) for value in symbol_metrics["Latest Date"].dropna().tolist() if str(value)]
    return {
        "symbol_count": int(len(symbol_metrics)),
        "returnable_count": int((symbol_metrics["Data Days"].fillna(0).astype(int) > 0).sum()),
        "standardized_count": int(symbol_metrics["Std Move"].notna().sum()),
        "min_data_days": min(data_days) if data_days else 0,
        "max_data_days": max(data_days) if data_days else 0,
        "latest_daily_date": max(latest_dates) if latest_dates else None,
        "raw_rows": len(daily_rows),
    }


def _warnings(symbol_metrics: pd.DataFrame, coverage: dict[str, Any]) -> list[str]:
    out: list[str] = []
    if int(coverage.get("returnable_count") or 0) <= 0:
        out.append("Stored futures daily OHLCV rows are not available yet. Run a 1y / 1d futures backfill first.")
        return out
    missing_symbols = (
        symbol_metrics[symbol_metrics["Data Days"].fillna(0).astype(int) <= 0]["Symbol"].tolist()
        if not symbol_metrics.empty
        else []
    )
    if missing_symbols:
        out.append(f"{len(missing_symbols)} futures symbols have no daily rows: {', '.join(missing_symbols[:8])}.")
    short_symbols = (
        symbol_metrics[
            (symbol_metrics["Data Days"].fillna(0).astype(int) > 0)
            & (symbol_metrics["Data Days"].fillna(0).astype(int) < MIN_RECOMMENDED_DAYS)
        ]["Symbol"].tolist()
        if not symbol_metrics.empty
        else []
    )
    if short_symbols:
        out.append(f"{len(short_symbols)} symbols have less than 6 months of daily data; standardized moves may be unstable.")
    if int(coverage.get("standardized_count") or 0) < int(coverage.get("symbol_count") or 0):
        out.append("Some symbols could not compute 60D volatility standardized moves.")
    latest_date = coverage.get("latest_daily_date")
    if latest_date:
        try:
            age_days = (date.today() - date.fromisoformat(str(latest_date))).days
            if age_days >= 7:
                out.append(f"Latest daily futures candle is {age_days} days old.")
        except ValueError:
            pass
    return out


def _status(coverage: dict[str, Any], warnings: Sequence[str]) -> str:
    if int(coverage.get("returnable_count") or 0) <= 0:
        return "MISSING"
    if warnings:
        return "REVIEW"
    return "OK"


def build_futures_macro_thermometer_snapshot(
    *,
    symbols: Sequence[str] | None = None,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
    query_fn: QueryFn | None = None,
    include_validation: bool = False,
) -> dict[str, Any]:
    query = query_fn or _default_query
    selected_symbols = [str(symbol).strip().upper() for symbol in (symbols or DEFAULT_CORE_FUTURES_SYMBOLS) if str(symbol).strip()]
    instruments = _instrument_rows(query)
    daily_rows = _load_daily_rows(query, symbols=selected_symbols, lookback_days=lookback_days)
    candles = _candle_frame(daily_rows)
    snapshot = build_macro_thermometer_read_model(
        candles=candles,
        instruments=instruments,
        selected_symbols=selected_symbols,
        daily_rows=daily_rows,
    )
    if include_validation:
        try:
            from app.services.futures_macro_validation import (
                build_futures_macro_validation_snapshot,
                build_interpretation_confidence,
            )

            validation = build_futures_macro_validation_snapshot(
                symbols=selected_symbols,
                query_fn=query,
                current_snapshot=snapshot,
            )
            confidence = build_interpretation_confidence(snapshot, validation)
        except Exception as exc:
            validation = {
                "status": "ERROR",
                "warnings": [f"Historical validation could not run: {exc}"],
                "scenario_summary": pd.DataFrame(),
                "current_scenario_metrics": {},
            }
            confidence = {
                "label": "Not Enough History",
                "tone": "warning",
                "score": 0,
                "reasons": ["Historical validation could not run."],
            }
        snapshot["validation"] = validation
        snapshot["confidence"] = confidence
        if str(confidence.get("label") or "") in {"Low Confidence", "Not Enough History"}:
            snapshot["summary_sentences"].append("다만 과거 표본이나 데이터 조건이 부족해 이 해석의 신뢰도는 낮게 봐야 합니다.")
    return snapshot


def clear_overview_futures_macro_snapshot_cache() -> None:
    _OVERVIEW_MACRO_SNAPSHOT_CACHE.clear()


def load_overview_futures_macro_snapshot(**kwargs: Any) -> dict[str, Any]:
    force_refresh = bool(kwargs.pop("force_refresh", False))
    cache_ttl_seconds = int(kwargs.pop("cache_ttl_seconds", OVERVIEW_MACRO_SNAPSHOT_CACHE_TTL_SECONDS))
    kwargs.setdefault("include_validation", True)
    kwargs.setdefault("lookback_days", 365 * 5 + 90)
    if kwargs.get("query_fn") is not None:
        return build_futures_macro_thermometer_snapshot(**kwargs)

    selected_symbols = tuple(
        str(symbol).strip().upper()
        for symbol in (kwargs.get("symbols") or DEFAULT_CORE_FUTURES_SYMBOLS)
        if str(symbol).strip()
    )
    cache_key = (
        selected_symbols,
        int(kwargs.get("lookback_days") or 0),
        bool(kwargs.get("include_validation")),
    )
    now = monotonic()
    cached = _OVERVIEW_MACRO_SNAPSHOT_CACHE.get(cache_key)
    if (
        cached is not None
        and not force_refresh
        and cache_ttl_seconds > 0
        and now - cached[0] <= cache_ttl_seconds
    ):
        return cached[1]

    snapshot = build_futures_macro_thermometer_snapshot(**kwargs)
    if cache_ttl_seconds > 0:
        _OVERVIEW_MACRO_SNAPSHOT_CACHE[cache_key] = (now, snapshot)
    return snapshot
