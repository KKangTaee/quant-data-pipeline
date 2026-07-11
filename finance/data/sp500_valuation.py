from __future__ import annotations

import re
from io import StringIO
from pathlib import Path
from typing import Any
from urllib.parse import urljoin
from urllib.request import Request, urlopen

import pandas as pd

from .db.mysql import MySQLClient
from .db.schema import VALUATION_SCHEMAS, sync_table_schema


FEDERAL_RESERVE_BASE_URL = "https://www.federalreserve.gov"
FOMC_CALENDAR_URL = f"{FEDERAL_RESERVE_BASE_URL}/monetarypolicy/fomccalendars.htm"
SHILLER_SOURCE = "robert_shiller_irrational_exuberance"
SHILLER_SOURCE_URL = "https://www.econ.yale.edu/~shiller/data/ie_data.xls"
SP500_EARNINGS_SOURCE = "sp_dow_jones_index_earnings"
FOMC_SEP_SOURCE = "federal_reserve_sep"
DB_META = "finance_meta"


def _fetch_text(url: str, *, timeout: int = 30) -> str:
    request = Request(
        url,
        headers={"User-Agent": "quant-data-pipeline/1.0 (+valuation research)"},
    )
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def _optional_float(value: Any) -> float | None:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(numeric):
        return None
    return numeric


def _shiller_month(value: Any) -> str | None:
    numeric = _optional_float(value)
    if numeric is None:
        return None
    text = f"{numeric:.2f}"
    year_text, month_text = text.split(".", 1)
    month = int(month_text)
    if month < 1 or month > 12:
        return None
    return f"{int(year_text):04d}-{month:02d}-01"


def normalize_shiller_monthly_frame(
    frame: pd.DataFrame,
    *,
    collected_at: str | None = None,
) -> list[dict[str, Any]]:
    """Normalize Shiller monthly price/earnings rows for descriptive valuation use."""
    rows: list[dict[str, Any]] = []
    for item in frame.to_dict("records"):
        observation_month = _shiller_month(item.get("Date"))
        spx_level = _optional_float(item.get("P"))
        trailing_eps = _optional_float(item.get("E"))
        cape = _optional_float(item.get("CAPE"))
        if observation_month is None or spx_level is None or trailing_eps is None:
            continue
        if spx_level <= 0 or trailing_eps <= 0:
            continue
        rows.append(
            {
                "observation_month": observation_month,
                "spx_level": spx_level,
                "trailing_eps": trailing_eps,
                "trailing_pe": spx_level / trailing_eps,
                "cape": cape,
                "data_quality": "interpolated",
                "source": SHILLER_SOURCE,
                "source_ref": SHILLER_SOURCE_URL,
                "source_version": None,
                "collected_at": collected_at,
                "error_msg": None,
            }
        )
    return rows


def read_shiller_workbook(
    source_ref: str = SHILLER_SOURCE_URL,
    *,
    collected_at: str | None = None,
) -> list[dict[str, Any]]:
    """Read Robert Shiller's monthly workbook and normalize its Data sheet."""
    frame = pd.read_excel(source_ref, sheet_name="Data", header=7)
    rows = normalize_shiller_monthly_frame(frame, collected_at=collected_at)
    for row in rows:
        row["source_ref"] = source_ref
    return rows


def _normalized_status(value: Any) -> str | None:
    normalized = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "actual": "actual",
        "reported": "actual",
        "estimate": "estimate",
        "estimated": "estimate",
        "consensus": "estimate",
        "mixed": "mixed",
        "blended": "mixed",
    }
    return aliases.get(normalized)


def normalize_index_earnings_frame(
    frame: pd.DataFrame,
    *,
    source_release_date: str,
    source_ref: str | None = None,
    collected_at: str | None = None,
) -> list[dict[str, Any]]:
    """Normalize explicit S&P index EPS rows without inferring actual/estimate status."""
    release_date = pd.to_datetime(source_release_date, errors="coerce")
    if pd.isna(release_date):
        raise ValueError(f"Invalid source release date: {source_release_date!r}")

    rows: list[dict[str, Any]] = []
    for item in frame.to_dict("records"):
        period_end = pd.to_datetime(item.get("period_end"), errors="coerce")
        value_status = _normalized_status(item.get("status") or item.get("value_status"))
        period_type = str(item.get("period_type") or "quarterly").strip().lower()
        if pd.isna(period_end) or value_status is None:
            continue
        if period_type not in {"quarterly", "annual", "ttm"}:
            continue
        for column, earnings_basis in (
            ("as_reported_eps", "as_reported"),
            ("operating_eps", "operating"),
        ):
            eps = _optional_float(item.get(column))
            if eps is None or eps <= 0:
                continue
            rows.append(
                {
                    "period_end": pd.Timestamp(period_end).strftime("%Y-%m-%d"),
                    "period_type": period_type,
                    "earnings_basis": earnings_basis,
                    "value_status": value_status,
                    "eps": eps,
                    "source": SP500_EARNINGS_SOURCE,
                    "source_ref": source_ref,
                    "source_release_date": pd.Timestamp(release_date).strftime("%Y-%m-%d"),
                    "collected_at": collected_at,
                    "error_msg": None,
                }
            )
    return rows


def read_sp500_index_earnings_workbook(
    workbook_path: str | Path,
    *,
    source_release_date: str,
    source_ref: str | None = None,
    collected_at: str | None = None,
) -> list[dict[str, Any]]:
    """Read a normalized S&P index-earnings workbook supplied by the operator.

    The importer intentionally requires explicit period/status columns. It does not
    infer whether a value is actual or estimated from workbook color or position.
    """
    frame = pd.read_excel(workbook_path)
    aliases = {
        "period end": "period_end",
        "period_end": "period_end",
        "period type": "period_type",
        "period_type": "period_type",
        "status": "status",
        "value status": "status",
        "value_status": "status",
        "as reported eps": "as_reported_eps",
        "as-reported eps": "as_reported_eps",
        "as_reported_eps": "as_reported_eps",
        "operating eps": "operating_eps",
        "operating_eps": "operating_eps",
    }
    renamed = {
        column: aliases.get(re.sub(r"\s+", " ", str(column).strip().lower()))
        for column in frame.columns
    }
    frame = frame.rename(columns={key: value for key, value in renamed.items() if value})
    required = {"period_end", "status"}
    if not required.issubset(frame.columns) or not {
        "as_reported_eps",
        "operating_eps",
    }.intersection(frame.columns):
        raise ValueError(
            "S&P earnings workbook requires period_end, status, and at least one EPS column."
        )
    return normalize_index_earnings_frame(
        frame,
        source_release_date=source_release_date,
        source_ref=source_ref or str(workbook_path),
        collected_at=collected_at,
    )


def discover_latest_fomc_sep_url(calendar_html: str) -> str:
    """Return the latest official accessible FOMC projections URL found in calendar HTML."""
    matches = re.findall(
        r'href=["\']([^"\']*fomcprojtabl(\d{8})\.htm(?:\?[^"\']*)?)["\']',
        str(calendar_html or ""),
        flags=re.IGNORECASE,
    )
    if not matches:
        raise ValueError("FOMC SEP accessible-material link was not found.")
    href, _ = max(matches, key=lambda match: match[1])
    return urljoin(FEDERAL_RESERVE_BASE_URL, href)


def _sep_release_date(source_url: str, html: str) -> str:
    url_match = re.search(r"fomcprojtabl(\d{8})", source_url)
    if url_match:
        return pd.to_datetime(url_match.group(1), format="%Y%m%d").strftime("%Y-%m-%d")
    text_match = re.search(
        r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}",
        html,
    )
    if not text_match:
        raise ValueError("FOMC SEP release date was not found.")
    return pd.to_datetime(text_match.group(0)).strftime("%Y-%m-%d")


def _range_pair(value: Any) -> tuple[float, float] | None:
    numbers = [float(item) for item in re.findall(r"-?\d+(?:\.\d+)?", str(value or ""))]
    if len(numbers) < 2:
        return None
    return numbers[0], numbers[1]


def _sep_variable(value: Any) -> str | None:
    normalized = re.sub(r"\s+", " ", str(value or "")).strip().lower()
    if normalized == "change in real gdp":
        return "real_gdp"
    if normalized == "pce inflation":
        return "pce_inflation"
    return None


def parse_fomc_sep_html(
    html: str,
    *,
    source_url: str,
    collected_at: str | None = None,
) -> list[dict[str, Any]]:
    """Parse GDP/PCE median and central-tendency values from official SEP accessible HTML."""
    release_date = _sep_release_date(source_url, html)
    tables = pd.read_html(StringIO(html))
    if not tables:
        raise ValueError("FOMC SEP table was not found.")

    rows: list[dict[str, Any]] = []
    first = tables[0]
    if isinstance(first.columns, pd.MultiIndex):
        variable_column = first.columns[0]
        for _, item in first.iterrows():
            variable_name = _sep_variable(item.get(variable_column))
            if variable_name is None:
                continue
            for column in first.columns[1:]:
                group = str(column[0]).lower()
                year_text = str(column[1])
                if not year_text.isdigit():
                    continue
                target_year = int(year_text)
                value = item.get(column)
                if group.startswith("median"):
                    numeric = _optional_float(value)
                    if numeric is not None:
                        rows.append(
                            _sep_row(
                                release_date,
                                target_year,
                                variable_name,
                                "median",
                                numeric,
                                source_url,
                                collected_at,
                            )
                        )
                elif group.startswith("central tendency"):
                    pair = _range_pair(value)
                    if pair is not None:
                        rows.extend(
                            [
                                _sep_row(
                                    release_date,
                                    target_year,
                                    variable_name,
                                    "central_tendency_lower",
                                    pair[0],
                                    source_url,
                                    collected_at,
                                ),
                                _sep_row(
                                    release_date,
                                    target_year,
                                    variable_name,
                                    "central_tendency_upper",
                                    pair[1],
                                    source_url,
                                    collected_at,
                                ),
                            ]
                        )
        return rows

    columns = [str(column) for column in first.columns]
    year_columns = [column for column in columns if column.isdigit()]
    for _, item in first.iterrows():
        variable_name = _sep_variable(item.get(columns[0]))
        statistic = str(item.get(columns[1]) or "").strip().lower()
        if variable_name is None:
            continue
        for year_column in year_columns:
            target_year = int(year_column)
            value = item.get(year_column)
            if statistic == "median":
                numeric = _optional_float(value)
                if numeric is not None:
                    rows.append(
                        _sep_row(
                            release_date,
                            target_year,
                            variable_name,
                            "median",
                            numeric,
                            source_url,
                            collected_at,
                        )
                    )
            elif statistic == "central tendency":
                pair = _range_pair(value)
                if pair is not None:
                    rows.extend(
                        [
                            _sep_row(
                                release_date,
                                target_year,
                                variable_name,
                                "central_tendency_lower",
                                pair[0],
                                source_url,
                                collected_at,
                            ),
                            _sep_row(
                                release_date,
                                target_year,
                                variable_name,
                                "central_tendency_upper",
                                pair[1],
                                source_url,
                                collected_at,
                            ),
                        ]
                    )
    if not rows:
        raise ValueError("FOMC SEP GDP/PCE values were not found.")
    return rows


def _sep_row(
    release_date: str,
    target_year: int,
    variable_name: str,
    statistic_name: str,
    value_pct: float,
    source_url: str,
    collected_at: str | None,
) -> dict[str, Any]:
    return {
        "release_date": release_date,
        "target_year": target_year,
        "variable_name": variable_name,
        "statistic_name": statistic_name,
        "value_pct": value_pct,
        "source": FOMC_SEP_SOURCE,
        "source_ref": source_url,
        "collected_at": collected_at,
        "error_msg": None,
    }


def _ensure_table(db: MySQLClient, table_name: str) -> None:
    schema = VALUATION_SCHEMAS[table_name]
    db.execute(schema)
    sync_table_schema(db, table_name, schema, DB_META)


def _open_meta_db(
    db_factory: Any,
    *,
    host: str,
    user: str,
    password: str,
    port: int,
) -> MySQLClient:
    db = db_factory(host, user, password, port)
    db.use_db(DB_META)
    return db


def _upsert_monthly_rows(db: MySQLClient, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    db.executemany(
        """
        INSERT INTO sp500_monthly_valuation (
          observation_month, spx_level, trailing_eps, trailing_pe, cape,
          data_quality, source, source_ref, source_version, collected_at, error_msg
        ) VALUES (
          %(observation_month)s, %(spx_level)s, %(trailing_eps)s, %(trailing_pe)s, %(cape)s,
          %(data_quality)s, %(source)s, %(source_ref)s, %(source_version)s, %(collected_at)s, %(error_msg)s
        )
        ON DUPLICATE KEY UPDATE
          spx_level = VALUES(spx_level), trailing_eps = VALUES(trailing_eps),
          trailing_pe = VALUES(trailing_pe), cape = VALUES(cape),
          data_quality = VALUES(data_quality), source_ref = VALUES(source_ref),
          source_version = VALUES(source_version), collected_at = VALUES(collected_at),
          error_msg = VALUES(error_msg)
        """,
        rows,
    )


def _upsert_earnings_rows(db: MySQLClient, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    db.executemany(
        """
        INSERT INTO sp500_index_earnings (
          period_end, period_type, earnings_basis, value_status, eps, source,
          source_ref, source_release_date, collected_at, error_msg
        ) VALUES (
          %(period_end)s, %(period_type)s, %(earnings_basis)s, %(value_status)s, %(eps)s, %(source)s,
          %(source_ref)s, %(source_release_date)s, %(collected_at)s, %(error_msg)s
        )
        ON DUPLICATE KEY UPDATE
          eps = VALUES(eps), source_ref = VALUES(source_ref),
          collected_at = VALUES(collected_at), error_msg = VALUES(error_msg)
        """,
        rows,
    )


def _upsert_sep_rows(db: MySQLClient, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    db.executemany(
        """
        INSERT INTO fomc_sep_projection (
          release_date, target_year, variable_name, statistic_name, value_pct,
          source, source_ref, collected_at, error_msg
        ) VALUES (
          %(release_date)s, %(target_year)s, %(variable_name)s, %(statistic_name)s, %(value_pct)s,
          %(source)s, %(source_ref)s, %(collected_at)s, %(error_msg)s
        )
        ON DUPLICATE KEY UPDATE
          release_date = VALUES(release_date), value_pct = VALUES(value_pct),
          source = VALUES(source), source_ref = VALUES(source_ref),
          collected_at = VALUES(collected_at), error_msg = VALUES(error_msg)
        """,
        rows,
    )


def collect_and_store_shiller_monthly_valuation(
    *,
    source_ref: str = SHILLER_SOURCE_URL,
    workbook_reader: Any = read_shiller_workbook,
    db_factory: Any = MySQLClient,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, Any]:
    """Collect and idempotently store Shiller monthly price/earnings history."""
    rows = workbook_reader(source_ref=source_ref)
    db = _open_meta_db(
        db_factory, host=host, user=user, password=password, port=port
    )
    try:
        _ensure_table(db, "sp500_monthly_valuation")
        _upsert_monthly_rows(db, rows)
    finally:
        db.close()
    return {
        "rows_written": len(rows),
        "source": SHILLER_SOURCE,
        "source_ref": source_ref,
        "warnings": [] if rows else ["정규화 가능한 Shiller 월별 행이 없습니다."],
    }


def import_and_store_sp500_index_earnings(
    workbook_path: str | Path,
    *,
    source_release_date: str,
    workbook_reader: Any = read_sp500_index_earnings_workbook,
    db_factory: Any = MySQLClient,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, Any]:
    """Import explicit actual/estimate S&P index EPS rows with release vintage."""
    release_date = pd.to_datetime(source_release_date, errors="coerce")
    if pd.isna(release_date):
        raise ValueError(f"Invalid source release date: {source_release_date!r}")
    release_text = pd.Timestamp(release_date).strftime("%Y-%m-%d")
    rows = workbook_reader(
        workbook_path,
        source_release_date=release_text,
        source_ref=str(workbook_path),
    )
    db = _open_meta_db(
        db_factory, host=host, user=user, password=password, port=port
    )
    try:
        _ensure_table(db, "sp500_index_earnings")
        _upsert_earnings_rows(db, rows)
    finally:
        db.close()
    return {
        "rows_written": len(rows),
        "source": SP500_EARNINGS_SOURCE,
        "source_ref": str(workbook_path),
        "release_date": release_text,
        "warnings": [] if rows else ["명시적 상태가 있는 S&P EPS 행이 없습니다."],
    }


def collect_and_store_fomc_sep(
    *,
    calendar_url: str = FOMC_CALENDAR_URL,
    calendar_fetcher: Any = _fetch_text,
    sep_fetcher: Any = _fetch_text,
    db_factory: Any = MySQLClient,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, Any]:
    """Discover, parse, and preserve the latest official SEP release vintage."""
    calendar_html = calendar_fetcher(calendar_url)
    source_ref = discover_latest_fomc_sep_url(calendar_html)
    rows = parse_fomc_sep_html(sep_fetcher(source_ref), source_url=source_ref)
    db = _open_meta_db(
        db_factory, host=host, user=user, password=password, port=port
    )
    try:
        _ensure_table(db, "fomc_sep_projection")
        _upsert_sep_rows(db, rows)
    finally:
        db.close()
    release_date = rows[0]["release_date"] if rows else None
    return {
        "rows_written": len(rows),
        "source": FOMC_SEP_SOURCE,
        "source_ref": source_ref,
        "release_date": release_date,
        "warnings": [] if rows else ["GDP/PCE SEP 행이 없습니다."],
    }
