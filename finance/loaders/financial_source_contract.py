from __future__ import annotations

from typing import Any

import pandas as pd


LEGACY_BROAD_YFINANCE_SOURCE = "legacy_broad_yfinance"
SEC_EDGAR_STATEMENT_SHADOW_SOURCE = "sec_edgar_statement_shadow"
SEC_EDGAR_STATEMENT_STRICT_SOURCE = "sec_edgar_statement_strict"

FINANCIAL_SOURCE_CONTRACT_COLUMNS = [
    "source",
    "financial_source",
    "financial_source_mode",
    "source_table",
    "source_detail",
    "available_at",
    "form_type",
    "accession_no",
]


def _column_or_default(
    df: pd.DataFrame,
    column: str | None,
    default: Any,
    *,
    datetime_value: bool = False,
) -> Any:
    if column and column in df.columns:
        values = df[column]
        return pd.to_datetime(values, errors="coerce") if datetime_value else values
    return default


def apply_financial_source_contract(
    df: pd.DataFrame,
    *,
    financial_source: str,
    financial_source_mode: str,
    source_table: str,
    source_detail: str | None = None,
    available_at_column: str | None = None,
    form_type_column: str | None = None,
    accession_no_column: str | None = None,
) -> pd.DataFrame:
    """Attach source contract columns without changing existing provider-normalized fields."""

    out = df.copy()
    out["source"] = financial_source
    out["financial_source"] = financial_source
    out["financial_source_mode"] = financial_source_mode
    out["source_table"] = source_table
    out["source_detail"] = source_detail or ""
    out["available_at"] = _column_or_default(
        out,
        available_at_column,
        pd.NaT,
        datetime_value=True,
    )
    out["form_type"] = _column_or_default(out, form_type_column, None)
    out["accession_no"] = _column_or_default(out, accession_no_column, None)
    return out


def source_contract_columns_present(df: pd.DataFrame) -> list[str]:
    return [column for column in FINANCIAL_SOURCE_CONTRACT_COLUMNS if column in df.columns]
