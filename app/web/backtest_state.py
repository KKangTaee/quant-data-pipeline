from __future__ import annotations

from app.web.backtest_common import (
    BACKTEST_WORKFLOW_PANEL_OPTIONS,
    QUALITY_STRICT_PRESETS,
    _activate_backtest_workflow_panel,
    _init_backtest_state,
    _request_backtest_panel,
    _set_single_strategy_target_from_strategy_key,
    clear_backtest_preview_caches,
)


def init_backtest_state() -> None:
    _init_backtest_state()


def request_backtest_panel(panel: str) -> None:
    _request_backtest_panel(panel)


def activate_backtest_workflow_panel() -> None:
    _activate_backtest_workflow_panel()


def set_single_strategy_target_from_strategy_key(strategy_key: str | None) -> None:
    _set_single_strategy_target_from_strategy_key(strategy_key)


__all__ = [
    "BACKTEST_WORKFLOW_PANEL_OPTIONS",
    "QUALITY_STRICT_PRESETS",
    "activate_backtest_workflow_panel",
    "clear_backtest_preview_caches",
    "init_backtest_state",
    "request_backtest_panel",
    "set_single_strategy_target_from_strategy_key",
]
