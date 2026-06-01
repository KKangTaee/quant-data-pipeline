from __future__ import annotations

import re
from typing import Any
from uuid import uuid4

import pandas as pd

from app.services.backtest_practical_validation_curve import (
    build_benchmark_parity,
    build_curve_provenance,
    normalize_result_curve as normalize_validation_curve,
)
from app.services.backtest_data_coverage_audit import (
    build_data_coverage_audit,
    build_db_data_coverage_context,
)
from app.services.backtest_construction_risk_audit import build_construction_risk_audit
from app.services.backtest_practical_validation_curve_context import (
    _combine_component_curves,
    _format_date,
    _normalize_result_curve,
    _parse_date,
    _price_proxy_curve,
    _summary_metrics_from_curve,
    compact_benchmark_curve_snapshot_from_bundle,
    compact_curve_snapshot_from_bundle,
)
from app.services.backtest_practical_validation_provider_context import build_provider_context
from app.services.backtest_practical_validation_modules import build_validation_module_plan
from app.services.backtest_selected_route_preflight import (
    build_practical_validation_selected_route_preflight,
)
from app.services.backtest_component_role_weight_audit import build_component_role_weight_audit
from app.services.backtest_realism_audit import build_backtest_realism_audit
from app.services.backtest_risk_contribution_audit import build_risk_contribution_audit
from app.services.backtest_validation_efficacy import build_validation_efficacy_audit
from app.runtime import (
    FINAL_SELECTION_DECISION_V2_SCHEMA_VERSION,
    PRACTICAL_VALIDATION_RESULT_SCHEMA_VERSION,
)
from app.services.backtest_practical_validation_source import (
    VALIDATION_PROFILE_OPTIONS,
    VALIDATION_PROFILE_QUESTIONS,
    _now_text,
    _optional_float,
    _slug,
    build_selection_source_from_candidate_draft,
    build_selection_source_from_saved_mix_prefill,
    build_selection_source_from_weighted_mix_prefill,
    build_validation_profile,
    source_components_dataframe,
)
from app.services.backtest_practical_validation_stress_sensitivity import (
    _baseline_rows,
    _build_overfit_audit,
    _correlation_risk_evidence,
    _market_context_evidence,
    _rolling_validation_evidence,
    _sensitivity_interpretation_result,
    _sensitivity_rows,
    _stress_interpretation_result,
    _stress_window_rows,
    build_robustness_lab_board,
)
from app.services.backtest_temporal_validation import (
    REGIME_MACRO_SERIES,
    build_oos_holdout_validation,
    build_regime_split_validation,
    build_walkforward_validation,
)
from finance.loaders import load_macro_series_observations, load_price_history


PRIMARY_TICKER_BUCKETS = {
    "SPY": "equity",
    "VOO": "equity",
    "VTI": "equity",
    "IVV": "equity",
    "QQQ": "equity",
    "DIA": "equity",
    "IWM": "equity",
    "VEA": "equity",
    "EFA": "equity",
    "EEM": "equity",
    "VWO": "equity",
    "TLT": "bond",
    "IEF": "bond",
    "SHY": "bond",
    "BND": "bond",
    "AGG": "bond",
    "LQD": "bond",
    "HYG": "bond",
    "TIP": "bond",
    "BIL": "cash",
    "SHV": "cash",
    "SGOV": "cash",
    "TBIL": "cash",
    "GLD": "gold",
    "IAU": "gold",
    "SGOL": "gold",
    "DBC": "commodity",
    "PDBC": "commodity",
    "USO": "commodity",
}
SECTOR_TICKERS = {
    "XLB",
    "XLC",
    "XLE",
    "XLF",
    "XLI",
    "XLK",
    "XLP",
    "XLRE",
    "XLU",
    "XLV",
    "XLY",
    "SMH",
    "SOXX",
    "IBB",
    "XBI",
    "IYR",
}
LEVERAGED_TICKERS = {"TQQQ", "UPRO", "SPXL", "SSO", "QLD", "TECL", "SOXL", "TMF"}
INVERSE_TICKERS = {"SH", "PSQ", "SDS", "QID", "SQQQ", "SPXU", "TZA", "DOG", "DXD"}
TOKEN_PATTERN = re.compile(r"\b[A-Z]{2,6}\b")

def _component_title(component: dict[str, Any]) -> str:
    return str(component.get("title") or component.get("strategy_name") or component.get("component_id") or "-")


def _component_weight(component: dict[str, Any]) -> float:
    return _optional_float(component.get("target_weight")) or 0.0


def _extract_ticker_tokens(value: Any) -> list[str]:
    tokens: list[str] = []
    if isinstance(value, (list, tuple, set)):
        raw_values = [str(item or "") for item in value]
    else:
        raw_values = [str(value or "")]
    for raw in raw_values:
        for token in TOKEN_PATTERN.findall(raw.upper()):
            if token in PRIMARY_TICKER_BUCKETS or token in SECTOR_TICKERS or token in LEVERAGED_TICKERS or token in INVERSE_TICKERS:
                tokens.append(token)
    return sorted(set(tokens))


def _component_tickers(component: dict[str, Any]) -> list[str]:
    tokens: list[str] = []
    for field in ("universe", "benchmark", "title", "strategy_name", "strategy_family", "strategy_key"):
        tokens.extend(_extract_ticker_tokens(component.get(field)))
    return sorted(set(tokens))


def _component_primary_buckets(component: dict[str, Any]) -> tuple[list[str], list[str]]:
    tickers = _component_tickers(component)
    buckets: list[str] = []
    flags: list[str] = []
    for ticker in tickers:
        if ticker in LEVERAGED_TICKERS:
            flags.append("leveraged")
            buckets.append("equity")
        elif ticker in INVERSE_TICKERS:
            flags.append("inverse")
            buckets.append("equity")
        elif ticker in SECTOR_TICKERS:
            flags.append("sector_theme")
            buckets.append("equity")
        else:
            bucket = PRIMARY_TICKER_BUCKETS.get(ticker)
            if bucket:
                buckets.append(bucket)
    text = " ".join(str(component.get(key) or "") for key in ("title", "strategy_family", "strategy_key")).lower()
    if not buckets:
        if any(term in text for term in ("sector", "growth", "equal", "relative", "spy", "qqq")):
            buckets.append("equity")
        elif any(term in text for term in ("gold", "commodity")):
            buckets.append("gold")
        elif any(term in text for term in ("bond", "treasury", "cash")):
            buckets.append("bond")
        elif "gtaa" in text:
            buckets.append("multi_asset")
    return sorted(set(buckets)), sorted(set(flags))


def _build_exposure_summary(active_components: list[dict[str, Any]]) -> dict[str, Any]:
    asset_exposure = {
        "equity": 0.0,
        "bond": 0.0,
        "cash": 0.0,
        "gold": 0.0,
        "commodity": 0.0,
        "multi_asset": 0.0,
        "unknown": 0.0,
    }
    flag_exposure = {"sector_theme": 0.0, "leveraged": 0.0, "inverse": 0.0}
    component_rows: list[dict[str, Any]] = []
    for component in active_components:
        weight = _component_weight(component)
        buckets, flags = _component_primary_buckets(component)
        if not buckets:
            buckets = ["unknown"]
        bucket_weight = weight / len(buckets) if buckets else weight
        for bucket in buckets:
            asset_exposure[bucket] = asset_exposure.get(bucket, 0.0) + bucket_weight
        for flag in flags:
            flag_exposure[flag] = flag_exposure.get(flag, 0.0) + weight
        component_rows.append(
            {
                "Component": _component_title(component),
                "Weight": weight,
                "Tickers": ", ".join(_component_tickers(component)) or "-",
                "Primary Buckets": ", ".join(buckets),
                "Flags": ", ".join(flags) or "-",
            }
        )
    known_weight = sum(value for bucket, value in asset_exposure.items() if bucket != "unknown")
    return {
        "asset_exposure": {key: round(value, 4) for key, value in asset_exposure.items()},
        "flag_exposure": {key: round(value, 4) for key, value in flag_exposure.items()},
        "known_weight": round(known_weight, 4),
        "unknown_weight": round(asset_exposure.get("unknown", 0.0), 4),
        "component_rows": component_rows,
    }


def _component_provider_symbol_weights(active_components: list[dict[str, Any]]) -> dict[str, float]:
    """Approximate provider lookup weights from component target weights and ETF universes."""
    weights: dict[str, float] = {}
    for component in active_components:
        component_weight = _component_weight(component)
        contract = dict(component.get("contract") or {})
        replay_contract = dict(component.get("replay_contract") or {})
        settings = dict(replay_contract.get("settings_snapshot") or {})
        raw_values = [component.get("universe"), contract.get("tickers"), settings.get("tickers")]
        tickers: list[str] = []
        for value in raw_values:
            if isinstance(value, str):
                tickers.extend(part.strip().upper() for part in re.split(r"[,\\s]+", value) if part.strip())
            elif isinstance(value, (list, tuple, set)):
                tickers.extend(str(part or "").strip().upper() for part in value if str(part or "").strip())
        if not tickers:
            tickers.extend(_component_tickers(component))
        benchmark = str(component.get("benchmark") or "").strip().upper()
        tickers = [ticker for ticker in dict.fromkeys(tickers) if ticker and ticker != "-" and ticker != benchmark]
        if not tickers:
            continue
        ticker_weight = component_weight / len(tickers)
        for ticker in tickers:
            weights[ticker] = weights.get(ticker, 0.0) + ticker_weight
    return {ticker: round(weight, 4) for ticker, weight in sorted(weights.items()) if weight > 0.0}


def _component_data_coverage_symbol_weights(active_components: list[dict[str, Any]]) -> dict[str, float]:
    """Approximate price / listing coverage weights from component universes and benchmarks."""
    weights: dict[str, float] = {}
    for component in active_components:
        component_weight = _component_weight(component)
        tickers = _component_universe_tickers(component)
        if not tickers:
            tickers = _component_tickers(component)
        tickers = [ticker for ticker in dict.fromkeys(tickers) if ticker and ticker != "-"]
        if not tickers:
            continue
        ticker_weight = component_weight / len(tickers)
        for ticker in tickers:
            weights[ticker] = weights.get(ticker, 0.0) + ticker_weight
    return {ticker: round(weight, 4) for ticker, weight in sorted(weights.items()) if weight > 0.0}


def _provider_origin_label(provider_area: dict[str, Any]) -> str:
    status = str(provider_area.get("status") or "").lower()
    if status in {"actual", "partial"}:
        return "provider_snapshot"
    if status == "bridge":
        return "db_bridge"
    if status == "proxy":
        return "price_proxy"
    return "provider_context"


def _domain_result(
    *,
    domain: str,
    title: str,
    status: str,
    summary: str,
    origin: str,
    key_metric: Any = "-",
    metrics: dict[str, Any] | None = None,
    evidence_rows: list[dict[str, Any]] | None = None,
    limitations: list[str] | None = None,
    next_action: str = "",
    profile_effect: str = "",
) -> dict[str, Any]:
    return {
        "domain": domain,
        "title": title,
        "status": status,
        "origin": origin,
        "key_metric": key_metric,
        "summary": summary,
        "metrics": dict(metrics or {}),
        "evidence_rows": list(evidence_rows or []),
        "limitations": list(limitations or []),
        "next_action": next_action,
        "profile_effect": profile_effect,
    }


def _diagnostic_display_rows(diagnostics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "Domain": item.get("title"),
            "Status": item.get("status"),
            "Key Metric": item.get("key_metric"),
            "Reason": item.get("summary"),
            "Origin": item.get("origin"),
            "Profile Effect": item.get("profile_effect") or "-",
            "Next Action": item.get("next_action") or "-",
        }
        for item in diagnostics
    ]


def _status_counts(diagnostics: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"PASS": 0, "REVIEW": 0, "BLOCKED": 0, "NOT_RUN": 0}
    for item in diagnostics:
        status = str(item.get("status") or "NOT_RUN")
        counts[status] = counts.get(status, 0) + 1
    return counts


def _diagnostic_score(
    diagnostics: list[dict[str, Any]],
    hard_blockers: list[str],
    profile: dict[str, Any] | None = None,
) -> float:
    if hard_blockers:
        return 0.0
    status_weights = {"PASS": 1.0, "REVIEW": 0.65, "NOT_RUN": 0.35, "BLOCKED": 0.0}
    domain_weights = dict((profile or {}).get("domain_weights") or {})
    if not diagnostics:
        return 0.0
    weighted_score = 0.0
    total_weight = 0.0
    for item in diagnostics:
        domain = str(item.get("domain") or "")
        domain_weight = float(domain_weights.get(domain, 1.0) or 1.0)
        total_weight += domain_weight
        weighted_score += status_weights.get(str(item.get("status") or "NOT_RUN"), 0.35) * domain_weight
    if total_weight <= 0.0:
        return 0.0
    return round(weighted_score / total_weight * 10.0, 1)


def _profile_score_rows(diagnostics: list[dict[str, Any]], profile: dict[str, Any]) -> list[dict[str, Any]]:
    status_weights = {"PASS": 1.0, "REVIEW": 0.65, "NOT_RUN": 0.35, "BLOCKED": 0.0}
    domain_weights = dict(profile.get("domain_weights") or {})
    rows: list[dict[str, Any]] = []
    for item in diagnostics:
        domain = str(item.get("domain") or "")
        domain_weight = float(domain_weights.get(domain, 1.0) or 1.0)
        status = str(item.get("status") or "NOT_RUN")
        rows.append(
            {
                "Domain": item.get("title"),
                "Status": status,
                "Profile Weight": round(domain_weight, 4),
                "Status Points": status_weights.get(status, 0.35),
                "Weighted Points": round(status_weights.get(status, 0.35) * domain_weight, 4),
                "Profile": profile.get("profile_label"),
            }
        )
    return rows


def _component_universe_tickers(component: dict[str, Any]) -> list[str]:
    contract = dict(component.get("contract") or {})
    replay_contract = dict(component.get("replay_contract") or {})
    settings = dict(replay_contract.get("settings_snapshot") or {})
    raw_values: list[Any] = [
        component.get("universe"),
        contract.get("tickers"),
        settings.get("tickers"),
        component.get("benchmark"),
    ]
    tokens: list[str] = []
    for value in raw_values:
        if isinstance(value, str):
            tokens.extend(part.strip().upper() for part in re.split(r"[,\\s]+", value) if part.strip())
        elif isinstance(value, (list, tuple, set)):
            tokens.extend(str(part or "").strip().upper() for part in value if str(part or "").strip())
    tokens.extend(_component_tickers(component))
    seen: set[str] = set()
    clean: list[str] = []
    for token in tokens:
        if not token or token in seen or token == "-":
            continue
        seen.add(token)
        clean.append(token)
    return clean


def _build_curve_context(
    source_row: dict[str, Any],
    active_components: list[dict[str, Any]],
    *,
    replay_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_period = dict(source_row.get("period") or {})
    replay_row = dict(replay_result or {})
    runtime_curve_source = str(replay_row.get("curve_source") or "actual_runtime_replay")
    replay_component_curves = {
        str(item.get("component_id") or ""): item
        for item in list(replay_row.get("component_results") or [])
        if item.get("result_curve")
    }
    source_curve = _normalize_result_curve(
        source_row.get("result_curve")
        or source_row.get("weighted_curve")
        or dict(source_row.get("source_snapshot") or {}).get("weighted_curve_snapshot")
    )
    replay_curve = normalize_validation_curve(replay_row.get("portfolio_curve"))
    if not replay_curve.empty:
        source_curve = replay_curve
        portfolio_curve_source = runtime_curve_source
    else:
        portfolio_curve_source = ""
    component_curves: list[dict[str, Any]] = []
    for component in active_components:
        replay_component = replay_component_curves.get(str(component.get("component_id") or ""))
        component_curve = normalize_validation_curve(dict(replay_component or {}).get("result_curve"))
        component_source = runtime_curve_source if not component_curve.empty else ""
        if component_curve.empty:
            component_curve = _normalize_result_curve(component.get("result_curve") or component.get("curve_snapshot"))
            component_source = "embedded_result_curve" if not component_curve.empty else ""
        if component_curve.empty:
            tickers = _component_universe_tickers(component)
            component_period = dict(component.get("period") or {})
            component_curve, proxy_meta = _price_proxy_curve(
                tickers,
                start=component.get("period_start") or component_period.get("start") or source_period.get("actual_start") or source_period.get("start"),
                end=component.get("period_end") or component_period.get("end") or source_period.get("actual_end") or source_period.get("end"),
            )
            component_source = str(proxy_meta.get("source") or proxy_meta.get("status") or "proxy_unavailable")
        component_curves.append(
            {
                "component": _component_title(component),
                "weight": _component_weight(component),
                "curve": component_curve,
                "source": component_source,
                "rows": len(component_curve) if isinstance(component_curve, pd.DataFrame) else 0,
            }
        )
    if source_curve.empty:
        source_curve = _combine_component_curves(component_curves)
        portfolio_curve_source = "component_curve_weighted_proxy" if not source_curve.empty else "unavailable"
    elif not portfolio_curve_source:
        portfolio_curve_source = "embedded_source_curve"

    benchmark_ticker = next(
        (
            str(component.get("benchmark") or "").strip().upper()
            for component in active_components
            if str(component.get("benchmark") or "").strip() not in {"", "-"}
        ),
        "",
    )
    benchmark_curve = normalize_validation_curve(replay_row.get("benchmark_curve"))
    benchmark_meta: dict[str, Any] = {"status": "NOT_RUN", "reason": "benchmark 없음"}
    if not benchmark_curve.empty:
        benchmark_meta = {
            "status": "PASS",
            "source": runtime_curve_source,
            "tickers": [replay_row.get("benchmark_ticker") or benchmark_ticker],
        }
    elif benchmark_curve.empty:
        benchmark_curve = _normalize_result_curve(source_row.get("benchmark_curve"))
    if benchmark_curve.empty and benchmark_ticker:
        start_value = source_period.get("actual_start") or source_period.get("start")
        end_value = source_period.get("actual_end") or source_period.get("end")
        if not source_curve.empty:
            start_value = source_curve["Date"].min()
            end_value = source_curve["Date"].max()
        benchmark_curve, benchmark_meta = _price_proxy_curve([benchmark_ticker], start=start_value, end=end_value)
    elif not benchmark_curve.empty and benchmark_meta.get("source") != runtime_curve_source:
        benchmark_meta = {"status": "PASS", "source": "embedded_benchmark_curve", "tickers": [benchmark_ticker]}

    return {
        "portfolio_curve": source_curve,
        "portfolio_curve_source": portfolio_curve_source,
        "portfolio_summary": _summary_metrics_from_curve(source_curve, name="Candidate Portfolio"),
        "component_curves": component_curves,
        "benchmark_ticker": benchmark_ticker,
        "benchmark_curve": benchmark_curve,
        "benchmark_meta": benchmark_meta,
        "curve_rows": [
            {
                "Component": item.get("component"),
                "Weight": item.get("weight"),
                "Curve Source": item.get("source"),
                "Rows": item.get("rows"),
            }
            for item in component_curves
        ],
    }


def _operability_rows(active_components: list[dict[str, Any]], source_period: dict[str, Any]) -> list[dict[str, Any]]:
    tickers = sorted({ticker for component in active_components for ticker in _component_universe_tickers(component)})
    if not tickers:
        return []
    end_value = source_period.get("actual_end") or source_period.get("end")
    end_ts = _parse_date(end_value)
    start_ts = end_ts - pd.Timedelta(days=90) if end_ts is not None else None
    try:
        history = load_price_history(
            symbols=tickers,
            start=_format_date(start_ts),
            end=_format_date(end_ts),
            timeframe="1d",
        )
    except Exception:
        return [
            {
                "Ticker": ticker,
                "Status": "NOT_RUN",
                "Latest Close": None,
                "Avg Dollar Volume 60D": None,
                "Reason": "price DB load failed",
            }
            for ticker in tickers
        ]
    if history.empty:
        return [
            {
                "Ticker": ticker,
                "Status": "NOT_RUN",
                "Latest Close": None,
                "Avg Dollar Volume 60D": None,
                "Reason": "price history 없음",
            }
            for ticker in tickers
        ]
    rows: list[dict[str, Any]] = []
    for ticker in tickers:
        ticker_df = history[history["symbol"].astype(str).str.upper() == ticker].copy()
        if ticker_df.empty:
            rows.append({"Ticker": ticker, "Status": "NOT_RUN", "Latest Close": None, "Avg Dollar Volume 60D": None, "Reason": "missing"})
            continue
        ticker_df["close"] = pd.to_numeric(ticker_df["close"], errors="coerce")
        ticker_df["volume"] = pd.to_numeric(ticker_df["volume"], errors="coerce")
        latest_close = _optional_float(ticker_df.sort_values("date")["close"].dropna().iloc[-1]) if not ticker_df["close"].dropna().empty else None
        avg_dollar_volume = float((ticker_df["close"] * ticker_df["volume"]).dropna().tail(60).mean()) if not (ticker_df["close"] * ticker_df["volume"]).dropna().empty else None
        status = "PASS"
        reason = "basic price/volume available"
        if latest_close is None or latest_close < 5.0:
            status = "REVIEW"
            reason = "low or missing latest price"
        if avg_dollar_volume is None or avg_dollar_volume < 5_000_000:
            status = "REVIEW"
            reason = "low or missing average dollar volume"
        rows.append(
            {
                "Ticker": ticker,
                "Status": status,
                "Latest Close": latest_close,
                "Avg Dollar Volume 60D": avg_dollar_volume,
                "Reason": reason,
            }
        )
    return rows


def _load_macro_regime_history(start: Any, end: Any) -> tuple[pd.DataFrame, str | None]:
    try:
        frame = load_macro_series_observations(
            REGIME_MACRO_SERIES,
            start=_format_date(start),
            end=_format_date(end),
        )
    except Exception as exc:
        return pd.DataFrame(), str(exc)
    return frame if isinstance(frame, pd.DataFrame) else pd.DataFrame(), None


def build_practical_validation_result(
    source: dict[str, Any],
    validation_profile: dict[str, Any] | None = None,
    replay_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the structured Practical Validation result used by Final Review V2."""
    now = _now_text()
    source_row = dict(source or {})
    profile_row = build_validation_profile(
        str((validation_profile or {}).get("profile_id") or "balanced_core"),
        dict((validation_profile or {}).get("answers") or {}),
    )
    thresholds = dict(profile_row.get("thresholds") or {})
    answers = dict(profile_row.get("answers") or {})
    source_id = str(source_row.get("selection_source_id") or "").strip()
    components = [dict(item or {}) for item in list(source_row.get("components") or [])]
    active_components = [
        component
        for component in components
        if (_optional_float(component.get("target_weight")) or 0.0) > 0.0
    ]
    target_weight_total = round(
        sum((_optional_float(component.get("target_weight")) or 0.0) for component in active_components),
        4,
    )
    data_trust = dict(source_row.get("data_trust") or {})
    real_money = dict(source_row.get("real_money_signal") or {})
    hard_blockers: list[str] = []
    review_gaps: list[str] = []
    source_period = dict(source_row.get("period") or {})
    source_summary = dict(source_row.get("summary") or {})
    source_title = source_row.get("source_title") or source_id

    if not source_id:
        hard_blockers.append("selection_source_id 없음")
    if not active_components:
        hard_blockers.append("active component 없음")
    if active_components and abs(target_weight_total - 100.0) > 0.01:
        hard_blockers.append(f"target weight 합계가 100%가 아님: {target_weight_total:.2f}%")
    if str(data_trust.get("status") or "").lower() in {"error", "blocked"}:
        hard_blockers.append(f"Data Trust blocked: {data_trust.get('status')}")
    if real_money.get("deployment") in {"blocked", "deployment_blocked"}:
        hard_blockers.append("Real-Money deployment blocked")

    if data_trust.get("warning_count"):
        review_gaps.append(f"Data Trust warning {data_trust.get('warning_count')}개")
    has_benchmark = any(str(component.get("benchmark") or "").strip() not in {"", "-"} for component in active_components)
    if not has_benchmark:
        review_gaps.append("benchmark snapshot 부족")
    replay_row = dict(replay_result or {})
    if replay_row and replay_row.get("status") in {"REVIEW", "BLOCKED"}:
        review_gaps.append(f"Runtime recheck status: {replay_row.get('status')}")
    period_coverage = dict(replay_row.get("period_coverage") or {})
    if period_coverage.get("status") == "REVIEW":
        review_gaps.append(
            "Runtime recheck period coverage review: "
            f"actual end {dict(period_coverage.get('actual_period') or {}).get('end') or '-'} / "
            f"requested end {dict(period_coverage.get('requested_period') or {}).get('end') or '-'}"
        )
    curve_context = _build_curve_context(source_row, active_components, replay_result=replay_row)
    portfolio_curve = _normalize_result_curve(curve_context.get("portfolio_curve"))
    benchmark_curve = _normalize_result_curve(curve_context.get("benchmark_curve"))
    portfolio_summary = dict(curve_context.get("portfolio_summary") or {})
    benchmark_parity = build_benchmark_parity(portfolio_curve, benchmark_curve)
    curve_provenance = build_curve_provenance(curve_context=curve_context, replay_result=replay_row)
    if benchmark_parity.get("status") == "REVIEW":
        review_gaps.append("Benchmark / comparator parity review 필요")
    # Provider snapshots answer "what can be verified at validation time", not the saved backtest end.
    provider_as_of = _format_date(now) or _format_date(source_row.get("created_at"))
    if provider_as_of is None:
        provider_as_of = _format_date(source_period.get("actual_end") or source_period.get("end"))
    if provider_as_of is None and not portfolio_curve.empty:
        provider_as_of = _format_date(portfolio_curve["Date"].max())
    provider_symbol_weights = _component_provider_symbol_weights(active_components)
    provider_context = build_provider_context(provider_symbol_weights, as_of_date=provider_as_of)
    provider_coverage = dict(provider_context.get("coverage") or {})
    provider_display_rows = list(provider_context.get("display_rows") or [])
    provider_look_through_board = dict(provider_context.get("look_through_board") or {})
    data_coverage_context = build_db_data_coverage_context(
        _component_data_coverage_symbol_weights(active_components),
        start=_format_date(source_period.get("actual_start") or source_period.get("start")),
        end=_format_date(source_period.get("actual_end") or source_period.get("end")),
        timeframe="1d",
    )

    def _compact_provider_area(area_key: str) -> dict[str, Any]:
        area = dict(provider_coverage.get(area_key) or {})
        provenance = dict(area.get("provenance") or {})
        out = {
            "status": area.get("status"),
            "diagnostic_status": area.get("diagnostic_status"),
            "freshness_status": provenance.get("freshness_status"),
            "source_mix": provenance.get("source_mix"),
        }
        if area_key == "macro":
            out["series_count"] = area.get("series_count")
            out["stale_count"] = area.get("stale_count")
            out["observation_range"] = provenance.get("observation_range")
        else:
            out["coverage_weight"] = area.get("coverage_weight")
            out["as_of_range"] = provenance.get("as_of_range")
            out["stale_weight"] = provenance.get("stale_weight")
        return out

    provider_statuses = {
        str(dict(item or {}).get("diagnostic_status") or "NOT_RUN")
        for item in provider_coverage.values()
        if isinstance(item, dict)
    }

    input_checks = [
        {
            "Criteria": "Selection source",
            "Ready": bool(source_id),
            "Current": source_id or "-",
            "Meaning": "Backtest Analysis에서 선택한 Clean V2 source가 있는지 봅니다.",
        },
        {
            "Criteria": "Active components",
            "Ready": bool(active_components),
            "Current": str(len(active_components)),
            "Meaning": "실전 검증할 component가 있는지 봅니다.",
        },
        {
            "Criteria": "Target weight total",
            "Ready": bool(active_components) and abs(target_weight_total - 100.0) <= 0.01,
            "Current": f"{target_weight_total:.2f}%",
            "Meaning": "포트폴리오 비중 합계가 100%인지 봅니다.",
        },
        {
            "Criteria": "Data Trust",
            "Ready": str(data_trust.get("status") or "").lower() not in {"error", "blocked"},
            "Current": data_trust.get("status") or "snapshot",
            "Meaning": "원본 실행 결과의 Data Trust가 차단 상태인지 봅니다.",
        },
        {
            "Criteria": "Execution boundary",
            "Ready": True,
            "Current": "live approval disabled / order instruction disabled",
            "Meaning": "이 검증은 후보 자료이며 주문이나 자동매매가 아닙니다.",
        },
        {
            "Criteria": "Curve evidence",
            "Ready": not portfolio_curve.empty,
            "Current": curve_context.get("portfolio_curve_source") or "-",
            "Meaning": "rolling / stress / baseline / correlation 계산에 쓸 portfolio curve가 있는지 봅니다.",
        },
        {
            "Criteria": "Runtime recheck",
            "Ready": replay_row.get("status") in {"PASS", "REVIEW"} and not portfolio_curve.empty,
            "Current": replay_row.get("status") or "NOT_RUN",
            "Meaning": "저장 snapshot이나 DB price proxy가 아니라 기존 strategy runtime이 실행되어 curve evidence를 만들었는지 봅니다.",
        },
        {
            "Criteria": "Runtime period coverage",
            "Ready": period_coverage.get("status") == "PASS",
            "Current": period_coverage.get("status") or "NOT_RUN",
            "Meaning": "최신 재검증 요청 종료일까지 실제 portfolio curve가 따라왔는지 봅니다.",
        },
        {
            "Criteria": "Benchmark parity",
            "Ready": benchmark_parity.get("status") == "PASS",
            "Current": benchmark_parity.get("status") or "NOT_RUN",
            "Meaning": "후보와 benchmark / comparator가 같은 기간 / coverage / frequency로 비교되는지 봅니다.",
        },
        {
            "Criteria": "Provider coverage",
            "Ready": "PASS" in provider_statuses or "REVIEW" in provider_statuses,
            "Current": ", ".join(sorted(provider_statuses)) if provider_statuses else "NOT_RUN",
            "Meaning": "ETF 운용성 / holdings / macro snapshot이 Practical Diagnostics에 연결될 수 있는지 봅니다.",
        },
    ]

    exposure_summary = _build_exposure_summary(active_components)
    asset_exposure = dict(exposure_summary.get("asset_exposure") or {})
    flag_exposure = dict(exposure_summary.get("flag_exposure") or {})
    exposure_rows = list(exposure_summary.get("component_rows") or [])
    known_weight = _optional_float(exposure_summary.get("known_weight")) or 0.0
    unknown_weight = _optional_float(exposure_summary.get("unknown_weight")) or 0.0
    provider_exposure = dict(provider_coverage.get("exposure") or {})
    if provider_exposure.get("diagnostic_status") in {"PASS", "REVIEW"}:
        provider_asset_exposure = dict(provider_exposure.get("asset_exposure") or {})
        if provider_asset_exposure:
            asset_exposure = provider_asset_exposure
            known_weight = _optional_float(provider_exposure.get("coverage_weight")) or known_weight
            unknown_weight = round(max(0.0, 100.0 - known_weight), 4)
            exposure_rows = list(provider_exposure.get("evidence_rows") or exposure_rows)
            exposure_summary = {
                **exposure_summary,
                "asset_exposure": asset_exposure,
                "known_weight": known_weight,
                "unknown_weight": unknown_weight,
                "provider_status": provider_exposure.get("status"),
                "provider_missing_symbols": list(provider_exposure.get("missing_symbols") or []),
            }
    equity_exposure = _optional_float(asset_exposure.get("equity")) or 0.0
    max_weight = max([_component_weight(component) for component in active_components], default=0.0)
    repeated_benchmarks = {
        str(component.get("benchmark") or "").strip().upper()
        for component in active_components
        if str(component.get("benchmark") or "").strip() not in {"", "-"}
    }
    duplicate_benchmark_count = max(0, len(active_components) - len(repeated_benchmarks)) if active_components else 0
    complexity_allows_inverse = answers.get("complexity_allowance") in {
        "inverse_leverage_limited",
        "tactical_high_turnover_allowed",
    }
    complexity_restricts_broad = answers.get("complexity_allowance") == "broad_etf_only"
    rolling_evidence = _rolling_validation_evidence(
        portfolio_curve,
        benchmark_curve,
        window_months=int(thresholds.get("rolling_window_months") or 36),
        mdd_review_line=float(thresholds.get("mdd_review_line") or -25.0),
    )
    walkforward_validation = build_walkforward_validation(
        portfolio_curve,
        benchmark_curve,
        portfolio_curve_source=curve_context.get("portfolio_curve_source"),
        benchmark_curve_source=dict(curve_context.get("benchmark_meta") or {}).get("source")
        or dict(curve_context.get("benchmark_meta") or {}).get("status"),
        benchmark_parity=benchmark_parity,
        window_months=int(thresholds.get("rolling_window_months") or 36),
    )
    oos_holdout_validation = build_oos_holdout_validation(
        portfolio_curve,
        benchmark_curve,
        portfolio_curve_source=curve_context.get("portfolio_curve_source"),
        benchmark_curve_source=dict(curve_context.get("benchmark_meta") or {}).get("source")
        or dict(curve_context.get("benchmark_meta") or {}).get("status"),
        benchmark_parity=benchmark_parity,
    )
    macro_history_start = (
        portfolio_curve["Date"].min()
        if not portfolio_curve.empty
        else source_period.get("actual_start") or source_period.get("start")
    )
    macro_history_end = (
        portfolio_curve["Date"].max()
        if not portfolio_curve.empty
        else source_period.get("actual_end") or source_period.get("end")
    )
    macro_history, macro_history_error = _load_macro_regime_history(macro_history_start, macro_history_end)
    regime_split_macro_source = (
        "macro_loader_error"
        if macro_history_error
        else "finance.loaders.macro.load_macro_series_observations"
    )
    regime_split_validation = build_regime_split_validation(
        portfolio_curve,
        benchmark_curve,
        macro_history,
        portfolio_curve_source=curve_context.get("portfolio_curve_source"),
        benchmark_curve_source=dict(curve_context.get("benchmark_meta") or {}).get("source")
        or dict(curve_context.get("benchmark_meta") or {}).get("status"),
        macro_source=regime_split_macro_source,
        benchmark_parity=benchmark_parity,
    )
    if macro_history_error:
        regime_split_validation["limitations"] = list(regime_split_validation.get("limitations") or []) + [
            f"Macro history loader failed: {macro_history_error}"
        ]

    input_status = "BLOCKED" if hard_blockers else "REVIEW" if review_gaps else "PASS"
    diagnostics: list[dict[str, Any]] = [
        _domain_result(
            domain="input_evidence_layer",
            title="1. Input Evidence Layer",
            status=input_status,
            origin="existing_evidence",
            key_metric=f"{len(active_components)} components / {target_weight_total:.2f}%",
            summary="원본 source, 비중 합계, Data Trust, 실행 경계 조건을 확인했습니다.",
            evidence_rows=input_checks,
            limitations=[] if input_status == "PASS" else hard_blockers + review_gaps,
            next_action="BLOCKED 항목이 있으면 Backtest Analysis에서 source를 다시 구성합니다.",
        )
    ]

    if not active_components:
        allocation_status = "BLOCKED"
        allocation_summary = "검증할 component가 없어 자산배분 적합성을 판단할 수 없습니다."
    elif known_weight <= 0.0:
        allocation_status = "NOT_RUN"
        allocation_summary = "ticker / 자산군 look-through coverage가 없어 proxy 분류를 실행하지 못했습니다."
    elif unknown_weight > 50.0:
        allocation_status = "REVIEW"
        allocation_summary = f"자산군 미분류 비중이 {unknown_weight:.1f}%라 look-through 보강이 필요합니다."
    elif equity_exposure > (_optional_float(thresholds.get("equity_exposure_review")) or 85.0):
        allocation_status = "REVIEW"
        allocation_summary = f"주식성 노출이 {equity_exposure:.1f}%로 {profile_row['profile_label']} 기준보다 높습니다."
    else:
        allocation_status = "PASS"
        allocation_summary = "현재 proxy 기준 자산군 분산은 프로필 기준 안에 있습니다."
    allocation_origin = "new_diagnostic"
    allocation_limitations = ["holdings look-through 데이터가 없으면 ticker/proxy 분류로만 판단합니다."]
    if provider_exposure.get("diagnostic_status") in {"PASS", "REVIEW"}:
        allocation_origin = _provider_origin_label(provider_exposure)
        allocation_status = str(provider_exposure.get("diagnostic_status") or allocation_status)
        if equity_exposure > (_optional_float(thresholds.get("equity_exposure_review")) or 85.0):
            allocation_status = "REVIEW"
            allocation_summary = f"Provider exposure 기준 주식성 노출이 {equity_exposure:.1f}%로 {profile_row['profile_label']} 기준보다 높습니다."
        else:
            allocation_summary = (
                f"Provider exposure snapshot 기준 자산군 coverage가 "
                f"{_optional_float(provider_exposure.get('coverage_weight')) or 0.0:.1f}%입니다."
            )
        allocation_limitations = [
            "ETF-of-ETF는 현재 1차 holdings / exposure 기준이며, 2차 underlying look-through는 후속입니다.",
            "Provider coverage가 없는 ETF는 missing symbol로 남깁니다.",
        ]
    elif active_components and allocation_status == "PASS":
        allocation_status = "REVIEW"
        allocation_summary = "ETF exposure provider snapshot이 없어 ticker/proxy 자산군 분류만 확인했습니다."
    diagnostics.append(
        _domain_result(
            domain="asset_allocation_fit",
            title="2. Asset Allocation Fit",
            status=allocation_status,
            origin=allocation_origin,
            key_metric=f"equity {equity_exposure:.1f}% / unknown {unknown_weight:.1f}%",
            summary=allocation_summary,
            metrics=exposure_summary,
            evidence_rows=exposure_rows,
            limitations=allocation_limitations,
            next_action="미분류 또는 과도한 주식성 노출이 있으면 ETF 구성과 목적을 재확인합니다.",
            profile_effect=f"{profile_row['profile_label']} equity review line {thresholds.get('equity_exposure_review')}%",
        )
    )

    if not active_components:
        concentration_status = "BLOCKED"
        concentration_summary = "검증할 component가 없어 집중도를 판단할 수 없습니다."
    elif max_weight > (_optional_float(thresholds.get("max_weight_review")) or 75.0):
        concentration_status = "REVIEW"
        concentration_summary = f"최대 component 비중이 {max_weight:.1f}%로 프로필 기준을 넘었습니다."
    elif complexity_restricts_broad and (flag_exposure.get("sector_theme", 0.0) or 0.0) > 0.0:
        concentration_status = "REVIEW"
        concentration_summary = "사용자 프로필은 broad ETF를 선호하지만 sector/theme 노출이 있습니다."
    else:
        concentration_status = "PASS"
        concentration_summary = "component 비중 집중도와 proxy exposure가 즉시 차단 수준은 아닙니다."
    provider_holdings = dict(provider_coverage.get("holdings") or {})
    concentration_origin = "new_diagnostic"
    concentration_key_metric = f"max component {max_weight:.1f}%"
    concentration_metrics = {
        "max_component_weight": round(max_weight, 4),
        "duplicate_benchmark_count": duplicate_benchmark_count,
        "flag_exposure": flag_exposure,
    }
    concentration_evidence_rows = exposure_rows
    concentration_limitations = ["ETF holdings-level overlap은 아직 계산하지 않고 ticker/proxy signal로 먼저 표시합니다."]
    if provider_holdings.get("diagnostic_status") in {"PASS", "REVIEW"}:
        concentration_origin = _provider_origin_label(provider_holdings)
        concentration_status = str(provider_holdings.get("diagnostic_status") or concentration_status)
        concentration_summary = str(provider_holdings.get("summary") or concentration_summary)
        concentration_key_metric = (
            f"top holding {dict(provider_holdings.get('metrics') or {}).get('top_holding_weight', 0.0)}% / "
            f"coverage {_optional_float(provider_holdings.get('coverage_weight')) or 0.0:.1f}%"
        )
        concentration_metrics = {
            **concentration_metrics,
            **dict(provider_holdings.get("metrics") or {}),
            "provider_coverage_weight": provider_holdings.get("coverage_weight"),
            "provider_missing_symbols": list(provider_holdings.get("missing_symbols") or []),
        }
        concentration_evidence_rows = list(provider_holdings.get("evidence_rows") or [])
        concentration_limitations = [
            "Holdings overlap은 최신 저장 snapshot 기준 compact top exposure만 저장합니다.",
            "Full holdings row는 DB에만 있고 Practical Validation JSONL에는 저장하지 않습니다.",
        ]
    elif active_components and concentration_status == "PASS":
        concentration_status = "REVIEW"
        concentration_summary = "ETF holdings snapshot이 없어 holdings overlap 대신 component / ticker proxy 집중도만 확인했습니다."
    diagnostics.append(
        _domain_result(
            domain="concentration_overlap_exposure",
            title="3. Concentration / Overlap / Exposure",
            status=concentration_status,
            origin=concentration_origin,
            key_metric=concentration_key_metric,
            summary=concentration_summary,
            metrics=concentration_metrics,
            evidence_rows=concentration_evidence_rows,
            limitations=concentration_limitations,
            next_action="중복 benchmark 또는 sector/theme 집중이 있으면 단순 대안과 목적을 비교합니다.",
            profile_effect=f"{profile_row['profile_label']} max weight review line {thresholds.get('max_weight_review')}%",
        )
    )

    correlation_evidence = _correlation_risk_evidence(list(curve_context.get("component_curves") or []))
    if len(active_components) <= 1:
        diversification_status = "REVIEW"
        diversification_summary = "단일 component 후보라 component 간 상관 / 위험기여 분산을 확인할 수 없습니다."
        diversification_rows = [
            {
                "Component": _component_title(component),
                "Weight": _component_weight(component),
                "Benchmark": component.get("benchmark") or "-",
                "Replay Contract": "present" if component.get("replay_contract") else "missing",
            }
            for component in active_components
        ]
        diversification_metrics = {}
    elif correlation_evidence.get("status") in {"PASS", "REVIEW"}:
        diversification_status = str(correlation_evidence.get("status"))
        diversification_summary = str(correlation_evidence.get("summary") or "상관 / 위험기여 proxy 계산됨")
        diversification_rows = list(correlation_evidence.get("rows") or [])
        diversification_metrics = dict(correlation_evidence.get("metrics") or {})
    else:
        diversification_status = "NOT_RUN"
        diversification_summary = str(correlation_evidence.get("summary") or "component별 수익률 replay matrix가 아직 없어 correlation / risk contribution은 후속 계산이 필요합니다.")
        diversification_rows = list(curve_context.get("curve_rows") or [])
        diversification_metrics = dict(correlation_evidence.get("metrics") or {})
    diagnostics.append(
        _domain_result(
            domain="correlation_diversification_risk_contribution",
            title="4. Correlation / Diversification / Risk Contribution",
            status=diversification_status,
            origin="new_diagnostic",
            key_metric=f"{len(active_components)} components",
            summary=diversification_summary,
            metrics=diversification_metrics,
            evidence_rows=diversification_rows,
            limitations=["curve가 embedded 결과가 아니라 DB price proxy일 수 있으므로 실제 전략 path와 다를 수 있습니다."],
            next_action="mix 후보라면 component별 return curve replay를 붙여 위험기여도를 계산합니다.",
        )
    )

    provider_macro = dict(provider_coverage.get("macro") or {})
    provider_regime = dict(provider_macro.get("regime") or {})
    provider_sentiment = dict(provider_macro.get("sentiment") or {})
    regime_evidence = _market_context_evidence(benchmark_curve if not benchmark_curve.empty else portfolio_curve, label="Regime")
    if provider_regime.get("diagnostic_status") in {"PASS", "REVIEW"}:
        regime_status = str(provider_regime.get("diagnostic_status"))
        regime_origin = "provider_snapshot"
        regime_key_metric = provider_regime.get("key_metric") or "FRED macro snapshot"
        regime_summary = str(provider_regime.get("summary") or provider_macro.get("summary") or "FRED macro snapshot을 확인했습니다.")
        regime_metrics = dict(provider_macro.get("metrics") or {})
        regime_rows = list(provider_regime.get("evidence_rows") or provider_macro.get("evidence_rows") or [])
        regime_limitations = ["FRED snapshot은 market-context evidence이며 trade signal이나 hard blocker가 아닙니다."]
        regime_next_action = "VIX / yield curve / credit spread가 review 상태이면 Final Review에서 현재 국면과 후보 목적을 같이 확인합니다."
    else:
        regime_status = str(regime_evidence.get("status") or "NOT_RUN")
        if regime_status == "PASS":
            regime_status = "REVIEW"
        regime_origin = "market_proxy" if regime_evidence.get("status") != "NOT_RUN" else "future_connector"
        regime_key_metric = "benchmark recent context"
        regime_summary = str(regime_evidence.get("summary") or "금리, 인플레이션, 경기 국면 데이터 connector가 아직 붙지 않아 macro suitability는 기록만 남깁니다.")
        regime_metrics = dict(regime_evidence.get("metrics") or {})
        regime_rows = list(regime_evidence.get("rows") or [])
        regime_limitations = ["현재는 benchmark recent return/drawdown/vol proxy이며, FRED macro connector data가 없으면 proxy로만 표시합니다."]
        regime_next_action = "Workspace > Ingestion에서 Macro Context Snapshot을 수집합니다."
    if regime_split_validation.get("status") in {"PASS", "REVIEW"}:
        regime_summary = f"{regime_summary} Historical split: {regime_split_validation.get('summary')}"
        regime_metrics = {
            **regime_metrics,
            "historical_regime_split": dict(regime_split_validation.get("metrics") or {}),
        }
        regime_rows = regime_rows + list(regime_split_validation.get("rows") or [])
        regime_limitations = regime_limitations + [
            "Historical regime split은 월별 compact evidence이며 full macro series / raw curve는 workflow JSONL에 저장하지 않습니다."
        ]
    diagnostics.append(
        _domain_result(
            domain="regime_macro_suitability",
            title="5. Regime / Macro Suitability",
            status=regime_status,
            origin=regime_origin,
            key_metric=regime_key_metric,
            summary=regime_summary,
            metrics=regime_metrics,
            evidence_rows=regime_rows,
            limitations=regime_limitations,
            next_action=regime_next_action,
        )
    )
    sentiment_evidence = _market_context_evidence(benchmark_curve if not benchmark_curve.empty else portfolio_curve, label="Risk-on/off")
    if provider_sentiment.get("diagnostic_status") in {"PASS", "REVIEW"}:
        sentiment_status = str(provider_sentiment.get("diagnostic_status"))
        sentiment_origin = "provider_snapshot"
        sentiment_key_metric = provider_sentiment.get("key_metric") or "FRED risk-on/off context"
        sentiment_summary = str(provider_sentiment.get("summary") or provider_macro.get("summary") or "FRED sentiment proxy를 확인했습니다.")
        sentiment_metrics = dict(provider_macro.get("metrics") or {})
        sentiment_rows = list(provider_sentiment.get("evidence_rows") or provider_macro.get("evidence_rows") or [])
        sentiment_limitations = ["Sentiment는 VIX / credit spread / yield curve 기반 proxy이며 단독 매수/매도 신호가 아닙니다."]
        sentiment_next_action = "Risk-off / caution이면 Final Review에서 추적 기간과 손실 감내 기준을 더 엄격히 확인합니다."
    else:
        sentiment_status = str(sentiment_evidence.get("status") or "NOT_RUN")
        if sentiment_status == "PASS":
            sentiment_status = "REVIEW"
        sentiment_origin = "market_proxy" if sentiment_evidence.get("status") != "NOT_RUN" else "future_connector"
        sentiment_key_metric = "risk-on/off proxy"
        sentiment_summary = str(sentiment_evidence.get("summary") or "VIX, Fear & Greed, credit spread / yield curve 보조지표는 아직 connector가 필요합니다.")
        sentiment_metrics = dict(sentiment_evidence.get("metrics") or {})
        sentiment_rows = list(sentiment_evidence.get("rows") or [])
        sentiment_limitations = ["VIX/Fear & Greed/Credit Spread가 아니라 price-action proxy입니다. 단독 hard blocker로 쓰지 않습니다."]
        sentiment_next_action = "Workspace > Ingestion에서 Macro Context Snapshot을 수집합니다."
    diagnostics.append(
        _domain_result(
            domain="sentiment_risk_on_off_overlay",
            title="6. Sentiment / Risk-On-Off Overlay",
            status=sentiment_status,
            origin=sentiment_origin,
            key_metric=sentiment_key_metric,
            summary=sentiment_summary,
            metrics=sentiment_metrics,
            evidence_rows=sentiment_rows,
            limitations=sentiment_limitations,
            next_action=sentiment_next_action,
        )
    )

    stress_rows = _stress_window_rows(source_period, portfolio_curve=portfolio_curve, benchmark_curve=benchmark_curve)
    stress_interpretation = _stress_interpretation_result(
        stress_rows,
        provider_macro=provider_macro,
        asset_exposure=asset_exposure,
    )
    covered_stress_count = int(stress_interpretation.get("covered_count") or 0)
    computed_stress_count = int(stress_interpretation.get("computed_count") or 0)
    stress_status = str(stress_interpretation.get("status") or "NOT_RUN")
    stress_summary = str(stress_interpretation.get("summary") or "stress interpretation을 생성하지 못했습니다.")
    diagnostics.append(
        _domain_result(
            domain="stress_scenario_diagnostics",
            title="7. Stress / Scenario Diagnostics",
            status=stress_status,
            origin="new_diagnostic",
            key_metric=f"{computed_stress_count}/{covered_stress_count} computed stress windows",
            summary=stress_summary,
            metrics=stress_interpretation,
            evidence_rows=list(stress_interpretation.get("rows") or []) + stress_rows,
            limitations=[
                "Compact monthly curve만 있으면 짧은 stress window는 NOT_RUN으로 남을 수 있습니다.",
                "Daily runtime replay가 연결된 window만 구간 return / MDD / benchmark spread를 계산합니다.",
            ],
            next_action=(
                "NOT_RUN covered window가 있으면 최신 DB 기준 실제 전략 replay를 실행해 stress evidence를 보강합니다."
                if stress_interpretation.get("uncomputed_count")
                else "REVIEW trigger가 있으면 해당 stress scenario의 component / macro / exposure 원인을 Final Review에서 확인합니다."
            ),
        )
    )

    alternative_rows = _baseline_rows(
        portfolio_curve,
        source_period=source_period,
        success_metric=str(answers.get("alternative_success_metric") or "better_risk_adjusted"),
    )
    baseline_status_values = {str(row.get("Result Status") or "NOT_RUN") for row in alternative_rows}
    if "PASS" in baseline_status_values and "REVIEW" not in baseline_status_values:
        alternative_status = "PASS"
        alternative_summary = "후보가 1차 단순 대안 baseline 대비 선택 기준을 충족했습니다."
    elif "PASS" in baseline_status_values or "REVIEW" in baseline_status_values:
        alternative_status = "REVIEW"
        alternative_summary = "일부 단순 대안 대비 복잡성을 보상하는 근거가 부족할 수 있습니다."
    else:
        alternative_status = "NOT_RUN"
        alternative_summary = "단순 대안 baseline replay 비교를 실행하지 못했습니다."
    diagnostics.append(
        _domain_result(
            domain="alternative_portfolio_challenge",
            title="8. Alternative Portfolio Challenge",
            status=alternative_status,
            origin="new_diagnostic",
            key_metric="SPY / QQQ / 60-40 / cash-aware",
            summary=alternative_summary,
            evidence_rows=alternative_rows,
            limitations=["미래 수익 보장이 아니라 단순 대안보다 복잡한 후보를 선택할 근거를 점검하는 용도입니다. DB 가격 proxy baseline입니다."],
            next_action="후속 구현에서 baseline curve를 같은 기간으로 replay해 risk-adjusted 비교를 추가합니다.",
            profile_effect=profile_row["answer_labels"].get("alternative_success_metric", "-"),
        )
    )

    leveraged_exposure = (_optional_float(flag_exposure.get("leveraged")) or 0.0) + (
        _optional_float(flag_exposure.get("inverse")) or 0.0
    )
    if leveraged_exposure > 20.0 and not complexity_allows_inverse:
        leveraged_status = "BLOCKED"
        leveraged_summary = f"레버리지/인버스 proxy 노출이 {leveraged_exposure:.1f}%인데 사용자 프로필에서 허용되지 않았습니다."
    elif leveraged_exposure > 0.0:
        leveraged_status = "REVIEW"
        leveraged_summary = f"레버리지/인버스 proxy 노출 {leveraged_exposure:.1f}%는 운용 목적과 기간 확인이 필요합니다."
    else:
        leveraged_status = "PASS"
        leveraged_summary = "레버리지/인버스 ETF proxy 노출이 감지되지 않았습니다."
    provider_operability = dict(provider_coverage.get("operability") or {})
    provider_leverage = dict(provider_operability.get("leverage") or {})
    leveraged_origin = "new_diagnostic"
    leveraged_key_metric = f"{leveraged_exposure:.1f}%"
    leveraged_metrics = {"leveraged_inverse_exposure": round(leveraged_exposure, 4), "flag_exposure": flag_exposure}
    leveraged_rows = exposure_rows
    leveraged_limitations = ["레버리지/인버스 적합성은 ticker proxy 기반이며 holding 목적과 rebalancing cadence를 함께 봐야 합니다."]
    if provider_leverage.get("diagnostic_status") in {"PASS", "REVIEW"}:
        provider_flagged_exposure = _optional_float(provider_leverage.get("flagged_exposure")) or 0.0
        leveraged_exposure = provider_flagged_exposure
        if provider_flagged_exposure > 20.0 and not complexity_allows_inverse:
            leveraged_status = "BLOCKED"
            leveraged_summary = f"Provider metadata 기준 레버리지/인버스 노출이 {provider_flagged_exposure:.1f}%인데 사용자 프로필에서 허용되지 않았습니다."
        elif provider_flagged_exposure > 0.0:
            leveraged_status = "REVIEW"
            leveraged_summary = f"Provider metadata 기준 레버리지/인버스 노출 {provider_flagged_exposure:.1f}%는 운용 목적과 기간 확인이 필요합니다."
        else:
            leveraged_status = "PASS"
            leveraged_summary = "Provider metadata 기준 레버리지/인버스 ETF가 감지되지 않았습니다."
        leveraged_origin = _provider_origin_label(provider_operability)
        leveraged_key_metric = f"{provider_flagged_exposure:.1f}%"
        leveraged_metrics = {
            "leveraged_inverse_exposure": round(provider_flagged_exposure, 4),
            "provider_coverage_weight": provider_operability.get("coverage_weight"),
        }
        leveraged_rows = list(provider_leverage.get("evidence_rows") or [])
        leveraged_limitations = [
            "Provider metadata가 없는 ETF는 missing coverage로 남기며 ticker proxy보다 우선하지 않습니다.",
            "레버리지/인버스 감지는 live approval이 아니라 Final Review 확인 근거입니다.",
        ]
    elif active_components and leveraged_status == "PASS":
        leveraged_status = "REVIEW"
        leveraged_summary = "Provider product metadata가 없어 ticker proxy 기준으로만 레버리지/인버스 노출 부재를 확인했습니다."
    diagnostics.append(
        _domain_result(
            domain="leveraged_inverse_etf_suitability",
            title="9. Leveraged / Inverse ETF Suitability",
            status=leveraged_status,
            origin=leveraged_origin,
            key_metric=leveraged_key_metric,
            summary=leveraged_summary,
            metrics=leveraged_metrics,
            evidence_rows=leveraged_rows,
            limitations=leveraged_limitations,
            next_action="노출이 있으면 Final Review에서 목적, 보유기간, 손실 감내, 재검토 trigger를 명시합니다.",
            profile_effect=profile_row["answer_labels"].get("complexity_allowance", "-"),
        )
    )

    excluded_tickers = list(data_trust.get("excluded_tickers") or [])
    operability_evidence_rows = _operability_rows(active_components, source_period)
    operability_status_values = {str(row.get("Status") or "NOT_RUN") for row in operability_evidence_rows}
    if str(data_trust.get("status") or "").lower() in {"error", "blocked"}:
        operability_status = "BLOCKED"
        operability_summary = "Data Trust가 차단되어 가격/운용 가능성 판단을 진행할 수 없습니다."
    elif "REVIEW" in operability_status_values:
        operability_status = "REVIEW"
        operability_summary = "일부 ticker의 가격 / 거래대금 proxy가 낮거나 누락되어 운용성 확인이 필요합니다."
    elif operability_evidence_rows and operability_status_values == {"PASS"}:
        operability_status = "PASS"
        operability_summary = "기본 가격 / 거래대금 proxy 기준 운용성 blocker는 감지되지 않았습니다."
    elif excluded_tickers or unknown_weight > 50.0:
        operability_status = "REVIEW"
        operability_summary = "제외 ticker 또는 미분류 비중이 있어 ETF 운용성 확인이 필요합니다."
    else:
        operability_status = "REVIEW"
        operability_summary = "기본 source는 있으나 expense ratio, spread, ADV, turnover coverage는 아직 별도 확인이 필요합니다."
    operability_origin = "new_diagnostic"
    operability_key_metric = f"one-way {thresholds.get('one_way_cost_bps')} bps assumption"
    operability_metrics = {
        "one_way_cost_bps": thresholds.get("one_way_cost_bps"),
        "excluded_tickers": excluded_tickers,
        "cost_interpretation": thresholds.get("cost_interpretation"),
    }
    operability_rows = [
        {
            "Item": "Cost assumption",
            "Current": f"one-way {thresholds.get('one_way_cost_bps')} bps",
            "Meaning": "거래 수수료, spread, slippage를 포함한 보수적 시작값",
        },
        {
            "Item": "Excluded tickers",
            "Current": ", ".join(excluded_tickers) if excluded_tickers else "-",
            "Meaning": "원본 backtest에서 가격/데이터 문제로 제외된 ticker",
        },
    ] + operability_evidence_rows
    operability_limitations = ["ETF expense ratio / bid-ask spread 데이터는 후속 connector이며, 현재는 DB price/volume proxy입니다."]
    operability_next_action = "Final Review 전에 cost/liquidity connector가 없다는 점을 판단 근거에 남깁니다."
    if provider_operability.get("diagnostic_status") in {"PASS", "REVIEW"}:
        operability_origin = _provider_origin_label(provider_operability)
        operability_status = str(provider_operability.get("diagnostic_status") or operability_status)
        operability_summary = str(provider_operability.get("summary") or operability_summary)
        operability_key_metric = f"provider coverage {_optional_float(provider_operability.get('coverage_weight')) or 0.0:.1f}%"
        operability_metrics = {
            **operability_metrics,
            **dict(provider_operability.get("metrics") or {}),
            "provider_coverage_weight": provider_operability.get("coverage_weight"),
            "provider_missing_symbols": list(provider_operability.get("missing_symbols") or []),
        }
        operability_rows = list(provider_operability.get("evidence_rows") or []) + [
            {
                "Item": "Cost assumption",
                "Current": f"one-way {thresholds.get('one_way_cost_bps')} bps",
                "Meaning": "provider cost/liquidity snapshot과 함께 보는 보수적 transaction cost 시작값",
            }
        ]
        operability_limitations = [
            "Provider별 field coverage가 다르므로 missing field가 있으면 REVIEW로 남깁니다.",
            "거래 가능성은 자동 주문 승인이 아니라 Final Review 확인 근거입니다.",
        ]
        operability_next_action = "REVIEW ticker가 있으면 expense / AUM / ADV / spread / premium-discount를 Final Review에서 확인합니다."
    elif operability_status == "PASS":
        operability_status = "REVIEW"
        operability_summary = "Provider operability snapshot이 없어 가격 / 거래대금 proxy만 확인했습니다."
    diagnostics.append(
        _domain_result(
            domain="operability_cost_liquidity",
            title="10. Operability / Cost / Liquidity",
            status=operability_status,
            origin=operability_origin,
            key_metric=operability_key_metric,
            summary=operability_summary,
            metrics=operability_metrics,
            evidence_rows=operability_rows,
            limitations=operability_limitations,
            next_action=operability_next_action,
            profile_effect=str(thresholds.get("cost_interpretation") or "-"),
        )
    )

    overfit_audit = _build_overfit_audit(source_row, active_components)
    sensitivity_rows = _sensitivity_rows(
        active_components,
        component_curves=list(curve_context.get("component_curves") or []),
        portfolio_curve=portfolio_curve,
    )
    sensitivity_interpretation = _sensitivity_interpretation_result(
        sensitivity_rows,
        overfit_audit=overfit_audit,
        rolling_evidence=rolling_evidence,
    )
    robustness_lab_board = build_robustness_lab_board(
        stress_interpretation=stress_interpretation,
        sensitivity_interpretation=sensitivity_interpretation,
        stress_rows=stress_rows,
        sensitivity_rows=sensitivity_rows,
        overfit_audit=overfit_audit,
        rolling_evidence=rolling_evidence,
    )
    robustness_status = (
        "REVIEW"
        if str(sensitivity_interpretation.get("status") or "NOT_RUN") == "REVIEW"
        else "PASS"
        if str(sensitivity_interpretation.get("status") or "NOT_RUN") == "PASS"
        else "NOT_RUN"
    )
    robustness_summary = str(sensitivity_interpretation.get("summary") or "sensitivity interpretation을 생성하지 못했습니다.")
    diagnostics.append(
        _domain_result(
            domain="robustness_sensitivity_overfit",
            title="11. Robustness / Sensitivity / Overfit",
            status=robustness_status,
            origin="new_diagnostic",
            key_metric=(
                f"computed {sensitivity_interpretation.get('computed_count', 0)} / "
                f"runtime follow-up {sensitivity_interpretation.get('runtime_followup_count', 0)}"
            ),
            summary=str(robustness_summary),
            metrics={
                **overfit_audit,
                "rolling_validation": dict(rolling_evidence.get("metrics") or {}),
                "sensitivity_interpretation": sensitivity_interpretation,
            },
            evidence_rows=list(sensitivity_interpretation.get("rows") or []) + list(rolling_evidence.get("rows") or []) + sensitivity_rows,
            limitations=["run_history 원본은 저장하지 않고 local audit summary만 결과 row에 남깁니다. Curve proxy일 수 있습니다."],
            next_action=(
                "REVIEW 항목은 Final Review에서 선택 근거와 monitoring trigger로 남기고, strategy-specific runtime은 후속 구현으로 보강합니다."
                if robustness_status == "REVIEW"
                else "strategy-specific runtime perturbation은 별도 후속으로 남기되, 현재 curve 기반 민감도는 계속 추적합니다."
            ),
        )
    )

    monitoring_status = "PASS" if active_components and abs(target_weight_total - 100.0) <= 0.01 and has_benchmark else "REVIEW"
    diagnostics.append(
        _domain_result(
            domain="monitoring_baseline_seed",
            title="12. Monitoring Baseline Seed",
            status=monitoring_status,
            origin="new_diagnostic",
            key_metric="monthly / rebalance review",
            summary="Final Review 이후 사후관리 baseline으로 쓸 component, benchmark, trigger seed를 구성했습니다.",
            evidence_rows=[
                {"Item": "Review cadence", "Value": "monthly_or_rebalance_review"},
                {"Item": "Benchmark present", "Value": has_benchmark},
                {"Item": "Active component count", "Value": len(active_components)},
                {"Item": "Target weight total", "Value": f"{target_weight_total:.2f}%"},
            ],
            limitations=["이 seed는 live approval이나 주문 지시가 아니라 최종 판단 이후 관찰 기준입니다."],
            next_action="Final Review에서 선택/보류/거절 판단과 함께 monitoring 기준을 확정합니다.",
        )
    )

    diagnostic_hard_blockers = [
        f"{item.get('title')}: {item.get('summary')}"
        for item in diagnostics
        if item.get("status") == "BLOCKED"
    ]
    for blocker in diagnostic_hard_blockers:
        if blocker not in hard_blockers:
            hard_blockers.append(blocker)

    diagnostic_review_gaps = [
        f"{item.get('title')}: {item.get('summary')}"
        for item in diagnostics
        if item.get("status") == "REVIEW"
    ]
    for gap in diagnostic_review_gaps:
        if gap not in review_gaps:
            review_gaps.append(gap)

    intent_mismatch_warnings: list[str] = []
    if answers.get("primary_goal") == "defensive" and equity_exposure > (_optional_float(thresholds.get("equity_exposure_review")) or 70.0):
        intent_mismatch_warnings.append("방어형 목적 대비 주식성 노출이 높습니다.")
    if answers.get("primary_goal") in {"growth", "aggressive"} and known_weight > 0.0 and equity_exposure < 50.0:
        intent_mismatch_warnings.append("성장/공격형 목적 대비 주식성 노출이 낮을 수 있습니다.")
    if complexity_restricts_broad and (
        (_optional_float(flag_exposure.get("sector_theme")) or 0.0) > 0.0 or leveraged_exposure > 0.0
    ):
        intent_mismatch_warnings.append("광범위 ETF만 허용한 프로필과 sector/theme 또는 leveraged/inverse 노출이 충돌합니다.")

    status_counts = _status_counts(diagnostics)
    not_run_domains = [
        {"domain": item.get("domain"), "title": item.get("title"), "next_action": item.get("next_action")}
        for item in diagnostics
        if item.get("status") == "NOT_RUN"
    ]
    not_run_critical_domains = [
        item
        for item in not_run_domains
        if item.get("domain")
        in {
            "correlation_diversification_risk_contribution",
            "stress_scenario_diagnostics",
            "alternative_portfolio_challenge",
            "robustness_sensitivity_overfit",
        }
    ]
    validation_score = _diagnostic_score(diagnostics, hard_blockers, profile_row)
    profile_score_rows = _profile_score_rows(diagnostics, profile_row)

    if hard_blockers:
        route = "BLOCKED"
        verdict = "Practical Validation 차단: 먼저 blocker를 해결해야 합니다."
        next_action = "Backtest Analysis에서 설정 / 데이터 / 비중을 다시 확인합니다."
    else:
        route = "READY_FOR_FINAL_REVIEW"
        if review_gaps or not_run_domains:
            verdict = "Final Review로 이동 가능: REVIEW / NOT_RUN 항목을 최종 판단 근거로 함께 확인해야 합니다."
            next_action = "Final Review에서 보강 필요 상태를 확인하고, selected-route gate가 통과될 때만 최종 선정으로 저장합니다."
        else:
            verdict = "Final Review로 이동 가능: 실전 후보 검증 자료가 구성되었습니다."
            next_action = "Final Review에서 selected-route gate를 확인한 뒤 최종 후보 선정 저장을 진행합니다."

    component_rows = [
        {
            "Component": _component_title(component),
            "Role": component.get("proposal_role") or "-",
            "Weight": component.get("target_weight"),
            "Asset Buckets": dict(exposure_rows[idx]).get("Primary Buckets") if idx < len(exposure_rows) else "-",
            "Flags": dict(exposure_rows[idx]).get("Flags") if idx < len(exposure_rows) else "-",
            "CAGR": component.get("baseline_cagr"),
            "MDD": component.get("baseline_mdd"),
            "Sharpe": component.get("baseline_sharpe"),
            "Benchmark": component.get("benchmark"),
            "Data Trust": component.get("data_trust_status"),
            "Registry ID": component.get("registry_id") or "-",
        }
        for idx, component in enumerate(active_components)
    ]

    result = {
        "schema_version": PRACTICAL_VALIDATION_RESULT_SCHEMA_VERSION,
        "validation_id": f"validation_{_slug(source_id)}_{uuid4().hex[:8]}",
        "selection_source_id": source_id,
        "created_at": now,
        "updated_at": now,
        "source_kind": source_row.get("source_kind"),
        "source_title": source_title,
        "validation_profile": profile_row,
        "validation_route": route,
        "validation_score": validation_score,
        "verdict": verdict,
        "next_action": next_action,
        "checks": input_checks,
        "hard_blockers": hard_blockers,
        "review_gaps": review_gaps,
        "paper_tracking_gaps": [
            f"{item.get('title')} NOT_RUN 확인 필요"
            for item in not_run_critical_domains
        ],
        "input_evidence": {
            "checks": input_checks,
            "source_period": source_period,
            "source_summary": source_summary,
            "data_trust": data_trust,
            "real_money_signal": real_money,
            "curve_provenance": curve_provenance,
            "benchmark_parity": benchmark_parity,
            "provider_coverage": provider_context,
            "data_coverage_context": data_coverage_context,
            "temporal_validation": walkforward_validation,
            "oos_holdout_validation": oos_holdout_validation,
            "regime_split_validation": regime_split_validation,
        },
        "provider_coverage": provider_context,
        "provider_coverage_display_rows": provider_display_rows,
        "data_coverage_context": data_coverage_context,
        "diagnostic_results": diagnostics,
        "diagnostic_display_rows": _diagnostic_display_rows(diagnostics),
        "diagnostic_summary": {
            "status_counts": status_counts,
            "score": validation_score,
            "profile_label": profile_row.get("profile_label"),
            "profile_id": profile_row.get("profile_id"),
            "origin": "practical_validation_v2_core",
        },
        "profile_score_rows": profile_score_rows,
        "not_run_domains": not_run_domains,
        "not_run_critical_domains": not_run_critical_domains,
        "intent_mismatch_warnings": intent_mismatch_warnings,
        "invariant_hard_blockers": profile_row.get("invariant_blockers") or [],
        "metrics": {
            "active_components": len(active_components),
            "weight_total": target_weight_total,
            "max_weight": max_weight,
            "asset_exposure": asset_exposure,
            "flag_exposure": flag_exposure,
            "known_weight": known_weight,
            "unknown_weight": unknown_weight,
            "covered_stress_windows": covered_stress_count,
            "computed_stress_windows": computed_stress_count,
            "local_trial_count": overfit_audit.get("trial_count", 0),
            "portfolio_curve_rows": len(portfolio_curve),
            "portfolio_curve_source": curve_context.get("portfolio_curve_source"),
            "portfolio_curve_summary": portfolio_summary,
            "benchmark_parity_status": benchmark_parity.get("status"),
            "benchmark_parity": benchmark_parity.get("metrics") or {},
            "rolling_validation": rolling_evidence.get("metrics") or {},
            "walkforward_validation": dict(walkforward_validation.get("metrics") or {}),
            "oos_holdout_validation": dict(oos_holdout_validation.get("metrics") or {}),
            "regime_split_validation": dict(regime_split_validation.get("metrics") or {}),
            "runtime_recheck_status": replay_row.get("status") or "NOT_RUN",
            "runtime_recheck_mode": replay_row.get("recheck_mode"),
            "runtime_recheck_extension_days": replay_row.get("extension_days"),
            "runtime_recheck_period": replay_row.get("requested_period") or {},
            "runtime_recheck_period_coverage": period_coverage,
            "provider_coverage": {
                "as_of_date": provider_context.get("as_of_date"),
                "symbols": list(provider_context.get("symbols") or []),
                "operability": _compact_provider_area("operability"),
                "holdings": _compact_provider_area("holdings"),
                "exposure": _compact_provider_area("exposure"),
                "macro": _compact_provider_area("macro"),
            },
            "provider_look_through": {
                "status": provider_look_through_board.get("status"),
                "holdings_coverage_weight": provider_look_through_board.get("holdings_coverage_weight"),
                "exposure_coverage_weight": provider_look_through_board.get("exposure_coverage_weight"),
                "top_holding_weight": provider_look_through_board.get("top_holding_weight"),
                "top_overlap_weight": provider_look_through_board.get("top_overlap_weight"),
                "unknown_exposure_weight": provider_look_through_board.get("unknown_exposure_weight"),
                "dominant_asset_bucket": provider_look_through_board.get("dominant_asset_bucket"),
                "dominant_asset_weight": provider_look_through_board.get("dominant_asset_weight"),
            },
            "data_coverage": {
                "symbols": list(data_coverage_context.get("symbols") or []),
                "requested_start": data_coverage_context.get("requested_start"),
                "requested_end": data_coverage_context.get("requested_end"),
                "price_window_error": data_coverage_context.get("price_window_error"),
                "asset_profile_error": data_coverage_context.get("asset_profile_error"),
            },
            "robustness_lab": {
                "status": robustness_lab_board.get("status"),
                "covered_stress_windows": robustness_lab_board.get("metrics", {}).get("covered_stress_windows"),
                "computed_stress_windows": robustness_lab_board.get("metrics", {}).get("computed_stress_windows"),
                "computed_sensitivity_checks": robustness_lab_board.get("metrics", {}).get("computed_sensitivity_checks"),
                "sensitivity_review_count": robustness_lab_board.get("metrics", {}).get("sensitivity_review_count"),
                "runtime_followup_count": robustness_lab_board.get("metrics", {}).get("runtime_followup_count"),
                "rolling_window_count": robustness_lab_board.get("metrics", {}).get("rolling_window_count"),
                "local_trial_count": robustness_lab_board.get("metrics", {}).get("local_trial_count"),
            },
        },
        "component_rows": component_rows,
        "stress_interpretation": stress_interpretation,
        "sensitivity_interpretation": sensitivity_interpretation,
        "robustness_validation": {
            "robustness_route": "READY_FOR_STRESS_SWEEP" if not hard_blockers else "BLOCKED_FOR_ROBUSTNESS",
            "robustness_score": validation_score if not hard_blockers else 0.0,
            "verdict": "stress / sensitivity / overfit preview가 구성되었습니다." if not hard_blockers else "source blocker가 있어 robustness preview가 차단됩니다.",
            "next_action": "Final Review에서 stress, sensitivity, NOT_RUN 항목을 최종 판단 근거로 확인합니다.",
            "blockers": list(hard_blockers),
            "component_rows": component_rows,
            "stress_summary_rows": stress_rows + sensitivity_rows,
            "stress_interpretation": stress_interpretation,
            "sensitivity_interpretation": sensitivity_interpretation,
            "robustness_lab_board": robustness_lab_board,
            "overfit_audit": overfit_audit,
            "sensitivity_rows": sensitivity_rows,
            "rolling_validation": rolling_evidence,
        },
        "paper_observation": {
            "mode": "inline_paper_observation",
            "route": "PAPER_OBSERVATION_READY" if not hard_blockers else "PAPER_OBSERVATION_REVIEW",
            "baseline_snapshot": {
                "target_weight_total": target_weight_total,
                "weighted_cagr": dict(source_row.get("summary") or {}).get("cagr"),
                "weighted_mdd": dict(source_row.get("summary") or {}).get("mdd"),
                "active_component_count": len(active_components),
            },
            "active_components": active_components,
            "checks": [
                {
                    "Criteria": "Observation source",
                    "Ready": bool(source_id),
                    "Current": source_id or "-",
                    "Meaning": "Final Review 이후 추적할 source id입니다.",
                },
                {
                    "Criteria": "Monitoring benchmark",
                    "Ready": has_benchmark,
                    "Current": "present" if has_benchmark else "missing",
                    "Meaning": "성과 관찰 시 상대 비교 기준이 있는지 봅니다.",
                },
                {
                    "Criteria": "Review triggers",
                    "Ready": True,
                    "Current": "CAGR / MDD / benchmark / Data Trust",
                    "Meaning": "선택 이후 재검토할 trigger seed입니다.",
                },
            ],
            "review_cadence": "monthly_or_rebalance_review",
            "review_triggers": [
                "CAGR deterioration review",
                "MDD expansion review",
                "Benchmark-relative underperformance review",
                "Data Trust refresh review",
            ],
        },
        "overfit_audit": overfit_audit,
        "stress_window_rows": stress_rows,
        "alternative_baseline_rows": alternative_rows,
        "sensitivity_rows": sensitivity_rows,
        "rolling_validation": rolling_evidence,
        "temporal_validation": walkforward_validation,
        "walkforward_validation": walkforward_validation,
        "oos_holdout_validation": oos_holdout_validation,
        "regime_split_validation": regime_split_validation,
        "curve_evidence": {
            "portfolio_curve_source": curve_context.get("portfolio_curve_source"),
            "portfolio_curve_rows": len(portfolio_curve),
            "component_curve_rows": list(curve_context.get("curve_rows") or []),
            "benchmark_ticker": curve_context.get("benchmark_ticker"),
            "benchmark_curve_rows": len(benchmark_curve),
            "benchmark_meta": dict(curve_context.get("benchmark_meta") or {}),
            "curve_provenance": curve_provenance,
            "benchmark_parity": benchmark_parity,
            "replay_attempt": replay_row,
            "period_coverage": period_coverage,
            "temporal_validation": walkforward_validation,
            "oos_holdout_validation": oos_holdout_validation,
            "regime_split_validation": regime_split_validation,
        },
        "final_review_handoff": {
            "route": route,
            "allowed": route == "READY_FOR_FINAL_REVIEW",
            "required_confirmations": [
                "REVIEW 상태 domain 확인",
                "NOT_RUN 상태 domain이 최종 판단을 막는지 확인",
                "사용자 검증 프로필과 후보 목적의 충돌 여부 확인",
            ],
            "not_live_approval": True,
        },
        "selection_source_snapshot": source_row,
        "final_decision_schema_target": FINAL_SELECTION_DECISION_V2_SCHEMA_VERSION,
    }
    data_coverage_audit = build_data_coverage_audit(result)
    result["data_coverage_audit"] = data_coverage_audit
    result["data_coverage_display_rows"] = list(data_coverage_audit.get("rows") or [])
    construction_risk_audit = build_construction_risk_audit(result)
    result["construction_risk_audit"] = construction_risk_audit
    result["construction_risk_display_rows"] = list(construction_risk_audit.get("rows") or [])
    risk_contribution_audit = build_risk_contribution_audit(result)
    result["risk_contribution_audit"] = risk_contribution_audit
    result["risk_contribution_display_rows"] = list(risk_contribution_audit.get("rows") or [])
    component_role_weight_audit = build_component_role_weight_audit(result)
    result["component_role_weight_audit"] = component_role_weight_audit
    result["component_role_weight_display_rows"] = list(component_role_weight_audit.get("rows") or [])
    backtest_realism_audit = build_backtest_realism_audit(result)
    result["backtest_realism_audit"] = backtest_realism_audit
    result["backtest_realism_display_rows"] = list(backtest_realism_audit.get("rows") or [])
    validation_efficacy_audit = build_validation_efficacy_audit(result)
    result["validation_efficacy_audit"] = validation_efficacy_audit
    result["validation_efficacy_display_rows"] = list(validation_efficacy_audit.get("rows") or [])
    selected_route_preflight = build_practical_validation_selected_route_preflight(result)
    result["selected_route_preflight"] = selected_route_preflight
    module_plan = build_validation_module_plan(
        source=source_row,
        validation_profile=profile_row,
        checks=input_checks,
        diagnostics=diagnostics,
        validation_efficacy_rows=result["validation_efficacy_display_rows"],
        data_coverage_rows=result["data_coverage_display_rows"],
        construction_risk_rows=result["construction_risk_display_rows"],
        risk_contribution_rows=result["risk_contribution_display_rows"],
        component_role_weight_rows=result["component_role_weight_display_rows"],
        backtest_realism_rows=result["backtest_realism_display_rows"],
        selected_route_preflight=selected_route_preflight,
    )
    result["source_traits"] = dict(module_plan.get("source_traits") or {})
    result["validation_modules"] = list(module_plan.get("modules") or [])
    result["validation_module_display_rows"] = list(module_plan.get("module_display_rows") or [])
    result["validation_module_summary"] = dict(module_plan.get("summary") or {})
    result["validation_board_map"] = dict(module_plan.get("board_map") or {})
    result["validation_board_display_rows"] = list(module_plan.get("board_display_rows") or [])
    result["applied_validation_board_display_rows"] = list(
        module_plan.get("applied_board_display_rows") or []
    )
    result["not_applicable_validation_board_display_rows"] = list(
        module_plan.get("not_applicable_board_display_rows") or []
    )
    result["validation_board_summary"] = dict(module_plan.get("board_summary") or {})
    result["final_review_gate"] = dict(module_plan.get("final_review_gate") or {})
    result["final_review_handoff"] = {
        **dict(result.get("final_review_handoff") or {}),
        "route": dict(module_plan.get("final_review_gate") or {}).get("route") or route,
        "allowed": bool(dict(module_plan.get("final_review_gate") or {}).get("can_save_and_move")),
        "module_gate": dict(module_plan.get("final_review_gate") or {}),
    }
    return result


__all__ = [
    "VALIDATION_PROFILE_OPTIONS",
    "VALIDATION_PROFILE_QUESTIONS",
    "build_practical_validation_result",
    "build_selection_source_from_candidate_draft",
    "build_selection_source_from_saved_mix_prefill",
    "build_selection_source_from_weighted_mix_prefill",
    "build_validation_profile",
    "compact_benchmark_curve_snapshot_from_bundle",
    "compact_curve_snapshot_from_bundle",
    "source_components_dataframe",
]
