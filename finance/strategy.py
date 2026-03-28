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


def risk_parity_trend(
    dfs: dict,
    start_balance: float,
    rebalance_interval: int = 1,
    vol_window: int = 6,        # 변동성 계산 window (월말 데이터면 6 = 6개월)
    filter_ma: str = "MA200",   # 트렌드 필터 컬럼명
) -> pd.DataFrame:
    """
    Risk Parity(1/vol) + Trend Filter 전략

    - 각 시점에서 (Close >= filter_ma) 만족하는 자산만 투자 대상으로 선택
    - 투자 대상들에 대해 최근 vol_window 기간 수익률 표준편차(rolling std)로 변동성 계산
    - 가중치 = (1/vol) 정규화
    - 리밸런싱 주기(rebalance_interval)마다 목표 비중으로 재조정
    - 조건 만족 자산이 0개면 전액 현금
    """

    tickers = list(dfs.keys())
    base_df = dfs[tickers[0]].sort_values("Date").reset_index(drop=True)
    dates = base_df["Date"]

    # 수익률/변동성 계산을 위해 Close 행렬 구성 (shape: [T, N])
    closes_mat = np.column_stack([dfs[t].sort_values("Date").reset_index(drop=True)["Close"].values for t in tickers])

    # 간단 수익률 (T, N)
    rets_mat = (closes_mat[1:] / closes_mat[:-1]) - 1
    rets_mat = np.vstack([np.full((1, rets_mat.shape[1]), np.nan), rets_mat])

    rows = []

    prev_total_balance = None
    prev_close = None

    # 현재 들고 있는 포지션 정보
    held_ticker_idx = []   # 투자중인 티커 index들
    next_balances = []     # 투자중인 자산들에 배분된 금액들
    cash = 0.0

    for i, date in enumerate(dates):
        closes = closes_mat[i].tolist()

        # =========================
        # 1) End Balance / Total Return
        # =========================
        if i == 0:
            end_balances = []
            total_balance = start_balance
            total_return = np.nan
        else:
            # 보유 자산 수익률만 적용
            if held_ticker_idx:
                asset_returns = [ (closes[j] / prev_close[j]) - 1 for j in held_ticker_idx ]
                end_balances = [ b * (1 + r) for b, r in zip(next_balances, asset_returns) ]
            else:
                end_balances = []

            total_balance = float(sum(end_balances) + cash)
            total_return = np.nan if prev_total_balance is None else (total_balance / prev_total_balance) - 1

        # =========================
        # 2) Rebalance? (다음 기간 목표 비중 산출)
        # =========================
        rebalancing = (i == 0) or (i % rebalance_interval == 0)

        # i == 0이면 start_balance로, 아니면 total_balance 기준으로 다음 배분 결정
        base_balance = start_balance if i == 0 else total_balance

        if rebalancing:
            # (A) 트렌드 필터 통과 자산 선정
            # filter_ma 컬럼이 각 df에 존재한다고 가정 (engine.add_ma로 생성)
            eligible = []
            for j, t in enumerate(tickers):
                ma_val = dfs[t].iloc[i].get(filter_ma, np.nan)
                if pd.notna(ma_val) and closes[j] >= float(ma_val):
                    eligible.append(j)

            # (B) 변동성 계산: 최근 vol_window 기간 rolling std
            # i 기준으로 과거 vol_window개 수익률 필요
            vols = {}
            for j in eligible:
                start_idx = max(0, i - vol_window + 1)
                window = rets_mat[start_idx:i+1, j]
                window = window[~np.isnan(window)]
                if len(window) < max(2, vol_window // 2):  # 너무 짧으면 제외(완화 가능)
                    continue
                v = float(np.std(window, ddof=1))
                if v > 0:
                    vols[j] = v

            # (C) 가중치 = 1/vol 정규화
            if vols:
                inv = {j: 1.0 / v for j, v in vols.items()}
                s = sum(inv.values())
                weights = {j: inv[j] / s for j in inv}
                held_ticker_idx = list(weights.keys())

                next_balances = [base_balance * weights[j] for j in held_ticker_idx]
                cash = base_balance - sum(next_balances)
                next_weights = [weights[j] for j in held_ticker_idx]
                next_tickers = [tickers[j] for j in held_ticker_idx]
            else:
                held_ticker_idx = []
                next_balances = []
                cash = base_balance
                next_weights = []
                next_tickers = []
        else:
            # 리밸런싱이 아니면, 그대로 보유(현금/보유자산 유지)
            next_weights = np.nan
            next_tickers = [tickers[j] for j in held_ticker_idx]

        end_tickers = [tickers[j] for j in held_ticker_idx] if i != 0 else np.nan

        rows.append({
            "Date": date,
            "End Ticker": end_tickers,
            "Next Ticker": next_tickers,
            "Next Weight": next_weights,
            "End Balance": end_balances,
            "Next Balance": next_balances,
            "Cash": float(cash),
            "Total Balance": float(total_balance),
            "Total Return": float(total_return) if pd.notna(total_return) else total_return,
            "Rebalancing": rebalancing
        })

        prev_close = closes
        prev_total_balance = total_balance

    return pd.DataFrame(rows)


def dual_momentum(
    dfs: dict,
    start_balance: float,
    top: int = 1,
    lookback_col: str = "12MReturn",
    filter_ma: str = "MA200",
    rebalance_interval: int = 1,
    cash_ticker: str | None = None,   # 예: "BIL" or "SHY" (없으면 '현금 고정')
) -> pd.DataFrame:
    """
    Dual Momentum + Trend Filter 전략

    로직
      1) risky 자산들 중 lookback_col (예: 12MReturn) 기준 top N 선택
      2) 선택된 자산 중 Close >= filter_ma 인 것만 편입
      3) 편입 자산이 0개면 현금(또는 cash_ticker) 보유
      4) rebalance_interval마다 리밸런싱(월말 데이터면 1 추천)

    주의
      - dfs는 engine에서 align_dates(), reset_index까지 끝난 상태를 가정
      - lookback_col, filter_ma 컬럼이 dfs의 각 df에 존재해야 함
        (engine 체이닝: .add_ma(200), .add_interval_returns([12]) 등)
    """

    tickers = list(dfs.keys())

    if cash_ticker is not None and cash_ticker not in tickers:
        raise ValueError(f"cash_ticker='{cash_ticker}'가 dfs에 없습니다. tickers={tickers}")

    # risky universe = cash_ticker 제외
    risky_tickers = [t for t in tickers if t != cash_ticker]
    if len(risky_tickers) == 0:
        raise ValueError("risky_tickers가 비었습니다. cash_ticker만 있는 상태입니다.")

    base_df = dfs[risky_tickers[0]].sort_values("Date").reset_index(drop=True)
    dates = base_df["Date"].tolist()

    # 보유 상태
    held = []            # 보유 티커 리스트
    next_balances = []   # 보유 티커별 다음 투자금
    cash = 0.0

    prev_total_balance = None
    prev_close = {t: None for t in tickers}

    rows = []

    for i, date in enumerate(dates):
        # 현재가/지표 로드
        close_now = {}
        score_now = {}
        ma_now = {}

        for t in tickers:
            df = dfs[t].sort_values("Date").reset_index(drop=True)
            row = df.iloc[i]

            close_now[t] = float(row["Close"])
            score_now[t] = float(row[lookback_col]) if pd.notna(row.get(lookback_col, np.nan)) else np.nan
            ma_now[t] = float(row[filter_ma]) if pd.notna(row.get(filter_ma, np.nan)) else np.nan

        # =========================
        # 1) End Balance / Total Return
        # =========================
        if i == 0:
            end_balances = []
            total_balance = float(start_balance)
            total_return = np.nan
        else:
            # 보유 자산 평가
            end_balances = []
            if held:
                for t, b in zip(held, next_balances):
                    pc = prev_close[t]
                    r = (close_now[t] / pc) - 1 if (pc is not None and pc != 0) else 0.0
                    end_balances.append(b * (1 + r))

            # 현금(또는 cash_ticker 기반 현금 수익률 적용)
            if cash_ticker is not None and cash > 0 and prev_close[cash_ticker] is not None:
                r_cash = (close_now[cash_ticker] / prev_close[cash_ticker]) - 1
                cash = cash * (1 + r_cash)

            total_balance = float(sum(end_balances) + cash)
            total_return = np.nan if prev_total_balance is None else (total_balance / prev_total_balance) - 1

        # =========================
        # 2) Next Allocation (Rebalance)
        # =========================
        rebalancing = (i == 0) or (i % rebalance_interval == 0)
        base_balance = float(start_balance if i == 0 else total_balance)

        if rebalancing:
            # 2-1) risky 중 모멘텀 top N 선택
            risky_scores = [(t, score_now[t]) for t in risky_tickers if pd.notna(score_now[t])]
            risky_scores.sort(key=lambda x: x[1])
            picked = [t for t, _ in risky_scores[-top:]][::-1]  # 높은 점수부터

            # 2-2) 트렌드 필터 통과만 투자
            invest = [t for t in picked if pd.notna(ma_now[t]) and close_now[t] >= ma_now[t]]

            if len(invest) == 0:
                # 전부 현금(또는 cash_ticker)
                held = []
                next_balances = []
                cash = base_balance
            else:
                # 동일가중 (공격형 기본)
                w = 1.0 / len(invest)
                held = invest
                next_balances = [base_balance * w] * len(invest)
                cash = base_balance - sum(next_balances)
        else:
            # 리밸런싱 아니면 그대로 유지
            pass

        rows.append({
            "Date": date,
            "End Ticker": (np.nan if i == 0 else held),
            "Next Ticker": held,
            "End Balance": (np.nan if i == 0 else end_balances),
            "Next Balance": next_balances,
            "Cash": float(cash),
            "Total Balance": float(total_balance),
            "Total Return": total_return,
            "Rebalancing": rebalancing,
        })

        # prev update
        for t in tickers:
            prev_close[t] = close_now[t]
        prev_total_balance = total_balance

    return pd.DataFrame(rows)



#-------------------
# 전략
#-------------------

class Strategy(ABC):

    @abstractmethod
    def run(self, dfs: dict) -> object:
        pass


def _rank_quality_snapshot(
    snapshot_df: pd.DataFrame,
    *,
    quality_factors: list[str],
    lower_is_better_factors: list[str] | None = None,
) -> pd.DataFrame:
    if snapshot_df is None or snapshot_df.empty:
        return pd.DataFrame()

    lower_is_better = set(lower_is_better_factors or [])
    required = {"symbol", *quality_factors}
    missing = required.difference(snapshot_df.columns)
    if missing:
        raise ValueError(f"quality snapshot is missing required columns: {sorted(missing)}")

    ranked = snapshot_df.copy()
    ranked["symbol"] = ranked["symbol"].astype(str).str.strip().str.upper()

    for factor in quality_factors:
        ranked[factor] = pd.to_numeric(ranked[factor], errors="coerce")

    ranked = ranked.dropna(subset=quality_factors).reset_index(drop=True)
    if ranked.empty:
        return ranked

    score_columns = []
    for factor in quality_factors:
        base = -ranked[factor] if factor in lower_is_better else ranked[factor]
        score_col = f"{factor}_score"
        ranked[score_col] = base.rank(method="average", pct=True, ascending=True)
        score_columns.append(score_col)

    ranked["Quality Score"] = ranked[score_columns].mean(axis=1)
    return ranked.sort_values(["Quality Score", "symbol"], ascending=[False, True]).reset_index(drop=True)


def quality_snapshot_equal_weight(
    price_dfs: dict,
    snapshot_by_date: dict,
    *,
    start_balance: float,
    quality_factors: list[str],
    top_n: int = 10,
    lower_is_better_factors: list[str] | None = None,
    rebalance_interval: int = 1,
    trend_filter_enabled: bool = False,
    trend_filter_window: int = 200,
    trend_filter_col: str | None = None,
) -> pd.DataFrame:
    """
    Monthly snapshot-based quality strategy.

    - rebalance date마다 quality snapshot을 조회해 top N을 선택
    - 선택된 종목을 동일가중으로 다음 구간 동안 보유
    - first-pass는 price-only engine을 억지로 확장하지 않고,
      runtime connection layer가 만든 snapshot payload를 직접 사용한다
    """
    if not price_dfs:
        raise ValueError("price_dfs is empty.")
    if not quality_factors:
        raise ValueError("quality_factors must not be empty.")
    if top_n <= 0:
        raise ValueError("top_n must be positive.")
    if rebalance_interval <= 0:
        raise ValueError("rebalance_interval must be positive.")
    if trend_filter_enabled and trend_filter_window <= 0:
        raise ValueError("trend_filter_window must be positive when trend filter is enabled.")

    tickers = list(price_dfs.keys())
    base_df = price_dfs[tickers[0]].sort_values("Date").reset_index(drop=True)
    dates = pd.to_datetime(base_df["Date"]).tolist()
    active_trend_col = trend_filter_col or f"MA{trend_filter_window}"

    prev_close: dict[str, float | None] = {ticker: None for ticker in tickers}
    prev_total_balance = None
    held_tickers: list[str] = []
    next_balances: list[float] = []
    cash = 0.0

    rows = []

    for i, date in enumerate(dates):
        current_date = pd.to_datetime(date)
        close_now = {}
        trend_now = {}
        for ticker in tickers:
            current_row = price_dfs[ticker].iloc[i]
            close_value = pd.to_numeric(current_row["Close"], errors="coerce")
            close_now[ticker] = float(close_value) if pd.notna(close_value) else np.nan
            if trend_filter_enabled:
                trend_value = pd.to_numeric(current_row.get(active_trend_col), errors="coerce")
                trend_now[ticker] = float(trend_value) if pd.notna(trend_value) else np.nan

        if i == 0:
            end_balances = []
            total_balance = float(start_balance)
            total_return = np.nan
        else:
            end_balances = []
            for ticker, balance in zip(held_tickers, next_balances):
                prev = prev_close.get(ticker)
                current_close = close_now.get(ticker)
                if prev is None or pd.isna(prev) or prev == 0 or pd.isna(current_close):
                    asset_return = 0.0
                else:
                    asset_return = (current_close / prev) - 1
                end_balances.append(balance * (1 + asset_return))

            total_balance = float(sum(end_balances) + cash)
            total_return = np.nan if prev_total_balance is None else (total_balance / prev_total_balance) - 1

        rebalancing = (i == 0) or (i % rebalance_interval == 0)
        base_balance = float(start_balance if i == 0 else total_balance)
        snapshot_key = current_date.normalize()
        selected_snapshot = pd.DataFrame()
        selected_scores: list[float] = []
        raw_selected_tickers: list[str] = []
        raw_selected_scores: list[float] = []
        overlay_rejected_tickers: list[str] = []

        if rebalancing:
            snapshot_df = snapshot_by_date.get(snapshot_key)
            ranked = _rank_quality_snapshot(
                snapshot_df if snapshot_df is not None else pd.DataFrame(),
                quality_factors=quality_factors,
                lower_is_better_factors=lower_is_better_factors,
            )
            if not ranked.empty:
                available_tickers = {
                    ticker for ticker in tickers
                    if pd.notna(close_now.get(ticker))
                }
                ranked = ranked[ranked["symbol"].isin(available_tickers)].reset_index(drop=True)

            if ranked.empty:
                held_tickers = []
                next_balances = []
                cash = base_balance
            else:
                selected_snapshot = ranked.head(min(top_n, len(ranked))).reset_index(drop=True)
                raw_selected_tickers = selected_snapshot["symbol"].tolist()
                raw_selected_scores = selected_snapshot["Quality Score"].astype(float).tolist()

                if trend_filter_enabled:
                    passed_mask = []
                    for symbol in raw_selected_tickers:
                        current_close = close_now.get(symbol)
                        current_trend = trend_now.get(symbol)
                        passed_mask.append(
                            pd.notna(current_close)
                            and pd.notna(current_trend)
                            and float(current_close) >= float(current_trend)
                        )
                    filtered_snapshot = selected_snapshot[passed_mask].reset_index(drop=True)
                    overlay_rejected_tickers = [
                        symbol for symbol, passed in zip(raw_selected_tickers, passed_mask) if not passed
                    ]
                    selected_snapshot = filtered_snapshot

                held_tickers = selected_snapshot["symbol"].tolist()
                selected_scores = selected_snapshot["Quality Score"].astype(float).tolist()
                if not held_tickers:
                    next_balances = []
                    cash = base_balance
                else:
                    allocation = base_balance / len(held_tickers)
                    next_balances = [allocation] * len(held_tickers)
                    cash = base_balance - sum(next_balances)

        rows.append(
            {
                "Date": current_date,
                "End Ticker": (np.nan if i == 0 else held_tickers),
                "Next Ticker": held_tickers,
                "Raw Selected Ticker": raw_selected_tickers,
                "Raw Selected Count": len(raw_selected_tickers),
                "Raw Selected Score": raw_selected_scores,
                "Overlay Rejected Ticker": overlay_rejected_tickers,
                "Overlay Rejected Count": len(overlay_rejected_tickers),
                "Trend Filter Enabled": trend_filter_enabled,
                "Trend Filter Column": (active_trend_col if trend_filter_enabled else np.nan),
                "End Balance": (np.nan if i == 0 else end_balances),
                "Next Balance": next_balances,
                "Cash": float(cash),
                "Selected Count": len(held_tickers),
                "Selected Score": selected_scores,
                "Total Balance": float(total_balance),
                "Total Return": total_return,
                "Rebalancing": rebalancing,
            }
        )

        prev_close = close_now
        prev_total_balance = total_balance

    return pd.DataFrame(rows)


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


class RiskParityTrendStrategy(Strategy):
    def __init__(
        self,
        start_balance: float,
        rebalance_interval: int = 1,
        vol_window: int = 6,
        filter_ma: str = "MA200",
    ):
        self.start_balance = start_balance
        self.rebalance_interval = rebalance_interval
        self.vol_window = vol_window
        self.filter_ma = filter_ma

    def run(self, dfs: dict) -> pd.DataFrame:
        return risk_parity_trend(
            dfs=dfs,
            start_balance=self.start_balance,
            rebalance_interval=self.rebalance_interval,
            vol_window=self.vol_window,
            filter_ma=self.filter_ma,
        )


class DualMomentumStrategy(Strategy):
    def __init__(
        self,
        start_balance: float,
        top: int = 1,
        lookback_col: str = "12MReturn",
        filter_ma: str = "MA200",
        rebalance_interval: int = 1,
        cash_ticker: str | None = None,
    ):
        self.start_balance = start_balance
        self.top = top
        self.lookback_col = lookback_col
        self.filter_ma = filter_ma
        self.rebalance_interval = rebalance_interval
        self.cash_ticker = cash_ticker

    def run(self, dfs: dict) -> pd.DataFrame:
        return dual_momentum(
            dfs=dfs,
            start_balance=self.start_balance,
            top=self.top,
            lookback_col=self.lookback_col,
            filter_ma=self.filter_ma,
            rebalance_interval=self.rebalance_interval,
            cash_ticker=self.cash_ticker,
        )
