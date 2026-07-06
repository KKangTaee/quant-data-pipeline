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
    if tone_text in {"positive", "warning", "danger", "neutral"}:
        return tone_text
    return "neutral"


def render_pv_styles() -> None:
    st.markdown(
        """
        <style>
          :root {
            --pv-bg: #ffffff;
            --pv-ink: #111827;
            --pv-muted: #4b5563;
            --pv-subtle: #6b7280;
            --pv-panel: #ffffff;
            --pv-panel-2: #ffffff;
            --pv-panel-3: #f3f4f6;
            --pv-line: rgba(17, 24, 39, 0.12);
            --pv-line-strong: rgba(17, 24, 39, 0.18);
            --pv-text: #111827;
            --pv-text-muted: #4b5563;
            --pv-positive: #22c55e;
            --pv-warning: #f59e0b;
            --pv-danger: #ef4444;
            --pv-neutral: #6b7280;
            --pv-cyan: #0891b2;
          }
          .pv-shell,
          .pv-shell * {
            box-sizing: border-box;
          }
          .pv-shell {
            width: 100%;
            margin: 0 0 1rem 0;
            color: var(--pv-text);
          }
          .pv-command {
            display: grid;
            grid-template-columns: minmax(0, 1.45fr) minmax(260px, 0.75fr);
            gap: 0.9rem;
            align-items: stretch;
            padding: 1rem;
            border: 1px solid var(--pv-line-strong);
            border-radius: 0;
            background: var(--pv-panel);
            box-shadow: none;
          }
          .pv-command-main {
            display: grid;
            gap: 0.75rem;
            align-content: start;
          }
          .pv-command-eyebrow,
          .pv-section-eyebrow,
          .pv-card-kicker,
          .pv-step-kicker {
            font-size: 0.74rem;
            line-height: 1.2;
            font-weight: 780;
            letter-spacing: 0;
            color: var(--pv-text-muted);
            overflow-wrap: anywhere;
          }
          .pv-command-title {
            font-size: 1.46rem;
            line-height: 1.15;
            font-weight: 840;
            color: var(--pv-text);
            overflow-wrap: anywhere;
          }
          .pv-command-detail {
            max-width: 74rem;
            font-size: 0.92rem;
            line-height: 1.48;
            color: var(--pv-text-muted);
            overflow-wrap: anywhere;
          }
          .pv-command-side {
            display: grid;
            gap: 0.6rem;
            align-content: stretch;
          }
          .pv-route-card {
            min-height: 132px;
            display: grid;
            gap: 0.5rem;
            align-content: start;
            padding: 0.9rem;
            border: 1px solid var(--pv-line);
            border-left: 4px solid var(--pv-neutral);
            border-radius: 0;
            background: var(--pv-panel-2);
          }
          .pv-route-positive,
          .pv-card-positive,
          .pv-section-positive,
          .pv-step-positive {
            border-left-color: var(--pv-positive);
          }
          .pv-route-warning,
          .pv-card-warning,
          .pv-section-warning,
          .pv-step-warning {
            border-left-color: var(--pv-warning);
          }
          .pv-route-danger,
          .pv-card-danger,
          .pv-section-danger,
          .pv-step-danger {
            border-left-color: var(--pv-danger);
          }
          .pv-route-neutral,
          .pv-card-neutral,
          .pv-section-neutral,
          .pv-step-neutral {
            border-left-color: var(--pv-neutral);
          }
          .pv-route-label {
            font-size: 0.78rem;
            font-weight: 760;
            color: var(--pv-text-muted);
            overflow-wrap: anywhere;
          }
          .pv-route-value {
            font-size: 1.06rem;
            line-height: 1.22;
            font-weight: 840;
            color: var(--pv-text);
            overflow-wrap: anywhere;
          }
          .pv-route-detail {
            font-size: 0.82rem;
            line-height: 1.38;
            color: var(--pv-text-muted);
            overflow-wrap: anywhere;
          }
          .pv-kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(min(100%, 145px), 1fr));
            gap: 0.58rem;
          }
          .pv-kpi {
            min-height: 82px;
            padding: 0.72rem 0.76rem;
            border: 1px solid var(--pv-line);
            border-radius: 0;
            background: var(--pv-panel-2);
          }
          .pv-kpi-label {
            font-size: 0.72rem;
            font-weight: 720;
            color: var(--pv-text-muted);
            overflow-wrap: anywhere;
          }
          .pv-kpi-value {
            margin-top: 0.28rem;
            font-size: 1.02rem;
            line-height: 1.2;
            font-weight: 820;
            color: var(--pv-text);
            overflow-wrap: anywhere;
          }
          .pv-kpi-detail {
            margin-top: 0.28rem;
            font-size: 0.76rem;
            line-height: 1.28;
            color: var(--pv-text-muted);
            overflow-wrap: anywhere;
          }
          .pv-step-rail {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(min(100%, 170px), 1fr));
            gap: 0.6rem;
            margin: 0.2rem 0 1rem 0;
          }
          .pv-step {
            min-height: 94px;
            padding: 0.76rem 0.82rem;
            border: 1px solid var(--pv-line);
            border-left: 4px solid var(--pv-neutral);
            border-radius: 0;
            background: var(--pv-panel-2);
            color: var(--pv-text);
          }
          .pv-step-marker {
            display: inline-flex;
            min-width: 1.65rem;
            height: 1.65rem;
            align-items: center;
            justify-content: center;
            margin-bottom: 0.45rem;
            border-radius: 0;
            background: var(--pv-panel-3);
            color: var(--pv-text);
            font-size: 0.78rem;
            font-weight: 820;
          }
          .pv-step-title {
            font-size: 0.9rem;
            line-height: 1.25;
            font-weight: 820;
            color: var(--pv-text);
            overflow-wrap: anywhere;
          }
          .pv-step-detail {
            margin-top: 0.25rem;
            font-size: 0.78rem;
            line-height: 1.35;
            color: var(--pv-text-muted);
            overflow-wrap: anywhere;
          }
          .pv-section {
            margin: 1.15rem 0 0.65rem 0;
            padding: 0.85rem 0.95rem;
            border: 1px solid var(--pv-line);
            border-left: 4px solid var(--pv-neutral);
            border-radius: 0;
            background: var(--pv-panel-2);
            color: var(--pv-text);
          }
          .pv-section-title {
            font-size: 1.04rem;
            line-height: 1.25;
            font-weight: 840;
            color: var(--pv-text);
            overflow-wrap: anywhere;
          }
          .pv-section-detail {
            margin-top: 0.36rem;
            max-width: 78rem;
            font-size: 0.88rem;
            line-height: 1.45;
            color: var(--pv-text-muted);
            overflow-wrap: anywhere;
          }
          .pv-card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(min(100%, var(--pv-card-min, 220px)), 1fr));
            gap: 0.7rem;
            margin: 0.45rem 0 1rem 0;
          }
          .pv-card {
            min-height: 126px;
            padding: 0.86rem 0.92rem;
            border: 1px solid var(--pv-line);
            border-left: 4px solid var(--pv-neutral);
            border-radius: 0;
            background: var(--pv-panel-2);
            color: var(--pv-text);
          }
          .pv-card-title {
            font-size: 0.98rem;
            line-height: 1.25;
            font-weight: 840;
            color: var(--pv-text);
            overflow-wrap: anywhere;
          }
          .pv-card-status {
            display: inline-flex;
            width: fit-content;
            margin-top: 0.52rem;
            padding: 0.2rem 0.52rem;
            border: 1px solid rgba(17, 24, 39, 0.1);
            border-radius: 0;
            background: rgba(127, 142, 163, 0.2);
            color: var(--pv-text);
            font-size: 0.75rem;
            line-height: 1.2;
            font-weight: 780;
            overflow-wrap: anywhere;
          }
          .pv-card-positive .pv-card-status { background: rgba(34, 197, 94, 0.12); color: #166534; }
          .pv-card-warning .pv-card-status { background: rgba(245, 158, 11, 0.14); color: #92400e; }
          .pv-card-danger .pv-card-status { background: rgba(239, 68, 68, 0.12); color: #991b1b; }
          .pv-card-detail {
            margin-top: 0.56rem;
            font-size: 0.84rem;
            line-height: 1.42;
            color: var(--pv-text-muted);
            overflow-wrap: anywhere;
          }
          .pv-card-meta {
            margin-top: 0.48rem;
            font-size: 0.77rem;
            line-height: 1.34;
            color: var(--pv-text-muted);
            overflow-wrap: anywhere;
          }
          .pv-profile-summary-title {
            margin: 0.58rem 0 0.42rem 0;
            color: var(--pv-text);
            font-size: 0.9rem;
            font-weight: 820;
            line-height: 1.3;
            overflow-wrap: anywhere;
          }
          .pv-profile-summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(min(100%, var(--pv-profile-card-min, 150px)), 1fr));
            gap: 0.62rem;
            margin: 0.25rem 0 0.72rem 0;
          }
          .pv-profile-summary-card {
            min-height: 104px;
            padding: 0.72rem 0.78rem;
            border: 1px solid var(--pv-line);
            border-top: 4px solid var(--pv-neutral);
            border-radius: 0;
            background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
            color: var(--pv-text);
          }
          .pv-profile-summary-card-positive { border-top-color: #0f8f83; }
          .pv-profile-summary-card-warning { border-top-color: #b45309; }
          .pv-profile-summary-card-danger { border-top-color: #b42318; }
          .pv-profile-summary-card-neutral { border-top-color: var(--pv-neutral); }
          .pv-profile-summary-label {
            color: var(--pv-text-muted);
            font-size: 0.78rem;
            font-weight: 800;
            line-height: 1.22;
            overflow-wrap: anywhere;
          }
          .pv-profile-summary-value {
            margin-top: 0.28rem;
            color: var(--pv-text);
            font-size: 1.12rem;
            font-weight: 860;
            line-height: 1.18;
            overflow-wrap: anywhere;
          }
          .pv-profile-summary-detail {
            margin-top: 0.34rem;
            color: var(--pv-text-muted);
            font-size: 0.78rem;
            line-height: 1.34;
            overflow-wrap: anywhere;
          }
          .pv-criteria-board {
            margin: 0.35rem 0 1rem 0;
            padding: 1rem;
            border: 1px solid var(--pv-line-strong);
            border-left: 4px solid var(--pv-neutral);
            border-radius: 0;
            background: linear-gradient(90deg, rgba(107, 114, 128, 0.08), rgba(255, 255, 255, 0.96) 36%, #ffffff);
            color: var(--pv-text);
          }
          .pv-criteria-board-positive {
            border-left-color: #0f8f83;
            background: linear-gradient(90deg, rgba(15, 143, 131, 0.1), rgba(255, 255, 255, 0.96) 36%, #ffffff);
          }
          .pv-criteria-board-warning {
            border-left-color: #b45309;
            background: linear-gradient(90deg, rgba(180, 83, 9, 0.1), rgba(255, 255, 255, 0.96) 36%, #ffffff);
          }
          .pv-criteria-board-danger {
            border-left-color: #b42318;
            background: linear-gradient(90deg, rgba(180, 35, 24, 0.1), rgba(255, 255, 255, 0.96) 36%, #ffffff);
          }
          .pv-criteria-kicker {
            color: var(--pv-text-muted);
            font-size: 0.78rem;
            font-weight: 850;
            line-height: 1.35;
          }
          .pv-criteria-title {
            margin-top: 0.24rem;
            color: var(--pv-text);
            font-size: 1.28rem;
            font-weight: 860;
            line-height: 1.32;
            overflow-wrap: anywhere;
          }
          .pv-criteria-detail {
            margin-top: 0.42rem;
            color: var(--pv-text-muted);
            font-size: 0.92rem;
            line-height: 1.48;
            overflow-wrap: anywhere;
          }
          .pv-criteria-metrics {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            margin-top: 0.9rem;
            border-top: 1px solid rgba(148, 163, 184, 0.2);
            border-bottom: 1px solid rgba(148, 163, 184, 0.2);
          }
          .pv-criteria-metric {
            min-width: 0;
            padding: 0.68rem 0.78rem;
            border-left: 1px solid rgba(148, 163, 184, 0.18);
          }
          .pv-criteria-metric:first-child {
            border-left: 0;
            padding-left: 0;
          }
          .pv-criteria-metric span {
            display: block;
            color: var(--pv-text-muted);
            font-size: 0.76rem;
            font-weight: 820;
            line-height: 1.35;
          }
          .pv-criteria-metric strong {
            display: block;
            margin-top: 0.16rem;
            color: var(--pv-text);
            font-size: 1.34rem;
            line-height: 1.12;
            overflow-wrap: anywhere;
          }
          .pv-criteria-groups {
            display: grid;
            gap: 0.98rem;
            margin-top: 0.95rem;
          }
          .pv-criteria-group {
            padding-bottom: 0.92rem;
            border-bottom: 1px solid rgba(148, 163, 184, 0.18);
          }
          .pv-criteria-group:last-child {
            padding-bottom: 0;
            border-bottom: 0;
          }
          .pv-criteria-group-head {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 0.58rem;
          }
          .pv-criteria-group-head strong {
            display: block;
            color: var(--pv-text);
            font-size: 0.98rem;
            line-height: 1.35;
            overflow-wrap: anywhere;
          }
          .pv-criteria-group-head span {
            display: block;
            margin-top: 0.16rem;
            color: var(--pv-text-muted);
            font-size: 0.8rem;
            font-weight: 760;
            line-height: 1.4;
            overflow-wrap: anywhere;
          }
          .pv-criteria-group-head b {
            color: var(--pv-text-muted);
            flex: 0 0 auto;
            font-size: 0.82rem;
            line-height: 1.35;
          }
          .pv-criteria-status-grid {
            display: grid;
            grid-template-columns: minmax(140px, 0.7fr) minmax(180px, 1fr) minmax(180px, 1fr);
            gap: 0;
            border: 1px solid rgba(148, 163, 184, 0.2);
            background: rgba(255, 255, 255, 0.72);
          }
          .pv-criteria-status-cell {
            min-width: 0;
            padding: 0.65rem 0.72rem;
            border-left: 1px solid rgba(148, 163, 184, 0.18);
          }
          .pv-criteria-status-cell:first-child,
          .pv-criteria-status-cell-wide {
            border-left: 0;
          }
          .pv-criteria-status-cell-wide {
            grid-column: 1 / -1;
            border-top: 1px solid rgba(148, 163, 184, 0.18);
          }
          .pv-criteria-status-cell span {
            display: block;
            color: var(--pv-text-muted);
            font-size: 0.76rem;
            font-weight: 840;
            line-height: 1.35;
          }
          .pv-criteria-status-cell strong,
          .pv-criteria-status-cell p {
            display: block;
            margin: 0.2rem 0 0;
            color: var(--pv-text);
            font-size: 0.88rem;
            font-weight: 780;
            line-height: 1.42;
            overflow-wrap: anywhere;
          }
          .pv-criteria-status-cell p {
            color: var(--pv-muted);
            font-weight: 650;
          }
          .pv-criteria-technical-detail {
            margin-top: 0.62rem;
          }
          .pv-criteria-technical-detail summary {
            cursor: pointer;
            color: var(--pv-text-muted);
            font-size: 0.78rem;
            font-weight: 840;
            line-height: 1.35;
          }
          .pv-criteria-technical-detail .pv-criteria-cards {
            margin-top: 0.58rem;
          }
          .pv-criteria-cards {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.72rem;
          }
          .pv-criteria-card {
            min-width: 0;
            padding: 0.74rem 0.82rem;
            border: 1px solid rgba(148, 163, 184, 0.22);
            border-top: 3px solid rgba(107, 114, 128, 0.5);
            border-radius: 0;
            background: rgba(255, 255, 255, 0.76);
          }
          .pv-criteria-card-positive { border-top-color: #0f8f83; }
          .pv-criteria-card-warning { border-top-color: #b45309; }
          .pv-criteria-card-danger { border-top-color: #b42318; }
          .pv-criteria-card-head {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 0.7rem;
          }
          .pv-criteria-card h5 {
            margin: 0;
            color: var(--pv-text);
            font-size: 1rem;
            line-height: 1.34;
            overflow-wrap: anywhere;
          }
          .pv-criteria-card-status {
            color: var(--pv-text-muted);
            flex: 0 0 auto;
            font-size: 0.76rem;
            font-weight: 850;
            line-height: 1.35;
            white-space: nowrap;
          }
          .pv-criteria-card-positive .pv-criteria-card-status { color: #0f8f83; }
          .pv-criteria-card-warning .pv-criteria-card-status { color: #b45309; }
          .pv-criteria-card-danger .pv-criteria-card-status { color: #b42318; }
          .pv-criteria-row {
            margin-top: 0.58rem;
            padding-top: 0.52rem;
            border-top: 1px solid rgba(148, 163, 184, 0.16);
          }
          .pv-criteria-row span,
          .pv-criteria-card footer {
            color: var(--pv-text-muted);
            font-size: 0.76rem;
            font-weight: 820;
            line-height: 1.35;
          }
          .pv-criteria-row p,
          .pv-criteria-card p {
            margin: 0.2rem 0 0;
            color: var(--pv-muted);
            font-size: 0.86rem;
            line-height: 1.45;
            overflow-wrap: anywhere;
          }
          .pv-criteria-card footer {
            display: flex;
            justify-content: space-between;
            gap: 0.7rem;
            margin-top: 0.62rem;
            padding-top: 0.5rem;
            border-top: 1px solid rgba(148, 163, 184, 0.16);
          }
          .pv-alert-panel {
            margin: 0.35rem 0 1rem 0;
            padding: 0.96rem;
            border: 1px solid var(--pv-line-strong);
            border-left: 4px solid var(--pv-danger);
            border-radius: 0;
            background: var(--pv-panel);
            color: var(--pv-text);
          }
          .pv-alert-panel-positive { border-left-color: var(--pv-positive); }
          .pv-alert-panel-warning { border-left-color: var(--pv-warning); }
          .pv-alert-panel-neutral { border-left-color: var(--pv-neutral); }
          .pv-alert-title {
            font-size: 1rem;
            line-height: 1.25;
            font-weight: 840;
            color: var(--pv-text);
            overflow-wrap: anywhere;
          }
          .pv-alert-detail {
            margin-top: 0.36rem;
            font-size: 0.86rem;
            line-height: 1.45;
            color: var(--pv-text-muted);
            overflow-wrap: anywhere;
          }
          div[data-testid="stDataFrame"] {
            border: 1px solid rgba(17, 24, 39, 0.12);
            border-radius: 0;
            overflow: hidden;
          }
          div[data-testid="stExpander"] details {
            border-radius: 0;
          }
          @media (max-width: 760px) {
            .pv-command {
              grid-template-columns: 1fr;
              padding: 0.84rem;
            }
            .pv-route-card {
              min-height: auto;
            }
            .pv-criteria-metrics,
            .pv-criteria-status-grid,
            .pv-criteria-cards {
              grid-template-columns: 1fr;
            }
            .pv-criteria-status-cell,
            .pv-criteria-status-cell-wide {
              border-left: 0;
              border-top: 1px solid rgba(148, 163, 184, 0.18);
            }
            .pv-criteria-status-cell:first-child {
              border-top: 0;
            }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_pv_section_header(
    *,
    title: str,
    detail: str = "",
    eyebrow: str = "",
    tone: str = "neutral",
) -> None:
    render_pv_styles()
    tone_class = _safe_tone(tone)
    eyebrow_html = (
        f'<div class="pv-section-eyebrow">{escape(eyebrow)}</div>' if eyebrow else ""
    )
    detail_html = f'<div class="pv-section-detail">{escape(detail)}</div>' if detail else ""
    st.markdown(
        '<div class="pv-shell">'
        f'<div class="pv-section pv-section-{tone_class}">'
        f"{eyebrow_html}"
        f'<div class="pv-section-title">{escape(title)}</div>'
        f"{detail_html}"
        "</div></div>",
        unsafe_allow_html=True,
    )


def render_pv_card_grid(cards: list[dict[str, Any]], *, min_width: int = 220) -> None:
    render_pv_styles()
    html_cards: list[str] = []
    for card in cards:
        tone = _safe_tone(card.get("tone"))
        kicker = str(card.get("kicker") or "")
        title = str(card.get("title") or "")
        status = _display_value(card.get("status"))
        detail = str(card.get("detail") or "")
        meta = str(card.get("meta") or "")
        kicker_html = f'<div class="pv-card-kicker">{escape(kicker)}</div>' if kicker else ""
        status_html = f'<div class="pv-card-status">{escape(status)}</div>' if status else ""
        detail_html = f'<div class="pv-card-detail">{escape(detail)}</div>' if detail else ""
        meta_html = f'<div class="pv-card-meta">{escape(meta)}</div>' if meta else ""
        html_cards.append(
            f'<div class="pv-card pv-card-{tone}">'
            f"{kicker_html}"
            f'<div class="pv-card-title">{escape(title)}</div>'
            f"{status_html}"
            f"{detail_html}"
            f"{meta_html}"
            "</div>"
        )
    st.markdown(
        '<div class="pv-shell">'
        f'<div class="pv-card-grid" style="--pv-card-min: {int(min_width)}px;">'
        f'{"".join(html_cards)}'
        "</div></div>",
        unsafe_allow_html=True,
    )


def render_pv_profile_summary_strip(
    items: list[dict[str, Any]],
    *,
    title: str = "선택한 검증 기준",
    min_width: int = 150,
) -> None:
    render_pv_styles()
    html_items: list[str] = []
    for item in items:
        tone = _safe_tone(item.get("tone"))
        label = str(item.get("label") or "")
        value = _display_value(item.get("value"))
        detail = str(item.get("detail") or "")
        detail_html = (
            f'<div class="pv-profile-summary-detail">{escape(detail)}</div>'
            if detail
            else ""
        )
        html_items.append(
            f'<div class="pv-profile-summary-card pv-profile-summary-card-{tone}">'
            f'<div class="pv-profile-summary-label">{escape(label)}</div>'
            f'<div class="pv-profile-summary-value">{escape(value)}</div>'
            f"{detail_html}"
            "</div>"
        )
    title_html = (
        f'<div class="pv-profile-summary-title">{escape(title)}</div>' if title else ""
    )
    st.markdown(
        '<div class="pv-shell">'
        f"{title_html}"
        f'<div class="pv-profile-summary-grid" style="--pv-profile-card-min: {int(min_width)}px;">'
        f'{"".join(html_items)}'
        "</div></div>",
        unsafe_allow_html=True,
    )


def render_pv_step_rail(steps: list[dict[str, Any]]) -> None:
    render_pv_styles()
    html_steps: list[str] = []
    for index, step in enumerate(steps, start=1):
        tone = _safe_tone(step.get("tone"))
        marker = str(step.get("marker") or index)
        title = str(step.get("title") or "")
        detail = str(step.get("detail") or "")
        kicker = str(step.get("kicker") or "")
        kicker_html = f'<div class="pv-step-kicker">{escape(kicker)}</div>' if kicker else ""
        html_steps.append(
            f'<div class="pv-step pv-step-{tone}">'
            f'<div class="pv-step-marker">{escape(marker)}</div>'
            f"{kicker_html}"
            f'<div class="pv-step-title">{escape(title)}</div>'
            f'<div class="pv-step-detail">{escape(detail)}</div>'
            "</div>"
        )
    st.markdown(
        '<div class="pv-shell">'
        f'<div class="pv-step-rail">{"".join(html_steps)}</div>'
        "</div>",
        unsafe_allow_html=True,
    )


def render_pv_command_center(
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
    render_pv_styles()
    kpi_html: list[str] = []
    for item in kpis:
        label = str(item.get("label") or "")
        value = _display_value(item.get("value"))
        detail_text = str(item.get("detail") or "")
        detail_html = (
            f'<div class="pv-kpi-detail">{escape(detail_text)}</div>' if detail_text else ""
        )
        kpi_html.append(
            '<div class="pv-kpi">'
            f'<div class="pv-kpi-label">{escape(label)}</div>'
            f'<div class="pv-kpi-value">{escape(value)}</div>'
            f"{detail_html}"
            "</div>"
        )
    route_tone_class = _safe_tone(route_tone)
    st.markdown(
        '<div class="pv-shell">'
        '<div class="pv-command">'
        '<div class="pv-command-main">'
        f'<div class="pv-command-eyebrow">{escape(eyebrow)}</div>'
        f'<div class="pv-command-title">{escape(title)}</div>'
        f'<div class="pv-command-detail">{escape(detail)}</div>'
        f'<div class="pv-kpi-grid">{"".join(kpi_html)}</div>'
        "</div>"
        '<div class="pv-command-side">'
        f'<div class="pv-route-card pv-route-{route_tone_class}">'
        f'<div class="pv-route-label">{escape(route_label)}</div>'
        f'<div class="pv-route-value">{escape(route_value)}</div>'
        f'<div class="pv-route-detail">{escape(route_detail)}</div>'
        "</div>"
        "</div>"
        "</div></div>",
        unsafe_allow_html=True,
    )


def render_pv_alert_panel(
    *,
    title: str,
    detail: str,
    tone: str = "neutral",
) -> None:
    render_pv_styles()
    tone_class = _safe_tone(tone)
    st.markdown(
        '<div class="pv-shell">'
        f'<div class="pv-alert-panel pv-alert-panel-{tone_class}">'
        f'<div class="pv-alert-title">{escape(title)}</div>'
        f'<div class="pv-alert-detail">{escape(detail)}</div>'
        "</div></div>",
        unsafe_allow_html=True,
    )
