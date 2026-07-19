from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Callable, Sequence

import pandas as pd

from .persistence import MonitoringItemRecord


MARKET_CHART_MAX_ROWS = 120
MARKET_CHART_LOOKBACK_DAYS = 240
MarketChartLoader = Callable[[MonitoringItemRecord, date, date], pd.DataFrame]


def _select_item(
    items: Sequence[MonitoringItemRecord],
    selected_item_id: str | None,
) -> MonitoringItemRecord | None:
    requested = next(
        (item for item in items if item.monitoring_item_id == selected_item_id),
        None,
    )
    if requested is not None:
        return requested
    return next((item for item in items if item.status != "ended"), items[0] if items else None)


def _projection(
    item: MonitoringItemRecord | None,
    *,
    status: str,
    rows: list[dict[str, Any]] | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    return {
        "status": status,
        "monitoring_item_id": item.monitoring_item_id if item else None,
        "source_type": item.source_type if item else None,
        "source_ref": item.source_ref if item else None,
        "instrument_kind": item.instrument_kind if item else None,
        "timeframe": "1d",
        "max_rows": MARKET_CHART_MAX_ROWS,
        "rows": rows or [],
        "reason": reason,
    }


def _compact_ohlcv_rows(frame: pd.DataFrame, basis_date: date) -> list[dict[str, Any]]:
    required = ["date", "open", "high", "low", "close"]
    if frame.empty or any(column not in frame.columns for column in required):
        return []

    compact = frame.copy()
    compact["date"] = pd.to_datetime(compact["date"], errors="coerce").dt.normalize()
    for column in ("open", "high", "low", "close", "volume"):
        if column in compact.columns:
            compact[column] = pd.to_numeric(compact[column], errors="coerce")
    compact = compact.dropna(subset=required)
    compact = compact.loc[compact["date"] <= pd.Timestamp(basis_date)]
    prices = compact[["open", "high", "low", "close"]]
    compact = compact.loc[
        (prices > 0).all(axis=1)
        & (compact["high"] >= prices.max(axis=1))
        & (compact["low"] <= prices.min(axis=1))
    ]
    compact = compact.sort_values("date").drop_duplicates(subset=["date"], keep="last").tail(MARKET_CHART_MAX_ROWS)

    rows: list[dict[str, Any]] = []
    has_volume = "volume" in compact.columns
    for row in compact.itertuples(index=False):
        volume = getattr(row, "volume", None) if has_volume else None
        rows.append(
            {
                "date": row.date.date().isoformat(),
                "open": float(row.open),
                "high": float(row.high),
                "low": float(row.low),
                "close": float(row.close),
                "volume": float(volume) if pd.notna(volume) and float(volume) >= 0 else None,
            }
        )
    return rows


def build_selected_item_market_chart(
    items: Sequence[MonitoringItemRecord],
    *,
    selected_item_id: str | None,
    basis_date: date | None,
    loader: MarketChartLoader,
) -> dict[str, Any]:
    """Project one selected direct security's bounded DB OHLCV history for the UI."""

    item = _select_item(items, selected_item_id)
    if item is None:
        return _projection(None, status="MISSING", reason="선택할 추적 항목이 없습니다.")
    if item.source_type == "selected_strategy":
        return _projection(
            item,
            status="UNSUPPORTED",
            reason="백테스트 전략에는 실제 OHLCV 캔들이 없습니다.",
        )
    if item.source_type != "direct_security" or item.instrument_kind not in {"stock", "etf"}:
        return _projection(item, status="UNSUPPORTED", reason="이 항목 유형은 OHLCV 차트를 지원하지 않습니다.")
    if basis_date is None:
        return _projection(item, status="MISSING", reason="공통 평가 기준일을 계산할 수 없습니다.")

    start_date = max(item.effective_start_date, basis_date - timedelta(days=MARKET_CHART_LOOKBACK_DAYS))
    try:
        frame = loader(item, start_date, basis_date)
        rows = _compact_ohlcv_rows(frame, basis_date)
    except Exception as exc:
        return _projection(item, status="ERROR", reason=f"가격 이력을 불러오지 못했습니다: {exc}")
    if not rows:
        return _projection(item, status="MISSING", reason="표시할 수 있는 완전한 OHLC 가격 이력이 없습니다.")
    return _projection(item, status="READY", rows=rows)
