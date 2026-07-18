from __future__ import annotations

import json
import os
import time
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .db.mysql import MySQLClient
from .db.schema import INSTITUTIONAL_13F_SCHEMAS, sync_table_schema


OPENFIGI_MAPPING_URL = "https://api.openfigi.com/v3/mapping"
OPENFIGI_SOURCE = "openfigi_v3"
OPENFIGI_SOURCE_REF = "https://www.openfigi.com/api/documentation"


def _now_utc_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def normalize_13f_identifier(value: Any) -> str | None:
    text = str(value or "").strip().upper()
    return text if len(text) == 9 and text.isalnum() else None


def build_openfigi_mapping_job(identifier: str) -> dict[str, str]:
    clean = normalize_13f_identifier(identifier)
    if not clean:
        raise ValueError(f"Invalid 13F identifier: {identifier!r}")
    return {
        "idType": "ID_CINS" if clean[0].isalpha() else "ID_CUSIP",
        "idValue": clean,
        "exchCode": "US",
        "marketSecDes": "Equity",
    }


def _clean_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _base_resolution(identifier: str, *, attempted_at: str) -> dict[str, Any]:
    clean = normalize_13f_identifier(identifier)
    if not clean:
        raise ValueError(f"Invalid 13F identifier: {identifier!r}")
    return {
        "identifier_value": clean,
        "identifier_type": "ID_CINS" if clean[0].isalpha() else "ID_CUSIP",
        "source": OPENFIGI_SOURCE,
        "source_ref": OPENFIGI_SOURCE_REF,
        "resolution_status": "unmapped",
        "symbol": None,
        "provider_name": None,
        "figi": None,
        "candidate_count": 0,
        "candidates_json": "[]",
        "warning_text": None,
        "error_text": None,
        "last_attempt_status": "success",
        "attempted_at": attempted_at,
        "resolved_at": attempted_at,
    }


def normalize_openfigi_mapping_result(
    identifier: str,
    payload: Mapping[str, Any],
    *,
    attempted_at: str,
) -> dict[str, Any]:
    """Reduce a provider response to one safe current 13F identity decision."""
    row = _base_resolution(identifier, attempted_at=attempted_at)
    candidates: list[dict[str, str | None]] = []
    seen: set[tuple[str, str | None]] = set()
    raw_data = payload.get("data")
    if isinstance(raw_data, list):
        for item in raw_data:
            if not isinstance(item, Mapping):
                continue
            ticker = (_clean_text(item.get("ticker")) or "").upper()
            if not ticker:
                continue
            figi = _clean_text(item.get("compositeFIGI") or item.get("figi"))
            key = (ticker, figi)
            if key in seen:
                continue
            seen.add(key)
            candidates.append(
                {
                    "ticker": ticker,
                    "name": _clean_text(item.get("name")),
                    "figi": figi,
                }
            )

    row["candidate_count"] = len(candidates)
    row["candidates_json"] = json.dumps(candidates, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    row["warning_text"] = _clean_text(payload.get("warning"))
    provider_error = _clean_text(payload.get("error"))
    if provider_error:
        return _error_resolution(identifier, provider_error, attempted_at=attempted_at)
    if len(candidates) == 1:
        candidate = candidates[0]
        row.update(
            {
                "resolution_status": "mapped",
                "symbol": candidate["ticker"],
                "provider_name": candidate["name"],
                "figi": candidate["figi"],
            }
        )
    elif len(candidates) > 1:
        row["resolution_status"] = "ambiguous"
    return row


def _error_resolution(identifier: str, error_text: str, *, attempted_at: str) -> dict[str, Any]:
    row = _base_resolution(identifier, attempted_at=attempted_at)
    row.update(
        {
            "error_text": str(error_text),
            "last_attempt_status": "error",
            "resolved_at": None,
        }
    )
    return row


def _chunks(rows: list[dict[str, Any]], size: int) -> Iterable[list[dict[str, Any]]]:
    for start in range(0, len(rows), size):
        yield rows[start : start + size]


def _dedupe_identifier_rows(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        identifier = normalize_13f_identifier(row.get("identifier_value") or row.get("cusip"))
        if identifier and identifier not in seen:
            output.append({**dict(row), "identifier_value": identifier})
            seen.add(identifier)
    return output


def _float_header(headers: Mapping[str, Any], name: str, default: float) -> float:
    try:
        return float(headers.get(name, default))
    except (TypeError, ValueError):
        return default


def _request_openfigi_batch(
    jobs: list[dict[str, str]],
    *,
    api_key: str | None,
    opener: Any,
    sleep_fn: Any,
    timeout: float,
    max_retries: int,
) -> tuple[list[dict[str, Any]], str | None, dict[str, float]]:
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "quant-data-pipeline/13f-identity",
    }
    clean_api_key = str(api_key or "").strip()
    if clean_api_key:
        headers["X-OPENFIGI-APIKEY"] = clean_api_key
    request = Request(
        OPENFIGI_MAPPING_URL,
        data=json.dumps(jobs).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    for attempt in range(max_retries + 1):
        try:
            with opener(request, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
                if not isinstance(payload, list):
                    return [], "OpenFIGI response must be a JSON array.", {}
                rate = {
                    "remaining": _float_header(response.headers, "ratelimit-remaining", -1.0),
                    "reset": _float_header(response.headers, "ratelimit-reset", 0.0),
                }
                return payload, None, rate
        except HTTPError as exc:
            if exc.code not in {429, 500, 503} or attempt >= max_retries:
                return [], f"OpenFIGI HTTP {exc.code}: {exc.reason}", {}
            reset = _float_header(exc.headers or {}, "ratelimit-reset", 0.0)
            sleep_fn(max(reset, 0.5 * (2**attempt)))
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            return [], f"OpenFIGI request failed: {exc}", {}
    return [], "OpenFIGI request failed after bounded retries.", {}


def collect_openfigi_resolutions(
    identifier_rows: Iterable[Mapping[str, Any]],
    *,
    api_key: str | None = None,
    opener: Any = urlopen,
    sleep_fn: Any = time.sleep,
    timeout: float = 30.0,
    max_retries: int = 2,
) -> list[dict[str, Any]]:
    """Resolve deduplicated 13F identifiers in provider-compliant batches."""
    clean_rows = _dedupe_identifier_rows(identifier_rows)
    batch_size = 100 if str(api_key or "").strip() else 10
    output: list[dict[str, Any]] = []
    batches = list(_chunks(clean_rows, batch_size))
    for batch_index, batch in enumerate(batches):
        jobs = [build_openfigi_mapping_job(row["identifier_value"]) for row in batch]
        payload, error_text, rate = _request_openfigi_batch(
            jobs,
            api_key=api_key,
            opener=opener,
            sleep_fn=sleep_fn,
            timeout=timeout,
            max_retries=max_retries,
        )
        attempted_at = _now_utc_text()
        if error_text is not None:
            output.extend(_error_resolution(row["identifier_value"], error_text, attempted_at=attempted_at) for row in batch)
            continue
        if len(payload) != len(batch):
            message = f"OpenFIGI response length mismatch: expected {len(batch)}, got {len(payload)}"
            output.extend(_error_resolution(row["identifier_value"], message, attempted_at=attempted_at) for row in batch)
            continue
        output.extend(
            normalize_openfigi_mapping_result(row["identifier_value"], result, attempted_at=attempted_at)
            for row, result in zip(batch, payload)
        )
        if batch_index < len(batches) - 1 and rate.get("remaining") == 0:
            sleep_fn(max(0.0, float(rate.get("reset") or 0.0)))
    return output


def _normalize_cik(value: Any) -> str | None:
    digits = "".join(character for character in str(value or "").strip() if character.isdigit())
    return digits.zfill(10)[-10:] if digits else None


def load_latest_13f_identifier_rows(
    db: MySQLClient,
    ciks: Iterable[str],
    *,
    refresh_existing: bool = False,
) -> list[dict[str, Any]]:
    """Load one row per latest-filing identifier for an explicit manager scope."""
    selected_ciks: list[str] = []
    for value in ciks:
        cik = _normalize_cik(value)
        if cik and cik not in selected_ciks:
            selected_ciks.append(cik)
    if not selected_ciks:
        return []

    placeholders = ", ".join(["%s"] * len(selected_ciks))
    retry_scope = ""
    if not refresh_existing:
        retry_scope = "AND (ir.identifier_value IS NULL OR ir.last_attempt_status = 'error')"
    sql = f"""
        SELECT
          h.cusip AS identifier_value,
          MAX(h.issuer_name) AS issuer_name
        FROM institutional_13f_manager m
        JOIN institutional_13f_holding h
          ON m.latest_accession_number = h.accession_number
        LEFT JOIN institutional_13f_identifier_resolution ir
          ON h.cusip = ir.identifier_value
         AND ir.source = 'openfigi_v3'
        WHERE m.cik IN ({placeholders})
          {retry_scope}
        GROUP BY h.cusip
        ORDER BY h.cusip
    """
    raw_rows = db.query(sql, tuple(selected_ciks))
    return _dedupe_identifier_rows(raw_rows)


def upsert_13f_identifier_resolutions(db: MySQLClient, rows: list[dict[str, Any]]) -> int:
    """Persist current provider decisions without erasing good state on request errors."""
    if not rows:
        return 0
    sql = """
        INSERT INTO institutional_13f_identifier_resolution (
          identifier_value, identifier_type, source, resolution_status, symbol,
          provider_name, figi, candidate_count, candidates_json, source_ref,
          warning_text, error_text, last_attempt_status, attempted_at, resolved_at
        ) VALUES (
          %(identifier_value)s, %(identifier_type)s, %(source)s, %(resolution_status)s, %(symbol)s,
          %(provider_name)s, %(figi)s, %(candidate_count)s, %(candidates_json)s, %(source_ref)s,
          %(warning_text)s, %(error_text)s, %(last_attempt_status)s, %(attempted_at)s, %(resolved_at)s
        )
        ON DUPLICATE KEY UPDATE
          identifier_type = VALUES(identifier_type),
          resolution_status = IF(VALUES(last_attempt_status) = 'error', resolution_status, VALUES(resolution_status)),
          symbol = IF(VALUES(last_attempt_status) = 'error', symbol, VALUES(symbol)),
          provider_name = IF(VALUES(last_attempt_status) = 'error', provider_name, VALUES(provider_name)),
          figi = IF(VALUES(last_attempt_status) = 'error', figi, VALUES(figi)),
          candidate_count = IF(VALUES(last_attempt_status) = 'error', candidate_count, VALUES(candidate_count)),
          candidates_json = IF(VALUES(last_attempt_status) = 'error', candidates_json, VALUES(candidates_json)),
          source_ref = VALUES(source_ref),
          warning_text = IF(VALUES(last_attempt_status) = 'error', warning_text, VALUES(warning_text)),
          error_text = VALUES(error_text),
          last_attempt_status = VALUES(last_attempt_status),
          attempted_at = VALUES(attempted_at),
          resolved_at = IF(VALUES(last_attempt_status) = 'error', resolved_at, VALUES(resolved_at))
    """
    db.executemany(sql, rows)
    return len(rows)


def collect_and_store_openfigi_13f_mappings(
    *,
    ciks: Iterable[str],
    api_key: str | None = None,
    refresh_existing: bool = False,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
    opener: Any = urlopen,
    sleep_fn: Any = time.sleep,
    timeout: float = 30.0,
    max_retries: int = 2,
) -> dict[str, Any]:
    """Resolve and persist latest 13F identities for a selected manager scope."""
    db = MySQLClient(host, user, password, port)
    identifiers: list[dict[str, Any]] = []
    resolutions: list[dict[str, Any]] = []
    rows_written = 0
    configured_api_key = api_key or os.getenv("OPENFIGI_API_KEY")
    try:
        db.use_db("finance_meta")
        sync_table_schema(
            db,
            "institutional_13f_identifier_resolution",
            INSTITUTIONAL_13F_SCHEMAS["institutional_13f_identifier_resolution"],
            "finance_meta",
        )
        identifiers = load_latest_13f_identifier_rows(db, ciks, refresh_existing=refresh_existing)
        resolutions = collect_openfigi_resolutions(
            identifiers,
            api_key=configured_api_key,
            opener=opener,
            sleep_fn=sleep_fn,
            timeout=timeout,
            max_retries=max_retries,
        )
        rows_written = upsert_13f_identifier_resolutions(db, resolutions)
    finally:
        db.close()

    counts = Counter(
        row["resolution_status"] if row["last_attempt_status"] != "error" else "error"
        for row in resolutions
    )
    return {
        "source": OPENFIGI_SOURCE,
        "source_ref": OPENFIGI_SOURCE_REF,
        "identifiers_requested": len(identifiers),
        "rows_written": rows_written,
        "mapped": counts["mapped"],
        "ambiguous": counts["ambiguous"],
        "unmapped": counts["unmapped"],
        "errors": counts["error"],
        "api_key_used": bool(configured_api_key),
        "target_table": "finance_meta.institutional_13f_identifier_resolution",
    }
