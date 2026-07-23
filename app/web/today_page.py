from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from typing import Any, Callable
from zoneinfo import ZoneInfo

import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx

from app.services.futures_macro_snapshot import (
    load_overview_futures_macro_materialized_snapshot,
)
from app.services.overview.events import build_market_events_snapshot
from app.services.portfolio_monitoring.intraday_refresh import (
    RegularSessionState,
    build_intraday_refresh_scope,
    build_live_portfolio_overlay,
    load_latest_daily_dates,
    load_latest_portfolio_quotes,
    load_workspace_eod_closes,
    resolve_regular_session_state,
)
from app.services.today import (
    build_today_read_model,
    project_today_portfolio_live,
)
from app.web.final_selected_portfolio_dashboard import (
    TodayPortfolioRuntimeContext,
    load_default_portfolio_monitoring_context_for_today,
    load_default_portfolio_monitoring_workspace_for_today,
)
from app.web.overview.components.common import overview_ui_css
from app.web.overview.market_context_helpers import (
    load_economic_cycle_model,
    load_sp500_valuation_model,
)
from app.web.overview.navigation import OVERVIEW_DEEP_TAB_QUERY_PARAM
from app.web.overview_dashboard_helpers import (
    load_overview_market_events_snapshot,
    load_overview_market_sentiment_snapshot,
)
from app.web.today_react_component import (
    render_today_workbench,
    today_react_component_available,
)
from app.web.today_intraday_auto_refresh import (
    CoordinatorSnapshot,
    get_today_intraday_coordinator,
)


_TODAY_PAGE_TARGETS: dict[str, object] = {}
_TODAY_EVENT_ROUTES: dict[str, tuple[str, dict[str, str] | None]] = {
    "open_market_research": (
        "market_research",
        {OVERVIEW_DEEP_TAB_QUERY_PARAM: "market-context"},
    ),
    "open_stock_research": (
        "stock_research",
        {OVERVIEW_DEEP_TAB_QUERY_PARAM: "market-movers"},
    ),
    "open_portfolio_monitoring": ("portfolio_monitoring", None),
}


def configure_today_page_targets(page_targets: dict[str, object]) -> None:
    """Configure existing Streamlit Page objects used by Today handoff links."""

    _TODAY_PAGE_TARGETS.clear()
    _TODAY_PAGE_TARGETS.update(
        {
            key: value
            for key, value in dict(page_targets or {}).items()
            if key in {"market_research", "stock_research", "portfolio_monitoring"}
            and value is not None
        }
    )


def _safe_load(loader: Callable[[], Any], *, label: str) -> Any:
    try:
        return loader()
    except Exception:  # pragma: no cover - actual UI resilience
        return {
            "status": "ERROR",
            "reason": f"{label} 저장 자료를 불러오지 못했습니다.",
        }


def load_today_market_calendar(*, generated_at: datetime) -> dict[str, Any]:
    """Load official holiday and early-close rows without broad event mixing."""

    now_utc = generated_at.astimezone(timezone.utc)
    market_date = now_utc.astimezone(ZoneInfo("America/New_York")).date()
    start_date = f"{market_date.year}-01-01"
    end_date = f"{market_date.year + 1}-12-31"
    snapshots = {
        "holiday": build_market_events_snapshot(
            start_date=start_date,
            end_date=end_date,
            event_type="MARKET_HOLIDAY",
            recent_days=0,
            limit=100,
            today=market_date,
        ),
        "early_close": build_market_events_snapshot(
            start_date=start_date,
            end_date=end_date,
            event_type="EARLY_CLOSE",
            recent_days=0,
            limit=100,
            today=market_date,
        ),
    }
    return {
        "holiday_rows": snapshots["holiday"].get("rows"),
        "early_close_rows": snapshots["early_close"].get("rows"),
        "statuses": {
            "holiday": snapshots["holiday"].get("status"),
            "early_close": snapshots["early_close"].get("status"),
        },
    }


def load_today_read_model(
    *,
    generated_at: datetime | None = None,
    portfolio_workspace: Any | None = None,
    portfolio_live: Any | None = None,
) -> dict[str, object]:
    """Load existing persisted sources and compose one read-only Today model."""

    timestamp = generated_at or datetime.now(timezone.utc)
    return build_today_read_model(
        economic_cycle=_safe_load(load_economic_cycle_model, label="경제 사이클"),
        sp500=_safe_load(load_sp500_valuation_model, label="S&P 500"),
        futures_macro=_safe_load(
            load_overview_futures_macro_materialized_snapshot,
            label="선물 매크로",
        ),
        sentiment=_safe_load(
            load_overview_market_sentiment_snapshot,
            label="시장 심리",
        ),
        events=_safe_load(
            lambda: load_overview_market_events_snapshot(horizon_days=45),
            label="시장 일정",
        ),
        portfolio=(
            portfolio_workspace
            if portfolio_workspace is not None
            else _safe_load(
                load_default_portfolio_monitoring_workspace_for_today,
                label="대표 포트폴리오",
            )
        ),
        market_calendar=_safe_load(
            lambda: load_today_market_calendar(generated_at=timestamp),
            label="미국 증시 일정",
        ),
        portfolio_live=portfolio_live,
        generated_at=timestamp,
    )


def _today_css() -> str:
    return """
<style>
.today-shell {
  --today-tone: var(--ov-mi-color-primary);
  color: inherit;
}
.today-header {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 1rem;
  align-items: end;
  margin: 0.2rem 0 0.85rem;
  padding: 0.15rem 0 0.9rem;
  border-bottom: 1px solid var(--ov-mi-border-subtle);
}
.today-kicker {
  color: var(--ov-mi-color-primary);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.today-title {
  margin: 0.22rem 0 0;
  color: inherit;
  font-size: 1.72rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.15;
  letter-spacing: -0.035em;
}
.today-subtitle {
  max-width: 58rem;
  margin-top: 0.3rem;
  color: inherit;
  opacity: 0.72;
  font-size: 0.88rem;
  line-height: 1.45;
}
.today-asof {
  min-width: 11rem;
  text-align: right;
}
.today-badge {
  display: inline-flex;
  align-items: center;
  min-height: 1.45rem;
  padding: 0.17rem 0.52rem;
  border: 1px solid color-mix(in srgb, var(--today-tone) 32%, transparent);
  border-radius: var(--ov-mi-radius-pill);
  background: color-mix(in srgb, var(--today-tone) 8%, var(--ov-mi-color-surface));
  color: var(--today-tone);
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
}
.today-asof-date {
  margin-top: 0.26rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
}
.today-market-brief {
  --today-tone: var(--ov-mi-color-warning);
  margin: 0 0 0.82rem;
  padding: 0.9rem 1rem;
  border-top: 1px solid var(--ov-mi-border-faint);
  border-bottom: 1px solid var(--ov-mi-border-faint);
  border-left: 4px solid var(--today-tone);
  background:
    linear-gradient(90deg, color-mix(in srgb, var(--today-tone) 7%, var(--ov-mi-color-surface)), rgba(255,255,255,0.98)),
    var(--ov-mi-color-surface);
}
.today-brief-label,
.today-section-kicker {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.today-brief-headline {
  max-width: 72rem;
  margin-top: 0.26rem;
  color: var(--ov-mi-color-text);
  font-size: 1.15rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.34;
  overflow-wrap: anywhere;
}
.today-brief-summary {
  max-width: 66rem;
  margin-top: 0.32rem;
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-body);
  line-height: 1.42;
}
.today-context-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.55fr) minmax(15rem, 0.72fr);
  gap: 0.72rem;
  margin-bottom: 0.9rem;
}
.today-panel {
  min-width: 0;
  padding: 0.75rem 0.82rem;
  border: 1px solid var(--ov-mi-border-faint);
  border-radius: var(--ov-mi-radius-panel);
  background: var(--ov-mi-color-surface);
}
.today-panel-head {
  display: flex;
  justify-content: space-between;
  gap: 0.7rem;
  align-items: baseline;
  padding-bottom: 0.48rem;
  border-bottom: 1px solid var(--ov-mi-border-faint);
}
.today-panel-title {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-title);
  font-weight: var(--ov-mi-weight-heading);
}
.today-panel-meta {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
}
.today-evidence-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.today-evidence {
  --evidence-tone: var(--ov-mi-color-neutral);
  min-width: 0;
  padding: 0.68rem 0.72rem;
  border-bottom: 1px solid var(--ov-mi-border-faint);
}
.today-evidence:nth-child(odd) {
  border-right: 1px solid var(--ov-mi-border-faint);
}
.today-evidence:nth-last-child(-n+2) {
  border-bottom: 0;
}
.today-evidence-label {
  color: var(--evidence-tone);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
}
.today-evidence-title {
  margin-top: 0.16rem;
  color: var(--ov-mi-color-text);
  font-size: 0.95rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.22;
  overflow-wrap: anywhere;
}
.today-evidence-detail {
  margin-top: 0.16rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.34;
  overflow-wrap: anywhere;
}
.today-evidence-date {
  margin-top: 0.22rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
}
.today-event {
  padding: 0.68rem 0.12rem 0.72rem;
}
.today-event-date {
  color: var(--ov-mi-color-primary);
  font-size: var(--ov-mi-font-xs);
  font-weight: var(--ov-mi-weight-label);
}
.today-event-title {
  margin-top: 0.2rem;
  color: var(--ov-mi-color-text);
  font-size: 0.96rem;
  font-weight: var(--ov-mi-weight-heading);
  line-height: 1.28;
}
.today-event-detail {
  margin-top: 0.18rem;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
}
.today-watch-list {
  margin: 0.25rem 0 0;
  padding: 0.58rem 0 0 1.05rem;
  border-top: 1px solid var(--ov-mi-border-faint);
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.45;
}
.today-portfolio {
  --today-tone: var(--ov-mi-color-positive);
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.9rem;
  margin: 0 0 0.92rem;
  padding: 0.9rem 1rem;
  border: 1px solid var(--ov-mi-border-faint);
  border-left: 4px solid var(--today-tone);
  border-radius: var(--ov-mi-radius-panel);
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--today-tone) 6%, var(--ov-mi-color-surface)), rgba(255,255,255,0.98)),
    var(--ov-mi-color-surface);
}
.today-portfolio-title {
  margin-top: 0.22rem;
  color: var(--ov-mi-color-text);
  font-size: 1.08rem;
  font-weight: var(--ov-mi-weight-heading);
}
.today-portfolio-summary {
  margin-top: 0.2rem;
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.38;
}
.today-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin-top: 0.72rem;
  border-top: 1px solid var(--ov-mi-border-subtle);
  border-bottom: 1px solid var(--ov-mi-border-subtle);
}
.today-metric {
  min-width: 0;
  padding: 0.56rem 0.55rem;
  border-left: 1px solid var(--ov-mi-border-faint);
}
.today-metric:first-child {
  border-left: 0;
  padding-left: 0;
}
.today-metric-label {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
}
.today-metric-value {
  margin-top: 0.12rem;
  color: var(--ov-mi-color-text);
  font-size: 1rem;
  font-weight: var(--ov-mi-weight-value);
  overflow-wrap: anywhere;
}
.today-metric-value.is-positive { color: var(--ov-mi-color-positive); }
.today-metric-value.is-negative { color: var(--ov-mi-color-danger); }
.today-contributor-section {
  display: grid;
  gap: 0.5rem;
}
.today-detail-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.62rem;
}
.today-contributor-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.5rem;
}
.today-contributor-card {
  display: grid;
  min-width: 0;
  gap: 0.25rem;
  padding: 0.68rem 0.75rem;
  border: 1px solid var(--ov-mi-border-faint);
  border-radius: var(--ov-mi-radius-card);
  background: var(--ov-mi-color-surface);
}
.today-contributor-symbol {
  color: var(--ov-mi-color-text);
  font-size: var(--ov-mi-font-caption);
  font-weight: var(--ov-mi-weight-label);
  overflow-wrap: anywhere;
}
.today-contributor-return-label {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
}
.today-contributor-return {
  color: var(--ov-mi-color-text);
  font-size: 0.94rem;
  font-weight: var(--ov-mi-weight-value);
}
.today-contributor-return.is-unavailable {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-caption);
}
.today-contributor-return.is-positive,
.today-contributor-footer strong.is-positive { color: var(--ov-mi-color-positive); }
.today-contributor-return.is-negative,
.today-contributor-footer strong.is-negative { color: var(--ov-mi-color-danger); }
.today-contributor-footer {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.5rem;
  margin-top: 0.3rem;
  padding-top: 0.42rem;
  border-top: 1px solid var(--ov-mi-border-faint);
}
.today-contributor-footer span {
  min-width: 0;
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  overflow-wrap: anywhere;
}
.today-contributor-footer strong {
  font-size: var(--ov-mi-font-caption);
  white-space: nowrap;
}
.today-contributor-note {
  color: var(--ov-mi-color-text-muted);
  font-size: var(--ov-mi-font-xs);
  line-height: 1.45;
}
.today-portfolio-visual {
  min-width: 0;
}
.today-sparkline {
  min-height: 7.4rem;
  padding: 0.3rem 0.42rem;
  border-bottom: 1px solid var(--ov-mi-border-faint);
  background: color-mix(in srgb, var(--ov-mi-color-surface-subtle) 62%, transparent);
}
.today-sparkline svg { width: 100%; height: 100%; }
.today-portfolio-detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.9rem;
}
.today-portfolio-detail-grid > section {
  display: grid;
  align-content: start;
  min-width: 0;
  gap: 0.5rem;
  padding: 0.75rem;
  border: 1px solid var(--ov-mi-border-faint);
  border-radius: var(--ov-mi-radius-card);
  background: color-mix(in srgb, var(--ov-mi-color-surface) 78%, transparent);
}
.today-review-list {
  display: grid;
  gap: 0.28rem;
}
.today-review-item {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 0.42rem;
  color: var(--ov-mi-color-text-subtle);
  font-size: var(--ov-mi-font-caption);
  line-height: 1.3;
}
.today-review-severity {
  color: var(--ov-mi-color-warning);
  font-weight: var(--ov-mi-weight-label);
}
.today-actions-head {
  margin: 0.1rem 0 0.42rem;
}
@media (max-width: 760px) {
  .today-header,
  .today-context-grid,
  .today-portfolio-detail-grid {
    grid-template-columns: 1fr;
  }
  .today-asof { text-align: left; }
  .today-evidence-grid { grid-template-columns: 1fr; }
  .today-evidence:nth-child(odd) { border-right: 0; }
  .today-evidence:nth-last-child(-n+2) { border-bottom: 1px solid var(--ov-mi-border-faint); }
  .today-evidence:last-child { border-bottom: 0; }
  .today-metrics { grid-template-columns: 1fr; }
  .today-metric,
  .today-metric:first-child {
    padding: 0.48rem 0;
    border-left: 0;
    border-top: 1px solid var(--ov-mi-border-faint);
  }
  .today-metric:first-child { border-top: 0; }
}
@media (max-width: 460px) {
  .today-contributor-grid { grid-template-columns: 1fr; }
}
</style>
"""


def _tone_css(value: Any) -> str:
    return {
        "positive": "var(--ov-mi-color-positive)",
        "warning": "var(--ov-mi-color-warning)",
        "danger": "var(--ov-mi-color-danger)",
        "negative": "var(--ov-mi-color-danger)",
        "primary": "var(--ov-mi-color-primary)",
    }.get(str(value or "").lower(), "var(--ov-mi-color-neutral)")


def _money(value: Any) -> str:
    try:
        return f"${float(value):,.0f}"
    except (TypeError, ValueError):
        return "—"


def _signed_money(value: Any) -> str:
    try:
        numeric = float(value)
        sign = "+" if numeric > 0 else "-" if numeric < 0 else ""
        return f"{sign}${abs(numeric):,.0f}"
    except (TypeError, ValueError):
        return "—"


def _percent(value: Any) -> str:
    try:
        return f"{float(value):+.2%}"
    except (TypeError, ValueError):
        return "—"


def _value_tone(value: Any) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return ""
    return "is-positive" if numeric > 0 else "is-negative" if numeric < 0 else ""


def _sparkline_svg(rows: list[dict[str, Any]]) -> str:
    values: list[float] = []
    for row in rows:
        try:
            value = row.get("cumulative_return", row.get("value"))
            values.append(float(value))
        except (TypeError, ValueError):
            continue
    if len(values) < 2:
        return '<div class="today-event-detail">표시할 가치곡선이 아직 없습니다.</div>'
    low, high = min(values), max(values)
    span = high - low or 1.0
    step = 100.0 / max(len(values) - 1, 1)
    points = " ".join(
        f"{index * step:.2f},{92.0 - ((value - low) / span) * 78.0:.2f}"
        for index, value in enumerate(values)
    )
    return (
        '<svg viewBox="0 0 100 100" preserveAspectRatio="none" role="img" '
        'aria-label="대표 포트폴리오 가치곡선">'
        '<line x1="0" x2="100" y1="92" y2="92" stroke="var(--ov-mi-border-subtle)" stroke-width="0.7" />'
        f'<polyline points="{points}" fill="none" stroke="var(--ov-mi-color-primary)" '
        'stroke-width="2" vector-effect="non-scaling-stroke" />'
        "</svg>"
    )


def build_today_html(model: dict[str, Any]) -> str:
    """Build escaped Today markup in the approved B information order."""

    header = dict(model.get("header") or {})
    market = dict(model.get("market") or {})
    portfolio = dict(model.get("portfolio") or {})
    evidence_html: list[str] = []
    for row in list(market.get("evidence") or []):
        evidence = dict(row or {})
        evidence_html.append(
            '<div class="today-evidence" '
            f'style="--evidence-tone:{_tone_css(evidence.get("tone"))};">'
            f'<div class="today-evidence-label">{escape(str(evidence.get("label") or "-"))}</div>'
            f'<div class="today-evidence-title">{escape(str(evidence.get("title") or "-"))}</div>'
            f'<div class="today-evidence-detail">{escape(str(evidence.get("detail") or "-"))}</div>'
            f'<div class="today-evidence-date">기준 {escape(str(evidence.get("as_of_date") or "-"))}</div>'
            "</div>"
        )
    event = dict(market.get("next_event") or {})
    event_html = (
        '<div class="today-event">'
        f'<div class="today-event-date">{escape(str(event.get("date") or "-"))} · D-{escape(str(event.get("days_until") or 0))}</div>'
        f'<div class="today-event-title">{escape(str(event.get("title") or "예정된 주요 일정 없음"))}</div>'
        f'<div class="today-event-detail">{escape(str(event.get("type") or "EVENT"))} · {escape(str(event.get("importance") or "-"))}</div>'
        "</div>"
    )
    watch_items = [str(value) for value in market.get("watch_items") or [] if str(value).strip()]
    watch_html = (
        '<ul class="today-watch-list">'
        + "".join(f"<li>{escape(value)}</li>" for value in watch_items)
        + "</ul>"
        if watch_items
        else '<div class="today-event-detail">추가 제한 사항이 없습니다.</div>'
    )
    metrics = dict(portfolio.get("metrics") or {})
    latest_return = metrics.get(
        "latest_observation_return",
        metrics.get("day_return"),
    )
    contributors = [dict(row or {}) for row in portfolio.get("contributors") or []]
    contributor_cards: list[str] = []
    for row in contributors:
        contribution = row.get("contribution_value", row.get("value"))
        total_return = row.get("total_return")
        return_html = (
            f'<strong class="today-contributor-return {_value_tone(total_return)}">'
            f'{escape(_percent(total_return))}</strong>'
            if total_return is not None
            else '<strong class="today-contributor-return is-unavailable">수익률 자료 부족</strong>'
        )
        contributor_cards.append(
            '<article class="today-contributor-card">'
            f'<div class="today-contributor-symbol">{escape(str(row.get("symbol") or "-"))}</div>'
            '<div class="today-contributor-return-label">종목 누적 수익률</div>'
            f'{return_html}'
            '<div class="today-contributor-footer">'
            '<span>포트폴리오 누적 기여</span>'
            f'<strong class="{_value_tone(contribution)}">{escape(_signed_money(contribution))}</strong>'
            '</div>'
            '</article>'
        )
    contributor_html = (
        "".join(contributor_cards)
        or '<div class="today-event-detail">기여 계산 자료가 없습니다.</div>'
    )
    review_rows = [dict(row or {}) for row in portfolio.get("review_items") or []]
    review_html = (
        "".join(
            '<div class="today-review-item">'
            f'<span class="today-review-severity">{escape(str(row.get("severity") or "INFO"))}</span>'
            f'<span>{escape(str(row.get("meaning") or "확인할 항목이 있습니다."))}</span>'
            "</div>"
            for row in review_rows
        )
        or '<div class="today-event-detail">현재 우선 확인 항목이 없습니다.</div>'
    )
    return f"""
<div class="today-shell">
  <section class="today-header">
    <div>
      <div class="today-kicker">TODAY · MARKET &amp; PORTFOLIO</div>
      <h1 class="today-title">오늘의 시장 판단</h1>
      <div class="today-subtitle">저장된 시장 근거와 대표 포트폴리오의 영향을 한 흐름에서 확인합니다.</div>
    </div>
    <div class="today-asof" style="--today-tone:{_tone_css(market.get('tone'))};">
      <span class="today-badge">{escape(str(header.get('status_label') or '자료 상태 확인'))} · {escape(str(header.get('source_ready_count') or 0))}/{escape(str(header.get('source_count') or 5))}</span>
      <div class="today-asof-date">기준 {escape(str(header.get('as_of_date') or '-'))}</div>
    </div>
  </section>

  <section class="today-market-brief" style="--today-tone:{_tone_css(market.get('tone'))};">
    <div class="today-brief-label">MARKET VIEW · 저장 근거 종합</div>
    <div class="today-brief-headline">{escape(str(market.get('headline') or '현재 자료로 종합 판단 보류'))}</div>
    <div class="today-brief-summary">{escape(str(market.get('summary') or '시장 근거를 확인합니다.'))}</div>
  </section>

  <section class="today-context-grid">
    <div class="today-panel">
      <div class="today-panel-head"><span class="today-panel-title">판단 근거</span><span class="today-panel-meta">기존 Research 저장 결과</span></div>
      <div class="today-evidence-grid">{''.join(evidence_html)}</div>
    </div>
    <div class="today-panel">
      <div class="today-panel-head"><span class="today-panel-title">다음 일정 · 주의</span><span class="today-panel-meta">최대 3건</span></div>
      {event_html}
      {watch_html}
    </div>
  </section>

  <section class="today-portfolio" style="--today-tone:{_tone_css('positive' if portfolio.get('status') == 'READY' else 'warning')};">
    <div>
      <div class="today-section-kicker">대표 포트폴리오 · 저장 가격 기준</div>
      <div class="today-portfolio-title">{escape(str(portfolio.get('name') or '대표 포트폴리오'))}</div>
      <div class="today-portfolio-summary">{escape(str(portfolio.get('summary') or '평가 결과를 확인합니다.'))} · 기준 {escape(str(portfolio.get('basis_date') or '-'))}</div>
      <div class="today-metrics">
        <div class="today-metric"><div class="today-metric-label">평가액</div><div class="today-metric-value">{escape(_money(metrics.get('current_value')))}</div></div>
        <div class="today-metric"><div class="today-metric-label">최근 거래일</div><div class="today-metric-value {_value_tone(latest_return)}">{escape(_percent(latest_return))}</div></div>
        <div class="today-metric"><div class="today-metric-label">누적</div><div class="today-metric-value {_value_tone(metrics.get('total_return'))}">{escape(_percent(metrics.get('total_return')))}</div></div>
      </div>
    </div>
    <div class="today-portfolio-visual">
      <div class="today-sparkline">{_sparkline_svg(list(portfolio.get('curve') or []))}</div>
    </div>
    <div class="today-portfolio-detail-grid">
      <section class="today-contributor-section">
        <div class="today-detail-heading">
          <span class="today-panel-meta">종목별 성과 기여</span>
          <span class="today-panel-meta">기여 상위 2 · 하위 2</span>
        </div>
        <div class="today-contributor-grid">{contributor_html}</div>
        <div class="today-contributor-note">
          종목 수익률은 입출금 영향을 조정한 누적 성과 · 기준 {escape(str(portfolio.get('basis_date') or '-'))}
        </div>
      </section>
      <section class="today-review-section">
        <div class="today-detail-heading">
          <span class="today-panel-meta">우선 확인</span>
        </div>
        <div class="today-review-list">{review_html}</div>
      </section>
    </div>
  </section>

  <div class="today-actions-head"><div class="today-section-kicker">다음 확인</div></div>
</div>
"""


def _render_action_links() -> None:
    links = (
        ("market_research", "시장 근거 자세히 보기", {OVERVIEW_DEEP_TAB_QUERY_PARAM: "market-context"}),
        ("stock_research", "영향이 큰 종목 조사", {OVERVIEW_DEEP_TAB_QUERY_PARAM: "market-movers"}),
        ("portfolio_monitoring", "포트폴리오 전체 점검", None),
    )
    columns = st.columns(3, gap="small")
    for column, (key, label, query_params) in zip(columns, links):
        target = _TODAY_PAGE_TARGETS.get(key)
        with column:
            if target is None:
                st.caption(f"{label} · 연결 준비 중")
                continue
            options: dict[str, Any] = {"label": label}
            if query_params:
                options["query_params"] = query_params
            st.page_link(target, **options)


def _normalize_today_event(value: object) -> dict[str, str] | None:
    if not isinstance(value, dict):
        return None
    event = value.get("event")
    if not isinstance(event, dict):
        return None
    event_id = str(event.get("id") or "").strip()
    if event_id not in _TODAY_EVENT_ROUTES:
        return None
    return {"id": event_id}


def _render_today_fallback(model: dict[str, object]) -> None:
    st.error(
        "Today React 화면을 불러오지 못했습니다. "
        "배포된 화면 빌드를 확인해 주세요."
    )
    st.markdown(
        overview_ui_css() + _today_css() + build_today_html(model),
        unsafe_allow_html=True,
    )
    _render_action_links()


def _route_today_event(event: dict[str, str]) -> None:
    target_key, query_params = _TODAY_EVENT_ROUTES[event["id"]]
    target = _TODAY_PAGE_TARGETS.get(target_key)
    if target is None:
        st.warning("연결할 기존 화면이 아직 준비되지 않았습니다.")
        return
    if query_params:
        st.switch_page(target, query_params=query_params)
        return
    st.switch_page(target)


def _load_today_portfolio_context() -> TodayPortfolioRuntimeContext:
    try:
        return load_default_portfolio_monitoring_context_for_today()
    except Exception:  # pragma: no cover - actual UI resilience
        return TodayPortfolioRuntimeContext(
            group=None,
            items=(),
            workspace={
                "status": "ERROR",
                "reason": "대표 포트폴리오 저장 자료를 불러오지 못했습니다.",
            },
        )


def should_run_today_portfolio_heartbeat(
    session: RegularSessionState,
    coordinator_state: CoordinatorSnapshot,
) -> bool:
    """Keep periodic runs only while the portfolio DB state can change."""

    if session.phase == "OPEN" and session.collection_allowed:
        return True
    return (
        session.phase == "CLOSED"
        and coordinator_state.eod_state in {"waiting", "running"}
    )


def _handle_today_component_value(
    component_value: dict[str, Any] | None,
    model: dict[str, object],
) -> None:
    if component_value is None:
        _render_today_fallback(model)
        return
    event = _normalize_today_event(component_value)
    if component_value.get("event") is not None and event is None:
        st.warning("지원하지 않는 Today 화면 동작은 실행하지 않았습니다.")
        return
    if event is not None:
        _route_today_event(event)


def _render_today_dynamic_body(
    *,
    generated_at: datetime | None = None,
) -> None:
    timestamp = generated_at or datetime.now(timezone.utc)
    context = _load_today_portfolio_context()
    model = load_today_read_model(
        generated_at=timestamp,
        portfolio_workspace=context.workspace,
    )
    if context.group is not None:
        try:
            scope = build_intraday_refresh_scope(
                context.group,
                context.items,
            )
            session = resolve_regular_session_state(
                model.get("market_session") or {},
                timestamp,
            )
            latest_daily_dates = (
                load_latest_daily_dates(scope, end=session.trade_date)
                if session.phase == "CLOSED"
                else {}
            )
            coordinator_state = get_today_intraday_coordinator().tick(
                scope=scope,
                session=session,
                now=timestamp,
                latest_daily_dates=latest_daily_dates,
            )
            if session.collection_allowed:
                quotes = load_latest_portfolio_quotes(scope, now=timestamp)
                eod_closes = load_workspace_eod_closes(
                    workspace=context.workspace,
                    scope=scope,
                )
                overlay = build_live_portfolio_overlay(
                    workspace=context.workspace,
                    scope=scope,
                    quotes=quotes,
                    eod_closes=eod_closes,
                    now=timestamp,
                )
                model["portfolio"]["live"] = project_today_portfolio_live(
                    overlay
                )
            elif coordinator_state.eod_state in {
                "waiting",
                "running",
                "exhausted",
            }:
                missing = list(coordinator_state.eod_missing_symbols)
                model["portfolio"]["live"] = project_today_portfolio_live(
                    {
                        "status": "EOD_WAITING",
                        "trade_date": (
                            session.trade_date.isoformat()
                            if session.trade_date is not None
                            else None
                        ),
                        "coverage": {
                            "fresh": max(len(scope.symbols) - len(missing), 0),
                            "expected": len(scope.symbols),
                        },
                        "fallback_symbols": missing,
                    }
                )
        except Exception:
            pass  # EOD Today remains available when live refresh is unavailable.

    if not today_react_component_available():
        _render_today_fallback(model)
        return

    component_value = render_today_workbench(
        model,
        key="today_workbench",
    )
    _handle_today_component_value(component_value, model)


@st.fragment(run_every=15)
def _render_today_dynamic_fragment() -> None:
    _render_today_dynamic_body()


def render_today_page() -> None:
    """Render the default market-and-portfolio landing fragment."""

    if get_script_run_ctx(suppress_warning=True) is None:
        _render_today_dynamic_body()
        return
    _render_today_dynamic_fragment()


__all__ = [
    "build_today_html",
    "configure_today_page_targets",
    "load_today_read_model",
    "render_today_page",
]
