from __future__ import annotations

from contextlib import contextmanager
from html import escape
from typing import Iterator, Sequence

import streamlit as st

from app.services.backtest_strategy_catalog import (
    LEVEL1_STRATEGY_MATURITY,
    LEVEL1_STRATEGY_PURPOSE_GROUPS,
    resolve_concrete_strategy_display_name,
)


_STRATEGY_DESCRIPTIONS = {
    "Quality + Value": "기업의 품질과 가치평가를 함께 비교해 보유 후보를 고릅니다.",
    "Quality": "수익성과 재무 건전성이 상대적으로 좋은 기업을 고릅니다.",
    "Value": "기초가치 대비 가격 부담이 낮은 기업을 고릅니다.",
    "GTAA": "자산군의 상대강도와 추세를 비교해 공격·방어 자산을 선택합니다.",
    "Global Relative Strength": "글로벌 자산군의 상대강도를 비교해 상위 자산을 보유합니다.",
    "Dual Momentum": "상대·절대 모멘텀을 함께 확인해 공격·방어 자산을 선택합니다.",
    "Risk Parity Trend": "변동성과 추세를 함께 사용해 자산별 위험 기여를 조정합니다.",
    "Equal Weight": "선택한 자산을 같은 비중으로 보유하고 정해진 주기로 조정합니다.",
    "Risk-On Momentum 5D": "단기 위험선호 종목을 탐색하는 개발 중 전략입니다.",
}


def _strategy_purpose_label(strategy_choice: str) -> str:
    return next(
        (
            str(group["label"])
            for group in LEVEL1_STRATEGY_PURPOSE_GROUPS.values()
            if strategy_choice in group["items"]
        ),
        "기타 전략",
    )


def build_single_strategy_settings_summary(
    strategy_choice: str,
    selected_variant: str | None,
) -> dict[str, str | None]:
    """Project the selected strategy into a user-facing Step 2 summary."""

    maturity = LEVEL1_STRATEGY_MATURITY.get(strategy_choice, "development")
    return {
        "strategy_choice": strategy_choice,
        "display_name": resolve_concrete_strategy_display_name(
            strategy_choice,
            selected_variant,
        ),
        "variant": selected_variant,
        "purpose": _strategy_purpose_label(strategy_choice),
        "maturity": maturity,
        "maturity_label": "운영 전략" if maturity == "production" else "개발 중",
        "description": _STRATEGY_DESCRIPTIONS.get(
            strategy_choice,
            "선택한 전략의 실행 조건을 확인합니다.",
        ),
    }


def build_compact_ticker_summary(
    tickers: Sequence[str],
    *,
    preview_count: int = 5,
) -> dict[str, str | int]:
    """Keep the first-read universe compact while preserving complete evidence."""

    normalized = [str(ticker).strip().upper() for ticker in tickers if str(ticker).strip()]
    preview = ", ".join(normalized[: max(1, preview_count)]) or "없음"
    return {
        "count": len(normalized),
        "headline": f"선택 종목 {len(normalized)}개 · 대표 {preview}",
        "full_text": ", ".join(normalized),
    }


def _render_single_settings_style() -> None:
    st.markdown(
        """
        <style>
        .bt1-settings-summary {
          color-scheme: light;
          background: linear-gradient(135deg, #f6faff 0%, #eef6f7 100%);
          border: 1px solid #d8e4ee;
          border-radius: 20px;
          padding: 1.1rem 1.2rem;
          margin: 0.25rem 0 1rem;
          color: #152033;
        }
        .bt1-settings-summary__eyebrow {
          color: #557086;
          font-size: 0.78rem;
          font-weight: 800;
          letter-spacing: 0.08em;
          text-transform: uppercase;
        }
        .bt1-settings-summary__title {
          font-size: 1.35rem;
          font-weight: 800;
          margin: 0.3rem 0 0.45rem;
        }
        .bt1-settings-summary__meta {
          display: flex;
          flex-wrap: wrap;
          gap: 0.45rem;
          margin-bottom: 0.55rem;
        }
        .bt1-settings-summary__meta span {
          background: #ffffff;
          border: 1px solid #d8e4ee;
          border-radius: 999px;
          color: #38536a;
          font-size: 0.78rem;
          font-weight: 700;
          padding: 0.28rem 0.58rem;
        }
        .bt1-settings-summary__description {
          color: #52677a;
          font-size: 0.92rem;
          line-height: 1.55;
          margin: 0;
        }
        @media (max-width: 760px) {
          .bt1-settings-summary { border-radius: 16px; padding: 1rem; }
          .bt1-settings-summary__title { font-size: 1.16rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_single_strategy_settings_header(
    *,
    strategy_choice: str,
    selected_variant: str | None,
    variant_key: str | None = None,
    variant_options: Sequence[str] = (),
) -> str | None:
    """Render the only Step 2 strategy summary and compact family variant control."""

    if variant_key and variant_options:
        options = list(variant_options)
        current_variant = selected_variant if selected_variant in options else options[0]
        if st.session_state.get(variant_key) not in options:
            st.session_state[variant_key] = current_variant
        selected_variant = st.segmented_control(
            "실행 기준",
            options=options,
            key=variant_key,
            help="연간 또는 분기 재무제표 기준을 선택합니다.",
            width="stretch",
        )
        selected_variant = str(selected_variant or current_variant)

    summary = build_single_strategy_settings_summary(strategy_choice, selected_variant)
    _render_single_settings_style()
    variant_badge = (
        f"<span>{escape(str(summary['variant']))}</span>"
        if summary.get("variant")
        else ""
    )
    st.markdown(
        f"""
        <section class="bt1-settings-summary">
          <div class="bt1-settings-summary__eyebrow">현재 설정 대상</div>
          <div class="bt1-settings-summary__title">{escape(str(summary['display_name']))}</div>
          <div class="bt1-settings-summary__meta">
            <span>{escape(str(summary['purpose']))}</span>
            {variant_badge}
            <span>{escape(str(summary['maturity_label']))}</span>
          </div>
          <p class="bt1-settings-summary__description">{escape(str(summary['description']))}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    return selected_variant


@contextmanager
def single_settings_section(title: str, description: str) -> Iterator[None]:
    """Render one consistent settings card without owning its strategy widgets."""

    with st.container(border=True):
        st.markdown(f"#### {title}")
        st.caption(description)
        yield


def render_compact_ticker_summary(
    tickers: Sequence[str],
    *,
    preview_count: int = 5,
) -> None:
    summary = build_compact_ticker_summary(tickers, preview_count=preview_count)
    st.caption(str(summary["headline"]))
    with st.expander("전체 종목 보기", expanded=False):
        st.code(str(summary["full_text"]) or "선택된 종목이 없습니다.")


__all__ = [
    "build_compact_ticker_summary",
    "build_single_strategy_settings_summary",
    "render_compact_ticker_summary",
    "render_single_strategy_settings_header",
    "single_settings_section",
]
