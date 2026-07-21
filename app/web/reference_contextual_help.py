from __future__ import annotations

import streamlit as st

from app.services.reference_contextual_help import get_reference_contextual_help


REFERENCE_PAGE_TARGET_KEYS = {"/reference": "reference"}
_REFERENCE_PAGE_TARGETS: dict[str, object] = {}


def _markdown_list(items: list[object]) -> str:
    return "\n".join(f"- {str(item)}" for item in items if str(item or "").strip())


def _reference_page_target_key(target: object) -> str | None:
    return REFERENCE_PAGE_TARGET_KEYS.get(str(target or "").strip())


def configure_reference_contextual_help_page_targets(page_targets: dict[str, object]) -> None:
    _REFERENCE_PAGE_TARGETS.clear()
    _REFERENCE_PAGE_TARGETS.update(
        {
            key: value
            for key, value in dict(page_targets or {}).items()
            if key in set(REFERENCE_PAGE_TARGET_KEYS.values()) and value is not None
        }
    )


def _render_reference_link(
    label: str,
    target: str,
    item_id: str,
    page_targets: dict[str, object],
) -> None:
    target_key = _reference_page_target_key(target)
    page_target = page_targets.get(target_key or "")
    if page_target is not None:
        st.page_link(
            page_target,
            label=label,
            query_params={"item": item_id},
        )
        return
    st.caption(f"{label}: Reference에서 `{item_id}`를 검색하세요.")


def render_reference_contextual_help(surface_key: str, *, expanded: bool = False) -> None:
    item = get_reference_contextual_help(surface_key)
    if not item:
        return

    page_targets = dict(_REFERENCE_PAGE_TARGETS)
    with st.expander(f"Reference help · {item.get('surface')}", expanded=expanded):
        st.caption(str(item.get("summary") or ""))

        links = list(item.get("links") or [])
        if links:
            st.markdown("**관련 Reference**")
            for link in links:
                _render_reference_link(
                    str(link.get("label") or "Reference"),
                    str(link.get("target") or "/reference"),
                    str(link.get("item_id") or ""),
                    page_targets,
                )

        next_checks = _markdown_list(list(item.get("next_checks") or []))
        if next_checks:
            st.markdown("**먼저 확인할 것**")
            st.markdown(next_checks)

        boundaries = _markdown_list(list(item.get("boundaries") or []))
        if boundaries:
            st.markdown("**경계**")
            st.markdown(boundaries)
