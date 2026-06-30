from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BacktestRunnerDefinition:
    strategy_key: str
    display_name: str
    runtime_module: str
    runtime_family: str


_RUNNER_DEFINITIONS = [
    BacktestRunnerDefinition("equal_weight", "Equal Weight", "app.runtime.backtest", "price_strategy"),
    BacktestRunnerDefinition("gtaa", "GTAA", "app.runtime.backtest", "price_strategy"),
    BacktestRunnerDefinition(
        "global_relative_strength",
        "Global Relative Strength",
        "app.runtime.backtest",
        "price_strategy",
    ),
    BacktestRunnerDefinition("risk_parity_trend", "Risk Parity Trend", "app.runtime.backtest", "price_strategy"),
    BacktestRunnerDefinition("dual_momentum", "Dual Momentum", "app.runtime.backtest", "price_strategy"),
    BacktestRunnerDefinition(
        "risk_on_momentum_5d",
        "Risk-On Momentum 5D",
        "app.runtime.backtest_risk_on_momentum",
        "swing_strategy",
    ),
    BacktestRunnerDefinition("quality_snapshot", "Quality Snapshot", "app.runtime.backtest_strict", "factor_strategy"),
    BacktestRunnerDefinition(
        "quality_snapshot_strict_annual",
        "Quality Snapshot (Strict Annual)",
        "app.runtime.backtest_strict",
        "factor_strategy",
    ),
    BacktestRunnerDefinition(
        "quality_snapshot_strict_quarterly_prototype",
        "Quality Snapshot (Strict Quarterly Prototype)",
        "app.runtime.backtest_strict",
        "factor_strategy",
    ),
    BacktestRunnerDefinition(
        "value_snapshot_strict_annual",
        "Value Snapshot (Strict Annual)",
        "app.runtime.backtest_strict",
        "factor_strategy",
    ),
    BacktestRunnerDefinition(
        "value_snapshot_strict_quarterly_prototype",
        "Value Snapshot (Strict Quarterly Prototype)",
        "app.runtime.backtest_strict",
        "factor_strategy",
    ),
    BacktestRunnerDefinition(
        "quality_value_snapshot_strict_annual",
        "Quality + Value Snapshot (Strict Annual)",
        "app.runtime.backtest_strict",
        "factor_strategy",
    ),
    BacktestRunnerDefinition(
        "quality_value_snapshot_strict_quarterly_prototype",
        "Quality + Value Snapshot (Strict Quarterly Prototype)",
        "app.runtime.backtest_strict",
        "factor_strategy",
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


__all__ = [
    "BacktestRunnerDefinition",
    "get_runner_definition",
    "get_runner_definition_for_display_name",
    "known_strategy_keys",
    "require_runner_definition",
]
