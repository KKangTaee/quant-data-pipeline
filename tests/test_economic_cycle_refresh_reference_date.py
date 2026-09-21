from datetime import date, datetime

import pytest

from app.jobs import overview_actions
from app.services.overview import economic_cycle_freshness
from app.services.overview.economic_cycle_asset_freshness import (
    DAILY_MACRO_SERIES,
    DAILY_PRICE_SERIES,
    WEEKLY_MACRO_SERIES,
    build_asset_pathway_freshness,
)


def _asset_freshness(observation_date, reference_date):
    """Use real cadence evaluation with deterministic external-data fixtures."""
    return build_asset_pathway_freshness(
        [
            {"series_id": series, "observation_date": observation_date, "value": 1.0}
            for series in (*DAILY_MACRO_SERIES, *WEEKLY_MACRO_SERIES)
        ],
        [
            {"provider_symbol": symbol, "candle_time_utc": observation_date, "close": 100.0}
            for symbol in DAILY_PRICE_SERIES
        ],
        reference_date=reference_date,
    )


def _official_snapshot(*, as_of_date, run_kind):
    assert as_of_date == date(2026, 8, 31)
    assert run_kind == "current"
    return {
        "as_of_date": "2026-08-31",
        "run_kind": "current",
        "observed_state_json": {
            "source": "philadelphia_fed_rtdsm",
            "available_series": 4,
            "total_series": 4,
            "series_quality": [],
        },
    }


def _unexpected_collection(**_kwargs):
    raise AssertionError("A fresh scope must not collect or republish data")


@pytest.mark.parametrize(
    "requested_date",
    [date(2026, 9, 21), datetime(2026, 9, 21, 9, 0), "2026-09-21", None],
)
@pytest.mark.parametrize(
    "collected_date, expected_status, expected_scopes",
    [
        ("2026-09-18", "success", ["asset_pathways"]),
        ("2026-08-28", "incomplete", []),
    ],
)
def test_asset_refresh_checks_request_date_before_and_after_collection(
    monkeypatch, requested_date, collected_date, expected_status, expected_scopes
):
    class Today(date):
        @classmethod
        def today(cls):
            return cls(2026, 9, 21)

    monkeypatch.setattr(overview_actions, "date", Today)
    monkeypatch.setattr(economic_cycle_freshness, "date", Today)
    observation_date = "2026-08-28"
    collection_calls = []

    def load_assets(*, reference_date):
        return _asset_freshness(observation_date, reference_date)

    def collect_assets():
        nonlocal observation_date
        collection_calls.append("asset_pathways")
        observation_date = collected_date
        return {
            "job_name": "refresh_economic_cycle_asset_pathways",
            "status": "success",
            "rows_written": 15,
            "failed_symbols": [],
        }

    result = overview_actions.run_overview_economic_cycle_refresh(
        as_of_date=requested_date,
        snapshot_loader=_official_snapshot,
        refresh_runner=_unexpected_collection,
        asset_freshness_loader=load_assets,
        asset_refresh_runner=collect_assets,
    )

    assert collection_calls == ["asset_pathways"]
    assert result["status"] == expected_status
    assert result["details"]["requested_scopes"] == ["asset_pathways"]
    assert result["details"]["refreshed_scopes"] == expected_scopes
    assert result["details"]["cache_scopes"] == expected_scopes
    assert result["details"]["failed_scopes"] == (
        [] if expected_status == "success" else ["asset_pathways"]
    )
    assert result["details"]["target_as_of_date"] == "2026-08-31"
    assert result["details"]["before_as_of_date"] == "2026-08-31"
    assert result["details"]["after_as_of_date"] == "2026-08-31"


def test_current_assets_do_not_trigger_collection_against_previous_month():
    result = overview_actions.run_overview_economic_cycle_refresh(
        as_of_date=date(2026, 9, 21),
        snapshot_loader=_official_snapshot,
        refresh_runner=_unexpected_collection,
        asset_freshness_loader=lambda *, reference_date: _asset_freshness(
            "2026-09-18", reference_date
        ),
        asset_refresh_runner=_unexpected_collection,
    )

    assert result["status"] == "success"
    assert result["details"]["requested_scopes"] == []
    assert result["details"]["pipeline_status"] == "not_run"
    assert result["rows_written"] == 0
