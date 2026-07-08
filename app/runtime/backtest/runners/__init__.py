from __future__ import annotations

from app.runtime.backtest.runners.dual_momentum import run_dual_momentum_backtest_from_db
from app.runtime.backtest.runners.equal_weight import run_equal_weight_backtest_from_db
from app.runtime.backtest.runners.global_relative_strength import run_global_relative_strength_backtest_from_db
from app.runtime.backtest.runners.gtaa import run_gtaa_backtest_from_db
from app.runtime.backtest.runners.risk_on_momentum import run_risk_on_momentum_5d_backtest_from_db
from app.runtime.backtest.runners.risk_parity_trend import run_risk_parity_trend_backtest_from_db
from app.runtime.backtest.runners.strict_factor import (
    run_quality_snapshot_backtest_from_db,
    run_quality_snapshot_strict_annual_backtest_from_db,
    run_quality_snapshot_strict_quarterly_prototype_backtest_from_db,
    run_quality_value_snapshot_strict_annual_backtest_from_db,
    run_quality_value_snapshot_strict_quarterly_prototype_backtest_from_db,
    run_statement_quality_prototype_backtest_from_db,
    run_value_snapshot_strict_annual_backtest_from_db,
    run_value_snapshot_strict_quarterly_prototype_backtest_from_db,
)

__all__ = [
    "run_dual_momentum_backtest_from_db",
    "run_equal_weight_backtest_from_db",
    "run_global_relative_strength_backtest_from_db",
    "run_gtaa_backtest_from_db",
    "run_quality_snapshot_backtest_from_db",
    "run_quality_snapshot_strict_annual_backtest_from_db",
    "run_quality_snapshot_strict_quarterly_prototype_backtest_from_db",
    "run_quality_value_snapshot_strict_annual_backtest_from_db",
    "run_quality_value_snapshot_strict_quarterly_prototype_backtest_from_db",
    "run_risk_on_momentum_5d_backtest_from_db",
    "run_risk_parity_trend_backtest_from_db",
    "run_statement_quality_prototype_backtest_from_db",
    "run_value_snapshot_strict_annual_backtest_from_db",
    "run_value_snapshot_strict_quarterly_prototype_backtest_from_db",
]
