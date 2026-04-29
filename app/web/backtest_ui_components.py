from __future__ import annotations

from html import escape
from typing import Any

import streamlit as st


def _route_tone(route_label: str) -> str:
    normalized = route_label.lower()
    if any(term in normalized for term in ["ready", "pass", "proposal"]):
        return "positive"
    if any(term in normalized for term in ["hold", "watchlist", "review", "check"]):
        return "warning"
    if any(term in normalized for term in ["reject", "blocked", "fail"]):
        return "danger"
    return "neutral"


# Render long Backtest status strings as wrapping cards instead of truncating Streamlit metrics.
def render_status_card_grid(cards: list[dict[str, Any]]) -> None:
    html_cards: list[str] = []
    for card in cards:
        title = escape(str(card.get("title") or ""))
        value = escape(str(card.get("value") or "-"))
        detail = escape(str(card.get("detail") or ""))
        tone = escape(str(card.get("tone") or "neutral"))
        detail_html = f'<div class="bt-status-card-detail">{detail}</div>' if detail else ""
        html_cards.append(
            f'<div class="bt-status-card bt-status-card-{tone}">'
            f'<div class="bt-status-card-title">{title}</div>'
            f'<div class="bt-status-card-value">{value}</div>'
            f"{detail_html}"
            "</div>"
        )
    st.markdown(
        """
        <style>
          .bt-status-card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 0.75rem;
            margin: 0.35rem 0 1rem 0;
          }
          .bt-status-card {
            min-height: 104px;
            padding: 0.9rem 1rem;
            border: 1px solid rgba(49, 51, 63, 0.18);
            border-top: 4px solid #64748b;
            border-radius: 8px;
            background: #ffffff;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
          }
          .bt-status-card-positive { border-top-color: #0f766e; }
          .bt-status-card-warning { border-top-color: #b45309; }
          .bt-status-card-danger { border-top-color: #b91c1c; }
          .bt-status-card-neutral { border-top-color: #475569; }
          .bt-status-card-title {
            font-size: 0.86rem;
            font-weight: 650;
            color: #475569;
            margin-bottom: 0.45rem;
            overflow-wrap: anywhere;
          }
          .bt-status-card-value {
            font-size: 1.35rem;
            font-weight: 700;
            line-height: 1.25;
            color: #111827;
            overflow-wrap: anywhere;
            word-break: break-word;
          }
          .bt-status-card-detail {
            margin-top: 0.45rem;
            font-size: 0.82rem;
            line-height: 1.3;
            color: #64748b;
            overflow-wrap: anywhere;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="bt-status-card-grid">{"".join(html_cards)}</div>',
        unsafe_allow_html=True,
    )


# Render the candidate review artifact chain as compact cards with one-line meaning and status.
def render_artifact_pipeline(cards: list[dict[str, Any]]) -> None:
    html_cards: list[str] = []
    for index, card in enumerate(cards, start=1):
        title = escape(str(card.get("title") or ""))
        detail = escape(str(card.get("detail") or ""))
        status = escape(str(card.get("status") or "-"))
        tone = escape(str(card.get("tone") or "neutral"))
        html_cards.append(
            f'<div class="bt-artifact-card bt-artifact-card-{tone}">'
            f'<div class="bt-artifact-step">{index}</div>'
            f'<div class="bt-artifact-title">{title}</div>'
            f'<div class="bt-artifact-detail">{detail}</div>'
            f'<div class="bt-artifact-status">{status}</div>'
            "</div>"
        )
    st.markdown(
        """
        <style>
          .bt-artifact-pipeline {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(176px, 1fr));
            gap: 0.75rem;
            margin: 0.45rem 0 1rem 0;
          }
          .bt-artifact-card {
            position: relative;
            min-height: 142px;
            padding: 0.95rem 1rem 0.9rem 1rem;
            border: 1px solid rgba(49, 51, 63, 0.16);
            border-radius: 8px;
            background: #ffffff;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
          }
          .bt-artifact-card-positive { border-top: 4px solid #0f766e; }
          .bt-artifact-card-warning { border-top: 4px solid #b45309; }
          .bt-artifact-card-danger { border-top: 4px solid #b91c1c; }
          .bt-artifact-card-neutral { border-top: 4px solid #64748b; }
          .bt-artifact-step {
            width: 1.55rem;
            height: 1.55rem;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 800;
            color: #ffffff;
            background: #475569;
            margin-bottom: 0.55rem;
          }
          .bt-artifact-card-positive .bt-artifact-step { background: #0f766e; }
          .bt-artifact-card-warning .bt-artifact-step { background: #b45309; }
          .bt-artifact-card-danger .bt-artifact-step { background: #b91c1c; }
          .bt-artifact-title {
            font-size: 1.02rem;
            font-weight: 760;
            color: #111827;
            line-height: 1.25;
            overflow-wrap: anywhere;
          }
          .bt-artifact-detail {
            margin-top: 0.45rem;
            min-height: 2.45rem;
            font-size: 0.86rem;
            line-height: 1.35;
            color: #475569;
            overflow-wrap: anywhere;
          }
          .bt-artifact-status {
            display: inline-flex;
            align-items: center;
            margin-top: 0.65rem;
            padding: 0.22rem 0.55rem;
            border-radius: 999px;
            background: #f1f5f9;
            color: #334155;
            font-size: 0.78rem;
            font-weight: 720;
            overflow-wrap: anywhere;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="bt-artifact-pipeline">{"".join(html_cards)}</div>',
        unsafe_allow_html=True,
    )


# Render a step's purpose through input/action/output cards instead of long instructional text.
def render_step_io_summary(
    *,
    input_label: str,
    input_detail: str,
    action_label: str,
    action_detail: str,
    output_label: str,
    output_detail: str,
) -> None:
    items = [
        ("Input", input_label, input_detail),
        ("Action", action_label, action_detail),
        ("Output", output_label, output_detail),
    ]
    html_items: list[str] = []
    for eyebrow, label, detail in items:
        html_items.append(
            '<div class="bt-io-card">'
            f'<div class="bt-io-eyebrow">{escape(eyebrow)}</div>'
            f'<div class="bt-io-label">{escape(label)}</div>'
            f'<div class="bt-io-detail">{escape(detail)}</div>'
            "</div>"
        )
    st.markdown(
        """
        <style>
          .bt-io-strip {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 0.65rem;
            margin: 0.35rem 0 1rem 0;
          }
          .bt-io-card {
            padding: 0.75rem 0.85rem;
            border: 1px solid rgba(49, 51, 63, 0.14);
            border-left: 4px solid #64748b;
            border-radius: 8px;
            background: #f8fafc;
          }
          .bt-io-eyebrow {
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0;
            color: #64748b;
            text-transform: uppercase;
            margin-bottom: 0.25rem;
          }
          .bt-io-label {
            font-size: 0.98rem;
            line-height: 1.25;
            font-weight: 760;
            color: #111827;
            overflow-wrap: anywhere;
          }
          .bt-io-detail {
            margin-top: 0.35rem;
            font-size: 0.84rem;
            line-height: 1.35;
            color: #475569;
            overflow-wrap: anywhere;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="bt-io-strip">{"".join(html_items)}</div>',
        unsafe_allow_html=True,
    )


# Render route/readiness decisions with wrapping route labels and a visible operator verdict.
def render_readiness_route_panel(
    *,
    route_label: str,
    score: float,
    blockers_count: int,
    verdict: str,
    next_action: str,
    route_title: str = "Route",
    score_title: str = "Readiness",
) -> None:
    route = escape(route_label or "-")
    score_text = escape(f"{score:.1f} / 10")
    blockers = escape(str(blockers_count))
    verdict_text = escape(verdict or "-")
    next_action_text = escape(next_action or "-")
    route_title_text = escape(route_title or "Route")
    score_title_text = escape(score_title or "Readiness")
    tone = _route_tone(route_label)
    st.markdown(
        """
        <style>
          .bt-route-panel {
            display: grid;
            grid-template-columns: minmax(240px, 0.95fr) minmax(280px, 1.25fr);
            gap: 0.85rem;
            align-items: stretch;
            margin: 0.45rem 0 0.85rem 0;
          }
          .bt-route-summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
            gap: 0.65rem;
          }
          .bt-route-card {
            padding: 0.85rem 0.95rem;
            border: 1px solid rgba(49, 51, 63, 0.18);
            border-radius: 8px;
            background: #ffffff;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
          }
          .bt-route-card-route { border-left: 4px solid #475569; }
          .bt-route-card-positive { border-left-color: #0f766e; }
          .bt-route-card-warning { border-left-color: #b45309; }
          .bt-route-card-danger { border-left-color: #b91c1c; }
          .bt-route-label {
            font-size: 0.84rem;
            font-weight: 650;
            color: #64748b;
            margin-bottom: 0.4rem;
          }
          .bt-route-value {
            font-size: 1.15rem;
            font-weight: 750;
            line-height: 1.25;
            color: #111827;
            overflow-wrap: anywhere;
            word-break: break-word;
          }
          .bt-route-verdict {
            padding: 0.95rem 1rem;
            border: 1px solid rgba(49, 51, 63, 0.18);
            border-radius: 8px;
            background: #f8fafc;
          }
          .bt-route-verdict-title {
            font-size: 0.84rem;
            font-weight: 650;
            color: #64748b;
            margin-bottom: 0.35rem;
          }
          .bt-route-verdict-main {
            font-size: 1.02rem;
            font-weight: 750;
            color: #111827;
            line-height: 1.35;
            overflow-wrap: anywhere;
          }
          .bt-route-next {
            margin-top: 0.8rem;
            font-size: 0.92rem;
            line-height: 1.45;
            color: #334155;
            overflow-wrap: anywhere;
          }
          @media (max-width: 760px) {
            .bt-route-panel { grid-template-columns: 1fr; }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="bt-route-panel">'
        f'<div class="bt-route-summary">'
        f'<div class="bt-route-card bt-route-card-route bt-route-card-{tone}">'
        f'<div class="bt-route-label">{route_title_text}</div><div class="bt-route-value">{route}</div></div>'
        f'<div class="bt-route-card"><div class="bt-route-label">{score_title_text}</div><div class="bt-route-value">{score_text}</div></div>'
        f'<div class="bt-route-card"><div class="bt-route-label">Blockers</div><div class="bt-route-value">{blockers}</div></div>'
        f"</div>"
        f'<div class="bt-route-verdict">'
        f'<div class="bt-route-verdict-title">판정</div><div class="bt-route-verdict-main">{verdict_text}</div>'
        f'<div class="bt-route-next"><strong>다음 행동</strong><br>{next_action_text}</div>'
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
