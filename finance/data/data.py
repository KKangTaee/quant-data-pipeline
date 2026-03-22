from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Iterable, Optional, Literal

import pandas as pd
import yfinance as yf

from .db.mysql import MySQLClient
from .db.schema import PRICE_SCHEMAS  # 방금 추가한 것


TABLE = "nyse_price_history"
DB_PRICE = "finance_price"
Interval = Literal["1d", "1wk", "1mo"]


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


def get_ohlcv(
    tickers: list[str],
    start: str | None = None,
    end: str | None = None,
    period: str = "1y",
    interval: str = "1d",
) -> dict:
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
        download_kwargs["end"] = end
    else:
        download_kwargs["period"] = period

    df = yf.download(**download_kwargs)
    if df is None or df.empty:
        return {}

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
    
    return out



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
    chunk_size: int = 100,
    sleep: float = 0.0,
    max_workers: int = 4,
    max_retry: int = 2,
    retry_backoff: float = 0.8,
    return_stats: bool = False,
    progress_callback: Optional[Callable[[dict[str, Any]], None]] = None,
):
    """
    symbols + (start/end 또는 period)로 yfinance OHLCV를 가져와 DB에 UPSERT.

    - start/end가 주어지면 start/end 우선
    - start/end가 없으면 period 사용
    """
    import time

    symbols = [s for s in symbols if s and str(s).strip()]
    if not symbols:
        return {
            "rows_written": 0,
            "symbols_requested": 0,
            "symbols_with_data": 0,
            "missing_symbols": [],
            "batch_errors": [],
        } if return_stats else 0

    db = MySQLClient(host, user, password, port)
    inserted = 0

    def chunked(lst, size):
        for i in range(0, len(lst), size):
            yield lst[i:i+size]

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
        last_error: str | None = None
        for attempt in range(max_retry + 1):
            try:
                dfs = get_ohlcv(
                    list(batch),
                    start=start,
                    end=end,
                    period=period,
                    interval=interval,
                )
                rows, loaded_symbols = rows_from_downloaded_frames(dfs, interval)
                loaded_symbol_set = set(loaded_symbols)
                missing_symbols = [sym for sym in batch if sym not in loaded_symbol_set]
                return {
                    "batch_index": batch_index,
                    "rows": rows,
                    "loaded_symbols": loaded_symbols,
                    "missing_symbols": missing_symbols,
                    "error": None,
                }
            except Exception as exc:
                last_error = str(exc)
                if attempt < max_retry:
                    time.sleep(retry_backoff * (attempt + 1))

        return {
            "batch_index": batch_index,
            "rows": [],
            "loaded_symbols": [],
            "missing_symbols": list(batch),
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
        total_batches = (total_symbols + chunk_size - 1) // chunk_size
        processed_symbols = 0
        symbols_with_data: set[str] = set()
        missing_symbols: set[str] = set()
        batch_errors: list[dict[str, Any]] = []

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

        batches = list(enumerate(chunked(symbols, chunk_size), start=1))
        worker_count = max(1, min(max_workers, len(batches)))

        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            future_map = {
                executor.submit(fetch_batch, batch_index, list(batch)): (batch_index, list(batch))
                for batch_index, batch in batches
            }

            for future in as_completed(future_map):
                batch_index, batch = future_map[future]
                result = future.result()
                rows = result["rows"]
                if rows:
                    db.executemany(upsert_sql, rows)
                    inserted += len(rows)

                symbols_with_data.update(result["loaded_symbols"])
                missing_symbols.update(result["missing_symbols"])
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
                        }
                    )

                if sleep > 0:
                    time.sleep(sleep)

    finally:
        db.close()

    stats = {
        "rows_written": inserted,
        "symbols_requested": total_symbols,
        "symbols_with_data": len(symbols_with_data),
        "missing_symbols": sorted(missing_symbols),
        "batch_errors": batch_errors,
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
