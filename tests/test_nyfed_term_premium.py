from __future__ import annotations

import importlib
from pathlib import Path

import pandas as pd


FIXTURE = Path(__file__).parent / "fixtures" / "acm_term_premium_excerpt.csv"
PAGE_URL = "https://www.newyorkfed.org/research/data_indicators/term-premia-tabs"
DOWNLOAD_URL = (
    "https://www.newyorkfed.org/medialibrary/media/research/"
    "data_indicators/ACMTermPremium.xls"
)


def test_discovery_normalizes_relative_and_absolute_official_links() -> None:
    from finance.data.nyfed_term_premium import discover_acm_download_url

    relative = (
        '<a href="/medialibrary/media/research/data_indicators/'
        'ACMTermPremium.xls">Download</a>'
    )
    absolute = f'<a href="{DOWNLOAD_URL}">Download</a>'

    assert discover_acm_download_url(relative) == DOWNLOAD_URL
    assert discover_acm_download_url(absolute) == DOWNLOAD_URL


def test_normalization_stores_collection_vintage_and_never_forward_fills() -> None:
    from finance.data.nyfed_term_premium import normalize_acm_term_premium

    rows = normalize_acm_term_premium(
        pd.read_csv(FIXTURE),
        collected_at="2026-08-02T03:15:00+00:00",
        source_ref=DOWNLOAD_URL,
    )

    assert [row["observation_date"] for row in rows] == [
        "2026-07-28",
        "2026-07-30",
    ]
    assert [row["value"] for row in rows] == [0.4123, 0.4388]
    assert {row["realtime_start"] for row in rows} == {"2026-08-02"}
    assert {row["released_at"] for row in rows} == {
        "2026-08-02T03:15:00+00:00"
    }
    assert {row["series_id"] for row in rows} == {"ACMTP10"}
    assert {row["source_mode"] for row in rows} == {
        "current_workbook_collection_vintage"
    }


def test_collector_persists_acm_rows_but_reports_limited_replay(monkeypatch) -> None:
    module = importlib.import_module("finance.data.nyfed_term_premium")
    page = (
        '<a href="/medialibrary/media/research/data_indicators/'
        'ACMTermPremium.xls">Download</a>'
    )
    frame = pd.read_csv(FIXTURE)
    synced: list[tuple[str, str]] = []

    monkeypatch.setattr(
        module,
        "sync_table_schema",
        lambda _db, table, _schema, database: synced.append((table, database)),
        raising=False,
    )

    class DB:
        def __init__(self) -> None:
            self.rows: list[dict[str, object]] = []

        def use_db(self, _database: str) -> None:
            pass

        def execute(self, _sql: str) -> None:
            pass

        def executemany(self, _sql: str, values: list[dict[str, object]]) -> None:
            self.rows.extend(values)

    db = DB()
    result = module.collect_and_store_acm_term_premium(
        page_url=PAGE_URL,
        connection=db,
        fetch_html=lambda _url: page,
        read_workbook=lambda url: frame if url == DOWNLOAD_URL else None,
        collected_at="2026-08-02T03:15:00+00:00",
    )

    assert result == {
        "stored": 2,
        "coverage_status": "LIMITED",
        "source_ref": DOWNLOAD_URL,
    }
    assert len(db.rows) == 2
    assert synced == [("macro_series_vintage_observation", "finance_meta")]
