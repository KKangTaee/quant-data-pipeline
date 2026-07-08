from __future__ import annotations

from html import escape
from typing import Any

import streamlit as st


def _display_value(value: Any) -> str:
    if value in (None, ""):
        return "-"
    return str(value)


def _safe_tone(tone: Any) -> str:
    tone_text = str(tone or "neutral").strip().lower()
    if tone_text in {"positive", "warning", "danger", "neutral", "info"}:
        return tone_text
    return "neutral"


def render_fr_styles() -> None:
    st.markdown(
        """
        <style>
          :root {
            --fr-ink: #111827;
            --fr-muted: #5f6b7a;
            --fr-subtle: #8491a3;
            --fr-bg: #f7f8fa;
            --fr-surface: #ffffff;
            --fr-panel: #f8fafc;
            --fr-line: rgba(31, 41, 55, 0.12);
            --fr-line-strong: rgba(31, 41, 55, 0.18);
            --fr-positive: #0f766e;
            --fr-warning: #b45309;
            --fr-danger: #b91c1c;
            --fr-info: #2563eb;
            --fr-neutral: #475569;
          }
          .fr-shell,
          .fr-shell * {
            box-sizing: border-box;
            letter-spacing: 0;
          }
          .fr-shell {
            width: 100%;
            margin: 0 0 1rem 0;
            color: var(--fr-ink);
          }
          .fr-command {
            display: grid;
            grid-template-columns: minmax(0, 1.5fr) minmax(260px, 0.82fr);
            gap: 0.9rem;
            align-items: stretch;
            padding: 1rem;
            border: 1px solid var(--fr-line-strong);
            border-radius: 8px;
            background: var(--fr-surface);
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.08);
          }
          .fr-command-main {
            display: grid;
            gap: 0.72rem;
            align-content: start;
          }
          .fr-eyebrow,
          .fr-card-kicker,
          .fr-step-kicker,
          .fr-section-eyebrow {
            font-size: 0.74rem;
            line-height: 1.2;
            font-weight: 780;
            color: var(--fr-muted);
            overflow-wrap: anywhere;
          }
          .fr-command-title {
            font-size: 1.48rem;
            line-height: 1.15;
            font-weight: 840;
            color: var(--fr-ink);
            overflow-wrap: anywhere;
          }
          .fr-command-detail {
            max-width: 78rem;
            font-size: 0.92rem;
            line-height: 1.48;
            color: var(--fr-muted);
            overflow-wrap: anywhere;
          }
          .fr-kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(min(100%, 145px), 1fr));
            gap: 0.58rem;
          }
          .fr-kpi {
            min-height: 82px;
            padding: 0.72rem 0.76rem;
            border: 1px solid var(--fr-line);
            border-radius: 8px;
            background: var(--fr-panel);
          }
          .fr-kpi-label {
            font-size: 0.72rem;
            font-weight: 720;
            color: var(--fr-muted);
            overflow-wrap: anywhere;
          }
          .fr-kpi-value {
            margin-top: 0.26rem;
            font-size: 1.02rem;
            line-height: 1.2;
            font-weight: 820;
            color: var(--fr-ink);
            overflow-wrap: anywhere;
          }
          .fr-kpi-detail {
            margin-top: 0.25rem;
            font-size: 0.76rem;
            line-height: 1.28;
            color: var(--fr-subtle);
            overflow-wrap: anywhere;
          }
          .fr-route-card,
          .fr-action-route {
            min-height: 132px;
            display: grid;
            gap: 0.48rem;
            align-content: start;
            padding: 0.92rem;
            border: 1px solid var(--fr-line);
            border-left: 4px solid var(--fr-neutral);
            border-radius: 8px;
            background: #f8fafc;
          }
          .fr-tone-positive { border-left-color: var(--fr-positive); }
          .fr-tone-warning { border-left-color: var(--fr-warning); }
          .fr-tone-danger { border-left-color: var(--fr-danger); }
          .fr-tone-info { border-left-color: var(--fr-info); }
          .fr-tone-neutral { border-left-color: var(--fr-neutral); }
          .fr-route-label {
            font-size: 0.78rem;
            font-weight: 760;
            color: var(--fr-muted);
            overflow-wrap: anywhere;
          }
          .fr-route-value {
            font-size: 1.08rem;
            line-height: 1.22;
            font-weight: 840;
            color: var(--fr-ink);
            overflow-wrap: anywhere;
          }
          .fr-route-detail {
            font-size: 0.82rem;
            line-height: 1.38;
            color: var(--fr-muted);
            overflow-wrap: anywhere;
          }
          .fr-flow {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(min(100%, 165px), 1fr));
            gap: 0.62rem;
            margin: 0.45rem 0 1rem 0;
          }
          .fr-step {
            min-height: 96px;
            padding: 0.78rem 0.82rem;
            border: 1px solid var(--fr-line);
            border-left: 4px solid var(--fr-neutral);
            border-radius: 8px;
            background: var(--fr-surface);
          }
          .fr-step-marker {
            display: inline-flex;
            min-width: 1.6rem;
            height: 1.6rem;
            align-items: center;
            justify-content: center;
            margin-bottom: 0.42rem;
            border-radius: 999px;
            background: #e2e8f0;
            color: #111827;
            font-size: 0.78rem;
            font-weight: 820;
          }
          .fr-step-title {
            font-size: 0.9rem;
            line-height: 1.25;
            font-weight: 820;
            color: var(--fr-ink);
            overflow-wrap: anywhere;
          }
          .fr-step-detail {
            margin-top: 0.24rem;
            font-size: 0.78rem;
            line-height: 1.35;
            color: var(--fr-muted);
            overflow-wrap: anywhere;
          }
          .fr-section {
            margin: 1.05rem 0 0.55rem 0;
            padding: 0.86rem 0.95rem;
            border: 1px solid var(--fr-line);
            border-left: 4px solid var(--fr-neutral);
            border-radius: 8px;
            background: var(--fr-surface);
          }
          .fr-section-title {
            font-size: 1.04rem;
            line-height: 1.25;
            font-weight: 840;
            color: var(--fr-ink);
            overflow-wrap: anywhere;
          }
          .fr-section-detail {
            margin-top: 0.34rem;
            max-width: 78rem;
            font-size: 0.88rem;
            line-height: 1.45;
            color: var(--fr-muted);
            overflow-wrap: anywhere;
          }
          .fr-lane-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(min(100%, var(--fr-lane-min, 230px)), 1fr));
            gap: 0.72rem;
            margin: 0.45rem 0 1rem 0;
          }
          .fr-lane {
            min-height: 132px;
            padding: 0.86rem 0.92rem;
            border: 1px solid var(--fr-line);
            border-left: 4px solid var(--fr-neutral);
            border-radius: 8px;
            background: var(--fr-surface);
          }
          .fr-lane-title {
            font-size: 0.98rem;
            line-height: 1.25;
            font-weight: 840;
            color: var(--fr-ink);
            overflow-wrap: anywhere;
          }
          .fr-lane-status {
            display: inline-flex;
            width: fit-content;
            margin-top: 0.5rem;
            padding: 0.2rem 0.52rem;
            border: 1px solid rgba(17, 24, 39, 0.1);
            border-radius: 999px;
            background: #eef2f7;
            color: #334155;
            font-size: 0.75rem;
            line-height: 1.2;
            font-weight: 780;
            overflow-wrap: anywhere;
          }
          .fr-lane-detail {
            margin-top: 0.54rem;
            font-size: 0.84rem;
            line-height: 1.42;
            color: var(--fr-muted);
            overflow-wrap: anywhere;
          }
          .fr-lane-meta {
            margin-top: 0.44rem;
            font-size: 0.77rem;
            line-height: 1.34;
            color: var(--fr-subtle);
            overflow-wrap: anywhere;
          }
          .fr-action {
            display: grid;
            grid-template-columns: minmax(0, 1.28fr) minmax(250px, 0.72fr);
            gap: 0.85rem;
            align-items: stretch;
            padding: 0.96rem;
            border: 1px solid var(--fr-line-strong);
            border-radius: 8px;
            background: var(--fr-surface);
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
          }
          .fr-action-title {
            font-size: 1.12rem;
            line-height: 1.24;
            font-weight: 840;
            color: var(--fr-ink);
            overflow-wrap: anywhere;
          }
          .fr-action-detail {
            margin-top: 0.38rem;
            font-size: 0.9rem;
            line-height: 1.45;
            color: var(--fr-muted);
            overflow-wrap: anywhere;
          }
          .fr-action-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 0.42rem;
            margin-top: 0.72rem;
          }
          .fr-chip {
            display: inline-flex;
            max-width: 100%;
            gap: 0.28rem;
            align-items: center;
            padding: 0.24rem 0.52rem;
            border: 1px solid var(--fr-line);
            border-radius: 999px;
            background: #f8fafc;
            color: #334155;
            font-size: 0.78rem;
            line-height: 1.2;
            font-weight: 740;
            overflow-wrap: anywhere;
            word-break: break-word;
          }
          .fr-chip-label {
            color: var(--fr-muted);
            font-weight: 760;
            white-space: nowrap;
          }
          .fr-chip-value {
            color: var(--fr-ink);
            overflow-wrap: anywhere;
            word-break: break-word;
          }
          @media (max-width: 760px) {
            .fr-command,
            .fr-action {
              grid-template-columns: 1fr;
              padding: 0.84rem;
            }
            .fr-route-card,
            .fr-action-route {
              min-height: auto;
            }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_fr_command_center(
    *,
    eyebrow: str,
    title: str,
    detail: str,
    route_label: str,
    route_value: str,
    route_detail: str,
    route_tone: str,
    kpis: list[dict[str, Any]],
) -> None:
    render_fr_styles()
    kpi_html: list[str] = []
    for item in kpis:
        label = escape(str(item.get("label") or ""))
        value = escape(_display_value(item.get("value")))
        detail_text = str(item.get("detail") or "")
        detail_html = f'<div class="fr-kpi-detail">{escape(detail_text)}</div>' if detail_text else ""
        kpi_html.append(
            '<div class="fr-kpi">'
            f'<div class="fr-kpi-label">{label}</div>'
            f'<div class="fr-kpi-value">{value}</div>'
            f"{detail_html}"
            "</div>"
        )
    tone = _safe_tone(route_tone)
    st.markdown(
        '<div class="fr-shell">'
        '<div class="fr-command">'
        '<div class="fr-command-main">'
        f'<div class="fr-eyebrow">{escape(eyebrow)}</div>'
        f'<div class="fr-command-title">{escape(title)}</div>'
        f'<div class="fr-command-detail">{escape(detail)}</div>'
        f'<div class="fr-kpi-grid">{"".join(kpi_html)}</div>'
        "</div>"
        '<div class="fr-command-side">'
        f'<div class="fr-route-card fr-tone-{tone}">'
        f'<div class="fr-route-label">{escape(route_label)}</div>'
        f'<div class="fr-route-value">{escape(route_value)}</div>'
        f'<div class="fr-route-detail">{escape(route_detail)}</div>'
        "</div>"
        "</div>"
        "</div></div>",
        unsafe_allow_html=True,
    )


def render_fr_flow(steps: list[dict[str, Any]]) -> None:
    render_fr_styles()
    html_steps: list[str] = []
    for index, step in enumerate(steps, start=1):
        tone = _safe_tone(step.get("tone"))
        marker = escape(str(step.get("marker") or index))
        kicker = str(step.get("kicker") or "")
        title = escape(str(step.get("title") or ""))
        detail = escape(str(step.get("detail") or ""))
        kicker_html = f'<div class="fr-step-kicker">{escape(kicker)}</div>' if kicker else ""
        html_steps.append(
            f'<div class="fr-step fr-tone-{tone}">'
            f'<div class="fr-step-marker">{marker}</div>'
            f"{kicker_html}"
            f'<div class="fr-step-title">{title}</div>'
            f'<div class="fr-step-detail">{detail}</div>'
            "</div>"
        )
    st.markdown(
        '<div class="fr-shell">'
        f'<div class="fr-flow">{"".join(html_steps)}</div>'
        "</div>",
        unsafe_allow_html=True,
    )


def render_fr_section_header(
    *,
    title: str,
    detail: str = "",
    eyebrow: str = "",
    tone: str = "neutral",
) -> None:
    render_fr_styles()
    tone_class = _safe_tone(tone)
    eyebrow_html = f'<div class="fr-section-eyebrow">{escape(eyebrow)}</div>' if eyebrow else ""
    detail_html = f'<div class="fr-section-detail">{escape(detail)}</div>' if detail else ""
    st.markdown(
        '<div class="fr-shell">'
        f'<div class="fr-section fr-tone-{tone_class}">'
        f"{eyebrow_html}"
        f'<div class="fr-section-title">{escape(title)}</div>'
        f"{detail_html}"
        "</div></div>",
        unsafe_allow_html=True,
    )


def render_fr_lane_grid(lanes: list[dict[str, Any]], *, min_width: int = 230) -> None:
    render_fr_styles()
    html_lanes: list[str] = []
    for lane in lanes:
        tone = _safe_tone(lane.get("tone"))
        kicker = str(lane.get("kicker") or "")
        title = str(lane.get("title") or "")
        status = _display_value(lane.get("status"))
        detail = str(lane.get("detail") or "")
        meta = str(lane.get("meta") or "")
        kicker_html = f'<div class="fr-card-kicker">{escape(kicker)}</div>' if kicker else ""
        status_html = f'<div class="fr-lane-status">{escape(status)}</div>' if status else ""
        detail_html = f'<div class="fr-lane-detail">{escape(detail)}</div>' if detail else ""
        meta_html = f'<div class="fr-lane-meta">{escape(meta)}</div>' if meta else ""
        html_lanes.append(
            f'<div class="fr-lane fr-tone-{tone}">'
            f"{kicker_html}"
            f'<div class="fr-lane-title">{escape(title)}</div>'
            f"{status_html}"
            f"{detail_html}"
            f"{meta_html}"
            "</div>"
        )
    st.markdown(
        '<div class="fr-shell">'
        f'<div class="fr-lane-grid" style="--fr-lane-min: {int(min_width)}px;">'
        f'{"".join(html_lanes)}'
        "</div></div>",
        unsafe_allow_html=True,
    )


def render_fr_action_panel(
    *,
    title: str,
    detail: str,
    route_label: str,
    route_value: str,
    route_detail: str,
    route_tone: str,
    meta_items: list[dict[str, Any]],
) -> None:
    render_fr_styles()
    chips: list[str] = []
    for item in meta_items:
        label = escape(str(item.get("label") or ""))
        value = escape(_display_value(item.get("value")))
        chips.append(
            '<span class="fr-chip">'
            f'<span class="fr-chip-label">{label}</span>'
            f'<span class="fr-chip-value">{value}</span>'
            "</span>"
        )
    tone = _safe_tone(route_tone)
    st.markdown(
        '<div class="fr-shell">'
        '<div class="fr-action">'
        '<div>'
        f'<div class="fr-action-title">{escape(title)}</div>'
        f'<div class="fr-action-detail">{escape(detail)}</div>'
        f'<div class="fr-action-meta">{"".join(chips)}</div>'
        "</div>"
        f'<div class="fr-action-route fr-tone-{tone}">'
        f'<div class="fr-route-label">{escape(route_label)}</div>'
        f'<div class="fr-route-value">{escape(route_value)}</div>'
        f'<div class="fr-route-detail">{escape(route_detail)}</div>'
        "</div>"
        "</div></div>",
        unsafe_allow_html=True,
    )
