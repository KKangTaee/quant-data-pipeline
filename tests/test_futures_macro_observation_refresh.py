from datetime import datetime, timezone


def snapshot(missing=()):
    return {
        "windows": {
            k: {
                "status": "PARTIAL" if missing else "AVAILABLE",
                "missing_symbols": list(missing),
            }
            for k in ("since_close", "last_hour")
        }
    }


def test_refresh_backfills_only_missing_symbols_once_per_bounded_period():
    from app.jobs.futures_macro_refresh import run_futures_macro_observation_refresh

    calls = []
    snapshots = iter(
        [snapshot(["6J=F"]), snapshot(["6J=F"]), snapshot(["6J=F"]), snapshot()]
    )

    def collect(**kwargs):
        calls.append(kwargs)
        return {"status": "success", "rows_written": 10, "failed_symbols": []}

    result = run_futures_macro_observation_refresh(
        evaluation_time=datetime(2026, 9, 21, 7, tzinfo=timezone.utc),
        window_loader=lambda **kw: next(snapshots),
        collect_runner=collect,
        daily_refresh_needed=lambda **kw: False,
        finalization_runner=lambda **kw: {"status": "not_required"},
        materialize_fn=lambda **kw: {"status": "reused"},
    )
    assert [(c["period"], c["interval"]) for c in calls] == [
        ("2d", "5m"),
        ("5d", "5m"),
        ("1mo", "5m"),
    ]
    assert calls[1]["symbols"] == ["6J=F"] and calls[2]["symbols"] == ["6J=F"]
    assert all(c["materialize_snapshot"] is False for c in calls)
    assert result["status"] == "success"


def test_good_endpoints_skip_backfill_and_daily_refresh():
    from app.jobs.futures_macro_refresh import run_futures_macro_observation_refresh

    calls = []

    def collect(**kw):
        calls.append(kw)
        return {"status": "success", "rows_written": 1, "failed_symbols": []}

    result = run_futures_macro_observation_refresh(
        evaluation_time=datetime(2026, 9, 21, 7, tzinfo=timezone.utc),
        window_loader=lambda **kw: snapshot(),
        collect_runner=collect,
        daily_refresh_needed=lambda **kw: False,
        finalization_runner=lambda **kw: {"status": "not_required"},
        materialize_fn=lambda **kw: {"status": "reused"},
    )
    assert len(calls) == 1 and calls[0]["interval"] == "5m"
    assert result["status"] == "success"


def test_provider_failure_is_bounded_and_does_not_report_success():
    from app.jobs.futures_macro_refresh import run_futures_macro_observation_refresh

    calls = []

    def fail(**kw):
        calls.append(kw)
        raise RuntimeError("provider offline")

    result = run_futures_macro_observation_refresh(
        evaluation_time=datetime(2026, 9, 21, 7, tzinfo=timezone.utc),
        window_loader=lambda **kw: snapshot(["6J=F"]),
        collect_runner=fail,
        daily_refresh_needed=lambda **kw: False,
        finalization_runner=lambda **kw: {"status": "not_required"},
        materialize_fn=lambda **kw: {"status": "reused"},
    )
    assert len(calls) == 3
    assert result["status"] != "success"
    assert result["details"]["windows"]["last_hour"]["status"] == "PARTIAL"


def test_materialization_failure_does_not_report_total_refresh_success():
    from app.jobs.futures_macro_refresh import run_futures_macro_observation_refresh

    r = run_futures_macro_observation_refresh(
        evaluation_time=datetime(2026, 9, 21, 7, tzinfo=timezone.utc),
        window_loader=lambda **kw: snapshot(),
        collect_runner=lambda **kw: {"status": "success", "rows_written": 1},
        daily_refresh_needed=lambda **kw: False,
        finalization_runner=lambda **kw: {"status": "not_required"},
        materialize_fn=lambda **kw: {"status": "unavailable"},
    )
    assert r["status"] == "partial_success"
