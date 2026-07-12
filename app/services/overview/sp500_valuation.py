from __future__ import annotations

import math
import statistics
from typing import Any

import pandas as pd


def _bucket(z_score: float) -> str:
    if z_score < -1.0:
        return "LOW"
    if z_score < 1.0:
        return "NEUTRAL"
    if z_score < 2.0:
        return "HIGH"
    return "EXTREME_HIGH"


def _distribution(values: list[float], window_months: int) -> dict[str, Any]:
    selected = values[-window_months:]
    logs = [math.log(value) for value in selected]
    mean_log = statistics.fmean(logs)
    std_log = statistics.stdev(logs)
    return {
        "window_months": window_months,
        "observation_count": len(selected),
        "mean_log": mean_log,
        "std_log": std_log,
        "mean_multiple": math.exp(mean_log),
        "minus_1sigma": math.exp(mean_log - std_log),
        "plus_1sigma": math.exp(mean_log + std_log),
        "plus_2sigma": math.exp(mean_log + (2.0 * std_log)),
    }


def calculate_multiple_regime(
    monthly_rows: pd.DataFrame | list[dict[str, Any]],
    *,
    official_window: int = 60,
    sensitivity_window: int = 36,
) -> dict[str, Any]:
    """Calculate descriptive log(P/E) zones over 60m with a 36m sensitivity view."""
    frame = pd.DataFrame(monthly_rows).copy()
    if frame.empty or "observation_month" not in frame or "trailing_pe" not in frame:
        return {
            "status": "INSUFFICIENT_HISTORY",
            "window_months": int(official_window),
            "observation_count": 0,
            "series": [],
        }
    frame["observation_month"] = pd.to_datetime(
        frame["observation_month"], errors="coerce"
    )
    frame["trailing_pe"] = pd.to_numeric(frame["trailing_pe"], errors="coerce")
    frame = (
        frame.dropna(subset=["observation_month", "trailing_pe"])
        .loc[lambda value: value["trailing_pe"] > 0]
        .sort_values("observation_month")
        .drop_duplicates("observation_month", keep="last")
    )
    required = max(int(official_window), int(sensitivity_window), 2)
    if len(frame) < required:
        return {
            "status": "INSUFFICIENT_HISTORY",
            "window_months": int(official_window),
            "observation_count": len(frame),
            "series": [],
        }

    official_frame = frame.tail(int(official_window))
    values = frame["trailing_pe"].astype(float).tolist()
    official = _distribution(values, int(official_window))
    sensitivity = _distribution(values, int(sensitivity_window))
    current_pe = float(official_frame.iloc[-1]["trailing_pe"])
    current_log = math.log(current_pe)
    current_z = (current_log - official["mean_log"]) / official["std_log"]
    sensitivity_z = (
        current_log - sensitivity["mean_log"]
    ) / sensitivity["std_log"]
    bucket = _bucket(current_z)
    sensitivity_bucket = _bucket(sensitivity_z)

    series = [
        {
            "month": row.observation_month.strftime("%Y-%m-%d"),
            "trailing_pe": float(row.trailing_pe),
        }
        for row in official_frame.itertuples()
    ]
    return {
        "status": "READY",
        "window_months": int(official_window),
        "observation_count": len(series),
        "series": series,
        "mean_multiple": official["mean_multiple"],
        "minus_1sigma": official["minus_1sigma"],
        "plus_1sigma": official["plus_1sigma"],
        "plus_2sigma": official["plus_2sigma"],
        "current_pe": current_pe,
        "current_basis_date": series[-1]["month"],
        "current_z": current_z,
        "bucket": bucket,
        "sensitivity": {
            "window_months": int(sensitivity_window),
            "observation_count": sensitivity["observation_count"],
            "mean_multiple": sensitivity["mean_multiple"],
            "current_z": sensitivity_z,
            "bucket": sensitivity_bucket,
        },
        "period_sensitive": bucket != sensitivity_bucket,
        "basis_start": series[0]["month"],
        "basis_end": series[-1]["month"],
        "methodology": "월별 후행 PER의 자연로그 평균과 표본 표준편차",
        "limitation": "이 구간은 상대적 가치평가 범위이며 확률적 신뢰구간이 아닙니다.",
    }


def _macro_growth(real_gdp_pct: float, pce_pct: float) -> float:
    return float(real_gdp_pct) + float(pce_pct)


def calculate_fomc_eps_scenarios(
    current_ttm_eps: float,
    sep_rows: pd.DataFrame | list[dict[str, Any]],
) -> dict[str, Any]:
    """Turn a complete SEP GDP/PCE vintage into macro-implied EPS sensitivities."""
    current_ttm_eps = float(current_ttm_eps)
    if current_ttm_eps <= 0:
        return {"status": "NON_POSITIVE_EPS", "scenarios": {}}
    frame = pd.DataFrame(sep_rows).copy()
    required = {"target_year", "variable_name", "statistic_name", "value_pct"}
    if frame.empty or not required.issubset(frame.columns):
        return {"status": "INSUFFICIENT_SEP", "scenarios": {}}
    frame["value_pct"] = pd.to_numeric(frame["value_pct"], errors="coerce")
    frame["target_year"] = pd.to_numeric(frame["target_year"], errors="coerce")
    frame = frame.dropna(subset=["target_year", "value_pct"])

    statistic_map = {
        "conservative": "central_tendency_lower",
        "baseline": "median",
        "optimistic": "central_tendency_upper",
    }
    selected_year: int | None = None
    selected: dict[str, dict[str, float]] = {}
    for target_year in sorted(frame["target_year"].astype(int).unique()):
        year_frame = frame.loc[frame["target_year"].astype(int) == target_year]
        candidate: dict[str, dict[str, float]] = {}
        for scenario, statistic_name in statistic_map.items():
            values: dict[str, float] = {}
            for variable in ("real_gdp", "pce_inflation"):
                match = year_frame.loc[
                    (year_frame["variable_name"] == variable)
                    & (year_frame["statistic_name"] == statistic_name),
                    "value_pct",
                ]
                if not match.empty:
                    values[variable] = float(match.iloc[0])
            if len(values) == 2:
                candidate[scenario] = values
        if len(candidate) == 3:
            selected_year = int(target_year)
            selected = candidate
            break
    if selected_year is None:
        return {"status": "INSUFFICIENT_SEP", "scenarios": {}}

    release_date = None
    source_ref = None
    if "release_date" in frame:
        parsed = pd.to_datetime(frame["release_date"], errors="coerce").dropna()
        if not parsed.empty:
            release_date = parsed.max().strftime("%Y-%m-%d")
    if "source_ref" in frame:
        refs = frame["source_ref"].dropna()
        source_ref = str(refs.iloc[0]) if not refs.empty else None

    result: dict[str, Any] = {
        "status": "READY",
        "current_ttm_eps": current_ttm_eps,
        "target_year": selected_year,
        "release_date": release_date,
        "source_ref": source_ref,
        "formula": "real GDP growth + PCE inflation",
        "method": "fomc_sep_macro_additive_growth",
        "limitation": "GDP와 PCE만 반영한 민감도이며 기업 마진·환율·자사주 효과는 포함하지 않습니다.",
    }
    for scenario, inputs in selected.items():
        growth_pct = _macro_growth(
            inputs["real_gdp"], inputs["pce_inflation"]
        )
        result[scenario] = {
            "real_gdp_pct": inputs["real_gdp"],
            "pce_inflation_pct": inputs["pce_inflation"],
            "growth_pct": growth_pct,
            "projected_eps": current_ttm_eps * (1.0 + (growth_pct / 100.0)),
        }
    return result


def calculate_index_scenario(
    *,
    multiple_regime: dict[str, Any],
    eps_scenarios: dict[str, Any],
    current_spx: dict[str, Any],
    current_spy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Combine macro EPS sensitivities and trailing-multiple zones into SPX scenarios."""
    if multiple_regime.get("status") != "READY" or eps_scenarios.get("status") != "READY":
        return {"status": "BLOCKED", "reason": "멀티플 또는 예상 EPS 근거가 충분하지 않습니다."}
    spx_price = float(current_spx.get("price") or 0)
    spx_date = str(current_spx.get("date") or "")
    if spx_price <= 0 or not spx_date:
        return {"status": "BLOCKED", "reason": "현재 SPX 기준값이 없습니다."}

    projected_eps = float(eps_scenarios["baseline"]["projected_eps"])
    values = {
        "lower": projected_eps * multiple_regime["minus_1sigma"],
        "baseline": projected_eps * multiple_regime["mean_multiple"],
        "upper": projected_eps * multiple_regime["plus_1sigma"],
    }
    gaps = {
        key: ((value / spx_price) - 1.0) * 100.0 for key, value in values.items()
    }
    current_vs_baseline_gap_pct = ((spx_price / values["baseline"]) - 1.0) * 100.0
    if current_vs_baseline_gap_pct > 0:
        valuation_position = "ABOVE_BASELINE"
    elif current_vs_baseline_gap_pct < 0:
        valuation_position = "BELOW_BASELINE"
    else:
        valuation_position = "AT_BASELINE"

    spy_equivalent = None
    spy_status = "UNAVAILABLE"
    if current_spy:
        spy_date = str(current_spy.get("date") or "")
        spy_price = float(current_spy.get("price") or 0)
        if spy_date != spx_date:
            spy_status = "DATE_MISMATCH"
        elif spy_price > 0:
            spy_status = "READY"
            spy_equivalent = {
                key: spy_price * value / spx_price for key, value in values.items()
            }
    return {
        "status": "READY",
        "as_of": spx_date,
        "current_spx": spx_price,
        "spx_scenarios": values,
        "gap_pct": gaps,
        "current_vs_baseline_gap_pct": current_vs_baseline_gap_pct,
        "valuation_position": valuation_position,
        "spy_status": spy_status,
        "spy_equivalent": spy_equivalent,
        "label": "예상 실적 기반 지수 시나리오",
        "limitation": "공식 적정가나 매수·매도 신호가 아닌 가정 조합 결과입니다.",
    }


def _price_evidence(
    current_prices: pd.DataFrame | list[dict[str, Any]], symbol: str
) -> dict[str, Any] | None:
    frame = pd.DataFrame(current_prices)
    if frame.empty or "symbol" not in frame:
        return None
    match = frame.loc[frame["symbol"] == symbol]
    if match.empty:
        return None
    row = match.iloc[-1]
    date = pd.to_datetime(row.get("latest_date"), errors="coerce")
    price = pd.to_numeric(row.get("price"), errors="coerce")
    if pd.isna(date) or pd.isna(price):
        return None
    return {"date": pd.Timestamp(date).strftime("%Y-%m-%d"), "price": float(price)}


def build_sp500_valuation_read_model(
    *,
    monthly_rows: pd.DataFrame | list[dict[str, Any]] | None = None,
    ttm_evidence: dict[str, Any] | None = None,
    sep_rows: pd.DataFrame | list[dict[str, Any]] | None = None,
    current_prices: pd.DataFrame | list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build the JSON-safe read model consumed by the React Market Context surface."""
    if monthly_rows is None or ttm_evidence is None or sep_rows is None or current_prices is None:
        from finance.loaders.price import load_latest_prices
        from finance.loaders.sp500_valuation import (
            load_latest_fomc_sep_projection,
            load_sp500_monthly_valuation,
            resolve_sp500_ttm_eps,
        )

        monthly_rows = monthly_rows if monthly_rows is not None else load_sp500_monthly_valuation()
        ttm_evidence = ttm_evidence if ttm_evidence is not None else resolve_sp500_ttm_eps()
        sep_rows = sep_rows if sep_rows is not None else load_latest_fomc_sep_projection()
        current_prices = (
            current_prices
            if current_prices is not None
            else load_latest_prices(["^GSPC", "SPY"])
        )

    ttm_evidence = dict(ttm_evidence or {})
    if (
        not ttm_evidence.get("eps_source_quality")
        and ttm_evidence.get("status", "READY") == "READY"
        and ttm_evidence.get("value_status") == "actual"
        and float(ttm_evidence.get("ttm_eps") or 0) > 0
    ):
        ttm_evidence.update(
            {
                "current_ttm_eps": float(ttm_evidence["ttm_eps"]),
                "eps_source": "S&P 공식 실제 EPS",
                "eps_source_quality": "official_actual",
                "eps_basis_date": ttm_evidence.get("latest_period_end"),
                "fallback_reason": None,
            }
        )
    spx = _price_evidence(current_prices, "^GSPC")
    spy = _price_evidence(current_prices, "SPY")
    multiple = calculate_multiple_regime(monthly_rows)
    current_ttm_eps = float(
        ttm_evidence.get("current_ttm_eps") or ttm_evidence.get("ttm_eps") or 0
    )
    eps_ready = (
        current_ttm_eps > 0
        and ttm_evidence.get("status", "READY") == "READY"
        and ttm_evidence.get("eps_source_quality")
        in {"official_actual", "interpolated_ttm_proxy"}
    )
    blocked = {
        "status": "BLOCKED",
        "reason": (
            ttm_evidence.get("fallback_reason")
            or "S&P 공식 실제 EPS 또는 Robert Shiller TTM EPS가 필요합니다."
        ),
    }
    if not eps_ready:
        earnings = dict(blocked)
        index = {"status": "BLOCKED", "reason": "EPS 기준값이 없습니다."}
    else:
        earnings = calculate_fomc_eps_scenarios(current_ttm_eps, sep_rows)
        earnings.update(
            {
                "eps_source": ttm_evidence.get("eps_source"),
                "eps_source_quality": ttm_evidence.get("eps_source_quality"),
                "eps_basis_date": ttm_evidence.get("eps_basis_date"),
                "fallback_reason": ttm_evidence.get("fallback_reason"),
            }
        )
        sep_release = pd.to_datetime(earnings.get("release_date"), errors="coerce")
        spx_date = pd.to_datetime(spx["date"], errors="coerce") if spx else pd.NaT
        if (
            earnings.get("status") == "READY"
            and not pd.isna(sep_release)
            and not pd.isna(spx_date)
            and (spx_date - sep_release).days > 180
        ):
            earnings["status"] = "STALE_SEP"
            earnings["reason"] = "최신 SPX 기준일보다 SEP 발표가 180일 넘게 오래되었습니다."
            index = {"status": "BLOCKED", "reason": earnings["reason"]}
        elif spx is None:
            index = {"status": "BLOCKED", "reason": "현재 SPX 기준값이 없습니다."}
        else:
            index = calculate_index_scenario(
                multiple_regime=multiple,
                eps_scenarios=earnings,
                current_spx=spx,
                current_spy=spy,
            )
        basis_dates = {
            "eps": ttm_evidence.get("eps_basis_date"),
            "sep": earnings.get("release_date"),
            "spx": spx.get("date") if spx else None,
        }
        distinct_dates = {str(value) for value in basis_dates.values() if value}
        index["basis_dates"] = basis_dates
        index["basis_date_mismatch"] = len(distinct_dates) > 1

    overall = "READY" if index.get("status") == "READY" else "BLOCKED"
    return {
        "schema_version": "sp500_valuation_v1",
        "status": overall,
        "basis": {
            "eps_basis": ttm_evidence.get("eps_source") or "EPS 기준 없음",
            "ttm_evidence": ttm_evidence,
            "spx": spx,
            "spy": spy,
            "official_window_months": 60,
            "sensitivity_window_months": 36,
        },
        "multiple_regime": multiple,
        "earnings_scenario": earnings,
        "index_scenario": index,
        "sources": [
            {"name": "Shiller 월별 가격·EPS", "role": "후행 PER 이력"},
            {
                "name": ttm_evidence.get("eps_source") or "EPS source 미확정",
                "role": "그래프 2 현재 TTM EPS 기준",
            },
            {"name": "Federal Reserve SEP", "role": "GDP·PCE 민감도"},
            {"name": "SPX·SPY EOD", "role": "현재 지수와 동일 기준일 환산"},
        ],
        "limitations": [
            "표준편차 구간은 상대평가 범위이며 신뢰구간이 아닙니다.",
            "FOMC 기반 EPS는 거시 민감도이며 애널리스트 컨센서스가 아닙니다.",
            "지수 시나리오는 공식 적정가나 투자 신호가 아닙니다.",
        ],
    }
