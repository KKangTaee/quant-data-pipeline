from __future__ import annotations

from datetime import date
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

import pytest
from openpyxl import Workbook


def _module():
    from finance.data import philadelphia_rtdsm

    return philadelphia_rtdsm


def _workbook_bytes(
    *,
    sheet_name: str = "employ",
    headers: tuple[str, ...] = ("EMPLOY20M1", "EMPLOY20M2"),
    rows: tuple[tuple[object, ...], ...] = (
        ("2019:10", 100.0, 101.0),
        ("2020:01", 110.0, 111.0),
        ("2020:02", "#N/A", 112.0),
    ),
    malformed_core_time: bool = True,
) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = sheet_name
    sheet.append(("DATE", *headers))
    for row in rows:
        sheet.append(row)
    raw = BytesIO()
    workbook.save(raw)
    if not malformed_core_time:
        return raw.getvalue()

    output = BytesIO()
    with ZipFile(BytesIO(raw.getvalue())) as source, ZipFile(
        output, "w", ZIP_DEFLATED
    ) as target:
        for member in source.infolist():
            payload = source.read(member.filename)
            if member.filename == "docProps/core.xml":
                payload = payload.replace(b"T08:", b"T 8:")
            target.writestr(member, payload)
    return output.getvalue()


def test_rtdsm_catalog_locks_four_provider_native_series() -> None:
    module = _module()

    catalog = {item.series_id: item for item in module.get_rtdsm_catalog()}

    assert set(catalog) == {"IPT", "H", "EMPLOY", "RUC"}
    assert catalog["RUC"].vintage_frequency == "quarterly"
    assert catalog["IPT"].factor_group == "activity"
    assert catalog["EMPLOY"].factor_group == "labor_income"


def test_rtdsm_headers_use_conservative_known_at_month_end() -> None:
    module = _module()

    assert module.parse_rtdsm_vintage_header(
        "EMPLOY64M12", series_id="EMPLOY", vintage_frequency="monthly"
    ) == date(1964, 12, 31)
    assert module.parse_rtdsm_vintage_header(
        "RUC26Q2", series_id="RUC", vintage_frequency="quarterly"
    ) == date(2026, 5, 31)


def test_rtdsm_header_rejects_prefix_and_frequency_mismatch() -> None:
    module = _module()

    with pytest.raises(module.RtdsmSourceError, match="header"):
        module.parse_rtdsm_vintage_header(
            "IPT64M12", series_id="EMPLOY", vintage_frequency="monthly"
        )
    with pytest.raises(module.RtdsmSourceError, match="header"):
        module.parse_rtdsm_vintage_header(
            "RUC26M2", series_id="RUC", vintage_frequency="quarterly"
        )


def test_normalize_repairs_only_core_metadata_and_emits_numeric_cells() -> None:
    module = _module()
    spec = next(
        item for item in module.get_rtdsm_catalog() if item.series_id == "EMPLOY"
    )

    rows = [
        row
        for batch in module.iter_rtdsm_normalized_batches(
            spec,
            _workbook_bytes(),
            collected_at="2026-08-12 00:00:00",
            batch_size=2,
        )
        for row in batch
    ]

    assert len(rows) == 5
    assert rows[0] == {
        "series_id": "EMPLOY",
        "observation_date": "2019-10-01",
        "realtime_start": "2020-01-31",
        "realtime_end": "2020-02-28",
        "released_at": "2020-02-01T04:59:59.999999+00:00",
        "source": "philadelphia_fed_rtdsm",
        "source_type": "official",
        "source_mode": "rtdsm_full_history_monthly",
        "source_ref": spec.workbook_url,
        "series_name": "Nonfarm payroll employment",
        "factor_group": "labor_income",
        "frequency": "monthly",
        "units": "thousands_sa",
        "value": 100.0,
        "release_lag_days": 122,
        "coverage_status": "actual",
        "missing_fields_json": "[]",
        "collected_at": "2026-08-12 00:00:00",
        "error_msg": None,
    }
    assert rows[-1]["observation_date"] == "2020-02-01"
    assert rows[-1]["realtime_start"] == "2020-02-29"
    assert rows[-1]["realtime_end"] == "9999-12-31"
    assert rows[-1]["value"] == 112.0
    assert all(row["value"] is not None for row in rows)


def test_normalize_incremental_overlap_includes_latest_stored_vintage() -> None:
    module = _module()
    spec = next(
        item for item in module.get_rtdsm_catalog() if item.series_id == "EMPLOY"
    )

    rows = [
        row
        for batch in module.iter_rtdsm_normalized_batches(
            spec,
            _workbook_bytes(),
            collected_at="2026-08-12 00:00:00",
            minimum_vintage_date="2020-02-29",
            batch_size=10,
        )
        for row in batch
    ]

    assert rows
    assert {row["realtime_start"] for row in rows} == {"2020-02-29"}


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        (_workbook_bytes(sheet_name="wrong"), "sheet"),
        (
            _workbook_bytes(headers=("EMPLOY20M2", "EMPLOY20M1")),
            "strictly increasing",
        ),
        (
            _workbook_bytes(rows=(("not-a-month", 1.0, 2.0),)),
            "observation",
        ),
        (
            _workbook_bytes(rows=(("2020:01", "#N/A", None),)),
            "numeric",
        ),
    ],
)
def test_normalize_rejects_malformed_workbook_contract(
    payload: bytes,
    message: str,
) -> None:
    module = _module()
    spec = next(
        item for item in module.get_rtdsm_catalog() if item.series_id == "EMPLOY"
    )

    with pytest.raises(module.RtdsmSourceError, match=message):
        list(
            module.iter_rtdsm_normalized_batches(
                spec,
                payload,
                collected_at="2026-08-12 00:00:00",
                batch_size=10,
            )
        )


def test_download_retries_bounded_failures() -> None:
    module = _module()
    spec = next(
        item for item in module.get_rtdsm_catalog() if item.series_id == "EMPLOY"
    )
    attempts: list[tuple[str, int]] = []

    def request_fn(url: str, timeout: int) -> bytes:
        attempts.append((url, timeout))
        if len(attempts) < 3:
            raise TimeoutError("temporary")
        return b"xlsx"

    result = module.download_rtdsm_workbook(
        spec,
        timeout=7,
        retries=3,
        request_fn=request_fn,
        sleep_fn=lambda _seconds: None,
    )

    assert result == b"xlsx"
    assert attempts == [(spec.workbook_url, 7)] * 3


def test_collect_uses_source_specific_incremental_overlap_and_batch_writer() -> None:
    module = _module()
    payload = _workbook_bytes()
    calls: list[tuple[str, object]] = []

    class DB:
        def query(self, sql: str, params: tuple[object, ...]):
            calls.append(("query", (sql, params)))
            return [
                {
                    "series_id": "EMPLOY",
                    "latest_realtime_start": "2020-02-29",
                }
            ]

    def fetcher(spec, **_kwargs):
        calls.append(("fetch", spec.series_id))
        return payload

    written: list[list[dict[str, object]]] = []

    def writer(rows, *, db):
        assert isinstance(db, DB)
        written.append([dict(row) for row in rows])
        return len(rows)

    summary = module.collect_rtdsm_history(
        series_ids=["EMPLOY"],
        connection=DB(),
        workbook_fetcher=fetcher,
        writer=writer,
        batch_size=2,
    )

    assert summary["requested"] == 1
    assert summary["stored"] == 3
    assert summary["missing"] == []
    assert summary["failed"] == []
    assert summary["source"] == "philadelphia_fed_rtdsm"
    assert summary["series_rows"] == {"EMPLOY": 3}
    assert len(written) == 2
    assert {
        row["realtime_start"] for batch in written for row in batch
    } == {"2020-02-29"}


def test_collect_records_series_failure_without_revised_data_fallback() -> None:
    module = _module()

    class DB:
        def query(self, _sql: str, _params: tuple[object, ...]):
            return []

    def fetcher(spec, **_kwargs):
        raise module.RtdsmSourceError(f"{spec.series_id} unavailable")

    summary = module.collect_rtdsm_history(
        series_ids=["IPT"],
        connection=DB(),
        workbook_fetcher=fetcher,
    )

    assert summary["stored"] == 0
    assert summary["missing"] == ["IPT"]
    assert summary["failed"] == [
        {"series_id": "IPT", "reason": "IPT unavailable"}
    ]
