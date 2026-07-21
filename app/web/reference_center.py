from __future__ import annotations

import streamlit as st

from app.services.reference_center import (
    build_reference_center_payload,
    get_reference_item,
    validate_reference_destination,
)
from app.web.reference_center_react_component import (
    reference_center_react_component_available,
    render_reference_center_workbench,
)


BACKTEST_DESTINATION_PANELS = {
    "backtest_analysis": "Backtest Analysis",
    "practical_validation": "Practical Validation",
    "final_review": "Final Review",
}

REFERENCE_PAGE_TARGET_KEYS = {
    "overview",
    "institutional_portfolios",
    "ingestion",
    "backtest",
    "portfolio_monitoring",
}

_REFERENCE_PAGE_TARGETS: dict[str, object] = {}


def request_backtest_panel(panel: str) -> None:
    """Load Backtest routing only when a Reference navigation intent needs it."""
    from app.web.backtest_state import request_backtest_panel as request_panel

    request_panel(panel)


def normalize_reference_event(value: object) -> dict[str, str] | None:
    if not isinstance(value, dict):
        return None
    event = value.get("event")
    if not isinstance(event, dict) or event.get("id") != "navigate_to_surface":
        return None

    destination = validate_reference_destination(event.get("destination"))
    item_id = str(event.get("item_id") or "").strip()
    if destination is None or get_reference_item(item_id) is None:
        return None

    return {
        "id": "navigate_to_surface",
        "destination": destination,
        "item_id": item_id,
        "nonce": str(event.get("nonce") or "").strip(),
    }


def resolve_reference_navigation(destination: object) -> dict[str, str] | None:
    normalized_destination = validate_reference_destination(destination)
    if normalized_destination is None:
        return None
    panel = BACKTEST_DESTINATION_PANELS.get(normalized_destination)
    if panel is not None:
        return {"page_target_key": "backtest", "panel": panel}
    return {"page_target_key": normalized_destination, "panel": ""}


def configure_reference_center_page_targets(page_targets: dict[str, object]) -> None:
    _REFERENCE_PAGE_TARGETS.clear()
    _REFERENCE_PAGE_TARGETS.update(
        {
            key: value
            for key, value in dict(page_targets or {}).items()
            if key in REFERENCE_PAGE_TARGET_KEYS and value is not None
        }
    )


def render_reference_center_page() -> None:
    initial_item = st.query_params.get("item")
    payload = build_reference_center_payload(initial_item)
    if payload["invalid_initial_item"]:
        st.warning("변경되었거나 삭제된 Reference 항목입니다. 기본 화면에서 다시 찾아보세요.")

    if not reference_center_react_component_available():
        st.error("Reference 화면을 불러오지 못했습니다. 배포된 React build를 확인해 주세요.")
        st.caption("검색과 도움말 콘텐츠는 변경되지 않았습니다. 화면을 새로고침한 뒤 다시 시도해 주세요.")
        return

    component_value = render_reference_center_workbench(payload)
    event = normalize_reference_event(component_value)
    raw_event = component_value.get("event") if isinstance(component_value, dict) else None
    if raw_event and event is None:
        st.warning("허용되지 않은 Reference 이동 요청입니다. 현재 상세 화면을 유지합니다.")
        return
    if event is None:
        return

    navigation = resolve_reference_navigation(event["destination"])
    if navigation is None:
        st.warning("이 Reference 항목의 이동 위치를 확인하지 못했습니다.")
        return
    page_target = _REFERENCE_PAGE_TARGETS.get(navigation["page_target_key"])
    if page_target is None:
        st.warning("연결된 제품 화면을 열 수 없습니다. 상단 navigation에서 직접 이동해 주세요.")
        return

    if navigation["panel"]:
        request_backtest_panel(navigation["panel"])
    st.switch_page(page_target)
