"""
Runtime-oriented database loader package for Phase 3.

This package will expose public loader entry points while keeping
shared normalization and query helpers inside domain modules.
"""

from .financial_statements import (
    load_statement_coverage_summary,
    load_statement_labels,
    load_statement_snapshot_strict,
    load_statement_timing_audit,
    load_statement_values,
)
from .factors import (
    load_factor_matrix,
    load_factor_snapshot,
    load_factors,
    load_statement_factor_snapshot_shadow,
    load_statement_factors_shadow,
    load_statement_quality_snapshot_strict,
)
from .fundamentals import (
    load_fundamental_snapshot,
    load_fundamentals,
    load_statement_fundamentals_shadow,
    load_statement_shadow_coverage_summary,
)
from .price import load_latest_market_date, load_price_freshness_summary, load_price_history, load_price_matrix
from .runtime_adapter import adapt_price_history_to_strategy_dfs, load_price_strategy_dfs
from .universe import load_asset_profile_status_summary, load_universe

__all__ = [
    "load_universe",
    "load_latest_market_date",
    "load_price_history",
    "load_price_freshness_summary",
    "load_price_matrix",
    "load_fundamentals",
    "load_fundamental_snapshot",
    "load_statement_fundamentals_shadow",
    "load_statement_shadow_coverage_summary",
    "load_factors",
    "load_factor_snapshot",
    "load_factor_matrix",
    "load_statement_factor_snapshot_shadow",
    "load_statement_factors_shadow",
    "load_statement_quality_snapshot_strict",
    "load_statement_values",
    "load_statement_labels",
    "load_statement_coverage_summary",
    "load_statement_snapshot_strict",
    "load_statement_timing_audit",
    "adapt_price_history_to_strategy_dfs",
    "load_price_strategy_dfs",
    "load_asset_profile_status_summary",
]
