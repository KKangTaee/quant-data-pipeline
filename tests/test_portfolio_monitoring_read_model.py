from __future__ import annotations

import importlib
import unittest
from datetime import date, datetime
from decimal import Decimal

import pandas as pd

from app.services.portfolio_monitoring.persistence import MonitoringItemRecord, PortfolioGroupRecord
from app.services.portfolio_monitoring.valuation import CorporateActionReview, ItemValueLane
from app.services.portfolio_monitoring.macro_context import MacroContext, MacroObservation


def _load_read_model():
    try:
        return importlib.import_module("app.services.portfolio_monitoring.read_model")
    except ModuleNotFoundError as exc:
        raise AssertionError("portfolio monitoring read-model module is required") from exc


def _item(
    item_id: str,
    *,
    requested: date,
    effective: date,
    capital: str = "100",
    status: str = "active",
    end: date | None = None,
    exit_value: str | None = None,
) -> MonitoringItemRecord:
    return MonitoringItemRecord(
        monitoring_item_id=item_id,
        portfolio_group_id="group-core",
        source_type="direct_security",
        source_ref=item_id.upper(),
        instrument_kind="stock",
        requested_start_date=requested,
        effective_start_date=effective,
        funding_mode="fixed_notional",
        input_notional=Decimal(capital),
        input_shares=None,
        entry_close=Decimal("10"),
        initial_capital=Decimal(capital),
        tracking_end_requested_date=end,
        tracking_end_effective_date=end,
        exit_value=Decimal(exit_value) if exit_value is not None else None,
        status=status,
    )


def _lane(item: MonitoringItemRecord, rows: list[tuple[str, float]]) -> ItemValueLane:
    frame = pd.DataFrame(rows, columns=["date", "total_value"])
    frame["date"] = pd.to_datetime(frame["date"])
    frame["data_status"] = item.status
    return ItemValueLane(
        monitoring_item_id=item.monitoring_item_id,
        source_ref=item.source_ref,
        effective_start_date=frame.iloc[0]["date"].date(),
        latest_usable_date=frame.iloc[-1]["date"].date(),
        initial_capital=item.initial_capital,
        status=item.status,
        curve=frame,
        review=CorporateActionReview("READY", Decimal("0"), Decimal("0"), ()),
    )


class FakeRepository:
    def __init__(self, groups, items):
        self.groups = groups
        self.items = items

    def list_groups(self, *, include_deleted=False):
        return list(self.groups)

    def list_items(self, portfolio_group_id, *, statuses=None):
        rows = [row for row in self.items if row.portfolio_group_id == portfolio_group_id]
        if statuses is not None:
            rows = [row for row in rows if row.status in statuses]
        return rows


class PortfolioMonitoringReadModelTests(unittest.TestCase):
    def test_alignment_keeps_pre_start_and_post_end_capital_as_cash(self) -> None:
        read_model = _load_read_model()
        active = _item("a", requested=date(2026, 7, 1), effective=date(2026, 7, 2))
        ended = _item(
            "b",
            requested=date(2026, 7, 1),
            effective=date(2026, 7, 3),
            status="ended",
            end=date(2026, 7, 3),
            exit_value="120",
        )

        result = read_model.align_group_value_lanes(
            [active, ended],
            {
                "a": _lane(active, [("2026-07-02", 110), ("2026-07-04", 130)]),
                "b": _lane(ended, [("2026-07-03", 120)]),
            },
        )
        curve = result.curve.set_index("date")

        self.assertEqual(result.basis_date, date(2026, 7, 4))
        self.assertEqual(curve.loc[pd.Timestamp("2026-07-01"), "item:a"], 100.0)
        self.assertEqual(curve.loc[pd.Timestamp("2026-07-01"), "item:b"], 100.0)
        self.assertEqual(curve.loc[pd.Timestamp("2026-07-04"), "item:b"], 120.0)
        self.assertEqual(result.active_item_count, 1)
        self.assertEqual(result.history_item_count, 2)

    def test_stale_active_lane_moves_common_basis_back_without_interpolation(self) -> None:
        read_model = _load_read_model()
        first = _item("first", requested=date(2026, 7, 1), effective=date(2026, 7, 1))
        later = _item("later", requested=date(2026, 7, 1), effective=date(2026, 7, 3))

        result = read_model.align_group_value_lanes(
            [first, later],
            {
                "first": _lane(first, [("2026-07-01", 100), ("2026-07-05", 120)]),
                "later": _lane(later, [("2026-07-03", 100), ("2026-07-04", 105)]),
            },
        )
        curve = result.curve.set_index("date")

        self.assertEqual(result.basis_date, date(2026, 7, 4))
        self.assertNotIn(pd.Timestamp("2026-07-05"), curve.index)
        self.assertEqual(curve.loc[pd.Timestamp("2026-07-01"), "item:later"], 100.0)
        self.assertEqual(curve.loc[pd.Timestamp("2026-07-03"), "item:first"], 100.0)

    def test_failed_lane_is_partial_and_preserves_planned_cash(self) -> None:
        read_model = _load_read_model()
        ready = _item("ready", requested=date(2026, 7, 1), effective=date(2026, 7, 1))
        failed = _item("failed", requested=date(2026, 7, 1), effective=date(2026, 7, 1))

        result = read_model.align_group_value_lanes(
            [ready, failed],
            {"ready": _lane(ready, [("2026-07-01", 100), ("2026-07-02", 110)]), "failed": RuntimeError("price gap")},
        )

        self.assertEqual(result.status, "PARTIAL")
        self.assertEqual(result.failures, {"failed": "price gap"})
        self.assertEqual(result.metrics.current_value, Decimal("210.0"))
        self.assertEqual(result.curve.iloc[-1]["item:failed"], 100.0)

    def test_metrics_use_daily_curve_actual_days_and_item_contributions(self) -> None:
        read_model = _load_read_model()
        curve = pd.DataFrame(
            {
                "date": pd.to_datetime(["2025-01-01", "2025-07-01", "2026-01-01"]),
                "total_value": [200.0, 180.0, 200.0],
                "item:a": [100.0, 80.0, 80.0],
                "item:b": [100.0, 100.0, 120.0],
            }
        )

        metrics = read_model.calculate_group_metrics(curve, Decimal("200"), date(2026, 1, 1))

        self.assertEqual(metrics.invested_capital, Decimal("200"))
        self.assertEqual(metrics.current_value, Decimal("200.0"))
        self.assertEqual(metrics.pnl, Decimal("0.0"))
        self.assertEqual(metrics.total_return, Decimal("0"))
        self.assertEqual(metrics.mdd, Decimal("-0.1"))
        self.assertEqual(metrics.cagr, Decimal("0"))
        self.assertFalse(metrics.short_window)
        self.assertEqual(metrics.total_contribution, Decimal("0.0"))
        self.assertEqual(metrics.downside_contribution, Decimal("-20.0"))
        self.assertEqual(metrics.contribution_by_item["a"], Decimal("-20.0"))

    def test_short_window_marker_is_explicit(self) -> None:
        read_model = _load_read_model()
        curve = pd.DataFrame(
            {
                "date": pd.to_datetime(["2026-07-01", "2026-07-31"]),
                "total_value": [100.0, 110.0],
            }
        )

        metrics = read_model.calculate_group_metrics(curve, Decimal("100"), date(2026, 7, 31))

        self.assertTrue(metrics.short_window)
        self.assertEqual(metrics.observation_days, 30)
        self.assertGreater(metrics.cagr, Decimal("0.1"))

    def test_workspace_projection_has_stable_top_level_contract_and_history(self) -> None:
        read_model = _load_read_model()
        group = PortfolioGroupRecord("group-core", "Core", True)
        active = _item("a", requested=date(2026, 7, 1), effective=date(2026, 7, 1))
        ended = _item("b", requested=date(2026, 7, 1), effective=date(2026, 7, 1), status="ended")
        repository = FakeRepository([group], [active, ended])

        workspace = read_model.build_portfolio_monitoring_workspace(
            repository,
            active_group_id="group-core",
            generated_at=datetime(2026, 7, 19, 12, 0, 0),
            lane_loader=lambda item: (
                _lane(item, [("2026-07-01", 100), ("2026-07-02", 101)])
                if item.monitoring_item_id == "a"
                else RuntimeError("legacy end missing")
            ),
        )

        self.assertEqual(
            set(workspace),
            {"schema_version", "generated_at", "config_fingerprint", "groups", "active_group", "catalog", "commands", "diagnosis", "macro_observation", "now_to_review", "source_health", "risk_calibration", "diagnosis_history", "method", "boundaries"},
        )
        self.assertEqual(workspace["schema_version"], "portfolio_monitoring_workspace_v1")
        self.assertTrue(workspace["groups"][0]["selected"])
        self.assertEqual(workspace["active_group"].status, "PARTIAL")
        self.assertEqual(workspace["active_group"].history_item_count, 2)
        self.assertEqual(workspace["generated_at"], "2026-07-19T12:00:00")
        self.assertEqual(len(workspace["config_fingerprint"]), 64)
        self.assertEqual(workspace["diagnosis"]["policy_version"], "portfolio_monitoring_policy_v1")
        self.assertEqual(workspace["diagnosis"]["top_three"], [])
        self.assertEqual(workspace["risk_calibration"]["publication_status"], "SUPPRESSED")
        self.assertNotIn("probability", workspace["risk_calibration"])

    def test_macro_projection_filters_low_confidence_and_exposes_source_health(self) -> None:
        read_model = _load_read_model()
        group = PortfolioGroupRecord("group-core", "Core", True)
        repository = FakeRepository([group], [])
        context = MacroContext(
            status="LIMITED", as_of_dates={"economic_cycle": "2026-07-01", "futures_macro": "2026-07-18"},
            publication="PROVISIONAL", cycle={}, family_scores={}, outlooks={}, pathways={}, coverage=0.75,
            warnings=("source as-of date mismatch",),
        )
        high = MacroObservation(
            "macro_tech_risk_off", "sector:Technology", "high", "MEDIUM", 0.5, ("risk_on",),
            "Technology 50% / risk-on -40", ("2026-07-18",), 0.75, "MEDIUM", "PROVISIONAL",
            "risk-on > -20", "다음 snapshot",
        )
        low = MacroObservation(
            "macro_data_low", "asset:gold", "medium", "MEDIUM", 0.3, ("gold",),
            "Gold context", ("2026-07-18",), 0.6, "LOW", "PROVISIONAL", "coverage >= 70%", "다음 snapshot",
        )

        workspace = read_model.build_portfolio_monitoring_workspace(
            repository, generated_at=datetime(2026, 7, 19, 12), macro_context=context,
            macro_observations=[high, low],
        )

        self.assertEqual(workspace["macro_observation"]["state"], "high")
        self.assertEqual(len(workspace["macro_observation"]["top_rows"]), 1)
        self.assertEqual(workspace["now_to_review"][0]["rule_id"], "macro_tech_risk_off")
        self.assertEqual(workspace["source_health"]["status"], "LIMITED")
        self.assertEqual(workspace["source_health"]["coverage"], 0.75)
        self.assertNotIn("probability", str(workspace["macro_observation"]).lower())

    def test_risk_calibration_projection_is_ready_only_and_fingerprint_safe(self) -> None:
        read_model = _load_read_model()
        base = {
            "publication_status": "READY", "probability": 0.27, "horizon_sessions": 21,
            "event_definition": "subsequent drawdown <= -10%", "sample_size": 300,
            "brier_score": 0.08, "baseline_brier": 0.10, "limitations": ["OOS only"],
            "policy_version": "portfolio_monitoring_policy_v1", "config_fingerprint": "a" * 64,
        }
        ready = read_model.project_risk_calibration(
            base, current_policy_version="portfolio_monitoring_policy_v1", current_config_fingerprint="a" * 64,
        )
        self.assertEqual(ready["probability"], 0.27)
        self.assertEqual(ready["sample_size"], 300)

        limited = read_model.project_risk_calibration(
            {**base, "publication_status": "LIMITED"},
            current_policy_version="portfolio_monitoring_policy_v1", current_config_fingerprint="a" * 64,
        )
        self.assertNotIn("probability", limited)
        stale = read_model.project_risk_calibration(
            base, current_policy_version="portfolio_monitoring_policy_v2", current_config_fingerprint="b" * 64,
        )
        self.assertEqual(stale["publication_status"], "SUPPRESSED")
        self.assertNotIn("probability", stale)
        self.assertIn("fingerprint", " ".join(stale["reasons"]))

    def test_workspace_projects_compact_diagnosis_history_timeline(self) -> None:
        read_model = _load_read_model()
        repository = FakeRepository([PortfolioGroupRecord("group-core", "Core", True)], [])
        workspace = read_model.build_portfolio_monitoring_workspace(
            repository,
            diagnosis_history=[{
                "as_of_date": "2026-07-01", "observation_state": "medium", "severity": "WATCH",
                "confidence": "MEDIUM", "resolved_at": "2026-07-18", "outcome": "resolved",
                "raw_series": [1, 2, 3],
            }],
        )
        self.assertEqual(workspace["diagnosis_history"][0]["outcome"], "resolved")
        self.assertNotIn("raw_series", workspace["diagnosis_history"][0])


if __name__ == "__main__":
    unittest.main()
