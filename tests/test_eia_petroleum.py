from __future__ import annotations

import pandas as pd

from app.jobs import ingestion_jobs
from finance.data import eia_petroleum
from finance.data.eia_petroleum import (
    collect_and_store_eia_weekly_petroleum,
    fetch_eia_weekly_petroleum_rows,
    normalize_eia_weekly_frame,
)


def test_eia_xls_parser_normalizes_weekly_rows() -> None:
    frame = pd.DataFrame(
        {"Date": ["2026-06-26", "bad"], "value": [408359, "NA"]}
    )

    rows = normalize_eia_weekly_frame(
        "WCESTUS1",
        frame,
        collected_at="2026-07-17 00:00:00",
    )

    assert rows == [
        {
            "series_id": "WCESTUS1",
            "observation_date": "2026-06-26",
            "source": "eia",
            "source_type": "official",
            "source_mode": "weekly_xls",
            "source_ref": "https://www.eia.gov/dnav/pet/hist_xls/WCESTUS1w.xls",
            "series_name": (
                "Weekly U.S. Ending Stocks excluding SPR of Crude Oil"
            ),
            "category": "petroleum_inventory",
            "frequency": "weekly",
            "units": "thousand_barrels",
            "value": 408359.0,
            "release_lag_days": None,
            "coverage_status": "actual",
            "missing_fields_json": "[]",
            "collected_at": "2026-07-17 00:00:00",
            "error_msg": None,
        }
    ]


def test_eia_fetcher_keeps_missing_and_failed_series_separate() -> None:
    def fake_fetcher(url: str) -> pd.DataFrame:
        if "WCESTUS1" in url:
            return pd.DataFrame({"Date": ["2026-06-26"], "value": [408359]})
        if "WCRFPUS2" in url:
            return pd.DataFrame(columns=["Date", "value"])
        raise RuntimeError("source unavailable")

    rows, missing, failed = fetch_eia_weekly_petroleum_rows(
        ["WCESTUS1", "WCRFPUS2", "WRPUPUS2"],
        fetcher=fake_fetcher,
        collected_at="2026-07-17 00:00:00",
    )

    assert [row["series_id"] for row in rows] == ["WCESTUS1"]
    assert missing == ["WCRFPUS2"]
    assert failed == [
        {"series_id": "WRPUPUS2", "reason": "source unavailable"}
    ]


def test_eia_collector_stores_normalized_rows(monkeypatch) -> None:
    stored: list[dict[str, object]] = []

    monkeypatch.setattr(
        eia_petroleum,
        "fetch_eia_weekly_petroleum_rows",
        lambda *_args, **_kwargs: (
            [{"series_id": "WCESTUS1", "coverage_status": "actual"}],
            [],
            [],
        ),
    )
    monkeypatch.setattr(
        eia_petroleum,
        "store_macro_observation_rows",
        lambda rows, **_kwargs: stored.extend(rows) or len(rows),
    )

    summary = collect_and_store_eia_weekly_petroleum(["WCESTUS1"])

    assert summary["stored"] == 1
    assert summary["source"] == "eia"
    assert stored == [{"series_id": "WCESTUS1", "coverage_status": "actual"}]


def test_macro_market_job_routes_fred_and_eia_series_separately(monkeypatch) -> None:
    calls: dict[str, list[str]] = {}

    def fake_fred(series_ids, **_kwargs):
        calls["fred"] = list(series_ids)
        return {
            "stored": 2,
            "missing": [],
            "failed": [],
            "coverage": {"actual": 2},
            "source": "fred",
            "source_mode": "csv",
        }

    def fake_eia(series_ids, **_kwargs):
        calls["eia"] = list(series_ids)
        return {
            "stored": 3,
            "missing": [],
            "failed": [],
            "coverage": {"actual": 3},
            "source": "eia",
            "source_mode": "weekly_xls",
        }

    monkeypatch.setattr(ingestion_jobs, "collect_and_store_macro_series", fake_fred)
    monkeypatch.setattr(
        ingestion_jobs,
        "collect_and_store_eia_weekly_petroleum",
        fake_eia,
        raising=False,
    )

    result = ingestion_jobs.run_collect_macro_market_context(
        ["DGS2", "T10YIE", "WCESTUS1", "WCRFPUS2", "WRPUPUS2"]
    )

    assert calls == {
        "fred": ["DGS2", "T10YIE"],
        "eia": ["WCESTUS1", "WCRFPUS2", "WRPUPUS2"],
    }
    assert result["status"] == "success"
    assert result["rows_written"] == 5
