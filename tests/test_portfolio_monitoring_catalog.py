from __future__ import annotations

import importlib
import unittest


def _load_catalog():
    try:
        return importlib.import_module("app.services.portfolio_monitoring.catalog")
    except ModuleNotFoundError as exc:
        raise AssertionError("portfolio monitoring catalog module is required") from exc


class FakeCatalogDb:
    def __init__(self, rows):
        self.rows = list(rows)
        self.used_databases = []
        self.queries = []
        self.closed = False

    def use_db(self, name):
        self.used_databases.append(name)

    def query(self, sql, params=None):
        self.queries.append((sql, list(params or [])))
        return list(self.rows)

    def close(self):
        self.closed = True


class PortfolioMonitoringCatalogTests(unittest.TestCase):
    def test_direct_search_preserves_stock_and_etf_kind_identity(self) -> None:
        catalog = _load_catalog()
        db = FakeCatalogDb(
            [
                {
                    "symbol": "AAPL",
                    "name": "Apple Inc.",
                    "kind": "stock",
                    "listing_status": "active",
                    "sector": "Technology",
                    "industry": "Consumer Electronics",
                },
                {
                    "symbol": "AAPLX",
                    "name": "Apple Income ETF",
                    "kind": "etf",
                    "listing_status": "active",
                    "fund_family": "Example Funds",
                },
            ]
        )

        rows = catalog.search_direct_securities("app", db_factory=lambda: db, limit=20)

        self.assertEqual(
            [(row.source_ref, row.instrument_kind) for row in rows],
            [("AAPL", "stock"), ("AAPLX", "etf")],
        )
        self.assertTrue(all(row.source_type == "direct_security" for row in rows))
        self.assertEqual(rows[0].metadata["sector"], "Technology")
        self.assertEqual(db.used_databases, ["finance_meta"])
        self.assertTrue(db.closed)
        sql, params = db.queries[0]
        self.assertIn("UNION ALL", sql)
        self.assertIn("nyse_stock", sql)
        self.assertIn("nyse_etf", sql)
        self.assertEqual(params, ["%APP%", "%APP%", "APP", "APP%", 20])

    def test_direct_search_excludes_explicit_unavailable_lifecycle_rows(self) -> None:
        catalog = _load_catalog()
        db = FakeCatalogDb(
            [
                {"symbol": "LIVE", "name": "Live Corp", "kind": "stock", "listing_status": "active"},
                {"symbol": "NOHIST", "name": "No Lifecycle ETF", "kind": "etf", "listing_status": None},
                {"symbol": "OLD", "name": "Old Corp", "kind": "stock", "listing_status": "inactive"},
                {"symbol": "UNK", "name": "Unknown Corp", "kind": "stock", "listing_status": "unknown"},
                {"symbol": "DEAD", "name": "Dead ETF", "kind": "etf", "listing_status": "delisted"},
            ]
        )

        rows = catalog.search_direct_securities("", db_factory=lambda: db, limit=20)

        self.assertEqual([row.source_ref for row in rows], ["LIVE", "NOHIST"])
        self.assertEqual(rows[1].readiness, "CATALOG_ONLY")

    def test_direct_search_normalizes_query_and_caps_results(self) -> None:
        catalog = _load_catalog()
        db = FakeCatalogDb(
            [
                {"symbol": f"SYM{index}", "name": f"Asset {index}", "kind": "stock", "listing_status": "active"}
                for index in range(8)
            ]
        )

        rows = catalog.search_direct_securities("  syM  ", db_factory=lambda: db, limit=3)

        self.assertEqual(len(rows), 3)
        self.assertEqual(db.queries[0][1], ["%SYM%", "%SYM%", "SYM", "SYM%", 3])

    def test_direct_search_ranks_exact_ticker_before_prefix_matches(self) -> None:
        catalog = _load_catalog()
        db = FakeCatalogDb(
            [
                {"symbol": "AAPB", "name": "Apple Bear ETF", "kind": "etf", "listing_status": "active"},
                {"symbol": "AAPL", "name": "Apple Inc.", "kind": "stock", "listing_status": "active"},
                {"symbol": "AAPU", "name": "Apple Bull ETF", "kind": "etf", "listing_status": "active"},
            ]
        )

        rows = catalog.search_direct_securities("aapl", db_factory=lambda: db, limit=5)

        self.assertEqual(rows[0].source_ref, "AAPL")

    def test_final_review_catalog_requires_authoritative_monitoring_candidate_true(self) -> None:
        catalog = _load_catalog()
        rows = catalog.list_monitoring_candidates(
            decision_loader=lambda: [
                {
                    "decision_id": "decision-ready",
                    "monitoring_candidate": True,
                    "source_title": "Ready Strategy",
                    "updated_at": "2026-07-18T10:00:00",
                },
                {
                    "decision_id": "decision-false",
                    "monitoring_candidate": False,
                    "source_title": "False Strategy",
                },
                {
                    "decision_id": "decision-one",
                    "monitoring_candidate": 1,
                    "source_title": "Integer One Is Not Authoritative",
                },
                {"monitoring_candidate": True, "source_title": "Missing Decision ID"},
            ]
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].source_ref, "decision-ready")
        self.assertEqual(rows[0].source_type, "selected_strategy")
        self.assertEqual(rows[0].instrument_kind, "strategy")
        self.assertEqual(rows[0].label, "Ready Strategy")

    def test_combined_catalog_routes_by_source_type_and_filters_strategy_text(self) -> None:
        catalog = _load_catalog()
        db = FakeCatalogDb(
            [{"symbol": "MSFT", "name": "Microsoft", "kind": "stock", "listing_status": "active"}]
        )
        decisions = lambda: [
            {
                "decision_id": "decision-growth",
                "monitoring_candidate": True,
                "source_title": "Growth Strategy",
            },
            {
                "decision_id": "decision-income",
                "monitoring_candidate": True,
                "source_title": "Income Strategy",
            },
        ]

        direct = catalog.search_monitoring_catalog(
            "msft",
            "direct_security",
            db_factory=lambda: db,
            decision_loader=decisions,
        )
        strategy = catalog.search_monitoring_catalog(
            "growth",
            "selected_strategy",
            db_factory=lambda: db,
            decision_loader=decisions,
        )

        self.assertEqual([row.source_ref for row in direct], ["MSFT"])
        self.assertEqual([row.source_ref for row in strategy], ["decision-growth"])
        with self.assertRaisesRegex(ValueError, "Unsupported monitoring catalog source type"):
            catalog.search_monitoring_catalog(
                "",
                "unsupported",
                db_factory=lambda: db,
                decision_loader=decisions,
            )


if __name__ == "__main__":
    unittest.main()
