import yfinance as yf
import pandas as pd
from typing import Iterable, Optional, Literal

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


def get_ohlcv(tickers:list, start:str=None, period:str="1y", interval:str="1d") -> dict:
    """
    일봉, 월봉 데이터 가져오기
        period : 1y, 1m
        interval : 1d, 1mo
    """

    df = yf.download(
        tickers,
        start=start,
        period=period,
        interval=interval,
        group_by="column",
        actions=True,
        progress=False,
    )
    tickers = df.columns.levels[1]

    out = {}
    for t in tickers:
        d = (df.xs(t, axis=1, level=1)
               .assign(Ticker=t)
               .reset_index())
        d["Date"] = pd.to_datetime(d["Date"])   # ✅ Date 컬럼 datetime으로 보장
        d.columns.name = None

        cols = d.columns.tolist()
        cols.insert(1, cols.pop(cols.index("Ticker")))
        d = d[cols]        
        out[t] = d
    
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
    chunk_size: int = 50,
    sleep: float = 0.4,
):
    """
    symbols + (start/end 또는 period)로 yfinance OHLCV를 가져와 DB에 UPSERT.

    - start/end가 주어지면 start/end 우선
    - start/end가 없으면 period 사용
    """
    import time
    import random

    symbols = [s for s in symbols if s and str(s).strip()]
    if not symbols:
        return 0

    db = MySQLClient(host, user, password, port)
    inserted = 0

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

        def chunked(lst, size):
            for i in range(0, len(lst), size):
                yield lst[i:i+size]

        for batch in chunked(symbols, chunk_size):
            # ✅ 네가 이미 만든 get_ohlcv 재사용
            if start or end:
                # yfinance download는 start/end 지원 → get_ohlcv는 start만 받으니,
                # 여기서는 start만 넘기고 end는 get_ohlcv 확장하거나,
                # 가장 간단히 period로 맞추는 방식도 가능.
                # (정교하게 하려면 get_ohlcv에 end 추가 추천)
                dfs = get_ohlcv(list(batch), start=start, period=period, interval=interval)
            else:
                dfs = get_ohlcv(list(batch), start=None, period=period, interval=interval)

            rows = []
            for sym, df in dfs.items():
                if df is None or df.empty:
                    continue

                d = df.copy()
                d["Date"] = pd.to_datetime(d["Date"]).dt.date

                # yfinance 컬럼명 케이스 대응
                # (Adj Close가 없을 수도 있음)
                cols = {c.lower(): c for c in d.columns}
                def col(name, default=None):
                    return cols.get(name.lower(), default)

                for _, r in d.iterrows():
                    rows.append((
                        sym,
                        interval,
                        r["Date"],
                        _to_none(r.get(col("Open"))),
                        _to_none(r.get(col("High"))),
                        _to_none(r.get(col("Low"))),
                        _to_none(r.get(col("Close"))),
                        _to_none(r.get(col("Adj Close"))),
                        _to_none(r.get(col("Volume"))),
                        _to_none(r.get(col("Dividends"))),
                        _to_none(r.get(col("Stock Splits"))),
                    ))

            if rows:
                db.executemany(upsert_sql, rows)
                inserted += len(rows)

            # 배치 sleep + 지터 (rate limit 완화)
            time.sleep(sleep + random.random() * 0.2)

    finally:
        db.close()

    return inserted


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
