from __future__ import annotations

import math
from datetime import datetime

import pytest


def _decision(
    meeting_date: str,
    *,
    before: float,
    after: float,
    dissent_action: str | None = None,
) -> dict[str, object]:
    dissents = (
        []
        if dissent_action is None
        else [{"member_name": "Dissent", "preferred_action": dissent_action}]
    )
    return {
        "meeting_date": meeting_date,
        "released_at": f"{meeting_date} 18:00:00",
        "target_lower_before_pct": before - 0.125,
        "target_upper_before_pct": before + 0.125,
        "target_lower_after_pct": after - 0.125,
        "target_upper_after_pct": after + 0.125,
        "vote_for_count": 11 - len(dissents),
        "vote_against_count": len(dissents),
        "dissents_json": dissents,
        "coverage_status": "READY",
    }


def _sep_release(
    meeting_date: str,
    *,
    target_year: int,
    midpoint: float,
) -> list[dict[str, object]]:
    return [
        {
            "meeting_date": meeting_date,
            "released_at": f"{meeting_date} 18:00:00",
            "target_period": str(target_year),
            "variable_name": "federal_funds_rate",
            "distribution_kind": "DOT",
            "bin_value_pct": midpoint,
            "participant_count": 12,
        }
    ]


def test_probability_smoothing_preserves_simplex_and_opens_zero_classes() -> None:
    from finance.policy_validation import smooth_probability_row

    result = smooth_probability_row(
        {"cut": 0.0, "hold": 1.0, "hike": 0.0},
        labels=("cut", "hold", "hike"),
        smoothing=0.15,
    )

    assert result == pytest.approx({"cut": 0.05, "hold": 0.90, "hike": 0.05})
    assert math.isclose(sum(result.values()), 1.0)


def test_policy_artifact_fails_closed_when_completed_origins_are_missing() -> None:
    from finance.policy_validation import fit_policy_path_artifact

    artifact = fit_policy_path_artifact(
        (
            _decision("2025-09-17", before=4.375, after=4.125),
            _decision("2025-10-29", before=4.125, after=3.875),
        ),
        _sep_release("2025-09-17", target_year=2025, midpoint=3.625),
        as_of_at="2026-08-03T13:45:00+00:00",
    )

    assert artifact.publication_status == "NOT_AVAILABLE"
    assert "completed_year_end_origins_missing" in artifact.reason_codes


def test_year_end_validation_excludes_contemporaneous_final_meeting_sep() -> None:
    from finance.policy_validation import _year_end_rows

    decisions = (
        _decision("2024-03-20", before=5.375, after=5.375),
        _decision("2024-12-18", before=5.375, after=5.125),
    )
    sep_rows = (
        *_sep_release("2024-03-20", target_year=2024, midpoint=4.625),
        *_sep_release("2024-12-18", target_year=2024, midpoint=5.125),
    )

    forecasts, targets, baselines = _year_end_rows(
        decisions,
        sep_rows,
        cutoff=datetime.fromisoformat("2025-08-03T13:45:00+00:00"),
    )

    assert len(forecasts) == 1
    assert targets == ["cut_1"]
    assert all(len(rows) == 1 for rows in baselines.values())


def test_policy_artifact_uses_only_completed_targets_and_can_pass_relaxed_gate() -> None:
    from finance.policy_validation import fit_policy_path_artifact

    decisions = (
        _decision("2022-03-16", before=0.125, after=0.375),
        _decision("2022-06-15", before=0.375, after=0.625),
        _decision("2022-09-21", before=0.625, after=0.875),
        _decision("2022-12-14", before=0.875, after=1.125, dissent_action="HOLD"),
        _decision("2023-03-22", before=1.125, after=1.125),
        _decision("2023-06-14", before=1.125, after=1.125),
        _decision("2023-09-20", before=1.125, after=1.125),
        _decision("2023-12-13", before=1.125, after=1.125, dissent_action="CUT_25"),
        _decision("2024-03-20", before=1.125, after=0.875),
        _decision("2024-06-12", before=0.875, after=0.625),
        _decision("2024-09-18", before=0.625, after=0.375),
        _decision("2024-12-18", before=0.375, after=0.125),
        # Current-year rows have no completed year-end target and must not enter
        # the year-end validation sample.
        _decision("2025-03-19", before=0.125, after=0.125),
    )
    sep_rows: list[dict[str, object]] = []
    for meeting_date, target_year, target_midpoint in (
        ("2022-03-16", 2022, 1.125),
        ("2022-06-15", 2022, 1.125),
        ("2022-09-21", 2022, 1.125),
        ("2022-12-14", 2022, 1.125),
        ("2023-03-22", 2023, 1.125),
        ("2023-06-14", 2023, 1.125),
        ("2023-09-20", 2023, 1.125),
        ("2023-12-13", 2023, 1.125),
        ("2024-03-20", 2024, 0.125),
        ("2024-06-12", 2024, 0.125),
        ("2024-09-18", 2024, 0.125),
        ("2024-12-18", 2024, 0.125),
        ("2025-03-19", 2025, 0.125),
    ):
        sep_rows.extend(
            _sep_release(
                meeting_date,
                target_year=target_year,
                midpoint=target_midpoint,
            )
        )

    artifact = fit_policy_path_artifact(
        decisions,
        sep_rows,
        as_of_at="2025-08-03T13:45:00+00:00",
        minimum_next_origins=2,
        minimum_year_end_origins=2,
        minimum_calibration_rows=2,
        maximum_calibration_error=1.0,
        require_baseline_improvement=False,
    )

    assert artifact.publication_status == "READY"
    assert artifact.year_end_validation["origin_count"] == 7
    assert artifact.next_meeting_validation["origin_count"] >= 8
    assert artifact.trained_through_decision_date == "2025-03-19"
    assert 0.0 <= artifact.next_meeting_smoothing <= 0.40
    assert 0.0 <= artifact.year_end_smoothing <= 0.40
