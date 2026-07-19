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


def _feature_frame(
    *,
    risk_on: tuple[float, float, float] = (0.1, 0.1, 0.1),
    growth: tuple[float, float, float] = (0.1, 0.1, 0.1),
    rate_pressure: tuple[float, float, float] = (0.1, 0.1, 0.1),
    dollar_pressure: tuple[float, float, float] = (0.1, 0.1, 0.1),
    safe_haven: tuple[float, float, float] = (0.1, 0.1, 0.1),
    inflation_pressure: tuple[float, float, float] = (0.1, 0.1, 0.1),
    drop_families: set[str] | None = None,
) -> pd.DataFrame:
    family_values = {
        "risk_on": risk_on,
        "growth": growth,
        "rate_pressure": rate_pressure,
        "dollar_pressure": dollar_pressure,
        "safe_haven": safe_haven,
        "inflation_pressure": inflation_pressure,
    }
    dates = pd.bdate_range("2026-06-01", periods=4)
    rows: list[dict[str, object]] = []
    for row_index, _ in enumerate(dates):
        record: dict[str, object] = {"available_symbol_count": 15}
        for family, (one_day, five_day, twenty_day) in family_values.items():
            record[f"{family}__1d_z"] = one_day
            record[f"{family}__5d_z"] = five_day
            record[f"{family}__20d_z"] = twenty_day
            record[f"{family}__5d_slope"] = five_day - twenty_day
            record[f"{family}__20d_slope"] = twenty_day * 0.2
            record[f"{family}__acceleration"] = one_day - five_day
            record[f"{family}__5d_persistence"] = 0.8
            record[f"{family}__20d_persistence"] = 0.75
            record[f"{family}__breadth"] = 0.75
            record[f"{family}__volatility_ratio"] = 1.0
        if row_index < len(dates) - 1:
            record["risk_on__1d_z"] = float(record["risk_on__1d_z"]) * 0.8
        rows.append(record)
    frame = pd.DataFrame(rows, index=dates).rename_axis("Date")
    for family in drop_families or set():
        frame.loc[:, [column for column in frame.columns if column.startswith(f"{family}__")]] = float("nan")
    return frame


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


class FuturesMacroCurrentPatternTests(unittest.TestCase):
    def test_current_pattern_labels_persistent_defensive_regime(self) -> None:
        from app.services.futures_macro_pattern import build_current_pattern_snapshot

        frame = _feature_frame(
            risk_on=(-1.1, -1.4, -1.2),
            safe_haven=(0.8, 1.0, 0.9),
            dollar_pressure=(0.4, 0.7, 0.6),
        )

        snapshot = build_current_pattern_snapshot(frame)

        self.assertEqual(snapshot["regime"], "defensive")
        self.assertEqual(snapshot["transition"], "persisting")
        self.assertIn("방어", snapshot["summary"])
        self.assertEqual(snapshot["path"][-1]["date"], frame.index[-1].date().isoformat())

    def test_current_pattern_labels_transition_attempt_when_short_windows_reverse_month(self) -> None:
        from app.services.futures_macro_pattern import build_current_pattern_snapshot

        snapshot = build_current_pattern_snapshot(
            _feature_frame(
                risk_on=(0.9, 0.7, -1.2),
                safe_haven=(-0.6, -0.6, 0.8),
            )
        )

        self.assertEqual(snapshot["transition"], "transition_attempt")
        self.assertTrue(any("5D" in item for item in snapshot["change_conditions"]))

    def test_current_pattern_keeps_conflict_and_low_signal_distinct(self) -> None:
        from app.services.futures_macro_pattern import build_current_pattern_snapshot

        conflict = build_current_pattern_snapshot(
            _feature_frame(
                risk_on=(0.9, 0.9, 0.8),
                growth=(0.7, 0.7, 0.7),
                safe_haven=(0.8, 0.8, 0.7),
            )
        )
        quiet = build_current_pattern_snapshot(_feature_frame())

        self.assertEqual((conflict["regime"], conflict["transition"]), ("mixed", "conflicting"))
        self.assertEqual((quiet["regime"], quiet["transition"]), ("mixed", "low_signal"))

    def test_current_pattern_returns_partial_without_forcing_missing_family(self) -> None:
        from app.services.futures_macro_pattern import build_current_pattern_snapshot

        snapshot = build_current_pattern_snapshot(
            _feature_frame(drop_families={"dollar_pressure"})
        )

        self.assertEqual(snapshot["status"], "PARTIAL")
        self.assertEqual(snapshot["families"]["dollar_pressure"]["status"], "UNAVAILABLE")


if __name__ == "__main__":
    unittest.main()
