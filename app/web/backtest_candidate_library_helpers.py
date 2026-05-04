from __future__ import annotations

import time
from datetime import datetime
from typing import Any

import pandas as pd

from app.web.runtime import (
    load_current_candidate_registry_latest,
    load_pre_live_candidate_registry_latest,
    run_dual_momentum_backtest_from_db,
    run_equal_weight_backtest_from_db,
    run_global_relative_strength_backtest_from_db,
    run_gtaa_backtest_from_db,
    run_quality_snapshot_strict_annual_backtest_from_db,
    run_quality_value_snapshot_strict_annual_backtest_from_db,
    run_risk_parity_trend_backtest_from_db,
    run_value_snapshot_strict_annual_backtest_from_db,
)
from app.web.runtime.backtest import (
    BacktestDataError,
    BacktestInputError,
    ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
    ETF_OPERABILITY_DEFAULT_MIN_AUM_B,
    ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
    ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    STRICT_DEFAULT_BENCHMARK_CONTRACT,
    STRICT_DEFAULT_DEFENSIVE_TICKERS,
    STRICT_DEFAULT_RISK_OFF_MODE,
    STRICT_DEFAULT_WEIGHTING_MODE,
    STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
    STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
    STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
    STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
    STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
    STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
    STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
    STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
    STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
    STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
    STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    QUALITY_STRICT_DEFAULT_FACTORS,
    VALUE_STRICT_DEFAULT_FACTORS,
)
from finance.sample import (
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_CASH_TICKER,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_SCORE_LOOKBACK_MONTHS,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_SCORE_WEIGHTS,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_SIGNAL_INTERVAL,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_TOP,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_TREND_FILTER_WINDOW,
    GLOBAL_RELATIVE_STRENGTH_SCORE_RETURN_COLUMNS,
    GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD,
    GTAA_DEFAULT_CRASH_GUARDRAIL_ENABLED,
    GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS,
    GTAA_DEFAULT_DEFENSIVE_TICKERS,
    GTAA_DEFAULT_RISK_OFF_MODE,
    GTAA_DEFAULT_SCORE_LOOKBACK_MONTHS,
    GTAA_DEFAULT_SCORE_WEIGHTS,
    GTAA_DEFAULT_TREND_FILTER_WINDOW,
    GTAA_SCORE_RETURN_COLUMNS,
)


ETF_REPLAY_STRATEGY_KEYS = {
    "equal_weight",
    "gtaa",
    "global_relative_strength",
    "risk_parity_trend",
    "dual_momentum",
}

STRICT_ANNUAL_REPLAY_STRATEGY_KEYS = {
    "quality_snapshot_strict_annual",
    "value_snapshot_strict_annual",
    "quality_value_snapshot_strict_annual",
}

SUPPORTED_REPLAY_STRATEGY_KEYS = ETF_REPLAY_STRATEGY_KEYS | STRICT_ANNUAL_REPLAY_STRATEGY_KEYS


# Return a readable display label for a current candidate row.
def candidate_library_record_label(record: dict[str, Any]) -> str:
    current = record.get("current") or {}
    pre_live = record.get("pre_live") or {}
    result = current.get("result") or {}
    title = current.get("title") or current.get("strategy_name") or current.get("registry_id") or "Candidate"
    status = pre_live.get("pre_live_status") or "no_pre_live_record"
    cagr = _format_percent(result.get("cagr"))
    mdd = _format_percent(result.get("mdd"))
    return f"{title} | {status} | CAGR {cagr} / MDD {mdd}"


# Load current candidates and attach the latest matching Pre-Live row when present.
def load_candidate_library_records() -> list[dict[str, Any]]:
    current_rows = load_current_candidate_registry_latest()
    pre_live_rows = load_pre_live_candidate_registry_latest()
    pre_live_by_candidate_id: dict[str, dict[str, Any]] = {}
    for row in pre_live_rows:
        candidate_id = str(row.get("source_candidate_registry_id") or "").strip()
        if candidate_id:
            pre_live_by_candidate_id[candidate_id] = row

    records: list[dict[str, Any]] = []
    for row in current_rows:
        registry_id = str(row.get("registry_id") or "").strip()
        if not registry_id:
            continue
        records.append(
            {
                "registry_id": registry_id,
                "current": row,
                "pre_live": pre_live_by_candidate_id.get(registry_id),
            }
        )

    return sorted(records, key=_candidate_sort_key)


# Convert candidate records into the compact table shown in Candidate Library.
def build_candidate_library_rows(records: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        current = record.get("current") or {}
        pre_live = record.get("pre_live") or {}
        result = current.get("result") or {}
        contract = current.get("contract") or {}
        tickers = list(contract.get("tickers") or [])
        rows.append(
            {
                "_record_index": index,
                "Recorded At": current.get("recorded_at"),
                "Title": current.get("title") or current.get("strategy_name"),
                "Family": current.get("strategy_family"),
                "Role": current.get("candidate_role"),
                "Pre-Live": pre_live.get("pre_live_status") or "-",
                "CAGR": result.get("cagr"),
                "MDD": result.get("mdd"),
                "Sharpe": result.get("sharpe"),
                "End Balance": result.get("end_balance"),
                "Top": contract.get("top") or contract.get("top_n"),
                "Interval": contract.get("interval") or contract.get("rebalance_interval"),
                "Benchmark": result.get("benchmark_ticker") or contract.get("benchmark_ticker"),
                "Universe": ", ".join(tickers),
                "Registry ID": current.get("registry_id"),
                "_search_text": " ".join(
                    str(value or "")
                    for value in [
                        current.get("registry_id"),
                        current.get("title"),
                        current.get("strategy_name"),
                        current.get("strategy_family"),
                        pre_live.get("pre_live_status"),
                        " ".join(tickers),
                    ]
                ).lower(),
            }
        )
    return pd.DataFrame(rows)


# Build a replay payload from a current candidate's persisted contract.
def build_candidate_replay_payload(current_row: dict[str, Any]) -> dict[str, Any]:
    contract = dict(current_row.get("contract") or {})
    execution_context = dict(current_row.get("execution_context") or {})
    compare_prefill = dict(current_row.get("compare_prefill") or {})
    period = dict(current_row.get("period") or {})
    strategy_key = (
        compare_prefill.get("strategy_key")
        or _strategy_family_to_key(current_row.get("strategy_family"))
    )
    if strategy_key not in SUPPORTED_REPLAY_STRATEGY_KEYS:
        raise BacktestInputError(
            f"Candidate Library replay supports these strategy candidates: {sorted(SUPPORTED_REPLAY_STRATEGY_KEYS)}"
        )

    payload = {
        "strategy_key": strategy_key,
        "strategy_name": current_row.get("title") or current_row.get("strategy_name") or strategy_key,
        "tickers": list(contract.get("tickers") or []),
        "start": execution_context.get("start") or period.get("start") or contract.get("start"),
        "end": execution_context.get("end") or period.get("end") or contract.get("end"),
        "timeframe": execution_context.get("timeframe") or contract.get("timeframe") or "1d",
        "option": execution_context.get("option") or contract.get("option") or "month_end",
        "universe_mode": contract.get("universe_mode") or "manual",
        "preset_name": contract.get("preset_name"),
        "benchmark_ticker": contract.get("benchmark_ticker") or ETF_REAL_MONEY_DEFAULT_BENCHMARK,
        "guardrail_reference_ticker": contract.get("guardrail_reference_ticker"),
        "min_price_filter": contract.get("min_price_filter", ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
        "transaction_cost_bps": contract.get(
            "transaction_cost_bps",
            ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
        ),
        "promotion_min_etf_aum_b": contract.get("promotion_min_etf_aum_b", ETF_OPERABILITY_DEFAULT_MIN_AUM_B),
        "promotion_max_bid_ask_spread_pct": contract.get(
            "promotion_max_bid_ask_spread_pct",
            ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
        ),
        "promotion_min_benchmark_coverage": contract.get("promotion_min_benchmark_coverage"),
        "promotion_min_net_cagr_spread": contract.get("promotion_min_net_cagr_spread"),
        "promotion_min_liquidity_clean_coverage": contract.get("promotion_min_liquidity_clean_coverage"),
        "promotion_max_underperformance_share": contract.get("promotion_max_underperformance_share"),
        "promotion_min_worst_rolling_excess_return": contract.get(
            "promotion_min_worst_rolling_excess_return"
        ),
        "promotion_max_strategy_drawdown": contract.get("promotion_max_strategy_drawdown"),
        "promotion_max_drawdown_gap_vs_benchmark": contract.get("promotion_max_drawdown_gap_vs_benchmark"),
    }

    if not payload["tickers"]:
        raise BacktestInputError("Candidate contract has no tickers.")
    if not payload["start"] or not payload["end"]:
        raise BacktestInputError("Candidate contract has no replay period.")

    if strategy_key == "equal_weight":
        payload["rebalance_interval"] = contract.get("rebalance_interval") or contract.get("interval") or 12
    elif strategy_key == "gtaa":
        payload.update(
            {
                "top": contract.get("top") or contract.get("top_n") or 3,
                "interval": contract.get("interval") or 1,
                "score_lookback_months": contract.get("score_lookback_months") or list(GTAA_DEFAULT_SCORE_LOOKBACK_MONTHS),
                "score_return_columns": contract.get("score_return_columns") or list(GTAA_SCORE_RETURN_COLUMNS),
                "score_weights": contract.get("score_weights") or dict(GTAA_DEFAULT_SCORE_WEIGHTS),
                "trend_filter_window": contract.get("trend_filter_window", GTAA_DEFAULT_TREND_FILTER_WINDOW),
                "risk_off_mode": contract.get("risk_off_mode", GTAA_DEFAULT_RISK_OFF_MODE),
                "defensive_tickers": contract.get("defensive_tickers") or list(GTAA_DEFAULT_DEFENSIVE_TICKERS),
                "market_regime_enabled": contract.get("market_regime_enabled", False),
                "market_regime_window": contract.get("market_regime_window", STRICT_MARKET_REGIME_DEFAULT_WINDOW),
                "market_regime_benchmark": contract.get("market_regime_benchmark", STRICT_MARKET_REGIME_DEFAULT_BENCHMARK),
                "crash_guardrail_enabled": contract.get(
                    "crash_guardrail_enabled",
                    GTAA_DEFAULT_CRASH_GUARDRAIL_ENABLED,
                ),
                "crash_guardrail_drawdown_threshold": contract.get(
                    "crash_guardrail_drawdown_threshold",
                    GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD,
                ),
                "crash_guardrail_lookback_months": contract.get(
                    "crash_guardrail_lookback_months",
                    GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS,
                ),
            }
        )
    elif strategy_key == "global_relative_strength":
        payload.update(
            {
                "cash_ticker": contract.get("cash_ticker", GLOBAL_RELATIVE_STRENGTH_DEFAULT_CASH_TICKER),
                "top": contract.get("top") or contract.get("top_n") or GLOBAL_RELATIVE_STRENGTH_DEFAULT_TOP,
                "interval": contract.get("interval") or GLOBAL_RELATIVE_STRENGTH_DEFAULT_SIGNAL_INTERVAL,
                "score_lookback_months": contract.get("score_lookback_months")
                or list(GLOBAL_RELATIVE_STRENGTH_DEFAULT_SCORE_LOOKBACK_MONTHS),
                "score_return_columns": contract.get("score_return_columns")
                or list(GLOBAL_RELATIVE_STRENGTH_SCORE_RETURN_COLUMNS),
                "score_weights": contract.get("score_weights")
                or dict(GLOBAL_RELATIVE_STRENGTH_DEFAULT_SCORE_WEIGHTS),
                "trend_filter_window": contract.get(
                    "trend_filter_window",
                    GLOBAL_RELATIVE_STRENGTH_DEFAULT_TREND_FILTER_WINDOW,
                ),
            }
        )
    elif strategy_key == "risk_parity_trend":
        payload.update(
            {
                "rebalance_interval": contract.get("rebalance_interval") or contract.get("interval") or 1,
                "vol_window": contract.get("vol_window") or 6,
            }
        )
    elif strategy_key == "dual_momentum":
        payload.update(
            {
                "top": contract.get("top") or contract.get("top_n") or 1,
                "rebalance_interval": contract.get("rebalance_interval") or contract.get("interval") or 1,
            }
        )
    elif strategy_key in STRICT_ANNUAL_REPLAY_STRATEGY_KEYS:
        payload.update(_strict_annual_payload_values(strategy_key, contract))

    payload.update(_guardrail_payload_values(contract))
    return payload


# Re-run a candidate payload and return the full UI result bundle.
def run_candidate_replay_payload(payload: dict[str, Any], *, current_row: dict[str, Any]) -> dict[str, Any]:
    started_at = time.perf_counter()
    strategy_key = payload.get("strategy_key")
    try:
        if strategy_key == "equal_weight":
            bundle = run_equal_weight_backtest_from_db(
                tickers=payload["tickers"],
                start=payload["start"],
                end=payload["end"],
                timeframe=payload["timeframe"],
                option=payload["option"],
                rebalance_interval=payload["rebalance_interval"],
                min_price_filter=payload.get("min_price_filter", ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
                transaction_cost_bps=payload.get("transaction_cost_bps", ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS),
                benchmark_ticker=payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
                guardrail_reference_ticker=payload.get("guardrail_reference_ticker"),
                promotion_min_etf_aum_b=payload.get("promotion_min_etf_aum_b", ETF_OPERABILITY_DEFAULT_MIN_AUM_B),
                promotion_max_bid_ask_spread_pct=payload.get(
                    "promotion_max_bid_ask_spread_pct",
                    ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
                ),
                promotion_min_benchmark_coverage=payload.get("promotion_min_benchmark_coverage"),
                promotion_min_net_cagr_spread=payload.get("promotion_min_net_cagr_spread"),
                promotion_min_liquidity_clean_coverage=payload.get("promotion_min_liquidity_clean_coverage"),
                promotion_max_underperformance_share=payload.get("promotion_max_underperformance_share"),
                promotion_min_worst_rolling_excess_return=payload.get(
                    "promotion_min_worst_rolling_excess_return"
                ),
                promotion_max_strategy_drawdown=payload.get("promotion_max_strategy_drawdown"),
                promotion_max_drawdown_gap_vs_benchmark=payload.get("promotion_max_drawdown_gap_vs_benchmark"),
                universe_mode=payload["universe_mode"],
                preset_name=payload["preset_name"],
            )
        elif strategy_key == "gtaa":
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
                crash_guardrail_drawdown_threshold=payload.get(
                    "crash_guardrail_drawdown_threshold",
                    GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD,
                ),
                crash_guardrail_lookback_months=payload.get(
                    "crash_guardrail_lookback_months",
                    GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS,
                ),
                min_price_filter=payload.get("min_price_filter", ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
                transaction_cost_bps=payload.get("transaction_cost_bps", ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS),
                benchmark_ticker=payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
                underperformance_guardrail_enabled=payload.get(
                    "underperformance_guardrail_enabled",
                    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
                ),
                underperformance_guardrail_window_months=payload.get(
                    "underperformance_guardrail_window_months",
                    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
                ),
                underperformance_guardrail_threshold=payload.get(
                    "underperformance_guardrail_threshold",
                    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
                ),
                drawdown_guardrail_enabled=payload.get(
                    "drawdown_guardrail_enabled",
                    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
                ),
                drawdown_guardrail_window_months=payload.get(
                    "drawdown_guardrail_window_months",
                    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
                ),
                drawdown_guardrail_strategy_threshold=payload.get(
                    "drawdown_guardrail_strategy_threshold",
                    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
                ),
                drawdown_guardrail_gap_threshold=payload.get(
                    "drawdown_guardrail_gap_threshold",
                    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
                ),
                promotion_min_etf_aum_b=payload.get("promotion_min_etf_aum_b", ETF_OPERABILITY_DEFAULT_MIN_AUM_B),
                promotion_max_bid_ask_spread_pct=payload.get(
                    "promotion_max_bid_ask_spread_pct",
                    ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
                ),
                universe_mode=payload["universe_mode"],
                preset_name=payload["preset_name"],
            )
        elif strategy_key == "global_relative_strength":
            bundle = run_global_relative_strength_backtest_from_db(
                tickers=payload["tickers"],
                cash_ticker=payload.get("cash_ticker", GLOBAL_RELATIVE_STRENGTH_DEFAULT_CASH_TICKER),
                start=payload["start"],
                end=payload["end"],
                timeframe=payload["timeframe"],
                option=payload["option"],
                top=payload.get("top", GLOBAL_RELATIVE_STRENGTH_DEFAULT_TOP),
                interval=payload.get("interval", GLOBAL_RELATIVE_STRENGTH_DEFAULT_SIGNAL_INTERVAL),
                score_lookback_months=payload.get("score_lookback_months"),
                score_return_columns=payload.get("score_return_columns"),
                score_weights=payload.get("score_weights"),
                trend_filter_window=payload.get(
                    "trend_filter_window",
                    GLOBAL_RELATIVE_STRENGTH_DEFAULT_TREND_FILTER_WINDOW,
                ),
                min_price_filter=payload.get("min_price_filter", ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
                transaction_cost_bps=payload.get("transaction_cost_bps", ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS),
                benchmark_ticker=payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
                promotion_min_etf_aum_b=payload.get("promotion_min_etf_aum_b", ETF_OPERABILITY_DEFAULT_MIN_AUM_B),
                promotion_max_bid_ask_spread_pct=payload.get(
                    "promotion_max_bid_ask_spread_pct",
                    ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
                ),
                universe_mode=payload["universe_mode"],
                preset_name=payload["preset_name"],
            )
        elif strategy_key == "risk_parity_trend":
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
                universe_mode=payload["universe_mode"],
                preset_name=payload["preset_name"],
            )
        elif strategy_key == "dual_momentum":
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
                universe_mode=payload["universe_mode"],
                preset_name=payload["preset_name"],
            )
        elif strategy_key == "quality_snapshot_strict_annual":
            bundle = run_quality_snapshot_strict_annual_backtest_from_db(
                tickers=payload["tickers"],
                start=payload["start"],
                end=payload["end"],
                timeframe=payload["timeframe"],
                option=payload["option"],
                quality_factors=payload["quality_factors"],
                **_strict_annual_runtime_kwargs(payload),
            )
        elif strategy_key == "value_snapshot_strict_annual":
            bundle = run_value_snapshot_strict_annual_backtest_from_db(
                tickers=payload["tickers"],
                start=payload["start"],
                end=payload["end"],
                timeframe=payload["timeframe"],
                option=payload["option"],
                value_factors=payload["value_factors"],
                **_strict_annual_runtime_kwargs(payload),
            )
        elif strategy_key == "quality_value_snapshot_strict_annual":
            bundle = run_quality_value_snapshot_strict_annual_backtest_from_db(
                tickers=payload["tickers"],
                start=payload["start"],
                end=payload["end"],
                timeframe=payload["timeframe"],
                option=payload["option"],
                quality_factors=payload["quality_factors"],
                value_factors=payload["value_factors"],
                **_strict_annual_runtime_kwargs(payload),
            )
        else:
            raise BacktestInputError(f"Unsupported candidate replay strategy key: {strategy_key}")
    except (BacktestInputError, BacktestDataError):
        raise

    elapsed_seconds = time.perf_counter() - started_at
    bundle = dict(bundle)
    meta = dict(bundle.get("meta") or {})
    meta["ui_elapsed_seconds"] = round(elapsed_seconds, 3)
    meta["candidate_library_replay"] = {
        "registry_id": current_row.get("registry_id"),
        "revision_id": current_row.get("revision_id"),
        "source_recorded_at": current_row.get("recorded_at"),
        "replayed_at": datetime.now().isoformat(timespec="seconds"),
    }
    bundle["meta"] = meta
    return bundle


# Create compact cards for the selected candidate snapshot.
def build_candidate_snapshot_cards(record: dict[str, Any]) -> list[dict[str, Any]]:
    current = record.get("current") or {}
    pre_live = record.get("pre_live") or {}
    result = current.get("result") or {}
    contract = current.get("contract") or {}
    blockers = list(result.get("blockers") or [])
    return [
        {
            "title": "Candidate",
            "value": current.get("title") or current.get("strategy_name") or current.get("registry_id"),
            "detail": current.get("registry_id"),
            "tone": "positive" if str(current.get("record_type") or "") == "current_candidate" else "neutral",
        },
        {
            "title": "Stored Result",
            "value": f"{_format_percent(result.get('cagr'))} CAGR",
            "detail": f"MDD {_format_percent(result.get('mdd'))}, Sharpe {_format_number(result.get('sharpe'))}",
            "tone": "positive",
        },
        {
            "title": "Replay Contract",
            "value": f"top {contract.get('top') or contract.get('top_n') or '-'} / interval {contract.get('interval') or contract.get('rebalance_interval') or '-'}",
            "detail": f"{len(contract.get('tickers') or [])} symbols, benchmark {result.get('benchmark_ticker') or contract.get('benchmark_ticker') or '-'}",
            "tone": "neutral",
        },
        {
            "title": "Operating State",
            "value": pre_live.get("pre_live_status") or "No Pre-Live Record",
            "detail": f"Blockers {len(blockers)}",
            "tone": "positive" if pre_live.get("pre_live_status") in {"paper_tracking", "watchlist"} and not blockers else "warning",
        },
    ]


# Create concise metadata badges for the selected candidate.
def build_candidate_badges(record: dict[str, Any]) -> list[dict[str, Any]]:
    current = record.get("current") or {}
    result = current.get("result") or {}
    contract = current.get("contract") or {}
    return [
        {"label": "Promotion", "value": result.get("promotion") or "-", "tone": "positive"},
        {"label": "Shortlist", "value": result.get("shortlist") or "-", "tone": "neutral"},
        {"label": "Deployment", "value": result.get("deployment") or "-", "tone": "neutral"},
        {"label": "Universe", "value": ", ".join(contract.get("tickers") or []), "tone": "neutral"},
    ]


def _candidate_sort_key(record: dict[str, Any]) -> tuple[str, str]:
    current = record.get("current") or {}
    return (str(current.get("strategy_family") or ""), str(current.get("title") or ""))


def _strategy_family_to_key(strategy_family: Any) -> str:
    normalized = str(strategy_family or "").strip().lower()
    if normalized in {"equal_weight", "gtaa", "global_relative_strength", "risk_parity_trend", "dual_momentum"}:
        return normalized
    if normalized == "quality":
        return "quality_snapshot_strict_annual"
    if normalized == "value":
        return "value_snapshot_strict_annual"
    if normalized == "quality_value":
        return "quality_value_snapshot_strict_annual"
    return normalized


# Restore strict annual candidate settings from the compact registry contract.
def _strict_annual_payload_values(strategy_key: str, contract: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "top": contract.get("top") or contract.get("top_n") or 10,
        "rebalance_interval": contract.get("rebalance_interval") or contract.get("interval") or 1,
        "min_history_months_filter": contract.get(
            "min_history_months_filter",
            STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
        ),
        "min_avg_dollar_volume_20d_m_filter": contract.get(
            "min_avg_dollar_volume_20d_m_filter",
            STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
        ),
        "benchmark_contract": contract.get("benchmark_contract", STRICT_DEFAULT_BENCHMARK_CONTRACT),
        "guardrail_reference_ticker": contract.get(
            "guardrail_reference_ticker",
            contract.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
        ),
        "promotion_min_benchmark_coverage": contract.get(
            "promotion_min_benchmark_coverage",
            STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
        ),
        "promotion_min_net_cagr_spread": contract.get(
            "promotion_min_net_cagr_spread",
            STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
        ),
        "promotion_min_liquidity_clean_coverage": contract.get(
            "promotion_min_liquidity_clean_coverage",
            STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
        ),
        "promotion_max_underperformance_share": contract.get(
            "promotion_max_underperformance_share",
            STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
        ),
        "promotion_min_worst_rolling_excess_return": contract.get(
            "promotion_min_worst_rolling_excess_return",
            STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
        ),
        "promotion_max_strategy_drawdown": contract.get(
            "promotion_max_strategy_drawdown",
            STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
        ),
        "promotion_max_drawdown_gap_vs_benchmark": contract.get(
            "promotion_max_drawdown_gap_vs_benchmark",
            STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
        ),
        "trend_filter_enabled": contract.get("trend_filter_enabled", False),
        "trend_filter_window": contract.get("trend_filter_window", 200),
        "weighting_mode": contract.get("weighting_mode", STRICT_DEFAULT_WEIGHTING_MODE),
        "rejected_slot_handling_mode": contract.get("rejected_slot_handling_mode"),
        "rejected_slot_fill_enabled": contract.get(
            "rejected_slot_fill_enabled",
            STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
        ),
        "partial_cash_retention_enabled": contract.get(
            "partial_cash_retention_enabled",
            STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
        ),
        "risk_off_mode": contract.get("risk_off_mode", STRICT_DEFAULT_RISK_OFF_MODE),
        "defensive_tickers": contract.get("defensive_tickers") or list(STRICT_DEFAULT_DEFENSIVE_TICKERS),
        "market_regime_enabled": contract.get("market_regime_enabled", False),
        "market_regime_window": contract.get("market_regime_window", STRICT_MARKET_REGIME_DEFAULT_WINDOW),
        "market_regime_benchmark": contract.get(
            "market_regime_benchmark",
            STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
        ),
        "universe_contract": contract.get("universe_contract"),
        "dynamic_candidate_tickers": contract.get("dynamic_candidate_tickers"),
        "dynamic_target_size": contract.get("dynamic_target_size"),
    }
    if strategy_key in {"quality_snapshot_strict_annual", "quality_value_snapshot_strict_annual"}:
        payload["quality_factors"] = contract.get("quality_factors") or list(QUALITY_STRICT_DEFAULT_FACTORS)
    if strategy_key in {"value_snapshot_strict_annual", "quality_value_snapshot_strict_annual"}:
        payload["value_factors"] = contract.get("value_factors") or list(VALUE_STRICT_DEFAULT_FACTORS)
    return payload


# Keep the strict annual replay dispatch aligned with the Single Strategy runner.
def _strict_annual_runtime_kwargs(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "top_n": payload.get("top", 10),
        "rebalance_interval": payload.get("rebalance_interval", 1),
        "min_price_filter": payload.get("min_price_filter", ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
        "min_history_months_filter": payload.get(
            "min_history_months_filter",
            STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
        ),
        "min_avg_dollar_volume_20d_m_filter": payload.get(
            "min_avg_dollar_volume_20d_m_filter",
            STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
        ),
        "transaction_cost_bps": payload.get(
            "transaction_cost_bps",
            ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
        ),
        "benchmark_contract": payload.get("benchmark_contract", STRICT_DEFAULT_BENCHMARK_CONTRACT),
        "benchmark_ticker": payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
        "guardrail_reference_ticker": payload.get(
            "guardrail_reference_ticker",
            payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
        ),
        "promotion_min_benchmark_coverage": payload.get(
            "promotion_min_benchmark_coverage",
            STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
        ),
        "promotion_min_net_cagr_spread": payload.get(
            "promotion_min_net_cagr_spread",
            STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
        ),
        "promotion_min_liquidity_clean_coverage": payload.get(
            "promotion_min_liquidity_clean_coverage",
            STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
        ),
        "promotion_max_underperformance_share": payload.get(
            "promotion_max_underperformance_share",
            STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
        ),
        "promotion_min_worst_rolling_excess_return": payload.get(
            "promotion_min_worst_rolling_excess_return",
            STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
        ),
        "promotion_max_strategy_drawdown": payload.get(
            "promotion_max_strategy_drawdown",
            STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
        ),
        "promotion_max_drawdown_gap_vs_benchmark": payload.get(
            "promotion_max_drawdown_gap_vs_benchmark",
            STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
        ),
        "trend_filter_enabled": payload.get("trend_filter_enabled", False),
        "trend_filter_window": payload.get("trend_filter_window", 200),
        "weighting_mode": payload.get("weighting_mode", STRICT_DEFAULT_WEIGHTING_MODE),
        "rejected_slot_handling_mode": payload.get("rejected_slot_handling_mode"),
        "rejected_slot_fill_enabled": payload.get(
            "rejected_slot_fill_enabled",
            STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
        ),
        "partial_cash_retention_enabled": payload.get(
            "partial_cash_retention_enabled",
            STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
        ),
        "risk_off_mode": payload.get("risk_off_mode", STRICT_DEFAULT_RISK_OFF_MODE),
        "defensive_tickers": payload.get("defensive_tickers", STRICT_DEFAULT_DEFENSIVE_TICKERS),
        "market_regime_enabled": payload.get("market_regime_enabled", False),
        "market_regime_window": payload.get("market_regime_window", STRICT_MARKET_REGIME_DEFAULT_WINDOW),
        "market_regime_benchmark": payload.get(
            "market_regime_benchmark",
            STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
        ),
        "underperformance_guardrail_enabled": payload.get(
            "underperformance_guardrail_enabled",
            STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
        ),
        "underperformance_guardrail_window_months": payload.get(
            "underperformance_guardrail_window_months",
            STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
        ),
        "underperformance_guardrail_threshold": payload.get(
            "underperformance_guardrail_threshold",
            STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
        ),
        "drawdown_guardrail_enabled": payload.get(
            "drawdown_guardrail_enabled",
            STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
        ),
        "drawdown_guardrail_window_months": payload.get(
            "drawdown_guardrail_window_months",
            STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
        ),
        "drawdown_guardrail_strategy_threshold": payload.get(
            "drawdown_guardrail_strategy_threshold",
            STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
        ),
        "drawdown_guardrail_gap_threshold": payload.get(
            "drawdown_guardrail_gap_threshold",
            STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
        ),
        "universe_mode": payload["universe_mode"],
        "preset_name": payload["preset_name"],
        "universe_contract": payload.get("universe_contract"),
        "dynamic_candidate_tickers": payload.get("dynamic_candidate_tickers"),
        "dynamic_target_size": payload.get("dynamic_target_size"),
    }


def _guardrail_payload_values(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "underperformance_guardrail_enabled": contract.get(
            "underperformance_guardrail_enabled",
            STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
        ),
        "underperformance_guardrail_window_months": contract.get(
            "underperformance_guardrail_window_months",
            STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
        ),
        "underperformance_guardrail_threshold": contract.get(
            "underperformance_guardrail_threshold",
            STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
        ),
        "drawdown_guardrail_enabled": contract.get(
            "drawdown_guardrail_enabled",
            STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
        ),
        "drawdown_guardrail_window_months": contract.get(
            "drawdown_guardrail_window_months",
            STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
        ),
        "drawdown_guardrail_strategy_threshold": contract.get(
            "drawdown_guardrail_strategy_threshold",
            STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
        ),
        "drawdown_guardrail_gap_threshold": contract.get(
            "drawdown_guardrail_gap_threshold",
            STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
        ),
    }


def _format_percent(value: Any) -> str:
    try:
        return f"{float(value):.2%}"
    except (TypeError, ValueError):
        return "-"


def _format_number(value: Any) -> str:
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return "-"
