from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import pandas as pd

from app.services.backtest_result_read_model import build_strategy_data_trust_rows
from app.services.backtest_weighted_portfolio import build_weighted_portfolio_bundle
from app.runtime.backtest import BacktestInputError

SavedPortfolioStrategyRunner = Callable[..., dict[str, Any]]
SavedPortfolioOverrideResolver = Callable[..., dict[str, Any]]


@dataclass(frozen=True)
class SavedPortfolioReplayResult:
    bundles: list[dict[str, Any]]
    weighted_bundle: dict[str, Any]
    selected_strategies: list[str]
    weights_percent: list[float]
    date_policy: str
    replay_source_context: dict[str, Any]
    compare_history_bundle: dict[str, Any]
    compare_history_context: dict[str, Any]
    weighted_history_context: dict[str, Any]


def replay_saved_portfolio_record(
    record: dict[str, Any],
    *,
    run_strategy: SavedPortfolioStrategyRunner,
    resolve_dynamic_inputs: SavedPortfolioOverrideResolver | None = None,
) -> SavedPortfolioReplayResult:
    compare_context = dict(record.get("compare_context") or {})
    upstream_source_context = dict(record.get("source_context") or {})
    selected_strategies = list(compare_context.get("selected_strategies") or [])
    if not selected_strategies:
        raise BacktestInputError("Saved portfolio does not contain selected strategies.")

    strategy_overrides = dict(compare_context.get("strategy_overrides") or {})
    bundles: list[dict[str, Any]] = []
    for strategy_name in selected_strategies:
        override = dict(strategy_overrides.get(strategy_name) or {})
        if resolve_dynamic_inputs is not None:
            override = resolve_dynamic_inputs(strategy_name=strategy_name, override=override)
        bundles.append(
            run_strategy(
                strategy_name,
                start=str(compare_context.get("start")),
                end=str(compare_context.get("end")),
                timeframe=str(compare_context.get("timeframe") or "1d"),
                option=str(compare_context.get("option") or "month_end"),
                overrides=override,
            )
        )

    portfolio_context = dict(record.get("portfolio_context") or {})
    weights_percent = [float(weight) for weight in (portfolio_context.get("weights_percent") or [])]
    if len(weights_percent) != len(selected_strategies):
        raise BacktestInputError("Saved portfolio weight count does not match the saved strategy count.")

    date_policy = str(portfolio_context.get("date_policy") or "intersection")
    replay_source_context = {
        "source_kind": "saved_portfolio",
        "source_label": record.get("name"),
        "saved_portfolio_id": record.get("portfolio_id"),
        "selected_strategies": selected_strategies,
        "weights_percent": weights_percent,
        "upstream_source_context": upstream_source_context,
    }
    compact_source_context = {
        "source_kind": "saved_portfolio",
        "source_label": record.get("name"),
        "saved_portfolio_id": record.get("portfolio_id"),
    }

    weighted_bundle = build_weighted_portfolio_bundle(
        bundles=bundles,
        weights_percent=weights_percent,
        date_policy=date_policy,
        portfolio_name=str(record.get("name") or ""),
        portfolio_id=str(record.get("portfolio_id") or ""),
        source_kind="saved_portfolio",
        compare_source_context=replay_source_context,
    )

    compare_history_bundle = {
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
    }
    compare_history_context = {
        "selected_strategies": selected_strategies,
        "strategy_overrides": strategy_overrides,
        "strategy_data_trust_rows": build_strategy_data_trust_rows(bundles),
        "weights_percent": weights_percent,
        "date_policy": portfolio_context.get("date_policy"),
        "saved_portfolio_id": record.get("portfolio_id"),
        "saved_portfolio_name": record.get("name"),
        "compare_source_context": compact_source_context,
        "strategy_summaries": [
            row
            for bundle in bundles
            for row in json.loads(bundle["summary_df"].to_json(orient="records", date_format="iso"))
        ],
    }
    weighted_history_context = {
        "selected_strategies": selected_strategies,
        "date_policy": portfolio_context.get("date_policy"),
        "weights_percent": weights_percent,
        "component_data_trust_rows": weighted_bundle.get("component_data_trust_rows") or [],
        "saved_portfolio_id": record.get("portfolio_id"),
        "saved_portfolio_name": record.get("name"),
        "compare_source_context": compact_source_context,
    }

    return SavedPortfolioReplayResult(
        bundles=bundles,
        weighted_bundle=weighted_bundle,
        selected_strategies=selected_strategies,
        weights_percent=weights_percent,
        date_policy=date_policy,
        replay_source_context=replay_source_context,
        compare_history_bundle=compare_history_bundle,
        compare_history_context=compare_history_context,
        weighted_history_context=weighted_history_context,
    )


__all__ = ["SavedPortfolioReplayResult", "replay_saved_portfolio_record"]
