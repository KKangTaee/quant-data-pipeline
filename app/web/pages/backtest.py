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
    append_backtest_run_history,
    build_backtest_result_bundle,
    inspect_strict_annual_price_freshness,
    load_backtest_run_history,
    run_dual_momentum_backtest_from_db,
    run_equal_weight_backtest_from_db,
    run_gtaa_backtest_from_db,
    run_quality_snapshot_backtest_from_db,
    run_quality_snapshot_strict_annual_backtest_from_db,
    run_quality_snapshot_strict_quarterly_prototype_backtest_from_db,
    run_quality_value_snapshot_strict_annual_backtest_from_db,
    run_quality_value_snapshot_strict_quarterly_prototype_backtest_from_db,
    run_risk_parity_trend_backtest_from_db,
    run_value_snapshot_strict_annual_backtest_from_db,
    run_value_snapshot_strict_quarterly_prototype_backtest_from_db,
)
from app.web.runtime.backtest import BacktestDataError, BacktestInputError
from finance.data.asset_profile import load_top_symbols_from_asset_profile
from finance.loaders import load_statement_coverage_summary, load_statement_shadow_coverage_summary
from finance.performance import make_monthly_weighted_portfolio


EQUAL_WEIGHT_PRESETS = {
    "Dividend ETFs": ["VIG", "SCHD", "DGRO", "GLD"],
    "Core ETFs": ["SPY", "QQQ", "TLT", "GLD"],
    "Big Tech": ["AAPL", "MSFT", "GOOG"],
}

GTAA_PRESETS = {
    "GTAA Universe": ["SPY", "IWD", "IWM", "IWN", "MTUM", "EFA", "TLT", "IEF", "LQD", "DBC", "VNQ", "GLD"],
}

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

COMPARE_STRATEGY_OPTIONS = [
    "Equal Weight",
    "GTAA",
    "Risk Parity Trend",
    "Dual Momentum",
    "Quality Snapshot",
    "Quality Snapshot (Strict Annual)",
    "Quality Snapshot (Strict Quarterly Prototype)",
    "Value Snapshot (Strict Annual)",
    "Value Snapshot (Strict Quarterly Prototype)",
    "Quality + Value Snapshot (Strict Annual)",
    "Quality + Value Snapshot (Strict Quarterly Prototype)",
]

SINGLE_STRATEGY_OPTIONS = COMPARE_STRATEGY_OPTIONS


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
                "Diagnosis": diagnosis,
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

    st.session_state.ingestion_prefill_request = {
        "target": target,
        "symbols_csv": symbols_csv,
        "widget_values": widget_values,
        "notice": notice,
    }


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
    if "backtest_prefill_strategy_choice" not in st.session_state:
        st.session_state.backtest_prefill_strategy_choice = None
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
            "`no_raw_statement_coverage`는 추가 statement 수집이 필요한 심볼이고, "
            "`raw_statement_present_but_shadow_missing`는 raw는 이미 있지만 shadow가 비어 있는 심볼입니다. "
            "현재는 `Extended Statement Refresh`가 shadow rebuild까지 같이 수행하므로, 먼저 그 경로를 다시 실행해보고 "
            "그래도 남으면 coverage hardening을 점검하는 것이 좋습니다."
        )
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

    st.markdown("### Latest Backtest Run")
    st.caption("First-pass result view. Summary, equity curve, preview table, and execution meta are separated so the screen reads more like a product surface.")
    for warning in meta.get("warnings") or []:
        st.warning(warning)

    st.markdown(f"#### {bundle['strategy_name']}")
    _render_summary_metrics(summary_df)

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

    tab_labels = ["Summary", "Equity Curve", "Balance Extremes", "Period Extremes"]
    if has_selection_history:
        tab_labels.append("Selection History")
    tab_labels.extend(["Result Table", "Meta"])
    tabs = st.tabs(tab_labels)
    tab_iter = iter(tabs)
    summary_tab = next(tab_iter)
    curve_tab = next(tab_iter)
    balance_tab = next(tab_iter)
    periods_tab = next(tab_iter)
    selection_tab = next(tab_iter) if has_selection_history else None
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
        st.caption("High / Low / End plus Best / Worst period markers are shown so the equity curve is easier to interpret than a plain line chart.")

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

    with table_tab:
        st.dataframe(result_df, use_container_width=True)

    with meta_tab:
        left, right = st.columns([1.1, 1.2], gap="large")
        with left:
            st.markdown("##### Execution Context")
            st.markdown(f"- `Mode`: `{meta['execution_mode']}`")
            st.markdown(f"- `Data`: `{meta['data_mode']}`")
            st.markdown(f"- `Universe`: `{meta['universe_mode']}`")
            st.markdown(f"- `Tickers`: `{', '.join(meta['tickers'])}`")
            st.markdown(f"- `Period`: `{meta['start']}` -> `{meta['end']}`")
            if meta.get("ui_elapsed_seconds") is not None:
                st.markdown(f"- `Elapsed`: `{meta['ui_elapsed_seconds']:.3f}s`")
            if meta.get("top") is not None:
                st.markdown(f"- `Top`: `{meta['top']}`")
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
            "tickers": ["SPY", "IWD", "IWM", "IWN", "MTUM", "EFA", "TLT", "IEF", "LQD", "DBC", "VNQ", "GLD"],
            "preset_name": "GTAA Universe",
            "runner": run_gtaa_backtest_from_db,
            "extra": {"top": 3},
        }
    if strategy_name == "Risk Parity Trend":
        return {
            "tickers": ["SPY", "TLT", "GLD", "IEF", "LQD"],
            "preset_name": "Risk Parity Universe",
            "runner": run_risk_parity_trend_backtest_from_db,
            "extra": {},
        }
    if strategy_name == "Dual Momentum":
        return {
            "tickers": ["QQQ", "SPY", "IWM", "SOXX", "BIL"],
            "preset_name": "Dual Momentum Universe",
            "runner": run_dual_momentum_backtest_from_db,
            "extra": {},
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
    if strategy_name in {
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


def _build_compare_highlight_rows(bundles: list[dict]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for bundle in bundles:
        chart_df = bundle["chart_df"].copy().sort_values("Date")
        result_df = bundle["result_df"].copy().sort_values("Date")
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


def _render_weighted_portfolio_builder() -> None:
    bundles = st.session_state.backtest_compare_bundles
    if not bundles or len(bundles) < 2:
        return

    strategy_names = [bundle["strategy_name"] for bundle in bundles]
    default_weight = round(100 / len(strategy_names), 2)

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
        normalized_weights = [weight / total_weight for weight in weights]
        combined_result = make_monthly_weighted_portfolio(
            dfs=[bundle["result_df"] for bundle in bundles],
            ratios=weights,
            names=strategy_names,
            date_policy=date_policy,
        )
        weighted_bundle = build_backtest_result_bundle(
            combined_result,
            strategy_name="Weighted Portfolio",
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
        weighted_bundle["component_weights"] = normalized_weights
        weighted_bundle["component_strategy_names"] = strategy_names
        weighted_bundle["date_policy"] = date_policy
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


def _render_weighted_portfolio_result(bundle: dict) -> None:
    if st.session_state.backtest_weighted_error:
        st.error(st.session_state.backtest_weighted_error)

    st.markdown("#### Weighted Portfolio Result")
    _render_summary_metrics(bundle["summary_df"])

    result_df = bundle["result_df"]
    chart_df = bundle["chart_df"]
    contribution_amount_df = bundle.get("component_contribution_amount_df")
    contribution_share_df = bundle.get("component_contribution_share_df")
    component_weights = bundle.get("component_weights") or []
    component_strategy_names = bundle.get("component_strategy_names") or []

    summary_tab, curve_tab, contribution_tab, balance_tab, periods_tab, table_tab = st.tabs(
        ["Summary", "Equity Curve", "Contribution", "Balance Extremes", "Period Extremes", "Result Table"]
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
                    "Configured Weight": component_weights,
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
    if record.get("snapshot_source") is not None:
        payload["snapshot_source"] = record.get("snapshot_source")

    # GTAA stores cadence in rebalance_interval for history summarization; map it back.
    if strategy_key == "gtaa":
        payload["interval"] = int(record.get("rebalance_interval") or 2)
    return payload


def _strategy_key_to_display_name(strategy_key: str | None) -> str | None:
    mapping = {
        "equal_weight": "Equal Weight",
        "gtaa": "GTAA",
        "risk_parity_trend": "Risk Parity Trend",
        "dual_momentum": "Dual Momentum",
        "quality_snapshot": "Quality Snapshot",
        "quality_snapshot_strict_annual": "Quality Snapshot (Strict Annual)",
        "quality_snapshot_strict_quarterly_prototype": "Quality Snapshot (Strict Quarterly Prototype)",
        "value_snapshot_strict_annual": "Value Snapshot (Strict Annual)",
        "value_snapshot_strict_quarterly_prototype": "Value Snapshot (Strict Quarterly Prototype)",
        "quality_value_snapshot_strict_annual": "Quality + Value Snapshot (Strict Annual)",
        "quality_value_snapshot_strict_quarterly_prototype": "Quality + Value Snapshot (Strict Quarterly Prototype)",
    }
    return mapping.get(strategy_key)


def _load_history_into_form(record: dict[str, Any]) -> bool:
    payload = _build_history_payload(record)
    strategy_name = _strategy_key_to_display_name(record.get("strategy_key"))
    if payload is None or strategy_name is None:
        return False

    st.session_state.backtest_prefill_payload = payload
    st.session_state.backtest_prefill_pending = True
    st.session_state.backtest_prefill_notice = f"Loaded `{strategy_name}` inputs from history."
    st.session_state.backtest_prefill_strategy_choice = strategy_name
    return True


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
        st.session_state["gtaa_interval"] = int(payload.get("interval") or 2)
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
        st.session_state["qss_trend_filter_enabled"] = bool(payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED))
        st.session_state["qss_trend_filter_window"] = int(payload.get("trend_filter_window") or STRICT_TREND_FILTER_DEFAULT_WINDOW)
        st.session_state["qss_market_regime_enabled"] = bool(payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED))
        st.session_state["qss_market_regime_window"] = int(payload.get("market_regime_window") or STRICT_MARKET_REGIME_DEFAULT_WINDOW)
        st.session_state["qss_market_regime_benchmark"] = payload.get("market_regime_benchmark") or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK
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
        st.session_state["vss_trend_filter_enabled"] = bool(payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED))
        st.session_state["vss_trend_filter_window"] = int(payload.get("trend_filter_window") or STRICT_TREND_FILTER_DEFAULT_WINDOW)
        st.session_state["vss_market_regime_enabled"] = bool(payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED))
        st.session_state["vss_market_regime_window"] = int(payload.get("market_regime_window") or STRICT_MARKET_REGIME_DEFAULT_WINDOW)
        st.session_state["vss_market_regime_benchmark"] = payload.get("market_regime_benchmark") or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK
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
        st.session_state["qvss_trend_filter_enabled"] = bool(payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED))
        st.session_state["qvss_trend_filter_window"] = int(payload.get("trend_filter_window") or STRICT_TREND_FILTER_DEFAULT_WINDOW)
        st.session_state["qvss_market_regime_enabled"] = bool(payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED))
        st.session_state["qvss_market_regime_window"] = int(payload.get("market_regime_window") or STRICT_MARKET_REGIME_DEFAULT_WINDOW)
        st.session_state["qvss_market_regime_benchmark"] = payload.get("market_regime_benchmark") or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK
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

    if isinstance(recorded_range, tuple) and len(recorded_range) == 2:
        recorded_start, recorded_end = recorded_range
    else:
        recorded_start = recorded_end = recorded_range

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
                    "snapshot_source": selected_record.get("snapshot_source"),
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
        st.caption("`Load Into Form`은 저장된 입력값을 Single Strategy 화면으로 불러와서 수정만 하도록 돕는 기능입니다. `Run Again`은 저장된 payload를 즉시 다시 실행합니다.")


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
                    trend_filter_enabled=payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED),
                    trend_filter_window=payload.get("trend_filter_window", STRICT_TREND_FILTER_DEFAULT_WINDOW),
                    market_regime_enabled=payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED),
                    market_regime_window=payload.get("market_regime_window", STRICT_MARKET_REGIME_DEFAULT_WINDOW),
                    market_regime_benchmark=payload.get("market_regime_benchmark", STRICT_MARKET_REGIME_DEFAULT_BENCHMARK),
                    universe_mode=payload["universe_mode"],
                    preset_name=payload["preset_name"],
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
                    trend_filter_enabled=payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED),
                    trend_filter_window=payload.get("trend_filter_window", STRICT_TREND_FILTER_DEFAULT_WINDOW),
                    market_regime_enabled=payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED),
                    market_regime_window=payload.get("market_regime_window", STRICT_MARKET_REGIME_DEFAULT_WINDOW),
                    market_regime_benchmark=payload.get("market_regime_benchmark", STRICT_MARKET_REGIME_DEFAULT_BENCHMARK),
                    universe_mode=payload["universe_mode"],
                    preset_name=payload["preset_name"],
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
                    trend_filter_enabled=payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED),
                    trend_filter_window=payload.get("trend_filter_window", STRICT_TREND_FILTER_DEFAULT_WINDOW),
                    market_regime_enabled=payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED),
                    market_regime_window=payload.get("market_regime_window", STRICT_MARKET_REGIME_DEFAULT_WINDOW),
                    market_regime_benchmark=payload.get("market_regime_benchmark", STRICT_MARKET_REGIME_DEFAULT_BENCHMARK),
                    universe_mode=payload["universe_mode"],
                    preset_name=payload["preset_name"],
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

    with st.form("equal_weight_backtest_form", clear_on_submit=False):
        universe_mode = st.radio(
            "Universe Mode",
            options=["Preset", "Manual"],
            horizontal=True,
            help="Preset은 빠른 실행용, Manual은 직접 종목을 입력하는 방식입니다.",
            key="eq_universe_mode",
        )

        preset_name = None
        tickers: list[str] = []

        if universe_mode == "Preset":
            preset_name = st.selectbox(
                "Preset",
                options=list(EQUAL_WEIGHT_PRESETS.keys()),
                index=0,
                key="eq_preset",
            )
            tickers = EQUAL_WEIGHT_PRESETS[preset_name]
            st.caption(f"Selected tickers: `{', '.join(tickers)}`")
        else:
            manual_tickers = st.text_input(
                "Tickers",
                value="VIG,SCHD,DGRO,GLD",
                help="Comma-separated tickers. Example: VIG,SCHD,DGRO,GLD",
                key="eq_manual_tickers",
            )
            tickers = _parse_manual_tickers(manual_tickers)

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
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Equal Weight")


def _render_gtaa_form() -> None:
    st.markdown("### GTAA")
    st.caption("DB-backed GTAA execution using the second public runtime wrapper.")
    _apply_single_strategy_prefill("gtaa")

    with st.form("gtaa_backtest_form", clear_on_submit=False):
        universe_mode = st.radio(
            "Universe Mode",
            options=["Preset", "Manual"],
            horizontal=True,
            help="GTAA는 기본적으로 preset universe 사용을 권장합니다.",
            key="gtaa_universe_mode",
        )

        preset_name = None
        tickers: list[str] = []

        if universe_mode == "Preset":
            preset_name = st.selectbox(
                "Preset",
                options=list(GTAA_PRESETS.keys()),
                index=0,
                key="gtaa_preset",
            )
            tickers = GTAA_PRESETS[preset_name]
            st.caption(f"Selected tickers: `{', '.join(tickers)}`")
        else:
            manual_tickers = st.text_input(
                "Tickers",
                value="SPY,IWD,IWM,IWN,MTUM,EFA,TLT,IEF,LQD,DBC,VNQ,GLD",
                help="Comma-separated tickers. Example: SPY,IWD,IWM,IWN,MTUM,EFA,TLT,IEF,LQD,DBC,VNQ,GLD",
                key="gtaa_manual_tickers",
            )
            tickers = _parse_manual_tickers(manual_tickers)

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
                value=2,
                step=1,
                help="기본값 2는 현재 GTAA 기준값입니다. 1이면 매월, 2면 격월로 신호를 계산합니다.",
                key="gtaa_interval",
            )

        submitted = st.form_submit_button("Run GTAA Backtest", use_container_width=True)

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
        "strategy_key": "gtaa",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "top": int(top),
        "interval": int(interval),
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
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
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Quality + Value Snapshot (Strict Annual)")


def render_backtest_tab() -> None:
    _init_backtest_state()

    st.subheader("Backtest")
    st.caption("Phase 4 backtest tab")

    st.info(
        "This tab is intentionally being opened in small steps. "
        "The app structure is now unified, but the public runtime boundary and first execution screen "
        "will be implemented after each product choice is confirmed."
    )

    left, right = st.columns([1.2, 1.0], gap="large")

    with left:
        st.markdown("### Current Direction")
        st.markdown(
            """
            - One main app
            - Separate `Ingestion` and `Backtest` tabs
            - Internal code split by tab / concern
            - DB-backed price-only strategies first, then the first factor strategy
            - `Equal Weight`, `GTAA`, `Risk Parity Trend`, `Dual Momentum`, `Quality Snapshot`, `Quality Snapshot (Strict Annual)`, `Value Snapshot (Strict Annual)`, and `Quality + Value Snapshot (Strict Annual)` are the current public strategy set
            - `Compare & Portfolio Builder` is the next layer on top of those strategy wrappers
            """
        )

        st.markdown("### Planned First Strategies")
        st.markdown(
            """
            - Equal Weight (first public wrapper)
            - GTAA (second public wrapper)
            - Risk Parity Trend (third public wrapper)
            - Dual Momentum (fourth public wrapper)
            - Quality Snapshot (first broad factor strategy)
            - Quality Snapshot (Strict Annual) (first strict statement-driven public candidate)
            - Value Snapshot (Strict Annual) (second strict statement-driven public candidate)
            - Quality + Value Snapshot (Strict Annual) (first strict multi-factor public candidate)
            """
        )

    with right:
        st.markdown("### Current Phase 4 Status")
        st.markdown(
            """
            - UI structure: chosen
            - Runtime public boundary: Equal Weight + GTAA + Risk Parity Trend + Dual Momentum + Quality Snapshot + Quality Snapshot (Strict Annual) + Value Snapshot (Strict Annual) + Quality + Value Snapshot (Strict Annual)
            - First screen scope: single-strategy execution forms
            - Strategy execution UI: basic result layout connected
            - Compare and weighted-portfolio builder: first-pass rollout
            """
        )

        st.markdown("### Next Step")
        st.markdown(
            """
            The current step opens multi-strategy comparison first, then uses those results for weighted portfolio construction.
            """
        )
    single_tab, compare_tab, history_tab = st.tabs(["Single Strategy", "Compare & Portfolio Builder", "History"])

    with single_tab:
        prefill_notice = st.session_state.get("backtest_prefill_notice")
        if prefill_notice:
            st.info(prefill_notice)
            st.session_state.backtest_prefill_notice = None

        pending_strategy_choice = st.session_state.get("backtest_prefill_strategy_choice")
        if pending_strategy_choice in SINGLE_STRATEGY_OPTIONS:
            st.session_state.backtest_strategy_choice = pending_strategy_choice
            st.session_state.backtest_prefill_strategy_choice = None

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
        elif strategy_choice == "Quality Snapshot":
            _render_quality_snapshot_form()
        elif strategy_choice == "Quality Snapshot (Strict Annual)":
            _render_quality_snapshot_strict_annual_form()
        elif strategy_choice == "Quality Snapshot (Strict Quarterly Prototype)":
            _render_quality_snapshot_strict_quarterly_prototype_form()
        elif strategy_choice == "Value Snapshot (Strict Quarterly Prototype)":
            _render_value_snapshot_strict_quarterly_prototype_form()
        elif strategy_choice == "Value Snapshot (Strict Annual)":
            _render_value_snapshot_strict_annual_form()
        elif strategy_choice == "Quality + Value Snapshot (Strict Quarterly Prototype)":
            _render_quality_value_snapshot_strict_quarterly_prototype_form()
        else:
            _render_quality_value_snapshot_strict_annual_form()
        st.divider()
        _render_last_run()

    with compare_tab:
        st.markdown("### Compare Strategies")
        st.caption("Start with a shared date range and compare up to four strategies chosen from eight DB-backed strategies. This section then feeds directly into a weighted portfolio builder.")

        selected_strategies = st.multiselect(
            "Strategies",
            options=COMPARE_STRATEGY_OPTIONS,
            default=["Equal Weight", "GTAA"],
            max_selections=4,
            help="Up to four strategies can be compared at once in the first pass.",
            key="compare_selected_strategies",
        )
        st.caption("Strategy selection is outside the form so the strategy-specific advanced inputs update immediately.")

        with st.form("compare_backtests_form", clear_on_submit=False):
            col1, col2 = st.columns(2)
            with col1:
                compare_start = st.date_input("Start Date", value=date(2016, 1, 1), key="compare_start")
            with col2:
                compare_end = st.date_input("End Date", value=DEFAULT_BACKTEST_END_DATE, key="compare_end")

            with st.expander("Advanced Inputs", expanded=False):
                compare_timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="compare_timeframe")
                compare_option = st.selectbox("Option", options=["month_end"], index=0, key="compare_option")
                st.markdown("##### Strategy-Specific Advanced Inputs")

                compare_strategy_overrides: dict[str, dict] = {}

                if "Equal Weight" in selected_strategies:
                    with st.expander("Equal Weight", expanded=False):
                        compare_strategy_overrides["Equal Weight"] = {
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
                    with st.expander("GTAA", expanded=False):
                        compare_strategy_overrides["GTAA"] = {
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
                                    value=2,
                                    step=1,
                                    key="compare_gtaa_interval",
                                )
                            ),
                        }

                if "Risk Parity Trend" in selected_strategies:
                    st.markdown("**Risk Parity Trend**")
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
                    }

                if "Dual Momentum" in selected_strategies:
                    st.markdown("**Dual Momentum**")
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
                    }

                if "Quality Snapshot" in selected_strategies:
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

                if "Quality Snapshot (Strict Annual)" in selected_strategies:
                    with st.expander("Quality Snapshot (Strict Annual)", expanded=False):
                        st.caption("Compare mode keeps the strict annual default lighter with `US Statement Coverage 100` so multi-strategy runs stay responsive.")
                        qss_compare_preset = st.selectbox(
                            "Strict Annual Quality Preset",
                            options=list(QUALITY_STRICT_PRESETS.keys()),
                            index=list(QUALITY_STRICT_PRESETS.keys()).index(STRICT_ANNUAL_COMPARE_DEFAULT_PRESET),
                            key="compare_qss_preset",
                        )
                        _render_ticker_preview(QUALITY_STRICT_PRESETS[qss_compare_preset], preview_count=8, tail_count=3)
                        _render_historical_universe_caption()
                        compare_strategy_overrides["Quality Snapshot (Strict Annual)"] = {
                            "preset_name": qss_compare_preset,
                            "tickers": QUALITY_STRICT_PRESETS[qss_compare_preset],
                            "universe_mode": "preset",
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

                if "Quality Snapshot (Strict Quarterly Prototype)" in selected_strategies:
                    with st.expander("Quality Snapshot (Strict Quarterly Prototype)", expanded=False):
                        st.caption("Research-only compare path. Default preset stays at `US Statement Coverage 100` to keep quarterly family validation tractable.")
                        qsqp_compare_preset = st.selectbox(
                            "Strict Quarterly Quality Preset",
                            options=list(QUALITY_STRICT_PRESETS.keys()),
                            index=list(QUALITY_STRICT_PRESETS.keys()).index(STRICT_QUARTERLY_PROTOTYPE_DEFAULT_PRESET),
                            key="compare_qsqp_preset",
                        )
                        _render_ticker_preview(QUALITY_STRICT_PRESETS[qsqp_compare_preset], preview_count=8, tail_count=3)
                        _render_historical_universe_caption()
                        compare_strategy_overrides["Quality Snapshot (Strict Quarterly Prototype)"] = {
                            "preset_name": qsqp_compare_preset,
                            "tickers": QUALITY_STRICT_PRESETS[qsqp_compare_preset],
                            "universe_mode": "preset",
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

                if "Value Snapshot (Strict Annual)" in selected_strategies:
                    with st.expander("Value Snapshot (Strict Annual)", expanded=False):
                        st.caption("Compare mode keeps the strict annual value default lighter with `US Statement Coverage 100` for responsiveness.")
                        vss_compare_preset = st.selectbox(
                            "Strict Annual Value Preset",
                            options=list(VALUE_STRICT_PRESETS.keys()),
                            index=list(VALUE_STRICT_PRESETS.keys()).index(STRICT_ANNUAL_COMPARE_DEFAULT_PRESET),
                            key="compare_vss_preset",
                        )
                        _render_ticker_preview(VALUE_STRICT_PRESETS[vss_compare_preset], preview_count=8, tail_count=3)
                        _render_historical_universe_caption()
                        compare_strategy_overrides["Value Snapshot (Strict Annual)"] = {
                            "preset_name": vss_compare_preset,
                            "tickers": VALUE_STRICT_PRESETS[vss_compare_preset],
                            "universe_mode": "preset",
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

                if "Value Snapshot (Strict Quarterly Prototype)" in selected_strategies:
                    with st.expander("Value Snapshot (Strict Quarterly Prototype)", expanded=False):
                        st.caption("Research-only compare path. Default preset stays at `US Statement Coverage 100` while quarterly value history is being validated.")
                        vsqp_compare_preset = st.selectbox(
                            "Strict Quarterly Value Preset",
                            options=list(VALUE_STRICT_PRESETS.keys()),
                            index=list(VALUE_STRICT_PRESETS.keys()).index(STRICT_QUARTERLY_PROTOTYPE_DEFAULT_PRESET),
                            key="compare_vsqp_preset",
                        )
                        _render_ticker_preview(VALUE_STRICT_PRESETS[vsqp_compare_preset], preview_count=8, tail_count=3)
                        _render_historical_universe_caption()
                        compare_strategy_overrides["Value Snapshot (Strict Quarterly Prototype)"] = {
                            "preset_name": vsqp_compare_preset,
                            "tickers": VALUE_STRICT_PRESETS[vsqp_compare_preset],
                            "universe_mode": "preset",
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

                if "Quality + Value Snapshot (Strict Annual)" in selected_strategies:
                    with st.expander("Quality + Value Snapshot (Strict Annual)", expanded=False):
                        st.caption("Compare mode keeps the strict annual multi-factor default lighter with `US Statement Coverage 100` so multi-strategy runs stay responsive.")
                        qvss_compare_preset = st.selectbox(
                            "Strict Annual Multi-Factor Preset",
                            options=list(QUALITY_STRICT_PRESETS.keys()),
                            index=list(QUALITY_STRICT_PRESETS.keys()).index(STRICT_ANNUAL_COMPARE_DEFAULT_PRESET),
                            key="compare_qvss_preset",
                        )
                        _render_ticker_preview(QUALITY_STRICT_PRESETS[qvss_compare_preset], preview_count=8, tail_count=3)
                        _render_historical_universe_caption()
                        compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"] = {
                            "preset_name": qvss_compare_preset,
                            "tickers": QUALITY_STRICT_PRESETS[qvss_compare_preset],
                            "universe_mode": "preset",
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

                if "Quality + Value Snapshot (Strict Quarterly Prototype)" in selected_strategies:
                    with st.expander("Quality + Value Snapshot (Strict Quarterly Prototype)", expanded=False):
                        st.caption("Research-only compare path. Default preset stays at `US Statement Coverage 100` while quarterly blended history is being validated.")
                        qvqp_compare_preset = st.selectbox(
                            "Strict Quarterly Multi-Factor Preset",
                            options=list(QUALITY_STRICT_PRESETS.keys()),
                            index=list(QUALITY_STRICT_PRESETS.keys()).index(STRICT_QUARTERLY_PROTOTYPE_DEFAULT_PRESET),
                            key="compare_qvqp_preset",
                        )
                        _render_ticker_preview(QUALITY_STRICT_PRESETS[qvqp_compare_preset], preview_count=8, tail_count=3)
                        _render_historical_universe_caption()
                        compare_strategy_overrides["Quality + Value Snapshot (Strict Quarterly Prototype)"] = {
                            "preset_name": qvqp_compare_preset,
                            "tickers": QUALITY_STRICT_PRESETS[qvqp_compare_preset],
                            "universe_mode": "preset",
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

        if compare_submitted:
            if not selected_strategies:
                st.session_state.backtest_compare_bundles = None
                st.session_state.backtest_compare_error_kind = "input"
                st.session_state.backtest_compare_error = "Select at least one strategy to compare."
            elif compare_start > compare_end:
                st.session_state.backtest_compare_bundles = None
                st.session_state.backtest_compare_error_kind = "input"
                st.session_state.backtest_compare_error = "Start Date must be earlier than or equal to End Date."
            else:
                try:
                    bundles = []
                    with st.spinner("Running multi-strategy comparison from DB..."):
                        for strategy_name in selected_strategies:
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
                                "tickers": selected_strategies,
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
                            "selected_strategies": selected_strategies,
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

    with history_tab:
        st.markdown("### Backtest History")
        st.caption("Single-strategy runs and strategy-comparison runs share the same persistent history and drilldown surface.")
        _render_persistent_backtest_history()
