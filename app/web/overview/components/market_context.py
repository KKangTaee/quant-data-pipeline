from __future__ import annotations

from html import escape
from typing import Any

import streamlit as st

from app.web.overview.components.common import *

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

__all__ = [
    "_macro_cockpit_badges_html",
    "_macro_cockpit_rail_html",
    "_macro_hybrid_tape_html",
    "_macro_cockpit_row_meta_html",
    "_signed_pct",
    "_sector_pressure_map_html",
    "_event_timeline_day_label",
    "_event_timeline_html",
    "_macro_cockpit_visual_board_html",
    "_macro_cockpit_brief_rows_html",
    "_macro_cockpit_next_checks_html",
    "_macro_cockpit_interpretation_cues_html",
    "_analog_pct",
    "_analog_delta_pct",
    "_analog_cell_strength",
    "_analog_row_asset",
    "_analog_row_horizon",
    "_analog_table_row_html",
    "_analog_table_block_html",
    "_analog_find_reference_row",
    "_analog_find_asset_horizon_row",
    "_analog_summary_strip_html",
    "_analog_outcome_matrix_html",
    "_analog_support_summary_html",
    "_analog_detail_tables_html",
    "_analog_interpretation_html",
    "_analog_rows_by_priority",
    "_analog_basis_group_html",
    "_analog_basis_warning_html",
    "_analog_basis_ledger_html",
    "_analog_method_line_html",
    "_macro_condition_list_html",
    "_macro_used_condition_summary_html",
    "_macro_dimension_anchor_count",
    "_macro_condition_is_used",
    "_macro_dimension_audit_html",
    "_macro_dimension_by_id",
    "_macro_condition_count",
    "_macro_count_label",
    "_macro_pool_label",
    "_macro_stage_label",
    "_macro_stage_state_name",
    "_macro_stage_detail",
    "_macro_independent_stage_detail",
    "_macro_condition_meaning",
    "_macro_condition_source_details_html",
    "_macro_sample_summary",
    "_macro_sample_flow_html",
    "_macro_result_delta_rows",
    "_macro_result_delta_html",
    "_macro_backdrop_state_name",
    "_macro_backdrop_display_label",
    "_macro_backdrop_description",
    "_macro_backdrop_state_label",
    "_macro_backdrop_interpretation",
    "_macro_backdrop_state_meaning",
    "_macro_backdrop_ratio",
    "_macro_backdrop_detail",
    "_macro_backdrop_preview_html",
    "_macro_conditioned_pilot_html",
    "_macro_cockpit_historical_analog_html",
    "_source_confidence_status_bucket",
    "_source_confidence_summary_strip_html",
    "_macro_cockpit_source_confidence_html",
    "_macro_cockpit_body_html",
    "_macro_context_reading_flow_html",
    "_macro_context_cockpit_html",
    "render_macro_context_cockpit",
    "render_macro_context_reading_flow",
    "render_overview_ia_closeout_guide",
]
