from __future__ import annotations

import importlib
import unittest
from datetime import date, timedelta


def _calibration():
    try:
        return importlib.import_module("app.services.portfolio_monitoring.calibration")
    except ModuleNotFoundError as exc:
        raise AssertionError("portfolio monitoring calibration module is required") from exc


class PortfolioMonitoringCalibrationTests(unittest.TestCase):
    def test_historical_replay_rejects_revised_non_pit_and_overlap_rows(self) -> None:
        calibration = _calibration()
        samples = [
            {"id": "train-ok", "as_of_date": "2025-01-02", "macro_vintage_date": "2025-01-02", "pit_exposure": True, "outcome_end_date": "2025-02-03", "outcome": 0},
            {"id": "future-vintage", "as_of_date": "2025-01-02", "macro_vintage_date": "2025-02-01", "pit_exposure": True, "outcome_end_date": "2025-02-03", "outcome": 0},
            {"id": "non-pit", "as_of_date": "2025-01-03", "macro_vintage_date": "2025-01-03", "pit_exposure": False, "outcome_end_date": "2025-02-04", "outcome": 1},
            {"id": "overlap", "as_of_date": "2025-05-15", "macro_vintage_date": "2025-05-15", "pit_exposure": True, "outcome_end_date": "2025-07-10", "outcome": 1},
            {"id": "validation-ok", "as_of_date": "2025-07-15", "macro_vintage_date": "2025-07-15", "pit_exposure": True, "outcome_end_date": "2025-08-15", "outcome": 1},
        ]

        replay = calibration.build_historical_replay(
            samples,
            split_dates={"train_end": "2025-06-30", "validation_start": "2025-07-14", "validation_end": "2025-12-31"},
            embargo_sessions=5,
        )

        self.assertEqual([row["id"] for row in replay.train_rows], ["train-ok"])
        self.assertEqual([row["id"] for row in replay.validation_rows], ["validation-ok"])
        self.assertEqual(set(replay.rejected), {"future-vintage", "non-pit", "overlap"})
        self.assertIn("future macro vintage", replay.rejected["future-vintage"])
        self.assertIn("non-PIT", replay.rejected["non-pit"])
        self.assertIn("embargo", replay.rejected["overlap"])

    def test_calibrator_reports_oos_brier_baseline_reliability_and_fingerprints(self) -> None:
        calibration = _calibration()
        train = [{"id": f"t{i}", "outcome": int(i < 60), "predicted_probability": 0.9 if i < 60 else 0.05} for i in range(300)]
        validation = [{"id": f"v{i}", "outcome": int(i < 60), "predicted_probability": 0.9 if i < 60 else 0.05} for i in range(300)]

        first = calibration.calibrate_risk_probability(train, validation)
        second = calibration.calibrate_risk_probability(train, validation)

        self.assertLess(first.brier_score, first.baseline_brier)
        self.assertLessEqual(first.max_reliability_error, 0.10)
        self.assertEqual(first.sample_size, 300)
        self.assertEqual(first.positive_count, 60)
        self.assertTrue(first.reliability_buckets)
        self.assertEqual(len(first.confidence_interval), 2)
        self.assertEqual(first.algorithm_fingerprint, second.algorithm_fingerprint)
        self.assertEqual(first.data_fingerprint, second.data_fingerprint)

    def test_publication_gate_suppresses_insufficient_and_integrity_blocked_artifacts(self) -> None:
        calibration = _calibration()
        small = calibration.calibrate_risk_probability(
            [{"outcome": 0, "predicted_probability": 0.1}] * 20,
            [{"outcome": int(i < 10), "predicted_probability": 0.5} for i in range(40)],
        )
        decision = calibration.evaluate_publication_gate(small)
        self.assertEqual(decision.status, "SUPPRESSED")
        self.assertIsNone(decision.probability)
        self.assertTrue(any("250" in reason for reason in decision.reasons))

        blocked = calibration.calibrate_risk_probability(
            [{"outcome": 0, "predicted_probability": 0.1}] * 300,
            [{"outcome": int(i < 60), "predicted_probability": 0.9 if i < 60 else 0.05} for i in range(300)],
            integrity_blockers=["future-revised macro vintage"],
        )
        self.assertEqual(calibration.evaluate_publication_gate(blocked).status, "SUPPRESSED")

    def test_publication_gate_requires_five_percent_brier_gain_and_reliability(self) -> None:
        calibration = _calibration()
        weak = calibration.calibrate_risk_probability(
            [{"outcome": int(i < 60), "predicted_probability": 0.2} for i in range(300)],
            [{"outcome": int(i < 60), "predicted_probability": 0.2} for i in range(300)],
        )
        weak_decision = calibration.evaluate_publication_gate(weak)
        self.assertEqual(weak_decision.status, "LIMITED")
        self.assertIsNone(weak_decision.probability)

        ready = calibration.calibrate_risk_probability(
            [{"outcome": int(i < 60), "predicted_probability": 0.9 if i < 60 else 0.05} for i in range(300)],
            [{"outcome": int(i < 60), "predicted_probability": 0.9 if i < 60 else 0.05} for i in range(300)],
        )
        ready_decision = calibration.evaluate_publication_gate(ready)
        self.assertEqual(ready_decision.status, "READY")
        self.assertIsNotNone(ready_decision.probability)
        self.assertEqual(ready_decision.sample_size, 300)


if __name__ == "__main__":
    unittest.main()
