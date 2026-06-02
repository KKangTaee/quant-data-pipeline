from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from typing import Any

import pandas as pd

from app.services.futures_macro_thermometer import (
    DAILY_INTERVAL,
    MIN_RECOMMENDED_DAYS,
    QueryFn,
    _default_query,
    _instrument_rows,
    _round,
    _safe_float,
    build_current_evidence_groups,
    compute_macro_scores,
    compute_symbol_metrics,
    generate_market_interpretation,
    normalize_futures_macro_daily_candles,
)
from finance.data.futures_market import DEFAULT_CORE_FUTURES_SYMBOLS


DEFAULT_VALIDATION_YEARS = 5
MIN_VALIDATION_YEARS = 3
VALIDATION_HORIZONS = (1, 5, 20)
VALIDATION_THRESHOLDS = (20, 40, 60)
PROXY_TARGET_SYMBOLS = ("SPY", "QQQ", "IWM", "TLT", "GLD", "UUP")

FUTURES_PROXY_MAP = {
    "ES=F": "SPY",
    "NQ=F": "QQQ",
    "RTY=F": "IWM",
    "ZN=F": "TLT",
    "ZB=F": "TLT",
    "GC=F": "GLD",
}

VALIDATION_CAVEATS = [
    "Historical validation is an ex-post consistency check, not a prediction guarantee.",
    "Futures targets use stored yfinance continuous futures rows when available.",
    "ETF proxy targets are labeled separately and do not prove futures contract performance.",
    "yfinance continuous futures can differ from exchange roll and maturity behavior.",
]


@dataclass(frozen=True)
class BasketReturn:
    value: float | None
    source: str
    symbols: str


def _load_validation_futures_rows(
    query_fn: QueryFn,
    *,
    symbols: Sequence[str],
    lookback_days: int,
) -> list[dict[str, Any]]:
    if not symbols:
        return []
    placeholders = ", ".join(["%s"] * len(symbols))
    params: list[Any] = [DAILY_INTERVAL, *symbols, max(1, int(lookback_days))]
    try:
        return query_fn(
            "finance_price",
            f"""
            SELECT provider_symbol, interval_code, candle_time_utc,
                   open, high, low, close, volume, source, provider_status
            FROM futures_ohlcv
            WHERE interval_code = %s
              AND provider_symbol IN ({placeholders})
              AND candle_time_utc >= DATE_SUB(UTC_TIMESTAMP(), INTERVAL %s DAY)
            ORDER BY provider_symbol, candle_time_utc
            """,
            params,
        )
    except Exception:
        return []


def _load_proxy_price_rows(
    query_fn: QueryFn,
    *,
    symbols: Sequence[str],
    lookback_days: int,
) -> list[dict[str, Any]]:
    if not symbols:
        return []
    placeholders = ", ".join(["%s"] * len(symbols))
    params: list[Any] = [*symbols, "1d", max(1, int(lookback_days))]
    try:
        return query_fn(
            "finance_price",
            f"""
            SELECT symbol, timeframe, `date`, close, adj_close, volume
            FROM nyse_price_history
            WHERE symbol IN ({placeholders})
              AND timeframe = %s
              AND `date` >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            ORDER BY symbol, `date`
            """,
            params,
        )
    except Exception:
        return []


def _matrix_from_futures_candles(candles: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(candles, pd.DataFrame) or candles.empty:
        return pd.DataFrame()
    frame = candles.copy()
    frame["date"] = pd.to_datetime(frame["Date"], errors="coerce").dt.normalize()
    frame["Close"] = pd.to_numeric(frame["Close"], errors="coerce")
    matrix = frame.pivot_table(index="date", columns="provider_symbol", values="Close", aggfunc="last")
    return matrix.sort_index()


def _matrix_from_proxy_rows(rows: Sequence[dict[str, Any]]) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for row in rows:
        symbol = str(row.get("symbol") or "").strip().upper()
        ts = pd.to_datetime(row.get("date"), errors="coerce")
        close = _safe_float(row.get("adj_close"))
        if close is None:
            close = _safe_float(row.get("close"))
        if not symbol or pd.isna(ts) or close is None:
            continue
        records.append({"date": ts.normalize(), "symbol": symbol, "close": close})
    if not records:
        return pd.DataFrame()
    frame = pd.DataFrame(records).drop_duplicates(subset=["date", "symbol"], keep="last")
    matrix = frame.pivot_table(index="date", columns="symbol", values="close", aggfunc="last")
    return matrix.sort_index()


def _forward_return(matrix: pd.DataFrame, symbol: str, as_of: Any, horizon: int) -> float | None:
    if not isinstance(matrix, pd.DataFrame) or matrix.empty or symbol not in matrix.columns:
        return None
    as_of_ts = pd.to_datetime(as_of, errors="coerce")
    if pd.isna(as_of_ts):
        return None
    as_of_ts = as_of_ts.normalize()
    series = pd.to_numeric(matrix[symbol], errors="coerce").dropna().sort_index()
    if series.empty:
        return None
    index = pd.DatetimeIndex(series.index).sort_values()
    current_pos = int(index.searchsorted(as_of_ts, side="right") - 1)
    if current_pos < 0:
        return None
    future_pos = current_pos + int(horizon)
    if future_pos >= len(index):
        return None
    current = _safe_float(series.iloc[current_pos])
    future = _safe_float(series.iloc[future_pos])
    if current in (None, 0) or future is None:
        return None
    return ((float(future) / float(current)) - 1.0) * 100.0


def _basket_forward_return(
    *,
    futures_matrix: pd.DataFrame,
    proxy_matrix: pd.DataFrame,
    futures_symbols: Sequence[str],
    proxy_symbols: Sequence[str] = (),
    as_of: Any,
    horizon: int,
    invert_futures: bool = False,
    invert_proxy: bool = False,
) -> BasketReturn:
    returns: list[float] = []
    source_kinds: set[str] = set()
    used_symbols: list[str] = []
    for symbol in futures_symbols:
        ret = _forward_return(futures_matrix, symbol, as_of, horizon)
        if ret is not None:
            returns.append(-ret if invert_futures else ret)
            source_kinds.add("futures")
            used_symbols.append(symbol)
            continue
        proxy_symbol = FUTURES_PROXY_MAP.get(symbol)
        if proxy_symbol:
            proxy_ret = _forward_return(proxy_matrix, proxy_symbol, as_of, horizon)
            if proxy_ret is not None:
                returns.append(-proxy_ret if invert_proxy else proxy_ret)
                source_kinds.add("ETF proxy")
                used_symbols.append(proxy_symbol)
    if not returns:
        for symbol in proxy_symbols:
            ret = _forward_return(proxy_matrix, symbol, as_of, horizon)
            if ret is not None:
                returns.append(-ret if invert_proxy else ret)
                source_kinds.add("ETF proxy")
                used_symbols.append(symbol)
    if not returns:
        return BasketReturn(None, "missing", "-")
    if source_kinds == {"futures"}:
        source = "futures"
    elif source_kinds == {"ETF proxy"}:
        source = "ETF proxy"
    else:
        source = "mixed futures / ETF proxy"
    return BasketReturn(sum(returns) / len(returns), source, ", ".join(used_symbols))


def _target_returns_for_date(
    *,
    futures_matrix: pd.DataFrame,
    proxy_matrix: pd.DataFrame,
    as_of: Any,
) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for horizon in VALIDATION_HORIZONS:
        baskets = {
            "Risk Asset": _basket_forward_return(
                futures_matrix=futures_matrix,
                proxy_matrix=proxy_matrix,
                futures_symbols=("ES=F", "NQ=F", "RTY=F"),
                as_of=as_of,
                horizon=horizon,
            ),
            "Growth Asset": _basket_forward_return(
                futures_matrix=futures_matrix,
                proxy_matrix=proxy_matrix,
                futures_symbols=("NQ=F",),
                proxy_symbols=("QQQ",),
                as_of=as_of,
                horizon=horizon,
            ),
            "Safe Haven": _basket_forward_return(
                futures_matrix=futures_matrix,
                proxy_matrix=proxy_matrix,
                futures_symbols=("GC=F", "ZN=F", "ZB=F", "6J=F"),
                proxy_symbols=("GLD", "TLT"),
                as_of=as_of,
                horizon=horizon,
            ),
            "Rates Duration": _basket_forward_return(
                futures_matrix=futures_matrix,
                proxy_matrix=proxy_matrix,
                futures_symbols=("ZN=F", "ZB=F"),
                proxy_symbols=("TLT",),
                as_of=as_of,
                horizon=horizon,
            ),
            "Gold": _basket_forward_return(
                futures_matrix=futures_matrix,
                proxy_matrix=proxy_matrix,
                futures_symbols=("GC=F",),
                proxy_symbols=("GLD",),
                as_of=as_of,
                horizon=horizon,
            ),
            "Dollar": _basket_forward_return(
                futures_matrix=futures_matrix,
                proxy_matrix=proxy_matrix,
                futures_symbols=("6E=F", "6J=F", "6B=F", "6A=F", "6C=F"),
                proxy_symbols=("UUP",),
                as_of=as_of,
                horizon=horizon,
                invert_futures=True,
            ),
        }
        for family, basket in baskets.items():
            prefix = f"{family} {horizon}D"
            out[f"{prefix} %"] = _round(basket.value, 3)
            out[f"{prefix} Source"] = basket.source
            out[f"{prefix} Symbols"] = basket.symbols
    return out


def _score_value_map(scores: pd.DataFrame) -> dict[str, int | None]:
    values: dict[str, int | None] = {}
    if not isinstance(scores, pd.DataFrame) or scores.empty:
        return values
    for _, row in scores.iterrows():
        value = row.get("Value")
        values[str(row.get("Score") or "")] = int(value) if value is not None and not pd.isna(value) else None
    return values


def _scenario_rule(scenario: Any) -> tuple[str | None, int, str]:
    text = str(scenario or "")
    if text in {"좋은 risk-on", "기술주 중심 랠리"}:
        return "Risk Asset", 1, "risk asset forward return > 0"
    if text in {"경기침체 우려 / risk-off", "안전자산 선호 risk-off", "달러 강세 risk-off"}:
        return "Risk Asset", -1, "risk asset forward return < 0"
    if text in {"금리 상승 부담", "인플레이션 쇼크 가능성"}:
        return "Growth Asset", -1, "NQ / QQQ-style growth forward return < 0"
    return None, 0, "mixed scenario; no forced directional hit rule"


def _build_validation_records(
    *,
    candles: pd.DataFrame,
    instruments: Sequence[dict[str, Any]],
    selected_symbols: Sequence[str],
    futures_matrix: pd.DataFrame,
    proxy_matrix: pd.DataFrame,
    min_standardized_symbols: int,
) -> pd.DataFrame:
    if not isinstance(candles, pd.DataFrame) or candles.empty:
        return pd.DataFrame()
    validation_dates = sorted(str(value) for value in candles["Date"].dropna().unique())
    rows: list[dict[str, Any]] = []
    for as_of_date in validation_dates:
        pit_candles = candles[candles["Date"] <= as_of_date]
        symbol_metrics = compute_symbol_metrics(
            pit_candles,
            instruments=instruments,
            selected_symbols=selected_symbols,
        )
        standardized_count = int(symbol_metrics["Std Move"].notna().sum()) if not symbol_metrics.empty else 0
        if standardized_count < max(1, int(min_standardized_symbols)):
            continue
        scores, components = compute_macro_scores(symbol_metrics)
        interpretation = generate_market_interpretation(scores, symbol_metrics)
        values = _score_value_map(scores)
        evidence_groups = build_current_evidence_groups(scores, components, symbol_metrics)
        target_returns = _target_returns_for_date(
            futures_matrix=futures_matrix,
            proxy_matrix=proxy_matrix,
            as_of=as_of_date,
        )
        if not any(target_returns.get(f"{family} {horizon}D %") is not None for family in ("Risk Asset", "Growth Asset", "Safe Haven", "Dollar") for horizon in VALIDATION_HORIZONS):
            continue
        family, direction, hit_rule = _scenario_rule(interpretation.get("scenario"))
        row: dict[str, Any] = {
            "Date": as_of_date,
            "Scenario": interpretation.get("scenario"),
            "Scenario Summary": interpretation.get("summary"),
            "Hit Family": family,
            "Hit Direction": direction,
            "Hit Rule": hit_rule,
            "Standardized Symbols": standardized_count,
            "Strong Evidence Count": int(evidence_groups.get("counts", {}).get("strong") or 0),
            "Weak Evidence Count": int(evidence_groups.get("counts", {}).get("weak") or 0),
            "Missing Symbol Count": int(evidence_groups.get("counts", {}).get("missing") or 0),
            "Conflicting Evidence Count": int(evidence_groups.get("counts", {}).get("conflicting") or 0),
        }
        for score_name, value in values.items():
            row[score_name] = value
        row.update(target_returns)
        rows.append(row)
    return pd.DataFrame(rows)


def _hit_series(group: pd.DataFrame, *, family: str | None, direction: int, horizon: int) -> tuple[pd.Series, pd.Series]:
    if not family or direction == 0:
        return pd.Series(dtype=float), pd.Series(dtype=bool)
    target_col = f"{family} {horizon}D %"
    if target_col not in group.columns:
        return pd.Series(dtype=float), pd.Series(dtype=bool)
    returns = pd.to_numeric(group[target_col], errors="coerce").dropna()
    if returns.empty:
        return returns, pd.Series(dtype=bool)
    aligned = returns * float(direction)
    hits = aligned > 0
    return aligned, hits


def _scenario_summary(records: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(records, pd.DataFrame) or records.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for scenario, group in records.groupby("Scenario", dropna=False):
        family, direction, hit_rule = _scenario_rule(scenario)
        row: dict[str, Any] = {
            "Scenario": scenario,
            "Occurrence Count": int(len(group)),
            "Target Family": family or "Mixed",
            "Hit Rule": hit_rule,
        }
        for horizon in VALIDATION_HORIZONS:
            target_col = f"{family} {horizon}D %" if family else None
            returns = pd.to_numeric(group[target_col], errors="coerce").dropna() if target_col and target_col in group else pd.Series(dtype=float)
            aligned, hits = _hit_series(group, family=family, direction=direction, horizon=horizon)
            row[f"Sample {horizon}D"] = int(len(returns))
            row[f"Mean {horizon}D %"] = _round(float(returns.mean()), 3) if not returns.empty else None
            row[f"Median {horizon}D %"] = _round(float(returns.median()), 3) if not returns.empty else None
            row[f"Hit Rate {horizon}D %"] = _round(float(hits.mean() * 100.0), 1) if len(hits) else None
            row[f"False Positive {horizon}D %"] = _round(float((1.0 - hits.mean()) * 100.0), 1) if len(hits) else None
            row[f"Max Adverse {horizon}D %"] = _round(float(aligned.min()), 3) if not aligned.empty else None
        rows.append(row)
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(["Occurrence Count", "Scenario"], ascending=[False, True]).reset_index(drop=True)


def _threshold_sensitivity(records: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(records, pd.DataFrame) or records.empty:
        return pd.DataFrame()
    specs = [
        ("Risk-On Score", "Risk Asset", 1, -1),
        ("Rate Pressure Score", "Growth Asset", -1, 1),
        ("Dollar Pressure Score", "Risk Asset", -1, 1),
        ("Safe Haven Score", "Safe Haven", 1, -1),
    ]
    rows: list[dict[str, Any]] = []
    for score_name, family, positive_direction, negative_direction in specs:
        if score_name not in records.columns:
            continue
        score_values = pd.to_numeric(records[score_name], errors="coerce")
        for threshold in VALIDATION_THRESHOLDS:
            masks = [
                ("Positive", score_values >= threshold, positive_direction),
                ("Negative", score_values <= -threshold, negative_direction),
            ]
            for direction_label, mask, expected_direction in masks:
                subset = records[mask.fillna(False)]
                for horizon in VALIDATION_HORIZONS:
                    target_col = f"{family} {horizon}D %"
                    returns = pd.to_numeric(subset[target_col], errors="coerce").dropna() if target_col in subset else pd.Series(dtype=float)
                    aligned = returns * float(expected_direction)
                    hits = aligned > 0
                    rows.append(
                        {
                            "Score": score_name,
                            "Threshold": threshold,
                            "Direction": direction_label,
                            "Target Family": family,
                            "Horizon": f"{horizon}D",
                            "Sample": int(len(returns)),
                            "Mean Forward Return %": _round(float(returns.mean()), 3) if not returns.empty else None,
                            "Median Forward Return %": _round(float(returns.median()), 3) if not returns.empty else None,
                            "Hit Rate %": _round(float(hits.mean() * 100.0), 1) if len(hits) else None,
                        }
                    )
    return pd.DataFrame(rows)


def _relationship_summary(records: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(records, pd.DataFrame) or records.empty:
        return pd.DataFrame()
    specs = [
        ("Risk-On Score", "Risk Asset", "positive"),
        ("Rate Pressure Score", "Growth Asset", "negative"),
        ("Dollar Pressure Score", "Risk Asset", "negative"),
        ("Safe Haven Score", "Safe Haven", "positive"),
    ]
    rows: list[dict[str, Any]] = []
    for score_name, family, expected in specs:
        if score_name not in records.columns:
            continue
        for horizon in VALIDATION_HORIZONS:
            target_col = f"{family} {horizon}D %"
            if target_col not in records.columns:
                continue
            subset = records[[score_name, target_col]].apply(pd.to_numeric, errors="coerce").dropna()
            corr = float(subset[score_name].corr(subset[target_col])) if len(subset) >= 3 else None
            rows.append(
                {
                    "Relationship": f"{score_name} vs {family} {horizon}D forward return",
                    "Score": score_name,
                    "Target Family": family,
                    "Horizon": f"{horizon}D",
                    "Expected Direction": expected,
                    "Sample": int(len(subset)),
                    "Correlation": _round(corr, 3) if corr is not None and not pd.isna(corr) else None,
                }
            )
    return pd.DataFrame(rows)


def _coverage(
    *,
    candles: pd.DataFrame,
    proxy_matrix: pd.DataFrame,
    records: pd.DataFrame,
    years: int,
    futures_rows: Sequence[dict[str, Any]],
    proxy_rows: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    candle_dates = pd.to_datetime(candles["Date"], errors="coerce").dropna() if isinstance(candles, pd.DataFrame) and not candles.empty else pd.Series(dtype="datetime64[ns]")
    first_date = candle_dates.min().date().isoformat() if not candle_dates.empty else None
    latest_date = candle_dates.max().date().isoformat() if not candle_dates.empty else None
    span_years = None
    if first_date and latest_date:
        span_years = round((date.fromisoformat(latest_date) - date.fromisoformat(first_date)).days / 365.25, 2)
    proxy_available = list(proxy_matrix.columns) if isinstance(proxy_matrix, pd.DataFrame) and not proxy_matrix.empty else []
    target_sources: list[str] = []
    if isinstance(records, pd.DataFrame) and not records.empty:
        source_columns = [column for column in records.columns if str(column).endswith(" Source")]
        for column in source_columns:
            target_sources.extend(
                str(value)
                for value in records[column].dropna().unique().tolist()
                if str(value).strip() and str(value) != "missing"
            )
    target_sources = sorted(set(target_sources))
    return {
        "requested_years": int(years),
        "minimum_recommended_years": MIN_VALIDATION_YEARS,
        "first_daily_date": first_date,
        "latest_daily_date": latest_date,
        "history_span_years": span_years,
        "futures_raw_rows": len(futures_rows),
        "proxy_raw_rows": len(proxy_rows),
        "proxy_symbols_available": proxy_available,
        "target_sources": target_sources,
        "used_etf_proxy_target": any("ETF proxy" in source for source in target_sources),
        "validation_dates": int(len(records)) if isinstance(records, pd.DataFrame) else 0,
    }


def _status_and_warnings(coverage: dict[str, Any], records: pd.DataFrame) -> tuple[str, list[str]]:
    warnings: list[str] = []
    if int(coverage.get("futures_raw_rows") or 0) <= 0:
        return "MISSING", ["Stored futures daily OHLCV rows are not available for historical validation."]
    if int(coverage.get("validation_dates") or 0) <= 0:
        return "MISSING", ["No point-in-time validation dates had enough score history and forward return targets."]
    span_years = _safe_float(coverage.get("history_span_years"))
    if span_years is None or span_years < MIN_VALIDATION_YEARS:
        warnings.append(f"Historical validation has less than {MIN_VALIDATION_YEARS} years of stored daily futures history.")
    if len(records) < 60:
        warnings.append("Historical validation sample is small; confidence should be downgraded.")
    if coverage.get("used_etf_proxy_target"):
        warnings.append("Some target validation may use ETF proxy rows when futures targets are unavailable.")
    return ("REVIEW" if warnings else "OK"), warnings


def _current_scenario_metrics(summary: pd.DataFrame, current_snapshot: dict[str, Any] | None) -> dict[str, Any]:
    scenario = None
    if current_snapshot:
        scenario = dict(current_snapshot.get("summary") or {}).get("scenario")
    if not scenario or not isinstance(summary, pd.DataFrame) or summary.empty:
        return {}
    matches = summary[summary["Scenario"] == scenario]
    if matches.empty:
        return {"Scenario": scenario, "Occurrence Count": 0}
    return dict(matches.iloc[0])


def build_futures_macro_validation_snapshot(
    *,
    symbols: Sequence[str] | None = None,
    years: int = DEFAULT_VALIDATION_YEARS,
    query_fn: QueryFn | None = None,
    current_snapshot: dict[str, Any] | None = None,
    min_standardized_symbols: int = 8,
) -> dict[str, Any]:
    query = query_fn or _default_query
    selected_symbols = [str(symbol).strip().upper() for symbol in (symbols or DEFAULT_CORE_FUTURES_SYMBOLS) if str(symbol).strip()]
    lookback_days = int(max(1, years) * 366 + MIN_RECOMMENDED_DAYS + max(VALIDATION_HORIZONS))
    futures_rows = _load_validation_futures_rows(query, symbols=selected_symbols, lookback_days=lookback_days)
    proxy_rows = _load_proxy_price_rows(query, symbols=PROXY_TARGET_SYMBOLS, lookback_days=lookback_days)
    candles = normalize_futures_macro_daily_candles(futures_rows)
    instruments = _instrument_rows(query)
    futures_matrix = _matrix_from_futures_candles(candles)
    proxy_matrix = _matrix_from_proxy_rows(proxy_rows)
    records = _build_validation_records(
        candles=candles,
        instruments=instruments,
        selected_symbols=selected_symbols,
        futures_matrix=futures_matrix,
        proxy_matrix=proxy_matrix,
        min_standardized_symbols=min_standardized_symbols,
    )
    scenario_summary = _scenario_summary(records)
    threshold_sensitivity = _threshold_sensitivity(records)
    relationships = _relationship_summary(records)
    coverage = _coverage(
        candles=candles,
        proxy_matrix=proxy_matrix,
        records=records,
        years=years,
        futures_rows=futures_rows,
        proxy_rows=proxy_rows,
    )
    status, warnings = _status_and_warnings(coverage, records)
    current_metrics = _current_scenario_metrics(scenario_summary, current_snapshot)
    return {
        "status": status,
        "coverage": coverage,
        "warnings": warnings,
        "scenario_summary": scenario_summary,
        "threshold_sensitivity": threshold_sensitivity,
        "relationships": relationships,
        "records": records,
        "current_scenario_metrics": current_metrics,
        "caveats": list(VALIDATION_CAVEATS),
        "source_note": "Point-in-time recalculation from stored daily futures OHLCV; ETF rows are used only as labeled proxy targets.",
    }


def _latest_age_days(latest_daily_date: Any) -> int | None:
    if not latest_daily_date:
        return None
    try:
        return (date.today() - date.fromisoformat(str(latest_daily_date))).days
    except ValueError:
        return None


def build_interpretation_confidence(
    current_snapshot: dict[str, Any],
    validation_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    coverage = dict(current_snapshot.get("coverage") or {})
    symbol_count = int(coverage.get("symbol_count") or 0)
    standardized_count = int(coverage.get("standardized_count") or 0)
    min_data_days = int(coverage.get("min_data_days") or 0)
    latest_age = _latest_age_days(coverage.get("latest_daily_date"))
    evidence_groups = dict(current_snapshot.get("evidence_groups") or {})
    evidence_counts = dict(evidence_groups.get("counts") or {})
    validation = validation_snapshot or {}
    current_metrics = dict(validation.get("current_scenario_metrics") or {})
    validation_coverage = dict(validation.get("coverage") or {})

    reasons: list[str] = []
    if standardized_count <= 0 or min_data_days < 61:
        return {
            "label": "Not Enough History",
            "tone": "warning",
            "score": 0,
            "sample_size": int(current_metrics.get("Sample 5D") or current_metrics.get("Occurrence Count") or 0),
            "hit_rate_5d": current_metrics.get("Hit Rate 5D %"),
            "latest_candle_age_days": latest_age,
            "reasons": ["60D volatility or daily history is not sufficient for current symbols."],
            "inputs": {
                "symbol_count": symbol_count,
                "standardized_count": standardized_count,
                "min_data_days": min_data_days,
                "validation_dates": int(validation_coverage.get("validation_dates") or 0),
            },
        }

    score = 0
    coverage_ratio = standardized_count / symbol_count if symbol_count else 0.0
    if coverage_ratio >= 0.9:
        score += 2
        reasons.append("Most core symbols have 60D standardized moves.")
    elif coverage_ratio >= 0.75:
        score += 1
        reasons.append("Most, but not all, core symbols have 60D standardized moves.")
    else:
        score -= 1
        reasons.append("Daily standardized coverage is partial.")

    strong_count = int(evidence_counts.get("strong") or 0)
    weak_count = int(evidence_counts.get("weak") or 0)
    missing_count = int(evidence_counts.get("missing") or 0)
    conflict_count = int(evidence_counts.get("conflicting") or 0)
    if strong_count >= 2:
        score += 1
        reasons.append("Current interpretation has multiple strong standardized components.")
    if weak_count > strong_count:
        score -= 1
        reasons.append("Weak components outnumber strong components.")
    if missing_count:
        score -= 1
        reasons.append(f"{missing_count} current symbols are missing daily rows.")
    if conflict_count >= 2:
        score -= 2
        reasons.append("Multiple score conflicts are present.")
    elif conflict_count == 1:
        score -= 1
        reasons.append("One score conflict is present.")

    if latest_age is None:
        score -= 1
        reasons.append("Latest daily candle age is unknown.")
    elif latest_age <= 3:
        score += 1
        reasons.append("Latest daily candle is recent.")
    elif latest_age >= 7:
        score -= 2
        reasons.append(f"Latest daily candle is {latest_age} days old.")
    else:
        score -= 1
        reasons.append(f"Latest daily candle is {latest_age} days old.")

    validation_dates = int(validation_coverage.get("validation_dates") or 0)
    scenario_sample = int(current_metrics.get("Sample 5D") or current_metrics.get("Occurrence Count") or 0)
    hit_rate = _safe_float(current_metrics.get("Hit Rate 5D %"))
    if validation_dates <= 0:
        score -= 3
        reasons.append("Historical validation has no usable point-in-time records.")
    elif scenario_sample >= 60:
        score += 2
        reasons.append("Current scenario has a useful historical sample.")
    elif scenario_sample >= 30:
        score += 1
        reasons.append("Current scenario has a moderate historical sample.")
    elif scenario_sample >= 10:
        reasons.append("Current scenario has a small historical sample.")
    else:
        score -= 2
        reasons.append("Current scenario historical sample is too small.")

    if hit_rate is not None:
        if hit_rate >= 55:
            score += 1
            reasons.append("Current scenario 5D hit rate is above a basic consistency threshold.")
        elif hit_rate < 45:
            score -= 1
            reasons.append("Current scenario 5D hit rate is below a basic consistency threshold.")
    else:
        reasons.append("Current mixed scenario is not forced into a directional hit-rate rule.")

    if validation_dates < 30 or scenario_sample < 5:
        label = "Not Enough History"
        tone = "warning"
    elif score >= 6:
        label = "High Confidence"
        tone = "positive"
    elif score >= 3:
        label = "Medium Confidence"
        tone = "warning"
    else:
        label = "Low Confidence"
        tone = "danger"

    return {
        "label": label,
        "tone": tone,
        "score": int(score),
        "sample_size": scenario_sample,
        "hit_rate_5d": _round(hit_rate, 1) if hit_rate is not None else None,
        "latest_candle_age_days": latest_age,
        "reasons": reasons[:8],
        "inputs": {
            "symbol_count": symbol_count,
            "standardized_count": standardized_count,
            "min_data_days": min_data_days,
            "strong_evidence_count": strong_count,
            "weak_evidence_count": weak_count,
            "missing_symbol_count": missing_count,
            "conflicting_score_count": conflict_count,
            "validation_dates": validation_dates,
            "history_span_years": validation_coverage.get("history_span_years"),
        },
    }
