import pandas as pd
import numpy as np

"""
    4️⃣ display.py — Presentation Layer
    📌 역할
        * 사람이 보기 좋게 만드는 단계
        * 분석 결과 표현 전용

    📦 포함 함수
        * round_columns
        * style_returns
"""


def round_columns(
    df: pd.DataFrame,
    cols: list,
    decimals: int = 1
) -> pd.DataFrame:
    """
    리스트 컬럼 + 스칼라 컬럼 내부 float 값을 반올림 (display용)

    - list / tuple  → 요소별 round
    - float / int  → 단일 round
    - NaN          → 유지
    """
    d = df.copy()

    def _round_value(val):
        # list or tuple - 먼저 체크 (배열에 pd.isna() 사용하면 에러)
        if isinstance(val, (list, tuple)):
            return [
                round(x, decimals) if pd.notna(x) else x
                for x in val
            ]
        
        # numpy array
        if isinstance(val, np.ndarray):
            return np.array([
                round(x, decimals) if pd.notna(x) else x
                for x in val
            ])

        # NaN 체크는 스칼라에만 적용
        if pd.isna(val):
            return val

        # scalar number
        if isinstance(val, (int, float, np.number)):
            return round(val, decimals)

        # others
        return val

    for col in cols:
        if col in d.columns:
            d[col] = d[col].apply(_round_value)

    return d


def style_returns(df, column: str):

    def color_return(val):
        if pd.isna(val):
            return ""
        if val > 0:
            return "color: red;"
        if val < 0:
            return "color: #3434ff;"
        return ""

    def clean_for_display(df):
        df2 = df.copy()
        for col in df2.columns:
            if df2[col].apply(lambda x: isinstance(x, list)).any():
                df2[col] = df2[col].apply(
                    lambda lst: [float(v) if isinstance(v, np.generic) else v for v in lst]
                    if isinstance(lst, list) else lst
                )
        return df2

    df = clean_for_display(df)

    return (
        df.style
          # ✅ 컬럼별 포맷 지정
          .format({
              "Total Balance": "{:,.1f}",   # ← 소수점 1자리
              column: "{:.2%}"               # Total Return
          })
          # ✅ 색상은 Total Return만
          .map(color_return, subset=[column])
    )