from __future__ import annotations


def test_rtdsm_ingestion_job_reports_success() -> None:
    from app.jobs.ingestion_jobs import (
        run_collect_economic_cycle_rtdsm_history,
    )

    result = run_collect_economic_cycle_rtdsm_history(
        collector=lambda: {
            "requested": 4,
            "stored": 123,
            "missing": [],
            "failed": [],
            "coverage": {"actual": 123},
            "series_rows": {"IPT": 30, "H": 30, "EMPLOY": 33, "RUC": 30},
            "source": "philadelphia_fed_rtdsm",
            "source_mode": "rtdsm_full_history",
        }
    )

    assert result["job_name"] == "collect_economic_cycle_rtdsm_history"
    assert result["status"] == "success"
    assert result["rows_written"] == 123
    assert result["symbols_requested"] == 4
    assert result["symbols_processed"] == 4
    assert result["failed_symbols"] == []
    assert result["details"]["source"] == "philadelphia_fed_rtdsm"
    assert (
        result["details"]["target_table"]
        == "finance_meta.macro_series_vintage_observation"
    )


def test_rtdsm_ingestion_job_reports_partial_source_failure() -> None:
    from app.jobs.ingestion_jobs import (
        run_collect_economic_cycle_rtdsm_history,
    )

    result = run_collect_economic_cycle_rtdsm_history(
        collector=lambda: {
            "requested": 4,
            "stored": 90,
            "missing": ["RUC"],
            "failed": [{"series_id": "RUC", "reason": "unavailable"}],
            "coverage": {"actual": 90},
            "series_rows": {"IPT": 30, "H": 30, "EMPLOY": 30},
            "source": "philadelphia_fed_rtdsm",
            "source_mode": "rtdsm_full_history",
        }
    )

    assert result["status"] == "partial_success"
    assert result["symbols_processed"] == 3
    assert result["failed_symbols"] == ["RUC"]
    assert result["details"]["missing"] == ["RUC"]


def test_rtdsm_ingestion_job_fails_closed_on_exception() -> None:
    from app.jobs.ingestion_jobs import (
        run_collect_economic_cycle_rtdsm_history,
    )

    def collector():
        raise RuntimeError("source contract changed")

    result = run_collect_economic_cycle_rtdsm_history(collector=collector)

    assert result["status"] == "failed"
    assert result["rows_written"] == 0
    assert result["details"]["source"] == "philadelphia_fed_rtdsm"
    assert "source contract changed" in result["message"]
