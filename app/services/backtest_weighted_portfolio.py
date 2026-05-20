from __future__ import annotations

from typing import Any

from app.services.backtest_result_read_model import (
    build_monthly_component_balance_views,
    build_strategy_data_trust_rows,
)
from app.runtime.backtest import build_backtest_result_bundle
from finance.performance import make_monthly_weighted_portfolio


def build_weighted_portfolio_bundle(
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
    contribution_amount_df, contribution_share_df = build_monthly_component_balance_views(
        bundles,
        strategy_names=strategy_names,
        weights=normalized_weights,
        date_policy=date_policy,
    )
    component_data_trust_rows = build_strategy_data_trust_rows(bundles)
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


__all__ = ["build_weighted_portfolio_bundle"]
