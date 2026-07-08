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


def _unified_summary_items_html(items: list[dict[str, Any]]) -> str:
    item_html: list[str] = []
    for item in items:
        detail = item.get("detail")
        detail_html = (
            f'<div class="ov-mm-unified-detail">{escape(_display_value(detail))}</div>'
            if detail not in (None, "")
            else ""
        )
        item_html.append(
            '<div class="ov-mm-unified-item">'
            f'<div class="ov-mm-unified-label">{escape(_display_value(item.get("label")))}</div>'
            f'<div class="ov-mm-unified-value">{escape(_display_value(item.get("value")))}</div>'
            f"{detail_html}"
            "</div>"
        )
    return "".join(item_html)


def render_market_movers_unified_summary(model: dict[str, Any]) -> None:
    tone_color = _market_movers_workbench_tone(model.get("tone"))
    trust_detail = _display_value(model.get("trust_detail"))
    trust_detail_html = f"<small>{escape(trust_detail)}</small>" if trust_detail not in ("", "-") else ""
    action = _display_value(model.get("action_label"))
    action_html = f'<span class="ov-mm-unified-action">{escape(action)}</span>' if action not in ("", "-") else ""
    st.markdown(
        overview_ui_css()
        + f"""
<section class="ov-mm-unified-summary" style="--ov-summary-tone:{tone_color};">
  <div class="ov-mm-unified-head">
    <div>
      <div class="ov-mm-unified-kicker">Market Movers</div>
      <div class="ov-mm-unified-title">{escape(_display_value(model.get("title")))}</div>
      <div class="ov-mm-unified-context">{escape(_display_value(model.get("context")))}</div>
    </div>
    <div class="ov-mm-unified-trust">
      <span>자료 상태</span>
      <strong>{escape(_display_value(model.get("trust_state")))}</strong>
      {trust_detail_html}
      {action_html}
    </div>
  </div>
  <div class="ov-mm-unified-grid">{_unified_summary_items_html(list(model.get("items") or []))}</div>
</section>""",
        unsafe_allow_html=True,
    )


def render_market_movers_empty_state(model: dict[str, Any]) -> None:
    tone_color = _market_movers_workbench_tone(model.get("tone"))
    trust_hint = dict(model.get("trust_hint") or {})
    trust_hint_html = ""
    if trust_hint:
        trust_hint_html = (
            '<div class="ov-mm-empty-trust">'
            f'<span>{escape(_display_value(trust_hint.get("label")))}</span>'
            f'<strong>{escape(_display_value(trust_hint.get("value")))}</strong>'
            f'<small>{escape(_display_value(trust_hint.get("detail")))}</small>'
            "</div>"
        )
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
  {trust_hint_html}
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


def render_market_movers_section_divider(title: str, detail: str | None = None) -> None:
    detail_html = ""
    if detail:
        detail_html = f'<span class="ov-mm-section-detail">{escape(_display_value(detail))}</span>'
    st.markdown(
        overview_ui_css()
        + f"""
<div class="ov-mm-section-divider">
  <span class="ov-mm-section-label">{escape(_display_value(title))}</span>
  {detail_html}
</div>""",
        unsafe_allow_html=True,
    )


def _market_mover_investigation_facts_html(facts: list[dict[str, Any]]) -> str:
    html: list[str] = []
    for item in facts:
        html.append(
            '<div class="ov-mm-investigation-fact">'
            f'<span>{escape(_display_value(item.get("label")))}</span>'
            f'<strong>{escape(_display_value(item.get("value")))}</strong>'
            f'<small>{escape(_display_value(item.get("detail")))}</small>'
            "</div>"
        )
    return "".join(html)


def _market_mover_investigation_status_html(items: list[dict[str, Any]]) -> str:
    html: list[str] = []
    for item in items:
        tone_color = escape(_overview_tone_color(item.get("tone")))
        html.append(
            f'<span class="ov-mm-investigation-status-item" style="--ov-status-tone:{tone_color};">'
            f'{escape(_display_value(item.get("label")))} · {escape(_display_value(item.get("value")))}'
            "</span>"
        )
    return "".join(html)


def render_market_mover_investigation_pane(model: dict[str, Any]) -> None:
    status_items_html = _market_mover_investigation_status_html(list(model.get("status_items") or []))
    st.markdown(
        overview_ui_css()
        + f"""
<section class="ov-mm-investigation-pane">
  <div class="ov-mm-investigation-head">
    <div>
      <div class="ov-mm-investigation-kicker">수동 조사 패널</div>
      <div class="ov-mm-investigation-title">{escape(_display_value(model.get("title")))}</div>
      <div class="ov-mm-investigation-subtitle">{escape(_display_value(model.get("subtitle")))}</div>
    </div>
    <span class="ov-mm-investigation-rank">{escape(_display_value(model.get("rank_badge")))}</span>
  </div>
  <div class="ov-mm-investigation-facts">{_market_mover_investigation_facts_html(list(model.get("facts") or []))}</div>
  <div class="ov-mm-investigation-status">{status_items_html}</div>
  <div class="ov-mm-investigation-boundary">{escape(_display_value(model.get("boundary_note")))}</div>
</section>""",
        unsafe_allow_html=True,
    )


def _market_mover_research_rows_html(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    is_income = any("net_income" in row for row in rows)
    if is_income:
        table_class = "ov-mm-research-table is-income"
        table_label = "annual and quarterly net income comparison"
        columns = [
            ("period", "구분", True),
            ("period_end", "회계기간", False),
            ("disclosure_date", "공시일", False),
            ("net_income", "당기순이익", False),
        ]
    else:
        table_class = "ov-mm-research-table is-per-eps"
        table_label = "PER EPS annual and quarterly comparison"
        columns = [
            ("period", "구분", True),
            ("period_end", "회계기간", False),
            ("disclosure_date", "공시일", False),
            ("per", "PER", False),
            ("eps", "EPS", False),
        ]
    html = [
        f'<div class="{table_class}" role="table" aria-label="{table_label}">',
        '<div class="ov-mm-research-table-row is-head" role="row">',
        "".join(f'<span role="columnheader">{escape(label)}</span>' for _, label, _ in columns),
        "</div>",
    ]
    for row in rows:
        cells: list[str] = []
        for key, _, strong in columns:
            value = escape(_display_value(row.get(key)))
            tag = "strong" if strong else "span"
            cells.append(f'<{tag} role="cell">{value}</{tag}>')
        html.append(
            '<div class="ov-mm-research-table-row" role="row">'
            f"{''.join(cells)}"
            "</div>"
        )
    html.append("</div>")
    return "".join(html)


def _market_mover_research_items_html(items: list[dict[str, Any]]) -> str:
    html: list[str] = []
    for item in items:
        tone_color = escape(_overview_tone_color(item.get("tone")))
        state_class = "is-available" if item.get("available") else "is-unavailable"
        rows = [dict(row) for row in list(item.get("rows") or []) if isinstance(row, dict)]
        row_class = " has-rows" if rows else ""
        html.append(
            f'<article class="ov-mm-research-item {state_class}{row_class}" style="--ov-research-tone:{tone_color};">'
            f'<div class="ov-mm-research-label">{escape(_display_value(item.get("label")))}</div>'
            f'<div class="ov-mm-research-value">{escape(_display_value(item.get("value")))}</div>'
            f"{_market_mover_research_rows_html(rows)}"
            f'<div class="ov-mm-research-detail">{escape(_display_value(item.get("detail")))}</div>'
            "</article>"
        )
    return "".join(html)


def _market_mover_research_collection_items_html(items: list[dict[str, Any]]) -> str:
    html: list[str] = []
    for item in items:
        detail = item.get("detail")
        detail_html = (
            f'<small>{escape(_display_value(detail))}</small>'
            if detail not in (None, "")
            else ""
        )
        html.append(
            '<div class="ov-mm-research-collection-item">'
            f'<span>{escape(_display_value(item.get("label")))}</span>'
            f'<strong>{escape(_display_value(item.get("value")))}</strong>'
            f"{detail_html}"
            "</div>"
        )
    return "".join(html)


def _market_mover_research_collection_html(model: dict[str, Any]) -> str:
    if not model:
        return ""
    headline = _display_value(model.get("headline"))
    if headline in ("", "-"):
        return ""
    tone_color = escape(_overview_tone_color(model.get("tone") or model.get("status")))
    status = _display_value(model.get("status"))
    status_html = f'<span class="ov-mm-research-collection-badge">{escape(status)}</span>' if status != "-" else ""
    return (
        f'<div class="ov-mm-research-collection" style="--ov-research-collection-tone:{tone_color};">'
        "<div>"
        '<div class="ov-mm-research-collection-kicker">재무제표 수집 상태</div>'
        f'<div class="ov-mm-research-collection-title">{escape(headline)}</div>'
        f'<div class="ov-mm-research-collection-detail">{escape(_display_value(model.get("detail")))}</div>'
        "</div>"
        f"{status_html}"
        f'<div class="ov-mm-research-collection-items">{_market_mover_research_collection_items_html(list(model.get("items") or []))}</div>'
        "</div>"
    )


def _chart_numeric_value(value: Any) -> float | None:
    if isinstance(value, str):
        value = value.strip().replace(",", "").replace("$", "")
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    return numeric


_RESEARCH_CHART_COLUMN_WIDTH_PX = 64
_RESEARCH_CHART_GAP_PX = 4
_RESEARCH_CHART_LINE_HEIGHT = 100.0


def _market_mover_research_line_svg(
    values: list[float],
    max_abs: float,
    *,
    uses_diverging_axis: bool = False,
) -> tuple[str, int]:
    plot_width = (
        len(values) * _RESEARCH_CHART_COLUMN_WIDTH_PX
        + max(0, len(values) - 1) * _RESEARCH_CHART_GAP_PX
    )
    if not values:
        return "", 0
    points: list[str] = []
    circles: list[str] = []
    step = _RESEARCH_CHART_COLUMN_WIDTH_PX + _RESEARCH_CHART_GAP_PX
    for index, value in enumerate(values):
        x = (_RESEARCH_CHART_COLUMN_WIDTH_PX / 2.0) + (index * step)
        if uses_diverging_axis:
            magnitude = (abs(value) / max_abs) * 50.0
            y = 50.0 - magnitude if value >= 0 else 50.0 + magnitude
        else:
            height = max(3.0, min(_RESEARCH_CHART_LINE_HEIGHT, (abs(value) / max_abs) * 100.0))
            y = _RESEARCH_CHART_LINE_HEIGHT - height
        y = max(2.0, min(98.0, y))
        points.append(f"{x:.2f},{y:.2f}")
        circles.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="2.15"></circle>')
    svg = (
        '<svg class="ov-mm-research-chart-line" aria-hidden="true" focusable="false" '
        f'viewBox="0 0 {float(plot_width):.2f} {_RESEARCH_CHART_LINE_HEIGHT:.2f}" '
        f'preserveAspectRatio="none" style="width:{plot_width}px;">'
        f'<polyline points="{" ".join(points)}"></polyline>'
        f'{"".join(circles)}'
        "</svg>"
    )
    return svg, plot_width


def _market_mover_research_bar_chart_html(chart: dict[str, Any], frequency: str) -> str:
    frequency_label = "분기" if frequency == "quarterly" else "연간"
    points = [
        dict(point)
        for point in list(dict(chart.get("series") or {}).get(frequency) or [])
        if isinstance(point, dict) and _chart_numeric_value(point.get("value")) is not None
    ]
    if not points:
        return (
            '<div class="ov-mm-research-chart is-empty">'
            f"표시할 {escape(frequency_label)} 데이터가 없습니다"
            "</div>"
        )
    values = [_chart_numeric_value(point.get("value")) or 0.0 for point in points]
    max_abs = max(abs(value) for value in values) or 1.0
    uses_diverging_axis = any(value < 0 for value in values)
    line_svg, plot_width = _market_mover_research_line_svg(
        values,
        max_abs,
        uses_diverging_axis=uses_diverging_axis,
    )
    height_scale = 50.0 if uses_diverging_axis else 100.0
    plot_wrap_class = (
        "ov-mm-research-chart-plot-wrap is-diverging"
        if uses_diverging_axis
        else "ov-mm-research-chart-plot-wrap"
    )
    bar_plot_class = (
        "ov-mm-research-chart-bar-plot is-diverging"
        if uses_diverging_axis
        else "ov-mm-research-chart-bar-plot"
    )
    zero_line_html = (
        '<div class="ov-mm-research-chart-zero-line" aria-hidden="true"></div>'
        if uses_diverging_axis
        else ""
    )
    columns: list[str] = []
    for point, value in zip(points, values):
        height = max(3.0, min(height_scale, (abs(value) / max_abs) * height_scale))
        direction_class = "is-negative" if value < 0 else "is-positive"
        disclosure = _display_value(point.get("disclosure_date"))
        period_end = _display_value(point.get("period_end"))
        details = [f"회계기간 {period_end}" if period_end not in ("", "-") else ""]
        if disclosure not in ("", "-"):
            details.append(f"공시 {disclosure}")
        detail_text = " · ".join(part for part in details if part)
        display_value = _display_value(point.get("display_value"))
        label = _display_value(point.get("label"))
        accessibility = " · ".join(part for part in [label, display_value, detail_text] if part)
        columns.append(
            f'<div class="ov-mm-research-chart-column {direction_class}" role="listitem" title="{escape(detail_text)}" aria-label="{escape(accessibility)}">'
            '<div class="ov-mm-research-chart-track">'
            f"{zero_line_html}"
            f'<span class="ov-mm-research-chart-bar" style="height:{height:.2f}%;"></span>'
            "</div>"
            '<div class="ov-mm-research-chart-caption">'
            f'<div class="ov-mm-research-chart-label">{escape(label)}</div>'
            f'<strong class="ov-mm-research-chart-value">{escape(display_value)}</strong>'
            "</div>"
            "</div>"
        )
    return (
        '<div class="ov-mm-research-chart">'
        f'<div class="ov-mm-research-chart-title">{escape(_display_value(chart.get("label")))} · {escape(frequency_label)}</div>'
        f'<div class="ov-mm-research-chart-scroll" tabindex="0" aria-label="{escape(_display_value(chart.get("label")))} {escape(frequency_label)} 그래프 가로 스크롤">'
        f'<div class="{plot_wrap_class}" style="width:{plot_width}px;">'
        f"{line_svg}"
        f'<div class="{bar_plot_class}" role="list" aria-label="{escape(_display_value(chart.get("label")))} {escape(frequency_label)} 막대그래프">{"".join(columns)}</div>'
        "</div>"
        "</div>"
        "</div>"
    )


def _render_market_mover_research_metric_charts(charts: list[dict[str, Any]]) -> None:
    charts = [dict(chart) for chart in charts if isinstance(chart, dict)]
    if not charts:
        return
    st.markdown(
        overview_ui_css()
        + """
<div class="ov-mm-research-chart-shell">
  <div class="ov-mm-research-chart-head">
    <div class="ov-mm-research-chart-kicker">기본 지표 그래프</div>
    <div class="ov-mm-research-chart-copy">표는 그대로 두고, 같은 재무제표 snapshot을 막대로 비교합니다.</div>
  </div>
</div>""",
        unsafe_allow_html=True,
    )
    metric_tabs = st.tabs([chart["label"] for chart in charts])
    for metric_tab, chart in zip(metric_tabs, charts):
        with metric_tab:
            st.markdown(
                '<div class="ov-mm-research-chart-pair">'
                + _market_mover_research_bar_chart_html(chart, "annual")
                + _market_mover_research_bar_chart_html(chart, "quarterly")
                + "</div>",
                unsafe_allow_html=True,
            )


def render_market_mover_research_snapshot(model: dict[str, Any]) -> None:
    st.markdown(
        overview_ui_css()
        + f"""
<section class="ov-mm-research-snapshot">
  <div class="ov-mm-research-head">
    <div>
      <div class="ov-mm-research-kicker">Research Snapshot</div>
      <div class="ov-mm-research-title">{escape(_display_value(model.get("title")))}</div>
      <div class="ov-mm-research-subtitle">{escape(_display_value(model.get("subtitle")))}</div>
    </div>
    <span class="ov-mm-research-asof">기준 {escape(_display_value(model.get("as_of_label")))}</span>
  </div>
  <div class="ov-mm-research-grid">{_market_mover_research_items_html(list(model.get("items") or []))}</div>
  {_market_mover_research_collection_html(dict(model.get("financial_statement_collection") or {}))}
  <div class="ov-mm-research-boundary">{escape(_display_value(model.get("boundary_note")))}</div>
</section>""",
        unsafe_allow_html=True,
    )
    _render_market_mover_research_metric_charts(list(model.get("metric_charts") or []))


def _data_trust_strip_items_html(items: list[dict[str, Any]]) -> str:
    html: list[str] = []
    for item in items:
        detail = item.get("detail")
        detail_html = (
            f'<small>{escape(_display_value(detail))}</small>'
            if detail not in (None, "")
            else ""
        )
        html.append(
            '<span class="ov-mm-data-trust-chip">'
            f'<span>{escape(_display_value(item.get("label")))}</span>'
            f'<strong>{escape(_display_value(item.get("value")))}</strong>'
            f"{detail_html}"
            "</span>"
        )
    return "".join(html)


def render_market_movers_data_trust_strip(model: dict[str, Any]) -> None:
    tone_color = escape(_overview_tone_color(model.get("tone")))
    st.markdown(
        overview_ui_css()
        + f"""
<section class="ov-mm-data-trust-strip" style="--ov-data-trust-tone:{tone_color};">
  <div class="ov-mm-data-trust-head">
    <div>
      <div class="ov-mm-data-trust-kicker">현재 결과 신뢰도</div>
      <div class="ov-mm-data-trust-title">{escape(_display_value(model.get("state")))}</div>
      <div class="ov-mm-data-trust-detail">{escape(_display_value(model.get("headline")))} · {escape(_display_value(model.get("detail")))}</div>
    </div>
    <span class="ov-mm-data-trust-action">{escape(_display_value(model.get("action_label")))}</span>
  </div>
  <div class="ov-mm-data-trust-chips">{_data_trust_strip_items_html(list(model.get("items") or []))}</div>
  <div class="ov-mm-data-trust-boundary">{escape(_display_value(model.get("boundary_note")))}</div>
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
            f"상승 비중 {escape(positive)}% · 하락 {escape(decliners)}"
            f" · 상승 상위 {escape(top_symbol)} {escape(top_return)}%"
            f" / 하락 상위 {escape(top_loser)} {escape(top_loser_return)}%"
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
            f'<div class="ov-sector-pressure-detail">상승 {escape(advancers)} / 하락 {escape(decliners)} · 시총비중 {escape(size_share)}%</div>'
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
    tone_color = escape(_overview_tone_color(model.get("tone") or model.get("status")))
    stats = [
        dict(model.get("participation") or {}),
        dict(model.get("leadership") or {}),
        dict(model.get("dispersion") or {}),
    ]
    stats_html = "".join(_sector_breadth_stat_html(item) for item in stats if item)
    lanes_html = _sector_breadth_lanes_html(list(model.get("lanes") or []))
    rail_pct = escape(_display_value(dict(model.get("participation") or {}).get("rail_pct") or 0))
    st.markdown(
        overview_ui_css()
        + f"""
<section class="ov-sector-breadth-map" style="--ov-band-tone:{tone_color};--ov-rail-fill:{rail_pct}%;">
  <div class="ov-sector-breadth-head">
    <div>
      <div class="ov-sector-breadth-kicker">시장 확산 지도</div>
      <div class="ov-sector-breadth-title">{escape(_display_value(model.get("headline")))}</div>
      <div class="ov-sector-breadth-detail">{escape(_display_value(model.get("detail")))} · 기준: {escape(_display_value(model.get("freshness")))}</div>
    </div>
    <span class="ov-sector-breadth-status">{escape(_display_value(model.get("status")))}</span>
  </div>
  <div class="ov-sector-breadth-rail">
    <span class="ov-sector-breadth-rail-fill"></span>
  </div>
  <div class="ov-sector-breadth-stats">{stats_html}</div>
  <div class="ov-sector-breadth-lanes">{lanes_html}</div>
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
      <div class="ov-breadth-kicker">섹터 확산 / 히트맵</div>
      <div class="ov-breadth-title">{escape(_display_value(summary.get("headline")))}</div>
      <div class="ov-breadth-detail">{escape(_display_value(summary.get("detail")))} · 기준: {escape(freshness)}</div>
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
<div class="ov-mm-refresh-rail">
  <div class="ov-mm-state-cluster">
    <span class="ov-mm-refresh-eyebrow">갱신</span>
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
    message_text = _market_refresh_state_detail(message)
    st.markdown(
        f'<div class="ov-mm-auto-message">{escape(str(message_text))}</div>',
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
    "_unified_summary_items_html",
    "render_breadth_heatmap_summary",
    "render_sector_breadth_market_map",
    "render_market_movers_coverage_trust",
    "render_market_movers_command_strip",
    "render_market_movers_empty_state",
    "render_market_mover_board",
    "render_market_mover_chart_workspace",
    "render_market_mover_investigation_pane",
    "render_market_movers_section_divider",
    "render_market_movers_data_trust_strip",
    "render_market_movers_unified_summary",
    "_market_refresh_state_label",
    "_market_refresh_state_detail",
    "render_market_refresh_status_bar",
    "render_market_auto_message",
    "render_market_auto_waiting_panel",
    "render_auto_refresh_timing_static",
    "render_auto_refresh_countdown",
]
