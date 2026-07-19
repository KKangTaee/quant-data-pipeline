from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable

import pandas as pd

from .commands import EntryResolution
from .persistence import MonitoringItemRecord
from .schemas import FundingMode


END_RETURN_GAP_TOLERANCE = Decimal("0.005")
SESSION_CONTINUITY_GAP_TOLERANCE = Decimal("0.01")


class EntryPriceUnavailableError(ValueError):
    pass


class ValuationInputError(ValueError):
    pass


@dataclass(frozen=True)
class CorporateActionReview:
    status: str
    total_return_gap: Decimal | None
    max_session_gap: Decimal | None
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class ItemValueLane:
    monitoring_item_id: str
    source_ref: str
    effective_start_date: date
    latest_usable_date: date
    initial_capital: Decimal
    status: str
    curve: pd.DataFrame
    review: CorporateActionReview


def _decimal(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return parsed if parsed.is_finite() else None


def _prepare_history(history: pd.DataFrame | Iterable[dict[str, Any]]) -> pd.DataFrame:
    frame = history.copy() if isinstance(history, pd.DataFrame) else pd.DataFrame(list(history))
    if frame.empty or "date" not in frame.columns or "close" not in frame.columns:
        return pd.DataFrame(
            columns=["date", "close", "adj_close", "dividends", "stock_splits"]
        )
    normalized = frame.copy()
    normalized["date"] = pd.to_datetime(normalized["date"], errors="coerce").dt.normalize()
    for column in ("close", "adj_close", "dividends", "stock_splits"):
        if column not in normalized.columns:
            normalized[column] = 0.0 if column in {"dividends", "stock_splits"} else float("nan")
        normalized[column] = pd.to_numeric(normalized[column], errors="coerce")
    normalized = normalized.dropna(subset=["date", "close"])
    normalized = normalized.loc[normalized["close"] > 0].copy()
    normalized["dividends"] = normalized["dividends"].fillna(0.0)
    normalized["stock_splits"] = normalized["stock_splits"].fillna(0.0)
    return (
        normalized.sort_values("date")
        .drop_duplicates(subset=["date"], keep="last")
        .reset_index(drop=True)
    )


def resolve_direct_security_entry(
    history: pd.DataFrame | Iterable[dict[str, Any]],
    requested_date: date,
    funding_mode: FundingMode | str,
    value: Decimal | int,
) -> EntryResolution:
    """Resolve the first positive stored close on or after the requested date."""

    if not isinstance(requested_date, date):
        raise ValuationInputError("requested date is required.")
    frame = _prepare_history(history)
    eligible = frame.loc[frame["date"] >= pd.Timestamp(requested_date)]
    if eligible.empty:
        raise EntryPriceUnavailableError(
            f"No usable close is available on or after {requested_date.isoformat()}."
        )
    row = eligible.iloc[0]
    entry_close = _decimal(row["close"])
    if entry_close is None or entry_close <= 0:
        raise EntryPriceUnavailableError(
            f"No usable close is available on or after {requested_date.isoformat()}."
        )
    normalized_mode = str(getattr(funding_mode, "value", funding_mode)).strip()
    if normalized_mode == FundingMode.FIXED_NOTIONAL.value:
        notional = _decimal(value)
        if notional is None or notional <= 0:
            raise ValuationInputError("positive notional is required.")
        units = notional / entry_close
        initial_capital = units * entry_close
    elif normalized_mode == FundingMode.FIXED_SHARES.value:
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValuationInputError("integer shares must be at least 1.")
        units = Decimal(value)
        initial_capital = units * entry_close
    else:
        raise ValuationInputError(f"Unsupported funding mode: {funding_mode!r}")
    return EntryResolution(
        effective_start_date=row["date"].date(),
        entry_close=entry_close,
        initial_capital=initial_capital,
        metadata={
            "virtual_units": str(units),
            "requested_start_date": requested_date.isoformat(),
            "effective_start_date": row["date"].date().isoformat(),
            "entry_price_source": "finance_price.nyse_price_history.close",
        },
    )


def _decimal_series(values: Iterable[Any]) -> list[Decimal]:
    normalized: list[Decimal] = []
    for value in values:
        parsed = _decimal(value)
        if parsed is None or parsed <= 0:
            raise ValuationInputError("Return index values must be positive and finite.")
        normalized.append(parsed)
    return normalized


def assess_corporate_action_consistency(
    raw_return_index: Iterable[Any],
    adjusted_return_index: Iterable[Any],
) -> CorporateActionReview:
    raw = _decimal_series(raw_return_index)
    adjusted = _decimal_series(adjusted_return_index)
    if not raw or len(raw) != len(adjusted):
        return CorporateActionReview(
            status="NOT_AVAILABLE",
            total_return_gap=None,
            max_session_gap=None,
            reasons=("Adjusted-close cross-check coverage is unavailable.",),
        )

    total_return_gap = abs((raw[-1] - Decimal("1")) - (adjusted[-1] - Decimal("1")))
    session_gaps: list[Decimal] = []
    for index in range(1, len(raw)):
        raw_return = raw[index] / raw[index - 1] - Decimal("1")
        adjusted_return = adjusted[index] / adjusted[index - 1] - Decimal("1")
        session_gaps.append(abs(raw_return - adjusted_return))
    max_session_gap = max(session_gaps, default=Decimal("0"))
    reasons: list[str] = []
    if total_return_gap > END_RETURN_GAP_TOLERANCE:
        reasons.append("End total-return gap exceeds 0.50%p.")
    if max_session_gap > SESSION_CONTINUITY_GAP_TOLERANCE:
        reasons.append("Single-session continuity gap exceeds 1.00%p.")
    return CorporateActionReview(
        status="DATA_REVIEW" if reasons else "READY",
        total_return_gap=total_return_gap,
        max_session_gap=max_session_gap,
        reasons=tuple(reasons),
    )


def _initial_units(item: MonitoringItemRecord) -> Decimal:
    if item.funding_mode == FundingMode.FIXED_NOTIONAL.value:
        if item.input_notional is None or item.input_notional <= 0:
            raise ValuationInputError("positive item notional is required.")
        return item.input_notional / item.entry_close
    if item.funding_mode == FundingMode.FIXED_SHARES.value:
        if isinstance(item.input_shares, bool) or not isinstance(item.input_shares, int) or item.input_shares < 1:
            raise ValuationInputError("integer item shares must be at least 1.")
        return Decimal(item.input_shares)
    raise ValuationInputError(f"Unsupported item funding mode: {item.funding_mode!r}")


def build_direct_security_value_lane(
    item: MonitoringItemRecord,
    history: pd.DataFrame | Iterable[dict[str, Any]],
) -> ItemValueLane:
    """Build a raw-close primary ledger with split units and cash dividends."""

    if item.source_type != "direct_security" or item.instrument_kind not in {"stock", "etf"}:
        raise ValuationInputError("A direct stock or ETF item is required.")
    if item.entry_close <= 0 or item.initial_capital <= 0:
        raise ValuationInputError("positive entry close and initial capital are required.")
    frame = _prepare_history(history)
    frame = frame.loc[frame["date"] >= pd.Timestamp(item.effective_start_date)].copy()
    if frame.empty or frame.iloc[0]["date"].date() != item.effective_start_date:
        raise EntryPriceUnavailableError(
            f"No usable close exists on effective start {item.effective_start_date.isoformat()}."
        )

    units = _initial_units(item)
    dividend_cash = Decimal("0")
    entry_adj_close = _decimal(frame.iloc[0]["adj_close"])
    rows: list[dict[str, Any]] = []
    raw_indexes: list[Decimal] = []
    adjusted_indexes: list[Decimal] = []
    adjusted_complete = entry_adj_close is not None and entry_adj_close > 0

    for row_index, row in frame.iterrows():
        close = _decimal(row["close"])
        if close is None or close <= 0:
            continue
        if row_index != frame.index[0]:
            split_factor = _decimal(row["stock_splits"])
            if split_factor is not None and split_factor > 0 and split_factor != 1:
                units *= split_factor
            dividend = _decimal(row["dividends"])
            if dividend is not None and dividend > 0:
                dividend_cash += units * dividend
        market_value = units * close
        total_value = market_value + dividend_cash
        raw_index = total_value / item.initial_capital
        adj_close = _decimal(row["adj_close"])
        if not adjusted_complete or adj_close is None or adj_close <= 0 or entry_adj_close is None:
            adjusted_complete = False
            adjusted_index = None
            adjusted_value = None
        else:
            adjusted_index = adj_close / entry_adj_close
            adjusted_value = item.initial_capital * adjusted_index
            adjusted_indexes.append(adjusted_index)
        raw_indexes.append(raw_index)
        rows.append(
            {
                "date": row["date"],
                "effective_units": float(units),
                "close": float(close),
                "market_value": float(market_value),
                "dividend_cash": float(dividend_cash),
                "total_value": float(total_value),
                "raw_return_index": float(raw_index),
                "adjusted_return_index": (
                    float(adjusted_index) if adjusted_index is not None else None
                ),
                "adjusted_value": float(adjusted_value) if adjusted_value is not None else None,
            }
        )

    if not rows:
        raise EntryPriceUnavailableError("No usable value rows are available after effective start.")
    review = (
        assess_corporate_action_consistency(raw_indexes, adjusted_indexes)
        if adjusted_complete and len(adjusted_indexes) == len(raw_indexes)
        else CorporateActionReview(
            status="NOT_AVAILABLE",
            total_return_gap=None,
            max_session_gap=None,
            reasons=("Adjusted-close cross-check coverage is unavailable.",),
        )
    )
    lane_status = (
        "data_review"
        if review.status == "DATA_REVIEW" or item.status == "data_review"
        else item.status
    )
    curve = pd.DataFrame(rows)
    curve["data_status"] = lane_status
    return ItemValueLane(
        monitoring_item_id=item.monitoring_item_id,
        source_ref=item.source_ref,
        effective_start_date=item.effective_start_date,
        latest_usable_date=curve.iloc[-1]["date"].date(),
        initial_capital=item.initial_capital,
        status=lane_status,
        curve=curve,
        review=review,
    )
