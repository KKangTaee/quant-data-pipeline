from __future__ import annotations

import json
import re
from collections.abc import Callable
from typing import Any

import pandas as pd

from finance.data.db.mysql import MySQLClient
from finance.data.us_stock_valuation import build_monthly_pit_valuation


QueryFn = Callable[[str, str, tuple[Any, ...]], list[dict[str, Any]]]
NON_COMMON_NAME_PATTERN = re.compile(
    r"\b(etf|exchange[- ]traded|mutual fund|fund|preferred|preference|warrant|unit|rights?)\b",
    re.IGNORECASE,
)
SUPPORTED_EXCHANGES = {
    "NASDAQ",
    "NASDAQGS",
    "NASDAQGM",
    "NASDAQCM",
    "NYSE",
    "NYSE AMERICAN",
    "NYSEAMERICAN",
}


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


def _is_supported_common_stock_row(row: dict[str, Any]) -> bool:
    kind = str(row.get("kind") or "stock").strip().lower()
    listing_status = str(row.get("listing_status") or "active").strip().lower()
    quote_type = str(row.get("quote_type") or "equity").strip().upper()
    exchange = str(row.get("exchange") or "").strip().upper()
    name = str(row.get("name") or "").strip()
    security_type = str(row.get("security_type") or "common_stock").strip().lower()
    if kind != "stock" or listing_status != "active":
        return False
    if quote_type not in {"EQUITY", "STOCK", ""}:
        return False
    if exchange and exchange not in SUPPORTED_EXCHANGES:
        return False
    if security_type not in {"common_stock", "common", "equity", "stock", ""}:
        return False
    return not NON_COMMON_NAME_PATTERN.search(name)


def search_us_common_stocks(
    query: str,
    *,
    limit: int = 12,
    query_fn: QueryFn | None = None,
) -> list[dict[str, Any]]:
    """Search stored current SEC-linked U.S. common stocks without provider calls."""
    normalized = " ".join(str(query or "").strip().upper().split())
    if len(normalized) < 2:
        return []
    resolved_limit = min(50, max(1, int(limit)))
    rows = _query(
        "finance_meta",
        f"""
        SELECT l.symbol, l.name, l.related_cik, l.kind, l.listing_status,
               l.evidence_json,
               JSON_UNQUOTE(JSON_EXTRACT(l.evidence_json, '$.exchange')) AS exchange,
               p.quote_type
        FROM nyse_symbol_lifecycle l
        LEFT JOIN nyse_asset_profile p
          ON p.symbol = l.symbol AND p.kind = 'stock'
        WHERE l.kind = 'stock'
          AND l.listing_status = 'active'
          AND l.source = 'sec_company_tickers_exchange'
          AND l.related_cik IS NOT NULL
          AND (UPPER(l.symbol) LIKE %s OR UPPER(l.name) LIKE %s)
        ORDER BY l.symbol ASC
        LIMIT {resolved_limit * 5}
        """,
        (f"{normalized}%", f"%{normalized}%"),
        query_fn=query_fn,
    )
    candidates: list[dict[str, Any]] = []
    for raw in rows:
        row = dict(raw)
        evidence = row.get("evidence_json")
        if isinstance(evidence, str):
            try:
                evidence = json.loads(evidence)
            except json.JSONDecodeError:
                evidence = {}
        if not isinstance(evidence, dict):
            evidence = {}
        row["exchange"] = row.get("exchange") or evidence.get("exchange")
        if not _is_supported_common_stock_row(row):
            continue
        symbol = str(row.get("symbol") or "").strip().upper()
        name = str(row.get("name") or "").strip()
        cik = _cik_text(row.get("related_cik"))
        if not symbol or not name or cik is None:
            continue
        candidates.append(
            {
                "symbol": symbol,
                "name": name,
                "exchange": str(row.get("exchange") or "").strip() or None,
                "cik": cik,
                "instrument_type": "common_stock",
                "adr_unit_status": (
                    "unverified"
                    if "adr" in name.lower() or "depositary" in name.lower()
                    else "not_adr"
                ),
            }
        )

    def rank(row: dict[str, Any]) -> tuple[int, str, str]:
        symbol = row["symbol"].upper()
        name = row["name"].upper()
        if symbol == normalized:
            score = 0
        elif symbol.startswith(normalized):
            score = 1
        elif name.startswith(normalized):
            score = 2
        else:
            score = 3
        return score, symbol, name

    return sorted(candidates, key=rank)[:resolved_limit]


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


def build_us_stock_valuation_collection_plan(
    symbol: str,
    *,
    as_of_date: str | None = None,
    loaded_inputs: dict[str, Any] | None = None,
    input_loader: Callable[..., dict[str, Any]] = load_us_stock_valuation_inputs,
) -> dict[str, Any]:
    """Classify exact one-symbol raw gaps without treating structural P/E limits as repairable."""
    normalized = str(symbol or "").strip().upper()
    inputs = dict(
        loaded_inputs
        or input_loader(normalized, as_of_date=as_of_date, valuation_months=119)
    )
    identity = inputs.get("identity")
    base = {"symbol": normalized, "identity": identity, "scopes": [], "missing_ranges": {}}
    if not isinstance(identity, dict) or str(identity.get("symbol") or "").strip().upper() != normalized:
        return {
            **base,
            "status": "ERROR",
            "reason_code": "IDENTITY_MISMATCH",
            "reason": "선택 ticker와 current SEC identity를 확인할 수 없습니다.",
        }
    coverage = dict(inputs.get("coverage") or {})
    listing_months = coverage.get("listing_months")
    if listing_months is not None and int(listing_months) < 60:
        return {
            **base,
            "status": "NOT_APPLICABLE",
            "reason_code": "STRUCTURALLY_SHORT_LISTING",
            "reason": f"상장 이력 {int(listing_months)}개월로 60개월 P/E 구간을 만들 수 없습니다.",
        }
    window = dict(inputs.get("window") or {})
    monthly_rows = [dict(row) for row in inputs.get("monthly_rows") or []]
    if not monthly_rows:
        monthly_rows = build_monthly_pit_valuation(
            inputs.get("statement_rows") or [],
            inputs.get("price_rows") or [],
            start_month=str(window.get("valuation_start")),
            end_month=str(window.get("as_of_date")),
        )
    monthly_rows = sorted(monthly_rows, key=lambda row: str(row.get("month") or ""))
    latest = monthly_rows[-1] if monthly_rows else {}
    latest_eps = pd.to_numeric(latest.get("ttm_eps"), errors="coerce")
    if not pd.isna(latest_eps) and float(latest_eps) <= 0:
        return {
            **base,
            "status": "NOT_APPLICABLE",
            "reason_code": "NON_POSITIVE_EPS",
            "reason": "현재 TTM EPS가 0 이하라 자료 수집으로 PER를 만들 수 없습니다.",
        }

    last_sixty = monthly_rows[-60:]
    missing_price_months = [
        pd.Timestamp(row["month"])
        for row in last_sixty
        if pd.isna(pd.to_numeric(row.get("price"), errors="coerce"))
        or float(pd.to_numeric(row.get("price"), errors="coerce")) <= 0
    ]
    missing_eps_months = [
        pd.Timestamp(row["month"])
        for row in last_sixty
        if pd.isna(pd.to_numeric(row.get("ttm_eps"), errors="coerce"))
    ]
    if len(last_sixty) < 60:
        missing_price_months.append(pd.Timestamp(window.get("valuation_start")))
        missing_eps_months.append(pd.Timestamp(window.get("valuation_start")))

    scopes: list[str] = []
    missing_ranges: dict[str, dict[str, Any]] = {}
    if missing_price_months:
        scopes.append("prices")
        first = min(missing_price_months).to_period("M").to_timestamp()
        last = max(missing_price_months).to_period("M").to_timestamp() + pd.offsets.MonthEnd(0)
        missing_ranges["prices"] = {
            "start": first.strftime("%Y-%m-%d"),
            "end": min(last, pd.Timestamp(window.get("as_of_date"))).strftime("%Y-%m-%d"),
        }
    if missing_eps_months:
        scopes.append("sec_statements")
        missing_ranges["sec_statements"] = {
            "start": window.get("statement_start"),
            "end": window.get("as_of_date"),
        }
    if not scopes:
        return {**base, "status": "READY", "reason_code": None, "reason": None}
    return {
        **base,
        "status": "COLLECTABLE",
        "reason_code": "RAW_DATA_GAP",
        "reason": "저장 가격 또는 SEC filing-aware TTM 근거가 부족합니다.",
        "scopes": scopes,
        "missing_ranges": missing_ranges,
    }
