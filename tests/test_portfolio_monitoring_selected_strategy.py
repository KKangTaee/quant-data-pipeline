from __future__ import annotations

import importlib
import unittest
from datetime import date
from decimal import Decimal

import pandas as pd

from app.services.portfolio_monitoring.persistence import MonitoringItemRecord


def _load_selected_strategy():
    try:
        return importlib.import_module("app.services.portfolio_monitoring.selected_strategy")
    except ModuleNotFoundError as exc:
        raise AssertionError("portfolio monitoring selected-strategy adapter is required") from exc


class PortfolioMonitoringSelectedStrategyTests(unittest.TestCase):
    def _item(self, *, funding_mode="fixed_notional") -> MonitoringItemRecord:
        return MonitoringItemRecord(
            monitoring_item_id="item-strategy",
            portfolio_group_id="group-core",
            source_type="selected_strategy",
            source_ref="decision-ready",
            instrument_kind="strategy",
            requested_start_date=date(2026, 7, 1),
            effective_start_date=date(2026, 7, 1),
            funding_mode=funding_mode,
            input_notional=Decimal("10000") if funding_mode == "fixed_notional" else None,
            input_shares=3 if funding_mode == "fixed_shares" else None,
            entry_close=Decimal("1"),
            initial_capital=Decimal("10000"),
        )

    @staticmethod
    def _decision_rows():
        return [
            {
                "decision_id": "decision-ready",
                "monitoring_candidate": True,
                "source_title": "Selected Strategy",
                "updated_at": "2026-07-18T10:00:00",
                "selected_components": [{"registry_id": "candidate-a", "target_weight": 100.0}],
            }
        ]

    def test_valid_replay_is_normalized_then_scaled_by_fixed_notional(self) -> None:
        selected = _load_selected_strategy()
        calls = []

        def replay(row, *, start, end, initial_capital):
            calls.append((row["decision_id"], start, end, initial_capital))
            return {
                "status": "ok",
                "blockers": [],
                "portfolio_result_df": pd.DataFrame(
                    {
                        "Date": ["2026-07-01", "2026-07-02"],
                        "Total Balance": [200.0, 220.0],
                    }
                ),
            }

        adapter = selected.SelectedStrategyReplayAdapter(
            decision_loader=self._decision_rows,
            replay_runner=replay,
        )
        lane = adapter.build_value_lane(self._item(), end_date=date(2026, 7, 2))

        self.assertEqual(calls, [("decision-ready", "2026-07-01", "2026-07-02", 10000.0)])
        self.assertEqual(lane.curve["total_value"].tolist(), [10000.0, 11000.0])
        self.assertEqual(lane.readiness.status, "READY")
        self.assertEqual(lane.readiness.source_dates["decision_updated_at"], "2026-07-18T10:00:00")

    def test_missing_decision_returns_blocked_contract(self) -> None:
        selected = _load_selected_strategy()
        adapter = selected.SelectedStrategyReplayAdapter(
            decision_loader=lambda: [],
            replay_runner=lambda *args, **kwargs: {},
        )

        contract = adapter.load_candidate_contract("decision-missing")

        self.assertEqual(contract.readiness.status, "BLOCKED")
        self.assertIn("Final Review decision", contract.readiness.blockers[0])

    def test_missing_replay_contract_is_blocked_before_replay(self) -> None:
        selected = _load_selected_strategy()
        calls = []
        adapter = selected.SelectedStrategyReplayAdapter(
            decision_loader=lambda: [
                {
                    "decision_id": "decision-ready",
                    "monitoring_candidate": True,
                    "selected_components": [],
                }
            ],
            replay_runner=lambda *args, **kwargs: calls.append(True),
        )

        contract = adapter.load_candidate_contract("decision-ready")

        self.assertEqual(contract.readiness.status, "BLOCKED")
        self.assertIn("replay contract", contract.readiness.blockers[0])
        self.assertEqual(calls, [])

    def test_newer_hold_locks_existing_selected_strategy(self) -> None:
        selected = _load_selected_strategy()
        adapter = selected.SelectedStrategyReplayAdapter(
            decision_loader=lambda: [
                {
                    "decision_id": "new-hold",
                    "selection_source_id": "selection-a",
                    "source_id": "validation-new-hold",
                    "updated_at": "2026-07-23",
                    "decision_route": "HOLD_FOR_MORE_PAPER_TRACKING",
                    "monitoring_candidate": False,
                },
                {
                    "decision_id": "old-selected",
                    "selection_source_id": "selection-a",
                    "source_id": "validation-old-selected",
                    "updated_at": "2026-07-22",
                    "decision_route": "SELECT_FOR_PRACTICAL_PORTFOLIO",
                    "monitoring_candidate": True,
                    "selected_components": [
                        {"registry_id": "candidate-a", "target_weight": 100.0}
                    ],
                },
            ]
        )

        contract = adapter.load_candidate_contract("old-selected")

        self.assertEqual(contract.readiness.status, "BLOCKED")
        self.assertEqual(
            contract.readiness.decision_lifecycle["state"],
            "TRACKING_ELIGIBILITY_CHANGED",
        )
        self.assertIsNotNone(contract.decision_row)
        self.assertEqual(contract.decision_row["decision_id"], "new-hold")

    def test_newer_selected_row_reactivates_old_monitoring_reference(self) -> None:
        selected = _load_selected_strategy()
        adapter = selected.SelectedStrategyReplayAdapter(
            decision_loader=lambda: [
                {
                    "decision_id": "new-selected",
                    "selection_source_id": "selection-a",
                    "updated_at": "2026-07-23",
                    "decision_route": "SELECT_FOR_PRACTICAL_PORTFOLIO",
                    "monitoring_candidate": True,
                    "selected_components": [
                        {"registry_id": "candidate-new", "target_weight": 100.0}
                    ],
                },
                {
                    "decision_id": "old-selected",
                    "selection_source_id": "selection-a",
                    "updated_at": "2026-07-22",
                    "decision_route": "SELECT_FOR_PRACTICAL_PORTFOLIO",
                    "monitoring_candidate": True,
                    "selected_components": [
                        {"registry_id": "candidate-old", "target_weight": 100.0}
                    ],
                },
            ]
        )

        contract = adapter.load_candidate_contract("old-selected")

        self.assertEqual(contract.readiness.status, "READY")
        self.assertIsNotNone(contract.decision_row)
        self.assertEqual(contract.decision_row["decision_id"], "new-selected")
        self.assertEqual(
            contract.readiness.source_dates["effective_decision_id"],
            "new-selected",
        )

    def test_replay_failure_surfaces_blocked_readiness(self) -> None:
        selected = _load_selected_strategy()
        adapter = selected.SelectedStrategyReplayAdapter(
            decision_loader=self._decision_rows,
            replay_runner=lambda *args, **kwargs: {
                "status": "error",
                "error": "provider history missing",
                "blockers": ["candidate-a unavailable"],
            },
        )

        with self.assertRaises(selected.SelectedStrategyReplayError) as captured:
            adapter.build_value_lane(self._item(), end_date=date(2026, 7, 2))

        self.assertEqual(captured.exception.readiness.status, "BLOCKED")
        self.assertIn("provider history missing", captured.exception.readiness.blockers)
        self.assertIn("candidate-a unavailable", captured.exception.readiness.blockers)

    def test_share_mode_is_rejected_for_selected_strategy(self) -> None:
        selected = _load_selected_strategy()
        adapter = selected.SelectedStrategyReplayAdapter(
            decision_loader=self._decision_rows,
            replay_runner=lambda *args, **kwargs: {},
        )

        with self.assertRaisesRegex(selected.SelectedStrategyInputError, "fixed notional"):
            adapter.build_value_lane(
                self._item(funding_mode="fixed_shares"),
                end_date=date(2026, 7, 2),
            )


if __name__ == "__main__":
    unittest.main()
