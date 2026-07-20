from __future__ import annotations

import unittest
from datetime import datetime, timezone

import pandas as pd

from tests.test_futures_macro_pattern import SYMBOLS


def _raw_daily_rows() -> list[dict[str, object]]:
    dates = pd.bdate_range(end="2026-07-17", periods=140)
    rows: list[dict[str, object]] = []
    latest: dict[str, float] = {}
    for symbol_index, symbol in enumerate(SYMBOLS):
        price = 90.0 + symbol_index * 4.0
        for index, session_date in enumerate(dates):
            price *= 1.0 + 0.0004 + 0.0015 * ((index % 7) - 3) / 3
            latest[symbol] = price
            rows.append(
                {
                    "provider_symbol": symbol,
                    "candle_time_utc": f"{session_date.date().isoformat()} 00:00:00",
                    "collected_at": f"{session_date.date().isoformat()} 23:00:00",
                    "open": price * 0.999,
                    "high": price * 1.002,
                    "low": price * 0.998,
                    "close": price,
                    "volume": 1_000 + index,
                    "source": "fixture",
                }
            )
    for symbol in SYMBOLS:
        price = latest[symbol] * 1.01
        rows.append(
            {
                "provider_symbol": symbol,
                "candle_time_utc": "2026-07-19 00:00:00",
                "collected_at": "2026-07-20 10:00:00",
                "open": price * 0.999,
                "high": price * 1.002,
                "low": price * 0.998,
                "close": price,
                "volume": 2_000,
                "source": "fixture",
            }
        )
    return rows


class FuturesMacroV2IntegrationTests(unittest.TestCase):
    def test_fixed_cutoff_keeps_sunday_monday_pending_and_prior_state_immutable(self) -> None:
        from app.services.futures_macro_pattern import (
            build_pattern_feature_frame,
            build_pattern_state_frame,
        )
        from app.services.futures_macro_sessions import (
            select_completed_futures_daily_rows,
        )
        from app.services.futures_macro_thermometer import (
            normalize_futures_macro_daily_candles,
        )

        rows = _raw_daily_rows()
        before = select_completed_futures_daily_rows(
            rows,
            evaluation_time=datetime(2026, 7, 20, 12, 0, tzinfo=timezone.utc),
        )
        after = select_completed_futures_daily_rows(
            rows,
            evaluation_time=datetime(2026, 7, 20, 23, 0, tzinfo=timezone.utc),
        )
        before_features = build_pattern_feature_frame(
            normalize_futures_macro_daily_candles(before.rows),
            selected_symbols=SYMBOLS,
        )
        after_features = build_pattern_feature_frame(
            normalize_futures_macro_daily_candles(after.rows),
            selected_symbols=SYMBOLS,
        )
        before_state = build_pattern_state_frame(before_features)
        after_state = build_pattern_state_frame(after_features)

        self.assertEqual(before.latest_final_session, "2026-07-17")
        self.assertEqual(before.pending_session, "2026-07-20")
        self.assertEqual(after.latest_final_session, "2026-07-20")
        pd.testing.assert_series_equal(
            before_state.loc[pd.Timestamp("2026-07-17")],
            after_state.loc[pd.Timestamp("2026-07-17")],
        )

    def test_raw_to_v3_payload_preserves_dates_suppresses_geometry_and_repeats_identity(self) -> None:
        from app.services.futures_macro_pattern import (
            build_current_pattern_snapshot,
            build_pattern_feature_frame,
        )
        from app.services.futures_macro_pattern_validation import (
            build_pattern_outlook_snapshot,
        )
        from app.services.futures_macro_sessions import (
            select_completed_futures_daily_rows,
        )
        from app.services.futures_macro_snapshot import (
            build_compact_futures_macro_payload,
            build_futures_macro_forecast_identity,
            compute_futures_macro_input_fingerprint,
        )
        from app.services.futures_macro_thermometer import (
            normalize_futures_macro_daily_candles,
        )
        from app.web.overview.futures_macro_helpers import (
            build_futures_macro_react_workbench_payload,
        )

        completed = select_completed_futures_daily_rows(
            _raw_daily_rows(),
            evaluation_time=datetime(2026, 7, 20, 12, 0, tzinfo=timezone.utc),
        )
        candles = normalize_futures_macro_daily_candles(completed.rows)
        features = build_pattern_feature_frame(candles, selected_symbols=SYMBOLS)
        current = build_current_pattern_snapshot(features)
        outlook = build_pattern_outlook_snapshot(
            candles,
            features,
            current,
            selected_symbols=SYMBOLS,
        )
        outlook["session"] = {
            "latest_final_session": completed.latest_final_session,
            "pending_session": completed.pending_session,
            "status": "PENDING_SESSION_FINALIZATION",
        }
        fingerprint = compute_futures_macro_input_fingerprint(
            {"rows": completed.rows, "resolver_version": "futures_daily_session_v1"}
        )
        outlook["input_fingerprint"] = fingerprint
        macro = {
            "coverage": {"latest_daily_date": completed.latest_final_session},
            "summary": {},
            "pattern": current,
        }
        payload = build_futures_macro_react_workbench_payload(
            macro,
            pattern_outlook=outlook,
        )
        compact = build_compact_futures_macro_payload(
            macro,
            outlook,
            source_marker="2026-07-19 00:00:00",
            materialized_at="2026-07-20 12:00:00",
            input_fingerprint=fingerprint,
        )
        first_identity = build_futures_macro_forecast_identity(
            as_of_date=outlook["as_of_date"],
            input_fingerprint=fingerprint,
        )
        second_identity = build_futures_macro_forecast_identity(
            as_of_date=outlook["as_of_date"],
            input_fingerprint=fingerprint,
        )

        self.assertEqual(payload["schema_version"], "futures_macro_react_workbench_v3")
        self.assertEqual(len(payload["pattern_map"]["path"]), 30)
        self.assertEqual(
            [item["date"] for item in payload["pattern_map"]["path"]],
            [item["date"] for item in current["path"]],
        )
        for horizon in payload["horizons"][1:]:
            self.assertNotEqual(horizon["coordinate_status"], "VERIFIED")
            self.assertEqual(horizon["terminal_regions"], [])
            self.assertIsNone(horizon["direction_vector"])
        self.assertEqual(compact["input_fingerprint"], fingerprint)
        self.assertEqual(first_identity, second_identity)


if __name__ == "__main__":
    unittest.main()
