from __future__ import annotations

from collections.abc import Iterable
from datetime import date
from typing import Any

import pandas as pd

from finance.data.data import probe_ohlcv_provider
from finance.loaders import (
    load_asset_profile_status_summary,
    load_latest_market_date,
    load_price_freshness_summary,
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
