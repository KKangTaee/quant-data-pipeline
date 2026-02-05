# performance.py
import pandas as pd
import numpy as np

def portfolio_performance_summary(
    result: pd.DataFrame,
    name: str,
    freq: str = "Y"   # "Y", "M", "D"
) -> pd.DataFrame:

    freq_map = {
        "Y": 1,
        "M": 12,
        "D": 252
    }

    if freq not in freq_map:
        raise ValueError("freq는 'Y', 'M', 'D' 중 하나여야 합니다.")

    ann_factor = freq_map[freq]

    df = result.sort_values("Date")

    start_date = df["Date"].iloc[0]
    end_date = df["Date"].iloc[-1]
    # tickers = df["Ticker"].iloc[0]

    start_balance = df["Total Balance"].iloc[0]
    end_balance = df["Total Balance"].iloc[-1]

    years = (end_date - start_date).days / 365.25

    returns = df["Total Return"].dropna()

    # --------------------
    # Annualized Metrics
    # --------------------
    cagr = (end_balance / start_balance) ** (1 / years) - 1

    mean_ann = returns.mean() * ann_factor
    std_ann = returns.std() * np.sqrt(ann_factor)

    sharpe = np.nan if std_ann == 0 else mean_ann / std_ann

    # --------------------
    # Maximum Drawdown
    # --------------------
    balance = df["Total Balance"]
    drawdown = balance / balance.cummax() - 1
    mdd = drawdown.min()

    # --------------------
    # Output (1 Row)
    # --------------------
    return pd.DataFrame([{
        "Name": name,
        # "Ticker": tickers,
        "Start Date": start_date,
        "End Date": end_date,
        "Start Balance": start_balance,
        "End Balance": end_balance,
        "CAGR": cagr,
        "Standard Deviation": std_ann,
        "Sharpe Ratio": sharpe,
        "Maximum Drawdown": mdd
    }])
