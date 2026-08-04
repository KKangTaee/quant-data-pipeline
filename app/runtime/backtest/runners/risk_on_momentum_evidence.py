from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from finance.swing import RISK_ON_MOMENTUM_STRATEGY_KEY, RiskOnMomentumConfig


DAILY_SWING_EVIDENCE_SCHEMA_VERSION = "daily_swing_evidence_v1"


def _number(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return None if pd.isna(parsed) else parsed


def _annualized_turnover(
    result_df: pd.DataFrame,
    trade_log_df: pd.DataFrame,
) -> float | None:
    if result_df is None or result_df.empty or trade_log_df is None or trade_log_df.empty:
        return None
    balances = pd.to_numeric(result_df.get("Total Balance"), errors="coerce").dropna()
    dates = pd.to_datetime(result_df.get("Date"), errors="coerce").dropna()
    if balances.empty or len(dates) < 2:
        return None
    average_assets = float(balances.mean())
    years = max((dates.max() - dates.min()).days / 365.25, 1.0 / 365.25)
    entries = pd.to_numeric(trade_log_df.get("entry_notional"), errors="coerce").fillna(0.0)
    proceeds = pd.to_numeric(trade_log_df.get("gross_proceeds"), errors="coerce").fillna(0.0)
    if average_assets <= 0:
        return None
    return float(((entries.sum() + proceeds.sum()) / 2.0) / average_assets / years)


def _best_benchmark(benchmark_comparison_df: pd.DataFrame) -> dict[str, Any]:
    if benchmark_comparison_df is None or benchmark_comparison_df.empty:
        return {"label": None, "cagr": None}
    rows = benchmark_comparison_df.copy()
    rows["cagr"] = pd.to_numeric(rows.get("cagr"), errors="coerce")
    rows = rows[rows["label"].astype(str).str.contains("Buy & Hold", na=False)].dropna(
        subset=["cagr"]
    )
    if rows.empty:
        return {"label": None, "cagr": None}
    best = rows.sort_values("cagr", ascending=False).iloc[0]
    return {"label": str(best.get("label") or ""), "cagr": float(best["cagr"])}


def build_daily_swing_evidence_packet(
    *,
    config: RiskOnMomentumConfig,
    meta: dict[str, Any],
    metrics: dict[str, Any],
    result_df: pd.DataFrame,
    trade_log_df: pd.DataFrame,
    random_summary_df: pd.DataFrame,
    benchmark_comparison_df: pd.DataFrame,
    quality_warning_df: pd.DataFrame,
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Build JSON-safe Level2 evidence without copying raw trade or scanner rows."""

    meta_row = dict(meta or {})
    metrics_row = dict(metrics or {})
    universe_source = str(meta_row.get("universe_source") or "")
    pit_membership_verified = bool(meta_row.get("pit_membership_verified")) or (
        "pit" in universe_source.lower()
    )
    delisting_coverage_verified = bool(meta_row.get("delisting_coverage_verified"))
    blockers: list[str] = []
    if not pit_membership_verified:
        blockers.append("Historical PIT universe membership is not verified.")
    if not delisting_coverage_verified:
        blockers.append("Delisted/security lifecycle coverage is not verified.")

    random_median_cagr = None
    if random_summary_df is not None and not random_summary_df.empty:
        values = pd.to_numeric(random_summary_df.get("cagr"), errors="coerce").dropna()
        if not values.empty:
            random_median_cagr = float(values.median())
    quality_rows = []
    if quality_warning_df is not None and not quality_warning_df.empty:
        for row in quality_warning_df.to_dict(orient="records"):
            quality_rows.append(
                {
                    "status": str(row.get("status") or "REVIEW"),
                    "warning": str(row.get("warning") or ""),
                    "evidence": str(row.get("evidence") or ""),
                }
            )
    artifact_path = str(dict(artifact or {}).get("run_json") or "")
    return {
        "schema_version": DAILY_SWING_EVIDENCE_SCHEMA_VERSION,
        "strategy_key": RISK_ON_MOMENTUM_STRATEGY_KEY,
        "status": "REVIEW" if blockers else "PASS",
        "period": {"start": config.start, "end": config.end, "frequency": "1d"},
        "universe": {
            "mode": meta_row.get("universe_mode"),
            "source": universe_source or None,
            "symbol_count": int(meta_row.get("universe_symbol_count") or 0),
            "pit_membership_verified": pit_membership_verified,
            "delisting_coverage_verified": delisting_coverage_verified,
        },
        "execution": {
            "mode": config.execution_mode,
            "exit_mode": config.exit_mode,
            "max_holding_days": int(config.max_holding_days),
            "average_holding_days": _number(metrics_row.get("avg_holding_days")),
            "transaction_cost_bps": float(config.transaction_cost_bps),
            "slippage_bps": float(config.slippage_bps),
            "total_fees": _number(metrics_row.get("total_fees")),
            "annualized_turnover": _annualized_turnover(result_df, trade_log_df),
            "macro_filter_mode": config.macro_filter_mode,
        },
        "performance": {
            "trade_count": int(metrics_row.get("total_trades") or 0),
            "cagr": _number(metrics_row.get("cagr")),
            "mdd": _number(metrics_row.get("mdd")),
        },
        "robustness": {
            "analysis_intensity": meta_row.get("analysis_intensity"),
            "simulation_executed_count": int(
                meta_row.get("simulation_executed_count") or 0
            ),
            "random_median_cagr": random_median_cagr,
            "best_benchmark": _best_benchmark(benchmark_comparison_df),
            "quality_warnings": quality_rows,
        },
        "artifact": {
            "artifact_name": Path(artifact_path).name if artifact_path else None,
            "trade_row_count": int(dict(artifact or {}).get("trade_row_count") or 0),
            "scanner_row_count": int(dict(artifact or {}).get("scanner_row_count") or 0),
            "raw_rows_embedded": False,
        },
        "review_blockers": blockers,
        "boundaries": {
            "compact_evidence_only": True,
            "registry_write": False,
            "live_approval": False,
            "auto_order": False,
            "auto_rebalance": False,
        },
    }


__all__ = [
    "DAILY_SWING_EVIDENCE_SCHEMA_VERSION",
    "build_daily_swing_evidence_packet",
]
