from __future__ import annotations

import pandas as pd

from finance.economic_cycle_observed_state import PHASE_SEQUENCE
from finance.economic_cycle_transition_dataset import TransitionDataset


def _vintage(
    series_id: str,
    observation_date: str,
    released_at: str,
    value: float,
) -> dict[str, object]:
    return {
        "series_id": series_id,
        "observation_date": observation_date,
        "released_at": released_at,
        "value": value,
    }


def _complete_rows() -> list[dict[str, object]]:
    from finance.economic_cycle_transition_drivers import REQUIRED_DRIVER_SERIES

    rows: list[dict[str, object]] = []
    dates = pd.date_range("1999-01-31", periods=18, freq="ME")
    for series_index, series_id in enumerate(REQUIRED_DRIVER_SERIES):
        for month_index, date in enumerate(dates):
            base = 100.0 + series_index + month_index
            if series_id not in {"PCEPILFE", "PERMIT"}:
                base = 1.0 + series_index * 0.1 + month_index * 0.02
            rows.append(
                _vintage(
                    series_id,
                    date.date().isoformat(),
                    (date + pd.Timedelta(days=1)).isoformat() + "Z",
                    base,
                )
            )
    return rows


def test_driver_panel_uses_only_releases_known_at_each_origin() -> None:
    from finance.economic_cycle_transition_drivers import (
        build_transition_driver_panel,
    )

    rows = [
        _vintage("DGS2", "2000-01-31", "2000-02-01T00:00:00Z", 5.0),
        _vintage("DGS2", "2000-01-31", "2000-04-01T00:00:00Z", 9.0),
        _vintage("DGS2", "2000-02-29", "2000-03-01T00:00:00Z", 4.0),
    ]

    panel = build_transition_driver_panel(
        rows,
        pd.to_datetime(["2000-02-29", "2000-04-30"]),
    )

    assert panel.loc[0, "DGS2_level"] == 5.0
    assert panel.loc[1, "DGS2_level"] == 4.0


def test_core_pce_and_curve_features_are_contextual_not_single_sign_rules() -> None:
    from finance.economic_cycle_transition_drivers import (
        build_transition_driver_panel,
    )

    panel = build_transition_driver_panel(
        _complete_rows(),
        pd.to_datetime(["2000-06-30"]),
    )

    assert {
        "PCEPILFE_3m_ann",
        "PCEPILFE_gap_2pct",
        "yield_curve_10y2y",
        "yield_curve_delta_3m",
        "DGS2_delta_1m",
        "DGS2_delta_6m",
    } <= set(panel)
    assert pd.notna(panel.loc[0, "PCEPILFE_3m_ann"])
    assert panel.loc[0, "yield_curve_10y2y"] == (
        panel.loc[0, "DGS10_level"] - panel.loc[0, "DGS2_level"]
    )


def test_market_features_do_not_use_prices_after_the_origin() -> None:
    from finance.economic_cycle_transition_drivers import (
        build_transition_driver_panel,
    )

    prices = [
        {
            "provider_symbol": "^GSPC",
            "candle_time_utc": "2000-01-31",
            "close": 100.0,
        },
        {
            "provider_symbol": "^GSPC",
            "candle_time_utc": "2000-02-29",
            "close": 110.0,
        },
        {
            "provider_symbol": "^GSPC",
            "candle_time_utc": "2000-03-31",
            "close": 220.0,
        },
    ]

    panel = build_transition_driver_panel(
        (),
        pd.to_datetime(["2000-02-29"]),
        market_rows=prices,
    )

    assert panel.loc[0, "SP500_return_1m_pct"] == 10.0


def _base_dataset() -> TransitionDataset:
    dates = pd.date_range("2000-01-31", periods=8, freq="ME")
    phases = (
        "recovery",
        "recovery",
        "expansion",
        "expansion",
        "slowdown",
        "slowdown",
        "contraction",
        "contraction",
    )
    rows = pd.DataFrame(
        {
            "forecast_origin": dates,
            "episode_id": (0, 0, 1, 1, 2, 2, 3, 3),
            "confirmed_phase": phases,
            "confirmed_transition_to": (
                None,
                None,
                "expansion",
                None,
                "slowdown",
                None,
                "contraction",
                None,
            ),
            "destination_target": (
                "expansion",
                "expansion",
                "slowdown",
                "slowdown",
                "contraction",
                "contraction",
                None,
                None,
            ),
            "eligible": (True,) * 8,
            "ineligible_reason": ("",) * 8,
            "episode_weight": (0.5,) * 8,
            "core_feature": tuple(float(index) for index in range(8)),
        }
    )
    return TransitionDataset(feature_names=("core_feature",), rows=rows)


def _state_frame() -> pd.DataFrame:
    rows = _base_dataset().rows
    return rows[
        ["forecast_origin", "episode_id", "confirmed_phase", "confirmed_transition_to"]
    ].copy()


def test_extended_dataset_keeps_core_rows_and_marks_missing_driver_rows_ineligible() -> None:
    from finance.economic_cycle_transition_drivers import extend_transition_dataset

    features = pd.DataFrame(
        {
            "forecast_origin": _base_dataset().rows["forecast_origin"],
            "DGS2_level": (None, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6),
        }
    )

    extended = extend_transition_dataset(
        _base_dataset(),
        features,
        ("DGS2_level",),
    )

    assert len(extended.rows) == len(_base_dataset().rows)
    assert extended.rows.loc[0, "ineligible_reason"] == "MISSING_DRIVER_FEATURE"
    assert not bool(extended.rows.loc[0, "eligible"])
    assert extended.rows.groupby("episode_id")["episode_weight"].sum().max() == 1.0


def test_driver_coverage_counts_unique_transition_episodes() -> None:
    from finance.economic_cycle_transition_drivers import (
        DriverCoverageGate,
        audit_transition_driver_coverage,
        extend_transition_dataset,
    )

    features = pd.DataFrame(
        {
            "forecast_origin": _base_dataset().rows["forecast_origin"],
            "DGS2_level": tuple(1.0 + index for index in range(8)),
        }
    )
    extended = extend_transition_dataset(
        _base_dataset(),
        features,
        ("DGS2_level",),
    )
    gate = DriverCoverageGate(
        minimum_usable_origins=1,
        minimum_independent_transitions=3,
        minimum_destination_events=0,
        minimum_holdout_destination_events=0,
    )

    report = audit_transition_driver_coverage(
        extended,
        _state_frame(),
        ("DGS2_level",),
        gate=gate,
    )

    assert report.independent_transitions == 3
    assert report.destination_counts == {
        "recovery": 0,
        "expansion": 1,
        "slowdown": 1,
        "contraction": 1,
    }
    assert report.status == "DRIVER_READY"
    assert set(report.destination_counts) == set(PHASE_SEQUENCE)
