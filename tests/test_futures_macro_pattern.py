from __future__ import annotations

import unittest

import pandas as pd


SYMBOLS = (
    "ES=F",
    "NQ=F",
    "YM=F",
    "RTY=F",
    "ZN=F",
    "ZB=F",
    "GC=F",
    "CL=F",
    "NG=F",
    "HG=F",
    "6E=F",
    "6J=F",
    "6B=F",
    "6A=F",
    "6C=F",
)


def _pattern_candles(*, days: int, shock_start: int | None = None) -> pd.DataFrame:
    dates = pd.bdate_range("2025-01-02", periods=days)
    risk_symbols = {"ES=F", "NQ=F", "YM=F", "RTY=F", "HG=F", "CL=F", "6A=F"}
    bond_symbols = {"ZN=F", "ZB=F"}
    fx_symbols = {"6E=F", "6J=F", "6B=F", "6A=F", "6C=F"}
    records: list[dict[str, object]] = []

    for symbol_index, symbol in enumerate(SYMBOLS):
        price = 90.0 + symbol_index * 4.0
        for index, current_date in enumerate(dates):
            daily_move = 0.0004 + 0.0018 * ((index % 7) - 3) / 3
            if shock_start is not None and index >= shock_start:
                if symbol in risk_symbols:
                    daily_move += 0.008
                if symbol in bond_symbols:
                    daily_move -= 0.007
                if symbol in fx_symbols:
                    daily_move -= 0.006
            price *= 1.0 + daily_move
            records.append(
                {
                    "provider_symbol": symbol,
                    "ts": current_date,
                    "Date": current_date.date().isoformat(),
                    "Close": price,
                }
            )
    return pd.DataFrame(records)


class FuturesMacroPatternFeatureTests(unittest.TestCase):
    def test_pattern_feature_frame_uses_trailing_rows_and_inverts_rates_and_fx(self) -> None:
        from app.services.futures_macro_pattern import build_pattern_feature_frame

        frame = build_pattern_feature_frame(
            _pattern_candles(days=90, shock_start=70),
            selected_symbols=SYMBOLS,
        )

        self.assertEqual(frame.index.name, "Date")
        self.assertEqual(list(frame.index), sorted(frame.index))
        latest = frame.iloc[-1]
        self.assertGreater(latest["risk_on__5d_z"], 0)
        self.assertGreater(latest["rate_pressure__5d_z"], 0)
        self.assertGreater(latest["dollar_pressure__5d_z"], 0)
        self.assertGreaterEqual(latest["risk_on__5d_persistence"], 0.0)
        self.assertLessEqual(latest["risk_on__5d_persistence"], 1.0)
        self.assertGreaterEqual(latest["risk_on__breadth"], 0.0)
        self.assertLessEqual(latest["risk_on__breadth"], 1.0)

    def test_pattern_feature_frame_is_stable_when_future_rows_are_appended(self) -> None:
        from app.services.futures_macro_pattern import build_pattern_feature_frame

        before = build_pattern_feature_frame(
            _pattern_candles(days=80, shock_start=70),
            selected_symbols=SYMBOLS,
        )
        after = build_pattern_feature_frame(
            _pattern_candles(days=90, shock_start=70),
            selected_symbols=SYMBOLS,
        )

        pd.testing.assert_series_equal(
            before.iloc[-1],
            after.loc[before.index[-1]],
            check_names=False,
        )

    def test_pattern_feature_frame_requires_past_sixty_day_volatility(self) -> None:
        from app.services.futures_macro_pattern import build_pattern_feature_frame

        frame = build_pattern_feature_frame(
            _pattern_candles(days=40),
            selected_symbols=SYMBOLS,
        )

        self.assertTrue(frame.empty)


if __name__ == "__main__":
    unittest.main()
