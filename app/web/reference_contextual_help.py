from __future__ import annotations

import streamlit as st

from app.services.reference_contextual_help import get_reference_contextual_help

REFERENCE_PAGE_TARGET_KEYS = {
    "/guides": "guides",
    "/glossary": "glossary",
}
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


def _render_reference_link(label: str, target: str, page_targets: dict[str, object]) -> None:
    target_key = _reference_page_target_key(target)
    page_target = page_targets.get(target_key or "")
    if page_target is not None:
        st.page_link(page_target, label=label)
        return

    fallback_label = target_key.title() if target_key else "Reference"
    st.caption(f"{label}: Reference > {fallback_label}")


def render_reference_contextual_help(surface_key: str, *, expanded: bool = False) -> None:
    item = get_reference_contextual_help(surface_key)
    if not item:
        return

    page_targets = dict(_REFERENCE_PAGE_TARGETS)
    with st.expander(f"Reference help - {item.get('surface')}", expanded=expanded):
        st.caption(str(item.get("summary") or ""))
        cols = st.columns([0.34, 0.33, 0.33], gap="small")
        with cols[0]:
            st.markdown("**Guide focus**")
            st.caption(str(item.get("guide_focus") or "-"))
        with cols[1]:
            st.markdown("**Glossary terms**")
            terms = [f"`{term}`" for term in list(item.get("glossary_terms") or [])]
            st.caption(", ".join(terms) if terms else "-")
        with cols[2]:
            st.markdown("**Reference links**")
            links = list(item.get("links") or [])
            if not links:
                st.caption("-")
            for link in links:
                label = str(link.get("label") or "Reference")
                target = str(link.get("target") or "/guides")
                _render_reference_link(label, target, page_targets)

        next_checks = _markdown_list(list(item.get("next_checks") or []))
        if next_checks:
            st.markdown("**먼저 확인할 것**")
            st.markdown(next_checks)

        boundaries = _markdown_list(list(item.get("boundaries") or []))
        if boundaries:
            st.markdown("**경계**")
            st.markdown(boundaries)
