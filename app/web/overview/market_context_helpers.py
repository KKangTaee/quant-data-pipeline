from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any

import pandas as pd
import streamlit as st

from app.jobs.overview_actions import (
    record_overview_action_result,
    run_overview_market_context_refresh_all,
    run_overview_market_context_refresh_smart,
)
from app.web.overview.session_helpers import _market_context_session_payload
from app.web.overview_dashboard_helpers import (
    load_overview_group_leadership_snapshot,
    load_overview_macro_context_cockpit,
    load_overview_market_context_historical_analog,
    load_overview_market_sentiment_snapshot,
)
from app.web.overview_ui_components import (
    OVERVIEW_COLOR_DANGER,
    OVERVIEW_COLOR_NEUTRAL,
    OVERVIEW_COLOR_POSITIVE,
    OVERVIEW_COLOR_WARNING,
)


MARKET_CONTEXT_REFRESH_RESULT_KEY = "overview_market_context_refresh_all_result"
MARKET_CONTEXT_REFRESH_REFLECTION_KEY = "overview_market_context_refresh_reflection"


def render_market_context_header() -> None:
    """Render the compact Market Context tab heading."""
    st.markdown("### 시장 맥락")
    st.caption("저장된 시장 자료로 현재 세션의 움직임, 확산, 이벤트 배경을 빠르게 확인합니다.")


def _store_overview_job_result(result_key: str, result: dict[str, Any]) -> None:
    st.session_state[result_key] = result
    try:
        record_overview_action_result(result)
    except Exception as exc:  # pragma: no cover - UI resilience only
        st.session_state["overview_run_history_warning"] = f"Run history write failed: {exc}"


def _clear_overview_market_context_caches() -> None:
    for loader in (
        load_overview_group_leadership_snapshot,
        load_overview_market_context_historical_analog,
        load_overview_market_sentiment_snapshot,
        load_overview_macro_context_cockpit,
    ):
        clear = getattr(loader, "clear", None)
        if callable(clear):
            clear()


def _status_tone(status: Any) -> str:
    normalized = str(status or "").lower()
    if normalized in {"success", "dry_run"}:
        return "positive"
    if normalized in {"partial_success", "skipped", "locked"}:
        return "warning"
    if normalized in {"failed", "error"}:
        return "danger"
    return "neutral"


def _overview_market_context_refresh_reflection_state(
    result: dict[str, Any],
    *,
    reflected_at: datetime | None = None,
) -> dict[str, Any]:
    status = str(result.get("status") or "unknown").lower()
    reflected_at_text = (reflected_at or datetime.now()).strftime("%Y-%m-%d %H:%M")
    jobs_failed = int(result.get("jobs_failed") or 0)
    jobs_run = int(result.get("jobs_run") or 0)
    reflected = status in {"success", "partial_success"}

    if status == "success":
        label = "방금 갱신을 반영했습니다"
        detail = f"상단 브리프는 새 snapshot을 다시 읽었습니다 · {reflected_at_text}"
    elif status == "partial_success":
        label = "일부 자료만 반영했습니다"
        detail = (
            f"성공한 자료는 다시 읽었고, 오래된 항목은 자료 상태를 참고하세요 · "
            f"{reflected_at_text}"
        )
    elif status in {"failed", "error"}:
        label = "갱신 실패 - 기존 자료를 계속 표시합니다"
        detail = f"상단 브리프는 기존 자료 기준이며 새로 반영된 자료처럼 표시하지 않습니다 · {reflected_at_text}"
    elif status in {"skipped", "locked"}:
        label = "갱신이 실행되지 않았습니다"
        detail = f"기존 자료를 계속 표시합니다 · {reflected_at_text}"
    else:
        label = "갱신 상태 보기"
        detail = f"기존 자료를 기준으로 표시 중입니다 · {reflected_at_text}"

    if status == "partial_success" and jobs_failed:
        detail = f"{detail} · 실패 {jobs_failed}개"
    elif status == "success" and jobs_run:
        detail = f"{detail} · 완료 {jobs_run}개"

    return {
        "status": status,
        "tone": _status_tone(status),
        "label": label,
        "detail": detail,
        "reflected": reflected,
        "reflected_at": reflected_at_text,
    }


def render_market_context_refresh_reflection() -> None:
    payload = st.session_state.get(MARKET_CONTEXT_REFRESH_REFLECTION_KEY)
    if not isinstance(payload, dict):
        return
    tone = str(payload.get("tone") or "neutral")
    tone_color = {
        "positive": OVERVIEW_COLOR_POSITIVE,
        "warning": OVERVIEW_COLOR_WARNING,
        "danger": OVERVIEW_COLOR_DANGER,
    }.get(tone, OVERVIEW_COLOR_NEUTRAL)
    st.markdown(
        (
            f'<div class="ov-macro-cockpit-refresh-reflection" style="--ov-refresh-reflection-tone:{tone_color};">'
            f'<span class="ov-macro-cockpit-refresh-reflection-label">{escape(str(payload.get("label") or ""))}</span>'
            f'<span class="ov-macro-cockpit-refresh-reflection-detail">{escape(str(payload.get("detail") or ""))}</span>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def load_market_context_cockpit_model() -> dict[str, Any]:
    market_session_context = _market_context_session_payload()
    return load_overview_macro_context_cockpit(
        market_session_context=market_session_context,
    )


def _overview_market_context_refresh_impact(label: str) -> str:
    if label == "S&P 500 Market Movers":
        return "움직임 / 확산 자료를 다시 읽습니다."
    if label == "Market Sentiment":
        return "Sentiment 배경 자료를 다시 읽습니다."
    if label == "FOMC Calendar":
        return "공식 FOMC 일정 배경을 다시 읽습니다."
    if label == "Macro Calendar":
        return "공식 macro 일정 배경을 다시 읽습니다."
    if label == "Earnings Calendar":
        return "실적 일정 rows를 갱신하지만 추정 일정은 직접 원인 근거로 쓰지 않습니다."
    return "관련 저장 자료를 다시 읽습니다."


def _render_overview_market_context_refresh_impact_summary(result: dict[str, Any]) -> None:
    rows = []
    for item in result.get("results") or []:
        if not isinstance(item, dict):
            continue
        label = str(item.get("label") or item.get("job_name") or "-")
        rows.append(
            {
                "자료": label,
                "상태": item.get("status") or "-",
                "브리프 반영": _overview_market_context_refresh_impact(label),
            }
        )
    if rows:
        st.markdown("#### 반영 결과")
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def _render_overview_market_context_refresh_result(result_key: str) -> None:
    result = st.session_state.get(result_key)
    if not isinstance(result, dict):
        return
    status = str(result.get("status") or "-")
    message = str(result.get("message") or "")
    if status == "success":
        st.success(message)
    elif status == "partial_success":
        st.warning(message)
    else:
        st.error(message)
    _render_overview_market_context_refresh_impact_summary(result)
    rows = []
    for item in result.get("results") or []:
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                "작업": item.get("label") or item.get("job_name") or "-",
                "상태": item.get("status") or "-",
                "저장 rows": item.get("rows_written") or 0,
                "메시지": item.get("message") or "",
            }
        )
    if rows:
        with st.expander("갱신 상세", expanded=False):
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def _overview_market_context_refresh_expander_label(cockpit_model: dict[str, Any]) -> str:
    refresh_plan = dict(cockpit_model.get("refresh_plan") or {})
    summary = dict(refresh_plan.get("summary") or {})
    headline = str(summary.get("headline") or "").strip()
    if headline:
        return f"필요 자료 보강 · {headline}"
    checks = [
        dict(item or {})
        for item in list(cockpit_model.get("context_findings") or cockpit_model.get("next_checks") or [])
        if isinstance(item, dict)
    ]
    if not checks:
        return "필요 자료 보강"
    review_checks = [
        check
        for check in checks
        if str(check.get("status") or "").upper() not in {"OK", "SUCCESS", "ACTUAL"}
        or str(check.get("repair_hint") or "").strip()
    ]
    top = review_checks[0] if review_checks else checks[0]
    source = str(top.get("source_area") or top.get("label") or top.get("title") or "자료 상태").strip()
    return f"필요 자료 보강 · {source}"


def _render_overview_market_context_smart_refresh_plan(cockpit_model: dict[str, Any]) -> list[str]:
    refresh_plan = dict(cockpit_model.get("refresh_plan") or {})
    items = [dict(item or {}) for item in list(refresh_plan.get("items") or []) if isinstance(item, dict)]
    return [str(item.get("action_id")) for item in items if str(item.get("action_id") or "").strip()]


def _overview_market_context_refresh_plan_parts(
    cockpit_model: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    refresh_plan = dict(cockpit_model.get("refresh_plan") or {})
    summary = dict(refresh_plan.get("summary") or {})
    items = [dict(item or {}) for item in list(refresh_plan.get("items") or []) if isinstance(item, dict)]
    excluded_items = [
        dict(item or {})
        for item in list(refresh_plan.get("excluded_items") or [])
        if isinstance(item, dict)
    ]
    return summary, items, excluded_items


def _overview_market_context_refresh_tone_color(has_actions: bool) -> str:
    return OVERVIEW_COLOR_WARNING if has_actions else OVERVIEW_COLOR_POSITIVE


def _overview_market_context_refresh_item_html(
    item: dict[str, Any],
    *,
    muted: bool = False,
) -> str:
    source = str(item.get("source_area") or item.get("label") or "-")
    resolution = str(item.get("resolution_label") or ("보강 제외" if muted else "보강 대상"))
    reason = str(item.get("reason") or "-")
    limitation = str(item.get("limitation") or "").strip()
    meta = f"{reason} · {limitation}" if limitation else reason
    return (
        '<div class="ov-refresh-status-row">'
        f'<div class="ov-refresh-status-source">{escape(source)}</div>'
        f'<div class="ov-refresh-status-copy">{escape(meta)}</div>'
        '<div class="ov-refresh-status-meta">'
        f'<span class="ov-refresh-status-pill">{escape(resolution)}</span>'
        "</div>"
        "</div>"
    )


def _render_overview_market_context_refresh_status_panel(
    cockpit_model: dict[str, Any],
    *,
    action_ids: list[str],
) -> None:
    summary, items, excluded_items = _overview_market_context_refresh_plan_parts(cockpit_model)
    has_actions = bool(action_ids)
    title = "현재 보강할 자료 이슈" if has_actions else "현재 보강할 자료 이슈 없음"
    badge = f"{len(action_ids)}개 실행 가능" if has_actions else "보강 없음"
    detail = str(
        summary.get("detail")
        or (
            "현재 화면에서 실제 갱신 가능한 자료만 기존 Overview action boundary로 실행합니다."
            if has_actions
            else "현재 브리프 자료는 저장 snapshot 기준으로 읽을 수 있으며, 참고 제한 항목은 보강 대상에서 제외합니다."
        )
    )
    active_action_ids = set(action_ids)
    active_items = [
        item
        for item in items
        if str(item.get("action_id") or "").strip() in active_action_ids
    ]
    if has_actions and not active_items:
        active_items = items
    rows_html = "".join(_overview_market_context_refresh_item_html(item) for item in active_items[:5])
    excluded_html = ""
    if excluded_items:
        excluded_rows = " ".join(
            f"{str(item.get('source_area') or item.get('label') or '-')}: {str(item.get('reason') or '-')}"
            for item in excluded_items[:3]
        )
        excluded_html = f'<div class="ov-refresh-status-muted">보강 제외 · {escape(excluded_rows)}</div>'
    no_action_note = ""
    if not has_actions:
        no_action_note = (
            '<div class="ov-refresh-status-muted">'
            "미국장 휴장 / 장외 시간에는 장중 snapshot 시간만으로 보강하지 않습니다. 필요하면 전체 보강을 수동으로 실행합니다."
            "</div>"
        )
    rows_block = f'<div class="ov-refresh-status-list">{rows_html}</div>' if rows_html else ""
    panel_html = (
        f'<div class="ov-refresh-status-panel" style="--ov-refresh-status-tone:{_overview_market_context_refresh_tone_color(has_actions)};">'
        '<div class="ov-refresh-status-head">'
        f'<div class="ov-refresh-status-title">{escape(title)}</div>'
        f'<div class="ov-refresh-status-badge">{escape(badge)}</div>'
        "</div>"
        f'<div class="ov-refresh-status-detail">{escape(detail)}</div>'
        f"{rows_block}"
        f"{excluded_html}"
        f"{no_action_note}"
        "</div>"
    )
    st.markdown(
        panel_html,
        unsafe_allow_html=True,
    )


def render_market_context_refresh_bar(cockpit_model: dict[str, Any]) -> None:
    result_key = MARKET_CONTEXT_REFRESH_RESULT_KEY
    refresh_plan = dict(cockpit_model.get("refresh_plan") or {})
    summary = dict(refresh_plan.get("summary") or {})
    with st.expander(_overview_market_context_refresh_expander_label(cockpit_model), expanded=False):
        st.markdown(
            '<div class="ov-macro-cockpit-refresh-assist">현재 화면은 저장된 DB snapshot을 읽고, 갱신은 기존 Overview action boundary로만 실행합니다.</div>',
            unsafe_allow_html=True,
        )
        action_ids = _render_overview_market_context_smart_refresh_plan(cockpit_model)
        _render_overview_market_context_refresh_status_panel(cockpit_model, action_ids=action_ids)
        if not action_ids:
            cols = st.columns([1.4, 0.82], gap="small", vertical_alignment="center")
            with cols[0]:
                st.caption(
                    "현재 실행할 이슈별 보강은 없습니다. 필요하면 전체 저장 snapshot 보강을 수동으로 실행합니다."
                )
            if cols[1].button(
                str(summary.get("full_refresh_label") or "전체 Market Context 자료 보강"),
                key="overview_market_context_refresh_all",
                use_container_width=True,
                type="secondary",
                help="S&P 500 movers, sentiment, FOMC/earnings/macro calendar를 갱신합니다. Top1000/Top2000/Futures는 각 전용 화면에서 관리합니다.",
            ):
                current_year = datetime.now().year
                with st.spinner("Market Context 전체 자료를 갱신하는 중입니다..."):
                    result = run_overview_market_context_refresh_all(years=(current_year, current_year + 1))
                    _store_overview_job_result(result_key, result)
                    st.session_state[MARKET_CONTEXT_REFRESH_REFLECTION_KEY] = (
                        _overview_market_context_refresh_reflection_state(result)
                    )
                    _clear_overview_market_context_caches()
                st.rerun()
        else:
            cols = st.columns([1.4, 0.72, 0.82], gap="small", vertical_alignment="center")
            with cols[0]:
                st.caption(
                    "자료 보강 후 Market Context cache를 비우고 같은 화면을 다시 읽습니다. raw job rows는 상세에만 표시합니다."
                )
            if cols[1].button(
                str(summary.get("primary_button_label") or "현재 이슈만 보강"),
                key="overview_market_context_refresh_smart",
                use_container_width=True,
                type="secondary",
                help="현재 Market Context에서 실제 보강 가능한 항목만 기존 Overview action boundary로 갱신합니다.",
            ):
                current_year = datetime.now().year
                with st.spinner("Market Context 자료를 갱신하는 중입니다..."):
                    result = run_overview_market_context_refresh_smart(
                        action_ids=action_ids,
                        years=(current_year, current_year + 1),
                    )
                    _store_overview_job_result(result_key, result)
                    st.session_state[MARKET_CONTEXT_REFRESH_REFLECTION_KEY] = (
                        _overview_market_context_refresh_reflection_state(result)
                    )
                    _clear_overview_market_context_caches()
                st.rerun()
            if cols[2].button(
                str(summary.get("full_refresh_label") or "전체 Market Context 자료 보강"),
                key="overview_market_context_refresh_all",
                use_container_width=True,
                type="secondary",
                help="S&P 500 movers, sentiment, FOMC/earnings/macro calendar를 갱신합니다. Top1000/Top2000/Futures는 각 전용 화면에서 관리합니다.",
            ):
                current_year = datetime.now().year
                with st.spinner("Market Context 전체 자료를 갱신하는 중입니다..."):
                    result = run_overview_market_context_refresh_all(years=(current_year, current_year + 1))
                    _store_overview_job_result(result_key, result)
                    st.session_state[MARKET_CONTEXT_REFRESH_REFLECTION_KEY] = (
                        _overview_market_context_refresh_reflection_state(result)
                    )
                    _clear_overview_market_context_caches()
                st.rerun()
        _render_overview_market_context_refresh_result(result_key)
