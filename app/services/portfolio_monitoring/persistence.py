from __future__ import annotations

import json
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
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
                  (portfolio_group_id, name, is_default, status, version, deleted_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                [
                    record.portfolio_group_id,
                    record.name,
                    int(record.is_default),
                    record.status,
                    record.version,
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
