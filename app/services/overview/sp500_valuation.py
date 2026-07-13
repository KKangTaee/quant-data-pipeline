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
        "minus_2sigma": math.exp(mean_log - (2.0 * std_log)),
        "minus_1sigma": math.exp(mean_log - std_log),
        "plus_1sigma": math.exp(mean_log + std_log),
        "plus_2sigma": math.exp(mean_log + (2.0 * std_log)),
    }


def calculate_multiple_regime(
    monthly_rows: pd.DataFrame | list[dict[str, Any]],
    *,
    official_window: int = 60,
    sensitivity_window: int = 36,
    current_spx: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Calculate complete-only bands and extend the display with provisional P/E."""
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
    for column in ("trailing_pe", "trailing_eps", "spx_level"):
        if column not in frame:
            frame[column] = None
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = (
        frame.dropna(subset=["observation_month"])
        .sort_values("observation_month")
        .drop_duplicates("observation_month", keep="last")
        .reset_index(drop=True)
    )
    complete_frame = frame.loc[
        frame["trailing_pe"].notna() & (frame["trailing_pe"] > 0)
    ].copy()
    required = max(int(official_window), int(sensitivity_window), 2)
    if len(complete_frame) < required:
        return {
            "status": "INSUFFICIENT_HISTORY",
            "window_months": int(official_window),
            "observation_count": len(complete_frame),
            "series": [],
        }

    official_frame = complete_frame.tail(int(official_window))
    values = complete_frame["trailing_pe"].astype(float).tolist()
    official = _distribution(values, int(official_window))
    sensitivity = _distribution(values, int(sensitivity_window))
    latest_complete = complete_frame.iloc[-1]
    latest_complete_month = pd.Timestamp(latest_complete["observation_month"])
    eps_frame = frame.loc[
        (frame["observation_month"] <= latest_complete_month)
        & frame["trailing_eps"].notna()
        & (frame["trailing_eps"] > 0)
    ]
    latest_eps = float(eps_frame.iloc[-1]["trailing_eps"]) if not eps_frame.empty else None
    latest_eps_month = (
        pd.Timestamp(eps_frame.iloc[-1]["observation_month"])
        if not eps_frame.empty
        else None
    )

    display_points: dict[pd.Timestamp, dict[str, Any]] = {
        pd.Timestamp(row.observation_month): {
            "month": pd.Timestamp(row.observation_month).strftime("%Y-%m-%d"),
            "trailing_pe": float(row.trailing_pe),
            "quality": "complete",
            "price_basis_date": pd.Timestamp(row.observation_month).strftime("%Y-%m-%d"),
            "eps_basis_date": pd.Timestamp(row.observation_month).strftime("%Y-%m-%d"),
            "price_source": "robert_shiller_monthly",
        }
        for row in complete_frame.itertuples()
    }
    if latest_eps is not None and latest_eps_month is not None:
        price_only = frame.loc[
            (frame["observation_month"] > latest_complete_month)
            & frame["spx_level"].notna()
            & (frame["spx_level"] > 0)
        ]
        for row in price_only.itertuples():
            month = pd.Timestamp(row.observation_month)
            display_points[month] = {
                "month": month.strftime("%Y-%m-%d"),
                "trailing_pe": float(row.spx_level) / latest_eps,
                "quality": "provisional",
                "price_basis_date": month.strftime("%Y-%m-%d"),
                "eps_basis_date": latest_eps_month.strftime("%Y-%m-%d"),
                "price_source": "robert_shiller_monthly",
            }

        spx_date = pd.to_datetime((current_spx or {}).get("date"), errors="coerce")
        spx_price = pd.to_numeric((current_spx or {}).get("price"), errors="coerce")
        if not pd.isna(spx_date) and not pd.isna(spx_price) and float(spx_price) > 0:
            current_month = pd.Timestamp(spx_date).to_period("M").to_timestamp()
            if current_month > latest_complete_month:
                display_points[current_month] = {
                    "month": current_month.strftime("%Y-%m-%d"),
                    "trailing_pe": float(spx_price) / latest_eps,
                    "quality": "provisional",
                    "price_basis_date": pd.Timestamp(spx_date).strftime("%Y-%m-%d"),
                    "eps_basis_date": latest_eps_month.strftime("%Y-%m-%d"),
                    "price_source": "spx_eod",
                }

    series = [display_points[key] for key in sorted(display_points)][-int(official_window):]
    current_point = series[-1]
    current_pe = float(current_point["trailing_pe"])
    current_log = math.log(current_pe)
    current_z = (current_log - official["mean_log"]) / official["std_log"]
    sensitivity_z = (
        current_log - sensitivity["mean_log"]
    ) / sensitivity["std_log"]
    bucket = _bucket(current_z)
    sensitivity_bucket = _bucket(sensitivity_z)

    return {
        "status": "READY",
        "window_months": int(official_window),
        "observation_count": len(series),
        "series": series,
        "mean_multiple": official["mean_multiple"],
        "minus_2sigma": official["minus_2sigma"],
        "minus_1sigma": official["minus_1sigma"],
        "plus_1sigma": official["plus_1sigma"],
        "plus_2sigma": official["plus_2sigma"],
        "current_pe": current_pe,
        "current_basis_date": current_point["price_basis_date"],
        "current_price_basis_date": current_point["price_basis_date"],
        "current_eps_basis_date": current_point["eps_basis_date"],
        "current_is_provisional": current_point["quality"] == "provisional",
        "latest_complete_pe": float(latest_complete["trailing_pe"]),
        "latest_complete_basis_date": latest_complete_month.strftime("%Y-%m-%d"),
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
        "basis_start": official_frame.iloc[0]["observation_month"].strftime("%Y-%m-%d"),
        "basis_end": official_frame.iloc[-1]["observation_month"].strftime("%Y-%m-%d"),
        "distribution_basis_start": official_frame.iloc[0]["observation_month"].strftime("%Y-%m-%d"),
        "display_start": series[0]["month"],
        "display_end": series[-1]["month"],
        "methodology": "월별 후행 PER의 자연로그 평균과 표본 표준편차",
        "limitation": "잠정 PER는 최신 확인 EPS를 유지한 표시값이며 평균·표준편차 표본에는 포함하지 않습니다.",
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


def _sep_median_inputs(
    sep_frame: pd.DataFrame,
    *,
    observation_month: pd.Timestamp,
    effective_at: pd.Timestamp,
    monthly_point: bool,
) -> dict[str, Any] | None:
    releases = sep_frame.loc[
        sep_frame["release_date"] < observation_month
        if monthly_point
        else sep_frame["release_date"] <= effective_at
    ]
    if releases.empty:
        return None
    release_date = releases["release_date"].max()
    target_year = int(observation_month.year)
    vintage = releases.loc[
        (releases["release_date"] == release_date)
        & (releases["target_year"] == target_year)
        & (releases["statistic_name"] == "median")
    ]
    values: dict[str, float] = {}
    for variable_name in ("real_gdp", "pce_inflation"):
        match = vintage.loc[vintage["variable_name"] == variable_name, "value_pct"]
        if not match.empty:
            values[variable_name] = float(match.iloc[0])
    if len(values) != 2:
        return None
    return {
        "release_date": pd.Timestamp(release_date).strftime("%Y-%m-%d"),
        "target_year": target_year,
        **values,
    }


def calculate_historical_index_scenario(
    monthly_rows: pd.DataFrame | list[dict[str, Any]],
    sep_rows: pd.DataFrame | list[dict[str, Any]],
    *,
    current_spx: dict[str, Any] | None = None,
    visible_months: int = 12,
    rolling_window: int = 60,
) -> dict[str, Any]:
    """Reconstruct a bounded macro-implied SPX path using effective SEP vintages."""
    window_months = max(1, int(visible_months))
    window_years = window_months // 12 if window_months % 12 == 0 else None
    window_label = f"{window_years}년" if window_years else f"{window_months}개월"
    frame = pd.DataFrame(monthly_rows).copy()
    sep_frame = pd.DataFrame(sep_rows).copy()
    required_monthly = {"observation_month", "spx_level", "trailing_eps"}
    required_sep = {
        "release_date",
        "target_year",
        "variable_name",
        "statistic_name",
        "value_pct",
    }
    if frame.empty or sep_frame.empty or not required_monthly.issubset(frame.columns) or not required_sep.issubset(sep_frame.columns):
        return {
            "status": "INSUFFICIENT_HISTORY",
            "window_months": window_months,
            "window_years": window_years,
            "series": [],
            "sep_releases": [],
        }

    frame["observation_month"] = pd.to_datetime(frame["observation_month"], errors="coerce")
    for column in ("spx_level", "trailing_eps"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    if "trailing_pe" not in frame:
        frame["trailing_pe"] = frame["spx_level"] / frame["trailing_eps"]
    frame["trailing_pe"] = pd.to_numeric(frame["trailing_pe"], errors="coerce")
    frame = (
        frame.dropna(subset=["observation_month", "spx_level"])
        .loc[lambda value: value["spx_level"] > 0]
        .sort_values("observation_month")
        .drop_duplicates("observation_month", keep="last")
        .reset_index(drop=True)
    )
    if frame.empty:
        return {
            "status": "INSUFFICIENT_HISTORY",
            "window_months": window_months,
            "window_years": window_years,
            "series": [],
            "sep_releases": [],
        }

    spx_date = pd.to_datetime((current_spx or {}).get("date"), errors="coerce")
    spx_price = pd.to_numeric((current_spx or {}).get("price"), errors="coerce")
    if not pd.isna(spx_date) and not pd.isna(spx_price) and float(spx_price) > 0:
        current_month = pd.Timestamp(spx_date).to_period("M").to_timestamp()
        same_month = frame["observation_month"] == current_month
        if same_month.any():
            frame.loc[same_month, "spx_level"] = float(spx_price)
        elif current_month > frame["observation_month"].max():
            frame = pd.concat(
                [
                    frame,
                    pd.DataFrame(
                        [
                            {
                                "observation_month": current_month,
                                "spx_level": float(spx_price),
                                "trailing_eps": None,
                                "trailing_pe": None,
                            }
                        ]
                    ),
                ],
                ignore_index=True,
            )
    else:
        spx_date = pd.NaT

    positive_eps = frame["trailing_eps"].where(frame["trailing_eps"] > 0)
    frame["effective_eps"] = positive_eps.ffill()
    frame["eps_basis_date"] = frame["observation_month"].where(positive_eps.notna()).ffill()

    sep_frame["release_date"] = pd.to_datetime(sep_frame["release_date"], errors="coerce")
    sep_frame["target_year"] = pd.to_numeric(sep_frame["target_year"], errors="coerce")
    sep_frame["value_pct"] = pd.to_numeric(sep_frame["value_pct"], errors="coerce")
    sep_frame = sep_frame.dropna(subset=["release_date", "target_year", "value_pct"])
    if sep_frame.empty:
        return {
            "status": "INSUFFICIENT_HISTORY",
            "window_months": window_months,
            "window_years": window_years,
            "series": [],
            "sep_releases": [],
        }
    sep_frame["target_year"] = sep_frame["target_year"].astype(int)

    end_month = (
        pd.Timestamp(spx_date).to_period("M").to_timestamp()
        if not pd.isna(spx_date)
        else frame["observation_month"].max()
    )
    start_month = end_month - pd.DateOffset(months=window_months - 1)
    visible = frame.loc[
        (frame["observation_month"] >= start_month)
        & (frame["observation_month"] <= end_month)
    ]
    series: list[dict[str, Any]] = []
    for row in visible.itertuples():
        month = pd.Timestamp(row.observation_month)
        is_current = not pd.isna(spx_date) and month.to_period("M") == pd.Timestamp(spx_date).to_period("M")
        effective_at = pd.Timestamp(spx_date) if is_current else month
        sep_inputs = _sep_median_inputs(
            sep_frame,
            observation_month=month,
            effective_at=effective_at,
            monthly_point=not is_current,
        )
        eps = float(row.effective_eps) if not pd.isna(row.effective_eps) else 0.0
        pe_history = frame.loc[
            (frame["observation_month"] <= month)
            & frame["trailing_pe"].notna()
            & (frame["trailing_pe"] > 0),
            "trailing_pe",
        ].astype(float).tolist()
        if sep_inputs is None or eps <= 0 or len(pe_history) < int(rolling_window):
            continue
        multiple = _distribution(pe_history, int(rolling_window))
        growth_pct = _macro_growth(
            sep_inputs["real_gdp"], sep_inputs["pce_inflation"]
        )
        projected_eps = eps * (1.0 + growth_pct / 100.0)
        actual_spx = float(row.spx_level)
        baseline_spx = projected_eps * multiple["mean_multiple"]
        basis_date = pd.Timestamp(row.eps_basis_date).strftime("%Y-%m-%d")
        series.append(
            {
                "month": month.strftime("%Y-%m-%d"),
                "actual_spx": actual_spx,
                "eps_basis_date": basis_date,
                "eps_carried_forward": basis_date != month.strftime("%Y-%m-%d"),
                "current_ttm_eps": eps,
                "sep_release_date": sep_inputs["release_date"],
                "target_year": sep_inputs["target_year"],
                "real_gdp_pct": sep_inputs["real_gdp"],
                "pce_inflation_pct": sep_inputs["pce_inflation"],
                "growth_pct": growth_pct,
                "projected_eps": projected_eps,
                "lower_spx": projected_eps * multiple["minus_1sigma"],
                "baseline_spx": baseline_spx,
                "upper_spx": projected_eps * multiple["plus_1sigma"],
                "gap_to_baseline_pct": ((actual_spx / baseline_spx) - 1.0) * 100.0,
            }
        )

    visible_releases = sorted(
        {
            pd.Timestamp(value).strftime("%Y-%m-%d")
            for value in sep_frame["release_date"]
            if start_month <= pd.Timestamp(value) <= (pd.Timestamp(spx_date) if not pd.isna(spx_date) else end_month + pd.offsets.MonthEnd(0))
        }
    )
    status = "READY" if len(series) >= 2 else "INSUFFICIENT_HISTORY"
    required_history_months = int(rolling_window) + window_months - 1
    available_history_months = int(
        frame.loc[
            (frame["observation_month"] <= end_month)
            & frame["trailing_pe"].notna()
            & (frame["trailing_pe"] > 0),
            "observation_month",
        ].nunique()
    )
    readiness = {
        "requested_display_months": window_months,
        "rolling_window_months": int(rolling_window),
        "required_history_months": required_history_months,
        "available_history_months": available_history_months,
        "missing_history_months": max(
            0, required_history_months - available_history_months
        ),
    }
    if status != "READY" and available_history_months < required_history_months:
        readiness["reason_code"] = "INSUFFICIENT_ROLLING_PER_WARMUP"
    return {
        "status": status,
        "window_months": window_months,
        "window_years": window_years,
        "observation_count": len(series),
        "coverage_start": series[0]["month"] if series else None,
        "coverage_end": series[-1]["month"] if series else None,
        "rolling_multiple_months": int(rolling_window),
        "series": series,
        "sep_releases": visible_releases,
        "label": f"최근 {window_label} 과거 시점 재구성 시나리오",
        "methodology": "각 월에 당시 사용 가능한 최신 SEP와 60개월 rolling log(PER)를 적용",
        "limitation": "Shiller EPS는 release-vintage PIT 원본이 아니며 미발표 월은 최신 확인 TTM EPS를 유지합니다.",
        **readiness,
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
    sep_history_rows: pd.DataFrame | list[dict[str, Any]] | None = None,
    current_prices: pd.DataFrame | list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build the JSON-safe read model consumed by the React Market Context surface."""
    sep_rows_supplied = sep_rows is not None
    if monthly_rows is None or ttm_evidence is None or sep_rows is None or current_prices is None or sep_history_rows is None:
        from finance.loaders.price import load_latest_prices
        from finance.loaders.sp500_valuation import (
            load_latest_fomc_sep_projection,
            load_fomc_sep_projection_history,
            load_sp500_monthly_valuation,
            resolve_sp500_ttm_eps,
        )

        monthly_rows = monthly_rows if monthly_rows is not None else load_sp500_monthly_valuation()
        ttm_evidence = ttm_evidence if ttm_evidence is not None else resolve_sp500_ttm_eps()
        sep_rows = sep_rows if sep_rows is not None else load_latest_fomc_sep_projection()
        sep_history_rows = (
            sep_history_rows
            if sep_history_rows is not None
            else (sep_rows if sep_rows_supplied else load_fomc_sep_projection_history())
        )
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
    multiple = calculate_multiple_regime(monthly_rows, current_spx=spx)
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

    history_options = {
        key: calculate_historical_index_scenario(
            monthly_rows,
            [] if sep_history_rows is None else sep_history_rows,
            current_spx=spx,
            visible_months=months,
        )
        for key, months in (("1y", 12), ("3y", 36), ("5y", 60))
    }
    index["history_options"] = history_options
    index["history"] = history_options["1y"]

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
