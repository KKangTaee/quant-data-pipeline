import yfinance as yf
import pandas as pd

"""
    1️⃣ data.py — Data Source / Boundary Layer
    📌 역할 (Responsibility)

    외부 세계와의 경계

    “시스템 밖”에서 데이터를 가져오는 유일한 위치

    📦 포함 함수
        * get_ohlcv
        * get_fx_rate
"""


def get_ohlcv(tickers:list, start:str=None, period:str="1y", interval:str="1d") -> dict:
    """
    일봉, 월봉 데이터 가져오기
        period : 1y, 1m
        interval : 1d, 1mo
    """

    df = yf.download(tickers, start=start, period=period, interval=interval, group_by="column", actions=True)
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