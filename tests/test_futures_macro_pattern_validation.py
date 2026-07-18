from __future__ import annotations

import unittest

import pandas as pd

from app.services.futures_macro_pattern import build_pattern_feature_frame
from tests.test_futures_macro_pattern import SYMBOLS, _pattern_candles


def _validation_fixture(*, days: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    candles = _pattern_candles(days=days)
    features = build_pattern_feature_frame(candles, selected_symbols=SYMBOLS)
    return candles, features


class FuturesMacroPatternOutcomeTests(unittest.TestCase):
    def test_forward_outcomes_use_as_of_volatility_and_exclusive_regimes(self) -> None:
        from app.services.futures_macro_pattern_validation import (
            OUTCOME_REGIMES,
            build_forward_outcome_frame,
        )

        candles, features = _validation_fixture(days=180)
        outcomes = build_forward_outcome_frame(
            candles,
            features,
            selected_symbols=SYMBOLS,
        )

        self.assertEqual(set(outcomes["horizon"]), {5, 20})
        self.assertTrue(outcomes["outcome_regime"].isin(OUTCOME_REGIMES).all())
        self.assertEqual(outcomes.groupby(["as_of_date", "horizon"]).size().max(), 1)
        self.assertTrue((outcomes["risk_on__path_iqr_z"] >= 0.0).all())
        self.assertTrue((outcomes["risk_on__max_adverse_z"] <= 0.0).all())
        self.assertGreater(outcomes["risk_on__path_iqr_z"].max(), 0.0)

    def test_appending_future_rows_does_not_change_completed_forward_label(self) -> None:
        from app.services.futures_macro_pattern_validation import build_forward_outcome_frame

        base_candles, base_features = _validation_fixture(days=160)
        more_candles, more_features = _validation_fixture(days=180)
        before = build_forward_outcome_frame(
            base_candles,
            base_features,
            selected_symbols=SYMBOLS,
        )
        after = build_forward_outcome_frame(
            more_candles,
            more_features,
            selected_symbols=SYMBOLS,
        )
        key = before.iloc[-30][["as_of_date", "horizon"]].tolist()
        left = before[(before["as_of_date"] == key[0]) & (before["horizon"] == key[1])].iloc[0]
        right = after[(after["as_of_date"] == key[0]) & (after["horizon"] == key[1])].iloc[0]

        self.assertEqual(left["outcome_regime"], right["outcome_regime"])

    def test_similar_episodes_exclude_overlap_and_separate_trading_row_anchors(self) -> None:
        from app.services.futures_macro_pattern_validation import select_similar_episodes

        _, features = _validation_fixture(days=260)
        current_date = features.index[-1]
        matches = select_similar_episodes(
            features,
            current_date=current_date,
            horizon=20,
        )
        positions = [features.index.get_loc(date) for date in matches["as_of_date"]]
        current_position = features.index.get_loc(current_date)
        ordered = sorted(positions)

        self.assertGreaterEqual(len(positions), 2)
        self.assertTrue(all(position <= current_position - 20 - 1 for position in positions))
        self.assertGreaterEqual(min(right - left for left, right in zip(ordered, ordered[1:])), 20)
        self.assertTrue(matches["similarity_distance"].is_monotonic_increasing)

    def test_similarity_scaling_ignores_rows_after_the_current_date(self) -> None:
        from app.services.futures_macro_pattern_validation import select_similar_episodes

        _, features = _validation_fixture(days=260)
        current_date = features.index[-21]
        base = select_similar_episodes(
            features,
            current_date=current_date,
            horizon=5,
        )
        mutated = features.copy()
        mutated.iloc[-20:, :] = 999.0
        after = select_similar_episodes(
            mutated,
            current_date=current_date,
            horizon=5,
        )

        pd.testing.assert_series_equal(
            base["as_of_date"],
            after["as_of_date"],
        )


if __name__ == "__main__":
    unittest.main()
