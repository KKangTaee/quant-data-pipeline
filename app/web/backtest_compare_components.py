from __future__ import annotations

from collections.abc import Iterable, Mapping
from html import escape
from typing import Any

import pandas as pd
import streamlit as st


def render_portfolio_mix_builder_css() -> None:
    st.markdown(
        """
        <style>
        .pmx-stepper, .pmx-section-head, .pmx-card-grid, .pmx-handoff-card {
            --pmx-surface: var(--secondary-background-color);
            --pmx-border: rgba(128, 128, 128, 0.28);
            --pmx-text: var(--text-color);
            --pmx-muted: #8a94a6;
        }
        .pmx-stepper {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.75rem;
            margin: 0.9rem 0 1.1rem;
        }
        .pmx-step {
            min-height: 5.25rem;
            border: 1px solid var(--pmx-border);
            border-radius: 8px;
            padding: 0.8rem 0.9rem;
            background: var(--pmx-surface);
        }
        .pmx-step.done {
            border-color: #a7d7b9;
            background: rgba(19, 115, 51, 0.10);
        }
        .pmx-step.active {
            border-color: #ff6b6b;
            background: rgba(255, 107, 107, 0.10);
        }
        .pmx-step.ready {
            border-color: #a7d7b9;
            background: rgba(19, 115, 51, 0.10);
        }
        .pmx-step.pending {
            background: var(--pmx-surface);
            color: var(--pmx-muted);
        }
        .pmx-step.blocked {
            border-color: #f2b8b5;
            background: rgba(180, 35, 24, 0.10);
        }
        .pmx-step-index {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 1.35rem;
            height: 1.35rem;
            margin-right: 0.35rem;
            border-radius: 999px;
            background: rgba(128, 128, 128, 0.18);
            color: var(--pmx-text);
            font-size: 0.78rem;
            font-weight: 700;
        }
        .pmx-step.done .pmx-step-index {
            background: #dff3e6;
            color: #137333;
        }
        .pmx-step.active .pmx-step-index {
            background: #ffe3e3;
            color: #c92a2a;
        }
        .pmx-step.ready .pmx-step-index {
            background: #dff3e6;
            color: #137333;
        }
        .pmx-step-title {
            display: block;
            margin-top: 0.15rem;
            font-weight: 750;
            color: var(--pmx-text);
        }
        .pmx-step-caption {
            display: block;
            margin-top: 0.35rem;
            font-size: 0.84rem;
            line-height: 1.35;
            color: var(--pmx-muted);
        }
        .pmx-section-head {
            margin: 0.4rem 0 0.75rem;
            padding: 0.95rem 1rem;
            border: 1px solid var(--pmx-border);
            border-left: 4px solid #ff6b6b;
            border-radius: 8px;
            background: var(--pmx-surface);
        }
        .pmx-section-head strong {
            display: block;
            color: var(--pmx-text);
            font-size: 1rem;
        }
        .pmx-section-head span {
            display: block;
            margin-top: 0.3rem;
            color: var(--pmx-muted);
            font-size: 0.9rem;
            line-height: 1.45;
        }
        .pmx-card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 0.75rem;
            margin: 0.7rem 0 1rem;
        }
        .pmx-component-card {
            border: 1px solid var(--pmx-border);
            border-radius: 8px;
            padding: 0.85rem 0.9rem;
            background: var(--pmx-surface);
        }
        .pmx-component-title {
            font-weight: 750;
            color: var(--pmx-text);
            margin-bottom: 0.25rem;
        }
        .pmx-component-contract {
            min-height: 1.8rem;
            color: var(--pmx-muted);
            font-size: 0.82rem;
            line-height: 1.3;
            margin-bottom: 0.65rem;
        }
        .pmx-metric-row {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.45rem;
            margin-bottom: 0.65rem;
        }
        .pmx-metric {
            padding: 0.45rem;
            border-radius: 7px;
            background: rgba(128, 128, 128, 0.12);
        }
        .pmx-metric small {
            display: block;
            color: var(--pmx-muted);
            font-size: 0.72rem;
            line-height: 1.1;
        }
        .pmx-metric strong {
            display: block;
            margin-top: 0.2rem;
            color: var(--pmx-text);
            font-size: 0.86rem;
        }
        .pmx-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.35rem;
        }
        .pmx-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            border-radius: 999px;
            padding: 0.2rem 0.5rem;
            font-size: 0.78rem;
            font-weight: 650;
            background: #f2f4f7;
            color: #344054;
        }
        .pmx-chip.pass {
            background: #e7f6ec;
            color: #137333;
        }
        .pmx-chip.review {
            background: #fff4d6;
            color: #8a5b00;
        }
        .pmx-chip.fail {
            background: #ffe4e4;
            color: #b42318;
        }
        .pmx-chip.neutral {
            background: #f2f4f7;
            color: #344054;
        }
        .pmx-handoff-card {
            border: 1px solid var(--pmx-border);
            border-radius: 8px;
            padding: 1rem;
            background: var(--pmx-surface);
            margin: 0.5rem 0 0.9rem;
        }
        .pmx-handoff-card.pass {
            border-color: #a7d7b9;
            background: rgba(19, 115, 51, 0.10);
        }
        .pmx-handoff-card.review {
            border-color: #efd28d;
            background: rgba(255, 196, 0, 0.10);
        }
        .pmx-handoff-card.fail {
            border-color: #f2b8b5;
            background: rgba(180, 35, 24, 0.10);
        }
        .pmx-handoff-title {
            display: block;
            color: var(--pmx-text);
            font-weight: 800;
            margin-bottom: 0.35rem;
        }
        .pmx-handoff-body {
            display: block;
            color: var(--pmx-muted);
            font-size: 0.9rem;
            line-height: 1.45;
        }
        @media (max-width: 900px) {
            .pmx-stepper {
                grid-template-columns: 1fr 1fr;
            }
            .pmx-metric-row {
                grid-template-columns: 1fr 1fr;
            }
        }
        @media (max-width: 560px) {
            .pmx-stepper,
            .pmx-card-grid,
            .pmx-metric-row {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def html_text(value: Any) -> str:
    return escape(str(value if value is not None else "-"))


def _metric_text(value: Any, kind: str) -> str:
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return "-"
    if pd.isna(numeric_value):
        return "-"
    if kind == "currency":
        return f"${numeric_value:,.1f}"
    if kind == "percent":
        return f"{numeric_value * 100:.2f}%"
    if kind == "ratio":
        return f"{numeric_value:.3f}"
    return f"{numeric_value:,.2f}"


def status_chip_tone(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    if not normalized or normalized == "-":
        return "neutral"
    if any(token in normalized for token in ["pass", "ready", "가능", "없음", "clean", "created"]):
        return "pass"
    if any(token in normalized for token in ["review", "conditional", "warning", "cadence", "확인", "필요"]):
        return "review"
    if any(token in normalized for token in ["fail", "hold", "block", "error", "disabled", "차단"]):
        return "fail"
    return "neutral"


def render_portfolio_mix_flow_strip(
    *,
    component_ready: bool,
    mix_ready: bool,
    can_send_to_practical_validation: bool | None = None,
) -> None:
    if not component_ready:
        active_index = 0
    elif not mix_ready:
        active_index = 1
    else:
        active_index = 2

    steps = [
        ("Component 실행", "같은 기간 조건으로 mix 재료를 만듭니다."),
        ("Weight 구성", "구성 전략 비중과 date alignment를 정합니다."),
        ("Mix 후보 판단", "mix 전체가 2차 검증 후보인지 확인합니다."),
        ("Practical Validation", "통과한 mix를 current selection source로 보냅니다."),
    ]
    step_cards = []
    for idx, (title, caption) in enumerate(steps):
        if idx < active_index:
            css_class = "done"
        elif idx == active_index:
            css_class = "active"
            if idx == 2 and can_send_to_practical_validation is False:
                css_class = "blocked"
        else:
            css_class = "pending"
        if idx == 3 and mix_ready and can_send_to_practical_validation is True:
            css_class = "ready"
        step_cards.append(
            f'<div class="pmx-step {css_class}">'
            f'<span class="pmx-step-index">{idx + 1}</span>'
            f'<span class="pmx-step-title">{html_text(title)}</span>'
            f'<span class="pmx-step-caption">{html_text(caption)}</span>'
            "</div>"
        )
    st.markdown(f'<div class="pmx-stepper">{"".join(step_cards)}</div>', unsafe_allow_html=True)


def render_portfolio_mix_section_head(title: str, body: str) -> None:
    st.markdown(
        f'<div class="pmx-section-head"><strong>{html_text(title)}</strong><span>{html_text(body)}</span></div>',
        unsafe_allow_html=True,
    )


def render_component_result_overview_cards(overview_rows: Iterable[Mapping[str, Any]]) -> None:
    cards = []
    for row in overview_rows:
        trust = row.get("Data Trust") or "-"
        promotion = row.get("Promotion") or "-"
        execution_preview = row.get("Execution Preview") or "-"
        cards.append(
            '<div class="pmx-component-card">'
            f'<div class="pmx-component-title">{html_text(row.get("Strategy"))}</div>'
            f'<div class="pmx-component-contract">{html_text(row.get("Contract"))}</div>'
            '<div class="pmx-metric-row">'
            f'<div class="pmx-metric"><small>End</small><strong>{html_text(_metric_text(row.get("End Balance"), "currency"))}</strong></div>'
            f'<div class="pmx-metric"><small>CAGR</small><strong>{html_text(_metric_text(row.get("CAGR"), "percent"))}</strong></div>'
            f'<div class="pmx-metric"><small>MDD</small><strong>{html_text(_metric_text(row.get("MDD"), "percent"))}</strong></div>'
            f'<div class="pmx-metric"><small>Sharpe</small><strong>{html_text(_metric_text(row.get("Sharpe"), "ratio"))}</strong></div>'
            '</div>'
            '<div class="pmx-chip-row">'
            f'<span class="pmx-chip {status_chip_tone(trust)}">Data {html_text(trust)}</span>'
            f'<span class="pmx-chip {status_chip_tone(promotion)}">Promotion {html_text(promotion)}</span>'
            f'<span class="pmx-chip {status_chip_tone(execution_preview)}">Source {html_text(execution_preview)}</span>'
            '</div>'
            '</div>'
        )
    st.markdown(f'<div class="pmx-card-grid">{"".join(cards)}</div>', unsafe_allow_html=True)
