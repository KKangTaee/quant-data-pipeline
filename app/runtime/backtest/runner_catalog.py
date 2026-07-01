from __future__ import annotations

from importlib import import_module
from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class BacktestRunnerDefinition:
    strategy_key: str
    display_name: str
    runtime_module: str
    runtime_family: str
    runner_name: str
    result_family: str
    supports_compare: bool = True
    supports_saved_replay: bool = True


_RUNNER_DEFINITIONS = [
    BacktestRunnerDefinition(
        "equal_weight",
        "Equal Weight",
        "app.runtime.backtest.runners.equal_weight",
        "price_strategy",
        "run_equal_weight_backtest_from_db",
        "single_strategy",
    ),
    BacktestRunnerDefinition(
        "gtaa",
        "GTAA",
        "app.runtime.backtest.runners.gtaa",
        "price_strategy",
        "run_gtaa_backtest_from_db",
        "single_strategy",
    ),
    BacktestRunnerDefinition(
        "global_relative_strength",
        "Global Relative Strength",
        "app.runtime.backtest.runners.global_relative_strength",
        "price_strategy",
        "run_global_relative_strength_backtest_from_db",
        "single_strategy",
    ),
    BacktestRunnerDefinition(
        "risk_parity_trend",
        "Risk Parity Trend",
        "app.runtime.backtest.runners.risk_parity_trend",
        "price_strategy",
        "run_risk_parity_trend_backtest_from_db",
        "single_strategy",
    ),
    BacktestRunnerDefinition(
        "dual_momentum",
        "Dual Momentum",
        "app.runtime.backtest.runners.dual_momentum",
        "price_strategy",
        "run_dual_momentum_backtest_from_db",
        "single_strategy",
    ),
    BacktestRunnerDefinition(
        "risk_on_momentum_5d",
        "Risk-On Momentum 5D",
        "app.runtime.backtest.runners.risk_on_momentum",
        "swing_strategy",
        "run_risk_on_momentum_5d_backtest_from_db",
        "single_strategy",
    ),
    BacktestRunnerDefinition(
        "quality_snapshot",
        "Quality Snapshot",
        "app.runtime.backtest.runners.strict_factor",
        "factor_strategy",
        "run_quality_snapshot_backtest_from_db",
        "single_strategy",
    ),
    BacktestRunnerDefinition(
        "quality_snapshot_strict_annual",
        "Quality Snapshot (Strict Annual)",
        "app.runtime.backtest.runners.strict_factor",
        "factor_strategy",
        "run_quality_snapshot_strict_annual_backtest_from_db",
        "single_strategy",
    ),
    BacktestRunnerDefinition(
        "quality_snapshot_strict_quarterly_prototype",
        "Quality Snapshot (Strict Quarterly Prototype)",
        "app.runtime.backtest.runners.strict_factor",
        "factor_strategy",
        "run_quality_snapshot_strict_quarterly_prototype_backtest_from_db",
        "single_strategy",
    ),
    BacktestRunnerDefinition(
        "value_snapshot_strict_annual",
        "Value Snapshot (Strict Annual)",
        "app.runtime.backtest.runners.strict_factor",
        "factor_strategy",
        "run_value_snapshot_strict_annual_backtest_from_db",
        "single_strategy",
    ),
    BacktestRunnerDefinition(
        "value_snapshot_strict_quarterly_prototype",
        "Value Snapshot (Strict Quarterly Prototype)",
        "app.runtime.backtest.runners.strict_factor",
        "factor_strategy",
        "run_value_snapshot_strict_quarterly_prototype_backtest_from_db",
        "single_strategy",
    ),
    BacktestRunnerDefinition(
        "quality_value_snapshot_strict_annual",
        "Quality + Value Snapshot (Strict Annual)",
        "app.runtime.backtest.runners.strict_factor",
        "factor_strategy",
        "run_quality_value_snapshot_strict_annual_backtest_from_db",
        "single_strategy",
    ),
    BacktestRunnerDefinition(
        "quality_value_snapshot_strict_quarterly_prototype",
        "Quality + Value Snapshot (Strict Quarterly Prototype)",
        "app.runtime.backtest.runners.strict_factor",
        "factor_strategy",
        "run_quality_value_snapshot_strict_quarterly_prototype_backtest_from_db",
        "single_strategy",
    ),
]

_RUNNER_BY_KEY = {definition.strategy_key: definition for definition in _RUNNER_DEFINITIONS}
_RUNNER_BY_DISPLAY_NAME = {definition.display_name: definition for definition in _RUNNER_DEFINITIONS}


def known_strategy_keys() -> list[str]:
    return sorted(_RUNNER_BY_KEY)


def get_runner_definition(strategy_key: str | None) -> BacktestRunnerDefinition | None:
    return _RUNNER_BY_KEY.get(str(strategy_key or "").strip())


def require_runner_definition(strategy_key: str | None) -> BacktestRunnerDefinition:
    definition = get_runner_definition(strategy_key)
    if definition is None:
        raise KeyError(f"Unknown backtest strategy runner: {strategy_key}")
    return definition


def get_runner_definition_for_display_name(display_name: str | None) -> BacktestRunnerDefinition | None:
    return _RUNNER_BY_DISPLAY_NAME.get(str(display_name or "").strip())


def load_runner_callable(definition: BacktestRunnerDefinition) -> Callable[..., Any]:
    module = import_module(definition.runtime_module)
    runner = getattr(module, definition.runner_name)
    if not callable(runner):
        raise TypeError(f"Backtest runner is not callable: {definition.runtime_module}.{definition.runner_name}")
    return runner


__all__ = [
    "BacktestRunnerDefinition",
    "get_runner_definition",
    "get_runner_definition_for_display_name",
    "load_runner_callable",
    "known_strategy_keys",
    "require_runner_definition",
]
