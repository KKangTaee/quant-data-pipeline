from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Sequence
from datetime import UTC, datetime
from time import sleep
from typing import Any
from uuid import uuid4

import pandas as pd
import yfinance as yf

from .db.mysql import MySQLClient
from .db.schema import FUTURES_MARKET_SCHEMAS, sync_table_schema


DB_META = "finance_meta"
DB_PRICE = "finance_price"
FUTURES_SOURCE = "yfinance"
DEFAULT_FUTURES_PERIOD = "1d"
DEFAULT_FUTURES_INTERVAL = "1m"
VALID_FUTURES_INTERVALS = {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d"}
MIN_1D_INTRADAY_ROWS_BEFORE_FALLBACK = 120

DEFAULT_FUTURES_INSTRUMENTS: tuple[dict[str, Any], ...] = (
    {"provider_symbol": "ES=F", "display_name": "E-mini S&P 500", "futures_group": "Equity Index", "exchange": "CME", "contract_hint": "S&P 500 index futures", "sort_order": 10},
    {"provider_symbol": "NQ=F", "display_name": "E-mini Nasdaq 100", "futures_group": "Equity Index", "exchange": "CME", "contract_hint": "Nasdaq 100 index futures", "sort_order": 20},
    {"provider_symbol": "YM=F", "display_name": "E-mini Dow", "futures_group": "Equity Index", "exchange": "CBOT", "contract_hint": "Dow Jones index futures", "sort_order": 30},
    {"provider_symbol": "RTY=F", "display_name": "E-mini Russell 2000", "futures_group": "Equity Index", "exchange": "CME", "contract_hint": "Russell 2000 index futures", "sort_order": 40},
    {"provider_symbol": "ZN=F", "display_name": "10Y Treasury Note", "futures_group": "Rates", "exchange": "CBOT", "contract_hint": "US 10-year Treasury note futures", "sort_order": 110},
    {"provider_symbol": "ZB=F", "display_name": "30Y Treasury Bond", "futures_group": "Rates", "exchange": "CBOT", "contract_hint": "US 30-year Treasury bond futures", "sort_order": 120},
    {"provider_symbol": "CL=F", "display_name": "WTI Crude Oil", "futures_group": "Commodities", "exchange": "NYMEX", "contract_hint": "WTI crude oil futures", "sort_order": 210},
    {"provider_symbol": "GC=F", "display_name": "Gold", "futures_group": "Commodities", "exchange": "COMEX", "contract_hint": "Gold futures", "sort_order": 220},
    {"provider_symbol": "SI=F", "display_name": "Silver", "futures_group": "Commodities", "exchange": "COMEX", "contract_hint": "Silver futures", "sort_order": 230},
    {"provider_symbol": "HG=F", "display_name": "Copper", "futures_group": "Commodities", "exchange": "COMEX", "contract_hint": "Copper futures", "sort_order": 240},
    {"provider_symbol": "NG=F", "display_name": "Natural Gas", "futures_group": "Commodities", "exchange": "NYMEX", "contract_hint": "Natural gas futures", "sort_order": 250},
    {"provider_symbol": "DX-Y.NYB", "display_name": "US Dollar Index", "futures_group": "FX Futures", "exchange": "ICE", "contract_hint": "US Dollar Index futures", "sort_order": 305},
    {"provider_symbol": "6E=F", "display_name": "Euro FX", "futures_group": "FX Futures", "exchange": "CME", "contract_hint": "EUR/USD futures", "sort_order": 310},
    {"provider_symbol": "6J=F", "display_name": "Japanese Yen", "futures_group": "FX Futures", "exchange": "CME", "contract_hint": "JPY/USD futures", "sort_order": 320},
    {"provider_symbol": "6B=F", "display_name": "British Pound", "futures_group": "FX Futures", "exchange": "CME", "contract_hint": "GBP/USD futures", "sort_order": 330},
    {"provider_symbol": "6A=F", "display_name": "Australian Dollar", "futures_group": "FX Futures", "exchange": "CME", "contract_hint": "AUD/USD futures", "sort_order": 340},
    {"provider_symbol": "6C=F", "display_name": "Canadian Dollar", "futures_group": "FX Futures", "exchange": "CME", "contract_hint": "CAD/USD futures", "sort_order": 350},
    {"provider_symbol": "MES=F", "display_name": "Micro E-mini S&P 500", "futures_group": "Optional Micro", "exchange": "CME", "contract_hint": "Micro S&P 500 index futures", "sort_order": 410},
    {"provider_symbol": "MNQ=F", "display_name": "Micro E-mini Nasdaq 100", "futures_group": "Optional Micro", "exchange": "CME", "contract_hint": "Micro Nasdaq 100 index futures", "sort_order": 420},
    {"provider_symbol": "M2K=F", "display_name": "Micro E-mini Russell 2000", "futures_group": "Optional Micro", "exchange": "CME", "contract_hint": "Micro Russell 2000 index futures", "sort_order": 430},
    {"provider_symbol": "MCL=F", "display_name": "Micro WTI Crude Oil", "futures_group": "Optional Micro", "exchange": "NYMEX", "contract_hint": "Micro WTI crude oil futures", "sort_order": 440},
    {"provider_symbol": "BTC=F", "display_name": "Bitcoin Futures", "futures_group": "Optional Crypto", "exchange": "CME", "contract_hint": "Bitcoin futures", "sort_order": 510},
    {"provider_symbol": "MBT=F", "display_name": "Micro Bitcoin Futures", "futures_group": "Optional Crypto", "exchange": "CME", "contract_hint": "Micro Bitcoin futures", "sort_order": 520},
    {"provider_symbol": "ETH=F", "display_name": "Ether Futures", "futures_group": "Optional Crypto", "exchange": "CME", "contract_hint": "Ether futures", "sort_order": 530},
)

DEFAULT_CORE_FUTURES_SYMBOLS = tuple(
    row["provider_symbol"]
    for row in DEFAULT_FUTURES_INSTRUMENTS
    if not str(row["futures_group"]).startswith("Optional")
)
DEFAULT_PREOPEN_FUTURES_SYMBOLS = ("NQ=F", "ZN=F", "CL=F", "6E=F", "GC=F", "6J=F")


def _utc_now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def _timestamp_str(value: datetime | None = None) -> str:
    ts = value or _utc_now()
    if ts.tzinfo is not None:
        ts = ts.astimezone(UTC).replace(tzinfo=None)
    return ts.strftime("%Y-%m-%d %H:%M:%S")


def _db(host: str, user: str, password: str, port: int) -> MySQLClient:
    return MySQLClient(host, user, password, port)


def normalize_futures_symbols(symbols: str | Iterable[Any] | None, *, max_symbols: int = 64) -> list[str]:
    if symbols is None:
        raw_items: Iterable[Any] = DEFAULT_CORE_FUTURES_SYMBOLS
    elif isinstance(symbols, str):
        raw_items = symbols.replace("\n", ",").split(",")
    else:
        raw_items = symbols

    out: list[str] = []
    seen: set[str] = set()
    for item in raw_items:
        symbol = str(item or "").strip().upper()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        out.append(symbol)
        if len(out) >= max(1, int(max_symbols or 64)):
            break
    return out


def sync_futures_market_tables(
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> None:
    meta_db = _db(host, user, password, port)
    price_db = _db(host, user, password, port)
    try:
        meta_db.use_db(DB_META)
        sync_table_schema(
            meta_db,
            "futures_instrument",
            FUTURES_MARKET_SCHEMAS["futures_instrument"],
            DB_META,
        )
        sync_table_schema(
            meta_db,
            "futures_market_monitor_run",
            FUTURES_MARKET_SCHEMAS["futures_market_monitor_run"],
            DB_META,
        )
        price_db.use_db(DB_PRICE)
        sync_table_schema(
            price_db,
            "futures_ohlcv",
            FUTURES_MARKET_SCHEMAS["futures_ohlcv"],
            DB_PRICE,
        )
    finally:
        meta_db.close()
        price_db.close()


def _instrument_rows(rows: Sequence[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for item in rows or DEFAULT_FUTURES_INSTRUMENTS:
        symbol = str(item.get("provider_symbol") or "").strip().upper()
        if not symbol:
            continue
        normalized.append(
            {
                "provider_symbol": symbol,
                "display_name": str(item.get("display_name") or symbol),
                "futures_group": str(item.get("futures_group") or "Other"),
                "exchange": item.get("exchange"),
                "contract_hint": item.get("contract_hint"),
                "source": str(item.get("source") or FUTURES_SOURCE),
                "source_type": str(item.get("source_type") or "manual_preset"),
                "active": 1 if item.get("active", 1) else 0,
                "sort_order": int(item.get("sort_order") or 1000),
                "notes": item.get("notes"),
            }
        )
    return normalized


def upsert_futures_instruments(
    rows: Sequence[dict[str, Any]] | None = None,
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> int:
    normalized = _instrument_rows(rows)
    if not normalized:
        return 0
    db = _db(host, user, password, port)
    try:
        db.use_db(DB_META)
        sync_table_schema(db, "futures_instrument", FUTURES_MARKET_SCHEMAS["futures_instrument"], DB_META)
        sql = """
        INSERT INTO futures_instrument (
          provider_symbol, display_name, futures_group, exchange, contract_hint,
          source, source_type, active, sort_order, notes
        ) VALUES (
          %(provider_symbol)s, %(display_name)s, %(futures_group)s, %(exchange)s, %(contract_hint)s,
          %(source)s, %(source_type)s, %(active)s, %(sort_order)s, %(notes)s
        )
        ON DUPLICATE KEY UPDATE
          display_name = VALUES(display_name),
          futures_group = VALUES(futures_group),
          exchange = VALUES(exchange),
          contract_hint = VALUES(contract_hint),
          source_type = VALUES(source_type),
          active = VALUES(active),
          sort_order = VALUES(sort_order),
          notes = VALUES(notes)
        """
        db.executemany(sql, normalized)
        return len(normalized)
    finally:
        db.close()


def _safe_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(parsed):
        return None
    return parsed


def _to_utc_naive(value: Any) -> str | None:
    if value in (None, ""):
        return None
    ts = pd.Timestamp(value)
    if pd.isna(ts):
        return None
    if ts.tzinfo is None:
        ts = ts.tz_localize(UTC)
    else:
        ts = ts.tz_convert(UTC)
    return ts.strftime("%Y-%m-%d %H:%M:%S")


def _symbol_frame(frame: pd.DataFrame, symbol: str) -> pd.DataFrame:
    if frame is None or frame.empty:
        return pd.DataFrame()
    if isinstance(frame.columns, pd.MultiIndex):
        for level in range(frame.columns.nlevels):
            try:
                symbols = {str(value).upper() for value in frame.columns.get_level_values(level)}
            except Exception:
                continue
            if symbol.upper() in symbols:
                return frame.xs(symbol, axis=1, level=level, drop_level=True)
        return pd.DataFrame()
    return frame


def _normalize_ohlcv_rows(
    frame: pd.DataFrame,
    *,
    symbol: str,
    interval: str,
    collected_at: str,
) -> list[dict[str, Any]]:
    symbol_frame = _symbol_frame(frame, symbol)
    if symbol_frame.empty:
        return []

    normalized_columns = {str(column).strip().lower().replace(" ", "_"): column for column in symbol_frame.columns}
    rows: list[dict[str, Any]] = []
    for index, item in symbol_frame.iterrows():
        candle_time = _to_utc_naive(index)
        if not candle_time:
            continue
        open_value = _safe_float(item.get(normalized_columns.get("open")))
        high_value = _safe_float(item.get(normalized_columns.get("high")))
        low_value = _safe_float(item.get(normalized_columns.get("low")))
        close_value = _safe_float(item.get(normalized_columns.get("close")))
        if all(value is None for value in (open_value, high_value, low_value, close_value)):
            continue
        rows.append(
            {
                "provider_symbol": symbol,
                "interval_code": interval,
                "candle_time_utc": candle_time,
                "source": FUTURES_SOURCE,
                "source_ref": f"yfinance:{symbol}:{interval}",
                "open": open_value,
                "high": high_value,
                "low": low_value,
                "close": close_value,
                "adj_close": _safe_float(item.get(normalized_columns.get("adj_close"))),
                "volume": _safe_float(item.get(normalized_columns.get("volume"))),
                "provider_status": "ok",
                "collected_at": collected_at,
                "error_msg": None,
            }
        )
    return rows


def upsert_futures_ohlcv_rows(
    rows: Sequence[dict[str, Any]],
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> int:
    normalized = list(rows)
    if not normalized:
        return 0
    db = _db(host, user, password, port)
    try:
        db.use_db(DB_PRICE)
        sync_table_schema(db, "futures_ohlcv", FUTURES_MARKET_SCHEMAS["futures_ohlcv"], DB_PRICE)
        sql = """
        INSERT INTO futures_ohlcv (
          provider_symbol, interval_code, candle_time_utc, source, source_ref,
          open, high, low, close, adj_close, volume,
          provider_status, collected_at, error_msg
        ) VALUES (
          %(provider_symbol)s, %(interval_code)s, %(candle_time_utc)s, %(source)s, %(source_ref)s,
          %(open)s, %(high)s, %(low)s, %(close)s, %(adj_close)s, %(volume)s,
          %(provider_status)s, %(collected_at)s, %(error_msg)s
        )
        ON DUPLICATE KEY UPDATE
          source_ref = VALUES(source_ref),
          open = VALUES(open),
          high = VALUES(high),
          low = VALUES(low),
          close = VALUES(close),
          adj_close = VALUES(adj_close),
          volume = VALUES(volume),
          provider_status = VALUES(provider_status),
          collected_at = VALUES(collected_at),
          error_msg = VALUES(error_msg)
        """
        db.executemany(sql, normalized)
        return len(normalized)
    finally:
        db.close()


def upsert_futures_monitor_run(
    row: dict[str, Any],
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> int:
    db = _db(host, user, password, port)
    try:
        db.use_db(DB_META)
        sync_table_schema(
            db,
            "futures_market_monitor_run",
            FUTURES_MARKET_SCHEMAS["futures_market_monitor_run"],
            DB_META,
        )
        payload = dict(row)
        for key in ("failed_symbols_json", "diagnostics_json"):
            value = payload.get(key)
            if isinstance(value, (dict, list, tuple)):
                payload[key] = json.dumps(value, ensure_ascii=False)
        sql = """
        INSERT INTO futures_market_monitor_run (
          run_id, source, period_code, interval_code, cadence_mode,
          status, started_at, finished_at, duration_sec,
          symbols_requested, symbols_processed, rows_written, latest_candle_time_utc,
          failed_symbols_json, diagnostics_json, message
        ) VALUES (
          %(run_id)s, %(source)s, %(period_code)s, %(interval_code)s, %(cadence_mode)s,
          %(status)s, %(started_at)s, %(finished_at)s, %(duration_sec)s,
          %(symbols_requested)s, %(symbols_processed)s, %(rows_written)s, %(latest_candle_time_utc)s,
          %(failed_symbols_json)s, %(diagnostics_json)s, %(message)s
        )
        ON DUPLICATE KEY UPDATE
          status = VALUES(status),
          finished_at = VALUES(finished_at),
          duration_sec = VALUES(duration_sec),
          symbols_requested = VALUES(symbols_requested),
          symbols_processed = VALUES(symbols_processed),
          rows_written = VALUES(rows_written),
          latest_candle_time_utc = VALUES(latest_candle_time_utc),
          failed_symbols_json = VALUES(failed_symbols_json),
          diagnostics_json = VALUES(diagnostics_json),
          message = VALUES(message)
        """
        db.execute(sql, payload)
        return 1
    finally:
        db.close()


def _download_prices(symbols: Sequence[str], *, period: str, interval: str) -> pd.DataFrame:
    return yf.download(
        list(symbols),
        period=period,
        interval=interval,
        progress=False,
        auto_adjust=False,
        threads=False,
    )


def _fallback_period_for_intraday_coverage(period: str, interval: str) -> str | None:
    """Return the bounded second-pass period for Yahoo futures intraday gaps."""
    if str(period or "").strip().lower() != "1d":
        return None
    if str(interval or "").strip().lower() != "1m":
        return None
    return "2d"


def collect_and_store_futures_ohlcv(
    symbols: str | Iterable[Any] | None = None,
    *,
    period: str = DEFAULT_FUTURES_PERIOD,
    interval: str = DEFAULT_FUTURES_INTERVAL,
    cadence_mode: str = "manual",
    max_symbols: int = 24,
    batch_size: int = 8,
    sleep_sec: float = 0.15,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
    downloader: Callable[..., pd.DataFrame] | None = None,
) -> dict[str, Any]:
    normalized_interval = str(interval or DEFAULT_FUTURES_INTERVAL).strip()
    if normalized_interval not in VALID_FUTURES_INTERVALS:
        raise ValueError(f"Unsupported futures interval: {interval!r}")
    normalized_period = str(period or DEFAULT_FUTURES_PERIOD).strip()
    normalized_symbols = normalize_futures_symbols(symbols, max_symbols=max_symbols)

    run_id = str(uuid4())
    started_at = _utc_now()
    collected_at = _timestamp_str(started_at)
    sync_futures_market_tables(host=host, user=user, password=password, port=port)
    upsert_futures_instruments(host=host, user=user, password=password, port=port)

    if not normalized_symbols:
        result = {
            "run_id": run_id,
            "source": FUTURES_SOURCE,
            "period": normalized_period,
            "interval": normalized_interval,
            "cadence_mode": cadence_mode,
            "status": "failed",
            "rows_written": 0,
            "symbols_requested": 0,
            "symbols_processed": 0,
            "failed_symbols": [],
            "latest_candle_time_utc": None,
            "message": "No futures symbols requested.",
            "diagnostics": {},
        }
        upsert_futures_monitor_run(
            {
                "run_id": run_id,
                "source": FUTURES_SOURCE,
                "period_code": normalized_period,
                "interval_code": normalized_interval,
                "cadence_mode": cadence_mode,
                "status": "failed",
                "started_at": collected_at,
                "finished_at": collected_at,
                "duration_sec": 0.0,
                "symbols_requested": 0,
                "symbols_processed": 0,
                "rows_written": 0,
                "latest_candle_time_utc": None,
                "failed_symbols_json": [],
                "diagnostics_json": {},
                "message": result["message"],
            },
            host=host,
            user=user,
            password=password,
            port=port,
        )
        return result

    price_downloader = downloader or _download_prices
    all_rows: list[dict[str, Any]] = []
    failed_symbols: list[str] = []
    sparse_symbols: list[str] = []
    initial_rows_by_symbol: dict[str, int] = {}
    batches: list[dict[str, Any]] = []
    for offset in range(0, len(normalized_symbols), max(1, int(batch_size or 1))):
        batch = normalized_symbols[offset : offset + max(1, int(batch_size or 1))]
        batch_started = _utc_now()
        frame = price_downloader(batch, period=normalized_period, interval=normalized_interval)
        batch_rows = 0
        for symbol in batch:
            rows = _normalize_ohlcv_rows(
                frame,
                symbol=symbol,
                interval=normalized_interval,
                collected_at=collected_at,
            )
            initial_rows_by_symbol[symbol] = len(rows)
            if not rows:
                failed_symbols.append(symbol)
            elif (
                _fallback_period_for_intraday_coverage(normalized_period, normalized_interval)
                and len(rows) < MIN_1D_INTRADAY_ROWS_BEFORE_FALLBACK
            ):
                sparse_symbols.append(symbol)
            batch_rows += len(rows)
            all_rows.extend(rows)
        batches.append(
            {
                "symbols": batch,
                "rows": batch_rows,
                "duration_sec": round((_utc_now() - batch_started).total_seconds(), 3),
            }
        )
        if sleep_sec and offset + len(batch) < len(normalized_symbols):
            sleep(max(0.0, float(sleep_sec)))

    fallback_retries: list[dict[str, Any]] = []
    fallback_period = _fallback_period_for_intraday_coverage(normalized_period, normalized_interval)
    fallback_candidates = [
        symbol
        for symbol in normalized_symbols
        if symbol in set(failed_symbols) or symbol in set(sparse_symbols)
    ]
    if fallback_period and fallback_candidates:
        recovered_symbols: set[str] = set()
        fallback_rows_by_symbol: dict[str, list[dict[str, Any]]] = {}
        for offset in range(0, len(fallback_candidates), max(1, int(batch_size or 1))):
            batch = fallback_candidates[offset : offset + max(1, int(batch_size or 1))]
            batch_started = _utc_now()
            frame = price_downloader(batch, period=fallback_period, interval=normalized_interval)
            batch_rows = 0
            batch_recovered: list[str] = []
            batch_failed: list[str] = []
            for symbol in batch:
                rows = _normalize_ohlcv_rows(
                    frame,
                    symbol=symbol,
                    interval=normalized_interval,
                    collected_at=collected_at,
                )
                if rows:
                    recovered_symbols.add(symbol)
                    batch_recovered.append(symbol)
                    batch_rows += len(rows)
                    fallback_rows_by_symbol[symbol] = rows
                else:
                    batch_failed.append(symbol)
            reason = (
                "sparse_1d_intraday_rows"
                if any(initial_rows_by_symbol.get(symbol, 0) > 0 for symbol in batch)
                else "empty_1d_intraday_rows"
            )
            fallback_retries.append(
                {
                    "period": fallback_period,
                    "interval": normalized_interval,
                    "reason": reason,
                    "symbols": batch,
                    "recovered_symbols": batch_recovered,
                    "failed_symbols": batch_failed,
                    "initial_rows_by_symbol": {
                        symbol: initial_rows_by_symbol.get(symbol, 0)
                        for symbol in batch
                    },
                    "rows": batch_rows,
                    "duration_sec": round((_utc_now() - batch_started).total_seconds(), 3),
                }
            )
            if sleep_sec and offset + len(batch) < len(fallback_candidates):
                sleep(max(0.0, float(sleep_sec)))
        if recovered_symbols:
            all_rows = [
                row
                for row in all_rows
                if str(row.get("provider_symbol") or "").upper() not in recovered_symbols
            ]
            for symbol in normalized_symbols:
                if symbol in fallback_rows_by_symbol:
                    all_rows.extend(fallback_rows_by_symbol[symbol])
        failed_symbols = [symbol for symbol in failed_symbols if symbol not in recovered_symbols]

    rows_written = upsert_futures_ohlcv_rows(
        all_rows,
        host=host,
        user=user,
        password=password,
        port=port,
    )
    latest_candle = max((row["candle_time_utc"] for row in all_rows), default=None)
    symbols_processed = len(normalized_symbols) - len(set(failed_symbols))
    status = "failed" if rows_written <= 0 else "partial_success" if failed_symbols else "success"
    finished_at = _utc_now()
    message = (
        "Futures OHLCV collection completed."
        if status == "success"
        else "Futures OHLCV collection completed with missing symbols."
        if status == "partial_success"
        else "Futures OHLCV collection wrote no rows."
    )
    diagnostics = {
        "batches": batches,
        "fallback_retries": fallback_retries,
        "default_source": "yfinance pilot source; not exchange-grade realtime",
    }
    upsert_futures_monitor_run(
        {
            "run_id": run_id,
            "source": FUTURES_SOURCE,
            "period_code": normalized_period,
            "interval_code": normalized_interval,
            "cadence_mode": cadence_mode,
            "status": status,
            "started_at": collected_at,
            "finished_at": _timestamp_str(finished_at),
            "duration_sec": round((finished_at - started_at).total_seconds(), 3),
            "symbols_requested": len(normalized_symbols),
            "symbols_processed": symbols_processed,
            "rows_written": rows_written,
            "latest_candle_time_utc": latest_candle,
            "failed_symbols_json": sorted(set(failed_symbols)),
            "diagnostics_json": diagnostics,
            "message": message,
        },
        host=host,
        user=user,
        password=password,
        port=port,
    )
    return {
        "run_id": run_id,
        "source": FUTURES_SOURCE,
        "period": normalized_period,
        "interval": normalized_interval,
        "cadence_mode": cadence_mode,
        "status": status,
        "rows_written": rows_written,
        "symbols_requested": len(normalized_symbols),
        "symbols_processed": symbols_processed,
        "failed_symbols": sorted(set(failed_symbols)),
        "latest_candle_time_utc": latest_candle,
        "message": message,
        "diagnostics": diagnostics,
    }
