from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any

import pandas as pd

from finance.data.db.mysql import MySQLClient


DB_META = "finance_meta"


_IDENTITY_SYMBOL_SQL = """
CASE
  WHEN ir.resolution_status = 'ambiguous' THEN NULL
  WHEN ir.resolution_status = 'mapped' THEN ir.symbol
  WHEN lm.symbol_count > 1 THEN NULL
  ELSE COALESCE(h.holding_symbol, lm.symbol)
END
""".strip()

_IDENTITY_SOURCE_SQL = """
CASE
  WHEN ir.resolution_status = 'ambiguous' THEN 'openfigi_v3_ambiguous'
  WHEN ir.resolution_status = 'mapped' THEN 'openfigi_v3'
  WHEN lm.symbol_count > 1 THEN 'legacy_mapping_ambiguous'
  ELSE COALESCE(h.symbol_source, lm.source)
END
""".strip()

_IDENTITY_STATUS_SQL = """
CASE
  WHEN ir.resolution_status = 'ambiguous' THEN 'ambiguous'
  WHEN ir.resolution_status = 'mapped' AND ir.symbol IS NOT NULL THEN 'mapped'
  WHEN lm.symbol_count > 1 THEN 'ambiguous'
  WHEN COALESCE(h.holding_symbol, lm.symbol) IS NOT NULL THEN 'mapped'
  ELSE 'unmapped'
END
""".strip()

_IDENTITY_JOIN_SQL = f"""
LEFT JOIN institutional_13f_identifier_resolution ir
  ON h.cusip = ir.identifier_value
 AND ir.source = 'openfigi_v3'
LEFT JOIN (
  SELECT
    cusip,
    UPPER(issuer_name) AS issuer_key,
    COUNT(DISTINCT symbol) AS symbol_count,
    CASE WHEN COUNT(DISTINCT symbol) = 1 THEN MAX(symbol) END AS symbol,
    CASE
      WHEN COUNT(DISTINCT symbol) = 1 THEN MAX(source)
      ELSE 'legacy_mapping_ambiguous'
    END AS source,
    CASE WHEN COUNT(DISTINCT symbol) = 1 THEN MAX(sector) END AS sector,
    CASE WHEN COUNT(DISTINCT symbol) = 1 THEN MAX(industry) END AS industry
  FROM institutional_13f_cusip_symbol_map
  GROUP BY cusip, UPPER(issuer_name)
) lm
  ON h.cusip = lm.cusip
 AND lm.issuer_key = UPPER(h.issuer_name)
LEFT JOIN nyse_asset_profile ap
  ON ap.symbol = {_IDENTITY_SYMBOL_SQL}
"""

_IDENTITY_SELECT_SQL = f"""
{_IDENTITY_SYMBOL_SQL} AS holding_symbol,
{_IDENTITY_SOURCE_SQL} AS symbol_source,
{_IDENTITY_STATUS_SQL} AS mapping_status,
COALESCE(h.figi, ir.figi) AS figi,
COALESCE(h.sector, ap.sector, lm.sector) AS sector,
COALESCE(h.industry, ap.industry, lm.industry) AS industry
"""


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


def resolve_effective_13f_quarter(
    filings: Iterable[dict[str, Any]],
    holdings_by_accession: dict[str, pd.DataFrame],
) -> dict[str, Any]:
    """Compose base, restatement, and additive amendments into one effective quarter."""

    ordered = sorted(
        (dict(row) for row in filings),
        key=lambda row: (
            str(row.get("filing_date") or ""),
            str(row.get("accession_number") or ""),
        ),
    )
    effective = pd.DataFrame()
    source_accessions: list[str] = []
    effective_filing: dict[str, Any] | None = None
    warnings: list[str] = []

    for filing in ordered:
        accession = str(filing.get("accession_number") or "").strip()
        if not accession:
            continue
        holdings = holdings_by_accession.get(accession)
        holdings = holdings.copy() if isinstance(holdings, pd.DataFrame) else pd.DataFrame()
        submission_type = str(filing.get("submission_type") or "").strip().upper()
        is_amendment = bool(filing.get("is_amendment")) or submission_type.endswith("/A")
        amendment_type = str(filing.get("amendment_type") or "").strip().upper()

        if submission_type == "13F-NT":
            warnings.append(f"Notice-only filing {accession} does not define owned holdings.")
            continue
        if not is_amendment:
            if holdings.empty:
                warnings.append(f"Base filing {accession} has no usable information table.")
                continue
            effective = holdings
            source_accessions = [accession]
            effective_filing = filing
            continue
        if "RESTATEMENT" in amendment_type:
            if effective_filing is None or holdings.empty:
                warnings.append(f"Restatement {accession} has no usable base or information table.")
                continue
            effective = holdings
            source_accessions = [accession]
            effective_filing = filing
            continue
        if "NEW HOLDINGS" in amendment_type:
            if effective_filing is None:
                warnings.append(f"Additive amendment {accession} has no accepted base filing.")
                continue
            if holdings.empty:
                warnings.append(f"Additive amendment {accession} has no usable information table.")
                continue
            effective = pd.concat([effective, holdings], ignore_index=True, sort=False)
            source_accessions.append(accession)
            effective_filing = filing
            continue

        warnings.append(f"Unknown amendment type for {accession}; kept the last unambiguous filing.")

    return {
        "available": effective_filing is not None and not effective.empty,
        "filing": effective_filing,
        "holdings": effective.reset_index(drop=True),
        "source_accessions": source_accessions,
        "warning": " ".join(warnings),
    }


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
        SELECT cusip
        FROM (
          SELECT identifier_value AS cusip, 0 AS source_order
          FROM institutional_13f_identifier_resolution
          WHERE source = 'openfigi_v3'
            AND resolution_status = 'mapped'
            AND symbol = %s
          UNION ALL
          SELECT cusip, 1 AS source_order
          FROM institutional_13f_cusip_symbol_map
          WHERE symbol = %s
        ) candidates
        ORDER BY source_order ASC, cusip ASC
        LIMIT %s
        """,
        (symbol, symbol, max(int(limit) * 4, int(limit))),
    )
    return list(dict.fromkeys(str(row["cusip"]) for row in rows if row.get("cusip")))[: int(limit)]


def _load_mapped_cusips_for_issuer(db: MySQLClient, query: str, *, limit: int = 25) -> list[str]:
    like_query = f"%{query.upper()}%"
    rows = db.query(
        """
        SELECT cusip
        FROM (
          SELECT identifier_value AS cusip, 0 AS source_order
          FROM institutional_13f_identifier_resolution
          WHERE source = 'openfigi_v3'
            AND resolution_status = 'mapped'
            AND UPPER(provider_name) LIKE %s
          UNION ALL
          SELECT cusip, 1 AS source_order
          FROM institutional_13f_cusip_symbol_map
          WHERE UPPER(issuer_name) LIKE %s
        ) candidates
        ORDER BY source_order ASC, cusip ASC
        LIMIT %s
        """,
        (like_query, like_query, max(int(limit) * 4, int(limit))),
    )
    return list(dict.fromkeys(str(row["cusip"]) for row in rows if row.get("cusip")))[: int(limit)]


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
          {_IDENTITY_SELECT_SQL},
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
        {_IDENTITY_JOIN_SQL}
        WHERE h.cusip IN ({placeholders})
        ORDER BY h.reported_value DESC, m.manager_name ASC
        LIMIT %s
        """,
        tuple([*cusips, int(limit)]),
    )


def _load_interest_rows_by_holding_symbol(db: MySQLClient, symbol: str, *, limit: int) -> list[dict[str, Any]]:
    return db.query(
        f"""
        SELECT
          m.manager_name,
          m.cik,
          f.period_of_report,
          f.filing_date,
          h.cusip,
          {_IDENTITY_SELECT_SQL},
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
        {_IDENTITY_JOIN_SQL}
        WHERE ({_IDENTITY_SYMBOL_SQL}) = %s
        ORDER BY h.reported_value DESC, m.manager_name ASC
        LIMIT %s
        """,
        (symbol, int(limit)),
    )


def _load_interest_rows_by_issuer_text(db: MySQLClient, clean_query: str, *, limit: int) -> list[dict[str, Any]]:
    like_query = f"%{clean_query.upper()}%"
    return db.query(
        f"""
        SELECT
          m.manager_name,
          m.cik,
          f.period_of_report,
          f.filing_date,
          h.cusip,
          {_IDENTITY_SELECT_SQL},
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
        {_IDENTITY_JOIN_SQL}
        WHERE UPPER(h.issuer_name) LIKE %s
           OR UPPER(ir.provider_name) LIKE %s
           OR lm.issuer_key LIKE %s
        ORDER BY h.reported_value DESC, m.manager_name ASC
        LIMIT %s
        """,
        (like_query, like_query, like_query, int(limit)),
    )


def _latest_report_period(db: MySQLClient) -> str | None:
    rows = db.query(
        """
        SELECT MAX(report_period) AS report_period
        FROM institutional_13f_holding
        """
    )
    if not rows:
        return None
    value = rows[0].get("report_period")
    return str(value) if value else None


def _load_popularity_rows(db: MySQLClient, report_period: str, *, limit: int, force_index: bool) -> list[dict[str, Any]]:
    index_clause = " FORCE INDEX(ix_report_period_cusip_cik)" if force_index else ""
    return db.query(
        f"""
        SELECT
          h.report_period,
          h.cusip,
          SUBSTRING_INDEX(
            GROUP_CONCAT(NULLIF(({_IDENTITY_SYMBOL_SQL}), '') ORDER BY h.reported_value DESC SEPARATOR '||'),
            '||',
            1
          ) AS holding_symbol,
          SUBSTRING_INDEX(
            GROUP_CONCAT(NULLIF(h.issuer_name, '') ORDER BY h.reported_value DESC SEPARATOR '||'),
            '||',
            1
          ) AS issuer_name,
          COUNT(DISTINCT h.cik) AS holder_count,
          COUNT(*) AS holding_rows,
          SUM(COALESCE(h.reported_value, 0)) AS total_reported_value,
          SUBSTRING_INDEX(
            GROUP_CONCAT(DISTINCT h.manager_name ORDER BY h.manager_name ASC SEPARATOR ', '),
            ', ',
            5
          ) AS sample_managers
        FROM institutional_13f_holding h{index_clause}
        {_IDENTITY_JOIN_SQL}
        WHERE h.report_period = %s
          AND (h.put_call IS NULL OR h.put_call = '')
        GROUP BY h.report_period, h.cusip
        ORDER BY holder_count DESC, total_reported_value DESC, issuer_name ASC
        LIMIT %s
        """,
        (report_period, int(limit)),
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


def load_institutional_13f_latest_submission_periods_by_ciks(
    ciks: Iterable[str],
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, str]:
    """Return latest submitted periods, including notice-only 13F filings."""

    normalized: list[str] = []
    for cik in ciks:
        digits = "".join(ch for ch in str(cik or "") if ch.isdigit())
        if digits:
            normalized.append(digits.zfill(10)[-10:])
    normalized = list(dict.fromkeys(normalized))
    if not normalized:
        return {}

    placeholders = ", ".join(["%s"] * len(normalized))
    db = _connect(host, user, password, port)
    try:
        rows = db.query(
            f"""
            SELECT cik, MAX(period_of_report) AS latest_report_period
            FROM institutional_13f_filing
            WHERE cik IN ({placeholders})
            GROUP BY cik
            """,
            tuple(normalized),
        )
    finally:
        db.close()
    return {
        str(row.get("cik") or "").zfill(10)[-10:]: str(row.get("latest_report_period"))
        for row in rows
        if row.get("cik") and row.get("latest_report_period")
    }


def load_institutional_13f_manager_watchlist(
    *,
    active_only: bool = True,
    limit: int = 200,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> pd.DataFrame:
    """Load curated manager watchlist metadata from finance_meta without fetching external data."""
    db = _connect(host, user, password, port)
    try:
        where = "WHERE active = 1" if active_only else ""
        rows = db.query(
            f"""
            SELECT cik, display_name, watchlist_label, alias, priority,
                   tags_json, external_links_json, source, notes
            FROM institutional_13f_manager_watchlist
            {where}
            ORDER BY priority ASC, display_name ASC
            LIMIT %s
            """,
            (int(limit),),
        )
    finally:
        db.close()

    for row in rows:
        for field in ("tags_json", "external_links_json"):
            value = row.get(field)
            if isinstance(value, str) and value.strip():
                try:
                    row[field] = json.loads(value)
                except json.JSONDecodeError:
                    row[field] = None
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
            f"""
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
              {_IDENTITY_SELECT_SQL},
              h.reported_value,
              h.shares_or_principal_amount,
              h.amount_type,
              h.put_call,
              h.investment_discretion,
              h.source_dataset,
              h.source_ref
            FROM institutional_13f_holding h
            {_IDENTITY_JOIN_SQL}
            WHERE h.accession_number = %s
            ORDER BY h.reported_value DESC, h.issuer_name ASC
            """,
            (accession_number,),
        )
    finally:
        db.close()
    return _frame(rows)


def _load_effective_history_from_db(
    db: MySQLClient,
    cik: str,
    *,
    limit: int,
    report_period: str | None = None,
) -> list[dict[str, Any]]:
    normalized_cik = str(cik).zfill(10)
    manager_rows = db.query(
        """
        SELECT cik, manager_name
        FROM institutional_13f_manager
        WHERE cik = %s
        LIMIT 1
        """,
        (normalized_cik,),
    )
    period_where = "AND period_of_report = %s" if report_period else ""
    period_params: tuple[Any, ...] = (
        (normalized_cik, report_period, int(limit))
        if report_period
        else (normalized_cik, int(limit))
    )
    period_rows = db.query(
        f"""
        SELECT DISTINCT period_of_report
        FROM institutional_13f_filing
        WHERE cik = %s
          {period_where}
        ORDER BY period_of_report DESC
        LIMIT %s
        """,
        period_params,
    )
    periods = [str(row.get("period_of_report")) for row in period_rows if row.get("period_of_report")]
    if not periods:
        return []

    period_placeholders = ", ".join(["%s"] * len(periods))
    filings = db.query(
        f"""
        SELECT *
        FROM institutional_13f_filing
        WHERE cik = %s AND period_of_report IN ({period_placeholders})
        ORDER BY period_of_report DESC, filing_date ASC, accession_number ASC
        """,
        tuple([normalized_cik, *periods]),
    )
    accessions = [str(row.get("accession_number")) for row in filings if row.get("accession_number")]
    holdings_by_accession: dict[str, pd.DataFrame] = {accession: pd.DataFrame() for accession in accessions}
    if accessions:
        accession_placeholders = ", ".join(["%s"] * len(accessions))
        holding_rows = db.query(
            f"""
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
              {_IDENTITY_SELECT_SQL},
              h.reported_value,
              h.shares_or_principal_amount,
              h.amount_type,
              h.put_call,
              h.investment_discretion,
              h.source_dataset,
              h.source_ref
            FROM institutional_13f_holding h
            {_IDENTITY_JOIN_SQL}
            WHERE h.accession_number IN ({accession_placeholders})
            ORDER BY h.accession_number, h.infotable_sk
            """,
            tuple(accessions),
        )
        holding_frame = _frame(holding_rows)
        if not holding_frame.empty:
            holdings_by_accession.update(
                {
                    str(accession): group.reset_index(drop=True)
                    for accession, group in holding_frame.groupby("accession_number", dropna=False)
                }
            )

    manager = dict(manager_rows[0]) if manager_rows else None
    history: list[dict[str, Any]] = []
    for period in periods:
        period_filings = [row for row in filings if str(row.get("period_of_report")) == period]
        resolved = resolve_effective_13f_quarter(period_filings, holdings_by_accession)
        resolved["manager"] = manager or (
            {
                "cik": normalized_cik,
                "manager_name": period_filings[0].get("manager_name"),
            }
            if period_filings
            else None
        )
        history.append(resolved)
    return history


def load_institutional_13f_effective_quarter(
    cik: str,
    report_period: str | None = None,
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, Any]:
    """Load one amendment-aware effective quarter without external fetches or writes."""

    db = _connect(host, user, password, port)
    try:
        history = _load_effective_history_from_db(
            db,
            cik,
            limit=1,
            report_period=report_period,
        )
    finally:
        db.close()
    if history:
        return history[0]
    return {
        "available": False,
        "manager": None,
        "filing": None,
        "holdings": pd.DataFrame(),
        "source_accessions": [],
        "warning": "No stored 13F filing is available for the requested quarter.",
    }


def load_institutional_13f_effective_history(
    cik: str,
    *,
    limit: int = 8,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> list[dict[str, Any]]:
    """Load amendment-aware effective quarters through one DB connection."""

    db = _connect(host, user, password, port)
    try:
        return _load_effective_history_from_db(db, cik, limit=max(1, int(limit)))
    finally:
        db.close()


def load_institutional_13f_portfolio_bundle(
    cik: str,
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, Any]:
    history = load_institutional_13f_effective_history(
        cik,
        limit=8,
        host=host,
        user=user,
        password=password,
        port=port,
    )
    available = [row for row in history if row.get("available")]
    latest_effective = available[0] if available else None
    previous_effective = available[1] if len(available) > 1 else None
    return {
        "manager": latest_effective.get("manager") if latest_effective else None,
        "latest_filing": latest_effective.get("filing") if latest_effective else None,
        "latest_holdings": latest_effective.get("holdings", pd.DataFrame()) if latest_effective else pd.DataFrame(),
        "previous_filing": previous_effective.get("filing") if previous_effective else None,
        "previous_holdings": (
            previous_effective.get("holdings", pd.DataFrame()) if previous_effective else pd.DataFrame()
        ),
        "latest_effective": latest_effective,
        "previous_effective": previous_effective,
    }


def load_institutional_13f_popularity_ranking(
    report_period: str | None = None,
    *,
    limit: int = 50,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> pd.DataFrame:
    """Rank securities by distinct 13F managers holding them for one report period."""
    db = _connect(host, user, password, port)
    columns = [
        "report_period",
        "cusip",
        "holding_symbol",
        "issuer_name",
        "holder_count",
        "holding_rows",
        "total_reported_value",
        "sample_managers",
    ]
    try:
        period = str(report_period or "").strip() or _latest_report_period(db)
        if not period:
            return _empty_frame(columns)
        try:
            rows = _load_popularity_rows(db, period, limit=limit, force_index=True)
        except Exception as exc:
            if "ix_report_period_cusip_cik" not in str(exc):
                raise
            rows = _load_popularity_rows(db, period, limit=limit, force_index=False)
    finally:
        db.close()

    frame = _frame(rows)
    if frame.empty:
        return _empty_frame(columns)
    for column in columns:
        if column not in frame.columns:
            frame[column] = None
    return frame[columns]


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
        rows = []
        if len(symbol) == 9 and symbol.isalnum():
            candidate_cusips = [symbol]
            rows.extend(_load_interest_rows_by_cusips(db, candidate_cusips, limit=max(int(limit) * 3, int(limit))))
        else:
            rows.extend(_load_interest_rows_by_holding_symbol(db, symbol, limit=int(limit)))
            if not rows:
                candidate_cusips = _load_mapped_cusips_for_symbol(db, symbol)
                if candidate_cusips:
                    rows.extend(_load_interest_rows_by_cusips(db, candidate_cusips, limit=max(int(limit) * 3, int(limit))))
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
