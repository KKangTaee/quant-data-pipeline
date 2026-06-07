from __future__ import annotations

from html import escape

import streamlit as st

from app.services.reference_contextual_help import get_reference_contextual_help


def _markdown_list(items: list[object]) -> str:
    return "\n".join(f"- {escape(str(item))}" for item in items if str(item or "").strip())


def render_reference_contextual_help(surface_key: str, *, expanded: bool = False) -> None:
    item = get_reference_contextual_help(surface_key)
    if not item:
        return

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
                label = escape(str(link.get("label") or "Reference"))
                target = escape(str(link.get("target") or "/guides"))
                st.markdown(f"- [{label}]({target})")

        next_checks = _markdown_list(list(item.get("next_checks") or []))
        if next_checks:
            st.markdown("**먼저 확인할 것**")
            st.markdown(next_checks)

        boundaries = _markdown_list(list(item.get("boundaries") or []))
        if boundaries:
            st.markdown("**경계**")
            st.markdown(boundaries)
