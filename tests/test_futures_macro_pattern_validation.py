from __future__ import annotations

import unittest
from unittest.mock import patch

import pandas as pd

from app.services.futures_macro_pattern import (
    build_current_pattern_snapshot,
    build_pattern_feature_frame,
)
from tests.test_futures_macro_pattern import SYMBOLS, _pattern_candles


def _validation_fixture(*, days: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    candles = _pattern_candles(days=days)
    features = build_pattern_feature_frame(candles, selected_symbols=SYMBOLS)
    return candles, features


def _dated_feature_frame(count: int) -> pd.DataFrame:
    dates = pd.bdate_range("2020-01-02", periods=count)
    return pd.DataFrame({"value": range(count)}, index=dates).rename_axis("Date")


def _outlook_fixture(*, days: int) -> dict[str, object]:
    candles, features = _validation_fixture(days=days)
    return {
        "candles": candles,
        "feature_frame": features,
        "current_pattern": build_current_pattern_snapshot(features),
        "selected_symbols": SYMBOLS,
    }


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


class FuturesMacroPatternPublicationTests(unittest.TestCase):
    def test_publication_status_requires_sample_brier_and_calibration(self) -> None:
        from app.services.futures_macro_pattern_validation import publication_status_for_metrics

        cases = (
            (29, 0.20, 0.25, 0.04, "UNAVAILABLE"),
            (30, 0.20, 0.25, 0.04, "PROVISIONAL"),
            (59, 0.20, 0.25, 0.04, "PROVISIONAL"),
            (60, 0.20, 0.25, 0.04, "VERIFIED"),
            (60, 0.26, 0.25, 0.04, "PROVISIONAL"),
            (60, 0.20, 0.25, 0.15, "PROVISIONAL"),
        )
        for episodes, brier, baseline_brier, calibration, expected in cases:
            with self.subTest(episodes=episodes, brier=brier, calibration=calibration):
                self.assertEqual(
                    publication_status_for_metrics(
                        episode_count=episodes,
                        brier_score=brier,
                        baseline_brier_score=baseline_brier,
                        calibration_error=calibration,
                        fold_improvement_ratio=0.67,
                    ),
                    expected,
                )

    def test_multiclass_brier_scores_probability_error(self) -> None:
        from app.services.futures_macro_pattern_validation import multiclass_brier_score

        score = multiclass_brier_score(
            ["defensive", "risk_seeking"],
            [
                {"defensive": 0.7, "risk_seeking": 0.1, "inflation_rate_pressure": 0.1, "mixed": 0.1},
                {"defensive": 0.2, "risk_seeking": 0.6, "inflation_rate_pressure": 0.1, "mixed": 0.1},
            ],
        )

        self.assertIsNotNone(score)
        self.assertAlmostEqual(float(score), 0.17, places=8)

    def test_walk_forward_folds_are_chronological_and_embargoed(self) -> None:
        from app.services.futures_macro_pattern_validation import build_walk_forward_folds

        frame = _dated_feature_frame(1200)
        folds = build_walk_forward_folds(frame, horizon=20)

        self.assertGreaterEqual(len(folds), 3)
        for fold in folds:
            self.assertLess(fold.train_end, fold.test_start)
            self.assertGreater(
                frame.index.get_loc(fold.test_start) - frame.index.get_loc(fold.train_end),
                20,
            )

    def test_outlook_reports_baseline_lift_and_no_edge_when_not_distinct(self) -> None:
        from app.services.futures_macro_pattern_validation import build_pattern_outlook_snapshot

        snapshot = build_pattern_outlook_snapshot(**_outlook_fixture(days=300))
        horizon = snapshot["horizons"][0]

        self.assertAlmostEqual(sum(horizon["probabilities"].values()), 1.0, places=8)
        self.assertEqual(set(horizon["probability_lift"]), set(horizon["baseline_probabilities"]))
        self.assertEqual(horizon["edge_label"], "방향 우위 미확인")

    def test_outlook_keeps_current_pattern_when_validation_is_unavailable(self) -> None:
        from app.services.futures_macro_pattern_validation import build_pattern_outlook_snapshot

        snapshot = build_pattern_outlook_snapshot(**_outlook_fixture(days=100))

        self.assertEqual(snapshot["status"], "LIMITED")
        self.assertTrue(
            all(item["estimate_status"] == "UNAVAILABLE" for item in snapshot["horizons"])
        )
        self.assertIn(snapshot["current_pattern"]["status"], {"READY", "PARTIAL"})

    def test_pattern_outlook_cache_reuses_marker_and_rebuilds_on_new_daily_row(self) -> None:
        import app.services.futures_macro_pattern_validation as service

        marker = {"value": "2026-07-17"}
        calls: list[dict[str, object]] = []

        def query_fn(db_name: str, sql: str, params=None):
            del db_name, sql, params
            return []

        def build(*args, **kwargs):
            del args
            calls.append(kwargs)
            return {"call": len(calls)}

        with (
            patch.object(service, "_latest_daily_cache_marker", side_effect=lambda query, symbols: marker["value"]),
            patch.object(service, "_load_validation_futures_rows", return_value=[]),
            patch.object(service, "build_pattern_outlook_snapshot", side_effect=build),
        ):
            service.clear_futures_macro_pattern_validation_cache()
            first = service.load_overview_futures_macro_pattern_outlook(
                query_fn=query_fn,
                symbols=("ES=F",),
                cache_ttl_seconds=60,
            )
            second = service.load_overview_futures_macro_pattern_outlook(
                query_fn=query_fn,
                symbols=("ES=F",),
                cache_ttl_seconds=60,
            )
            marker["value"] = "2026-07-18"
            third = service.load_overview_futures_macro_pattern_outlook(
                query_fn=query_fn,
                symbols=("ES=F",),
                cache_ttl_seconds=60,
            )

        self.assertIs(first, second)
        self.assertEqual(third["call"], 2)


if __name__ == "__main__":
    unittest.main()
