from __future__ import annotations

import json
from html import escape
from typing import Any

import streamlit as st
import streamlit.components.v1 as components


OVERVIEW_COLOR_POSITIVE = "#0f766e"
OVERVIEW_COLOR_PRIMARY = "#2563eb"
OVERVIEW_COLOR_WARNING = "#b45309"
OVERVIEW_COLOR_DANGER = "#dc2626"
OVERVIEW_COLOR_DANGER_DARK = "#b91c1c"
OVERVIEW_COLOR_NEUTRAL = "#64748b"
OVERVIEW_COLOR_TEXT = "#111827"
OVERVIEW_COLOR_TEXT_SUBTLE = "#475569"
OVERVIEW_COLOR_TEXT_MUTED = "#94a3b8"
OVERVIEW_COLOR_TEXT_INVERSE = "#ffffff"
OVERVIEW_COLOR_SURFACE = "#ffffff"
OVERVIEW_COLOR_SURFACE_SUBTLE = "#f8fafc"
OVERVIEW_COLOR_SURFACE_ALT = "#fcfcfd"
OVERVIEW_COLOR_BORDER = "#e5e7eb"
OVERVIEW_COLOR_PURPLE = "#7c3aed"
OVERVIEW_COLOR_CYAN = "#0891b2"
OVERVIEW_COLOR_LIME = "#65a30d"
OVERVIEW_COLOR_SOFT = "#cbd5e1"

OVERVIEW_DIVERGING_RANGE = [
    OVERVIEW_COLOR_DANGER_DARK,
    OVERVIEW_COLOR_SURFACE_SUBTLE,
    OVERVIEW_COLOR_POSITIVE,
]
OVERVIEW_SERIES_COLORS = [
    OVERVIEW_COLOR_POSITIVE,
    OVERVIEW_COLOR_PRIMARY,
    OVERVIEW_COLOR_WARNING,
    OVERVIEW_COLOR_PURPLE,
    OVERVIEW_COLOR_CYAN,
    OVERVIEW_COLOR_LIME,
    OVERVIEW_COLOR_NEUTRAL,
]
OVERVIEW_SECTOR_COLOR_MAP = {
    "Basic Materials": "#8b5cf6",
    "Communication Services": "#0891b2",
    "Consumer Cyclical": "#d97706",
    "Consumer Defensive": "#65a30d",
    "Energy": "#0f766e",
    "Financial Services": "#2563eb",
    "Healthcare": "#14b8a6",
    "Industrials": "#7c3aed",
    "Real Estate": "#64748b",
    "Technology": "#0284c7",
    "Utilities": "#16a34a",
    "Unknown": OVERVIEW_COLOR_NEUTRAL,
}

_CSS_TOKENS = {
    "color-positive": OVERVIEW_COLOR_POSITIVE,
    "color-primary": OVERVIEW_COLOR_PRIMARY,
    "color-warning": OVERVIEW_COLOR_WARNING,
    "color-danger": OVERVIEW_COLOR_DANGER,
    "color-neutral": OVERVIEW_COLOR_NEUTRAL,
    "color-text": OVERVIEW_COLOR_TEXT,
    "color-text-inverse": OVERVIEW_COLOR_TEXT_INVERSE,
    "color-surface": OVERVIEW_COLOR_SURFACE,
    "color-surface-subtle": OVERVIEW_COLOR_SURFACE_SUBTLE,
    "color-text-muted": "rgba(100, 116, 139, 0.95)",
    "color-text-soft": "rgba(100, 116, 139, 0.98)",
    "border-faint": "rgba(100, 116, 139, 0.14)",
    "border-subtle": "rgba(100, 116, 139, 0.18)",
    "border-control": "rgba(100, 116, 139, 0.24)",
    "fill-control": "rgba(148, 163, 184, 0.10)",
    "fill-subtle": "rgba(148, 163, 184, 0.08)",
    "track-fill": "rgba(100, 116, 139, 0.18)",
    "radius-panel": "8px",
    "radius-pill": "999px",
    "font-xs": "0.74rem",
    "font-caption": "0.75rem",
    "font-chip": "0.76rem",
    "font-label": "0.78rem",
    "font-body": "0.82rem",
    "font-title": "0.95rem",
    "font-value": "1rem",
    "weight-label": "720",
    "weight-strong": "750",
    "weight-heading": "760",
    "weight-value": "780",
    "gap-xs": "0.28rem",
    "gap-sm": "0.35rem",
    "gap-md": "0.55rem",
    "gap-lg": "0.75rem",
}


def _css_token_block() -> str:
    return "\n".join(f"  --ov-mi-{name}: {value};" for name, value in _CSS_TOKENS.items())


def _style_token_block() -> str:
    return f":root {{\n{_css_token_block()}\n}}\n"


def _display_value(value: Any) -> str:
    if value in (None, ""):
        return "-"
    return str(value)


def overview_ui_css() -> str:
    return (
        "<style>\n"
        + _style_token_block()
        + """
.ov-mm-toolbar-label {
  margin: 0.2rem 0 0.45rem 0;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-label);
  font-weight: var(--ov-mi-weight-label);
  letter-spacing: 0;
  text-transform: uppercase;
}
.ov-market-session {
  display: grid;
  grid-template-columns: minmax(16rem, 1.4fr) repeat(3, minmax(8rem, 1fr));
  gap: var(--ov-mi-gap-md);
  align-items: stretch;
  margin: 0.35rem 0 0.92rem 0;
  padding: 0.52rem;
  border: 1px solid var(--ov-mi-border-faint);
  border-left: 4px solid var(--ov-session-tone, var(--ov-mi-color-neutral));
  border-radius: var(--ov-mi-radius-panel);
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--ov-session-tone, var(--ov-mi-color-neutral)) 7%, transparent), rgba(255, 255, 255, 0.95)),
    var(--ov-mi-color-surface);
}
.ov-market-session-main {
  min-width: 0;
  padding: 0.18rem 0.35rem 0.18rem 0.2rem;
}
.ov-market-session-status {
  display: inline-flex;
  align-items: center;
  min-height: 1.38rem;
  padding: 0.14rem 0.46rem;
  border: 1px solid color-mix(in srgb, var(--ov-session-tone, var(--ov-mi-color-neutral)) 34%, transparent);
  border-radius: var(--ov-mi-radius-pill);
  background: color-mix(in srgb, var(--ov-session-tone, var(--ov-mi-color-neutral)) 9%, transparent);
  color: var(--ov-session-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.1;
}
.ov-market-session-title {
  color: inherit;
  font-size: var(--ov-mi-font-title);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.22;
  margin-top: 0.35rem;
  overflow-wrap: anywhere;
}
.ov-market-session-detail {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.25;
  margin-top: 0.15rem;
  overflow-wrap: anywhere;
}
.ov-market-session-item {
  min-width: 0;
  padding: 0.52rem 0.62rem;
  border-left: 1px solid var(--ov-mi-border-faint);
}
.ov-market-session-label {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
}
.ov-market-session-value {
  color: inherit;
  font-size: var(--ov-mi-font-value);
  font-weight: var(--ov-mi-weight-value);
  line-height: 1.2;
  margin-top: 0.13rem;
  overflow-wrap: anywhere;
}
.ov-market-session-item-detail {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.22;
  margin-top: 0.12rem;
  overflow-wrap: anywhere;
}
.ov-mm-refresh-label {
  margin: 0.85rem 0 0.42rem 0;
  color: inherit;
  font-size: var(--ov-mi-font-title);
  font-weight: var(--ov-mi-weight-heading);
}
.ov-mm-status-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--ov-mi-gap-lg);
  padding: 0.54rem 0 0.62rem 0;
  border-top: 1px solid var(--ov-mi-border-subtle);
  border-bottom: 1px solid var(--ov-mi-border-subtle);
  margin-bottom: var(--ov-mi-gap-md);
}
.ov-mm-state-cluster {
  display: flex;
  align-items: center;
  gap: var(--ov-mi-gap-md);
  min-width: 0;
  flex-wrap: wrap;
}
.ov-mm-state-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  min-height: 2rem;
  padding: 0.34rem 0.64rem;
  border-radius: var(--ov-mi-radius-pill);
  border: 1px solid var(--ov-mi-border-control);
  background: var(--ov-mi-fill-control);
}
.ov-mm-state-dot {
  width: 0.52rem;
  height: 0.52rem;
  border-radius: var(--ov-mi-radius-pill);
  background: var(--ov-mm-state-color, var(--ov-mi-color-neutral));
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--ov-mm-state-color, var(--ov-mi-color-neutral)) 18%, transparent);
}
.ov-mm-state-label {
  color: inherit;
  font-weight: var(--ov-mi-weight-strong);
  white-space: nowrap;
}
.ov-mm-state-detail {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-body);
}
.ov-mm-chip-row {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--ov-mi-gap-sm);
  flex-wrap: wrap;
}
.ov-mm-chip {
  display: inline-flex;
  align-items: center;
  gap: var(--ov-mi-gap-xs);
  min-height: 1.7rem;
  padding: 0.25rem 0.52rem;
  border-radius: var(--ov-mi-radius-pill);
  border: 1px solid var(--ov-mi-border-subtle);
  background: var(--ov-mi-fill-subtle);
  color: var(--ov-mi-color-text-soft);
  font-size: var(--ov-mi-font-chip);
  line-height: 1.2;
}
.ov-mm-chip strong {
  color: inherit;
  font-weight: var(--ov-mi-weight-strong);
}
.ov-mm-auto-static {
  border: 1px solid var(--ov-mi-border-control);
  border-radius: var(--ov-mi-radius-panel);
  padding: 0.65rem 0.75rem;
  margin: 0.35rem 0 0.45rem 0;
  background: var(--ov-mi-fill-subtle);
}
.ov-mm-auto-static-title {
  font-weight: var(--ov-mi-weight-strong);
  color: inherit;
}
.ov-mm-auto-static-detail,
.ov-mm-auto-static-due {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-body);
}
.ov-mm-auto-static-detail {
  margin-top: 0.15rem;
}
.ov-mm-auto-static-track {
  height: 6px;
  border-radius: var(--ov-mi-radius-pill);
  background: var(--ov-mi-track-fill);
  margin-top: var(--ov-mi-gap-md);
  overflow: hidden;
}
.ov-mm-auto-static-bar {
  height: 100%;
  background: var(--ov-mi-color-positive);
  border-radius: var(--ov-mi-radius-pill);
}
.ov-mm-auto-message {
  color: var(--ov-mi-color-text-soft);
  font-size: var(--ov-mi-font-body);
  line-height: 1.35;
  margin: 0.1rem 0 0.35rem 0;
}
.ov-mm-meta-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0;
  border-top: 1px solid var(--ov-mi-border-subtle);
  border-bottom: 1px solid var(--ov-mi-border-subtle);
  margin: 0.25rem 0 0.9rem 0;
}
.ov-mm-meta-item {
  min-width: 0;
  padding: 0.58rem 0.8rem;
  border-left: 1px solid var(--ov-mi-border-faint);
}
.ov-mm-meta-item:first-child {
  border-left: 0;
  padding-left: 0;
}
.ov-mm-meta-label {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  letter-spacing: 0;
}
.ov-mm-meta-value {
  color: inherit;
  font-size: var(--ov-mi-font-value);
  font-weight: var(--ov-mi-weight-value);
  line-height: 1.25;
  margin-top: 0.12rem;
  overflow-wrap: anywhere;
}
.ov-mm-meta-detail {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.28;
  margin-top: 0.1rem;
  overflow-wrap: anywhere;
}
.ov-events-summary {
  display: grid;
  grid-template-columns: minmax(14rem, 1.45fr) repeat(3, minmax(8rem, 1fr));
  gap: var(--ov-mi-gap-md);
  margin: 0.45rem 0 0.85rem 0;
}
.ov-events-summary-item {
  position: relative;
  min-width: 0;
  overflow: hidden;
  padding: 0.72rem 0.82rem 0.72rem 0.9rem;
  border: 1px solid var(--ov-mi-border-subtle);
  border-radius: var(--ov-mi-radius-panel);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(248, 250, 252, 0.72)),
    var(--ov-mi-color-surface-subtle);
}
.ov-events-summary-item::before {
  content: "";
  position: absolute;
  inset: 0 auto 0 0;
  width: 4px;
  background: var(--ov-event-tone, var(--ov-mi-color-neutral));
}
.ov-events-summary-primary {
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--ov-event-tone, var(--ov-mi-color-primary)) 10%, transparent), rgba(255, 255, 255, 0.92)),
    var(--ov-mi-color-surface-subtle);
}
.ov-events-summary-label-row {
  display: flex;
  align-items: center;
  gap: var(--ov-mi-gap-xs);
  min-width: 0;
}
.ov-events-summary-dot {
  width: 0.42rem;
  height: 0.42rem;
  border-radius: var(--ov-mi-radius-pill);
  background: var(--ov-event-tone, var(--ov-mi-color-neutral));
  flex: 0 0 auto;
}
.ov-events-summary-label {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  letter-spacing: 0;
}
.ov-events-summary-value {
  color: inherit;
  font-size: 1.08rem;
  font-weight: var(--ov-mi-weight-value);
  line-height: 1.2;
  margin-top: 0.16rem;
  overflow-wrap: anywhere;
}
.ov-events-summary-primary .ov-events-summary-value {
  font-size: 1.18rem;
}
.ov-events-summary-detail {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.25;
  margin-top: 0.14rem;
  overflow-wrap: anywhere;
}
.ov-events-source-lane {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--ov-mi-gap-sm);
  margin: 0.24rem 0 0.64rem 0;
  padding: 0.48rem;
  border: 1px solid var(--ov-mi-border-faint);
  border-radius: var(--ov-mi-radius-panel);
  background:
    linear-gradient(180deg, rgba(248, 250, 252, 0.84), rgba(255, 255, 255, 0.94)),
    var(--ov-mi-color-surface-subtle);
}
.ov-events-source {
  position: relative;
  min-width: 0;
  border: 1px solid var(--ov-mi-border-subtle);
  border-left: 4px solid var(--ov-event-tone, var(--ov-mi-color-neutral));
  border-radius: var(--ov-mi-radius-panel);
  background: var(--ov-mi-color-surface);
  padding: 0.54rem 0.6rem 0.5rem 0.66rem;
}
.ov-events-source-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--ov-mi-gap-sm);
  min-width: 0;
}
.ov-events-source-title {
  color: inherit;
  font-size: var(--ov-mi-font-body);
  font-weight: var(--ov-mi-weight-strong);
  white-space: nowrap;
}
.ov-events-source-state {
  flex: 0 0 auto;
  color: var(--ov-event-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
  white-space: nowrap;
  border: 1px solid color-mix(in srgb, var(--ov-event-tone, var(--ov-mi-color-neutral)) 36%, transparent);
  border-radius: var(--ov-mi-radius-pill);
  background: color-mix(in srgb, var(--ov-event-tone, var(--ov-mi-color-neutral)) 9%, transparent);
  padding: 0.12rem 0.42rem;
}
.ov-events-source-detail {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.28;
  margin-top: 0.2rem;
  overflow-wrap: anywhere;
}
.ov-events-source-body {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--ov-mi-gap-xs);
  margin-top: 0.42rem;
  padding-top: 0.42rem;
  border-top: 1px solid var(--ov-mi-border-faint);
}
.ov-events-source-field {
  min-width: 0;
}
.ov-events-source-field-label {
  color: var(--ov-mi-color-text-muted);
  font-size: 0.68rem;
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.1;
}
.ov-events-source-field-value {
  color: inherit;
  font-size: 0.76rem;
  font-weight: var(--ov-mi-weight-strong);
  line-height: 1.18;
  margin-top: 0.12rem;
  overflow-wrap: anywhere;
}
.ov-events-warning-stack {
  display: grid;
  gap: var(--ov-mi-gap-xs);
  margin: 0.24rem 0 0.72rem 0;
}
.ov-events-warning {
  display: flex;
  align-items: flex-start;
  gap: var(--ov-mi-gap-sm);
  padding: 0.44rem 0.62rem;
  border: 1px solid color-mix(in srgb, var(--ov-mi-color-warning) 24%, transparent);
  border-left: 3px solid var(--ov-mi-color-warning);
  border-radius: var(--ov-mi-radius-panel);
  background: color-mix(in srgb, var(--ov-mi-color-warning) 8%, var(--ov-mi-color-surface));
  color: #8a5a05;
  font-size: var(--ov-mi-font-body);
  line-height: 1.3;
}
.ov-events-warning-label {
  color: var(--ov-mi-color-warning);
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
  white-space: nowrap;
}
.ov-events-agenda {
  display: grid;
  gap: 0.85rem;
  margin-top: 0.35rem;
}
.ov-events-section {
  border-top: 1px solid var(--ov-mi-border-subtle);
  padding-top: 0.68rem;
}
.ov-events-section:first-child {
  border-top: 0;
  padding-top: 0;
}
.ov-events-section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--ov-mi-gap-md);
  margin-bottom: 0.48rem;
}
.ov-events-section-title {
  color: inherit;
  font-size: var(--ov-mi-font-title);
  font-weight: var(--ov-mi-weight-heading);
}
.ov-events-section-meta {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
}
.ov-events-row {
  display: grid;
  grid-template-columns: minmax(7rem, 0.8fr) minmax(0, 2.2fr) minmax(8rem, 1fr);
  gap: var(--ov-mi-gap-md);
  align-items: center;
  padding: 0.55rem 0;
  border-top: 1px solid var(--ov-mi-border-faint);
}
.ov-events-row:first-of-type {
  border-top: 0;
}
.ov-events-date {
  min-width: 0;
}
.ov-events-day {
  color: inherit;
  font-size: var(--ov-mi-font-body);
  font-weight: var(--ov-mi-weight-strong);
  line-height: 1.2;
}
.ov-events-countdown {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.2;
  margin-top: 0.12rem;
}
.ov-events-main {
  min-width: 0;
}
.ov-events-title {
  color: inherit;
  font-size: var(--ov-mi-font-body);
  font-weight: var(--ov-mi-weight-strong);
  line-height: 1.25;
  overflow-wrap: anywhere;
}
.ov-events-subtitle {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.25;
  margin-top: 0.15rem;
  overflow-wrap: anywhere;
}
.ov-events-badges {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--ov-mi-gap-xs);
  flex-wrap: wrap;
}
.ov-events-badge {
  display: inline-flex;
  align-items: center;
  min-height: 1.45rem;
  padding: 0.2rem 0.45rem;
  border-radius: var(--ov-mi-radius-pill);
  border: 1px solid color-mix(in srgb, var(--ov-event-tone, var(--ov-mi-color-neutral)) 34%, transparent);
  background: color-mix(in srgb, var(--ov-event-tone, var(--ov-mi-color-neutral)) 9%, transparent);
  color: var(--ov-event-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.1;
  white-space: nowrap;
}
.ov-events-empty {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-body);
  padding: 0.7rem 0;
}
@media (max-width: 760px) {
  .ov-mm-status-bar {
    align-items: flex-start;
    flex-direction: column;
  }
  .ov-mm-chip-row {
    justify-content: flex-start;
  }
  .ov-mm-meta-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .ov-market-session {
    grid-template-columns: 1fr;
  }
  .ov-market-session-item {
    border-left: 0;
    border-top: 1px solid var(--ov-mi-border-faint);
  }
  .ov-mm-meta-item:nth-child(odd) {
    border-left: 0;
    padding-left: 0;
  }
  .ov-events-summary,
  .ov-events-source-lane {
    grid-template-columns: 1fr;
  }
  .ov-events-row {
    grid-template-columns: 1fr;
    gap: var(--ov-mi-gap-sm);
  }
  .ov-events-badges {
    justify-content: flex-start;
  }
}
</style>
""".strip()
    )


def market_movers_ui_css() -> str:
    return overview_ui_css()


def render_overview_toolbar_label(label: str) -> None:
    st.markdown(
        f'{overview_ui_css()}<div class="ov-mm-toolbar-label">{escape(label)}</div>',
        unsafe_allow_html=True,
    )


def render_market_movers_toolbar_label(label: str) -> None:
    render_overview_toolbar_label(label)


def render_overview_meta_strip(items: list[dict[str, Any]]) -> None:
    item_html: list[str] = []
    for item in items:
        detail = item.get("detail")
        detail_html = (
            f'<div class="ov-mm-meta-detail">{escape(str(detail))}</div>'
            if detail not in (None, "")
            else ""
        )
        item_html.append(
            '<div class="ov-mm-meta-item">'
            f'<div class="ov-mm-meta-label">{escape(str(item.get("title") or "-"))}</div>'
            f'<div class="ov-mm-meta-value">{escape(_display_value(item.get("value")))}</div>'
            f"{detail_html}"
            "</div>"
        )
    st.markdown(
        overview_ui_css()
        + f"""
<div class="ov-mm-meta-strip">
          {"".join(item_html)}
        </div>""",
        unsafe_allow_html=True,
    )


def render_market_snapshot_meta_strip(items: list[dict[str, Any]]) -> None:
    render_overview_meta_strip(items)


def _overview_tone_color(tone: Any) -> str:
    normalized = str(tone or "").lower()
    if normalized in {"positive", "official", "macro"}:
        return OVERVIEW_COLOR_POSITIVE
    if normalized in {"primary", "fomc"}:
        return OVERVIEW_COLOR_PRIMARY
    if normalized in {"warning", "earnings", "estimate"}:
        return OVERVIEW_COLOR_WARNING
    if normalized in {"danger", "review", "failed"}:
        return OVERVIEW_COLOR_DANGER
    if normalized in {"purple"}:
        return OVERVIEW_COLOR_PURPLE
    if normalized in {"cyan"}:
        return OVERVIEW_COLOR_CYAN
    return OVERVIEW_COLOR_NEUTRAL


def _badge_html(label: Any, tone: Any = None) -> str:
    return (
        f'<span class="ov-events-badge" style="--ov-event-tone:{escape(_overview_tone_color(tone))};">'
        f"{escape(_display_value(label))}"
        "</span>"
    )


def render_market_session_banner(model: dict[str, Any]) -> None:
    tone_color = escape(_overview_tone_color(model.get("tone")))
    item_html: list[str] = []
    for item in list(model.get("items") or [])[:3]:
        detail = item.get("detail")
        detail_html = (
            f'<div class="ov-market-session-item-detail">{escape(str(detail))}</div>'
            if detail not in (None, "")
            else ""
        )
        item_html.append(
            '<div class="ov-market-session-item">'
            f'<div class="ov-market-session-label">{escape(str(item.get("label") or "-"))}</div>'
            f'<div class="ov-market-session-value">{escape(_display_value(item.get("value")))}</div>'
            f"{detail_html}"
            "</div>"
        )
    st.markdown(
        overview_ui_css()
        + f"""
<div class="ov-market-session" style="--ov-session-tone:{tone_color};">
  <div class="ov-market-session-main">
    <span class="ov-market-session-status">{escape(_display_value(model.get("status")))}</span>
    <div class="ov-market-session-title">{escape(_display_value(model.get("title")))}</div>
    <div class="ov-market-session-detail">{escape(_display_value(model.get("detail")))}</div>
  </div>
  {"".join(item_html)}
</div>""",
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


def _market_refresh_state_label(value: Any) -> str:
    text = str(value or "-").strip()
    mapping = {
        "Fresh": "최신",
        "Update needed": "갱신 필요",
        "Update due": "갱신 필요",
        "Stale": "오래됨",
        "Partial": "부분 누락",
        "Failed": "실패",
    }
    return mapping.get(text, text)


def _market_refresh_state_detail(value: Any) -> str:
    text = str(value or "").strip()
    mapping = {
        "No action needed yet.": "아직 조치가 필요하지 않습니다.",
        "Run Update Daily Snapshot.": "일중 스냅샷 갱신을 실행하면 최신 quote로 갱신됩니다.",
        "using EOD fallback": "일중 스냅샷 대신 EOD fallback을 사용 중입니다.",
    }
    return mapping.get(text, text)


def render_market_refresh_status_bar(
    *,
    universe_label: str,
    price_mode: Any,
    returnable: Any,
    universe_count: Any,
    returnable_pct: Any,
    next_check_text: str,
    state: dict[str, str | bool] | None,
) -> None:
    label = _market_refresh_state_label((state or {}).get("label") or "Unknown")
    detail = _market_refresh_state_detail((state or {}).get("detail") or "")
    dot_color = str((state or {}).get("dot_color") or OVERVIEW_COLOR_NEUTRAL)
    coverage_text = f"{returnable} / {universe_count}"
    if returnable_pct is not None:
        coverage_text += f" ({float(returnable_pct):.1f}%)"
    detail_html = f'<span class="ov-mm-state-detail">{escape(detail)}</span>' if detail else ""
    st.markdown(
        overview_ui_css()
        + f"""
<div class="ov-mm-refresh-label">데이터 갱신</div>
<div class="ov-mm-status-bar">
          <div class="ov-mm-state-cluster">
            <span class="ov-mm-state-pill" style="--ov-mm-state-color:{escape(dot_color)};">
              <span class="ov-mm-state-dot"></span>
              <span class="ov-mm-state-label">{escape(label)}</span>
              {detail_html}
            </span>
          </div>
          <div class="ov-mm-chip-row">
            <span class="ov-mm-chip">범위 <strong>{escape(universe_label)}</strong></span>
            <span class="ov-mm-chip">가격 <strong>{escape(str(price_mode or "-"))}</strong></span>
            <span class="ov-mm-chip">커버리지 <strong>{escape(coverage_text)}</strong></span>
            <span class="ov-mm-chip">다음 확인 <strong>{escape(next_check_text)}</strong></span>
          </div>
        </div>""",
        unsafe_allow_html=True,
    )


def render_market_auto_message(message: Any) -> None:
    if message in (None, ""):
        return
    st.markdown(
        f'<div class="ov-mm-auto-message">{escape(str(message))}</div>',
        unsafe_allow_html=True,
    )


def render_market_auto_waiting_panel(coverage_label: Any = "선택한 coverage") -> None:
    st.markdown(
        overview_ui_css()
        + f"""
<div class="ov-mm-auto-static">
          <div class="ov-mm-auto-static-title">자동 갱신 대기</div>
          <div class="ov-mm-auto-static-detail">자동 갱신을 켜면 현재 브라우저 세션에서 {escape(str(coverage_label))} 일중 스냅샷 갱신 조건을 확인합니다.</div>
        </div>""",
        unsafe_allow_html=True,
    )


def render_auto_refresh_timing_static(timing: dict[str, Any]) -> None:
    progress_pct = int(timing.get("progress_pct") or 0)
    st.markdown(
        overview_ui_css()
        + f"""
<div class="ov-mm-auto-static">
          <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;">
            <div>
              <div class="ov-mm-auto-static-title">{escape(str(timing["title"]))}</div>
              <div class="ov-mm-auto-static-detail">{escape(str(timing["detail"]))}</div>
            </div>
            <div class="ov-mm-auto-static-due">다음 가능 시각: {escape(str(timing["next_due_at"]))}</div>
          </div>
          <div class="ov-mm-auto-static-track">
            <div class="ov-mm-auto-static-bar" style="width:{progress_pct}%;"></div>
          </div>
        </div>""",
        unsafe_allow_html=True,
    )


def render_auto_refresh_countdown(
    timing: dict[str, Any],
    *,
    auto_reload: bool,
    key_suffix: str,
    default_cadence_seconds: int = 300,
) -> None:
    remaining = max(0, int(timing.get("remaining_seconds") or 0))
    cadence_seconds = max(1, int(timing.get("cadence_seconds") or default_cadence_seconds))
    title = str(timing.get("title") or "자동 갱신 대기")
    detail = str(timing.get("detail") or "")
    next_due_at = str(timing.get("next_due_at") or "-")
    progress_pct = max(0, min(100, int(timing.get("progress_pct") or 0)))
    component_id = f"overview-refresh-countdown-{abs(hash(key_suffix))}"
    style_tokens = _style_token_block()
    components.html(
        f"""
        <style>
          {style_tokens}
          html, body {{
            margin: 0;
            background: transparent;
            color-scheme: light dark;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          }}
          .ov-auto-countdown {{
            border: 1px solid var(--ov-mi-border-control);
            border-radius: var(--ov-mi-radius-panel);
            padding: 10px 12px;
            background: var(--ov-mi-fill-control);
          }}
          .ov-auto-countdown-title {{ font-weight: var(--ov-mi-weight-strong); color: var(--ov-mi-color-text); }}
          .ov-auto-countdown-detail {{ font-size: var(--ov-mi-font-body); color: var(--ov-mi-color-neutral); margin-top: 2px; }}
          .ov-auto-countdown-due {{ font-size: var(--ov-mi-font-caption); color: var(--ov-mi-color-text-soft); }}
          .ov-auto-countdown-track {{
            height: 6px;
            border-radius: var(--ov-mi-radius-pill);
            background: var(--ov-mi-track-fill);
            margin-top: 9px;
            overflow: hidden;
          }}
          .ov-auto-countdown-bar {{
            height: 100%;
            width: {progress_pct}%;
            background: var(--ov-mi-color-positive);
            border-radius: var(--ov-mi-radius-pill);
            transition: width 0.25s linear;
          }}
          @media (prefers-color-scheme: dark) {{
            .ov-auto-countdown {{
              border-color: rgba(148, 163, 184, 0.28);
              background: rgba(148, 163, 184, 0.08);
            }}
            .ov-auto-countdown-title {{ color: var(--ov-mi-color-surface-subtle); }}
            .ov-auto-countdown-detail, .ov-auto-countdown-due {{ color: {OVERVIEW_COLOR_SOFT}; }}
            .ov-auto-countdown-track {{ background: rgba(203, 213, 225, 0.16); }}
          }}
        </style>
        <div id="{component_id}" class="ov-auto-countdown">
          <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;">
            <div>
              <div data-countdown-title class="ov-auto-countdown-title">{escape(title)}</div>
              <div class="ov-auto-countdown-detail">{escape(detail)}</div>
            </div>
            <div class="ov-auto-countdown-due">다음 가능 시각: {escape(next_due_at)}</div>
          </div>
          <div class="ov-auto-countdown-track">
            <div data-countdown-bar class="ov-auto-countdown-bar"></div>
          </div>
        </div>
        <script>
        (() => {{
          const root = document.getElementById({json.dumps(component_id)});
          if (!root) return;
          const titleNode = root.querySelector("[data-countdown-title]");
          const barNode = root.querySelector("[data-countdown-bar]");
          const startedRemaining = {remaining};
          const cadenceSeconds = {cadence_seconds};
          const autoReload = {json.dumps(bool(auto_reload and remaining > 0))};
          const loadedAt = Date.now();
          let didReload = false;
          function formatRemaining(totalSeconds) {{
            const safe = Math.max(0, Math.floor(totalSeconds));
            const minutes = Math.floor(safe / 60);
            const seconds = safe % 60;
            if (minutes <= 0) return `${{seconds}}초`;
            if (seconds === 0) return `${{minutes}}분`;
            return `${{minutes}}분 ${{seconds}}초`;
          }}
          function tick() {{
            const elapsed = Math.floor((Date.now() - loadedAt) / 1000);
            const remainingNow = Math.max(0, startedRemaining - elapsed);
            const elapsedWithinCadence = Math.max(0, cadenceSeconds - remainingNow);
            const progress = Math.max(0, Math.min(100, Math.round((elapsedWithinCadence / cadenceSeconds) * 100)));
            titleNode.textContent = `다음 갱신까지 ${{formatRemaining(remainingNow)}}`;
            barNode.style.width = `${{progress}}%`;
            if (autoReload && remainingNow <= 0 && !didReload) {{
              didReload = true;
              setTimeout(() => {{
                try {{
                  window.parent.location.reload();
                }} catch (error) {{
                  window.location.reload();
                }}
              }}, 500);
            }}
          }}
          tick();
          window.setInterval(tick, 1000);
        }})();
        </script>
        """,
        height=86,
    )
