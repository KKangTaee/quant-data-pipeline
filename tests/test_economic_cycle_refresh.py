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
