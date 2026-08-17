from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any, Callable, Mapping, Sequence
from xml.etree import ElementTree

from .institutional_13f import (
    DB_META,
    _resolve_user_agent,
    _sync_schema,
    _build_manager_rows,
    _clean_text,
    _date_text,
    _float_value,
    _int_value,
    _normalize_cik,
    _now_utc_text,
    store_normalized_sec_13f_rows,
)
from .db.mysql import MySQLClient


SUPPORTED_13F_FORMS = {"13F-HR", "13F-HR/A", "13F-NT"}
EDGAR_WATCHLIST_SOURCE = "sec_edgar_watchlist_13f"


def _parallel_recent_rows(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    recent = payload.get("filings", {}).get("recent", {})
    if not isinstance(recent, Mapping):
        return []
    columns = {str(key): list(value) for key, value in recent.items() if isinstance(value, list)}
    row_count = max((len(values) for values in columns.values()), default=0)
    return [
        {key: values[index] if index < len(values) else None for key, values in columns.items()}
        for index in range(row_count)
    ]


def find_sec_13f_submission(
    payload: Mapping[str, Any],
    *,
    cik: str,
    report_period: str,
) -> list[dict[str, Any]]:
    """Return supported recent 13F filings for one exact report period."""

    normalized_cik = _normalize_cik(cik)
    normalized_period = _date_text(report_period)
    if not normalized_cik or not normalized_period:
        return []
    filings: list[dict[str, Any]] = []
    for row in _parallel_recent_rows(payload):
        submission_type = str(row.get("form") or "").strip().upper()
        if submission_type not in SUPPORTED_13F_FORMS:
            continue
        if _date_text(row.get("reportDate")) != normalized_period:
            continue
        accession = _clean_text(row.get("accessionNumber"))
        filing_date = _date_text(row.get("filingDate"))
        if not accession or not filing_date:
            continue
        filings.append(
            {
                "accession_number": accession,
                "cik": normalized_cik,
                "submission_type": submission_type,
                "filing_date": filing_date,
                "report_period": normalized_period,
                "primary_document": _clean_text(row.get("primaryDocument")),
            }
        )
    return sorted(filings, key=lambda row: (row["filing_date"], row["accession_number"]))


def _local_name(element: ElementTree.Element) -> str:
    return element.tag.rsplit("}", 1)[-1].lower()


def _find_element(root: ElementTree.Element, name: str) -> ElementTree.Element | None:
    wanted = name.lower()
    return next((element for element in root.iter() if _local_name(element) == wanted), None)


def _find_text(root: ElementTree.Element, name: str) -> str | None:
    element = _find_element(root, name)
    return _clean_text(element.text if element is not None else None)


def _bool_text(value: str | None) -> int:
    return 1 if str(value or "").strip().lower() in {"true", "1", "yes", "y"} else 0


def normalize_sec_13f_xml_documents(
    *,
    primary_xml: str | bytes,
    information_xml: str | bytes | None,
    accession_number: str,
    filing_date: str,
    source_ref: str,
    collected_at: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Normalize one EDGAR filing cover/summary XML and optional information table."""

    primary_root = ElementTree.fromstring(primary_xml)
    collected = collected_at or _now_utc_text()
    cik = _normalize_cik(_find_text(primary_root, "cik"))
    manager_name = _find_text(primary_root, "name") or "Unknown manager"
    submission_type = (_find_text(primary_root, "submissionType") or "13F-HR").upper()
    period_of_report = _date_text(_find_text(primary_root, "reportCalendarOrQuarter"))
    normalized_filing_date = _date_text(filing_date)
    if not cik or not period_of_report or not normalized_filing_date:
        raise ValueError("13F primary XML is missing CIK, report period, or filing date")

    filing = {
        "accession_number": str(accession_number).strip(),
        "cik": cik,
        "manager_name": manager_name,
        "submission_type": submission_type,
        "filing_date": normalized_filing_date,
        "period_of_report": period_of_report,
        "report_calendar_or_quarter": period_of_report,
        "is_amendment": _bool_text(_find_text(primary_root, "isAmendment")),
        "amendment_no": _int_value(_find_text(primary_root, "amendmentNo")),
        "amendment_type": _find_text(primary_root, "amendmentType"),
        "report_type": _find_text(primary_root, "reportType"),
        "form13f_file_number": _find_text(primary_root, "form13FFileNumber"),
        "table_entry_total": _int_value(_find_text(primary_root, "tableEntryTotal")),
        "table_value_total": _float_value(_find_text(primary_root, "tableValueTotal")),
        "is_confidential_omitted": (
            _bool_text(_find_text(primary_root, "isConfidentialOmitted"))
            if _find_text(primary_root, "isConfidentialOmitted") is not None
            else None
        ),
        "source_dataset": EDGAR_WATCHLIST_SOURCE,
        "source_ref": source_ref,
        "collected_at": collected,
    }

    holdings: list[dict[str, Any]] = []
    if information_xml:
        information_root = ElementTree.fromstring(information_xml)
        info_rows = [element for element in information_root.iter() if _local_name(element) == "infotable"]
        for index, row in enumerate(info_rows, start=1):
            cusip = _find_text(row, "cusip")
            issuer_name = _find_text(row, "nameOfIssuer")
            if not cusip or not issuer_name:
                continue
            holdings.append(
                {
                    "accession_number": filing["accession_number"],
                    "infotable_sk": index,
                    "cik": cik,
                    "manager_name": manager_name,
                    "report_period": period_of_report,
                    "filing_date": normalized_filing_date,
                    "issuer_name": issuer_name,
                    "title_of_class": _find_text(row, "titleOfClass"),
                    "cusip": cusip.upper(),
                    "figi": _find_text(row, "figi"),
                    "reported_value": _float_value(_find_text(row, "value")),
                    "shares_or_principal_amount": _float_value(_find_text(row, "sshPrnamt")),
                    "amount_type": _find_text(row, "sshPrnamtType"),
                    "put_call": _find_text(row, "putCall"),
                    "investment_discretion": _find_text(row, "investmentDiscretion"),
                    "other_manager": _find_text(row, "otherManager"),
                    "voting_auth_sole": _float_value(_find_text(row, "Sole")),
                    "voting_auth_shared": _float_value(_find_text(row, "Shared")),
                    "voting_auth_none": _float_value(_find_text(row, "None")),
                    "holding_symbol": None,
                    "symbol_source": None,
                    "sector": None,
                    "industry": None,
                    "source_dataset": EDGAR_WATCHLIST_SOURCE,
                    "source_ref": source_ref,
                    "collected_at": collected,
                }
            )

    managers = _build_manager_rows([filing]) if holdings and submission_type != "13F-NT" else []
    for manager in managers:
        manager["source"] = EDGAR_WATCHLIST_SOURCE
    return {"managers": managers, "filings": [filing], "holdings": holdings}


def _fetch_sec_bytes(url: str, *, user_agent: str | None, timeout: float) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": _resolve_user_agent(user_agent),
            "Accept-Encoding": "identity",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=float(timeout)) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"SEC EDGAR request failed: {url} HTTP {exc.code} {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"SEC EDGAR request failed: {url} {exc.reason}") from exc


def fetch_sec_13f_submissions(
    cik: str,
    *,
    user_agent: str | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    normalized_cik = _normalize_cik(cik)
    if not normalized_cik:
        raise ValueError(f"invalid CIK: {cik}")
    url = f"https://data.sec.gov/submissions/CIK{normalized_cik}.json"
    return json.loads(_fetch_sec_bytes(url, user_agent=user_agent, timeout=timeout).decode("utf-8"))


def _archive_base(cik: str, accession_number: str) -> str:
    return (
        f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
        f"{accession_number.replace('-', '')}/"
    )


def _select_xml_documents(filing: Mapping[str, Any], index_payload: Mapping[str, Any]) -> tuple[str, str | None]:
    items = index_payload.get("directory", {}).get("item", [])
    documents = [dict(item) for item in items if isinstance(item, Mapping)]
    primary_name = str(filing.get("primary_document") or "").strip()
    primary_basename = primary_name.rsplit("/", 1)[-1].lower()
    xml_documents = [row for row in documents if str(row.get("name") or "").lower().endswith(".xml")]
    primary = next(
        (
            row
            for row in xml_documents
            if str(row.get("name") or "").lower() in {primary_name.lower(), primary_basename}
        ),
        None,
    )
    if primary is None:
        primary = next(
            (
                row
                for row in xml_documents
                if str(row.get("type") or "").strip().upper() in SUPPORTED_13F_FORMS
            ),
            None,
        )
    if primary is None:
        raise ValueError("EDGAR filing directory has no raw primary 13F XML document")

    information = next(
        (
            row
            for row in xml_documents
            if row is not primary and "INFORMATION TABLE" in str(row.get("type") or "").upper()
        ),
        None,
    )
    if information is None:
        information = next(
            (
                row
                for row in xml_documents
                if row is not primary
                and any(token in str(row.get("name") or "").lower() for token in ("infotable", "information"))
            ),
            None,
        )
    if information is None:
        remaining_xml = [row for row in xml_documents if row is not primary]
        if len(remaining_xml) == 1:
            information = remaining_xml[0]
    return str(primary["name"]), str(information["name"]) if information else None


def fetch_sec_13f_filing_documents(
    filing: Mapping[str, Any],
    *,
    user_agent: str | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    base_url = _archive_base(str(filing["cik"]), str(filing["accession_number"]))
    index_payload = json.loads(
        _fetch_sec_bytes(f"{base_url}index.json", user_agent=user_agent, timeout=timeout).decode("utf-8")
    )
    primary_name, information_name = _select_xml_documents(filing, index_payload)
    primary_xml = _fetch_sec_bytes(
        f"{base_url}{primary_name}", user_agent=user_agent, timeout=timeout
    ).decode("utf-8", errors="replace")
    information_xml = None
    if information_name:
        information_xml = _fetch_sec_bytes(
            f"{base_url}{information_name}", user_agent=user_agent, timeout=timeout
        ).decode("utf-8", errors="replace")
    if str(filing.get("submission_type") or "").upper() != "13F-NT" and not information_xml:
        raise ValueError("EDGAR 13F-HR filing has no raw information-table XML document")
    return {
        "primary_xml": primary_xml,
        "information_xml": information_xml,
        "source_ref": base_url,
    }


def _existing_accessions(db: MySQLClient, accessions: Sequence[str]) -> set[str]:
    if not accessions:
        return set()
    placeholders = ", ".join(["%s"] * len(accessions))
    rows = db.query(
        f"SELECT accession_number FROM institutional_13f_filing WHERE accession_number IN ({placeholders})",
        tuple(accessions),
    )
    return {str(row.get("accession_number") or "") for row in rows}


def collect_and_store_sec_13f_watchlist(
    *,
    ciks: Sequence[str],
    report_period: str,
    user_agent: str | None = None,
    request_timeout: float = 30.0,
    request_sleep: float = 0.11,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
    db_factory: Callable[..., MySQLClient] = MySQLClient,
    sync_schema: bool = True,
    submissions_fetcher: Callable[..., Mapping[str, Any]] = fetch_sec_13f_submissions,
    filing_documents_fetcher: Callable[..., Mapping[str, Any]] = fetch_sec_13f_filing_documents,
) -> dict[str, Any]:
    """Collect public target-period filings with per-manager write isolation."""

    normalized_period = _date_text(report_period)
    if not normalized_period:
        raise ValueError(f"invalid report period: {report_period}")
    expected_ciks = [cik for cik in (_normalize_cik(value) for value in ciks) if cik]
    manager_results: list[dict[str, Any]] = []
    totals = {
        "updated_managers": 0,
        "already_current_managers": 0,
        "notice_only_managers": 0,
        "not_filed_managers": 0,
        "failed_managers": 0,
        "rows_written": 0,
    }

    db = db_factory(host, user, password, port)
    try:
        db.use_db(DB_META)
        if sync_schema:
            _sync_schema(db)
        for index, cik in enumerate(expected_ciks):
            if request_sleep > 0 and index:
                time.sleep(float(request_sleep))
            accessions: list[str] = []
            try:
                payload = submissions_fetcher(
                    cik,
                    user_agent=user_agent,
                    timeout=float(request_timeout),
                )
                filings = find_sec_13f_submission(payload, cik=cik, report_period=normalized_period)
                accessions = [str(row["accession_number"]) for row in filings]
                if not filings:
                    totals["not_filed_managers"] += 1
                    manager_results.append({"cik": cik, "status": "not_filed", "accessions": []})
                    continue

                existing = _existing_accessions(db, accessions)
                pending_filings = [row for row in filings if row["accession_number"] not in existing]
                if not pending_filings:
                    totals["already_current_managers"] += 1
                    manager_results.append({"cik": cik, "status": "already_current", "accessions": accessions})
                    continue

                combined: dict[str, list[dict[str, Any]]] = {
                    "managers": [],
                    "filings": [],
                    "holdings": [],
                }
                for filing in pending_filings:
                    documents = filing_documents_fetcher(
                        filing,
                        user_agent=user_agent,
                        timeout=float(request_timeout),
                    )
                    normalized = normalize_sec_13f_xml_documents(
                        primary_xml=documents["primary_xml"],
                        information_xml=documents.get("information_xml"),
                        accession_number=str(filing["accession_number"]),
                        filing_date=str(filing["filing_date"]),
                        source_ref=str(documents["source_ref"]),
                    )
                    normalized_filing = normalized["filings"][0]
                    if normalized_filing["cik"] != cik or normalized_filing["period_of_report"] != normalized_period:
                        raise ValueError(
                            "EDGAR filing identity does not match the requested CIK and report period"
                        )
                    for key in combined:
                        combined[key].extend(normalized[key])

                has_holdings_filing = bool(combined["managers"] and combined["holdings"])
                notice_only = all(
                    str(filing.get("submission_type") or "").upper() == "13F-NT"
                    for filing in pending_filings
                )
                if not has_holdings_filing and not notice_only:
                    raise ValueError("published 13F filing has no complete owned information table")

                db.begin()
                counts = store_normalized_sec_13f_rows(
                    db,
                    combined,
                    source_ref=combined["filings"][-1].get("source_ref") if combined["filings"] else None,
                )
                db.commit()
                totals["rows_written"] += counts["rows_written"]
                status = "notice_only" if notice_only else "updated"
                totals[f"{status}_managers"] += 1
                manager_results.append(
                    {
                        "cik": cik,
                        "status": status,
                        "accessions": accessions,
                        **counts,
                    }
                )
            except Exception as exc:
                db.rollback()
                totals["failed_managers"] += 1
                manager_results.append(
                    {
                        "cik": cik,
                        "status": "failed",
                        "accessions": accessions,
                        "error": str(exc),
                    }
                )
    finally:
        db.close()

    return {
        "source": EDGAR_WATCHLIST_SOURCE,
        "report_period": normalized_period,
        "expected_managers": len(expected_ciks),
        **totals,
        "manager_results": manager_results,
    }
