"""Source-neutral FRED/ALFRED vintage collection primitives."""

from __future__ import annotations

import json
import math
import time
from datetime import date, datetime, time as clock_time, timedelta, timezone
from typing import Any, Iterable, Iterator, Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


VINTAGE_TABLE = "macro_series_vintage_observation"
FRED_API_URL = "https://api.stlouisfed.org/fred/series/observations"
FRED_VINTAGE_DATES_URL = "https://api.stlouisfed.org/fred/series/vintagedates"
EARLIEST_REALTIME_DATE = "1776-07-04"
OPEN_ENDED_REALTIME_DATE = "9999-12-31"
FRED_SOURCE_MODE = "fred_output_type_1_realtime_intervals"
MAX_VINTAGE_DATES_PER_REQUEST = 2_000
SAFE_VINTAGE_DATES_PER_WINDOW = MAX_VINTAGE_DATES_PER_REQUEST - 1
MAX_VINTAGE_DATE_PAGE_SIZE = 10_000
DEFAULT_OBSERVATION_PAGE_SIZE = 50_000
VINTAGE_UPSERT_MAX_STATEMENT_LENGTH = 16 * 1024 * 1024
DEFAULT_TIMEOUT = 60
DEFAULT_RETRIES = 3

RELEASE_POLICIES = {
    "OFFICIAL_0830_ET": clock_time(8, 30),
    "OFFICIAL_1000_ET": clock_time(10, 0),
    "END_OF_DAY_ET": clock_time(23, 59, 59, 999999),
}


class FredVintageError(RuntimeError):
    """Raised when the vintage source contract cannot be satisfied safely."""


def _date_text(value: object, *, field: str) -> str:
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    text = str(value or "").strip()
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError as exc:
        raise FredVintageError(f"Invalid {field}: {value!r}") from exc


def _collected_at_text(value: datetime | str) -> str:
    if isinstance(value, datetime):
        normalized = value
        if normalized.tzinfo is not None:
            normalized = normalized.astimezone(timezone.utc).replace(tzinfo=None)
        return normalized.strftime("%Y-%m-%d %H:%M:%S")
    text = str(value).strip()
    if not text:
        raise FredVintageError("collected_at is required")
    return text


def _db_datetime_text(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        parsed = value
    else:
        text = str(value).strip()
        if not text:
            return None
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError as exc:
            raise FredVintageError(f"Invalid released_at: {value!r}") from exc
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed.strftime("%Y-%m-%d %H:%M:%S.%f")


def _parse_value(value: object) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if text in {"", ".", "-", "--", "NA", "N/A", "None", "nan"}:
        return None
    try:
        parsed = float(text.replace(",", ""))
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def _safe_fetch_error(exc: Exception) -> str:
    """Describe provider failures without exposing credentials in request URLs."""

    if isinstance(exc, HTTPError):
        return f"HTTP {exc.code}"
    if isinstance(exc, URLError):
        return "URL error"
    return type(exc).__name__


def _urllib_json(
    endpoint: str,
    params: dict[str, object],
    *,
    timeout: int,
    retries: int,
) -> dict[str, Any]:
    url = f"{endpoint}?{urlencode(params)}"
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "quant-data-pipeline/fred-vintages-v1",
        },
    )
    last_error: Exception | None = None
    for attempt in range(max(1, int(retries))):
        try:
            with urlopen(request, timeout=int(timeout)) as response:
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt + 1 < max(1, int(retries)):
                time.sleep(0.4 * (attempt + 1))
    detail = _safe_fetch_error(last_error) if last_error is not None else "unknown error"
    raise FredVintageError(f"FRED vintage fetch failed: {detail}") from None


def _request_json(
    endpoint: str,
    params: dict[str, object],
    *,
    session: Any,
    timeout: int,
    retries: int,
) -> dict[str, Any]:
    if session is None:
        payload = _urllib_json(
            endpoint,
            params,
            timeout=int(timeout),
            retries=int(retries),
        )
    else:
        last_error: Exception | None = None
        last_status: object | None = None
        attempts = max(1, int(retries))
        for attempt in range(attempts):
            response: Any = None
            try:
                response = session.get(
                    endpoint,
                    params=params,
                    timeout=int(timeout),
                )
                response.raise_for_status()
                payload = response.json()
                break
            except Exception as exc:
                last_error = exc
                last_status = getattr(response, "status_code", None)
                if attempt + 1 < attempts:
                    time.sleep(0.4 * (attempt + 1))
        else:
            detail = (
                f"HTTP {last_status}"
                if last_status is not None
                else type(last_error).__name__
            )
            raise FredVintageError(f"FRED vintage fetch failed: {detail}") from None
    if not isinstance(payload, dict):
        raise FredVintageError("FRED response must be a JSON object")
    if payload.get("error_code") is not None:
        raise FredVintageError(
            f"FRED API error {payload.get('error_code')}: {payload.get('error_message')}"
        )
    return payload


def resolve_released_at(realtime_start: str, *, release_policy: str) -> str:
    """Resolve a FRED vintage date to a conservative, explicit UTC release time."""

    policy = str(release_policy or "").strip().upper()
    release_clock = RELEASE_POLICIES.get(policy)
    if release_clock is None:
        raise FredVintageError(f"Unknown release policy: {release_policy!r}")
    local_release = datetime.combine(
        date.fromisoformat(_date_text(realtime_start, field="realtime_start")),
        release_clock,
        tzinfo=ZoneInfo("America/New_York"),
    )
    return local_release.astimezone(timezone.utc).isoformat()


def fetch_fred_vintage_dates(
    series_id: str,
    *,
    api_key: str,
    session: Any = None,
    realtime_start: str = EARLIEST_REALTIME_DATE,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
) -> list[str]:
    """Return official release/revision dates used to partition ALFRED queries."""

    normalized_series = str(series_id or "").strip().upper()
    normalized_key = str(api_key or "").strip()
    resolved_realtime_start = _date_text(realtime_start, field="realtime_start")
    if not normalized_series:
        raise FredVintageError("series_id is required")
    if not normalized_key:
        raise FredVintageError("FRED_API_KEY is required for vintage data")

    offset = 0
    vintage_dates: list[str] = []
    while True:
        params: dict[str, object] = {
            "series_id": normalized_series,
            "api_key": normalized_key,
            "file_type": "json",
            "sort_order": "asc",
            "realtime_start": resolved_realtime_start,
            "realtime_end": OPEN_ENDED_REALTIME_DATE,
            "limit": MAX_VINTAGE_DATE_PAGE_SIZE,
            "offset": offset,
        }
        payload = _request_json(
            FRED_VINTAGE_DATES_URL,
            params,
            session=session,
            timeout=int(timeout),
            retries=int(retries),
        )
        items = payload.get("vintage_dates")
        if not isinstance(items, list):
            raise FredVintageError(
                "FRED vintage-date response has no vintage_dates list"
            )
        vintage_dates.extend(_date_text(item, field="vintage date") for item in items)
        count = int(payload.get("count") or len(vintage_dates))
        offset += len(items)
        if not items or offset >= count:
            break
    return sorted(set(vintage_dates))


def build_realtime_windows(
    vintage_dates: Sequence[str] | Iterable[str],
    *,
    lower_bound: str | None = None,
    chunk_size: int = MAX_VINTAGE_DATES_PER_REQUEST,
) -> list[tuple[str, str]]:
    """Split ALFRED requests without exceeding the vintage-date limit."""

    if int(chunk_size) < 1 or int(chunk_size) > MAX_VINTAGE_DATES_PER_REQUEST:
        raise FredVintageError(
            f"chunk_size must be between 1 and {MAX_VINTAGE_DATES_PER_REQUEST}"
        )
    # FRED can count one additional internal vintage inside an otherwise exact
    # 2,000-date boundary. Leave one slot so the API's inclusive count stays safe.
    window_size = min(int(chunk_size), SAFE_VINTAGE_DATES_PER_WINDOW)
    resolved_lower_bound = _date_text(
        lower_bound or EARLIEST_REALTIME_DATE,
        field="lower_bound",
    )
    normalized_dates = sorted(
        {
            normalized
            for item in vintage_dates
            if (normalized := _date_text(item, field="vintage date"))
            >= resolved_lower_bound
        }
    )
    if not normalized_dates:
        return [(resolved_lower_bound, OPEN_ENDED_REALTIME_DATE)]

    windows: list[tuple[str, str]] = []
    for index in range(0, len(normalized_dates), window_size):
        realtime_start = (
            resolved_lower_bound if index == 0 else normalized_dates[index]
        )
        next_index = index + window_size
        realtime_end = (
            (
                date.fromisoformat(normalized_dates[next_index])
                - timedelta(days=1)
            ).isoformat()
            if next_index < len(normalized_dates)
            else OPEN_ENDED_REALTIME_DATE
        )
        windows.append((realtime_start, realtime_end))
    return windows


def iter_fred_vintage_pages(
    series_id: str,
    *,
    api_key: str,
    session: Any = None,
    realtime_start: str = EARLIEST_REALTIME_DATE,
    page_size: int = DEFAULT_OBSERVATION_PAGE_SIZE,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
) -> Iterator[list[dict[str, object]]]:
    """Yield long-form real-time observation pages for one series."""

    normalized_series = str(series_id or "").strip().upper()
    normalized_key = str(api_key or "").strip()
    resolved_realtime_start = _date_text(realtime_start, field="realtime_start")
    if not normalized_series:
        raise FredVintageError("series_id is required")
    if not normalized_key:
        raise FredVintageError("FRED_API_KEY is required for vintage data")

    vintage_dates = fetch_fred_vintage_dates(
        normalized_series,
        api_key=normalized_key,
        session=session,
        realtime_start=resolved_realtime_start,
        timeout=int(timeout),
        retries=int(retries),
    )
    limit = max(1, min(int(page_size), 100_000))
    for window_start, realtime_end in build_realtime_windows(
        vintage_dates,
        lower_bound=resolved_realtime_start,
    ):
        offset = 0
        while True:
            params: dict[str, object] = {
                "series_id": normalized_series,
                "api_key": normalized_key,
                "file_type": "json",
                "output_type": 1,
                "sort_order": "asc",
                "realtime_start": window_start,
                "realtime_end": realtime_end,
                "limit": limit,
                "offset": offset,
            }
            payload = _request_json(
                FRED_API_URL,
                params,
                session=session,
                timeout=int(timeout),
                retries=int(retries),
            )
            observations = payload.get("observations")
            if not isinstance(observations, list):
                raise FredVintageError(
                    "FRED vintage response has no observations list"
                )
            page = [item for item in observations if isinstance(item, dict)]
            if page:
                yield page
            count = int(payload.get("count") or (offset + len(observations)))
            offset += len(observations)
            if not observations or offset >= count:
                break


def fetch_fred_vintages(
    series_id: str,
    *,
    api_key: str,
    session: Any = None,
    realtime_start: str = EARLIEST_REALTIME_DATE,
    limit: int = 100_000,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
) -> list[dict[str, object]]:
    """Fetch every real-time version for one series with deterministic pagination."""

    rows: list[dict[str, object]] = []
    for page in iter_fred_vintage_pages(
        series_id,
        api_key=api_key,
        session=session,
        realtime_start=realtime_start,
        page_size=int(limit),
        timeout=int(timeout),
        retries=int(retries),
    ):
        rows.extend(page)
    return sorted(
        rows,
        key=lambda item: (
            str(item.get("date") or ""),
            str(item.get("realtime_start") or ""),
            str(item.get("realtime_end") or ""),
        ),
    )


def normalize_fred_vintage_rows(
    spec: object,
    payload_rows: Iterable[Mapping[str, object]],
    *,
    collected_at: datetime | str,
) -> list[dict[str, object]]:
    """Normalize source rows while keeping release and revision identities separate."""

    series_id = str(getattr(spec, "series_id", "") or "").strip().upper()
    factor_group = str(
        getattr(spec, "group", None) or getattr(spec, "factor", None) or ""
    ).strip()
    frequency = str(getattr(spec, "frequency", "") or "").strip() or None
    release_policy = str(getattr(spec, "release_policy", "") or "").strip()
    release_anchor = str(
        getattr(spec, "release_anchor", "realtime_start") or "realtime_start"
    ).strip()
    if release_anchor not in {"realtime_start", "observation_date"}:
        raise FredVintageError(f"Unknown release_anchor: {release_anchor!r}")
    if not series_id or not factor_group:
        raise FredVintageError("spec must define series_id and group/factor")

    collected_text = _collected_at_text(collected_at)
    normalized: list[dict[str, object]] = []
    for item in payload_rows:
        observation_date = _date_text(item.get("date"), field="observation date")
        realtime_start = _date_text(
            item.get("realtime_start"), field="realtime_start"
        )
        realtime_end = _date_text(
            item.get("realtime_end") or OPEN_ENDED_REALTIME_DATE,
            field="realtime_end",
        )
        value = _parse_value(item.get("value"))
        release_date = (
            observation_date
            if release_anchor == "observation_date"
            else realtime_start
        )
        release_lag_days = (
            date.fromisoformat(release_date) - date.fromisoformat(observation_date)
        ).days
        missing_fields = ["value"] if value is None else []
        negative_lag = release_lag_days < 0
        coverage_status = (
            "missing" if missing_fields else "partial" if negative_lag else "actual"
        )
        normalized.append(
            {
                "series_id": series_id,
                "observation_date": observation_date,
                "realtime_start": realtime_start,
                "realtime_end": realtime_end,
                "released_at": (
                    resolve_released_at(
                        release_date,
                        release_policy=release_policy,
                    )
                    if release_policy
                    else None
                ),
                "source": "fred",
                "source_type": "official",
                "source_mode": FRED_SOURCE_MODE,
                "source_ref": f"https://fred.stlouisfed.org/series/{series_id}",
                "series_name": series_id,
                "factor_group": factor_group,
                "frequency": frequency,
                "units": None,
                "value": value,
                "release_lag_days": release_lag_days,
                "coverage_status": coverage_status,
                "missing_fields_json": json.dumps(
                    missing_fields,
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                "collected_at": collected_text,
                "error_msg": "negative_release_lag" if negative_lag else None,
            }
        )
    return sorted(
        normalized,
        key=lambda row: (
            str(row["series_id"]),
            str(row["observation_date"]),
            str(row["realtime_start"]),
        ),
    )


def upsert_fred_vintage_rows(
    rows: Sequence[Mapping[str, object]],
    *,
    db: object,
) -> int:
    """Idempotently store normalized versions by the shared vintage business key."""

    if not rows:
        return 0
    prepared = [
        dict(row, released_at=_db_datetime_text(row.get("released_at")))
        for row in rows
    ]
    sql = f"""
    INSERT INTO {VINTAGE_TABLE} (
      series_id, observation_date, realtime_start, realtime_end, released_at,
      source, source_type, source_mode, source_ref,
      series_name, factor_group, frequency, units, value, release_lag_days,
      coverage_status, missing_fields_json, collected_at, error_msg
    ) VALUES (
      %(series_id)s, %(observation_date)s, %(realtime_start)s, %(realtime_end)s, %(released_at)s,
      %(source)s, %(source_type)s, %(source_mode)s, %(source_ref)s,
      %(series_name)s, %(factor_group)s, %(frequency)s, %(units)s, %(value)s, %(release_lag_days)s,
      %(coverage_status)s, %(missing_fields_json)s, %(collected_at)s, %(error_msg)s
    )
    ON DUPLICATE KEY UPDATE
      realtime_end = VALUES(realtime_end), released_at = VALUES(released_at),
      source_type = VALUES(source_type), source_mode = VALUES(source_mode),
      source_ref = VALUES(source_ref), series_name = VALUES(series_name),
      factor_group = VALUES(factor_group), frequency = VALUES(frequency),
      units = VALUES(units), value = VALUES(value),
      release_lag_days = VALUES(release_lag_days),
      coverage_status = VALUES(coverage_status),
      missing_fields_json = VALUES(missing_fields_json),
      collected_at = VALUES(collected_at), error_msg = VALUES(error_msg)
    """
    raw_connection = getattr(db, "conn", None)
    if raw_connection is None:
        db.executemany(sql, prepared)
    else:
        with raw_connection.cursor() as cursor:
            if hasattr(cursor, "max_stmt_length"):
                cursor.max_stmt_length = VINTAGE_UPSERT_MAX_STATEMENT_LENGTH
            cursor.executemany(sql, prepared)
    return len(prepared)


def load_latest_vintage_realtime_starts(
    series_ids: Iterable[str],
    *,
    db: object,
) -> dict[str, str]:
    """Read each requested series' latest stored revision boundary."""

    requested = tuple(
        dict.fromkeys(str(item or "").strip().upper() for item in series_ids)
    )
    if not requested or any(not item for item in requested):
        raise FredVintageError("At least one non-empty series_id is required")
    placeholders = ",".join(["%s"] * len(requested))
    sql = f"""
    SELECT series_id, MAX(realtime_start) AS latest_realtime_start
    FROM {VINTAGE_TABLE}
    WHERE series_id IN ({placeholders})
    GROUP BY series_id
    """
    rows = db.query(sql, requested)
    return {
        str(row["series_id"]).strip().upper(): _date_text(
            row["latest_realtime_start"],
            field="latest_realtime_start",
        )
        for row in rows
        if row.get("series_id") and row.get("latest_realtime_start")
    }
