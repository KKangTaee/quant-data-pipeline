from __future__ import annotations

import json
import time
from datetime import date
from functools import lru_cache
from typing import Any

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from app.web.runtime import (
    BACKTEST_HISTORY_FILE,
    SAVED_PORTFOLIO_FILE,
    append_backtest_run_history,
    build_backtest_result_bundle,
    delete_saved_portfolio,
    inspect_strict_annual_price_freshness,
    load_backtest_run_history,
    load_saved_portfolios,
    run_dual_momentum_backtest_from_db,
    run_equal_weight_backtest_from_db,
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
from finance.sample import (
    GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD,
    GTAA_DEFAULT_CRASH_GUARDRAIL_ENABLED,
    GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS,
    GTAA_DEFAULT_DEFENSIVE_TICKERS,
    GTAA_DEFAULT_SCORE_LOOKBACK_MONTHS,
    GTAA_DEFAULT_RISK_OFF_MODE,
    GTAA_SCORE_RETURN_COLUMNS,
    GTAA_DEFAULT_SCORE_WEIGHTS,
    GTAA_DEFAULT_TREND_FILTER_WINDOW,
    STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
    STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
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

GTAA_RISK_OFF_MODE_LABELS = {
    "Cash Only": "cash_only",
    "Defensive Bond Preference": "defensive_bond_preference",
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
    if "backtest_weighted_portfolio_prefill" not in st.session_state:
        st.session_state.backtest_weighted_portfolio_prefill = None
    if "backtest_saved_portfolio_notice" not in st.session_state:
        st.session_state.backtest_saved_portfolio_notice = None
    if "backtest_active_panel" not in st.session_state:
        st.session_state.backtest_active_panel = "Single Strategy"
    if "backtest_requested_panel" not in st.session_state:
        st.session_state.backtest_requested_panel = None
    requested_panel = st.session_state.get("backtest_requested_panel")
    if requested_panel in {"Single Strategy", "Compare & Portfolio Builder", "History"}:
        st.session_state.backtest_active_panel = requested_panel
        st.session_state.backtest_requested_panel = None
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
    if "qss_trend_filter_enabled" not in st.session_state:
        st.session_state["qss_trend_filter_enabled"] = STRICT_TREND_FILTER_DEFAULT_ENABLED
    if "qss_trend_filter_window" not in st.session_state:
        st.session_state["qss_trend_filter_window"] = STRICT_TREND_FILTER_DEFAULT_WINDOW
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
    if preset_name in STRICT_ANNUAL_MANAGED_PRESET_SPECS and "US Statement Coverage 1000" in QUALITY_STRICT_PRESETS:
        candidate_tickers = QUALITY_STRICT_PRESETS["US Statement Coverage 1000"]
    else:
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
            "Phase 10 first pass dynamic PIT mode입니다. 현재 managed candidate pool 안에서 "
            f"각 리밸런싱 날짜 기준 `price * latest-known {freq_label} shares_outstanding`로 top-N 모집군을 다시 구성합니다."
        )
        st.caption(
            f"Dynamic candidate pool: `{len(dynamic_candidate_tickers)}` symbols | "
            f"target membership: `{dynamic_target_size}` | "
            f"현재는 `{freq_label}` strict family first pass, approximate PIT market-cap mode입니다."
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


def _summarize_params(meta: dict[str, Any]) -> str:
    parts = []
    if meta.get("universe_contract"):
        parts.append(f"universe_contract={meta['universe_contract']}")
    if meta.get("timeframe"):
        parts.append(f"timeframe={meta['timeframe']}")
    if meta.get("option"):
        parts.append(f"option={meta['option']}")
    if meta.get("factor_freq"):
        parts.append(f"factor_freq={meta['factor_freq']}")
    if meta.get("snapshot_mode"):
        parts.append(f"snapshot_mode={meta['snapshot_mode']}")
    if meta.get("snapshot_source"):
        parts.append(f"snapshot_source={meta['snapshot_source']}")
    if meta.get("rebalance_interval") is not None:
        parts.append(f"rebalance_interval={meta['rebalance_interval']}")
    if meta.get("top") is not None:
        parts.append(f"top={meta['top']}")
    if meta.get("vol_window") is not None:
        parts.append(f"vol_window={meta['vol_window']}")
    if meta.get("quality_factors"):
        parts.append(f"quality_factors={','.join(meta['quality_factors'])}")
    if meta.get("value_factors"):
        parts.append(f"value_factors={','.join(meta['value_factors'])}")
    if meta.get("trend_filter_enabled"):
        parts.append("trend_filter=on")
        parts.append(f"trend_window={meta.get('trend_filter_window') or STRICT_TREND_FILTER_DEFAULT_WINDOW}")
    if meta.get("market_regime_enabled"):
        parts.append("market_regime=on")
        parts.append(f"regime_benchmark={meta.get('market_regime_benchmark') or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK}")
        parts.append(f"regime_window={meta.get('market_regime_window') or STRICT_MARKET_REGIME_DEFAULT_WINDOW}")
    if meta.get("min_avg_dollar_volume_20d_m_filter") is not None:
        parts.append(f"min_adv20d_m={float(meta.get('min_avg_dollar_volume_20d_m_filter') or 0.0):.1f}")
    if meta.get("benchmark_contract"):
        parts.append(f"benchmark_contract={meta.get('benchmark_contract')}")
    if meta.get("promotion_min_benchmark_coverage") is not None:
        parts.append(f"min_benchmark_coverage={float(meta.get('promotion_min_benchmark_coverage') or 0.0):.0%}")
    if meta.get("promotion_min_net_cagr_spread") is not None:
        parts.append(f"min_net_cagr_spread={float(meta.get('promotion_min_net_cagr_spread') or 0.0):.0%}")
    if meta.get("promotion_min_liquidity_clean_coverage") is not None:
        parts.append(f"min_liquidity_clean_coverage={float(meta.get('promotion_min_liquidity_clean_coverage') or 0.0):.0%}")
    if meta.get("promotion_max_underperformance_share") is not None:
        parts.append(f"max_underperf_share={float(meta.get('promotion_max_underperformance_share') or 0.0):.0%}")
    if meta.get("promotion_min_worst_rolling_excess_return") is not None:
        parts.append(
            f"min_worst_rolling_excess={float(meta.get('promotion_min_worst_rolling_excess_return') or 0.0):.0%}"
        )
    if meta.get("promotion_max_strategy_drawdown") is not None:
        parts.append(f"max_strategy_drawdown={float(meta.get('promotion_max_strategy_drawdown') or 0.0):.0%}")
    if meta.get("promotion_max_drawdown_gap_vs_benchmark") is not None:
        parts.append(
            f"max_drawdown_gap={float(meta.get('promotion_max_drawdown_gap_vs_benchmark') or 0.0):.0%}"
        )
    return ", ".join(parts)


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


def _render_trend_filter_help_popover() -> None:
    _render_inline_help_popover(
        "추세 필터 오버레이",
        "월말 리밸런싱 시점에만 확인하는 1차 버전입니다. 예를 들어 랭킹으로 A와 B가 뽑혔는데, 리밸런싱 당일 A는 200일 이동평균선 아래이고 B는 위에 있으면 A 비중은 현금으로 두고 B만 다음 리밸런싱까지 보유합니다. 일별로 중간 점검하는 구조는 아닙니다.",
    )


def _render_market_regime_help_popover() -> None:
    _render_inline_help_popover(
        "마켓 레짐 오버레이",
        "개별 종목이 아니라 시장 전체 상태를 먼저 보는 상위 오버레이입니다. 1차 버전에서는 월말 리밸런싱 시점에만 지정한 벤치마크(예: SPY)의 종가가 이동평균선 아래인지 확인합니다. Window 200은 보통 200거래일 이동평균선, 즉 장기 추세선을 뜻합니다. 벤치마크가 해당 이동평균선 아래면 그 달 strict factor 포트폴리오는 전부 현금으로 두고, 위에 있으면 기존 팩터 선택 결과를 그대로 집행합니다.",
    )


def _render_interpretation_summary_help_popover() -> None:
    _render_inline_help_popover(
        "해석 요약",
        "Raw Candidate Events는 각 리밸런싱에서 팩터 랭킹으로 최종 후보(top N)까지 올라온 종목 수의 총합입니다. Final Selected Events는 오버레이까지 반영한 뒤 실제 보유 후보로 남은 종목 수의 총합입니다. 이 값들은 전체 모집군 크기를 뜻하지 않습니다. 오버레이가 꺼져 있으면 보통 Raw와 Final이 같고, 오버레이가 켜져 있으면 Raw와 Final의 차이만큼 추가 필터가 개입한 것으로 해석하면 됩니다. Overlay Rejections는 개별 종목 추세 필터로 제외된 횟수 합계이고, Regime Blocked Events / Regime Cash Rebalances는 시장 상태 오버레이 때문에 포트폴리오 전체가 현금으로 이동한 흔적을 요약합니다.",
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
    st.caption(
        "실전형 annual strict contract에서는 `Minimum Price`, `Minimum History (Months)`, "
        "`Minimum Avg Dollar Volume 20D`, `Transaction Cost`, `Benchmark Contract`, `Benchmark Ticker`, "
        "`Benchmark Policy`, `Validation Policy`, `Portfolio Guardrail Policy`를 같이 사용합니다."
    )
    col1, col2, col3, col4, col5, col6 = st.columns(6, gap="small")
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
                help="최근 20거래일 평균 거래대금이 이 값보다 낮은 종목은 해당 날짜 후보에서 제외합니다. 단위는 백만 달러입니다.",
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
            help="Ticker benchmark는 `SPY` 같은 기준 ETF와 직접 비교합니다. Candidate Universe Equal-Weight는 같은 후보군을 단순 균등 보유했을 때와 비교합니다.",
        )
        benchmark_contract = STRICT_BENCHMARK_CONTRACT_LABELS[benchmark_contract_label]
    with col6:
        benchmark_ticker = str(
            st.text_input(
                "Benchmark Ticker",
                value=default_benchmark,
                key=f"{key_prefix}_benchmark_ticker",
                help="Ticker benchmark 또는 underperformance guardrail에서 사용할 기준 ETF ticker입니다. 기본값은 `SPY`입니다.",
            )
        ).strip().upper()

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
            help="리밸런싱 행 중 유동성 제외가 발생하지 않아야 하는 최소 비율입니다.",
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
    if benchmark_contract == STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT:
        st.caption(
            "`Candidate Universe Equal-Weight`는 같은 후보 universe를 단순 균등 보유했을 때와 비교하는 benchmark입니다. "
            "현재 first pass에서는 validation / promotion overlay에 사용되고, actual underperformance guardrail rule은 여전히 `Benchmark Ticker`를 기준으로 동작합니다."
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
                help="rolling window 중 benchmark를 밑돈 비율이 이 값보다 높으면 승격을 보수적으로 봅니다.",
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
                help="rolling excess return 최악 구간이 이 값보다 더 낮으면 승격을 보수적으로 봅니다.",
            )
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
                help="전략의 최대 낙폭이 이 값보다 더 깊으면 승격을 보수적으로 봅니다.",
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
                help="전략의 최대 낙폭이 benchmark보다 이 값 이상 더 나쁘면 승격을 보수적으로 봅니다.",
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


def _risk_off_mode_value_to_label(value: str | None) -> str:
    for label, mode_value in GTAA_RISK_OFF_MODE_LABELS.items():
        if mode_value == value:
            return label
    return "Cash Only"


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


def _render_last_run() -> None:
    error = st.session_state.backtest_last_error
    error_kind = st.session_state.backtest_last_error_kind
    bundle = st.session_state.backtest_last_bundle

    if error:
        if error_kind == "input":
            st.warning(error)
        elif error_kind == "data":
            st.error(error)
            st.caption("Hint: run the ingestion pipeline for the requested tickers and date range, then try again.")
        else:
            st.error(error)

    if not bundle:
        return

    summary_df = bundle["summary_df"]
    chart_df = bundle["chart_df"]
    result_df = bundle["result_df"]
    meta = bundle["meta"]
    warnings = list(meta.get("warnings") or [])

    st.markdown("### Latest Backtest Run")
    strategy_key = meta.get("strategy_key")
    has_selection_history = strategy_key in {
        "quality_snapshot",
        "quality_snapshot_strict_annual",
        "quality_snapshot_strict_quarterly_prototype",
        "value_snapshot_strict_annual",
        "value_snapshot_strict_quarterly_prototype",
        "quality_value_snapshot_strict_annual",
        "quality_value_snapshot_strict_quarterly_prototype",
    }

    dynamic_snapshot_rows = bundle.get("dynamic_universe_snapshot_rows") or []
    dynamic_candidate_status_rows = bundle.get("dynamic_candidate_status_rows") or []
    has_dynamic_details = bool(
        dynamic_snapshot_rows
        or dynamic_candidate_status_rows
        or meta.get("universe_contract") == HISTORICAL_DYNAMIC_PIT_UNIVERSE
    )
    has_real_money_details = bool(meta.get("real_money_hardening"))

    st.info(
        "가장 최근 실행한 백테스트 결과입니다. "
        "먼저 `Summary`에서 핵심 숫자를 보고, `Equity Curve`에서 흐름을 확인한 뒤, "
        "`Real-Money`와 `Meta`에서 실전형 해석과 실행 조건을 읽으면 가장 자연스럽습니다."
    )

    guide_left, guide_right = st.columns([1.4, 1.0], gap="small")
    with guide_left:
        st.markdown("##### 결과 읽는 순서")
        st.markdown(
            "- `Summary`: 수익률과 위험의 핵심 숫자 확인\n"
            "- `Equity Curve`: 전략 흐름과 회복 구간 확인\n"
            "- `Real-Money`: 실전 후보 해석, 검토 근거, 실행 부담 확인\n"
            "- `Meta`: 이번 실행의 계약과 세부 설정 재확인"
        )
    with guide_right:
        st.markdown("##### 이번 실행에 포함된 보기")
        availability_lines = [
            f"- `Selection History`: {'있음' if has_selection_history else '없음'}",
            f"- `Dynamic Universe`: {'있음' if has_dynamic_details else '없음'}",
            f"- `Real-Money`: {'있음' if has_real_money_details else '없음'}",
        ]
        st.markdown("\n".join(availability_lines))

    if warnings:
        warning_lines = "\n".join(f"- {warning}" for warning in warnings)
        st.warning(
            "이번 실행에서 같이 봐야 할 주의 사항이 있습니다.\n\n"
            + warning_lines
        )

    st.markdown(f"#### {bundle['strategy_name']}")
    _render_summary_metrics(summary_df)

    tab_labels = ["Summary", "Equity Curve", "Balance Extremes", "Period Extremes"]
    if has_selection_history:
        tab_labels.append("Selection History")
    if has_dynamic_details:
        tab_labels.append("Dynamic Universe")
    if has_real_money_details:
        tab_labels.append("Real-Money")
    tab_labels.extend(["Result Table", "Meta"])
    tabs = st.tabs(tab_labels)
    tab_iter = iter(tabs)
    summary_tab = next(tab_iter)
    curve_tab = next(tab_iter)
    balance_tab = next(tab_iter)
    periods_tab = next(tab_iter)
    selection_tab = next(tab_iter) if has_selection_history else None
    dynamic_tab = next(tab_iter) if has_dynamic_details else None
    real_money_tab = next(tab_iter) if has_real_money_details else None
    table_tab = next(tab_iter)
    meta_tab = next(tab_iter)

    with summary_tab:
        st.dataframe(summary_df, use_container_width=True)

    with curve_tab:
        _render_balance_chart_with_markers(
            chart_df,
            result_df=result_df,
            title="Equity Curve",
        )
        st.caption(
            "고점 / 저점 / 마지막 지점과 최고 / 최저 기간 마커를 같이 보여줘서, "
            "단순 선 그래프보다 전략 흐름을 더 쉽게 읽을 수 있습니다."
        )

    with balance_tab:
        high_df, low_df = _build_balance_extremes_tables(chart_df, top_n=3)
        high_col, low_col = st.columns(2, gap="large")
        with high_col:
            st.markdown("##### Top 3 Balance Highs")
            st.dataframe(high_df, use_container_width=True, hide_index=True)
        with low_col:
            st.markdown("##### Top 3 Balance Lows")
            st.dataframe(low_df, use_container_width=True, hide_index=True)

    with periods_tab:
        best_df, worst_df = _build_period_extremes_tables(result_df, top_n=3)
        best_col, worst_col = st.columns(2, gap="large")
        with best_col:
            st.markdown("##### Top 3 Best Periods")
            st.dataframe(best_df, use_container_width=True, hide_index=True)
        with worst_col:
            st.markdown("##### Top 3 Worst Periods")
            st.dataframe(worst_df, use_container_width=True, hide_index=True)

    if selection_tab is not None:
        with selection_tab:
            _render_snapshot_selection_history(
                result_df,
                strategy_name=bundle["strategy_name"],
                factor_names=(meta.get("quality_factors") or []) + [
                    name for name in (meta.get("value_factors") or [])
                    if name not in (meta.get("quality_factors") or [])
                ],
                snapshot_mode=meta.get("snapshot_mode"),
                snapshot_source=meta.get("snapshot_source"),
            )

    if dynamic_tab is not None:
        with dynamic_tab:
            _render_dynamic_universe_details(bundle)

    if real_money_tab is not None:
        with real_money_tab:
            _render_real_money_details(bundle)

    with table_tab:
        st.dataframe(result_df, use_container_width=True)

    with meta_tab:
        left, right = st.columns([1.1, 1.2], gap="large")
        with left:
            st.markdown("##### Execution Context")
            st.markdown(f"- `Mode`: `{meta['execution_mode']}`")
            st.markdown(f"- `Data`: `{meta['data_mode']}`")
            st.markdown(f"- `Universe`: `{meta['universe_mode']}`")
            if meta.get("universe_contract"):
                st.markdown(f"- `Universe Contract`: `{meta['universe_contract']}`")
            st.markdown(f"- `Tickers`: `{', '.join(meta['tickers'])}`")
            st.markdown(f"- `Period`: `{meta['start']}` -> `{meta['end']}`")
            if meta.get("ui_elapsed_seconds") is not None:
                st.markdown(f"- `Elapsed`: `{meta['ui_elapsed_seconds']:.3f}s`")
            if meta.get("top") is not None:
                st.markdown(f"- `Top`: `{meta['top']}`")
            if meta.get("min_price_filter") is not None:
                st.markdown(f"- `Minimum Price`: `{float(meta['min_price_filter']):.2f}`")
            if meta.get("min_history_months_filter") is not None:
                st.markdown(f"- `Minimum History`: `{int(meta.get('min_history_months_filter') or 0)}M`")
            if meta.get("min_avg_dollar_volume_20d_m_filter") is not None:
                st.markdown(
                    f"- `Min Avg Dollar Volume 20D`: `{float(meta.get('min_avg_dollar_volume_20d_m_filter') or 0.0):.1f}M`"
                )
                if meta.get("liquidity_excluded_total") is not None:
                    st.markdown(
                        f"- `Liquidity Excluded`: total `{int(meta.get('liquidity_excluded_total') or 0)}`, "
                        f"rows `{int(meta.get('liquidity_excluded_active_rows') or 0)}`"
                    )
                if meta.get("liquidity_clean_coverage") is not None:
                    st.markdown(
                        f"- `Liquidity Clean Coverage`: `{float(meta.get('liquidity_clean_coverage') or 0.0):.2%}`"
                    )
            if meta.get("transaction_cost_bps") is not None:
                st.markdown(f"- `Transaction Cost`: `{float(meta['transaction_cost_bps']):.1f} bps`")
            if meta.get("promotion_min_etf_aum_b") is not None:
                st.markdown(
                    f"- `Min ETF AUM`: `${float(meta.get('promotion_min_etf_aum_b') or 0.0):.1f}B`"
                )
            if meta.get("promotion_max_bid_ask_spread_pct") is not None:
                st.markdown(
                    f"- `Max Bid-Ask Spread`: `{float(meta.get('promotion_max_bid_ask_spread_pct') or 0.0):.2%}`"
                )
            if meta.get("benchmark_contract"):
                st.markdown(
                    f"- `Benchmark Contract`: `{_benchmark_contract_value_to_label(meta.get('benchmark_contract'))}`"
                )
            if meta.get("benchmark_ticker"):
                st.markdown(f"- `Benchmark`: `{meta['benchmark_ticker']}`")
            if meta.get("benchmark_symbol_count") is not None:
                st.markdown(f"- `Benchmark Universe`: `{int(meta.get('benchmark_symbol_count') or 0)}`")
            if meta.get("benchmark_eligible_symbol_count") is not None:
                st.markdown(f"- `Benchmark Eligible`: `{int(meta.get('benchmark_eligible_symbol_count') or 0)}`")
            if meta.get("benchmark_cagr") is not None:
                st.markdown(f"- `Benchmark CAGR`: `{float(meta['benchmark_cagr']):.2%}`")
            if meta.get("net_cagr_spread") is not None:
                st.markdown(f"- `Net CAGR Spread`: `{float(meta['net_cagr_spread']):.2%}`")
            if meta.get("benchmark_row_coverage") is not None:
                st.markdown(f"- `Benchmark Coverage`: `{float(meta['benchmark_row_coverage']):.2%}`")
            if meta.get("promotion_min_benchmark_coverage") is not None:
                st.markdown(
                    f"- `Min Benchmark Coverage`: `{float(meta.get('promotion_min_benchmark_coverage') or 0.0):.0%}`"
                )
            if meta.get("promotion_min_net_cagr_spread") is not None:
                st.markdown(
                    f"- `Min Net CAGR Spread`: `{float(meta.get('promotion_min_net_cagr_spread') or 0.0):.0%}`"
                )
            if meta.get("promotion_min_liquidity_clean_coverage") is not None:
                st.markdown(
                    f"- `Min Liquidity Clean Coverage`: `{float(meta.get('promotion_min_liquidity_clean_coverage') or 0.0):.0%}`"
                )
            if meta.get("promotion_max_underperformance_share") is not None:
                st.markdown(
                    f"- `Max Underperformance Share`: `{float(meta.get('promotion_max_underperformance_share') or 0.0):.0%}`"
                )
            if meta.get("promotion_min_worst_rolling_excess_return") is not None:
                st.markdown(
                    f"- `Min Worst Rolling Excess`: `{float(meta.get('promotion_min_worst_rolling_excess_return') or 0.0):.0%}`"
                )
            if meta.get("promotion_max_strategy_drawdown") is not None:
                st.markdown(
                    f"- `Max Strategy Drawdown`: `{float(meta.get('promotion_max_strategy_drawdown') or 0.0):.0%}`"
                )
            if meta.get("promotion_max_drawdown_gap_vs_benchmark") is not None:
                st.markdown(
                    f"- `Max Drawdown Gap`: `{float(meta.get('promotion_max_drawdown_gap_vs_benchmark') or 0.0):.0%}`"
                )
            if meta.get("etf_operability_status"):
                st.markdown(f"- `ETF Operability Status`: `{meta.get('etf_operability_status')}`")
            if meta.get("underperformance_guardrail_enabled"):
                st.markdown(
                    f"- `Underperformance Guardrail`: `{int(meta.get('underperformance_guardrail_window_months') or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS)}M`, "
                    f"`{float(meta.get('underperformance_guardrail_threshold') or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD):.0%}`"
                )
                if meta.get("underperformance_guardrail_trigger_count") is not None:
                    st.markdown(
                        f"- `Guardrail Trigger Count`: `{int(meta.get('underperformance_guardrail_trigger_count') or 0)}`"
                    )
            if meta.get("drawdown_guardrail_enabled"):
                st.markdown(
                    f"- `Drawdown Guardrail`: `{int(meta.get('drawdown_guardrail_window_months') or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS)}M`, "
                    f"`{float(meta.get('drawdown_guardrail_strategy_threshold') or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD):.0%}`, "
                    f"`gap {float(meta.get('drawdown_guardrail_gap_threshold') or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD):.0%}`"
                )
                if meta.get("drawdown_guardrail_trigger_count") is not None:
                    st.markdown(
                        f"- `Drawdown Trigger Count`: `{int(meta.get('drawdown_guardrail_trigger_count') or 0)}`"
                    )
            if meta.get("avg_turnover") is not None:
                st.markdown(f"- `Average Turnover`: `{float(meta['avg_turnover']):.2%}`")
            if meta.get("estimated_cost_total") is not None:
                st.markdown(f"- `Estimated Cost Total`: `{float(meta['estimated_cost_total']):,.1f}`")
            if meta.get("validation_status"):
                st.markdown(f"- `Validation Status`: `{meta['validation_status']}`")
            if meta.get("benchmark_policy_status"):
                st.markdown(f"- `Benchmark Policy Status`: `{meta['benchmark_policy_status']}`")
            if meta.get("liquidity_policy_status"):
                st.markdown(f"- `Liquidity Policy Status`: `{meta['liquidity_policy_status']}`")
            if meta.get("validation_policy_status"):
                st.markdown(f"- `Validation Policy Status`: `{meta['validation_policy_status']}`")
            if meta.get("guardrail_policy_status"):
                st.markdown(f"- `Guardrail Policy Status`: `{meta['guardrail_policy_status']}`")
            if meta.get("promotion_decision"):
                st.markdown(f"- `Promotion Decision`: `{meta['promotion_decision']}`")
            if meta.get("promotion_next_step"):
                st.markdown(f"- `Promotion Next Step`: `{meta['promotion_next_step']}`")
            if meta.get("shortlist_status"):
                st.markdown(
                    f"- `Shortlist Status`: `{meta['shortlist_status']}` "
                    f"(`{_shortlist_status_value_to_label(meta.get('shortlist_status'))}`)"
                )
            if meta.get("shortlist_next_step"):
                st.markdown(f"- `Shortlist Next Step`: `{meta['shortlist_next_step']}`")
            if meta.get("shortlist_family"):
                st.markdown(f"- `Shortlist Family`: `{meta['shortlist_family']}`")
            if meta.get("probation_status"):
                st.markdown(
                    f"- `Probation Status`: `{meta['probation_status']}` "
                    f"(`{_probation_status_value_to_label(meta.get('probation_status'))}`)"
                )
            if meta.get("probation_stage"):
                st.markdown(f"- `Probation Stage`: `{meta['probation_stage']}`")
            if meta.get("probation_review_frequency"):
                st.markdown(f"- `Probation Review Frequency`: `{meta['probation_review_frequency']}`")
            if meta.get("probation_next_step"):
                st.markdown(f"- `Probation Next Step`: `{meta['probation_next_step']}`")
            if meta.get("monitoring_status"):
                st.markdown(
                    f"- `Monitoring Status`: `{meta['monitoring_status']}` "
                    f"(`{_monitoring_status_value_to_label(meta.get('monitoring_status'))}`)"
                )
            if meta.get("monitoring_review_frequency"):
                st.markdown(f"- `Monitoring Review Frequency`: `{meta['monitoring_review_frequency']}`")
            if meta.get("monitoring_next_step"):
                st.markdown(f"- `Monitoring Next Step`: `{meta['monitoring_next_step']}`")
            if meta.get("monitoring_focus"):
                st.markdown(
                    "- `Monitoring Focus`: "
                    + ", ".join(f"`{item}`" for item in list(meta.get("monitoring_focus") or []))
                )
            if meta.get("monitoring_breach_signals"):
                st.markdown(
                    "- `Monitoring Breach Signals`: "
                    + ", ".join(f"`{item}`" for item in list(meta.get("monitoring_breach_signals") or []))
                )
            if meta.get("deployment_readiness_status"):
                st.markdown(
                    f"- `Deployment Readiness`: `{meta['deployment_readiness_status']}` "
                    f"(`{_deployment_readiness_status_value_to_label(meta.get('deployment_readiness_status'))}`)"
                )
            if meta.get("deployment_readiness_next_step"):
                st.markdown(f"- `Deployment Next Step`: `{meta['deployment_readiness_next_step']}`")
            if meta.get("deployment_check_pass_count") is not None:
                st.markdown(
                    f"- `Deployment Checklist Counts`: pass `{int(meta.get('deployment_check_pass_count') or 0)}`, "
                    f"watch `{int(meta.get('deployment_check_watch_count') or 0)}`, "
                    f"fail `{int(meta.get('deployment_check_fail_count') or 0)}`, "
                    f"unavailable `{int(meta.get('deployment_check_unavailable_count') or 0)}`"
                )
            if meta.get("rolling_review_status"):
                st.markdown(
                    f"- `Rolling Review`: `{meta['rolling_review_status']}` "
                    f"(`{_review_status_value_to_label(meta.get('rolling_review_status'))}`)"
                )
            if meta.get("rolling_review_window_label"):
                st.markdown(f"- `Rolling Review Window`: `{meta['rolling_review_window_label']}`")
            if meta.get("rolling_review_recent_excess_return") is not None:
                st.markdown(
                    f"- `Recent Window Excess`: `{float(meta.get('rolling_review_recent_excess_return') or 0.0):.2%}`"
                )
            if meta.get("out_of_sample_review_status"):
                st.markdown(
                    f"- `Out-Of-Sample Review`: `{meta['out_of_sample_review_status']}` "
                    f"(`{_review_status_value_to_label(meta.get('out_of_sample_review_status'))}`)"
                )
            if meta.get("out_of_sample_out_sample_excess_return") is not None:
                st.markdown(
                    f"- `Out-Of-Sample Excess`: `{float(meta.get('out_of_sample_out_sample_excess_return') or 0.0):.2%}`"
                )
            if meta.get("strategy_max_drawdown") is not None:
                st.markdown(f"- `Strategy Max Drawdown`: `{float(meta['strategy_max_drawdown']):.2%}`")
            if meta.get("benchmark_max_drawdown") is not None:
                st.markdown(f"- `Benchmark Max Drawdown`: `{float(meta['benchmark_max_drawdown']):.2%}`")
            if meta.get("drawdown_gap_vs_benchmark") is not None:
                st.markdown(f"- `Drawdown Gap vs Benchmark`: `{float(meta['drawdown_gap_vs_benchmark']):.2%}`")
            if meta.get("rolling_underperformance_share") is not None:
                st.markdown(
                    f"- `Rolling Underperformance`: share `{float(meta['rolling_underperformance_share']):.2%}`, "
                    f"current streak `{int(meta.get('rolling_underperformance_current_streak') or 0)}`, "
                    f"worst excess `{float(meta.get('rolling_underperformance_worst_excess_return') or 0.0):.2%}`"
                )
            if meta.get("promotion_rationale"):
                st.markdown(
                    "- `Promotion Rationale`: "
                    + ", ".join(f"`{item}`" for item in list(meta.get("promotion_rationale") or []))
                )
            if meta.get("benchmark_policy_watch_signals"):
                st.markdown(
                    "- `Benchmark Policy Signals`: "
                    + ", ".join(f"`{item}`" for item in list(meta.get("benchmark_policy_watch_signals") or []))
                )
            if meta.get("guardrail_policy_watch_signals"):
                st.markdown(
                    "- `Guardrail Policy Signals`: "
                    + ", ".join(f"`{item}`" for item in list(meta.get("guardrail_policy_watch_signals") or []))
                )
            if meta.get("dynamic_candidate_count") is not None:
                st.markdown(
                    f"- `Dynamic Candidate Pool`: `{meta.get('dynamic_candidate_count')}` "
                    f"(target `{meta.get('dynamic_target_size') or '-'}`)"
                )
            if dynamic_snapshot_rows or dynamic_candidate_status_rows:
                st.markdown(
                    f"- `Dynamic Detail Rows`: snapshot `{len(dynamic_snapshot_rows)}`, "
                    f"candidate `{len(dynamic_candidate_status_rows)}`"
                )
            if meta.get("trend_filter_enabled"):
                st.markdown(f"- `Trend Filter`: `MA{meta.get('trend_filter_window', STRICT_TREND_FILTER_DEFAULT_WINDOW)}`")
            if meta.get("market_regime_enabled"):
                st.markdown(
                    f"- `Market Regime`: `{meta.get('market_regime_benchmark', STRICT_MARKET_REGIME_DEFAULT_BENCHMARK)} < MA{meta.get('market_regime_window', STRICT_MARKET_REGIME_DEFAULT_WINDOW)} => cash`"
                )
            price_freshness = meta.get("price_freshness") or {}
            freshness_details = price_freshness.get("details") or {}
            if freshness_details:
                st.markdown(
                    f"- `Price Freshness`: common `{freshness_details.get('common_latest_date', '-')}`, "
                    f"newest `{freshness_details.get('newest_latest_date', '-')}`, "
                    f"spread `{freshness_details.get('spread_days', 0)}d`"
                )
            universe_debug = meta.get("universe_debug") or {}
            if universe_debug:
                st.markdown(
                    f"- `Membership Count`: avg `{universe_debug.get('avg_membership_count', '-')}`, "
                    f"min `{universe_debug.get('min_membership_count', '-')}`, "
                    f"max `{universe_debug.get('max_membership_count', '-')}`"
                )
                if universe_debug.get("price_window_start") or universe_debug.get("price_window_end"):
                    st.markdown(
                        f"- `Price Window`: `{universe_debug.get('price_window_start', '-')}` -> `{universe_debug.get('price_window_end', '-')}`"
                    )
                if universe_debug.get("profile_delisted_count") is not None or universe_debug.get("profile_issue_count") is not None:
                    st.markdown(
                        f"- `Profile Diagnostics`: active `{universe_debug.get('profile_active_count', '-')}`, "
                        f"delisted `{universe_debug.get('profile_delisted_count', '-')}`, "
                        f"issue `{universe_debug.get('profile_issue_count', '-')}`"
                    )
        with right:
            st.markdown("##### Runtime Metadata")
            st.json(meta)


def _strategy_compare_defaults(strategy_name: str) -> dict:
    if strategy_name == "Equal Weight":
        return {
            "tickers": ["VIG", "SCHD", "DGRO", "GLD"],
            "preset_name": "Dividend ETFs",
            "runner": run_equal_weight_backtest_from_db,
            "extra": {"rebalance_interval": 12},
        }
    if strategy_name == "GTAA":
        return {
            "tickers": GTAA_DEFAULT_TICKERS,
            "preset_name": "GTAA Universe",
            "runner": run_gtaa_backtest_from_db,
            "extra": {
                "top": 3,
                "interval": GTAA_DEFAULT_SIGNAL_INTERVAL,
                "score_lookback_months": list(GTAA_DEFAULT_SCORE_LOOKBACK_MONTHS),
                "score_return_columns": list(GTAA_SCORE_RETURN_COLUMNS),
                "score_weights": GTAA_DEFAULT_SCORE_WEIGHTS.copy(),
                "trend_filter_window": GTAA_DEFAULT_TREND_FILTER_WINDOW,
                "risk_off_mode": GTAA_DEFAULT_RISK_OFF_MODE,
                "defensive_tickers": GTAA_DEFAULT_DEFENSIVE_TICKERS.copy(),
                "market_regime_enabled": False,
                "market_regime_window": STRICT_MARKET_REGIME_DEFAULT_WINDOW,
                "market_regime_benchmark": STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
                "crash_guardrail_enabled": GTAA_DEFAULT_CRASH_GUARDRAIL_ENABLED,
                "crash_guardrail_drawdown_threshold": GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD,
                "crash_guardrail_lookback_months": GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS,
                "min_price_filter": ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
                "transaction_cost_bps": ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
                "promotion_min_etf_aum_b": ETF_OPERABILITY_DEFAULT_MIN_AUM_B,
                "promotion_max_bid_ask_spread_pct": ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
                "benchmark_ticker": ETF_REAL_MONEY_DEFAULT_BENCHMARK,
            },
        }
    if strategy_name == "Risk Parity Trend":
        return {
            "tickers": ["SPY", "TLT", "GLD", "IEF", "LQD"],
            "preset_name": "Risk Parity Universe",
            "runner": run_risk_parity_trend_backtest_from_db,
            "extra": {
                "min_price_filter": ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
                "transaction_cost_bps": ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
                "promotion_min_etf_aum_b": ETF_OPERABILITY_DEFAULT_MIN_AUM_B,
                "promotion_max_bid_ask_spread_pct": ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
                "benchmark_ticker": ETF_REAL_MONEY_DEFAULT_BENCHMARK,
            },
        }
    if strategy_name == "Dual Momentum":
        return {
            "tickers": ["QQQ", "SPY", "IWM", "SOXX", "BIL"],
            "preset_name": "Dual Momentum Universe",
            "runner": run_dual_momentum_backtest_from_db,
            "extra": {
                "min_price_filter": ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
                "transaction_cost_bps": ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
                "promotion_min_etf_aum_b": ETF_OPERABILITY_DEFAULT_MIN_AUM_B,
                "promotion_max_bid_ask_spread_pct": ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
                "benchmark_ticker": ETF_REAL_MONEY_DEFAULT_BENCHMARK,
            },
        }
    if strategy_name == "Quality Snapshot":
        return {
            "tickers": ["AAPL", "MSFT", "GOOG"],
            "preset_name": "Big Tech Quality Trial",
            "runner": run_quality_snapshot_backtest_from_db,
            "extra": {
                "factor_freq": "annual",
                "rebalance_freq": "monthly",
                "quality_factors": ["roe", "gross_margin", "operating_margin", "debt_ratio"],
                "top_n": 2,
                "snapshot_mode": "broad_research",
            },
        }
    if strategy_name == "Quality Snapshot (Strict Annual)":
        return {
            "tickers": QUALITY_STRICT_PRESETS[STRICT_ANNUAL_COMPARE_DEFAULT_PRESET],
            "preset_name": STRICT_ANNUAL_COMPARE_DEFAULT_PRESET,
            "runner": run_quality_snapshot_strict_annual_backtest_from_db,
            "extra": {
                "quality_factors": QUALITY_STRICT_DEFAULT_FACTORS,
                "top_n": 2,
                "min_price_filter": ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
                "min_history_months_filter": STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
                "min_avg_dollar_volume_20d_m_filter": STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
                "transaction_cost_bps": ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
                "benchmark_ticker": ETF_REAL_MONEY_DEFAULT_BENCHMARK,
                "promotion_min_benchmark_coverage": STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
                "promotion_min_net_cagr_spread": STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
                "promotion_min_liquidity_clean_coverage": STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
                "promotion_max_underperformance_share": STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
                "promotion_min_worst_rolling_excess_return": STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
                "promotion_max_strategy_drawdown": STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
                "promotion_max_drawdown_gap_vs_benchmark": STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
                "underperformance_guardrail_enabled": STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
                "underperformance_guardrail_window_months": STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
                "underperformance_guardrail_threshold": STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
                "drawdown_guardrail_enabled": STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
                "drawdown_guardrail_window_months": STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
                "drawdown_guardrail_strategy_threshold": STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
                "drawdown_guardrail_gap_threshold": STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
            },
        }
    if strategy_name == "Quality Snapshot (Strict Quarterly Prototype)":
        return {
            "tickers": QUALITY_STRICT_PRESETS[STRICT_QUARTERLY_PROTOTYPE_DEFAULT_PRESET],
            "preset_name": STRICT_QUARTERLY_PROTOTYPE_DEFAULT_PRESET,
            "runner": run_quality_snapshot_strict_quarterly_prototype_backtest_from_db,
            "extra": {
                "quality_factors": QUALITY_STRICT_DEFAULT_FACTORS,
                "top_n": 2,
            },
        }
    if strategy_name == "Value Snapshot (Strict Annual)":
        return {
            "tickers": VALUE_STRICT_PRESETS[STRICT_ANNUAL_COMPARE_DEFAULT_PRESET],
            "preset_name": STRICT_ANNUAL_COMPARE_DEFAULT_PRESET,
            "runner": run_value_snapshot_strict_annual_backtest_from_db,
            "extra": {
                "value_factors": VALUE_STRICT_DEFAULT_FACTORS,
                "top_n": 10,
                "min_price_filter": ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
                "min_history_months_filter": STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
                "min_avg_dollar_volume_20d_m_filter": STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
                "transaction_cost_bps": ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
                "benchmark_ticker": ETF_REAL_MONEY_DEFAULT_BENCHMARK,
                "promotion_min_benchmark_coverage": STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
                "promotion_min_net_cagr_spread": STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
                "promotion_min_liquidity_clean_coverage": STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
                "promotion_max_underperformance_share": STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
                "promotion_min_worst_rolling_excess_return": STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
                "promotion_max_strategy_drawdown": STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
                "promotion_max_drawdown_gap_vs_benchmark": STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
                "underperformance_guardrail_enabled": STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
                "underperformance_guardrail_window_months": STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
                "underperformance_guardrail_threshold": STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
                "drawdown_guardrail_enabled": STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
                "drawdown_guardrail_window_months": STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
                "drawdown_guardrail_strategy_threshold": STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
                "drawdown_guardrail_gap_threshold": STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
            },
        }
    if strategy_name == "Value Snapshot (Strict Quarterly Prototype)":
        return {
            "tickers": VALUE_STRICT_PRESETS[STRICT_QUARTERLY_PROTOTYPE_DEFAULT_PRESET],
            "preset_name": STRICT_QUARTERLY_PROTOTYPE_DEFAULT_PRESET,
            "runner": run_value_snapshot_strict_quarterly_prototype_backtest_from_db,
            "extra": {
                "value_factors": VALUE_STRICT_DEFAULT_FACTORS,
                "top_n": 10,
            },
        }
    if strategy_name == "Quality + Value Snapshot (Strict Annual)":
        return {
            "tickers": QUALITY_STRICT_PRESETS[STRICT_ANNUAL_COMPARE_DEFAULT_PRESET],
            "preset_name": STRICT_ANNUAL_COMPARE_DEFAULT_PRESET,
            "runner": run_quality_value_snapshot_strict_annual_backtest_from_db,
            "extra": {
                "quality_factors": QUALITY_STRICT_DEFAULT_FACTORS,
                "value_factors": VALUE_STRICT_DEFAULT_FACTORS,
                "top_n": 10,
                "min_price_filter": ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
                "min_history_months_filter": STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
                "min_avg_dollar_volume_20d_m_filter": STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
                "transaction_cost_bps": ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
                "benchmark_ticker": ETF_REAL_MONEY_DEFAULT_BENCHMARK,
                "promotion_min_benchmark_coverage": STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
                "promotion_min_net_cagr_spread": STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
                "promotion_min_liquidity_clean_coverage": STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
                "promotion_max_underperformance_share": STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
                "promotion_min_worst_rolling_excess_return": STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
                "promotion_max_strategy_drawdown": STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
                "promotion_max_drawdown_gap_vs_benchmark": STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
                "underperformance_guardrail_enabled": STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
                "underperformance_guardrail_window_months": STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
                "underperformance_guardrail_threshold": STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
                "drawdown_guardrail_enabled": STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
                "drawdown_guardrail_window_months": STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
                "drawdown_guardrail_strategy_threshold": STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
                "drawdown_guardrail_gap_threshold": STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
            },
        }
    if strategy_name == "Quality + Value Snapshot (Strict Quarterly Prototype)":
        return {
            "tickers": QUALITY_STRICT_PRESETS[STRICT_QUARTERLY_PROTOTYPE_DEFAULT_PRESET],
            "preset_name": STRICT_QUARTERLY_PROTOTYPE_DEFAULT_PRESET,
            "runner": run_quality_value_snapshot_strict_quarterly_prototype_backtest_from_db,
            "extra": {
                "quality_factors": QUALITY_STRICT_DEFAULT_FACTORS,
                "value_factors": VALUE_STRICT_DEFAULT_FACTORS,
                "top_n": 10,
            },
        }
    raise BacktestInputError(f"Unsupported compare strategy: {strategy_name}")


def _resolve_compare_strategy_universe(
    strategy_name: str,
    *,
    preset_name: str | None,
    fallback_tickers: list[str],
) -> tuple[list[str], str | None]:
    if strategy_name == "Quality Snapshot (Strict Annual)":
        if preset_name in QUALITY_STRICT_PRESETS:
            return QUALITY_STRICT_PRESETS[preset_name], preset_name
    elif strategy_name == "Quality Snapshot (Strict Quarterly Prototype)":
        if preset_name in QUALITY_STRICT_PRESETS:
            return QUALITY_STRICT_PRESETS[preset_name], preset_name
    elif strategy_name == "Value Snapshot (Strict Annual)":
        if preset_name in VALUE_STRICT_PRESETS:
            return VALUE_STRICT_PRESETS[preset_name], preset_name
    elif strategy_name == "Value Snapshot (Strict Quarterly Prototype)":
        if preset_name in VALUE_STRICT_PRESETS:
            return VALUE_STRICT_PRESETS[preset_name], preset_name
    elif strategy_name == "Quality + Value Snapshot (Strict Annual)":
        if preset_name in QUALITY_STRICT_PRESETS:
            return QUALITY_STRICT_PRESETS[preset_name], preset_name
    elif strategy_name == "Quality + Value Snapshot (Strict Quarterly Prototype)":
        if preset_name in QUALITY_STRICT_PRESETS:
            return QUALITY_STRICT_PRESETS[preset_name], preset_name

    return fallback_tickers, preset_name


def _run_compare_strategy(
    strategy_name: str,
    *,
    start: str,
    end: str,
    timeframe: str,
    option: str,
    overrides: dict | None = None,
) -> dict:
    config = _strategy_compare_defaults(strategy_name)
    runner = config["runner"]
    params = dict(config["extra"])
    if overrides:
        params.update(overrides)

    tickers = config["tickers"]
    preset_name = config["preset_name"]
    universe_mode = "preset"
    if strategy_name == "Equal Weight":
        universe_mode = params.pop("universe_mode", "preset")
        preset_name = params.pop("preset_name", preset_name)
        tickers = list(params.pop("tickers", tickers))
        if universe_mode == "preset" and preset_name in EQUAL_WEIGHT_PRESETS:
            tickers = EQUAL_WEIGHT_PRESETS[preset_name]
        else:
            universe_mode = "manual_tickers"
            preset_name = None
    elif strategy_name == "GTAA":
        universe_mode = params.pop("universe_mode", "preset")
        preset_name = params.pop("preset_name", preset_name)
        tickers = list(params.pop("tickers", tickers))
        if universe_mode == "preset" and preset_name in GTAA_PRESETS:
            tickers = GTAA_PRESETS[preset_name]
        else:
            universe_mode = "manual_tickers"
            preset_name = None
    elif strategy_name in {
        "Quality Snapshot (Strict Annual)",
        "Quality Snapshot (Strict Quarterly Prototype)",
        "Value Snapshot (Strict Annual)",
        "Value Snapshot (Strict Quarterly Prototype)",
        "Quality + Value Snapshot (Strict Annual)",
        "Quality + Value Snapshot (Strict Quarterly Prototype)",
    }:
        tickers, preset_name = _resolve_compare_strategy_universe(
            strategy_name,
            preset_name=params.pop("preset_name", preset_name),
            fallback_tickers=params.pop("tickers", tickers),
        )
        universe_mode = params.pop("universe_mode", "preset")

    return runner(
        tickers=tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        universe_mode=universe_mode,
        preset_name=preset_name,
        **params,
    )


def _build_balance_compare_view(bundles: list[dict]) -> pd.DataFrame:
    series_list = []
    for bundle in bundles:
        chart_df = bundle["chart_df"].copy()
        name = bundle["strategy_name"]
        series = chart_df.set_index("Date")["Total Balance"].rename(name)
        series_list.append(series)

    return pd.concat(series_list, axis=1).sort_index()


def _build_monthly_component_balance_views(
    bundles: list[dict],
    *,
    strategy_names: list[str],
    weights: list[float],
    date_policy: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    monthly_balances = []
    for bundle, strategy_name in zip(bundles, strategy_names):
        result_df = bundle["result_df"].copy()
        result_df["Date"] = pd.to_datetime(result_df["Date"])
        result_df["_month"] = result_df["Date"].dt.to_period("M")
        monthly_df = result_df.groupby("_month", as_index=False).agg(TotalBalance=("Total Balance", "mean"))
        monthly_df["Date"] = monthly_df["_month"].dt.to_timestamp("M")
        monthly_df = monthly_df.drop(columns=["_month"]).set_index("Date").sort_index()
        monthly_balances.append(monthly_df.rename(columns={"TotalBalance": strategy_name}))

    join_how = "outer" if date_policy == "union" else "inner"
    balance_wide = pd.concat(monthly_balances, axis=1, join=join_how).sort_index()

    normalized_weights = pd.Series(weights, index=strategy_names, dtype=float)
    normalized_weights = normalized_weights / normalized_weights.sum()

    weight_frame = balance_wide.notna().mul(normalized_weights, axis=1)
    denominator = weight_frame.sum(axis=1).replace(0, pd.NA)
    contribution_amount = balance_wide.mul(normalized_weights, axis=1).div(denominator, axis=0)
    contribution_share = contribution_amount.div(contribution_amount.sum(axis=1), axis=0)

    return contribution_amount, contribution_share


def _build_drawdown_compare_view(bundles: list[dict]) -> pd.DataFrame:
    drawdown_frames = []
    for bundle in bundles:
        result_df = bundle["result_df"].copy().sort_values("Date")
        balance = result_df["Total Balance"]
        drawdown = (balance / balance.cummax() - 1).rename(bundle["strategy_name"])
        drawdown_frames.append(pd.DataFrame({"Date": result_df["Date"], bundle["strategy_name"]: drawdown}))

    merged = drawdown_frames[0]
    for frame in drawdown_frames[1:]:
        merged = merged.merge(frame, on="Date", how="outer")

    return merged.sort_values("Date").set_index("Date")


def _build_total_return_compare_view(bundles: list[dict]) -> pd.DataFrame:
    series_list = []
    for bundle in bundles:
        chart_df = bundle["chart_df"].copy()
        name = bundle["strategy_name"]
        series = chart_df.set_index("Date")["Total Return"].rename(name)
        series_list.append(series)

    return pd.concat(series_list, axis=1).sort_index()


def _build_period_extremes_tables(result_df: pd.DataFrame, top_n: int = 3) -> tuple[pd.DataFrame, pd.DataFrame]:
    period_df = (
        result_df[["Date", "Total Return", "Total Balance"]]
        .dropna(subset=["Total Return"])
        .sort_values("Date")
        .copy()
    )

    best = (
        period_df.sort_values("Total Return", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    worst = (
        period_df.sort_values("Total Return", ascending=True)
        .head(top_n)
        .reset_index(drop=True)
    )
    return best, worst


def _build_balance_extremes_tables(chart_df: pd.DataFrame, top_n: int = 3) -> tuple[pd.DataFrame, pd.DataFrame]:
    balance_df = (
        chart_df[["Date", "Total Balance", "Total Return"]]
        .dropna(subset=["Total Balance"])
        .sort_values("Date")
        .copy()
    )

    highs = (
        balance_df.sort_values("Total Balance", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    lows = (
        balance_df.sort_values("Total Balance", ascending=True)
        .head(top_n)
        .reset_index(drop=True)
    )
    return highs, lows


def _build_balance_marker_df(chart_df: pd.DataFrame, result_df: pd.DataFrame | None = None) -> pd.DataFrame:
    base_df = chart_df.copy()
    base_df["Date"] = pd.to_datetime(base_df["Date"])

    high_idx = base_df["Total Balance"].idxmax()
    low_idx = base_df["Total Balance"].idxmin()
    end_idx = base_df.index[-1]

    marker_df = pd.concat(
        [
            pd.DataFrame([base_df.loc[high_idx]]).assign(Marker="High"),
            pd.DataFrame([base_df.loc[low_idx]]).assign(Marker="Low"),
            pd.DataFrame([base_df.loc[end_idx]]).assign(Marker="End"),
        ],
        ignore_index=True,
    ).drop_duplicates(subset=["Date", "Marker"])

    if result_df is not None and not result_df.empty:
        best_df, worst_df = _build_period_extremes_tables(result_df, top_n=1)
        if not best_df.empty:
            best_row = base_df.loc[base_df["Date"] == pd.to_datetime(best_df.iloc[0]["Date"])]
            if not best_row.empty:
                marker_df = pd.concat(
                    [marker_df, best_row.assign(Marker="Best Period")],
                    ignore_index=True,
                )
        if not worst_df.empty:
            worst_row = base_df.loc[base_df["Date"] == pd.to_datetime(worst_df.iloc[0]["Date"])]
            if not worst_row.empty:
                marker_df = pd.concat(
                    [marker_df, worst_row.assign(Marker="Worst Period")],
                    ignore_index=True,
                )

    return marker_df.drop_duplicates(subset=["Date", "Marker"])


def _render_balance_chart_with_markers(
    chart_df: pd.DataFrame,
    *,
    result_df: pd.DataFrame | None = None,
    title: str = "Equity Curve",
) -> None:
    base_df = chart_df.copy()
    base_df["Date"] = pd.to_datetime(base_df["Date"])
    marker_df = _build_balance_marker_df(chart_df, result_df)

    line = (
        alt.Chart(base_df)
        .mark_line()
        .encode(
            x=alt.X("Date:T", title="Date"),
            y=alt.Y("Total Balance:Q", title="Total Balance"),
            tooltip=[
                alt.Tooltip("Date:T", title="Date"),
                alt.Tooltip("Total Balance:Q", title="Total Balance", format=",.1f"),
                alt.Tooltip("Total Return:Q", title="Total Return", format=".3f"),
            ],
        )
    )

    points = (
        alt.Chart(marker_df)
        .mark_point(size=90, filled=True)
        .encode(
            x="Date:T",
            y="Total Balance:Q",
            color=alt.Color(
                "Marker:N",
                scale=alt.Scale(
                    domain=["High", "Low", "End", "Best Period", "Worst Period"],
                    range=["#d62728", "#1f77b4", "#2ca02c", "#ff7f0e", "#9467bd"],
                ),
            ),
            tooltip=[
                alt.Tooltip("Marker:N", title="Marker"),
                alt.Tooltip("Date:T", title="Date"),
                alt.Tooltip("Total Balance:Q", title="Total Balance", format=",.1f"),
            ],
        )
    )

    labels = (
        alt.Chart(marker_df)
        .mark_text(align="left", dx=8, dy=-8, fontSize=12)
        .encode(
            x="Date:T",
            y="Total Balance:Q",
            text="Marker:N",
            color=alt.value("#444"),
        )
    )

    st.altair_chart(
        (line + points + labels).properties(height=360, title=title),
        use_container_width=True,
    )


def _render_dynamic_universe_details(bundle: dict[str, Any]) -> None:
    meta = bundle.get("meta") or {}
    universe_debug = meta.get("universe_debug") or {}
    snapshot_rows = bundle.get("dynamic_universe_snapshot_rows") or []
    candidate_status_rows = bundle.get("dynamic_candidate_status_rows") or []

    if (
        not snapshot_rows
        and not candidate_status_rows
        and meta.get("universe_contract") != HISTORICAL_DYNAMIC_PIT_UNIVERSE
    ):
        st.caption("이번 결과는 `Historical Dynamic PIT Universe` run이 아니어서 dynamic universe 상세가 없습니다.")
        return

    st.caption(
        "`Historical Dynamic PIT Universe`에서는 리밸런싱 날짜마다 모집군을 다시 계산합니다. "
        "`dynamic_universe_snapshot_rows`는 날짜별 membership/continuity 요약이고, "
        "`dynamic_candidate_status_rows`는 후보 심볼별 가격 이력과 profile 상태를 보여줍니다."
    )

    if universe_debug:
        summary_cols = st.columns(4)
        summary_cols[0].metric("Candidate Pool", universe_debug.get("candidate_pool_count", "-"))
        summary_cols[1].metric("Target Size", universe_debug.get("target_size", "-"))
        summary_cols[2].metric("Membership Avg", universe_debug.get("avg_membership_count", "-"))
        summary_cols[3].metric("Turnover Avg", universe_debug.get("avg_turnover_count", "-"))

    if snapshot_rows:
        st.markdown("##### dynamic_universe_snapshot_rows")
        st.caption(
            "각 행은 리밸런싱 날짜 1개입니다. "
            "`membership_count`는 실제 편입 수, "
            "`continuity_ready_count`는 그 날짜를 가격 이력상 자연스럽게 커버하는 후보 수, "
            "`pre_listing_excluded_count` / `post_last_price_excluded_count`는 상장 전 또는 마지막 가격 이후라 제외된 후보 수입니다."
        )
        st.dataframe(pd.DataFrame(snapshot_rows), use_container_width=True, hide_index=True)

    if candidate_status_rows:
        st.markdown("##### dynamic_candidate_status_rows")
        st.caption(
            "각 행은 후보 심볼 1개입니다. "
            "`first_price_date` / `last_price_date`는 현재 DB 가격 이력 범위, "
            "`profile_status` / `profile_delisted_at`는 asset profile 기준 continuity 힌트입니다."
        )
        st.dataframe(pd.DataFrame(candidate_status_rows), use_container_width=True, hide_index=True)


def _render_real_money_details(bundle: dict[str, Any]) -> None:
    meta = bundle.get("meta") or {}
    if not meta.get("real_money_hardening"):
        st.caption("이 결과에는 Phase 12 real-money hardening 정보가 없습니다.")
        return

    result_df = bundle.get("result_df")
    benchmark_chart_df = bundle.get("benchmark_chart_df")
    benchmark_summary_df = bundle.get("benchmark_summary_df")

    def _render_value_list_caption(prefix: str, values: list[Any] | tuple[Any, ...] | None) -> None:
        if values:
            st.caption(prefix + ": " + ", ".join(f"`{value}`" for value in list(values)))

    def _section_header(title: str, description: str):
        section = st.container(border=True)
        with section:
            st.markdown(f"##### {title}")
            st.caption(description)
        return section

    st.info(
        "이 탭은 실전형 해석을 한 번에 보기 위한 화면입니다. "
        "먼저 `현재 판단`에서 지금 상태를 보고, "
        "그다음 `검토 근거`에서 왜 그런 판단이 나왔는지 확인하고, "
        "`실행 부담`에서 비용/유동성/ETF 운용 가능성을 본 뒤, "
        "마지막 `상세 데이터`에서 원자료를 확인하면 됩니다."
    )

    summary_cols = st.columns(6, gap="small")
    summary_cols[0].metric("Promotion", str(meta.get("promotion_decision") or "-").upper())
    summary_cols[1].metric("Shortlist", _shortlist_status_value_to_label(meta.get("shortlist_status")))
    summary_cols[2].metric("Probation", _probation_status_value_to_label(meta.get("probation_status")))
    summary_cols[3].metric("Deployment", _deployment_readiness_status_value_to_label(meta.get("deployment_readiness_status")))
    summary_cols[4].metric("Rolling Review", _review_status_value_to_label(meta.get("rolling_review_status")))
    summary_cols[5].metric("Validation", _review_status_value_to_label(meta.get("validation_status")))

    overview_tab, review_tab, execution_tab, detail_tab = st.tabs(
        ["현재 판단", "검토 근거", "실행 부담", "상세 데이터"]
    )

    with overview_tab:
        st.caption(
            "이 섹션은 이 전략을 지금 어떤 단계로 해석해야 하는지 보여줍니다. "
            "즉 `당장 보류할지`, `paper probation으로 둘지`, `소액 trial까지 볼지`를 먼저 판단하는 곳입니다."
        )

        if meta.get("promotion_decision"):
            with _section_header("전략 승격 판단", "이 전략이 현재 계약 기준에서 어느 정도까지 올라왔는지 보여줍니다."):
                decision = str(meta.get("promotion_decision") or "-")
                next_step = str(meta.get("promotion_next_step") or "-")
                promotion_cols = st.columns(2, gap="small")
                promotion_cols[0].metric("Decision", decision.upper())
                promotion_cols[1].metric("Next Step", next_step)
                rationale = list(meta.get("promotion_rationale") or [])
                if rationale:
                    st.caption("왜 이렇게 판단했는지: " + ", ".join(f"`{item}`" for item in rationale))
                if decision == "real_money_candidate":
                    st.success(
                        "현재 계약 기준에서는 실전형 후보로 읽을 수 있는 상태입니다. "
                        "다음 단계는 paper tracking 또는 소액 probation이 자연스럽습니다."
                    )
                elif decision == "production_candidate":
                    st.info(
                        "지금은 많이 정리된 상태이지만, 더 강한 robustness 검토 전까지는 "
                        "production candidate로 두는 편이 맞습니다."
                    )
                elif decision == "hold":
                    st.warning(
                        "현재 run은 바로 승격하기보다 hold로 보는 편이 맞습니다. "
                        "validation gap 또는 contract issue를 먼저 정리하는 것이 좋습니다."
                    )
                    hold_guidance_rows = _build_hold_resolution_guidance_rows(meta)
                    with st.container(border=True):
                        st.markdown("##### Hold 해결 가이드")
                        st.caption(
                            "이 전략이 무조건 나쁘다는 뜻은 아닙니다. "
                            "지금은 승격 전에 먼저 풀어야 하는 검증 blocker가 있다는 뜻입니다."
                        )
                        st.caption(
                            "아래 표에서 `현재 상태`는 지금 막히는 정도를, "
                            "`상태를 보는 위치`는 실제 화면 위치를, "
                            "`바로 해볼 일`은 가장 먼저 손댈 설정이나 데이터를 뜻합니다."
                        )
                        if hold_guidance_rows:
                            st.dataframe(
                                pd.DataFrame(hold_guidance_rows),
                                use_container_width=True,
                                hide_index=True,
                            )
                        st.info(
                            "먼저 `검토 근거`에서 막히는 항목을 확인하고, "
                            "필요하면 `실행 부담`에서 유동성 / 비용 / ETF 운용 가능성까지 같이 점검하면 가장 빠릅니다."
                        )

        if meta.get("shortlist_status"):
            with _section_header("후보 전략 숏리스트", "실전 후보 목록 안에서 현재 어느 단계인지 보여줍니다."):
                shortlist_status = str(meta.get("shortlist_status") or "-")
                shortlist_next_step = str(meta.get("shortlist_next_step") or "-")
                shortlist_family = str(meta.get("shortlist_family") or meta.get("strategy_family") or "-")
                shortlist_cols = st.columns(3, gap="small")
                shortlist_cols[0].metric("Family", shortlist_family)
                shortlist_cols[1].metric("Status", _shortlist_status_value_to_label(shortlist_status))
                shortlist_cols[2].metric("Next Step", shortlist_next_step)
                shortlist_rationale = list(meta.get("shortlist_rationale") or [])
                if shortlist_rationale:
                    st.caption("숏리스트 판단 근거: " + ", ".join(f"`{item}`" for item in shortlist_rationale))
                if shortlist_status == "small_capital_trial":
                    st.success(
                        "현재 계약 기준에서는 소액 실전 trial까지 검토할 수 있는 shortlist 상태입니다. "
                        "다만 월별 review 기록은 계속 남기는 편이 맞습니다."
                    )
                elif shortlist_status == "paper_probation":
                    st.info(
                        "현재 run은 paper probation으로 먼저 관찰하는 편이 가장 자연스럽습니다. "
                        "다음 review를 통과하면 소액 trial을 검토할 수 있습니다."
                    )
                elif shortlist_status == "watchlist":
                    st.info(
                        "지금은 shortlist watchlist로 두고, 추가 robustness / monitoring review를 거친 뒤 "
                        "paper probation으로 올리는 편이 맞습니다."
                    )
                elif shortlist_status == "hold":
                    st.warning(
                        "현재 run은 shortlist 단계로 올리기보다 hold로 두는 편이 맞습니다. "
                        "promotion / policy gap을 먼저 정리한 뒤 다시 보는 것이 좋습니다."
                    )

        if meta.get("probation_status") or meta.get("monitoring_status"):
            with _section_header(
                "Probation / Monitoring",
                "실제 운용 전 관찰 단계입니다. paper tracking 중인지, routine review로 충분한지, breach 신호가 있는지를 봅니다.",
            ):
                probation_status = str(meta.get("probation_status") or "-")
                probation_stage = str(meta.get("probation_stage") or "-")
                probation_review_frequency = str(meta.get("probation_review_frequency") or "-")
                monitoring_status = str(meta.get("monitoring_status") or "-")
                monitoring_review_frequency = str(meta.get("monitoring_review_frequency") or "-")
                probation_cols = st.columns(5, gap="small")
                probation_cols[0].metric("Probation", _probation_status_value_to_label(probation_status))
                probation_cols[1].metric("Stage", probation_stage)
                probation_cols[2].metric("Probation Review", probation_review_frequency)
                probation_cols[3].metric("Monitoring", _monitoring_status_value_to_label(monitoring_status))
                probation_cols[4].metric("Monitoring Review", monitoring_review_frequency)
                if meta.get("probation_next_step"):
                    st.caption(f"다음 probation 액션: `{meta.get('probation_next_step')}`")
                probation_rationale = list(meta.get("probation_rationale") or [])
                if probation_rationale:
                    st.caption("Probation 판단 근거: " + ", ".join(f"`{item}`" for item in probation_rationale))
                monitoring_focus = list(meta.get("monitoring_focus") or [])
                if monitoring_focus:
                    st.caption("지켜볼 항목: " + ", ".join(f"`{item}`" for item in monitoring_focus))
                monitoring_breach_signals = list(meta.get("monitoring_breach_signals") or [])
                if monitoring_breach_signals:
                    st.caption("경고 신호: " + ", ".join(f"`{item}`" for item in monitoring_breach_signals))

                if monitoring_status == "breach_watch":
                    st.warning(
                        "현재 probation 단계에서 breach signal이 관찰됐습니다. "
                        "비중 확대보다는 월별 review와 rule re-check를 먼저 하는 편이 맞습니다."
                    )
                elif monitoring_status == "heightened_review":
                    st.info(
                        "지금은 monitoring watch signal이 있어서, routine review보다 조금 더 보수적으로 월별 확인을 이어가는 편이 좋습니다."
                    )
                elif monitoring_status == "routine_review":
                    st.success("현재 기준에서는 routine monthly review로 probation을 이어갈 수 있는 상태입니다.")

        if meta.get("deployment_readiness_status"):
            with _section_header(
                "Deployment Readiness",
                "실제 배치 직전 체크리스트입니다. pass / watch / fail / unavailable 개수를 보고 지금 배치를 열어도 되는지 판단합니다.",
            ):
                deployment_status = str(meta.get("deployment_readiness_status") or "-")
                deployment_next_step = str(meta.get("deployment_readiness_next_step") or "-")
                deployment_cols = st.columns(6, gap="small")
                deployment_cols[0].metric("Status", _deployment_readiness_status_value_to_label(deployment_status))
                deployment_cols[1].metric("Next Step", deployment_next_step)
                deployment_cols[2].metric("Pass", str(int(meta.get("deployment_check_pass_count") or 0)))
                deployment_cols[3].metric("Watch", str(int(meta.get("deployment_check_watch_count") or 0)))
                deployment_cols[4].metric("Fail", str(int(meta.get("deployment_check_fail_count") or 0)))
                deployment_cols[5].metric("Unavailable", str(int(meta.get("deployment_check_unavailable_count") or 0)))

                deployment_rationale = list(meta.get("deployment_readiness_rationale") or [])
                if deployment_rationale:
                    st.caption("Deployment 판단 근거: " + ", ".join(f"`{item}`" for item in deployment_rationale))

                checklist_rows = list(meta.get("deployment_checklist_rows") or [])
                if checklist_rows:
                    with st.expander("Checklist 상세 보기", expanded=deployment_status in {"review_required", "blocked"}):
                        st.dataframe(pd.DataFrame(checklist_rows), use_container_width=True, hide_index=True)

                if deployment_status == "small_capital_ready":
                    st.success("현재 checklist 기준에서는 small-capital trial까지 비교적 자연스럽게 볼 수 있는 상태입니다.")
                elif deployment_status == "small_capital_ready_with_review":
                    st.info(
                        "현재 checklist 기준에서는 소액 trial은 가능하지만, watch / unavailable 항목을 같이 보면서 더 보수적으로 운용하는 편이 맞습니다."
                    )
                elif deployment_status == "paper_only":
                    st.info("지금은 deployment-ready보다는 paper probation 단계로 두는 편이 맞습니다.")
                elif deployment_status == "review_required":
                    st.warning("failed checklist 항목이 있어, 수동 review 없이 바로 비중을 늘리는 것은 보수적이지 않습니다.")
                elif deployment_status == "blocked":
                    st.warning("현재 checklist 기준에서는 deployment를 열기보다 blocker를 먼저 해결하는 편이 맞습니다.")

    with review_tab:
        st.caption(
            "이 섹션은 왜 이런 결론이 나왔는지 보여줍니다. "
            "benchmark 대비 성과, 최근 구간 consistency, 정책 기준 통과 여부를 함께 보시면 됩니다."
        )

        if meta.get("benchmark_available") or meta.get("benchmark_contract") or meta.get("benchmark_ticker"):
            with _section_header(
                "Benchmark / Validation 요약",
                "benchmark와 비교했을 때 현재 run이 어느 정도로 버티는지 빠르게 읽는 요약입니다.",
            ):
                benchmark_cols = st.columns(6, gap="small")
                benchmark_cols[0].metric("Benchmark Contract", _benchmark_contract_value_to_label(meta.get("benchmark_contract")))
                benchmark_cols[1].metric(
                    "Benchmark",
                    str(
                        meta.get("benchmark_label")
                        if meta.get("benchmark_contract") == STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT
                        else meta.get("benchmark_ticker") or meta.get("benchmark_label") or "-"
                    ),
                )
                benchmark_cols[2].metric("Benchmark Available", "Yes" if meta.get("benchmark_available") else "No")
                if meta.get("benchmark_symbol_count") is not None:
                    benchmark_cols[3].metric("Benchmark Universe", str(int(meta.get("benchmark_symbol_count") or 0)))
                if meta.get("benchmark_eligible_symbol_count") is not None:
                    benchmark_cols[4].metric("Benchmark Eligible", str(int(meta.get("benchmark_eligible_symbol_count") or 0)))
                if meta.get("benchmark_end_balance") is not None:
                    benchmark_cols[5].metric("Benchmark End Balance", f"{float(meta.get('benchmark_end_balance')):,.1f}")
                summary_lines: list[str] = []
                if meta.get("benchmark_cagr") is not None:
                    summary_lines.append(f"Benchmark CAGR `{float(meta.get('benchmark_cagr')):.2%}`")
                if meta.get("net_cagr_spread") is not None:
                    summary_lines.append(f"Net CAGR Spread `{float(meta.get('net_cagr_spread')):.2%}`")
                if meta.get("net_excess_end_balance") is not None:
                    summary_lines.append(f"Net Excess End Balance `{float(meta.get('net_excess_end_balance')):,.1f}`")
                if meta.get("benchmark_row_coverage") is not None:
                    summary_lines.append(f"Coverage `{float(meta.get('benchmark_row_coverage')):.2%}`")
                if summary_lines:
                    st.caption(" | ".join(summary_lines))
                if meta.get("benchmark_contract") == STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT:
                    st.caption(
                        "Candidate-universe equal-weight benchmark는 같은 후보 universe를 단순히 균등 보유했을 때의 reference curve입니다."
                    )

        if meta.get("benchmark_available"):
            with _section_header(
                "Validation Surface",
                "benchmark 대비 최근 구간에서 얼마나 자주 뒤처졌는지, 낙폭이 얼마나 깊었는지를 요약합니다.",
            ):
                validation_cols = st.columns(4, gap="small")
                validation_cols[0].metric("Validation Status", str(meta.get("validation_status") or "normal").upper())
                if meta.get("strategy_max_drawdown") is not None:
                    validation_cols[1].metric("Strategy Max Drawdown", f"{float(meta.get('strategy_max_drawdown')):.2%}")
                if meta.get("benchmark_max_drawdown") is not None:
                    validation_cols[2].metric("Benchmark Max Drawdown", f"{float(meta.get('benchmark_max_drawdown')):.2%}")
                validation_cols[3].metric("Rolling Window", str(meta.get("validation_window_label") or "-"))

                rolling_cols = st.columns(4, gap="small")
                if meta.get("rolling_underperformance_share") is not None:
                    rolling_cols[0].metric("Underperformance Share", f"{float(meta.get('rolling_underperformance_share')):.2%}")
                rolling_cols[1].metric("Current Underperf Streak", str(int(meta.get("rolling_underperformance_current_streak") or 0)))
                rolling_cols[2].metric("Longest Underperf Streak", str(int(meta.get("rolling_underperformance_longest_streak") or 0)))
                if meta.get("rolling_underperformance_worst_excess_return") is not None:
                    rolling_cols[3].metric(
                        "Worst Rolling Excess",
                        f"{float(meta.get('rolling_underperformance_worst_excess_return')):.2%}",
                    )
                _render_value_list_caption("Validation watch signals", meta.get("validation_watch_signals"))

                status = str(meta.get("validation_status") or "normal")
                if status == "caution":
                    st.warning(
                        "Benchmark-relative drawdown 또는 rolling underperformance 진단이 높게 나왔습니다. "
                        "실전 승격 전 재검토가 필요한 상태로 보는 편이 맞습니다."
                    )
                elif status == "watch":
                    st.info(
                        "일부 benchmark-relative validation 지표가 watch 상태입니다. "
                        "추가 구간 검증이나 contract robustness 확인이 권장됩니다."
                    )

        if meta.get("rolling_review_status") or meta.get("out_of_sample_review_status"):
            with _section_header(
                "최근 구간 / Out-of-Sample Review",
                "최근 구간과 전후반 구간을 따로 봐서, 특정 시기 우연인지 아니면 비교적 꾸준한지 확인하는 섹션입니다.",
            ):
                review_cols = st.columns(5, gap="small")
                review_cols[0].metric("Rolling Review", _review_status_value_to_label(meta.get("rolling_review_status")))
                review_cols[1].metric("Rolling Window", str(meta.get("rolling_review_window_label") or "-"))
                if meta.get("rolling_review_recent_excess_return") is not None:
                    review_cols[2].metric("Recent Excess", f"{float(meta.get('rolling_review_recent_excess_return')):.2%}")
                if meta.get("rolling_review_recent_drawdown_gap") is not None:
                    review_cols[3].metric("Recent DD Gap", f"{float(meta.get('rolling_review_recent_drawdown_gap')):.2%}")
                review_cols[4].metric("OOS Review", _review_status_value_to_label(meta.get("out_of_sample_review_status")))

                split_cols = st.columns(3, gap="small")
                if meta.get("out_of_sample_in_sample_excess_return") is not None:
                    split_cols[0].metric("In-Sample Excess", f"{float(meta.get('out_of_sample_in_sample_excess_return')):.2%}")
                if meta.get("out_of_sample_out_sample_excess_return") is not None:
                    split_cols[1].metric("Out-Sample Excess", f"{float(meta.get('out_of_sample_out_sample_excess_return')):.2%}")
                if meta.get("out_of_sample_excess_change") is not None:
                    split_cols[2].metric("Excess Change", f"{float(meta.get('out_of_sample_excess_change')):.2%}")

                if meta.get("rolling_review_recent_start") is not None and meta.get("rolling_review_recent_end") is not None:
                    st.caption(
                        "Recent review window: "
                        f"`{meta.get('rolling_review_recent_start')}` -> `{meta.get('rolling_review_recent_end')}`"
                    )
                rolling_review_rationale = list(meta.get("rolling_review_rationale") or [])
                if rolling_review_rationale:
                    st.caption("Rolling review rationale: " + ", ".join(f"`{item}`" for item in rolling_review_rationale))
                if meta.get("out_of_sample_in_sample_start") is not None and meta.get("out_of_sample_out_sample_end") is not None:
                    st.caption(
                        "Split-period review: "
                        f"in-sample `{meta.get('out_of_sample_in_sample_start')}` -> `{meta.get('out_of_sample_in_sample_end')}`, "
                        f"out-sample `{meta.get('out_of_sample_out_sample_start')}` -> `{meta.get('out_of_sample_out_sample_end')}`"
                    )
                out_of_sample_review_rationale = list(meta.get("out_of_sample_review_rationale") or [])
                if out_of_sample_review_rationale:
                    st.caption("Out-of-sample rationale: " + ", ".join(f"`{item}`" for item in out_of_sample_review_rationale))

                if str(meta.get("rolling_review_status") or "").strip().lower() == "caution" or str(
                    meta.get("out_of_sample_review_status") or ""
                ).strip().lower() == "caution":
                    st.warning(
                        "최근 구간 또는 split-period review에서 caution이 잡혔습니다. "
                        "지금은 비중 확대보다 recent regime robustness review를 먼저 하는 편이 맞습니다."
                    )
                elif str(meta.get("rolling_review_status") or "").strip().lower() == "watch" or str(
                    meta.get("out_of_sample_review_status") or ""
                ).strip().lower() == "watch":
                    st.info(
                        "최근 구간 review는 완전히 깨지진 않았지만, current regime robustness를 조금 더 보수적으로 해석하는 편이 좋습니다."
                    )

        if (
            meta.get("benchmark_policy_status")
            or meta.get("liquidity_policy_status")
            or meta.get("validation_policy_status")
            or meta.get("guardrail_policy_status")
        ):
            with st.expander("세부 정책 기준 보기", expanded=False):
                st.caption(
                    "아래 항목은 승격 판단에 사용된 세부 정책 기준입니다. "
                    "평소에는 summary만 보고, 정책이 왜 `watch`나 `caution`인지 확인할 때만 펼쳐 보면 됩니다."
                )

                if meta.get("benchmark_policy_status"):
                    st.markdown("##### Benchmark Policy")
                    policy_cols = st.columns(5, gap="small")
                    policy_cols[0].metric("Policy Status", str(meta.get("benchmark_policy_status") or "normal").upper())
                    if meta.get("promotion_min_benchmark_coverage") is not None:
                        policy_cols[1].metric("Min Coverage", f"{float(meta.get('promotion_min_benchmark_coverage') or 0.0):.0%}")
                    if meta.get("benchmark_row_coverage") is not None:
                        policy_cols[2].metric("Actual Coverage", f"{float(meta.get('benchmark_row_coverage') or 0.0):.2%}")
                    if meta.get("promotion_min_net_cagr_spread") is not None:
                        policy_cols[3].metric("Min Net CAGR Spread", f"{float(meta.get('promotion_min_net_cagr_spread') or 0.0):.0%}")
                    if meta.get("net_cagr_spread") is not None:
                        policy_cols[4].metric("Actual Net CAGR Spread", f"{float(meta.get('net_cagr_spread') or 0.0):.2%}")
                    _render_value_list_caption("Benchmark policy signals", meta.get("benchmark_policy_watch_signals"))
                    policy_status = str(meta.get("benchmark_policy_status") or "normal").lower()
                    if policy_status == "caution":
                        st.warning("현재 benchmark policy 기준에서는 coverage 또는 상대 CAGR이 충분하지 않습니다. 승격 전 추가 검토가 필요한 상태입니다.")
                    elif policy_status == "watch":
                        st.info("Benchmark policy 기준에서 일부 watch 신호가 있습니다. 실전 승격 전 robustness 확인을 더 하는 편이 좋습니다.")

                if meta.get("liquidity_policy_status"):
                    st.markdown("##### Liquidity Policy")
                    liquidity_policy_cols = st.columns(4, gap="small")
                    liquidity_policy_cols[0].metric("Policy Status", str(meta.get("liquidity_policy_status") or "normal").upper())
                    if meta.get("promotion_min_liquidity_clean_coverage") is not None:
                        liquidity_policy_cols[1].metric("Min Clean Coverage", f"{float(meta.get('promotion_min_liquidity_clean_coverage') or 0.0):.0%}")
                    if meta.get("liquidity_clean_coverage") is not None:
                        liquidity_policy_cols[2].metric("Actual Clean Coverage", f"{float(meta.get('liquidity_clean_coverage') or 0.0):.2%}")
                    if meta.get("liquidity_excluded_active_rows") is not None:
                        liquidity_policy_cols[3].metric("Liquidity Excluded Rows", str(int(meta.get("liquidity_excluded_active_rows") or 0)))
                    _render_value_list_caption("Liquidity policy signals", meta.get("liquidity_policy_watch_signals"))
                    liquidity_policy_status = str(meta.get("liquidity_policy_status") or "normal").lower()
                    if liquidity_policy_status == "caution":
                        st.warning("현재 liquidity policy 기준에서는 유동성 제외가 너무 자주 발생했습니다. 실전 승격 전 후보군 또는 investability 계약을 다시 점검하는 편이 맞습니다.")
                    elif liquidity_policy_status == "watch":
                        st.info("Liquidity policy 기준에서 watch 신호가 있습니다. 유동성 제외 빈도와 후보군 구성을 한 번 더 검토하는 편이 좋습니다.")
                    elif liquidity_policy_status == "unavailable":
                        st.info("Liquidity policy는 현재 unavailable 상태입니다. 실전 승격 기준으로 보려면 `Min Avg Dollar Volume 20D` 필터를 함께 사용하는 편이 좋습니다.")

                if meta.get("validation_policy_status"):
                    st.markdown("##### Validation Policy")
                    validation_policy_cols = st.columns(5, gap="small")
                    validation_policy_cols[0].metric("Policy Status", str(meta.get("validation_policy_status") or "normal").upper())
                    if meta.get("promotion_max_underperformance_share") is not None:
                        validation_policy_cols[1].metric("Max Underperf Share", f"{float(meta.get('promotion_max_underperformance_share') or 0.0):.0%}")
                    if meta.get("rolling_underperformance_share") is not None:
                        validation_policy_cols[2].metric("Actual Underperf Share", f"{float(meta.get('rolling_underperformance_share') or 0.0):.2%}")
                    if meta.get("promotion_min_worst_rolling_excess_return") is not None:
                        validation_policy_cols[3].metric("Min Worst Excess", f"{float(meta.get('promotion_min_worst_rolling_excess_return') or 0.0):.0%}")
                    if meta.get("rolling_underperformance_worst_excess_return") is not None:
                        validation_policy_cols[4].metric("Actual Worst Excess", f"{float(meta.get('rolling_underperformance_worst_excess_return') or 0.0):.2%}")
                    _render_value_list_caption("Validation policy signals", meta.get("validation_policy_watch_signals"))
                    validation_policy_status = str(meta.get("validation_policy_status") or "normal").lower()
                    if validation_policy_status == "caution":
                        st.warning("현재 validation policy 기준에서는 rolling underperformance robustness가 충분하지 않습니다. 실전 승격 전 계약을 더 보수적으로 보는 편이 맞습니다.")
                    elif validation_policy_status == "watch":
                        st.info("Validation policy 기준에서 watch 신호가 있습니다. 추가 구간 robustness 검증을 더 하는 편이 좋습니다.")
                    elif validation_policy_status == "unavailable":
                        st.info("Validation policy는 현재 unavailable 상태입니다. aligned benchmark validation history가 있어야 승격 기준으로 해석할 수 있습니다.")

                if meta.get("guardrail_policy_status"):
                    st.markdown("##### Portfolio Guardrail Policy")
                    guardrail_policy_cols = st.columns(5, gap="small")
                    guardrail_policy_cols[0].metric("Policy Status", str(meta.get("guardrail_policy_status") or "normal").upper())
                    if meta.get("promotion_max_strategy_drawdown") is not None:
                        guardrail_policy_cols[1].metric("Max Strategy DD", f"{float(meta.get('promotion_max_strategy_drawdown') or 0.0):.0%}")
                    if meta.get("strategy_max_drawdown") is not None:
                        guardrail_policy_cols[2].metric("Actual Strategy DD", f"{float(meta.get('strategy_max_drawdown') or 0.0):.2%}")
                    if meta.get("promotion_max_drawdown_gap_vs_benchmark") is not None:
                        guardrail_policy_cols[3].metric("Max DD Gap", f"{float(meta.get('promotion_max_drawdown_gap_vs_benchmark') or 0.0):.0%}")
                    if meta.get("drawdown_gap_vs_benchmark") is not None:
                        guardrail_policy_cols[4].metric("Actual DD Gap", f"{float(meta.get('drawdown_gap_vs_benchmark') or 0.0):.2%}")
                    _render_value_list_caption("Guardrail policy signals", meta.get("guardrail_policy_watch_signals"))
                    guardrail_policy_status = str(meta.get("guardrail_policy_status") or "normal").lower()
                    if guardrail_policy_status == "caution":
                        st.warning("현재 portfolio guardrail policy 기준에서는 낙폭 방어가 충분하지 않습니다. 실전 승격 전 drawdown contract를 더 보수적으로 보는 편이 맞습니다.")
                    elif guardrail_policy_status == "watch":
                        st.info("Portfolio guardrail policy 기준에서 watch 신호가 있습니다. 최대 낙폭과 benchmark 대비 drawdown gap을 한 번 더 점검하는 편이 좋습니다.")
                    elif guardrail_policy_status == "unavailable":
                        st.info("Portfolio guardrail policy는 현재 unavailable 상태입니다. 실전 승격 기준으로 보려면 usable benchmark drawdown history가 필요합니다.")

        if benchmark_chart_df is not None and result_df is not None:
            with _section_header(
                "Strategy vs Benchmark Chart",
                "전략의 net 곡선과 benchmark reference curve를 겹쳐서 봅니다. 최근 구간에서 벌어지는 방향을 읽을 때 유용합니다.",
            ):
                strategy_line = (
                    bundle["chart_df"][["Date", "Total Balance"]]
                    .rename(columns={"Total Balance": bundle["strategy_name"]})
                    .set_index("Date")
                )
                benchmark_line = (
                    benchmark_chart_df[["Date", "Benchmark Total Balance"]]
                    .rename(
                        columns={
                            "Benchmark Total Balance": str(
                                meta.get("benchmark_label") or meta.get("benchmark_ticker") or "Benchmark"
                            )
                        }
                    )
                    .set_index("Date")
                )
                overlay_df = pd.concat([strategy_line, benchmark_line], axis=1).sort_index()
                _render_compare_altair_chart(
                    overlay_df,
                    title="Net Strategy vs Benchmark",
                    y_title="Total Balance",
                    show_end_markers=True,
                )
                st.caption("전략은 비용 반영 후 `net` 곡선이고, benchmark는 비용을 반영하지 않은 단순 reference curve입니다.")

    with execution_tab:
        st.caption(
            "이 섹션은 이 전략을 실제로 운용할 때 드는 부담을 봅니다. "
            "가격/유동성/turnover/비용/ETF 운용 가능성, 그리고 실제 방어 규칙이 여기에 모여 있습니다."
        )

        with _section_header(
            "실행 계약 요약",
            "가격, 이력, 유동성, turnover, 비용처럼 실제 운용 시 바로 영향을 주는 기본 조건을 보여줍니다.",
        ):
            top_cols = st.columns(6, gap="small")
            top_cols[0].metric("Minimum Price", f"{float(meta.get('min_price_filter') or 0.0):.2f}")
            top_cols[1].metric("Minimum History", f"{int(meta.get('min_history_months_filter') or 0)}M")
            top_cols[2].metric("Min Avg Dollar Volume 20D", f"{float(meta.get('min_avg_dollar_volume_20d_m_filter') or 0.0):.1f}M")
            top_cols[3].metric("Transaction Cost", f"{float(meta.get('transaction_cost_bps') or 0.0):.1f} bps")
            top_cols[4].metric("Avg Turnover", f"{float(meta.get('avg_turnover') or 0.0):.2%}")
            top_cols[5].metric("Estimated Cost Total", f"{float(meta.get('estimated_cost_total') or 0.0):,.1f}")
            if meta.get("liquidity_excluded_total") is not None:
                st.caption(
                    "Liquidity excluded candidates: "
                    f"`{int(meta.get('liquidity_excluded_total') or 0)}` total, "
                    f"`{int(meta.get('liquidity_excluded_active_rows') or 0)}` rows."
                )
            if meta.get("liquidity_clean_coverage") is not None:
                st.caption("Liquidity clean coverage on rebalance rows: " f"`{float(meta.get('liquidity_clean_coverage') or 0.0):.2%}`")

        if meta.get("liquidity_policy_status") or meta.get("promotion_min_liquidity_clean_coverage") is not None:
            with _section_header(
                "Liquidity Policy",
                "유동성 때문에 실제 운용 해석이 가능한지 보는 섹션입니다. "
                "특히 `unavailable`이면 현재 설정만으로는 유동성 검증을 아예 하지 못하고 있다는 뜻입니다.",
            ):
                liquidity_policy_status = str(meta.get("liquidity_policy_status") or "unavailable").lower()
                liquidity_policy_cols = st.columns(5, gap="small")
                liquidity_policy_cols[0].metric("Policy Status", liquidity_policy_status.upper())
                liquidity_policy_cols[1].metric(
                    "Min Avg Dollar Volume 20D",
                    f"{float(meta.get('min_avg_dollar_volume_20d_m_filter') or 0.0):.1f}M",
                )
                liquidity_policy_cols[2].metric(
                    "Min Clean Coverage",
                    f"{float(meta.get('promotion_min_liquidity_clean_coverage') or 0.0):.0%}",
                )
                liquidity_policy_cols[3].metric(
                    "Actual Clean Coverage",
                    (
                        f"{float(meta.get('liquidity_clean_coverage')):.2%}"
                        if meta.get("liquidity_clean_coverage") is not None
                        else "-"
                    ),
                )
                liquidity_policy_cols[4].metric(
                    "Liquidity Excluded Rows",
                    str(int(meta.get("liquidity_excluded_active_rows") or 0)),
                )

                st.caption(
                    "`Min Avg Dollar Volume 20D`는 최근 20거래일 평균 거래대금 기준이고, "
                    "`Liquidity Clean Coverage`는 리밸런싱 시점 중 유동성 제외 없이 지나간 비율입니다."
                )

                liquidity_policy_signals = [
                    _liquidity_policy_signal_to_korean_label(item)
                    for item in list(meta.get("liquidity_policy_watch_signals") or [])
                ]
                _render_value_list_caption("Liquidity policy signals", liquidity_policy_signals)

                min_avg_dollar_volume = float(meta.get("min_avg_dollar_volume_20d_m_filter") or 0.0)
                clean_coverage = meta.get("liquidity_clean_coverage")

                if liquidity_policy_status == "normal":
                    st.success(
                        "현재 유동성 정책 기준에서는 특별한 blocker가 없습니다. "
                        "실전 해석에서 유동성 쪽은 비교적 안정적으로 통과한 상태입니다."
                    )
                elif liquidity_policy_status == "watch":
                    st.info(
                        "현재 유동성 정책은 watch 상태입니다. "
                        "당장 막히는 수준은 아니지만, 유동성 제외 빈도가 기준에 가까워서 후보군을 조금 더 점검하는 편이 좋습니다."
                    )
                elif liquidity_policy_status == "caution":
                    st.warning(
                        "현재 유동성 정책은 caution 상태입니다. "
                        "리밸런싱 시점에서 유동성 제외가 너무 자주 발생해 실전 승격을 바로 열기 어렵습니다."
                    )
                    st.info(
                        "먼저 `Min Avg Dollar Volume 20D` 기준을 확인하고, 거래가 얇은 종목이 자주 걸리는지 후보군을 다시 점검해보세요."
                    )
                elif liquidity_policy_status == "unavailable":
                    if min_avg_dollar_volume <= 0.0:
                        st.warning(
                            "현재는 `Min Avg Dollar Volume 20D`가 `0.0M`이라 유동성 정책을 실제로 판정하지 못했습니다."
                        )
                        st.info(
                            "해결 방법: `Advanced Inputs`에서 `Min Avg Dollar Volume 20D`를 `0`보다 큰 값으로 설정한 뒤 다시 실행하세요. "
                            "즉 지금은 유동성 필터를 꺼둔 상태라, 승격 판단용 liquidity review가 비활성화된 것입니다."
                        )
                    elif clean_coverage is None:
                        st.warning(
                            "유동성 필터 값은 있지만, `Liquidity Clean Coverage`가 계산되지 않아 정책 판단을 못 하고 있습니다."
                        )
                        st.info(
                            "해결 방법: 결과 데이터에 유동성 제외/coverage가 실제로 계산됐는지 확인하고, 필요하면 기간이나 universe contract를 다시 점검하세요."
                        )
                    else:
                        st.info(
                            "현재 설정만으로는 유동성 정책을 충분히 해석하기 어렵습니다. "
                            "유동성 필터 값과 clean coverage 계산 여부를 함께 확인하는 편이 좋습니다."
                        )

        if (
            meta.get("promotion_min_etf_aum_b") is not None
            or meta.get("promotion_max_bid_ask_spread_pct") is not None
            or meta.get("etf_operability_status")
        ):
            with _section_header(
                "ETF 운용 가능성",
                "ETF 전략에서만 보이는 항목입니다. 현재 시점 기준으로 ETF 규모와 bid-ask spread가 너무 불안정하지 않은지 확인합니다.",
            ):
                etf_cols = st.columns(5, gap="small")
                etf_cols[0].metric("Policy Status", str(meta.get("etf_operability_status") or "unavailable").upper())
                if meta.get("promotion_min_etf_aum_b") is not None:
                    etf_cols[1].metric("Min ETF AUM", f"${float(meta.get('promotion_min_etf_aum_b') or 0.0):.1f}B")
                if meta.get("promotion_max_bid_ask_spread_pct") is not None:
                    etf_cols[2].metric("Max Bid-Ask Spread", f"{float(meta.get('promotion_max_bid_ask_spread_pct') or 0.0):.2%}")
                if meta.get("etf_operability_clean_coverage") is not None:
                    etf_cols[3].metric("Clean Coverage", f"{float(meta.get('etf_operability_clean_coverage') or 0.0):.2%}")
                if meta.get("etf_operability_clean_pass_count") is not None:
                    etf_cols[4].metric("Clean Pass", f"{int(meta.get('etf_operability_clean_pass_count') or 0)} / {int(meta.get('etf_symbol_count') or 0)}")
                if meta.get("etf_operability_data_coverage") is not None:
                    st.caption(f"ETF operability data coverage: `{float(meta.get('etf_operability_data_coverage') or 0.0):.2%}`")
                if meta.get("etf_aum_pass_count") is not None or meta.get("etf_spread_pass_count") is not None:
                    st.caption(
                        "Pass counts: "
                        f"AUM `{int(meta.get('etf_aum_pass_count') or 0)}` / `{int(meta.get('etf_symbol_count') or 0)}`, "
                        f"Spread `{int(meta.get('etf_spread_pass_count') or 0)}` / `{int(meta.get('etf_symbol_count') or 0)}`"
                    )
                with st.expander("문제 ETF / 누락 데이터 보기", expanded=False):
                    _render_value_list_caption("AUM-below-policy ETF", meta.get("etf_aum_failed_symbols"))
                    _render_value_list_caption("Spread-above-policy ETF", meta.get("etf_spread_failed_symbols"))
                    _render_value_list_caption("Missing ETF operability fields", meta.get("etf_operability_missing_data_symbols"))
                    _render_value_list_caption("ETF operability signals", meta.get("etf_operability_watch_signals"))
                etf_status = str(meta.get("etf_operability_status") or "unavailable").lower()
                if etf_status == "caution":
                    st.warning("현재 ETF operability policy 기준에서는 자산 규모나 bid-ask spread가 충분히 안정적이지 않습니다. 실전 승격 전 ETF universe를 다시 점검하는 편이 맞습니다.")
                elif etf_status == "watch":
                    st.info("ETF operability policy 기준에서 일부 watch 신호가 있습니다. 현재 AUM과 bid-ask spread를 한 번 더 점검하는 편이 좋습니다.")
                elif etf_status == "unavailable":
                    st.info("ETF operability policy는 현재 unavailable 상태입니다. ETF asset profile을 새로 수집한 뒤 다시 해석하는 편이 맞습니다.")

        if meta.get("underperformance_guardrail_enabled") or meta.get("drawdown_guardrail_enabled"):
            with _section_header(
                "실제 방어 규칙",
                "경고만 보여주는 것이 아니라, 조건이 깨지면 실제 rebalance를 더 보수적으로 만들 수 있는 규칙입니다.",
            ):
                if meta.get("underperformance_guardrail_enabled"):
                    guardrail_cols = st.columns(4, gap="small")
                    guardrail_cols[0].metric("Underperformance Guardrail", "ON")
                    guardrail_cols[1].metric(
                        "Window",
                        f"{int(meta.get('underperformance_guardrail_window_months') or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS)}M",
                    )
                    guardrail_cols[2].metric(
                        "Threshold",
                        f"{float(meta.get('underperformance_guardrail_threshold') or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD):.0%}",
                    )
                    guardrail_cols[3].metric("Trigger Count", str(int(meta.get("underperformance_guardrail_trigger_count") or 0)))
                    if meta.get("underperformance_guardrail_trigger_share") is not None:
                        st.caption(
                            "Guardrail triggered on "
                            f"`{float(meta.get('underperformance_guardrail_trigger_share')):.2%}` of recorded rows."
                        )
                if meta.get("drawdown_guardrail_enabled"):
                    drawdown_guardrail_cols = st.columns(5, gap="small")
                    drawdown_guardrail_cols[0].metric("Drawdown Guardrail", "ON")
                    drawdown_guardrail_cols[1].metric(
                        "Window",
                        f"{int(meta.get('drawdown_guardrail_window_months') or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS)}M",
                    )
                    drawdown_guardrail_cols[2].metric(
                        "Strategy DD Threshold",
                        f"{float(meta.get('drawdown_guardrail_strategy_threshold') or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD):.0%}",
                    )
                    drawdown_guardrail_cols[3].metric(
                        "DD Gap Threshold",
                        f"{float(meta.get('drawdown_guardrail_gap_threshold') or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD):.0%}",
                    )
                    drawdown_guardrail_cols[4].metric("Trigger Count", str(int(meta.get("drawdown_guardrail_trigger_count") or 0)))
                    if meta.get("drawdown_guardrail_trigger_share") is not None:
                        st.caption(
                            "Drawdown guardrail triggered on "
                            f"`{float(meta.get('drawdown_guardrail_trigger_share')):.2%}` of recorded rows."
                        )

    with detail_tab:
        st.caption(
            "이 섹션은 원자료 확인용입니다. "
            "요약 판단은 앞의 세 탭에서 끝내고, 여기서는 세부 숫자나 표를 다시 확인할 때만 보시면 됩니다."
        )

        detail_cols: list[str] = []
        if result_df is not None and "Estimated Cost" in result_df.columns:
            with _section_header(
                "Cost Detail Preview",
                "비용이 실제로 어떻게 누적됐는지 확인하는 원자료 미리보기입니다.",
            ):
                detail_cols.append("Date")
                detail_cols.extend(
                    [
                        column
                        for column in [
                            "Gross Total Balance",
                            "Total Balance",
                            "Turnover",
                            "Estimated Cost",
                            "Cumulative Estimated Cost",
                        ]
                        if column in result_df.columns
                    ]
                )
                st.dataframe(result_df[detail_cols].head(12), use_container_width=True, hide_index=True)

        if benchmark_summary_df is not None:
            with _section_header(
                "Benchmark Summary",
                "benchmark와의 비교 결과를 표 형태로 다시 확인하는 상세 데이터입니다.",
            ):
                st.dataframe(benchmark_summary_df, use_container_width=True, hide_index=True)


def _build_compare_highlight_rows(bundles: list[dict]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for bundle in bundles:
        chart_df = bundle["chart_df"].copy().sort_values("Date")
        result_df = bundle["result_df"].copy().sort_values("Date")
        meta = bundle.get("meta") or {}
        universe_debug = meta.get("universe_debug") or {}
        high_df, low_df = _build_balance_extremes_tables(chart_df, top_n=1)
        best_df, worst_df = _build_period_extremes_tables(result_df, top_n=1)

        high_row = high_df.iloc[0] if not high_df.empty else {}
        low_row = low_df.iloc[0] if not low_df.empty else {}
        best_row = best_df.iloc[0] if not best_df.empty else {}
        worst_row = worst_df.iloc[0] if not worst_df.empty else {}
        end_row = chart_df.iloc[-1] if not chart_df.empty else {}

        rows.append(
            {
                "Strategy": bundle["strategy_name"],
                "Universe Contract": meta.get("universe_contract") or "-",
                "Dynamic Candidate Pool": meta.get("dynamic_candidate_count"),
                "Membership Avg": universe_debug.get("avg_membership_count"),
                "Min Price": meta.get("min_price_filter"),
                "Min History (M)": meta.get("min_history_months_filter"),
                "Min ADV20D ($M)": meta.get("min_avg_dollar_volume_20d_m_filter"),
                "Cost (bps)": meta.get("transaction_cost_bps"),
                "Min ETF AUM ($B)": meta.get("promotion_min_etf_aum_b"),
                "Max Spread (%)": (
                    float(meta.get("promotion_max_bid_ask_spread_pct")) * 100.0
                    if meta.get("promotion_max_bid_ask_spread_pct") is not None
                    else None
                ),
                "Avg Turnover": meta.get("avg_turnover"),
                "Benchmark Contract": _benchmark_contract_value_to_label(meta.get("benchmark_contract")),
                "Benchmark": meta.get("benchmark_ticker") or meta.get("benchmark_label"),
                "ETF Operability": meta.get("etf_operability_status"),
                "Benchmark Policy": meta.get("benchmark_policy_status"),
                "Liquidity Policy": meta.get("liquidity_policy_status"),
                "Validation Policy": meta.get("validation_policy_status"),
                "Guardrail Policy": meta.get("guardrail_policy_status"),
                "Net CAGR Spread": meta.get("net_cagr_spread"),
                "Validation": meta.get("validation_status"),
                "Promotion": meta.get("promotion_decision"),
                "Shortlist": _shortlist_status_value_to_label(meta.get("shortlist_status")),
                "Probation": _probation_status_value_to_label(meta.get("probation_status")),
                "Monitoring": _monitoring_status_value_to_label(meta.get("monitoring_status")),
                "Deployment": _deployment_readiness_status_value_to_label(meta.get("deployment_readiness_status")),
                "Deploy Next": meta.get("deployment_readiness_next_step"),
                "Rolling Review": _review_status_value_to_label(meta.get("rolling_review_status")),
                "Recent Excess": meta.get("rolling_review_recent_excess_return"),
                "OOS Review": _review_status_value_to_label(meta.get("out_of_sample_review_status")),
                "OOS Excess": meta.get("out_of_sample_out_sample_excess_return"),
                "Shortlist Next": meta.get("shortlist_next_step"),
                "Guardrail Triggers": meta.get("underperformance_guardrail_trigger_count"),
                "DD Guardrail Triggers": meta.get("drawdown_guardrail_trigger_count"),
                "Strategy Max DD": meta.get("strategy_max_drawdown"),
                "Drawdown Gap": meta.get("drawdown_gap_vs_benchmark"),
                "Worst Rolling Excess": meta.get("rolling_underperformance_worst_excess_return"),
                "Membership Range": (
                    f"{int(universe_debug['min_membership_count'])} -> {int(universe_debug['max_membership_count'])}"
                    if universe_debug.get("min_membership_count") is not None
                    and universe_debug.get("max_membership_count") is not None
                    else "-"
                ),
                "High Date": high_row.get("Date"),
                "High Balance": high_row.get("Total Balance"),
                "Low Date": low_row.get("Date"),
                "Low Balance": low_row.get("Total Balance"),
                "End Date": end_row.get("Date"),
                "End Balance": end_row.get("Total Balance"),
                "Best Period Date": best_row.get("Date"),
                "Best Period Return": best_row.get("Total Return"),
                "Worst Period Date": worst_row.get("Date"),
                "Worst Period Return": worst_row.get("Total Return"),
            }
        )
    return pd.DataFrame(rows)


def _render_compare_altair_chart(
    compare_df: pd.DataFrame,
    *,
    title: str,
    y_title: str,
    show_end_markers: bool = False,
) -> None:
    long_df = (
        compare_df.reset_index()
        .melt(id_vars="Date", var_name="Strategy", value_name="Value")
        .dropna(subset=["Value"])
    )

    chart = (
        alt.Chart(long_df)
        .mark_line(point=True)
        .encode(
            x=alt.X("Date:T", title="Date"),
            y=alt.Y("Value:Q", title=y_title),
            color=alt.Color("Strategy:N", title="Strategy"),
            tooltip=[
                alt.Tooltip("Date:T", title="Date"),
                alt.Tooltip("Strategy:N", title="Strategy"),
                alt.Tooltip("Value:Q", title=y_title, format=",.3f"),
            ],
        )
        .properties(title=title, height=360)
    )

    if not show_end_markers:
        st.altair_chart(chart, use_container_width=True)
        return

    marker_df = long_df.sort_values("Date").groupby("Strategy", as_index=False).tail(1)
    end_points = (
        alt.Chart(marker_df)
        .mark_point(size=90, filled=True)
        .encode(
            x="Date:T",
            y="Value:Q",
            color=alt.Color("Strategy:N", legend=None),
            tooltip=[
                alt.Tooltip("Date:T", title="End Date"),
                alt.Tooltip("Strategy:N", title="Strategy"),
                alt.Tooltip("Value:Q", title=y_title, format=",.3f"),
            ],
        )
    )
    end_labels = (
        alt.Chart(marker_df)
        .mark_text(align="left", dx=8, dy=-8, fontSize=11)
        .encode(
            x="Date:T",
            y="Value:Q",
            text="Strategy:N",
            color=alt.Color("Strategy:N", legend=None),
        )
    )
    st.altair_chart(chart + end_points + end_labels, use_container_width=True)


def _render_stacked_component_chart(
    component_df: pd.DataFrame,
    *,
    title: str,
    y_title: str,
    percent: bool = False,
) -> None:
    long_df = (
        component_df.reset_index()
        .rename(columns={"index": "Date"})
        .melt(id_vars="Date", var_name="Strategy", value_name="Value")
        .dropna(subset=["Value"])
    )

    tooltip_format = ".2%" if percent else ",.1f"
    y_axis_format = "%" if percent else ",.0f"

    chart = (
        alt.Chart(long_df)
        .mark_area()
        .encode(
            x=alt.X("Date:T", title="Date"),
            y=alt.Y("Value:Q", title=y_title, stack="zero", axis=alt.Axis(format=y_axis_format)),
            color=alt.Color("Strategy:N", title="Strategy"),
            tooltip=[
                alt.Tooltip("Date:T", title="Date"),
                alt.Tooltip("Strategy:N", title="Strategy"),
                alt.Tooltip("Value:Q", title=y_title, format=tooltip_format),
            ],
        )
        .properties(height=360, title=title)
    )
    st.altair_chart(chart, use_container_width=True)


def _render_compare_results() -> None:
    error = st.session_state.backtest_compare_error
    error_kind = st.session_state.backtest_compare_error_kind
    bundles = st.session_state.backtest_compare_bundles

    if error:
        if error_kind == "input":
            st.warning(error)
        elif error_kind == "data":
            st.error(error)
            st.caption("Hint: compare mode also depends on DB-backed OHLCV being present for each strategy universe.")
        else:
            st.error(error)

    if not bundles:
        return

    summary_df = pd.concat([bundle["summary_df"] for bundle in bundles], ignore_index=True)
    summary_df = summary_df.sort_values("End Balance", ascending=False).reset_index(drop=True)
    highlight_df = _build_compare_highlight_rows(bundles)

    balance_view = _build_balance_compare_view(bundles)
    drawdown_view = _build_drawdown_compare_view(bundles)
    return_view = _build_total_return_compare_view(bundles)

    st.markdown("### Strategy Comparison")
    st.caption("The first compare view focuses on strategy-to-strategy readability: one summary table, one overlay equity chart, and one overlay drawdown chart.")
    if any((bundle.get("meta") or {}).get("universe_contract") == HISTORICAL_DYNAMIC_PIT_UNIVERSE for bundle in bundles):
        st.info(
            "This compare run includes `Historical Dynamic PIT Universe` strategies. "
            "In Phase 10 first pass, annual strict strategies rebuild approximate rebalance-date membership, so "
            "`Dynamic Candidate Pool`, `Membership Avg`, and `Membership Range` help explain why static and dynamic results diverge."
        )

    summary_tab, balance_tab, drawdown_tab, return_tab, highlights_tab, focus_tab, meta_tab = st.tabs(
        ["Summary Compare", "Equity Overlay", "Drawdown Overlay", "Return Overlay", "Strategy Highlights", "Focused Strategy", "Execution Meta"]
    )

    with summary_tab:
        st.dataframe(summary_df, use_container_width=True)

    with balance_tab:
        _render_compare_altair_chart(
            balance_view,
            title="Equity Curve Overlay",
            y_title="Total Balance",
            show_end_markers=True,
        )
        st.caption("Sparse strategies such as GTAA can have fewer rebalance dates than monthly strategies. Points are shown so those paths remain visible, and end markers label the latest position of each strategy.")

    with drawdown_tab:
        _render_compare_altair_chart(
            drawdown_view,
            title="Drawdown Overlay",
            y_title="Drawdown",
            show_end_markers=True,
        )
        st.caption("Overlay drawdown curves make downside behavior easier to compare than end-balance alone. End markers make the latest drawdown state easier to read.")

    with return_tab:
        _render_compare_altair_chart(
            return_view,
            title="Total Return Overlay",
            y_title="Total Return",
            show_end_markers=True,
        )
        st.caption("This view helps compare period-by-period aggressiveness and recovery, not just end balance. End markers show the current total-return position of each strategy.")

    with highlights_tab:
        st.caption("This table is a compact compare-level summary of each strategy's high / low / end state plus best / worst period.")
        st.dataframe(highlight_df, use_container_width=True, hide_index=True)

    with focus_tab:
        strategy_names = [bundle["strategy_name"] for bundle in bundles]
        focus_default = summary_df.iloc[0]["Name"] if "Name" in summary_df.columns and not summary_df.empty else strategy_names[0]
        focused_strategy = st.selectbox(
            "Focused Strategy",
            options=strategy_names,
            index=strategy_names.index(focus_default) if focus_default in strategy_names else 0,
            key="compare_focus_strategy",
            help="Overlay chart는 전체 비교용이고, 여기서는 선택한 전략 하나를 자세히 읽습니다.",
        )
        focused_bundle = next(bundle for bundle in bundles if bundle["strategy_name"] == focused_strategy)
        focused_result_df = focused_bundle["result_df"]
        focused_chart_df = focused_bundle["chart_df"]

        st.caption("선택한 전략 하나에 대해 high / low / best / worst period를 더 자세히 확인할 수 있습니다.")
        _render_summary_metrics(focused_bundle["summary_df"])
        _render_balance_chart_with_markers(
            focused_chart_df,
            result_df=focused_result_df,
            title=f"{focused_strategy} Equity Curve",
        )

        high_df, low_df = _build_balance_extremes_tables(focused_chart_df, top_n=3)
        best_df, worst_df = _build_period_extremes_tables(focused_result_df, top_n=3)

        upper_left, upper_right = st.columns(2, gap="large")
        with upper_left:
            st.markdown("##### Top 3 Balance Highs")
            st.dataframe(high_df, use_container_width=True, hide_index=True)
        with upper_right:
            st.markdown("##### Top 3 Balance Lows")
            st.dataframe(low_df, use_container_width=True, hide_index=True)

        lower_left, lower_right = st.columns(2, gap="large")
        with lower_left:
            st.markdown("##### Top 3 Best Periods")
            st.dataframe(best_df, use_container_width=True, hide_index=True)
        with lower_right:
            st.markdown("##### Top 3 Worst Periods")
            st.dataframe(worst_df, use_container_width=True, hide_index=True)

        if focused_bundle["meta"].get("strategy_key") in {
            "quality_snapshot",
            "quality_snapshot_strict_annual",
            "quality_snapshot_strict_quarterly_prototype",
            "value_snapshot_strict_annual",
            "value_snapshot_strict_quarterly_prototype",
            "quality_value_snapshot_strict_annual",
            "quality_value_snapshot_strict_quarterly_prototype",
        }:
            st.divider()
            st.markdown("##### Selection Interpretation")
            _render_snapshot_selection_history(
                focused_result_df,
                strategy_name=focused_bundle["strategy_name"],
                factor_names=(focused_bundle["meta"].get("quality_factors") or []) + [
                    name for name in (focused_bundle["meta"].get("value_factors") or [])
                    if name not in (focused_bundle["meta"].get("quality_factors") or [])
                ],
                snapshot_mode=focused_bundle["meta"].get("snapshot_mode"),
                snapshot_source=focused_bundle["meta"].get("snapshot_source"),
            )

        if focused_bundle["meta"].get("real_money_hardening"):
            st.divider()
            st.markdown("##### Real-Money Contract")
            _render_real_money_details(focused_bundle)

    with meta_tab:
        meta_rows = []
        for bundle in bundles:
            meta = bundle["meta"]
            meta_rows.append(
                {
                    "strategy": bundle["strategy_name"],
                    "tickers": ", ".join(meta["tickers"]),
                    "start": meta["start"],
                    "end": meta["end"],
                    "timeframe": meta["timeframe"],
                    "option": meta["option"],
                    "rebalance_interval": meta.get("rebalance_interval"),
                    "top": meta.get("top"),
                    "min_price_filter": meta.get("min_price_filter"),
                    "min_history_months_filter": meta.get("min_history_months_filter"),
                    "min_avg_dollar_volume_20d_m_filter": meta.get("min_avg_dollar_volume_20d_m_filter"),
                    "transaction_cost_bps": meta.get("transaction_cost_bps"),
                    "promotion_min_etf_aum_b": meta.get("promotion_min_etf_aum_b"),
                    "promotion_max_bid_ask_spread_pct": meta.get("promotion_max_bid_ask_spread_pct"),
                    "benchmark_ticker": meta.get("benchmark_ticker"),
                    "etf_operability_status": meta.get("etf_operability_status"),
                    "promotion_min_benchmark_coverage": meta.get("promotion_min_benchmark_coverage"),
                    "promotion_min_net_cagr_spread": meta.get("promotion_min_net_cagr_spread"),
                    "promotion_min_liquidity_clean_coverage": meta.get("promotion_min_liquidity_clean_coverage"),
                    "promotion_max_underperformance_share": meta.get("promotion_max_underperformance_share"),
                    "promotion_min_worst_rolling_excess_return": meta.get("promotion_min_worst_rolling_excess_return"),
                    "promotion_max_strategy_drawdown": meta.get("promotion_max_strategy_drawdown"),
                    "promotion_max_drawdown_gap_vs_benchmark": meta.get("promotion_max_drawdown_gap_vs_benchmark"),
                    "strategy_family": meta.get("strategy_family"),
                    "shortlist_status": meta.get("shortlist_status"),
                    "shortlist_next_step": meta.get("shortlist_next_step"),
                    "probation_status": meta.get("probation_status"),
                    "probation_stage": meta.get("probation_stage"),
                    "probation_review_frequency": meta.get("probation_review_frequency"),
                    "probation_next_step": meta.get("probation_next_step"),
                    "monitoring_status": meta.get("monitoring_status"),
                    "monitoring_review_frequency": meta.get("monitoring_review_frequency"),
                    "monitoring_next_step": meta.get("monitoring_next_step"),
                    "deployment_readiness_status": meta.get("deployment_readiness_status"),
                    "deployment_readiness_next_step": meta.get("deployment_readiness_next_step"),
                    "deployment_check_pass_count": meta.get("deployment_check_pass_count"),
                    "deployment_check_watch_count": meta.get("deployment_check_watch_count"),
                    "deployment_check_fail_count": meta.get("deployment_check_fail_count"),
                    "rolling_review_status": meta.get("rolling_review_status"),
                    "rolling_review_window_label": meta.get("rolling_review_window_label"),
                    "rolling_review_recent_excess_return": meta.get("rolling_review_recent_excess_return"),
                    "out_of_sample_review_status": meta.get("out_of_sample_review_status"),
                    "out_of_sample_out_sample_excess_return": meta.get("out_of_sample_out_sample_excess_return"),
                    "underperformance_guardrail_enabled": meta.get("underperformance_guardrail_enabled"),
                    "underperformance_guardrail_window_months": meta.get("underperformance_guardrail_window_months"),
                    "underperformance_guardrail_threshold": meta.get("underperformance_guardrail_threshold"),
                    "drawdown_guardrail_enabled": meta.get("drawdown_guardrail_enabled"),
                    "drawdown_guardrail_window_months": meta.get("drawdown_guardrail_window_months"),
                    "drawdown_guardrail_strategy_threshold": meta.get("drawdown_guardrail_strategy_threshold"),
                    "drawdown_guardrail_gap_threshold": meta.get("drawdown_guardrail_gap_threshold"),
                    "avg_turnover": meta.get("avg_turnover"),
                    "trend_filter": (
                        f"MA{meta.get('trend_filter_window', STRICT_TREND_FILTER_DEFAULT_WINDOW)}"
                        if meta.get("trend_filter_enabled")
                        else "off"
                    ),
                    "vol_window": meta.get("vol_window"),
                    "preset_name": meta["preset_name"],
                }
            )
        st.dataframe(pd.DataFrame(meta_rows), use_container_width=True)


def _build_weighted_portfolio_bundle(
    *,
    bundles: list[dict[str, Any]],
    weights_percent: list[float],
    date_policy: str,
    portfolio_name: str | None = None,
    portfolio_id: str | None = None,
    source_kind: str = "weighted_builder",
) -> dict[str, Any]:
    strategy_names = [bundle["strategy_name"] for bundle in bundles]
    total_weight = sum(float(weight) for weight in weights_percent)
    if total_weight <= 0:
        raise ValueError("At least one strategy weight must be greater than zero.")

    normalized_weights = [float(weight) / total_weight for weight in weights_percent]
    combined_result = make_monthly_weighted_portfolio(
        dfs=[bundle["result_df"] for bundle in bundles],
        ratios=weights_percent,
        names=strategy_names,
        date_policy=date_policy,
    )
    result_name = f"Saved Portfolio: {portfolio_name}" if portfolio_name else "Weighted Portfolio"
    weighted_bundle = build_backtest_result_bundle(
        combined_result,
        strategy_name=result_name,
        strategy_key="weighted_portfolio",
        input_params={
            "tickers": strategy_names,
            "start": bundles[0]["meta"]["start"],
            "end": bundles[0]["meta"]["end"],
            "timeframe": bundles[0]["meta"]["timeframe"],
            "option": bundles[0]["meta"]["option"],
            "universe_mode": "strategy_mix",
            "preset_name": "weighted_builder",
        },
        execution_mode="db",
        data_mode="db_backed_composite",
        summary_freq="M",
        warnings=[],
    )
    contribution_amount_df, contribution_share_df = _build_monthly_component_balance_views(
        bundles,
        strategy_names=strategy_names,
        weights=normalized_weights,
        date_policy=date_policy,
    )
    weighted_bundle["component_contribution_amount_df"] = contribution_amount_df
    weighted_bundle["component_contribution_share_df"] = contribution_share_df
    weighted_bundle["component_input_weights"] = [float(weight) for weight in weights_percent]
    weighted_bundle["component_weights"] = normalized_weights
    weighted_bundle["component_strategy_names"] = strategy_names
    weighted_bundle["date_policy"] = date_policy
    weighted_bundle["meta"] = dict(weighted_bundle.get("meta") or {})
    weighted_bundle["meta"].update(
        {
            "portfolio_name": portfolio_name,
            "portfolio_id": portfolio_id,
            "portfolio_source_kind": source_kind,
            "selected_strategies": strategy_names,
            "date_policy": date_policy,
            "input_weights_percent": [float(weight) for weight in weights_percent],
            "normalized_weights": normalized_weights,
        }
    )
    return weighted_bundle


def _build_saved_portfolio_display_rows(saved_portfolios: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for item in saved_portfolios:
        compare_context = item.get("compare_context") or {}
        portfolio_context = item.get("portfolio_context") or {}
        strategy_names = list(portfolio_context.get("strategy_names") or compare_context.get("selected_strategies") or [])
        weights_percent = list(portfolio_context.get("weights_percent") or [])
        weight_pairs = [
            f"{strategy_name} {float(weight):.1f}%"
            for strategy_name, weight in zip(strategy_names, weights_percent)
        ]
        rows.append(
            {
                "Name": item.get("name"),
                "Updated At": item.get("updated_at") or item.get("saved_at"),
                "Strategies": ", ".join(strategy_names),
                "Weights": " | ".join(weight_pairs),
                "Date Policy": portfolio_context.get("date_policy"),
                "Period": f"{compare_context.get('start')} -> {compare_context.get('end')}",
                "Description": item.get("description"),
            }
        )
    return pd.DataFrame(rows)


def _run_saved_portfolio_record(record: dict[str, Any]) -> None:
    compare_context = dict(record.get("compare_context") or {})
    selected_strategies = list(compare_context.get("selected_strategies") or [])
    if not selected_strategies:
        raise BacktestInputError("Saved portfolio does not contain selected strategies.")

    strategy_overrides = compare_context.get("strategy_overrides") or {}
    bundles: list[dict[str, Any]] = []
    for strategy_name in selected_strategies:
        bundles.append(
            _run_compare_strategy(
                strategy_name,
                start=str(compare_context.get("start")),
                end=str(compare_context.get("end")),
                timeframe=str(compare_context.get("timeframe") or "1d"),
                option=str(compare_context.get("option") or "month_end"),
                overrides=_resolve_saved_portfolio_dynamic_inputs(
                    strategy_name=strategy_name,
                    override=dict(strategy_overrides.get(strategy_name) or {}),
                ),
            )
        )

    portfolio_context = dict(record.get("portfolio_context") or {})
    weights_percent = [float(weight) for weight in (portfolio_context.get("weights_percent") or [])]
    if len(weights_percent) != len(selected_strategies):
        raise BacktestInputError("Saved portfolio weight count does not match the saved strategy count.")

    weighted_bundle = _build_weighted_portfolio_bundle(
        bundles=bundles,
        weights_percent=weights_percent,
        date_policy=str(portfolio_context.get("date_policy") or "intersection"),
        portfolio_name=str(record.get("name") or ""),
        portfolio_id=str(record.get("portfolio_id") or ""),
        source_kind="saved_portfolio",
    )

    st.session_state.backtest_compare_bundles = bundles
    st.session_state.backtest_compare_error = None
    st.session_state.backtest_compare_error_kind = None
    st.session_state.backtest_weighted_bundle = weighted_bundle
    st.session_state.backtest_weighted_error = None
    st.session_state.backtest_requested_panel = "Compare & Portfolio Builder"

    append_backtest_run_history(
        bundle={
            "summary_df": pd.DataFrame(),
            "meta": {
                "strategy_key": "strategy_comparison",
                "execution_mode": "db",
                "data_mode": "db_backed_compare",
                "tickers": selected_strategies,
                "start": compare_context.get("start"),
                "end": compare_context.get("end"),
                "timeframe": compare_context.get("timeframe"),
                "option": compare_context.get("option"),
                "universe_mode": "strategy_compare",
                "preset_name": "saved_portfolio_compare",
            },
        },
        run_kind="strategy_compare",
        context={
            "selected_strategies": selected_strategies,
            "strategy_overrides": strategy_overrides,
            "saved_portfolio_id": record.get("portfolio_id"),
            "saved_portfolio_name": record.get("name"),
            "strategy_summaries": [
                row
                for bundle in bundles
                for row in json.loads(bundle["summary_df"].to_json(orient="records", date_format="iso"))
            ],
        },
    )
    append_backtest_run_history(
        bundle=weighted_bundle,
        run_kind="weighted_portfolio",
        context={
            "selected_strategies": selected_strategies,
            "date_policy": portfolio_context.get("date_policy"),
            "saved_portfolio_id": record.get("portfolio_id"),
            "saved_portfolio_name": record.get("name"),
        },
    )


def _render_weighted_portfolio_builder() -> None:
    bundles = st.session_state.backtest_compare_bundles
    if not bundles or len(bundles) < 2:
        return

    strategy_names = [bundle["strategy_name"] for bundle in bundles]
    default_weight = round(100 / len(strategy_names), 2)
    _apply_weighted_portfolio_prefill(strategy_names)

    st.markdown("### Weighted Portfolio Builder")
    st.caption("Combine already-compared strategies into one monthly weighted portfolio. This is the first UI path for cases like `Dual Momentum 50 + GTAA 50`.")

    with st.form("weighted_portfolio_builder_form", clear_on_submit=False):
        weight_cols = st.columns(min(len(strategy_names), 4))
        weights = []
        for idx, strategy_name in enumerate(strategy_names):
            with weight_cols[idx % len(weight_cols)]:
                weight = st.number_input(
                    f"{strategy_name} Weight (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=default_weight,
                    step=5.0,
                    key=f"weight_{strategy_name}",
                )
                weights.append(weight)

        date_policy = st.selectbox(
            "Date Alignment",
            options=["intersection", "union"],
            index=0,
            help="`intersection` keeps only shared months across strategies. It is the safer first default for combined backtests.",
            key="weighted_portfolio_date_policy",
        )

        submitted = st.form_submit_button("Build Weighted Portfolio", use_container_width=True)

    if not submitted:
        weighted_bundle = st.session_state.backtest_weighted_bundle
        if weighted_bundle:
            _render_weighted_portfolio_result(weighted_bundle)
        return

    total_weight = sum(weights)
    if total_weight <= 0:
        st.session_state.backtest_weighted_error = "At least one strategy weight must be greater than zero."
        st.session_state.backtest_weighted_bundle = None
        st.error(st.session_state.backtest_weighted_error)
        return

    try:
        weighted_bundle = _build_weighted_portfolio_bundle(
            bundles=bundles,
            weights_percent=weights,
            date_policy=date_policy,
            source_kind="weighted_builder",
        )
    except Exception as exc:
        st.session_state.backtest_weighted_bundle = None
        st.session_state.backtest_weighted_error = f"Weighted portfolio build failed: {exc}"
        st.error(st.session_state.backtest_weighted_error)
        return

    st.session_state.backtest_weighted_bundle = weighted_bundle
    st.session_state.backtest_weighted_error = None
    append_backtest_run_history(
        bundle=weighted_bundle,
        run_kind="weighted_portfolio",
        context={"selected_strategies": strategy_names, "date_policy": date_policy},
    )
    st.success("Weighted portfolio created.")
    _render_weighted_portfolio_result(weighted_bundle)


def _render_saved_portfolio_workspace() -> None:
    st.markdown("### Saved Portfolios")
    st.caption("현재 compare 결과와 weighted portfolio 구성을 저장해두고, 나중에 다시 `Load Into Compare` 또는 `Run Saved Portfolio`로 이어갈 수 있습니다.")

    saved_notice = st.session_state.get("backtest_saved_portfolio_notice")
    if saved_notice:
        st.success(saved_notice)
        st.session_state.backtest_saved_portfolio_notice = None

    compare_bundles = st.session_state.backtest_compare_bundles
    weighted_bundle = st.session_state.backtest_weighted_bundle
    if compare_bundles and weighted_bundle:
        with st.expander("Save Current Weighted Portfolio", expanded=False):
            st.caption("현재 compare 결과 + weighted portfolio 구성(weight/date policy)을 저장합니다. 이후에는 저장된 포트폴리오를 바로 다시 실행하거나 compare 화면으로 불러와 수정할 수 있습니다.")
            with st.form("save_saved_portfolio_form", clear_on_submit=False):
                portfolio_name = st.text_input(
                    "Portfolio Name",
                    value="",
                    placeholder="예: Annual Strict Blend 60/40",
                    key="saved_portfolio_name_input",
                )
                portfolio_description = st.text_area(
                    "Description",
                    value="",
                    placeholder="이 포트폴리오를 어떻게 쓰려는지 간단히 메모합니다.",
                    key="saved_portfolio_description_input",
                )
                save_submitted = st.form_submit_button("Save Portfolio", use_container_width=True)
            if save_submitted:
                try:
                    record = save_saved_portfolio(
                        name=portfolio_name,
                        description=portfolio_description,
                        compare_context=_build_saved_portfolio_compare_context(compare_bundles),
                        portfolio_context=_build_saved_portfolio_context(
                            bundles=compare_bundles,
                            weighted_bundle=weighted_bundle,
                        ),
                        source_context={
                            "created_from": "weighted_portfolio_builder",
                            "source_strategy_names": [bundle["strategy_name"] for bundle in compare_bundles],
                        },
                    )
                    st.session_state.backtest_saved_portfolio_notice = (
                        f"저장된 포트폴리오 `{record.get('name')}`를 만들었습니다."
                    )
                    st.rerun()
                except Exception as exc:
                    st.error(f"Saved portfolio creation failed: {exc}")
    else:
        st.caption("먼저 compare를 실행하고 `Weighted Portfolio Builder`에서 결과를 만든 뒤 저장할 수 있습니다.")

    saved_portfolios = load_saved_portfolios(limit=100)
    if not saved_portfolios:
        st.info("저장된 포트폴리오가 아직 없습니다.")
        st.caption(f"Path: {SAVED_PORTFOLIO_FILE}")
        return

    st.caption(f"Path: {SAVED_PORTFOLIO_FILE}")
    st.dataframe(_build_saved_portfolio_display_rows(saved_portfolios), use_container_width=True, hide_index=True)

    record_labels = [
        f"{item.get('updated_at') or item.get('saved_at')} | {item.get('name')}"
        for item in saved_portfolios
    ]
    selected_label = st.selectbox(
        "Inspect Saved Portfolio",
        options=record_labels,
        index=0,
        key="saved_portfolio_selected_record",
    )
    selected_record = saved_portfolios[record_labels.index(selected_label)]

    compare_context = selected_record.get("compare_context") or {}
    portfolio_context = selected_record.get("portfolio_context") or {}
    detail_tabs = st.tabs(["Summary", "Compare Context", "Raw Record"])
    with detail_tabs[0]:
        st.json(
            {
                "portfolio_id": selected_record.get("portfolio_id"),
                "name": selected_record.get("name"),
                "description": selected_record.get("description"),
                "saved_at": selected_record.get("saved_at"),
                "updated_at": selected_record.get("updated_at"),
                "selected_strategies": compare_context.get("selected_strategies"),
                "weights_percent": portfolio_context.get("weights_percent"),
                "date_policy": portfolio_context.get("date_policy"),
                "period": f"{compare_context.get('start')} -> {compare_context.get('end')}",
            }
        )
    with detail_tabs[1]:
        left, right = st.columns(2, gap="large")
        with left:
            st.markdown("##### Compare Context")
            st.json(compare_context)
        with right:
            st.markdown("##### Portfolio Context")
            st.json(portfolio_context)
    with detail_tabs[2]:
        st.json(selected_record)

    action_cols = st.columns([0.24, 0.24, 0.20, 0.32], gap="small")
    with action_cols[0]:
        if st.button("Load Into Compare", key="saved_portfolio_load_into_compare", use_container_width=True):
            _queue_saved_portfolio_compare_prefill(selected_record)
            st.rerun()
    with action_cols[1]:
        if st.button("Run Saved Portfolio", key="saved_portfolio_run", use_container_width=True):
            try:
                with st.spinner("Running saved portfolio from stored compare context..."):
                    _run_saved_portfolio_record(selected_record)
                st.session_state.backtest_saved_portfolio_notice = (
                    f"저장된 포트폴리오 `{selected_record.get('name')}`를 다시 실행했습니다."
                )
                st.rerun()
            except Exception as exc:
                st.error(f"Saved portfolio run failed: {exc}")
    with action_cols[2]:
        if st.button("Delete", key="saved_portfolio_delete", use_container_width=True):
            if delete_saved_portfolio(str(selected_record.get("portfolio_id") or "")):
                st.session_state.backtest_saved_portfolio_notice = (
                    f"저장된 포트폴리오 `{selected_record.get('name')}`를 삭제했습니다."
                )
                st.rerun()
            else:
                st.error("Saved portfolio delete failed.")
    with action_cols[3]:
        st.caption(
            "`Load Into Compare`는 저장된 전략 조합/기간/weights를 비교 화면으로 다시 채웁니다. "
            "`Run Saved Portfolio`는 compare부터 weighted portfolio 결과까지 한 번에 다시 실행합니다."
        )


def _render_weighted_portfolio_result(bundle: dict) -> None:
    if st.session_state.backtest_weighted_error:
        st.error(st.session_state.backtest_weighted_error)

    st.markdown("#### Weighted Portfolio Result")
    _render_summary_metrics(bundle["summary_df"])

    result_df = bundle["result_df"]
    chart_df = bundle["chart_df"]
    contribution_amount_df = bundle.get("component_contribution_amount_df")
    contribution_share_df = bundle.get("component_contribution_share_df")
    component_input_weights = bundle.get("component_input_weights") or []
    component_weights = bundle.get("component_weights") or []
    component_strategy_names = bundle.get("component_strategy_names") or []
    meta = bundle.get("meta") or {}

    summary_tab, curve_tab, contribution_tab, balance_tab, periods_tab, table_tab, meta_tab = st.tabs(
        ["Summary", "Equity Curve", "Contribution", "Balance Extremes", "Period Extremes", "Result Table", "Meta"]
    )

    with summary_tab:
        st.dataframe(bundle["summary_df"], use_container_width=True)
    with curve_tab:
        _render_balance_chart_with_markers(
            chart_df,
            result_df=result_df,
            title="Weighted Portfolio Equity Curve",
        )
        st.caption("Weighted portfolio results reuse the same marker language as single-strategy runs.")
    with contribution_tab:
        st.caption("This view shows how each compared strategy contributes to the weighted portfolio over time under the current date-alignment rule.")
        if contribution_amount_df is None or contribution_share_df is None:
            st.info("Contribution views are not available for this weighted portfolio result.")
        else:
            weights_df = pd.DataFrame(
                {
                    "Strategy": component_strategy_names,
                    "Configured Weight (%)": component_input_weights or [round(float(weight) * 100.0, 2) for weight in component_weights],
                    "Normalized Weight": component_weights,
                }
            )
            end_share_row = contribution_share_df.iloc[-1].rename("Ending Share").reset_index()
            end_share_row.columns = ["Strategy", "Ending Share"]
            contribution_summary_df = weights_df.merge(end_share_row, on="Strategy", how="left")

            st.markdown("##### Weight Snapshot")
            st.dataframe(contribution_summary_df, use_container_width=True, hide_index=True)

            amount_chart_tab, share_chart_tab = st.tabs(["Contribution Amount", "Contribution Share"])
            with amount_chart_tab:
                title_col, help_col = st.columns([0.92, 0.08], gap="small")
                with title_col:
                    st.markdown("##### Contribution Amount")
                with help_col:
                    _render_inline_help_popover(
                        "Contribution Amount",
                        "Each layer shows how much of the weighted portfolio balance comes from that strategy at each month. It is an amount-based view, not a percentage view.",
                    )
                _render_stacked_component_chart(
                    contribution_amount_df,
                    title="Weighted Portfolio Contribution Amount",
                    y_title="Contribution Amount",
                    percent=False,
                )
                st.caption("Each layer shows the strategy's weighted contribution to total balance at each month.")
            with share_chart_tab:
                title_col, help_col = st.columns([0.92, 0.08], gap="small")
                with title_col:
                    st.markdown("##### Contribution Share")
                with help_col:
                    _render_inline_help_popover(
                        "Contribution Share",
                        "This normalizes contribution into percentage share of the total weighted portfolio balance. It helps compare relative influence between strategies over time.",
                    )
                _render_stacked_component_chart(
                    contribution_share_df,
                    title="Weighted Portfolio Contribution Share",
                    y_title="Contribution Share",
                    percent=True,
                )
                st.caption("This normalizes the same contribution view into percentage share of total portfolio balance.")
    with balance_tab:
        high_df, low_df = _build_balance_extremes_tables(chart_df, top_n=3)
        high_col, low_col = st.columns(2, gap="large")
        with high_col:
            st.markdown("##### Top 3 Balance Highs")
            st.dataframe(high_df, use_container_width=True, hide_index=True)
        with low_col:
            st.markdown("##### Top 3 Balance Lows")
            st.dataframe(low_df, use_container_width=True, hide_index=True)
    with periods_tab:
        best_df, worst_df = _build_period_extremes_tables(result_df, top_n=3)
        best_col, worst_col = st.columns(2, gap="large")
        with best_col:
            st.markdown("##### Top 3 Best Periods")
            st.dataframe(best_df, use_container_width=True, hide_index=True)
        with worst_col:
            st.markdown("##### Top 3 Worst Periods")
            st.dataframe(worst_df, use_container_width=True, hide_index=True)
    with table_tab:
        st.dataframe(result_df, use_container_width=True)
    with meta_tab:
        st.markdown("##### Portfolio Context")
        st.markdown(f"- `Portfolio Name`: `{meta.get('portfolio_name') or '-'}`")
        st.markdown(f"- `Portfolio ID`: `{meta.get('portfolio_id') or '-'}`")
        st.markdown(f"- `Source`: `{meta.get('portfolio_source_kind') or 'weighted_builder'}`")
        st.markdown(f"- `Date Policy`: `{meta.get('date_policy') or bundle.get('date_policy') or '-'}`")
        st.markdown(f"- `Selected Strategies`: `{', '.join(meta.get('selected_strategies') or component_strategy_names)}`")
        st.markdown(f"- `Input Weights (%)`: `{meta.get('input_weights_percent') or component_input_weights or []}`")
        st.json(meta)


def _build_backtest_history_rows(history: list[dict[str, Any]]) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []

    for item in history:
        summary = item.get("summary") or {}
        context = item.get("context") or {}
        strategy_name = summary.get("strategy_name") or item.get("strategy_key") or "Comparison"
        selected_strategies = context.get("selected_strategies", [])
        search_text = " ".join(
            [
                str(item.get("run_kind", "")),
                str(strategy_name),
                " ".join(item.get("tickers", [])),
                " ".join(selected_strategies),
                str(item.get("preset_name", "")),
            ]
        ).lower()

        rows.append(
            {
                "_record_index": len(records),
                "recorded_at": item.get("recorded_at"),
                "_recorded_at_dt": pd.to_datetime(item.get("recorded_at"), errors="coerce"),
                "run_kind": item.get("run_kind"),
                "strategy": strategy_name,
                "end_balance": summary.get("end_balance"),
                "cagr": summary.get("cagr"),
                "sharpe_ratio": summary.get("sharpe_ratio"),
                "drawdown": summary.get("maximum_drawdown"),
                "tickers": ", ".join(item.get("tickers", [])),
                "params": _summarize_params(item),
                "selected_strategies": ", ".join(selected_strategies),
                "_search_text": search_text,
            }
        )
        records.append(item)

    return pd.DataFrame(rows), records


def _format_history_record_label(record: dict[str, Any]) -> str:
    summary = record.get("summary") or {}
    context = record.get("context") or {}
    strategy_name = summary.get("strategy_name") or record.get("strategy_key") or "Comparison"
    recorded_at = record.get("recorded_at", "unknown")
    run_kind = record.get("run_kind", "unknown")
    selected = context.get("selected_strategies") or []
    if selected:
        return f"{recorded_at} | {run_kind} | {strategy_name} | {', '.join(selected)}"
    return f"{recorded_at} | {run_kind} | {strategy_name}"


def _history_strategy_display_name(record: dict[str, Any]) -> str:
    summary = record.get("summary") or {}
    return summary.get("strategy_name") or record.get("strategy_key") or "Unknown Strategy"


def _build_history_payload(record: dict[str, Any]) -> dict[str, Any] | None:
    strategy_key = record.get("strategy_key")
    if strategy_key not in {"equal_weight", "gtaa", "risk_parity_trend", "dual_momentum"}:
        if strategy_key not in {
            "quality_snapshot",
            "quality_snapshot_strict_annual",
            "quality_snapshot_strict_quarterly_prototype",
            "value_snapshot_strict_annual",
            "value_snapshot_strict_quarterly_prototype",
            "quality_value_snapshot_strict_annual",
            "quality_value_snapshot_strict_quarterly_prototype",
        }:
            return None

    payload = {
        "strategy_key": strategy_key,
        "tickers": record.get("tickers", []),
        "start": record.get("input_start"),
        "end": record.get("input_end"),
        "timeframe": record.get("timeframe") or "1d",
        "option": record.get("option") or "month_end",
        "universe_mode": record.get("universe_mode") or "manual_tickers",
        "preset_name": record.get("preset_name"),
    }

    if record.get("rebalance_interval") is not None:
        payload["rebalance_interval"] = int(record["rebalance_interval"])
    if record.get("top") is not None:
        payload["top"] = int(record["top"])
    if record.get("vol_window") is not None:
        payload["vol_window"] = int(record["vol_window"])
    if record.get("factor_freq") is not None:
        payload["factor_freq"] = record.get("factor_freq")
    if record.get("rebalance_freq") is not None:
        payload["rebalance_freq"] = record.get("rebalance_freq")
    if record.get("snapshot_mode") is not None:
        payload["snapshot_mode"] = record.get("snapshot_mode")
    if record.get("quality_factors") is not None:
        payload["quality_factors"] = list(record.get("quality_factors") or [])
    if record.get("value_factors") is not None:
        payload["value_factors"] = list(record.get("value_factors") or [])
    if record.get("trend_filter_enabled") is not None:
        payload["trend_filter_enabled"] = bool(record.get("trend_filter_enabled"))
    if record.get("trend_filter_window") is not None:
        payload["trend_filter_window"] = int(record.get("trend_filter_window") or STRICT_TREND_FILTER_DEFAULT_WINDOW)
    if record.get("market_regime_enabled") is not None:
        payload["market_regime_enabled"] = bool(record.get("market_regime_enabled"))
    if record.get("market_regime_window") is not None:
        payload["market_regime_window"] = int(record.get("market_regime_window") or STRICT_MARKET_REGIME_DEFAULT_WINDOW)
    if record.get("market_regime_benchmark") is not None:
        payload["market_regime_benchmark"] = record.get("market_regime_benchmark") or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK
    if record.get("underperformance_guardrail_enabled") is not None:
        payload["underperformance_guardrail_enabled"] = bool(record.get("underperformance_guardrail_enabled"))
    if record.get("underperformance_guardrail_window_months") is not None:
        payload["underperformance_guardrail_window_months"] = int(
            record.get("underperformance_guardrail_window_months") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
    if record.get("underperformance_guardrail_threshold") is not None:
        payload["underperformance_guardrail_threshold"] = float(
            record.get("underperformance_guardrail_threshold") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD
        )
    if record.get("drawdown_guardrail_enabled") is not None:
        payload["drawdown_guardrail_enabled"] = bool(record.get("drawdown_guardrail_enabled"))
    if record.get("drawdown_guardrail_window_months") is not None:
        payload["drawdown_guardrail_window_months"] = int(
            record.get("drawdown_guardrail_window_months") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
    if record.get("drawdown_guardrail_strategy_threshold") is not None:
        payload["drawdown_guardrail_strategy_threshold"] = float(
            record.get("drawdown_guardrail_strategy_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD
        )
    if record.get("drawdown_guardrail_gap_threshold") is not None:
        payload["drawdown_guardrail_gap_threshold"] = float(
            record.get("drawdown_guardrail_gap_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD
        )
    if record.get("score_lookback_months") is not None:
        payload["score_lookback_months"] = [int(value) for value in list(record.get("score_lookback_months") or [])]
    if record.get("score_return_columns") is not None:
        payload["score_return_columns"] = list(record.get("score_return_columns") or [])
    if record.get("score_weights") is not None:
        payload["score_weights"] = dict(record.get("score_weights") or {})
    if record.get("risk_off_mode") is not None:
        payload["risk_off_mode"] = record.get("risk_off_mode") or GTAA_DEFAULT_RISK_OFF_MODE
    if record.get("defensive_tickers") is not None:
        payload["defensive_tickers"] = list(record.get("defensive_tickers") or [])
    if record.get("crash_guardrail_enabled") is not None:
        payload["crash_guardrail_enabled"] = bool(record.get("crash_guardrail_enabled"))
    if record.get("crash_guardrail_drawdown_threshold") is not None:
        payload["crash_guardrail_drawdown_threshold"] = float(record.get("crash_guardrail_drawdown_threshold") or GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD)
    if record.get("crash_guardrail_lookback_months") is not None:
        payload["crash_guardrail_lookback_months"] = int(record.get("crash_guardrail_lookback_months") or GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS)
    if record.get("min_price_filter") is not None:
        payload["min_price_filter"] = float(record.get("min_price_filter") or 0.0)
    if record.get("min_history_months_filter") is not None:
        payload["min_history_months_filter"] = int(
            record.get("min_history_months_filter") or STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS
        )
    if record.get("min_avg_dollar_volume_20d_m_filter") is not None:
        payload["min_avg_dollar_volume_20d_m_filter"] = float(
            record.get("min_avg_dollar_volume_20d_m_filter") or STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M
        )
    if record.get("transaction_cost_bps") is not None:
        payload["transaction_cost_bps"] = float(record.get("transaction_cost_bps") or 0.0)
    if record.get("promotion_min_etf_aum_b") is not None:
        payload["promotion_min_etf_aum_b"] = float(record.get("promotion_min_etf_aum_b") or 0.0)
    if record.get("promotion_max_bid_ask_spread_pct") is not None:
        payload["promotion_max_bid_ask_spread_pct"] = float(
            record.get("promotion_max_bid_ask_spread_pct") or 0.0
        )
    if record.get("benchmark_contract") is not None:
        payload["benchmark_contract"] = str(
            record.get("benchmark_contract") or STRICT_DEFAULT_BENCHMARK_CONTRACT
        ).strip().lower()
    if record.get("benchmark_ticker") is not None:
        payload["benchmark_ticker"] = str(record.get("benchmark_ticker") or "").strip().upper() or ETF_REAL_MONEY_DEFAULT_BENCHMARK
    if record.get("promotion_min_benchmark_coverage") is not None:
        payload["promotion_min_benchmark_coverage"] = float(
            record.get("promotion_min_benchmark_coverage") or STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE
        )
    if record.get("promotion_min_net_cagr_spread") is not None:
        payload["promotion_min_net_cagr_spread"] = float(
            record.get("promotion_min_net_cagr_spread") or STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD
        )
    if record.get("promotion_min_liquidity_clean_coverage") is not None:
        payload["promotion_min_liquidity_clean_coverage"] = float(
            record.get("promotion_min_liquidity_clean_coverage") or STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE
        )
    if record.get("promotion_max_underperformance_share") is not None:
        payload["promotion_max_underperformance_share"] = float(
            record.get("promotion_max_underperformance_share") or STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE
        )
    if record.get("promotion_min_worst_rolling_excess_return") is not None:
        payload["promotion_min_worst_rolling_excess_return"] = float(
            record.get("promotion_min_worst_rolling_excess_return")
            or STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN
        )
    if record.get("promotion_max_strategy_drawdown") is not None:
        payload["promotion_max_strategy_drawdown"] = float(
            record.get("promotion_max_strategy_drawdown") or STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN
        )
    if record.get("promotion_max_drawdown_gap_vs_benchmark") is not None:
        payload["promotion_max_drawdown_gap_vs_benchmark"] = float(
            record.get("promotion_max_drawdown_gap_vs_benchmark")
            or STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK
        )
    if record.get("snapshot_source") is not None:
        payload["snapshot_source"] = record.get("snapshot_source")
    if record.get("universe_contract") is not None:
        payload["universe_contract"] = record.get("universe_contract")
    if record.get("dynamic_target_size") is not None:
        payload["dynamic_target_size"] = int(record.get("dynamic_target_size"))

    # GTAA stores cadence in rebalance_interval for history summarization; map it back.
    if strategy_key == "gtaa":
        payload["interval"] = int(record.get("rebalance_interval") or GTAA_DEFAULT_SIGNAL_INTERVAL)
    return payload


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


def _render_single_strategy_family_form(strategy_choice: str) -> None:
    variant_key = _single_family_variant_session_key(strategy_choice)
    variant_options = family_variant_options(strategy_choice)
    if not variant_key or not variant_options:
        return

    st.caption("이 카테고리 안에서 실행 variant를 선택합니다.")
    selected_variant = st.selectbox(
        f"{strategy_choice} Variant",
        options=variant_options,
        key=variant_key,
    )
    concrete_strategy_name = resolve_concrete_strategy_display_name(strategy_choice, selected_variant)

    if concrete_strategy_name == "Quality Snapshot":
        _render_quality_snapshot_form()
    elif concrete_strategy_name == "Quality Snapshot (Strict Annual)":
        _render_quality_snapshot_strict_annual_form()
    elif concrete_strategy_name == "Quality Snapshot (Strict Quarterly Prototype)":
        _render_quality_snapshot_strict_quarterly_prototype_form()
    elif concrete_strategy_name == "Value Snapshot (Strict Annual)":
        _render_value_snapshot_strict_annual_form()
    elif concrete_strategy_name == "Value Snapshot (Strict Quarterly Prototype)":
        _render_value_snapshot_strict_quarterly_prototype_form()
    elif concrete_strategy_name == "Quality + Value Snapshot (Strict Annual)":
        _render_quality_value_snapshot_strict_annual_form()
    elif concrete_strategy_name == "Quality + Value Snapshot (Strict Quarterly Prototype)":
        _render_quality_value_snapshot_strict_quarterly_prototype_form()


def _load_history_into_form(record: dict[str, Any]) -> bool:
    payload = _build_history_payload(record)
    strategy_key = record.get("strategy_key")
    strategy_name = _strategy_key_to_display_name(strategy_key)
    strategy_choice, strategy_variant = strategy_key_to_selection(strategy_key)
    if payload is None or strategy_name is None or strategy_choice is None:
        return False

    st.session_state.backtest_prefill_payload = payload
    st.session_state.backtest_prefill_pending = True
    st.session_state.backtest_prefill_notice = (
        f"히스토리에서 `{_family_strategy_summary_label(strategy_key) or strategy_name}` 입력값을 불러왔습니다."
    )
    st.session_state.backtest_prefill_strategy_choice = strategy_choice
    st.session_state.backtest_prefill_strategy_variant = strategy_variant
    st.session_state.backtest_requested_panel = "Single Strategy"
    return True


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
        lines.append(f"Benchmark: `{payload.get('benchmark_ticker')}`")
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


def _bundle_to_saved_strategy_override(bundle: dict[str, Any]) -> dict[str, Any]:
    meta = dict(bundle.get("meta") or {})
    strategy_name = bundle.get("strategy_name")

    if strategy_name == "Equal Weight":
        return {
            "tickers": list(meta.get("tickers") or EQUAL_WEIGHT_PRESETS["Dividend ETFs"]),
            "preset_name": meta.get("preset_name") or "Dividend ETFs",
            "universe_mode": meta.get("universe_mode") or "preset",
            "rebalance_interval": int(meta.get("rebalance_interval") or 12),
        }
    if strategy_name == "GTAA":
        return {
            "tickers": list(meta.get("tickers") or GTAA_DEFAULT_TICKERS),
            "preset_name": meta.get("preset_name") or "GTAA Universe",
            "universe_mode": meta.get("universe_mode") or "preset",
            "top": int(meta.get("top") or 3),
            "interval": int(meta.get("rebalance_interval") or GTAA_DEFAULT_SIGNAL_INTERVAL),
            "score_lookback_months": list(meta.get("score_lookback_months") or GTAA_DEFAULT_SCORE_LOOKBACK_MONTHS),
            "score_return_columns": list(meta.get("score_return_columns") or GTAA_SCORE_RETURN_COLUMNS),
            "score_weights": dict(meta.get("score_weights") or GTAA_DEFAULT_SCORE_WEIGHTS),
            "trend_filter_window": int(meta.get("trend_filter_window") or GTAA_DEFAULT_TREND_FILTER_WINDOW),
            "risk_off_mode": meta.get("risk_off_mode") or GTAA_DEFAULT_RISK_OFF_MODE,
            "defensive_tickers": list(meta.get("defensive_tickers") or GTAA_DEFAULT_DEFENSIVE_TICKERS),
            "market_regime_enabled": bool(meta.get("market_regime_enabled", False)),
            "market_regime_window": int(meta.get("market_regime_window") or STRICT_MARKET_REGIME_DEFAULT_WINDOW),
            "market_regime_benchmark": meta.get("market_regime_benchmark") or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
            "crash_guardrail_enabled": bool(meta.get("crash_guardrail_enabled", GTAA_DEFAULT_CRASH_GUARDRAIL_ENABLED)),
            "crash_guardrail_drawdown_threshold": float(meta.get("crash_guardrail_drawdown_threshold") or GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD),
            "crash_guardrail_lookback_months": int(meta.get("crash_guardrail_lookback_months") or GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS),
            "min_price_filter": float(meta.get("min_price_filter") or ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
            "transaction_cost_bps": float(meta.get("transaction_cost_bps") or ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS),
            "promotion_min_etf_aum_b": float(meta.get("promotion_min_etf_aum_b") or ETF_OPERABILITY_DEFAULT_MIN_AUM_B),
            "promotion_max_bid_ask_spread_pct": float(
                meta.get("promotion_max_bid_ask_spread_pct") or ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT
            ),
            "benchmark_ticker": meta.get("benchmark_ticker") or ETF_REAL_MONEY_DEFAULT_BENCHMARK,
            "underperformance_guardrail_enabled": bool(
                meta.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED)
            ),
            "underperformance_guardrail_window_months": int(
                meta.get("underperformance_guardrail_window_months") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS
            ),
            "underperformance_guardrail_threshold": float(
                meta.get("underperformance_guardrail_threshold") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD
            ),
            "drawdown_guardrail_enabled": bool(
                meta.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED)
            ),
            "drawdown_guardrail_window_months": int(
                meta.get("drawdown_guardrail_window_months") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS
            ),
            "drawdown_guardrail_strategy_threshold": float(
                meta.get("drawdown_guardrail_strategy_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD
            ),
            "drawdown_guardrail_gap_threshold": float(
                meta.get("drawdown_guardrail_gap_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD
            ),
        }
    if strategy_name == "Risk Parity Trend":
        return {
            "rebalance_interval": int(meta.get("rebalance_interval") or 1),
            "vol_window": int(meta.get("vol_window") or 6),
            "min_price_filter": float(meta.get("min_price_filter") or ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
            "transaction_cost_bps": float(meta.get("transaction_cost_bps") or ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS),
            "promotion_min_etf_aum_b": float(meta.get("promotion_min_etf_aum_b") or ETF_OPERABILITY_DEFAULT_MIN_AUM_B),
            "promotion_max_bid_ask_spread_pct": float(
                meta.get("promotion_max_bid_ask_spread_pct") or ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT
            ),
            "benchmark_ticker": meta.get("benchmark_ticker") or ETF_REAL_MONEY_DEFAULT_BENCHMARK,
            "underperformance_guardrail_enabled": bool(
                meta.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED)
            ),
            "underperformance_guardrail_window_months": int(
                meta.get("underperformance_guardrail_window_months") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS
            ),
            "underperformance_guardrail_threshold": float(
                meta.get("underperformance_guardrail_threshold") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD
            ),
            "drawdown_guardrail_enabled": bool(
                meta.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED)
            ),
            "drawdown_guardrail_window_months": int(
                meta.get("drawdown_guardrail_window_months") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS
            ),
            "drawdown_guardrail_strategy_threshold": float(
                meta.get("drawdown_guardrail_strategy_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD
            ),
            "drawdown_guardrail_gap_threshold": float(
                meta.get("drawdown_guardrail_gap_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD
            ),
        }
    if strategy_name == "Dual Momentum":
        return {
            "top": int(meta.get("top") or 1),
            "rebalance_interval": int(meta.get("rebalance_interval") or 1),
            "min_price_filter": float(meta.get("min_price_filter") or ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
            "transaction_cost_bps": float(meta.get("transaction_cost_bps") or ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS),
            "promotion_min_etf_aum_b": float(meta.get("promotion_min_etf_aum_b") or ETF_OPERABILITY_DEFAULT_MIN_AUM_B),
            "promotion_max_bid_ask_spread_pct": float(
                meta.get("promotion_max_bid_ask_spread_pct") or ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT
            ),
            "benchmark_ticker": meta.get("benchmark_ticker") or ETF_REAL_MONEY_DEFAULT_BENCHMARK,
            "underperformance_guardrail_enabled": bool(
                meta.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED)
            ),
            "underperformance_guardrail_window_months": int(
                meta.get("underperformance_guardrail_window_months") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS
            ),
            "underperformance_guardrail_threshold": float(
                meta.get("underperformance_guardrail_threshold") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD
            ),
            "drawdown_guardrail_enabled": bool(
                meta.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED)
            ),
            "drawdown_guardrail_window_months": int(
                meta.get("drawdown_guardrail_window_months") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS
            ),
            "drawdown_guardrail_strategy_threshold": float(
                meta.get("drawdown_guardrail_strategy_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD
            ),
            "drawdown_guardrail_gap_threshold": float(
                meta.get("drawdown_guardrail_gap_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD
            ),
        }

    override: dict[str, Any] = {
        "tickers": list(meta.get("tickers") or []),
        "preset_name": meta.get("preset_name"),
        "universe_mode": meta.get("universe_mode") or "preset",
    }
    if meta.get("top") is not None:
        override["top_n"] = int(meta.get("top"))
    if meta.get("rebalance_interval") is not None:
        override["rebalance_interval"] = int(meta.get("rebalance_interval"))
    if meta.get("quality_factors") is not None:
        override["quality_factors"] = list(meta.get("quality_factors") or [])
    if meta.get("value_factors") is not None:
        override["value_factors"] = list(meta.get("value_factors") or [])
    if meta.get("factor_freq") is not None:
        override["factor_freq"] = meta.get("factor_freq")
    if meta.get("rebalance_freq") is not None:
        override["rebalance_freq"] = meta.get("rebalance_freq")
    if meta.get("snapshot_mode") is not None:
        override["snapshot_mode"] = meta.get("snapshot_mode")
    if meta.get("universe_contract") is not None:
        override["universe_contract"] = meta.get("universe_contract")
    if meta.get("dynamic_target_size") is not None:
        override["dynamic_target_size"] = int(meta.get("dynamic_target_size"))
    if meta.get("trend_filter_enabled") is not None:
        override["trend_filter_enabled"] = bool(meta.get("trend_filter_enabled"))
    if meta.get("trend_filter_window") is not None:
        override["trend_filter_window"] = int(meta.get("trend_filter_window"))
    if meta.get("market_regime_enabled") is not None:
        override["market_regime_enabled"] = bool(meta.get("market_regime_enabled"))
    if meta.get("market_regime_window") is not None:
        override["market_regime_window"] = int(meta.get("market_regime_window"))
    if meta.get("market_regime_benchmark") is not None:
        override["market_regime_benchmark"] = meta.get("market_regime_benchmark")
    if meta.get("min_price_filter") is not None:
        override["min_price_filter"] = float(meta.get("min_price_filter"))
    if meta.get("min_history_months_filter") is not None:
        override["min_history_months_filter"] = int(meta.get("min_history_months_filter"))
    if meta.get("min_avg_dollar_volume_20d_m_filter") is not None:
        override["min_avg_dollar_volume_20d_m_filter"] = float(meta.get("min_avg_dollar_volume_20d_m_filter"))
    if meta.get("transaction_cost_bps") is not None:
        override["transaction_cost_bps"] = float(meta.get("transaction_cost_bps"))
    if meta.get("benchmark_contract") is not None:
        override["benchmark_contract"] = meta.get("benchmark_contract")
    if meta.get("benchmark_ticker") is not None:
        override["benchmark_ticker"] = meta.get("benchmark_ticker")
    if meta.get("promotion_min_benchmark_coverage") is not None:
        override["promotion_min_benchmark_coverage"] = float(meta.get("promotion_min_benchmark_coverage"))
    if meta.get("promotion_min_net_cagr_spread") is not None:
        override["promotion_min_net_cagr_spread"] = float(meta.get("promotion_min_net_cagr_spread"))
    if meta.get("promotion_min_liquidity_clean_coverage") is not None:
        override["promotion_min_liquidity_clean_coverage"] = float(meta.get("promotion_min_liquidity_clean_coverage"))
    if meta.get("promotion_max_underperformance_share") is not None:
        override["promotion_max_underperformance_share"] = float(meta.get("promotion_max_underperformance_share"))
    if meta.get("promotion_min_worst_rolling_excess_return") is not None:
        override["promotion_min_worst_rolling_excess_return"] = float(meta.get("promotion_min_worst_rolling_excess_return"))
    if meta.get("promotion_max_strategy_drawdown") is not None:
        override["promotion_max_strategy_drawdown"] = float(meta.get("promotion_max_strategy_drawdown"))
    if meta.get("promotion_max_drawdown_gap_vs_benchmark") is not None:
        override["promotion_max_drawdown_gap_vs_benchmark"] = float(meta.get("promotion_max_drawdown_gap_vs_benchmark"))
    if meta.get("underperformance_guardrail_enabled") is not None:
        override["underperformance_guardrail_enabled"] = bool(meta.get("underperformance_guardrail_enabled"))
    if meta.get("underperformance_guardrail_window_months") is not None:
        override["underperformance_guardrail_window_months"] = int(meta.get("underperformance_guardrail_window_months"))
    if meta.get("underperformance_guardrail_threshold") is not None:
        override["underperformance_guardrail_threshold"] = float(meta.get("underperformance_guardrail_threshold"))
    if meta.get("drawdown_guardrail_enabled") is not None:
        override["drawdown_guardrail_enabled"] = bool(meta.get("drawdown_guardrail_enabled"))
    if meta.get("drawdown_guardrail_window_months") is not None:
        override["drawdown_guardrail_window_months"] = int(meta.get("drawdown_guardrail_window_months"))
    if meta.get("drawdown_guardrail_strategy_threshold") is not None:
        override["drawdown_guardrail_strategy_threshold"] = float(meta.get("drawdown_guardrail_strategy_threshold"))
    if meta.get("drawdown_guardrail_gap_threshold") is not None:
        override["drawdown_guardrail_gap_threshold"] = float(meta.get("drawdown_guardrail_gap_threshold"))
    return override


def _build_saved_portfolio_compare_context(bundles: list[dict[str, Any]]) -> dict[str, Any]:
    if not bundles:
        raise ValueError("Compare bundles are required.")

    first_meta = bundles[0].get("meta") or {}
    selected_strategies = [str(bundle.get("strategy_name")) for bundle in bundles]
    strategy_overrides = {
        str(bundle.get("strategy_name")): _bundle_to_saved_strategy_override(bundle)
        for bundle in bundles
    }
    return {
        "selected_strategies": selected_strategies,
        "start": first_meta.get("start"),
        "end": first_meta.get("end"),
        "timeframe": first_meta.get("timeframe") or "1d",
        "option": first_meta.get("option") or "month_end",
        "strategy_overrides": strategy_overrides,
    }


def _build_saved_portfolio_context(
    *,
    bundles: list[dict[str, Any]],
    weighted_bundle: dict[str, Any],
) -> dict[str, Any]:
    strategy_names = list(weighted_bundle.get("component_strategy_names") or [bundle["strategy_name"] for bundle in bundles])
    input_weights = list(weighted_bundle.get("component_input_weights") or [])
    normalized_weights = list(weighted_bundle.get("component_weights") or [])
    if not input_weights and normalized_weights:
        input_weights = [round(float(weight) * 100.0, 4) for weight in normalized_weights]
    if not normalized_weights and input_weights:
        total_weight = sum(float(weight) for weight in input_weights)
        normalized_weights = [
            (float(weight) / total_weight) if total_weight > 0 else 0.0
            for weight in input_weights
        ]

    return {
        "strategy_names": strategy_names,
        "weights_percent": [float(weight) for weight in input_weights],
        "normalized_weights": [float(weight) for weight in normalized_weights],
        "date_policy": weighted_bundle.get("date_policy") or "intersection",
    }


def _queue_saved_portfolio_compare_prefill(saved_portfolio: dict[str, Any]) -> None:
    compare_context = dict(saved_portfolio.get("compare_context") or {})
    portfolio_context = dict(saved_portfolio.get("portfolio_context") or {})
    st.session_state.backtest_compare_prefill_payload = compare_context
    st.session_state.backtest_compare_prefill_pending = True
    st.session_state.backtest_compare_prefill_notice = (
        f"저장된 포트폴리오 `{saved_portfolio.get('name')}` 설정을 `Compare & Portfolio Builder`로 불러왔습니다."
    )
    st.session_state.backtest_weighted_portfolio_prefill = {
        "strategy_names": list(portfolio_context.get("strategy_names") or []),
        "weights_percent": list(portfolio_context.get("weights_percent") or []),
        "date_policy": portfolio_context.get("date_policy") or "intersection",
    }
    st.session_state.backtest_requested_panel = "Compare & Portfolio Builder"


def _apply_compare_strategy_prefill(strategy_name: str, override: dict[str, Any]) -> None:
    if strategy_name == "Equal Weight":
        preset_name = override.get("preset_name")
        universe_mode = override.get("universe_mode")
        tickers_text = ",".join(list(override.get("tickers") or EQUAL_WEIGHT_PRESETS["Dividend ETFs"]))
        st.session_state["compare_eq_universe_mode"] = (
            "Preset" if universe_mode == "preset" and preset_name in EQUAL_WEIGHT_PRESETS else "Manual"
        )
        if st.session_state["compare_eq_universe_mode"] == "Preset":
            st.session_state["compare_eq_preset"] = preset_name or "Dividend ETFs"
        else:
            st.session_state["compare_eq_manual_tickers"] = tickers_text
        st.session_state["compare_eq_interval"] = int(override.get("rebalance_interval") or 12)
        return
    if strategy_name == "GTAA":
        preset_name = override.get("preset_name")
        universe_mode = override.get("universe_mode")
        tickers_text = ",".join(list(override.get("tickers") or GTAA_DEFAULT_TICKERS))
        st.session_state["compare_gtaa_universe_mode"] = (
            "Preset" if universe_mode == "preset" and preset_name in GTAA_PRESETS else "Manual"
        )
        if st.session_state["compare_gtaa_universe_mode"] == "Preset":
            st.session_state["compare_gtaa_preset"] = preset_name or "GTAA Universe"
        else:
            st.session_state["compare_gtaa_manual_tickers"] = tickers_text
        st.session_state["compare_gtaa_top"] = int(override.get("top") or 3)
        st.session_state["compare_gtaa_interval"] = int(
            override.get("interval") or override.get("rebalance_interval") or GTAA_DEFAULT_SIGNAL_INTERVAL
        )
        _set_gtaa_score_selection_state(
            key_prefix="compare_gtaa",
            score_lookback_months=list(
                override.get("score_lookback_months")
                or [_gtaa_months_from_return_col(col) for col in list(override.get("score_return_columns") or GTAA_SCORE_RETURN_COLUMNS)]
            ),
        )
        st.session_state["compare_gtaa_trend_filter_window"] = int(
            override.get("trend_filter_window") or GTAA_DEFAULT_TREND_FILTER_WINDOW
        )
        st.session_state["compare_gtaa_risk_off_mode"] = _risk_off_mode_value_to_label(
            override.get("risk_off_mode") or GTAA_DEFAULT_RISK_OFF_MODE
        )
        st.session_state["compare_gtaa_defensive_tickers"] = ",".join(
            list(override.get("defensive_tickers") or GTAA_DEFAULT_DEFENSIVE_TICKERS)
        )
        st.session_state["compare_gtaa_risk_off_market_regime_enabled"] = bool(
            override.get("market_regime_enabled", False)
        )
        st.session_state["compare_gtaa_risk_off_market_regime_window"] = int(
            override.get("market_regime_window") or STRICT_MARKET_REGIME_DEFAULT_WINDOW
        )
        st.session_state["compare_gtaa_risk_off_market_regime_benchmark"] = (
            override.get("market_regime_benchmark") or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK
        )
        st.session_state["compare_gtaa_crash_guardrail_enabled"] = bool(
            override.get("crash_guardrail_enabled", GTAA_DEFAULT_CRASH_GUARDRAIL_ENABLED)
        )
        st.session_state["compare_gtaa_crash_guardrail_drawdown_threshold"] = float(
            (override.get("crash_guardrail_drawdown_threshold") or GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD) * 100.0
        )
        st.session_state["compare_gtaa_crash_guardrail_lookback_months"] = int(
            override.get("crash_guardrail_lookback_months") or GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS
        )
        st.session_state["compare_gtaa_min_price_filter"] = float(override.get("min_price_filter") or ETF_REAL_MONEY_DEFAULT_MIN_PRICE)
        st.session_state["compare_gtaa_transaction_cost_bps"] = float(override.get("transaction_cost_bps") or ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS)
        st.session_state["compare_gtaa_promotion_min_etf_aum_b"] = float(
            override.get("promotion_min_etf_aum_b") or ETF_OPERABILITY_DEFAULT_MIN_AUM_B
        )
        st.session_state["compare_gtaa_promotion_max_bid_ask_spread_pct"] = float(
            (override.get("promotion_max_bid_ask_spread_pct") or ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT) * 100.0
        )
        st.session_state["compare_gtaa_benchmark_ticker"] = str(override.get("benchmark_ticker") or ETF_REAL_MONEY_DEFAULT_BENCHMARK).strip().upper()
        st.session_state["compare_gtaa_underperformance_guardrail_enabled"] = bool(
            override.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["compare_gtaa_underperformance_guardrail_window_months"] = int(
            override.get("underperformance_guardrail_window_months") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["compare_gtaa_underperformance_guardrail_threshold"] = float(
            (override.get("underperformance_guardrail_threshold") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD) * 100.0
        )
        st.session_state["compare_gtaa_drawdown_guardrail_enabled"] = bool(
            override.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["compare_gtaa_drawdown_guardrail_window_months"] = int(
            override.get("drawdown_guardrail_window_months") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["compare_gtaa_drawdown_guardrail_strategy_threshold"] = float(
            (override.get("drawdown_guardrail_strategy_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD) * 100.0
        )
        st.session_state["compare_gtaa_drawdown_guardrail_gap_threshold"] = float(
            (override.get("drawdown_guardrail_gap_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD) * 100.0
        )
        return
    if strategy_name == "Risk Parity Trend":
        st.session_state["compare_rp_interval"] = int(override.get("rebalance_interval") or 1)
        st.session_state["compare_rp_vol_window"] = int(override.get("vol_window") or 6)
        st.session_state["compare_rp_min_price_filter"] = float(override.get("min_price_filter") or ETF_REAL_MONEY_DEFAULT_MIN_PRICE)
        st.session_state["compare_rp_transaction_cost_bps"] = float(override.get("transaction_cost_bps") or ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS)
        st.session_state["compare_rp_promotion_min_etf_aum_b"] = float(
            override.get("promotion_min_etf_aum_b") or ETF_OPERABILITY_DEFAULT_MIN_AUM_B
        )
        st.session_state["compare_rp_promotion_max_bid_ask_spread_pct"] = float(
            (override.get("promotion_max_bid_ask_spread_pct") or ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT) * 100.0
        )
        st.session_state["compare_rp_benchmark_ticker"] = str(override.get("benchmark_ticker") or ETF_REAL_MONEY_DEFAULT_BENCHMARK).strip().upper()
        st.session_state["compare_rp_underperformance_guardrail_enabled"] = bool(
            override.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["compare_rp_underperformance_guardrail_window_months"] = int(
            override.get("underperformance_guardrail_window_months") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["compare_rp_underperformance_guardrail_threshold"] = float(
            (override.get("underperformance_guardrail_threshold") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD) * 100.0
        )
        st.session_state["compare_rp_drawdown_guardrail_enabled"] = bool(
            override.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["compare_rp_drawdown_guardrail_window_months"] = int(
            override.get("drawdown_guardrail_window_months") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["compare_rp_drawdown_guardrail_strategy_threshold"] = float(
            (override.get("drawdown_guardrail_strategy_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD) * 100.0
        )
        st.session_state["compare_rp_drawdown_guardrail_gap_threshold"] = float(
            (override.get("drawdown_guardrail_gap_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD) * 100.0
        )
        return
    if strategy_name == "Dual Momentum":
        st.session_state["compare_dm_top"] = int(override.get("top") or 1)
        st.session_state["compare_dm_interval"] = int(override.get("rebalance_interval") or 1)
        st.session_state["compare_dm_min_price_filter"] = float(override.get("min_price_filter") or ETF_REAL_MONEY_DEFAULT_MIN_PRICE)
        st.session_state["compare_dm_transaction_cost_bps"] = float(override.get("transaction_cost_bps") or ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS)
        st.session_state["compare_dm_promotion_min_etf_aum_b"] = float(
            override.get("promotion_min_etf_aum_b") or ETF_OPERABILITY_DEFAULT_MIN_AUM_B
        )
        st.session_state["compare_dm_promotion_max_bid_ask_spread_pct"] = float(
            (override.get("promotion_max_bid_ask_spread_pct") or ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT) * 100.0
        )
        st.session_state["compare_dm_benchmark_ticker"] = str(override.get("benchmark_ticker") or ETF_REAL_MONEY_DEFAULT_BENCHMARK).strip().upper()
        st.session_state["compare_dm_underperformance_guardrail_enabled"] = bool(
            override.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["compare_dm_underperformance_guardrail_window_months"] = int(
            override.get("underperformance_guardrail_window_months") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["compare_dm_underperformance_guardrail_threshold"] = float(
            (override.get("underperformance_guardrail_threshold") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD) * 100.0
        )
        st.session_state["compare_dm_drawdown_guardrail_enabled"] = bool(
            override.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["compare_dm_drawdown_guardrail_window_months"] = int(
            override.get("drawdown_guardrail_window_months") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["compare_dm_drawdown_guardrail_strategy_threshold"] = float(
            (override.get("drawdown_guardrail_strategy_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD) * 100.0
        )
        st.session_state["compare_dm_drawdown_guardrail_gap_threshold"] = float(
            (override.get("drawdown_guardrail_gap_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD) * 100.0
        )
        return
    if strategy_name == "Quality Snapshot":
        st.session_state["compare_qs_top_n"] = int(override.get("top_n") or 2)
        st.session_state["compare_qs_factors"] = list(override.get("quality_factors") or ["roe", "gross_margin", "operating_margin", "debt_ratio"])
        return

    strict_compare_key_map = {
        "Quality Snapshot (Strict Annual)": "qss",
        "Quality Snapshot (Strict Quarterly Prototype)": "qsqp",
        "Value Snapshot (Strict Annual)": "vss",
        "Value Snapshot (Strict Quarterly Prototype)": "vsqp",
        "Quality + Value Snapshot (Strict Annual)": "qvss",
        "Quality + Value Snapshot (Strict Quarterly Prototype)": "qvqp",
    }
    key_prefix = strict_compare_key_map.get(strategy_name)
    if not key_prefix:
        return

    preset_name = override.get("preset_name")
    if preset_name:
        st.session_state[f"compare_{key_prefix}_preset"] = preset_name
    st.session_state[f"compare_{key_prefix}_top_n"] = int(override.get("top_n") or (10 if "Value" in strategy_name or "Multi-Factor" in strategy_name else 2))
    st.session_state[f"compare_{key_prefix}_rebalance_interval"] = int(override.get("rebalance_interval") or 1)
    st.session_state[f"compare_{key_prefix}_universe_contract"] = _universe_contract_value_to_label(
        override.get("universe_contract") or STATIC_MANAGED_RESEARCH_UNIVERSE
    )
    st.session_state[f"compare_{key_prefix}_trend_filter_enabled"] = bool(
        override.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED)
    )
    st.session_state[f"compare_{key_prefix}_trend_filter_window"] = int(
        override.get("trend_filter_window") or STRICT_TREND_FILTER_DEFAULT_WINDOW
    )
    st.session_state[f"compare_{key_prefix}_market_regime_enabled"] = bool(
        override.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED)
    )
    st.session_state[f"compare_{key_prefix}_market_regime_window"] = int(
        override.get("market_regime_window") or STRICT_MARKET_REGIME_DEFAULT_WINDOW
    )
    st.session_state[f"compare_{key_prefix}_market_regime_benchmark"] = (
        override.get("market_regime_benchmark") or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK
    )
    st.session_state[f"compare_{key_prefix}_underperformance_guardrail_enabled"] = bool(
        override.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED)
    )
    st.session_state[f"compare_{key_prefix}_underperformance_guardrail_window_months"] = int(
        override.get("underperformance_guardrail_window_months") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS
    )
    st.session_state[f"compare_{key_prefix}_underperformance_guardrail_threshold"] = float(
        (override.get("underperformance_guardrail_threshold") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD) * 100.0
    )
    st.session_state[f"compare_{key_prefix}_drawdown_guardrail_enabled"] = bool(
        override.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED)
    )
    st.session_state[f"compare_{key_prefix}_drawdown_guardrail_window_months"] = int(
        override.get("drawdown_guardrail_window_months") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS
    )
    st.session_state[f"compare_{key_prefix}_drawdown_guardrail_strategy_threshold"] = float(
        (override.get("drawdown_guardrail_strategy_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD) * 100.0
    )
    st.session_state[f"compare_{key_prefix}_drawdown_guardrail_gap_threshold"] = float(
        (override.get("drawdown_guardrail_gap_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD) * 100.0
    )
    st.session_state[f"compare_{key_prefix}_min_price_filter"] = float(
        override.get("min_price_filter") or ETF_REAL_MONEY_DEFAULT_MIN_PRICE
    )
    st.session_state[f"compare_{key_prefix}_min_history_months_filter"] = int(
        override.get("min_history_months_filter") or STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS
    )
    st.session_state[f"compare_{key_prefix}_min_avg_dollar_volume_20d_m_filter"] = float(
        override.get("min_avg_dollar_volume_20d_m_filter") or STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M
    )
    st.session_state[f"compare_{key_prefix}_transaction_cost_bps"] = float(
        override.get("transaction_cost_bps") or ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS
    )
    st.session_state[f"compare_{key_prefix}_benchmark_contract"] = _benchmark_contract_value_to_label(
        override.get("benchmark_contract") or STRICT_DEFAULT_BENCHMARK_CONTRACT
    )
    st.session_state[f"compare_{key_prefix}_benchmark_ticker"] = str(
        override.get("benchmark_ticker") or ETF_REAL_MONEY_DEFAULT_BENCHMARK
    ).strip().upper()
    st.session_state[f"compare_{key_prefix}_promotion_min_benchmark_coverage"] = float(
        (override.get("promotion_min_benchmark_coverage") or STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE) * 100.0
    )
    st.session_state[f"compare_{key_prefix}_promotion_min_net_cagr_spread"] = float(
        (override.get("promotion_min_net_cagr_spread") or STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD) * 100.0
    )
    st.session_state[f"compare_{key_prefix}_promotion_min_liquidity_clean_coverage"] = float(
        (override.get("promotion_min_liquidity_clean_coverage") or STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE) * 100.0
    )
    st.session_state[f"compare_{key_prefix}_promotion_max_underperformance_share"] = float(
        (override.get("promotion_max_underperformance_share") or STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE) * 100.0
    )
    st.session_state[f"compare_{key_prefix}_promotion_min_worst_rolling_excess_return"] = float(
        (override.get("promotion_min_worst_rolling_excess_return") or STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN) * 100.0
    )
    st.session_state[f"compare_{key_prefix}_promotion_max_strategy_drawdown"] = float(
        (override.get("promotion_max_strategy_drawdown") or STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN) * 100.0
    )
    st.session_state[f"compare_{key_prefix}_promotion_max_drawdown_gap_vs_benchmark"] = float(
        (override.get("promotion_max_drawdown_gap_vs_benchmark") or STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK) * 100.0
    )
    if override.get("quality_factors") is not None:
        quality_key = "quality_factors" if key_prefix in {"qvss", "qvqp"} else "factors"
        st.session_state[f"compare_{key_prefix}_{quality_key}"] = list(override.get("quality_factors") or [])
    if override.get("value_factors") is not None:
        value_key = "factors" if key_prefix in {"vss", "vsqp"} else "value_factors"
        st.session_state[f"compare_{key_prefix}_{value_key}"] = list(override.get("value_factors") or [])


def _apply_compare_prefill() -> None:
    payload = st.session_state.get("backtest_compare_prefill_payload")
    pending = st.session_state.get("backtest_compare_prefill_pending")
    if not payload or not pending:
        return

    selected_strategies = list(payload.get("selected_strategies") or [])
    selected_strategy_categories: list[str] = []
    for strategy_name in selected_strategies:
        strategy_choice, strategy_variant = display_name_to_selection(strategy_name)
        resolved_choice = strategy_choice or strategy_name
        if resolved_choice not in selected_strategy_categories:
            selected_strategy_categories.append(resolved_choice)
        variant_key = _compare_family_variant_session_key(resolved_choice)
        if variant_key and strategy_variant:
            st.session_state[variant_key] = strategy_variant
    if selected_strategy_categories:
        st.session_state["compare_selected_strategies"] = selected_strategy_categories
    if payload.get("start"):
        st.session_state["compare_start"] = pd.to_datetime(payload.get("start")).date()
    if payload.get("end"):
        st.session_state["compare_end"] = pd.to_datetime(payload.get("end")).date()
    if payload.get("timeframe"):
        st.session_state["compare_timeframe"] = payload.get("timeframe")
    if payload.get("option"):
        st.session_state["compare_option"] = payload.get("option")

    strategy_overrides = payload.get("strategy_overrides") or {}
    for strategy_name in selected_strategies:
        override = strategy_overrides.get(strategy_name) or {}
        _apply_compare_strategy_prefill(strategy_name, override)

    st.session_state.backtest_compare_prefill_pending = False


def _apply_weighted_portfolio_prefill(strategy_names: list[str]) -> None:
    payload = st.session_state.get("backtest_weighted_portfolio_prefill")
    if not payload:
        return

    saved_strategy_names = list(payload.get("strategy_names") or [])
    if saved_strategy_names != strategy_names:
        return

    for strategy_name, weight in zip(saved_strategy_names, payload.get("weights_percent") or []):
        st.session_state[f"weight_{strategy_name}"] = float(weight)
    st.session_state["weighted_portfolio_date_policy"] = payload.get("date_policy") or "intersection"
    st.session_state.backtest_weighted_portfolio_prefill = None


def _resolve_saved_portfolio_dynamic_inputs(
    *,
    strategy_name: str,
    override: dict[str, Any],
) -> dict[str, Any]:
    params = dict(override)
    universe_contract = params.get("universe_contract") or STATIC_MANAGED_RESEARCH_UNIVERSE
    if universe_contract != HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        return params

    tickers = list(params.get("tickers") or [])
    preset_name = params.get("preset_name")
    statement_freq = "quarterly" if "Quarterly Prototype" in strategy_name else "annual"
    dynamic_candidate_tickers, dynamic_target_size = _resolve_strict_dynamic_universe_inputs(
        tickers=tickers,
        preset_name=preset_name,
        universe_contract=universe_contract,
        statement_freq=statement_freq,
    )
    params["dynamic_candidate_tickers"] = dynamic_candidate_tickers
    params["dynamic_target_size"] = dynamic_target_size
    return params


def _normalize_recorded_date_range(
    value: Any,
    *,
    fallback_start: date,
    fallback_end: date,
) -> tuple[date, date]:
    if isinstance(value, tuple):
        normalized_items = [item for item in value if isinstance(item, date)]
        if len(normalized_items) >= 2:
            return normalized_items[0], normalized_items[1]
        if len(normalized_items) == 1:
            return normalized_items[0], fallback_end
        return fallback_start, fallback_end

    if isinstance(value, date):
        return value, fallback_end

    return fallback_start, fallback_end


def _apply_single_strategy_prefill(strategy_key: str) -> None:
    payload = st.session_state.get("backtest_prefill_payload")
    pending = st.session_state.get("backtest_prefill_pending")
    if not payload or not pending or payload.get("strategy_key") != strategy_key:
        return

    start_date = pd.to_datetime(payload.get("start")).date() if payload.get("start") else date(2016, 1, 1)
    end_date = pd.to_datetime(payload.get("end")).date() if payload.get("end") else DEFAULT_BACKTEST_END_DATE
    tickers_text = ",".join(payload.get("tickers", []))
    preset_name = payload.get("preset_name")
    universe_mode = payload.get("universe_mode")

    if strategy_key == "equal_weight":
        st.session_state["eq_universe_mode"] = "Preset" if universe_mode == "preset" and preset_name in EQUAL_WEIGHT_PRESETS else "Manual"
        if st.session_state["eq_universe_mode"] == "Preset":
            st.session_state["eq_preset"] = preset_name
        else:
            st.session_state["eq_manual_tickers"] = tickers_text
        st.session_state["eq_start"] = start_date
        st.session_state["eq_end"] = end_date
        st.session_state["eq_timeframe"] = payload.get("timeframe") or "1d"
        st.session_state["eq_option"] = payload.get("option") or "month_end"
        st.session_state["eq_rebalance_interval"] = int(payload.get("rebalance_interval") or 12)
    elif strategy_key == "gtaa":
        st.session_state["gtaa_universe_mode"] = "Preset" if universe_mode == "preset" and preset_name in GTAA_PRESETS else "Manual"
        if st.session_state["gtaa_universe_mode"] == "Preset":
            st.session_state["gtaa_preset"] = preset_name
        else:
            st.session_state["gtaa_manual_tickers"] = tickers_text
        st.session_state["gtaa_start"] = start_date
        st.session_state["gtaa_end"] = end_date
        st.session_state["gtaa_timeframe"] = payload.get("timeframe") or "1d"
        st.session_state["gtaa_option"] = payload.get("option") or "month_end"
        st.session_state["gtaa_top"] = int(payload.get("top") or 3)
        st.session_state["gtaa_interval"] = int(payload.get("interval") or GTAA_DEFAULT_SIGNAL_INTERVAL)
        _set_gtaa_score_selection_state(
            key_prefix="gtaa",
            score_lookback_months=list(
                payload.get("score_lookback_months")
                or [_gtaa_months_from_return_col(col) for col in list(payload.get("score_return_columns") or GTAA_SCORE_RETURN_COLUMNS)]
            ),
        )
        st.session_state["gtaa_trend_filter_window"] = int(payload.get("trend_filter_window") or GTAA_DEFAULT_TREND_FILTER_WINDOW)
        st.session_state["gtaa_risk_off_mode"] = _risk_off_mode_value_to_label(payload.get("risk_off_mode") or GTAA_DEFAULT_RISK_OFF_MODE)
        st.session_state["gtaa_defensive_tickers"] = ",".join(
            list(payload.get("defensive_tickers") or GTAA_DEFAULT_DEFENSIVE_TICKERS)
        )
        st.session_state["gtaa_risk_off_market_regime_enabled"] = bool(
            payload.get("market_regime_enabled", False)
        )
        st.session_state["gtaa_risk_off_market_regime_window"] = int(
            payload.get("market_regime_window") or STRICT_MARKET_REGIME_DEFAULT_WINDOW
        )
        st.session_state["gtaa_risk_off_market_regime_benchmark"] = (
            payload.get("market_regime_benchmark") or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK
        )
        st.session_state["gtaa_crash_guardrail_enabled"] = bool(
            payload.get("crash_guardrail_enabled", GTAA_DEFAULT_CRASH_GUARDRAIL_ENABLED)
        )
        st.session_state["gtaa_crash_guardrail_drawdown_threshold"] = float(
            (payload.get("crash_guardrail_drawdown_threshold") or GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD) * 100.0
        )
        st.session_state["gtaa_crash_guardrail_lookback_months"] = int(
            payload.get("crash_guardrail_lookback_months") or GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS
        )
        st.session_state["gtaa_min_price_filter"] = float(payload.get("min_price_filter") or ETF_REAL_MONEY_DEFAULT_MIN_PRICE)
        st.session_state["gtaa_transaction_cost_bps"] = float(payload.get("transaction_cost_bps") or ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS)
        st.session_state["gtaa_promotion_min_etf_aum_b"] = float(
            payload.get("promotion_min_etf_aum_b") or ETF_OPERABILITY_DEFAULT_MIN_AUM_B
        )
        st.session_state["gtaa_promotion_max_bid_ask_spread_pct"] = float(
            (payload.get("promotion_max_bid_ask_spread_pct") or ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT) * 100.0
        )
        st.session_state["gtaa_benchmark_ticker"] = str(payload.get("benchmark_ticker") or ETF_REAL_MONEY_DEFAULT_BENCHMARK).strip().upper()
        st.session_state["gtaa_underperformance_guardrail_enabled"] = bool(
            payload.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["gtaa_underperformance_guardrail_window_months"] = int(
            payload.get("underperformance_guardrail_window_months") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["gtaa_underperformance_guardrail_threshold"] = float(
            (payload.get("underperformance_guardrail_threshold") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD) * 100.0
        )
        st.session_state["gtaa_drawdown_guardrail_enabled"] = bool(
            payload.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["gtaa_drawdown_guardrail_window_months"] = int(
            payload.get("drawdown_guardrail_window_months") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["gtaa_drawdown_guardrail_strategy_threshold"] = float(
            (payload.get("drawdown_guardrail_strategy_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD) * 100.0
        )
        st.session_state["gtaa_drawdown_guardrail_gap_threshold"] = float(
            (payload.get("drawdown_guardrail_gap_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD) * 100.0
        )
    elif strategy_key == "risk_parity_trend":
        st.session_state["rp_universe_mode"] = "Preset" if universe_mode == "preset" and preset_name in RISK_PARITY_PRESETS else "Manual"
        if st.session_state["rp_universe_mode"] == "Preset":
            st.session_state["rp_preset"] = preset_name
        else:
            st.session_state["rp_manual_tickers"] = tickers_text
        st.session_state["rp_start"] = start_date
        st.session_state["rp_end"] = end_date
        st.session_state["rp_timeframe"] = payload.get("timeframe") or "1d"
        st.session_state["rp_option"] = payload.get("option") or "month_end"
        st.session_state["rp_rebalance_interval"] = int(payload.get("rebalance_interval") or 1)
        st.session_state["rp_vol_window"] = int(payload.get("vol_window") or 6)
        st.session_state["rp_min_price_filter"] = float(payload.get("min_price_filter") or ETF_REAL_MONEY_DEFAULT_MIN_PRICE)
        st.session_state["rp_transaction_cost_bps"] = float(payload.get("transaction_cost_bps") or ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS)
        st.session_state["rp_promotion_min_etf_aum_b"] = float(
            payload.get("promotion_min_etf_aum_b") or ETF_OPERABILITY_DEFAULT_MIN_AUM_B
        )
        st.session_state["rp_promotion_max_bid_ask_spread_pct"] = float(
            (payload.get("promotion_max_bid_ask_spread_pct") or ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT) * 100.0
        )
        st.session_state["rp_benchmark_ticker"] = str(payload.get("benchmark_ticker") or ETF_REAL_MONEY_DEFAULT_BENCHMARK).strip().upper()
        st.session_state["rp_underperformance_guardrail_enabled"] = bool(
            payload.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["rp_underperformance_guardrail_window_months"] = int(
            payload.get("underperformance_guardrail_window_months") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["rp_underperformance_guardrail_threshold"] = float(
            (payload.get("underperformance_guardrail_threshold") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD) * 100.0
        )
        st.session_state["rp_drawdown_guardrail_enabled"] = bool(
            payload.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["rp_drawdown_guardrail_window_months"] = int(
            payload.get("drawdown_guardrail_window_months") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["rp_drawdown_guardrail_strategy_threshold"] = float(
            (payload.get("drawdown_guardrail_strategy_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD) * 100.0
        )
        st.session_state["rp_drawdown_guardrail_gap_threshold"] = float(
            (payload.get("drawdown_guardrail_gap_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD) * 100.0
        )
    elif strategy_key == "dual_momentum":
        st.session_state["dm_universe_mode"] = "Preset" if universe_mode == "preset" and preset_name in DUAL_MOMENTUM_PRESETS else "Manual"
        if st.session_state["dm_universe_mode"] == "Preset":
            st.session_state["dm_preset"] = preset_name
        else:
            st.session_state["dm_manual_tickers"] = tickers_text
        st.session_state["dm_start"] = start_date
        st.session_state["dm_end"] = end_date
        st.session_state["dm_timeframe"] = payload.get("timeframe") or "1d"
        st.session_state["dm_option"] = payload.get("option") or "month_end"
        st.session_state["dm_top"] = int(payload.get("top") or 1)
        st.session_state["dm_rebalance_interval"] = int(payload.get("rebalance_interval") or 1)
        st.session_state["dm_min_price_filter"] = float(payload.get("min_price_filter") or ETF_REAL_MONEY_DEFAULT_MIN_PRICE)
        st.session_state["dm_transaction_cost_bps"] = float(payload.get("transaction_cost_bps") or ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS)
        st.session_state["dm_promotion_min_etf_aum_b"] = float(
            payload.get("promotion_min_etf_aum_b") or ETF_OPERABILITY_DEFAULT_MIN_AUM_B
        )
        st.session_state["dm_promotion_max_bid_ask_spread_pct"] = float(
            (payload.get("promotion_max_bid_ask_spread_pct") or ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT) * 100.0
        )
        st.session_state["dm_benchmark_ticker"] = str(payload.get("benchmark_ticker") or ETF_REAL_MONEY_DEFAULT_BENCHMARK).strip().upper()
        st.session_state["dm_underperformance_guardrail_enabled"] = bool(
            payload.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["dm_underperformance_guardrail_window_months"] = int(
            payload.get("underperformance_guardrail_window_months") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["dm_underperformance_guardrail_threshold"] = float(
            (payload.get("underperformance_guardrail_threshold") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD) * 100.0
        )
        st.session_state["dm_drawdown_guardrail_enabled"] = bool(
            payload.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["dm_drawdown_guardrail_window_months"] = int(
            payload.get("drawdown_guardrail_window_months") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["dm_drawdown_guardrail_strategy_threshold"] = float(
            (payload.get("drawdown_guardrail_strategy_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD) * 100.0
        )
        st.session_state["dm_drawdown_guardrail_gap_threshold"] = float(
            (payload.get("drawdown_guardrail_gap_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD) * 100.0
        )
    elif strategy_key == "quality_snapshot":
        st.session_state["qs_universe_mode"] = "Preset" if universe_mode == "preset" and preset_name in QUALITY_BROAD_PRESETS else "Manual"
        if st.session_state["qs_universe_mode"] == "Preset":
            st.session_state["qs_preset"] = preset_name
        else:
            st.session_state["qs_manual_tickers"] = tickers_text
        st.session_state["qs_start"] = start_date
        st.session_state["qs_end"] = end_date
        st.session_state["qs_top_n"] = int(payload.get("top") or 2)
        st.session_state["qs_timeframe"] = payload.get("timeframe") or "1d"
        st.session_state["qs_option"] = payload.get("option") or "month_end"
        st.session_state["qs_factor_freq"] = payload.get("factor_freq") or "annual"
        st.session_state["qs_snapshot_mode"] = payload.get("snapshot_mode") or "broad_research"
        st.session_state["qs_quality_factors"] = payload.get("quality_factors") or ["roe", "gross_margin", "operating_margin", "debt_ratio"]
    elif strategy_key == "quality_snapshot_strict_annual":
        st.session_state["qss_universe_mode"] = "Preset" if universe_mode == "preset" and preset_name in QUALITY_STRICT_PRESETS else "Manual"
        if st.session_state["qss_universe_mode"] == "Preset":
            st.session_state["qss_preset"] = preset_name
        else:
            st.session_state["qss_manual_tickers"] = tickers_text
        st.session_state["qss_start"] = start_date
        st.session_state["qss_end"] = end_date
        st.session_state["qss_top_n"] = int(payload.get("top") or 2)
        st.session_state["qss_timeframe"] = payload.get("timeframe") or "1d"
        st.session_state["qss_option"] = payload.get("option") or "month_end"
        st.session_state["qss_quality_factors"] = payload.get("quality_factors") or QUALITY_STRICT_DEFAULT_FACTORS
        st.session_state["qss_universe_contract"] = next(
            (label for label, value in STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.items() if value == (payload.get("universe_contract") or STATIC_MANAGED_RESEARCH_UNIVERSE)),
            "Static Managed Research Universe",
        )
        st.session_state["qss_trend_filter_enabled"] = bool(payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED))
        st.session_state["qss_trend_filter_window"] = int(payload.get("trend_filter_window") or STRICT_TREND_FILTER_DEFAULT_WINDOW)
        st.session_state["qss_market_regime_enabled"] = bool(payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED))
        st.session_state["qss_market_regime_window"] = int(payload.get("market_regime_window") or STRICT_MARKET_REGIME_DEFAULT_WINDOW)
        st.session_state["qss_market_regime_benchmark"] = payload.get("market_regime_benchmark") or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK
        st.session_state["qss_underperformance_guardrail_enabled"] = bool(
            payload.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["qss_underperformance_guardrail_window_months"] = int(
            payload.get("underperformance_guardrail_window_months") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["qss_underperformance_guardrail_threshold"] = float(
            (payload.get("underperformance_guardrail_threshold") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD) * 100.0
        )
        st.session_state["qss_drawdown_guardrail_enabled"] = bool(
            payload.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["qss_drawdown_guardrail_window_months"] = int(
            payload.get("drawdown_guardrail_window_months") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["qss_drawdown_guardrail_strategy_threshold"] = float(
            (payload.get("drawdown_guardrail_strategy_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD) * 100.0
        )
        st.session_state["qss_drawdown_guardrail_gap_threshold"] = float(
            (payload.get("drawdown_guardrail_gap_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD) * 100.0
        )
        st.session_state["qss_min_price_filter"] = float(payload.get("min_price_filter") or ETF_REAL_MONEY_DEFAULT_MIN_PRICE)
        st.session_state["qss_min_history_months_filter"] = int(
            payload.get("min_history_months_filter") or STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS
        )
        st.session_state["qss_min_avg_dollar_volume_20d_m_filter"] = float(
            payload.get("min_avg_dollar_volume_20d_m_filter") or STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M
        )
        st.session_state["qss_transaction_cost_bps"] = float(payload.get("transaction_cost_bps") or ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS)
        st.session_state["qss_benchmark_contract"] = _benchmark_contract_value_to_label(
            payload.get("benchmark_contract") or STRICT_DEFAULT_BENCHMARK_CONTRACT
        )
        st.session_state["qss_benchmark_ticker"] = str(payload.get("benchmark_ticker") or ETF_REAL_MONEY_DEFAULT_BENCHMARK).strip().upper()
        st.session_state["qss_promotion_min_benchmark_coverage"] = float(
            (payload.get("promotion_min_benchmark_coverage") or STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE) * 100.0
        )
        st.session_state["qss_promotion_min_net_cagr_spread"] = float(
            (payload.get("promotion_min_net_cagr_spread") or STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD) * 100.0
        )
        st.session_state["qss_promotion_min_liquidity_clean_coverage"] = float(
            (payload.get("promotion_min_liquidity_clean_coverage") or STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE) * 100.0
        )
        st.session_state["qss_promotion_max_underperformance_share"] = float(
            (payload.get("promotion_max_underperformance_share") or STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE) * 100.0
        )
        st.session_state["qss_promotion_min_worst_rolling_excess_return"] = float(
            (payload.get("promotion_min_worst_rolling_excess_return") or STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN) * 100.0
        )
        st.session_state["qss_promotion_max_strategy_drawdown"] = float(
            (payload.get("promotion_max_strategy_drawdown") or STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN) * 100.0
        )
        st.session_state["qss_promotion_max_drawdown_gap_vs_benchmark"] = float(
            (payload.get("promotion_max_drawdown_gap_vs_benchmark") or STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK) * 100.0
        )
    elif strategy_key == "quality_snapshot_strict_quarterly_prototype":
        st.session_state["qsqp_universe_mode"] = "Preset" if universe_mode == "preset" and preset_name in QUALITY_STRICT_PRESETS else "Manual"
        if st.session_state["qsqp_universe_mode"] == "Preset":
            st.session_state["qsqp_preset"] = preset_name
        else:
            st.session_state["qsqp_manual_tickers"] = tickers_text
        st.session_state["qsqp_start"] = start_date
        st.session_state["qsqp_end"] = end_date
        st.session_state["qsqp_top_n"] = int(payload.get("top") or 2)
        st.session_state["qsqp_timeframe"] = payload.get("timeframe") or "1d"
        st.session_state["qsqp_option"] = payload.get("option") or "month_end"
        st.session_state["qsqp_quality_factors"] = payload.get("quality_factors") or QUALITY_STRICT_DEFAULT_FACTORS
        st.session_state["qsqp_universe_contract"] = next(
            (label for label, value in STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.items() if value == (payload.get("universe_contract") or STATIC_MANAGED_RESEARCH_UNIVERSE)),
            "Static Managed Research Universe",
        )
        st.session_state["qsqp_trend_filter_enabled"] = bool(payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED))
        st.session_state["qsqp_trend_filter_window"] = int(payload.get("trend_filter_window") or STRICT_TREND_FILTER_DEFAULT_WINDOW)
        st.session_state["qsqp_market_regime_enabled"] = bool(payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED))
        st.session_state["qsqp_market_regime_window"] = int(payload.get("market_regime_window") or STRICT_MARKET_REGIME_DEFAULT_WINDOW)
        st.session_state["qsqp_market_regime_benchmark"] = payload.get("market_regime_benchmark") or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK
    elif strategy_key == "value_snapshot_strict_annual":
        st.session_state["vss_universe_mode"] = "Preset" if universe_mode == "preset" and preset_name in VALUE_STRICT_PRESETS else "Manual"
        if st.session_state["vss_universe_mode"] == "Preset":
            st.session_state["vss_preset"] = preset_name
        else:
            st.session_state["vss_manual_tickers"] = tickers_text
        st.session_state["vss_start"] = start_date
        st.session_state["vss_end"] = end_date
        st.session_state["vss_top_n"] = int(payload.get("top") or 10)
        st.session_state["vss_timeframe"] = payload.get("timeframe") or "1d"
        st.session_state["vss_option"] = payload.get("option") or "month_end"
        st.session_state["vss_value_factors"] = payload.get("value_factors") or VALUE_STRICT_DEFAULT_FACTORS
        st.session_state["vss_universe_contract"] = next(
            (label for label, value in STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.items() if value == (payload.get("universe_contract") or STATIC_MANAGED_RESEARCH_UNIVERSE)),
            "Static Managed Research Universe",
        )
        st.session_state["vss_trend_filter_enabled"] = bool(payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED))
        st.session_state["vss_trend_filter_window"] = int(payload.get("trend_filter_window") or STRICT_TREND_FILTER_DEFAULT_WINDOW)
        st.session_state["vss_market_regime_enabled"] = bool(payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED))
        st.session_state["vss_market_regime_window"] = int(payload.get("market_regime_window") or STRICT_MARKET_REGIME_DEFAULT_WINDOW)
        st.session_state["vss_market_regime_benchmark"] = payload.get("market_regime_benchmark") or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK
        st.session_state["vss_underperformance_guardrail_enabled"] = bool(
            payload.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["vss_underperformance_guardrail_window_months"] = int(
            payload.get("underperformance_guardrail_window_months") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["vss_underperformance_guardrail_threshold"] = float(
            (payload.get("underperformance_guardrail_threshold") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD) * 100.0
        )
        st.session_state["vss_drawdown_guardrail_enabled"] = bool(
            payload.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["vss_drawdown_guardrail_window_months"] = int(
            payload.get("drawdown_guardrail_window_months") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["vss_drawdown_guardrail_strategy_threshold"] = float(
            (payload.get("drawdown_guardrail_strategy_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD) * 100.0
        )
        st.session_state["vss_drawdown_guardrail_gap_threshold"] = float(
            (payload.get("drawdown_guardrail_gap_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD) * 100.0
        )
        st.session_state["vss_min_price_filter"] = float(payload.get("min_price_filter") or ETF_REAL_MONEY_DEFAULT_MIN_PRICE)
        st.session_state["vss_min_history_months_filter"] = int(
            payload.get("min_history_months_filter") or STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS
        )
        st.session_state["vss_min_avg_dollar_volume_20d_m_filter"] = float(
            payload.get("min_avg_dollar_volume_20d_m_filter") or STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M
        )
        st.session_state["vss_transaction_cost_bps"] = float(payload.get("transaction_cost_bps") or ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS)
        st.session_state["vss_benchmark_contract"] = _benchmark_contract_value_to_label(
            payload.get("benchmark_contract") or STRICT_DEFAULT_BENCHMARK_CONTRACT
        )
        st.session_state["vss_benchmark_ticker"] = str(payload.get("benchmark_ticker") or ETF_REAL_MONEY_DEFAULT_BENCHMARK).strip().upper()
        st.session_state["vss_promotion_min_benchmark_coverage"] = float(
            (payload.get("promotion_min_benchmark_coverage") or STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE) * 100.0
        )
        st.session_state["vss_promotion_min_net_cagr_spread"] = float(
            (payload.get("promotion_min_net_cagr_spread") or STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD) * 100.0
        )
        st.session_state["vss_promotion_min_liquidity_clean_coverage"] = float(
            (payload.get("promotion_min_liquidity_clean_coverage") or STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE) * 100.0
        )
        st.session_state["vss_promotion_max_underperformance_share"] = float(
            (payload.get("promotion_max_underperformance_share") or STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE) * 100.0
        )
        st.session_state["vss_promotion_min_worst_rolling_excess_return"] = float(
            (payload.get("promotion_min_worst_rolling_excess_return") or STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN) * 100.0
        )
        st.session_state["vss_promotion_max_strategy_drawdown"] = float(
            (payload.get("promotion_max_strategy_drawdown") or STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN) * 100.0
        )
        st.session_state["vss_promotion_max_drawdown_gap_vs_benchmark"] = float(
            (payload.get("promotion_max_drawdown_gap_vs_benchmark") or STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK) * 100.0
        )
    elif strategy_key == "value_snapshot_strict_quarterly_prototype":
        st.session_state["vsqp_universe_mode"] = "Preset" if universe_mode == "preset" and preset_name in VALUE_STRICT_PRESETS else "Manual"
        if st.session_state["vsqp_universe_mode"] == "Preset":
            st.session_state["vsqp_preset"] = preset_name
        else:
            st.session_state["vsqp_manual_tickers"] = tickers_text
        st.session_state["vsqp_start"] = start_date
        st.session_state["vsqp_end"] = end_date
        st.session_state["vsqp_top_n"] = int(payload.get("top") or 10)
        st.session_state["vsqp_timeframe"] = payload.get("timeframe") or "1d"
        st.session_state["vsqp_option"] = payload.get("option") or "month_end"
        st.session_state["vsqp_value_factors"] = payload.get("value_factors") or VALUE_STRICT_DEFAULT_FACTORS
        st.session_state["vsqp_universe_contract"] = next(
            (label for label, value in STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.items() if value == (payload.get("universe_contract") or STATIC_MANAGED_RESEARCH_UNIVERSE)),
            "Static Managed Research Universe",
        )
        st.session_state["vsqp_trend_filter_enabled"] = bool(payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED))
        st.session_state["vsqp_trend_filter_window"] = int(payload.get("trend_filter_window") or STRICT_TREND_FILTER_DEFAULT_WINDOW)
        st.session_state["vsqp_market_regime_enabled"] = bool(payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED))
        st.session_state["vsqp_market_regime_window"] = int(payload.get("market_regime_window") or STRICT_MARKET_REGIME_DEFAULT_WINDOW)
        st.session_state["vsqp_market_regime_benchmark"] = payload.get("market_regime_benchmark") or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK
    elif strategy_key == "quality_value_snapshot_strict_annual":
        st.session_state["qvss_universe_mode"] = "Preset" if universe_mode == "preset" and preset_name in QUALITY_STRICT_PRESETS else "Manual"
        if st.session_state["qvss_universe_mode"] == "Preset":
            st.session_state["qvss_preset"] = preset_name
        else:
            st.session_state["qvss_manual_tickers"] = tickers_text
        st.session_state["qvss_start"] = start_date
        st.session_state["qvss_end"] = end_date
        st.session_state["qvss_top_n"] = int(payload.get("top") or 10)
        st.session_state["qvss_timeframe"] = payload.get("timeframe") or "1d"
        st.session_state["qvss_option"] = payload.get("option") or "month_end"
        st.session_state["qvss_quality_factors"] = payload.get("quality_factors") or QUALITY_STRICT_DEFAULT_FACTORS
        st.session_state["qvss_value_factors"] = payload.get("value_factors") or VALUE_STRICT_DEFAULT_FACTORS
        st.session_state["qvss_universe_contract"] = next(
            (label for label, value in STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.items() if value == (payload.get("universe_contract") or STATIC_MANAGED_RESEARCH_UNIVERSE)),
            "Static Managed Research Universe",
        )
        st.session_state["qvss_trend_filter_enabled"] = bool(payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED))
        st.session_state["qvss_trend_filter_window"] = int(payload.get("trend_filter_window") or STRICT_TREND_FILTER_DEFAULT_WINDOW)
        st.session_state["qvss_market_regime_enabled"] = bool(payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED))
        st.session_state["qvss_market_regime_window"] = int(payload.get("market_regime_window") or STRICT_MARKET_REGIME_DEFAULT_WINDOW)
        st.session_state["qvss_market_regime_benchmark"] = payload.get("market_regime_benchmark") or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK
        st.session_state["qvss_underperformance_guardrail_enabled"] = bool(
            payload.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["qvss_underperformance_guardrail_window_months"] = int(
            payload.get("underperformance_guardrail_window_months") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["qvss_underperformance_guardrail_threshold"] = float(
            (payload.get("underperformance_guardrail_threshold") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD) * 100.0
        )
        st.session_state["qvss_drawdown_guardrail_enabled"] = bool(
            payload.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["qvss_drawdown_guardrail_window_months"] = int(
            payload.get("drawdown_guardrail_window_months") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["qvss_drawdown_guardrail_strategy_threshold"] = float(
            (payload.get("drawdown_guardrail_strategy_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD) * 100.0
        )
        st.session_state["qvss_drawdown_guardrail_gap_threshold"] = float(
            (payload.get("drawdown_guardrail_gap_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD) * 100.0
        )
        st.session_state["qvss_min_price_filter"] = float(payload.get("min_price_filter") or ETF_REAL_MONEY_DEFAULT_MIN_PRICE)
        st.session_state["qvss_min_history_months_filter"] = int(
            payload.get("min_history_months_filter") or STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS
        )
        st.session_state["qvss_min_avg_dollar_volume_20d_m_filter"] = float(
            payload.get("min_avg_dollar_volume_20d_m_filter") or STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M
        )
        st.session_state["qvss_transaction_cost_bps"] = float(payload.get("transaction_cost_bps") or ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS)
        st.session_state["qvss_benchmark_contract"] = _benchmark_contract_value_to_label(
            payload.get("benchmark_contract") or STRICT_DEFAULT_BENCHMARK_CONTRACT
        )
        st.session_state["qvss_benchmark_ticker"] = str(payload.get("benchmark_ticker") or ETF_REAL_MONEY_DEFAULT_BENCHMARK).strip().upper()
        st.session_state["qvss_promotion_min_benchmark_coverage"] = float(
            (payload.get("promotion_min_benchmark_coverage") or STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE) * 100.0
        )
        st.session_state["qvss_promotion_min_net_cagr_spread"] = float(
            (payload.get("promotion_min_net_cagr_spread") or STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD) * 100.0
        )
        st.session_state["qvss_promotion_min_liquidity_clean_coverage"] = float(
            (payload.get("promotion_min_liquidity_clean_coverage") or STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE) * 100.0
        )
        st.session_state["qvss_promotion_max_underperformance_share"] = float(
            (payload.get("promotion_max_underperformance_share") or STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE) * 100.0
        )
        st.session_state["qvss_promotion_min_worst_rolling_excess_return"] = float(
            (payload.get("promotion_min_worst_rolling_excess_return") or STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN) * 100.0
        )
        st.session_state["qvss_promotion_max_strategy_drawdown"] = float(
            (payload.get("promotion_max_strategy_drawdown") or STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN) * 100.0
        )
        st.session_state["qvss_promotion_max_drawdown_gap_vs_benchmark"] = float(
            (payload.get("promotion_max_drawdown_gap_vs_benchmark") or STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK) * 100.0
        )
    elif strategy_key == "quality_value_snapshot_strict_quarterly_prototype":
        st.session_state["qvqp_universe_mode"] = "Preset" if universe_mode == "preset" and preset_name in QUALITY_STRICT_PRESETS else "Manual"
        if st.session_state["qvqp_universe_mode"] == "Preset":
            st.session_state["qvqp_preset"] = preset_name
        else:
            st.session_state["qvqp_manual_tickers"] = tickers_text
        st.session_state["qvqp_start"] = start_date
        st.session_state["qvqp_end"] = end_date
        st.session_state["qvqp_top_n"] = int(payload.get("top") or 10)
        st.session_state["qvqp_timeframe"] = payload.get("timeframe") or "1d"
        st.session_state["qvqp_option"] = payload.get("option") or "month_end"
        st.session_state["qvqp_quality_factors"] = payload.get("quality_factors") or QUALITY_STRICT_DEFAULT_FACTORS
        st.session_state["qvqp_value_factors"] = payload.get("value_factors") or VALUE_STRICT_DEFAULT_FACTORS
        st.session_state["qvqp_universe_contract"] = next(
            (label for label, value in STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.items() if value == (payload.get("universe_contract") or STATIC_MANAGED_RESEARCH_UNIVERSE)),
            "Static Managed Research Universe",
        )
        st.session_state["qvqp_trend_filter_enabled"] = bool(payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED))
        st.session_state["qvqp_trend_filter_window"] = int(payload.get("trend_filter_window") or STRICT_TREND_FILTER_DEFAULT_WINDOW)
        st.session_state["qvqp_market_regime_enabled"] = bool(payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED))
        st.session_state["qvqp_market_regime_window"] = int(payload.get("market_regime_window") or STRICT_MARKET_REGIME_DEFAULT_WINDOW)
        st.session_state["qvqp_market_regime_benchmark"] = payload.get("market_regime_benchmark") or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK

    st.session_state.backtest_prefill_pending = False


def _build_snapshot_selection_history(result_df: pd.DataFrame) -> pd.DataFrame:
    if result_df.empty or "Selected Count" not in result_df.columns:
        return pd.DataFrame()

    selection_df = result_df.copy()

    def _first_series(frame: pd.DataFrame, column: str) -> pd.Series | None:
        if column not in frame.columns:
            return None
        value = frame[column]
        if isinstance(value, pd.DataFrame):
            return value.iloc[:, 0]
        return value

    if selection_df.columns.duplicated().any():
        selection_df = selection_df.loc[:, ~selection_df.columns.duplicated()].copy()

    selection_df["Date"] = pd.to_datetime(selection_df["Date"], errors="coerce")
    selection_df = selection_df.dropna(subset=["Date"])

    if "Rebalancing" in selection_df.columns:
        selection_df = selection_df[selection_df["Rebalancing"].fillna(False)]

    selected_count_series = _first_series(selection_df, "Selected Count")
    raw_selected_count_series = _first_series(selection_df, "Raw Selected Count")
    selected_count = selected_count_series.fillna(0) if selected_count_series is not None else 0
    raw_selected_count = raw_selected_count_series.fillna(0) if raw_selected_count_series is not None else 0
    selection_df = selection_df[(selected_count > 0) | (raw_selected_count > 0)].copy()
    if selection_df.empty:
        return pd.DataFrame()

    keep_columns = [
        "Date",
        "Raw Selected Ticker",
        "Raw Selected Count",
        "Raw Selected Score",
        "Overlay Rejected Ticker",
        "Overlay Rejected Count",
        "Regime Blocked Ticker",
        "Regime Blocked Count",
        "Next Ticker",
        "Selected Count",
        "Selected Score",
        "Trend Filter Enabled",
        "Trend Filter Column",
        "Market Regime Enabled",
        "Market Regime Benchmark",
        "Market Regime Column",
        "Market Regime State",
        "Cash",
        "Total Balance",
        "Total Return",
    ]
    existing = [column for column in keep_columns if column in selection_df.columns]
    selection_df = selection_df[existing].copy()
    rename_map = {
        "Next Ticker": "Selected Tickers",
        "Selected Score": "Selection Score",
        "Raw Selected Ticker": "Raw Selected Tickers",
        "Raw Selected Score": "Raw Selection Score",
        "Overlay Rejected Ticker": "Overlay Rejected Tickers",
        "Regime Blocked Ticker": "Regime Blocked Tickers",
    }
    selection_df = selection_df.rename(columns=rename_map).reset_index(drop=True)

    list_columns = [
        "Raw Selected Tickers",
        "Overlay Rejected Tickers",
        "Regime Blocked Tickers",
        "Selected Tickers",
    ]
    score_list_columns = [
        "Raw Selection Score",
        "Selection Score",
    ]
    for column in list_columns:
        if column in selection_df.columns:
            selection_df[column] = selection_df[column].apply(_stringify_symbol_list)
    for column in score_list_columns:
        if column in selection_df.columns:
            selection_df[column] = selection_df[column].apply(_stringify_score_list)

    cash_series = _first_series(selection_df, "Cash")
    total_balance_series = _first_series(selection_df, "Total Balance")
    if cash_series is not None and total_balance_series is not None:
        total_balance = pd.to_numeric(total_balance_series, errors="coerce")
        cash_balance = pd.to_numeric(cash_series, errors="coerce").fillna(0.0)
        selection_df["Cash Share Ratio"] = np.where(
            total_balance > 0,
            cash_balance / total_balance,
            np.nan,
        )
    else:
        selection_df["Cash Share Ratio"] = np.nan

    def _build_interpretation(row: pd.Series) -> str:
        raw_count = int(row.get("Raw Selected Count") or 0)
        rejected_count = int(row.get("Overlay Rejected Count") or 0)
        regime_blocked_count = int(row.get("Regime Blocked Count") or 0)
        selected_count = int(row.get("Selected Count") or 0)
        regime_state = str(row.get("Market Regime State") or "").strip().lower()
        regime_benchmark = str(row.get("Market Regime Benchmark") or "").strip() or "benchmark"
        cash_share = row.get("Cash Share Ratio")
        cash_share_text = (
            f"{float(cash_share) * 100:.1f}%"
            if pd.notna(cash_share)
            else "n/a"
        )

        if raw_count <= 0:
            return "No usable ranked candidates were available at this rebalance, so the portfolio stayed in cash."
        if regime_blocked_count > 0 and regime_state == "risk_off":
            return (
                f"Market regime overlay moved the portfolio fully to cash because `{regime_benchmark}` "
                f"was in risk-off state at this rebalance. It blocked {regime_blocked_count} post-filter candidate(s)."
            )
        if selected_count <= 0 and rejected_count > 0:
            return f"Trend overlay rejected all {raw_count} raw candidates, so the portfolio moved fully to cash."
        if rejected_count > 0:
            return (
                f"Trend overlay kept {selected_count} of {raw_count} raw candidates and sent "
                f"{rejected_count} name(s) to cash. Cash share after rebalance: {cash_share_text}."
            )
        if pd.notna(cash_share) and float(cash_share) > 0:
            return (
                f"All final candidates passed the current filters, but the portfolio still kept "
                f"{cash_share_text} in cash because fewer names were investable than the nominal top-N."
            )
        return "All selected candidates passed the current rules and the portfolio remained fully invested."

    selection_df["Interpretation"] = selection_df.apply(_build_interpretation, axis=1)
    if "Cash Share Ratio" in selection_df.columns:
        selection_df["Cash Share"] = selection_df["Cash Share Ratio"].apply(
            lambda value: f"{float(value) * 100:.1f}%" if pd.notna(value) else ""
        )

    return selection_df


def _build_overlay_rejection_frequency_view(selection_df: pd.DataFrame) -> pd.DataFrame:
    if selection_df.empty or "Overlay Rejected Tickers" not in selection_df.columns:
        return pd.DataFrame()

    exploded_rows: list[dict[str, Any]] = []
    for _, row in selection_df.iterrows():
        row_date = pd.to_datetime(row.get("Date"), errors="coerce")
        rejected_tickers = _normalize_symbol_sequence(row.get("Overlay Rejected Tickers"))
        for symbol in rejected_tickers:
            exploded_rows.append({"symbol": symbol, "Date": row_date})

    if not exploded_rows:
        return pd.DataFrame()

    exploded_df = pd.DataFrame(exploded_rows)
    rejection_df = (
        exploded_df.groupby("symbol", as_index=False)
        .agg(
            RejectedEvents=("Date", "size"),
            FirstRejected=("Date", "min"),
            LastRejected=("Date", "max"),
        )
        .sort_values(["RejectedEvents", "symbol"], ascending=[False, True])
        .reset_index(drop=True)
    )
    rejection_df["FirstRejected"] = pd.to_datetime(rejection_df["FirstRejected"]).dt.strftime("%Y-%m-%d")
    rejection_df["LastRejected"] = pd.to_datetime(rejection_df["LastRejected"]).dt.strftime("%Y-%m-%d")
    return rejection_df


def _build_market_regime_event_view(selection_df: pd.DataFrame) -> pd.DataFrame:
    if selection_df.empty or "Market Regime State" not in selection_df.columns:
        return pd.DataFrame()

    regime_df = selection_df.copy()
    regime_df = regime_df[regime_df["Market Regime State"].astype(str).str.lower() == "risk_off"].copy()
    if regime_df.empty:
        return pd.DataFrame()

    keep = [
        "Date",
        "Market Regime Benchmark",
        "Market Regime Column",
        "Raw Selected Count",
        "Regime Blocked Count",
        "Regime Blocked Tickers",
        "Cash Share",
    ]
    keep = [column for column in keep if column in regime_df.columns]
    event_df = regime_df[keep].copy()
    event_df["Date"] = pd.to_datetime(event_df["Date"]).dt.strftime("%Y-%m-%d")
    return event_df.reset_index(drop=True)


def _build_selection_interpretation_summary(selection_df: pd.DataFrame) -> pd.DataFrame:
    if selection_df.empty:
        return pd.DataFrame()

    raw_candidate_events = int(pd.to_numeric(selection_df.get("Raw Selected Count"), errors="coerce").fillna(0).sum())
    final_selected_events = int(pd.to_numeric(selection_df.get("Selected Count"), errors="coerce").fillna(0).sum())
    overlay_rejections = int(pd.to_numeric(selection_df.get("Overlay Rejected Count"), errors="coerce").fillna(0).sum())
    regime_rejections = int(pd.to_numeric(selection_df.get("Regime Blocked Count"), errors="coerce").fillna(0).sum())
    regime_cash_rebalances = int(
        (
            selection_df.get("Market Regime State", pd.Series(dtype=str))
            .astype(str)
            .str.lower()
            .eq("risk_off")
        ).sum()
    )
    cash_only_rebalances = int(
        (pd.to_numeric(selection_df.get("Selected Count"), errors="coerce").fillna(0) <= 0).sum()
    )
    avg_selected_count = float(
        pd.to_numeric(selection_df.get("Selected Count"), errors="coerce").fillna(0).mean()
    )
    cash_share_series = pd.to_numeric(selection_df.get("Cash Share Ratio"), errors="coerce")
    avg_cash_share = float(cash_share_series.fillna(0).mean()) if cash_share_series is not None else 0.0

    return pd.DataFrame(
        [
            {
                "Raw Candidate Events": raw_candidate_events,
                "Final Selected Events": final_selected_events,
                "Overlay Rejections": overlay_rejections,
                "Regime Blocked Events": regime_rejections,
                "Regime Cash Rebalances": regime_cash_rebalances,
                "Cash-Only Rebalances": cash_only_rebalances,
                "Avg Selected Count": round(avg_selected_count, 2),
                "Avg Cash Share": f"{avg_cash_share * 100:.1f}%",
            }
        ]
    )


def _normalize_symbol_sequence(value: Any) -> list[str]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(symbol).strip() for symbol in value if str(symbol).strip()]

    raw = str(value).strip()
    if not raw:
        return []

    raw = raw.strip("[]")
    cleaned = [part.strip().strip("'").strip('"') for part in raw.split(",")]
    return [symbol for symbol in cleaned if symbol]


def _stringify_symbol_list(value: Any) -> str:
    symbols = _normalize_symbol_sequence(value)
    return ", ".join(symbols)


def _stringify_score_list(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    if isinstance(value, (list, tuple, set)):
        return ", ".join(f"{float(item):.3f}" for item in value)
    return str(value)


def _build_selection_frequency_view(selection_df: pd.DataFrame) -> pd.DataFrame:
    if selection_df.empty or "Selected Tickers" not in selection_df.columns:
        return pd.DataFrame()

    exploded_rows: list[dict[str, Any]] = []
    for _, row in selection_df.iterrows():
        row_date = pd.to_datetime(row.get("Date"), errors="coerce")
        selected_tickers = _normalize_symbol_sequence(row.get("Selected Tickers"))
        for symbol in selected_tickers:
            exploded_rows.append({"symbol": symbol, "Date": row_date})

    if not exploded_rows:
        return pd.DataFrame()

    exploded_df = pd.DataFrame(exploded_rows)
    frequency_df = (
        exploded_df.groupby("symbol", as_index=False)
        .agg(
            SelectedEvents=("Date", "size"),
            FirstSelected=("Date", "min"),
            LastSelected=("Date", "max"),
        )
        .sort_values(["SelectedEvents", "symbol"], ascending=[False, True])
        .reset_index(drop=True)
    )
    frequency_df["FirstSelected"] = pd.to_datetime(frequency_df["FirstSelected"]).dt.strftime("%Y-%m-%d")
    frequency_df["LastSelected"] = pd.to_datetime(frequency_df["LastSelected"]).dt.strftime("%Y-%m-%d")
    return frequency_df


def _render_snapshot_selection_history(
    result_df: pd.DataFrame,
    *,
    strategy_name: str,
    factor_names: list[str],
    snapshot_mode: str | None,
    snapshot_source: str | None,
) -> None:
    try:
        selection_df = _build_snapshot_selection_history(result_df)
    except Exception as exc:  # pragma: no cover - UI fallback path
        st.warning(
            "Selection history could not be rendered for this run payload. "
            "Try rerunning the backtest to rebuild the latest result bundle."
        )
        st.caption(f"Renderer detail: {type(exc).__name__}: {exc}")
        return

    if selection_df.empty:
        st.info("No active selection history is available for this run.")
        return

    first_active = pd.to_datetime(selection_df.iloc[0]["Date"]).strftime("%Y-%m-%d")
    event_count = len(selection_df)
    distinct_names = sorted(
        {
            symbol.strip()
            for value in selection_df["Selected Tickers"].dropna()
            for symbol in _normalize_symbol_sequence(value)
            if symbol.strip()
        }
    )
    overlay_active = (
        "Trend Filter Enabled" in selection_df.columns
        and selection_df["Trend Filter Enabled"].fillna(False).astype(bool).any()
    )
    regime_active = (
        "Market Regime Enabled" in selection_df.columns
        and selection_df["Market Regime Enabled"].fillna(False).astype(bool).any()
    )

    st.caption(
        "이 화면은 strict annual 전략 검증에서 가장 실무적인 질문인 "
        "‘각 리밸런싱 날짜에 실제로 어떤 종목이 선택되었는가?’를 읽기 쉽게 보여주기 위한 뷰입니다."
    )
    left, center, right = st.columns(3, gap="large")
    with left:
        st.metric("First Active Date", first_active)
    with center:
        st.metric("Active Rebalances", f"{event_count}")
    with right:
        st.metric("Distinct Selected Names", f"{len(distinct_names)}")

    meta_df = pd.DataFrame(
        [
            {
                "Strategy": strategy_name,
                "Snapshot Mode": snapshot_mode,
                "Snapshot Source": snapshot_source or "n/a",
                "Factors": ", ".join(factor_names) if factor_names else "n/a",
                "Trend Overlay": (
                    selection_df.loc[selection_df["Trend Filter Enabled"].fillna(False), "Trend Filter Column"].iloc[0]
                    if overlay_active and "Trend Filter Column" in selection_df.columns
                    else "off"
                ),
                "Market Regime Overlay": (
                    (
                        f"{selection_df.loc[selection_df['Market Regime Enabled'].fillna(False), 'Market Regime Benchmark'].iloc[0]} / "
                        f"{selection_df.loc[selection_df['Market Regime Enabled'].fillna(False), 'Market Regime Column'].iloc[0]}"
                    )
                    if regime_active
                    else "off"
                ),
            }
        ]
    )
    st.dataframe(meta_df, use_container_width=True, hide_index=True)
    if overlay_active:
        st.caption(
            "Raw Selected는 팩터 랭킹으로 뽑힌 1차 후보이고, Final Selected는 오버레이까지 통과한 실제 보유 후보입니다. Overlay Rejected는 월말 추세 필터를 통과하지 못해 해당 리밸런싱에서 현금으로 전환된 종목입니다."
        )
    if regime_active:
        st.caption(
            "Market Regime은 개별 종목 필터가 아니라 시장 전체 상태를 보는 상위 오버레이입니다. risk-off로 판정된 리밸런싱에서는 strict factor 후보가 있어도 포트폴리오 전체가 현금으로 이동할 수 있습니다."
        )

    history_tab, interpretation_tab, frequency_tab = st.tabs(["History", "Interpretation", "Selection Frequency"])
    with history_tab:
        cash_title_col, cash_help_col = st.columns([0.92, 0.08], gap="small")
        with cash_title_col:
            st.caption("`Cash Share`는 각 리밸런싱 직후 포트폴리오에서 현금으로 남아 있는 비중입니다.")
        with cash_help_col:
            _render_cash_share_help_popover()
        st.dataframe(selection_df.drop(columns=["Cash Share Ratio"], errors="ignore"), use_container_width=True, hide_index=True)
    with interpretation_tab:
        interpretation_summary_df = _build_selection_interpretation_summary(selection_df)
        if not interpretation_summary_df.empty:
            summary_title_col, summary_help_col = st.columns([0.92, 0.08], gap="small")
            with summary_title_col:
                st.markdown("##### Interpretation Summary")
            with summary_help_col:
                _render_interpretation_summary_help_popover()
            st.caption("참고: 이 표의 Raw / Final 값은 전체 모집군 크기가 아니라 리밸런싱별 선택 이벤트의 누적 합계입니다.")
            st.dataframe(interpretation_summary_df, use_container_width=True, hide_index=True)
        rejection_df = _build_overlay_rejection_frequency_view(selection_df)
        if not rejection_df.empty:
            reject_title_col, reject_help_col = st.columns([0.92, 0.08], gap="small")
            with reject_title_col:
                st.markdown("##### Overlay Rejection Frequency")
            with reject_help_col:
                _render_overlay_rejection_frequency_help_popover()
            st.dataframe(rejection_df, use_container_width=True, hide_index=True)
        else:
            st.caption("이번 실행에서는 오버레이로 제외된 종목이 기록되지 않았습니다.")
        regime_event_df = _build_market_regime_event_view(selection_df)
        if not regime_event_df.empty:
            regime_title_col, regime_help_col = st.columns([0.92, 0.08], gap="small")
            with regime_title_col:
                st.markdown("##### Market Regime Events")
            with regime_help_col:
                _render_market_regime_events_help_popover()
            st.dataframe(regime_event_df, use_container_width=True, hide_index=True)
    with frequency_tab:
        frequency_df = _build_selection_frequency_view(selection_df)
        if frequency_df.empty:
            st.info("이번 실행에서는 선택 빈도 요약을 만들 수 있는 데이터가 없습니다.")
        else:
            st.caption("이 표는 전략이 여러 리밸런싱에 걸쳐 반복적으로 선택하는 종목이 무엇인지 보기 위한 요약입니다.")
            st.dataframe(frequency_df, use_container_width=True, hide_index=True)


def _render_persistent_backtest_history() -> None:
    st.markdown("### Persistent Backtest History")
    history = load_backtest_run_history(limit=100)
    if not history:
        st.info("No persisted backtest history found yet.")
        return

    st.caption(f"Path: {BACKTEST_HISTORY_FILE}")
    history_df, history_records = _build_backtest_history_rows(history)

    filter_col, search_col = st.columns([1.1, 1.4], gap="large")
    with filter_col:
        selected_run_kinds = st.multiselect(
            "Run Kind Filter",
            options=sorted(history_df["run_kind"].dropna().unique().tolist()),
            default=sorted(history_df["run_kind"].dropna().unique().tolist()),
            key="backtest_history_run_kind_filter",
        )
    with search_col:
        search_text = st.text_input(
            "Search",
            value="",
            placeholder="strategy, ticker, preset, selected strategies",
            key="backtest_history_search_text",
        ).strip().lower()

    date_filter_col, sort_filter_col = st.columns([1.2, 1.0], gap="large")
    recorded_dates = pd.to_datetime(history_df["recorded_at"], errors="coerce")
    min_recorded_date = recorded_dates.min().date() if not recorded_dates.isna().all() else date.today()
    max_recorded_date = recorded_dates.max().date() if not recorded_dates.isna().all() else date.today()
    with date_filter_col:
        recorded_range = st.date_input(
            "Recorded Date Range",
            value=(min_recorded_date, max_recorded_date),
            min_value=min_recorded_date,
            max_value=max_recorded_date,
            key="backtest_history_recorded_range",
        )
    with sort_filter_col:
        sort_by = st.selectbox(
            "Sort",
            options=[
                "Recorded At (Newest)",
                "Recorded At (Oldest)",
                "End Balance (High)",
                "CAGR (High)",
                "Sharpe Ratio (High)",
                "Drawdown (Best)",
            ],
            index=0,
            key="backtest_history_sort_by",
        )

    with st.expander("Metric Threshold Filters", expanded=False):
        threshold_cols = st.columns(4, gap="large")
        with threshold_cols[0]:
            use_min_end_balance = st.checkbox("Min End Balance", value=False, key="history_filter_use_end_balance")
            min_end_balance = st.number_input(
                "Threshold",
                min_value=0.0,
                value=10000.0,
                step=1000.0,
                key="history_filter_min_end_balance",
                disabled=not use_min_end_balance,
            )
        with threshold_cols[1]:
            use_min_cagr = st.checkbox("Min CAGR", value=False, key="history_filter_use_cagr")
            min_cagr = st.number_input(
                "Threshold ",
                value=0.0,
                step=0.01,
                format="%.4f",
                key="history_filter_min_cagr",
                disabled=not use_min_cagr,
            )
        with threshold_cols[2]:
            use_min_sharpe = st.checkbox("Min Sharpe Ratio", value=False, key="history_filter_use_sharpe")
            min_sharpe = st.number_input(
                "Threshold  ",
                value=0.0,
                step=0.1,
                format="%.4f",
                key="history_filter_min_sharpe",
                disabled=not use_min_sharpe,
            )
        with threshold_cols[3]:
            use_max_drawdown = st.checkbox("Max Drawdown", value=False, key="history_filter_use_drawdown")
            max_drawdown = st.number_input(
                "Threshold   ",
                value=-0.20,
                step=0.01,
                format="%.4f",
                key="history_filter_max_drawdown",
                disabled=not use_max_drawdown,
            )

    recorded_start, recorded_end = _normalize_recorded_date_range(
        recorded_range,
        fallback_start=min_recorded_date,
        fallback_end=max_recorded_date,
    )

    filtered_indices = []
    for idx, row in history_df.iterrows():
        if selected_run_kinds and row["run_kind"] not in selected_run_kinds:
            continue
        if search_text and search_text not in str(row["_search_text"]):
            continue
        row_recorded_at = pd.to_datetime(row["recorded_at"], errors="coerce")
        if pd.notna(row_recorded_at):
            row_date = row_recorded_at.date()
            if row_date < recorded_start or row_date > recorded_end:
                continue
        if use_min_end_balance and (
            pd.isna(row["end_balance"]) or float(row["end_balance"]) < float(min_end_balance)
        ):
            continue
        if use_min_cagr and (
            pd.isna(row["cagr"]) or float(row["cagr"]) < float(min_cagr)
        ):
            continue
        if use_min_sharpe and (
            pd.isna(row["sharpe_ratio"]) or float(row["sharpe_ratio"]) < float(min_sharpe)
        ):
            continue
        if use_max_drawdown and (
            pd.isna(row["drawdown"]) or float(row["drawdown"]) < float(max_drawdown)
        ):
            continue
        filtered_indices.append(idx)

    filtered_df = history_df.loc[filtered_indices].copy()
    filtered_records = [history_records[idx] for idx in filtered_indices]

    if filtered_df.empty:
        st.info("No history records matched the current filter.")
        return

    sort_column = "_recorded_at_dt"
    ascending = False
    na_position = "last"
    if sort_by == "Recorded At (Oldest)":
        ascending = True
    elif sort_by == "End Balance (High)":
        sort_column = "end_balance"
    elif sort_by == "CAGR (High)":
        sort_column = "cagr"
    elif sort_by == "Sharpe Ratio (High)":
        sort_column = "sharpe_ratio"
    elif sort_by == "Drawdown (Best)":
        sort_column = "drawdown"
        ascending = False

    filtered_df = filtered_df.sort_values(sort_column, ascending=ascending, na_position=na_position).reset_index(drop=True)
    filtered_records = [history_records[int(idx)] for idx in filtered_df["_record_index"].tolist()]

    display_df = filtered_df.drop(columns=["_search_text", "_record_index", "_recorded_at_dt"])
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("#### History Drilldown")
    selected_label = st.selectbox(
        "Inspect Record",
        options=[_format_history_record_label(record) for record in filtered_records],
        index=0,
        key="backtest_history_selected_record",
    )
    selected_record = filtered_records[
        [_format_history_record_label(record) for record in filtered_records].index(selected_label)
    ]

    summary = selected_record.get("summary") or {}
    context = selected_record.get("context") or {}
    detail_tabs = st.tabs(["Summary", "Input & Context", "Raw Record"])

    with detail_tabs[0]:
        if summary:
            st.dataframe(pd.DataFrame([summary]), use_container_width=True, hide_index=True)
        elif selected_record.get("run_kind") == "strategy_compare":
            compare_summary_rows = context.get("strategy_summaries") or []
            if compare_summary_rows:
                st.caption("Compare records keep per-strategy summary rows instead of one primary summary row.")
                st.dataframe(pd.DataFrame(compare_summary_rows), use_container_width=True, hide_index=True)
            else:
                st.info("This compare history record does not include stored per-strategy summary rows. Older compare records may only keep the selected strategy list.")
        else:
            st.info("This history record does not include a primary summary row.")

    with detail_tabs[1]:
        left, right = st.columns(2, gap="large")
        with left:
            st.markdown("##### Input")
            st.json(
                {
                    "run_kind": selected_record.get("run_kind"),
                    "strategy_key": selected_record.get("strategy_key"),
                    "tickers": selected_record.get("tickers", []),
                    "start": selected_record.get("input_start"),
                    "end": selected_record.get("input_end"),
                    "timeframe": selected_record.get("timeframe"),
                    "option": selected_record.get("option"),
                    "rebalance_interval": selected_record.get("rebalance_interval"),
                    "top": selected_record.get("top"),
                    "vol_window": selected_record.get("vol_window"),
                    "factor_freq": selected_record.get("factor_freq"),
                    "rebalance_freq": selected_record.get("rebalance_freq"),
                    "snapshot_mode": selected_record.get("snapshot_mode"),
                    "quality_factors": selected_record.get("quality_factors"),
                    "value_factors": selected_record.get("value_factors"),
                    "trend_filter_enabled": selected_record.get("trend_filter_enabled"),
                    "trend_filter_window": selected_record.get("trend_filter_window"),
                    "market_regime_enabled": selected_record.get("market_regime_enabled"),
                    "market_regime_window": selected_record.get("market_regime_window"),
                    "market_regime_benchmark": selected_record.get("market_regime_benchmark"),
                    "underperformance_guardrail_enabled": selected_record.get("underperformance_guardrail_enabled"),
                    "underperformance_guardrail_window_months": selected_record.get("underperformance_guardrail_window_months"),
                    "underperformance_guardrail_threshold": selected_record.get("underperformance_guardrail_threshold"),
                    "drawdown_guardrail_enabled": selected_record.get("drawdown_guardrail_enabled"),
                    "drawdown_guardrail_window_months": selected_record.get("drawdown_guardrail_window_months"),
                    "drawdown_guardrail_strategy_threshold": selected_record.get("drawdown_guardrail_strategy_threshold"),
                    "drawdown_guardrail_gap_threshold": selected_record.get("drawdown_guardrail_gap_threshold"),
                    "snapshot_source": selected_record.get("snapshot_source"),
                    "universe_contract": selected_record.get("universe_contract"),
                    "dynamic_target_size": selected_record.get("dynamic_target_size"),
                    "ui_elapsed_seconds": selected_record.get("ui_elapsed_seconds"),
                    "universe_mode": selected_record.get("universe_mode"),
                    "preset_name": selected_record.get("preset_name"),
                }
            )
        with right:
            st.markdown("##### Context")
            if selected_record.get("run_kind") == "strategy_compare":
                compare_overrides = context.get("strategy_overrides") or {}
                if compare_overrides:
                    override_rows = []
                    for strategy_name, overrides in compare_overrides.items():
                        override_rows.append(
                            {
                                "Strategy": strategy_name,
                                "Preset": overrides.get("preset_name"),
                                "Top N": overrides.get("top_n"),
                                "Rebalance Interval": overrides.get("rebalance_interval"),
                                "Trend Filter": overrides.get("trend_filter_enabled"),
                                "Trend Window": overrides.get("trend_filter_window"),
                                "Market Regime": overrides.get("market_regime_enabled"),
                                "Regime Window": overrides.get("market_regime_window"),
                                "Regime Benchmark": overrides.get("market_regime_benchmark"),
                            }
                        )
                    st.caption("Compare 기록은 전략별 override가 context에 저장됩니다. 아래 표에서 trend/regime 설정을 바로 확인할 수 있습니다.")
                    st.dataframe(pd.DataFrame(override_rows), use_container_width=True, hide_index=True)
            dynamic_universe_preview_rows = context.get("dynamic_universe_preview_rows") or []
            if dynamic_universe_preview_rows:
                st.caption(
                    "`dynamic_universe_preview_rows`는 history에 같이 저장되는 날짜별 모집군 미리보기입니다. "
                    "각 행은 리밸런싱 날짜 1개이며, membership / continuity / profile 관련 count를 빠르게 다시 확인할 때 씁니다."
                )
                st.dataframe(pd.DataFrame(dynamic_universe_preview_rows), use_container_width=True, hide_index=True)
            dynamic_universe_artifact = context.get("dynamic_universe_artifact") or {}
            if dynamic_universe_artifact:
                st.caption(
                    "`dynamic_universe_artifact`는 dynamic universe 상세를 별도 JSON 파일로 저장한 산출물입니다. "
                    "`artifact_dir`는 저장 폴더, `snapshot_json`은 실제 JSON 파일 경로입니다."
                )
                artifact_cols = st.columns(2)
                with artifact_cols[0]:
                    st.markdown(f"- `artifact_dir`: `{dynamic_universe_artifact.get('artifact_dir', '-')}`")
                    st.markdown(f"- `snapshot_json`: `{dynamic_universe_artifact.get('snapshot_json', '-')}`")
                with artifact_cols[1]:
                    st.markdown(f"- `snapshot_row_count`: `{dynamic_universe_artifact.get('snapshot_row_count', '-')}`")
                    st.markdown(f"- `candidate_status_row_count`: `{dynamic_universe_artifact.get('candidate_status_row_count', '-')}`")
                st.json(dynamic_universe_artifact)
            if context.get("saved_portfolio_name") or context.get("saved_portfolio_id"):
                st.caption(
                    "이 run은 저장된 포트폴리오에서 다시 실행된 결과입니다. "
                    "아래 값으로 history run과 saved portfolio definition을 연결할 수 있습니다."
                )
                st.json(
                    {
                        "saved_portfolio_name": context.get("saved_portfolio_name"),
                        "saved_portfolio_id": context.get("saved_portfolio_id"),
                    }
                )
            st.json(context or {"context": None})

    with detail_tabs[2]:
        st.json(selected_record)

    st.markdown("#### Actions")
    payload = _build_history_payload(selected_record)
    if payload is None:
        st.caption("This record type is not rerunnable yet. `Run Again` and `Load Into Form` are currently supported for single-strategy records only.")
        return

    action_cols = st.columns([0.18, 0.18, 0.64], gap="small")
    with action_cols[0]:
        if st.button("Load Into Form", key="backtest_history_load_into_form", use_container_width=True):
            if _load_history_into_form(selected_record):
                st.rerun()
    with action_cols[1]:
        if st.button("Run Again", key="backtest_history_run_again", use_container_width=True):
            _handle_backtest_run(payload, strategy_name=_history_strategy_display_name(selected_record))
    with action_cols[2]:
        st.caption(
            "`Load Into Form`을 누르면 저장된 입력값을 `Single Strategy` 화면으로 불러오고, "
            "화면도 자동으로 그쪽으로 이동합니다. "
            "`Run Again`은 저장된 payload를 즉시 다시 실행합니다."
        )


def _handle_backtest_run(payload: dict, *, strategy_name: str) -> None:
    st.markdown("#### Runtime Payload")
    st.json(payload)

    try:
        spinner_text = f"Running {strategy_name} backtest from DB..."
        started_at = time.perf_counter()
        with st.spinner(spinner_text):
            if payload["strategy_key"] == "equal_weight":
                bundle = run_equal_weight_backtest_from_db(
                    tickers=payload["tickers"],
                    start=payload["start"],
                    end=payload["end"],
                    timeframe=payload["timeframe"],
                    option=payload["option"],
                    rebalance_interval=payload["rebalance_interval"],
                    universe_mode=payload["universe_mode"],
                    preset_name=payload["preset_name"],
                )
            elif payload["strategy_key"] == "gtaa":
                bundle = run_gtaa_backtest_from_db(
                    tickers=payload["tickers"],
                    start=payload["start"],
                    end=payload["end"],
                    timeframe=payload["timeframe"],
                    option=payload["option"],
                    top=payload["top"],
                    interval=payload["interval"],
                    score_lookback_months=payload.get("score_lookback_months"),
                    score_return_columns=payload.get("score_return_columns"),
                    score_weights=payload.get("score_weights"),
                    trend_filter_window=payload.get("trend_filter_window", GTAA_DEFAULT_TREND_FILTER_WINDOW),
                    risk_off_mode=payload.get("risk_off_mode", GTAA_DEFAULT_RISK_OFF_MODE),
                    defensive_tickers=payload.get("defensive_tickers", GTAA_DEFAULT_DEFENSIVE_TICKERS),
                    market_regime_enabled=payload.get("market_regime_enabled", False),
                    market_regime_window=payload.get("market_regime_window", STRICT_MARKET_REGIME_DEFAULT_WINDOW),
                    market_regime_benchmark=payload.get("market_regime_benchmark", STRICT_MARKET_REGIME_DEFAULT_BENCHMARK),
                    crash_guardrail_enabled=payload.get("crash_guardrail_enabled", GTAA_DEFAULT_CRASH_GUARDRAIL_ENABLED),
                    crash_guardrail_drawdown_threshold=payload.get("crash_guardrail_drawdown_threshold", GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD),
                    crash_guardrail_lookback_months=payload.get("crash_guardrail_lookback_months", GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS),
                    min_price_filter=payload.get("min_price_filter", ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
                    transaction_cost_bps=payload.get("transaction_cost_bps", ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS),
                    benchmark_ticker=payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
                    underperformance_guardrail_enabled=payload.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED),
                    underperformance_guardrail_window_months=payload.get("underperformance_guardrail_window_months", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS),
                    underperformance_guardrail_threshold=payload.get("underperformance_guardrail_threshold", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD),
                    drawdown_guardrail_enabled=payload.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED),
                    drawdown_guardrail_window_months=payload.get("drawdown_guardrail_window_months", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS),
                    drawdown_guardrail_strategy_threshold=payload.get("drawdown_guardrail_strategy_threshold", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD),
                    drawdown_guardrail_gap_threshold=payload.get("drawdown_guardrail_gap_threshold", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD),
                    promotion_min_etf_aum_b=payload.get("promotion_min_etf_aum_b", ETF_OPERABILITY_DEFAULT_MIN_AUM_B),
                    promotion_max_bid_ask_spread_pct=payload.get("promotion_max_bid_ask_spread_pct", ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT),
                    universe_mode=payload["universe_mode"],
                    preset_name=payload["preset_name"],
                )
            elif payload["strategy_key"] == "risk_parity_trend":
                bundle = run_risk_parity_trend_backtest_from_db(
                    tickers=payload["tickers"],
                    start=payload["start"],
                    end=payload["end"],
                    timeframe=payload["timeframe"],
                    option=payload["option"],
                    rebalance_interval=payload.get("rebalance_interval", 1),
                    vol_window=payload.get("vol_window", 6),
                    min_price_filter=payload.get("min_price_filter", ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
                    transaction_cost_bps=payload.get("transaction_cost_bps", ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS),
                    benchmark_ticker=payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
                    underperformance_guardrail_enabled=payload.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED),
                    underperformance_guardrail_window_months=payload.get("underperformance_guardrail_window_months", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS),
                    underperformance_guardrail_threshold=payload.get("underperformance_guardrail_threshold", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD),
                    drawdown_guardrail_enabled=payload.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED),
                    drawdown_guardrail_window_months=payload.get("drawdown_guardrail_window_months", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS),
                    drawdown_guardrail_strategy_threshold=payload.get("drawdown_guardrail_strategy_threshold", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD),
                    drawdown_guardrail_gap_threshold=payload.get("drawdown_guardrail_gap_threshold", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD),
                    promotion_min_etf_aum_b=payload.get("promotion_min_etf_aum_b", ETF_OPERABILITY_DEFAULT_MIN_AUM_B),
                    promotion_max_bid_ask_spread_pct=payload.get("promotion_max_bid_ask_spread_pct", ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT),
                    universe_mode=payload["universe_mode"],
                    preset_name=payload["preset_name"],
                )
            elif payload["strategy_key"] == "dual_momentum":
                bundle = run_dual_momentum_backtest_from_db(
                    tickers=payload["tickers"],
                    start=payload["start"],
                    end=payload["end"],
                    timeframe=payload["timeframe"],
                    option=payload["option"],
                    top=payload.get("top", 1),
                    rebalance_interval=payload.get("rebalance_interval", 1),
                    min_price_filter=payload.get("min_price_filter", ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
                    transaction_cost_bps=payload.get("transaction_cost_bps", ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS),
                    benchmark_ticker=payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
                    underperformance_guardrail_enabled=payload.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED),
                    underperformance_guardrail_window_months=payload.get("underperformance_guardrail_window_months", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS),
                    underperformance_guardrail_threshold=payload.get("underperformance_guardrail_threshold", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD),
                    drawdown_guardrail_enabled=payload.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED),
                    drawdown_guardrail_window_months=payload.get("drawdown_guardrail_window_months", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS),
                    drawdown_guardrail_strategy_threshold=payload.get("drawdown_guardrail_strategy_threshold", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD),
                    drawdown_guardrail_gap_threshold=payload.get("drawdown_guardrail_gap_threshold", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD),
                    promotion_min_etf_aum_b=payload.get("promotion_min_etf_aum_b", ETF_OPERABILITY_DEFAULT_MIN_AUM_B),
                    promotion_max_bid_ask_spread_pct=payload.get("promotion_max_bid_ask_spread_pct", ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT),
                    universe_mode=payload["universe_mode"],
                    preset_name=payload["preset_name"],
                )
            elif payload["strategy_key"] == "quality_snapshot":
                bundle = run_quality_snapshot_backtest_from_db(
                    tickers=payload["tickers"],
                    start=payload["start"],
                    end=payload["end"],
                    timeframe=payload["timeframe"],
                    option=payload["option"],
                    factor_freq=payload["factor_freq"],
                    rebalance_freq=payload["rebalance_freq"],
                    quality_factors=payload["quality_factors"],
                    top_n=payload["top"],
                    snapshot_mode=payload["snapshot_mode"],
                    universe_mode=payload["universe_mode"],
                    preset_name=payload["preset_name"],
                )
            elif payload["strategy_key"] == "quality_snapshot_strict_annual":
                bundle = run_quality_snapshot_strict_annual_backtest_from_db(
                    tickers=payload["tickers"],
                    start=payload["start"],
                    end=payload["end"],
                    timeframe=payload["timeframe"],
                    option=payload["option"],
                    quality_factors=payload["quality_factors"],
                    top_n=payload["top"],
                    rebalance_interval=payload.get("rebalance_interval", 1),
                    min_price_filter=payload.get("min_price_filter", ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
                    min_history_months_filter=payload.get("min_history_months_filter", STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS),
                    min_avg_dollar_volume_20d_m_filter=payload.get("min_avg_dollar_volume_20d_m_filter", STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M),
                    transaction_cost_bps=payload.get("transaction_cost_bps", ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS),
                    benchmark_contract=payload.get("benchmark_contract", STRICT_DEFAULT_BENCHMARK_CONTRACT),
                    benchmark_ticker=payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
                    promotion_min_benchmark_coverage=payload.get("promotion_min_benchmark_coverage", STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE),
                    promotion_min_net_cagr_spread=payload.get("promotion_min_net_cagr_spread", STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD),
                    promotion_min_liquidity_clean_coverage=payload.get("promotion_min_liquidity_clean_coverage", STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE),
                    promotion_max_underperformance_share=payload.get("promotion_max_underperformance_share", STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE),
                    promotion_min_worst_rolling_excess_return=payload.get("promotion_min_worst_rolling_excess_return", STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN),
                    promotion_max_strategy_drawdown=payload.get("promotion_max_strategy_drawdown", STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN),
                    promotion_max_drawdown_gap_vs_benchmark=payload.get("promotion_max_drawdown_gap_vs_benchmark", STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK),
                    trend_filter_enabled=payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED),
                    trend_filter_window=payload.get("trend_filter_window", STRICT_TREND_FILTER_DEFAULT_WINDOW),
                    market_regime_enabled=payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED),
                    market_regime_window=payload.get("market_regime_window", STRICT_MARKET_REGIME_DEFAULT_WINDOW),
                    market_regime_benchmark=payload.get("market_regime_benchmark", STRICT_MARKET_REGIME_DEFAULT_BENCHMARK),
                    underperformance_guardrail_enabled=payload.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED),
                    underperformance_guardrail_window_months=payload.get("underperformance_guardrail_window_months", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS),
                    underperformance_guardrail_threshold=payload.get("underperformance_guardrail_threshold", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD),
                    drawdown_guardrail_enabled=payload.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED),
                    drawdown_guardrail_window_months=payload.get("drawdown_guardrail_window_months", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS),
                    drawdown_guardrail_strategy_threshold=payload.get("drawdown_guardrail_strategy_threshold", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD),
                    drawdown_guardrail_gap_threshold=payload.get("drawdown_guardrail_gap_threshold", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD),
                    universe_mode=payload["universe_mode"],
                    preset_name=payload["preset_name"],
                    universe_contract=payload.get("universe_contract", STATIC_MANAGED_RESEARCH_UNIVERSE),
                    dynamic_candidate_tickers=payload.get("dynamic_candidate_tickers"),
                    dynamic_target_size=payload.get("dynamic_target_size"),
                )
            elif payload["strategy_key"] == "quality_snapshot_strict_quarterly_prototype":
                bundle = run_quality_snapshot_strict_quarterly_prototype_backtest_from_db(
                    tickers=payload["tickers"],
                    start=payload["start"],
                    end=payload["end"],
                    timeframe=payload["timeframe"],
                    option=payload["option"],
                    quality_factors=payload["quality_factors"],
                    top_n=payload["top"],
                    rebalance_interval=payload.get("rebalance_interval", 1),
                    trend_filter_enabled=payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED),
                    trend_filter_window=payload.get("trend_filter_window", STRICT_TREND_FILTER_DEFAULT_WINDOW),
                    market_regime_enabled=payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED),
                    market_regime_window=payload.get("market_regime_window", STRICT_MARKET_REGIME_DEFAULT_WINDOW),
                    market_regime_benchmark=payload.get("market_regime_benchmark", STRICT_MARKET_REGIME_DEFAULT_BENCHMARK),
                    universe_mode=payload["universe_mode"],
                    preset_name=payload["preset_name"],
                    universe_contract=payload.get("universe_contract", STATIC_MANAGED_RESEARCH_UNIVERSE),
                    dynamic_candidate_tickers=payload.get("dynamic_candidate_tickers"),
                    dynamic_target_size=payload.get("dynamic_target_size"),
                )
            elif payload["strategy_key"] == "value_snapshot_strict_annual":
                bundle = run_value_snapshot_strict_annual_backtest_from_db(
                    tickers=payload["tickers"],
                    start=payload["start"],
                    end=payload["end"],
                    timeframe=payload["timeframe"],
                    option=payload["option"],
                    value_factors=payload["value_factors"],
                    top_n=payload["top"],
                    rebalance_interval=payload.get("rebalance_interval", 1),
                    min_price_filter=payload.get("min_price_filter", ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
                    min_history_months_filter=payload.get("min_history_months_filter", STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS),
                    min_avg_dollar_volume_20d_m_filter=payload.get("min_avg_dollar_volume_20d_m_filter", STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M),
                    transaction_cost_bps=payload.get("transaction_cost_bps", ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS),
                    benchmark_contract=payload.get("benchmark_contract", STRICT_DEFAULT_BENCHMARK_CONTRACT),
                    benchmark_ticker=payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
                    promotion_min_benchmark_coverage=payload.get("promotion_min_benchmark_coverage", STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE),
                    promotion_min_net_cagr_spread=payload.get("promotion_min_net_cagr_spread", STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD),
                    promotion_min_liquidity_clean_coverage=payload.get("promotion_min_liquidity_clean_coverage", STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE),
                    promotion_max_underperformance_share=payload.get("promotion_max_underperformance_share", STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE),
                    promotion_min_worst_rolling_excess_return=payload.get("promotion_min_worst_rolling_excess_return", STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN),
                    promotion_max_strategy_drawdown=payload.get("promotion_max_strategy_drawdown", STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN),
                    promotion_max_drawdown_gap_vs_benchmark=payload.get("promotion_max_drawdown_gap_vs_benchmark", STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK),
                    trend_filter_enabled=payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED),
                    trend_filter_window=payload.get("trend_filter_window", STRICT_TREND_FILTER_DEFAULT_WINDOW),
                    market_regime_enabled=payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED),
                    market_regime_window=payload.get("market_regime_window", STRICT_MARKET_REGIME_DEFAULT_WINDOW),
                    market_regime_benchmark=payload.get("market_regime_benchmark", STRICT_MARKET_REGIME_DEFAULT_BENCHMARK),
                    underperformance_guardrail_enabled=payload.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED),
                    underperformance_guardrail_window_months=payload.get("underperformance_guardrail_window_months", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS),
                    underperformance_guardrail_threshold=payload.get("underperformance_guardrail_threshold", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD),
                    drawdown_guardrail_enabled=payload.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED),
                    drawdown_guardrail_window_months=payload.get("drawdown_guardrail_window_months", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS),
                    drawdown_guardrail_strategy_threshold=payload.get("drawdown_guardrail_strategy_threshold", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD),
                    drawdown_guardrail_gap_threshold=payload.get("drawdown_guardrail_gap_threshold", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD),
                    universe_mode=payload["universe_mode"],
                    preset_name=payload["preset_name"],
                    universe_contract=payload.get("universe_contract", STATIC_MANAGED_RESEARCH_UNIVERSE),
                    dynamic_candidate_tickers=payload.get("dynamic_candidate_tickers"),
                    dynamic_target_size=payload.get("dynamic_target_size"),
                )
            elif payload["strategy_key"] == "value_snapshot_strict_quarterly_prototype":
                bundle = run_value_snapshot_strict_quarterly_prototype_backtest_from_db(
                    tickers=payload["tickers"],
                    start=payload["start"],
                    end=payload["end"],
                    timeframe=payload["timeframe"],
                    option=payload["option"],
                    value_factors=payload["value_factors"],
                    top_n=payload["top"],
                    rebalance_interval=payload.get("rebalance_interval", 1),
                    trend_filter_enabled=payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED),
                    trend_filter_window=payload.get("trend_filter_window", STRICT_TREND_FILTER_DEFAULT_WINDOW),
                    market_regime_enabled=payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED),
                    market_regime_window=payload.get("market_regime_window", STRICT_MARKET_REGIME_DEFAULT_WINDOW),
                    market_regime_benchmark=payload.get("market_regime_benchmark", STRICT_MARKET_REGIME_DEFAULT_BENCHMARK),
                    universe_mode=payload["universe_mode"],
                    preset_name=payload["preset_name"],
                    universe_contract=payload.get("universe_contract", STATIC_MANAGED_RESEARCH_UNIVERSE),
                    dynamic_candidate_tickers=payload.get("dynamic_candidate_tickers"),
                    dynamic_target_size=payload.get("dynamic_target_size"),
                )
            elif payload["strategy_key"] == "quality_value_snapshot_strict_annual":
                bundle = run_quality_value_snapshot_strict_annual_backtest_from_db(
                    tickers=payload["tickers"],
                    start=payload["start"],
                    end=payload["end"],
                    timeframe=payload["timeframe"],
                    option=payload["option"],
                    quality_factors=payload["quality_factors"],
                    value_factors=payload["value_factors"],
                    top_n=payload["top"],
                    rebalance_interval=payload.get("rebalance_interval", 1),
                    min_price_filter=payload.get("min_price_filter", ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
                    min_history_months_filter=payload.get("min_history_months_filter", STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS),
                    min_avg_dollar_volume_20d_m_filter=payload.get("min_avg_dollar_volume_20d_m_filter", STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M),
                    transaction_cost_bps=payload.get("transaction_cost_bps", ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS),
                    benchmark_contract=payload.get("benchmark_contract", STRICT_DEFAULT_BENCHMARK_CONTRACT),
                    benchmark_ticker=payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
                    promotion_min_benchmark_coverage=payload.get("promotion_min_benchmark_coverage", STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE),
                    promotion_min_net_cagr_spread=payload.get("promotion_min_net_cagr_spread", STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD),
                    promotion_min_liquidity_clean_coverage=payload.get("promotion_min_liquidity_clean_coverage", STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE),
                    promotion_max_underperformance_share=payload.get("promotion_max_underperformance_share", STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE),
                    promotion_min_worst_rolling_excess_return=payload.get("promotion_min_worst_rolling_excess_return", STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN),
                    promotion_max_strategy_drawdown=payload.get("promotion_max_strategy_drawdown", STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN),
                    promotion_max_drawdown_gap_vs_benchmark=payload.get("promotion_max_drawdown_gap_vs_benchmark", STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK),
                    trend_filter_enabled=payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED),
                    trend_filter_window=payload.get("trend_filter_window", STRICT_TREND_FILTER_DEFAULT_WINDOW),
                    market_regime_enabled=payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED),
                    market_regime_window=payload.get("market_regime_window", STRICT_MARKET_REGIME_DEFAULT_WINDOW),
                    market_regime_benchmark=payload.get("market_regime_benchmark", STRICT_MARKET_REGIME_DEFAULT_BENCHMARK),
                    underperformance_guardrail_enabled=payload.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED),
                    underperformance_guardrail_window_months=payload.get("underperformance_guardrail_window_months", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS),
                    underperformance_guardrail_threshold=payload.get("underperformance_guardrail_threshold", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD),
                    drawdown_guardrail_enabled=payload.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED),
                    drawdown_guardrail_window_months=payload.get("drawdown_guardrail_window_months", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS),
                    drawdown_guardrail_strategy_threshold=payload.get("drawdown_guardrail_strategy_threshold", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD),
                    drawdown_guardrail_gap_threshold=payload.get("drawdown_guardrail_gap_threshold", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD),
                    universe_mode=payload["universe_mode"],
                    preset_name=payload["preset_name"],
                    universe_contract=payload.get("universe_contract", STATIC_MANAGED_RESEARCH_UNIVERSE),
                    dynamic_candidate_tickers=payload.get("dynamic_candidate_tickers"),
                    dynamic_target_size=payload.get("dynamic_target_size"),
                )
            elif payload["strategy_key"] == "quality_value_snapshot_strict_quarterly_prototype":
                bundle = run_quality_value_snapshot_strict_quarterly_prototype_backtest_from_db(
                    tickers=payload["tickers"],
                    start=payload["start"],
                    end=payload["end"],
                    timeframe=payload["timeframe"],
                    option=payload["option"],
                    quality_factors=payload["quality_factors"],
                    value_factors=payload["value_factors"],
                    top_n=payload["top"],
                    rebalance_interval=payload.get("rebalance_interval", 1),
                    trend_filter_enabled=payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED),
                    trend_filter_window=payload.get("trend_filter_window", STRICT_TREND_FILTER_DEFAULT_WINDOW),
                    market_regime_enabled=payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED),
                    market_regime_window=payload.get("market_regime_window", STRICT_MARKET_REGIME_DEFAULT_WINDOW),
                    market_regime_benchmark=payload.get("market_regime_benchmark", STRICT_MARKET_REGIME_DEFAULT_BENCHMARK),
                    universe_mode=payload["universe_mode"],
                    preset_name=payload["preset_name"],
                    universe_contract=payload.get("universe_contract", STATIC_MANAGED_RESEARCH_UNIVERSE),
                    dynamic_candidate_tickers=payload.get("dynamic_candidate_tickers"),
                    dynamic_target_size=payload.get("dynamic_target_size"),
                )
            else:
                raise BacktestInputError(f"Unsupported strategy key: {payload['strategy_key']}")
    except BacktestInputError as exc:
        st.session_state.backtest_last_bundle = None
        st.session_state.backtest_last_error_kind = "input"
        st.session_state.backtest_last_error = f"Backtest input issue: {exc}"
        return
    except BacktestDataError as exc:
        st.session_state.backtest_last_bundle = None
        st.session_state.backtest_last_error_kind = "data"
        st.session_state.backtest_last_error = f"Backtest data issue: {exc}"
        return
    except Exception as exc:
        st.session_state.backtest_last_bundle = None
        st.session_state.backtest_last_error_kind = "system"
        st.session_state.backtest_last_error = f"Backtest execution failed: {exc}"
        return

    elapsed_seconds = time.perf_counter() - started_at
    bundle = dict(bundle)
    meta = dict(bundle.get("meta") or {})
    meta["ui_elapsed_seconds"] = round(elapsed_seconds, 3)
    bundle["meta"] = meta

    st.session_state.backtest_last_bundle = bundle
    st.session_state.backtest_last_error = None
    st.session_state.backtest_last_error_kind = None
    append_backtest_run_history(bundle=bundle, run_kind="single_strategy")
    st.success(f"{strategy_name} backtest execution completed in {elapsed_seconds:.3f}s.")


def _render_equal_weight_form() -> None:
    st.markdown("### Equal Weight")
    st.caption("DB-backed equal-weight portfolio execution using the first public runtime wrapper.")
    _apply_single_strategy_prefill("equal_weight")

    _universe_mode, preset_name, tickers = _render_equal_weight_universe_inputs(
        key_prefix="eq",
    )

    with st.form("equal_weight_backtest_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=date(2016, 1, 1), key="eq_start")
        with col2:
            end_date = st.date_input("End Date", value=DEFAULT_BACKTEST_END_DATE, key="eq_end")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="eq_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="eq_option")
            rebalance_interval = st.number_input(
                "Rebalance Interval",
                min_value=1,
                max_value=36,
                value=12,
                step=1,
                help="Equal Weight sample 기준 기본값은 12입니다.",
                key="eq_rebalance_interval",
            )

        submitted = st.form_submit_button("Run Equal Weight Backtest", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []

    if not tickers:
        validation_errors.append("At least one ticker is required.")
    if start_date > end_date:
        validation_errors.append("Start Date must be earlier than or equal to End Date.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "equal_weight",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "rebalance_interval": int(rebalance_interval),
        "universe_mode": _universe_mode,
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Equal Weight")


def _render_gtaa_form() -> None:
    st.markdown("### GTAA")
    st.caption("DB-backed GTAA execution using the second public runtime wrapper.")
    _apply_single_strategy_prefill("gtaa")

    _universe_mode, preset_name, tickers = _render_gtaa_universe_inputs(
        key_prefix="gtaa",
    )

    with st.form("gtaa_backtest_form", clear_on_submit=False):

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=date(2016, 1, 1), key="gtaa_start")
        with col2:
            end_date = st.date_input("End Date", value=DEFAULT_BACKTEST_END_DATE, key="gtaa_end")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="gtaa_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="gtaa_option")
            top = st.number_input(
                "Top Assets",
                min_value=1,
                max_value=12,
                value=3,
                step=1,
                help="GTAA는 평균 score 상위 자산을 선택합니다.",
                key="gtaa_top",
            )
            interval = st.number_input(
                "Signal Interval (months)",
                min_value=1,
                max_value=12,
                value=GTAA_DEFAULT_SIGNAL_INTERVAL,
                step=1,
                help="현재 기본값은 1입니다. 1이면 매월, 2면 격월로 신호를 계산합니다.",
                key="gtaa_interval",
            )
            st.divider()
            (
                min_price_filter,
                transaction_cost_bps,
                benchmark_ticker,
                promotion_min_etf_aum_b,
                promotion_max_bid_ask_spread_pct,
            ) = _render_etf_real_money_inputs(
                key_prefix="gtaa",
            )
            (
                underperformance_guardrail_enabled,
                underperformance_guardrail_window_months,
                underperformance_guardrail_threshold,
                drawdown_guardrail_enabled,
                drawdown_guardrail_window_months,
                drawdown_guardrail_strategy_threshold,
                drawdown_guardrail_gap_threshold,
            ) = _render_etf_guardrail_inputs(
                key_prefix="gtaa",
                label_prefix="GTAA ",
            )
            score_lookback_months, score_weights = _render_gtaa_score_weight_inputs(key_prefix="gtaa")
            risk_off_contract = _render_gtaa_risk_off_contract_inputs(key_prefix="gtaa")

        submitted = st.form_submit_button("Run GTAA Backtest", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("At least one ticker is required.")
    if start_date > end_date:
        validation_errors.append("Start Date must be earlier than or equal to End Date.")
    if not score_lookback_months:
        validation_errors.append("GTAA Score Horizons must contain at least one lookback window.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "gtaa",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "top": int(top),
        "interval": int(interval),
        "score_lookback_months": list(score_lookback_months),
        "score_return_columns": [_gtaa_return_col_from_months(months) for months in score_lookback_months],
        "score_weights": score_weights,
        "trend_filter_window": int(risk_off_contract["trend_filter_window"]),
        "risk_off_mode": risk_off_contract["risk_off_mode"],
        "defensive_tickers": list(risk_off_contract["defensive_tickers"]),
        "market_regime_enabled": bool(risk_off_contract["market_regime_enabled"]),
        "market_regime_window": int(risk_off_contract["market_regime_window"]),
        "market_regime_benchmark": risk_off_contract["market_regime_benchmark"],
        "crash_guardrail_enabled": bool(risk_off_contract["crash_guardrail_enabled"]),
        "crash_guardrail_drawdown_threshold": float(risk_off_contract["crash_guardrail_drawdown_threshold"]),
        "crash_guardrail_lookback_months": int(risk_off_contract["crash_guardrail_lookback_months"]),
        "min_price_filter": float(min_price_filter),
        "transaction_cost_bps": float(transaction_cost_bps),
        "benchmark_ticker": benchmark_ticker,
        "promotion_min_etf_aum_b": float(promotion_min_etf_aum_b),
        "promotion_max_bid_ask_spread_pct": float(promotion_max_bid_ask_spread_pct),
        "underperformance_guardrail_enabled": bool(underperformance_guardrail_enabled),
        "underperformance_guardrail_window_months": int(underperformance_guardrail_window_months),
        "underperformance_guardrail_threshold": float(underperformance_guardrail_threshold),
        "drawdown_guardrail_enabled": bool(drawdown_guardrail_enabled),
        "drawdown_guardrail_window_months": int(drawdown_guardrail_window_months),
        "drawdown_guardrail_strategy_threshold": float(drawdown_guardrail_strategy_threshold),
        "drawdown_guardrail_gap_threshold": float(drawdown_guardrail_gap_threshold),
        "universe_mode": _universe_mode,
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="GTAA")


def _render_risk_parity_form() -> None:
    st.markdown("### Risk Parity Trend")
    st.caption("DB-backed risk-parity trend execution using the third public runtime wrapper.")
    _apply_single_strategy_prefill("risk_parity_trend")

    with st.form("risk_parity_backtest_form", clear_on_submit=False):
        universe_mode = st.radio(
            "Universe Mode",
            options=["Preset", "Manual"],
            horizontal=True,
            help="Risk Parity Trend도 기본적으로 preset universe 사용을 권장합니다.",
            key="rp_universe_mode",
        )

        preset_name = None
        tickers: list[str] = []

        if universe_mode == "Preset":
            preset_name = st.selectbox(
                "Preset",
                options=list(RISK_PARITY_PRESETS.keys()),
                index=0,
                key="rp_preset",
            )
            tickers = RISK_PARITY_PRESETS[preset_name]
            st.caption(f"Selected tickers: `{', '.join(tickers)}`")
        else:
            manual_tickers = st.text_input(
                "Tickers",
                value="SPY,TLT,GLD,IEF,LQD",
                help="Comma-separated tickers. Example: SPY,TLT,GLD,IEF,LQD",
                key="rp_manual_tickers",
            )
            tickers = _parse_manual_tickers(manual_tickers)

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=date(2016, 1, 1), key="rp_start")
        with col2:
            end_date = st.date_input("End Date", value=DEFAULT_BACKTEST_END_DATE, key="rp_end")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="rp_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="rp_option")
            rebalance_interval = int(
                st.number_input(
                    "Rebalance Interval (months)",
                    min_value=1,
                    max_value=12,
                    value=1,
                    step=1,
                    key="rp_rebalance_interval",
                )
            )
            vol_window = int(
                st.number_input(
                    "Volatility Window (months)",
                    min_value=1,
                    max_value=24,
                    value=6,
                    step=1,
                    key="rp_vol_window",
                )
            )
            st.divider()
            (
                min_price_filter,
                transaction_cost_bps,
                benchmark_ticker,
                promotion_min_etf_aum_b,
                promotion_max_bid_ask_spread_pct,
            ) = _render_etf_real_money_inputs(
                key_prefix="rp",
            )
            (
                underperformance_guardrail_enabled,
                underperformance_guardrail_window_months,
                underperformance_guardrail_threshold,
                drawdown_guardrail_enabled,
                drawdown_guardrail_window_months,
                drawdown_guardrail_strategy_threshold,
                drawdown_guardrail_gap_threshold,
            ) = _render_etf_guardrail_inputs(
                key_prefix="rp",
                label_prefix="Risk Parity ",
            )

        submitted = st.form_submit_button("Run Risk Parity Trend Backtest", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("At least one ticker is required.")
    if start_date > end_date:
        validation_errors.append("Start Date must be earlier than or equal to End Date.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "risk_parity_trend",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "rebalance_interval": int(rebalance_interval),
        "vol_window": int(vol_window),
        "min_price_filter": float(min_price_filter),
        "transaction_cost_bps": float(transaction_cost_bps),
        "benchmark_ticker": benchmark_ticker,
        "promotion_min_etf_aum_b": float(promotion_min_etf_aum_b),
        "promotion_max_bid_ask_spread_pct": float(promotion_max_bid_ask_spread_pct),
        "underperformance_guardrail_enabled": bool(underperformance_guardrail_enabled),
        "underperformance_guardrail_window_months": int(underperformance_guardrail_window_months),
        "underperformance_guardrail_threshold": float(underperformance_guardrail_threshold),
        "drawdown_guardrail_enabled": bool(drawdown_guardrail_enabled),
        "drawdown_guardrail_window_months": int(drawdown_guardrail_window_months),
        "drawdown_guardrail_strategy_threshold": float(drawdown_guardrail_strategy_threshold),
        "drawdown_guardrail_gap_threshold": float(drawdown_guardrail_gap_threshold),
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Risk Parity Trend")


def _render_dual_momentum_form() -> None:
    st.markdown("### Dual Momentum")
    st.caption("DB-backed dual momentum execution using the fourth public runtime wrapper.")
    _apply_single_strategy_prefill("dual_momentum")

    with st.form("dual_momentum_backtest_form", clear_on_submit=False):
        universe_mode = st.radio(
            "Universe Mode",
            options=["Preset", "Manual"],
            horizontal=True,
            help="Dual Momentum도 기본 preset universe를 기준으로 시작하는 편이 안전합니다.",
            key="dm_universe_mode",
        )

        preset_name = None
        tickers: list[str] = []

        if universe_mode == "Preset":
            preset_name = st.selectbox(
                "Preset",
                options=list(DUAL_MOMENTUM_PRESETS.keys()),
                index=0,
                key="dm_preset",
            )
            tickers = DUAL_MOMENTUM_PRESETS[preset_name]
            st.caption(f"Selected tickers: `{', '.join(tickers)}`")
        else:
            manual_tickers = st.text_input(
                "Tickers",
                value="QQQ,SPY,IWM,SOXX,BIL",
                help="Comma-separated tickers. Example: QQQ,SPY,IWM,SOXX,BIL",
                key="dm_manual_tickers",
            )
            tickers = _parse_manual_tickers(manual_tickers)

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=date(2016, 1, 1), key="dm_start")
        with col2:
            end_date = st.date_input("End Date", value=DEFAULT_BACKTEST_END_DATE, key="dm_end")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="dm_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="dm_option")
            top = int(
                st.number_input(
                    "Top Assets",
                    min_value=1,
                    max_value=5,
                    value=1,
                    step=1,
                    key="dm_top",
                )
            )
            rebalance_interval = int(
                st.number_input(
                    "Rebalance Interval (months)",
                    min_value=1,
                    max_value=12,
                    value=1,
                    step=1,
                    key="dm_rebalance_interval",
                )
            )
            st.divider()
            (
                min_price_filter,
                transaction_cost_bps,
                benchmark_ticker,
                promotion_min_etf_aum_b,
                promotion_max_bid_ask_spread_pct,
            ) = _render_etf_real_money_inputs(
                key_prefix="dm",
            )
            (
                underperformance_guardrail_enabled,
                underperformance_guardrail_window_months,
                underperformance_guardrail_threshold,
                drawdown_guardrail_enabled,
                drawdown_guardrail_window_months,
                drawdown_guardrail_strategy_threshold,
                drawdown_guardrail_gap_threshold,
            ) = _render_etf_guardrail_inputs(
                key_prefix="dm",
                label_prefix="Dual Momentum ",
            )

        submitted = st.form_submit_button("Run Dual Momentum Backtest", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("At least one ticker is required.")
    if start_date > end_date:
        validation_errors.append("Start Date must be earlier than or equal to End Date.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "dual_momentum",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "top": int(top),
        "rebalance_interval": int(rebalance_interval),
        "min_price_filter": float(min_price_filter),
        "transaction_cost_bps": float(transaction_cost_bps),
        "benchmark_ticker": benchmark_ticker,
        "promotion_min_etf_aum_b": float(promotion_min_etf_aum_b),
        "promotion_max_bid_ask_spread_pct": float(promotion_max_bid_ask_spread_pct),
        "underperformance_guardrail_enabled": bool(underperformance_guardrail_enabled),
        "underperformance_guardrail_window_months": int(underperformance_guardrail_window_months),
        "underperformance_guardrail_threshold": float(underperformance_guardrail_threshold),
        "drawdown_guardrail_enabled": bool(drawdown_guardrail_enabled),
        "drawdown_guardrail_window_months": int(drawdown_guardrail_window_months),
        "drawdown_guardrail_strategy_threshold": float(drawdown_guardrail_strategy_threshold),
        "drawdown_guardrail_gap_threshold": float(drawdown_guardrail_gap_threshold),
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Dual Momentum")


def _render_quality_snapshot_form() -> None:
    st.markdown("### Quality Snapshot")
    st.caption("Research-oriented quality snapshot strategy using broad-research factor snapshots. This first pass ranks quality factors and holds top names equally between monthly rebalances.")
    _render_quality_family_guide("quality_broad")
    with st.expander("Data Requirements", expanded=False):
        st.markdown(
            "- `Daily Market Update` 또는 OHLCV 수집으로 **가격 데이터**를 먼저 채워야 합니다.\n"
            "- `Weekly Fundamental Refresh`로 **`nyse_fundamentals` + `nyse_factors`**를 채워야 합니다.\n"
            "- 현재 공개 버전은 **`Extended Statement Refresh`가 필수는 아닙니다**. 이 전략은 detailed statement ledger를 직접 읽지 않습니다.\n"
            "- 첫 공개 버전은 **stock-oriented** 입니다. ETF 위주 유니버스는 quality factor snapshot이 비거나 의미가 약할 수 있습니다.\n"
            "- 현재 `Factor Frequency`는 `annual`만 지원하므로, 같은 universe에 대해 `Weekly Fundamental Refresh (annual)`를 맞춰서 돌리는 편이 가장 자연스럽습니다."
        )
        st.caption("Current public mode: `broad_research` (research-oriented snapshot, not strict PIT)")
    _apply_single_strategy_prefill("quality_snapshot")

    universe_mode = st.radio(
        "Universe Mode",
        options=["Preset", "Manual"],
        horizontal=True,
        help="첫 factor strategy는 stock-only quality universe를 기준으로 시작하는 편이 안전합니다.",
        key="qs_universe_mode",
    )

    preset_name = None
    tickers: list[str] = []

    if universe_mode == "Preset":
        preset_name = st.selectbox(
            "Preset",
            options=list(QUALITY_BROAD_PRESETS.keys()),
            index=0,
            key="qs_preset",
        )
        tickers = QUALITY_BROAD_PRESETS[preset_name]
        _render_ticker_preview(tickers)
    else:
        manual_tickers = st.text_input(
            "Tickers",
            value="AAPL,MSFT,GOOG",
            help="Comma-separated stock tickers. Example: AAPL,MSFT,GOOG",
            key="qs_manual_tickers",
        )
        tickers = _parse_manual_tickers(manual_tickers)
        _render_ticker_preview(tickers)

    with st.form("quality_snapshot_backtest_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("Start Date", value=date(2016, 1, 1), key="qs_start")
        with col2:
            end_date = st.date_input("End Date", value=DEFAULT_BACKTEST_END_DATE, key="qs_end")
        with col3:
            top_n = st.number_input(
                "Top N",
                min_value=1,
                max_value=20,
                value=2,
                step=1,
                help="Quality score 상위 종목 수입니다.",
                key="qs_top_n",
            )

        st.caption("Hidden defaults in this first pass: `monthly rebalance`, `equal-weight holding`.")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="qs_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="qs_option")
            factor_freq = st.selectbox(
                "Factor Frequency",
                options=["annual"],
                index=0,
                key="qs_factor_freq",
                help="첫 버전은 annual quality snapshot만 지원합니다.",
            )
            quality_factors = st.multiselect(
                "Quality Factors",
                options=["roe", "gross_margin", "operating_margin", "debt_ratio"],
                default=["roe", "gross_margin", "operating_margin", "debt_ratio"],
                key="qs_quality_factors",
                help="높을수록 좋은 factor와 낮을수록 좋은 factor를 내부 score rule로 함께 처리합니다.",
            )
            snapshot_mode = st.selectbox(
                "Snapshot Mode",
                options=["broad_research"],
                index=0,
                key="qs_snapshot_mode",
                help="첫 공개 버전은 broad-research snapshot을 사용합니다. strict PIT mode는 후속 단계로 남겨둡니다.",
            )

        submitted = st.form_submit_button("Run Quality Snapshot Backtest", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("At least one ticker is required.")
    if start_date > end_date:
        validation_errors.append("Start Date must be earlier than or equal to End Date.")
    if not quality_factors:
        validation_errors.append("Select at least one quality factor.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "quality_snapshot",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "top": int(top_n),
        "factor_freq": factor_freq,
        "rebalance_freq": "monthly",
        "snapshot_mode": snapshot_mode,
        "quality_factors": quality_factors,
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Quality Snapshot")


def _render_quality_snapshot_strict_annual_form() -> None:
    st.markdown("### Quality Snapshot (Strict Annual)")
    st.caption("Strict annual statement-driven quality strategy. This public candidate ranks annual statement shadow factors, then holds the top names equally between monthly rebalances.")
    _render_quality_family_guide("quality_strict")
    with st.expander("Data Requirements", expanded=False):
        st.markdown(
            "- `Daily Market Update` 또는 OHLCV 수집으로 **가격 데이터**를 먼저 채워야 합니다.\n"
            "- `Extended Statement Refresh`를 **annual** 기준으로 먼저 채워야 합니다.\n"
            "- 이 경로는 현재 **strict annual statement shadow factors**를 사용합니다.\n"
            "- wider annual coverage 검증은 **US / EDGAR-friendly top-300 stock universe** 기준으로 확인되었습니다.\n"
            "- 현재는 stock-oriented path이며, ETF 중심 universe에는 적합하지 않습니다."
        )
        st.caption("Current public candidate mode: `strict_statement_annual` + `shadow_factors`")
    _apply_single_strategy_prefill("quality_snapshot_strict_annual")

    universe_mode = st.radio(
        "Universe Mode",
        options=["Preset", "Manual"],
        horizontal=True,
        help="Single Strategy에서는 annual statement coverage가 검증된 미국 주식 preset을 기본값으로 사용합니다.",
        key="qss_universe_mode",
    )

    preset_name = None
    tickers: list[str] = []
    if universe_mode == "Preset":
        preset_name = st.selectbox(
            "Preset",
            options=list(QUALITY_STRICT_PRESETS.keys()),
            index=list(QUALITY_STRICT_PRESETS.keys()).index(STRICT_ANNUAL_SINGLE_DEFAULT_PRESET),
            key="qss_preset",
        )
        tickers = QUALITY_STRICT_PRESETS[preset_name]
        _render_ticker_preview(tickers)
        _render_historical_universe_caption()
        _render_strict_preset_status_note(preset_name)
    else:
        manual_tickers = st.text_input(
            "Tickers",
            value="AAPL,MSFT,GOOG",
            help="쉼표로 구분한 주식 티커를 입력합니다. 예: AAPL,MSFT,GOOG",
            key="qss_manual_tickers",
        )
        tickers = _parse_manual_tickers(manual_tickers)
        _render_ticker_preview(tickers)

    _render_strict_price_freshness_preflight(
        tickers=tickers,
        end_value=st.session_state.get("qss_end", DEFAULT_BACKTEST_END_DATE),
        timeframe=st.session_state.get("qss_timeframe", "1d"),
        strategy_label="Quality Snapshot (Strict Annual)",
    )

    with st.form("quality_snapshot_strict_annual_backtest_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("Start Date", value=date(2016, 1, 1), key="qss_start")
        with col2:
            end_date = st.date_input("End Date", value=DEFAULT_BACKTEST_END_DATE, key="qss_end")
        with col3:
            top_n = st.number_input(
                "Top N",
                min_value=1,
                max_value=20,
                value=2,
                step=1,
                help="strict annual quality 점수 기준으로 상위 몇 개 종목을 선택할지 정합니다.",
                key="qss_top_n",
            )

        st.caption("Hidden defaults in this first pass: `annual statement snapshots`, `monthly rebalance`, `equal-weight holding`.")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="qss_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="qss_option")
            rebalance_interval = st.number_input(
                "Rebalance Interval",
                min_value=1,
                max_value=12,
                value=1,
                step=1,
                help="기본은 매월 리밸런싱(1)이며, 연구 목적이면 몇 달 간격으로 건너뛸 수도 있습니다.",
                key="qss_rebalance_interval",
            )
            universe_contract_label = st.selectbox(
                "Universe Contract",
                options=list(STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.keys()),
                index=0,
                key="qss_universe_contract",
                help="Static은 현재 managed preset을 고정해서 사용합니다. Dynamic PIT는 Phase 10 first pass로, annual strict에서만 각 리밸런싱 날짜 기준 모집군을 다시 계산합니다.",
            )
            universe_contract = STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS[universe_contract_label]
            dynamic_candidate_tickers, dynamic_target_size = _render_strict_annual_universe_contract_note(
                universe_contract=universe_contract,
                tickers=tickers,
                preset_name=preset_name,
            )
            quality_factors = st.multiselect(
                "Quality Factors",
                options=QUALITY_STRICT_FACTOR_OPTIONS,
                default=QUALITY_STRICT_DEFAULT_FACTORS,
                key="qss_quality_factors",
                help="기본은 coverage-first 팩터 조합입니다. 필요하면 예전 quality factor도 다시 포함할 수 있습니다.",
            )
            trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
            with trend_title_col:
                st.markdown("##### Trend Filter Overlay")
            with trend_help_col:
                _render_trend_filter_help_popover()
            trend_filter_enabled = st.checkbox(
                "Enable",
                value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                key="qss_trend_filter_enabled",
            )
            trend_filter_window = int(
                st.number_input(
                    "Trend Filter Window",
                    min_value=20,
                    max_value=400,
                    value=STRICT_TREND_FILTER_DEFAULT_WINDOW,
                    step=10,
                    key="qss_trend_filter_window",
                )
            )
            market_regime_enabled, market_regime_window, market_regime_benchmark = _render_market_regime_overlay_inputs(
                key_prefix="qss",
                label_prefix="",
            )
            (
                benchmark_contract,
                min_price_filter,
                min_history_months_filter,
                min_avg_dollar_volume_20d_m_filter,
                transaction_cost_bps,
                benchmark_ticker,
                promotion_min_benchmark_coverage,
                promotion_min_net_cagr_spread,
                promotion_min_liquidity_clean_coverage,
                promotion_max_underperformance_share,
                promotion_min_worst_rolling_excess_return,
                promotion_max_strategy_drawdown,
                promotion_max_drawdown_gap_vs_benchmark,
            ) = _render_strict_annual_real_money_inputs(
                key_prefix="qss",
            )
            (
                underperformance_guardrail_enabled,
                underperformance_guardrail_window_months,
                underperformance_guardrail_threshold,
            ) = _render_underperformance_guardrail_inputs(
                key_prefix="qss",
                label_prefix="Strict Annual Quality ",
            )
            (
                drawdown_guardrail_enabled,
                drawdown_guardrail_window_months,
                drawdown_guardrail_strategy_threshold,
                drawdown_guardrail_gap_threshold,
            ) = _render_drawdown_guardrail_inputs(
                key_prefix="qss",
                label_prefix="Strict Annual Quality ",
            )

        submitted = st.form_submit_button("Run Strict Annual Quality Backtest", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("At least one ticker is required.")
    if start_date > end_date:
        validation_errors.append("Start Date must be earlier than or equal to End Date.")
    if not quality_factors:
        validation_errors.append("Select at least one quality factor.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "quality_snapshot_strict_annual",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "top": int(top_n),
        "rebalance_interval": int(rebalance_interval),
        "factor_freq": "annual",
        "snapshot_mode": "strict_statement_annual",
        "quality_factors": quality_factors,
        "trend_filter_enabled": bool(trend_filter_enabled),
        "trend_filter_window": int(trend_filter_window),
        "market_regime_enabled": bool(market_regime_enabled),
        "market_regime_window": int(market_regime_window),
        "market_regime_benchmark": market_regime_benchmark,
        "min_price_filter": float(min_price_filter),
        "min_history_months_filter": int(min_history_months_filter),
        "min_avg_dollar_volume_20d_m_filter": float(min_avg_dollar_volume_20d_m_filter),
        "transaction_cost_bps": float(transaction_cost_bps),
        "benchmark_contract": benchmark_contract,
        "benchmark_ticker": benchmark_ticker,
        "promotion_min_benchmark_coverage": float(promotion_min_benchmark_coverage),
        "promotion_min_net_cagr_spread": float(promotion_min_net_cagr_spread),
        "promotion_min_liquidity_clean_coverage": float(promotion_min_liquidity_clean_coverage),
        "promotion_max_underperformance_share": float(promotion_max_underperformance_share),
        "promotion_min_worst_rolling_excess_return": float(promotion_min_worst_rolling_excess_return),
        "promotion_max_strategy_drawdown": float(promotion_max_strategy_drawdown),
        "promotion_max_drawdown_gap_vs_benchmark": float(promotion_max_drawdown_gap_vs_benchmark),
        "underperformance_guardrail_enabled": bool(underperformance_guardrail_enabled),
        "underperformance_guardrail_window_months": int(underperformance_guardrail_window_months),
        "underperformance_guardrail_threshold": float(underperformance_guardrail_threshold),
        "drawdown_guardrail_enabled": bool(drawdown_guardrail_enabled),
        "drawdown_guardrail_window_months": int(drawdown_guardrail_window_months),
        "drawdown_guardrail_strategy_threshold": float(drawdown_guardrail_strategy_threshold),
        "drawdown_guardrail_gap_threshold": float(drawdown_guardrail_gap_threshold),
        "universe_contract": universe_contract,
        "dynamic_candidate_tickers": dynamic_candidate_tickers,
        "dynamic_target_size": dynamic_target_size,
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Quality Snapshot (Strict Annual)")


def _render_quality_snapshot_strict_quarterly_prototype_form() -> None:
    st.markdown("### Quality Snapshot (Strict Quarterly Prototype)")
    st.caption("Research-only quarterly strict quality strategy. This Phase 7 path ranks quarterly statement shadow factors and keeps the top names equally between monthly rebalances.")
    _apply_single_strategy_prefill("quality_snapshot_strict_quarterly_prototype")

    with st.expander("Data Requirements", expanded=False):
        st.markdown(
            "- `Daily Market Update` 또는 OHLCV 수집으로 **가격 데이터**를 먼저 채워야 합니다.\n"
            "- `Extended Statement Refresh`와 statement shadow factor rebuild가 **quarterly** 기준으로 준비되어 있어야 합니다.\n"
            "- 이 경로는 현재 **research-only quarterly strict prototype** 입니다.\n"
            "- annual strict public family와 달리, coverage / freshness / runtime 검증이 이번 Phase 7에서 함께 진행됩니다."
        )
        st.caption("Current prototype mode: `strict_statement_quarterly` + `shadow_factors` + `research_only`")
        st.caption(
            "주의: 현재 DB의 quarterly shadow coverage 상태에 따라 실제 투자 구간이 요청한 시작일보다 늦게 열릴 수 있습니다. "
            "Phase 7 first pass 이후 `US Statement Coverage 100` 기본 preset은 다시 2016 부근부터 열리지만, 다른 universe나 수동 ticker 조합은 coverage 상태에 따라 더 늦을 수 있습니다."
        )

    universe_mode = st.radio(
        "Universe Mode",
        options=["Preset", "Manual"],
        horizontal=True,
        help="quarterly prototype first pass는 검증 비용을 낮추기 위해 `US Statement Coverage 100`을 기본 preset으로 둡니다.",
        key="qsqp_universe_mode",
    )

    preset_name = None
    tickers: list[str] = []
    if universe_mode == "Preset":
        preset_name = st.selectbox(
            "Preset",
            options=list(QUALITY_STRICT_PRESETS.keys()),
            index=list(QUALITY_STRICT_PRESETS.keys()).index(STRICT_QUARTERLY_PROTOTYPE_DEFAULT_PRESET),
            key="qsqp_preset",
        )
        tickers = QUALITY_STRICT_PRESETS[preset_name]
        _render_ticker_preview(tickers)
        _render_historical_universe_caption()
    else:
        manual_tickers = st.text_input(
            "Tickers",
            value="AAPL,MSFT,GOOG",
            help="쉼표로 구분한 주식 티커를 입력합니다. 예: AAPL,MSFT,GOOG",
            key="qsqp_manual_tickers",
        )
        tickers = _parse_manual_tickers(manual_tickers)
        _render_ticker_preview(tickers)

    _render_strict_price_freshness_preflight(
        tickers=tickers,
        end_value=st.session_state.get("qsqp_end", DEFAULT_BACKTEST_END_DATE),
        timeframe=st.session_state.get("qsqp_timeframe", "1d"),
        strategy_label="Quality Snapshot (Strict Quarterly Prototype)",
    )
    _render_statement_shadow_coverage_preview(
        tickers=tickers,
        freq="quarterly",
        strategy_label="Quality Snapshot (Strict Quarterly Prototype)",
    )

    with st.form("quality_snapshot_strict_quarterly_prototype_backtest_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("Start Date", value=date(2016, 1, 1), key="qsqp_start")
        with col2:
            end_date = st.date_input("End Date", value=DEFAULT_BACKTEST_END_DATE, key="qsqp_end")
        with col3:
            top_n = st.number_input(
                "Top N",
                min_value=1,
                max_value=20,
                value=2,
                step=1,
                help="strict quarterly quality 점수 기준으로 상위 몇 개 종목을 선택할지 정합니다.",
                key="qsqp_top_n",
            )

        st.caption("Research-only defaults in this first pass: `quarterly statement snapshots`, `monthly rebalance`, `equal-weight holding`.")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="qsqp_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="qsqp_option")
            rebalance_interval = st.number_input(
                "Rebalance Interval",
                min_value=1,
                max_value=12,
                value=1,
                step=1,
                help="기본은 매월 리밸런싱(1)이며, quarterly snapshot 자체는 가장 최근 usable filing 기준으로 따라갑니다.",
                key="qsqp_rebalance_interval",
            )
            universe_contract_label = st.selectbox(
                "Universe Contract",
                options=list(STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.keys()),
                index=0,
                key="qsqp_universe_contract",
                help="Static은 현재 managed preset을 고정해서 사용합니다. Dynamic PIT는 Phase 10 first pass로, quarterly strict에서도 각 리밸런싱 날짜 기준 모집군을 다시 계산합니다.",
            )
            universe_contract = STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS[universe_contract_label]
            dynamic_candidate_tickers, dynamic_target_size = _render_strict_dynamic_universe_contract_note(
                universe_contract=universe_contract,
                tickers=tickers,
                preset_name=preset_name,
                statement_freq="quarterly",
            )
            quality_factors = st.multiselect(
                "Quality Factors",
                options=QUALITY_STRICT_FACTOR_OPTIONS,
                default=QUALITY_STRICT_DEFAULT_FACTORS,
                key="qsqp_quality_factors",
                help="first-pass quarterly prototype도 quality strict와 같은 coverage-first 팩터 조합을 기본값으로 사용합니다.",
            )
            trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
            with trend_title_col:
                st.markdown("##### Trend Filter Overlay")
            with trend_help_col:
                _render_trend_filter_help_popover()
            trend_filter_enabled = st.checkbox(
                "Enable",
                value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                key="qsqp_trend_filter_enabled",
            )
            trend_filter_window = int(
                st.number_input(
                    "Trend Filter Window",
                    min_value=20,
                    max_value=400,
                    value=STRICT_TREND_FILTER_DEFAULT_WINDOW,
                    step=10,
                    key="qsqp_trend_filter_window",
                )
            )
            market_regime_enabled, market_regime_window, market_regime_benchmark = _render_market_regime_overlay_inputs(
                key_prefix="qsqp",
                label_prefix="",
            )

        submitted = st.form_submit_button("Run Strict Quarterly Quality Prototype", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("At least one ticker is required.")
    if start_date > end_date:
        validation_errors.append("Start Date must be earlier than or equal to End Date.")
    if not quality_factors:
        validation_errors.append("Select at least one quality factor.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "quality_snapshot_strict_quarterly_prototype",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "top": int(top_n),
        "rebalance_interval": int(rebalance_interval),
        "factor_freq": "quarterly",
        "snapshot_mode": "strict_statement_quarterly",
        "quality_factors": quality_factors,
        "trend_filter_enabled": bool(trend_filter_enabled),
        "trend_filter_window": int(trend_filter_window),
        "market_regime_enabled": bool(market_regime_enabled),
        "market_regime_window": int(market_regime_window),
        "market_regime_benchmark": market_regime_benchmark,
        "universe_contract": universe_contract,
        "dynamic_candidate_tickers": dynamic_candidate_tickers,
        "dynamic_target_size": dynamic_target_size,
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Quality Snapshot (Strict Quarterly Prototype)")


def _render_value_snapshot_strict_quarterly_prototype_form() -> None:
    st.markdown("### Value Snapshot (Strict Quarterly Prototype)")
    st.caption(
        "Research-only quarterly strict value strategy. This Phase 8 path ranks quarterly statement shadow value factors and holds the cheapest names equally between monthly rebalances."
    )
    with st.expander("Data Requirements", expanded=False):
        st.markdown(
            "- `Daily Market Update` 또는 OHLCV 수집으로 **가격 데이터**를 먼저 채워야 합니다.\n"
            "- `Extended Statement Refresh`와 statement shadow factor rebuild가 **quarterly** 기준으로 준비되어 있어야 합니다.\n"
            "- 이 경로는 현재 **research-only quarterly strict value prototype** 입니다.\n"
            "- annual strict value public candidate와 달리, coverage / freshness / interpretation parity를 이번 Phase 8에서 함께 검증합니다."
        )
        st.caption("Current prototype mode: `strict_statement_quarterly` + `shadow_factors` + `research_only`")
        st.caption(
            "주의: 현재 DB의 quarterly shadow coverage 상태에 따라 실제 투자 구간이 요청한 시작일보다 늦게 열릴 수 있습니다. "
            "`US Statement Coverage 100` 기본 preset은 검증용 anchor일 뿐이고, 다른 universe나 수동 ticker 조합은 coverage 상태에 따라 더 늦게 열릴 수 있습니다."
        )
    _apply_single_strategy_prefill("value_snapshot_strict_quarterly_prototype")

    universe_mode = st.radio(
        "Universe Mode",
        options=["Preset", "Manual"],
        horizontal=True,
        help="quarterly strict value prototype first pass는 검증 비용을 낮추기 위해 `US Statement Coverage 100`을 기본 preset으로 둡니다.",
        key="vsqp_universe_mode",
    )

    preset_name = None
    tickers: list[str] = []
    if universe_mode == "Preset":
        preset_name = st.selectbox(
            "Preset",
            options=list(VALUE_STRICT_PRESETS.keys()),
            index=list(VALUE_STRICT_PRESETS.keys()).index(STRICT_QUARTERLY_PROTOTYPE_DEFAULT_PRESET),
            key="vsqp_preset",
        )
        tickers = VALUE_STRICT_PRESETS[preset_name]
        _render_ticker_preview(tickers)
        _render_historical_universe_caption()
    else:
        manual_tickers = st.text_input(
            "Tickers",
            value="AAPL,MSFT,GOOG",
            help="쉼표로 구분한 주식 티커를 입력합니다. 예: AAPL,MSFT,GOOG",
            key="vsqp_manual_tickers",
        )
        tickers = _parse_manual_tickers(manual_tickers)
        _render_ticker_preview(tickers)

    _render_strict_price_freshness_preflight(
        tickers=tickers,
        end_value=st.session_state.get("vsqp_end", DEFAULT_BACKTEST_END_DATE),
        timeframe=st.session_state.get("vsqp_timeframe", "1d"),
        strategy_label="Value Snapshot (Strict Quarterly Prototype)",
    )
    _render_statement_shadow_coverage_preview(
        tickers=tickers,
        freq="quarterly",
        strategy_label="Value Snapshot (Strict Quarterly Prototype)",
    )

    with st.form("value_snapshot_strict_quarterly_prototype_backtest_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("Start Date", value=date(2016, 1, 1), key="vsqp_start")
        with col2:
            end_date = st.date_input("End Date", value=DEFAULT_BACKTEST_END_DATE, key="vsqp_end")
        with col3:
            top_n = st.number_input(
                "Top N",
                min_value=1,
                max_value=50,
                value=10,
                step=1,
                help="strict quarterly value 점수 기준으로 상위 몇 개 종목을 선택할지 정합니다.",
                key="vsqp_top_n",
            )

        st.caption("Research-only defaults in this first pass: `quarterly statement shadow factors`, `monthly rebalance`, `equal-weight holding`.")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="vsqp_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="vsqp_option")
            rebalance_interval = st.number_input(
                "Rebalance Interval",
                min_value=1,
                max_value=12,
                value=1,
                step=1,
                help="기본은 매월 리밸런싱(1)이며, quarterly snapshot 자체는 가장 최근 usable filing 기준으로 따라갑니다.",
                key="vsqp_rebalance_interval",
            )
            universe_contract_label = st.selectbox(
                "Universe Contract",
                options=list(STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.keys()),
                index=0,
                key="vsqp_universe_contract",
                help="Static은 현재 managed preset을 고정해서 사용합니다. Dynamic PIT는 Phase 10 first pass로, quarterly strict에서도 각 리밸런싱 날짜 기준 모집군을 다시 계산합니다.",
            )
            universe_contract = STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS[universe_contract_label]
            dynamic_candidate_tickers, dynamic_target_size = _render_strict_dynamic_universe_contract_note(
                universe_contract=universe_contract,
                tickers=tickers,
                preset_name=preset_name,
                statement_freq="quarterly",
            )
            value_factors = st.multiselect(
                "Value Factors",
                options=VALUE_STRICT_FACTOR_OPTIONS,
                default=VALUE_STRICT_DEFAULT_FACTORS,
                key="vsqp_value_factors",
                help="quarterly prototype도 yield / book-to-market 중심의 coverage-first 기본 조합을 사용합니다.",
            )
            trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
            with trend_title_col:
                st.markdown("##### Trend Filter Overlay")
            with trend_help_col:
                _render_trend_filter_help_popover()
            trend_filter_enabled = st.checkbox(
                "Enable",
                value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                key="vsqp_trend_filter_enabled",
            )
            trend_filter_window = int(
                st.number_input(
                    "Trend Filter Window",
                    min_value=20,
                    max_value=400,
                    value=STRICT_TREND_FILTER_DEFAULT_WINDOW,
                    step=10,
                    key="vsqp_trend_filter_window",
                )
            )
            market_regime_enabled, market_regime_window, market_regime_benchmark = _render_market_regime_overlay_inputs(
                key_prefix="vsqp",
                label_prefix="",
            )

        submitted = st.form_submit_button("Run Strict Quarterly Value Prototype", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("At least one ticker is required.")
    if start_date > end_date:
        validation_errors.append("Start Date must be earlier than or equal to End Date.")
    if not value_factors:
        validation_errors.append("Select at least one value factor.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "value_snapshot_strict_quarterly_prototype",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "top": int(top_n),
        "rebalance_interval": int(rebalance_interval),
        "factor_freq": "quarterly",
        "snapshot_mode": "strict_statement_quarterly",
        "snapshot_source": "shadow_factors",
        "value_factors": value_factors,
        "trend_filter_enabled": bool(trend_filter_enabled),
        "trend_filter_window": int(trend_filter_window),
        "market_regime_enabled": bool(market_regime_enabled),
        "market_regime_window": int(market_regime_window),
        "market_regime_benchmark": market_regime_benchmark,
        "universe_contract": universe_contract,
        "dynamic_candidate_tickers": dynamic_candidate_tickers,
        "dynamic_target_size": dynamic_target_size,
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Value Snapshot (Strict Quarterly Prototype)")


def _render_value_snapshot_strict_annual_form() -> None:
    st.markdown("### Value Snapshot (Strict Annual)")
    st.caption("Strict annual statement-driven value strategy. This public candidate ranks precomputed annual statement shadow factors and holds the cheapest names equally between monthly rebalances.")
    _render_quality_family_guide("value_strict")
    with st.expander("Data Requirements", expanded=False):
        st.markdown(
            "- `Daily Market Update` 또는 OHLCV 수집으로 **가격 데이터**를 먼저 채워야 합니다.\n"
            "- `Extended Statement Refresh`를 **annual** 기준으로 먼저 채워야 합니다.\n"
            "- 현재 value strict path는 **statement shadow factors**를 사용합니다.\n"
            "- valuation 계열은 statement + nearest-period shares fallback hybrid 의미를 가질 수 있습니다.\n"
            "- wider annual coverage 검증은 **US / EDGAR-friendly top-300 stock universe** 기준으로 확인되었습니다."
        )
        st.caption("Current public candidate mode: `strict_statement_annual` + `shadow_factors`")
    _apply_single_strategy_prefill("value_snapshot_strict_annual")

    universe_mode = st.radio(
        "Universe Mode",
        options=["Preset", "Manual"],
        horizontal=True,
        help="strict annual value도 annual coverage가 확인된 preset을 기본값으로 사용합니다.",
        key="vss_universe_mode",
    )

    preset_name = None
    tickers: list[str] = []
    if universe_mode == "Preset":
        preset_name = st.selectbox(
            "Preset",
            options=list(VALUE_STRICT_PRESETS.keys()),
            index=list(VALUE_STRICT_PRESETS.keys()).index(STRICT_ANNUAL_SINGLE_DEFAULT_PRESET),
            key="vss_preset",
        )
        tickers = VALUE_STRICT_PRESETS[preset_name]
        _render_ticker_preview(tickers)
        _render_historical_universe_caption()
        _render_strict_preset_status_note(preset_name)
    else:
        manual_tickers = st.text_input(
            "Tickers",
            value="AAPL,MSFT,GOOG",
            help="쉼표로 구분한 주식 티커를 입력합니다. 예: AAPL,MSFT,GOOG",
            key="vss_manual_tickers",
        )
        tickers = _parse_manual_tickers(manual_tickers)
        _render_ticker_preview(tickers)

    _render_strict_price_freshness_preflight(
        tickers=tickers,
        end_value=st.session_state.get("vss_end", DEFAULT_BACKTEST_END_DATE),
        timeframe=st.session_state.get("vss_timeframe", "1d"),
        strategy_label="Value Snapshot (Strict Annual)",
    )

    with st.form("value_snapshot_strict_annual_backtest_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("Start Date", value=date(2016, 1, 1), key="vss_start")
        with col2:
            end_date = st.date_input("End Date", value=DEFAULT_BACKTEST_END_DATE, key="vss_end")
        with col3:
            top_n = st.number_input(
                "Top N",
                min_value=1,
                max_value=50,
                value=10,
                step=1,
                help="strict annual value 점수 기준으로 상위 몇 개 종목을 선택할지 정합니다.",
                key="vss_top_n",
            )

        st.caption("Hidden defaults in this first pass: `annual statement shadow factors`, `monthly rebalance`, `equal-weight holding`.")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="vss_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="vss_option")
            rebalance_interval = st.number_input(
                "Rebalance Interval",
                min_value=1,
                max_value=12,
                value=1,
                step=1,
                help="기본은 매월 리밸런싱(1)이며, 연구 목적이면 몇 달 간격으로 건너뛸 수도 있습니다.",
                key="vss_rebalance_interval",
            )
            universe_contract_label = st.selectbox(
                "Universe Contract",
                options=list(STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.keys()),
                index=0,
                key="vss_universe_contract",
                help="Static은 현재 managed preset을 고정해서 사용합니다. Dynamic PIT는 Phase 10 first pass로, annual strict에서만 각 리밸런싱 날짜 기준 모집군을 다시 계산합니다.",
            )
            universe_contract = STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS[universe_contract_label]
            dynamic_candidate_tickers, dynamic_target_size = _render_strict_annual_universe_contract_note(
                universe_contract=universe_contract,
                tickers=tickers,
                preset_name=preset_name,
            )
            value_factors = st.multiselect(
                "Value Factors",
                options=VALUE_STRICT_FACTOR_OPTIONS,
                default=VALUE_STRICT_DEFAULT_FACTORS,
                key="vss_value_factors",
                help="높을수록 좋은 yield / book-to-market 계열과 낮을수록 좋은 inverse multiple 계열을 함께 지원합니다.",
            )
            trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
            with trend_title_col:
                st.markdown("##### Trend Filter Overlay")
            with trend_help_col:
                _render_trend_filter_help_popover()
            trend_filter_enabled = st.checkbox(
                "Enable",
                value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                key="vss_trend_filter_enabled",
            )
            trend_filter_window = int(
                st.number_input(
                    "Trend Filter Window",
                    min_value=20,
                    max_value=400,
                    value=STRICT_TREND_FILTER_DEFAULT_WINDOW,
                    step=10,
                    key="vss_trend_filter_window",
                )
            )
            market_regime_enabled, market_regime_window, market_regime_benchmark = _render_market_regime_overlay_inputs(
                key_prefix="vss",
                label_prefix="",
            )
            (
                benchmark_contract,
                min_price_filter,
                min_history_months_filter,
                min_avg_dollar_volume_20d_m_filter,
                transaction_cost_bps,
                benchmark_ticker,
                promotion_min_benchmark_coverage,
                promotion_min_net_cagr_spread,
                promotion_min_liquidity_clean_coverage,
                promotion_max_underperformance_share,
                promotion_min_worst_rolling_excess_return,
                promotion_max_strategy_drawdown,
                promotion_max_drawdown_gap_vs_benchmark,
            ) = _render_strict_annual_real_money_inputs(
                key_prefix="vss",
            )
            (
                underperformance_guardrail_enabled,
                underperformance_guardrail_window_months,
                underperformance_guardrail_threshold,
            ) = _render_underperformance_guardrail_inputs(
                key_prefix="vss",
                label_prefix="Strict Annual Value ",
            )
            (
                drawdown_guardrail_enabled,
                drawdown_guardrail_window_months,
                drawdown_guardrail_strategy_threshold,
                drawdown_guardrail_gap_threshold,
            ) = _render_drawdown_guardrail_inputs(
                key_prefix="vss",
                label_prefix="Strict Annual Value ",
            )

        submitted = st.form_submit_button("Run Strict Annual Value Backtest", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("At least one ticker is required.")
    if start_date > end_date:
        validation_errors.append("Start Date must be earlier than or equal to End Date.")
    if not value_factors:
        validation_errors.append("Select at least one value factor.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "value_snapshot_strict_annual",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "top": int(top_n),
        "rebalance_interval": int(rebalance_interval),
        "factor_freq": "annual",
        "snapshot_mode": "strict_statement_annual",
        "snapshot_source": "shadow_factors",
        "value_factors": value_factors,
        "trend_filter_enabled": bool(trend_filter_enabled),
        "trend_filter_window": int(trend_filter_window),
        "market_regime_enabled": bool(market_regime_enabled),
        "market_regime_window": int(market_regime_window),
        "market_regime_benchmark": market_regime_benchmark,
        "min_price_filter": float(min_price_filter),
        "min_history_months_filter": int(min_history_months_filter),
        "min_avg_dollar_volume_20d_m_filter": float(min_avg_dollar_volume_20d_m_filter),
        "transaction_cost_bps": float(transaction_cost_bps),
        "benchmark_contract": benchmark_contract,
        "benchmark_ticker": benchmark_ticker,
        "promotion_min_benchmark_coverage": float(promotion_min_benchmark_coverage),
        "promotion_min_net_cagr_spread": float(promotion_min_net_cagr_spread),
        "promotion_min_liquidity_clean_coverage": float(promotion_min_liquidity_clean_coverage),
        "promotion_max_underperformance_share": float(promotion_max_underperformance_share),
        "promotion_min_worst_rolling_excess_return": float(promotion_min_worst_rolling_excess_return),
        "promotion_max_strategy_drawdown": float(promotion_max_strategy_drawdown),
        "promotion_max_drawdown_gap_vs_benchmark": float(promotion_max_drawdown_gap_vs_benchmark),
        "underperformance_guardrail_enabled": bool(underperformance_guardrail_enabled),
        "underperformance_guardrail_window_months": int(underperformance_guardrail_window_months),
        "underperformance_guardrail_threshold": float(underperformance_guardrail_threshold),
        "drawdown_guardrail_enabled": bool(drawdown_guardrail_enabled),
        "drawdown_guardrail_window_months": int(drawdown_guardrail_window_months),
        "drawdown_guardrail_strategy_threshold": float(drawdown_guardrail_strategy_threshold),
        "drawdown_guardrail_gap_threshold": float(drawdown_guardrail_gap_threshold),
        "universe_contract": universe_contract,
        "dynamic_candidate_tickers": dynamic_candidate_tickers,
        "dynamic_target_size": dynamic_target_size,
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Value Snapshot (Strict Annual)")


def _render_quality_value_snapshot_strict_quarterly_prototype_form() -> None:
    st.markdown("### Quality + Value Snapshot (Strict Quarterly Prototype)")
    st.caption(
        "Research-only quarterly strict multi-factor strategy. This Phase 8 path blends quarterly quality and value shadow factors, then holds the combined top names equally between monthly rebalances."
    )
    with st.expander("Data Requirements", expanded=False):
        st.markdown(
            "- `Daily Market Update` 또는 OHLCV 수집으로 **가격 데이터**를 먼저 채워야 합니다.\n"
            "- `Extended Statement Refresh`와 statement shadow factor rebuild가 **quarterly** 기준으로 준비되어 있어야 합니다.\n"
            "- 이 경로는 현재 **research-only quarterly strict multi-factor prototype** 입니다.\n"
            "- quality + value availability가 동시에 필요하므로 quarterly quality/value 단독 경로보다 usable history가 조금 더 보수적으로 보일 수 있습니다."
        )
        st.caption("Current prototype mode: `strict_statement_quarterly` + `shadow_factors` + `quality_value_blend` + `research_only`")
        st.caption(
            "주의: 현재 DB의 quarterly shadow coverage 상태에 따라 실제 투자 구간이 요청한 시작일보다 늦게 열릴 수 있습니다. "
            "`US Statement Coverage 100` 기본 preset은 검증 anchor이고, 다른 universe나 수동 ticker 조합은 coverage 상태에 따라 더 늦게 열릴 수 있습니다."
        )
    _apply_single_strategy_prefill("quality_value_snapshot_strict_quarterly_prototype")

    universe_mode = st.radio(
        "Universe Mode",
        options=["Preset", "Manual"],
        horizontal=True,
        help="quarterly strict multi-factor prototype first pass는 검증 비용을 낮추기 위해 `US Statement Coverage 100`을 기본 preset으로 둡니다.",
        key="qvqp_universe_mode",
    )

    preset_name = None
    tickers: list[str] = []
    if universe_mode == "Preset":
        preset_name = st.selectbox(
            "Preset",
            options=list(QUALITY_STRICT_PRESETS.keys()),
            index=list(QUALITY_STRICT_PRESETS.keys()).index(STRICT_QUARTERLY_PROTOTYPE_DEFAULT_PRESET),
            key="qvqp_preset",
        )
        tickers = QUALITY_STRICT_PRESETS[preset_name]
        _render_ticker_preview(tickers)
        _render_historical_universe_caption()
    else:
        manual_tickers = st.text_input(
            "Tickers",
            value="AAPL,MSFT,GOOG",
            help="쉼표로 구분한 주식 티커를 입력합니다. 예: AAPL,MSFT,GOOG",
            key="qvqp_manual_tickers",
        )
        tickers = _parse_manual_tickers(manual_tickers)
        _render_ticker_preview(tickers)

    _render_strict_price_freshness_preflight(
        tickers=tickers,
        end_value=st.session_state.get("qvqp_end", DEFAULT_BACKTEST_END_DATE),
        timeframe=st.session_state.get("qvqp_timeframe", "1d"),
        strategy_label="Quality + Value Snapshot (Strict Quarterly Prototype)",
    )
    _render_statement_shadow_coverage_preview(
        tickers=tickers,
        freq="quarterly",
        strategy_label="Quality + Value Snapshot (Strict Quarterly Prototype)",
    )

    with st.form("quality_value_snapshot_strict_quarterly_prototype_backtest_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("Start Date", value=date(2016, 1, 1), key="qvqp_start")
        with col2:
            end_date = st.date_input("End Date", value=DEFAULT_BACKTEST_END_DATE, key="qvqp_end")
        with col3:
            top_n = st.number_input(
                "Top N",
                min_value=1,
                max_value=30,
                value=10,
                step=1,
                help="strict quarterly multi-factor 종합 점수 기준으로 상위 몇 개 종목을 선택할지 정합니다.",
                key="qvqp_top_n",
            )

        st.caption("Research-only defaults in this first pass: `quarterly statement shadow factors`, `monthly rebalance`, `equal-weight holding`.")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="qvqp_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="qvqp_option")
            rebalance_interval = st.number_input(
                "Rebalance Interval",
                min_value=1,
                max_value=12,
                value=1,
                step=1,
                help="기본은 매월 리밸런싱(1)이며, quarterly snapshot 자체는 가장 최근 usable filing 기준으로 따라갑니다.",
                key="qvqp_rebalance_interval",
            )
            universe_contract_label = st.selectbox(
                "Universe Contract",
                options=list(STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.keys()),
                index=0,
                key="qvqp_universe_contract",
                help="Static은 현재 managed preset을 고정해서 사용합니다. Dynamic PIT는 Phase 10 first pass로, quarterly strict에서도 각 리밸런싱 날짜 기준 모집군을 다시 계산합니다.",
            )
            universe_contract = STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS[universe_contract_label]
            dynamic_candidate_tickers, dynamic_target_size = _render_strict_dynamic_universe_contract_note(
                universe_contract=universe_contract,
                tickers=tickers,
                preset_name=preset_name,
                statement_freq="quarterly",
            )
            quality_factors = st.multiselect(
                "Quality Factors",
                options=QUALITY_STRICT_FACTOR_OPTIONS,
                default=QUALITY_STRICT_DEFAULT_FACTORS,
                key="qvqp_quality_factors",
            )
            value_factors = st.multiselect(
                "Value Factors",
                options=VALUE_STRICT_FACTOR_OPTIONS,
                default=VALUE_STRICT_DEFAULT_FACTORS,
                key="qvqp_value_factors",
            )
            trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
            with trend_title_col:
                st.markdown("##### Trend Filter Overlay")
            with trend_help_col:
                _render_trend_filter_help_popover()
            trend_filter_enabled = st.checkbox(
                "Enable",
                value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                key="qvqp_trend_filter_enabled",
            )
            trend_filter_window = int(
                st.number_input(
                    "Trend Filter Window",
                    min_value=20,
                    max_value=400,
                    value=STRICT_TREND_FILTER_DEFAULT_WINDOW,
                    step=10,
                    key="qvqp_trend_filter_window",
                )
            )
            market_regime_enabled, market_regime_window, market_regime_benchmark = _render_market_regime_overlay_inputs(
                key_prefix="qvqp",
                label_prefix="",
            )

        submitted = st.form_submit_button("Run Strict Quarterly Quality + Value Prototype", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("At least one ticker is required.")
    if start_date > end_date:
        validation_errors.append("Start Date must be earlier than or equal to End Date.")
    if not quality_factors:
        validation_errors.append("Select at least one quality factor.")
    if not value_factors:
        validation_errors.append("Select at least one value factor.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "quality_value_snapshot_strict_quarterly_prototype",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "top": int(top_n),
        "rebalance_interval": int(rebalance_interval),
        "factor_freq": "quarterly",
        "snapshot_mode": "strict_statement_quarterly",
        "snapshot_source": "shadow_factors",
        "quality_factors": quality_factors,
        "value_factors": value_factors,
        "trend_filter_enabled": bool(trend_filter_enabled),
        "trend_filter_window": int(trend_filter_window),
        "market_regime_enabled": bool(market_regime_enabled),
        "market_regime_window": int(market_regime_window),
        "market_regime_benchmark": market_regime_benchmark,
        "universe_contract": universe_contract,
        "dynamic_candidate_tickers": dynamic_candidate_tickers,
        "dynamic_target_size": dynamic_target_size,
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Quality + Value Snapshot (Strict Quarterly Prototype)")


def _render_quality_value_snapshot_strict_annual_form() -> None:
    st.markdown("### Quality + Value Snapshot (Strict Annual)")
    st.caption(
        "Strict annual multi-factor strategy. This public candidate blends coverage-first quality signals "
        "with annual statement-driven valuation factors, then holds the combined top names equally between monthly rebalances."
    )
    _render_quality_family_guide("quality_value_strict")
    with st.expander("Data Requirements", expanded=False):
        st.markdown(
            "- `Daily Market Update` 또는 OHLCV 수집으로 **가격 데이터**를 먼저 채워야 합니다.\n"
            "- `Extended Statement Refresh`를 **annual** 기준으로 먼저 채워야 합니다.\n"
            "- 현재 multi-factor strict path는 **statement shadow factors**를 사용합니다.\n"
            "- quality + value factor availability가 동시에 필요하므로 usable history는 quality strict보다 조금 더 보수적으로 보셔야 합니다.\n"
            "- wider annual coverage 검증은 **US / EDGAR-friendly stock universe** 기준으로 진행합니다."
        )
        st.caption("Current public candidate mode: `strict_statement_annual` + `shadow_factors` + `quality_value_blend`")
    _apply_single_strategy_prefill("quality_value_snapshot_strict_annual")

    universe_mode = st.radio(
        "Universe Mode",
        options=["Preset", "Manual"],
        horizontal=True,
        help="strict annual multi-factor도 annual coverage가 검증된 preset을 기본값으로 사용합니다.",
        key="qvss_universe_mode",
    )

    preset_name = None
    tickers: list[str] = []
    if universe_mode == "Preset":
        preset_name = st.selectbox(
            "Preset",
            options=list(QUALITY_STRICT_PRESETS.keys()),
            index=list(QUALITY_STRICT_PRESETS.keys()).index(STRICT_ANNUAL_SINGLE_DEFAULT_PRESET),
            key="qvss_preset",
        )
        tickers = QUALITY_STRICT_PRESETS[preset_name]
        _render_ticker_preview(tickers)
        _render_historical_universe_caption()
        _render_strict_preset_status_note(preset_name)
    else:
        manual_tickers = st.text_input(
            "Tickers",
            value="AAPL,MSFT,GOOG",
            help="쉼표로 구분한 주식 티커를 입력합니다. 예: AAPL,MSFT,GOOG",
            key="qvss_manual_tickers",
        )
        tickers = _parse_manual_tickers(manual_tickers)
        _render_ticker_preview(tickers)

    _render_strict_price_freshness_preflight(
        tickers=tickers,
        end_value=st.session_state.get("qvss_end", DEFAULT_BACKTEST_END_DATE),
        timeframe=st.session_state.get("qvss_timeframe", "1d"),
        strategy_label="Quality + Value Snapshot (Strict Annual)",
    )

    with st.form("quality_value_snapshot_strict_annual_backtest_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("Start Date", value=date(2016, 1, 1), key="qvss_start")
        with col2:
            end_date = st.date_input("End Date", value=DEFAULT_BACKTEST_END_DATE, key="qvss_end")
        with col3:
            top_n = st.number_input(
                "Top N",
                min_value=1,
                max_value=30,
                value=10,
                step=1,
                help="strict annual multi-factor 종합 점수 기준으로 상위 몇 개 종목을 선택할지 정합니다.",
                key="qvss_top_n",
            )

        st.caption("Hidden defaults in this first pass: `annual statement shadow factors`, `monthly rebalance`, `equal-weight holding`.")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="qvss_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="qvss_option")
            rebalance_interval = st.number_input(
                "Rebalance Interval",
                min_value=1,
                max_value=12,
                value=1,
                step=1,
                help="기본은 매월 리밸런싱(1)이며, 연구 목적이면 몇 달 간격으로 건너뛸 수도 있습니다.",
                key="qvss_rebalance_interval",
            )
            universe_contract_label = st.selectbox(
                "Universe Contract",
                options=list(STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.keys()),
                index=0,
                key="qvss_universe_contract",
                help="Static은 현재 managed preset을 고정해서 사용합니다. Dynamic PIT는 Phase 10 first pass로, annual strict에서만 각 리밸런싱 날짜 기준 모집군을 다시 계산합니다.",
            )
            universe_contract = STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS[universe_contract_label]
            dynamic_candidate_tickers, dynamic_target_size = _render_strict_annual_universe_contract_note(
                universe_contract=universe_contract,
                tickers=tickers,
                preset_name=preset_name,
            )
            quality_factors = st.multiselect(
                "Quality Factors",
                options=QUALITY_STRICT_FACTOR_OPTIONS,
                default=QUALITY_STRICT_DEFAULT_FACTORS,
                key="qvss_quality_factors",
            )
            value_factors = st.multiselect(
                "Value Factors",
                options=VALUE_STRICT_FACTOR_OPTIONS,
                default=VALUE_STRICT_DEFAULT_FACTORS,
                key="qvss_value_factors",
            )
            trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
            with trend_title_col:
                st.markdown("##### Trend Filter Overlay")
            with trend_help_col:
                _render_trend_filter_help_popover()
            trend_filter_enabled = st.checkbox(
                "Enable",
                value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                key="qvss_trend_filter_enabled",
            )
            trend_filter_window = int(
                st.number_input(
                    "Trend Filter Window",
                    min_value=20,
                    max_value=400,
                    value=STRICT_TREND_FILTER_DEFAULT_WINDOW,
                    step=10,
                    key="qvss_trend_filter_window",
                )
            )
            market_regime_enabled, market_regime_window, market_regime_benchmark = _render_market_regime_overlay_inputs(
                key_prefix="qvss",
                label_prefix="",
            )
            (
                benchmark_contract,
                min_price_filter,
                min_history_months_filter,
                min_avg_dollar_volume_20d_m_filter,
                transaction_cost_bps,
                benchmark_ticker,
                promotion_min_benchmark_coverage,
                promotion_min_net_cagr_spread,
                promotion_min_liquidity_clean_coverage,
                promotion_max_underperformance_share,
                promotion_min_worst_rolling_excess_return,
                promotion_max_strategy_drawdown,
                promotion_max_drawdown_gap_vs_benchmark,
            ) = _render_strict_annual_real_money_inputs(
                key_prefix="qvss",
            )
            (
                underperformance_guardrail_enabled,
                underperformance_guardrail_window_months,
                underperformance_guardrail_threshold,
            ) = _render_underperformance_guardrail_inputs(
                key_prefix="qvss",
                label_prefix="Strict Annual Multi-Factor ",
            )
            (
                drawdown_guardrail_enabled,
                drawdown_guardrail_window_months,
                drawdown_guardrail_strategy_threshold,
                drawdown_guardrail_gap_threshold,
            ) = _render_drawdown_guardrail_inputs(
                key_prefix="qvss",
                label_prefix="Strict Annual Multi-Factor ",
            )

        submitted = st.form_submit_button("Run Strict Annual Quality + Value Backtest", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("At least one ticker is required.")
    if start_date > end_date:
        validation_errors.append("Start Date must be earlier than or equal to End Date.")
    if not quality_factors:
        validation_errors.append("Select at least one quality factor.")
    if not value_factors:
        validation_errors.append("Select at least one value factor.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "quality_value_snapshot_strict_annual",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "top": int(top_n),
        "rebalance_interval": int(rebalance_interval),
        "factor_freq": "annual",
        "snapshot_mode": "strict_statement_annual",
        "snapshot_source": "shadow_factors",
        "quality_factors": quality_factors,
        "value_factors": value_factors,
        "trend_filter_enabled": bool(trend_filter_enabled),
        "trend_filter_window": int(trend_filter_window),
        "market_regime_enabled": bool(market_regime_enabled),
        "market_regime_window": int(market_regime_window),
        "market_regime_benchmark": market_regime_benchmark,
        "min_price_filter": float(min_price_filter),
        "min_history_months_filter": int(min_history_months_filter),
        "min_avg_dollar_volume_20d_m_filter": float(min_avg_dollar_volume_20d_m_filter),
        "transaction_cost_bps": float(transaction_cost_bps),
        "benchmark_contract": benchmark_contract,
        "benchmark_ticker": benchmark_ticker,
        "promotion_min_benchmark_coverage": float(promotion_min_benchmark_coverage),
        "promotion_min_net_cagr_spread": float(promotion_min_net_cagr_spread),
        "promotion_min_liquidity_clean_coverage": float(promotion_min_liquidity_clean_coverage),
        "promotion_max_underperformance_share": float(promotion_max_underperformance_share),
        "promotion_min_worst_rolling_excess_return": float(promotion_min_worst_rolling_excess_return),
        "promotion_max_strategy_drawdown": float(promotion_max_strategy_drawdown),
        "promotion_max_drawdown_gap_vs_benchmark": float(promotion_max_drawdown_gap_vs_benchmark),
        "underperformance_guardrail_enabled": bool(underperformance_guardrail_enabled),
        "underperformance_guardrail_window_months": int(underperformance_guardrail_window_months),
        "underperformance_guardrail_threshold": float(underperformance_guardrail_threshold),
        "drawdown_guardrail_enabled": bool(drawdown_guardrail_enabled),
        "drawdown_guardrail_window_months": int(drawdown_guardrail_window_months),
        "drawdown_guardrail_strategy_threshold": float(drawdown_guardrail_strategy_threshold),
        "drawdown_guardrail_gap_threshold": float(drawdown_guardrail_gap_threshold),
        "universe_contract": universe_contract,
        "dynamic_candidate_tickers": dynamic_candidate_tickers,
        "dynamic_target_size": dynamic_target_size,
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Quality + Value Snapshot (Strict Annual)")


def render_backtest_tab() -> None:
    _init_backtest_state()

    st.subheader("Backtest")
    st.caption("단일 전략 실행, 전략 비교, 실행 이력을 한 화면에서 관리합니다.")

    with st.expander("Backtest 사용 안내", expanded=False):
        st.markdown(
            """
            - `Single Strategy`: 전략 1개를 실행하고 결과를 바로 확인하는 화면입니다.
            - `Compare & Portfolio Builder`: 여러 전략을 같은 기간으로 비교하는 화면입니다.
            - `History`: 저장된 실행 결과를 다시 보고, `Run Again` 또는 `Load Into Form`을 사용하는 화면입니다.
            - `Load Into Form`을 누르면 저장된 입력값이 `Single Strategy` 화면으로 자동 이동하며 다시 채워집니다.
            - `quarterly strict prototype` 전략은 현재 **research-only** 경로입니다.
            """
        )
        st.caption(
            "`늦은 active start`는 요청한 시작일에는 아직 usable한 statement shadow가 부족해서, "
            "실제 첫 보유/선택이 그보다 뒤에서 시작되는 상황을 뜻합니다."
        )

    active_panel = st.radio(
        "Backtest Panel",
        options=["Single Strategy", "Compare & Portfolio Builder", "History"],
        horizontal=True,
        label_visibility="collapsed",
        key="backtest_active_panel",
    )

    if active_panel == "Single Strategy":
        prefill_notice = st.session_state.get("backtest_prefill_notice")
        if prefill_notice:
            st.info(prefill_notice)
            prefill_lines = _build_prefill_summary_lines(st.session_state.get("backtest_prefill_payload"))
            if prefill_lines:
                st.caption("이번에 불러온 입력값 요약")
                st.markdown("\n".join(f"- {line}" for line in prefill_lines))
            st.session_state.backtest_prefill_notice = None

        pending_strategy_choice = st.session_state.get("backtest_prefill_strategy_choice")
        pending_strategy_variant = st.session_state.get("backtest_prefill_strategy_variant")
        if pending_strategy_choice not in SINGLE_STRATEGY_OPTIONS:
            remapped_choice, remapped_variant = display_name_to_selection(pending_strategy_choice)
            if remapped_choice in SINGLE_STRATEGY_OPTIONS:
                pending_strategy_choice = remapped_choice
                pending_strategy_variant = pending_strategy_variant or remapped_variant
        if pending_strategy_choice in SINGLE_STRATEGY_OPTIONS:
            st.session_state.backtest_strategy_choice = pending_strategy_choice
            variant_key = _single_family_variant_session_key(pending_strategy_choice)
            if variant_key and pending_strategy_variant in family_variant_options(pending_strategy_choice):
                st.session_state[variant_key] = pending_strategy_variant
            st.session_state.backtest_prefill_strategy_choice = None
            st.session_state.backtest_prefill_strategy_variant = None

        current_strategy_choice = st.session_state.get("backtest_strategy_choice")
        if current_strategy_choice not in SINGLE_STRATEGY_OPTIONS:
            remapped_choice, remapped_variant = display_name_to_selection(current_strategy_choice)
            if remapped_choice in SINGLE_STRATEGY_OPTIONS:
                st.session_state.backtest_strategy_choice = remapped_choice
                variant_key = _single_family_variant_session_key(remapped_choice)
                if variant_key and remapped_variant in family_variant_options(remapped_choice):
                    st.session_state[variant_key] = remapped_variant

        strategy_choice = st.selectbox(
            "Strategy",
            options=SINGLE_STRATEGY_OPTIONS,
            index=0,
            help="The first Phase 4 UI keeps one strategy form visible at a time.",
            key="backtest_strategy_choice",
        )

        st.divider()
        if strategy_choice == "Equal Weight":
            _render_equal_weight_form()
        elif strategy_choice == "GTAA":
            _render_gtaa_form()
        elif strategy_choice == "Risk Parity Trend":
            _render_risk_parity_form()
        elif strategy_choice == "Dual Momentum":
            _render_dual_momentum_form()
        else:
            _render_single_strategy_family_form(strategy_choice)
        st.divider()
        _render_last_run()

    elif active_panel == "Compare & Portfolio Builder":
        st.markdown("### Compare Strategies")
        st.caption("Start with a shared date range and compare up to four strategies chosen from the current DB-backed strategy surface. This section then feeds directly into a weighted portfolio builder.")
        _apply_compare_prefill()

        compare_prefill_notice = st.session_state.get("backtest_compare_prefill_notice")
        if compare_prefill_notice:
            st.info(compare_prefill_notice)
            st.session_state.backtest_compare_prefill_notice = None

        current_compare_selection = list(st.session_state.get("compare_selected_strategies") or [])
        normalized_compare_selection: list[str] = []
        for strategy_name in current_compare_selection:
            resolved_choice, resolved_variant = display_name_to_selection(strategy_name)
            normalized_choice = resolved_choice or strategy_name
            if normalized_choice in COMPARE_STRATEGY_OPTIONS and normalized_choice not in normalized_compare_selection:
                normalized_compare_selection.append(normalized_choice)
            variant_key = _compare_family_variant_session_key(normalized_choice)
            if variant_key and resolved_variant in family_variant_options(normalized_choice):
                st.session_state[variant_key] = resolved_variant
        if normalized_compare_selection and normalized_compare_selection != current_compare_selection:
            st.session_state["compare_selected_strategies"] = normalized_compare_selection

        selected_strategies = st.multiselect(
            "Strategies",
            options=COMPARE_STRATEGY_OPTIONS,
            default=["Equal Weight", "GTAA"],
            max_selections=4,
            help="Up to four strategies can be compared at once in the first pass.",
            key="compare_selected_strategies",
        )
        st.caption("Strategy selection is outside the form so the strategy-specific sections update immediately.")

        compare_eq_universe_mode = "preset"
        compare_eq_preset_name: str | None = "Dividend ETFs"
        compare_eq_tickers = list(EQUAL_WEIGHT_PRESETS["Dividend ETFs"])

        compare_gtaa_universe_mode = "preset"
        compare_gtaa_preset_name: str | None = "GTAA Universe"
        compare_gtaa_tickers = list(GTAA_DEFAULT_TICKERS)

        with st.form("compare_backtests_form", clear_on_submit=False):
            col1, col2 = st.columns(2)
            with col1:
                compare_start = st.date_input("Start Date", value=date(2016, 1, 1), key="compare_start")
            with col2:
                compare_end = st.date_input("End Date", value=DEFAULT_BACKTEST_END_DATE, key="compare_end")

            with st.expander("Advanced Inputs", expanded=True):
                compare_timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="compare_timeframe")
                compare_option = st.selectbox("Option", options=["month_end"], index=0, key="compare_option")
                st.markdown("##### Strategy-Specific Advanced Inputs")

                compare_strategy_overrides: dict[str, dict] = {}
                quality_compare_strategy_name: str | None = None
                value_compare_strategy_name: str | None = None
                quality_value_compare_strategy_name: str | None = None

                if "Quality" in selected_strategies:
                    with st.expander("Quality Family", expanded=True):
                        quality_compare_variant = st.selectbox(
                            "Quality Variant",
                            options=family_variant_options("Quality"),
                            key="compare_quality_variant",
                        )
                        quality_compare_strategy_name = resolve_concrete_strategy_display_name(
                            "Quality",
                            quality_compare_variant,
                        )
                        st.caption(f"현재 compare 실행 variant: `{quality_compare_strategy_name}`")

                if "Value" in selected_strategies:
                    with st.expander("Value Family", expanded=True):
                        value_compare_variant = st.selectbox(
                            "Value Variant",
                            options=family_variant_options("Value"),
                            key="compare_value_variant",
                        )
                        value_compare_strategy_name = resolve_concrete_strategy_display_name(
                            "Value",
                            value_compare_variant,
                        )
                        st.caption(f"현재 compare 실행 variant: `{value_compare_strategy_name}`")

                if "Quality + Value" in selected_strategies:
                    with st.expander("Quality + Value Family", expanded=True):
                        quality_value_compare_variant = st.selectbox(
                            "Quality + Value Variant",
                            options=family_variant_options("Quality + Value"),
                            key="compare_quality_value_variant",
                        )
                        quality_value_compare_strategy_name = resolve_concrete_strategy_display_name(
                            "Quality + Value",
                            quality_value_compare_variant,
                        )
                        st.caption(f"현재 compare 실행 variant: `{quality_value_compare_strategy_name}`")

                if "Equal Weight" in selected_strategies:
                    with st.expander("Equal Weight", expanded=True):
                        (
                            compare_eq_universe_mode,
                            compare_eq_preset_name,
                            compare_eq_tickers,
                        ) = _render_equal_weight_universe_inputs(
                            key_prefix="compare_eq",
                            radio_label="Equal Weight Universe Mode",
                            preset_label="Equal Weight Preset",
                            ticker_label="Equal Weight Tickers",
                        )
                        compare_strategy_overrides["Equal Weight"] = {
                            "tickers": list(compare_eq_tickers),
                            "preset_name": compare_eq_preset_name,
                            "universe_mode": compare_eq_universe_mode,
                            "rebalance_interval": int(
                                st.number_input(
                                    "Equal Weight Rebalance Interval",
                                    min_value=1,
                                    max_value=36,
                                    value=12,
                                    step=1,
                                    key="compare_eq_interval",
                                )
                            )
                        }

                if "GTAA" in selected_strategies:
                    with st.expander("GTAA", expanded=True):
                        (
                            compare_gtaa_universe_mode,
                            compare_gtaa_preset_name,
                            compare_gtaa_tickers,
                        ) = _render_gtaa_universe_inputs(
                            key_prefix="compare_gtaa",
                            radio_label="GTAA Universe Mode",
                            preset_label="GTAA Preset",
                            ticker_label="GTAA Tickers",
                        )
                        (
                            min_price_filter,
                            transaction_cost_bps,
                            benchmark_ticker,
                            promotion_min_etf_aum_b,
                            promotion_max_bid_ask_spread_pct,
                        ) = _render_etf_real_money_inputs(
                            key_prefix="compare_gtaa",
                        )
                        (
                            underperformance_guardrail_enabled,
                            underperformance_guardrail_window_months,
                            underperformance_guardrail_threshold,
                            drawdown_guardrail_enabled,
                            drawdown_guardrail_window_months,
                            drawdown_guardrail_strategy_threshold,
                            drawdown_guardrail_gap_threshold,
                        ) = _render_etf_guardrail_inputs(
                            key_prefix="compare_gtaa",
                            label_prefix="GTAA ",
                        )
                        compare_gtaa_score_lookback_months, compare_gtaa_score_weights = _render_gtaa_score_weight_inputs(
                            key_prefix="compare_gtaa"
                        )
                        risk_off_contract = _render_gtaa_risk_off_contract_inputs(key_prefix="compare_gtaa")
                        compare_strategy_overrides["GTAA"] = {
                            "tickers": list(compare_gtaa_tickers),
                            "preset_name": compare_gtaa_preset_name,
                            "universe_mode": compare_gtaa_universe_mode,
                            "top": int(
                                st.number_input(
                                    "GTAA Top Assets",
                                    min_value=1,
                                    max_value=12,
                                    value=3,
                                    step=1,
                                    key="compare_gtaa_top",
                                )
                            ),
                            "interval": int(
                                st.number_input(
                                    "GTAA Signal Interval (months)",
                                    min_value=1,
                                    max_value=12,
                                    value=GTAA_DEFAULT_SIGNAL_INTERVAL,
                                    step=1,
                                    key="compare_gtaa_interval",
                                )
                            ),
                            "score_lookback_months": list(compare_gtaa_score_lookback_months),
                            "score_return_columns": [_gtaa_return_col_from_months(months) for months in compare_gtaa_score_lookback_months],
                            "score_weights": compare_gtaa_score_weights,
                            "trend_filter_window": int(risk_off_contract["trend_filter_window"]),
                            "risk_off_mode": risk_off_contract["risk_off_mode"],
                            "defensive_tickers": list(risk_off_contract["defensive_tickers"]),
                            "market_regime_enabled": bool(risk_off_contract["market_regime_enabled"]),
                            "market_regime_window": int(risk_off_contract["market_regime_window"]),
                            "market_regime_benchmark": risk_off_contract["market_regime_benchmark"],
                            "crash_guardrail_enabled": bool(risk_off_contract["crash_guardrail_enabled"]),
                            "crash_guardrail_drawdown_threshold": float(risk_off_contract["crash_guardrail_drawdown_threshold"]),
                            "crash_guardrail_lookback_months": int(risk_off_contract["crash_guardrail_lookback_months"]),
                            "min_price_filter": float(min_price_filter),
                            "transaction_cost_bps": float(transaction_cost_bps),
                            "benchmark_ticker": benchmark_ticker,
                            "promotion_min_etf_aum_b": float(promotion_min_etf_aum_b),
                            "promotion_max_bid_ask_spread_pct": float(promotion_max_bid_ask_spread_pct),
                            "underperformance_guardrail_enabled": bool(underperformance_guardrail_enabled),
                            "underperformance_guardrail_window_months": int(underperformance_guardrail_window_months),
                            "underperformance_guardrail_threshold": float(underperformance_guardrail_threshold),
                            "drawdown_guardrail_enabled": bool(drawdown_guardrail_enabled),
                            "drawdown_guardrail_window_months": int(drawdown_guardrail_window_months),
                            "drawdown_guardrail_strategy_threshold": float(drawdown_guardrail_strategy_threshold),
                            "drawdown_guardrail_gap_threshold": float(drawdown_guardrail_gap_threshold),
                        }

                if "Risk Parity Trend" in selected_strategies:
                    st.markdown("**Risk Parity Trend**")
                    (
                        min_price_filter,
                        transaction_cost_bps,
                        benchmark_ticker,
                        promotion_min_etf_aum_b,
                        promotion_max_bid_ask_spread_pct,
                    ) = _render_etf_real_money_inputs(
                        key_prefix="compare_rp",
                    )
                    (
                        underperformance_guardrail_enabled,
                        underperformance_guardrail_window_months,
                        underperformance_guardrail_threshold,
                        drawdown_guardrail_enabled,
                        drawdown_guardrail_window_months,
                        drawdown_guardrail_strategy_threshold,
                        drawdown_guardrail_gap_threshold,
                    ) = _render_etf_guardrail_inputs(
                        key_prefix="compare_rp",
                        label_prefix="Risk Parity ",
                    )
                    compare_strategy_overrides["Risk Parity Trend"] = {
                        "rebalance_interval": int(
                            st.number_input(
                                "Risk Parity Rebalance Interval",
                                min_value=1,
                                max_value=12,
                                value=1,
                                step=1,
                                key="compare_rp_interval",
                            )
                        ),
                        "vol_window": int(
                            st.number_input(
                                "Risk Parity Vol Window (months)",
                                min_value=1,
                                max_value=24,
                                value=6,
                                step=1,
                                key="compare_rp_vol_window",
                            )
                        ),
                        "min_price_filter": float(min_price_filter),
                        "transaction_cost_bps": float(transaction_cost_bps),
                        "benchmark_ticker": benchmark_ticker,
                        "promotion_min_etf_aum_b": float(promotion_min_etf_aum_b),
                        "promotion_max_bid_ask_spread_pct": float(promotion_max_bid_ask_spread_pct),
                        "underperformance_guardrail_enabled": bool(underperformance_guardrail_enabled),
                        "underperformance_guardrail_window_months": int(underperformance_guardrail_window_months),
                        "underperformance_guardrail_threshold": float(underperformance_guardrail_threshold),
                        "drawdown_guardrail_enabled": bool(drawdown_guardrail_enabled),
                        "drawdown_guardrail_window_months": int(drawdown_guardrail_window_months),
                        "drawdown_guardrail_strategy_threshold": float(drawdown_guardrail_strategy_threshold),
                        "drawdown_guardrail_gap_threshold": float(drawdown_guardrail_gap_threshold),
                    }

                if "Dual Momentum" in selected_strategies:
                    st.markdown("**Dual Momentum**")
                    (
                        min_price_filter,
                        transaction_cost_bps,
                        benchmark_ticker,
                        promotion_min_etf_aum_b,
                        promotion_max_bid_ask_spread_pct,
                    ) = _render_etf_real_money_inputs(
                        key_prefix="compare_dm",
                    )
                    (
                        underperformance_guardrail_enabled,
                        underperformance_guardrail_window_months,
                        underperformance_guardrail_threshold,
                        drawdown_guardrail_enabled,
                        drawdown_guardrail_window_months,
                        drawdown_guardrail_strategy_threshold,
                        drawdown_guardrail_gap_threshold,
                    ) = _render_etf_guardrail_inputs(
                        key_prefix="compare_dm",
                        label_prefix="Dual Momentum ",
                    )
                    compare_strategy_overrides["Dual Momentum"] = {
                        "top": int(
                            st.number_input(
                                "Dual Momentum Top Assets",
                                min_value=1,
                                max_value=5,
                                value=1,
                                step=1,
                                key="compare_dm_top",
                            )
                        ),
                        "rebalance_interval": int(
                            st.number_input(
                                "Dual Momentum Rebalance Interval",
                                min_value=1,
                                max_value=12,
                                value=1,
                                step=1,
                                key="compare_dm_interval",
                            )
                        ),
                        "min_price_filter": float(min_price_filter),
                        "transaction_cost_bps": float(transaction_cost_bps),
                        "benchmark_ticker": benchmark_ticker,
                        "promotion_min_etf_aum_b": float(promotion_min_etf_aum_b),
                        "promotion_max_bid_ask_spread_pct": float(promotion_max_bid_ask_spread_pct),
                        "underperformance_guardrail_enabled": bool(underperformance_guardrail_enabled),
                        "underperformance_guardrail_window_months": int(underperformance_guardrail_window_months),
                        "underperformance_guardrail_threshold": float(underperformance_guardrail_threshold),
                        "drawdown_guardrail_enabled": bool(drawdown_guardrail_enabled),
                        "drawdown_guardrail_window_months": int(drawdown_guardrail_window_months),
                        "drawdown_guardrail_strategy_threshold": float(drawdown_guardrail_strategy_threshold),
                        "drawdown_guardrail_gap_threshold": float(drawdown_guardrail_gap_threshold),
                    }

                if quality_compare_strategy_name == "Quality Snapshot":
                    st.markdown("**Quality Snapshot**")
                    compare_strategy_overrides["Quality Snapshot"] = {
                        "top_n": int(
                            st.number_input(
                                "Quality Top N",
                                min_value=1,
                                max_value=20,
                                value=2,
                                step=1,
                                key="compare_qs_top_n",
                            )
                        ),
                        "quality_factors": st.multiselect(
                            "Quality Factors",
                            options=["roe", "gross_margin", "operating_margin", "debt_ratio"],
                            default=["roe", "gross_margin", "operating_margin", "debt_ratio"],
                            key="compare_qs_factors",
                        ),
                        "factor_freq": "annual",
                        "rebalance_freq": "monthly",
                        "snapshot_mode": "broad_research",
                    }

                if quality_compare_strategy_name == "Quality Snapshot (Strict Annual)":
                    with st.expander("Quality Snapshot (Strict Annual)", expanded=False):
                        st.caption("Compare mode keeps the strict annual default lighter with `US Statement Coverage 100` so multi-strategy runs stay responsive.")
                        qss_compare_preset = st.selectbox(
                            "Strict Annual Quality Preset",
                            options=list(QUALITY_STRICT_PRESETS.keys()),
                            index=list(QUALITY_STRICT_PRESETS.keys()).index(STRICT_ANNUAL_COMPARE_DEFAULT_PRESET),
                            key="compare_qss_preset",
                        )
                        qss_compare_contract_label = st.selectbox(
                            "Strict Annual Quality Universe Contract",
                            options=list(STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.keys()),
                            index=0,
                            key="compare_qss_universe_contract",
                            help="Static은 현재 managed preset을 고정해서 사용합니다. Dynamic PIT는 Phase 10 first pass로, annual strict compare에서도 각 리밸런싱 날짜 기준 membership를 다시 계산합니다.",
                        )
                        qss_compare_universe_contract = STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS[qss_compare_contract_label]
                        qss_dynamic_candidate_tickers, qss_dynamic_target_size = _render_strict_annual_universe_contract_note(
                            universe_contract=qss_compare_universe_contract,
                            tickers=QUALITY_STRICT_PRESETS[qss_compare_preset],
                            preset_name=qss_compare_preset,
                        )
                        _render_ticker_preview(QUALITY_STRICT_PRESETS[qss_compare_preset], preview_count=8, tail_count=3)
                        _render_historical_universe_caption()
                        compare_strategy_overrides["Quality Snapshot (Strict Annual)"] = {
                            "preset_name": qss_compare_preset,
                            "tickers": QUALITY_STRICT_PRESETS[qss_compare_preset],
                            "universe_mode": "preset",
                            "universe_contract": qss_compare_universe_contract,
                            "dynamic_candidate_tickers": qss_dynamic_candidate_tickers,
                            "dynamic_target_size": qss_dynamic_target_size,
                            "top_n": int(
                                st.number_input(
                                    "Strict Annual Quality Top N",
                                    min_value=1,
                                    max_value=20,
                                    value=2,
                                    step=1,
                                    key="compare_qss_top_n",
                                )
                            ),
                            "rebalance_interval": int(
                                st.number_input(
                                    "Strict Annual Quality Rebalance Interval",
                                    min_value=1,
                                    max_value=12,
                                    value=1,
                                    step=1,
                                    key="compare_qss_rebalance_interval",
                                )
                            ),
                            "quality_factors": st.multiselect(
                                "Strict Annual Quality Factors",
                                options=QUALITY_STRICT_FACTOR_OPTIONS,
                                default=QUALITY_STRICT_DEFAULT_FACTORS,
                                key="compare_qss_factors",
                            ),
                        }
                        trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
                        with trend_title_col:
                            st.markdown("##### Strict Annual Quality Trend Filter")
                        with trend_help_col:
                            _render_trend_filter_help_popover()
                        compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["trend_filter_enabled"] = st.checkbox(
                            "Enable",
                            value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                            key="compare_qss_trend_filter_enabled",
                        )
                        compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["trend_filter_window"] = int(
                            st.number_input(
                                "Strict Annual Quality Trend Filter Window",
                                min_value=20,
                                max_value=400,
                                value=STRICT_TREND_FILTER_DEFAULT_WINDOW,
                                step=10,
                                key="compare_qss_trend_filter_window",
                            )
                        )
                        (
                            compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["market_regime_enabled"],
                            compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["market_regime_window"],
                            compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["market_regime_benchmark"],
                        ) = _render_market_regime_overlay_inputs(
                            key_prefix="compare_qss",
                            label_prefix="Strict Annual Quality ",
                        )
                        (
                            benchmark_contract,
                            min_price_filter,
                            min_history_months_filter,
                            min_avg_dollar_volume_20d_m_filter,
                            transaction_cost_bps,
                            benchmark_ticker,
                            promotion_min_benchmark_coverage,
                            promotion_min_net_cagr_spread,
                            promotion_min_liquidity_clean_coverage,
                            promotion_max_underperformance_share,
                            promotion_min_worst_rolling_excess_return,
                            promotion_max_strategy_drawdown,
                            promotion_max_drawdown_gap_vs_benchmark,
                        ) = _render_strict_annual_real_money_inputs(
                            key_prefix="compare_qss",
                        )
                        compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["min_price_filter"] = float(min_price_filter)
                        compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["min_history_months_filter"] = int(min_history_months_filter)
                        compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["min_avg_dollar_volume_20d_m_filter"] = float(min_avg_dollar_volume_20d_m_filter)
                        compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["transaction_cost_bps"] = float(transaction_cost_bps)
                        compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["benchmark_contract"] = benchmark_contract
                        compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["benchmark_ticker"] = benchmark_ticker
                        compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["promotion_min_benchmark_coverage"] = float(promotion_min_benchmark_coverage)
                        compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["promotion_min_net_cagr_spread"] = float(promotion_min_net_cagr_spread)
                        compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["promotion_min_liquidity_clean_coverage"] = float(promotion_min_liquidity_clean_coverage)
                        compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["promotion_max_underperformance_share"] = float(promotion_max_underperformance_share)
                        compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["promotion_min_worst_rolling_excess_return"] = float(promotion_min_worst_rolling_excess_return)
                        compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["promotion_max_strategy_drawdown"] = float(promotion_max_strategy_drawdown)
                        compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["promotion_max_drawdown_gap_vs_benchmark"] = float(promotion_max_drawdown_gap_vs_benchmark)
                        (
                            compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["underperformance_guardrail_enabled"],
                            compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["underperformance_guardrail_window_months"],
                            compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["underperformance_guardrail_threshold"],
                        ) = _render_underperformance_guardrail_inputs(
                            key_prefix="compare_qss",
                            label_prefix="Strict Annual Quality ",
                        )
                        (
                            compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["drawdown_guardrail_enabled"],
                            compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["drawdown_guardrail_window_months"],
                            compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["drawdown_guardrail_strategy_threshold"],
                            compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["drawdown_guardrail_gap_threshold"],
                        ) = _render_drawdown_guardrail_inputs(
                            key_prefix="compare_qss",
                            label_prefix="Strict Annual Quality ",
                        )

                if quality_compare_strategy_name == "Quality Snapshot (Strict Quarterly Prototype)":
                    with st.expander("Quality Snapshot (Strict Quarterly Prototype)", expanded=False):
                        st.caption("Research-only compare path. Default preset stays at `US Statement Coverage 100` to keep quarterly family validation tractable.")
                        qsqp_compare_preset = st.selectbox(
                            "Strict Quarterly Quality Preset",
                            options=list(QUALITY_STRICT_PRESETS.keys()),
                            index=list(QUALITY_STRICT_PRESETS.keys()).index(STRICT_QUARTERLY_PROTOTYPE_DEFAULT_PRESET),
                            key="compare_qsqp_preset",
                        )
                        qsqp_compare_contract_label = st.selectbox(
                            "Strict Quarterly Quality Universe Contract",
                            options=list(STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.keys()),
                            index=0,
                            key="compare_qsqp_universe_contract",
                            help="Static은 현재 managed preset을 고정해서 사용합니다. Dynamic PIT는 Phase 10 first pass로, quarterly strict에서도 각 리밸런싱 날짜 기준 membership를 다시 계산합니다.",
                        )
                        qsqp_compare_universe_contract = STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS[qsqp_compare_contract_label]
                        qsqp_dynamic_candidate_tickers, qsqp_dynamic_target_size = _render_strict_dynamic_universe_contract_note(
                            universe_contract=qsqp_compare_universe_contract,
                            tickers=QUALITY_STRICT_PRESETS[qsqp_compare_preset],
                            preset_name=qsqp_compare_preset,
                            statement_freq="quarterly",
                        )
                        _render_ticker_preview(QUALITY_STRICT_PRESETS[qsqp_compare_preset], preview_count=8, tail_count=3)
                        _render_historical_universe_caption()
                        compare_strategy_overrides["Quality Snapshot (Strict Quarterly Prototype)"] = {
                            "preset_name": qsqp_compare_preset,
                            "tickers": QUALITY_STRICT_PRESETS[qsqp_compare_preset],
                            "universe_mode": "preset",
                            "universe_contract": qsqp_compare_universe_contract,
                            "dynamic_candidate_tickers": qsqp_dynamic_candidate_tickers,
                            "dynamic_target_size": qsqp_dynamic_target_size,
                            "top_n": int(
                                st.number_input(
                                    "Strict Quarterly Quality Top N",
                                    min_value=1,
                                    max_value=20,
                                    value=2,
                                    step=1,
                                    key="compare_qsqp_top_n",
                                )
                            ),
                            "rebalance_interval": int(
                                st.number_input(
                                    "Strict Quarterly Quality Rebalance Interval",
                                    min_value=1,
                                    max_value=12,
                                    value=1,
                                    step=1,
                                    key="compare_qsqp_rebalance_interval",
                                )
                            ),
                            "quality_factors": st.multiselect(
                                "Strict Quarterly Quality Factors",
                                options=QUALITY_STRICT_FACTOR_OPTIONS,
                                default=QUALITY_STRICT_DEFAULT_FACTORS,
                                key="compare_qsqp_factors",
                            ),
                        }
                        trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
                        with trend_title_col:
                            st.markdown("##### Strict Quarterly Quality Trend Filter")
                        with trend_help_col:
                            _render_trend_filter_help_popover()
                        compare_strategy_overrides["Quality Snapshot (Strict Quarterly Prototype)"]["trend_filter_enabled"] = st.checkbox(
                            "Enable",
                            value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                            key="compare_qsqp_trend_filter_enabled",
                        )
                        compare_strategy_overrides["Quality Snapshot (Strict Quarterly Prototype)"]["trend_filter_window"] = int(
                            st.number_input(
                                "Strict Quarterly Quality Trend Filter Window",
                                min_value=20,
                                max_value=400,
                                value=STRICT_TREND_FILTER_DEFAULT_WINDOW,
                                step=10,
                                key="compare_qsqp_trend_filter_window",
                            )
                        )
                        (
                            compare_strategy_overrides["Quality Snapshot (Strict Quarterly Prototype)"]["market_regime_enabled"],
                            compare_strategy_overrides["Quality Snapshot (Strict Quarterly Prototype)"]["market_regime_window"],
                            compare_strategy_overrides["Quality Snapshot (Strict Quarterly Prototype)"]["market_regime_benchmark"],
                        ) = _render_market_regime_overlay_inputs(
                            key_prefix="compare_qsqp",
                            label_prefix="Strict Quarterly Quality ",
                        )

                if value_compare_strategy_name == "Value Snapshot (Strict Annual)":
                    with st.expander("Value Snapshot (Strict Annual)", expanded=False):
                        st.caption("Compare mode keeps the strict annual value default lighter with `US Statement Coverage 100` for responsiveness.")
                        vss_compare_preset = st.selectbox(
                            "Strict Annual Value Preset",
                            options=list(VALUE_STRICT_PRESETS.keys()),
                            index=list(VALUE_STRICT_PRESETS.keys()).index(STRICT_ANNUAL_COMPARE_DEFAULT_PRESET),
                            key="compare_vss_preset",
                        )
                        vss_compare_contract_label = st.selectbox(
                            "Strict Annual Value Universe Contract",
                            options=list(STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.keys()),
                            index=0,
                            key="compare_vss_universe_contract",
                            help="Static은 현재 managed preset을 고정해서 사용합니다. Dynamic PIT는 Phase 10 first pass로, annual strict compare에서도 각 리밸런싱 날짜 기준 membership를 다시 계산합니다.",
                        )
                        vss_compare_universe_contract = STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS[vss_compare_contract_label]
                        vss_dynamic_candidate_tickers, vss_dynamic_target_size = _render_strict_annual_universe_contract_note(
                            universe_contract=vss_compare_universe_contract,
                            tickers=VALUE_STRICT_PRESETS[vss_compare_preset],
                            preset_name=vss_compare_preset,
                        )
                        _render_ticker_preview(VALUE_STRICT_PRESETS[vss_compare_preset], preview_count=8, tail_count=3)
                        _render_historical_universe_caption()
                        compare_strategy_overrides["Value Snapshot (Strict Annual)"] = {
                            "preset_name": vss_compare_preset,
                            "tickers": VALUE_STRICT_PRESETS[vss_compare_preset],
                            "universe_mode": "preset",
                            "universe_contract": vss_compare_universe_contract,
                            "dynamic_candidate_tickers": vss_dynamic_candidate_tickers,
                            "dynamic_target_size": vss_dynamic_target_size,
                            "top_n": int(
                                st.number_input(
                                    "Strict Annual Value Top N",
                                    min_value=1,
                                    max_value=50,
                                    value=10,
                                    step=1,
                                    key="compare_vss_top_n",
                                )
                            ),
                            "rebalance_interval": int(
                                st.number_input(
                                    "Strict Annual Value Rebalance Interval",
                                    min_value=1,
                                    max_value=12,
                                    value=1,
                                    step=1,
                                    key="compare_vss_rebalance_interval",
                                )
                            ),
                            "value_factors": st.multiselect(
                                "Strict Annual Value Factors",
                                options=VALUE_STRICT_FACTOR_OPTIONS,
                                default=VALUE_STRICT_DEFAULT_FACTORS,
                                key="compare_vss_factors",
                            ),
                        }
                        trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
                        with trend_title_col:
                            st.markdown("##### Strict Annual Value Trend Filter")
                        with trend_help_col:
                            _render_trend_filter_help_popover()
                        compare_strategy_overrides["Value Snapshot (Strict Annual)"]["trend_filter_enabled"] = st.checkbox(
                            "Enable",
                            value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                            key="compare_vss_trend_filter_enabled",
                        )
                        compare_strategy_overrides["Value Snapshot (Strict Annual)"]["trend_filter_window"] = int(
                            st.number_input(
                                "Strict Annual Value Trend Filter Window",
                                min_value=20,
                                max_value=400,
                                value=STRICT_TREND_FILTER_DEFAULT_WINDOW,
                                step=10,
                                key="compare_vss_trend_filter_window",
                            )
                        )
                        (
                            compare_strategy_overrides["Value Snapshot (Strict Annual)"]["market_regime_enabled"],
                            compare_strategy_overrides["Value Snapshot (Strict Annual)"]["market_regime_window"],
                            compare_strategy_overrides["Value Snapshot (Strict Annual)"]["market_regime_benchmark"],
                        ) = _render_market_regime_overlay_inputs(
                            key_prefix="compare_vss",
                            label_prefix="Strict Annual Value ",
                        )
                        (
                            benchmark_contract,
                            min_price_filter,
                            min_history_months_filter,
                            min_avg_dollar_volume_20d_m_filter,
                            transaction_cost_bps,
                            benchmark_ticker,
                            promotion_min_benchmark_coverage,
                            promotion_min_net_cagr_spread,
                            promotion_min_liquidity_clean_coverage,
                            promotion_max_underperformance_share,
                            promotion_min_worst_rolling_excess_return,
                            promotion_max_strategy_drawdown,
                            promotion_max_drawdown_gap_vs_benchmark,
                        ) = _render_strict_annual_real_money_inputs(
                            key_prefix="compare_vss",
                        )
                        compare_strategy_overrides["Value Snapshot (Strict Annual)"]["min_price_filter"] = float(min_price_filter)
                        compare_strategy_overrides["Value Snapshot (Strict Annual)"]["min_history_months_filter"] = int(min_history_months_filter)
                        compare_strategy_overrides["Value Snapshot (Strict Annual)"]["min_avg_dollar_volume_20d_m_filter"] = float(min_avg_dollar_volume_20d_m_filter)
                        compare_strategy_overrides["Value Snapshot (Strict Annual)"]["transaction_cost_bps"] = float(transaction_cost_bps)
                        compare_strategy_overrides["Value Snapshot (Strict Annual)"]["benchmark_contract"] = benchmark_contract
                        compare_strategy_overrides["Value Snapshot (Strict Annual)"]["benchmark_ticker"] = benchmark_ticker
                        compare_strategy_overrides["Value Snapshot (Strict Annual)"]["promotion_min_benchmark_coverage"] = float(promotion_min_benchmark_coverage)
                        compare_strategy_overrides["Value Snapshot (Strict Annual)"]["promotion_min_net_cagr_spread"] = float(promotion_min_net_cagr_spread)
                        compare_strategy_overrides["Value Snapshot (Strict Annual)"]["promotion_min_liquidity_clean_coverage"] = float(promotion_min_liquidity_clean_coverage)
                        compare_strategy_overrides["Value Snapshot (Strict Annual)"]["promotion_max_underperformance_share"] = float(promotion_max_underperformance_share)
                        compare_strategy_overrides["Value Snapshot (Strict Annual)"]["promotion_min_worst_rolling_excess_return"] = float(promotion_min_worst_rolling_excess_return)
                        compare_strategy_overrides["Value Snapshot (Strict Annual)"]["promotion_max_strategy_drawdown"] = float(promotion_max_strategy_drawdown)
                        compare_strategy_overrides["Value Snapshot (Strict Annual)"]["promotion_max_drawdown_gap_vs_benchmark"] = float(promotion_max_drawdown_gap_vs_benchmark)
                        (
                            compare_strategy_overrides["Value Snapshot (Strict Annual)"]["underperformance_guardrail_enabled"],
                            compare_strategy_overrides["Value Snapshot (Strict Annual)"]["underperformance_guardrail_window_months"],
                            compare_strategy_overrides["Value Snapshot (Strict Annual)"]["underperformance_guardrail_threshold"],
                        ) = _render_underperformance_guardrail_inputs(
                            key_prefix="compare_vss",
                            label_prefix="Strict Annual Value ",
                        )
                        (
                            compare_strategy_overrides["Value Snapshot (Strict Annual)"]["drawdown_guardrail_enabled"],
                            compare_strategy_overrides["Value Snapshot (Strict Annual)"]["drawdown_guardrail_window_months"],
                            compare_strategy_overrides["Value Snapshot (Strict Annual)"]["drawdown_guardrail_strategy_threshold"],
                            compare_strategy_overrides["Value Snapshot (Strict Annual)"]["drawdown_guardrail_gap_threshold"],
                        ) = _render_drawdown_guardrail_inputs(
                            key_prefix="compare_vss",
                            label_prefix="Strict Annual Value ",
                        )

                if value_compare_strategy_name == "Value Snapshot (Strict Quarterly Prototype)":
                    with st.expander("Value Snapshot (Strict Quarterly Prototype)", expanded=False):
                        st.caption("Research-only compare path. Default preset stays at `US Statement Coverage 100` while quarterly value history is being validated.")
                        vsqp_compare_preset = st.selectbox(
                            "Strict Quarterly Value Preset",
                            options=list(VALUE_STRICT_PRESETS.keys()),
                            index=list(VALUE_STRICT_PRESETS.keys()).index(STRICT_QUARTERLY_PROTOTYPE_DEFAULT_PRESET),
                            key="compare_vsqp_preset",
                        )
                        vsqp_compare_contract_label = st.selectbox(
                            "Strict Quarterly Value Universe Contract",
                            options=list(STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.keys()),
                            index=0,
                            key="compare_vsqp_universe_contract",
                            help="Static은 현재 managed preset을 고정해서 사용합니다. Dynamic PIT는 Phase 10 first pass로, quarterly strict에서도 각 리밸런싱 날짜 기준 membership를 다시 계산합니다.",
                        )
                        vsqp_compare_universe_contract = STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS[vsqp_compare_contract_label]
                        vsqp_dynamic_candidate_tickers, vsqp_dynamic_target_size = _render_strict_dynamic_universe_contract_note(
                            universe_contract=vsqp_compare_universe_contract,
                            tickers=VALUE_STRICT_PRESETS[vsqp_compare_preset],
                            preset_name=vsqp_compare_preset,
                            statement_freq="quarterly",
                        )
                        _render_ticker_preview(VALUE_STRICT_PRESETS[vsqp_compare_preset], preview_count=8, tail_count=3)
                        _render_historical_universe_caption()
                        compare_strategy_overrides["Value Snapshot (Strict Quarterly Prototype)"] = {
                            "preset_name": vsqp_compare_preset,
                            "tickers": VALUE_STRICT_PRESETS[vsqp_compare_preset],
                            "universe_mode": "preset",
                            "universe_contract": vsqp_compare_universe_contract,
                            "dynamic_candidate_tickers": vsqp_dynamic_candidate_tickers,
                            "dynamic_target_size": vsqp_dynamic_target_size,
                            "top_n": int(
                                st.number_input(
                                    "Strict Quarterly Value Top N",
                                    min_value=1,
                                    max_value=50,
                                    value=10,
                                    step=1,
                                    key="compare_vsqp_top_n",
                                )
                            ),
                            "rebalance_interval": int(
                                st.number_input(
                                    "Strict Quarterly Value Rebalance Interval",
                                    min_value=1,
                                    max_value=12,
                                    value=1,
                                    step=1,
                                    key="compare_vsqp_rebalance_interval",
                                )
                            ),
                            "value_factors": st.multiselect(
                                "Strict Quarterly Value Factors",
                                options=VALUE_STRICT_FACTOR_OPTIONS,
                                default=VALUE_STRICT_DEFAULT_FACTORS,
                                key="compare_vsqp_factors",
                            ),
                        }
                        trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
                        with trend_title_col:
                            st.markdown("##### Strict Quarterly Value Trend Filter")
                        with trend_help_col:
                            _render_trend_filter_help_popover()
                        compare_strategy_overrides["Value Snapshot (Strict Quarterly Prototype)"]["trend_filter_enabled"] = st.checkbox(
                            "Enable",
                            value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                            key="compare_vsqp_trend_filter_enabled",
                        )
                        compare_strategy_overrides["Value Snapshot (Strict Quarterly Prototype)"]["trend_filter_window"] = int(
                            st.number_input(
                                "Strict Quarterly Value Trend Filter Window",
                                min_value=20,
                                max_value=400,
                                value=STRICT_TREND_FILTER_DEFAULT_WINDOW,
                                step=10,
                                key="compare_vsqp_trend_filter_window",
                            )
                        )
                        (
                            compare_strategy_overrides["Value Snapshot (Strict Quarterly Prototype)"]["market_regime_enabled"],
                            compare_strategy_overrides["Value Snapshot (Strict Quarterly Prototype)"]["market_regime_window"],
                            compare_strategy_overrides["Value Snapshot (Strict Quarterly Prototype)"]["market_regime_benchmark"],
                        ) = _render_market_regime_overlay_inputs(
                            key_prefix="compare_vsqp",
                            label_prefix="Strict Quarterly Value ",
                        )

                if quality_value_compare_strategy_name == "Quality + Value Snapshot (Strict Annual)":
                    with st.expander("Quality + Value Snapshot (Strict Annual)", expanded=False):
                        st.caption("Compare mode keeps the strict annual multi-factor default lighter with `US Statement Coverage 100` so multi-strategy runs stay responsive.")
                        qvss_compare_preset = st.selectbox(
                            "Strict Annual Multi-Factor Preset",
                            options=list(QUALITY_STRICT_PRESETS.keys()),
                            index=list(QUALITY_STRICT_PRESETS.keys()).index(STRICT_ANNUAL_COMPARE_DEFAULT_PRESET),
                            key="compare_qvss_preset",
                        )
                        qvss_compare_contract_label = st.selectbox(
                            "Strict Annual Multi-Factor Universe Contract",
                            options=list(STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.keys()),
                            index=0,
                            key="compare_qvss_universe_contract",
                            help="Static은 현재 managed preset을 고정해서 사용합니다. Dynamic PIT는 Phase 10 first pass로, annual strict compare에서도 각 리밸런싱 날짜 기준 membership를 다시 계산합니다.",
                        )
                        qvss_compare_universe_contract = STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS[qvss_compare_contract_label]
                        qvss_dynamic_candidate_tickers, qvss_dynamic_target_size = _render_strict_annual_universe_contract_note(
                            universe_contract=qvss_compare_universe_contract,
                            tickers=QUALITY_STRICT_PRESETS[qvss_compare_preset],
                            preset_name=qvss_compare_preset,
                        )
                        _render_ticker_preview(QUALITY_STRICT_PRESETS[qvss_compare_preset], preview_count=8, tail_count=3)
                        _render_historical_universe_caption()
                        compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"] = {
                            "preset_name": qvss_compare_preset,
                            "tickers": QUALITY_STRICT_PRESETS[qvss_compare_preset],
                            "universe_mode": "preset",
                            "universe_contract": qvss_compare_universe_contract,
                            "dynamic_candidate_tickers": qvss_dynamic_candidate_tickers,
                            "dynamic_target_size": qvss_dynamic_target_size,
                            "top_n": int(
                                st.number_input(
                                    "Strict Annual Multi-Factor Top N",
                                    min_value=1,
                                    max_value=30,
                                    value=10,
                                    step=1,
                                    key="compare_qvss_top_n",
                                )
                            ),
                            "rebalance_interval": int(
                                st.number_input(
                                    "Strict Annual Multi-Factor Rebalance Interval",
                                    min_value=1,
                                    max_value=12,
                                    value=1,
                                    step=1,
                                    key="compare_qvss_rebalance_interval",
                                )
                            ),
                            "quality_factors": st.multiselect(
                                "Strict Annual Multi-Factor Quality Factors",
                                options=QUALITY_STRICT_FACTOR_OPTIONS,
                                default=QUALITY_STRICT_DEFAULT_FACTORS,
                                key="compare_qvss_quality_factors",
                            ),
                            "value_factors": st.multiselect(
                                "Strict Annual Multi-Factor Value Factors",
                                options=VALUE_STRICT_FACTOR_OPTIONS,
                                default=VALUE_STRICT_DEFAULT_FACTORS,
                                key="compare_qvss_value_factors",
                            ),
                        }
                        trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
                        with trend_title_col:
                            st.markdown("##### Strict Annual Multi-Factor Trend Filter")
                        with trend_help_col:
                            _render_trend_filter_help_popover()
                        compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["trend_filter_enabled"] = st.checkbox(
                            "Enable",
                            value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                            key="compare_qvss_trend_filter_enabled",
                        )
                        compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["trend_filter_window"] = int(
                            st.number_input(
                                "Strict Annual Multi-Factor Trend Filter Window",
                                min_value=20,
                                max_value=400,
                                value=STRICT_TREND_FILTER_DEFAULT_WINDOW,
                                step=10,
                                key="compare_qvss_trend_filter_window",
                            )
                        )
                        (
                            compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["market_regime_enabled"],
                            compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["market_regime_window"],
                            compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["market_regime_benchmark"],
                        ) = _render_market_regime_overlay_inputs(
                            key_prefix="compare_qvss",
                            label_prefix="Strict Annual Multi-Factor ",
                        )
                        (
                            benchmark_contract,
                            min_price_filter,
                            min_history_months_filter,
                            min_avg_dollar_volume_20d_m_filter,
                            transaction_cost_bps,
                            benchmark_ticker,
                            promotion_min_benchmark_coverage,
                            promotion_min_net_cagr_spread,
                            promotion_min_liquidity_clean_coverage,
                            promotion_max_underperformance_share,
                            promotion_min_worst_rolling_excess_return,
                            promotion_max_strategy_drawdown,
                            promotion_max_drawdown_gap_vs_benchmark,
                        ) = _render_strict_annual_real_money_inputs(
                            key_prefix="compare_qvss",
                        )
                        compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["min_price_filter"] = float(min_price_filter)
                        compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["min_history_months_filter"] = int(min_history_months_filter)
                        compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["min_avg_dollar_volume_20d_m_filter"] = float(min_avg_dollar_volume_20d_m_filter)
                        compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["transaction_cost_bps"] = float(transaction_cost_bps)
                        compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["benchmark_contract"] = benchmark_contract
                        compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["benchmark_ticker"] = benchmark_ticker
                        compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["promotion_min_benchmark_coverage"] = float(promotion_min_benchmark_coverage)
                        compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["promotion_min_net_cagr_spread"] = float(promotion_min_net_cagr_spread)
                        compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["promotion_min_liquidity_clean_coverage"] = float(promotion_min_liquidity_clean_coverage)
                        compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["promotion_max_underperformance_share"] = float(promotion_max_underperformance_share)
                        compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["promotion_min_worst_rolling_excess_return"] = float(promotion_min_worst_rolling_excess_return)
                        compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["promotion_max_strategy_drawdown"] = float(promotion_max_strategy_drawdown)
                        compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["promotion_max_drawdown_gap_vs_benchmark"] = float(promotion_max_drawdown_gap_vs_benchmark)
                        (
                            compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["underperformance_guardrail_enabled"],
                            compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["underperformance_guardrail_window_months"],
                            compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["underperformance_guardrail_threshold"],
                        ) = _render_underperformance_guardrail_inputs(
                            key_prefix="compare_qvss",
                            label_prefix="Strict Annual Multi-Factor ",
                        )
                        (
                            compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["drawdown_guardrail_enabled"],
                            compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["drawdown_guardrail_window_months"],
                            compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["drawdown_guardrail_strategy_threshold"],
                            compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["drawdown_guardrail_gap_threshold"],
                        ) = _render_drawdown_guardrail_inputs(
                            key_prefix="compare_qvss",
                            label_prefix="Strict Annual Multi-Factor ",
                        )

                if quality_value_compare_strategy_name == "Quality + Value Snapshot (Strict Quarterly Prototype)":
                    with st.expander("Quality + Value Snapshot (Strict Quarterly Prototype)", expanded=False):
                        st.caption("Research-only compare path. Default preset stays at `US Statement Coverage 100` while quarterly blended history is being validated.")
                        qvqp_compare_preset = st.selectbox(
                            "Strict Quarterly Multi-Factor Preset",
                            options=list(QUALITY_STRICT_PRESETS.keys()),
                            index=list(QUALITY_STRICT_PRESETS.keys()).index(STRICT_QUARTERLY_PROTOTYPE_DEFAULT_PRESET),
                            key="compare_qvqp_preset",
                        )
                        qvqp_compare_contract_label = st.selectbox(
                            "Strict Quarterly Multi-Factor Universe Contract",
                            options=list(STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.keys()),
                            index=0,
                            key="compare_qvqp_universe_contract",
                            help="Static은 현재 managed preset을 고정해서 사용합니다. Dynamic PIT는 Phase 10 first pass로, quarterly strict에서도 각 리밸런싱 날짜 기준 membership를 다시 계산합니다.",
                        )
                        qvqp_compare_universe_contract = STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS[qvqp_compare_contract_label]
                        qvqp_dynamic_candidate_tickers, qvqp_dynamic_target_size = _render_strict_dynamic_universe_contract_note(
                            universe_contract=qvqp_compare_universe_contract,
                            tickers=QUALITY_STRICT_PRESETS[qvqp_compare_preset],
                            preset_name=qvqp_compare_preset,
                            statement_freq="quarterly",
                        )
                        _render_ticker_preview(QUALITY_STRICT_PRESETS[qvqp_compare_preset], preview_count=8, tail_count=3)
                        _render_historical_universe_caption()
                        compare_strategy_overrides["Quality + Value Snapshot (Strict Quarterly Prototype)"] = {
                            "preset_name": qvqp_compare_preset,
                            "tickers": QUALITY_STRICT_PRESETS[qvqp_compare_preset],
                            "universe_mode": "preset",
                            "universe_contract": qvqp_compare_universe_contract,
                            "dynamic_candidate_tickers": qvqp_dynamic_candidate_tickers,
                            "dynamic_target_size": qvqp_dynamic_target_size,
                            "top_n": int(
                                st.number_input(
                                    "Strict Quarterly Multi-Factor Top N",
                                    min_value=1,
                                    max_value=30,
                                    value=10,
                                    step=1,
                                    key="compare_qvqp_top_n",
                                )
                            ),
                            "rebalance_interval": int(
                                st.number_input(
                                    "Strict Quarterly Multi-Factor Rebalance Interval",
                                    min_value=1,
                                    max_value=12,
                                    value=1,
                                    step=1,
                                    key="compare_qvqp_rebalance_interval",
                                )
                            ),
                            "quality_factors": st.multiselect(
                                "Strict Quarterly Multi-Factor Quality Factors",
                                options=QUALITY_STRICT_FACTOR_OPTIONS,
                                default=QUALITY_STRICT_DEFAULT_FACTORS,
                                key="compare_qvqp_quality_factors",
                            ),
                            "value_factors": st.multiselect(
                                "Strict Quarterly Multi-Factor Value Factors",
                                options=VALUE_STRICT_FACTOR_OPTIONS,
                                default=VALUE_STRICT_DEFAULT_FACTORS,
                                key="compare_qvqp_value_factors",
                            ),
                        }
                        trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
                        with trend_title_col:
                            st.markdown("##### Strict Quarterly Multi-Factor Trend Filter")
                        with trend_help_col:
                            _render_trend_filter_help_popover()
                        compare_strategy_overrides["Quality + Value Snapshot (Strict Quarterly Prototype)"]["trend_filter_enabled"] = st.checkbox(
                            "Enable",
                            value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                            key="compare_qvqp_trend_filter_enabled",
                        )
                        compare_strategy_overrides["Quality + Value Snapshot (Strict Quarterly Prototype)"]["trend_filter_window"] = int(
                            st.number_input(
                                "Strict Quarterly Multi-Factor Trend Filter Window",
                                min_value=20,
                                max_value=400,
                                value=STRICT_TREND_FILTER_DEFAULT_WINDOW,
                                step=10,
                                key="compare_qvqp_trend_filter_window",
                            )
                        )
                        (
                            compare_strategy_overrides["Quality + Value Snapshot (Strict Quarterly Prototype)"]["market_regime_enabled"],
                            compare_strategy_overrides["Quality + Value Snapshot (Strict Quarterly Prototype)"]["market_regime_window"],
                            compare_strategy_overrides["Quality + Value Snapshot (Strict Quarterly Prototype)"]["market_regime_benchmark"],
                        ) = _render_market_regime_overlay_inputs(
                            key_prefix="compare_qvqp",
                            label_prefix="Strict Quarterly Multi-Factor ",
                        )

            compare_submitted = st.form_submit_button("Run Strategy Comparison", use_container_width=True)

        selected_strategy_execution_names: list[str] = []
        for strategy_name in selected_strategies:
            if strategy_name == "Quality":
                if quality_compare_strategy_name:
                    selected_strategy_execution_names.append(quality_compare_strategy_name)
            elif strategy_name == "Value":
                if value_compare_strategy_name:
                    selected_strategy_execution_names.append(value_compare_strategy_name)
            elif strategy_name == "Quality + Value":
                if quality_value_compare_strategy_name:
                    selected_strategy_execution_names.append(quality_value_compare_strategy_name)
            else:
                selected_strategy_execution_names.append(strategy_name)

        if compare_submitted:
            if not selected_strategies:
                st.session_state.backtest_compare_bundles = None
                st.session_state.backtest_compare_error_kind = "input"
                st.session_state.backtest_compare_error = "Select at least one strategy to compare."
            elif compare_start > compare_end:
                st.session_state.backtest_compare_bundles = None
                st.session_state.backtest_compare_error_kind = "input"
                st.session_state.backtest_compare_error = "Start Date must be earlier than or equal to End Date."
            elif (
                "Equal Weight" in selected_strategies
                and not (compare_strategy_overrides.get("Equal Weight", {}).get("tickers") or [])
            ):
                st.session_state.backtest_compare_bundles = None
                st.session_state.backtest_compare_error_kind = "input"
                st.session_state.backtest_compare_error = "Equal Weight universe must contain at least one ticker."
            elif (
                "GTAA" in selected_strategies
                and not (compare_strategy_overrides.get("GTAA", {}).get("score_lookback_months") or [])
            ):
                st.session_state.backtest_compare_bundles = None
                st.session_state.backtest_compare_error_kind = "input"
                st.session_state.backtest_compare_error = "GTAA Score Horizons must contain at least one lookback window."
            elif (
                "GTAA" in selected_strategies
                and not (compare_strategy_overrides.get("GTAA", {}).get("tickers") or [])
            ):
                st.session_state.backtest_compare_bundles = None
                st.session_state.backtest_compare_error_kind = "input"
                st.session_state.backtest_compare_error = "GTAA universe must contain at least one ticker."
            else:
                try:
                    bundles = []
                    with st.spinner("Running multi-strategy comparison from DB..."):
                        for strategy_name in selected_strategy_execution_names:
                            bundles.append(
                                _run_compare_strategy(
                                    strategy_name,
                                    start=compare_start.isoformat(),
                                    end=compare_end.isoformat(),
                                    timeframe=compare_timeframe,
                                    option=compare_option,
                                    overrides=compare_strategy_overrides.get(strategy_name),
                                )
                            )
                    st.session_state.backtest_compare_bundles = bundles
                    st.session_state.backtest_compare_error = None
                    st.session_state.backtest_compare_error_kind = None
                    append_backtest_run_history(
                        bundle={
                            "summary_df": pd.DataFrame(),
                            "meta": {
                                "strategy_key": "strategy_comparison",
                                "execution_mode": "db",
                                "data_mode": "db_backed_compare",
                                "tickers": selected_strategy_execution_names,
                                "start": compare_start.isoformat(),
                                "end": compare_end.isoformat(),
                                "timeframe": compare_timeframe,
                                "option": compare_option,
                                "universe_mode": "strategy_compare",
                                "preset_name": "compare_mode",
                            },
                        },
                        run_kind="strategy_compare",
                        context={
                            "selected_strategies": selected_strategy_execution_names,
                            "selected_strategy_categories": selected_strategies,
                            "strategy_overrides": compare_strategy_overrides,
                            "strategy_summaries": [
                                row
                                for bundle in bundles
                                for row in json.loads(bundle["summary_df"].to_json(orient="records", date_format="iso"))
                            ],
                        },
                    )
                    st.success("Strategy comparison completed.")
                except BacktestInputError as exc:
                    st.session_state.backtest_compare_bundles = None
                    st.session_state.backtest_compare_error_kind = "input"
                    st.session_state.backtest_compare_error = f"Comparison input issue: {exc}"
                except BacktestDataError as exc:
                    st.session_state.backtest_compare_bundles = None
                    st.session_state.backtest_compare_error_kind = "data"
                    st.session_state.backtest_compare_error = f"Comparison data issue: {exc}"
                except Exception as exc:
                    st.session_state.backtest_compare_bundles = None
                    st.session_state.backtest_compare_error_kind = "system"
                    st.session_state.backtest_compare_error = f"Comparison execution failed: {exc}"

        st.divider()
        _render_compare_results()
        st.divider()
        _render_weighted_portfolio_builder()
        st.divider()
        _render_saved_portfolio_workspace()

    else:
        st.markdown("### Backtest History")
        st.caption("Single-strategy runs and strategy-comparison runs share the same persistent history and drilldown surface.")
        _render_persistent_backtest_history()
