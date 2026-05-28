from __future__ import annotations

import gzip
import json
import os
import time
import zlib
from datetime import datetime, timezone
from typing import Any, Callable, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .db.mysql import MySQLClient
from .db.schema import NYSE_SCHEMAS, sync_table_schema

DB_NAME = "finance_meta"
SEC_COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_SUBMISSIONS_URL_TEMPLATE = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
SEC_SUBMISSIONS_ARCHIVE_URL_TEMPLATE = "https://data.sec.gov/submissions/{file_name}"
SEC_FILING_ARCHIVE_URL_TEMPLATE = "https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{primary_document}"
SEC_FILING_DIRECTORY_URL_TEMPLATE = "https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/"
DEFAULT_SEC_USER_AGENT = "quant-data-pipeline local-research@example.com"
FORM25_TYPES = {"25", "25/A", "25-NSE", "25-NSE/A"}


JsonFetcher = Callable[[str, str, float], Any]


def _now_utc_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _resolve_user_agent(user_agent: str | None = None) -> str:
    return str(user_agent or os.getenv("SEC_USER_AGENT") or DEFAULT_SEC_USER_AGENT).strip()


def _safe_date(value: Any) -> str | None:
    text = str(value or "").strip()
    if len(text) == 10 and text[4] == "-" and text[7] == "-":
        return text
    return None


def _parse_symbol_list(symbols: str | Iterable[str] | None) -> list[str]:
    if symbols is None:
        return []
    if isinstance(symbols, str):
        raw = symbols.replace("\n", ",").split(",")
    else:
        raw = list(symbols)

    parsed: list[str] = []
    seen: set[str] = set()
    for item in raw:
        symbol = str(item or "").strip().upper()
        if symbol and symbol not in seen:
            parsed.append(symbol)
            seen.add(symbol)
    return parsed


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


def fetch_sec_json(url: str, user_agent: str, timeout: float = 30.0) -> Any:
    request = Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            body = _decode_response_body(response.read(), response.headers.get("Content-Encoding"))
            return json.loads(body.decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"SEC request failed {exc.code}: {url}") from exc
    except URLError as exc:
        raise RuntimeError(f"SEC request failed: {url} ({exc.reason})") from exc


def normalize_sec_ticker_map(payload: Any) -> dict[str, dict[str, Any]]:
    """Normalize SEC company_tickers.json into an uppercase ticker map."""
    if not isinstance(payload, dict):
        return {}

    out: dict[str, dict[str, Any]] = {}
    for value in payload.values():
        if not isinstance(value, dict):
            continue
        ticker = str(value.get("ticker") or "").strip().upper()
        cik_raw = value.get("cik_str")
        try:
            cik = int(cik_raw)
        except (TypeError, ValueError):
            continue
        if not ticker:
            continue
        out[ticker] = {
            "ticker": ticker,
            "cik": cik,
            "title": str(value.get("title") or "").strip() or None,
        }
    return out


def _recent_filing_records(submissions: dict[str, Any]) -> list[dict[str, Any]]:
    recent = ((submissions.get("filings") or {}).get("recent") or {}) if isinstance(submissions, dict) else {}
    if not isinstance(recent, dict):
        return []

    columns = {
        "form": recent.get("form") or [],
        "accessionNumber": recent.get("accessionNumber") or [],
        "filingDate": recent.get("filingDate") or [],
        "reportDate": recent.get("reportDate") or [],
        "primaryDocument": recent.get("primaryDocument") or [],
    }
    max_len = max((len(value) for value in columns.values() if isinstance(value, list)), default=0)
    rows: list[dict[str, Any]] = []
    for idx in range(max_len):
        row: dict[str, Any] = {}
        for key, values in columns.items():
            row[key] = values[idx] if isinstance(values, list) and idx < len(values) else None
        rows.append(row)
    return rows


def extract_sec_form25_filings(submissions: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract Form 25 filing metadata from SEC submissions JSON."""
    filings: list[dict[str, Any]] = []
    seen_accessions: set[str] = set()
    for row in _recent_filing_records(submissions):
        form_type = str(row.get("form") or "").strip().upper()
        accession_no = str(row.get("accessionNumber") or "").strip()
        if form_type not in FORM25_TYPES or not accession_no or accession_no in seen_accessions:
            continue
        seen_accessions.add(accession_no)
        filings.append(
            {
                "form_type": form_type,
                "accession_no": accession_no,
                "filing_date": _safe_date(row.get("filingDate")),
                "report_date": _safe_date(row.get("reportDate")),
                "primary_document": str(row.get("primaryDocument") or "").strip() or None,
            }
        )
    return filings


def _archive_json_file_names(submissions: dict[str, Any], max_archive_files: int) -> list[str]:
    files = ((submissions.get("filings") or {}).get("files") or []) if isinstance(submissions, dict) else []
    names: list[str] = []
    for item in files:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "").strip()
        if name.endswith(".json"):
            names.append(name)
        if len(names) >= max(0, int(max_archive_files)):
            break
    return names


def _filing_url(cik: int, accession_no: str, primary_document: str | None) -> str:
    accession_clean = accession_no.replace("-", "")
    cik_text = str(int(cik))
    if primary_document:
        return SEC_FILING_ARCHIVE_URL_TEMPLATE.format(
            cik=cik_text,
            accession=accession_clean,
            primary_document=primary_document,
        )
    return SEC_FILING_DIRECTORY_URL_TEMPLATE.format(cik=cik_text, accession=accession_clean)


def build_sec_form25_lifecycle_rows(
    symbol: str,
    kind: str,
    company: dict[str, Any],
    filings: Iterable[dict[str, Any]],
    *,
    collected_at: str | None = None,
) -> list[dict[str, Any]]:
    """Convert SEC Form 25 filings into lifecycle rows for nyse_symbol_lifecycle."""
    normalized_symbol = str(symbol or "").strip().upper()
    normalized_kind = "etf" if str(kind or "").strip().lower() == "etf" else "stock"
    cik = int(company.get("cik") or company.get("cik_str") or 0)
    title = str(company.get("title") or "").strip() or None
    collected = collected_at or _now_utc_text()
    rows: list[dict[str, Any]] = []

    for filing in filings:
        accession_no = str(filing.get("accession_no") or "").strip()
        if not normalized_symbol or not accession_no or cik <= 0:
            continue
        accession_clean = accession_no.replace("-", "")
        filing_date = _safe_date(filing.get("filing_date"))
        primary_document = str(filing.get("primary_document") or "").strip() or None
        form_type = str(filing.get("form_type") or "").strip().upper() or "25"
        source_ref = _filing_url(cik, accession_no, primary_document)
        evidence = {
            "source": "sec_edgar_form25",
            "symbol": normalized_symbol,
            "cik": cik,
            "company_title": title,
            "form_type": form_type,
            "accession_no": accession_no,
            "filing_date": filing_date,
            "report_date": _safe_date(filing.get("report_date")),
            "primary_document": primary_document,
            "source_note": "SEC Form 25 delisting evidence; absence of Form 25 is not active-listing proof",
        }
        rows.append(
            {
                "symbol": normalized_symbol,
                "kind": normalized_kind,
                "listing_status": "delisted",
                "source": f"sec_form25_{accession_clean}"[:64],
                "source_type": "delisting_feed",
                "coverage_status": "actual",
                "first_seen_date": None,
                "last_seen_date": filing_date,
                "inactive_detected_at": filing_date,
                "name": title,
                "source_ref": source_ref,
                "evidence_json": json.dumps(evidence, ensure_ascii=False, sort_keys=True),
                "collected_at": collected,
                "error_msg": None,
            }
        )
    return rows


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


def _upsert_lifecycle_rows(db: MySQLClient, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0

    sync_table_schema(db, "nyse_symbol_lifecycle", NYSE_SCHEMAS["symbol_lifecycle"], DB_NAME)
    sql = """
        INSERT INTO nyse_symbol_lifecycle (
            symbol, kind, listing_status, source, source_type, coverage_status,
            first_seen_date, last_seen_date, inactive_detected_at,
            name, source_ref, evidence_json, collected_at, error_msg
        )
        VALUES (
            %(symbol)s, %(kind)s, %(listing_status)s, %(source)s, %(source_type)s, %(coverage_status)s,
            %(first_seen_date)s, %(last_seen_date)s, %(inactive_detected_at)s,
            %(name)s, %(source_ref)s, %(evidence_json)s, %(collected_at)s, %(error_msg)s
        )
        ON DUPLICATE KEY UPDATE
            listing_status = VALUES(listing_status),
            source_type = VALUES(source_type),
            coverage_status = VALUES(coverage_status),
            first_seen_date = COALESCE(first_seen_date, VALUES(first_seen_date)),
            last_seen_date = VALUES(last_seen_date),
            inactive_detected_at = VALUES(inactive_detected_at),
            name = VALUES(name),
            source_ref = VALUES(source_ref),
            evidence_json = VALUES(evidence_json),
            collected_at = VALUES(collected_at),
            error_msg = NULL
    """
    db.executemany(sql, rows)
    return len(rows)


def collect_and_store_sec_form25_delistings(
    symbols: str | Iterable[str] | None,
    *,
    user_agent: str | None = None,
    include_archive_files: bool = True,
    max_archive_files: int = 5,
    request_sleep: float = 0.2,
    request_timeout: float = 30.0,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
    fetch_json: JsonFetcher | None = None,
) -> dict[str, Any]:
    """Collect official SEC Form 25 delisting evidence and store compact DB rows."""
    parsed_symbols = _parse_symbol_list(symbols)
    if not parsed_symbols:
        raise ValueError("symbols are required for SEC Form 25 delisting collection")

    effective_user_agent = _resolve_user_agent(user_agent)
    fetcher = fetch_json or fetch_sec_json
    ticker_map = normalize_sec_ticker_map(fetcher(SEC_COMPANY_TICKERS_URL, effective_user_agent, request_timeout))
    db = MySQLClient(host, user, password, port)
    all_rows: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    unmapped_symbols: list[str] = []
    symbols_without_form25: list[str] = []
    mapped_symbols: list[str] = []
    archive_files_checked = 0

    try:
        db.use_db(DB_NAME)
        kind_by_symbol = _load_symbol_kind_map(db, parsed_symbols)
        for symbol in parsed_symbols:
            company = ticker_map.get(symbol)
            if not company:
                unmapped_symbols.append(symbol)
                continue

            mapped_symbols.append(symbol)
            try:
                submissions_url = SEC_SUBMISSIONS_URL_TEMPLATE.format(cik=int(company["cik"]))
                submissions = fetcher(submissions_url, effective_user_agent, request_timeout)
                filings = extract_sec_form25_filings(submissions)

                if include_archive_files:
                    seen_accessions = {filing["accession_no"] for filing in filings}
                    for file_name in _archive_json_file_names(submissions, max_archive_files):
                        if request_sleep > 0:
                            time.sleep(float(request_sleep))
                        archive_files_checked += 1
                        archive_url = SEC_SUBMISSIONS_ARCHIVE_URL_TEMPLATE.format(file_name=file_name)
                        archive_payload = fetcher(archive_url, effective_user_agent, request_timeout)
                        archived_filings = extract_sec_form25_filings(archive_payload)
                        for filing in archived_filings:
                            accession_no = filing.get("accession_no")
                            if accession_no in seen_accessions:
                                continue
                            filings.append(filing)
                            seen_accessions.add(accession_no)

                if not filings:
                    symbols_without_form25.append(symbol)
                    continue

                all_rows.extend(
                    build_sec_form25_lifecycle_rows(
                        symbol,
                        kind_by_symbol.get(symbol, "stock"),
                        company,
                        filings,
                    )
                )
            except Exception as exc:
                errors.append({"symbol": symbol, "error": str(exc)})
            finally:
                if request_sleep > 0:
                    time.sleep(float(request_sleep))

        rows_written = _upsert_lifecycle_rows(db, all_rows)
    finally:
        db.close()

    return {
        "source": "sec_edgar_form25",
        "target_table": "finance_meta.nyse_symbol_lifecycle",
        "requested": len(parsed_symbols),
        "mapped": len(mapped_symbols),
        "forms_found": len(all_rows),
        "rows_written": rows_written,
        "archive_files_checked": archive_files_checked,
        "unmapped_symbols": unmapped_symbols,
        "symbols_without_form25": symbols_without_form25,
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
            "Form 25 is delisting / withdrawal evidence, not complete historical universe membership.",
            "Absence of Form 25 is not proof that a symbol is active.",
            "SEC ticker mapping may miss historical or changed tickers.",
            "Set SEC_USER_AGENT or pass user_agent for declared SEC scripted access.",
        ],
    }
