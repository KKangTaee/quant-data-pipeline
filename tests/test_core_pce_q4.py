from __future__ import annotations

from datetime import datetime, timezone


def _spf_rows() -> tuple[dict[str, object], ...]:
    probabilities = (3.0, 23.0, 31.0, 27.0, 11.0, 4.0, 1.0, 0.0, 0.0, 0.0)
    labels = (
        (">=4.0", 4.0, None),
        ("3.5-3.9", 3.5, 3.9),
        ("3.0-3.4", 3.0, 3.4),
        ("2.5-2.9", 2.5, 2.9),
        ("2.0-2.4", 2.0, 2.4),
        ("1.5-1.9", 1.5, 1.9),
        ("1.0-1.4", 1.0, 1.4),
        ("0.5-0.9", 0.5, 0.9),
        ("0.0-0.4", 0.0, 0.4),
        ("decline", None, 0.0),
    )
    return tuple(
        {
            "survey_year": 2026,
            "survey_quarter": 2,
            "target_year": 2026,
            "bin_number": index,
            "bin_label": label,
            "bin_lower_pct": lower,
            "bin_upper_pct": upper,
            "mean_probability_pct": probability,
            "released_at": "2026-05-16 03:59:59.999999",
        }
        for index, (probability, (label, lower, upper)) in enumerate(
            zip(probabilities, labels, strict=True), start=1
        )
    )


def test_spf_distribution_samples_use_latest_complete_target_year_density() -> None:
    from finance.core_pce_q4 import spf_probability_samples

    samples, released_at = spf_probability_samples(
        _spf_rows(), target_year=2026, sample_count=1_000
    )

    assert len(samples) == 1_000
    assert released_at == "2026-05-16 03:59:59.999999"
    assert min(samples) >= 1.2
    assert max(samples) == 4.25
    assert sum(sample >= 3.5 for sample in samples) / len(samples) == 0.26


def test_q4_actual_uses_one_consistent_target_release_vintage_after_rebasing() -> None:
    from finance.core_pce_q4 import _actual_q4_targets

    rows = []
    for year, first_level, consistent_level in ((2024, 110.0, 100.0), (2025, 102.0, 102.0)):
        for month in (10, 11, 12):
            first_release = (
                f"{year + (1 if month == 12 else 0)}-"
                f"{1 if month == 12 else month + 1:02d}-28T13:30:00+00:00"
            )
            rows.append(
                {
                    "series_id": "PCEPILFE",
                    "observation_date": f"{year}-{month:02d}-01",
                    "realtime_start": first_release[:10],
                    "released_at": first_release,
                    "value": first_level,
                }
            )
            rows.append(
                {
                    "series_id": "PCEPILFE",
                    "observation_date": f"{year}-{month:02d}-01",
                    "realtime_start": "2026-01-28",
                    "released_at": "2026-01-28T13:30:00+00:00",
                    "value": consistent_level,
                }
            )

    targets = _actual_q4_targets(
        rows, cutoff=datetime(2026, 8, 3, tzinfo=timezone.utc)
    )

    assert round(targets[2025][0], 8) == 2.0
    assert targets[2025][1].isoformat() == "2026-01-28T13:30:00+00:00"


def test_q4_linear_pool_uses_only_completed_prior_targets_and_can_publish() -> None:
    from finance.core_pce_q4 import Q4ValidationOrigin, fit_q4_linear_pool
    from finance.inflation_policy_validation import PublicationThresholds

    origins = []
    for year in range(2018, 2026):
        actual = 2.0 + (year - 2018) * 0.2
        for quarter, month in enumerate((2, 5, 8, 11), start=1):
            origins.append(
                Q4ValidationOrigin(
                    forecast_origin_at=f"{year}-{month:02d}-15T20:00:00+00:00",
                    target_available_at=(
                        f"{year + 1}-01-31T13:30:00+00:00"
                    ),
                    target_year=year,
                    actual_q4_pct=actual,
                    model_samples_pct=(actual - 0.1, actual, actual + 0.1),
                    spf_samples_pct=(actual - 0.6, actual - 0.5, actual - 0.4),
                    naive_prediction_pct=actual - 1.0,
                )
            )

    artifact = fit_q4_linear_pool(
        origins,
        as_of_at=datetime(2026, 8, 3, tzinfo=timezone.utc),
        thresholds=PublicationThresholds(
            minimum_origins=24,
            minimum_complete_feature_ratio=1.0,
            maximum_calibration_error=0.60,
            require_baseline_improvement=True,
        ),
        minimum_target_years=6,
        candidate_model_weights=(0.0, 0.25, 0.50, 0.75),
        default_model_weight=0.25,
    )

    assert artifact.publication_status == "READY"
    assert artifact.validation_metrics["origin_count"] == 32.0
    assert artifact.validation_metrics["target_year_count"] == 8.0
    assert artifact.validation_metrics["latest_training_target_through_at"] < (
        "2026-08-03T00:00:00+00:00"
    )
    assert artifact.model_weight == 0.50
    assert artifact.spf_weight == 0.50
    assert artifact.validation_metrics["crps"] < artifact.validation_metrics["baseline_crps"]


def test_q4_linear_pool_stays_limited_when_independent_target_years_are_too_few() -> None:
    from finance.core_pce_q4 import Q4ValidationOrigin, fit_q4_linear_pool
    from finance.inflation_policy_validation import PublicationThresholds

    origins = tuple(
        Q4ValidationOrigin(
            forecast_origin_at=f"2025-{month:02d}-15T20:00:00+00:00",
            target_available_at="2026-01-31T13:30:00+00:00",
            target_year=2025,
            actual_q4_pct=3.0,
            model_samples_pct=(2.9, 3.0, 3.1),
            spf_samples_pct=(2.8, 3.0, 3.2),
            naive_prediction_pct=2.0,
        )
        for month in (2, 5, 8, 11)
    )

    artifact = fit_q4_linear_pool(
        origins,
        as_of_at="2026-08-03T03:00:00+00:00",
        thresholds=PublicationThresholds(1, 1.0, 1.0, False),
        minimum_target_years=2,
    )

    assert artifact.publication_status == "LIMITED"
    assert "insufficient_independent_target_years" in artifact.publication_reasons
