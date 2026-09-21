"""Futures-only UI: two stored-price windows and a bounded refresh command."""

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
        "미국장 마감 이후와 최근 1시간의 변화, 함께 움직인 자산과 다음 확인 조건을 봅니다."
    )


def _futures_macro_react_event_payload(event):
    if not isinstance(event, dict):
        return {}
    return event.get("event") if isinstance(event.get("event"), dict) else event


def dispatch_futures_macro_action(event, *, state, run_action=None):
    """Acknowledge the actual result and suppress replayed or concurrent session commands."""
    event = _futures_macro_react_event_payload(event)
    action, nonce = event.get("id"), event.get("nonce")
    if action not in {"daily_refresh", "reload", "economic_cycle"} or not nonce:
        return False
    if state.get("futures_macro_ack") == nonce or state.get("futures_macro_pending"):
        return False
    state["futures_macro_pending"] = True
    try:
        if action == "daily_refresh":
            state["futures_macro_result"] = (
                run_action or run_futures_macro_observation_refresh
            )()
        elif action == "reload":
            state["futures_macro_result"] = {
                "status": "success",
                "message": "저장 자료를 다시 읽었습니다.",
            }
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
    left, right = st.columns(2)
    if left.button("최신 데이터 반영", key="futures_macro_refresh"):
        event = {"id": "daily_refresh", "nonce": datetime.now(timezone.utc).isoformat()}
    if right.button("저장 자료 다시 읽기", key="futures_macro_reload"):
        event = {"id": "reload", "nonce": datetime.now(timezone.utc).isoformat()}
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
    st.caption(
        f"{STATUS_LABELS[w['status']]} · {_kst(w.get('start_utc'))} → {_kst(w.get('end_utc'))} KST"
    )
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
    for col, price in zip(st.columns(3), payload["windows"][period]["prices"][3:]):
        value = price["return_pct"]
        col.metric(price["label"], "—" if value is None else f"{value:+.2f}%")
    st.markdown("**관측 사실**")
    for fact in reading["observation_facts"]:
        st.write(f"• {fact}")
    st.markdown("**가능한 의미**")
    st.write(reading["interpretation"])
    for fact in reading["counter_evidence"]:
        st.info(fact)
    st.markdown("**다음 확인 조건**")
    for check in reading["next_checks"]:
        st.write(f"• {check}")
    with st.expander("계산 기준과 자료 공백"):
        st.write(w["evidence"]["source"])
        st.write("누락: " + (", ".join(w["missing_symbols"]) or "핵심 비교 자료 확보"))
        for line in w["evidence"]["caveats"]:
            st.caption(line)
    with st.expander("과거 사례 검증"):
        st.write(
            "장중 조건 검증 전입니다. 현재 구간의 이후 상승·하락 확률은 제공하지 않습니다."
        )
    return event


def _render_futures_macro_panel(*, detail_expanded=False):
    try:
        payload = build_futures_macro_intraday_read_model()
        st.session_state["futures_macro_last_good_payload"] = payload
    except Exception:
        st.error("저장 자료를 읽지 못했습니다. 잠시 후 다시 읽어 주세요.")
        if st.button("저장 자료 다시 읽기", key="futures_macro_retry"):
            st.rerun()
        return
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
