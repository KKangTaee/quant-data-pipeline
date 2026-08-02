from __future__ import annotations

import json


def _required_success_collectors():
    return {
        "macro_vintages": lambda: {"status": "success", "rows": 100},
        "sep": lambda: {"status": "success", "rows": 40},
        "decisions": lambda: {"status": "success", "rows": 6},
        "term_premium": lambda: {
            "status": "success",
            "rows": 500,
            "coverage_status": "LIMITED",
        },
        "pce_components": lambda: {"status": "success", "rows": 120},
    }


def test_partial_required_source_failure_blocks_materialization() -> None:
    from app.jobs.inflation_policy_refresh import run_inflation_policy_raw_refresh

    collectors = _required_success_collectors()
    collectors["sep"] = lambda: {"status": "failed", "rows": 0}

    result = run_inflation_policy_raw_refresh(collectors=collectors)

    assert result["status"] == "failed"
    assert result["failed_sources"] == ["sep"]
    assert result["materialization_allowed"] is False


def test_optional_source_limit_degrades_without_blocking_required_data() -> None:
    from app.jobs.inflation_policy_refresh import run_inflation_policy_raw_refresh

    collectors = _required_success_collectors()
    collectors["term_premium"] = lambda: {
        "status": "failed",
        "rows": 0,
        "reason": "workbook unavailable",
    }
    collectors["pce_components"] = lambda: {
        "status": "not_available",
        "rows": 0,
        "reason": "BEA_API_KEY missing",
    }

    result = run_inflation_policy_raw_refresh(collectors=collectors)

    assert result["status"] == "partial_success"
    assert result["failed_sources"] == []
    assert result["limited_sources"] == ["pce_components", "term_premium"]
    assert result["materialization_allowed"] is True


def test_macro_coverage_gap_identifies_required_series() -> None:
    from app.jobs.inflation_policy_refresh import run_inflation_policy_raw_refresh

    collectors = _required_success_collectors()
    collectors["macro_vintages"] = lambda: {
        "status": "success",
        "stored": 20,
        "coverage": {
            "PCEPILFE": 5,
            "DGS2": 5,
            "DGS10": 0,
            "DFII10": 5,
            "T10YIE": 5,
        },
    }

    result = run_inflation_policy_raw_refresh(collectors=collectors)

    assert result["status"] == "failed"
    assert result["required_series_gaps"] == ["DGS10"]
    assert result["materialization_allowed"] is False


def test_scheduler_registers_weekday_job_outside_browser_safe() -> None:
    from app.jobs.overview_automation import OVERVIEW_AUTOMATION_JOB_SPECS

    spec = next(
        item for item in OVERVIEW_AUTOMATION_JOB_SPECS
        if item.job_id == "inflation_policy_raw"
    )

    assert spec.cadence_minutes == 24 * 60
    assert spec.profiles == ("safe", "standard", "broad")
    assert "browser_safe" not in spec.profiles
    assert spec.weekdays_only is True


def test_ingestion_wrapper_returns_compact_job_result(monkeypatch) -> None:
    import app.jobs.ingestion_jobs as module

    monkeypatch.setattr(
        module,
        "run_inflation_policy_raw_refresh",
        lambda **_kwargs: {
            "status": "partial_success",
            "rows_written": 166,
            "failed_sources": [],
            "limited_sources": ["term_premium"],
            "materialization_allowed": True,
            "sources": {},
        },
        raising=False,
    )

    result = module.run_collect_inflation_policy_raw_context(
        as_of_at="2026-08-02T03:15:00+00:00"
    )

    assert result["job_name"] == "collect_inflation_policy_raw_context"
    assert result["status"] == "partial_success"
    assert result["rows_written"] == 166
    assert result["details"]["materialization_allowed"] is True


def test_cli_prints_one_compact_json_result(monkeypatch, capsys) -> None:
    import app.jobs.inflation_policy_refresh as module

    loaded: list[bool] = []
    monkeypatch.setattr(
        module,
        "load_project_local_env",
        lambda: loaded.append(True),
        raising=False,
    )
    monkeypatch.setattr(
        module,
        "run_inflation_policy_raw_refresh",
        lambda **_kwargs: {
            "status": "success",
            "rows_written": 10,
            "failed_sources": [],
            "limited_sources": [],
            "materialization_allowed": True,
            "sources": {},
        },
    )

    assert module.main(["--as-of-at", "2026-08-02T03:15:00+00:00"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "success"
    assert loaded == [True]
