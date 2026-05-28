from __future__ import annotations

import json
from collections import Counter
from collections.abc import Iterable
from datetime import date, datetime, timezone
from typing import Any

from .db.mysql import MySQLClient
from .db.schema import NYSE_SCHEMAS, sync_table_schema

DB_NAME = "finance_meta"
COMPUTED_SNAPSHOT_SOURCE = "computed_snapshot_lifecycle"


def _now_utc_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


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


def _date_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text[:10]).date().isoformat()
    except ValueError:
        return None


def _current_snapshot_row(row: dict[str, Any]) -> bool:
    source_type = str(row.get("source_type") or "").strip().lower()
    if source_type != "current_listing_snapshot":
        return False
    listing_status = str(row.get("listing_status") or "").strip().lower()
    if listing_status not in {"active", "unknown", ""}:
        return False
    coverage_status = str(row.get("coverage_status") or "").strip().lower()
    if coverage_status in {"missing", "error"}:
        return False
    event_type = str(row.get("event_type") or "").strip().lower()
    return event_type in {"", "unknown", "listing_observed"}


def _observation_dates(row: dict[str, Any]) -> list[str]:
    dates = {
        _date_text(row.get("first_seen_date")),
        _date_text(row.get("last_seen_date")),
        _date_text(row.get("event_date")),
    }
    return sorted(date_value for date_value in dates if date_value)


def _latest_non_empty(rows: list[dict[str, Any]], key: str) -> Any:
    rows_by_date = sorted(
        rows,
        key=lambda item: _date_text(item.get("last_seen_date")) or _date_text(item.get("event_date")) or "",
        reverse=True,
    )
    for row in rows_by_date:
        value = row.get(key)
        if value is not None and str(value).strip():
            return value
    return None


def build_computed_snapshot_lifecycle_rows(
    lifecycle_rows: Iterable[dict[str, Any]],
    *,
    collected_at: str | None = None,
    min_observation_dates: int = 2,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Summarize repeated current snapshots without treating absence as delisting proof."""
    input_rows = [dict(row or {}) for row in lifecycle_rows if isinstance(row, dict)]
    current_rows = [row for row in input_rows if _current_snapshot_row(row)]
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    skipped_missing_symbol = 0
    skipped_missing_kind = 0

    for row in current_rows:
        symbol = str(row.get("symbol") or "").strip().upper()
        kind = str(row.get("kind") or "").strip().lower()
        if not symbol:
            skipped_missing_symbol += 1
            continue
        if kind not in {"stock", "etf"}:
            skipped_missing_kind += 1
            continue
        grouped.setdefault((symbol, kind), []).append(row)

    collected = collected_at or _now_utc_text()
    rows: list[dict[str, Any]] = []
    skipped_insufficient_observation_dates = 0

    for (symbol, kind), symbol_rows in sorted(grouped.items()):
        observation_dates = sorted({date_value for row in symbol_rows for date_value in _observation_dates(row)})
        if len(observation_dates) < int(min_observation_dates) or observation_dates[0] == observation_dates[-1]:
            skipped_insufficient_observation_dates += 1
            continue

        sources = sorted({str(row.get("source") or "").strip() for row in symbol_rows if row.get("source")})
        source_type_counts = Counter(str(row.get("source_type") or "unknown").strip() or "unknown" for row in symbol_rows)
        evidence = {
            "source": COMPUTED_SNAPSHOT_SOURCE,
            "policy": "computed_from_repeated_current_snapshots",
            "symbol": symbol,
            "kind": kind,
            "snapshot_sources": sources,
            "source_count": len(sources),
            "observation_date_count": len(observation_dates),
            "first_observed_date": observation_dates[0],
            "last_observed_date": observation_dates[-1],
            "source_type_counts": dict(sorted(source_type_counts.items())),
            "coverage_status": "partial",
            "pass_eligible": False,
            "pass_condition": "Data Coverage Audit requires coverage_status=actual before computed snapshot evidence can PASS.",
            "source_note": (
                "Repeated current snapshots summarize observed active presence; absence from current snapshots is not delisting proof."
            ),
        }
        rows.append(
            {
                "symbol": symbol,
                "kind": kind,
                "listing_status": "active",
                "source": COMPUTED_SNAPSHOT_SOURCE,
                "source_type": "computed_from_snapshots",
                "coverage_status": "partial",
                "first_seen_date": observation_dates[0],
                "last_seen_date": observation_dates[-1],
                "inactive_detected_at": None,
                "event_type": "historical_membership",
                "event_date": observation_dates[-1],
                "related_symbol": None,
                "related_cik": _latest_non_empty(symbol_rows, "related_cik"),
                "name": _latest_non_empty(symbol_rows, "name"),
                "source_ref": None,
                "evidence_json": json.dumps(evidence, ensure_ascii=False, sort_keys=True),
                "collected_at": collected,
                "error_msg": None,
            }
        )

    return rows, {
        "source": COMPUTED_SNAPSHOT_SOURCE,
        "input_rows": len(input_rows),
        "current_snapshot_rows": len(current_rows),
        "groups_seen": len(grouped),
        "rows_built": len(rows),
        "min_observation_dates": int(min_observation_dates),
        "skipped_missing_symbol": skipped_missing_symbol,
        "skipped_missing_kind": skipped_missing_kind,
        "skipped_insufficient_observation_dates": skipped_insufficient_observation_dates,
    }


def _load_current_snapshot_rows(db: MySQLClient, symbols: list[str]) -> list[dict[str, Any]]:
    sync_table_schema(db, "nyse_symbol_lifecycle", NYSE_SCHEMAS["symbol_lifecycle"], DB_NAME)
    params: list[Any] = ["current_listing_snapshot"]
    symbol_filter = ""
    if symbols:
        placeholders = ", ".join(["%s"] * len(symbols))
        symbol_filter = f" AND symbol IN ({placeholders})"
        params.extend(symbols)

    return db.query(
        f"""
        SELECT
            symbol,
            kind,
            listing_status,
            source,
            source_type,
            coverage_status,
            first_seen_date,
            last_seen_date,
            inactive_detected_at,
            event_type,
            event_date,
            related_symbol,
            related_cik,
            name,
            source_ref,
            collected_at,
            error_msg
        FROM nyse_symbol_lifecycle
        WHERE source_type = %s{symbol_filter}
        ORDER BY symbol ASC, kind ASC, source ASC
        """,
        tuple(params),
    )


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
            first_seen_date = VALUES(first_seen_date),
            last_seen_date = VALUES(last_seen_date),
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


def collect_and_store_computed_snapshot_lifecycle(
    symbols: str | Iterable[str] | None = None,
    *,
    min_observation_dates: int = 2,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, Any]:
    """Build conservative computed lifecycle rows from existing current snapshot evidence."""
    parsed_symbols = _parse_symbol_list(symbols)
    db = MySQLClient(host, user, password, port)
    try:
        db.use_db(DB_NAME)
        source_rows = _load_current_snapshot_rows(db, parsed_symbols)
        rows, metadata = build_computed_snapshot_lifecycle_rows(
            source_rows,
            min_observation_dates=int(min_observation_dates),
        )
        rows_written = _upsert_lifecycle_rows(db, rows)
    finally:
        db.close()

    computed_symbols = sorted({row["symbol"] for row in rows})
    requested_missing_symbols = sorted(set(parsed_symbols) - set(computed_symbols)) if parsed_symbols else []
    return {
        "source": COMPUTED_SNAPSHOT_SOURCE,
        "target_table": "finance_meta.nyse_symbol_lifecycle",
        "requested": len(parsed_symbols) if parsed_symbols else int(metadata.get("groups_seen") or 0),
        "source_rows": len(source_rows),
        "rows_found": len(rows),
        "rows_written": rows_written,
        "computed_symbols": computed_symbols,
        "requested_missing_symbols": requested_missing_symbols,
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
            "Computed rows summarize repeated current snapshot observations only.",
            "Absence from a snapshot is not delisting proof.",
            "Rows are stored as partial evidence and must not loosen survivorship PASS criteria.",
        ],
    }
