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
    "color-text-subtle": OVERVIEW_COLOR_TEXT_SUBTLE,
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
    "radius-card": "6px",
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


def _display_status_label(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in {"ok", "success", "actual", "fresh", "high"}:
        return "자료 정상"
    if normalized == "reference_limit":
        return "참고 제한"
    if normalized == "meta":
        return "관리 메타"
    if normalized in {"review", "due", "partial"}:
        return "자료 확인 필요"
    if normalized == "stale":
        return "자료 오래됨"
    if normalized in {"missing", "no_data", "not_run", "insufficient_data", "no_universe"}:
        return "자료 부족"
    if normalized in {"failed", "error"}:
        return "확인 실패"
    return str(value or "상태 미확인")


def _display_freshness_label(value: Any) -> str:
    text = str(value or "").strip()
    if not text or text == "-":
        return "기준일 없음"
    return text


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
  color: var(--ov-mi-color-text);
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
  color: var(--ov-mi-color-text);
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
.ov-macro-cockpit {
  margin: 0.5rem 0 0.95rem 0;
  padding: 0.78rem 0 0.82rem 0.78rem;
  border-top: 1px solid var(--ov-mi-border-faint);
  border-bottom: 1px solid var(--ov-mi-border-faint);
  border-left: 3px solid var(--ov-cockpit-tone, var(--ov-mi-color-neutral));
  border-radius: 0;
  background:
    linear-gradient(90deg, color-mix(in srgb, var(--ov-cockpit-tone, var(--ov-mi-color-neutral)) 5%, var(--ov-mi-color-surface)), rgba(255,255,255,0.98)),
    var(--ov-mi-color-surface);
}
.ov-macro-cockpit-head {
  display: grid;
  grid-template-columns: minmax(16rem, 1fr) auto;
  gap: var(--ov-mi-gap-md);
  align-items: start;
  margin-bottom: 0.64rem;
}
.ov-macro-cockpit-kicker {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.15;
  text-transform: uppercase;
}
.ov-macro-cockpit-narrative {
  max-width: 62rem;
}
.ov-macro-cockpit-title {
  margin-top: 0.22rem;
  color: var(--ov-mi-color-text);
  font-size: 1.08rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.22;
  overflow-wrap: anywhere;
}
.ov-macro-cockpit-detail {
  max-width: 58rem;
  margin-top: 0.28rem;
  color: var(--ov-mi-color-text-subtle);
  font-size: 0.84rem;
  line-height: 1.42;
  overflow-wrap: anywhere;
}
.ov-macro-cockpit-status {
  display: inline-flex;
  align-items: center;
  min-height: 1.46rem;
  padding: 0.18rem 0.52rem;
  border: 1px solid color-mix(in srgb, var(--ov-cockpit-tone, var(--ov-mi-color-neutral)) 36%, transparent);
  border-radius: var(--ov-mi-radius-pill);
  background: color-mix(in srgb, var(--ov-cockpit-tone, var(--ov-mi-color-neutral)) 9%, transparent);
  color: var(--ov-cockpit-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.1;
  white-space: nowrap;
}
.ov-macro-cockpit-rail {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0;
  margin: 0.12rem 0 0.68rem 0;
  border-top: 1px solid var(--ov-mi-border-subtle);
  border-bottom: 1px solid var(--ov-mi-border-subtle);
  background: color-mix(in srgb, var(--ov-cockpit-tone, var(--ov-mi-color-neutral)) 4%, var(--ov-mi-color-surface));
}
.ov-macro-hybrid-tape {
  grid-template-columns: repeat(5, minmax(0, 1fr));
  margin-bottom: 0.74rem;
}
.ov-macro-tape-cell {
  min-width: 0;
  padding: 0.52rem 0.62rem;
  border-left: 1px solid var(--ov-mi-border-faint);
}
.ov-macro-tape-cell:first-child {
  border-left: 0;
}
.ov-macro-tape-label {
  color: var(--ov-tape-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.1;
  overflow-wrap: anywhere;
}
.ov-macro-tape-value {
  margin-top: 0.16rem;
  color: var(--ov-mi-color-text);
  font-size: 0.94rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.17;
  overflow-wrap: anywhere;
}
.ov-macro-tape-detail {
  margin-top: 0.12rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.2;
  overflow-wrap: anywhere;
}
.ov-macro-status-item {
  display: grid;
  grid-template-columns: minmax(7rem, 0.52fr) minmax(10rem, 0.86fr) minmax(0, 1.35fr);
  gap: var(--ov-mi-gap-md);
  align-items: baseline;
  min-width: 0;
  padding: 0.48rem 0.3rem 0.48rem 0;
  border-top: 1px solid var(--ov-mi-border-faint);
}
.ov-macro-status-item:first-child {
  border-top: 0;
}
.ov-macro-status-label {
  color: var(--ov-rail-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.1;
}
.ov-macro-status-value {
  color: var(--ov-mi-color-text);
  font-size: 0.94rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.18;
  overflow-wrap: anywhere;
}
.ov-macro-status-detail {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.22;
  overflow-wrap: anywhere;
}
.ov-macro-visual-board {
  min-width: 0;
  margin-top: 0.7rem;
}
.ov-macro-brief,
.ov-macro-cues {
  min-width: 0;
}
.ov-macro-visual-board {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(18rem, 0.8fr);
  gap: var(--ov-mi-gap-lg);
  padding: 0.64rem 0 0.68rem 0;
  border-top: 1px solid var(--ov-mi-border-faint);
  border-bottom: 1px solid var(--ov-mi-border-faint);
}
.ov-sector-pressure,
.ov-event-timeline-panel {
  min-width: 0;
}
.ov-sector-pressure-map {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  grid-auto-rows: minmax(3.8rem, auto);
  gap: 0.28rem;
}
.ov-sector-pressure-tile {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  min-width: 0;
  min-height: 3.8rem;
  padding: 0.48rem 0.52rem;
  border: 1px solid color-mix(in srgb, var(--ov-pressure-tone, var(--ov-mi-color-neutral)) 24%, transparent);
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--ov-pressure-tone, var(--ov-mi-color-neutral)) 17%, var(--ov-mi-color-surface)), color-mix(in srgb, var(--ov-pressure-tone, var(--ov-mi-color-neutral)) 7%, var(--ov-mi-color-surface)));
}
.ov-sector-pressure-name {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-body);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.14;
  overflow-wrap: anywhere;
}
.ov-sector-pressure-value {
  margin-top: 0.14rem;
  color: var(--ov-pressure-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.14;
}
.ov-sector-pressure-detail {
  margin-top: 0.12rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.18;
  overflow-wrap: anywhere;
}
.ov-event-timeline {
  display: grid;
  gap: 0;
  border-top: 1px solid var(--ov-mi-border-faint);
  border-bottom: 1px solid var(--ov-mi-border-faint);
}
.ov-event-timeline-row {
  display: grid;
  grid-template-columns: 3.4rem minmax(0, 1fr) auto;
  gap: var(--ov-mi-gap-sm);
  align-items: baseline;
  min-width: 0;
  padding: 0.48rem 0;
  border-top: 1px solid var(--ov-mi-border-faint);
}
.ov-event-timeline-row:first-child {
  border-top: 0;
}
.ov-event-timeline-day {
  color: var(--ov-event-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.15;
}
.ov-event-timeline-title {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-body);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.16;
  overflow-wrap: anywhere;
}
.ov-event-timeline-detail {
  margin-top: 0.12rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.2;
  overflow-wrap: anywhere;
}
.ov-event-timeline-status {
  color: var(--ov-event-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.12;
  text-align: right;
  white-space: nowrap;
}
.ov-macro-section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--ov-mi-gap-md);
  margin: 0 0 0.62rem 0;
}
.ov-macro-section-title {
  color: var(--ov-mi-color-text);
  font-size: 1.05rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.2;
}
.ov-macro-section-note {
  color: var(--ov-mi-color-text-muted);
  font-size: 0.84rem;
  line-height: 1.34;
  text-align: right;
  overflow-wrap: anywhere;
}
.ov-macro-reading-flow {
  display: grid;
  gap: 1.18rem;
  margin: 1rem 0 1.18rem 0;
}
.ov-macro-reading-section {
  min-width: 0;
  padding: 1.08rem 0 0.96rem 0;
  border-top: 1px solid var(--ov-mi-border-faint);
  background: transparent;
}
.ov-macro-reading-section .ov-macro-section-head {
  align-items: flex-start;
  margin-bottom: 0.66rem;
}
.ov-macro-reading-section .ov-macro-section-title {
  font-size: 1.08rem;
  line-height: 1.2;
}
.ov-macro-reading-section .ov-macro-section-note {
  max-width: 42rem;
  font-size: 0.86rem;
  line-height: 1.38;
  text-align: left;
}
.ov-macro-reading-section .ov-macro-brief-row {
  grid-template-columns: 2.45rem minmax(0, 1fr);
  padding: 0.58rem 0.18rem 0.6rem 0;
}
.ov-macro-reading-section .ov-macro-brief-step {
  width: 1.74rem;
  height: 1.74rem;
  font-size: 0.8rem;
}
.ov-macro-reading-section .ov-macro-brief-label {
  font-size: var(--ov-mi-font-label);
}
.ov-macro-reading-section .ov-macro-brief-value {
  margin-top: 0.16rem;
  font-size: 1.04rem;
}
.ov-macro-reading-section .ov-macro-brief-detail {
  max-width: 58rem;
  font-size: 0.84rem;
  line-height: 1.36;
}
.ov-macro-reading-section .ov-macro-cue-row {
  padding: 0.68rem 0;
}
.ov-macro-reading-section .ov-macro-cue-value {
  font-size: 1rem;
  line-height: 1.22;
}
.ov-macro-reading-section .ov-macro-cue-detail {
  font-size: 0.86rem;
  line-height: 1.36;
}
.ov-macro-reading-section .ov-macro-cue-action {
  margin-top: 0.22rem;
  font-size: 0.84rem;
  line-height: 1.34;
}
.ov-macro-reading-section .ov-source-confidence-title,
.ov-macro-reading-section .ov-historical-analog-title {
  font-size: 1.08rem;
  line-height: 1.2;
}
.ov-macro-reading-section .ov-source-confidence-detail,
.ov-macro-reading-section .ov-historical-analog-detail {
  line-height: 1.32;
}
.ov-historical-analog-row.is-muted-reference {
  background: transparent;
}
.ov-historical-analog-row.is-muted-reference .ov-historical-analog-title,
.ov-historical-analog-row.is-muted-reference .ov-historical-analog-detail,
.ov-historical-analog-row.is-muted-reference .ov-historical-analog-note,
.ov-historical-analog-row.is-muted-reference .ov-historical-analog-limitations {
  color: var(--ov-mi-color-text-muted);
}
.ov-source-confidence.is-evidence-footer {
  background: transparent;
}
.ov-market-brief-lane {
  min-width: 0;
  margin-top: 0.92rem;
  padding-top: 0.76rem;
  border-top: 1px solid var(--ov-mi-border-faint);
}
.ov-market-brief-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: var(--ov-mi-gap-md);
  margin-bottom: 0.46rem;
}
.ov-market-brief-title {
  color: var(--ov-mi-color-text);
  font-size: 1.02rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.2;
}
.ov-market-brief-note {
  max-width: 38rem;
  color: var(--ov-mi-color-text-muted);
  font-size: 0.84rem;
  line-height: 1.34;
  text-align: right;
  overflow-wrap: anywhere;
}
.ov-market-brief-list {
  display: grid;
  gap: 0;
  margin: 0;
  padding: 0;
  list-style: none;
  border-top: 1px solid var(--ov-mi-border-faint);
}
.ov-market-brief-row {
  display: grid;
  grid-template-columns: minmax(2.4rem, 0.12fr) minmax(8rem, 0.35fr) minmax(0, 1fr);
  gap: 0.78rem;
  align-items: start;
  min-width: 0;
  padding: 0.72rem 0;
  border-bottom: 1px solid var(--ov-mi-border-faint);
}
.ov-market-brief-step {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.72rem;
  height: 1.72rem;
  border-radius: var(--ov-mi-radius-pill);
  background: color-mix(in srgb, var(--ov-row-tone, var(--ov-mi-color-neutral)) 10%, transparent);
  color: var(--ov-row-tone, var(--ov-mi-color-neutral));
  font-size: 0.82rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1;
}
.ov-market-brief-label {
  color: var(--ov-mi-color-text-muted);
  font-size: 0.84rem;
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.22;
  overflow-wrap: anywhere;
}
.ov-market-brief-value {
  margin-top: 0.1rem;
  color: var(--ov-mi-color-text);
  font-size: 1.02rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.2;
  overflow-wrap: anywhere;
}
.ov-market-brief-detail {
  color: var(--ov-mi-color-text-subtle);
  font-size: 0.9rem;
  line-height: 1.42;
  overflow-wrap: anywhere;
}
.ov-macro-brief-list {
  display: grid;
  gap: var(--ov-mi-gap-sm);
  margin: 0;
  padding: 0;
  list-style: none;
}
.ov-macro-brief-row {
  display: grid;
  grid-template-columns: 2.1rem minmax(0, 1fr);
  gap: var(--ov-mi-gap-sm);
  min-width: 0;
  padding: 0.54rem 0.18rem 0.54rem 0;
  border-top: 1px solid var(--ov-mi-border-faint);
  background: transparent;
}
.ov-macro-brief-row:first-child {
  border-top: 0;
}
.ov-macro-brief-step {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.55rem;
  height: 1.55rem;
  border-radius: var(--ov-mi-radius-pill);
  background: color-mix(in srgb, var(--ov-row-tone, var(--ov-mi-color-neutral)) 10%, transparent);
  color: var(--ov-row-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1;
}
.ov-macro-brief-main {
  min-width: 0;
}
.ov-macro-brief-label,
.ov-macro-cue-label {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.14;
  overflow-wrap: anywhere;
}
.ov-macro-brief-value {
  margin-top: 0.14rem;
  color: var(--ov-mi-color-text);
  font-size: 0.98rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.18;
  overflow-wrap: anywhere;
}
.ov-macro-brief-detail,
.ov-macro-cue-detail,
.ov-macro-cue-action,
.ov-macro-cockpit-row-meta {
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.25;
  overflow-wrap: anywhere;
}
.ov-macro-brief-detail {
  margin-top: 0.22rem;
}
.ov-macro-cues-list {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 0;
  margin: 0;
  padding: 0;
  list-style: none;
  border-top: 1px solid var(--ov-mi-border-faint);
}
.ov-macro-cue-row {
  display: grid;
  grid-template-columns: minmax(4rem, 0.18fr) minmax(0, 0.95fr) minmax(0, 1.2fr) minmax(12rem, 0.8fr);
  gap: 0.86rem;
  align-items: start;
  min-width: 0;
  padding: 0.7rem 0;
  border-bottom: 1px solid var(--ov-mi-border-faint);
  background: transparent;
}
.ov-macro-cue-head {
  display: block;
  min-width: 0;
}
.ov-macro-cue-status {
  color: var(--ov-cue-tone, var(--ov-mi-color-neutral));
  font-size: 0.84rem;
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.2;
  overflow-wrap: anywhere;
}
.ov-macro-cue-value {
  color: var(--ov-mi-color-text);
  font-size: 1rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.22;
  overflow-wrap: anywhere;
}
.ov-macro-cue-detail {
  font-size: 0.86rem;
  line-height: 1.36;
}
.ov-macro-cue-action {
  color: color-mix(in srgb, var(--ov-cue-tone, var(--ov-mi-color-neutral)) 78%, var(--ov-mi-color-text));
  font-weight: var(--ov-mi-weight-label);
}
.ov-context-finding-rail {
  display: grid;
  gap: 0;
  margin: 0;
  padding: 0;
  list-style: none;
  border-top: 1px solid var(--ov-mi-border-faint);
}
.ov-context-finding-row {
  display: grid;
  grid-template-columns: minmax(5rem, 0.22fr) minmax(0, 1.1fr) minmax(0, 1.15fr) minmax(12rem, 0.8fr);
  gap: 0.86rem;
  align-items: start;
  min-width: 0;
  padding: 0.72rem 0;
  border-bottom: 1px solid var(--ov-mi-border-faint);
  background: transparent;
}
.ov-context-finding-priority {
  color: var(--ov-check-tone, var(--ov-mi-color-neutral));
  font-size: 0.9rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.2;
}
.ov-context-finding-label {
  margin-top: 0.18rem;
  color: var(--ov-mi-color-text-muted);
  font-size: 0.78rem;
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.2;
  overflow-wrap: anywhere;
}
.ov-context-finding-kicker {
  color: var(--ov-mi-color-text-muted);
  font-size: 0.76rem;
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.18;
}
.ov-context-finding-conclusion {
  margin-top: 0.12rem;
  color: var(--ov-mi-color-text);
  font-size: 1rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.22;
  overflow-wrap: anywhere;
}
.ov-context-finding-detail,
.ov-context-finding-evidence,
.ov-context-finding-meta {
  color: var(--ov-mi-color-text-subtle);
  font-size: 0.86rem;
  line-height: 1.36;
  overflow-wrap: anywhere;
}
.ov-context-finding-evidence {
  color: color-mix(in srgb, var(--ov-check-tone, var(--ov-mi-color-neutral)) 78%, var(--ov-mi-color-text));
  font-weight: var(--ov-mi-weight-label);
}
.ov-context-finding-meta {
  margin-top: 0.2rem;
  color: var(--ov-mi-color-text-muted);
  font-size: 0.78rem;
}
.ov-macro-cockpit-row-meta {
  display: flex;
  gap: var(--ov-mi-gap-xs);
  flex-wrap: wrap;
  margin-top: 0.26rem;
  font-size: var(--ov-mi-font-xs);
}
.ov-macro-cockpit-badges {
  display: flex;
  flex-wrap: wrap;
  gap: var(--ov-mi-gap-xs);
  margin-top: 0.42rem;
}
.ov-macro-cockpit-badge {
  display: inline-flex;
  align-items: center;
  max-width: 100%;
  min-height: 1.3rem;
  padding: 0.14rem 0.4rem;
  border: 1px solid color-mix(in srgb, var(--ov-badge-tone, var(--ov-mi-color-neutral)) 26%, transparent);
  border-radius: var(--ov-mi-radius-pill);
  background: color-mix(in srgb, var(--ov-badge-tone, var(--ov-mi-color-neutral)) 8%, transparent);
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.08;
  overflow-wrap: anywhere;
}
.ov-macro-cockpit-boundary {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.28;
  overflow-wrap: anywhere;
}
.ov-source-confidence {
  margin-top: 0;
  padding-top: 0;
  border-top: 0;
}
.ov-context-disclosure {
  min-width: 0;
}
.ov-context-disclosure > summary {
  cursor: pointer;
  list-style: none;
}
.ov-context-disclosure > summary::-webkit-details-marker {
  display: none;
}
.ov-context-disclosure > summary::after {
  content: "+";
  float: right;
  width: 1.35rem;
  height: 1.35rem;
  border: 1px solid var(--ov-mi-border-control);
  border-radius: var(--ov-mi-radius-pill);
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-body);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.18rem;
  text-align: center;
}
.ov-context-disclosure[open] > summary::after {
  content: "-";
}
.ov-context-disclosure-body {
  margin-top: 0.5rem;
}
.ov-source-confidence-summary,
.ov-ia-closeout-summary {
  display: block;
  min-width: 0;
}
.ov-source-confidence-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--ov-mi-gap-md);
  margin-bottom: 0.44rem;
}
.ov-source-confidence-title {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.18;
}
.ov-source-confidence-detail {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.24;
  overflow-wrap: anywhere;
}
.ov-source-confidence-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 0.32rem;
  margin-top: 0.36rem;
  min-width: 0;
}
.ov-source-status-board {
  display: block;
  margin-top: 0.46rem;
  padding-top: 0.44rem;
  border-top: 1px solid var(--ov-mi-border-faint);
}
.ov-source-status-board-title {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.15;
}
.ov-source-status-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.42rem;
  margin-top: 0.36rem;
}
.ov-source-status-metric {
  min-width: 0;
  padding: 0.34rem 0.46rem;
  border-top: 2px solid var(--ov-source-strip-tone, var(--ov-mi-color-neutral));
  background: color-mix(in srgb, var(--ov-source-strip-tone, var(--ov-mi-color-neutral)) 5%, rgba(255,255,255,0.92));
}
.ov-source-status-label {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.15;
  overflow-wrap: anywhere;
}
.ov-source-status-value {
  display: block;
  margin-top: 0.14rem;
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-title);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.08;
}
.ov-source-status-legacy {
  display: block;
  height: 0;
  overflow: hidden;
}
.ov-source-confidence-scan {
  display: flex;
  flex-wrap: wrap;
  gap: 0.28rem;
  margin-top: 0.36rem;
}
.ov-source-confidence-pill,
.ov-source-confidence-source {
  display: inline-flex;
  align-items: center;
  min-height: 1.45rem;
  padding: 0.16rem 0.5rem;
  border: 1px solid color-mix(in srgb, var(--ov-source-strip-tone, var(--ov-mi-color-neutral)) 22%, var(--ov-mi-border-faint));
  border-radius: var(--ov-mi-radius-pill);
  background: color-mix(in srgb, var(--ov-source-strip-tone, var(--ov-mi-color-neutral)) 6%, rgba(255,255,255,0.94));
  color: color-mix(in srgb, var(--ov-source-strip-tone, var(--ov-mi-color-neutral)) 78%, var(--ov-mi-color-text));
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.12;
  white-space: nowrap;
}
.ov-source-confidence-source {
  background: rgba(255,255,255,0.72);
  color: var(--ov-mi-color-text-subtle);
  font-weight: var(--ov-mi-weight-body);
  max-width: min(100%, 34rem);
  white-space: normal;
}
.ov-source-confidence-status {
  flex: 0 0 auto;
  color: var(--ov-source-status-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.1;
  white-space: nowrap;
}
.ov-source-confidence-list {
  display: grid;
  gap: 0;
  border-top: 1px solid var(--ov-mi-border-faint);
  border-bottom: 1px solid var(--ov-mi-border-faint);
}
.ov-source-ledger {
  min-width: 0;
}
.ov-source-ledger-head {
  display: grid;
  grid-template-columns: minmax(7.5rem, 0.55fr) minmax(10rem, 0.8fr) minmax(0, 1fr) minmax(10rem, 0.85fr);
  gap: var(--ov-mi-gap-md);
  padding: 0.34rem 0.18rem;
  border-top: 1px solid var(--ov-mi-border-subtle);
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.14;
}
.ov-source-action-strip {
  margin-top: 0.44rem;
  padding-top: 0.36rem;
  border-top: 1px solid var(--ov-mi-border-faint);
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.3;
  overflow-wrap: anywhere;
}
.ov-refresh-status-panel {
  margin: 0.35rem 0 0.58rem;
  padding: 0.54rem 0.62rem;
  border: 1px solid var(--ov-mi-border-faint);
  border-left: 3px solid var(--ov-refresh-status-tone, var(--ov-mi-color-neutral));
  border-radius: var(--ov-mi-radius-card);
  background: rgba(255,255,255,0.92);
}
.ov-refresh-status-head {
  display: flex;
  justify-content: space-between;
  gap: var(--ov-mi-gap-md);
  align-items: baseline;
}
.ov-refresh-status-title {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-body);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.18;
}
.ov-refresh-status-badge {
  flex: 0 0 auto;
  color: var(--ov-refresh-status-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.12;
}
.ov-refresh-status-detail {
  margin-top: 0.2rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.26;
  overflow-wrap: anywhere;
}
.ov-refresh-status-list {
  display: grid;
  gap: 0.34rem;
  margin-top: 0.48rem;
}
.ov-refresh-status-row {
  display: grid;
  grid-template-columns: minmax(8rem, 0.55fr) minmax(0, 1fr) minmax(10rem, 0.8fr);
  gap: var(--ov-mi-gap-md);
  padding-top: 0.36rem;
  border-top: 1px solid var(--ov-mi-border-faint);
}
.ov-refresh-status-source {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.16;
  overflow-wrap: anywhere;
}
.ov-refresh-status-copy,
.ov-refresh-status-meta {
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.28;
  overflow-wrap: anywhere;
}
.ov-refresh-status-pill {
  display: inline-flex;
  align-items: center;
  min-height: 1.35rem;
  padding: 0.14rem 0.44rem;
  border: 1px solid color-mix(in srgb, var(--ov-refresh-status-tone, var(--ov-mi-color-neutral)) 20%, var(--ov-mi-border-faint));
  border-radius: var(--ov-mi-radius-pill);
  color: color-mix(in srgb, var(--ov-refresh-status-tone, var(--ov-mi-color-neutral)) 78%, var(--ov-mi-color-text));
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.1;
}
.ov-refresh-status-muted {
  margin-top: 0.45rem;
  padding-top: 0.34rem;
  border-top: 1px solid var(--ov-mi-border-faint);
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.28;
  overflow-wrap: anywhere;
}
.ov-historical-analog-row {
  margin-top: 0;
  padding-top: 0;
  border-top: 0;
}
.ov-historical-analog-head {
  display: flex;
  justify-content: space-between;
  gap: var(--ov-mi-gap-md);
  align-items: flex-start;
}
.ov-historical-analog-title {
  color: var(--ov-mi-color-text);
  font-size: 1.08rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.18;
}
.ov-historical-analog-detail,
.ov-historical-analog-meta,
.ov-historical-analog-scope,
.ov-historical-analog-limitations,
.ov-historical-analog-note {
  color: var(--ov-mi-color-text-muted);
  font-size: 0.86rem;
  line-height: 1.36;
  overflow-wrap: anywhere;
}
.ov-historical-analog-status {
  flex: 0 0 auto;
  color: var(--ov-analog-tone, var(--ov-mi-color-neutral));
  font-size: 0.86rem;
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.12;
  white-space: nowrap;
}
.ov-historical-analog-meta {
  display: block;
  margin-top: 0.34rem;
}
.ov-historical-analog-scope {
  margin-top: 0.5rem;
  padding-top: 0.42rem;
  border-top: 1px solid var(--ov-mi-border-faint);
}
.ov-analog-basis-bar {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 0;
  margin-top: 0.72rem;
  border-top: 1px solid var(--ov-mi-border-subtle);
  border-bottom: 1px solid var(--ov-mi-border-subtle);
}
.ov-analog-basis-summary {
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr) minmax(0, 1.15fr) minmax(0, 0.9fr);
}
.ov-analog-basis-cell {
  min-width: 0;
  padding: 0.68rem 0.74rem;
  border-left: 1px solid var(--ov-mi-border-faint);
}
.ov-analog-basis-cell:first-child {
  border-left: 0;
}
.ov-analog-basis-cell span {
  display: block;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.14;
}
.ov-analog-basis-cell strong {
  display: block;
  margin-top: 0.16rem;
  color: var(--ov-mi-color-text);
  font-size: 0.92rem;
  line-height: 1.2;
  overflow-wrap: anywhere;
}
.ov-analog-basis-cell small {
  display: block;
  margin-top: 0.12rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.18;
  overflow-wrap: anywhere;
}
.ov-analog-technical-details {
  margin-top: 0.42rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.28;
}
.ov-analog-technical-details summary {
  cursor: pointer;
  color: var(--ov-mi-color-text-subtle);
  font-weight: var(--ov-mi-weight-label);
}
.ov-analog-technical-details div {
  margin-top: 0.18rem;
  overflow-wrap: anywhere;
}
.ov-analog-basis-warning {
  margin-top: 0.62rem;
  padding: 0.58rem 0.66rem;
  border-left: 3px solid var(--ov-analog-tone, var(--ov-mi-color-neutral));
  background: color-mix(in srgb, var(--ov-analog-tone, var(--ov-mi-color-neutral)) 7%, transparent);
  color: var(--ov-mi-color-text-subtle);
  font-size: 0.88rem;
  line-height: 1.38;
  overflow-wrap: anywhere;
}
.ov-analog-basis-warning strong {
  display: block;
  color: var(--ov-analog-tone, var(--ov-mi-color-neutral));
  font-size: 0.92rem;
}
.ov-analog-basis-warning span,
.ov-analog-basis-warning p {
  display: block;
  margin: 0.18rem 0 0;
}
.ov-analog-basis-ledger {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0;
  margin-top: 0.68rem;
  border-top: 1px solid var(--ov-mi-border-subtle);
  border-bottom: 1px solid var(--ov-mi-border-subtle);
  background: transparent;
}
.ov-analog-basis-group {
  min-width: 0;
  padding: 0.68rem 0.72rem;
  border-left: 1px solid var(--ov-mi-border-faint);
}
.ov-analog-basis-group:first-child {
  border-left: 0;
}
.ov-analog-basis-title {
  color: var(--ov-analog-tone, var(--ov-mi-color-neutral));
  font-size: 0.82rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.16;
}
.ov-analog-basis-list {
  display: grid;
  gap: 0.24rem;
  margin-top: 0.36rem;
}
.ov-analog-basis-item {
  display: grid;
  grid-template-columns: minmax(4.9rem, 0.48fr) minmax(0, 1fr);
  gap: 0.34rem;
  align-items: baseline;
  min-width: 0;
}
.ov-analog-basis-label {
  color: var(--ov-mi-color-text-muted);
  font-size: 0.78rem;
  line-height: 1.18;
}
.ov-analog-basis-value {
  color: var(--ov-mi-color-text-subtle);
  font-size: 0.8rem;
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.2;
  overflow-wrap: anywhere;
}
.ov-historical-analog-table {
  width: 100%;
  border-collapse: collapse;
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-caption);
}
.ov-historical-analog-table th,
.ov-historical-analog-table td {
  padding: 0.24rem 0.32rem;
  border-bottom: 1px solid var(--ov-mi-border-faint);
  text-align: right;
  vertical-align: top;
}
.ov-historical-analog-table th:first-child,
.ov-historical-analog-table td:first-child {
  text-align: left;
}
.ov-historical-analog-note {
  margin-top: 0.44rem;
  padding-top: 0.34rem;
  border-top: 1px solid var(--ov-mi-border-faint);
}
.ov-analog-explain {
  max-width: 58rem;
  margin-top: 0.68rem;
  color: var(--ov-mi-color-text-subtle);
  font-size: 0.92rem;
  line-height: 1.48;
  overflow-wrap: anywhere;
}
.ov-analog-method-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(0, 1.4fr) minmax(0, 1fr);
  gap: 0;
  margin-top: 0.74rem;
  border-top: 1px solid var(--ov-mi-border-subtle);
  border-bottom: 1px solid var(--ov-mi-border-subtle);
}
.ov-analog-method-step {
  min-width: 0;
  padding: 0.74rem 0.78rem;
  border-left: 1px solid var(--ov-mi-border-faint);
}
.ov-analog-method-step:first-child {
  border-left: 0;
}
.ov-analog-method-kicker {
  color: var(--ov-analog-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.14;
}
.ov-analog-method-title {
  margin-top: 0.14rem;
  color: var(--ov-mi-color-text);
  font-size: 0.94rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.2;
}
.ov-analog-method-detail {
  margin-top: 0.18rem;
  color: var(--ov-mi-color-text-muted);
  font-size: 0.86rem;
  line-height: 1.38;
  overflow-wrap: anywhere;
}
.ov-analog-method-line {
  display: grid;
  gap: 0.16rem;
  margin-top: 0.74rem;
  padding: 0.62rem 0.72rem;
  border-top: 1px solid var(--ov-mi-border-subtle);
  border-bottom: 1px solid var(--ov-mi-border-subtle);
  color: var(--ov-mi-color-text-subtle);
  font-size: 0.9rem;
  line-height: 1.42;
  overflow-wrap: anywhere;
}
.ov-analog-method-line strong {
  color: var(--ov-analog-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-xs);
  line-height: 1.14;
}
.ov-analog-method-line small {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.2;
}
.ov-analog-summary-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin-top: 0.72rem;
  border-top: 1px solid var(--ov-mi-border-subtle);
  border-bottom: 1px solid var(--ov-mi-border-subtle);
  background: transparent;
}
.ov-analog-summary-item {
  min-width: 0;
  padding: 0.68rem 0.72rem;
  border-left: 1px solid var(--ov-mi-border-faint);
}
.ov-analog-summary-item:first-child {
  border-left: 0;
}
.ov-analog-summary-label {
  color: var(--ov-mi-color-text-muted);
  font-size: 0.8rem;
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.12;
  overflow-wrap: anywhere;
}
.ov-analog-summary-value {
  margin-top: 0.14rem;
  color: var(--ov-mi-color-text);
  font-size: 1.05rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.18;
  overflow-wrap: anywhere;
}
.ov-analog-summary-detail {
  margin-top: 0.12rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.18;
  overflow-wrap: anywhere;
}
.ov-analog-interpretation {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr);
  gap: 0;
  margin-top: 0.68rem;
  border-top: 1px solid var(--ov-mi-border-subtle);
  border-bottom: 1px solid var(--ov-mi-border-subtle);
  padding-top: 0;
  color: var(--ov-mi-color-text-subtle);
  font-size: 0.92rem;
  line-height: 1.48;
  overflow-wrap: anywhere;
}
.ov-analog-insight {
  min-width: 0;
  padding: 0.66rem 0.76rem;
  border-left: 1px solid var(--ov-mi-border-faint);
}
.ov-analog-insight:first-child {
  border-left: 0;
}
.ov-analog-insight-label {
  color: var(--ov-analog-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.14;
}
.ov-analog-insight-copy {
  margin-top: 0.16rem;
  color: var(--ov-mi-color-text-subtle);
  font-size: 0.9rem;
  line-height: 1.42;
}
.ov-analog-outcome-matrix {
  margin-top: 0.74rem;
  border-top: 1px solid var(--ov-mi-border-subtle);
  border-bottom: 1px solid var(--ov-mi-border-subtle);
}
.ov-analog-outcome-head {
  display: flex;
  justify-content: space-between;
  gap: var(--ov-mi-gap-sm);
  align-items: baseline;
  padding: 0.58rem 0.72rem 0.46rem;
  border-bottom: 1px solid var(--ov-mi-border-faint);
}
.ov-analog-outcome-title {
  color: var(--ov-mi-color-text);
  font-size: 0.94rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.16;
}
.ov-analog-outcome-note {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.18;
  text-align: right;
}
.ov-analog-matrix-grid {
  display: grid;
  min-width: 0;
}
.ov-analog-matrix-header,
.ov-analog-matrix-row {
  display: grid;
  grid-template-columns: minmax(5.4rem, 0.55fr) repeat(var(--ov-analog-horizon-count, 3), minmax(0, 1fr));
  min-width: 0;
}
.ov-analog-matrix-header {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
}
.ov-analog-matrix-heading,
.ov-analog-matrix-asset,
.ov-analog-matrix-cell {
  border-left: 1px solid var(--ov-mi-border-faint);
  border-bottom: 1px solid var(--ov-mi-border-faint);
}
.ov-analog-matrix-heading:first-child,
.ov-analog-matrix-asset:first-child {
  border-left: 0;
}
.ov-analog-matrix-heading {
  padding: 0.34rem 0.58rem;
  text-align: right;
}
.ov-analog-matrix-asset {
  padding: 0.62rem 0.66rem;
  color: var(--ov-mi-color-text);
  font-size: 0.9rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.18;
}
.ov-analog-matrix-cell {
  min-width: 0;
  padding: 0.52rem 0.58rem;
  text-align: right;
  background: transparent;
}
.ov-analog-matrix-cell.has-return-gradient {
  background:
    linear-gradient(
      90deg,
      color-mix(in srgb, var(--ov-analog-cell-tone, var(--ov-mi-color-neutral)) calc(var(--ov-analog-cell-strength, 5%) + 7%), rgba(255,255,255,0.96)),
      color-mix(in srgb, var(--ov-analog-cell-tone, var(--ov-mi-color-neutral)) calc(var(--ov-analog-cell-strength, 5%) * 0.42 + 3%), rgba(255,255,255,0.99))
    );
}
.ov-analog-matrix-cell.has-return-gradient.is-positive {
  --ov-analog-cell-tone: var(--ov-mi-color-positive);
}
.ov-analog-matrix-cell.has-return-gradient.is-negative {
  --ov-analog-cell-tone: var(--ov-mi-color-danger);
}
.ov-analog-matrix-cell-label {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.12;
}
.ov-analog-matrix-cell strong {
  display: block;
  margin-top: 0.12rem;
  color: var(--ov-mi-color-text);
  font-size: 0.98rem;
  line-height: 1.16;
}
.ov-analog-matrix-cell span,
.ov-analog-matrix-cell small {
  display: block;
  margin-top: 0.08rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.14;
}
.ov-analog-support-summary {
  margin-top: 0.7rem;
  border-top: 1px solid var(--ov-mi-border-subtle);
  border-bottom: 1px solid var(--ov-mi-border-subtle);
}
.ov-analog-support-head {
  padding: 0.58rem 0.72rem 0.42rem;
  border-bottom: 1px solid var(--ov-mi-border-faint);
}
.ov-analog-support-title {
  color: var(--ov-mi-color-text);
  font-size: 0.92rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.16;
}
.ov-analog-support-note {
  margin-top: 0.12rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.22;
}
.ov-analog-support-list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0;
}
.ov-analog-support-item {
  min-width: 0;
  padding: 0.58rem 0.68rem;
  border-left: 1px solid var(--ov-mi-border-faint);
}
.ov-analog-support-item:first-child {
  border-left: 0;
}
.ov-analog-support-label {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.12;
}
.ov-analog-support-value {
  margin-top: 0.12rem;
  color: var(--ov-mi-color-text);
  font-size: 0.94rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.16;
}
.ov-analog-support-detail {
  margin-top: 0.1rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.18;
}
.ov-analog-detail-tables {
  margin-top: 0.66rem;
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-caption);
}
.ov-analog-detail-tables summary {
  cursor: pointer;
  padding: 0.48rem 0;
  border-top: 1px solid var(--ov-mi-border-faint);
  color: var(--ov-mi-color-text);
  font-weight: var(--ov-mi-weight-heading);
}
.ov-analog-condition {
  display: flex;
  flex-wrap: wrap;
  gap: 0.22rem 0.48rem;
  align-items: baseline;
  margin-top: 0.34rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.24;
  overflow-wrap: anywhere;
}
.ov-analog-matrix-legend {
  margin-top: 0.36rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.18;
  text-align: right;
}
.ov-analog-condition span {
  color: var(--ov-analog-tone, var(--ov-mi-color-neutral));
  font-weight: var(--ov-mi-weight-label);
}
.ov-historical-analog-table-block {
  margin-top: 0.58rem;
  min-width: 0;
  overflow-x: auto;
}
.ov-historical-analog-table-block.is-secondary {
  margin-top: 0.48rem;
}
.ov-historical-analog-table-title {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.18;
}
.ov-historical-analog-table-note {
  margin-top: 0.12rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.2;
  overflow-wrap: anywhere;
}
.ov-historical-analog-table-block .ov-historical-analog-table {
  margin-top: 0.34rem;
}
.ov-analog-gap-panel {
  display: grid;
  gap: var(--ov-mi-gap-sm);
  margin-top: 0.56rem;
  padding: 0.62rem 0.7rem;
  border: 1px solid color-mix(in srgb, var(--ov-analog-tone, var(--ov-mi-color-neutral)) 24%, transparent);
  border-left: 3px solid var(--ov-analog-tone, var(--ov-mi-color-neutral));
  background:
    linear-gradient(90deg, color-mix(in srgb, var(--ov-analog-tone, var(--ov-mi-color-neutral)) 7%, var(--ov-mi-color-surface)), rgba(255,255,255,0.99)),
    var(--ov-mi-color-surface);
}
.ov-analog-gap-title {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-body);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.18;
}
.ov-analog-gap-detail,
.ov-analog-gap-action {
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.28;
}
.ov-analog-gap-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--ov-mi-gap-xs);
  margin-top: 0.04rem;
}
.ov-analog-gap-item {
  min-width: 0;
  padding: 0.44rem 0.5rem;
  border: 1px solid var(--ov-mi-border-faint);
  background: rgba(255,255,255,0.58);
}
.ov-analog-gap-symbol {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.14;
}
.ov-analog-gap-rows {
  margin-top: 0.1rem;
  color: var(--ov-analog-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
}
.ov-analog-gap-meta {
  margin-top: 0.1rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.18;
  overflow-wrap: anywhere;
}
.ov-historical-analog-limitations {
  margin-top: 0.4rem;
}
.ov-macro-compare-section {
  margin-top: 1.2rem;
  padding: 1rem 0 0.1rem 0;
  border-top: 1px solid color-mix(in srgb, var(--ov-macro-pilot-tone, var(--ov-mi-color-neutral)) 24%, transparent);
  background: transparent;
}
.ov-macro-conditioned-head {
  display: flex;
  justify-content: space-between;
  gap: 0.7rem;
  align-items: flex-start;
}
.ov-macro-conditioned-title {
  font-size: 1.05rem;
  font-weight: var(--ov-mi-weight-heading);
  color: var(--ov-mi-color-text);
}
.ov-macro-conditioned-status {
  color: var(--ov-macro-pilot-tone, var(--ov-mi-color-neutral));
  font-size: 0.84rem;
  font-weight: var(--ov-mi-weight-label);
  white-space: nowrap;
}
.ov-macro-conditioned-detail,
.ov-macro-conditioned-reason,
.ov-macro-conditioned-quality {
  margin-top: 0.42rem;
  color: var(--ov-mi-color-text-muted);
  font-size: 0.88rem;
  line-height: 1.45;
}
.ov-macro-delta-matrix,
.ov-macro-backdrop-grid {
  display: grid;
  gap: 0.5rem;
  margin-top: 0.7rem;
}
.ov-macro-basis-bar {
  margin-top: 0.62rem;
  grid-template-columns: repeat(auto-fit, minmax(13rem, 1fr));
}
.ov-macro-basis-cell .ov-macro-basis-meaning {
  color: var(--ov-mi-color-text);
  font-size: 0.8rem;
  line-height: 1.24;
}
.ov-macro-basis-cell .ov-macro-basis-count-detail {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
}
.ov-macro-flow-item,
.ov-macro-delta-row,
.ov-macro-backdrop-item {
  min-width: 0;
  padding: 0.62rem 0.66rem;
  border-top: 1px solid var(--ov-mi-border-faint);
  background: transparent;
}
.ov-macro-flow-label,
.ov-macro-delta-label,
.ov-macro-backdrop-label {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.16;
}
.ov-macro-flow-value,
.ov-macro-delta-value,
.ov-macro-backdrop-value {
  margin-top: 0.14rem;
  color: var(--ov-mi-color-text);
  font-size: 1rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.18;
}
.ov-macro-flow-detail,
.ov-macro-delta-detail,
.ov-macro-backdrop-detail {
  margin-top: 0.12rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.22;
  overflow-wrap: anywhere;
}
.ov-macro-conditioned-summary,
.ov-macro-backdrop-description,
.ov-macro-backdrop-meaning {
  margin-top: 0.16rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.24;
}
.ov-macro-backdrop-meaning {
  color: var(--ov-mi-color-text);
  font-weight: var(--ov-mi-weight-label);
}
.ov-macro-delta-matrix .ov-analog-outcome-note {
  max-width: 34rem;
}
.ov-macro-backdrop {
  margin-top: 0.82rem;
}
.ov-macro-backdrop-head {
  display: flex;
  justify-content: space-between;
  gap: 0.7rem;
  align-items: baseline;
}
.ov-macro-backdrop-title {
  color: var(--ov-mi-color-text);
  font-size: 0.96rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.2;
}
.ov-macro-backdrop-note {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.2;
}
.ov-macro-backdrop-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.ov-macro-backdrop-top {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  align-items: center;
}
.ov-macro-backdrop-state {
  flex: 0 0 auto;
  padding: 0.08rem 0.34rem;
  border: 1px solid color-mix(in srgb, var(--ov-macro-pilot-tone, var(--ov-mi-color-neutral)) 24%, var(--ov-mi-border-faint));
  border-radius: 999px;
  color: var(--ov-macro-pilot-tone, var(--ov-mi-color-neutral));
  font-size: 0.72rem;
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.16;
  white-space: nowrap;
}
.ov-macro-backdrop-item .ov-macro-backdrop-value {
  margin-top: 0.34rem;
  font-size: 1.12rem;
}
.ov-macro-backdrop-ratio {
  margin-top: 0.32rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.18;
}
.ov-macro-backdrop-track {
  height: 0.3rem;
  margin-top: 0.18rem;
  overflow: hidden;
  border-radius: 999px;
  background: var(--ov-mi-bg-subtle);
}
.ov-macro-backdrop-fill {
  height: 100%;
  border-radius: inherit;
  background: color-mix(in srgb, var(--ov-macro-pilot-tone, var(--ov-mi-color-neutral)) 44%, transparent);
}
.ov-macro-conditioned-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.5rem;
  margin-top: 0.72rem;
}
.ov-macro-funnel-track,
.ov-macro-compare-lanes {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.5rem;
  margin-top: 0.62rem;
}
.ov-macro-compare-lanes {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.ov-macro-funnel-item,
.ov-macro-compare-lane {
  min-width: 0;
  padding: 0.62rem 0.66rem;
  border-top: 1px solid var(--ov-mi-border-faint);
  background: transparent;
}
.ov-macro-funnel-label,
.ov-macro-compare-label {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.16;
}
.ov-macro-funnel-value,
.ov-macro-compare-value {
  margin-top: 0.14rem;
  color: var(--ov-mi-color-text);
  font-size: 1rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.18;
}
.ov-macro-funnel-detail,
.ov-macro-compare-detail {
  margin-top: 0.12rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.22;
  overflow-wrap: anywhere;
}
.ov-macro-condition-summary {
  margin-top: 0.64rem;
  padding-top: 0.46rem;
  border-top: 1px solid var(--ov-mi-border-faint);
}
.ov-macro-condition-summary-title {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.14;
}
.ov-macro-condition-chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.38rem;
  margin-top: 0.34rem;
}
.ov-macro-condition-chip {
  max-width: 18rem;
  padding: 0.36rem 0.48rem;
  border: 1px solid color-mix(in srgb, var(--ov-macro-pilot-tone, var(--ov-mi-color-neutral)) 24%, transparent);
  border-radius: var(--ov-mi-radius-card);
  background: color-mix(in srgb, var(--ov-macro-pilot-tone, var(--ov-mi-color-neutral)) 5%, transparent);
}
.ov-macro-condition-chip strong,
.ov-macro-condition-chip span {
  display: block;
  overflow-wrap: anywhere;
}
.ov-macro-condition-chip strong {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.14;
}
.ov-macro-condition-chip span {
  margin-top: 0.1rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.16;
}
.ov-macro-conditioned-details {
  margin-top: 0.72rem;
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-caption);
}
.ov-macro-conditioned-details summary {
  cursor: pointer;
  padding: 0.44rem 0;
  border-top: 1px solid var(--ov-mi-border-faint);
  color: var(--ov-mi-color-text);
  font-weight: var(--ov-mi-weight-heading);
}
.ov-macro-conditioned-stat {
  padding: 0.5rem 0.56rem;
  border-top: 1px solid var(--ov-mi-border-faint);
  background: transparent;
}
.ov-macro-conditioned-stat-label {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
}
.ov-macro-conditioned-stat-value {
  margin-top: 0.16rem;
  color: var(--ov-mi-color-text);
  font-size: 0.9rem;
  font-weight: var(--ov-mi-weight-heading);
}
.ov-macro-conditioned-condition-group {
  margin-top: 0.72rem;
}
.ov-macro-dimension-audit {
  margin-top: 0.78rem;
  padding-top: 0.64rem;
  border-top: 1px solid var(--ov-mi-border-faint);
}
.ov-macro-dimension-head {
  display: flex;
  justify-content: space-between;
  gap: 0.7rem;
  align-items: flex-start;
}
.ov-macro-dimension-title {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-heading);
}
.ov-macro-dimension-summary {
  margin-top: 0.16rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.38;
}
.ov-macro-dimension-status {
  color: var(--ov-macro-pilot-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  white-space: nowrap;
}
.ov-macro-dimension-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.48rem;
  margin-top: 0.56rem;
}
.ov-macro-dimension-groups {
  display: grid;
  gap: 0.58rem;
  margin-top: 0.62rem;
}
.ov-macro-dimension-group {
  min-width: 0;
  padding-top: 0.48rem;
  border-top: 1px solid var(--ov-mi-border-faint);
}
.ov-macro-dimension-group:first-child {
  border-top: 0;
  padding-top: 0;
}
.ov-macro-dimension-group-title {
  color: var(--ov-macro-pilot-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.14;
}
.ov-macro-dimension-group-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.48rem;
  margin-top: 0.4rem;
}
.ov-macro-dimension-item {
  min-width: 0;
  padding: 0.48rem 0;
  border-top: 1px solid var(--ov-mi-border-faint);
  background: transparent;
}
.ov-macro-dimension-top {
  display: flex;
  justify-content: space-between;
  gap: 0.45rem;
  align-items: flex-start;
}
.ov-macro-dimension-label {
  min-width: 0;
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.25;
  overflow-wrap: anywhere;
}
.ov-macro-dimension-pill {
  flex: 0 0 auto;
  color: var(--ov-macro-pilot-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
}
.ov-macro-dimension-meta {
  margin-top: 0.18rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.36;
  overflow-wrap: anywhere;
}
.ov-macro-conditioned-condition-title {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-heading);
}
.ov-macro-conditioned-condition-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.48rem;
  margin-top: 0.42rem;
}
.ov-macro-conditioned-condition {
  padding: 0.48rem 0;
  border-top: 1px solid var(--ov-mi-border-faint);
  background: transparent;
}
.ov-macro-conditioned-condition strong {
  display: block;
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-caption);
}
.ov-macro-conditioned-condition span {
  display: inline-block;
  margin-top: 0.2rem;
  color: var(--ov-macro-pilot-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
}
.ov-macro-conditioned-condition p {
  margin: 0.18rem 0 0;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.4;
}
.ov-macro-conditioned-empty {
  margin-top: 0.7rem;
  padding: 0.54rem 0.6rem;
  border-radius: 7px;
  background: rgba(241,245,249,0.82);
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
}
.ov-source-confidence-body {
  padding-top: 0.12rem;
}
.ov-source-confidence-group {
  margin-top: 0.62rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--ov-mi-border);
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.1;
}
.ov-source-confidence-group:first-child {
  margin-top: 0;
  padding-top: 0;
  border-top: 0;
}
.ov-source-confidence-group span {
  margin-left: 0.35rem;
  color: var(--ov-mi-color-text-subtle);
  font-weight: var(--ov-mi-weight-body);
}
.ov-source-confidence-row {
  display: grid;
  grid-template-columns: minmax(7.5rem, 0.55fr) minmax(10rem, 0.8fr) minmax(0, 1fr) minmax(10rem, 0.85fr);
  gap: var(--ov-mi-gap-md);
  align-items: start;
  min-width: 0;
  padding: 0.48rem 0.18rem 0.48rem 0;
  border-top: 1px solid var(--ov-mi-border-faint);
  background: transparent;
}
.ov-source-confidence-row:first-child {
  border-top: 0;
}
.ov-source-confidence-surface {
  color: var(--ov-source-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.12;
  overflow-wrap: anywhere;
}
.ov-source-confidence-row-status {
  color: var(--ov-source-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.12;
  margin-top: 0.18rem;
}
.ov-source-confidence-row-title {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-body);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.18;
  overflow-wrap: anywhere;
}
.ov-source-confidence-row-detail,
.ov-source-confidence-row-meta,
.ov-source-confidence-row-basis,
.ov-source-confidence-row-usage,
.ov-source-confidence-row-action,
.ov-source-confidence-row-caveat {
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.23;
  overflow-wrap: anywhere;
}
.ov-source-confidence-row-detail,
.ov-source-confidence-row-usage,
.ov-source-confidence-row-action {
  margin-top: 0.14rem;
}
.ov-source-confidence-row-meta,
.ov-source-confidence-row-caveat {
  margin-top: 0;
}
.ov-source-confidence-row-basis strong,
.ov-source-confidence-row-usage strong,
.ov-source-confidence-row-action strong {
  display: block;
  margin-bottom: 0.12rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.1;
}
.ov-source-confidence-row-action {
  color: var(--ov-source-tone, var(--ov-mi-color-neutral));
  font-weight: var(--ov-mi-weight-label);
}
.ov-source-confidence-boundary {
  margin-top: 0.44rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.25;
  overflow-wrap: anywhere;
}
.ov-macro-cockpit-boundary {
  margin-top: 0.56rem;
  padding-top: 0.42rem;
  border-top: 1px solid var(--ov-mi-border-faint);
  background: transparent;
}
.ov-macro-cockpit-refresh-assist {
  margin-top: 0.5rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.25;
}
.ov-macro-cockpit-refresh-reflection {
  display: flex;
  flex-wrap: wrap;
  gap: 0.22rem 0.48rem;
  align-items: baseline;
  margin: 0.35rem 0 0.46rem 0;
  padding: 0.34rem 0.48rem;
  border: 1px solid color-mix(in srgb, var(--ov-refresh-reflection-tone, var(--ov-mi-color-neutral)) 24%, transparent);
  border-left: 3px solid var(--ov-refresh-reflection-tone, var(--ov-mi-color-neutral));
  border-radius: var(--ov-mi-radius-card);
  background: color-mix(in srgb, var(--ov-refresh-reflection-tone, var(--ov-mi-color-neutral)) 6%, var(--ov-mi-color-surface));
}
.ov-macro-cockpit-refresh-reflection-label {
  color: var(--ov-refresh-reflection-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.16;
}
.ov-macro-cockpit-refresh-reflection-detail {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.18;
}
.ov-ia-closeout {
  margin: 0.1rem 0 0.95rem 0;
  padding: 0.62rem;
  border: 1px solid var(--ov-mi-border-faint);
  border-radius: var(--ov-mi-radius-panel);
  background:
    linear-gradient(180deg, rgba(248,250,252,0.92), rgba(255,255,255,0.96)),
    var(--ov-mi-color-surface);
}
.ov-ia-closeout-head {
  display: grid;
  grid-template-columns: minmax(14rem, 1fr) auto;
  gap: var(--ov-mi-gap-md);
  align-items: start;
  margin-bottom: 0.5rem;
}
.ov-ia-closeout-kicker {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.15;
  text-transform: uppercase;
}
.ov-ia-closeout-title {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-title);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.2;
  margin-top: 0.15rem;
  overflow-wrap: anywhere;
}
.ov-ia-closeout-detail,
.ov-ia-closeout-boundary {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.27;
  overflow-wrap: anywhere;
}
.ov-ia-closeout-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--ov-mi-gap-sm);
}
.ov-ia-closeout-body {
  padding-top: 0.04rem;
}
.ov-ia-closeout-card {
  min-width: 0;
  padding: 0.52rem 0.58rem;
  border: 1px solid var(--ov-mi-border-faint);
  border-left: 3px solid var(--ov-ia-tone, var(--ov-mi-color-neutral));
  border-radius: var(--ov-mi-radius-card);
  background: rgba(255,255,255,0.9);
}
.ov-ia-closeout-card-head {
  display: flex;
  justify-content: space-between;
  gap: var(--ov-mi-gap-sm);
  align-items: flex-start;
}
.ov-ia-closeout-card-title {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-body);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.18;
}
.ov-ia-closeout-card-status {
  flex: 0 0 auto;
  color: var(--ov-ia-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.12;
  text-align: right;
}
.ov-ia-closeout-card-detail,
.ov-ia-closeout-owner,
.ov-ia-closeout-next {
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.24;
  overflow-wrap: anywhere;
}
.ov-ia-closeout-card-detail {
  margin-top: 0.22rem;
}
.ov-ia-closeout-owner {
  margin-top: 0.24rem;
  padding-top: 0.22rem;
  border-top: 1px solid var(--ov-mi-border-faint);
}
.ov-ia-closeout-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: var(--ov-mi-gap-xs);
  margin-top: 0.3rem;
}
.ov-ia-closeout-chip {
  display: inline-flex;
  align-items: center;
  min-height: 1.28rem;
  padding: 0.13rem 0.38rem;
  border: 1px solid color-mix(in srgb, var(--ov-ia-tone, var(--ov-mi-color-neutral)) 26%, transparent);
  border-radius: var(--ov-mi-radius-pill);
  background: color-mix(in srgb, var(--ov-ia-tone, var(--ov-mi-color-neutral)) 7%, transparent);
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.08;
}
.ov-ia-closeout-next {
  margin-top: 0.22rem;
}
.ov-ia-closeout-boundary {
  margin-top: 0.44rem;
}
.ov-data-handoff {
  margin: 0.48rem 0 0.88rem 0;
  padding: 0.68rem;
  border: 1px solid var(--ov-mi-border-faint);
  border-left: 4px solid var(--ov-handoff-tone, var(--ov-mi-color-neutral));
  border-radius: var(--ov-mi-radius-panel);
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--ov-handoff-tone, var(--ov-mi-color-neutral)) 6%, var(--ov-mi-color-surface)), rgba(255,255,255,0.98)),
    var(--ov-mi-color-surface);
}
.ov-data-handoff-head {
  display: grid;
  grid-template-columns: minmax(14rem, 1fr) auto;
  gap: var(--ov-mi-gap-md);
  align-items: start;
  margin-bottom: 0.56rem;
}
.ov-data-handoff-kicker {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.15;
  text-transform: uppercase;
}
.ov-data-handoff-title {
  margin-top: 0.16rem;
  color: var(--ov-mi-color-text);
  font-size: 1rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.2;
  overflow-wrap: anywhere;
}
.ov-data-handoff-detail {
  margin-top: 0.16rem;
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.3;
  overflow-wrap: anywhere;
}
.ov-data-handoff-status {
  display: inline-flex;
  align-items: center;
  min-height: 1.42rem;
  padding: 0.17rem 0.5rem;
  border: 1px solid color-mix(in srgb, var(--ov-handoff-tone, var(--ov-mi-color-neutral)) 36%, transparent);
  border-radius: var(--ov-mi-radius-pill);
  background: color-mix(in srgb, var(--ov-handoff-tone, var(--ov-mi-color-neutral)) 9%, transparent);
  color: var(--ov-handoff-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.1;
  white-space: nowrap;
}
.ov-data-handoff-counts {
  display: flex;
  flex-wrap: wrap;
  gap: var(--ov-mi-gap-xs);
  margin-bottom: 0.5rem;
}
.ov-data-handoff-count {
  display: inline-flex;
  align-items: center;
  min-height: 1.28rem;
  padding: 0.13rem 0.38rem;
  border: 1px solid color-mix(in srgb, var(--ov-count-tone, var(--ov-mi-color-neutral)) 26%, transparent);
  border-radius: var(--ov-mi-radius-pill);
  background: color-mix(in srgb, var(--ov-count-tone, var(--ov-mi-color-neutral)) 7%, transparent);
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.08;
}
.ov-data-handoff-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--ov-mi-gap-md);
}
.ov-data-handoff-card {
  min-width: 0;
  padding: 0.56rem 0.62rem;
  border: 1px solid var(--ov-mi-border-faint);
  border-left: 3px solid var(--ov-item-tone, var(--ov-mi-color-neutral));
  border-radius: var(--ov-mi-radius-card);
  background: rgba(255,255,255,0.92);
}
.ov-data-handoff-card-head {
  display: flex;
  justify-content: space-between;
  gap: var(--ov-mi-gap-sm);
  align-items: flex-start;
}
.ov-data-handoff-area {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-body);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.18;
  overflow-wrap: anywhere;
}
.ov-data-handoff-rank {
  flex: 0 0 auto;
  color: var(--ov-item-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.12;
  text-align: right;
}
.ov-data-handoff-meta,
.ov-data-handoff-action,
.ov-data-handoff-target,
.ov-data-handoff-boundary,
.ov-data-handoff-empty {
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.28;
  overflow-wrap: anywhere;
}
.ov-data-handoff-meta {
  margin-top: 0.26rem;
}
.ov-data-handoff-action {
  margin-top: 0.34rem;
  color: var(--ov-mi-color-text);
}
.ov-data-handoff-target {
  margin-top: 0.28rem;
  padding-top: 0.32rem;
  border-top: 1px solid var(--ov-mi-border-faint);
}
.ov-data-handoff-boundary,
.ov-data-handoff-empty {
  margin-top: 0.52rem;
  padding: 0.4rem 0.48rem;
  border: 1px solid var(--ov-mi-border-faint);
  border-radius: var(--ov-mi-radius-card);
  background: rgba(248,250,252,0.78);
}
.ov-breadth-summary,
.ov-macro-week-lane {
  margin: 0.48rem 0 0.82rem 0;
  padding: 0.66rem;
  border: 1px solid var(--ov-mi-border-faint);
  border-left: 4px solid var(--ov-band-tone, var(--ov-mi-color-neutral));
  border-radius: var(--ov-mi-radius-panel);
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--ov-band-tone, var(--ov-mi-color-neutral)) 6%, var(--ov-mi-color-surface)), rgba(255,255,255,0.98)),
    var(--ov-mi-color-surface);
}
.ov-breadth-head,
.ov-macro-week-head {
  display: grid;
  grid-template-columns: minmax(14rem, 1fr) auto;
  gap: var(--ov-mi-gap-md);
  align-items: start;
  margin-bottom: 0.54rem;
}
.ov-breadth-kicker,
.ov-macro-week-kicker {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.15;
  text-transform: uppercase;
}
.ov-breadth-title,
.ov-macro-week-title {
  margin-top: 0.16rem;
  color: var(--ov-mi-color-text);
  font-size: 1rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.2;
  overflow-wrap: anywhere;
}
.ov-breadth-detail,
.ov-macro-week-detail,
.ov-breadth-boundary,
.ov-macro-week-boundary {
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.28;
  overflow-wrap: anywhere;
}
.ov-breadth-detail,
.ov-macro-week-detail {
  margin-top: 0.16rem;
}
.ov-breadth-status,
.ov-macro-week-status {
  display: inline-flex;
  align-items: center;
  min-height: 1.42rem;
  padding: 0.17rem 0.5rem;
  border: 1px solid color-mix(in srgb, var(--ov-band-tone, var(--ov-mi-color-neutral)) 36%, transparent);
  border-radius: var(--ov-mi-radius-pill);
  background: color-mix(in srgb, var(--ov-band-tone, var(--ov-mi-color-neutral)) 9%, transparent);
  color: var(--ov-band-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.1;
  white-space: nowrap;
}
.ov-breadth-card-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--ov-mi-gap-sm);
}
.ov-breadth-card {
  min-width: 0;
  padding: 0.5rem 0.56rem;
  border: 1px solid color-mix(in srgb, var(--ov-card-tone, var(--ov-mi-color-neutral)) 25%, transparent);
  border-top: 3px solid var(--ov-card-tone, var(--ov-mi-color-neutral));
  border-radius: var(--ov-mi-radius-card);
  background: rgba(255,255,255,0.9);
}
.ov-breadth-card-label,
.ov-breadth-row-label,
.ov-macro-week-cluster-label,
.ov-macro-week-item-meta {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.14;
  overflow-wrap: anywhere;
}
.ov-breadth-card-value,
.ov-breadth-row-value,
.ov-macro-week-cluster-value,
.ov-macro-week-item-title {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-body);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.18;
  margin-top: 0.16rem;
  overflow-wrap: anywhere;
}
.ov-breadth-card-detail,
.ov-breadth-row-detail,
.ov-macro-week-item-detail {
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.24;
  margin-top: 0.14rem;
  overflow-wrap: anywhere;
}
.ov-breadth-row-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: var(--ov-mi-gap-xs);
  margin-top: 0.5rem;
}
.ov-breadth-row {
  min-width: 0;
  padding: 0.43rem 0.48rem;
  border-left: 3px solid var(--ov-row-tone, var(--ov-mi-color-neutral));
  border-radius: var(--ov-mi-radius-card);
  background: rgba(248,250,252,0.82);
}
.ov-sector-breadth-map {
  margin: 0.44rem 0 0.74rem 0;
  padding: 0.58rem;
  border: 1px solid var(--ov-mi-border-faint);
  border-left: 4px solid var(--ov-band-tone, var(--ov-mi-color-neutral));
  border-radius: 0 var(--ov-mi-radius-panel) var(--ov-mi-radius-panel) 0;
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--ov-band-tone, var(--ov-mi-color-neutral)) 5%, var(--ov-mi-color-surface)), rgba(255,255,255,0.98)),
    var(--ov-mi-color-surface);
}
.ov-sector-breadth-head {
  display: grid;
  grid-template-columns: minmax(14rem, 1fr) auto;
  gap: var(--ov-mi-gap-md);
  align-items: start;
  margin-bottom: 0.52rem;
}
.ov-sector-breadth-kicker {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.15;
  text-transform: uppercase;
}
.ov-sector-breadth-title {
  margin-top: 0.16rem;
  color: var(--ov-mi-color-text);
  font-size: 1rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.2;
  overflow-wrap: anywhere;
}
.ov-sector-breadth-detail,
.ov-sector-breadth-boundary {
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.28;
  overflow-wrap: anywhere;
}
.ov-sector-breadth-detail {
  margin-top: 0.16rem;
}
.ov-sector-breadth-status {
  display: inline-flex;
  align-items: center;
  min-height: 1.42rem;
  padding: 0.17rem 0.5rem;
  border: 1px solid color-mix(in srgb, var(--ov-band-tone, var(--ov-mi-color-neutral)) 34%, transparent);
  border-radius: var(--ov-mi-radius-pill);
  background: color-mix(in srgb, var(--ov-band-tone, var(--ov-mi-color-neutral)) 8%, transparent);
  color: var(--ov-band-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.1;
  white-space: nowrap;
}
.ov-sector-breadth-rail {
  position: relative;
  height: 0.46rem;
  border-radius: var(--ov-mi-radius-pill);
  background: color-mix(in srgb, var(--ov-mi-color-neutral) 13%, transparent);
  overflow: hidden;
}
.ov-sector-breadth-rail-fill {
  display: block;
  width: var(--ov-rail-fill, 0%);
  height: 100%;
  border-radius: var(--ov-mi-radius-pill);
  background: var(--ov-band-tone, var(--ov-mi-color-positive));
}
.ov-sector-breadth-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  border-top: 1px solid var(--ov-mi-border-faint);
  border-bottom: 1px solid var(--ov-mi-border-faint);
  margin-top: 0.5rem;
}
.ov-sector-breadth-stat {
  min-width: 0;
  padding: 0.4rem 0.52rem;
  border-left: 1px solid var(--ov-mi-border-faint);
}
.ov-sector-breadth-stat:first-child {
  border-left: 0;
}
.ov-sector-breadth-stat-label,
.ov-sector-breadth-stat span,
.ov-sector-breadth-lane-detail,
.ov-sector-breadth-lane-foot,
.ov-sector-breadth-leader small {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.18;
  overflow-wrap: anywhere;
}
.ov-sector-breadth-stat strong {
  display: block;
  margin: 0.08rem 0 0.06rem 0;
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-title);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.14;
  overflow-wrap: anywhere;
}
.ov-sector-breadth-lanes {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--ov-mi-gap-sm);
  margin-top: 0.56rem;
  max-height: 31rem;
  overflow-y: auto;
  overscroll-behavior: contain;
}
.ov-sector-breadth-lane {
  min-width: 0;
  padding: 0.48rem 0.52rem;
  border: 1px solid color-mix(in srgb, var(--ov-lane-tone, var(--ov-mi-color-neutral)) 24%, transparent);
  border-radius: var(--ov-mi-radius-card);
  background: rgba(248,250,252,0.78);
}
.ov-sector-breadth-lane-head {
  display: flex;
  justify-content: space-between;
  gap: var(--ov-mi-gap-sm);
  align-items: baseline;
  color: var(--ov-mi-color-text);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.16;
  overflow-wrap: anywhere;
}
.ov-sector-breadth-lane-head strong {
  color: var(--ov-lane-tone, var(--ov-mi-color-neutral));
  white-space: nowrap;
}
.ov-sector-breadth-lane-track {
  position: relative;
  height: 0.48rem;
  margin-top: 0.36rem;
  border-radius: var(--ov-mi-radius-pill);
  background: rgba(148,163,184,0.18);
  overflow: hidden;
}
.ov-sector-breadth-zero {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  width: 1px;
  background: rgba(100,116,139,0.42);
}
.ov-sector-breadth-bar {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  width: var(--ov-lane-bar, 0%);
  border-radius: var(--ov-mi-radius-pill);
  background: var(--ov-lane-tone, var(--ov-mi-color-neutral));
}
.ov-sector-breadth-bar--negative {
  left: auto;
  right: 50%;
}
.ov-sector-breadth-lane-detail,
.ov-sector-breadth-lane-foot {
  margin-top: 0.28rem;
}
.ov-sector-breadth-leader-strip {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: var(--ov-mi-gap-xs);
  margin-top: 0.55rem;
}
.ov-sector-breadth-leader {
  min-width: 0;
  padding: 0.4rem 0.46rem;
  border-left: 3px solid var(--ov-leader-tone, var(--ov-mi-color-neutral));
  border-radius: var(--ov-mi-radius-card);
  background: rgba(255,255,255,0.72);
}
.ov-sector-breadth-leader span,
.ov-sector-breadth-leader strong,
.ov-sector-breadth-leader small {
  display: block;
  overflow-wrap: anywhere;
}
.ov-sector-breadth-leader span {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.12;
}
.ov-sector-breadth-leader strong {
  margin-top: 0.1rem;
  color: var(--ov-mi-color-text);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.12;
}
.ov-sector-breadth-boundary {
  margin-top: 0.52rem;
  padding: 0.4rem 0.48rem;
  border: 1px solid var(--ov-mi-border-faint);
  border-radius: var(--ov-mi-radius-card);
  background: rgba(248,250,252,0.78);
}
.ov-macro-week-clusters {
  display: flex;
  flex-wrap: wrap;
  gap: var(--ov-mi-gap-xs);
  margin-bottom: 0.48rem;
}
.ov-macro-week-cluster {
  display: inline-flex;
  align-items: baseline;
  gap: 0.24rem;
  min-height: 1.42rem;
  padding: 0.18rem 0.45rem;
  border: 1px solid color-mix(in srgb, var(--ov-cluster-tone, var(--ov-mi-color-neutral)) 28%, transparent);
  border-radius: var(--ov-mi-radius-pill);
  background: color-mix(in srgb, var(--ov-cluster-tone, var(--ov-mi-color-neutral)) 8%, transparent);
}
.ov-macro-week-cluster-value {
  color: var(--ov-cluster-tone, var(--ov-mi-color-neutral));
  margin-top: 0;
}
.ov-macro-week-section {
  margin-top: 0.42rem;
}
.ov-macro-week-section-head {
  display: flex;
  justify-content: space-between;
  gap: var(--ov-mi-gap-sm);
  margin-bottom: 0.28rem;
}
.ov-macro-week-section-title {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.2;
}
.ov-macro-week-section-note {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.2;
  text-align: right;
}
.ov-macro-week-items {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--ov-mi-gap-sm);
}
.ov-macro-week-item {
  min-width: 0;
  padding: 0.5rem 0.56rem;
  border: 1px solid var(--ov-mi-border-faint);
  border-left: 3px solid var(--ov-item-tone, var(--ov-mi-color-neutral));
  border-radius: var(--ov-mi-radius-card);
  background: rgba(255,255,255,0.9);
}
.ov-breadth-boundary,
.ov-macro-week-boundary {
  margin-top: 0.52rem;
  padding: 0.38rem 0.46rem;
  border: 1px solid var(--ov-mi-border-faint);
  border-radius: var(--ov-mi-radius-card);
  background: rgba(248,250,252,0.78);
}
.ov-mm-refresh-rail {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--ov-mi-gap-md);
  padding: 0.42rem 0;
  border-top: 1px solid var(--ov-mi-border-faint);
  border-bottom: 1px solid var(--ov-mi-border-faint);
  margin: 0.18rem 0 0.48rem 0;
}
.ov-mm-state-cluster {
  display: flex;
  align-items: center;
  gap: var(--ov-mi-gap-sm);
  min-width: 0;
  flex-wrap: wrap;
}
.ov-mm-refresh-eyebrow {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.12;
}
.ov-mm-state-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.38rem;
  min-height: 1.58rem;
  padding: 0.18rem 0.52rem;
  border-radius: var(--ov-mi-radius-pill);
  border: 1px solid var(--ov-mi-border-subtle);
  background: var(--ov-mi-fill-subtle);
}
.ov-mm-state-dot {
  width: 0.44rem;
  height: 0.44rem;
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
  min-height: 1.46rem;
  padding: 0.14rem 0.44rem;
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
.ov-mm-section-divider {
  display: flex;
  align-items: center;
  gap: var(--ov-mi-gap-sm);
  min-width: 0;
  margin: 0.84rem 0 0.42rem 0;
  color: inherit;
}
.ov-mm-section-divider::after {
  content: "";
  flex: 1 1 2rem;
  height: 1px;
  background: color-mix(in srgb, currentColor 18%, transparent);
}
.ov-mm-section-label {
  color: currentColor;
  font-size: var(--ov-mi-font-body);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.16;
  white-space: nowrap;
}
.ov-mm-section-detail {
  min-width: 0;
  color: color-mix(in srgb, currentColor 66%, transparent);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.2;
  overflow-wrap: anywhere;
}
div[class*="st-key-overview_market_movers_refresh_mode"] div[data-baseweb="select"] > div {
  min-height: 2rem;
}
div[class*="st-key-overview_"][class*="_intraday_refresh"] button,
div[class*="st-key-overview_"][class*="_eod_history_refresh"] button,
div[class*="st-key-overview_"][class*="_market_movers_reload"] button,
div[class*="st-key-overview_"][class*="_universe_static"] button,
div[class*="st-key-overview_sp500_universe_refresh"] button,
div[class*="st-key-overview_nasdaq_symbol_directory_refresh"] button {
  min-height: 2rem;
  padding-top: 0.25rem;
  padding-bottom: 0.25rem;
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
.ov-futures-command {
  display: grid;
  grid-template-columns: minmax(17rem, 1.2fr) minmax(16rem, 1fr) minmax(16rem, 1fr);
  gap: var(--ov-mi-gap-md);
  align-items: stretch;
  margin: 0.42rem 0 0.85rem 0;
  padding: 0.58rem;
  border-top: 1px solid var(--ov-mi-border-subtle);
  border-bottom: 1px solid var(--ov-mi-border-subtle);
  border-radius: var(--ov-mi-radius-panel);
  background:
    linear-gradient(90deg, rgba(15, 118, 110, 0.08), rgba(37, 99, 235, 0.06) 52%, rgba(255, 255, 255, 0)),
    var(--ov-mi-color-surface);
}
.ov-futures-command-cell {
  min-width: 0;
  padding: 0.5rem 0.65rem;
  border-left: 1px solid var(--ov-mi-border-faint);
}
.ov-futures-command-cell:first-child {
  border-left: 0;
}
.ov-futures-kicker {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  letter-spacing: 0;
  text-transform: uppercase;
}
.ov-futures-title {
  color: var(--ov-mi-color-text);
  font-size: 1.08rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.18;
  margin-top: 0.22rem;
  overflow-wrap: anywhere;
}
.ov-futures-detail {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.26;
  margin-top: 0.18rem;
  overflow-wrap: anywhere;
}
.ov-futures-feed-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--ov-mi-gap-xs);
  margin-top: 0.35rem;
}
.ov-futures-feed-pill {
  display: inline-flex;
  align-items: center;
  min-height: 1.5rem;
  padding: 0.22rem 0.48rem;
  border-radius: var(--ov-mi-radius-pill);
  border: 1px solid color-mix(in srgb, var(--ov-feed-tone, var(--ov-mi-color-neutral)) 34%, transparent);
  background: color-mix(in srgb, var(--ov-feed-tone, var(--ov-mi-color-neutral)) 9%, transparent);
  color: var(--ov-feed-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.1;
}
.ov-futures-workbench-bar {
  display: grid;
  grid-template-columns: minmax(16rem, 1.15fr) minmax(15rem, 1fr) minmax(12rem, 0.78fr) minmax(14rem, 0.95fr);
  gap: 0;
  align-items: stretch;
  margin: 0.5rem 0 0.5rem 0;
  border: 1px solid var(--ov-mi-border-subtle);
  border-radius: var(--ov-mi-radius-panel);
  background: var(--ov-mi-color-surface);
  overflow: hidden;
}
.ov-futures-workbench-item {
  min-width: 0;
  padding: 0.68rem 0.82rem;
  border-left: 1px solid var(--ov-mi-border-faint);
  border-top: 3px solid color-mix(in srgb, var(--ov-workbench-tone, var(--ov-mi-color-neutral)) 72%, transparent);
  background: linear-gradient(180deg, color-mix(in srgb, var(--ov-workbench-tone, var(--ov-mi-color-neutral)) 6%, transparent), rgba(255,255,255,0));
}
.ov-futures-workbench-item:first-child {
  border-left: 0;
}
.ov-futures-workbench-label {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.15;
}
.ov-futures-workbench-value {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-title);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.2;
  margin-top: 0.18rem;
  overflow-wrap: anywhere;
}
.ov-futures-workbench-detail {
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.24;
  margin-top: 0.14rem;
  overflow-wrap: anywhere;
}
.ov-futures-refresh-module {
  display: grid;
  gap: var(--ov-mi-gap-md);
  margin: 0 0 0.48rem 0;
  padding: 0.72rem 0.78rem;
  border: 1px solid var(--ov-mi-border-faint);
  border-radius: var(--ov-mi-radius-panel);
  background: var(--ov-mi-color-surface);
}
.ov-futures-refresh-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--ov-mi-gap-md);
}
.ov-futures-refresh-title {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-title);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.2;
}
.ov-futures-refresh-meta {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.2;
}
.ov-futures-refresh-sources {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--ov-mi-gap-sm);
}
.ov-futures-refresh-source {
  min-width: 0;
  padding: 0.58rem 0.66rem;
  border: 1px solid color-mix(in srgb, var(--ov-refresh-tone, var(--ov-mi-color-neutral)) 24%, transparent);
  border-left: 4px solid var(--ov-refresh-tone, var(--ov-mi-color-neutral));
  border-radius: var(--ov-mi-radius-card);
  background: color-mix(in srgb, var(--ov-refresh-tone, var(--ov-mi-color-neutral)) 5%, transparent);
}
.ov-futures-refresh-source-label {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.1;
}
.ov-futures-refresh-source-main {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--ov-mi-gap-sm);
  margin-top: 0.18rem;
}
.ov-futures-refresh-source-main strong {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-body);
  font-weight: var(--ov-mi-weight-value);
}
.ov-futures-refresh-source-main span {
  color: var(--ov-refresh-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
}
.ov-futures-refresh-source-detail {
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.25;
  margin-top: 0.14rem;
  overflow-wrap: anywhere;
}
.ov-futures-watch-strip {
  display: grid;
  grid-template-columns: minmax(8rem, 0.22fr) minmax(0, 1fr);
  gap: var(--ov-mi-gap-md);
  align-items: stretch;
  margin: 0.35rem 0 0.7rem 0;
  padding: 0.58rem 0.66rem;
  border: 1px solid var(--ov-mi-border-faint);
  border-radius: var(--ov-mi-radius-panel);
  background: var(--ov-mi-color-surface-subtle);
}
.ov-futures-watch-head {
  display: flex;
  min-width: 0;
  flex-direction: column;
  justify-content: center;
  gap: 0.18rem;
  padding-right: 0.2rem;
}
.ov-futures-watch-label {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-body);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.18;
}
.ov-futures-watch-note {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.24;
}
.ov-futures-watch-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(8.2rem, 1fr));
  gap: var(--ov-mi-gap-xs);
  min-width: 0;
}
.ov-futures-watch-item {
  min-width: 0;
  padding: 0.48rem 0.52rem;
  border: 1px solid color-mix(in srgb, var(--ov-watch-tone, var(--ov-mi-color-neutral)) 25%, transparent);
  border-top: 3px solid var(--ov-watch-tone, var(--ov-mi-color-neutral));
  border-radius: var(--ov-mi-radius-card);
  background: rgba(255,255,255,0.78);
}
.ov-futures-watch-symbol {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-body);
  font-weight: var(--ov-mi-weight-value);
  line-height: 1.15;
}
.ov-futures-watch-title {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.18;
  margin-top: 0.1rem;
  min-height: 1.05rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ov-futures-watch-move {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.22;
  margin-top: 0.28rem;
}
.ov-futures-watch-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.22rem;
  margin-top: 0.3rem;
}
.ov-futures-watch-meta span {
  display: inline-flex;
  align-items: center;
  min-height: 1.24rem;
  padding: 0.12rem 0.34rem;
  border-radius: var(--ov-mi-radius-pill);
  background: color-mix(in srgb, var(--ov-watch-tone, var(--ov-mi-color-neutral)) 9%, transparent);
  color: var(--ov-watch-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.1;
}
.ov-futures-section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--ov-mi-gap-md);
  margin: 0.48rem 0 0.5rem 0;
  padding-bottom: 0.35rem;
  border-bottom: 1px solid var(--ov-mi-border-faint);
}
.ov-futures-section-title {
  color: inherit;
  font-size: var(--ov-mi-font-title);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.2;
}
.ov-futures-section-meta {
  color: color-mix(in srgb, currentColor 72%, transparent);
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
}
.ov-futures-symbol-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--ov-mi-gap-md);
  margin: 0.34rem 0 0.18rem 0;
}
.ov-futures-symbol-title {
  color: inherit;
  font-size: var(--ov-mi-font-body);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.2;
}
.ov-futures-symbol-meta {
  color: color-mix(in srgb, currentColor 72%, transparent);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.18;
  text-align: right;
}
.ov-futures-quiet-note {
  color: color-mix(in srgb, currentColor 72%, transparent);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.25;
  margin: 0.2rem 0 0.35rem 0;
}
.ov-futures-control-note {
  color: color-mix(in srgb, currentColor 68%, transparent);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.25;
  margin: 0.15rem 0 0.35rem 0;
}
.ov-futures-live-strip,
.ov-futures-macro-strip,
.ov-futures-week-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--ov-mi-gap-sm);
  margin: 0.35rem 0 0.65rem 0;
}
.ov-futures-live-item,
.ov-futures-macro-item,
.ov-futures-week-item {
  min-width: 0;
  padding: 0.58rem 0.68rem;
  border: 1px solid color-mix(in srgb, var(--ov-signal-tone, var(--ov-mi-color-neutral)) 28%, transparent);
  border-top: 3px solid var(--ov-signal-tone, var(--ov-mi-color-neutral));
  border-radius: var(--ov-mi-radius-panel);
  background: color-mix(in srgb, var(--ov-signal-tone, var(--ov-mi-color-neutral)) 5%, transparent);
}
.ov-futures-live-label,
.ov-futures-macro-label,
.ov-futures-week-label {
  color: color-mix(in srgb, currentColor 68%, transparent);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.15;
  text-transform: uppercase;
}
.ov-futures-live-value,
.ov-futures-macro-value,
.ov-futures-week-value {
  color: inherit;
  font-size: 1.02rem;
  font-weight: var(--ov-mi-weight-value);
  line-height: 1.16;
  margin-top: 0.22rem;
  overflow-wrap: anywhere;
}
.ov-futures-live-detail,
.ov-futures-macro-detail,
.ov-futures-week-detail {
  color: color-mix(in srgb, currentColor 70%, transparent);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.22;
  margin-top: 0.16rem;
  overflow-wrap: anywhere;
}
.ov-futures-chart-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--ov-mi-gap-md);
  margin-bottom: 0.38rem;
}
.ov-futures-chart-title {
  color: inherit;
  font-size: 1.02rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.18;
}
.ov-futures-chart-subtitle {
  color: color-mix(in srgb, currentColor 68%, transparent);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.2;
  margin-top: 0.15rem;
}
.ov-futures-chart-state {
  display: inline-flex;
  align-items: center;
  min-height: 1.45rem;
  padding: 0.18rem 0.45rem;
  border-radius: var(--ov-mi-radius-pill);
  border: 1px solid color-mix(in srgb, var(--ov-chart-tone, var(--ov-mi-color-neutral)) 34%, transparent);
  background: color-mix(in srgb, var(--ov-chart-tone, var(--ov-mi-color-neutral)) 9%, transparent);
  color: var(--ov-chart-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.1;
  white-space: nowrap;
}
.ov-futures-chart-question {
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-body);
  line-height: 1.36;
  margin: 0.12rem 0 0.58rem 0;
  padding: 0.48rem 0.62rem;
  border-left: 3px solid var(--ov-mi-color-primary);
  background: color-mix(in srgb, var(--ov-mi-color-primary) 5%, transparent);
  border-radius: var(--ov-mi-radius-card);
}
.ov-futures-chart-metrics,
.ov-futures-score-lane {
  display: flex;
  align-items: center;
  gap: var(--ov-mi-gap-xs);
  flex-wrap: wrap;
  margin: 0.1rem 0 0.48rem 0;
}
.ov-futures-mini-metric,
.ov-futures-score-chip {
  display: inline-flex;
  align-items: baseline;
  gap: 0.25rem;
  min-height: 1.55rem;
  padding: 0.22rem 0.5rem;
  border-radius: var(--ov-mi-radius-pill);
  border: 1px solid color-mix(in srgb, var(--ov-chip-tone, var(--ov-mi-color-neutral)) 30%, transparent);
  background: color-mix(in srgb, var(--ov-chip-tone, var(--ov-mi-color-neutral)) 8%, transparent);
  color: inherit;
  font-size: var(--ov-mi-font-caption);
  line-height: 1.1;
  white-space: nowrap;
}
.ov-futures-mini-metric-label,
.ov-futures-score-label {
  color: color-mix(in srgb, currentColor 62%, transparent);
  font-weight: var(--ov-mi-weight-label);
}
.ov-futures-mini-metric-value,
.ov-futures-score-value {
  color: var(--ov-chip-tone, var(--ov-mi-color-neutral));
  font-weight: var(--ov-mi-weight-value);
}
.ov-futures-macro-hero {
  padding: 0.15rem 0 0.15rem 0;
}
.ov-futures-macro-action-copy {
  min-width: 0;
  padding: 0.04rem 0 0.1rem 0;
}
.ov-futures-macro-action-title {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-title);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.2;
}
.ov-futures-macro-action-meta {
  color: color-mix(in srgb, currentColor 72%, transparent);
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.28;
  margin-top: 0.12rem;
  overflow-wrap: anywhere;
}
.ov-futures-macro-action-detail {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.26;
  margin-top: 0.12rem;
  overflow-wrap: anywhere;
}
.ov-futures-macro-action-rule {
  height: 1px;
  margin: 0.04rem 0 0.62rem 0;
  border-bottom: 1px solid var(--ov-mi-border-faint);
}
.st-key-overview_futures_macro_tab_daily_refresh button,
.st-key-overview_futures_macro_tab_reload button {
  min-height: 2.35rem;
  padding: 0.36rem 0.7rem;
  border-radius: var(--ov-mi-radius-card);
  box-shadow: none;
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
  letter-spacing: 0;
  line-height: 1.18;
}
.st-key-overview_futures_macro_tab_daily_refresh button {
  border: 1px solid #0f766e;
  background: #0f766e;
  color: #fff;
}
.st-key-overview_futures_macro_tab_daily_refresh button:hover {
  border-color: #115e59;
  background: #115e59;
  color: #fff;
}
.st-key-overview_futures_macro_tab_reload button {
  border: 1px solid var(--ov-mi-border-control);
  background: rgba(255,255,255,0.76);
  color: var(--ov-mi-color-text);
}
.st-key-overview_futures_macro_tab_reload button:hover {
  border-color: color-mix(in srgb, var(--ov-mi-color-primary) 34%, var(--ov-mi-border-control));
  background: color-mix(in srgb, var(--ov-mi-color-primary) 7%, rgba(255,255,255,0.9));
  color: var(--ov-mi-color-text);
}
.ov-futures-brief {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(18rem, 0.95fr);
  gap: var(--ov-mi-gap-md);
  align-items: stretch;
  margin: 0.3rem 0 0.8rem 0;
  padding: 0.85rem;
  border: 1px solid var(--ov-mi-border-subtle);
  border-radius: var(--ov-mi-radius-panel);
  background:
    linear-gradient(135deg, rgba(37, 99, 235, 0.07), rgba(15, 118, 110, 0.055) 48%, rgba(255, 255, 255, 0)),
    var(--ov-mi-color-surface);
}
.ov-futures-brief-main {
  min-width: 0;
  padding-right: 0.2rem;
}
.ov-futures-brief-eyebrow {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.15;
}
.ov-futures-brief-scenario {
  color: var(--ov-mi-color-text);
  font-size: 1.38rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.18;
  margin-top: 0.24rem;
  overflow-wrap: anywhere;
}
.ov-futures-brief-subscenario {
  display: inline-flex;
  align-items: center;
  max-width: 100%;
  margin-top: 0.42rem;
  padding: 0.22rem 0.5rem;
  border-radius: var(--ov-mi-radius-pill);
  border: 1px solid var(--ov-mi-border-control);
  background: rgba(255,255,255,0.68);
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.24;
  overflow-wrap: anywhere;
}
.ov-futures-brief-mixed-reason {
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.42;
  margin-top: 0.38rem;
  max-width: 68rem;
}
.ov-futures-brief-sentence {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-body);
  line-height: 1.46;
  margin-top: 0.5rem;
  max-width: 68rem;
}
.ov-futures-brief-evidence {
  display: flex;
  flex-wrap: wrap;
  gap: var(--ov-mi-gap-xs);
  margin-top: 0.62rem;
}
.ov-futures-brief-evidence-chip {
  display: inline-flex;
  align-items: center;
  min-height: 1.5rem;
  padding: 0.2rem 0.48rem;
  border-radius: var(--ov-mi-radius-pill);
  border: 1px solid var(--ov-mi-border-control);
  background: rgba(255,255,255,0.72);
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
}
.ov-futures-brief-support {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--ov-mi-gap-sm);
}
.ov-futures-brief-support-item {
  min-width: 0;
  padding: 0.58rem 0.62rem;
  border: 1px solid color-mix(in srgb, var(--ov-brief-tone, var(--ov-mi-color-neutral)) 25%, transparent);
  border-left: 3px solid var(--ov-brief-tone, var(--ov-mi-color-neutral));
  border-radius: var(--ov-mi-radius-card);
  background: rgba(255,255,255,0.72);
}
.ov-futures-brief-support-label {
  color: color-mix(in srgb, currentColor 66%, transparent);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
}
.ov-futures-brief-support-value {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-value);
  font-weight: var(--ov-mi-weight-value);
  line-height: 1.18;
  margin-top: 0.18rem;
}
.ov-futures-brief-support-detail {
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.22;
  margin-top: 0.15rem;
}
.ov-futures-macro-eyebrow {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  letter-spacing: 0;
  text-transform: uppercase;
}
.ov-futures-macro-scenario {
  color: inherit;
  font-size: 1.08rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.25;
  margin: 0.2rem 0 0.42rem 0;
}
.ov-futures-macro-sentence {
  color: inherit;
  font-size: var(--ov-mi-font-body);
  line-height: 1.42;
  margin-bottom: 0.44rem;
}
.ov-futures-macro-evidence {
  color: color-mix(in srgb, currentColor 70%, transparent);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.3;
  margin-bottom: 0.55rem;
}
.ov-futures-macro-week-summary {
  color: inherit;
  font-size: var(--ov-mi-font-body);
  line-height: 1.42;
  margin: 0.18rem 0 0.48rem 0;
}
.ov-futures-week-flow {
  margin: 0.62rem 0 0.62rem 0;
  padding: 0.78rem;
  border: 1px solid var(--ov-mi-border-subtle);
  border-radius: var(--ov-mi-radius-panel);
  background: var(--ov-mi-color-surface-subtle);
}
.ov-futures-week-flow-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--ov-mi-gap-md);
}
.ov-futures-week-flow-title {
  color: var(--ov-mi-color-text);
  font-size: 1.08rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.2;
}
.ov-futures-week-flow-basis {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.24;
  margin-top: 0.18rem;
}
.ov-futures-week-driver {
  display: inline-flex;
  align-items: baseline;
  gap: 0.35rem;
  padding: 0.34rem 0.56rem;
  border-radius: var(--ov-mi-radius-pill);
  border: 1px solid color-mix(in srgb, var(--ov-week-tone, var(--ov-mi-color-neutral)) 35%, transparent);
  background: color-mix(in srgb, var(--ov-week-tone, var(--ov-mi-color-neutral)) 9%, transparent);
  color: var(--ov-week-tone, var(--ov-mi-color-neutral));
  white-space: nowrap;
}
.ov-futures-week-driver span {
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
}
.ov-futures-week-driver strong {
  font-size: var(--ov-mi-font-value);
  font-weight: var(--ov-mi-weight-value);
}
.ov-futures-week-summary {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-body);
  line-height: 1.42;
  margin-top: 0.58rem;
}
.ov-futures-week-lanes {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--ov-mi-gap-md);
  margin-top: 0.62rem;
}
.ov-futures-week-lane {
  min-width: 0;
}
.ov-futures-week-lane-title {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  margin-bottom: 0.34rem;
}
.ov-futures-week-lane-item {
  display: grid;
  grid-template-columns: minmax(5.2rem, 0.6fr) minmax(4.4rem, 0.32fr) minmax(0, 1fr);
  gap: var(--ov-mi-gap-sm);
  align-items: center;
  min-width: 0;
  padding: 0.42rem 0.5rem;
  border-top: 1px solid var(--ov-mi-border-faint);
}
.ov-futures-week-lane-label {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
  overflow-wrap: anywhere;
}
.ov-futures-week-lane-value {
  color: var(--ov-week-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-value);
  white-space: nowrap;
}
.ov-futures-week-lane-detail,
.ov-futures-week-lane-empty {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.24;
  overflow-wrap: anywhere;
}
.ov-futures-evidence-state,
.ov-futures-validation-summary,
.ov-futures-data-management {
  margin: 0.45rem 0 0.85rem 0;
  padding: 0.72rem 0.78rem;
  border: 1px solid var(--ov-mi-border-faint);
  border-radius: var(--ov-mi-radius-panel);
  background: var(--ov-mi-color-surface);
}
.ov-futures-evidence-title,
.ov-futures-validation-title,
.ov-futures-data-management-title {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-title);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.2;
}
.ov-futures-evidence-summary,
.ov-futures-validation-coverage {
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.25;
  margin-top: 0.18rem;
}
.ov-futures-evidence-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--ov-mi-gap-sm);
  margin-top: 0.62rem;
}
.ov-futures-evidence-section {
  min-width: 0;
  padding: 0.58rem 0.62rem;
  border: 1px solid var(--ov-mi-border-faint);
  border-radius: var(--ov-mi-radius-card);
  background: var(--ov-mi-color-surface-subtle);
}
.ov-futures-evidence-section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--ov-mi-gap-sm);
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-body);
  font-weight: var(--ov-mi-weight-heading);
}
.ov-futures-evidence-section-head strong {
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
}
.ov-futures-evidence-description,
.ov-futures-evidence-empty {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.25;
  margin-top: 0.22rem;
}
.ov-futures-evidence-item {
  margin-top: 0.46rem;
  padding-top: 0.42rem;
  border-top: 1px solid var(--ov-mi-border-faint);
}
.ov-futures-evidence-item-title {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-body);
  font-weight: var(--ov-mi-weight-value);
  line-height: 1.2;
}
.ov-futures-evidence-item-meta {
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.18;
  margin-top: 0.12rem;
}
.ov-futures-evidence-item-meaning {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.28;
  margin-top: 0.16rem;
}
.ov-futures-validation-head {
  display: flex;
  align-items: stretch;
  justify-content: space-between;
  gap: var(--ov-mi-gap-md);
}
.ov-futures-validation-scenario {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-body);
  font-weight: var(--ov-mi-weight-value);
  line-height: 1.22;
  margin-top: 0.16rem;
}
.ov-futures-validation-occurrence {
  min-width: 8rem;
  padding: 0.48rem 0.58rem;
  border: 1px solid var(--ov-mi-border-faint);
  border-radius: var(--ov-mi-radius-card);
  background: var(--ov-mi-color-surface-subtle);
  text-align: right;
}
.ov-futures-validation-occurrence span,
.ov-futures-validation-metric span,
.ov-futures-data-management-grid span {
  display: block;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.12;
}
.ov-futures-validation-occurrence strong,
.ov-futures-validation-metric strong,
.ov-futures-data-management-grid strong {
  display: block;
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-value);
  font-weight: var(--ov-mi-weight-value);
  line-height: 1.18;
  margin-top: 0.13rem;
}
.ov-futures-validation-metrics,
.ov-futures-data-management-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--ov-mi-gap-sm);
  margin-top: 0.58rem;
}
.ov-futures-validation-metric,
.ov-futures-data-management-grid > div {
  min-width: 0;
  padding: 0.48rem 0.56rem;
  border: 1px solid var(--ov-mi-border-faint);
  border-radius: var(--ov-mi-radius-card);
  background: var(--ov-mi-color-surface-subtle);
}
.ov-futures-validation-copy,
.ov-futures-validation-effect {
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-body);
  line-height: 1.35;
  margin-top: 0.55rem;
}
.ov-futures-validation-effect {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
}
.ov-mm-command {
  min-width: 0;
  margin: 0.38rem 0 0.72rem 0;
  padding: 0.62rem 0.68rem;
  border-top: 3px solid var(--ov-command-tone, var(--ov-mi-color-neutral));
  border-bottom: 1px solid var(--ov-mi-border-faint);
  background: color-mix(in srgb, var(--ov-command-tone, var(--ov-mi-color-neutral)) 5%, var(--ov-mi-color-surface));
}
.ov-mm-command-head {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: var(--ov-mi-gap-md);
  align-items: start;
  margin-bottom: 0.52rem;
}
.ov-mm-command-kicker {
  color: var(--ov-command-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.12;
  text-transform: uppercase;
}
.ov-mm-command-title {
  margin-top: 0.13rem;
  color: var(--ov-mi-color-text);
  font-size: 1.04rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.18;
}
.ov-mm-command-context {
  margin-top: 0.12rem;
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.24;
  overflow-wrap: anywhere;
}
.ov-mm-command-badge {
  display: inline-flex;
  align-items: center;
  min-height: 1.38rem;
  padding: 0.14rem 0.48rem;
  border: 1px solid color-mix(in srgb, var(--ov-command-tone, var(--ov-mi-color-neutral)) 32%, transparent);
  border-radius: var(--ov-mi-radius-pill);
  background: color-mix(in srgb, var(--ov-command-tone, var(--ov-mi-color-neutral)) 8%, transparent);
  color: var(--ov-command-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
  white-space: nowrap;
}
.ov-mm-command-grid {
  display: grid;
  grid-template-columns: repeat(8, minmax(0, 1fr));
  gap: 0;
  border-top: 1px solid var(--ov-mi-border-faint);
  border-bottom: 1px solid var(--ov-mi-border-faint);
}
.ov-mm-command-item {
  min-width: 0;
  padding: 0.44rem 0.5rem;
  border-left: 1px solid var(--ov-mi-border-faint);
}
.ov-mm-command-item:first-child {
  border-left: 0;
}
.ov-mm-command-label {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.12;
}
.ov-mm-command-value {
  margin-top: 0.12rem;
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-title);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.16;
  overflow-wrap: anywhere;
}
.ov-mm-command-detail {
  margin-top: 0.1rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.16;
  overflow-wrap: anywhere;
}
.ov-mm-unified-summary {
  min-width: 0;
  margin: 0.38rem 0 0.62rem 0;
  padding: 0.62rem 0.68rem;
  border-top: 3px solid var(--ov-summary-tone, var(--ov-mi-color-neutral));
  border-bottom: 1px solid var(--ov-mi-border-faint);
  background: linear-gradient(
      90deg,
      color-mix(in srgb, var(--ov-summary-tone, var(--ov-mi-color-neutral)) 7%, var(--ov-mi-color-surface)),
      rgba(255,255,255,0.94) 42%,
      var(--ov-mi-color-surface)
    );
}
.ov-mm-unified-head {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(10rem, auto);
  gap: var(--ov-mi-gap-md);
  align-items: start;
  margin-bottom: 0.5rem;
}
.ov-mm-unified-kicker {
  color: var(--ov-summary-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.12;
  text-transform: uppercase;
}
.ov-mm-unified-title {
  margin-top: 0.12rem;
  color: var(--ov-mi-color-text);
  font-size: 1.05rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.18;
}
.ov-mm-unified-context {
  margin-top: 0.12rem;
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.24;
  overflow-wrap: anywhere;
}
.ov-mm-unified-trust {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-items: center;
  gap: 0.28rem;
  min-width: 0;
}
.ov-mm-unified-trust span,
.ov-mm-unified-trust small {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.14;
}
.ov-mm-unified-trust strong,
.ov-mm-unified-action {
  display: inline-flex;
  align-items: center;
  min-height: 1.34rem;
  padding: 0.12rem 0.46rem;
  border: 1px solid color-mix(in srgb, var(--ov-summary-tone, var(--ov-mi-color-neutral)) 32%, transparent);
  border-radius: var(--ov-mi-radius-pill);
  background: color-mix(in srgb, var(--ov-summary-tone, var(--ov-mi-color-neutral)) 8%, transparent);
  color: var(--ov-summary-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.14;
  white-space: nowrap;
}
.ov-mm-unified-grid {
  display: grid;
  grid-template-columns: minmax(9.5rem, 1.15fr) repeat(4, minmax(0, 1fr));
  gap: 0;
  border-top: 1px solid var(--ov-mi-border-faint);
  border-bottom: 1px solid var(--ov-mi-border-faint);
}
.ov-mm-unified-item {
  min-width: 0;
  padding: 0.4rem 0.52rem;
  border-left: 1px solid var(--ov-mi-border-faint);
}
.ov-mm-unified-item:first-child {
  border-left: 0;
}
.ov-mm-unified-label {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.12;
}
.ov-mm-unified-value {
  margin-top: 0.1rem;
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-body);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.15;
  overflow-wrap: anywhere;
}
.ov-mm-unified-detail {
  margin-top: 0.08rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.14;
  overflow-wrap: anywhere;
}
.ov-mm-trust {
  min-width: 0;
  margin: 0.52rem 0 0.82rem 0;
  padding: 0.56rem 0.64rem;
  border-left: 3px solid var(--ov-trust-tone, var(--ov-mi-color-neutral));
  border-top: 1px solid var(--ov-mi-border-faint);
  border-bottom: 1px solid var(--ov-mi-border-faint);
  background: color-mix(in srgb, var(--ov-trust-tone, var(--ov-mi-color-neutral)) 4%, var(--ov-mi-color-surface));
}
.ov-mm-trust-head {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: var(--ov-mi-gap-md);
  align-items: start;
  margin-bottom: 0.42rem;
}
.ov-mm-trust-kicker {
  color: var(--ov-trust-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.12;
  text-transform: uppercase;
}
.ov-mm-trust-title {
  margin-top: 0.12rem;
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-title);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.16;
}
.ov-mm-trust-detail,
.ov-mm-trust-boundary {
  margin-top: 0.12rem;
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.28;
  overflow-wrap: anywhere;
}
.ov-mm-trust-action {
  display: inline-flex;
  align-items: center;
  min-height: 1.34rem;
  padding: 0.12rem 0.46rem;
  border: 1px solid color-mix(in srgb, var(--ov-trust-tone, var(--ov-mi-color-neutral)) 30%, transparent);
  border-radius: var(--ov-mi-radius-pill);
  background: color-mix(in srgb, var(--ov-trust-tone, var(--ov-mi-color-neutral)) 7%, transparent);
  color: var(--ov-trust-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
  white-space: nowrap;
}
.ov-mm-trust-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 0;
  border-top: 1px solid var(--ov-mi-border-faint);
  border-bottom: 1px solid var(--ov-mi-border-faint);
}
.ov-mm-trust-item {
  min-width: 0;
  padding: 0.36rem 0.46rem;
  border-left: 1px solid var(--ov-mi-border-faint);
}
.ov-mm-trust-item:first-child {
  border-left: 0;
}
.ov-mm-trust-label {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.12;
}
.ov-mm-trust-value {
  margin-top: 0.1rem;
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-body);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.15;
  overflow-wrap: anywhere;
}
.ov-mm-trust-detail-small {
  margin-top: 0.08rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.14;
  overflow-wrap: anywhere;
}
.ov-mm-trust-boundary {
  padding: 0.34rem 0.4rem;
  border: 1px solid var(--ov-mi-border-faint);
  background: rgba(248,250,252,0.74);
}
.ov-mm-data-trust-strip {
  min-width: 0;
  margin: 0.48rem 0 0.72rem 0;
  padding: 0.52rem 0.58rem;
  border-left: 3px solid var(--ov-data-trust-tone, var(--ov-mi-color-neutral));
  border-top: 1px solid var(--ov-mi-border-faint);
  border-bottom: 1px solid var(--ov-mi-border-faint);
  background: color-mix(in srgb, var(--ov-data-trust-tone, var(--ov-mi-color-neutral)) 4%, var(--ov-mi-color-surface));
}
.ov-mm-data-trust-head {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: var(--ov-mi-gap-md);
  align-items: start;
}
.ov-mm-data-trust-kicker {
  color: var(--ov-data-trust-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.12;
}
.ov-mm-data-trust-title {
  margin-top: 0.08rem;
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-title);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.14;
}
.ov-mm-data-trust-detail,
.ov-mm-data-trust-boundary {
  margin-top: 0.1rem;
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.24;
  overflow-wrap: anywhere;
}
.ov-mm-data-trust-action {
  display: inline-flex;
  align-items: center;
  min-height: 1.32rem;
  padding: 0.12rem 0.46rem;
  border: 1px solid color-mix(in srgb, var(--ov-data-trust-tone, var(--ov-mi-color-neutral)) 30%, transparent);
  border-radius: var(--ov-mi-radius-pill);
  background: color-mix(in srgb, var(--ov-data-trust-tone, var(--ov-mi-color-neutral)) 7%, transparent);
  color: var(--ov-data-trust-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
  white-space: nowrap;
}
.ov-mm-data-trust-chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--ov-mi-gap-xs);
  margin-top: 0.44rem;
}
.ov-mm-data-trust-chip {
  display: inline-flex;
  align-items: baseline;
  gap: 0.24rem;
  min-height: 1.42rem;
  padding: 0.16rem 0.44rem;
  border: 1px solid var(--ov-mi-border-faint);
  border-radius: var(--ov-mi-radius-pill);
  background: rgba(255,255,255,0.72);
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.12;
}
.ov-mm-data-trust-chip strong {
  color: var(--ov-mi-color-text);
  font-weight: var(--ov-mi-weight-heading);
}
.ov-mm-data-trust-chip small {
  color: var(--ov-mi-color-text-muted);
}
.ov-mm-data-trust-boundary {
  padding: 0.3rem 0.38rem;
  border: 1px solid var(--ov-mi-border-faint);
  background: rgba(248,250,252,0.72);
}
.ov-mm-empty-state {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(12rem, 0.34fr) minmax(11rem, 0.3fr);
  gap: var(--ov-mi-gap-lg);
  align-items: center;
  margin: 0.62rem 0 0.86rem 0;
  padding: 0.72rem 0.76rem;
  border-top: 3px solid var(--ov-empty-tone, var(--ov-mi-color-neutral));
  border-bottom: 1px solid var(--ov-mi-border-faint);
  background: color-mix(in srgb, var(--ov-empty-tone, var(--ov-mi-color-neutral)) 5%, var(--ov-mi-color-surface));
}
.ov-mm-empty-kicker {
  color: var(--ov-empty-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.12;
}
.ov-mm-empty-title {
  margin-top: 0.16rem;
  color: var(--ov-mi-color-text);
  font-size: 1rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.2;
}
.ov-mm-empty-detail {
  margin-top: 0.18rem;
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-body);
  line-height: 1.36;
}
.ov-mm-empty-action {
  min-width: 0;
  padding-left: 0.75rem;
  border-left: 1px solid var(--ov-mi-border-faint);
}
.ov-mm-empty-action span {
  display: inline-flex;
  max-width: 100%;
  padding: 0.16rem 0.52rem;
  border-radius: var(--ov-mi-radius-pill);
  border: 1px solid color-mix(in srgb, var(--ov-empty-tone, var(--ov-mi-color-neutral)) 34%, transparent);
  background: color-mix(in srgb, var(--ov-empty-tone, var(--ov-mi-color-neutral)) 8%, transparent);
  color: var(--ov-empty-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
  line-height: 1.14;
}
	.ov-mm-empty-action small {
	  display: block;
	  margin-top: 0.26rem;
	  color: var(--ov-mi-color-text-muted);
	  font-size: var(--ov-mi-font-caption);
	  line-height: 1.25;
	}
.ov-mm-empty-trust {
  min-width: 0;
  padding-left: 0.75rem;
  border-left: 1px solid var(--ov-mi-border-faint);
}
.ov-mm-empty-trust span,
.ov-mm-empty-trust small {
  display: block;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.2;
}
.ov-mm-empty-trust strong {
  display: block;
  margin: 0.08rem 0;
  color: var(--ov-empty-tone, var(--ov-mi-color-neutral));
  font-size: var(--ov-mi-font-body);
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.14;
  overflow-wrap: anywhere;
}
	.ov-mm-board {
	  min-width: 0;
	  margin: 0.1rem 0 0.82rem 0;
	  padding: 0.56rem 0.62rem;
	  border-top: 1px solid var(--ov-mi-border-faint);
	  border-bottom: 1px solid var(--ov-mi-border-faint);
	  background: color-mix(in srgb, var(--ov-mi-color-primary) 3%, var(--ov-mi-color-surface));
	}
	.ov-mm-board-head {
	  display: grid;
	  grid-template-columns: minmax(0, 1fr) auto;
	  gap: var(--ov-mi-gap-md);
	  align-items: start;
	  margin-bottom: 0.48rem;
	}
	.ov-mm-board-kicker {
	  color: var(--ov-mi-color-primary);
	  font-size: var(--ov-mi-font-xs);
	  font-weight: var(--ov-mi-weight-label);
	  line-height: 1.12;
	  text-transform: uppercase;
	}
	.ov-mm-board-title {
	  margin-top: 0.12rem;
	  color: var(--ov-mi-color-text);
	  font-size: var(--ov-mi-font-title);
	  font-weight: var(--ov-mi-weight-heading);
	  line-height: 1.15;
	}
	.ov-mm-board-detail,
	.ov-mm-board-boundary {
	  margin-top: 0.12rem;
	  color: var(--ov-mi-color-text-subtle);
	  font-size: var(--ov-mi-font-caption);
	  line-height: 1.25;
	  overflow-wrap: anywhere;
	}
	.ov-mm-board-count {
	  padding: 0.12rem 0.46rem;
	  border: 1px solid var(--ov-mi-border-control);
	  border-radius: var(--ov-mi-radius-pill);
	  color: var(--ov-mi-color-text-muted);
	  font-size: var(--ov-mi-font-caption);
	  font-weight: var(--ov-mi-weight-label);
	  white-space: nowrap;
	}
	.ov-mm-tape {
	  display: grid;
	  grid-template-columns: repeat(5, minmax(0, 1fr));
	  border-top: 1px solid var(--ov-mi-border-faint);
	  border-bottom: 1px solid var(--ov-mi-border-faint);
	}
	.ov-mm-tape-cell {
	  min-width: 0;
	  padding: 0.46rem 0.48rem;
	  border-left: 1px solid var(--ov-mi-border-faint);
	  border-top: 2px solid var(--ov-tape-tone, var(--ov-mi-color-neutral));
	  background: color-mix(in srgb, var(--ov-tape-tone, var(--ov-mi-color-neutral)) 4%, transparent);
	}
	.ov-mm-tape-cell:first-child {
	  border-left: 0;
	}
	.ov-mm-tape-rank,
	.ov-mm-tape-detail {
	  color: var(--ov-mi-color-text-muted);
	  font-size: var(--ov-mi-font-xs);
	  font-weight: var(--ov-mi-weight-label);
	  line-height: 1.12;
	}
	.ov-mm-tape-symbol {
	  margin-top: 0.12rem;
	  color: var(--ov-mi-color-text);
	  font-size: var(--ov-mi-font-title);
	  font-weight: var(--ov-mi-weight-heading);
	  line-height: 1.12;
	  overflow-wrap: anywhere;
	}
	.ov-mm-tape-value {
	  margin-top: 0.08rem;
	  color: var(--ov-tape-tone, var(--ov-mi-color-neutral));
	  font-size: var(--ov-mi-font-body);
	  font-weight: var(--ov-mi-weight-heading);
	  line-height: 1.12;
	}
	.ov-mm-list {
	  display: grid;
	  gap: 0;
	  margin-top: 0.5rem;
	  border-top: 1px solid var(--ov-mi-border-faint);
	  max-height: 42rem;
	  overflow-y: auto;
	  overscroll-behavior: contain;
	}
	.ov-mm-list-row {
	  display: grid;
	  grid-template-columns: 2.6rem minmax(8rem, 1.1fr) minmax(6rem, 0.8fr) minmax(8rem, 1fr);
	  gap: var(--ov-mi-gap-sm);
	  align-items: center;
	  min-width: 0;
	  padding: 0.42rem 0.36rem;
	  border-bottom: 1px solid var(--ov-mi-border-faint);
	  border-left: 3px solid var(--ov-row-tone, var(--ov-mi-color-neutral));
	}
	.ov-mm-list-rank {
	  color: var(--ov-mi-color-text-muted);
	  font-size: var(--ov-mi-font-caption);
	  font-weight: var(--ov-mi-weight-label);
	}
	.ov-mm-list-symbol,
	.ov-mm-list-metric strong {
	  color: var(--ov-mi-color-text);
	  font-size: var(--ov-mi-font-body);
	  font-weight: var(--ov-mi-weight-heading);
	  line-height: 1.14;
	}
	.ov-mm-list-name,
	.ov-mm-list-sector,
	.ov-mm-list-secondary,
	.ov-mm-list-metric span {
	  color: var(--ov-mi-color-text-muted);
	  font-size: var(--ov-mi-font-caption);
	  line-height: 1.18;
	  overflow-wrap: anywhere;
	}
	.ov-mm-list-metric {
	  text-align: right;
	}
	.ov-mm-list-metric strong {
	  display: block;
	  color: var(--ov-row-tone, var(--ov-mi-color-neutral));
	}
	.ov-mm-board-boundary {
	  padding: 0.32rem 0.38rem;
	  border: 1px solid var(--ov-mi-border-faint);
	  background: rgba(248,250,252,0.72);
	}
	.ov-mm-chart-workspace {
	  min-width: 0;
	  margin: 0.1rem 0 0.5rem 0;
	  padding: 0.54rem 0.6rem;
	  border-top: 1px solid var(--ov-mi-border-faint);
	  border-bottom: 1px solid var(--ov-mi-border-faint);
	  background: color-mix(in srgb, var(--ov-mi-color-neutral) 4%, var(--ov-mi-color-surface));
	}
	.ov-mm-chart-head {
	  display: grid;
	  grid-template-columns: minmax(0, 1fr) auto;
	  gap: var(--ov-mi-gap-sm);
	  align-items: start;
	  margin-bottom: 0.46rem;
	}
	.ov-mm-chart-kicker {
	  color: var(--ov-mi-color-text-muted);
	  font-size: var(--ov-mi-font-xs);
	  font-weight: var(--ov-mi-weight-label);
	  line-height: 1.12;
	}
	.ov-mm-chart-title {
	  margin-top: 0.12rem;
	  color: var(--ov-mi-color-text);
	  font-size: var(--ov-mi-font-title);
	  font-weight: var(--ov-mi-weight-heading);
	  line-height: 1.15;
	}
	.ov-mm-chart-detail {
	  margin-top: 0.12rem;
	  color: var(--ov-mi-color-text-subtle);
	  font-size: var(--ov-mi-font-caption);
	  line-height: 1.24;
	  overflow-wrap: anywhere;
	}
	.ov-mm-chart-badge {
	  padding: 0.12rem 0.48rem;
	  border: 1px solid var(--ov-mi-border-control);
	  border-radius: var(--ov-mi-radius-pill);
	  color: var(--ov-mi-color-text-muted);
	  font-size: var(--ov-mi-font-caption);
	  font-weight: var(--ov-mi-weight-label);
	  white-space: nowrap;
	}
	.ov-mm-chart-facts {
	  display: grid;
	  grid-template-columns: repeat(3, minmax(0, 1fr));
	  border-top: 1px solid var(--ov-mi-border-faint);
	  border-bottom: 1px solid var(--ov-mi-border-faint);
	}
	.ov-mm-chart-fact {
	  min-width: 0;
	  padding: 0.36rem 0.42rem;
	  border-left: 1px solid var(--ov-mi-border-faint);
	}
	.ov-mm-chart-fact:first-child {
	  border-left: 0;
	}
	.ov-mm-chart-fact-label,
	.ov-mm-chart-fact-detail {
	  color: var(--ov-mi-color-text-muted);
	  font-size: var(--ov-mi-font-xs);
	  font-weight: var(--ov-mi-weight-label);
	  line-height: 1.14;
	  overflow-wrap: anywhere;
	}
	.ov-mm-chart-fact-value {
	  margin-top: 0.08rem;
	  color: var(--ov-mi-color-text);
	  font-size: var(--ov-mi-font-body);
	  font-weight: var(--ov-mi-weight-heading);
	  line-height: 1.14;
	  overflow-wrap: anywhere;
	}
	.ov-mm-investigation-pane {
	  margin: 0.42rem 0 0.72rem 0;
	  padding: 0.66rem;
	  border: 1px solid var(--ov-mi-border-faint);
	  border-left: 4px solid var(--ov-mi-color-primary);
	  border-radius: var(--ov-mi-radius-panel);
	  background:
	    linear-gradient(135deg, color-mix(in srgb, var(--ov-mi-color-primary) 5%, var(--ov-mi-color-surface)), rgba(255,255,255,0.98)),
	    var(--ov-mi-color-surface);
	}
	.ov-mm-investigation-head {
	  display: grid;
	  grid-template-columns: minmax(0, 1fr) auto;
	  gap: var(--ov-mi-gap-md);
	  align-items: start;
	  margin-bottom: 0.52rem;
	}
	.ov-mm-investigation-kicker {
	  color: var(--ov-mi-color-text-muted);
	  font-size: var(--ov-mi-font-xs);
	  font-weight: var(--ov-mi-weight-label);
	  line-height: 1.12;
	  text-transform: uppercase;
	}
	.ov-mm-investigation-title {
	  margin-top: 0.12rem;
	  color: var(--ov-mi-color-text);
	  font-size: 1.02rem;
	  font-weight: var(--ov-mi-weight-heading);
	  line-height: 1.16;
	  overflow-wrap: anywhere;
	}
	.ov-mm-investigation-subtitle,
	.ov-mm-investigation-boundary {
	  color: var(--ov-mi-color-text-subtle);
	  font-size: var(--ov-mi-font-caption);
	  line-height: 1.26;
	  overflow-wrap: anywhere;
	}
	.ov-mm-investigation-subtitle {
	  margin-top: 0.14rem;
	}
	.ov-mm-investigation-rank {
	  display: inline-flex;
	  align-items: center;
	  min-height: 1.5rem;
	  padding: 0.18rem 0.52rem;
	  border: 1px solid color-mix(in srgb, var(--ov-mi-color-primary) 32%, transparent);
	  border-radius: var(--ov-mi-radius-pill);
	  background: color-mix(in srgb, var(--ov-mi-color-primary) 8%, transparent);
	  color: var(--ov-mi-color-primary);
	  font-size: var(--ov-mi-font-caption);
	  font-weight: var(--ov-mi-weight-label);
	  line-height: 1.1;
	  white-space: nowrap;
	}
	.ov-mm-investigation-facts {
	  display: grid;
	  grid-template-columns: repeat(6, minmax(0, 1fr));
	  border-top: 1px solid var(--ov-mi-border-faint);
	  border-bottom: 1px solid var(--ov-mi-border-faint);
	}
	.ov-mm-investigation-fact {
	  min-width: 0;
	  padding: 0.42rem 0.48rem;
	  border-left: 1px solid var(--ov-mi-border-faint);
	}
	.ov-mm-investigation-fact:first-child {
	  border-left: 0;
	}
	.ov-mm-investigation-fact span,
	.ov-mm-investigation-fact small {
	  display: block;
	  color: var(--ov-mi-color-text-muted);
	  font-size: var(--ov-mi-font-xs);
	  font-weight: var(--ov-mi-weight-label);
	  line-height: 1.14;
	  overflow-wrap: anywhere;
	}
	.ov-mm-investigation-fact strong {
	  display: block;
	  margin-top: 0.1rem;
	  color: var(--ov-mi-color-text);
	  font-size: var(--ov-mi-font-body);
	  font-weight: var(--ov-mi-weight-heading);
	  line-height: 1.14;
	  overflow-wrap: anywhere;
	}
	.ov-mm-investigation-status {
	  display: flex;
	  flex-wrap: wrap;
	  gap: var(--ov-mi-gap-xs);
	  margin-top: 0.5rem;
	}
	.ov-mm-investigation-status-item {
	  display: inline-flex;
	  align-items: center;
	  min-height: 1.42rem;
	  padding: 0.14rem 0.46rem;
	  border: 1px solid color-mix(in srgb, var(--ov-status-tone, var(--ov-mi-color-neutral)) 28%, transparent);
	  border-radius: var(--ov-mi-radius-pill);
	  background: color-mix(in srgb, var(--ov-status-tone, var(--ov-mi-color-neutral)) 7%, transparent);
	  color: var(--ov-status-tone, var(--ov-mi-color-neutral));
	  font-size: var(--ov-mi-font-caption);
	  font-weight: var(--ov-mi-weight-label);
	  line-height: 1.1;
	}
	.ov-mm-investigation-boundary {
	  margin-top: 0.52rem;
	  padding: 0.4rem 0.48rem;
	  border: 1px solid var(--ov-mi-border-faint);
	  border-radius: var(--ov-mi-radius-card);
	  background: rgba(248,250,252,0.78);
	}
	.ov-mm-research-snapshot {
	  margin: 0.42rem 0 0.72rem 0;
	  padding: 0.62rem;
	  border: 1px solid var(--ov-mi-border-faint);
	  border-radius: var(--ov-mi-radius-panel);
	  background: var(--ov-mi-color-surface);
	}
	.ov-mm-research-head {
	  display: grid;
	  grid-template-columns: minmax(0, 1fr) auto;
	  gap: var(--ov-mi-gap-md);
	  align-items: start;
	  margin-bottom: 0.48rem;
	}
	.ov-mm-research-kicker {
	  color: var(--ov-mi-color-text-muted);
	  font-size: var(--ov-mi-font-xs);
	  font-weight: var(--ov-mi-weight-label);
	  line-height: 1.12;
	  text-transform: uppercase;
	}
	.ov-mm-research-title {
	  margin-top: 0.1rem;
	  color: var(--ov-mi-color-text);
	  font-size: var(--ov-mi-font-title);
	  font-weight: var(--ov-mi-weight-heading);
	  line-height: 1.14;
	}
	.ov-mm-research-subtitle,
	.ov-mm-research-detail,
	.ov-mm-research-boundary {
	  color: var(--ov-mi-color-text-subtle);
	  font-size: var(--ov-mi-font-caption);
	  line-height: 1.24;
	  overflow-wrap: anywhere;
	}
	.ov-mm-research-subtitle {
	  margin-top: 0.12rem;
	}
	.ov-mm-research-asof {
	  display: inline-flex;
	  align-items: center;
	  min-height: 1.42rem;
	  padding: 0.14rem 0.46rem;
	  border: 1px solid var(--ov-mi-border-control);
	  border-radius: var(--ov-mi-radius-pill);
	  background: var(--ov-mi-fill-control);
	  color: var(--ov-mi-color-text-subtle);
	  font-size: var(--ov-mi-font-caption);
	  font-weight: var(--ov-mi-weight-label);
	  line-height: 1.1;
	  white-space: nowrap;
	}
		.ov-mm-research-grid {
		  display: grid;
		  grid-template-columns: repeat(6, minmax(0, 1fr));
		  border-top: 1px solid var(--ov-mi-border-faint);
		  border-bottom: 1px solid var(--ov-mi-border-faint);
		}
	.ov-mm-research-item {
	  min-width: 0;
	  padding: 0.46rem 0.52rem;
	  border-left: 1px solid var(--ov-mi-border-faint);
		  border-top: 3px solid color-mix(in srgb, var(--ov-research-tone, var(--ov-mi-color-neutral)) 78%, transparent);
		  background: rgba(248,250,252,0.58);
		}
		.ov-mm-research-item.has-rows {
		  grid-column: span 2;
		}
		.ov-mm-research-item:first-child {
		  border-left: 0;
		}
	.ov-mm-research-item.is-unavailable {
	  border-top-color: color-mix(in srgb, var(--ov-mi-color-neutral) 38%, transparent);
	  background: rgba(248,250,252,0.34);
	}
	.ov-mm-research-label {
	  color: var(--ov-mi-color-text-muted);
	  font-size: var(--ov-mi-font-xs);
	  font-weight: var(--ov-mi-weight-label);
	  line-height: 1.12;
	  overflow-wrap: anywhere;
	}
	.ov-mm-research-value {
	  margin-top: 0.12rem;
	  color: var(--ov-mi-color-text);
	  font-size: var(--ov-mi-font-body);
	  font-weight: var(--ov-mi-weight-heading);
	  line-height: 1.14;
	  overflow-wrap: anywhere;
	}
		.ov-mm-research-item.is-unavailable .ov-mm-research-value {
		  color: var(--ov-mi-color-text-muted);
		}
		.ov-mm-research-table {
		  min-width: 0;
		  margin-top: 0.36rem;
		  border-top: 1px solid var(--ov-mi-border-faint);
		  border-bottom: 1px solid var(--ov-mi-border-faint);
		}
		.ov-mm-research-table-row {
		  display: grid;
		  grid-template-columns: minmax(2.8rem, 0.62fr) minmax(5.2rem, 1fr) minmax(3.6rem, 0.76fr) minmax(3.6rem, 0.76fr);
		  gap: var(--ov-mi-gap-sm);
		  align-items: baseline;
		  min-width: 0;
		  padding: 0.28rem 0;
		  border-top: 1px solid var(--ov-mi-border-faint);
		  color: var(--ov-mi-color-text);
		  font-size: var(--ov-mi-font-caption);
		  line-height: 1.16;
		}
		.ov-mm-research-table-row:first-child {
		  border-top: 0;
		}
		.ov-mm-research-table-row.is-head {
		  color: var(--ov-mi-color-text-muted);
		  font-size: var(--ov-mi-font-xs);
		  font-weight: var(--ov-mi-weight-label);
		}
		.ov-mm-research-table-row > span,
		.ov-mm-research-table-row > strong {
		  min-width: 0;
		  overflow-wrap: anywhere;
		}
		.ov-mm-research-table-row > strong {
		  color: var(--ov-mi-color-text);
		  font-weight: var(--ov-mi-weight-heading);
		}
		.ov-mm-research-detail {
		  margin-top: 0.18rem;
		}
	.ov-mm-research-boundary {
	  margin-top: 0.48rem;
	  padding: 0.38rem 0.46rem;
	  border: 1px solid var(--ov-mi-border-faint);
	  border-radius: var(--ov-mi-radius-card);
	  background: rgba(248,250,252,0.74);
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
	  .ov-mm-command-head,
	  .ov-mm-unified-head,
	  .ov-mm-trust-head,
	  .ov-mm-data-trust-head,
	  .ov-mm-empty-state,
	  .ov-mm-board-head,
	  .ov-mm-chart-head,
	  .ov-mm-investigation-head,
	  .ov-mm-research-head {
	    grid-template-columns: 1fr;
	  }
	  .ov-mm-command-grid,
	  .ov-mm-unified-grid,
	  .ov-mm-trust-grid {
	    grid-template-columns: repeat(2, minmax(0, 1fr));
	  }
	  .ov-mm-unified-trust {
	    justify-content: flex-start;
	  }
	  .ov-mm-tape {
	    grid-template-columns: repeat(2, minmax(0, 1fr));
	  }
	  .ov-mm-tape-cell:nth-child(odd) {
	    border-left: 0;
	  }
	  .ov-mm-list-row {
	    grid-template-columns: 2.4rem minmax(0, 1fr);
	  }
	  .ov-mm-chart-facts {
	    grid-template-columns: 1fr;
	  }
	  .ov-mm-investigation-facts {
	    grid-template-columns: repeat(2, minmax(0, 1fr));
	  }
		  .ov-mm-research-grid {
		    grid-template-columns: 1fr;
		  }
		  .ov-mm-research-item.has-rows {
		    grid-column: span 1;
		  }
	  .ov-mm-chart-fact,
	  .ov-mm-research-item,
	  .ov-mm-chart-fact:first-child {
	    border-left: 0;
	    border-top: 1px solid var(--ov-mi-border-faint);
	  }
	  .ov-mm-research-item:first-child,
	  .ov-mm-chart-fact:first-child {
	    border-top: 0;
	  }
	  .ov-mm-investigation-fact:nth-child(odd) {
	    border-left: 0;
	  }
	  .ov-mm-list-sector,
	  .ov-mm-list-metric {
	    grid-column: 2;
	    text-align: left;
	  }
  .ov-mm-command-item:nth-child(odd),
  .ov-mm-unified-item:nth-child(odd),
  .ov-mm-trust-item:nth-child(odd) {
    border-left: 0;
  }
  .ov-mm-empty-action {
    padding-left: 0;
    padding-top: 0.48rem;
    border-left: 0;
    border-top: 1px solid var(--ov-mi-border-faint);
  }
  .ov-mm-empty-trust {
    padding-left: 0;
    padding-top: 0.48rem;
    border-left: 0;
    border-top: 1px solid var(--ov-mi-border-faint);
  }
  .ov-market-session {
    grid-template-columns: 1fr;
  }
  .ov-market-session-item {
    border-left: 0;
    border-top: 1px solid var(--ov-mi-border-faint);
  }
  .ov-macro-cockpit-head,
  .ov-macro-cockpit-next,
  .ov-ia-closeout-head,
  .ov-data-handoff-head,
  .ov-breadth-head,
  .ov-sector-breadth-head,
  .ov-macro-week-head {
    grid-template-columns: 1fr;
  }
  .ov-macro-cockpit-rail {
    grid-template-columns: 1fr;
  }
  .ov-macro-hybrid-tape,
  .ov-macro-visual-board,
  .ov-sector-pressure-map {
    grid-template-columns: 1fr;
  }
  .ov-macro-tape-cell,
  .ov-macro-tape-cell:first-child {
    border-left: 0;
    border-top: 1px solid var(--ov-mi-border-faint);
  }
  .ov-macro-tape-cell:first-child {
    border-top: 0;
  }
  .ov-macro-status-item,
  .ov-macro-cue-row,
  .ov-market-brief-row,
  .ov-context-finding-row,
  .ov-source-confidence-row,
  .ov-source-ledger-head,
  .ov-refresh-status-row,
  .ov-event-timeline-row {
    grid-template-columns: 1fr;
    gap: var(--ov-mi-gap-xs);
  }
  .ov-source-status-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .ov-refresh-status-head {
    display: block;
  }
  .ov-refresh-status-badge {
    display: block;
    margin-top: 0.2rem;
  }
  .ov-market-brief-head {
    display: block;
  }
  .ov-market-brief-note {
    margin-top: 0.16rem;
    text-align: left;
  }
  .ov-analog-summary-strip,
  .ov-analog-basis-ledger,
  .ov-analog-basis-bar {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .ov-analog-method-grid,
  .ov-analog-interpretation {
    grid-template-columns: 1fr;
  }
  .ov-analog-outcome-head {
    display: block;
  }
  .ov-analog-outcome-note {
    margin-top: 0.14rem;
    text-align: left;
  }
  .ov-analog-matrix-grid {
    overflow-x: auto;
  }
  .ov-analog-matrix-header,
  .ov-analog-matrix-row {
    min-width: 42rem;
  }
  .ov-analog-support-list {
    grid-template-columns: 1fr;
  }
  .ov-analog-support-item {
    border-left: 0;
    border-top: 1px solid var(--ov-mi-border-faint);
  }
  .ov-analog-support-item:first-child {
    border-top: 0;
  }
  .ov-macro-conditioned-stats,
  .ov-macro-sample-flow,
  .ov-macro-backdrop-grid,
  .ov-macro-sample-funnel,
  .ov-macro-funnel-track,
  .ov-macro-comparison-grid,
  .ov-macro-compare-lanes,
  .ov-macro-conditioned-condition-list,
  .ov-macro-dimension-grid,
  .ov-macro-dimension-group-list {
    grid-template-columns: 1fr;
  }
  .ov-macro-dimension-head {
    display: block;
  }
  .ov-macro-delta-row {
    grid-template-columns: 1fr;
  }
  .ov-macro-delta-value {
    text-align: left;
  }
  .ov-macro-dimension-status {
    margin-top: 0.16rem;
  }
  .ov-analog-summary-item:nth-child(odd) {
    border-left: 0;
  }
  .ov-analog-basis-group:nth-child(odd) {
    border-left: 0;
  }
  .ov-analog-basis-cell:nth-child(odd),
  .ov-analog-method-step,
  .ov-analog-insight {
    border-left: 0;
  }
  .ov-event-timeline-status {
    text-align: left;
  }
  .ov-macro-week-section-head {
    display: block;
  }
  .ov-macro-week-section-note {
    margin-top: 0.12rem;
    text-align: left;
  }
  .ov-ia-closeout-grid,
  .ov-data-handoff-grid,
  .ov-breadth-card-grid,
  .ov-breadth-row-grid,
  .ov-sector-breadth-stats,
  .ov-sector-breadth-lanes,
  .ov-sector-breadth-leader-strip,
  .ov-macro-week-items {
    grid-template-columns: 1fr;
  }
  .ov-sector-breadth-stat,
  .ov-sector-breadth-stat:first-child {
    border-left: 0;
    border-top: 1px solid var(--ov-mi-border-faint);
  }
  .ov-sector-breadth-stat:first-child {
    border-top: 0;
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
  .ov-futures-command {
    grid-template-columns: 1fr;
  }
  .ov-futures-workbench-bar,
  .ov-futures-watch-strip,
  .ov-futures-brief,
  .ov-futures-week-lanes,
  .ov-futures-refresh-sources,
  .ov-futures-evidence-grid,
  .ov-futures-validation-metrics,
  .ov-futures-data-management-grid {
    grid-template-columns: 1fr;
  }
  .ov-futures-refresh-head,
  .ov-futures-validation-head {
    align-items: flex-start;
    flex-direction: column;
  }
  .ov-futures-validation-occurrence {
    min-width: 0;
    text-align: left;
    width: 100%;
  }
  .ov-futures-watch-list {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .ov-futures-watch-head {
    padding-right: 0;
  }
  .ov-futures-workbench-item,
  .ov-futures-workbench-item:first-child {
    border-left: 0;
    border-top: 1px solid var(--ov-mi-border-faint);
  }
  .ov-futures-workbench-item:first-child {
    border-top: 3px solid color-mix(in srgb, var(--ov-workbench-tone, var(--ov-mi-color-neutral)) 72%, transparent);
  }
  .ov-futures-brief-support {
    grid-template-columns: 1fr;
  }
  .ov-futures-week-flow-head {
    flex-direction: column;
  }
  .ov-futures-week-driver {
    white-space: normal;
  }
  .ov-futures-week-lane-item {
    grid-template-columns: 1fr;
    gap: 0.18rem;
  }
  .ov-futures-command-cell,
  .ov-futures-command-cell:first-child {
    border-left: 0;
    border-top: 1px solid var(--ov-mi-border-faint);
  }
  .ov-futures-command-cell:first-child {
    border-top: 0;
  }
  .ov-futures-symbol-head,
  .ov-futures-section-head {
    align-items: flex-start;
    flex-direction: column;
  }
  .ov-futures-symbol-meta {
    text-align: left;
  }
  .ov-futures-live-strip,
  .ov-futures-macro-strip,
  .ov-futures-week-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .ov-futures-chart-head {
    flex-direction: column;
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

__all__ = [
    "OVERVIEW_COLOR_POSITIVE",
    "OVERVIEW_COLOR_PRIMARY",
    "OVERVIEW_COLOR_WARNING",
    "OVERVIEW_COLOR_DANGER",
    "OVERVIEW_COLOR_DANGER_DARK",
    "OVERVIEW_COLOR_NEUTRAL",
    "OVERVIEW_COLOR_TEXT",
    "OVERVIEW_COLOR_TEXT_SUBTLE",
    "OVERVIEW_COLOR_TEXT_MUTED",
    "OVERVIEW_COLOR_TEXT_INVERSE",
    "OVERVIEW_COLOR_SURFACE",
    "OVERVIEW_COLOR_SURFACE_SUBTLE",
    "OVERVIEW_COLOR_SURFACE_ALT",
    "OVERVIEW_COLOR_BORDER",
    "OVERVIEW_COLOR_PURPLE",
    "OVERVIEW_COLOR_CYAN",
    "OVERVIEW_COLOR_LIME",
    "OVERVIEW_COLOR_SOFT",
    "OVERVIEW_DIVERGING_RANGE",
    "OVERVIEW_SERIES_COLORS",
    "OVERVIEW_SECTOR_COLOR_MAP",
    "_CSS_TOKENS",
    "_css_token_block",
    "_style_token_block",
    "_display_value",
    "_display_status_label",
    "_display_freshness_label",
    "overview_ui_css",
    "market_movers_ui_css",
    "render_overview_toolbar_label",
    "render_market_movers_toolbar_label",
    "render_overview_meta_strip",
    "render_market_snapshot_meta_strip",
    "_overview_tone_color",
    "_badge_html",
]
