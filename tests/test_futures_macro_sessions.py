from __future__ import annotations

import unittest
from datetime import datetime, timezone


class FuturesDailySessionResolverTests(unittest.TestCase):
    def test_evaluation_cache_token_changes_at_new_york_final_cutoff(self) -> None:
        from app.services.futures_macro_sessions import (
            futures_session_evaluation_token,
        )

        before = futures_session_evaluation_token(
            datetime(2026, 7, 20, 22, 14, tzinfo=timezone.utc)
        )
        after = futures_session_evaluation_token(
            datetime(2026, 7, 20, 22, 15, tzinfo=timezone.utc)
        )

        self.assertEqual(before, "2026-07-20:IN_PROGRESS")
        self.assertEqual(after, "2026-07-20:FINAL")

    def test_validation_loader_selects_collection_timestamp(self) -> None:
        from app.services.futures_macro_validation import (
            _load_validation_futures_rows,
        )

        captured: dict[str, object] = {}

        def query(database, sql, params):
            captured.update(database=database, sql=sql, params=params)
            return []

        _load_validation_futures_rows(
            query,
            symbols=("ES=F",),
            lookback_days=30,
        )

        self.assertIn("collected_at", str(captured["sql"]))

    def test_prior_weekday_is_final(self) -> None:
        from app.services.futures_macro_sessions import (
            resolve_futures_daily_session,
        )

        result = resolve_futures_daily_session(
            "ES=F",
            "2026-07-17 00:00:00",
            "2026-07-20 12:00:00",
            datetime(2026, 7, 20, 12, 0, tzinfo=timezone.utc),
        )

        self.assertEqual(result.session_date, "2026-07-17")
        self.assertEqual(result.status, "FINAL")

    def test_sunday_provider_label_maps_to_monday_session(self) -> None:
        from app.services.futures_macro_sessions import (
            resolve_futures_daily_session,
        )

        result = resolve_futures_daily_session(
            "ES=F",
            "2026-07-19 00:00:00",
            "2026-07-20 12:00:00",
            datetime(2026, 7, 20, 12, 0, tzinfo=timezone.utc),
        )

        self.assertEqual(result.raw_candle_date, "2026-07-19")
        self.assertEqual(result.session_date, "2026-07-20")
        self.assertEqual(result.status, "IN_PROGRESS")

    def test_same_new_york_date_becomes_final_only_after_cutoff(self) -> None:
        from app.services.futures_macro_sessions import (
            resolve_futures_daily_session,
        )

        before = resolve_futures_daily_session(
            "ES=F",
            "2026-07-20 00:00:00",
            "2026-07-20 20:00:00",
            datetime(2026, 7, 20, 22, 14, tzinfo=timezone.utc),
        )
        after = resolve_futures_daily_session(
            "ES=F",
            "2026-07-20 00:00:00",
            "2026-07-20 23:00:00",
            datetime(2026, 7, 20, 22, 15, tzinfo=timezone.utc),
        )

        self.assertEqual(before.status, "IN_PROGRESS")
        self.assertEqual(after.status, "FINAL")

    def test_saturday_and_unparseable_labels_are_unknown(self) -> None:
        from app.services.futures_macro_sessions import (
            resolve_futures_daily_session,
        )

        saturday = resolve_futures_daily_session(
            "ES=F",
            "2026-07-18 00:00:00",
            None,
            datetime(2026, 7, 20, 12, 0, tzinfo=timezone.utc),
        )
        broken = resolve_futures_daily_session(
            "ES=F",
            "not-a-date",
            None,
            datetime(2026, 7, 20, 12, 0, tzinfo=timezone.utc),
        )

        self.assertEqual((saturday.session_date, saturday.status), (None, "UNKNOWN"))
        self.assertEqual((broken.session_date, broken.status), (None, "UNKNOWN"))

    def test_completed_rows_collapse_canonical_duplicates_and_keep_pending_evidence(self) -> None:
        from app.services.futures_macro_sessions import (
            select_completed_futures_daily_rows,
        )

        rows = [
            {
                "provider_symbol": "ES=F",
                "candle_time_utc": "2026-07-17 00:00:00",
                "collected_at": "2026-07-18 01:00:00",
                "close": 100.0,
            },
            {
                "provider_symbol": "ES=F",
                "candle_time_utc": "2026-07-19 00:00:00",
                "collected_at": "2026-07-20 10:00:00",
                "close": 101.0,
            },
            {
                "provider_symbol": "ES=F",
                "candle_time_utc": "2026-07-20 00:00:00",
                "collected_at": "2026-07-20 11:00:00",
                "close": 102.0,
            },
        ]

        before_cutoff = select_completed_futures_daily_rows(
            rows,
            evaluation_time=datetime(2026, 7, 20, 12, 0, tzinfo=timezone.utc),
        )
        after_cutoff = select_completed_futures_daily_rows(
            rows,
            evaluation_time=datetime(2026, 7, 20, 23, 0, tzinfo=timezone.utc),
        )

        self.assertEqual(before_cutoff.latest_final_session, "2026-07-17")
        self.assertEqual(before_cutoff.pending_session, "2026-07-20")
        self.assertEqual([row["close"] for row in before_cutoff.rows], [100.0])
        self.assertEqual(after_cutoff.latest_final_session, "2026-07-20")
        self.assertIsNone(after_cutoff.pending_session)
        self.assertEqual([row["close"] for row in after_cutoff.rows], [100.0, 102.0])
        self.assertEqual(after_cutoff.rows[-1]["Date"], "2026-07-20")
        self.assertEqual(
            after_cutoff.rows[-1]["raw_candle_time_utc"],
            "2026-07-20 00:00:00",
        )


if __name__ == "__main__":
    unittest.main()
