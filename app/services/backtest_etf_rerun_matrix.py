from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Mapping

from app.services.backtest_etf_evidence_expansion import ETF_EVIDENCE_EXPANSION_TARGET_KEYS
from app.services.backtest_strategy_catalog import STRATEGY_KEY_TO_DISPLAY_NAME


Runner = Callable[..., dict[str, Any]]

_COMMON_ROUTE_BOUNDARY = (
    "Backtest Analysis session-only rerun matrix; Practical Validation owns evidence results, "
    "Final Review owns selected-route decisions, and Portfolio Monitoring remains read-only."
)

_STORAGE_BOUNDARY = (
    "ETF rerun matrix results are kept in Streamlit session state only; this service does not write "
    "run history, workflow registries, saved setups, validation results, final decisions, monitoring logs, "
    "provider snapshots, or current-candidate promotion artifacts."
)

_RISK_PARITY_DEFAULT_TICKERS = ["SPY", "TLT", "GLD", "IEF", "LQD"]
_DUAL_MOMENTUM_DEFAULT_TICKERS = ["QQQ", "SPY", "IWM", "SOXX", "BIL"]

_SCENARIOS_BY_STRATEGY: dict[str, list[dict[str, Any]]] = {
    "global_relative_strength": [
        {
            "scenario_id": "grs_core_monthly_top3",
            "scenario_name": "Core monthly top 3",
            "evidence_focus": "Baseline ETF relative-strength anchor with default cash proxy and benchmark policy.",
            "params": {
                "universe_mode": "preset",
                "preset_name": "Global Relative Strength Core ETF Universe",
                "option": "month_end",
                "top": 3,
                "interval": 1,
                "benchmark_ticker": "SPY",
            },
        },
        {
            "scenario_id": "grs_concentrated_top2",
            "scenario_name": "Concentrated top 2",
            "evidence_focus": "Concentration sensitivity before current-candidate promotion.",
            "params": {
                "universe_mode": "preset",
                "preset_name": "Global Relative Strength Core ETF Universe",
                "option": "month_end",
                "top": 2,
                "interval": 1,
                "benchmark_ticker": "SPY",
            },
        },
        {
            "scenario_id": "grs_slower_signal_interval3",
            "scenario_name": "Slower signal interval 3",
            "evidence_focus": "Turnover and signal cadence sensitivity without changing strategy runtime behavior.",
            "params": {
                "universe_mode": "preset",
                "preset_name": "Global Relative Strength Core ETF Universe",
                "option": "month_end",
                "top": 3,
                "interval": 3,
                "benchmark_ticker": "SPY",
            },
        },
    ],
    "risk_parity_trend": [
        {
            "scenario_id": "rpt_core_vol6",
            "scenario_name": "Core volatility window 6",
            "evidence_focus": "Baseline defensive ETF allocation anchor.",
            "params": {
                "tickers": list(_RISK_PARITY_DEFAULT_TICKERS),
                "universe_mode": "preset",
                "preset_name": "Risk Parity Universe",
                "option": "month_end",
                "rebalance_interval": 1,
                "vol_window": 6,
                "benchmark_ticker": "SPY",
            },
        },
        {
            "scenario_id": "rpt_fast_vol3",
            "scenario_name": "Fast volatility window 3",
            "evidence_focus": "Low-volatility overweight and fast regime sensitivity.",
            "params": {
                "tickers": list(_RISK_PARITY_DEFAULT_TICKERS),
                "universe_mode": "preset",
                "preset_name": "Risk Parity Universe",
                "option": "month_end",
                "rebalance_interval": 1,
                "vol_window": 3,
                "benchmark_ticker": "SPY",
            },
        },
        {
            "scenario_id": "rpt_slow_vol12",
            "scenario_name": "Slow volatility window 12",
            "evidence_focus": "Correlation regime and slow risk-estimate sensitivity.",
            "params": {
                "tickers": list(_RISK_PARITY_DEFAULT_TICKERS),
                "universe_mode": "preset",
                "preset_name": "Risk Parity Universe",
                "option": "month_end",
                "rebalance_interval": 1,
                "vol_window": 12,
                "benchmark_ticker": "SPY",
            },
        },
    ],
    "dual_momentum": [
        {
            "scenario_id": "dm_core_top1",
            "scenario_name": "Core top 1",
            "evidence_focus": "Baseline tactical ETF momentum anchor and cash-proxy behavior.",
            "params": {
                "tickers": list(_DUAL_MOMENTUM_DEFAULT_TICKERS),
                "universe_mode": "preset",
                "preset_name": "Dual Momentum Universe",
                "option": "month_end",
                "top": 1,
                "rebalance_interval": 1,
                "benchmark_ticker": "SPY",
            },
        },
        {
            "scenario_id": "dm_diversified_top2",
            "scenario_name": "Diversified top 2",
            "evidence_focus": "Concentration and whipsaw sensitivity against the top-1 baseline.",
            "params": {
                "tickers": list(_DUAL_MOMENTUM_DEFAULT_TICKERS),
                "universe_mode": "preset",
                "preset_name": "Dual Momentum Universe",
                "option": "month_end",
                "top": 2,
                "rebalance_interval": 1,
                "benchmark_ticker": "SPY",
            },
        },
        {
            "scenario_id": "dm_slower_rebalance3",
            "scenario_name": "Slower rebalance interval 3",
            "evidence_focus": "Turnover, transaction-cost, and trend-turn sensitivity.",
            "params": {
                "tickers": list(_DUAL_MOMENTUM_DEFAULT_TICKERS),
                "universe_mode": "preset",
                "preset_name": "Dual Momentum Universe",
                "option": "month_end",
                "top": 1,
                "rebalance_interval": 3,
                "benchmark_ticker": "SPY",
            },
        },
    ],
}


def _default_runner_map() -> dict[str, Runner]:
    from app.runtime.backtest import (
        run_dual_momentum_backtest_from_db,
        run_global_relative_strength_backtest_from_db,
        run_risk_parity_trend_backtest_from_db,
    )

    return {
        "global_relative_strength": run_global_relative_strength_backtest_from_db,
        "risk_parity_trend": run_risk_parity_trend_backtest_from_db,
        "dual_momentum": run_dual_momentum_backtest_from_db,
    }


def _summary_row(bundle: Mapping[str, Any]) -> Mapping[str, Any]:
    summary = bundle.get("summary")
    if isinstance(summary, Mapping):
        return summary

    summary_df = bundle.get("summary_df")
    if summary_df is None or bool(getattr(summary_df, "empty", True)):
        return {}
    try:
        return summary_df.iloc[0].to_dict()
    except (AttributeError, IndexError, TypeError):
        return {}


def _summary_metric(row: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if row.get(key) not in (None, ""):
            return row.get(key)
    return None


def _price_freshness_status(meta: Mapping[str, Any]) -> str | None:
    freshness = meta.get("price_freshness")
    if isinstance(freshness, Mapping) and freshness.get("status") not in (None, ""):
        return str(freshness.get("status"))
    value = meta.get("price_freshness_status")
    return str(value) if value not in (None, "") else None


def _promotion_decision(meta: Mapping[str, Any]) -> str | None:
    value = meta.get("promotion_decision")
    if isinstance(value, Mapping):
        decision = value.get("decision") or value.get("status")
        return str(decision) if decision not in (None, "") else None
    return str(value) if value not in (None, "") else None


def _summarize_bundle(
    *,
    scenario: Mapping[str, Any],
    strategy_key: str,
    bundle: Mapping[str, Any],
) -> dict[str, Any]:
    meta = bundle.get("meta") if isinstance(bundle.get("meta"), Mapping) else {}
    summary = _summary_row(bundle)
    warnings = meta.get("warnings") if isinstance(meta, Mapping) else []
    warning_count = len(warnings) if isinstance(warnings, list) else 0

    return {
        "strategy_key": strategy_key,
        "display_name": STRATEGY_KEY_TO_DISPLAY_NAME[strategy_key],
        "scenario_id": scenario.get("scenario_id"),
        "scenario_name": scenario.get("scenario_name"),
        "evidence_focus": scenario.get("evidence_focus"),
        "status": "PASS",
        "actual_result_start": meta.get("actual_result_start"),
        "actual_result_end": meta.get("actual_result_end"),
        "result_rows": meta.get("result_rows"),
        "cagr": _summary_metric(summary, "cagr", "CAGR"),
        "maximum_drawdown": _summary_metric(summary, "maximum_drawdown", "mdd", "Maximum Drawdown"),
        "sharpe_ratio": _summary_metric(summary, "sharpe_ratio", "sharpe", "Sharpe Ratio"),
        "price_freshness_status": _price_freshness_status(meta),
        "promotion_decision": _promotion_decision(meta),
        "warning_count": warning_count,
        "error": "",
        "params": deepcopy(dict(scenario.get("params") or {})),
    }


def _error_row(*, scenario: Mapping[str, Any], strategy_key: str, error: Exception) -> dict[str, Any]:
    return {
        "strategy_key": strategy_key,
        "display_name": STRATEGY_KEY_TO_DISPLAY_NAME[strategy_key],
        "scenario_id": scenario.get("scenario_id"),
        "scenario_name": scenario.get("scenario_name"),
        "evidence_focus": scenario.get("evidence_focus"),
        "status": "ERROR",
        "actual_result_start": None,
        "actual_result_end": None,
        "result_rows": None,
        "cagr": None,
        "maximum_drawdown": None,
        "sharpe_ratio": None,
        "price_freshness_status": None,
        "promotion_decision": None,
        "warning_count": 0,
        "error": str(error),
        "params": deepcopy(dict(scenario.get("params") or {})),
    }


def build_etf_rerun_matrix_plan() -> dict[str, Any]:
    """Build the session-only ETF rerun matrix plan without running backtests."""

    rows: list[dict[str, Any]] = []
    scenario_count = 0
    for strategy_key in ETF_EVIDENCE_EXPANSION_TARGET_KEYS:
        scenarios = deepcopy(_SCENARIOS_BY_STRATEGY[strategy_key])
        scenario_count += len(scenarios)
        rows.append(
            {
                "strategy_key": strategy_key,
                "display_name": STRATEGY_KEY_TO_DISPLAY_NAME[strategy_key],
                "scenario_count": len(scenarios),
                "scenarios": scenarios,
                "route_boundary": _COMMON_ROUTE_BOUNDARY,
            }
        )

    return deepcopy(
        {
            "matrix_id": "etf_rerun_matrix_session_v1",
            "title": "ETF Rerun Matrix Workbench",
            "status": "Session-only ETF rerun matrix plan",
            "summary": (
                "Defines DB-backed rerun scenarios for GRS / Risk Parity / Dual Momentum so current-anchor "
                "evidence can be reviewed before any promotion workflow writes."
            ),
            "target_strategy_keys": list(ETF_EVIDENCE_EXPANSION_TARGET_KEYS),
            "rows": rows,
            "strategy_count": len(rows),
            "scenario_count": scenario_count,
            "runs_backtests_on_render": False,
            "writes_run_history": False,
            "writes_validation_results": False,
            "creates_current_candidate": False,
            "storage_boundary": _STORAGE_BOUNDARY,
            "route_boundary": _COMMON_ROUTE_BOUNDARY,
        }
    )


def run_etf_rerun_matrix(
    strategy_key: str,
    *,
    runner_map: Mapping[str, Runner] | None = None,
) -> dict[str, Any]:
    """Run the selected ETF strategy matrix and return compact session-only evidence rows."""

    normalized_key = str(strategy_key or "").strip().lower()
    if normalized_key not in _SCENARIOS_BY_STRATEGY:
        raise ValueError(f"Unsupported ETF rerun matrix strategy: {strategy_key}")

    runners = dict(runner_map) if runner_map is not None else _default_runner_map()
    runner = runners.get(normalized_key)
    if runner is None:
        raise ValueError(f"Missing ETF rerun matrix runner for strategy: {normalized_key}")

    rows: list[dict[str, Any]] = []
    for scenario in _SCENARIOS_BY_STRATEGY[normalized_key]:
        try:
            bundle = runner(**deepcopy(dict(scenario.get("params") or {})))
            rows.append(
                _summarize_bundle(
                    scenario=scenario,
                    strategy_key=normalized_key,
                    bundle=bundle,
                )
            )
        except Exception as exc:  # UI should show partial matrix evidence instead of losing all rows.
            rows.append(_error_row(scenario=scenario, strategy_key=normalized_key, error=exc))

    error_count = sum(1 for row in rows if row["status"] == "ERROR")
    pass_count = sum(1 for row in rows if row["status"] == "PASS")
    status = "COMPLETED" if error_count == 0 else "COMPLETED_WITH_ERRORS"

    return deepcopy(
        {
            "matrix_id": "etf_rerun_matrix_session_v1",
            "strategy_key": normalized_key,
            "display_name": STRATEGY_KEY_TO_DISPLAY_NAME[normalized_key],
            "status": status,
            "rows": rows,
            "scenario_count": len(rows),
            "pass_count": pass_count,
            "error_count": error_count,
            "runs_backtests": True,
            "writes_run_history": False,
            "writes_validation_results": False,
            "creates_current_candidate": False,
            "storage_boundary": _STORAGE_BOUNDARY,
            "route_boundary": _COMMON_ROUTE_BOUNDARY,
        }
    )


__all__ = [
    "build_etf_rerun_matrix_plan",
    "run_etf_rerun_matrix",
]
