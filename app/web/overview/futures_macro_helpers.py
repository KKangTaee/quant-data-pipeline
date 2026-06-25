from __future__ import annotations

from datetime import datetime
from html import escape
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
from app.services.futures_macro_validation import build_current_scenario_validation_summary
from app.web.overview.session_helpers import _snapshot_value
from app.web.overview_ui_components import _overview_tone_color


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
MACRO_EVIDENCE_TEXT_LABELS = {
    "Risk-On": "위험선호",
    "Growth": "성장",
    "Rate Pressure": "금리 부담",
    "Dollar Pressure": "달러 압력",
    "Safe Haven": "안전자산",
    "Inflation": "물가 압력",
}


def render_futures_macro_header() -> None:
    st.markdown("### 선물 매크로")
    st.caption("저장된 선물 일봉으로 현재 macro 상태와 과거 점검 근거를 함께 확인합니다.")


def _store_overview_job_result(result_key: str, result: dict[str, Any]) -> None:
    st.session_state[result_key] = result
    try:
        record_overview_action_result(result)
    except Exception as exc:  # pragma: no cover - UI resilience only
        st.session_state["overview_run_history_warning"] = f"Run history write failed: {exc}"


def _run_futures_daily_ohlcv_action() -> dict[str, Any]:
    return run_overview_futures_daily_ohlcv()


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
    symbols = [str(symbol) for symbol in snapshot.get("symbols") or [] if str(symbol).strip()]
    ordered: list[str] = []
    for symbol in symbols:
        if symbol and symbol not in ordered:
            ordered.append(symbol)
    return ordered


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
        sample = current_metrics.get("Sample 5D") or 0
    occurrence_count = confidence.get("occurrence_count")
    if occurrence_count is None:
        occurrence_count = current_metrics.get("Occurrence Count") or 0
    hit_rate = confidence.get("hit_rate_5d")
    if hit_rate is None:
        hit_rate = current_metrics.get("Hit Rate 5D %")
    hit_applicable = bool(confidence.get("hit_applicable"))
    validation_dates = validation_coverage.get("validation_dates") or 0
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
            "detail": f"{validation_dates}개 PIT 날짜 · {span or '-'}년",
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
            "detail": f"기준일 {_snapshot_value(coverage.get('latest_daily_date'))}",
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
        st.info("현재 시나리오 기준 과거 점검 요약이 아직 없습니다.")
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
              <div class="ov-futures-validation-title">{escape(str(summary.get("title") or "과거 점검 요약"))}</div>
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
        with st.expander("전체 시나리오 원본 표", expanded=False):
            st.dataframe(
                scenario_summary[[col for col in preferred_cols if col in scenario_summary.columns]],
                width="stretch",
                hide_index=True,
            )
    relationships = validation.get("relationships")
    threshold_sensitivity = validation.get("threshold_sensitivity")
    if isinstance(relationships, pd.DataFrame) and not relationships.empty:
        with st.expander("점수와 이후 수익률 관계 원본", expanded=False):
            st.dataframe(relationships, width="stretch", hide_index=True)
    if isinstance(threshold_sensitivity, pd.DataFrame) and not threshold_sensitivity.empty:
        with st.expander("점수 기준 민감도 원본", expanded=False):
            st.dataframe(threshold_sensitivity, width="stretch", hide_index=True)


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
            <div><span>매크로 일봉 기준일</span><strong>{escape(latest_daily)}</strong></div>
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
    _render_futures_section_header("원본 표", "상세 분석자가 확인할 수 있는 계산 원본")
    if isinstance(scores, pd.DataFrame) and not scores.empty:
        with st.expander("원본 점수 표", expanded=False):
            st.dataframe(scores.drop(columns=["Tone"], errors="ignore"), width="stretch", hide_index=True)
    if isinstance(components, pd.DataFrame) and not components.empty:
        with st.expander("구성 선물별 기여", expanded=False):
            st.dataframe(components, width="stretch", hide_index=True)
    if isinstance(symbols, pd.DataFrame) and not symbols.empty:
        with st.expander("선물별 일봉 변화 원본", expanded=False):
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
            _store_overview_job_result(
                "overview_futures_daily_ohlcv_result",
                _run_futures_daily_ohlcv_action(),
            )
            clear_overview_futures_macro_snapshot_cache()
            st.session_state["overview_futures_macro_daily_refreshed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.rerun()
    if cols[2].button(
        "다시 읽기",
        key="overview_futures_macro_tab_reload",
        use_container_width=True,
        help="수집 job은 실행하지 않고 현재 DB 기준으로 매크로 snapshot cache만 비운 뒤 다시 읽습니다.",
    ):
        clear_overview_futures_macro_snapshot_cache()
        st.session_state["overview_futures_macro_reloaded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.rerun()
    st.markdown('<div class="ov-futures-macro-action-rule"></div>', unsafe_allow_html=True)


def _render_futures_macro_panel(*, detail_expanded: bool = False) -> None:
    macro = load_overview_futures_macro_snapshot()
    coverage = dict(macro.get("coverage") or {})
    scores = macro.get("scores")
    components = macro.get("score_components")
    symbols = macro.get("symbols")
    confidence = dict(macro.get("confidence") or {})
    validation = dict(macro.get("validation") or {})

    _render_futures_macro_refresh_controls(
        section_detail=(
            f"일봉 {coverage.get('standardized_count') or 0}/{coverage.get('symbol_count') or 0}개"
            f" · 기준일 {_snapshot_value(coverage.get('latest_daily_date'))}"
        ),
    )
    _render_futures_market_brief(macro)
    _render_weekly_macro_context(dict(macro.get("weekly_context") or {}))
    _render_macro_score_lane(scores)
    warnings = list(macro.get("warnings") or [])
    warnings.extend(str(item) for item in validation.get("warnings") or [])
    if warnings:
        _render_snapshot_warnings({"warnings": [_futures_warning_label(warning) for warning in warnings]})

    cautions = [_macro_caution_label(item) for item in macro.get("cautions") or [] if str(item).strip()]
    cautions.extend(_macro_caution_label(item) for item in validation.get("caveats") or [] if str(item).strip())
    with st.expander("근거 해석 / 원본 데이터", expanded=detail_expanded):
        _render_macro_evidence_reading(list(macro.get("evidence_reading") or []))
        _render_macro_validation_summary(validation, confidence_label=str(confidence.get("label") or ""))
        _render_futures_macro_data_management(macro)
        _render_futures_macro_raw_tables(
            scores=scores,
            components=components,
            symbols=symbols,
            validation=validation,
            cautions=cautions,
        )


def render_futures_macro_fragment(*, detail_expanded: bool) -> None:
    @st.fragment
    def futures_macro_context_fragment() -> None:
        _render_futures_macro_panel(detail_expanded=detail_expanded)

    futures_macro_context_fragment()
