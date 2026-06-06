from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import numpy as np
import pandas as pd

from .swing import RiskOnMomentumConfig, SwingBacktestResult, clone_config, run_risk_on_momentum_backtest


def _metric_row(
    label: str,
    result: SwingBacktestResult,
    config: RiskOnMomentumConfig,
    *,
    suite: str,
    variable: str,
    value: str,
) -> dict[str, Any]:
    metrics = dict(result.metrics or {})
    return {
        "suite": suite,
        "variable": variable,
        "value": value,
        "label": label,
        "exit_mode": config.exit_mode,
        "macro_filter_mode": config.macro_filter_mode,
        "max_holding_days": int(config.max_holding_days),
        "stop_loss_pct": float(config.stop_loss_pct),
        "take_profit_pct": float(config.take_profit_pct),
        "atr_period": int(config.atr_period),
        "stop_atr_multiple": float(config.stop_atr_multiple),
        "take_profit_atr_multiple": float(config.take_profit_atr_multiple),
        "transaction_cost_bps": float(config.transaction_cost_bps),
        "slippage_bps": float(config.slippage_bps),
        "total_trades": metrics.get("total_trades"),
        "win_rate": metrics.get("win_rate"),
        "avg_return": metrics.get("avg_return"),
        "expectancy": metrics.get("expectancy"),
        "cumulative_return": metrics.get("cumulative_return"),
        "cagr": metrics.get("cagr"),
        "mdd": metrics.get("mdd"),
        "sharpe_ratio": metrics.get("sharpe_ratio"),
        "avg_holding_days": metrics.get("avg_holding_days"),
        "max_consecutive_losses": metrics.get("max_consecutive_losses"),
        "total_fees": metrics.get("total_fees"),
    }


def _curve_frame(results: Iterable[tuple[str, SwingBacktestResult]]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for label, result in results:
        if result.result_df.empty:
            continue
        frame = result.result_df[["Date", "Total Balance"]].copy()
        frame["Date"] = pd.to_datetime(frame["Date"], errors="coerce")
        frame["label"] = label
        frame["total_balance"] = pd.to_numeric(frame["Total Balance"], errors="coerce")
        start_balance = frame["total_balance"].dropna().iloc[0] if not frame["total_balance"].dropna().empty else np.nan
        frame["cumulative_return"] = frame["total_balance"] / start_balance - 1.0 if start_balance else np.nan
        frames.append(frame[["Date", "label", "total_balance", "cumulative_return"]])
    if not frames:
        return pd.DataFrame(columns=["Date", "label", "total_balance", "cumulative_return"])
    return pd.concat(frames, ignore_index=True).sort_values(["label", "Date"]).reset_index(drop=True)


def _run_variant(
    price_history: pd.DataFrame,
    *,
    config: RiskOnMomentumConfig,
    macro_scores: pd.DataFrame | None,
    statement_history: pd.DataFrame | None,
    prepared_features: pd.DataFrame | None,
) -> SwingBacktestResult:
    return run_risk_on_momentum_backtest(
        price_history,
        config=clone_config(config, collect_scanner_rows=False),
        macro_scores=macro_scores,
        statement_history=statement_history,
        prepared_features=prepared_features,
    )


def build_swing_comparison_suite(
    price_history: pd.DataFrame,
    *,
    config: RiskOnMomentumConfig,
    primary_result: SwingBacktestResult,
    macro_scores: pd.DataFrame | None,
    statement_history: pd.DataFrame | None,
    prepared_features: pd.DataFrame | None,
) -> dict[str, pd.DataFrame]:
    rows: list[dict[str, Any]] = []
    curves: dict[str, pd.DataFrame] = {}

    exit_variants = [
        ("fixed_pct -2.5/+5.0", clone_config(config, exit_mode="fixed_pct", stop_loss_pct=-2.5, take_profit_pct=5.0)),
        (
            "atr_based 1.0/2.0 ATR14",
            clone_config(config, exit_mode="atr_based", atr_period=14, stop_atr_multiple=1.0, take_profit_atr_multiple=2.0),
        ),
    ]
    exit_results: list[tuple[str, SwingBacktestResult]] = []
    for label, variant_config in exit_variants:
        result = primary_result if variant_config == config else _run_variant(
            price_history,
            config=variant_config,
            macro_scores=macro_scores,
            statement_history=statement_history,
            prepared_features=prepared_features,
        )
        exit_results.append((label, result))
        rows.append(_metric_row(label, result, variant_config, suite="comparison", variable="exit_mode", value=variant_config.exit_mode))
    curves["exit_curve_df"] = _curve_frame(exit_results)

    macro_variants = [
        ("macro hard_filter", clone_config(config, macro_filter_enabled=True, macro_filter_mode="hard_filter")),
        ("macro ranking_penalty", clone_config(config, macro_filter_enabled=True, macro_filter_mode="ranking_penalty")),
        ("macro off", clone_config(config, macro_filter_enabled=False, macro_filter_mode="off")),
    ]
    macro_results: list[tuple[str, SwingBacktestResult]] = []
    for label, variant_config in macro_variants:
        result = primary_result if variant_config == config else _run_variant(
            price_history,
            config=variant_config,
            macro_scores=macro_scores,
            statement_history=statement_history,
            prepared_features=prepared_features,
        )
        macro_results.append((label, result))
        rows.append(_metric_row(label, result, variant_config, suite="comparison", variable="macro_filter_mode", value=variant_config.macro_filter_mode))
    curves["macro_curve_df"] = _curve_frame(macro_results)

    holding_variants = [
        (f"{days}D max hold", clone_config(config, max_holding_days=days))
        for days in [3, 5, 10]
    ]
    holding_results: list[tuple[str, SwingBacktestResult]] = []
    for label, variant_config in holding_variants:
        result = primary_result if variant_config == config else _run_variant(
            price_history,
            config=variant_config,
            macro_scores=macro_scores,
            statement_history=statement_history,
            prepared_features=prepared_features,
        )
        holding_results.append((label, result))
        rows.append(_metric_row(label, result, variant_config, suite="comparison", variable="max_holding_days", value=str(variant_config.max_holding_days)))
    curves["holding_curve_df"] = _curve_frame(holding_results)

    return {
        "comparison_df": pd.DataFrame(rows),
        **curves,
    }


def build_swing_sensitivity_suite(
    price_history: pd.DataFrame,
    *,
    config: RiskOnMomentumConfig,
    macro_scores: pd.DataFrame | None,
    statement_history: pd.DataFrame | None,
    prepared_features: pd.DataFrame | None,
) -> pd.DataFrame:
    variants: list[tuple[str, str, str, RiskOnMomentumConfig]] = []
    for stop_loss, take_profit in [(-2.0, 4.0), (-2.5, 5.0), (-3.0, 6.0)]:
        variants.append(
            (
                "fixed_pct",
                "stop/take",
                f"{stop_loss:.1f}/{take_profit:.1f}",
                clone_config(config, exit_mode="fixed_pct", stop_loss_pct=stop_loss, take_profit_pct=take_profit),
            )
        )
    for stop_atr, take_atr in [(1.0, 2.0), (1.5, 3.0)]:
        variants.append(
            (
                "atr_based",
                "atr_multiples",
                f"{stop_atr:.1f}/{take_atr:.1f}",
                clone_config(config, exit_mode="atr_based", atr_period=14, stop_atr_multiple=stop_atr, take_profit_atr_multiple=take_atr),
            )
        )
    base_cost = float(config.transaction_cost_bps)
    base_slippage = float(config.slippage_bps)
    for cost_bps, slippage_bps in [(base_cost, base_slippage), (5.0, 5.0), (10.0, 10.0)]:
        variants.append(
            (
                "cost_slippage",
                "cost/slippage bps",
                f"{cost_bps:.0f}/{slippage_bps:.0f}",
                clone_config(config, transaction_cost_bps=cost_bps, slippage_bps=slippage_bps),
            )
        )
    threshold_variants = [
        ("base", 0.0, 1.0, 1.0, 1.0),
        ("stricter", 0.2, 0.8, 0.8, 0.8),
        ("looser", -0.2, 1.2, 1.2, 1.2),
    ]
    for label, risk_on_min, rate_max, dollar_max, safe_max in threshold_variants:
        variants.append(
            (
                "macro_threshold",
                "macro thresholds",
                label,
                clone_config(
                    config,
                    risk_on_min=risk_on_min,
                    rate_pressure_max=rate_max,
                    dollar_pressure_max=dollar_max,
                    safe_haven_max=safe_max,
                ),
            )
        )

    rows: list[dict[str, Any]] = []
    for suite_label, variable, value, variant_config in variants:
        result = _run_variant(
            price_history,
            config=variant_config,
            macro_scores=macro_scores,
            statement_history=statement_history,
            prepared_features=prepared_features,
        )
        rows.append(_metric_row(suite_label, result, variant_config, suite="sensitivity", variable=variable, value=value))
    return pd.DataFrame(rows)


def build_swing_stability_tables(result: SwingBacktestResult) -> dict[str, pd.DataFrame]:
    trades = result.trade_log_df.copy()
    closed = trades[trades.get("exit_reason", pd.Series(dtype=str)) != "END_OF_BACKTEST"].copy() if not trades.empty else trades
    if not closed.empty:
        closed["exit_date"] = pd.to_datetime(closed["exit_date"], errors="coerce")
        closed["year"] = closed["exit_date"].dt.strftime("%Y")
        closed["month"] = closed["exit_date"].dt.strftime("%Y-%m")
        closed["net_return_pct"] = pd.to_numeric(closed["net_return_pct"], errors="coerce")
        closed["net_pnl"] = pd.to_numeric(closed["net_pnl"], errors="coerce")

    yearly = result.yearly_returns_df.copy()
    if not yearly.empty and not closed.empty:
        trade_year = closed.groupby("year", as_index=False).agg(
            trade_count=("symbol", "size"),
            win_rate=("net_return_pct", lambda s: float((s > 0).mean()) if len(s) else np.nan),
            net_pnl=("net_pnl", "sum"),
        )
        yearly = yearly.merge(trade_year, on="year", how="left")

    monthly = result.monthly_returns_df.copy()
    if not monthly.empty and not closed.empty:
        trade_month = closed.groupby("month", as_index=False).agg(
            trade_count=("symbol", "size"),
            win_rate=("net_return_pct", lambda s: float((s > 0).mean()) if len(s) else np.nan),
            net_pnl=("net_pnl", "sum"),
        )
        monthly = monthly.merge(trade_month, on="month", how="left")

    contribution = result.ticker_contribution_df.copy()
    if not contribution.empty:
        total_positive = pd.to_numeric(contribution["net_pnl"], errors="coerce").clip(lower=0).sum()
        contribution["positive_pnl_share"] = (
            pd.to_numeric(contribution["net_pnl"], errors="coerce").clip(lower=0) / total_positive
            if total_positive
            else np.nan
        )
    return {
        "yearly_stability_df": yearly,
        "monthly_stability_df": monthly,
        "ticker_dependency_df": contribution,
    }


def build_trade_cause_summary(trades: pd.DataFrame) -> pd.DataFrame:
    if trades is None or trades.empty:
        return pd.DataFrame(columns=["exit_reason_code", "trades", "win_rate", "avg_return", "net_pnl", "avg_holding_days"])
    closed = trades[trades.get("exit_reason", pd.Series(dtype=str)) != "END_OF_BACKTEST"].copy()
    if closed.empty:
        return pd.DataFrame(columns=["exit_reason_code", "trades", "win_rate", "avg_return", "net_pnl", "avg_holding_days"])
    closed["exit_reason_code"] = closed.get("exit_reason_code", closed["exit_reason"]).astype(str).str.lower()
    closed["net_return_pct"] = pd.to_numeric(closed["net_return_pct"], errors="coerce")
    closed["net_pnl"] = pd.to_numeric(closed["net_pnl"], errors="coerce")
    closed["holding_days"] = pd.to_numeric(closed["holding_days"], errors="coerce")
    return closed.groupby("exit_reason_code", as_index=False).agg(
        trades=("symbol", "size"),
        win_rate=("net_return_pct", lambda s: float((s > 0).mean()) if len(s) else np.nan),
        avg_return=("net_return_pct", "mean"),
        net_pnl=("net_pnl", "sum"),
        avg_holding_days=("holding_days", "mean"),
    )


def build_quality_warnings(
    *,
    result: SwingBacktestResult,
    random_summary_df: pd.DataFrame | None,
    benchmark_comparison_df: pd.DataFrame | None,
    sensitivity_df: pd.DataFrame | None,
    price_freshness: dict[str, Any] | None,
    macro_scores: pd.DataFrame | None,
    macro_filter_enabled: bool,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    def add(status: str, warning: str, evidence: str, action: str) -> None:
        rows.append({"status": status, "warning": warning, "evidence": evidence, "research_action": action})

    metrics = dict(result.metrics or {})
    total_trades = int(metrics.get("total_trades") or 0)
    if total_trades < 30:
        add("REVIEW", "Low trade count", f"Closed trades={total_trades}", "Do not overstate statistical reliability.")

    contribution = result.ticker_contribution_df.copy()
    if not contribution.empty:
        pnl = pd.to_numeric(contribution["net_pnl"], errors="coerce")
        positive_total = pnl.clip(lower=0).sum()
        top3_share = pnl.clip(lower=0).nlargest(3).sum() / positive_total if positive_total else 0.0
        if top3_share >= 0.50:
            add("REVIEW", "Ticker dependency", f"Top 3 positive P&L share={top3_share:.1%}", "Inspect ticker-level contribution before promotion.")

    yearly = result.yearly_returns_df.copy()
    if not yearly.empty and "return" in yearly.columns:
        returns = pd.to_numeric(yearly["return"], errors="coerce").dropna()
        positive_total = returns.clip(lower=0).sum()
        best_share = returns.clip(lower=0).max() / positive_total if positive_total else 0.0
        if best_share >= 0.60 and len(returns) > 1:
            add("REVIEW", "Year dependency", f"Best positive year share={best_share:.1%}", "Check whether one year explains most of the return.")

    if random_summary_df is not None and not random_summary_df.empty and "cagr" in random_summary_df.columns:
        random_median = float(pd.to_numeric(random_summary_df["cagr"], errors="coerce").median())
        primary_cagr = float(metrics.get("cagr") or 0.0)
        if primary_cagr - random_median < 0.02:
            add("REVIEW", "Weak random-ranking edge", f"Strategy CAGR - random median CAGR={primary_cagr - random_median:.1%}", "Compare signal edge against random ranking.")

    if benchmark_comparison_df is not None and not benchmark_comparison_df.empty:
        bench = benchmark_comparison_df[benchmark_comparison_df["label"].astype(str).str.contains("SPY|QQQ", regex=True, na=False)]
        if not bench.empty and "cagr" in bench.columns:
            best_bench_cagr = float(pd.to_numeric(bench["cagr"], errors="coerce").max())
            primary_cagr = float(metrics.get("cagr") or 0.0)
            if primary_cagr < best_bench_cagr:
                add("REVIEW", "Benchmark comparison weakness", f"Best SPY/QQQ CAGR={best_bench_cagr:.1%}; strategy CAGR={primary_cagr:.1%}", "Review benchmark-relative stability.")

    if sensitivity_df is not None and not sensitivity_df.empty:
        cost_rows = sensitivity_df[sensitivity_df["variable"] == "cost/slippage bps"].copy()
        base = cost_rows[cost_rows["value"].astype(str) == "0/0"]
        high_cost = cost_rows[cost_rows["value"].astype(str) == "10/10"]
        if not base.empty and not high_cost.empty:
            base_return = float(pd.to_numeric(base["cumulative_return"], errors="coerce").iloc[0])
            high_cost_return = float(pd.to_numeric(high_cost["cumulative_return"], errors="coerce").iloc[0])
            if base_return > 0 and high_cost_return < base_return * 0.5:
                add("REVIEW", "Cost/slippage sensitivity", f"Base return={base_return:.1%}; 10/10 bps return={high_cost_return:.1%}", "Treat cost assumptions as a primary research risk.")

    freshness_status = str((price_freshness or {}).get("status") or "").lower()
    if freshness_status in {"warning", "error"}:
        add("REVIEW", "Price freshness issue", f"Freshness status={freshness_status}", "Refresh or inspect DB price coverage before relying on the run.")

    if macro_filter_enabled and (macro_scores is None or macro_scores.empty):
        add("NEEDS_INPUT", "Missing macro rows", "Macro filter enabled but no futures Mean-Z rows were available.", "Refresh futures macro data or run macro off for comparison.")

    if not rows:
        add("PASS", "No major research quality warnings", "Configured checks did not flag the primary run.", "Still treat this as historical research evidence.")
    return pd.DataFrame(rows)
