from __future__ import annotations

import math
import unittest

import pandas as pd

from tests.test_futures_macro_pattern import _feature_frame


def _predictor_fixture(count: int = 120) -> pd.DataFrame:
    from app.services.futures_macro_outlook_model import (
        MOMENTUM_PREDICTOR_COLUMNS,
    )

    dates = pd.bdate_range("2025-01-02", periods=count)
    rows = []
    for index in range(count):
        rows.append(
            {
                column: float(((index + offset * 3) % 17) / 10.0)
                for offset, column in enumerate(MOMENTUM_PREDICTOR_COLUMNS)
            }
        )
    return pd.DataFrame(rows, index=dates).rename_axis("Date")


def _context_fixture(index: pd.Index) -> pd.DataFrame:
    from app.services.futures_macro_context import (
        EVENT_CONTEXT_COLUMNS,
        MACRO_CONTEXT_COLUMNS,
    )

    frame = pd.DataFrame(index=index)
    for offset, column in enumerate((*MACRO_CONTEXT_COLUMNS, *EVENT_CONTEXT_COLUMNS)):
        frame[column] = [float(((position + offset) % 11) / 10.0) for position in range(len(index))]
    return frame


class MomentumPredictorTests(unittest.TestCase):
    def test_inner_selection_chooses_momentum_when_it_has_lower_brier(self) -> None:
        from app.services.futures_macro_outlook_model import (
            select_candidate_from_inner_evaluations,
        )

        selected = select_candidate_from_inner_evaluations(
            pd.DataFrame(
                [
                    {"candidate": "M1_MOMENTUM", "temperature": 1.0, "brier_loss": 0.31},
                    {"candidate": "M1_MOMENTUM", "temperature": 1.0, "brier_loss": 0.29},
                    {"candidate": "M2B_BALANCED", "temperature": 1.0, "brier_loss": 0.38},
                    {"candidate": "M2B_BALANCED", "temperature": 1.0, "brier_loss": 0.34},
                ]
            )
        )

        self.assertEqual(selected["candidate"], "M1_MOMENTUM")
        self.assertEqual(selected["temperature"], 1.0)

    def test_inner_selection_allows_hybrid_only_when_it_wins(self) -> None:
        from app.services.futures_macro_outlook_model import (
            select_candidate_from_inner_evaluations,
        )

        selected = select_candidate_from_inner_evaluations(
            pd.DataFrame(
                [
                    {"candidate": "M1_MOMENTUM", "temperature": 0.5, "brier_loss": 0.42},
                    {"candidate": "M2A_LIGHT", "temperature": 0.5, "brier_loss": 0.33},
                    {"candidate": "M2B_BALANCED", "temperature": 0.5, "brier_loss": 0.35},
                ]
            )
        )

        self.assertEqual(selected["candidate"], "M2A_LIGHT")

    def test_inner_selection_tie_prefers_simpler_candidate_then_lower_temperature(self) -> None:
        from app.services.futures_macro_outlook_model import (
            select_candidate_from_inner_evaluations,
        )

        selected = select_candidate_from_inner_evaluations(
            pd.DataFrame(
                [
                    {"candidate": "M2C_MACRO_SENSITIVE", "temperature": 0.5, "brier_loss": 0.30},
                    {"candidate": "M1_MOMENTUM", "temperature": 2.0, "brier_loss": 0.30},
                    {"candidate": "M1_MOMENTUM", "temperature": 0.5, "brier_loss": 0.30},
                ]
            )
        )

        self.assertEqual(selected, {
            "candidate": "M1_MOMENTUM",
            "temperature": 0.5,
            "mean_brier": 0.30,
            "evaluation_count": 1,
        })

    def test_inner_selection_rejects_candidate_without_shared_fold_coverage(self) -> None:
        from app.services.futures_macro_outlook_model import (
            select_candidate_from_inner_evaluations,
        )

        selected = select_candidate_from_inner_evaluations(
            pd.DataFrame(
                [
                    {"candidate": "M1_MOMENTUM", "temperature": 1.0, "brier_loss": 0.30},
                    {"candidate": "M1_MOMENTUM", "temperature": 1.0, "brier_loss": 0.32},
                    {"candidate": "M2B_BALANCED", "temperature": 1.0, "brier_loss": 0.01},
                ]
            )
        )

        self.assertEqual(selected["candidate"], "M1_MOMENTUM")


    def test_projection_uses_the_fixed_sixteen_predictors(self) -> None:
        from app.services.futures_macro_outlook_model import (
            MOMENTUM_PREDICTOR_COLUMNS,
            build_momentum_predictor_frame,
        )

        features = _feature_frame(
            risk_on=(0.8, 0.5, -0.2),
            rate_pressure=(0.4, 0.2, 0.1),
            dollar_pressure=(0.2, 0.0, -0.1),
            inflation_pressure=(0.6, 0.4, 0.3),
        )
        predictors = build_momentum_predictor_frame(
            features,
            selected_symbol_count=15,
        )
        latest = predictors.iloc[-1]

        self.assertEqual(tuple(predictors.columns), MOMENTUM_PREDICTOR_COLUMNS)
        self.assertAlmostEqual(latest["state_x"], 0.5)
        self.assertAlmostEqual(latest["state_y"], 0.2)
        self.assertAlmostEqual(latest["impulse_x"], 0.3)
        self.assertAlmostEqual(latest["impulse_y"], 0.2)
        self.assertEqual(latest["coverage_ratio"], 1.0)

    def test_ranking_excludes_overlap_and_spaces_episode_origins(self) -> None:
        from app.services.futures_macro_outlook_model import (
            CANDIDATES,
            rank_weighted_analog_episodes,
        )

        predictors = _predictor_fixture()
        current_date = predictors.index[-1]
        ranked = rank_weighted_analog_episodes(
            predictors,
            pd.DataFrame(index=predictors.index),
            current_date=current_date,
            horizon=20,
            candidate=CANDIDATES[0],
            temperature=1.0,
            max_episodes=10,
        )
        positions = sorted(predictors.index.get_loc(value) for value in ranked["as_of_date"])
        current_position = predictors.index.get_loc(current_date)

        self.assertTrue(all(position <= current_position - 21 for position in positions))
        self.assertGreaterEqual(min(b - a for a, b in zip(positions, positions[1:])), 20)
        self.assertTrue(ranked["combined_distance"].is_monotonic_increasing)

    def test_train_scaling_ignores_rows_after_the_forecast_origin(self) -> None:
        from app.services.futures_macro_outlook_model import (
            CANDIDATES,
            rank_weighted_analog_episodes,
        )

        predictors = _predictor_fixture()
        current_date = predictors.index[-21]
        before = rank_weighted_analog_episodes(
            predictors,
            pd.DataFrame(index=predictors.index),
            current_date=current_date,
            horizon=5,
            candidate=CANDIDATES[0],
            temperature=1.0,
        )
        mutated = predictors.copy()
        mutated.loc[mutated.index > current_date, :] = 999.0
        after = rank_weighted_analog_episodes(
            mutated,
            pd.DataFrame(index=mutated.index),
            current_date=current_date,
            horizon=5,
            candidate=CANDIDATES[0],
            temperature=1.0,
        )

        pd.testing.assert_frame_equal(before, after)

    def test_episode_weight_uses_the_selected_temperature(self) -> None:
        from app.services.futures_macro_outlook_model import (
            CANDIDATES,
            rank_weighted_analog_episodes,
        )

        predictors = _predictor_fixture()
        ranked = rank_weighted_analog_episodes(
            predictors,
            pd.DataFrame(index=predictors.index),
            current_date=predictors.index[-1],
            horizon=5,
            candidate=CANDIDATES[0],
            temperature=2.0,
            max_episodes=5,
        )

        self.assertAlmostEqual(
            ranked.iloc[0]["weight"],
            math.exp(-ranked.iloc[0]["combined_distance"] / 2.0),
        )

    def test_missing_macro_context_disables_hybrid_but_not_momentum(self) -> None:
        from app.services.futures_macro_outlook_model import (
            CANDIDATES,
            rank_weighted_analog_episodes,
        )

        predictors = _predictor_fixture()
        empty_context = pd.DataFrame(index=predictors.index)
        momentum = rank_weighted_analog_episodes(
            predictors,
            empty_context,
            current_date=predictors.index[-1],
            horizon=5,
            candidate=CANDIDATES[0],
            temperature=1.0,
        )
        hybrid_missing = rank_weighted_analog_episodes(
            predictors,
            empty_context,
            current_date=predictors.index[-1],
            horizon=5,
            candidate=CANDIDATES[2],
            temperature=1.0,
        )
        hybrid_ready = rank_weighted_analog_episodes(
            predictors,
            _context_fixture(predictors.index),
            current_date=predictors.index[-1],
            horizon=5,
            candidate=CANDIDATES[2],
            temperature=1.0,
        )

        self.assertFalse(momentum.empty)
        self.assertTrue(hybrid_missing.empty)
        self.assertEqual(hybrid_missing.attrs["unavailable_reason"], "macro_context_missing")
        self.assertFalse(hybrid_ready.empty)


if __name__ == "__main__":
    unittest.main()
