from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKTEST_HISTORY_FILE = PROJECT_ROOT / ".note" / "finance" / "BACKTEST_RUN_HISTORY.jsonl"
BACKTEST_ARTIFACT_DIR = PROJECT_ROOT / ".note" / "finance" / "backtest_artifacts"
BACKTEST_HISTORY_SCHEMA_VERSION = 2
_SAFE_CHARS = re.compile(r"[^A-Za-z0-9_.-]+")


def _safe_token(value: str | None, *, fallback: str) -> str:
    token = _SAFE_CHARS.sub("_", (value or "").strip())
    token = token.strip("._")
    return token or fallback


def _write_dynamic_universe_artifact(
    *,
    bundle: dict[str, Any],
    run_kind: str,
    recorded_at: str,
) -> dict[str, Any] | None:
    snapshot_rows = bundle.get("dynamic_universe_snapshot_rows") or []
    candidate_status_rows = bundle.get("dynamic_candidate_status_rows") or []
    meta = dict(bundle.get("meta") or {})
    universe_debug = meta.get("universe_debug") or {}
    if not snapshot_rows and not universe_debug:
        return None

    BACKTEST_ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    base_name = (
        f"{_safe_token(recorded_at.replace(':', '-'), fallback='record')}_"
        f"{_safe_token(str(meta.get('strategy_key')), fallback='strategy')}_dynamic_universe"
    )
    artifact_dir = BACKTEST_ARTIFACT_DIR / base_name
    counter = 2
    while artifact_dir.exists():
        artifact_dir = BACKTEST_ARTIFACT_DIR / f"{base_name}_{counter}"
        counter += 1
    artifact_dir.mkdir(parents=True, exist_ok=False)

    payload = {
        "recorded_at": recorded_at,
        "run_kind": run_kind,
        "strategy_key": meta.get("strategy_key"),
        "strategy_name": bundle.get("strategy_name"),
        "universe_contract": meta.get("universe_contract"),
        "dynamic_target_size": meta.get("dynamic_target_size"),
        "dynamic_candidate_count": meta.get("dynamic_candidate_count"),
        "universe_debug": universe_debug,
        "snapshot_rows": snapshot_rows,
        "candidate_status_rows": candidate_status_rows,
    }
    artifact_path = artifact_dir / "dynamic_universe_snapshot.json"
    artifact_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    return {
        "artifact_dir": str(artifact_dir),
        "snapshot_json": str(artifact_path),
        "snapshot_row_count": len(snapshot_rows),
        "candidate_status_row_count": len(candidate_status_rows),
    }


def _extract_primary_summary(bundle: dict[str, Any]) -> dict[str, Any]:
    summary_df = bundle.get("summary_df")
    if summary_df is None or summary_df.empty:
        return {}

    row = summary_df.iloc[0]
    return {
        "strategy_name": row.get("Name"),
        "start_date": str(row.get("Start Date")),
        "end_date": str(row.get("End Date")),
        "start_balance": float(row.get("Start Balance")),
        "end_balance": float(row.get("End Balance")),
        "cagr": float(row.get("CAGR")),
        "standard_deviation": float(row.get("Standard Deviation")),
        "sharpe_ratio": float(row.get("Sharpe Ratio")),
        "maximum_drawdown": float(row.get("Maximum Drawdown")),
    }


def append_backtest_run_history(
    *,
    bundle: dict[str, Any],
    run_kind: str,
    context: dict[str, Any] | None = None,
) -> None:
    meta = dict(bundle.get("meta") or {})
    recorded_at = datetime.now().isoformat(timespec="seconds")
    merged_context = dict(context or {})
    dynamic_artifact = _write_dynamic_universe_artifact(
        bundle=bundle,
        run_kind=run_kind,
        recorded_at=recorded_at,
    )
    if dynamic_artifact is not None:
        merged_context.setdefault("dynamic_universe_artifact", dynamic_artifact)
        merged_context.setdefault(
            "dynamic_universe_preview_rows",
            list((meta.get("universe_debug") or {}).get("per_date_rows") or [])[:24],
        )

    gate_snapshot = {
        "promotion_decision": meta.get("promotion_decision"),
        "promotion_next_step": meta.get("promotion_next_step"),
        "promotion_rationale": meta.get("promotion_rationale"),
        "shortlist_status": meta.get("shortlist_status"),
        "shortlist_next_step": meta.get("shortlist_next_step"),
        "shortlist_rationale": meta.get("shortlist_rationale"),
        "probation_status": meta.get("probation_status"),
        "probation_stage": meta.get("probation_stage"),
        "probation_next_step": meta.get("probation_next_step"),
        "monitoring_status": meta.get("monitoring_status"),
        "monitoring_next_step": meta.get("monitoring_next_step"),
        "deployment_readiness_status": meta.get("deployment_readiness_status"),
        "deployment_readiness_next_step": meta.get("deployment_readiness_next_step"),
        "deployment_readiness_rationale": meta.get("deployment_readiness_rationale"),
        "deployment_check_pass_count": meta.get("deployment_check_pass_count"),
        "deployment_check_watch_count": meta.get("deployment_check_watch_count"),
        "deployment_check_fail_count": meta.get("deployment_check_fail_count"),
        "deployment_check_unavailable_count": meta.get("deployment_check_unavailable_count"),
        "validation_status": meta.get("validation_status"),
        "benchmark_policy_status": meta.get("benchmark_policy_status"),
        "liquidity_policy_status": meta.get("liquidity_policy_status"),
        "validation_policy_status": meta.get("validation_policy_status"),
        "guardrail_policy_status": meta.get("guardrail_policy_status"),
        "etf_operability_status": meta.get("etf_operability_status"),
        "rolling_review_status": meta.get("rolling_review_status"),
        "out_of_sample_review_status": meta.get("out_of_sample_review_status"),
        "price_freshness_status": (meta.get("price_freshness") or {}).get("status"),
    }

    record = {
        "schema_version": BACKTEST_HISTORY_SCHEMA_VERSION,
        "recorded_at": recorded_at,
        "run_kind": run_kind,
        "strategy_key": meta.get("strategy_key"),
        "execution_mode": meta.get("execution_mode"),
        "data_mode": meta.get("data_mode"),
        "tickers": meta.get("tickers", []),
        "input_start": meta.get("start"),
        "input_end": meta.get("end"),
        "timeframe": meta.get("timeframe"),
        "option": meta.get("option"),
        "rebalance_interval": meta.get("rebalance_interval"),
        "top": meta.get("top"),
        "vol_window": meta.get("vol_window"),
        "factor_freq": meta.get("factor_freq"),
        "rebalance_freq": meta.get("rebalance_freq"),
        "snapshot_mode": meta.get("snapshot_mode"),
        "quality_factors": meta.get("quality_factors"),
        "value_factors": meta.get("value_factors"),
        "trend_filter_enabled": meta.get("trend_filter_enabled"),
        "trend_filter_window": meta.get("trend_filter_window"),
        "weighting_mode": meta.get("weighting_mode"),
        "rejected_slot_handling_mode": meta.get("rejected_slot_handling_mode"),
        "rejected_slot_fill_enabled": meta.get("rejected_slot_fill_enabled"),
        "partial_cash_retention_enabled": meta.get("partial_cash_retention_enabled"),
        "market_regime_enabled": meta.get("market_regime_enabled"),
        "market_regime_window": meta.get("market_regime_window"),
        "market_regime_benchmark": meta.get("market_regime_benchmark"),
        "score_lookback_months": meta.get("score_lookback_months"),
        "score_return_columns": meta.get("score_return_columns"),
        "score_weights": meta.get("score_weights"),
        "risk_off_mode": meta.get("risk_off_mode"),
        "defensive_tickers": meta.get("defensive_tickers"),
        "crash_guardrail_enabled": meta.get("crash_guardrail_enabled"),
        "crash_guardrail_drawdown_threshold": meta.get("crash_guardrail_drawdown_threshold"),
        "crash_guardrail_lookback_months": meta.get("crash_guardrail_lookback_months"),
        "underperformance_guardrail_enabled": meta.get("underperformance_guardrail_enabled"),
        "underperformance_guardrail_window_months": meta.get("underperformance_guardrail_window_months"),
        "underperformance_guardrail_threshold": meta.get("underperformance_guardrail_threshold"),
        "drawdown_guardrail_enabled": meta.get("drawdown_guardrail_enabled"),
        "drawdown_guardrail_window_months": meta.get("drawdown_guardrail_window_months"),
        "drawdown_guardrail_strategy_threshold": meta.get("drawdown_guardrail_strategy_threshold"),
        "drawdown_guardrail_gap_threshold": meta.get("drawdown_guardrail_gap_threshold"),
        "min_price_filter": meta.get("min_price_filter"),
        "min_history_months_filter": meta.get("min_history_months_filter"),
        "min_avg_dollar_volume_20d_m_filter": meta.get("min_avg_dollar_volume_20d_m_filter"),
        "transaction_cost_bps": meta.get("transaction_cost_bps"),
        "promotion_min_etf_aum_b": meta.get("promotion_min_etf_aum_b"),
        "promotion_max_bid_ask_spread_pct": meta.get("promotion_max_bid_ask_spread_pct"),
        "benchmark_contract": meta.get("benchmark_contract"),
        "benchmark_ticker": meta.get("benchmark_ticker"),
        "promotion_min_benchmark_coverage": meta.get("promotion_min_benchmark_coverage"),
        "promotion_min_net_cagr_spread": meta.get("promotion_min_net_cagr_spread"),
        "promotion_min_liquidity_clean_coverage": meta.get("promotion_min_liquidity_clean_coverage"),
        "promotion_max_underperformance_share": meta.get("promotion_max_underperformance_share"),
        "promotion_min_worst_rolling_excess_return": meta.get("promotion_min_worst_rolling_excess_return"),
        "promotion_max_strategy_drawdown": meta.get("promotion_max_strategy_drawdown"),
        "promotion_max_drawdown_gap_vs_benchmark": meta.get("promotion_max_drawdown_gap_vs_benchmark"),
        "snapshot_source": meta.get("snapshot_source"),
        "universe_contract": meta.get("universe_contract"),
        "dynamic_target_size": meta.get("dynamic_target_size"),
        "ui_elapsed_seconds": meta.get("ui_elapsed_seconds"),
        "universe_mode": meta.get("universe_mode"),
        "preset_name": meta.get("preset_name"),
        "promotion_decision": meta.get("promotion_decision"),
        "shortlist_status": meta.get("shortlist_status"),
        "probation_status": meta.get("probation_status"),
        "monitoring_status": meta.get("monitoring_status"),
        "deployment_readiness_status": meta.get("deployment_readiness_status"),
        "warnings": meta.get("warnings", []),
        "gate_snapshot": gate_snapshot,
        "summary": _extract_primary_summary(bundle),
        "context": merged_context,
    }

    BACKTEST_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with BACKTEST_HISTORY_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_backtest_run_history(limit: int = 30) -> list[dict[str, Any]]:
    if not BACKTEST_HISTORY_FILE.exists():
        return []

    rows: list[dict[str, Any]] = []
    for line in BACKTEST_HISTORY_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    return rows[-limit:][::-1]
