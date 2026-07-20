from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

import pandas as pd

from finance.data.db.mysql import MySQLClient
from finance.data.sentiment_store import (
    DB_META,
    MARKET_SENTIMENT_BATCH_TABLE,
    MARKET_SENTIMENT_SNAPSHOT_TABLE,
)

from .macro import load_macro_series_observations, load_macro_snapshot


CORE_SENTIMENT_SERIES = (
    "CNN_FEAR_GREED",
    "AAII_BULLISH",
    "AAII_NEUTRAL",
    "AAII_BEARISH",
    "AAII_BULL_BEAR_SPREAD",
)
CNN_COMPONENT_SERIES = (
    "CNN_FNG_MARKET_MOMENTUM_SP500",
    "CNN_FNG_STOCK_PRICE_STRENGTH",
    "CNN_FNG_STOCK_PRICE_BREADTH",
    "CNN_FNG_PUT_CALL_OPTIONS",
    "CNN_FNG_MARKET_VOLATILITY_VIX",
    "CNN_FNG_JUNK_BOND_DEMAND",
    "CNN_FNG_SAFE_HAVEN_DEMAND",
)
DEFAULT_SENTIMENT_SERIES = CORE_SENTIMENT_SERIES + CNN_COMPONENT_SERIES
QueryFn = Callable[[str, str, tuple[Any, ...]], list[dict[str, Any]]]
PIT_COLUMNS = [
    "id",
    "batch_id",
    "collection_id",
    "series_id",
    "observation_date",
    "source",
    "source_type",
    "source_mode",
    "source_ref",
    "series_name",
    "category",
    "frequency",
    "units",
    "value",
    "release_lag_days",
    "coverage_status",
    "missing_fields_json",
    "observed_at",
    "error_msg",
]


def load_market_sentiment_snapshot(
    series_ids: str | Iterable[str] | None = None,
    *,
    as_of_date: str | None = None,
    max_staleness_days: int = 14,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> pd.DataFrame:
    """Load latest DB-backed CNN / AAII sentiment rows for Overview."""
    return load_macro_snapshot(
        series_ids=series_ids or DEFAULT_SENTIMENT_SERIES,
        as_of_date=as_of_date,
        max_staleness_days=max_staleness_days,
        host=host,
        user=user,
        password=password,
        port=port,
    )


def load_market_sentiment_history(
    series_ids: str | Iterable[str] | None = None,
    *,
    start: str | None = None,
    end: str | None = None,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> pd.DataFrame:
    """Load stored CNN / AAII sentiment history for charts and tables."""
    return load_macro_series_observations(
        series_ids=series_ids or DEFAULT_SENTIMENT_SERIES,
        start=start,
        end=end,
        host=host,
        user=user,
        password=password,
        port=port,
    )


def _query_sentiment(
    sql: str,
    params: tuple[Any, ...],
    *,
    query_fn: QueryFn | None,
) -> list[dict[str, Any]]:
    if query_fn is not None:
        return list(query_fn(DB_META, sql, params))
    db = MySQLClient("localhost", "root", "1234", 3306)
    try:
        db.use_db(DB_META)
        return db.query(sql, params)
    except Exception as exc:
        message = str(exc).lower()
        if "market_sentiment_" in message and (
            "doesn't exist" in message or "unknown table" in message
        ):
            return []
        raise
    finally:
        db.close()


def _known_at_utc(value: str | pd.Timestamp) -> pd.Timestamp:
    known_at = pd.Timestamp(value)
    if pd.isna(known_at):
        raise ValueError("known_at must be a valid timestamp")
    if known_at.tzinfo is None:
        return known_at.tz_localize("UTC")
    return known_at.tz_convert("UTC")


def load_market_sentiment_as_known(
    *,
    known_at: str | pd.Timestamp,
    series_ids: str | Iterable[str] | None = None,
    observation_start: str | None = None,
    observation_end: str | None = None,
    query_fn: QueryFn | None = None,
) -> pd.DataFrame:
    """Return the latest source version that the app knew by one UTC cutoff."""
    known_at_utc = _known_at_utc(known_at)
    known_at_mysql = known_at_utc.tz_localize(None).to_pydatetime()
    end_date = observation_end or known_at_utc.date().isoformat()
    predicates = ["observed_at <= %s", "observation_date <= %s"]
    params: list[Any] = [known_at_mysql, end_date]

    if observation_start:
        predicates.append("observation_date >= %s")
        params.append(observation_start)
    if series_ids is not None:
        requested = (series_ids,) if isinstance(series_ids, str) else tuple(series_ids)
        normalized = tuple(
            dict.fromkeys(str(series_id or "").strip().upper() for series_id in requested)
        )
        if not normalized or any(not series_id for series_id in normalized):
            raise ValueError("series_ids must contain at least one non-empty value")
        placeholders = ",".join(["%s"] * len(normalized))
        predicates.append(f"series_id IN ({placeholders})")
        params.extend(normalized)

    where_clause = "\n        AND ".join(predicates)
    sql = f"""
    WITH eligible_versions AS (
      SELECT snapshot_rows.*,
             ROW_NUMBER() OVER (
               PARTITION BY series_id, observation_date, source
               ORDER BY observed_at DESC, id DESC
             ) AS version_rank
      FROM {MARKET_SENTIMENT_SNAPSHOT_TABLE} snapshot_rows
      WHERE {where_clause}
    )
    SELECT id, batch_id, collection_id, series_id, observation_date, source,
           source_type, source_mode, source_ref, series_name, category, frequency,
           units, value, release_lag_days, coverage_status, missing_fields_json,
           observed_at, error_msg
    FROM eligible_versions
    WHERE version_rank = 1
    ORDER BY series_id, observation_date, source
    """
    raw_rows = _query_sentiment(sql, tuple(params), query_fn=query_fn)
    if not raw_rows:
        return pd.DataFrame(columns=PIT_COLUMNS)

    frame = pd.DataFrame(raw_rows)
    for column in PIT_COLUMNS:
        if column not in frame:
            frame[column] = None
    frame["series_id"] = frame["series_id"].fillna("").astype(str).str.upper()
    frame["observation_date"] = pd.to_datetime(frame["observation_date"], errors="coerce")
    frame["observed_at"] = pd.to_datetime(frame["observed_at"], errors="coerce", utc=True)
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")

    start_value = pd.Timestamp(observation_start) if observation_start else None
    end_value = pd.Timestamp(end_date)
    eligible = frame[frame["observed_at"].notna() & (frame["observed_at"] <= known_at_utc)]
    eligible = eligible[
        eligible["observation_date"].notna() & (eligible["observation_date"] <= end_value)
    ]
    if start_value is not None:
        eligible = eligible[eligible["observation_date"] >= start_value]
    if series_ids is not None:
        eligible = eligible[eligible["series_id"].isin(normalized)]
    if eligible.empty:
        return pd.DataFrame(columns=PIT_COLUMNS)

    eligible = eligible.sort_values(
        ["series_id", "observation_date", "source", "observed_at", "id"],
        kind="stable",
    )
    eligible = eligible.drop_duplicates(
        subset=["series_id", "observation_date", "source"], keep="last"
    )
    return eligible[PIT_COLUMNS].sort_values(
        ["series_id", "observation_date", "source"], kind="stable"
    ).reset_index(drop=True)


def load_market_sentiment_capture_summary(
    *, query_fn: QueryFn | None = None
) -> dict[str, dict[str, Any]]:
    """Summarize successful immutable capture coverage for each source."""
    sql = f"""
    SELECT source, MIN(observed_at) AS pit_start_at,
           MAX(observed_at) AS latest_capture_at, COUNT(*) AS capture_count
    FROM {MARKET_SENTIMENT_BATCH_TABLE}
    WHERE status IN ('success','partial') AND observed_at IS NOT NULL
    GROUP BY source ORDER BY source
    """
    rows = _query_sentiment(sql, (), query_fn=query_fn)
    summary: dict[str, dict[str, Any]] = {}
    for raw in rows:
        source = str(raw.get("source") or "").strip()
        if not source:
            continue
        values: dict[str, Any] = {}
        for key in ("pit_start_at", "latest_capture_at"):
            parsed = pd.to_datetime(raw.get(key), errors="coerce")
            values[key] = None if pd.isna(parsed) else pd.Timestamp(parsed).strftime("%Y-%m-%d %H:%M:%S")
        values["capture_count"] = int(raw.get("capture_count") or 0)
        summary[source] = values
    return summary
