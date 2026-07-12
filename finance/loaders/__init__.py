"""
Runtime-oriented database loader package for Phase 3.

This package will expose public loader entry points while keeping
shared normalization and query helpers inside domain modules.
"""

from .financial_statements import (
    load_statement_coverage_summary,
    load_statement_filings,
    load_statement_labels,
    load_statement_snapshot_strict,
    load_statement_timing_audit,
    load_statement_values,
)
from .financial_source_contract import (
    LEGACY_BROAD_YFINANCE_SOURCE,
    SEC_EDGAR_STATEMENT_SHADOW_SOURCE,
    SEC_EDGAR_STATEMENT_STRICT_SOURCE,
    apply_financial_source_contract,
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
from .macro import load_macro_series_observations, load_macro_snapshot
from .nasdaq100_valuation import (
    load_latest_nasdaq100_ttm_proxy,
    load_nasdaq100_monthly_valuation,
)
from .price import (
    load_latest_market_date,
    load_latest_prices,
    load_price_freshness_summary,
    load_price_history,
    load_price_matrix,
    load_price_window_summary,
)
from .provider import load_etf_exposure_snapshot, load_etf_holdings_snapshot, load_etf_operability_snapshot
from .runtime_adapter import adapt_price_history_to_strategy_dfs, load_price_strategy_dfs
from .sp500_valuation import (
    load_latest_fomc_sep_projection,
    load_latest_shiller_ttm_eps,
    load_latest_sp500_ttm_actual_eps,
    load_sp500_monthly_valuation,
    resolve_sp500_ttm_eps,
)
from .futures import load_futures_ohlcv
from .universe import (
    load_asset_profile_status_summary,
    load_pit_universe_members,
    load_pit_universe_membership_snapshots,
    load_symbol_lifecycle_coverage_summary,
    load_universe,
)

__all__ = [
    "load_universe",
    "load_latest_market_date",
    "load_latest_prices",
    "load_price_history",
    "load_futures_ohlcv",
    "load_price_freshness_summary",
    "load_price_window_summary",
    "load_price_matrix",
    "load_etf_operability_snapshot",
    "load_etf_holdings_snapshot",
    "load_etf_exposure_snapshot",
    "load_fundamentals",
    "load_fundamental_snapshot",
    "load_statement_fundamentals_shadow",
    "load_statement_shadow_coverage_summary",
    "load_macro_series_observations",
    "load_macro_snapshot",
    "load_nasdaq100_monthly_valuation",
    "load_latest_nasdaq100_ttm_proxy",
    "load_factors",
    "load_factor_snapshot",
    "load_factor_matrix",
    "load_statement_factor_snapshot_shadow",
    "load_statement_factors_shadow",
    "load_statement_quality_snapshot_strict",
    "load_statement_values",
    "load_statement_filings",
    "load_statement_labels",
    "load_statement_coverage_summary",
    "load_statement_snapshot_strict",
    "load_statement_timing_audit",
    "LEGACY_BROAD_YFINANCE_SOURCE",
    "SEC_EDGAR_STATEMENT_SHADOW_SOURCE",
    "SEC_EDGAR_STATEMENT_STRICT_SOURCE",
    "apply_financial_source_contract",
    "adapt_price_history_to_strategy_dfs",
    "load_price_strategy_dfs",
    "load_asset_profile_status_summary",
    "load_symbol_lifecycle_coverage_summary",
    "load_pit_universe_members",
    "load_pit_universe_membership_snapshots",
    "load_sp500_monthly_valuation",
    "load_latest_sp500_ttm_actual_eps",
    "load_latest_shiller_ttm_eps",
    "load_latest_fomc_sep_projection",
    "resolve_sp500_ttm_eps",
]
