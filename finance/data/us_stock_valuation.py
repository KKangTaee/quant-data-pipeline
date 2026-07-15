from __future__ import annotations

import math
import statistics
from collections.abc import Iterable, Mapping
from typing import Any

import pandas as pd

from finance.data.nasdaq100_valuation import derive_filing_aware_ttm_eps


def _split_factor_from_frame(
    frame: pd.DataFrame,
    *,
    after: str | pd.Timestamp,
    through: str | pd.Timestamp,
) -> float:
    """Multiply split events after a fact and no later than the PIT cutoff."""
    if frame.empty or not {"date", "stock_splits"}.issubset(frame.columns):
        return 1.0
    start = pd.to_datetime(after, errors="coerce")
    end = pd.to_datetime(through, errors="coerce")
    if pd.isna(start) or pd.isna(end):
        return 1.0
    events = frame.loc[
        frame["date"].notna()
        & (frame["date"] > pd.Timestamp(start))
        & (frame["date"] <= pd.Timestamp(end))
        & frame["stock_splits"].notna()
        & (frame["stock_splits"] > 0),
        "stock_splits",
    ]
    return float(events.product()) if not events.empty else 1.0


def split_factor_between(
    price_rows: Iterable[Mapping[str, Any]],
    *,
    after: str | pd.Timestamp,
    through: str | pd.Timestamp,
) -> float:
    """Return only splits known after a fact and through the valuation cutoff."""
    frame = pd.DataFrame([dict(row) for row in price_rows])
    if frame.empty or not {"date", "stock_splits"}.issubset(frame.columns):
        return 1.0
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame["stock_splits"] = pd.to_numeric(frame["stock_splits"], errors="coerce")
    return _split_factor_from_frame(frame, after=after, through=through)


def _price_frame(price_rows: list[dict[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame(price_rows)
    if frame.empty or not {"date", "close"}.issubset(frame.columns):
        return pd.DataFrame(columns=["symbol", "date", "close", "stock_splits"])
    if "symbol" not in frame:
        frame["symbol"] = None
    if "stock_splits" not in frame:
        frame["stock_splits"] = 0.0
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
    frame["stock_splits"] = pd.to_numeric(frame["stock_splits"], errors="coerce").fillna(0.0)
    return (
        frame.dropna(subset=["date"])
        .sort_values(["symbol", "date"], na_position="first")
        .drop_duplicates(["symbol", "date"], keep="last")
        .reset_index(drop=True)
    )


def build_monthly_pit_valuation(
    statement_rows: Iterable[Mapping[str, Any]],
    price_rows: Iterable[Mapping[str, Any]],
    *,
    start_month: str,
    end_month: str,
) -> list[dict[str, Any]]:
    """Build explicit calendar-month rows without interpolating price or EPS."""
    statements = [dict(row) for row in statement_rows]
    prices = [dict(row) for row in price_rows]
    price_frame = _price_frame(prices)
    start = pd.Timestamp(start_month).to_period("M").to_timestamp()
    end = pd.Timestamp(end_month).to_period("M").to_timestamp()
    symbols = {
        str(row.get("symbol") or "").strip().upper()
        for row in statements + prices
        if str(row.get("symbol") or "").strip()
    }
    symbol = sorted(symbols)[0] if symbols else ""
    rows: list[dict[str, Any]] = []

    for month in pd.date_range(start, end, freq="MS"):
        month_end = month + pd.offsets.MonthEnd(0)
        month_prices = price_frame.loc[
            (price_frame["date"] >= month)
            & (price_frame["date"] <= month_end)
            & price_frame["close"].notna()
            & (price_frame["close"] > 0)
        ]
        if symbol:
            month_prices = month_prices.loc[
                month_prices["symbol"].astype(str).str.upper() == symbol
            ]
        price_row = month_prices.iloc[-1] if not month_prices.empty else None
        price = float(price_row["close"]) if price_row is not None else None
        price_basis_date = (
            pd.Timestamp(price_row["date"]).strftime("%Y-%m-%d")
            if price_row is not None
            else None
        )

        normalized_statements: list[dict[str, Any]] = []
        for statement in statements:
            available_at = pd.to_datetime(statement.get("available_at"), errors="coerce")
            value = pd.to_numeric(statement.get("value"), errors="coerce")
            if pd.isna(available_at) or pd.isna(value) or pd.Timestamp(available_at) > month_end:
                continue
            fact_split_factor = _split_factor_from_frame(
                price_frame,
                after=pd.Timestamp(available_at),
                through=month_end,
            )
            normalized_statements.append(
                {
                    **statement,
                    "value": float(value) / fact_split_factor,
                }
            )

        resolved = derive_filing_aware_ttm_eps(
            normalized_statements,
            as_of_date=month_end.strftime("%Y-%m-%d"),
        )
        evidence = resolved.get(symbol) if symbol else None
        quarters = list((evidence or {}).get("quarters") or [])
        adjusted_quarters: list[dict[str, Any]] = []
        for quarter in quarters:
            factor = _split_factor_from_frame(
                price_frame,
                after=str(quarter["available_at"]),
                through=month_end,
            )
            adjusted_quarters.append(
                {
                    **quarter,
                    "raw_eps": float(quarter["eps"]) * factor,
                    "eps": float(quarter["eps"]),
                    "split_factor": factor,
                }
            )
        ttm_eps = (
            sum(float(quarter["eps"]) for quarter in adjusted_quarters)
            if len(adjusted_quarters) == 4
            else None
        )
        eps_basis_date = (
            max(str(quarter["available_at"]) for quarter in adjusted_quarters)
            if adjusted_quarters
            else None
        )
        split_factor = (
            max(float(quarter["split_factor"]) for quarter in adjusted_quarters)
            if adjusted_quarters
            else 1.0
        )

        if price is None:
            quality = "missing_price"
        elif ttm_eps is None:
            quality = "insufficient_eps"
        elif ttm_eps <= 0:
            quality = "non_positive_eps"
        else:
            quality = "complete"
        trailing_pe = (
            price / ttm_eps
            if price is not None and ttm_eps is not None and ttm_eps > 0
            else None
        )
        rows.append(
            {
                "symbol": symbol or None,
                "month": month.strftime("%Y-%m-%d"),
                "price": price,
                "price_basis_date": price_basis_date,
                "ttm_eps": ttm_eps,
                "eps_basis_date": eps_basis_date,
                "trailing_pe": trailing_pe,
                "quarter_ends": [str(quarter["period_end"]) for quarter in adjusted_quarters],
                "quarters": adjusted_quarters,
                "split_factor": split_factor,
                "quality": quality,
            }
        )
    return rows


def _multiple_distribution(values: list[float], window_months: int) -> dict[str, float]:
    selected = values[-int(window_months) :]
    logs = [math.log(value) for value in selected]
    mean_log = statistics.fmean(logs)
    std_log = statistics.stdev(logs) if len(logs) > 1 else 0.0
    return {
        "mean_log": mean_log,
        "std_log": std_log,
        "mean_multiple": math.exp(mean_log),
        "minus_2sigma": math.exp(mean_log - 2.0 * std_log),
        "minus_1sigma": math.exp(mean_log - std_log),
        "plus_1sigma": math.exp(mean_log + std_log),
        "plus_2sigma": math.exp(mean_log + 2.0 * std_log),
    }


def _multiple_bucket(z_score: float) -> str:
    if z_score < -1.0:
        return "LOW"
    if z_score < 1.0:
        return "NEUTRAL"
    if z_score < 2.0:
        return "HIGH"
    return "EXTREME_HIGH"


def calculate_stock_multiple_regime(
    monthly_rows: Iterable[Mapping[str, Any]],
    *,
    official_window: int = 60,
    sensitivity_window: int = 36,
) -> dict[str, Any]:
    """Calculate positive complete-only log(P/E) bands for one stock."""
    frame = pd.DataFrame([dict(row) for row in monthly_rows])
    required_columns = {"month", "trailing_pe"}
    official = max(2, int(official_window))
    sensitivity = max(2, int(sensitivity_window))
    if frame.empty or not required_columns.issubset(frame.columns):
        return {
            "status": "INSUFFICIENT_HISTORY",
            "window_months": official,
            "observation_count": 0,
            "series": [],
        }
    frame["month"] = pd.to_datetime(frame["month"], errors="coerce")
    frame["trailing_pe"] = pd.to_numeric(frame["trailing_pe"], errors="coerce")
    if "quality" not in frame:
        frame["quality"] = "complete"
    complete = (
        frame.loc[
            frame["month"].notna()
            & frame["trailing_pe"].notna()
            & (frame["trailing_pe"] > 0)
            & frame["quality"].astype(str).eq("complete")
        ]
        .sort_values("month")
        .drop_duplicates("month", keep="last")
    )
    if len(complete) < official:
        return {
            "status": "INSUFFICIENT_HISTORY",
            "window_months": official,
            "observation_count": int(len(complete)),
            "series": [],
        }
    official_frame = complete.tail(official)
    values = complete["trailing_pe"].astype(float).tolist()
    official_stats = _multiple_distribution(values, official)
    sensitivity_stats = _multiple_distribution(values, sensitivity)
    current = official_frame.iloc[-1]
    current_pe = float(current["trailing_pe"])
    current_log = math.log(current_pe)
    official_z = (
        (current_log - official_stats["mean_log"]) / official_stats["std_log"]
        if official_stats["std_log"] > 0
        else 0.0
    )
    sensitivity_z = (
        (current_log - sensitivity_stats["mean_log"]) / sensitivity_stats["std_log"]
        if sensitivity_stats["std_log"] > 0
        else 0.0
    )
    bucket = _multiple_bucket(official_z)
    sensitivity_bucket = _multiple_bucket(sensitivity_z)
    series = [
        {
            "month": pd.Timestamp(row.month).strftime("%Y-%m-%d"),
            "trailing_pe": float(row.trailing_pe),
            "quality": "complete",
            "price_basis_date": getattr(row, "price_basis_date", None),
            "eps_basis_date": getattr(row, "eps_basis_date", None),
        }
        for row in official_frame.itertuples()
    ]
    return {
        "status": "READY",
        "window_months": official,
        "observation_count": len(series),
        "series": series,
        **official_stats,
        "current_pe": current_pe,
        "current_z": official_z,
        "bucket": bucket,
        "current_basis_date": series[-1]["price_basis_date"] or series[-1]["month"],
        "current_price_basis_date": series[-1]["price_basis_date"],
        "current_eps_basis_date": series[-1]["eps_basis_date"],
        "sensitivity": {
            "window_months": sensitivity,
            "observation_count": sensitivity,
            "mean_multiple": sensitivity_stats["mean_multiple"],
            "current_z": sensitivity_z,
            "bucket": sensitivity_bucket,
        },
        "period_sensitive": bucket != sensitivity_bucket,
        "basis_start": series[0]["month"],
        "basis_end": series[-1]["month"],
        "methodology": "월별 positive P/E의 자연로그 평균과 표본 표준편차",
        "limitation": "기업 자체의 최근 멀티플 분포이며 절대 내재가치나 신뢰구간이 아닙니다.",
    }


def _normalize_sep_rows(sep_rows: Iterable[Mapping[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame([dict(row) for row in sep_rows])
    required = {"release_date", "target_year", "variable_name", "statistic_name", "value_pct"}
    if frame.empty or not required.issubset(frame.columns):
        return pd.DataFrame(columns=sorted(required))
    frame["release_date"] = pd.to_datetime(frame["release_date"], errors="coerce")
    frame["target_year"] = pd.to_numeric(frame["target_year"], errors="coerce")
    frame["value_pct"] = pd.to_numeric(frame["value_pct"], errors="coerce")
    frame = frame.dropna(subset=["release_date", "target_year", "value_pct"])
    frame["target_year"] = frame["target_year"].astype(int)
    return frame


def _sep_macro_as_of(
    sep_frame: pd.DataFrame,
    *,
    effective_at: pd.Timestamp,
    target_year: int,
) -> dict[str, Any] | None:
    eligible = sep_frame.loc[
        (sep_frame["release_date"] <= effective_at)
        & (sep_frame["target_year"] == int(target_year))
        & frame_statistic_median(sep_frame)
    ]
    for release_date in sorted(eligible["release_date"].unique(), reverse=True):
        vintage = eligible.loc[eligible["release_date"] == release_date]
        values: dict[str, float] = {}
        for variable in ("real_gdp", "pce_inflation"):
            match = vintage.loc[vintage["variable_name"] == variable, "value_pct"]
            if not match.empty:
                values[variable] = float(match.iloc[-1])
        if len(values) == 2:
            return {
                "release_date": pd.Timestamp(release_date).strftime("%Y-%m-%d"),
                "target_year": int(target_year),
                "real_gdp_pct": values["real_gdp"],
                "pce_inflation_pct": values["pce_inflation"],
                "macro_pct": values["real_gdp"] + values["pce_inflation"],
            }
    return None


def frame_statistic_median(frame: pd.DataFrame) -> pd.Series:
    """Keep the median predicate explicit for readable SEP filtering."""
    return frame["statistic_name"].astype(str).eq("median")


def calculate_company_excess_growth(
    quarterly_ttm_rows: Iterable[Mapping[str, Any]],
    sep_rows: Iterable[Mapping[str, Any]],
    *,
    as_of_date: str,
) -> dict[str, Any]:
    """Estimate recent company EPS growth in excess of applicable SEP macro proxy."""
    frame = pd.DataFrame([dict(row) for row in quarterly_ttm_rows])
    sep_frame = _normalize_sep_rows(sep_rows)
    required = {"period_end", "available_at", "ttm_eps"}
    as_of = pd.Timestamp(as_of_date)
    if frame.empty or sep_frame.empty or not required.issubset(frame.columns):
        return {"status": "INSUFFICIENT_HISTORY", "observation_count": 0, "observations": []}
    frame["period_end"] = pd.to_datetime(frame["period_end"], errors="coerce")
    frame["available_at"] = pd.to_datetime(frame["available_at"], errors="coerce")
    frame["ttm_eps"] = pd.to_numeric(frame["ttm_eps"], errors="coerce")
    frame = (
        frame.dropna(subset=["period_end", "available_at", "ttm_eps"])
        .loc[lambda value: value["available_at"] <= as_of]
        .sort_values(["period_end", "available_at"])
        .drop_duplicates("period_end", keep="last")
        .reset_index(drop=True)
    )
    if frame.empty:
        return {"status": "INSUFFICIENT_HISTORY", "observation_count": 0, "observations": []}
    latest_available = pd.Timestamp(frame["available_at"].max())
    recent_start = latest_available - pd.DateOffset(years=3)
    observations: list[dict[str, Any]] = []
    for index in range(4, len(frame)):
        current = frame.iloc[index]
        previous = frame.iloc[index - 4]
        current_eps = float(current["ttm_eps"])
        previous_eps = float(previous["ttm_eps"])
        if current_eps <= 0 or previous_eps <= 0 or pd.Timestamp(current["available_at"]) < recent_start:
            continue
        macro = _sep_macro_as_of(
            sep_frame,
            effective_at=pd.Timestamp(current["available_at"]),
            target_year=int(pd.Timestamp(current["period_end"]).year),
        )
        if macro is None:
            continue
        company_yoy_pct = ((current_eps / previous_eps) - 1.0) * 100.0
        observations.append(
            {
                "period_end": pd.Timestamp(current["period_end"]).strftime("%Y-%m-%d"),
                "available_at": pd.Timestamp(current["available_at"]).strftime("%Y-%m-%d"),
                "company_yoy_pct": company_yoy_pct,
                "macro_baseline_pct": float(macro["macro_pct"]),
                "excess_growth_pct": company_yoy_pct - float(macro["macro_pct"]),
                "sep_release_date": macro["release_date"],
                "sep_target_year": macro["target_year"],
            }
        )
    values = pd.Series([row["excess_growth_pct"] for row in observations], dtype="float64")
    current_macro = _sep_macro_as_of(
        sep_frame,
        effective_at=as_of,
        target_year=int(as_of.year),
    )
    base = {
        "observation_count": len(observations),
        "observations": observations,
        "current_macro_pct": current_macro.get("macro_pct") if current_macro else None,
        "current_real_gdp_pct": current_macro.get("real_gdp_pct") if current_macro else None,
        "current_pce_inflation_pct": current_macro.get("pce_inflation_pct") if current_macro else None,
        "current_sep_release_date": current_macro.get("release_date") if current_macro else None,
    }
    if len(values) < 8 or current_macro is None:
        return {"status": "INSUFFICIENT_HISTORY", **base}
    q1 = float(values.quantile(0.25))
    q3 = float(values.quantile(0.75))
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    clipped = values.clip(lower=lower, upper=upper)
    return {
        "status": "READY",
        **base,
        "p25_pct": float(clipped.quantile(0.25)),
        "p50_pct": float(clipped.quantile(0.50)),
        "p75_pct": float(clipped.quantile(0.75)),
        "tukey_lower_pct": lower,
        "tukey_upper_pct": upper,
        "raw_min_pct": float(values.min()),
        "raw_max_pct": float(values.max()),
        "clipped_min_pct": float(clipped.min()),
        "clipped_max_pct": float(clipped.max()),
    }


def calculate_stock_scenarios(
    current_ttm_eps: float,
    multiple_regime: Mapping[str, Any],
    excess_growth: Mapping[str, Any],
) -> dict[str, Any]:
    """Combine macro/excess EPS growth with the stock's own P/E anchors."""
    eps = float(current_ttm_eps)
    if eps <= 0:
        return {"status": "NOT_APPLICABLE", "reason_code": "NON_POSITIVE_EPS"}
    if multiple_regime.get("status") != "READY":
        return {
            "status": "BLOCKED",
            "reason_code": "MULTIPLE_HISTORY_INSUFFICIENT",
            "reason": "최근 positive P/E 멀티플 근거가 충분하지 않습니다.",
        }
    if excess_growth.get("status") != "READY":
        observations = int(excess_growth.get("observation_count") or 0)
        return {
            "status": "BLOCKED",
            "reason_code": "INSUFFICIENT_GROWTH_HISTORY",
            "reason": f"최근 3년 positive-to-positive TTM EPS 성장 관측이 {observations}/8개입니다.",
            "observation_count": observations,
            "required_observations": 8,
        }
    macro = float(excess_growth["current_macro_pct"])
    definitions = {
        "conservative": ("p25_pct", "minus_1sigma"),
        "baseline": ("p50_pct", "mean_multiple"),
        "optimistic": ("p75_pct", "plus_1sigma"),
    }
    result: dict[str, Any] = {
        "status": "READY",
        "current_ttm_eps": eps,
        "current_macro_pct": macro,
        "sep_release_date": excess_growth.get("current_sep_release_date"),
        "label": "거시·기업 실적 결합 상대가치 시나리오",
        "limitation": "공식 목표주가나 매매 신호가 아닌 자체 재구성 시나리오입니다.",
    }
    for scenario, (percentile_key, multiple_key) in definitions.items():
        excess_pct = float(excess_growth[percentile_key])
        growth_pct = macro + excess_pct
        projected_eps = eps * (1.0 + growth_pct / 100.0)
        multiple = float(multiple_regime[multiple_key])
        result[scenario] = {
            "macro_pct": macro,
            "company_excess_pct": excess_pct,
            "growth_pct": growth_pct,
            "projected_eps": projected_eps,
            "multiple": multiple,
            "price": projected_eps * multiple if projected_eps > 0 else None,
        }
    return result


def calculate_historical_stock_scenario(
    monthly_rows: Iterable[Mapping[str, Any]],
    quarterly_ttm_rows: Iterable[Mapping[str, Any]],
    sep_rows: Iterable[Mapping[str, Any]],
    *,
    visible_months: int,
    rolling_window: int = 60,
) -> dict[str, Any]:
    """Reconstruct visible months using only evidence available at each month-end."""
    rows = [dict(row) for row in monthly_rows]
    frame = pd.DataFrame(rows)
    visible = max(1, int(visible_months))
    rolling = max(2, int(rolling_window))
    required_history = rolling + visible - 1
    if frame.empty or not {"month", "trailing_pe", "ttm_eps", "price"}.issubset(frame.columns):
        return {
            "status": "INSUFFICIENT_HISTORY",
            "observation_count": 0,
            "series": [],
            "required_history_months": required_history,
            "available_history_months": 0,
            "reason_code": "INSUFFICIENT_ROLLING_PER_WARMUP",
        }
    frame["month"] = pd.to_datetime(frame["month"], errors="coerce")
    frame["trailing_pe"] = pd.to_numeric(frame["trailing_pe"], errors="coerce")
    frame = frame.dropna(subset=["month"]).sort_values("month").drop_duplicates("month", keep="last")
    end_month = pd.Timestamp(frame["month"].max())
    visible_frame = frame.tail(visible)
    series: list[dict[str, Any]] = []
    for row in visible_frame.itertuples():
        month = pd.Timestamp(row.month)
        month_end = month + pd.offsets.MonthEnd(0)
        history_rows = frame.loc[frame["month"] <= month].to_dict("records")
        multiple = calculate_stock_multiple_regime(
            [{**item, "month": pd.Timestamp(item["month"]).strftime("%Y-%m-%d")} for item in history_rows],
            official_window=rolling,
            sensitivity_window=min(36, rolling),
        )
        excess = calculate_company_excess_growth(
            quarterly_ttm_rows,
            sep_rows,
            as_of_date=month_end.strftime("%Y-%m-%d"),
        )
        eps = pd.to_numeric(getattr(row, "ttm_eps", None), errors="coerce")
        price = pd.to_numeric(getattr(row, "price", None), errors="coerce")
        if multiple.get("status") != "READY" or excess.get("status") != "READY" or pd.isna(eps) or pd.isna(price):
            continue
        scenario = calculate_stock_scenarios(float(eps), multiple, excess)
        if scenario.get("status") != "READY":
            continue
        series.append(
            {
                "month": month.strftime("%Y-%m-%d"),
                "actual_price": float(price),
                "current_ttm_eps": float(eps),
                "sep_release_date": excess.get("current_sep_release_date"),
                "current_macro_pct": excess.get("current_macro_pct"),
                "lower_price": scenario["conservative"]["price"],
                "baseline_price": scenario["baseline"]["price"],
                "upper_price": scenario["optimistic"]["price"],
                "gap_to_baseline_pct": (
                    (float(price) / float(scenario["baseline"]["price"])) - 1.0
                )
                * 100.0,
            }
        )
    positive = frame.loc[frame["trailing_pe"].notna() & (frame["trailing_pe"] > 0), "month"]
    available = int(positive.nunique())
    status = "READY" if len(series) == visible else "INSUFFICIENT_HISTORY"
    result = {
        "status": status,
        "window_months": visible,
        "observation_count": len(series),
        "series": series,
        "required_history_months": required_history,
        "available_history_months": available,
        "missing_history_months": max(0, required_history - available),
        "coverage_start": series[0]["month"] if series else None,
        "coverage_end": series[-1]["month"] if series else None,
        "rolling_multiple_months": rolling,
        "label": f"최근 {visible}개월 과거 시점 상대가치 시나리오",
        "methodology": "각 월말의 filing/SEP available-at와 rolling log(P/E)만 사용",
    }
    if status != "READY" and available < required_history:
        result["reason_code"] = "INSUFFICIENT_ROLLING_PER_WARMUP"
    elif status != "READY":
        result["reason_code"] = "INSUFFICIENT_PIT_EVIDENCE"
    return result


def classify_us_stock_readiness(
    identity: Mapping[str, Any] | None,
    coverage: Mapping[str, Any],
    monthly_rows: Iterable[Mapping[str, Any]],
    growth_evidence: Mapping[str, Any],
) -> dict[str, Any]:
    """Separate repairable raw gaps from structurally invalid P/E cases."""
    if not identity:
        return {"status": "ERROR", "reason_code": "IDENTITY_MISSING", "reason": "선택 기업 identity를 확인하지 못했습니다."}
    if identity.get("instrument_type") != "common_stock":
        return {"status": "NOT_APPLICABLE", "reason_code": "UNSUPPORTED_INSTRUMENT", "reason": "V1은 미국 보통주만 지원합니다."}
    if identity.get("adr_unit_status") == "unverified":
        return {"status": "NOT_APPLICABLE", "reason_code": "ADR_UNIT_UNVERIFIED", "reason": "ADR 주당 단위와 거래 증권 비율을 확인할 수 없습니다."}
    requested = int(coverage.get("requested_months") or 60)
    listing_months = coverage.get("listing_months")
    if listing_months is not None and int(listing_months) < requested:
        return {
            "status": "NOT_APPLICABLE",
            "reason_code": "STRUCTURALLY_SHORT_LISTING",
            "reason": f"상장 이력 {int(listing_months)}개월로 필요한 {requested}개월을 충족할 수 없습니다.",
        }
    rows = sorted(
        [dict(row) for row in monthly_rows],
        key=lambda row: str(row.get("month") or ""),
    )
    latest_eps = pd.to_numeric(rows[-1].get("ttm_eps"), errors="coerce") if rows else float("nan")
    if not pd.isna(latest_eps) and float(latest_eps) <= 0:
        return {"status": "NOT_APPLICABLE", "reason_code": "NON_POSITIVE_EPS", "reason": "현재 TTM EPS가 0 이하라 PER로 평가할 수 없습니다."}
    missing_scopes = []
    if coverage.get("price_missing"):
        missing_scopes.append("prices")
    if coverage.get("statement_missing"):
        missing_scopes.append("sec_statements")
    if missing_scopes:
        if not str(identity.get("cik") or "").strip():
            missing_scopes.insert(0, "sec_identity")
        return {
            "status": "COLLECTABLE",
            "reason_code": "RAW_DATA_GAP",
            "reason": "선택 기업의 저장 가격 또는 SEC 실적 자료가 부족합니다.",
            "collection_scopes": missing_scopes,
        }
    complete_count = sum(
        1
        for row in rows
        if row.get("quality") == "complete"
        and pd.notna(pd.to_numeric(row.get("trailing_pe"), errors="coerce"))
        and float(row["trailing_pe"]) > 0
    )
    if complete_count < 60:
        return {
            "status": "COLLECTABLE",
            "reason_code": "INCOMPLETE_MONTHLY_RAW_DATA",
            "reason": f"positive P/E 월이 {complete_count}/60개입니다.",
            "collection_scopes": ["prices", "sec_statements"],
        }
    return {"status": "READY", "reason_code": None, "reason": None}
