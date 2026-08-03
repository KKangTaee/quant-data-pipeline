from __future__ import annotations

from io import BytesIO
import importlib
from zipfile import ZIP_DEFLATED, ZipFile

import pandas as pd


MEAN_URL = (
    "https://www.philadelphiafed.org/-/media/FRBP/Assets/Surveys-And-Data/"
    "survey-of-professional-forecasters/data-files/files/Mean_PRCPCE_Level.xlsx"
)


def _workbook_bytes() -> bytes:
    columns = ["YEAR", "QUARTER", *(f"PRCPCE{i}" for i in range(1, 21))]
    frame = pd.DataFrame(
        [
            [2006, 4, *("#N/A" for _ in range(20))],
            [
                2026,
                2,
                3.0,
                23.0,
                31.0,
                27.0,
                11.0,
                4.0,
                1.0,
                0.0,
                0.0,
                0.0,
                2.0,
                9.0,
                13.0,
                29.0,
                32.0,
                12.0,
                2.0,
                1.0,
                0.0,
                0.0,
            ]
        ],
        columns=columns,
    )
    raw = BytesIO()
    with pd.ExcelWriter(raw, engine="openpyxl") as writer:
        frame.to_excel(writer, sheet_name="Mean_Level", index=False)
    malformed = BytesIO()
    with ZipFile(BytesIO(raw.getvalue())) as source, ZipFile(
        malformed, "w", ZIP_DEFLATED
    ) as target:
        for info in source.infolist():
            payload = source.read(info.filename)
            if info.filename == "docProps/core.xml":
                payload = payload.replace(b"T02:", b"T 2:")
            target.writestr(info, payload)
    return malformed.getvalue()


def test_release_date_parser_uses_official_news_release_date() -> None:
    from finance.data.spf_core_pce import parse_spf_release_dates

    text = """
    2025 Q4             11/11/25***         11/17/25***
    2026 Q1             3/2/26**            3/6/26**
         Q2             5/12/26             5/15/26
    """

    assert parse_spf_release_dates(text) == {
        (2025, 4): "2025-11-17",
        (2026, 1): "2026-03-06",
        (2026, 2): "2026-05-15",
    }


def test_workbook_parser_repairs_malformed_metadata_and_maps_both_horizons() -> None:
    from finance.data.spf_core_pce import parse_spf_core_pce_workbook

    rows = parse_spf_core_pce_workbook(
        _workbook_bytes(),
        release_dates={(2006, 4): "2006-11-13", (2026, 2): "2026-05-15"},
        collected_at="2026-08-03T03:00:00+00:00",
        source_ref=MEAN_URL,
    )

    assert len(rows) == 20
    current = [row for row in rows if row["target_year"] == 2026]
    following = [row for row in rows if row["target_year"] == 2027]
    assert sum(float(row["mean_probability_pct"]) for row in current) == 100.0
    assert sum(float(row["mean_probability_pct"]) for row in following) == 100.0
    assert current[0]["bin_label"] == ">=4.0"
    assert current[-1]["bin_label"] == "decline"
    assert {row["released_at"] for row in rows} == {
        "2026-05-16 03:59:59.999999"
    }
    assert {row["source_ref"] for row in rows} == {MEAN_URL}


def test_collector_persists_official_probability_rows_with_exact_key(monkeypatch) -> None:
    module = importlib.import_module("finance.data.spf_core_pce")
    synced: list[tuple[str, str]] = []

    monkeypatch.setattr(
        module,
        "sync_table_schema",
        lambda _db, table, _schema, database: synced.append((table, database)),
    )

    class DB:
        def __init__(self) -> None:
            self.rows: list[dict[str, object]] = []
            self.sql = ""

        def use_db(self, _database: str) -> None:
            pass

        def execute(self, _sql: str) -> None:
            pass

        def executemany(self, _sql: str, values: list[dict[str, object]]) -> None:
            self.sql = _sql
            self.rows.extend(values)

    db = DB()
    result = module.collect_and_store_spf_core_pce_probabilities(
        connection=db,
        fetch_text=lambda _url: "2026 Q2 5/12/26 5/15/26",
        fetch_bytes=lambda _url: _workbook_bytes(),
        collected_at="2026-08-03T03:00:00+00:00",
    )

    assert result["status"] == "success"
    assert result["stored"] == 20
    assert result["latest_survey"] == "2026Q2"
    assert len(db.rows) == 20
    assert "ON DUPLICATE KEY UPDATE" in db.sql
    assert synced == [("spf_core_pce_probability", "finance_meta")]
