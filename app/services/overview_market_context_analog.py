from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

import pandas as pd

from finance.loaders.price import load_price_history


DEFAULT_COMPARISON_SYMBOLS = ("SPY", "QQQ", "TLT", "GLD", "IWM", "HYG", "LQD")
DEFAULT_HORIZONS = (5, 20, 60)
DEFAULT_MIN_HISTORY_ROWS = 756
DEFAULT_MIN_SAMPLE_COUNT = 8
DEFAULT_MIN_ANCHOR_GAP = 20
DEFAULT_RELATIVE_STRENGTH_FLOOR = 0.01
DEFAULT_RELATIVE_STRENGTH_RATIO = 0.5


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
) -> dict[str, Any]:
    current_as_of = _coverage_current_as_of(coverage or [])
    return {
        "schema_version": "overview_market_context_historical_analog_v1",
        "status": status,
        "headline": headline,
        "detail": detail,
        "leadership_sector": leadership_sector,
        "proxy_etf": proxy_etf,
        "sample_count": 0,
        "condition_summary": "",
        "data_window": "",
        "current_as_of": current_as_of,
        "calculation_note": "현재 sector ETF의 SPY 대비 5D 상대강도 기준",
        "coverage": coverage or [],
        "coverage_gaps": coverage_gaps or [],
        "repair_action": repair_action or {},
        "rows": [],
        "anchor_dates": [],
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


def summarize_price_coverage(
    price_history: pd.DataFrame | None,
    *,
    symbols: Iterable[str],
    min_rows: int = DEFAULT_MIN_HISTORY_ROWS,
) -> list[dict[str, Any]]:
    frame = _normalize_price_history(price_history)
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


def _price_matrix(price_history: pd.DataFrame | None, symbols: Sequence[str]) -> pd.DataFrame:
    frame = _normalize_price_history(price_history)
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


def _load_default_price_history(symbols: Sequence[str]) -> pd.DataFrame:
    return load_price_history(symbols=symbols, timeframe="1d")


def build_historical_analog_snapshot(
    *,
    group_leadership_snapshot: dict[str, Any] | None,
    price_history: pd.DataFrame | None = None,
    comparison_symbols: Sequence[str] = DEFAULT_COMPARISON_SYMBOLS,
    horizons: Sequence[int] = DEFAULT_HORIZONS,
    min_history_rows: int = DEFAULT_MIN_HISTORY_ROWS,
    min_sample_count: int = DEFAULT_MIN_SAMPLE_COUNT,
    min_anchor_gap: int = DEFAULT_MIN_ANCHOR_GAP,
    relative_strength_floor: float = DEFAULT_RELATIVE_STRENGTH_FLOOR,
    relative_strength_ratio: float = DEFAULT_RELATIVE_STRENGTH_RATIO,
) -> dict[str, Any]:
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
        )

    symbols = list(dict.fromkeys([str(proxy_etf), "SPY", *[str(item) for item in comparison_symbols]]))
    if price_history is None:
        try:
            price_history = _load_default_price_history(symbols)
        except Exception as exc:  # pragma: no cover - UI resilience around local DB availability
            return _base_model(
                status="INSUFFICIENT_DATA",
                headline="과거 유사 맥락 자료 부족",
                detail=f"DB price history read failed: {exc}",
                leadership_sector=str(leadership_sector or ""),
                proxy_etf=str(proxy_etf),
            )

    coverage = summarize_price_coverage(price_history, symbols=symbols, min_rows=min_history_rows)
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
        )

    matrix = _price_matrix(price_history, symbols)
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
        )

    analysis_matrix = matrix.dropna(subset=[str(proxy_etf), "SPY"])
    max_horizon = max(int(horizon) for horizon in horizons)
    if len(analysis_matrix) < max(min_history_rows, max_horizon + 6):
        return _base_model(
            status="INSUFFICIENT_DATA",
            headline="과거 유사 맥락 자료 부족",
            detail=f"{leadership_sector}({proxy_etf})와 SPY 공통 history가 {len(analysis_matrix)} rows로 부족합니다.",
            leadership_sector=str(leadership_sector or ""),
            proxy_etf=str(proxy_etf),
            coverage=coverage,
            coverage_gaps=coverage_gaps,
            repair_action=repair_action,
        )

    latest_index = len(analysis_matrix) - 1
    proxy_series = analysis_matrix[str(proxy_etf)]
    spy_series = analysis_matrix["SPY"]
    current_proxy_5d = _period_return(proxy_series, latest_index, 5)
    current_spy_5d = _period_return(spy_series, latest_index, 5)
    if current_proxy_5d is None or current_spy_5d is None:
        return _base_model(
            status="INSUFFICIENT_DATA",
            headline="과거 유사 맥락 자료 부족",
            detail=f"{leadership_sector}({proxy_etf})의 최근 5D 상대강도 계산 구간이 부족합니다.",
            leadership_sector=str(leadership_sector or ""),
            proxy_etf=str(proxy_etf),
            coverage=coverage,
            coverage_gaps=coverage_gaps,
            repair_action=repair_action,
        )

    current_rel_5d = current_proxy_5d - current_spy_5d
    current_proxy_20d = _period_return(proxy_series, latest_index, 20)
    current_spy_20d = _period_return(spy_series, latest_index, 20)
    current_rel_20d = (
        current_proxy_20d - current_spy_20d
        if current_proxy_20d is not None and current_spy_20d is not None
        else None
    )
    threshold = max(relative_strength_floor, current_rel_5d * relative_strength_ratio)
    latest_forwardable_index = latest_index - max_horizon
    candidates: list[int] = []
    for index in range(5, max(5, latest_forwardable_index + 1)):
        proxy_return = _period_return(proxy_series, index, 5)
        spy_return = _period_return(spy_series, index, 5)
        if proxy_return is None or spy_return is None:
            continue
        if proxy_return - spy_return >= threshold:
            candidates.append(index)

    anchor_indices = _dedupe_anchor_indices(candidates, min_gap=min_anchor_gap)
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

    sample_count = len(anchor_indices)
    status = "OK" if sample_count >= min_sample_count else "REVIEW"
    headline = (
        f"과거 유사 맥락 {sample_count}회 발견"
        if status == "OK"
        else f"과거 유사 맥락 표본 {sample_count}회"
    )
    condition_summary = (
        f"{proxy_etf} 5D-SPY 5D 상대강도 >= {_format_pct(threshold)} "
        f"(현재 5D gap {_format_pct(current_rel_5d)}, 20D gap {_format_pct(current_rel_20d)})"
    )
    first_date = _format_date(analysis_matrix.index.min()) or ""
    last_date = _format_date(analysis_matrix.index.max()) or ""
    return {
        "schema_version": "overview_market_context_historical_analog_v1",
        "status": status,
        "headline": headline,
        "detail": f"{leadership_sector}({proxy_etf})가 SPY 대비 강했던 과거 구간 기준",
        "leadership_sector": str(leadership_sector or ""),
        "proxy_etf": str(proxy_etf),
        "sample_count": sample_count,
        "condition_summary": condition_summary,
        "data_window": f"{first_date} - {last_date}" if first_date and last_date else "",
        "current_as_of": last_date,
        "calculation_note": "현재 sector ETF의 SPY 대비 5D 상대강도 기준",
        "coverage": coverage,
        "coverage_gaps": coverage_gaps,
        "repair_action": repair_action,
        "rows": rows,
        "anchor_dates": [_format_date(analysis_matrix.index[index]) for index in anchor_indices],
        "limitations": _default_limitations(),
        "boundary_note": (
            "Overview context-only 참고 정보입니다. Backtest strategy, validation gate, "
            "Final Review decision, Operations monitoring으로 연결하지 않습니다."
        ),
    }
