from __future__ import annotations

from collections import Counter
from datetime import date

import pytest


def _episode(
    *,
    year: int,
    month: int,
    q4: float,
    steps: int,
    shift: float,
):
    from finance.joint_rate_paths import RateEpisode

    rates = {
        "DGS2": (3.50, 3.50 + shift),
        "DGS10": (4.40, 4.40 + shift * 0.6),
        "DFII10": (1.90, 1.90 + shift * 0.4),
        "T10YIE": (2.50, 2.50 + shift * 0.2),
    }
    return RateEpisode(
        origin_date=date(year, month, 28),
        target_date=date(year, 12, 31),
        origin_month=month,
        current_rates={key: values[0] for key, values in rates.items()},
        endpoint_rates={key: values[-1] for key, values in rates.items()},
        rate_paths_pct=rates,
        q4_core_pce_pct=q4,
        policy_net_steps=steps,
    )


def test_rank_copula_paths_preserve_requested_marginals_and_current_rate_start() -> None:
    from finance.joint_rate_paths import simulate_joint_rate_paths

    episodes = tuple(
        _episode(
            year=2018 + index,
            month=7,
            q4=2.0 + index * 0.5,
            steps=index - 2,
            shift=(index - 2) * 0.20,
        )
        for index in range(5)
    )
    levels = {
        date(2025, 10, 1): 100.0,
        date(2025, 11, 1): 100.2,
        date(2025, 12, 1): 100.4,
        date(2026, 1, 1): 100.6,
        date(2026, 2, 1): 100.8,
        date(2026, 3, 1): 101.0,
        date(2026, 4, 1): 101.2,
        date(2026, 5, 1): 101.4,
        date(2026, 6, 1): 101.6,
    }
    q4_samples = tuple(2.5 + index * 0.01 for index in range(100))

    paths = simulate_joint_rate_paths(
        episodes,
        q4_samples_pct=q4_samples,
        policy_net_move_probabilities={
            "cut_3_plus": 0.0,
            "cut_2": 0.0,
            "cut_1": 0.20,
            "hold": 0.50,
            "hike_1": 0.30,
            "hike_2": 0.0,
            "hike_3_plus": 0.0,
        },
        current_rates={
            "DGS2": 3.70,
            "DGS10": 4.68,
            "DFII10": 2.10,
            "T10YIE": 2.58,
        },
        current_policy_midpoint_pct=3.625,
        levels=levels,
        forecast_months=tuple(date(2026, month, 1) for month in range(7, 13)),
        rate_scales={key: 1.0 for key in ("DGS2", "DGS10", "DFII10", "T10YIE")},
        sample_count=100,
        seed=7,
    )

    assert sorted(path.q4_core_pce_pct for path in paths) == pytest.approx(
        sorted(q4_samples)
    )
    step_counts = Counter(path.policy_net_steps for path in paths)
    assert step_counts[-1] == pytest.approx(20, abs=8)
    assert step_counts[0] == pytest.approx(50, abs=10)
    assert step_counts[1] == pytest.approx(30, abs=8)
    assert all(path.rate_paths_pct["DGS10"][0] == 4.68 for path in paths)
    assert all(
        path.year_end_policy_midpoint_pct
        == pytest.approx(3.625 + 0.25 * path.policy_net_steps)
        for path in paths
    )
    assert all(len(path.remaining_monthly_mom_pct) == 6 for path in paths)


def test_joint_artifact_fails_closed_without_a_chronological_rate_library() -> None:
    from finance.joint_rate_paths import fit_joint_rate_path_artifact

    artifact = fit_joint_rate_path_artifact(
        macro_rows=(),
        q4_samples_pct=(2.5, 2.6),
        policy_net_move_probabilities={"hold": 1.0},
        levels={},
        forecast_months=(date(2026, 12, 1),),
        current_policy_midpoint_pct=3.625,
        as_of_at="2026-08-03T03:15:00+00:00",
        sample_count=100,
        seed=3,
    )

    assert artifact.publication_status == "NOT_AVAILABLE"
    assert "rate_episode_library_missing" in artifact.reason_codes
    assert artifact.paths == ()


def test_series_map_excludes_observations_or_releases_after_cutoff() -> None:
    from finance.joint_rate_paths import _series_map

    rows = (
        {
            "series_id": "DGS10",
            "observation_date": "2026-07-30",
            "released_at": "2026-07-30T21:00:00Z",
            "value": 4.68,
        },
        {
            "series_id": "DGS10",
            "observation_date": "2026-07-30",
            "released_at": "2026-08-04T12:00:00Z",
            "value": 9.99,
        },
        {
            "series_id": "DGS10",
            "observation_date": "2026-08-04",
            "released_at": "2026-08-04T21:00:00Z",
            "value": 8.88,
        },
    )

    series = _series_map(rows, cutoff_at="2026-08-03T03:15:00Z")

    assert series["DGS10"] == ((date(2026, 7, 30), 4.68),)


def test_joint_artifact_materializes_paths_only_after_all_gates_pass(
    monkeypatch,
) -> None:
    import importlib

    module = importlib.import_module("finance.joint_rate_paths")
    episodes = tuple(
        _episode(year=1990 + index, month=7, q4=2.0, steps=0, shift=0.1)
        for index in range(25)
    )
    instrument_metrics = {
        instrument: {
            "crps": 0.1,
            "baseline_crps": 0.2,
            "calibration_error": 0.1,
            "origin_count": 48,
        }
        for instrument in module.RATE_INSTRUMENTS
    }
    current_series = {
        instrument: ((date(2026, 7, 30), 4.0),)
        for instrument in module.RATE_INSTRUMENTS
    }
    current_series.update({"FEDFUNDS": (), "PCEPILFE": ()})

    monkeypatch.setattr(module, "build_rate_episodes", lambda *_args, **_kwargs: episodes)
    monkeypatch.setattr(
        module,
        "validate_rate_episode_library",
        lambda _episodes: (
            {"instruments": instrument_metrics, "minimum_origin_count": 48},
            {instrument: 1.0 for instrument in module.RATE_INSTRUMENTS},
        ),
    )
    monkeypatch.setattr(
        module,
        "validate_dynamic_resistance_reach",
        lambda *_args, **_kwargs: {
            "origin_count": 48.0,
            "brier_score": 0.1,
            "baseline_brier_score": 0.2,
            "calibration_error": 0.1,
        },
    )
    monkeypatch.setattr(module, "_series_map", lambda *_args, **_kwargs: current_series)
    monkeypatch.setattr(
        module,
        "simulate_joint_rate_paths",
        lambda *_args, **_kwargs: ("validated-path",),
    )

    artifact = module.fit_joint_rate_path_artifact(
        macro_rows=(),
        q4_samples_pct=(2.5, 2.6),
        policy_net_move_probabilities={"hold": 1.0},
        levels={},
        forecast_months=(date(2026, 12, 1),),
        current_policy_midpoint_pct=3.625,
        as_of_at="2026-08-03T03:15:00Z",
        sample_count=100,
        seed=3,
    )

    assert artifact.publication_status == "READY"
    assert artifact.reason_codes == ()
    assert artifact.paths == ("validated-path",)
