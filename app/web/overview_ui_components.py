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
  .ov-macro-cockpit-head,
  .ov-macro-cockpit-next,
  .ov-ia-closeout-head,
  .ov-data-handoff-head,
  .ov-breadth-head,
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
  .ov-macro-week-items {
    grid-template-columns: 1fr;
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


def _macro_cockpit_badges_html(badges: list[dict[str, Any]]) -> str:
    html: list[str] = []
    for badge in badges[:4]:
        tone = escape(_overview_tone_color(badge.get("tone")))
        label = _display_value(badge.get("label"))
        value = _display_value(badge.get("value"))
        html.append(
            f'<span class="ov-macro-cockpit-badge" style="--ov-badge-tone:{tone};">'
            f"{escape(label)}: {escape(value)}"
            "</span>"
        )
    return "".join(html)


def _macro_cockpit_rail_html(items: list[dict[str, Any]]) -> str:
    if not items:
        return ""
    html: list[str] = []
    for item in items[:3]:
        tone_color = escape(_overview_tone_color(item.get("tone")))
        html.append(
            f'<div class="ov-macro-status-item" style="--ov-rail-tone:{tone_color};">'
            f'<div class="ov-macro-status-label">{escape(_display_value(item.get("label")))}</div>'
            f'<div class="ov-macro-status-value">{escape(_display_value(item.get("value")))}</div>'
            f'<div class="ov-macro-status-detail">{escape(_display_value(item.get("detail")))}</div>'
            "</div>"
        )
    return f'<div class="ov-macro-cockpit-rail">{"".join(html)}</div>'


def _macro_hybrid_tape_html(items: list[dict[str, Any]]) -> str:
    if not items:
        return ""
    html: list[str] = []
    for item in items[:5]:
        tone_color = escape(_overview_tone_color(item.get("tone")))
        html.append(
            f'<div class="ov-macro-tape-cell" style="--ov-tape-tone:{tone_color};">'
            f'<div class="ov-macro-tape-label">{escape(_display_value(item.get("label")))}</div>'
            f'<div class="ov-macro-tape-value">{escape(_display_value(item.get("value")))}</div>'
            f'<div class="ov-macro-tape-detail">{escape(_display_value(item.get("detail")))}</div>'
            "</div>"
        )
    return f'<div class="ov-macro-cockpit-rail ov-macro-hybrid-tape">{"".join(html)}</div>'


def _macro_cockpit_row_meta_html(row: dict[str, Any]) -> str:
    target = _display_value(row.get("target_tab") or row.get("source"))
    freshness = _display_value(row.get("freshness_label") or _display_freshness_label(row.get("freshness")))
    status = _display_value(row.get("status_label") or _display_status_label(row.get("status")))
    return (
        '<div class="ov-macro-cockpit-row-meta">'
        f"<span>근거 화면: {escape(target)}</span>"
        f"<span>자료 기준: {escape(freshness)}</span>"
        f"<span>{escape(status)}</span>"
        "</div>"
    )


def _signed_pct(value: Any, *, digits: int = 1) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "-"
    return f"{numeric:+.{digits}f}%"


def _sector_pressure_map_html(model: dict[str, Any]) -> str:
    rows = list(model.get("heatmap_rows") or [])
    if not rows:
        return ""
    tiles: list[str] = []
    for row in rows:
        tone_color = escape(_overview_tone_color(row.get("tone")))
        group = _display_value(row.get("group"))
        weighted = _signed_pct(row.get("market_cap_weighted_return_pct"), digits=2)
        positive = row.get("positive_symbol_share_pct")
        try:
            positive_label = "-" if positive in (None, "") else f"{float(positive):.0f}% positive"
        except (TypeError, ValueError):
            positive_label = _display_value(positive)
        symbols = _display_value(row.get("symbols"))
        detail = f"{positive_label} · {symbols} symbols"
        tiles.append(
            f'<div class="ov-sector-pressure-tile" style="--ov-pressure-tone:{tone_color};">'
            f'<div class="ov-sector-pressure-name">{escape(group)}</div>'
            f'<div class="ov-sector-pressure-value">{escape(weighted)}</div>'
            f'<div class="ov-sector-pressure-detail">{escape(detail)}</div>'
            "</div>"
        )
    summary = dict(model.get("summary") or {})
    coverage = dict(model.get("coverage") or {})
    freshness = _display_value(coverage.get("freshness") or "-")
    return (
        '<section class="ov-sector-pressure">'
        '<div class="ov-macro-section-head">'
        '<div>'
        '<div class="ov-macro-section-title">섹터 압력 지도</div>'
        f'<div class="ov-macro-section-note">{escape(_display_value(summary.get("headline")))} · 자료 기준 {escape(freshness)}</div>'
        "</div>"
        "</div>"
        f'<div class="ov-sector-pressure-map">{"".join(tiles)}</div>'
        "</section>"
    )


def _event_timeline_day_label(value: Any) -> str:
    try:
        days = int(float(value))
    except (TypeError, ValueError):
        return "D?"
    if days < 0:
        return f"D{days}"
    if days == 0:
        return "D0"
    return f"D+{days}"


def _event_timeline_html(model: dict[str, Any]) -> str:
    items = list(model.get("items") or [])
    if not items:
        return ""
    rows: list[str] = []
    for item in items[:5]:
        tone_color = escape(_overview_tone_color(item.get("tone")))
        cluster = _display_value(item.get("cluster") or item.get("type"))
        day_label = _event_timeline_day_label(item.get("days_until"))
        detail_parts = [
            cluster,
            _display_value(item.get("freshness")),
            _display_value(item.get("quality_action")),
        ]
        detail = " · ".join(part for part in detail_parts if part and part != "-")
        rows.append(
            f'<div class="ov-event-timeline-row" style="--ov-event-tone:{tone_color};">'
            f'<div class="ov-event-timeline-day">{escape(day_label)}</div>'
            "<div>"
            f'<div class="ov-event-timeline-title">{escape(_display_value(item.get("title")))}</div>'
            f'<div class="ov-event-timeline-detail">{escape(detail)}</div>'
            "</div>"
            f'<div class="ov-event-timeline-status">{escape(cluster)}</div>'
            "</div>"
        )
    coverage = dict(model.get("coverage") or {})
    review_count = _display_value(coverage.get("review_count") or 0)
    latest = _display_value(coverage.get("latest_collected_at") or "-")
    return (
        '<section class="ov-event-timeline-panel">'
        '<div class="ov-macro-section-head">'
        '<div>'
        '<div class="ov-macro-section-title">이벤트 타임라인</div>'
        f'<div class="ov-macro-section-note">확인 필요 {escape(review_count)}개 · 자료 기준 {escape(latest)}</div>'
        "</div>"
        "</div>"
        f'<div class="ov-event-timeline">{"".join(rows)}</div>'
        "</section>"
    )


def _macro_cockpit_visual_board_html(model: dict[str, Any]) -> str:
    sector_html = _sector_pressure_map_html(dict(model.get("sector_pressure") or {}))
    timeline_html = _event_timeline_html(dict(model.get("event_timeline") or {}))
    if not (sector_html or timeline_html):
        return ""
    return f'<section class="ov-macro-visual-board">{sector_html}{timeline_html}</section>'


def _macro_cockpit_brief_rows_html(
    rows: list[dict[str, Any]],
    *,
    market_session: dict[str, Any] | None = None,
) -> str:
    if not rows:
        return ""
    session = dict(market_session or {})
    title = _display_value(session.get("brief_title") or "오늘의 시장 브리프")
    subtitle = _display_value(session.get("brief_subtitle"))
    note_html = (
        f'<div class="ov-market-brief-note">{escape(subtitle)}</div>'
        if subtitle != "-"
        else ""
    )
    html: list[str] = []
    for index, row in enumerate(rows[:4], start=1):
        tone_color = escape(_overview_tone_color(row.get("tone")))
        badges = _macro_cockpit_badges_html(list(row.get("badges") or []))
        html.append(
            f'<li class="ov-market-brief-row" style="--ov-row-tone:{tone_color};">'
            f'<div class="ov-market-brief-step">{index}</div>'
            "<div>"
            f'<div class="ov-market-brief-label">{escape(_display_value(row.get("label")))}</div>'
            f'<div class="ov-market-brief-value">{escape(_display_value(row.get("value")))}</div>'
            "</div>"
            "<div>"
            f'<div class="ov-market-brief-detail">{escape(_display_value(row.get("detail")))}</div>'
            f'<div class="ov-macro-cockpit-badges">{badges}</div>'
            f'{_macro_cockpit_row_meta_html(row)}'
            "</div>"
            "</li>"
        )
    return (
        '<section class="ov-market-brief-lane">'
        '<div class="ov-market-brief-head">'
        f'<div class="ov-market-brief-title">{escape(title)}</div>'
        f"{note_html}"
        "</div>"
        f'<ol class="ov-market-brief-list">{"".join(html)}</ol>'
        "</section>"
    )


def _macro_cockpit_next_checks_html(checks: list[dict[str, Any]]) -> str:
    if not checks:
        return ""
    html: list[str] = []
    for check in checks[:4]:
        tone_color = escape(_overview_tone_color(check.get("tone")))
        status_label = _display_value(
            check.get("priority")
            or check.get("status_label")
            or _display_status_label(check.get("status"))
        )
        source_area = _display_value(check.get("source_area"))
        evidence = _display_value(check.get("evidence") or check.get("reason") or check.get("detail"))
        freshness = _display_value(check.get("freshness"))
        meta_parts = []
        if source_area != "-":
            meta_parts.append(f"자료 영역: {source_area}")
        if freshness != "-":
            meta_parts.append(f"자료 기준: {freshness}")
        repair_hint = _display_value(check.get("repair_hint"))
        if repair_hint != "-":
            meta_parts.append(f"보강: {repair_hint}")
        meta_html = " · ".join(meta_parts)
        html.append(
            f'<li class="ov-context-finding-row" style="--ov-check-tone:{tone_color};">'
            "<div>"
            f'<div class="ov-context-finding-priority">{escape(status_label)}</div>'
            f'<div class="ov-context-finding-label">{escape(_display_value(check.get("label") or check.get("target_tab")))}</div>'
            "</div>"
            "<div>"
            '<div class="ov-context-finding-kicker">결론</div>'
            f'<div class="ov-context-finding-conclusion">{escape(_display_value(check.get("conclusion") or check.get("title") or check.get("value")))}</div>'
            "</div>"
            "<div>"
            '<div class="ov-context-finding-kicker">해석 영향</div>'
            f'<div class="ov-context-finding-detail">{escape(_display_value(check.get("interpretation") or check.get("detail")))}</div>'
            "</div>"
            "<div>"
            '<div class="ov-context-finding-kicker">자료 기준</div>'
            f'<div class="ov-context-finding-evidence">{escape(evidence)}</div>'
            f'<div class="ov-context-finding-meta">{escape(meta_html)}</div>'
            "</div>"
            "</li>"
        )
    return (
        '<section class="ov-macro-reading-section ov-macro-cues" style="--ov-reading-tone:var(--ov-mi-color-warning);">'
        '<div class="ov-macro-section-head">'
        '<div class="ov-macro-section-title">추가 근거 메모</div>'
        '<div class="ov-macro-section-note">기본 시장 브리프에 흡수하지 않은 보조 근거가 있을 때만 분리해 표시합니다.</div>'
        "</div>"
        f'<ol class="ov-context-finding-rail">{"".join(html)}</ol>'
        "</section>"
    )


def _macro_cockpit_interpretation_cues_html(cues: list[dict[str, Any]]) -> str:
    return _macro_cockpit_next_checks_html(cues)


def _analog_pct(value: Any) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "-"
    return f"{numeric:+.1f}%"


def _analog_delta_pct(value: Any) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "-"
    return f"{numeric:+.1f}%p"


def _analog_cell_strength(value: Any) -> str:
    try:
        numeric = abs(float(value))
    except (TypeError, ValueError):
        return "0.0%"
    if numeric <= 0:
        return "0.0%"
    strength = min(20.0, 4.0 + numeric * 2.0)
    return f"{strength:.1f}%"


def _analog_row_asset(row: dict[str, Any]) -> str:
    return str(row.get("asset") or "").strip().upper()


def _analog_row_horizon(row: dict[str, Any]) -> str:
    return str(row.get("horizon") or "").strip().upper()


def _analog_table_row_html(row: dict[str, Any]) -> str:
    return (
        "<tr>"
        f"<td>{escape(_display_value(row.get('asset')))} · {escape(_display_value(row.get('horizon')))}</td>"
        f"<td>{escape(_analog_pct(row.get('median_return_pct')))}</td>"
        f"<td>{escape(_analog_pct(row.get('positive_rate_pct')))}</td>"
        f"<td>{escape(_analog_pct(row.get('best_return_pct')))}</td>"
        f"<td>{escape(_analog_pct(row.get('worst_return_pct')))}</td>"
        f"<td>{escape(_display_value(row.get('sample_count')))}</td>"
        "</tr>"
    )


def _analog_table_block_html(
    rows: list[dict[str, Any]],
    *,
    title: str,
    note: str,
    secondary: bool = False,
) -> str:
    if not rows:
        return ""
    row_html = "".join(_analog_table_row_html(row) for row in rows)
    block_class = "ov-historical-analog-table-block"
    if secondary:
        block_class += " is-secondary"
    return (
        f'<div class="{block_class}">'
        f'<div class="ov-historical-analog-table-title">{escape(title)}</div>'
        f'<div class="ov-historical-analog-table-note">{escape(note)}</div>'
        '<table class="ov-historical-analog-table">'
        "<thead><tr><th>자산 · 기간</th><th>중간값</th><th>상승 비율</th><th>최선</th><th>최악</th><th>표본</th></tr></thead>"
        f"<tbody>{row_html}</tbody>"
        "</table>"
        "</div>"
    )


def _analog_find_reference_row(rows: list[dict[str, Any]], proxy_etf: str) -> dict[str, Any]:
    proxy = proxy_etf.strip().upper()
    for horizon in ("20D", "5D", "60D"):
        for row in rows:
            if _analog_row_asset(row) == proxy and _analog_row_horizon(row) == horizon:
                return row
    return rows[0] if rows else {}


def _analog_find_asset_horizon_row(rows: list[dict[str, Any]], asset: str, horizon: str) -> dict[str, Any]:
    normalized_asset = asset.strip().upper()
    normalized_horizon = horizon.strip().upper()
    for row in rows:
        if _analog_row_asset(row) == normalized_asset and _analog_row_horizon(row) == normalized_horizon:
            return row
    return {}


def _analog_summary_strip_html(model: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    proxy_etf = _display_value(model.get("proxy_etf"))
    reference = _analog_find_reference_row(rows, str(model.get("proxy_etf") or ""))
    reference_horizon = _display_value(reference.get("horizon") or "20D")
    spy_reference = _analog_find_asset_horizon_row(rows, "SPY", str(reference.get("horizon") or "20D"))
    qqq_reference = _analog_find_asset_horizon_row(rows, "QQQ", str(reference.get("horizon") or "20D"))
    comparison = spy_reference or qqq_reference
    comparison_asset = _display_value(comparison.get("asset") or "SPY")
    comparison_value = _analog_pct(comparison.get("median_return_pct")) if comparison else "-"
    metrics = [
        (
            f"{proxy_etf} {reference_horizon} 중간값",
            _analog_pct(reference.get("median_return_pct")),
            "유사 구간 이후 해당 기간 중앙 경로",
        ),
        (
            "상승 비율",
            _analog_pct(reference.get("positive_rate_pct")),
            "같은 표본에서 양수였던 비율",
        ),
        ("최악", _analog_pct(reference.get("worst_return_pct")), "같은 표본 안의 가장 나쁜 경로"),
        (
            "시장 기준 비교",
            f"{comparison_asset} {comparison_value}",
            f"같은 표본의 {reference_horizon} 중앙 경로",
        ),
    ]
    metric_html = "".join(
        '<div class="ov-analog-summary-item">'
        f'<div class="ov-analog-summary-label">{escape(label)}</div>'
        f'<div class="ov-analog-summary-value">{escape(value)}</div>'
        f'<div class="ov-analog-summary-detail">{escape(detail)}</div>'
        "</div>"
        for label, value, detail in metrics
    )
    return f'<div class="ov-analog-summary-strip">{metric_html}</div>'


def _analog_outcome_matrix_html(rows: list[dict[str, Any]], *, title: str, note: str) -> str:
    if not rows:
        return ""
    asset_order = list(dict.fromkeys(_analog_row_asset(row) for row in rows if _analog_row_asset(row)))
    horizon_order = [
        horizon
        for horizon in ("5D", "20D", "60D", "1M")
        if any(_analog_row_horizon(row) == horizon for row in rows)
    ]
    if not horizon_order:
        horizon_order = list(dict.fromkeys(_analog_row_horizon(row) for row in rows if _analog_row_horizon(row)))
    header_html = "".join(f'<div class="ov-analog-matrix-heading">{escape(horizon)}</div>' for horizon in horizon_order)
    row_html: list[str] = []
    for asset in asset_order:
        cells: list[str] = []
        for horizon in horizon_order:
            row = _analog_find_asset_horizon_row(rows, asset, horizon)
            if not row:
                cells.append('<div class="ov-analog-matrix-cell is-empty">-</div>')
                continue
            median = row.get("median_return_pct")
            try:
                median_value = float(median)
            except (TypeError, ValueError):
                median_value = 0.0
            tone_class = "is-positive" if median_value > 0 else "is-negative" if median_value < 0 else "is-flat"
            strength = _analog_cell_strength(median)
            gradient_class = "has-return-gradient" if tone_class in {"is-positive", "is-negative"} else ""
            cells.append(
                f'<div class="ov-analog-matrix-cell {gradient_class} {tone_class}" style="--ov-analog-cell-strength:{escape(strength)};">'
                f'<div class="ov-analog-matrix-cell-label">{escape(asset)} · {escape(horizon)}</div>'
                f'<strong>{escape(_analog_pct(row.get("median_return_pct")))}</strong>'
                f'<span>상승 {escape(_analog_pct(row.get("positive_rate_pct")))}</span>'
                f'<small>최악 {escape(_analog_pct(row.get("worst_return_pct")))}</small>'
                "</div>"
            )
        row_html.append(
            '<div class="ov-analog-matrix-row">'
            f'<div class="ov-analog-matrix-asset">{escape(asset)}</div>'
            f'{"".join(cells)}'
            "</div>"
        )
    return (
        '<div class="ov-analog-outcome-matrix">'
        '<div class="ov-analog-outcome-head">'
        f'<div class="ov-analog-outcome-title">{escape(title)}</div>'
        f'<div class="ov-analog-outcome-note">{escape(note)}</div>'
        "</div>"
        f'<div class="ov-analog-matrix-grid" style="--ov-analog-horizon-count:{len(horizon_order)};">'
        f'<div class="ov-analog-matrix-header"><div></div>{header_html}</div>'
        f'{"".join(row_html)}'
        "</div>"
        '<div class="ov-analog-matrix-legend">색상은 중간값 방향과 크기 기준</div>'
        "</div>"
    )


def _analog_support_summary_html(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    asset_order = list(dict.fromkeys(_analog_row_asset(row) for row in rows if _analog_row_asset(row)))
    items: list[str] = []
    for asset in asset_order[:6]:
        reference = (
            _analog_find_asset_horizon_row(rows, asset, "20D")
            or _analog_find_asset_horizon_row(rows, asset, "60D")
            or _analog_find_asset_horizon_row(rows, asset, "5D")
        )
        if not reference:
            continue
        horizon = _display_value(reference.get("horizon"))
        items.append(
            '<div class="ov-analog-support-item">'
            f'<div class="ov-analog-support-label">{escape(asset)} · {escape(horizon)}</div>'
            f'<div class="ov-analog-support-value">{escape(_analog_pct(reference.get("median_return_pct")))} median</div>'
            f'<div class="ov-analog-support-detail">상승 {escape(_analog_pct(reference.get("positive_rate_pct")))} · 최악 {escape(_analog_pct(reference.get("worst_return_pct")))}</div>'
            "</div>"
        )
    if not items:
        return ""
    return (
        '<div class="ov-analog-support-summary">'
        '<div class="ov-analog-support-head">'
        '<div class="ov-analog-support-title">시장 배경 요약</div>'
        '<div class="ov-analog-support-note">채권, 금, 중소형주, 크레딧 등은 리더십 판단의 보조 배경으로 낮춰 봅니다.</div>'
        "</div>"
        f'<div class="ov-analog-support-list">{"".join(items)}</div>'
        "</div>"
    )


def _analog_detail_tables_html(primary_rows: list[dict[str, Any]], support_rows: list[dict[str, Any]]) -> str:
    table_html = (
        f"{_analog_table_block_html(primary_rows, title='비교 자산 원본 통계', note='위 matrix에 사용한 원본 분포입니다.')}"
        f"{_analog_table_block_html(support_rows, title='그 밖의 자산 원본 통계', note='기본 흐름에서는 낮춘 보조 자산 분포입니다.', secondary=True)}"
    )
    if not table_html:
        return ""
    return (
        '<details class="ov-analog-detail-tables">'
        "<summary>상세 통계</summary>"
        f"{table_html}"
        "</details>"
    )


def _analog_interpretation_html(model: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    proxy_etf = _display_value(model.get("proxy_etf"))
    reference = _analog_find_reference_row(rows, str(model.get("proxy_etf") or ""))
    horizon = _display_value(reference.get("horizon") or "20D")
    median = reference.get("median_return_pct")
    positive_rate = reference.get("positive_rate_pct")
    worst = reference.get("worst_return_pct")
    try:
        median_value = float(median)
    except (TypeError, ValueError):
        median_value = 0.0
    try:
        positive_value = float(positive_rate)
    except (TypeError, ValueError):
        positive_value = 0.0
    if median_value > 0 and positive_value >= 50:
        main = f"먼저 읽을 결론: 비슷한 상대강도 이후에는 {proxy_etf}가 {horizon} 기준 플러스였던 표본이 더 많았습니다."
    elif median_value < 0 or positive_value < 50:
        main = f"먼저 읽을 결론: 비슷한 상대강도 이후에도 {proxy_etf}의 {horizon} 흐름은 뚜렷하게 우호적이지 않았습니다."
    else:
        main = f"먼저 읽을 결론: 비슷한 상대강도 이후 {proxy_etf}의 {horizon} 분포는 한쪽으로 강하게 기울지 않았습니다."
    caution = f"표본 안의 최악은 {_analog_pct(worst)}입니다. 이 통계는 미래 움직임 보장이 아닙니다."
    return (
        '<div class="ov-analog-interpretation">'
        '<div class="ov-analog-insight">'
        '<div class="ov-analog-insight-label">먼저 볼 점</div>'
        f'<div class="ov-analog-insight-copy">{escape(main)}</div>'
        "</div>"
        '<div class="ov-analog-insight">'
        '<div class="ov-analog-insight-label">주의할 점</div>'
        f'<div class="ov-analog-insight-copy">{escape(caution)}</div>'
        "</div>"
        "</div>"
    )


def _analog_rows_by_priority(rows: list[dict[str, Any]], proxy_etf: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    display_rows = rows[:15]
    primary_assets = {asset for asset in (proxy_etf.strip().upper(), "SPY", "QQQ", "TLT", "GLD") if asset}
    primary_rows = [row for row in display_rows if _analog_row_asset(row) in primary_assets]
    support_rows = [row for row in display_rows if _analog_row_asset(row) not in primary_assets]
    if not primary_rows:
        return display_rows[:9], display_rows[9:]
    return primary_rows, support_rows


def _analog_basis_group_html(title: str, items: list[tuple[str, Any]]) -> str:
    item_html = "".join(
        '<div class="ov-analog-basis-item">'
        f'<span class="ov-analog-basis-label">{escape(label)}</span>'
        f'<span class="ov-analog-basis-value">{escape(_display_value(value))}</span>'
        "</div>"
        for label, value in items
    )
    return (
        '<div class="ov-analog-basis-group">'
        f'<div class="ov-analog-basis-title">{escape(title)}</div>'
        f'<div class="ov-analog-basis-list">{item_html}</div>'
        "</div>"
    )


def _analog_basis_warning_html(model: dict[str, Any]) -> str:
    alignment = dict(model.get("as_of_alignment") or {})
    warnings = [str(item) for item in list(model.get("basis_warnings") or []) if str(item).strip()]
    if not warnings and bool(alignment.get("is_aligned", True)):
        return ""
    requested = _display_value(alignment.get("requested_as_of") or model.get("requested_as_of") or "latest")
    effective = _display_value(alignment.get("effective_as_of") or model.get("current_as_of"))
    reason = _display_value(alignment.get("reason") or (warnings[0] if warnings else ""))
    warning = _display_value(warnings[0] if warnings else reason)
    limiting_symbols = [
        str(symbol).strip().upper()
        for symbol in list(alignment.get("limiting_symbols") or [])
        if str(symbol).strip()
    ]
    limiter_html = ""
    if limiting_symbols:
        limiter_html = (
            f'<span>제한한 가격 자료: {escape(", ".join(limiting_symbols[:6]))}'
            f'{escape(f" 외 {len(limiting_symbols) - 6}개" if len(limiting_symbols) > 6 else "")}</span>'
        )
    return (
        '<div class="ov-analog-basis-warning">'
        "<strong>선택 기준일과 실제 계산일이 다릅니다</strong>"
        f'<span>요청 기준일: {escape(requested)} · 실제 계산 기준일: {escape(effective)}</span>'
        f'<p>{escape(warning if warning != "-" else reason)}</p>'
        f"{limiter_html}"
        "</div>"
    )


def _analog_basis_ledger_html(
    model: dict[str, Any],
    *,
    requested_as_of: str,
    current_as_of: str,
    data_window: str,
    calculation_note: str,
    replay_basis: str,
    pattern_label: str,
) -> str:
    alignment = dict(model.get("as_of_alignment") or {})
    alignment_reason = alignment.get("reason")
    condition = _display_value(model.get("condition_summary") or model.get("detail"))
    sector = _display_value(model.get("leadership_sector"))
    proxy_etf = _display_value(model.get("proxy_etf"))
    sample_count = _display_value(model.get("sample_count"))
    is_aligned = bool(alignment.get("is_aligned", True))
    basis_value = f"{requested_as_of} · 계산 기준일 {current_as_of}"
    basis_detail = (
        alignment_reason
        if alignment_reason and not is_aligned
        else "DB 공통 가격의 최신 usable 기준으로 계산"
    )
    cells = [
        ("계산 기준", basis_value, basis_detail),
        ("기준 자산", f"{sector} · {proxy_etf}", "선택한 기준 시점의 리더십 섹터"),
        ("유사 조건", pattern_label, condition),
        ("표본", f"{sample_count}회", data_window),
    ]
    cell_html = "".join(
        '<div class="ov-analog-basis-cell">'
        f'<span>{escape(label)}</span>'
        f'<strong>{escape(_display_value(value))}</strong>'
        f'<small>{escape(_display_value(detail))}</small>'
        "</div>"
        for label, value, detail in cells
    )
    replay_note = replay_basis if replay_basis != "-" else "현재 universe/sector metadata 기준"
    boundary_note = "선택 기준일 이후 가격은 anchor/condition 계산에 사용하지 않음"
    return (
        f'<div class="ov-analog-basis-bar ov-analog-basis-summary">{cell_html}</div>'
        '<details class="ov-analog-technical-details">'
        "<summary>계산 경계 상세</summary>"
        f'<div>계산식: {escape(calculation_note)}</div>'
        f'<div>replay: {escape(replay_note)}</div>'
        f'<div>as-of 경계: {escape(boundary_note)}</div>'
        "</details>"
    )


def _analog_method_line_html(
    model: dict[str, Any],
    *,
    condition: str,
    pattern_label: str,
) -> str:
    proxy_etf = _display_value(model.get("proxy_etf"))
    return (
        '<div class="ov-analog-method-line">'
        '<strong>유사 맥락 계산</strong>'
        f'<span>선택한 기준 시점의 리더십 섹터를 ETF proxy로 보고, {escape(proxy_etf)}가 SPY 대비 {escape(pattern_label)} 기준 강했던 과거 구간을 찾습니다. 각 anchor 이후 5D / 20D / 60D 분포를 비교합니다.</span>'
        f'<small>조건: {escape(condition)}</small>'
        "</div>"
    )


def _macro_condition_list_html(title: str, items: list[dict[str, Any]]) -> str:
    display_items = items or [
        {
            "label": "-",
            "status_label": "없음",
            "detail": "이번 기준에서는 표시할 조건이 없습니다.",
        }
    ]
    item_html = "".join(
        '<div class="ov-macro-conditioned-condition">'
        f'<strong>{escape(_display_value(item.get("label")))}</strong>'
        f'<span>{escape(_display_value(item.get("status_label") or _display_status_label(item.get("status"))))}</span>'
        f'<p>{escape(_display_value(item.get("detail")))}</p>'
        "</div>"
        for item in display_items[:6]
    )
    return (
        '<div class="ov-macro-conditioned-condition-group">'
        f'<div class="ov-macro-conditioned-condition-title">{escape(title)}</div>'
        f'<div class="ov-macro-conditioned-condition-list">{item_html}</div>'
        "</div>"
    )


def _macro_used_condition_summary_html(items: list[dict[str, Any]]) -> str:
    if not items:
        return ""
    item_html = "".join(
        '<div class="ov-macro-condition-chip">'
        f'<strong>{escape(_display_value(item.get("label")))}</strong>'
        f'<span>{escape(_display_value(item.get("detail")))}</span>'
        "</div>"
        for item in items[:4]
    )
    return (
        '<div class="ov-macro-condition-summary">'
        '<div class="ov-macro-condition-summary-title">사용 조건</div>'
        f'<div class="ov-macro-condition-chip-row">{item_html}</div>'
        "</div>"
    )


def _macro_dimension_anchor_count(pilot: dict[str, Any], condition_id: str) -> Any:
    audit = dict(pilot.get("macro_dimension_audit") or {})
    for item in list(audit.get("dimensions") or []):
        if str(item.get("id") or "") == condition_id:
            return item.get("anchor_preview_count")
    return None


def _macro_condition_is_used(pilot: dict[str, Any], condition_id: str) -> bool:
    return any(str(item.get("id") or "") == condition_id for item in list(pilot.get("used_conditions") or []))


def _macro_dimension_audit_html(audit: dict[str, Any]) -> str:
    if not audit:
        return ""
    dimensions = list(audit.get("dimensions") or [])
    if not dimensions:
        return ""
    status_label = _display_value(audit.get("status_label") or _display_status_label(audit.get("status")))
    summary = _display_value(audit.get("summary"))

    def render_item(item: dict[str, Any]) -> str:
        latest = _display_value(item.get("latest_date"))
        coverage_start = _display_value(item.get("coverage_start"))
        coverage_end = _display_value(item.get("coverage_end"))
        anchor_count = _display_value(item.get("anchor_preview_count"))
        if str(item.get("status") or "").strip().upper() == "AVAILABLE_REFERENCE":
            anchor_text = f"같은 상태 {anchor_count}회"
        else:
            anchor_text = f"anchor {anchor_count}회"
        meta_parts = [
            f"usage: {_display_value(item.get('usage'))}",
            f"as-of: {latest}",
            f"coverage: {coverage_start} - {coverage_end}",
            anchor_text,
        ]
        bucket = _display_value(item.get("current_bucket"))
        if bucket != "-":
            meta_parts.append(f"bucket: {bucket}")
        return (
            '<div class="ov-macro-dimension-item">'
            '<div class="ov-macro-dimension-top">'
            f'<div class="ov-macro-dimension-label">{escape(_display_value(item.get("label")))}</div>'
            f'<div class="ov-macro-dimension-pill">{escape(_display_value(item.get("status_label") or _display_status_label(item.get("status"))))}</div>'
            "</div>"
            f'<div class="ov-macro-dimension-meta">{escape(" · ".join(meta_parts))}</div>'
            f'<div class="ov-macro-dimension-meta">{escape(_display_value(item.get("detail")))}</div>'
            "</div>"
        )

    group_order: list[tuple[str, Any]] = [
        ("기본 유사 맥락 기준", lambda item: str(item.get("id") or "") == "sector_relative_strength"),
        (
            "Macro 추가 조건",
            lambda item: str(item.get("status") or "").strip().upper() == "USED"
            and str(item.get("id") or "") != "sector_relative_strength",
        ),
        ("조건 미사용 참고 배경", lambda item: str(item.get("status") or "").strip().upper() == "AVAILABLE_REFERENCE"),
        ("보류 / annotation", lambda item: str(item.get("status") or "").strip().upper() == "DEFERRED"),
        (
            "이력 부족 / 자료 없음",
            lambda item: str(item.get("status") or "").strip().upper()
            in {"INSUFFICIENT_HISTORY", "UNAVAILABLE", "INSUFFICIENT_CONTEXT", "MISSING"},
        ),
        ("기타", lambda item: True),
    ]
    used_ids: set[int] = set()
    group_html: list[str] = []
    for title, predicate in group_order:
        items = [item for item in dimensions if id(item) not in used_ids and predicate(item)]
        if not items:
            continue
        used_ids.update(id(item) for item in items)
        group_html.append(
            '<div class="ov-macro-dimension-group">'
            f'<div class="ov-macro-dimension-group-title">{escape(title)}</div>'
            f'<div class="ov-macro-dimension-group-list">{"".join(render_item(item) for item in items)}</div>'
            "</div>"
        )
    return (
        '<div class="ov-macro-dimension-audit">'
        '<div class="ov-macro-dimension-head">'
        "<div>"
        '<div class="ov-macro-dimension-title">맥락 차원 상태</div>'
        '<div class="ov-macro-dimension-summary">조건 역할 세부</div>'
        f'<div class="ov-macro-dimension-summary">{escape(summary)}</div>'
        "</div>"
        f'<div class="ov-macro-dimension-status">{escape(status_label)}</div>'
        "</div>"
        f'<div class="ov-macro-dimension-groups">{"".join(group_html)}</div>'
        "</div>"
    )


def _macro_dimension_by_id(pilot: dict[str, Any], dimension_id: str) -> dict[str, Any]:
    audit = dict(pilot.get("macro_dimension_audit") or {})
    for item in list(audit.get("dimensions") or []):
        if str(item.get("id") or "") == dimension_id:
            return dict(item)
    return {}


def _macro_condition_count(pilot: dict[str, Any], condition: dict[str, Any], *, is_last: bool) -> Any:
    dimension = _macro_dimension_by_id(pilot, str(condition.get("id") or ""))
    count = dimension.get("anchor_preview_count")
    if count not in (None, ""):
        return count
    return pilot.get("sample_count") if is_last else "-"


def _macro_count_label(value: Any) -> str:
    display = _display_value(value)
    return "확인 중" if display == "-" else f"{display}회"


def _macro_pool_label(label: str, value: Any) -> str:
    display = _display_value(value)
    return f"{label} 표본" if display == "-" else f"{label} {display}회"


def _macro_stage_label(condition_id: str) -> str:
    labels = {
        "gld_safe_haven_context": "GLD 조건 적용",
        "futures_rate_pressure_context": "금리선물 조건 적용",
    }
    return labels.get(condition_id, "Macro 조건 적용")


def _macro_stage_state_name(condition_id: str) -> str:
    names = {
        "gld_safe_haven_context": "GLD 상태",
        "futures_rate_pressure_context": "금리선물 상태",
    }
    return names.get(condition_id, "Macro 상태")


def _macro_stage_detail(
    *,
    condition: dict[str, Any],
    count: Any,
    broad_count: Any,
    previous_condition_id: str | None,
    previous_count: Any,
) -> str:
    condition_id = str(condition.get("id") or "")
    count_label = _macro_count_label(count)
    if condition_id == "gld_safe_haven_context":
        return f"{_macro_pool_label('기본', broad_count)} 중 GLD 상태 {count_label}"
    if condition_id == "futures_rate_pressure_context":
        previous_label = "GLD 조건 통과" if previous_condition_id == "gld_safe_haven_context" else "직전 조건 통과"
        return f"{_macro_pool_label(previous_label, previous_count)} 중 금리선물 상태 {count_label}"
    return f"{_macro_pool_label('직전 조건 통과', previous_count)} 중 {_macro_stage_state_name(condition_id)} {count_label}"


def _macro_independent_stage_detail(
    *,
    condition_id: str,
    count: Any,
    broad_count: Any,
    futures_available: Any = None,
) -> str:
    count_label = _macro_count_label(count)
    broad_label = _macro_pool_label("기본", broad_count)
    if condition_id == "gld_safe_haven_context":
        return f"{broad_label} 중 GLD 상태 {count_label}"
    if condition_id == "futures_rate_pressure_context":
        detail = f"{broad_label} 중 금리선물 상태 {count_label}"
        if futures_available not in (None, "", broad_count):
            detail = f"{detail} · 계산 가능 {_macro_count_label(futures_available)}"
        return detail
    if condition_id == "macro_condition_intersection":
        return f"GLD와 금리선물이 모두 같았던 {count_label}"
    return f"{broad_label} 중 {_macro_stage_state_name(condition_id)} {count_label}"


def _macro_condition_meaning(
    condition_id: str,
    condition: dict[str, Any],
    *,
    proxy_etf: str,
    pattern_label: str,
) -> str:
    detail = str(condition.get("detail") or condition.get("label") or "").strip().lower()
    if condition_id == "sector_relative_strength":
        proxy = _display_value(proxy_etf)
        if proxy == "-":
            proxy = "기준 섹터 ETF"
        pattern = _display_value(pattern_label)
        if pattern == "-":
            pattern = "선택 패턴"
        return f"{proxy}가 SPY 대비 {pattern} 기준 비슷하게 강했던 구간"
    if condition_id == "gld_safe_haven_context":
        if "중립" in detail or "neutral" in detail:
            return "GLD가 현재처럼 중립권이었던 과거 구간"
        if "상승" in detail or "positive" in detail or "up" in detail:
            return "GLD가 현재처럼 상승 흐름이었던 과거 구간"
        if "하락" in detail or "negative" in detail or "down" in detail:
            return "GLD가 현재처럼 하락 흐름이었던 과거 구간"
        return "GLD가 현재와 비슷한 금/안전자산 배경이었던 구간"
    if condition_id == "futures_rate_pressure_context":
        if "mixed" in detail or "엇갈" in detail:
            return "ZN=F/ZB=F가 현재처럼 금리 압력이 엇갈렸던 구간"
        return "ZN=F/ZB=F가 현재와 비슷한 금리선물 배경이었던 구간"
    if condition_id == "macro_condition_intersection":
        return "GLD와 금리선물 배경이 모두 현재와 같았던 과거 구간"
    return f"{_macro_stage_state_name(condition_id)}가 현재와 비슷했던 구간"


def _macro_condition_source_details_html(pilot: dict[str, Any]) -> str:
    conditions = [
        item for item in list(pilot.get("used_conditions") or [])
        if str(item.get("id") or "") != "sector_relative_strength"
    ]
    if not conditions:
        return ""
    item_html = "".join(
        '<div class="ov-macro-dimension-item">'
        '<div class="ov-macro-dimension-top">'
        f'<div class="ov-macro-dimension-label">{escape(_display_value(item.get("label")))}</div>'
        f'<div class="ov-macro-dimension-pill">{escape(_display_value(item.get("status_label") or _display_status_label(item.get("status"))))}</div>'
        "</div>"
        f'<div class="ov-macro-dimension-meta">{escape(_display_value(item.get("detail")))}</div>'
        "</div>"
        for item in conditions
    )
    return (
        '<div class="ov-macro-dimension-group">'
        '<div class="ov-macro-dimension-group-title">Macro 조건 원문</div>'
        f'<div class="ov-macro-dimension-group-list">{item_html}</div>'
        "</div>"
    )


def _macro_sample_summary(pilot: dict[str, Any], macro_conditions: list[dict[str, Any]]) -> str:
    broad_count = pilot.get("broad_sample_count")
    sample_count = pilot.get("sample_count")
    if not macro_conditions:
        return f"기본 유사 맥락 {_macro_count_label(broad_count)}을 Macro 추가 조건 없이 그대로 비교합니다."
    return (
        f"기본 유사 맥락 {_macro_count_label(broad_count)} 중 "
        f"Macro 추가 배경까지 현재와 같았던 표본은 {_macro_count_label(sample_count)}입니다. "
        f"아래는 기본 {_macro_count_label(broad_count)}와 최종 {_macro_count_label(sample_count)}의 결과 차이입니다."
    )


def _macro_sample_flow_html(pilot: dict[str, Any], *, proxy_etf: str, pattern_label: str) -> str:
    used_conditions = list(pilot.get("used_conditions") or [])
    basis_condition = next(
        (item for item in used_conditions if str(item.get("id") or "") == "sector_relative_strength"),
        {},
    )
    macro_conditions = [
        item for item in used_conditions
        if str(item.get("id") or "") != "sector_relative_strength"
    ]
    by_condition_id = {str(item.get("id") or ""): item for item in used_conditions}
    condition_counts = dict(pilot.get("macro_condition_counts") or {})
    gld_condition = by_condition_id.get("gld_safe_haven_context")
    futures_condition = by_condition_id.get("futures_rate_pressure_context")
    has_intersection_counts = bool(condition_counts) and gld_condition and futures_condition
    items: list[tuple[str, str, str, str]] = [
        (
            "기본 유사 맥락 기준",
            _macro_count_label(pilot.get("broad_sample_count")),
            _macro_condition_meaning(
                "sector_relative_strength",
                basis_condition,
                proxy_etf=proxy_etf,
                pattern_label=pattern_label,
            ),
            _display_value(basis_condition.get("label") or "Sector ETF vs SPY relative strength"),
        )
    ]
    if has_intersection_counts:
        broad_count = condition_counts.get("broad", pilot.get("broad_sample_count"))
        gld_count = condition_counts.get("gld")
        futures_count = condition_counts.get("futures")
        intersection_count = condition_counts.get("intersection", pilot.get("sample_count"))
        futures_available = condition_counts.get("futures_available")
        items.extend(
            [
                (
                    "GLD 같은 상태",
                    _macro_count_label(gld_count),
                    _macro_condition_meaning(
                        "gld_safe_haven_context",
                        gld_condition,
                        proxy_etf=proxy_etf,
                        pattern_label=pattern_label,
                    ),
                    _macro_independent_stage_detail(
                        condition_id="gld_safe_haven_context",
                        count=gld_count,
                        broad_count=broad_count,
                    ),
                ),
                (
                    "금리선물 같은 상태",
                    _macro_count_label(futures_count),
                    _macro_condition_meaning(
                        "futures_rate_pressure_context",
                        futures_condition,
                        proxy_etf=proxy_etf,
                        pattern_label=pattern_label,
                    ),
                    _macro_independent_stage_detail(
                        condition_id="futures_rate_pressure_context",
                        count=futures_count,
                        broad_count=broad_count,
                        futures_available=futures_available,
                    ),
                ),
                (
                    "두 조건 모두",
                    _macro_count_label(intersection_count),
                    _macro_condition_meaning(
                        "macro_condition_intersection",
                        {},
                        proxy_etf=proxy_etf,
                        pattern_label=pattern_label,
                    ),
                    _macro_independent_stage_detail(
                        condition_id="macro_condition_intersection",
                        count=intersection_count,
                        broad_count=broad_count,
                    ),
                ),
            ]
        )
        summary = _macro_sample_summary(pilot, macro_conditions)
        item_html = "".join(
            '<div class="ov-analog-basis-cell ov-macro-basis-cell">'
            f'<span>{escape(label)}</span>'
            f'<strong>{escape(count)}</strong>'
            f'<small class="ov-macro-basis-meaning">{escape(meaning)}</small>'
            f'<small class="ov-macro-basis-count-detail">{escape(detail)}</small>'
            "</div>"
            for label, count, meaning, detail in items
        )
        return (
            f'<div class="ov-macro-conditioned-summary">{escape(summary)}</div>'
            f'<div class="ov-analog-basis-bar ov-analog-basis-summary ov-macro-basis-bar">{item_html}</div>'
        )
    previous_condition_id: str | None = None
    previous_count: Any = pilot.get("broad_sample_count")
    for index, condition in enumerate(macro_conditions):
        condition_id = str(condition.get("id") or "")
        count = _macro_condition_count(pilot, condition, is_last=index == len(macro_conditions) - 1)
        items.append(
            (
                _macro_stage_label(condition_id),
                _macro_count_label(count),
                _macro_condition_meaning(
                    condition_id,
                    condition,
                    proxy_etf=proxy_etf,
                    pattern_label=pattern_label,
                ),
                _macro_stage_detail(
                    condition=condition,
                    count=count,
                    broad_count=pilot.get("broad_sample_count"),
                    previous_condition_id=previous_condition_id,
                    previous_count=previous_count,
                ),
            )
        )
        previous_condition_id = condition_id
        previous_count = count
    summary = _macro_sample_summary(pilot, macro_conditions)
    item_html = "".join(
        '<div class="ov-analog-basis-cell ov-macro-basis-cell">'
        f'<span>{escape(label)}</span>'
        f'<strong>{escape(count)}</strong>'
        f'<small class="ov-macro-basis-meaning">{escape(meaning)}</small>'
        f'<small class="ov-macro-basis-count-detail">{escape(detail)}</small>'
        "</div>"
        for label, count, meaning, detail in items
    )
    return (
        f'<div class="ov-macro-conditioned-summary">{escape(summary)}</div>'
        f'<div class="ov-analog-basis-bar ov-analog-basis-summary ov-macro-basis-bar">{item_html}</div>'
    )


def _macro_result_delta_rows(
    *,
    broad_rows: list[dict[str, Any]],
    conditioned_rows: list[dict[str, Any]],
    proxy_etf: str,
) -> list[tuple[str, dict[str, Any], dict[str, Any], float | None]]:
    if not broad_rows or not conditioned_rows:
        return []
    reference = _analog_find_reference_row(conditioned_rows, proxy_etf)
    reference_horizon = _analog_row_horizon(reference) or "20D"
    primary_rows, _ = _analog_rows_by_priority(conditioned_rows, proxy_etf)
    ordered = [
        row for row in primary_rows
        if _analog_row_horizon(row) == reference_horizon
    ] or primary_rows[:5]
    results: list[tuple[str, dict[str, Any], dict[str, Any], float | None]] = []
    for row in ordered[:5]:
        asset = _analog_row_asset(row)
        horizon = _analog_row_horizon(row)
        broad = _analog_find_asset_horizon_row(broad_rows, asset, horizon)
        if not broad:
            continue
        delta: float | None = None
        try:
            delta = float(row.get("median_return_pct")) - float(broad.get("median_return_pct"))
        except (TypeError, ValueError):
            delta = None
        results.append((f"{asset} {horizon}", broad, row, delta))
    return results


def _macro_result_delta_html(
    *,
    broad_rows: list[dict[str, Any]],
    conditioned_rows: list[dict[str, Any]],
    proxy_etf: str,
) -> str:
    rows = _macro_result_delta_rows(
        broad_rows=broad_rows,
        conditioned_rows=conditioned_rows,
        proxy_etf=proxy_etf,
    )
    if not rows:
        return ""
    conditioned_sample = _display_value(rows[0][2].get("sample_count")) if rows else "-"

    def cell_html(label: str, value: Any, detail: str, *, strength_source: Any) -> str:
        try:
            numeric = float(strength_source)
        except (TypeError, ValueError):
            numeric = 0.0
        tone_class = "is-positive" if numeric > 0 else "is-negative" if numeric < 0 else "is-flat"
        gradient_class = "has-return-gradient" if tone_class in {"is-positive", "is-negative"} else ""
        return (
            f'<div class="ov-analog-matrix-cell {gradient_class} {tone_class}" style="--ov-analog-cell-strength:{escape(_analog_cell_strength(strength_source))};">'
            f'<div class="ov-analog-matrix-cell-label">{escape(label)}</div>'
            f'<strong>{escape(_analog_pct(value) if label != "변화" else _analog_delta_pct(value))}</strong>'
            f'<span>{escape(detail)}</span>'
            "</div>"
        )

    header_html = (
        '<div class="ov-analog-matrix-heading">기본</div>'
        '<div class="ov-analog-matrix-heading">조건 후</div>'
        '<div class="ov-analog-matrix-heading">변화</div>'
    )
    row_html = "".join(
        '<div class="ov-analog-matrix-row ov-macro-delta-matrix-row">'
        f'<div class="ov-analog-matrix-asset">{escape(label)}</div>'
        f'{cell_html("기본", broad.get("median_return_pct"), f"상승 {_analog_pct(broad.get("positive_rate_pct"))}", strength_source=broad.get("median_return_pct"))}'
        f'{cell_html("조건 후", conditioned.get("median_return_pct"), f"상승 {_analog_pct(conditioned.get("positive_rate_pct"))}", strength_source=conditioned.get("median_return_pct"))}'
        f'{cell_html("변화", delta, f"표본 {_display_value(conditioned.get("sample_count"))}회", strength_source=delta)}'
        "</div>"
        for label, broad, conditioned, delta in rows
    )
    return (
        '<div class="ov-analog-outcome-matrix ov-macro-delta-matrix">'
        '<div class="ov-analog-outcome-head">'
        '<div class="ov-analog-outcome-title">Macro 조건 결과 비교</div>'
        f'<div class="ov-analog-outcome-note">기본 표본과 Macro 조건 후 최종 {escape(conditioned_sample)}회 표본의 중앙 경로 차이입니다.</div>'
        "</div>"
        '<div class="ov-analog-matrix-grid" style="--ov-analog-horizon-count:3;">'
        f'<div class="ov-analog-matrix-header"><div></div>{header_html}</div>'
        f"{row_html}"
        "</div>"
        '<div class="ov-analog-matrix-legend">색상은 중간값 또는 변화 방향과 크기 기준</div>'
        "</div>"
    )


def _macro_backdrop_state_name(dimension_id: str) -> str:
    names = {
        "macro_t10y3m": "금리곡선",
        "macro_vixcls": "변동성",
        "macro_baa10y": "신용스프레드",
    }
    return names.get(dimension_id, "Macro")


def _macro_backdrop_display_label(dimension_id: str) -> str:
    labels = {
        "macro_t10y3m": "금리곡선",
        "macro_vixcls": "변동성",
        "macro_baa10y": "신용스프레드",
    }
    return labels.get(dimension_id, "Macro 배경")


def _macro_backdrop_description(dimension_id: str) -> str:
    descriptions = {
        "macro_t10y3m": "T10Y3M yield curve proxy · 10년물-3개월물 금리차",
        "macro_vixcls": "VIXCLS volatility backdrop · VIX 지수",
        "macro_baa10y": "BAA10Y credit spread backdrop · BAA 회사채와 10년 국채 금리차",
    }
    return descriptions.get(dimension_id, "")


def _macro_backdrop_state_label(dimension_id: str, raw_value: Any) -> str:
    raw = str(raw_value or "").strip().lower()
    if dimension_id == "macro_t10y3m":
        if "inverted" in raw or "역전" in raw:
            return "역전 금리곡선"
        if "flat" in raw or "평탄" in raw:
            return "평탄한 금리곡선"
        if "positive" in raw or "양" in raw:
            return "양의 금리곡선"
        return "금리곡선 참고"
    if dimension_id == "macro_vixcls":
        if "calm" in raw or "low" in raw or "안정" in raw:
            return "변동성 안정권"
        if "stress" in raw or "high" in raw or "elevated" in raw or "경계" in raw:
            return "변동성 경계"
        if "watch" in raw or "주의" in raw:
            return "변동성 주의"
        return "변동성 참고"
    if dimension_id == "macro_baa10y":
        if "contained" in raw or "stable" in raw or "안정" in raw:
            return "신용위험 안정권"
        if "widen" in raw or "stress" in raw or "elevated" in raw or "주의" in raw:
            return "신용위험 주의"
        return "신용스프레드 참고"
    return "Macro 참고"


def _macro_backdrop_interpretation(dimension_id: str) -> str:
    descriptions = {
        "macro_t10y3m": "금리곡선이 경기 둔화나 완화 기대를 어떻게 반영하는지 봅니다.",
        "macro_vixcls": "주식시장 변동성과 위험 회피 분위기를 보는 지표입니다.",
        "macro_baa10y": "회사채와 국채 금리차로 신용위험 부담을 봅니다.",
    }
    return descriptions.get(dimension_id, "")


def _macro_backdrop_state_meaning(dimension_id: str, raw_value: Any) -> str:
    raw = str(raw_value or "").strip().lower()
    if dimension_id == "macro_t10y3m":
        if "inverted" in raw or "역전" in raw:
            return "단기금리가 장기금리보다 높아진 역전 구간입니다."
        if "flat" in raw or "평탄" in raw:
            return "장단기 금리차가 작아 경기 기대가 뚜렷하게 벌어지지 않은 구간입니다."
        if "positive" in raw or "양" in raw:
            return "10년물 금리가 3개월물보다 높아 현재는 역전 구간은 아닙니다."
        return "금리곡선 상태를 참고 배경으로만 봅니다."
    if dimension_id == "macro_vixcls":
        if "calm" in raw or "low" in raw or "안정" in raw:
            return "VIX가 18 아래라 변동성은 비교적 안정권입니다."
        if "stress" in raw or "high" in raw or "elevated" in raw or "경계" in raw:
            return "VIX가 25 이상이라 위험 회피 압력이 높은 구간입니다."
        if "watch" in raw or "주의" in raw:
            return "VIX가 18 이상 25 미만이라 평온 구간보다는 높은 주의 구간입니다."
        return "변동성 상태를 참고 배경으로만 봅니다."
    if dimension_id == "macro_baa10y":
        if "contained" in raw or "stable" in raw or "안정" in raw:
            return "스프레드가 2%p 아래라 신용 부담은 안정권입니다."
        if "watch" in raw or "주의" in raw:
            return "스프레드가 2~3%p 구간이라 신용 부담을 주의해서 봅니다."
        if "widen" in raw or "stress" in raw or "elevated" in raw or "경계" in raw:
            return "스프레드가 3%p 이상으로 벌어져 신용 부담이 높은 구간입니다."
        return "신용스프레드 상태를 참고 배경으로만 봅니다."
    return ""


def _macro_backdrop_ratio(item: dict[str, Any], *, broad_count: Any) -> tuple[str, str]:
    count = item.get("anchor_preview_count")
    label = f"{_display_value(count)} / {_display_value(broad_count)}"
    try:
        numerator = float(count)
        denominator = float(broad_count)
        if denominator <= 0:
            raise ValueError
        width = max(0.0, min(100.0, numerator / denominator * 100.0))
    except (TypeError, ValueError):
        width = 0.0
    return label, f"{width:.1f}%"


def _macro_backdrop_detail(item: dict[str, Any]) -> str:
    dimension_id = str(item.get("id") or "")
    latest_date = _display_value(item.get("latest_date"))
    interpretation = _macro_backdrop_interpretation(dimension_id)
    return f"기준일 {latest_date} · 조건에는 쓰지 않은 참고 배경입니다. {interpretation}"


def _macro_backdrop_preview_html(pilot: dict[str, Any]) -> str:
    audit = dict(pilot.get("macro_dimension_audit") or {})
    dimensions = [
        dict(item) for item in list(audit.get("dimensions") or [])
        if str(item.get("status") or "").strip().upper() == "AVAILABLE_REFERENCE"
        and str(item.get("id") or "") in {"macro_t10y3m", "macro_vixcls", "macro_baa10y"}
    ]
    if not dimensions:
        return ""
    broad_count = audit.get("broad_anchor_count") or pilot.get("broad_sample_count")
    item_parts: list[str] = []
    for item in dimensions:
        dimension_id = str(item.get("id") or "")
        raw_state = item.get("current_bucket") or item.get("status_label")
        ratio_label, ratio_width = _macro_backdrop_ratio(item, broad_count=broad_count)
        state_meaning = _macro_backdrop_state_meaning(dimension_id, raw_state)
        item_parts.append(
            '<div class="ov-macro-backdrop-item">'
            '<div class="ov-macro-backdrop-top">'
            f'<div class="ov-macro-backdrop-label">{escape(_macro_backdrop_display_label(dimension_id))}</div>'
            f'<div class="ov-macro-backdrop-state">{escape(_macro_backdrop_state_label(dimension_id, raw_state))}</div>'
            "</div>"
            f'<div class="ov-macro-backdrop-value">{escape(_display_value(item.get("current_value")))}</div>'
            f'<div class="ov-macro-backdrop-meaning">{escape(state_meaning)}</div>'
            '<div class="ov-macro-backdrop-ratio">'
            f'<span>같은 상태 {escape(ratio_label)}</span>'
            '<div class="ov-macro-backdrop-track">'
            f'<div class="ov-macro-backdrop-fill" style="width:{escape(ratio_width)};"></div>'
            "</div>"
            "</div>"
            f'<div class="ov-macro-backdrop-description">{escape(_macro_backdrop_description(dimension_id))}</div>'
            f'<div class="ov-macro-backdrop-detail">{escape(_macro_backdrop_detail(item))}</div>'
            "</div>"
        )
    item_html = "".join(item_parts)
    return (
        '<div class="ov-macro-backdrop">'
        '<div class="ov-macro-backdrop-head">'
        '<div class="ov-macro-backdrop-title">조건에는 쓰지 않은 Macro 배경</div>'
        '<div class="ov-macro-backdrop-note">참고 전용</div>'
        "</div>"
        f'<div class="ov-macro-backdrop-grid">{item_html}</div>'
        "</div>"
    )


def _macro_conditioned_pilot_html(model: dict[str, Any], *, proxy_etf: str) -> str:
    pilot = dict(model.get("macro_conditioned_analog") or {})
    if not pilot:
        return ""
    tone_color = escape(_overview_tone_color(pilot.get("tone") or pilot.get("status")))
    status_label = _display_value(pilot.get("status_label") or _display_status_label(pilot.get("status")))
    sample_quality = dict(pilot.get("sample_quality") or {})
    rows = list(pilot.get("rows") or [])
    broad_rows = list(model.get("rows") or [])
    broad_reference = _analog_find_reference_row(broad_rows, proxy_etf)
    pilot_reference = _analog_find_reference_row(rows, proxy_etf)
    primary_rows, support_rows = _analog_rows_by_priority(rows, proxy_etf)
    table_html = ""
    if rows:
        table_html = (
            f"{_analog_table_block_html(primary_rows, title='Macro 조건 후 핵심 자산 원본 통계', note='Macro 추가 조건 후 남은 anchor 표본의 원본 분포입니다.')}"
            f"{_analog_table_block_html(support_rows, title='Macro 조건 후 보조 자산 원본 통계', note='같은 조건 후 표본의 배경 자산 분포입니다.', secondary=True)}"
        )
    pattern_label = _display_value(model.get("pattern_window_label") or model.get("pattern_window") or "5D")
    sample_flow_html = _macro_sample_flow_html(pilot, proxy_etf=proxy_etf, pattern_label=pattern_label)
    comparison_html = _macro_result_delta_html(
        broad_rows=broad_rows,
        conditioned_rows=rows,
        proxy_etf=proxy_etf,
    )
    backdrop_html = _macro_backdrop_preview_html(pilot)
    dimension_audit_html = _macro_dimension_audit_html(dict(pilot.get("macro_dimension_audit") or {}))
    condition_source_html = "" if dimension_audit_html else _macro_condition_source_details_html(pilot)
    details_html = ""
    if dimension_audit_html or condition_source_html or table_html:
        details_html = (
            '<details class="ov-macro-conditioned-details">'
            "<summary>Macro 조건 상세</summary>"
            f"{dimension_audit_html}"
            f"{condition_source_html}"
            f"{table_html}"
            "</details>"
        )
    return (
        f'<section class="ov-macro-reading-section ov-macro-compare-section" style="--ov-macro-pilot-tone:{tone_color};--ov-reading-tone:{tone_color};">'
        '<div class="ov-macro-conditioned-head">'
        "<div>"
        '<div class="ov-macro-conditioned-title">Macro 조건 후 결과 변화</div>'
        f'<div class="ov-macro-conditioned-detail">{escape(_display_value(pilot.get("headline")))}</div>'
        "</div>"
        f'<div class="ov-macro-conditioned-status">{escape(status_label)}</div>'
        "</div>"
        f"{sample_flow_html}"
        f"{comparison_html}"
        f'<div class="ov-macro-conditioned-quality">표본 품질: {escape(_display_value(sample_quality.get("label")))} · {escape(_display_value(sample_quality.get("detail")))}</div>'
        f'<div class="ov-macro-conditioned-reason">표본 {escape(_display_value(pilot.get("sample_count")))}회라 broad 결과와 함께 낮춰 읽습니다.</div>'
        f"{backdrop_html}"
        f"{details_html}"
        "</section>"
    )


def _macro_cockpit_historical_analog_html(model: dict[str, Any]) -> str:
    if not model:
        return ""
    tone_color = escape(_overview_tone_color(model.get("status")))
    status_label = _display_value(model.get("status_label") or _display_status_label(model.get("status")))
    rows = list(model.get("rows") or [])
    coverage_gaps = list(model.get("coverage_gaps") or [])
    repair_action = dict(model.get("repair_action") or {})
    condition = _display_value(model.get("condition_summary") or model.get("detail"))
    proxy_etf = _display_value(model.get("proxy_etf"))
    pattern_label = _display_value(model.get("pattern_window_label") or model.get("pattern_window") or "5D")
    if rows:
        primary_rows, support_rows = _analog_rows_by_priority(rows, proxy_etf)
        body_html = (
            f"{_analog_method_line_html(model, condition=condition, pattern_label=pattern_label)}"
            f"{_analog_summary_strip_html(model, rows)}"
            f"{_analog_outcome_matrix_html(primary_rows, title='핵심 자산 비교', note='기준 섹터 ETF, SPY, QQQ, 채권 TLT, 금 GLD를 같은 표본으로 비교합니다.')}"
            f"{_analog_detail_tables_html(primary_rows, support_rows)}"
        )
    elif coverage_gaps and repair_action:
        gap_rows: list[str] = []
        for gap in coverage_gaps[:6]:
            row_count = _display_value(gap.get("row_count"))
            min_rows = _display_value(gap.get("min_rows"))
            window = " ~ ".join(
                item
                for item in (
                    _display_value(gap.get("start_date")),
                    _display_value(gap.get("end_date")),
                )
                if item != "-"
            )
            gap_rows.append(
                '<div class="ov-analog-gap-item">'
                f'<div class="ov-analog-gap-symbol">{escape(_display_value(gap.get("symbol")))}</div>'
                f'<div class="ov-analog-gap-rows">{escape(row_count)} / {escape(min_rows)} rows</div>'
                f'<div class="ov-analog-gap-meta">{escape(window or _display_value(gap.get("detail")))}</div>'
                "</div>"
            )
        action_symbols = ", ".join(str(symbol) for symbol in repair_action.get("symbols") or [])
        action_detail = (
            f"아래 자료 수집 버튼으로 {escape(action_symbols)} "
            f"{escape(_display_value(repair_action.get('period')))} "
            f"{escape(_display_value(repair_action.get('interval')))} 가격 이력을 보강합니다."
        )
        body_html = (
            '<div class="ov-analog-gap-panel">'
            f'<div class="ov-analog-gap-title">{escape(_display_value(repair_action.get("label") or "부족 ETF 가격 이력 보강"))}</div>'
            '<div class="ov-analog-gap-detail">과거 유사 맥락을 계산하려면 아래 가격 이력이 먼저 필요합니다.</div>'
            f'<div class="ov-analog-gap-list">{"".join(gap_rows)}</div>'
            f'<div class="ov-analog-gap-action">{action_detail}</div>'
            "</div>"
        )
    else:
        body_html = (
            '<div class="ov-historical-analog-note">'
            "자료가 충분한 sector ETF history가 쌓이면 5D / 20D / 60D 요약을 표시합니다."
            "</div>"
        )
    limitations = " · ".join(str(item) for item in list(model.get("limitations") or [])[:4])
    section_class = "ov-macro-reading-section ov-historical-analog-row"
    if not rows:
        section_class += " is-muted-reference"
    current_as_of = _display_value(model.get("current_as_of"))
    requested_as_of = _display_value(model.get("requested_as_of") or "latest")
    data_window = _display_value(model.get("data_window"))
    calculation_note = _display_value(model.get("calculation_note") or f"선택한 기준 시점의 sector ETF SPY 대비 {pattern_label} 상대강도 기준")
    replay_basis = _display_value(model.get("leadership_replay_basis"))
    scope_html = (
        '<div class="ov-historical-analog-scope">'
        "기준 변경은 아래 과거 참고 통계에만 적용됩니다. 상단 시장 브리프는 현재 세션에 맞춘 장중 snapshot 또는 마지막 거래일 기준이며, 기준 시점/기준일/패턴 기간 변경은 이 섹션의 과거 분포만 다시 계산합니다."
        "</div>"
    )
    meta_html = _analog_basis_ledger_html(
        model,
        requested_as_of=requested_as_of,
        current_as_of=current_as_of,
        data_window=data_window,
        calculation_note=calculation_note,
        replay_basis=replay_basis,
        pattern_label=pattern_label,
    )
    basis_warning_html = _analog_basis_warning_html(model)
    condition_html = "" if rows else f'<div class="ov-historical-analog-detail">{escape(condition)}</div>'
    macro_pilot_html = _macro_conditioned_pilot_html(model, proxy_etf=proxy_etf) if rows else ""
    section_detail = (
        "선택 기준과 유사했던 과거 구간의 이후 분포"
        if rows
        else _display_value(model.get("headline"))
    )
    analog_section_html = (
        f'<section class="{section_class}" style="--ov-analog-tone:{tone_color};--ov-reading-tone:{tone_color};">'
        '<div class="ov-historical-analog-head">'
        "<div>"
        '<div class="ov-historical-analog-title">참고: 과거 유사 맥락</div>'
        f'<div class="ov-historical-analog-detail">{escape(section_detail)}</div>'
        "</div>"
        f'<div class="ov-historical-analog-status">{escape(status_label)}</div>'
        "</div>"
        f"{scope_html}"
        f"{basis_warning_html}"
        f'<div class="ov-historical-analog-meta">{meta_html}</div>'
        f"{condition_html}"
        f"{body_html}"
        f'<div class="ov-historical-analog-limitations">{escape(limitations)}</div>'
        "</section>"
    )
    return f"{analog_section_html}{macro_pilot_html}"


def _source_confidence_status_bucket(status: Any) -> str:
    normalized = str(status or "").strip().upper()
    if normalized in {"OK", "PASS", "READY", "SUCCESS"}:
        return "ok"
    if normalized in {"REFERENCE_LIMIT", "META", "INFO"}:
        return "reference"
    if normalized in {"MISSING", "INSUFFICIENT_DATA", "BLOCKED", "FAILED", "ERROR"}:
        return "missing"
    return "review"


def _source_confidence_summary_strip_html(summary: dict[str, Any], items: list[dict[str, Any]]) -> str:
    def safe_count(value: Any) -> int:
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return 0

    bucket_counts = {"ok": 0, "review": 0, "reference": 0, "missing": 0}
    for item in items:
        bucket_counts[_source_confidence_status_bucket(item.get("status"))] += 1
    ok_count = summary.get("ok_count", bucket_counts["ok"])
    review_count = summary.get("review_count", bucket_counts["review"])
    reference_count = summary.get("reference_count", bucket_counts["reference"])
    missing_count = summary.get("missing_count", bucket_counts["missing"])
    metric_items = [
        ("브리프 자료 정상", ok_count, "정상", "OK"),
        ("현재 보강 대상", review_count, "보강", "REVIEW" if safe_count(review_count) else "OK"),
        ("참고 제한", reference_count, "참고", "META"),
        ("자료 부족", missing_count, "부족", "INSUFFICIENT_DATA" if safe_count(missing_count) else "OK"),
    ]
    metrics: list[str] = []
    for label, count, legacy_label, tone in metric_items:
        count_text = _display_value(count)
        metrics.append(
            f'<div class="ov-source-status-metric" style="--ov-source-strip-tone:{escape(_overview_tone_color(tone))};">'
            f'<div class="ov-source-status-label">{escape(label)}</div>'
            f'<strong class="ov-source-status-value">{escape(count_text)}개</strong>'
            f'<span class="ov-source-status-legacy">{escape(label)} {escape(count_text)}개</span>'
            f'<span class="ov-source-status-legacy">{escape(legacy_label)} {escape(count_text)}</span>'
            "</div>"
        )
    review_items = [
        item
        for item in items
        if item.get("counts_for_status", True) and _source_confidence_status_bucket(item.get("status")) != "ok"
    ]
    reference_items = [
        item
        for item in items
        if not item.get("counts_for_status", True) and _source_confidence_status_bucket(item.get("status")) != "ok"
    ]
    action_items = review_items[:3] or reference_items[:2] or items[:2]
    chips: list[str] = []
    for item in action_items:
        surface = _display_value(item.get("surface"))
        item_status = _display_value(item.get("status_label") or _display_status_label(item.get("status")))
        next_check = _display_value(item.get("next_check"))
        action_hint = "" if next_check == "-" else f" → {next_check}"
        chips.append(
            f'<span class="ov-source-confidence-source" style="--ov-source-strip-tone:{escape(_overview_tone_color(item.get("tone") or item.get("status")))};">'
            f"{escape(surface)} · {escape(item_status)}{escape(action_hint)}"
            "</span>"
        )
    scan_html = f'<div class="ov-source-confidence-scan">{"".join(chips)}</div>' if chips else ""
    return (
        '<div class="ov-source-confidence-strip ov-source-status-board">'
        '<div class="ov-source-status-board-title">자료 상태 요약</div>'
        f'<div class="ov-source-status-grid">{"".join(metrics)}</div>'
        f"{scan_html}"
        "</div>"
    )


def _macro_cockpit_source_confidence_html(model: dict[str, Any]) -> str:
    if not model:
        return ""
    summary = dict(model.get("summary") or {})
    status_tone = escape(_overview_tone_color(model.get("status")))
    status_label = _display_value(model.get("status_label") or _display_status_label(model.get("status")))
    source_items = list(model.get("items") or [])
    summary_strip_html = _source_confidence_summary_strip_html(summary, source_items)
    summary_detail = _display_value(summary.get("detail"))
    if "관리 위치" in summary_detail:
        summary_detail = "브리프에 직접 쓰는 자료와 참고 / 관리 자료를 나누고, 실제 보강 대상만 따로 표시합니다."
    def render_source_row(item: dict[str, Any]) -> str:
        tone_color = escape(_overview_tone_color(item.get("tone") or item.get("status")))
        bucket = _source_confidence_status_bucket(item.get("status"))
        item_status = _display_value(item.get("status_label") or _display_status_label(item.get("status")))
        freshness = _display_value(item.get("freshness_label") or _display_freshness_label(item.get("freshness")))
        next_check = _display_value(item.get("next_check"))
        caveat = _display_value(item.get("caveat"))
        action_note = caveat
        if bucket == "ok":
            action_note = "보강 불필요"
        elif next_check != "-":
            action_note = next_check
        elif bucket == "reference":
            action_note = "참고로 분리" if caveat == "-" else caveat
        return (
            f'<div class="ov-source-confidence-row" style="--ov-source-tone:{tone_color};">'
            '<div>'
            f'<div class="ov-source-confidence-surface">{escape(_display_value(item.get("surface")))}</div>'
            f'<div class="ov-source-confidence-row-status">{escape(item_status)}</div>'
            "</div>"
            "<div>"
            '<div class="ov-source-confidence-row-basis">'
            "<strong>자료 기준</strong>"
            f'{escape(freshness)}'
            "</div>"
            "</div>"
            "<div>"
            f'<div class="ov-source-confidence-row-title">{escape(_display_value(item.get("title")))}</div>'
            f'<div class="ov-source-confidence-row-detail">{escape(_display_value(item.get("detail")))}</div>'
            '<div class="ov-source-confidence-row-usage">'
            "<strong>사용 위치</strong>"
            f'{escape(_display_value(item.get("owner")))}'
            "</div>"
            "</div>"
            "<div>"
            '<div class="ov-source-confidence-row-action">'
            "<strong>보강 판단</strong>"
            f'{escape(action_note)}'
            "</div>"
            "</div>"
            "</div>"
        )

    direct_items = [
        item
        for item in source_items[:6]
        if str(item.get("source_role") or "brief_source") in {"brief_source", "context_source"}
    ]
    reference_items = [
        item
        for item in source_items[:6]
        if str(item.get("source_role") or "brief_source") not in {"brief_source", "context_source"}
    ]
    sections: list[str] = []
    if direct_items:
        sections.append(
            '<div class="ov-source-confidence-group">시장 브리프 직접 자료 <span>브리프 자료</span></div>'
            + "".join(render_source_row(item) for item in direct_items)
        )
    if reference_items:
        sections.append(
            '<div class="ov-source-confidence-group">참고 / 관리 자료 <span>참고 / 관리 메타</span></div>'
            + "".join(render_source_row(item) for item in reference_items)
        )
    ledger_head = (
        '<div class="ov-source-ledger-head">'
        "<div>자료</div>"
        "<div>자료 기준</div>"
        "<div>사용 위치</div>"
        "<div>보강 판단</div>"
        "</div>"
    )
    action_strip = (
        '<div class="ov-source-action-strip">'
        "필요 자료 보강은 아래 접힌 영역에서 기존 Overview 갱신 경로로만 실행합니다. 실행 대상이 없으면 전체 보강만 보조로 남기며, 이 화면은 provider를 직접 호출하지 않습니다."
        "</div>"
    )
    return (
        f'<details class="ov-macro-reading-section ov-source-confidence ov-source-ledger ov-context-disclosure is-evidence-footer" style="--ov-source-status-tone:{status_tone};--ov-reading-tone:{status_tone};">'
        '<summary class="ov-source-confidence-summary">'
        '<div class="ov-source-confidence-head">'
        '<div>'
        '<div class="ov-source-confidence-title">근거: 자료 기준 / 출처 상태</div>'
        f'<div class="ov-source-confidence-detail">{escape(summary_detail)}</div>'
        f"{summary_strip_html}"
        '</div>'
        f'<div class="ov-source-confidence-status">{escape(status_label)}</div>'
        '</div>'
        '</summary>'
        '<div class="ov-source-confidence-body ov-context-disclosure-body">'
        f"{ledger_head}"
        f'<div class="ov-source-confidence-list ov-source-ledger">{"".join(sections)}</div>'
        f"{action_strip}"
        f'<div class="ov-source-confidence-boundary">{escape(_display_value(model.get("boundary_note")))}</div>'
        '</div>'
        '</details>'
    )


def _macro_cockpit_body_html(model: dict[str, Any]) -> str:
    summary = dict(model.get("summary") or {})
    rail_html = _macro_hybrid_tape_html(list(summary.get("rail") or []))
    if not rail_html:
        rail_html = _macro_cockpit_rail_html(list(summary.get("rail") or []))
    brief_html = _macro_cockpit_brief_rows_html(
        list(model.get("brief_rows") or []),
        market_session=dict(model.get("market_session") or {}),
    )
    visual_board_html = _macro_cockpit_visual_board_html(model)
    return f"{rail_html}{brief_html}{visual_board_html}"


def _macro_context_reading_flow_html(
    model: dict[str, Any],
    *,
    include_brief: bool = True,
    include_next_checks: bool = True,
    include_historical_analog: bool = True,
    include_source_confidence: bool = True,
) -> str:
    brief_rows_html = (
        _macro_cockpit_brief_rows_html(
            list(model.get("brief_rows") or []),
            market_session=dict(model.get("market_session") or {}),
        )
        if include_brief
        else ""
    )
    context_findings = list(model.get("extra_context_findings") or [])
    next_checks_html = _macro_cockpit_next_checks_html(context_findings) if include_next_checks else ""
    historical_analog_html = (
        _macro_cockpit_historical_analog_html(dict(model.get("historical_analog") or {}))
        if include_historical_analog
        else ""
    )
    source_confidence_html = (
        _macro_cockpit_source_confidence_html(dict(model.get("source_confidence") or {}))
        if include_source_confidence
        else ""
    )
    boundary_html = (
        f'<div class="ov-macro-reading-boundary ov-macro-cockpit-boundary">{escape(_display_value(model.get("boundary_note")))}</div>'
        if _display_value(model.get("boundary_note")) != "-"
        else ""
    )
    flow_html = (
        f"{brief_rows_html}"
        f"{next_checks_html}"
        f"{historical_analog_html}"
        f"{source_confidence_html}"
        f"{boundary_html}"
    )
    if not flow_html:
        return ""
    return f'<section class="ov-macro-reading-flow">{flow_html}</section>'


def _macro_context_cockpit_html(model: dict[str, Any], *, include_reading_flow: bool = True) -> str:
    summary = dict(model.get("summary") or {})
    tone_color = escape(_overview_tone_color(summary.get("tone") or model.get("status")))
    body_html = _macro_cockpit_body_html(model)
    reading_flow_html = _macro_context_reading_flow_html(model, include_brief=False) if include_reading_flow else ""
    return (
        f'<section class="ov-macro-cockpit" style="--ov-cockpit-tone:{tone_color};">'
        '<div class="ov-macro-cockpit-head">'
        '<div class="ov-macro-cockpit-narrative">'
        '<div class="ov-macro-cockpit-kicker">오늘의 시장 맥락</div>'
        f'<div class="ov-macro-cockpit-title">{escape(_display_value(summary.get("headline")))}</div>'
        f'<div class="ov-macro-cockpit-detail">{escape(_display_value(summary.get("detail")))}</div>'
        "</div>"
        f'<span class="ov-macro-cockpit-status">{escape(_display_value(summary.get("status_label") or _display_status_label(model.get("status"))))}</span>'
        "</div>"
        f"{body_html}"
        "</section>"
        f"{reading_flow_html}"
    )


def render_macro_context_cockpit(model: dict[str, Any], *, include_reading_flow: bool = True) -> None:
    st.markdown(
        overview_ui_css()
        + _macro_context_cockpit_html(model, include_reading_flow=include_reading_flow),
        unsafe_allow_html=True,
    )


def render_macro_context_reading_flow(
    model: dict[str, Any],
    *,
    include_brief: bool = True,
    include_next_checks: bool = True,
    include_historical_analog: bool = True,
    include_source_confidence: bool = True,
) -> None:
    st.markdown(
        _macro_context_reading_flow_html(
            model,
            include_brief=include_brief,
            include_next_checks=include_next_checks,
            include_historical_analog=include_historical_analog,
            include_source_confidence=include_source_confidence,
        ),
        unsafe_allow_html=True,
    )


def render_overview_ia_closeout_guide(model: dict[str, Any]) -> None:
    if not model:
        return
    cards: list[str] = []
    for section in list(model.get("sections") or []):
        tone_color = escape(_overview_tone_color(section.get("tone") or section.get("status")))
        chips = "".join(
            f'<span class="ov-ia-closeout-chip">{escape(_display_value(tab))}</span>'
            for tab in list(section.get("tabs") or [])
        )
        cards.append(
            f'<article class="ov-ia-closeout-card" style="--ov-ia-tone:{tone_color};">'
            '<div class="ov-ia-closeout-card-head">'
            f'<div class="ov-ia-closeout-card-title">{escape(_display_value(section.get("title")))}</div>'
            f'<div class="ov-ia-closeout-card-status">{escape(_display_value(section.get("status")))}</div>'
            "</div>"
            f'<div class="ov-ia-closeout-card-detail">{escape(_display_value(section.get("detail")))}</div>'
            f'<div class="ov-ia-closeout-tabs">{chips}</div>'
            f'<div class="ov-ia-closeout-owner">Owner: {escape(_display_value(section.get("owner")))}</div>'
            f'<div class="ov-ia-closeout-next">{escape(_display_value(section.get("next_step")))}</div>'
            "</article>"
        )
    st.markdown(
        overview_ui_css()
        + f"""
<details class="ov-ia-closeout ov-context-disclosure">
  <summary class="ov-ia-closeout-summary">
    <div class="ov-ia-closeout-head">
    <div>
      <div class="ov-ia-closeout-kicker">Overview Map / 화면 지도</div>
      <div class="ov-ia-closeout-title">{escape(_display_value(model.get("title")))}</div>
      <div class="ov-ia-closeout-detail">{escape(_display_value(model.get("detail")))}</div>
    </div>
    </div>
  </summary>
  <div class="ov-ia-closeout-body ov-context-disclosure-body">
    <div class="ov-ia-closeout-grid">{"".join(cards)}</div>
    <div class="ov-ia-closeout-boundary">{escape(_display_value(model.get("boundary_note")))}</div>
  </div>
</details>""",
        unsafe_allow_html=True,
    )


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


def _breadth_summary_cards_html(cards: list[dict[str, Any]]) -> str:
    html: list[str] = []
    for card in cards[:4]:
        tone_color = escape(_overview_tone_color(card.get("tone")))
        html.append(
            f'<article class="ov-breadth-card" style="--ov-card-tone:{tone_color};">'
            f'<div class="ov-breadth-card-label">{escape(_display_value(card.get("title")))}</div>'
            f'<div class="ov-breadth-card-value">{escape(_display_value(card.get("value")))}</div>'
            f'<div class="ov-breadth-card-detail">{escape(_display_value(card.get("detail")))}</div>'
            "</article>"
        )
    return "".join(html)


def _breadth_rows_html(rows: list[dict[str, Any]]) -> str:
    html: list[str] = []
    for row in rows[:5]:
        tone_color = escape(_overview_tone_color(row.get("tone")))
        group = _display_value(row.get("group"))
        weighted = _display_value(row.get("market_cap_weighted_return_pct"))
        positive = _display_value(row.get("positive_symbol_share_pct"))
        top_symbol = _display_value(row.get("top_symbol"))
        top_return = _display_value(row.get("top_symbol_return_pct"))
        html.append(
            f'<div class="ov-breadth-row" style="--ov-row-tone:{tone_color};">'
            f'<div class="ov-breadth-row-label">#{escape(_display_value(row.get("rank")))} · {escape(group)}</div>'
            f'<div class="ov-breadth-row-value">{escape(weighted)}%</div>'
            f'<div class="ov-breadth-row-detail">{escape(positive)}% positive · {escape(top_symbol)} {escape(top_return)}%</div>'
            "</div>"
        )
    return "".join(html)


def render_breadth_heatmap_summary(model: dict[str, Any]) -> None:
    summary = dict(model.get("summary") or {})
    tone_color = escape(_overview_tone_color(model.get("status")))
    cards_html = _breadth_summary_cards_html(list(model.get("cards") or []))
    rows_html = _breadth_rows_html(list(model.get("heatmap_rows") or []))
    coverage = dict(model.get("coverage") or {})
    freshness = _display_value(coverage.get("freshness"))
    st.markdown(
        overview_ui_css()
        + f"""
<section class="ov-breadth-summary" style="--ov-band-tone:{tone_color};">
  <div class="ov-breadth-head">
    <div>
      <div class="ov-breadth-kicker">Breadth / Concentration</div>
      <div class="ov-breadth-title">{escape(_display_value(summary.get("headline")))}</div>
      <div class="ov-breadth-detail">{escape(_display_value(summary.get("detail")))} · Freshness: {escape(freshness)}</div>
    </div>
    <span class="ov-breadth-status">{escape(_display_value(model.get("status")))}</span>
  </div>
  <div class="ov-breadth-card-grid">{cards_html}</div>
  <div class="ov-breadth-row-grid">{rows_html}</div>
  <div class="ov-breadth-boundary">{escape(_display_value(model.get("boundary_note")))}</div>
</section>""",
        unsafe_allow_html=True,
    )


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
