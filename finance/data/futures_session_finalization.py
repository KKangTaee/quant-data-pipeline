"""Build and persist completed futures sessions from stored intraday rows."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
import math
from typing import Any
from zoneinfo import ZoneInfo

from .db.mysql import MySQLClient
from .db.schema import FUTURES_MARKET_SCHEMAS, sync_table_schema


FUTURES_SESSION_FINALIZATION_BASIS = "yfinance_5m_session_aggregate_v1"
NEW_YORK = ZoneInfo("America/New_York")
DB_PRICE = "finance_price"


@dataclass(frozen=True)
class SessionFinalizationBatch:
    session_date: str
    window_start_utc: datetime
    window_end_utc: datetime
    rows: tuple[dict[str, object], ...]
    missing_symbols: tuple[str, ...]

    @property
    def complete(self) -> bool:
        return not self.missing_symbols


def _date_value(value: str | date) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value).strip())


def _utc_datetime(value: object) -> datetime | None:
    if isinstance(value, datetime):
        parsed = value
    else:
        text = str(value or "").strip()
        if not text:
            return None
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _finite_float(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def futures_session_window_utc(
    session_date: str | date,
) -> tuple[datetime, datetime]:
    """Return the completed futures session as a half-open UTC window."""

    session_day = _date_value(session_date)
    start_et = datetime.combine(
        session_day - timedelta(days=1),
        time(18, 0),
        tzinfo=NEW_YORK,
    )
    end_et = datetime.combine(
        session_day,
        time(17, 0),
        tzinfo=NEW_YORK,
    )
    return (
        start_et.astimezone(timezone.utc),
        end_et.astimezone(timezone.utc),
    )


def _first_finite(
    rows: Sequence[dict[str, Any]],
    field: str,
) -> float | None:
    for row in rows:
        value = _finite_float(row.get(field))
        if value is not None:
            return value
    return None


def _last_finite(
    rows: Sequence[dict[str, Any]],
    field: str,
) -> float | None:
    for row in reversed(rows):
        value = _finite_float(row.get(field))
        if value is not None:
            return value
    return None


def build_session_finalization_batch(
    intraday_rows: Sequence[dict[str, Any]],
    *,
    session_date: str | date,
    daily_targets: Mapping[str, object],
    required_symbols: Sequence[str],
    finalized_at: datetime,
) -> SessionFinalizationBatch:
    """Aggregate stored 5m rows without allowing the next evening session."""

    session_day = _date_value(session_date)
    start_utc, end_utc = futures_session_window_utc(session_day)
    start_et = start_utc.astimezone(NEW_YORK)
    end_et = end_utc.astimezone(NEW_YORK)
    source_ref = (
        f"yfinance:5m:[{start_et.isoformat()},{end_et.isoformat()})"
    )
    finalized_utc = _utc_datetime(finalized_at)
    if finalized_utc is None:
        raise ValueError("finalized_at must be a valid datetime")
    finalized_text = finalized_utc.replace(tzinfo=None).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    required = tuple(
        dict.fromkeys(
            str(symbol).strip().upper()
            for symbol in required_symbols
            if str(symbol).strip()
        )
    )
    targets = {
        str(symbol).strip().upper(): target
        for symbol, target in daily_targets.items()
        if str(symbol).strip()
    }
    grouped: dict[str, list[tuple[datetime, dict[str, Any]]]] = {
        symbol: [] for symbol in required
    }
    for raw in intraday_rows:
        row = dict(raw)
        symbol = str(row.get("provider_symbol") or "").strip().upper()
        if symbol not in grouped:
            continue
        timestamp = _utc_datetime(row.get("candle_time_utc"))
        if timestamp is None or timestamp < start_utc or timestamp >= end_utc:
            continue
        grouped[symbol].append((timestamp, row))

    aggregates: list[dict[str, object]] = []
    missing: list[str] = []
    for symbol in required:
        target = targets.get(symbol)
        timed_rows = sorted(grouped[symbol], key=lambda item: item[0])
        rows = [row for _, row in timed_rows]
        close = _last_finite(rows, "close")
        if target is None or not rows or close is None:
            missing.append(symbol)
            continue
        highs = [
            value
            for row in rows
            if (value := _finite_float(row.get("high"))) is not None
        ]
        lows = [
            value
            for row in rows
            if (value := _finite_float(row.get("low"))) is not None
        ]
        volumes = [
            value
            for row in rows
            if (value := _finite_float(row.get("volume"))) is not None
        ]
        aggregates.append(
            {
                "provider_symbol": symbol,
                "daily_candle_time_utc": target,
                "source": "yfinance",
                "final_open": _first_finite(rows, "open"),
                "final_high": max(highs) if highs else None,
                "final_low": min(lows) if lows else None,
                "final_close": close,
                "final_adj_close": close,
                "final_volume": sum(volumes) if volumes else None,
                "finalization_basis": FUTURES_SESSION_FINALIZATION_BASIS,
                "final_source_ref": source_ref,
                "finalized_at": finalized_text,
            }
        )

    return SessionFinalizationBatch(
        session_date=session_day.isoformat(),
        window_start_utc=start_utc,
        window_end_utc=end_utc,
        rows=tuple(aggregates),
        missing_symbols=tuple(missing),
    )


def _db(
    host: str,
    user: str,
    password: str,
    port: int,
) -> MySQLClient:
    return MySQLClient(
        host=host,
        user=user,
        password=password,
        port=port,
    )


def _normalized_symbols(symbols: Sequence[str]) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            str(symbol).strip().upper()
            for symbol in symbols
            if str(symbol).strip()
        )
    )


def load_latest_futures_daily_rows(
    symbols: Sequence[str],
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> list[dict[str, Any]]:
    """Load one latest raw daily row per symbol for finalization planning."""

    selected = _normalized_symbols(symbols)
    if not selected:
        return []
    placeholders = ", ".join(["%s"] * len(selected))
    db = _db(host, user, password, port)
    try:
        db.use_db(DB_PRICE)
        return db.query(
            f"""
            SELECT daily.provider_symbol, daily.candle_time_utc,
                   daily.collected_at,
                   daily.open, daily.high, daily.low, daily.close,
                   daily.adj_close, daily.volume,
                   daily.final_open, daily.final_high, daily.final_low,
                   daily.final_close, daily.final_adj_close,
                   daily.final_volume, daily.finalization_basis,
                   daily.final_source_ref, daily.finalized_at
            FROM futures_ohlcv AS daily
            INNER JOIN (
              SELECT provider_symbol, MAX(candle_time_utc) AS latest_candle
              FROM futures_ohlcv
              WHERE interval_code = %s
                AND source = %s
                AND provider_symbol IN ({placeholders})
              GROUP BY provider_symbol
            ) AS latest
              ON latest.provider_symbol = daily.provider_symbol
             AND latest.latest_candle = daily.candle_time_utc
            WHERE daily.interval_code = '1d'
              AND daily.source = 'yfinance'
            ORDER BY daily.provider_symbol
            """,
            ["1d", "yfinance", *selected],
        )
    finally:
        db.close()


def load_stored_futures_intraday_rows(
    symbols: Sequence[str],
    *,
    start_utc: datetime,
    end_utc: datetime,
    interval_code: str = "5m",
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> list[dict[str, Any]]:
    """Read stored intraday evidence for one exact half-open session."""

    selected = _normalized_symbols(symbols)
    if not selected:
        return []
    start = _utc_datetime(start_utc)
    end = _utc_datetime(end_utc)
    if start is None or end is None or start >= end:
        raise ValueError("start_utc must precede end_utc")
    placeholders = ", ".join(["%s"] * len(selected))
    db = _db(host, user, password, port)
    try:
        db.use_db(DB_PRICE)
        return db.query(
            f"""
            SELECT provider_symbol, candle_time_utc,
                   open, high, low, close, volume, collected_at
            FROM futures_ohlcv
            WHERE interval_code = %s
              AND source = %s
              AND provider_symbol IN ({placeholders})
              AND candle_time_utc >= %s
              AND candle_time_utc < %s
            ORDER BY provider_symbol, candle_time_utc
            """,
            [
                str(interval_code).strip(),
                "yfinance",
                *selected,
                start.replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S"),
                end.replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S"),
            ],
        )
    finally:
        db.close()


def write_futures_daily_finalization(
    batch: SessionFinalizationBatch,
    *,
    required_symbols: Sequence[str],
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> int:
    """Atomically attach one complete finalized session to raw daily rows."""

    required = _normalized_symbols(required_symbols)
    present = {
        str(row.get("provider_symbol") or "").strip().upper()
        for row in batch.rows
    }
    if (
        batch.missing_symbols
        or present != set(required)
        or len(batch.rows) != len(required)
    ):
        return 0
    db = _db(host, user, password, port)
    try:
        db.use_db(DB_PRICE)
        sync_table_schema(
            db,
            "futures_ohlcv",
            FUTURES_MARKET_SCHEMAS["futures_ohlcv"],
            DB_PRICE,
        )
        update_sql = """
        UPDATE futures_ohlcv
        SET final_open = %(final_open)s,
            final_high = %(final_high)s,
            final_low = %(final_low)s,
            final_close = %(final_close)s,
            final_adj_close = %(final_adj_close)s,
            final_volume = %(final_volume)s,
            finalization_basis = %(finalization_basis)s,
            final_source_ref = %(final_source_ref)s,
            finalized_at = %(finalized_at)s
        WHERE provider_symbol = %(provider_symbol)s
          AND interval_code = '1d'
          AND candle_time_utc = %(daily_candle_time_utc)s
          AND source = 'yfinance'
        """
        db.begin()
        try:
            db.executemany(update_sql, list(batch.rows))
            db.commit()
        except Exception:
            db.rollback()
            raise
        return len(batch.rows)
    finally:
        db.close()
