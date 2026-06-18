from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

import pandas as pd

from finance.loaders.futures import load_futures_ohlcv
from finance.loaders.price import load_price_history


DEFAULT_COMPARISON_SYMBOLS = ("SPY", "QQQ", "TLT", "GLD", "IWM", "HYG", "LQD")
DEFAULT_HORIZONS = (5, 20, 60)
DEFAULT_MIN_HISTORY_ROWS = 756
DEFAULT_MIN_SAMPLE_COUNT = 8
DEFAULT_MIN_ANCHOR_GAP = 20
DEFAULT_RELATIVE_STRENGTH_FLOOR = 0.01
DEFAULT_RELATIVE_STRENGTH_RATIO = 0.5
DEFAULT_PATTERN_WINDOW = "5D"
DEFAULT_GLD_CONTEXT_THRESHOLD = 0.01
DEFAULT_FUTURES_CONTEXT_THRESHOLD = 0.005
DEFAULT_FUTURES_RATE_PRESSURE_SYMBOLS = ("ZN=F", "ZB=F")
PATTERN_WINDOW_SPECS: dict[str, dict[str, Any]] = {
    "5D": {"days": 5, "label": "5D", "group_period": "weekly"},
    "20D": {"days": 20, "label": "20D", "group_period": "monthly"},
    "MONTHLY": {"days": 21, "label": "Monthly", "group_period": "monthly"},
}


_SECTOR_PROXY_ROWS: tuple[dict[str, Any], ...] = (
    {
        "sector": "Communication Services",
        "symbol": "XLC",
        "aliases": ("communication services", "communications", "communication service"),
    },
    {
        "sector": "Consumer Discretionary",
        "symbol": "XLY",
        "aliases": ("consumer discretionary", "consumer cyclical", "cyclical"),
    },
    {
        "sector": "Consumer Staples",
        "symbol": "XLP",
        "aliases": ("consumer staples", "consumer defensive", "defensive", "staples"),
    },
    {
        "sector": "Energy",
        "symbol": "XLE",
        "aliases": ("energy",),
    },
    {
        "sector": "Financials",
        "symbol": "XLF",
        "aliases": ("financials", "financial services", "finance"),
    },
    {
        "sector": "Health Care",
        "symbol": "XLV",
        "aliases": ("health care", "healthcare", "health"),
    },
    {
        "sector": "Industrials",
        "symbol": "XLI",
        "aliases": ("industrials", "industrial"),
    },
    {
        "sector": "Materials",
        "symbol": "XLB",
        "aliases": ("materials", "basic materials"),
    },
    {
        "sector": "Real Estate",
        "symbol": "XLRE",
        "aliases": ("real estate", "realestate"),
    },
    {
        "sector": "Technology",
        "symbol": "XLK",
        "aliases": ("technology", "information technology", "tech"),
    },
    {
        "sector": "Utilities",
        "symbol": "XLU",
        "aliases": ("utilities", "utility"),
    },
)


def _normalize_label(value: Any) -> str:
    text = str(value or "").strip().lower().replace("&", " and ")
    normalized = "".join(char if char.isalnum() else " " for char in text)
    return " ".join(normalized.split())


def _format_date(value: Any) -> str | None:
    if value is None or value == "":
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.date().isoformat()


def _format_pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{value * 100:+.1f}%"


def _condition_item(
    *,
    condition_id: str,
    label: str,
    status: str,
    detail: str,
    status_label: str,
) -> dict[str, Any]:
    return {
        "id": condition_id,
        "label": label,
        "status": status,
        "status_label": status_label,
        "detail": detail,
    }


def _macro_pilot_excluded_conditions() -> list[dict[str, Any]]:
    return [
        _condition_item(
            condition_id="fred_rates",
            label="2Y / 10Y FRED rates context",
            status="DISABLED",
            status_label="사용 안 함",
            detail="3차-B에서는 새 FRED series 수집, provider fetch, UI 직접 fetch를 하지 않습니다.",
        ),
        _condition_item(
            condition_id="events_sentiment",
            label="Events / sentiment historical conditioning",
            status="DISABLED",
            status_label="이번 차수 제외",
            detail="events / sentiment 조건화는 3차-B pilot 범위 밖입니다.",
        ),
    ]


def _sample_quality(status: str, *, sample_count: int, broad_sample_count: int, min_sample_count: int) -> dict[str, Any]:
    normalized = str(status or "").upper()
    if normalized == "OK":
        return {
            "status": "OK",
            "label": "pilot sample usable",
            "detail": f"Broad {broad_sample_count}회 중 Macro 조건 포함 {sample_count}회가 남아 최소 표본 {min_sample_count}회를 충족합니다.",
        }
    if sample_count > 0:
        return {
            "status": "REVIEW",
            "label": "pilot-limited",
            "detail": f"Broad {broad_sample_count}회 중 Macro 조건 포함 {sample_count}회만 남아 broad 결과와 함께 읽어야 합니다.",
        }
    if normalized == "DISABLED":
        return {
            "status": "DISABLED",
            "label": "disabled",
            "detail": "필수 조건이 계산되지 않아 Macro 조건 포함 pilot을 계산하지 않았습니다.",
        }
    return {
        "status": "INSUFFICIENT_CONTEXT",
        "label": "insufficient context",
        "detail": "추가 macro 조건을 계산할 수 없거나 조건을 통과한 anchor가 없습니다.",
    }


def _macro_conditioned_disabled_model(
    *,
    status: str,
    headline: str,
    detail: str,
    used_conditions: list[dict[str, Any]] | None = None,
    insufficient_conditions: list[dict[str, Any]] | None = None,
    broad_sample_count: int = 0,
) -> dict[str, Any]:
    return {
        "schema_version": "overview_market_context_macro_conditioned_analog_pilot_v1",
        "status": status,
        "status_label": "조건 부족" if status == "INSUFFICIENT_CONTEXT" else "비활성",
        "headline": headline,
        "detail": detail,
        "condition_summary": detail,
        "broad_sample_count": int(broad_sample_count),
        "sample_count": 0,
        "additional_condition_count": 0,
        "sample_reduction_reason": detail,
        "sample_quality": _sample_quality(status, sample_count=0, broad_sample_count=int(broad_sample_count), min_sample_count=1),
        "used_conditions": used_conditions or [],
        "insufficient_conditions": insufficient_conditions or [],
        "excluded_conditions": _macro_pilot_excluded_conditions(),
        "coverage_gaps": [],
        "rows": [],
        "anchor_dates": [],
    }


def _gld_context_bucket(value: float | None, *, threshold: float = DEFAULT_GLD_CONTEXT_THRESHOLD) -> dict[str, str] | None:
    if value is None or pd.isna(value):
        return None
    if float(value) >= threshold:
        return {"key": "gold_bid", "label": "GLD 상승 context"}
    if float(value) <= -threshold:
        return {"key": "gold_fading", "label": "GLD 하락 context"}
    return {"key": "gold_mixed", "label": "GLD 중립권 context"}


def _normalize_pattern_window(value: str | None) -> dict[str, Any]:
    normalized = str(value or DEFAULT_PATTERN_WINDOW).strip().upper().replace(" ", "")
    if normalized in {"1M", "MONTH", "MONTHLY"}:
        normalized = "MONTHLY"
    if normalized not in PATTERN_WINDOW_SPECS:
        normalized = DEFAULT_PATTERN_WINDOW
    spec = dict(PATTERN_WINDOW_SPECS[normalized])
    spec["key"] = normalized
    return spec


def historical_analog_pattern_window_options() -> tuple[dict[str, Any], ...]:
    return tuple({"key": key, **value} for key, value in PATTERN_WINDOW_SPECS.items())


def _default_limitations() -> list[str]:
    return [
        "과거 통계는 미래 움직임 보장이 아님",
        "sector ETF proxy 사용",
        "sample이 적으면 신뢰 낮음",
        "survivorship/PIT 한계",
        "transaction cost/slippage 미반영",
    ]


def _base_model(
    *,
    status: str,
    headline: str,
    detail: str,
    leadership_sector: str | None = None,
    proxy_etf: str | None = None,
    coverage: list[dict[str, Any]] | None = None,
    coverage_gaps: list[dict[str, Any]] | None = None,
    repair_action: dict[str, Any] | None = None,
    as_of_date: str | None = None,
    pattern_window: str | None = None,
) -> dict[str, Any]:
    current_as_of = _coverage_current_as_of(coverage or [])
    pattern = _normalize_pattern_window(pattern_window)
    return {
        "schema_version": "overview_market_context_historical_analog_v2",
        "status": status,
        "headline": headline,
        "detail": detail,
        "leadership_sector": leadership_sector,
        "proxy_etf": proxy_etf,
        "sample_count": 0,
        "condition_summary": "",
        "data_window": "",
        "current_as_of": current_as_of,
        "requested_as_of": as_of_date or "latest",
        "as_of_mode": "selected" if as_of_date else "latest",
        "pattern_window": pattern["key"],
        "pattern_window_label": pattern["label"],
        "pattern_window_days": pattern["days"],
        "calculation_note": f"선택한 기준 시점의 sector ETF SPY 대비 {pattern['label']} 상대강도 기준",
        "leadership_replay_basis": "current universe/sector metadata + DB prices through the selected as-of date",
        "coverage": coverage or [],
        "coverage_gaps": coverage_gaps or [],
        "repair_action": repair_action or {},
        "rows": [],
        "anchor_dates": [],
        "macro_conditioned_analog": _macro_conditioned_disabled_model(
            status="INSUFFICIENT_CONTEXT",
            headline="Macro 조건 포함 pilot 조건 부족",
            detail="Broad historical analog의 sector ETF / SPY 조건이 먼저 계산되어야 합니다.",
            insufficient_conditions=[
                _condition_item(
                    condition_id="sector_relative_strength",
                    label="Sector ETF vs SPY relative strength",
                    status="INSUFFICIENT_CONTEXT",
                    status_label="조건 부족",
                    detail="리더십 sector proxy 또는 가격 이력이 부족해 필수 broad 조건을 계산하지 못했습니다.",
                )
            ],
        ),
        "limitations": _default_limitations(),
        "boundary_note": (
            "Overview context-only 참고 정보입니다. Backtest strategy, validation gate, "
            "Final Review decision, Operations monitoring으로 연결하지 않습니다."
        ),
    }


def sector_etf_proxy_map() -> dict[str, dict[str, Any]]:
    """Return the GICS sector to representative ETF proxy map used by Overview analog context."""
    return {
        row["sector"]: {
            "sector": row["sector"],
            "symbol": row["symbol"],
            "aliases": tuple(row["aliases"]),
        }
        for row in _SECTOR_PROXY_ROWS
    }


def resolve_sector_etf_proxy(sector_label: Any) -> dict[str, Any] | None:
    normalized = _normalize_label(sector_label)
    if not normalized:
        return None
    for row in _SECTOR_PROXY_ROWS:
        if normalized == _normalize_label(row["sector"]):
            return {
                "sector": row["sector"],
                "symbol": row["symbol"],
                "matched_label": str(sector_label or ""),
            }
        if normalized in {_normalize_label(alias) for alias in row["aliases"]}:
            return {
                "sector": row["sector"],
                "symbol": row["symbol"],
                "matched_label": str(sector_label or ""),
            }
    return None


def _leadership_rows(group_leadership_snapshot: dict[str, Any] | None) -> pd.DataFrame:
    if not group_leadership_snapshot:
        return pd.DataFrame()
    rows = group_leadership_snapshot.get("rows")
    if isinstance(rows, pd.DataFrame):
        return rows.copy()
    if isinstance(rows, list):
        return pd.DataFrame(rows)
    return pd.DataFrame()


def resolve_leadership_sector_proxy(group_leadership_snapshot: dict[str, Any] | None) -> dict[str, Any]:
    rows = _leadership_rows(group_leadership_snapshot)
    if rows.empty:
        return {
            "status": "INSUFFICIENT_DATA",
            "leadership_sector": None,
            "proxy_etf": None,
            "detail": "Current sector leadership rows are unavailable.",
        }
    top = rows.iloc[0].to_dict()
    label = top.get("Group") or top.get("Sector") or top.get("sector")
    proxy = resolve_sector_etf_proxy(label)
    if proxy is None:
        return {
            "status": "INSUFFICIENT_DATA",
            "leadership_sector": str(label or "Unknown"),
            "proxy_etf": None,
            "detail": "Current leadership sector does not map to a sector ETF proxy.",
        }
    return {
        "status": "OK",
        "leadership_sector": str(label or proxy["sector"]),
        "canonical_sector": proxy["sector"],
        "proxy_etf": proxy["symbol"],
        "rank": int(top.get("Rank") or 1),
        "detail": f"{label} leadership maps to {proxy['symbol']}.",
    }


def _price_column(frame: pd.DataFrame) -> pd.Series:
    if "adj_close" in frame.columns and "close" in frame.columns:
        adj_close = pd.to_numeric(frame["adj_close"], errors="coerce")
        close = pd.to_numeric(frame["close"], errors="coerce")
        return adj_close.fillna(close)
    if "adj_close" in frame.columns:
        return pd.to_numeric(frame["adj_close"], errors="coerce")
    if "close" in frame.columns:
        return pd.to_numeric(frame["close"], errors="coerce")
    if "price" in frame.columns:
        return pd.to_numeric(frame["price"], errors="coerce")
    return pd.Series([None] * len(frame), index=frame.index, dtype="float64")


def _normalize_price_history(price_history: pd.DataFrame | None) -> pd.DataFrame:
    if price_history is None or price_history.empty:
        return pd.DataFrame(columns=["symbol", "date", "price"])
    frame = price_history.copy()
    if "symbol" not in frame.columns or "date" not in frame.columns:
        return pd.DataFrame(columns=["symbol", "date", "price"])
    frame["symbol"] = frame["symbol"].astype(str).str.upper()
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame["price"] = _price_column(frame)
    frame = frame.dropna(subset=["symbol", "date", "price"])
    frame = frame[frame["price"] > 0]
    return frame[["symbol", "date", "price"]].sort_values(["symbol", "date"])


def _filter_price_history_as_of(frame: pd.DataFrame, end_date: str | None) -> pd.DataFrame:
    if frame.empty or not end_date:
        return frame
    end_ts = pd.to_datetime(end_date, errors="coerce")
    if pd.isna(end_ts):
        return frame
    return frame[frame["date"] <= end_ts.normalize()]


def _normalize_futures_history(futures_history: pd.DataFrame | None) -> pd.DataFrame:
    if futures_history is None or futures_history.empty:
        return pd.DataFrame(columns=["symbol", "date", "close"])
    frame = futures_history.copy()
    if "provider_symbol" not in frame.columns or "candle_time_utc" not in frame.columns or "close" not in frame.columns:
        return pd.DataFrame(columns=["symbol", "date", "close"])
    if "interval_code" in frame.columns:
        frame = frame[frame["interval_code"].astype(str).str.lower() == "1d"]
    frame["symbol"] = frame["provider_symbol"].astype(str).str.upper()
    timestamps = pd.to_datetime(frame["candle_time_utc"], errors="coerce", utc=True)
    frame["date"] = timestamps.dt.tz_convert(None).dt.normalize()
    frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
    frame = frame.dropna(subset=["symbol", "date", "close"])
    frame = frame[frame["close"] > 0]
    if frame.empty:
        return pd.DataFrame(columns=["symbol", "date", "close"])
    return frame[["symbol", "date", "close"]].sort_values(["symbol", "date"]).drop_duplicates(["symbol", "date"], keep="last")


def _rate_pressure_members() -> dict[str, float]:
    try:
        from app.services.futures_macro_thermometer import SCORE_DEFINITIONS

        for definition in SCORE_DEFINITIONS:
            if definition.name == "Rate Pressure Score":
                return {str(symbol).upper(): float(weight) for symbol, weight in definition.members.items()}
    except Exception:  # pragma: no cover - defensive fallback around optional service import
        pass
    return {"ZN=F": -1.0, "ZB=F": -1.0}


def _futures_rate_pressure_bucket(
    futures_history: pd.DataFrame,
    *,
    as_of_date: Any,
    pattern_days: int,
    pattern_label: str,
    threshold: float = DEFAULT_FUTURES_CONTEXT_THRESHOLD,
) -> dict[str, Any] | None:
    frame = _normalize_futures_history(futures_history)
    as_of_ts = pd.to_datetime(as_of_date, errors="coerce")
    if frame.empty or pd.isna(as_of_ts):
        return None
    as_of_ts = as_of_ts.normalize()
    members = _rate_pressure_members()
    signed_values: list[float] = []
    used_symbols: list[str] = []
    latest_dates: list[str] = []
    for symbol, signed_weight in members.items():
        symbol_rows = frame[(frame["symbol"] == symbol) & (frame["date"] <= as_of_ts)].sort_values("date")
        if len(symbol_rows) <= pattern_days:
            continue
        latest = float(symbol_rows.iloc[-1]["close"])
        base = float(symbol_rows.iloc[-(pattern_days + 1)]["close"])
        if base <= 0:
            continue
        raw_return = latest / base - 1.0
        signed_values.append(raw_return * (1.0 if signed_weight >= 0 else -1.0))
        used_symbols.append(symbol)
        latest_dates.append(_format_date(symbol_rows.iloc[-1]["date"]) or "")
    if not signed_values:
        return None
    signed_average = float(pd.Series(signed_values, dtype="float64").mean())
    if signed_average >= threshold:
        key = "rate_pressure_up"
        label = "Rate pressure up"
    elif signed_average <= -threshold:
        key = "rate_pressure_easing"
        label = "Rate pressure easing"
    else:
        key = "rates_mixed"
        label = "Rates mixed"
    used_label = "/".join(used_symbols)
    latest_date = max(date for date in latest_dates if date) if any(latest_dates) else _format_date(as_of_ts)
    return {
        "key": key,
        "label": label,
        "signed_return": signed_average,
        "used_symbols": used_symbols,
        "used_label": used_label,
        "latest_date": latest_date,
        "detail": (
            f"{used_label} {pattern_label} futures proxy {_format_pct(signed_average)}; "
            f"{label}; stored daily OHLCV through {latest_date}"
        ),
    }


def summarize_price_coverage(
    price_history: pd.DataFrame | None,
    *,
    symbols: Iterable[str],
    min_rows: int = DEFAULT_MIN_HISTORY_ROWS,
    end_date: str | None = None,
) -> list[dict[str, Any]]:
    frame = _filter_price_history_as_of(_normalize_price_history(price_history), end_date)
    requested = [str(symbol).upper() for symbol in symbols if str(symbol or "").strip()]
    rows: list[dict[str, Any]] = []
    for symbol in dict.fromkeys(requested):
        symbol_rows = frame[frame["symbol"] == symbol]
        row_count = int(symbol_rows["date"].nunique()) if not symbol_rows.empty else 0
        start_date = _format_date(symbol_rows["date"].min()) if row_count else None
        end_date = _format_date(symbol_rows["date"].max()) if row_count else None
        status = "OK" if row_count >= min_rows else "INSUFFICIENT_DATA"
        rows.append(
            {
                "symbol": symbol,
                "status": status,
                "start_date": start_date,
                "end_date": end_date,
                "row_count": row_count,
                "min_rows": int(min_rows),
                "detail": (
                    f"{row_count} rows from {start_date} to {end_date}"
                    if row_count
                    else "No DB price rows available"
                ),
            }
        )
    return rows


def _coverage_gap_rows(coverage: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    for row in coverage:
        if str(row.get("status") or "") == "OK":
            continue
        symbol = str(row.get("symbol") or "").strip().upper()
        if not symbol:
            continue
        gaps.append(
            {
                "symbol": symbol,
                "row_count": int(row.get("row_count") or 0),
                "min_rows": int(row.get("min_rows") or DEFAULT_MIN_HISTORY_ROWS),
                "start_date": row.get("start_date"),
                "end_date": row.get("end_date"),
                "detail": row.get("detail") or "",
            }
        )
    return gaps


def _coverage_current_as_of(coverage: Sequence[dict[str, Any]]) -> str:
    dates = [
        parsed
        for row in coverage
        if isinstance(row, dict)
        for parsed in [_format_date(row.get("end_date"))]
        if parsed
    ]
    return max(dates) if dates else ""


def _coverage_repair_action(coverage_gaps: Sequence[dict[str, Any]]) -> dict[str, Any]:
    symbols = list(dict.fromkeys(str(row.get("symbol") or "").strip().upper() for row in coverage_gaps))
    symbols = [symbol for symbol in symbols if symbol]
    if not symbols:
        return {}
    return {
        "label": "부족 ETF 가격 이력 보강",
        "symbols": symbols,
        "period": "10y",
        "interval": "1d",
        "target_table": "finance_price.nyse_price_history",
        "source": "yfinance OHLCV",
        "action": "overview_historical_analog_ohlcv",
    }


def _price_matrix(
    price_history: pd.DataFrame | None,
    symbols: Sequence[str],
    *,
    end_date: str | None = None,
) -> pd.DataFrame:
    frame = _filter_price_history_as_of(_normalize_price_history(price_history), end_date)
    if frame.empty:
        return pd.DataFrame()
    frame = frame[frame["symbol"].isin(set(symbols))]
    if frame.empty:
        return pd.DataFrame()
    matrix = frame.pivot_table(index="date", columns="symbol", values="price", aggfunc="last").sort_index()
    matrix.columns.name = None
    return matrix


def _period_return(series: pd.Series, index: int, periods: int) -> float | None:
    base_index = index - periods
    if base_index < 0 or index >= len(series):
        return None
    base = series.iloc[base_index]
    current = series.iloc[index]
    if pd.isna(base) or pd.isna(current) or float(base) <= 0:
        return None
    return float(current) / float(base) - 1.0


def _forward_return(series: pd.Series, index: int, horizon: int) -> float | None:
    target_index = index + horizon
    if target_index >= len(series):
        return None
    base = series.iloc[index]
    target = series.iloc[target_index]
    if pd.isna(base) or pd.isna(target) or float(base) <= 0:
        return None
    return float(target) / float(base) - 1.0


def _dedupe_anchor_indices(indices: list[int], *, min_gap: int) -> list[int]:
    selected: list[int] = []
    for index in indices:
        if not selected or index - selected[-1] >= min_gap:
            selected.append(index)
    return selected


def _summary_row(asset: str, horizon: int, values: list[float]) -> dict[str, Any] | None:
    if not values:
        return None
    series = pd.Series(values, dtype="float64")
    return {
        "asset": asset,
        "horizon": f"{horizon}D",
        "median_return_pct": round(float(series.median()) * 100.0, 2),
        "positive_rate_pct": round(float((series > 0).mean()) * 100.0, 2),
        "best_return_pct": round(float(series.max()) * 100.0, 2),
        "worst_return_pct": round(float(series.min()) * 100.0, 2),
        "sample_count": int(series.count()),
    }


def _distribution_rows_for_anchors(
    analysis_matrix: pd.DataFrame,
    *,
    symbols: Sequence[str],
    horizons: Sequence[int],
    anchor_indices: Sequence[int],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    assets = [symbol for symbol in symbols if symbol in analysis_matrix.columns]
    for asset in assets:
        series = analysis_matrix[asset]
        for horizon in horizons:
            values = [
                value
                for anchor in anchor_indices
                if (value := _forward_return(series, anchor, int(horizon))) is not None
            ]
            row = _summary_row(asset, int(horizon), values)
            if row is not None:
                rows.append(row)
    return rows


def _macro_conditioned_pilot_model(
    *,
    analysis_matrix: pd.DataFrame,
    symbols: Sequence[str],
    horizons: Sequence[int],
    anchor_indices: Sequence[int],
    pattern_days: int,
    pattern_label: str,
    proxy_etf: str,
    broad_condition_summary: str,
    coverage_by_symbol: dict[str, dict[str, Any]],
    min_sample_count: int,
    futures_history: pd.DataFrame | None = None,
    futures_as_of_date: str | None = None,
    futures_load_error: str | None = None,
) -> dict[str, Any]:
    broad_sample_count = len(anchor_indices)
    sector_condition = _condition_item(
        condition_id="sector_relative_strength",
        label="Sector ETF vs SPY relative strength",
        status="USED",
        status_label="사용",
        detail=broad_condition_summary,
    )
    gld_coverage = coverage_by_symbol.get("GLD")
    if "GLD" not in analysis_matrix.columns or not gld_coverage or gld_coverage.get("status") != "OK":
        detail = (
            "GLD price proxy 가격 이력이 부족해 Macro 조건 포함 pilot은 계산하지 않고 "
            "기존 broad 결과를 그대로 표시합니다."
        )
        gld_detail = "GLD price rows unavailable"
        if gld_coverage:
            gld_detail = (
                f"GLD {gld_coverage.get('row_count') or 0} / {gld_coverage.get('min_rows') or DEFAULT_MIN_HISTORY_ROWS} rows "
                f"({gld_coverage.get('start_date') or '-'} ~ {gld_coverage.get('end_date') or '-'})"
            )
        model = _macro_conditioned_disabled_model(
            status="INSUFFICIENT_CONTEXT",
            headline="Macro 조건 포함 pilot 조건 부족",
            detail=detail,
            used_conditions=[sector_condition],
            insufficient_conditions=[
                _condition_item(
                    condition_id="gld_safe_haven_context",
                    label="GLD price proxy safe-haven / gold context",
                    status="INSUFFICIENT_CONTEXT",
                    status_label="조건 부족",
                    detail=gld_detail,
                )
            ],
            broad_sample_count=broad_sample_count,
        )
        if gld_coverage and gld_coverage.get("status") != "OK":
            model["coverage_gaps"] = [
                {
                    "symbol": "GLD",
                    "row_count": int(gld_coverage.get("row_count") or 0),
                    "min_rows": int(gld_coverage.get("min_rows") or DEFAULT_MIN_HISTORY_ROWS),
                    "start_date": gld_coverage.get("start_date"),
                    "end_date": gld_coverage.get("end_date"),
                    "detail": gld_coverage.get("detail") or "",
                }
            ]
        return model

    latest_index = len(analysis_matrix) - 1
    gld_series = analysis_matrix["GLD"]
    current_gld_return = _period_return(gld_series, latest_index, pattern_days)
    current_bucket = _gld_context_bucket(current_gld_return)
    if current_bucket is None:
        return _macro_conditioned_disabled_model(
            status="INSUFFICIENT_CONTEXT",
            headline="Macro 조건 포함 pilot 조건 부족",
            detail=f"GLD {pattern_label} context 계산 구간이 부족합니다.",
            used_conditions=[sector_condition],
            insufficient_conditions=[
                _condition_item(
                    condition_id="gld_safe_haven_context",
                    label="GLD price proxy safe-haven / gold context",
                    status="INSUFFICIENT_CONTEXT",
                    status_label="조건 부족",
                    detail=f"GLD {pattern_label} return unavailable",
                )
            ],
            broad_sample_count=broad_sample_count,
        )

    gld_conditioned_anchor_indices: list[int] = []
    for anchor in anchor_indices:
        anchor_gld_return = _period_return(gld_series, int(anchor), pattern_days)
        anchor_bucket = _gld_context_bucket(anchor_gld_return)
        if anchor_bucket and anchor_bucket["key"] == current_bucket["key"]:
            gld_conditioned_anchor_indices.append(int(anchor))

    conditioned_anchor_indices = list(gld_conditioned_anchor_indices)
    used_conditions = [
        sector_condition,
        _condition_item(
            condition_id="gld_safe_haven_context",
            label="GLD price proxy safe-haven / gold context",
            status="USED",
            status_label="사용",
            detail=(
                f"현재 GLD {pattern_label} return {_format_pct(current_gld_return)}; "
                f"{current_bucket['label']}와 같은 anchor만 사용"
            ),
        ),
    ]
    insufficient_conditions: list[dict[str, Any]] = []
    additional_condition_count = 1
    futures_condition_clause = ""
    futures_condition_detail = ""
    current_futures_bucket = _futures_rate_pressure_bucket(
        futures_history if futures_history is not None else pd.DataFrame(),
        as_of_date=futures_as_of_date or analysis_matrix.index[-1],
        pattern_days=pattern_days,
        pattern_label=pattern_label,
    )
    if current_futures_bucket is None:
        detail = (
            f"{'/'.join(DEFAULT_FUTURES_RATE_PRESSURE_SYMBOLS)} stored futures daily OHLCV "
            f"{pattern_label} rows are insufficient through {futures_as_of_date or _format_date(analysis_matrix.index[-1]) or '-'}."
        )
        if futures_load_error:
            detail = f"{detail} DB read failed: {futures_load_error}"
        insufficient_conditions.append(
            _condition_item(
                condition_id="futures_rate_pressure_context",
                label="Rate Pressure futures proxy (ZN=F/ZB=F)",
                status="INSUFFICIENT_CONTEXT",
                status_label="조건 부족",
                detail=detail,
            )
        )
    else:
        futures_matched_anchor_indices: list[int] = []
        futures_bucket_count = 0
        for anchor in gld_conditioned_anchor_indices:
            anchor_bucket = _futures_rate_pressure_bucket(
                futures_history if futures_history is not None else pd.DataFrame(),
                as_of_date=analysis_matrix.index[int(anchor)],
                pattern_days=pattern_days,
                pattern_label=pattern_label,
            )
            if anchor_bucket is None:
                continue
            futures_bucket_count += 1
            if anchor_bucket["key"] == current_futures_bucket["key"]:
                futures_matched_anchor_indices.append(int(anchor))
        if futures_bucket_count <= 0:
            insufficient_conditions.append(
                _condition_item(
                    condition_id="futures_rate_pressure_context",
                    label="Rate Pressure futures proxy (ZN=F/ZB=F)",
                    status="INSUFFICIENT_CONTEXT",
                    status_label="조건 부족",
                    detail=(
                        f"Current {current_futures_bucket['detail']}; anchor-date futures buckets are unavailable "
                        f"for GLD-conditioned anchors."
                    ),
                )
            )
        else:
            conditioned_anchor_indices = futures_matched_anchor_indices
            additional_condition_count = 2
            futures_condition_detail = (
                f"{current_futures_bucket['detail']}; anchor buckets computed "
                f"{futures_bucket_count}/{len(gld_conditioned_anchor_indices)}"
            )
            used_conditions.append(
                _condition_item(
                    condition_id="futures_rate_pressure_context",
                    label="Rate Pressure futures proxy (ZN=F/ZB=F)",
                    status="USED",
                    status_label="사용",
                    detail=futures_condition_detail,
                )
            )
            futures_condition_clause = (
                f" + Rate Pressure futures proxy {current_futures_bucket['label']} "
                f"({current_futures_bucket['used_label']} {pattern_label} {_format_pct(current_futures_bucket['signed_return'])})"
            )

    rows = _distribution_rows_for_anchors(
        analysis_matrix,
        symbols=symbols,
        horizons=horizons,
        anchor_indices=conditioned_anchor_indices,
    )
    sample_count = len(conditioned_anchor_indices)
    status = "OK" if sample_count >= min_sample_count else ("REVIEW" if sample_count > 0 else "INSUFFICIENT_CONTEXT")
    status_label = "자료 정상" if status == "OK" else ("pilot 표본 좁음" if status == "REVIEW" else "조건 부족")
    gld_detail = (
        f"현재 GLD {pattern_label} return {_format_pct(current_gld_return)}; "
        f"{current_bucket['label']}와 같은 anchor만 사용"
    )
    sample_reduction_reason = (
        f"Broad {broad_sample_count}회 중 Macro 조건 포함 {sample_count}회만 남았습니다. "
        f"추가 조건은 {gld_detail}"
        f"{'; futures proxy ' + futures_condition_detail if futures_condition_detail else ''}입니다."
    )
    if insufficient_conditions:
        sample_reduction_reason = (
            f"{sample_reduction_reason} "
            f"{insufficient_conditions[0]['label']}은 조건 부족으로 이번 표본 축소에 사용하지 않았습니다."
        )
    return {
        "schema_version": "overview_market_context_macro_conditioned_analog_pilot_v1",
        "status": status,
        "status_label": status_label,
        "headline": f"Macro 조건 포함 pilot 표본 {sample_count}회",
        "detail": f"기존 broad analog {broad_sample_count}회 중 추가 macro context까지 맞는 {sample_count}회만 별도로 봅니다.",
        "condition_summary": (
            f"{proxy_etf} relative strength + GLD {pattern_label} context "
            f"{current_bucket['label']} ({_format_pct(current_gld_return)}){futures_condition_clause}"
        ),
        "broad_sample_count": broad_sample_count,
        "sample_count": sample_count,
        "additional_condition_count": additional_condition_count,
        "sample_reduction_reason": sample_reduction_reason,
        "sample_quality": _sample_quality(
            status,
            sample_count=sample_count,
            broad_sample_count=broad_sample_count,
            min_sample_count=min_sample_count,
        ),
        "used_conditions": used_conditions,
        "insufficient_conditions": insufficient_conditions,
        "excluded_conditions": _macro_pilot_excluded_conditions(),
        "coverage_gaps": [],
        "rows": rows,
        "anchor_dates": [
            date_value
            for index in conditioned_anchor_indices
            for date_value in [_format_date(analysis_matrix.index[index])]
            if date_value
        ],
    }


def _load_default_price_history(symbols: Sequence[str]) -> pd.DataFrame:
    return load_price_history(symbols=symbols, timeframe="1d")


def _load_default_price_history_as_of(symbols: Sequence[str], end_date: str | None) -> pd.DataFrame:
    return load_price_history(symbols=symbols, timeframe="1d", end=end_date)


def _load_default_futures_ohlcv_as_of(symbols: Sequence[str], end_date: str | None) -> pd.DataFrame:
    return load_futures_ohlcv(symbols=symbols, interval_code="1d", end=end_date)


def build_historical_analog_snapshot(
    *,
    group_leadership_snapshot: dict[str, Any] | None,
    price_history: pd.DataFrame | None = None,
    comparison_symbols: Sequence[str] = DEFAULT_COMPARISON_SYMBOLS,
    horizons: Sequence[int] = DEFAULT_HORIZONS,
    as_of_date: str | None = None,
    pattern_window: str | None = DEFAULT_PATTERN_WINDOW,
    min_history_rows: int = DEFAULT_MIN_HISTORY_ROWS,
    min_sample_count: int = DEFAULT_MIN_SAMPLE_COUNT,
    min_anchor_gap: int = DEFAULT_MIN_ANCHOR_GAP,
    relative_strength_floor: float = DEFAULT_RELATIVE_STRENGTH_FLOOR,
    relative_strength_ratio: float = DEFAULT_RELATIVE_STRENGTH_RATIO,
    futures_history: pd.DataFrame | None = None,
) -> dict[str, Any]:
    pattern = _normalize_pattern_window(pattern_window)
    pattern_days = int(pattern["days"])
    pattern_label = str(pattern["label"])
    normalized_as_of = _format_date(as_of_date)
    leadership = resolve_leadership_sector_proxy(group_leadership_snapshot)
    leadership_sector = leadership.get("leadership_sector")
    proxy_etf = leadership.get("proxy_etf")
    if not proxy_etf:
        return _base_model(
            status="INSUFFICIENT_DATA",
            headline="과거 유사 맥락 자료 부족",
            detail=str(leadership.get("detail") or "Current sector leadership proxy is unavailable."),
            leadership_sector=leadership_sector,
            proxy_etf=None,
            as_of_date=normalized_as_of,
            pattern_window=str(pattern["key"]),
        )

    symbols = list(dict.fromkeys([str(proxy_etf), "SPY", *[str(item) for item in comparison_symbols]]))
    if price_history is None:
        try:
            price_history = _load_default_price_history_as_of(symbols, normalized_as_of)
        except Exception as exc:  # pragma: no cover - UI resilience around local DB availability
            return _base_model(
                status="INSUFFICIENT_DATA",
                headline="과거 유사 맥락 자료 부족",
                detail=f"DB price history read failed: {exc}",
                leadership_sector=str(leadership_sector or ""),
                proxy_etf=str(proxy_etf),
                as_of_date=normalized_as_of,
                pattern_window=str(pattern["key"]),
            )

    coverage = summarize_price_coverage(
        price_history,
        symbols=symbols,
        min_rows=min_history_rows,
        end_date=normalized_as_of,
    )
    coverage_gaps = _coverage_gap_rows(coverage)
    repair_action = _coverage_repair_action(coverage_gaps)
    coverage_by_symbol = {row["symbol"]: row for row in coverage}
    proxy_coverage = coverage_by_symbol.get(str(proxy_etf))
    spy_coverage = coverage_by_symbol.get("SPY")
    if not proxy_coverage or proxy_coverage["status"] != "OK" or not spy_coverage or spy_coverage["status"] != "OK":
        insufficient = proxy_coverage if not proxy_coverage or proxy_coverage["status"] != "OK" else spy_coverage
        detail = (
            f"{leadership_sector}({proxy_etf}) 기준 가격 coverage가 부족합니다. "
            f"{(insufficient or {}).get('symbol') or proxy_etf}: "
            f"{(insufficient or {}).get('row_count') or 0} rows "
            f"({(insufficient or {}).get('start_date') or '-'} ~ {(insufficient or {}).get('end_date') or '-'})."
        )
        return _base_model(
            status="INSUFFICIENT_DATA",
            headline="과거 유사 맥락 자료 부족",
            detail=detail,
            leadership_sector=str(leadership_sector or ""),
            proxy_etf=str(proxy_etf),
            coverage=coverage,
            coverage_gaps=coverage_gaps,
            repair_action=repair_action,
            as_of_date=normalized_as_of,
            pattern_window=str(pattern["key"]),
        )

    matrix = _price_matrix(price_history, symbols, end_date=normalized_as_of)
    if matrix.empty or str(proxy_etf) not in matrix.columns or "SPY" not in matrix.columns:
        return _base_model(
            status="INSUFFICIENT_DATA",
            headline="과거 유사 맥락 자료 부족",
            detail=f"{leadership_sector}({proxy_etf})와 SPY 공통 가격 구간이 없습니다.",
            leadership_sector=str(leadership_sector or ""),
            proxy_etf=str(proxy_etf),
            coverage=coverage,
            coverage_gaps=coverage_gaps,
            repair_action=repair_action,
            as_of_date=normalized_as_of,
            pattern_window=str(pattern["key"]),
        )

    analysis_matrix = matrix.dropna(subset=[str(proxy_etf), "SPY"])
    max_horizon = max(int(horizon) for horizon in horizons)
    if len(analysis_matrix) < max(min_history_rows, max_horizon + pattern_days + 1):
        return _base_model(
            status="INSUFFICIENT_DATA",
            headline="과거 유사 맥락 자료 부족",
            detail=f"{leadership_sector}({proxy_etf})와 SPY 공통 history가 {len(analysis_matrix)} rows로 부족합니다.",
            leadership_sector=str(leadership_sector or ""),
            proxy_etf=str(proxy_etf),
            coverage=coverage,
            coverage_gaps=coverage_gaps,
            repair_action=repair_action,
            as_of_date=normalized_as_of,
            pattern_window=str(pattern["key"]),
        )

    latest_index = len(analysis_matrix) - 1
    proxy_series = analysis_matrix[str(proxy_etf)]
    spy_series = analysis_matrix["SPY"]
    current_proxy_window = _period_return(proxy_series, latest_index, pattern_days)
    current_spy_window = _period_return(spy_series, latest_index, pattern_days)
    if current_proxy_window is None or current_spy_window is None:
        return _base_model(
            status="INSUFFICIENT_DATA",
            headline="과거 유사 맥락 자료 부족",
            detail=f"{leadership_sector}({proxy_etf})의 {pattern_label} 상대강도 계산 구간이 부족합니다.",
            leadership_sector=str(leadership_sector or ""),
            proxy_etf=str(proxy_etf),
            coverage=coverage,
            coverage_gaps=coverage_gaps,
            repair_action=repair_action,
            as_of_date=normalized_as_of,
            pattern_window=str(pattern["key"]),
        )

    current_rel_window = current_proxy_window - current_spy_window
    current_proxy_5d = _period_return(proxy_series, latest_index, 5)
    current_spy_5d = _period_return(spy_series, latest_index, 5)
    current_rel_5d = (
        current_proxy_5d - current_spy_5d
        if current_proxy_5d is not None and current_spy_5d is not None
        else None
    )
    current_proxy_20d = _period_return(proxy_series, latest_index, 20)
    current_spy_20d = _period_return(spy_series, latest_index, 20)
    current_rel_20d = (
        current_proxy_20d - current_spy_20d
        if current_proxy_20d is not None and current_spy_20d is not None
        else None
    )
    threshold = max(relative_strength_floor, current_rel_window * relative_strength_ratio)
    latest_forwardable_index = latest_index - max_horizon
    candidates: list[int] = []
    for index in range(pattern_days, max(pattern_days, latest_forwardable_index + 1)):
        proxy_return = _period_return(proxy_series, index, pattern_days)
        spy_return = _period_return(spy_series, index, pattern_days)
        if proxy_return is None or spy_return is None:
            continue
        if proxy_return - spy_return >= threshold:
            candidates.append(index)

    anchor_indices = _dedupe_anchor_indices(candidates, min_gap=min_anchor_gap)
    rows = _distribution_rows_for_anchors(
        analysis_matrix,
        symbols=symbols,
        horizons=horizons,
        anchor_indices=anchor_indices,
    )

    sample_count = len(anchor_indices)
    status = "OK" if sample_count >= min_sample_count else "REVIEW"
    headline = (
        f"과거 유사 맥락 {sample_count}회 발견"
        if status == "OK"
        else f"과거 유사 맥락 표본 {sample_count}회"
    )
    condition_summary = (
        f"{proxy_etf} {pattern_label}-SPY {pattern_label} 상대강도 >= {_format_pct(threshold)} "
        f"(선택 기준 gap {_format_pct(current_rel_window)}, 5D gap {_format_pct(current_rel_5d)}, "
        f"20D gap {_format_pct(current_rel_20d)})"
    )
    first_date = _format_date(analysis_matrix.index.min()) or ""
    last_date = _format_date(analysis_matrix.index.max()) or ""
    futures_load_error: str | None = None
    if futures_history is None:
        try:
            futures_history = _load_default_futures_ohlcv_as_of(DEFAULT_FUTURES_RATE_PRESSURE_SYMBOLS, last_date)
        except Exception as exc:  # pragma: no cover - UI resilience around local DB availability
            futures_history = pd.DataFrame()
            futures_load_error = str(exc)
    macro_conditioned_analog = _macro_conditioned_pilot_model(
        analysis_matrix=analysis_matrix,
        symbols=symbols,
        horizons=horizons,
        anchor_indices=anchor_indices,
        pattern_days=pattern_days,
        pattern_label=pattern_label,
        proxy_etf=str(proxy_etf),
        broad_condition_summary=condition_summary,
        coverage_by_symbol=coverage_by_symbol,
        min_sample_count=min_sample_count,
        futures_history=futures_history,
        futures_as_of_date=last_date,
        futures_load_error=futures_load_error,
    )
    return {
        "schema_version": "overview_market_context_historical_analog_v2",
        "status": status,
        "headline": headline,
        "detail": f"{leadership_sector}({proxy_etf})가 SPY 대비 강했던 과거 구간 기준",
        "leadership_sector": str(leadership_sector or ""),
        "proxy_etf": str(proxy_etf),
        "sample_count": sample_count,
        "condition_summary": condition_summary,
        "data_window": f"{first_date} - {last_date}" if first_date and last_date else "",
        "current_as_of": last_date,
        "requested_as_of": normalized_as_of or "latest",
        "as_of_mode": "selected" if normalized_as_of else "latest",
        "pattern_window": pattern["key"],
        "pattern_window_label": pattern_label,
        "pattern_window_days": pattern_days,
        "calculation_note": f"선택한 기준 시점의 sector ETF SPY 대비 {pattern_label} 상대강도 기준",
        "leadership_replay_basis": "current universe/sector metadata + DB prices through the selected as-of date",
        "coverage": coverage,
        "coverage_gaps": coverage_gaps,
        "repair_action": repair_action,
        "rows": rows,
        "anchor_dates": [
            date_value
            for index in anchor_indices
            for date_value in [_format_date(analysis_matrix.index[index])]
            if date_value
        ],
        "macro_conditioned_analog": macro_conditioned_analog,
        "limitations": [
            *_default_limitations(),
            "선택 기준일 이후 가격은 anchor 탐색과 forward 분포에 사용하지 않음",
            "as-of sector leadership은 현재 universe/sector metadata 기반 재계산",
        ],
        "boundary_note": (
            "Overview context-only 참고 정보입니다. Backtest strategy, validation gate, "
            "Final Review decision, Operations monitoring으로 연결하지 않습니다."
        ),
    }
