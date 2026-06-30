from __future__ import annotations

from collections.abc import Iterable
from datetime import date
from typing import Any

import pandas as pd

from finance.data.data import probe_ohlcv_provider
from finance.data.financial_statements import inspect_financial_statement_source
from finance.data.market_intelligence import (
    load_market_cap_universe_members,
    load_market_universe_members,
    load_nasdaq_symbol_directory_universe_members,
)
from finance.loaders import (
    load_asset_profile_status_summary,
    load_latest_market_date,
    load_price_freshness_summary,
    load_statement_coverage_summary,
    load_statement_shadow_coverage_summary,
)

from .ingestion_jobs import parse_symbols, split_valid_invalid_symbols


def _normalize_end(value: str | date | None) -> pd.Timestamp:
    if value is None:
        return pd.Timestamp.today().normalize()
    return pd.to_datetime(value).normalize()


def _classify_stale_symbol(
    *,
    symbol: str,
    db_latest: pd.Timestamp | None,
    target_end: pd.Timestamp,
    provider_probe: dict[str, Any],
    profile_row: dict[str, Any] | None,
) -> tuple[str, str, str]:
    provider_latest_raw = provider_probe.get("latest_provider_date")
    provider_latest = pd.to_datetime(provider_latest_raw).normalize() if provider_latest_raw else None
    probe_status = str(provider_probe.get("probe_status") or "")
    rate_limit_hit = bool(provider_probe.get("rate_limit_hit"))
    any_data = bool(provider_probe.get("any_data"))

    profile_row = profile_row or {}
    profile_status = str(profile_row.get("status") or "").strip().lower()
    delisted_at = profile_row.get("delisted_at")

    db_is_current = db_latest is not None and pd.notna(db_latest) and db_latest.normalize() >= target_end

    if db_is_current:
        return (
            "up_to_date_in_db",
            "No action needed.",
            "DB already has daily prices through the effective trading end.",
        )

    if rate_limit_hit and not any_data:
        return (
            "rate_limited_during_probe",
            "Retry diagnosis later. Provider probe itself hit a rate limit.",
            "The provider probe could not gather reliable evidence because rate limiting occurred before usable data was returned.",
        )

    if provider_latest is not None and provider_latest >= target_end:
        return (
            "local_ingestion_gap",
            "Run targeted Daily Market Update for this symbol.",
            "Provider can still return fresh daily rows through the effective trading end, but DB is behind.",
        )

    if (
        provider_latest is not None
        and db_latest is not None
        and pd.notna(db_latest)
        and provider_latest > db_latest.normalize()
        and provider_latest < target_end
    ):
        return (
            "local_ingestion_gap_partial",
            "Run targeted Daily Market Update. Provider has newer rows than DB, even though it is still behind the market end.",
            "DB is stale and provider has at least some newer rows available.",
        )

    if profile_status in {"delisted", "not_found"} or pd.notna(delisted_at):
        return (
            "likely_delisted_or_symbol_changed",
            "Treat this as a likely symbol-status issue first. Retry ingestion is not the default next step.",
            "Asset profile already marks this symbol as unavailable, delisted, or otherwise not active.",
        )

    if profile_status == "error":
        return (
            "asset_profile_error",
            "Run Metadata Refresh, then re-check this symbol.",
            "Asset profile metadata is itself in an error state, so symbol-status interpretation is weaker.",
        )

    if probe_status == "no_data":
        return (
            "provider_source_gap_or_symbol_issue",
            "Provider did not return usable rows. Retry later, and if it persists inspect symbol mapping or corporate action history.",
            "The DB is stale and the provider probe also returned no usable data.",
        )

    if provider_latest is not None and provider_latest <= target_end:
        return (
            "provider_source_gap",
            "Provider is not offering newer rows than the DB. Retry later; if this persists, treat it as a provider/symbol issue.",
            "The provider probe does return data, but not newer data through the effective trading end.",
        )

    if db_latest is None or pd.isna(db_latest):
        return (
            "missing_price_rows",
            "DB has no usable daily price rows for this symbol. Use provider probe and targeted refresh to decide the next step.",
            "There are no daily price rows in DB for this symbol at the requested timeframe.",
        )

    return (
        "inconclusive",
        "Evidence is mixed. Re-run the diagnosis later or inspect the symbol manually.",
        "The available DB, provider, and asset-profile signals do not clearly separate local ingestion, provider gap, or symbol-status issues.",
    )


def _build_targeted_daily_payload(
    *,
    rows: list[dict[str, Any]],
    target_end: pd.Timestamp,
) -> dict[str, Any] | None:
    local_gap_symbols = [
        row["symbol"]
        for row in rows
        if row.get("diagnosis") in {"local_ingestion_gap", "local_ingestion_gap_partial"}
    ]
    if not local_gap_symbols:
        return None

    refresh_start_candidates: list[pd.Timestamp] = []
    fallback_start = (target_end - pd.Timedelta(days=30)).normalize()
    for row in rows:
        if row.get("symbol") not in local_gap_symbols:
            continue
        db_latest_raw = row.get("db_latest")
        if db_latest_raw:
            db_latest = pd.to_datetime(db_latest_raw, errors="coerce")
            if pd.notna(db_latest):
                refresh_start_candidates.append((db_latest.normalize() - pd.Timedelta(days=7)).normalize())
            else:
                refresh_start_candidates.append(fallback_start)
        else:
            refresh_start_candidates.append(fallback_start)

    refresh_start = min(refresh_start_candidates) if refresh_start_candidates else fallback_start
    symbols_csv = ",".join(local_gap_symbols)
    payload_block = (
        f"symbols={symbols_csv}\n"
        f"start={refresh_start.strftime('%Y-%m-%d')}\n"
        f"end={target_end.strftime('%Y-%m-%d')}\n"
        "period=1mo\n"
        "interval=1d"
    )
    return {
        "symbols": local_gap_symbols,
        "symbols_csv": symbols_csv,
        "start": refresh_start.strftime("%Y-%m-%d"),
        "end": target_end.strftime("%Y-%m-%d"),
        "payload_block": payload_block,
    }


def inspect_price_stale_symbols(
    symbols: str | Iterable[str] | None,
    *,
    end: str | date | None = None,
    timeframe: str = "1d",
    provider_probe_periods: tuple[str, ...] = ("5d", "1mo", "3mo"),
    max_symbols: int = 20,
) -> dict[str, Any]:
    parsed, invalid_symbols = split_valid_invalid_symbols(symbols)
    if not parsed:
        return {
            "status": "error",
            "message": "No valid symbols provided for price stale diagnosis.",
            "details": {"invalid_symbols": invalid_symbols, "rows": [], "probe_rows": []},
        }

    if len(parsed) > max_symbols:
        return {
            "status": "error",
            "message": f"Price stale diagnosis is limited to {max_symbols} symbols at a time.",
            "details": {
                "invalid_symbols": invalid_symbols,
                "requested_count": len(parsed),
                "max_symbols": max_symbols,
                "rows": [],
                "probe_rows": [],
            },
        }

    end_ts = _normalize_end(end)
    effective_end_ts = load_latest_market_date(end=end_ts.strftime("%Y-%m-%d"), timeframe=timeframe)
    if effective_end_ts is None or pd.isna(effective_end_ts):
        effective_end_ts = end_ts
    target_end = effective_end_ts.normalize()

    freshness_df = load_price_freshness_summary(parsed, end=end_ts.strftime("%Y-%m-%d"), timeframe=timeframe)
    freshness_map = {
        str(row["symbol"]).upper(): row
        for _, row in freshness_df.iterrows()
        if row.get("symbol") is not None
    } if not freshness_df.empty else {}

    profile_df = load_asset_profile_status_summary(parsed)
    profile_map = {
        str(row["symbol"]).upper(): row.to_dict()
        for _, row in profile_df.iterrows()
        if row.get("symbol") is not None
    } if not profile_df.empty else {}

    diagnosis_rows: list[dict[str, Any]] = []
    probe_rows: list[dict[str, Any]] = []
    diagnosis_counts: dict[str, int] = {}

    for symbol in parsed:
        db_row = freshness_map.get(symbol)
        db_latest = None
        db_row_count = None
        if db_row is not None:
            db_latest = pd.to_datetime(db_row.get("latest_date"), errors="coerce")
            db_row_count = int(db_row.get("row_count") or 0)

        provider_probe = probe_ohlcv_provider(
            symbol,
            periods=provider_probe_periods,
            interval=timeframe,  # diagnosis is aligned to the daily preflight path
        )
        profile_row = profile_map.get(symbol) or {}

        diagnosis, recommended_action, note = _classify_stale_symbol(
            symbol=symbol,
            db_latest=db_latest,
            target_end=target_end,
            provider_probe=provider_probe,
            profile_row=profile_row,
        )
        diagnosis_counts[diagnosis] = diagnosis_counts.get(diagnosis, 0) + 1

        provider_latest_raw = provider_probe.get("latest_provider_date")
        provider_latest = pd.to_datetime(provider_latest_raw, errors="coerce") if provider_latest_raw else None
        db_lag_days = (
            int((target_end - db_latest.normalize()).days)
            if db_latest is not None and pd.notna(db_latest)
            else None
        )
        provider_lag_days = (
            int((target_end - provider_latest.normalize()).days)
            if provider_latest is not None and pd.notna(provider_latest)
            else None
        )

        diagnosis_rows.append(
            {
                "symbol": symbol,
                "db_latest": db_latest.normalize().strftime("%Y-%m-%d") if db_latest is not None and pd.notna(db_latest) else None,
                "db_lag_days": db_lag_days,
                "db_row_count": db_row_count,
                "provider_latest": provider_latest.normalize().strftime("%Y-%m-%d") if provider_latest is not None and pd.notna(provider_latest) else None,
                "provider_lag_days": provider_lag_days,
                "probe_status": provider_probe.get("probe_status"),
                "profile_status": profile_row.get("status"),
                "delisted_at": (
                    pd.to_datetime(profile_row.get("delisted_at"), errors="coerce").strftime("%Y-%m-%d")
                    if profile_row.get("delisted_at") is not None and pd.notna(pd.to_datetime(profile_row.get("delisted_at"), errors="coerce"))
                    else None
                ),
                "diagnosis": diagnosis,
                "recommended_action": recommended_action,
                "note": note,
            }
        )

        for probe in provider_probe.get("probes") or []:
            probe_rows.append(
                {
                    "symbol": symbol,
                    "period": probe.get("period"),
                    "row_count": probe.get("row_count"),
                    "latest_date": probe.get("latest_date"),
                    "rate_limit_hit": probe.get("rate_limit_hit"),
                    "provider_no_data_hit": probe.get("provider_no_data_hit"),
                    "provider_output_excerpt": probe.get("provider_output_excerpt"),
                }
            )

    targeted_payload = _build_targeted_daily_payload(rows=diagnosis_rows, target_end=target_end)

    if any(row.get("diagnosis") not in {"up_to_date_in_db"} for row in diagnosis_rows):
        status = "warning"
        message = (
            f"Diagnosed {len(diagnosis_rows)} symbol(s) against effective trading end "
            f"`{target_end.strftime('%Y-%m-%d')}`. Review the classification table for likely cause and action."
        )
    else:
        status = "ok"
        message = f"All diagnosed symbols are already current through `{target_end.strftime('%Y-%m-%d')}` in DB."

    return {
        "status": status,
        "message": message,
        "details": {
            "requested_count": len(parsed),
            "invalid_symbols": invalid_symbols,
            "selected_end_date": end_ts.strftime("%Y-%m-%d"),
            "effective_end_date": target_end.strftime("%Y-%m-%d"),
            "timeframe": timeframe,
            "provider_probe_periods": list(provider_probe_periods),
            "diagnosis_counts": diagnosis_counts,
            "rows": diagnosis_rows,
            "probe_rows": probe_rows,
            "targeted_daily_market_payload": targeted_payload,
        },
    }


SUPPORTED_ANNUAL_FORMS = {"10-K", "10-K/A"}
SUPPORTED_QUARTERLY_FORMS = {"10-Q", "10-Q/A", "10-K", "10-K/A"}
FOREIGN_OR_NONSTANDARD_FORMS = {"20-F", "20-F/A", "6-K", "6-K/A", "40-F", "40-F/A"}
STATEMENT_UNIVERSE_LABELS = {
    "SP500": "S&P 500",
    "TOP1000": "Top 1000 by market cap",
    "TOP2000": "Top 2000 by market cap",
    "NASDAQ": "Nasdaq-listed current snapshot",
}


def _normalize_symbol_map(df: pd.DataFrame, key: str = "symbol") -> dict[str, dict[str, Any]]:
    if df.empty:
        return {}
    out: dict[str, dict[str, Any]] = {}
    for _, row in df.iterrows():
        symbol = str(row.get(key) or "").strip().upper()
        if not symbol:
            continue
        out[symbol] = row.to_dict()
    return out


def _build_statement_refresh_payload(symbols: list[str], freq: str) -> dict[str, Any] | None:
    if not symbols:
        return None
    symbols_csv = ",".join(symbols)
    return {
        "symbols": symbols,
        "symbols_csv": symbols_csv,
        "payload_block": (
            f"symbols={symbols_csv}\n"
            f"freq={freq}\n"
            "periods=0\n"
            f"period={freq}"
        ),
    }


def _build_statement_shadow_rebuild_payload(symbols: list[str], freq: str) -> dict[str, Any] | None:
    if not symbols:
        return None
    symbols_csv = ",".join(symbols)
    return {
        "symbols": symbols,
        "symbols_csv": symbols_csv,
        "payload_block": (
            f"symbols={symbols_csv}\n"
            f"freq={freq}"
        ),
    }


def _load_statement_coverage_universe_members(
    universe_code: str,
    *,
    universe_limit: int | None,
) -> tuple[str, str, list[dict[str, Any]]]:
    normalized = str(universe_code or "TOP1000").strip().upper()
    if normalized == "SP500":
        return normalized, "Current S&P 500 constituents", load_market_universe_members("SP500")
    if normalized == "NASDAQ":
        rows = load_nasdaq_symbol_directory_universe_members()
        limit = int(universe_limit or 0)
        return normalized, "Nasdaq-listed current snapshot", rows[:limit] if limit > 0 else rows

    if normalized not in {"TOP1000", "TOP2000"}:
        normalized = "TOP1000"
    default_limit = 2000 if normalized == "TOP2000" else 1000
    limit = int(universe_limit or default_limit)
    return (
        normalized,
        "Latest asset_profile.market_cap snapshot",
        load_market_cap_universe_members(normalized, universe_limit=limit),
    )


def _to_timestamp(value: Any) -> pd.Timestamp | None:
    ts = pd.to_datetime(value, errors="coerce")
    if pd.isna(ts):
        return None
    return ts.normalize()


def _is_recent_statement_period(value: Any, *, as_of_ts: pd.Timestamp, max_age_days: int) -> bool:
    ts = _to_timestamp(value)
    if ts is None:
        return False
    return int((as_of_ts - ts).days) <= max_age_days


def _classify_statement_universe_coverage_row(
    *,
    raw_row: dict[str, Any] | None,
    shadow_row: dict[str, Any] | None,
    profile_row: dict[str, Any] | None,
    as_of_ts: pd.Timestamp,
    max_annual_age_days: int,
) -> tuple[str, str, str]:
    raw_rows = int(raw_row.get("strict_rows") or 0) if raw_row else 0
    shadow_rows = int(shadow_row.get("shadow_rows") or 0) if shadow_row else 0
    shadow_recent = _is_recent_statement_period(
        shadow_row.get("max_period_end") if shadow_row else None,
        as_of_ts=as_of_ts,
        max_age_days=max_annual_age_days,
    )
    raw_recent = _is_recent_statement_period(
        raw_row.get("max_period_end") if raw_row else None,
        as_of_ts=as_of_ts,
        max_age_days=max_annual_age_days,
    )

    if shadow_rows > 0 and shadow_recent:
        return (
            "statement_shadow_available",
            "No immediate action.",
            "EDGAR statement shadow rows are present and recent enough for annual coverage QA.",
        )
    if shadow_rows > 0 and not shadow_recent:
        return (
            "statement_shadow_stale_no_recent_10k",
            "Run Statement Coverage Diagnosis, then targeted EDGAR annual refresh for stale symbols.",
            "Statement shadow rows exist, but the latest annual period is older than the freshness window.",
        )
    if raw_rows > 0 and not raw_recent:
        return (
            "raw_present_but_no_recent_10k",
            "Run Statement Coverage Diagnosis before deciding between refresh and exclusion.",
            "Strict raw statement rows exist, but the latest annual period is stale; this can mean no recent 10-K has been collected.",
        )
    if raw_rows > 0:
        return (
            "raw_present_shadow_missing",
            "Run Statement Shadow Rebuild for these symbols first.",
            "Strict raw EDGAR rows are already present, so a shadow rebuild is the fastest next action.",
        )

    profile_row = profile_row or {}
    country = str(profile_row.get("country") or "").strip().lower()
    if country and country not in {"united states", "usa", "us", "u.s.", "u.s.a."}:
        return (
            "non_us_issuer_or_foreign_form_expected",
            "Review whether this issuer belongs in strict annual US statement coverage.",
            "The current asset profile is non-US, so 20-F / 6-K / foreign-form structure may be expected.",
        )

    profile_status = str(profile_row.get("status") or "").strip().lower()
    if profile_status in {"delisted", "not_found", "error"}:
        return (
            "symbol_status_or_profile_issue",
            "Refresh or inspect asset profile / lifecycle evidence before rerunning EDGAR collection.",
            "Asset profile status weakens the statement-source interpretation.",
        )
    if not profile_row:
        return (
            "missing_profile_or_universe_metadata",
            "Refresh metadata, then rerun coverage QA.",
            "The symbol is in the selected universe but has no compact asset-profile row for source QA.",
        )

    return (
        "edgar_unavailable_or_cik_mapping_issue",
        "Run Statement Coverage Diagnosis on a small sample before targeted EDGAR annual refresh.",
        "No DB raw/shadow statement rows are present. The next read-only step is to separate unavailable EDGAR source from CIK/ticker mapping gaps.",
    )


def inspect_statement_universe_coverage(
    *,
    universe_code: str = "TOP1000",
    universe_limit: int | None = None,
    freq: str = "annual",
    as_of_date: str | date | None = None,
    max_annual_age_days: int = 800,
) -> dict[str, Any]:
    normalized_freq = str(freq or "annual").strip().lower()
    as_of_ts = _normalize_end(as_of_date)
    normalized_universe, coverage_basis, universe_rows = _load_statement_coverage_universe_members(
        universe_code,
        universe_limit=universe_limit,
    )
    symbols = []
    for row in universe_rows:
        symbol = str(row.get("symbol") or "").strip().upper()
        if symbol and symbol not in symbols:
            symbols.append(symbol)

    if not symbols:
        return {
            "status": "error",
            "message": f"No symbols resolved for {normalized_universe} statement universe coverage QA.",
            "details": {
                "universe_code": normalized_universe,
                "universe_label": STATEMENT_UNIVERSE_LABELS.get(normalized_universe, normalized_universe),
                "coverage_basis": coverage_basis,
                "universe_count": 0,
                "reason_counts": {},
                "rows": [],
                "next_actions": ["Refresh or inspect the selected universe source before statement QA."],
            },
        }

    raw_summary = load_statement_coverage_summary(symbols, freq=normalized_freq)
    shadow_summary = load_statement_shadow_coverage_summary(symbols, freq=normalized_freq)
    profile_summary = load_asset_profile_status_summary(symbols)
    raw_map = _normalize_symbol_map(raw_summary)
    shadow_map = _normalize_symbol_map(shadow_summary)
    profile_map = _normalize_symbol_map(profile_summary)
    universe_map = _normalize_symbol_map(pd.DataFrame(universe_rows)) if universe_rows else {}

    reason_counts: dict[str, int] = {}
    rows: list[dict[str, Any]] = []
    for symbol in symbols:
        raw_row = raw_map.get(symbol)
        shadow_row = shadow_map.get(symbol)
        profile_row = profile_map.get(symbol)
        reason, recommended_action, note = _classify_statement_universe_coverage_row(
            raw_row=raw_row,
            shadow_row=shadow_row,
            profile_row=profile_row,
            as_of_ts=as_of_ts,
            max_annual_age_days=max_annual_age_days,
        )
        reason_counts[reason] = reason_counts.get(reason, 0) + 1
        rows.append(
            {
                "symbol": symbol,
                "name": (universe_map.get(symbol) or {}).get("name"),
                "country": (profile_row or {}).get("country"),
                "profile_status": (profile_row or {}).get("status"),
                "raw_strict_rows": int(raw_row.get("strict_rows") or 0) if raw_row else 0,
                "raw_max_period_end": str(_to_timestamp(raw_row.get("max_period_end")).date()) if raw_row and _to_timestamp(raw_row.get("max_period_end")) is not None else None,
                "shadow_rows": int(shadow_row.get("shadow_rows") or 0) if shadow_row else 0,
                "shadow_max_period_end": str(_to_timestamp(shadow_row.get("max_period_end")).date()) if shadow_row and _to_timestamp(shadow_row.get("max_period_end")) is not None else None,
                "reason_group": reason,
                "recommended_action": recommended_action,
                "note": note,
            }
        )

    shadow_available = reason_counts.get("statement_shadow_available", 0)
    stale_shadow = reason_counts.get("statement_shadow_stale_no_recent_10k", 0)
    raw_available = sum(1 for row in rows if int(row.get("raw_strict_rows") or 0) > 0)
    missing_count = len(symbols) - shadow_available
    coverage_pct = round((shadow_available / len(symbols)) * 100, 2) if symbols else 0.0
    status = "ok" if missing_count == 0 else "warning"
    next_actions = [
        "Use Statement Coverage Diagnosis on sampled missing symbols before rerunning EDGAR annual refresh.",
        "Use Statement Shadow Rebuild for raw_present_shadow_missing symbols.",
        "Keep non-US / foreign-form and CIK mapping gaps as source QA decisions; do not use yfinance financial statements as primary fallback.",
    ]

    rows.sort(key=lambda item: (item["reason_group"] != "statement_shadow_available", item["reason_group"], item["symbol"]))
    return {
        "status": status,
        "message": (
            f"{STATEMENT_UNIVERSE_LABELS.get(normalized_universe, normalized_universe)} EDGAR annual coverage by universe: "
            f"{shadow_available}/{len(symbols)} symbols have recent statement shadow rows."
        ),
        "details": {
            "universe_code": normalized_universe,
            "universe_label": STATEMENT_UNIVERSE_LABELS.get(normalized_universe, normalized_universe),
            "coverage_basis": coverage_basis,
            "freq": normalized_freq,
            "as_of_date": as_of_ts.strftime("%Y-%m-%d"),
            "max_annual_age_days": max_annual_age_days,
            "universe_count": len(symbols),
            "universe_limit": universe_limit,
            "coverage": {
                "shadow_available_count": shadow_available,
                "shadow_stale_count": stale_shadow,
                "raw_available_count": raw_available,
                "missing_or_not_ready_count": missing_count,
                "shadow_coverage_pct": coverage_pct,
            },
            "reason_counts": reason_counts,
            "rows": rows,
            "next_actions": next_actions,
        },
    }


def _classify_statement_coverage_symbol(
    *,
    symbol: str,
    freq: str,
    raw_row: dict[str, Any] | None,
    shadow_row: dict[str, Any] | None,
    source_payload: dict[str, Any],
) -> tuple[str, str, str, list[str]]:
    raw_rows = int(raw_row.get("strict_rows") or 0) if raw_row else 0
    shadow_rows = int(shadow_row.get("shadow_rows") or 0) if shadow_row else 0
    fact_count = int(source_payload.get("statement_fact_count") or 0)
    filing_count = int(source_payload.get("filing_count") or 0)
    form_counts = dict(source_payload.get("form_counts") or {})
    forms = {str(form).upper() for form in form_counts.keys() if form}
    supported_forms = SUPPORTED_QUARTERLY_FORMS if str(freq) == "quarterly" else SUPPORTED_ANNUAL_FORMS
    supported_form_hits = sorted(forms & supported_forms)
    foreign_form_hits = sorted(forms & FOREIGN_OR_NONSTANDARD_FORMS)
    timing_inventory = dict(source_payload.get("timing_field_inventory") or {})
    facts_with_accession = int(timing_inventory.get("facts_with_accession") or 0)
    facts_with_unit = int(timing_inventory.get("facts_with_unit") or 0)
    facts_with_period_end = int(timing_inventory.get("facts_with_period_end") or 0)

    if shadow_rows > 0:
        return (
            "shadow_available",
            "추가 조치가 필요하지 않습니다.",
            "이 심볼은 이미 DB에 statement shadow coverage가 있습니다.",
            [
                "1. 이 심볼은 현재 복구 작업이 필요하지 않습니다.",
            ],
        )

    if raw_rows > 0 and shadow_rows == 0:
        return (
            "raw_present_shadow_missing",
            "먼저 `Statement Shadow Rebuild Only`를 실행하세요.",
            "DB에는 strict raw statement row가 이미 있으므로, EDGAR를 다시 호출하지 않고 shadow 테이블만 재생성하는 쪽이 더 빠른 복구 경로입니다.",
            [
                "1. 이 심볼과 빈도(freq)에 대해 `Statement Shadow Rebuild Only`를 실행합니다.",
                "2. 다시 `Statement Shadow Coverage Preview`를 확인합니다.",
                "3. 그래도 shadow가 비어 있으면 raw 재수집 반복보다 coverage-hardening 경로를 점검합니다.",
            ],
        )

    if fact_count == 0 and filing_count == 0:
        return (
            "source_empty_or_symbol_issue",
            "재수집부터 시작하지 말고, 먼저 심볼/source 유효성을 점검하세요.",
            "live EDGAR sample도 비어 있으므로 단순한 로컬 DB 누락만은 아닙니다. 이 심볼이 기대한 EDGAR issuer path에 제대로 매핑되지 않을 가능성이 있습니다.",
            [
                "1. 이 케이스는 일반적인 재수집 대상이 아니라 symbol/source 이슈로 먼저 봅니다.",
                "2. 이 심볼이 현재 universe에서 의도한 canonical input이 맞는지 확인합니다.",
                "3. 중요 심볼이라면 issuer mapping을 점검하고, 지원 여부가 정리될 때까지 strict coverage에서 제외하는 것도 검토합니다.",
            ],
        )

    if foreign_form_hits and not supported_form_hits:
        return (
            "foreign_or_nonstandard_form_structure",
            "재수집만으로는 해결될 가능성이 낮고, form-structure 지원 이슈로 보는 편이 맞습니다.",
            "source fact는 내려오지만 주된 form이 `20-F` / `6-K` 같은 foreign/non-standard 구조여서, 현재 strict path가 핵심으로 보는 `10-Q` / `10-K` 경로와 맞지 않습니다.",
            [
                "1. `Extended Statement Refresh`만 다시 돌린다고 해결된다고 가정하지 않습니다.",
                "2. foreign-form 지원을 추가할지, strict coverage에서 제외할지 파이프라인 차원의 결정을 합니다.",
                "3. 필요하면 해당 지원이 들어가기 전까지 strict quarterly universe 밖에 두는 것이 안전합니다.",
            ],
        )

    if fact_count > 0 and supported_form_hits and facts_with_accession > 0 and facts_with_unit > 0 and facts_with_period_end > 0:
        return (
            "source_present_raw_missing",
            "먼저 targeted `Extended Statement Refresh`를 실행하세요.",
            "live source에는 supported form 기반의 usable statement fact가 보이는데 DB에 strict raw row가 없습니다. 이런 경우가 targeted 재수집을 가장 먼저 시도할 만한 패턴입니다.",
            [
                "1. 이 심볼에 대해 `periods = 0`으로 targeted `Extended Statement Refresh`를 실행합니다.",
                "2. raw row는 생겼는데 shadow가 없으면 `Statement Shadow Rebuild Only`로 전환합니다.",
                "3. 그래도 raw row가 안 생기면 strict filtering rule이나 source-to-ledger normalization을 점검합니다.",
            ],
        )

    if fact_count > 0 and not supported_form_hits:
        return (
            "source_present_but_not_supported_for_current_mode",
            "일반적인 재수집 대상으로 보기에는 신뢰도가 낮습니다.",
            "source가 완전히 비어 있지는 않지만, 현재 strict mode가 기대하는 filing/form 조합으로 노출되지 않습니다.",
            [
                "1. 재수집은 선택 사항이지만 기본 우선 조치는 아닙니다.",
                "2. 이 심볼이 현재 strict mode와 다른 보고 구조를 갖는지 확인합니다.",
                "3. 새 form 지원을 의도적으로 추가하지 않는다면 strict coverage universe에서 제외하는 것도 검토합니다.",
            ],
        )

    return (
        "inconclusive_statement_coverage",
        "근거가 섞여 있습니다. 중요한 심볼이면 PIT inspection과 소규모 targeted refresh를 함께 보세요.",
        "source가 완전히 비어 있지는 않지만, 전형적인 raw-missing 복구 패턴에도 완전히 들어맞지는 않습니다.",
        [
            "1. 중요한 심볼이면 소규모 targeted `Extended Statement Refresh`를 한 번 시도합니다.",
            "2. 그래도 raw coverage가 없으면 source payload와 strict filtering path를 같이 점검합니다.",
            "3. 원인이 더 분명해질 때까지 strict coverage에서 제외하는 것도 검토합니다.",
        ],
    )


def inspect_statement_coverage_symbols(
    symbols: str | Iterable[str] | None,
    *,
    freq: str = "quarterly",
    sample_size: int = 2,
    max_symbols: int = 10,
) -> dict[str, Any]:
    parsed, invalid_symbols = split_valid_invalid_symbols(symbols)
    if not parsed:
        return {
            "status": "error",
            "message": "No valid symbols provided for statement coverage diagnosis.",
            "details": {"invalid_symbols": invalid_symbols, "rows": [], "source_rows": []},
        }

    if len(parsed) > max_symbols:
        return {
            "status": "error",
            "message": f"Statement coverage diagnosis is limited to {max_symbols} symbols at a time.",
            "details": {
                "invalid_symbols": invalid_symbols,
                "requested_count": len(parsed),
                "max_symbols": max_symbols,
                "rows": [],
                "source_rows": [],
            },
        }

    raw_summary = load_statement_coverage_summary(parsed, freq=freq)
    shadow_summary = load_statement_shadow_coverage_summary(parsed, freq=freq)
    raw_map = _normalize_symbol_map(raw_summary)
    shadow_map = _normalize_symbol_map(shadow_summary)

    diagnosis_rows: list[dict[str, Any]] = []
    source_rows: list[dict[str, Any]] = []
    diagnosis_counts: dict[str, int] = {}
    refresh_candidates: list[str] = []
    rebuild_candidates: list[str] = []

    for symbol in parsed:
        source_payload = inspect_financial_statement_source(symbol, sample_size=sample_size)
        raw_row = raw_map.get(symbol)
        shadow_row = shadow_map.get(symbol)
        diagnosis, recommended_action, note, stepwise_guidance = _classify_statement_coverage_symbol(
            symbol=symbol,
            freq=freq,
            raw_row=raw_row,
            shadow_row=shadow_row,
            source_payload=source_payload,
        )
        diagnosis_counts[diagnosis] = diagnosis_counts.get(diagnosis, 0) + 1
        if diagnosis == "source_present_raw_missing":
            refresh_candidates.append(symbol)
        if diagnosis == "raw_present_shadow_missing":
            rebuild_candidates.append(symbol)

        form_counts = dict(source_payload.get("form_counts") or {})
        dominant_forms = ", ".join(
            f"{form}:{count}" for form, count in sorted(form_counts.items(), key=lambda item: (-item[1], item[0]))[:3]
        )

        diagnosis_rows.append(
            {
                "symbol": symbol,
                "raw_strict_rows": int(raw_row.get("strict_rows") or 0) if raw_row else 0,
                "shadow_rows": int(shadow_row.get("shadow_rows") or 0) if shadow_row else 0,
                "source_fact_count": int(source_payload.get("statement_fact_count") or 0),
                "source_filing_count": int(source_payload.get("filing_count") or 0),
                "dominant_forms": dominant_forms or "-",
                "diagnosis": diagnosis,
                "recommended_action": recommended_action,
                "note": note,
                "stepwise_guidance": " | ".join(stepwise_guidance),
            }
        )

        source_rows.append(
            {
                "symbol": symbol,
                "statement_fact_count": int(source_payload.get("statement_fact_count") or 0),
                "filing_count": int(source_payload.get("filing_count") or 0),
                "form_counts": form_counts,
                "fiscal_period_counts": dict(source_payload.get("fiscal_period_counts") or {}),
                "timing_field_inventory": dict(source_payload.get("timing_field_inventory") or {}),
                "sample_filings": source_payload.get("sample_filings") or [],
                "sample_facts": source_payload.get("sample_facts") or [],
            }
        )

    refresh_payload = _build_statement_refresh_payload(refresh_candidates, freq)
    rebuild_payload = _build_statement_shadow_rebuild_payload(rebuild_candidates, freq)

    warning_diagnoses = {
        row["diagnosis"]
        for row in diagnosis_rows
        if row["diagnosis"] not in {"shadow_available"}
    }
    status = "warning" if warning_diagnoses else "ok"
    if status == "ok":
        message = "All diagnosed symbols already have statement coverage for the selected mode."
    else:
        message = (
            f"Diagnosed {len(diagnosis_rows)} symbol(s) for statement coverage recovery. "
            "Review the classification table to decide whether raw collection, shadow rebuild, or exclusion/support work is more appropriate."
        )

    return {
        "status": status,
        "message": message,
        "details": {
            "freq": freq,
            "requested_count": len(parsed),
            "invalid_symbols": invalid_symbols,
            "diagnosis_counts": diagnosis_counts,
            "rows": diagnosis_rows,
            "source_rows": source_rows,
            "extended_refresh_payload": refresh_payload,
            "shadow_rebuild_payload": rebuild_payload,
        },
    }
