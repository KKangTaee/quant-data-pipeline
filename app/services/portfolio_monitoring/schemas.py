from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, is_dataclass, replace
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Any, Mapping


class SourceType(str, Enum):
    DIRECT_SECURITY = "direct_security"
    SELECTED_STRATEGY = "selected_strategy"


class InstrumentKind(str, Enum):
    STOCK = "stock"
    ETF = "etf"
    STRATEGY = "strategy"


class FundingMode(str, Enum):
    FIXED_NOTIONAL = "fixed_notional"
    FIXED_SHARES = "fixed_shares"


class ItemStatus(str, Enum):
    ACTIVE = "active"
    ENDED = "ended"
    DATA_REVIEW = "data_review"


class CommandStatus(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class CommandType(str, Enum):
    CREATE_GROUP = "create_group"
    RENAME_GROUP = "rename_group"
    ADD_ITEM = "add_item"
    END_ITEM = "end_item"
    REOPEN_ITEM = "reopen_item"
    CORRECT_INITIAL_QUANTITY = "correct_initial_quantity"
    RECORD_POSITION_TRADE = "record_position_trade"
    REPLACE_POSITION_TRADE = "replace_position_trade"
    VOID_POSITION_TRADE = "void_position_trade"
    IMPORT_LEGACY = "import_legacy"


class PositionEventAction(str, Enum):
    CREATE = "create"
    REPLACE = "replace"
    VOID = "void"


class PositionEffect(str, Enum):
    INITIAL_QUANTITY_CORRECTION = "initial_quantity_correction"
    BUY = "buy"
    SELL = "sell"


class ExecutionPriceSource(str, Enum):
    DB_CLOSE_DEFAULT = "db_close_default"
    MANUAL_OVERRIDE = "manual_override"


@dataclass(frozen=True)
class AddMonitoringItemInput:
    portfolio_group_id: str
    source_type: SourceType
    source_ref: str
    instrument_kind: InstrumentKind
    requested_start_date: date
    funding_mode: FundingMode
    input_notional: Decimal | None = None
    input_shares: int | None = None


@dataclass(frozen=True)
class MonitoringCommandInput:
    command_id: str
    command_type: CommandType
    target_id: str | None
    payload: Mapping[str, Any]
    expected_version: int | None = None


@dataclass(frozen=True)
class PositionTradeInput:
    monitoring_item_id: str
    position_effect: PositionEffect
    trade_date: date
    quantity: int
    execution_price: Decimal
    fee_usd: Decimal = Decimal("0")
    note: str = ""


@dataclass(frozen=True)
class InitialQuantityCorrectionInput:
    monitoring_item_id: str
    quantity: int
    note: str = ""
    requested_start_date: date | None = None


@dataclass(frozen=True)
class ReplacePositionTradeInput:
    monitoring_item_id: str
    root_event_id: str
    expected_event_id: str
    position_effect: PositionEffect
    trade_date: date
    quantity: int
    execution_price: Decimal
    fee_usd: Decimal = Decimal("0")
    note: str = ""


@dataclass(frozen=True)
class VoidPositionTradeInput:
    monitoring_item_id: str
    root_event_id: str
    expected_event_id: str


@dataclass(frozen=True)
class DiagnosisSnapshotIdentity:
    portfolio_group_id: str
    as_of_date: date
    config_fingerprint: str
    policy_version: str


def _positive_decimal(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return decimal_value if decimal_value.is_finite() and decimal_value > 0 else None


def _nonnegative_decimal(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return decimal_value if decimal_value.is_finite() and decimal_value >= 0 else None


def _validated_position_note(value: Any) -> str:
    note = str(value or "").strip()
    if len(note) > 500:
        raise ValueError("note must contain at most 500 characters.")
    return note


def _validated_item_id(value: Any) -> str:
    item_id = str(value or "").strip()
    if not item_id:
        raise ValueError("monitoring item id is required.")
    return item_id


def _validated_quantity(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError("quantity must be an integer of at least 1.")
    return value


def validate_position_trade_input(value: PositionTradeInput) -> PositionTradeInput:
    """Normalize a buy/sell request without trusting client price provenance."""

    if not isinstance(value, PositionTradeInput):
        raise TypeError("PositionTradeInput is required.")
    item_id = _validated_item_id(value.monitoring_item_id)
    if value.position_effect not in {PositionEffect.BUY, PositionEffect.SELL}:
        raise ValueError("position trade must be buy or sell.")
    if not isinstance(value.trade_date, date):
        raise ValueError("trade date is required.")
    quantity = _validated_quantity(value.quantity)
    price = _positive_decimal(value.execution_price)
    if price is None:
        raise ValueError("execution price must be positive.")
    fee = _nonnegative_decimal(value.fee_usd)
    if fee is None:
        raise ValueError("fee must be nonnegative.")
    if (
        value.position_effect == PositionEffect.SELL
        and Decimal(quantity) * price - fee <= 0
    ):
        raise ValueError("sell withdrawal must be positive after fees.")
    return replace(
        value,
        monitoring_item_id=item_id,
        quantity=quantity,
        execution_price=price,
        fee_usd=fee,
        note=_validated_position_note(value.note),
    )


def validate_initial_quantity_correction_input(
    value: InitialQuantityCorrectionInput,
) -> InitialQuantityCorrectionInput:
    if not isinstance(value, InitialQuantityCorrectionInput):
        raise TypeError("InitialQuantityCorrectionInput is required.")
    if value.requested_start_date is not None and not isinstance(
        value.requested_start_date, date
    ):
        raise ValueError("requested start date must be a date.")
    return replace(
        value,
        monitoring_item_id=_validated_item_id(value.monitoring_item_id),
        quantity=_validated_quantity(value.quantity),
        note=_validated_position_note(value.note),
    )


def validate_replace_position_trade_input(
    value: ReplacePositionTradeInput,
) -> ReplacePositionTradeInput:
    if not isinstance(value, ReplacePositionTradeInput):
        raise TypeError("ReplacePositionTradeInput is required.")
    root_event_id = str(value.root_event_id or "").strip()
    expected_event_id = str(value.expected_event_id or "").strip()
    if not root_event_id or not expected_event_id:
        raise ValueError("root and expected position event ids are required.")
    trade = validate_position_trade_input(
        PositionTradeInput(
            monitoring_item_id=value.monitoring_item_id,
            position_effect=value.position_effect,
            trade_date=value.trade_date,
            quantity=value.quantity,
            execution_price=value.execution_price,
            fee_usd=value.fee_usd,
            note=value.note,
        )
    )
    return ReplacePositionTradeInput(
        monitoring_item_id=trade.monitoring_item_id,
        root_event_id=root_event_id,
        expected_event_id=expected_event_id,
        position_effect=trade.position_effect,
        trade_date=trade.trade_date,
        quantity=trade.quantity,
        execution_price=trade.execution_price,
        fee_usd=trade.fee_usd,
        note=trade.note,
    )


def validate_void_position_trade_input(
    value: VoidPositionTradeInput,
) -> VoidPositionTradeInput:
    if not isinstance(value, VoidPositionTradeInput):
        raise TypeError("VoidPositionTradeInput is required.")
    root_event_id = str(value.root_event_id or "").strip()
    expected_event_id = str(value.expected_event_id or "").strip()
    if not root_event_id or not expected_event_id:
        raise ValueError("root and expected position event ids are required.")
    return replace(
        value,
        monitoring_item_id=_validated_item_id(value.monitoring_item_id),
        root_event_id=root_event_id,
        expected_event_id=expected_event_id,
    )


def validate_add_item_input(value: AddMonitoringItemInput) -> AddMonitoringItemInput:
    """Validate and normalize the server-owned add-item command boundary."""

    if not isinstance(value, AddMonitoringItemInput):
        raise TypeError("AddMonitoringItemInput is required.")
    group_id = str(value.portfolio_group_id or "").strip()
    source_ref = str(value.source_ref or "").strip()
    if not group_id:
        raise ValueError("portfolio group id is required.")
    if not source_ref:
        raise ValueError("source reference is required.")
    if not isinstance(value.requested_start_date, date):
        raise ValueError("requested start date is required.")

    if value.source_type == SourceType.SELECTED_STRATEGY:
        if value.instrument_kind != InstrumentKind.STRATEGY:
            raise ValueError("selected strategy requires strategy instrument kind.")
        if value.funding_mode != FundingMode.FIXED_NOTIONAL:
            raise ValueError("selected strategy supports fixed notional only.")
    elif value.source_type == SourceType.DIRECT_SECURITY:
        if value.instrument_kind not in {InstrumentKind.STOCK, InstrumentKind.ETF}:
            raise ValueError("direct security requires stock or ETF instrument kind.")
    else:
        raise ValueError("unsupported source type.")

    if value.funding_mode == FundingMode.FIXED_SHARES:
        shares = value.input_shares
        if isinstance(shares, bool) or not isinstance(shares, int) or shares < 1:
            raise ValueError("integer shares must be at least 1.")
        if value.input_notional is not None:
            raise ValueError("input_notional must be empty in fixed shares mode.")
        return replace(value, portfolio_group_id=group_id, source_ref=source_ref)

    if value.funding_mode != FundingMode.FIXED_NOTIONAL:
        raise ValueError("unsupported funding mode.")
    notional = _positive_decimal(value.input_notional)
    if notional is None:
        raise ValueError("positive notional is required.")
    if value.input_shares is not None:
        raise ValueError("input_shares must be empty in fixed notional mode.")
    return replace(
        value,
        portfolio_group_id=group_id,
        source_ref=source_ref,
        input_notional=notional,
    )


def _fingerprint_value(value: Any) -> Any:
    if is_dataclass(value):
        return _fingerprint_value(asdict(value))
    if isinstance(value, Mapping):
        return {
            str(key): _fingerprint_value(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_fingerprint_value(item) for item in value]
    if isinstance(value, (set, frozenset)):
        normalized = [_fingerprint_value(item) for item in value]
        return sorted(normalized, key=lambda item: json.dumps(item, sort_keys=True))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat(timespec="microseconds")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return format(value, "f")
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"Unsupported fingerprint value: {type(value).__name__}")


def build_request_fingerprint(payload: Any) -> str:
    """Return a stable SHA-256 identity for an idempotent command payload."""

    canonical = json.dumps(
        _fingerprint_value(payload),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
