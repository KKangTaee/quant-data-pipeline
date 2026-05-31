from __future__ import annotations

import json
import os
from datetime import date, datetime, timezone
from typing import Any, Callable, Iterable

from .db.mysql import MySQLClient
from .db.schema import NYSE_SCHEMAS, sync_table_schema
from .sec_delisting import DEFAULT_SEC_USER_AGENT, fetch_sec_json

DB_NAME = "finance_meta"
SEC_COMPANY_TICKERS_EXCHANGE_URL = "https://www.sec.gov/files/company_tickers_exchange.json"

JsonFetcher = Callable[[str, str, float], Any]


def _now_utc_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _snapshot_date_text(snapshot_date: str | None = None) -> str:
    return str(snapshot_date or date.today().isoformat())


def _resolve_user_agent(user_agent: str | None = None) -> str:
    return str(user_agent or os.getenv("SEC_USER_AGENT") or DEFAULT_SEC_USER_AGENT).strip()


def _parse_symbol_list(symbols: str | Iterable[str] | None) -> list[str]:
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


def normalize_sec_company_tickers_exchange(payload: Any) -> list[dict[str, Any]]:
    """Normalize SEC company_tickers_exchange.json into row dictionaries."""
    if not isinstance(payload, dict):
        return []
    fields = payload.get("fields") or []
    data = payload.get("data") or []
    if not isinstance(fields, list) or not isinstance(data, list):
        return []

    normalized: list[dict[str, Any]] = []
    for raw_row in data:
        if not isinstance(raw_row, list):
            continue
        row = {str(field): raw_row[idx] if idx < len(raw_row) else None for idx, field in enumerate(fields)}
        symbol = str(row.get("ticker") or "").strip().upper()
        if not symbol:
            continue
        try:
            cik = int(row.get("cik"))
        except (TypeError, ValueError):
            continue
        normalized.append(
            {
                "cik": cik,
                "name": str(row.get("name") or "").strip() or None,
                "ticker": symbol,
                "exchange": str(row.get("exchange") or "").strip() or None,
            }
        )
    return normalized


def _load_symbol_kind_map(db: MySQLClient, symbols: list[str]) -> dict[str, str]:
    if not symbols:
        return {}

    placeholders = ", ".join(["%s"] * len(symbols))
    kind_by_symbol: dict[str, str] = {}
    for table, kind in (("nyse_etf", "etf"), ("nyse_stock", "stock")):
        try:
            rows = db.query(f"SELECT symbol FROM {table} WHERE symbol IN ({placeholders})", tuple(symbols))
        except Exception:
            continue
        for row in rows:
            symbol = str(row.get("symbol") or "").strip().upper()
            if symbol:
                kind_by_symbol[symbol] = kind
    return kind_by_symbol


def build_sec_company_ticker_lifecycle_rows(
    records: Iterable[dict[str, Any]],
    *,
    kind_by_symbol: dict[str, str] | None = None,
    symbols: str | Iterable[str] | None = None,
    collected_at: str | None = None,
    snapshot_date: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Convert SEC current CIK / ticker / exchange associations into partial lifecycle evidence."""
    requested_symbols = set(_parse_symbol_list(symbols))
    kind_lookup = {str(key or "").upper(): value for key, value in dict(kind_by_symbol or {}).items()}
    collected = collected_at or _now_utc_text()
    event_date = _snapshot_date_text(snapshot_date)
    rows: list[dict[str, Any]] = []
    skipped_not_requested = 0
    skipped_missing_symbol = 0
    skipped_missing_cik = 0

    for record in records:
        symbol = str(record.get("ticker") or record.get("symbol") or "").strip().upper()
        if not symbol:
            skipped_missing_symbol += 1
            continue
        if requested_symbols and symbol not in requested_symbols:
            skipped_not_requested += 1
            continue
        try:
            cik = int(record.get("cik"))
        except (TypeError, ValueError):
            skipped_missing_cik += 1
            continue

        exchange = str(record.get("exchange") or "").strip() or None
        name = str(record.get("name") or "").strip() or None
        evidence = {
            "source": "sec_company_tickers_exchange",
            "symbol": symbol,
            "cik": cik,
            "name": name,
            "exchange": exchange,
            "event_type": "listing_observed",
            "event_date": event_date,
            "source_note": "SEC current CIK / ticker / exchange association; not historical membership proof",
        }
        rows.append(
            {
                "symbol": symbol,
                "kind": kind_lookup.get(symbol, "stock"),
                "listing_status": "active",
                "source": "sec_company_tickers_exchange",
                "source_type": "current_listing_snapshot",
                "coverage_status": "partial",
                "first_seen_date": event_date,
                "last_seen_date": event_date,
                "inactive_detected_at": None,
                "event_type": "listing_observed",
                "event_date": event_date,
                "related_symbol": None,
                "related_cik": cik,
                "name": name,
                "source_ref": SEC_COMPANY_TICKERS_EXCHANGE_URL,
                "evidence_json": json.dumps(evidence, ensure_ascii=False, sort_keys=True),
                "collected_at": collected,
                "error_msg": None,
            }
        )

    return rows, {
        "event_date": event_date,
        "rows_built": len(rows),
        "symbols_requested": sorted(requested_symbols),
        "skipped_not_requested": skipped_not_requested,
        "skipped_missing_symbol": skipped_missing_symbol,
        "skipped_missing_cik": skipped_missing_cik,
    }


def _upsert_lifecycle_rows(db: MySQLClient, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0

    sync_table_schema(db, "nyse_symbol_lifecycle", NYSE_SCHEMAS["symbol_lifecycle"], DB_NAME)
    sql = """
        INSERT INTO nyse_symbol_lifecycle (
            symbol, kind, listing_status, source, source_type, coverage_status,
            first_seen_date, last_seen_date, inactive_detected_at,
            event_type, event_date, related_symbol, related_cik,
            name, source_ref, evidence_json, collected_at, error_msg
        )
        VALUES (
            %(symbol)s, %(kind)s, %(listing_status)s, %(source)s, %(source_type)s, %(coverage_status)s,
            %(first_seen_date)s, %(last_seen_date)s, %(inactive_detected_at)s,
            %(event_type)s, %(event_date)s, %(related_symbol)s, %(related_cik)s,
            %(name)s, %(source_ref)s, %(evidence_json)s, %(collected_at)s, %(error_msg)s
        )
        ON DUPLICATE KEY UPDATE
            listing_status = VALUES(listing_status),
            source_type = VALUES(source_type),
            coverage_status = VALUES(coverage_status),
            first_seen_date = CASE
                WHEN first_seen_date IS NULL OR VALUES(first_seen_date) < first_seen_date
                    THEN VALUES(first_seen_date)
                ELSE first_seen_date
            END,
            last_seen_date = CASE
                WHEN last_seen_date IS NULL OR VALUES(last_seen_date) > last_seen_date
                    THEN VALUES(last_seen_date)
                ELSE last_seen_date
            END,
            inactive_detected_at = NULL,
            event_type = VALUES(event_type),
            event_date = VALUES(event_date),
            related_symbol = VALUES(related_symbol),
            related_cik = VALUES(related_cik),
            name = VALUES(name),
            source_ref = VALUES(source_ref),
            evidence_json = VALUES(evidence_json),
            collected_at = VALUES(collected_at),
            error_msg = NULL
    """
    db.executemany(sql, rows)
    return len(rows)


def collect_and_store_sec_company_ticker_crosscheck(
    symbols: str | Iterable[str] | None = None,
    *,
    user_agent: str | None = None,
    request_timeout: float = 30.0,
    snapshot_date: str | None = None,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
    fetch_json: JsonFetcher | None = None,
) -> dict[str, Any]:
    """Collect SEC current CIK / ticker / exchange associations into lifecycle evidence rows."""
    effective_user_agent = _resolve_user_agent(user_agent)
    fetcher = fetch_json or fetch_sec_json
    records = normalize_sec_company_tickers_exchange(
        fetcher(SEC_COMPANY_TICKERS_EXCHANGE_URL, effective_user_agent, request_timeout)
    )
    requested_symbols = _parse_symbol_list(symbols)
    source_symbols = [str(record.get("ticker") or "").upper() for record in records if record.get("ticker")]
    target_symbols = requested_symbols or source_symbols

    db = MySQLClient(host, user, password, port)
    try:
        db.use_db(DB_NAME)
        kind_by_symbol = _load_symbol_kind_map(db, target_symbols)
        rows, metadata = build_sec_company_ticker_lifecycle_rows(
            records,
            kind_by_symbol=kind_by_symbol,
            symbols=requested_symbols,
            snapshot_date=snapshot_date,
        )
        rows_written = _upsert_lifecycle_rows(db, rows)
    finally:
        db.close()

    found_symbols = {row["symbol"] for row in rows}
    requested_missing = sorted(set(requested_symbols) - found_symbols) if requested_symbols else []
    return {
        "source": "sec_company_tickers_exchange",
        "target_table": "finance_meta.nyse_symbol_lifecycle",
        "requested": len(requested_symbols) if requested_symbols else len(source_symbols),
        "records_found": len(records),
        "rows_found": len(rows),
        "rows_written": rows_written,
        "requested_missing_symbols": requested_missing,
        "metadata": metadata,
        "execution_boundary": {
            "db_write": True,
            "registry_write": False,
            "memo_persistence": False,
            "preset_persistence": False,
            "report_file_write": False,
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
        },
        "source_limitations": [
            "SEC company_tickers_exchange is a current CIK / ticker / exchange association file.",
            "The association is useful identity evidence, not historical membership proof.",
            "Rows are stored as partial listing_observed evidence and must not loosen survivorship PASS criteria.",
        ],
    }
