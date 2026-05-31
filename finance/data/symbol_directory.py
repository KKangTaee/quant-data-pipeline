from __future__ import annotations

import csv
import gzip
import json
import os
import re
import zlib
from dataclasses import dataclass
from datetime import date, datetime, timezone
from io import StringIO
from typing import Any, Callable, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .db.mysql import MySQLClient
from .db.schema import NYSE_SCHEMAS, sync_table_schema

DB_NAME = "finance_meta"
DEFAULT_NASDAQ_USER_AGENT = "quant-data-pipeline local-research@example.com"
NASDAQ_LISTED_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
NASDAQ_OTHER_LISTED_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"

TextFetcher = Callable[[str, str, float], str]


@dataclass(frozen=True)
class SymbolDirectorySource:
    key: str
    url: str
    source: str
    symbol_field: str
    name_field: str
    exchange: str | None = None
    exchange_field: str | None = None


SYMBOL_DIRECTORY_SOURCES: dict[str, SymbolDirectorySource] = {
    "nasdaqlisted": SymbolDirectorySource(
        key="nasdaqlisted",
        url=NASDAQ_LISTED_URL,
        source="nasdaq_symdir_nasdaqlisted",
        symbol_field="Symbol",
        name_field="Security Name",
        exchange="Nasdaq",
    ),
    "otherlisted": SymbolDirectorySource(
        key="otherlisted",
        url=NASDAQ_OTHER_LISTED_URL,
        source="nasdaq_symdir_otherlisted",
        symbol_field="ACT Symbol",
        name_field="Security Name",
        exchange_field="Exchange",
    ),
}


def _now_utc_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _resolve_user_agent(user_agent: str | None = None) -> str:
    return str(user_agent or os.getenv("NASDAQ_USER_AGENT") or DEFAULT_NASDAQ_USER_AGENT).strip()


def _decode_response_body(raw: bytes, encoding: str | None) -> bytes:
    normalized = str(encoding or "").lower()
    if normalized == "gzip":
        return gzip.decompress(raw)
    if normalized == "deflate":
        try:
            return zlib.decompress(raw)
        except zlib.error:
            return zlib.decompress(raw, -zlib.MAX_WBITS)
    return raw


def fetch_symbol_directory_text(url: str, user_agent: str, timeout: float = 30.0) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept": "text/plain,*/*",
            "Accept-Encoding": "gzip, deflate",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            body = _decode_response_body(response.read(), response.headers.get("Content-Encoding"))
            return body.decode("utf-8-sig")
    except HTTPError as exc:
        raise RuntimeError(f"Nasdaq Symbol Directory request failed {exc.code}: {url}") from exc
    except URLError as exc:
        raise RuntimeError(f"Nasdaq Symbol Directory request failed: {url} ({exc.reason})") from exc


def _normalize_source_keys(sources: str | Iterable[str] | None) -> list[str]:
    if sources is None:
        raw = list(SYMBOL_DIRECTORY_SOURCES)
    elif isinstance(sources, str):
        raw = sources.replace("\n", ",").split(",")
    else:
        raw = list(sources)

    out: list[str] = []
    seen: set[str] = set()
    for item in raw:
        key = str(item or "").strip().lower()
        if not key or key in seen:
            continue
        if key not in SYMBOL_DIRECTORY_SOURCES:
            raise ValueError(f"unsupported symbol directory source: {key}")
        out.append(key)
        seen.add(key)
    return out


def _parse_file_creation_date(lines: list[str]) -> tuple[str | None, str | None]:
    for line in reversed(lines):
        text = line.strip()
        if not text.lower().startswith("file creation time:"):
            continue
        match = re.search(r"File Creation Time:\s*(\d{2})(\d{2})(\d{4})(\d{2})?:?(\d{2})?", text, re.I)
        if not match:
            return None, text
        month, day, year = match.group(1), match.group(2), match.group(3)
        return f"{year}-{month}-{day}", text
    return None, None


def _parse_pipe_rows(text: str) -> tuple[list[dict[str, str]], dict[str, Any]]:
    lines = [line.strip("\r") for line in str(text or "").splitlines() if line.strip()]
    file_date, file_creation_time = _parse_file_creation_date(lines)
    data_lines = [line for line in lines if not line.strip().lower().startswith("file creation time:")]
    if not data_lines:
        return [], {"file_creation_date": file_date, "file_creation_time": file_creation_time, "row_count": 0}

    reader = csv.DictReader(StringIO("\n".join(data_lines)), delimiter="|")
    rows = [dict(row) for row in reader if isinstance(row, dict)]
    return rows, {
        "file_creation_date": file_date,
        "file_creation_time": file_creation_time,
        "row_count": len(rows),
        "columns": list(reader.fieldnames or []),
    }


def _kind_from_row(row: dict[str, Any]) -> str:
    return "etf" if str(row.get("ETF") or "").strip().upper() == "Y" else "stock"


def _event_date_text(file_date: str | None, snapshot_date: str | None = None) -> str:
    return str(snapshot_date or file_date or date.today().isoformat())


def build_symbol_directory_lifecycle_rows(
    source_key: str,
    text: str,
    *,
    collected_at: str | None = None,
    snapshot_date: str | None = None,
    include_test_issues: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Convert a Nasdaq Symbol Directory current file into partial lifecycle evidence."""
    source = SYMBOL_DIRECTORY_SOURCES[str(source_key).strip().lower()]
    records, metadata = _parse_pipe_rows(text)
    collected = collected_at or _now_utc_text()
    event_date = _event_date_text(metadata.get("file_creation_date"), snapshot_date=snapshot_date)
    rows: list[dict[str, Any]] = []
    skipped_test_issues = 0
    skipped_missing_symbol = 0

    for record in records:
        symbol = str(record.get(source.symbol_field) or "").strip().upper()
        if not symbol:
            skipped_missing_symbol += 1
            continue
        if str(record.get("Test Issue") or "").strip().upper() == "Y" and not include_test_issues:
            skipped_test_issues += 1
            continue

        exchange = str(record.get(source.exchange_field) or "").strip() if source.exchange_field else source.exchange
        evidence = {
            "source": "nasdaq_symbol_directory",
            "source_file": source.key,
            "symbol": symbol,
            "event_type": "listing_observed",
            "event_date": event_date,
            "exchange": exchange or None,
            "market_category": str(record.get("Market Category") or "").strip() or None,
            "financial_status": str(record.get("Financial Status") or "").strip() or None,
            "cqs_symbol": str(record.get("CQS Symbol") or "").strip() or None,
            "nasdaq_symbol": str(record.get("NASDAQ Symbol") or "").strip() or None,
            "etf_flag": str(record.get("ETF") or "").strip() or None,
            "test_issue": str(record.get("Test Issue") or "").strip() or None,
            "file_creation_time": metadata.get("file_creation_time"),
            "source_note": "current Nasdaq Symbol Directory snapshot; not historical membership or delisting proof",
        }
        rows.append(
            {
                "symbol": symbol,
                "kind": _kind_from_row(record),
                "listing_status": "active",
                "source": source.source,
                "source_type": "current_listing_snapshot",
                "coverage_status": "partial",
                "first_seen_date": event_date,
                "last_seen_date": event_date,
                "inactive_detected_at": None,
                "event_type": "listing_observed",
                "event_date": event_date,
                "related_symbol": None,
                "related_cik": None,
                "name": str(record.get(source.name_field) or "").strip() or None,
                "source_ref": source.url,
                "evidence_json": json.dumps(evidence, ensure_ascii=False, sort_keys=True),
                "collected_at": collected,
                "error_msg": None,
            }
        )

    metadata.update(
        {
            "source": source.source,
            "source_key": source.key,
            "event_date": event_date,
            "rows_built": len(rows),
            "skipped_test_issues": skipped_test_issues,
            "skipped_missing_symbol": skipped_missing_symbol,
            "include_test_issues": bool(include_test_issues),
        }
    )
    return rows, metadata


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


def collect_and_store_symbol_directory_snapshots(
    sources: str | Iterable[str] | None = None,
    *,
    user_agent: str | None = None,
    request_timeout: float = 30.0,
    include_test_issues: bool = False,
    snapshot_date: str | None = None,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
    fetch_text: TextFetcher | None = None,
) -> dict[str, Any]:
    """Collect Nasdaq public current symbol directory files into lifecycle evidence rows."""
    source_keys = _normalize_source_keys(sources)
    effective_user_agent = _resolve_user_agent(user_agent)
    fetcher = fetch_text or fetch_symbol_directory_text
    all_rows: list[dict[str, Any]] = []
    source_summaries: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []

    for source_key in source_keys:
        source = SYMBOL_DIRECTORY_SOURCES[source_key]
        try:
            text = fetcher(source.url, effective_user_agent, request_timeout)
            rows, metadata = build_symbol_directory_lifecycle_rows(
                source_key,
                text,
                snapshot_date=snapshot_date,
                include_test_issues=include_test_issues,
            )
            all_rows.extend(rows)
            source_summaries.append(metadata)
        except Exception as exc:
            errors.append({"source": source_key, "error": str(exc)})

    db = MySQLClient(host, user, password, port)
    try:
        db.use_db(DB_NAME)
        rows_written = _upsert_lifecycle_rows(db, all_rows)
    finally:
        db.close()

    skipped_test_issues = sum(int(summary.get("skipped_test_issues") or 0) for summary in source_summaries)
    skipped_missing_symbol = sum(int(summary.get("skipped_missing_symbol") or 0) for summary in source_summaries)
    return {
        "source": "nasdaq_symbol_directory",
        "target_table": "finance_meta.nyse_symbol_lifecycle",
        "sources_requested": source_keys,
        "files_processed": len(source_summaries),
        "rows_found": len(all_rows),
        "rows_written": rows_written,
        "skipped_test_issues": skipped_test_issues,
        "skipped_missing_symbol": skipped_missing_symbol,
        "source_summaries": source_summaries,
        "errors": errors,
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
            "Nasdaq Symbol Directory files are current snapshots, not historical membership feeds.",
            "Absence from a current file is not delisting proof.",
            "Rows are stored as partial listing_observed evidence and must not loosen survivorship PASS criteria.",
        ],
    }
