from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.backtest_strategy_catalog import (
    display_name_to_selection,
    display_name_to_strategy_key,
    resolve_concrete_strategy_display_name,
)


def _input(label: str, detail: str) -> dict[str, str]:
    return {"label": label, "detail": detail}


def _section(title: str, summary: str, items: list[str]) -> dict[str, Any]:
    return {"title": title, "summary": summary, "items": list(items)}


_COMMON_DATE_INPUTS = [
    _input("Start Date", "Backtest start date."),
    _input("End Date", "Requested end date; strict preflights compare against the effective trading end."),
]

_ETF_PROMOTION_SECTION = _section(
    "Promotion Policy Signal",
    "ETF-like first-pass handoff assumptions and comparators.",
    [
        "Minimum Price",
        "Transaction Cost (bps)",
        "Benchmark Ticker",
        "Min ETF AUM",
        "Max Bid-Ask Spread",
    ],
)

_ETF_GUARDRAIL_SECTION = _section(
    "ETF Guardrails",
    "Optional second-pass trailing underperformance and drawdown cash fallback rules.",
    [
        "Underperformance Guardrail",
        "Drawdown Guardrail",
    ],
)

_STRICT_OVERLAY_SECTION = _section(
    "Overlay",
    "Optional trend and market-regime filters before final holdings are accepted.",
    [
        "Trend Filter Overlay",
        "Market Regime Overlay",
    ],
)

_STRICT_PORTFOLIO_HANDLING_SECTION = _section(
    "Portfolio Handling & Defensive Rules",
    "Contracts for final weights, rejected slots, and defensive sleeve behavior.",
    [
        "Weighting Contract",
        "Rejected Slot Handling Contract",
        "Defensive Sleeve Contract",
    ],
)

_STRICT_ANNUAL_PROMOTION_SECTION = _section(
    "Promotion Policy Signal",
    "Annual strict handoff policy for investability, benchmark, validation, and portfolio guardrail thresholds.",
    [
        "Minimum Price",
        "Minimum History",
        "Min Avg Dollar Volume 20D",
        "Benchmark Contract",
        "Benchmark Policy",
        "Validation Policy",
        "Portfolio Guardrail Policy",
    ],
)

_STRICT_GUARDRAIL_SECTION = _section(
    "Guardrails",
    "Optional benchmark-relative underperformance and drawdown reference rules.",
    [
        "Underperformance Guardrail",
        "Drawdown Guardrail",
        "Guardrail / Reference Ticker",
    ],
)

_STRICT_PRICE_PREFLIGHT_SECTION = _section(
    "Price Freshness Preflight",
    "Checks DB price coverage and latest-date spread before execution.",
    [
        "Requested symbols",
        "Covered symbols",
        "Common latest date",
        "Stale / missing symbols",
    ],
)

_STATEMENT_COVERAGE_PREFLIGHT_SECTION = _section(
    "Statement Shadow Coverage Preview",
    "Quarterly prototype coverage check for usable statement shadow factors.",
    [
        "Available statement snapshots",
        "Usable factor history",
        "Coverage warning",
    ],
)


_DETAILS_BY_DISPLAY_NAME: dict[str, dict[str, Any]] = {
    "Equal Weight": {
        "summary": "DB-backed equal-weight portfolio execution using preset or manual ETF universes.",
        "data_source": "DB daily prices",
        "timing": "month_end rebalance",
        "universe_modes": ["Preset", "Manual"],
        "universe_note": "Preset is fast for ETF experiments; Manual accepts comma-separated tickers.",
        "badges": ["etf", "baseline"],
        "primary_inputs": _COMMON_DATE_INPUTS,
        "advanced_sections": [
            _section(
                "Advanced Inputs",
                "Basic execution cadence.",
                ["Timeframe", "Option", "Rebalance Interval"],
            ),
            _ETF_PROMOTION_SECTION,
        ],
        "preflight_sections": [],
        "run_button_label": "Run Equal Weight Backtest",
    },
    "GTAA": {
        "summary": "Global tactical asset allocation using score horizons, top assets, and optional risk-off overlay.",
        "data_source": "DB daily prices",
        "timing": "month_end score and rebalance",
        "universe_modes": ["Preset", "Manual"],
        "universe_note": "Preset can apply strategy-specific defaults for top count, interval, score horizons, and defensive tickers.",
        "badges": ["etf", "tactical", "risk-off"],
        "primary_inputs": _COMMON_DATE_INPUTS,
        "advanced_sections": [
            _section(
                "Advanced Inputs",
                "Core GTAA ranking contract.",
                ["Timeframe", "Option", "Top Assets", "Signal Interval", "Score Horizons"],
            ),
            _section(
                "Risk-Off Overlay",
                "Defensive mode and macro-aware risk-off settings.",
                ["Trend Filter Window", "Risk-Off Mode", "Defensive Tickers", "Market Regime Overlay", "Crash Guardrail"],
            ),
            _ETF_PROMOTION_SECTION,
            _ETF_GUARDRAIL_SECTION,
        ],
        "preflight_sections": [],
        "run_button_label": "Run GTAA Backtest",
    },
    "Global Relative Strength": {
        "summary": "ETF relative-strength strategy that ranks cross-asset sleeves and can move rejected assets to a cash ticker.",
        "data_source": "DB daily prices",
        "timing": "month_end score and trend filter",
        "universe_modes": ["Preset", "Manual"],
        "universe_note": "Preset covers global equity, commodity, credit, treasury, inflation, and cash sleeves.",
        "badges": ["etf", "relative-strength", "trend"],
        "primary_inputs": _COMMON_DATE_INPUTS,
        "advanced_sections": [
            _section(
                "Advanced Inputs",
                "Relative-strength score and trend contract.",
                ["Timeframe", "Option", "Cash / Defensive Ticker", "Top Assets", "Signal Interval", "Score Horizons", "Trend Filter Window"],
            ),
            _ETF_PROMOTION_SECTION,
        ],
        "preflight_sections": [_STRICT_PRICE_PREFLIGHT_SECTION],
        "run_button_label": "Run Global Relative Strength Backtest",
    },
    "Risk Parity Trend": {
        "summary": "ETF risk-parity trend strategy that sizes sleeves from recent volatility.",
        "data_source": "DB daily prices",
        "timing": "month_end rebalance",
        "universe_modes": ["Preset", "Manual"],
        "universe_note": "Preset starts from diversified ETF sleeves; Manual accepts comma-separated tickers.",
        "badges": ["etf", "risk-parity", "trend"],
        "primary_inputs": _COMMON_DATE_INPUTS,
        "advanced_sections": [
            _section(
                "Advanced Inputs",
                "Risk-parity execution contract.",
                ["Timeframe", "Option", "Rebalance Interval", "Volatility Window"],
            ),
            _ETF_PROMOTION_SECTION,
            _ETF_GUARDRAIL_SECTION,
        ],
        "preflight_sections": [],
        "run_button_label": "Run Risk Parity Trend Backtest",
    },
    "Dual Momentum": {
        "summary": "ETF momentum strategy that selects top assets from preset or manual universes.",
        "data_source": "DB daily prices",
        "timing": "month_end rebalance",
        "universe_modes": ["Preset", "Manual"],
        "universe_note": "Preset provides an offensive / defensive ETF universe; Manual accepts comma-separated tickers.",
        "badges": ["etf", "momentum"],
        "primary_inputs": _COMMON_DATE_INPUTS,
        "advanced_sections": [
            _section(
                "Advanced Inputs",
                "Momentum execution contract.",
                ["Timeframe", "Option", "Top Assets", "Rebalance Interval"],
            ),
            _ETF_PROMOTION_SECTION,
            _ETF_GUARDRAIL_SECTION,
        ],
        "preflight_sections": [],
        "run_button_label": "Run Dual Momentum Backtest",
    },
    "Risk-On Momentum 5D": {
        "summary": "DB-backed stock swing strategy with D+1 open execution and short holding windows.",
        "data_source": "DB daily stock prices plus futures macro context",
        "timing": "daily close-based signal",
        "universe_modes": ["Top1000", "Top2000", "S&P 500", "Manual"],
        "universe_note": "Managed universes are resolved from DB asset-profile market-cap data; Manual accepts stock tickers.",
        "badges": ["stock swing", "daily", "macro-filter"],
        "primary_inputs": [
            *_COMMON_DATE_INPUTS,
            _input("Start Balance", "Initial capital for swing simulation."),
        ],
        "advanced_sections": [
            _section(
                "Execution / Exit",
                "Position count, holding period, fixed percent, and ATR-based exit rules.",
                ["Execution Mode", "Max New Positions / Day", "Max Total Positions", "Exit Mode", "Max Holding Days", "Stop Loss", "Take Profit", "ATR Settings"],
            ),
            _section(
                "Macro / Candidate Filters",
                "Risk-on macro filter and liquidity / price candidate filters.",
                ["Macro Filter Mode", "Risk-On Min", "Rate Pressure Max", "Dollar Pressure Max", "Safe Haven Max", "Penalty Weights", "Min Price", "Min ADV 20D", "Min Avg Volume 20D"],
            ),
            _section(
                "Cost / Comparison",
                "Cost assumptions and optional V2 research diagnostics.",
                ["Transaction Cost", "Slippage", "Random Iterations", "Scanner Rows / Day", "Comparison Suite", "Sensitivity Suite"],
            ),
        ],
        "preflight_sections": [],
        "run_button_label": "Run Risk-On Momentum 5D Backtest",
    },
    "Quality Snapshot": {
        "summary": "Research-oriented broad quality snapshot using factor snapshots rather than strict statement PIT handling.",
        "data_source": "nyse_factors",
        "timing": "broad_research annual factor snapshot",
        "universe_modes": ["Preset", "Manual"],
        "universe_note": "Stock-oriented quick research path; ETF universes may have sparse factor coverage.",
        "badges": ["quality", "research"],
        "primary_inputs": [
            *_COMMON_DATE_INPUTS,
            _input("Top N", "Number of top ranked quality names to hold."),
        ],
        "advanced_sections": [
            _section(
                "Advanced Inputs",
                "Broad quality factor snapshot settings.",
                ["Timeframe", "Option", "Factor Frequency", "Quality Factors", "Snapshot Mode"],
            )
        ],
        "preflight_sections": [],
        "run_button_label": "Run Quality Snapshot Backtest",
    },
}


def _strict_factor_detail(
    *,
    display_name: str,
    summary: str,
    factor_items: list[str],
    family_badge: str,
    top_label: str,
    run_button_label: str,
    quarterly: bool = False,
    annual_promotion: bool = True,
) -> dict[str, Any]:
    badges = [family_badge, "strict", "quarterly" if quarterly else "annual"]
    if quarterly:
        badges.append("prototype")
    advanced_sections = [
        _section(
            "Advanced Inputs",
            "Strict factor execution and universe contract.",
            ["Timeframe", "Option", "Rebalance Interval", "Universe Contract", *factor_items],
        ),
        _STRICT_OVERLAY_SECTION,
        _STRICT_PORTFOLIO_HANDLING_SECTION,
    ]
    if annual_promotion:
        advanced_sections.extend([_STRICT_ANNUAL_PROMOTION_SECTION, _STRICT_GUARDRAIL_SECTION])

    preflight_sections = [_STRICT_PRICE_PREFLIGHT_SECTION]
    if quarterly:
        preflight_sections.append(_STATEMENT_COVERAGE_PREFLIGHT_SECTION)

    return {
        "summary": summary,
        "data_source": "nyse_factors_statement shadow factors",
        "timing": "strict_statement_quarterly" if quarterly else "strict_statement_annual",
        "universe_modes": ["Preset", "Manual"],
        "universe_note": "Preset uses managed US statement coverage lists; Manual accepts stock tickers.",
        "badges": badges,
        "is_prototype": quarterly,
        "primary_inputs": [
            *_COMMON_DATE_INPUTS,
            _input("Top N", top_label),
        ],
        "advanced_sections": advanced_sections,
        "preflight_sections": preflight_sections,
        "run_button_label": run_button_label,
    }


_DETAILS_BY_DISPLAY_NAME.update(
    {
        "Quality Snapshot (Strict Annual)": _strict_factor_detail(
            display_name="Quality Snapshot (Strict Annual)",
            summary="Strict annual statement-driven quality strategy using coverage-first quality shadow factors.",
            factor_items=["Quality Factors"],
            family_badge="quality",
            top_label="Number of top ranked strict annual quality names to hold.",
            run_button_label="Run Strict Annual Quality Backtest",
        ),
        "Quality Snapshot (Strict Quarterly Prototype)": _strict_factor_detail(
            display_name="Quality Snapshot (Strict Quarterly Prototype)",
            summary="Research-only quarterly strict quality prototype using quarterly statement shadow factors.",
            factor_items=["Quality Factors"],
            family_badge="quality",
            top_label="Number of top ranked strict quarterly quality names to hold.",
            run_button_label="Run Strict Quarterly Quality Prototype",
            quarterly=True,
            annual_promotion=False,
        ),
        "Value Snapshot (Strict Annual)": _strict_factor_detail(
            display_name="Value Snapshot (Strict Annual)",
            summary="Strict annual statement-driven value strategy using valuation shadow factors.",
            factor_items=["Value Factors"],
            family_badge="value",
            top_label="Number of cheapest strict annual value names to hold.",
            run_button_label="Run Strict Annual Value Backtest",
        ),
        "Value Snapshot (Strict Quarterly Prototype)": _strict_factor_detail(
            display_name="Value Snapshot (Strict Quarterly Prototype)",
            summary="Research-only quarterly strict value prototype using quarterly valuation shadow factors.",
            factor_items=["Value Factors"],
            family_badge="value",
            top_label="Number of cheapest strict quarterly value names to hold.",
            run_button_label="Run Strict Quarterly Value Prototype",
            quarterly=True,
            annual_promotion=False,
        ),
        "Quality + Value Snapshot (Strict Annual)": _strict_factor_detail(
            display_name="Quality + Value Snapshot (Strict Annual)",
            summary="Strict annual multi-factor strategy blending quality and value shadow factors.",
            factor_items=["Quality Factors", "Value Factors"],
            family_badge="quality-value",
            top_label="Number of top ranked strict annual blended names to hold.",
            run_button_label="Run Strict Annual Quality + Value Backtest",
        ),
        "Quality + Value Snapshot (Strict Quarterly Prototype)": _strict_factor_detail(
            display_name="Quality + Value Snapshot (Strict Quarterly Prototype)",
            summary="Research-only quarterly strict multi-factor prototype blending quality and value shadow factors.",
            factor_items=["Quality Factors", "Value Factors"],
            family_badge="quality-value",
            top_label="Number of top ranked strict quarterly blended names to hold.",
            run_button_label="Run Strict Quarterly Quality + Value Prototype",
            quarterly=True,
            annual_promotion=False,
        ),
    }
)


def _fallback_detail(display_name: str) -> dict[str, Any]:
    return {
        "summary": f"{display_name} strategy detail is not cataloged yet.",
        "data_source": "Unknown",
        "timing": "Unknown",
        "universe_modes": [],
        "universe_note": "",
        "badges": ["strategy"],
        "primary_inputs": list(_COMMON_DATE_INPUTS),
        "advanced_sections": [],
        "preflight_sections": [],
        "run_button_label": f"Run {display_name} Backtest",
        "is_prototype": False,
    }


def build_backtest_strategy_detail_model(
    strategy_choice: str | None,
    variant: str | None = None,
) -> dict[str, Any]:
    """Return a Streamlit-free read model for the selected Backtest strategy form."""
    selected_choice = str(strategy_choice or "Equal Weight").strip() or "Equal Weight"
    concrete_display_name = resolve_concrete_strategy_display_name(selected_choice, variant)
    detail = deepcopy(_DETAILS_BY_DISPLAY_NAME.get(concrete_display_name) or _fallback_detail(concrete_display_name))
    family, resolved_variant = display_name_to_selection(concrete_display_name)
    if family == concrete_display_name:
        family = None
    strategy_key = display_name_to_strategy_key(concrete_display_name)

    detail.setdefault("is_prototype", "prototype" in [str(badge).lower() for badge in detail.get("badges", [])])
    detail.update(
        {
            "strategy_choice": selected_choice,
            "display_name": concrete_display_name,
            "strategy_key": strategy_key or "",
            "family": family or "",
            "variant": resolved_variant or "",
        }
    )
    return detail


__all__ = ["build_backtest_strategy_detail_model"]
