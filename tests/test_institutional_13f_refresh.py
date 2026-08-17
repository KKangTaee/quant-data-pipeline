from __future__ import annotations

from datetime import date
import importlib
import io
import urllib.error


PRIMARY_13F_XML = """<?xml version="1.0" encoding="UTF-8"?>
<edgarSubmission xmlns="http://www.sec.gov/edgar/thirteenffiler">
  <headerData><submissionType>13F-HR</submissionType><filerInfo><filer><credentials>
    <cik>0001067983</cik>
  </credentials></filer></filerInfo></headerData>
  <formData>
    <coverPage>
      <reportCalendarOrQuarter>06-30-2026</reportCalendarOrQuarter>
      <isAmendment>false</isAmendment>
      <filingManager><name>BERKSHIRE HATHAWAY INC</name></filingManager>
      <reportType>13F HOLDINGS REPORT</reportType>
      <form13FFileNumber>028-04567</form13FFileNumber>
    </coverPage>
    <summaryPage><otherIncludedManagersCount>0</otherIncludedManagersCount>
      <tableEntryTotal>1</tableEntryTotal><tableValueTotal>1000</tableValueTotal>
      <isConfidentialOmitted>false</isConfidentialOmitted>
    </summaryPage>
  </formData>
</edgarSubmission>
"""

INFORMATION_13F_XML = """<?xml version="1.0" encoding="UTF-8"?>
<informationTable xmlns="http://www.sec.gov/edgar/document/thirteenf/informationtable">
  <infoTable>
    <nameOfIssuer>APPLE INC</nameOfIssuer><titleOfClass>COM</titleOfClass>
    <cusip>037833100</cusip><figi>BBG000B9XRY4</figi><value>1000</value>
    <shrsOrPrnAmt><sshPrnamt>10</sshPrnamt><sshPrnamtType>SH</sshPrnamtType></shrsOrPrnAmt>
    <investmentDiscretion>SOLE</investmentDiscretion>
    <votingAuthority><Sole>10</Sole><Shared>0</Shared><None>0</None></votingAuthority>
  </infoTable>
</informationTable>
"""


def test_2026_deadlines_roll_weekend_and_federal_holiday() -> None:
    from app.services.institutional_13f_refresh import form_13f_due_date

    assert form_13f_due_date("2026-03-31") == date(2026, 5, 15)
    assert form_13f_due_date("2026-06-30") == date(2026, 8, 14)
    assert form_13f_due_date("2026-09-30") == date(2026, 11, 16)
    assert form_13f_due_date("2026-12-31") == date(2027, 2, 16)


def test_refresh_action_targets_latest_due_quarter_from_local_manager_periods() -> None:
    from app.services.institutional_13f_refresh import build_institutional_refresh_action

    action = build_institutional_refresh_action(
        as_of_date="2026-08-17",
        manager_periods={"0001067983": "2026-03-31", "0001350694": "2026-06-30"},
        expected_ciks=["0001067983", "0001350694"],
    )

    assert action == {
        "action_id": "refresh_institutional_13f",
        "visible": True,
        "status": "partial",
        "target_report_period": "2026-06-30",
        "target_quarter_label": "2026년 2분기",
        "label": "2026년 2분기 업데이트 확인 및 갱신",
        "description": "버튼을 누르면 SEC 공개 자료를 확인한 뒤 가능한 기관을 갱신합니다.",
        "completed_managers": 1,
        "expected_managers": 2,
        "pending_ciks": ["0001067983"],
        "next_due_date": "2026-11-16",
    }


def test_refresh_action_hides_when_every_expected_manager_is_current() -> None:
    from app.services.institutional_13f_refresh import build_institutional_refresh_action

    action = build_institutional_refresh_action(
        as_of_date="2026-08-17",
        manager_periods={"0001067983": "2026-06-30", "0001350694": "2026-06-30"},
        expected_ciks=["0001067983", "0001350694"],
    )

    assert action["status"] == "current"
    assert action["visible"] is False
    assert action["pending_ciks"] == []
    assert action["next_due_date"] == "2026-11-16"


def test_workbench_payload_preserves_injected_local_refresh_action() -> None:
    from app.services.institutional_portfolios import build_institutional_workbench_payload

    refresh_action = {
        "action_id": "refresh_institutional_13f",
        "visible": True,
        "status": "due",
        "target_report_period": "2026-06-30",
    }

    payload = build_institutional_workbench_payload(
        model={"summary": {}, "holdings": [], "changes": [], "sector_exposure": []},
        managers=[],
        selected_cik=None,
        interest_model=None,
        refresh_action=refresh_action,
    )

    assert payload["refresh_action"] == refresh_action


def test_bulk_listing_selects_dataset_whose_window_contains_due_date() -> None:
    from finance.data.institutional_13f import (
        parse_sec_13f_dataset_candidates,
        select_sec_13f_dataset_candidate,
    )

    html = """
    <table>
      <tr><td><a href="/files/01mar2026-31may2026_form13f.zip">2026 March April May 13F</a></td></tr>
      <tr><td><a href="/files/01jun2026-31aug2026_form13f.zip">2026 June July August 13F</a></td></tr>
    </table>
    """

    candidates = parse_sec_13f_dataset_candidates(html, base_url="https://www.sec.gov/data")
    selected = select_sec_13f_dataset_candidate(candidates, report_period="2026-06-30")

    assert selected is not None
    assert selected["dataset_url"] == "https://www.sec.gov/files/01jun2026-31aug2026_form13f.zip"
    assert selected["window_start"] == "2026-06-01"
    assert selected["window_end"] == "2026-08-31"


def test_bulk_listing_rejects_non_dataset_anchors_and_out_of_window_dataset() -> None:
    from finance.data.institutional_13f import (
        parse_sec_13f_dataset_candidates,
        select_sec_13f_dataset_candidate,
    )

    html = """
    <a href="/files/not-a-range_form13f.zip">Malformed label</a>
    <a href="/files/01jun2026-31aug2026_form13f.csv">Wrong format</a>
    <a href="/files/01mar2026-31may2026_form13f.zip">Valid older window</a>
    """

    candidates = parse_sec_13f_dataset_candidates(html, base_url="https://www.sec.gov/data")

    assert len(candidates) == 1
    assert select_sec_13f_dataset_candidate(candidates, report_period="2026-06-30") is None


def test_bulk_discovery_fetches_official_listing_with_declared_user_agent(monkeypatch) -> None:
    collector = importlib.import_module("finance.data.institutional_13f")

    captured: dict[str, object] = {}

    class Response(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            self.close()

    def fake_urlopen(request, *, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return Response(b'<a href="/files/01jun2026-31aug2026_form13f.zip">Q2 window</a>')

    monkeypatch.setattr(collector.urllib.request, "urlopen", fake_urlopen)

    selected = collector.discover_sec_13f_dataset_candidate(
        "2026-06-30",
        user_agent="Institutional research contact@example.com",
        timeout=7.0,
    )

    assert selected is not None
    assert selected["window_end"] == "2026-08-31"
    assert captured["timeout"] == 7.0
    request = captured["request"]
    assert request.full_url == collector.SEC_13F_DATASETS_PAGE
    assert request.get_header("User-agent") == "Institutional research contact@example.com"


def test_bulk_discovery_preserves_sec_http_status_in_runtime_error(monkeypatch) -> None:
    collector = importlib.import_module("finance.data.institutional_13f")

    def reject(_request, *, timeout):
        raise urllib.error.HTTPError(
            collector.SEC_13F_DATASETS_PAGE,
            429,
            "Too Many Requests",
            hdrs=None,
            fp=None,
        )

    monkeypatch.setattr(collector.urllib.request, "urlopen", reject)

    try:
        collector.discover_sec_13f_dataset_candidate("2026-06-30")
    except RuntimeError as exc:
        message = str(exc)
    else:
        raise AssertionError("SEC HTTP failure must not be swallowed")

    assert collector.SEC_13F_DATASETS_PAGE in message
    assert "429" in message


def test_find_sec_13f_submission_filters_exact_period_and_supported_forms() -> None:
    from finance.data.institutional_13f_edgar import find_sec_13f_submission

    payload = {
        "filings": {
            "recent": {
                "accessionNumber": [
                    "0001193125-26-352200",
                    "0001193125-26-352201",
                    "0001193125-26-100000",
                    "0001193125-26-352299",
                ],
                "filingDate": ["2026-08-14", "2026-08-15", "2026-05-15", "2026-08-16"],
                "reportDate": ["2026-06-30", "2026-06-30", "2026-03-31", "2026-06-30"],
                "form": ["13F-HR", "13F-HR/A", "13F-HR", "8-K"],
                "primaryDocument": ["primary.xml", "amendment.xml", "old.xml", "current.htm"],
            }
        }
    }

    filings = find_sec_13f_submission(payload, cik="0001067983", report_period="2026-06-30")

    assert [row["accession_number"] for row in filings] == [
        "0001193125-26-352200",
        "0001193125-26-352201",
    ]
    assert filings[0]["submission_type"] == "13F-HR"
    assert filings[0]["cik"] == "0001067983"


def test_normalize_sec_13f_xml_documents_preserves_namespace_fields_and_holdings() -> None:
    from finance.data.institutional_13f_edgar import normalize_sec_13f_xml_documents

    normalized = normalize_sec_13f_xml_documents(
        primary_xml=PRIMARY_13F_XML,
        information_xml=INFORMATION_13F_XML,
        accession_number="0001193125-26-352200",
        filing_date="2026-08-14",
        source_ref="https://www.sec.gov/Archives/edgar/data/1067983/000119312526352200/",
        collected_at="2026-08-17 00:00:00",
    )

    assert normalized["filings"][0]["period_of_report"] == "2026-06-30"
    assert normalized["filings"][0]["table_entry_total"] == 1
    assert normalized["holdings"][0]["cusip"] == "037833100"
    assert normalized["holdings"][0]["infotable_sk"] == 1
    assert normalized["holdings"][0]["voting_auth_sole"] == 10.0


def test_normalize_sec_13f_notice_does_not_fabricate_holdings() -> None:
    from finance.data.institutional_13f_edgar import normalize_sec_13f_xml_documents

    notice_xml = PRIMARY_13F_XML.replace("13F-HR", "13F-NT")
    normalized = normalize_sec_13f_xml_documents(
        primary_xml=notice_xml,
        information_xml=None,
        accession_number="0001193125-26-352250",
        filing_date="2026-08-14",
        source_ref="https://www.sec.gov/Archives/edgar/data/1067983/000119312526352250/",
        collected_at="2026-08-17 00:00:00",
    )

    assert normalized["filings"][0]["submission_type"] == "13F-NT"
    assert normalized["holdings"] == []
    assert normalized["managers"] == []


def test_store_normalized_sec_13f_rows_returns_stable_upsert_counts() -> None:
    from finance.data.institutional_13f import store_normalized_sec_13f_rows

    class FakeDB:
        def __init__(self) -> None:
            self.batches: list[tuple[str, list[dict]]] = []

        def executemany(self, sql: str, rows: list[dict]) -> None:
            self.batches.append((sql, rows))

        def query(self, _sql: str, _params=None) -> list[dict]:
            return []

    db = FakeDB()
    normalized = {
        "managers": [{"cik": "0001067983"}],
        "filings": [{"accession_number": "0001193125-26-352200"}],
        "holdings": [{"cusip": "037833100", "issuer_name": "APPLE INC"}],
    }

    result = store_normalized_sec_13f_rows(db, normalized, source_ref="unit-test")

    assert result == {
        "managers_written": 1,
        "filings_written": 1,
        "holdings_written": 1,
        "cusip_symbol_maps_written": 0,
        "rows_written": 3,
    }
    assert len(db.batches) == 3
    assert all("ON DUPLICATE KEY UPDATE" in sql for sql, _rows in db.batches)


def test_watchlist_collection_commits_each_manager_and_replay_is_idempotent() -> None:
    from finance.data.institutional_13f_edgar import collect_and_store_sec_13f_watchlist

    class FakeDB:
        def __init__(self) -> None:
            self.existing_accessions: set[str] = set()
            self.begin_count = 0
            self.commit_count = 0
            self.rollback_count = 0

        def use_db(self, _name: str) -> None:
            return None

        def begin(self) -> None:
            self.begin_count += 1

        def commit(self) -> None:
            self.commit_count += 1

        def rollback(self) -> None:
            self.rollback_count += 1

        def close(self) -> None:
            return None

        def execute(self, _sql: str, _params=None) -> None:
            return None

        def executemany(self, sql: str, rows: list[dict]) -> None:
            if "INSERT INTO institutional_13f_filing" in sql:
                self.existing_accessions.update(row["accession_number"] for row in rows)

        def query(self, sql: str, params=None) -> list[dict]:
            if "FROM institutional_13f_filing" in sql:
                requested = set(params or ())
                return [
                    {"accession_number": accession}
                    for accession in sorted(self.existing_accessions & requested)
                ]
            return []

    db = FakeDB()
    submissions = {
        cik: {
            "filings": {
                "recent": {
                    "accessionNumber": [accession],
                    "filingDate": ["2026-08-14"],
                    "reportDate": ["2026-06-30"],
                    "form": ["13F-HR"],
                    "primaryDocument": ["primary.xml"],
                }
            }
        }
        for cik, accession in {
            "0001067983": "0001193125-26-352200",
            "0001350694": "0001193125-26-352201",
        }.items()
    }

    def submissions_fetcher(cik: str, **_kwargs):
        return submissions[cik]

    def documents_fetcher(filing: dict, **_kwargs):
        return {
            "primary_xml": PRIMARY_13F_XML,
            "information_xml": INFORMATION_13F_XML,
            "source_ref": "https://www.sec.gov/Archives/edgar/data/1067983/000119312526352200/",
        }

    first = collect_and_store_sec_13f_watchlist(
        ciks=["0001067983", "0001350694"],
        report_period="2026-06-30",
        db_factory=lambda *_args, **_kwargs: db,
        sync_schema=False,
        submissions_fetcher=submissions_fetcher,
        filing_documents_fetcher=documents_fetcher,
        request_sleep=0,
    )
    second = collect_and_store_sec_13f_watchlist(
        ciks=["0001067983"],
        report_period="2026-06-30",
        db_factory=lambda *_args, **_kwargs: db,
        sync_schema=False,
        submissions_fetcher=submissions_fetcher,
        filing_documents_fetcher=documents_fetcher,
        request_sleep=0,
    )

    assert first["updated_managers"] == 1
    assert first["failed_managers"] == 1
    assert [row["status"] for row in first["manager_results"]] == ["updated", "failed"]
    assert db.commit_count == 1
    assert db.rollback_count == 1
    assert second["already_current_managers"] == 1
    assert second["rows_written"] == 0
