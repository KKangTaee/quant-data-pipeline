from __future__ import annotations

import unittest


class FuturesMacroSnapshotPersistenceTests(unittest.TestCase):
    def test_schema_has_versioned_marker_and_unique_current_key(self) -> None:
        from finance.data.db.schema import FUTURES_MARKET_SCHEMAS

        schema = FUTURES_MARKET_SCHEMAS["futures_macro_snapshot"]

        self.assertIn("source_marker", schema)
        self.assertIn("schema_version", schema)
        self.assertIn("algorithm_version", schema)
        self.assertIn("snapshot_json LONGTEXT", schema)
        self.assertIn("UNIQUE KEY uk_futures_macro_snapshot_key", schema)

    def test_loader_returns_latest_row_without_calculation(self) -> None:
        from finance.loaders.futures_macro_snapshot import (
            load_latest_futures_macro_snapshot,
        )

        captured: dict[str, object] = {}

        def query(db_name, sql, params):
            captured.update(db_name=db_name, sql=sql, params=params)
            return [
                {
                    "snapshot_key": "overview_current",
                    "source_marker": "2026-07-17 00:00:00",
                }
            ]

        row = load_latest_futures_macro_snapshot(query_fn=query)

        self.assertIsNotNone(row)
        self.assertEqual(row["snapshot_key"], "overview_current")
        self.assertEqual(captured["db_name"], "finance_meta")
        self.assertNotIn("futures_ohlcv", str(captured["sql"]))


if __name__ == "__main__":
    unittest.main()
