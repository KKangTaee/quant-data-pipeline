from __future__ import annotations

import json
from html import escape
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from app.web.overview.components.common import *


def _market_movers_workbench_tone(value: Any) -> str:
    return escape(_overview_tone_color(value))


def _command_strip_items_html(items: list[dict[str, Any]]) -> str:
    item_html: list[str] = []
    for item in items:
        detail = item.get("detail")
        detail_html = (
            f'<div class="ov-mm-command-detail">{escape(_display_value(detail))}</div>'
            if detail not in (None, "")
            else ""
        )
        item_html.append(
            '<div class="ov-mm-command-item">'
            f'<div class="ov-mm-command-label">{escape(_display_value(item.get("label")))}</div>'
            f'<div class="ov-mm-command-value">{escape(_display_value(item.get("value")))}</div>'
            f"{detail_html}"
            "</div>"
        )
    return "".join(item_html)


def render_market_movers_command_strip(model: dict[str, Any]) -> None:
    tone_color = _market_movers_workbench_tone(model.get("tone"))
    st.markdown(
        overview_ui_css()
        + f"""
<section class="ov-mm-command" style="--ov-command-tone:{tone_color};">
  <div class="ov-mm-command-head">
    <div>
      <div class="ov-mm-command-kicker">Market Movers</div>
      <div class="ov-mm-command-title">{escape(_display_value(model.get("headline")))}</div>
      <div class="ov-mm-command-context">{escape(_display_value(model.get("context")))}</div>
    </div>
    <span class="ov-mm-command-badge">{escape(_display_value(model.get("status_label")))}</span>
  </div>
  <div class="ov-mm-command-grid">{_command_strip_items_html(list(model.get("items") or []))}</div>
</section>""",
        unsafe_allow_html=True,
    )


def render_market_movers_empty_state(model: dict[str, Any]) -> None:
    tone_color = _market_movers_workbench_tone(model.get("tone"))
    st.markdown(
        overview_ui_css()
        + f"""
<section class="ov-mm-empty-state" style="--ov-empty-tone:{tone_color};">
  <div>
    <div class="ov-mm-empty-kicker">현재 선택 조건</div>
    <div class="ov-mm-empty-title">{escape(_display_value(model.get("title")))}</div>
    <div class="ov-mm-empty-detail">{escape(_display_value(model.get("detail")))}</div>
  </div>
  <div class="ov-mm-empty-action">
    <span>{escape(_display_value(model.get("primary_action")))}</span>
    <small>{escape(_display_value(model.get("investigation_note")))}</small>
  </div>
</section>""",
        unsafe_allow_html=True,
    )


def _market_mover_board_rows_html(rows: list[dict[str, Any]]) -> str:
    html: list[str] = []
    for row in rows:
        tone_color = escape(_overview_tone_color(row.get("tone")))
        secondary = _display_value(row.get("secondary"))
        secondary_html = (
            f'<div class="ov-mm-list-secondary">{escape(secondary)}</div>'
            if secondary not in ("", "-")
            else ""
        )
        html.append(
            f'<article class="ov-mm-list-row" style="--ov-row-tone:{tone_color};">'
            f'<div class="ov-mm-list-rank">#{escape(_display_value(row.get("rank")))}</div>'
            '<div class="ov-mm-list-identity">'
            f'<div class="ov-mm-list-symbol">{escape(_display_value(row.get("symbol")))}</div>'
            f'<div class="ov-mm-list-name">{escape(_display_value(row.get("name")))}</div>'
            "</div>"
            f'<div class="ov-mm-list-sector">{escape(_display_value(row.get("sector")))}</div>'
            '<div class="ov-mm-list-metric">'
            f'<span>{escape(_display_value(row.get("primary_metric_label")))}</span>'
            f'<strong>{escape(_display_value(row.get("primary_metric")))}</strong>'
            f"{secondary_html}"
            "</div>"
            "</article>"
        )
    return "".join(html)


def _market_mover_tape_html(rows: list[dict[str, Any]]) -> str:
    html: list[str] = []
    for row in rows[:5]:
        tone_color = escape(_overview_tone_color(row.get("tone")))
        html.append(
            f'<div class="ov-mm-tape-cell" style="--ov-tape-tone:{tone_color};">'
            f'<div class="ov-mm-tape-rank">#{escape(_display_value(row.get("rank")))}</div>'
            f'<div class="ov-mm-tape-symbol">{escape(_display_value(row.get("symbol")))}</div>'
            f'<div class="ov-mm-tape-value">{escape(_display_value(row.get("primary_metric")))}</div>'
            f'<div class="ov-mm-tape-detail">{escape(_display_value(row.get("sector")))}</div>'
            "</div>"
        )
    return "".join(html)


def render_market_mover_board(model: dict[str, Any]) -> None:
    rows = list(model.get("rows") or [])
    if not rows:
        return
    st.markdown(
        overview_ui_css()
        + f"""
<section class="ov-mm-board">
  <div class="ov-mm-board-head">
    <div>
      <div class="ov-mm-board-kicker">Ranking Board</div>
      <div class="ov-mm-board-title">{escape(_display_value(model.get("title")))}</div>
      <div class="ov-mm-board-detail">{escape(_display_value(model.get("subtitle")))}</div>
    </div>
    <span class="ov-mm-board-count">{escape(_display_value(dict(model.get("summary") or {}).get("count")))} rows</span>
  </div>
  <div class="ov-mm-tape">{_market_mover_tape_html(rows)}</div>
  <div class="ov-mm-list">{_market_mover_board_rows_html(rows)}</div>
  <div class="ov-mm-board-boundary">{escape(_display_value(model.get("boundary_note")))}</div>
</section>""",
        unsafe_allow_html=True,
    )


def _market_mover_chart_facts_html(facts: list[dict[str, Any]]) -> str:
    html: list[str] = []
    for item in facts:
        detail = item.get("detail")
        detail_html = (
            f'<div class="ov-mm-chart-fact-detail">{escape(_display_value(detail))}</div>'
            if detail not in (None, "")
            else ""
        )
        html.append(
            '<div class="ov-mm-chart-fact">'
            f'<div class="ov-mm-chart-fact-label">{escape(_display_value(item.get("label")))}</div>'
            f'<div class="ov-mm-chart-fact-value">{escape(_display_value(item.get("value")))}</div>'
            f"{detail_html}"
            "</div>"
        )
    return "".join(html)


def render_market_mover_chart_workspace(model: dict[str, Any]) -> None:
    st.markdown(
        overview_ui_css()
        + f"""
<section class="ov-mm-chart-workspace">
  <div class="ov-mm-chart-head">
    <div>
      <div class="ov-mm-chart-kicker">{escape(_display_value(model.get("kicker")))}</div>
      <div class="ov-mm-chart-title">{escape(_display_value(model.get("title")))}</div>
      <div class="ov-mm-chart-detail">{escape(_display_value(model.get("subtitle")))}</div>
    </div>
    <span class="ov-mm-chart-badge">{escape(_display_value(model.get("metric_label")))}</span>
  </div>
  <div class="ov-mm-chart-facts">{_market_mover_chart_facts_html(list(model.get("facts") or []))}</div>
</section>""",
        unsafe_allow_html=True,
    )

def _coverage_trust_items_html(items: list[dict[str, Any]]) -> str:
    html: list[str] = []
    for item in items:
        detail = item.get("detail")
        detail_html = (
            f'<div class="ov-mm-trust-detail-small">{escape(_display_value(detail))}</div>'
            if detail not in (None, "")
            else ""
        )
        html.append(
            '<div class="ov-mm-trust-item">'
            f'<div class="ov-mm-trust-label">{escape(_display_value(item.get("label")))}</div>'
            f'<div class="ov-mm-trust-value">{escape(_display_value(item.get("value")))}</div>'
            f"{detail_html}"
            "</div>"
        )
    return "".join(html)


def render_market_movers_coverage_trust(model: dict[str, Any]) -> None:
    tone_color = _market_movers_workbench_tone(model.get("tone"))
    action = dict(model.get("suggested_action") or {})
    st.markdown(
        overview_ui_css()
        + f"""
<section class="ov-mm-trust" style="--ov-trust-tone:{tone_color};">
  <div class="ov-mm-trust-head">
    <div>
      <div class="ov-mm-trust-kicker">Coverage Trust</div>
      <div class="ov-mm-trust-title">자료 신뢰 상태: {escape(_display_value(model.get("state")))}</div>
      <div class="ov-mm-trust-detail">{escape(_display_value(model.get("headline")))} · {escape(_display_value(model.get("detail")))}</div>
    </div>
    <span class="ov-mm-trust-action">{escape(_display_value(action.get("label")))}</span>
  </div>
  <div class="ov-mm-trust-grid">{_coverage_trust_items_html(list(model.get("items") or []))}</div>
  <div class="ov-mm-trust-boundary">{escape(_display_value(model.get("boundary_note")))}</div>
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
        decliners = _display_value(row.get("decliners"))
        top_symbol = _display_value(row.get("top_symbol"))
        top_return = _display_value(row.get("top_symbol_return_pct"))
        top_loser = _display_value(row.get("top_loser"))
        top_loser_return = _display_value(row.get("top_loser_return_pct"))
        html.append(
            f'<div class="ov-breadth-row" style="--ov-row-tone:{tone_color};">'
            f'<div class="ov-breadth-row-label">#{escape(_display_value(row.get("rank")))} · {escape(group)}</div>'
            f'<div class="ov-breadth-row-value">{escape(weighted)}%</div>'
            "<div class=\"ov-breadth-row-detail\">"
            f"{escape(positive)}% positive · Decliners {escape(decliners)}"
            f" · {escape(top_symbol)} {escape(top_return)}%"
            f" / Top Loser {escape(top_loser)} {escape(top_loser_return)}%"
            "</div>"
            "</div>"
        )
    return "".join(html)


def _sector_breadth_heatmap_html(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    tiles: list[str] = []
    for row in rows:
        tone_color = escape(_overview_tone_color(row.get("tone")))
        group = _display_value(row.get("group"))
        weighted = _display_value(row.get("market_cap_weighted_return_pct"))
        advancers = _display_value(row.get("advancers"))
        decliners = _display_value(row.get("decliners"))
        size_share = _display_value(row.get("market_cap_share_pct"))
        tiles.append(
            f'<div class="ov-sector-pressure-tile" style="--ov-pressure-tone:{tone_color};">'
            f'<div class="ov-sector-pressure-name">{escape(group)}</div>'
            f'<div class="ov-sector-pressure-value">{escape(weighted)}%</div>'
            f'<div class="ov-sector-pressure-detail">{escape(advancers)} adv / {escape(decliners)} dec · {escape(size_share)}% cap</div>'
            "</div>"
        )
    return f'<div class="ov-sector-pressure-map">{"".join(tiles)}</div>'


def _sector_breadth_stat_html(item: dict[str, Any]) -> str:
    return (
        '<div class="ov-sector-breadth-stat">'
        f'<span class="ov-sector-breadth-stat-label">{escape(_display_value(item.get("label")))}</span>'
        f'<strong>{escape(_display_value(item.get("value")))}</strong>'
        f'<span>{escape(_display_value(item.get("detail")))}</span>'
        "</div>"
    )


def _sector_breadth_lanes_html(lanes: list[dict[str, Any]]) -> str:
    html: list[str] = []
    for lane in lanes:
        tone_color = escape(_overview_tone_color(lane.get("tone")))
        direction = "negative" if str(lane.get("direction") or "") == "negative" else "positive"
        bar_width = escape(_display_value(lane.get("bar_width_pct")))
        html.append(
            f'<div class="ov-sector-breadth-lane" style="--ov-lane-tone:{tone_color};--ov-lane-bar:{bar_width}%;">'
            '<div class="ov-sector-breadth-lane-head">'
            f'<span>#{escape(_display_value(lane.get("rank")))} · {escape(_display_value(lane.get("sector")))}</span>'
            f'<strong>{escape(_display_value(lane.get("return_label")))}</strong>'
            "</div>"
            '<div class="ov-sector-breadth-lane-track">'
            '<span class="ov-sector-breadth-zero"></span>'
            f'<span class="ov-sector-breadth-bar ov-sector-breadth-bar--{direction}"></span>'
            "</div>"
            '<div class="ov-sector-breadth-lane-detail">'
            f'{escape(_display_value(lane.get("participation_detail")))} · {escape(_display_value(lane.get("cap_detail")))}'
            "</div>"
            '<div class="ov-sector-breadth-lane-foot">'
            f'{escape(_display_value(lane.get("top_gainer_detail")))} / {escape(_display_value(lane.get("top_loser_detail")))}'
            "</div>"
            "</div>"
        )
    return "".join(html)


def _sector_breadth_leader_strip_html(leaders: list[dict[str, Any]]) -> str:
    html: list[str] = []
    for item in leaders:
        tone_color = escape(_overview_tone_color(item.get("tone")))
        html.append(
            f'<div class="ov-sector-breadth-leader" style="--ov-leader-tone:{tone_color};">'
            f'<span>{escape(_display_value(item.get("rank")))} · {escape(_display_value(item.get("sector")))}</span>'
            f'<strong>{escape(_display_value(item.get("return_label")))}</strong>'
            f'<small>{escape(_display_value(item.get("participation_label")))}</small>'
            "</div>"
        )
    return "".join(html)


def render_sector_breadth_market_map(model: dict[str, Any]) -> None:
    tone_color = escape(_overview_tone_color(model.get("status")))
    stats = [
        dict(model.get("participation") or {}),
        dict(model.get("leadership") or {}),
        dict(model.get("dispersion") or {}),
    ]
    stats_html = "".join(_sector_breadth_stat_html(item) for item in stats if item)
    lanes_html = _sector_breadth_lanes_html(list(model.get("lanes") or []))
    leaders_html = _sector_breadth_leader_strip_html(list(model.get("leaders") or []))
    rail_pct = escape(_display_value(dict(model.get("participation") or {}).get("rail_pct") or 0))
    st.markdown(
        overview_ui_css()
        + f"""
<section class="ov-sector-breadth-map" style="--ov-band-tone:{tone_color};--ov-rail-fill:{rail_pct}%;">
  <div class="ov-sector-breadth-head">
    <div>
      <div class="ov-sector-breadth-kicker">시장 확산 지도</div>
      <div class="ov-sector-breadth-title">{escape(_display_value(model.get("headline")))}</div>
      <div class="ov-sector-breadth-detail">{escape(_display_value(model.get("detail")))} · Freshness: {escape(_display_value(model.get("freshness")))}</div>
    </div>
    <span class="ov-sector-breadth-status">{escape(_display_value(model.get("status")))}</span>
  </div>
  <div class="ov-sector-breadth-rail">
    <span class="ov-sector-breadth-rail-fill"></span>
  </div>
  <div class="ov-sector-breadth-stats">{stats_html}</div>
  <div class="ov-sector-breadth-lanes">{lanes_html}</div>
  <div class="ov-sector-breadth-leader-strip">{leaders_html}</div>
  <div class="ov-sector-breadth-boundary">{escape(_display_value(model.get("boundary_note")))}</div>
</section>""",
        unsafe_allow_html=True,
    )


def render_breadth_heatmap_summary(model: dict[str, Any]) -> None:
    summary = dict(model.get("summary") or {})
    tone_color = escape(_overview_tone_color(model.get("status")))
    cards_html = _breadth_summary_cards_html(list(model.get("cards") or []))
    heatmap_rows = list(model.get("heatmap_rows") or [])
    heatmap_html = _sector_breadth_heatmap_html(heatmap_rows)
    rows_html = _breadth_rows_html(heatmap_rows)
    coverage = dict(model.get("coverage") or {})
    freshness = _display_value(coverage.get("freshness"))
    st.markdown(
        overview_ui_css()
        + f"""
<section class="ov-breadth-summary" style="--ov-band-tone:{tone_color};">
  <div class="ov-breadth-head">
    <div>
      <div class="ov-breadth-kicker">Sector Breadth / Heatmap</div>
      <div class="ov-breadth-title">{escape(_display_value(summary.get("headline")))}</div>
      <div class="ov-breadth-detail">{escape(_display_value(summary.get("detail")))} · Freshness: {escape(freshness)}</div>
    </div>
    <span class="ov-breadth-status">{escape(_display_value(model.get("status")))}</span>
  </div>
  <div class="ov-breadth-card-grid">{cards_html}</div>
  {heatmap_html}
  <div class="ov-breadth-row-grid">{rows_html}</div>
  <div class="ov-breadth-boundary">{escape(_display_value(model.get("boundary_note")))}</div>
</section>""",
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

__all__ = [
    "_breadth_summary_cards_html",
    "_breadth_rows_html",
    "_coverage_trust_items_html",
    "render_breadth_heatmap_summary",
    "render_sector_breadth_market_map",
    "render_market_movers_coverage_trust",
    "render_market_movers_command_strip",
    "render_market_movers_empty_state",
    "render_market_mover_board",
    "render_market_mover_chart_workspace",
    "_market_refresh_state_label",
    "_market_refresh_state_detail",
    "render_market_refresh_status_bar",
    "render_market_auto_message",
    "render_market_auto_waiting_panel",
    "render_auto_refresh_timing_static",
    "render_auto_refresh_countdown",
]
