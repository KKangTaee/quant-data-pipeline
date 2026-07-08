from __future__ import annotations

import io
import os
import time
import urllib.error
import urllib.request
import zipfile
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from .db.mysql import MySQLClient
from .db.schema import INSTITUTIONAL_13F_SCHEMAS, sync_table_schema
from .sec_delisting import DEFAULT_SEC_USER_AGENT


DB_META = "finance_meta"
SEC_13F_DATASETS_PAGE = "https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets"
SEC_13F_SOURCE_CAVEATS = [
    "SEC Form 13F is a delayed quarterly disclosure and can be filed up to 45 days after quarter end.",
    "13F holdings are not real-time buys or sells and are not a buy/sell signal.",
    "13F does not show short positions, cash, many derivatives, hedges, or full portfolio intent.",
    "Amendments, confidential treatment, and source extraction issues can change visible holdings.",
    "CUSIP-symbol mapping is partial unless a separate mapping source is verified.",
]
DATASET_FILE_KEYS = {
    "submission": ("SUBMISSION",),
    "coverpage": ("COVERPAGE",),
    "summarypage": ("SUMMARYPAGE",),
    "infotable": ("INFOTABLE", "INFOTABLE_SK"),
}


def _now_utc_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _resolve_user_agent(user_agent: str | None = None) -> str:
    return str(user_agent or os.getenv("SEC_USER_AGENT") or DEFAULT_SEC_USER_AGENT).strip()


def _normalize_cik(value: Any) -> str | None:
    text = str(value or "").strip()
    digits = "".join(ch for ch in text if ch.isdigit())
    if not digits:
        return None
    return digits.zfill(10)[-10:]


def _normalize_accession(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return None
    return text


def _date_text(value: Any) -> str | None:
    text = _clean_text(value)
    if not text:
        return None
    parsed = pd.to_datetime(text, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.date().isoformat()


def _int_value(value: Any) -> int | None:
    text = _clean_text(value)
    if not text:
        return None
    try:
        return int(float(text.replace(",", "")))
    except (TypeError, ValueError):
        return None


def _float_value(value: Any) -> float | None:
    text = _clean_text(value)
    if not text:
        return None
    try:
        return float(text.replace(",", ""))
    except (TypeError, ValueError):
        return None


def _bool_flag(value: Any) -> int:
    text = str(value or "").strip().upper()
    return 1 if text in {"Y", "YES", "TRUE", "1", "X"} else 0


def _optional_bool_flag(value: Any) -> int | None:
    text = str(value or "").strip().upper()
    if not text:
        return None
    return 1 if text in {"Y", "YES", "TRUE", "1", "X"} else 0


def _normalize_frame_columns(frame: pd.DataFrame | None) -> pd.DataFrame:
    if frame is None or frame.empty:
        return pd.DataFrame()
    out = frame.copy()
    out.columns = [str(column).strip().upper() for column in out.columns]
    return out


def _records(frame: pd.DataFrame | None) -> list[dict[str, Any]]:
    normalized = _normalize_frame_columns(frame)
    if normalized.empty:
        return []
    normalized = normalized.where(pd.notna(normalized), None)
    return normalized.to_dict(orient="records")


def _index_by_accession(frame: pd.DataFrame | None) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in _records(frame):
        accession = _normalize_accession(row.get("ACCESSION_NUMBER"))
        if accession:
            indexed[accession] = row
    return indexed


def _filing_source_ref(cik: str | None, accession_number: str | None, fallback: str | None = None) -> str | None:
    if not cik or not accession_number:
        return fallback
    accession_clean = accession_number.replace("-", "")
    try:
        cik_path = str(int(cik))
    except ValueError:
        cik_path = cik.lstrip("0") or cik
    return f"https://www.sec.gov/Archives/edgar/data/{cik_path}/{accession_clean}/"


def _build_manager_rows(filings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for filing in filings:
        cik = str(filing.get("cik") or "").strip()
        if cik:
            grouped[cik].append(filing)

    manager_rows: list[dict[str, Any]] = []
    for cik, rows in grouped.items():
        latest = sorted(
            rows,
            key=lambda row: (
                str(row.get("period_of_report") or ""),
                str(row.get("filing_date") or ""),
                str(row.get("accession_number") or ""),
            ),
            reverse=True,
        )[0]
        manager_rows.append(
            {
                "cik": cik,
                "manager_name": latest.get("manager_name"),
                "latest_accession_number": latest.get("accession_number"),
                "latest_report_period": latest.get("period_of_report"),
                "latest_filing_date": latest.get("filing_date"),
                "filing_count": len({row.get("accession_number") for row in rows if row.get("accession_number")}),
                "source": "sec_form_13f_dataset",
                "source_ref": latest.get("source_ref"),
                "last_collected_at": latest.get("collected_at"),
            }
        )
    return manager_rows


def normalize_sec_13f_frames(
    frames: dict[str, pd.DataFrame],
    *,
    source_dataset: str,
    source_ref: str | None = None,
    collected_at: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Normalize official SEC 13F data set frames into DB-ready rows."""
    collected = collected_at or _now_utc_text()
    submission_rows = _records(frames.get("submission"))
    cover_by_accession = _index_by_accession(frames.get("coverpage"))
    summary_by_accession = _index_by_accession(frames.get("summarypage"))

    filing_rows: list[dict[str, Any]] = []
    filing_by_accession: dict[str, dict[str, Any]] = {}
    for row in submission_rows:
        accession = _normalize_accession(row.get("ACCESSION_NUMBER"))
        cik = _normalize_cik(row.get("CIK"))
        if not accession or not cik:
            continue
        cover = cover_by_accession.get(accession, {})
        summary = summary_by_accession.get(accession, {})
        manager_name = _clean_text(cover.get("FILINGMANAGER_NAME")) or "Unknown manager"
        filing = {
            "accession_number": accession,
            "cik": cik,
            "manager_name": manager_name,
            "submission_type": _clean_text(row.get("SUBMISSIONTYPE")) or "13F-HR",
            "filing_date": _date_text(row.get("FILING_DATE")),
            "period_of_report": _date_text(row.get("PERIODOFREPORT")),
            "report_calendar_or_quarter": _date_text(cover.get("REPORTCALENDARORQUARTER")),
            "is_amendment": _bool_flag(cover.get("ISAMENDMENT")),
            "amendment_no": _int_value(cover.get("AMENDMENTNO")),
            "amendment_type": _clean_text(cover.get("AMENDMENTTYPE")),
            "report_type": _clean_text(cover.get("REPORTTYPE")),
            "form13f_file_number": _clean_text(cover.get("FORM13FFILENUMBER")),
            "table_entry_total": _int_value(summary.get("TABLEENTRYTOTAL")),
            "table_value_total": _float_value(summary.get("TABLEVALUETOTAL")),
            "is_confidential_omitted": _optional_bool_flag(summary.get("ISCONFIDENTIALOMITTED")),
            "source_dataset": source_dataset,
            "source_ref": _filing_source_ref(cik, accession, source_ref),
            "collected_at": collected,
        }
        if not filing["filing_date"] or not filing["period_of_report"]:
            continue
        filing_rows.append(filing)
        filing_by_accession[accession] = filing

    holding_rows: list[dict[str, Any]] = []
    for row in _records(frames.get("infotable")):
        accession = _normalize_accession(row.get("ACCESSION_NUMBER"))
        filing = filing_by_accession.get(str(accession or ""))
        if not filing:
            continue
        infotable_sk = _int_value(row.get("INFOTABLE_SK"))
        cusip = _clean_text(row.get("CUSIP"))
        issuer_name = _clean_text(row.get("NAMEOFISSUER"))
        if infotable_sk is None or not cusip or not issuer_name:
            continue
        holding_rows.append(
            {
                "accession_number": filing["accession_number"],
                "infotable_sk": infotable_sk,
                "cik": filing["cik"],
                "manager_name": filing["manager_name"],
                "report_period": filing["period_of_report"],
                "filing_date": filing["filing_date"],
                "issuer_name": issuer_name,
                "title_of_class": _clean_text(row.get("TITLEOFCLASS")),
                "cusip": cusip.upper(),
                "figi": _clean_text(row.get("FIGI")),
                "reported_value": _float_value(row.get("VALUE")),
                "shares_or_principal_amount": _float_value(row.get("SSHPRNAMT")),
                "amount_type": _clean_text(row.get("SSHPRNAMTTYPE")),
                "put_call": _clean_text(row.get("PUTCALL")),
                "investment_discretion": _clean_text(row.get("INVESTMENTDISCRETION")),
                "other_manager": _clean_text(row.get("OTHERMANAGER")),
                "voting_auth_sole": _float_value(row.get("VOTING_AUTH_SOLE")),
                "voting_auth_shared": _float_value(row.get("VOTING_AUTH_SHARED")),
                "voting_auth_none": _float_value(row.get("VOTING_AUTH_NONE")),
                "holding_symbol": None,
                "symbol_source": None,
                "sector": None,
                "industry": None,
                "source_dataset": source_dataset,
                "source_ref": filing["source_ref"] or source_ref,
                "collected_at": collected,
            }
        )

    return {
        "managers": _build_manager_rows(filing_rows),
        "filings": filing_rows,
        "holdings": holding_rows,
    }


def _dataset_key_from_name(name: str) -> str | None:
    normalized_name = Path(name).name.upper()
    for key, tokens in DATASET_FILE_KEYS.items():
        if all(token in normalized_name for token in tokens):
            return key
        if normalized_name.startswith(tokens[0]) and normalized_name.endswith((".TSV", ".TXT")):
            return key
    return None


def read_sec_13f_dataset_zip(zip_source: str | Path | bytes) -> dict[str, pd.DataFrame]:
    """Read official SEC 13F zip files into named data frames without DB writes."""
    if isinstance(zip_source, (str, Path)):
        zip_file = zipfile.ZipFile(Path(zip_source))
    else:
        zip_file = zipfile.ZipFile(io.BytesIO(zip_source))

    frames: dict[str, pd.DataFrame] = {}
    with zip_file:
        for member in zip_file.namelist():
            key = _dataset_key_from_name(member)
            if not key:
                continue
            with zip_file.open(member) as handle:
                frames[key] = pd.read_csv(
                    handle,
                    sep="\t",
                    dtype=str,
                    keep_default_na=False,
                    encoding="utf-8",
                )
    return frames


def download_sec_13f_dataset_zip(
    dataset_url: str,
    *,
    user_agent: str | None = None,
    timeout: float = 60.0,
) -> bytes:
    """Download a SEC 13F data set zip with declared fair-access headers."""
    request = urllib.request.Request(
        dataset_url,
        headers={
            "User-Agent": _resolve_user_agent(user_agent),
            "Accept-Encoding": "gzip, deflate",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"SEC 13F dataset request failed {exc.code}: {dataset_url}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"SEC 13F dataset request failed: {dataset_url} ({exc.reason})") from exc


def _sync_schema(db: MySQLClient) -> None:
    for table_name, create_sql in INSTITUTIONAL_13F_SCHEMAS.items():
        sync_table_schema(db, table_name, create_sql, DB_META)


def _upsert_manager_rows(db: MySQLClient, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0
    sql = """
        INSERT INTO institutional_13f_manager (
          cik, manager_name, latest_accession_number, latest_report_period, latest_filing_date,
          filing_count, source, source_ref, last_collected_at
        ) VALUES (
          %(cik)s, %(manager_name)s, %(latest_accession_number)s, %(latest_report_period)s, %(latest_filing_date)s,
          %(filing_count)s, %(source)s, %(source_ref)s, %(last_collected_at)s
        )
        ON DUPLICATE KEY UPDATE
          manager_name = VALUES(manager_name),
          latest_accession_number = VALUES(latest_accession_number),
          latest_report_period = VALUES(latest_report_period),
          latest_filing_date = VALUES(latest_filing_date),
          filing_count = GREATEST(filing_count, VALUES(filing_count)),
          source = VALUES(source),
          source_ref = VALUES(source_ref),
          last_collected_at = VALUES(last_collected_at)
    """
    db.executemany(sql, rows)
    return len(rows)


def _upsert_filing_rows(db: MySQLClient, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0
    sql = """
        INSERT INTO institutional_13f_filing (
          accession_number, cik, manager_name, submission_type, filing_date, period_of_report,
          report_calendar_or_quarter, is_amendment, amendment_no, amendment_type, report_type,
          form13f_file_number, table_entry_total, table_value_total, is_confidential_omitted,
          source_dataset, source_ref, collected_at
        ) VALUES (
          %(accession_number)s, %(cik)s, %(manager_name)s, %(submission_type)s, %(filing_date)s, %(period_of_report)s,
          %(report_calendar_or_quarter)s, %(is_amendment)s, %(amendment_no)s, %(amendment_type)s, %(report_type)s,
          %(form13f_file_number)s, %(table_entry_total)s, %(table_value_total)s, %(is_confidential_omitted)s,
          %(source_dataset)s, %(source_ref)s, %(collected_at)s
        )
        ON DUPLICATE KEY UPDATE
          cik = VALUES(cik),
          manager_name = VALUES(manager_name),
          submission_type = VALUES(submission_type),
          filing_date = VALUES(filing_date),
          period_of_report = VALUES(period_of_report),
          report_calendar_or_quarter = VALUES(report_calendar_or_quarter),
          is_amendment = VALUES(is_amendment),
          amendment_no = VALUES(amendment_no),
          amendment_type = VALUES(amendment_type),
          report_type = VALUES(report_type),
          form13f_file_number = VALUES(form13f_file_number),
          table_entry_total = VALUES(table_entry_total),
          table_value_total = VALUES(table_value_total),
          is_confidential_omitted = VALUES(is_confidential_omitted),
          source_dataset = VALUES(source_dataset),
          source_ref = VALUES(source_ref),
          collected_at = VALUES(collected_at)
    """
    db.executemany(sql, rows)
    return len(rows)


def _upsert_holding_rows(db: MySQLClient, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0
    sql = """
        INSERT INTO institutional_13f_holding (
          accession_number, infotable_sk, cik, manager_name, report_period, filing_date,
          issuer_name, title_of_class, cusip, figi, reported_value, shares_or_principal_amount,
          amount_type, put_call, investment_discretion, other_manager,
          voting_auth_sole, voting_auth_shared, voting_auth_none,
          holding_symbol, symbol_source, sector, industry, source_dataset, source_ref, collected_at
        ) VALUES (
          %(accession_number)s, %(infotable_sk)s, %(cik)s, %(manager_name)s, %(report_period)s, %(filing_date)s,
          %(issuer_name)s, %(title_of_class)s, %(cusip)s, %(figi)s, %(reported_value)s, %(shares_or_principal_amount)s,
          %(amount_type)s, %(put_call)s, %(investment_discretion)s, %(other_manager)s,
          %(voting_auth_sole)s, %(voting_auth_shared)s, %(voting_auth_none)s,
          %(holding_symbol)s, %(symbol_source)s, %(sector)s, %(industry)s, %(source_dataset)s, %(source_ref)s, %(collected_at)s
        )
        ON DUPLICATE KEY UPDATE
          cik = VALUES(cik),
          manager_name = VALUES(manager_name),
          report_period = VALUES(report_period),
          filing_date = VALUES(filing_date),
          issuer_name = VALUES(issuer_name),
          title_of_class = VALUES(title_of_class),
          cusip = VALUES(cusip),
          figi = VALUES(figi),
          reported_value = VALUES(reported_value),
          shares_or_principal_amount = VALUES(shares_or_principal_amount),
          amount_type = VALUES(amount_type),
          put_call = VALUES(put_call),
          investment_discretion = VALUES(investment_discretion),
          other_manager = VALUES(other_manager),
          voting_auth_sole = VALUES(voting_auth_sole),
          voting_auth_shared = VALUES(voting_auth_shared),
          voting_auth_none = VALUES(voting_auth_none),
          holding_symbol = COALESCE(VALUES(holding_symbol), holding_symbol),
          symbol_source = COALESCE(VALUES(symbol_source), symbol_source),
          sector = COALESCE(VALUES(sector), sector),
          industry = COALESCE(VALUES(industry), industry),
          source_dataset = VALUES(source_dataset),
          source_ref = VALUES(source_ref),
          collected_at = VALUES(collected_at)
    """
    db.executemany(sql, rows)
    return len(rows)


def collect_and_store_sec_13f_dataset(
    *,
    dataset_zip_path: str | Path | None = None,
    dataset_url: str | None = None,
    source_dataset: str | None = None,
    user_agent: str | None = None,
    request_timeout: float = 60.0,
    request_sleep: float = 0.0,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, Any]:
    """Collect a SEC Form 13F official data set into finance_meta tables."""
    if not dataset_zip_path and not dataset_url:
        raise ValueError("dataset_zip_path or dataset_url is required for SEC Form 13F collection")

    if request_sleep > 0:
        time.sleep(float(request_sleep))

    source_ref = str(dataset_url or dataset_zip_path or SEC_13F_DATASETS_PAGE)
    dataset_label = source_dataset or Path(str(dataset_zip_path or dataset_url)).stem or "sec_form_13f_dataset"
    if dataset_zip_path:
        frames = read_sec_13f_dataset_zip(dataset_zip_path)
    else:
        frames = read_sec_13f_dataset_zip(
            download_sec_13f_dataset_zip(str(dataset_url), user_agent=user_agent, timeout=float(request_timeout))
        )

    normalized = normalize_sec_13f_frames(
        frames,
        source_dataset=dataset_label,
        source_ref=source_ref,
        collected_at=_now_utc_text(),
    )

    db = MySQLClient(host, user, password, port)
    try:
        db.use_db(DB_META)
        _sync_schema(db)
        manager_rows = _upsert_manager_rows(db, normalized["managers"])
        filing_rows = _upsert_filing_rows(db, normalized["filings"])
        holding_rows = _upsert_holding_rows(db, normalized["holdings"])
    finally:
        db.close()

    return {
        "source": "sec_form_13f_dataset",
        "source_dataset": dataset_label,
        "source_ref": source_ref,
        "target_tables": [
            "finance_meta.institutional_13f_manager",
            "finance_meta.institutional_13f_filing",
            "finance_meta.institutional_13f_holding",
            "finance_meta.institutional_13f_cusip_symbol_map",
        ],
        "rows_written": manager_rows + filing_rows + holding_rows,
        "managers_written": manager_rows,
        "filings_written": filing_rows,
        "holdings_written": holding_rows,
        "source_limitations": SEC_13F_SOURCE_CAVEATS,
        "execution_boundary": {
            "db_write": True,
            "registry_write": False,
            "memo_persistence": False,
            "preset_persistence": False,
            "report_file_write": False,
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
        },
    }
