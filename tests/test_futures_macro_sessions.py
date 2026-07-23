from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import patch


class FuturesDailySessionResolverTests(unittest.TestCase):
    def test_thermometer_cache_and_builder_share_one_default_evaluation_time(self) -> None:
        from app.services.futures_macro_thermometer import (
            load_overview_futures_macro_snapshot,
        )

        evaluated_at = datetime(2026, 7, 20, 22, 14, 59, tzinfo=timezone.utc)
        with (
            patch(
                "app.services.futures_macro_thermometer.datetime"
            ) as datetime_mock,
            patch(
                "app.services.futures_macro_thermometer._latest_daily_cache_marker",
                return_value="2026-07-20 00:00:00",
            ),
            patch(
                "app.services.futures_macro_thermometer.build_futures_macro_thermometer_snapshot",
                return_value={"status": "OK"},
            ) as builder,
        ):
            datetime_mock.now.return_value = evaluated_at
            result = load_overview_futures_macro_snapshot(
                force_refresh=True,
                cache_ttl_seconds=0,
            )

        self.assertEqual(result["status"], "OK")
        self.assertEqual(builder.call_args.kwargs["evaluation_time"], evaluated_at)

    def test_evaluation_cache_token_changes_only_with_new_york_date(self) -> None:
        from app.services.futures_macro_sessions import (
            futures_session_evaluation_token,
        )

        before = futures_session_evaluation_token(
            datetime(2026, 7, 20, 22, 14, tzinfo=timezone.utc)
        )
        after = futures_session_evaluation_token(
            datetime(2026, 7, 20, 22, 15, tzinfo=timezone.utc)
        )

        self.assertEqual(before, "2026-07-20")
        self.assertEqual(after, "2026-07-20")

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

    def test_same_new_york_date_is_pending_after_evening_reopen(self) -> None:
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
        self.assertEqual(after.status, "IN_PROGRESS")
        self.assertEqual(after.reason, "same_date_provider_bar_can_still_move")

    def test_same_new_york_date_can_be_final_when_collected_during_settlement_gap(self) -> None:
        from app.services.futures_macro_sessions import (
            resolve_futures_daily_session,
        )

        result = resolve_futures_daily_session(
            "ES=F",
            "2026-07-20 00:00:00",
            "2026-07-20 21:30:00",  # 17:30 ET, before the 18:00 reopen.
            datetime(2026, 7, 21, 0, 0, tzinfo=timezone.utc),
        )

        self.assertEqual(result.status, "FINAL")
        self.assertEqual(result.reason, "same_date_collected_during_settlement_gap")

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
        self.assertEqual(after_cutoff.latest_final_session, "2026-07-17")
        self.assertEqual(after_cutoff.pending_session, "2026-07-20")
        self.assertEqual([row["close"] for row in after_cutoff.rows], [100.0])


if __name__ == "__main__":
    unittest.main()
