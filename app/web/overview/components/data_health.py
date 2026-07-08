from __future__ import annotations

from html import escape
from typing import Any

import streamlit as st

from app.web.overview.components.common import *

def _data_handoff_count_tone(label: str) -> str:
    normalized = str(label or "").upper()
    if normalized in {"OK", "SUCCESS"}:
        return "positive"
    if normalized in {"FAILED", "MISSING", "STALE"}:
        return "danger"
    if normalized in {"PARTIAL", "DUE", "REVIEW"}:
        return "warning"
    return "neutral"


def _data_handoff_counts_html(counts: dict[str, Any]) -> str:
    if not counts:
        return ""
    ordered_labels = ["Failed", "Missing", "Stale", "Partial", "Due", "OK"]
    labels = [label for label in ordered_labels if label in counts]
    labels.extend(sorted(str(label) for label in counts if str(label) not in labels))
    html: list[str] = []
    for label in labels:
        value = counts.get(label)
        tone = escape(_overview_tone_color(_data_handoff_count_tone(label)))
        html.append(
            f'<span class="ov-data-handoff-count" style="--ov-count-tone:{tone};">'
            f"{escape(str(label))}: {escape(_display_value(value))}"
            "</span>"
        )
    return "".join(html)


def _data_handoff_items_html(items: list[dict[str, Any]]) -> str:
    html: list[str] = []
    for item in items:
        tone_color = escape(_overview_tone_color(item.get("tone")))
        alternate = item.get("alternate_surface")
        alternate_text = f" · Alternative: {alternate}" if alternate not in (None, "", "-") else ""
        html.append(
            f'<article class="ov-data-handoff-card" style="--ov-item-tone:{tone_color};">'
            '<div class="ov-data-handoff-card-head">'
            f'<div class="ov-data-handoff-area">{escape(_display_value(item.get("area")))}</div>'
            f'<div class="ov-data-handoff-rank">#{escape(_display_value(item.get("rank")))} · {escape(_display_value(item.get("status")))}</div>'
            "</div>"
            f'<div class="ov-data-handoff-meta">{escape(_display_value(item.get("reason")))}</div>'
            f'<div class="ov-data-handoff-action"><strong>Next:</strong> {escape(_display_value(item.get("next_action")))}</div>'
            f'<div class="ov-data-handoff-target"><strong>Go to:</strong> {escape(_display_value(item.get("target_surface")))}'
            f'<br><strong>Owner:</strong> {escape(_display_value(item.get("owner_surface")))}{escape(alternate_text)}</div>'
            "</article>"
        )
    return "".join(html)


def render_data_health_ingestion_handoff(model: dict[str, Any]) -> None:
    summary = dict(model.get("summary") or {})
    tone_color = escape(_overview_tone_color(model.get("status")))
    counts_html = _data_handoff_counts_html(dict(model.get("counts") or {}))
    items = list(model.get("priority_items") or [])
    items_html = _data_handoff_items_html(items)
    empty_html = (
        ""
        if items
        else f'<div class="ov-data-handoff-empty">{escape(_display_value(summary.get("detail")))}</div>'
    )
    st.markdown(
        overview_ui_css()
        + f"""
<section class="ov-data-handoff" style="--ov-handoff-tone:{tone_color};">
  <div class="ov-data-handoff-head">
    <div>
      <div class="ov-data-handoff-kicker">Data Health Handoff</div>
      <div class="ov-data-handoff-title">{escape(_display_value(summary.get("headline")))}</div>
      <div class="ov-data-handoff-detail">{escape(_display_value(summary.get("detail")))}</div>
    </div>
    <span class="ov-data-handoff-status">{escape(_display_value(model.get("status")))}</span>
  </div>
  <div class="ov-data-handoff-counts">{counts_html}</div>
  <div class="ov-data-handoff-grid">{items_html}</div>
  {empty_html}
  <div class="ov-data-handoff-boundary">{escape(_display_value(model.get("boundary_note")))}</div>
</section>""",
        unsafe_allow_html=True,
    )

__all__ = [
    "_data_handoff_count_tone",
    "_data_handoff_counts_html",
    "_data_handoff_items_html",
    "render_data_health_ingestion_handoff",
]
