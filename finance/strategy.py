import pandas as pd
import numpy as np

from abc import ABC, abstractmethod

"""
    3️⃣ strategy.py — Decision & Simulation Layer
    📌 역할
        * 투자 의사결정
        * 시간 흐름을 따라가는 시뮬레이션

    📦 포함 함수
        * equal_weight_strategy
        * gtaa3
"""


def equal_weight(
    dfs: dict,
    start_balance: float,
    rebalance_interval: int,
) -> pd.DataFrame:
    """
        균등 전략
            * dfs 의 자산에 균등하게 배분하는 전략
            * rebalance_interval 간격마다 리벨런싱

        Params
            * dfs : 데이터 딕셔너리 정보 ex { "AMD" : df, ... }
            * start_balance : 초기 투자금
            * rebalance_interval : 리벨런싱 기간
    """

    tickers = list(dfs.keys())
    n_assets = len(tickers)

    base_df = dfs[tickers[0]].sort_values("Date").reset_index(drop=True)
    dates = base_df["Date"]

    rows = []

    prev_close = None
    prev_end_balance = None
    prev_total_balance = None
    for i, date in enumerate(dates):

        closes = [dfs[t].iloc[i]["Close"] for t in tickers]

        # =========================
        # Return & End Balance
        # =========================
        end_balances = []
        total_return = 0
        total_balance = 0
        
        if i == 0:
            returns = [np.nan] * n_assets
            end_balances = [0] * n_assets
            total_balance = start_balance
        else:
            returns = [(c / pc) - 1 for c, pc in zip(closes, prev_close)]
            end_balances = [
                nb * (1 + r) for nb, r in zip(next_balances, returns)
            ]

            total_balance = sum(end_balances)
            total_return = (
                np.nan if i == 0
                else (total_balance / prev_total_balance) - 1
            )


        # =========================
        # Next Balance
        # =========================
        if i == 0:
            next_balances = [start_balance / n_assets] * n_assets
            rebalancing = True
        else:
            rebalancing = (i % rebalance_interval == 0)

            if rebalancing:
                next_balances = [total_balance / n_assets] * n_assets
            else:
                next_balances = end_balances.copy()

        
        rows.append({
            "Date": date,
            "Ticker": tickers,
            "Close": closes,
            "Next Balance": next_balances,
            "End Balance": end_balances,
            "Return": returns,
            "Total Balance": total_balance,
            "Total Return": total_return,
            "Rebalancing": rebalancing
        })

        prev_close = closes
        prev_end_balance = end_balances
        prev_total_balance = total_balance

    return pd.DataFrame(rows)



def gtaa3(dfs:dict, start_balance:int, top:int, filter_ma:str) ->dict:
    """
        gtaa3 전략
            * dfs 에서 평균 수익률 이 높은  top개를 뽑음
            * 뽑아진 top 자산의 가격 > 이동평균 값(filter_ma) 인 경우
            * 자산의 가격 < 이동평균 값(filter_ma) 인 자신은 포함하지 않고, 현금 보유
            * 예시 
                1. SPY, TLT, GLD 이렇게 3개가 top 수익률로 뽑힘.
                2. 각각의 종가 데이터(Close)는 [200, 100, 50]
                3. 각각의 이평선 값은 [150, 110, 40]
                4. SPY, GLD에만 투자하고, 나머지는 현금으로 보유

        Params
            * top : 가장 높은 값 몇개를 추출
            * filter_ma : 어떤 이동평균과 현재 값을 비교할건지
    """

    tickers = list(dfs.keys())
    n_assets = top

    base_df = dfs[tickers[0]].sort_values("Date").reset_index(drop=True)
    dates = base_df["Date"]

    rows = []

    prev_close = None
    prev_total_balance = None
    end_ticker_to_index = None
    cash = 0

    for i, date in enumerate(dates):

        closes = [dfs[t].iloc[i]["Close"] for t in tickers]
        scores = [dfs[t].iloc[i]['Avg Score'] for t in tickers]
        mas = [dfs[t].iloc[i][filter_ma] for t in tickers]

        top_idx = np.argsort(scores)[-n_assets:][::-1]
        next_ticker = [tickers[i] for i in top_idx]

        # 필터 후 결정된 티커들만 수집
        next_ticker_to_index = [
            (ticker, idx)
            for ticker, idx in zip(next_ticker, top_idx)
            if closes[idx] >= mas[idx]
        ]

        # =========================
        # Return & End Balance
        # =========================
        end_balances = []
        total_return = 0
        total_balance = 0
        
        
        if i == 0:
            returns = [np.nan] * n_assets
            end_balances = [0] * n_assets
            total_balance = start_balance
        else:
            returns = [(c / pc) - 1 for c, pc in zip(closes, prev_close)]
            end_ticker_return = [returns[idx] for _, idx in end_ticker_to_index]

            end_balances = [
                nb * (1 + r) for nb, r in zip(next_balances, end_ticker_return)
            ]

            total_balance = sum(end_balances) + cash
            total_return = (
                np.nan if i == 0
                else (total_balance / prev_total_balance) - 1
            )


        # =========================
        # Next Balance
        # =========================
        base_balance = start_balance if i == 0 else total_balance
        bal = round(base_balance / n_assets, 1)

        next_balances = [bal] * len(next_ticker_to_index)
        cash = bal * (n_assets - len(next_ticker_to_index))

        end_tickers = (
            [t for t, _ in end_ticker_to_index]
            if isinstance(end_ticker_to_index, (list, tuple))
            else np.nan
        )
        
        rows.append({
            "Date": date,
            # "Ticker": tickers,
            "End Ticker" : end_tickers,
            "Next Ticker" : [t for t,_ in next_ticker_to_index],
            # "Close": closes,
            "End Balance": end_balances,
            "Next Balance": next_balances,
            "Cash" : int(cash),
            # "Return": returns,
            "Total Balance": total_balance,
            "Total Return": total_return, 
        })

        prev_close = closes
        end_ticker_to_index = next_ticker_to_index
        prev_total_balance = total_balance

    return pd.DataFrame(rows)



#-------------------
# 전략
#-------------------

class Strategy(ABC):

    @abstractmethod
    def run(self, dfs: dict) -> object:
        pass


class EqualWeightStrategy(Strategy):

    def __init__(self, start_balance: float, rebalance_interval: int):
        self.start_balance = start_balance
        self.rebalance_interval = rebalance_interval

    def run(self, dfs: dict) -> pd.DataFrame:
        return equal_weight(
            dfs,
            self.start_balance,
            self.rebalance_interval
        )


class GTAA3Strategy(Strategy):

    def __init__(self, start_balance: int, top: int, filter_ma: str):
        self.start_balance = start_balance
        self.top = top
        self.filter_ma = filter_ma

    def run(self, dfs: dict) -> pd.DataFrame:
        return gtaa3(
            dfs,
            self.start_balance,
            self.top,
            self.filter_ma
        )