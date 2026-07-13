from __future__ import annotations

from typing import Any

import pandas as pd

from app.services.overview.sp500_valuation import (
    calculate_fomc_eps_scenarios,
    calculate_historical_index_scenario,
    calculate_index_scenario,
    calculate_multiple_regime,
)


INSTRUMENT = {
    "id": "nasdaq100",
    "label": "Nasdaq-100",
    "proxy_symbol": "QQQ",
    "price_label": "QQQ 가격",
    "multiple_label": "재구성 후행 PER",
    "method_label": "QQQ 보유종목 기반",
}


def _price_evidence(rows: pd.DataFrame | list[dict[str, Any]], symbol: str) -> dict[str, Any] | None:
    frame = pd.DataFrame(rows)
    if frame.empty or "symbol" not in frame:
        return None
    match = frame.loc[frame["symbol"] == symbol]
    if match.empty:
        return None
    row = match.iloc[-1]
    date = pd.to_datetime(row.get("latest_date"), errors="coerce")
    price = pd.to_numeric(row.get("price"), errors="coerce")
    if pd.isna(date) or pd.isna(price) or float(price) <= 0:
        return None
    return {"date": pd.Timestamp(date).strftime("%Y-%m-%d"), "price": float(price)}


def _adapt_monthly(rows: pd.DataFrame | list[dict[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame(rows).copy()
    return frame.rename(
        columns={"qqq_price": "spx_level", "reconstructed_ttm_eps": "trailing_eps"}
    )


def _adapt_index_contract(result: dict[str, Any]) -> dict[str, Any]:
    adapted = dict(result)
    if "spx_scenarios" in adapted:
        adapted["price_scenarios"] = adapted["spx_scenarios"]
        adapted["current_price"] = adapted.get("current_spx")
    return adapted


def _adapt_history_contract(result: dict[str, Any]) -> dict[str, Any]:
    adapted = dict(result)
    adapted["series"] = [
        {
            **point,
            "actual_price": point.get("actual_spx"),
            "lower_price": point.get("lower_spx"),
            "baseline_price": point.get("baseline_spx"),
            "upper_price": point.get("upper_spx"),
        }
        for point in result.get("series", [])
    ]
    return adapted


def build_nasdaq100_valuation_read_model(
    *,
    monthly_rows: pd.DataFrame | list[dict[str, Any]] | None = None,
    ttm_evidence: dict[str, Any] | None = None,
    sep_rows: pd.DataFrame | list[dict[str, Any]] | None = None,
    sep_history_rows: pd.DataFrame | list[dict[str, Any]] | None = None,
    current_prices: pd.DataFrame | list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a QQQ proxy model without turning sub-95% coverage into a value signal."""
    sep_supplied = sep_rows is not None
    if any(value is None for value in (monthly_rows, ttm_evidence, sep_rows, sep_history_rows, current_prices)):
        from finance.loaders.nasdaq100_valuation import (
            load_latest_nasdaq100_ttm_proxy,
            load_nasdaq100_monthly_valuation,
        )
        from finance.loaders.price import load_latest_prices
        from finance.loaders.sp500_valuation import (
            load_fomc_sep_projection_history,
            load_latest_fomc_sep_projection,
        )

        monthly_rows = monthly_rows if monthly_rows is not None else load_nasdaq100_monthly_valuation()
        ttm_evidence = ttm_evidence if ttm_evidence is not None else load_latest_nasdaq100_ttm_proxy()
        sep_rows = sep_rows if sep_rows is not None else load_latest_fomc_sep_projection()
        sep_history_rows = sep_history_rows if sep_history_rows is not None else (
            sep_rows if sep_supplied else load_fomc_sep_projection_history()
        )
        current_prices = current_prices if current_prices is not None else load_latest_prices(["QQQ"])

    raw_frame = pd.DataFrame(monthly_rows).copy()
    frame = _adapt_monthly(raw_frame)
    evidence = dict(ttm_evidence or {})
    qqq = _price_evidence([] if current_prices is None else current_prices, "QQQ")
    multiple = calculate_multiple_regime(frame, current_spx=qqq)
    current_eps = float(evidence.get("current_ttm_eps") or evidence.get("ttm_eps") or 0)
    eps_ready = (
        evidence.get("status") == "READY"
        and evidence.get("eps_source_quality") == "reconstructed_actual"
        and current_eps > 0
    )
    coverage = {
        "minimum_required_pct": 95.0,
        "coverage_weight_pct": evidence.get("coverage_weight_pct"),
        "unmapped_weight_pct": evidence.get("unmapped_weight_pct"),
        "holding_snapshot_date": evidence.get("holding_snapshot_date"),
        "holding_snapshot_quality": evidence.get("holding_snapshot_quality"),
        "error_code": evidence.get("error_code"),
    }
    if eps_ready:
        earnings = calculate_fomc_eps_scenarios(
            current_eps, [] if sep_rows is None else sep_rows
        )
        index = (
            _adapt_index_contract(
                calculate_index_scenario(
                    multiple_regime=multiple,
                    eps_scenarios=earnings,
                    current_spx=qqq or {},
                )
            )
            if qqq
            else {"status": "BLOCKED", "reason": "현재 QQQ 기준값이 없습니다."}
        )
    else:
        reason = evidence.get("error_code") or "95% earnings coverage gate를 통과하지 못했습니다."
        earnings = {"status": "BLOCKED", "reason": reason}
        index = {"status": "BLOCKED", "reason": reason}

    history_options = {
        key: _adapt_history_contract(
            calculate_historical_index_scenario(
                frame,
                [] if sep_history_rows is None else sep_history_rows,
                current_spx=qqq,
                visible_months=months,
            )
        )
        for key, months in (("1y", 12), ("3y", 36), ("5y", 60))
    }
    index["history_options"] = history_options
    index["history"] = history_options["1y"]
    status = "READY" if index.get("status") == "READY" else "BLOCKED"
    if status == "BLOCKED":
        coverage["repair_action"] = {
            "id": "repair_nasdaq100_60m",
            "label": "60개월 가치평가 자료 보강",
            "detail": "누락된 구성 종목 EPS와 가격 이력을 보강한 뒤 다시 계산합니다.",
            "enabled": True,
        }
    return {
        "schema_version": "nasdaq100_valuation_v1",
        "status": status,
        "instrument": dict(INSTRUMENT),
        "coverage": coverage,
        "basis": {"ttm_evidence": evidence, "qqq": qqq, "official_window_months": 60, "sensitivity_window_months": 36},
        "multiple_regime": multiple,
        "earnings_scenario": earnings,
        "index_scenario": index,
        "sources": [
            {"name": "SEC QQQ NPORT/N-30B-2", "role": "보유종목·비중"},
            {"name": "SEC company facts", "role": "구성종목 실제 희석 EPS"},
            {"name": "QQQ EOD", "role": "무료·무계정 가격 proxy"},
            {"name": "Federal Reserve SEP", "role": "GDP·PCE 민감도"},
        ],
        "limitations": [
            "QQQ는 Nasdaq-100 지수 자체가 아닌 거래 가능 proxy입니다.",
            "coverage 95% 미만 월은 값과 시나리오를 노출하지 않습니다.",
            "지수 시나리오는 공식 적정가나 투자 신호가 아닙니다.",
        ],
    }
