from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

import pandas as pd

from finance.data.db.mysql import MySQLClient

from .price import load_price_freshness_summary


def _normalize_symbol(value: Any) -> str:
    return str(value or "").strip().upper()


def _normalize_symbols(values: Iterable[Any] | None) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values or []:
        symbol = _normalize_symbol(value)
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        out.append(symbol)
    return out


def _date_text(value: Any) -> str | None:
    if value in (None, ""):
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.strftime("%Y-%m-%d")


def _safe_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(parsed):
        return None
    return parsed


def _price_rows_by_symbol(rows: Sequence[Mapping[str, Any]] | pd.DataFrame | None) -> dict[str, dict[str, Any]]:
    if isinstance(rows, pd.DataFrame):
        records = rows.to_dict(orient="records")
    else:
        records = [dict(row) for row in rows or []]
    out: dict[str, dict[str, Any]] = {}
    for row in records:
        symbol = _normalize_symbol(row.get("symbol"))
        if not symbol:
            continue
        item = dict(row)
        item["symbol"] = symbol
        item["latest_date"] = _date_text(row.get("latest_date"))
        out[symbol] = item
    return out


def _refresh_symbols_from_price_details(price_details: Mapping[str, Any]) -> list[str]:
    raw = price_details.get("refresh_symbols_all")
    if not raw:
        raw = list(price_details.get("stale_symbols_all") or []) + list(price_details.get("missing_symbols_all") or [])
    if not raw:
        raw = list(price_details.get("stale_symbols") or []) + list(price_details.get("missing_symbols") or [])
    return _normalize_symbols(raw)


def _classify_confidence(score: float) -> str:
    if score >= 0.85:
        return "HIGH"
    if score >= 0.65:
        return "MEDIUM"
    return "LOW"


def _parse_evidence_json(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if value in (None, ""):
        return {}
    if not isinstance(value, str):
        return {}
    try:
        parsed = json.loads(value)
    except (TypeError, ValueError, json.JSONDecodeError):
        return {}
    return dict(parsed) if isinstance(parsed, Mapping) else {}


def _evidence_factor(
    label: str,
    *,
    score: float | None = None,
    detail: Any = None,
    source: Any = None,
) -> dict[str, Any]:
    factor: dict[str, Any] = {"label": label}
    if score is not None:
        factor["score"] = round(float(score), 4)
    detail_text = str(detail or "").strip()
    if detail_text:
        factor["detail"] = detail_text
    source_text = str(source or "").strip()
    if source_text:
        factor["source"] = source_text
    return factor


def _infer_source_quality(row: Mapping[str, Any], evidence: Mapping[str, Any]) -> str:
    explicit = str(evidence.get("source_quality") or "").strip()
    if explicit:
        return explicit
    source_ref = str(row.get("source_ref") or "").strip()
    source = str(row.get("source") or "").strip().lower()
    source_type = str(row.get("source_type") or "").strip().lower()
    if source_ref and any(marker in f"{source} {source_type}" for marker in ["press", "exchange", "sec", "historical_listing"]):
        return "official_corporate_action"
    if source_ref:
        return "referenced_lifecycle"
    if row.get("related_cik"):
        return "identity_crosscheck"
    return "lifecycle_row"


def _candidate_score(
    row: Mapping[str, Any],
    resolved_price: Mapping[str, Any] | None,
    target_end: str | None,
) -> tuple[float, list[dict[str, Any]], dict[str, Any]]:
    evidence_payload = _parse_evidence_json(row.get("evidence_json"))
    evidence_factors: list[dict[str, Any]] = []
    score = _safe_float(row.get("confidence"))
    if score is None:
        score = 0.6
    else:
        evidence_factors.append(_evidence_factor("lifecycle row confidence", score=score))
    if row.get("related_cik"):
        score = max(score, 0.86)
        evidence_factors.append(_evidence_factor("same CIK", score=0.86, detail=row.get("related_cik")))
    if str(row.get("coverage_status") or "").strip().lower() == "actual":
        score = max(score, 0.82)
        evidence_factors.append(_evidence_factor("lifecycle evidence", score=0.82))
    latest_date = _date_text((resolved_price or {}).get("latest_date"))
    if latest_date and (target_end is None or latest_date >= target_end):
        score = max(score, 0.9)
        evidence_factors.append(_evidence_factor("resolved ticker has current price", score=0.9, detail=latest_date))
    if row.get("source_ref"):
        score = max(score, 0.88)
        evidence_factors.append(_evidence_factor("official/source reference", score=0.88, source=row.get("source_ref")))
    source_quality = _infer_source_quality(row, evidence_payload)
    if source_quality == "official_corporate_action":
        score = max(score, 0.9)
    review_note = str(evidence_payload.get("review_note") or evidence_payload.get("summary") or "").strip()
    evidence_payload["source_quality"] = source_quality
    if review_note:
        evidence_payload["review_note"] = review_note
    if evidence_factors:
        evidence_payload["evidence_factors"] = evidence_factors
    return min(score, 0.99), evidence_factors, evidence_payload


def diagnose_symbol_identity_issues(
    symbols: Iterable[Any] | None,
    *,
    price_details: Mapping[str, Any] | None = None,
    lifecycle_rows: Sequence[Mapping[str, Any]] | pd.DataFrame | None = None,
    resolved_price_rows: Sequence[Mapping[str, Any]] | pd.DataFrame | None = None,
) -> dict[str, Any]:
    """Build ticker-change candidates for stale/missing symbols without applying them."""
    price_details = dict(price_details or {})
    requested = _normalize_symbols(symbols)
    problem_symbols = _refresh_symbols_from_price_details(price_details) or requested
    problem_symbol_set = set(problem_symbols)
    target_end = _date_text(price_details.get("effective_end_date") or price_details.get("target_end_date"))
    resolved_price_by_symbol = _price_rows_by_symbol(resolved_price_rows)
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()
    records = lifecycle_rows.to_dict(orient="records") if isinstance(lifecycle_rows, pd.DataFrame) else list(lifecycle_rows or [])

    for raw_row in records:
        row = dict(raw_row)
        source_symbol = _normalize_symbol(row.get("symbol") or row.get("source_symbol"))
        resolved_symbol = _normalize_symbol(row.get("related_symbol") or row.get("resolved_symbol"))
        if (
            not source_symbol
            or not resolved_symbol
            or source_symbol == resolved_symbol
            or source_symbol not in problem_symbol_set
            or source_symbol in seen
        ):
            continue
        if str(row.get("event_type") or "").strip().lower() != "ticker_change":
            continue
        resolved_price = resolved_price_by_symbol.get(resolved_symbol)
        score, evidence_factors, evidence_payload = _candidate_score(row, resolved_price, target_end)
        evidence_labels = [str(factor.get("label")) for factor in evidence_factors if factor.get("label")]
        evidence_summary = "; ".join(evidence_labels) if evidence_labels else "ticker-change lifecycle row"
        confidence_level = _classify_confidence(score)
        recommended_action = (
            "apply_ticker_change_repair"
            if confidence_level in {"HIGH", "MEDIUM"}
            else "review_symbol_identity"
        )
        evidence_payload["summary"] = evidence_summary
        evidence_payload["recommended_action"] = recommended_action
        candidates.append(
            {
                "issue_type": "symbol_identity_issue",
                "source_symbol": source_symbol,
                "resolved_symbol": resolved_symbol,
                "alias_type": "ticker_change",
                "event_type": "ticker_change",
                "effective_date": _date_text(row.get("event_date")),
                "related_cik": row.get("related_cik"),
                "confidence": round(score, 4),
                "confidence_level": confidence_level,
                "resolution_status": str(row.get("resolution_status") or "candidate").strip().lower() or "candidate",
                "evidence_summary": evidence_summary,
                "evidence_factors": evidence_factors,
                "evidence": evidence_payload,
                "source_quality": evidence_payload.get("source_quality"),
                "review_note": evidence_payload.get("review_note"),
                "recommended_action": recommended_action,
                "review_required": recommended_action != "apply_ticker_change_repair",
                "source": row.get("source"),
                "source_ref": row.get("source_ref"),
                "name": row.get("name"),
                "resolved_latest_date": _date_text((resolved_price or {}).get("latest_date")),
            }
        )
        seen.add(source_symbol)

    candidates.sort(key=lambda item: (-float(item.get("confidence") or 0.0), item["source_symbol"]))
    return {
        "schema_version": "symbol_identity_diagnosis_v1",
        "issue_type": "symbol_identity_issue",
        "symbols": problem_symbols,
        "issue_count": len(candidates),
        "candidates": candidates,
    }


def load_ticker_change_lifecycle_rows(symbols: Iterable[Any] | None) -> list[dict[str, Any]]:
    normalized = _normalize_symbols(symbols)
    if not normalized:
        return []
    placeholders = ",".join(["%s"] * len(normalized))
    db: MySQLClient | None = None
    try:
        db = MySQLClient("localhost", "root", "1234", 3306)
        db.use_db("finance_meta")
        try:
            return db.query(
                f"""
                SELECT
                    symbol, kind, listing_status, source, source_type, coverage_status,
                    event_type, event_date, related_symbol, related_cik, resolution_status,
                    confidence, name, source_ref, evidence_json, collected_at, error_msg
                FROM nyse_symbol_lifecycle
                WHERE symbol IN ({placeholders})
                  AND event_type = %s
                  AND related_symbol IS NOT NULL
                ORDER BY
                    CASE resolution_status WHEN 'active' THEN 0 WHEN 'candidate' THEN 1 ELSE 2 END,
                    confidence DESC,
                    event_date DESC
                """,
                normalized + ["ticker_change"],
            )
        except Exception:
            return db.query(
                f"""
                SELECT
                    symbol, kind, listing_status, source, source_type, coverage_status,
                    event_type, event_date, related_symbol, related_cik,
                    'candidate' AS resolution_status,
                    NULL AS confidence,
                    name, source_ref, evidence_json, collected_at, error_msg
                FROM nyse_symbol_lifecycle
                WHERE symbol IN ({placeholders})
                  AND event_type = %s
                  AND related_symbol IS NOT NULL
                ORDER BY event_date DESC
                """,
                normalized + ["ticker_change"],
            )
    except Exception:
        return []
    finally:
        if db is not None:
            db.close()


def load_active_symbol_resolutions(symbols: Iterable[Any] | None) -> dict[str, dict[str, Any]]:
    rows = load_ticker_change_lifecycle_rows(symbols)
    active: dict[str, dict[str, Any]] = {}
    for row in rows:
        source_symbol = _normalize_symbol(row.get("symbol"))
        resolved_symbol = _normalize_symbol(row.get("related_symbol"))
        if not source_symbol or not resolved_symbol or source_symbol in active:
            continue
        if str(row.get("resolution_status") or "").strip().lower() != "active":
            continue
        active[source_symbol] = {
            "source_symbol": source_symbol,
            "resolved_symbol": resolved_symbol,
            "alias_type": "ticker_change",
            "effective_date": _date_text(row.get("event_date")),
            "confidence": _safe_float(row.get("confidence")),
            "resolution_status": "active",
            "source": row.get("source"),
            "source_ref": row.get("source_ref"),
        }
    return active


def diagnose_symbol_identity_issues_from_db(
    symbols: Iterable[Any] | None,
    *,
    price_details: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    price_details = dict(price_details or {})
    problem_symbols = _refresh_symbols_from_price_details(price_details) or _normalize_symbols(symbols)
    lifecycle_rows = load_ticker_change_lifecycle_rows(problem_symbols)
    resolved_symbols = _normalize_symbols(row.get("related_symbol") for row in lifecycle_rows)
    target_end = _date_text(price_details.get("effective_end_date") or price_details.get("target_end_date"))
    resolved_price_rows: list[dict[str, Any]] = []
    if resolved_symbols:
        try:
            frame = load_price_freshness_summary(resolved_symbols, end=target_end)
            resolved_price_rows = frame.to_dict(orient="records") if not frame.empty else []
        except Exception:
            resolved_price_rows = []
    return diagnose_symbol_identity_issues(
        problem_symbols,
        price_details=price_details,
        lifecycle_rows=lifecycle_rows,
        resolved_price_rows=resolved_price_rows,
    )
