from __future__ import annotations

import json
import logging
import re
import time
from collections.abc import Callable
from datetime import date, datetime, timedelta, timezone
from io import BytesIO
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4

from bs4 import BeautifulSoup
import pandas as pd

from .db.mysql import MySQLClient
from .sentiment_store import (
    DB_META,
    MACRO_TABLE,
    MARKET_SENTIMENT_BATCH_TABLE,
    MARKET_SENTIMENT_SNAPSHOT_TABLE,
    ensure_market_sentiment_schema,
    persist_market_sentiment_source_capture,
    record_market_sentiment_source_failure,
)


LOGGER = logging.getLogger(__name__)

CNN_FEAR_GREED_URL = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
CNN_FEAR_GREED_PAGE = "https://www.cnn.com/markets/fear-and-greed"
AAII_SENTIMENT_URL = "https://www.aaii.com/sentimentsurvey/sent_results"
AAII_SENTIMENT_HISTORY_URL = "https://www.aaii.com/files/surveys/sentiment.xls"
AAII_DAILY_CAPTURE_WEEKS = 26
DEFAULT_TIMEOUT = 20
DEFAULT_RETRIES = 2
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
)

CNN_COMPONENTS: dict[str, tuple[str, str]] = {
    "market_momentum_sp500": ("CNN_FNG_MARKET_MOMENTUM_SP500", "Market Momentum"),
    "stock_price_strength": ("CNN_FNG_STOCK_PRICE_STRENGTH", "Stock Price Strength"),
    "stock_price_breadth": ("CNN_FNG_STOCK_PRICE_BREADTH", "Stock Price Breadth"),
    "put_call_options": ("CNN_FNG_PUT_CALL_OPTIONS", "Put / Call Options"),
    "market_volatility_vix": ("CNN_FNG_MARKET_VOLATILITY_VIX", "Market Volatility"),
    "junk_bond_demand": ("CNN_FNG_JUNK_BOND_DEMAND", "Junk Bond Demand"),
    "safe_haven_demand": ("CNN_FNG_SAFE_HAVEN_DEMAND", "Safe Haven Demand"),
}

AAII_SERIES: dict[str, tuple[str, str, str]] = {
    "bullish": ("AAII_BULLISH", "AAII Bullish Sentiment", "percent"),
    "neutral": ("AAII_NEUTRAL", "AAII Neutral Sentiment", "percent"),
    "bearish": ("AAII_BEARISH", "AAII Bearish Sentiment", "percent"),
    "spread": ("AAII_BULL_BEAR_SPREAD", "AAII Bull-Bear Spread", "percentage_point"),
}
EXPECTED_SENTIMENT_SERIES = {
    "cnn_fear_greed": {"CNN_FEAR_GREED", *[value[0] for value in CNN_COMPONENTS.values()]},
    "aaii_sentiment_survey": {value[0] for value in AAII_SERIES.values()},
}


def _utc_now_string() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text in {".", "-", "--", "NA", "N/A", "nan", "None"}:
        return None
    try:
        return float(text.replace(",", "").replace("%", ""))
    except ValueError:
        return None


def _date_string(value: Any) -> str | None:
    if value is None:
        return None
    parsed = pd.to_datetime(value, errors="coerce", utc=True)
    if pd.isna(parsed):
        return None
    return pd.Timestamp(parsed).strftime("%Y-%m-%d")


def _epoch_ms_date(value: Any) -> str | None:
    numeric = _optional_float(value)
    if numeric is None:
        return _date_string(value)
    unit = "ms" if numeric > 10_000_000_000 else "s"
    parsed = pd.to_datetime(numeric, unit=unit, errors="coerce", utc=True)
    if pd.isna(parsed):
        return None
    return pd.Timestamp(parsed).strftime("%Y-%m-%d")


def _metadata_json(metadata: dict[str, Any]) -> str:
    compact = {
        key: value
        for key, value in metadata.items()
        if value is not None and value != "" and not (isinstance(value, float) and pd.isna(value))
    }
    return json.dumps(compact, ensure_ascii=False, sort_keys=True)


def _sentiment_row(
    series_id: str,
    *,
    observation_date: str,
    source: str,
    source_mode: str,
    source_ref: str,
    series_name: str,
    category: str,
    units: str,
    value: float,
    collected_at: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "series_id": series_id,
        "observation_date": observation_date,
        "source": source,
        "source_type": "official",
        "source_mode": source_mode,
        "source_ref": source_ref,
        "series_name": series_name,
        "category": category,
        "frequency": "daily" if source == "cnn_fear_greed" else "weekly",
        "units": units,
        "value": value,
        "release_lag_days": None,
        "coverage_status": "actual",
        "missing_fields_json": _metadata_json(metadata or {}),
        "collected_at": collected_at,
        "error_msg": None,
    }


def parse_cnn_fear_greed_graphdata(payload: dict[str, Any], *, collected_at: str | None = None) -> list[dict[str, Any]]:
    """Normalize CNN Fear & Greed graphdata JSON into macro observation rows."""
    collected = collected_at or _utc_now_string()
    rows: list[dict[str, Any]] = []

    historical = payload.get("fear_and_greed_historical")
    if isinstance(historical, dict):
        for item in historical.get("data") or []:
            if not isinstance(item, dict):
                continue
            observation_date = _epoch_ms_date(item.get("x"))
            score = _optional_float(item.get("y") if item.get("y") is not None else item.get("score"))
            if observation_date is None or score is None:
                continue
            rows.append(
                _sentiment_row(
                    "CNN_FEAR_GREED",
                    observation_date=observation_date,
                    source="cnn_fear_greed",
                    source_mode="json",
                    source_ref=CNN_FEAR_GREED_PAGE,
                    series_name="CNN Fear & Greed Index",
                    category="sentiment_index",
                    units="score_0_100",
                    value=score,
                    collected_at=collected,
                    metadata={"rating": item.get("rating"), "payload": "historical"},
                )
            )

    current = payload.get("fear_and_greed")
    if isinstance(current, dict):
        observation_date = _date_string(current.get("timestamp"))
        score = _optional_float(current.get("score"))
        if observation_date is not None and score is not None:
            rows.append(
                _sentiment_row(
                    "CNN_FEAR_GREED",
                    observation_date=observation_date,
                    source="cnn_fear_greed",
                    source_mode="json",
                    source_ref=CNN_FEAR_GREED_PAGE,
                    series_name="CNN Fear & Greed Index",
                    category="sentiment_index",
                    units="score_0_100",
                    value=score,
                    collected_at=collected,
                    metadata={
                        "rating": current.get("rating"),
                        "previous_close": current.get("previous_close"),
                        "previous_1_week": current.get("previous_1_week"),
                        "previous_1_month": current.get("previous_1_month"),
                        "previous_1_year": current.get("previous_1_year"),
                        "payload": "current",
                    },
                )
            )

    for payload_key, (series_id, series_name) in CNN_COMPONENTS.items():
        item = payload.get(payload_key)
        if not isinstance(item, dict):
            continue
        observation_date = _epoch_ms_date(item.get("timestamp"))
        score = _optional_float(item.get("score"))
        if observation_date is None or score is None:
            continue
        rows.append(
            _sentiment_row(
                series_id,
                observation_date=observation_date,
                source="cnn_fear_greed",
                source_mode="json",
                source_ref=CNN_FEAR_GREED_PAGE,
                series_name=series_name,
                category="sentiment_component",
                units="score_0_100",
                value=score,
                collected_at=collected,
                metadata={"rating": item.get("rating"), "component_key": payload_key},
            )
        )

    return rows


def _aaii_report_date(value: str, *, current_year: int, last_month: int | None) -> tuple[str | None, int, int | None]:
    cleaned = " ".join(str(value or "").replace(",", "").split())
    parsed = pd.to_datetime(cleaned, errors="coerce")
    if not pd.isna(parsed) and re.search(r"\d{4}", cleaned):
        timestamp = pd.Timestamp(parsed)
        return timestamp.strftime("%Y-%m-%d"), int(timestamp.year), int(timestamp.month)

    match = re.match(r"^([A-Za-z]{3,9})\s+(\d{1,2})$", cleaned)
    if not match:
        return None, current_year, last_month
    month_text, day_text = match.groups()
    month = int(pd.Timestamp(f"2000 {month_text[:3]} 1").month)
    year = current_year
    if last_month is not None and month > last_month:
        year -= 1
    try:
        return date(year, month, int(day_text)).isoformat(), year, month
    except ValueError:
        return None, current_year, last_month


def parse_aaii_sentiment_frame(
    frame: pd.DataFrame,
    *,
    collected_at: str,
    source_mode: str,
    source_ref: str,
) -> list[dict[str, Any]]:
    """Normalize complete official AAII weekly rows without inventing missing responses."""
    required = ["Reported Date", "Bullish", "Neutral", "Bearish"]
    if not set(required).issubset(frame.columns):
        raise RuntimeError(f"AAII workbook is missing required columns: {required}")
    normalized = frame[required].copy()
    normalized["Reported Date"] = pd.to_datetime(
        normalized["Reported Date"],
        errors="coerce",
    )
    for column in required[1:]:
        normalized[column] = pd.to_numeric(normalized[column], errors="coerce")
    normalized = normalized.dropna(subset=required).sort_values("Reported Date")

    rows: list[dict[str, Any]] = []
    for item in normalized.to_dict("records"):
        observation_date = pd.Timestamp(item["Reported Date"]).strftime("%Y-%m-%d")
        bullish = round(float(item["Bullish"]) * 100.0, 4)
        neutral = round(float(item["Neutral"]) * 100.0, 4)
        bearish = round(float(item["Bearish"]) * 100.0, 4)
        values = {
            "bullish": bullish,
            "neutral": neutral,
            "bearish": bearish,
            "spread": round(bullish - bearish, 4),
        }
        metadata = {
            "reported_date": observation_date,
            "bullish_fraction": float(item["Bullish"]),
            "neutral_fraction": float(item["Neutral"]),
            "bearish_fraction": float(item["Bearish"]),
        }
        for key, value in values.items():
            series_id, series_name, units = AAII_SERIES[key]
            rows.append(
                _sentiment_row(
                    series_id,
                    observation_date=observation_date,
                    source="aaii_sentiment_survey",
                    source_mode=source_mode,
                    source_ref=source_ref,
                    series_name=series_name,
                    category="sentiment_survey",
                    units=units,
                    value=value,
                    collected_at=collected_at,
                    metadata=metadata,
                )
            )
    return rows


def parse_aaii_sentiment_rows_from_workbook(
    data: bytes,
    *,
    collected_at: str | None = None,
) -> list[dict[str, Any]]:
    """Read the official AAII SENTIMENT sheet and normalize complete weekly observations."""
    frame = pd.read_excel(BytesIO(data), sheet_name="SENTIMENT", header=3)
    return parse_aaii_sentiment_frame(
        frame,
        collected_at=collected_at or _utc_now_string(),
        source_mode="xls",
        source_ref=AAII_SENTIMENT_HISTORY_URL,
    )


def parse_aaii_sentiment_rows_from_html(
    html: str | bytes,
    *,
    collected_at: str | None = None,
    today: date | None = None,
) -> list[dict[str, Any]]:
    """Normalize the AAII official historical sentiment table into macro observation rows."""
    text = html.decode("utf-8", errors="replace") if isinstance(html, bytes) else str(html)
    soup = BeautifulSoup(text, "html.parser")
    collected = collected_at or _utc_now_string()
    today_value = today or date.today()

    target_table = None
    for table in soup.find_all("table"):
        headers = [cell.get_text(" ", strip=True).lower() for cell in table.find_all(["th", "td"])[:4]]
        if headers[:4] == ["reported date", "bullish", "neutral", "bearish"]:
            target_table = table
            break
    if target_table is None:
        return []

    rows: list[dict[str, Any]] = []
    current_year = today_value.year
    last_month: int | None = None
    for tr in target_table.find_all("tr")[1:]:
        cells = [cell.get_text(" ", strip=True) for cell in tr.find_all(["td", "th"])]
        if len(cells) < 4:
            continue
        raw_report_date = cells[0]
        parsed_date, current_year, last_month = _aaii_report_date(
            raw_report_date,
            current_year=current_year,
            last_month=last_month,
        )
        observation_date = (
            date.fromisoformat(parsed_date) + timedelta(days=1)
        ).isoformat() if parsed_date else None
        bullish = _optional_float(cells[1])
        neutral = _optional_float(cells[2])
        bearish = _optional_float(cells[3])
        if observation_date is None or bullish is None or neutral is None or bearish is None:
            continue
        values = {
            "bullish": bullish,
            "neutral": neutral,
            "bearish": bearish,
            "spread": round(bullish - bearish, 4),
        }
        metadata = {
            "bullish": bullish,
            "neutral": neutral,
            "bearish": bearish,
            "reported_date_raw": raw_report_date,
            "normalized_report_date": observation_date,
        }
        for key, value in values.items():
            series_id, series_name, units = AAII_SERIES[key]
            rows.append(
                _sentiment_row(
                    series_id,
                    observation_date=observation_date,
                    source="aaii_sentiment_survey",
                    source_mode="html",
                    source_ref=AAII_SENTIMENT_URL,
                    series_name=series_name,
                    category="sentiment_survey",
                    units=units,
                    value=value,
                    collected_at=collected,
                    metadata=metadata,
                )
            )

    return rows


def _fetch_bytes(
    url: str,
    *,
    headers: dict[str, str],
    timeout: int,
    retries: int,
    fetcher: Callable[[Request, int], bytes] | None = None,
    browser_impersonate: bool = False,
) -> bytes:
    request = Request(url, headers=headers)
    last_error: Exception | None = None
    attempts = max(int(retries), 1)
    for attempt in range(attempts):
        try:
            if fetcher is not None:
                return fetcher(request, int(timeout))
            if browser_impersonate:
                try:
                    from curl_cffi import requests as curl_requests
                except ImportError:
                    pass
                else:
                    response = curl_requests.get(
                        url,
                        headers=headers,
                        timeout=int(timeout),
                        impersonate="chrome",
                    )
                    if int(response.status_code) >= 400:
                        raise RuntimeError(f"HTTP {response.status_code}")
                    return bytes(response.content)
            with urlopen(request, timeout=int(timeout)) as response:
                return response.read()
        except (HTTPError, URLError, TimeoutError) as exc:
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(0.4 * (attempt + 1))
        except Exception as exc:
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(0.4 * (attempt + 1))
    if isinstance(last_error, HTTPError):
        raise RuntimeError(f"HTTP {last_error.code}") from last_error
    if isinstance(last_error, URLError):
        raise RuntimeError(f"fetch failed: {last_error.reason}") from last_error
    if isinstance(last_error, RuntimeError):
        raise last_error
    raise RuntimeError(f"fetch failed: {last_error}") from last_error


def fetch_cnn_fear_greed_rows(
    *,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
    fetcher: Callable[[Request, int], bytes] | None = None,
) -> list[dict[str, Any]]:
    data = _fetch_bytes(
        CNN_FEAR_GREED_URL,
        headers={
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "application/json,text/plain,*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": CNN_FEAR_GREED_PAGE,
        },
        timeout=timeout,
        retries=retries,
        fetcher=fetcher,
    )
    payload = json.loads(data.decode("utf-8"))
    return parse_cnn_fear_greed_graphdata(payload)


def fetch_aaii_sentiment_history_rows(
    *,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
    fetcher: Callable[[Request, int], bytes] | None = None,
) -> list[dict[str, Any]]:
    data = _fetch_bytes(
        AAII_SENTIMENT_HISTORY_URL,
        headers={
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "application/vnd.ms-excel,application/octet-stream,*/*",
            "Referer": AAII_SENTIMENT_URL,
        },
        timeout=timeout,
        retries=retries,
        fetcher=fetcher,
    )
    rows = parse_aaii_sentiment_rows_from_workbook(data)
    if not rows:
        raise RuntimeError("AAII official workbook contained no complete observations")
    return rows


def _latest_aaii_weeks(
    rows: list[dict[str, Any]],
    count: int,
) -> list[dict[str, Any]]:
    dates = sorted(
        {
            str(row.get("observation_date") or "")
            for row in rows
            if row.get("observation_date")
        }
    )
    allowed = set(dates[-max(int(count), 1):])
    return [
        row
        for row in rows
        if str(row.get("observation_date") or "") in allowed
    ]


def fetch_aaii_sentiment_rows(
    *,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
    today: date | None = None,
    fetcher: Callable[[Request, int], bytes] | None = None,
) -> list[dict[str, Any]]:
    try:
        history = fetch_aaii_sentiment_history_rows(
            timeout=timeout,
            retries=retries,
            fetcher=fetcher,
        )
        return _latest_aaii_weeks(history, AAII_DAILY_CAPTURE_WEEKS)
    except Exception as workbook_error:
        LOGGER.warning(
            "AAII workbook fetch failed; using official HTML fallback: %s",
            workbook_error,
        )

    data = _fetch_bytes(
        AAII_SENTIMENT_URL,
        headers={
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.aaii.com/sentimentsurvey",
        },
        timeout=timeout,
        retries=retries,
        fetcher=fetcher,
        browser_impersonate=True,
    )
    rows = parse_aaii_sentiment_rows_from_html(data, today=today)
    if not rows:
        text = data.decode("utf-8", errors="replace")
        if "Pardon Our Interruption" in text:
            raise RuntimeError("AAII official page returned an anti-bot interstitial")
        raise RuntimeError("AAII official sentiment table was not found in the response")
    return _latest_aaii_weeks(rows, AAII_DAILY_CAPTURE_WEEKS)


def _source_coverage(source: str, rows: list[dict[str, Any]]) -> tuple[str, dict[str, Any]]:
    expected = EXPECTED_SENTIMENT_SERIES[source]
    observed = {str(row.get("series_id") or "").upper() for row in rows}
    missing = sorted(expected - observed)
    return ("partial" if missing else "success"), {
        "expected": len(expected),
        "observed": len(expected & observed),
        "missing_series": missing,
    }


def _source_observed_at(rows: list[dict[str, Any]]) -> str:
    values = {str(row.get("collected_at") or "") for row in rows}
    if len(values) != 1 or "" in values:
        raise RuntimeError("One source response must have one collected_at")
    return values.pop()


def _record_source_failure_safely(db: MySQLClient, **values: Any) -> bool:
    try:
        record_market_sentiment_source_failure(db, **values)
    except Exception:
        LOGGER.exception("Failed to record sentiment source failure: %s", values.get("source"))
        return False
    return True


def collect_and_store_market_sentiment(
    *,
    include_cnn: bool = True,
    include_aaii: bool = True,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, Any]:
    """Collect CNN and AAII into source-isolated immutable and canonical stores."""
    source_fetchers: list[tuple[str, str, Callable[[], list[dict[str, Any]]]]] = []
    if include_cnn:
        source_fetchers.append(
            (
                "cnn_fear_greed",
                CNN_FEAR_GREED_PAGE,
                lambda: fetch_cnn_fear_greed_rows(timeout=timeout, retries=retries),
            )
        )
    if include_aaii:
        source_fetchers.append(
            (
                "aaii_sentiment_survey",
                AAII_SENTIMENT_URL,
                lambda: fetch_aaii_sentiment_rows(timeout=timeout, retries=retries),
            )
        )

    collection_id = str(uuid4())
    failed: list[dict[str, str]] = []
    missing: list[str] = []
    source_row_counts: dict[str, int] = {}
    batch_ids: dict[str, str] = {}
    snapshot_rows_stored = 0
    canonical_rows_stored = 0
    stored_rows: list[dict[str, Any]] = []

    db = MySQLClient(host, user, password, port)
    try:
        ensure_market_sentiment_schema(db)
        for source, source_ref, fetch_rows in source_fetchers:
            batch_id = str(uuid4())
            requested_at = _utc_now_string()
            try:
                source_rows = fetch_rows()
                source_row_counts[source] = len(source_rows)
                if not source_rows:
                    missing.append(source)
                    if _record_source_failure_safely(
                        db,
                        collection_id=collection_id,
                        batch_id=batch_id,
                        source=source,
                        source_ref=source_ref,
                        requested_at=requested_at,
                        completed_at=_utc_now_string(),
                        status="missing",
                        error_msg="Source returned no normalized observations",
                    ):
                        batch_ids[source] = batch_id
                    continue

                status, source_coverage = _source_coverage(source, source_rows)
                saved = persist_market_sentiment_source_capture(
                    db,
                    collection_id=collection_id,
                    batch_id=batch_id,
                    source=source,
                    source_ref=source_ref,
                    requested_at=requested_at,
                    observed_at=_source_observed_at(source_rows),
                    completed_at=_utc_now_string(),
                    status=status,
                    coverage=source_coverage,
                    rows=source_rows,
                )
                batch_ids[source] = batch_id
                snapshot_rows_stored += int(saved["snapshot_rows_written"])
                canonical_rows_stored += int(saved["canonical_rows_written"])
                stored_rows.extend(source_rows)
            except Exception as exc:
                reason = str(exc)[:500]
                failed.append({"source": source, "reason": reason})
                source_row_counts[source] = 0
                LOGGER.warning("Market sentiment fetch/store failed for %s: %s", source, exc)
                if _record_source_failure_safely(
                    db,
                    collection_id=collection_id,
                    batch_id=batch_id,
                    source=source,
                    source_ref=source_ref,
                    requested_at=requested_at,
                    completed_at=_utc_now_string(),
                    status="error",
                    error_msg=reason,
                ):
                    batch_ids[source] = batch_id
    finally:
        db.close()

    coverage: dict[str, int] = {}
    for row in stored_rows:
        status = str(row.get("coverage_status") or "missing")
        coverage[status] = coverage.get(status, 0) + 1

    return {
        "requested": len(source_fetchers),
        "stored": canonical_rows_stored,
        "updated": None,
        "missing": missing,
        "failed": failed,
        "coverage": coverage,
        "sources": [source for source, _, _ in source_fetchers],
        "source_row_counts": source_row_counts,
        "collection_id": collection_id,
        "batch_ids": batch_ids,
        "snapshot_rows_stored": snapshot_rows_stored,
        "canonical_rows_stored": canonical_rows_stored,
        "target_table": f"{DB_META}.{MACRO_TABLE}",
        "target_tables": [
            f"{DB_META}.{MACRO_TABLE}",
            f"{DB_META}.{MARKET_SENTIMENT_BATCH_TABLE}",
            f"{DB_META}.{MARKET_SENTIMENT_SNAPSHOT_TABLE}",
        ],
    }
