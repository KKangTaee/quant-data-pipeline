from __future__ import annotations

import importlib
import math
import unittest
from dataclasses import replace
from datetime import date
from decimal import Decimal

import pandas as pd

from app.services.portfolio_monitoring.exposure import ExposureBucket, ExposureResult
from app.services.portfolio_monitoring.persistence import MonitoringItemRecord
from app.services.portfolio_monitoring.read_model import GroupMetrics, GroupValueResult
from app.services.portfolio_monitoring.valuation import CorporateActionReview, ItemValueLane


def _diagnosis():
    try:
        return importlib.import_module("app.services.portfolio_monitoring.diagnosis")
    except ModuleNotFoundError as exc:
        raise AssertionError("portfolio monitoring diagnosis module is required") from exc


def _item(item_id: str, weight: float) -> MonitoringItemRecord:
    return MonitoringItemRecord(
        monitoring_item_id=item_id,
        portfolio_group_id="group",
        source_type="direct_security",
        source_ref=item_id.upper(),
        instrument_kind="stock",
        requested_start_date=date(2025, 1, 1),
        effective_start_date=date(2025, 1, 1),
        funding_mode="fixed_notional",
        input_notional=Decimal(str(weight * 1000)),
        input_shares=None,
        entry_close=Decimal("10"),
        initial_capital=Decimal(str(weight * 1000)),
    )


def _lane(item: MonitoringItemRecord, values: list[float]) -> ItemValueLane:
    frame = pd.DataFrame({
        "date": pd.bdate_range("2025-01-01", periods=len(values)),
        "total_value": values,
    })
    return ItemValueLane(
        monitoring_item_id=item.monitoring_item_id,
        source_ref=item.source_ref,
        effective_start_date=frame.iloc[0]["date"].date(),
        latest_usable_date=frame.iloc[-1]["date"].date(),
        initial_capital=item.initial_capital,
        status="active",
        curve=frame,
        review=CorporateActionReview("READY", Decimal("0"), Decimal("0"), ()),
    )


def _group(items, lanes) -> GroupValueResult:
    dates = next(iter(lanes.values())).curve["date"]
    curve = pd.DataFrame({"date": dates})
    for item in items:
        curve[f"item:{item.monitoring_item_id}"] = lanes[item.monitoring_item_id].curve["total_value"]
    curve["total_value"] = curve.filter(like="item:").sum(axis=1)
    metrics = GroupMetrics(
        invested_capital=Decimal("1000"), current_value=Decimal(str(curve.iloc[-1]["total_value"])),
        pnl=Decimal("0"), total_return=Decimal("0"), mdd=Decimal("-0.12"), cagr=None,
        observation_days=300, short_window=True, total_contribution=Decimal("25"),
        downside_contribution=Decimal("-40"), contribution_by_item={"a": Decimal("-30"), "b": Decimal("55")},
    )
    return GroupValueResult("READY", dates.iloc[-1].date(), curve, metrics, {}, (), 2, 2)


class PortfolioMonitoringDiagnosisTests(unittest.TestCase):
    def test_behavior_facts_cover_windows_trend_drawdown_volatility_and_contribution(self) -> None:
        diagnosis = _diagnosis()
        a, b = _item("a", 0.6), _item("b", 0.4)
        a_values = [100 + index * 0.1 for index in range(220)]
        a_values[-21:] = [100 - index * 2 for index in range(21)]
        b_values = [80 + value * 0.7 for value in a_values]
        lanes = {"a": _lane(a, a_values), "b": _lane(b, b_values)}

        facts = diagnosis.build_behavior_facts(_group([a, b], lanes), lanes)
        first = facts.items["a"]

        self.assertIsNotNone(first.returns[21])
        self.assertIsNotNone(first.returns[63])
        self.assertIsNotNone(first.returns[126])
        self.assertIsNotNone(first.ma_distance[50])
        self.assertIsNotNone(first.ma_distance[200])
        self.assertGreaterEqual(first.consecutive_below_200d, 5)
        self.assertLess(first.current_drawdown, 0)
        self.assertLessEqual(first.mdd, first.current_drawdown)
        self.assertGreater(first.volatility_63d, 0)
        self.assertGreater(facts.pairwise_correlations[("a", "b")], 0.8)
        self.assertEqual(facts.total_contribution, 25.0)
        self.assertEqual(facts.downside_contribution, -40.0)
        self.assertEqual(first.contribution, -30.0)

    def test_policy_boundaries_and_final_review_override_are_deterministic(self) -> None:
        diagnosis = _diagnosis()
        exposure = ExposureResult(
            buckets=(ExposureBucket("sector", "Technology", 0.35, "a", "profile", "2026-07-18"),),
            total_weight=1.0, covered_weight=1.0, uncovered_weight=0.0, coverage_ratio=1.0,
        )
        behavior = diagnosis.BehaviorFacts(
            items={
                "a": diagnosis.ItemBehaviorFact(
                    "a", 0.25, {21: 0.0, 63: -0.10, 126: 0.0}, {50: -0.01, 200: -0.01},
                    5, -0.10, -0.10, 0.2, -35.0,
                )
            },
            pairwise_correlations={}, total_contribution=-35.0, downside_contribution=-100.0,
            source_dates=("2026-07-18",),
        )

        rows = diagnosis.evaluate_portfolio_rules(exposure, behavior)
        by_id = {row.rule_id: row for row in rows}
        self.assertEqual(by_id["single_item_concentration:a"].severity, "WATCH")
        self.assertEqual(by_id["sector_concentration:Technology"].severity, "WATCH")
        self.assertEqual(by_id["trend_break_200d:a"].severity, "WATCH")
        self.assertEqual(by_id["current_drawdown:a"].severity, "WATCH")
        self.assertEqual(by_id["downside_contribution:a"].severity, "WATCH")
        self.assertEqual(by_id["recent_weakness_63d:a"].severity, "WATCH")

        overridden = diagnosis.evaluate_portfolio_rules(
            exposure,
            behavior,
            overrides={"recent_weakness_63d": {"watch": -0.05, "high": -0.08, "provenance": "final_review"}},
        )
        weakness = next(row for row in overridden if row.rule_id == "recent_weakness_63d:a")
        self.assertEqual(weakness.severity, "HIGH")
        self.assertEqual(weakness.policy_provenance, "final_review")

    def test_high_thresholds_are_inclusive(self) -> None:
        diagnosis = _diagnosis()
        behavior = diagnosis.BehaviorFacts(
            items={"a": diagnosis.ItemBehaviorFact("a", 0.4, {21: 0, 63: -0.2, 126: 0}, {50: 0, 200: -0.1}, 20, -0.15, -0.15, 0.2, -50)},
            pairwise_correlations={}, total_contribution=-50, downside_contribution=-100, source_dates=(),
        )
        exposure = ExposureResult((), 1, 1, 0, 1)
        by_id = {row.rule_id: row for row in diagnosis.evaluate_portfolio_rules(exposure, behavior)}

        self.assertEqual(by_id["single_item_concentration:a"].severity, "HIGH")
        self.assertEqual(by_id["trend_break_200d:a"].severity, "HIGH")
        self.assertEqual(by_id["current_drawdown:a"].severity, "HIGH")
        self.assertEqual(by_id["downside_contribution:a"].severity, "HIGH")
        self.assertEqual(by_id["recent_weakness_63d:a"].severity, "HIGH")

    def test_projection_deduplicates_roots_and_separates_confidence_bands(self) -> None:
        diagnosis = _diagnosis()
        base = diagnosis.DiagnosisFact(
            rule_id="trend_break_200d:a", root_id="trend:a", policy_version=diagnosis.DIAGNOSIS_POLICY_VERSION,
            classification="weakness", severity="WATCH", persistence=5, affected_weight=0.3,
            contribution=-10.0, measured_fact="below 200D 5 sessions", threshold="watch 5 sessions",
            source_dates=("2026-07-18",), coverage=0.92, confidence="HIGH",
            meaning="장기 추세 확인 필요", change_condition="200D 위 회복", next_check="다음 종가",
        )
        facts = [
            base,
            replace(base, rule_id="recent_weakness_63d:a", severity="HIGH", persistence=63),
            replace(base, rule_id="sector_concentration:Technology", root_id="sector:Technology", affected_weight=0.55, confidence="MEDIUM", coverage=0.75),
            replace(base, rule_id="data_gap", root_id="coverage", classification="data_gap", severity="WATCH", confidence="LOW", coverage=0.6),
            replace(base, rule_id="diversification_strength", root_id="strength:diversification", classification="strength", severity="INFO", affected_weight=0.2),
        ]

        projection = diagnosis.project_diagnoses(facts, 0.92)

        self.assertEqual([row.rule_id for row in projection.top_three], ["recent_weakness_63d:a", "sector_concentration:Technology"])
        self.assertEqual(len([row for row in projection.all_rows if row.root_id == "trend:a"]), 1)
        self.assertEqual(len(projection.strengths), 1)
        self.assertEqual(len(projection.weaknesses), 2)
        self.assertEqual(len(projection.data_gaps), 1)
        self.assertTrue(all(row.confidence != "LOW" for row in projection.top_three))

    def test_projection_limits_first_read_to_three_with_stable_priority(self) -> None:
        diagnosis = _diagnosis()
        rows = [
            diagnosis.DiagnosisFact(
                rule_id=f"row:{index}", root_id=f"root:{index}", policy_version=diagnosis.DIAGNOSIS_POLICY_VERSION,
                classification="weakness", severity="HIGH" if index < 2 else "WATCH",
                persistence=index + 1, affected_weight=0.1 * (index + 1), contribution=None,
                measured_fact=str(index), threshold="test", source_dates=(), coverage=1.0,
                confidence="HIGH", meaning="확인", change_condition="변화", next_check="다음",
            ) for index in range(5)
        ]
        projection = diagnosis.project_diagnoses(rows, 1.0)

        self.assertEqual(len(projection.top_three), 3)
        self.assertEqual([row.rule_id for row in projection.top_three[:2]], ["row:1", "row:0"])


if __name__ == "__main__":
    unittest.main()
