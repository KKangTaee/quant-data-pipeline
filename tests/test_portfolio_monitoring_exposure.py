from __future__ import annotations

import importlib
import unittest


def _module():
    try:
        return importlib.import_module("app.services.portfolio_monitoring.exposure")
    except ModuleNotFoundError as exc:
        raise AssertionError("portfolio monitoring exposure module is required") from exc


class PortfolioMonitoringExposureTests(unittest.TestCase):
    def test_direct_stock_projects_source_dated_sector_and_industry(self) -> None:
        exposure = _module()
        result = exposure.build_direct_stock_exposure(
            {"monitoring_item_id": "aapl", "portfolio_weight": 0.4},
            {"sector": "Technology", "industry": "Consumer Electronics", "as_of_date": "2026-07-18"},
        )

        self.assertEqual(result.covered_weight, 0.4)
        self.assertEqual(result.coverage_ratio, 1.0)
        self.assertEqual(result.bucket_weight("sector", "Technology"), 0.4)
        self.assertEqual(result.bucket_weight("industry", "Consumer Electronics"), 0.4)
        self.assertEqual(result.buckets[0].source_date, "2026-07-18")

    def test_etf_holdings_lookthrough_has_priority_and_aggregates_overlap(self) -> None:
        exposure = _module()
        etf = exposure.build_etf_exposure(
            {"monitoring_item_id": "qqq", "portfolio_weight": 0.6},
            {
                "as_of_date": "2026-07-17",
                "holdings": [
                    {"symbol": "AAPL", "weight": 0.5, "sector": "Technology"},
                    {"symbol": "MSFT", "weight": 0.25, "sector": "Technology"},
                ],
            },
            {"as_of_date": "2026-07-16", "sector_weights": {"Technology": 0.95}},
        )
        direct = exposure.build_direct_stock_exposure(
            {"monitoring_item_id": "aapl", "source_ref": "AAPL", "portfolio_weight": 0.4},
            {"sector": "Technology", "as_of_date": "2026-07-18"},
        )
        result = exposure.aggregate_group_exposure([etf, direct])

        self.assertAlmostEqual(etf.covered_weight, 0.45)
        self.assertAlmostEqual(etf.uncovered_weight, 0.15)
        self.assertAlmostEqual(result.bucket_weight("symbol", "AAPL"), 0.7)
        self.assertAlmostEqual(result.bucket_weight("sector", "Technology"), 0.85)
        self.assertEqual({row.provenance for row in etf.buckets}, {"etf_holdings_lookthrough"})

    def test_etf_uses_top_level_snapshot_only_when_holdings_are_missing(self) -> None:
        exposure = _module()
        result = exposure.build_etf_exposure(
            {"monitoring_item_id": "gld", "portfolio_weight": 0.25},
            None,
            {"as_of_date": "2026-07-15", "asset_weights": {"gold": 0.9}},
        )

        self.assertAlmostEqual(result.bucket_weight("asset", "gold"), 0.225)
        self.assertAlmostEqual(result.covered_weight, 0.225)
        self.assertAlmostEqual(result.uncovered_weight, 0.025)
        self.assertEqual(result.buckets[0].provenance, "etf_top_level_exposure")

    def test_selected_strategy_uses_target_weights_without_inventing_classification(self) -> None:
        exposure = _module()
        result = exposure.build_selected_strategy_exposure(
            {"monitoring_item_id": "strategy", "portfolio_weight": 0.5},
            {
                "as_of_date": "2026-07-14",
                "targets": [
                    {"symbol": "SPY", "weight": 0.6, "asset": "equity"},
                    {"symbol": "TLT", "weight": 0.3, "asset": "duration"},
                ],
            },
        )

        self.assertAlmostEqual(result.bucket_weight("symbol", "SPY"), 0.3)
        self.assertAlmostEqual(result.bucket_weight("asset", "duration"), 0.15)
        self.assertAlmostEqual(result.covered_weight, 0.45)
        self.assertAlmostEqual(result.uncovered_weight, 0.05)

    def test_weights_not_summing_to_one_preserve_total_and_coverage(self) -> None:
        exposure = _module()
        known = exposure.build_direct_stock_exposure(
            {"monitoring_item_id": "known", "portfolio_weight": 0.3},
            {"sector": "Financials", "as_of_date": "2026-07-18"},
        )
        missing = exposure.build_direct_stock_exposure(
            {"monitoring_item_id": "missing", "portfolio_weight": 0.2},
            None,
        )
        result = exposure.aggregate_group_exposure([known, missing])

        self.assertAlmostEqual(result.total_weight, 0.5)
        self.assertAlmostEqual(result.covered_weight, 0.3)
        self.assertAlmostEqual(result.uncovered_weight, 0.2)
        self.assertAlmostEqual(result.coverage_ratio, 0.6)
        self.assertEqual(result.bucket_weight("sector", "Unknown"), 0.0)


if __name__ == "__main__":
    unittest.main()
