from __future__ import annotations

import copy
import importlib
import unittest
from contextlib import contextmanager
from dataclasses import replace
from datetime import date
from decimal import Decimal


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
        self.transaction_count = 0
        self.rollback_count = 0
        self.fail_item_insert = False

    @contextmanager
    def transaction(self):
        snapshot = copy.deepcopy((self.groups, self.items, self.commands))
        self.transaction_count += 1
        try:
            yield self
        except Exception:
            self.groups, self.items, self.commands = snapshot
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

    def test_mysql_repository_ensure_schema_uses_finance_meta(self) -> None:
        _, persistence, _ = _load_modules()
        db = RecordingDb()
        repository = persistence.MySQLMonitoringRepository(lambda: db)

        repository.ensure_schema()

        self.assertEqual(db.used_databases, ["finance_meta"])
        self.assertEqual(len(db.executed), 3)
        self.assertTrue(all("CREATE TABLE IF NOT EXISTS" in sql for sql, _ in db.executed))
        self.assertTrue(db.closed)


if __name__ == "__main__":
    unittest.main()
