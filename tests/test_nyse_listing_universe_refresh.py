from __future__ import annotations

from collections.abc import Iterable
import unittest
from unittest.mock import patch

import pandas as pd

from finance.data import nyse, nyse_db


def _listing_frame(*rows: tuple[str, str]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "symbol": symbol,
                "name": name,
                "url": f"/quote/{symbol}",
            }
            for symbol, name in rows
        ]
    )


class _FakeListingDB:
    def __init__(
        self,
        current: dict[str, Iterable[str]],
        *,
        fail_on_write: bool = False,
    ) -> None:
        self.current = {
            kind: {str(symbol) for symbol in symbols}
            for kind, symbols in current.items()
        }
        self.fail_on_write = fail_on_write
        self.begin_count = 0
        self.commit_count = 0
        self.rollback_count = 0
        self.closed = False
        self.executemany_calls: list[tuple[str, list]] = []
        self.execute_calls: list[tuple[str, object]] = []

    def use_db(self, db_name: str) -> None:
        assert db_name == "finance_meta"

    def query(self, sql: str, params=None) -> list[dict]:
        if "FROM nyse_stock" in sql:
            if "COUNT(*)" in sql:
                return [{"row_count": len(self.current["stock"])}]
            return [{"symbol": symbol} for symbol in sorted(self.current["stock"])]
        if "FROM nyse_etf" in sql:
            if "COUNT(*)" in sql:
                return [{"row_count": len(self.current["etf"])}]
            return [{"symbol": symbol} for symbol in sorted(self.current["etf"])]
        if "FROM nyse_symbol_lifecycle" in sql:
            return [
                {
                    "kind": "stock",
                    "last_seen_date": "2026-05-31",
                    "collected_at": "2026-05-31 00:00:00",
                },
                {
                    "kind": "etf",
                    "last_seen_date": "2026-05-31",
                    "collected_at": "2026-05-31 00:00:00",
                },
            ]
        raise AssertionError(f"Unexpected query: {sql}")

    def execute(self, sql: str, params=None) -> None:
        self.execute_calls.append((sql, params))
        if self.fail_on_write and "DELETE FROM nyse_" in sql:
            raise RuntimeError("write failed")
        if "DELETE FROM nyse_stock" in sql:
            self.current["stock"].difference_update(params or [])
        if "DELETE FROM nyse_etf" in sql:
            self.current["etf"].difference_update(params or [])

    def executemany(self, sql: str, params: list) -> None:
        self.executemany_calls.append((sql, params))
        if self.fail_on_write and (
            "INSERT INTO nyse_stock" in sql or "INSERT INTO nyse_etf" in sql
        ):
            raise RuntimeError("write failed")
        if "INSERT INTO nyse_stock" in sql:
            self.current["stock"].update(str(row[0]) for row in params)
        if "INSERT INTO nyse_etf" in sql:
            self.current["etf"].update(str(row[0]) for row in params)

    def begin(self) -> None:
        self.begin_count += 1

    def commit(self) -> None:
        self.commit_count += 1

    def rollback(self) -> None:
        self.rollback_count += 1

    def close(self) -> None:
        self.closed = True


class NyseListingUniverseRefreshTest(unittest.TestCase):
    def test_fetch_nyse_listing_snapshot_returns_frame_and_api_stats(self) -> None:
        with patch.object(
            nyse,
            "_fetch_api_rows",
            return_value=[
                {
                    "normalizedTicker": "NEW",
                    "instrumentName": "New Co",
                    "url": "/quote/NEW",
                    "total": 1,
                }
            ],
        ):
            frame, stats = nyse.fetch_nyse_listing_snapshot("stock")

        self.assertEqual(frame["symbol"].tolist(), ["NEW"])
        self.assertEqual(stats["api_total"], 1)
        self.assertEqual(stats["deduped_rows"], 1)

    def test_refresh_replaces_stock_and_etf_in_one_transaction(self) -> None:
        db = _FakeListingDB(
            {
                "stock": {"OLD", "KEEP"},
                "etf": {"OLDX", "KEEPX"},
            }
        )

        with patch.object(nyse_db, "sync_table_schema"):
            summary = nyse_db.refresh_nyse_listing_universe(
                {
                    "stock": _listing_frame(
                        ("KEEP", "Keep"),
                        ("NEW", "New"),
                    ),
                    "etf": _listing_frame(
                        ("KEEPX", "Keep ETF"),
                        ("NEWX", "New ETF"),
                    ),
                },
                snapshot_date="2026-07-23",
                minimum_retention_ratio=0.0,
                db_factory=lambda *args, **kwargs: db,
            )

        self.assertEqual(db.begin_count, 1)
        self.assertEqual(db.commit_count, 1)
        self.assertEqual(db.rollback_count, 0)
        self.assertEqual(
            db.current,
            {
                "stock": {"KEEP", "NEW"},
                "etf": {"KEEPX", "NEWX"},
            },
        )
        self.assertEqual(
            summary["kinds"]["stock"]["added_symbols"],
            ["NEW"],
        )
        self.assertEqual(
            summary["kinds"]["stock"]["removed_symbols"],
            ["OLD"],
        )
        self.assertEqual(
            summary["kinds"]["etf"]["added_symbols"],
            ["NEWX"],
        )
        self.assertEqual(
            summary["kinds"]["etf"]["removed_symbols"],
            ["OLDX"],
        )

    def test_refresh_rejects_suspicious_collapse_before_transaction(self) -> None:
        db = _FakeListingDB(
            {
                "stock": {f"S{index}" for index in range(100)},
                "etf": {f"E{index}" for index in range(100)},
            }
        )

        with (
            patch.object(nyse_db, "sync_table_schema"),
            self.assertRaisesRegex(ValueError, "retention"),
        ):
            nyse_db.refresh_nyse_listing_universe(
                {
                    "stock": _listing_frame(("NEW", "New")),
                    "etf": _listing_frame(("NEWX", "New ETF")),
                },
                db_factory=lambda *args, **kwargs: db,
            )

        self.assertEqual(db.begin_count, 0)
        self.assertEqual(db.commit_count, 0)
        self.assertEqual(db.rollback_count, 0)

    def test_refresh_rolls_back_both_kinds_on_write_failure(self) -> None:
        db = _FakeListingDB(
            {
                "stock": {"OLD"},
                "etf": {"OLDX"},
            },
            fail_on_write=True,
        )

        with (
            patch.object(nyse_db, "sync_table_schema"),
            self.assertRaisesRegex(RuntimeError, "write failed"),
        ):
            nyse_db.refresh_nyse_listing_universe(
                {
                    "stock": _listing_frame(("NEW", "New")),
                    "etf": _listing_frame(("NEWX", "New ETF")),
                },
                minimum_retention_ratio=0.0,
                db_factory=lambda *args, **kwargs: db,
            )

        self.assertEqual(db.commit_count, 0)
        self.assertEqual(db.rollback_count, 1)
        self.assertTrue(db.closed)

    def test_listing_universe_status_uses_lifecycle_snapshot_date(self) -> None:
        db = _FakeListingDB(
            {
                "stock": {"AAPL", "MSFT"},
                "etf": {"SPY"},
            }
        )

        status = nyse_db.load_nyse_listing_universe_status(
            db_factory=lambda *args, **kwargs: db,
        )

        self.assertEqual(status["status"], "ok")
        self.assertEqual(status["latest_snapshot_date"], "2026-05-31")
        self.assertEqual(status["kinds"]["stock"]["row_count"], 2)
        self.assertEqual(status["kinds"]["etf"]["row_count"], 1)


if __name__ == "__main__":
    unittest.main()
