from __future__ import annotations

from html import escape
from typing import Any

import streamlit as st

from app.web.overview.components.common import *

def _macro_week_clusters_html(clusters: dict[str, Any]) -> str:
    html: list[str] = []
    for label, cluster in clusters.items():
        if not isinstance(cluster, dict):
            continue
        tone_color = escape(_overview_tone_color(cluster.get("tone")))
        count = _display_value(cluster.get("count"))
        review = cluster.get("review_count")
        review_text = f" · {review} review" if review not in (None, "", 0) else ""
        html.append(
            f'<span class="ov-macro-week-cluster" style="--ov-cluster-tone:{tone_color};">'
            f'<span class="ov-macro-week-cluster-label">{escape(str(label))}</span>'
            f'<span class="ov-macro-week-cluster-value">{escape(count)}{escape(review_text)}</span>'
            "</span>"
        )
    return "".join(html)


def _macro_week_days_label(value: Any) -> str:
    if value in (None, ""):
        return "date pending"
    try:
        day_number = int(value)
    except (TypeError, ValueError):
        return _display_value(value)
    if day_number < 0:
        return f"{abs(day_number)}d ago"
    if day_number == 0:
        return "today"
    return f"in {day_number}d"


def _macro_week_items_html(items: list[dict[str, Any]], *, limit: int = 4) -> str:
    html: list[str] = []
    for item in items[:limit]:
        tone_color = escape(_overview_tone_color(item.get("tone")))
        meta = (
            f"{_display_value(item.get('date'))} · {_display_value(item.get('window'))} · "
            f"{_macro_week_days_label(item.get('days_until'))} · "
            f"{_display_value(item.get('cluster'))}"
        )
        detail = (
            f"{_display_value(item.get('source_type'))} · {_display_value(item.get('freshness'))} · "
            f"{_display_value(item.get('quality_action'))}"
        )
        html.append(
            f'<article class="ov-macro-week-item" style="--ov-item-tone:{tone_color};">'
            f'<div class="ov-macro-week-item-meta">{escape(meta)}</div>'
            f'<div class="ov-macro-week-item-title">{escape(_display_value(item.get("title")))}</div>'
            f'<div class="ov-macro-week-item-detail">{escape(detail)}</div>'
            "</article>"
        )
    return "".join(html)


def _macro_week_section_html(title: str, note: str, items: list[dict[str, Any]]) -> str:
    items_html = _macro_week_items_html(items)
    if not items_html:
        return ""
    return (
        '<section class="ov-macro-week-section">'
        '<div class="ov-macro-week-section-head">'
        f'<div class="ov-macro-week-section-title">{escape(title)}</div>'
        f'<div class="ov-macro-week-section-note">{escape(note)}</div>'
        '</div>'
        f'<div class="ov-macro-week-items">{items_html}</div>'
        '</section>'
    )


def render_macro_week_lane(model: dict[str, Any]) -> None:
    summary = dict(model.get("summary") or {})
    tone_color = escape(_overview_tone_color(model.get("status")))
    clusters_html = _macro_week_clusters_html(dict(model.get("clusters") or {}))
    recent_html = _macro_week_section_html(
        "방금 지난 주요 이벤트",
        "최근 macro 발표가 시장 해석에 남기는 변수입니다.",
        list(model.get("recent_items") or []),
    )
    upcoming_html = _macro_week_section_html(
        "다가오는 주요 이벤트",
        "앞으로 확인할 macro / earnings 일정입니다.",
        list(model.get("upcoming_items") or []),
    )
    fallback_items_html = _macro_week_items_html(list(model.get("items") or [])) if not (recent_html or upcoming_html) else ""
    coverage = dict(model.get("coverage") or {})
    latest = _display_value(coverage.get("latest_collected_at"))
    empty_html = "" if (recent_html or upcoming_html or fallback_items_html) else '<div class="ov-events-empty">No near-term stored event rows in this lane.</div>'
    st.markdown(
        overview_ui_css()
        + f"""
<section class="ov-macro-week-lane" style="--ov-band-tone:{tone_color};">
  <div class="ov-macro-week-head">
    <div>
      <div class="ov-macro-week-kicker">Macro Week Lane</div>
      <div class="ov-macro-week-title">{escape(_display_value(summary.get("headline")))}</div>
      <div class="ov-macro-week-detail">{escape(_display_value(summary.get("detail")))} · Latest collection: {escape(latest)}</div>
    </div>
    <span class="ov-macro-week-status">{escape(_display_value(model.get("status")))}</span>
  </div>
  <div class="ov-macro-week-clusters">{clusters_html}</div>
  {recent_html}
  {upcoming_html}
  <div class="ov-macro-week-items">{fallback_items_html}</div>
  {empty_html}
  <div class="ov-macro-week-boundary">{escape(_display_value(model.get("boundary_note")))}</div>
</section>""",
        unsafe_allow_html=True,
    )


def render_events_summary_strip(items: list[dict[str, Any]]) -> None:
    item_html: list[str] = []
    for index, item in enumerate(items):
        detail = item.get("detail")
        detail_html = (
            f'<div class="ov-events-summary-detail">{escape(str(detail))}</div>'
            if detail not in (None, "")
            else ""
        )
        tone = escape(_overview_tone_color(item.get("tone") or ("primary" if index == 0 else "neutral")))
        class_name = "ov-events-summary-item ov-events-summary-primary" if index == 0 else "ov-events-summary-item"
        item_html.append(
            f'<div class="{class_name}" style="--ov-event-tone:{tone};">'
            '<div class="ov-events-summary-label-row">'
            '<span class="ov-events-summary-dot"></span>'
            f'<span class="ov-events-summary-label">{escape(str(item.get("label") or "-"))}</span>'
            "</div>"
            f'<div class="ov-events-summary-value">{escape(_display_value(item.get("value")))}</div>'
            f"{detail_html}"
            "</div>"
        )
    st.markdown(
        overview_ui_css()
        + f"""
<div class="ov-events-summary">
          {"".join(item_html)}
        </div>""",
        unsafe_allow_html=True,
    )


def render_event_source_lane(sources: list[dict[str, Any]]) -> None:
    source_html: list[str] = []
    for source in sources:
        tone_color = _overview_tone_color(source.get("tone"))
        body_html = ""
        if any(key in source for key in ("rows", "latest", "review_count")):
            body_html = (
                '<div class="ov-events-source-body">'
                '<div class="ov-events-source-field">'
                '<div class="ov-events-source-field-label">Rows</div>'
                f'<div class="ov-events-source-field-value">{escape(_display_value(source.get("rows")))}</div>'
                "</div>"
                '<div class="ov-events-source-field">'
                '<div class="ov-events-source-field-label">Latest</div>'
                f'<div class="ov-events-source-field-value">{escape(_display_value(source.get("latest")))}</div>'
                "</div>"
                '<div class="ov-events-source-field">'
                '<div class="ov-events-source-field-label">Review</div>'
                f'<div class="ov-events-source-field-value">{escape(_display_value(source.get("review_count")))}</div>'
                "</div>"
                "</div>"
            )
        elif source.get("detail") not in (None, ""):
            body_html = f'<div class="ov-events-source-detail">{escape(_display_value(source.get("detail")))}</div>'
        source_html.append(
            f'<div class="ov-events-source" style="--ov-event-tone:{escape(tone_color)};">'
            '<div class="ov-events-source-head">'
            f'<span class="ov-events-source-title">{escape(str(source.get("title") or "-"))}</span>'
            f'<span class="ov-events-source-state">{escape(_display_value(source.get("status")))}</span>'
            "</div>"
            f"{body_html}"
            "</div>"
        )
    st.markdown(
        overview_ui_css()
        + f"""
<div class="ov-events-source-lane">
          {"".join(source_html)}
        </div>""",
        unsafe_allow_html=True,
    )


def render_event_warning_strip(warnings: list[Any]) -> None:
    warning_html: list[str] = []
    for warning in warnings:
        warning_html.append(
            '<div class="ov-events-warning">'
            '<span class="ov-events-warning-label">Review</span>'
            f'<span>{escape(str(warning))}</span>'
            "</div>"
        )
    if not warning_html:
        return
    st.markdown(
        overview_ui_css()
        + f"""
<div class="ov-events-warning-stack">
          {"".join(warning_html)}
        </div>""",
        unsafe_allow_html=True,
    )


def render_event_agenda_sections(
    sections: list[dict[str, Any]],
    *,
    empty_message: str = "No event rows match the selected filters.",
) -> None:
    section_html: list[str] = []
    for section in sections:
        rows = list(section.get("rows") or [])
        if not rows:
            continue
        row_html: list[str] = []
        for row in rows:
            badges = "".join(_badge_html(badge.get("label"), badge.get("tone")) for badge in row.get("badges") or [])
            row_html.append(
                '<div class="ov-events-row">'
                '<div class="ov-events-date">'
                f'<div class="ov-events-day">{escape(_display_value(row.get("date")))}</div>'
                f'<div class="ov-events-countdown">{escape(_display_value(row.get("countdown")))}</div>'
                "</div>"
                '<div class="ov-events-main">'
                f'<div class="ov-events-title">{escape(_display_value(row.get("title")))}</div>'
                f'<div class="ov-events-subtitle">{escape(_display_value(row.get("subtitle")))}</div>'
                "</div>"
                f'<div class="ov-events-badges">{badges}</div>'
                "</div>"
            )
        section_html.append(
            '<div class="ov-events-section">'
            '<div class="ov-events-section-head">'
            f'<span class="ov-events-section-title">{escape(str(section.get("title") or "-"))}</span>'
            f'<span class="ov-events-section-meta">{escape(str(section.get("meta") or f"{len(rows)} events"))}</span>'
            "</div>"
            f"{''.join(row_html)}"
            "</div>"
        )
    if not section_html:
        section_html.append(f'<div class="ov-events-empty">{escape(empty_message)}</div>')
    st.markdown(
        overview_ui_css()
        + f"""
<div class="ov-events-agenda">
          {"".join(section_html)}
        </div>""",
        unsafe_allow_html=True,
    )

__all__ = [
    "_macro_week_clusters_html",
    "_macro_week_days_label",
    "_macro_week_items_html",
    "_macro_week_section_html",
    "render_macro_week_lane",
    "render_events_summary_strip",
    "render_event_source_lane",
    "render_event_warning_strip",
    "render_event_agenda_sections",
]
