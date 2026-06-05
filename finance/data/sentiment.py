from __future__ import annotations

import json
import logging
import re
import time
from collections.abc import Callable
from datetime import date, datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
import pandas as pd

from .db.mysql import MySQLClient
from .macro import DB_META, MACRO_TABLE, ensure_macro_series_schema


LOGGER = logging.getLogger(__name__)

CNN_FEAR_GREED_URL = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
CNN_FEAR_GREED_PAGE = "https://www.cnn.com/markets/fear-and-greed"
AAII_SENTIMENT_URL = "https://www.aaii.com/sentimentsurvey/sent_results"
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
        observation_date, current_year, last_month = _aaii_report_date(
            cells[0],
            current_year=current_year,
            last_month=last_month,
        )
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
        metadata = {"bullish": bullish, "neutral": neutral, "bearish": bearish, "reported_date": cells[0]}
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


def fetch_aaii_sentiment_rows(
    *,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
    today: date | None = None,
    fetcher: Callable[[Request, int], bytes] | None = None,
) -> list[dict[str, Any]]:
    data = _fetch_bytes(
        AAII_SENTIMENT_URL,
        headers={
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.aaii.com/sentimentsurvey",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        },
        timeout=timeout,
        retries=retries,
        fetcher=fetcher,
        browser_impersonate=True,
    )
    rows = parse_aaii_sentiment_rows_from_html(data, today=today)
    if not rows:
        text = data.decode("utf-8", errors="replace") if isinstance(data, bytes) else str(data)
        if "Pardon Our Interruption" in text:
            raise RuntimeError("AAII official page returned an anti-bot interstitial")
        raise RuntimeError("AAII official sentiment table was not found in the response")
    return rows


def _upsert_sentiment_rows(db: MySQLClient, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    sql = f"""
    INSERT INTO {MACRO_TABLE} (
      series_id, observation_date, source, source_type, source_mode, source_ref,
      series_name, category, frequency, units, value, release_lag_days,
      coverage_status, missing_fields_json, collected_at, error_msg
    ) VALUES (
      %(series_id)s, %(observation_date)s, %(source)s, %(source_type)s, %(source_mode)s, %(source_ref)s,
      %(series_name)s, %(category)s, %(frequency)s, %(units)s, %(value)s, %(release_lag_days)s,
      %(coverage_status)s, %(missing_fields_json)s, %(collected_at)s, %(error_msg)s
    )
    ON DUPLICATE KEY UPDATE
      source_type = VALUES(source_type),
      source_mode = VALUES(source_mode),
      source_ref = VALUES(source_ref),
      series_name = VALUES(series_name),
      category = VALUES(category),
      frequency = VALUES(frequency),
      units = VALUES(units),
      value = VALUES(value),
      release_lag_days = VALUES(release_lag_days),
      coverage_status = VALUES(coverage_status),
      missing_fields_json = VALUES(missing_fields_json),
      collected_at = VALUES(collected_at),
      error_msg = VALUES(error_msg)
    """
    db.executemany(sql, rows)


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
    """Collect market sentiment context and UPSERT it into macro_series_observation."""
    source_fetchers: list[tuple[str, Callable[[], list[dict[str, Any]]]]] = []
    if include_cnn:
        source_fetchers.append(("cnn_fear_greed", lambda: fetch_cnn_fear_greed_rows(timeout=timeout, retries=retries)))
    if include_aaii:
        source_fetchers.append(("aaii_sentiment_survey", lambda: fetch_aaii_sentiment_rows(timeout=timeout, retries=retries)))

    rows: list[dict[str, Any]] = []
    failed: list[dict[str, str]] = []
    missing: list[str] = []
    source_row_counts: dict[str, int] = {}
    for source, fetch_rows in source_fetchers:
        try:
            source_rows = fetch_rows()
            if source_rows:
                rows.extend(source_rows)
                source_row_counts[source] = len(source_rows)
            else:
                missing.append(source)
                source_row_counts[source] = 0
        except Exception as exc:
            failed.append({"source": source, "reason": str(exc)[:500]})
            source_row_counts[source] = 0
            LOGGER.warning("Market sentiment fetch failed for %s: %s", source, exc)

    ensure_macro_series_schema(host=host, user=user, password=password, port=port)
    db = MySQLClient(host, user, password, port)
    try:
        db.use_db(DB_META)
        _upsert_sentiment_rows(db, rows)
    finally:
        db.close()

    coverage: dict[str, int] = {}
    for row in rows:
        status = str(row.get("coverage_status") or "missing")
        coverage[status] = coverage.get(status, 0) + 1

    return {
        "requested": len(source_fetchers),
        "stored": len(rows),
        "updated": None,
        "missing": missing,
        "failed": failed,
        "coverage": coverage,
        "sources": [source for source, _ in source_fetchers],
        "source_row_counts": source_row_counts,
        "target_table": f"{DB_META}.{MACRO_TABLE}",
    }
