from __future__ import annotations

import json
from datetime import datetime
from html import escape
from typing import Any, Callable

import altair as alt
import pandas as pd
import streamlit as st

from app.jobs.overview_actions import (
    record_overview_action_result,
    run_overview_market_context_refresh_all,
    run_overview_market_context_refresh_smart,
    run_overview_us_stock_data_refresh,
)
from app.web.overview.session_helpers import _market_context_session_payload
from app.web.overview_dashboard_helpers import (
    load_overview_group_leadership_snapshot,
    load_overview_macro_context_cockpit,
    load_overview_market_context_historical_analog,
    load_overview_market_sentiment_snapshot,
)
from app.web.overview.components.common import (
    OVERVIEW_COLOR_DANGER,
    OVERVIEW_COLOR_NEUTRAL,
    OVERVIEW_COLOR_POSITIVE,
    OVERVIEW_COLOR_TEXT,
    OVERVIEW_COLOR_TEXT_INVERSE,
    OVERVIEW_COLOR_WARNING,
    OVERVIEW_DIVERGING_RANGE,
)


MARKET_CONTEXT_REFRESH_RESULT_KEY = "overview_market_context_refresh_all_result"
MARKET_CONTEXT_REFRESH_REFLECTION_KEY = "overview_market_context_refresh_reflection"
US_STOCK_SEARCH_QUERY_KEY = "overview_us_stock_valuation_search_query"
US_STOCK_SELECTED_SYMBOL_KEY = "overview_us_stock_valuation_selected_symbol"
US_STOCK_COLLECTION_RESULT_KEY = "overview_us_stock_valuation_collection_result"
US_STOCK_EVENT_KEY = "overview_us_stock_valuation_last_event"
US_STOCK_EVENT_IDS = {
    "search_us_stock",
    "select_us_stock",
    "refresh_us_stock_data",
}
GROUP_TREND_HEATMAP_MIN_HEIGHT = 280
GROUP_TREND_HEATMAP_ROW_HEIGHT = 54


def render_market_context_header() -> None:
    """Render the compact Market Context tab heading."""
    st.markdown("### 시장 맥락")
    st.caption("S&P 500 또는 미국 개별주식의 현재 멀티플과 상대가치 시나리오를 확인합니다.")


@st.cache_data(ttl=300, show_spinner=False)
def load_sp500_valuation_model() -> dict[str, Any]:
    """Load the DB-backed, JSON-safe valuation read model."""
    from app.services.overview.sp500_valuation import build_sp500_valuation_read_model

    return build_sp500_valuation_read_model()


@st.cache_data(ttl=300, show_spinner=False)
def load_market_context_valuation_model(
    selected_symbol: str | None = None,
    search_query: str | None = None,
) -> dict[str, Any]:
    """Load independently isolated S&P 500 and selected-stock read models."""
    from app.services.overview.market_context_valuation import (
        build_market_context_valuation_read_model,
    )

    model = build_market_context_valuation_read_model(
        selected_symbol=selected_symbol,
        search_query=search_query,
    )
    return json.loads(json.dumps(model, default=str))


def _render_market_context_valuation_fallback(payload: dict[str, Any]) -> None:
    """Keep the valuation question readable when the React build is unavailable."""
    st.info("가치평가 화면 빌드를 찾지 못해 핵심 수치만 표시합니다.")
    instruments = dict(payload.get("instruments") or {})
    payload = dict(instruments.get(payload.get("default_instrument") or "sp500") or payload)
    multiple = dict(payload.get("multiple_regime") or {})
    earnings = dict(payload.get("earnings_scenario") or {})
    index = dict(payload.get("index_scenario") or {})
    cols = st.columns(3)
    cols[0].metric("현재 후행 PER", f"{float(multiple.get('current_pe') or 0):.2f}x")
    cols[1].metric("5년 중심 PER", f"{float(multiple.get('mean_multiple') or 0):.2f}x")
    cols[2].metric("가치평가 구간", str(multiple.get("bucket") or "자료 부족"))
    scenarios = dict(index.get("spx_scenarios") or {})
    if scenarios:
        st.write("예상 실적 기반 SPX 시나리오", scenarios)
    st.caption(
        f"EPS 출처: {earnings.get('eps_source') or '확인 필요'} · "
        f"EPS 기준: {earnings.get('eps_basis_date') or '-'} · "
        f"SEP 발표: {earnings.get('release_date') or '-'}"
    )
    baseline = dict(earnings.get("baseline") or {})
    if baseline:
        st.caption(
            f"적용 GDP {float(baseline.get('real_gdp_pct') or 0):.1f}% + "
            f"PCE {float(baseline.get('pce_inflation_pct') or 0):.1f}% = "
            f"예상 EPS 성장률 {float(baseline.get('growth_pct') or 0):.1f}%"
        )
    if earnings.get("fallback_reason"):
        st.caption(str(earnings["fallback_reason"]))
    st.caption("거시 지표 기반 자체 예상이며 애널리스트 컨센서스가 아닙니다.")


def _market_context_valuation_event_payload(
    event: dict[str, Any] | None,
) -> dict[str, Any]:
    if not isinstance(event, dict):
        return {}
    nested = event.get("event")
    return dict(nested) if isinstance(nested, dict) else dict(event)


def _consume_market_context_valuation_event(
    payload: dict[str, Any],
    *,
    state: Any,
) -> bool:
    action_id = str(payload.get("id") or payload.get("action_id") or "").strip()
    if action_id not in US_STOCK_EVENT_IDS:
        return False
    nonce = payload.get("nonce") or payload.get("token") or action_id
    event_token = f"{action_id}:{nonce}"
    if state.get(US_STOCK_EVENT_KEY) == event_token:
        return False
    state[US_STOCK_EVENT_KEY] = event_token
    return True


def _render_us_stock_collection_progress(status: Any, update: dict[str, Any]) -> None:
    stage_labels = {
        "preflight": "누락 구간 확인",
        "identity": "SEC CIK 연결",
        "profile": "시장가치 수집",
        "prices": "가격 수집",
        "sec": "SEC 분기 실적 수집",
        "complete": "완료",
    }
    stage = str(update.get("stage") or "")
    message = str(update.get("message") or stage_labels.get(stage) or "자료를 보강합니다.")
    status.write(f"{stage_labels.get(stage, stage or '진행')} · {message}")


def _run_us_stock_refresh_for_ui(symbol: str) -> dict[str, Any]:
    with st.status(
        f"{symbol} 최신 자료를 확인하는 중입니다.",
        expanded=True,
    ) as status:
        result = run_overview_us_stock_data_refresh(
            symbol,
            progress_callback=lambda update: _render_us_stock_collection_progress(
                status, update
            ),
        )
        result_status = str(result.get("status") or "failed").lower()
        if result_status == "success":
            status.update(
                label=f"{symbol} 최신 자료 확인을 마쳤습니다.",
                state="complete",
            )
        elif result_status == "partial_success":
            status.update(label="수집 가능한 자료를 반영했고 남은 항목이 있습니다.", state="complete")
        else:
            status.update(label="최신 자료를 반영하지 못했습니다.", state="error")
    return result


def _handle_market_context_valuation_event(
    event: dict[str, Any] | None,
    *,
    state: Any = None,
    run_action: Callable[[str], dict[str, Any]] | None = None,
    store_result: Callable[[dict[str, Any]], None] | None = None,
    clear_cache: Callable[[], None] | None = None,
    rerun: Callable[[], None] | None = None,
) -> bool:
    resolved_state = state if state is not None else st.session_state
    payload = _market_context_valuation_event_payload(event)
    action_id = str(payload.get("id") or payload.get("action_id") or "").strip()
    if action_id not in US_STOCK_EVENT_IDS:
        return False
    if action_id == "refresh_us_stock_data":
        selected = str(resolved_state.get(US_STOCK_SELECTED_SYMBOL_KEY) or "").upper()
        event_symbol = str(payload.get("symbol") or "").strip().upper()
        if not selected or event_symbol != selected:
            return False
    if not _consume_market_context_valuation_event(payload, state=resolved_state):
        return False
    if action_id == "search_us_stock":
        resolved_state[US_STOCK_SEARCH_QUERY_KEY] = str(payload.get("query") or "").strip()
        resolved_state.pop(US_STOCK_SELECTED_SYMBOL_KEY, None)
        (rerun or st.rerun)()
        return True
    if action_id == "select_us_stock":
        symbol = str(payload.get("symbol") or "").strip().upper()
        if not symbol:
            return False
        resolved_state[US_STOCK_SELECTED_SYMBOL_KEY] = symbol
        (rerun or st.rerun)()
        return True

    symbol = str(resolved_state.get(US_STOCK_SELECTED_SYMBOL_KEY) or "").upper()
    result = (run_action or _run_us_stock_refresh_for_ui)(symbol)
    if store_result is not None:
        store_result(result)
    else:
        _store_overview_job_result(US_STOCK_COLLECTION_RESULT_KEY, result)
    if str(result.get("status") or "").lower() != "failed":
        (clear_cache or load_market_context_valuation_model.clear)()
    (rerun or st.rerun)()
    return True


def _us_stock_collection_reflection(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": str(result.get("status") or "failed"),
        "message": str(result.get("message") or ""),
    }


def render_market_context_valuation() -> None:
    """Render the React-first valuation surface and consume explicit stock actions."""
    from app.web.overview.market_context_react_component import (
        market_context_valuation_component_available,
        render_market_context_valuation_component,
    )

    selected_symbol = str(
        st.session_state.get(US_STOCK_SELECTED_SYMBOL_KEY) or ""
    ).strip().upper()
    search_query = str(
        st.session_state.get(US_STOCK_SEARCH_QUERY_KEY) or ""
    ).strip()
    try:
        payload = load_market_context_valuation_model(
            selected_symbol or None,
            search_query or None,
        )
    except Exception as exc:  # pragma: no cover - UI resilience only
        st.warning(f"시장 가치평가 자료를 불러오지 못했습니다: {exc}")
        return
    payload = json.loads(json.dumps(payload, default=str))
    collection_result = st.session_state.pop(US_STOCK_COLLECTION_RESULT_KEY, None)
    if isinstance(collection_result, dict):
        instruments = dict(payload.get("instruments") or {})
        stock = dict(instruments.get("us_stock") or {})
        stock["collection_result"] = _us_stock_collection_reflection(collection_result)
        instruments["us_stock"] = stock
        payload["instruments"] = instruments
    if market_context_valuation_component_available():
        event = render_market_context_valuation_component(payload)
        _handle_market_context_valuation_event(event)
        return
    _render_market_context_valuation_fallback(payload)


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


def _symmetric_return_domain(values: pd.Series) -> list[float]:
    numeric = pd.to_numeric(values, errors="coerce").dropna()
    max_abs = max(1.0, float(numeric.abs().max()) if not numeric.empty else 1.0)
    return [-max_abs * 1.08, max_abs * 1.08]


def _symmetric_return_scale(values: pd.Series) -> alt.Scale:
    return alt.Scale(domain=_symmetric_return_domain(values), range=OVERVIEW_DIVERGING_RANGE)


def _build_group_leadership_trend_heatmap(rows: pd.DataFrame) -> alt.Chart:
    metric = "Market Cap Weighted Return %"
    chart_rows = rows.copy()
    if not chart_rows.empty and metric in chart_rows and "Date" in chart_rows:
        chart_rows["Date"] = pd.to_datetime(chart_rows["Date"], errors="coerce")
        chart_rows[metric] = pd.to_numeric(chart_rows[metric], errors="coerce")
        chart_rows = chart_rows.dropna(subset=["Date", metric])
    if chart_rows.empty:
        chart_rows = pd.DataFrame(
            [{"Date": pd.Timestamp.today().normalize(), "Group": "No Data", metric: 0.0, "Symbols": 0}]
        )
    chart_rows["Date Label"] = chart_rows["Date"].dt.strftime("%m-%d")
    chart_rows["Return Label"] = chart_rows[metric].map(lambda value: f"{float(value):+.2f}%")
    date_order = (
        chart_rows.sort_values("Date")["Date Label"].drop_duplicates().tolist()
        if "Date Label" in chart_rows
        else []
    )
    group_order = chart_rows["Group"].drop_duplicates().tolist() if "Group" in chart_rows else ["No Data"]
    chart_height = max(GROUP_TREND_HEATMAP_MIN_HEIGHT, GROUP_TREND_HEATMAP_ROW_HEIGHT * len(group_order))
    base = (
        alt.Chart(chart_rows)
        .mark_rect(cornerRadius=2)
        .encode(
            x=alt.X(
                "Date Label:N",
                sort=date_order,
                title=None,
                axis=alt.Axis(labelAngle=0, labelFontSize=10),
            ),
            y=alt.Y(
                "Group:N",
                sort=group_order,
                title=None,
                axis=alt.Axis(labelLimit=240, labelFontSize=12),
            ),
            color=alt.Color(
                f"{metric}:Q",
                scale=_symmetric_return_scale(chart_rows[metric]),
                legend=alt.Legend(title="Return %", orient="bottom"),
            ),
            tooltip=["Date:T", "Group:N", "Return Label:N", "Symbols:Q", "Top Symbol:N"],
        )
    )
    text = (
        alt.Chart(chart_rows)
        .mark_text(fontSize=11)
        .encode(
            x=alt.X("Date Label:N", sort=date_order, title=None),
            y=alt.Y("Group:N", sort=group_order, title=None),
            text=alt.Text("Return Label:N"),
            color=alt.condition(
                f"datum['{metric}'] >= 8 || datum['{metric}'] <= -8",
                alt.value(OVERVIEW_COLOR_TEXT_INVERSE),
                alt.value(OVERVIEW_COLOR_TEXT),
            ),
        )
    )
    return (base + text).properties(height=chart_height)


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
