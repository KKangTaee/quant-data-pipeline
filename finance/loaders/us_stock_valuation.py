from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

import pandas as pd

from finance.data.db.mysql import MySQLClient


QueryFn = Callable[[str, str, tuple[Any, ...]], list[dict[str, Any]]]


def _query(
    database: str,
    sql: str,
    params: tuple[Any, ...],
    *,
    query_fn: QueryFn | None,
) -> list[dict[str, Any]]:
    if query_fn is not None:
        return list(query_fn(database, sql, params))
    db = MySQLClient("localhost", "root", "1234", 3306)
    try:
        db.use_db(database)
        return db.query(sql, params)
    finally:
        db.close()


def _cik_text(value: Any) -> str | None:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return f"{number:010d}" if number > 0 else None


def load_us_stock_identity(
    symbol: str,
    *,
    query_fn: QueryFn | None = None,
) -> dict[str, Any] | None:
    """Resolve one current SEC-linked common-stock identity from stored evidence."""
    normalized = str(symbol or "").strip().upper()
    if not normalized:
        return None
    rows = _query(
        "finance_meta",
        """
        SELECT symbol, name, related_cik, first_seen_date, last_seen_date,
               evidence_json,
               JSON_UNQUOTE(JSON_EXTRACT(evidence_json, '$.exchange')) AS exchange
        FROM nyse_symbol_lifecycle
        WHERE symbol = %s
          AND kind = 'stock'
          AND listing_status = 'active'
          AND source = 'sec_company_tickers_exchange'
          AND related_cik IS NOT NULL
        ORDER BY collected_at DESC, updated_at DESC
        LIMIT 1
        """,
        (normalized,),
        query_fn=query_fn,
    )
    if not rows:
        return None
    row = dict(rows[0])
    evidence = row.get("evidence_json")
    if isinstance(evidence, str):
        try:
            evidence = json.loads(evidence)
        except json.JSONDecodeError:
            evidence = {}
    if not isinstance(evidence, dict):
        evidence = {}
    exchange = str(row.get("exchange") or evidence.get("exchange") or "").strip() or None
    name = str(row.get("name") or "").strip() or normalized
    return {
        "symbol": normalized,
        "name": name,
        "exchange": exchange,
        "cik": _cik_text(row.get("related_cik")),
        "instrument_type": "common_stock",
        "adr_unit_status": "unverified" if "adr" in name.lower() else "not_adr",
        "first_seen_date": row.get("first_seen_date"),
        "last_seen_date": row.get("last_seen_date"),
        "identity_source": "sec_company_tickers_exchange",
    }


def _coverage(
    *,
    identity: dict[str, Any] | None,
    prices: list[dict[str, Any]],
    statements: list[dict[str, Any]],
    valuation_months: int,
    as_of: pd.Timestamp,
) -> dict[str, Any]:
    price_frame = pd.DataFrame(prices)
    statement_frame = pd.DataFrame(statements)
    price_months = 0
    first_price_date = None
    latest_price_date = None
    if not price_frame.empty and "date" in price_frame:
        dates = pd.to_datetime(price_frame["date"], errors="coerce").dropna()
        if not dates.empty:
            price_months = int(dates.dt.to_period("M").nunique())
            first_price_date = dates.min().strftime("%Y-%m-%d")
            latest_price_date = dates.max().strftime("%Y-%m-%d")
    latest_statement_available_at = None
    if not statement_frame.empty and "available_at" in statement_frame:
        available = pd.to_datetime(statement_frame["available_at"], errors="coerce").dropna()
        if not available.empty:
            latest_statement_available_at = available.max().strftime("%Y-%m-%d")
    first_seen = pd.to_datetime((identity or {}).get("first_seen_date"), errors="coerce")
    listing_months = (
        int((as_of.to_period("M") - pd.Timestamp(first_seen).to_period("M")).n) + 1
        if not pd.isna(first_seen)
        else None
    )
    return {
        "requested_months": int(valuation_months),
        "price_months": price_months,
        "price_missing": price_months < int(valuation_months),
        "first_price_date": first_price_date,
        "latest_price_date": latest_price_date,
        "statement_row_count": int(len(statement_frame)),
        "statement_missing": statement_frame.empty,
        "latest_statement_available_at": latest_statement_available_at,
        "listing_months": listing_months,
    }


def load_us_stock_valuation_inputs(
    symbol: str,
    *,
    as_of_date: str | None = None,
    valuation_months: int = 119,
    statement_lookback_months: int = 18,
    query_fn: QueryFn | None = None,
) -> dict[str, Any]:
    """Read one symbol's bounded price, SEC EPS, and SEP evidence without writes."""
    normalized = str(symbol or "").strip().upper()
    as_of = pd.Timestamp(as_of_date or pd.Timestamp.now().strftime("%Y-%m-%d")).normalize()
    months = max(1, int(valuation_months))
    lookback = max(0, int(statement_lookback_months))
    valuation_start = as_of.to_period("M").to_timestamp() - pd.DateOffset(months=months - 1)
    statement_start = valuation_start - pd.DateOffset(months=lookback)
    start_text = valuation_start.strftime("%Y-%m-%d")
    statement_start_text = statement_start.strftime("%Y-%m-%d")
    end_text = as_of.strftime("%Y-%m-%d")

    identity = load_us_stock_identity(normalized, query_fn=query_fn)
    if identity is None:
        return {
            "identity": None,
            "price_rows": [],
            "statement_rows": [],
            "sep_rows": [],
            "window": {
                "valuation_start": start_text,
                "statement_start": statement_start_text,
                "as_of_date": end_text,
                "valuation_months": months,
            },
            "coverage": {"identity_missing": True},
        }

    price_rows = _query(
        "finance_price",
        """
        SELECT symbol, `date`, close, adj_close, stock_splits
        FROM nyse_price_history
        WHERE symbol = %s
          AND timeframe = '1d'
          AND `date` BETWEEN %s AND %s
        ORDER BY `date` ASC
        """,
        (normalized, start_text, end_text),
        query_fn=query_fn,
    )
    statement_rows = _query(
        "finance_fundamental",
        """
        SELECT symbol, concept, unit, source_period_type, period_type,
               fiscal_year, fiscal_quarter, period_start, period_end,
               value, available_at, report_date, form_type, accession_no, source
        FROM nyse_financial_statement_values
        WHERE symbol = %s
          AND period_end >= %s
          AND available_at <= %s
          AND source_period_type = 'duration'
          AND period_type IN ('Q', 'FY')
          AND (
            concept LIKE '%%EarningsPerShareDiluted'
            OR concept LIKE '%%EarningsPerShareBasicAndDiluted'
            OR concept LIKE '%%DilutedEarningsLossPerShare'
          )
          AND LOWER(unit) IN ('usd per share', 'usd/shares', 'usd/share')
        ORDER BY period_end ASC, available_at ASC, accession_no ASC
        """,
        (normalized, statement_start_text, end_text),
        query_fn=query_fn,
    )
    sep_rows = _query(
        "finance_meta",
        """
        SELECT release_date, target_year, variable_name, statistic_name,
               value_pct, source, source_ref
        FROM fomc_sep_projection
        WHERE release_date >= %s
          AND release_date <= %s
          AND variable_name IN ('real_gdp', 'pce_inflation')
        ORDER BY release_date ASC, target_year ASC, variable_name ASC, statistic_name ASC
        """,
        (statement_start_text, end_text),
        query_fn=query_fn,
    )
    return {
        "identity": identity,
        "price_rows": price_rows,
        "statement_rows": statement_rows,
        "sep_rows": sep_rows,
        "window": {
            "valuation_start": start_text,
            "statement_start": statement_start_text,
            "as_of_date": end_text,
            "valuation_months": months,
        },
        "coverage": _coverage(
            identity=identity,
            prices=price_rows,
            statements=statement_rows,
            valuation_months=months,
            as_of=as_of,
        ),
    }
