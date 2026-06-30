from __future__ import annotations

from typing import Any

import pandas as pd


SAFE_QUARTERLY_STATEMENT_FORMS = frozenset({"10-Q", "10-Q/A"})
QUARTERLY_FLOW_STATEMENT_COLUMNS = frozenset(
    {
        "total_revenue",
        "gross_profit",
        "operating_income",
        "ebit",
        "pretax_income",
        "interest_expense",
        "net_income",
        "operating_cash_flow",
        "free_cash_flow",
        "capital_expenditure",
        "dividends_paid",
    }
)
QUARTERLY_FLOW_SOURCE_COLUMNS = frozenset(
    {
        "gross_profit_source",
        "operating_income_source",
        "ebit_source",
        "free_cash_flow_source",
    }
)


def normalize_statement_form_type(value: Any) -> str:
    try:
        if value is None or pd.isna(value):
            return ""
    except (TypeError, ValueError):
        if value is None:
            return ""
    return str(value).strip().upper()


def is_safe_quarterly_statement_form(value: Any) -> bool:
    return normalize_statement_form_type(value) in SAFE_QUARTERLY_STATEMENT_FORMS


def filter_safe_quarterly_statement_rows(
    df: pd.DataFrame,
    *,
    freq: str,
    form_type_column: str,
) -> pd.DataFrame:
    if df.empty or str(freq).strip().lower() != "quarterly":
        return df
    if form_type_column not in df.columns:
        return df.iloc[0:0].copy().reset_index(drop=True)

    safe_mask = df[form_type_column].map(is_safe_quarterly_statement_form)
    return df[safe_mask].copy().reset_index(drop=True)


def sanitize_quarterly_statement_flow_record(record: dict[str, Any]) -> dict[str, Any]:
    out = dict(record)
    if str(out.get("freq") or "").strip().lower() != "quarterly":
        return out

    form_type = normalize_statement_form_type(out.get("latest_form_type") or out.get("form_type"))
    if is_safe_quarterly_statement_form(form_type):
        return out

    for column in QUARTERLY_FLOW_STATEMENT_COLUMNS:
        if column in out:
            out[column] = None
    for column in QUARTERLY_FLOW_SOURCE_COLUMNS:
        if column in out:
            out[column] = "blocked_10k_fy_flow"

    out["source_mode"] = "quarterly_10k_flow_blocked"
    out["timing_basis"] = "blocked_10k_fy_flow"
    reason = (
        f"quarterly flow values blocked for {form_type or 'unknown'} filing; "
        "Q4 synthetic adjustment is not implemented"
    )
    existing_error = out.get("error_msg")
    out["error_msg"] = f"{existing_error}; {reason}" if existing_error else reason
    return out
