import pandas as pd
import numpy as np

"""
    2️⃣ transform.py — Pure Data Transformation Layer
    📌 역할
        DataFrame → DataFrame 변환
        데이터 형태·구조·지표 계산

    📦 포함 함수
        * add_ma
        * filter_ohlcv
        * filter_finance_history
        * slice_ohlcv
        * add_returns
        * add_interval_returns
        * align_dfs_by_date_intersection
        * merge_dfs_to_df
        * drop_columns
        * add_avg_score
        * select_rows_by_interval_with_ends
"""

def add_ma(
    dfs:dict,
    windows=(5,10,20,60,120),
    price_col="Close",
    prefix="MA"
) ->dict:

    """
    이평선 구하기
    dfs: { 'AAPL': df, 'MSFT': df, ... }
    windows: 이동평균 기간들 (int 또는 iterable)
    price_col: 기준 가격 컬럼 (보통 Close)
    prefix: 컬럼명 접두사 (MA5, MA20 ...)
    """
    # windows가 단일 정수면 튜플로 변환
    if isinstance(windows, int):
        windows = (windows,)
    
    out = {}

    for t, df in dfs.items():
        d = df.copy()

        # 안전장치: 정렬 + 타입
        d["Date"] = pd.to_datetime(d["Date"])
        d = d.sort_values("Date")

        # 이동평균 생성
        for w in windows:
            d[f"{prefix}{w}"] = d[price_col].rolling(window=w, min_periods=w).mean()

        # 가장 긴 이동평균선 값이 Nan이면 제외하자
        d = d.dropna(subset=[f"{prefix}{max(windows)}"])
        out[t] = d

    return out


def filter_ohlcv(dfs: dict, option: str) -> dict:
    """
    OHLCV 필터링

    option
        - "month_end" : 매월말(실제 마지막 거래일)
        - "year_end"  : 매년말(실제 마지막 거래일)
    """

    out = {}

    for key, df in dfs.items():
        d = filter_finance_history(df, option)
        out[key] = d

    return out


def filter_finance_history(df: pd.DataFrame, option: str) -> pd.DataFrame:
    """
    금융 데이터 필터링

    option
        - "month_start" : 매월초(실제 첫 거래일)
        - "month_end"   : 매월말(실제 마지막 거래일)
        - "year_start"  : 매년초(실제 첫 거래일)
        - "year_end"    : 매년말(실제 마지막 거래일)
    """
    d = df.copy()
    d["Date"] = pd.to_datetime(d["Date"])
    d = d.sort_values("Date").set_index("Date")

    if option == "month_start":
        freq = "BMS"
        selector = "head"
    elif option == "month_end":
        freq = "BME"
        selector = "tail"
    elif option == "year_start":
        freq = "BYS"
        selector = "head"
    elif option == "year_end":
        freq = "BYE"
        selector = "tail"
    else:
        raise ValueError(f"지원하지 않는 option입니다: {option}")

    # 1️⃣ 기간별 배당금 합계
    dividends_sum = (
        d["Dividends"]
        .groupby(pd.Grouper(freq=freq))
        .sum()
    )

    # 2️⃣ 기간별 첫/마지막 거래일
    grouped = d.groupby(pd.Grouper(freq=freq))
    result = grouped.head(1) if selector == "head" else grouped.tail(1)

    # 3️⃣ 배당금 합계 반영
    result["Dividends"] = dividends_sum.values

    return result.reset_index()



def slice_ohlcv(dfs: dict, start=None, end=None) -> dict:
    """
    OHLCV dict에서 Date 기준으로 특정 기간만 슬라이싱

    start : str | datetime | None
        시작 날짜 (None이면 제한 없음)
    end : str | datetime | None
        종료 날짜 (None이면 오늘 날짜)
    """

    # end가 None이면 오늘 날짜
    if end is None:
        end = pd.Timestamp.today().normalize()
    else:
        end = pd.to_datetime(end)

    # start는 None이면 그대로 둠
    if start is not None:
        start = pd.to_datetime(start)

    out = {}

    for ticker, df in dfs.items():
        d = df.copy()

        d["Date"] = pd.to_datetime(d["Date"])
        d = d.sort_values("Date")

        # start / end 예외 처리
        if start is not None:
            d = d[d["Date"] >= start]

        d = d[d["Date"] <= end]

        out[ticker] = d.reset_index(drop=True)

    return out


def add_returns(
    dfs_by_ticker: dict,
    price_col: str = "Close",
    out_col: str = "Return",
    method: str = "simple",   # "simple" or "log"
    fill_first: float | None = np.nan
) -> dict:
    """
    각 티커별 OHLCV DataFrame에 전 row 대비 수익률 컬럼을 추가해서 반환.

    Parameters
    ----------
    dfs_by_ticker : dict
        { 'AAPL': df, 'MSFT': df, ... }
    price_col : str
        수익률 계산에 사용할 가격 컬럼 (보통 Close)
    out_col : str
        결과 수익률 컬럼명
    method : str
        "simple" : (P_t / P_{t-1}) - 1
        "log"    : log(P_t / P_{t-1})
    fill_first : float | None
        첫 행 수익률(이전값이 없어 NaN) 처리값.
        None이면 그대로 둠, 기본은 NaN.

    Returns
    -------
    dict
        수익률 컬럼이 추가된 DataFrame dict
    """
    out = {}

    for t, df in dfs_by_ticker.items():
        d = df.copy()

        # 안전: 날짜 정렬
        if "Date" in d.columns:
            d["Date"] = pd.to_datetime(d["Date"])
            d = d.sort_values("Date")

        # 가격 컬럼 체크
        if price_col not in d.columns:
            raise KeyError(f"[{t}] '{price_col}' 컬럼이 없습니다. 현재 컬럼: {list(d.columns)}")

        s = d[price_col].astype(float)

        if method == "simple":
            r = s.pct_change()
        elif method == "log":
            r = np.log(s).diff()
        else:
            raise ValueError("method는 'simple' 또는 'log'만 가능합니다.")

        if fill_first is not None:
            r = r.fillna(fill_first)

        d[out_col] = r
        out[t] = d.reset_index(drop=True)

    return out


def add_interval_returns(
    dfs: dict,
    return_intervals: list,
    price_col: str = "Close",
    date_col: str = "Date",
    suffix: str = "MReturn"
) -> dict:
    """
    dfs(dict)의 각 DataFrame에 N개월 누적 수익률 컬럼 추가

    예:
        return_intervals = [1, 3, 6]
        → 1MReturn, 3MReturn, 6MReturn

    수익률 정의:
        (P_t / P_{t-n}) - 1
    """

    out = {}

    for key, df in dfs.items():
        d = df.copy()

        # 안전 처리
        d[date_col] = pd.to_datetime(d[date_col])
        d = d.sort_values(date_col).reset_index(drop=True)

        if price_col not in d.columns:
            raise KeyError(f"[{key}] '{price_col}' 컬럼이 없습니다.")

        price = d[price_col].astype(float)

        for n in return_intervals:
            col_name = f"{n}{suffix}"
            d[col_name] = price / price.shift(n) - 1

        # 가장 긴 이동평균선 값이 Nan이면 제외하자
        d = d.dropna(subset=[f"{max(return_intervals)}{suffix}"])
        out[key] = d

    return out


def align_dfs_by_date_intersection(
    dfs: dict,
    date_col: str = "Date"
) -> dict:
    """
    dfs(dict)의 각 DataFrame을 Date 컬럼 기준 교집합으로 정렬

    Parameters
    ----------
    dfs : dict
        { 'AAPL': df, 'MSFT': df, ... }
    date_col : str
        날짜 컬럼명 (기본: "Date")

    Returns
    -------
    dict
        Date 교집합만 남긴 DataFrame dict
    """

    if not dfs:
        return {}

    # 1️⃣ 모든 df의 Date를 set으로 수집
    date_sets = []

    for df in dfs.values():
        if date_col not in df.columns:
            raise KeyError(f"'{date_col}' 컬럼이 없습니다.")

        s = pd.to_datetime(df[date_col]).dropna().unique()
        date_sets.append(set(s))

    # 2️⃣ Date 교집합
    common_dates = set.intersection(*date_sets)

    if not common_dates:
        raise ValueError("공통 Date가 없습니다.")

    # 3️⃣ 각 df 필터링
    out = {}

    for key, df in dfs.items():
        d = df.copy()
        d[date_col] = pd.to_datetime(d[date_col])

        d = (
            d[d[date_col].isin(common_dates)]
              .sort_values(date_col)
              .reset_index(drop=True)
        )

        out[key] = d

    return out


def merge_dfs_to_df(dfs: dict, input_df: pd.DataFrame) -> dict:
    """
    dfs 딕셔너리의 각 df에 input_df를 병합하기
    ex. 환율 같은 데이터 각 열에 추가할 때 사용
    """

    def normalize_date(df, col="Date"):
        d = df.copy()
        d[col] = pd.to_datetime(d[col])

        # timezone 있으면 제거
        if d[col].dt.tz is not None:
            d[col] = d[col].dt.tz_localize(None)

        return d

    # input_df 정리
    idf = normalize_date(input_df)
    idf = idf.sort_values("Date")

    out = {}

    for key, df in dfs.items():
        d = normalize_date(df)
        d = d.sort_values("Date")

        d = pd.merge(
            d,
            idf,
            on="Date",
            how="left"
        )

        out[key] = d

    return out


def drop_columns(dfs:dict, drop_cols) -> dict:
    """
        특정 컬럼 제거
    """
    
    if isinstance(drop_cols, str):
        drop_cols = [drop_cols]
    
    out ={}
    
    for key, df in dfs.items():
        d = df.copy()
        d = d.drop(columns=drop_cols)

        out[key] =d

    return out


def add_avg_score(
    dfs:dict,
    return_cols = ("1MReturn", "3MReturn", "6MReturn", "12MReturn"),
    out_col ="Avg Score",
) -> dict:

    out = {}
    for key, df in dfs.items():
        d = df.copy()

        missing = [c for c in return_cols if c not in d.columns]
        if missing:
            raise KeyError(f"다음 컬럼이 없습니다 : {missing}")

        d[out_col] = d[list(return_cols)].mean(axis=1)
        out[key] = d

    return out


def select_rows_by_interval_with_ends(
    dfs:dict,
    interval:int
)-> dict:
    """
    interval 간격으로 row 선택하되,
    첫 row와 마지막 row는 반드시 포함
    """
    if interval <= 0:
        raise ValueError("interval은 1이상의 정수여야 합니다")
    
    out = {}
    for key, df in dfs.items():
        d = df.copy()

        n = len(df)
        if n == 0:
            out[key] = d
            continue

        idx = list(range(0, n, interval))
        
        if (n-1) not in idx:
            idx.append(n-1)

        d = d.iloc[idx].reset_index(drop=True)
        out[key] = d

    return out