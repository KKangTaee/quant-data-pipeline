from __future__ import annotations

import json

import os

import re

import urllib.request

from collections.abc import Callable, Sequence

from datetime import date, datetime, timezone, timedelta

from html import unescape

from typing import Any

from urllib.parse import quote, quote_plus, urlencode, urlparse

from xml.etree import ElementTree

import pandas as pd

from finance.loaders.sentiment import (
    CNN_COMPONENT_SERIES,
    CORE_SENTIMENT_SERIES,
    load_market_sentiment_history,
    load_market_sentiment_snapshot,
)

SENTIMENT_COLUMNS = [
    "Series",
    "Value",
    "Label",
    "Observation Date",
    "Staleness Days",
    "Status",
    "Source",
]

SENTIMENT_COMPONENT_COLUMNS = [
    "Series",
    "Score",
    "Rating",
    "Observation Date",
    "Status",
]

SENTIMENT_HISTORY_COLUMNS = [
    "Date",
    "Series",
    "Value",
    "Source",
]

SENTIMENT_SERIES_LABELS = {
    "CNN_FEAR_GREED": "CNN Fear & Greed",
    "AAII_BULLISH": "AAII Bullish",
    "AAII_NEUTRAL": "AAII Neutral",
    "AAII_BEARISH": "AAII Bearish",
    "AAII_BULL_BEAR_SPREAD": "AAII Bull-Bear Spread",
    "CNN_FNG_MARKET_MOMENTUM_SP500": "Market Momentum",
    "CNN_FNG_STOCK_PRICE_STRENGTH": "Stock Price Strength",
    "CNN_FNG_STOCK_PRICE_BREADTH": "Stock Price Breadth",
    "CNN_FNG_PUT_CALL_OPTIONS": "Put / Call Options",
    "CNN_FNG_MARKET_VOLATILITY_VIX": "Market Volatility",
    "CNN_FNG_JUNK_BOND_DEMAND": "Junk Bond Demand",
    "CNN_FNG_SAFE_HAVEN_DEMAND": "Safe Haven Demand",
}

SENTIMENT_SERIES_IDS_BY_LABEL = {label: series_id for series_id, label in SENTIMENT_SERIES_LABELS.items()}

AAII_HISTORICAL_AVERAGES = {
    "bullish": 38.0,
    "neutral": 31.5,
    "bearish": 30.5,
}

CNN_COMPONENT_LEARNING_NOTES = {
    "Market Momentum": {
        "label_ko": "지수 추세",
        "what_it_checks": "S&P 500이 125일 이동평균 대비 얼마나 강한지 봅니다.",
        "greed_meaning": "지수 자체의 추세가 강해 투자자들이 위험을 받아들이는 쪽입니다.",
        "fear_meaning": "지수가 중기 평균 아래로 약해져 투자자들이 조심스러워진 상태입니다.",
        "neutral_meaning": "지수 추세가 뚜렷하게 한쪽으로 치우치지 않았습니다.",
    },
    "Stock Price Strength": {
        "label_ko": "신고가 확산",
        "what_it_checks": "NYSE 52주 신고가 종목과 신저가 종목의 균형을 봅니다.",
        "greed_meaning": "많은 종목이 신고가를 만들며 상승 리더십이 넓어지는 상태입니다.",
        "fear_meaning": "신고가보다 약한 종목이 많아 상승 리더십이 좁아진 상태입니다.",
        "neutral_meaning": "신고가와 신저가 압력이 크게 기울지 않았습니다.",
    },
    "Stock Price Breadth": {
        "label_ko": "시장 폭",
        "what_it_checks": "상승 종목 거래량과 하락 종목 거래량의 균형을 봅니다.",
        "greed_meaning": "상승 종목 쪽으로 거래가 넓게 붙어 시장 참여가 강합니다.",
        "fear_meaning": "상승 참여 폭이 약해 지수 상승이 일부 종목에 기대고 있을 수 있습니다.",
        "neutral_meaning": "상승/하락 참여 폭이 뚜렷하게 갈리지 않았습니다.",
    },
    "Put / Call Options": {
        "label_ko": "옵션 포지션",
        "what_it_checks": "풋옵션과 콜옵션 수요의 균형을 봅니다.",
        "greed_meaning": "방어적 풋 수요보다 상승 또는 위험선호 옵션 수요가 강합니다.",
        "fear_meaning": "풋옵션 수요가 늘어 하락 방어 심리가 강합니다.",
        "neutral_meaning": "옵션 시장의 상승/방어 수요가 크게 치우치지 않았습니다.",
    },
    "Market Volatility": {
        "label_ko": "변동성",
        "what_it_checks": "VIX가 50일 평균 대비 얼마나 높거나 낮은지 봅니다.",
        "greed_meaning": "변동성 압력이 낮아 시장이 비교적 안정을 가격에 반영합니다.",
        "fear_meaning": "변동성 압력이 높아 투자자들이 급락 위험을 더 크게 봅니다.",
        "neutral_meaning": "변동성은 현재 공포/탐욕 어느 쪽도 강하게 말하지 않습니다.",
    },
    "Junk Bond Demand": {
        "label_ko": "신용 위험선호",
        "what_it_checks": "고위험 회사채와 우량채의 금리 스프레드를 봅니다.",
        "greed_meaning": "고위험 채권 수요가 강해 신용시장도 위험을 받아들이는 쪽입니다.",
        "fear_meaning": "고위험 채권 수요가 약해 신용시장은 방어적으로 움직입니다.",
        "neutral_meaning": "신용시장의 위험선호가 크게 기울지 않았습니다.",
    },
    "Safe Haven Demand": {
        "label_ko": "주식 vs 안전자산",
        "what_it_checks": "최근 20거래일 주식과 국채 성과 차이를 봅니다.",
        "greed_meaning": "국채보다 주식 선호가 강해 위험자산 선호가 우세합니다.",
        "fear_meaning": "주식보다 국채 선호가 강해 방어적 심리가 우세합니다.",
        "neutral_meaning": "주식과 국채 선호가 크게 갈리지 않았습니다.",
    },
}

def _safe_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(numeric):
        return None
    return numeric

def _iso_date(value: Any) -> str | None:
    if value in (None, ""):
        return None
    ts = pd.Timestamp(value)
    if pd.isna(ts):
        return None
    return ts.strftime("%Y-%m-%d")

def _empty_sentiment_analysis(*, status: str, message: str) -> dict[str, Any]:
    return {
        "phase": "DATA_REVIEW",
        "phase_label": "데이터 확인",
        "tone": "danger" if status == "ERROR" else "warning",
        "headline": "시장 심리 해석에 필요한 데이터가 부족합니다.",
        "summary": message,
        "data_confidence": {
            "status": "Blocked" if status == "ERROR" else "Needs refresh",
            "tone": "danger" if status == "ERROR" else "warning",
            "detail": message,
        },
        "driver_summary": {"greed_count": 0, "fear_count": 0, "neutral_count": 0},
        "driver_groups": {"greed": [], "fear": [], "neutral": []},
        "range_context": [],
        "divergence": {
            "status": "데이터 없음",
            "tone": "warning",
            "headline_direction": "neutral",
            "component_direction": "neutral",
            "aaii_direction": "neutral",
            "summary": message,
            "items": [],
        },
        "component_history": [],
        "analysis_steps": [
            {
                "title": "데이터 상태",
                "status": status,
                "tone": "danger" if status == "ERROR" else "warning",
                "detail": message,
            }
        ],
        "next_checks": [
            {
                "target": "Market Sentiment refresh",
                "reason": "CNN / AAII observations must be available before reading sentiment context.",
                "tone": "warning",
            }
        ],
    }

def _empty_sentiment_snapshot(*, status: str, message: str) -> dict[str, Any]:
    return {
        "status": status,
        "rows": pd.DataFrame(columns=SENTIMENT_COLUMNS),
        "component_rows": pd.DataFrame(columns=SENTIMENT_COMPONENT_COLUMNS),
        "history_rows": pd.DataFrame(columns=SENTIMENT_HISTORY_COLUMNS),
        "coverage": {
            "cnn_score": None,
            "cnn_rating": None,
            "aaii_bearish": None,
            "aaii_bull_bear_spread": None,
            "source_count": 0,
            "stale_count": 0,
            "missing_count": 2,
        },
        "analysis": _empty_sentiment_analysis(status=status, message=message),
        "warnings": [message] if message else [],
    }

def _metadata_from_row(row: pd.Series | dict[str, Any]) -> dict[str, Any]:
    raw = row.get("missing_fields_json") if isinstance(row, pd.Series) else row.get("missing_fields_json")
    if not raw:
        return {}
    if isinstance(raw, dict):
        return dict(raw)
    try:
        parsed = json.loads(str(raw))
    except (TypeError, ValueError):
        return {}
    return parsed if isinstance(parsed, dict) else {}

def _latest_sentiment_row(frame: pd.DataFrame, series_id: str) -> pd.Series | None:
    if frame.empty or "series_id" not in frame:
        return None
    rows = frame[frame["series_id"].astype(str).str.upper() == series_id].copy()
    if rows.empty:
        return None
    rows["observation_date_sort"] = pd.to_datetime(rows.get("observation_date"), errors="coerce")
    rows = rows.sort_values("observation_date_sort", ascending=False)
    return rows.iloc[0]

def _sentiment_status(row: pd.Series | None) -> str:
    if row is None:
        return "Missing"
    if str(row.get("snapshot_status") or row.get("coverage_status") or "").lower() not in {"actual", "ok"}:
        return "Stale"
    return "OK"

def _sentiment_display_value(series_id: str, value: Any) -> str:
    numeric = _safe_float(value)
    if numeric is None:
        return "-"
    if series_id == "AAII_BULL_BEAR_SPREAD":
        return f"{numeric:+.1f} pp"
    if series_id.startswith("AAII_"):
        return f"{numeric:.1f}%"
    return f"{numeric:.1f}"

def _sentiment_table_row(row: pd.Series, *, label: str) -> dict[str, Any]:
    series_id = str(row.get("series_id") or "").upper()
    metadata = _metadata_from_row(row)
    return {
        "Series": label,
        "Value": _sentiment_display_value(series_id, row.get("value")),
        "Label": metadata.get("rating") or "-",
        "Observation Date": _iso_date(row.get("observation_date")) or "-",
        "Staleness Days": _safe_float(row.get("staleness_days")),
        "Status": _sentiment_status(row),
        "Source": row.get("source") or "-",
    }

def _sentiment_score_bucket(value: Any) -> dict[str, str]:
    numeric = _safe_float(value)
    if numeric is None:
        return {"label": "Missing", "label_ko": "데이터 없음", "direction": "neutral", "tone": "warning"}
    if numeric < 25:
        return {"label": "Extreme Fear", "label_ko": "극단적 공포", "direction": "fear", "tone": "danger"}
    if numeric < 45:
        return {"label": "Fear", "label_ko": "공포", "direction": "fear", "tone": "warning"}
    if numeric < 55:
        return {"label": "Neutral", "label_ko": "중립", "direction": "neutral", "tone": "neutral"}
    if numeric < 75:
        return {"label": "Greed", "label_ko": "탐욕", "direction": "greed", "tone": "positive"}
    return {"label": "Extreme Greed", "label_ko": "극단적 탐욕", "direction": "greed", "tone": "positive"}

def _cnn_component_note(series: Any) -> dict[str, str]:
    key = str(series or "")
    return CNN_COMPONENT_LEARNING_NOTES.get(
        key,
        {
            "label_ko": key or "-",
            "what_it_checks": "CNN Fear & Greed를 구성하는 세부 시장 행동 지표입니다.",
            "greed_meaning": "이 값이 높으면 해당 지표는 위험선호 쪽으로 해석합니다.",
            "fear_meaning": "이 값이 낮으면 해당 지표는 방어적 심리 쪽으로 해석합니다.",
            "neutral_meaning": "이 값이 중립이면 해당 지표만으로는 방향성이 강하지 않습니다.",
        },
    )

def _cnn_component_current_reading(series: Any, bucket: dict[str, str]) -> str:
    note = _cnn_component_note(series)
    direction = bucket.get("direction")
    label_ko = note.get("label_ko") or str(series or "-")
    if direction == "greed":
        return f"{label_ko}: {note['greed_meaning']}"
    if direction == "fear":
        return f"{label_ko}: {note['fear_meaning']}"
    return f"{label_ko}: {note['neutral_meaning']}"

def _join_component_labels(rows: list[dict[str, Any]]) -> str:
    labels = []
    for row in rows:
        note = _cnn_component_note(row.get("series"))
        labels.append(note.get("label_ko") or str(row.get("series") or "-"))
    return ", ".join(labels) if labels else "해당 신호 없음"

def _sentiment_driver_groups(component_rows: list[dict[str, Any]]) -> tuple[dict[str, list[dict[str, Any]]], dict[str, int]]:
    groups: dict[str, list[dict[str, Any]]] = {"greed": [], "fear": [], "neutral": []}
    for row in component_rows:
        bucket = _sentiment_score_bucket(row.get("Score"))
        direction = bucket["direction"]
        note = _cnn_component_note(row.get("Series"))
        groups[direction].append(
            {
                "series": row.get("Series") or "-",
                "label_ko": note["label_ko"],
                "score": row.get("Score"),
                "rating": row.get("Rating") or "-",
                "rating_label_ko": bucket["label_ko"],
                "tone": bucket["tone"],
                "direction": direction,
                "what_it_checks": note["what_it_checks"],
                "current_reading": _cnn_component_current_reading(row.get("Series"), bucket),
            }
        )
    summary = {
        "greed_count": len(groups["greed"]),
        "fear_count": len(groups["fear"]),
        "neutral_count": len(groups["neutral"]),
    }
    return groups, summary

def _sentiment_component_explanations(component_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    explanations: list[dict[str, Any]] = []
    for row in component_rows:
        bucket = _sentiment_score_bucket(row.get("Score"))
        note = _cnn_component_note(row.get("Series"))
        explanations.append(
            {
                "series": row.get("Series") or "-",
                "label_ko": note["label_ko"],
                "score": row.get("Score"),
                "rating": row.get("Rating") or "-",
                "rating_label_ko": bucket["label_ko"],
                "direction": bucket["direction"],
                "tone": bucket["tone"],
                "what_it_checks": note["what_it_checks"],
                "greed_meaning": note["greed_meaning"],
                "fear_meaning": note["fear_meaning"],
                "current_reading": _cnn_component_current_reading(row.get("Series"), bucket),
            }
        )
    return explanations

def _sentiment_history_observations(frame: pd.DataFrame | None, series_ids: Sequence[str]) -> pd.DataFrame:
    columns = ["series_id", "observation_date", "value", "source"]
    if not isinstance(frame, pd.DataFrame) or frame.empty or "series_id" not in frame:
        return pd.DataFrame(columns=columns)
    rows = frame.copy()
    rows["series_id"] = rows["series_id"].astype(str).str.upper()
    rows = rows[rows["series_id"].isin({str(series_id).upper() for series_id in series_ids})].copy()
    if rows.empty:
        return pd.DataFrame(columns=columns)
    rows["observation_date"] = pd.to_datetime(rows.get("observation_date"), errors="coerce")
    rows["value"] = pd.to_numeric(rows.get("value"), errors="coerce")
    rows["source"] = rows.get("source", pd.Series(dtype=str))
    return rows.dropna(subset=["observation_date", "value"]).sort_values(["series_id", "observation_date"])

def _round_metric(value: float | None) -> float | None:
    return None if value is None else round(float(value), 2)

def _recent_range_position_label(percentile: float | None) -> str:
    if percentile is None:
        return "자료 부족"
    if percentile <= 25:
        return "낮은 편"
    if percentile >= 75:
        return "높은 편"
    return "중간권"

def _build_sentiment_range_context(
    history_frame: pd.DataFrame | None,
    coverage: dict[str, Any],
) -> list[dict[str, Any]]:
    current_values = {
        "CNN_FEAR_GREED": _safe_float(coverage.get("cnn_score")),
        "AAII_BEARISH": _safe_float(coverage.get("aaii_bearish")),
        "AAII_BULL_BEAR_SPREAD": _safe_float(coverage.get("aaii_bull_bear_spread")),
    }
    history = _sentiment_history_observations(history_frame, tuple(current_values))
    rows: list[dict[str, Any]] = []
    for series_id, current_value in current_values.items():
        label = SENTIMENT_SERIES_LABELS.get(series_id, series_id)
        series_history = history[history["series_id"] == series_id]
        values = list(series_history["value"].dropna())
        latest_value = current_value if current_value is not None else (float(values[-1]) if values else None)
        sample_count = len(values)
        percentile = None
        min_value = max_value = median_value = None
        if sample_count and latest_value is not None:
            percentile = round((sum(1 for value in values if value <= latest_value) / sample_count) * 100, 1)
            min_value = round(float(min(values)), 2)
            max_value = round(float(max(values)), 2)
            median_value = round(float(pd.Series(values).median()), 2)
        position_label = _recent_range_position_label(percentile)
        if sample_count and latest_value is not None:
            detail = (
                f"최근 {sample_count}개 관측 기준 {position_label}입니다. "
                f"범위 {min_value:g}~{max_value:g}, 중앙값 {median_value:g}, 현재 {latest_value:g}."
            )
        else:
            detail = "최근 범위를 계산할 history가 부족합니다."
        rows.append(
            {
                "series_id": series_id,
                "series": label,
                "latest_value": _round_metric(latest_value),
                "sample_count": sample_count,
                "min_value": min_value,
                "max_value": max_value,
                "median_value": median_value,
                "percentile": percentile,
                "position_label": position_label,
                "tone": "neutral" if percentile is None or 25 < percentile < 75 else "warning",
                "detail": detail,
            }
        )
    return rows

def _aaii_direction(*, bearish: float | None, spread: float | None) -> str:
    if bearish is None:
        return "neutral"
    if bearish >= 35 or (spread is not None and spread < 0):
        return "fear"
    if bearish <= 25 and spread is not None and spread > 10:
        return "greed"
    return "neutral"

def _component_balance_direction(driver_summary: dict[str, int]) -> str:
    greed_count = int(driver_summary.get("greed_count") or 0)
    fear_count = int(driver_summary.get("fear_count") or 0)
    if greed_count and fear_count:
        return "mixed"
    if greed_count > fear_count:
        return "greed"
    if fear_count > greed_count:
        return "fear"
    return "neutral"

def _direction_label(direction: str) -> str:
    return {
        "greed": "탐욕",
        "fear": "공포",
        "neutral": "중립",
        "mixed": "혼합",
    }.get(direction, "중립")


def _direction_tone(direction: str) -> str:
    if direction == "greed":
        return "positive"
    if direction in {"fear", "mixed"}:
        return "warning"
    return "neutral"


def _format_divergence_value(value: float | None, suffix: str = "") -> str:
    if value is None:
        return "-"
    return f"{value:.1f}{suffix}"


def _headline_divergence_detail(direction: str, label: str) -> str:
    if direction == "greed":
        return f"CNN headline은 {label} 쪽입니다. headline만 보면 위험선호가 우세합니다."
    if direction == "fear":
        return f"CNN headline은 {label} 쪽입니다. headline만 보면 방어적 심리가 우세합니다."
    return f"CNN headline은 {label}입니다. 공포나 탐욕 어느 쪽도 강하게 밀지 않습니다."


def _component_divergence_detail(direction: str, driver_summary: dict[str, int]) -> str:
    greed_count = int(driver_summary.get("greed_count") or 0)
    fear_count = int(driver_summary.get("fear_count") or 0)
    neutral_count = int(driver_summary.get("neutral_count") or 0)
    if direction == "mixed":
        neutral_tail = f" 중립 {neutral_count}개도 있어" if neutral_count else ""
        return (
            f"CNN 구성요소는 탐욕 {greed_count}개와 공포 {fear_count}개가 함께 나와"
            f"{neutral_tail} 내부가 갈라져 있습니다. headline을 한 방향으로 단정하기 어렵게 만드는 부분입니다."
        )
    if direction == "greed":
        return f"CNN 구성요소는 탐욕 {greed_count}개가 우세해 위험선호 쪽 압력이 더 많이 보입니다."
    if direction == "fear":
        return f"CNN 구성요소는 공포 {fear_count}개가 우세해 방어적 심리 쪽 압력이 더 많이 보입니다."
    return f"CNN 구성요소는 중립 {neutral_count}개 중심이라 내부 쏠림이 강하지 않습니다."


def _aaii_divergence_detail(direction: str, *, bearish: float | None, spread: float | None) -> str:
    bearish_text = _format_divergence_value(bearish, "%")
    spread_text = _format_divergence_value(spread, "pp")
    if direction == "fear":
        return (
            f"AAII는 bearish {bearish_text}, bull-bear spread {spread_text} 기준으로 비관 쪽입니다. "
            "설문 심리는 headline보다 방어적으로 읽힙니다."
        )
    if direction == "greed":
        return (
            f"AAII는 bearish {bearish_text}, bull-bear spread {spread_text} 기준으로 낙관 쪽입니다. "
            "설문 심리는 위험선호가 우세합니다."
        )
    return (
        f"AAII는 bearish {bearish_text}, bull-bear spread {spread_text} 기준으로 중립권입니다. "
        "설문 심리만으로 한 방향을 단정하기 어렵습니다."
    )

def _build_sentiment_divergence(
    *,
    cnn_bucket: dict[str, str],
    aaii_bearish: float | None,
    aaii_spread: float | None,
    driver_summary: dict[str, int],
) -> dict[str, Any]:
    headline_direction = cnn_bucket.get("direction") or "neutral"
    component_direction = _component_balance_direction(driver_summary)
    aaii_direction = _aaii_direction(bearish=aaii_bearish, spread=aaii_spread)
    directions = {headline_direction, component_direction, aaii_direction}
    headline_label = cnn_bucket.get("label_ko") or _direction_label(headline_direction)
    component_label = (
        f"탐욕 {int(driver_summary.get('greed_count') or 0)} / "
        f"공포 {int(driver_summary.get('fear_count') or 0)} / "
        f"중립 {int(driver_summary.get('neutral_count') or 0)}"
    )
    if component_direction == "mixed" or len(directions) >= 3:
        status = "뚜렷한 엇갈림"
        tone = "warning"
        summary = "CNN headline, CNN 구성요소, AAII 설문이 서로 다르게 말합니다. 한 방향으로 단정하기보다 어떤 축이 갈라지는지 보는 구간입니다."
    elif len(directions) == 2:
        status = "부분 엇갈림"
        tone = "neutral"
        summary = "주요 심리 축 일부가 다른 방향을 가리킵니다. headline만 단독으로 읽지 않는 편이 안전합니다."
    else:
        status = "대체로 같은 방향"
        tone = "positive" if headline_direction == "greed" else "warning" if headline_direction == "fear" else "neutral"
        summary = "CNN headline, 구성요소, AAII 설문이 대체로 같은 방향입니다. 그래도 이 화면은 시장 배경 확인용입니다."
    return {
        "status": status,
        "tone": tone,
        "headline_direction": headline_direction,
        "component_direction": component_direction,
        "aaii_direction": aaii_direction,
        "summary": summary,
        "items": [
            {
                "label": "CNN headline",
                "direction": headline_direction,
                "status": headline_label,
                "direction_label": headline_label,
                "tone": _direction_tone(headline_direction),
                "detail": _headline_divergence_detail(headline_direction, headline_label),
            },
            {
                "label": "CNN components",
                "direction": component_direction,
                "status": component_label,
                "direction_label": component_label,
                "tone": _direction_tone(component_direction),
                "detail": _component_divergence_detail(component_direction, driver_summary),
            },
            {
                "label": "AAII survey",
                "direction": aaii_direction,
                "status": _direction_label(aaii_direction),
                "direction_label": _direction_label(aaii_direction),
                "tone": _direction_tone(aaii_direction),
                "detail": _aaii_divergence_detail(aaii_direction, bearish=aaii_bearish, spread=aaii_spread),
            },
        ],
    }

def _build_component_history_context(
    history_frame: pd.DataFrame | None,
    component_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    history = _sentiment_history_observations(history_frame, CNN_COMPONENT_SERIES)
    rows: list[dict[str, Any]] = []
    for row in component_rows:
        series = str(row.get("Series") or "")
        series_id = SENTIMENT_SERIES_IDS_BY_LABEL.get(series, series)
        note = _cnn_component_note(series)
        series_history = history[history["series_id"] == series_id].sort_values("observation_date")
        latest = _safe_float(row.get("Score"))
        latest_date = str(row.get("Observation Date") or "-")
        previous = None
        previous_date = "-"
        if len(series_history) >= 2:
            latest_history = series_history.iloc[-1]
            previous_history = series_history.iloc[-2]
            latest = _safe_float(latest_history.get("value")) if latest is None else latest
            latest_date = _iso_date(latest_history.get("observation_date")) or latest_date
            previous = _safe_float(previous_history.get("value"))
            previous_date = _iso_date(previous_history.get("observation_date")) or "-"
        elif len(series_history) == 1 and latest is None:
            latest_history = series_history.iloc[-1]
            latest = _safe_float(latest_history.get("value"))
            latest_date = _iso_date(latest_history.get("observation_date")) or latest_date
        change = None if latest is None or previous is None else round(latest - previous, 2)
        if change is None:
            change_direction = "flat"
            detail = "이전 관측값이 부족해 변화폭을 계산하지 못했습니다."
        elif change > 0:
            change_direction = "up"
            detail = f"이전 관측 대비 +{change:g}p 높아졌습니다."
        elif change < 0:
            change_direction = "down"
            detail = f"이전 관측 대비 {change:g}p 낮아졌습니다."
        else:
            change_direction = "flat"
            detail = "이전 관측과 같은 수준입니다."
        rows.append(
            {
                "series": series,
                "series_id": series_id,
                "label_ko": note.get("label_ko") or series,
                "latest": _round_metric(latest),
                "latest_date": latest_date,
                "previous": _round_metric(previous),
                "previous_date": previous_date,
                "change": change,
                "change_direction": change_direction,
                "tone": "positive" if change_direction == "up" else "warning" if change_direction == "down" else "neutral",
                "detail": detail,
            }
        )
    return rows

def _aaii_pessimism_status(*, bearish: float | None, spread: float | None) -> dict[str, str]:
    if bearish is None:
        return {
            "status": "데이터 없음",
            "tone": "warning",
            "detail": "AAII bearish sentiment가 아직 없습니다.",
        }
    bearish_gap = bearish - AAII_HISTORICAL_AVERAGES["bearish"]
    spread_text = "-" if spread is None else f"{spread:+.1f}pp"
    if bearish >= 50 or (spread is not None and spread <= -20):
        status = "비관 강함"
        tone = "danger"
    elif bearish >= 35 or (spread is not None and spread < 0):
        status = "비관 우위"
        tone = "warning"
    elif bearish <= 25 and spread is not None and spread > 10:
        status = "낙관 우위"
        tone = "positive"
    else:
        status = "균형"
        tone = "neutral"
    return {
        "status": status,
        "tone": tone,
        "detail": f"Bearish {bearish:.1f}%는 장기 평균보다 {bearish_gap:+.1f}pp 높고, bull-bear spread는 {spread_text}입니다.",
    }

def _market_sentiment_phase(
    *,
    cnn_score: float | None,
    aaii_bearish: float | None,
    aaii_spread: float | None,
    driver_summary: dict[str, int],
    missing_count: int,
    stale_count: int,
) -> dict[str, str]:
    if missing_count or cnn_score is None or aaii_bearish is None:
        return {
            "phase": "DATA_REVIEW",
            "phase_label": "데이터 확인",
            "tone": "warning",
            "headline": "시장 심리 해석에 필요한 핵심 데이터가 부족합니다.",
            "summary": "CNN Fear & Greed와 AAII bearish sentiment를 갱신한 뒤 다시 확인하세요.",
        }
    if stale_count:
        return {
            "phase": "STALE_REVIEW",
            "phase_label": "신선도 확인",
            "tone": "warning",
            "headline": "저장된 시장 심리 데이터가 오래됐습니다.",
            "summary": "해석은 가능하지만 최신 시장 상태로 보기 전에 수집을 갱신하는 편이 안전합니다.",
        }

    greed_count = int(driver_summary.get("greed_count") or 0)
    fear_count = int(driver_summary.get("fear_count") or 0)
    split_drivers = greed_count > 0 and fear_count > 0
    if cnn_score < 25 and aaii_bearish >= 45:
        return {
            "phase": "FEAR_STRESS",
            "phase_label": "공포 압력",
            "tone": "danger",
            "headline": "공포 심리가 강하게 우세합니다.",
            "summary": "CNN score와 AAII bearish가 동시에 방어적입니다. 가격 반등보다 위험 관리 확인이 먼저입니다.",
        }
    if cnn_score >= 75 and aaii_spread is not None and aaii_spread >= 10:
        return {
            "phase": "EUPHORIA_RISK",
            "phase_label": "탐욕 과열",
            "tone": "warning",
            "headline": "탐욕 심리가 과열권에 가깝습니다.",
            "summary": "강한 위험 선호가 보이지만 과열과 crowding 가능성을 함께 확인해야 합니다.",
        }
    if (45 <= cnn_score < 55 and (split_drivers or (aaii_spread is not None and aaii_spread <= 0))) or (
        cnn_score < 60 and split_drivers and aaii_spread is not None and aaii_spread <= 0
    ):
        return {
            "phase": "MIXED_NEUTRAL",
            "phase_label": "혼합 중립",
            "tone": "neutral",
            "headline": "중립이지만 내부는 엇갈린 시장 심리입니다.",
            "summary": "헤드라인 점수는 중립권이지만 일부 CNN 구성요소는 탐욕, 일부는 공포를 가리킵니다. AAII도 약한 비관 쪽입니다.",
        }
    if cnn_score >= 55:
        return {
            "phase": "GREED_LEANING",
            "phase_label": "탐욕 우위",
            "tone": "positive",
            "headline": "탐욕 심리가 우위입니다.",
            "summary": "위험 선호가 우세하지만 AAII와 breadth가 같은 방향인지 확인해야 합니다.",
        }
    return {
        "phase": "FEAR_LEANING",
        "phase_label": "공포 우위",
        "tone": "warning",
        "headline": "공포 심리가 우위입니다.",
        "summary": "방어적 심리가 우세합니다. 반등 신호보다 breadth와 credit confirmation을 먼저 확인하세요.",
    }

def _build_market_sentiment_analysis(
    *,
    coverage: dict[str, Any],
    component_rows: list[dict[str, Any]],
    history_rows: pd.DataFrame | None = None,
) -> dict[str, Any]:
    cnn_score = _safe_float(coverage.get("cnn_score"))
    aaii_bearish = _safe_float(coverage.get("aaii_bearish"))
    aaii_spread = _safe_float(coverage.get("aaii_bull_bear_spread"))
    missing_count = int(coverage.get("missing_count") or 0)
    stale_count = int(coverage.get("stale_count") or 0)
    driver_groups, driver_summary = _sentiment_driver_groups(component_rows)
    phase = _market_sentiment_phase(
        cnn_score=cnn_score,
        aaii_bearish=aaii_bearish,
        aaii_spread=aaii_spread,
        driver_summary=driver_summary,
        missing_count=missing_count,
        stale_count=stale_count,
    )
    cnn_bucket = _sentiment_score_bucket(cnn_score)
    aaii_status = _aaii_pessimism_status(bearish=aaii_bearish, spread=aaii_spread)
    divergence = _build_sentiment_divergence(
        cnn_bucket=cnn_bucket,
        aaii_bearish=aaii_bearish,
        aaii_spread=aaii_spread,
        driver_summary=driver_summary,
    )
    data_confidence = {
        "status": "High" if missing_count == 0 and stale_count == 0 else "Review",
        "tone": "positive" if missing_count == 0 and stale_count == 0 else "warning",
        "detail": f"{coverage.get('source_count') or 0}개 source 준비, missing {missing_count}, stale {stale_count}.",
    }
    greed_rows = driver_groups["greed"]
    fear_rows = driver_groups["fear"]
    neutral_rows = driver_groups["neutral"]
    greed_labels = _join_component_labels(greed_rows)
    fear_labels = _join_component_labels(fear_rows)
    neutral_clause = "" if not neutral_rows else f" 중립 신호는 {_join_component_labels(neutral_rows)}입니다."
    cnn_score_text = "-" if cnn_score is None else f"{cnn_score:.1f}"
    aaii_spread_text = "-" if aaii_spread is None else f"{aaii_spread:+.1f}pp"
    analysis_steps = [
        {
            "title": "지금 결론",
            "status": phase["phase_label"],
            "tone": phase["tone"],
            "detail": f"{phase['headline']} {phase['summary']}",
        },
        {
            "title": "왜 이렇게 보나",
            "status": f"CNN {cnn_score_text} · AAII spread {aaii_spread_text}",
            "tone": cnn_bucket["tone"],
            "detail": f"CNN 헤드라인은 {cnn_bucket['label_ko']}권이고, {aaii_status['detail']} 그래서 겉으로는 중립에 가깝지만 설문은 약한 비관을 보탭니다.",
        },
        {
            "title": "강한 신호",
            "status": f"{driver_summary['greed_count']}개 탐욕 쪽",
            "tone": "positive" if greed_rows else "neutral",
            "detail": f"{greed_labels} 신호는 위험선호를 가리킵니다.",
        },
        {
            "title": "약한 신호",
            "status": f"{driver_summary['fear_count']}개 공포 쪽",
            "tone": "warning" if fear_rows else "neutral",
            "detail": f"{fear_labels}는 시장 참여 폭, 상승 리더십, 신용시장 중 일부가 약하다는 신호입니다.{neutral_clause}",
        },
        {
            "title": "그래서 어떻게 보나",
            "status": phase["phase_label"],
            "tone": phase["tone"],
            "detail": "지수는 버티지만 내부 체력은 확인이 필요한 상태입니다. 강한 상승장 확신보다는 혼합 중립으로 두고 breadth, credit, macro 확인을 붙입니다.",
        },
        {
            "title": "다음 확인",
            "status": "확인 필요",
            "tone": "neutral",
            "detail": "Market Movers breadth, Futures Macro Thermometer, Events calendar가 같은 방향인지 보면 이 중립이 건강한 중립인지, 취약한 중립인지 갈라집니다.",
        },
    ]
    return {
        **phase,
        "data_confidence": data_confidence,
        "driver_summary": driver_summary,
        "driver_groups": driver_groups,
        "component_explanations": _sentiment_component_explanations(component_rows),
        "range_context": _build_sentiment_range_context(history_rows, coverage),
        "divergence": divergence,
        "component_history": _build_component_history_context(history_rows, component_rows),
        "analysis_steps": analysis_steps,
        "next_checks": [
            {
                "target": "Market Movers breadth",
                "reason": "상승 종목 비중이 넓으면 건강한 중립, 좁으면 일부 대형주 중심 중립일 수 있습니다.",
                "watch_for": "상승 종목 수, sector breadth, Stock Price Breadth와 같은 방향인지 확인",
                "tone": "neutral",
            },
            {
                "target": "Futures Macro Thermometer",
                "reason": "주식 심리와 금리/달러/원자재 압력이 충돌하면 headline 중립을 그대로 믿기 어렵습니다.",
                "watch_for": "risk-on, rate pressure, dollar pressure가 sentiment와 같은 방향인지 확인",
                "tone": "neutral",
            },
            {
                "target": "Events calendar",
                "reason": "FOMC, CPI, earnings 같은 이벤트가 심리 급변의 원인인지 확인합니다.",
                "watch_for": "다가오는 고중요 이벤트와 stale estimate 여부",
                "tone": "neutral",
            },
        ],
    }

def build_market_sentiment_snapshot(
    *,
    snapshot_rows: pd.DataFrame | None = None,
    history_rows: pd.DataFrame | None = None,
    today: date | None = None,
    max_history_days: int = 180,
) -> dict[str, Any]:
    """Build the Overview sentiment read model from stored CNN / AAII observations."""
    today_value = today or date.today()
    start_date = (pd.Timestamp(today_value) - pd.Timedelta(days=max_history_days)).strftime("%Y-%m-%d")
    end_date = pd.Timestamp(today_value).strftime("%Y-%m-%d")
    try:
        snapshot_frame = (
            snapshot_rows.copy()
            if isinstance(snapshot_rows, pd.DataFrame)
            else load_market_sentiment_snapshot(as_of_date=end_date, max_staleness_days=14)
        )
        history_frame = (
            history_rows.copy()
            if isinstance(history_rows, pd.DataFrame)
            else load_market_sentiment_history(
                series_ids=("CNN_FEAR_GREED", "AAII_BEARISH", "AAII_BULL_BEAR_SPREAD", *CNN_COMPONENT_SERIES),
                start=start_date,
                end=end_date,
            )
        )
    except Exception as exc:
        return _empty_sentiment_snapshot(status="ERROR", message=f"Market sentiment snapshot failed: {exc}")

    if snapshot_frame.empty:
        return _empty_sentiment_snapshot(
            status="MISSING",
            message="Stored CNN Fear & Greed / AAII sentiment rows are not available. Run Market Sentiment refresh.",
        )

    for frame in (snapshot_frame, history_frame):
        for column in ("observation_date", "collected_at"):
            if column in frame:
                frame[column] = pd.to_datetime(frame[column], errors="coerce")
        if "value" in frame:
            frame["value"] = pd.to_numeric(frame["value"], errors="coerce")

    ordered_core = ["CNN_FEAR_GREED", "AAII_BEARISH", "AAII_BULL_BEAR_SPREAD", "AAII_BULLISH", "AAII_NEUTRAL"]
    table_rows: list[dict[str, Any]] = []
    missing_core = 0
    stale_count = 0
    for series_id in ordered_core:
        row = _latest_sentiment_row(snapshot_frame, series_id)
        if row is None:
            if series_id in {"CNN_FEAR_GREED", "AAII_BEARISH"}:
                missing_core += 1
            continue
        status = _sentiment_status(row)
        if status != "OK":
            stale_count += 1
        table_rows.append(_sentiment_table_row(row, label=SENTIMENT_SERIES_LABELS.get(series_id, series_id)))

    component_rows: list[dict[str, Any]] = []
    for series_id in CNN_COMPONENT_SERIES:
        row = _latest_sentiment_row(snapshot_frame, series_id)
        if row is None:
            continue
        metadata = _metadata_from_row(row)
        component_rows.append(
            {
                "Series": SENTIMENT_SERIES_LABELS.get(series_id, series_id),
                "Score": round(float(row.get("value")), 1) if _safe_float(row.get("value")) is not None else None,
                "Rating": metadata.get("rating") or "-",
                "Observation Date": _iso_date(row.get("observation_date")) or "-",
                "Status": _sentiment_status(row),
            }
        )

    history_out = pd.DataFrame(columns=SENTIMENT_HISTORY_COLUMNS)
    if isinstance(history_frame, pd.DataFrame) and not history_frame.empty:
        visible_history = history_frame[
            history_frame.get("series_id", pd.Series(dtype=str)).astype(str).str.upper().isin(
                {"CNN_FEAR_GREED", "AAII_BEARISH", "AAII_BULL_BEAR_SPREAD"}
            )
        ].copy()
        if not visible_history.empty:
            visible_history["Date"] = visible_history["observation_date"].map(_iso_date)
            visible_history["Series"] = visible_history["series_id"].map(
                lambda value: SENTIMENT_SERIES_LABELS.get(str(value).upper(), str(value))
            )
            visible_history["Value"] = visible_history["value"].map(lambda value: round(float(value), 2) if _safe_float(value) is not None else None)
            visible_history["Source"] = visible_history.get("source", pd.Series(dtype=str))
            history_out = visible_history[SENTIMENT_HISTORY_COLUMNS].dropna(subset=["Date"]).sort_values(["Date", "Series"])

    cnn_row = _latest_sentiment_row(snapshot_frame, "CNN_FEAR_GREED")
    cnn_meta = _metadata_from_row(cnn_row) if cnn_row is not None else {}
    aaii_bearish_row = _latest_sentiment_row(snapshot_frame, "AAII_BEARISH")
    aaii_spread_row = _latest_sentiment_row(snapshot_frame, "AAII_BULL_BEAR_SPREAD")
    warnings: list[str] = []
    if missing_core:
        warnings.append("CNN Fear & Greed or AAII bearish sentiment is missing from stored observations.")
    if stale_count:
        warnings.append("One or more sentiment observations are stale or partial.")
    status = "OK" if missing_core == 0 and stale_count == 0 else "REVIEW" if table_rows else "MISSING"
    coverage = {
        "cnn_score": _safe_float(cnn_row.get("value")) if cnn_row is not None else None,
        "cnn_rating": cnn_meta.get("rating") if cnn_row is not None else None,
        "aaii_bearish": _safe_float(aaii_bearish_row.get("value")) if aaii_bearish_row is not None else None,
        "aaii_bull_bear_spread": _safe_float(aaii_spread_row.get("value")) if aaii_spread_row is not None else None,
        "source_count": len({str(row.get("Source") or "") for row in table_rows if row.get("Source")}),
        "stale_count": stale_count,
        "missing_count": missing_core,
    }
    return {
        "status": status,
        "rows": pd.DataFrame(table_rows, columns=SENTIMENT_COLUMNS),
        "component_rows": pd.DataFrame(component_rows, columns=SENTIMENT_COMPONENT_COLUMNS),
        "history_rows": history_out,
        "coverage": coverage,
        "analysis": _build_market_sentiment_analysis(
            coverage=coverage,
            component_rows=component_rows,
            history_rows=history_frame,
        ),
        "warnings": warnings,
    }

__all__ = ["build_market_sentiment_snapshot"]
