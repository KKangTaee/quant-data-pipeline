from __future__ import annotations

from datetime import date


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


def test_overview_action_uses_previous_friday_and_requires_persisted_target() -> None:
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
            {"as_of_date": "2026-07-21", "run_kind": "intramonth_nowcast"},
            {"as_of_date": "2026-07-24", "run_kind": "intramonth_nowcast"},
        ]
    )
    result = run_overview_economic_cycle_refresh(
        as_of_date=date(2026, 7, 25),
        refresh_runner=runner,
        snapshot_loader=lambda **_kwargs: next(rows),
    )

    assert calls == [date(2026, 7, 24)]
    assert result["status"] == "partial_success"
    assert result["details"]["target_as_of_date"] == "2026-07-24"
    assert result["details"]["after_as_of_date"] == "2026-07-24"


def test_overview_action_rejects_success_without_persisted_target() -> None:
    from app.jobs.overview_actions import run_overview_economic_cycle_refresh

    result = run_overview_economic_cycle_refresh(
        as_of_date=date(2026, 7, 25),
        refresh_runner=lambda **_kwargs: {
            "job_name": "refresh_economic_cycle_intramonth",
            "status": "success",
            "rows_written": 1,
            "failed_symbols": [],
            "message": "claimed success",
            "details": {},
        },
        snapshot_loader=lambda **_kwargs: {
            "as_of_date": "2026-07-21",
            "run_kind": "intramonth_nowcast",
        },
    )

    assert result["status"] == "incomplete"
    assert result["details"]["after_as_of_date"] == "2026-07-21"
    assert "기존 2026-07-21 결과를 유지" in result["message"]


def test_overview_action_preserves_failed_pipeline_result() -> None:
    from app.jobs.overview_actions import run_overview_economic_cycle_refresh

    rows = iter(
        [
            {"as_of_date": "2026-07-21"},
            {"as_of_date": "2026-07-21"},
        ]
    )
    result = run_overview_economic_cycle_refresh(
        as_of_date=date(2026, 7, 25),
        refresh_runner=lambda **_kwargs: {
            "job_name": "refresh_economic_cycle_intramonth",
            "status": "failed",
            "rows_written": 0,
            "failed_symbols": ["PAYEMS"],
            "message": "gap",
            "details": {},
        },
        snapshot_loader=lambda **_kwargs: next(rows),
    )

    assert result["status"] == "failed"
    assert result["rows_written"] == 0
    assert result["details"]["after_as_of_date"] == "2026-07-21"


def test_overview_action_skips_pipeline_when_target_is_already_persisted() -> None:
    from app.jobs.overview_actions import run_overview_economic_cycle_refresh

    result = run_overview_economic_cycle_refresh(
        as_of_date=date(2026, 7, 25),
        refresh_runner=lambda **_kwargs: (_ for _ in ()).throw(
            AssertionError("pipeline must not run")
        ),
        snapshot_loader=lambda **_kwargs: {
            "as_of_date": "2026-07-24",
            "run_kind": "intramonth_nowcast",
        },
    )

    assert result["status"] == "success"
    assert result["rows_written"] == 0
    assert result["details"]["before_as_of_date"] == "2026-07-24"
    assert result["details"]["pipeline_status"] == "not_run"


def test_overview_action_reports_runner_exception_and_preserves_prior_date() -> None:
    from app.jobs.overview_actions import run_overview_economic_cycle_refresh

    result = run_overview_economic_cycle_refresh(
        as_of_date=date(2026, 7, 25),
        refresh_runner=lambda **_kwargs: (_ for _ in ()).throw(
            RuntimeError("provider unavailable")
        ),
        snapshot_loader=lambda **_kwargs: {
            "as_of_date": "2026-07-21",
            "run_kind": "intramonth_nowcast",
        },
    )

    assert result["status"] == "failed"
    assert result["details"]["before_as_of_date"] == "2026-07-21"
    assert result["details"]["after_as_of_date"] == "2026-07-21"
    assert "기존 2026-07-21 결과를 유지" in result["message"]
