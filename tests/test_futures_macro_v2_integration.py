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
    def test_evening_reopen_keeps_sunday_monday_pending_and_prior_state_immutable(self) -> None:
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
        self.assertEqual(after.latest_final_session, "2026-07-17")
        self.assertEqual(after.pending_session, "2026-07-20")
        pd.testing.assert_frame_equal(before_state, after_state)
        pd.testing.assert_series_equal(
            before_state.loc[pd.Timestamp("2026-07-17")],
            after_state.loc[pd.Timestamp("2026-07-17")],
        )
