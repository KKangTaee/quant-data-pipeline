from __future__ import annotations

import sys
from collections.abc import Sequence
from typing import Any

import pandas as pd

from app.runtime.backtest.common import BacktestDataError, BacktestInputError
from app.runtime.backtest.common import validate_backtest_date_range as _validate_backtest_date_range
from app.runtime.backtest.result_bundle import build_backtest_result_bundle
from app.runtime.backtest.runners.risk_on_momentum import (
    RISK_ON_MOMENTUM_BENCHMARK_TICKERS,
    RISK_ON_MOMENTUM_DEFAULT_UNIVERSE_LIMIT,
    RISK_ON_MOMENTUM_DEFAULT_UNIVERSE_MODE,
    run_risk_on_momentum_5d_backtest_from_db,
)
from app.runtime.backtest.real_money import (
    ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
    ETF_OPERABILITY_DEFAULT_MIN_AUM_B,
    ETF_OPERABILITY_STRATEGY_KEYS,
    ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
    ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
    REAL_MONEY_CASH_LABEL,
    STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT,
    STRICT_BENCHMARK_CONTRACT_TICKER,
    STRICT_DEFAULT_BENCHMARK_CONTRACT,
    STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
    STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
    STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
    STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
    STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
    STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
    STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
    _apply_real_money_hardening,
    _apply_transaction_cost_postprocess,
    _build_benchmark_policy_surface,
    _build_benchmark_result_df,
    _build_deployment_readiness_contract,
    _build_etf_operability_policy_surface,
    _build_guardrail_policy_surface,
    _build_liquidity_policy_surface,
    _build_promotion_decision,
    _build_probation_and_monitoring_contract,
    _build_real_money_validation_surface,
    _build_rolling_and_out_of_sample_review_surface,
    _build_shortlist_contract,
    _build_validation_policy_surface,
    _build_weight_map,
    _coerce_float,
    _coerce_list_cell,
    _compute_drawdown_stats,
    _compute_total_return,
    _estimate_turnover_series,
    _missing_turnover_input_columns,
    _normalize_tickers,
    _policy_status_to_check_status,
    _resolve_guardrail_reference_ticker,
    _rolling_validation_window,
    _turnover_diagnostics_from_result,
)
from finance.loaders import (
    load_asset_profile_status_summary,
    load_factor_snapshot,
    load_latest_market_date,
    load_price_freshness_summary,
    load_price_history,
    load_statement_factor_snapshot_shadow,
    load_statement_snapshot_strict,
)
from finance.sample import (
    GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD,
    GTAA_DEFAULT_CRASH_GUARDRAIL_ENABLED,
    GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS,
    GTAA_DEFAULT_DEFENSIVE_TICKERS,
    GTAA_DEFAULT_RISK_OFF_MODE,
    GTAA_DEFAULT_SCORE_LOOKBACK_MONTHS,
    GTAA_DEFAULT_SIGNAL_INTERVAL,
    GTAA_DEFAULT_TREND_FILTER_WINDOW,
    GTAA_DEFAULT_SCORE_WEIGHTS,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_CASH_TICKER,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_SCORE_LOOKBACK_MONTHS,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_SIGNAL_INTERVAL,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_TICKERS,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_TOP,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_TREND_FILTER_WINDOW,
    HISTORICAL_DYNAMIC_PIT_UNIVERSE,
    STATIC_MANAGED_RESEARCH_UNIVERSE,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
    STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
    STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    STRICT_DEFAULT_DEFENSIVE_TICKERS,
    STRICT_DEFAULT_REJECTION_HANDLING_MODE,
    STRICT_DEFAULT_RISK_OFF_MODE,
    STRICT_DEFAULT_WEIGHTING_MODE,
    STRICT_REJECTION_HANDLING_MODE_FILL_RETAIN_CASH,
    STRICT_REJECTION_HANDLING_MODE_FILL_REWEIGHT,
    STRICT_REJECTION_HANDLING_MODE_RETAIN_CASH,
    STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
    STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
    STRICT_RISK_OFF_MODE_DEFENSIVE,
    STRICT_WEIGHTING_MODE_EQUAL,
    STRICT_WEIGHTING_MODE_RANK_TAPERED,
    QUALITY_STRICT_DEFAULT_FACTORS,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    VALUE_STRICT_DEFAULT_FACTORS,
    get_dual_momentum_from_db,
    get_equal_weight_from_db,
    get_global_relative_strength_from_db,
    get_gtaa3_from_db,
    get_quality_snapshot_from_db,
    get_risk_parity_trend_from_db,
    get_statement_quality_snapshot_from_db,
    get_statement_quality_value_snapshot_shadow_from_db,
    get_statement_quality_snapshot_shadow_from_db,
    get_statement_value_snapshot_shadow_from_db,
    resolve_strict_rejection_handling_mode,
    strict_rejection_handling_mode_to_flags,
)

from app.runtime.backtest.runners.strict_factor import (
    _build_strict_rejected_slot_handling_warning,
    _dynamic_universe_warning,
    _inspect_dynamic_universe_price_pool,
    _preflight_quality_snapshot_data,
    _preflight_statement_quality_data,
    _preflight_statement_quality_shadow_data,
    _run_statement_quality_bundle,
    inspect_strict_annual_price_freshness,
    run_quality_snapshot_backtest_from_db,
    run_quality_snapshot_strict_annual_backtest_from_db,
    run_quality_snapshot_strict_quarterly_prototype_backtest_from_db,
    run_quality_value_snapshot_strict_annual_backtest_from_db,
    run_quality_value_snapshot_strict_quarterly_prototype_backtest_from_db,
    run_statement_quality_prototype_backtest_from_db,
    run_value_snapshot_strict_annual_backtest_from_db,
    run_value_snapshot_strict_quarterly_prototype_backtest_from_db,
)


_RUNTIME_HOOK_DEFAULTS: dict[str, Any] = {}


def _runtime_hook(name: str, fallback: Any, *module_names: str) -> Any:
    """Resolve patched compatibility facade hooks without changing production defaults."""
    default = _RUNTIME_HOOK_DEFAULTS.get(name, fallback)
    for module_name in (*module_names, "app.runtime.backtest", "app.runtime.backtest.facade"):
        module = sys.modules.get(module_name)
        if module is None:
            continue
        candidate = getattr(module, name, None)
        if candidate is not None and candidate is not default:
            return candidate
    return fallback


def _resolve_dynamic_etf_promotion_policy_defaults(
    *,
    promotion_min_benchmark_coverage: float | None,
    promotion_min_net_cagr_spread: float | None,
    promotion_min_liquidity_clean_coverage: float | None,
    promotion_max_underperformance_share: float | None,
    promotion_min_worst_rolling_excess_return: float | None,
    promotion_max_strategy_drawdown: float | None,
    promotion_max_drawdown_gap_vs_benchmark: float | None,
) -> dict[str, float]:
    """Attach strict-compatible promotion thresholds to ETF dynamic strategy contracts."""

    return {
        "promotion_min_benchmark_coverage": float(
            STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE
            if promotion_min_benchmark_coverage is None
            else promotion_min_benchmark_coverage
        ),
        "promotion_min_net_cagr_spread": float(
            STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD
            if promotion_min_net_cagr_spread is None
            else promotion_min_net_cagr_spread
        ),
        "promotion_min_liquidity_clean_coverage": float(
            STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE
            if promotion_min_liquidity_clean_coverage is None
            else promotion_min_liquidity_clean_coverage
        ),
        "promotion_max_underperformance_share": float(
            STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE
            if promotion_max_underperformance_share is None
            else promotion_max_underperformance_share
        ),
        "promotion_min_worst_rolling_excess_return": float(
            STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN
            if promotion_min_worst_rolling_excess_return is None
            else promotion_min_worst_rolling_excess_return
        ),
        "promotion_max_strategy_drawdown": float(
            STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN
            if promotion_max_strategy_drawdown is None
            else promotion_max_strategy_drawdown
        ),
        "promotion_max_drawdown_gap_vs_benchmark": float(
            STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK
            if promotion_max_drawdown_gap_vs_benchmark is None
            else promotion_max_drawdown_gap_vs_benchmark
        ),
    }


def _normalize_grs_score_contract(
    *,
    score_lookback_months: Sequence[int] | None,
    score_return_columns: Sequence[str] | None,
    score_weights: dict[str, float] | None,
) -> tuple[list[int], list[str], dict[str, float]]:
    if score_return_columns is not None:
        normalized_columns = [
            str(column).strip()
            for column in score_return_columns
            if str(column).strip()
        ]
    else:
        lookbacks = (
            list(score_lookback_months)
            if score_lookback_months is not None
            else list(GLOBAL_RELATIVE_STRENGTH_DEFAULT_SCORE_LOOKBACK_MONTHS)
        )
        normalized_columns = [f"{int(months)}MReturn" for months in lookbacks]

    if not normalized_columns:
        raise BacktestInputError("Global Relative Strength score window must contain at least one return column.")

    parsed_months: list[int] = []
    for column in normalized_columns:
        if column.endswith("MReturn"):
            raw_months = column[: -len("MReturn")]
            if raw_months.isdigit():
                parsed_months.append(int(raw_months))

    if score_lookback_months is not None:
        normalized_months = [int(value) for value in score_lookback_months]
    else:
        normalized_months = parsed_months

    if not normalized_months:
        raise BacktestInputError("Global Relative Strength score lookback months could not be derived from the selected windows.")

    if score_weights is None:
        normalized_weights = {column: 1.0 for column in normalized_columns}
    else:
        normalized_weights = {
            column: float(score_weights.get(column, 0.0))
            for column in normalized_columns
        }

    if sum(abs(value) for value in normalized_weights.values()) <= 0:
        raise BacktestInputError("Global Relative Strength score weights must include at least one non-zero weight.")

    return normalized_months, normalized_columns, normalized_weights


def _build_grs_top_n_concentration_summary(result_df: pd.DataFrame) -> dict[str, Any]:
    if result_df is None or result_df.empty:
        return {
            "contract_version": "grs_top_n_concentration_v1",
            "observation_count": 0,
        }

    def _numeric_series(column: str) -> pd.Series:
        if column not in result_df.columns:
            return pd.Series(dtype="float64")
        return pd.to_numeric(result_df[column], errors="coerce")

    selected = _numeric_series("Selected Count")
    target_slots = _numeric_series("Target Slot Count")
    unfilled = _numeric_series("Unfilled Slot Count")
    cash_share = _numeric_series("Cash Share")
    max_weight = _numeric_series("Max Position Weight")
    statuses = (
        result_df.get("Concentration Status", pd.Series(dtype=object))
        .dropna()
        .astype(str)
        .str.strip()
    )

    return {
        "contract_version": "grs_top_n_concentration_v1",
        "observation_count": int(len(result_df)),
        "max_selected_count": int(selected.max()) if not selected.dropna().empty else None,
        "max_target_slot_count": int(target_slots.max()) if not target_slots.dropna().empty else None,
        "max_unfilled_slot_count": int(unfilled.max()) if not unfilled.dropna().empty else None,
        "max_cash_share": float(cash_share.max()) if not cash_share.dropna().empty else None,
        "avg_cash_share": float(cash_share.mean()) if not cash_share.dropna().empty else None,
        "max_position_weight": float(max_weight.max()) if not max_weight.dropna().empty else None,
        "status_values": sorted(dict.fromkeys(status for status in statuses.tolist() if status)),
    }


def _build_grs_strategy_contract(
    *,
    cash_ticker: str | None,
    benchmark_contract: str,
    benchmark_ticker: str | None,
    top: int,
    interval: int,
    trend_filter_window: int,
    score_lookback_months: list[int],
    score_return_columns: list[str],
    score_weights: dict[str, float],
) -> dict[str, Any]:
    return {
        "contract_version": "grs_strategy_contract_v1",
        "cash_proxy_ticker": cash_ticker,
        "benchmark_contract": benchmark_contract,
        "benchmark_ticker": benchmark_ticker,
        "top_n": int(top),
        "rebalance_interval_months": int(interval),
        "trend_filter_window": int(trend_filter_window),
        "score_lookback_months": list(score_lookback_months),
        "score_return_columns": list(score_return_columns),
        "score_weights": dict(score_weights),
        "cash_handling": "trend_rejected_slots_retained_in_cash_proxy",
    }


def _numeric_result_series(result_df: pd.DataFrame, column: str) -> pd.Series:
    if result_df is None or result_df.empty or column not in result_df.columns:
        return pd.Series(dtype="float64")
    return pd.to_numeric(result_df[column], errors="coerce")


def _bool_result_series(result_df: pd.DataFrame, column: str) -> pd.Series:
    if result_df is None or result_df.empty or column not in result_df.columns:
        return pd.Series(dtype=bool)
    return result_df[column].fillna(False).astype(bool)


def _unique_text_values(result_df: pd.DataFrame, column: str) -> list[str]:
    if result_df is None or result_df.empty or column not in result_df.columns:
        return []
    values: list[str] = []
    for value in result_df[column].dropna().tolist():
        if isinstance(value, (list, tuple, set)):
            values.extend(str(item).strip() for item in value if str(item).strip())
        else:
            text = str(value).strip()
            if text:
                values.append(text)
    return sorted(dict.fromkeys(values))


def _build_risk_parity_trend_contract(
    *,
    vol_window: int,
    rebalance_interval: int,
    min_price_filter: float | None,
    benchmark_ticker: str | None,
    underperformance_guardrail_enabled: bool,
    drawdown_guardrail_enabled: bool,
) -> dict[str, Any]:
    return {
        "contract_version": "risk_parity_trend_contract_v1",
        "volatility_window_months": int(vol_window),
        "rebalance_interval_months": int(rebalance_interval),
        "trend_filter_window": 200,
        "weighting_mode": "inverse_vol",
        "eligible_universe": "trend_and_min_price_filtered",
        "cash_handling": "cash_only_when_no_positive_inverse_vol_or_guardrail",
        "min_price_filter": min_price_filter,
        "benchmark_ticker": benchmark_ticker,
        "underperformance_guardrail_enabled": bool(underperformance_guardrail_enabled),
        "drawdown_guardrail_enabled": bool(drawdown_guardrail_enabled),
    }


def _build_risk_parity_inverse_vol_summary(result_df: pd.DataFrame) -> dict[str, Any]:
    if result_df is None or result_df.empty:
        return {
            "contract_version": "risk_parity_inverse_vol_summary_v1",
            "observation_count": 0,
        }

    selected = _numeric_result_series(result_df, "Selected Count")
    eligible = _numeric_result_series(result_df, "Eligible Count")
    cash_share = _numeric_result_series(result_df, "Cash Share")
    max_weight = _numeric_result_series(result_df, "Max Position Weight")
    cash_only = _bool_result_series(result_df, "Cash Only State")
    guardrail_cash_only = _bool_result_series(result_df, "Guardrail Cash Only State")

    return {
        "contract_version": "risk_parity_inverse_vol_summary_v1",
        "observation_count": int(len(result_df)),
        "max_selected_count": int(selected.max()) if not selected.dropna().empty else None,
        "max_eligible_count": int(eligible.max()) if not eligible.dropna().empty else None,
        "cash_only_rebalances": int(cash_only.sum()) if not cash_only.empty else 0,
        "guardrail_cash_only_rebalances": int(guardrail_cash_only.sum()) if not guardrail_cash_only.empty else 0,
        "max_cash_share": float(cash_share.max()) if not cash_share.dropna().empty else None,
        "max_position_weight": float(max_weight.max()) if not max_weight.dropna().empty else None,
        "low_vol_overweight_tickers": _unique_text_values(result_df, "Low Vol Overweight Ticker"),
        "cash_only_reasons": _unique_text_values(result_df, "Cash Only Reason"),
    }


def _build_dual_momentum_contract(
    *,
    top: int,
    rebalance_interval: int,
    min_price_filter: float | None,
    benchmark_ticker: str | None,
    underperformance_guardrail_enabled: bool,
    drawdown_guardrail_enabled: bool,
    cash_proxy_ticker: str = "BIL",
) -> dict[str, Any]:
    return {
        "contract_version": "dual_momentum_contract_v1",
        "top_n": int(top),
        "rebalance_interval_months": int(rebalance_interval),
        "lookback_column": "12MReturn",
        "trend_filter_window": 200,
        "weighting_mode": "equal_slot_with_cash_retention",
        "cash_proxy_ticker": cash_proxy_ticker,
        "cash_handling": "trend_rejected_top_n_slots_retained_in_cash_proxy",
        "min_price_filter": min_price_filter,
        "benchmark_ticker": benchmark_ticker,
        "underperformance_guardrail_enabled": bool(underperformance_guardrail_enabled),
        "drawdown_guardrail_enabled": bool(drawdown_guardrail_enabled),
    }


def _build_dual_momentum_concentration_turnover_summary(result_df: pd.DataFrame) -> dict[str, Any]:
    if result_df is None or result_df.empty:
        return {
            "contract_version": "dual_momentum_concentration_turnover_v1",
            "observation_count": 0,
        }

    selected = _numeric_result_series(result_df, "Selected Count")
    target_slots = _numeric_result_series(result_df, "Target Slot Count")
    trend_rejected = _numeric_result_series(result_df, "Trend Rejected Count")
    unfilled = _numeric_result_series(result_df, "Unfilled Slot Count")
    cash_share = _numeric_result_series(result_df, "Cash Share")
    max_weight = _numeric_result_series(result_df, "Max Position Weight")
    selection_changed = _bool_result_series(result_df, "Selection Changed")
    statuses = _unique_text_values(result_df, "Concentration Status")
    whipsaw_statuses = _unique_text_values(result_df, "Whipsaw Status")

    return {
        "contract_version": "dual_momentum_concentration_turnover_v1",
        "observation_count": int(len(result_df)),
        "max_selected_count": int(selected.max()) if not selected.dropna().empty else None,
        "max_target_slot_count": int(target_slots.max()) if not target_slots.dropna().empty else None,
        "max_trend_rejected_count": int(trend_rejected.max()) if not trend_rejected.dropna().empty else None,
        "max_unfilled_slot_count": int(unfilled.max()) if not unfilled.dropna().empty else None,
        "max_cash_share": float(cash_share.max()) if not cash_share.dropna().empty else None,
        "max_position_weight": float(max_weight.max()) if not max_weight.dropna().empty else None,
        "selection_change_events": int(selection_changed.sum()) if not selection_changed.empty else 0,
        "concentration_status_values": statuses,
        "whipsaw_status_values": whipsaw_statuses,
    }




def _summary_frequency(option: str, timeframe: str) -> str:
    if option == "month_end":
        return "M"
    if timeframe == "1d":
        return "D"
    return "M"




def _preflight_equal_weight_data(
    *,
    tickers: list[str],
    start: str | None,
    end: str | None,
    timeframe: str,
) -> None:
    history = load_price_history(
        symbols=tickers,
        start=start,
        end=end,
        timeframe=timeframe,
    )
    if history.empty:
        raise BacktestDataError(
            "No OHLCV rows were found in MySQL for the requested tickers and date range. "
            "Run the ingestion pipeline first."
        )

    available_symbols = set(history["symbol"].astype(str).str.upper().unique().tolist())
    missing = [ticker for ticker in tickers if ticker not in available_symbols]
    if missing:
        raise BacktestDataError(
            "Some requested tickers do not have DB price history for the selected range: "
            + ", ".join(missing)
        )


def _preflight_price_strategy_data(
    *,
    tickers: list[str],
    start: str | None,
    end: str | None,
    timeframe: str,
) -> None:
    history = load_price_history(
        symbols=tickers,
        start=start,
        end=end,
        timeframe=timeframe,
    )
    if history.empty:
        raise BacktestDataError(
            "No OHLCV rows were found in MySQL for the requested tickers and date range. "
            "Run the ingestion pipeline first."
        )

    available_symbols = set(history["symbol"].astype(str).str.upper().unique().tolist())
    missing = [ticker for ticker in tickers if ticker not in available_symbols]
    if missing:
        raise BacktestDataError(
            "Some requested tickers do not have DB price history for the selected range: "
            + ", ".join(missing)
        )









_RUNTIME_HOOK_DEFAULTS.update(
    {
        "_apply_real_money_hardening": _apply_real_money_hardening,
        "_preflight_price_strategy_data": _preflight_price_strategy_data,
        "get_dual_momentum_from_db": get_dual_momentum_from_db,
        "get_equal_weight_from_db": get_equal_weight_from_db,
        "get_global_relative_strength_from_db": get_global_relative_strength_from_db,
        "get_gtaa3_from_db": get_gtaa3_from_db,
        "get_risk_parity_trend_from_db": get_risk_parity_trend_from_db,
        "inspect_strict_annual_price_freshness": inspect_strict_annual_price_freshness,
    }
)


__all__ = [name for name in globals() if not name.startswith("__")]
