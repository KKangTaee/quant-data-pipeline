from __future__ import annotations

import inspect
import json
import sys
import time
from datetime import date, datetime, timedelta
from functools import lru_cache
from pathlib import Path
from collections.abc import Callable
from typing import Any

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.web.runtime import (
    CANDIDATE_REVIEW_NOTES_FILE,
    CURRENT_CANDIDATE_REGISTRY_FILE,
    SAVED_PORTFOLIO_FILE,
    append_candidate_review_note as _append_candidate_review_note,
    append_backtest_run_history,
    append_current_candidate_registry_row as _append_current_candidate_registry_row,
    build_backtest_result_bundle,
    delete_saved_portfolio,
    inspect_strict_annual_price_freshness,
    load_candidate_review_notes as _load_candidate_review_notes,
    load_current_candidate_registry_latest as _load_current_candidate_registry_latest,
    load_pre_live_candidate_registry_latest as _load_pre_live_candidate_registry_latest,
    load_saved_portfolios,
    run_dual_momentum_backtest_from_db,
    run_equal_weight_backtest_from_db,
    run_global_relative_strength_backtest_from_db,
    run_gtaa_backtest_from_db,
    run_quality_snapshot_backtest_from_db,
    run_quality_snapshot_strict_annual_backtest_from_db,
    run_quality_snapshot_strict_quarterly_prototype_backtest_from_db,
    run_quality_value_snapshot_strict_annual_backtest_from_db,
    run_quality_value_snapshot_strict_quarterly_prototype_backtest_from_db,
    run_risk_parity_trend_backtest_from_db,
    save_saved_portfolio,
    run_value_snapshot_strict_annual_backtest_from_db,
    run_value_snapshot_strict_quarterly_prototype_backtest_from_db,
)
from app.web.runtime.backtest import BacktestDataError, BacktestInputError
from app.web.runtime.backtest import (
    ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    GTAA_DEFAULT_SIGNAL_INTERVAL,
    ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
    ETF_OPERABILITY_DEFAULT_MIN_AUM_B,
    ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
    ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
    STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT,
    STRICT_BENCHMARK_CONTRACT_TICKER,
    STRICT_DEFAULT_BENCHMARK_CONTRACT,
    STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
    STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
    STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
    STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
    STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
    STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
    STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
)
from app.web.backtest_strategy_catalog import (
    COMPARE_STRATEGY_OPTIONS,
    SINGLE_STRATEGY_OPTIONS,
    display_name_to_selection,
    family_variant_options,
    resolve_concrete_strategy_display_name,
    strategy_key_to_display_name as catalog_strategy_key_to_display_name,
    strategy_key_to_selection,
)
from app.web.backtest_workflow_routes import (
    BACKTEST_ANALYSIS_MODE_SINGLE,
    BACKTEST_LEGACY_PANEL_OPTIONS,
    BACKTEST_STAGE_ANALYSIS,
    BACKTEST_STAGE_OPTIONS,
    PRACTICAL_VALIDATION_MODE_SELECTED_SOURCE,
    _route_target_to_stage_and_mode,
    _valid_backtest_route_targets,
)
from app.web.backtest_candidate_review_helpers import (
    CANDIDATE_REVIEW_DECISION_OPTIONS,
    CURRENT_CANDIDATE_RECORD_TYPE_OPTIONS,
    _build_current_candidate_registry_rows_for_display,
    _candidate_review_draft_from_bundle,
    _current_candidate_registry_selection_label,
    _queue_candidate_review_draft,
)
from finance.sample import (
    GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD,
    GTAA_DEFAULT_CRASH_GUARDRAIL_ENABLED,
    GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS,
    GTAA_DEFAULT_DEFENSIVE_TICKERS,
    STRICT_DEFAULT_REJECTION_HANDLING_MODE,
    STRICT_DEFAULT_WEIGHTING_MODE,
    STRICT_DEFAULT_DEFENSIVE_TICKERS,
    STRICT_DEFAULT_RISK_OFF_MODE,
    GTAA_DEFAULT_SCORE_LOOKBACK_MONTHS,
    GTAA_DEFAULT_RISK_OFF_MODE,
    GTAA_SCORE_RETURN_COLUMNS,
    GTAA_DEFAULT_SCORE_WEIGHTS,
    GTAA_DEFAULT_TREND_FILTER_WINDOW,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_CASH_TICKER,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_SCORE_LOOKBACK_MONTHS,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_SCORE_WEIGHTS,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_SIGNAL_INTERVAL,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_TICKERS,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_TOP,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_TREND_FILTER_WINDOW,
    GLOBAL_RELATIVE_STRENGTH_SCORE_RETURN_COLUMNS,
    STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
    STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
    STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
    STRICT_REJECTION_HANDLING_MODE_FILL_RETAIN_CASH,
    STRICT_REJECTION_HANDLING_MODE_FILL_REWEIGHT,
    STRICT_REJECTION_HANDLING_MODE_RETAIN_CASH,
    STRICT_REJECTION_HANDLING_MODE_REWEIGHT,
    STRICT_WEIGHTING_MODE_EQUAL,
    STRICT_WEIGHTING_MODE_RANK_TAPERED,
    STRICT_RISK_OFF_MODE_CASH,
    STRICT_RISK_OFF_MODE_DEFENSIVE,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    resolve_strict_rejection_handling_mode,
    strict_rejection_handling_mode_to_flags,
)
from finance.data.asset_profile import load_top_symbols_from_asset_profile
from finance.loaders import load_statement_coverage_summary, load_statement_shadow_coverage_summary
from finance.performance import make_monthly_weighted_portfolio


EQUAL_WEIGHT_PRESETS = {
    "Dividend ETFs": ["VIG", "SCHD", "DGRO", "GLD"],
    "Core ETFs": ["SPY", "QQQ", "TLT", "GLD"],
    "Big Tech": ["AAPL", "MSFT", "GOOG"],
}

GTAA_DEFAULT_TICKERS = ["SPY", "IWD", "IWM", "IWN", "MTUM", "EFA", "TLT", "IEF", "LQD", "PDBC", "VNQ", "GLD"]
GTAA_NO_COMMODITY_QUAL_USMV_TICKERS = ["SPY", "IWD", "IWM", "IWN", "MTUM", "EFA", "TLT", "IEF", "LQD", "VNQ", "GLD", "QUAL", "USMV"]
GTAA_QQQ_XLE_IAU_TIP_TICKERS = ["SPY", "IWD", "IWM", "IWN", "MTUM", "EFA", "TLT", "IEF", "LQD", "PDBC", "VNQ", "GLD", "QQQ", "XLE", "IAU", "TIP"]
GTAA_QQQ_QUAL_USMV_XLE_IAU_TICKERS = ["SPY", "IWD", "IWM", "IWN", "MTUM", "EFA", "TLT", "IEF", "LQD", "PDBC", "VNQ", "GLD", "QQQ", "QUAL", "USMV", "XLE", "IAU"]
GTAA_U3_COMMODITY_TICKERS = ["SPY", "QQQ", "XLE", "COMT", "IAU", "GLD", "QUAL", "USMV", "TIP", "TLT", "IEF", "LQD", "VNQ", "EFA", "MTUM"]
GTAA_U1_OFFENSIVE_TICKERS = ["SPY", "QQQ", "MTUM", "QUAL", "USMV", "VUG", "VTV", "RSP", "IAU", "XLE", "TIP", "TLT", "IEF", "LQD", "VNQ", "EFA"]
GTAA_U5_SMALLCAP_VALUE_TICKERS = ["SPY", "QQQ", "IWM", "IWN", "IWD", "MTUM", "QUAL", "USMV", "EFA", "VNQ", "TLT", "IEF", "LQD", "IAU", "XLE", "TIP"]

GTAA_PRESETS = {
    "GTAA Universe": GTAA_DEFAULT_TICKERS,
    "GTAA Universe (No Commodity + QUAL + USMV)": GTAA_NO_COMMODITY_QUAL_USMV_TICKERS,
    "GTAA Universe (QQQ + XLE + IAU + TIP)": GTAA_QQQ_XLE_IAU_TIP_TICKERS,
    "GTAA Universe (QQQ + QUAL + USMV + XLE + IAU)": GTAA_QQQ_QUAL_USMV_XLE_IAU_TICKERS,
    "GTAA Universe (U3 Commodity Candidate Base)": GTAA_U3_COMMODITY_TICKERS,
    "GTAA Universe (U1 Offensive Candidate Base)": GTAA_U1_OFFENSIVE_TICKERS,
    "GTAA Universe (U5 Smallcap Value Candidate Base)": GTAA_U5_SMALLCAP_VALUE_TICKERS,
}

GLOBAL_RELATIVE_STRENGTH_PRESETS = {
    "Global Relative Strength Core ETF Universe": list(GLOBAL_RELATIVE_STRENGTH_DEFAULT_TICKERS),
    "Global Relative Strength Compact Smoke Universe": ["SPY", "EFA", "TLT", "GLD"],
}

GTAA_RISK_OFF_MODE_LABELS = {
    "Cash Only": "cash_only",
    "Defensive Bond Preference": "defensive_bond_preference",
}
STRICT_RISK_OFF_MODE_LABELS = {
    "Cash Only": STRICT_RISK_OFF_MODE_CASH,
    "Defensive Sleeve Preference": STRICT_RISK_OFF_MODE_DEFENSIVE,
}
STRICT_WEIGHTING_MODE_LABELS = {
    "Equal Weight": STRICT_WEIGHTING_MODE_EQUAL,
    "Rank-Tapered": STRICT_WEIGHTING_MODE_RANK_TAPERED,
}
STRICT_REJECTION_HANDLING_MODE_LABELS = {
    "Reweight Survivors": STRICT_REJECTION_HANDLING_MODE_REWEIGHT,
    "Retain Unfilled Slots As Cash": STRICT_REJECTION_HANDLING_MODE_RETAIN_CASH,
    "Fill Then Reweight Survivors": STRICT_REJECTION_HANDLING_MODE_FILL_REWEIGHT,
    "Fill Then Retain Unfilled Slots As Cash": STRICT_REJECTION_HANDLING_MODE_FILL_RETAIN_CASH,
}
STRICT_RISK_OFF_MODE_EXPLANATIONS = {
    STRICT_RISK_OFF_MODE_CASH: "포트폴리오 전체를 쉬어야 할 때 100% 현금으로 둡니다.",
    STRICT_RISK_OFF_MODE_DEFENSIVE: "포트폴리오 전체를 쉬어야 할 때 현금 대신 지정한 방어 ETF sleeve로 이동합니다.",
}
STRICT_WEIGHTING_MODE_EXPLANATIONS = {
    STRICT_WEIGHTING_MODE_EQUAL: "최종 선택된 종목을 동일 비중으로 나눠 담습니다.",
    STRICT_WEIGHTING_MODE_RANK_TAPERED: "최종 선택된 종목 중 상위 rank에 조금 더 높은 비중을 주되 과도한 집중은 피합니다.",
}
STRICT_REJECTION_HANDLING_MODE_EXPLANATIONS = {
    STRICT_REJECTION_HANDLING_MODE_REWEIGHT: "Trend Filter로 일부 종목이 탈락하면, 남은 생존 종목들끼리 다시 100% 재배분합니다.",
    STRICT_REJECTION_HANDLING_MODE_RETAIN_CASH: "Trend Filter로 일부 종목이 탈락하면, 비어 있는 슬롯 비중만큼 현금으로 남깁니다.",
    STRICT_REJECTION_HANDLING_MODE_FILL_REWEIGHT: "먼저 다음 순위의 추세 통과 종목으로 빈 슬롯을 채우고, 그래도 남은 슬롯은 생존 종목들끼리 다시 재배분합니다.",
    STRICT_REJECTION_HANDLING_MODE_FILL_RETAIN_CASH: "먼저 다음 순위의 추세 통과 종목으로 빈 슬롯을 채우고, 그래도 남은 슬롯은 현금으로 남깁니다.",
}
SNAPSHOT_SELECTION_HISTORY_STRATEGY_KEYS = {
    "quality_snapshot",
    "quality_snapshot_strict_annual",
    "quality_snapshot_strict_quarterly_prototype",
    "value_snapshot_strict_annual",
    "value_snapshot_strict_quarterly_prototype",
    "quality_value_snapshot_strict_annual",
    "quality_value_snapshot_strict_quarterly_prototype",
}
GTAA_SCORE_WEIGHT_LABELS = [
    ("1MReturn", "1M"),
    ("3MReturn", "3M"),
    ("6MReturn", "6M"),
    ("12MReturn", "12M"),
]

RISK_PARITY_PRESETS = {
    "Risk Parity Universe": ["SPY", "TLT", "GLD", "IEF", "LQD"],
}

DUAL_MOMENTUM_PRESETS = {
    "Dual Momentum Universe": ["QQQ", "SPY", "IWM", "SOXX", "BIL"],
}

ETF_GUARDRAIL_STRATEGY_KEYS = {"gtaa", "risk_parity_trend", "dual_momentum"}

QUALITY_BROAD_PRESETS = {
    "Big Tech Quality Trial": ["AAPL", "MSFT", "GOOG"],
}

QUALITY_STRICT_DEFAULT_FACTORS = [
    "roe",
    "roa",
    "net_margin",
    "asset_turnover",
    "current_ratio",
]

QUALITY_STRICT_LEGACY_DEFAULT_FACTORS = [
    "roe",
    "gross_margin",
    "operating_margin",
    "debt_ratio",
]

QUALITY_STRICT_FACTOR_OPTIONS = [
    "roe",
    "roa",
    "net_margin",
    "asset_turnover",
    "current_ratio",
    "cash_ratio",
    "operating_margin",
    "interest_coverage",
    "ocf_margin",
    "fcf_margin",
    "net_debt_to_equity",
    "debt_to_assets",
    "debt_ratio",
    "gross_margin",
]

VALUE_STRICT_DEFAULT_FACTORS = [
    "book_to_market",
    "earnings_yield",
    "sales_yield",
    "ocf_yield",
    "operating_income_yield",
]

VALUE_STRICT_LEGACY_DEFAULT_FACTORS = [
    "per",
    "pbr",
    "sales_yield",
    "earnings_yield",
]

VALUE_STRICT_FACTOR_OPTIONS = [
    "book_to_market",
    "earnings_yield",
    "sales_yield",
    "ocf_yield",
    "fcf_yield",
    "operating_income_yield",
    "liquidation_value",
    "per",
    "pbr",
    "psr",
    "pcr",
    "pfcr",
    "ev_ebit",
    "por",
]

STRICT_TREND_FILTER_DEFAULT_ENABLED = False
STRICT_TREND_FILTER_DEFAULT_WINDOW = 200
STRICT_MARKET_REGIME_DEFAULT_ENABLED = False
STRICT_MARKET_REGIME_DEFAULT_WINDOW = 200
STRICT_MARKET_REGIME_DEFAULT_BENCHMARK = "SPY"
STRICT_MARKET_REGIME_BENCHMARK_OPTIONS = ["SPY", "QQQ", "VTI", "IWM"]
DEFAULT_BACKTEST_END_DATE = date.today()
CURRENT_CANDIDATE_COMPARE_DEFAULT_START = date(2016, 1, 1)
CURRENT_CANDIDATE_COMPARE_DEFAULT_END = date(2026, 4, 1)
BACKTEST_PANEL_OPTIONS = list(BACKTEST_STAGE_OPTIONS) + [
    panel for panel in BACKTEST_LEGACY_PANEL_OPTIONS if panel not in set(BACKTEST_STAGE_OPTIONS)
]
BACKTEST_WORKFLOW_PANEL_OPTIONS = list(BACKTEST_STAGE_OPTIONS)
STATIC_MANAGED_RESEARCH_UNIVERSE = "static_managed_research"
HISTORICAL_DYNAMIC_PIT_UNIVERSE = "historical_dynamic_pit"
STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS = {
    "Static Managed Research Universe": STATIC_MANAGED_RESEARCH_UNIVERSE,
    "Historical Dynamic PIT Universe": HISTORICAL_DYNAMIC_PIT_UNIVERSE,
}
STRICT_BENCHMARK_CONTRACT_LABELS = {
    "Ticker Benchmark": STRICT_BENCHMARK_CONTRACT_TICKER,
    "Candidate Universe Equal-Weight": STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT,
}

QUALITY_STRICT_TOP300_TICKERS = [
    "NVDA", "GOOGL", "GOOG", "AAPL", "MSFT", "AMZN", "META", "TSLA", "AVGO", "WMT",
    "LLY", "JPM", "V", "XOM", "JNJ", "MA", "MU", "COST", "ORCL", "ABBV",
    "BAC", "HD", "PG", "CVX", "PLTR", "NFLX", "KO", "AMD", "CAT", "CSCO",
    "MRK", "WFC", "LRCX", "MS", "GS", "PM", "AMAT", "IBM", "RTX", "UNH",
    "INTC", "AXP", "MCD", "PEP", "TMUS", "TMO", "GEV", "C", "AMGN", "TXN",
    "VZ", "T", "ABT", "SCHW", "NEE", "CRM", "DIS", "BA", "APH", "KLAC",
    "GILD", "ANET", "TJX", "ISRG", "BX", "SCCO", "BLK", "QCOM", "HON", "LOW",
    "APP", "UBER", "ADI", "DHR", "BKNG", "PFE", "DE", "UNP", "LMT", "COF",
    "SYK", "SPGI", "BSX", "COP", "NEM", "WELL", "IBKR", "PLD", "PH", "VRTX",
    "CMCSA", "HCA", "INTU", "PGR", "BMY", "ADBE", "PANW", "NOW", "SBUX", "MO",
    "CRWD", "CME", "MCK", "SO", "NOC", "UPS", "CVS", "CEG", "GLW", "PNC",
    "GD", "DUK", "KKR", "USB", "NKE", "FCX", "MRSH", "WDC", "ICE", "SHW",
    "SNDK", "WM", "RCL", "CVNA", "MAR", "ADP", "DASH", "EMR", "MMM", "FDX",
    "BK", "CMI", "ORLY", "ITW", "REGN", "MCO", "AMT", "WMB", "SNPS", "MNST",
    "ECL", "GM", "ABNB", "EQIX", "DELL", "MDLZ", "CTAS", "BAM", "ELV", "SLB",
    "CL", "HOOD", "EPD", "NSC", "APO", "CI", "SPG", "CDNS", "CSX", "HLT",
    "AEP", "VRT", "TDG", "PWR", "TFC", "COR", "PCAR", "MSI", "RSG", "WBD",
    "KMI", "TRV", "LHX", "MRVL", "ET", "ROST", "PSX", "APD", "AZO", "FTNT",
    "EOG", "VLO", "NET", "BDX", "MPC", "SNOW", "RKT", "MPWR", "DLR", "FITB",
    "BKR", "AFL", "SRE", "O", "MPLX", "ZTS", "GWW", "F", "AJG", "ALL",
    "ADSK", "FAST", "URI", "CMG", "D", "AME", "CARR", "CAH", "FERG", "TGT",
    "MET", "CTVA", "IDXX", "AU", "EA", "PSA", "OKE", "NDAQ", "ROK", "VST",
    "CBRE", "COIN", "EW", "FANG", "CRWV", "HEI", "DAL", "LNG", "XEL", "OXY",
    "WDAY", "DHI", "EXC", "RBLX", "CCL", "YUM", "TER", "ETR", "KR", "NUE",
    "TRGP", "ARES", "MCHP", "ALNY", "FIX", "MSCI", "AMP", "EBAY", "AIG", "CUK",
    "DDOG", "EL", "WAB", "HSY", "VMC", "ODFL", "SYY", "LVS", "PEG", "MLM",
    "RKLB", "BE", "KEYS", "PYPL", "HIG", "CIEN", "ED", "ROP", "KDP", "IR",
    "HBAN", "RMD", "TTWO", "CPRT", "MDLN", "STT", "WEC", "CCI", "MTB", "MSTR",
    "VTR", "CTSH", "PRU", "UAL", "COHR", "GEHC", "AXON", "CPNG", "XYZ", "LITE",
    "OTIS", "PAYX", "EQT", "PCG", "XYL", "IQV", "KVUE", "KMB", "UI", "INSM",
]

STRICT_ANNUAL_MANAGED_PRESET_SPECS = {
    "US Statement Coverage 100": 100,
    "US Statement Coverage 300": 300,
    "US Statement Coverage 500": 500,
    "US Statement Coverage 1000": 1000,
}
STRICT_ANNUAL_SINGLE_DEFAULT_PRESET = "US Statement Coverage 300"
STRICT_ANNUAL_COMPARE_DEFAULT_PRESET = "US Statement Coverage 100"
STRICT_QUARTERLY_PROTOTYPE_DEFAULT_PRESET = "US Statement Coverage 100"


@lru_cache(maxsize=1)
def _load_managed_strict_annual_presets() -> dict[str, list[str]]:
    presets: dict[str, list[str]] = {
        "Big Tech Strict Trial": ["AAPL", "MSFT", "GOOG"],
    }

    for preset_name, limit in STRICT_ANNUAL_MANAGED_PRESET_SPECS.items():
        try:
            symbols = load_top_symbols_from_asset_profile(
                "stock",
                country="United States",
                on_filter=True,
                limit=limit,
                order_by="market_cap_desc",
            )
        except Exception:
            symbols = []
        if symbols:
            presets[preset_name] = symbols

    if "US Statement Coverage 100" not in presets:
        presets["US Statement Coverage 100"] = QUALITY_STRICT_TOP300_TICKERS[:100]
    if "US Statement Coverage 300" not in presets:
        presets["US Statement Coverage 300"] = QUALITY_STRICT_TOP300_TICKERS
    if "US Statement Coverage 500" not in presets:
        presets["US Statement Coverage 500"] = presets["US Statement Coverage 300"].copy()
    if "US Statement Coverage 1000" not in presets:
        presets["US Statement Coverage 1000"] = presets["US Statement Coverage 500"].copy()

    ordered_names = [
        "US Statement Coverage 100",
        "US Statement Coverage 300",
        "US Statement Coverage 500",
        "US Statement Coverage 1000",
        "Big Tech Strict Trial",
    ]
    return {name: presets[name] for name in ordered_names if name in presets}


QUALITY_STRICT_PRESETS = _load_managed_strict_annual_presets()

VALUE_STRICT_PRESETS = QUALITY_STRICT_PRESETS

SINGLE_FAMILY_VARIANT_SESSION_KEYS = {
    "Quality": "single_quality_variant",
    "Value": "single_value_variant",
    "Quality + Value": "single_quality_value_variant",
}

COMPARE_FAMILY_VARIANT_SESSION_KEYS = {
    "Quality": "compare_quality_variant",
    "Value": "compare_value_variant",
    "Quality + Value": "compare_quality_value_variant",
}


@lru_cache(maxsize=128)
def _load_statement_shadow_coverage_preview(symbols_key: tuple[str, ...], freq: str) -> dict[str, Any]:
    symbols = [str(symbol).strip().upper() for symbol in symbols_key if str(symbol).strip()]
    if not symbols:
        return {
            "requested_count": 0,
            "covered_count": 0,
            "row_count": 0,
            "min_period_end": None,
            "max_period_end": None,
            "median_rows_per_symbol": 0,
            "min_available_at": None,
            "covered_symbols": [],
            "missing_symbols": [],
            "missing_count": 0,
            "raw_present_missing_count": 0,
            "no_raw_missing_count": 0,
            "missing_rows": [],
            "refresh_payload": None,
            "shadow_rebuild_payload": None,
        }

    shadow_summary = load_statement_shadow_coverage_summary(symbols=symbols, freq=freq)
    if not shadow_summary.empty:
        working = shadow_summary.copy()
        working["symbol"] = working["symbol"].astype(str).str.upper()
        working["min_period_end"] = pd.to_datetime(working["min_period_end"], errors="coerce")
        working["max_period_end"] = pd.to_datetime(working["max_period_end"], errors="coerce")
        working["min_available_at"] = pd.to_datetime(working["min_available_at"], errors="coerce")
        working["max_available_at"] = pd.to_datetime(working["max_available_at"], errors="coerce")
    else:
        working = pd.DataFrame(
            columns=[
                "symbol",
                "shadow_rows",
                "min_period_end",
                "max_period_end",
                "min_available_at",
                "max_available_at",
            ]
        )

    rows_per_symbol = working["shadow_rows"] if not working.empty and "shadow_rows" in working.columns else pd.Series(dtype="int64")
    min_available_at = working["min_available_at"].min() if not working.empty and working["min_available_at"].notna().any() else None

    covered_symbols = sorted(working["symbol"].dropna().astype(str).str.upper().unique().tolist()) if not working.empty else []
    covered_symbol_set = set(covered_symbols)
    missing_symbols = [symbol for symbol in symbols if symbol not in covered_symbol_set]

    raw_summary = load_statement_coverage_summary(symbols=missing_symbols, freq=freq) if missing_symbols else pd.DataFrame()
    if not raw_summary.empty:
        raw_summary = raw_summary.copy()
        raw_summary["symbol"] = raw_summary["symbol"].astype(str).str.upper()
        raw_summary["min_period_end"] = pd.to_datetime(raw_summary["min_period_end"], errors="coerce")
        raw_summary["max_period_end"] = pd.to_datetime(raw_summary["max_period_end"], errors="coerce")
        raw_summary["min_available_at"] = pd.to_datetime(raw_summary["min_available_at"], errors="coerce")
        raw_summary["max_available_at"] = pd.to_datetime(raw_summary["max_available_at"], errors="coerce")
    raw_map = {
        str(row["symbol"]).upper(): row
        for _, row in raw_summary.iterrows()
        if row.get("symbol") is not None
    }

    missing_rows: list[dict[str, Any]] = []
    raw_present_missing_symbols: list[str] = []
    no_raw_missing_symbols: list[str] = []
    for symbol in missing_symbols:
        raw_row = raw_map.get(symbol)
        if raw_row is not None:
            raw_present_missing_symbols.append(symbol)
            diagnosis = "raw_statement_present_but_shadow_missing"
            recommended_action = (
                "Raw strict statement rows already exist. Re-run Extended Statement Refresh under the current shadow-rebuild path first; "
                "if the symbol still remains uncovered, inspect the statement-shadow coverage hardening path."
            )
        else:
            no_raw_missing_symbols.append(symbol)
            diagnosis = "no_raw_statement_coverage"
            recommended_action = (
                "No strict raw statement coverage is currently stored for this symbol. "
                "Run Extended Statement Refresh or Financial Statement Ingestion first."
            )

        missing_rows.append(
            {
                "Symbol": symbol,
                "Coverage Gap Status": diagnosis,
                "Raw Strict Rows": int(raw_row["strict_rows"]) if raw_row is not None and pd.notna(raw_row.get("strict_rows")) else 0,
                "Raw Earliest Period": (
                    pd.to_datetime(raw_row["min_period_end"]).strftime("%Y-%m-%d")
                    if raw_row is not None and pd.notna(raw_row.get("min_period_end"))
                    else "-"
                ),
                "Raw Latest Period": (
                    pd.to_datetime(raw_row["max_period_end"]).strftime("%Y-%m-%d")
                    if raw_row is not None and pd.notna(raw_row.get("max_period_end"))
                    else "-"
                ),
                "Raw Latest Available": (
                    pd.to_datetime(raw_row["max_available_at"]).strftime("%Y-%m-%d")
                    if raw_row is not None and pd.notna(raw_row.get("max_available_at"))
                    else "-"
                ),
                "Recommended Action": recommended_action,
            }
        )

    refresh_payload = None
    if no_raw_missing_symbols:
        symbols_csv = ",".join(no_raw_missing_symbols)
        refresh_payload = {
            "symbols_csv": symbols_csv,
            "payload_block": (
                f"symbols={symbols_csv}\n"
                f"freq={freq}\n"
                "periods=0\n"
                f"period={freq}"
            ),
        }

    shadow_rebuild_payload = None
    if raw_present_missing_symbols:
        rebuild_csv = ",".join(raw_present_missing_symbols)
        shadow_rebuild_payload = {
            "symbols_csv": rebuild_csv,
            "payload_block": (
                f"symbols={rebuild_csv}\n"
                f"freq={freq}"
            ),
        }

    return {
        "requested_count": len(symbols),
        "covered_count": int(len(covered_symbols)),
        "row_count": int(rows_per_symbol.sum()) if not rows_per_symbol.empty else 0,
        "min_period_end": working["min_period_end"].min() if not working.empty else None,
        "max_period_end": working["max_period_end"].max() if not working.empty else None,
        "median_rows_per_symbol": int(rows_per_symbol.median()) if not rows_per_symbol.empty else 0,
        "min_available_at": min_available_at,
        "covered_symbols": covered_symbols,
        "missing_symbols": missing_symbols,
        "missing_count": len(missing_symbols),
        "raw_present_missing_count": len(raw_present_missing_symbols),
        "no_raw_missing_count": len(no_raw_missing_symbols),
        "missing_rows": missing_rows,
        "refresh_payload": refresh_payload,
        "shadow_rebuild_payload": shadow_rebuild_payload,
    }


def clear_backtest_preview_caches() -> None:
    _load_statement_shadow_coverage_preview.cache_clear()


def _queue_ingestion_prefill(
    *,
    target: str,
    symbols_csv: str,
    freq: str,
    notice: str,
) -> None:
    widget_values: dict[str, Any] = {}
    if target == "extended_statement_refresh":
        widget_values = {
            "ext_period_input": freq,
            "ext_periods_input": 0,
        }
    elif target == "statement_shadow_rebuild":
        widget_values = {
            "shadow_rebuild_freq_input": freq,
        }
    elif target == "statement_coverage_diagnosis":
        widget_values = {
            "statement_coverage_diag_freq": freq,
            "statement_coverage_diag_sample_size": 2,
        }

    st.session_state.ingestion_prefill_request = {
        "target": target,
        "symbols_csv": symbols_csv,
        "widget_values": widget_values,
        "notice": notice,
    }
    st.session_state.backtest_prefill_notice = notice
    st.session_state.backtest_operator_bridge_notice = (
        f"{notice} `Coverage Gap Drilldown` 표는 coarse 상태만 보여주고, "
        "세부 원인 분류는 `Statement Coverage Diagnosis` 카드에서 확인합니다."
    )


def _init_backtest_state() -> None:
    if "backtest_last_bundle" not in st.session_state:
        st.session_state.backtest_last_bundle = None
    if "backtest_last_error" not in st.session_state:
        st.session_state.backtest_last_error = None
    if "backtest_last_error_kind" not in st.session_state:
        st.session_state.backtest_last_error_kind = None
    if "backtest_compare_bundles" not in st.session_state:
        st.session_state.backtest_compare_bundles = None
    if "backtest_compare_error" not in st.session_state:
        st.session_state.backtest_compare_error = None
    if "backtest_compare_error_kind" not in st.session_state:
        st.session_state.backtest_compare_error_kind = None
    if "backtest_weighted_bundle" not in st.session_state:
        st.session_state.backtest_weighted_bundle = None
    if "backtest_weighted_error" not in st.session_state:
        st.session_state.backtest_weighted_error = None
    if "backtest_prefill_payload" not in st.session_state:
        st.session_state.backtest_prefill_payload = None
    if "backtest_prefill_pending" not in st.session_state:
        st.session_state.backtest_prefill_pending = False
    if "backtest_prefill_notice" not in st.session_state:
        st.session_state.backtest_prefill_notice = None
    if "backtest_operator_bridge_notice" not in st.session_state:
        st.session_state.backtest_operator_bridge_notice = None
    if "backtest_prefill_strategy_choice" not in st.session_state:
        st.session_state.backtest_prefill_strategy_choice = None
    if "backtest_prefill_strategy_variant" not in st.session_state:
        st.session_state.backtest_prefill_strategy_variant = None
    if "backtest_compare_prefill_payload" not in st.session_state:
        st.session_state.backtest_compare_prefill_payload = None
    if "backtest_compare_prefill_pending" not in st.session_state:
        st.session_state.backtest_compare_prefill_pending = False
    if "backtest_compare_prefill_notice" not in st.session_state:
        st.session_state.backtest_compare_prefill_notice = None
    if "backtest_compare_source_context" not in st.session_state:
        st.session_state.backtest_compare_source_context = None
    if "backtest_compare_workspace_mode" not in st.session_state:
        st.session_state.backtest_compare_workspace_mode = "전략 비교"
    if "backtest_compare_workspace_mode_request" not in st.session_state:
        st.session_state.backtest_compare_workspace_mode_request = None
    if "backtest_compare_result_notice" not in st.session_state:
        st.session_state.backtest_compare_result_notice = None
    if "backtest_weighted_portfolio_prefill" not in st.session_state:
        st.session_state.backtest_weighted_portfolio_prefill = None
    if "backtest_saved_portfolio_notice" not in st.session_state:
        st.session_state.backtest_saved_portfolio_notice = None
    if "backtest_candidate_review_draft" not in st.session_state:
        st.session_state.backtest_candidate_review_draft = None
    if "backtest_candidate_review_draft_notice" not in st.session_state:
        st.session_state.backtest_candidate_review_draft_notice = None
    if "backtest_candidate_review_note_notice" not in st.session_state:
        st.session_state.backtest_candidate_review_note_notice = None
    if "backtest_analysis_mode" not in st.session_state:
        st.session_state.backtest_analysis_mode = BACKTEST_ANALYSIS_MODE_SINGLE
    if "backtest_practical_validation_mode" not in st.session_state:
        st.session_state.backtest_practical_validation_mode = PRACTICAL_VALIDATION_MODE_SELECTED_SOURCE
    if "backtest_practical_validation_source" not in st.session_state:
        st.session_state.backtest_practical_validation_source = None
    if "backtest_practical_validation_notice" not in st.session_state:
        st.session_state.backtest_practical_validation_notice = None
    if "backtest_active_stage" not in st.session_state:
        st.session_state.backtest_active_stage = BACKTEST_STAGE_ANALYSIS
    if "backtest_active_panel" not in st.session_state:
        st.session_state.backtest_active_panel = BACKTEST_STAGE_ANALYSIS
    if "backtest_workflow_active_panel" not in st.session_state:
        st.session_state.backtest_workflow_active_panel = BACKTEST_STAGE_ANALYSIS
    if "backtest_requested_panel" not in st.session_state:
        st.session_state.backtest_requested_panel = None
    requested_panel = st.session_state.get("backtest_requested_panel")
    if requested_panel in _valid_backtest_route_targets():
        route = _route_target_to_stage_and_mode(str(requested_panel))
        requested_stage = str(route.get("stage") or BACKTEST_STAGE_ANALYSIS)
        st.session_state.backtest_active_stage = requested_stage
        st.session_state.backtest_active_panel = requested_stage
        st.session_state.backtest_workflow_active_panel = requested_stage
        if route.get("analysis_mode"):
            st.session_state.backtest_analysis_mode = route["analysis_mode"]
        if route.get("practical_mode"):
            st.session_state.backtest_practical_validation_mode = route["practical_mode"]
        st.session_state.backtest_requested_panel = None
    active_panel = st.session_state.get("backtest_active_panel")
    if active_panel in set(BACKTEST_WORKFLOW_PANEL_OPTIONS):
        st.session_state.backtest_active_stage = active_panel
        st.session_state.backtest_workflow_active_panel = active_panel
    elif active_panel in _valid_backtest_route_targets():
        route = _route_target_to_stage_and_mode(str(active_panel))
        active_stage = str(route.get("stage") or BACKTEST_STAGE_ANALYSIS)
        st.session_state.backtest_active_stage = active_stage
        st.session_state.backtest_active_panel = active_stage
        st.session_state.backtest_workflow_active_panel = active_stage
        if route.get("analysis_mode"):
            st.session_state.backtest_analysis_mode = route["analysis_mode"]
        if route.get("practical_mode"):
            st.session_state.backtest_practical_validation_mode = route["practical_mode"]
    else:
        st.session_state.backtest_active_stage = BACKTEST_STAGE_ANALYSIS
        st.session_state.backtest_active_panel = BACKTEST_STAGE_ANALYSIS
        st.session_state.backtest_workflow_active_panel = BACKTEST_STAGE_ANALYSIS
    if "qss_end" not in st.session_state:
        st.session_state["qss_end"] = DEFAULT_BACKTEST_END_DATE
    if "qss_timeframe" not in st.session_state:
        st.session_state["qss_timeframe"] = "1d"
    if "vss_end" not in st.session_state:
        st.session_state["vss_end"] = DEFAULT_BACKTEST_END_DATE
    if "vss_timeframe" not in st.session_state:
        st.session_state["vss_timeframe"] = "1d"
    if "qvss_end" not in st.session_state:
        st.session_state["qvss_end"] = DEFAULT_BACKTEST_END_DATE
    if "qvss_timeframe" not in st.session_state:
        st.session_state["qvss_timeframe"] = "1d"
    if "qsqp_end" not in st.session_state:
        st.session_state["qsqp_end"] = DEFAULT_BACKTEST_END_DATE
    if "qsqp_timeframe" not in st.session_state:
        st.session_state["qsqp_timeframe"] = "1d"
    if "vsqp_end" not in st.session_state:
        st.session_state["vsqp_end"] = DEFAULT_BACKTEST_END_DATE
    if "vsqp_timeframe" not in st.session_state:
        st.session_state["vsqp_timeframe"] = "1d"
    if "qvqp_end" not in st.session_state:
        st.session_state["qvqp_end"] = DEFAULT_BACKTEST_END_DATE
    if "qvqp_timeframe" not in st.session_state:
        st.session_state["qvqp_timeframe"] = "1d"
    for quarterly_prefix in ("qsqp", "vsqp", "qvqp"):
        if f"{quarterly_prefix}_weighting_mode" not in st.session_state:
            st.session_state[f"{quarterly_prefix}_weighting_mode"] = _strict_weighting_mode_value_to_label(
                STRICT_DEFAULT_WEIGHTING_MODE
            )
        if f"{quarterly_prefix}_rejected_slot_handling_mode" not in st.session_state:
            st.session_state[f"{quarterly_prefix}_rejected_slot_handling_mode"] = _strict_rejection_handling_mode_value_to_label(
                STRICT_DEFAULT_REJECTION_HANDLING_MODE
            )
        if f"{quarterly_prefix}_rejected_slot_fill_enabled" not in st.session_state:
            st.session_state[f"{quarterly_prefix}_rejected_slot_fill_enabled"] = STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED
        if f"{quarterly_prefix}_partial_cash_retention_enabled" not in st.session_state:
            st.session_state[f"{quarterly_prefix}_partial_cash_retention_enabled"] = STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED
        if f"{quarterly_prefix}_risk_off_mode" not in st.session_state:
            st.session_state[f"{quarterly_prefix}_risk_off_mode"] = _strict_risk_off_mode_value_to_label(
                STRICT_DEFAULT_RISK_OFF_MODE
            )
        if f"{quarterly_prefix}_defensive_tickers" not in st.session_state:
            st.session_state[f"{quarterly_prefix}_defensive_tickers"] = ",".join(STRICT_DEFAULT_DEFENSIVE_TICKERS)
    if "qss_trend_filter_enabled" not in st.session_state:
        st.session_state["qss_trend_filter_enabled"] = STRICT_TREND_FILTER_DEFAULT_ENABLED
    if "qss_trend_filter_window" not in st.session_state:
        st.session_state["qss_trend_filter_window"] = STRICT_TREND_FILTER_DEFAULT_WINDOW
    if "qss_weighting_mode" not in st.session_state:
        st.session_state["qss_weighting_mode"] = _strict_weighting_mode_value_to_label(STRICT_DEFAULT_WEIGHTING_MODE)
    if "qss_rejected_slot_handling_mode" not in st.session_state:
        st.session_state["qss_rejected_slot_handling_mode"] = _strict_rejection_handling_mode_value_to_label(
            STRICT_DEFAULT_REJECTION_HANDLING_MODE
        )
    if "qss_rejected_slot_fill_enabled" not in st.session_state:
        st.session_state["qss_rejected_slot_fill_enabled"] = STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED
    if "qss_partial_cash_retention_enabled" not in st.session_state:
        st.session_state["qss_partial_cash_retention_enabled"] = STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED
    if "qss_risk_off_mode" not in st.session_state:
        st.session_state["qss_risk_off_mode"] = _strict_risk_off_mode_value_to_label(STRICT_DEFAULT_RISK_OFF_MODE)
    if "qss_defensive_tickers" not in st.session_state:
        st.session_state["qss_defensive_tickers"] = ",".join(STRICT_DEFAULT_DEFENSIVE_TICKERS)
    if "qss_market_regime_enabled" not in st.session_state:
        st.session_state["qss_market_regime_enabled"] = STRICT_MARKET_REGIME_DEFAULT_ENABLED
    if "qss_market_regime_window" not in st.session_state:
        st.session_state["qss_market_regime_window"] = STRICT_MARKET_REGIME_DEFAULT_WINDOW
    if "qss_market_regime_benchmark" not in st.session_state:
        st.session_state["qss_market_regime_benchmark"] = STRICT_MARKET_REGIME_DEFAULT_BENCHMARK
    if "qss_underperformance_guardrail_enabled" not in st.session_state:
        st.session_state["qss_underperformance_guardrail_enabled"] = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED
    if "qss_underperformance_guardrail_window_months" not in st.session_state:
        st.session_state["qss_underperformance_guardrail_window_months"] = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS
    if "qss_underperformance_guardrail_threshold" not in st.session_state:
        st.session_state["qss_underperformance_guardrail_threshold"] = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD * 100.0
    if "qss_drawdown_guardrail_enabled" not in st.session_state:
        st.session_state["qss_drawdown_guardrail_enabled"] = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED
    if "qss_drawdown_guardrail_window_months" not in st.session_state:
        st.session_state["qss_drawdown_guardrail_window_months"] = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS
    if "qss_drawdown_guardrail_strategy_threshold" not in st.session_state:
        st.session_state["qss_drawdown_guardrail_strategy_threshold"] = (
            STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD * 100.0
        )
    if "qss_drawdown_guardrail_gap_threshold" not in st.session_state:
        st.session_state["qss_drawdown_guardrail_gap_threshold"] = (
            STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD * 100.0
        )
    if "qss_min_history_months_filter" not in st.session_state:
        st.session_state["qss_min_history_months_filter"] = STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS
    if "qss_min_avg_dollar_volume_20d_m_filter" not in st.session_state:
        st.session_state["qss_min_avg_dollar_volume_20d_m_filter"] = STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M
    if "qss_benchmark_contract" not in st.session_state:
        st.session_state["qss_benchmark_contract"] = "Ticker Benchmark"
    if "qss_promotion_min_benchmark_coverage" not in st.session_state:
        st.session_state["qss_promotion_min_benchmark_coverage"] = STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE * 100.0
    if "qss_promotion_min_net_cagr_spread" not in st.session_state:
        st.session_state["qss_promotion_min_net_cagr_spread"] = STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD * 100.0
    if "qss_promotion_min_liquidity_clean_coverage" not in st.session_state:
        st.session_state["qss_promotion_min_liquidity_clean_coverage"] = (
            STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE * 100.0
        )
    if "qss_promotion_max_underperformance_share" not in st.session_state:
        st.session_state["qss_promotion_max_underperformance_share"] = (
            STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE * 100.0
        )
    if "qss_promotion_min_worst_rolling_excess_return" not in st.session_state:
        st.session_state["qss_promotion_min_worst_rolling_excess_return"] = (
            STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN * 100.0
        )
    if "qss_promotion_max_strategy_drawdown" not in st.session_state:
        st.session_state["qss_promotion_max_strategy_drawdown"] = (
            STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN * 100.0
        )
    if "qss_promotion_max_drawdown_gap_vs_benchmark" not in st.session_state:
        st.session_state["qss_promotion_max_drawdown_gap_vs_benchmark"] = (
            STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK * 100.0
        )
    if "vss_trend_filter_enabled" not in st.session_state:
        st.session_state["vss_trend_filter_enabled"] = STRICT_TREND_FILTER_DEFAULT_ENABLED
    if "vss_trend_filter_window" not in st.session_state:
        st.session_state["vss_trend_filter_window"] = STRICT_TREND_FILTER_DEFAULT_WINDOW
    if "vss_weighting_mode" not in st.session_state:
        st.session_state["vss_weighting_mode"] = _strict_weighting_mode_value_to_label(STRICT_DEFAULT_WEIGHTING_MODE)
    if "vss_rejected_slot_handling_mode" not in st.session_state:
        st.session_state["vss_rejected_slot_handling_mode"] = _strict_rejection_handling_mode_value_to_label(
            STRICT_DEFAULT_REJECTION_HANDLING_MODE
        )
    if "vss_rejected_slot_fill_enabled" not in st.session_state:
        st.session_state["vss_rejected_slot_fill_enabled"] = STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED
    if "vss_partial_cash_retention_enabled" not in st.session_state:
        st.session_state["vss_partial_cash_retention_enabled"] = STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED
    if "vss_risk_off_mode" not in st.session_state:
        st.session_state["vss_risk_off_mode"] = _strict_risk_off_mode_value_to_label(STRICT_DEFAULT_RISK_OFF_MODE)
    if "vss_defensive_tickers" not in st.session_state:
        st.session_state["vss_defensive_tickers"] = ",".join(STRICT_DEFAULT_DEFENSIVE_TICKERS)
    if "vss_market_regime_enabled" not in st.session_state:
        st.session_state["vss_market_regime_enabled"] = STRICT_MARKET_REGIME_DEFAULT_ENABLED
    if "vss_market_regime_window" not in st.session_state:
        st.session_state["vss_market_regime_window"] = STRICT_MARKET_REGIME_DEFAULT_WINDOW
    if "vss_market_regime_benchmark" not in st.session_state:
        st.session_state["vss_market_regime_benchmark"] = STRICT_MARKET_REGIME_DEFAULT_BENCHMARK
    if "vss_underperformance_guardrail_enabled" not in st.session_state:
        st.session_state["vss_underperformance_guardrail_enabled"] = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED
    if "vss_underperformance_guardrail_window_months" not in st.session_state:
        st.session_state["vss_underperformance_guardrail_window_months"] = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS
    if "vss_underperformance_guardrail_threshold" not in st.session_state:
        st.session_state["vss_underperformance_guardrail_threshold"] = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD * 100.0
    if "vss_drawdown_guardrail_enabled" not in st.session_state:
        st.session_state["vss_drawdown_guardrail_enabled"] = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED
    if "vss_drawdown_guardrail_window_months" not in st.session_state:
        st.session_state["vss_drawdown_guardrail_window_months"] = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS
    if "vss_drawdown_guardrail_strategy_threshold" not in st.session_state:
        st.session_state["vss_drawdown_guardrail_strategy_threshold"] = (
            STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD * 100.0
        )
    if "vss_drawdown_guardrail_gap_threshold" not in st.session_state:
        st.session_state["vss_drawdown_guardrail_gap_threshold"] = (
            STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD * 100.0
        )
    if "vss_min_history_months_filter" not in st.session_state:
        st.session_state["vss_min_history_months_filter"] = STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS
    if "vss_min_avg_dollar_volume_20d_m_filter" not in st.session_state:
        st.session_state["vss_min_avg_dollar_volume_20d_m_filter"] = STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M
    if "vss_benchmark_contract" not in st.session_state:
        st.session_state["vss_benchmark_contract"] = "Ticker Benchmark"
    if "vss_promotion_min_benchmark_coverage" not in st.session_state:
        st.session_state["vss_promotion_min_benchmark_coverage"] = STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE * 100.0
    if "vss_promotion_min_net_cagr_spread" not in st.session_state:
        st.session_state["vss_promotion_min_net_cagr_spread"] = STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD * 100.0
    if "vss_promotion_min_liquidity_clean_coverage" not in st.session_state:
        st.session_state["vss_promotion_min_liquidity_clean_coverage"] = (
            STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE * 100.0
        )
    if "vss_promotion_max_underperformance_share" not in st.session_state:
        st.session_state["vss_promotion_max_underperformance_share"] = (
            STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE * 100.0
        )
    if "vss_promotion_min_worst_rolling_excess_return" not in st.session_state:
        st.session_state["vss_promotion_min_worst_rolling_excess_return"] = (
            STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN * 100.0
        )
    if "vss_promotion_max_strategy_drawdown" not in st.session_state:
        st.session_state["vss_promotion_max_strategy_drawdown"] = (
            STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN * 100.0
        )
    if "vss_promotion_max_drawdown_gap_vs_benchmark" not in st.session_state:
        st.session_state["vss_promotion_max_drawdown_gap_vs_benchmark"] = (
            STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK * 100.0
        )
    if "qvss_trend_filter_enabled" not in st.session_state:
        st.session_state["qvss_trend_filter_enabled"] = STRICT_TREND_FILTER_DEFAULT_ENABLED
    if "qvss_trend_filter_window" not in st.session_state:
        st.session_state["qvss_trend_filter_window"] = STRICT_TREND_FILTER_DEFAULT_WINDOW
    if "qvss_weighting_mode" not in st.session_state:
        st.session_state["qvss_weighting_mode"] = _strict_weighting_mode_value_to_label(STRICT_DEFAULT_WEIGHTING_MODE)
    if "qvss_rejected_slot_handling_mode" not in st.session_state:
        st.session_state["qvss_rejected_slot_handling_mode"] = _strict_rejection_handling_mode_value_to_label(
            STRICT_DEFAULT_REJECTION_HANDLING_MODE
        )
    if "qvss_rejected_slot_fill_enabled" not in st.session_state:
        st.session_state["qvss_rejected_slot_fill_enabled"] = STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED
    if "qvss_partial_cash_retention_enabled" not in st.session_state:
        st.session_state["qvss_partial_cash_retention_enabled"] = STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED
    if "qvss_risk_off_mode" not in st.session_state:
        st.session_state["qvss_risk_off_mode"] = _strict_risk_off_mode_value_to_label(STRICT_DEFAULT_RISK_OFF_MODE)
    if "qvss_defensive_tickers" not in st.session_state:
        st.session_state["qvss_defensive_tickers"] = ",".join(STRICT_DEFAULT_DEFENSIVE_TICKERS)
    if "qvss_market_regime_enabled" not in st.session_state:
        st.session_state["qvss_market_regime_enabled"] = STRICT_MARKET_REGIME_DEFAULT_ENABLED
    if "qvss_market_regime_window" not in st.session_state:
        st.session_state["qvss_market_regime_window"] = STRICT_MARKET_REGIME_DEFAULT_WINDOW
    if "qvss_market_regime_benchmark" not in st.session_state:
        st.session_state["qvss_market_regime_benchmark"] = STRICT_MARKET_REGIME_DEFAULT_BENCHMARK
    if "qvss_underperformance_guardrail_enabled" not in st.session_state:
        st.session_state["qvss_underperformance_guardrail_enabled"] = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED
    if "qvss_underperformance_guardrail_window_months" not in st.session_state:
        st.session_state["qvss_underperformance_guardrail_window_months"] = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS
    if "qvss_underperformance_guardrail_threshold" not in st.session_state:
        st.session_state["qvss_underperformance_guardrail_threshold"] = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD * 100.0
    if "qvss_drawdown_guardrail_enabled" not in st.session_state:
        st.session_state["qvss_drawdown_guardrail_enabled"] = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED
    if "qvss_drawdown_guardrail_window_months" not in st.session_state:
        st.session_state["qvss_drawdown_guardrail_window_months"] = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS
    if "qvss_drawdown_guardrail_strategy_threshold" not in st.session_state:
        st.session_state["qvss_drawdown_guardrail_strategy_threshold"] = (
            STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD * 100.0
        )
    if "qvss_drawdown_guardrail_gap_threshold" not in st.session_state:
        st.session_state["qvss_drawdown_guardrail_gap_threshold"] = (
            STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD * 100.0
        )
    if "qvss_min_history_months_filter" not in st.session_state:
        st.session_state["qvss_min_history_months_filter"] = STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS
    if "qvss_min_avg_dollar_volume_20d_m_filter" not in st.session_state:
        st.session_state["qvss_min_avg_dollar_volume_20d_m_filter"] = STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M
    if "qvss_benchmark_contract" not in st.session_state:
        st.session_state["qvss_benchmark_contract"] = "Ticker Benchmark"
    if "qvss_promotion_min_benchmark_coverage" not in st.session_state:
        st.session_state["qvss_promotion_min_benchmark_coverage"] = STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE * 100.0
    if "qvss_promotion_min_net_cagr_spread" not in st.session_state:
        st.session_state["qvss_promotion_min_net_cagr_spread"] = STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD * 100.0
    if "qvss_promotion_min_liquidity_clean_coverage" not in st.session_state:
        st.session_state["qvss_promotion_min_liquidity_clean_coverage"] = (
            STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE * 100.0
        )
    if "qvss_promotion_max_underperformance_share" not in st.session_state:
        st.session_state["qvss_promotion_max_underperformance_share"] = (
            STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE * 100.0
        )
    if "qvss_promotion_min_worst_rolling_excess_return" not in st.session_state:
        st.session_state["qvss_promotion_min_worst_rolling_excess_return"] = (
            STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN * 100.0
        )
    if "qvss_promotion_max_strategy_drawdown" not in st.session_state:
        st.session_state["qvss_promotion_max_strategy_drawdown"] = (
            STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN * 100.0
        )
    if "qvss_promotion_max_drawdown_gap_vs_benchmark" not in st.session_state:
        st.session_state["qvss_promotion_max_drawdown_gap_vs_benchmark"] = (
            STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK * 100.0
        )
    if "qsqp_trend_filter_enabled" not in st.session_state:
        st.session_state["qsqp_trend_filter_enabled"] = STRICT_TREND_FILTER_DEFAULT_ENABLED
    if "qsqp_trend_filter_window" not in st.session_state:
        st.session_state["qsqp_trend_filter_window"] = STRICT_TREND_FILTER_DEFAULT_WINDOW
    if "qsqp_market_regime_enabled" not in st.session_state:
        st.session_state["qsqp_market_regime_enabled"] = STRICT_MARKET_REGIME_DEFAULT_ENABLED
    if "qsqp_market_regime_window" not in st.session_state:
        st.session_state["qsqp_market_regime_window"] = STRICT_MARKET_REGIME_DEFAULT_WINDOW
    if "qsqp_market_regime_benchmark" not in st.session_state:
        st.session_state["qsqp_market_regime_benchmark"] = STRICT_MARKET_REGIME_DEFAULT_BENCHMARK
    if "vsqp_trend_filter_enabled" not in st.session_state:
        st.session_state["vsqp_trend_filter_enabled"] = STRICT_TREND_FILTER_DEFAULT_ENABLED
    if "vsqp_trend_filter_window" not in st.session_state:
        st.session_state["vsqp_trend_filter_window"] = STRICT_TREND_FILTER_DEFAULT_WINDOW
    if "vsqp_market_regime_enabled" not in st.session_state:
        st.session_state["vsqp_market_regime_enabled"] = STRICT_MARKET_REGIME_DEFAULT_ENABLED
    if "vsqp_market_regime_window" not in st.session_state:
        st.session_state["vsqp_market_regime_window"] = STRICT_MARKET_REGIME_DEFAULT_WINDOW
    if "vsqp_market_regime_benchmark" not in st.session_state:
        st.session_state["vsqp_market_regime_benchmark"] = STRICT_MARKET_REGIME_DEFAULT_BENCHMARK
    if "qvqp_trend_filter_enabled" not in st.session_state:
        st.session_state["qvqp_trend_filter_enabled"] = STRICT_TREND_FILTER_DEFAULT_ENABLED
    if "qvqp_trend_filter_window" not in st.session_state:
        st.session_state["qvqp_trend_filter_window"] = STRICT_TREND_FILTER_DEFAULT_WINDOW
    if "qvqp_market_regime_enabled" not in st.session_state:
        st.session_state["qvqp_market_regime_enabled"] = STRICT_MARKET_REGIME_DEFAULT_ENABLED
    if "qvqp_market_regime_window" not in st.session_state:
        st.session_state["qvqp_market_regime_window"] = STRICT_MARKET_REGIME_DEFAULT_WINDOW
    if "qvqp_market_regime_benchmark" not in st.session_state:
        st.session_state["qvqp_market_regime_benchmark"] = STRICT_MARKET_REGIME_DEFAULT_BENCHMARK

    # Migrate old strict-annual default factor selections from prior sessions.
    if st.session_state.get("qss_quality_factors") == QUALITY_STRICT_LEGACY_DEFAULT_FACTORS:
        st.session_state["qss_quality_factors"] = QUALITY_STRICT_DEFAULT_FACTORS.copy()
    if st.session_state.get("compare_qss_factors") == QUALITY_STRICT_LEGACY_DEFAULT_FACTORS:
        st.session_state["compare_qss_factors"] = QUALITY_STRICT_DEFAULT_FACTORS.copy()
    if st.session_state.get("vss_value_factors") == VALUE_STRICT_LEGACY_DEFAULT_FACTORS:
        st.session_state["vss_value_factors"] = VALUE_STRICT_DEFAULT_FACTORS.copy()
    if st.session_state.get("qvss_value_factors") == VALUE_STRICT_LEGACY_DEFAULT_FACTORS:
        st.session_state["qvss_value_factors"] = VALUE_STRICT_DEFAULT_FACTORS.copy()
    if st.session_state.get("compare_vss_factors") == VALUE_STRICT_LEGACY_DEFAULT_FACTORS:
        st.session_state["compare_vss_factors"] = VALUE_STRICT_DEFAULT_FACTORS.copy()
    if st.session_state.get("compare_qvss_value_factors") == VALUE_STRICT_LEGACY_DEFAULT_FACTORS:
        st.session_state["compare_qvss_value_factors"] = VALUE_STRICT_DEFAULT_FACTORS.copy()


def _request_backtest_panel(panel: str) -> None:
    if panel not in _valid_backtest_route_targets():
        return
    st.session_state.backtest_requested_panel = panel


# Sync the visual workflow selector to the active Backtest panel.
def _activate_backtest_workflow_panel() -> None:
    selected_panel = st.session_state.get("backtest_workflow_active_panel")
    if selected_panel in set(BACKTEST_WORKFLOW_PANEL_OPTIONS):
        st.session_state.backtest_active_stage = selected_panel
        st.session_state.backtest_active_panel = selected_panel


def _parse_manual_tickers(text: str) -> list[str]:
    seen: set[str] = set()
    tickers: list[str] = []

    for raw in text.split(","):
        symbol = raw.strip().upper()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        tickers.append(symbol)

    return tickers


def _format_currency(value: float) -> str:
    return f"${value:,.1f}"


def _format_percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def _format_ratio(value: float) -> str:
    return f"{value:.3f}"


def _render_ticker_preview(tickers: list[str], *, preview_count: int = 12, tail_count: int = 5) -> None:
    if not tickers:
        st.caption("Selected tickers: `0`")
        return

    if len(tickers) <= preview_count:
        preview = ", ".join(tickers)
        st.caption(f"Selected tickers ({len(tickers)}): `{preview}`")
        return

    head = ", ".join(tickers[:preview_count])
    tail = ", ".join(tickers[-tail_count:]) if tail_count > 0 else ""
    remaining = len(tickers) - preview_count - min(tail_count, len(tickers) - preview_count)

    preview = f"Head: {head}"
    if remaining > 0:
        preview += f" ... (+{remaining} more) "
    if tail:
        preview += f"| Tail: {tail}"

    st.caption(f"Selected tickers ({len(tickers)}): `{preview}`")


def _render_equal_weight_universe_inputs(
    *,
    key_prefix: str,
    radio_label: str = "Universe Mode",
    preset_label: str = "Preset",
    ticker_label: str = "Tickers",
) -> tuple[str, str | None, list[str]]:
    universe_mode_label = st.radio(
        radio_label,
        options=["Preset", "Manual"],
        horizontal=True,
        help="Preset은 빠른 실행용, Manual은 직접 종목을 입력하는 방식입니다.",
        key=f"{key_prefix}_universe_mode",
    )

    preset_name: str | None = None
    tickers: list[str] = []

    if universe_mode_label == "Preset":
        preset_name = st.selectbox(
            preset_label,
            options=list(EQUAL_WEIGHT_PRESETS.keys()),
            index=0,
            key=f"{key_prefix}_preset",
        )
        tickers = list(EQUAL_WEIGHT_PRESETS[preset_name])
    else:
        manual_tickers = st.text_input(
            ticker_label,
            value="VIG,SCHD,DGRO,GLD",
            help="Comma-separated tickers. Example: VIG,SCHD,DGRO,GLD",
            key=f"{key_prefix}_manual_tickers",
        )
        tickers = _parse_manual_tickers(manual_tickers)

    _render_ticker_preview(tickers)
    return ("preset" if universe_mode_label == "Preset" else "manual_tickers"), preset_name, tickers


def _render_gtaa_preset_note(preset_name: str | None) -> None:
    if preset_name == "GTAA Universe":
        st.caption("Current default preset: uses `PDBC` as the commodity sleeve.")
    elif preset_name == "GTAA Universe (No Commodity + QUAL + USMV)":
        st.caption("Top candidate preset: removes the commodity sleeve and adds `QUAL`, `USMV`.")
    elif preset_name == "GTAA Universe (QQQ + XLE + IAU + TIP)":
        st.caption("Top candidate preset: adds `QQQ`, `XLE`, `IAU`, `TIP` on top of the current GTAA core.")
    elif preset_name == "GTAA Universe (QQQ + QUAL + USMV + XLE + IAU)":
        st.caption("Top candidate preset: current strongest Phase 12 GTAA candidate with growth, quality, low-vol, gold, and energy broadeners.")
    elif preset_name == "GTAA Universe (U3 Commodity Candidate Base)":
        st.caption("Verified Phase 12 candidate base: commodity/inflation-heavy mix. Best validated contract so far was `month_end`, `top=2`, `interval=3`, `Score Horizons=1/3/6`.")
    elif preset_name == "GTAA Universe (U1 Offensive Candidate Base)":
        st.caption("Verified Phase 12 candidate base: growth + quality + style diversification mix. Best validated contract so far was `month_end`, `top=2`, `interval=3`, `Score Horizons=1/3/6/12`.")
    elif preset_name == "GTAA Universe (U5 Smallcap Value Candidate Base)":
        st.caption("Verified Phase 12 candidate base: smallcap/value-aware defensive mix. Best validated contract so far was `month_end`, `top=3`, `interval=3`, `Score Horizons=1/3/6/12`.")


def _render_gtaa_universe_inputs(
    *,
    key_prefix: str,
    radio_label: str = "Universe Mode",
    preset_label: str = "Preset",
    ticker_label: str = "Tickers",
) -> tuple[str, str | None, list[str]]:
    universe_mode_label = st.radio(
        radio_label,
        options=["Preset", "Manual"],
        horizontal=True,
        help="GTAA는 기본적으로 preset universe 사용을 권장합니다.",
        key=f"{key_prefix}_universe_mode",
    )

    preset_name: str | None = None
    tickers: list[str] = []

    if universe_mode_label == "Preset":
        preset_name = st.selectbox(
            preset_label,
            options=list(GTAA_PRESETS.keys()),
            index=0,
            key=f"{key_prefix}_preset",
        )
        tickers = list(GTAA_PRESETS[preset_name])
        _render_gtaa_preset_note(preset_name)
    else:
        manual_tickers = st.text_input(
            ticker_label,
            value="SPY,IWD,IWM,IWN,MTUM,EFA,TLT,IEF,LQD,PDBC,VNQ,GLD",
            help="Comma-separated tickers. Example: SPY,IWD,IWM,IWN,MTUM,EFA,TLT,IEF,LQD,PDBC,VNQ,GLD",
            key=f"{key_prefix}_manual_tickers",
        )
        tickers = _parse_manual_tickers(manual_tickers)

    _render_ticker_preview(tickers)
    return ("preset" if universe_mode_label == "Preset" else "manual_tickers"), preset_name, tickers


def _render_global_relative_strength_preset_note(preset_name: str | None) -> None:
    if preset_name == "Global Relative Strength Core ETF Universe":
        st.caption(
            "Phase 24 default universe: global equity, commodity, credit, treasury, and inflation ETF sleeves."
        )
    elif preset_name == "Global Relative Strength Compact Smoke Universe":
        st.caption("Small smoke-test universe for quick UI/runtime validation.")


def _render_global_relative_strength_universe_inputs(
    *,
    key_prefix: str,
    radio_label: str = "Universe Mode",
    preset_label: str = "Preset",
    ticker_label: str = "Tickers",
) -> tuple[str, str | None, list[str]]:
    universe_mode_label = st.radio(
        radio_label,
        options=["Preset", "Manual"],
        horizontal=True,
        help="Global Relative Strength는 Phase 24 기본 ETF preset으로 시작하고, 필요하면 직접 ticker를 넣어 검증합니다.",
        key=f"{key_prefix}_universe_mode",
    )

    preset_name: str | None = None
    tickers: list[str] = []

    if universe_mode_label == "Preset":
        preset_name = st.selectbox(
            preset_label,
            options=list(GLOBAL_RELATIVE_STRENGTH_PRESETS.keys()),
            index=0,
            key=f"{key_prefix}_preset",
        )
        tickers = list(GLOBAL_RELATIVE_STRENGTH_PRESETS[preset_name])
        _render_global_relative_strength_preset_note(preset_name)
    else:
        manual_tickers = st.text_input(
            ticker_label,
            value=",".join(GLOBAL_RELATIVE_STRENGTH_DEFAULT_TICKERS),
            help="Comma-separated tickers. Example: SPY,EFA,EEM,IWM,VNQ,GLD,DBC,LQD,HYG,IEF,TLT,TIP",
            key=f"{key_prefix}_manual_tickers",
        )
        tickers = _parse_manual_tickers(manual_tickers)

    _render_ticker_preview(tickers)
    return ("preset" if universe_mode_label == "Preset" else "manual_tickers"), preset_name, tickers


def _render_strict_preset_status_note(preset_name: str | None) -> None:
    if preset_name == "US Statement Coverage 300":
        st.info(
            "This is the current strict annual public default. It has the best balance today between "
            "coverage depth, runtime, and operator stability."
        )
    elif preset_name == "US Statement Coverage 100":
        st.caption("This lighter preset is mainly intended for compare mode and faster strict annual smoke runs.")
    elif preset_name in {"US Statement Coverage 500", "US Statement Coverage 1000"}:
        st.warning(
            "This wider preset is currently a staged operator preset. It is useful for coverage expansion work, "
            "but it is not the official strict annual public default yet."
        )
    elif preset_name == "Big Tech Strict Trial":
        st.caption("This preset is still useful for strict annual smoke checks and fast architecture validation.")


def _render_historical_universe_help_popover() -> None:
    _render_inline_help_popover(
        "히스토리컬 백테스트 모집군",
        "Preset 종목군은 실행 전체 기간 동안 고정됩니다. 종료일 기준으로 stale 종목을 다른 종목으로 교체하지 않습니다. 대신 각 리밸런싱 날짜마다 그 날짜에 가격과 팩터 데이터를 사용할 수 있는 종목만 후보로 평가합니다.",
    )


def _render_historical_universe_caption() -> None:
    st.caption(
        "히스토리컬 모드: preset 종목군은 실행 동안 고정됩니다. "
        "각 리밸런싱 날짜마다 가격과 팩터 데이터를 사용할 수 있는 종목만 후보가 됩니다."
    )


def _resolve_strict_dynamic_universe_inputs(
    *,
    tickers: list[str],
    preset_name: str | None,
    universe_contract: str,
    statement_freq: str = "annual",
) -> tuple[list[str], int | None]:
    if universe_contract != HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        return [], None

    target_size = STRICT_ANNUAL_MANAGED_PRESET_SPECS.get(preset_name or "", len(tickers))
    candidate_tickers = tickers

    return candidate_tickers, int(target_size)


def _render_strict_dynamic_universe_contract_note(
    *,
    universe_contract: str,
    tickers: list[str],
    preset_name: str | None,
    statement_freq: str = "annual",
) -> tuple[list[str], int | None]:
    dynamic_candidate_tickers, dynamic_target_size = _resolve_strict_dynamic_universe_inputs(
        tickers=tickers,
        preset_name=preset_name,
        universe_contract=universe_contract,
        statement_freq=statement_freq,
    )

    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        freq_label = str(statement_freq).strip().lower()
        st.info(
            "Phase 10 first pass dynamic PIT mode입니다. 현재 선택한 candidate pool 안에서 "
            f"각 리밸런싱 날짜 기준 `price * latest-known {freq_label} shares_outstanding`로 top-N 모집군을 다시 구성합니다."
        )
        st.caption(
            f"Dynamic candidate pool: `{len(dynamic_candidate_tickers)}` symbols | "
            f"target membership: `{dynamic_target_size}` | "
            f"현재는 `{freq_label}` strict family first pass이며, 선택한 preset/manual candidate pool을 기준으로 membership를 다시 계산합니다."
        )

    return dynamic_candidate_tickers, dynamic_target_size


def _render_strict_annual_universe_contract_note(
    *,
    universe_contract: str,
    tickers: list[str],
    preset_name: str | None,
) -> tuple[list[str], int | None]:
    return _render_strict_dynamic_universe_contract_note(
        universe_contract=universe_contract,
        tickers=tickers,
        preset_name=preset_name,
        statement_freq="annual",
    )


def _render_quality_family_guide(current_strategy: str) -> None:
    guide_df = pd.DataFrame(
        [
            {
                "Strategy": "Quality Snapshot",
                "Data Source": "nyse_factors",
                "Timing": "broad_research",
                "History / Coverage": "summary/factor history depends on weekly refresh depth",
                "Speed": "Fastest",
                "Best For": "research-oriented trial / quick UI runs",
            },
            {
                "Strategy": "Quality Snapshot (Strict Annual)",
                "Data Source": "nyse_factors_statement",
                "Timing": "strict_statement_annual",
                "History / Coverage": "annual statement shadow factors, wider US stock coverage",
                "Speed": "Medium",
                "Best For": "long-history strict annual quality backtests",
            },
            {
                "Strategy": "Value Snapshot (Strict Annual)",
                "Data Source": "nyse_factors_statement",
                "Timing": "strict_statement_annual",
                "History / Coverage": "annual statement shadow factors, valuation coverage can start later",
                "Speed": "Medium",
                "Best For": "strict annual value family validation",
            },
            {
                "Strategy": "Quality + Value Snapshot (Strict Annual)",
                "Data Source": "nyse_factors_statement",
                "Timing": "strict_statement_annual",
                "History / Coverage": "annual statement shadow factors, combined quality/value availability",
                "Speed": "Medium",
                "Best For": "strict annual multi-factor validation",
            },
        ]
    )

    with st.expander("Broad vs Strict Guide", expanded=False):
        st.dataframe(guide_df, width="stretch", hide_index=True)
        if current_strategy == "quality_broad":
            st.info(
                "Use `Quality Snapshot` when we want the quickest research-oriented run. "
                "It is easier to refresh, but history depth depends on broad fundamentals/factors coverage."
            )
        elif current_strategy == "quality_strict":
            st.info(
                "Use `Quality Snapshot (Strict Annual)` when we want the stricter annual statement path. "
                "It is slower than broad quality, but it now supports wider US stock universes with long history. "
                "Today the public default stays on `US Statement Coverage 300`; wider presets remain staged operator options."
            )
        elif current_strategy == "value_strict":
            st.info(
                "Use `Value Snapshot (Strict Annual)` when we want the strict annual valuation family. "
                "It shares the same annual statement shadow source, but usable history can begin later than quality. "
                "It currently follows the same managed-universe ladder, with `300` as the main public default."
            )
        elif current_strategy == "quality_value_strict":
            st.info(
                "Use `Quality + Value Snapshot (Strict Annual)` when we want a blended strict annual family. "
                "It keeps the same annual statement shadow source, but combines coverage-first quality inputs with valuation discipline. "
                "This is the first strict multi-factor public candidate, built on the same `300` default universe."
            )



def _render_summary_metrics(summary_df) -> None:
    row = summary_df.iloc[0]

    metric_cols = st.columns(4)
    metric_cols[0].metric("End Balance", _format_currency(float(row["End Balance"])))
    metric_cols[1].metric("CAGR", _format_percent(float(row["CAGR"])))
    metric_cols[2].metric("Sharpe Ratio", _format_ratio(float(row["Sharpe Ratio"])))
    metric_cols[3].metric("Maximum Drawdown", _format_percent(float(row["Maximum Drawdown"])))


def _render_inline_help_popover(title: str, body: str) -> None:
    with st.popover("?", help=title, use_container_width=False):
        st.markdown(f"**{title}**")
        st.caption(body)


def _render_inline_help_markdown_popover(title: str, body: str) -> None:
    with st.popover("?", help=title, use_container_width=False):
        st.markdown(f"**{title}**")
        st.markdown(body)


def _render_trend_filter_help_popover() -> None:
    _render_inline_help_popover(
        "추세 필터 오버레이",
        "월말 리밸런싱 시점에만 확인하는 1차 버전입니다. 예를 들어 랭킹으로 A와 B가 뽑혔는데, 리밸런싱 당일 A는 200일 이동평균선 아래이고 B는 위에 있으면 A는 제외됩니다. strict annual form에서는 `Rejected Slot Handling Contract`로 그 빈 자리를 다음 순위 종목으로 보충할지, 현금으로 남길지, 아니면 최종 생존 종목들에 다시 재배분할지를 한 번에 고릅니다. 일별로 중간 점검하는 구조는 아닙니다.",
    )


def _render_rejected_slot_handling_help_popover() -> None:
    _render_inline_help_markdown_popover(
        "Rejected Slot Handling Contract",
        """
이 계약은 **Trend Filter 때문에 raw top-N 일부가 탈락했을 때** 빈 슬롯을 어떻게 처리할지 정합니다.

쉽게 말하면:
- `Top 10` 중 `2개`만 trend filter에 걸려 빠졌을 때
- 그 비어 있는 `2자리`를 어떻게 처리할지 정하는 규칙입니다.

- `Reweight Survivors`
  - 남은 생존 종목들끼리 다시 100% 재배분합니다.

- `Retain Unfilled Slots As Cash`
  - 비어 있는 슬롯 비중만큼 현금으로 남깁니다.

- `Fill Then Reweight Survivors`
  - 먼저 다음 순위의 추세 통과 종목으로 채웁니다.
  - 그래도 빈 슬롯이 남으면 생존 종목들끼리 다시 재배분합니다.

- `Fill Then Retain Unfilled Slots As Cash`
  - 먼저 다음 순위의 추세 통과 종목으로 채웁니다.
  - 그래도 빈 슬롯이 남으면 그 비중은 현금으로 남깁니다.

이 계약은 **일부 종목만 빠졌을 때** 쓰는 규칙입니다.
`Market Regime`이나 guardrail 때문에 **원래 factor 포트폴리오 전체를 멈추고 현금 또는 방어 ETF로 전체 전환하는 상황**은 아래 `Risk-Off Contract`가 담당합니다.
        """.strip(),
    )


def _render_market_regime_help_popover() -> None:
    _render_inline_help_popover(
        "마켓 레짐 오버레이",
        "개별 종목이 아니라 시장 전체 상태를 먼저 보는 상위 오버레이입니다. 1차 버전에서는 월말 리밸런싱 시점에만 지정한 벤치마크(예: SPY)의 종가가 이동평균선 아래인지 확인합니다. Window 200은 보통 200거래일 이동평균선, 즉 장기 추세선을 뜻합니다. 벤치마크가 해당 이동평균선 아래면 그 달 strict factor 포트폴리오는 전부 현금으로 두고, 위에 있으면 기존 팩터 선택 결과를 그대로 집행합니다.",
    )


def _render_interpretation_summary_help_popover() -> None:
    _render_inline_help_popover(
        "해석 요약",
        "Raw Candidate Events는 각 리밸런싱에서 팩터 랭킹으로 최종 후보(top N)까지 올라온 종목 수의 총합입니다. Final Selected Events는 오버레이까지 반영한 뒤 실제 보유 후보로 남은 종목 수의 총합입니다. 이 값들은 전체 모집군 크기를 뜻하지 않습니다. 오버레이가 꺼져 있으면 보통 Raw와 Final이 같고, 오버레이가 켜져 있으면 Raw와 Final의 차이만큼 추가 필터가 개입한 것으로 해석하면 됩니다. `Rejected Slot Handling`은 trend rejection 이후 빈 슬롯을 어떻게 처리하도록 계약했는지의 현재 실행 언어입니다. `Weighting Contract`는 최종 선택 종목에 어떤 비중 규칙을 썼는지, `Risk-Off Contract`는 포트폴리오 전체를 쉬어야 할 때 현금으로 갈지 방어 sleeve로 갈지를 뜻합니다. Filled Events는 제외된 자리 일부를 다음 순위 종목으로 보충한 횟수, Cash-Retained Events는 부분 rejection 이후 빈 슬롯 일부를 현금으로 남긴 횟수입니다. Defensive Sleeve Activations는 포트폴리오 전체를 방어 ETF sleeve로 전환한 횟수입니다. Regime Blocked Events / Regime Cash Rebalances는 시장 상태 오버레이 때문에 factor 포트폴리오 전체가 멈춘 흔적을 요약합니다.",
    )


def _render_overlay_rejection_frequency_help_popover() -> None:
    _render_inline_help_popover(
        "오버레이 제외 빈도",
        "각 종목이 추세 필터 때문에 실제 보유에서 몇 번 제외되었는지 보여줍니다. RejectedEvents는 제외된 횟수, FirstRejected와 LastRejected는 처음/마지막으로 제외된 날짜입니다. 이 표는 오버레이가 특정 종목에 얼마나 자주 개입했는지 보는 용도입니다.",
    )


def _render_market_regime_events_help_popover() -> None:
    _render_inline_help_popover(
        "마켓 레짐 이벤트",
        "이 표는 벤치마크가 risk-off 상태로 판단되어 포트폴리오 전체가 현금으로 이동한 리밸런싱만 모아 보여줍니다. 즉 특정 종목이 잘린 기록이 아니라, 시장 상태 때문에 strict factor 포트폴리오 전체 노출이 차단된 날짜를 읽는 용도입니다.",
    )


def _render_cash_share_help_popover() -> None:
    _render_inline_help_popover(
        "현금 비중",
        "Cash Share는 해당 리밸런싱 직후 포트폴리오에서 현금으로 남아 있는 비중입니다. 오버레이로 일부 종목이 제외되거나, 투자 가능한 종목 수가 목표 Top N보다 적을 때 현금 비중이 생길 수 있습니다. 오버레이가 꺼져 있고 투자 가능한 종목 수가 충분하면 보통 0%에 가깝습니다.",
    )


def _render_strict_risk_off_contract_help_popover() -> None:
    _render_inline_help_markdown_popover(
        "Risk-Off Contract",
        """
이 계약은 **포트폴리오 전체를 쉬어야 할 때** 무엇을 할지 정합니다.

쉽게 말하면:
- 일부 종목 몇 개만 빠진 상황이 아니라
- 이번 리밸런싱에서 **원래 factor 포트폴리오 전체를 멈추고 현금 또는 방어 ETF 쪽으로 옮길지** 정하는 규칙입니다.

`포트폴리오 전체를 쉰다`는 뜻은:
- 개별 종목 몇 개만 빠지는 것이 아니라
- `Market Regime` 또는 guardrail 때문에
- 그 시점의 factor 포트폴리오 전체를 그대로 쓰지 않고
- 현금 또는 방어 ETF 쪽으로 전체 전환하는 상황을 뜻합니다.

옵션 설명:

- `Cash Only`
  - 포트폴리오 전체를 쉬어야 하면 100% 현금으로 둡니다.

- `Defensive Sleeve Preference`
  - 포트폴리오 전체를 쉬어야 하면 `Defensive Sleeve Tickers`에 적은 방어 ETF 묶음으로 이동합니다.

즉 이것은 **포트폴리오 전체 전환 계약**이고,
`Trend Filter` 때문에 일부 종목만 빠졌을 때 쓰는 `Rejected Slot Handling Contract`와는 다른 역할입니다.
        """.strip(),
    )


def _render_strict_weighting_contract_help_popover() -> None:
    _render_inline_help_markdown_popover(
        "Weighting Contract",
        """
이 계약은 **최종 선택된 종목들 사이에 비중을 어떻게 나눌지** 정합니다.

- `Equal Weight`
  - 모든 선택 종목을 동일 비중으로 담습니다.

- `Rank-Tapered`
  - 상위 rank 종목에 조금 더 높은 비중을 주되, 과도한 집중은 피합니다.

토글형 기능이라기보다,
백테스트를 돌릴 때 항상 함께 저장되는 **기본 비중 규칙**이라고 보면 됩니다.
        """.strip(),
    )


def _render_strict_overlay_section_intro() -> None:
    st.caption(
        "이 영역은 overlay 자체를 켜고 해석하는 곳입니다. "
        "`Trend Filter`는 개별 종목 일부를 제외할 수 있고, "
        "`Market Regime`은 필요하면 factor 포트폴리오 전체를 멈추고 현금 또는 방어 ETF 쪽으로 전환할 수 있습니다."
    )


def _render_strict_portfolio_handling_contracts_intro() -> None:
    st.caption(
        "이 영역은 overlay 결과를 실제 포트폴리오에서 어떻게 처리할지 정하는 곳입니다."
    )
    st.markdown(
        "- `Rejected Slot Handling Contract`: Trend Filter로 일부 종목만 빠졌을 때 빈 슬롯을 어떻게 처리할지 정합니다.\n"
        "- `Risk-Off Contract`: `Market Regime`이나 guardrail 때문에 factor 포트폴리오 전체를 현금 또는 방어 ETF 쪽으로 전환해야 할 때 무엇을 할지 정합니다.\n"
        "- `Weighting Contract`: 최종적으로 보유하게 된 종목 사이에 비중을 어떻게 나눌지 정합니다."
    )
    st.caption(
        "참고로 이 세 contract는 토글형 on/off 기능이 아니라, "
        "백테스트를 돌릴 때 항상 저장되는 기본 처리 규칙입니다. "
        "다만 관련 상황이 실제로 발생할 때만 결과에 눈에 띄는 영향을 줍니다."
    )


def _render_strict_quarterly_productionization_note(*, family_label: str) -> None:
    st.info(
        f"Phase 23 기준으로 `{family_label}`는 실행 / compare / history 재현성을 제품 기능 수준으로 끌어올리는 중입니다. "
        "아직 투자 후보 승격이나 real-money promotion 단계는 아니며, 이번 화면에서는 quarterly cadence와 portfolio handling contract가 "
        "같은 payload로 저장되고 재실행되는지를 먼저 확인합니다."
    )


def _render_statement_shadow_coverage_help_popover() -> None:
    _render_inline_help_popover(
        "Statement Shadow Coverage Preview",
        "이 preview는 가격 데이터가 아니라 quarterly/annual statement shadow coverage를 확인하는 용도입니다. "
        "`Covered`는 현재 DB의 `nyse_fundamentals_statement`에서 usable shadow rows가 있는 심볼 수를 뜻합니다. "
        "`Requested`보다 작으면 일부 심볼은 factor 계산용 statement shadow가 아직 없다는 뜻이며, "
        "아래 drilldown에서 어떤 심볼이 빠졌는지와 raw statement가 아예 없는지까지 확인할 수 있습니다.",
    )


def _render_statement_shadow_coverage_preview(
    *,
    tickers: list[str],
    freq: str,
    strategy_label: str,
) -> None:
    if not tickers:
        return

    summary = _load_statement_shadow_coverage_preview(tuple(tickers), freq)
    title_col, help_col = st.columns([0.92, 0.08], gap="small")
    with title_col:
        st.markdown("#### Statement Shadow Coverage Preview")
    with help_col:
        _render_statement_shadow_coverage_help_popover()
    st.caption(f"Current `{freq}` statement-shadow coverage for `{strategy_label}` before execution.")

    metric_cols = st.columns(5)
    metric_cols[0].metric("Requested", summary.get("requested_count", 0))
    metric_cols[1].metric("Covered", summary.get("covered_count", 0))
    metric_cols[2].metric(
        "Earliest Period",
        (
            pd.to_datetime(summary.get("min_period_end")).strftime("%Y-%m-%d")
            if summary.get("min_period_end") is not None and pd.notna(summary.get("min_period_end"))
            else "-"
        ),
    )
    metric_cols[3].metric(
        "Latest Period",
        (
            pd.to_datetime(summary.get("max_period_end")).strftime("%Y-%m-%d")
            if summary.get("max_period_end") is not None and pd.notna(summary.get("max_period_end"))
            else "-"
        ),
    )
    metric_cols[4].metric("Median Rows / Symbol", summary.get("median_rows_per_symbol", 0))

    if summary.get("covered_count", 0) == 0:
        st.warning("No statement shadow rows are currently available for the selected symbols.")

    if summary.get("covered_count", 0) < summary.get("requested_count", 0):
        st.caption(
            "일부 심볼은 아직 statement shadow coverage가 없습니다. 이 경우 해당 심볼은 초기 리밸런싱 구간에서 자연스럽게 제외됩니다."
        )
    min_available_at = summary.get("min_available_at")
    if min_available_at is not None and pd.notna(min_available_at):
        st.caption(
            "이 preview는 raw statement ledger가 아니라 rebuilt statement shadow를 기준으로 합니다. "
            f"현재 earliest `latest_available_at`은 `{pd.to_datetime(min_available_at).strftime('%Y-%m-%d')}` 입니다."
        )

    missing_count = int(summary.get("missing_count", 0) or 0)
    if missing_count == 0:
        return

    bridge_notice = st.session_state.get("backtest_operator_bridge_notice")
    if bridge_notice:
        st.success(bridge_notice)
        st.session_state.backtest_operator_bridge_notice = None

    st.info(
        f"`Covered`에서 빠진 `{missing_count}`개 심볼을 아래에서 확인할 수 있습니다. "
        "이 표는 단순히 missing symbol 목록만 보여주는 것이 아니라, "
        "raw statement 자체가 없는지(`no_raw_statement_coverage`) 아니면 raw는 있는데 shadow만 비어 있는지까지 같이 구분합니다."
    )
    gap_cols = st.columns(3)
    gap_cols[0].metric("Missing", missing_count)
    gap_cols[1].metric("Need Raw Collection", int(summary.get("no_raw_missing_count", 0) or 0))
    gap_cols[2].metric("Raw Exists / Shadow Missing", int(summary.get("raw_present_missing_count", 0) or 0))

    with st.expander("Coverage Gap Drilldown", expanded=False):
        st.caption(
            "여기 표의 `Coverage Gap Status`는 coarse 분류입니다. "
            "`no_raw_statement_coverage`는 추가 statement 수집이 필요한 심볼이고, "
            "`raw_statement_present_but_shadow_missing`는 raw는 이미 있지만 shadow가 비어 있는 심볼입니다. "
            "세부 원인 분류(`source_empty_or_symbol_issue`, `foreign_or_nonstandard_form_structure`, "
            "`source_present_raw_missing` 등)는 `Statement Coverage Diagnosis` 카드에서 확인합니다. "
            "현재는 `Extended Statement Refresh`가 shadow rebuild까지 같이 수행하므로, 먼저 그 경로를 다시 실행해보고 "
            "그래도 남으면 coverage hardening을 점검하는 것이 좋습니다."
        )
        missing_symbols_csv = ",".join(summary.get("missing_symbols") or [])
        if missing_symbols_csv:
            if st.button(
                "Send Missing Symbols To Statement Coverage Diagnosis",
                key=f"shadow_gap_send_diagnosis_{strategy_label}_{freq}",
                use_container_width=True,
            ):
                _queue_ingestion_prefill(
                    target="statement_coverage_diagnosis",
                    symbols_csv=missing_symbols_csv,
                    freq=freq,
                    notice=(
                        "Loaded missing coverage symbols into `Statement Coverage Diagnosis`. "
                        "Open the `Ingestion` tab and run the prepared diagnosis card when you are ready."
                    ),
                )
                st.rerun()
        missing_df = pd.DataFrame(summary.get("missing_rows") or [])
        if not missing_df.empty:
            st.dataframe(missing_df, use_container_width=True, hide_index=True)

        refresh_payload = summary.get("refresh_payload")
        if refresh_payload:
            st.caption(
                "아래 payload는 `no_raw_statement_coverage`로 분류된 심볼만 대상으로 한 `Extended Statement Refresh` / "
                "`Financial Statement Ingestion` 입력 예시입니다."
            )
            st.code(refresh_payload["payload_block"], language="text")
            if st.button(
                "Send Raw-Coverage Gaps To Extended Statement Refresh",
                key=f"shadow_gap_send_refresh_{strategy_label}_{freq}",
                use_container_width=True,
            ):
                _queue_ingestion_prefill(
                    target="extended_statement_refresh",
                    symbols_csv=refresh_payload["symbols_csv"],
                    freq=freq,
                    notice=(
                        "Loaded raw-coverage gap symbols into `Extended Statement Refresh`. "
                        "Open the `Ingestion` tab and run the prepared card when you are ready."
                    ),
                )
                st.rerun()
        else:
            st.caption(
                "현재 missing symbol은 모두 raw statement coverage가 이미 있는 상태입니다. "
                "현행 `Extended Statement Refresh`는 shadow rebuild까지 같이 수행하므로, 먼저 그 경로를 다시 실행해보고 "
                "그래도 남으면 coverage hardening 점검이 더 우선입니다."
            )

        shadow_rebuild_payload = summary.get("shadow_rebuild_payload")
        if shadow_rebuild_payload:
            st.caption(
                "아래 payload는 `raw_statement_present_but_shadow_missing` 심볼만 대상으로 한 "
                "`Statement Shadow Rebuild Only` 입력 예시입니다."
            )
            st.code(shadow_rebuild_payload["payload_block"], language="text")
            if st.button(
                "Send Shadow-Missing Gaps To Statement Shadow Rebuild",
                key=f"shadow_gap_send_rebuild_{strategy_label}_{freq}",
                use_container_width=True,
            ):
                _queue_ingestion_prefill(
                    target="statement_shadow_rebuild",
                    symbols_csv=shadow_rebuild_payload["symbols_csv"],
                    freq=freq,
                    notice=(
                        "Loaded raw-present / shadow-missing symbols into `Statement Shadow Rebuild Only`. "
                        "Open the `Ingestion` tab and run the prepared card when you are ready."
                    ),
                )
                st.rerun()


def _build_daily_market_update_refresh_payload(details: dict[str, Any]) -> dict[str, str] | None:
    refresh_symbols = list(details.get("refresh_symbols_all") or [])
    target_end = details.get("target_end_date")
    common_latest = details.get("common_latest_date")

    if not refresh_symbols or not target_end or not common_latest:
        return None

    common_latest_ts = pd.to_datetime(common_latest, errors="coerce")
    if pd.isna(common_latest_ts):
        return None

    refresh_start = (common_latest_ts - pd.Timedelta(days=7)).strftime("%Y-%m-%d")
    symbols_csv = ",".join(refresh_symbols)
    return {
        "symbols_csv": symbols_csv,
        "start": refresh_start,
        "end": str(target_end),
        "payload_block": (
            f"symbols={symbols_csv}\n"
            f"start={refresh_start}\n"
            f"end={target_end}\n"
            "period=1mo\n"
            "interval=1d"
        ),
    }


def _render_market_regime_overlay_inputs(
    *,
    key_prefix: str,
    label_prefix: str,
) -> tuple[bool, int, str]:
    regime_title_col, regime_help_col = st.columns([0.92, 0.08], gap="small")
    with regime_title_col:
        st.markdown(f"##### {label_prefix}Market Regime Overlay")
    with regime_help_col:
        _render_market_regime_help_popover()

    regime_enabled = st.checkbox(
        "Enable",
        value=STRICT_MARKET_REGIME_DEFAULT_ENABLED,
        key=f"{key_prefix}_market_regime_enabled",
    )
    regime_window = int(
        st.number_input(
            f"{label_prefix}Market Regime Window",
            min_value=20,
            max_value=400,
            value=STRICT_MARKET_REGIME_DEFAULT_WINDOW,
            step=10,
            key=f"{key_prefix}_market_regime_window",
        )
    )
    regime_benchmark = st.selectbox(
        f"{label_prefix}Market Regime Benchmark",
        options=STRICT_MARKET_REGIME_BENCHMARK_OPTIONS,
        index=STRICT_MARKET_REGIME_BENCHMARK_OPTIONS.index(STRICT_MARKET_REGIME_DEFAULT_BENCHMARK),
        key=f"{key_prefix}_market_regime_benchmark",
        help="risk-on / risk-off를 판단할 벤치마크를 고릅니다.",
    )
    st.caption("Enable이 꺼져 있어도 Window와 Benchmark 값은 미리 조정할 수 있고, 오버레이를 켜면 그 값이 사용됩니다.")
    return regime_enabled, regime_window, regime_benchmark


def _render_advanced_group_caption(message: str) -> None:
    st.caption(message)


def _render_etf_real_money_inputs(
    *,
    key_prefix: str,
    default_min_price: float = ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
    default_transaction_cost_bps: float = ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
    default_benchmark: str = ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    default_min_etf_aum_b: float = ETF_OPERABILITY_DEFAULT_MIN_AUM_B,
    default_max_bid_ask_spread_pct: float = ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
) -> tuple[float, float, str, float, float]:
    st.markdown("##### Real-Money Contract")
    st.caption("설명은 `Reference > Guides > Real-Money Contract 값 해설` 또는 `Reference > Glossary`에서 다시 볼 수 있습니다.")
    st.caption(
        "실전형 first pass에서는 너무 낮은 가격 ETF를 걸러내는 `Minimum Price`, "
        "리밸런싱 turnover에 적용할 `Transaction Cost`, 비교 기준이 되는 `Benchmark Ticker`, "
        "ETF current-operability를 읽는 `Min ETF AUM`, `Max Bid-Ask Spread`를 같이 사용합니다."
    )
    left, center, right, far_left, far_right = st.columns(5, gap="small")
    with left:
        min_price_filter = float(
            st.number_input(
                "Minimum Price",
                min_value=0.0,
                max_value=1000.0,
                value=float(default_min_price),
                step=1.0,
                key=f"{key_prefix}_min_price_filter",
                help="이 값보다 싼 ETF는 해당 날짜 투자 후보에서 제외합니다.",
            )
        )
    with center:
        transaction_cost_bps = float(
            st.number_input(
                "Transaction Cost (bps)",
                min_value=0.0,
                max_value=500.0,
                value=float(default_transaction_cost_bps),
                step=1.0,
                key=f"{key_prefix}_transaction_cost_bps",
                help="리밸런싱 turnover 비율에 곱하는 왕복 비용 가정입니다. 10bps = 0.10%입니다.",
            )
        )
    with right:
        benchmark_ticker = str(
            st.text_input(
                "Benchmark Ticker",
                value=default_benchmark,
                key=f"{key_prefix}_benchmark_ticker",
                help="전략 결과를 비교할 기준 ETF ticker입니다. 기본값은 `SPY`입니다.",
            )
        ).strip().upper()
    with far_left:
        promotion_min_etf_aum_b = float(
            st.number_input(
                "Min ETF AUM ($B)",
                min_value=0.0,
                max_value=1000.0,
                value=float(default_min_etf_aum_b),
                step=0.5,
                key=f"{key_prefix}_promotion_min_etf_aum_b",
                help="현재 asset profile 기준 ETF 총자산이 이 값보다 작은 종목은 실전 운용 후보로 보수적으로 평가합니다.",
            )
        )
    with far_right:
        max_bid_ask_spread_percent = float(
            st.number_input(
                "Max Bid-Ask Spread (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(default_max_bid_ask_spread_pct) * 100.0,
                step=0.05,
                key=f"{key_prefix}_promotion_max_bid_ask_spread_pct",
                help="현재 bid/ask 기준 스프레드가 이 값보다 넓은 ETF는 실전 운용 후보로 보수적으로 평가합니다.",
            )
        )

    st.caption(
        "이 first pass는 `gross` 전략 곡선을 유지하면서, turnover 기반 예상 비용을 반영한 `net` 곡선, "
        "benchmark overlay, ETF current-operability(AUM / bid-ask spread) policy를 같이 보여줍니다."
    )
    return (
        min_price_filter,
        transaction_cost_bps,
        benchmark_ticker,
        promotion_min_etf_aum_b,
        max_bid_ask_spread_percent / 100.0,
    )


def _render_etf_guardrail_inputs(
    *,
    key_prefix: str,
    label_prefix: str = "ETF ",
) -> tuple[bool, int, float, bool, int, float, float]:
    st.markdown("##### ETF Second-Pass Guardrails")
    st.caption(
        "ETF 전략군 second pass에서는 benchmark-relative trailing 약세와 낙폭 악화를 "
        "실제 rebalance cash fallback 규칙으로도 실험할 수 있습니다."
    )
    (
        underperformance_guardrail_enabled,
        underperformance_guardrail_window_months,
        underperformance_guardrail_threshold,
    ) = _render_underperformance_guardrail_inputs(
        key_prefix=key_prefix,
        label_prefix=label_prefix,
    )
    (
        drawdown_guardrail_enabled,
        drawdown_guardrail_window_months,
        drawdown_guardrail_strategy_threshold,
        drawdown_guardrail_gap_threshold,
    ) = _render_drawdown_guardrail_inputs(
        key_prefix=key_prefix,
        label_prefix=label_prefix,
    )
    return (
        underperformance_guardrail_enabled,
        underperformance_guardrail_window_months,
        underperformance_guardrail_threshold,
        drawdown_guardrail_enabled,
        drawdown_guardrail_window_months,
        drawdown_guardrail_strategy_threshold,
        drawdown_guardrail_gap_threshold,
    )


def _render_strict_annual_real_money_inputs(
    *,
    key_prefix: str,
    default_min_price: float = ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
    default_min_history_months: int = STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
    default_min_avg_dollar_volume_20d_m: float = STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
    default_transaction_cost_bps: float = ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
    default_benchmark_contract: str = STRICT_DEFAULT_BENCHMARK_CONTRACT,
    default_benchmark: str = ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    default_promotion_min_benchmark_coverage: float = STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
    default_promotion_min_net_cagr_spread: float = STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
    default_promotion_min_liquidity_clean_coverage: float = STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
    default_promotion_max_underperformance_share: float = STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
    default_promotion_min_worst_rolling_excess_return: float = STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
    default_promotion_max_strategy_drawdown: float = STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
    default_promotion_max_drawdown_gap_vs_benchmark: float = STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
) -> tuple[str, float, int, float, float, str, float, float, float, float, float, float, float]:
    st.markdown("##### Real-Money Contract")
    st.caption("설명은 `Reference > Guides > Real-Money Contract 값 해설` 또는 `Reference > Glossary`에서 다시 볼 수 있습니다.")
    st.caption(
        "실전형 annual strict contract에서는 `Minimum Price`, `Minimum History (Months)`, "
        "`Minimum Avg Dollar Volume 20D`, `Transaction Cost`, `Benchmark Contract`, `Benchmark Ticker`, "
        "`Benchmark Policy`, `Validation Policy`, `Portfolio Guardrail Policy`를 같이 사용합니다."
    )
    col1, col2, col3, col4, col5 = st.columns(5, gap="small")
    with col1:
        min_price_filter = float(
            st.number_input(
                "Minimum Price",
                min_value=0.0,
                max_value=1000.0,
                value=float(default_min_price),
                step=1.0,
                key=f"{key_prefix}_min_price_filter",
                help="이 값보다 싼 종목은 해당 날짜 투자 후보에서 제외합니다.",
            )
        )
    with col2:
        min_history_months_filter = int(
            st.number_input(
                "Minimum History (Months)",
                min_value=0,
                max_value=120,
                value=int(default_min_history_months),
                step=1,
                key=f"{key_prefix}_min_history_months_filter",
                help="이 개월 수보다 짧은 가격 이력만 있는 종목은 해당 날짜 후보에서 제외합니다. 0이면 비활성화입니다.",
            )
        )
    with col3:
        min_avg_dollar_volume_20d_m_filter = float(
            st.number_input(
                "Min Avg Dollar Volume 20D ($M)",
                min_value=0.0,
                max_value=5000.0,
                value=float(default_min_avg_dollar_volume_20d_m),
                step=1.0,
                key=f"{key_prefix}_min_avg_dollar_volume_20d_m_filter",
                help=(
                    "OHLCV의 `close × volume`으로 하루 거래대금을 만든 뒤, 최근 20거래일 평균을 계산합니다. "
                    "그 평균이 이 값보다 낮은 종목은 해당 날짜 후보에서 제외합니다. 단위는 백만 달러입니다."
                ),
            )
        )
    with col4:
        transaction_cost_bps = float(
            st.number_input(
                "Transaction Cost (bps)",
                min_value=0.0,
                max_value=500.0,
                value=float(default_transaction_cost_bps),
                step=1.0,
                key=f"{key_prefix}_transaction_cost_bps",
                help="리밸런싱 turnover 비율에 곱하는 왕복 비용 가정입니다. 10bps = 0.10%입니다.",
            )
        )
    with col5:
        benchmark_contract_label = st.selectbox(
            "Benchmark Contract",
            options=list(STRICT_BENCHMARK_CONTRACT_LABELS.keys()),
            index=list(STRICT_BENCHMARK_CONTRACT_LABELS.values()).index(
                str(default_benchmark_contract or STRICT_DEFAULT_BENCHMARK_CONTRACT).strip().lower()
                if str(default_benchmark_contract or "").strip().lower() in STRICT_BENCHMARK_CONTRACT_LABELS.values()
                else STRICT_DEFAULT_BENCHMARK_CONTRACT
            ),
            key=f"{key_prefix}_benchmark_contract",
            help=(
                "이 전략을 무엇과 비교할지 정하는 기준입니다.\n\n"
                "- `Ticker Benchmark`: `SPY` 같은 기준 ETF 1개와 직접 비교합니다.\n"
                "- `Candidate Universe Equal-Weight`: 같은 후보 universe에서 그 시점에 투자 가능했던 종목들을 단순 균등 비중으로 담은 기준선과 비교합니다.\n\n"
                "쉽게 말하면, `Ticker Benchmark`는 외부 기준 ETF와 비교하는 방식이고, "
                "`Candidate Universe Equal-Weight`는 같은 후보군 안에서 '복잡한 전략 없이 그냥 고르게 샀을 때'와 비교하는 방식입니다."
            ),
        )
        benchmark_contract = STRICT_BENCHMARK_CONTRACT_LABELS[benchmark_contract_label]
    default_benchmark = str(default_benchmark or ETF_REAL_MONEY_DEFAULT_BENCHMARK).strip().upper()
    benchmark_ticker = str(
        st.text_input(
            "Benchmark Ticker",
            value=default_benchmark,
            key=f"{key_prefix}_benchmark_ticker",
            help=(
                "전략 결과를 직접 비교할 benchmark ticker입니다.\n\n"
                "- `Ticker Benchmark`일 때: 이 입력값을 그대로 benchmark curve로 사용합니다.\n"
                "- `Candidate Universe Equal-Weight`일 때: benchmark curve는 후보군 equal-weight로 자동 생성되므로, "
                "이 입력값은 직접 비교 baseline 계산에는 쓰이지 않습니다."
            ),
        )
    ).strip().upper()
    st.caption(
        "`Benchmark Contract`는 비교 방식을 뜻하고, `Benchmark Ticker`는 실제로 무엇과 직접 비교할지를 뜻합니다. "
        "`Guardrail / Reference Ticker`는 아래 `Guardrails` 탭에서 따로 정합니다."
    )
    st.caption(
        "`Candidate Universe Equal-Weight`에서는 benchmark curve가 후보군 equal-weight로 자동 생성됩니다. "
        "그래서 이 경우 `Benchmark Ticker`는 직접 비교 baseline 계산에는 쓰이지 않습니다. "
        "guardrail 기준 ticker는 아래 `Guardrails` 탭에서 따로 정할 수 있습니다."
    )

    policy_left, policy_right = st.columns(2, gap="small")
    with policy_left:
        promotion_min_benchmark_coverage = float(
            st.number_input(
                "Min Benchmark Coverage (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(default_promotion_min_benchmark_coverage) * 100.0,
                step=1.0,
                key=f"{key_prefix}_promotion_min_benchmark_coverage",
                help="승격 판단에서 benchmark와 날짜가 충분히 겹쳐야 하는 최소 비율입니다.",
            )
        )
    with policy_right:
        promotion_min_net_cagr_spread = float(
            st.number_input(
                "Min Net CAGR Spread (%)",
                min_value=-100.0,
                max_value=100.0,
                value=float(default_promotion_min_net_cagr_spread) * 100.0,
                step=1.0,
                key=f"{key_prefix}_promotion_min_net_cagr_spread",
                help="전략의 net CAGR이 benchmark CAGR보다 이 값 이상 높거나 덜 나빠야 승격 후보로 인정합니다.",
            )
        )

    promotion_min_liquidity_clean_coverage = float(
        st.number_input(
            "Min Liquidity Clean Coverage (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(default_promotion_min_liquidity_clean_coverage) * 100.0,
            step=1.0,
            key=f"{key_prefix}_promotion_min_liquidity_clean_coverage",
            help=(
                "먼저 각 종목이 `Min Avg Dollar Volume 20D` 기준을 통과하는지 보고, "
                "그 다음 리밸런싱 행 중 유동성 제외 없이 지나간 비율이 이 값 이상이어야 "
                "`Liquidity Policy`를 정상에 가깝게 읽습니다."
            ),
        )
    )

    st.caption(
        "`Minimum History (Months)`는 각 리밸런싱 시점 전에 최소 몇 개월의 가격 이력이 쌓여 있어야 "
        "그 종목을 투자 후보로 인정할지를 뜻합니다."
    )
    if float(min_avg_dollar_volume_20d_m_filter or 0.0) > 0.0:
        st.caption(
            "`Min Avg Dollar Volume 20D ($M)`는 최근 20거래일 평균 거래대금이 충분히 큰 종목만 남겨서 "
            "실제로 사고팔기 너무 어려운 후보를 줄이기 위한 필터입니다."
        )
    st.caption(
        "`Benchmark Policy`는 benchmark overlay가 있더라도 커버리지와 상대 CAGR이 너무 약하면 "
        "바로 `real_money_candidate`로 올리지 않도록 하는 승격 기준입니다."
    )
    st.caption(
        "`Comparison Baseline`은 이 전략을 무엇과 직접 비교할지 정하는 부분이고, "
        "`Guardrail / Reference Ticker`는 아래 `Guardrails` 탭에서 underperformance / drawdown guardrail 기준으로 따로 정하는 부분입니다."
    )
    if benchmark_contract == STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT:
        st.caption(
            "`Candidate Universe Equal-Weight`는 같은 후보 universe에서 그 시점에 투자 가능했던 종목들을 "
            "복잡한 ranking 없이 그냥 똑같이 나눠 담았을 때의 기준선입니다. "
            "즉 `SPY` 같은 외부 ETF와 비교하는 대신, 같은 후보군 안에서 단순하게 투자했을 때보다 전략이 실제로 더 나은지 보려는 목적입니다."
        )
        st.caption(
            "이 모드에서는 `Benchmark Ticker`는 benchmark curve 계산에 쓰이지 않습니다. "
            "guardrail 기준 ticker는 아래 `Guardrails` 탭에서 따로 정합니다."
        )
    else:
        st.caption(
            "`Ticker Benchmark` 모드에서는 `Benchmark Ticker`가 직접 비교 curve를 만듭니다. "
            "guardrail 기준을 benchmark와 같게 둘지 다르게 둘지는 아래 `Guardrails` 탭에서 정합니다."
        )
    st.caption(
        "`Liquidity Clean Coverage`는 리밸런싱 행 대부분이 유동성 제외 없이 지나가야 "
        "실전 승격 후보로 인정하겠다는 later-pass 기준입니다."
    )
    robustness_left, robustness_right = st.columns(2, gap="small")
    with robustness_left:
        promotion_max_underperformance_share = float(
            st.number_input(
                "Max Underperformance Share (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(default_promotion_max_underperformance_share) * 100.0,
                step=1.0,
                key=f"{key_prefix}_promotion_max_underperformance_share",
                help=(
                    "rolling 구간은 일정 길이의 비교 창을 한 칸씩 옮겨가며 보는 구간입니다. "
                    "그 rolling 구간들 중 benchmark보다 뒤처진 비율이 이 값보다 높으면 "
                    '\"너무 자주 benchmark에 진다\"고 보고 승격을 보수적으로 해석합니다.'
                ),
            )
        )
    with robustness_right:
        promotion_min_worst_rolling_excess_return = float(
            st.number_input(
                "Min Worst Rolling Excess (%)",
                min_value=-100.0,
                max_value=100.0,
                value=float(default_promotion_min_worst_rolling_excess_return) * 100.0,
                step=1.0,
                key=f"{key_prefix}_promotion_min_worst_rolling_excess_return",
                help=(
                    "rolling 구간들 중 benchmark 대비 상대 성과가 가장 나빴던 구간을 봅니다. "
                    "그 최악 구간의 excess return이 이 값보다 더 낮으면 "
                    '\"특정 시기에 너무 크게 무너졌다\"고 보고 승격을 보수적으로 해석합니다.'
                ),
            )
        )
    st.caption(
        "여기서 `rolling 구간`은 전체 기간을 한 번에 보지 않고, "
        "일정 길이의 비교 창(window)을 한 칸씩 옮겨가며 반복해서 보는 작은 평가 구간을 뜻합니다."
    )
    st.caption(
        "`Validation Policy`는 benchmark-relative validation 지표 중 "
        "`Underperformance Share`와 `Worst Rolling Excess`를 실제 승격 판단 기준으로 연결한 later-pass rule입니다."
    )
    guardrail_left, guardrail_right = st.columns(2, gap="small")
    with guardrail_left:
        promotion_max_strategy_drawdown = float(
            st.number_input(
                "Max Strategy Drawdown (%)",
                min_value=-100.0,
                max_value=0.0,
                value=float(default_promotion_max_strategy_drawdown) * 100.0,
                step=1.0,
                key=f"{key_prefix}_promotion_max_strategy_drawdown",
                help=(
                    "전략 자체 최대 낙폭이 이 값보다 더 깊으면 "
                    '\"수익률이 좋아도 손실 구간이 너무 깊다\"고 보고 승격을 보수적으로 해석합니다.'
                ),
            )
        )
    with guardrail_right:
        promotion_max_drawdown_gap_vs_benchmark = float(
            st.number_input(
                "Max Drawdown Gap vs Benchmark (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(default_promotion_max_drawdown_gap_vs_benchmark) * 100.0,
                step=1.0,
                key=f"{key_prefix}_promotion_max_drawdown_gap_vs_benchmark",
                help=(
                    "전략 최대 낙폭이 benchmark보다 이 값 이상 더 나쁘면 "
                    '\"benchmark 대비 downside behavior가 너무 약하다\"고 보고 승격을 보수적으로 해석합니다.'
                ),
            )
        )
    st.caption(
        "`Portfolio Guardrail Policy`는 수익률이 좋아 보여도 낙폭이 너무 깊거나 benchmark보다 지나치게 나쁜 경우에는 "
        "실전 승격을 더 보수적으로 보겠다는 later-pass 기준입니다."
    )
    return (
        benchmark_contract,
        min_price_filter,
        min_history_months_filter,
        min_avg_dollar_volume_20d_m_filter,
        transaction_cost_bps,
        benchmark_ticker,
        promotion_min_benchmark_coverage / 100.0,
        promotion_min_net_cagr_spread / 100.0,
        promotion_min_liquidity_clean_coverage / 100.0,
        promotion_max_underperformance_share / 100.0,
        promotion_min_worst_rolling_excess_return / 100.0,
        promotion_max_strategy_drawdown / 100.0,
        promotion_max_drawdown_gap_vs_benchmark / 100.0,
    )


def _render_underperformance_guardrail_inputs(
    *,
    key_prefix: str,
    label_prefix: str = "",
) -> tuple[bool, int, float]:
    st.markdown(f"##### {label_prefix}Underperformance Guardrail")
    st.caption(
        "전략의 trailing 성과가 benchmark보다 일정 수준 이상 계속 약하면, "
        "다음 리밸런싱 구간은 현금으로 물러나는 실험적 guardrail입니다."
    )
    enabled = st.checkbox(
        "Enable",
        value=STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
        key=f"{key_prefix}_underperformance_guardrail_enabled",
    )
    left, right = st.columns(2, gap="small")
    with left:
        window_months = int(
            st.number_input(
                f"{label_prefix}Guardrail Window (Months)",
                min_value=3,
                max_value=36,
                value=STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
                step=1,
                key=f"{key_prefix}_underperformance_guardrail_window_months",
                help="전략과 benchmark의 trailing 비교를 몇 개월 기준으로 볼지 정합니다.",
            )
        )
    with right:
        threshold_percent = float(
            st.number_input(
                f"{label_prefix}Worst Excess Threshold (%)",
                min_value=-50.0,
                max_value=0.0,
                value=float(STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD) * 100.0,
                step=1.0,
                key=f"{key_prefix}_underperformance_guardrail_threshold",
                help="전략 trailing 수익률이 benchmark보다 이 값 이하로 더 나쁘면 guardrail을 켭니다.",
            )
        )
    st.caption("Enable이 꺼져 있어도 Window와 Threshold는 미리 조정해둘 수 있습니다.")
    return enabled, window_months, threshold_percent / 100.0


def _render_drawdown_guardrail_inputs(
    *,
    key_prefix: str,
    label_prefix: str = "",
) -> tuple[bool, int, float, float]:
    st.markdown(f"##### {label_prefix}Drawdown Guardrail")
    st.caption(
        "전략의 최근 낙폭이 너무 깊어지거나 benchmark보다 낙폭이 지나치게 나빠지면, "
        "다음 리밸런싱 구간은 현금으로 물러나는 실험적 guardrail입니다."
    )
    enabled = st.checkbox(
        "Enable",
        value=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
        key=f"{key_prefix}_drawdown_guardrail_enabled",
    )
    left, center, right = st.columns(3, gap="small")
    with left:
        window_months = int(
            st.number_input(
                f"{label_prefix}Drawdown Window (Months)",
                min_value=3,
                max_value=36,
                value=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
                step=1,
                key=f"{key_prefix}_drawdown_guardrail_window_months",
                help="전략과 benchmark의 trailing drawdown을 몇 개월 기준으로 볼지 정합니다.",
            )
        )
    with center:
        strategy_threshold_percent = float(
            st.number_input(
                f"{label_prefix}Strategy DD Threshold (%)",
                min_value=-80.0,
                max_value=0.0,
                value=float(STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD) * 100.0,
                step=1.0,
                key=f"{key_prefix}_drawdown_guardrail_strategy_threshold",
                help="전략의 trailing drawdown이 이 값보다 더 깊어지면 guardrail을 켭니다.",
            )
        )
    with right:
        gap_threshold_percent = float(
            st.number_input(
                f"{label_prefix}Drawdown Gap Threshold (%)",
                min_value=0.0,
                max_value=50.0,
                value=float(STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD) * 100.0,
                step=1.0,
                key=f"{key_prefix}_drawdown_guardrail_gap_threshold",
                help="전략 drawdown이 benchmark보다 이 값 이상 더 나빠지면 guardrail을 켭니다.",
            )
        )
    st.caption("Enable이 꺼져 있어도 Window와 Threshold는 미리 조정해둘 수 있습니다.")
    return (
        enabled,
        window_months,
        strategy_threshold_percent / 100.0,
        gap_threshold_percent / 100.0,
    )


def _render_guardrail_reference_ticker_input(
    *,
    key_prefix: str,
    benchmark_ticker: str,
    default_guardrail_reference_ticker: str | None = None,
    underperformance_guardrail_enabled: bool = False,
    drawdown_guardrail_enabled: bool = False,
) -> str:
    st.markdown("##### Guardrail / Reference Ticker")
    raw_guardrail_default = str(default_guardrail_reference_ticker or "").strip().upper()
    benchmark_ticker = str(benchmark_ticker or ETF_REAL_MONEY_DEFAULT_BENCHMARK).strip().upper()
    optional_guardrail_default = (
        raw_guardrail_default if raw_guardrail_default and raw_guardrail_default != benchmark_ticker else ""
    )
    guardrail_reference_ticker = str(
        st.text_input(
            "Guardrail / Reference Ticker (Optional)",
            value=optional_guardrail_default,
            key=f"{key_prefix}_guardrail_reference_ticker",
            placeholder="비워두면 Benchmark Ticker와 동일하게 사용",
            help=(
                "underperformance / drawdown guardrail이 따로 참고하는 기준 ticker입니다.\n\n"
                "비워두면 기본적으로 `Benchmark Ticker`를 그대로 같이 사용합니다.\n"
                "즉 benchmark와 guardrail을 같은 ticker로 볼 거면 비워둬도 됩니다."
            ),
        )
    ).strip().upper()
    if underperformance_guardrail_enabled or drawdown_guardrail_enabled:
        st.caption(
            "현재 guardrail이 켜져 있으면 이 값이 underperformance / drawdown guardrail 기준 ticker로 사용됩니다. "
            "비워두면 `Benchmark Ticker`를 그대로 같이 사용합니다."
        )
    else:
        st.caption(
            "현재 guardrail 둘 다 꺼져 있으면 이 값은 실질적으로 영향이 없습니다. "
            "나중에 guardrail을 켤 때를 대비해 미리 적어둘 수 있습니다."
        )
    return guardrail_reference_ticker


def _gtaa_return_col_from_months(months: int) -> str:
    return f"{int(months)}MReturn"


def _gtaa_months_from_return_col(return_col: str) -> int | None:
    text = str(return_col or "").strip()
    if not text.endswith("MReturn"):
        return None
    number_text = text[:-7]
    if not number_text.isdigit():
        return None
    months = int(number_text)
    return months if months > 0 else None


def _build_equal_gtaa_score_weights(score_lookback_months: list[int]) -> dict[str, float]:
    return {
        _gtaa_return_col_from_months(int(months)): 1.0
        for months in score_lookback_months
    }


def _set_gtaa_score_selection_state(
    *,
    key_prefix: str,
    score_lookback_months: list[int] | None,
) -> None:
    normalized: list[int] = []
    seen: set[int] = set()
    for value in list(score_lookback_months or GTAA_DEFAULT_SCORE_LOOKBACK_MONTHS):
        try:
            months = int(value)
        except (TypeError, ValueError):
            continue
        if months <= 0 or months in seen:
            continue
        seen.add(months)
        normalized.append(months)
    if not normalized:
        normalized = list(GTAA_DEFAULT_SCORE_LOOKBACK_MONTHS)
    st.session_state[f"{key_prefix}_score_lookback_months"] = normalized


def _set_global_relative_strength_score_selection_state(
    *,
    key_prefix: str,
    score_lookback_months: list[int] | None,
) -> None:
    normalized: list[int] = []
    seen: set[int] = set()
    for value in list(score_lookback_months or GLOBAL_RELATIVE_STRENGTH_DEFAULT_SCORE_LOOKBACK_MONTHS):
        try:
            months = int(value)
        except (TypeError, ValueError):
            continue
        if months <= 0 or months in seen:
            continue
        seen.add(months)
        normalized.append(months)
    if not normalized:
        normalized = list(GLOBAL_RELATIVE_STRENGTH_DEFAULT_SCORE_LOOKBACK_MONTHS)
    st.session_state[f"{key_prefix}_score_lookback_months"] = normalized


def _render_gtaa_score_weight_inputs(*, key_prefix: str) -> tuple[list[int], dict[str, float]]:
    st.markdown("##### Score Horizons")
    st.caption(
        "기본값은 `1M / 3M / 6M / 12M`이고, 여기서 사용할 horizon만 고를 수 있습니다. "
        "선택된 horizon은 모두 동일 비중으로 점수에 반영됩니다."
    )
    score_lookback_months = st.multiselect(
        "Score Horizons",
        options=list(GTAA_DEFAULT_SCORE_LOOKBACK_MONTHS),
        default=list(GTAA_DEFAULT_SCORE_LOOKBACK_MONTHS),
        format_func=lambda months: f"{int(months)}M",
        key=f"{key_prefix}_score_lookback_months",
        help="GTAA score 계산에 실제로 포함할 horizon입니다. 예를 들어 `1M, 3M`만 남기면 두 구간만 균등하게 사용합니다.",
    )
    if not score_lookback_months:
        st.warning("Score Horizon을 최소 1개는 선택해야 합니다.")
    score_weights = _build_equal_gtaa_score_weights(list(score_lookback_months))
    return score_lookback_months, score_weights


def _render_global_relative_strength_score_weight_inputs(*, key_prefix: str) -> tuple[list[int], dict[str, float]]:
    st.markdown("##### Score Horizons")
    st.caption(
        "상대강도 점수를 계산할 기간입니다. 기본값은 `1M / 3M / 6M / 12M`이고, "
        "선택된 기간은 동일 비중으로 합산합니다."
    )
    score_lookback_months = st.multiselect(
        "Score Horizons",
        options=list(GLOBAL_RELATIVE_STRENGTH_DEFAULT_SCORE_LOOKBACK_MONTHS),
        default=list(GLOBAL_RELATIVE_STRENGTH_DEFAULT_SCORE_LOOKBACK_MONTHS),
        format_func=lambda months: f"{int(months)}M",
        key=f"{key_prefix}_score_lookback_months",
        help="Global Relative Strength score에 포함할 lookback 기간입니다.",
    )
    if not score_lookback_months:
        st.warning("Score Horizon을 최소 1개는 선택해야 합니다.")
    score_weights = _build_equal_gtaa_score_weights(list(score_lookback_months))
    return score_lookback_months, score_weights


def _risk_off_mode_value_to_label(value: str | None) -> str:
    for label, mode_value in GTAA_RISK_OFF_MODE_LABELS.items():
        if mode_value == value:
            return label
    return "Cash Only"


def _strict_risk_off_mode_value_to_label(value: str | None) -> str:
    for label, mode_value in STRICT_RISK_OFF_MODE_LABELS.items():
        if mode_value == value:
            return label
    return "Cash Only"


def _strict_weighting_mode_value_to_label(value: str | None) -> str:
    for label, mode_value in STRICT_WEIGHTING_MODE_LABELS.items():
        if mode_value == value:
            return label
    return "Equal Weight"


def _strict_rejection_handling_mode_value_to_label(value: str | None) -> str:
    resolved_mode = resolve_strict_rejection_handling_mode(value)
    for label, mode_value in STRICT_REJECTION_HANDLING_MODE_LABELS.items():
        if mode_value == resolved_mode:
            return label
    return "Reweight Survivors"


def _strict_rejection_handling_label_from_flags(
    *,
    rejected_slot_fill_enabled: bool,
    partial_cash_retention_enabled: bool,
) -> str:
    return _strict_rejection_handling_mode_value_to_label(
        resolve_strict_rejection_handling_mode(
            None,
            rejected_slot_fill_enabled=rejected_slot_fill_enabled,
            partial_cash_retention_enabled=partial_cash_retention_enabled,
        )
    )


def _strict_risk_off_reason_to_label(reason: str | None) -> str:
    normalized = str(reason or "").strip().lower()
    mapping = {
        "market_regime": "Market Regime",
        "underperformance_guardrail": "Underperformance Guardrail",
        "drawdown_guardrail": "Drawdown Guardrail",
        "crash_guardrail": "Crash Guardrail",
    }
    return mapping.get(normalized, normalized or "Unknown")


def _stringify_label_list(value: Any, *, label_fn: Callable[[str | None], str] | None = None) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    if isinstance(value, (list, tuple, set)):
        labels = [
            (label_fn(item) if label_fn else str(item).strip())
            for item in value
        ]
        labels = [label for label in labels if str(label).strip()]
        return ", ".join(labels)
    text = str(value).strip()
    if not text:
        return ""
    return label_fn(text) if label_fn else text


def _render_gtaa_risk_off_contract_inputs(*, key_prefix: str) -> dict[str, Any]:
    st.markdown("##### Risk-Off Contract")
    st.caption(
        "GTAA가 위험구간으로 판단될 때 현금으로 물러날지, 방어 채권으로 더 채울지, "
        "그리고 어떤 조건을 위험구간으로 볼지 설정합니다."
    )
    left, right = st.columns(2, gap="small")
    with left:
        trend_filter_window = int(
            st.number_input(
                "Trend Filter Window",
                min_value=20,
                max_value=400,
                value=GTAA_DEFAULT_TREND_FILTER_WINDOW,
                step=10,
                key=f"{key_prefix}_trend_filter_window",
                help="GTAA 각 후보가 통과해야 하는 이동평균 필터 기간입니다. 기본은 `MA200`입니다.",
            )
        )
    with right:
        risk_off_mode_label = st.selectbox(
            "Fallback Mode",
            options=list(GTAA_RISK_OFF_MODE_LABELS.keys()),
            index=list(GTAA_RISK_OFF_MODE_LABELS.values()).index(GTAA_DEFAULT_RISK_OFF_MODE),
            key=f"{key_prefix}_risk_off_mode",
            help="위험구간 또는 top 후보 부족 시 현금만 들고 있을지, 방어 채권으로 남은 슬롯을 채울지 고릅니다.",
        )

    defensive_tickers_text = st.text_input(
        "Defensive Tickers",
        value=",".join(GTAA_DEFAULT_DEFENSIVE_TICKERS),
        key=f"{key_prefix}_defensive_tickers",
        help="Fallback Mode가 `Defensive Bond Preference`일 때 사용할 방어 채권 후보입니다.",
    )

    regime_enabled, regime_window, regime_benchmark = _render_market_regime_overlay_inputs(
        key_prefix=f"{key_prefix}_risk_off",
        label_prefix="GTAA ",
    )

    crash_cols = st.columns([0.32, 0.34, 0.34], gap="small")
    with crash_cols[0]:
        crash_guardrail_enabled = st.checkbox(
            "Enable Crash Guardrail",
            value=GTAA_DEFAULT_CRASH_GUARDRAIL_ENABLED,
            key=f"{key_prefix}_crash_guardrail_enabled",
            help="벤치마크가 최근 고점 대비 크게 빠지면 GTAA를 위험구간으로 간주합니다.",
        )
    with crash_cols[1]:
        crash_guardrail_drawdown_threshold = float(
            st.number_input(
                "Crash Drawdown Threshold (%)",
                min_value=1.0,
                max_value=80.0,
                value=float(GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD * 100.0),
                step=1.0,
                key=f"{key_prefix}_crash_guardrail_drawdown_threshold",
                help="이 비율 이상 벤치마크가 최근 고점에서 빠지면 crash-side guardrail을 켭니다.",
            )
        )
    with crash_cols[2]:
        crash_guardrail_lookback_months = int(
            st.number_input(
                "Crash Lookback (months)",
                min_value=3,
                max_value=36,
                value=GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS,
                step=1,
                key=f"{key_prefix}_crash_guardrail_lookback_months",
                help="최근 몇 개월의 고점을 기준으로 drawdown을 계산할지 정합니다.",
            )
        )

    return {
        "trend_filter_window": trend_filter_window,
        "risk_off_mode": GTAA_RISK_OFF_MODE_LABELS[risk_off_mode_label],
        "defensive_tickers": _parse_manual_tickers(defensive_tickers_text),
        "market_regime_enabled": bool(regime_enabled),
        "market_regime_window": int(regime_window),
        "market_regime_benchmark": regime_benchmark,
        "crash_guardrail_enabled": bool(crash_guardrail_enabled),
        "crash_guardrail_drawdown_threshold": float(crash_guardrail_drawdown_threshold) / 100.0,
        "crash_guardrail_lookback_months": int(crash_guardrail_lookback_months),
    }


def _render_strict_defensive_sleeve_contract_inputs(
    *,
    key_prefix: str,
    label_prefix: str = "",
) -> tuple[str, list[str]]:
    prefix = label_prefix.strip()
    label_base = f"{prefix} " if prefix else ""
    title_col, help_col = st.columns([0.92, 0.08], gap="small")
    with title_col:
        st.markdown("##### Risk-Off Contract")
    with help_col:
        _render_strict_risk_off_contract_help_popover()
    st.caption(
        "`Market Regime`이나 guardrail 때문에 factor 포트폴리오 전체를 그대로 두지 못할 때, "
        "현금으로 쉴지 방어 ETF sleeve로 옮길지 정합니다."
    )
    st.caption(
        "쉽게 말해, 일부 종목 몇 개만 빠지는 상황이 아니라 "
        "이번 리밸런싱에서 포트폴리오 전체를 현금 또는 방어 ETF 쪽으로 전환하는 규칙입니다."
    )
    risk_off_mode_label = st.selectbox(
        f"{label_base}Risk-Off Contract",
        options=list(STRICT_RISK_OFF_MODE_LABELS.keys()),
        index=list(STRICT_RISK_OFF_MODE_LABELS.values()).index(STRICT_DEFAULT_RISK_OFF_MODE),
        key=f"{key_prefix}_risk_off_mode",
        help="포트폴리오 전체를 쉬어야 할 때 `Cash Only`로 둘지, `Defensive Sleeve Preference`로 방어 ETF sleeve를 담을지 정합니다.",
    )
    risk_off_mode = STRICT_RISK_OFF_MODE_LABELS[risk_off_mode_label]
    st.caption(f"현재 선택: {STRICT_RISK_OFF_MODE_EXPLANATIONS[risk_off_mode]}")
    st.caption(
        "`Defensive Sleeve Risk-Off`는 위 `Risk-Off Contract`에서 "
        "`Defensive Sleeve Preference`를 골랐을 때 사용하는 방어 ETF fallback입니다."
    )
    defensive_tickers_text = st.text_input(
        f"{label_base}Defensive Sleeve Tickers",
        value=",".join(STRICT_DEFAULT_DEFENSIVE_TICKERS),
        key=f"{key_prefix}_defensive_tickers",
        help="`Risk-Off Contract = Defensive Sleeve Preference`일 때 포트폴리오 전체를 쉬어야 하는 구간에서 동일가중으로 담을 방어 ETF 목록입니다. 예: `BIL,SHY,LQD`. `Cash Only`면 저장은 되지만 실제로는 사용되지 않습니다.",
    )
    st.caption(
        "`Defensive Sleeve Tickers`는 포트폴리오 전체를 쉬어야 할 때 현금 대신 잠시 담을 방어 ETF 목록입니다. "
        "예를 들어 `BIL, SHY, LQD`를 넣으면 해당 구간에 이 세 ETF를 동일가중으로 사용합니다."
    )
    return (
        risk_off_mode,
        _parse_manual_tickers(defensive_tickers_text),
    )


def _render_strict_weighting_contract_inputs(
    *,
    key_prefix: str,
    label_prefix: str = "",
) -> str:
    prefix = label_prefix.strip()
    label_base = f"{prefix} " if prefix else ""
    title_col, help_col = st.columns([0.92, 0.08], gap="small")
    with title_col:
        st.markdown("##### Weighting Contract")
    with help_col:
        _render_strict_weighting_contract_help_popover()
    st.caption(
        "최종 선택된 종목에 비중을 어떻게 나눌지 정합니다. "
        "strict annual 기본은 `Equal Weight`이고, `Rank-Tapered`는 상위 rank에 조금 더 무게를 두는 실험적 옵션입니다."
    )
    st.caption(
        "쉽게 말해, 무엇을 살지 정한 뒤 그 종목들을 얼마씩 담을지를 정하는 기본 비중 규칙입니다."
    )
    weighting_mode_label = st.selectbox(
        f"{label_base}Weighting Contract",
        options=list(STRICT_WEIGHTING_MODE_LABELS.keys()),
        index=list(STRICT_WEIGHTING_MODE_LABELS.values()).index(STRICT_DEFAULT_WEIGHTING_MODE),
        key=f"{key_prefix}_weighting_mode",
        help="`Equal Weight`는 모든 선택 종목을 동일 비중으로 보유합니다. "
        "`Rank-Tapered`는 상위 rank 종목을 약간 더 비중 있게 담되, 과도한 집중은 피하는 완만한 taper를 씁니다.",
    )
    weighting_mode = STRICT_WEIGHTING_MODE_LABELS[weighting_mode_label]
    st.caption(f"현재 선택: {STRICT_WEIGHTING_MODE_EXPLANATIONS[weighting_mode]}")
    return weighting_mode


def _render_strict_rejected_slot_handling_contract_inputs(
    *,
    key_prefix: str,
    label_prefix: str = "",
) -> str:
    prefix = label_prefix.strip()
    label_base = f"{prefix} " if prefix else ""
    title_col, help_col = st.columns([0.92, 0.08], gap="small")
    with title_col:
        st.markdown("##### Rejected Slot Handling Contract")
    with help_col:
        _render_rejected_slot_handling_help_popover()
    st.caption(
        "Trend Filter가 raw top-N 일부를 탈락시킨 뒤, 빈 슬롯을 다음 순위 이름으로 보충할지 "
        "혹은 최종적으로 현금/재배분으로 처리할지를 정합니다."
    )
    st.caption(
        "쉽게 말해, 상위 후보 중 일부 종목만 빠졌을 때 그 빈 자리를 어떻게 처리할지 정하는 규칙입니다."
    )
    handling_mode_label = st.selectbox(
        f"{label_base}Rejected Slot Handling Contract",
        options=list(STRICT_REJECTION_HANDLING_MODE_LABELS.keys()),
        index=list(STRICT_REJECTION_HANDLING_MODE_LABELS.values()).index(STRICT_DEFAULT_REJECTION_HANDLING_MODE),
        key=f"{key_prefix}_rejected_slot_handling_mode",
        help="`Fill Then ...`은 먼저 다음 순위의 추세 통과 종목으로 채우고, 남는 슬롯만 현금 유지 또는 재배분합니다. "
        "`Retain ... Cash`는 trend rejection 이후 남은 빈 슬롯 비중을 현금으로 남깁니다.",
    )
    handling_mode = STRICT_REJECTION_HANDLING_MODE_LABELS[handling_mode_label]
    st.caption(f"현재 선택: {STRICT_REJECTION_HANDLING_MODE_EXPLANATIONS[handling_mode]}")
    return handling_mode


def _render_strict_price_freshness_preflight(
    *,
    tickers: list[str],
    end_value: date,
    timeframe: str,
    strategy_label: str,
) -> None:
    if not tickers:
        return

    report = inspect_strict_annual_price_freshness(
        tickers=tickers,
        end=end_value.isoformat(),
        timeframe=timeframe,
    )
    details = report.get("details") or {}

    title_col, help_col = st.columns([0.92, 0.08], gap="small")
    with title_col:
        st.markdown("#### Price Freshness Preflight")
    with help_col:
        _render_historical_universe_help_popover()
    st.caption(f"Current DB latest-date spread for `{strategy_label}` before execution.")
    st.caption("`Stale` means the symbol's latest daily price in DB stops before the effective trading end used for this check.")
    if (
        details.get("selected_end_date")
        and details.get("effective_end_date")
        and details.get("selected_end_date") != details.get("effective_end_date")
    ):
        st.caption(
            f"Selected end `{details['selected_end_date']}` is being compared against effective trading end `{details['effective_end_date']}`."
        )

    if report["status"] == "ok":
        st.success(report["message"])
    elif report["status"] == "warning":
        st.warning(report["message"])
    else:
        st.error(report["message"])

    metric_cols = st.columns(5)
    metric_cols[0].metric("Requested", details.get("requested_count", 0))
    metric_cols[1].metric("Covered", details.get("covered_count", 0))
    metric_cols[2].metric("Common Latest", details.get("common_latest_date", "-"))
    metric_cols[3].metric("Newest Latest", details.get("newest_latest_date", "-"))
    metric_cols[4].metric("Spread", f"{details.get('spread_days', 0)}d")

    if details.get("stale_count", 0) > 0 or details.get("missing_count", 0) > 0:
        with st.expander("Preflight Details", expanded=False):
            if details.get("selected_end_date"):
                st.markdown(f"- `Selected End`: `{details['selected_end_date']}`")
            if details.get("effective_end_date"):
                st.markdown(f"- `Effective Trading End`: `{details['effective_end_date']}`")
            if details.get("stale_count", 0) > 0:
                st.markdown(f"- `Stale Symbols`: `{details['stale_count']}`")
                if details.get("stale_symbols"):
                    st.caption("First stale symbols:")
                    st.code(", ".join(details["stale_symbols"]))
            if details.get("missing_count", 0) > 0:
                st.markdown(f"- `Missing Symbols`: `{details['missing_count']}`")
                if details.get("missing_symbols"):
                    st.caption("First missing symbols:")
                    st.code(", ".join(details["missing_symbols"]))
            reason_counts = details.get("reason_counts") or {}
            classification_rows = details.get("classification_rows") or []
            if reason_counts:
                st.markdown("**Heuristic Reason Summary**")
                reason_df = pd.DataFrame(
                    [{"Reason": reason, "Count": count} for reason, count in reason_counts.items()]
                ).sort_values(["Count", "Reason"], ascending=[False, True])
                st.dataframe(reason_df, use_container_width=True, hide_index=True)
            if classification_rows:
                st.markdown("**Stale / Missing Classification**")
                st.caption(
                    "These labels are heuristic. They help us distinguish likely delisting/symbol issues from ordinary lagging price coverage, but they are not a formal delisting confirmation."
                )
                classification_df = pd.DataFrame(classification_rows).rename(
                    columns={
                        "symbol": "Symbol",
                        "latest_date": "Latest Date",
                        "lag_days": "Lag Days",
                        "profile_status": "Profile Status",
                        "reason": "Reason",
                        "note": "Note",
                    }
                )
                st.dataframe(classification_df, use_container_width=True, hide_index=True)
            st.caption(
                "If this check is yellow, run `Daily Market Update` for the lagging symbols first. "
                "That usually prevents duplicate or shifted final-month rows in large-universe strict statement runs."
            )
            st.caption(
                "If you need to distinguish DB ingestion gaps from provider/source gaps or likely delisting, "
                "use `Ingestion > Manual Jobs / Inspection > Price Stale Diagnosis`."
            )
            payload = _build_daily_market_update_refresh_payload(details)
            if payload is not None:
                st.markdown("**Daily Market Update Refresh Payload**")
                left, right = st.columns(2)
                left.metric("Refresh Symbols", f"{len(details.get('refresh_symbols_all') or [])}")
                right.metric("Suggested Window", f"{payload['start']} -> {payload['end']}")
                st.caption(
                    "Use this payload in `Daily Market Update` when the strict annual preflight is yellow. "
                    "It targets only the lagging or missing symbols instead of re-running the whole universe."
                )
                st.code(payload["payload_block"])
                st.text_area(
                    "Refresh Symbols CSV",
                    value=payload["symbols_csv"],
                    height=120,
                    key=f"strict_refresh_symbols_{strategy_label}",
                )

def _strategy_key_to_display_name(strategy_key: str | None) -> str | None:
    return catalog_strategy_key_to_display_name(strategy_key)

def _family_strategy_summary_label(strategy_key: str | None) -> str | None:
    family_name, variant_name = strategy_key_to_selection(strategy_key)
    if family_name is None:
        return None
    if variant_name:
        return f"{family_name} / {variant_name}"
    return family_name

def _single_family_variant_session_key(strategy_choice: str) -> str | None:
    return SINGLE_FAMILY_VARIANT_SESSION_KEYS.get(strategy_choice)

def _compare_family_variant_session_key(strategy_choice: str) -> str | None:
    return COMPARE_FAMILY_VARIANT_SESSION_KEYS.get(strategy_choice)

def _strategy_capability_rows(strategy_name: str | None) -> list[dict[str, str]]:
    name = str(strategy_name or "").strip()
    if not name:
        return []

    common_history = "History / Load Into Form / Run Again 지원"
    if name.endswith("(Strict Annual)"):
        return [
            {
                "확인 영역": "Cadence / 데이터",
                "현재 상태": "Annual statement shadow factor 기반 strict family",
                "확인 포인트": "연간 재무제표 cadence를 쓰며, monthly rebalance로 실행합니다.",
            },
            {
                "확인 영역": "Data Trust",
                "현재 상태": "Price Freshness Preflight + Data Trust Summary 지원",
                "확인 포인트": "결과 상단에서 실제 결과 기간과 가격 최신성을 확인합니다.",
            },
            {
                "확인 영역": "선택 기록",
                "현재 상태": "Selection History / Interpretation 지원",
                "확인 포인트": "선택 종목, trend rejection, risk-off, weighting 해석을 볼 수 있습니다.",
            },
            {
                "확인 영역": "Real-Money / Guardrail",
                "현재 상태": "가장 성숙한 기준 surface",
                "확인 포인트": "Benchmark, liquidity, validation, underperformance/drawdown guardrail을 함께 봅니다.",
            },
            {
                "확인 영역": "저장 / 재실행",
                "현재 상태": common_history,
                "확인 포인트": "입력값과 contract 값이 history / replay에서 복원되어야 합니다.",
            },
        ]

    if name.endswith("(Strict Quarterly Prototype)"):
        return [
            {
                "확인 영역": "Cadence / 데이터",
                "현재 상태": "Quarterly statement shadow factor 기반 prototype",
                "확인 포인트": "분기 재무제표 cadence를 쓰지만, 아직 annual strict와 같은 성숙도로 보지 않습니다.",
            },
            {
                "확인 영역": "Data Trust",
                "현재 상태": "Price Freshness Preflight + Data Trust Summary 지원",
                "확인 포인트": "분기 factor coverage와 실제 결과 기간을 annual과 같은 방식으로 확인합니다.",
            },
            {
                "확인 영역": "선택 기록",
                "현재 상태": "Selection History / Interpretation 지원",
                "확인 포인트": "quarterly 선택 기록이 annual처럼 잘못 읽히지 않는지 봅니다.",
            },
            {
                "확인 영역": "Portfolio Handling",
                "현재 상태": "Weighting / Rejected Slot / Risk-Off contract 지원",
                "확인 포인트": "단, Real-Money promotion / Guardrail 판단은 아직 annual strict 중심입니다.",
            },
            {
                "확인 영역": "저장 / 재실행",
                "현재 상태": common_history,
                "확인 포인트": "quarterly cadence와 contract 값이 load / replay에서 유지되어야 합니다.",
            },
        ]

    if name == "Global Relative Strength":
        return [
            {
                "확인 영역": "Cadence / 데이터",
                "현재 상태": "Price-only ETF relative strength family",
                "확인 포인트": "재무제표 factor가 아니라 ETF 가격, 상대강도, trend filter를 사용합니다.",
            },
            {
                "확인 영역": "Data Trust",
                "현재 상태": "Price Freshness Preflight + Data Trust Summary 지원",
                "확인 포인트": "Phase 27 기준으로 stale / missing ETF 가격을 먼저 확인합니다.",
            },
            {
                "확인 영역": "선택 기록",
                "현재 상태": "Snapshot Selection History 대상은 아님",
                "확인 포인트": "행별 factor 선택표가 아니라 ETF ranking / result table 중심으로 봅니다.",
            },
            {
                "확인 영역": "Real-Money / Guardrail",
                "현재 상태": "ETF operability + cost/benchmark first pass 지원",
                "확인 포인트": "AUM/spread/cost/benchmark는 보지만, ETF underperformance/drawdown guardrail은 아직 붙이지 않습니다.",
            },
            {
                "확인 영역": "저장 / 재실행",
                "현재 상태": common_history,
                "확인 포인트": "cash ticker, score horizon, score weight, trend window가 복원되어야 합니다.",
            },
        ]

    if name == "GTAA":
        return [
            {
                "확인 영역": "Cadence / 데이터",
                "현재 상태": "Price-only tactical ETF family",
                "확인 포인트": "ETF 가격과 score / risk-off overlay를 중심으로 실행합니다.",
            },
            {
                "확인 영역": "Data Trust",
                "현재 상태": "Result window summary 지원, dedicated price freshness surface는 확장 후보",
                "확인 포인트": "Phase 28에서 GRS 수준의 freshness surface가 필요한지 봅니다.",
            },
            {
                "확인 영역": "Real-Money / Guardrail",
                "현재 상태": "ETF Real-Money + ETF Guardrail surface 지원",
                "확인 포인트": "risk-off overlay와 crash / ETF guardrail을 함께 확인합니다.",
            },
            {
                "확인 영역": "저장 / 재실행",
                "현재 상태": common_history,
                "확인 포인트": "score weights, risk-off, defensive tickers, guardrail 값이 복원되어야 합니다.",
            },
        ]

    if name in {"Risk Parity Trend", "Dual Momentum"}:
        return [
            {
                "확인 영역": "Cadence / 데이터",
                "현재 상태": "Price-only ETF strategy",
                "확인 포인트": "재무제표 cadence가 아니라 ETF 가격 기반 전략입니다.",
            },
            {
                "확인 영역": "Data Trust",
                "현재 상태": "Result window summary 지원, dedicated price freshness surface는 확장 후보",
                "확인 포인트": "Phase 28에서 GRS 수준으로 맞출 필요가 있는지 확인합니다.",
            },
            {
                "확인 영역": "Real-Money / Guardrail",
                "현재 상태": "ETF Real-Money + ETF Guardrail surface 지원",
                "확인 포인트": "ETF operability와 guardrail 정책을 함께 봅니다.",
            },
            {
                "확인 영역": "저장 / 재실행",
                "현재 상태": common_history,
                "확인 포인트": "전략별 핵심 입력값이 history / replay에서 복원되어야 합니다.",
            },
        ]

    if name == "Equal Weight":
        return [
            {
                "확인 영역": "Cadence / 데이터",
                "현재 상태": "Price-only baseline strategy",
                "확인 포인트": "전략 후보가 아니라 비교 기준 또는 단순 포트폴리오 baseline으로 봅니다.",
            },
            {
                "확인 영역": "Data Trust",
                "현재 상태": "Result window summary 지원",
                "확인 포인트": "별도 price freshness preflight는 아직 없습니다.",
            },
            {
                "확인 영역": "Real-Money / Guardrail",
                "현재 상태": "promotion / guardrail 판단 대상 아님",
                "확인 포인트": "실전 후보 판정이 아니라 기준선 역할입니다.",
            },
            {
                "확인 영역": "저장 / 재실행",
                "현재 상태": common_history,
                "확인 포인트": "ticker와 rebalance interval이 복원되어야 합니다.",
            },
        ]

    return [
        {
            "확인 영역": "지원 범위",
            "현재 상태": "개별 전략 설정을 확인해야 함",
            "확인 포인트": "Phase 28 parity map에 아직 명시되지 않은 전략입니다.",
        }
    ]

def _render_strategy_capability_snapshot(strategy_name: str | None) -> None:
    rows = _strategy_capability_rows(strategy_name)
    if not rows:
        return

    with st.expander("Strategy Capability Snapshot", expanded=False):
        st.caption(
            "Phase 28 기준으로 이 전략이 어떤 cadence, data trust, Real-Money/Guardrail, "
            "history/replay 지원 범위를 갖는지 빠르게 확인하는 표입니다."
        )
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

def _set_single_strategy_target_from_strategy_key(strategy_key: str | None) -> None:
    strategy_choice, strategy_variant = strategy_key_to_selection(strategy_key)
    if strategy_choice is None:
        return

    st.session_state.backtest_prefill_strategy_choice = strategy_choice
    st.session_state.backtest_prefill_strategy_variant = strategy_variant

def _resolve_guardrail_reference_ticker_value(data: dict[str, Any] | None) -> str | None:
    data = dict(data or {})
    ticker = str(
        data.get("guardrail_reference_ticker")
        or data.get("benchmark_ticker")
        or ""
    ).strip().upper()
    return ticker or None

def _raw_guardrail_reference_ticker_value(data: dict[str, Any] | None) -> str | None:
    data = dict(data or {})
    ticker = str(data.get("guardrail_reference_ticker") or "").strip().upper()
    return ticker or None

def _guardrail_reference_display_value(data: dict[str, Any] | None) -> str:
    raw_ticker = _raw_guardrail_reference_ticker_value(data)
    if raw_ticker:
        return raw_ticker
    benchmark_ticker = str(dict(data or {}).get("benchmark_ticker") or "").strip().upper()
    if benchmark_ticker:
        return "Same as Benchmark Ticker"
    return "-"

def _compare_summary_benchmark_ticker_value(data: dict[str, Any] | None) -> str:
    data = dict(data or {})
    if data.get("benchmark_contract") == STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT:
        return ""
    return str(data.get("benchmark_ticker") or "").strip().upper()

def _compare_summary_guardrail_reference_value(data: dict[str, Any] | None) -> str:
    data = dict(data or {})
    guardrail_used = bool(data.get("underperformance_guardrail_enabled") or data.get("drawdown_guardrail_enabled"))
    if not guardrail_used:
        return ""
    raw_ticker = _raw_guardrail_reference_ticker_value(data)
    if raw_ticker:
        return raw_ticker
    benchmark_ticker = str(data.get("benchmark_ticker") or "").strip().upper()
    if benchmark_ticker:
        return "Same as Benchmark Ticker"
    return ""

def _build_prefill_summary_lines(payload: dict[str, Any] | None) -> list[str]:
    if not payload:
        return []

    lines: list[str] = []
    strategy_key = payload.get("strategy_key")
    strategy_name = _strategy_key_to_display_name(strategy_key)
    strategy_summary_label = _family_strategy_summary_label(strategy_key)
    if strategy_summary_label:
        lines.append(f"전략: `{strategy_summary_label}`")
    elif strategy_name:
        lines.append(f"전략: `{strategy_name}`")

    start = payload.get("start")
    end = payload.get("end")
    if start or end:
        lines.append(f"기간: `{start or '-'} -> {end or '-'}`")

    preset_name = payload.get("preset_name")
    tickers = payload.get("tickers") or []
    universe_mode = payload.get("universe_mode")
    if universe_mode == "preset" and preset_name:
        lines.append(f"모집군: preset `{preset_name}`")
    elif tickers:
        lines.append(f"모집군: 수동 ticker `{','.join(tickers[:10])}`")

    if payload.get("top") is not None:
        lines.append(f"Top N: `{payload.get('top')}`")
    if payload.get("min_price_filter") is not None:
        lines.append(f"Minimum Price: `{payload.get('min_price_filter')}`")
    if payload.get("min_history_months_filter") is not None:
        lines.append(f"Minimum History: `{payload.get('min_history_months_filter')}M`")
    if payload.get("min_avg_dollar_volume_20d_m_filter") is not None:
        lines.append(f"Min Avg Dollar Volume 20D: `{payload.get('min_avg_dollar_volume_20d_m_filter')}M`")
    if payload.get("transaction_cost_bps") is not None:
        lines.append(f"Transaction Cost: `{payload.get('transaction_cost_bps')}` bps")
    if payload.get("promotion_min_etf_aum_b") is not None:
        lines.append(f"Min ETF AUM: `${float(payload.get('promotion_min_etf_aum_b')):.1f}B`")
    if payload.get("promotion_max_bid_ask_spread_pct") is not None:
        lines.append(
            f"Max Bid-Ask Spread: `{float(payload.get('promotion_max_bid_ask_spread_pct')):.2%}`"
        )
    if payload.get("benchmark_contract"):
        lines.append(f"Benchmark Contract: `{_benchmark_contract_value_to_label(payload.get('benchmark_contract'))}`")
    if payload.get("benchmark_ticker"):
        lines.append(f"Benchmark Ticker: `{payload.get('benchmark_ticker')}`")
    if payload.get("cash_ticker"):
        lines.append(f"Cash / Defensive Ticker: `{payload.get('cash_ticker')}`")
    guardrail_reference_ticker = _raw_guardrail_reference_ticker_value(payload)
    if guardrail_reference_ticker:
        lines.append(f"Guardrail / Reference Ticker: `{guardrail_reference_ticker}`")
    elif payload.get("benchmark_ticker"):
        lines.append("Guardrail / Reference Ticker: `Same as Benchmark Ticker`")
    if payload.get("promotion_min_benchmark_coverage") is not None:
        lines.append(
            f"Min Benchmark Coverage: `{float(payload.get('promotion_min_benchmark_coverage')):.0%}`"
        )
    if payload.get("promotion_min_net_cagr_spread") is not None:
        lines.append(
            f"Min Net CAGR Spread: `{float(payload.get('promotion_min_net_cagr_spread')):.0%}`"
        )
    if payload.get("promotion_min_liquidity_clean_coverage") is not None:
        lines.append(
            f"Min Liquidity Clean Coverage: `{float(payload.get('promotion_min_liquidity_clean_coverage')):.0%}`"
        )
    if payload.get("promotion_max_underperformance_share") is not None:
        lines.append(
            f"Max Underperformance Share: `{float(payload.get('promotion_max_underperformance_share')):.0%}`"
        )
    if payload.get("promotion_min_worst_rolling_excess_return") is not None:
        lines.append(
            f"Min Worst Rolling Excess: `{float(payload.get('promotion_min_worst_rolling_excess_return')):.0%}`"
        )
    if payload.get("promotion_max_strategy_drawdown") is not None:
        lines.append(
            f"Max Strategy Drawdown: `{float(payload.get('promotion_max_strategy_drawdown')):.0%}`"
        )
    if payload.get("promotion_max_drawdown_gap_vs_benchmark") is not None:
        lines.append(
            f"Max Drawdown Gap: `{float(payload.get('promotion_max_drawdown_gap_vs_benchmark')):.0%}`"
        )
    if payload.get("underperformance_guardrail_enabled"):
        lines.append(
            "Underperformance Guardrail: "
            f"`{payload.get('underperformance_guardrail_window_months', STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS)}M`, "
            f"`{float(payload.get('underperformance_guardrail_threshold', STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD)):.0%}`"
        )
    if payload.get("drawdown_guardrail_enabled"):
        lines.append(
            "Drawdown Guardrail: "
            f"`{payload.get('drawdown_guardrail_window_months', STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS)}M`, "
            f"`{float(payload.get('drawdown_guardrail_strategy_threshold', STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD)):.0%}`, "
            f"`gap {float(payload.get('drawdown_guardrail_gap_threshold', STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD)):.0%}`"
        )
    if payload.get("score_lookback_months"):
        selected_horizons = [f"{int(months)}M" for months in list(payload.get("score_lookback_months") or [])]
        lines.append(f"Score Horizons: `{', '.join(selected_horizons)}`")
    elif payload.get("score_return_columns"):
        label_map = dict(GTAA_SCORE_WEIGHT_LABELS)
        selected_horizons = [label_map.get(col, col) for col in list(payload.get("score_return_columns") or [])]
        lines.append(f"Score Horizons: `{', '.join(selected_horizons)}`")

    contract = payload.get("universe_contract")
    if contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        lines.append("Universe Contract: `Historical Dynamic PIT Universe`")
    elif contract == STATIC_MANAGED_RESEARCH_UNIVERSE:
        lines.append("Universe Contract: `Static Managed Research Universe`")

    factor_freq = payload.get("factor_freq")
    snapshot_mode = payload.get("snapshot_mode")
    if factor_freq or snapshot_mode:
        lines.append(
            "설정: "
            f"`factor_freq={factor_freq or '-'}`, `snapshot_mode={snapshot_mode or '-'}`"
        )

    return lines

def _universe_contract_value_to_label(value: str | None) -> str:
    for label, contract_value in STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.items():
        if contract_value == value:
            return label
    return "Static Managed Research Universe"

def _benchmark_contract_value_to_label(value: str | None) -> str:
    for label, contract_value in STRICT_BENCHMARK_CONTRACT_LABELS.items():
        if contract_value == value:
            return label
    return "Ticker Benchmark"

def _shortlist_status_value_to_label(value: str | None) -> str:
    mapping = {
        "watchlist": "Watchlist",
        "paper_probation": "Paper Probation",
        "small_capital_trial": "Small Capital Trial",
        "hold": "Hold",
    }
    return mapping.get(str(value or "").strip().lower(), "-")

def _probation_status_value_to_label(value: str | None) -> str:
    mapping = {
        "not_ready": "Not Ready",
        "watchlist_review": "Watchlist Review",
        "paper_tracking": "Paper Tracking",
        "small_capital_live_trial": "Small Capital Trial",
    }
    return mapping.get(str(value or "").strip().lower(), "-")

def _monitoring_status_value_to_label(value: str | None) -> str:
    mapping = {
        "blocked": "Blocked",
        "routine_review": "Routine Review",
        "heightened_review": "Heightened Review",
        "breach_watch": "Breach Watch",
    }
    return mapping.get(str(value or "").strip().lower(), "-")

def _review_status_value_to_label(value: str | None) -> str:
    mapping = {
        "normal": "Normal",
        "watch": "Watch",
        "caution": "Caution",
        "unavailable": "Unavailable",
    }
    return mapping.get(str(value or "").strip().lower(), "-")

def _deployment_readiness_status_value_to_label(value: str | None) -> str:
    mapping = {
        "blocked": "Blocked",
        "review_required": "Review Required",
        "watchlist_only": "Watchlist Only",
        "paper_only": "Paper Only",
        "small_capital_ready": "Small Capital Ready",
        "small_capital_ready_with_review": "Small Capital Ready (Review)",
    }
    return mapping.get(str(value or "").strip().lower(), "-")

def _liquidity_policy_signal_to_korean_label(value: str | None) -> str:
    mapping = {
        "liquidity_filter_disabled": "유동성 필터가 꺼져 있음",
        "liquidity_coverage_missing": "유동성 coverage 계산 데이터 없음",
        "liquidity_clean_coverage_below_policy": "리밸런싱 시점 clean coverage가 기준보다 낮음",
    }
    key = str(value or "").strip().lower()
    return mapping.get(key, key or "-")

def _issue_status_to_korean_label(value: str | None) -> str:
    mapping = {
        "watch": "Watch",
        "caution": "Caution",
        "unavailable": "Unavailable",
        "warning": "Warning",
        "error": "Error",
        "missing": "Missing",
    }
    key = str(value or "").strip().lower()
    return mapping.get(key, key or "-")

def _issue_status_meaning(item_label: str, status: str) -> str:
    normalized = str(status or "").strip().lower()
    if normalized == "watch":
        return f"{item_label}에 주의 신호가 있어 추가 검토가 권장되는 상태입니다."
    if normalized == "caution":
        return f"{item_label}가 현재 승격 판단을 직접 막고 있는 강한 경고 상태입니다."
    if normalized == "unavailable":
        return f"{item_label}를 판단할 데이터나 계약이 부족해 승격 해석을 할 수 없는 상태입니다."
    if normalized == "warning":
        return f"{item_label}에 경고가 있어 보수적으로 해석해야 하는 상태입니다."
    if normalized == "error":
        return f"{item_label} 관련 데이터나 계산에 오류가 있어 현재 상태로는 신뢰하기 어렵습니다."
    if normalized == "missing":
        return f"{item_label}가 연결되지 않아 비교나 정책 판단을 할 수 없는 상태입니다."
    return "상태 의미를 확인하려면 관련 섹션의 상세 값을 함께 보는 편이 좋습니다."

def _build_stage_issue_resolution_rows(meta: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    def add_row(
        item_label: str,
        status: str | None,
        location: str,
        action: str,
    ) -> None:
        normalized = str(status or "").strip().lower()
        if normalized not in {"watch", "caution", "unavailable", "warning", "error", "missing"}:
            return
        rows.append(
            {
                "항목": item_label,
                "현재 상태": _issue_status_to_korean_label(normalized),
                "상태를 보는 위치": location,
                "이 상태의 뜻": _issue_status_meaning(item_label, normalized),
                "바로 해볼 일": action,
            }
        )

    benchmark_available = bool(meta.get("benchmark_available"))
    if not benchmark_available:
        add_row(
            "Benchmark 비교",
            "missing",
            "검토 근거 > Benchmark / Validation 요약",
            "Benchmark Contract와 Benchmark Ticker를 먼저 연결하고 benchmark curve가 실제로 생성되는지 다시 실행합니다.",
        )

    add_row(
        "Validation",
        meta.get("validation_status"),
        "검토 근거 > Validation Surface",
        "Underperformance Share, Worst Rolling Excess, Drawdown 지표를 확인하고 benchmark 또는 전략 계약을 다시 검토합니다.",
    )
    add_row(
        "Benchmark Policy",
        meta.get("benchmark_policy_status"),
        "검토 근거 > 세부 정책 기준 보기 > Benchmark Policy",
        "Coverage와 Net CAGR Spread를 확인하고 benchmark contract, benchmark ticker, 기간을 다시 점검합니다.",
    )
    add_row(
        "Liquidity Policy",
        meta.get("liquidity_policy_status"),
        "실행 부담 > Liquidity Policy",
        "Min Avg Dollar Volume 20D, Clean Coverage, Liquidity Excluded Rows를 보고 유동성 필터나 후보군을 조정합니다.",
    )
    add_row(
        "Validation Policy",
        meta.get("validation_policy_status"),
        "검토 근거 > 세부 정책 기준 보기 > Validation Policy",
        "Max Underperformance Share, Min Worst Excess, Actual 값을 비교해 robustness 계약을 다시 확인합니다.",
    )
    add_row(
        "Portfolio Guardrail Policy",
        meta.get("guardrail_policy_status"),
        "검토 근거 > 세부 정책 기준 보기 > Portfolio Guardrail Policy",
        "Strategy Max Drawdown과 Drawdown Gap이 기준을 넘는지 확인하고 낙폭 계약을 더 보수적으로 검토합니다.",
    )
    add_row(
        "ETF Operability",
        meta.get("etf_operability_status"),
        "실행 부담 > ETF 운용 가능성",
        "AUM, bid-ask spread, 누락 프로필 데이터를 확인하고 문제가 큰 ETF는 교체하거나 metadata를 보강합니다.",
    )

    freshness_status = str((meta.get("price_freshness") or {}).get("status") or "").strip().lower()
    add_row(
        "Price Freshness",
        freshness_status,
        "결과 상단 안내 / Execution Context",
        "Daily Market Update 또는 targeted refresh로 최신 가격을 다시 채우고 재실행합니다.",
    )
    return rows

def _build_hold_resolution_guidance_rows(meta: dict[str, Any]) -> list[dict[str, str]]:
    guidance_specs = {
        "benchmark_unavailable": {
            "막히는 항목": "벤치마크 비교 없음",
            "먼저 볼 위치": "검토 근거 > Benchmark / Validation 요약",
            "권장 조치": "Benchmark Contract와 Benchmark Ticker를 설정하고 benchmark curve가 실제로 생성되는지 다시 실행합니다.",
        },
        "validation_caution": {
            "막히는 항목": "검증 상태가 caution",
            "먼저 볼 위치": "검토 근거 > Validation Surface",
            "권장 조치": "Underperformance Share, Worst Rolling Excess, Drawdown 지표를 확인하고 benchmark 또는 전략 계약을 다시 검토합니다.",
        },
        "benchmark_policy_caution": {
            "막히는 항목": "벤치마크 정책 미통과",
            "먼저 볼 위치": "검토 근거 > 세부 정책 기준 보기 > Benchmark Policy",
            "권장 조치": "Benchmark Coverage와 Net CAGR Spread가 기준을 넘는지 확인하고 benchmark contract 또는 기간을 조정합니다.",
        },
        "benchmark_policy_unavailable": {
            "막히는 항목": "벤치마크 정책 판단 불가",
            "먼저 볼 위치": "검토 근거 > 세부 정책 기준 보기 > Benchmark Policy",
            "권장 조치": "usable benchmark history가 충분한지 확인하고, benchmark contract를 먼저 안정적으로 연결합니다.",
        },
        "liquidity_policy_caution": {
            "막히는 항목": "유동성 정책 미통과",
            "먼저 볼 위치": "실행 부담 > Liquidity Policy",
            "권장 조치": "Min Avg Dollar Volume 20D 기준이나 후보군을 조정하고, 거래가 너무 얇은 종목이 자주 제외되는지 확인합니다.",
        },
        "liquidity_policy_unavailable": {
            "막히는 항목": "유동성 정책 판단 불가",
            "먼저 볼 위치": "실행 부담 > Liquidity Policy",
            "권장 조치": "유동성 필터를 켜고 usable liquidity history가 있는지 확인한 뒤 다시 실행합니다.",
        },
        "validation_policy_caution": {
            "막히는 항목": "승격 검증 정책 미통과",
            "먼저 볼 위치": "검토 근거 > 세부 정책 기준 보기 > Validation Policy",
            "권장 조치": "Max Underperformance Share와 Min Worst Rolling Excess 기준을 확인하고 robustness를 다시 검토합니다.",
        },
        "validation_policy_unavailable": {
            "막히는 항목": "승격 검증 정책 판단 불가",
            "먼저 볼 위치": "검토 근거 > 세부 정책 기준 보기 > Validation Policy",
            "권장 조치": "aligned benchmark validation history가 충분한지 확인하고 benchmark/기간 계약을 다시 점검합니다.",
        },
        "guardrail_policy_caution": {
            "막히는 항목": "가드레일 정책 미통과",
            "먼저 볼 위치": "검토 근거 > 세부 정책 기준 보기 > Portfolio Guardrail Policy",
            "권장 조치": "Strategy Max Drawdown과 Drawdown Gap이 기준을 넘는지 확인하고 drawdown contract를 더 보수적으로 재검토합니다.",
        },
        "guardrail_policy_unavailable": {
            "막히는 항목": "가드레일 정책 판단 불가",
            "먼저 볼 위치": "검토 근거 > 세부 정책 기준 보기 > Portfolio Guardrail Policy",
            "권장 조치": "usable benchmark drawdown history가 있는지 확인하고 guardrail 계산에 필요한 benchmark 연결을 먼저 안정화합니다.",
        },
        "etf_operability_caution": {
            "막히는 항목": "ETF 운용 가능성 이슈",
            "먼저 볼 위치": "실행 부담 > ETF Operability",
            "권장 조치": "ETF AUM, bid-ask spread, asset profile freshness를 확인하고 운용이 불리한 ETF는 교체를 검토합니다.",
        },
        "etf_operability_unavailable": {
            "막히는 항목": "ETF 운용 가능성 판단 불가",
            "먼저 볼 위치": "실행 부담 > ETF Operability",
            "권장 조치": "ETF asset profile과 spread/AUM 데이터가 충분한지 확인하고 operability metadata를 먼저 안정화합니다.",
        },
        "price_freshness_error": {
            "막히는 항목": "가격 데이터 최신성 오류",
            "먼저 볼 위치": "결과 상단 안내 / Execution Context",
            "권장 조치": "Daily Market Update 또는 targeted refresh를 실행한 뒤 다시 백테스트합니다.",
        },
    }

    rows: list[dict[str, str]] = []
    seen_blockers: set[str] = set()
    for rationale_code in list(meta.get("promotion_rationale") or []):
        spec = guidance_specs.get(str(rationale_code or "").strip())
        if not spec:
            continue
        blocker = spec["막히는 항목"]
        if blocker in seen_blockers:
            continue
        rows.append(spec)
        seen_blockers.add(blocker)

    richer_rows = _build_stage_issue_resolution_rows(meta)
    if richer_rows:
        return richer_rows

    if not rows and str(meta.get("promotion_next_step") or "").strip() == "resolve_validation_gaps_before_promotion":
        rows.append(
            {
                "막히는 항목": "승격 검증 기준 미통과",
                "먼저 볼 위치": "검토 근거 / 실행 부담",
                "권장 조치": "Validation, Benchmark, Liquidity, Guardrail 섹션 중 `caution` 또는 `unavailable` 항목부터 먼저 확인합니다.",
            }
        )

    return rows

def _should_show_guardrail_surface(meta: dict[str, Any]) -> bool:
    strategy_key = str(meta.get("strategy_key") or "").strip().lower()
    if strategy_key in ETF_GUARDRAIL_STRATEGY_KEYS:
        return True
    return (
        meta.get("underperformance_guardrail_enabled") is not None
        or meta.get("drawdown_guardrail_enabled") is not None
        or meta.get("underperformance_guardrail_trigger_count") is not None
        or meta.get("drawdown_guardrail_trigger_count") is not None
    )

__all__ = [name for name in globals() if not name.startswith("__")]
