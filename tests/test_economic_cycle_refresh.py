from __future__ import annotations

from datetime import date


def _ready_asset_freshness(**_kwargs):
    return {"status": "READY", "refresh_required": False}


def test_cycle_freshness_uses_latest_closed_month_not_latest_weekday() -> None:
    from app.services.overview.economic_cycle_freshness import (
        build_economic_cycle_freshness,
        latest_closed_economic_cycle_month_end,
    )

    target = latest_closed_economic_cycle_month_end(date(2026, 8, 17))
    freshness = build_economic_cycle_freshness(
        {"as_of_date": "2026-07-31"},
        today=date(2026, 8, 17),
    )

    assert target == date(2026, 7, 31)
    assert freshness["target_as_of_date"] == "2026-07-31"
    assert freshness["status"] == "READY"
    assert freshness["refresh_required"] is False


def test_cycle_freshness_exposes_latest_rtdsm_observation_date() -> None:
    import json

    from app.services.overview.economic_cycle_freshness import (
        build_economic_cycle_freshness,
    )

    freshness = build_economic_cycle_freshness(
        {
            "as_of_date": "2026-07-31",
            "observed_state_json": json.dumps(
                {
                    "series_quality": [
                        {"series_id": "IPT", "latest_observation_date": "2026-06-01"},
                        {"series_id": "RUC", "latest_observation_date": "2026-04-01"},
                    ]
                }
            ),
        },
        today=date(2026, 8, 17),
    )

    assert freshness["latest_source_observation_date"] == "2026-06-01"


def test_cycle_freshness_requests_republish_for_legacy_quality_contract() -> None:
    import json

    from app.services.overview.economic_cycle_freshness import (
        build_economic_cycle_freshness,
    )

    freshness = build_economic_cycle_freshness(
        {
            "as_of_date": "2026-07-31",
            "observed_state_json": json.dumps(
                {
                    "phase": "recovery",
                    "source": "philadelphia_fed_rtdsm",
                    "activity_score": -0.4,
                    "labor_income_score": 0.1,
                }
            ),
        },
        today=date(2026, 8, 17),
    )

    assert freshness["status"] == "REFRESH_AVAILABLE"
    assert freshness["quality_refresh_required"] is True


def test_overview_republishes_current_month_when_quality_contract_is_legacy() -> None:
    import json

    from app.jobs.overview_actions import run_overview_economic_cycle_refresh

    old = {
        "as_of_date": "2026-07-31",
        "observed_state_json": json.dumps(
            {"source": "philadelphia_fed_rtdsm", "phase": "recovery"}
        ),
    }
    refreshed = {
        "as_of_date": "2026-07-31",
        "observed_state_json": json.dumps(
            {
                "source": "philadelphia_fed_rtdsm",
                "phase": "recovery",
                "available_series": 4,
                "total_series": 4,
                "series_quality": [],
            }
        ),
    }
    snapshots = iter([old, refreshed])
    calls: list[date] = []

    result = run_overview_economic_cycle_refresh(
        as_of_date=date(2026, 8, 17),
        refresh_runner=lambda *, as_of_date: calls.append(as_of_date)
        or {
            "job_name": "refresh_economic_cycle_official_month",
            "status": "success",
            "rows_written": 1,
            "failed_symbols": [],
        },
        snapshot_loader=lambda **_kwargs: next(snapshots),
        asset_freshness_loader=_ready_asset_freshness,
    )

    assert calls == [date(2026, 8, 17)]
    assert result["status"] == "success"
    assert result["details"]["refreshed_scopes"] == ["cycle_snapshot"]


def test_official_refresh_collects_only_rtdsm_then_publishes_closed_month() -> None:
    from app.jobs.economic_cycle_refresh import run_economic_cycle_official_refresh

    calls: list[tuple[str, date | None]] = []

    def collector():
        calls.append(("collect", None))
        return {
            "job_name": "collect_economic_cycle_rtdsm_history",
            "status": "success",
            "rows_written": 4,
            "symbols_requested": 4,
            "symbols_processed": 4,
            "failed_symbols": [],
        }

    def rollover(*, as_of_date, force_refresh):
        assert force_refresh is True
        calls.append(("rollover", as_of_date))
        return {"status": "created", "as_of_date": "2026-07-31", "rows_written": 1}

    result = run_economic_cycle_official_refresh(
        as_of_date=date(2026, 8, 17),
        collector=collector,
        rollover=rollover,
    )

    assert calls == [("collect", None), ("rollover", date(2026, 8, 17))]
    assert result["status"] == "success"
    assert result["details"]["as_of_date"] == "2026-07-31"
    assert result["details"]["series_scope"] == "RTDSM_4"


def test_official_refresh_preserves_snapshot_when_rtdsm_collection_has_gaps() -> None:
    from app.jobs.economic_cycle_refresh import run_economic_cycle_official_refresh

    result = run_economic_cycle_official_refresh(
        as_of_date=date(2026, 8, 17),
        collector=lambda: {
            "job_name": "collect_economic_cycle_rtdsm_history",
            "status": "partial_success",
            "rows_written": 3,
            "symbols_requested": 4,
            "symbols_processed": 3,
            "failed_symbols": ["RUC"],
        },
        rollover=lambda **_kwargs: (_ for _ in ()).throw(
            AssertionError("rollover must not run with incomplete RTDSM inputs")
        ),
    )

    assert result["status"] == "failed"
    assert result["failed_symbols"] == ["RUC"]
    assert result["details"]["snapshot_written"] is False


def test_overview_action_refreshes_the_latest_closed_official_month() -> None:
    from app.jobs.overview_actions import run_overview_economic_cycle_refresh

    runner_dates: list[date] = []
    loader_kinds: list[str] = []
    snapshots = iter(
        [{"as_of_date": "2026-06-30"}, {"as_of_date": "2026-07-31"}]
    )

    def load_snapshot(**kwargs):
        loader_kinds.append(str(kwargs.get("run_kind")))
        return next(snapshots)

    result = run_overview_economic_cycle_refresh(
        as_of_date=date(2026, 8, 17),
        refresh_runner=lambda *, as_of_date: runner_dates.append(as_of_date)
        or {
            "job_name": "refresh_economic_cycle_official_month",
            "status": "success",
            "rows_written": 1,
            "failed_symbols": [],
        },
        snapshot_loader=load_snapshot,
        asset_freshness_loader=_ready_asset_freshness,
    )

    assert runner_dates == [date(2026, 8, 17)]
    assert loader_kinds == ["current", "current"]
    assert result["details"]["target_as_of_date"] == "2026-07-31"
    assert result["details"]["after_as_of_date"] == "2026-07-31"


def test_refresh_stops_before_rollover_when_one_series_fails() -> None:
    from app.jobs.economic_cycle_refresh import run_economic_cycle_intramonth_refresh

    result = run_economic_cycle_intramonth_refresh(
        as_of_date="2026-07-21",
        collector=lambda **_kwargs: {
            "stored": 12,
            "failed": [{"series_id": "PAYEMS", "reason": "provider gap"}],
            "missing": [],
        },
        rollover=lambda **_kwargs: (_ for _ in ()).throw(
            AssertionError("rollover must not run")
        ),
        materializer=lambda **_kwargs: (_ for _ in ()).throw(
            AssertionError("materializer must not run")
        ),
    )

    assert result["status"] == "failed"
    assert result["rows_written"] == 0
    assert result["details"]["collection_rows_written"] == 12
    assert result["failed_symbols"] == ["PAYEMS"]


def test_refresh_runs_collect_rollover_materialize_in_order() -> None:
    from app.jobs.economic_cycle_refresh import run_economic_cycle_intramonth_refresh

    calls: list[tuple[str, date]] = []

    def collector(**_kwargs):
        calls.append(("collect", date(2026, 7, 21)))
        return {
            "stored": 17,
            "failed": [],
            "missing": [],
            "collection_mode": "incremental_overlap",
        }

    def rollover(*, as_of_date):
        calls.append(("rollover", as_of_date))
        return {"status": "current", "as_of_date": "2026-06-30", "rows_written": 0}

    def materializer(*, as_of_date):
        calls.append(("materialize", as_of_date))
        return type(
            "Snapshot",
            (),
            {"status": "LIMITED", "model_version": "cycle-v1"},
        )()

    result = run_economic_cycle_intramonth_refresh(
        as_of_date="2026-07-21",
        collector=collector,
        rollover=rollover,
        materializer=materializer,
    )

    assert calls == [
        ("collect", date(2026, 7, 21)),
        ("rollover", date(2026, 7, 21)),
        ("materialize", date(2026, 7, 21)),
    ]
    assert result["status"] == "partial_success"
    assert result["rows_written"] == 1
    assert result["details"]["as_of_date"] == "2026-07-21"
    assert result["details"]["collection_mode"] == "incremental_overlap"


def test_overview_action_uses_closed_month_and_requires_persisted_target() -> None:
    from app.jobs.overview_actions import run_overview_economic_cycle_refresh

    calls = []

    def runner(*, as_of_date):
        calls.append(as_of_date)
        return {
            "job_name": "refresh_economic_cycle_intramonth",
            "status": "partial_success",
            "rows_written": 1,
            "failed_symbols": [],
            "message": "provisional",
            "details": {},
        }

    rows = iter(
        [
            {"as_of_date": "2026-06-30", "run_kind": "current"},
            {"as_of_date": "2026-07-31", "run_kind": "current"},
        ]
    )
    result = run_overview_economic_cycle_refresh(
        as_of_date=date(2026, 8, 25),
        refresh_runner=runner,
        snapshot_loader=lambda **_kwargs: next(rows),
        asset_freshness_loader=_ready_asset_freshness,
    )

    assert calls == [date(2026, 8, 25)]
    assert result["status"] == "partial_success"
    assert result["details"]["target_as_of_date"] == "2026-07-31"
    assert result["details"]["after_as_of_date"] == "2026-07-31"


def test_overview_action_rejects_success_without_persisted_target() -> None:
    from app.jobs.overview_actions import run_overview_economic_cycle_refresh

    result = run_overview_economic_cycle_refresh(
        as_of_date=date(2026, 8, 25),
        refresh_runner=lambda **_kwargs: {
            "job_name": "refresh_economic_cycle_intramonth",
            "status": "success",
            "rows_written": 1,
            "failed_symbols": [],
            "message": "claimed success",
            "details": {},
        },
        snapshot_loader=lambda **_kwargs: {
            "as_of_date": "2026-06-30",
            "run_kind": "current",
        },
        asset_freshness_loader=_ready_asset_freshness,
    )

    assert result["status"] == "incomplete"
    assert result["details"]["after_as_of_date"] == "2026-06-30"
    assert "기존 2026-06-30 결과를 유지" in result["message"]


def test_overview_action_preserves_failed_pipeline_result() -> None:
    from app.jobs.overview_actions import run_overview_economic_cycle_refresh

    rows = iter(
        [
            {"as_of_date": "2026-06-30"},
            {"as_of_date": "2026-06-30"},
        ]
    )
    result = run_overview_economic_cycle_refresh(
        as_of_date=date(2026, 8, 25),
        refresh_runner=lambda **_kwargs: {
            "job_name": "refresh_economic_cycle_intramonth",
            "status": "failed",
            "rows_written": 0,
            "failed_symbols": ["PAYEMS"],
            "message": "gap",
            "details": {},
        },
        snapshot_loader=lambda **_kwargs: next(rows),
        asset_freshness_loader=_ready_asset_freshness,
    )

    assert result["status"] == "failed"
    assert result["rows_written"] == 0
    assert result["details"]["after_as_of_date"] == "2026-06-30"


def test_overview_action_skips_pipeline_when_target_is_already_persisted() -> None:
    from app.jobs.overview_actions import run_overview_economic_cycle_refresh

    result = run_overview_economic_cycle_refresh(
        as_of_date=date(2026, 8, 25),
        refresh_runner=lambda **_kwargs: (_ for _ in ()).throw(
            AssertionError("pipeline must not run")
        ),
        snapshot_loader=lambda **_kwargs: {
            "as_of_date": "2026-07-31",
            "run_kind": "current",
        },
        asset_freshness_loader=_ready_asset_freshness,
    )

    assert result["status"] == "success"
    assert result["rows_written"] == 0
    assert result["details"]["before_as_of_date"] == "2026-07-31"
    assert result["details"]["pipeline_status"] == "not_run"


def test_overview_action_reports_runner_exception_and_preserves_prior_date() -> None:
    from app.jobs.overview_actions import run_overview_economic_cycle_refresh

    result = run_overview_economic_cycle_refresh(
        as_of_date=date(2026, 8, 25),
        refresh_runner=lambda **_kwargs: (_ for _ in ()).throw(
            RuntimeError("provider unavailable")
        ),
        snapshot_loader=lambda **_kwargs: {
            "as_of_date": "2026-06-30",
            "run_kind": "current",
        },
        asset_freshness_loader=_ready_asset_freshness,
    )

    assert result["status"] == "failed"
    assert result["details"]["before_as_of_date"] == "2026-06-30"
    assert result["details"]["after_as_of_date"] == "2026-06-30"
    assert "기존 2026-06-30 결과를 유지" in result["message"]


def test_overview_refresh_runs_only_stale_asset_scope() -> None:
    from app.jobs.overview_actions import run_overview_economic_cycle_refresh

    calls: list[str] = []
    asset_rows = iter(
        [
            {"status": "REFRESH_AVAILABLE", "refresh_required": True},
            {"status": "READY", "refresh_required": False},
        ]
    )

    result = run_overview_economic_cycle_refresh(
        as_of_date=date(2026, 8, 10),
        refresh_runner=lambda **_kwargs: (_ for _ in ()).throw(
            AssertionError("cycle refresh must not run")
        ),
        snapshot_loader=lambda **_kwargs: {"as_of_date": "2026-08-10"},
        asset_freshness_loader=lambda **_kwargs: next(asset_rows),
        asset_refresh_runner=lambda: calls.append("asset")
        or {
            "job_name": "refresh_economic_cycle_asset_pathways",
            "status": "success",
            "rows_written": 10,
            "failed_symbols": [],
        },
    )

    assert calls == ["asset"]
    assert result["status"] == "success"
    assert result["details"]["requested_scopes"] == ["asset_pathways"]
    assert result["details"]["cache_scopes"] == ["asset_pathways"]


def test_overview_refresh_runs_only_stale_cycle_scope() -> None:
    from app.jobs.overview_actions import run_overview_economic_cycle_refresh

    snapshots = iter(
        [{"as_of_date": "2026-06-30"}, {"as_of_date": "2026-07-31"}]
    )
    cycle_calls: list[date] = []

    result = run_overview_economic_cycle_refresh(
        as_of_date=date(2026, 8, 10),
        refresh_runner=lambda *, as_of_date: cycle_calls.append(as_of_date)
        or {
            "job_name": "refresh_economic_cycle_intramonth",
            "status": "success",
            "rows_written": 1,
            "failed_symbols": [],
        },
        snapshot_loader=lambda **_kwargs: next(snapshots),
        asset_freshness_loader=lambda **_kwargs: {
            "status": "READY",
            "refresh_required": False,
        },
        asset_refresh_runner=lambda: (_ for _ in ()).throw(
            AssertionError("asset refresh must not run")
        ),
    )

    assert cycle_calls == [date(2026, 8, 10)]
    assert result["details"]["requested_scopes"] == ["cycle_snapshot"]
    assert result["details"]["cache_scopes"] == ["cycle_snapshot"]


def test_overview_refresh_keeps_successful_asset_scope_when_cycle_fails() -> None:
    from app.jobs.overview_actions import run_overview_economic_cycle_refresh

    snapshots = iter(
        [{"as_of_date": "2026-06-30"}, {"as_of_date": "2026-06-30"}]
    )
    assets = iter(
        [
            {
                "status": "REFRESH_AVAILABLE",
                "refresh_required": True,
                "stale_series": ["DGS2"],
            },
            {
                "status": "READY",
                "refresh_required": False,
                "stale_series": [],
            },
        ]
    )

    result = run_overview_economic_cycle_refresh(
        as_of_date=date(2026, 8, 10),
        refresh_runner=lambda **_kwargs: {
            "job_name": "refresh_economic_cycle_intramonth",
            "status": "failed",
            "rows_written": 0,
            "failed_symbols": ["PAYEMS"],
        },
        snapshot_loader=lambda **_kwargs: next(snapshots),
        asset_freshness_loader=lambda **_kwargs: next(assets),
        asset_refresh_runner=lambda: {
            "job_name": "refresh_economic_cycle_asset_pathways",
            "status": "success",
            "rows_written": 10,
            "failed_symbols": [],
        },
    )

    assert result["status"] == "partial_success"
    assert result["details"]["cache_scopes"] == ["asset_pathways"]
    assert result["details"]["failed_scopes"] == ["cycle_snapshot"]
    assert result["details"]["after_as_of_date"] == "2026-06-30"
