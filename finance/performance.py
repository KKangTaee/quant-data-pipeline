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



def make_monthly_weighted_portfolio(
    dfs,
    ratios=None,
    names=None,
    date_col="Date",
    balance_col="Total Balance",
    return_col="Total Return",
    out_label_col="Portfolio",
    return_method="from_balance",   # "from_balance" | "weighted_returns"
    date_policy="union",            # "union" | "intersection"
):
    if not isinstance(dfs, (list, tuple)) or len(dfs) == 0:
        raise ValueError("dfs는 1개 이상 DataFrame을 담은 리스트/튜플이어야 합니다.")

    n = len(dfs)

    if ratios is None:
        ratios = [1 / n] * n
    if len(ratios) != n:
        raise ValueError("ratios 길이는 dfs 개수와 같아야 합니다.")

    ratios = np.array(ratios, dtype=float)
    if np.any(ratios < 0):
        raise ValueError("ratios에는 음수가 들어갈 수 없습니다.")
    if ratios.sum() == 0:
        raise ValueError("ratios 합이 0입니다.")
    ratios = ratios / ratios.sum()

    if names is None:
        names = [f"portfolio{i+1}" for i in range(n)]
    if len(names) != n:
        raise ValueError("names 길이는 dfs 개수와 같아야 합니다.")

    pct = (ratios * 100).round().astype(int)
    portfolio_label = "+".join([f"{nm}({p})" for nm, p in zip(names, pct)])

    monthly_balances = []
    monthly_returns = []

    for df, nm in zip(dfs, names):
        tmp = df.copy()
        tmp[date_col] = pd.to_datetime(tmp[date_col])

        tmp["_month"] = tmp[date_col].dt.to_period("M")
        m = tmp.groupby("_month", as_index=False).agg(
            TotalBalance=(balance_col, "mean"),
            TotalReturn=(return_col, "mean") if return_col in tmp.columns else (balance_col, lambda s: np.nan),
        )
        m[date_col] = m["_month"].dt.to_timestamp("M")
        m = m.drop(columns=["_month"]).set_index(date_col).sort_index()

        monthly_balances.append(m[["TotalBalance"]].rename(columns={"TotalBalance": nm}))
        monthly_returns.append(m[["TotalReturn"]].rename(columns={"TotalReturn": nm}))

    # 여기서 union / intersection 결정
    join_how = "outer" if date_policy == "union" else "inner"
    if date_policy not in ("union", "intersection"):
        raise ValueError("date_policy는 'union' 또는 'intersection'만 가능합니다.")

    bal_wide = pd.concat(monthly_balances, axis=1, join=join_how).sort_index()
    ret_wide = pd.concat(monthly_returns, axis=1, join=join_how).sort_index()

    w = pd.Series(ratios, index=names)

    if date_policy == "union":
        # union일 때는 기존처럼 있는 것만으로 재정규화
        denom = bal_wide.notna().mul(w, axis=1).sum(axis=1)
        weighted_balance = bal_wide.mul(w, axis=1).sum(axis=1) / denom.replace(0, np.nan)

        if return_method == "weighted_returns":
            denom_r = ret_wide.notna().mul(w, axis=1).sum(axis=1)
            weighted_return = ret_wide.mul(w, axis=1).sum(axis=1) / denom_r.replace(0, np.nan)
        else:  # from_balance
            weighted_return = weighted_balance.pct_change()
            weighted_return.iloc[0] = 0.0

    else:
        # intersection이면 모든 df가 값이 있는 달만 남으니 그냥 가중합
        weighted_balance = bal_wide.mul(w, axis=1).sum(axis=1)

        if return_method == "weighted_returns":
            weighted_return = ret_wide.mul(w, axis=1).sum(axis=1)
        else:
            weighted_return = weighted_balance.pct_change()
            weighted_return.iloc[0] = 0.0

    out = pd.DataFrame({
        date_col: weighted_balance.index,
        out_label_col: portfolio_label,
        "Total Balance": weighted_balance.values,
        "Total Return": weighted_return.values,
    }).reset_index(drop=True)

    return out