from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

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

    def test_job_fetches_both_snapshots_before_writer(self) -> None:
        from app.jobs import ingestion_jobs

        calls: list[tuple[str, object]] = []
        frames = {
            "stock": _listing_frame(("NEW", "New")),
            "etf": _listing_frame(("NEWX", "New ETF")),
        }

        def fetcher(kind: str):
            calls.append(("fetch", kind))
            return frames[kind], {
                "api_total": 1,
                "deduped_rows": 1,
            }

        def writer(received, **kwargs):
            calls.append(("write", tuple(received)))
            return {
                "snapshot_date": "2026-07-23",
                "rows_written": 2,
                "lifecycle_rows_written": 2,
                "kinds": {
                    "stock": {
                        "current_count": 1,
                        "added_count": 1,
                        "removed_count": 0,
                    },
                    "etf": {
                        "current_count": 1,
                        "added_count": 1,
                        "removed_count": 0,
                    },
                },
            }

        result = ingestion_jobs.run_refresh_nyse_listing_universe(
            snapshot_fetcher=fetcher,
            writer=writer,
            snapshot_date="2026-07-23",
        )

        self.assertEqual(
            calls,
            [
                ("fetch", "stock"),
                ("fetch", "etf"),
                ("write", ("stock", "etf")),
            ],
        )
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["rows_written"], 2)
        self.assertEqual(
            result["details"]["source_stats"]["stock"]["api_total"],
            1,
        )

    def test_job_does_not_write_when_etf_fetch_fails(self) -> None:
        from app.jobs import ingestion_jobs

        writer = Mock()
        fetcher = Mock(
            side_effect=[
                (
                    _listing_frame(("NEW", "New")),
                    {"api_total": 1, "deduped_rows": 1},
                ),
                RuntimeError("ETF source unavailable"),
            ]
        )

        result = ingestion_jobs.run_refresh_nyse_listing_universe(
            snapshot_fetcher=fetcher,
            writer=writer,
        )

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["rows_written"], 0)
        self.assertTrue(result["details"]["masters_preserved"])
        self.assertIn("existing masters were preserved", result["message"])
        writer.assert_not_called()

    def test_action_is_registered_guided_and_dispatched(self) -> None:
        from app.web.ingestion import dispatcher, guides, registry

        definition = registry.INGESTION_ACTION_REGISTRY[
            "refresh_nyse_listing_universe"
        ]
        self.assertEqual(
            definition["section"],
            registry.INGESTION_COLLECTION_OPERATIONAL,
        )
        self.assertEqual(
            definition["target_tables"],
            [
                "finance_meta.nyse_stock",
                "finance_meta.nyse_etf",
                "finance_meta.nyse_symbol_lifecycle",
            ],
        )
        self.assertEqual(
            guides.JOB_GUIDE["refresh_nyse_listing_universe"]["title"],
            "주식·ETF 종목 목록 최신화",
        )

        progress_callback = Mock()
        with patch.object(
            dispatcher,
            "run_refresh_nyse_listing_universe",
            return_value={"status": "success", "rows_written": 2},
        ) as runner:
            result = dispatcher.dispatch_job(
                {
                    "action": "refresh_nyse_listing_universe",
                    "job_name": "refresh_nyse_listing_universe",
                    "params": {"snapshot_date": "2026-07-23"},
                },
                progress_callback=progress_callback,
            )

        runner.assert_called_once_with(
            snapshot_date="2026-07-23",
            progress_callback=progress_callback,
        )
        self.assertEqual(result["status"], "success")

    def test_operational_section_places_refresh_before_daily_price_update(
        self,
    ) -> None:
        sections_source = Path(
            "app/web/ingestion/sections.py"
        ).read_text(encoding="utf-8")
        page_source = Path(
            "app/web/ingestion/page.py"
        ).read_text(encoding="utf-8")

        refresh_index = sections_source.index(
            'with st.expander("주식·ETF 종목 목록 최신화"'
        )
        daily_index = sections_source.index(
            'with st.expander("일별 가격 업데이트"'
        )

        self.assertLess(refresh_index, daily_index)
        self.assertIn(
            '"action": "refresh_nyse_listing_universe"',
            sections_source,
        )
        self.assertIn(
            '"주식·ETF 종목 목록 최신화"',
            sections_source,
        )
        self.assertIn(
            "load_nyse_listing_universe_status",
            page_source,
        )
        self.assertNotIn(
            '_render_job_brief("refresh_nyse_listing_universe")',
            sections_source,
        )

    def test_inline_result_summary_focuses_on_universe_changes(self) -> None:
        from app.web.ingestion import results

        summary = results.build_listing_universe_refresh_summary(
            {
                "status": "success",
                "message": "completed",
                "details": {
                    "snapshot_date": "2026-07-23",
                    "kinds": {
                        "stock": {
                            "current_count": 6770,
                            "added_count": 158,
                            "removed_count": 126,
                        },
                        "etf": {
                            "current_count": 5537,
                            "added_count": 372,
                            "removed_count": 67,
                        },
                    },
                },
            }
        )

        self.assertEqual(summary["snapshot_date"], "2026-07-23")
        self.assertEqual(summary["stock"], "6,770 · +158 / -126")
        self.assertEqual(summary["etf"], "5,537 · +372 / -67")
        self.assertIn("일별 가격 업데이트", summary["next_action"])


if __name__ == "__main__":
    unittest.main()
