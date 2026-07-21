from __future__ import annotations

import json
import hashlib
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Callable, ContextManager, Iterator, Protocol

from finance.data.db.mysql import MySQLClient
from finance.data.db.schema import PORTFOLIO_MONITORING_SCHEMAS

from .schemas import CommandStatus


FINANCE_META_DB = "finance_meta"
DEFAULT_PORTFOLIO_GROUP_ID = "monitoring_default"
DEFAULT_PORTFOLIO_GROUP_NAME = "기본 포트폴리오"


@dataclass(frozen=True)
class PortfolioGroupRecord:
    portfolio_group_id: str
    name: str
    is_default: bool
    status: str = "active"
    version: int = 1
    metadata: dict[str, Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


@dataclass(frozen=True)
class MonitoringItemRecord:
    monitoring_item_id: str
    portfolio_group_id: str
    source_type: str
    source_ref: str
    instrument_kind: str
    requested_start_date: date
    effective_start_date: date
    funding_mode: str
    input_notional: Decimal | None
    input_shares: int | None
    entry_close: Decimal
    initial_capital: Decimal
    tracking_end_requested_date: date | None = None
    tracking_end_effective_date: date | None = None
    exit_value: Decimal | None = None
    status: str = "active"
    metadata: dict[str, Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True)
class StoredCommandRecord:
    command_id: str
    command_type: str
    target_id: str | None
    request_fingerprint: str
    status: CommandStatus
    result_ref: str | None = None
    result_json: dict[str, Any] | None = None
    error_message: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True)
class PositionEventRecord:
    """Immutable revision in an individual-stock position event chain."""

    position_event_id: str
    root_event_id: str
    supersedes_event_id: str | None
    monitoring_item_id: str
    event_order: int
    event_action: str
    position_effect: str
    trade_date: date
    quantity: int | None
    execution_price: Decimal | None
    reference_close: Decimal | None
    execution_price_source: str | None
    fee_usd: Decimal
    note: str
    command_id: str
    created_at: datetime | None = None
    requested_start_date: date | None = None
    effective_start_date: date | None = None


class MonitoringRepository(Protocol):
    def transaction(self) -> ContextManager["MonitoringRepository"]: ...

    def list_groups(self, *, include_deleted: bool = False) -> list[PortfolioGroupRecord]: ...

    def get_group(self, portfolio_group_id: str, *, for_update: bool = False) -> PortfolioGroupRecord | None: ...

    def insert_group(self, record: PortfolioGroupRecord) -> PortfolioGroupRecord: ...

    def update_group_name(self, portfolio_group_id: str, name: str, expected_version: int) -> PortfolioGroupRecord | None: ...

    def list_items(self, portfolio_group_id: str, *, statuses: set[str] | None = None) -> list[MonitoringItemRecord]: ...

    def get_item(self, monitoring_item_id: str, *, for_update: bool = False) -> MonitoringItemRecord | None: ...

    def insert_item(self, record: MonitoringItemRecord) -> MonitoringItemRecord: ...

    def end_item(self, monitoring_item_id: str, resolution: Any) -> MonitoringItemRecord | None: ...

    def reopen_item(self, monitoring_item_id: str) -> MonitoringItemRecord | None: ...

    def list_position_events(
        self,
        monitoring_item_id: str,
        *,
        for_update: bool = False,
    ) -> list[PositionEventRecord]: ...

    def get_position_event(
        self,
        position_event_id: str,
        *,
        for_update: bool = False,
    ) -> PositionEventRecord | None: ...

    def next_position_event_order(self, monitoring_item_id: str) -> int: ...

    def insert_position_event(self, record: PositionEventRecord) -> PositionEventRecord: ...

    def get_command(self, command_id: str) -> StoredCommandRecord | None: ...

    def insert_command(self, record: StoredCommandRecord) -> StoredCommandRecord: ...

    def finish_command(
        self,
        command_id: str,
        *,
        status: CommandStatus,
        result_ref: str | None,
        result_json: dict[str, Any] | None,
        error_message: str | None = None,
    ) -> StoredCommandRecord: ...


def _json_object(value: Any) -> dict[str, Any] | None:
    if value is None or value == "":
        return None
    if isinstance(value, dict):
        return dict(value)
    try:
        parsed = json.loads(str(value))
    except (TypeError, ValueError, json.JSONDecodeError):
        return None
    return dict(parsed) if isinstance(parsed, dict) else None


def _json_dump(value: dict[str, Any] | None) -> str | None:
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _group_from_row(row: dict[str, Any] | None) -> PortfolioGroupRecord | None:
    if not row:
        return None
    return PortfolioGroupRecord(
        portfolio_group_id=str(row.get("portfolio_group_id") or ""),
        name=str(row.get("name") or ""),
        is_default=bool(row.get("is_default")),
        status=str(row.get("status") or "active"),
        version=int(row.get("version") or 1),
        metadata=_json_object(row.get("metadata_json")),
        created_at=row.get("created_at"),
        updated_at=row.get("updated_at"),
        deleted_at=row.get("deleted_at"),
    )


def _item_from_row(row: dict[str, Any] | None) -> MonitoringItemRecord | None:
    if not row:
        return None
    return MonitoringItemRecord(
        monitoring_item_id=str(row.get("monitoring_item_id") or ""),
        portfolio_group_id=str(row.get("portfolio_group_id") or ""),
        source_type=str(row.get("source_type") or ""),
        source_ref=str(row.get("source_ref") or ""),
        instrument_kind=str(row.get("instrument_kind") or ""),
        requested_start_date=row["requested_start_date"],
        effective_start_date=row["effective_start_date"],
        funding_mode=str(row.get("funding_mode") or ""),
        input_notional=row.get("input_notional"),
        input_shares=row.get("input_shares"),
        entry_close=Decimal(str(row.get("entry_close"))),
        initial_capital=Decimal(str(row.get("initial_capital"))),
        tracking_end_requested_date=row.get("tracking_end_requested_date"),
        tracking_end_effective_date=row.get("tracking_end_effective_date"),
        exit_value=(Decimal(str(row["exit_value"])) if row.get("exit_value") is not None else None),
        status=str(row.get("status") or "active"),
        metadata=_json_object(row.get("metadata_json")),
        created_at=row.get("created_at"),
        updated_at=row.get("updated_at"),
    )


def _command_from_row(row: dict[str, Any] | None) -> StoredCommandRecord | None:
    if not row:
        return None
    return StoredCommandRecord(
        command_id=str(row.get("command_id") or ""),
        command_type=str(row.get("command_type") or ""),
        target_id=(str(row["target_id"]) if row.get("target_id") is not None else None),
        request_fingerprint=str(row.get("request_fingerprint") or ""),
        status=CommandStatus(str(row.get("status") or CommandStatus.PENDING.value)),
        result_ref=(str(row["result_ref"]) if row.get("result_ref") is not None else None),
        result_json=_json_object(row.get("result_json")),
        error_message=(str(row["error_message"]) if row.get("error_message") else None),
        created_at=row.get("created_at"),
        updated_at=row.get("updated_at"),
    )


def _optional_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


def _position_event_from_row(
    row: dict[str, Any] | None,
) -> PositionEventRecord | None:
    if not row:
        return None
    return PositionEventRecord(
        position_event_id=str(row.get("position_event_id") or ""),
        root_event_id=str(row.get("root_event_id") or ""),
        supersedes_event_id=(
            str(row["supersedes_event_id"])
            if row.get("supersedes_event_id") is not None
            else None
        ),
        monitoring_item_id=str(row.get("monitoring_item_id") or ""),
        event_order=int(row.get("event_order") or 0),
        event_action=str(row.get("event_action") or ""),
        position_effect=str(row.get("position_effect") or ""),
        trade_date=row["trade_date"],
        requested_start_date=row.get("requested_start_date"),
        effective_start_date=row.get("effective_start_date"),
        quantity=(int(row["quantity"]) if row.get("quantity") is not None else None),
        execution_price=_optional_decimal(row.get("execution_price")),
        reference_close=_optional_decimal(row.get("reference_close")),
        execution_price_source=(
            str(row["execution_price_source"])
            if row.get("execution_price_source") is not None
            else None
        ),
        fee_usd=Decimal(str(row.get("fee_usd") or 0)),
        note=str(row.get("note") or ""),
        command_id=str(row.get("command_id") or ""),
        created_at=row.get("created_at"),
    )


_POSITION_EVENT_OPTIONAL_COLUMNS = {
    "requested_start_date": "DATE NULL",
    "effective_start_date": "DATE NULL",
}


def _ensure_position_event_optional_columns(db: MySQLClient) -> None:
    """Add initial-correction date columns without rewriting stored events."""

    rows = db.query(
        """
        SELECT COLUMN_NAME
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        """,
        [FINANCE_META_DB, "monitoring_security_position_event"],
    )
    existing = {str(row.get("COLUMN_NAME") or "").casefold() for row in rows}
    for name, definition in _POSITION_EVENT_OPTIONAL_COLUMNS.items():
        if name.casefold() in existing:
            continue
        db.execute(
            f"ALTER TABLE `monitoring_security_position_event` "
            f"ADD COLUMN `{name}` {definition}"
        )


class MySQLMonitoringRepository:
    """MySQL-backed monitoring lifecycle repository with explicit transaction reuse."""

    def __init__(self, db_factory: Callable[[], MySQLClient]) -> None:
        self._db_factory = db_factory
        self._active_db: MySQLClient | None = None

    @contextmanager
    def _connection(self) -> Iterator[MySQLClient]:
        if self._active_db is not None:
            yield self._active_db
            return
        db = self._db_factory()
        try:
            db.use_db(FINANCE_META_DB)
            yield db
        finally:
            db.close()

    @contextmanager
    def transaction(self) -> Iterator["MySQLMonitoringRepository"]:
        if self._active_db is not None:
            yield self
            return
        db = self._db_factory()
        db.use_db(FINANCE_META_DB)
        db.begin()
        self._active_db = db
        try:
            yield self
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            self._active_db = None
            db.close()

    def ensure_schema(self) -> None:
        with self._connection() as db:
            for create_sql in PORTFOLIO_MONITORING_SCHEMAS.values():
                db.execute(create_sql)
            _ensure_position_event_optional_columns(db)

    def get_or_create_default_group(self) -> PortfolioGroupRecord:
        if self._active_db is not None:
            return self._get_or_create_default_group_in_transaction()
        with self.transaction():
            return self._get_or_create_default_group_in_transaction()

    def _get_or_create_default_group_in_transaction(self) -> PortfolioGroupRecord:
        existing = self.get_group(DEFAULT_PORTFOLIO_GROUP_ID, for_update=True)
        if existing is not None:
            return existing
        return self.insert_group(
            PortfolioGroupRecord(
                portfolio_group_id=DEFAULT_PORTFOLIO_GROUP_ID,
                name=DEFAULT_PORTFOLIO_GROUP_NAME,
                is_default=True,
            )
        )

    def list_groups(self, *, include_deleted: bool = False) -> list[PortfolioGroupRecord]:
        where = "" if include_deleted else "WHERE deleted_at IS NULL"
        with self._connection() as db:
            rows = db.query(
                f"""
                SELECT * FROM monitoring_portfolio_group
                {where}
                ORDER BY is_default DESC, created_at ASC, portfolio_group_id ASC
                """
            )
        return [record for row in rows if (record := _group_from_row(row)) is not None]

    def get_group(self, portfolio_group_id: str, *, for_update: bool = False) -> PortfolioGroupRecord | None:
        suffix = " FOR UPDATE" if for_update else ""
        with self._connection() as db:
            rows = db.query(
                f"SELECT * FROM monitoring_portfolio_group WHERE portfolio_group_id = %s{suffix}",
                [portfolio_group_id],
            )
        return _group_from_row(rows[0] if rows else None)

    def insert_group(self, record: PortfolioGroupRecord) -> PortfolioGroupRecord:
        with self._connection() as db:
            db.execute(
                """
                INSERT INTO monitoring_portfolio_group
                  (portfolio_group_id, name, is_default, status, version, metadata_json, deleted_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                [
                    record.portfolio_group_id,
                    record.name,
                    int(record.is_default),
                    record.status,
                    record.version,
                    _json_dump(record.metadata),
                    record.deleted_at,
                ],
            )
        return record

    def update_group_name(self, portfolio_group_id: str, name: str, expected_version: int) -> PortfolioGroupRecord | None:
        current = self.get_group(portfolio_group_id, for_update=True)
        if current is None or current.version != expected_version:
            return None
        with self._connection() as db:
            db.execute(
                """
                UPDATE monitoring_portfolio_group
                SET name = %s, version = version + 1
                WHERE portfolio_group_id = %s AND version = %s AND deleted_at IS NULL
                """,
                [name, portfolio_group_id, expected_version],
            )
        return self.get_group(portfolio_group_id, for_update=True)

    def list_items(self, portfolio_group_id: str, *, statuses: set[str] | None = None) -> list[MonitoringItemRecord]:
        params: list[Any] = [portfolio_group_id]
        where = ["portfolio_group_id = %s"]
        if statuses:
            normalized = sorted(str(getattr(status, "value", status)) for status in statuses)
            where.append(f"status IN ({','.join(['%s'] * len(normalized))})")
            params.extend(normalized)
        with self._connection() as db:
            rows = db.query(
                f"SELECT * FROM monitoring_portfolio_item WHERE {' AND '.join(where)} ORDER BY created_at ASC, monitoring_item_id ASC",
                params,
            )
        return [record for row in rows if (record := _item_from_row(row)) is not None]

    def get_item(self, monitoring_item_id: str, *, for_update: bool = False) -> MonitoringItemRecord | None:
        suffix = " FOR UPDATE" if for_update else ""
        with self._connection() as db:
            rows = db.query(
                f"SELECT * FROM monitoring_portfolio_item WHERE monitoring_item_id = %s{suffix}",
                [monitoring_item_id],
            )
        return _item_from_row(rows[0] if rows else None)

    def insert_item(self, record: MonitoringItemRecord) -> MonitoringItemRecord:
        with self._connection() as db:
            db.execute(
                """
                INSERT INTO monitoring_portfolio_item (
                  monitoring_item_id, portfolio_group_id, source_type, source_ref,
                  instrument_kind, requested_start_date, effective_start_date,
                  funding_mode, input_notional, input_shares, entry_close,
                  initial_capital, status, metadata_json
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                [
                    record.monitoring_item_id,
                    record.portfolio_group_id,
                    record.source_type,
                    record.source_ref,
                    record.instrument_kind,
                    record.requested_start_date,
                    record.effective_start_date,
                    record.funding_mode,
                    record.input_notional,
                    record.input_shares,
                    record.entry_close,
                    record.initial_capital,
                    record.status,
                    _json_dump(record.metadata),
                ],
            )
        return record

    def end_item(self, monitoring_item_id: str, resolution: Any) -> MonitoringItemRecord | None:
        current = self.get_item(monitoring_item_id, for_update=True)
        if current is None:
            return None
        with self._connection() as db:
            db.execute(
                """
                UPDATE monitoring_portfolio_item
                SET tracking_end_requested_date = %s,
                    tracking_end_effective_date = %s,
                    exit_value = %s,
                    status = 'ended'
                WHERE monitoring_item_id = %s AND status IN ('active','data_review')
                """,
                [
                    resolution.requested_end_date,
                    resolution.effective_end_date,
                    resolution.exit_value,
                    monitoring_item_id,
                ],
            )
        return self.get_item(monitoring_item_id, for_update=True)

    def reopen_item(self, monitoring_item_id: str) -> MonitoringItemRecord | None:
        current = self.get_item(monitoring_item_id, for_update=True)
        if current is None or current.status != "ended":
            return None
        with self._connection() as db:
            db.execute(
                """
                UPDATE monitoring_portfolio_item
                SET tracking_end_requested_date = NULL,
                    tracking_end_effective_date = NULL,
                    exit_value = NULL,
                    status = 'active'
                WHERE monitoring_item_id = %s AND status = 'ended'
                """,
                [monitoring_item_id],
            )
        return self.get_item(monitoring_item_id, for_update=True)

    def list_position_events(
        self,
        monitoring_item_id: str,
        *,
        for_update: bool = False,
    ) -> list[PositionEventRecord]:
        suffix = " FOR UPDATE" if for_update else ""
        with self._connection() as db:
            rows = db.query(
                "SELECT * FROM monitoring_security_position_event "
                "WHERE monitoring_item_id = %s "
                f"ORDER BY trade_date, event_order, created_at, position_event_id{suffix}",
                [monitoring_item_id],
            )
        return [
            record
            for row in rows
            if (record := _position_event_from_row(row)) is not None
        ]

    def get_position_event(
        self,
        position_event_id: str,
        *,
        for_update: bool = False,
    ) -> PositionEventRecord | None:
        suffix = " FOR UPDATE" if for_update else ""
        with self._connection() as db:
            rows = db.query(
                "SELECT * FROM monitoring_security_position_event "
                f"WHERE position_event_id = %s{suffix}",
                [position_event_id],
            )
        return _position_event_from_row(rows[0] if rows else None)

    def next_position_event_order(self, monitoring_item_id: str) -> int:
        # The command layer locks the owning monitoring item before allocating.
        with self._connection() as db:
            rows = db.query(
                "SELECT COALESCE(MAX(event_order), 0) AS max_order "
                "FROM monitoring_security_position_event "
                "WHERE monitoring_item_id = %s",
                [monitoring_item_id],
            )
        return int(rows[0]["max_order"] or 0) + 1

    def insert_position_event(self, record: PositionEventRecord) -> PositionEventRecord:
        with self._connection() as db:
            db.execute(
                """
                INSERT INTO monitoring_security_position_event (
                  position_event_id, root_event_id, supersedes_event_id,
                  monitoring_item_id, event_order, event_action, position_effect,
                  trade_date, requested_start_date, effective_start_date,
                  quantity, execution_price, reference_close,
                  execution_price_source, fee_usd, note, command_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                [
                    record.position_event_id,
                    record.root_event_id,
                    record.supersedes_event_id,
                    record.monitoring_item_id,
                    record.event_order,
                    record.event_action,
                    record.position_effect,
                    record.trade_date,
                    record.requested_start_date,
                    record.effective_start_date,
                    record.quantity,
                    record.execution_price,
                    record.reference_close,
                    record.execution_price_source,
                    record.fee_usd,
                    record.note,
                    record.command_id,
                ],
            )
        return record

    def get_command(self, command_id: str) -> StoredCommandRecord | None:
        with self._connection() as db:
            rows = db.query(
                "SELECT * FROM monitoring_portfolio_command WHERE command_id = %s",
                [command_id],
            )
        return _command_from_row(rows[0] if rows else None)

    def insert_command(self, record: StoredCommandRecord) -> StoredCommandRecord:
        with self._connection() as db:
            db.execute(
                """
                INSERT INTO monitoring_portfolio_command
                  (command_id, command_type, target_id, request_fingerprint, status)
                VALUES (%s, %s, %s, %s, %s)
                """,
                [
                    record.command_id,
                    record.command_type,
                    record.target_id,
                    record.request_fingerprint,
                    record.status.value,
                ],
            )
        return record

    def finish_command(
        self,
        command_id: str,
        *,
        status: CommandStatus,
        result_ref: str | None,
        result_json: dict[str, Any] | None,
        error_message: str | None = None,
    ) -> StoredCommandRecord:
        with self._connection() as db:
            db.execute(
                """
                UPDATE monitoring_portfolio_command
                SET status = %s, result_ref = %s, result_json = %s, error_message = %s
                WHERE command_id = %s
                """,
                [status.value, result_ref, _json_dump(result_json), error_message, command_id],
            )
        updated = self.get_command(command_id)
        if updated is None:
            raise RuntimeError(f"Command disappeared after update: {command_id}")
        return updated


@dataclass(frozen=True)
class LegacyImportIssue:
    code: str
    legacy_portfolio_id: str
    legacy_slot_id: str | None
    decision_id: str | None
    message: str


@dataclass(frozen=True)
class LegacyItemPlan:
    legacy_portfolio_id: str
    legacy_slot_id: str
    decision_id: str
    requested_start_date: date
    initial_capital: Decimal
    memo: str
    use_latest_end: bool
    requested_end_date: date | None


@dataclass(frozen=True)
class LegacyGroupPlan:
    legacy_portfolio_id: str
    name: str
    description: str
    source_schema_version: int | None
    items: tuple[LegacyItemPlan, ...]


@dataclass(frozen=True)
class LegacyImportPlan:
    source_path: str
    source_fingerprint: str
    groups: tuple[LegacyGroupPlan, ...]
    issues: tuple[LegacyImportIssue, ...]
    group_create_count: int
    item_create_count: int
    duplicate_item_count: int
    blocked_item_count: int


@dataclass(frozen=True)
class LegacyImportResult:
    source_fingerprint: str
    groups_created: int
    groups_replayed: int
    items_created: int
    items_replayed: int
    items_blocked: int
    items_skipped: int
    group_ids_by_legacy_id: dict[str, str]
    issues: tuple[LegacyImportIssue, ...]


def _legacy_date(value: Any) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def _legacy_positive_decimal(value: Any) -> Decimal | None:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return parsed if parsed.is_finite() and parsed > 0 else None


def _legacy_rows(source_bytes: bytes) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(source_bytes.decode("utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid legacy portfolio JSONL at line {line_number}.") from exc
        if not isinstance(row, dict):
            raise ValueError(f"Legacy portfolio row {line_number} must be an object.")
        rows.append(dict(row))
    return rows


def build_legacy_import_plan(
    path: Path | str,
    final_candidates: Sequence[dict[str, Any]],
) -> LegacyImportPlan:
    """Build a deterministic, read-only migration plan from the legacy saved JSONL."""

    source_path = Path(path)
    source_bytes = source_path.read_bytes()
    source_fingerprint = hashlib.sha256(source_bytes).hexdigest()
    candidate_ids = {
        str(row.get("decision_id") or "").strip()
        for row in final_candidates
        if row.get("monitoring_candidate") is True
        and str(row.get("decision_id") or "").strip()
    }
    groups: list[LegacyGroupPlan] = []
    issues: list[LegacyImportIssue] = []
    duplicate_count = 0
    blocked_count = 0

    for row_index, row in enumerate(_legacy_rows(source_bytes), start=1):
        if row.get("deleted_at"):
            continue
        legacy_portfolio_id = str(row.get("portfolio_id") or f"legacy-row-{row_index}").strip()
        name = str(row.get("name") or "").strip() or f"Imported Portfolio {row_index}"
        description = str(row.get("description") or "").strip()
        raw_slots = [dict(slot) for slot in list(row.get("strategy_slots") or []) if isinstance(slot, dict)]
        slot_decision_ids = {
            str(slot.get("decision_id") or "").strip()
            for slot in raw_slots
            if str(slot.get("decision_id") or "").strip()
        }
        for decision_id in list(row.get("selected_decision_ids") or []):
            clean_decision_id = str(decision_id or "").strip()
            if clean_decision_id and clean_decision_id not in slot_decision_ids:
                raw_slots.append(
                    {
                        "slot_id": f"slot_{clean_decision_id}",
                        "decision_id": clean_decision_id,
                    }
                )

        items: list[LegacyItemPlan] = []
        seen_decision_ids: set[str] = set()
        for slot_index, slot in enumerate(raw_slots, start=1):
            decision_id = str(slot.get("decision_id") or "").strip()
            slot_id = str(slot.get("slot_id") or f"slot-{slot_index}").strip()
            if decision_id in seen_decision_ids:
                duplicate_count += 1
                issues.append(
                    LegacyImportIssue(
                        code="duplicate_source",
                        legacy_portfolio_id=legacy_portfolio_id,
                        legacy_slot_id=slot_id,
                        decision_id=decision_id or None,
                        message="Duplicate selected strategy in the same legacy portfolio was skipped.",
                    )
                )
                continue
            if decision_id:
                seen_decision_ids.add(decision_id)
            if not decision_id or decision_id not in candidate_ids:
                blocked_count += 1
                issues.append(
                    LegacyImportIssue(
                        code="missing_monitoring_candidate",
                        legacy_portfolio_id=legacy_portfolio_id,
                        legacy_slot_id=slot_id,
                        decision_id=decision_id or None,
                        message="The Final Review monitoring candidate is missing or no longer monitorable.",
                    )
                )
                continue
            requested_start = _legacy_date(slot.get("start"))
            initial_capital = _legacy_positive_decimal(slot.get("initial_capital"))
            if requested_start is None or initial_capital is None:
                blocked_count += 1
                issues.append(
                    LegacyImportIssue(
                        code="invalid_legacy_slot",
                        legacy_portfolio_id=legacy_portfolio_id,
                        legacy_slot_id=slot_id,
                        decision_id=decision_id,
                        message="A valid start date and positive initial capital are required.",
                    )
                )
                continue
            items.append(
                LegacyItemPlan(
                    legacy_portfolio_id=legacy_portfolio_id,
                    legacy_slot_id=slot_id,
                    decision_id=decision_id,
                    requested_start_date=requested_start,
                    initial_capital=initial_capital,
                    memo=str(slot.get("memo") or "").strip(),
                    use_latest_end=bool(slot.get("use_latest_end", True)),
                    requested_end_date=_legacy_date(slot.get("end")),
                )
            )
        groups.append(
            LegacyGroupPlan(
                legacy_portfolio_id=legacy_portfolio_id,
                name=name,
                description=description,
                source_schema_version=(int(row["schema_version"]) if row.get("schema_version") is not None else None),
                items=tuple(items),
            )
        )

    return LegacyImportPlan(
        source_path=str(source_path),
        source_fingerprint=source_fingerprint,
        groups=tuple(groups),
        issues=tuple(issues),
        group_create_count=len(groups),
        item_create_count=sum(len(group.items) for group in groups),
        duplicate_item_count=duplicate_count,
        blocked_item_count=blocked_count,
    )


def _legacy_command_id(base_command_id: str, *identity: str) -> str:
    digest = hashlib.sha256(
        "|".join([str(base_command_id), *[str(value) for value in identity]]).encode("utf-8")
    ).hexdigest()
    return f"legacy_{digest[:48]}"


def import_legacy_portfolios(
    repository: MonitoringRepository,
    plan: LegacyImportPlan,
    command_id: str,
) -> LegacyImportResult:
    """Apply a prepared legacy plan through normal idempotent monitoring commands."""

    from .commands import EntryResolution, execute_add_item, execute_create_group
    from .schemas import (
        AddMonitoringItemInput,
        CommandType,
        FundingMode,
        InstrumentKind,
        MonitoringCommandInput,
        SourceType,
    )

    clean_command_id = str(command_id or "").strip()
    if not clean_command_id:
        raise ValueError("command_id is required.")
    groups_created = 0
    groups_replayed = 0
    items_created = 0
    items_replayed = 0
    group_ids: dict[str, str] = {}

    for group in plan.groups:
        group_metadata = {
            "legacy_portfolio_id": group.legacy_portfolio_id,
            "legacy_source_fingerprint": plan.source_fingerprint,
            "legacy_source_path": plan.source_path,
            "legacy_schema_version": group.source_schema_version,
            "legacy_description": group.description,
        }
        group_result = execute_create_group(
            repository,
            MonitoringCommandInput(
                command_id=_legacy_command_id(
                    clean_command_id,
                    plan.source_fingerprint,
                    "group",
                    group.legacy_portfolio_id,
                ),
                command_type=CommandType.CREATE_GROUP,
                target_id=None,
                payload={"name": group.name, "metadata": group_metadata},
            ),
        )
        group_ids[group.legacy_portfolio_id] = group_result.target_id
        if group_result.replayed:
            groups_replayed += 1
        else:
            groups_created += 1

        for item in group.items:
            item_metadata = {
                "legacy_portfolio_id": item.legacy_portfolio_id,
                "legacy_slot_id": item.legacy_slot_id,
                "legacy_decision_id": item.decision_id,
                "legacy_source_fingerprint": plan.source_fingerprint,
                "legacy_memo": item.memo,
                "legacy_use_latest_end": item.use_latest_end,
                "legacy_requested_end_date": (
                    item.requested_end_date.isoformat() if item.requested_end_date else None
                ),
                "legacy_requires_revalidation": True,
            }
            item_result = execute_add_item(
                repository,
                MonitoringCommandInput(
                    command_id=_legacy_command_id(
                        clean_command_id,
                        plan.source_fingerprint,
                        "item",
                        item.legacy_portfolio_id,
                        item.legacy_slot_id,
                    ),
                    command_type=CommandType.ADD_ITEM,
                    target_id=group_result.target_id,
                    payload={},
                ),
                AddMonitoringItemInput(
                    portfolio_group_id=group_result.target_id,
                    source_type=SourceType.SELECTED_STRATEGY,
                    source_ref=item.decision_id,
                    instrument_kind=InstrumentKind.STRATEGY,
                    requested_start_date=item.requested_start_date,
                    funding_mode=FundingMode.FIXED_NOTIONAL,
                    input_notional=item.initial_capital,
                ),
                resolve_entry=lambda validated, metadata=item_metadata: EntryResolution(
                    effective_start_date=validated.requested_start_date,
                    entry_close=Decimal("1"),
                    initial_capital=validated.input_notional or Decimal("0"),
                    metadata=metadata,
                ),
            )
            if item_result.replayed:
                items_replayed += 1
            else:
                items_created += 1

    return LegacyImportResult(
        source_fingerprint=plan.source_fingerprint,
        groups_created=groups_created,
        groups_replayed=groups_replayed,
        items_created=items_created,
        items_replayed=items_replayed,
        items_blocked=plan.blocked_item_count,
        items_skipped=plan.duplicate_item_count,
        group_ids_by_legacy_id=group_ids,
        issues=plan.issues,
    )
