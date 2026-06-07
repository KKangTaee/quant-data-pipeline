from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np
import pandas as pd

from finance.loaders import load_asset_profile_status_summary, load_price_history
from finance.performance import portfolio_performance_summary
from finance.sample import STATIC_MANAGED_RESEARCH_UNIVERSE, STRICT_MARKET_REGIME_DEFAULT_BENCHMARK


ETF_REAL_MONEY_DEFAULT_MIN_PRICE = 5.0
ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS = 10.0
ETF_REAL_MONEY_DEFAULT_BENCHMARK = "SPY"
ETF_OPERABILITY_DEFAULT_MIN_AUM_B = 1.0
ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT = 0.005
STRICT_BENCHMARK_CONTRACT_TICKER = "ticker"
STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT = "candidate_universe_equal_weight"
STRICT_DEFAULT_BENCHMARK_CONTRACT = STRICT_BENCHMARK_CONTRACT_TICKER
STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE = 0.95
STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD = -0.02
STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE = 0.90
STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE = 0.55
STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN = -0.15
STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN = -0.35
STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK = 0.08
REAL_MONEY_CASH_LABEL = "__CASH__"
ETF_OPERABILITY_STRATEGY_KEYS = {
    "equal_weight",
    "gtaa",
    "global_relative_strength",
    "risk_parity_trend",
    "dual_momentum",
}


def _normalize_tickers(tickers: Sequence[str] | None) -> list[str]:
    if tickers is None:
        return ["VIG", "SCHD", "DGRO", "GLD"]

    normalized: list[str] = []
    seen: set[str] = set()

    for raw in tickers:
        symbol = str(raw).strip().upper()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        normalized.append(symbol)

    if not normalized:
        from app.runtime.backtest import BacktestInputError

        raise BacktestInputError("At least one ticker must be provided.")

    return normalized


def _coerce_list_cell(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if pd.isna(value):
        return []
    return []


def _coerce_float(value: Any, default: float = 0.0) -> float:
    if value is None or pd.isna(value):
        return float(default)
    return float(value)


def _build_weight_map(
    tickers: list[Any],
    balances: list[Any],
    *,
    cash_value: float,
    total_balance: float,
) -> dict[str, float]:
    if total_balance <= 0:
        return {REAL_MONEY_CASH_LABEL: 1.0}

    weights: dict[str, float] = {}
    for ticker, balance in zip(tickers, balances):
        symbol = str(ticker).strip().upper()
        if not symbol:
            continue
        weight = max(_coerce_float(balance), 0.0) / total_balance
        weights[symbol] = weights.get(symbol, 0.0) + weight

    cash_weight = max(float(cash_value), 0.0) / total_balance
    if cash_weight > 0 or not weights:
        weights[REAL_MONEY_CASH_LABEL] = cash_weight

    return weights


_TURNOVER_INPUT_COLUMNS = {"End Ticker", "End Balance", "Next Ticker", "Next Balance"}


def _missing_turnover_input_columns(result_df: pd.DataFrame) -> list[str]:
    return sorted(column for column in _TURNOVER_INPUT_COLUMNS if column not in result_df.columns)


def _estimate_turnover_series(result_df: pd.DataFrame) -> pd.Series:
    if _missing_turnover_input_columns(result_df):
        return pd.Series([np.nan] * len(result_df), index=result_df.index, dtype=float)

    turnovers: list[float] = []
    for _, row in result_df.iterrows():
        if "Rebalancing" in result_df.columns and bool(row.get("Rebalancing")) is False:
            turnovers.append(0.0)
            continue

        gross_total_balance = max(_coerce_float(row.get("Total Balance")), 0.0)
        if gross_total_balance <= 0:
            turnovers.append(0.0)
            continue

        end_tickers = _coerce_list_cell(row.get("End Ticker"))
        end_balances = _coerce_list_cell(row.get("End Balance"))
        next_tickers = _coerce_list_cell(row.get("Next Ticker"))
        next_balances = _coerce_list_cell(row.get("Next Balance"))
        next_cash = max(_coerce_float(row.get("Cash")), 0.0)
        end_cash = max(gross_total_balance - sum(_coerce_float(value) for value in end_balances), 0.0)

        current_weights = _build_weight_map(
            end_tickers,
            end_balances,
            cash_value=end_cash,
            total_balance=gross_total_balance,
        )
        target_weights = _build_weight_map(
            next_tickers,
            next_balances,
            cash_value=next_cash,
            total_balance=gross_total_balance,
        )

        universe = set(current_weights) | set(target_weights)
        turnover = 0.5 * sum(
            abs(current_weights.get(symbol, 0.0) - target_weights.get(symbol, 0.0))
            for symbol in universe
        )
        turnovers.append(float(turnover))

    return pd.Series(turnovers, index=result_df.index, dtype=float)


def _turnover_diagnostics_from_result(working: pd.DataFrame) -> dict[str, Any]:
    missing_columns = _missing_turnover_input_columns(working)
    turnover = pd.to_numeric(working.get("Turnover"), errors="coerce")
    observed = turnover.dropna()
    if "Rebalancing" in working.columns:
        rebalance_mask = working["Rebalancing"].fillna(False).astype(bool)
    else:
        rebalance_mask = pd.Series(True, index=working.index)
    rebalance_turnover = turnover[rebalance_mask].dropna()

    if missing_columns:
        estimation_status = "not_estimated_missing_holdings"
        turnover_source = "missing_result_holding_columns"
    elif observed.empty:
        estimation_status = "not_estimated_no_observations"
        turnover_source = "end_next_holdings_weight_delta"
    else:
        estimation_status = "estimated_from_holdings"
        turnover_source = "end_next_holdings_weight_delta"

    return {
        "turnover_model_contract_version": "turnover_evidence_contract_v1",
        "turnover_estimation_status": estimation_status,
        "turnover_source": turnover_source,
        "turnover_input_missing_columns": missing_columns,
        "turnover_observation_count": int(observed.count()),
        "turnover_rebalance_rows": int(rebalance_mask.sum()) if not working.empty else 0,
        "turnover_nonzero_count": int((observed > 0).sum()),
        "avg_turnover": float(observed.mean()) if not observed.empty else None,
        "max_turnover": float(observed.max()) if not observed.empty else None,
        "avg_rebalance_turnover": float(rebalance_turnover.mean()) if not rebalance_turnover.empty else None,
    }


def _apply_transaction_cost_postprocess(
    result_df: pd.DataFrame,
    *,
    transaction_cost_bps: float,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    working = result_df.copy()
    working["Gross Total Balance"] = pd.to_numeric(working["Total Balance"], errors="coerce")
    working["Gross Total Return"] = pd.to_numeric(working["Total Return"], errors="coerce")
    working["Turnover"] = _estimate_turnover_series(working)

    cost_rate = max(float(transaction_cost_bps or 0.0), 0.0) / 10000.0
    prev_net_balance: float | None = None
    net_balances: list[float] = []
    net_returns: list[float] = []
    estimated_costs: list[float] = []
    cumulative_cost = 0.0
    cumulative_costs: list[float] = []

    for _, row in working.iterrows():
        gross_balance = max(_coerce_float(row.get("Gross Total Balance")), 0.0)
        gross_return = row.get("Gross Total Return")
        turnover = max(_coerce_float(row.get("Turnover")), 0.0)

        if prev_net_balance is None or pd.isna(gross_return):
            pre_cost_balance = gross_balance
        else:
            pre_cost_balance = prev_net_balance * (1.0 + float(gross_return))

        estimated_cost = pre_cost_balance * cost_rate * turnover
        net_balance = max(pre_cost_balance - estimated_cost, 0.0)
        net_return = (
            np.nan
            if prev_net_balance is None or prev_net_balance == 0
            else (net_balance / prev_net_balance) - 1.0
        )

        cumulative_cost += estimated_cost
        net_balances.append(float(net_balance))
        net_returns.append(net_return)
        estimated_costs.append(float(estimated_cost))
        cumulative_costs.append(float(cumulative_cost))
        prev_net_balance = float(net_balance)

    working["Estimated Cost"] = estimated_costs
    working["Cumulative Estimated Cost"] = cumulative_costs
    working["Net Total Balance"] = net_balances
    working["Net Total Return"] = net_returns
    working["Total Balance"] = working["Net Total Balance"]
    working["Total Return"] = working["Net Total Return"]

    diagnostics = _turnover_diagnostics_from_result(working)
    estimated_cost_series = pd.to_numeric(working["Estimated Cost"], errors="coerce").fillna(0.0)
    gross_end_balance = float(working["Gross Total Balance"].iloc[-1]) if not working.empty else 0.0
    net_end_balance = float(working["Total Balance"].iloc[-1]) if not working.empty else 0.0
    estimated_cost_total = float(estimated_cost_series.sum()) if not working.empty else 0.0
    estimated_cost_positive_rows = int((estimated_cost_series > 0).sum())
    gross_net_end_balance_delta = float(gross_end_balance - net_end_balance)
    if float(transaction_cost_bps or 0.0) <= 0:
        net_curve_status = "applied_zero_cost_bps"
    elif diagnostics.get("turnover_estimation_status") != "estimated_from_holdings":
        net_curve_status = "applied_without_turnover_estimate"
    elif estimated_cost_total > 0 and gross_net_end_balance_delta > 0 and estimated_cost_positive_rows > 0:
        net_curve_status = "applied_with_measurable_cost"
    else:
        net_curve_status = "applied_no_cost_impact"
    diagnostics.update(
        {
            "net_cost_curve_contract_version": "net_cost_curve_contract_v1",
            "net_cost_curve_status": net_curve_status,
            "net_cost_curve_application_target": "result_df.Total Balance/Total Return",
            "total_balance_is_net_of_cost": True,
            "net_cost_curve_rows": int(len(working)),
            "estimated_cost_total": estimated_cost_total,
            "estimated_cost_positive_rows": estimated_cost_positive_rows,
            "gross_net_end_balance_delta": gross_net_end_balance_delta,
        }
    )
    return working, diagnostics


def _build_candidate_universe_equal_weight_benchmark_df(
    *,
    benchmark_universe_tickers: Sequence[str] | None,
    dates: pd.Series,
    start: str | None,
    end: str | None,
    timeframe: str,
    initial_balance: float,
) -> tuple[pd.DataFrame | None, dict[str, Any]]:
    tickers = _normalize_tickers(benchmark_universe_tickers)
    history = load_price_history(
        symbols=tickers,
        start=start,
        end=end,
        timeframe=timeframe,
    )
    if history.empty:
        return None, {
            "benchmark_label": "Candidate Universe EW Benchmark",
            "benchmark_symbol_count": len(tickers),
            "benchmark_eligible_symbol_count": 0,
        }

    working = history.loc[:, ["date", "symbol", "close"]].copy()
    working["date"] = pd.to_datetime(working["date"], errors="coerce")
    working["symbol"] = working["symbol"].astype(str).str.upper()
    working["close"] = pd.to_numeric(working["close"], errors="coerce")
    working = working.dropna(subset=["date", "symbol", "close"])
    if working.empty:
        return None, {
            "benchmark_label": "Candidate Universe EW Benchmark",
            "benchmark_symbol_count": len(tickers),
            "benchmark_eligible_symbol_count": 0,
        }

    pivot = (
        working.pivot_table(index="date", columns="symbol", values="close", aggfunc="last")
        .sort_index()
    )
    if pivot.empty:
        return None, {
            "benchmark_label": "Candidate Universe EW Benchmark",
            "benchmark_symbol_count": len(tickers),
            "benchmark_eligible_symbol_count": 0,
        }

    target_index = pd.Index(pd.to_datetime(dates).sort_values().unique(), name="Date")
    expanded_index = pivot.index.union(target_index)
    aligned_prices = pivot.reindex(expanded_index).sort_index().ffill().reindex(target_index)
    if aligned_prices.empty:
        return None, {
            "benchmark_label": "Candidate Universe EW Benchmark",
            "benchmark_symbol_count": len(tickers),
            "benchmark_eligible_symbol_count": 0,
        }

    first_row = aligned_prices.iloc[0]
    eligible_symbols = [
        str(symbol)
        for symbol, value in first_row.items()
        if pd.notna(value) and float(value) > 0.0
    ]
    if not eligible_symbols:
        return None, {
            "benchmark_label": "Candidate Universe EW Benchmark",
            "benchmark_symbol_count": len(tickers),
            "benchmark_eligible_symbol_count": 0,
        }

    eligible_prices = aligned_prices.loc[:, eligible_symbols].copy()
    base_prices = pd.to_numeric(eligible_prices.iloc[0], errors="coerce")
    eligible_prices = eligible_prices.loc[:, base_prices.notna() & (base_prices > 0.0)]
    if eligible_prices.empty:
        return None, {
            "benchmark_label": "Candidate Universe EW Benchmark",
            "benchmark_symbol_count": len(tickers),
            "benchmark_eligible_symbol_count": 0,
        }

    base_prices = pd.to_numeric(eligible_prices.iloc[0], errors="coerce")
    per_symbol_balance = float(initial_balance) / float(len(eligible_prices.columns))
    balance_matrix = eligible_prices.divide(base_prices, axis=1) * per_symbol_balance
    total_balance = balance_matrix.sum(axis=1, min_count=1)
    benchmark_df = pd.DataFrame(
        {
            "Date": target_index,
            "Benchmark Total Balance": total_balance.values,
        }
    )
    benchmark_df["Benchmark Total Return"] = benchmark_df["Benchmark Total Balance"].pct_change()
    return benchmark_df.reset_index(drop=True), {
        "benchmark_label": "Candidate Universe EW Benchmark",
        "benchmark_symbol_count": len(tickers),
        "benchmark_eligible_symbol_count": int(len(eligible_prices.columns)),
    }


def _build_benchmark_result_df(
    *,
    benchmark_contract: str | None,
    benchmark_ticker: str | None,
    benchmark_universe_tickers: Sequence[str] | None,
    dates: pd.Series,
    start: str | None,
    end: str | None,
    timeframe: str,
    initial_balance: float,
) -> tuple[pd.DataFrame | None, dict[str, Any]]:
    contract = str(benchmark_contract or STRICT_DEFAULT_BENCHMARK_CONTRACT).strip().lower()
    if contract == STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT:
        return _build_candidate_universe_equal_weight_benchmark_df(
            benchmark_universe_tickers=benchmark_universe_tickers,
            dates=dates,
            start=start,
            end=end,
            timeframe=timeframe,
            initial_balance=initial_balance,
        )

    symbol = str(benchmark_ticker or "").strip().upper()
    if not symbol:
        return None, {
            "benchmark_label": None,
            "benchmark_symbol_count": 1 if symbol else 0,
            "benchmark_eligible_symbol_count": 0,
        }

    history = load_price_history(
        symbols=[symbol],
        start=start,
        end=end,
        timeframe=timeframe,
    )
    if history.empty:
        return None, {
            "benchmark_label": f"{symbol} Benchmark",
            "benchmark_symbol_count": 1,
            "benchmark_eligible_symbol_count": 0,
        }

    benchmark_history = (
        history.loc[history["symbol"].astype(str).str.upper() == symbol, ["date", "close"]]
        .dropna(subset=["date", "close"])
        .sort_values("date")
        .rename(columns={"date": "price_date", "close": "Benchmark Close"})
        .reset_index(drop=True)
    )
    if benchmark_history.empty:
        return None, {
            "benchmark_label": f"{symbol} Benchmark",
            "benchmark_symbol_count": 1,
            "benchmark_eligible_symbol_count": 0,
        }

    target_dates = pd.DataFrame({"Date": pd.to_datetime(dates).sort_values().unique()})
    aligned = pd.merge_asof(
        target_dates.sort_values("Date"),
        benchmark_history,
        left_on="Date",
        right_on="price_date",
        direction="backward",
    ).dropna(subset=["Benchmark Close"])
    if aligned.empty:
        return None, {
            "benchmark_label": f"{symbol} Benchmark",
            "benchmark_symbol_count": 1,
            "benchmark_eligible_symbol_count": 0,
        }

    base_price = float(aligned.iloc[0]["Benchmark Close"])
    if base_price <= 0:
        return None, {
            "benchmark_label": f"{symbol} Benchmark",
            "benchmark_symbol_count": 1,
            "benchmark_eligible_symbol_count": 0,
        }

    aligned["Benchmark Total Balance"] = float(initial_balance) * (
        aligned["Benchmark Close"].astype(float) / base_price
    )
    aligned["Benchmark Total Return"] = aligned["Benchmark Total Balance"].pct_change()
    return aligned.reset_index(drop=True), {
        "benchmark_label": f"{symbol} Benchmark",
        "benchmark_symbol_count": 1,
        "benchmark_eligible_symbol_count": 1,
    }


def _resolve_guardrail_reference_ticker(
    benchmark_ticker: str | None,
    guardrail_reference_ticker: str | None,
) -> str:
    return str(
        guardrail_reference_ticker
        or benchmark_ticker
        or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK
    ).strip().upper()


def _compute_drawdown_stats(balance_series: pd.Series) -> tuple[float | None, float | None]:
    series = pd.to_numeric(balance_series, errors="coerce").dropna()
    if series.empty:
        return None, None

    drawdown = (series / series.cummax()) - 1.0
    return float(drawdown.iloc[-1]), float(drawdown.min())


def _compute_total_return(balance_series: pd.Series) -> float | None:
    series = pd.to_numeric(balance_series, errors="coerce").dropna()
    if len(series) < 2:
        return None
    base_value = float(series.iloc[0])
    end_value = float(series.iloc[-1])
    if base_value <= 0:
        return None
    return float((end_value / base_value) - 1.0)


def _rolling_validation_window(summary_freq: str) -> tuple[int, str]:
    normalized = str(summary_freq or "M").strip().upper()
    if normalized == "D":
        return 252, "252D"
    return 12, "12M"


def _build_real_money_validation_surface(
    *,
    strategy_df: pd.DataFrame,
    benchmark_df: pd.DataFrame,
    summary_freq: str,
) -> dict[str, Any]:
    aligned = pd.merge(
        strategy_df[["Date", "Total Balance", "Total Return"]].copy(),
        benchmark_df[["Date", "Benchmark Total Balance", "Benchmark Total Return"]].copy(),
        on="Date",
        how="inner",
    ).dropna(subset=["Total Balance", "Benchmark Total Balance"])
    if aligned.empty:
        return {}

    strategy_current_dd, strategy_max_dd = _compute_drawdown_stats(aligned["Total Balance"])
    benchmark_current_dd, benchmark_max_dd = _compute_drawdown_stats(aligned["Benchmark Total Balance"])

    window_size, window_label = _rolling_validation_window(summary_freq)
    strategy_returns = pd.to_numeric(aligned["Total Return"], errors="coerce")
    benchmark_returns = pd.to_numeric(aligned["Benchmark Total Return"], errors="coerce")

    strategy_roll = (1.0 + strategy_returns).rolling(window_size, min_periods=window_size).apply(np.prod, raw=True) - 1.0
    benchmark_roll = (1.0 + benchmark_returns).rolling(window_size, min_periods=window_size).apply(np.prod, raw=True) - 1.0
    rolling_excess = (strategy_roll - benchmark_roll).dropna()

    underperf_mask = rolling_excess < 0
    underperf_share = float(underperf_mask.mean()) if not rolling_excess.empty else None
    worst_excess = float(rolling_excess.min()) if not rolling_excess.empty else None
    latest_excess = float(rolling_excess.iloc[-1]) if not rolling_excess.empty else None

    current_streak = 0
    longest_streak = 0
    running_streak = 0
    for underperformed in underperf_mask.tolist():
        if underperformed:
            running_streak += 1
            longest_streak = max(longest_streak, running_streak)
        else:
            running_streak = 0
    current_streak = running_streak

    watch_signals: list[str] = []
    severe_signals = 0
    if strategy_max_dd is not None and benchmark_max_dd is not None and strategy_max_dd < (benchmark_max_dd - 0.05):
        watch_signals.append("drawdown_gap")
    if worst_excess is not None and worst_excess <= -0.10:
        watch_signals.append("worst_excess")
    if current_streak >= 3:
        watch_signals.append("current_underperformance_streak")
    if underperf_share is not None and underperf_share >= 0.60:
        watch_signals.append("underperformance_share")

    if strategy_max_dd is not None and benchmark_max_dd is not None and strategy_max_dd < (benchmark_max_dd - 0.10):
        severe_signals += 1
    if worst_excess is not None and worst_excess <= -0.15:
        severe_signals += 1
    if current_streak >= 4:
        severe_signals += 1

    if severe_signals > 0 or len(watch_signals) >= 2:
        validation_status = "caution"
    elif watch_signals:
        validation_status = "watch"
    else:
        validation_status = "normal"

    return {
        "validation_status": validation_status,
        "validation_window_periods": int(window_size),
        "validation_window_label": window_label,
        "strategy_current_drawdown": strategy_current_dd,
        "strategy_max_drawdown": strategy_max_dd,
        "benchmark_current_drawdown": benchmark_current_dd,
        "benchmark_max_drawdown": benchmark_max_dd,
        "rolling_underperformance_observations": int(len(rolling_excess)),
        "rolling_underperformance_share": underperf_share,
        "rolling_underperformance_current_streak": int(current_streak),
        "rolling_underperformance_longest_streak": int(longest_streak),
        "rolling_underperformance_worst_excess_return": worst_excess,
        "rolling_underperformance_latest_excess_return": latest_excess,
        "validation_watch_signals": watch_signals,
    }


def _build_rolling_and_out_of_sample_review_surface(
    *,
    strategy_df: pd.DataFrame,
    benchmark_df: pd.DataFrame,
    summary_freq: str,
) -> dict[str, Any]:
    aligned = pd.merge(
        strategy_df[["Date", "Total Balance", "Total Return"]].copy(),
        benchmark_df[["Date", "Benchmark Total Balance", "Benchmark Total Return"]].copy(),
        on="Date",
        how="inner",
    ).dropna(subset=["Total Balance", "Benchmark Total Balance"])
    if aligned.empty:
        return {}

    aligned = aligned.sort_values("Date").reset_index(drop=True)
    window_size, window_label = _rolling_validation_window(summary_freq)
    observations = int(len(aligned))

    review: dict[str, Any] = {
        "rolling_review_window_periods": int(window_size),
        "rolling_review_window_label": window_label,
        "rolling_review_observations": observations,
        "out_of_sample_review_observations": observations,
    }

    if observations < window_size:
        review.update(
            {
                "rolling_review_status": "unavailable",
                "rolling_review_rationale": ["insufficient_recent_window_history"],
            }
        )
    else:
        recent = aligned.tail(window_size).copy()
        previous = aligned.iloc[-(window_size * 2) : -window_size].copy() if observations >= (window_size * 2) else pd.DataFrame()

        recent_strategy_return = _compute_total_return(recent["Total Balance"])
        recent_benchmark_return = _compute_total_return(recent["Benchmark Total Balance"])
        recent_excess = (
            float(recent_strategy_return - recent_benchmark_return)
            if recent_strategy_return is not None and recent_benchmark_return is not None
            else None
        )
        _, recent_strategy_max_dd = _compute_drawdown_stats(recent["Total Balance"])
        _, recent_benchmark_max_dd = _compute_drawdown_stats(recent["Benchmark Total Balance"])
        recent_drawdown_gap = (
            float(recent_strategy_max_dd - recent_benchmark_max_dd)
            if recent_strategy_max_dd is not None and recent_benchmark_max_dd is not None
            else None
        )

        previous_excess = None
        if not previous.empty:
            previous_strategy_return = _compute_total_return(previous["Total Balance"])
            previous_benchmark_return = _compute_total_return(previous["Benchmark Total Balance"])
            if previous_strategy_return is not None and previous_benchmark_return is not None:
                previous_excess = float(previous_strategy_return - previous_benchmark_return)

        rolling_signals: list[str] = []
        rolling_severe_signals = 0
        if recent_excess is not None:
            if recent_excess < 0:
                rolling_signals.append("recent_window_underperformance")
            if recent_excess <= -0.10:
                rolling_severe_signals += 1
        if recent_drawdown_gap is not None:
            if recent_drawdown_gap < -0.05:
                rolling_signals.append("recent_window_drawdown_gap")
            if recent_drawdown_gap <= -0.10:
                rolling_severe_signals += 1
        if previous_excess is not None and recent_excess is not None:
            deterioration = float(recent_excess - previous_excess)
            if deterioration <= -0.10:
                rolling_signals.append("recent_window_deterioration")
            if deterioration <= -0.15:
                rolling_severe_signals += 1
            review["rolling_review_recent_vs_previous_excess_change"] = deterioration

        if rolling_severe_signals > 0 or len(rolling_signals) >= 2:
            rolling_status = "caution"
        elif rolling_signals:
            rolling_status = "watch"
        else:
            rolling_status = "normal"

        review.update(
            {
                "rolling_review_status": rolling_status,
                "rolling_review_rationale": rolling_signals,
                "rolling_review_recent_excess_return": recent_excess,
                "rolling_review_previous_excess_return": previous_excess,
                "rolling_review_recent_strategy_max_drawdown": recent_strategy_max_dd,
                "rolling_review_recent_benchmark_max_drawdown": recent_benchmark_max_dd,
                "rolling_review_recent_drawdown_gap": recent_drawdown_gap,
                "rolling_review_recent_start": recent["Date"].iloc[0],
                "rolling_review_recent_end": recent["Date"].iloc[-1],
            }
        )

    if observations < 6:
        review.update(
            {
                "out_of_sample_review_status": "unavailable",
                "out_of_sample_review_rationale": ["insufficient_split_sample_history"],
            }
        )
        return review

    split_index = max(1, observations // 2)
    if split_index >= observations:
        review.update(
            {
                "out_of_sample_review_status": "unavailable",
                "out_of_sample_review_rationale": ["insufficient_split_sample_history"],
            }
        )
        return review

    in_sample = aligned.iloc[:split_index].copy()
    out_of_sample = aligned.iloc[split_index:].copy()
    if len(in_sample) < 2 or len(out_of_sample) < 2:
        review.update(
            {
                "out_of_sample_review_status": "unavailable",
                "out_of_sample_review_rationale": ["insufficient_split_sample_history"],
            }
        )
        return review

    in_strategy_return = _compute_total_return(in_sample["Total Balance"])
    in_benchmark_return = _compute_total_return(in_sample["Benchmark Total Balance"])
    out_strategy_return = _compute_total_return(out_of_sample["Total Balance"])
    out_benchmark_return = _compute_total_return(out_of_sample["Benchmark Total Balance"])

    in_excess = (
        float(in_strategy_return - in_benchmark_return)
        if in_strategy_return is not None and in_benchmark_return is not None
        else None
    )
    out_excess = (
        float(out_strategy_return - out_benchmark_return)
        if out_strategy_return is not None and out_benchmark_return is not None
        else None
    )
    _, in_max_dd = _compute_drawdown_stats(in_sample["Total Balance"])
    _, in_benchmark_max_dd = _compute_drawdown_stats(in_sample["Benchmark Total Balance"])
    _, out_max_dd = _compute_drawdown_stats(out_of_sample["Total Balance"])
    _, out_benchmark_max_dd = _compute_drawdown_stats(out_of_sample["Benchmark Total Balance"])

    out_drawdown_gap = (
        float(out_max_dd - out_benchmark_max_dd)
        if out_max_dd is not None and out_benchmark_max_dd is not None
        else None
    )
    excess_change = float(out_excess - in_excess) if out_excess is not None and in_excess is not None else None

    out_signals: list[str] = []
    out_severe_signals = 0
    if out_excess is not None:
        if out_excess < 0:
            out_signals.append("out_of_sample_underperformance")
        if out_excess <= -0.10:
            out_severe_signals += 1
    if out_drawdown_gap is not None:
        if out_drawdown_gap < -0.05:
            out_signals.append("out_of_sample_drawdown_gap")
        if out_drawdown_gap <= -0.10:
            out_severe_signals += 1
    if excess_change is not None:
        if excess_change <= -0.10:
            out_signals.append("split_period_deterioration")
        if excess_change <= -0.15:
            out_severe_signals += 1

    if out_severe_signals > 0 or len(out_signals) >= 2:
        out_status = "caution"
    elif out_signals:
        out_status = "watch"
    else:
        out_status = "normal"

    review.update(
        {
            "out_of_sample_review_status": out_status,
            "out_of_sample_review_rationale": out_signals,
            "out_of_sample_in_sample_excess_return": in_excess,
            "out_of_sample_out_sample_excess_return": out_excess,
            "out_of_sample_excess_change": excess_change,
            "out_of_sample_in_sample_start": in_sample["Date"].iloc[0],
            "out_of_sample_in_sample_end": in_sample["Date"].iloc[-1],
            "out_of_sample_out_sample_start": out_of_sample["Date"].iloc[0],
            "out_of_sample_out_sample_end": out_of_sample["Date"].iloc[-1],
            "out_of_sample_in_sample_strategy_max_drawdown": in_max_dd,
            "out_of_sample_in_sample_benchmark_max_drawdown": in_benchmark_max_dd,
            "out_of_sample_out_sample_strategy_max_drawdown": out_max_dd,
            "out_of_sample_out_sample_benchmark_max_drawdown": out_benchmark_max_dd,
            "out_of_sample_out_sample_drawdown_gap": out_drawdown_gap,
        }
    )
    return review


def _build_promotion_decision(meta: dict[str, Any]) -> dict[str, Any]:
    benchmark_available = bool(meta.get("benchmark_available"))
    validation_status = str(meta.get("validation_status") or "").strip().lower()
    benchmark_policy_status = str(meta.get("benchmark_policy_status") or "").strip().lower()
    etf_operability_status = str(meta.get("etf_operability_status") or "").strip().lower()
    liquidity_policy_status = str(meta.get("liquidity_policy_status") or "").strip().lower()
    validation_policy_status = str(meta.get("validation_policy_status") or "").strip().lower()
    guardrail_policy_status = str(meta.get("guardrail_policy_status") or "").strip().lower()
    universe_contract = meta.get("universe_contract")
    price_freshness = meta.get("price_freshness") or {}
    freshness_status = str(price_freshness.get("status") or "").strip().lower()

    rationale: list[str] = []
    if not benchmark_available:
        rationale.append("benchmark_unavailable")
    if validation_status == "caution":
        rationale.append("validation_caution")
    elif validation_status == "watch":
        rationale.append("validation_watch")
    if benchmark_policy_status == "caution":
        rationale.append("benchmark_policy_caution")
    elif benchmark_policy_status == "watch":
        rationale.append("benchmark_policy_watch")
    elif benchmark_policy_status == "unavailable":
        rationale.append("benchmark_policy_unavailable")
    if etf_operability_status == "caution":
        rationale.append("etf_operability_caution")
    elif etf_operability_status == "watch":
        rationale.append("etf_operability_watch")
    elif etf_operability_status == "unavailable":
        rationale.append("etf_operability_unavailable")
    if liquidity_policy_status == "caution":
        rationale.append("liquidity_policy_caution")
    elif liquidity_policy_status == "watch":
        rationale.append("liquidity_policy_watch")
    elif liquidity_policy_status == "unavailable":
        rationale.append("liquidity_policy_unavailable")
    if validation_policy_status == "caution":
        rationale.append("validation_policy_caution")
    elif validation_policy_status == "watch":
        rationale.append("validation_policy_watch")
    elif validation_policy_status == "unavailable":
        rationale.append("validation_policy_unavailable")
    if guardrail_policy_status == "caution":
        rationale.append("guardrail_policy_caution")
    elif guardrail_policy_status == "watch":
        rationale.append("guardrail_policy_watch")
    elif guardrail_policy_status == "unavailable":
        rationale.append("guardrail_policy_unavailable")
    if universe_contract == STATIC_MANAGED_RESEARCH_UNIVERSE:
        rationale.append("static_universe_contract")
    if freshness_status == "warning":
        rationale.append("price_freshness_warning")
    elif freshness_status == "error":
        rationale.append("price_freshness_error")

    if (
        benchmark_available
        and validation_status == "normal"
        and benchmark_policy_status in {"", "normal"}
        and etf_operability_status in {"", "normal"}
        and liquidity_policy_status in {"", "normal"}
        and validation_policy_status in {"", "normal"}
        and guardrail_policy_status in {"", "normal"}
        and universe_contract != STATIC_MANAGED_RESEARCH_UNIVERSE
        and freshness_status not in {"warning", "error"}
    ):
        decision = "real_money_candidate"
        next_step = "paper_trade_or_small_capital_probation"
    elif (
        not benchmark_available
        or validation_status == "caution"
        or benchmark_policy_status == "caution"
        or etf_operability_status in {"caution", "unavailable"}
        or liquidity_policy_status in {"caution", "unavailable"}
        or validation_policy_status in {"caution", "unavailable"}
        or guardrail_policy_status in {"caution", "unavailable"}
        or freshness_status == "error"
    ):
        decision = "hold"
        next_step = "resolve_validation_gaps_before_promotion"
    else:
        decision = "production_candidate"
        next_step = "run_more_robustness_and_guardrail_review"

    return {
        "promotion_decision": decision,
        "promotion_rationale": rationale,
        "promotion_next_step": next_step,
    }


def _build_shortlist_contract(meta: dict[str, Any]) -> dict[str, Any]:
    decision = str(meta.get("promotion_decision") or "").strip().lower()
    strategy_key = str(meta.get("strategy_key") or "").strip().lower()
    strategy_family = str(meta.get("strategy_family") or meta.get("strategy_name") or "").strip()
    universe_contract = str(meta.get("universe_contract") or "").strip().lower()
    benchmark_contract = str(meta.get("benchmark_contract") or "").strip().lower()
    benchmark_available = bool(meta.get("benchmark_available"))
    drawdown_guardrail_enabled = bool(meta.get("drawdown_guardrail_enabled"))
    underperformance_guardrail_enabled = bool(meta.get("underperformance_guardrail_enabled"))

    if not decision:
        return {}

    rationale: list[str] = []
    status: str
    next_step: str

    if decision == "hold":
        status = "hold"
        next_step = "resolve_contract_gaps_before_shortlist"
        rationale.append("promotion_hold")
    elif decision == "production_candidate":
        status = "watchlist"
        next_step = "manual_review_then_paper_probation_gate"
        rationale.append("promotion_production_candidate")
    else:
        is_etf_strategy = strategy_key in ETF_OPERABILITY_STRATEGY_KEYS
        annual_small_capital_ready = (
            not is_etf_strategy
            and drawdown_guardrail_enabled
            and underperformance_guardrail_enabled
            and benchmark_available
            and universe_contract != STATIC_MANAGED_RESEARCH_UNIVERSE
            and benchmark_contract == STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT
        )
        if annual_small_capital_ready:
            status = "small_capital_trial"
            next_step = "start_small_capital_trial_with_monthly_review"
            rationale.extend(
                [
                    "promotion_real_money_candidate",
                    "annual_guardrails_enabled",
                    "candidate_equal_weight_benchmark",
                ]
            )
        else:
            status = "paper_probation"
            next_step = "start_paper_probation_and_monitor_monthly"
            rationale.append("promotion_real_money_candidate")
            if is_etf_strategy:
                rationale.append("etf_second_pass_pending")
            else:
                rationale.append("paper_probation_first")

    return {
        "shortlist_status": status,
        "shortlist_next_step": next_step,
        "shortlist_rationale": rationale,
        "shortlist_family": strategy_family,
    }


def _build_probation_and_monitoring_contract(meta: dict[str, Any]) -> dict[str, Any]:
    shortlist_status = str(meta.get("shortlist_status") or "").strip().lower()
    strategy_key = str(meta.get("strategy_key") or "").strip().lower()
    strategy_family = str(meta.get("shortlist_family") or meta.get("strategy_family") or "").strip()
    benchmark_available = bool(meta.get("benchmark_available"))
    price_freshness = meta.get("price_freshness") or {}
    freshness_status = str(price_freshness.get("status") or "").strip().lower()

    if not shortlist_status:
        return {}

    probation_status: str
    probation_stage: str
    probation_review_frequency: str
    probation_next_step: str
    probation_rationale: list[str] = []

    if shortlist_status == "hold":
        probation_status = "not_ready"
        probation_stage = "contract_gap_resolution"
        probation_review_frequency = "ad_hoc"
        probation_next_step = "resolve_contract_gaps_before_probation"
        probation_rationale.append("shortlist_hold")
    elif shortlist_status == "watchlist":
        probation_status = "watchlist_review"
        probation_stage = "pre_probation_review"
        probation_review_frequency = "monthly"
        probation_next_step = "review_robustness_and_policy_gaps_before_paper_probation"
        probation_rationale.append("shortlist_watchlist")
    elif shortlist_status == "small_capital_trial":
        probation_status = "small_capital_live_trial"
        probation_stage = "live_probation"
        probation_review_frequency = "monthly"
        probation_next_step = "run_small_capital_trial_with_monthly_breach_review"
        probation_rationale.append("shortlist_small_capital_trial")
    else:
        probation_status = "paper_tracking"
        probation_stage = "paper_probation"
        probation_review_frequency = "monthly"
        probation_next_step = "track_paper_results_and_recheck_policy_monthly"
        probation_rationale.append("shortlist_paper_probation")

    monitoring_focus: list[str] = []
    if benchmark_available:
        monitoring_focus.append("benchmark_relative_validation")
    if meta.get("underperformance_guardrail_enabled") or meta.get("rolling_underperformance_share") is not None:
        monitoring_focus.append("rolling_underperformance")
    if meta.get("drawdown_guardrail_enabled") or meta.get("strategy_max_drawdown") is not None:
        monitoring_focus.append("drawdown_control")
    if meta.get("rolling_review_status"):
        monitoring_focus.append("recent_regime_review")
    if meta.get("out_of_sample_review_status"):
        monitoring_focus.append("split_period_consistency")
    if meta.get("liquidity_policy_status"):
        monitoring_focus.append("liquidity_cleanliness")
    if strategy_key in ETF_OPERABILITY_STRATEGY_KEYS or str(meta.get("etf_operability_status") or "").strip():
        monitoring_focus.append("etf_operability")
    if freshness_status:
        monitoring_focus.append("price_freshness")

    watch_signals: list[str] = []
    severe_signals: list[str] = []

    def _register_policy_signal(name: str, value: Any) -> None:
        status = str(value or "").strip().lower()
        if status in {"caution", "unavailable", "error"}:
            severe_signals.append(f"{name}_{status}")
        elif status in {"watch", "warning"}:
            watch_signals.append(f"{name}_{status}")

    _register_policy_signal("validation", meta.get("validation_status"))
    _register_policy_signal("benchmark_policy", meta.get("benchmark_policy_status"))
    _register_policy_signal("etf_operability", meta.get("etf_operability_status"))
    _register_policy_signal("liquidity_policy", meta.get("liquidity_policy_status"))
    _register_policy_signal("validation_policy", meta.get("validation_policy_status"))
    _register_policy_signal("guardrail_policy", meta.get("guardrail_policy_status"))
    _register_policy_signal("price_freshness", freshness_status)

    rolling_review_status = str(meta.get("rolling_review_status") or "").strip().lower()
    if rolling_review_status == "caution":
        severe_signals.append("rolling_review_caution")
    elif rolling_review_status in {"watch", "unavailable"}:
        watch_signals.append(f"rolling_review_{rolling_review_status}")

    out_of_sample_review_status = str(meta.get("out_of_sample_review_status") or "").strip().lower()
    if out_of_sample_review_status == "caution":
        severe_signals.append("out_of_sample_review_caution")
    elif out_of_sample_review_status in {"watch", "unavailable"}:
        watch_signals.append(f"out_of_sample_review_{out_of_sample_review_status}")

    under_trigger_count = int(meta.get("underperformance_guardrail_trigger_count") or 0)
    drawdown_trigger_count = int(meta.get("drawdown_guardrail_trigger_count") or 0)
    if under_trigger_count > 0:
        severe_signals.append("underperformance_guardrail_triggered")
    if drawdown_trigger_count > 0:
        severe_signals.append("drawdown_guardrail_triggered")

    monitoring_breach_signals = severe_signals + watch_signals
    if probation_status == "not_ready":
        monitoring_status = "blocked"
        monitoring_review_frequency = "ad_hoc"
        monitoring_next_step = "resolve_blockers_before_monitoring"
    elif severe_signals:
        monitoring_status = "breach_watch"
        monitoring_review_frequency = "monthly"
        monitoring_next_step = "review_breach_signals_before_capital_increase"
    elif watch_signals:
        monitoring_status = "heightened_review"
        monitoring_review_frequency = "monthly"
        monitoring_next_step = "continue_monthly_review_and_track_watch_signals"
    else:
        monitoring_status = "routine_review"
        monitoring_review_frequency = "monthly"
        monitoring_next_step = "continue_probation_and_record_monthly_notes"

    return {
        "probation_status": probation_status,
        "probation_stage": probation_stage,
        "probation_review_frequency": probation_review_frequency,
        "probation_next_step": probation_next_step,
        "probation_rationale": probation_rationale,
        "monitoring_status": monitoring_status,
        "monitoring_focus": monitoring_focus,
        "monitoring_breach_signals": monitoring_breach_signals,
        "monitoring_review_frequency": monitoring_review_frequency,
        "monitoring_next_step": monitoring_next_step,
        "monitoring_family": strategy_family,
    }


def _policy_status_to_check_status(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in {"", "normal"}:
        return "pass"
    if normalized == "watch":
        return "watch"
    if normalized == "unavailable":
        return "unavailable"
    return "fail"


def _build_deployment_readiness_contract(meta: dict[str, Any]) -> dict[str, Any]:
    checklist_rows: list[dict[str, Any]] = []

    def add_row(check: str, status: str, detail: str) -> None:
        checklist_rows.append(
            {
                "Check": check,
                "Status": status,
                "Detail": detail,
            }
        )

    benchmark_available = bool(meta.get("benchmark_available"))
    benchmark_contract = str(meta.get("benchmark_contract") or "").strip().lower()
    universe_contract = str(meta.get("universe_contract") or "").strip().lower()
    freshness_status = str((meta.get("price_freshness") or {}).get("status") or "").strip().lower()
    rolling_review_status = str(meta.get("rolling_review_status") or "").strip().lower()
    out_of_sample_review_status = str(meta.get("out_of_sample_review_status") or "").strip().lower()
    benchmark_policy_status = str(meta.get("benchmark_policy_status") or "").strip().lower()
    liquidity_policy_status = str(meta.get("liquidity_policy_status") or "").strip().lower()
    validation_policy_status = str(meta.get("validation_policy_status") or "").strip().lower()
    guardrail_policy_status = str(meta.get("guardrail_policy_status") or "").strip().lower()
    etf_operability_status = str(meta.get("etf_operability_status") or "").strip().lower()

    if universe_contract:
        universe_status = "fail" if universe_contract == STATIC_MANAGED_RESEARCH_UNIVERSE else "pass"
        add_row(
            "Universe Contract",
            universe_status,
            "historical dynamic PIT가 아니면 strict annual 실전 해석은 더 보수적으로 본다"
            if universe_status == "fail"
            else "dynamic PIT contract 기준으로 해석 가능",
        )

    add_row(
        "Benchmark Availability",
        "pass" if benchmark_available else "fail",
        "benchmark overlay available" if benchmark_available else "benchmark overlay unavailable",
    )

    if benchmark_contract:
        add_row(
            "Benchmark Contract",
            "pass" if benchmark_contract else "unavailable",
            str(meta.get("benchmark_label") or meta.get("benchmark_ticker") or benchmark_contract),
        )

    if benchmark_policy_status:
        add_row("Benchmark Policy", _policy_status_to_check_status(benchmark_policy_status), benchmark_policy_status)
    if liquidity_policy_status:
        add_row("Liquidity Policy", _policy_status_to_check_status(liquidity_policy_status), liquidity_policy_status)
    if validation_policy_status:
        add_row("Validation Policy", _policy_status_to_check_status(validation_policy_status), validation_policy_status)
    if guardrail_policy_status:
        add_row("Guardrail Policy", _policy_status_to_check_status(guardrail_policy_status), guardrail_policy_status)
    if etf_operability_status:
        add_row("ETF Operability", _policy_status_to_check_status(etf_operability_status), etf_operability_status)

    if freshness_status:
        freshness_check_status = "pass"
        if freshness_status == "warning":
            freshness_check_status = "watch"
        elif freshness_status == "error":
            freshness_check_status = "fail"
        add_row("Price Freshness", freshness_check_status, freshness_status)

    if rolling_review_status:
        add_row("Rolling Review", _policy_status_to_check_status(rolling_review_status), rolling_review_status)
    if out_of_sample_review_status:
        add_row(
            "Split-Period Review",
            _policy_status_to_check_status(out_of_sample_review_status),
            out_of_sample_review_status,
        )

    pass_count = sum(1 for row in checklist_rows if row["Status"] == "pass")
    watch_count = sum(1 for row in checklist_rows if row["Status"] == "watch")
    fail_count = sum(1 for row in checklist_rows if row["Status"] == "fail")
    unavailable_count = sum(1 for row in checklist_rows if row["Status"] == "unavailable")

    rationale: list[str] = []
    if fail_count > 0:
        status = "blocked"
        next_step = "resolve_preview_gaps_before_validation_handoff"
        rationale.append("source_checks_block_progress")
    elif unavailable_count > 0:
        status = "review_required"
        next_step = "resolve_unavailable_preview_evidence"
        rationale.append("preview_evidence_unavailable")
    elif watch_count > 0:
        status = "review_required"
        next_step = "review_watch_items_before_validation_handoff"
        rationale.append("source_checks_need_review")
    else:
        status = "small_capital_ready"
        next_step = "send_to_practical_validation_for_execution_review"
        rationale.append("source_checks_ready_for_next_review")

    return {
        "deployment_readiness_status": status,
        "deployment_readiness_next_step": next_step,
        "deployment_readiness_rationale": rationale,
        "deployment_checklist_rows": checklist_rows,
        "deployment_check_pass_count": int(pass_count),
        "deployment_check_watch_count": int(watch_count),
        "deployment_check_fail_count": int(fail_count),
        "deployment_check_unavailable_count": int(unavailable_count),
    }


def _build_benchmark_policy_surface(meta: dict[str, Any]) -> dict[str, Any]:
    min_coverage_raw = meta.get("promotion_min_benchmark_coverage")
    min_spread_raw = meta.get("promotion_min_net_cagr_spread")
    if min_coverage_raw is None and min_spread_raw is None:
        return {}

    benchmark_available = bool(meta.get("benchmark_available"))
    coverage = meta.get("benchmark_row_coverage")
    spread = meta.get("net_cagr_spread")
    min_coverage = float(min_coverage_raw) if min_coverage_raw is not None else None
    min_spread = float(min_spread_raw) if min_spread_raw is not None else None

    watch_signals: list[str] = []
    severe_signals = 0
    coverage_pass: bool | None = None
    spread_pass: bool | None = None

    if not benchmark_available:
        return {
            "benchmark_policy_status": "unavailable",
            "benchmark_policy_watch_signals": ["benchmark_unavailable"],
            "benchmark_policy_coverage_pass": coverage_pass,
            "benchmark_policy_spread_pass": spread_pass,
        }

    if min_coverage is not None:
        if coverage is None:
            coverage_pass = None
            watch_signals.append("benchmark_coverage_missing")
            severe_signals += 1
        else:
            coverage_value = float(coverage)
            coverage_pass = coverage_value >= min_coverage
            if not coverage_pass:
                watch_signals.append("benchmark_coverage_below_policy")
                if coverage_value < max(0.0, min_coverage - 0.10):
                    severe_signals += 1

    if min_spread is not None:
        if spread is None:
            spread_pass = None
            watch_signals.append("net_cagr_spread_missing")
            severe_signals += 1
        else:
            spread_value = float(spread)
            spread_pass = spread_value >= min_spread
            if not spread_pass:
                watch_signals.append("net_cagr_spread_below_policy")
                if spread_value < (min_spread - 0.05):
                    severe_signals += 1

    if severe_signals > 0:
        status = "caution"
    elif watch_signals:
        status = "watch"
    else:
        status = "normal"

    return {
        "benchmark_policy_status": status,
        "benchmark_policy_watch_signals": watch_signals,
        "benchmark_policy_coverage_pass": coverage_pass,
        "benchmark_policy_spread_pass": spread_pass,
    }


def _build_liquidity_policy_surface(meta: dict[str, Any]) -> dict[str, Any]:
    min_clean_coverage_raw = meta.get("promotion_min_liquidity_clean_coverage")
    if min_clean_coverage_raw is None:
        return {}

    min_avg_dollar_volume = float(meta.get("min_avg_dollar_volume_20d_m_filter") or 0.0)
    clean_coverage = meta.get("liquidity_clean_coverage")
    min_clean_coverage = float(min_clean_coverage_raw)

    if min_avg_dollar_volume <= 0.0:
        return {
            "liquidity_policy_status": "unavailable",
            "liquidity_policy_watch_signals": ["liquidity_filter_disabled"],
            "liquidity_policy_clean_coverage_pass": None,
        }

    if clean_coverage is None:
        return {
            "liquidity_policy_status": "unavailable",
            "liquidity_policy_watch_signals": ["liquidity_coverage_missing"],
            "liquidity_policy_clean_coverage_pass": None,
        }

    clean_coverage_value = float(clean_coverage)
    coverage_pass = clean_coverage_value >= min_clean_coverage
    if coverage_pass:
        status = "normal"
        watch_signals: list[str] = []
    else:
        watch_signals = ["liquidity_clean_coverage_below_policy"]
        if clean_coverage_value < max(0.0, min_clean_coverage - 0.10):
            status = "caution"
        else:
            status = "watch"

    return {
        "liquidity_policy_status": status,
        "liquidity_policy_watch_signals": watch_signals,
        "liquidity_policy_clean_coverage_pass": coverage_pass,
    }


def _build_validation_policy_surface(meta: dict[str, Any]) -> dict[str, Any]:
    max_share_raw = meta.get("promotion_max_underperformance_share")
    min_worst_raw = meta.get("promotion_min_worst_rolling_excess_return")
    if max_share_raw is None and min_worst_raw is None:
        return {}

    benchmark_available = bool(meta.get("benchmark_available"))
    share = meta.get("rolling_underperformance_share")
    worst = meta.get("rolling_underperformance_worst_excess_return")
    observations = int(meta.get("rolling_underperformance_observations") or 0)
    max_share = float(max_share_raw) if max_share_raw is not None else None
    min_worst = float(min_worst_raw) if min_worst_raw is not None else None

    watch_signals: list[str] = []
    severe_signals = 0
    share_pass: bool | None = None
    worst_pass: bool | None = None

    if not benchmark_available or observations <= 0:
        unavailable_signals: list[str] = []
        if not benchmark_available:
            unavailable_signals.append("validation_policy_benchmark_unavailable")
        if observations <= 0:
            unavailable_signals.append("validation_policy_observations_missing")
        return {
            "validation_policy_status": "unavailable",
            "validation_policy_watch_signals": unavailable_signals,
            "validation_policy_share_pass": share_pass,
            "validation_policy_worst_excess_pass": worst_pass,
        }

    if max_share is not None:
        if share is None:
            watch_signals.append("underperformance_share_missing")
            severe_signals += 1
        else:
            share_value = float(share)
            share_pass = share_value <= max_share
            if not share_pass:
                watch_signals.append("underperformance_share_above_policy")
                if share_value > min(1.0, max_share + 0.10):
                    severe_signals += 1

    if min_worst is not None:
        if worst is None:
            watch_signals.append("worst_rolling_excess_missing")
            severe_signals += 1
        else:
            worst_value = float(worst)
            worst_pass = worst_value >= min_worst
            if not worst_pass:
                watch_signals.append("worst_rolling_excess_below_policy")
                if worst_value < (min_worst - 0.05):
                    severe_signals += 1

    if severe_signals > 0:
        status = "caution"
    elif watch_signals:
        status = "watch"
    else:
        status = "normal"

    return {
        "validation_policy_status": status,
        "validation_policy_watch_signals": watch_signals,
        "validation_policy_share_pass": share_pass,
        "validation_policy_worst_excess_pass": worst_pass,
    }


def _build_guardrail_policy_surface(meta: dict[str, Any]) -> dict[str, Any]:
    max_strategy_dd_raw = meta.get("promotion_max_strategy_drawdown")
    max_drawdown_gap_raw = meta.get("promotion_max_drawdown_gap_vs_benchmark")
    if max_strategy_dd_raw is None and max_drawdown_gap_raw is None:
        return {}

    strategy_max_drawdown = meta.get("strategy_max_drawdown")
    benchmark_available = bool(meta.get("benchmark_available"))
    benchmark_max_drawdown = meta.get("benchmark_max_drawdown")
    max_strategy_drawdown = float(max_strategy_dd_raw) if max_strategy_dd_raw is not None else None
    max_drawdown_gap = float(max_drawdown_gap_raw) if max_drawdown_gap_raw is not None else None

    strategy_drawdown_pass: bool | None = None
    drawdown_gap_pass: bool | None = None
    drawdown_gap_vs_benchmark: float | None = None
    unavailable_signals: list[str] = []
    watch_signals: list[str] = []
    severe_signals = 0

    if max_strategy_drawdown is not None:
        if strategy_max_drawdown is None:
            unavailable_signals.append("strategy_drawdown_missing")
        else:
            strategy_drawdown_value = float(strategy_max_drawdown)
            strategy_drawdown_pass = strategy_drawdown_value >= max_strategy_drawdown
            if not strategy_drawdown_pass:
                watch_signals.append("strategy_drawdown_above_policy")
                if strategy_drawdown_value < (max_strategy_drawdown - 0.05):
                    severe_signals += 1

    if max_drawdown_gap is not None:
        if not benchmark_available or benchmark_max_drawdown is None or strategy_max_drawdown is None:
            if not benchmark_available or benchmark_max_drawdown is None:
                unavailable_signals.append("guardrail_policy_benchmark_unavailable")
            if strategy_max_drawdown is None:
                unavailable_signals.append("guardrail_policy_strategy_drawdown_missing")
        else:
            drawdown_gap_vs_benchmark = float(benchmark_max_drawdown) - float(strategy_max_drawdown)
            drawdown_gap_pass = drawdown_gap_vs_benchmark <= max_drawdown_gap
            if not drawdown_gap_pass:
                watch_signals.append("drawdown_gap_above_policy")
                if drawdown_gap_vs_benchmark > (max_drawdown_gap + 0.05):
                    severe_signals += 1

    if unavailable_signals:
        return {
            "guardrail_policy_status": "unavailable",
            "guardrail_policy_watch_signals": unavailable_signals,
            "guardrail_policy_strategy_drawdown_pass": strategy_drawdown_pass,
            "guardrail_policy_drawdown_gap_pass": drawdown_gap_pass,
            "drawdown_gap_vs_benchmark": drawdown_gap_vs_benchmark,
        }

    if severe_signals > 0:
        status = "caution"
    elif watch_signals:
        status = "watch"
    else:
        status = "normal"

    return {
        "guardrail_policy_status": status,
        "guardrail_policy_watch_signals": watch_signals,
        "guardrail_policy_strategy_drawdown_pass": strategy_drawdown_pass,
        "guardrail_policy_drawdown_gap_pass": drawdown_gap_pass,
        "drawdown_gap_vs_benchmark": drawdown_gap_vs_benchmark,
    }


def _build_etf_operability_policy_surface(meta: dict[str, Any]) -> dict[str, Any]:
    min_aum_raw = meta.get("promotion_min_etf_aum_b")
    max_spread_raw = meta.get("promotion_max_bid_ask_spread_pct")
    if min_aum_raw is None and max_spread_raw is None:
        return {}

    strategy_key = str(meta.get("strategy_key") or "").strip()
    if strategy_key not in ETF_OPERABILITY_STRATEGY_KEYS:
        return {}

    tickers = _normalize_tickers(meta.get("tickers") or [])
    if not tickers:
        return {
            "etf_operability_status": "unavailable",
            "etf_operability_watch_signals": ["etf_operability_universe_empty"],
        }

    profile_df = load_asset_profile_status_summary(tickers)
    if profile_df.empty:
        return {
            "etf_operability_status": "unavailable",
            "etf_operability_watch_signals": ["etf_operability_profile_missing"],
            "etf_symbol_count": len(tickers),
            "etf_profile_symbol_count": 0,
        }

    working = profile_df.copy()
    working["symbol"] = working["symbol"].astype(str).str.upper()
    if "kind" in working.columns:
        working["kind"] = working["kind"].astype(str).str.lower()
    if "quote_type" in working.columns:
        working["quote_type"] = working["quote_type"].astype(str).str.upper()

    etf_mask = pd.Series(False, index=working.index)
    if "kind" in working.columns:
        etf_mask = etf_mask | working["kind"].eq("etf")
    if "quote_type" in working.columns:
        etf_mask = etf_mask | working["quote_type"].eq("ETF")
    etf_rows = working.loc[etf_mask].copy()
    if etf_rows.empty:
        return {
            "etf_operability_status": "unavailable",
            "etf_operability_watch_signals": ["etf_operability_no_etf_profile_rows"],
            "etf_symbol_count": len(tickers),
            "etf_profile_symbol_count": 0,
        }

    min_aum_b = float(min_aum_raw) if min_aum_raw is not None else None
    max_spread_pct = float(max_spread_raw) if max_spread_raw is not None else None

    etf_rows["total_assets"] = pd.to_numeric(etf_rows.get("total_assets"), errors="coerce")
    etf_rows["bid"] = pd.to_numeric(etf_rows.get("bid"), errors="coerce")
    etf_rows["ask"] = pd.to_numeric(etf_rows.get("ask"), errors="coerce")
    etf_rows["aum_b"] = etf_rows["total_assets"] / 1_000_000_000.0
    etf_rows["mid_price"] = (etf_rows["bid"] + etf_rows["ask"]) / 2.0
    etf_rows["bid_ask_spread_pct"] = np.where(
        (etf_rows["bid"] > 0) & (etf_rows["ask"] > 0) & (etf_rows["mid_price"] > 0),
        (etf_rows["ask"] - etf_rows["bid"]).abs() / etf_rows["mid_price"],
        np.nan,
    )

    etf_count = int(len(etf_rows))
    available_aum_mask = etf_rows["aum_b"].notna()
    available_spread_mask = etf_rows["bid_ask_spread_pct"].notna()
    available_aum_count = int(available_aum_mask.sum())
    available_spread_count = int(available_spread_mask.sum())

    if min_aum_b is not None and available_aum_count <= 0:
        return {
            "etf_operability_status": "unavailable",
            "etf_operability_watch_signals": ["etf_aum_missing"],
            "etf_symbol_count": etf_count,
            "etf_profile_symbol_count": etf_count,
            "etf_aum_available_count": available_aum_count,
            "etf_spread_available_count": available_spread_count,
        }
    if max_spread_pct is not None and available_spread_count <= 0:
        return {
            "etf_operability_status": "unavailable",
            "etf_operability_watch_signals": ["etf_bid_ask_spread_missing"],
            "etf_symbol_count": etf_count,
            "etf_profile_symbol_count": etf_count,
            "etf_aum_available_count": available_aum_count,
            "etf_spread_available_count": available_spread_count,
        }

    aum_pass_mask = (
        etf_rows["aum_b"] >= min_aum_b
        if min_aum_b is not None
        else pd.Series(True, index=etf_rows.index)
    )
    spread_pass_mask = (
        etf_rows["bid_ask_spread_pct"] <= max_spread_pct
        if max_spread_pct is not None
        else pd.Series(True, index=etf_rows.index)
    )
    aum_pass_mask = aum_pass_mask.fillna(False)
    spread_pass_mask = spread_pass_mask.fillna(False)
    clean_mask = aum_pass_mask & spread_pass_mask
    operability_data_mask = available_aum_mask & available_spread_mask

    clean_coverage = float(clean_mask.mean()) if etf_count > 0 else None
    data_coverage = float(operability_data_mask.mean()) if etf_count > 0 else None
    aum_pass_count = int(aum_pass_mask.sum())
    spread_pass_count = int(spread_pass_mask.sum())
    clean_pass_count = int(clean_mask.sum())

    aum_failed_symbols = etf_rows.loc[available_aum_mask & ~aum_pass_mask, "symbol"].astype(str).tolist()
    spread_failed_symbols = etf_rows.loc[available_spread_mask & ~spread_pass_mask, "symbol"].astype(str).tolist()
    missing_data_symbols = etf_rows.loc[~operability_data_mask, "symbol"].astype(str).tolist()

    watch_signals: list[str] = []
    severe_signals = 0
    if data_coverage is not None and data_coverage < 1.0:
        watch_signals.append("etf_operability_partial_data_coverage")
        if data_coverage < 0.75:
            severe_signals += 1
    if aum_failed_symbols:
        watch_signals.append("etf_aum_below_policy")
        if clean_coverage is not None and clean_coverage < 0.75:
            severe_signals += 1
    if spread_failed_symbols:
        watch_signals.append("etf_bid_ask_spread_above_policy")
        if clean_coverage is not None and clean_coverage < 0.75:
            severe_signals += 1

    if severe_signals > 0:
        status = "caution"
    elif watch_signals:
        status = "watch"
    else:
        status = "normal"

    return {
        "etf_operability_status": status,
        "etf_operability_watch_signals": watch_signals,
        "etf_symbol_count": etf_count,
        "etf_profile_symbol_count": etf_count,
        "etf_aum_available_count": available_aum_count,
        "etf_spread_available_count": available_spread_count,
        "etf_aum_pass_count": aum_pass_count,
        "etf_spread_pass_count": spread_pass_count,
        "etf_operability_clean_pass_count": clean_pass_count,
        "etf_operability_clean_coverage": clean_coverage,
        "etf_operability_data_coverage": data_coverage,
        "etf_aum_failed_symbols": aum_failed_symbols[:10],
        "etf_spread_failed_symbols": spread_failed_symbols[:10],
        "etf_operability_missing_data_symbols": missing_data_symbols[:10],
    }


def _apply_real_money_hardening(
    bundle: dict[str, Any],
    *,
    summary_freq: str,
    min_price_filter: float,
    transaction_cost_bps: float,
    benchmark_contract: str | None,
    benchmark_ticker: str | None,
    guardrail_reference_ticker: str | None = None,
    benchmark_universe_tickers: Sequence[str] | None = None,
    promotion_min_etf_aum_b: float | None = None,
    promotion_max_bid_ask_spread_pct: float | None = None,
    promotion_min_benchmark_coverage: float | None = None,
    promotion_min_net_cagr_spread: float | None = None,
    promotion_min_liquidity_clean_coverage: float | None = None,
    promotion_max_underperformance_share: float | None = None,
    promotion_min_worst_rolling_excess_return: float | None = None,
    promotion_max_strategy_drawdown: float | None = None,
    promotion_max_drawdown_gap_vs_benchmark: float | None = None,
) -> dict[str, Any]:
    result_df = bundle["result_df"].copy()
    hardened_df, turnover_stats = _apply_transaction_cost_postprocess(
        result_df,
        transaction_cost_bps=transaction_cost_bps,
    )

    bundle["result_df"] = hardened_df
    bundle["chart_df"] = hardened_df[["Date", "Total Balance", "Total Return"]].copy()
    bundle["summary_df"] = portfolio_performance_summary(
        hardened_df,
        name=bundle["strategy_name"],
        freq=summary_freq,
    )

    meta = dict(bundle.get("meta") or {})
    warnings = list(meta.get("warnings") or [])
    warnings.append(
        "실전 검토용 보강이 적용되었습니다: 투자 가능성 필터, 회전율 추정, 거래비용, "
        "벤치마크/유동성 기반 실전 후보 승격 정책을 함께 반영했습니다."
    )
    meta.update(
        {
            "warnings": warnings,
            "real_money_hardening": True,
            "cost_model_contract_version": "cost_model_source_contract_v1",
            "cost_model_source": "app.runtime.backtest._apply_transaction_cost_postprocess",
            "cost_model_formula": "estimated_cost=pre_cost_balance*(transaction_cost_bps/10000)*estimated_turnover",
            "cost_application_status": "applied_to_result_curve",
            "cost_application_target": "result_df.Total Balance/Total Return",
            "cost_turnover_source": turnover_stats["turnover_source"],
            "net_cost_curve_contract_version": turnover_stats["net_cost_curve_contract_version"],
            "net_cost_curve_status": turnover_stats["net_cost_curve_status"],
            "net_cost_curve_application_target": turnover_stats["net_cost_curve_application_target"],
            "total_balance_is_net_of_cost": turnover_stats["total_balance_is_net_of_cost"],
            "net_cost_curve_rows": turnover_stats["net_cost_curve_rows"],
            "min_price_filter": float(min_price_filter or 0.0),
            "transaction_cost_bps": float(transaction_cost_bps or 0.0),
            "benchmark_contract": str(benchmark_contract or STRICT_DEFAULT_BENCHMARK_CONTRACT).strip().lower(),
            "benchmark_ticker": str(benchmark_ticker or "").strip().upper() or None,
            "guardrail_reference_ticker": str(guardrail_reference_ticker or "").strip().upper() or None,
            "promotion_min_etf_aum_b": (
                float(promotion_min_etf_aum_b) if promotion_min_etf_aum_b is not None else None
            ),
            "promotion_max_bid_ask_spread_pct": (
                float(promotion_max_bid_ask_spread_pct)
                if promotion_max_bid_ask_spread_pct is not None
                else None
            ),
            "promotion_min_benchmark_coverage": (
                float(promotion_min_benchmark_coverage) if promotion_min_benchmark_coverage is not None else None
            ),
            "promotion_min_net_cagr_spread": (
                float(promotion_min_net_cagr_spread) if promotion_min_net_cagr_spread is not None else None
            ),
            "promotion_min_liquidity_clean_coverage": (
                float(promotion_min_liquidity_clean_coverage)
                if promotion_min_liquidity_clean_coverage is not None
                else None
            ),
            "promotion_max_underperformance_share": (
                float(promotion_max_underperformance_share)
                if promotion_max_underperformance_share is not None
                else None
            ),
            "promotion_min_worst_rolling_excess_return": (
                float(promotion_min_worst_rolling_excess_return)
                if promotion_min_worst_rolling_excess_return is not None
                else None
            ),
            "promotion_max_strategy_drawdown": (
                float(promotion_max_strategy_drawdown)
                if promotion_max_strategy_drawdown is not None
                else None
            ),
            "promotion_max_drawdown_gap_vs_benchmark": (
                float(promotion_max_drawdown_gap_vs_benchmark)
                if promotion_max_drawdown_gap_vs_benchmark is not None
                else None
            ),
            "avg_turnover": turnover_stats["avg_turnover"],
            "max_turnover": turnover_stats["max_turnover"],
            "avg_rebalance_turnover": turnover_stats["avg_rebalance_turnover"],
            "turnover_model_contract_version": turnover_stats["turnover_model_contract_version"],
            "turnover_estimation_status": turnover_stats["turnover_estimation_status"],
            "turnover_source": turnover_stats["turnover_source"],
            "turnover_input_missing_columns": turnover_stats["turnover_input_missing_columns"],
            "turnover_observation_count": turnover_stats["turnover_observation_count"],
            "turnover_rebalance_rows": turnover_stats["turnover_rebalance_rows"],
            "turnover_nonzero_count": turnover_stats["turnover_nonzero_count"],
            "estimated_cost_total": turnover_stats["estimated_cost_total"],
            "estimated_cost_positive_rows": turnover_stats["estimated_cost_positive_rows"],
            "gross_start_balance": float(hardened_df["Gross Total Balance"].iloc[0]),
            "gross_end_balance": float(hardened_df["Gross Total Balance"].iloc[-1]),
            "net_end_balance": float(hardened_df["Total Balance"].iloc[-1]),
            "gross_net_end_balance_delta": turnover_stats["gross_net_end_balance_delta"],
        }
    )
    strategy_summary_df = bundle.get("summary_df")
    if strategy_summary_df is not None and not strategy_summary_df.empty and "CAGR" in strategy_summary_df.columns:
        meta["strategy_cagr"] = float(strategy_summary_df.iloc[0]["CAGR"])
    if "Underperformance Guardrail Triggered" in hardened_df.columns:
        guardrail_triggered = hardened_df["Underperformance Guardrail Triggered"].fillna(False).astype(bool)
        meta["underperformance_guardrail_trigger_count"] = int(guardrail_triggered.sum())
        meta["underperformance_guardrail_trigger_share"] = (
            float(guardrail_triggered.mean()) if not guardrail_triggered.empty else 0.0
        )
    if "Drawdown Guardrail Triggered" in hardened_df.columns:
        drawdown_guardrail_triggered = hardened_df["Drawdown Guardrail Triggered"].fillna(False).astype(bool)
        meta["drawdown_guardrail_trigger_count"] = int(drawdown_guardrail_triggered.sum())
        meta["drawdown_guardrail_trigger_share"] = (
            float(drawdown_guardrail_triggered.mean()) if not drawdown_guardrail_triggered.empty else 0.0
        )
    if "Liquidity Excluded Count" in hardened_df.columns:
        liquidity_excluded = pd.to_numeric(hardened_df["Liquidity Excluded Count"], errors="coerce").fillna(0)
        rebalancing_mask = pd.Series(True, index=hardened_df.index)
        if "Rebalancing" in hardened_df.columns:
            rebalancing_mask = hardened_df["Rebalancing"].fillna(False).astype(bool)
        liquidity_rebalance_rows = int(rebalancing_mask.sum())
        if liquidity_rebalance_rows <= 0:
            liquidity_rebalance_rows = int(len(hardened_df))
            rebalancing_mask = pd.Series(True, index=hardened_df.index)
        liquidity_excluded_active_rows = int(((liquidity_excluded > 0) & rebalancing_mask).sum())
        meta["liquidity_excluded_total"] = int(liquidity_excluded.sum())
        meta["liquidity_excluded_active_rows"] = liquidity_excluded_active_rows
        meta["liquidity_rebalance_rows"] = liquidity_rebalance_rows
        meta["liquidity_clean_coverage"] = (
            float(1.0 - (liquidity_excluded_active_rows / liquidity_rebalance_rows))
            if liquidity_rebalance_rows > 0
            else None
        )

    etf_operability_policy_surface = _build_etf_operability_policy_surface(meta)
    if etf_operability_policy_surface:
        meta.update(etf_operability_policy_surface)
        etf_operability_status = str(etf_operability_policy_surface.get("etf_operability_status") or "").lower()
        if etf_operability_status == "caution":
            warnings.append(
                "ETF 운용 가능성 정책이 주의 상태입니다: 일부 ETF가 운용자산(AUM)/스프레드 기준을 통과하지 못했거나, "
                "필요한 ETF 기본 정보 데이터가 부족합니다."
            )
        elif etf_operability_status == "watch":
            warnings.append(
                "ETF 운용 가능성 정책이 관찰 상태입니다: 일부 ETF가 운용자산(AUM)/스프레드 선호 기준보다 낮거나, "
                "현재 기본 정보 데이터가 일부만 있습니다."
            )
        elif etf_operability_status == "unavailable":
            warnings.append(
                "ETF 운용 가능성 정책을 판단할 수 없습니다: 이 전략을 실전 후보로 해석하기 전에 ETF 기본 정보를 먼저 갱신해야 합니다."
            )

    benchmark_df, benchmark_info = _build_benchmark_result_df(
        benchmark_contract=meta.get("benchmark_contract"),
        benchmark_ticker=benchmark_ticker,
        benchmark_universe_tickers=benchmark_universe_tickers,
        dates=hardened_df["Date"],
        start=meta.get("start"),
        end=meta.get("end"),
        timeframe=meta.get("timeframe") or "1d",
        initial_balance=float(hardened_df["Gross Total Balance"].iloc[0]),
    )
    if benchmark_info:
        meta["benchmark_label"] = benchmark_info.get("benchmark_label")
        meta["benchmark_symbol_count"] = benchmark_info.get("benchmark_symbol_count")
        meta["benchmark_eligible_symbol_count"] = benchmark_info.get("benchmark_eligible_symbol_count")
    if benchmark_df is not None:
        benchmark_summary_input = benchmark_df.rename(
            columns={
                "Benchmark Total Balance": "Total Balance",
                "Benchmark Total Return": "Total Return",
            }
        )[["Date", "Total Balance", "Total Return"]].copy()
        bundle["benchmark_chart_df"] = benchmark_df
        benchmark_summary_df = portfolio_performance_summary(
            benchmark_summary_input,
            name=str(meta.get("benchmark_label") or meta.get("benchmark_ticker") or "Benchmark"),
            freq=summary_freq,
        )
        bundle["benchmark_summary_df"] = benchmark_summary_df
        meta["benchmark_available"] = True
        meta["benchmark_end_balance"] = float(benchmark_df["Benchmark Total Balance"].iloc[-1])
        meta["net_excess_end_balance"] = float(hardened_df["Total Balance"].iloc[-1] - benchmark_df["Benchmark Total Balance"].iloc[-1])
        meta["benchmark_row_coverage"] = float(benchmark_df["Benchmark Total Balance"].notna().mean())
        if benchmark_summary_df is not None and not benchmark_summary_df.empty and "CAGR" in benchmark_summary_df.columns:
            meta["benchmark_cagr"] = float(benchmark_summary_df.iloc[0]["CAGR"])
            if meta.get("strategy_cagr") is not None:
                meta["net_cagr_spread"] = float(meta["strategy_cagr"] - meta["benchmark_cagr"])
        validation_surface = _build_real_money_validation_surface(
            strategy_df=hardened_df,
            benchmark_df=benchmark_df,
            summary_freq=summary_freq,
        )
        if validation_surface:
            meta.update(validation_surface)
            watch_signals = validation_surface.get("validation_watch_signals") or []
            if validation_surface.get("validation_status") == "caution":
                warnings.append(
                    "검증 결과가 주의 상태입니다: 벤치마크 대비 낙폭 또는 반복 구간 부진 지표가 높습니다. "
                    "실전 후보 승격 전에 검토 신호로 확인해야 합니다."
                )
            elif validation_surface.get("validation_status") == "watch":
                warnings.append(
                    "검증 결과가 관찰 상태입니다: 이 실행을 강한 실전 후보로 보기 전에 벤치마크 대비 부진 또는 낙폭 지표를 확인해야 합니다."
                )
            if watch_signals:
                meta["validation_watch_signals"] = watch_signals

        rolling_review_surface = _build_rolling_and_out_of_sample_review_surface(
            strategy_df=hardened_df,
            benchmark_df=benchmark_df,
            summary_freq=summary_freq,
        )
        if rolling_review_surface:
            meta.update(rolling_review_surface)
            rolling_status = rolling_review_surface.get("rolling_review_status")
            out_of_sample_status = rolling_review_surface.get("out_of_sample_review_status")
            rolling_signals = rolling_review_surface.get("rolling_review_rationale") or []
            out_of_sample_signals = rolling_review_surface.get("out_of_sample_review_rationale") or []
            if rolling_status == "caution":
                warnings.append(
                    "반복 구간 검토가 주의 상태입니다: 최근 검증 구간에서 선호하는 배포 준비 기준보다 벤치마크 대비 성과가 약하게 나타났습니다."
                )
            elif rolling_status == "watch":
                warnings.append(
                    "반복 구간 검토가 관찰 상태입니다: 최근 시장 구간의 성과가 선호하는 배포 준비 기준보다 약합니다."
                )
            if out_of_sample_status == "caution":
                warnings.append(
                    "간이 전후반 구간 점검이 주의 상태입니다: 뒤쪽 구간에서 벤치마크 대비 성과가 낮거나, 앞쪽 구간보다 성과가 뚜렷하게 악화되었습니다."
                )
            elif out_of_sample_status == "watch":
                warnings.append(
                    "간이 전후반 구간 점검이 관찰 상태입니다: 뒤쪽 구간이 앞쪽 구간보다 약하므로 후속 검증에서 다시 확인해야 합니다."
                )
            if rolling_signals:
                meta["rolling_review_signals"] = rolling_signals
            if out_of_sample_signals:
                meta["out_of_sample_review_signals"] = out_of_sample_signals
    else:
        meta["benchmark_available"] = False
        benchmark_contract = str(meta.get("benchmark_contract") or STRICT_DEFAULT_BENCHMARK_CONTRACT).strip().lower()
        if benchmark_contract == STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT:
            warnings.append(
                "후보군 동일비중 벤치마크를 만들 수 없습니다: 요청한 날짜에 필요한 가격 이력이 충분하지 않습니다."
            )
        elif meta.get("benchmark_ticker"):
            warnings.append(
                f"벤치마크 비교선을 만들 수 없습니다: `{meta['benchmark_ticker']}`의 DB 가격 이력이 요청한 날짜에 충분하지 않습니다."
            )

    benchmark_policy_surface = _build_benchmark_policy_surface(meta)
    if benchmark_policy_surface:
        meta.update(benchmark_policy_surface)
        policy_status = benchmark_policy_surface.get("benchmark_policy_status")
        policy_signals = benchmark_policy_surface.get("benchmark_policy_watch_signals") or []
        if policy_status == "caution":
            warnings.append(
                "벤치마크 정책이 주의 상태입니다: 정렬된 벤치마크 적용 범위 또는 순 CAGR 차이가 현재 실전 후보 승격 기준보다 크게 낮습니다."
            )
        elif policy_status == "watch":
            warnings.append(
                "벤치마크 정책이 관찰 상태입니다: 벤치마크 적용 범위 또는 순 CAGR 차이가 선호하는 실전 후보 승격 기준보다 낮습니다."
            )
        if policy_signals:
            meta["benchmark_policy_watch_signals"] = policy_signals

    liquidity_policy_surface = _build_liquidity_policy_surface(meta)
    if liquidity_policy_surface:
        meta.update(liquidity_policy_surface)
        liquidity_policy_status = liquidity_policy_surface.get("liquidity_policy_status")
        liquidity_policy_signals = liquidity_policy_surface.get("liquidity_policy_watch_signals") or []
        if liquidity_policy_status == "caution":
            warnings.append(
                "유동성 정책이 주의 상태입니다: 현재 실전 후보 승격 기준에서 유동성 제외가 필요한 리밸런싱 행이 너무 많습니다."
            )
        elif liquidity_policy_status == "watch":
            warnings.append(
                "유동성 정책이 관찰 상태입니다: 유동성 제외 비율이 선호하는 실전 후보 승격 기준보다 높습니다."
            )
        elif liquidity_policy_status == "unavailable":
            warnings.append(
                "유동성 정책을 판단할 수 없습니다: 실전 후보 승격 수준의 유동성 검토에는 `최근 20거래일 평균 거래대금` 필터가 필요합니다."
            )
        if liquidity_policy_signals:
            meta["liquidity_policy_watch_signals"] = liquidity_policy_signals

    validation_policy_surface = _build_validation_policy_surface(meta)
    if validation_policy_surface:
        meta.update(validation_policy_surface)
        validation_policy_status = validation_policy_surface.get("validation_policy_status")
        validation_policy_signals = validation_policy_surface.get("validation_policy_watch_signals") or []
        if validation_policy_status == "caution":
            warnings.append(
                "검증 정책이 주의 상태입니다: 반복 구간 부진 비율 또는 최악의 반복 구간 초과수익이 현재 실전 후보 승격 기준보다 크게 낮습니다."
            )
        elif validation_policy_status == "watch":
            warnings.append(
                "검증 정책이 관찰 상태입니다: 반복 구간 부진 비율 또는 최악의 반복 구간 초과수익이 선호하는 실전 후보 승격 기준보다 낮습니다."
            )
        elif validation_policy_status == "unavailable":
            warnings.append(
                "검증 정책을 판단할 수 없습니다: 실전 후보 승격 수준의 견고성 검토에는 정렬된 벤치마크 검증 이력이 필요합니다."
            )
        if validation_policy_signals:
            meta["validation_policy_watch_signals"] = validation_policy_signals

    guardrail_policy_surface = _build_guardrail_policy_surface(meta)
    if guardrail_policy_surface:
        meta.update(guardrail_policy_surface)
        guardrail_policy_status = guardrail_policy_surface.get("guardrail_policy_status")
        guardrail_policy_signals = guardrail_policy_surface.get("guardrail_policy_watch_signals") or []
        if guardrail_policy_status == "caution":
            warnings.append(
                "방어 기준 정책이 주의 상태입니다: 전략 낙폭 또는 벤치마크 대비 낙폭 차이가 현재 포트폴리오 방어 기준을 초과했습니다."
            )
        elif guardrail_policy_status == "watch":
            warnings.append(
                "방어 기준 정책이 관찰 상태입니다: 낙폭 흐름이 선호하는 포트폴리오 방어 기준보다 약합니다."
            )
        elif guardrail_policy_status == "unavailable":
            warnings.append(
                "방어 기준 정책을 판단할 수 없습니다: 실전 후보 승격 수준의 낙폭 방어 기준 검토에는 사용 가능한 전략/벤치마크 낙폭 이력이 필요합니다."
            )
        if guardrail_policy_signals:
            meta["guardrail_policy_watch_signals"] = guardrail_policy_signals

    meta.update(_build_promotion_decision(meta))
    meta.update(_build_shortlist_contract(meta))
    meta.update(_build_probation_and_monitoring_contract(meta))
    meta.update(_build_deployment_readiness_contract(meta))
    bundle["meta"] = meta
    return bundle
