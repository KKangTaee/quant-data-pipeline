from __future__ import annotations

from app.web.backtest_common import *  # noqa: F401,F403
from app.web.backtest_practical_validation_helpers import (
    build_selection_source_from_saved_mix_prefill,
    queue_practical_validation_source,
)
from app.web.backtest_history import (
    render_real_money_guardrail_parity_snapshot as _render_real_money_guardrail_parity_snapshot,
)
from app.web.backtest_result_display import *  # noqa: F401,F403

def _strategy_compare_defaults(strategy_name: str) -> dict:
    if strategy_name == "Equal Weight":
        return {
            "tickers": ["VIG", "SCHD", "DGRO", "GLD"],
            "preset_name": "Dividend ETFs",
            "runner": run_equal_weight_backtest_from_db,
            "extra": {
                "rebalance_interval": 12,
                "min_price_filter": ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
                "transaction_cost_bps": ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
                "benchmark_ticker": ETF_REAL_MONEY_DEFAULT_BENCHMARK,
                "promotion_min_etf_aum_b": ETF_OPERABILITY_DEFAULT_MIN_AUM_B,
                "promotion_max_bid_ask_spread_pct": ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
            },
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
    if strategy_name == "Global Relative Strength":
        return {
            "tickers": list(GLOBAL_RELATIVE_STRENGTH_DEFAULT_TICKERS),
            "preset_name": "Global Relative Strength Core ETF Universe",
            "runner": run_global_relative_strength_backtest_from_db,
            "extra": {
                "cash_ticker": GLOBAL_RELATIVE_STRENGTH_DEFAULT_CASH_TICKER,
                "top": GLOBAL_RELATIVE_STRENGTH_DEFAULT_TOP,
                "interval": GLOBAL_RELATIVE_STRENGTH_DEFAULT_SIGNAL_INTERVAL,
                "score_lookback_months": list(GLOBAL_RELATIVE_STRENGTH_DEFAULT_SCORE_LOOKBACK_MONTHS),
                "score_return_columns": list(GLOBAL_RELATIVE_STRENGTH_SCORE_RETURN_COLUMNS),
                "score_weights": dict(GLOBAL_RELATIVE_STRENGTH_DEFAULT_SCORE_WEIGHTS),
                "trend_filter_window": GLOBAL_RELATIVE_STRENGTH_DEFAULT_TREND_FILTER_WINDOW,
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
                "weighting_mode": STRICT_DEFAULT_WEIGHTING_MODE,
                "rejected_slot_handling_mode": STRICT_DEFAULT_REJECTION_HANDLING_MODE,
                "rejected_slot_fill_enabled": STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
                "partial_cash_retention_enabled": STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
                "risk_off_mode": STRICT_DEFAULT_RISK_OFF_MODE,
                "defensive_tickers": STRICT_DEFAULT_DEFENSIVE_TICKERS,
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
                "weighting_mode": STRICT_DEFAULT_WEIGHTING_MODE,
                "rejected_slot_handling_mode": STRICT_DEFAULT_REJECTION_HANDLING_MODE,
                "rejected_slot_fill_enabled": STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
                "partial_cash_retention_enabled": STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
                "risk_off_mode": STRICT_DEFAULT_RISK_OFF_MODE,
                "defensive_tickers": STRICT_DEFAULT_DEFENSIVE_TICKERS,
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
                "weighting_mode": STRICT_DEFAULT_WEIGHTING_MODE,
                "rejected_slot_handling_mode": STRICT_DEFAULT_REJECTION_HANDLING_MODE,
                "rejected_slot_fill_enabled": STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
                "partial_cash_retention_enabled": STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
                "risk_off_mode": STRICT_DEFAULT_RISK_OFF_MODE,
                "defensive_tickers": STRICT_DEFAULT_DEFENSIVE_TICKERS,
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
    elif strategy_name == "Global Relative Strength":
        universe_mode = params.pop("universe_mode", "preset")
        preset_name = params.pop("preset_name", preset_name)
        tickers = list(params.pop("tickers", tickers))
        if universe_mode == "preset" and preset_name in GLOBAL_RELATIVE_STRENGTH_PRESETS:
            tickers = GLOBAL_RELATIVE_STRENGTH_PRESETS[preset_name]
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

    runner_signature = inspect.signature(runner)
    if not any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD
        for parameter in runner_signature.parameters.values()
    ):
        params = {
            key: value
            for key, value in params.items()
            if key in runner_signature.parameters
        }

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

def _safe_summary_metric(bundle: dict[str, Any], column: str) -> float | None:
    summary_df = bundle.get("summary_df")
    if not isinstance(summary_df, pd.DataFrame) or summary_df.empty or column not in summary_df.columns:
        return None
    value = pd.to_numeric(pd.Series([summary_df.iloc[0].get(column)]), errors="coerce").iloc[0]
    if pd.isna(value):
        return None
    return float(value)

def _compare_strategy_contract_label(bundle: dict[str, Any]) -> str:
    meta = dict(bundle.get("meta") or {})
    parts = []
    if meta.get("preset_name"):
        parts.append(f"preset={meta.get('preset_name')}")
    if meta.get("top") is not None:
        parts.append(f"top={meta.get('top')}")
    if meta.get("rebalance_interval") is not None:
        parts.append(f"interval={meta.get('rebalance_interval')}")
    if meta.get("score_lookback_months"):
        score_parts = []
        for month in meta.get("score_lookback_months") or []:
            month_text = str(month).strip()
            score_parts.append(month_text if month_text.upper().endswith("M") else f"{month_text}M")
        parts.append("score=" + "/".join(score_parts))
    if meta.get("trend_filter_window") is not None:
        parts.append(f"trend=MA{meta.get('trend_filter_window')}")
    if meta.get("risk_off_mode"):
        parts.append(f"risk_off={meta.get('risk_off_mode')}")
    return " / ".join(parts) if parts else "-"

def _build_compare_strategy_overview_rows(bundles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    data_trust_rows = {
        str(row.get("Strategy") or ""): row
        for row in _build_strategy_data_trust_rows(bundles)
    }
    rows: list[dict[str, Any]] = []
    for bundle in bundles:
        strategy_name = str(bundle.get("strategy_name") or "-")
        meta = dict(bundle.get("meta") or {})
        data_trust = data_trust_rows.get(strategy_name, {})
        rows.append(
            {
                "Strategy": strategy_name,
                "Contract": _compare_strategy_contract_label(bundle),
                "End Balance": _safe_summary_metric(bundle, "End Balance"),
                "CAGR": _safe_summary_metric(bundle, "CAGR"),
                "MDD": _safe_summary_metric(bundle, "Maximum Drawdown"),
                "Sharpe": _safe_summary_metric(bundle, "Sharpe Ratio"),
                "Data Trust": data_trust.get("Interpretation") or "-",
                "Promotion": meta.get("promotion_decision") or "-",
                "Deployment": _deployment_readiness_status_value_to_label(meta.get("deployment_readiness_status")),
            }
        )
    return rows

def _rank_candidate_metric(
    metric_rows: list[dict[str, Any]],
    *,
    candidate_strategy: str,
    column: str,
    higher_is_better: bool = True,
) -> dict[str, Any]:
    values = [
        (str(row.get("Strategy") or ""), row.get(column))
        for row in metric_rows
        if row.get(column) is not None and not pd.isna(row.get(column))
    ]
    candidate_value = next((value for strategy, value in values if strategy == candidate_strategy), None)
    if candidate_value is None or not values:
        return {
            "rank": None,
            "count": len(values),
            "value": candidate_value,
            "top_half": False,
        }
    better_count = sum(
        1
        for _, value in values
        if (float(value) > float(candidate_value) if higher_is_better else float(value) < float(candidate_value))
    )
    rank = better_count + 1
    count = len(values)
    top_half_limit = max(1, (count + 1) // 2)
    return {
        "rank": rank,
        "count": count,
        "value": float(candidate_value),
        "top_half": rank <= top_half_limit,
    }

def _build_compare_relative_evidence(
    *,
    bundles: list[dict[str, Any]],
    candidate_strategy: str,
) -> dict[str, Any]:
    overview_rows = _build_compare_strategy_overview_rows(bundles)
    metric_specs = [
        ("End Balance", "End Balance", True),
        ("CAGR", "CAGR", True),
        ("Maximum Drawdown", "MDD", True),
        ("Sharpe Ratio", "Sharpe", True),
    ]
    rank_rows: list[dict[str, Any]] = []
    advantages: list[str] = []
    for label, column, higher_is_better in metric_specs:
        rank_info = _rank_candidate_metric(
            overview_rows,
            candidate_strategy=candidate_strategy,
            column=column,
            higher_is_better=higher_is_better,
        )
        rank = rank_info.get("rank")
        count = rank_info.get("count") or 0
        if rank_info.get("top_half"):
            advantages.append(label)
        rank_rows.append(
            {
                "비교 항목": label,
                "현재 값": rank_info.get("value"),
                "순위": f"{rank} / {count}" if rank is not None and count else "-",
                "판단": "상위권 근거" if rank_info.get("top_half") else "추가 설명 필요",
            }
        )

    cagr_rank = next((row for row in rank_rows if row["비교 항목"] == "CAGR"), {})
    mdd_rank = next((row for row in rank_rows if row["비교 항목"] == "Maximum Drawdown"), {})
    cagr_rank_text = str(cagr_rank.get("순위") or "")
    mdd_rank_text = str(mdd_rank.get("순위") or "")
    bottom_on_cagr_and_mdd = False
    if " / " in cagr_rank_text and " / " in mdd_rank_text:
        cagr_pos, cagr_count = [int(value.strip()) for value in cagr_rank_text.split(" / ")]
        mdd_pos, mdd_count = [int(value.strip()) for value in mdd_rank_text.split(" / ")]
        bottom_on_cagr_and_mdd = cagr_pos == cagr_count and mdd_pos == mdd_count

    has_return_advantage = bool({"End Balance", "CAGR"}.intersection(advantages))
    has_risk_advantage = bool({"Maximum Drawdown", "Sharpe Ratio"}.intersection(advantages))
    if has_return_advantage and has_risk_advantage:
        score = 3.0
        judgment = "성과와 위험 쪽에 모두 설명 가능한 상대 근거가 있음"
    elif advantages:
        score = 2.0
        judgment = "일부 상대 우위가 있어 Candidate Review 검토 가능"
    elif bottom_on_cagr_and_mdd:
        score = 0.0
        judgment = "CAGR과 MDD가 모두 최하위라 후보 초안 전에 재검토 필요"
    else:
        score = 1.0
        judgment = "상대 우위가 약해 operator 설명이 필요"

    return {
        "score": score,
        "judgment": judgment,
        "advantages": advantages,
        "rank_rows": rank_rows,
        "overview_rows": overview_rows,
    }

def _safe_interval_months_from_meta(meta: dict[str, Any]) -> int:
    for key in ("rebalance_interval", "interval"):
        try:
            value = meta.get(key)
            if value in (None, ""):
                continue
            interval = int(float(value))
            if interval > 0:
                return interval
        except (TypeError, ValueError):
            continue
    return 0


# Detect normal result-date gaps created by month-end interval strategies such
# as GTAA, so cadence gaps are not treated as stale price data.
def _build_cadence_alignment_assessment(
    *,
    meta: dict[str, Any],
    requested_end: Any,
    actual_end: Any,
    shortened_days: int,
) -> dict[str, Any]:
    if shortened_days <= 31:
        return {}
    strategy_label = " ".join(
        str(meta.get(key) or "")
        for key in ("strategy_key", "strategy_name", "preset_name")
    ).lower()
    if "gtaa" not in strategy_label:
        return {}
    option = str(meta.get("option") or "").strip().lower()
    if option != "month_end":
        return {}
    interval = _safe_interval_months_from_meta(meta)
    if interval <= 1:
        return {}

    actual_end_ts = pd.to_datetime(actual_end, errors="coerce")
    requested_end_ts = pd.to_datetime(requested_end, errors="coerce")
    if pd.isna(actual_end_ts) or pd.isna(requested_end_ts):
        return {}
    actual_anchor = actual_end_ts + pd.offsets.MonthEnd(0)
    next_expected_close = actual_anchor + pd.offsets.MonthEnd(interval)
    if requested_end_ts.date() > next_expected_close.date():
        return {}

    return {
        "strategy": meta.get("strategy_name") or meta.get("strategy_key") or "GTAA",
        "interval": interval,
        "option": option,
        "actual_anchor": str(actual_anchor.date()),
        "next_expected_close": str(next_expected_close.date()),
        "requested_end": str(requested_end_ts.date()),
        "shortened_days": shortened_days,
        "judgment": (
            f"GTAA interval={interval}, month_end 기준 다음 확정 row "
            f"{next_expected_close.date()} 전의 정상 cadence gap"
        ),
    }


def _build_compare_data_trust_assessment(bundle: dict[str, Any]) -> dict[str, Any]:
    meta = dict(bundle.get("meta") or {})
    result_df = bundle.get("result_df")
    price_freshness = dict(meta.get("price_freshness") or {})
    freshness_status = str(price_freshness.get("status") or "").strip().lower()
    excluded_tickers = list(meta.get("excluded_tickers") or [])
    malformed_price_rows = list(meta.get("malformed_price_rows") or [])
    warnings = list(meta.get("warnings") or [])

    requested_end = meta.get("end") or meta.get("requested_end") or meta.get("input_end")
    actual_end = meta.get("actual_result_end")
    if not actual_end and isinstance(result_df, pd.DataFrame) and not result_df.empty and "Date" in result_df.columns:
        actual_end = str(pd.to_datetime(result_df["Date"], errors="coerce").max().date())
    actual_end_ts = pd.to_datetime(actual_end, errors="coerce")
    requested_end_ts = pd.to_datetime(requested_end, errors="coerce")
    period_shortened = (
        pd.notna(actual_end_ts)
        and pd.notna(requested_end_ts)
        and actual_end_ts.date() < requested_end_ts.date()
    )
    shortened_days = (
        (requested_end_ts.date() - actual_end_ts.date()).days
        if period_shortened
        else 0
    )
    cadence_meta = {**meta, "strategy_name": bundle.get("strategy_name") or meta.get("strategy_name")}
    cadence_alignment = _build_cadence_alignment_assessment(
        meta=cadence_meta,
        requested_end=requested_end,
        actual_end=actual_end,
        shortened_days=shortened_days,
    )

    reasons: list[str] = []
    if freshness_status == "error":
        reasons.append("가격 최신성 error")
    if period_shortened:
        if cadence_alignment:
            reasons.append(str(cadence_alignment.get("judgment")))
        else:
            reasons.append(f"실제 결과 종료일이 요청 종료일보다 {shortened_days}일 짧음")
    if freshness_status == "warning":
        reasons.append("가격 최신성 warning")
    if excluded_tickers:
        reasons.append(f"excluded ticker {len(excluded_tickers)}개")
    if malformed_price_rows:
        reasons.append(f"malformed price row {len(malformed_price_rows)}개")
    if warnings:
        reasons.append(f"warning {len(warnings)}개")

    data_blocked = freshness_status == "error" or (shortened_days > 31 and not cadence_alignment)
    data_warning = (
        period_shortened
        or freshness_status == "warning"
        or bool(excluded_tickers)
        or bool(malformed_price_rows)
        or bool(warnings)
    )

    if data_blocked:
        score = 0.0
        judgment = "Data Trust blocked"
        gate_status = "blocked"
        tone = "error"
    elif data_warning:
        score = 1.0
        judgment = "Data Trust warning"
        gate_status = "warning"
        tone = "warning"
    else:
        score = 2.0
        judgment = "Data Trust OK"
        gate_status = "ok"
        tone = "success"

    return {
        "score": score,
        "judgment": judgment,
        "gate_status": gate_status,
        "tone": tone,
        "reasons": reasons,
        "requested_end": requested_end,
        "actual_end": actual_end,
        "shortened_days": shortened_days,
        "cadence_alignment": cadence_alignment,
    }

def _build_compare_real_money_gate_assessment(bundle: dict[str, Any]) -> dict[str, Any]:
    meta = dict(bundle.get("meta") or {})
    if not meta.get("real_money_hardening"):
        return {
            "score": 1.0,
            "ready": False,
            "hard_blocked": True,
            "judgment": "Real-Money gate 정보가 없어 후보 초안 전 재확인 필요",
            "reasons": ["Real-Money hardening 정보 없음"],
        }

    promotion = str(meta.get("promotion_decision") or "").strip().lower()
    deployment = str(meta.get("deployment_readiness_status") or "").strip().lower()
    severe_statuses = {"caution", "unavailable", "error", "missing"}
    severe_issue_rows = [
        row
        for row in _build_stage_issue_resolution_rows(meta)
        if str(row.get("현재 상태") or "").strip().lower() in severe_statuses
    ]

    promotion_ok = bool(promotion and promotion != "hold")
    deployment_ok = bool(deployment and deployment != "blocked")
    blocker_ok = not severe_issue_rows
    score = float(promotion_ok) + float(deployment_ok) + float(blocker_ok)
    reasons: list[str] = []
    if not promotion_ok:
        reasons.append("Promotion Decision이 hold이거나 비어 있음")
    if not deployment_ok:
        reasons.append("Deployment Readiness가 blocked이거나 비어 있음")
    reasons.extend(f"{row.get('항목')}: {row.get('현재 상태')}" for row in severe_issue_rows)

    ready = promotion_ok and deployment_ok and blocker_ok
    if ready:
        judgment = "Real-Money gate가 Candidate Review 검토를 막지 않음"
    else:
        judgment = "Real-Money gate에서 먼저 해결할 blocker가 있음"

    return {
        "score": score,
        "ready": ready,
        "hard_blocked": not ready,
        "judgment": judgment,
        "reasons": reasons,
    }

def _build_candidate_draft_readiness_evaluation(
    bundles: list[dict[str, Any]],
    *,
    candidate_strategy: str,
) -> dict[str, Any]:
    selected_bundle = next(
        (bundle for bundle in bundles if str(bundle.get("strategy_name") or "") == candidate_strategy),
        None,
    )
    compare_complete = (
        len(bundles) >= 2
        and all(isinstance(bundle.get("summary_df"), pd.DataFrame) and not bundle["summary_df"].empty for bundle in bundles)
        and all(isinstance(bundle.get("result_df"), pd.DataFrame) and not bundle["result_df"].empty for bundle in bundles)
    )
    compare_score = 2.0 if compare_complete else (1.0 if len(bundles) >= 2 else 0.0)
    compare_judgment = (
        "2개 이상 전략이 정상 비교됨"
        if compare_score == 2.0
        else "Compare 실행 결과가 부족하거나 1개 전략만 있음"
    )

    if selected_bundle is None:
        data_assessment = {
            "score": 0.0,
            "judgment": "선택 후보 없음",
            "gate_status": "blocked",
            "tone": "error",
            "reasons": ["선택 후보 없음"],
        }
        real_money_assessment = {"score": 0.0, "ready": False, "hard_blocked": True, "judgment": "선택 후보 없음", "reasons": []}
        relative_evidence = {
            "score": 0.0,
            "judgment": "선택 후보 없음",
            "advantages": [],
            "rank_rows": [],
            "overview_rows": _build_compare_strategy_overview_rows(bundles),
        }
    else:
        data_assessment = _build_compare_data_trust_assessment(selected_bundle)
        real_money_assessment = _build_compare_real_money_gate_assessment(selected_bundle)
        relative_evidence = _build_compare_relative_evidence(
            bundles=bundles,
            candidate_strategy=candidate_strategy,
        )

    score = round(
        compare_score
        + float(data_assessment["score"])
        + float(real_money_assessment["score"])
        + float(relative_evidence["score"]),
        1,
    )
    data_gate_status = str(data_assessment.get("gate_status") or "ok").strip().lower()
    blocking_gate = (
        compare_score < 2.0
        or data_gate_status == "blocked"
        or bool(real_money_assessment.get("hard_blocked"))
        or float(relative_evidence["score"]) == 0.0
    )
    clean_pass = (
        score >= 8.0
        and compare_score == 2.0
        and float(data_assessment["score"]) == 2.0
        and data_gate_status == "ok"
        and bool(real_money_assessment.get("ready"))
        and float(relative_evidence["score"]) >= 2.0
    )
    conditional_pass = (
        score >= 6.5
        and compare_score >= 1.0
        and data_gate_status in {"ok", "warning"}
        and bool(real_money_assessment.get("ready"))
        and float(relative_evidence["score"]) >= 1.0
    )

    if clean_pass:
        stage_status = "PASS"
        verdict = "PASS: Candidate Review로 이동 가능"
        tone = "success"
        next_action = "선택 후보를 6단계 Candidate Review로 보내고 operator 판단과 registry 저장 준비를 이어갑니다."
    elif conditional_pass:
        stage_status = "CONDITIONAL"
        verdict = "CONDITIONAL: 보강 항목을 남기고 Candidate Review 이동 가능"
        tone = "warning"
        next_action = "6단계 Candidate Review로 넘기되 비교 약점과 확인 항목을 Review Note에 명시합니다."
    else:
        stage_status = "FAIL"
        verdict = "FAIL: 5단계 Compare 보강 필요"
        tone = "error"
        next_action = "아래 Summary / Data Trust / Real-Money / Strategy Highlights를 다시 확인합니다."

    blocking_reasons: list[str] = []
    if compare_score < 2.0:
        blocking_reasons.append(compare_judgment)
    if data_gate_status == "blocked":
        blocking_reasons.extend(data_assessment.get("reasons") or [str(data_assessment.get("judgment"))])
    if real_money_assessment.get("hard_blocked"):
        blocking_reasons.extend(real_money_assessment.get("reasons") or [str(real_money_assessment.get("judgment"))])
    if float(relative_evidence["score"]) == 0.0:
        blocking_reasons.append(str(relative_evidence.get("judgment")))

    review_reasons: list[str] = []
    if data_gate_status == "warning":
        review_reasons.extend(data_assessment.get("reasons") or [str(data_assessment.get("judgment"))])
    if float(relative_evidence["score"]) in {1.0, 2.0}:
        review_reasons.append(str(relative_evidence.get("judgment")))

    criteria_rows = [
        {
            "기준": "Compare Run",
            "상태": "PASS" if compare_score == 2.0 else ("REVIEW" if compare_score == 1.0 else "FAIL"),
            "현재 값": f"{len(bundles)}개 전략",
            "점수": f"{compare_score:g} / 2",
            "판단": compare_judgment,
        },
        {
            "기준": "Data Trust",
            "상태": "PASS" if data_gate_status == "ok" else ("REVIEW" if data_gate_status == "warning" else "FAIL"),
            "현재 값": data_assessment.get("judgment"),
            "점수": f"{float(data_assessment['score']):g} / 2",
            "판단": ", ".join(data_assessment.get("reasons") or []) or "특이사항 없음",
        },
        {
            "기준": "Real-Money Gate",
            "상태": "PASS" if bool(real_money_assessment.get("ready")) else "FAIL",
            "현재 값": real_money_assessment.get("judgment"),
            "점수": f"{float(real_money_assessment['score']):g} / 3",
            "판단": ", ".join(real_money_assessment.get("reasons") or []) or "특이사항 없음",
        },
        {
            "기준": "Relative Evidence",
            "상태": "PASS" if float(relative_evidence["score"]) >= 2.0 else ("REVIEW" if float(relative_evidence["score"]) >= 1.0 else "FAIL"),
            "현재 값": relative_evidence.get("judgment"),
            "점수": f"{float(relative_evidence['score']):g} / 3",
            "판단": ", ".join(relative_evidence.get("advantages") or []) or "상대 우위 약함",
        },
    ]

    return {
        "score": score,
        "stage_status": stage_status,
        "verdict": verdict,
        "tone": tone,
        "next_action": next_action,
        "can_send_to_candidate_draft": clean_pass or conditional_pass,
        "data_trust_gate": {
            "status": data_gate_status,
            "tone": data_assessment.get("tone") or "success",
            "judgment": data_assessment.get("judgment"),
            "reasons": data_assessment.get("reasons") or [],
            "requested_end": data_assessment.get("requested_end"),
            "actual_end": data_assessment.get("actual_end"),
        },
        "criteria_rows": criteria_rows,
        "rank_rows": relative_evidence.get("rank_rows") or [],
        "overview_rows": relative_evidence.get("overview_rows") or [],
        "blocking_reasons": blocking_reasons,
        "review_reasons": review_reasons,
        "selected_bundle": selected_bundle,
    }

# Read append-only workflow registries to see whether a saved mix has moved beyond
# reusable setup storage into proposal / final-review workflow records.
def _find_saved_mix_workflow_references(record: dict[str, Any]) -> list[dict[str, str]]:
    portfolio_id = str(record.get("portfolio_id") or "").strip()
    portfolio_name = str(record.get("name") or "").strip()
    search_terms = [term for term in {portfolio_id, portfolio_name} if term]
    if not search_terms:
        return []

    registry_paths = [
        PROJECT_ROOT / ".note" / "finance" / "registries" / "CURRENT_CANDIDATE_REGISTRY.jsonl",
        PROJECT_ROOT / ".note" / "finance" / "registries" / "PRE_LIVE_CANDIDATE_REGISTRY.jsonl",
        PROJECT_ROOT / ".note" / "finance" / "registries" / "PORTFOLIO_PROPOSAL_REGISTRY.jsonl",
        PROJECT_ROOT / ".note" / "finance" / "registries" / "FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl",
    ]
    references: list[dict[str, str]] = []
    for path in registry_paths:
        if not path.exists():
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
            if any(term in line for term in search_terms):
                references.append(
                    {
                        "Registry": path.name,
                        "Line": str(line_number),
                        "Matched": ", ".join(term for term in search_terms if term in line),
                    }
                )
    return references

def _weighted_bundle_actual_end(bundle: dict[str, Any]) -> str | None:
    result_df = bundle.get("result_df")
    if not isinstance(result_df, pd.DataFrame) or result_df.empty or "Date" not in result_df.columns:
        return None
    actual_end = pd.to_datetime(result_df["Date"], errors="coerce").max()
    if pd.isna(actual_end):
        return None
    return str(actual_end.date())

def _safe_int_value(value: Any) -> int:
    try:
        if value is None or value == "":
            return 0
        return int(float(value))
    except (TypeError, ValueError):
        return 0

# Evaluate a saved weighted mix as a reusable portfolio setup, separate from the
# single-strategy 5단계 Candidate Review handoff gate.
def _build_saved_mix_validation_evaluation(
    *,
    record: dict[str, Any],
    weighted_bundle: dict[str, Any] | None,
    bundles: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    replay_ready = (
        isinstance(weighted_bundle, dict)
        and isinstance(weighted_bundle.get("summary_df"), pd.DataFrame)
        and not weighted_bundle["summary_df"].empty
        and isinstance(weighted_bundle.get("result_df"), pd.DataFrame)
        and not weighted_bundle["result_df"].empty
    )
    compare_context = dict(record.get("compare_context") or {})
    requested_end = compare_context.get("end")
    actual_end = _weighted_bundle_actual_end(weighted_bundle or {}) if replay_ready else None
    requested_end_ts = pd.to_datetime(requested_end, errors="coerce")
    actual_end_ts = pd.to_datetime(actual_end, errors="coerce")
    shortened_days = (
        (requested_end_ts.date() - actual_end_ts.date()).days
        if pd.notna(requested_end_ts)
        and pd.notna(actual_end_ts)
        and actual_end_ts.date() < requested_end_ts.date()
        else 0
    )

    component_bundles = list(bundles or [])
    component_data_assessments = [
        _build_compare_data_trust_assessment(bundle)
        for bundle in component_bundles
    ]
    cadence_alignments = [
        dict(assessment.get("cadence_alignment") or {})
        for assessment in component_data_assessments
        if assessment.get("cadence_alignment")
    ]
    data_rows = list((weighted_bundle or {}).get("component_data_trust_rows") or [])
    has_component_error = any(str(row.get("Price Freshness") or "").strip().lower() == "error" for row in data_rows)
    has_cadence_aligned_gap = bool(shortened_days > 31 and cadence_alignments)
    has_component_review = shortened_days > 0 or any(
        str(row.get("Interpretation") or "").strip() not in {"", "-", "눈에 띄는 데이터 이슈 없음"}
        or _safe_int_value(row.get("Warnings")) > 0
        or _safe_int_value(row.get("Excluded Tickers")) > 0
        or _safe_int_value(row.get("Malformed Tickers")) > 0
        for row in data_rows
    )
    if not replay_ready:
        data_status = "FAIL"
        data_score = 0.0
        data_judgment = "replay 결과 없음"
    elif has_component_error:
        data_status = "FAIL"
        data_score = 0.0
        data_judgment = "구성 전략 데이터에 error가 있음"
    elif has_cadence_aligned_gap:
        data_status = "CADENCE ALIGNED"
        data_score = 1.5
        data_judgment = "구성 전략 결과 종료일 차이는 정상 cadence 범위로 보임"
    elif has_component_review:
        data_status = "REVIEW"
        data_score = 1.0
        data_judgment = "구성 전략 기간 / warning 확인 필요"
    else:
        data_status = "PASS"
        data_score = 2.0
        data_judgment = "구성 전략 데이터 조건이 깨끗함"

    real_money_missing: list[str] = []
    real_money_blocked: list[str] = []
    for bundle in component_bundles:
        meta = dict(bundle.get("meta") or {})
        strategy_name = str(bundle.get("strategy_name") or meta.get("strategy_name") or "-")
        promotion = str(meta.get("promotion_decision") or "").strip().lower()
        deployment = str(meta.get("deployment_readiness_status") or "").strip().lower()
        if not meta.get("real_money_hardening"):
            real_money_missing.append(strategy_name)
        if promotion == "hold" or deployment == "blocked":
            real_money_blocked.append(strategy_name)
    if real_money_blocked:
        real_money_status = "FAIL"
        real_money_score = 0.0
        real_money_judgment = "Real-Money blocker가 있는 구성 전략 포함"
    elif real_money_missing:
        real_money_status = "REVIEW"
        real_money_score = 1.0
        real_money_judgment = "Real-Money 정보가 없는 구성 전략 포함"
    elif component_bundles:
        real_money_status = "PASS"
        real_money_score = 2.0
        real_money_judgment = "구성 전략 Real-Money gate가 막지 않음"
    else:
        real_money_status = "REVIEW"
        real_money_score = 1.0
        real_money_judgment = "구성 전략 replay 정보 확인 필요"

    workflow_references = _find_saved_mix_workflow_references(record)
    workflow_status = "PASS" if workflow_references else "NOT RECORDED"
    workflow_score = 3.0 if workflow_references else 0.0
    workflow_judgment = (
        "proposal / final review workflow 기록 있음"
        if workflow_references
        else "saved mix setup만 있고 5~10단계 workflow registry 기록은 아직 없음"
    )

    replay_score = 3.0 if replay_ready else 0.0
    score = round(replay_score + data_score + real_money_score + workflow_score, 1)
    if not replay_ready or data_status == "FAIL" or real_money_status == "FAIL":
        stage_status = "BLOCKED"
        verdict = "Replay 또는 구성 전략 gate를 먼저 해결해야 합니다."
        tone = "error"
    elif workflow_status == "PASS":
        stage_status = "WORKFLOW RECORDED"
        verdict = "저장 mix가 workflow registry에서도 확인됩니다."
        tone = "success"
    else:
        stage_status = "REPLAY OK"
        verdict = "성과 replay는 가능하지만, 5~10단계 workflow 통과 기록은 아직 없습니다."
        tone = "warning"

    criteria_rows = [
        {
            "기준": "Mix Replay",
            "상태": "PASS" if replay_ready else "FAIL",
            "현재 값": "weighted result 생성됨" if replay_ready else "weighted result 없음",
            "점수": f"{replay_score:g} / 3",
            "판단": "저장된 compare context와 weights로 다시 실행 가능" if replay_ready else "Mix 재실행 및 검증을 다시 실행해야 함",
        },
        {
            "기준": "Mix Data Trust",
            "상태": data_status,
            "현재 값": f"actual_end={actual_end or '-'}, requested_end={requested_end or '-'}",
            "점수": f"{data_score:g} / 2",
            "판단": (
                "; ".join(str(item.get("judgment")) for item in cadence_alignments if item.get("judgment"))
                if cadence_alignments
                else
                f"{data_judgment}, {shortened_days}일 짧음"
                if shortened_days
                else data_judgment
            ),
        },
        {
            "기준": "Component Real-Money",
            "상태": real_money_status,
            "현재 값": real_money_judgment,
            "점수": f"{real_money_score:g} / 2",
            "판단": ", ".join(real_money_blocked or real_money_missing) or "특이사항 없음",
        },
        {
            "기준": "Workflow Registry",
            "상태": workflow_status,
            "현재 값": f"{len(workflow_references)}개 참조",
            "점수": f"{workflow_score:g} / 3",
            "판단": workflow_judgment,
        },
    ]

    return {
        "score": score,
        "stage_status": stage_status,
        "verdict": verdict,
        "tone": tone,
        "criteria_rows": criteria_rows,
        "workflow_references": workflow_references,
        "data_rows": data_rows,
        "actual_end": actual_end,
        "requested_end": requested_end,
        "shortened_days": shortened_days,
        "cadence_alignments": cadence_alignments,
    }

# Extract the replay period from a result bundle so a saved mix proposal can
# preserve the exact data window it was rebuilt from.
def _bundle_result_period(bundle: dict[str, Any]) -> dict[str, str | None]:
    result_df = bundle.get("result_df")
    if not isinstance(result_df, pd.DataFrame) or result_df.empty or "Date" not in result_df.columns:
        meta = dict(bundle.get("meta") or {})
        return {"start": meta.get("start"), "end": meta.get("actual_result_end") or meta.get("end")}
    dates = pd.to_datetime(result_df["Date"], errors="coerce").dropna()
    if dates.empty:
        return {"start": None, "end": None}
    return {"start": str(dates.min().date()), "end": str(dates.max().date())}

# Normalize a result summary row into the compact evidence fields used by
# saved-mix validation and Portfolio Proposal prefill.
def _bundle_summary_snapshot(bundle: dict[str, Any]) -> dict[str, Any]:
    summary_df = bundle.get("summary_df")
    if not isinstance(summary_df, pd.DataFrame) or summary_df.empty:
        return {}
    row = dict(summary_df.iloc[0].to_dict())
    return {
        "name": row.get("Name"),
        "cagr": row.get("CAGR"),
        "mdd": row.get("Maximum Drawdown"),
        "sharpe": row.get("Sharpe Ratio"),
        "end_balance": row.get("End Balance"),
    }

# Create stable id fragments for saved-mix synthetic component identifiers.
def _saved_mix_slug(value: Any) -> str:
    raw = str(value or "").strip().lower()
    cleaned = "".join(char if char.isalnum() else "_" for char in raw)
    return "_".join(part for part in cleaned.split("_") if part) or "saved_mix"

# Suggest a proposal role from the saved weight distribution without changing
# the user's stored weights.
def _saved_mix_component_role(strategy_name: str, weight: float, max_weight: float) -> str:
    if weight == max_weight:
        return "core_anchor"
    if "risk" in strategy_name.lower() or "bond" in strategy_name.lower():
        return "defensive_sleeve"
    return "diversifier"

# Build the cross-panel payload that turns a replayed saved mix into a Portfolio
# Proposal draft source rather than a Candidate Review handoff.
def _build_saved_mix_proposal_prefill_payload(record: dict[str, Any]) -> dict[str, Any]:
    weighted_bundle = dict(st.session_state.get("backtest_weighted_bundle") or {})
    bundles = list(st.session_state.get("backtest_compare_bundles") or [])
    compare_context = dict(record.get("compare_context") or {})
    portfolio_context = dict(record.get("portfolio_context") or {})
    source_context = dict(record.get("source_context") or {})
    upstream_context = dict(source_context.get("compare_source_context") or {})
    registry_ids = list(upstream_context.get("registry_ids") or [])
    candidate_titles = list(upstream_context.get("candidate_titles") or [])
    weights_percent = [float(weight) for weight in list(portfolio_context.get("weights_percent") or [])]
    strategy_names = list(portfolio_context.get("strategy_names") or compare_context.get("selected_strategies") or [])
    max_weight = max(weights_percent, default=0.0)
    override_map = dict(compare_context.get("strategy_overrides") or {})

    components: list[dict[str, Any]] = []
    for idx, strategy_name in enumerate(strategy_names):
        bundle = next((item for item in bundles if str(item.get("strategy_name") or "") == str(strategy_name)), {})
        meta = dict(bundle.get("meta") or {})
        summary = _bundle_summary_snapshot(bundle)
        data_assessment = _build_compare_data_trust_assessment(bundle) if bundle else {}
        weight = weights_percent[idx] if idx < len(weights_percent) else 0.0
        registry_id = str(registry_ids[idx]) if idx < len(registry_ids) else ""
        if not registry_id:
            registry_id = f"saved_mix_component_{_saved_mix_slug(record.get('portfolio_id'))}_{_saved_mix_slug(strategy_name)}"
        contract = {
            "start": compare_context.get("start"),
            "end": compare_context.get("end"),
            "timeframe": compare_context.get("timeframe"),
            "option": compare_context.get("option"),
            **dict(override_map.get(strategy_name) or {}),
        }
        title = str(candidate_titles[idx]) if idx < len(candidate_titles) else str(strategy_name)
        components.append(
            {
                "registry_id": registry_id,
                "title": title,
                "strategy_family": _saved_mix_slug(strategy_name),
                "strategy_name": strategy_name,
                "candidate_role": "saved_mix_component",
                "proposal_role": _saved_mix_component_role(str(strategy_name), weight, max_weight),
                "target_weight": weight,
                "weight_reason": "Saved Mix에서 재생성한 목표 비중",
                "data_trust_status": str(data_assessment.get("gate_status") or "warning"),
                "pre_live_status": "saved_mix_replay",
                "promotion": meta.get("promotion_decision"),
                "shortlist": meta.get("shortlist_status"),
                "deployment": meta.get("deployment_readiness_status"),
                "cagr": summary.get("cagr"),
                "mdd": summary.get("mdd"),
                "period": _bundle_result_period(bundle),
                "contract": contract,
                "benchmark": meta.get("benchmark_ticker") or contract.get("benchmark_ticker") or "-",
                "universe": ",".join(str(ticker) for ticker in list(contract.get("tickers") or [])) or str(contract.get("preset_name") or "-"),
                "compare_evidence": {
                    "source_kind": "saved_mix_replay",
                    "saved_portfolio_id": record.get("portfolio_id"),
                    "saved_portfolio_name": record.get("name"),
                    "date_policy": portfolio_context.get("date_policy"),
                },
                "open_candidate_blockers": [],
            }
        )

    return {
        "source_kind": "saved_portfolio_mix",
        "saved_portfolio_id": record.get("portfolio_id"),
        "saved_portfolio_name": record.get("name"),
        "description": record.get("description"),
        "compare_context": compare_context,
        "portfolio_context": portfolio_context,
        "source_context": source_context,
        "weighted_summary": _bundle_summary_snapshot(weighted_bundle),
        "weighted_period": _bundle_result_period(weighted_bundle),
        "components": components,
    }

# Render the saved-mix stop/go board in the saved portfolio workspace.
def _render_saved_mix_validation_board(record: dict[str, Any]) -> None:
    weighted_bundle = st.session_state.get("backtest_weighted_bundle")
    bundles = st.session_state.get("backtest_compare_bundles") or []
    evaluation = _build_saved_mix_validation_evaluation(
        record=record,
        weighted_bundle=weighted_bundle,
        bundles=bundles,
    )
    with st.container(border=True):
        st.markdown("### Portfolio Mix 검증 보드")
        st.caption(
            "이 보드는 저장 mix 자체를 다시 열었을 때 보는 검증입니다. "
            "개별 전략을 Candidate Review로 보내는 5단계 보드와 분리해서, mix replay 가능 여부와 workflow 기록 여부를 봅니다."
        )
        metric_cols = st.columns([0.2, 0.18, 0.18, 0.44], gap="small")
        metric_cols[0].metric("Mix 상태", str(evaluation["stage_status"]))
        metric_cols[1].metric("Readiness", f"{float(evaluation['score']):.1f} / 10")
        metric_cols[2].metric("Blockers", sum(1 for row in evaluation["criteria_rows"] if row["상태"] == "FAIL"))
        with metric_cols[3]:
            st.caption("판정")
            st.markdown(f"**{evaluation['verdict']}**")
            st.caption("다음 행동")
            if evaluation["stage_status"] == "WORKFLOW RECORDED":
                st.markdown("Portfolio Proposal / Final Review 쪽 기록을 열어 실제 통과 판단을 이어서 확인합니다.")
            elif evaluation["tone"] == "warning":
                st.markdown("이 mix를 실제 workflow 후보로 쓰려면 Portfolio Proposal 또는 Final Review 단계에 별도로 기록해야 합니다.")
            else:
                st.markdown("Replay result, Data Trust, Real-Money blocker를 먼저 다시 확인합니다.")
        st.progress(max(0.0, min(float(evaluation["score"]) / 10.0, 1.0)))
        message = (
            f"{evaluation['verdict']} "
            "Saved mix는 reusable setup이므로, 이 보드에서 workflow registry 기록 유무를 따로 확인합니다."
        )
        if evaluation["tone"] == "success":
            st.success(message)
        elif evaluation["tone"] == "warning":
            st.warning(message)
        else:
            st.error(message)
        if evaluation["tone"] != "error":
            st.info(
                "이 saved mix는 이미 비중이 정해진 포트폴리오 조합입니다. "
                "따라서 단일 전략 후보를 다루는 Candidate Review로 보내지 않고, "
                "Portfolio Proposal에서 포트폴리오 초안으로 기록합니다."
            )
            if st.button(
                "Practical Validation으로 보내기",
                key=f"use_saved_mix_in_portfolio_proposal_{record.get('portfolio_id')}",
                use_container_width=True,
            ):
                prefill = _build_saved_mix_proposal_prefill_payload(record)
                source = build_selection_source_from_saved_mix_prefill(prefill)
                queue_practical_validation_source(source, persist=True)
                st.session_state.portfolio_proposal_saved_mix_prefill = prefill
                st.session_state.portfolio_proposal_saved_mix_notice = (
                    f"Saved Mix `{record.get('name')}`를 Practical Validation source로 저장했습니다. "
                    "이 경로는 Candidate Review / legacy Proposal 저장을 필수로 요구하지 않습니다."
                )
                st.rerun()
        st.dataframe(pd.DataFrame(evaluation["criteria_rows"]), use_container_width=True, hide_index=True)
        if evaluation["workflow_references"]:
            with st.expander("Workflow Registry References", expanded=False):
                st.dataframe(pd.DataFrame(evaluation["workflow_references"]), use_container_width=True, hide_index=True)
        if evaluation.get("cadence_alignments"):
            with st.expander("Cadence-Aligned Data Trust Notes", expanded=False):
                st.dataframe(pd.DataFrame(evaluation["cadence_alignments"]), use_container_width=True, hide_index=True)
        if evaluation["data_rows"]:
            with st.expander("Component Data Trust Snapshot", expanded=False):
                st.dataframe(pd.DataFrame(evaluation["data_rows"]), use_container_width=True, hide_index=True)

# Render the stage-5 stop/go board before a strategy is handed off to Candidate Review.
def _render_candidate_draft_readiness_box(bundles: list[dict[str, Any]]) -> None:
    if not bundles:
        return

    strategy_names = [str(bundle.get("strategy_name") or "") for bundle in bundles if bundle.get("strategy_name")]
    if not strategy_names:
        return

    default_strategy = st.session_state.get("compare_focus_strategy")
    if default_strategy not in strategy_names:
        best_bundle = max(
            bundles,
            key=lambda bundle: _safe_summary_metric(bundle, "End Balance") or float("-inf"),
        )
        default_strategy = str(best_bundle.get("strategy_name") or strategy_names[0])
    default_index = strategy_names.index(default_strategy) if default_strategy in strategy_names else 0

    with st.container(border=True):
        st.markdown("##### 개별 후보 5단계 Compare 검증 보드")
        st.caption(
            "이 보드는 개별 전략 후보의 5단계 stop/go 판단입니다. "
            "mix 자체 검증은 `저장된 비중 조합` 화면의 Portfolio Mix 검증 보드에서 확인합니다."
        )
        candidate_strategy = st.selectbox(
            "5단계에서 검증할 개별 후보",
            options=strategy_names,
            index=default_index,
            key="compare_candidate_draft_readiness_strategy",
            help="Compare에 올린 개별 전략 중 Candidate Review로 보낼 후보를 고릅니다. 비중 mix는 Portfolio Proposal 경로를 사용합니다.",
        )
        evaluation = _build_candidate_draft_readiness_evaluation(
            bundles,
            candidate_strategy=candidate_strategy,
        )
        score = float(evaluation["score"])
        tone = str(evaluation["tone"])
        data_gate = dict(evaluation.get("data_trust_gate") or {})
        data_gate_status = str(data_gate.get("status") or "-").upper()
        stage_status = str(evaluation.get("stage_status") or "-")

        metric_cols = st.columns([0.18, 0.18, 0.2, 0.44], gap="small")
        metric_cols[0].metric("5단계 판정", stage_status)
        metric_cols[1].metric("Readiness", f"{score:.1f} / 10")
        metric_cols[2].metric("Data Trust", data_gate_status)
        with metric_cols[3]:
            st.caption("Candidate")
            st.markdown(f"**{candidate_strategy}**")
            st.markdown(f"**{evaluation['verdict']}**")
            st.caption("다음 행동")
            st.markdown(str(evaluation["next_action"]))
        st.progress(max(0.0, min(score / 10.0, 1.0)))
        st.caption(
            "점수 기준: `8.0점 이상`은 PASS, `6.5점 이상`은 CONDITIONAL, 그 아래 또는 hard blocker가 있으면 FAIL입니다. "
            "Data Trust는 점수를 강제로 깎는 cap이 아니라 별도 gate로 표시합니다."
        )

        message = f"{evaluation['verdict']}: Compare 결과, Data Trust, Real-Money gate, 상대 비교 근거를 합산했습니다."
        if tone == "success":
            st.success(message)
        elif tone == "warning":
            st.warning(message)
        else:
            st.error(message)

        if data_gate.get("status") == "warning":
            warning_text = ", ".join(str(item) for item in data_gate.get("reasons") or []) or str(data_gate.get("judgment"))
            st.warning(f"Data Trust Warning: {warning_text}")
        elif data_gate.get("status") == "blocked":
            blocked_text = ", ".join(str(item) for item in data_gate.get("reasons") or []) or str(data_gate.get("judgment"))
            st.error(f"Data Trust Blocked: {blocked_text}")

        st.markdown("**5단계 검증 기준**")
        st.dataframe(pd.DataFrame(evaluation["criteria_rows"]), use_container_width=True, hide_index=True)

        if evaluation["blocking_reasons"]:
            st.caption("막는 항목: " + ", ".join(f"`{item}`" for item in evaluation["blocking_reasons"]))
        elif evaluation["review_reasons"]:
            st.caption("Review Note에 같이 남길 항목: " + ", ".join(f"`{item}`" for item in evaluation["review_reasons"]))
        else:
            st.caption("6단계 Candidate Review로 넘기기 전에 막는 핵심 항목은 보이지 않습니다.")

        st.markdown("##### 다음 행동")
        action_cols = st.columns([0.34, 0.66], gap="small")
        with action_cols[0]:
            if st.button(
                "Practical Validation으로 보내기",
                key="compare_send_candidate_draft",
                disabled=not bool(evaluation["can_send_to_candidate_draft"]),
                use_container_width=True,
            ):
                selected_bundle = evaluation.get("selected_bundle")
                if selected_bundle is not None:
                    draft = _candidate_review_draft_from_bundle(selected_bundle)
                    draft["source_kind"] = "compare_focused_strategy"
                    draft["compare_readiness_evaluation"] = {
                        "score": evaluation["score"],
                        "verdict": evaluation["verdict"],
                        "criteria_rows": evaluation["criteria_rows"],
                        "rank_rows": evaluation["rank_rows"],
                    }
                    _queue_candidate_review_draft(draft)
                    st.rerun()
        with action_cols[1]:
            st.caption(
                "이 버튼을 누르면 선택한 개별 전략이 Clean V2 source로 저장되고 Practical Validation에서 실전 검증을 이어갑니다. "
                "아직 최종 선택이나 live approval은 아닙니다."
            )

        rank_rows = evaluation.get("rank_rows") or []
        if rank_rows:
            with st.expander("상대 비교 순위 보기", expanded=False):
                st.dataframe(pd.DataFrame(rank_rows), use_container_width=True, hide_index=True)

        with st.expander("이번 Compare 구성 보기", expanded=False):
            st.dataframe(pd.DataFrame(evaluation["overview_rows"]), use_container_width=True, hide_index=True)

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
                "Benchmark": meta.get("benchmark_label") if meta.get("benchmark_contract") == STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT else meta.get("benchmark_ticker") or meta.get("benchmark_label"),
                "Guardrail Ref": _resolve_guardrail_reference_ticker_value(meta),
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

    st.markdown("### 개별 전략 비교 상세")
    st.caption(
        "5단계 Compare의 상세 근거입니다. Summary, Data Trust, Real-Money / Guardrail, "
        "Strategy Highlights, Focused Strategy를 탭별로 확인합니다."
    )
    if any((bundle.get("meta") or {}).get("universe_contract") == HISTORICAL_DYNAMIC_PIT_UNIVERSE for bundle in bundles):
        st.info(
            "This compare run includes `Historical Dynamic PIT Universe` strategies. "
            "In Phase 10 first pass, annual strict strategies rebuild approximate rebalance-date membership, so "
            "`Dynamic Candidate Pool`, `Membership Avg`, and `Membership Range` help explain why static and dynamic results diverge."
        )
    _render_candidate_draft_readiness_box(bundles)

    summary_tab, data_trust_tab, real_money_guardrail_tab, balance_tab, drawdown_tab, return_tab, highlights_tab, focus_tab, meta_tab = st.tabs(
        [
            "Summary Compare",
            "Data Trust",
            "Real-Money / Guardrail",
            "Equity Overlay",
            "Drawdown Overlay",
            "Return Overlay",
            "Strategy Highlights",
            "Focused Strategy",
            "Execution Meta",
        ]
    )

    with summary_tab:
        st.dataframe(summary_df, use_container_width=True)

    with data_trust_tab:
        _render_strategy_data_trust_snapshot(
            bundles,
            title="Compare Data Trust Snapshot",
            caption=(
                "Compare 결과를 해석하기 전에 각 전략의 요청 종료일, 실제 결과 종료일, "
                "가격 최신성, 제외 ticker, 결측 row를 함께 확인합니다."
            ),
        )

    with real_money_guardrail_tab:
        _render_real_money_guardrail_parity_snapshot(
            [
                {
                    "strategy_name": bundle.get("strategy_name"),
                    "strategy_key": dict(bundle.get("meta") or {}).get("strategy_key"),
                    "data": dict(bundle.get("meta") or {}),
                }
                for bundle in bundles
            ],
            title="Compare Real-Money / Guardrail Scope",
            caption=(
                "이 표는 selected strategies를 같은 compare 결과 안에서 해석할 때, "
                "어떤 전략은 full strict Real-Money 검증 대상이고 어떤 전략은 prototype 또는 ETF first-pass인지 구분합니다."
            ),
        )

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
        st.caption(
            "이 표는 compare 전용 요약 surface입니다. "
            "single run의 `Real-Money` 탭과 같은 것이 아니라, 여러 전략의 high / low / end state와 best / worst period를 한 번에 훑기 위한 표입니다. "
            "한 전략을 더 자세히 보려면 `Focused Strategy` 안의 `Real-Money Contract`로 내려가면 됩니다."
        )
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

        if focused_bundle["meta"].get("strategy_key") in SNAPSHOT_SELECTION_HISTORY_STRATEGY_KEYS:
            st.divider()
            st.markdown("##### Selection History & Interpretation")
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
    compare_source_context: dict[str, Any] | None = None,
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
    component_data_trust_rows = _build_strategy_data_trust_rows(bundles)
    weighted_bundle["component_contribution_amount_df"] = contribution_amount_df
    weighted_bundle["component_contribution_share_df"] = contribution_share_df
    weighted_bundle["component_data_trust_rows"] = component_data_trust_rows
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
            "component_data_trust_rows": component_data_trust_rows,
            "compare_source_context": dict(compare_source_context or {}),
        }
    )
    return weighted_bundle

def _build_saved_portfolio_display_rows(saved_portfolios: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for item in saved_portfolios:
        compare_context = item.get("compare_context") or {}
        portfolio_context = item.get("portfolio_context") or {}
        source_context = item.get("source_context") or {}
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
                "Source": source_context.get("source_label") or _compare_source_kind_label(source_context.get("source_kind")),
                "Description": item.get("description"),
            }
        )
    return pd.DataFrame(rows)

def _saved_portfolio_value_is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, (float, np.floating)) and pd.isna(value):
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True

def _format_saved_portfolio_value(value: Any) -> str:
    if not _saved_portfolio_value_is_present(value):
        return "-"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple, set)):
        items = [str(item) for item in list(value)]
        preview = ", ".join(items[:8])
        if len(items) > 8:
            preview += f" 외 {len(items) - 8}개"
        return preview
    if isinstance(value, dict):
        text = json.dumps(value, ensure_ascii=False, default=str)
    else:
        text = str(value)
    if len(text) > 140:
        return text[:137] + "..."
    return text

def _saved_portfolio_field_summary(source: dict[str, Any], fields: list[str]) -> str:
    pairs = [
        f"{field}={_format_saved_portfolio_value(source.get(field))}"
        for field in fields
        if _saved_portfolio_value_is_present(source.get(field))
    ]
    return " / ".join(pairs) if pairs else "-"

def _saved_portfolio_present_count(source: dict[str, Any], fields: list[str]) -> int:
    return sum(1 for field in fields if _saved_portfolio_value_is_present(source.get(field)))

def _saved_portfolio_strategy_expected_fields(strategy_name: str) -> tuple[list[str], str]:
    if strategy_name.endswith("(Strict Annual)") or strategy_name.endswith("(Strict Quarterly Prototype)"):
        fields = [
            "universe_mode",
            "preset_name",
            "tickers",
            "top_n",
            "rebalance_interval",
            "factor_freq",
            "snapshot_mode",
            "quality_factors",
            "value_factors",
            "universe_contract",
            "dynamic_target_size",
            "trend_filter_enabled",
            "trend_filter_window",
            "weighting_mode",
            "rejected_slot_handling_mode",
            "risk_off_mode",
            "defensive_tickers",
            "market_regime_enabled",
            "benchmark_contract",
            "benchmark_ticker",
            "guardrail_reference_ticker",
            "underperformance_guardrail_enabled",
            "drawdown_guardrail_enabled",
        ]
        return fields, "strict factor 전략은 cadence, factor, universe, overlay, portfolio handling, guardrail 설정이 replay 의미를 결정합니다."

    if strategy_name == "Global Relative Strength":
        fields = [
            "universe_mode",
            "preset_name",
            "tickers",
            "cash_ticker",
            "top",
            "interval",
            "score_lookback_months",
            "score_return_columns",
            "score_weights",
            "trend_filter_window",
            "min_price_filter",
            "transaction_cost_bps",
            "benchmark_ticker",
        ]
        return fields, "GRS는 score horizon / weight, cash ticker, trend window가 replay 의미를 결정합니다."

    if strategy_name == "GTAA":
        fields = [
            "universe_mode",
            "preset_name",
            "tickers",
            "top",
            "interval",
            "score_lookback_months",
            "score_return_columns",
            "score_weights",
            "trend_filter_window",
            "risk_off_mode",
            "defensive_tickers",
            "market_regime_enabled",
            "crash_guardrail_enabled",
            "benchmark_ticker",
        ]
        return fields, "GTAA는 score, risk-off, defensive sleeve, crash guardrail 설정이 replay 의미를 결정합니다."

    if strategy_name == "Risk Parity Trend":
        fields = [
            "rebalance_interval",
            "vol_window",
            "min_price_filter",
            "transaction_cost_bps",
            "benchmark_ticker",
            "underperformance_guardrail_enabled",
            "drawdown_guardrail_enabled",
        ]
        return fields, "Risk Parity Trend는 vol window와 ETF operability / guardrail 입력을 같이 확인합니다."

    if strategy_name == "Dual Momentum":
        fields = [
            "top",
            "rebalance_interval",
            "min_price_filter",
            "transaction_cost_bps",
            "benchmark_ticker",
            "underperformance_guardrail_enabled",
            "drawdown_guardrail_enabled",
        ]
        return fields, "Dual Momentum은 top, cadence, ETF operability / guardrail 입력을 같이 확인합니다."

    if strategy_name == "Equal Weight":
        fields = [
            "universe_mode",
            "preset_name",
            "tickers",
            "rebalance_interval",
            "min_price_filter",
            "transaction_cost_bps",
            "benchmark_ticker",
            "promotion_min_etf_aum_b",
            "promotion_max_bid_ask_spread_pct",
        ]
        return fields, "Equal Weight는 ticker universe, cadence, ETF operability / benchmark 입력을 같이 확인합니다."

    return ["universe_mode", "preset_name", "tickers", "top", "rebalance_interval"], "전략별 핵심 override가 저장됐는지 확인합니다."

def _build_saved_portfolio_replay_parity_rows(record: dict[str, Any]) -> pd.DataFrame:
    compare_context = dict(record.get("compare_context") or {})
    portfolio_context = dict(record.get("portfolio_context") or {})
    strategy_overrides = dict(compare_context.get("strategy_overrides") or {})
    selected_strategies = list(compare_context.get("selected_strategies") or [])
    strategy_names = list(portfolio_context.get("strategy_names") or [])
    weights_percent = list(portfolio_context.get("weights_percent") or [])

    rows: list[dict[str, str]] = []
    rows.append(
        {
            "확인 영역": "Compare 공용 입력",
            "저장 상태": "저장됨" if _saved_portfolio_present_count(compare_context, ["start", "end", "timeframe", "option"]) == 4 else "일부 누락",
            "저장된 값": _saved_portfolio_field_summary(compare_context, ["start", "end", "timeframe", "option"]),
            "왜 중요한가": "Replay는 이 기간과 timeframe / option으로 strategy compare를 다시 실행합니다.",
        }
    )
    rows.append(
        {
            "확인 영역": "전략 목록",
            "저장 상태": "저장됨" if selected_strategies else "누락 가능",
            "저장된 값": _format_saved_portfolio_value(selected_strategies),
            "왜 중요한가": "어떤 전략들을 다시 compare하고 weighted portfolio로 섞을지 결정합니다.",
        }
    )
    rows.append(
        {
            "확인 영역": "Weight / Date Alignment",
            "저장 상태": "저장됨" if len(weights_percent) == len(selected_strategies) and weights_percent else "일부 누락",
            "저장된 값": (
                f"strategy_names={_format_saved_portfolio_value(strategy_names)} / "
                f"weights_percent={_format_saved_portfolio_value(weights_percent)} / "
                f"date_policy={_format_saved_portfolio_value(portfolio_context.get('date_policy'))}"
            ),
            "왜 중요한가": "`전략 비교에서 수정하기`와 `Mix 재실행 및 검증`이 같은 weight와 date alignment로 이어지는지 확인합니다.",
        }
    )
    rows.append(
        {
            "확인 영역": "Strategy Override Map",
            "저장 상태": "저장됨" if all(strategy in strategy_overrides for strategy in selected_strategies) else "일부 누락",
            "저장된 값": f"{sum(1 for strategy in selected_strategies if strategy in strategy_overrides)} / {len(selected_strategies)} strategies",
            "왜 중요한가": "전략별 세부 옵션이 없으면 replay가 기본값으로 돌아가 다른 결과가 될 수 있습니다.",
        }
    )

    for strategy_name in selected_strategies:
        override = dict(strategy_overrides.get(strategy_name) or {})
        fields, reason = _saved_portfolio_strategy_expected_fields(strategy_name)
        present = _saved_portfolio_present_count(override, fields)
        status = "저장됨" if present >= max(1, min(4, len(fields))) else "누락 가능"
        if not override:
            status = "누락 가능"
        rows.append(
            {
                "확인 영역": strategy_name,
                "저장 상태": status,
                "저장된 값": _saved_portfolio_field_summary(override, fields),
                "왜 중요한가": reason,
            }
        )

    return pd.DataFrame(rows)

def _build_saved_portfolio_override_summary_rows(record: dict[str, Any]) -> pd.DataFrame:
    compare_context = dict(record.get("compare_context") or {})
    strategy_overrides = dict(compare_context.get("strategy_overrides") or {})
    rows: list[dict[str, Any]] = []
    for strategy_name in list(compare_context.get("selected_strategies") or []):
        override = dict(strategy_overrides.get(strategy_name) or {})
        _, strategy_variant = display_name_to_selection(strategy_name)
        rows.append(
            {
                "Strategy": strategy_name,
                "Variant": strategy_variant or "-",
                "Top / Interval": (
                    f"{override.get('top_n') or override.get('top') or '-'} / "
                    f"{override.get('rebalance_interval') or override.get('interval') or '-'}"
                ),
                "Universe": _format_saved_portfolio_value(
                    override.get("universe_contract") or override.get("preset_name") or override.get("universe_mode")
                ),
                "Cadence / Snapshot": _format_saved_portfolio_value(
                    override.get("factor_freq") or override.get("snapshot_mode") or override.get("score_lookback_months")
                ),
                "Overlay / Handling": _format_saved_portfolio_value(
                    {
                        key: override.get(key)
                        for key in [
                            "trend_filter_enabled",
                            "trend_filter_window",
                            "weighting_mode",
                            "rejected_slot_handling_mode",
                            "risk_off_mode",
                            "market_regime_enabled",
                        ]
                        if key in override
                    }
                ),
                "Benchmark / Guardrail": _format_saved_portfolio_value(
                    {
                        key: override.get(key)
                        for key in [
                            "benchmark_contract",
                            "benchmark_ticker",
                            "guardrail_reference_ticker",
                            "underperformance_guardrail_enabled",
                            "drawdown_guardrail_enabled",
                        ]
                        if key in override
                    }
                ),
            }
        )
    return pd.DataFrame(rows)

def _render_saved_portfolio_replay_parity_snapshot(record: dict[str, Any]) -> None:
    parity_df = _build_saved_portfolio_replay_parity_rows(record)
    if parity_df.empty:
        return

    compare_context = dict(record.get("compare_context") or {})
    portfolio_context = dict(record.get("portfolio_context") or {})
    selected_strategies = list(compare_context.get("selected_strategies") or [])
    weights_percent = list(portfolio_context.get("weights_percent") or [])

    st.markdown("#### 저장된 비중 조합 Replay / 편집 Parity Snapshot")
    st.caption(
        "이 표는 저장된 portfolio mix를 `전략 비교에서 수정하기` 또는 `Mix 재실행 및 검증`으로 다시 열 때 "
        "전략 목록, 공용 기간, strategy-specific override, weight/date alignment가 충분히 남아 있는지 확인하는 표입니다."
    )
    metric_cols = st.columns(4, gap="small")
    metric_cols[0].metric("Strategies", len(selected_strategies))
    metric_cols[1].metric("Weights", len(weights_percent))
    metric_cols[2].metric("Overrides", len(dict(compare_context.get("strategy_overrides") or {})))
    metric_cols[3].metric("Date Policy", portfolio_context.get("date_policy") or "-")
    st.dataframe(parity_df, use_container_width=True, hide_index=True)

    override_df = _build_saved_portfolio_override_summary_rows(record)
    if not override_df.empty:
        with st.expander("Strategy Override Summary", expanded=False):
            st.caption(
                "전략별 저장 override를 사람이 읽기 쉬운 형태로 줄여서 보여줍니다. "
                "정확한 전체 payload는 `Compare Context` 또는 `Raw Record` 탭에서 확인합니다."
            )
            st.dataframe(override_df, use_container_width=True, hide_index=True)
    _render_real_money_guardrail_parity_snapshot(
        [
            {
                "strategy_name": strategy_name,
                "strategy_key": None,
                "data": dict((compare_context.get("strategy_overrides") or {}).get(strategy_name) or {}),
            }
            for strategy_name in selected_strategies
        ],
        title="Saved Portfolio Real-Money / Guardrail Scope",
        caption=(
            "저장 포트폴리오 안의 각 전략이 어떤 Real-Money / Guardrail 범위로 다시 열리는지 확인합니다. "
            "quarterly prototype과 ETF first-pass를 annual strict full surface로 오해하지 않기 위한 표입니다."
        ),
    )

def _run_saved_portfolio_record(record: dict[str, Any]) -> None:
    compare_context = dict(record.get("compare_context") or {})
    source_context = dict(record.get("source_context") or {})
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
        compare_source_context={
            "source_kind": "saved_portfolio",
            "source_label": record.get("name"),
            "saved_portfolio_id": record.get("portfolio_id"),
            "selected_strategies": selected_strategies,
            "weights_percent": weights_percent,
            "upstream_source_context": source_context,
        },
    )

    st.session_state.backtest_compare_bundles = bundles
    st.session_state.backtest_compare_error = None
    st.session_state.backtest_compare_error_kind = None
    st.session_state.backtest_weighted_bundle = weighted_bundle
    st.session_state.backtest_weighted_error = None
    st.session_state.backtest_compare_source_context = {
        "source_kind": "saved_portfolio",
        "source_label": record.get("name"),
        "saved_portfolio_id": record.get("portfolio_id"),
        "selected_strategies": selected_strategies,
        "weights_percent": weights_percent,
        "upstream_source_context": source_context,
    }
    st.session_state.backtest_saved_portfolio_replay_id = str(record.get("portfolio_id") or "")
    st.session_state.backtest_compare_result_notice = None
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
            "strategy_data_trust_rows": _build_strategy_data_trust_rows(bundles),
            "weights_percent": weights_percent,
            "date_policy": portfolio_context.get("date_policy"),
            "saved_portfolio_id": record.get("portfolio_id"),
            "saved_portfolio_name": record.get("name"),
            "compare_source_context": {
                "source_kind": "saved_portfolio",
                "source_label": record.get("name"),
                "saved_portfolio_id": record.get("portfolio_id"),
            },
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
            "weights_percent": weights_percent,
            "component_data_trust_rows": weighted_bundle.get("component_data_trust_rows") or [],
            "saved_portfolio_id": record.get("portfolio_id"),
            "saved_portfolio_name": record.get("name"),
            "compare_source_context": {
                "source_kind": "saved_portfolio",
                "source_label": record.get("name"),
                "saved_portfolio_id": record.get("portfolio_id"),
            },
        },
    )

# Detect whether the latest compare result can offer GTAA / Equal Weight mix shortcuts.
def _weighted_strategy_role_flags(strategy_names: list[str]) -> dict[str, bool]:
    return {
        "gtaa": any("gtaa" in str(name).lower() for name in strategy_names),
        "equal_weight": any("equal weight" in str(name).lower() for name in strategy_names),
    }

# Fill the weight inputs with a common core/satellite GTAA + Equal Weight allocation.
def _apply_gtaa_equal_weight_mix_preset(strategy_names: list[str], *, gtaa_weight: float, equal_weight: float) -> None:
    for strategy_name in strategy_names:
        normalized = str(strategy_name).lower()
        if "gtaa" in normalized:
            st.session_state[f"weight_{strategy_name}"] = float(gtaa_weight)
        elif "equal weight" in normalized:
            st.session_state[f"weight_{strategy_name}"] = float(equal_weight)
        else:
            st.session_state[f"weight_{strategy_name}"] = 0.0
    st.session_state.backtest_weighted_portfolio_notice = (
        f"비중을 GTAA {gtaa_weight:.0f}% / Equal Weight {equal_weight:.0f}%로 채웠습니다."
    )

def _render_weighted_portfolio_builder() -> None:
    bundles = st.session_state.backtest_compare_bundles
    if not bundles or len(bundles) < 2:
        return

    strategy_names = [bundle["strategy_name"] for bundle in bundles]
    compare_source_context = dict(st.session_state.get("backtest_compare_source_context") or {})
    default_weight = round(100 / len(strategy_names), 2)
    _apply_weighted_portfolio_prefill(strategy_names)

    st.markdown("### 2. 비중 포트폴리오 구성")
    st.caption(
        "방금 비교한 전략들을 하나의 mix로 섞습니다. 여기서 만든 결과는 바로 아래에서 확인한 뒤 저장할 수 있습니다."
    )
    _render_compare_source_context_card(compare_source_context, bundles)
    weighted_notice = st.session_state.get("backtest_weighted_portfolio_notice")
    if weighted_notice:
        st.success(weighted_notice)
        st.session_state.backtest_weighted_portfolio_notice = None

    role_flags = _weighted_strategy_role_flags(strategy_names)
    if role_flags["gtaa"] and role_flags["equal_weight"]:
        with st.container(border=True):
            st.markdown("##### 빠른 비중 설정")
            st.caption("GTAA와 Equal Weight를 함께 비교 중이면 자주 쓰는 core/satellite 비중을 한 번에 채울 수 있습니다.")
            quick_cols = st.columns([0.25, 0.25, 0.50], gap="small")
            with quick_cols[0]:
                if st.button("GTAA 70 / EW 30", key="weighted_mix_gtaa70_ew30", use_container_width=True):
                    _apply_gtaa_equal_weight_mix_preset(strategy_names, gtaa_weight=70.0, equal_weight=30.0)
                    st.rerun()
            with quick_cols[1]:
                if st.button("GTAA 50 / EW 50", key="weighted_mix_gtaa50_ew50", use_container_width=True):
                    _apply_gtaa_equal_weight_mix_preset(strategy_names, gtaa_weight=50.0, equal_weight=50.0)
                    st.rerun()
            with quick_cols[2]:
                st.caption("다른 전략이 함께 있으면 빠른 설정 시 해당 전략 비중은 0%로 둡니다.")

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

        total_weight = sum(weights)
        if abs(total_weight - 100.0) <= 0.01:
            st.success("총 비중이 100%입니다. 이 상태로 결과를 만들 수 있습니다.")
        else:
            st.warning(
                f"현재 총 비중은 {total_weight:.1f}%입니다. 실행 시 내부 계산은 정규화되지만, 저장/검토용 mix는 100%로 맞추는 것을 권장합니다."
            )

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
            st.markdown("### 3. 비중 포트폴리오 결과 확인")
            _render_weighted_portfolio_result(weighted_bundle)
            _render_save_weighted_portfolio_panel(weighted_bundle)
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
            compare_source_context=compare_source_context,
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
        context={
            "selected_strategies": strategy_names,
            "date_policy": date_policy,
            "weights_percent": weights,
            "component_data_trust_rows": weighted_bundle.get("component_data_trust_rows") or [],
            "compare_source_context": compare_source_context,
        },
    )
    st.success("Weighted portfolio created.")
    st.markdown("### 3. 비중 포트폴리오 결과 확인")
    _render_weighted_portfolio_result(weighted_bundle)
    _render_save_weighted_portfolio_panel(weighted_bundle)

def _render_current_candidate_bundle_workspace() -> None:
    rows = _load_current_candidate_registry_latest()
    if not rows:
        return

    display_df = _build_current_candidate_registry_rows_for_display(rows)
    anchor_rows = [row for row in rows if str(row.get("record_type") or "") == "current_candidate"]
    near_miss_rows = [row for row in rows if str(row.get("record_type") or "") == "near_miss"]
    label_to_row = {_current_candidate_registry_selection_label(row): row for row in rows}

    st.caption(
        "문서에 정리된 대표 후보를 compare form에 다시 채워 넣는 보조 도구입니다. "
        "바로 compare를 실행하는 버튼은 아니고, 아래 form의 전략/기간/override를 먼저 채웁니다."
    )
    with st.expander("What This Does", expanded=False):
        st.markdown(
            "- `Load Recommended Candidates`: 각 family에서 지금 기준점으로 쓰는 대표 후보를 compare form에 채웁니다.\n"
            "- `Load Lower-MDD Alternatives`: 수익 단계는 조금 약하지만 낙폭은 더 낮았던 대안 후보를 compare form에 채웁니다.\n"
            "- `Pick Specific Candidates Manually`: 현재 registry에 기록된 후보를 직접 보고 골라 compare form에 채웁니다.\n"
            "- 이 목록은 모든 백테스트 결과가 자동으로 쌓이는 공간이 아닙니다.\n"
            "- 현재는 `.note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl`에 active 상태로 기록된 대표 후보와 대안 후보만 보여줍니다.\n"
            "- 같은 family 후보는 한 번에 하나만 compare form으로 불러올 수 있습니다."
        )
    quick_tab, manual_tab = st.tabs(["Quick Bundles", "Pick Manually"])
    with quick_tab:
        st.caption("대표 후보 묶음이나 더 방어적인 대안 묶음을 한 번에 불러옵니다.")
        quick_action_cols = st.columns(2, gap="small")
        with quick_action_cols[0]:
            if st.button("Load Recommended Candidates", key="load_current_candidate_anchors", use_container_width=True):
                try:
                    _queue_current_candidate_compare_prefill(anchor_rows)
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
            st.caption(
                f"현재 기준점으로 쓰는 대표 후보 `{len(anchor_rows)}`개를 한 번에 불러옵니다. "
                "예: Value / Quality / Quality + Value의 현재 main candidate."
            )
        with quick_action_cols[1]:
            if st.button("Load Lower-MDD Alternatives", key="load_current_candidate_near_misses", use_container_width=True):
                try:
                    _queue_current_candidate_compare_prefill(near_miss_rows)
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
            st.caption(
                f"낙폭은 더 낮았지만 승격 단계는 조금 약했던 대안 후보 `{len(near_miss_rows)}`개를 불러옵니다."
            )
    with manual_tab:
        st.caption("특정 후보만 골라 비교하고 싶다면 여기서 직접 선택합니다.")
        st.info(
            "이 목록은 새 백테스트를 돌리거나 Markdown 문서를 만든다고 자동으로 생기지 않습니다. "
            "현재는 `.note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl`에 active 상태로 기록된 후보만 여기 보입니다."
        )
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        selected_labels = st.multiselect(
            "Choose Specific Candidates To Load Into Compare",
            options=list(label_to_row.keys()),
            max_selections=4,
            help="최소 2개 후보를 고르면 compare form으로 바로 불러올 수 있습니다. 같은 family 후보는 한 번에 하나만 지원합니다.",
            key="current_candidate_bundle_selection",
        )
        if st.button("Load Selected Candidates Into Compare", key="load_selected_candidate_bundle", use_container_width=True):
            try:
                selected_rows = [label_to_row[label] for label in selected_labels]
                _queue_current_candidate_compare_prefill(selected_rows)
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

def _build_compare_prefill_summary_rows(payload: dict[str, Any]) -> pd.DataFrame:
    strategy_overrides = dict(payload.get("strategy_overrides") or {})
    rows: list[dict[str, Any]] = []
    for strategy_name in list(payload.get("selected_strategies") or []):
        override = dict(strategy_overrides.get(strategy_name) or {})
        strategy_choice, strategy_variant = display_name_to_selection(strategy_name)
        benchmark_contract = override.get("benchmark_contract")
        benchmark_ticker = override.get("benchmark_ticker")
        guardrail_reference_ticker = _resolve_guardrail_reference_ticker_value(override)
        benchmark_contract_text = (
            _benchmark_contract_value_to_label(benchmark_contract)
            if benchmark_contract
            else "-"
        )
        rows.append(
            {
                "Strategy": strategy_name,
                "Variant": strategy_variant or "-",
                "Top N": override.get("top_n") or override.get("top") or "-",
                "Universe Contract": _universe_contract_value_to_label(override.get("universe_contract")),
                "Benchmark Contract": benchmark_contract_text,
                "Benchmark Ticker": _compare_summary_benchmark_ticker_value(override),
                "Guardrail / Reference Ticker": _compare_summary_guardrail_reference_value(override),
                "Trend Filter": "On" if override.get("trend_filter_enabled") or override.get("trend_filter_window") else "Off",
                "Market Regime": "On" if override.get("market_regime_enabled") else "Off",
                "Weighting Contract": _strict_weighting_mode_value_to_label(
                    override.get("weighting_mode") or STRICT_DEFAULT_WEIGHTING_MODE
                ),
                "Risk-Off Contract": _strict_risk_off_mode_value_to_label(
                    override.get("risk_off_mode") or STRICT_DEFAULT_RISK_OFF_MODE
                ),
            }
        )
    return pd.DataFrame(rows)

def _render_compare_prefill_applied_card(payload: dict[str, Any] | None, source_context: dict[str, Any] | None) -> None:
    payload = dict(payload or {})
    source_context = dict(source_context or {})
    if not payload:
        return

    selected_strategies = list(payload.get("selected_strategies") or [])
    if not selected_strategies:
        return

    start = payload.get("start") or "-"
    end = payload.get("end") or "-"
    option = payload.get("option") or "-"
    timeframe = payload.get("timeframe") or "-"
    source_label = str(source_context.get("source_label") or "-").strip()
    source_kind = str(source_context.get("source_kind") or "").strip()
    candidate_titles = [str(value).strip() for value in list(source_context.get("candidate_titles") or []) if str(value).strip()]

    st.markdown("##### Compare Form Updated")
    if source_kind == "saved_portfolio":
        st.caption(
            "저장된 비중 조합을 편집하기 위해 개별 전략 비교 form을 다시 채웠습니다. "
            "이 화면의 5단계 보드는 개별 전략 후보 검증이고, mix 검증은 `저장된 비중 조합` 화면에서 진행합니다."
        )
    else:
        st.caption(
            "방금 불러온 후보 묶음 기준으로 compare form이 다시 채워졌습니다. "
            "아직 compare를 실행한 것은 아니고, 아래 입력값이 바뀐 상태입니다."
        )
    top_cols = st.columns(3, gap="small")
    with top_cols[0]:
        st.markdown(f"**불러온 방식**  \n`{_compare_source_kind_plain_text(source_context.get('source_kind'))}`")
    with top_cols[1]:
        st.markdown(f"**불러온 묶음 이름**  \n`{source_label or '-'}`")
    with top_cols[2]:
        st.markdown(f"**자동으로 맞춰진 기간**  \n`{start} -> {end}`")
    if candidate_titles:
        st.caption(f"이번에 불러온 후보: `{', '.join(candidate_titles)}`")
    st.caption(
        f"현재 compare form에는 `{', '.join(selected_strategies)}` 전략이 선택되어 있고, "
        f"`Timeframe = {timeframe}`, `Option = {option}`으로 채워져 있습니다."
    )
    summary_df = _build_compare_prefill_summary_rows(payload)
    if not summary_df.empty:
        st.caption("아래 표는 각 전략에 어떤 핵심 설정이 채워졌는지 요약한 것입니다.")
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        if "Candidate Universe Equal-Weight" in summary_df.get("Benchmark Contract", pd.Series(dtype=str)).astype(str).tolist():
            st.caption(
                "여기서 `Candidate Universe Equal-Weight`는 benchmark contract 자체를 뜻합니다. "
                "이 경우 표의 `Benchmark Ticker`가 빈칸이면 direct benchmark ticker가 실제로 쓰이지 않는다는 뜻이고, "
                "`Guardrail / Reference Ticker`는 equal-weight contract에서도 underperformance / drawdown guardrail이 "
                "참고하는 별도 기준 ticker입니다."
            )
        if "Same as Benchmark Ticker" in summary_df.get("Guardrail / Reference Ticker", pd.Series(dtype=str)).astype(str).tolist():
            st.caption(
                "`Same as Benchmark Ticker`는 별도 guardrail ticker를 따로 넣지 않았다는 뜻입니다. "
                "이 경우 guardrail은 `Benchmark Ticker`를 그대로 기준으로 같이 사용합니다."
            )
        if not summary_df.get("Guardrail / Reference Ticker", pd.Series(dtype=str)).astype(str).str.strip().any():
            st.caption(
                "`Guardrail / Reference Ticker`가 빈칸이면 현재 compare에 불러온 전략들에서 "
                "underperformance / drawdown guardrail이 실제로 켜져 있지 않다는 뜻입니다."
            )
    st.markdown("**어디서 확인하면 되나**")
    st.markdown(
        "- 바로 아래 `Strategies`에서 어떤 전략이 선택됐는지 확인\n"
        "- `Compare Period & Shared Inputs`에서 기간, timeframe, option이 어떻게 채워졌는지 확인\n"
        "- `Strategy-Specific Advanced Inputs`에서 strategy별 override를 확인"
    )
    if source_kind == "saved_portfolio":
        st.info(
            "구성 전략을 바꾸거나 weight를 다시 만들 때만 `Run Strategy Comparison`을 실행하세요. "
            "저장된 mix 자체 검증은 `저장된 비중 조합`에서 `Mix 재실행 및 검증`을 사용합니다."
        )
    else:
        st.info("값이 맞으면 `Run Strategy Comparison`을 눌러 실제 compare를 실행하면 됩니다.")

def _format_portfolio_name_weight(weight: float) -> str:
    if abs(float(weight) - round(float(weight))) < 0.0001:
        return f"{int(round(float(weight)))}%"
    return f"{float(weight):.1f}%"

def _suggest_weighted_portfolio_name(weighted_bundle: dict[str, Any]) -> str:
    strategy_names = [
        str(name).strip()
        for name in list(weighted_bundle.get("component_strategy_names") or [])
        if str(name).strip()
    ]
    input_weights = [float(weight) for weight in list(weighted_bundle.get("component_input_weights") or [])]
    normalized_weights = [float(weight) * 100.0 for weight in list(weighted_bundle.get("component_weights") or [])]
    weights = input_weights if len(input_weights) == len(strategy_names) else normalized_weights

    if strategy_names and len(weights) == len(strategy_names):
        return " + ".join(
            f"{strategy_name} {_format_portfolio_name_weight(weight)}"
            for strategy_name, weight in zip(strategy_names, weights)
        )
    if strategy_names:
        return " + ".join(strategy_names)
    return "Weighted Portfolio"

def _weighted_portfolio_name_signature(weighted_bundle: dict[str, Any]) -> str:
    meta = dict(weighted_bundle.get("meta") or {})
    return json.dumps(
        {
            "strategies": list(weighted_bundle.get("component_strategy_names") or []),
            "weights": list(weighted_bundle.get("component_input_weights") or []),
            "date_policy": weighted_bundle.get("date_policy") or meta.get("date_policy"),
            "start": meta.get("start"),
            "end": meta.get("end"),
        },
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )

def _sync_saved_portfolio_name_suggestion(weighted_bundle: dict[str, Any]) -> str:
    suggested_name = _suggest_weighted_portfolio_name(weighted_bundle)
    signature = _weighted_portfolio_name_signature(weighted_bundle)
    if st.session_state.get("saved_portfolio_name_signature") != signature:
        st.session_state["saved_portfolio_name_input"] = suggested_name
        st.session_state["saved_portfolio_name_signature"] = signature
    return suggested_name

# Save the just-built weighted result as a reusable setup, separate from formal registries.
def _render_save_weighted_portfolio_panel(weighted_bundle: dict[str, Any]) -> None:
    compare_bundles = st.session_state.backtest_compare_bundles
    if not compare_bundles or not weighted_bundle:
        return

    compare_source_context = dict(st.session_state.get("backtest_compare_source_context") or {})
    with st.container(border=True):
        st.markdown("#### 저장")
        st.caption(
            "지금 확인한 strategy mix를 다시 열 수 있는 저장 항목으로 남깁니다. "
            "후보 registry가 아니라 재현 가능한 weighted portfolio setup입니다."
        )
        st.caption(f"저장 위치: `{SAVED_PORTFOLIO_FILE}`")
        suggested_name = _sync_saved_portfolio_name_suggestion(weighted_bundle)
        with st.form("save_saved_portfolio_form", clear_on_submit=False):
            portfolio_name = st.text_input(
                "Portfolio Mix Name",
                value=suggested_name or "",
                placeholder="예: GTAA Clean-6 70 + Equal Weight Growth 30",
                help="저장된 비중 조합 화면의 목록에 표시될 이름입니다.",
                key="saved_portfolio_name_input",
            )
            portfolio_description = st.text_area(
                "Memo",
                value="",
                placeholder="이 mix를 왜 저장하는지, 어떤 용도로 다시 볼지 간단히 남깁니다.",
                help="나중에 저장된 mix를 다시 열었을 때 용도를 빠르게 떠올릴 수 있게 해줍니다.",
                key="saved_portfolio_description_input",
            )
            save_submitted = st.form_submit_button("Save Portfolio Mix", use_container_width=True)
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
                        "compare_source_context": compare_source_context,
                    },
                )
                st.session_state.backtest_saved_portfolio_notice = (
                    f"저장된 portfolio mix `{record.get('name')}`를 만들었습니다. `저장된 비중 조합` 화면에서 확인할 수 있습니다."
                )
                st.rerun()
            except Exception as exc:
                st.error(f"Portfolio mix save failed: {exc}")

def _render_saved_portfolio_workspace() -> None:
    st.markdown("### 저장된 비중 조합")
    st.caption(
        "저장한 weighted portfolio mix를 다시 실행하고 mix-level 검증으로 읽습니다. "
        "개별 후보 5단계 검증이 아니라 Portfolio Proposal로 이어지는 비중 조합 작업 공간입니다."
    )

    saved_portfolios = load_saved_portfolios(limit=100)
    if not saved_portfolios:
        st.info("저장된 portfolio mix가 아직 없습니다. `개별 전략 비교`에서 비중 포트폴리오 결과를 만든 뒤 저장할 수 있습니다.")
        st.caption(f"저장 위치: `{SAVED_PORTFOLIO_FILE}`")
        return

    st.caption(f"저장 위치: `{SAVED_PORTFOLIO_FILE}`")
    st.dataframe(_build_saved_portfolio_display_rows(saved_portfolios), use_container_width=True, hide_index=True)

    record_labels = [
        f"{item.get('updated_at') or item.get('saved_at')} | {item.get('name')}"
        for item in saved_portfolios
    ]
    selected_label = st.selectbox(
        "저장된 비중 조합 선택",
        options=record_labels,
        index=0,
        key="saved_portfolio_selected_record",
    )
    selected_record = saved_portfolios[record_labels.index(selected_label)]

    compare_context = selected_record.get("compare_context") or {}
    portfolio_context = selected_record.get("portfolio_context") or {}
    source_context = selected_record.get("source_context") or {}

    _render_saved_portfolio_replay_parity_snapshot(selected_record)

    detail_tabs = st.tabs(["Summary", "Source & Actions", "Compare Context", "Raw Record"])
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
        st.markdown("##### Source")
        st.json(
            {
                "source_kind": source_context.get("compare_source_context", {}).get("source_kind") or source_context.get("created_from"),
                "source_label": source_context.get("compare_source_context", {}).get("source_label"),
                "source_strategy_names": source_context.get("source_strategy_names"),
            }
        )
        st.markdown("##### Next Action")
        st.markdown(
            "- `Mix 재실행 및 검증`: 저장 당시 compare context와 weighted portfolio 구성을 그대로 다시 실행하고 mix 검증 보드를 확인합니다."
        )
        st.markdown(
            "- `전략 비교에서 수정하기`: 저장된 전략 조합, compare 기간, strategy-specific 설정, weight/date alignment를 form에 다시 채워 수정합니다."
        )
        st.markdown("- `조합 삭제`: 더 이상 쓰지 않는 저장 mix를 정리합니다.")
    with detail_tabs[2]:
        left, right = st.columns(2, gap="large")
        with left:
            st.markdown("##### Compare Context")
            st.json(compare_context)
        with right:
            st.markdown("##### Portfolio Context")
            st.json(portfolio_context)
    with detail_tabs[3]:
        st.json(selected_record)

    action_cols = st.columns([0.24, 0.24, 0.20, 0.32], gap="small")
    with action_cols[0]:
        if st.button("Mix 재실행 및 검증", key="saved_portfolio_run", use_container_width=True):
            try:
                with st.spinner("Running saved mix from stored compare context..."):
                    _run_saved_portfolio_record(selected_record)
                st.session_state.backtest_saved_portfolio_notice = (
                    f"저장된 portfolio mix `{selected_record.get('name')}`를 다시 실행했습니다."
                )
                st.rerun()
            except Exception as exc:
                st.error(f"Saved mix run failed: {exc}")
    with action_cols[1]:
        if st.button("전략 비교에서 수정하기", key="saved_portfolio_load_into_compare", use_container_width=True):
            _queue_saved_portfolio_compare_prefill(selected_record)
            st.rerun()
    with action_cols[2]:
        if st.button("조합 삭제", key="saved_portfolio_delete", use_container_width=True):
            if delete_saved_portfolio(str(selected_record.get("portfolio_id") or "")):
                st.session_state.backtest_saved_portfolio_notice = (
                    f"저장된 portfolio mix `{selected_record.get('name')}`를 삭제했습니다."
                )
                st.rerun()
            else:
                st.error("Saved mix delete failed.")
    with action_cols[3]:
        st.caption(
            "`Mix 재실행 및 검증`은 저장된 비중 조합 자체를 평가합니다. "
            "`전략 비교에서 수정하기`는 검증이 아니라 form 편집 / 재구성 진입입니다."
        )

    if _saved_portfolio_replay_matches_selected_record(selected_record):
        st.divider()
        _render_saved_mix_replay_result_card()
        _render_saved_mix_validation_board(selected_record)
        with st.expander("Weighted Portfolio Result 상세", expanded=True):
            weighted_bundle = st.session_state.get("backtest_weighted_bundle")
            if weighted_bundle:
                _render_weighted_portfolio_result(weighted_bundle)
            else:
                st.info("Replay 결과가 아직 없습니다. `Mix 재실행 및 검증`을 다시 실행해 주세요.")
        bundles = st.session_state.get("backtest_compare_bundles") or []
        if bundles:
            with st.expander("구성 전략 참고 Summary", expanded=False):
                overview_rows = _build_compare_strategy_overview_rows(list(bundles))
                if overview_rows:
                    st.dataframe(pd.DataFrame(overview_rows), use_container_width=True, hide_index=True)
                data_rows = _build_strategy_data_trust_rows(list(bundles))
                if data_rows:
                    st.markdown("##### Component Data Trust")
                    st.dataframe(pd.DataFrame(data_rows), use_container_width=True, hide_index=True)

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
    component_data_trust_rows = list(bundle.get("component_data_trust_rows") or [])
    meta = bundle.get("meta") or {}

    summary_tab, data_trust_tab, curve_tab, contribution_tab, balance_tab, periods_tab, table_tab, meta_tab = st.tabs(
        [
            "Summary",
            "Component Data Trust",
            "Equity Curve",
            "Contribution",
            "Balance Extremes",
            "Period Extremes",
            "Result Table",
            "Meta",
        ]
    )

    with summary_tab:
        st.dataframe(bundle["summary_df"], use_container_width=True)
    with data_trust_tab:
        st.caption(
            "Weighted Portfolio 자체는 여러 전략 결과를 섞은 composite입니다. "
            "따라서 먼저 각 구성 전략이 어떤 실제 결과 기간과 데이터 상태에서 계산됐는지 확인합니다."
        )
        if component_data_trust_rows:
            st.dataframe(pd.DataFrame(component_data_trust_rows), use_container_width=True, hide_index=True)
        else:
            st.info("이 weighted portfolio에는 component data trust snapshot이 저장되어 있지 않습니다. 최신 compare 결과에서 다시 생성하면 표시됩니다.")
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

def _bundle_to_saved_strategy_override(bundle: dict[str, Any]) -> dict[str, Any]:
    meta = dict(bundle.get("meta") or {})
    strategy_name = bundle.get("strategy_name")

    if strategy_name == "Equal Weight":
        return {
            "tickers": list(meta.get("tickers") or EQUAL_WEIGHT_PRESETS["Dividend ETFs"]),
            "preset_name": meta.get("preset_name") or "Dividend ETFs",
            "universe_mode": meta.get("universe_mode") or "preset",
            "rebalance_interval": int(meta.get("rebalance_interval") or 12),
            "min_price_filter": float(meta.get("min_price_filter") or ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
            "transaction_cost_bps": float(
                meta.get("transaction_cost_bps") or ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS
            ),
            "promotion_min_etf_aum_b": float(
                meta.get("promotion_min_etf_aum_b") or ETF_OPERABILITY_DEFAULT_MIN_AUM_B
            ),
            "promotion_max_bid_ask_spread_pct": float(
                meta.get("promotion_max_bid_ask_spread_pct") or ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT
            ),
            "benchmark_ticker": meta.get("benchmark_ticker") or ETF_REAL_MONEY_DEFAULT_BENCHMARK,
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
    if strategy_name == "Global Relative Strength":
        return {
            "tickers": list(meta.get("tickers") or GLOBAL_RELATIVE_STRENGTH_DEFAULT_TICKERS),
            "preset_name": meta.get("preset_name") or "Global Relative Strength Core ETF Universe",
            "universe_mode": meta.get("universe_mode") or "preset",
            "cash_ticker": meta.get("cash_ticker") or GLOBAL_RELATIVE_STRENGTH_DEFAULT_CASH_TICKER,
            "top": int(meta.get("top") or GLOBAL_RELATIVE_STRENGTH_DEFAULT_TOP),
            "interval": int(
                meta.get("rebalance_interval") or GLOBAL_RELATIVE_STRENGTH_DEFAULT_SIGNAL_INTERVAL
            ),
            "score_lookback_months": list(
                meta.get("score_lookback_months") or GLOBAL_RELATIVE_STRENGTH_DEFAULT_SCORE_LOOKBACK_MONTHS
            ),
            "score_return_columns": list(
                meta.get("score_return_columns") or GLOBAL_RELATIVE_STRENGTH_SCORE_RETURN_COLUMNS
            ),
            "score_weights": dict(
                meta.get("score_weights") or GLOBAL_RELATIVE_STRENGTH_DEFAULT_SCORE_WEIGHTS
            ),
            "trend_filter_window": int(
                meta.get("trend_filter_window") or GLOBAL_RELATIVE_STRENGTH_DEFAULT_TREND_FILTER_WINDOW
            ),
            "min_price_filter": float(meta.get("min_price_filter") or ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
            "transaction_cost_bps": float(
                meta.get("transaction_cost_bps") or ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS
            ),
            "promotion_min_etf_aum_b": float(
                meta.get("promotion_min_etf_aum_b") or ETF_OPERABILITY_DEFAULT_MIN_AUM_B
            ),
            "promotion_max_bid_ask_spread_pct": float(
                meta.get("promotion_max_bid_ask_spread_pct") or ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT
            ),
            "benchmark_ticker": meta.get("benchmark_ticker") or ETF_REAL_MONEY_DEFAULT_BENCHMARK,
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
    if meta.get("weighting_mode") is not None:
        override["weighting_mode"] = meta.get("weighting_mode")
    if meta.get("rejected_slot_handling_mode") is not None:
        override["rejected_slot_handling_mode"] = meta.get("rejected_slot_handling_mode")
    if meta.get("rejected_slot_fill_enabled") is not None:
        override["rejected_slot_fill_enabled"] = bool(meta.get("rejected_slot_fill_enabled"))
    if meta.get("partial_cash_retention_enabled") is not None:
        override["partial_cash_retention_enabled"] = bool(meta.get("partial_cash_retention_enabled"))
    if meta.get("risk_off_mode") is not None:
        override["risk_off_mode"] = meta.get("risk_off_mode")
    if meta.get("defensive_tickers") is not None:
        override["defensive_tickers"] = list(meta.get("defensive_tickers") or [])
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
    if meta.get("guardrail_reference_ticker") is not None:
        override["guardrail_reference_ticker"] = meta.get("guardrail_reference_ticker")
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

COMPARE_MODE_STRATEGY = "개별 전략 비교"
COMPARE_MODE_SAVED_MIX = "저장된 비중 조합"
LEGACY_COMPARE_MODE_LABELS = {
    "전략 비교": COMPARE_MODE_STRATEGY,
    "저장 Mix 다시 열기": COMPARE_MODE_SAVED_MIX,
}


def _normalize_compare_workspace_mode(value: Any) -> str | None:
    raw = str(value or "").strip()
    if raw in {COMPARE_MODE_STRATEGY, COMPARE_MODE_SAVED_MIX}:
        return raw
    return LEGACY_COMPARE_MODE_LABELS.get(raw)


def _queue_saved_portfolio_compare_prefill(saved_portfolio: dict[str, Any]) -> None:
    compare_context = dict(saved_portfolio.get("compare_context") or {})
    portfolio_context = dict(saved_portfolio.get("portfolio_context") or {})
    source_context = dict(saved_portfolio.get("source_context") or {})
    st.session_state.backtest_compare_prefill_payload = compare_context
    st.session_state.backtest_compare_prefill_pending = True
    st.session_state.backtest_saved_portfolio_replay_id = None
    st.session_state.backtest_compare_workspace_mode_request = COMPARE_MODE_STRATEGY
    st.session_state.backtest_compare_prefill_notice = (
        f"저장된 비중 조합 `{saved_portfolio.get('name')}`의 compare 전략/기간/세부 설정과 "
        "weight/date alignment를 개별 전략 비교 form에 다시 채웠습니다. "
        "이 경로는 mix 검증이 아니라 편집 / 재구성용입니다."
    )
    st.session_state.backtest_compare_source_context = {
        "source_kind": "saved_portfolio",
        "source_label": saved_portfolio.get("name"),
        "saved_portfolio_id": saved_portfolio.get("portfolio_id"),
        "saved_portfolio_name": saved_portfolio.get("name"),
        "selected_strategies": list(compare_context.get("selected_strategies") or []),
        "weights_percent": list(portfolio_context.get("weights_percent") or []),
        "upstream_source_context": source_context,
    }
    st.session_state.backtest_weighted_portfolio_prefill = {
        "strategy_names": list(portfolio_context.get("strategy_names") or []),
        "weights_percent": list(portfolio_context.get("weights_percent") or []),
        "date_policy": portfolio_context.get("date_policy") or "intersection",
    }
    st.session_state.backtest_requested_panel = "Compare & Portfolio Builder"

def _current_candidate_registry_default_compare_override(row: dict[str, Any]) -> dict[str, Any] | None:
    registry_id = str(row.get("registry_id") or "").strip()
    strategy_name = str(row.get("strategy_name") or "").strip()
    if not registry_id or not strategy_name:
        return None

    rejected_slot_fill_enabled, partial_cash_retention_enabled = strict_rejection_handling_mode_to_flags(
        STRICT_DEFAULT_REJECTION_HANDLING_MODE
    )
    common_override: dict[str, Any] = {
        "preset_name": STRICT_ANNUAL_COMPARE_DEFAULT_PRESET,
        "tickers": list(QUALITY_STRICT_PRESETS[STRICT_ANNUAL_COMPARE_DEFAULT_PRESET]),
        "universe_mode": "preset",
        "universe_contract": HISTORICAL_DYNAMIC_PIT_UNIVERSE,
        "rebalance_interval": 1,
        "trend_filter_window": STRICT_TREND_FILTER_DEFAULT_WINDOW,
        "market_regime_enabled": False,
        "market_regime_window": STRICT_MARKET_REGIME_DEFAULT_WINDOW,
        "market_regime_benchmark": STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
        "rejected_slot_handling_mode": STRICT_DEFAULT_REJECTION_HANDLING_MODE,
        "rejected_slot_fill_enabled": rejected_slot_fill_enabled,
        "partial_cash_retention_enabled": partial_cash_retention_enabled,
        "weighting_mode": STRICT_DEFAULT_WEIGHTING_MODE,
        "risk_off_mode": STRICT_DEFAULT_RISK_OFF_MODE,
        "defensive_tickers": list(STRICT_DEFAULT_DEFENSIVE_TICKERS),
        "min_price_filter": ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
        "min_history_months_filter": STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
        "min_avg_dollar_volume_20d_m_filter": STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
        "transaction_cost_bps": ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
        "promotion_min_benchmark_coverage": STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
        "promotion_min_net_cagr_spread": STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
        "promotion_min_liquidity_clean_coverage": STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
        "promotion_max_underperformance_share": STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
        "promotion_min_worst_rolling_excess_return": STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
        "promotion_max_strategy_drawdown": STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
        "promotion_max_drawdown_gap_vs_benchmark": STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
        "underperformance_guardrail_enabled": True,
        "underperformance_guardrail_window_months": STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
        "underperformance_guardrail_threshold": STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
        "drawdown_guardrail_enabled": True,
        "drawdown_guardrail_window_months": STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
        "drawdown_guardrail_strategy_threshold": STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
        "drawdown_guardrail_gap_threshold": STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
    }

    if registry_id == "value_current_anchor_top14_psr":
        return {
            **common_override,
            "top_n": 14,
            "benchmark_contract": STRICT_BENCHMARK_CONTRACT_TICKER,
            "benchmark_ticker": "SPY",
            "trend_filter_enabled": False,
            "value_factors": VALUE_STRICT_DEFAULT_FACTORS + ["psr"],
        }
    if registry_id == "value_lower_mdd_near_miss_pfcr":
        return {
            **common_override,
            "top_n": 14,
            "benchmark_contract": STRICT_BENCHMARK_CONTRACT_TICKER,
            "benchmark_ticker": "SPY",
            "trend_filter_enabled": False,
            "value_factors": VALUE_STRICT_DEFAULT_FACTORS + ["psr", "pfcr"],
        }
    if registry_id == "quality_current_anchor_top12_lqd":
        return {
            **common_override,
            "top_n": 12,
            "benchmark_contract": STRICT_BENCHMARK_CONTRACT_TICKER,
            "benchmark_ticker": "LQD",
            "trend_filter_enabled": True,
            "quality_factors": ["roe", "roa", "cash_ratio", "debt_to_assets"],
        }
    if registry_id == "quality_cleaner_alternative_top12_spy":
        return {
            **common_override,
            "top_n": 12,
            "benchmark_contract": STRICT_BENCHMARK_CONTRACT_TICKER,
            "benchmark_ticker": "SPY",
            "trend_filter_enabled": True,
            "quality_factors": ["roe", "roa", "cash_ratio", "debt_to_assets"],
        }
    if registry_id == "quality_value_current_anchor_top10_por":
        return {
            **common_override,
            "top_n": 10,
            "benchmark_contract": STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT,
            "benchmark_ticker": "SPY",
            "trend_filter_enabled": False,
            "quality_factors": ["roe", "roa", "operating_margin", "asset_turnover", "current_ratio"],
            "value_factors": ["book_to_market", "earnings_yield", "sales_yield", "pcr", "por", "per"],
        }
    if registry_id == "quality_value_lower_mdd_near_miss_top9":
        return {
            **common_override,
            "top_n": 9,
            "benchmark_contract": STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT,
            "benchmark_ticker": "SPY",
            "trend_filter_enabled": False,
            "quality_factors": ["roe", "roa", "operating_margin", "asset_turnover", "current_ratio"],
            "value_factors": ["book_to_market", "earnings_yield", "sales_yield", "pcr", "por", "per"],
        }
    return None

def _normalize_gtaa_registry_risk_off_mode(value: str | None) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in set(GTAA_RISK_OFF_MODE_LABELS.values()):
        return normalized
    if "defensive" in normalized:
        return "defensive_bond_preference"
    return GTAA_DEFAULT_RISK_OFF_MODE

def _current_candidate_registry_contract_compare_override(row: dict[str, Any]) -> dict[str, Any] | None:
    strategy_name = str(row.get("strategy_name") or "").strip()
    contract = dict(row.get("contract") or {})
    if not strategy_name or not contract:
        return None

    if strategy_name == "GTAA":
        tickers = list(contract.get("tickers") or [])
        if not tickers:
            return None
        score_lookback_months = [
            int(months)
            for months in list(contract.get("score_lookback_months") or [])
            if months is not None
        ]
        if not score_lookback_months:
            score_lookback_months = [
                months
                for months in [
                    _gtaa_months_from_return_col(col)
                    for col in list(contract.get("score_return_columns") or GTAA_SCORE_RETURN_COLUMNS)
                ]
                if months is not None
            ]

        override: dict[str, Any] = {
            "tickers": tickers,
            "universe_mode": "manual_tickers",
            "top": int(contract.get("top") or 3),
            "interval": int(contract.get("interval") or contract.get("rebalance_interval") or GTAA_DEFAULT_SIGNAL_INTERVAL),
            "score_lookback_months": score_lookback_months,
            "score_return_columns": [
                _gtaa_return_col_from_months(int(months)) for months in score_lookback_months
            ],
            "score_weights": _build_equal_gtaa_score_weights(score_lookback_months),
            "trend_filter_window": int(contract.get("trend_filter_window") or GTAA_DEFAULT_TREND_FILTER_WINDOW),
            "risk_off_mode": _normalize_gtaa_registry_risk_off_mode(contract.get("risk_off_mode")),
            "defensive_tickers": list(contract.get("defensive_tickers") or GTAA_DEFAULT_DEFENSIVE_TICKERS),
            "market_regime_enabled": bool(contract.get("market_regime_enabled", False)),
            "market_regime_window": int(contract.get("market_regime_window") or STRICT_MARKET_REGIME_DEFAULT_WINDOW),
            "market_regime_benchmark": contract.get("market_regime_benchmark")
            or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
            "crash_guardrail_enabled": bool(contract.get("crash_guardrail_enabled", GTAA_DEFAULT_CRASH_GUARDRAIL_ENABLED)),
            "crash_guardrail_drawdown_threshold": float(
                contract.get("crash_guardrail_drawdown_threshold") or GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD
            ),
            "crash_guardrail_lookback_months": int(
                contract.get("crash_guardrail_lookback_months") or GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS
            ),
            "min_price_filter": float(contract.get("min_price_filter") or ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
            "transaction_cost_bps": float(contract.get("transaction_cost_bps") or ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS),
            "benchmark_ticker": str(contract.get("benchmark_ticker") or ETF_REAL_MONEY_DEFAULT_BENCHMARK).strip().upper(),
            "promotion_min_etf_aum_b": float(contract.get("promotion_min_etf_aum_b") or ETF_OPERABILITY_DEFAULT_MIN_AUM_B),
            "promotion_max_bid_ask_spread_pct": float(
                contract.get("promotion_max_bid_ask_spread_pct") or ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT
            ),
            "underperformance_guardrail_enabled": bool(
                contract.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED)
            ),
            "underperformance_guardrail_window_months": int(
                contract.get("underperformance_guardrail_window_months") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS
            ),
            "underperformance_guardrail_threshold": float(
                contract.get("underperformance_guardrail_threshold") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD
            ),
            "drawdown_guardrail_enabled": bool(
                contract.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED)
            ),
            "drawdown_guardrail_window_months": int(
                contract.get("drawdown_guardrail_window_months") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS
            ),
            "drawdown_guardrail_strategy_threshold": float(
                contract.get("drawdown_guardrail_strategy_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD
            ),
            "drawdown_guardrail_gap_threshold": float(
                contract.get("drawdown_guardrail_gap_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD
            ),
        }
        if contract.get("preset_name"):
            override["preset_name"] = contract.get("preset_name")
            override["universe_mode"] = contract.get("universe_mode") or "preset"
        return override

    return None

def _current_candidate_registry_row_to_compare_prefill(row: dict[str, Any]) -> dict[str, Any] | None:
    compare_prefill = dict(row.get("compare_prefill") or {})
    strategy_name = str(compare_prefill.get("strategy_name") or row.get("strategy_name") or "").strip()
    if not strategy_name:
        return None

    execution_context = dict(row.get("execution_context") or {})
    strategy_override = dict(compare_prefill.get("strategy_override") or {})
    if not strategy_override:
        strategy_override = _current_candidate_registry_default_compare_override(row) or {}
    if not strategy_override:
        strategy_override = _current_candidate_registry_contract_compare_override(row) or {}
    if not strategy_override:
        return None
    if not strategy_override.get("guardrail_reference_ticker"):
        strategy_override["guardrail_reference_ticker"] = _resolve_guardrail_reference_ticker_value(
            strategy_override
        ) or ETF_REAL_MONEY_DEFAULT_BENCHMARK

    return {
        "strategy_name": strategy_name,
        "start": execution_context.get("start") or CURRENT_CANDIDATE_COMPARE_DEFAULT_START.isoformat(),
        "end": execution_context.get("end") or CURRENT_CANDIDATE_COMPARE_DEFAULT_END.isoformat(),
        "timeframe": execution_context.get("timeframe") or "1d",
        "option": execution_context.get("option") or "month_end",
        "strategy_override": strategy_override,
    }

def _queue_current_candidate_compare_prefill(rows: list[dict[str, Any]]) -> None:
    compare_ready_items: list[dict[str, Any]] = []
    seen_categories: set[str] = set()
    for row in rows:
        item = _current_candidate_registry_row_to_compare_prefill(row)
        if not item:
            raise ValueError(f"후보 `{row.get('title')}`는 아직 compare prefill contract가 준비되지 않았습니다.")
        strategy_choice, _ = display_name_to_selection(item["strategy_name"])
        normalized_choice = strategy_choice or item["strategy_name"]
        if normalized_choice in seen_categories:
            raise ValueError("같은 strategy family 후보는 한 번에 하나만 compare로 보낼 수 있습니다.")
        seen_categories.add(normalized_choice)
        compare_ready_items.append(item)

    if len(compare_ready_items) < 2:
        raise ValueError("Compare로 보내려면 최소 2개의 후보를 선택해야 합니다.")
    if len(compare_ready_items) > 4:
        raise ValueError("Compare bundle은 최대 4개 후보까지만 지원합니다.")

    starts = {str(item["start"]) for item in compare_ready_items}
    ends = {str(item["end"]) for item in compare_ready_items}
    timeframes = {str(item["timeframe"]) for item in compare_ready_items}
    options = {str(item["option"]) for item in compare_ready_items}

    payload = {
        "selected_strategies": [item["strategy_name"] for item in compare_ready_items],
        "start": min(starts) if starts else CURRENT_CANDIDATE_COMPARE_DEFAULT_START.isoformat(),
        "end": max(ends) if ends else CURRENT_CANDIDATE_COMPARE_DEFAULT_END.isoformat(),
        "timeframe": next(iter(timeframes), "1d"),
        "option": next(iter(options), "month_end"),
        "strategy_overrides": {
            item["strategy_name"]: item["strategy_override"] for item in compare_ready_items
        },
    }
    titles = ", ".join(str(row.get("title") or row.get("registry_id") or "") for row in rows)
    st.session_state.backtest_compare_prefill_payload = payload
    st.session_state.backtest_compare_prefill_pending = True
    st.session_state.backtest_compare_prefill_notice = (
        f"current candidate bundle `{titles}`를 `Compare & Portfolio Builder`로 불러왔습니다."
    )
    st.session_state.backtest_compare_source_context = {
        "source_kind": "current_candidate_bundle",
        "source_label": titles,
        "registry_ids": [str(row.get("registry_id") or "") for row in rows],
        "candidate_titles": [str(row.get("title") or "") for row in rows],
        "selected_strategies": payload["selected_strategies"],
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
        st.session_state["compare_eq_min_price_filter"] = float(
            override.get("min_price_filter") or ETF_REAL_MONEY_DEFAULT_MIN_PRICE
        )
        st.session_state["compare_eq_transaction_cost_bps"] = float(
            override.get("transaction_cost_bps") or ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS
        )
        st.session_state["compare_eq_benchmark_ticker"] = str(
            override.get("benchmark_ticker") or ETF_REAL_MONEY_DEFAULT_BENCHMARK
        ).strip().upper()
        st.session_state["compare_eq_promotion_min_etf_aum_b"] = float(
            override.get("promotion_min_etf_aum_b") or ETF_OPERABILITY_DEFAULT_MIN_AUM_B
        )
        st.session_state["compare_eq_promotion_max_bid_ask_spread_pct"] = float(
            (override.get("promotion_max_bid_ask_spread_pct") or ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT) * 100.0
        )
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
    if strategy_name == "Global Relative Strength":
        preset_name = override.get("preset_name")
        universe_mode = override.get("universe_mode")
        tickers_text = ",".join(list(override.get("tickers") or GLOBAL_RELATIVE_STRENGTH_DEFAULT_TICKERS))
        st.session_state["compare_grs_universe_mode"] = (
            "Preset"
            if universe_mode == "preset" and preset_name in GLOBAL_RELATIVE_STRENGTH_PRESETS
            else "Manual"
        )
        if st.session_state["compare_grs_universe_mode"] == "Preset":
            st.session_state["compare_grs_preset"] = (
                preset_name or "Global Relative Strength Core ETF Universe"
            )
        else:
            st.session_state["compare_grs_manual_tickers"] = tickers_text
        st.session_state["compare_grs_cash_ticker"] = str(
            override.get("cash_ticker") or GLOBAL_RELATIVE_STRENGTH_DEFAULT_CASH_TICKER
        ).strip().upper()
        st.session_state["compare_grs_top"] = int(
            override.get("top") or GLOBAL_RELATIVE_STRENGTH_DEFAULT_TOP
        )
        st.session_state["compare_grs_interval"] = int(
            override.get("interval")
            or override.get("rebalance_interval")
            or GLOBAL_RELATIVE_STRENGTH_DEFAULT_SIGNAL_INTERVAL
        )
        _set_global_relative_strength_score_selection_state(
            key_prefix="compare_grs",
            score_lookback_months=list(
                override.get("score_lookback_months")
                or [
                    _gtaa_months_from_return_col(col)
                    for col in list(override.get("score_return_columns") or GLOBAL_RELATIVE_STRENGTH_SCORE_RETURN_COLUMNS)
                ]
            ),
        )
        st.session_state["compare_grs_trend_filter_window"] = int(
            override.get("trend_filter_window") or GLOBAL_RELATIVE_STRENGTH_DEFAULT_TREND_FILTER_WINDOW
        )
        st.session_state["compare_grs_min_price_filter"] = float(
            override.get("min_price_filter") or ETF_REAL_MONEY_DEFAULT_MIN_PRICE
        )
        st.session_state["compare_grs_transaction_cost_bps"] = float(
            override.get("transaction_cost_bps") or ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS
        )
        st.session_state["compare_grs_promotion_min_etf_aum_b"] = float(
            override.get("promotion_min_etf_aum_b") or ETF_OPERABILITY_DEFAULT_MIN_AUM_B
        )
        st.session_state["compare_grs_promotion_max_bid_ask_spread_pct"] = float(
            (override.get("promotion_max_bid_ask_spread_pct") or ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT) * 100.0
        )
        st.session_state["compare_grs_benchmark_ticker"] = str(
            override.get("benchmark_ticker") or ETF_REAL_MONEY_DEFAULT_BENCHMARK
        ).strip().upper()
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
    st.session_state[f"compare_{key_prefix}_weighting_mode"] = _strict_weighting_mode_value_to_label(
        override.get("weighting_mode") or STRICT_DEFAULT_WEIGHTING_MODE
    )
    st.session_state[f"compare_{key_prefix}_rejected_slot_handling_mode"] = _strict_rejection_handling_mode_value_to_label(
        resolve_strict_rejection_handling_mode(
            override.get("rejected_slot_handling_mode"),
            rejected_slot_fill_enabled=bool(
                override.get("rejected_slot_fill_enabled", STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED)
            ),
            partial_cash_retention_enabled=bool(
                override.get("partial_cash_retention_enabled", STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED)
            ),
        )
    )
    st.session_state[f"compare_{key_prefix}_rejected_slot_fill_enabled"] = bool(
        override.get("rejected_slot_fill_enabled", STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED)
    )
    st.session_state[f"compare_{key_prefix}_partial_cash_retention_enabled"] = bool(
        override.get("partial_cash_retention_enabled", STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED)
    )
    st.session_state[f"compare_{key_prefix}_risk_off_mode"] = _strict_risk_off_mode_value_to_label(
        override.get("risk_off_mode") or STRICT_DEFAULT_RISK_OFF_MODE
    )
    st.session_state[f"compare_{key_prefix}_defensive_tickers"] = ",".join(
        list(override.get("defensive_tickers") or STRICT_DEFAULT_DEFENSIVE_TICKERS)
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
    st.session_state[f"compare_{key_prefix}_guardrail_reference_ticker"] = str(
        override.get("guardrail_reference_ticker") or ""
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

def _compare_source_kind_label(source_kind: str | None) -> str:
    mapping = {
        "current_candidate_bundle": "Current Candidate Bundle",
        "saved_portfolio": "Saved Portfolio Re-entry",
        "manual_compare_selection": "Manual Compare Selection",
    }
    return mapping.get(str(source_kind or "").strip(), str(source_kind or "Manual Compare Selection"))

def _compare_source_kind_plain_text(source_kind: str | None) -> str:
    mapping = {
        "current_candidate_bundle": "Current candidate 후보 묶음에서 불러옴",
        "saved_portfolio": "저장된 포트폴리오에서 다시 불러옴",
        "manual_compare_selection": "직접 선택한 compare 설정",
    }
    return mapping.get(str(source_kind or "").strip(), "직접 선택한 compare 설정")

def _build_weighted_builder_compare_rows(bundles: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for bundle in bundles:
        summary_df = bundle.get("summary_df")
        meta = dict(bundle.get("meta") or {})
        summary_row = summary_df.iloc[0] if summary_df is not None and not summary_df.empty else None
        rows.append(
            {
                "Strategy": bundle.get("strategy_name") or "-",
                "Period": f"{meta.get('start') or '-'} -> {meta.get('end') or '-'}",
                "CAGR": _format_percent(float(summary_row["CAGR"])) if summary_row is not None and pd.notna(summary_row.get("CAGR")) else "-",
                "MDD": _format_percent(float(summary_row["Maximum Drawdown"])) if summary_row is not None and pd.notna(summary_row.get("Maximum Drawdown")) else "-",
                "Promotion": meta.get("promotion_label") or meta.get("promotion_status") or meta.get("promotion") or "-",
            }
        )
    return pd.DataFrame(rows)

def _render_compare_source_context_card(source_context: dict[str, Any] | None, bundles: list[dict[str, Any]]) -> None:
    source_context = dict(source_context or {})
    if not source_context and not bundles:
        return

    first_meta = dict((bundles[0].get("meta") or {}) if bundles else {})
    source_kind = _compare_source_kind_label(source_context.get("source_kind"))
    source_label = str(source_context.get("source_label") or "-").strip()
    selected_strategies = list(source_context.get("selected_strategies") or [bundle.get("strategy_name") for bundle in bundles])
    registry_ids = list(source_context.get("registry_ids") or [])
    weights_percent = list(source_context.get("weights_percent") or [])
    compare_period = f"{first_meta.get('start') or '-'} -> {first_meta.get('end') or '-'}"
    timeframe = first_meta.get("timeframe") or "-"
    option = first_meta.get("option") or "-"
    strategy_rows_df = _build_weighted_builder_compare_rows(bundles)

    st.markdown("##### What You Are Combining")
    st.caption(
        "지금 `Weighted Portfolio Builder`는 가장 최근 compare 결과를 기준으로 동작합니다. "
        "즉 아래에 보이는 전략들을 어떤 비중으로 섞을지 정하는 단계입니다."
    )
    summary_cols = st.columns(4, gap="small")
    with summary_cols[0]:
        st.markdown(f"**들어온 경로**  \n`{_compare_source_kind_plain_text(source_context.get('source_kind'))}`")
    with summary_cols[1]:
        st.markdown(f"**묶음 이름**  \n`{source_label or '-'}`")
    with summary_cols[2]:
        st.markdown(f"**비교 기간**  \n`{compare_period}`")
    with summary_cols[3]:
        st.markdown(f"**조합할 전략 수**  \n`{len([name for name in selected_strategies if name])}`")
    st.caption(
        f"현재 compare 결과는 `Timeframe = {timeframe}`, `Option = {option}` 기준입니다. "
        "이 설정 위에서 아래 가중 조합을 만들게 됩니다."
    )
    if not strategy_rows_df.empty:
        st.markdown("**이번에 섞게 되는 전략**")
        st.dataframe(strategy_rows_df, use_container_width=True, hide_index=True)
    if registry_ids:
        st.caption(f"Registry IDs: {', '.join(registry_ids)}")
    if weights_percent:
        st.caption(
            "이 compare는 이전에 저장된 비중을 함께 갖고 들어왔습니다: "
            + ", ".join(f"{float(weight):.1f}%" for weight in weights_percent)
        )
    st.info(
        "권장 흐름: 1) 위 전략 표를 보고 무엇을 섞는지 확인하고, "
        "2) 바로 아래에서 strategy별 weight를 넣고, "
        "3) `Date Alignment`를 고른 뒤, "
        "4) `Build Weighted Portfolio`를 눌러 결과를 만듭니다."
    )

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

def _is_saved_mix_replay_context() -> bool:
    source_context = dict(st.session_state.get("backtest_compare_source_context") or {})
    saved_portfolio_id = str(source_context.get("saved_portfolio_id") or "")
    replay_id = str(st.session_state.get("backtest_saved_portfolio_replay_id") or "")
    return (
        str(source_context.get("source_kind") or "").strip() == "saved_portfolio"
        and bool(replay_id)
        and replay_id == saved_portfolio_id
    )

# Keep replay details attached to the saved mix the user is currently inspecting.
def _saved_portfolio_replay_matches_selected_record(record: dict[str, Any]) -> bool:
    source_context = dict(st.session_state.get("backtest_compare_source_context") or {})
    replay_id = str(st.session_state.get("backtest_saved_portfolio_replay_id") or "")
    selected_id = str(record.get("portfolio_id") or "")
    return (
        bool(replay_id)
        and replay_id == selected_id
        and str(source_context.get("source_kind") or "").strip() == "saved_portfolio"
        and str(source_context.get("saved_portfolio_id") or "") == selected_id
        and isinstance(st.session_state.get("backtest_weighted_bundle"), dict)
    )

def _render_saved_mix_replay_result_card() -> None:
    source_context = dict(st.session_state.get("backtest_compare_source_context") or {})
    weighted_bundle = st.session_state.get("backtest_weighted_bundle")
    strategy_names = list(source_context.get("selected_strategies") or [])
    weights_percent = list(source_context.get("weights_percent") or [])
    source_label = str(source_context.get("source_label") or "Saved Portfolio Mix")
    saved_portfolio_id = str(source_context.get("saved_portfolio_id") or "-")

    with st.container(border=True):
        st.markdown("### 저장 Mix Replay 결과")
        st.caption(
            "이 영역은 저장된 비중 포트폴리오 mix 자체를 다시 연 결과입니다. "
            "아래 `Portfolio Mix 검증 보드`에서 mix replay와 workflow 기록 여부를 분리해서 확인합니다."
        )
        summary_cols = st.columns(4, gap="small")
        with summary_cols[0]:
            st.markdown(f"**Mix 이름**  \n{source_label}")
        with summary_cols[1]:
            st.markdown(f"**Portfolio ID**  \n`{saved_portfolio_id}`")
        with summary_cols[2]:
            st.markdown(f"**구성 전략**  \n{len(strategy_names)}개")
        with summary_cols[3]:
            st.markdown(
                "**비중**  \n"
                + (
                    " / ".join(f"{float(weight):.0f}%" for weight in weights_percent)
                    if weights_percent
                    else "-"
                )
            )
        if weighted_bundle and isinstance(weighted_bundle.get("summary_df"), pd.DataFrame):
            _render_summary_metrics(weighted_bundle["summary_df"])
            st.caption("상세 equity curve, contribution, result table은 아래 `3. 비중 포트폴리오 결과 확인`에서 확인합니다.")
        else:
            st.info("저장된 비중 조합의 weighted portfolio 결과가 아직 없습니다. `Mix 재실행 및 검증`을 실행하면 생성됩니다.")

# Render the create-new-mix side of Compare & Portfolio Builder.
def _render_strategy_compare_workspace() -> None:
    st.markdown("### 1. 개별 전략 비교")
    st.caption(
        "공통 기간으로 전략 후보를 비교하고, 개별 후보를 6단계 Candidate Review로 보낼지 판단합니다. "
        "비중 조합 자체는 아래 비중 포트폴리오 구성 또는 저장된 비중 조합 화면에서 별도로 검증합니다."
    )
    _apply_compare_prefill()
    compare_prefill_notice = st.session_state.get("backtest_compare_prefill_notice")
    if compare_prefill_notice:
        st.info(compare_prefill_notice)
        st.session_state.backtest_compare_prefill_notice = None
        _render_compare_prefill_applied_card(
            st.session_state.get("backtest_compare_prefill_payload"),
            st.session_state.get("backtest_compare_source_context"),
        )
    compare_result_notice = st.session_state.get("backtest_compare_result_notice")
    if compare_result_notice:
        st.success(compare_result_notice)
        st.session_state.backtest_compare_result_notice = None
    if st.session_state.backtest_compare_bundles or st.session_state.backtest_compare_error:
        if _is_saved_mix_replay_context():
            st.info(
                "최근 `Mix 재실행 및 검증` 결과는 `저장된 비중 조합` 화면에서 바로 확인합니다. "
                "새로운 개별 전략 5단계 비교를 하려면 아래 입력을 조정한 뒤 `Run Strategy Comparison`을 실행하세요."
            )
        else:
            with st.container(border=True):
                st.markdown("### 개별 전략 5단계 Compare 결과")
                st.caption(
                    "최근 실행한 개별 전략 Compare 결과입니다. 여기서 Summary, Data Trust, Real-Money gate, "
                    "상대 비교 근거를 보고 단일 후보를 Candidate Review로 넘길 수 있는지 확인합니다. "
                    "저장된 mix는 이 보드가 아니라 Portfolio Mix 검증 보드에서 판단합니다."
                )
                _render_compare_results()
        st.divider()
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
    st.caption("Strategy selection updates the strategy-specific sections immediately.")
    if _load_current_candidate_registry_latest():
        st.caption("문서에 정리된 대표 후보를 바로 가져오려면 아래 `Quick Re-entry From Current Candidates`를 펼치면 됩니다.")
        with st.expander("Quick Re-entry From Current Candidates", expanded=False):
            _render_current_candidate_bundle_workspace()
    quality_compare_strategy_name: str | None = None
    value_compare_strategy_name: str | None = None
    quality_value_compare_strategy_name: str | None = None
    selected_compare_families = [
        strategy_name
        for strategy_name in ["Quality", "Value", "Quality + Value"]
        if strategy_name in selected_strategies
    ]
    compare_eq_universe_mode = "preset"
    compare_eq_preset_name: str | None = "Dividend ETFs"
    compare_eq_tickers = list(EQUAL_WEIGHT_PRESETS["Dividend ETFs"])
    compare_gtaa_universe_mode = "preset"
    compare_gtaa_preset_name: str | None = "GTAA Universe"
    compare_gtaa_tickers = list(GTAA_DEFAULT_TICKERS)
    compare_grs_universe_mode = "preset"
    compare_grs_preset_name: str | None = "Global Relative Strength Core ETF Universe"
    compare_grs_tickers = list(GLOBAL_RELATIVE_STRENGTH_DEFAULT_TICKERS)
    st.markdown("#### Compare Period & Shared Inputs")
    st.caption(
        "모든 compare 전략이 함께 사용하는 기간과 실행 옵션입니다. "
        "`Timeframe`과 `Option`은 특정 전략 전용 설정이 아니므로 날짜 입력과 같은 공용 영역에서 관리합니다."
    )
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            compare_start = st.date_input("Start Date", value=date(2016, 1, 1), key="compare_start")
        with col2:
            compare_end = st.date_input("End Date", value=DEFAULT_BACKTEST_END_DATE, key="compare_end")
        with col3:
            compare_timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="compare_timeframe")
        with col4:
            compare_option = st.selectbox("Option", options=["month_end"], index=0, key="compare_option")

        st.markdown("#### Strategy-Specific Advanced Inputs")
        st.caption(
            "아래 섹션은 선택된 전략과 variant에 맞춰 다시 구성됩니다. "
            "Annual / Quarterly를 바꾸면 별도 적용 버튼 없이 이 영역이 즉시 갱신됩니다."
        )
        with st.container():
            if selected_compare_families:
                st.caption(
                    "Annual / Quarterly variant는 각 전략 박스 안에서 선택합니다. "
                    "선택한 variant에 맞는 세부 입력이 같은 박스 안에 이어집니다."
                )

            compare_strategy_overrides: dict[str, dict] = {}
            quality_compare_settings_container = None
            value_compare_settings_container = None
            quality_value_compare_settings_container = None

            if "Quality" in selected_strategies:
                with st.container(border=True):
                    st.markdown("##### Quality")
                    quality_variant_key = _compare_family_variant_session_key("Quality")
                    if quality_variant_key:
                        quality_selected_variant = st.selectbox(
                            "Quality Variant",
                            options=family_variant_options("Quality"),
                            key=quality_variant_key,
                        )
                        quality_compare_strategy_name = resolve_concrete_strategy_display_name(
                            "Quality",
                            quality_selected_variant,
                        )
                    st.caption(f"현재 compare 실행 variant: `{quality_compare_strategy_name}`")
                    st.caption("선택한 variant의 세부 설정이 아래에 이어집니다.")
                    _render_strategy_capability_snapshot(quality_compare_strategy_name)
                    quality_compare_settings_container = st.container()

            if "Value" in selected_strategies:
                with st.container(border=True):
                    st.markdown("##### Value")
                    value_variant_key = _compare_family_variant_session_key("Value")
                    if value_variant_key:
                        value_selected_variant = st.selectbox(
                            "Value Variant",
                            options=family_variant_options("Value"),
                            key=value_variant_key,
                        )
                        value_compare_strategy_name = resolve_concrete_strategy_display_name(
                            "Value",
                            value_selected_variant,
                        )
                    st.caption(f"현재 compare 실행 variant: `{value_compare_strategy_name}`")
                    st.caption("선택한 variant의 세부 설정이 아래에 이어집니다.")
                    _render_strategy_capability_snapshot(value_compare_strategy_name)
                    value_compare_settings_container = st.container()

            if "Quality + Value" in selected_strategies:
                with st.container(border=True):
                    st.markdown("##### Quality + Value")
                    quality_value_variant_key = _compare_family_variant_session_key("Quality + Value")
                    if quality_value_variant_key:
                        quality_value_selected_variant = st.selectbox(
                            "Quality + Value Variant",
                            options=family_variant_options("Quality + Value"),
                            key=quality_value_variant_key,
                        )
                        quality_value_compare_strategy_name = resolve_concrete_strategy_display_name(
                            "Quality + Value",
                            quality_value_selected_variant,
                        )
                    st.caption(f"현재 compare 실행 variant: `{quality_value_compare_strategy_name}`")
                    st.caption("선택한 variant의 세부 설정이 아래에 이어집니다.")
                    _render_strategy_capability_snapshot(quality_value_compare_strategy_name)
                    quality_value_compare_settings_container = st.container()

            if "Equal Weight" in selected_strategies:
                with st.container(border=True):
                    st.markdown("##### Equal Weight")
                    _render_strategy_capability_snapshot("Equal Weight")
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
                                help=(
                                    "`option=month_end` 기준으로 1=매월(대략 4주), 4=4개월마다, 12=연 1회입니다."
                                ),
                                key="compare_eq_interval",
                            )
                        )
                    }
                    with st.expander("Real-Money Contract", expanded=False):
                        (
                            min_price_filter,
                            transaction_cost_bps,
                            benchmark_ticker,
                            promotion_min_etf_aum_b,
                            promotion_max_bid_ask_spread_pct,
                        ) = _render_etf_real_money_inputs(
                            key_prefix="compare_eq",
                        )
                    compare_strategy_overrides["Equal Weight"]["min_price_filter"] = float(min_price_filter)
                    compare_strategy_overrides["Equal Weight"]["transaction_cost_bps"] = float(transaction_cost_bps)
                    compare_strategy_overrides["Equal Weight"]["benchmark_ticker"] = benchmark_ticker
                    compare_strategy_overrides["Equal Weight"]["promotion_min_etf_aum_b"] = float(promotion_min_etf_aum_b)
                    compare_strategy_overrides["Equal Weight"]["promotion_max_bid_ask_spread_pct"] = float(
                        promotion_max_bid_ask_spread_pct
                    )

            if "GTAA" in selected_strategies:
                with st.container(border=True):
                    st.markdown("##### GTAA")
                    _render_strategy_capability_snapshot("GTAA")
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
                    _render_advanced_group_caption("핵심 GTAA 계약은 위에 두고, overlay / 실전 계약 / guardrail은 아래 그룹으로 분리했습니다.")
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
                    }
                    compare_gtaa_score_lookback_months, compare_gtaa_score_weights = _render_gtaa_score_weight_inputs(
                        key_prefix="compare_gtaa"
                    )
                    compare_strategy_overrides["GTAA"]["score_lookback_months"] = list(compare_gtaa_score_lookback_months)
                    compare_strategy_overrides["GTAA"]["score_return_columns"] = [
                        _gtaa_return_col_from_months(months) for months in compare_gtaa_score_lookback_months
                    ]
                    compare_strategy_overrides["GTAA"]["score_weights"] = compare_gtaa_score_weights
                    with st.expander("Risk-Off Overlay", expanded=False):
                        risk_off_contract = _render_gtaa_risk_off_contract_inputs(key_prefix="compare_gtaa")
                    compare_strategy_overrides["GTAA"]["trend_filter_window"] = int(risk_off_contract["trend_filter_window"])
                    compare_strategy_overrides["GTAA"]["risk_off_mode"] = risk_off_contract["risk_off_mode"]
                    compare_strategy_overrides["GTAA"]["defensive_tickers"] = list(risk_off_contract["defensive_tickers"])
                    compare_strategy_overrides["GTAA"]["market_regime_enabled"] = bool(risk_off_contract["market_regime_enabled"])
                    compare_strategy_overrides["GTAA"]["market_regime_window"] = int(risk_off_contract["market_regime_window"])
                    compare_strategy_overrides["GTAA"]["market_regime_benchmark"] = risk_off_contract["market_regime_benchmark"]
                    compare_strategy_overrides["GTAA"]["crash_guardrail_enabled"] = bool(risk_off_contract["crash_guardrail_enabled"])
                    compare_strategy_overrides["GTAA"]["crash_guardrail_drawdown_threshold"] = float(risk_off_contract["crash_guardrail_drawdown_threshold"])
                    compare_strategy_overrides["GTAA"]["crash_guardrail_lookback_months"] = int(risk_off_contract["crash_guardrail_lookback_months"])
                    with st.expander("Real-Money Contract", expanded=False):
                        (
                            min_price_filter,
                            transaction_cost_bps,
                            benchmark_ticker,
                            promotion_min_etf_aum_b,
                            promotion_max_bid_ask_spread_pct,
                        ) = _render_etf_real_money_inputs(
                            key_prefix="compare_gtaa",
                        )
                    compare_strategy_overrides["GTAA"]["min_price_filter"] = float(min_price_filter)
                    compare_strategy_overrides["GTAA"]["transaction_cost_bps"] = float(transaction_cost_bps)
                    compare_strategy_overrides["GTAA"]["benchmark_ticker"] = benchmark_ticker
                    compare_strategy_overrides["GTAA"]["promotion_min_etf_aum_b"] = float(promotion_min_etf_aum_b)
                    compare_strategy_overrides["GTAA"]["promotion_max_bid_ask_spread_pct"] = float(promotion_max_bid_ask_spread_pct)
                    with st.expander("ETF Guardrails", expanded=False):
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
                    compare_strategy_overrides["GTAA"]["underperformance_guardrail_enabled"] = bool(underperformance_guardrail_enabled)
                    compare_strategy_overrides["GTAA"]["underperformance_guardrail_window_months"] = int(underperformance_guardrail_window_months)
                    compare_strategy_overrides["GTAA"]["underperformance_guardrail_threshold"] = float(underperformance_guardrail_threshold)
                    compare_strategy_overrides["GTAA"]["drawdown_guardrail_enabled"] = bool(drawdown_guardrail_enabled)
                    compare_strategy_overrides["GTAA"]["drawdown_guardrail_window_months"] = int(drawdown_guardrail_window_months)
                    compare_strategy_overrides["GTAA"]["drawdown_guardrail_strategy_threshold"] = float(drawdown_guardrail_strategy_threshold)
                    compare_strategy_overrides["GTAA"]["drawdown_guardrail_gap_threshold"] = float(drawdown_guardrail_gap_threshold)

            if "Global Relative Strength" in selected_strategies:
                with st.container(border=True):
                    st.markdown("##### Global Relative Strength")
                    _render_strategy_capability_snapshot("Global Relative Strength")
                    (
                        compare_grs_universe_mode,
                        compare_grs_preset_name,
                        compare_grs_tickers,
                    ) = _render_global_relative_strength_universe_inputs(
                        key_prefix="compare_grs",
                        radio_label="Global Relative Strength Universe Mode",
                        preset_label="Global Relative Strength Preset",
                        ticker_label="Global Relative Strength Tickers",
                    )
                    _render_advanced_group_caption(
                        "상대강도 선택 규칙은 위에 두고, cash fallback과 실전 계약은 같은 박스 안에서 관리합니다."
                    )
                    compare_strategy_overrides["Global Relative Strength"] = {
                        "tickers": list(compare_grs_tickers),
                        "preset_name": compare_grs_preset_name,
                        "universe_mode": compare_grs_universe_mode,
                        "cash_ticker": str(
                            st.text_input(
                                "Global Relative Strength Cash / Defensive Ticker",
                                value=GLOBAL_RELATIVE_STRENGTH_DEFAULT_CASH_TICKER,
                                help="선택된 ETF가 trend filter를 통과하지 못하면 이 ticker로 대피합니다.",
                                key="compare_grs_cash_ticker",
                            )
                            or ""
                        ).strip().upper(),
                        "top": int(
                            st.number_input(
                                "Global Relative Strength Top Assets",
                                min_value=1,
                                max_value=12,
                                value=GLOBAL_RELATIVE_STRENGTH_DEFAULT_TOP,
                                step=1,
                                key="compare_grs_top",
                            )
                        ),
                        "interval": int(
                            st.number_input(
                                "Global Relative Strength Signal Interval (months)",
                                min_value=1,
                                max_value=12,
                                value=GLOBAL_RELATIVE_STRENGTH_DEFAULT_SIGNAL_INTERVAL,
                                step=1,
                                key="compare_grs_interval",
                            )
                        ),
                        "trend_filter_enabled": True,
                        "trend_filter_window": int(
                            st.number_input(
                                "Global Relative Strength Trend Filter Window",
                                min_value=20,
                                max_value=400,
                                value=GLOBAL_RELATIVE_STRENGTH_DEFAULT_TREND_FILTER_WINDOW,
                                step=10,
                                key="compare_grs_trend_filter_window",
                            )
                        ),
                    }
                    compare_grs_score_lookback_months, compare_grs_score_weights = (
                        _render_global_relative_strength_score_weight_inputs(key_prefix="compare_grs")
                    )
                    compare_strategy_overrides["Global Relative Strength"]["score_lookback_months"] = list(
                        compare_grs_score_lookback_months
                    )
                    compare_strategy_overrides["Global Relative Strength"]["score_return_columns"] = [
                        _gtaa_return_col_from_months(months)
                        for months in compare_grs_score_lookback_months
                    ]
                    compare_strategy_overrides["Global Relative Strength"]["score_weights"] = compare_grs_score_weights
                    with st.expander("Real-Money Contract", expanded=False):
                        (
                            min_price_filter,
                            transaction_cost_bps,
                            benchmark_ticker,
                            promotion_min_etf_aum_b,
                            promotion_max_bid_ask_spread_pct,
                        ) = _render_etf_real_money_inputs(
                            key_prefix="compare_grs",
                        )
                    compare_strategy_overrides["Global Relative Strength"]["min_price_filter"] = float(min_price_filter)
                    compare_strategy_overrides["Global Relative Strength"]["transaction_cost_bps"] = float(transaction_cost_bps)
                    compare_strategy_overrides["Global Relative Strength"]["benchmark_ticker"] = benchmark_ticker
                    compare_strategy_overrides["Global Relative Strength"]["promotion_min_etf_aum_b"] = float(promotion_min_etf_aum_b)
                    compare_strategy_overrides["Global Relative Strength"]["promotion_max_bid_ask_spread_pct"] = float(
                        promotion_max_bid_ask_spread_pct
                    )

            if "Risk Parity Trend" in selected_strategies:
                with st.container(border=True):
                    st.markdown("##### Risk Parity Trend")
                    _render_strategy_capability_snapshot("Risk Parity Trend")
                    _render_advanced_group_caption("핵심 실행 계약은 위에 두고, 실전 계약과 guardrail은 아래 그룹으로 분리했습니다.")
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
                    with st.expander("Real-Money Contract", expanded=False):
                        (
                            min_price_filter,
                            transaction_cost_bps,
                            benchmark_ticker,
                            promotion_min_etf_aum_b,
                            promotion_max_bid_ask_spread_pct,
                        ) = _render_etf_real_money_inputs(
                            key_prefix="compare_rp",
                        )
                    compare_strategy_overrides["Risk Parity Trend"]["min_price_filter"] = float(min_price_filter)
                    compare_strategy_overrides["Risk Parity Trend"]["transaction_cost_bps"] = float(transaction_cost_bps)
                    compare_strategy_overrides["Risk Parity Trend"]["benchmark_ticker"] = benchmark_ticker
                    compare_strategy_overrides["Risk Parity Trend"]["promotion_min_etf_aum_b"] = float(promotion_min_etf_aum_b)
                    compare_strategy_overrides["Risk Parity Trend"]["promotion_max_bid_ask_spread_pct"] = float(promotion_max_bid_ask_spread_pct)
                    with st.expander("ETF Guardrails", expanded=False):
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
                    compare_strategy_overrides["Risk Parity Trend"]["underperformance_guardrail_enabled"] = bool(underperformance_guardrail_enabled)
                    compare_strategy_overrides["Risk Parity Trend"]["underperformance_guardrail_window_months"] = int(underperformance_guardrail_window_months)
                    compare_strategy_overrides["Risk Parity Trend"]["underperformance_guardrail_threshold"] = float(underperformance_guardrail_threshold)
                    compare_strategy_overrides["Risk Parity Trend"]["drawdown_guardrail_enabled"] = bool(drawdown_guardrail_enabled)
                    compare_strategy_overrides["Risk Parity Trend"]["drawdown_guardrail_window_months"] = int(drawdown_guardrail_window_months)
                    compare_strategy_overrides["Risk Parity Trend"]["drawdown_guardrail_strategy_threshold"] = float(drawdown_guardrail_strategy_threshold)
                    compare_strategy_overrides["Risk Parity Trend"]["drawdown_guardrail_gap_threshold"] = float(drawdown_guardrail_gap_threshold)

            if "Dual Momentum" in selected_strategies:
                with st.container(border=True):
                    st.markdown("##### Dual Momentum")
                    _render_strategy_capability_snapshot("Dual Momentum")
                    _render_advanced_group_caption("핵심 실행 계약은 위에 두고, 실전 계약과 guardrail은 아래 그룹으로 분리했습니다.")
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
                    with st.expander("Real-Money Contract", expanded=False):
                        (
                            min_price_filter,
                            transaction_cost_bps,
                            benchmark_ticker,
                            promotion_min_etf_aum_b,
                            promotion_max_bid_ask_spread_pct,
                        ) = _render_etf_real_money_inputs(
                            key_prefix="compare_dm",
                        )
                    compare_strategy_overrides["Dual Momentum"]["min_price_filter"] = float(min_price_filter)
                    compare_strategy_overrides["Dual Momentum"]["transaction_cost_bps"] = float(transaction_cost_bps)
                    compare_strategy_overrides["Dual Momentum"]["benchmark_ticker"] = benchmark_ticker
                    compare_strategy_overrides["Dual Momentum"]["promotion_min_etf_aum_b"] = float(promotion_min_etf_aum_b)
                    compare_strategy_overrides["Dual Momentum"]["promotion_max_bid_ask_spread_pct"] = float(promotion_max_bid_ask_spread_pct)
                    with st.expander("ETF Guardrails", expanded=False):
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
                    compare_strategy_overrides["Dual Momentum"]["underperformance_guardrail_enabled"] = bool(underperformance_guardrail_enabled)
                    compare_strategy_overrides["Dual Momentum"]["underperformance_guardrail_window_months"] = int(underperformance_guardrail_window_months)
                    compare_strategy_overrides["Dual Momentum"]["underperformance_guardrail_threshold"] = float(underperformance_guardrail_threshold)
                    compare_strategy_overrides["Dual Momentum"]["drawdown_guardrail_enabled"] = bool(drawdown_guardrail_enabled)
                    compare_strategy_overrides["Dual Momentum"]["drawdown_guardrail_window_months"] = int(drawdown_guardrail_window_months)
                    compare_strategy_overrides["Dual Momentum"]["drawdown_guardrail_strategy_threshold"] = float(drawdown_guardrail_strategy_threshold)
                    compare_strategy_overrides["Dual Momentum"]["drawdown_guardrail_gap_threshold"] = float(drawdown_guardrail_gap_threshold)

            if quality_compare_strategy_name == "Quality Snapshot" and quality_compare_settings_container is not None:
                with quality_compare_settings_container:
                    st.markdown("##### Quality Snapshot")
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

            if quality_compare_strategy_name == "Quality Snapshot (Strict Annual)" and quality_compare_settings_container is not None:
                with quality_compare_settings_container:
                    st.markdown("##### Quality Snapshot (Strict Annual)")
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
                    _render_advanced_group_caption("핵심 factor / universe 계약은 위에 두고, overlay와 포트폴리오 처리 규칙은 아래 펼쳐보기로 묶었습니다.")
                    with st.expander("Overlay", expanded=False):
                        _render_strict_overlay_section_intro()
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
                    with st.expander("Portfolio Handling & Defensive Rules", expanded=False):
                        _render_strict_portfolio_handling_contracts_intro()
                        compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["rejected_slot_handling_mode"] = _render_strict_rejected_slot_handling_contract_inputs(
                            key_prefix="compare_qss",
                            label_prefix="Strict Annual Quality",
                        )
                        (
                            compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["rejected_slot_fill_enabled"],
                            compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["partial_cash_retention_enabled"],
                        ) = strict_rejection_handling_mode_to_flags(
                            compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["rejected_slot_handling_mode"]
                        )
                        compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["weighting_mode"] = _render_strict_weighting_contract_inputs(
                            key_prefix="compare_qss",
                            label_prefix="Strict Annual Quality",
                        )
                        (
                            compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["risk_off_mode"],
                            compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["defensive_tickers"],
                        ) = _render_strict_defensive_sleeve_contract_inputs(
                            key_prefix="compare_qss",
                            label_prefix="Strict Annual Quality",
                        )
                    with st.expander("Real-Money Contract", expanded=False):
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
                    with st.expander("Guardrails", expanded=False):
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
                        compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["guardrail_reference_ticker"] = _render_guardrail_reference_ticker_input(
                            key_prefix="compare_qss",
                            benchmark_ticker=benchmark_ticker,
                            default_guardrail_reference_ticker=compare_strategy_overrides["Quality Snapshot (Strict Annual)"].get("guardrail_reference_ticker"),
                            underperformance_guardrail_enabled=compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["underperformance_guardrail_enabled"],
                            drawdown_guardrail_enabled=compare_strategy_overrides["Quality Snapshot (Strict Annual)"]["drawdown_guardrail_enabled"],
                        )

            if quality_compare_strategy_name == "Quality Snapshot (Strict Quarterly Prototype)" and quality_compare_settings_container is not None:
                with quality_compare_settings_container:
                    st.markdown("##### Quality Snapshot (Strict Quarterly Prototype)")
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
                    _render_advanced_group_caption("핵심 factor / universe 계약은 위에 두고, overlay와 포트폴리오 처리 규칙은 아래 펼쳐보기로 묶었습니다.")
                    with st.expander("Overlay", expanded=False):
                        _render_strict_overlay_section_intro()
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
                    with st.expander("Portfolio Handling & Defensive Rules", expanded=False):
                        _render_strict_portfolio_handling_contracts_intro()
                        compare_strategy_overrides["Quality Snapshot (Strict Quarterly Prototype)"]["rejected_slot_handling_mode"] = _render_strict_rejected_slot_handling_contract_inputs(
                            key_prefix="compare_qsqp",
                            label_prefix="Strict Quarterly Quality",
                        )
                        (
                            compare_strategy_overrides["Quality Snapshot (Strict Quarterly Prototype)"]["rejected_slot_fill_enabled"],
                            compare_strategy_overrides["Quality Snapshot (Strict Quarterly Prototype)"]["partial_cash_retention_enabled"],
                        ) = strict_rejection_handling_mode_to_flags(
                            compare_strategy_overrides["Quality Snapshot (Strict Quarterly Prototype)"]["rejected_slot_handling_mode"]
                        )
                        compare_strategy_overrides["Quality Snapshot (Strict Quarterly Prototype)"]["weighting_mode"] = _render_strict_weighting_contract_inputs(
                            key_prefix="compare_qsqp",
                            label_prefix="Strict Quarterly Quality",
                        )
                        (
                            compare_strategy_overrides["Quality Snapshot (Strict Quarterly Prototype)"]["risk_off_mode"],
                            compare_strategy_overrides["Quality Snapshot (Strict Quarterly Prototype)"]["defensive_tickers"],
                        ) = _render_strict_defensive_sleeve_contract_inputs(
                            key_prefix="compare_qsqp",
                            label_prefix="Strict Quarterly Quality",
                        )

            if value_compare_strategy_name == "Value Snapshot (Strict Annual)" and value_compare_settings_container is not None:
                with value_compare_settings_container:
                    st.markdown("##### Value Snapshot (Strict Annual)")
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
                    _render_advanced_group_caption("핵심 factor / universe 계약은 위에 두고, overlay와 포트폴리오 처리 규칙은 아래 펼쳐보기로 묶었습니다.")
                    with st.expander("Overlay", expanded=False):
                        _render_strict_overlay_section_intro()
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
                    with st.expander("Portfolio Handling & Defensive Rules", expanded=False):
                        _render_strict_portfolio_handling_contracts_intro()
                        compare_strategy_overrides["Value Snapshot (Strict Annual)"]["rejected_slot_handling_mode"] = _render_strict_rejected_slot_handling_contract_inputs(
                            key_prefix="compare_vss",
                            label_prefix="Strict Annual Value",
                        )
                        (
                            compare_strategy_overrides["Value Snapshot (Strict Annual)"]["rejected_slot_fill_enabled"],
                            compare_strategy_overrides["Value Snapshot (Strict Annual)"]["partial_cash_retention_enabled"],
                        ) = strict_rejection_handling_mode_to_flags(
                            compare_strategy_overrides["Value Snapshot (Strict Annual)"]["rejected_slot_handling_mode"]
                        )
                        compare_strategy_overrides["Value Snapshot (Strict Annual)"]["weighting_mode"] = _render_strict_weighting_contract_inputs(
                            key_prefix="compare_vss",
                            label_prefix="Strict Annual Value",
                        )
                        (
                            compare_strategy_overrides["Value Snapshot (Strict Annual)"]["risk_off_mode"],
                            compare_strategy_overrides["Value Snapshot (Strict Annual)"]["defensive_tickers"],
                        ) = _render_strict_defensive_sleeve_contract_inputs(
                            key_prefix="compare_vss",
                            label_prefix="Strict Annual Value",
                        )
                    with st.expander("Real-Money Contract", expanded=False):
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
                    with st.expander("Guardrails", expanded=False):
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
                        compare_strategy_overrides["Value Snapshot (Strict Annual)"]["guardrail_reference_ticker"] = _render_guardrail_reference_ticker_input(
                            key_prefix="compare_vss",
                            benchmark_ticker=benchmark_ticker,
                            default_guardrail_reference_ticker=compare_strategy_overrides["Value Snapshot (Strict Annual)"].get("guardrail_reference_ticker"),
                            underperformance_guardrail_enabled=compare_strategy_overrides["Value Snapshot (Strict Annual)"]["underperformance_guardrail_enabled"],
                            drawdown_guardrail_enabled=compare_strategy_overrides["Value Snapshot (Strict Annual)"]["drawdown_guardrail_enabled"],
                        )

            if value_compare_strategy_name == "Value Snapshot (Strict Quarterly Prototype)" and value_compare_settings_container is not None:
                with value_compare_settings_container:
                    st.markdown("##### Value Snapshot (Strict Quarterly Prototype)")
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
                    _render_advanced_group_caption("핵심 factor / universe 계약은 위에 두고, overlay와 포트폴리오 처리 규칙은 아래 펼쳐보기로 묶었습니다.")
                    with st.expander("Overlay", expanded=False):
                        _render_strict_overlay_section_intro()
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
                    with st.expander("Portfolio Handling & Defensive Rules", expanded=False):
                        _render_strict_portfolio_handling_contracts_intro()
                        compare_strategy_overrides["Value Snapshot (Strict Quarterly Prototype)"]["rejected_slot_handling_mode"] = _render_strict_rejected_slot_handling_contract_inputs(
                            key_prefix="compare_vsqp",
                            label_prefix="Strict Quarterly Value",
                        )
                        (
                            compare_strategy_overrides["Value Snapshot (Strict Quarterly Prototype)"]["rejected_slot_fill_enabled"],
                            compare_strategy_overrides["Value Snapshot (Strict Quarterly Prototype)"]["partial_cash_retention_enabled"],
                        ) = strict_rejection_handling_mode_to_flags(
                            compare_strategy_overrides["Value Snapshot (Strict Quarterly Prototype)"]["rejected_slot_handling_mode"]
                        )
                        compare_strategy_overrides["Value Snapshot (Strict Quarterly Prototype)"]["weighting_mode"] = _render_strict_weighting_contract_inputs(
                            key_prefix="compare_vsqp",
                            label_prefix="Strict Quarterly Value",
                        )
                        (
                            compare_strategy_overrides["Value Snapshot (Strict Quarterly Prototype)"]["risk_off_mode"],
                            compare_strategy_overrides["Value Snapshot (Strict Quarterly Prototype)"]["defensive_tickers"],
                        ) = _render_strict_defensive_sleeve_contract_inputs(
                            key_prefix="compare_vsqp",
                            label_prefix="Strict Quarterly Value",
                        )

            if quality_value_compare_strategy_name == "Quality + Value Snapshot (Strict Annual)" and quality_value_compare_settings_container is not None:
                with quality_value_compare_settings_container:
                    st.markdown("##### Quality + Value Snapshot (Strict Annual)")
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
                    _render_advanced_group_caption("핵심 factor / universe 계약은 위에 두고, overlay와 포트폴리오 처리 규칙은 아래 펼쳐보기로 묶었습니다.")
                    with st.expander("Overlay", expanded=False):
                        _render_strict_overlay_section_intro()
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
                    with st.expander("Portfolio Handling & Defensive Rules", expanded=False):
                        _render_strict_portfolio_handling_contracts_intro()
                        compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["rejected_slot_handling_mode"] = _render_strict_rejected_slot_handling_contract_inputs(
                            key_prefix="compare_qvss",
                            label_prefix="Strict Annual Multi-Factor",
                        )
                        (
                            compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["rejected_slot_fill_enabled"],
                            compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["partial_cash_retention_enabled"],
                        ) = strict_rejection_handling_mode_to_flags(
                            compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["rejected_slot_handling_mode"]
                        )
                        compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["weighting_mode"] = _render_strict_weighting_contract_inputs(
                            key_prefix="compare_qvss",
                            label_prefix="Strict Annual Multi-Factor",
                        )
                        (
                            compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["risk_off_mode"],
                            compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["defensive_tickers"],
                        ) = _render_strict_defensive_sleeve_contract_inputs(
                            key_prefix="compare_qvss",
                            label_prefix="Strict Annual Multi-Factor",
                        )
                    with st.expander("Real-Money Contract", expanded=False):
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
                    with st.expander("Guardrails", expanded=False):
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
                        compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["guardrail_reference_ticker"] = _render_guardrail_reference_ticker_input(
                            key_prefix="compare_qvss",
                            benchmark_ticker=benchmark_ticker,
                            default_guardrail_reference_ticker=compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"].get("guardrail_reference_ticker"),
                            underperformance_guardrail_enabled=compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["underperformance_guardrail_enabled"],
                            drawdown_guardrail_enabled=compare_strategy_overrides["Quality + Value Snapshot (Strict Annual)"]["drawdown_guardrail_enabled"],
                        )

            if quality_value_compare_strategy_name == "Quality + Value Snapshot (Strict Quarterly Prototype)" and quality_value_compare_settings_container is not None:
                with quality_value_compare_settings_container:
                    st.markdown("##### Quality + Value Snapshot (Strict Quarterly Prototype)")
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
                    _render_advanced_group_caption("핵심 factor / universe 계약은 위에 두고, overlay와 포트폴리오 처리 규칙은 아래 펼쳐보기로 묶었습니다.")
                    with st.expander("Overlay", expanded=False):
                        _render_strict_overlay_section_intro()
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
                    with st.expander("Portfolio Handling & Defensive Rules", expanded=False):
                        _render_strict_portfolio_handling_contracts_intro()
                        compare_strategy_overrides["Quality + Value Snapshot (Strict Quarterly Prototype)"]["rejected_slot_handling_mode"] = _render_strict_rejected_slot_handling_contract_inputs(
                            key_prefix="compare_qvqp",
                            label_prefix="Strict Quarterly Multi-Factor",
                        )
                        (
                            compare_strategy_overrides["Quality + Value Snapshot (Strict Quarterly Prototype)"]["rejected_slot_fill_enabled"],
                            compare_strategy_overrides["Quality + Value Snapshot (Strict Quarterly Prototype)"]["partial_cash_retention_enabled"],
                        ) = strict_rejection_handling_mode_to_flags(
                            compare_strategy_overrides["Quality + Value Snapshot (Strict Quarterly Prototype)"]["rejected_slot_handling_mode"]
                        )
                        compare_strategy_overrides["Quality + Value Snapshot (Strict Quarterly Prototype)"]["weighting_mode"] = _render_strict_weighting_contract_inputs(
                            key_prefix="compare_qvqp",
                            label_prefix="Strict Quarterly Multi-Factor",
                        )
                        (
                            compare_strategy_overrides["Quality + Value Snapshot (Strict Quarterly Prototype)"]["risk_off_mode"],
                            compare_strategy_overrides["Quality + Value Snapshot (Strict Quarterly Prototype)"]["defensive_tickers"],
                        ) = _render_strict_defensive_sleeve_contract_inputs(
                            key_prefix="compare_qvqp",
                            label_prefix="Strict Quarterly Multi-Factor",
                        )

        compare_submitted = st.button(
            "Run Strategy Comparison",
            key="compare_run_strategy_comparison",
            use_container_width=True,
        )
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
        st.session_state.backtest_saved_portfolio_replay_id = None
        st.session_state.backtest_compare_source_context = {
            "source_kind": "manual_compare",
            "source_label": "Manual Strategy Comparison",
            "selected_strategies": selected_strategy_execution_names,
        }
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
        elif (
            "Global Relative Strength" in selected_strategies
            and not (compare_strategy_overrides.get("Global Relative Strength", {}).get("tickers") or [])
        ):
            st.session_state.backtest_compare_bundles = None
            st.session_state.backtest_compare_error_kind = "input"
            st.session_state.backtest_compare_error = "Global Relative Strength universe must contain at least one ticker."
        elif (
            "Global Relative Strength" in selected_strategies
            and not (compare_strategy_overrides.get("Global Relative Strength", {}).get("cash_ticker") or "")
        ):
            st.session_state.backtest_compare_bundles = None
            st.session_state.backtest_compare_error_kind = "input"
            st.session_state.backtest_compare_error = "Global Relative Strength cash ticker is required."
        elif (
            "Global Relative Strength" in selected_strategies
            and not (compare_strategy_overrides.get("Global Relative Strength", {}).get("score_lookback_months") or [])
        ):
            st.session_state.backtest_compare_bundles = None
            st.session_state.backtest_compare_error_kind = "input"
            st.session_state.backtest_compare_error = "Global Relative Strength Score Horizons must contain at least one lookback window."
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
                st.session_state.backtest_weighted_bundle = None
                st.session_state.backtest_weighted_error = None
                st.session_state.backtest_compare_workspace_mode_request = COMPARE_MODE_STRATEGY
                st.session_state.backtest_compare_result_notice = (
                    "개별 전략 Compare 결과를 만들었습니다. 아래 5단계 Compare 검증 보드에서 통과 여부를 확인하세요."
                )
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
                        "strategy_data_trust_rows": _build_strategy_data_trust_rows(bundles),
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
        st.rerun()
    if st.session_state.backtest_compare_bundles:
        st.divider()
    _render_weighted_portfolio_builder()

# Render and operate the Compare & Portfolio Builder workspace.
def render_compare_portfolio_workspace() -> None:
    saved_notice = st.session_state.get("backtest_saved_portfolio_notice")
    if saved_notice:
        st.success(saved_notice)
        st.session_state.backtest_saved_portfolio_notice = None

    mode_options = [COMPARE_MODE_STRATEGY, COMPARE_MODE_SAVED_MIX]
    requested_mode = _normalize_compare_workspace_mode(st.session_state.get("backtest_compare_workspace_mode_request"))
    if requested_mode in mode_options:
        st.session_state.backtest_compare_workspace_mode = requested_mode
        st.session_state.backtest_compare_workspace_mode_request = None
    current_mode = _normalize_compare_workspace_mode(st.session_state.get("backtest_compare_workspace_mode"))
    if current_mode not in mode_options:
        current_mode = COMPARE_MODE_STRATEGY
    st.session_state.backtest_compare_workspace_mode = current_mode
    if hasattr(st, "segmented_control"):
        st.segmented_control(
            "Compare Workspace",
            options=mode_options,
            selection_mode="single",
            required=True,
            key="backtest_compare_workspace_mode",
            label_visibility="collapsed",
            width="stretch",
        )
    else:
        st.radio(
            "Compare Workspace",
            options=mode_options,
            horizontal=True,
            key="backtest_compare_workspace_mode",
            label_visibility="collapsed",
        )

    if st.session_state.backtest_compare_workspace_mode == COMPARE_MODE_STRATEGY:
        _render_strategy_compare_workspace()
    else:
        _render_saved_portfolio_workspace()

__all__ = [name for name in globals() if not name.startswith("__")]
