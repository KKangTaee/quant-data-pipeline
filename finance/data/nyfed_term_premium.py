"""Collect the current New York Fed ACM 10-year term-premium workbook vintage."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Callable
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

import pandas as pd
from bs4 import BeautifulSoup

from .db.mysql import MySQLClient
from .db.schema import PROVIDER_SCHEMAS, sync_table_schema
from .fred_vintages import VINTAGE_TABLE, upsert_fred_vintage_rows


NYFED_BASE_URL = "https://www.newyorkfed.org"
ACM_PAGE_URL = f"{NYFED_BASE_URL}/research/data_indicators/term-premia-tabs"
ACM_DOWNLOAD_URL = (
    f"{NYFED_BASE_URL}/medialibrary/media/research/"
    "data_indicators/ACMTermPremium.xls"
)
DB_META = "finance_meta"
ACM_SOURCE_MODE = "current_workbook_collection_vintage"


def _official_url(href: str) -> str:
    url = urljoin(NYFED_BASE_URL, str(href or "").strip())
    host = (urlparse(url).hostname or "").casefold()
    if host not in {"newyorkfed.org", "www.newyorkfed.org"}:
        raise ValueError("ACM download must use the official New York Fed host")
    return url


def discover_acm_download_url(page_html: str) -> str:
    """Resolve the official ACM workbook link exposed by the web application."""

    soup = BeautifulSoup(page_html, "html.parser")
    for anchor in soup.find_all("a", href=True):
        href = str(anchor.get("href") or "")
        if "acmtermpremium.xls" in href.casefold():
            return _official_url(href)
    # The current page renders the download from its JavaScript bundle. Keep the
    # documented official file as a bounded fallback only on that application page.
    normalized = str(page_html or "").casefold()
    if "treasury term premia" in normalized or "term-premia/js/main" in normalized:
        return ACM_DOWNLOAD_URL
    raise ValueError("Official ACM workbook link was not found")


def _aware_utc(value: str | datetime) -> datetime:
    parsed = (
        value
        if isinstance(value, datetime)
        else datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    )
    if parsed.tzinfo is None:
        raise ValueError("collected_at must include a timezone")
    return parsed.astimezone(timezone.utc)


def normalize_acm_term_premium(
    frame: pd.DataFrame,
    *,
    collected_at: str | datetime,
    source_ref: str,
) -> list[dict[str, object]]:
    """Normalize ACMTP10 without treating workbook history as historical vintages."""

    columns = {str(column).strip().upper(): column for column in frame.columns}
    if "DATE" not in columns or "ACMTP10" not in columns:
        raise ValueError("ACM workbook must contain DATE and ACMTP10")
    collected = _aware_utc(collected_at)
    realtime_start = collected.date().isoformat()
    collected_text = collected.replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")
    released_at = collected.isoformat()

    dates = pd.to_datetime(frame[columns["DATE"]], errors="coerce")
    values = pd.to_numeric(frame[columns["ACMTP10"]], errors="coerce")
    rows: list[dict[str, object]] = []
    for observation, value in zip(dates, values):
        if pd.isna(observation) or pd.isna(value):
            continue
        observation_date = observation.date().isoformat()
        rows.append(
            {
                "series_id": "ACMTP10",
                "observation_date": observation_date,
                "realtime_start": realtime_start,
                "realtime_end": "9999-12-31",
                "released_at": released_at,
                "source": "new_york_fed_acm",
                "source_type": "official",
                "source_mode": ACM_SOURCE_MODE,
                "source_ref": _official_url(source_ref),
                "series_name": "ACM 10-Year Treasury Term Premium",
                "factor_group": "rates",
                "frequency": "daily",
                "units": "percent",
                "value": float(value),
                "release_lag_days": (
                    collected.date() - observation.date()
                ).days,
                "coverage_status": "actual",
                "missing_fields_json": json.dumps([]),
                "collected_at": collected_text,
                "error_msg": None,
            }
        )
    return sorted(rows, key=lambda row: str(row["observation_date"]))


def _fetch_html(url: str) -> str:
    request = Request(
        url,
        headers={"User-Agent": "quant-data-pipeline/1.0 research@example.com"},
    )
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def _read_daily_workbook(url: str) -> pd.DataFrame:
    return pd.read_excel(url, sheet_name="ACM Daily")


def collect_and_store_acm_term_premium(
    *,
    page_url: str = ACM_PAGE_URL,
    connection: object | None = None,
    fetch_html: Callable[[str], str] | None = None,
    read_workbook: Callable[[str], pd.DataFrame] | None = None,
    collected_at: str | datetime | None = None,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, object]:
    """Persist today's workbook snapshot and explicitly limit historical replay."""

    fetcher = fetch_html or _fetch_html
    reader = read_workbook or _read_daily_workbook
    source_ref = discover_acm_download_url(fetcher(page_url))
    frame = reader(source_ref)
    if not isinstance(frame, pd.DataFrame):
        raise ValueError("ACM workbook reader must return a DataFrame")
    rows = normalize_acm_term_premium(
        frame,
        collected_at=collected_at or datetime.now(timezone.utc),
        source_ref=source_ref,
    )
    if not rows:
        raise ValueError("ACM workbook contains no usable ACMTP10 rows")

    owns_connection = connection is None
    db = connection or MySQLClient(host, user, password, port)
    try:
        db.use_db(DB_META)
        schema = PROVIDER_SCHEMAS[VINTAGE_TABLE]
        db.execute(schema)
        sync_table_schema(db, VINTAGE_TABLE, schema, DB_META)
        stored = upsert_fred_vintage_rows(rows, db=db)
    finally:
        if owns_connection:
            db.close()
    return {
        "stored": stored,
        "coverage_status": "LIMITED",
        "source_ref": source_ref,
    }
