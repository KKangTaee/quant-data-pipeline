from __future__ import annotations

from typing import Any

import pandas as pd

from finance.loaders import (
    load_asset_profile_status_summary,
    load_price_window_summary,
    load_symbol_lifecycle_coverage_summary,
)


DATA_COVERAGE_AUDIT_SCHEMA_VERSION = "data_coverage_audit_v1"
DATA_COVERAGE_CONTEXT_SCHEMA_VERSION = "data_coverage_context_v1"

DATA_COVERAGE_READY = "DATA_COVERAGE_READY"
DATA_COVERAGE_REVIEW = "DATA_COVERAGE_REVIEW"
DATA_COVERAGE_NEEDS_INPUT = "DATA_COVERAGE_NEEDS_INPUT"
DATA_COVERAGE_BLOCKED = "DATA_COVERAGE_BLOCKED"

DATA_COVERAGE_ROUTE_LABELS = {
    DATA_COVERAGE_READY: "Ready",
    DATA_COVERAGE_REVIEW: "Review Required",
    DATA_COVERAGE_NEEDS_INPUT: "Coverage Input Needed",
    DATA_COVERAGE_BLOCKED: "Blocked",
}

_STATUS_RANK = {
    "PASS": 0,
    "REVIEW": 1,
    "NEEDS_INPUT": 2,
    "BLOCKED": 3,
}
_HISTORICAL_LIFECYCLE_SOURCE_TYPES = {"historical_listing", "delisting_feed", "computed_from_snapshots"}
_SEC_IDENTITY_SOURCE = "sec_company_tickers_exchange"


def _safe_text(value: Any, fallback: str = "-") -> str:
    text = str(value or "").strip()
    return text or fallback


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(numeric):
        return None
    return numeric


def _date_text(value: Any) -> str | None:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return pd.Timestamp(parsed).strftime("%Y-%m-%d")


def _status(value: Any, *, default: str = "NEEDS_INPUT") -> str:
    text = str(value or "").strip().upper()
    if not text or text in {"-", "NONE", "NULL", "N/A", "UNKNOWN"}:
        return default
    if text in {"BLOCKED", "BLOCK", "ERROR", "FAILED", "FAIL"} or "ERROR" in text:
        return "BLOCKED"
    if text in {"NOT_RUN", "MISSING", "NO_DATA", "UNAVAILABLE"}:
        return "NEEDS_INPUT"
    if text in {"PASS", "OK", "READY", "SUCCESS", "FRESH", "COMPLETE", "COMPLETED"}:
        return "PASS"
    if text.startswith("READY_"):
        return "PASS"
    if text in {"REVIEW", "STALE", "PARTIAL", "WARNING", "WARN", "WATCH"} or "REVIEW" in text:
        return "REVIEW"
    return default


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "pass", "ready", "controlled"}


def _row(
    *,
    criteria: str,
    status: str,
    current: Any,
    evidence: Any,
    next_action: str,
    meaning: str,
) -> dict[str, Any]:
    normalized = status if status in _STATUS_RANK else _status(status, default="REVIEW")
    return {
        "Criteria": criteria,
        "Status": normalized,
        "Ready": normalized == "PASS",
        "Current": _safe_text(current),
        "Evidence": _safe_text(evidence),
        "Next Action": next_action,
        "Meaning": meaning,
    }


def _frame_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    if frame.empty:
        return []
    records: list[dict[str, Any]] = []
    for record in frame.to_dict(orient="records"):
        clean: dict[str, Any] = {}
        for key, value in dict(record).items():
            if isinstance(value, pd.Timestamp):
                clean[key] = _date_text(value)
            elif not isinstance(value, (dict, list, tuple, set)) and pd.isna(value):
                clean[key] = None
            else:
                clean[key] = value
        records.append(clean)
    return records


def _normalize_symbol_weights(symbol_weights: dict[str, Any] | None) -> dict[str, float]:
    clean: dict[str, float] = {}
    for symbol, weight in dict(symbol_weights or {}).items():
        ticker = str(symbol or "").strip().upper()
        numeric = _optional_float(weight)
        if not ticker:
            continue
        clean[ticker] = clean.get(ticker, 0.0) + (numeric if numeric is not None and numeric > 0.0 else 1.0)
    if not clean:
        return {}
    total = sum(clean.values())
    if total <= 0:
        return {symbol: 0.0 for symbol in sorted(clean)}
    return {symbol: round(weight / total * 100.0, 4) for symbol, weight in sorted(clean.items())}


def build_db_data_coverage_context(
    symbol_weights: dict[str, Any] | None,
    *,
    start: str | None,
    end: str | None,
    timeframe: str = "1d",
) -> dict[str, Any]:
    """Build compact DB coverage evidence for Practical Validation without persisting raw rows."""

    weights = _normalize_symbol_weights(symbol_weights)
    symbols = list(weights)
    price_window_rows: list[dict[str, Any]] = []
    asset_profile_rows: list[dict[str, Any]] = []
    symbol_lifecycle_rows: list[dict[str, Any]] = []
    price_window_error = None
    asset_profile_error = None
    symbol_lifecycle_error = None
    if symbols:
        try:
            price_window_rows = _frame_records(
                load_price_window_summary(symbols=symbols, start=start, end=end, timeframe=timeframe)
            )
        except Exception as exc:  # pragma: no cover - DB failures are surfaced as evidence.
            price_window_error = str(exc)
        try:
            asset_profile_rows = _frame_records(load_asset_profile_status_summary(symbols))
        except Exception as exc:  # pragma: no cover - DB failures are surfaced as evidence.
            asset_profile_error = str(exc)
        try:
            symbol_lifecycle_rows = _frame_records(
                load_symbol_lifecycle_coverage_summary(symbols=symbols, start=start, end=end)
            )
        except Exception as exc:  # pragma: no cover - DB failures are surfaced as evidence.
            symbol_lifecycle_error = str(exc)
    return {
        "schema_version": DATA_COVERAGE_CONTEXT_SCHEMA_VERSION,
        "source": "finance.loaders",
        "symbols": symbols,
        "symbol_weights": weights,
        "requested_start": start,
        "requested_end": end,
        "timeframe": timeframe,
        "price_window_rows": price_window_rows,
        "price_window_error": price_window_error,
        "asset_profile_rows": asset_profile_rows,
        "asset_profile_error": asset_profile_error,
        "symbol_lifecycle_rows": symbol_lifecycle_rows,
        "symbol_lifecycle_error": symbol_lifecycle_error,
    }


def _nested_values_for_keys(value: Any, keys: set[str]) -> list[Any]:
    found: list[Any] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key or "").strip().lower() in keys:
                found.append(child)
            if isinstance(child, dict):
                found.extend(_nested_values_for_keys(child, keys))
            elif isinstance(child, list):
                for item in child:
                    found.extend(_nested_values_for_keys(item, keys))
    elif isinstance(value, list):
        for item in value:
            found.extend(_nested_values_for_keys(item, keys))
    return found


def _explicit_historical_universe(validation: dict[str, Any]) -> tuple[bool, str]:
    keys = {
        "survivorship_control",
        "survivorship_bias_control",
        "survivorship_status",
        "historical_universe",
        "pit_universe",
        "universe_history",
        "listing_history",
    }
    for value in _nested_values_for_keys(validation, keys):
        if isinstance(value, dict):
            candidate = value.get("status") or value.get("Current") or value.get("current") or value.get("mode")
        else:
            candidate = value
        text = str(candidate or "").strip().lower()
        if isinstance(value, bool) and value:
            return True, "explicit survivorship control flag"
        if text in {"pass", "controlled", "historical", "pit", "point_in_time", "point-in-time"}:
            return True, _safe_text(candidate)
    return False, "historical universe / delisting evidence not attached"


def _context(validation: dict[str, Any]) -> dict[str, Any]:
    return dict(
        validation.get("data_coverage_context")
        or dict(validation.get("input_evidence") or {}).get("data_coverage_context")
        or {}
    )


def _price_window_row(validation: dict[str, Any], context: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    weights = _normalize_symbol_weights(context.get("symbol_weights"))
    symbols = list(context.get("symbols") or weights)
    rows = [dict(row or {}) for row in _as_list(context.get("price_window_rows")) if isinstance(row, dict)]
    requested_start = _date_text(context.get("requested_start"))
    requested_end = _date_text(context.get("requested_end"))
    rows_by_symbol = {str(row.get("symbol") or "").upper(): row for row in rows}
    missing_symbols: list[str] = []
    gap_symbols: list[str] = []
    covered_weight = 0.0
    for symbol in symbols:
        row = rows_by_symbol.get(str(symbol).upper())
        weight = weights.get(str(symbol).upper(), 0.0) or (100.0 / len(symbols) if symbols else 0.0)
        if not row or (_optional_float(row.get("window_row_count")) or 0.0) <= 0:
            missing_symbols.append(str(symbol).upper())
            continue
        covered_weight += weight
        first_window = _date_text(row.get("first_window_date"))
        latest_window = _date_text(row.get("latest_window_date"))
        if requested_start and first_window and first_window > requested_start:
            gap_symbols.append(str(symbol).upper())
        if requested_end and latest_window and latest_window < requested_end:
            gap_symbols.append(str(symbol).upper())
    covered_weight = round(min(100.0, covered_weight), 4)
    if context.get("price_window_error"):
        status = "NEEDS_INPUT"
        evidence = context.get("price_window_error")
    elif not symbols or not rows:
        status = "NEEDS_INPUT"
        evidence = "price window rows missing"
    elif missing_symbols:
        status = "NEEDS_INPUT" if covered_weight < 80.0 else "REVIEW"
        evidence = f"missing={', '.join(missing_symbols[:6])}"
    elif gap_symbols:
        status = "REVIEW"
        evidence = f"window gaps={', '.join(sorted(set(gap_symbols))[:6])}"
    else:
        status = "PASS"
        evidence = "all requested symbols have DB price rows in window"
    metrics = {
        "symbol_count": len(symbols),
        "covered_weight": covered_weight,
        "missing_symbols": missing_symbols,
        "gap_symbols": sorted(set(gap_symbols)),
    }
    return _row(
        criteria="Price DB window coverage",
        status=status,
        current=f"{covered_weight:.1f}% / symbols={len(symbols)}",
        evidence=evidence,
        next_action="missing price symbols or window gaps를 DB price ingestion으로 보강합니다." if status != "PASS" else "추가 조치 없음",
        meaning="요청 검증 기간에 필요한 가격 row가 DB에 존재하는지 확인합니다.",
    ), metrics


def _provider_snapshot_row(validation: dict[str, Any]) -> dict[str, Any]:
    rows = [
        dict(row or {})
        for row in _as_list(validation.get("provider_coverage_display_rows") or dict(validation.get("provider_coverage") or {}).get("display_rows"))
        if isinstance(row, dict)
    ]
    statuses = [_status(row.get("Diagnostic Status") or row.get("Status") or row.get("Coverage")) for row in rows]
    freshness = {str(row.get("Freshness") or "").strip().lower() for row in rows}
    if not rows:
        status = "NEEDS_INPUT"
        evidence = "provider coverage display rows missing"
    elif "BLOCKED" in statuses:
        status = "BLOCKED"
        evidence = "provider coverage blocked"
    elif "NEEDS_INPUT" in statuses:
        status = "NEEDS_INPUT"
        evidence = "provider snapshot missing"
    elif "REVIEW" in statuses or freshness.intersection({"stale", "unknown", "not_run"}):
        status = "REVIEW"
        evidence = f"freshness={', '.join(sorted(item for item in freshness if item)) or '-'}"
    else:
        status = "PASS"
        evidence = f"{len(rows)} provider areas"
    return _row(
        criteria="Provider snapshot freshness",
        status=status,
        current=", ".join(sorted(set(statuses))) or "NOT_RUN",
        evidence=evidence,
        next_action="provider / holdings / exposure / macro snapshot freshness를 보강합니다." if status != "PASS" else "추가 조치 없음",
        meaning="DB-backed provider snapshot이 검증 기준일에 충분히 가까운지 확인합니다.",
    )


def _pit_window_row(validation: dict[str, Any], price_status: str) -> dict[str, Any]:
    curve_evidence = dict(validation.get("curve_evidence") or {})
    provenance = dict(curve_evidence.get("curve_provenance") or {})
    period = dict(curve_evidence.get("period_coverage") or provenance.get("period_coverage") or {})
    runtime_status = _status(provenance.get("runtime_recheck_status") or dict(curve_evidence.get("replay_attempt") or {}).get("status"))
    period_status = _status(provenance.get("period_coverage_status") or period.get("status"))
    source = _safe_text(curve_evidence.get("portfolio_curve_source") or provenance.get("portfolio_curve_source"), "unavailable")
    if price_status in {"BLOCKED", "NEEDS_INPUT"} or runtime_status == "NEEDS_INPUT" or period_status == "NEEDS_INPUT":
        status = "NEEDS_INPUT"
    elif runtime_status == "BLOCKED" or period_status == "BLOCKED":
        status = "BLOCKED"
    elif price_status == "PASS" and runtime_status == "PASS" and period_status == "PASS" and "runtime" in source.lower():
        status = "PASS"
    else:
        status = "REVIEW"
    return _row(
        criteria="PIT price window coverage",
        status=status,
        current=f"{source} / price={price_status} / replay={runtime_status} / period={period_status}",
        evidence=provenance.get("runtime_recheck_mode") or provenance.get("runtime_recheck_mode_label") or "curve provenance",
        next_action="runtime replay와 DB price window evidence를 같은 기간 기준으로 보강합니다." if status != "PASS" else "추가 조치 없음",
        meaning="검증 기간의 가격 row와 runtime replay가 look-ahead 없이 같은 기간을 읽는지 확인합니다.",
    )


def _lifecycle_row_covers_requested_period(row: dict[str, Any], *, start: str | None, end: str | None) -> bool:
    first_seen = _date_text(row.get("first_seen_date"))
    last_seen = _date_text(row.get("last_seen_date"))
    if not start or not end:
        return False
    if not first_seen or first_seen > start:
        return False
    if last_seen and last_seen < end:
        return False
    listing_status = str(row.get("listing_status") or "").strip().lower()
    coverage_status = str(row.get("coverage_status") or "").strip().lower()
    if listing_status in {"error", "unknown", "not_found"}:
        return False
    if coverage_status != "actual":
        return False
    return str(row.get("source_type") or "").strip().lower() in _HISTORICAL_LIFECYCLE_SOURCE_TYPES


def _lifecycle_category(row: dict[str, Any]) -> str:
    source = str(row.get("source") or "").strip().lower()
    source_type = str(row.get("source_type") or "").strip().lower()
    coverage_status = str(row.get("coverage_status") or "").strip().lower()
    if source == _SEC_IDENTITY_SOURCE:
        return "identity_crosscheck"
    if source_type == "current_listing_snapshot":
        return "current_snapshot"
    if source_type == "computed_from_snapshots" and coverage_status != "actual":
        return "computed_partial"
    if source_type == "delisting_feed" and coverage_status == "actual":
        return "delisting_actual"
    if source_type == "historical_listing" and coverage_status == "actual":
        return "historical_actual"
    if source_type in _HISTORICAL_LIFECYCLE_SOURCE_TYPES and coverage_status == "actual":
        return "actual_other"
    if coverage_status in {"partial", "bridge", "proxy"}:
        return "partial_other"
    if coverage_status in {"missing", "error"}:
        return "unusable"
    return "unknown"


def _symbol_preview(symbols: list[str], *, limit: int = 6) -> str:
    clean = [str(symbol or "").upper() for symbol in symbols if str(symbol or "").strip()]
    if not clean:
        return "-"
    suffix = "" if len(clean) <= limit else f"+{len(clean) - limit}"
    return ",".join(clean[:limit]) + suffix


def _symbol_lifecycle_evidence(context: dict[str, Any]) -> dict[str, Any]:
    symbols = [str(symbol or "").upper() for symbol in list(context.get("symbols") or []) if str(symbol or "").strip()]
    rows = [dict(row or {}) for row in _as_list(context.get("symbol_lifecycle_rows")) if isinstance(row, dict)]
    requested_start = _date_text(context.get("requested_start"))
    requested_end = _date_text(context.get("requested_end"))
    if context.get("symbol_lifecycle_error"):
        return {
            "status": "NEEDS_INPUT",
            "current": f"lifecycle error / symbols={len(symbols)}",
            "evidence": context.get("symbol_lifecycle_error"),
            "covered_symbols": [],
            "partial_symbols": [],
            "missing_symbols": symbols,
            "actual_symbols": [],
            "actual_noncovering_symbols": [],
            "current_snapshot_symbols": [],
            "identity_crosscheck_symbols": [],
            "computed_partial_symbols": [],
            "delisting_actual_symbols": [],
            "row_counts_by_category": {},
        }
    if not symbols:
        return {
            "status": "NEEDS_INPUT",
            "current": "symbols=0",
            "evidence": "requested symbols missing",
            "covered_symbols": [],
            "partial_symbols": [],
            "missing_symbols": [],
            "actual_symbols": [],
            "actual_noncovering_symbols": [],
            "current_snapshot_symbols": [],
            "identity_crosscheck_symbols": [],
            "computed_partial_symbols": [],
            "delisting_actual_symbols": [],
            "row_counts_by_category": {},
        }
    rows_by_symbol: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        symbol = str(row.get("symbol") or "").upper()
        if symbol:
            rows_by_symbol.setdefault(symbol, []).append(row)
    covered_symbols: list[str] = []
    partial_symbols: list[str] = []
    missing_symbols: list[str] = []
    actual_symbols: set[str] = set()
    actual_noncovering_symbols: set[str] = set()
    current_snapshot_symbols: set[str] = set()
    identity_crosscheck_symbols: set[str] = set()
    computed_partial_symbols: set[str] = set()
    delisting_actual_symbols: set[str] = set()
    row_counts_by_category: dict[str, int] = {}
    evidence_sources: set[str] = set()
    for symbol in symbols:
        candidates = rows_by_symbol.get(symbol) or []
        for candidate in candidates:
            source_type = str(candidate.get("source_type") or "").strip().lower()
            event_type = str(candidate.get("event_type") or "").strip().lower()
            source = str(candidate.get("source") or "").strip()
            category = _lifecycle_category(candidate)
            row_counts_by_category[category] = row_counts_by_category.get(category, 0) + 1
            if category in {"historical_actual", "delisting_actual", "actual_other"}:
                actual_symbols.add(symbol)
            if category == "current_snapshot":
                current_snapshot_symbols.add(symbol)
            elif category == "identity_crosscheck":
                identity_crosscheck_symbols.add(symbol)
            elif category == "computed_partial":
                computed_partial_symbols.add(symbol)
            elif category == "delisting_actual":
                delisting_actual_symbols.add(symbol)
            if source_type:
                event_label = f":{event_type}" if event_type else ""
                coverage_label = str(candidate.get("coverage_status") or "").strip().lower()
                evidence_sources.add(f"{source_type}{event_label}:{coverage_label or '-'}:{source or '-'}")
        has_covering_row = any(
            _lifecycle_row_covers_requested_period(candidate, start=requested_start, end=requested_end)
            for candidate in candidates
        )
        if has_covering_row:
            covered_symbols.append(symbol)
        elif candidates:
            partial_symbols.append(symbol)
        else:
            missing_symbols.append(symbol)
        if candidates and not has_covering_row and symbol in actual_symbols:
            actual_noncovering_symbols.add(symbol)
    actual_symbols_list = sorted(actual_symbols)
    actual_noncovering_list = sorted(actual_noncovering_symbols)
    current_snapshot_list = sorted(current_snapshot_symbols)
    identity_crosscheck_list = sorted(identity_crosscheck_symbols)
    computed_partial_list = sorted(computed_partial_symbols)
    delisting_actual_list = sorted(delisting_actual_symbols)
    source_mix = ", ".join(sorted(evidence_sources)[:6]) or "-"
    if len(covered_symbols) == len(symbols):
        status = "PASS"
        evidence = f"actual_covering={_symbol_preview(covered_symbols)} / sources={source_mix}"
    elif rows:
        status = "REVIEW"
        evidence = (
            f"partial={_symbol_preview(partial_symbols)} / "
            f"missing={_symbol_preview(missing_symbols)} / "
            f"actual_noncovering={_symbol_preview(actual_noncovering_list)} / "
            f"current_snapshot={_symbol_preview(current_snapshot_list)} / "
            f"sec_identity={_symbol_preview(identity_crosscheck_list)} / "
            f"computed_partial={_symbol_preview(computed_partial_list)} / "
            f"delisting_actual={_symbol_preview(delisting_actual_list)}"
        )
    else:
        status = "NEEDS_INPUT"
        evidence = "symbol lifecycle rows missing"
    return {
        "status": status,
        "current": (
            f"covered={len(covered_symbols)} / partial={len(partial_symbols)} / missing={len(missing_symbols)} / "
            f"actual={len(actual_symbols_list)} / current={len(current_snapshot_list)} / "
            f"sec={len(identity_crosscheck_list)} / computed={len(computed_partial_list)}"
        ),
        "evidence": evidence,
        "covered_symbols": covered_symbols,
        "partial_symbols": partial_symbols,
        "missing_symbols": missing_symbols,
        "actual_symbols": actual_symbols_list,
        "actual_noncovering_symbols": actual_noncovering_list,
        "current_snapshot_symbols": current_snapshot_list,
        "identity_crosscheck_symbols": identity_crosscheck_list,
        "computed_partial_symbols": computed_partial_list,
        "delisting_actual_symbols": delisting_actual_list,
        "row_counts_by_category": dict(sorted(row_counts_by_category.items())),
        "source_mix": source_mix,
    }


def _universe_listing_row(validation: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    historical, historical_evidence = _explicit_historical_universe(validation)
    lifecycle = _symbol_lifecycle_evidence(context)
    rows = [dict(row or {}) for row in _as_list(context.get("asset_profile_rows")) if isinstance(row, dict)]
    symbols = list(context.get("symbols") or [])
    profile_symbols = {str(row.get("symbol") or "").upper() for row in rows}
    missing = [symbol for symbol in symbols if str(symbol).upper() not in profile_symbols]
    statuses = {str(row.get("status") or "").strip().lower() for row in rows}
    if historical:
        status = "PASS"
        evidence = historical_evidence
    elif lifecycle["status"] == "PASS":
        status = "PASS"
        evidence = lifecycle["evidence"]
    elif lifecycle["status"] == "REVIEW":
        status = "REVIEW"
        evidence = lifecycle["evidence"]
    elif context.get("asset_profile_error"):
        status = "NEEDS_INPUT"
        evidence = context.get("asset_profile_error")
    elif not rows:
        status = "NEEDS_INPUT"
        evidence = "asset profile rows missing"
    elif missing:
        status = "REVIEW"
        evidence = f"missing profile={', '.join(missing[:6])}"
    elif statuses.intersection({"delisted", "not_found", "error"}):
        status = "REVIEW"
        evidence = f"profile statuses={', '.join(sorted(statuses))}"
    else:
        status = "REVIEW"
        evidence = "current listing/profile rows found, historical membership not proven"
    return _row(
        criteria="Universe / listing evidence",
        status=status,
        current=f"profiles={len(rows)} / lifecycle={lifecycle['current']} / symbols={len(symbols)}",
        evidence=evidence,
        next_action="historical universe membership 또는 listing history evidence를 보강합니다." if status != "PASS" else "추가 조치 없음",
        meaning="검증 universe가 현재 생존 종목만으로 과거를 재구성하지 않는지 확인합니다.",
    )


def _survivorship_row(validation: dict[str, Any], context: dict[str, Any], universe_status: str) -> dict[str, Any]:
    historical, evidence = _explicit_historical_universe(validation)
    lifecycle = _symbol_lifecycle_evidence(context)
    if historical:
        status = "PASS"
    elif lifecycle["status"] == "PASS":
        status = "PASS"
        evidence = lifecycle["evidence"]
    elif universe_status == "NEEDS_INPUT":
        status = "NEEDS_INPUT"
        evidence = lifecycle["evidence"]
    else:
        status = "REVIEW"
        evidence = lifecycle["evidence"]
    return _row(
        criteria="Survivorship / delisting control",
        status=status,
        current=evidence if status == "PASS" else f"not proven / {lifecycle['current']}",
        evidence=evidence,
        next_action="historical universe / delisting 기준을 별도 DB evidence로 보강합니다." if status != "PASS" else "추가 조치 없음",
        meaning="과거에 사라진 종목을 배제해 성과가 과대평가되는 위험을 확인합니다.",
    )


def _execution_boundary_row() -> dict[str, Any]:
    return _row(
        criteria="Data storage boundary",
        status="PASS",
        current="read-only audit / compact evidence only",
        evidence="db_write=False / registry_write=False / memo_persistence=False",
        next_action="추가 조치 없음",
        meaning="Data Coverage Audit은 DB loader 결과를 읽지만 새 workflow 저장소나 사용자 메모를 만들지 않습니다.",
    )


def _route_from_rows(rows: list[dict[str, Any]]) -> str:
    statuses = {str(row.get("Status") or "") for row in rows}
    if "BLOCKED" in statuses:
        return DATA_COVERAGE_BLOCKED
    if "NEEDS_INPUT" in statuses:
        return DATA_COVERAGE_NEEDS_INPUT
    if "REVIEW" in statuses:
        return DATA_COVERAGE_REVIEW
    return DATA_COVERAGE_READY


def build_data_coverage_audit(validation: dict[str, Any]) -> dict[str, Any]:
    """Summarize DB-backed data coverage evidence without adding persistence."""

    validation = dict(validation or {})
    context = _context(validation)
    price_row, price_metrics = _price_window_row(validation, context)
    provider_row = _provider_snapshot_row(validation)
    pit_row = _pit_window_row(validation, str(price_row.get("Status") or "NEEDS_INPUT"))
    universe_row = _universe_listing_row(validation, context)
    lifecycle_evidence = _symbol_lifecycle_evidence(context)
    survivorship_row = _survivorship_row(validation, context, str(universe_row.get("Status") or "NEEDS_INPUT"))
    rows = [
        price_row,
        provider_row,
        pit_row,
        universe_row,
        survivorship_row,
        _execution_boundary_row(),
    ]
    route = _route_from_rows(rows)
    status_counts = {
        status: sum(1 for row in rows if row.get("Status") == status)
        for status in _STATUS_RANK
    }
    if route == DATA_COVERAGE_READY:
        conclusion = "Data coverage audit 기준으로 즉시 보강이 필요한 공백이 없습니다."
        next_action = "Final Review에서 gate policy와 operator 판단을 함께 확인합니다."
    elif route == DATA_COVERAGE_BLOCKED:
        conclusion = "Data coverage audit에서 차단 항목이 발견됐습니다."
        next_action = "BLOCKED 항목을 먼저 해소한 뒤 최종 선택 판단을 진행합니다."
    elif route == DATA_COVERAGE_NEEDS_INPUT:
        conclusion = "PIT / price / provider / universe coverage 판단을 위해 추가 DB evidence가 필요합니다."
        next_action = "DB price ingestion, provider snapshot, historical universe evidence를 우선 보강합니다."
    else:
        conclusion = "DB coverage 근거는 일부 확인됐지만 REVIEW 항목이 남아 있습니다."
        next_action = "REVIEW 항목을 최종 판단 사유에 명시하거나 evidence를 보강합니다."
    return {
        "schema_version": DATA_COVERAGE_AUDIT_SCHEMA_VERSION,
        "route": route,
        "route_label": DATA_COVERAGE_ROUTE_LABELS.get(route, route),
        "overall_status": route.replace("DATA_COVERAGE_", ""),
        "conclusion": conclusion,
        "next_action": next_action,
        "rows": rows,
        "metrics": {
            "ready_rows": status_counts["PASS"],
            "total_rows": len(rows),
            "pass": status_counts["PASS"],
            "review": status_counts["REVIEW"],
            "needs_input": status_counts["NEEDS_INPUT"],
            "blocked": status_counts["BLOCKED"],
            "symbol_count": price_metrics.get("symbol_count", 0),
            "price_covered_weight": price_metrics.get("covered_weight", 0.0),
            "missing_price_symbols": list(price_metrics.get("missing_symbols") or []),
            "lifecycle_covered_symbols": list(lifecycle_evidence.get("covered_symbols") or []),
            "lifecycle_partial_symbols": list(lifecycle_evidence.get("partial_symbols") or []),
            "lifecycle_missing_symbols": list(lifecycle_evidence.get("missing_symbols") or []),
            "lifecycle_actual_symbols": list(lifecycle_evidence.get("actual_symbols") or []),
            "lifecycle_actual_noncovering_symbols": list(
                lifecycle_evidence.get("actual_noncovering_symbols") or []
            ),
            "lifecycle_current_snapshot_symbols": list(lifecycle_evidence.get("current_snapshot_symbols") or []),
            "lifecycle_identity_crosscheck_symbols": list(
                lifecycle_evidence.get("identity_crosscheck_symbols") or []
            ),
            "lifecycle_computed_partial_symbols": list(lifecycle_evidence.get("computed_partial_symbols") or []),
            "lifecycle_delisting_actual_symbols": list(lifecycle_evidence.get("delisting_actual_symbols") or []),
            "lifecycle_row_counts_by_category": dict(lifecycle_evidence.get("row_counts_by_category") or {}),
        },
        "execution_boundary": {
            "write_policy": "read_only_data_coverage_audit",
            "db_write": False,
            "registry_write": False,
            "memo_persistence": False,
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
        },
    }


__all__ = [
    "DATA_COVERAGE_AUDIT_SCHEMA_VERSION",
    "DATA_COVERAGE_CONTEXT_SCHEMA_VERSION",
    "DATA_COVERAGE_READY",
    "DATA_COVERAGE_REVIEW",
    "DATA_COVERAGE_NEEDS_INPUT",
    "DATA_COVERAGE_BLOCKED",
    "build_db_data_coverage_context",
    "build_data_coverage_audit",
]
