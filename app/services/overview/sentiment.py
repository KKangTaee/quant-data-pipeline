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
    "State",
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

def _aaii_direction(*, spread: float | None, bearish: float | None = None) -> str:
    """Classify AAII survey direction from the bull-bear spread alone."""
    del bearish  # Compatibility for existing callers; the spread owns direction in v2.
    if spread is None:
        return "unavailable"
    if spread >= 10:
        return "optimistic"
    if spread <= -10:
        return "pessimistic"
    return "neutral"


def _aaii_direction_label(direction: str) -> str:
    return {
        "optimistic": "낙관",
        "pessimistic": "비관",
        "neutral": "중립",
        "unavailable": "판정 보류",
    }.get(direction, "판정 보류")


def _sentiment_history_state_label(series_id: Any, value: Any) -> str:
    """Attach server-owned interpretation to historical headline and spread rows."""
    normalized = str(series_id or "").upper()
    numeric = _safe_float(value)
    if normalized == "CNN_FEAR_GREED":
        return _sentiment_score_bucket(numeric)["label_ko"] if numeric is not None else "판정 보류"
    if normalized == "AAII_BULL_BEAR_SPREAD":
        return _aaii_direction_label(_aaii_direction(spread=numeric))
    return ""


def _aaii_direction_tone(direction: str) -> str:
    if direction == "optimistic":
        return "positive"
    if direction in {"pessimistic", "unavailable"}:
        return "warning"
    return "neutral"


def _series_latest_previous(
    history_frame: pd.DataFrame | None,
    series_id: str,
    *,
    current: float | None,
) -> dict[str, Any]:
    history = _sentiment_history_observations(history_frame, (series_id,))
    history = history[history["series_id"] == series_id].sort_values("observation_date")
    latest = current
    latest_date = None
    previous = None
    previous_date = None
    if not history.empty:
        latest_row = history.iloc[-1]
        if latest is None:
            latest = _safe_float(latest_row.get("value"))
        latest_date = _iso_date(latest_row.get("observation_date"))
        if len(history) >= 2:
            previous_row = history.iloc[-2]
            previous = _safe_float(previous_row.get("value"))
            previous_date = _iso_date(previous_row.get("observation_date"))
    change = None if latest is None or previous is None else round(latest - previous, 2)
    return {
        "latest": _round_metric(latest),
        "latest_date": latest_date,
        "previous": _round_metric(previous),
        "previous_date": previous_date,
        "change": change,
    }


def _range_context_item(
    history_frame: pd.DataFrame | None,
    coverage: dict[str, Any],
    series_id: str,
) -> dict[str, Any]:
    for item in _build_sentiment_range_context(history_frame, coverage):
        if item.get("series_id") == series_id:
            return item
    return {
        "series_id": series_id,
        "series": SENTIMENT_SERIES_LABELS.get(series_id, series_id),
        "latest_value": None,
        "sample_count": 0,
        "percentile": None,
        "position_label": "자료 부족",
        "tone": "neutral",
        "detail": "최근 범위를 계산할 history가 부족합니다.",
    }


def _build_cnn_axis(
    *,
    coverage: dict[str, Any],
    component_rows: list[dict[str, Any]],
    history_rows: pd.DataFrame | None,
) -> dict[str, Any]:
    current = _safe_float(coverage.get("cnn_score"))
    bucket = _sentiment_score_bucket(current)
    _, driver_summary = _sentiment_driver_groups(component_rows)
    component_direction = _component_balance_direction(driver_summary)
    history = _series_latest_previous(history_rows, "CNN_FEAR_GREED", current=current)
    if not component_rows:
        components_support = "CNN 구성요소 이력이 부족해 headline 내부 확신도를 계산하지 못했습니다."
    elif component_direction == "mixed":
        components_support = "CNN 구성요소가 공포와 탐욕으로 갈려 headline 내부 확신도는 낮습니다."
    elif component_direction == bucket["direction"]:
        components_support = "CNN 구성요소가 headline과 같은 방향을 가리킵니다."
    else:
        components_support = "CNN 구성요소의 중심 방향이 headline과 달라 추가 확인이 필요합니다."
    return {
        "label": "시장 행동",
        "source": "CNN Fear & Greed",
        "available": current is not None,
        "direction": bucket["direction"] if current is not None else "unavailable",
        "direction_label": bucket["label_ko"] if current is not None else "판정 보류",
        "tone": bucket["tone"],
        "current": _round_metric(current),
        "previous": history["previous"],
        "change": history["change"],
        "latest_date": history["latest_date"],
        "previous_date": history["previous_date"],
        "range": _range_context_item(history_rows, coverage, "CNN_FEAR_GREED"),
        "component_balance": {**driver_summary, "direction": component_direction},
        "components_support": components_support,
        "detail": (
            "가격·변동성·시장폭·옵션·신용·안전자산 수요를 합친 시장 행동 심리입니다."
            if current is not None
            else "CNN Fear & Greed 관측값이 없습니다."
        ),
    }


def _build_aaii_axis(
    *,
    coverage: dict[str, Any],
    history_rows: pd.DataFrame | None,
) -> dict[str, Any]:
    bullish = _safe_float(coverage.get("aaii_bullish"))
    neutral = _safe_float(coverage.get("aaii_neutral"))
    bearish = _safe_float(coverage.get("aaii_bearish"))
    spread = _safe_float(coverage.get("aaii_bull_bear_spread"))
    direction = _aaii_direction(spread=spread)
    history = _series_latest_previous(history_rows, "AAII_BULL_BEAR_SPREAD", current=spread)
    comparisons: dict[str, dict[str, float | None]] = {}
    for key, value in (("bullish", bullish), ("neutral", neutral), ("bearish", bearish)):
        average = AAII_HISTORICAL_AVERAGES[key]
        comparisons[key] = {
            "current": _round_metric(value),
            "historical_average": average,
            "difference_pp": None if value is None else round(value - average, 1),
        }
    spread_text = "-" if spread is None else f"{spread:+.1f}pp"
    return {
        "label": "개인투자자 설문",
        "source": "AAII Sentiment Survey",
        "available": spread is not None,
        "direction": direction,
        "direction_label": _aaii_direction_label(direction),
        "tone": _aaii_direction_tone(direction),
        "current": _round_metric(spread),
        "previous": history["previous"],
        "change": history["change"],
        "latest_date": history["latest_date"],
        "previous_date": history["previous_date"],
        "spread": _round_metric(spread),
        "responses": {
            "bullish": _round_metric(bullish),
            "neutral": _round_metric(neutral),
            "bearish": _round_metric(bearish),
        },
        "long_term_comparison": comparisons,
        "range": _range_context_item(history_rows, coverage, "AAII_BULL_BEAR_SPREAD"),
        "detail": (
            f"Bull-Bear Spread {spread_text} 기준으로 {_aaii_direction_label(direction)} 우위입니다."
            if spread is not None
            else "Bull-Bear Spread가 없어 설문 방향 판정을 보류합니다."
        ),
    }


def _build_sentiment_axes(
    *,
    coverage: dict[str, Any],
    component_rows: list[dict[str, Any]],
    history_rows: pd.DataFrame | None,
) -> dict[str, dict[str, Any]]:
    """Build independent market-behavior and investor-survey axes."""
    return {
        "market_behavior": _build_cnn_axis(
            coverage=coverage,
            component_rows=component_rows,
            history_rows=history_rows,
        ),
        "investor_survey": _build_aaii_axis(coverage=coverage, history_rows=history_rows),
    }


def _build_sentiment_cross_read(
    *,
    market_behavior: dict[str, Any],
    investor_survey: dict[str, Any],
) -> dict[str, Any]:
    """Explain agreement without collapsing the two sentiment axes into one score."""
    cnn_direction = str(market_behavior.get("direction") or "unavailable")
    aaii_direction = str(investor_survey.get("direction") or "unavailable")
    cnn_label = str(market_behavior.get("direction_label") or "판정 보류")
    aaii_label = str(investor_survey.get("direction_label") or "판정 보류")
    phase_label = f"행동 {cnn_label} · 설문 {aaii_label}"
    confidence_note = str(market_behavior.get("components_support") or "")

    if not market_behavior.get("available") or not investor_survey.get("available"):
        return {
            "phase": "PARTIAL_DATA",
            "phase_label": phase_label,
            "status": "한 축만 확인 가능",
            "tone": "warning",
            "headline": "CNN과 AAII 중 한 축만 확인할 수 있습니다.",
            "meaning": "두 source가 모두 준비되기 전에는 일치·엇갈림을 판정하지 않습니다.",
            "summary": "두 source가 모두 준비되기 전에는 일치·엇갈림을 판정하지 않습니다.",
            "confidence_note": confidence_note,
            "market_direction": cnn_direction,
            "survey_direction": aaii_direction,
        }

    risk_on_pair = cnn_direction == "greed" and aaii_direction == "optimistic"
    defensive_pair = cnn_direction == "fear" and aaii_direction == "pessimistic"
    opposite_pair = (cnn_direction, aaii_direction) in {
        ("greed", "pessimistic"),
        ("fear", "optimistic"),
    }
    neutral_pair = cnn_direction == "neutral" and aaii_direction == "neutral"
    if risk_on_pair:
        phase, status, tone = "ALIGNED_RISK_ON", "심리 일치 · 위험선호", "positive"
        headline = "시장 행동과 개인투자자 설문이 모두 낙관 쪽입니다."
        meaning = "가격 행동과 설문 인식이 함께 위험선호를 가리킵니다. 과열 여부는 별도로 확인해야 합니다."
    elif defensive_pair:
        phase, status, tone = "ALIGNED_DEFENSIVE", "심리 일치 · 방어 우위", "warning"
        headline = "시장 행동과 개인투자자 설문이 모두 방어 쪽입니다."
        meaning = "가격 행동과 설문 인식이 함께 공포·비관을 가리킵니다. 반전으로 단정하지 않습니다."
    elif opposite_pair:
        phase, status, tone = "DIVERGENT", "뚜렷한 엇갈림", "warning"
        headline = f"시장 행동은 {cnn_label}, 개인투자자 설문은 {aaii_label} — 심리가 엇갈립니다."
        meaning = "가격과 거래에서 드러난 행동과 설문으로 표현한 인식이 반대 방향입니다. 한 축만으로 시장 심리를 단정하지 않습니다."
    elif neutral_pair:
        phase, status, tone = "ALIGNED_NEUTRAL", "중립 일치", "neutral"
        headline = "시장 행동과 개인투자자 설문이 모두 중립권입니다."
        meaning = "두 축 모두 방향성이 약합니다. 다음 관측에서 중립권을 벗어나는지 확인합니다."
    else:
        phase, status, tone = "PARTIAL_DIVERGENCE", "부분 엇갈림", "neutral"
        headline = f"시장 행동은 {cnn_label}, 개인투자자 설문은 {aaii_label}입니다."
        meaning = "한 축은 방향성을 보이지만 다른 축은 중립권입니다. 방향이 합쳐지는지 확인합니다."
    return {
        "phase": phase,
        "phase_label": phase_label,
        "status": status,
        "tone": tone,
        "headline": headline,
        "meaning": meaning,
        "summary": meaning,
        "confidence_note": confidence_note,
        "market_direction": cnn_direction,
        "survey_direction": aaii_direction,
    }


def _build_two_axis_divergence_context(
    *,
    axes: dict[str, dict[str, Any]],
    cross_read: dict[str, Any],
) -> dict[str, Any]:
    """Keep the legacy divergence slot without counting CNN components twice."""
    market = axes["market_behavior"]
    survey = axes["investor_survey"]
    return {
        "status": cross_read["status"],
        "tone": cross_read["tone"],
        "headline_direction": market["direction"],
        "component_direction": market["component_balance"]["direction"],
        "aaii_direction": survey["direction"],
        "summary": cross_read["meaning"],
        "items": [
            {
                "label": "CNN market behavior",
                "direction": market["direction"],
                "status": market["direction_label"],
                "direction_label": market["direction_label"],
                "tone": market["tone"],
                "detail": f"CNN Fear & Greed {market['current'] if market['current'] is not None else '-'} · {market['components_support']}",
            },
            {
                "label": "AAII survey",
                "direction": survey["direction"],
                "status": survey["direction_label"],
                "direction_label": survey["direction_label"],
                "tone": survey["tone"],
                "detail": survey["detail"],
            },
        ],
    }


def _build_sentiment_watch_conditions(
    axes: dict[str, dict[str, Any]],
    cross_read: dict[str, Any],
) -> list[dict[str, str]]:
    """Describe the three relationship paths that can change the current cross-read."""
    market = axes["market_behavior"]
    survey = axes["investor_survey"]
    return [
        {
            "key": "confirm",
            "label": "정렬 확인",
            "condition": (
                f"CNN {market['direction_label']}와 AAII {survey['direction_label']}가 "
                "같은 방향으로 모이는지 확인합니다."
            ),
            "basis": "두 source의 다음 유효 관측",
            "tone": "positive",
        },
        {
            "key": "reverse",
            "label": "설문 반전",
            "condition": (
                f"AAII {survey['direction_label']} 우위가 ±10pp 경계를 넘어 "
                "반대 방향으로 전환되는지 확인합니다."
            ),
            "basis": "AAII 주간 Bull-Bear Spread",
            "tone": "warning",
        },
        {
            "key": "persist",
            "label": "관계 지속",
            "condition": f"현재 `{cross_read['status']}` 관계가 다음 CNN·AAII 관측에서도 이어지는지 확인합니다.",
            "basis": "CNN 일간 × AAII 주간",
            "tone": str(cross_read.get("tone") or "neutral"),
        },
    ]


def _build_sentiment_outlook() -> dict[str, Any]:
    """Publish horizon slots without inventing probabilities before PIT validation."""
    status_reason = (
        "장기 이력과 point-in-time 분리 검증을 통과한 estimator가 없어 "
        "확률을 공개하지 않습니다."
    )
    horizons = [
        {
            "key": "1W",
            "label": "1주",
            "period_label": "다음 5거래일",
            "trading_days": 5,
            "status": "UNAVAILABLE",
            "status_label": "통계적 판단 불가",
            "dominant_path": None,
            "probabilities": [],
            "baseline": None,
            "episode_count": 0,
            "validation_evidence": [],
            "status_reason": status_reason,
        },
        {
            "key": "1M",
            "label": "1개월",
            "period_label": "다음 20거래일",
            "trading_days": 20,
            "status": "UNAVAILABLE",
            "status_label": "통계적 판단 불가",
            "dominant_path": None,
            "probabilities": [],
            "baseline": None,
            "episode_count": 0,
            "validation_evidence": [],
            "status_reason": status_reason,
        },
    ]
    return {
        "status": "UNAVAILABLE",
        "summary": "현재는 확률 전망 대신 다음 CNN·AAII 관측 조건을 확인합니다.",
        "horizons": horizons,
    }

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

def _build_market_sentiment_analysis(
    *,
    coverage: dict[str, Any],
    component_rows: list[dict[str, Any]],
    history_rows: pd.DataFrame | None = None,
) -> dict[str, Any]:
    cnn_score = _safe_float(coverage.get("cnn_score"))
    aaii_spread = _safe_float(coverage.get("aaii_bull_bear_spread"))
    missing_count = int(coverage.get("missing_count") or 0)
    stale_count = int(coverage.get("stale_count") or 0)
    driver_groups, driver_summary = _sentiment_driver_groups(component_rows)
    axes = _build_sentiment_axes(
        coverage=coverage,
        component_rows=component_rows,
        history_rows=history_rows,
    )
    cross_read = _build_sentiment_cross_read(
        market_behavior=axes["market_behavior"],
        investor_survey=axes["investor_survey"],
    )
    phase = {
        "phase": cross_read["phase"],
        "phase_label": cross_read["phase_label"],
        "tone": cross_read["tone"],
        "headline": cross_read["headline"],
        "summary": cross_read["meaning"],
    }
    divergence = _build_two_axis_divergence_context(axes=axes, cross_read=cross_read)
    data_confidence = {
        "status": "High" if missing_count == 0 and stale_count == 0 else "Review",
        "tone": "positive" if missing_count == 0 and stale_count == 0 else "warning",
        "detail": f"{coverage.get('source_count') or 0}개 source 준비, missing {missing_count}, stale {stale_count}.",
    }
    cnn_score_text = "-" if cnn_score is None else f"{cnn_score:.1f}"
    aaii_spread_text = "-" if aaii_spread is None else f"{aaii_spread:+.1f}pp"
    watch_conditions = _build_sentiment_watch_conditions(axes, cross_read)
    analysis_steps = [
        {
            "title": "현재 판단",
            "status": cross_read["status"],
            "tone": cross_read["tone"],
            "detail": f"{cross_read['headline']} {cross_read['meaning']}",
        },
        {
            "title": "CNN 시장 행동",
            "status": f"CNN {cnn_score_text} · {axes['market_behavior']['direction_label']}",
            "tone": axes["market_behavior"]["tone"],
            "detail": f"{axes['market_behavior']['detail']} {axes['market_behavior']['components_support']}",
        },
        {
            "title": "AAII 투자자 인식",
            "status": f"Spread {aaii_spread_text} · {axes['investor_survey']['direction_label']}",
            "tone": axes["investor_survey"]["tone"],
            "detail": axes["investor_survey"]["detail"],
        },
        {
            "title": "다음 확인",
            "status": "두 source의 다음 관측",
            "tone": "neutral",
            "detail": " ".join(item["condition"] for item in watch_conditions),
        },
    ]
    return {
        **phase,
        "axes": axes,
        "cross_read": cross_read,
        "watch_conditions": watch_conditions,
        "outlook": _build_sentiment_outlook(),
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
                "target": item["label"],
                "reason": item["condition"],
                "watch_for": item["basis"],
                "tone": item["tone"],
            }
            for item in watch_conditions
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
                series_ids=(
                    "CNN_FEAR_GREED",
                    "AAII_BULLISH",
                    "AAII_NEUTRAL",
                    "AAII_BEARISH",
                    "AAII_BULL_BEAR_SPREAD",
                    *CNN_COMPONENT_SERIES,
                ),
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
    missing_core_labels: list[str] = []
    stale_count = 0
    for series_id in ordered_core:
        row = _latest_sentiment_row(snapshot_frame, series_id)
        if row is None:
            missing_core += 1
            missing_core_labels.append(SENTIMENT_SERIES_LABELS.get(series_id, series_id))
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
                {
                    "CNN_FEAR_GREED",
                    "AAII_BULLISH",
                    "AAII_NEUTRAL",
                    "AAII_BEARISH",
                    "AAII_BULL_BEAR_SPREAD",
                }
            )
        ].copy()
        if not visible_history.empty:
            visible_history["Date"] = visible_history["observation_date"].map(_iso_date)
            visible_history["Series"] = visible_history["series_id"].map(
                lambda value: SENTIMENT_SERIES_LABELS.get(str(value).upper(), str(value))
            )
            visible_history["Value"] = visible_history["value"].map(lambda value: round(float(value), 2) if _safe_float(value) is not None else None)
            visible_history["Source"] = visible_history.get("source", pd.Series(dtype=str))
            visible_history["State"] = visible_history.apply(
                lambda row: _sentiment_history_state_label(row.get("series_id"), row.get("value")),
                axis=1,
            )
            history_out = visible_history[SENTIMENT_HISTORY_COLUMNS].dropna(subset=["Date"]).sort_values(["Date", "Series"])

    cnn_row = _latest_sentiment_row(snapshot_frame, "CNN_FEAR_GREED")
    cnn_meta = _metadata_from_row(cnn_row) if cnn_row is not None else {}
    aaii_bullish_row = _latest_sentiment_row(snapshot_frame, "AAII_BULLISH")
    aaii_neutral_row = _latest_sentiment_row(snapshot_frame, "AAII_NEUTRAL")
    aaii_bearish_row = _latest_sentiment_row(snapshot_frame, "AAII_BEARISH")
    aaii_spread_row = _latest_sentiment_row(snapshot_frame, "AAII_BULL_BEAR_SPREAD")
    warnings: list[str] = []
    if missing_core:
        warnings.append(f"Required sentiment observations are missing: {', '.join(missing_core_labels)}.")
    if stale_count:
        warnings.append("One or more sentiment observations are stale or partial.")
    status = "OK" if missing_core == 0 and stale_count == 0 else "REVIEW" if table_rows else "MISSING"
    coverage = {
        "cnn_score": _safe_float(cnn_row.get("value")) if cnn_row is not None else None,
        "cnn_rating": cnn_meta.get("rating") if cnn_row is not None else None,
        "aaii_bullish": _safe_float(aaii_bullish_row.get("value")) if aaii_bullish_row is not None else None,
        "aaii_neutral": _safe_float(aaii_neutral_row.get("value")) if aaii_neutral_row is not None else None,
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
