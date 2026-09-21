"""Futures-only UI: two stored-price windows and a bounded refresh command."""

from copy import deepcopy
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import streamlit as st

from app.jobs.futures_macro_refresh import run_futures_macro_observation_refresh
from app.services.overview.futures_macro import build_futures_macro_intraday_read_model
from app.web.overview.futures_macro_react_component import (
    futures_macro_react_component_available,
    render_futures_macro_react_workbench,
)

STATUS_LABELS = {
    "AVAILABLE": "관측 가능",
    "PARTIAL": "일부 자료 부족",
    "STALE": "관측 지연",
    "MARKET_CLOSED": "정규 거래 중단 · 마지막 관측",
    "UNAVAILABLE": "비교 자료 부족",
}


def render_futures_macro_header():
    st.markdown("### 선물 매크로")
    st.caption(
        "미국장 마감 이후와 최근 1시간의 가격 변화, 주가지수 동행과 국채·달러 조합의 실제 판정을 봅니다."
    )


def _futures_macro_react_event_payload(event):
    if not isinstance(event, dict):
        return {}
    return event.get("event") if isinstance(event.get("event"), dict) else event


def dispatch_futures_macro_action(event, *, state, run_action=None):
    """Acknowledge the actual result and suppress replayed or concurrent session commands."""
    event = _futures_macro_react_event_payload(event)
    action, nonce = event.get("id"), event.get("nonce")
    if action not in {"daily_refresh", "economic_cycle"} or not nonce:
        return False
    if state.get("futures_macro_ack") == nonce or state.get("futures_macro_pending"):
        return False
    state["futures_macro_pending"] = True
    try:
        if action == "daily_refresh":
            state["futures_macro_result"] = (
                run_action or run_futures_macro_observation_refresh
            )()
        else:
            state["futures_macro_destination"] = "economic-cycle"
    except Exception:
        state["futures_macro_result"] = {
            "status": "failed",
            "message": "갱신을 완료하지 못했습니다. 마지막 저장 관측을 표시합니다. 다시 시도해 주세요.",
        }
    finally:
        state["futures_macro_pending"] = False
        state["futures_macro_ack"] = nonce
    return True


def _kst(value):
    return (
        datetime.fromisoformat(value)
        .astimezone(ZoneInfo("Asia/Seoul"))
        .strftime("%m-%d %H:%M")
        if value
        else "확인 불가"
    )


def _render_intraday_fallback(payload):
    """Fallback consumes the same prices and interpretation as the React surface."""
    event = None
    if st.button("최신 데이터 반영", key="futures_macro_refresh"):
        event = {"id": "daily_refresh", "nonce": datetime.now(timezone.utc).isoformat()}
    period = st.radio(
        "비교 구간",
        ["since_close", "last_hour"],
        format_func=lambda x: (
            "미국장 마감 이후" if x == "since_close" else "최근 1시간"
        ),
        horizontal=True,
    )
    w = payload["windows"][period]
    reading = w["reading"]
    st.subheader(reading["headline"])
    st.write(reading["interpretation"])
    st.caption(
        f"{STATUS_LABELS[w['status']]} · {_kst(w.get('start_utc'))} → {_kst(w.get('end_utc'))} KST"
    )
    context = w["time_context"]
    st.markdown(f"**선물 가격 변화 · {context['label']}**")
    st.caption(
        f"비교 시작 {_kst(w.get('start_utc'))} → 마지막 관측 {_kst(w.get('end_utc'))} KST · "
        f"화면 조회 {_kst(context['evaluated_at_utc'])} KST 기준 · "
        f"마지막 관측은 조회 시점보다 {context['observation_age_minutes']}분 전"
        if context["observation_age_minutes"] is not None
        else "비교 시각 확인 불가"
    )
    st.caption(context["explanation"])
    cycle = payload["cycle_background"]
    st.caption(
        f"경기 배경: {cycle['state']} · {cycle.get('as_of_date') or '기준일 없음'}"
    )
    if st.button("경기국면 보기", key="futures_macro_cycle"):
        event = {
            "id": "economic_cycle",
            "nonce": datetime.now(timezone.utc).isoformat(),
        }
    for col, price in zip(st.columns(3), payload["windows"][period]["prices"][:3]):
        value = price["return_pct"]
        col.metric(price["label"], "—" if value is None else f"{value:+.2f}%")
        col.caption(price["description"])
    for col, price in zip(st.columns(3), payload["windows"][period]["prices"][3:]):
        value = price["return_pct"]
        col.metric(price["label"], "—" if value is None else f"{value:+.2f}%")
        col.caption(price["description"])
    st.markdown("**두 가지 확인 결과**")
    for col, check in zip(st.columns(2), reading["condition_results"]):
        with col:
            st.markdown(f"**{check['title']}**")
            for evidence in check["evidence"]:
                value = evidence["return_pct"]
                formatted = "—" if value is None else f"{value:+.2f}%"
                st.write(f"{evidence['label']} {formatted} · {evidence['direction']}")
            st.markdown(f"**확인 결과: {check['verdict']}**")
            st.write(check["explanation"])
            comparison = check["comparison"]
            st.caption(comparison["summary"])
            if comparison.get("previous_evidence"):
                with st.expander("1시간 전 판정에 사용한 값"):
                    st.caption(
                        f"{_kst(comparison['previous_start_utc'])} → {_kst(comparison['previous_end_utc'])} KST"
                    )
                    for evidence in comparison["previous_evidence"]:
                        st.write(
                            f"{evidence['label']} {evidence['return_pct']:+.2f}% · {evidence['direction']}"
                        )
    for fact in reading["counter_evidence"]:
        st.info(fact)
    st.caption(
        "상승·하락은 0.01% 표시 단위의 방향이며 영향의 크기를 뜻하지 않습니다. 현재와 1시간 전의 관측 비교이며 다음 시간의 방향 예측이 아닙니다."
    )
    with st.expander("지표 구성과 계산 기준"):
        st.write(w["evidence"]["source"])
        st.write("누락: " + (", ".join(w["missing_symbols"]) or "핵심 비교 자료 확보"))
        for line in w["evidence"]["caveats"]:
            st.caption(line)
        st.caption(
            "장중 조건 검증 전입니다. 현재 구간의 이후 상승·하락 확률은 제공하지 않습니다."
        )
    with st.expander("추가 관측 근거"):
        for fact in reading["observation_facts"]:
            st.write(f"• {fact}")
    return event


def _render_futures_macro_panel(*, detail_expanded=False):
    try:
        payload = build_futures_macro_intraday_read_model()
        st.session_state["futures_macro_last_good_payload"] = payload
    except Exception:
        st.error("저장 자료를 읽지 못했습니다. 잠시 후 다시 읽어 주세요.")
        payload = deepcopy(st.session_state.get("futures_macro_last_good_payload"))
        if not payload:
            if st.button("다시 시도", key="futures_macro_retry"):
                st.rerun()
            return
        from app.services.futures_macro_reading import (
            build_futures_macro_change_reading,
        )

        for window in payload["windows"].values():
            window["status"] = "STALE"
            window["reading"] = build_futures_macro_change_reading(window)
    payload["command"] = {
        "ack_nonce": st.session_state.get("futures_macro_ack"),
        "pending": bool(st.session_state.get("futures_macro_pending")),
        "result": {
            k: v
            for k, v in st.session_state.get("futures_macro_result", {}).items()
            if k in {"status", "message"}
        },
    }
    if futures_macro_react_component_available():
        event = render_futures_macro_react_workbench(
            payload, key="overview_futures_macro_workbench"
        )
    else:
        result = payload["command"]["result"]
        if result:
            st.info(result.get("message"))
        event = _render_intraday_fallback(payload)
    if dispatch_futures_macro_action(event, state=st.session_state):
        destination = st.session_state.pop("futures_macro_destination", None)
        if destination:
            from app.web.overview.navigation import OVERVIEW_DEEP_TAB_QUERY_PARAM

            st.query_params[OVERVIEW_DEEP_TAB_QUERY_PARAM] = destination
        st.rerun()


def render_futures_macro_fragment(*, detail_expanded=False):
    @st.fragment
    def futures_macro_context_fragment():
        _render_futures_macro_panel(detail_expanded=detail_expanded)

    futures_macro_context_fragment()
