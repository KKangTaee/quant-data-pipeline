from __future__ import annotations

from typing import Any

import pandas as pd

from finance.loaders import (
    load_etf_exposure_snapshot,
    load_etf_holdings_snapshot,
    load_etf_operability_snapshot,
    load_macro_snapshot,
)


PROVIDER_CONTEXT_SCHEMA_VERSION = 2
DEFAULT_PROVIDER_STALENESS_DAYS = 45
DEFAULT_MACRO_SERIES = ("VIXCLS", "T10Y3M", "BAA10Y")
SOURCE_TYPE_RANK = {
    "official": 3,
    "database_bridge": 2,
    "bridge": 2,
    "computed_proxy": 1,
    "proxy": 1,
}
ASSET_CLASS_BUCKETS = {
    "equity": "equity",
    "stock": "equity",
    "fixed income": "bond",
    "bond": "bond",
    "treasury": "bond",
    "cash": "cash",
    "money market": "cash",
    "gold": "gold",
    "commodity": "commodity",
    "commodities": "commodity",
}


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


def _first_optional_float(*values: Any) -> float | None:
    for value in values:
        numeric = _optional_float(value)
        if numeric is not None:
            return numeric
    return None


def _date_text(value: Any) -> str | None:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return pd.Timestamp(parsed).strftime("%Y-%m-%d")


def _analysis_date(as_of_date: str | None) -> pd.Timestamp | None:
    if as_of_date is None:
        return None
    parsed = pd.to_datetime(as_of_date, errors="coerce")
    if pd.isna(parsed):
        return None
    ts = pd.Timestamp(parsed)
    if ts.tzinfo is not None:
        ts = ts.tz_convert(None)
    return ts.normalize()


def _days_old(*, analysis_date: pd.Timestamp | None, snapshot_date: Any) -> int | None:
    if analysis_date is None:
        return None
    parsed = pd.to_datetime(snapshot_date, errors="coerce")
    if pd.isna(parsed):
        return None
    ts = pd.Timestamp(parsed)
    if ts.tzinfo is not None:
        ts = ts.tz_convert(None)
    return int((analysis_date - ts.normalize()).days)


def _compact_unique(values: Any, *, limit: int = 4) -> list[str]:
    out: list[str] = []
    for value in list(values or []):
        text = str(value or "").strip()
        if not text or text.lower() in {"nan", "none"} or text in out:
            continue
        out.append(text)
        if len(out) >= limit:
            break
    return out


def _range_text(values: Any) -> str:
    parsed = pd.to_datetime(pd.Series(list(values or [])), errors="coerce").dropna()
    if parsed.empty:
        return "-"
    dates = sorted(pd.Timestamp(value).strftime("%Y-%m-%d") for value in parsed)
    if dates[0] == dates[-1]:
        return dates[0]
    return f"{dates[0]}..{dates[-1]}"


def _best_source_type(values: Any) -> str:
    candidates = _compact_unique(values, limit=8)
    if not candidates:
        return "unknown"
    return sorted(candidates, key=lambda value: SOURCE_TYPE_RANK.get(value.lower(), 0), reverse=True)[0]


def _source_mix_label(source_type_weights: dict[str, float], sources: list[str]) -> str:
    if source_type_weights:
        return ", ".join(
            f"{source_type} {weight:.1f}%"
            for source_type, weight in sorted(source_type_weights.items(), key=lambda item: (-item[1], item[0]))
        )
    if sources:
        return ", ".join(sources)
    return "-"


def _pct_text(value: Any) -> str:
    numeric = _optional_float(value)
    if numeric is None:
        return "-"
    return f"{numeric * 100:.2f}%"


def _money_text(value: Any) -> str:
    numeric = _optional_float(value)
    if numeric is None:
        return "-"
    abs_value = abs(numeric)
    if abs_value >= 1_000_000_000:
        return f"${numeric / 1_000_000_000:.2f}B"
    if abs_value >= 1_000_000:
        return f"${numeric / 1_000_000:.1f}M"
    return f"${numeric:,.0f}"


def _first_text(*values: Any) -> str:
    for value in values:
        if value is None:
            continue
        try:
            if pd.isna(value):
                continue
        except Exception:
            pass
        text = str(value).strip()
        if text:
            return text
    return ""


def _normalize_symbol_weights(symbol_weights: dict[str, Any] | None) -> dict[str, float]:
    weights: dict[str, float] = {}
    for symbol, weight in dict(symbol_weights or {}).items():
        clean_symbol = str(symbol or "").strip().upper()
        clean_weight = _optional_float(weight)
        if not clean_symbol or clean_weight is None or clean_weight <= 0.0:
            continue
        weights[clean_symbol] = weights.get(clean_symbol, 0.0) + clean_weight
    return dict(sorted(weights.items()))


def _coverage_status_from_weight(coverage_weight: float) -> str:
    if coverage_weight >= 80.0:
        return "actual"
    if coverage_weight >= 50.0:
        return "partial"
    if coverage_weight > 0.0:
        return "proxy"
    return "not_run"


def _result_status_from_coverage(coverage_weight: float) -> str:
    if coverage_weight >= 80.0:
        return "PASS"
    if coverage_weight >= 50.0:
        return "REVIEW"
    return "NOT_RUN"


def _quality_bucket_for_statuses(statuses: set[str]) -> str:
    lowered = {str(status or "").strip().lower() for status in statuses}
    for status in ("actual", "partial", "bridge", "proxy", "missing", "error"):
        if status in lowered:
            return status
    return "not_run"


def _coverage_quality(
    frame: pd.DataFrame,
    *,
    symbol_column: str,
    symbol_weights: dict[str, float],
) -> dict[str, Any]:
    if frame.empty or "coverage_status" not in frame.columns or symbol_column not in frame.columns:
        return {
            "status": "not_run",
            "diagnostic_status": "NOT_RUN",
            "bucket_weights": {},
        }

    bucket_weights = {
        "actual": 0.0,
        "partial": 0.0,
        "bridge": 0.0,
        "proxy": 0.0,
        "missing": 0.0,
        "error": 0.0,
    }
    work = frame.copy()
    work["_symbol"] = work[symbol_column].astype(str).str.upper()
    for symbol, group in work.groupby("_symbol", dropna=False):
        bucket = _quality_bucket_for_statuses(set(group["coverage_status"].dropna().astype(str)))
        if bucket in bucket_weights:
            bucket_weights[bucket] += symbol_weights.get(str(symbol), 0.0)

    bucket_weights = {key: round(value, 4) for key, value in bucket_weights.items() if value > 0.0}
    official_weight = bucket_weights.get("actual", 0.0) + bucket_weights.get("partial", 0.0)
    supported_weight = official_weight + bucket_weights.get("bridge", 0.0) + bucket_weights.get("proxy", 0.0)
    if bucket_weights.get("actual", 0.0) >= 80.0:
        status = "actual"
    elif official_weight > 0.0:
        status = "partial"
    elif bucket_weights.get("bridge", 0.0) > 0.0:
        status = "bridge"
    elif bucket_weights.get("proxy", 0.0) > 0.0:
        status = "proxy"
    else:
        status = "not_run"

    if status == "actual":
        diagnostic_status = "PASS"
    elif supported_weight > 0.0:
        diagnostic_status = "REVIEW"
    else:
        diagnostic_status = "NOT_RUN"
    return {
        "status": status,
        "diagnostic_status": diagnostic_status,
        "bucket_weights": bucket_weights,
    }


def _provider_provenance_summary(
    frame: pd.DataFrame,
    *,
    symbol_column: str,
    symbol_weights: dict[str, float],
    as_of_date: str | None,
    max_staleness_days: int,
    date_column: str = "as_of_date",
) -> dict[str, Any]:
    """Summarize provider row source and freshness without carrying raw holdings rows."""

    symbols = list(symbol_weights)
    if frame.empty or symbol_column not in frame.columns:
        return {
            "freshness_status": "not_run",
            "source_mix": "-",
            "source_type_weights": {},
            "coverage_status_weights": {},
            "as_of_range": "-",
            "collected_range": "-",
            "stale_symbols": [],
            "stale_weight": 0.0,
            "unknown_freshness_symbols": symbols,
            "unknown_freshness_weight": round(sum(symbol_weights.get(symbol, 0.0) for symbol in symbols), 4),
            "max_staleness_days": int(max_staleness_days),
            "symbol_rows": [
                {
                    "Symbol": symbol,
                    "Target Weight": round(symbol_weights.get(symbol, 0.0), 4),
                    "Coverage": "not_run",
                    "Source Type": "unknown",
                    "Sources": "-",
                    "As Of": None,
                    "Collected": None,
                    "Staleness Days": None,
                    "Freshness": "not_run",
                }
                for symbol in symbols
            ],
        }

    analysis_date = _analysis_date(as_of_date)
    work = frame.copy()
    work["_symbol"] = work[symbol_column].astype(str).str.upper()
    stale_symbols: list[str] = []
    unknown_freshness_symbols: list[str] = []
    source_type_weights: dict[str, float] = {}
    coverage_status_weights: dict[str, float] = {}
    symbol_rows: list[dict[str, Any]] = []

    for symbol in symbols:
        group = work[work["_symbol"] == symbol]
        weight = round(symbol_weights.get(symbol, 0.0), 4)
        if group.empty:
            coverage = "not_run"
            best_source_type = "unknown"
            sources: list[str] = []
            latest_snapshot = None
            latest_collected = None
            staleness_days = None
            freshness = "not_run"
            coverage_status_weights[coverage] = coverage_status_weights.get(coverage, 0.0) + weight
        else:
            coverage = _quality_bucket_for_statuses(set(group.get("coverage_status", pd.Series(dtype=str)).dropna().astype(str)))
            best_source_type = _best_source_type(group.get("source_type", pd.Series(dtype=str)).dropna().astype(str).tolist())
            sources = _compact_unique(group.get("source", pd.Series(dtype=str)).dropna().astype(str).tolist(), limit=4)
            latest_snapshot_series = pd.to_datetime(group.get(date_column, pd.Series(dtype=str)), errors="coerce").dropna()
            latest_collected_series = pd.to_datetime(group.get("collected_at", pd.Series(dtype=str)), errors="coerce").dropna()
            latest_snapshot = latest_snapshot_series.max() if not latest_snapshot_series.empty else None
            latest_collected = latest_collected_series.max() if not latest_collected_series.empty else None
            staleness_days = _days_old(analysis_date=analysis_date, snapshot_date=latest_snapshot)
            if staleness_days is None:
                freshness = "unknown"
                unknown_freshness_symbols.append(symbol)
            elif staleness_days > int(max_staleness_days):
                freshness = "stale"
                stale_symbols.append(symbol)
            else:
                freshness = "fresh"
            source_type_weights[best_source_type] = source_type_weights.get(best_source_type, 0.0) + weight
            coverage_status_weights[coverage] = coverage_status_weights.get(coverage, 0.0) + weight

        symbol_rows.append(
            {
                "Symbol": symbol,
                "Target Weight": weight,
                "Coverage": coverage,
                "Source Type": best_source_type,
                "Sources": ", ".join(sources) if sources else "-",
                "As Of": _date_text(latest_snapshot),
                "Collected": _date_text(latest_collected),
                "Staleness Days": staleness_days,
                "Freshness": freshness,
            }
        )

    source_type_weights = {key: round(value, 4) for key, value in source_type_weights.items() if value > 0.0}
    coverage_status_weights = {key: round(value, 4) for key, value in coverage_status_weights.items() if value > 0.0}
    stale_weight = round(sum(symbol_weights.get(symbol, 0.0) for symbol in stale_symbols), 4)
    unknown_weight = round(sum(symbol_weights.get(symbol, 0.0) for symbol in unknown_freshness_symbols), 4)
    if stale_symbols:
        freshness_status = "stale"
    elif unknown_freshness_symbols:
        freshness_status = "unknown"
    elif source_type_weights:
        freshness_status = "fresh"
    else:
        freshness_status = "not_run"
    return {
        "freshness_status": freshness_status,
        "source_mix": _source_mix_label(source_type_weights, _compact_unique(work.get("source", pd.Series(dtype=str)).dropna().astype(str).tolist(), limit=4)),
        "source_type_weights": source_type_weights,
        "coverage_status_weights": coverage_status_weights,
        "as_of_range": _range_text(work.get(date_column, pd.Series(dtype=str)).dropna().tolist()),
        "collected_range": _range_text(work.get("collected_at", pd.Series(dtype=str)).dropna().tolist()),
        "stale_symbols": stale_symbols,
        "stale_weight": stale_weight,
        "unknown_freshness_symbols": unknown_freshness_symbols,
        "unknown_freshness_weight": unknown_weight,
        "max_staleness_days": int(max_staleness_days),
        "symbol_rows": symbol_rows,
    }


def _downgrade_pass_for_freshness(diagnostic_status: str, provenance: dict[str, Any]) -> str:
    status = str(diagnostic_status or "NOT_RUN").upper()
    if status == "PASS" and str(provenance.get("freshness_status") or "") in {"stale", "unknown"}:
        return "REVIEW"
    return status


def _combined_look_through_status(*statuses: Any) -> str:
    normalized = {str(status or "NOT_RUN").strip().upper() for status in statuses}
    if "BLOCKED" in normalized:
        return "BLOCKED"
    if "REVIEW" in normalized:
        return "REVIEW"
    if "PASS" in normalized and "NOT_RUN" in normalized:
        return "REVIEW"
    if "PASS" in normalized:
        return "PASS"
    return "NOT_RUN"


def _asset_bucket_rows(asset_exposure: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for bucket, weight in sorted(
        dict(asset_exposure or {}).items(),
        key=lambda item: (_optional_float(item[1]) or 0.0),
        reverse=True,
    ):
        numeric = round(_optional_float(weight) or 0.0, 4)
        if numeric <= 0.0:
            continue
        rows.append(
            {
                "Asset Bucket": str(bucket),
                "Portfolio Weight": numeric,
                "Judgment": "REVIEW" if str(bucket) == "unknown" else "PASS",
            }
        )
    return rows


def _symbol_rows_by_symbol(provenance: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for raw_row in list(dict(provenance or {}).get("symbol_rows") or []):
        row = dict(raw_row or {}) if isinstance(raw_row, dict) else {}
        symbol = str(row.get("Symbol") or "").strip().upper()
        if symbol:
            rows[symbol] = row
    return rows


def _look_through_fund_coverage_rows(
    symbol_weights: dict[str, float],
    holdings_provenance: dict[str, Any],
    exposure_provenance: dict[str, Any],
) -> list[dict[str, Any]]:
    holdings_rows = _symbol_rows_by_symbol(holdings_provenance)
    exposure_rows = _symbol_rows_by_symbol(exposure_provenance)
    rows: list[dict[str, Any]] = []
    for symbol, weight in symbol_weights.items():
        holding_row = holdings_rows.get(symbol, {})
        exposure_row = exposure_rows.get(symbol, {})
        rows.append(
            {
                "Symbol": symbol,
                "Target Weight": round(weight, 4),
                "Holdings Coverage": holding_row.get("Coverage") or "not_run",
                "Holdings Freshness": holding_row.get("Freshness") or "-",
                "Holdings As Of": holding_row.get("As Of") or "-",
                "Exposure Coverage": exposure_row.get("Coverage") or "not_run",
                "Exposure Freshness": exposure_row.get("Freshness") or "-",
                "Exposure As Of": exposure_row.get("As Of") or "-",
            }
        )
    return rows


def _build_look_through_board(
    symbol_weights: dict[str, float],
    holdings: dict[str, Any],
    exposure: dict[str, Any],
) -> dict[str, Any]:
    """Build a compact holdings / exposure board without storing full provider rows."""

    holdings_provenance = dict(holdings.get("provenance") or {})
    exposure_provenance = dict(exposure.get("provenance") or {})
    holdings_status = str(holdings.get("diagnostic_status") or "NOT_RUN").upper()
    exposure_status = str(exposure.get("diagnostic_status") or "NOT_RUN").upper()
    status = _combined_look_through_status(holdings_status, exposure_status)
    holdings_coverage = _optional_float(holdings.get("coverage_weight")) or 0.0
    exposure_coverage = _optional_float(exposure.get("coverage_weight")) or 0.0
    holdings_metrics = dict(holdings.get("metrics") or {})
    asset_exposure = dict(exposure.get("asset_exposure") or {})
    top_holding_weight = round(_optional_float(holdings_metrics.get("top_holding_weight")) or 0.0, 4)
    top_overlap_weight = round(_optional_float(holdings_metrics.get("top_overlap_weight")) or 0.0, 4)
    unknown_exposure = round(_optional_float(asset_exposure.get("unknown")) or 0.0, 4)
    asset_rows = _asset_bucket_rows(asset_exposure)
    known_asset_rows = [row for row in asset_rows if row.get("Asset Bucket") != "unknown"]
    dominant_asset = known_asset_rows[0] if known_asset_rows else {}
    dominant_asset_label = str(dominant_asset.get("Asset Bucket") or "-")
    dominant_asset_weight = _optional_float(dominant_asset.get("Portfolio Weight")) or 0.0

    summary_rows = [
        {
            "Check": "Holdings Coverage",
            "Status": holdings_status,
            "Current": f"{holdings_coverage:.1f}%",
            "Evidence": (
                f"{holdings_provenance.get('freshness_status') or '-'} / "
                f"{holdings_provenance.get('source_mix') or '-'} / "
                f"{holdings_provenance.get('as_of_range') or '-'}"
            ),
            "Meaning": "ETF holdings snapshot이 target weight 기준으로 얼마나 실제 holdings overlap에 연결됐는지 봅니다.",
        },
        {
            "Check": "Exposure Coverage",
            "Status": exposure_status,
            "Current": f"{exposure_coverage:.1f}%",
            "Evidence": (
                f"{exposure_provenance.get('freshness_status') or '-'} / "
                f"{exposure_provenance.get('source_mix') or '-'} / "
                f"{exposure_provenance.get('as_of_range') or '-'}"
            ),
            "Meaning": "ETF exposure snapshot이 asset bucket look-through에 얼마나 연결됐는지 봅니다.",
        },
        {
            "Check": "Top Holding",
            "Status": "REVIEW" if top_holding_weight > 25.0 else "PASS" if holdings_coverage > 0.0 else "NOT_RUN",
            "Current": f"{top_holding_weight:.1f}%",
            "Evidence": f"{holdings_metrics.get('holding_count', 0)} compact holding row(s)",
            "Meaning": "단일 underlying holding이 portfolio weight에서 차지하는 최대 비중입니다.",
        },
        {
            "Check": "Top Overlap",
            "Status": "REVIEW" if top_overlap_weight > 20.0 else "PASS" if holdings_coverage > 0.0 else "NOT_RUN",
            "Current": f"{top_overlap_weight:.1f}%",
            "Evidence": f"{holdings_metrics.get('overlap_count', 0)} overlapped holding row(s)",
            "Meaning": "여러 ETF에 중복 포함된 holding의 최대 portfolio weight입니다.",
        },
        {
            "Check": "Dominant Asset Bucket",
            "Status": "PASS" if dominant_asset else "NOT_RUN",
            "Current": f"{dominant_asset_label} {dominant_asset_weight:.1f}%" if dominant_asset else "-",
            "Evidence": f"unknown {unknown_exposure:.1f}%",
            "Meaning": "provider exposure 기준 가장 큰 자산군과 미분류 비중입니다.",
        },
    ]
    if unknown_exposure > 0.0:
        summary_rows.append(
            {
                "Check": "Unknown Exposure",
                "Status": "REVIEW",
                "Current": f"{unknown_exposure:.1f}%",
                "Evidence": "missing exposure coverage",
                "Meaning": "미분류 exposure는 자산군 판단의 남은 공백입니다.",
            }
        )

    if status == "NOT_RUN":
        summary = "ETF holdings / exposure snapshot이 없어 look-through board를 만들지 못했습니다."
    else:
        summary = (
            f"Look-through board status {status}: holdings coverage {holdings_coverage:.1f}%, "
            f"exposure coverage {exposure_coverage:.1f}%, dominant asset {dominant_asset_label} "
            f"{dominant_asset_weight:.1f}%, top holding {top_holding_weight:.1f}%."
        )

    return {
        "schema_version": "look_through_board_v1",
        "status": status,
        "summary": summary,
        "holdings_status": holdings_status,
        "exposure_status": exposure_status,
        "holdings_coverage_weight": round(holdings_coverage, 4),
        "exposure_coverage_weight": round(exposure_coverage, 4),
        "top_holding_weight": top_holding_weight,
        "top_overlap_weight": top_overlap_weight,
        "unknown_exposure_weight": unknown_exposure,
        "dominant_asset_bucket": dominant_asset_label,
        "dominant_asset_weight": round(dominant_asset_weight, 4),
        "summary_rows": summary_rows,
        "asset_bucket_rows": asset_rows,
        "top_holding_rows": list(holdings.get("evidence_rows") or [])[:12],
        "fund_coverage_rows": _look_through_fund_coverage_rows(
            symbol_weights,
            holdings_provenance,
            exposure_provenance,
        ),
        "exposure_detail_rows": list(exposure.get("evidence_rows") or [])[:12],
        "limitations": [
            "V1 board는 1차 ETF holdings / exposure snapshot 기준입니다.",
            "ETF-of-ETF 2차 underlying look-through expansion은 후속 작업입니다.",
            "Full holdings row는 DB에만 두고 validation / final decision에는 compact rows만 남깁니다.",
        ],
    }


def _supported_symbols(frame: pd.DataFrame, *, symbol_column: str) -> list[str]:
    """Return symbols with usable provider rows, excluding explicit missing/error rows."""
    if frame.empty or symbol_column not in frame.columns:
        return []
    work = frame.copy()
    if "coverage_status" in work.columns:
        work = work[
            ~work["coverage_status"].astype(str).str.lower().isin({"missing", "error"})
        ]
    return sorted(set(work[symbol_column].astype(str).str.upper()))


def _safe_loader(callable_obj: Any, *args: Any, **kwargs: Any) -> tuple[pd.DataFrame, str | None]:
    try:
        result = callable_obj(*args, **kwargs)
    except Exception as exc:
        return pd.DataFrame(), str(exc)
    return result if isinstance(result, pd.DataFrame) else pd.DataFrame(), None


def _best_operability_rows(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    work = frame.copy()
    coverage_rank = {"actual": 5, "partial": 4, "bridge": 3, "proxy": 2, "missing": 1, "error": 0}
    source_rank = SOURCE_TYPE_RANK
    work["_coverage_rank"] = work["coverage_status"].astype(str).str.lower().map(coverage_rank).fillna(0)
    work["_source_rank"] = work["source_type"].astype(str).str.lower().map(source_rank).fillna(0)
    work["_as_of"] = pd.to_datetime(work["as_of_date"], errors="coerce")
    work = work.sort_values(["symbol", "_coverage_rank", "_source_rank", "_as_of"], ascending=[True, False, False, False])
    merged_rows: list[pd.Series] = []
    fill_columns = [
        "expense_ratio",
        "turnover_ratio",
        "total_assets",
        "net_assets",
        "nav",
        "market_price",
        "premium_discount_pct",
        "bid",
        "ask",
        "bid_ask_spread_pct",
        "median_bid_ask_spread_pct",
        "avg_daily_volume",
        "avg_daily_dollar_volume",
        "leverage_factor",
        "is_inverse",
        "has_daily_objective",
        "inception_date",
        "fund_family",
        "category",
    ]
    for _, group in work.groupby("symbol", sort=False):
        base = group.iloc[0].copy()
        used_sources = [_first_text(base.get("source"))]
        used_source_types = [_first_text(base.get("source_type"))]
        for column in fill_columns:
            if column not in group.columns:
                continue
            current = base.get(column)
            try:
                current_missing = pd.isna(current)
            except Exception:
                current_missing = current is None
            if not current_missing:
                continue
            for _, candidate in group.iloc[1:].iterrows():
                candidate_value = candidate.get(column)
                try:
                    candidate_missing = pd.isna(candidate_value)
                except Exception:
                    candidate_missing = candidate_value is None
                if candidate_missing:
                    continue
                base[column] = candidate_value
                source = _first_text(candidate.get("source"))
                source_type = _first_text(candidate.get("source_type"))
                if source and source not in used_sources:
                    used_sources.append(source)
                if source_type and source_type not in used_source_types:
                    used_source_types.append(source_type)
                break
        if len([source for source in used_sources if source]) > 1:
            base["source"] = " + ".join(source for source in used_sources if source)
        if len([source_type for source_type in used_source_types if source_type]) > 1:
            base["source_type"] = " + ".join(source_type for source_type in used_source_types if source_type)
        merged_rows.append(base)
    if not merged_rows:
        return work.drop(columns=["_coverage_rank", "_source_rank", "_as_of"])
    return pd.DataFrame(merged_rows).drop(columns=["_coverage_rank", "_source_rank", "_as_of"], errors="ignore")


def _canonical_asset_bucket(name: Any) -> str:
    text = str(name or "").strip().lower()
    for needle, bucket in ASSET_CLASS_BUCKETS.items():
        if needle in text:
            return bucket
    return "other"


def _build_exposure_context(
    symbol_weights: dict[str, float],
    as_of_date: str | None,
    *,
    max_staleness_days: int,
) -> dict[str, Any]:
    symbols = list(symbol_weights)
    frame, error = _safe_loader(
        load_etf_exposure_snapshot,
        symbols,
        as_of_date=as_of_date,
        latest=True,
    )
    if error:
        return {
            "status": "not_run",
            "diagnostic_status": "NOT_RUN",
            "summary": f"ETF exposure loader failed: {error}",
            "coverage_weight": 0.0,
            "missing_symbols": symbols,
            "asset_exposure": {},
            "provenance": _provider_provenance_summary(
                pd.DataFrame(),
                symbol_column="fund_symbol",
                symbol_weights=symbol_weights,
                as_of_date=as_of_date,
                max_staleness_days=max_staleness_days,
            ),
            "evidence_rows": [],
        }
    if frame.empty:
        return {
            "status": "not_run",
            "diagnostic_status": "NOT_RUN",
            "summary": "ETF exposure snapshot이 없어 asset allocation look-through를 실행하지 못했습니다.",
            "coverage_weight": 0.0,
            "missing_symbols": symbols,
            "asset_exposure": {},
            "provenance": _provider_provenance_summary(
                frame,
                symbol_column="fund_symbol",
                symbol_weights=symbol_weights,
                as_of_date=as_of_date,
                max_staleness_days=max_staleness_days,
            ),
            "evidence_rows": [],
        }

    asset_rows = frame[frame["exposure_type"].astype(str).str.lower() == "asset_class"].copy()
    covered_symbols = _supported_symbols(asset_rows, symbol_column="fund_symbol")
    coverage_weight = round(sum(symbol_weights.get(symbol, 0.0) for symbol in covered_symbols), 4)
    missing_symbols = [symbol for symbol in symbols if symbol not in covered_symbols]
    asset_exposure: dict[str, float] = {
        "equity": 0.0,
        "bond": 0.0,
        "cash": 0.0,
        "gold": 0.0,
        "commodity": 0.0,
        "other": 0.0,
        "unknown": round(max(0.0, 100.0 - coverage_weight), 4),
    }
    for _, row in asset_rows.iterrows():
        fund_symbol = str(row.get("fund_symbol") or "").upper()
        weight = symbol_weights.get(fund_symbol, 0.0)
        exposure_weight = _optional_float(row.get("weight_pct")) or 0.0
        bucket = _canonical_asset_bucket(row.get("exposure_name"))
        asset_exposure[bucket] = asset_exposure.get(bucket, 0.0) + (weight * exposure_weight / 100.0)

    asset_exposure = {key: round(value, 4) for key, value in asset_exposure.items()}
    top_rows = (
        asset_rows.assign(
            PortfolioWeight=lambda df: df.apply(
                lambda row: round(
                    symbol_weights.get(str(row.get("fund_symbol") or "").upper(), 0.0)
                    * (_optional_float(row.get("weight_pct")) or 0.0)
                    / 100.0,
                    4,
                ),
                axis=1,
            )
        )
        .sort_values("PortfolioWeight", ascending=False)
        .head(12)
    )
    evidence_rows = [
        {
            "Fund": row.get("fund_symbol"),
            "Exposure": row.get("exposure_name"),
            "Bucket": _canonical_asset_bucket(row.get("exposure_name")),
            "Fund Weight": _optional_float(row.get("weight_pct")),
            "Portfolio Weight": _optional_float(row.get("PortfolioWeight")),
            "Source": row.get("source"),
            "As Of": _date_text(row.get("as_of_date")),
            "Coverage": row.get("coverage_status"),
        }
        for _, row in top_rows.iterrows()
    ]
    quality = _coverage_quality(asset_rows, symbol_column="fund_symbol", symbol_weights=symbol_weights)
    status = str(quality.get("status") or _coverage_status_from_weight(coverage_weight))
    diagnostic_status = str(quality.get("diagnostic_status") or _result_status_from_coverage(coverage_weight))
    provenance = _provider_provenance_summary(
        asset_rows,
        symbol_column="fund_symbol",
        symbol_weights=symbol_weights,
        as_of_date=as_of_date,
        max_staleness_days=max_staleness_days,
    )
    diagnostic_status = _downgrade_pass_for_freshness(diagnostic_status, provenance)
    return {
        "status": status,
        "diagnostic_status": diagnostic_status,
        "summary": (
            f"ETF exposure snapshot covers {coverage_weight:.1f}% of target weight."
            if coverage_weight > 0.0
            else "ETF exposure snapshot coverage is unavailable."
        ),
        "coverage_weight": coverage_weight,
        "covered_symbols": covered_symbols,
        "missing_symbols": missing_symbols,
        "asset_exposure": asset_exposure,
        "bucket_weights": dict(quality.get("bucket_weights") or {}),
        "provenance": provenance,
        "evidence_rows": evidence_rows,
    }


def _build_holdings_context(
    symbol_weights: dict[str, float],
    as_of_date: str | None,
    *,
    max_staleness_days: int,
) -> dict[str, Any]:
    symbols = list(symbol_weights)
    frame, error = _safe_loader(
        load_etf_holdings_snapshot,
        symbols,
        as_of_date=as_of_date,
        latest=True,
    )
    if error:
        return {
            "status": "not_run",
            "diagnostic_status": "NOT_RUN",
            "summary": f"ETF holdings loader failed: {error}",
            "coverage_weight": 0.0,
            "missing_symbols": symbols,
            "evidence_rows": [],
            "metrics": {},
            "provenance": _provider_provenance_summary(
                pd.DataFrame(),
                symbol_column="fund_symbol",
                symbol_weights=symbol_weights,
                as_of_date=as_of_date,
                max_staleness_days=max_staleness_days,
            ),
        }
    if frame.empty:
        return {
            "status": "not_run",
            "diagnostic_status": "NOT_RUN",
            "summary": "ETF holdings snapshot이 없어 holdings overlap을 계산하지 못했습니다.",
            "coverage_weight": 0.0,
            "missing_symbols": symbols,
            "evidence_rows": [],
            "metrics": {},
            "provenance": _provider_provenance_summary(
                frame,
                symbol_column="fund_symbol",
                symbol_weights=symbol_weights,
                as_of_date=as_of_date,
                max_staleness_days=max_staleness_days,
            ),
        }

    work = frame.copy()
    work["fund_symbol"] = work["fund_symbol"].astype(str).str.upper()
    covered_symbols = _supported_symbols(work, symbol_column="fund_symbol")
    coverage_weight = round(sum(symbol_weights.get(symbol, 0.0) for symbol in covered_symbols), 4)
    missing_symbols = [symbol for symbol in symbols if symbol not in covered_symbols]
    work["holding_key"] = work.apply(
        lambda row: _first_text(row.get("holding_symbol"), row.get("holding_id"), row.get("holding_name")).upper(),
        axis=1,
    )
    work["holding_label"] = work.apply(
        lambda row: _first_text(row.get("holding_symbol"), row.get("holding_name"), row.get("holding_id")) or "-",
        axis=1,
    )
    work["portfolio_weight"] = work.apply(
        lambda row: symbol_weights.get(str(row.get("fund_symbol") or "").upper(), 0.0)
        * ((_optional_float(row.get("weight_pct")) or 0.0) / 100.0),
        axis=1,
    )
    grouped = (
        work.groupby("holding_key", dropna=False)
        .agg(
            Holding=("holding_label", "first"),
            PortfolioWeight=("portfolio_weight", "sum"),
            FundCount=("fund_symbol", "nunique"),
            Funds=("fund_symbol", lambda values: ", ".join(sorted(set(str(value) for value in values))[:6])),
        )
        .reset_index()
        .sort_values("PortfolioWeight", ascending=False)
    )
    top_holding_weight = _optional_float(grouped["PortfolioWeight"].iloc[0]) if not grouped.empty else None
    overlap_frame = grouped[grouped["FundCount"] >= 2].copy()
    top_overlap_weight = _optional_float(overlap_frame["PortfolioWeight"].iloc[0]) if not overlap_frame.empty else 0.0
    quality = _coverage_quality(work, symbol_column="fund_symbol", symbol_weights=symbol_weights)
    diagnostic_status = str(quality.get("diagnostic_status") or _result_status_from_coverage(coverage_weight))
    if diagnostic_status == "PASS" and ((top_holding_weight or 0.0) > 25.0 or (top_overlap_weight or 0.0) > 20.0):
        diagnostic_status = "REVIEW"
    status = str(quality.get("status") or _coverage_status_from_weight(coverage_weight))
    provenance = _provider_provenance_summary(
        work,
        symbol_column="fund_symbol",
        symbol_weights=symbol_weights,
        as_of_date=as_of_date,
        max_staleness_days=max_staleness_days,
    )
    diagnostic_status = _downgrade_pass_for_freshness(diagnostic_status, provenance)
    evidence_rows = [
        {
            "Holding": row.get("Holding"),
            "Portfolio Weight": round(_optional_float(row.get("PortfolioWeight")) or 0.0, 4),
            "Fund Count": int(row.get("FundCount") or 0),
            "Funds": row.get("Funds"),
            "Judgment": "REVIEW"
            if (_optional_float(row.get("PortfolioWeight")) or 0.0) > 25.0 or int(row.get("FundCount") or 0) >= 2
            else "PASS",
        }
        for _, row in grouped.head(12).iterrows()
    ]
    return {
        "status": status,
        "diagnostic_status": diagnostic_status,
        "summary": (
            f"ETF holdings snapshot covers {coverage_weight:.1f}% of target weight; "
            f"top holding {top_holding_weight or 0.0:.1f}%, top overlap {top_overlap_weight or 0.0:.1f}%."
        ),
        "coverage_weight": coverage_weight,
        "covered_symbols": covered_symbols,
        "missing_symbols": missing_symbols,
        "bucket_weights": dict(quality.get("bucket_weights") or {}),
        "evidence_rows": evidence_rows,
        "provenance": provenance,
        "metrics": {
            "top_holding_weight": round(top_holding_weight or 0.0, 4),
            "top_overlap_weight": round(top_overlap_weight or 0.0, 4),
            "holding_count": int(len(grouped)),
            "overlap_count": int(len(overlap_frame)),
        },
    }


def _operability_judgment(row: pd.Series) -> tuple[str, str]:
    reasons: list[str] = []
    coverage = str(row.get("coverage_status") or "").lower()
    if coverage in {"missing", "error"}:
        reasons.append(f"coverage={coverage}")
    net_assets = _first_optional_float(row.get("net_assets"), row.get("total_assets"))
    adv = _optional_float(row.get("avg_daily_dollar_volume"))
    spread = _first_optional_float(row.get("bid_ask_spread_pct"), row.get("median_bid_ask_spread_pct"))
    expense = _optional_float(row.get("expense_ratio"))
    premium = _optional_float(row.get("premium_discount_pct"))
    available_groups = sum(
        1
        for value in (
            expense,
            net_assets,
            adv,
            spread,
            premium if premium is not None else (_optional_float(row.get("nav")) and _optional_float(row.get("market_price"))),
        )
        if value is not None
    )
    if available_groups < 3:
        reasons.append("core field coverage < 3")
    if net_assets is not None and net_assets < 100_000_000:
        reasons.append("AUM below $100M")
    if adv is not None and adv < 5_000_000:
        reasons.append("ADV below $5M")
    if spread is not None and spread > 0.005:
        reasons.append("spread above 0.5%")
    if expense is not None and expense > 0.01:
        reasons.append("expense ratio above 1%")
    if premium is not None and abs(premium) > 0.01:
        reasons.append("premium/discount above 1%")
    return ("REVIEW", "; ".join(reasons)) if reasons else ("PASS", "provider / bridge fields sufficient")


def _build_operability_context(
    symbol_weights: dict[str, float],
    as_of_date: str | None,
    *,
    max_staleness_days: int,
) -> dict[str, Any]:
    symbols = list(symbol_weights)
    frame, error = _safe_loader(
        load_etf_operability_snapshot,
        symbols,
        as_of_date=as_of_date,
        latest=True,
    )
    if error:
        return {
            "status": "not_run",
            "diagnostic_status": "NOT_RUN",
            "summary": f"ETF operability loader failed: {error}",
            "coverage_weight": 0.0,
            "missing_symbols": symbols,
            "evidence_rows": [],
            "provenance": _provider_provenance_summary(
                pd.DataFrame(),
                symbol_column="symbol",
                symbol_weights=symbol_weights,
                as_of_date=as_of_date,
                max_staleness_days=max_staleness_days,
            ),
            "leverage": {"diagnostic_status": "NOT_RUN", "flagged_exposure": 0.0, "evidence_rows": []},
        }
    if frame.empty:
        return {
            "status": "not_run",
            "diagnostic_status": "NOT_RUN",
            "summary": "ETF operability snapshot이 없어 provider 기반 비용/유동성 확인을 실행하지 못했습니다.",
            "coverage_weight": 0.0,
            "missing_symbols": symbols,
            "evidence_rows": [],
            "provenance": _provider_provenance_summary(
                frame,
                symbol_column="symbol",
                symbol_weights=symbol_weights,
                as_of_date=as_of_date,
                max_staleness_days=max_staleness_days,
            ),
            "leverage": {"diagnostic_status": "NOT_RUN", "flagged_exposure": 0.0, "evidence_rows": []},
        }

    best = _best_operability_rows(frame)
    provenance = _provider_provenance_summary(
        best,
        symbol_column="symbol",
        symbol_weights=symbol_weights,
        as_of_date=as_of_date,
        max_staleness_days=max_staleness_days,
    )
    covered_symbols = _supported_symbols(best, symbol_column="symbol")
    coverage_weight = round(sum(symbol_weights.get(symbol, 0.0) for symbol in covered_symbols), 4)
    missing_symbols = [symbol for symbol in symbols if symbol not in covered_symbols]
    evidence_rows: list[dict[str, Any]] = []
    review_count = 0
    review_symbols: list[str] = []
    asset_values: list[float] = []
    adv_values: list[float] = []
    spread_values: list[float] = []
    expense_values: list[float] = []
    premium_values: list[float] = []
    flagged_exposure = 0.0
    leverage_rows: list[dict[str, Any]] = []
    for _, row in best.iterrows():
        symbol = str(row.get("symbol") or "").upper()
        judgment, reason = _operability_judgment(row)
        review_count += 1 if judgment == "REVIEW" else 0
        if judgment == "REVIEW":
            review_symbols.append(symbol)
        net_assets = _first_optional_float(row.get("net_assets"), row.get("total_assets"))
        adv = _optional_float(row.get("avg_daily_dollar_volume"))
        spread = _first_optional_float(row.get("bid_ask_spread_pct"), row.get("median_bid_ask_spread_pct"))
        expense = _optional_float(row.get("expense_ratio"))
        premium = _optional_float(row.get("premium_discount_pct"))
        if net_assets is not None:
            asset_values.append(net_assets)
        if adv is not None:
            adv_values.append(adv)
        if spread is not None:
            spread_values.append(spread)
        if expense is not None:
            expense_values.append(expense)
        if premium is not None:
            premium_values.append(abs(premium))
        leverage_factor = _optional_float(row.get("leverage_factor"))
        is_inverse = bool(_optional_float(row.get("is_inverse")) or 0.0)
        daily_objective = bool(_optional_float(row.get("has_daily_objective")) or 0.0)
        is_flagged = (leverage_factor is not None and leverage_factor > 1.0) or is_inverse or daily_objective
        if is_flagged:
            flagged_exposure += symbol_weights.get(symbol, 0.0)
        leverage_rows.append(
            {
                "Ticker": symbol,
                "Target Weight": round(symbol_weights.get(symbol, 0.0), 4),
                "Source": row.get("source"),
                "Coverage": row.get("coverage_status"),
                "Leverage Factor": leverage_factor,
                "Inverse": is_inverse,
                "Daily Objective": daily_objective,
                "Judgment": "REVIEW" if is_flagged else "PASS",
            }
        )
        evidence_rows.append(
            {
                "Ticker": symbol,
                "Target Weight": round(symbol_weights.get(symbol, 0.0), 4),
                "Source": row.get("source"),
                "Coverage": row.get("coverage_status"),
                "Expense": _pct_text(row.get("expense_ratio")),
                "Assets": _money_text(_first_optional_float(row.get("net_assets"), row.get("total_assets"))),
                "ADV": _money_text(row.get("avg_daily_dollar_volume")),
                "Spread": _pct_text(_first_optional_float(row.get("bid_ask_spread_pct"), row.get("median_bid_ask_spread_pct"))),
                "Premium/Discount": _pct_text(row.get("premium_discount_pct")),
                "As Of": _date_text(row.get("as_of_date")),
                "Judgment": judgment,
                "Reason": reason,
            }
        )

    quality = _coverage_quality(best, symbol_column="symbol", symbol_weights=symbol_weights)
    diagnostic_status = str(quality.get("diagnostic_status") or _result_status_from_coverage(coverage_weight))
    status = str(quality.get("status") or _coverage_status_from_weight(coverage_weight))
    if status == "actual" and coverage_weight >= 80.0 and review_count == 0:
        diagnostic_status = "PASS"
    elif diagnostic_status == "PASS" and review_count > 0:
        diagnostic_status = "REVIEW"
    diagnostic_status = _downgrade_pass_for_freshness(diagnostic_status, provenance)
    leverage_status = "REVIEW" if flagged_exposure > 0.0 else "PASS" if coverage_weight > 0.0 else "NOT_RUN"
    return {
        "status": status,
        "diagnostic_status": diagnostic_status,
        "summary": (
            f"ETF operability snapshot covers {coverage_weight:.1f}% of target weight; "
            f"{review_count} ticker(s) need review."
        ),
        "coverage_weight": coverage_weight,
        "covered_symbols": covered_symbols,
        "missing_symbols": missing_symbols,
        "bucket_weights": dict(quality.get("bucket_weights") or {}),
        "evidence_rows": evidence_rows,
        "provenance": provenance,
        "metrics": {
            "review_count": review_count,
            "review_symbols": review_symbols,
            "covered_symbol_count": len(covered_symbols),
            "missing_symbol_count": len(missing_symbols),
            "min_net_assets": min(asset_values) if asset_values else None,
            "min_avg_daily_dollar_volume": min(adv_values) if adv_values else None,
            "max_bid_ask_spread_pct": max(spread_values) if spread_values else None,
            "max_expense_ratio": max(expense_values) if expense_values else None,
            "max_abs_premium_discount_pct": max(premium_values) if premium_values else None,
        },
        "leverage": {
            "diagnostic_status": leverage_status,
            "flagged_exposure": round(flagged_exposure, 4),
            "evidence_rows": leverage_rows,
        },
    }


def _macro_value(rows: dict[str, dict[str, Any]], series_id: str) -> float | None:
    return _optional_float(dict(rows.get(series_id) or {}).get("value"))


def _macro_provenance_summary(frame: pd.DataFrame, *, max_staleness_days: int) -> dict[str, Any]:
    if frame.empty:
        return {
            "freshness_status": "not_run",
            "source_mix": "-",
            "series_count": 0,
            "stale_count": 0,
            "observation_range": "-",
            "collected_range": "-",
            "stale_series": [],
            "max_staleness_days": int(max_staleness_days),
            "series_rows": [],
        }
    rows = [dict(row) for _, row in frame.iterrows()]
    stale_series: list[str] = []
    series_rows: list[dict[str, Any]] = []
    source_labels: list[str] = []
    for row in rows:
        series_id = str(row.get("series_id") or "").upper()
        source = _first_text(row.get("source"), "unknown")
        source_type = _first_text(row.get("source_type"), "unknown")
        source_mode = _first_text(row.get("source_mode"))
        source_label = f"{source}/{source_mode}" if source_mode else f"{source}/{source_type}"
        if source_label not in source_labels:
            source_labels.append(source_label)
        staleness_days = _optional_float(row.get("staleness_days"))
        snapshot_status = str(row.get("snapshot_status") or "").lower()
        freshness = "fresh"
        if snapshot_status != "actual" or (staleness_days is not None and staleness_days > int(max_staleness_days)):
            freshness = "stale"
            stale_series.append(series_id)
        series_rows.append(
            {
                "Series": series_id,
                "Coverage": row.get("coverage_status"),
                "Source": source,
                "Source Type": source_type,
                "Source Mode": source_mode or "-",
                "Observation Date": _date_text(row.get("observation_date")),
                "Collected": _date_text(row.get("collected_at")),
                "Staleness Days": staleness_days,
                "Freshness": freshness,
            }
        )
    freshness_status = "stale" if stale_series else "fresh" if series_rows else "not_run"
    return {
        "freshness_status": freshness_status,
        "source_mix": ", ".join(source_labels[:4]) if source_labels else "-",
        "series_count": len(series_rows),
        "stale_count": len(stale_series),
        "observation_range": _range_text([row.get("observation_date") for row in rows]),
        "collected_range": _range_text([row.get("collected_at") for row in rows]),
        "stale_series": stale_series,
        "max_staleness_days": int(max_staleness_days),
        "series_rows": series_rows,
    }


def _build_macro_context(as_of_date: str | None, max_staleness_days: int = 10) -> dict[str, Any]:
    frame, error = _safe_loader(
        load_macro_snapshot,
        DEFAULT_MACRO_SERIES,
        as_of_date=as_of_date,
        max_staleness_days=max_staleness_days,
    )
    if error:
        return {
            "status": "not_run",
            "diagnostic_status": "NOT_RUN",
            "summary": f"Macro loader failed: {error}",
            "series_count": 0,
            "stale_count": 0,
            "evidence_rows": [],
            "provenance": _macro_provenance_summary(pd.DataFrame(), max_staleness_days=max_staleness_days),
            "regime": {"diagnostic_status": "NOT_RUN"},
            "sentiment": {"diagnostic_status": "NOT_RUN"},
        }
    if frame.empty:
        return {
            "status": "not_run",
            "diagnostic_status": "NOT_RUN",
            "summary": "FRED macro snapshot이 없어 macro / sentiment context를 실행하지 못했습니다.",
            "series_count": 0,
            "stale_count": 0,
            "evidence_rows": [],
            "provenance": _macro_provenance_summary(frame, max_staleness_days=max_staleness_days),
            "regime": {"diagnostic_status": "NOT_RUN"},
            "sentiment": {"diagnostic_status": "NOT_RUN"},
        }
    rows_by_series = {str(row.get("series_id") or "").upper(): dict(row) for _, row in frame.iterrows()}
    actual_rows = [row for row in rows_by_series.values() if row.get("snapshot_status") == "actual"]
    stale_rows = [row for row in rows_by_series.values() if row.get("snapshot_status") != "actual"]
    vix = _macro_value(rows_by_series, "VIXCLS")
    curve = _macro_value(rows_by_series, "T10Y3M")
    credit = _macro_value(rows_by_series, "BAA10Y")
    risk_reasons: list[str] = []
    if vix is not None and vix >= 30.0:
        risk_reasons.append("VIX >= 30")
    elif vix is not None and vix >= 20.0:
        risk_reasons.append("VIX >= 20")
    if curve is not None and curve < 0.0:
        risk_reasons.append("yield curve inverted")
    if credit is not None and credit >= 3.0:
        risk_reasons.append("credit spread >= 3")
    elif credit is not None and credit >= 2.5:
        risk_reasons.append("credit spread >= 2.5")
    evidence_rows = [
        {
            "Series": row.get("series_id"),
            "Category": row.get("category"),
            "Value": _optional_float(row.get("value")),
            "Observation Date": _date_text(row.get("observation_date")),
            "Staleness Days": _optional_float(row.get("staleness_days")),
            "Snapshot Status": row.get("snapshot_status"),
            "Source": row.get("source"),
        }
        for row in rows_by_series.values()
    ]
    series_count = len(actual_rows)
    stale_count = len(stale_rows)
    provenance = _macro_provenance_summary(frame, max_staleness_days=max_staleness_days)
    base_status = "actual" if series_count >= 3 and stale_count == 0 else "partial" if series_count > 0 else "not_run"
    regime_status = "NOT_RUN" if series_count == 0 else "REVIEW" if series_count < 3 or stale_count > 0 or risk_reasons else "PASS"
    sentiment_status = "NOT_RUN" if series_count == 0 else "REVIEW" if series_count < 2 or stale_count > 0 or risk_reasons else "PASS"
    risk_label = "risk-off / caution" if risk_reasons else "neutral / risk-on"
    summary = (
        f"FRED macro snapshot has {series_count}/3 actual series"
        + (f"; review: {', '.join(risk_reasons)}." if risk_reasons else ".")
    )
    return {
        "status": base_status,
        "diagnostic_status": regime_status,
        "summary": summary,
        "series_count": series_count,
        "stale_count": stale_count,
        "evidence_rows": evidence_rows,
        "provenance": provenance,
        "metrics": {"vix": vix, "yield_curve": curve, "credit_spread": credit, "risk_label": risk_label},
        "regime": {
            "diagnostic_status": regime_status,
            "key_metric": f"VIX {vix if vix is not None else '-'} / YC {curve if curve is not None else '-'} / BAA10Y {credit if credit is not None else '-'}",
            "summary": summary,
            "evidence_rows": evidence_rows,
        },
        "sentiment": {
            "diagnostic_status": sentiment_status,
            "key_metric": risk_label,
            "summary": (
                f"Risk-on/off context is {risk_label}"
                + (f" because {', '.join(risk_reasons)}." if risk_reasons else " based on VIX / credit spread / yield curve.")
            ),
            "evidence_rows": evidence_rows,
        },
    }


def build_provider_context(
    symbol_weights: dict[str, Any] | None,
    *,
    as_of_date: str | None = None,
    max_provider_staleness_days: int = DEFAULT_PROVIDER_STALENESS_DAYS,
    max_macro_staleness_days: int = 10,
) -> dict[str, Any]:
    """Build compact provider evidence for Practical Validation without storing raw provider rows."""
    weights = _normalize_symbol_weights(symbol_weights)
    symbols = list(weights)
    provider_staleness_days = int(max_provider_staleness_days)
    if provider_staleness_days < 0:
        raise ValueError("max_provider_staleness_days must be non-negative.")
    if not symbols:
        empty = {
            "status": "not_run",
            "diagnostic_status": "NOT_RUN",
            "summary": "검증 대상 ETF symbol이 없어 provider context를 만들지 못했습니다.",
            "coverage_weight": 0.0,
            "missing_symbols": [],
            "evidence_rows": [],
            "provenance": _provider_provenance_summary(
                pd.DataFrame(),
                symbol_column="symbol",
                symbol_weights={},
                as_of_date=as_of_date,
                max_staleness_days=provider_staleness_days,
            ),
        }
        macro = _build_macro_context(as_of_date, max_staleness_days=max_macro_staleness_days)
        look_through_board = _build_look_through_board({}, empty, empty)
        return {
            "schema_version": PROVIDER_CONTEXT_SCHEMA_VERSION,
            "as_of_date": as_of_date,
            "symbols": [],
            "symbol_weights": {},
            "coverage": {
                "operability": empty,
                "holdings": empty,
                "exposure": empty,
                "macro": macro,
            },
            "look_through_board": look_through_board,
            "display_rows": _provider_display_rows(empty, empty, empty, macro),
        }

    exposure = _build_exposure_context(weights, as_of_date, max_staleness_days=provider_staleness_days)
    holdings = _build_holdings_context(weights, as_of_date, max_staleness_days=provider_staleness_days)
    operability = _build_operability_context(weights, as_of_date, max_staleness_days=provider_staleness_days)
    macro = _build_macro_context(as_of_date, max_staleness_days=max_macro_staleness_days)
    look_through_board = _build_look_through_board(weights, holdings, exposure)
    return {
        "schema_version": PROVIDER_CONTEXT_SCHEMA_VERSION,
        "as_of_date": as_of_date,
        "symbols": symbols,
        "symbol_weights": {symbol: round(weight, 4) for symbol, weight in weights.items()},
        "coverage": {
            "operability": operability,
            "holdings": holdings,
            "exposure": exposure,
            "macro": macro,
        },
        "look_through_board": look_through_board,
        "display_rows": _provider_display_rows(operability, holdings, exposure, macro),
    }


def _provider_display_rows(
    operability: dict[str, Any],
    holdings: dict[str, Any],
    exposure: dict[str, Any],
    macro: dict[str, Any],
) -> list[dict[str, Any]]:
    op_provenance = dict(operability.get("provenance") or {})
    holdings_provenance = dict(holdings.get("provenance") or {})
    exposure_provenance = dict(exposure.get("provenance") or {})
    macro_provenance = dict(macro.get("provenance") or {})
    return [
        {
            "Area": "ETF Operability",
            "Coverage": operability.get("status"),
            "Diagnostic Status": operability.get("diagnostic_status"),
            "Coverage Weight": operability.get("coverage_weight"),
            "Source Mix": op_provenance.get("source_mix") or "-",
            "Freshness": op_provenance.get("freshness_status") or "-",
            "As Of Range": op_provenance.get("as_of_range") or "-",
            "Summary": operability.get("summary"),
        },
        {
            "Area": "ETF Holdings",
            "Coverage": holdings.get("status"),
            "Diagnostic Status": holdings.get("diagnostic_status"),
            "Coverage Weight": holdings.get("coverage_weight"),
            "Source Mix": holdings_provenance.get("source_mix") or "-",
            "Freshness": holdings_provenance.get("freshness_status") or "-",
            "As Of Range": holdings_provenance.get("as_of_range") or "-",
            "Summary": holdings.get("summary"),
        },
        {
            "Area": "ETF Exposure",
            "Coverage": exposure.get("status"),
            "Diagnostic Status": exposure.get("diagnostic_status"),
            "Coverage Weight": exposure.get("coverage_weight"),
            "Source Mix": exposure_provenance.get("source_mix") or "-",
            "Freshness": exposure_provenance.get("freshness_status") or "-",
            "As Of Range": exposure_provenance.get("as_of_range") or "-",
            "Summary": exposure.get("summary"),
        },
        {
            "Area": "Macro Context",
            "Coverage": macro.get("status"),
            "Diagnostic Status": macro.get("diagnostic_status"),
            "Coverage Weight": None,
            "Source Mix": macro_provenance.get("source_mix") or "-",
            "Freshness": macro_provenance.get("freshness_status") or "-",
            "As Of Range": macro_provenance.get("observation_range") or "-",
            "Summary": macro.get("summary"),
        },
    ]
