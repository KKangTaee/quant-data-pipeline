from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable, Sequence

import pandas as pd

from .commands import EndResolution, EntryResolution
from .persistence import MonitoringItemRecord, PositionEventRecord
from .position_events import (
    is_position_ledger_item,
    project_position_events,
    validate_position_sequence,
)
from .schemas import FundingMode


END_RETURN_GAP_TOLERANCE = Decimal("0.005")
SESSION_CONTINUITY_GAP_TOLERANCE = Decimal("0.01")


class EntryPriceUnavailableError(ValueError):
    pass


class TrackingEndValueUnavailableError(ValueError):
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
class PositionLedgerSummary:
    eligible: bool
    effective_initial_shares: Decimal | None
    current_shares: Decimal | None
    cumulative_contributions: Decimal
    cumulative_withdrawals: Decimal
    pnl: Decimal | None
    event_rows: tuple[dict[str, Any], ...]
    requested_start_date: date | None = None
    effective_start_date: date | None = None
    entry_close: Decimal | None = None
    initial_capital: Decimal | None = None


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
    readiness: Any | None = None
    position: PositionLedgerSummary | None = None


def _decimal(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return parsed if parsed.is_finite() else None


def resolve_tracking_end(
    lane: ItemValueLane,
    requested_end_date: date,
) -> EndResolution:
    """Freeze tracking at the latest usable value known on the requested date."""

    if not isinstance(requested_end_date, date):
        raise ValuationInputError("requested end date is required.")
    frame = lane.curve.copy()
    if frame.empty or "date" not in frame.columns or "total_value" not in frame.columns:
        raise TrackingEndValueUnavailableError(
            "요청한 종료일 이전에 사용할 수 있는 평가금액이 없습니다."
        )
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce").dt.normalize()
    frame["total_value"] = pd.to_numeric(frame["total_value"], errors="coerce")
    eligible = frame.dropna(subset=["date", "total_value"])
    eligible = eligible.loc[
        eligible["date"] <= pd.Timestamp(requested_end_date)
    ].sort_values("date")
    if eligible.empty:
        raise TrackingEndValueUnavailableError(
            "요청한 종료일 이전에 사용할 수 있는 평가금액이 없습니다."
        )
    row = eligible.iloc[-1]
    exit_value = _decimal(row["total_value"])
    if exit_value is None or exit_value < 0:
        raise TrackingEndValueUnavailableError(
            "종료 평가금액을 계산할 수 없습니다."
        )
    return EndResolution(
        requested_end_date=requested_end_date,
        effective_end_date=pd.Timestamp(row["date"]).date(),
        exit_value=exit_value,
    )


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


def modified_dietz_return(
    begin_value: Decimal,
    end_value: Decimal,
    net_external_flow: Decimal,
) -> Decimal | None:
    """Calculate a daily return using a fixed half-day external-flow weight."""

    denominator = begin_value + Decimal("0.5") * net_external_flow
    if denominator <= 0:
        return None
    return (end_value - begin_value - net_external_flow) / denominator


def build_direct_security_value_lane(
    item: MonitoringItemRecord,
    history: pd.DataFrame | Iterable[dict[str, Any]],
    position_events: Sequence[PositionEventRecord] = (),
) -> ItemValueLane:
    """Build a split-first position ledger with flow-adjusted performance."""

    if item.source_type != "direct_security" or item.instrument_kind not in {"stock", "etf"}:
        raise ValuationInputError("A direct stock or ETF item is required.")
    if item.entry_close <= 0 or item.initial_capital <= 0:
        raise ValuationInputError("positive entry close and initial capital are required.")
    event_records = tuple(position_events)
    position_eligible = is_position_ledger_item(item)
    if event_records and not position_eligible:
        raise ValuationInputError(
            "Position events require a stock or ETF held by share count."
        )
    projection = (
        project_position_events(item, event_records)
        if position_eligible
        else None
    )
    initial_contract = projection.initial_contract if projection is not None else None
    effective_start_date = (
        initial_contract.effective_start_date
        if initial_contract is not None
        else item.effective_start_date
    )
    frame = _prepare_history(history)
    frame = frame.loc[
        frame["date"] >= pd.Timestamp(effective_start_date)
    ].copy()
    if frame.empty or frame.iloc[0]["date"].date() != effective_start_date:
        raise EntryPriceUnavailableError(
            f"No usable close exists on effective start {effective_start_date.isoformat()}."
        )
    if projection is not None:
        units = Decimal(projection.initial_contract.initial_shares)
    else:
        units = _initial_units(item)
    initial_capital = (
        initial_contract.initial_capital
        if initial_contract is not None
        else item.initial_capital
    )
    if initial_capital <= 0:
        raise ValuationInputError("effective initial capital must be positive.")

    split_factors: dict[date, Decimal] = {}
    for row_index, row in frame.iterrows():
        if row_index == frame.index[0]:
            continue
        factor = _decimal(row["stock_splits"])
        if factor is not None and factor > 0 and factor != 1:
            split_factors[row["date"].date()] = factor
    snapshots = (
        validate_position_sequence(item, projection, split_factors)
        if projection is not None
        else ()
    )
    trades_by_date: dict[date, list[Any]] = {}
    if projection is not None:
        available_dates = {timestamp.date() for timestamp in frame["date"]}
        for trade in projection.trades:
            if trade.trade_date not in available_dates:
                raise ValuationInputError(
                    "Every effective trade requires an exact stored market date."
                )
            trades_by_date.setdefault(trade.trade_date, []).append(trade)

    dividend_cash = Decimal("0")
    cumulative_contributions = initial_capital
    cumulative_withdrawals = Decimal("0")
    entry_adj_close = _decimal(frame.iloc[0]["adj_close"])
    rows: list[dict[str, Any]] = []
    raw_indexes: list[Decimal] = []
    adjusted_indexes: list[Decimal] = []
    adjusted_complete = entry_adj_close is not None and entry_adj_close > 0
    flow_adjusted_index: Decimal | None = Decimal("1")
    previous_total = initial_capital
    invalid_flow_return = False

    for row_index, row in frame.iterrows():
        close = _decimal(row["close"])
        if close is None or close <= 0:
            continue
        row_date = row["date"].date()
        if row_index != frame.index[0]:
            split_factor = _decimal(row["stock_splits"])
            if split_factor is not None and split_factor > 0 and split_factor != 1:
                units *= split_factor
        external_flow = Decimal("0")
        for trade in trades_by_date.get(row_date, []):
            if trade.execution_price is None or trade.execution_price <= 0:
                raise ValuationInputError("Effective trades require a positive price.")
            quantity = Decimal(trade.quantity)
            if trade.position_effect == "buy":
                contribution = quantity * trade.execution_price + trade.fee_usd
                units += quantity
                cumulative_contributions += contribution
                external_flow += contribution
            else:
                withdrawal = quantity * trade.execution_price - trade.fee_usd
                if withdrawal <= 0:
                    raise ValuationInputError(
                        "Sell withdrawal must remain positive after fees."
                    )
                units -= quantity
                cumulative_withdrawals += withdrawal
                external_flow -= withdrawal
            if units < 1:
                raise ValuationInputError(
                    "A partial sell must leave at least one share."
                )
        if row_index != frame.index[0]:
            dividend = _decimal(row["dividends"])
            if dividend is not None and dividend > 0:
                dividend_cash += units * dividend
        market_value = units * close
        total_value = market_value + dividend_cash
        daily_return = modified_dietz_return(
            previous_total,
            total_value,
            external_flow,
        )
        if daily_return is None or flow_adjusted_index is None:
            invalid_flow_return = True
            flow_adjusted_index = None
        else:
            flow_adjusted_index *= Decimal("1") + daily_return
        raw_index = (
            flow_adjusted_index
            if event_records
            else total_value / initial_capital
        )
        adj_close = _decimal(row["adj_close"])
        if (
            event_records
            or not adjusted_complete
            or adj_close is None
            or adj_close <= 0
            or entry_adj_close is None
        ):
            adjusted_complete = False
            adjusted_index = None
            adjusted_value = None
        else:
            adjusted_index = adj_close / entry_adj_close
            adjusted_value = initial_capital * adjusted_index
            adjusted_indexes.append(adjusted_index)
        if raw_index is not None:
            raw_indexes.append(raw_index)
        rows.append(
            {
                "date": row["date"],
                "effective_units": float(units),
                "close": float(close),
                "market_value": float(market_value),
                "dividend_cash": float(dividend_cash),
                "total_value": float(total_value),
                "raw_return_index": float(raw_index) if raw_index is not None else None,
                "adjusted_return_index": (
                    float(adjusted_index) if adjusted_index is not None else None
                ),
                "adjusted_value": float(adjusted_value) if adjusted_value is not None else None,
                "external_flow": float(external_flow),
                "cumulative_contributions": float(cumulative_contributions),
                "cumulative_withdrawals": float(cumulative_withdrawals),
                "daily_flow_adjusted_return": (
                    float(daily_return) if daily_return is not None else None
                ),
                "flow_adjusted_index": (
                    float(flow_adjusted_index)
                    if flow_adjusted_index is not None
                    else None
                ),
            }
        )
        previous_total = total_value

    if not rows:
        raise EntryPriceUnavailableError("No usable value rows are available after effective start.")
    review = (
        assess_corporate_action_consistency(raw_indexes, adjusted_indexes)
        if (
            not event_records
            and adjusted_complete
            and len(adjusted_indexes) == len(raw_indexes)
        )
        else CorporateActionReview(
            status="NOT_AVAILABLE",
            total_return_gap=None,
            max_session_gap=None,
            reasons=("Adjusted-close cross-check coverage is unavailable.",),
        )
    )
    lane_status = (
        "data_review"
        if (
            review.status == "DATA_REVIEW"
            or item.status == "data_review"
            or invalid_flow_return
        )
        else item.status
    )
    curve = pd.DataFrame(rows)
    curve["data_status"] = lane_status
    position = None
    if projection is not None:
        shares_after_by_root = {
            snapshot.root_event_id: snapshot.shares_after
            for snapshot in snapshots
        }
        record_by_id = {
            record.position_event_id: record for record in event_records
        }
        terminal_id_by_root = {
            audit.root_event_id: audit.position_event_id
            for audit in projection.audit_rows
            if audit.status in {"active", "voided"}
        }
        event_rows = []
        for audit in projection.audit_rows:
            record = record_by_id[audit.position_event_id]
            event_rows.append(
                {
                    "root_event_id": record.root_event_id,
                    "current_event_id": terminal_id_by_root[record.root_event_id],
                    "position_event_id": record.position_event_id,
                    "status": audit.status,
                    "position_effect": record.position_effect,
                    "trade_date": record.trade_date.isoformat(),
                    "event_order": record.event_order,
                    "quantity": record.quantity,
                    "execution_price": record.execution_price,
                    "reference_close": record.reference_close,
                    "execution_price_source": record.execution_price_source,
                    "fee_usd": record.fee_usd,
                    "note": record.note,
                    "shares_after": (
                        shares_after_by_root.get(record.root_event_id)
                        if audit.status == "active"
                        else None
                    ),
                }
            )
        position = PositionLedgerSummary(
            eligible=True,
            effective_initial_shares=Decimal(
                projection.effective_initial_shares or 0
            ),
            current_shares=units,
            cumulative_contributions=cumulative_contributions,
            cumulative_withdrawals=cumulative_withdrawals,
            pnl=previous_total
            + cumulative_withdrawals
            - cumulative_contributions,
            event_rows=tuple(event_rows),
            requested_start_date=projection.initial_contract.requested_start_date,
            effective_start_date=projection.initial_contract.effective_start_date,
            entry_close=projection.initial_contract.entry_close,
            initial_capital=projection.initial_contract.initial_capital,
        )
    return ItemValueLane(
        monitoring_item_id=item.monitoring_item_id,
        source_ref=item.source_ref,
        effective_start_date=effective_start_date,
        latest_usable_date=curve.iloc[-1]["date"].date(),
        initial_capital=initial_capital,
        status=lane_status,
        curve=curve,
        review=review,
        position=position,
    )
