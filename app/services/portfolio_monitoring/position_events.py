from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Mapping, Sequence

from .persistence import MonitoringItemRecord, PositionEventRecord


class PositionEventIntegrityError(RuntimeError):
    """Raised when an append-only revision chain is internally inconsistent."""


class PositionEventValidationError(ValueError):
    """Raised when an otherwise valid event would create an invalid position."""


@dataclass(frozen=True)
class EffectivePositionEvent:
    root_event_id: str
    current_event_id: str
    event_order: int
    position_effect: str
    trade_date: date
    quantity: int
    execution_price: Decimal | None
    reference_close: Decimal | None
    execution_price_source: str | None
    fee_usd: Decimal
    note: str


@dataclass(frozen=True)
class PositionAuditRow:
    position_event_id: str
    root_event_id: str
    status: str
    position_effect: str
    trade_date: date
    event_order: int


@dataclass(frozen=True)
class PositionQuantitySnapshot:
    root_event_id: str
    shares_before: Decimal
    shares_after: Decimal


@dataclass(frozen=True)
class PositionEventProjection:
    eligible: bool
    eligibility_reason: str | None
    effective_initial_shares: int | None
    initial_correction: EffectivePositionEvent | None
    trades: tuple[EffectivePositionEvent, ...]
    audit_rows: tuple[PositionAuditRow, ...]


def assert_position_item_eligible(item: MonitoringItemRecord) -> None:
    """Restrict position commands to active direct stocks held by share count."""

    _assert_position_item_shape(item)
    if item.status not in {"active", "data_review"}:
        raise PositionEventValidationError(
            "활성 개별주식의 보유 수량 방식에서만 사용할 수 있습니다."
        )


def _assert_position_item_shape(item: MonitoringItemRecord) -> None:
    if not (
        item.source_type == "direct_security"
        and item.instrument_kind == "stock"
        and item.funding_mode == "fixed_shares"
    ):
        raise PositionEventValidationError(
            "개별주식의 보유 수량 방식에서만 사용할 수 있습니다."
        )


def _terminal_revisions(
    records: Sequence[PositionEventRecord],
) -> dict[str, PositionEventRecord]:
    by_id: dict[str, PositionEventRecord] = {}
    by_root: dict[str, list[PositionEventRecord]] = {}
    for record in records:
        if record.position_event_id in by_id:
            raise PositionEventIntegrityError(
                f"Duplicate position event id: {record.position_event_id}"
            )
        by_id[record.position_event_id] = record
        by_root.setdefault(record.root_event_id, []).append(record)

    terminal_by_root: dict[str, PositionEventRecord] = {}
    for root_event_id, chain in by_root.items():
        roots = [row for row in chain if row.supersedes_event_id is None]
        if len(roots) != 1 or roots[0].event_action != "create":
            raise PositionEventIntegrityError(
                f"Position event root must have exactly one create revision: {root_event_id}"
            )
        root = roots[0]
        successor_by_id: dict[str, PositionEventRecord] = {}
        for row in chain:
            if row.monitoring_item_id != root.monitoring_item_id:
                raise PositionEventIntegrityError("A revision chain cannot cross monitoring items.")
            if row.event_order != root.event_order:
                raise PositionEventIntegrityError("A revision must preserve its root event order.")
            if row.position_effect != root.position_effect:
                raise PositionEventIntegrityError("A revision must preserve its position effect.")
            if row is root:
                continue
            if row.event_action not in {"replace", "void"}:
                raise PositionEventIntegrityError("A successor revision must replace or void.")
            predecessor = by_id.get(str(row.supersedes_event_id or ""))
            if predecessor is None or predecessor.root_event_id != root_event_id:
                raise PositionEventIntegrityError(
                    f"Missing predecessor in position event chain: {row.position_event_id}"
                )
            if predecessor.position_event_id in successor_by_id:
                raise PositionEventIntegrityError("A position event revision cannot fork.")
            successor_by_id[predecessor.position_event_id] = row

        current = root
        visited = {current.position_event_id}
        while current.position_event_id in successor_by_id:
            current = successor_by_id[current.position_event_id]
            if current.position_event_id in visited:
                raise PositionEventIntegrityError("A position event revision chain cannot cycle.")
            visited.add(current.position_event_id)
        if len(visited) != len(chain):
            raise PositionEventIntegrityError("A position event revision chain is disconnected.")
        terminal_by_root[root_event_id] = current
    return terminal_by_root


def _effective_event(record: PositionEventRecord) -> EffectivePositionEvent:
    if record.quantity is None or record.quantity < 1:
        raise PositionEventIntegrityError("An effective position event requires positive quantity.")
    return EffectivePositionEvent(
        root_event_id=record.root_event_id,
        current_event_id=record.position_event_id,
        event_order=record.event_order,
        position_effect=record.position_effect,
        trade_date=record.trade_date,
        quantity=record.quantity,
        execution_price=record.execution_price,
        reference_close=record.reference_close,
        execution_price_source=record.execution_price_source,
        fee_usd=record.fee_usd,
        note=record.note,
    )


def _audit_rows(
    records: Sequence[PositionEventRecord],
    terminal_by_root: Mapping[str, PositionEventRecord],
) -> tuple[PositionAuditRow, ...]:
    rows = []
    for record in sorted(
        records,
        key=lambda row: (
            row.trade_date,
            row.event_order,
            row.created_at.isoformat() if row.created_at is not None else "",
            row.position_event_id,
        ),
    ):
        terminal = terminal_by_root[record.root_event_id]
        if record.position_event_id != terminal.position_event_id:
            status = "superseded"
        elif record.event_action == "void":
            status = "voided"
        else:
            status = "active"
        rows.append(
            PositionAuditRow(
                position_event_id=record.position_event_id,
                root_event_id=record.root_event_id,
                status=status,
                position_effect=record.position_effect,
                trade_date=record.trade_date,
                event_order=record.event_order,
            )
        )
    return tuple(rows)


def project_position_events(
    item: MonitoringItemRecord,
    records: Sequence[PositionEventRecord],
) -> PositionEventProjection:
    """Resolve terminal revisions while retaining their immutable audit history."""

    _assert_position_item_shape(item)
    if any(record.monitoring_item_id != item.monitoring_item_id for record in records):
        raise PositionEventIntegrityError("Position events must belong to the projected item.")
    terminal_by_root = _terminal_revisions(records)
    effective = [
        row for row in terminal_by_root.values() if row.event_action != "void"
    ]
    corrections = [
        row
        for row in effective
        if row.position_effect == "initial_quantity_correction"
    ]
    if len(corrections) > 1:
        raise PositionEventIntegrityError(
            "Only one initial quantity correction root is allowed."
        )
    initial_shares = corrections[0].quantity if corrections else item.input_shares
    if initial_shares is None or initial_shares < 1:
        raise PositionEventIntegrityError("The effective initial quantity must be positive.")
    trades = tuple(
        _effective_event(row)
        for row in sorted(
            (
                row
                for row in effective
                if row.position_effect in {"buy", "sell"}
            ),
            key=lambda row: (row.trade_date, row.event_order, row.root_event_id),
        )
    )
    return PositionEventProjection(
        eligible=True,
        eligibility_reason=None,
        effective_initial_shares=initial_shares,
        initial_correction=(
            _effective_event(corrections[0]) if corrections else None
        ),
        trades=trades,
        audit_rows=_audit_rows(records, terminal_by_root),
    )


def validate_position_sequence(
    item: MonitoringItemRecord,
    projection: PositionEventProjection,
    split_factors: Mapping[date, Decimal],
) -> tuple[PositionQuantitySnapshot, ...]:
    """Apply splits before same-date trades and prohibit a full or oversell."""

    _assert_position_item_shape(item)
    shares = Decimal(projection.effective_initial_shares or 0)
    if shares < 1:
        raise PositionEventValidationError("최초 보유수량은 최소 1주여야 합니다.")
    snapshots: list[PositionQuantitySnapshot] = []
    applied_split_dates: set[date] = set()
    for trade in projection.trades:
        for split_date in sorted(split_factors):
            if split_date in applied_split_dates or split_date > trade.trade_date:
                continue
            split_factor = Decimal(split_factors[split_date])
            if split_factor <= 0:
                raise PositionEventValidationError("분할 배수는 양수여야 합니다.")
            shares *= split_factor
            applied_split_dates.add(split_date)
        before = shares
        if trade.position_effect == "buy":
            shares += Decimal(trade.quantity)
        else:
            shares -= Decimal(trade.quantity)
        if shares < 1:
            raise PositionEventValidationError(
                "일부매도 후 최소 1주를 유지해야 합니다. 전량매도는 추적 종료를 이용해 주세요."
            )
        snapshots.append(
            PositionQuantitySnapshot(
                root_event_id=trade.root_event_id,
                shares_before=before,
                shares_after=shares,
            )
        )
    return tuple(snapshots)
