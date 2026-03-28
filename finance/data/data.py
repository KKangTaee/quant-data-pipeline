import io
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import redirect_stderr, redirect_stdout
from typing import Any, Callable, Iterable, Optional, Literal

import pandas as pd
import yfinance as yf

from .db.mysql import MySQLClient
from .db.schema import PRICE_SCHEMAS  # 방금 추가한 것


TABLE = "nyse_price_history"
DB_PRICE = "finance_price"
Interval = Literal["1d", "1wk", "1mo"]
PRICE_VALUE_COLUMNS = [
    "Open",
    "High",
    "Low",
    "Close",
    "Adj Close",
    "Volume",
    "Dividends",
    "Stock Splits",
]
RATE_LIMIT_MARKERS = ("too many requests", "rate limited", "yfratelimiterror")
PROVIDER_NO_DATA_MARKERS = (
    "possibly delisted",
    "no price data found",
    "no timezone found",
    "http error 404",
)


"""
    1️⃣ data.py — Data Source / Boundary Layer
    📌 역할 (Responsibility)

    외부 세계와의 경계

    “시스템 밖”에서 데이터를 가져오는 유일한 위치

    📦 포함 함수
        * get_ohlcv
        * get_fx_rate
"""

def _to_none(x):
    # MySQL insert용 NaN 처리
    if x is None:
        return None
    try:
        if pd.isna(x):
            return None
    except Exception:
        pass
    return x


def _sleep_with_jitter(base_sleep: float, jitter_ratio: float = 0.25) -> float:
    if base_sleep <= 0:
        return 0.0
    jitter = base_sleep * max(jitter_ratio, 0.0)
    actual_sleep = base_sleep + random.uniform(0.0, jitter)
    time.sleep(actual_sleep)
    return actual_sleep


def _extract_provider_symbols(provider_output: str, batch: list[str]) -> list[str]:
    if not provider_output:
        return []

    output_upper = provider_output.upper()
    matched: list[str] = []
    for sym in batch:
        if sym.upper() in output_upper:
            matched.append(sym)
    return matched


def _classify_provider_output(
    *,
    provider_output: str,
    batch: list[str],
    missing_symbols: list[str],
) -> dict[str, Any]:
    normalized = provider_output.lower()
    matched_symbols = _extract_provider_symbols(provider_output, batch)
    rate_limit_hit = any(marker in normalized for marker in RATE_LIMIT_MARKERS)
    no_data_hit = any(marker in normalized for marker in PROVIDER_NO_DATA_MARKERS)

    rate_limited_symbols: list[str] = []
    provider_no_data_symbols: list[str] = []

    if rate_limit_hit:
        rate_limited_symbols = matched_symbols or missing_symbols or list(batch)

    if no_data_hit:
        provider_no_data_symbols = [
            sym for sym in (matched_symbols or missing_symbols) if sym not in rate_limited_symbols
        ]

    provider_excerpt = "\n".join(line for line in provider_output.splitlines()[:8] if line.strip())

    return {
        "rate_limit_hit": rate_limit_hit,
        "rate_limited_symbols": sorted(set(rate_limited_symbols)),
        "provider_no_data_symbols": sorted(set(provider_no_data_symbols)),
        "provider_output_excerpt": provider_excerpt,
    }


def _infer_requested_date_window(
    *,
    start: str | None = None,
    end: str | None = None,
    period: str = "1y",
) -> tuple[str | None, str | None]:
    """
    start/end가 없을 때 period 기준으로 대략적인 요청 구간을 계산한다.
    canonical refresh에서 기존 범위를 지우고 다시 넣을 때 사용한다.
    """
    end_ts = pd.to_datetime(end).normalize() if end is not None else pd.Timestamp.today().normalize()

    if start is not None:
        start_ts = pd.to_datetime(start).normalize()
        return start_ts.strftime("%Y-%m-%d"), end_ts.strftime("%Y-%m-%d")

    p = str(period).strip().lower()
    if p == "max":
        return None, end_ts.strftime("%Y-%m-%d")

    if p.endswith("d") and p[:-1].isdigit():
        start_ts = end_ts - pd.DateOffset(days=int(p[:-1]))
        return start_ts.strftime("%Y-%m-%d"), end_ts.strftime("%Y-%m-%d")

    if p.endswith("mo") and p[:-2].isdigit():
        start_ts = end_ts - pd.DateOffset(months=int(p[:-2]))
        return start_ts.strftime("%Y-%m-%d"), end_ts.strftime("%Y-%m-%d")

    if p.endswith("y") and p[:-1].isdigit():
        start_ts = end_ts - pd.DateOffset(years=int(p[:-1]))
        return start_ts.strftime("%Y-%m-%d"), end_ts.strftime("%Y-%m-%d")

    return None, end_ts.strftime("%Y-%m-%d")


def _delete_ohlcv_rows(
    db: MySQLClient,
    *,
    symbols: list[str],
    timeframe: str,
    start: str | None,
    end: str | None,
) -> None:
    if not symbols:
        return

    placeholders = ",".join(["%s"] * len(symbols))
    where = [f"symbol IN ({placeholders})", "timeframe = %s"]
    params: list[Any] = list(symbols) + [timeframe]

    if start is not None:
        where.append("`date` >= %s")
        params.append(start)
    if end is not None:
        where.append("`date` <= %s")
        params.append(end)

    sql = f"DELETE FROM {TABLE} WHERE {' AND '.join(where)}"
    db.execute(sql, params)


def get_ohlcv(
    tickers: list[str],
    start: str | None = None,
    end: str | None = None,
    period: str = "1y",
    interval: str = "1d",
    return_provider_output: bool = False,
) -> dict | tuple[dict, str]:
    """
    일봉, 월봉 데이터 가져오기
        period : 1y, 1m
        interval : 1d, 1mo
    """

    tickers = [str(t).strip().upper() for t in tickers if str(t).strip()]
    if not tickers:
        return {}

    download_kwargs = {
        "tickers": tickers,
        "interval": interval,
        "group_by": "column",
        "actions": True,
        "progress": False,
        "threads": False,
        "auto_adjust": False,
    }
    if start is not None or end is not None:
        download_kwargs["start"] = start
        if end is not None:
            inclusive_end = pd.to_datetime(end).normalize() + pd.Timedelta(days=1)
            download_kwargs["end"] = inclusive_end.strftime("%Y-%m-%d")
        else:
            download_kwargs["end"] = end
    else:
        download_kwargs["period"] = period

    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
        df = yf.download(**download_kwargs)
    provider_output = "\n".join(
        part.strip()
        for part in (stdout_buffer.getvalue(), stderr_buffer.getvalue())
        if part and part.strip()
    )
    if df is None or df.empty:
        return ({}, provider_output) if return_provider_output else {}

    out = {}
    if isinstance(df.columns, pd.MultiIndex):
        available_tickers = list(dict.fromkeys(df.columns.get_level_values(1)))
        for t in available_tickers:
            try:
                sliced = df.xs(t, axis=1, level=1)
            except KeyError:
                continue
            if sliced is None or sliced.empty:
                continue
            d = sliced.dropna(how="all").assign(Ticker=t).reset_index()
            if d.empty:
                continue
            d["Date"] = pd.to_datetime(d["Date"])
            d.columns.name = None

            cols = d.columns.tolist()
            cols.insert(1, cols.pop(cols.index("Ticker")))
            out[t] = d[cols]
    else:
        ticker = tickers[0]
        d = df.dropna(how="all").assign(Ticker=ticker).reset_index()
        if not d.empty:
            d["Date"] = pd.to_datetime(d["Date"])
            d.columns.name = None
            cols = d.columns.tolist()
            cols.insert(1, cols.pop(cols.index("Ticker")))
            out[ticker] = d[cols]
    
    return (out, provider_output) if return_provider_output else out



def get_fx_rate(base: str, quote: str, period="1y", interval="1d") -> float:
    """
    base → quote 환율을 반환
    예: base='USD', quote='KRW' → USDKRW 환율
    """
    ticker = f"{base}{quote}=X"
    df = yf.Ticker(ticker).history(period=period, interval=interval)

    if df.empty:
        raise ValueError(f"환율 데이터를 가져올 수 없습니다: {ticker}")

    df['Ticker']=f"{base}/{quote}"
    df = df.reset_index()
    df = df[['Date','Ticker','Close']]

    df = (
    df.pivot(index="Date", columns="Ticker", values="Close")
        .reset_index()
    )
    df.columns.name = None
    return df


def store_ohlcv_to_mysql(
    symbols: Iterable[str],
    start: Optional[str] = None,
    end: Optional[str] = None,
    period: str = "1y",
    interval: Interval = "1d",
    host="localhost",
    user="root",
    password="1234",
    port=3306,
    chunk_size: int = 40,
    sleep: float = 0.15,
    max_workers: int = 2,
    max_retry: int = 3,
    retry_backoff: float = 1.5,
    sleep_jitter_ratio: float = 0.25,
    rate_limit_cooldown_sec: float = 0.0,
    rate_limit_circuit_break_threshold: int = 1,
    cooldown_chunk_size: int | None = None,
    degrade_to_single_worker_on_rate_limit: bool = True,
    replace_requested_range: bool = True,
    return_stats: bool = False,
    progress_callback: Optional[Callable[[dict[str, Any]], None]] = None,
):
    """
    symbols + (start/end 또는 period)로 yfinance OHLCV를 가져와 DB에 UPSERT.

    - start/end가 주어지면 start/end 우선
    - start/end가 없으면 period 사용
    """
    symbols = [s for s in symbols if s and str(s).strip()]
    if not symbols:
        return {
            "rows_written": 0,
            "symbols_requested": 0,
            "symbols_with_data": 0,
            "missing_symbols": [],
            "batch_errors": [],
            "rate_limited_symbols": [],
            "provider_no_data_symbols": [],
            "provider_message_batches": [],
            "cooldown_events": [],
            "timing_breakdown": {
                "fetch_sec": 0.0,
                "delete_sec": 0.0,
                "upsert_sec": 0.0,
                "retry_sleep_sec": 0.0,
                "cooldown_sleep_sec": 0.0,
                "inter_batch_sleep_sec": 0.0,
                "batch_count": 0,
                "written_batch_count": 0,
                "avg_fetch_sec_per_batch": 0.0,
                "avg_rows_per_written_batch": 0.0,
            },
        } if return_stats else 0

    db = MySQLClient(host, user, password, port)
    inserted = 0

    def chunked(lst, size):
        for i in range(0, len(lst), size):
            yield lst[i:i+size]

    requested_start, requested_end = _infer_requested_date_window(start=start, end=end, period=period)

    def rows_from_downloaded_frames(downloaded: dict[str, pd.DataFrame], timeframe: str) -> tuple[list[tuple], list[str]]:
        rows: list[tuple] = []
        loaded_symbols: list[str] = []

        for sym, df in downloaded.items():
            if df is None or df.empty:
                continue

            d = df.copy()
            d["Date"] = pd.to_datetime(d["Date"], errors="coerce").dt.date
            d = d.dropna(subset=["Date"])
            if d.empty:
                continue

            cols = {c.lower(): c for c in d.columns}

            existing_value_cols = [cols[c.lower()] for c in PRICE_VALUE_COLUMNS if c.lower() in cols]
            if existing_value_cols:
                d = d.dropna(subset=existing_value_cols, how="all")
            if d.empty:
                continue

            def col(name, default=None):
                return cols.get(name.lower(), default)

            for _, r in d.iterrows():
                rows.append(
                    (
                        sym,
                        timeframe,
                        r["Date"],
                        _to_none(r.get(col("Open"))),
                        _to_none(r.get(col("High"))),
                        _to_none(r.get(col("Low"))),
                        _to_none(r.get(col("Close"))),
                        _to_none(r.get(col("Adj Close"))),
                        _to_none(r.get(col("Volume"))),
                        _to_none(r.get(col("Dividends"))),
                        _to_none(r.get(col("Stock Splits"))),
                    )
                )

            loaded_symbols.append(sym)

        return rows, loaded_symbols

    def fetch_batch(batch_index: int, batch: list[str]) -> dict[str, Any]:
        fetch_started = time.perf_counter()
        last_error: str | None = None
        retry_sleep_sec = 0.0
        for attempt in range(max_retry + 1):
            try:
                dfs, provider_output = get_ohlcv(
                    list(batch),
                    start=start,
                    end=end,
                    period=period,
                    interval=interval,
                    return_provider_output=True,
                )
                rows, loaded_symbols = rows_from_downloaded_frames(dfs, interval)
                loaded_symbol_set = set(loaded_symbols)
                missing_symbols = [sym for sym in batch if sym not in loaded_symbol_set]
                provider_diag = _classify_provider_output(
                    provider_output=provider_output,
                    batch=batch,
                    missing_symbols=missing_symbols,
                )
                return {
                    "batch_index": batch_index,
                    "rows": rows,
                    "loaded_symbols": loaded_symbols,
                    "missing_symbols": missing_symbols,
                    "fetch_elapsed_sec": time.perf_counter() - fetch_started,
                    "retry_sleep_sec": retry_sleep_sec,
                    "rate_limit_hit": provider_diag["rate_limit_hit"],
                    "rate_limited_symbols": provider_diag["rate_limited_symbols"],
                    "provider_no_data_symbols": provider_diag["provider_no_data_symbols"],
                    "provider_output_excerpt": provider_diag["provider_output_excerpt"],
                    "error": None,
                }
            except Exception as exc:
                last_error = str(exc)
                if attempt < max_retry:
                    retry_sleep_sec += _sleep_with_jitter(retry_backoff * (attempt + 1), sleep_jitter_ratio)

        return {
            "batch_index": batch_index,
            "rows": [],
            "loaded_symbols": [],
            "missing_symbols": list(batch),
            "fetch_elapsed_sec": time.perf_counter() - fetch_started,
            "retry_sleep_sec": retry_sleep_sec,
            "rate_limit_hit": any(marker in str(last_error).lower() for marker in RATE_LIMIT_MARKERS),
            "rate_limited_symbols": list(batch)
            if any(marker in str(last_error).lower() for marker in RATE_LIMIT_MARKERS)
            else [],
            "provider_no_data_symbols": [],
            "provider_output_excerpt": "",
            "error": last_error,
        }

    try:
        db.use_db(DB_PRICE)
        db.execute(PRICE_SCHEMAS["price_history"])

        upsert_sql = """
        INSERT INTO nyse_price_history
            (symbol, timeframe, `date`,
             open, high, low, close, adj_close, volume,
             dividends, stock_splits)
        VALUES
            (%s, %s, %s,
             %s, %s, %s, %s, %s, %s,
             %s, %s)
        ON DUPLICATE KEY UPDATE
            open = VALUES(open),
            high = VALUES(high),
            low  = VALUES(low),
            close = VALUES(close),
            adj_close = VALUES(adj_close),
            volume = VALUES(volume),
            dividends = VALUES(dividends),
            stock_splits = VALUES(stock_splits)
        """

        total_symbols = len(symbols)
        total_batches = (total_symbols + max(chunk_size, 1) - 1) // max(chunk_size, 1)
        processed_symbols = 0
        symbols_with_data: set[str] = set()
        missing_symbols: set[str] = set()
        rate_limited_symbols: set[str] = set()
        provider_no_data_symbols: set[str] = set()
        batch_errors: list[dict[str, Any]] = []
        provider_message_batches: list[dict[str, Any]] = []
        cooldown_events: list[dict[str, Any]] = []
        total_fetch_sec = 0.0
        total_delete_sec = 0.0
        total_upsert_sec = 0.0
        total_retry_sleep_sec = 0.0
        total_cooldown_sleep_sec = 0.0
        total_inter_batch_sleep_sec = 0.0
        total_written_batches = 0

        if progress_callback is not None:
            progress_callback(
                {
                    "event": "batch_progress",
                    "processed_symbols": 0,
                    "total_symbols": total_symbols,
                    "batch_index": 0,
                    "total_batches": total_batches,
                    "rows_written": 0,
                }
            )

        current_chunk_size = max(1, chunk_size)
        current_worker_count = max(1, max_workers)
        next_batch_index = 1
        offset = 0
        consecutive_rate_limit_batches = 0

        while offset < total_symbols:
            window_batches: list[tuple[int, list[str]]] = []
            for _ in range(max(1, current_worker_count)):
                batch = symbols[offset : offset + current_chunk_size]
                if not batch:
                    break
                window_batches.append((next_batch_index, batch))
                next_batch_index += 1
                offset += len(batch)

            if not window_batches:
                break

            if len(window_batches) == 1:
                batch_index, batch = window_batches[0]
                window_results = [(batch_index, batch, fetch_batch(batch_index, batch))]
            else:
                with ThreadPoolExecutor(max_workers=len(window_batches)) as executor:
                    future_map = {
                        executor.submit(fetch_batch, batch_index, list(batch)): (batch_index, list(batch))
                        for batch_index, batch in window_batches
                    }
                    window_results = []
                    for future in as_completed(future_map):
                        batch_index, batch = future_map[future]
                        window_results.append((batch_index, batch, future.result()))

            for batch_index, batch, result in sorted(window_results, key=lambda item: item[0]):
                rows = result["rows"]
                total_fetch_sec += float(result.get("fetch_elapsed_sec") or 0.0)
                total_retry_sleep_sec += float(result.get("retry_sleep_sec") or 0.0)
                if rows:
                    if replace_requested_range and requested_end is not None:
                        delete_started = time.perf_counter()
                        _delete_ohlcv_rows(
                            db,
                            symbols=result["loaded_symbols"],
                            timeframe=interval,
                            start=requested_start,
                            end=requested_end,
                        )
                        total_delete_sec += time.perf_counter() - delete_started
                    upsert_started = time.perf_counter()
                    db.executemany(upsert_sql, rows)
                    total_upsert_sec += time.perf_counter() - upsert_started
                    inserted += len(rows)
                    total_written_batches += 1

                symbols_with_data.update(result["loaded_symbols"])
                missing_symbols.update(result["missing_symbols"])
                rate_limited_symbols.update(result.get("rate_limited_symbols") or [])
                provider_no_data_symbols.update(result.get("provider_no_data_symbols") or [])
                if result.get("provider_output_excerpt"):
                    provider_message_batches.append(
                        {
                            "batch_index": batch_index,
                            "symbols": batch,
                            "message_excerpt": result["provider_output_excerpt"],
                        }
                    )
                if result["error"]:
                    batch_errors.append(
                        {
                            "batch_index": batch_index,
                            "symbols": batch,
                            "error": result["error"],
                        }
                    )

                processed_symbols += len(batch)
                if progress_callback is not None:
                    progress_callback(
                        {
                            "event": "batch_progress",
                            "processed_symbols": processed_symbols,
                            "total_symbols": total_symbols,
                            "batch_index": batch_index,
                            "total_batches": total_batches,
                            "rows_written": inserted,
                            "symbols_with_data": len(symbols_with_data),
                            "missing_symbols": len(missing_symbols),
                            "rate_limited_symbols": len(rate_limited_symbols),
                        }
                    )

            window_rate_limit_hits = sum(
                1 for _, _, result in window_results if bool(result.get("rate_limit_hit"))
            )
            if window_rate_limit_hits:
                consecutive_rate_limit_batches += window_rate_limit_hits
                if degrade_to_single_worker_on_rate_limit:
                    current_worker_count = 1
                if cooldown_chunk_size is not None:
                    current_chunk_size = max(1, min(current_chunk_size, cooldown_chunk_size))
                if (
                    rate_limit_cooldown_sec > 0
                    and consecutive_rate_limit_batches >= max(1, rate_limit_circuit_break_threshold)
                ):
                    cooldown_event = {
                        "after_batch_index": window_results[-1][0],
                        "cooldown_sec": rate_limit_cooldown_sec,
                        "rate_limit_batches": window_rate_limit_hits,
                        "current_chunk_size": current_chunk_size,
                        "current_max_workers": current_worker_count,
                    }
                    cooldown_events.append(cooldown_event)
                    if progress_callback is not None:
                        progress_callback(
                            {
                                "event": "rate_limit_cooldown",
                                **cooldown_event,
                                "total_symbols": total_symbols,
                                "processed_symbols": processed_symbols,
                            }
                        )
                    total_cooldown_sleep_sec += _sleep_with_jitter(rate_limit_cooldown_sec, sleep_jitter_ratio)
            else:
                consecutive_rate_limit_batches = 0

            total_inter_batch_sleep_sec += _sleep_with_jitter(sleep, sleep_jitter_ratio)

    finally:
        db.close()

    total_completed_batches = next_batch_index - 1
    stats = {
        "rows_written": inserted,
        "symbols_requested": total_symbols,
        "symbols_with_data": len(symbols_with_data),
        "missing_symbols": sorted(missing_symbols),
        "batch_errors": batch_errors,
        "rate_limited_symbols": sorted(rate_limited_symbols),
        "provider_no_data_symbols": sorted(provider_no_data_symbols),
        "provider_message_batches": provider_message_batches,
        "cooldown_events": cooldown_events,
        "timing_breakdown": {
            "fetch_sec": round(total_fetch_sec, 3),
            "delete_sec": round(total_delete_sec, 3),
            "upsert_sec": round(total_upsert_sec, 3),
            "retry_sleep_sec": round(total_retry_sleep_sec, 3),
            "cooldown_sleep_sec": round(total_cooldown_sleep_sec, 3),
            "inter_batch_sleep_sec": round(total_inter_batch_sleep_sec, 3),
            "batch_count": total_completed_batches,
            "written_batch_count": total_written_batches,
            "avg_fetch_sec_per_batch": round(total_fetch_sec / total_completed_batches, 3)
            if total_completed_batches
            else 0.0,
            "avg_rows_per_written_batch": round(inserted / total_written_batches, 3)
            if total_written_batches
            else 0.0,
        },
    }
    return stats if return_stats else inserted


def load_ohlcv_many_mysql(
    symbols: list[str],
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    host="localhost",
    user="root",
    password="1234",
    port=3306,
    chunk_size: int = 800,  # IN 절 너무 길어지는 것 방지
) -> pd.DataFrame:
    if not symbols:
        return pd.DataFrame()

    db = MySQLClient(host, user, password, port)
    try:
        db.use_db(DB_PRICE)

        out = []
        for i in range(0, len(symbols), chunk_size):
            batch = symbols[i:i+chunk_size]
            placeholders = ",".join(["%s"] * len(batch))

            where = [f"symbol IN ({placeholders})", "timeframe=%s"]
            params = list(batch) + [timeframe]

            if start:
                where.append("`date` >= %s")
                params.append(start)
            if end:
                where.append("`date` <= %s")
                params.append(end)

            sql = f"""
            SELECT
                symbol, `date`, open, high, low, close, adj_close, volume,
                dividends, stock_splits
            FROM {TABLE}
            WHERE {" AND ".join(where)}
            ORDER BY symbol ASC, `date` ASC
            """
            out.extend(db.query(sql, params))

        df = pd.DataFrame(out)
        if df.empty:
            return df
        df["date"] = pd.to_datetime(df["date"])
        return df

    finally:
        db.close()
