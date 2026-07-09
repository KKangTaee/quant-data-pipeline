from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pandas as pd

from finance.data.db.mysql import MySQLClient


DB_META = "finance_meta"


def _empty_frame(columns: list[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=columns)


def _normalize_symbols(symbols: str | Iterable[str] | None) -> list[str]:
    if symbols is None:
        return []
    if isinstance(symbols, str):
        raw = symbols.replace("\n", ",").split(",")
    else:
        raw = list(symbols)
    out: list[str] = []
    seen: set[str] = set()
    for item in raw:
        symbol = str(item or "").strip().upper()
        if symbol and symbol not in seen:
            out.append(symbol)
            seen.add(symbol)
    return out


def _frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def _connect(host: str, user: str, password: str, port: int) -> MySQLClient:
    db = MySQLClient(host, user, password, port)
    db.use_db(DB_META)
    return db


def _dedupe_interest_rows(rows: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
    seen: set[tuple[Any, ...]] = set()
    deduped: list[dict[str, Any]] = []
    for row in rows:
        key = (
            row.get("cik"),
            row.get("period_of_report"),
            row.get("cusip"),
            row.get("holding_symbol"),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    deduped.sort(key=lambda row: (float(row.get("reported_value") or 0.0), str(row.get("manager_name") or "")), reverse=True)
    return deduped[:limit]


def _load_mapped_cusips_for_symbol(db: MySQLClient, symbol: str, *, limit: int = 25) -> list[str]:
    rows = db.query(
        """
        SELECT DISTINCT cusip
        FROM institutional_13f_cusip_symbol_map
        WHERE symbol = %s
        ORDER BY cusip ASC
        LIMIT %s
        """,
        (symbol, int(limit)),
    )
    return [str(row["cusip"]) for row in rows if row.get("cusip")]


def _load_mapped_cusips_for_issuer(db: MySQLClient, query: str, *, limit: int = 25) -> list[str]:
    like_query = f"%{query.upper()}%"
    rows = db.query(
        """
        SELECT DISTINCT cusip
        FROM institutional_13f_cusip_symbol_map
        WHERE UPPER(issuer_name) LIKE %s
        ORDER BY cusip ASC
        LIMIT %s
        """,
        (like_query, int(limit)),
    )
    return [str(row["cusip"]) for row in rows if row.get("cusip")]


def _load_interest_rows_by_cusips(db: MySQLClient, cusips: list[str], *, limit: int) -> list[dict[str, Any]]:
    if not cusips:
        return []
    placeholders = ", ".join(["%s"] * len(cusips))
    return db.query(
        f"""
        SELECT
          m.manager_name,
          m.cik,
          f.period_of_report,
          f.filing_date,
          h.cusip,
          COALESCE(h.holding_symbol, sm.symbol) AS holding_symbol,
          h.issuer_name,
          h.reported_value,
          h.shares_or_principal_amount,
          h.source_ref,
          f.table_value_total AS total_reported_value
        FROM institutional_13f_holding h FORCE INDEX(ix_cusip)
        INNER JOIN institutional_13f_filing f
          ON h.accession_number = f.accession_number
        INNER JOIN institutional_13f_manager m
          ON m.latest_accession_number = f.accession_number
        LEFT JOIN institutional_13f_cusip_symbol_map sm
          ON h.cusip = sm.cusip
        WHERE h.cusip IN ({placeholders})
        ORDER BY h.reported_value DESC, m.manager_name ASC
        LIMIT %s
        """,
        tuple([*cusips, int(limit)]),
    )


def _load_interest_rows_by_holding_symbol(db: MySQLClient, symbol: str, *, limit: int) -> list[dict[str, Any]]:
    return db.query(
        """
        SELECT
          m.manager_name,
          m.cik,
          f.period_of_report,
          f.filing_date,
          h.cusip,
          COALESCE(h.holding_symbol, sm.symbol) AS holding_symbol,
          h.issuer_name,
          h.reported_value,
          h.shares_or_principal_amount,
          h.source_ref,
          f.table_value_total AS total_reported_value
        FROM institutional_13f_holding h FORCE INDEX(ix_holding_symbol)
        INNER JOIN institutional_13f_filing f
          ON h.accession_number = f.accession_number
        INNER JOIN institutional_13f_manager m
          ON m.latest_accession_number = f.accession_number
        LEFT JOIN institutional_13f_cusip_symbol_map sm
          ON h.cusip = sm.cusip
        WHERE h.holding_symbol = %s
        ORDER BY h.reported_value DESC, m.manager_name ASC
        LIMIT %s
        """,
        (symbol, int(limit)),
    )


def _load_interest_rows_by_issuer_text(db: MySQLClient, clean_query: str, *, limit: int) -> list[dict[str, Any]]:
    like_query = f"%{clean_query.upper()}%"
    return db.query(
        """
        SELECT
          m.manager_name,
          m.cik,
          f.period_of_report,
          f.filing_date,
          h.cusip,
          COALESCE(h.holding_symbol, sm.symbol) AS holding_symbol,
          h.issuer_name,
          h.reported_value,
          h.shares_or_principal_amount,
          h.source_ref,
          f.table_value_total AS total_reported_value
        FROM institutional_13f_manager m
        INNER JOIN institutional_13f_filing f
          ON m.latest_accession_number = f.accession_number
        INNER JOIN institutional_13f_holding h
          ON f.accession_number = h.accession_number
        LEFT JOIN institutional_13f_cusip_symbol_map sm
          ON h.cusip = sm.cusip
        WHERE UPPER(h.issuer_name) LIKE %s
           OR UPPER(sm.issuer_name) LIKE %s
        ORDER BY h.reported_value DESC, m.manager_name ASC
        LIMIT %s
        """,
        (like_query, like_query, int(limit)),
    )


def load_institutional_13f_managers(
    query: str | None = None,
    *,
    limit: int = 100,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> pd.DataFrame:
    """Load searchable 13F manager rows from finance_meta."""
    db = _connect(host, user, password, port)
    try:
        where = ""
        params: list[Any] = []
        if query and str(query).strip():
            where = "WHERE manager_name LIKE %s OR cik LIKE %s"
            token = f"%{str(query).strip()}%"
            params.extend([token, token])
        params.append(int(limit))
        rows = db.query(
            f"""
            SELECT cik, manager_name, latest_accession_number, latest_report_period,
                   latest_filing_date, filing_count, source_ref
            FROM institutional_13f_manager
            {where}
            ORDER BY latest_report_period DESC, latest_filing_date DESC, manager_name ASC
            LIMIT %s
            """,
            tuple(params),
        )
    finally:
        db.close()
    return _frame(rows)


def load_institutional_13f_managers_by_ciks(
    ciks: Iterable[str],
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> pd.DataFrame:
    """Load manager rows for explicit CIKs, preserving the DB read-only loader boundary."""
    normalized: list[str] = []
    for cik in ciks:
        digits = "".join(ch for ch in str(cik or "") if ch.isdigit())
        if digits:
            normalized.append(digits.zfill(10)[-10:])
    normalized = list(dict.fromkeys(normalized))
    if not normalized:
        return _empty_frame(
            [
                "cik",
                "manager_name",
                "latest_accession_number",
                "latest_report_period",
                "latest_filing_date",
                "filing_count",
                "source_ref",
            ]
        )
    placeholders = ", ".join(["%s"] * len(normalized))
    db = _connect(host, user, password, port)
    try:
        rows = db.query(
            f"""
            SELECT cik, manager_name, latest_accession_number, latest_report_period,
                   latest_filing_date, filing_count, source_ref
            FROM institutional_13f_manager
            WHERE cik IN ({placeholders})
            """,
            tuple(normalized),
        )
    finally:
        db.close()
    return _frame(rows)


def load_institutional_13f_refresh_status(
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, Any] | None:
    """Load the latest SEC 13F refresh status row for the product surface."""
    db = _connect(host, user, password, port)
    try:
        rows = db.query(
            """
            SELECT source_key, source_dataset, source_ref, status, last_collected_at,
                   latest_report_period, latest_filing_date, managers_written, filings_written,
                   holdings_written, rows_written, is_stale, stale_reason, error_message,
                   source_limitations_json, updated_at
            FROM institutional_13f_refresh_status
            WHERE source_key = 'sec_form_13f_dataset'
            LIMIT 1
            """
        )
    finally:
        db.close()
    return rows[0] if rows else None


def load_institutional_13f_latest_filing(
    cik: str,
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, Any] | None:
    db = _connect(host, user, password, port)
    try:
        rows = db.query(
            """
            SELECT *
            FROM institutional_13f_filing
            WHERE cik = %s
            ORDER BY period_of_report DESC, filing_date DESC, accession_number DESC
            LIMIT 1
            """,
            (str(cik).zfill(10),),
        )
    finally:
        db.close()
    return rows[0] if rows else None


def load_institutional_13f_previous_filing(
    cik: str,
    period_of_report: str,
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, Any] | None:
    db = _connect(host, user, password, port)
    try:
        rows = db.query(
            """
            SELECT *
            FROM institutional_13f_filing
            WHERE cik = %s AND period_of_report < %s
            ORDER BY period_of_report DESC, filing_date DESC, accession_number DESC
            LIMIT 1
            """,
            (str(cik).zfill(10), period_of_report),
        )
    finally:
        db.close()
    return rows[0] if rows else None


def load_institutional_13f_holdings(
    accession_number: str,
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> pd.DataFrame:
    """Load holdings for one filing with optional symbol/profile enrichment."""
    db = _connect(host, user, password, port)
    try:
        rows = db.query(
            """
            SELECT
              h.accession_number,
              h.infotable_sk,
              h.cik,
              h.manager_name,
              h.report_period,
              h.filing_date,
              h.issuer_name,
              h.title_of_class,
              h.cusip,
              h.figi,
              h.reported_value,
              h.shares_or_principal_amount,
              h.amount_type,
              h.put_call,
              h.investment_discretion,
              COALESCE(h.holding_symbol, m.symbol) AS holding_symbol,
              COALESCE(h.symbol_source, m.source) AS symbol_source,
              COALESCE(h.sector, m.sector) AS sector,
              COALESCE(h.industry, m.industry) AS industry,
              h.source_dataset,
              h.source_ref
            FROM institutional_13f_holding h
            LEFT JOIN institutional_13f_cusip_symbol_map m
              ON h.cusip = m.cusip
            WHERE h.accession_number = %s
            ORDER BY h.reported_value DESC, h.issuer_name ASC
            """,
            (accession_number,),
        )
    finally:
        db.close()
    return _frame(rows)


def load_institutional_13f_portfolio_bundle(
    cik: str,
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, Any]:
    latest = load_institutional_13f_latest_filing(cik, host=host, user=user, password=password, port=port)
    if not latest:
        return {
            "manager": None,
            "latest_filing": None,
            "latest_holdings": pd.DataFrame(),
            "previous_filing": None,
            "previous_holdings": pd.DataFrame(),
        }
    previous = load_institutional_13f_previous_filing(
        cik,
        str(latest["period_of_report"]),
        host=host,
        user=user,
        password=password,
        port=port,
    )
    latest_holdings = load_institutional_13f_holdings(
        str(latest["accession_number"]),
        host=host,
        user=user,
        password=password,
        port=port,
    )
    previous_holdings = (
        load_institutional_13f_holdings(
            str(previous["accession_number"]),
            host=host,
            user=user,
            password=password,
            port=port,
        )
        if previous
        else pd.DataFrame()
    )
    return {
        "manager": {"cik": latest["cik"], "manager_name": latest["manager_name"]},
        "latest_filing": latest,
        "latest_holdings": latest_holdings,
        "previous_filing": previous,
        "previous_holdings": previous_holdings,
    }


def load_institutional_13f_interest(
    query: str,
    *,
    limit: int = 100,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> pd.DataFrame:
    """Find current latest-filing holders by symbol, CUSIP, or issuer text."""
    normalized_symbols = _normalize_symbols(query)
    clean_query = str(query or "").strip()
    if not clean_query:
        return _empty_frame([])

    symbol = normalized_symbols[0] if normalized_symbols else clean_query.upper()
    db = _connect(host, user, password, port)
    try:
        candidate_cusips: list[str] = []
        if len(symbol) == 9 and symbol.isalnum():
            candidate_cusips.append(symbol)
        candidate_cusips.extend(_load_mapped_cusips_for_symbol(db, symbol))
        candidate_cusips = list(dict.fromkeys(candidate_cusips))

        rows = []
        if candidate_cusips:
            rows.extend(_load_interest_rows_by_cusips(db, candidate_cusips, limit=max(int(limit) * 3, int(limit))))
        rows.extend(_load_interest_rows_by_holding_symbol(db, symbol, limit=int(limit)))
        if not rows:
            issuer_cusips = _load_mapped_cusips_for_issuer(db, clean_query)
            if issuer_cusips:
                rows = _load_interest_rows_by_cusips(db, issuer_cusips, limit=max(int(limit) * 3, int(limit)))
            else:
                rows = _load_interest_rows_by_issuer_text(db, clean_query, limit=int(limit))
    finally:
        db.close()

    rows = _dedupe_interest_rows(rows, limit=int(limit))
    frame = _frame(rows)
    if frame.empty:
        return frame
    frame["weight_pct"] = [
        round((float(value or 0.0) / float(total or 1.0)) * 100.0, 4)
        for value, total in zip(frame["reported_value"], frame["total_reported_value"])
    ]
    return frame
