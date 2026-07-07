from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from datetime import datetime
from typing import Any

from finance.data.db.mysql import MySQLClient
from finance.data.db.schema import NYSE_SCHEMAS, sync_table_schema


def _normalize_symbol(value: Any) -> str:
    return str(value or "").strip().upper()


def _safe_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _json_payload(value: Any) -> str:
    if value in (None, ""):
        return "{}"
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, default=str)


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _ticker_change_row(candidate: Mapping[str, Any], *, status: str, collected_at: str) -> dict[str, Any] | None:
    source_symbol = _normalize_symbol(candidate.get("source_symbol") or candidate.get("symbol"))
    resolved_symbol = _normalize_symbol(candidate.get("resolved_symbol") or candidate.get("related_symbol"))
    if not source_symbol or not resolved_symbol or source_symbol == resolved_symbol:
        return None
    normalized_status = str(candidate.get("resolution_status") or status or "active").strip().lower()
    if normalized_status not in {"candidate", "active", "rejected", "unknown"}:
        normalized_status = "unknown"
    evidence = dict(candidate.get("evidence") or {})
    if candidate.get("evidence_summary") and "summary" not in evidence:
        evidence["summary"] = candidate.get("evidence_summary")
    evidence["status"] = normalized_status
    return {
        "symbol": source_symbol,
        "kind": str(candidate.get("kind") or "stock").strip().lower() or "stock",
        "listing_status": "unknown",
        "source": str(candidate.get("source") or "backtest_symbol_resolver_manual").strip(),
        "source_type": str(candidate.get("source_type") or "historical_listing").strip(),
        "coverage_status": str(candidate.get("coverage_status") or "actual").strip(),
        "event_type": "ticker_change",
        "event_date": candidate.get("effective_date") or candidate.get("event_date"),
        "related_symbol": resolved_symbol,
        "related_cik": candidate.get("related_cik"),
        "resolution_status": normalized_status,
        "confidence": _safe_float(candidate.get("confidence")),
        "name": candidate.get("name"),
        "source_ref": candidate.get("source_ref"),
        "evidence_json": _json_payload(evidence or candidate.get("evidence_json")),
        "collected_at": collected_at,
        "error_msg": None,
    }


def upsert_ticker_change_resolutions(
    candidates: Iterable[Mapping[str, Any]],
    *,
    status: str = "active",
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> int:
    """Persist user-reviewed ticker-change repair rows in nyse_symbol_lifecycle."""
    collected_at = _timestamp()
    rows = [
        row
        for candidate in candidates
        if (row := _ticker_change_row(candidate, status=status, collected_at=collected_at))
    ]
    db = MySQLClient(host, user, password, port)
    try:
        db.use_db("finance_meta")
        sync_table_schema(db, "nyse_symbol_lifecycle", NYSE_SCHEMAS["symbol_lifecycle"], "finance_meta")
        if not rows:
            return 0
        sql = """
        INSERT INTO nyse_symbol_lifecycle (
            symbol, kind, listing_status, source, source_type, coverage_status,
            event_type, event_date, related_symbol, related_cik, resolution_status,
            confidence, name, source_ref, evidence_json, collected_at, error_msg
        ) VALUES (
            %(symbol)s, %(kind)s, %(listing_status)s, %(source)s, %(source_type)s, %(coverage_status)s,
            %(event_type)s, %(event_date)s, %(related_symbol)s, %(related_cik)s, %(resolution_status)s,
            %(confidence)s, %(name)s, %(source_ref)s, %(evidence_json)s, %(collected_at)s, %(error_msg)s
        )
        ON DUPLICATE KEY UPDATE
            listing_status = VALUES(listing_status),
            source_type = VALUES(source_type),
            coverage_status = VALUES(coverage_status),
            event_type = VALUES(event_type),
            event_date = VALUES(event_date),
            related_symbol = VALUES(related_symbol),
            related_cik = VALUES(related_cik),
            resolution_status = VALUES(resolution_status),
            confidence = VALUES(confidence),
            name = VALUES(name),
            source_ref = VALUES(source_ref),
            evidence_json = VALUES(evidence_json),
            collected_at = VALUES(collected_at),
            error_msg = VALUES(error_msg)
        """
        db.executemany(sql, rows)
        return len(rows)
    finally:
        db.close()
