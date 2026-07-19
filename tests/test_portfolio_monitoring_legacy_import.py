from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from tests.test_portfolio_monitoring_commands import FakeRepository


FIXTURE_PATH = Path("tests/fixtures/selected_dashboard_portfolios_legacy.jsonl")


def _candidate_rows():
    return [
        {
            "decision_id": "decision-valid",
            "monitoring_candidate": True,
            "source_title": "Core GRS",
        },
        {
            "decision_id": "decision-valid-2",
            "monitoring_candidate": True,
            "source_title": "Satellite GRS",
        },
        {
            "decision_id": "decision-not-monitorable",
            "monitoring_candidate": False,
            "source_title": "Rejected",
        },
    ]


def _load_import_api():
    from app.services.portfolio_monitoring import persistence

    if not hasattr(persistence, "build_legacy_import_plan"):
        raise AssertionError("build_legacy_import_plan is required")
    if not hasattr(persistence, "import_legacy_portfolios"):
        raise AssertionError("import_legacy_portfolios is required")
    return persistence.build_legacy_import_plan, persistence.import_legacy_portfolios


class PortfolioMonitoringLegacyImportTests(unittest.TestCase):
    def test_group_schema_has_legacy_provenance_storage(self) -> None:
        from finance.data.db.schema import PORTFOLIO_MONITORING_SCHEMAS

        group_sql = PORTFOLIO_MONITORING_SCHEMAS["monitoring_portfolio_group"]
        self.assertIn("metadata_json JSON NULL", group_sql)

    def test_dry_run_reports_create_skip_and_block_counts_without_writing(self) -> None:
        build_legacy_import_plan, _ = _load_import_api()

        repository = FakeRepository()
        source_before = FIXTURE_PATH.read_bytes()

        plan = build_legacy_import_plan(FIXTURE_PATH, _candidate_rows())

        self.assertEqual(plan.group_create_count, 2)
        self.assertEqual(plan.item_create_count, 2)
        self.assertEqual(plan.duplicate_item_count, 1)
        self.assertEqual(plan.blocked_item_count, 1)
        self.assertEqual(
            {issue.code for issue in plan.issues},
            {"duplicate_source", "missing_monitoring_candidate"},
        )
        self.assertEqual(repository.groups, {})
        self.assertEqual(repository.items, {})
        self.assertEqual(repository.commands, {})
        self.assertEqual(FIXTURE_PATH.read_bytes(), source_before)
        self.assertEqual(
            plan.source_fingerprint,
            hashlib.sha256(source_before).hexdigest(),
        )

    def test_invalid_capital_blocks_only_the_legacy_slot(self) -> None:
        build_legacy_import_plan, _ = _load_import_api()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "invalid-capital.jsonl"
            path.write_text(
                '{"portfolio_id":"legacy-invalid","name":"Invalid",'
                '"strategy_slots":[{"slot_id":"slot-invalid",'
                '"decision_id":"decision-valid","start":"2024-01-02",'
                '"initial_capital":null}]}\n',
                encoding="utf-8",
            )

            plan = build_legacy_import_plan(path, _candidate_rows())

        self.assertEqual(plan.group_create_count, 1)
        self.assertEqual(plan.item_create_count, 0)
        self.assertEqual(plan.blocked_item_count, 1)
        self.assertEqual(plan.issues[0].code, "invalid_legacy_slot")

    def test_import_is_idempotent_and_preserves_group_and_item_provenance(self) -> None:
        build_legacy_import_plan, import_legacy_portfolios = _load_import_api()

        repository = FakeRepository()
        source_before = FIXTURE_PATH.read_bytes()
        plan = build_legacy_import_plan(FIXTURE_PATH, _candidate_rows())

        first = import_legacy_portfolios(repository, plan, command_id="legacy-import-v1")

        self.assertEqual(first.groups_created, 2)
        self.assertEqual(first.groups_replayed, 0)
        self.assertEqual(first.items_created, 2)
        self.assertEqual(first.items_replayed, 0)
        self.assertEqual(first.items_blocked, 1)
        self.assertEqual(first.items_skipped, 1)
        self.assertEqual(len(repository.groups), 2)
        self.assertEqual(len(repository.items), 2)
        self.assertEqual(len(repository.commands), 4)

        group_by_legacy_id = {
            group.metadata["legacy_portfolio_id"]: group
            for group in repository.groups.values()
        }
        self.assertEqual(set(group_by_legacy_id), {"legacy-core", "legacy-satellite"})
        self.assertTrue(
            all(
                group.metadata["legacy_source_fingerprint"] == plan.source_fingerprint
                for group in group_by_legacy_id.values()
            )
        )

        item_by_decision = {item.source_ref: item for item in repository.items.values()}
        core = item_by_decision["decision-valid"]
        self.assertEqual(core.source_type, "selected_strategy")
        self.assertEqual(core.instrument_kind, "strategy")
        self.assertEqual(core.funding_mode, "fixed_notional")
        self.assertEqual(str(core.input_notional), "10000.0")
        self.assertIsNone(core.input_shares)
        self.assertEqual(core.metadata["legacy_slot_id"], "slot-valid")
        self.assertEqual(core.metadata["legacy_decision_id"], "decision-valid")
        self.assertEqual(core.metadata["legacy_memo"], "core sleeve")
        self.assertEqual(core.metadata["legacy_use_latest_end"], True)

        second = import_legacy_portfolios(repository, plan, command_id="legacy-import-v1")

        self.assertEqual(second.groups_created, 0)
        self.assertEqual(second.groups_replayed, 2)
        self.assertEqual(second.items_created, 0)
        self.assertEqual(second.items_replayed, 2)
        self.assertEqual(len(repository.groups), 2)
        self.assertEqual(len(repository.items), 2)
        self.assertEqual(len(repository.commands), 4)
        self.assertEqual(FIXTURE_PATH.read_bytes(), source_before)

    def test_missing_decision_blocks_only_the_item_not_its_group(self) -> None:
        build_legacy_import_plan, import_legacy_portfolios = _load_import_api()

        repository = FakeRepository()
        plan = build_legacy_import_plan(FIXTURE_PATH, _candidate_rows())
        result = import_legacy_portfolios(repository, plan, command_id="legacy-import-v1")

        core_group_id = result.group_ids_by_legacy_id["legacy-core"]
        core_items = repository.list_items(core_group_id)
        self.assertEqual([item.source_ref for item in core_items], ["decision-valid"])
        self.assertNotIn("decision-missing", {item.source_ref for item in repository.items.values()})
        self.assertIn(
            "missing_monitoring_candidate",
            {issue.code for issue in result.issues},
        )


if __name__ == "__main__":
    unittest.main()
