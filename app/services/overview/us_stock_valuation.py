from __future__ import annotations

import math
from datetime import date, datetime
from typing import Any, Mapping

import pandas as pd

from finance.data.us_stock_valuation import (
    build_monthly_pit_valuation,
    calculate_company_excess_growth,
    calculate_historical_stock_scenario,
    calculate_stock_multiple_regime,
    calculate_stock_scenarios,
    classify_us_stock_readiness,
)
from finance.loaders.us_stock_valuation import (
    load_us_stock_valuation_inputs,
    search_us_common_stocks,
)


INSTRUMENT = {
    "id": "us_stock",
    "label": "미국 개별주식",
    "proxy_symbol": None,
    "price_label": "선택 종목 주가",
    "multiple_label": "후행 PER",
    "method_label": "기업 자체 이력 기반",
}


def _empty_model(status: str, reason: str | None = None) -> dict[str, Any]:
    state = {"status": status}
    if reason:
        state["reason"] = reason
    return {
        "schema_version": "us_stock_valuation_v1",
        "status": status,
        "instrument": dict(INSTRUMENT),
        "search": {"query": "", "results": []},
        "selection": None,
        "readiness": dict(state),
        "multiple_regime": {**state, "series": []},
        "earnings_scenario": dict(state),
        "index_scenario": {**state, "history_options": {}},
        "sources": [],
        "limitations": [],
    }


def _quarterly_ttm_from_monthly(monthly_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collapse monthly carry-forward rows into distinct filing-aware TTM observations."""
    keyed: dict[tuple[str, str], dict[str, Any]] = {}
    for row in monthly_rows:
        quarter_ends = [str(value) for value in row.get("quarter_ends") or [] if value]
        available_at = str(row.get("eps_basis_date") or "")
        ttm_eps = pd.to_numeric(row.get("ttm_eps"), errors="coerce")
        if len(quarter_ends) != 4 or not available_at or pd.isna(ttm_eps):
            continue
        period_end = max(quarter_ends)
        keyed[(period_end, available_at)] = {
            "period_end": period_end,
            "available_at": available_at,
            "ttm_eps": float(ttm_eps),
        }
    return sorted(keyed.values(), key=lambda row: (row["period_end"], row["available_at"]))


def _latest_monthly(monthly_rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not monthly_rows:
        return None
    return sorted(monthly_rows, key=lambda row: str(row.get("month") or ""))[-1]


def _collection_action(
    identity: Mapping[str, Any],
    coverage: Mapping[str, Any],
    window: Mapping[str, Any],
    scopes: list[str],
) -> dict[str, Any]:
    missing_ranges: dict[str, Any] = {}
    if "prices" in scopes:
        missing_ranges["prices"] = coverage.get("price_missing_range") or {
            "start": window.get("valuation_start"),
            "end": window.get("as_of_date"),
        }
    if "sec_statements" in scopes:
        missing_ranges["sec_statements"] = coverage.get("statement_missing_range") or {
            "start": window.get("statement_start"),
            "end": window.get("as_of_date"),
        }
    return {
        "id": "collect_us_stock_valuation",
        "label": "가치평가 자료 수집",
        "detail": "선택한 한 종목의 누락 가격과 SEC 분기 실적만 동기 수집합니다.",
        "symbol": identity.get("symbol"),
        "cik": identity.get("cik"),
        "scopes": scopes,
        "missing_ranges": missing_ranges,
        "enabled": True,
    }


def _scenario_index(
    scenarios: Mapping[str, Any],
    *,
    latest: Mapping[str, Any] | None,
    history_options: dict[str, Any],
) -> dict[str, Any]:
    if scenarios.get("status") != "READY":
        return {
            "status": "BLOCKED",
            "reason": scenarios.get("reason") or "상대가치 시나리오 근거가 충분하지 않습니다.",
            "history_options": history_options,
        }
    current_price = float((latest or {}).get("price") or 0)
    prices = {
        "lower": scenarios["conservative"].get("price"),
        "baseline": scenarios["baseline"].get("price"),
        "upper": scenarios["optimistic"].get("price"),
    }
    baseline = float(prices["baseline"] or 0)
    gap_pct = {
        key: ((float(value) / current_price) - 1.0) * 100.0
        for key, value in prices.items()
        if value is not None and current_price > 0
    }
    current_vs_baseline = (
        ((current_price / baseline) - 1.0) * 100.0
        if current_price > 0 and baseline > 0
        else None
    )
    return {
        "status": "READY",
        "as_of": (latest or {}).get("price_basis_date"),
        "current_price": current_price or None,
        "price_scenarios": prices,
        "scenarios": {
            key: dict(scenarios[key])
            for key in ("conservative", "baseline", "optimistic")
        },
        "gap_pct": gap_pct,
        "current_vs_baseline_gap_pct": current_vs_baseline,
        "valuation_position": (
            "ABOVE_BASELINE"
            if current_vs_baseline is not None and current_vs_baseline > 0
            else "BELOW_BASELINE"
            if current_vs_baseline is not None and current_vs_baseline < 0
            else "AT_BASELINE"
        ),
        "history_options": history_options,
        "history": history_options.get("1y"),
        "label": "거시·기업 실적 결합 상대가치 시나리오",
        "limitation": "공식 적정가·목표주가·매매 신호가 아닌 자체 재구성 시나리오입니다.",
    }


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, (pd.Timestamp, datetime, date)):
        return value.isoformat()[:10]
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if hasattr(value, "item"):
        return _json_safe(value.item())
    return str(value)


def build_us_stock_valuation_read_model(
    *,
    selected_symbol: str | None = None,
    search_query: str | None = None,
    loaded_inputs: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build one selected stock's DB-backed relative-value read model."""
    symbol = str(selected_symbol or "").strip().upper()
    if not symbol:
        query = str(search_query or "").strip()
        model = _empty_model("NOT_SELECTED")
        model["search"] = {
            "query": query,
            "results": search_us_common_stocks(query) if len(query) >= 2 else [],
        }
        return model
    try:
        inputs = dict(loaded_inputs or load_us_stock_valuation_inputs(symbol))
        identity = inputs.get("identity")
        if not isinstance(identity, Mapping):
            return _empty_model("ERROR", "선택 기업 identity/schema를 확인하지 못했습니다.")
        if str(identity.get("symbol") or "").strip().upper() != symbol:
            return _empty_model("ERROR", "선택 ticker와 DB identity가 일치하지 않습니다.")
        window = dict(inputs.get("window") or {})
        coverage = dict(inputs.get("coverage") or {})
        monthly_rows = [dict(row) for row in inputs.get("monthly_rows") or []]
        if not monthly_rows:
            monthly_rows = build_monthly_pit_valuation(
                inputs.get("statement_rows") or [],
                inputs.get("price_rows") or [],
                start_month=str(window.get("valuation_start")),
                end_month=str(window.get("as_of_date")),
            )
        quarterly_rows = [dict(row) for row in inputs.get("quarterly_ttm_rows") or []]
        if not quarterly_rows:
            quarterly_rows = _quarterly_ttm_from_monthly(monthly_rows)
        as_of_date = str(window.get("as_of_date") or (_latest_monthly(monthly_rows) or {}).get("price_basis_date") or "")
        multiple = calculate_stock_multiple_regime(monthly_rows)
        growth = calculate_company_excess_growth(
            quarterly_rows,
            inputs.get("sep_rows") or [],
            as_of_date=as_of_date,
        )
        price_months = pd.to_numeric(coverage.get("price_months"), errors="coerce")
        readiness_coverage = {
            **coverage,
            "requested_months": 60,
            "price_missing": (
                int(price_months) < 60
                if not pd.isna(price_months)
                else bool(coverage.get("price_missing"))
            ),
        }
        readiness = classify_us_stock_readiness(
            identity,
            readiness_coverage,
            monthly_rows,
            growth,
        )
        latest = _latest_monthly(monthly_rows)
        current_eps = float((latest or {}).get("ttm_eps") or 0)
        scenarios = calculate_stock_scenarios(current_eps, multiple, growth)
        history_options = {
            key: calculate_historical_stock_scenario(
                monthly_rows,
                quarterly_rows,
                inputs.get("sep_rows") or [],
                visible_months=months,
            )
            for key, months in (("1y", 12), ("3y", 36), ("5y", 60))
        }

        status = str(readiness.get("status") or "ERROR")
        earnings = {
            "status": "READY" if scenarios.get("status") == "READY" else "BLOCKED",
            "reason_code": scenarios.get("reason_code"),
            "reason": scenarios.get("reason"),
            "observation_count": growth.get("observation_count"),
            "required_observations": 8,
            "current_ttm_eps": current_eps if current_eps else None,
            "eps_basis_date": (latest or {}).get("eps_basis_date"),
            "eps_source": "SEC filing-aware diluted EPS TTM",
            "eps_source_quality": "official_actual",
            "release_date": growth.get("current_sep_release_date"),
            "real_gdp_pct": growth.get("current_real_gdp_pct"),
            "pce_inflation_pct": growth.get("current_pce_inflation_pct"),
            "current_macro_pct": growth.get("current_macro_pct"),
            "company_excess_growth": {
                key: growth.get(key)
                for key in ("p25_pct", "p50_pct", "p75_pct", "observation_count")
            },
            "scenarios": {
                key: scenarios.get(key)
                for key in ("conservative", "baseline", "optimistic")
            },
            "methodology": "FOMC real GDP + PCE 거시 proxy에 기업의 최근 3년 TTM EPS 초과성장 P25/P50/P75를 결합",
            "limitation": "FOMC 지표는 기업 이익 전망이 아니며 결과는 상대가치 시나리오입니다.",
        }
        index = _scenario_index(scenarios, latest=latest, history_options=history_options)
        model: dict[str, Any] = {
            "schema_version": "us_stock_valuation_v1",
            "status": status,
            "instrument": {**INSTRUMENT, "proxy_symbol": identity.get("symbol")},
            "search": {"query": "", "results": []},
            "selection": {
                "symbol": identity.get("symbol"),
                "name": identity.get("name"),
                "exchange": identity.get("exchange"),
                "cik": identity.get("cik"),
                "latest_price_date": coverage.get("latest_price_date") or (latest or {}).get("price_basis_date"),
                "eps_basis_date": (latest or {}).get("eps_basis_date"),
            },
            "readiness": readiness,
            "basis": {
                "window": window,
                "coverage": coverage,
                "price": latest,
                "official_window_months": 60,
                "sensitivity_window_months": 36,
            },
            "multiple_regime": multiple,
            "earnings_scenario": earnings,
            "index_scenario": index,
            "sources": [
                {"name": "DB EOD raw close/split", "role": "월말 주가와 split-neutral share basis"},
                {"name": "SEC detailed statements", "role": "filing-aware diluted EPS TTM"},
                {"name": "Federal Reserve SEP", "role": "real GDP + PCE 거시 proxy"},
            ],
            "limitations": [
                "상대 멀티플 구간은 기업 자신의 최근 이력 비교입니다.",
                "적자·0 EPS는 PER와 가격 시나리오를 계산하지 않습니다.",
                "결과는 공식 적정가·목표주가·매매 신호가 아닙니다.",
            ],
        }
        if status == "COLLECTABLE":
            model["collection_action"] = _collection_action(
                identity,
                coverage,
                window,
                list(readiness.get("collection_scopes") or []),
            )
        return _json_safe(model)
    except Exception as exc:
        return _empty_model("ERROR", f"{type(exc).__name__}: {exc}")
