from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np
import pandas as pd

from finance.loaders import (
    load_asset_profile_status_summary,
    load_factor_snapshot,
    load_latest_market_date,
    load_price_freshness_summary,
    load_price_history,
    load_statement_factor_snapshot_shadow,
    load_statement_snapshot_strict,
)
from finance.performance import portfolio_performance_summary
from finance.sample import (
    GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD,
    GTAA_DEFAULT_CRASH_GUARDRAIL_ENABLED,
    GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS,
    GTAA_DEFAULT_DEFENSIVE_TICKERS,
    GTAA_DEFAULT_RISK_OFF_MODE,
    GTAA_DEFAULT_SCORE_LOOKBACK_MONTHS,
    GTAA_DEFAULT_SIGNAL_INTERVAL,
    GTAA_DEFAULT_TREND_FILTER_WINDOW,
    GTAA_DEFAULT_SCORE_WEIGHTS,
    HISTORICAL_DYNAMIC_PIT_UNIVERSE,
    STATIC_MANAGED_RESEARCH_UNIVERSE,
    STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
    STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
    STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    QUALITY_STRICT_DEFAULT_FACTORS,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    VALUE_STRICT_DEFAULT_FACTORS,
    get_dual_momentum_from_db,
    get_equal_weight_from_db,
    get_gtaa3_from_db,
    get_quality_snapshot_from_db,
    get_risk_parity_trend_from_db,
    get_statement_quality_snapshot_from_db,
    get_statement_quality_value_snapshot_shadow_from_db,
    get_statement_quality_snapshot_shadow_from_db,
    get_statement_value_snapshot_shadow_from_db,
)


class BacktestInputError(ValueError):
    """Raised when user-facing backtest input is structurally invalid."""


class BacktestDataError(ValueError):
    """Raised when the requested DB-backed backtest cannot find required market data."""


ETF_REAL_MONEY_DEFAULT_MIN_PRICE = 5.0
ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS = 10.0
ETF_REAL_MONEY_DEFAULT_BENCHMARK = "SPY"
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
        raise BacktestInputError("At least one ticker must be provided.")

    return normalized


def _summary_frequency(option: str, timeframe: str) -> str:
    if option == "month_end":
        return "M"
    if timeframe == "1d":
        return "D"
    return "M"


def _validate_backtest_date_range(start: str | None, end: str | None) -> tuple[pd.Timestamp | None, pd.Timestamp | None]:
    start_ts = pd.to_datetime(start) if start is not None else None
    end_ts = pd.to_datetime(end) if end is not None else None

    if start_ts is not None and end_ts is not None and start_ts > end_ts:
        raise BacktestInputError("Start date must be earlier than or equal to end date.")

    return start_ts, end_ts


def _preflight_equal_weight_data(
    *,
    tickers: list[str],
    start: str | None,
    end: str | None,
    timeframe: str,
) -> None:
    history = load_price_history(
        symbols=tickers,
        start=start,
        end=end,
        timeframe=timeframe,
    )
    if history.empty:
        raise BacktestDataError(
            "No OHLCV rows were found in MySQL for the requested tickers and date range. "
            "Run the ingestion pipeline first."
        )

    available_symbols = set(history["symbol"].astype(str).str.upper().unique().tolist())
    missing = [ticker for ticker in tickers if ticker not in available_symbols]
    if missing:
        raise BacktestDataError(
            "Some requested tickers do not have DB price history for the selected range: "
            + ", ".join(missing)
        )


def _preflight_price_strategy_data(
    *,
    tickers: list[str],
    start: str | None,
    end: str | None,
    timeframe: str,
) -> None:
    history = load_price_history(
        symbols=tickers,
        start=start,
        end=end,
        timeframe=timeframe,
    )
    if history.empty:
        raise BacktestDataError(
            "No OHLCV rows were found in MySQL for the requested tickers and date range. "
            "Run the ingestion pipeline first."
        )

    available_symbols = set(history["symbol"].astype(str).str.upper().unique().tolist())
    missing = [ticker for ticker in tickers if ticker not in available_symbols]
    if missing:
        raise BacktestDataError(
            "Some requested tickers do not have DB price history for the selected range: "
            + ", ".join(missing)
        )


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


def _estimate_turnover_series(result_df: pd.DataFrame) -> pd.Series:
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


def _apply_transaction_cost_postprocess(
    result_df: pd.DataFrame,
    *,
    transaction_cost_bps: float,
) -> tuple[pd.DataFrame, dict[str, float]]:
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

    diagnostics = {
        "avg_turnover": float(working["Turnover"].mean()) if not working.empty else 0.0,
        "max_turnover": float(working["Turnover"].max()) if not working.empty else 0.0,
        "estimated_cost_total": float(working["Estimated Cost"].sum()) if not working.empty else 0.0,
    }
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


def _compute_drawdown_stats(balance_series: pd.Series) -> tuple[float | None, float | None]:
    series = pd.to_numeric(balance_series, errors="coerce").dropna()
    if series.empty:
        return None, None

    drawdown = (series / series.cummax()) - 1.0
    return float(drawdown.iloc[-1]), float(drawdown.min())


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


def _build_promotion_decision(meta: dict[str, Any]) -> dict[str, Any]:
    benchmark_available = bool(meta.get("benchmark_available"))
    validation_status = str(meta.get("validation_status") or "").strip().lower()
    benchmark_policy_status = str(meta.get("benchmark_policy_status") or "").strip().lower()
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


def _apply_real_money_hardening(
    bundle: dict[str, Any],
    *,
    summary_freq: str,
    min_price_filter: float,
    transaction_cost_bps: float,
    benchmark_contract: str | None,
    benchmark_ticker: str | None,
    benchmark_universe_tickers: Sequence[str] | None = None,
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
        "Phase 12 real-money hardening applied: investability filters, turnover estimate, "
        "transaction cost, and benchmark/liquidity promotion policy overlays."
    )
    meta.update(
        {
            "warnings": warnings,
            "real_money_hardening": True,
            "min_price_filter": float(min_price_filter or 0.0),
            "transaction_cost_bps": float(transaction_cost_bps or 0.0),
            "benchmark_contract": str(benchmark_contract or STRICT_DEFAULT_BENCHMARK_CONTRACT).strip().lower(),
            "benchmark_ticker": str(benchmark_ticker or "").strip().upper() or None,
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
            "estimated_cost_total": turnover_stats["estimated_cost_total"],
            "gross_start_balance": float(hardened_df["Gross Total Balance"].iloc[0]),
            "gross_end_balance": float(hardened_df["Gross Total Balance"].iloc[-1]),
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
                    "Validation caution: benchmark-relative drawdown / rolling underperformance diagnostics are elevated. "
                    "Treat this as a real-money review signal before promotion."
                )
            elif validation_surface.get("validation_status") == "watch":
                warnings.append(
                    "Validation watch: benchmark-relative underperformance or drawdown diagnostics need review before treating this run as a strong real-money candidate."
                )
            if watch_signals:
                meta["validation_watch_signals"] = watch_signals
    else:
        meta["benchmark_available"] = False
        benchmark_contract = str(meta.get("benchmark_contract") or STRICT_DEFAULT_BENCHMARK_CONTRACT).strip().lower()
        if benchmark_contract == STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT:
            warnings.append(
                "Benchmark overlay could not be built because candidate-universe equal-weight price history "
                "was not sufficiently available on the requested dates."
            )
        elif meta.get("benchmark_ticker"):
            warnings.append(
                f"Benchmark overlay could not be built because DB price history for `{meta['benchmark_ticker']}` "
                "was not available on the requested dates."
            )

    benchmark_policy_surface = _build_benchmark_policy_surface(meta)
    if benchmark_policy_surface:
        meta.update(benchmark_policy_surface)
        policy_status = benchmark_policy_surface.get("benchmark_policy_status")
        policy_signals = benchmark_policy_surface.get("benchmark_policy_watch_signals") or []
        if policy_status == "caution":
            warnings.append(
                "Benchmark policy caution: aligned benchmark coverage or net CAGR spread fell materially below the current promotion contract."
            )
        elif policy_status == "watch":
            warnings.append(
                "Benchmark policy watch: benchmark coverage or net CAGR spread is below the preferred promotion contract."
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
                "Liquidity policy caution: too many rebalance rows required liquidity exclusions for the current promotion contract."
            )
        elif liquidity_policy_status == "watch":
            warnings.append(
                "Liquidity policy watch: liquidity exclusions are above the preferred promotion contract."
            )
        elif liquidity_policy_status == "unavailable":
            warnings.append(
                "Liquidity policy unavailable: promotion-grade liquidity review needs an active Min Avg Dollar Volume 20D filter."
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
                "Validation policy caution: rolling underperformance share or worst rolling excess return fell materially below the current promotion contract."
            )
        elif validation_policy_status == "watch":
            warnings.append(
                "Validation policy watch: rolling underperformance share or worst rolling excess return is below the preferred promotion contract."
            )
        elif validation_policy_status == "unavailable":
            warnings.append(
                "Validation policy unavailable: promotion-grade robustness review needs aligned benchmark validation history."
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
                "Guardrail policy caution: strategy drawdown or drawdown gap vs benchmark exceeded the current portfolio guardrail contract."
            )
        elif guardrail_policy_status == "watch":
            warnings.append(
                "Guardrail policy watch: drawdown behavior is weaker than the preferred portfolio guardrail contract."
            )
        elif guardrail_policy_status == "unavailable":
            warnings.append(
                "Guardrail policy unavailable: promotion-grade drawdown guardrail review needs usable strategy and benchmark drawdown history."
            )
        if guardrail_policy_signals:
            meta["guardrail_policy_watch_signals"] = guardrail_policy_signals

    meta.update(_build_promotion_decision(meta))
    bundle["meta"] = meta
    return bundle


def _inspect_dynamic_universe_price_pool(
    *,
    tickers: list[str],
    end: str | None,
    timeframe: str,
) -> dict[str, Any]:
    history = load_price_history(
        symbols=tickers,
        start=None,
        end=end,
        timeframe=timeframe,
    )
    if history.empty:
        raise BacktestDataError(
            "No OHLCV rows were found in MySQL for the requested dynamic candidate pool. "
            "Run the ingestion pipeline first."
        )

    available_symbols = sorted(
        history["symbol"].astype(str).str.upper().dropna().unique().tolist()
    )
    available_set = set(available_symbols)
    missing = [ticker for ticker in tickers if ticker not in available_set]
    return {
        "requested_count": len(tickers),
        "available_count": len(available_symbols),
        "missing_count": len(missing),
        "missing_symbols": missing,
    }


def _dynamic_universe_warning(statement_freq: str) -> str:
    normalized_freq = str(statement_freq or "annual").strip().lower()
    return (
        "Phase 10 first pass dynamic universe: approximate rebalance-date PIT membership is rebuilt "
        f"from the managed candidate pool using rebalance-date close * latest-known {normalized_freq} shares_outstanding."
    )


def _preflight_quality_snapshot_data(
    *,
    tickers: list[str],
    end: str | None,
    factor_freq: str,
    quality_factors: list[str],
) -> None:
    if end is None:
        raise BacktestInputError("Quality snapshot strategy requires an end date.")

    snapshot = load_factor_snapshot(
        quality_factors,
        symbols=tickers,
        as_of_date=end,
        freq=factor_freq,
    )
    if snapshot.empty:
        raise BacktestDataError(
            "No factor snapshot rows were found for the requested tickers and end date. "
            "Run the fundamentals/factors pipeline first."
        )

    available_symbols = set(snapshot["symbol"].astype(str).str.upper().unique().tolist())
    missing = [ticker for ticker in tickers if ticker not in available_symbols]
    if len(missing) == len(tickers):
        raise BacktestDataError(
            "None of the requested tickers have factor snapshot rows for the selected end date."
        )


def _preflight_statement_quality_data(
    *,
    tickers: list[str],
    end: str | None,
    statement_freq: str,
) -> None:
    if end is None:
        raise BacktestInputError("Statement-driven quality prototype requires an end date.")

    snapshot = load_statement_snapshot_strict(
        symbols=tickers,
        as_of_date=end,
        freq=statement_freq,
    )
    if snapshot.empty:
        raise BacktestDataError(
            "No strict statement snapshot rows were found for the requested tickers and end date. "
            "Run Extended Statement Refresh first."
        )

    available_symbols = set(snapshot["symbol"].astype(str).str.upper().unique().tolist())
    if not available_symbols:
        raise BacktestDataError(
            "No symbols in the requested universe have strict statement snapshot coverage at the selected end date."
        )


def _preflight_statement_quality_shadow_data(
    *,
    tickers: list[str],
    end: str | None,
    statement_freq: str,
    factor_names: list[str],
) -> None:
    if end is None:
        raise BacktestInputError("Statement-driven shadow quality path requires an end date.")

    snapshot = load_statement_factor_snapshot_shadow(
        factor_names,
        symbols=tickers,
        as_of_date=end,
        freq=statement_freq,
    )
    if snapshot.empty:
        raise BacktestDataError(
            "No statement-driven shadow factor snapshot rows were found for the requested tickers and end date. "
            "Run Extended Statement Refresh and rebuild statement shadow factors first."
        )


def inspect_strict_annual_price_freshness(
    *,
    tickers: Sequence[str] | None = None,
    end: str | None = None,
    timeframe: str = "1d",
) -> dict[str, Any]:
    normalized_tickers = _normalize_tickers(tickers)
    end_ts = pd.to_datetime(end).normalize() if end is not None else None
    effective_end_ts = end_ts

    if end_ts is not None:
        market_latest = load_latest_market_date(end=end, timeframe=timeframe)
        if market_latest is not None and pd.notna(market_latest):
            effective_end_ts = market_latest.normalize()

    summary = load_price_freshness_summary(
        symbols=normalized_tickers,
        end=end,
        timeframe=timeframe,
    )
    if summary.empty:
        return {
            "status": "error",
            "message": "No DB price rows were found for the selected strict annual universe.",
            "details": {
                "requested_count": len(normalized_tickers),
                "covered_count": 0,
                "missing_count": len(normalized_tickers),
                "missing_symbols": normalized_tickers[:20],
                "selected_end_date": end_ts.strftime("%Y-%m-%d") if end_ts is not None else None,
                "effective_end_date": effective_end_ts.strftime("%Y-%m-%d") if effective_end_ts is not None else None,
                "effective_end_shift_days": (
                    int((end_ts - effective_end_ts).days)
                    if end_ts is not None and effective_end_ts is not None
                    else 0
                ),
            },
        }

    working = summary.copy()
    working["symbol"] = working["symbol"].astype(str).str.upper()
    working["latest_date"] = pd.to_datetime(working["latest_date"], errors="coerce")
    working = working[working["symbol"].notna() & working["latest_date"].notna()].reset_index(drop=True)

    covered_symbols = set(working["symbol"].tolist())
    missing_symbols = [ticker for ticker in normalized_tickers if ticker not in covered_symbols]

    if working.empty:
        return {
            "status": "error",
            "message": "No usable DB price dates were found for the selected strict annual universe.",
            "details": {
                "requested_count": len(normalized_tickers),
                "covered_count": 0,
                "missing_count": len(normalized_tickers),
                "missing_symbols": normalized_tickers[:20],
                "selected_end_date": end_ts.strftime("%Y-%m-%d") if end_ts is not None else None,
                "effective_end_date": effective_end_ts.strftime("%Y-%m-%d") if effective_end_ts is not None else None,
                "effective_end_shift_days": (
                    int((end_ts - effective_end_ts).days)
                    if end_ts is not None and effective_end_ts is not None
                    else 0
                ),
            },
        }

    common_latest = working["latest_date"].min().normalize()
    newest_latest = working["latest_date"].max().normalize()
    spread_days = int((newest_latest - common_latest).days)
    target_end = effective_end_ts if effective_end_ts is not None else newest_latest
    effective_shift_days = (
        int((end_ts - target_end).days) if end_ts is not None and target_end is not None else 0
    )

    stale_df = working[working["latest_date"].dt.normalize() < target_end].sort_values(["latest_date", "symbol"])
    lagging_df = working[working["latest_date"].dt.normalize() < newest_latest].sort_values(["latest_date", "symbol"])
    stale_symbols_all = stale_df["symbol"].tolist()
    lagging_symbols_all = lagging_df["symbol"].tolist()

    classification_symbols = sorted(set(stale_symbols_all + missing_symbols))
    classification_rows: list[dict[str, Any]] = []
    reason_counts: dict[str, int] = {}
    if classification_symbols:
        profile_df = load_asset_profile_status_summary(classification_symbols)
        profile_map = {
            str(row["symbol"]).upper(): row
            for _, row in profile_df.iterrows()
            if row.get("symbol") is not None
        }

        def _classify_reason(symbol: str, latest_date: pd.Timestamp | None) -> dict[str, Any]:
            profile = profile_map.get(symbol, {})
            profile_status = str(profile.get("status") or "").strip().lower()
            profile_error = str(profile.get("error_msg") or "").strip() or None
            delisted_at = profile.get("delisted_at")
            lag_days = None
            if latest_date is not None and pd.notna(latest_date) and target_end is not None:
                lag_days = int((target_end - latest_date.normalize()).days)

            if profile_status in {"delisted", "not_found"} or pd.notna(delisted_at):
                reason = "likely_delisted_or_symbol_changed"
                note = "Asset profile already marks this symbol as unavailable or delisted."
            elif profile_status == "error":
                reason = "asset_profile_error"
                note = "Asset profile collection is in an error state for this symbol."
            elif latest_date is None or pd.isna(latest_date):
                reason = "missing_price_rows"
                note = "No DB daily price rows exist for the selected timeframe."
            elif lag_days is not None and lag_days <= 7:
                reason = "minor_source_lag"
                note = "The symbol lags the selected end date by less than or equal to 7 days."
            elif lag_days is not None and lag_days <= 30:
                reason = "source_gap_or_symbol_issue"
                note = "The symbol has a material lag versus the selected end date while still looking active in asset profile."
            else:
                reason = "persistent_source_gap_or_symbol_issue"
                note = "The symbol is far behind the selected end date and may need provider or symbol-status investigation."

            if profile_error and reason != "asset_profile_error":
                note = f"{note} asset_profile_error={profile_error}"

            return {
                "symbol": symbol,
                "latest_date": (
                    latest_date.normalize().strftime("%Y-%m-%d")
                    if latest_date is not None and pd.notna(latest_date)
                    else None
                ),
                "lag_days": lag_days,
                "profile_status": profile_status or None,
                "reason": reason,
                "note": note,
            }

        for symbol in classification_symbols:
            latest_match = working.loc[working["symbol"] == symbol, "latest_date"]
            latest_date = latest_match.iloc[0] if not latest_match.empty else None
            row = _classify_reason(symbol, latest_date)
            classification_rows.append(row)
            reason_counts[row["reason"]] = reason_counts.get(row["reason"], 0) + 1

    details = {
        "requested_count": len(normalized_tickers),
        "covered_count": int(len(working)),
        "missing_count": len(missing_symbols),
        "missing_symbols": missing_symbols[:20],
        "missing_symbols_all": missing_symbols,
        "selected_end_date": end_ts.strftime("%Y-%m-%d") if end_ts is not None else None,
        "target_end_date": target_end.strftime("%Y-%m-%d") if target_end is not None else None,
        "effective_end_date": target_end.strftime("%Y-%m-%d") if target_end is not None else None,
        "effective_end_shift_days": effective_shift_days,
        "effective_end_basis": (
            "latest_market_date_on_or_before_selected_end"
            if effective_shift_days > 0
            else "selected_end_date"
        ),
        "common_latest_date": common_latest.strftime("%Y-%m-%d"),
        "newest_latest_date": newest_latest.strftime("%Y-%m-%d"),
        "spread_days": spread_days,
        "stale_count": int(len(stale_df)),
        "stale_symbols": stale_symbols_all[:20],
        "stale_symbols_all": stale_symbols_all,
        "lagging_count": int(len(lagging_df)),
        "lagging_symbols": lagging_symbols_all[:20],
        "lagging_symbols_all": lagging_symbols_all,
        "refresh_symbols_all": sorted(set(stale_symbols_all + missing_symbols)),
        "reason_counts": reason_counts,
        "classification_rows": classification_rows[:50],
        "classification_scope": "heuristic",
    }

    if not missing_symbols and len(stale_df) == 0 and spread_days == 0:
        if effective_shift_days > 0 and end_ts is not None:
            message = (
                f"All {len(normalized_tickers)} selected symbols have price data through effective trading end "
                f"`{target_end.strftime('%Y-%m-%d')}`. Selected end `{end_ts.strftime('%Y-%m-%d')}` does not have "
                "a later DB market session."
            )
        else:
            message = (
                f"All {len(normalized_tickers)} selected symbols have price data through "
                f"`{common_latest.strftime('%Y-%m-%d')}`."
            )
        return {
            "status": "ok",
            "message": message,
            "details": details,
        }

    message_parts: list[str] = []
    if effective_shift_days > 0 and end_ts is not None:
        message_parts.append(
            f"Selected end `{end_ts.strftime('%Y-%m-%d')}` maps to effective trading end "
            f"`{target_end.strftime('%Y-%m-%d')}` for DB freshness checks."
        )
    if missing_symbols:
        message_parts.append(f"{len(missing_symbols)} symbols have no DB price rows.")
    if len(stale_df) > 0:
        message_parts.append(
            f"{len(stale_df)} symbols stop before the effective trading end `{target_end.strftime('%Y-%m-%d')}`."
        )
    if spread_days > 0:
        message_parts.append(
            f"Latest-date spread inside the universe is {spread_days} day(s) "
            f"(`{common_latest.strftime('%Y-%m-%d')}` -> `{newest_latest.strftime('%Y-%m-%d')}`)."
        )

    return {
        "status": "warning",
        "message": " ".join(message_parts),
        "details": details,
    }


def build_backtest_result_bundle(
    result_df: pd.DataFrame,
    *,
    strategy_name: str,
    strategy_key: str,
    input_params: dict[str, Any],
    execution_mode: str = "db",
    data_mode: str = "db_backed",
    summary_freq: str = "M",
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    """
    Build the minimal UI-facing bundle for a single backtest run.
    """
    if result_df is None or result_df.empty:
        raise ValueError("Backtest result is empty.")

    required_columns = {"Date", "Total Balance", "Total Return"}
    missing = required_columns.difference(result_df.columns)
    if missing:
        raise ValueError(f"Backtest result is missing required columns: {sorted(missing)}")

    result_df = result_df.copy()
    result_df["Date"] = pd.to_datetime(result_df["Date"])
    result_df = result_df.sort_values("Date").reset_index(drop=True)

    summary_df = portfolio_performance_summary(
        result_df,
        name=strategy_name,
        freq=summary_freq,
    )
    chart_df = result_df[["Date", "Total Balance", "Total Return"]].copy()

    meta = {
        "execution_mode": execution_mode,
        "data_mode": data_mode,
        "strategy_key": strategy_key,
        "tickers": input_params.get("tickers", []),
        "start": input_params.get("start"),
        "end": input_params.get("end"),
        "timeframe": input_params.get("timeframe"),
        "option": input_params.get("option"),
        "rebalance_interval": input_params.get("rebalance_interval"),
        "universe_mode": input_params.get("universe_mode"),
        "preset_name": input_params.get("preset_name"),
        "warnings": warnings or [],
    }
    if input_params.get("top") is not None:
        meta["top"] = input_params.get("top")
    if input_params.get("vol_window") is not None:
        meta["vol_window"] = input_params.get("vol_window")
    if input_params.get("factor_freq") is not None:
        meta["factor_freq"] = input_params.get("factor_freq")
    if input_params.get("rebalance_freq") is not None:
        meta["rebalance_freq"] = input_params.get("rebalance_freq")
    if input_params.get("snapshot_mode") is not None:
        meta["snapshot_mode"] = input_params.get("snapshot_mode")
    if input_params.get("quality_factors") is not None:
        meta["quality_factors"] = input_params.get("quality_factors")
    if input_params.get("value_factors") is not None:
        meta["value_factors"] = input_params.get("value_factors")
    if input_params.get("trend_filter_enabled") is not None:
        meta["trend_filter_enabled"] = input_params.get("trend_filter_enabled")
    if input_params.get("trend_filter_window") is not None:
        meta["trend_filter_window"] = input_params.get("trend_filter_window")
    if input_params.get("market_regime_enabled") is not None:
        meta["market_regime_enabled"] = input_params.get("market_regime_enabled")
    if input_params.get("market_regime_window") is not None:
        meta["market_regime_window"] = input_params.get("market_regime_window")
    if input_params.get("market_regime_benchmark") is not None:
        meta["market_regime_benchmark"] = input_params.get("market_regime_benchmark")
    if input_params.get("min_price_filter") is not None:
        meta["min_price_filter"] = input_params.get("min_price_filter")
    if input_params.get("min_history_months_filter") is not None:
        meta["min_history_months_filter"] = input_params.get("min_history_months_filter")
    if input_params.get("min_avg_dollar_volume_20d_m_filter") is not None:
        meta["min_avg_dollar_volume_20d_m_filter"] = input_params.get("min_avg_dollar_volume_20d_m_filter")
    if input_params.get("transaction_cost_bps") is not None:
        meta["transaction_cost_bps"] = input_params.get("transaction_cost_bps")
    if input_params.get("benchmark_ticker") is not None:
        meta["benchmark_ticker"] = input_params.get("benchmark_ticker")
    if input_params.get("promotion_min_benchmark_coverage") is not None:
        meta["promotion_min_benchmark_coverage"] = input_params.get("promotion_min_benchmark_coverage")
    if input_params.get("promotion_min_net_cagr_spread") is not None:
        meta["promotion_min_net_cagr_spread"] = input_params.get("promotion_min_net_cagr_spread")
    if input_params.get("promotion_min_liquidity_clean_coverage") is not None:
        meta["promotion_min_liquidity_clean_coverage"] = input_params.get("promotion_min_liquidity_clean_coverage")
    if input_params.get("promotion_max_underperformance_share") is not None:
        meta["promotion_max_underperformance_share"] = input_params.get("promotion_max_underperformance_share")
    if input_params.get("promotion_min_worst_rolling_excess_return") is not None:
        meta["promotion_min_worst_rolling_excess_return"] = input_params.get("promotion_min_worst_rolling_excess_return")
    if input_params.get("promotion_max_strategy_drawdown") is not None:
        meta["promotion_max_strategy_drawdown"] = input_params.get("promotion_max_strategy_drawdown")
    if input_params.get("promotion_max_drawdown_gap_vs_benchmark") is not None:
        meta["promotion_max_drawdown_gap_vs_benchmark"] = input_params.get("promotion_max_drawdown_gap_vs_benchmark")
    if input_params.get("underperformance_guardrail_enabled") is not None:
        meta["underperformance_guardrail_enabled"] = input_params.get("underperformance_guardrail_enabled")
    if input_params.get("underperformance_guardrail_window_months") is not None:
        meta["underperformance_guardrail_window_months"] = input_params.get("underperformance_guardrail_window_months")
    if input_params.get("underperformance_guardrail_threshold") is not None:
        meta["underperformance_guardrail_threshold"] = input_params.get("underperformance_guardrail_threshold")
    if input_params.get("snapshot_source") is not None:
        meta["snapshot_source"] = input_params.get("snapshot_source")
    if input_params.get("universe_contract") is not None:
        meta["universe_contract"] = input_params.get("universe_contract")
    if input_params.get("dynamic_target_size") is not None:
        meta["dynamic_target_size"] = input_params.get("dynamic_target_size")
    if input_params.get("dynamic_candidate_count") is not None:
        meta["dynamic_candidate_count"] = input_params.get("dynamic_candidate_count")
    if input_params.get("dynamic_candidate_preview") is not None:
        meta["dynamic_candidate_preview"] = input_params.get("dynamic_candidate_preview")
    if input_params.get("universe_builder_scope") is not None:
        meta["universe_builder_scope"] = input_params.get("universe_builder_scope")
    if input_params.get("universe_debug") is not None:
        meta["universe_debug"] = input_params.get("universe_debug")
    if input_params.get("score_weights") is not None:
        meta["score_weights"] = input_params.get("score_weights")
    if input_params.get("score_lookback_months") is not None:
        meta["score_lookback_months"] = input_params.get("score_lookback_months")
    if input_params.get("score_return_columns") is not None:
        meta["score_return_columns"] = input_params.get("score_return_columns")
    if input_params.get("risk_off_mode") is not None:
        meta["risk_off_mode"] = input_params.get("risk_off_mode")
    if input_params.get("defensive_tickers") is not None:
        meta["defensive_tickers"] = input_params.get("defensive_tickers")
    if input_params.get("crash_guardrail_enabled") is not None:
        meta["crash_guardrail_enabled"] = input_params.get("crash_guardrail_enabled")
    if input_params.get("crash_guardrail_drawdown_threshold") is not None:
        meta["crash_guardrail_drawdown_threshold"] = input_params.get("crash_guardrail_drawdown_threshold")
    if input_params.get("crash_guardrail_lookback_months") is not None:
        meta["crash_guardrail_lookback_months"] = input_params.get("crash_guardrail_lookback_months")

    return {
        "strategy_name": strategy_name,
        "result_df": result_df,
        "summary_df": summary_df,
        "chart_df": chart_df,
        "meta": meta,
    }


def run_equal_weight_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    rebalance_interval: int = 12,
    universe_mode: str = "manual_tickers",
    preset_name: str | None = None,
) -> dict[str, Any]:
    """
    Public UI-facing runtime wrapper for the first DB-backed backtest screen.
    """
    normalized_tickers = _normalize_tickers(tickers)
    _validate_backtest_date_range(start, end)
    _preflight_price_strategy_data(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
    )

    result_df = get_equal_weight_from_db(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        interval=rebalance_interval,
    )

    return build_backtest_result_bundle(
        result_df,
        strategy_name="Equal Weight",
        strategy_key="equal_weight",
        input_params={
            "tickers": normalized_tickers,
            "start": start,
            "end": end,
            "timeframe": timeframe,
            "option": option,
            "rebalance_interval": rebalance_interval,
            "universe_mode": universe_mode,
            "preset_name": preset_name,
        },
        summary_freq=_summary_frequency(option, timeframe),
    )


def run_gtaa_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    top: int = 3,
    interval: int = GTAA_DEFAULT_SIGNAL_INTERVAL,
    min_price_filter: float | None = None,
    transaction_cost_bps: float | None = None,
    benchmark_ticker: str | None = None,
    score_lookback_months: Sequence[int] | None = None,
    score_return_columns: Sequence[str] | None = None,
    score_weights: dict[str, float] | None = None,
    trend_filter_window: int = GTAA_DEFAULT_TREND_FILTER_WINDOW,
    risk_off_mode: str = GTAA_DEFAULT_RISK_OFF_MODE,
    defensive_tickers: Sequence[str] | None = None,
    market_regime_enabled: bool = False,
    market_regime_window: int = STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    market_regime_benchmark: str = STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    crash_guardrail_enabled: bool = GTAA_DEFAULT_CRASH_GUARDRAIL_ENABLED,
    crash_guardrail_drawdown_threshold: float = GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD,
    crash_guardrail_lookback_months: int = GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS,
    universe_mode: str = "preset",
    preset_name: str | None = None,
) -> dict[str, Any]:
    """
    Public UI-facing runtime wrapper for the second DB-backed backtest screen.
    """
    normalized_tickers = _normalize_tickers(tickers)
    _validate_backtest_date_range(start, end)
    _preflight_price_strategy_data(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
    )
    if (market_regime_enabled or crash_guardrail_enabled) and market_regime_benchmark:
        benchmark_symbol = str(market_regime_benchmark).strip().upper()
        if benchmark_symbol and benchmark_symbol not in normalized_tickers:
            _preflight_price_strategy_data(
                tickers=[benchmark_symbol],
                start=start,
                end=end,
                timeframe=timeframe,
            )

    normalized_score_lookback_months = [
        int(value)
        for value in (
            list(score_lookback_months)
            if score_lookback_months is not None
            else list(GTAA_DEFAULT_SCORE_LOOKBACK_MONTHS)
        )
    ]
    normalized_score_return_columns = [f"{months}MReturn" for months in normalized_score_lookback_months]
    normalized_score_weights = (
        {f"{months}MReturn": 1.0 for months in normalized_score_lookback_months}
        if score_weights is None
        else dict(score_weights)
    )

    result_df = get_gtaa3_from_db(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        top=top,
        interval=interval,
        min_price=min_price_filter,
        score_lookback_months=normalized_score_lookback_months,
        score_return_columns=normalized_score_return_columns,
        score_weights=normalized_score_weights,
        trend_filter_window=trend_filter_window,
        risk_off_mode=risk_off_mode,
        defensive_tickers=list(defensive_tickers or GTAA_DEFAULT_DEFENSIVE_TICKERS),
        market_regime_enabled=market_regime_enabled,
        market_regime_window=market_regime_window,
        market_regime_benchmark=market_regime_benchmark,
        crash_guardrail_enabled=crash_guardrail_enabled,
        crash_guardrail_drawdown_threshold=crash_guardrail_drawdown_threshold,
        crash_guardrail_lookback_months=crash_guardrail_lookback_months,
    )

    bundle = build_backtest_result_bundle(
        result_df,
        strategy_name="GTAA",
        strategy_key="gtaa",
        input_params={
            "tickers": normalized_tickers,
            "start": start,
            "end": end,
            "timeframe": timeframe,
            "option": option,
            "top": top,
            "rebalance_interval": interval,
            "min_price_filter": min_price_filter,
            "transaction_cost_bps": transaction_cost_bps,
            "benchmark_ticker": benchmark_ticker,
            "score_lookback_months": normalized_score_lookback_months,
            "score_return_columns": normalized_score_return_columns,
            "score_weights": normalized_score_weights,
            "trend_filter_window": trend_filter_window,
            "risk_off_mode": risk_off_mode,
            "defensive_tickers": list(defensive_tickers or GTAA_DEFAULT_DEFENSIVE_TICKERS),
            "market_regime_enabled": market_regime_enabled,
            "market_regime_window": market_regime_window,
            "market_regime_benchmark": market_regime_benchmark,
            "crash_guardrail_enabled": crash_guardrail_enabled,
            "crash_guardrail_drawdown_threshold": crash_guardrail_drawdown_threshold,
            "crash_guardrail_lookback_months": crash_guardrail_lookback_months,
            "universe_mode": universe_mode,
            "preset_name": preset_name,
        },
        summary_freq=_summary_frequency(option, timeframe),
    )
    return _apply_real_money_hardening(
        bundle,
        summary_freq=_summary_frequency(option, timeframe),
        min_price_filter=min_price_filter,
        transaction_cost_bps=transaction_cost_bps,
        benchmark_contract=STRICT_DEFAULT_BENCHMARK_CONTRACT,
        benchmark_ticker=benchmark_ticker,
        benchmark_universe_tickers=normalized_tickers,
    )


def run_risk_parity_trend_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    rebalance_interval: int = 1,
    vol_window: int = 6,
    min_price_filter: float = ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
    transaction_cost_bps: float = ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
    benchmark_ticker: str = ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    universe_mode: str = "preset",
    preset_name: str | None = None,
) -> dict[str, Any]:
    normalized_tickers = _normalize_tickers(tickers)
    _validate_backtest_date_range(start, end)
    _preflight_price_strategy_data(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
    )

    result_df = get_risk_parity_trend_from_db(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        rebalance_interval=rebalance_interval,
        vol_window=vol_window,
        min_price=min_price_filter,
    )

    bundle = build_backtest_result_bundle(
        result_df,
        strategy_name="Risk Parity Trend",
        strategy_key="risk_parity_trend",
        input_params={
            "tickers": normalized_tickers,
            "start": start,
            "end": end,
            "timeframe": timeframe,
            "option": option,
            "rebalance_interval": rebalance_interval,
            "vol_window": vol_window,
            "min_price_filter": min_price_filter,
            "transaction_cost_bps": transaction_cost_bps,
            "benchmark_ticker": benchmark_ticker,
            "universe_mode": universe_mode,
            "preset_name": preset_name,
        },
        summary_freq=_summary_frequency(option, timeframe),
    )
    return _apply_real_money_hardening(
        bundle,
        summary_freq=_summary_frequency(option, timeframe),
        min_price_filter=min_price_filter,
        transaction_cost_bps=transaction_cost_bps,
        benchmark_contract=STRICT_DEFAULT_BENCHMARK_CONTRACT,
        benchmark_ticker=benchmark_ticker,
        benchmark_universe_tickers=normalized_tickers,
    )


def run_dual_momentum_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    top: int = 1,
    rebalance_interval: int = 1,
    min_price_filter: float = ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
    transaction_cost_bps: float = ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
    benchmark_ticker: str = ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    universe_mode: str = "preset",
    preset_name: str | None = None,
) -> dict[str, Any]:
    normalized_tickers = _normalize_tickers(tickers)
    _validate_backtest_date_range(start, end)
    _preflight_price_strategy_data(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
    )

    result_df = get_dual_momentum_from_db(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        top=top,
        rebalance_interval=rebalance_interval,
        min_price=min_price_filter,
    )

    bundle = build_backtest_result_bundle(
        result_df,
        strategy_name="Dual Momentum",
        strategy_key="dual_momentum",
        input_params={
            "tickers": normalized_tickers,
            "start": start,
            "end": end,
            "timeframe": timeframe,
            "option": option,
            "top": top,
            "rebalance_interval": rebalance_interval,
            "min_price_filter": min_price_filter,
            "transaction_cost_bps": transaction_cost_bps,
            "benchmark_ticker": benchmark_ticker,
            "universe_mode": universe_mode,
            "preset_name": preset_name,
        },
        summary_freq=_summary_frequency(option, timeframe),
    )
    return _apply_real_money_hardening(
        bundle,
        summary_freq=_summary_frequency(option, timeframe),
        min_price_filter=min_price_filter,
        transaction_cost_bps=transaction_cost_bps,
        benchmark_contract=STRICT_DEFAULT_BENCHMARK_CONTRACT,
        benchmark_ticker=benchmark_ticker,
        benchmark_universe_tickers=normalized_tickers,
    )


def run_quality_snapshot_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    factor_freq: str = "annual",
    rebalance_freq: str = "monthly",
    quality_factors: Sequence[str] | None = None,
    top_n: int = 2,
    rebalance_interval: int = 1,
    snapshot_mode: str = "broad_research",
    universe_mode: str = "manual_tickers",
    preset_name: str | None = None,
) -> dict[str, Any]:
    normalized_tickers = _normalize_tickers(tickers)
    _validate_backtest_date_range(start, end)

    if snapshot_mode != "broad_research":
        raise BacktestInputError("The first public quality snapshot runtime supports only 'broad_research' mode.")
    if rebalance_freq != "monthly":
        raise BacktestInputError("The first public quality snapshot runtime currently supports only monthly rebalance.")

    normalized_factors = [str(name).strip() for name in (quality_factors or ["roe", "gross_margin", "operating_margin", "debt_ratio"]) if str(name).strip()]
    if not normalized_factors:
        raise BacktestInputError("At least one quality factor must be provided.")

    _preflight_price_strategy_data(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
    )
    _preflight_quality_snapshot_data(
        tickers=normalized_tickers,
        end=end,
        factor_freq=factor_freq,
        quality_factors=normalized_factors,
    )

    result_df = get_quality_snapshot_from_db(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        factor_freq=factor_freq,
        quality_factors=normalized_factors,
        top_n=top_n,
        rebalance_interval=rebalance_interval,
        snapshot_mode=snapshot_mode,
    )

    warnings: list[str] = []
    if start:
        selected_mask = result_df.get("Selected Count")
        if selected_mask is not None:
            active_rows = result_df[result_df["Selected Count"].fillna(0) > 0]
            if not active_rows.empty:
                first_active_date = pd.to_datetime(active_rows.iloc[0]["Date"]).strftime("%Y-%m-%d")
                if first_active_date > start:
                    warnings.append(
                        "No usable quality snapshot rows were available at the requested start date. "
                        f"The strategy stayed in cash until `{first_active_date}`."
                    )

    return build_backtest_result_bundle(
        result_df,
        strategy_name="Quality Snapshot",
        strategy_key="quality_snapshot",
        input_params={
            "tickers": normalized_tickers,
            "start": start,
            "end": end,
            "timeframe": timeframe,
            "option": option,
            "top": top_n,
            "rebalance_interval": rebalance_interval,
            "factor_freq": factor_freq,
            "rebalance_freq": rebalance_freq,
            "snapshot_mode": snapshot_mode,
            "quality_factors": normalized_factors,
            "universe_mode": universe_mode,
            "preset_name": preset_name,
        },
        summary_freq=_summary_frequency(option, timeframe),
        data_mode="db_backed_factor_snapshot",
        warnings=warnings,
    )


def _run_statement_quality_bundle(
    *,
    strategy_name: str,
    strategy_key: str,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    statement_freq: str = "annual",
    quality_factors: Sequence[str] | None = None,
    top_n: int = 2,
    rebalance_interval: int = 1,
    min_price_filter: float = ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
    min_history_months_filter: int = STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
    min_avg_dollar_volume_20d_m_filter: float = STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
    transaction_cost_bps: float = ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
    benchmark_contract: str = STRICT_DEFAULT_BENCHMARK_CONTRACT,
    benchmark_ticker: str = ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    promotion_min_benchmark_coverage: float = STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
    promotion_min_net_cagr_spread: float = STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
    promotion_min_liquidity_clean_coverage: float = STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
    promotion_max_underperformance_share: float = STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
    promotion_min_worst_rolling_excess_return: float = STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
    promotion_max_strategy_drawdown: float = STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
    promotion_max_drawdown_gap_vs_benchmark: float = STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
    trend_filter_enabled: bool = False,
    trend_filter_window: int = 200,
    market_regime_enabled: bool = False,
    market_regime_window: int = STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    market_regime_benchmark: str = STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    underperformance_guardrail_enabled: bool = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    underperformance_guardrail_window_months: int = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    underperformance_guardrail_threshold: float = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    universe_mode: str = "manual_tickers",
    preset_name: str | None = None,
    universe_contract: str = STATIC_MANAGED_RESEARCH_UNIVERSE,
    dynamic_candidate_tickers: Sequence[str] | None = None,
    dynamic_target_size: int | None = None,
    static_warnings: Sequence[str] | None = None,
    snapshot_source: str = "rebuild_statement",
) -> dict[str, Any]:
    normalized_tickers = _normalize_tickers(tickers)
    _validate_backtest_date_range(start, end)
    strict_label = f"strict {statement_freq}"
    universe_input_tickers = normalized_tickers
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        universe_input_tickers = _normalize_tickers(dynamic_candidate_tickers or normalized_tickers)

    normalized_factors = [
        str(name).strip()
        for name in (quality_factors or QUALITY_STRICT_DEFAULT_FACTORS)
        if str(name).strip()
    ]
    if not normalized_factors:
        raise BacktestInputError("At least one quality factor must be provided.")

    price_freshness = inspect_strict_annual_price_freshness(
        tickers=universe_input_tickers,
        end=end,
        timeframe=timeframe,
    )

    dynamic_price_pool = None
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        dynamic_price_pool = _inspect_dynamic_universe_price_pool(
            tickers=universe_input_tickers,
            end=end,
            timeframe=timeframe,
        )
    else:
        _preflight_price_strategy_data(
            tickers=universe_input_tickers,
            start=start,
            end=end,
            timeframe=timeframe,
        )
    if market_regime_enabled:
        _preflight_price_strategy_data(
            tickers=[market_regime_benchmark],
            start=start,
            end=end,
            timeframe=timeframe,
        )
    if underperformance_guardrail_enabled and benchmark_ticker:
        _preflight_price_strategy_data(
            tickers=[benchmark_ticker],
            start=start,
            end=end,
            timeframe=timeframe,
        )
    if snapshot_source == "shadow_factors":
        _preflight_statement_quality_shadow_data(
            tickers=universe_input_tickers,
            end=end,
            statement_freq=statement_freq,
            factor_names=normalized_factors,
        )
        result_payload = get_statement_quality_snapshot_shadow_from_db(
            tickers=normalized_tickers,
            start=start,
            end=end,
            timeframe=timeframe,
            option=option,
            statement_freq=statement_freq,
            quality_factors=normalized_factors,
            top_n=top_n,
            rebalance_interval=rebalance_interval,
            min_price=float(min_price_filter or 0.0),
            min_history_months=int(min_history_months_filter or 0),
            min_avg_dollar_volume_20d_m=float(min_avg_dollar_volume_20d_m_filter or 0.0),
            trend_filter_enabled=trend_filter_enabled,
            trend_filter_window=trend_filter_window,
            market_regime_enabled=market_regime_enabled,
            market_regime_window=market_regime_window,
            market_regime_benchmark=market_regime_benchmark,
            benchmark_ticker=benchmark_ticker,
            underperformance_guardrail_enabled=underperformance_guardrail_enabled,
            underperformance_guardrail_window_months=underperformance_guardrail_window_months,
            underperformance_guardrail_threshold=underperformance_guardrail_threshold,
            universe_contract=universe_contract,
            dynamic_candidate_tickers=universe_input_tickers,
            dynamic_target_size=dynamic_target_size,
            return_details=True,
        )
        result_df = result_payload["result_df"]
        universe_debug = result_payload.get("universe_debug")
        dynamic_universe_snapshot_rows = result_payload.get("universe_snapshot_rows") or []
        dynamic_candidate_status_rows = result_payload.get("candidate_status_rows") or []
    else:
        _preflight_statement_quality_data(
            tickers=normalized_tickers,
            end=end,
            statement_freq=statement_freq,
        )
        result_df = get_statement_quality_snapshot_from_db(
            tickers=normalized_tickers,
            start=start,
            end=end,
            timeframe=timeframe,
            option=option,
            statement_freq=statement_freq,
            quality_factors=normalized_factors,
            top_n=top_n,
            rebalance_interval=rebalance_interval,
        )
        universe_debug = None
        dynamic_universe_snapshot_rows = []
        dynamic_candidate_status_rows = []

    warnings: list[str] = list(static_warnings or [])
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        warnings.append(_dynamic_universe_warning(statement_freq))
        if dynamic_price_pool and dynamic_price_pool["missing_count"] > 0:
            preview = ", ".join(dynamic_price_pool["missing_symbols"][:15])
            more = ""
            if dynamic_price_pool["missing_count"] > 15:
                more = f" ... (+{dynamic_price_pool['missing_count'] - 15} more)"
            warnings.append(
                "Dynamic candidate pool note: "
                f"{dynamic_price_pool['missing_count']} candidate symbols do not have any DB price history up to the selected end date "
                f"and were naturally excluded from the approximate PIT membership build: {preview}{more}"
            )
    if price_freshness["status"] == "warning":
        warnings.append(
            "Price freshness preflight: "
            + price_freshness["message"]
            + f" Large-universe {strict_label} runs can show duplicate or shifted final-month rows until lagging symbols are refreshed."
        )
    if start:
        active_rows = result_df[result_df["Selected Count"].fillna(0) > 0]
        if not active_rows.empty:
            first_active_date = pd.to_datetime(active_rows.iloc[0]["Date"]).strftime("%Y-%m-%d")
            if first_active_date > start:
                warnings.append(
                    "No usable strict statement snapshot rows were available at the requested start date. "
                    f"The strategy stayed in cash until `{first_active_date}`."
                )
    if min_history_months_filter:
        warnings.append(
            "Minimum history filter enabled: candidates need at least "
            f"`{int(min_history_months_filter)}M` of DB price history before each rebalance."
        )
    if min_avg_dollar_volume_20d_m_filter:
        warnings.append(
            "Liquidity filter enabled: candidates need at least "
            f"`{float(min_avg_dollar_volume_20d_m_filter):.1f}M` of trailing 20-day average dollar volume "
            "before each rebalance."
        )

    input_params = {
        "tickers": normalized_tickers,
        "start": start,
        "end": end,
        "timeframe": timeframe,
        "option": option,
        "top": top_n,
        "rebalance_interval": rebalance_interval,
        "factor_freq": statement_freq,
        "quality_factors": normalized_factors,
        "trend_filter_enabled": trend_filter_enabled,
        "trend_filter_window": trend_filter_window,
        "market_regime_enabled": market_regime_enabled,
        "market_regime_window": market_regime_window,
        "market_regime_benchmark": market_regime_benchmark,
        "underperformance_guardrail_enabled": underperformance_guardrail_enabled,
        "underperformance_guardrail_window_months": underperformance_guardrail_window_months,
        "underperformance_guardrail_threshold": underperformance_guardrail_threshold,
        "snapshot_mode": f"strict_statement_{statement_freq}",
        "universe_mode": universe_mode,
        "preset_name": preset_name,
        "snapshot_source": snapshot_source,
        "universe_contract": universe_contract,
        "dynamic_target_size": dynamic_target_size,
        "dynamic_candidate_count": len(universe_input_tickers),
        "dynamic_candidate_preview": universe_input_tickers[:20],
        "universe_builder_scope": (
            f"{statement_freq}_first_pass"
            if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE
            else None
        ),
        "universe_debug": universe_debug,
    }
    if min_price_filter is not None:
        input_params["min_price_filter"] = min_price_filter
    if min_history_months_filter is not None:
        input_params["min_history_months_filter"] = int(min_history_months_filter or 0)
    if min_avg_dollar_volume_20d_m_filter is not None:
        input_params["min_avg_dollar_volume_20d_m_filter"] = float(min_avg_dollar_volume_20d_m_filter or 0.0)
    if transaction_cost_bps is not None:
        input_params["transaction_cost_bps"] = transaction_cost_bps
    if benchmark_contract is not None:
        input_params["benchmark_contract"] = str(benchmark_contract or STRICT_DEFAULT_BENCHMARK_CONTRACT).strip().lower()
    if benchmark_ticker is not None:
        input_params["benchmark_ticker"] = benchmark_ticker
    if promotion_min_benchmark_coverage is not None:
        input_params["promotion_min_benchmark_coverage"] = float(promotion_min_benchmark_coverage)
    if promotion_min_net_cagr_spread is not None:
        input_params["promotion_min_net_cagr_spread"] = float(promotion_min_net_cagr_spread)
    if promotion_min_liquidity_clean_coverage is not None:
        input_params["promotion_min_liquidity_clean_coverage"] = float(promotion_min_liquidity_clean_coverage)
    if promotion_max_underperformance_share is not None:
        input_params["promotion_max_underperformance_share"] = float(promotion_max_underperformance_share)
    if promotion_min_worst_rolling_excess_return is not None:
        input_params["promotion_min_worst_rolling_excess_return"] = float(promotion_min_worst_rolling_excess_return)
    if promotion_max_strategy_drawdown is not None:
        input_params["promotion_max_strategy_drawdown"] = float(promotion_max_strategy_drawdown)
    if promotion_max_drawdown_gap_vs_benchmark is not None:
        input_params["promotion_max_drawdown_gap_vs_benchmark"] = float(promotion_max_drawdown_gap_vs_benchmark)

    bundle = build_backtest_result_bundle(
        result_df,
        strategy_name=strategy_name,
        strategy_key=strategy_key,
        input_params=input_params,
        summary_freq=_summary_frequency(option, timeframe),
        data_mode="db_backed_strict_statement_shadow_factors" if snapshot_source == "shadow_factors" else "db_backed_strict_statement_snapshot",
        warnings=warnings,
    )
    bundle["meta"]["price_freshness"] = price_freshness
    if trend_filter_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            f"Trend Filter Overlay enabled: month-end selections with `Close < MA{trend_filter_window}` move to cash until the next rebalance."
        ]
    if market_regime_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            f"Market Regime Overlay enabled: month-end selections move fully to cash when `{market_regime_benchmark}` closes below `MA{market_regime_window}`."
        ]
    if underperformance_guardrail_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            "Underperformance Guardrail enabled: rebalance candidates move to cash when trailing strategy excess return "
            f"vs `{benchmark_ticker}` over `{underperformance_guardrail_window_months}M` falls below "
            f"`{underperformance_guardrail_threshold:.0%}`."
        ]
    if dynamic_universe_snapshot_rows:
        bundle["dynamic_universe_snapshot_rows"] = dynamic_universe_snapshot_rows
    if dynamic_candidate_status_rows:
        bundle["dynamic_candidate_status_rows"] = dynamic_candidate_status_rows
    return bundle


def run_quality_snapshot_strict_annual_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    quality_factors: Sequence[str] | None = None,
    top_n: int = 2,
    rebalance_interval: int = 1,
    min_price_filter: float = ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
    min_history_months_filter: int = STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
    min_avg_dollar_volume_20d_m_filter: float = STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
    transaction_cost_bps: float = ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
    benchmark_contract: str = STRICT_DEFAULT_BENCHMARK_CONTRACT,
    benchmark_ticker: str = ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    promotion_min_benchmark_coverage: float = STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
    promotion_min_net_cagr_spread: float = STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
    promotion_min_liquidity_clean_coverage: float = STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
    promotion_max_underperformance_share: float = STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
    promotion_min_worst_rolling_excess_return: float = STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
    promotion_max_strategy_drawdown: float = STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
    promotion_max_drawdown_gap_vs_benchmark: float = STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
    trend_filter_enabled: bool = False,
    trend_filter_window: int = 200,
    market_regime_enabled: bool = False,
    market_regime_window: int = STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    market_regime_benchmark: str = STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    underperformance_guardrail_enabled: bool = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    underperformance_guardrail_window_months: int = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    underperformance_guardrail_threshold: float = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    universe_mode: str = "manual_tickers",
    preset_name: str | None = None,
    universe_contract: str = STATIC_MANAGED_RESEARCH_UNIVERSE,
    dynamic_candidate_tickers: Sequence[str] | None = None,
    dynamic_target_size: int | None = None,
) -> dict[str, Any]:
    bundle = _run_statement_quality_bundle(
        strategy_name="Quality Snapshot (Strict Annual)",
        strategy_key="quality_snapshot_strict_annual",
        tickers=tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        statement_freq="annual",
        quality_factors=quality_factors,
        top_n=top_n,
        rebalance_interval=rebalance_interval,
        min_price_filter=min_price_filter,
        min_history_months_filter=min_history_months_filter,
        min_avg_dollar_volume_20d_m_filter=min_avg_dollar_volume_20d_m_filter,
        transaction_cost_bps=transaction_cost_bps,
        benchmark_contract=benchmark_contract,
        benchmark_ticker=benchmark_ticker,
        promotion_min_benchmark_coverage=promotion_min_benchmark_coverage,
        promotion_min_net_cagr_spread=promotion_min_net_cagr_spread,
        promotion_min_liquidity_clean_coverage=promotion_min_liquidity_clean_coverage,
        promotion_max_underperformance_share=promotion_max_underperformance_share,
        promotion_min_worst_rolling_excess_return=promotion_min_worst_rolling_excess_return,
        promotion_max_strategy_drawdown=promotion_max_strategy_drawdown,
        promotion_max_drawdown_gap_vs_benchmark=promotion_max_drawdown_gap_vs_benchmark,
        trend_filter_enabled=trend_filter_enabled,
        trend_filter_window=trend_filter_window,
        market_regime_enabled=market_regime_enabled,
        market_regime_window=market_regime_window,
        market_regime_benchmark=market_regime_benchmark,
        underperformance_guardrail_enabled=underperformance_guardrail_enabled,
        underperformance_guardrail_window_months=underperformance_guardrail_window_months,
        underperformance_guardrail_threshold=underperformance_guardrail_threshold,
        universe_mode=universe_mode,
        preset_name=preset_name,
        universe_contract=universe_contract,
        dynamic_candidate_tickers=dynamic_candidate_tickers,
        dynamic_target_size=dynamic_target_size,
        snapshot_source="shadow_factors",
        static_warnings=[
            "Strict annual statement path: ranks annual statement-driven quality snapshots using precomputed statement shadow factors for faster public execution.",
        ],
    )
    return _apply_real_money_hardening(
        bundle,
        summary_freq=_summary_frequency(option, timeframe),
        min_price_filter=min_price_filter,
        transaction_cost_bps=transaction_cost_bps,
        benchmark_contract=benchmark_contract,
        benchmark_ticker=benchmark_ticker,
        benchmark_universe_tickers=_normalize_tickers(dynamic_candidate_tickers or tickers),
        promotion_min_benchmark_coverage=promotion_min_benchmark_coverage,
        promotion_min_net_cagr_spread=promotion_min_net_cagr_spread,
        promotion_min_liquidity_clean_coverage=promotion_min_liquidity_clean_coverage,
        promotion_max_underperformance_share=promotion_max_underperformance_share,
        promotion_min_worst_rolling_excess_return=promotion_min_worst_rolling_excess_return,
        promotion_max_strategy_drawdown=promotion_max_strategy_drawdown,
        promotion_max_drawdown_gap_vs_benchmark=promotion_max_drawdown_gap_vs_benchmark,
    )


def run_statement_quality_prototype_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    statement_freq: str = "annual",
    quality_factors: Sequence[str] | None = None,
    top_n: int = 2,
    rebalance_interval: int = 1,
    trend_filter_enabled: bool = False,
    trend_filter_window: int = 200,
    market_regime_enabled: bool = False,
    market_regime_window: int = STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    market_regime_benchmark: str = STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    universe_mode: str = "manual_tickers",
    preset_name: str | None = None,
) -> dict[str, Any]:
    return _run_statement_quality_bundle(
        strategy_name="Statement Quality Prototype",
        strategy_key="statement_quality_prototype",
        tickers=tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        statement_freq=statement_freq,
        quality_factors=quality_factors,
        top_n=top_n,
        rebalance_interval=rebalance_interval,
        trend_filter_enabled=trend_filter_enabled,
        trend_filter_window=trend_filter_window,
        market_regime_enabled=market_regime_enabled,
        market_regime_window=market_regime_window,
        market_regime_benchmark=market_regime_benchmark,
        universe_mode=universe_mode,
        preset_name=preset_name,
        snapshot_source="rebuild_statement",
        static_warnings=[
            "Prototype path: strict statement snapshots are used for sample-universe architecture validation.",
        ],
    )


def run_value_snapshot_strict_annual_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    value_factors: Sequence[str] | None = None,
    top_n: int = 10,
    rebalance_interval: int = 1,
    min_price_filter: float = ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
    min_history_months_filter: int = STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
    min_avg_dollar_volume_20d_m_filter: float = STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
    transaction_cost_bps: float = ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
    benchmark_contract: str = STRICT_DEFAULT_BENCHMARK_CONTRACT,
    benchmark_ticker: str = ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    promotion_min_benchmark_coverage: float = STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
    promotion_min_net_cagr_spread: float = STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
    promotion_min_liquidity_clean_coverage: float = STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
    promotion_max_underperformance_share: float = STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
    promotion_min_worst_rolling_excess_return: float = STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
    promotion_max_strategy_drawdown: float = STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
    promotion_max_drawdown_gap_vs_benchmark: float = STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
    trend_filter_enabled: bool = False,
    trend_filter_window: int = 200,
    market_regime_enabled: bool = False,
    market_regime_window: int = STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    market_regime_benchmark: str = STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    underperformance_guardrail_enabled: bool = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    underperformance_guardrail_window_months: int = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    underperformance_guardrail_threshold: float = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    universe_mode: str = "manual_tickers",
    preset_name: str | None = None,
    universe_contract: str = STATIC_MANAGED_RESEARCH_UNIVERSE,
    dynamic_candidate_tickers: Sequence[str] | None = None,
    dynamic_target_size: int | None = None,
) -> dict[str, Any]:
    normalized_tickers = _normalize_tickers(tickers)
    _validate_backtest_date_range(start, end)
    universe_input_tickers = normalized_tickers
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        universe_input_tickers = _normalize_tickers(dynamic_candidate_tickers or normalized_tickers)

    normalized_factors = [
        str(name).strip()
        for name in (value_factors or VALUE_STRICT_DEFAULT_FACTORS)
        if str(name).strip()
    ]
    if not normalized_factors:
        raise BacktestInputError("At least one value factor must be provided.")

    price_freshness = inspect_strict_annual_price_freshness(
        tickers=universe_input_tickers,
        end=end,
        timeframe=timeframe,
    )

    dynamic_price_pool = None
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        dynamic_price_pool = _inspect_dynamic_universe_price_pool(
            tickers=universe_input_tickers,
            end=end,
            timeframe=timeframe,
        )
    else:
        _preflight_price_strategy_data(
            tickers=universe_input_tickers,
            start=start,
            end=end,
            timeframe=timeframe,
        )
    if market_regime_enabled:
        _preflight_price_strategy_data(
            tickers=[market_regime_benchmark],
            start=start,
            end=end,
            timeframe=timeframe,
        )
    if underperformance_guardrail_enabled and benchmark_ticker:
        _preflight_price_strategy_data(
            tickers=[benchmark_ticker],
            start=start,
            end=end,
            timeframe=timeframe,
        )
    _preflight_statement_quality_shadow_data(
        tickers=universe_input_tickers,
        end=end,
        statement_freq="annual",
        factor_names=normalized_factors,
    )

    result_payload = get_statement_value_snapshot_shadow_from_db(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        statement_freq="annual",
        value_factors=normalized_factors,
        top_n=top_n,
        rebalance_interval=rebalance_interval,
        min_price=min_price_filter,
        min_history_months=min_history_months_filter,
        min_avg_dollar_volume_20d_m=min_avg_dollar_volume_20d_m_filter,
        trend_filter_enabled=trend_filter_enabled,
        trend_filter_window=trend_filter_window,
        market_regime_enabled=market_regime_enabled,
        market_regime_window=market_regime_window,
        market_regime_benchmark=market_regime_benchmark,
        benchmark_ticker=benchmark_ticker,
        underperformance_guardrail_enabled=underperformance_guardrail_enabled,
        underperformance_guardrail_window_months=underperformance_guardrail_window_months,
        underperformance_guardrail_threshold=underperformance_guardrail_threshold,
        universe_contract=universe_contract,
        dynamic_candidate_tickers=universe_input_tickers,
        dynamic_target_size=dynamic_target_size,
        return_details=True,
    )
    result_df = result_payload["result_df"]
    universe_debug = result_payload.get("universe_debug")
    dynamic_universe_snapshot_rows = result_payload.get("universe_snapshot_rows") or []
    dynamic_candidate_status_rows = result_payload.get("candidate_status_rows") or []

    warnings = [
        "Strict annual value path: ranks annual statement-driven value snapshots using precomputed statement shadow factors.",
    ]
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        warnings.append(_dynamic_universe_warning("annual"))
        if dynamic_price_pool and dynamic_price_pool["missing_count"] > 0:
            preview = ", ".join(dynamic_price_pool["missing_symbols"][:15])
            more = ""
            if dynamic_price_pool["missing_count"] > 15:
                more = f" ... (+{dynamic_price_pool['missing_count'] - 15} more)"
            warnings.append(
                "Dynamic candidate pool note: "
                f"{dynamic_price_pool['missing_count']} candidate symbols do not have any DB price history up to the selected end date "
                f"and were naturally excluded from the approximate PIT membership build: {preview}{more}"
            )
    if price_freshness["status"] == "warning":
        warnings.append(
            "Price freshness preflight: "
            + price_freshness["message"]
            + " Large-universe strict annual runs can show duplicate or shifted final-month rows until lagging symbols are refreshed."
        )
    if start:
        active_rows = result_df[result_df["Selected Count"].fillna(0) > 0]
        if not active_rows.empty:
            first_active_date = pd.to_datetime(active_rows.iloc[0]["Date"]).strftime("%Y-%m-%d")
            if first_active_date > start:
                warnings.append(
                    "No usable strict statement shadow rows were available at the requested start date. "
                    f"The strategy stayed in cash until `{first_active_date}`."
                )
    if min_history_months_filter:
        warnings.append(
            "Minimum history filter enabled: candidates need at least "
            f"`{int(min_history_months_filter)}M` of DB price history before each rebalance."
        )
    if min_avg_dollar_volume_20d_m_filter:
        warnings.append(
            "Liquidity filter enabled: candidates need at least "
            f"`{float(min_avg_dollar_volume_20d_m_filter):.1f}M` of trailing 20-day average dollar volume "
            "before each rebalance."
        )

    bundle = build_backtest_result_bundle(
        result_df,
        strategy_name="Value Snapshot (Strict Annual)",
        strategy_key="value_snapshot_strict_annual",
        input_params={
            "tickers": normalized_tickers,
            "start": start,
            "end": end,
            "timeframe": timeframe,
            "option": option,
            "top": top_n,
            "rebalance_interval": rebalance_interval,
            "min_price_filter": min_price_filter,
            "min_history_months_filter": int(min_history_months_filter or 0),
            "min_avg_dollar_volume_20d_m_filter": float(min_avg_dollar_volume_20d_m_filter or 0.0),
            "transaction_cost_bps": transaction_cost_bps,
            "benchmark_contract": benchmark_contract,
            "benchmark_ticker": benchmark_ticker,
            "promotion_min_benchmark_coverage": float(promotion_min_benchmark_coverage),
            "promotion_min_net_cagr_spread": float(promotion_min_net_cagr_spread),
            "promotion_min_liquidity_clean_coverage": float(promotion_min_liquidity_clean_coverage),
            "promotion_max_underperformance_share": float(promotion_max_underperformance_share),
            "promotion_min_worst_rolling_excess_return": float(promotion_min_worst_rolling_excess_return),
            "promotion_max_strategy_drawdown": float(promotion_max_strategy_drawdown),
            "promotion_max_drawdown_gap_vs_benchmark": float(promotion_max_drawdown_gap_vs_benchmark),
            "factor_freq": "annual",
            "value_factors": normalized_factors,
            "trend_filter_enabled": trend_filter_enabled,
            "trend_filter_window": trend_filter_window,
            "market_regime_enabled": market_regime_enabled,
            "market_regime_window": market_regime_window,
            "market_regime_benchmark": market_regime_benchmark,
            "underperformance_guardrail_enabled": underperformance_guardrail_enabled,
            "underperformance_guardrail_window_months": underperformance_guardrail_window_months,
            "underperformance_guardrail_threshold": underperformance_guardrail_threshold,
            "snapshot_mode": "strict_statement_annual",
            "snapshot_source": "shadow_factors",
            "universe_mode": universe_mode,
            "preset_name": preset_name,
            "universe_contract": universe_contract,
            "dynamic_target_size": dynamic_target_size,
            "dynamic_candidate_count": len(universe_input_tickers),
            "dynamic_candidate_preview": universe_input_tickers[:20],
            "universe_builder_scope": ("annual_first_pass" if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE else None),
            "universe_debug": universe_debug,
        },
        summary_freq=_summary_frequency(option, timeframe),
        data_mode="db_backed_strict_statement_shadow_factors",
        warnings=warnings,
    )
    bundle["meta"]["price_freshness"] = price_freshness
    if trend_filter_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            f"Trend Filter Overlay enabled: month-end selections with `Close < MA{trend_filter_window}` move to cash until the next rebalance."
        ]
    if market_regime_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            f"Market Regime Overlay enabled: month-end selections move fully to cash when `{market_regime_benchmark}` closes below `MA{market_regime_window}`."
        ]
    if underperformance_guardrail_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            "Underperformance Guardrail enabled: rebalance candidates move to cash when trailing strategy excess return "
            f"vs `{benchmark_ticker}` over `{underperformance_guardrail_window_months}M` falls below "
            f"`{underperformance_guardrail_threshold:.0%}`."
        ]
    if dynamic_universe_snapshot_rows:
        bundle["dynamic_universe_snapshot_rows"] = dynamic_universe_snapshot_rows
    if dynamic_candidate_status_rows:
        bundle["dynamic_candidate_status_rows"] = dynamic_candidate_status_rows
    return _apply_real_money_hardening(
        bundle,
        summary_freq=_summary_frequency(option, timeframe),
        min_price_filter=min_price_filter,
        transaction_cost_bps=transaction_cost_bps,
        benchmark_contract=benchmark_contract,
        benchmark_ticker=benchmark_ticker,
        benchmark_universe_tickers=universe_input_tickers,
        promotion_min_benchmark_coverage=promotion_min_benchmark_coverage,
        promotion_min_net_cagr_spread=promotion_min_net_cagr_spread,
        promotion_min_liquidity_clean_coverage=promotion_min_liquidity_clean_coverage,
        promotion_max_underperformance_share=promotion_max_underperformance_share,
        promotion_min_worst_rolling_excess_return=promotion_min_worst_rolling_excess_return,
        promotion_max_strategy_drawdown=promotion_max_strategy_drawdown,
        promotion_max_drawdown_gap_vs_benchmark=promotion_max_drawdown_gap_vs_benchmark,
    )


def run_value_snapshot_strict_quarterly_prototype_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    value_factors: Sequence[str] | None = None,
    top_n: int = 10,
    rebalance_interval: int = 1,
    trend_filter_enabled: bool = False,
    trend_filter_window: int = 200,
    market_regime_enabled: bool = False,
    market_regime_window: int = STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    market_regime_benchmark: str = STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    universe_mode: str = "manual_tickers",
    preset_name: str | None = None,
    universe_contract: str = STATIC_MANAGED_RESEARCH_UNIVERSE,
    dynamic_candidate_tickers: Sequence[str] | None = None,
    dynamic_target_size: int | None = None,
) -> dict[str, Any]:
    normalized_tickers = _normalize_tickers(tickers)
    _validate_backtest_date_range(start, end)
    universe_input_tickers = normalized_tickers
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        universe_input_tickers = _normalize_tickers(dynamic_candidate_tickers or normalized_tickers)

    normalized_factors = [
        str(name).strip()
        for name in (value_factors or VALUE_STRICT_DEFAULT_FACTORS)
        if str(name).strip()
    ]
    if not normalized_factors:
        raise BacktestInputError("At least one quarterly value factor must be provided.")

    price_freshness = inspect_strict_annual_price_freshness(
        tickers=universe_input_tickers,
        end=end,
        timeframe=timeframe,
    )

    dynamic_price_pool = None
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        dynamic_price_pool = _inspect_dynamic_universe_price_pool(
            tickers=universe_input_tickers,
            end=end,
            timeframe=timeframe,
        )
    else:
        _preflight_price_strategy_data(
            tickers=universe_input_tickers,
            start=start,
            end=end,
            timeframe=timeframe,
        )
    if market_regime_enabled:
        _preflight_price_strategy_data(
            tickers=[market_regime_benchmark],
            start=start,
            end=end,
            timeframe=timeframe,
        )
    _preflight_statement_quality_shadow_data(
        tickers=universe_input_tickers,
        end=end,
        statement_freq="quarterly",
        factor_names=normalized_factors,
    )

    result_payload = get_statement_value_snapshot_shadow_from_db(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        statement_freq="quarterly",
        value_factors=normalized_factors,
        top_n=top_n,
        rebalance_interval=rebalance_interval,
        trend_filter_enabled=trend_filter_enabled,
        trend_filter_window=trend_filter_window,
        market_regime_enabled=market_regime_enabled,
        market_regime_window=market_regime_window,
        market_regime_benchmark=market_regime_benchmark,
        universe_contract=universe_contract,
        dynamic_candidate_tickers=universe_input_tickers,
        dynamic_target_size=dynamic_target_size,
        return_details=True,
    )
    result_df = result_payload["result_df"]
    universe_debug = result_payload.get("universe_debug")
    dynamic_universe_snapshot_rows = result_payload.get("universe_snapshot_rows") or []
    dynamic_candidate_status_rows = result_payload.get("candidate_status_rows") or []

    warnings = [
        "Research-only quarterly value prototype: ranks quarterly statement shadow value factors and is intended for quarterly family validation rather than public default use.",
    ]
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        warnings.append(_dynamic_universe_warning("quarterly"))
        if dynamic_price_pool and dynamic_price_pool["missing_count"] > 0:
            preview = ", ".join(dynamic_price_pool["missing_symbols"][:15])
            more = ""
            if dynamic_price_pool["missing_count"] > 15:
                more = f" ... (+{dynamic_price_pool['missing_count'] - 15} more)"
            warnings.append(
                "Dynamic candidate pool note: "
                f"{dynamic_price_pool['missing_count']} candidate symbols do not have any DB price history up to the selected end date "
                f"and were naturally excluded from the approximate PIT membership build: {preview}{more}"
            )
    if price_freshness["status"] == "warning":
        warnings.append(
            "Price freshness preflight: "
            + price_freshness["message"]
            + " Wider quarterly prototype runs can degrade in the final month until lagging symbols are refreshed."
        )
    if start:
        active_rows = result_df[result_df["Selected Count"].fillna(0) > 0]
        if not active_rows.empty:
            first_active_date = pd.to_datetime(active_rows.iloc[0]["Date"]).strftime("%Y-%m-%d")
            if first_active_date > start:
                warnings.append(
                    "No usable quarterly statement shadow rows were available at the requested start date. "
                    f"The strategy stayed in cash until `{first_active_date}`."
                )

    bundle = build_backtest_result_bundle(
        result_df,
        strategy_name="Value Snapshot (Strict Quarterly Prototype)",
        strategy_key="value_snapshot_strict_quarterly_prototype",
        input_params={
            "tickers": normalized_tickers,
            "start": start,
            "end": end,
            "timeframe": timeframe,
            "option": option,
            "top": top_n,
            "rebalance_interval": rebalance_interval,
            "factor_freq": "quarterly",
            "value_factors": normalized_factors,
            "trend_filter_enabled": trend_filter_enabled,
            "trend_filter_window": trend_filter_window,
            "market_regime_enabled": market_regime_enabled,
            "market_regime_window": market_regime_window,
            "market_regime_benchmark": market_regime_benchmark,
            "snapshot_mode": "strict_statement_quarterly",
            "snapshot_source": "shadow_factors",
            "universe_mode": universe_mode,
            "preset_name": preset_name,
            "universe_contract": universe_contract,
            "dynamic_target_size": dynamic_target_size,
            "dynamic_candidate_count": len(universe_input_tickers),
            "dynamic_candidate_preview": universe_input_tickers[:20],
            "universe_builder_scope": ("quarterly_first_pass" if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE else None),
            "universe_debug": universe_debug,
        },
        summary_freq=_summary_frequency(option, timeframe),
        data_mode="db_backed_strict_statement_shadow_factors",
        warnings=warnings,
    )
    bundle["meta"]["price_freshness"] = price_freshness
    if trend_filter_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            f"Trend Filter Overlay enabled: month-end selections with `Close < MA{trend_filter_window}` move to cash until the next rebalance."
        ]
    if market_regime_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            f"Market Regime Overlay enabled: month-end selections move fully to cash when `{market_regime_benchmark}` closes below `MA{market_regime_window}`."
        ]
    if dynamic_universe_snapshot_rows:
        bundle["dynamic_universe_snapshot_rows"] = dynamic_universe_snapshot_rows
    if dynamic_candidate_status_rows:
        bundle["dynamic_candidate_status_rows"] = dynamic_candidate_status_rows
    return bundle


def run_quality_value_snapshot_strict_annual_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    quality_factors: Sequence[str] | None = None,
    value_factors: Sequence[str] | None = None,
    top_n: int = 10,
    rebalance_interval: int = 1,
    min_price_filter: float = ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
    min_history_months_filter: int = STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
    min_avg_dollar_volume_20d_m_filter: float = STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
    transaction_cost_bps: float = ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
    benchmark_contract: str = STRICT_DEFAULT_BENCHMARK_CONTRACT,
    benchmark_ticker: str = ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    promotion_min_benchmark_coverage: float = STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
    promotion_min_net_cagr_spread: float = STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
    promotion_min_liquidity_clean_coverage: float = STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
    promotion_max_underperformance_share: float = STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
    promotion_min_worst_rolling_excess_return: float = STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
    promotion_max_strategy_drawdown: float = STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
    promotion_max_drawdown_gap_vs_benchmark: float = STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
    trend_filter_enabled: bool = False,
    trend_filter_window: int = 200,
    market_regime_enabled: bool = False,
    market_regime_window: int = STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    market_regime_benchmark: str = STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    underperformance_guardrail_enabled: bool = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    underperformance_guardrail_window_months: int = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    underperformance_guardrail_threshold: float = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    universe_mode: str = "manual_tickers",
    preset_name: str | None = None,
    universe_contract: str = STATIC_MANAGED_RESEARCH_UNIVERSE,
    dynamic_candidate_tickers: Sequence[str] | None = None,
    dynamic_target_size: int | None = None,
) -> dict[str, Any]:
    normalized_tickers = _normalize_tickers(tickers)
    _validate_backtest_date_range(start, end)
    universe_input_tickers = normalized_tickers
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        universe_input_tickers = _normalize_tickers(dynamic_candidate_tickers or normalized_tickers)

    normalized_quality_factors = [
        str(name).strip()
        for name in (quality_factors or QUALITY_STRICT_DEFAULT_FACTORS)
        if str(name).strip()
    ]
    normalized_value_factors = [
        str(name).strip()
        for name in (value_factors or VALUE_STRICT_DEFAULT_FACTORS)
        if str(name).strip()
    ]
    normalized_factor_names: list[str] = []
    for factor_name in [*normalized_quality_factors, *normalized_value_factors]:
        if factor_name and factor_name not in normalized_factor_names:
            normalized_factor_names.append(factor_name)

    if not normalized_factor_names:
        raise BacktestInputError("At least one strict annual quality/value factor must be provided.")

    price_freshness = inspect_strict_annual_price_freshness(
        tickers=universe_input_tickers,
        end=end,
        timeframe=timeframe,
    )

    dynamic_price_pool = None
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        dynamic_price_pool = _inspect_dynamic_universe_price_pool(
            tickers=universe_input_tickers,
            end=end,
            timeframe=timeframe,
        )
    else:
        _preflight_price_strategy_data(
            tickers=universe_input_tickers,
            start=start,
            end=end,
            timeframe=timeframe,
        )
    if market_regime_enabled:
        _preflight_price_strategy_data(
            tickers=[market_regime_benchmark],
            start=start,
            end=end,
            timeframe=timeframe,
        )
    if underperformance_guardrail_enabled and benchmark_ticker:
        _preflight_price_strategy_data(
            tickers=[benchmark_ticker],
            start=start,
            end=end,
            timeframe=timeframe,
        )
    _preflight_statement_quality_shadow_data(
        tickers=universe_input_tickers,
        end=end,
        statement_freq="annual",
        factor_names=normalized_factor_names,
    )

    result_payload = get_statement_quality_value_snapshot_shadow_from_db(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        statement_freq="annual",
        quality_factors=normalized_quality_factors,
        value_factors=normalized_value_factors,
        top_n=top_n,
        rebalance_interval=rebalance_interval,
        min_price=min_price_filter,
        min_history_months=min_history_months_filter,
        min_avg_dollar_volume_20d_m=min_avg_dollar_volume_20d_m_filter,
        trend_filter_enabled=trend_filter_enabled,
        trend_filter_window=trend_filter_window,
        market_regime_enabled=market_regime_enabled,
        market_regime_window=market_regime_window,
        market_regime_benchmark=market_regime_benchmark,
        benchmark_ticker=benchmark_ticker,
        underperformance_guardrail_enabled=underperformance_guardrail_enabled,
        underperformance_guardrail_window_months=underperformance_guardrail_window_months,
        underperformance_guardrail_threshold=underperformance_guardrail_threshold,
        universe_contract=universe_contract,
        dynamic_candidate_tickers=universe_input_tickers,
        dynamic_target_size=dynamic_target_size,
        return_details=True,
    )
    result_df = result_payload["result_df"]
    universe_debug = result_payload.get("universe_debug")
    dynamic_universe_snapshot_rows = result_payload.get("universe_snapshot_rows") or []
    dynamic_candidate_status_rows = result_payload.get("candidate_status_rows") or []

    warnings = [
        "Strict annual multi-factor path: combines coverage-first quality factors with annual statement-driven valuation factors.",
    ]
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        warnings.append(_dynamic_universe_warning("annual"))
        if dynamic_price_pool and dynamic_price_pool["missing_count"] > 0:
            preview = ", ".join(dynamic_price_pool["missing_symbols"][:15])
            more = ""
            if dynamic_price_pool["missing_count"] > 15:
                more = f" ... (+{dynamic_price_pool['missing_count'] - 15} more)"
            warnings.append(
                "Dynamic candidate pool note: "
                f"{dynamic_price_pool['missing_count']} candidate symbols do not have any DB price history up to the selected end date "
                f"and were naturally excluded from the approximate PIT membership build: {preview}{more}"
            )
    if price_freshness["status"] == "warning":
        warnings.append(
            "Price freshness preflight: "
            + price_freshness["message"]
            + " Large-universe strict annual runs can show duplicate or shifted final-month rows until lagging symbols are refreshed."
        )
    if start:
        active_rows = result_df[result_df["Selected Count"].fillna(0) > 0]
        if not active_rows.empty:
            first_active_date = pd.to_datetime(active_rows.iloc[0]["Date"]).strftime("%Y-%m-%d")
            if first_active_date > start:
                warnings.append(
                    "No usable strict annual multi-factor snapshot rows were available at the requested start date. "
                    f"The strategy stayed in cash until `{first_active_date}`."
                )
    if min_history_months_filter:
        warnings.append(
            "Minimum history filter enabled: candidates need at least "
            f"`{int(min_history_months_filter)}M` of DB price history before each rebalance."
        )
    if min_avg_dollar_volume_20d_m_filter:
        warnings.append(
            "Liquidity filter enabled: candidates need at least "
            f"`{float(min_avg_dollar_volume_20d_m_filter):.1f}M` of trailing 20-day average dollar volume "
            "before each rebalance."
        )

    bundle = build_backtest_result_bundle(
        result_df,
        strategy_name="Quality + Value Snapshot (Strict Annual)",
        strategy_key="quality_value_snapshot_strict_annual",
        input_params={
            "tickers": normalized_tickers,
            "start": start,
            "end": end,
            "timeframe": timeframe,
            "option": option,
            "top": top_n,
            "rebalance_interval": rebalance_interval,
            "min_price_filter": min_price_filter,
            "min_history_months_filter": int(min_history_months_filter or 0),
            "min_avg_dollar_volume_20d_m_filter": float(min_avg_dollar_volume_20d_m_filter or 0.0),
            "transaction_cost_bps": transaction_cost_bps,
            "benchmark_contract": benchmark_contract,
            "benchmark_ticker": benchmark_ticker,
            "promotion_min_benchmark_coverage": float(promotion_min_benchmark_coverage),
            "promotion_min_net_cagr_spread": float(promotion_min_net_cagr_spread),
            "promotion_min_liquidity_clean_coverage": float(promotion_min_liquidity_clean_coverage),
            "promotion_max_underperformance_share": float(promotion_max_underperformance_share),
            "promotion_min_worst_rolling_excess_return": float(promotion_min_worst_rolling_excess_return),
            "promotion_max_strategy_drawdown": float(promotion_max_strategy_drawdown),
            "promotion_max_drawdown_gap_vs_benchmark": float(promotion_max_drawdown_gap_vs_benchmark),
            "factor_freq": "annual",
            "quality_factors": normalized_quality_factors,
            "value_factors": normalized_value_factors,
            "trend_filter_enabled": trend_filter_enabled,
            "trend_filter_window": trend_filter_window,
            "market_regime_enabled": market_regime_enabled,
            "market_regime_window": market_regime_window,
            "market_regime_benchmark": market_regime_benchmark,
            "underperformance_guardrail_enabled": underperformance_guardrail_enabled,
            "underperformance_guardrail_window_months": underperformance_guardrail_window_months,
            "underperformance_guardrail_threshold": underperformance_guardrail_threshold,
            "snapshot_mode": "strict_statement_annual",
            "snapshot_source": "shadow_factors",
            "universe_mode": universe_mode,
            "preset_name": preset_name,
            "universe_contract": universe_contract,
            "dynamic_target_size": dynamic_target_size,
            "dynamic_candidate_count": len(universe_input_tickers),
            "dynamic_candidate_preview": universe_input_tickers[:20],
            "universe_builder_scope": ("annual_first_pass" if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE else None),
            "universe_debug": universe_debug,
        },
        summary_freq=_summary_frequency(option, timeframe),
        data_mode="db_backed_strict_statement_shadow_factors",
        warnings=warnings,
    )
    bundle["meta"]["price_freshness"] = price_freshness
    if trend_filter_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            f"Trend Filter Overlay enabled: month-end selections with `Close < MA{trend_filter_window}` move to cash until the next rebalance."
        ]
    if market_regime_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            f"Market Regime Overlay enabled: month-end selections move fully to cash when `{market_regime_benchmark}` closes below `MA{market_regime_window}`."
        ]
    if underperformance_guardrail_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            "Underperformance Guardrail enabled: rebalance candidates move to cash when trailing strategy excess return "
            f"vs `{benchmark_ticker}` over `{underperformance_guardrail_window_months}M` falls below "
            f"`{underperformance_guardrail_threshold:.0%}`."
        ]
    if dynamic_universe_snapshot_rows:
        bundle["dynamic_universe_snapshot_rows"] = dynamic_universe_snapshot_rows
    if dynamic_candidate_status_rows:
        bundle["dynamic_candidate_status_rows"] = dynamic_candidate_status_rows
    return _apply_real_money_hardening(
        bundle,
        summary_freq=_summary_frequency(option, timeframe),
        min_price_filter=min_price_filter,
        transaction_cost_bps=transaction_cost_bps,
        benchmark_contract=benchmark_contract,
        benchmark_ticker=benchmark_ticker,
        benchmark_universe_tickers=universe_input_tickers,
        promotion_min_benchmark_coverage=promotion_min_benchmark_coverage,
        promotion_min_net_cagr_spread=promotion_min_net_cagr_spread,
        promotion_min_liquidity_clean_coverage=promotion_min_liquidity_clean_coverage,
        promotion_max_underperformance_share=promotion_max_underperformance_share,
        promotion_min_worst_rolling_excess_return=promotion_min_worst_rolling_excess_return,
        promotion_max_strategy_drawdown=promotion_max_strategy_drawdown,
        promotion_max_drawdown_gap_vs_benchmark=promotion_max_drawdown_gap_vs_benchmark,
    )


def run_quality_value_snapshot_strict_quarterly_prototype_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    quality_factors: Sequence[str] | None = None,
    value_factors: Sequence[str] | None = None,
    top_n: int = 10,
    rebalance_interval: int = 1,
    trend_filter_enabled: bool = False,
    trend_filter_window: int = 200,
    market_regime_enabled: bool = False,
    market_regime_window: int = STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    market_regime_benchmark: str = STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    universe_mode: str = "manual_tickers",
    preset_name: str | None = None,
    universe_contract: str = STATIC_MANAGED_RESEARCH_UNIVERSE,
    dynamic_candidate_tickers: Sequence[str] | None = None,
    dynamic_target_size: int | None = None,
) -> dict[str, Any]:
    normalized_tickers = _normalize_tickers(tickers)
    _validate_backtest_date_range(start, end)
    universe_input_tickers = normalized_tickers
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        universe_input_tickers = _normalize_tickers(dynamic_candidate_tickers or normalized_tickers)

    normalized_quality_factors = [
        str(name).strip()
        for name in (quality_factors or QUALITY_STRICT_DEFAULT_FACTORS)
        if str(name).strip()
    ]
    normalized_value_factors = [
        str(name).strip()
        for name in (value_factors or VALUE_STRICT_DEFAULT_FACTORS)
        if str(name).strip()
    ]
    normalized_factor_names: list[str] = []
    for factor_name in [*normalized_quality_factors, *normalized_value_factors]:
        if factor_name and factor_name not in normalized_factor_names:
            normalized_factor_names.append(factor_name)

    if not normalized_factor_names:
        raise BacktestInputError("At least one quarterly quality/value factor must be provided.")

    price_freshness = inspect_strict_annual_price_freshness(
        tickers=universe_input_tickers,
        end=end,
        timeframe=timeframe,
    )

    dynamic_price_pool = None
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        dynamic_price_pool = _inspect_dynamic_universe_price_pool(
            tickers=universe_input_tickers,
            end=end,
            timeframe=timeframe,
        )
    else:
        _preflight_price_strategy_data(
            tickers=universe_input_tickers,
            start=start,
            end=end,
            timeframe=timeframe,
        )
    if market_regime_enabled:
        _preflight_price_strategy_data(
            tickers=[market_regime_benchmark],
            start=start,
            end=end,
            timeframe=timeframe,
        )
    _preflight_statement_quality_shadow_data(
        tickers=universe_input_tickers,
        end=end,
        statement_freq="quarterly",
        factor_names=normalized_factor_names,
    )

    result_payload = get_statement_quality_value_snapshot_shadow_from_db(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        statement_freq="quarterly",
        quality_factors=normalized_quality_factors,
        value_factors=normalized_value_factors,
        top_n=top_n,
        rebalance_interval=rebalance_interval,
        trend_filter_enabled=trend_filter_enabled,
        trend_filter_window=trend_filter_window,
        market_regime_enabled=market_regime_enabled,
        market_regime_window=market_regime_window,
        market_regime_benchmark=market_regime_benchmark,
        universe_contract=universe_contract,
        dynamic_candidate_tickers=universe_input_tickers,
        dynamic_target_size=dynamic_target_size,
        return_details=True,
    )
    result_df = result_payload["result_df"]
    universe_debug = result_payload.get("universe_debug")
    dynamic_universe_snapshot_rows = result_payload.get("universe_snapshot_rows") or []
    dynamic_candidate_status_rows = result_payload.get("candidate_status_rows") or []

    warnings = [
        "Research-only quarterly multi-factor prototype: combines quarterly quality and value shadow factors for family-level validation, not public default use.",
    ]
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        warnings.append(_dynamic_universe_warning("quarterly"))
        if dynamic_price_pool and dynamic_price_pool["missing_count"] > 0:
            preview = ", ".join(dynamic_price_pool["missing_symbols"][:15])
            more = ""
            if dynamic_price_pool["missing_count"] > 15:
                more = f" ... (+{dynamic_price_pool['missing_count'] - 15} more)"
            warnings.append(
                "Dynamic candidate pool note: "
                f"{dynamic_price_pool['missing_count']} candidate symbols do not have any DB price history up to the selected end date "
                f"and were naturally excluded from the approximate PIT membership build: {preview}{more}"
            )
    if price_freshness["status"] == "warning":
        warnings.append(
            "Price freshness preflight: "
            + price_freshness["message"]
            + " Wider quarterly prototype runs can degrade in the final month until lagging symbols are refreshed."
        )
    if start:
        active_rows = result_df[result_df["Selected Count"].fillna(0) > 0]
        if not active_rows.empty:
            first_active_date = pd.to_datetime(active_rows.iloc[0]["Date"]).strftime("%Y-%m-%d")
            if first_active_date > start:
                warnings.append(
                    "No usable quarterly multi-factor snapshot rows were available at the requested start date. "
                    f"The strategy stayed in cash until `{first_active_date}`."
                )

    bundle = build_backtest_result_bundle(
        result_df,
        strategy_name="Quality + Value Snapshot (Strict Quarterly Prototype)",
        strategy_key="quality_value_snapshot_strict_quarterly_prototype",
        input_params={
            "tickers": normalized_tickers,
            "start": start,
            "end": end,
            "timeframe": timeframe,
            "option": option,
            "top": top_n,
            "rebalance_interval": rebalance_interval,
            "factor_freq": "quarterly",
            "quality_factors": normalized_quality_factors,
            "value_factors": normalized_value_factors,
            "trend_filter_enabled": trend_filter_enabled,
            "trend_filter_window": trend_filter_window,
            "market_regime_enabled": market_regime_enabled,
            "market_regime_window": market_regime_window,
            "market_regime_benchmark": market_regime_benchmark,
            "snapshot_mode": "strict_statement_quarterly",
            "snapshot_source": "shadow_factors",
            "universe_mode": universe_mode,
            "preset_name": preset_name,
            "universe_contract": universe_contract,
            "dynamic_target_size": dynamic_target_size,
            "dynamic_candidate_count": len(universe_input_tickers),
            "dynamic_candidate_preview": universe_input_tickers[:20],
            "universe_builder_scope": ("quarterly_first_pass" if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE else None),
            "universe_debug": universe_debug,
        },
        summary_freq=_summary_frequency(option, timeframe),
        data_mode="db_backed_strict_statement_shadow_factors",
        warnings=warnings,
    )
    bundle["meta"]["price_freshness"] = price_freshness
    if trend_filter_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            f"Trend Filter Overlay enabled: month-end selections with `Close < MA{trend_filter_window}` move to cash until the next rebalance."
        ]
    if market_regime_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            f"Market Regime Overlay enabled: month-end selections move fully to cash when `{market_regime_benchmark}` closes below `MA{market_regime_window}`."
        ]
    if dynamic_universe_snapshot_rows:
        bundle["dynamic_universe_snapshot_rows"] = dynamic_universe_snapshot_rows
    if dynamic_candidate_status_rows:
        bundle["dynamic_candidate_status_rows"] = dynamic_candidate_status_rows
    return bundle


def run_quality_snapshot_strict_quarterly_prototype_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    quality_factors: Sequence[str] | None = None,
    top_n: int = 2,
    rebalance_interval: int = 1,
    trend_filter_enabled: bool = False,
    trend_filter_window: int = 200,
    market_regime_enabled: bool = False,
    market_regime_window: int = STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    market_regime_benchmark: str = STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    universe_mode: str = "manual_tickers",
    preset_name: str | None = None,
    universe_contract: str = STATIC_MANAGED_RESEARCH_UNIVERSE,
    dynamic_candidate_tickers: Sequence[str] | None = None,
    dynamic_target_size: int | None = None,
) -> dict[str, Any]:
    return _run_statement_quality_bundle(
        strategy_name="Quality Snapshot (Strict Quarterly Prototype)",
        strategy_key="quality_snapshot_strict_quarterly_prototype",
        tickers=tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        statement_freq="quarterly",
        quality_factors=quality_factors,
        top_n=top_n,
        rebalance_interval=rebalance_interval,
        trend_filter_enabled=trend_filter_enabled,
        trend_filter_window=trend_filter_window,
        market_regime_enabled=market_regime_enabled,
        market_regime_window=market_regime_window,
        market_regime_benchmark=market_regime_benchmark,
        universe_mode=universe_mode,
        preset_name=preset_name,
        universe_contract=universe_contract,
        dynamic_candidate_tickers=dynamic_candidate_tickers,
        dynamic_target_size=dynamic_target_size,
        snapshot_source="shadow_factors",
        static_warnings=[
            "Research-only quarterly strict prototype: ranks quarterly statement shadow factors and is intended for Phase 6 entry/validation rather than public default use.",
        ],
    )
