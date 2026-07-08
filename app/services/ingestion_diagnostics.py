from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import date
from typing import Any

import pandas as pd

from app.jobs.diagnostics import (
    inspect_price_stale_symbols,
    inspect_statement_coverage_symbols,
    inspect_statement_universe_coverage,
)
from finance.data.financial_statements import inspect_financial_statement_source
from finance.loaders import load_statement_coverage_summary, load_statement_timing_audit
from finance.loaders.price import load_price_window_summary


def _normalize_symbols(symbols: Sequence[str] | Iterable[str] | None) -> list[str]:
    if symbols is None:
        return []
    return [str(symbol).strip().upper() for symbol in symbols if str(symbol).strip()]


def load_price_window_preflight_summary(
    symbols: Sequence[str] | Iterable[str],
    *,
    start: str | None,
    end: str | None,
    timeframe: str,
) -> pd.DataFrame:
    """Read existing DB price-window coverage for the Ingestion preflight card."""

    return load_price_window_summary(
        symbols=_normalize_symbols(symbols),
        start=start,
        end=end,
        timeframe=timeframe,
    )


def run_price_stale_diagnosis(
    symbols: str | Iterable[str] | None,
    *,
    end: str | date | None,
    timeframe: str = "1d",
) -> dict[str, Any]:
    """Run read-only stale price diagnosis without writing DB rows."""

    return inspect_price_stale_symbols(
        symbols,
        end=end,
        timeframe=timeframe,
    )


def run_statement_coverage_diagnosis(
    symbols: str | Iterable[str] | None,
    *,
    freq: str,
    sample_size: int,
) -> dict[str, Any]:
    """Run read-only strict statement coverage recovery diagnosis."""

    return inspect_statement_coverage_symbols(
        symbols,
        freq=freq,
        sample_size=sample_size,
    )


def run_statement_universe_coverage_qa(
    *,
    universe_code: str,
    universe_limit: int | None,
    freq: str,
    as_of_date: str | date | None,
) -> dict[str, Any]:
    """Run DB-backed EDGAR statement coverage QA for a broad universe."""

    return inspect_statement_universe_coverage(
        universe_code=universe_code,
        universe_limit=universe_limit,
        freq=freq,
        as_of_date=as_of_date,
    )


def run_statement_pit_inspection(
    symbols: Sequence[str] | Iterable[str],
    *,
    inspect_freq: str,
    audit_symbol_limit: int,
    audit_limit_per_symbol: int,
    source_symbol: str | None,
    source_sample_size: int,
) -> dict[str, Any]:
    """Collect read-only statement PIT inspection frames and one optional source sample."""

    normalized_symbols = _normalize_symbols(symbols)
    audit_scope = normalized_symbols[:audit_symbol_limit]
    normalized_source_symbol = str(source_symbol or "").strip().upper()

    coverage_df = load_statement_coverage_summary(
        symbols=normalized_symbols,
        freq=inspect_freq,
    )
    audit_df = load_statement_timing_audit(
        symbols=audit_scope,
        freq=inspect_freq,
        limit_per_symbol=audit_limit_per_symbol,
    )
    source_payload = (
        inspect_financial_statement_source(normalized_source_symbol, sample_size=source_sample_size)
        if normalized_source_symbol
        else None
    )

    return {
        "inspect_freq": inspect_freq,
        "coverage_df": coverage_df,
        "audit_df": audit_df,
        "audit_scope": audit_scope,
        "source_symbol": normalized_source_symbol,
        "source_payload": source_payload,
    }
