from __future__ import annotations

import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from app.runtime.backtest import BacktestDataError, BacktestInputError

CompareStrategyRunner = Callable[..., dict[str, Any]]


@dataclass(frozen=True)
class StrategyCompareExecutionResult:
    ok: bool
    bundles: list[dict[str, Any]] | None = None
    error_kind: str | None = None
    error_message: str | None = None
    elapsed_seconds: float = 0.0


def execute_strategy_compare(
    strategy_names: Sequence[str],
    *,
    start: str,
    end: str,
    timeframe: str,
    option: str,
    overrides_by_strategy: Mapping[str, Mapping[str, Any]] | None,
    run_strategy: CompareStrategyRunner,
) -> StrategyCompareExecutionResult:
    """Run a manual multi-strategy compare without depending on Streamlit UI state."""

    started_at = time.perf_counter()
    try:
        bundles = [
            run_strategy(
                strategy_name,
                start=start,
                end=end,
                timeframe=timeframe,
                option=option,
                overrides=dict((overrides_by_strategy or {}).get(strategy_name) or {}),
            )
            for strategy_name in strategy_names
        ]
    except BacktestInputError as exc:
        return StrategyCompareExecutionResult(
            ok=False,
            error_kind="input",
            error_message=f"Comparison input issue: {exc}",
        )
    except BacktestDataError as exc:
        return StrategyCompareExecutionResult(
            ok=False,
            error_kind="data",
            error_message=f"Comparison data issue: {exc}",
        )
    except Exception as exc:
        return StrategyCompareExecutionResult(
            ok=False,
            error_kind="system",
            error_message=f"Comparison execution failed: {exc}",
        )

    return StrategyCompareExecutionResult(
        ok=True,
        bundles=bundles,
        elapsed_seconds=time.perf_counter() - started_at,
    )


__all__ = ["StrategyCompareExecutionResult", "execute_strategy_compare"]
