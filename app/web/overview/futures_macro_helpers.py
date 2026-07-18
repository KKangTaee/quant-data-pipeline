from __future__ import annotations

from datetime import datetime
from html import escape
from math import isfinite
from typing import Any

import pandas as pd
import streamlit as st

from app.jobs.overview_actions import (
    record_overview_action_result,
    run_overview_futures_daily_ohlcv,
)
from app.services.futures_macro_thermometer import (
    clear_overview_futures_macro_snapshot_cache,
    load_overview_futures_macro_snapshot,
)
from app.services.futures_macro_pattern_validation import (
    clear_futures_macro_pattern_validation_cache,
    load_overview_futures_macro_pattern_outlook,
)
from app.services.futures_macro_validation import (
    build_current_scenario_validation_summary,
    build_futures_macro_validation_snapshot,
    build_interpretation_confidence,
    clear_futures_macro_validation_cache,
)
from app.web.overview.session_helpers import _snapshot_value
from app.web.overview.components.common import _overview_tone_color
from app.web.overview.futures_macro_react_component import (
    futures_macro_react_component_available,
    render_futures_macro_react_workbench,
)


FUTURES_GROUP_LABELS = {
    "Pre-open Core": "개장 전 핵심",
    "Equity Index": "주가지수",
    "Rates": "금리",
    "Commodities": "원자재",
    "FX Futures": "환율",
    "All": "전체 보기",
}
FUTURES_COMPACT_CHART_LIMIT = 6
FUTURES_STATE_LABELS = {
    "Calm": "안정",
    "Moving": "움직임",
    "Sharp": "급변",
    "Stale": "오래됨",
    "Missing": "자료 없음",
    "OK": "정상",
    "REVIEW": "확인 필요",
    "MISSING": "자료 없음",
}
MACRO_CONFIDENCE_LABELS = {
    "High Confidence": "근거 강도 높음",
    "Medium Confidence": "근거 강도 보통",
    "Low Confidence": "근거 강도 낮음",
    "Not Enough History": "근거 부족",
}
MACRO_CONFIDENCE_SHORT_LABELS = {
    "High Confidence": "높음",
    "Medium Confidence": "보통",
    "Low Confidence": "낮음",
    "Not Enough History": "부족",
}
MACRO_SCORE_LABELS = {
    "Risk-On Score": "위험선호",
    "Growth Score": "성장",
    "Rate Pressure Score": "금리",
    "Dollar Pressure Score": "달러",
    "Safe Haven Score": "안전자산",
    "Inflation Pressure Score": "물가",
}
MACRO_SCORE_POLARITY_LABELS = {
    "Risk-On Score": "+ 위험선호 강화 · - 위험회피",
    "Growth Score": "+ 성장 기대 강화 · - 성장 우려",
    "Rate Pressure Score": "+ 금리 부담 확대 · - 금리 부담 완화",
    "Dollar Pressure Score": "+ 달러 압력 확대 · - 달러 압력 완화",
    "Safe Haven Score": "+ 방어 수요 강화 · - 방어 수요 약화",
    "Inflation Pressure Score": "+ 물가 압력 확대 · - 물가 압력 완화",
}
MACRO_EVIDENCE_TEXT_LABELS = {
    "Risk-On": "위험선호",
    "Growth": "성장",
    "Rate Pressure": "금리 부담",
    "Dollar Pressure": "달러 압력",
    "Safe Haven": "안전자산",
    "Inflation": "물가 압력",
}
OVERVIEW_FUTURES_MACRO_VALIDATION_KEY = "overview_futures_macro_validation_snapshot"
OVERVIEW_FUTURES_MACRO_VALIDATION_CONFIDENCE_KEY = "overview_futures_macro_validation_confidence"
OVERVIEW_FUTURES_MACRO_VALIDATION_LOADED_AT_KEY = "overview_futures_macro_validation_loaded_at"
OVERVIEW_FUTURES_MACRO_REACT_EVENT_KEY = "overview_futures_macro_react_last_event"


def render_futures_macro_header() -> None:
    st.markdown("### 선물 매크로")
    st.caption("저장된 선물 일봉으로 현재 패턴과 다음 1주·1개월 조건부 위험 체제를 함께 확인합니다.")


def _store_overview_job_result(result_key: str, result: dict[str, Any]) -> None:
    st.session_state[result_key] = result
    try:
        record_overview_action_result(result)
    except Exception as exc:  # pragma: no cover - UI resilience only
        st.session_state["overview_run_history_warning"] = f"Run history write failed: {exc}"


def _run_futures_daily_ohlcv_action() -> dict[str, Any]:
    return run_overview_futures_daily_ohlcv()


def _clear_futures_macro_validation_state() -> None:
    clear_futures_macro_validation_cache()
    clear_futures_macro_pattern_validation_cache()
    for key in (
        OVERVIEW_FUTURES_MACRO_VALIDATION_KEY,
        OVERVIEW_FUTURES_MACRO_VALIDATION_CONFIDENCE_KEY,
        OVERVIEW_FUTURES_MACRO_VALIDATION_LOADED_AT_KEY,
    ):
        st.session_state.pop(key, None)


def _futures_macro_session_validation() -> tuple[dict[str, Any], dict[str, Any], str]:
    validation = st.session_state.get(OVERVIEW_FUTURES_MACRO_VALIDATION_KEY)
    confidence = st.session_state.get(OVERVIEW_FUTURES_MACRO_VALIDATION_CONFIDENCE_KEY)
    loaded_at = st.session_state.get(OVERVIEW_FUTURES_MACRO_VALIDATION_LOADED_AT_KEY)
    return (
        dict(validation) if isinstance(validation, dict) else {},
        dict(confidence) if isinstance(confidence, dict) else {},
        str(loaded_at or ""),
    )


def _load_futures_macro_validation_for_session(macro: dict[str, Any]) -> None:
    validation = build_futures_macro_validation_snapshot(
        symbols=_futures_selected_symbols(macro),
        current_snapshot=macro,
    )
    confidence = build_interpretation_confidence(macro, validation)
    st.session_state[OVERVIEW_FUTURES_MACRO_VALIDATION_KEY] = validation
    st.session_state[OVERVIEW_FUTURES_MACRO_VALIDATION_CONFIDENCE_KEY] = confidence
    st.session_state[OVERVIEW_FUTURES_MACRO_VALIDATION_LOADED_AT_KEY] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _reload_futures_macro_snapshot_for_ui() -> None:
    clear_overview_futures_macro_snapshot_cache()
    _clear_futures_macro_validation_state()
    st.session_state["overview_futures_macro_reloaded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _refresh_futures_macro_daily_for_ui() -> None:
    _store_overview_job_result(
        "overview_futures_daily_ohlcv_result",
        _run_futures_daily_ohlcv_action(),
    )
    clear_overview_futures_macro_snapshot_cache()
    _clear_futures_macro_validation_state()
    st.session_state["overview_futures_macro_daily_refreshed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _render_market_job_result(result_key: str) -> None:
    result = st.session_state.get(result_key)
    if not isinstance(result, dict):
        return
    status = str(result.get("status") or "")
    message = str(result.get("message") or "")
    if status == "success":
        st.success(message)
    elif status == "partial_success":
        st.warning(message)
    else:
        st.error(message)
    details = dict(result.get("details") or {})
    if details:
        source = details.get("source") or "-"
        method = details.get("method") or details.get("method_requested") or "-"
        duration = result.get("duration_sec")
        st.caption(
            "Rows: "
            f"{result.get('rows_written') or 0}, "
            f"Processed: {result.get('symbols_processed') or 0} / {result.get('symbols_requested') or 0}, "
            f"Source: {source}, Method: {method}, Duration: {_snapshot_value(duration)}s"
        )


def _render_snapshot_warnings(snapshot: dict[str, Any]) -> None:
    for warning in list(snapshot.get("warnings") or []):
        if str(warning).strip():
            st.warning(str(warning))


def _futures_interval_label(value: str) -> str:
    return {
        "1m": "1분",
        "5m": "5분",
        "15m": "15분",
        "60m": "60분",
        "1h": "60분",
    }.get(value, value)


def _futures_group_label(value: str) -> str:
    return FUTURES_GROUP_LABELS.get(value, value)


def _futures_state_label(value: Any) -> str:
    return FUTURES_STATE_LABELS.get(str(value or ""), str(value or "-"))


def _futures_state_tone(value: str) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in {"calm", "ok"}:
        return "positive"
    if normalized in {"moving", "due", "review"}:
        return "warning"
    if normalized in {"sharp", "stale", "missing", "failed"}:
        return "danger"
    return "neutral"


def _format_futures_percent(value: Any) -> str:
    try:
        if value is None or pd.isna(value):
            return "-"
        return f"{float(value):+.2f}%"
    except (TypeError, ValueError):
        return "-"


def _format_futures_age(value: Any) -> str:
    try:
        if value is None or pd.isna(value):
            return "-"
        return f"{float(value):.0f}분"
    except (TypeError, ValueError):
        return "-"


def _futures_metric_for_symbol(rows: Any, symbol: str) -> dict[str, Any]:
    if not isinstance(rows, pd.DataFrame) or rows.empty or "Symbol" not in rows:
        return {}
    matches = rows[rows["Symbol"] == symbol]
    return dict(matches.iloc[0]) if not matches.empty else {}


def _futures_selected_symbols(snapshot: dict[str, Any]) -> list[str]:
    raw_symbols = snapshot.get("symbols")
    if isinstance(raw_symbols, pd.DataFrame):
        if raw_symbols.empty or "Symbol" not in raw_symbols:
            symbols = []
        else:
            symbols = [str(symbol) for symbol in raw_symbols["Symbol"].dropna().tolist() if str(symbol).strip()]
    else:
        symbols = [str(symbol) for symbol in (raw_symbols or []) if str(symbol).strip()]
    ordered: list[str] = []
    for symbol in symbols:
        if symbol and symbol not in ordered:
            ordered.append(symbol)
    return ordered


def _display_text(value: Any, default: str = "-") -> str:
    text = str(value or "").strip()
    return text if text else default


def _react_metric(label: str, value: Any, *, detail: Any = None, tone: str = "neutral") -> dict[str, str]:
    return {
        "label": str(label),
        "value": _snapshot_value(value),
        "detail": "" if detail in (None, "") else str(detail),
        "tone": str(tone or "neutral"),
    }


def _futures_macro_react_scores(scores: Any) -> list[dict[str, str]]:
    if not isinstance(scores, pd.DataFrame) or scores.empty:
        return []
    rows: list[dict[str, str]] = []
    for row in scores.to_dict("records"):
        score_name = str(row.get("Score") or "")
        rows.append(
            {
                "label": MACRO_SCORE_LABELS.get(score_name, score_name),
                "value": _snapshot_value(row.get("Value")),
                "direction": _display_text(row.get("Direction")),
                "coverage": _display_text(row.get("Coverage")),
                "tone": str(row.get("Tone") or "neutral"),
                "polarity": MACRO_SCORE_POLARITY_LABELS.get(score_name, "+ 강화 · - 약화"),
                "description": _display_text(row.get("Description"), ""),
            }
        )
    return rows


def _futures_macro_react_flow_cards(cards: list[Any]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for card in cards:
        if not isinstance(card, dict):
            continue
        out.append(
            {
                "label": _display_text(card.get("label")),
                "value": _display_text(card.get("value")),
                "detail": _display_text(card.get("detail"), ""),
                "meaning": _display_text(card.get("meaning"), ""),
                "tone": str(card.get("tone") or "neutral"),
            }
        )
    return out


def _futures_macro_react_flow_period(period: dict[str, Any]) -> dict[str, Any]:
    key = _display_text(period.get("key"), "1W")
    return {
        "key": key,
        "label": _display_text(period.get("label"), key),
        "title": _display_text(period.get("title"), "최근 1주 흐름"),
        "basis": _display_text(period.get("basis"), "저장된 1D 선물 OHLCV의 최근 5거래일 변화율"),
        "summary": _display_text(period.get("summary"), "최근 흐름을 계산할 자료가 부족합니다."),
        "cards": _futures_macro_react_flow_cards(list(period.get("cards") or [])),
    }


def _futures_macro_react_flow(weekly_context: dict[str, Any], flow_context: dict[str, Any] | None = None) -> dict[str, Any]:
    periods: list[dict[str, Any]] = []
    if isinstance(flow_context, dict):
        for period in list(flow_context.get("periods") or []):
            if isinstance(period, dict):
                periods.append(_futures_macro_react_flow_period(period))
    if periods:
        default_period = (
            _display_text(flow_context.get("default_period"), periods[0]["key"])
            if isinstance(flow_context, dict)
            else periods[0]["key"]
        )
        selected = next((period for period in periods if period["key"] == default_period), periods[0])
        return {
            "title": selected["title"],
            "basis": selected["basis"],
            "summary": selected["summary"],
            "cards": selected["cards"],
            "default_period": default_period,
            "periods": periods,
        }

    cards = _futures_macro_react_flow_cards(list(weekly_context.get("cards") or []))
    fallback_period = {
        "key": "1W",
        "label": "1W",
        "title": "최근 1주 흐름",
        "basis": _display_text(weekly_context.get("basis"), "저장된 1D 선물 OHLCV의 최근 5거래일 변화율"),
        "summary": _display_text(weekly_context.get("summary"), "최근 흐름을 계산할 자료가 부족합니다."),
        "cards": cards,
    }
    return {
        "title": fallback_period["title"],
        "basis": fallback_period["basis"],
        "summary": fallback_period["summary"],
        "cards": cards,
        "default_period": "1W",
        "periods": [fallback_period],
    }


def _futures_macro_react_evidence_sections(macro: dict[str, Any]) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    for section in list(macro.get("evidence_reading") or []):
        if not isinstance(section, dict):
            continue
        items: list[dict[str, str]] = []
        for item in list(section.get("items") or [])[:6]:
            if not isinstance(item, dict):
                continue
            items.append(
                {
                    "title": _display_text(item.get("title")),
                    "score_label": _display_text(item.get("score_label"), ""),
                    "symbol": _display_text(item.get("symbol"), ""),
                    "contribution_z": _display_text(item.get("contribution_z"), ""),
                    "impact_label": _display_text(item.get("impact_label"), ""),
                    "meaning": _display_text(item.get("meaning"), ""),
                }
            )
        sections.append(
            {
                "key": _display_text(section.get("key")),
                "label": _display_text(section.get("label")),
                "description": _display_text(section.get("description"), ""),
                "count": int(section.get("count") or len(items)),
                "empty_label": _display_text(section.get("empty_label"), "표시할 근거가 없습니다."),
                "items": items,
            }
        )
    return sections


def _futures_macro_react_validation_state(validation: dict[str, Any], loaded_at: str) -> dict[str, str]:
    if validation:
        detail = f"과거 점검 기준: {loaded_at}" if loaded_at else "과거 점검을 불러왔습니다."
        return {"state": "불러옴", "detail": detail, "tone": "positive", "loaded_at": loaded_at}
    return {
        "state": "대기",
        "detail": "탭 첫 진입은 현재 매크로만 빠르게 읽고, 과거 점검은 필요할 때 계산합니다.",
        "tone": "warning",
        "loaded_at": "",
    }


def _futures_macro_react_validation_metrics(validation: dict[str, Any]) -> list[dict[str, str]]:
    if not validation:
        return [
            _react_metric("상태", "아직 불러오지 않음", detail="버튼으로 historical validation 계산", tone="warning"),
            _react_metric("점검 기준", "-", detail="계산 전"),
            _react_metric("비슷한 상태", "-", detail="계산 전"),
        ]
    coverage = dict(validation.get("coverage") or {})
    current_metrics = dict(validation.get("current_scenario_metrics") or {})
    occurrence = current_metrics.get("Occurrence Count")
    hit_applicable = bool(current_metrics.get("Directional Hit Applicable"))
    history_span = coverage.get("history_span_years")
    try:
        history_span_detail = f"{float(history_span):.2f}년 범위"
    except (TypeError, ValueError):
        history_span_detail = "기간 미확인"
    validation_dates = coverage.get("validation_dates")
    validation_dates_value = f"{_validation_int_value(validation_dates):,}개"
    occurrence_value = f"{_validation_int_value(occurrence):,}회"
    occurrence_detail = "5D 방향성 적용" if hit_applicable else "방향성 비적용"
    return [
        _react_metric("상태", validation.get("status") or "OK", detail=history_span_detail, tone="positive"),
        _react_metric("점검 기준", validation_dates_value, detail=history_span_detail),
        _react_metric("비슷한 상태", occurrence_value, detail=occurrence_detail),
    ]


def _validation_count_label(value: Any) -> str:
    try:
        if value is None or pd.isna(value):
            return "0회"
        return f"{int(value):,}회"
    except (TypeError, ValueError):
        return "0회"


def _validation_int_value(value: Any) -> int:
    try:
        if value is None or pd.isna(value):
            return 0
        return int(value)
    except (TypeError, ValueError):
        return 0


def _validation_signed_percent_label(value: Any) -> str:
    try:
        if value is None or pd.isna(value):
            return "-"
        return f"{float(value):+.2f}%"
    except (TypeError, ValueError):
        return "-"


def _validation_plain_percent_label(value: Any) -> str:
    try:
        if value is None or pd.isna(value):
            return "-"
        return f"{float(value):.1f}%"
    except (TypeError, ValueError):
        return "-"


def _validation_frequency_reading(occurrence_count: int, validation_dates: int) -> dict[str, str]:
    if validation_dates <= 0:
        return {
            "value": "확인 부족",
            "detail": "점검 기준일이 없어 빈도를 계산하지 못했습니다.",
        }
    ratio = max(0.0, min(1.0, float(occurrence_count) / float(validation_dates)))
    if ratio >= 0.5:
        value = "자주 발생"
    elif ratio >= 0.15:
        value = "반복 확인"
    elif occurrence_count > 0:
        value = "드문 상태"
    else:
        value = "확인 부족"
    return {
        "value": value,
        "detail": f"빈도 표본 {_validation_plain_percent_label(ratio * 100.0)} · 방향성 적중률 표본과 구분합니다.",
    }


def _validation_horizon_metric(
    metrics: dict[str, Any],
    *,
    horizon: int,
    hit_applicable: bool,
    occurrence_count: int,
) -> dict[str, str]:
    if not hit_applicable:
        return {
            "label": f"{horizon}거래일 표본",
            "value": "방향성 없음",
            "detail": (
                f"비슷한 과거 상태 {_validation_count_label(occurrence_count)} · "
                f"이 상태는 {horizon}D 적중률로 읽지 않습니다."
            ),
        }
    sample = _validation_int_value(metrics.get(f"Sample {horizon}D"))
    mean_value = _validation_signed_percent_label(metrics.get(f"Mean {horizon}D %"))
    hit_rate = _validation_plain_percent_label(metrics.get(f"Hit Rate {horizon}D %"))
    if sample <= 0 or mean_value == "-":
        return {
            "label": f"{horizon}거래일 표본",
            "value": "표본 부족",
            "detail": f"계산 가능 표본 {_validation_count_label(sample)} · 방향 일관성 {hit_rate}",
        }
    return {
        "label": f"{horizon}거래일 표본",
        "value": mean_value,
        "detail": f"표본 {_validation_count_label(sample)} · 방향 일관성 {hit_rate}",
    }


def _validation_asset_reading(metrics: dict[str, Any], *, hit_applicable: bool) -> dict[str, str]:
    family = _display_text(metrics.get("Target Family"), "Mixed")
    rule = _display_text(metrics.get("Hit Rule"), "mixed scenario; no forced directional hit rule")
    if not hit_applicable:
        return {
            "label": "자산군 해석",
            "value": "중립 / 관망",
            "detail": f"Target Family: {family} · 방향성 hit rule 없음",
        }
    family_label = {
        "Risk Asset": "위험자산",
        "Growth Asset": "성장자산",
        "Safe Haven": "방어자산",
        "Dollar": "달러",
    }.get(family, family)
    if "> 0" in rule:
        value = f"{family_label} 우위"
    elif "< 0" in rule:
        value = f"{family_label} 약세"
    else:
        value = f"{family_label} 방향성 참고"
    return {
        "label": "자산군 해석",
        "value": value,
        "detail": f"Target Family: {family} · Hit Rule: {rule}",
    }


def _validation_confidence_effect(metrics: dict[str, Any], *, hit_applicable: bool, occurrence_count: int) -> str:
    if not hit_applicable:
        return (
            f"비슷한 과거 상태 {_validation_count_label(occurrence_count)}였지만 이 상태는 상승/하락 확률로 읽지 않습니다. "
            "계산된 표본 통계만 사용하며, 매수/매도 신호가 아니라 현재 해석을 보수적으로 볼지 확인하는 근거입니다."
        )
    sample_5d = _validation_int_value(metrics.get("Sample 5D"))
    mean_5d = _validation_signed_percent_label(metrics.get("Mean 5D %"))
    hit_rate_5d = _validation_plain_percent_label(metrics.get("Hit Rate 5D %"))
    return (
        f"비슷한 과거 상태 {_validation_count_label(occurrence_count)} 중 5D 계산 표본 {_validation_count_label(sample_5d)}에서 "
        f"5D 평균 {mean_5d}, 방향 일관성 {hit_rate_5d}입니다. "
        "계산된 표본 통계만 사용하며, 매수/매도 신호가 아니라 현재 해석을 보수적으로 볼지 확인하는 근거입니다."
    )


def _futures_macro_react_validation_conclusion(
    macro: dict[str, Any],
    validation: dict[str, Any],
) -> list[dict[str, str]]:
    if not validation:
        return [
            {"label": "비슷한 상태", "value": "계산 전", "detail": "과거 표본 계산 전입니다."},
            {"label": "상태 빈도", "value": "계산 전", "detail": "과거 표본 계산 후 표시합니다."},
            {"label": "방향성 판정", "value": "대기", "detail": "계산 후 hit rule 적용 여부를 표시합니다."},
            {"label": "판정 이유", "value": "계산 전", "detail": "Target Family / Hit Rule 계산 전입니다."},
        ]

    coverage = dict(validation.get("coverage") or {})
    current_metrics = dict(validation.get("current_scenario_metrics") or {})
    summary = dict(macro.get("summary") or {})
    scenario = _display_text(current_metrics.get("Scenario") or summary.get("scenario"), "현재 상태")
    occurrence_count = _validation_int_value(current_metrics.get("Occurrence Count"))
    validation_dates = _validation_int_value(coverage.get("validation_dates"))
    hit_applicable = bool(current_metrics.get("Directional Hit Applicable"))
    family = _display_text(current_metrics.get("Target Family"), "Mixed")
    rule = _display_text(current_metrics.get("Hit Rule"), "mixed scenario; no forced directional hit rule")
    frequency = _validation_frequency_reading(occurrence_count, validation_dates)
    similar_value = (
        f"{_validation_count_label(occurrence_count)} / {validation_dates:,}일"
        if validation_dates > 0
        else f"{_validation_count_label(occurrence_count)} / 점검 기준 미확인"
    )
    if hit_applicable:
        direction_value = "적용 가능"
        direction_detail = f"Hit Rule: {rule}"
        reason_value = family
    else:
        direction_value = "보류"
        direction_detail = "혼재/관망 상태라 특정 자산 상승/하락 적중률로 채점하지 않습니다."
        reason_value = "Hit rule 없음"
    return [
        {
            "label": "비슷한 상태",
            "value": similar_value,
            "detail": f"현재 상태: {scenario} · 과거 빈도 표본입니다.",
        },
        {"label": "상태 빈도", "value": frequency["value"], "detail": frequency["detail"]},
        {"label": "방향성 판정", "value": direction_value, "detail": direction_detail},
        {"label": "판정 이유", "value": reason_value, "detail": f"Target Family: {family} · Hit Rule: {rule}"},
    ]


def _futures_macro_react_validation_insight(
    macro: dict[str, Any],
    validation: dict[str, Any],
    *,
    confidence_label: str = "",
) -> dict[str, Any]:
    coverage = dict(macro.get("coverage") or {})
    summary = dict(macro.get("summary") or {})
    scenario = _display_text(summary.get("scenario"), "현재 상태 미확인")
    standardized = int(coverage.get("standardized_count") or 0)
    symbol_count = int(coverage.get("symbol_count") or 0)
    basis = (
        f"현재 1D 선물 {standardized}/{symbol_count}개 움직임을 같은 계산식으로 과거 날짜에 다시 적용합니다."
    )
    evidence_counts = {"strong": 0, "weak": 0, "conflicting": 0, "missing": 0}
    for section in list(macro.get("evidence_reading") or []):
        key = str(section.get("key") or "")
        if key in evidence_counts:
            evidence_counts[key] = int(section.get("count") or 0)
    evidence_bridge = {
        "label": "자산군 해석",
        "value": "계산 전",
        "detail": (
            f"현재 근거: 강한 근거 {evidence_counts['strong']}개 · "
            f"약한 근거 {evidence_counts['weak']}개 · 충돌 근거 {evidence_counts['conflicting']}개"
        ),
    }
    if not validation:
        return {
            "purpose": "오늘과 비슷한 과거 흐름 확인",
            "basis": basis,
            "current_state": {"label": "판정", "value": "계산 전", "detail": f"현재 상태: {scenario}"},
            "sample": {"label": "5거래일 표본", "value": "계산 전", "detail": "과거 표본 계산 전입니다."},
            "directionality": {"label": "20거래일 표본", "value": "계산 전", "detail": "과거 표본 계산 전입니다."},
            "evidence_bridge": evidence_bridge,
            "confidence_effect": "버튼을 눌러 과거 표본 통계를 계산합니다. 결과 문구는 계산된 표본 통계만 사용합니다.",
        }

    validation_summary = build_current_scenario_validation_summary(validation, confidence_label=confidence_label)
    current_metrics = dict(validation.get("current_scenario_metrics") or {})
    occurrence_count = _validation_int_value(current_metrics.get("Occurrence Count"))
    hit_applicable = bool(validation_summary.get("hit_rate_applicable"))
    state_value = "방향성 참고 가능" if hit_applicable else "방향성 보류"
    five_day = _validation_horizon_metric(
        current_metrics,
        horizon=5,
        hit_applicable=hit_applicable,
        occurrence_count=occurrence_count,
    )
    twenty_day = _validation_horizon_metric(
        current_metrics,
        horizon=20,
        hit_applicable=hit_applicable,
        occurrence_count=occurrence_count,
    )
    asset_reading = _validation_asset_reading(current_metrics, hit_applicable=hit_applicable)
    return {
        "purpose": "오늘과 비슷한 과거 흐름 확인",
        "basis": basis,
        "current_state": {
            "label": "판정",
            "value": state_value,
            "detail": (
                f"{scenario} · {_display_text(summary.get('sub_scenario') or summary.get('regime_hint'), '현재 상태')}"
            ),
        },
        "sample": five_day,
        "directionality": twenty_day,
        "evidence_bridge": asset_reading,
        "confidence_effect": _validation_confidence_effect(
            current_metrics,
            hit_applicable=hit_applicable,
            occurrence_count=occurrence_count,
        ),
    }


def _futures_macro_react_validation_visual_candidates(validation: dict[str, Any]) -> list[dict[str, str]]:
    if not validation:
        return [
            {
                "key": "similar_state_frequency",
                "label": "비슷했던 날 분포",
                "status": "pending",
                "detail": "과거 점검 계산 후 현재 상태가 과거에 얼마나 자주 나왔는지 시각화할 수 있습니다.",
            },
            {
                "key": "forward_return_distribution",
                "label": "이후 흐름 분포",
                "status": "pending",
                "detail": "방향성 적용 가능 여부를 확인한 뒤 시각화 여부를 결정합니다.",
            },
    ]
    current_metrics = dict(validation.get("current_scenario_metrics") or {})
    occurrence_count = _validation_int_value(current_metrics.get("Occurrence Count"))
    sample_5d = _validation_int_value(current_metrics.get("Sample 5D"))
    hit_applicable = bool(current_metrics.get("Directional Hit Applicable"))
    return [
        {
            "key": "similar_state_frequency",
            "label": "비슷했던 날 분포",
            "status": "ready" if occurrence_count > 0 else "insufficient",
            "detail": f"현재 상태와 같은 과거 분류 {occurrence_count:,}회를 기간별 빈도로 보여줄 수 있습니다.",
        },
        {
            "key": "forward_return_distribution",
            "label": "이후 흐름 분포",
            "status": "ready" if hit_applicable and sample_5d > 0 else "not_applicable",
            "detail": (
                f"방향성 표본 {sample_5d:,}회의 5D 이후 흐름 분포를 보여줄 수 있습니다."
                if hit_applicable and sample_5d > 0
                else "혼재 또는 저신호 상태는 이후 방향성 분포보다 발생 빈도 시각화가 우선입니다."
            ),
        },
    ]


PATTERN_REGIME_LABELS = {
    "risk_seeking": "위험선호 체제",
    "defensive": "방어적 위험 체제",
    "inflation_rate_pressure": "물가·금리 부담 체제",
    "mixed": "혼재 체제",
}
PATTERN_ASSET_DEFINITIONS = (
    ("risk_assets", "주식 위험선호", "risk_on"),
    ("rates", "금리 부담", "rate_pressure"),
    ("dollar", "달러 압력", "dollar_pressure"),
    ("safe_haven", "안전자산", "safe_haven"),
    ("commodities", "원자재·물가", "inflation_pressure"),
)


def _current_pattern_horizon(pattern: dict[str, Any]) -> dict[str, Any]:
    return {
        "key": "current",
        "label": "현재 관측",
        "kind": "observation",
        "title": _display_text(pattern.get("regime_label"), "현재 체제 자료 부족"),
        "summary": _display_text(pattern.get("summary"), "다중 기간 패턴을 계산할 자료가 부족합니다."),
        "estimate_status": "PROVISIONAL" if pattern.get("status") in {"READY", "PARTIAL"} else "UNAVAILABLE",
        "edge_label": _display_text(pattern.get("transition_label"), "자료 부족"),
        "status_reason": "현재는 1D / 5D / 20D 관측이며 미래 확률이 아닙니다.",
    }


def _future_conditional_path(item: dict[str, Any], status: str) -> dict[str, Any]:
    """Normalize service-owned analog coordinates without fabricating fallbacks."""

    raw = dict(item.get("conditional_path") or {})
    path_status = str(raw.get("status") or "UNAVAILABLE")
    base = {
        "status": path_status,
        "episode_count": int(
            raw.get("episode_count") or item.get("episode_count") or 0
        ),
        "band_label": _display_text(
            raw.get("band_label"),
            "과거 유사 패턴 가운데 50%",
        ),
        "validation": dict(raw.get("validation") or {}),
    }
    if status == "UNAVAILABLE" or path_status == "UNAVAILABLE":
        return {**base, "status": "UNAVAILABLE", "points": [], "terminal": None}
    coordinate_keys = (
        "x",
        "y",
        "lower_x",
        "upper_x",
        "lower_y",
        "upper_y",
    )
    points: list[dict[str, Any]] = []
    for raw_point in list(raw.get("points") or []):
        point = dict(raw_point or {})
        if point.get("step") is None or any(
            point.get(key) is None for key in coordinate_keys
        ):
            continue
        coordinates = {key: float(point[key]) for key in coordinate_keys}
        if not all(isfinite(value) for value in coordinates.values()):
            continue
        points.append({"step": int(point["step"]), **coordinates})
    return {
        **base,
        "points": points,
        "terminal": points[-1] if points else None,
    }


def _future_pattern_horizon(item: dict[str, Any]) -> dict[str, Any]:
    status = str(item.get("estimate_status") or "UNAVAILABLE")
    raw_probabilities = dict(item.get("probabilities") or {}) if status != "UNAVAILABLE" else {}
    baseline = dict(item.get("baseline_probabilities") or {})
    lift = dict(item.get("probability_lift") or {})
    probabilities = [
        {
            "key": key,
            "label": PATTERN_REGIME_LABELS[key],
            "value": float(raw_probabilities.get(key) or 0.0),
            "baseline": float(baseline.get(key) or 0.0),
            "lift": float(lift.get(key) or 0.0),
        }
        for key in ("risk_seeking", "defensive", "inflation_rate_pressure", "mixed")
        if key in raw_probabilities
    ]
    horizon = int(item.get("horizon") or 0)
    dominant = str(item.get("dominant_regime") or "")
    return {
        "key": f"{horizon}D",
        "label": _display_text(item.get("label"), "조건부 전망"),
        "kind": "conditional_outlook",
        "title": PATTERN_REGIME_LABELS.get(dominant, "조건부 방향 우위 미확인"),
        "summary": _display_text(item.get("edge_label"), "방향 우위 미확인"),
        "estimate_status": status,
        "edge_label": _display_text(item.get("edge_label"), "방향 우위 미확인"),
        "baseline_label": "평소 기준 확률",
        "probabilities": probabilities,
        "episode_count": int(item.get("episode_count") or 0),
        "status_reason": _display_text(item.get("status_reason"), "검증 근거가 부족합니다."),
        "conditional_path": _future_conditional_path(item, status),
    }


def _pattern_command_payload(macro: dict[str, Any], pattern_outlook: dict[str, Any]) -> dict[str, Any]:
    coverage = dict(macro.get("coverage") or {})
    standardized = int(coverage.get("standardized_count") or 0)
    symbol_count = int(coverage.get("symbol_count") or 0)
    latest_daily = _snapshot_value(coverage.get("latest_daily_date") or pattern_outlook.get("as_of_date"))
    return {
        "title": "선물 매크로 패턴",
        "detail": f"일봉 {standardized}/{symbol_count}개 · 기준일 {latest_daily} · stored continuous futures",
        "actions": [
            {"id": "daily_refresh", "label": "일봉 갱신", "kind": "primary", "detail": "저장된 주요 선물 5년 1D OHLCV를 다시 수집합니다."},
            {"id": "reload", "label": "다시 읽기", "kind": "secondary", "detail": "현재 DB 기준으로 snapshot cache를 비운 뒤 다시 읽습니다."},
        ],
    }


def _pattern_hero_payload(macro: dict[str, Any], pattern: dict[str, Any]) -> dict[str, Any]:
    coverage = dict(pattern.get("coverage") or {})
    summary = dict(macro.get("summary") or {})
    evidence = dict(pattern.get("evidence") or {})
    return {
        "kicker": "현재 선물 체제",
        "title": _display_text(pattern.get("regime_label"), "현재 체제 자료 부족"),
        "transition_label": _display_text(pattern.get("transition_label"), "자료 부족"),
        "summary": _display_text(pattern.get("summary") or summary.get("summary"), "현재 패턴을 계산할 자료가 부족합니다."),
        "today_summary": _display_text(summary.get("summary"), "오늘의 재가격화 근거가 부족합니다."),
        "as_of_date": _display_text(pattern.get("as_of_date"), "-"),
        "estimate_status": "PROVISIONAL" if pattern.get("status") in {"READY", "PARTIAL"} else "UNAVAILABLE",
        "coverage_label": f"family {coverage.get('available_family_count') or 0}/{coverage.get('required_family_count') or 6}",
        "evidence": [str(value) for value in list(evidence.get("current") or []) if str(value).strip()],
    }


def _pattern_evidence_payload(
    pattern: dict[str, Any],
    pattern_outlook: dict[str, Any],
    macro: dict[str, Any],
) -> dict[str, Any]:
    evidence = dict(pattern.get("evidence") or {})
    macro_summary = dict(macro.get("summary") or {})
    outlook_items = [
        f"{item.get('label')}: {item.get('edge_label')} · {item.get('estimate_status')}"
        for item in list(pattern_outlook.get("horizons") or [])
    ]
    current_items = list(evidence.get("current") or [])
    current_items.extend(str(item) for item in list(macro_summary.get("evidence") or [])[:2])
    return {
        "title": "현재 근거와 변화 조건",
        "groups": [
            {"key": "current", "label": "현재 위치", "items": current_items},
            {"key": "transition", "label": "지속·전환", "items": list(evidence.get("transition") or [])},
            {"key": "outlook", "label": "전망 우위", "items": outlook_items},
            {"key": "invalidate", "label": "바뀌는 조건", "items": list(pattern.get("change_conditions") or [])},
        ],
    }


def _family_state_label(family: dict[str, Any], key: str) -> str:
    value = family.get(key)
    if value is None:
        return "자료 부족"
    numeric = float(value)
    if numeric >= 0.5:
        return "강화"
    if numeric <= -0.5:
        return "약화"
    return "중립"


def _pathway_outlook_label(horizon: dict[str, Any], pathway_key: str) -> str:
    if str(horizon.get("estimate_status")) == "UNAVAILABLE":
        return "검증 부족"
    pathway = dict(dict(horizon.get("asset_pathways") or {}).get(pathway_key) or {})
    value = pathway.get("median_forward_z")
    if value is None:
        return "우위 미확인"
    if float(value) >= 0.25:
        return "상방 우세"
    if float(value) <= -0.25:
        return "하방 우세"
    return "우위 미확인"


def _pattern_asset_pathways(
    pattern: dict[str, Any],
    pattern_outlook: dict[str, Any],
) -> list[dict[str, Any]]:
    families = dict(pattern.get("families") or {})
    horizon_map = {
        int(item.get("horizon") or 0): item
        for item in list(pattern_outlook.get("horizons") or [])
    }
    change_conditions = list(pattern.get("change_conditions") or [])
    status_order = {"VERIFIED": 2, "PROVISIONAL": 1, "UNAVAILABLE": 0}
    horizon_statuses = [str(item.get("estimate_status") or "UNAVAILABLE") for item in horizon_map.values()]
    estimate_status = min(horizon_statuses, key=lambda value: status_order.get(value, 0)) if horizon_statuses else "UNAVAILABLE"
    return [
        {
            "key": pathway_key,
            "label": label,
            "current": {
                "one_day": _family_state_label(dict(families.get(family_key) or {}), "one_day"),
                "five_day": _family_state_label(dict(families.get(family_key) or {}), "five_day"),
                "twenty_day": _family_state_label(dict(families.get(family_key) or {}), "twenty_day"),
            },
            "outlook": {
                "five_day": _pathway_outlook_label(dict(horizon_map.get(5) or {}), pathway_key),
                "twenty_day": _pathway_outlook_label(dict(horizon_map.get(20) or {}), pathway_key),
            },
            "change_condition": _display_text(change_conditions[0] if change_conditions else None, "다음 5D persistence를 확인합니다."),
            "estimate_status": estimate_status,
        }
        for pathway_key, label, family_key in PATTERN_ASSET_DEFINITIONS
    ]


def _pattern_method_payload(pattern_outlook: dict[str, Any]) -> dict[str, Any]:
    method = dict(pattern_outlook.get("method") or {})
    effective = dict(method.get("effective_episodes") or {})
    brier = dict(method.get("brier") or {})
    baseline = dict(method.get("baseline_brier") or {})
    calibration = dict(method.get("calibration") or {})
    return {
        "source": "stored yfinance continuous futures daily OHLCV",
        "effective_episodes": f"5D {effective.get('5', 0)}개 · 20D {effective.get('20', 0)}개",
        "brier": f"5D {_snapshot_value(brier.get('5'))} · 20D {_snapshot_value(brier.get('20'))}",
        "baseline_brier": f"5D {_snapshot_value(baseline.get('5'))} · 20D {_snapshot_value(baseline.get('20'))}",
        "calibration": f"5D {_snapshot_value(calibration.get('5'))} · 20D {_snapshot_value(calibration.get('20'))}",
        "caveats": [str(item) for item in list(pattern_outlook.get("limitations") or [])],
    }


def build_futures_macro_react_workbench_payload(
    macro: dict[str, Any],
    *,
    pattern_outlook: dict[str, Any],
) -> dict[str, Any]:
    pattern = dict(pattern_outlook.get("current_pattern") or macro.get("pattern") or {})
    return {
        "schema_version": "futures_macro_react_workbench_v2",
        "component": "FuturesMacroWorkbench",
        "command": _pattern_command_payload(macro, pattern_outlook),
        "hero": _pattern_hero_payload(macro, pattern),
        "horizons": [
            _current_pattern_horizon(pattern),
            *[
                _future_pattern_horizon(item)
                for item in list(pattern_outlook.get("horizons") or [])
            ],
        ],
        "pattern_map": {
            "title": "최근 패턴 경로",
            "x_label": "위험선호",
            "y_label": "매크로 부담",
            "path": list(pattern.get("path") or []),
        },
        "evidence": _pattern_evidence_payload(pattern, pattern_outlook, macro),
        "ribbon": {"title": "최근 60거래일 체제", "items": list(pattern.get("ribbon") or [])},
        "asset_pathways": _pattern_asset_pathways(pattern, pattern_outlook),
        "method": _pattern_method_payload(pattern_outlook),
        "action_boundary": "python_dispatch_only",
        "boundary_note": "이 화면은 빠른 시장 재가격화와 조건부 위험 체제를 설명하며 매수매도 신호가 아닙니다.",
    }


def _futures_macro_react_event_payload(event: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(event, dict):
        return {}
    nested = event.get("event")
    if isinstance(nested, dict):
        return dict(nested)
    return event


def _handle_futures_macro_react_event(event: dict[str, Any] | None, macro: dict[str, Any]) -> None:
    payload = _futures_macro_react_event_payload(event)
    action_id = str(payload.get("id") or payload.get("action_id") or "")
    if not action_id:
        return
    nonce = payload.get("nonce") or payload.get("token") or action_id
    event_key = f"{action_id}:{nonce}"
    if st.session_state.get(OVERVIEW_FUTURES_MACRO_REACT_EVENT_KEY) == event_key:
        return
    st.session_state[OVERVIEW_FUTURES_MACRO_REACT_EVENT_KEY] = event_key
    if action_id == "daily_refresh":
        with st.spinner("선물 5년 일봉을 yfinance에서 수집하는 중입니다..."):
            _refresh_futures_macro_daily_for_ui()
        st.rerun()
    if action_id == "reload":
        _reload_futures_macro_snapshot_for_ui()
        st.rerun()


def _futures_symbols_with_candles(snapshot: dict[str, Any], selected_symbols: list[str] | None = None) -> list[str]:
    selected = selected_symbols if selected_symbols is not None else _futures_selected_symbols(snapshot)
    all_candles = snapshot.get("all_candles")
    if not isinstance(all_candles, pd.DataFrame) or all_candles.empty or "Symbol" not in all_candles:
        return []
    chartable = {str(symbol) for symbol in all_candles["Symbol"].dropna().unique()}
    return [symbol for symbol in selected if symbol in chartable]


def _futures_chart_symbols(snapshot: dict[str, Any], *, chart_scope: str = "compact_6") -> list[str]:
    selected = _futures_selected_symbols(snapshot)
    chartable = _futures_symbols_with_candles(snapshot, selected)
    if chart_scope == "all_with_data":
        return chartable
    candidates = chartable or selected
    return candidates[:FUTURES_COMPACT_CHART_LIMIT]


def _futures_chart_scope_label(scope: str) -> str:
    if scope == "all_with_data":
        return "데이터 있는 전체"
    return "핵심 6개"


def _futures_chart_scope_detail(snapshot: dict[str, Any], *, chart_scope: str) -> str:
    selected_count = len(_futures_selected_symbols(snapshot))
    chartable_count = len(_futures_symbols_with_candles(snapshot))
    shown_count = len(_futures_chart_symbols(snapshot, chart_scope=chart_scope))
    if chart_scope == "all_with_data":
        return f"선택 {selected_count}개 중 데이터 있는 {shown_count}개 표시"
    return f"차트 가능 {chartable_count or selected_count}개 중 {shown_count}개 표시"


def _futures_feed_state(snapshot: dict[str, Any], *, refresh_mode: str) -> dict[str, Any]:
    coverage = dict(snapshot.get("coverage") or {})
    latest_age = coverage.get("latest_age_minutes")
    oldest_age = coverage.get("oldest_age_minutes")
    status = str(snapshot.get("status") or "MISSING")
    if latest_age is None or pd.isna(latest_age):
        label = "자료 없음"
        detail = "저장 candle 없음"
        tone = "danger"
    else:
        age_value = int(latest_age or 0)
        if age_value <= 2 and status == "OK":
            label = "신선함"
            detail = f"최신 {age_value}분"
            tone = "positive"
        elif age_value <= 10:
            label = "확인 필요"
            detail = f"최신 {age_value}분"
            tone = "warning"
        else:
            label = "오래됨"
            detail = f"최신 {age_value}분"
            tone = "danger"
    cadence = "수동 확인"
    if refresh_mode == "auto_60s":
        cadence = "60초 자동 확인"
    elif refresh_mode == "fast_20s":
        cadence = "20초 빠른 확인"
    return {
        "label": label,
        "detail": detail,
        "tone": tone,
        "cadence": cadence,
        "latest_age": latest_age,
        "oldest_age": oldest_age,
    }


def _futures_data_action_hint(feed: dict[str, Any]) -> str:
    tone = str(feed.get("tone") or "neutral")
    cadence = str(feed.get("cadence") or "-")
    if tone == "positive":
        return f"확인 완료 · {cadence}"
    if str(feed.get("label") or "") == "자료 없음":
        return f"1분봉 갱신 필요 · {cadence}"
    return f"갱신 필요 · {cadence}"


def _futures_next_action_state(feed: dict[str, Any]) -> dict[str, str]:
    label = str(feed.get("label") or "")
    tone = str(feed.get("tone") or "neutral")
    cadence = str(feed.get("cadence") or "-")
    detail = str(feed.get("detail") or "-")
    if tone == "positive":
        return {"value": "자료 양호", "detail": f"{detail} · {cadence}", "tone": "positive"}
    if label in {"자료 없음", "오래됨"} or tone == "danger":
        return {"value": "갱신 필요", "detail": f"{detail} · {cadence}", "tone": "danger"}
    return {"value": "확인 필요", "detail": f"{detail} · {cadence}", "tone": tone or "warning"}


def _futures_compact_symbols_label(selected_symbols: list[str]) -> str:
    if not selected_symbols:
        return "-"
    if len(selected_symbols) <= 4:
        return ", ".join(selected_symbols)
    return f"{', '.join(selected_symbols[:4])} 외 {len(selected_symbols) - 4}개"


def _futures_command_summary_items(
    *,
    snapshot: dict[str, Any],
    group: str,
    selected_symbols: list[str],
    lookback_label: str,
    chart_interval: str,
    refresh_mode: str,
) -> list[dict[str, Any]]:
    feed = _futures_feed_state(snapshot, refresh_mode=refresh_mode)
    top_move = dict(snapshot.get("top_move") or {})
    return [
        {
            "label": "관찰 범위",
            "value": f"{_futures_group_label(group)} · {len(selected_symbols)}개",
            "detail": _futures_compact_symbols_label(selected_symbols),
            "tone": "neutral",
            "pills": [str(feed.get("cadence") or "-")],
            "pill_tones": ["neutral"],
        },
        {
            "label": "데이터 상태",
            "value": str(feed.get("label") or "-"),
            "detail": _futures_data_action_hint(feed),
            "tone": str(feed.get("tone") or "neutral"),
            "pills": [str(feed.get("detail") or "-")],
            "pill_tones": [str(feed.get("tone") or "neutral")],
        },
        {
            "label": "단기 움직임",
            "value": str(top_move.get("Symbol") or "-"),
            "detail": (
                f"15분 {_format_futures_percent(top_move.get('15m %'))} · 60분 {_format_futures_percent(top_move.get('60m %'))}"
                if top_move.get("Symbol")
                else "저장 candle 대기"
            ),
            "tone": _futures_state_tone(str(top_move.get("State") or "")),
            "pills": [
                _futures_state_label(top_move.get("State") or "대기"),
                f"{lookback_label} · {_futures_interval_label(chart_interval)} 봉",
            ],
            "pill_tones": [_futures_state_tone(str(top_move.get("State") or "")), "neutral"],
        },
    ]


def _futures_workbench_context_items(
    *,
    snapshot: dict[str, Any],
    group: str,
    selected_symbols: list[str],
    lookback_label: str,
    chart_interval: str,
    chart_scope: str,
    refresh_mode: str,
) -> list[dict[str, Any]]:
    feed = _futures_feed_state(snapshot, refresh_mode=refresh_mode)
    next_action = _futures_next_action_state(feed)
    return [
        {
            "label": "관찰",
            "value": f"{_futures_group_label(group)} · {len(selected_symbols)}개",
            "detail": _futures_compact_symbols_label(selected_symbols),
            "tone": "neutral",
        },
        {
            "label": "차트",
            "value": f"{lookback_label} · {_futures_interval_label(chart_interval)} 봉 · {_futures_chart_scope_label(chart_scope)}",
            "detail": _futures_chart_scope_detail(snapshot, chart_scope=chart_scope),
            "tone": "neutral",
        },
        {
            "label": "자료",
            "value": str(feed.get("label") or "-"),
            "detail": str(feed.get("detail") or "-"),
            "tone": str(feed.get("tone") or "neutral"),
        },
        {
            "label": "다음 행동",
            "value": next_action["value"],
            "detail": next_action["detail"],
            "tone": next_action["tone"],
        },
    ]


def _futures_daily_coverage_label(coverage: dict[str, Any]) -> str:
    standardized_count = int(coverage.get("standardized_count") or 0)
    symbol_count = int(coverage.get("symbol_count") or 0)
    if symbol_count <= 0:
        return "0/0"
    return f"{standardized_count}/{symbol_count}"


def _futures_refresh_module_model(
    *,
    snapshot: dict[str, Any],
    macro: dict[str, Any],
    selected_symbols: list[str],
    refresh_mode: str,
) -> dict[str, Any]:
    feed = _futures_feed_state(snapshot, refresh_mode=refresh_mode)
    macro_coverage = dict(macro.get("coverage") or {})
    latest_age = _format_futures_age(feed.get("latest_age"))
    live_status = _futures_next_action_state(feed)
    macro_basis = _snapshot_value(macro_coverage.get("latest_daily_date"))
    macro_coverage_label = _futures_daily_coverage_label(macro_coverage)
    macro_standardized = int(macro_coverage.get("standardized_count") or 0)
    macro_symbol_count = int(macro_coverage.get("symbol_count") or 0)
    macro_ok = macro_symbol_count > 0 and macro_standardized >= macro_symbol_count
    return {
        "title": "자료 갱신",
        "sources": [
            {
                "label": "실시간 차트 자료",
                "basis": "1분봉",
                "status": live_status["value"],
                "detail": f"선택 선물 {len(selected_symbols)}개 · 최신 candle {latest_age} · 60초 자동 확인 대상",
                "tone": live_status["tone"],
            },
            {
                "label": "매크로 일봉 자료",
                "basis": "1D OHLCV",
                "status": "자료 양호" if macro_ok else "확인 필요",
                "detail": f"macro context 기준일 {macro_basis} · daily coverage {macro_coverage_label}",
                "tone": "positive" if macro_ok else "warning",
            },
        ],
        "actions": [
            {"label": "1분봉 갱신", "kind": "live"},
            {"label": "일봉 매크로 갱신", "kind": "macro_daily"},
            {"label": "화면 다시 읽기", "kind": "reload"},
        ],
        "modes": [
            {"label": "수동", "value": "manual"},
            {"label": "60초 자동 확인", "value": "auto_60s"},
        ],
    }


def _futures_watch_strip_items(snapshot: dict[str, Any], selected_symbols: list[str]) -> list[dict[str, Any]]:
    rows = snapshot.get("rows")
    items: list[dict[str, Any]] = []
    for symbol in selected_symbols:
        metric = _futures_metric_for_symbol(rows, symbol)
        state = str(metric.get("State") or "Missing")
        items.append(
            {
                "symbol": symbol,
                "title": str(metric.get("Name") or symbol),
                "state": _futures_state_label(state),
                "move": (
                    f"15분 {_format_futures_percent(metric.get('15m %'))} · "
                    f"60분 {_format_futures_percent(metric.get('60m %'))}"
                ),
                "age": _format_futures_age(metric.get("Age Min")),
                "tone": _futures_state_tone(state),
            }
        )
    return items


def _futures_live_summary_line(
    snapshot: dict[str, Any],
    *,
    chart_interval: str,
    lookback_label: str,
    chart_scope: str,
) -> str:
    selected_count = len([symbol for symbol in snapshot.get("symbols") or [] if str(symbol).strip()])
    return (
        f"선택 {selected_count}개 · {_futures_interval_label(chart_interval)} 봉 · {lookback_label} 범위 · "
        f"{_futures_chart_scope_detail(snapshot, chart_scope=chart_scope)}"
    )


def _macro_confidence_label(value: Any) -> str:
    return MACRO_CONFIDENCE_LABELS.get(str(value or ""), str(value or "근거 부족"))


def _macro_confidence_short_label(value: Any) -> str:
    return MACRO_CONFIDENCE_SHORT_LABELS.get(str(value or ""), _macro_confidence_label(value))


def _macro_evidence_summary_label(value: Any) -> str:
    text = str(value or "")
    for source_label, display_label in MACRO_EVIDENCE_TEXT_LABELS.items():
        text = text.replace(source_label, display_label)
    return text


def _macro_validation_status_label(value: Any) -> str:
    normalized = str(value or "")
    if normalized == "OK":
        return "점검 가능"
    if normalized == "REVIEW":
        return "확인 필요"
    if normalized == "MISSING":
        return "자료 부족"
    if normalized == "ERROR":
        return "점검 실패"
    return normalized or "-"


def _macro_confidence_reason_label(value: Any) -> str:
    text = str(value or "")
    if text.startswith("Latest daily futures candle is ") and text.endswith(" days old."):
        age = text.removeprefix("Latest daily futures candle is ").removesuffix(" days old.")
        return f"최근 선물 일봉 기준이 {age}일 전이라 오늘 해석은 신선도를 확인해야 합니다."
    translations = {
        "Most core symbols have 60D standardized moves.": "대부분의 핵심 선물이 60D 표준화 이동을 계산할 수 있습니다.",
        "Most, but not all, core symbols have 60D standardized moves.": "대부분의 핵심 선물이 60D 표준화 이동을 계산할 수 있습니다.",
        "Daily standardized coverage is partial.": "일봉 표준화 계산 가능 범위가 일부에 그칩니다.",
        "Current interpretation has multiple strong standardized components.": "현재 해석에 힘을 보태는 강한 표준화 움직임이 여러 개 있습니다.",
        "Weak components outnumber strong components.": "강한 근거보다 약한 구성요소가 더 많습니다.",
        "Latest daily candle is recent.": "최근 일봉 데이터가 비교적 최신입니다.",
        "Historical validation has no usable point-in-time records.": "과거 점검에 쓸 PIT 기록이 부족합니다.",
        "Current scenario has a useful directional historical sample.": "현재 시나리오와 비슷한 과거 방향성 표본이 충분합니다.",
        "Current scenario directional historical sample is too small.": "현재 시나리오의 방향성 과거 표본이 너무 작습니다.",
        "Current scenario 5D hit rate is above a basic consistency threshold.": "현재 시나리오의 5D 과거 일관성이 기본 기준보다 높습니다.",
        "Current scenario 5D hit rate is below a basic consistency threshold.": "현재 시나리오의 5D 과거 일관성이 기본 기준보다 낮습니다.",
        "Current scenario is not forced into a directional hit-rate rule.": "현재 시나리오는 방향성 적중률 규칙에 억지로 넣지 않습니다.",
        "Historical validation could not run.": "과거 점검을 실행하지 못했습니다.",
    }
    return translations.get(text, text or "근거 점검 대기")


def _futures_warning_label(value: Any) -> str:
    text = str(value or "")
    if text.startswith("Latest daily futures candle is ") and text.endswith(" days old."):
        age = text.removeprefix("Latest daily futures candle is ").removesuffix(" days old.")
        return f"최근 선물 일봉 기준이 {age}일 전입니다. 최신 해석이 필요한 경우 일봉 매크로 갱신을 확인하세요."
    if "futures symbols have no daily rows" in text:
        return text.replace("futures symbols have no daily rows", "개 선물의 일봉 데이터가 없습니다")
    if "symbols have less than 6 months of daily data" in text:
        return "일부 선물의 일봉 이력이 6개월 미만입니다. 표준화 움직임은 보수적으로 해석하세요."
    return text


def _macro_caution_label(value: Any) -> str:
    text = str(value or "")
    translations = {
        "Historical validation is an ex-post consistency check, not a prediction guarantee.": "과거 점검은 사후 일관성 확인이며 예측 보장이 아닙니다.",
        "Futures targets use stored yfinance continuous futures rows when available.": "선물 대상은 저장된 yfinance 연속 선물 row가 있으면 그것을 사용합니다.",
        "ETF proxy targets are labeled separately and do not prove futures contract performance.": "ETF proxy 대상은 별도로 표시되며 선물 계약 성과를 증명하지 않습니다.",
        "yfinance continuous futures can differ from exchange roll and maturity behavior.": "yfinance 연속 선물은 거래소 roll / 만기 구조와 다를 수 있습니다.",
        "Historical validation sample is small; confidence should be downgraded.": "과거 점검 표본이 작아 근거 강도는 낮춰 읽어야 합니다.",
    }
    if text.startswith("Historical validation has less than ") and text.endswith(" years of stored daily futures history."):
        years = text.removeprefix("Historical validation has less than ").removesuffix(" years of stored daily futures history.")
        return f"저장된 일봉 선물 이력이 {years}년 미만이라 과거 점검 표본을 보수적으로 읽어야 합니다."
    if text.startswith("Historical validation could not run:"):
        return f"과거 점검을 실행하지 못했습니다: {text.split(':', 1)[1].strip()}"
    return translations.get(text, text)


def _render_futures_section_header(title: str, detail: str | None = None) -> None:
    st.markdown(
        f"""
        <div class="ov-futures-section-head">
          <div class="ov-futures-section-title">{escape(title)}</div>
          <div class="ov-futures-section-meta">{escape(detail or "")}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _format_macro_score(value: Any) -> str:
    try:
        if value is None or pd.isna(value):
            return "-"
        return f"{float(value):+.0f}"
    except (TypeError, ValueError):
        return "-"


def _macro_score_cards(scores: Any) -> list[dict[str, Any]]:
    if not isinstance(scores, pd.DataFrame) or scores.empty:
        return [{"title": "Macro Scores", "value": "-", "detail": "waiting for daily futures data", "tone": "neutral"}]
    cards: list[dict[str, Any]] = []
    for _, row in scores.iterrows():
        cards.append(
            {
                "title": str(row.get("Score") or "-"),
                "value": _format_macro_score(row.get("Value")),
                "detail": f"{row.get('Direction') or '-'} · {row.get('Coverage') or '-'}",
                "tone": str(row.get("Tone") or "neutral"),
            }
        )
    return cards


def _macro_score_badges(scores: Any) -> list[dict[str, Any]]:
    if not isinstance(scores, pd.DataFrame) or scores.empty:
        return [{"label": "매크로", "value": "-", "tone": "neutral"}]
    badges: list[dict[str, Any]] = []
    for _, row in scores.iterrows():
        score_name = str(row.get("Score") or "-")
        badges.append(
            {
                "label": MACRO_SCORE_LABELS.get(score_name, score_name.replace(" Score", "")),
                "value": _format_macro_score(row.get("Value")),
                "tone": str(row.get("Tone") or "neutral"),
            }
        )
    return badges


def _format_macro_percent(value: Any, *, digits: int = 1) -> str:
    try:
        if value is None or pd.isna(value):
            return "-"
        return f"{float(value):.{digits}f}%"
    except (TypeError, ValueError):
        return "-"


def _macro_support_items(macro: dict[str, Any]) -> list[dict[str, Any]]:
    confidence = dict(macro.get("confidence") or {})
    validation = dict(macro.get("validation") or {})
    validation_coverage = dict(validation.get("coverage") or {})
    current_metrics = dict(validation.get("current_scenario_metrics") or {})
    sample = confidence.get("sample_size")
    if sample is None:
        sample = current_metrics.get("Sample 5D")
    sample = _validation_int_value(sample)
    occurrence_count = confidence.get("occurrence_count")
    if occurrence_count is None:
        occurrence_count = current_metrics.get("Occurrence Count")
    occurrence_count = _validation_int_value(occurrence_count)
    hit_rate = confidence.get("hit_rate_5d")
    if hit_rate is None:
        hit_rate = current_metrics.get("Hit Rate 5D %")
    hit_applicable = bool(confidence.get("hit_applicable"))
    validation_dates = _validation_int_value(validation_coverage.get("validation_dates"))
    span = validation_coverage.get("history_span_years")
    return [
        {
            "label": "근거 강도",
            "value": _macro_confidence_short_label(confidence.get("label")),
            "detail": _macro_confidence_reason_label((list(confidence.get("reasons") or [])[:1] or [""])[0]),
            "tone": confidence.get("tone") or "warning",
        },
        {
            "label": "과거 점검",
            "value": _macro_validation_status_label(validation.get("status")),
            "detail": f"점검 기준 {validation_dates:,}개 · {span or '-'}년",
            "tone": "positive" if validation.get("status") == "OK" else "warning",
        },
        {
            "label": "유사 구간",
            "value": sample or occurrence_count or 0,
            "detail": f"5D 적중 {_format_macro_percent(hit_rate)}" if hit_applicable else "발생 횟수, 적중률 n/a",
            "tone": "positive" if int(sample or occurrence_count or 0) >= 60 else "warning",
        },
    ]


def _futures_market_brief_model(macro: dict[str, Any]) -> dict[str, Any]:
    coverage = dict(macro.get("coverage") or {})
    summary = dict(macro.get("summary") or {})
    sentences = [str(sentence) for sentence in macro.get("summary_sentences") or [] if str(sentence).strip()]
    evidence_chips = [
        _macro_evidence_summary_label(item)
        for item in macro.get("evidence") or []
        if str(item).strip()
    ]
    support_items = _macro_support_items(macro)
    support_items.append(
        {
            "label": "자료 기준",
            "value": f"{coverage.get('standardized_count') or 0}/{coverage.get('symbol_count') or 0}개",
            "detail": f"CME/yfinance 일봉 세션 기준일 {_snapshot_value(coverage.get('latest_daily_date'))}",
            "tone": "neutral",
        }
    )
    return {
        "eyebrow": "오늘 기준 시장 브리프",
        "scenario": str(summary.get("scenario") or "시장 해석 대기"),
        "sub_scenario": str(summary.get("sub_scenario") or ""),
        "regime_hint": str(summary.get("regime_hint") or ""),
        "mixed_reason": str(summary.get("mixed_reason") or ""),
        "sentence": sentences[0] if sentences else "저장된 일봉 선물 데이터로 시장 흐름을 해석합니다.",
        "support_items": support_items,
        "evidence_chips": evidence_chips[:4],
    }


def _render_futures_market_brief(macro: dict[str, Any]) -> None:
    model = _futures_market_brief_model(macro)
    support_html: list[str] = []
    for item in model["support_items"]:
        tone_color = _overview_tone_color(str(item.get("tone") or "neutral"))
        support_html.append(
            f'<div class="ov-futures-brief-support-item" style="--ov-brief-tone:{tone_color};">'
            f'<div class="ov-futures-brief-support-label">{escape(str(item.get("label") or "-"))}</div>'
            f'<div class="ov-futures-brief-support-value">{escape(str(item.get("value") or "-"))}</div>'
            f'<div class="ov-futures-brief-support-detail">{escape(str(item.get("detail") or ""))}</div>'
            "</div>"
        )
    evidence_html = "".join(
        f'<span class="ov-futures-brief-evidence-chip">{escape(str(chip))}</span>'
        for chip in model["evidence_chips"]
    )
    if not evidence_html:
        evidence_html = '<span class="ov-futures-brief-evidence-chip">상세 근거는 아래 disclosure에서 확인</span>'
    subscenario_text = " · ".join(
        item for item in [str(model.get("sub_scenario") or ""), str(model.get("regime_hint") or "")] if item
    )
    subscenario_html = f'<div class="ov-futures-brief-subscenario">{escape(subscenario_text)}</div>' if subscenario_text else ""
    mixed_reason = str(model.get("mixed_reason") or "").strip()
    mixed_reason_html = f'<div class="ov-futures-brief-mixed-reason">{escape(mixed_reason)}</div>' if mixed_reason else ""
    st.markdown(
        f"""
        <div class="ov-futures-brief">
          <div class="ov-futures-brief-main">
            <div class="ov-futures-brief-eyebrow">{escape(str(model["eyebrow"]))}</div>
            <div class="ov-futures-brief-scenario">{escape(str(model["scenario"]))}</div>
            {subscenario_html}
            {mixed_reason_html}
            <div class="ov-futures-brief-sentence">{escape(str(model["sentence"]))}</div>
            <div class="ov-futures-brief-evidence">{evidence_html}</div>
          </div>
          <div class="ov-futures-brief-support">{"".join(support_html)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _macro_weekly_value_float(value: Any) -> float:
    try:
        text = str(value or "0").replace("%", "").replace(",", "").strip()
        if text.startswith("+"):
            text = text[1:]
        return float(text)
    except (TypeError, ValueError):
        return 0.0


def _futures_weekly_flow_model(weekly_context: dict[str, Any]) -> dict[str, Any]:
    cards = [dict(card) for card in weekly_context.get("cards") or []]
    ranked = sorted(cards, key=lambda card: abs(_macro_weekly_value_float(card.get("value"))), reverse=True)
    driver = ranked[0] if ranked else {}
    supporting = [card for card in cards if str(card.get("tone") or "neutral") == "positive"]
    tempering = [card for card in cards if str(card.get("tone") or "neutral") in {"danger", "warning"}]
    neutral = [card for card in cards if str(card.get("tone") or "neutral") == "neutral"]
    return {
        "title": "최근 1주 흐름",
        "basis": str(weekly_context.get("basis") or "저장된 1D 선물 OHLCV의 최근 5거래일 변화율"),
        "summary": str(weekly_context.get("summary") or ""),
        "driver": driver,
        "supporting": supporting,
        "tempering": tempering,
        "neutral": neutral,
    }


def _render_weekly_macro_context(weekly_context: dict[str, Any]) -> None:
    model = _futures_weekly_flow_model(weekly_context)
    if not model["driver"]:
        return
    driver = dict(model["driver"])
    driver_tone = _overview_tone_color(str(driver.get("tone") or "neutral"))

    def weekly_item_html(item: dict[str, Any]) -> str:
        tone_color = _overview_tone_color(str(item.get("tone") or "neutral"))
        return (
            f'<div class="ov-futures-week-lane-item" style="--ov-week-tone:{tone_color};">'
            f'<span class="ov-futures-week-lane-label">{escape(str(item.get("label") or "-"))}</span>'
            f'<span class="ov-futures-week-lane-value">{escape(str(item.get("value") or "-"))}</span>'
            f'<span class="ov-futures-week-lane-detail">{escape(str(item.get("detail") or item.get("meaning") or ""))}</span>'
            "</div>"
        )

    supporting_html = "".join(weekly_item_html(item) for item in model["supporting"][:3])
    tempering_html = "".join(weekly_item_html(item) for item in model["tempering"][:3])
    if not supporting_html:
        supporting_html = '<div class="ov-futures-week-lane-empty">뚜렷한 지지 흐름 없음</div>'
    if not tempering_html:
        tempering_html = '<div class="ov-futures-week-lane-empty">뚜렷한 완화/충돌 흐름 없음</div>'
    st.markdown(
        f"""
        <div class="ov-futures-week-flow">
          <div class="ov-futures-week-flow-head">
            <div>
              <div class="ov-futures-week-flow-title">{escape(str(model["title"]))}</div>
              <div class="ov-futures-week-flow-basis">{escape(str(model["basis"]))}</div>
            </div>
            <div class="ov-futures-week-driver" style="--ov-week-tone:{driver_tone};">
              <span>{escape(str(driver.get("label") or "-"))}</span>
              <strong>{escape(str(driver.get("value") or "-"))}</strong>
            </div>
          </div>
          <div class="ov-futures-week-summary">{escape(str(model["summary"]))}</div>
          <div class="ov-futures-week-lanes">
            <div class="ov-futures-week-lane">
              <div class="ov-futures-week-lane-title">오늘 해석을 지지</div>
              {supporting_html}
            </div>
            <div class="ov-futures-week-lane">
              <div class="ov-futures-week-lane-title">주의해서 볼 흐름</div>
              {tempering_html}
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _macro_score_tone(row: pd.Series) -> str:
    tone = str(row.get("Tone") or "").strip()
    if tone and tone != "neutral":
        return tone
    try:
        value = float(row.get("Value"))
    except (TypeError, ValueError):
        return "neutral"
    if value > 0:
        return "positive"
    if value < 0:
        return "danger"
    return "neutral"


def _render_macro_score_lane(scores: Any) -> None:
    badges = _macro_score_badges(scores)
    if isinstance(scores, pd.DataFrame) and not scores.empty:
        score_rows = [(badge, _macro_score_tone(row)) for badge, (_, row) in zip(badges, scores.iterrows(), strict=False)]
    else:
        score_rows = [(badge, str(badge.get("tone") or "neutral")) for badge in badges]
    html_items: list[str] = []
    for badge, tone in score_rows:
        tone_color = _overview_tone_color(tone)
        html_items.append(
            f'<span class="ov-futures-score-chip" style="--ov-chip-tone:{tone_color};">'
            f'<span class="ov-futures-score-label">{escape(str(badge.get("label") or "-"))}</span>'
            f'<span class="ov-futures-score-value">{escape(str(badge.get("value") or "-"))}</span>'
            "</span>"
        )
    st.markdown(f'<div class="ov-futures-score-lane">{"".join(html_items)}</div>', unsafe_allow_html=True)


def _render_macro_evidence_reading(sections: list[dict[str, Any]]) -> None:
    if not sections:
        st.info("해석 가능한 macro evidence가 아직 없습니다.")
        return
    by_key = {str(section.get("key") or ""): section for section in sections}
    summary = " · ".join(
        [
            f"강한 근거 {int(dict(by_key.get('strong') or {}).get('count') or 0)}개",
            f"약한 근거 {int(dict(by_key.get('weak') or {}).get('count') or 0)}개",
            f"충돌 {int(dict(by_key.get('conflicting') or {}).get('count') or 0)}개",
            f"자료 부족 {int(dict(by_key.get('missing') or {}).get('count') or 0)}개",
        ]
    )
    section_html: list[str] = []
    for section in sections:
        items = list(section.get("items") or [])
        item_html: list[str] = []
        if not items:
            item_html.append(
                f'<div class="ov-futures-evidence-empty">{escape(str(section.get("empty_label") or "해당 항목 없음"))}</div>'
            )
        for item in items[:4]:
            contribution = str(item.get("contribution_z") or "-")
            impact = str(item.get("impact_label") or "")
            meta_parts = []
            if contribution and contribution != "-":
                meta_parts.append(f"기여도 {contribution}")
            if impact:
                meta_parts.append(impact)
            item_html.append(
                '<div class="ov-futures-evidence-item">'
                f'<div class="ov-futures-evidence-item-title">{escape(str(item.get("title") or "-"))}</div>'
                f'<div class="ov-futures-evidence-item-meta">{escape(" · ".join(meta_parts) or str(item.get("detail") or ""))}</div>'
                f'<div class="ov-futures-evidence-item-meaning">{escape(str(item.get("meaning") or ""))}</div>'
                "</div>"
            )
        section_html.append(
            '<div class="ov-futures-evidence-section">'
            '<div class="ov-futures-evidence-section-head">'
            f'<span>{escape(str(section.get("label") or "-"))}</span>'
            f'<strong>{int(section.get("count") or 0)}개</strong>'
            "</div>"
            f'<div class="ov-futures-evidence-description">{escape(str(section.get("description") or ""))}</div>'
            f'{"".join(item_html)}'
            "</div>"
        )
    st.markdown(
        f"""
        <div class="ov-futures-evidence-state">
          <div class="ov-futures-evidence-title">현재 근거 상태</div>
          <div class="ov-futures-evidence-summary">{escape(summary)}</div>
          <div class="ov-futures-evidence-grid">{"".join(section_html)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_macro_validation_summary(validation: dict[str, Any], *, confidence_label: str | None = None) -> None:
    summary = build_current_scenario_validation_summary(validation, confidence_label=confidence_label)
    if not summary:
        st.info("현재 해석 기준 과거 일관성 요약이 아직 없습니다.")
        return
    metric_html = "".join(
        '<div class="ov-futures-validation-metric">'
        f'<span>{escape(str(item.get("label") or "-"))}</span>'
        f'<strong>{escape(str(item.get("value") or "-"))}</strong>'
        "</div>"
        for item in list(summary.get("metrics") or [])[:3]
    )
    occurrence = dict(summary.get("occurrence") or {})
    st.markdown(
        f"""
        <div class="ov-futures-validation-summary">
          <div class="ov-futures-validation-head">
            <div>
              <div class="ov-futures-validation-title">{escape(str(summary.get("title") or "현재 해석의 과거 일관성"))}</div>
              <div class="ov-futures-validation-scenario">현재 시나리오: {escape(str(summary.get("scenario") or "-"))}</div>
            </div>
            <div class="ov-futures-validation-occurrence">
              <span>{escape(str(occurrence.get("label") or "-"))}</span>
              <strong>{escape(str(occurrence.get("value") or "-"))}</strong>
            </div>
          </div>
          <div class="ov-futures-validation-coverage">점검 범위: {escape(str(summary.get("coverage") or "-"))}</div>
          <div class="ov-futures-validation-metrics">{metric_html}</div>
          <div class="ov-futures-validation-copy">{escape(str(summary.get("interpretation") or ""))}</div>
          <div class="ov-futures-validation-effect">{escape(str(summary.get("confidence_effect") or ""))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_macro_validation_raw_tables(validation: dict[str, Any]) -> None:
    scenario_summary = validation.get("scenario_summary")
    if isinstance(scenario_summary, pd.DataFrame) and not scenario_summary.empty:
        preferred_cols = [
            "Scenario",
            "Occurrence Count",
            "Target Family",
            "Sample 1D",
            "Mean 1D %",
            "Hit Rate 1D %",
            "Sample 5D",
            "Mean 5D %",
            "Hit Rate 5D %",
            "Sample 20D",
            "Mean 20D %",
            "Hit Rate 20D %",
            "Max Adverse 5D %",
        ]
        with st.expander("과거 시나리오 표본", expanded=False):
            st.dataframe(
                scenario_summary[[col for col in preferred_cols if col in scenario_summary.columns]],
                width="stretch",
                hide_index=True,
            )
    relationships = validation.get("relationships")
    threshold_sensitivity = validation.get("threshold_sensitivity")
    if isinstance(relationships, pd.DataFrame) and not relationships.empty:
        with st.expander("점수-이후수익 관계", expanded=False):
            st.dataframe(relationships, width="stretch", hide_index=True)
    if isinstance(threshold_sensitivity, pd.DataFrame) and not threshold_sensitivity.empty:
        with st.expander("기준값 민감도", expanded=False):
            st.dataframe(threshold_sensitivity, width="stretch", hide_index=True)


def _render_futures_raw_table_map(*, validation_available: bool) -> None:
    steps = [
        ("매크로 컨텍스트", "현재 점수 원본 · 점수 구성 기여"),
        ("최근 흐름", "선물 일봉 변화"),
        ("과거 점검", "과거 시나리오 표본" if validation_available else "과거 점검을 불러오면 표시"),
        ("검산 순서", "현재 점수 -> 구성 기여 -> 선물 일봉 변화 -> 과거 표본"),
    ]
    items = "".join(
        "<div>"
        f"<span>{escape(title)}</span>"
        f"<strong>{escape(detail)}</strong>"
        "</div>"
        for title, detail in steps
    )
    st.markdown(
        f"""
        <div class="ov-futures-raw-map">
          <div class="ov-futures-raw-map-title">화면 섹션별 원본 연결</div>
          <div class="ov-futures-raw-map-flow">이 영역은 상단 세 섹션의 판단을 검산하는 원본 데이터입니다.</div>
          <div class="ov-futures-raw-map-grid">{items}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_futures_macro_data_management(macro: dict[str, Any]) -> None:
    coverage = dict(macro.get("coverage") or {})
    coverage_label = _futures_daily_coverage_label(coverage)
    latest_daily = _snapshot_value(coverage.get("latest_daily_date"))
    raw_rows = int(coverage.get("raw_rows") or 0)
    st.markdown(
        f"""
        <div class="ov-futures-data-management">
          <div class="ov-futures-data-management-title">자료 관리</div>
          <div class="ov-futures-data-management-grid">
            <div><span>CME/yfinance 일봉 세션 기준일</span><strong>{escape(latest_daily)}</strong></div>
            <div><span>daily coverage</span><strong>{escape(coverage_label)}</strong></div>
            <div><span>저장 row</span><strong>{raw_rows:,}</strong></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _render_market_job_result("overview_futures_daily_ohlcv_result")


def _render_futures_macro_raw_tables(
    *,
    scores: Any,
    components: Any,
    symbols: Any,
    validation: dict[str, Any],
    cautions: list[str],
) -> None:
    _render_futures_section_header("원본 데이터", "매크로 컨텍스트 · 최근 흐름 · 과거 점검의 계산 추적")
    _render_futures_raw_table_map(validation_available=bool(validation))
    if isinstance(scores, pd.DataFrame) and not scores.empty:
        with st.expander("현재 점수 원본", expanded=False):
            st.dataframe(scores.drop(columns=["Tone"], errors="ignore"), width="stretch", hide_index=True)
    if isinstance(components, pd.DataFrame) and not components.empty:
        with st.expander("점수 구성 기여", expanded=False):
            st.dataframe(components, width="stretch", hide_index=True)
    if isinstance(symbols, pd.DataFrame) and not symbols.empty:
        with st.expander("선물 일봉 변화", expanded=False):
            st.dataframe(symbols, width="stretch", hide_index=True)
    _render_macro_validation_raw_tables(validation)
    if cautions:
        with st.expander("해석 주의점", expanded=False):
            for caution in list(dict.fromkeys(cautions)):
                st.caption(caution)


def _render_futures_macro_refresh_controls(*, section_detail: str) -> None:
    refreshed_at = st.session_state.get("overview_futures_macro_daily_refreshed_at")
    reloaded_at = st.session_state.get("overview_futures_macro_reloaded_at")
    status_text = refreshed_at or reloaded_at
    status_label = "최근 일봉 갱신" if refreshed_at else "최근 다시 읽기"
    status_detail = ""
    if status_text:
        status_detail = f'<div class="ov-futures-macro-action-detail">{escape(status_label)}: {escape(str(status_text))}</div>'
    cols = st.columns([1, 0.16, 0.16], gap="small", vertical_alignment="center")
    cols[0].markdown(
        f"""
        <div class="ov-futures-macro-action-copy">
          <div class="ov-futures-macro-action-title">매크로 컨텍스트</div>
          <div class="ov-futures-macro-action-meta">{escape(section_detail)}</div>
          {status_detail}
        </div>
        """,
        unsafe_allow_html=True,
    )
    if cols[1].button(
        "일봉 갱신",
        key="overview_futures_macro_tab_daily_refresh",
        use_container_width=True,
        help="저장된 주요 선물 5년 1D OHLCV를 다시 수집하고 매크로 snapshot cache를 비웁니다.",
    ):
        with st.spinner("선물 5년 일봉을 yfinance에서 수집하는 중입니다..."):
            _refresh_futures_macro_daily_for_ui()
        st.rerun()
    if cols[2].button(
        "다시 읽기",
        key="overview_futures_macro_tab_reload",
        use_container_width=True,
        help="수집 job은 실행하지 않고 현재 DB 기준으로 매크로 snapshot cache만 비운 뒤 다시 읽습니다.",
    ):
        _reload_futures_macro_snapshot_for_ui()
        st.rerun()
    st.markdown('<div class="ov-futures-macro-action-rule"></div>', unsafe_allow_html=True)


def _render_futures_macro_validation_controls(
    macro: dict[str, Any],
    *,
    validation: dict[str, Any],
    loaded_at: str,
) -> None:
    state = "불러옴" if validation else "대기"
    detail = (
        f"과거 점검 기준: {loaded_at}"
        if validation and loaded_at
        else "탭 첫 진입은 현재 매크로만 빠르게 읽고, 과거 점검은 필요할 때 계산합니다."
    )
    cols = st.columns([1, 0.22], gap="small", vertical_alignment="center")
    cols[0].markdown(
        f"""
        <div class="ov-futures-validation-action-copy">
          <div class="ov-futures-validation-action-title">과거 점검</div>
          <div class="ov-futures-validation-action-meta">{escape(state)} · {escape(detail)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if cols[1].button(
        "과거 점검 불러오기",
        key="overview_futures_macro_validation_load",
        use_container_width=True,
        help="저장된 선물 일봉과 proxy 가격으로 historical validation을 계산합니다. 첫 실행은 수 초 걸릴 수 있습니다.",
    ):
        with st.spinner("과거 점검을 계산하는 중입니다..."):
            _load_futures_macro_validation_for_session(macro)
        st.rerun()


def _render_futures_pattern_outlook_fallback(pattern_outlook: dict[str, Any]) -> None:
    pattern = dict(pattern_outlook.get("current_pattern") or {})
    st.markdown(f"#### {_display_text(pattern.get('regime_label'), '현재 체제 자료 부족')}")
    st.caption(
        f"{_display_text(pattern.get('transition_label'), '자료 부족')} · "
        f"{_display_text(pattern.get('summary'), '다중 기간 패턴을 계산할 자료가 부족합니다.')}"
    )
    for horizon in list(pattern_outlook.get("horizons") or []):
        label = _display_text(horizon.get("label"), "조건부 전망")
        status = _display_text(horizon.get("estimate_status"), "UNAVAILABLE")
        edge = _display_text(horizon.get("edge_label"), "방향 우위 미확인")
        st.markdown(f"**{label} · {status}** — {edge}")
        st.caption(_display_text(horizon.get("status_reason"), "검증 근거가 부족합니다."))
    conditions = [str(item) for item in list(pattern.get("change_conditions") or []) if str(item).strip()]
    if conditions:
        st.markdown("**다음 확인 조건**")
        for condition in conditions:
            st.caption(f"- {condition}")


def _render_futures_macro_panel(*, detail_expanded: bool = False) -> None:
    macro = load_overview_futures_macro_snapshot(include_validation=False)
    pattern_outlook = load_overview_futures_macro_pattern_outlook()
    coverage = dict(macro.get("coverage") or {})
    scores = macro.get("scores")
    components = macro.get("score_components")
    symbols = macro.get("symbols")
    react_available = futures_macro_react_component_available()

    if react_available:
        payload = build_futures_macro_react_workbench_payload(
            macro,
            pattern_outlook=pattern_outlook,
        )
        react_event = render_futures_macro_react_workbench(payload, key="overview_futures_macro_workbench")
        _handle_futures_macro_react_event(react_event, macro)
    else:
        _render_futures_macro_refresh_controls(
            section_detail=(
                f"일봉 {coverage.get('standardized_count') or 0}/{coverage.get('symbol_count') or 0}개"
                f" · 기준일 {_snapshot_value(coverage.get('latest_daily_date'))} · CME/yfinance 일봉 세션 기준"
            ),
        )
        _render_futures_market_brief(macro)
        _render_futures_pattern_outlook_fallback(pattern_outlook)
    warnings = list(macro.get("warnings") or [])
    if warnings:
        _render_snapshot_warnings({"warnings": [_futures_warning_label(warning) for warning in warnings]})

    cautions = [_macro_caution_label(item) for item in macro.get("cautions") or [] if str(item).strip()]
    cautions.extend(_macro_caution_label(item) for item in pattern_outlook.get("limitations") or [] if str(item).strip())
    with st.expander("원본 데이터 / 계산 추적", expanded=detail_expanded):
        if react_available:
            st.caption("이 영역은 상단 세 섹션의 판단을 검산하는 원본 데이터입니다. 자료 기준, 점수 계산표, 선물 일봉 변화, 과거 표본을 순서대로 확인합니다.")
        else:
            _render_macro_evidence_reading(list(macro.get("evidence_reading") or []))
        _render_futures_macro_data_management(macro)
        _render_futures_macro_raw_tables(
            scores=scores,
            components=components,
            symbols=symbols,
            validation={},
            cautions=cautions,
        )


def render_futures_macro_fragment(*, detail_expanded: bool) -> None:
    @st.fragment
    def futures_macro_context_fragment() -> None:
        _render_futures_macro_panel(detail_expanded=detail_expanded)

    futures_macro_context_fragment()
