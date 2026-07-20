from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone

import pandas as pd


class FuturesMacroEventLoaderTests(unittest.TestCase):
    def test_loader_keeps_only_official_events_known_by_cutoff(self) -> None:
        from finance.loaders.market_events import (
            load_official_macro_event_history,
        )

        rows = [
            {
                "event_key": "good",
                "event_date": "2026-07-08",
                "event_type": "MACRO_CPI",
                "source_type": "official",
                "event_status": "active",
                "collected_at": "2026-07-01 12:00:00",
            },
            {
                "event_key": "late",
                "event_date": "2026-07-09",
                "event_type": "MACRO_EMPLOYMENT",
                "source_type": "official",
                "event_status": "active",
                "collected_at": "2026-07-11 12:00:00",
            },
            {
                "event_key": "estimate",
                "event_date": "2026-07-10",
                "event_type": "MACRO_GDP",
                "source_type": "provider_estimate",
                "event_status": "active",
                "collected_at": "2026-07-01 12:00:00",
            },
            {
                "event_key": "superseded",
                "event_date": "2026-07-10",
                "event_type": "FOMC_MEETING",
                "source_type": "official",
                "event_status": "superseded",
                "collected_at": "2026-07-01 12:00:00",
            },
        ]

        loaded = load_official_macro_event_history(
            start_date="2026-07-01",
            end_date="2026-07-31",
            known_at=datetime(2026, 7, 10, 23, 0, tzinfo=timezone.utc),
            query_fn=lambda *_args: rows,
        )

        self.assertEqual([row["event_key"] for row in loaded], ["good"])


class FuturesMacroContextFrameTests(unittest.TestCase):
    def _cycle_row(self, as_of: str, winner: str, contribution: float) -> dict[str, object]:
        probabilities = {
            phase: 0.7 if phase == winner else 0.1
            for phase in ("recovery", "expansion", "slowdown", "recession")
        }
        return {
            "as_of_date": as_of,
            "data_cutoff_date": as_of,
            "status": "READY",
            "probabilities_json": json.dumps(probabilities),
            "factor_contributions_json": json.dumps(
                [
                    {"factor": "activity_score", "value": contribution},
                    {"factor": "inflation_policy_score", "value": -contribution},
                ]
            ),
        }

    def test_context_backward_joins_cycle_without_filling_before_first_snapshot(self) -> None:
        from app.services.futures_macro_context import (
            build_futures_macro_context_frame,
        )

        dates = pd.DatetimeIndex(["2026-06-29", "2026-06-30", "2026-07-02"])
        frame = build_futures_macro_context_frame(
            dates,
            cycle_rows=[self._cycle_row("2026-06-30", "expansion", 0.8)],
            event_rows=[],
        )

        self.assertTrue(pd.isna(frame.loc[pd.Timestamp("2026-06-29"), "cycle_risk_balance"]))
        self.assertAlmostEqual(
            frame.loc[pd.Timestamp("2026-06-30"), "cycle_risk_balance"],
            0.6,
        )
        self.assertAlmostEqual(
            frame.loc[pd.Timestamp("2026-07-02"), "activity_contribution"],
            0.8,
        )
        self.assertGreaterEqual(frame.loc[pd.Timestamp("2026-07-02"), "cycle_entropy"], 0.0)
        self.assertLessEqual(frame.loc[pd.Timestamp("2026-07-02"), "cycle_entropy"], 1.0)

    def test_event_context_excludes_schedule_collected_after_origin(self) -> None:
        from app.services.futures_macro_context import (
            build_futures_macro_context_frame,
        )

        dates = pd.bdate_range("2026-07-01", periods=8)
        events = [
            {
                "event_key": "cpi",
                "event_date": "2026-07-08",
                "event_type": "MACRO_CPI",
                "source_type": "official",
                "event_status": "active",
                "collected_at": "2026-07-02 12:00:00+00:00",
            },
            {
                "event_key": "late-fomc",
                "event_date": "2026-07-09",
                "event_type": "FOMC_MEETING",
                "source_type": "official",
                "event_status": "active",
                "collected_at": "2026-07-09 23:59:00+00:00",
            },
        ]

        frame = build_futures_macro_context_frame(
            dates,
            cycle_rows=[],
            event_rows=events,
        )

        self.assertEqual(frame.loc[pd.Timestamp("2026-07-01"), "event_count_5d"], 0.0)
        self.assertEqual(frame.loc[pd.Timestamp("2026-07-02"), "event_count_5d"], 1.0)
        self.assertEqual(frame.loc[pd.Timestamp("2026-07-02"), "has_inflation_5d"], 1.0)
        self.assertEqual(frame.loc[pd.Timestamp("2026-07-02"), "has_fomc_5d"], 0.0)

    def test_empty_context_preserves_missing_macro_and_zero_known_event_counts(self) -> None:
        from app.services.futures_macro_context import (
            build_futures_macro_context_frame,
        )

        dates = pd.DatetimeIndex(["2026-07-01", "2026-07-02"])
        frame = build_futures_macro_context_frame(
            dates,
            cycle_rows=[],
            event_rows=[],
        )

        self.assertTrue(frame["cycle_risk_balance"].isna().all())
        self.assertTrue(frame["event_count_5d"].eq(0.0).all())


if __name__ == "__main__":
    unittest.main()
