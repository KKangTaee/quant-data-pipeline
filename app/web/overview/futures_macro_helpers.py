from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from math import isfinite
from typing import Any

import pandas as pd
import streamlit as st

from finance.data.futures_market import (
    DEFAULT_CORE_FUTURES_SYMBOLS,
)

from app.jobs.overview_actions import (
    record_overview_action_result,
    run_overview_futures_daily_ohlcv,
)
from app.services.futures_macro_thermometer import (
    SCORE_DEFINITIONS,
    SIGNAL_Z_THRESHOLD,
    clear_overview_futures_macro_snapshot_cache,
)
from app.services.futures_macro_intraday import (
    load_overview_futures_macro_intraday_observation,
)
from app.services.futures_macro_pattern_validation import (
    clear_futures_macro_pattern_validation_cache,
)
from app.services.futures_macro_snapshot import (
    load_overview_futures_macro_materialized_snapshot,
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
PATTERN_CORE_FAMILY_DEFINITIONS = (
    ("risk_on", "위험선호"),
    ("rate_pressure", "금리 부담"),
    ("dollar_pressure", "달러 압력"),
    ("inflation_pressure", "물가 압력"),
)
PATTERN_CONFIRMATION_FAMILY_DEFINITIONS = (
    ("growth", "성장 기대"),
    ("safe_haven", "방어 수요"),
)
PATTERN_RISK_ALIGNMENT_SIGN = {
    "risk_on": 1.0,
    "rate_pressure": -1.0,
    "dollar_pressure": -1.0,
    "inflation_pressure": -1.0,
}
PATTERN_FAMILY_POLARITY_COPY = {
    "risk_on": ("위험선호 강화", "위험선호 약화", "위험선호 중립"),
    "growth": ("성장 기대 강화", "성장 기대 약화", "성장 기대 중립"),
    "rate_pressure": ("금리 부담 확대", "금리 부담 완화", "금리 부담 중립"),
    "dollar_pressure": ("달러 압력 확대", "달러 압력 완화", "달러 압력 중립"),
    "safe_haven": ("방어 수요 강화", "방어 수요 약화", "방어 수요 중립"),
    "inflation_pressure": ("물가 압력 확대", "물가 압력 완화", "물가 압력 중립"),
}
PATTERN_CONFIRMATION_RISK_ALIGNMENT_SIGN = {
    "growth": 1.0,
    "safe_haven": -1.0,
}
PATTERN_FAMILY_BASIS_COPY = {
    "risk_on": "ES/NQ/YM/RTY",
    "growth": "RTY/HG/CL/6A",
    "rate_pressure": "ZN/ZB",
    "dollar_pressure": "주요 FX",
    "safe_haven": "GC/ZN/ZB/6J",
    "inflation_pressure": "CL/HG/NG",
}
PATTERN_FAMILY_HEADLINE_COPY = {
    ("risk_on", 1): "주가지수 위험선호 강화",
    ("risk_on", -1): "주가지수 위험선호 약화",
    ("rate_pressure", 1): "국채선물 기반 금리 부담 확대",
    ("rate_pressure", -1): "국채선물 기반 금리 부담 완화",
    ("dollar_pressure", 1): "주요 통화선물 기반 달러 압력 확대",
    ("dollar_pressure", -1): "주요 통화선물 기반 달러 압력 완화",
    ("inflation_pressure", 1): "원자재선물 기반 물가 압력 확대",
    ("inflation_pressure", -1): "원자재선물 기반 물가 압력 완화",
}
PATTERN_FAMILY_SCENARIO_COPY = {
    ("risk_on", 1): {
        "summary": "위험선호 강화가 이어지면 주가지수와 경기민감 자산의 우호적 환경이 유지될 수 있습니다.",
        "continuation": "1D와 5D에서 위험선호 강화가 함께 유지되고 성장 기대가 약해지지 않을 때",
        "invalidation": "1D 위험선호가 약화로 반전하거나 5D 위험선호 강화가 중립권으로 낮아질 때",
        "sensitive_assets": ["주가지수", "성장주", "경기민감 자산"],
    },
    ("risk_on", -1): {
        "summary": "위험선호 약화가 이어지면 주가지수와 경기민감 자산의 부담이 유지될 수 있습니다.",
        "continuation": "1D와 5D에서 위험선호 약화가 함께 유지되고 달러·물가 압력이 약해지지 않을 때",
        "invalidation": "1D 위험선호가 강화로 반전하거나 5D 위험선호 약화가 중립권으로 낮아질 때",
        "sensitive_assets": ["주가지수", "성장주", "경기민감 자산"],
    },
    ("rate_pressure", 1): {
        "summary": "금리 부담 확대가 이어지면 장기채와 성장주의 변동성 부담이 커질 수 있습니다.",
        "continuation": "1D와 5D에서 금리 부담 확대가 함께 유지되고 달러 또는 물가 압력이 동반될 때",
        "invalidation": "1D 금리 부담이 완화로 반전하거나 국채선물 약세가 5D 중립권으로 낮아질 때",
        "sensitive_assets": ["미 국채", "성장주", "금"],
    },
    ("rate_pressure", -1): {
        "summary": "금리 부담 완화가 이어지면 장기채와 금리 민감 자산의 압력이 낮아질 수 있습니다.",
        "continuation": "1D와 5D에서 금리 부담 완화가 함께 유지되고 달러 압력이 확대되지 않을 때",
        "invalidation": "1D 금리 부담이 확대로 반전하거나 국채선물 강세가 5D 중립권으로 낮아질 때",
        "sensitive_assets": ["미 국채", "성장주", "금리 민감 자산"],
    },
    ("dollar_pressure", 1): {
        "summary": "달러 압력 확대가 이어지면 원자재와 달러 민감 위험자산의 부담이 커질 수 있습니다.",
        "continuation": "1D와 5D에서 달러 압력 확대가 함께 유지되고 금리 부담 또는 위험선호 약화가 동반될 때",
        "invalidation": "1D 달러 압력이 완화로 반전하거나 주요 FX 약세가 5D 중립권으로 낮아질 때",
        "sensitive_assets": ["달러 민감 자산", "원자재", "신흥국 위험자산"],
    },
    ("dollar_pressure", -1): {
        "summary": "달러 압력 완화가 이어지면 원자재와 비달러 위험자산의 부담이 낮아질 수 있습니다.",
        "continuation": "1D와 5D에서 달러 압력 완화가 함께 유지되고 위험선호가 약화되지 않을 때",
        "invalidation": "1D 달러 압력이 확대로 반전하거나 주요 FX 강세가 5D 중립권으로 낮아질 때",
        "sensitive_assets": ["비달러 자산", "원자재", "신흥국 위험자산"],
    },
    ("inflation_pressure", 1): {
        "summary": "물가 압력 확대가 이어지면 원자재와 금리 민감 자산의 변동성이 커질 수 있습니다.",
        "continuation": "1D와 5D에서 물가 압력 확대가 함께 유지되고 국채선물 약세가 동반될 때",
        "invalidation": "1D 물가 압력이 완화로 반전하거나 원자재 강세가 5D 중립권으로 낮아질 때",
        "sensitive_assets": ["원자재", "미 국채", "장기 성장주"],
    },
    ("inflation_pressure", -1): {
        "summary": "물가 압력 완화가 이어지면 원자재발 금리 부담이 낮아질 수 있습니다.",
        "continuation": "1D와 5D에서 물가 압력 완화가 함께 유지되고 금리 부담이 확대되지 않을 때",
        "invalidation": "1D 물가 압력이 확대로 반전하거나 원자재 약세가 5D 중립권으로 낮아질 때",
        "sensitive_assets": ["원자재", "미 국채", "물가 민감 자산"],
    },
}
FUTURES_MACRO_SHARED_CONTEXT_SYMBOLS = ("DX-Y.NYB",)
FUTURES_MACRO_RAW_OBSERVATION_SYMBOLS = ("SI=F",)


def _pattern_observation_status(pattern: dict[str, Any]) -> str:
    """Map stored current-pattern coverage to an observation-only status."""

    status = str(pattern.get("status") or "UNAVAILABLE")
    if status == "READY":
        return "OBSERVED"
    if status in {"PARTIAL", "LIMITED"}:
        return "PARTIAL"
    return "UNAVAILABLE"


def _pattern_direction_value(value: Any, family_key: str) -> dict[str, Any]:
    positive, negative, neutral = PATTERN_FAMILY_POLARITY_COPY[family_key]
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return {
            "label": "자료 부족",
            "semantic_label": "자료 부족",
            "tone": "unavailable",
            "value": None,
        }
    if not isfinite(numeric):
        return {
            "label": "자료 부족",
            "semantic_label": "자료 부족",
            "tone": "unavailable",
            "value": None,
        }
    if numeric >= SIGNAL_Z_THRESHOLD:
        label, semantic_label, tone = "강화", positive, "positive"
    elif numeric <= -SIGNAL_Z_THRESHOLD:
        label, semantic_label, tone = "약화", negative, "negative"
    else:
        label, semantic_label, tone = "중립", neutral, "neutral"
    return {
        "label": label,
        "semantic_label": semantic_label,
        "tone": tone,
        "value": numeric,
    }


def _pattern_family_direction_row(
    families: dict[str, Any],
    family_key: str,
    label: str,
) -> dict[str, Any]:
    family = dict(families.get(family_key) or {})
    return {
        "key": family_key,
        "label": label,
        "one_day": _pattern_direction_value(family.get("one_day"), family_key),
        "five_day": _pattern_direction_value(family.get("five_day"), family_key),
        "twenty_day": _pattern_direction_value(family.get("twenty_day"), family_key),
        "status": str(family.get("status") or "UNAVAILABLE"),
    }


def _material_family_phrases(rows: list[dict[str, Any]], window: str) -> list[str]:
    phrases = []
    for row in rows:
        state = dict(row.get(window) or {})
        if state.get("tone") not in {"positive", "negative"}:
            continue
        phrases.append(
            str(state.get("semantic_label") or f"{row.get('label')} {state.get('label')}")
        )
    return phrases


def _join_korean_phrases(phrases: list[str]) -> str:
    cleaned = [phrase.strip() for phrase in phrases if phrase.strip()]
    if len(cleaned) <= 1:
        return cleaned[0] if cleaned else ""
    if len(cleaned) == 2:
        return f"{cleaned[0]}와 {cleaned[1]}"
    return f"{', '.join(cleaned[:-1])}와 {cleaned[-1]}"


def _pattern_core_alignment_summary(core_rows: list[dict[str, Any]]) -> str:
    phrases = _material_family_phrases(core_rows, "five_day")
    if not phrases:
        return (
            "최근 5거래일 동안 뚜렷하게 강화되거나 약화된 핵심축은 없습니다. "
            "위험선호·금리·달러·물가가 같은 방향으로 모이지 않아 전체 단기 "
            "방향은 중립에 가깝습니다."
        )
    if len(phrases) == 1:
        return (
            f"최근 5거래일에는 {phrases[0]}만 뚜렷합니다. "
            "다른 핵심축이 함께 움직이지 않아 전체 단기 방향이 한쪽으로 "
            "정렬됐다고 보기는 어렵습니다."
        )

    alignment = []
    for row in core_rows:
        state = dict(row.get("five_day") or {})
        value = state.get("value")
        if value is None or abs(float(value)) < SIGNAL_Z_THRESHOLD:
            continue
        sign = PATTERN_RISK_ALIGNMENT_SIGN.get(str(row.get("key")))
        if sign is not None:
            alignment.append(float(value) * sign)
    joined = _join_korean_phrases(phrases)
    if alignment and all(value > 0 for value in alignment):
        return (
            f"최근 5거래일에는 {joined}가 함께 나타났습니다. "
            "핵심축이 위험선호 방향으로 정렬돼 전체 단기 흐름도 같은 방향을 "
            "가리킵니다."
        )
    if alignment and all(value < 0 for value in alignment):
        return (
            f"최근 5거래일에는 {joined}가 함께 나타났습니다. "
            "핵심축이 방어·부담 방향으로 정렬돼 전체 단기 흐름도 같은 방향을 "
            "가리킵니다."
        )
    return (
        f"최근 5거래일에는 {joined}가 함께 나타났지만 서로 가리키는 방향은 "
        "엇갈립니다. 핵심축이 한쪽으로 모이지 않아 전체 단기 방향에는 "
        "뚜렷한 우위가 없습니다."
    )


def _pattern_one_day_change_summary(core_rows: list[dict[str, Any]]) -> str:
    newly_material: list[str] = []
    reversed_rows: list[str] = []
    continuing: list[str] = []
    for row in core_rows:
        one_day = dict(row.get("one_day") or {})
        five_day = dict(row.get("five_day") or {})
        one_tone = str(one_day.get("tone") or "")
        five_tone = str(five_day.get("tone") or "")
        if one_tone not in {"positive", "negative"}:
            continue
        phrase = str(one_day.get("semantic_label") or row.get("label") or "")
        if five_tone not in {"positive", "negative"}:
            newly_material.append(phrase)
        elif one_tone != five_tone:
            reversed_rows.append(phrase)
        else:
            continuing.append(phrase)

    event_count = sum(bool(items) for items in (newly_material, reversed_rows, continuing))
    if event_count == 0:
        return (
            "최근 1거래일에 새로 강화되거나 반전된 핵심축은 없습니다. "
            "최근 5거래일 흐름을 바꿀 만한 새 신호도 나타나지 않았습니다."
        )
    if event_count == 1 and continuing:
        return (
            f"{_join_korean_phrases(continuing)}가 하루 흐름에서도 이어지고 있습니다. "
            "다른 핵심축의 변화는 크지 않아 새로운 방향 전환으로 보기는 "
            "어렵습니다."
        )
    if event_count == 1 and newly_material:
        return (
            f"{_join_korean_phrases(newly_material)}가 최근 1거래일에 새롭게 "
            "두드러졌습니다. 아직 최근 5거래일 방향으로 이어지지 않아 새로운 "
            "단기 방향으로 단정하기는 어렵습니다."
        )
    if event_count == 1 and reversed_rows:
        return (
            f"{_join_korean_phrases(reversed_rows)}가 최근 5거래일 흐름과 반대 "
            "방향으로 움직였습니다. 하루 변화만으로 기존 단기 방향이 바뀌었다고 "
            "보기는 어렵습니다."
        )

    events: list[tuple[str, str]] = []
    if newly_material:
        subject = _join_korean_phrases(newly_material)
        events.append((f"{subject}가 새로 두드러졌고", f"{subject}가 새로 두드러졌습니다"))
    if reversed_rows:
        subject = _join_korean_phrases(reversed_rows)
        events.append(
            (
                f"{subject}가 최근 5거래일과 반대로 움직였고",
                f"{subject}가 최근 5거래일과 반대로 움직였습니다",
            )
        )
    if continuing:
        subject = _join_korean_phrases(continuing)
        events.append(
            (
                f"{subject}가 기존 방향을 이어갔고",
                f"{subject}가 기존 방향을 이어갔습니다",
            )
        )
    observation = ", ".join(event[0] for event in events[:-1])
    if observation:
        observation += f", {events[-1][1]}."
    else:
        observation = f"{events[-1][1]}."
    return (
        f"{observation} 하루 신호가 한 방향으로 모이지 않아 단기 전환 여부는 "
        "아직 불분명합니다."
    )


def _pattern_confirmation_summary(
    core_rows: list[dict[str, Any]],
    confirmation_rows: list[dict[str, Any]],
) -> str:
    core = {str(row.get("key")): row for row in core_rows}
    confirmations = {str(row.get("key")): row for row in confirmation_rows}
    risk_state = dict(core.get("risk_on", {}).get("five_day") or {})
    safe_state = dict(confirmations.get("safe_haven", {}).get("five_day") or {})
    if risk_state.get("tone") == "negative" and safe_state.get("tone") == "negative":
        return "주가지수 약화와 안전자산 약화가 함께 나타나 전형적 방어 정렬은 아닙니다."
    if risk_state.get("tone") == "negative" and safe_state.get("tone") == "positive":
        return "주가지수 약화와 안전자산 강화가 함께 나타나 방어 정렬입니다."
    phrases = _material_family_phrases(confirmation_rows, "five_day")
    if not phrases:
        return "확인 신호가 최근 5거래일 핵심 방향과 뚜렷하게 동조하지 않습니다."
    return f"확인 신호는 {' · '.join(phrases)}입니다."


def _pattern_background_relationship_summary(
    rows: list[dict[str, Any]],
) -> str:
    aligned: list[str] = []
    reversed_rows: list[str] = []
    for row in rows:
        five = dict(row.get("five_day") or {})
        twenty = dict(row.get("twenty_day") or {})
        five_value = five.get("value")
        twenty_value = twenty.get("value")
        if five_value is None or twenty_value is None:
            continue
        if abs(float(five_value)) < SIGNAL_Z_THRESHOLD or abs(float(twenty_value)) < SIGNAL_Z_THRESHOLD:
            continue
        target = aligned if float(five_value) * float(twenty_value) > 0 else reversed_rows
        target.append(
            str(five.get("semantic_label") or row.get("label") or "")
        )
    if reversed_rows and aligned:
        return (
            f"{_join_korean_phrases(aligned)}는 최근 20거래일 배경과 같은 방향으로 "
            f"이어지고, {_join_korean_phrases(reversed_rows)}는 반대로 움직이고 "
            "있습니다. 지속과 반전이 함께 나타나 중기 배경과의 관계는 "
            "혼재합니다."
        )
    if reversed_rows:
        return (
            f"{_join_korean_phrases(reversed_rows)}가 최근 20거래일 배경과 반대 "
            "방향으로 움직이고 있습니다. 단기 흐름이 기존 배경에서 벗어나는 "
            "변화지만, 이것만으로 중기 방향 전환을 확정하기는 어렵습니다."
        )
    if aligned:
        return (
            f"{_join_korean_phrases(aligned)}가 최근 20거래일 배경과 같은 방향으로 "
            "이어지고 있습니다. 다른 핵심축의 지속이나 반전은 뚜렷하지 않아 "
            "중기 흐름 전체가 한 방향으로 굳어진 상태는 아닙니다."
        )
    return (
        "최근 5거래일과 20거래일 사이에 뚜렷하게 이어지거나 반전된 핵심축은 "
        "없습니다. 현재 단기 흐름은 기존 중기 배경과 분명한 관계를 만들지 "
        "못하고 있습니다."
    )


def _futures_macro_calculation_scope(
    macro: dict[str, Any],
    pattern: dict[str, Any],
) -> dict[str, Any]:
    macro_coverage = dict(macro.get("coverage") or {})
    pattern_coverage = dict(pattern.get("coverage") or {})
    direct_symbols = sorted(
        {
            str(symbol)
            for definition in SCORE_DEFINITIONS
            for symbol in definition.members
        }
    )
    return {
        "collected_count": int(
            macro_coverage.get("symbol_count") or len(DEFAULT_CORE_FUTURES_SYMBOLS)
        ),
        "direct_family_input_count": len(direct_symbols),
        "available_family_count": int(
            pattern_coverage.get("available_family_count") or 0
        ),
        "required_family_count": int(
            pattern_coverage.get("required_family_count") or 6
        ),
        "shared_context_symbols": list(FUTURES_MACRO_SHARED_CONTEXT_SYMBOLS),
        "raw_observation_symbols": list(FUTURES_MACRO_RAW_OBSERVATION_SYMBOLS),
    }


def _material_state_sign(row: dict[str, Any], window: str) -> int | None:
    state = dict(row.get(window) or {})
    value = state.get("value")
    if value is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if not isfinite(numeric):
        return None
    if numeric >= SIGNAL_Z_THRESHOLD:
        return 1
    if numeric <= -SIGNAL_Z_THRESHOLD:
        return -1
    return 0


def _repricing_evidence_label(row: dict[str, Any], window: str = "five_day") -> str:
    state = dict(row.get(window) or {})
    family_key = str(row.get("key") or "")
    semantic = str(state.get("semantic_label") or row.get("label") or "자료 부족")
    basis = PATTERN_FAMILY_BASIS_COPY.get(family_key, "선물군")
    return f"{semantic} · {basis} 기반"


def _empty_market_repricing_payload(*, unavailable: bool) -> dict[str, Any]:
    if unavailable:
        return {
            "status": "UNAVAILABLE",
            "confidence_label": "자료 부족",
            "headline": "시장 재가격화를 해석할 관측값이 부족합니다.",
            "interpretation": "네 개 핵심 선물군의 5D 관측이 준비되어야 유력 해석과 반대 근거를 나눌 수 있습니다.",
            "supporting_evidence": [],
            "counter_evidence": [],
            "conditional_scenario": {
                "summary": "현재 자료로는 조건부 시나리오를 만들지 않습니다.",
                "continuation_condition": "핵심 선물군의 5D 관측이 준비될 때",
                "invalidation_condition": "관측 자료가 다시 부족하거나 stale 상태가 될 때",
                "sensitive_assets": [],
            },
        }
    return {
        "status": "LOW_SIGNAL",
        "confidence_label": "뚜렷한 중심축 없음",
        "headline": "뚜렷한 거시 재가격화가 없습니다.",
        "interpretation": "위험선호·금리·달러·물가 가운데 5D 기준으로 평소 변동 범위를 뚜렷하게 벗어난 핵심축이 없습니다.",
        "supporting_evidence": [],
        "counter_evidence": [],
        "conditional_scenario": {
            "summary": "현재는 특정 시나리오보다 관망이 우선입니다.",
            "continuation_condition": "핵심축이 중립권에 머무를 때",
            "invalidation_condition": "한 개 이상의 핵심축이 5D 평소 변동 범위를 뚜렷하게 벗어날 때",
            "sensitive_assets": [],
        },
    }


def _one_day_repricing_shock_payload(
    core_rows: list[dict[str, Any]],
    confirmation_rows: list[dict[str, Any]],
) -> dict[str, Any] | None:
    material_core = [
        row
        for row in core_rows
        if _material_state_sign(row, "one_day") in {-1, 1}
    ]
    if not material_core:
        return None
    leading = max(
        material_core,
        key=lambda row: abs(float(dict(row.get("one_day") or {}).get("value") or 0.0)),
    )
    leading_key = str(leading.get("key") or "")
    leading_sign = int(_material_state_sign(leading, "one_day") or 0)
    leading_risk_sign = leading_sign * PATTERN_RISK_ALIGNMENT_SIGN[leading_key]
    supporting_core: list[dict[str, Any]] = []
    counter_core: list[dict[str, Any]] = []
    for row in material_core:
        family_key = str(row.get("key") or "")
        state_sign = int(_material_state_sign(row, "one_day") or 0)
        normalized = state_sign * PATTERN_RISK_ALIGNMENT_SIGN[family_key]
        target = supporting_core if normalized == leading_risk_sign else counter_core
        target.append(row)

    supporting_confirmation: list[dict[str, Any]] = []
    counter_confirmation: list[dict[str, Any]] = []
    for row in confirmation_rows:
        state_sign = _material_state_sign(row, "one_day")
        family_key = str(row.get("key") or "")
        if state_sign not in {-1, 1}:
            continue
        normalized = int(state_sign) * PATTERN_CONFIRMATION_RISK_ALIGNMENT_SIGN[family_key]
        target = (
            supporting_confirmation
            if normalized == leading_risk_sign
            else counter_confirmation
        )
        target.append(row)

    leading_semantic = str(dict(leading.get("one_day") or {}).get("semantic_label"))
    leading_basis = PATTERN_FAMILY_BASIS_COPY[leading_key]
    support_phrases = [
        str(dict(row.get("one_day") or {}).get("semantic_label"))
        for row in supporting_core
        if row is not leading
    ]
    counter_phrases = [
        str(dict(row.get("one_day") or {}).get("semantic_label"))
        for row in counter_core
    ]
    interpretation = (
        f"{leading_basis} 기반 {leading_semantic}가 1D에서 가장 강하지만 아직 "
        "5D 핵심 방향으로 이어지지 않았습니다."
    )
    if support_phrases and counter_phrases:
        interpretation += (
            f" {_join_korean_phrases(support_phrases)}가 동반하지만 "
            f"{_join_korean_phrases(counter_phrases)}가 반대로 움직여 현재 해석은 "
            "초기 단계입니다."
        )
    elif counter_phrases:
        shock_label = {
            "risk_on": "위험선호 변화",
            "rate_pressure": "금리 충격",
            "dollar_pressure": "달러 충격",
            "inflation_pressure": "물가 충격",
        }[leading_key]
        interpretation += (
            f" {_join_korean_phrases(counter_phrases)}가 반대로 움직여 "
            f"{shock_label} 해석은 초기 단계입니다."
        )
    elif support_phrases:
        interpretation += (
            f" {_join_korean_phrases(support_phrases)}가 같은 방향으로 동반하지만 "
            "지속 여부는 아직 확인되지 않았습니다."
        )
    else:
        interpretation += " 다른 핵심축이 동반하지 않아 단일 충격으로 봅니다."

    scenario = PATTERN_FAMILY_SCENARIO_COPY[(leading_key, leading_sign)]
    return {
        "status": "NEW_SHOCK",
        "confidence_label": "1D 새 충격",
        "headline": f"1D {PATTERN_FAMILY_HEADLINE_COPY[(leading_key, leading_sign)]}가 새로 두드러졌습니다.",
        "interpretation": interpretation,
        "supporting_evidence": [
            _repricing_evidence_label(row, "one_day")
            for row in [*supporting_core, *supporting_confirmation]
        ],
        "counter_evidence": [
            _repricing_evidence_label(row, "one_day")
            for row in [*counter_core, *counter_confirmation]
        ],
        "conditional_scenario": {
            "summary": scenario["summary"],
            "continuation_condition": scenario["continuation"],
            "invalidation_condition": scenario["invalidation"],
            "sensitive_assets": list(scenario["sensitive_assets"]),
        },
    }


def _market_repricing_payload(
    core_rows: list[dict[str, Any]],
    confirmation_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Turn current family observations into one cautious macro repricing hypothesis."""

    finite_core = [
        row
        for row in core_rows
        if _material_state_sign(row, "five_day") is not None
    ]
    if not finite_core:
        return _empty_market_repricing_payload(unavailable=True)
    material_core = [
        row
        for row in finite_core
        if _material_state_sign(row, "five_day") in {-1, 1}
    ]
    if not material_core:
        one_day_shock = _one_day_repricing_shock_payload(
            core_rows,
            confirmation_rows,
        )
        return one_day_shock or _empty_market_repricing_payload(unavailable=False)

    leading = max(
        material_core,
        key=lambda row: abs(float(dict(row.get("five_day") or {}).get("value") or 0.0)),
    )
    leading_key = str(leading.get("key") or "")
    leading_sign = int(_material_state_sign(leading, "five_day") or 0)
    leading_risk_sign = leading_sign * PATTERN_RISK_ALIGNMENT_SIGN[leading_key]

    supporting_core: list[dict[str, Any]] = []
    counter_core: list[dict[str, Any]] = []
    for row in material_core:
        family_key = str(row.get("key") or "")
        state_sign = int(_material_state_sign(row, "five_day") or 0)
        normalized = state_sign * PATTERN_RISK_ALIGNMENT_SIGN[family_key]
        target = supporting_core if normalized == leading_risk_sign else counter_core
        target.append(row)

    supporting_confirmation: list[dict[str, Any]] = []
    counter_confirmation: list[dict[str, Any]] = []
    for row in confirmation_rows:
        state_sign = _material_state_sign(row, "five_day")
        family_key = str(row.get("key") or "")
        if state_sign not in {-1, 1}:
            continue
        normalized = int(state_sign) * PATTERN_CONFIRMATION_RISK_ALIGNMENT_SIGN[family_key]
        target = (
            supporting_confirmation
            if normalized == leading_risk_sign
            else counter_confirmation
        )
        target.append(row)

    one_day_sign = _material_state_sign(leading, "one_day")
    one_day_reversal = one_day_sign in {-1, 1} and one_day_sign != leading_sign
    supporting_evidence = [
        _repricing_evidence_label(row)
        for row in [*supporting_core, *supporting_confirmation]
    ]
    counter_evidence = [
        _repricing_evidence_label(row)
        for row in [*counter_core, *counter_confirmation]
    ]
    if one_day_reversal:
        one_day = dict(leading.get("one_day") or {})
        counter_evidence.append(
            f"1D {one_day.get('semantic_label')} · 5D 핵심 방향과 반대"
        )

    leading_semantic = str(dict(leading.get("five_day") or {}).get("semantic_label"))
    leading_basis = PATTERN_FAMILY_BASIS_COPY[leading_key]
    support_phrases = [
        str(dict(row.get("five_day") or {}).get("semantic_label"))
        for row in supporting_core
        if row is not leading
    ]
    counter_phrases = [
        str(dict(row.get("five_day") or {}).get("semantic_label"))
        for row in counter_core
    ]
    leading_sentence = f"{leading_basis} 기반 {leading_semantic}가 가장 강합니다."
    risk_direction = "위험선호" if leading_risk_sign > 0 else "방어"
    if support_phrases and counter_phrases:
        interpretation = (
            f"{leading_sentence} {_join_korean_phrases(support_phrases)}가 같은 "
            f"{risk_direction} 방향을 지지하지만, "
            f"{_join_korean_phrases(counter_phrases)}가 반대로 움직여 한 가지 "
            "거시 원인으로 확정할 수 없습니다."
        )
    elif support_phrases:
        interpretation = (
            f"{leading_sentence} {_join_korean_phrases(support_phrases)}가 같은 "
            f"{risk_direction} 방향을 지지해 교차자산 정렬이 나타납니다."
        )
    elif counter_phrases:
        interpretation = (
            f"{leading_sentence} {_join_korean_phrases(counter_phrases)}가 반대로 "
            "움직여 단일 거시 해석의 신뢰도는 낮습니다."
        )
    else:
        interpretation = (
            f"{leading_sentence} 다른 핵심 선물군이 같은 방향으로 동반하지 않아 "
            "현재는 단일 축 재가격화로 봅니다."
        )

    has_counter = bool(counter_core or counter_confirmation or one_day_reversal)
    if has_counter:
        status, confidence_label = "MIXED", "해석 충돌"
    elif len(supporting_core) >= 2:
        status, confidence_label = "ALIGNED", "교차자산 정렬"
    else:
        status, confidence_label = "SINGLE_AXIS", "단일 축"

    scenario = PATTERN_FAMILY_SCENARIO_COPY[(leading_key, leading_sign)]
    return {
        "status": status,
        "confidence_label": confidence_label,
        "headline": f"{PATTERN_FAMILY_HEADLINE_COPY[(leading_key, leading_sign)]}가 재가격화의 중심입니다.",
        "interpretation": interpretation,
        "supporting_evidence": supporting_evidence,
        "counter_evidence": counter_evidence,
        "conditional_scenario": {
            "summary": scenario["summary"],
            "continuation_condition": scenario["continuation"],
            "invalidation_condition": scenario["invalidation"],
            "sensitive_assets": list(scenario["sensitive_assets"]),
        },
    }


def _short_horizon_decision_payload(
    macro: dict[str, Any],
    pattern: dict[str, Any],
    pattern_outlook: dict[str, Any],
) -> dict[str, Any]:
    families = dict(pattern.get("families") or {})
    core_rows = [
        _pattern_family_direction_row(families, key, label)
        for key, label in PATTERN_CORE_FAMILY_DEFINITIONS
    ]
    confirmation_rows = [
        _pattern_family_direction_row(families, key, label)
        for key, label in PATTERN_CONFIRMATION_FAMILY_DEFINITIONS
    ]
    core_summary = _pattern_core_alignment_summary(core_rows)
    confirmation_summary = _pattern_confirmation_summary(
        core_rows,
        confirmation_rows,
    )
    one_day_summary = _pattern_one_day_change_summary(core_rows)
    twenty_day_summary = _pattern_background_relationship_summary(core_rows)
    return {
        "observation_cards": [
            {
                "key": "1D",
                "title": "1D · 지금 새로 생긴 변화",
                "summary": one_day_summary,
            },
            {
                "key": "5D",
                "title": "5D · 현재 단기 방향",
                "summary": core_summary,
            },
            {
                "key": "20D",
                "title": "20D · 기존 배경과의 관계",
                "summary": twenty_day_summary,
            },
        ],
        "current_summary": f"{core_summary} {confirmation_summary}",
        "one_day_shock": {
            "title": "최근 1거래일 · 새 충격",
            "summary": one_day_summary,
        },
        "five_day_direction": {
            "title": "최근 5거래일 · 단기 방향",
            "summary": core_summary,
        },
        "twenty_day_background": {
            "title": "최근 20거래일 · 기존 배경과의 관계",
            "summary": twenty_day_summary,
        },
        "market_repricing": _market_repricing_payload(core_rows, confirmation_rows),
        "core_directions": core_rows,
        "confirmation_signals": confirmation_rows,
        "confirmation_summary": confirmation_summary,
        "change_conditions": [
            str(item)
            for item in list(pattern.get("change_conditions") or [])
            if str(item).strip()
        ],
        "calculation_scope": _futures_macro_calculation_scope(macro, pattern),
    }


def _current_pattern_horizon(pattern: dict[str, Any]) -> dict[str, Any]:
    return {
        "key": "current",
        "label": "현재 관측",
        "kind": "observation",
        "title": _display_text(pattern.get("regime_label"), "현재 체제 자료 부족"),
        "summary": _display_text(pattern.get("summary"), "다중 기간 패턴을 계산할 자료가 부족합니다."),
        "observation_status": _pattern_observation_status(pattern),
        "edge_label": _display_text(pattern.get("transition_label"), "자료 부족"),
        "status_reason": "현재는 1D / 5D / 20D 관측이며 미래 확률이 아닙니다.",
    }


def _probability_rows(item: dict[str, Any]) -> list[dict[str, Any]]:
    raw_probabilities = dict(item.get("probabilities") or {})
    baseline = dict(item.get("baseline_probabilities") or {})
    lift = dict(item.get("probability_lift") or {})
    return [
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


def _verified_terminal_regions(item: dict[str, Any], status: str) -> list[dict[str, float]]:
    if status != "VERIFIED":
        return []
    fields = (
        "mass", "center_x", "center_y", "radius_major", "radius_minor", "rotation_deg"
    )
    regions: list[dict[str, float]] = []
    for value in list(item.get("terminal_regions") or []):
        raw = dict(value or {})
        if any(raw.get(field) is None for field in fields):
            continue
        region = {field: float(raw[field]) for field in fields}
        if all(isfinite(number) for number in region.values()):
            regions.append(region)
    return sorted(regions, key=lambda region: region["mass"], reverse=True)


def _verified_direction_vector(item: dict[str, Any], status: str) -> dict[str, float] | None:
    if status != "VERIFIED":
        return None
    raw = dict(item.get("direction_vector") or {})
    fields = ("median_dx", "median_dy", "lower_dx", "upper_dx", "lower_dy", "upper_dy")
    if any(raw.get(field) is None for field in fields):
        return None
    vector = {field: float(raw[field]) for field in fields}
    return vector if all(isfinite(value) for value in vector.values()) else None


def _future_pattern_horizon(item: dict[str, Any]) -> dict[str, Any]:
    probability_status = str(item.get("probability_status") or "UNAVAILABLE")
    coordinate_status = str(item.get("coordinate_status") or "UNAVAILABLE")
    vector_status = str(item.get("vector_status") or "UNAVAILABLE")
    disclosure = _probability_rows(item)
    probabilities = disclosure if probability_status == "VERIFIED" else []
    disclosure_probabilities = disclosure if probability_status == "PROVISIONAL" else []
    horizon = int(item.get("horizon") or 0)
    dominant = str(item.get("dominant_regime") or "")
    if probability_status == "VERIFIED":
        title = PATTERN_REGIME_LABELS.get(dominant, "조건부 방향 우위 미확인")
        edge_label = _display_text(item.get("edge_label"), "검증된 확률 우위")
    elif probability_status == "NO_EDGE":
        title = edge_label = "baseline 대비 예측 우위 없음"
    elif probability_status == "PROVISIONAL":
        title = edge_label = "검증 중 · 확정 우위 없음"
    else:
        title = "조건부 방향 우위 미확인"
        edge_label = "방향 우위 미확인"
    return {
        "key": f"{horizon}D",
        "label": _display_text(item.get("label"), "조건부 전망"),
        "kind": "conditional_outlook",
        "title": title,
        "summary": edge_label,
        "probability_status": probability_status,
        "coordinate_status": coordinate_status,
        "vector_status": vector_status,
        "edge_label": edge_label,
        "baseline_label": "평소 기준 확률",
        "probabilities": probabilities,
        "disclosure_probabilities": disclosure_probabilities,
        "episode_count": int(item.get("episode_count") or 0),
        "status_reason": _display_text(item.get("status_reason"), "검증 근거가 부족합니다."),
        "selected_candidate": item.get("selected_candidate"),
        "terminal_regions": _verified_terminal_regions(item, coordinate_status),
        "direction_vector": _verified_direction_vector(item, vector_status),
        "macro_adjustment": dict(item.get("macro_adjustment") or {}),
    }


def _pattern_command_payload(
    macro: dict[str, Any],
    pattern_outlook: dict[str, Any],
    current_observation: dict[str, Any],
) -> dict[str, Any]:
    coverage = dict(macro.get("coverage") or {})
    standardized = int(coverage.get("standardized_count") or 0)
    symbol_count = int(coverage.get("symbol_count") or 0)
    latest_daily = _snapshot_value(coverage.get("latest_daily_date") or pattern_outlook.get("as_of_date"))
    return {
        "title": "선물 매크로 패턴",
        "detail": (
            f"일봉 {standardized}/{symbol_count}개 · 완료 기준일 {latest_daily} · "
            f"현재 관측 {current_observation.get('session_date') or latest_daily}"
        ),
        "actions": [
            {"id": "daily_refresh", "label": "최신 데이터 갱신", "kind": "primary", "detail": "주요 선물의 최근 1년 일봉을 겹쳐 갱신하고, 진행 중 세션은 저장된 5분봉으로 현재 관측을 최신화하며 이력이 부족한 종목만 장기 보강합니다."},
            {"id": "reload", "label": "다시 읽기", "kind": "secondary", "detail": "provider 수집이나 전망 계산 없이 저장된 snapshot을 다시 읽습니다."},
        ],
    }


def _pattern_hero_payload(
    macro: dict[str, Any],
    pattern: dict[str, Any],
    current_observation: dict[str, Any],
) -> dict[str, Any]:
    summary = dict(macro.get("summary") or {})
    evidence = dict(pattern.get("evidence") or {})
    observation_mode = str(
        current_observation.get("observation_mode") or "COMPLETED"
    )
    observation_status = str(current_observation.get("status") or "")
    if observation_mode == "INTRADAY_PROVISIONAL":
        observation_label = (
            "장중 잠정 관측 · 일부 family"
            if observation_status == "INTRADAY_PARTIAL"
            else "장중 잠정 관측"
        )
        observation_detail = (
            "저장된 완료 5분봉을 모든 사용 가능 family의 공통 시각까지 반영했습니다."
        )
    else:
        observation_label = "마지막 완료 일봉"
        observation_detail = (
            "거래 중인 세션의 5분봉이 없거나 충분하지 않아 마지막 완료 일봉을 사용합니다."
            if current_observation.get("fallback_reason") not in {None, "no_pending_session"}
            else "현재 진행 중인 세션이 없어 마지막 완료 일봉을 사용합니다."
        )
    return {
        "kicker": "시장 재가격화 레이더",
        "title": _display_text(pattern.get("regime_label"), "현재 체제 자료 부족"),
        "transition_label": _display_text(pattern.get("transition_label"), "자료 부족"),
        "summary": _display_text(pattern.get("summary") or summary.get("summary"), "현재 패턴을 계산할 자료가 부족합니다."),
        "today_summary": _display_text(summary.get("summary"), "오늘의 재가격화 근거가 부족합니다."),
        "as_of_date": _display_text(pattern.get("as_of_date"), "-"),
        "completed_as_of_date": _display_text(
            current_observation.get("completed_as_of_date"),
            _display_text(pattern.get("as_of_date"), "-"),
        ),
        "observation_mode": observation_mode,
        "observation_label": observation_label,
        "observation_detail": observation_detail,
        "observed_at_utc": current_observation.get("observed_at_utc"),
        "observed_at_et": current_observation.get("observed_at_et"),
        "freshness_minutes": current_observation.get("freshness_minutes"),
        "fallback_reason": current_observation.get("fallback_reason"),
        "observation_status": _pattern_observation_status(pattern),
        "coverage_label": "최근 1 · 5 · 20거래일",
        "evidence": [str(value) for value in list(evidence.get("current") or []) if str(value).strip()],
    }


def _resolved_current_observation(
    pattern_outlook: dict[str, Any],
    current_observation: dict[str, Any] | None,
) -> dict[str, Any]:
    completed_pattern = dict(pattern_outlook.get("current_pattern") or {})
    session = dict(pattern_outlook.get("session") or {})
    if isinstance(current_observation, dict):
        candidate = dict(current_observation)
        if isinstance(candidate.get("pattern"), dict):
            return candidate
    completed_as_of_date = (
        session.get("latest_final_session")
        or pattern_outlook.get("as_of_date")
        or completed_pattern.get("as_of_date")
    )
    return {
        "status": "COMPLETED_FALLBACK",
        "observation_mode": "COMPLETED",
        "pattern": completed_pattern,
        "session_date": completed_as_of_date,
        "completed_as_of_date": completed_as_of_date,
        "observed_at_utc": None,
        "observed_at_et": None,
        "freshness_minutes": None,
        "available_family_count": int(
            dict(completed_pattern.get("coverage") or {}).get(
                "available_family_count"
            )
            or 0
        ),
        "required_family_count": int(
            dict(completed_pattern.get("coverage") or {}).get(
                "required_family_count"
            )
            or 6
        ),
        "fallback_reason": (
            "no_pending_session"
            if session.get("pending_session") is None
            else "intraday_observation_unavailable"
        ),
    }


def _pattern_evidence_payload(
    pattern: dict[str, Any],
    pattern_outlook: dict[str, Any],
    macro: dict[str, Any],
) -> dict[str, Any]:
    evidence = dict(pattern.get("evidence") or {})
    macro_summary = dict(macro.get("summary") or {})
    outlook_items = [
        f"{item.get('label')}: {item.get('status_reason')} · {item.get('probability_status')}"
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
    status = str(horizon.get("probability_status") or "UNAVAILABLE")
    if status == "UNAVAILABLE":
        return "검증 부족"
    if status == "NO_EDGE":
        return "예측 우위 없음"
    if status != "VERIFIED":
        return "검증 중"
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
    five_day = dict(horizon_map.get(5) or {})
    twenty_day = dict(horizon_map.get(20) or {})
    observation_status = _pattern_observation_status(pattern)
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
                "five_day": _pathway_outlook_label(five_day, pathway_key),
                "five_day_status": str(five_day.get("probability_status") or "UNAVAILABLE"),
                "twenty_day": _pathway_outlook_label(twenty_day, pathway_key),
                "twenty_day_status": str(twenty_day.get("probability_status") or "UNAVAILABLE"),
            },
            "change_condition": _display_text(change_conditions[0] if change_conditions else None, "다음 5D persistence를 확인합니다."),
            "observation_status": observation_status,
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


def _compact_trace_rows(value: Any, *, limit: int = 80) -> list[dict[str, Any]]:
    if isinstance(value, pd.DataFrame):
        records = value.to_dict(orient="records")
    elif isinstance(value, list):
        records = [dict(item) for item in value if isinstance(item, dict)]
    else:
        records = []
    return records[: max(1, int(limit))]


def _calculation_trace_payload(
    macro: dict[str, Any],
    *,
    snapshot_metadata: dict[str, Any] | None,
    pattern_outlook: dict[str, Any],
) -> dict[str, Any]:
    coverage = dict(macro.get("coverage") or {})
    metadata = dict(snapshot_metadata or {})
    table_specs = (
        ("scores", "현재 점수 원본", macro.get("scores")),
        ("components", "점수 구성 기여", macro.get("score_components")),
        ("symbols", "선물 일봉 변화", macro.get("symbols")),
    )
    tables = []
    for key, label, value in table_specs:
        rows = _compact_trace_rows(value)
        columns = list(rows[0].keys()) if rows else []
        tables.append(
            {
                "key": key,
                "label": label,
                "columns": columns,
                "rows": rows,
            }
        )
    cautions = [
        _macro_caution_label(item)
        for item in list(macro.get("cautions") or [])
        if str(item).strip()
    ]
    cautions.extend(
        _macro_caution_label(item)
        for item in list(pattern_outlook.get("limitations") or [])
        if str(item).strip()
    )
    return {
        "metadata": [
            {
                "label": "CME/yfinance 일봉 세션 기준일",
                "value": _snapshot_value(
                    coverage.get("latest_daily_date") or metadata.get("as_of_date")
                ),
            },
            {
                "label": "snapshot 저장 시각",
                "value": _snapshot_value(metadata.get("materialized_at")),
            },
            {
                "label": "source marker",
                "value": _snapshot_value(metadata.get("source_marker")),
            },
            {
                "label": "daily coverage",
                "value": _futures_daily_coverage_label(coverage),
            },
            {
                "label": "저장 row",
                "value": f"{int(coverage.get('raw_rows') or 0):,}",
            },
        ],
        "tables": tables,
        "cautions": list(dict.fromkeys(cautions)),
    }


def build_futures_macro_react_workbench_payload(
    macro: dict[str, Any],
    *,
    pattern_outlook: dict[str, Any],
    snapshot_metadata: dict[str, Any] | None = None,
    current_observation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    observation = _resolved_current_observation(
        pattern_outlook,
        current_observation,
    )
    pattern = dict(
        observation.get("pattern")
        or pattern_outlook.get("current_pattern")
        or macro.get("pattern")
        or {}
    )
    session = dict(pattern_outlook.get("session") or {})
    return {
        "schema_version": "futures_macro_react_workbench_v7",
        "component": "FuturesMacroWorkbench",
        "command": _pattern_command_payload(
            macro,
            pattern_outlook,
            observation,
        ),
        "hero": _pattern_hero_payload(macro, pattern, observation),
        "observation": {
            key: observation.get(key)
            for key in (
                "status",
                "observation_mode",
                "session_date",
                "completed_as_of_date",
                "observed_at_utc",
                "observed_at_et",
                "freshness_minutes",
                "available_family_count",
                "required_family_count",
                "fallback_reason",
            )
        },
        "short_horizon_decision": _short_horizon_decision_payload(
            macro,
            pattern,
            pattern_outlook,
        ),
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
            "y_label": "금리·달러·물가 압력",
            "domain": {"x": [-2.5, 2.5], "y": [-2.5, 2.5]},
            "path": list(pattern.get("path") or [])[-30:],
        },
        "session_evidence": {
            "latest_final_session": session.get("latest_final_session"),
            "pending_session": session.get("pending_session"),
            "status": session.get("status"),
        },
        "evidence": _pattern_evidence_payload(pattern, pattern_outlook, macro),
        "ribbon": {"title": "최근 60거래일 체제", "items": list(pattern.get("ribbon") or [])},
        "asset_pathways": _pattern_asset_pathways(pattern, pattern_outlook),
        "method": _pattern_method_payload(pattern_outlook),
        "calculation_trace": _calculation_trace_payload(
            macro,
            snapshot_metadata=snapshot_metadata,
            pattern_outlook=pattern_outlook,
        ),
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
        with st.spinner("선물 일봉과 진행 중 세션의 최신 5분봉을 갱신하는 중입니다..."):
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
    status_label = "최근 최신 데이터 갱신" if refreshed_at else "최근 다시 읽기"
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
        "최신 갱신",
        key="overview_futures_macro_tab_daily_refresh",
        use_container_width=True,
        help="최근 1년 일봉과 진행 중 세션의 5분봉 현재 관측을 갱신하고, 이력이 부족한 종목만 장기 보강합니다.",
    ):
        with st.spinner("선물 일봉과 진행 중 세션의 최신 5분봉을 갱신하는 중입니다..."):
            _refresh_futures_macro_daily_for_ui()
        st.rerun()
    if cols[2].button(
        "다시 읽기",
        key="overview_futures_macro_tab_reload",
        use_container_width=True,
        help="provider 수집이나 전망 계산 없이 저장된 snapshot을 다시 읽습니다.",
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
    _ = detail_expanded
    materialized = load_overview_futures_macro_materialized_snapshot()
    if str(materialized.get("status") or "") == "READY":
        macro = dict(materialized.get("macro") or {})
        pattern_outlook = dict(materialized.get("pattern_outlook") or {})
        snapshot_metadata = dict(materialized.get("metadata") or {})
        try:
            current_observation = (
                load_overview_futures_macro_intraday_observation(
                    completed_pattern=dict(
                        pattern_outlook.get("current_pattern") or {}
                    ),
                    evaluation_time=datetime.now(timezone.utc),
                )
            )
        except Exception:
            current_observation = None
    else:
        reason = _display_text(
            materialized.get("reason"),
            "저장된 선물 매크로 snapshot이 없어 일봉 갱신이 필요합니다.",
        )
        macro = {
            "status": "MISSING",
            "coverage": {},
            "warnings": [reason],
            "summary": {"summary": reason},
            "cautions": [reason],
        }
        pattern_outlook = {
            "status": "LIMITED",
            "horizons": [],
            "limitations": [reason],
        }
        snapshot_metadata = {}
        current_observation = None
    coverage = dict(macro.get("coverage") or {})
    react_available = futures_macro_react_component_available()

    if react_available:
        payload = build_futures_macro_react_workbench_payload(
            macro,
            pattern_outlook=pattern_outlook,
            snapshot_metadata=snapshot_metadata,
            current_observation=current_observation,
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
            _render_snapshot_warnings(
                {"warnings": [_futures_warning_label(warning) for warning in warnings]}
            )


def render_futures_macro_fragment(*, detail_expanded: bool) -> None:
    @st.fragment
    def futures_macro_context_fragment() -> None:
        _render_futures_macro_panel(detail_expanded=detail_expanded)

    futures_macro_context_fragment()
