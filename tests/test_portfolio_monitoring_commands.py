from __future__ import annotations

import copy
import importlib
import unittest
from contextlib import contextmanager
from dataclasses import replace
from datetime import date
from decimal import Decimal
from unittest.mock import patch


def _load_modules():
    try:
        commands = importlib.import_module("app.services.portfolio_monitoring.commands")
        persistence = importlib.import_module("app.services.portfolio_monitoring.persistence")
        schemas = importlib.import_module("app.services.portfolio_monitoring.schemas")
    except ModuleNotFoundError as exc:
        raise AssertionError("portfolio monitoring command modules are required") from exc
    return commands, persistence, schemas


class FakeRepository:
    def __init__(self) -> None:
        self.groups = {}
        self.items = {}
        self.commands = {}
        self.position_events = []
        self.transaction_count = 0
        self.rollback_count = 0
        self.fail_item_insert = False

    @contextmanager
    def transaction(self):
        snapshot = copy.deepcopy(
            (self.groups, self.items, self.commands, self.position_events)
        )
        self.transaction_count += 1
        try:
            yield self
        except Exception:
            self.groups, self.items, self.commands, self.position_events = snapshot
            self.rollback_count += 1
            raise

    def list_groups(self, *, include_deleted=False):
        rows = list(self.groups.values())
        if not include_deleted:
            rows = [row for row in rows if row.deleted_at is None]
        return rows

    def get_group(self, portfolio_group_id, *, for_update=False):
        return self.groups.get(portfolio_group_id)

    def insert_group(self, record):
        self.groups[record.portfolio_group_id] = record
        return record

    def update_group_name(self, portfolio_group_id, name, expected_version):
        current = self.groups.get(portfolio_group_id)
        if current is None or current.version != expected_version:
            return None
        updated = replace(current, name=name, version=current.version + 1)
        self.groups[portfolio_group_id] = updated
        return updated

    def list_items(self, portfolio_group_id, *, statuses=None):
        rows = [
            row
            for row in self.items.values()
            if row.portfolio_group_id == portfolio_group_id
        ]
        if statuses is not None:
            rows = [row for row in rows if row.status in set(statuses)]
        return rows

    def get_item(self, monitoring_item_id, *, for_update=False):
        return self.items.get(monitoring_item_id)

    def insert_item(self, record):
        if self.fail_item_insert:
            raise RuntimeError("injected item insert failure")
        self.items[record.monitoring_item_id] = record
        return record

    def end_item(self, monitoring_item_id, resolution):
        current = self.items.get(monitoring_item_id)
        if current is None:
            return None
        updated = replace(
            current,
            tracking_end_requested_date=resolution.requested_end_date,
            tracking_end_effective_date=resolution.effective_end_date,
            exit_value=resolution.exit_value,
            status="ended",
        )
        self.items[monitoring_item_id] = updated
        return updated

    def reopen_item(self, monitoring_item_id):
        current = self.items.get(monitoring_item_id)
        if current is None or current.status != "ended":
            return None
        updated = replace(
            current,
            tracking_end_requested_date=None,
            tracking_end_effective_date=None,
            exit_value=None,
            status="active",
        )
        self.items[monitoring_item_id] = updated
        return updated

    def list_position_events(self, monitoring_item_id, *, for_update=False):
        return [
            row
            for row in self.position_events
            if row.monitoring_item_id == monitoring_item_id
        ]

    def get_position_event(self, position_event_id, *, for_update=False):
        return next(
            (
                row
                for row in self.position_events
                if row.position_event_id == position_event_id
            ),
            None,
        )

    def next_position_event_order(self, monitoring_item_id):
        orders = [
            row.event_order
            for row in self.position_events
            if row.monitoring_item_id == monitoring_item_id
        ]
        return max(orders, default=0) + 1

    def insert_position_event(self, record):
        self.position_events.append(record)
        return record

    def get_command(self, command_id):
        return self.commands.get(command_id)

    def insert_command(self, record):
        self.commands[record.command_id] = record
        return record

    def finish_command(self, command_id, *, status, result_ref, result_json, error_message=None):
        current = self.commands[command_id]
        updated = replace(
            current,
            status=status,
            result_ref=result_ref,
            result_json=result_json,
            error_message=error_message,
        )
        self.commands[command_id] = updated
        return updated


class RecordingDb:
    def __init__(self) -> None:
        self.used_databases = []
        self.executed = []
        self.closed = False

    def use_db(self, name):
        self.used_databases.append(name)

    def execute(self, sql, params=None):
        self.executed.append((sql, params))

    def close(self):
        self.closed = True


class PortfolioMonitoringCommandTests(unittest.TestCase):
    def _command(self, schemas, command_id, command_type, *, target_id=None, payload=None, expected_version=None):
        return schemas.MonitoringCommandInput(
            command_id=command_id,
            command_type=command_type,
            target_id=target_id,
            payload=payload or {},
            expected_version=expected_version,
        )

    def _direct_item(self, schemas, *, group_id, symbol="AAPL"):
        return schemas.AddMonitoringItemInput(
            portfolio_group_id=group_id,
            source_type=schemas.SourceType.DIRECT_SECURITY,
            source_ref=symbol,
            instrument_kind=schemas.InstrumentKind.STOCK,
            requested_start_date=date(2026, 7, 1),
            funding_mode=schemas.FundingMode.FIXED_NOTIONAL,
            input_notional=Decimal("10000"),
        )

    def _stored_direct_item(self, persistence, *, shares=30):
        return persistence.MonitoringItemRecord(
            monitoring_item_id="item-amd",
            portfolio_group_id="group-core",
            source_type="direct_security",
            source_ref="AMD",
            instrument_kind="stock",
            requested_start_date=date(2026, 7, 1),
            effective_start_date=date(2026, 7, 1),
            funding_mode="fixed_shares",
            input_notional=None,
            input_shares=shares,
            entry_close=Decimal("100"),
            initial_capital=Decimal(shares * 100),
        )

    def _position_event(
        self,
        persistence,
        *,
        event_id,
        root_id,
        supersedes=None,
        order=1,
        action="create",
        effect="buy",
        quantity=5,
        trade_date=date(2026, 7, 10),
        price=Decimal("100"),
    ):
        return persistence.PositionEventRecord(
            position_event_id=event_id,
            root_event_id=root_id,
            supersedes_event_id=supersedes,
            monitoring_item_id="item-amd",
            event_order=order,
            event_action=action,
            position_effect=effect,
            trade_date=trade_date,
            quantity=quantity,
            execution_price=price,
            reference_close=price,
            execution_price_source="db_close_default",
            fee_usd=Decimal("0"),
            note="",
            command_id=f"command-{event_id}",
        )

    def test_record_trade_uses_close_default_and_replays_same_command(self) -> None:
        commands, persistence, schemas = _load_modules()
        repository = FakeRepository()
        item = self._stored_direct_item(persistence)
        repository.items[item.monitoring_item_id] = item
        value = schemas.PositionTradeInput(
            monitoring_item_id=item.monitoring_item_id,
            position_effect=schemas.PositionEffect.BUY,
            trade_date=date(2026, 7, 10),
            quantity=5,
            execution_price=Decimal("160"),
            fee_usd=Decimal("0"),
            note="추가매수",
        )
        command = self._command(
            schemas,
            "trade-1",
            schemas.CommandType.RECORD_POSITION_TRADE,
            target_id=item.monitoring_item_id,
            payload={"trade_date": "2026-07-10", "quantity": 5},
        )

        first = commands.execute_record_position_trade(
            repository,
            command,
            value,
            resolve_reference_close=lambda current, day: Decimal("160"),
            validate_candidate=lambda current, records: None,
        )
        replay = commands.execute_record_position_trade(
            repository,
            command,
            value,
            resolve_reference_close=lambda current, day: Decimal("160"),
            validate_candidate=lambda current, records: None,
        )

        self.assertFalse(first.replayed)
        self.assertTrue(replay.replayed)
        self.assertEqual(len(repository.position_events), 1)
        self.assertEqual(
            repository.position_events[0].execution_price_source,
            "db_close_default",
        )

    def test_manual_price_is_preserved_with_reference_close(self) -> None:
        commands, persistence, schemas = _load_modules()
        repository = FakeRepository()
        item = self._stored_direct_item(persistence)
        repository.items[item.monitoring_item_id] = item

        commands.execute_record_position_trade(
            repository,
            self._command(
                schemas,
                "trade-manual",
                schemas.CommandType.RECORD_POSITION_TRADE,
                target_id=item.monitoring_item_id,
            ),
            schemas.PositionTradeInput(
                monitoring_item_id=item.monitoring_item_id,
                position_effect=schemas.PositionEffect.BUY,
                trade_date=date(2026, 7, 10),
                quantity=5,
                execution_price=Decimal("159.25"),
            ),
            resolve_reference_close=lambda current, day: Decimal("160"),
            validate_candidate=lambda current, records: None,
        )

        row = repository.position_events[0]
        self.assertEqual(row.execution_price, Decimal("159.25"))
        self.assertEqual(row.reference_close, Decimal("160"))
        self.assertEqual(row.execution_price_source, "manual_override")

    def test_replace_rejects_stale_terminal_revision(self) -> None:
        commands, persistence, schemas = _load_modules()
        repository = FakeRepository()
        item = self._stored_direct_item(persistence)
        repository.items[item.monitoring_item_id] = item
        repository.position_events = [
            self._position_event(
                persistence, event_id="buy-v1", root_id="buy-root"
            ),
            self._position_event(
                persistence,
                event_id="buy-v2",
                root_id="buy-root",
                supersedes="buy-v1",
                action="replace",
                quantity=6,
            ),
        ]

        with self.assertRaisesRegex(commands.CommandConflictError, "최신 거래 기록"):
            commands.execute_replace_position_trade(
                repository,
                self._command(
                    schemas,
                    "replace-stale",
                    schemas.CommandType.REPLACE_POSITION_TRADE,
                    target_id=item.monitoring_item_id,
                ),
                schemas.ReplacePositionTradeInput(
                    monitoring_item_id=item.monitoring_item_id,
                    root_event_id="buy-root",
                    expected_event_id="buy-v1",
                    position_effect=schemas.PositionEffect.BUY,
                    trade_date=date(2026, 7, 10),
                    quantity=7,
                    execution_price=Decimal("100"),
                ),
                resolve_reference_close=lambda current, day: Decimal("100"),
                validate_candidate=lambda current, records: None,
            )
        self.assertEqual(len(repository.position_events), 2)

    def test_initial_correction_rolls_back_when_later_sell_becomes_invalid(self) -> None:
        commands, persistence, schemas = _load_modules()
        from app.services.portfolio_monitoring.position_events import (
            project_position_events,
            validate_position_sequence,
        )

        repository = FakeRepository()
        item = self._stored_direct_item(persistence, shares=30)
        repository.items[item.monitoring_item_id] = item
        repository.position_events = [
            self._position_event(
                persistence,
                event_id="sell-v1",
                root_id="sell-root",
                effect="sell",
                quantity=25,
            )
        ]

        def validate_candidate(current, records):
            projection = project_position_events(current, records)
            validate_position_sequence(current, projection, split_factors={})

        with self.assertRaisesRegex(ValueError, "최소 1주"):
            commands.execute_correct_initial_quantity(
                repository,
                self._command(
                    schemas,
                    "correct-invalid",
                    schemas.CommandType.CORRECT_INITIAL_QUANTITY,
                    target_id=item.monitoring_item_id,
                ),
                schemas.InitialQuantityCorrectionInput(
                    item.monitoring_item_id, 20, "입력 오류 수정"
                ),
                validate_candidate=validate_candidate,
            )
        self.assertEqual(len(repository.position_events), 1)
        self.assertNotIn("correct-invalid", repository.commands)

    def test_replace_and_void_append_revisions_without_changing_root_order(self) -> None:
        commands, persistence, schemas = _load_modules()
        repository = FakeRepository()
        item = self._stored_direct_item(persistence)
        repository.items[item.monitoring_item_id] = item
        original = self._position_event(
            persistence,
            event_id="buy-v1",
            root_id="buy-root",
            order=4,
        )
        repository.position_events = [original]

        replaced = commands.execute_replace_position_trade(
            repository,
            self._command(
                schemas,
                "replace-buy",
                schemas.CommandType.REPLACE_POSITION_TRADE,
                target_id=item.monitoring_item_id,
            ),
            schemas.ReplacePositionTradeInput(
                monitoring_item_id=item.monitoring_item_id,
                root_event_id="buy-root",
                expected_event_id="buy-v1",
                position_effect=schemas.PositionEffect.BUY,
                trade_date=date(2026, 7, 11),
                quantity=7,
                execution_price=Decimal("101"),
            ),
            resolve_reference_close=lambda current, day: Decimal("102"),
            validate_candidate=lambda current, records: None,
        )
        replacement = repository.position_events[-1]
        self.assertEqual(replaced.target_id, "buy-root")
        self.assertEqual(replacement.event_order, 4)
        self.assertEqual(replacement.supersedes_event_id, "buy-v1")
        self.assertEqual(replacement.execution_price_source, "manual_override")

        commands.execute_void_position_trade(
            repository,
            self._command(
                schemas,
                "void-buy",
                schemas.CommandType.VOID_POSITION_TRADE,
                target_id=item.monitoring_item_id,
            ),
            schemas.VoidPositionTradeInput(
                monitoring_item_id=item.monitoring_item_id,
                root_event_id="buy-root",
                expected_event_id=replacement.position_event_id,
            ),
            validate_candidate=lambda current, records: None,
        )
        voided = repository.position_events[-1]
        self.assertEqual(voided.event_action, "void")
        self.assertEqual(voided.event_order, 4)
        self.assertIsNone(voided.execution_price)
        self.assertIsNone(voided.reference_close)

    def test_trade_input_rejects_nonpositive_net_sell_proceeds(self) -> None:
        _, _, schemas = _load_modules()
        value = schemas.PositionTradeInput(
            monitoring_item_id="item-amd",
            position_effect=schemas.PositionEffect.SELL,
            trade_date=date(2026, 7, 10),
            quantity=1,
            execution_price=Decimal("10"),
            fee_usd=Decimal("10"),
        )

        with self.assertRaisesRegex(ValueError, "withdrawal must be positive"):
            schemas.validate_position_trade_input(value)

    def test_default_group_is_created_exactly_once(self) -> None:
        commands, _, _ = _load_modules()
        repository = FakeRepository()

        first = commands.ensure_default_group(repository)
        second = commands.ensure_default_group(repository)

        self.assertEqual(first.portfolio_group_id, second.portfolio_group_id)
        self.assertEqual(first.name, "기본 포트폴리오")
        self.assertTrue(first.is_default)
        self.assertEqual(len(repository.groups), 1)

    def test_create_group_rejects_blank_and_duplicate_names(self) -> None:
        commands, _, schemas = _load_modules()
        repository = FakeRepository()
        commands.ensure_default_group(repository)

        blank = self._command(
            schemas,
            "cmd-blank",
            schemas.CommandType.CREATE_GROUP,
            payload={"name": "   "},
        )
        with self.assertRaisesRegex(commands.CommandValidationError, "name is required"):
            commands.execute_create_group(repository, blank)
        self.assertNotIn("cmd-blank", repository.commands)

        created = commands.execute_create_group(
            repository,
            self._command(
                schemas,
                "cmd-create-growth",
                schemas.CommandType.CREATE_GROUP,
                payload={"name": "Growth"},
            ),
        )
        self.assertEqual(created.status, schemas.CommandStatus.SUCCEEDED)

        duplicate = self._command(
            schemas,
            "cmd-create-growth-2",
            schemas.CommandType.CREATE_GROUP,
            payload={"name": " growth "},
        )
        with self.assertRaisesRegex(commands.CommandValidationError, "already exists"):
            commands.execute_create_group(repository, duplicate)
        self.assertNotIn("cmd-create-growth-2", repository.commands)

    def test_rename_group_uses_optimistic_version(self) -> None:
        commands, _, schemas = _load_modules()
        repository = FakeRepository()
        group = commands.ensure_default_group(repository)

        result = commands.execute_rename_group(
            repository,
            self._command(
                schemas,
                "cmd-rename",
                schemas.CommandType.RENAME_GROUP,
                target_id=group.portfolio_group_id,
                payload={"name": "Core"},
                expected_version=1,
            ),
        )
        renamed = repository.groups[result.target_id]
        self.assertEqual(renamed.name, "Core")
        self.assertEqual(renamed.version, 2)

        stale = self._command(
            schemas,
            "cmd-rename-stale",
            schemas.CommandType.RENAME_GROUP,
            target_id=group.portfolio_group_id,
            payload={"name": "Stale"},
            expected_version=1,
        )
        with self.assertRaisesRegex(commands.CommandConflictError, "version conflict"):
            commands.execute_rename_group(repository, stale)
        self.assertEqual(repository.groups[group.portfolio_group_id].name, "Core")
        self.assertNotIn("cmd-rename-stale", repository.commands)

    def test_same_command_replays_and_changed_request_is_rejected(self) -> None:
        commands, _, schemas = _load_modules()
        repository = FakeRepository()
        command = self._command(
            schemas,
            "cmd-idempotent",
            schemas.CommandType.CREATE_GROUP,
            payload={"name": "Income"},
        )

        first = commands.execute_create_group(repository, command)
        second = commands.execute_create_group(repository, command)

        self.assertFalse(first.replayed)
        self.assertTrue(second.replayed)
        self.assertEqual(first.target_id, second.target_id)
        self.assertEqual(len(repository.groups), 1)

        changed = self._command(
            schemas,
            "cmd-idempotent",
            schemas.CommandType.CREATE_GROUP,
            payload={"name": "Changed"},
        )
        with self.assertRaisesRegex(commands.CommandConflictError, "different request"):
            commands.execute_create_group(repository, changed)

    def test_add_item_rejects_duplicate_active_source_and_maximum_ten(self) -> None:
        commands, persistence, schemas = _load_modules()
        repository = FakeRepository()
        group = commands.ensure_default_group(repository)

        def resolve_entry(item):
            return commands.EntryResolution(
                effective_start_date=date(2026, 7, 1),
                entry_close=Decimal("100"),
                initial_capital=item.input_notional or Decimal("0"),
            )

        first_item = self._direct_item(schemas, group_id=group.portfolio_group_id)
        commands.execute_add_item(
            repository,
            self._command(schemas, "cmd-add-aapl", schemas.CommandType.ADD_ITEM),
            first_item,
            resolve_entry=resolve_entry,
        )
        duplicate = self._direct_item(schemas, group_id=group.portfolio_group_id)
        with self.assertRaisesRegex(commands.CommandValidationError, "already active"):
            commands.execute_add_item(
                repository,
                self._command(schemas, "cmd-add-aapl-2", schemas.CommandType.ADD_ITEM),
                duplicate,
                resolve_entry=resolve_entry,
            )

        for index in range(1, 10):
            symbol = f"SYM{index}"
            commands.execute_add_item(
                repository,
                self._command(schemas, f"cmd-add-{symbol}", schemas.CommandType.ADD_ITEM),
                self._direct_item(schemas, group_id=group.portfolio_group_id, symbol=symbol),
                resolve_entry=resolve_entry,
            )
        self.assertEqual(
            len(repository.list_items(group.portfolio_group_id, statuses={"active", "data_review"})),
            10,
        )

        with self.assertRaisesRegex(commands.CommandValidationError, "maximum 10"):
            commands.execute_add_item(
                repository,
                self._command(schemas, "cmd-add-eleven", schemas.CommandType.ADD_ITEM),
                self._direct_item(schemas, group_id=group.portfolio_group_id, symbol="ELEVEN"),
                resolve_entry=resolve_entry,
            )
        self.assertNotIn("cmd-add-eleven", repository.commands)

        ended = next(iter(repository.items.values()))
        repository.items[ended.monitoring_item_id] = replace(ended, status="ended")
        replacement = commands.execute_add_item(
            repository,
            self._command(schemas, "cmd-add-after-end", schemas.CommandType.ADD_ITEM),
            self._direct_item(schemas, group_id=group.portfolio_group_id, symbol="NEW"),
            resolve_entry=resolve_entry,
        )
        self.assertEqual(replacement.status, schemas.CommandStatus.SUCCEEDED)
        self.assertIsInstance(repository.items[replacement.target_id], persistence.MonitoringItemRecord)

    def test_failed_item_insert_rolls_back_pending_command(self) -> None:
        commands, _, schemas = _load_modules()
        repository = FakeRepository()
        group = commands.ensure_default_group(repository)
        repository.fail_item_insert = True

        with self.assertRaisesRegex(RuntimeError, "injected item insert failure"):
            commands.execute_add_item(
                repository,
                self._command(schemas, "cmd-add-fail", schemas.CommandType.ADD_ITEM),
                self._direct_item(schemas, group_id=group.portfolio_group_id),
                resolve_entry=lambda item: commands.EntryResolution(
                    effective_start_date=date(2026, 7, 1),
                    entry_close=Decimal("100"),
                    initial_capital=Decimal("10000"),
                ),
            )

        self.assertNotIn("cmd-add-fail", repository.commands)
        self.assertEqual(repository.rollback_count, 1)

    def test_end_item_preserves_record_and_converts_status(self) -> None:
        commands, _, schemas = _load_modules()
        repository = FakeRepository()
        group = commands.ensure_default_group(repository)
        added = commands.execute_add_item(
            repository,
            self._command(schemas, "cmd-add-endable", schemas.CommandType.ADD_ITEM),
            self._direct_item(schemas, group_id=group.portfolio_group_id),
            resolve_entry=lambda item: commands.EntryResolution(
                effective_start_date=date(2026, 7, 1),
                entry_close=Decimal("100"),
                initial_capital=Decimal("10000"),
            ),
        )

        ended = commands.execute_end_item(
            repository,
            self._command(
                schemas,
                "cmd-end-item",
                schemas.CommandType.END_ITEM,
                target_id=added.target_id,
            ),
            resolve_end=lambda item: commands.EndResolution(
                requested_end_date=date(2026, 7, 18),
                effective_end_date=date(2026, 7, 17),
                exit_value=Decimal("10500"),
            ),
        )

        item = repository.items[ended.target_id]
        self.assertEqual(item.status, "ended")
        self.assertEqual(item.exit_value, Decimal("10500"))
        self.assertEqual(len(repository.items), 1)
        self.assertIn("요청일 2026-07-18", ended.message)
        self.assertIn("적용일 2026-07-17", ended.message)
        self.assertIn("$10,500.00", ended.message)

    def test_reopen_item_cancels_end_on_the_same_tracking_record(self) -> None:
        commands, _, schemas = _load_modules()
        repository = FakeRepository()
        group = commands.ensure_default_group(repository)
        added = commands.execute_add_item(
            repository,
            self._command(schemas, "cmd-add-reopenable", schemas.CommandType.ADD_ITEM),
            self._direct_item(schemas, group_id=group.portfolio_group_id),
            resolve_entry=lambda item: commands.EntryResolution(
                effective_start_date=date(2026, 7, 1),
                entry_close=Decimal("100"),
                initial_capital=Decimal("10000"),
            ),
        )
        commands.execute_end_item(
            repository,
            self._command(
                schemas,
                "cmd-end-before-reopen",
                schemas.CommandType.END_ITEM,
                target_id=added.target_id,
            ),
            resolve_end=lambda item: commands.EndResolution(
                requested_end_date=date(2026, 7, 18),
                effective_end_date=date(2026, 7, 17),
                exit_value=Decimal("10500"),
            ),
        )

        reopen_command = self._command(
            schemas,
            "cmd-reopen-item",
            schemas.CommandType.REOPEN_ITEM,
            target_id=added.target_id,
        )
        reopened = commands.execute_reopen_item(
            repository,
            reopen_command,
        )
        replayed = commands.execute_reopen_item(repository, reopen_command)

        item = repository.items[reopened.target_id]
        self.assertEqual(reopened.target_id, added.target_id)
        self.assertEqual(item.status, "active")
        self.assertIsNone(item.tracking_end_requested_date)
        self.assertIsNone(item.tracking_end_effective_date)
        self.assertIsNone(item.exit_value)
        self.assertEqual(item.effective_start_date, date(2026, 7, 1))
        self.assertEqual(item.initial_capital, Decimal("10000"))
        self.assertEqual(len(repository.items), 1)
        self.assertIn("추적 종료를 취소했습니다", reopened.message)
        self.assertTrue(replayed.replayed)
        self.assertEqual(replayed.target_id, added.target_id)

    def test_reopen_item_rejects_duplicate_active_source(self) -> None:
        commands, persistence, schemas = _load_modules()
        repository = FakeRepository()
        group = commands.ensure_default_group(repository)
        ended = persistence.MonitoringItemRecord(
            monitoring_item_id="item-ended-aapl",
            portfolio_group_id=group.portfolio_group_id,
            source_type="direct_security",
            source_ref="AAPL",
            instrument_kind="stock",
            requested_start_date=date(2026, 6, 1),
            effective_start_date=date(2026, 6, 1),
            funding_mode="fixed_notional",
            input_notional=Decimal("10000"),
            input_shares=None,
            entry_close=Decimal("100"),
            initial_capital=Decimal("10000"),
            tracking_end_requested_date=date(2026, 6, 30),
            tracking_end_effective_date=date(2026, 6, 30),
            exit_value=Decimal("10100"),
            status="ended",
        )
        active = replace(ended, monitoring_item_id="item-active-aapl", status="active")
        repository.items = {ended.monitoring_item_id: ended, active.monitoring_item_id: active}

        with self.assertRaisesRegex(commands.CommandValidationError, "already active"):
            commands.execute_reopen_item(
                repository,
                self._command(
                    schemas,
                    "cmd-reopen-duplicate",
                    schemas.CommandType.REOPEN_ITEM,
                    target_id=ended.monitoring_item_id,
                ),
            )

    def test_reopen_item_rejects_group_with_ten_active_items(self) -> None:
        commands, persistence, schemas = _load_modules()
        repository = FakeRepository()
        group = commands.ensure_default_group(repository)
        base = persistence.MonitoringItemRecord(
            monitoring_item_id="item-ended",
            portfolio_group_id=group.portfolio_group_id,
            source_type="direct_security",
            source_ref="ENDED",
            instrument_kind="stock",
            requested_start_date=date(2026, 6, 1),
            effective_start_date=date(2026, 6, 1),
            funding_mode="fixed_notional",
            input_notional=Decimal("10000"),
            input_shares=None,
            entry_close=Decimal("100"),
            initial_capital=Decimal("10000"),
            status="ended",
        )
        repository.items[base.monitoring_item_id] = base
        for index in range(10):
            item = replace(
                base,
                monitoring_item_id=f"item-active-{index}",
                source_ref=f"SYM{index}",
                status="active",
            )
            repository.items[item.monitoring_item_id] = item

        with self.assertRaisesRegex(commands.CommandValidationError, "maximum of 10"):
            commands.execute_reopen_item(
                repository,
                self._command(
                    schemas,
                    "cmd-reopen-full",
                    schemas.CommandType.REOPEN_ITEM,
                    target_id=base.monitoring_item_id,
                ),
            )

    def test_reopen_item_rejects_an_item_that_is_not_ended(self) -> None:
        commands, persistence, schemas = _load_modules()
        repository = FakeRepository()
        group = commands.ensure_default_group(repository)
        active = persistence.MonitoringItemRecord(
            monitoring_item_id="item-active",
            portfolio_group_id=group.portfolio_group_id,
            source_type="direct_security",
            source_ref="AAPL",
            instrument_kind="stock",
            requested_start_date=date(2026, 7, 1),
            effective_start_date=date(2026, 7, 1),
            funding_mode="fixed_notional",
            input_notional=Decimal("10000"),
            input_shares=None,
            entry_close=Decimal("100"),
            initial_capital=Decimal("10000"),
            status="active",
        )
        repository.items[active.monitoring_item_id] = active

        with self.assertRaisesRegex(commands.CommandValidationError, "Only an ended"):
            commands.execute_reopen_item(
                repository,
                self._command(
                    schemas,
                    "cmd-reopen-active",
                    schemas.CommandType.REOPEN_ITEM,
                    target_id=active.monitoring_item_id,
                ),
            )

    def test_mysql_repository_reopen_item_clears_end_fields(self) -> None:
        _, persistence, _ = _load_modules()
        db = RecordingDb()
        repository = persistence.MySQLMonitoringRepository(lambda: db)
        ended = persistence.MonitoringItemRecord(
            monitoring_item_id="item-ended",
            portfolio_group_id="group-a",
            source_type="direct_security",
            source_ref="AAPL",
            instrument_kind="stock",
            requested_start_date=date(2026, 7, 1),
            effective_start_date=date(2026, 7, 1),
            funding_mode="fixed_notional",
            input_notional=Decimal("10000"),
            input_shares=None,
            entry_close=Decimal("100"),
            initial_capital=Decimal("10000"),
            tracking_end_requested_date=date(2026, 7, 18),
            tracking_end_effective_date=date(2026, 7, 17),
            exit_value=Decimal("10500"),
            status="ended",
        )
        reopened = replace(
            ended,
            tracking_end_requested_date=None,
            tracking_end_effective_date=None,
            exit_value=None,
            status="active",
        )

        with patch.object(repository, "get_item", side_effect=[ended, reopened]):
            result = repository.reopen_item(ended.monitoring_item_id)

        self.assertEqual(result, reopened)
        self.assertEqual(db.used_databases, ["finance_meta"])
        self.assertEqual(db.executed[0][1], [ended.monitoring_item_id])
        normalized_sql = " ".join(db.executed[0][0].split())
        self.assertIn("tracking_end_requested_date = NULL", normalized_sql)
        self.assertIn("tracking_end_effective_date = NULL", normalized_sql)
        self.assertIn("exit_value = NULL", normalized_sql)
        self.assertIn("status = 'active'", normalized_sql)
        self.assertTrue(db.closed)

    def test_mysql_repository_ensure_schema_uses_finance_meta(self) -> None:
        _, persistence, _ = _load_modules()
        db = RecordingDb()
        repository = persistence.MySQLMonitoringRepository(lambda: db)

        repository.ensure_schema()

        self.assertEqual(db.used_databases, ["finance_meta"])
        self.assertEqual(len(db.executed), len(persistence.PORTFOLIO_MONITORING_SCHEMAS))
        self.assertTrue(all("CREATE TABLE IF NOT EXISTS" in sql for sql, _ in db.executed))
        self.assertTrue(
            all(
                table_name in sql
                for table_name, (sql, _) in zip(
                    persistence.PORTFOLIO_MONITORING_SCHEMAS,
                    db.executed,
                    strict=True,
                )
            )
        )
        self.assertTrue(db.closed)


if __name__ == "__main__":
    unittest.main()
