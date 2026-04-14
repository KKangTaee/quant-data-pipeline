import pandas as pd
import numpy as np

from abc import ABC, abstractmethod

"""
3️⃣ strategy.py — Decision & Simulation Layer

이 파일은 현재도 finance 전략의 핵심 simulation / decision 레이어다.

역할:
    * 투자 의사결정
    * 시간 흐름을 따라가는 시뮬레이션
    * rebalance 결과를 result dataframe으로 전개

현재 구조에서의 경계:
    * `finance/sample.py`
        - DB / factor / snapshot 데이터를 strategy 입력 형태로 조립
    * `finance/strategy.py`
        - 실제 strategy simulation 수행
    * `app/web/runtime/backtest.py`
        - 웹앱에서 쓰는 runtime wrapper / bundle / meta 조립
    * `app/web/pages/backtest.py`
        - Streamlit UI / compare / history orchestration

즉 quality / value / quality+value 계열도
UI는 `backtest.py`에서 열리지만,
실제 strategy simulation 경로는 여전히 이 레이어와 sample/runtime 조합에 있다.
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



def gtaa3(
    dfs: dict,
    start_balance: int,
    top: int,
    filter_ma: str,
    min_price: float = 0.0,
    score_col: str = "Avg Score",
    risk_off_mode: str = "cash_only",
    defensive_tickers: list[str] | None = None,
    risk_overlay_df: pd.DataFrame | None = None,
    market_regime_enabled: bool = False,
    market_regime_window: int = 200,
    market_regime_benchmark: str | None = None,
    crash_guardrail_enabled: bool = False,
    crash_guardrail_drawdown_threshold: float = 0.15,
    underperformance_guardrail_enabled: bool = False,
    underperformance_guardrail_window_months: int = 12,
    underperformance_guardrail_threshold: float = -0.10,
    underperformance_guardrail_benchmark: str | None = None,
    underperformance_guardrail_df: pd.DataFrame | None = None,
    drawdown_guardrail_enabled: bool = False,
    drawdown_guardrail_window_months: int = 12,
    drawdown_guardrail_strategy_threshold: float = -0.35,
    drawdown_guardrail_gap_threshold: float = 0.08,
    drawdown_guardrail_benchmark: str | None = None,
    drawdown_guardrail_df: pd.DataFrame | None = None,
) -> dict:
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
    defensive_set = {
        ticker for ticker in (defensive_tickers or [])
        if ticker in tickers
    }

    if risk_off_mode not in {"cash_only", "defensive_bond_preference"}:
        raise ValueError("risk_off_mode must be one of {'cash_only', 'defensive_bond_preference'}.")

    regime_by_date: dict[pd.Timestamp, dict[str, float | str | bool]] = {}
    active_regime_col = f"MA{market_regime_window}"
    if risk_overlay_df is not None and not risk_overlay_df.empty:
        working_overlay = risk_overlay_df.copy()
        working_overlay["Date"] = pd.to_datetime(working_overlay["Date"], errors="coerce")
        working_overlay = working_overlay.dropna(subset=["Date"]).sort_values("Date")
        for _, overlay_row in working_overlay.iterrows():
            overlay_date = pd.Timestamp(overlay_row["Date"]).normalize()
            regime_close = pd.to_numeric(overlay_row.get("Close"), errors="coerce")
            regime_trend = pd.to_numeric(overlay_row.get(active_regime_col), errors="coerce")
            crash_drawdown = pd.to_numeric(overlay_row.get("Crash Drawdown"), errors="coerce")
            regime_by_date[overlay_date] = {
                "close": float(regime_close) if pd.notna(regime_close) else np.nan,
                "trend": float(regime_trend) if pd.notna(regime_trend) else np.nan,
                "crash_drawdown": float(crash_drawdown) if pd.notna(crash_drawdown) else np.nan,
            }

    if underperformance_guardrail_enabled and underperformance_guardrail_df is None:
        raise ValueError("underperformance_guardrail_df is required when GTAA underperformance guardrail is enabled.")
    if drawdown_guardrail_enabled and drawdown_guardrail_df is None:
        raise ValueError("drawdown_guardrail_df is required when GTAA drawdown guardrail is enabled.")

    guardrail_close_by_date = _build_guardrail_close_by_date(
        underperformance_guardrail_df if underperformance_guardrail_enabled else drawdown_guardrail_df
    )
    guardrail_close_history: list[float] = []
    strategy_balance_history: list[float] = []

    base_df = dfs[tickers[0]].sort_values("Date").reset_index(drop=True)
    dates = base_df["Date"]

    rows = []

    prev_close = None
    prev_total_balance = None
    end_ticker_to_index = None
    cash = 0

    for i, date in enumerate(dates):

        closes = [dfs[t].iloc[i]["Close"] for t in tickers]
        scores = [dfs[t].iloc[i][score_col] for t in tickers]
        mas = [dfs[t].iloc[i][filter_ma] for t in tickers]

        top_idx = np.argsort(scores)[-n_assets:][::-1]
        next_ticker = [tickers[i] for i in top_idx]
        raw_selected_tickers = next_ticker.copy()
        raw_selected_scores = [float(scores[idx]) for idx in top_idx]

        # 필터 후 결정된 티커들만 수집
        next_ticker_to_index = [
            (ticker, idx)
            for ticker, idx in zip(next_ticker, top_idx)
            if closes[idx] >= mas[idx] and _passes_min_price(closes[idx], min_price)
        ]
        overlay_rejected_tickers = [ticker for ticker in next_ticker if ticker not in {t for t, _ in next_ticker_to_index}]
        defensive_fill_tickers: list[str] = []

        current_date = pd.to_datetime(date).normalize()
        regime_state = "off"
        regime_close_now = np.nan
        regime_trend_now = np.nan
        crash_drawdown_now = np.nan
        crash_guardrail_triggered = False
        risk_off_reasons: list[str] = []

        overlay_state = regime_by_date.get(current_date)
        if market_regime_enabled:
            if overlay_state is None:
                regime_state = "unknown"
            else:
                regime_close_now = overlay_state["close"]
                regime_trend_now = overlay_state["trend"]
                if pd.notna(regime_close_now) and pd.notna(regime_trend_now):
                    regime_state = "risk_on" if float(regime_close_now) >= float(regime_trend_now) else "risk_off"
                else:
                    regime_state = "unknown"
                if regime_state == "risk_off":
                    risk_off_reasons.append("market_regime")

        if crash_guardrail_enabled:
            if overlay_state is None:
                crash_drawdown_now = np.nan
            else:
                crash_drawdown_now = overlay_state["crash_drawdown"]
                if pd.notna(crash_drawdown_now) and float(crash_drawdown_now) <= -abs(float(crash_guardrail_drawdown_threshold)):
                    crash_guardrail_triggered = True
                    risk_off_reasons.append("crash_guardrail")

        def _build_defensive_candidates(existing_pairs: list[tuple[str, int]]) -> list[tuple[str, int]]:
            if not defensive_set:
                return []
            existing_names = {ticker for ticker, _ in existing_pairs}
            candidate_pairs = [
                (ticker, idx)
                for idx, ticker in enumerate(tickers)
                if ticker in defensive_set and ticker not in existing_names
            ]
            candidate_pairs = [
                (ticker, idx)
                for ticker, idx in candidate_pairs
                if closes[idx] >= mas[idx] and _passes_min_price(closes[idx], min_price)
            ]
            candidate_pairs.sort(key=lambda item: float(scores[item[1]]), reverse=True)
            return candidate_pairs

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

        guardrail_fields = _evaluate_portfolio_guardrails(
            current_date=current_date,
            step_index=i,
            current_total_balance=float(total_balance),
            strategy_balance_history=strategy_balance_history,
            guardrail_close_history=guardrail_close_history,
            guardrail_close_by_date=guardrail_close_by_date,
            underperformance_guardrail_enabled=underperformance_guardrail_enabled,
            underperformance_guardrail_window_months=underperformance_guardrail_window_months,
            underperformance_guardrail_threshold=underperformance_guardrail_threshold,
            underperformance_guardrail_benchmark=underperformance_guardrail_benchmark,
            drawdown_guardrail_enabled=drawdown_guardrail_enabled,
            drawdown_guardrail_window_months=drawdown_guardrail_window_months,
            drawdown_guardrail_strategy_threshold=drawdown_guardrail_strategy_threshold,
            drawdown_guardrail_gap_threshold=drawdown_guardrail_gap_threshold,
            drawdown_guardrail_benchmark=drawdown_guardrail_benchmark,
        )
        guardrail_risk_off = bool(
            guardrail_fields["Underperformance Guardrail Triggered"]
            or guardrail_fields["Drawdown Guardrail Triggered"]
        )
        if bool(guardrail_fields["Underperformance Guardrail Triggered"]):
            risk_off_reasons.append("underperformance_guardrail")
        if bool(guardrail_fields["Drawdown Guardrail Triggered"]):
            risk_off_reasons.append("drawdown_guardrail")

        if guardrail_risk_off:
            next_ticker_to_index = []
        elif risk_off_reasons:
            if risk_off_mode == "defensive_bond_preference":
                next_ticker_to_index = _build_defensive_candidates([])[:n_assets]
                defensive_fill_tickers = [ticker for ticker, _ in next_ticker_to_index]
            else:
                next_ticker_to_index = []
        elif risk_off_mode == "defensive_bond_preference" and len(next_ticker_to_index) < n_assets:
            defensive_candidates = _build_defensive_candidates(next_ticker_to_index)
            slots_left = max(n_assets - len(next_ticker_to_index), 0)
            added_pairs = defensive_candidates[:slots_left]
            next_ticker_to_index = next_ticker_to_index + added_pairs
            defensive_fill_tickers = [ticker for ticker, _ in added_pairs]


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
        
        row = {
            "Date": date,
            # "Ticker": tickers,
            "End Ticker" : end_tickers,
            "Next Ticker" : [t for t,_ in next_ticker_to_index],
            "Raw Selected Ticker": raw_selected_tickers,
            "Raw Selected Score": raw_selected_scores,
            "Overlay Rejected Ticker": overlay_rejected_tickers,
            "Overlay Rejected Count": len(overlay_rejected_tickers),
            "Defensive Fallback Ticker": defensive_fill_tickers,
            "Defensive Fallback Count": len(defensive_fill_tickers),
            "Trend Filter Column": filter_ma,
            "Risk-Off Mode": risk_off_mode,
            "Market Regime Enabled": market_regime_enabled,
            "Market Regime Benchmark": market_regime_benchmark if market_regime_enabled else np.nan,
            "Regime State": regime_state,
            "Regime Close": regime_close_now,
            "Regime Trend": regime_trend_now,
            "Crash Guardrail Enabled": crash_guardrail_enabled,
            "Crash Guardrail Triggered": crash_guardrail_triggered,
            "Crash Drawdown": crash_drawdown_now,
            "Risk-Off Reason": risk_off_reasons,
            # "Close": closes,
            "End Balance": end_balances,
            "Next Balance": next_balances,
            "Cash" : int(cash),
            # "Return": returns,
            "Total Balance": total_balance,
            "Total Return": total_return, 
        }
        row.update(guardrail_fields)
        rows.append(row)

        prev_close = closes
        end_ticker_to_index = next_ticker_to_index
        prev_total_balance = total_balance
        strategy_balance_history.append(float(total_balance))
        guardrail_close_history.append(
            float(guardrail_fields["Underperformance Guardrail Benchmark Close"])
            if pd.notna(guardrail_fields["Underperformance Guardrail Benchmark Close"])
            else np.nan
        )

    return pd.DataFrame(rows)


def _passes_min_price(close_value: float, min_price: float) -> bool:
    threshold = max(float(min_price or 0.0), 0.0)
    return float(close_value) >= threshold


def _passes_min_avg_dollar_volume(
    avg_dollar_volume: float | None,
    min_avg_dollar_volume_20d_m: float,
) -> bool:
    threshold = max(float(min_avg_dollar_volume_20d_m or 0.0), 0.0) * 1_000_000.0
    if threshold <= 0:
        return True
    if avg_dollar_volume is None or pd.isna(avg_dollar_volume):
        return False
    return float(avg_dollar_volume) >= threshold


def risk_parity_trend(
    dfs: dict,
    start_balance: float,
    rebalance_interval: int = 1,
    vol_window: int = 6,        # 변동성 계산 window (월말 데이터면 6 = 6개월)
    filter_ma: str = "MA200",   # 트렌드 필터 컬럼명
    min_price: float = 0.0,
    underperformance_guardrail_enabled: bool = False,
    underperformance_guardrail_window_months: int = 12,
    underperformance_guardrail_threshold: float = -0.10,
    underperformance_guardrail_benchmark: str | None = None,
    underperformance_guardrail_df: pd.DataFrame | None = None,
    drawdown_guardrail_enabled: bool = False,
    drawdown_guardrail_window_months: int = 12,
    drawdown_guardrail_strategy_threshold: float = -0.35,
    drawdown_guardrail_gap_threshold: float = 0.08,
    drawdown_guardrail_benchmark: str | None = None,
    drawdown_guardrail_df: pd.DataFrame | None = None,
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

    if underperformance_guardrail_enabled and underperformance_guardrail_df is None:
        raise ValueError("underperformance_guardrail_df is required when risk parity guardrail is enabled.")
    if drawdown_guardrail_enabled and drawdown_guardrail_df is None:
        raise ValueError("drawdown_guardrail_df is required when risk parity drawdown guardrail is enabled.")
    guardrail_close_by_date = _build_guardrail_close_by_date(
        underperformance_guardrail_df if underperformance_guardrail_enabled else drawdown_guardrail_df
    )
    guardrail_close_history: list[float] = []
    strategy_balance_history: list[float] = []

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
        guardrail_fields = _evaluate_portfolio_guardrails(
            current_date=date,
            step_index=i,
            current_total_balance=float(base_balance),
            strategy_balance_history=strategy_balance_history,
            guardrail_close_history=guardrail_close_history,
            guardrail_close_by_date=guardrail_close_by_date,
            underperformance_guardrail_enabled=underperformance_guardrail_enabled,
            underperformance_guardrail_window_months=underperformance_guardrail_window_months,
            underperformance_guardrail_threshold=underperformance_guardrail_threshold,
            underperformance_guardrail_benchmark=underperformance_guardrail_benchmark,
            drawdown_guardrail_enabled=drawdown_guardrail_enabled,
            drawdown_guardrail_window_months=drawdown_guardrail_window_months,
            drawdown_guardrail_strategy_threshold=drawdown_guardrail_strategy_threshold,
            drawdown_guardrail_gap_threshold=drawdown_guardrail_gap_threshold,
            drawdown_guardrail_benchmark=drawdown_guardrail_benchmark,
        )
        guardrail_risk_off = bool(
            guardrail_fields["Underperformance Guardrail Triggered"]
            or guardrail_fields["Drawdown Guardrail Triggered"]
        )

        if rebalancing:
            if guardrail_risk_off:
                held_ticker_idx = []
                next_balances = []
                cash = base_balance
                next_weights = []
                next_tickers = []
            else:
                # (A) 트렌드 필터 통과 자산 선정
                eligible = []
                for j, t in enumerate(tickers):
                    ma_val = dfs[t].iloc[i].get(filter_ma, np.nan)
                    if (
                        pd.notna(ma_val)
                        and closes[j] >= float(ma_val)
                        and _passes_min_price(closes[j], min_price)
                    ):
                        eligible.append(j)

                # (B) 변동성 계산
                vols = {}
                for j in eligible:
                    start_idx = max(0, i - vol_window + 1)
                    window = rets_mat[start_idx:i+1, j]
                    window = window[~np.isnan(window)]
                    if len(window) < max(2, vol_window // 2):
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

        row = {
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
        }
        row.update(guardrail_fields)
        rows.append(row)

        prev_close = closes
        prev_total_balance = total_balance
        strategy_balance_history.append(float(total_balance))
        guardrail_close_history.append(
            float(guardrail_fields["Underperformance Guardrail Benchmark Close"])
            if pd.notna(guardrail_fields["Underperformance Guardrail Benchmark Close"])
            else np.nan
        )

    return pd.DataFrame(rows)


def dual_momentum(
    dfs: dict,
    start_balance: float,
    top: int = 1,
    lookback_col: str = "12MReturn",
    filter_ma: str = "MA200",
    rebalance_interval: int = 1,
    cash_ticker: str | None = None,   # 예: "BIL" or "SHY" (없으면 '현금 고정')
    min_price: float = 0.0,
    underperformance_guardrail_enabled: bool = False,
    underperformance_guardrail_window_months: int = 12,
    underperformance_guardrail_threshold: float = -0.10,
    underperformance_guardrail_benchmark: str | None = None,
    underperformance_guardrail_df: pd.DataFrame | None = None,
    drawdown_guardrail_enabled: bool = False,
    drawdown_guardrail_window_months: int = 12,
    drawdown_guardrail_strategy_threshold: float = -0.35,
    drawdown_guardrail_gap_threshold: float = 0.08,
    drawdown_guardrail_benchmark: str | None = None,
    drawdown_guardrail_df: pd.DataFrame | None = None,
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

    if underperformance_guardrail_enabled and underperformance_guardrail_df is None:
        raise ValueError("underperformance_guardrail_df is required when dual momentum guardrail is enabled.")
    if drawdown_guardrail_enabled and drawdown_guardrail_df is None:
        raise ValueError("drawdown_guardrail_df is required when dual momentum drawdown guardrail is enabled.")
    guardrail_close_by_date = _build_guardrail_close_by_date(
        underperformance_guardrail_df if underperformance_guardrail_enabled else drawdown_guardrail_df
    )
    guardrail_close_history: list[float] = []
    strategy_balance_history: list[float] = []

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
        guardrail_fields = _evaluate_portfolio_guardrails(
            current_date=date,
            step_index=i,
            current_total_balance=float(base_balance),
            strategy_balance_history=strategy_balance_history,
            guardrail_close_history=guardrail_close_history,
            guardrail_close_by_date=guardrail_close_by_date,
            underperformance_guardrail_enabled=underperformance_guardrail_enabled,
            underperformance_guardrail_window_months=underperformance_guardrail_window_months,
            underperformance_guardrail_threshold=underperformance_guardrail_threshold,
            underperformance_guardrail_benchmark=underperformance_guardrail_benchmark,
            drawdown_guardrail_enabled=drawdown_guardrail_enabled,
            drawdown_guardrail_window_months=drawdown_guardrail_window_months,
            drawdown_guardrail_strategy_threshold=drawdown_guardrail_strategy_threshold,
            drawdown_guardrail_gap_threshold=drawdown_guardrail_gap_threshold,
            drawdown_guardrail_benchmark=drawdown_guardrail_benchmark,
        )
        guardrail_risk_off = bool(
            guardrail_fields["Underperformance Guardrail Triggered"]
            or guardrail_fields["Drawdown Guardrail Triggered"]
        )

        if rebalancing:
            if guardrail_risk_off:
                held = []
                next_balances = []
                cash = base_balance
            else:
                risky_scores = [(t, score_now[t]) for t in risky_tickers if pd.notna(score_now[t])]
                risky_scores.sort(key=lambda x: x[1])
                picked = [t for t, _ in risky_scores[-top:]][::-1]

                invest = [
                    t
                    for t in picked
                    if pd.notna(ma_now[t])
                    and close_now[t] >= ma_now[t]
                    and _passes_min_price(close_now[t], min_price)
                ]

                if len(invest) == 0:
                    held = []
                    next_balances = []
                    cash = base_balance
                else:
                    w = 1.0 / len(invest)
                    held = invest
                    next_balances = [base_balance * w] * len(invest)
                    cash = base_balance - sum(next_balances)
        else:
            # 리밸런싱 아니면 그대로 유지
            pass

        row = {
            "Date": date,
            "End Ticker": (np.nan if i == 0 else held),
            "Next Ticker": held,
            "End Balance": (np.nan if i == 0 else end_balances),
            "Next Balance": next_balances,
            "Cash": float(cash),
            "Total Balance": float(total_balance),
            "Total Return": total_return,
            "Rebalancing": rebalancing,
        }
        row.update(guardrail_fields)
        rows.append(row)

        # prev update
        for t in tickers:
            prev_close[t] = close_now[t]
        prev_total_balance = total_balance
        strategy_balance_history.append(float(total_balance))
        guardrail_close_history.append(
            float(guardrail_fields["Underperformance Guardrail Benchmark Close"])
            if pd.notna(guardrail_fields["Underperformance Guardrail Benchmark Close"])
            else np.nan
        )

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


def _build_strict_annual_weights(
    *,
    tickers: list[str],
    weighting_mode: str,
) -> list[float]:
    count = len(tickers)
    if count <= 0:
        return []
    if weighting_mode == "equal_weight":
        return [1.0 / float(count)] * count
    if weighting_mode == "rank_tapered":
        raw = np.linspace(1.0, 0.5, count, dtype="float64")
        normalized = raw / raw.sum()
        return [float(weight) for weight in normalized]
    raise ValueError("weighting_mode must be one of {'equal_weight', 'rank_tapered'}.")


def _passes_min_history_months(
    first_valid_date: pd.Timestamp | None,
    current_date: pd.Timestamp,
    min_history_months: int,
) -> bool:
    if min_history_months <= 0:
        return True
    if first_valid_date is None or pd.isna(first_valid_date):
        return False
    months_delta = (
        (int(current_date.year) - int(first_valid_date.year)) * 12
        + (int(current_date.month) - int(first_valid_date.month))
    )
    return months_delta >= int(min_history_months)


def _window_max_drawdown(values: list[float]) -> float:
    series = pd.to_numeric(pd.Series(list(values), dtype="float64"), errors="coerce").dropna()
    if series.empty:
        return np.nan
    running_max = series.cummax()
    drawdown = series / running_max - 1.0
    return float(drawdown.min())


def _build_guardrail_close_by_date(guardrail_df: pd.DataFrame | None) -> dict[pd.Timestamp, float]:
    close_by_date: dict[pd.Timestamp, float] = {}
    if guardrail_df is None or guardrail_df.empty:
        return close_by_date

    working = guardrail_df.copy()
    working["Date"] = pd.to_datetime(working["Date"], errors="coerce")
    working = working.dropna(subset=["Date"]).sort_values("Date")
    for _, row in working.iterrows():
        close_value = pd.to_numeric(row.get("Close"), errors="coerce")
        if pd.isna(close_value):
            continue
        close_by_date[pd.Timestamp(row["Date"]).normalize()] = float(close_value)
    return close_by_date


def _evaluate_portfolio_guardrails(
    *,
    current_date,
    step_index: int,
    current_total_balance: float,
    strategy_balance_history: list[float],
    guardrail_close_history: list[float],
    guardrail_close_by_date: dict[pd.Timestamp, float],
    underperformance_guardrail_enabled: bool = False,
    underperformance_guardrail_window_months: int = 12,
    underperformance_guardrail_threshold: float = -0.10,
    underperformance_guardrail_benchmark: str | None = None,
    drawdown_guardrail_enabled: bool = False,
    drawdown_guardrail_window_months: int = 12,
    drawdown_guardrail_strategy_threshold: float = -0.35,
    drawdown_guardrail_gap_threshold: float = 0.08,
    drawdown_guardrail_benchmark: str | None = None,
) -> dict[str, float | str | bool]:
    snapshot_key = pd.to_datetime(current_date).normalize()
    benchmark_close_now = guardrail_close_by_date.get(snapshot_key, np.nan)

    under_state = "off"
    under_triggered = False
    strategy_return = np.nan
    benchmark_return = np.nan
    excess_return = np.nan
    if underperformance_guardrail_enabled:
        if step_index < int(underperformance_guardrail_window_months):
            under_state = "warming_up"
        else:
            lookback_index = step_index - int(underperformance_guardrail_window_months)
            start_strategy_balance = strategy_balance_history[lookback_index]
            start_benchmark_close = guardrail_close_history[lookback_index]
            if (
                pd.notna(start_strategy_balance)
                and float(start_strategy_balance) > 0.0
                and pd.notna(start_benchmark_close)
                and float(start_benchmark_close) > 0.0
                and pd.notna(benchmark_close_now)
                and float(benchmark_close_now) > 0.0
            ):
                strategy_return = (float(current_total_balance) / float(start_strategy_balance)) - 1.0
                benchmark_return = (float(benchmark_close_now) / float(start_benchmark_close)) - 1.0
                excess_return = float(strategy_return - benchmark_return)
                if float(excess_return) <= -abs(float(underperformance_guardrail_threshold)):
                    under_state = "risk_off"
                    under_triggered = True
                else:
                    under_state = "risk_on"
            else:
                under_state = "unknown"

    drawdown_state = "off"
    drawdown_triggered = False
    strategy_drawdown = np.nan
    benchmark_drawdown = np.nan
    drawdown_gap = np.nan
    if drawdown_guardrail_enabled:
        if step_index < int(drawdown_guardrail_window_months):
            drawdown_state = "warming_up"
        else:
            lookback_index = step_index - int(drawdown_guardrail_window_months)
            strategy_window_values = strategy_balance_history[lookback_index:step_index] + [float(current_total_balance)]
            strategy_drawdown = _window_max_drawdown(strategy_window_values)
            if pd.notna(benchmark_close_now):
                benchmark_window_values = guardrail_close_history[lookback_index:step_index] + [float(benchmark_close_now)]
                benchmark_drawdown = _window_max_drawdown(benchmark_window_values)
                if pd.notna(strategy_drawdown) and pd.notna(benchmark_drawdown):
                    drawdown_gap = float(benchmark_drawdown) - float(strategy_drawdown)

            drawdown_limit_breached = (
                pd.notna(strategy_drawdown)
                and float(strategy_drawdown) <= -abs(float(drawdown_guardrail_strategy_threshold))
            )
            gap_limit_breached = (
                pd.notna(drawdown_gap)
                and float(drawdown_gap) > float(drawdown_guardrail_gap_threshold)
            )
            if drawdown_limit_breached or gap_limit_breached:
                drawdown_state = "risk_off"
                drawdown_triggered = True
            elif pd.notna(strategy_drawdown):
                drawdown_state = "risk_on"
            else:
                drawdown_state = "unknown"

    return {
        "Underperformance Guardrail Enabled": underperformance_guardrail_enabled,
        "Underperformance Guardrail Benchmark": (
            underperformance_guardrail_benchmark if underperformance_guardrail_enabled else np.nan
        ),
        "Underperformance Guardrail Window (Months)": (
            int(underperformance_guardrail_window_months) if underperformance_guardrail_enabled else np.nan
        ),
        "Underperformance Guardrail Threshold": (
            -abs(float(underperformance_guardrail_threshold)) if underperformance_guardrail_enabled else np.nan
        ),
        "Underperformance Guardrail State": under_state,
        "Underperformance Guardrail Triggered": under_triggered,
        "Underperformance Guardrail Benchmark Close": benchmark_close_now,
        "Underperformance Guardrail Strategy Return": strategy_return,
        "Underperformance Guardrail Benchmark Return": benchmark_return,
        "Underperformance Guardrail Excess Return": excess_return,
        "Drawdown Guardrail Enabled": drawdown_guardrail_enabled,
        "Drawdown Guardrail Benchmark": (
            drawdown_guardrail_benchmark if drawdown_guardrail_enabled else np.nan
        ),
        "Drawdown Guardrail Window (Months)": (
            int(drawdown_guardrail_window_months) if drawdown_guardrail_enabled else np.nan
        ),
        "Drawdown Guardrail Strategy Threshold": (
            -abs(float(drawdown_guardrail_strategy_threshold)) if drawdown_guardrail_enabled else np.nan
        ),
        "Drawdown Guardrail Gap Threshold": (
            float(drawdown_guardrail_gap_threshold) if drawdown_guardrail_enabled else np.nan
        ),
        "Drawdown Guardrail State": drawdown_state,
        "Drawdown Guardrail Triggered": drawdown_triggered,
        "Drawdown Guardrail Benchmark Close": benchmark_close_now,
        "Drawdown Guardrail Strategy Drawdown": strategy_drawdown,
        "Drawdown Guardrail Benchmark Drawdown": benchmark_drawdown,
        "Drawdown Guardrail Gap": drawdown_gap,
    }


def quality_snapshot_equal_weight(
    price_dfs: dict,
    snapshot_by_date: dict,
    *,
    start_balance: float,
    quality_factors: list[str],
    top_n: int = 10,
    lower_is_better_factors: list[str] | None = None,
    rebalance_interval: int = 1,
    min_price: float = 0.0,
    min_history_months: int = 0,
    min_avg_dollar_volume_20d_m: float = 0.0,
    candidate_tickers: list[str] | None = None,
    trend_filter_enabled: bool = False,
    trend_filter_window: int = 200,
    trend_filter_col: str | None = None,
    weighting_mode: str = "equal_weight",
    partial_cash_retention_enabled: bool = False,
    risk_off_mode: str = "cash_only",
    defensive_tickers: list[str] | None = None,
    market_regime_enabled: bool = False,
    market_regime_window: int = 200,
    market_regime_benchmark: str | None = None,
    market_regime_df: pd.DataFrame | None = None,
    market_regime_col: str | None = None,
    underperformance_guardrail_enabled: bool = False,
    underperformance_guardrail_window_months: int = 12,
    underperformance_guardrail_threshold: float = -0.10,
    underperformance_guardrail_benchmark: str | None = None,
    underperformance_guardrail_df: pd.DataFrame | None = None,
    drawdown_guardrail_enabled: bool = False,
    drawdown_guardrail_window_months: int = 12,
    drawdown_guardrail_strategy_threshold: float = -0.35,
    drawdown_guardrail_gap_threshold: float = 0.08,
    drawdown_guardrail_benchmark: str | None = None,
    drawdown_guardrail_df: pd.DataFrame | None = None,
    first_valid_price_dates: dict[str, pd.Timestamp | None] | None = None,
    avg_dollar_volume_20d_by_date: dict[str, dict[pd.Timestamp, float]] | None = None,
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
    if min_price < 0:
        raise ValueError("min_price must be non-negative.")
    if min_history_months < 0:
        raise ValueError("min_history_months must be non-negative.")
    if min_avg_dollar_volume_20d_m < 0:
        raise ValueError("min_avg_dollar_volume_20d_m must be non-negative.")
    if trend_filter_enabled and trend_filter_window <= 0:
        raise ValueError("trend_filter_window must be positive when trend filter is enabled.")
    if market_regime_enabled and market_regime_window <= 0:
        raise ValueError("market_regime_window must be positive when market regime overlay is enabled.")
    if market_regime_enabled and market_regime_df is None:
        raise ValueError("market_regime_df is required when market regime overlay is enabled.")
    if underperformance_guardrail_enabled and underperformance_guardrail_window_months <= 0:
        raise ValueError("underperformance_guardrail_window_months must be positive when the guardrail is enabled.")
    if underperformance_guardrail_enabled and underperformance_guardrail_df is None:
        raise ValueError("underperformance_guardrail_df is required when the guardrail is enabled.")
    if drawdown_guardrail_enabled and drawdown_guardrail_window_months <= 0:
        raise ValueError("drawdown_guardrail_window_months must be positive when the guardrail is enabled.")
    if drawdown_guardrail_enabled and drawdown_guardrail_df is None:
        raise ValueError("drawdown_guardrail_df is required when the guardrail is enabled.")
    if drawdown_guardrail_enabled and drawdown_guardrail_gap_threshold < 0:
        raise ValueError("drawdown_guardrail_gap_threshold must be non-negative when the guardrail is enabled.")
    if weighting_mode not in {"equal_weight", "rank_tapered"}:
        raise ValueError("weighting_mode must be one of {'equal_weight', 'rank_tapered'}.")
    if risk_off_mode not in {"cash_only", "defensive_sleeve_preference"}:
        raise ValueError("risk_off_mode must be one of {'cash_only', 'defensive_sleeve_preference'}.")

    tickers = list(price_dfs.keys())
    selection_tickers = [
        str(ticker).strip().upper()
        for ticker in (candidate_tickers or tickers)
        if str(ticker).strip() and str(ticker).strip().upper() in price_dfs
    ]
    if not selection_tickers:
        selection_tickers = list(tickers)
    defensive_set = {
        ticker for ticker in (defensive_tickers or [])
        if ticker in tickers
    }
    base_df = price_dfs[tickers[0]].sort_values("Date").reset_index(drop=True)
    dates = pd.to_datetime(base_df["Date"]).tolist()
    effective_first_valid_dates = dict(first_valid_price_dates or {})
    effective_avg_dollar_volume = dict(avg_dollar_volume_20d_by_date or {})
    if not effective_first_valid_dates:
        for ticker in tickers:
            working = price_dfs[ticker][["Date", "Close"]].copy()
            working["Date"] = pd.to_datetime(working["Date"], errors="coerce")
            working["Close"] = pd.to_numeric(working["Close"], errors="coerce")
            valid = working.dropna(subset=["Date", "Close"])
            effective_first_valid_dates[ticker] = (
                pd.Timestamp(valid["Date"].iloc[0]).normalize() if not valid.empty else None
            )
    active_trend_col = trend_filter_col or f"MA{trend_filter_window}"
    active_regime_col = market_regime_col or f"MA{market_regime_window}"

    regime_by_date: dict[pd.Timestamp, dict[str, float]] = {}
    if market_regime_enabled and market_regime_df is not None:
        working_regime = market_regime_df.copy()
        working_regime["Date"] = pd.to_datetime(working_regime["Date"], errors="coerce")
        working_regime = working_regime.dropna(subset=["Date"]).sort_values("Date")
        for _, regime_row in working_regime.iterrows():
            regime_date = pd.Timestamp(regime_row["Date"]).normalize()
            regime_close = pd.to_numeric(regime_row.get("Close"), errors="coerce")
            regime_trend = pd.to_numeric(regime_row.get(active_regime_col), errors="coerce")
            regime_by_date[regime_date] = {
                "close": float(regime_close) if pd.notna(regime_close) else np.nan,
                "trend": float(regime_trend) if pd.notna(regime_trend) else np.nan,
            }

    guardrail_close_by_date: dict[pd.Timestamp, float] = {}
    if underperformance_guardrail_enabled and underperformance_guardrail_df is not None:
        working_guardrail = underperformance_guardrail_df.copy()
        working_guardrail["Date"] = pd.to_datetime(working_guardrail["Date"], errors="coerce")
        working_guardrail = working_guardrail.dropna(subset=["Date"]).sort_values("Date")
        for _, guardrail_row in working_guardrail.iterrows():
            guardrail_date = pd.Timestamp(guardrail_row["Date"]).normalize()
            guardrail_close = pd.to_numeric(guardrail_row.get("Close"), errors="coerce")
            guardrail_close_by_date[guardrail_date] = float(guardrail_close) if pd.notna(guardrail_close) else np.nan

    drawdown_guardrail_close_by_date: dict[pd.Timestamp, float] = {}
    if drawdown_guardrail_enabled and drawdown_guardrail_df is not None:
        working_drawdown_guardrail = drawdown_guardrail_df.copy()
        working_drawdown_guardrail["Date"] = pd.to_datetime(working_drawdown_guardrail["Date"], errors="coerce")
        working_drawdown_guardrail = working_drawdown_guardrail.dropna(subset=["Date"]).sort_values("Date")
        for _, guardrail_row in working_drawdown_guardrail.iterrows():
            guardrail_date = pd.Timestamp(guardrail_row["Date"]).normalize()
            guardrail_close = pd.to_numeric(guardrail_row.get("Close"), errors="coerce")
            drawdown_guardrail_close_by_date[guardrail_date] = (
                float(guardrail_close) if pd.notna(guardrail_close) else np.nan
            )

    prev_close: dict[str, float | None] = {ticker: None for ticker in tickers}
    prev_total_balance = None
    held_tickers: list[str] = []
    next_balances: list[float] = []
    next_weights: list[float] = []
    cash = 0.0
    total_balance_history: list[float] = []
    guardrail_close_history: list[float] = []
    drawdown_guardrail_close_history: list[float] = []

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
        defensive_sleeve_tickers: list[str] = []
        regime_blocked_tickers: list[str] = []
        underperformance_blocked_tickers: list[str] = []
        drawdown_blocked_tickers: list[str] = []
        history_excluded_tickers: list[str] = []
        liquidity_excluded_tickers: list[str] = []
        risk_off_reasons: list[str] = []
        partial_cash_retention_active = False
        partial_cash_retention_base_count = np.nan

        regime_state = "off"
        regime_close_now = np.nan
        regime_trend_now = np.nan
        if market_regime_enabled:
            regime_row = regime_by_date.get(snapshot_key)
            if regime_row is None:
                regime_state = "unknown"
            else:
                regime_close_now = regime_row["close"]
                regime_trend_now = regime_row["trend"]
                if pd.notna(regime_close_now) and pd.notna(regime_trend_now):
                    regime_state = "risk_on" if float(regime_close_now) >= float(regime_trend_now) else "risk_off"
                else:
                    regime_state = "unknown"
                if regime_state == "risk_off":
                    risk_off_reasons.append("market_regime")

        guardrail_state = "off"
        guardrail_triggered = False
        guardrail_benchmark_close_now = np.nan
        guardrail_strategy_return = np.nan
        guardrail_benchmark_return = np.nan
        guardrail_excess_return = np.nan
        if underperformance_guardrail_enabled:
            guardrail_benchmark_close_now = guardrail_close_by_date.get(snapshot_key, np.nan)
            if i < int(underperformance_guardrail_window_months):
                guardrail_state = "warming_up"
            else:
                lookback_index = i - int(underperformance_guardrail_window_months)
                if (
                    lookback_index >= 0
                    and lookback_index < len(total_balance_history)
                    and lookback_index < len(guardrail_close_history)
                ):
                    base_strategy_balance = total_balance_history[lookback_index]
                    base_benchmark_close = guardrail_close_history[lookback_index]
                    if (
                        pd.notna(base_strategy_balance)
                        and pd.notna(base_benchmark_close)
                        and float(base_strategy_balance) > 0
                        and float(base_benchmark_close) > 0
                        and pd.notna(guardrail_benchmark_close_now)
                    ):
                        guardrail_strategy_return = (float(total_balance) / float(base_strategy_balance)) - 1.0
                        guardrail_benchmark_return = (
                            float(guardrail_benchmark_close_now) / float(base_benchmark_close)
                        ) - 1.0
                        guardrail_excess_return = guardrail_strategy_return - guardrail_benchmark_return
                        if float(guardrail_excess_return) <= -abs(float(underperformance_guardrail_threshold)):
                            guardrail_state = "risk_off"
                            guardrail_triggered = True
                            risk_off_reasons.append("underperformance_guardrail")
                        else:
                            guardrail_state = "risk_on"
                    else:
                        guardrail_state = "unknown"
                else:
                    guardrail_state = "unknown"

        drawdown_guardrail_state = "off"
        drawdown_guardrail_triggered = False
        drawdown_guardrail_benchmark_close_now = np.nan
        drawdown_guardrail_strategy_drawdown = np.nan
        drawdown_guardrail_benchmark_drawdown = np.nan
        drawdown_guardrail_gap = np.nan
        if drawdown_guardrail_enabled:
            drawdown_guardrail_benchmark_close_now = drawdown_guardrail_close_by_date.get(snapshot_key, np.nan)
            if i < int(drawdown_guardrail_window_months):
                drawdown_guardrail_state = "warming_up"
            else:
                lookback_index = i - int(drawdown_guardrail_window_months)
                strategy_window_values = total_balance_history[lookback_index:i] + [float(total_balance)]
                drawdown_guardrail_strategy_drawdown = _window_max_drawdown(strategy_window_values)
                if pd.notna(drawdown_guardrail_benchmark_close_now):
                    benchmark_window_values = drawdown_guardrail_close_history[lookback_index:i] + [
                        float(drawdown_guardrail_benchmark_close_now)
                    ]
                    drawdown_guardrail_benchmark_drawdown = _window_max_drawdown(benchmark_window_values)
                    if (
                        pd.notna(drawdown_guardrail_strategy_drawdown)
                        and pd.notna(drawdown_guardrail_benchmark_drawdown)
                    ):
                        drawdown_guardrail_gap = (
                            float(drawdown_guardrail_benchmark_drawdown)
                            - float(drawdown_guardrail_strategy_drawdown)
                        )
                breached_strategy = (
                    pd.notna(drawdown_guardrail_strategy_drawdown)
                    and float(drawdown_guardrail_strategy_drawdown)
                    <= -abs(float(drawdown_guardrail_strategy_threshold))
                )
                breached_gap = (
                    pd.notna(drawdown_guardrail_gap)
                    and float(drawdown_guardrail_gap) > float(drawdown_guardrail_gap_threshold)
                )
                if breached_strategy or breached_gap:
                    drawdown_guardrail_state = "risk_off"
                    drawdown_guardrail_triggered = True
                    risk_off_reasons.append("drawdown_guardrail")
                elif pd.notna(drawdown_guardrail_strategy_drawdown):
                    drawdown_guardrail_state = "risk_on"
                else:
                    drawdown_guardrail_state = "unknown"

        def _build_defensive_sleeve_candidates() -> list[str]:
            if not defensive_set:
                return []
            candidates: list[str] = []
            for ticker in defensive_tickers or []:
                normalized_ticker = str(ticker).strip().upper()
                if normalized_ticker not in defensive_set:
                    continue
                current_close = close_now.get(normalized_ticker)
                if pd.isna(current_close) or not _passes_min_price(float(current_close), min_price):
                    continue
                candidates.append(normalized_ticker)
            return candidates

        if rebalancing:
            snapshot_df = snapshot_by_date.get(snapshot_key)
            ranked = _rank_quality_snapshot(
                snapshot_df if snapshot_df is not None else pd.DataFrame(),
                quality_factors=quality_factors,
                lower_is_better_factors=lower_is_better_factors,
            )
            if not ranked.empty:
                available_tickers = set()
                for ticker in selection_tickers:
                    current_close = close_now.get(ticker)
                    if pd.isna(current_close):
                        continue
                    if not _passes_min_price(float(current_close), min_price):
                        continue
                    if not _passes_min_history_months(
                        effective_first_valid_dates.get(ticker),
                        snapshot_key,
                        int(min_history_months),
                    ):
                        history_excluded_tickers.append(ticker)
                        continue
                    if not _passes_min_avg_dollar_volume(
                        (effective_avg_dollar_volume.get(ticker) or {}).get(snapshot_key),
                        float(min_avg_dollar_volume_20d_m or 0.0),
                    ):
                        liquidity_excluded_tickers.append(ticker)
                        continue
                    available_tickers.add(ticker)
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

                if market_regime_enabled and not selected_snapshot.empty and regime_state == "risk_off":
                    regime_blocked_tickers = selected_snapshot["symbol"].tolist()
                    selected_snapshot = selected_snapshot.iloc[0:0].copy()

                if underperformance_guardrail_enabled and not selected_snapshot.empty and guardrail_state == "risk_off":
                    underperformance_blocked_tickers = selected_snapshot["symbol"].tolist()
                    selected_snapshot = selected_snapshot.iloc[0:0].copy()

                if drawdown_guardrail_enabled and not selected_snapshot.empty and drawdown_guardrail_state == "risk_off":
                    drawdown_blocked_tickers = selected_snapshot["symbol"].tolist()
                    selected_snapshot = selected_snapshot.iloc[0:0].copy()

                held_tickers = selected_snapshot["symbol"].tolist()
                selected_scores = selected_snapshot["Quality Score"].astype(float).tolist()
                if risk_off_reasons and risk_off_mode == "defensive_sleeve_preference":
                    defensive_sleeve_tickers = _build_defensive_sleeve_candidates()
                    held_tickers = list(defensive_sleeve_tickers)
                    selected_scores = []
                if not held_tickers:
                    next_balances = []
                    next_weights = []
                    cash = base_balance
                else:
                    allocation_base_count = len(held_tickers)
                    if (
                        partial_cash_retention_enabled
                        and trend_filter_enabled
                        and overlay_rejected_tickers
                        and raw_selected_tickers
                    ):
                        allocation_base_count = len(raw_selected_tickers)
                        partial_cash_retention_active = allocation_base_count > len(held_tickers)
                        partial_cash_retention_base_count = float(allocation_base_count)
                    invested_fraction = float(len(held_tickers)) / float(allocation_base_count)
                    invested_balance = float(base_balance) * invested_fraction
                    if risk_off_reasons and risk_off_mode == "defensive_sleeve_preference":
                        next_weights = _build_strict_annual_weights(
                            tickers=held_tickers,
                            weighting_mode="equal_weight",
                        )
                    else:
                        next_weights = _build_strict_annual_weights(
                            tickers=held_tickers,
                            weighting_mode=weighting_mode,
                        )
                    next_balances = [float(invested_balance) * float(weight) for weight in next_weights]
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
                "Weighting Mode": weighting_mode,
                "Risk-Off Mode": risk_off_mode,
                "Risk-Off Reason": risk_off_reasons,
                "Defensive Sleeve Ticker": defensive_sleeve_tickers,
                "Defensive Sleeve Count": len(defensive_sleeve_tickers),
                "Trend Filter Enabled": trend_filter_enabled,
                "Trend Filter Column": (active_trend_col if trend_filter_enabled else np.nan),
                "Partial Cash Retention Enabled": partial_cash_retention_enabled,
                "Partial Cash Retention Active": partial_cash_retention_active,
                "Partial Cash Retention Base Count": partial_cash_retention_base_count,
                "Market Regime Enabled": market_regime_enabled,
                "Market Regime Benchmark": (market_regime_benchmark if market_regime_enabled else np.nan),
                "Market Regime Column": (active_regime_col if market_regime_enabled else np.nan),
                "Market Regime State": regime_state,
                "Market Regime Close": regime_close_now,
                "Market Regime Trend": regime_trend_now,
                "Regime Blocked Ticker": regime_blocked_tickers,
                "Regime Blocked Count": len(regime_blocked_tickers),
                "Underperformance Guardrail Enabled": underperformance_guardrail_enabled,
                "Underperformance Guardrail Benchmark": (
                    underperformance_guardrail_benchmark if underperformance_guardrail_enabled else np.nan
                ),
                "Underperformance Guardrail Window": (
                    int(underperformance_guardrail_window_months) if underperformance_guardrail_enabled else np.nan
                ),
                "Underperformance Guardrail Threshold": (
                    -abs(float(underperformance_guardrail_threshold)) if underperformance_guardrail_enabled else np.nan
                ),
                "Minimum History Months": int(min_history_months or 0),
                "History Excluded Ticker": history_excluded_tickers,
                "History Excluded Count": len(history_excluded_tickers),
                "Minimum Avg Dollar Volume 20D ($M)": float(min_avg_dollar_volume_20d_m or 0.0),
                "Liquidity Excluded Ticker": liquidity_excluded_tickers,
                "Liquidity Excluded Count": len(liquidity_excluded_tickers),
                "Underperformance Guardrail State": guardrail_state,
                "Underperformance Guardrail Triggered": guardrail_triggered,
                "Underperformance Guardrail Benchmark Close": guardrail_benchmark_close_now,
                "Underperformance Guardrail Strategy Return": guardrail_strategy_return,
                "Underperformance Guardrail Benchmark Return": guardrail_benchmark_return,
                "Underperformance Guardrail Excess Return": guardrail_excess_return,
                "Underperformance Blocked Ticker": underperformance_blocked_tickers,
                "Underperformance Blocked Count": len(underperformance_blocked_tickers),
                "Drawdown Guardrail Enabled": drawdown_guardrail_enabled,
                "Drawdown Guardrail Benchmark": (
                    drawdown_guardrail_benchmark if drawdown_guardrail_enabled else np.nan
                ),
                "Drawdown Guardrail Window": (
                    int(drawdown_guardrail_window_months) if drawdown_guardrail_enabled else np.nan
                ),
                "Drawdown Guardrail Strategy Threshold": (
                    -abs(float(drawdown_guardrail_strategy_threshold)) if drawdown_guardrail_enabled else np.nan
                ),
                "Drawdown Guardrail Gap Threshold": (
                    float(drawdown_guardrail_gap_threshold) if drawdown_guardrail_enabled else np.nan
                ),
                "Drawdown Guardrail State": drawdown_guardrail_state,
                "Drawdown Guardrail Triggered": drawdown_guardrail_triggered,
                "Drawdown Guardrail Benchmark Close": drawdown_guardrail_benchmark_close_now,
                "Drawdown Guardrail Strategy Drawdown": drawdown_guardrail_strategy_drawdown,
                "Drawdown Guardrail Benchmark Drawdown": drawdown_guardrail_benchmark_drawdown,
                "Drawdown Guardrail Gap": drawdown_guardrail_gap,
                "Drawdown Blocked Ticker": drawdown_blocked_tickers,
                "Drawdown Blocked Count": len(drawdown_blocked_tickers),
                "End Balance": (np.nan if i == 0 else end_balances),
                "Next Balance": next_balances,
                "Next Weight": next_weights,
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
        total_balance_history.append(float(total_balance))
        guardrail_close_history.append(
            float(guardrail_benchmark_close_now) if pd.notna(guardrail_benchmark_close_now) else np.nan
        )
        drawdown_guardrail_close_history.append(
            float(drawdown_guardrail_benchmark_close_now)
            if pd.notna(drawdown_guardrail_benchmark_close_now)
            else np.nan
        )

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

    def __init__(
        self,
        start_balance: int,
        top: int,
        filter_ma: str,
        min_price: float = 0.0,
        score_col: str = "Avg Score",
        risk_off_mode: str = "cash_only",
        defensive_tickers: list[str] | None = None,
        risk_overlay_df: pd.DataFrame | None = None,
        market_regime_enabled: bool = False,
        market_regime_window: int = 200,
        market_regime_benchmark: str | None = None,
        crash_guardrail_enabled: bool = False,
        crash_guardrail_drawdown_threshold: float = 0.15,
        underperformance_guardrail_enabled: bool = False,
        underperformance_guardrail_window_months: int = 12,
        underperformance_guardrail_threshold: float = -0.10,
        underperformance_guardrail_benchmark: str | None = None,
        underperformance_guardrail_df: pd.DataFrame | None = None,
        drawdown_guardrail_enabled: bool = False,
        drawdown_guardrail_window_months: int = 12,
        drawdown_guardrail_strategy_threshold: float = -0.35,
        drawdown_guardrail_gap_threshold: float = 0.08,
        drawdown_guardrail_benchmark: str | None = None,
        drawdown_guardrail_df: pd.DataFrame | None = None,
    ):
        self.start_balance = start_balance
        self.top = top
        self.filter_ma = filter_ma
        self.min_price = min_price
        self.score_col = score_col
        self.risk_off_mode = risk_off_mode
        self.defensive_tickers = defensive_tickers or []
        self.risk_overlay_df = risk_overlay_df
        self.market_regime_enabled = market_regime_enabled
        self.market_regime_window = market_regime_window
        self.market_regime_benchmark = market_regime_benchmark
        self.crash_guardrail_enabled = crash_guardrail_enabled
        self.crash_guardrail_drawdown_threshold = crash_guardrail_drawdown_threshold
        self.underperformance_guardrail_enabled = underperformance_guardrail_enabled
        self.underperformance_guardrail_window_months = underperformance_guardrail_window_months
        self.underperformance_guardrail_threshold = underperformance_guardrail_threshold
        self.underperformance_guardrail_benchmark = underperformance_guardrail_benchmark
        self.underperformance_guardrail_df = underperformance_guardrail_df
        self.drawdown_guardrail_enabled = drawdown_guardrail_enabled
        self.drawdown_guardrail_window_months = drawdown_guardrail_window_months
        self.drawdown_guardrail_strategy_threshold = drawdown_guardrail_strategy_threshold
        self.drawdown_guardrail_gap_threshold = drawdown_guardrail_gap_threshold
        self.drawdown_guardrail_benchmark = drawdown_guardrail_benchmark
        self.drawdown_guardrail_df = drawdown_guardrail_df

    def run(self, dfs: dict) -> pd.DataFrame:
        return gtaa3(
            dfs,
            self.start_balance,
            self.top,
            self.filter_ma,
            self.min_price,
            self.score_col,
            self.risk_off_mode,
            self.defensive_tickers,
            self.risk_overlay_df,
            self.market_regime_enabled,
            self.market_regime_window,
            self.market_regime_benchmark,
            self.crash_guardrail_enabled,
            self.crash_guardrail_drawdown_threshold,
            self.underperformance_guardrail_enabled,
            self.underperformance_guardrail_window_months,
            self.underperformance_guardrail_threshold,
            self.underperformance_guardrail_benchmark,
            self.underperformance_guardrail_df,
            self.drawdown_guardrail_enabled,
            self.drawdown_guardrail_window_months,
            self.drawdown_guardrail_strategy_threshold,
            self.drawdown_guardrail_gap_threshold,
            self.drawdown_guardrail_benchmark,
            self.drawdown_guardrail_df,
        )


class RiskParityTrendStrategy(Strategy):
    def __init__(
        self,
        start_balance: float,
        rebalance_interval: int = 1,
        vol_window: int = 6,
        filter_ma: str = "MA200",
        min_price: float = 0.0,
        underperformance_guardrail_enabled: bool = False,
        underperformance_guardrail_window_months: int = 12,
        underperformance_guardrail_threshold: float = -0.10,
        underperformance_guardrail_benchmark: str | None = None,
        underperformance_guardrail_df: pd.DataFrame | None = None,
        drawdown_guardrail_enabled: bool = False,
        drawdown_guardrail_window_months: int = 12,
        drawdown_guardrail_strategy_threshold: float = -0.35,
        drawdown_guardrail_gap_threshold: float = 0.08,
        drawdown_guardrail_benchmark: str | None = None,
        drawdown_guardrail_df: pd.DataFrame | None = None,
    ):
        self.start_balance = start_balance
        self.rebalance_interval = rebalance_interval
        self.vol_window = vol_window
        self.filter_ma = filter_ma
        self.min_price = min_price
        self.underperformance_guardrail_enabled = underperformance_guardrail_enabled
        self.underperformance_guardrail_window_months = underperformance_guardrail_window_months
        self.underperformance_guardrail_threshold = underperformance_guardrail_threshold
        self.underperformance_guardrail_benchmark = underperformance_guardrail_benchmark
        self.underperformance_guardrail_df = underperformance_guardrail_df
        self.drawdown_guardrail_enabled = drawdown_guardrail_enabled
        self.drawdown_guardrail_window_months = drawdown_guardrail_window_months
        self.drawdown_guardrail_strategy_threshold = drawdown_guardrail_strategy_threshold
        self.drawdown_guardrail_gap_threshold = drawdown_guardrail_gap_threshold
        self.drawdown_guardrail_benchmark = drawdown_guardrail_benchmark
        self.drawdown_guardrail_df = drawdown_guardrail_df

    def run(self, dfs: dict) -> pd.DataFrame:
        return risk_parity_trend(
            dfs=dfs,
            start_balance=self.start_balance,
            rebalance_interval=self.rebalance_interval,
            vol_window=self.vol_window,
            filter_ma=self.filter_ma,
            min_price=self.min_price,
            underperformance_guardrail_enabled=self.underperformance_guardrail_enabled,
            underperformance_guardrail_window_months=self.underperformance_guardrail_window_months,
            underperformance_guardrail_threshold=self.underperformance_guardrail_threshold,
            underperformance_guardrail_benchmark=self.underperformance_guardrail_benchmark,
            underperformance_guardrail_df=self.underperformance_guardrail_df,
            drawdown_guardrail_enabled=self.drawdown_guardrail_enabled,
            drawdown_guardrail_window_months=self.drawdown_guardrail_window_months,
            drawdown_guardrail_strategy_threshold=self.drawdown_guardrail_strategy_threshold,
            drawdown_guardrail_gap_threshold=self.drawdown_guardrail_gap_threshold,
            drawdown_guardrail_benchmark=self.drawdown_guardrail_benchmark,
            drawdown_guardrail_df=self.drawdown_guardrail_df,
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
        min_price: float = 0.0,
        underperformance_guardrail_enabled: bool = False,
        underperformance_guardrail_window_months: int = 12,
        underperformance_guardrail_threshold: float = -0.10,
        underperformance_guardrail_benchmark: str | None = None,
        underperformance_guardrail_df: pd.DataFrame | None = None,
        drawdown_guardrail_enabled: bool = False,
        drawdown_guardrail_window_months: int = 12,
        drawdown_guardrail_strategy_threshold: float = -0.35,
        drawdown_guardrail_gap_threshold: float = 0.08,
        drawdown_guardrail_benchmark: str | None = None,
        drawdown_guardrail_df: pd.DataFrame | None = None,
    ):
        self.start_balance = start_balance
        self.top = top
        self.lookback_col = lookback_col
        self.filter_ma = filter_ma
        self.rebalance_interval = rebalance_interval
        self.cash_ticker = cash_ticker
        self.min_price = min_price
        self.underperformance_guardrail_enabled = underperformance_guardrail_enabled
        self.underperformance_guardrail_window_months = underperformance_guardrail_window_months
        self.underperformance_guardrail_threshold = underperformance_guardrail_threshold
        self.underperformance_guardrail_benchmark = underperformance_guardrail_benchmark
        self.underperformance_guardrail_df = underperformance_guardrail_df
        self.drawdown_guardrail_enabled = drawdown_guardrail_enabled
        self.drawdown_guardrail_window_months = drawdown_guardrail_window_months
        self.drawdown_guardrail_strategy_threshold = drawdown_guardrail_strategy_threshold
        self.drawdown_guardrail_gap_threshold = drawdown_guardrail_gap_threshold
        self.drawdown_guardrail_benchmark = drawdown_guardrail_benchmark
        self.drawdown_guardrail_df = drawdown_guardrail_df

    def run(self, dfs: dict) -> pd.DataFrame:
        return dual_momentum(
            dfs=dfs,
            start_balance=self.start_balance,
            top=self.top,
            lookback_col=self.lookback_col,
            filter_ma=self.filter_ma,
            rebalance_interval=self.rebalance_interval,
            cash_ticker=self.cash_ticker,
            min_price=self.min_price,
            underperformance_guardrail_enabled=self.underperformance_guardrail_enabled,
            underperformance_guardrail_window_months=self.underperformance_guardrail_window_months,
            underperformance_guardrail_threshold=self.underperformance_guardrail_threshold,
            underperformance_guardrail_benchmark=self.underperformance_guardrail_benchmark,
            underperformance_guardrail_df=self.underperformance_guardrail_df,
            drawdown_guardrail_enabled=self.drawdown_guardrail_enabled,
            drawdown_guardrail_window_months=self.drawdown_guardrail_window_months,
            drawdown_guardrail_strategy_threshold=self.drawdown_guardrail_strategy_threshold,
            drawdown_guardrail_gap_threshold=self.drawdown_guardrail_gap_threshold,
            drawdown_guardrail_benchmark=self.drawdown_guardrail_benchmark,
            drawdown_guardrail_df=self.drawdown_guardrail_df,
        )
