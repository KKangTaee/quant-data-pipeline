from __future__ import annotations

import json
from datetime import date
from typing import Any

import numpy as np
import pandas as pd

from app.web.runtime.backtest import (
    ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    GTAA_DEFAULT_SIGNAL_INTERVAL,
    STRICT_DEFAULT_BENCHMARK_CONTRACT,
    STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
    STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
    STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
    STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
    STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
    STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
    STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
)
from app.web.backtest_strategy_catalog import (
    strategy_key_to_display_name as catalog_strategy_key_to_display_name,
)
from finance.sample import (
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_SIGNAL_INTERVAL,
    GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD,
    GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS,
    GTAA_DEFAULT_RISK_OFF_MODE,
    STRICT_DEFAULT_WEIGHTING_MODE,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
    STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
    STRICT_TREND_FILTER_DEFAULT_WINDOW,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
)


# Map a stored strategy key to the canonical UI display name used in replay summaries.
def _strategy_key_to_display_name(strategy_key: str | None) -> str | None:
    return catalog_strategy_key_to_display_name(strategy_key)


# Summarize a stored run's key settings into the compact History table column.
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
    if meta.get("cash_ticker"):
        parts.append(f"cash_ticker={meta['cash_ticker']}")
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


# Build the searchable / sortable table model for persisted backtest runs.
def _build_backtest_history_rows(history: list[dict[str, Any]]) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []

    for item in history:
        summary = item.get("summary") or {}
        context = item.get("context") or {}
        gate_snapshot = item.get("gate_snapshot") or {}
        promotion_decision = item.get("promotion_decision") or gate_snapshot.get("promotion_decision")
        shortlist_status = item.get("shortlist_status") or gate_snapshot.get("shortlist_status")
        deployment_status = item.get("deployment_readiness_status") or gate_snapshot.get("deployment_readiness_status")
        strategy_name = summary.get("strategy_name") or item.get("strategy_key") or "Comparison"
        selected_strategies = context.get("selected_strategies", [])
        search_text = " ".join(
            [
                str(item.get("run_kind", "")),
                str(strategy_name),
                " ".join(item.get("tickers", [])),
                " ".join(selected_strategies),
                str(item.get("preset_name", "")),
                str(promotion_decision or ""),
                str(shortlist_status or ""),
                str(deployment_status or ""),
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
                "promotion": promotion_decision,
                "shortlist": shortlist_status,
                "deployment": deployment_status,
                "tickers": ", ".join(item.get("tickers", [])),
                "params": _summarize_params(item),
                "selected_strategies": ", ".join(selected_strategies),
                "_search_text": search_text,
            }
        )
        records.append(item)

    return pd.DataFrame(rows), records


# Format a stable selectbox label for one stored History record.
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


# Pick the most readable strategy name stored in a History record.
def _history_strategy_display_name(record: dict[str, Any]) -> str:
    summary = record.get("summary") or {}
    return summary.get("strategy_name") or record.get("strategy_key") or "Unknown Strategy"


# Reconstruct the Single Strategy runtime payload from a persisted History record.
def _build_history_payload(record: dict[str, Any]) -> dict[str, Any] | None:
    strategy_key = record.get("strategy_key")
    if strategy_key not in {
        "equal_weight",
        "gtaa",
        "global_relative_strength",
        "risk_parity_trend",
        "dual_momentum",
    }:
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
    if record.get("cash_ticker") is not None:
        payload["cash_ticker"] = str(record.get("cash_ticker") or "").strip().upper()
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
    if record.get("weighting_mode") is not None:
        payload["weighting_mode"] = str(record.get("weighting_mode") or STRICT_DEFAULT_WEIGHTING_MODE).strip()
    if record.get("rejected_slot_handling_mode") is not None:
        payload["rejected_slot_handling_mode"] = str(record.get("rejected_slot_handling_mode") or "").strip()
    if record.get("rejected_slot_fill_enabled") is not None:
        payload["rejected_slot_fill_enabled"] = bool(record.get("rejected_slot_fill_enabled"))
    if record.get("partial_cash_retention_enabled") is not None:
        payload["partial_cash_retention_enabled"] = bool(record.get("partial_cash_retention_enabled"))
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
    if record.get("guardrail_reference_ticker") is not None:
        payload["guardrail_reference_ticker"] = (
            str(record.get("guardrail_reference_ticker") or "").strip().upper()
            or payload.get("benchmark_ticker")
            or ETF_REAL_MONEY_DEFAULT_BENCHMARK
        )
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
    if record.get("research_source") is not None:
        payload["research_source"] = record.get("research_source")

    # GTAA stores cadence in rebalance_interval for history summarization; map it back.
    if strategy_key == "gtaa":
        payload["interval"] = int(record.get("rebalance_interval") or GTAA_DEFAULT_SIGNAL_INTERVAL)
    elif strategy_key == "global_relative_strength":
        payload["interval"] = int(
            record.get("rebalance_interval") or GLOBAL_RELATIVE_STRENGTH_DEFAULT_SIGNAL_INTERVAL
        )
    return payload


# Decide whether a History field contains a meaningful replay value.
def _history_value_is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, (float, np.floating)) and pd.isna(value):
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


# Convert stored History values into compact table text.
def _format_history_parity_value(value: Any) -> str:
    if not _history_value_is_present(value):
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


# Return only the replay fields that are present in a History record.
def _history_record_field_pairs(record: dict[str, Any], fields: list[str]) -> list[tuple[str, Any]]:
    pairs: list[tuple[str, Any]] = []
    for field in fields:
        value = record.get(field)
        if _history_value_is_present(value):
            pairs.append((field, value))
    return pairs


# Summarize stored replay fields into a compact key=value sentence.
def _history_field_summary(record: dict[str, Any], fields: list[str]) -> str:
    pairs = _history_record_field_pairs(record, fields)
    if not pairs:
        return "-"
    return " / ".join(f"{field}={_format_history_parity_value(value)}" for field, value in pairs)


# Describe the Real-Money / Guardrail scope that applies to one strategy family.
def _real_money_guardrail_scope_for_strategy(
    strategy_name: str | None,
    strategy_key: str | None = None,
) -> dict[str, str]:
    name = str(strategy_name or "").strip()
    key = str(strategy_key or "").strip()

    annual_strict_keys = {
        "quality_snapshot_strict_annual",
        "value_snapshot_strict_annual",
        "quality_value_snapshot_strict_annual",
    }
    quarterly_keys = {
        "quality_snapshot_strict_quarterly_prototype",
        "value_snapshot_strict_quarterly_prototype",
        "quality_value_snapshot_strict_quarterly_prototype",
    }

    if name.endswith("(Strict Annual)") or key in annual_strict_keys:
        return {
            "real_money_scope": "Full strict equity Real-Money surface",
            "guardrail_scope": "Underperformance / Drawdown guardrails + Guardrail Reference Ticker",
            "interpretation": "Phase 28 기준 실전 검증 surface의 기준선입니다. history/replay에서 benchmark, investability, promotion, guardrail 입력이 유지되어야 합니다.",
        }
    if name.endswith("(Strict Quarterly Prototype)") or key in quarterly_keys:
        return {
            "real_money_scope": "Deferred: quarterly prototype은 아직 promotion 대상 아님",
            "guardrail_scope": "Portfolio handling risk-off는 지원, Real-Money guardrail surface는 보류",
            "interpretation": "quarterly는 cadence/replay 검증 단계입니다. annual strict와 같은 실전 승격 후보로 읽지 않습니다.",
        }
    if name == "Global Relative Strength" or key == "global_relative_strength":
        return {
            "real_money_scope": "ETF operability + cost / benchmark first pass",
            "guardrail_scope": "Trend safety net 중심, ETF underperformance/drawdown guardrail은 아직 없음",
            "interpretation": "가격 기반 ETF 전략입니다. AUM/spread/cost/benchmark는 보지만, annual strict식 promotion guardrail과 동일하게 보지 않습니다.",
        }
    if name == "GTAA" or key == "gtaa":
        return {
            "real_money_scope": "ETF Real-Money first pass",
            "guardrail_scope": "ETF underperformance / drawdown guardrails + tactical risk-off / crash guardrail",
            "interpretation": "ETF tactical 전략입니다. annual strict와 데이터 구조는 다르지만 ETF용 guardrail 입력은 replay에서 유지되어야 합니다.",
        }
    if name in {"Risk Parity Trend", "Dual Momentum"} or key in {"risk_parity_trend", "dual_momentum"}:
        return {
            "real_money_scope": "ETF Real-Money first pass",
            "guardrail_scope": "ETF underperformance / drawdown guardrails",
            "interpretation": "가격 기반 ETF 전략입니다. 비용, benchmark, ETF guardrail 입력이 저장 / 재실행에서 유지되어야 합니다.",
        }
    if name == "Equal Weight" or key == "equal_weight":
        return {
            "real_money_scope": "Not a promotion target",
            "guardrail_scope": "No dedicated guardrail surface",
            "interpretation": "비교 기준선 또는 단순 baseline입니다. 실전 후보 승격 판단 대상으로 보지 않습니다.",
        }
    return {
        "real_money_scope": "개별 전략 확인 필요",
        "guardrail_scope": "개별 전략 확인 필요",
        "interpretation": "Phase 28 parity map에 아직 명시되지 않은 전략입니다.",
    }


# Select the replay fields that matter for each strategy family's operating scope.
def _real_money_guardrail_replay_fields_for_strategy(
    strategy_name: str | None,
    strategy_key: str | None = None,
) -> list[str]:
    name = str(strategy_name or "").strip()
    key = str(strategy_key or "").strip()
    if name.endswith("(Strict Annual)") or key in {
        "quality_snapshot_strict_annual",
        "value_snapshot_strict_annual",
        "quality_value_snapshot_strict_annual",
    }:
        return [
            "benchmark_contract",
            "benchmark_ticker",
            "guardrail_reference_ticker",
            "min_price_filter",
            "min_history_months_filter",
            "min_avg_dollar_volume_20d_m_filter",
            "transaction_cost_bps",
            "promotion_min_benchmark_coverage",
            "promotion_min_net_cagr_spread",
            "promotion_max_underperformance_share",
            "promotion_max_strategy_drawdown",
            "underperformance_guardrail_enabled",
            "drawdown_guardrail_enabled",
        ]
    if name.endswith("(Strict Quarterly Prototype)") or key in {
        "quality_snapshot_strict_quarterly_prototype",
        "value_snapshot_strict_quarterly_prototype",
        "quality_value_snapshot_strict_quarterly_prototype",
    }:
        return [
            "weighting_mode",
            "rejected_slot_handling_mode",
            "risk_off_mode",
            "defensive_tickers",
            "market_regime_enabled",
            "market_regime_window",
            "market_regime_benchmark",
        ]
    if name == "Global Relative Strength" or key == "global_relative_strength":
        return [
            "benchmark_ticker",
            "min_price_filter",
            "transaction_cost_bps",
            "promotion_min_etf_aum_b",
            "promotion_max_bid_ask_spread_pct",
            "trend_filter_window",
            "cash_ticker",
        ]
    if name == "GTAA" or key == "gtaa":
        return [
            "benchmark_ticker",
            "min_price_filter",
            "transaction_cost_bps",
            "promotion_min_etf_aum_b",
            "promotion_max_bid_ask_spread_pct",
            "underperformance_guardrail_enabled",
            "drawdown_guardrail_enabled",
            "risk_off_mode",
            "crash_guardrail_enabled",
        ]
    if name in {"Risk Parity Trend", "Dual Momentum"} or key in {"risk_parity_trend", "dual_momentum"}:
        return [
            "benchmark_ticker",
            "min_price_filter",
            "transaction_cost_bps",
            "promotion_min_etf_aum_b",
            "promotion_max_bid_ask_spread_pct",
            "underperformance_guardrail_enabled",
            "drawdown_guardrail_enabled",
        ]
    return ["benchmark_ticker", "min_price_filter", "transaction_cost_bps"]


# Build the shared Real-Money / Guardrail scope table used by Compare, saved portfolios, and History.
def _build_real_money_guardrail_parity_rows(items: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    for item in items:
        strategy_name = str(item.get("strategy_name") or _strategy_key_to_display_name(item.get("strategy_key")) or "-")
        strategy_key = str(item.get("strategy_key") or "").strip()
        data = dict(item.get("data") or {})
        scope = _real_money_guardrail_scope_for_strategy(strategy_name, strategy_key)
        fields = _real_money_guardrail_replay_fields_for_strategy(strategy_name, strategy_key)
        rows.append(
            {
                "Strategy": strategy_name,
                "Real-Money Scope": scope["real_money_scope"],
                "Guardrail Scope": scope["guardrail_scope"],
                "Saved / Replay Values": _history_field_summary(data, fields),
                "Interpretation": scope["interpretation"],
            }
        )
    return pd.DataFrame(rows)


# Build one replay parity row for a specific History check area.
def _history_parity_row(
    record: dict[str, Any],
    *,
    area: str,
    fields: list[str],
    why: str,
    required: bool = True,
    note: str | None = None,
) -> dict[str, str]:
    pairs = _history_record_field_pairs(record, fields)
    if pairs:
        status = "저장됨"
    elif required:
        status = "누락 가능"
    else:
        status = "없음 또는 미사용"
    return {
        "확인 영역": area,
        "저장 상태": status,
        "저장된 값": _history_field_summary(record, fields),
        "왜 중요한가": note or why,
    }


# Build the full History replay parity checklist for a selected persisted run.
def _build_history_replay_parity_rows(record: dict[str, Any]) -> list[dict[str, str]]:
    record = dict(record)
    summary = record.get("summary") or {}
    gate_snapshot = record.get("gate_snapshot") or {}
    record.setdefault("actual_result_start", summary.get("start_date"))
    record.setdefault("actual_result_end", summary.get("end_date"))
    if record.get("result_rows") is None:
        record["result_rows"] = summary.get("result_rows")
    if not record.get("price_freshness") and gate_snapshot.get("price_freshness_status"):
        record["price_freshness_status"] = gate_snapshot.get("price_freshness_status")

    strategy_key = str(record.get("strategy_key") or "").strip()
    rows: list[dict[str, str]] = []

    def add(area: str, fields: list[str], why: str, *, required: bool = True, note: str | None = None) -> None:
        rows.append(
            _history_parity_row(
                record,
                area=area,
                fields=fields,
                why=why,
                required=required,
                note=note,
            )
        )

    add(
        "전략과 실행 기간",
        ["strategy_key", "input_start", "input_end", "timeframe", "option"],
        "`Load Into Form`과 `Run Again`이 어떤 전략을 어떤 기간으로 다시 열지 결정합니다.",
    )
    add(
        "Universe / Ticker",
        ["universe_mode", "preset_name", "tickers"],
        "저장 기록을 다시 열었을 때 같은 후보군으로 시작하는지 확인합니다.",
    )
    add(
        "결과 데이터 범위",
        ["actual_result_start", "actual_result_end", "result_rows"],
        "요청 기간과 실제 계산 기간이 달랐는지 history에서도 다시 확인합니다.",
        required=False,
    )
    add(
        "Data Trust",
        ["price_freshness", "price_freshness_status", "requested_tickers", "excluded_tickers", "malformed_price_rows"],
        "결과 기간이 짧아졌을 때 데이터 문제인지 전략 문제인지 다시 구분합니다.",
        required=False,
    )

    strict_keys = {
        "quality_snapshot",
        "quality_snapshot_strict_annual",
        "quality_snapshot_strict_quarterly_prototype",
        "value_snapshot_strict_annual",
        "value_snapshot_strict_quarterly_prototype",
        "quality_value_snapshot_strict_annual",
        "quality_value_snapshot_strict_quarterly_prototype",
    }
    quarterly_keys = {
        "quality_snapshot_strict_quarterly_prototype",
        "value_snapshot_strict_quarterly_prototype",
        "quality_value_snapshot_strict_quarterly_prototype",
    }
    annual_strict_keys = {
        "quality_snapshot_strict_annual",
        "value_snapshot_strict_annual",
        "quality_value_snapshot_strict_annual",
    }

    if strategy_key in strict_keys:
        add(
            "Statement cadence / factor",
            ["factor_freq", "rebalance_freq", "snapshot_mode", "quality_factors", "value_factors"],
            "annual과 quarterly prototype이 서로 다른 cadence로 저장됐는지 확인합니다.",
        )
        add(
            "Universe Contract",
            ["universe_contract", "dynamic_target_size", "snapshot_source", "research_source"],
            "static / historical dynamic universe가 load 또는 rerun에서 유지되는지 봅니다.",
            required=False,
        )
        add(
            "Overlay",
            [
                "trend_filter_enabled",
                "trend_filter_window",
                "market_regime_enabled",
                "market_regime_window",
                "market_regime_benchmark",
            ],
            "trend filter와 market regime 조건이 저장 기록에서 사라지지 않았는지 확인합니다.",
            required=False,
        )
        add(
            "Portfolio Handling",
            [
                "weighting_mode",
                "rejected_slot_handling_mode",
                "rejected_slot_fill_enabled",
                "partial_cash_retention_enabled",
                "risk_off_mode",
                "defensive_tickers",
            ],
            "weighting, rejected slot 처리, risk-off 처리 계약이 form에 복원되는지 봅니다.",
            required=False,
        )
        if strategy_key in annual_strict_keys:
            add(
                "Real-Money / Guardrail",
                [
                    "benchmark_contract",
                    "benchmark_ticker",
                    "guardrail_reference_ticker",
                    "min_price_filter",
                    "min_history_months_filter",
                    "min_avg_dollar_volume_20d_m_filter",
                    "transaction_cost_bps",
                    "underperformance_guardrail_enabled",
                    "drawdown_guardrail_enabled",
                ],
                "annual strict의 실전 검증 입력과 guardrail 설정이 재진입 과정에서 유지되는지 확인합니다.",
                required=False,
            )
            add(
                "Promotion 기준",
                [
                    "promotion_min_benchmark_coverage",
                    "promotion_min_net_cagr_spread",
                    "promotion_min_liquidity_clean_coverage",
                    "promotion_max_underperformance_share",
                    "promotion_min_worst_rolling_excess_return",
                    "promotion_max_strategy_drawdown",
                    "promotion_max_drawdown_gap_vs_benchmark",
                ],
                "승격 판단 기준을 조정한 실행인지, 기본값 실행인지 구분합니다.",
                required=False,
            )
        elif strategy_key in quarterly_keys:
            rows.append(
                {
                    "확인 영역": "Real-Money / Guardrail",
                    "저장 상태": "prototype 범위",
                    "저장된 값": "quarterly prototype은 annual strict 수준의 Real-Money / Guardrail surface가 아직 아닙니다.",
                    "왜 중요한가": "quarterly 결과를 annual strict와 같은 실전 검증 완료 상태로 오해하지 않기 위한 구분입니다.",
                }
            )

    elif strategy_key == "global_relative_strength":
        add(
            "Relative Strength score",
            ["score_lookback_months", "score_return_columns", "score_weights"],
            "GRS의 상대강도 산식과 기간이 다시 실행할 때 유지되는지 봅니다.",
            required=False,
        )
        add(
            "Cash / Trend",
            ["cash_ticker", "trend_filter_window", "top", "rebalance_interval"],
            "cash ticker, trend window, 선택 개수, 리밸런싱 cadence가 복원되는지 확인합니다.",
        )
        add(
            "ETF Real-Money 입력",
            [
                "benchmark_ticker",
                "min_price_filter",
                "transaction_cost_bps",
                "promotion_min_etf_aum_b",
                "promotion_max_bid_ask_spread_pct",
            ],
            "ETF 운용 가능성 검토에 쓰는 입력이 history에 남아 있는지 봅니다.",
            required=False,
        )

    elif strategy_key == "gtaa":
        add(
            "GTAA score / cadence",
            ["score_lookback_months", "score_return_columns", "score_weights", "top", "rebalance_interval"],
            "GTAA ranking과 리밸런싱 cadence가 저장 기록에서 유지되는지 봅니다.",
            required=False,
        )
        add(
            "Risk-Off / Defensive",
            [
                "trend_filter_window",
                "risk_off_mode",
                "defensive_tickers",
                "market_regime_enabled",
                "market_regime_window",
                "market_regime_benchmark",
                "crash_guardrail_enabled",
            ],
            "risk-off와 defensive sleeve 관련 설정이 재실행 때 유지되는지 확인합니다.",
            required=False,
        )
        add(
            "ETF Real-Money / Guardrail",
            [
                "benchmark_ticker",
                "min_price_filter",
                "transaction_cost_bps",
                "underperformance_guardrail_enabled",
                "drawdown_guardrail_enabled",
            ],
            "ETF 실전 검증 입력과 guardrail 설정이 저장됐는지 봅니다.",
            required=False,
        )

    elif strategy_key in {"risk_parity_trend", "dual_momentum"}:
        add(
            "ETF 전략 입력",
            ["top", "rebalance_interval", "vol_window"],
            "전략별 핵심 입력이 load / rerun에서 유지되는지 봅니다.",
            required=False,
        )
        add(
            "ETF Real-Money / Guardrail",
            [
                "benchmark_ticker",
                "min_price_filter",
                "transaction_cost_bps",
                "underperformance_guardrail_enabled",
                "drawdown_guardrail_enabled",
            ],
            "ETF 실전 검증 입력과 guardrail 설정이 저장됐는지 봅니다.",
            required=False,
        )

    elif strategy_key == "equal_weight":
        add(
            "Equal Weight 입력",
            ["rebalance_interval", "tickers"],
            "단순 기준선 전략을 같은 ticker와 리밸런싱 주기로 다시 열 수 있는지 봅니다.",
        )

    return rows


# Normalize Streamlit date_input variants into a start/end range.
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
