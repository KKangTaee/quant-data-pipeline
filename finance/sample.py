"""
Sample and smoke-test entrypoints for the finance package.

Path split:
- legacy direct-fetch functions:
  provider-backed reference samples that read OHLCV directly from yfinance
- `*_from_db` functions:
  DB-backed runtime samples that validate the loader/engine/strategy path
"""

from math import comb
from functools import lru_cache
from IPython.display import display
import pandas as pd
import numpy as np
from .engine import BacktestEngine
from .strategy import (
    EqualWeightStrategy,
    GTAA3Strategy,
    GlobalRelativeStrengthStrategy,
    RiskParityTrendStrategy,
    DualMomentumStrategy,
    quality_snapshot_equal_weight,
)

from .performance import(
    portfolio_performance_summary,
    make_monthly_weighted_portfolio,
)
from .display import round_columns

from .visualize import(
    plot_equity_curves
)
from .transform import align_dfs_by_date_union, align_dfs_to_canonical_period_dates

from finance.data.asset_profile import(
    collect_and_store_asset_profiles,
    load_symbols_from_asset_profile
)
from .loaders import (
    load_asset_profile_status_summary,
    load_factor_snapshot,
    load_price_history,
    load_statement_factor_snapshot_shadow,
    load_statement_factors_shadow,
    load_statement_fundamentals_shadow,
    load_statement_quality_snapshot_strict,
)

from .data.fundamentals import(
    upsert_fundamentals
)

from .data.factors import(
    upsert_factors,
)
from .data.financial_statements import (
    inspect_financial_statement_source,
    upsert_financial_statements,
)

from finance.data.db.schema import sync_table_schema, NYSE_SCHEMAS
from finance.data.db.mysql import MySQLClient

QUALITY_STRICT_DEFAULT_FACTORS = [
    "roe",
    "roa",
    "net_margin",
    "asset_turnover",
    "current_ratio",
]

VALUE_STRICT_DEFAULT_FACTORS = [
    "book_to_market",
    "earnings_yield",
    "sales_yield",
    "ocf_yield",
    "operating_income_yield",
]

STRICT_TREND_FILTER_DEFAULT_ENABLED = False
STRICT_TREND_FILTER_DEFAULT_WINDOW = 200
STRICT_WEIGHTING_MODE_EQUAL = "equal_weight"
STRICT_WEIGHTING_MODE_RANK_TAPERED = "rank_tapered"
STRICT_DEFAULT_WEIGHTING_MODE = STRICT_WEIGHTING_MODE_EQUAL
STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED = False
STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED = False
STRICT_REJECTION_HANDLING_MODE_REWEIGHT = "reweight_survivors"
STRICT_REJECTION_HANDLING_MODE_RETAIN_CASH = "retain_unfilled_as_cash"
STRICT_REJECTION_HANDLING_MODE_FILL_REWEIGHT = "fill_then_reweight"
STRICT_REJECTION_HANDLING_MODE_FILL_RETAIN_CASH = "fill_then_retain_cash"
STRICT_REJECTION_HANDLING_MODE_OPTIONS = (
    STRICT_REJECTION_HANDLING_MODE_REWEIGHT,
    STRICT_REJECTION_HANDLING_MODE_RETAIN_CASH,
    STRICT_REJECTION_HANDLING_MODE_FILL_REWEIGHT,
    STRICT_REJECTION_HANDLING_MODE_FILL_RETAIN_CASH,
)
STRICT_DEFAULT_REJECTION_HANDLING_MODE = STRICT_REJECTION_HANDLING_MODE_REWEIGHT
STRICT_RISK_OFF_MODE_CASH = "cash_only"
STRICT_RISK_OFF_MODE_DEFENSIVE = "defensive_sleeve_preference"
STRICT_DEFAULT_RISK_OFF_MODE = STRICT_RISK_OFF_MODE_CASH
STRICT_DEFAULT_DEFENSIVE_TICKERS = ["BIL", "SHY", "LQD"]
STRICT_MARKET_REGIME_DEFAULT_ENABLED = False
STRICT_MARKET_REGIME_DEFAULT_WINDOW = 200
STRICT_MARKET_REGIME_DEFAULT_BENCHMARK = "SPY"
STRICT_MARKET_REGIME_BENCHMARK_OPTIONS = ["SPY", "QQQ", "VTI", "IWM"]
STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS = 0
STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M = 0.0
STRICT_INVESTABILITY_DEFAULT_LIQUIDITY_LOOKBACK_DAYS = 20
STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED = False
STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS = 12
STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD = -0.10
STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED = False
STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS = 12
STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD = -0.35
STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD = 0.08
STATIC_MANAGED_RESEARCH_UNIVERSE = "static_managed_research"
HISTORICAL_DYNAMIC_PIT_UNIVERSE = "historical_dynamic_pit"
GTAA_DEFAULT_SIGNAL_INTERVAL = 1
GTAA_DEFAULT_SCORE_LOOKBACK_MONTHS = [1, 3, 6, 12]
GTAA_SCORE_RETURN_COLUMNS = tuple(f"{months}MReturn" for months in GTAA_DEFAULT_SCORE_LOOKBACK_MONTHS)
GTAA_DEFAULT_SCORE_WEIGHTS = {
    "1MReturn": 1.0,
    "3MReturn": 1.0,
    "6MReturn": 1.0,
    "12MReturn": 1.0,
}
GTAA_DEFAULT_TREND_FILTER_WINDOW = 200
GTAA_DEFAULT_DEFENSIVE_TICKERS = ["TLT", "IEF", "LQD"]
GTAA_RISK_OFF_MODE_CASH = "cash_only"
GTAA_RISK_OFF_MODE_DEFENSIVE = "defensive_bond_preference"
GTAA_DEFAULT_RISK_OFF_MODE = GTAA_RISK_OFF_MODE_CASH
GTAA_DEFAULT_CRASH_GUARDRAIL_ENABLED = False
GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD = 0.15
GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS = 12
GTAA_DEFAULT_TICKERS = ["SPY", "IWD", "IWM", "IWN", "MTUM", "EFA", "TLT", "IEF", "LQD", "PDBC", "VNQ", "GLD"]
GLOBAL_RELATIVE_STRENGTH_DEFAULT_TICKERS = ["SPY", "EFA", "EEM", "IWM", "VNQ", "GLD", "DBC", "LQD", "HYG", "IEF", "TLT", "TIP"]
GLOBAL_RELATIVE_STRENGTH_DEFAULT_CASH_TICKER = "BIL"
GLOBAL_RELATIVE_STRENGTH_DEFAULT_TOP = 4
GLOBAL_RELATIVE_STRENGTH_DEFAULT_SIGNAL_INTERVAL = 1
GLOBAL_RELATIVE_STRENGTH_DEFAULT_SCORE_LOOKBACK_MONTHS = [1, 3, 6, 12]
GLOBAL_RELATIVE_STRENGTH_SCORE_RETURN_COLUMNS = tuple(
    f"{months}MReturn" for months in GLOBAL_RELATIVE_STRENGTH_DEFAULT_SCORE_LOOKBACK_MONTHS
)
GLOBAL_RELATIVE_STRENGTH_DEFAULT_SCORE_WEIGHTS = {
    "1MReturn": 1.0,
    "3MReturn": 1.0,
    "6MReturn": 1.0,
    "12MReturn": 1.0,
}
GLOBAL_RELATIVE_STRENGTH_DEFAULT_TREND_FILTER_WINDOW = 200


def resolve_strict_rejection_handling_mode(
    rejected_slot_handling_mode: str | None = None,
    *,
    rejected_slot_fill_enabled: bool = STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
    partial_cash_retention_enabled: bool = STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
) -> str:
    normalized_mode = str(rejected_slot_handling_mode or "").strip().lower()
    if normalized_mode in STRICT_REJECTION_HANDLING_MODE_OPTIONS:
        return normalized_mode
    if bool(rejected_slot_fill_enabled) and bool(partial_cash_retention_enabled):
        return STRICT_REJECTION_HANDLING_MODE_FILL_RETAIN_CASH
    if bool(rejected_slot_fill_enabled):
        return STRICT_REJECTION_HANDLING_MODE_FILL_REWEIGHT
    if bool(partial_cash_retention_enabled):
        return STRICT_REJECTION_HANDLING_MODE_RETAIN_CASH
    return STRICT_REJECTION_HANDLING_MODE_REWEIGHT


def strict_rejection_handling_mode_to_flags(
    rejected_slot_handling_mode: str | None = None,
) -> tuple[bool, bool]:
    resolved_mode = resolve_strict_rejection_handling_mode(rejected_slot_handling_mode)
    if resolved_mode == STRICT_REJECTION_HANDLING_MODE_FILL_RETAIN_CASH:
        return True, True
    if resolved_mode == STRICT_REJECTION_HANDLING_MODE_FILL_REWEIGHT:
        return True, False
    if resolved_mode == STRICT_REJECTION_HANDLING_MODE_RETAIN_CASH:
        return False, True
    return False, False


def _score_return_col_from_months(months: int) -> str:
    return f"{int(months)}MReturn"


def _parse_score_months_from_return_col(value: str) -> int | None:
    text = str(value or "").strip()
    if not text.endswith("MReturn"):
        return None
    number_text = text[:-7]
    if not number_text.isdigit():
        return None
    months = int(number_text)
    return months if months > 0 else None


def _normalize_gtaa_score_lookback_months(
    score_lookback_months=None,
    score_return_columns=None,
):
    raw_values = []
    if score_lookback_months is not None:
        raw_values = list(score_lookback_months)
    elif score_return_columns is not None:
        raw_values = list(score_return_columns)
    else:
        raw_values = list(GTAA_DEFAULT_SCORE_LOOKBACK_MONTHS)

    normalized = []
    seen = set()
    for value in raw_values:
        if isinstance(value, str):
            months = _parse_score_months_from_return_col(value)
            if months is None and value.strip().isdigit():
                months = int(value.strip())
        else:
            try:
                months = int(value)
            except (TypeError, ValueError):
                months = None
        if months is None or months <= 0 or months in seen:
            continue
        seen.add(months)
        normalized.append(months)

    return normalized or list(GTAA_DEFAULT_SCORE_LOOKBACK_MONTHS)


def _history_start_with_buffer(start=None, *, years: int = 0, months: int = 0, days: int = 0):
    """
        지표 warmup을 위해 실제 조회 시작일을 더 앞당긴다.
        sample 함수는 마지막에 `.slice(start=...)`를 다시 수행하므로
        여기서는 indicator 계산에 필요한 이력만 확보하면 된다.
    """
    if start is None:
        return None

    ts = pd.to_datetime(start)
    buffered = ts - pd.DateOffset(years=years, months=months, days=days)
    return buffered.strftime("%Y-%m-%d")


def _build_price_only_engine(
    tickers,
    *,
    option="month_end",
    period="15y",
    start=None,
    end=None,
    timeframe="1d",
    from_db=False,
    history_buffer_years=0,
):
    """
        Price-only 전략 sample이 공통으로 사용하는 engine 시작 경로.
        - direct path: provider-backed reference sample
        - DB path: loader/runtime-backed sample
    """
    engine = BacktestEngine(tickers, period=("db" if from_db else period), option=option)

    if from_db:
        history_start = _history_start_with_buffer(start, years=history_buffer_years)
        return engine.load_ohlcv_from_db(
            start=start,
            end=end,
            timeframe=timeframe,
            history_start=history_start,
        )

    return engine.load_ohlcv()


def _build_snapshot_strategy_price_dfs(
    tickers,
    *,
    option="month_end",
    start=None,
    end=None,
    timeframe="1d",
    from_db=False,
    trend_filter_window: int | None = None,
):
    """
    Snapshot 전략용 price input builder.

    price-only ETF 전략과 달리, 대형 주식 유니버스 snapshot 전략은
    모든 심볼의 공통 날짜 교집합을 강제하면 usable history가 극단적으로 줄어들 수 있다.
    따라서 여기서는:
    - period filter는 유지하고
    - 마지막에 union calendar를 만든 뒤
    - period당 canonical date 하나로 다시 정렬
    하는 방식을 사용한다.
    """
    history_buffer_years = 2 if trend_filter_window else 0
    engine = _build_price_only_engine(
        tickers,
        option=option,
        start=start,
        end=end,
        timeframe=timeframe,
        from_db=from_db,
        history_buffer_years=history_buffer_years,
    )

    if trend_filter_window:
        engine = engine.add_ma(trend_filter_window)

    engine = (
        engine.filter_by_period()
        .slice(start=start, end=end)
        .drop_columns(["High", "Low", "Open", "Volume"])
    )

    price_dfs = align_dfs_by_date_union(engine.dfs)
    if option in {"month_start", "month_end", "year_start", "year_end"}:
        price_dfs = align_dfs_to_canonical_period_dates(
            price_dfs,
            option=option,
        )
    if not price_dfs:
        raise ValueError("No DB-backed price data is available for the requested snapshot strategy run.")

    return price_dfs


def _build_market_regime_overlay_df(
    benchmark_ticker: str,
    *,
    option="month_end",
    start=None,
    end=None,
    timeframe="1d",
    from_db=False,
    market_regime_window: int = STRICT_MARKET_REGIME_DEFAULT_WINDOW,
) -> pd.DataFrame:
    benchmark_dfs = _build_snapshot_strategy_price_dfs(
        [benchmark_ticker],
        option=option,
        start=start,
        end=end,
        timeframe=timeframe,
        from_db=from_db,
        trend_filter_window=market_regime_window,
    )
    benchmark_df = next(iter(benchmark_dfs.values())).copy()
    keep_cols = ["Date", "Close", f"MA{market_regime_window}"]
    return benchmark_df[[column for column in keep_cols if column in benchmark_df.columns]].copy()


def _build_underperformance_guardrail_df(
    benchmark_ticker: str,
    *,
    option="month_end",
    start=None,
    end=None,
    timeframe="1d",
    from_db=False,
) -> pd.DataFrame:
    benchmark_dfs = _build_snapshot_strategy_price_dfs(
        [benchmark_ticker],
        option=option,
        start=start,
        end=end,
        timeframe=timeframe,
        from_db=from_db,
    )
    benchmark_df = next(iter(benchmark_dfs.values())).copy()
    keep_cols = ["Date", "Close"]
    return benchmark_df[[column for column in keep_cols if column in benchmark_df.columns]].copy()


def _build_gtaa_risk_overlay_df(
    benchmark_ticker: str,
    *,
    option="month_end",
    start=None,
    end=None,
    timeframe="1d",
    from_db=False,
    market_regime_enabled=False,
    market_regime_window=STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    crash_guardrail_enabled=GTAA_DEFAULT_CRASH_GUARDRAIL_ENABLED,
    crash_guardrail_lookback_months=GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS,
):
    history_buffer_years = max(
        2,
        int(np.ceil(float(max(market_regime_window, 1)) / 252.0)) + 1 if market_regime_enabled else 2,
        int(np.ceil(float(max(crash_guardrail_lookback_months, 1)) / 12.0)) + 1 if crash_guardrail_enabled else 2,
    )

    engine = _build_price_only_engine(
        [benchmark_ticker],
        option=option,
        start=start,
        end=end,
        timeframe=timeframe,
        from_db=from_db,
        history_buffer_years=history_buffer_years,
    )
    if market_regime_enabled:
        engine = engine.add_ma(market_regime_window)

    engine = (
        engine.filter_by_period()
        .slice(start=start, end=end)
        .drop_columns(["High", "Low", "Open", "Volume"])
    )

    benchmark_df = next(iter(engine.dfs.values())).copy()
    keep_cols = ["Date", "Close"]
    if market_regime_enabled:
        keep_cols.append(f"MA{market_regime_window}")

    overlay_df = benchmark_df[[column for column in keep_cols if column in benchmark_df.columns]].copy()
    if crash_guardrail_enabled:
        overlay_df["Crash Rolling Peak"] = (
            pd.to_numeric(overlay_df["Close"], errors="coerce")
            .rolling(window=max(int(crash_guardrail_lookback_months), 1), min_periods=1)
            .max()
        )
        overlay_df["Crash Drawdown"] = (
            pd.to_numeric(overlay_df["Close"], errors="coerce") / overlay_df["Crash Rolling Peak"]
        ) - 1.0

    return overlay_df.reset_index(drop=True)

def get_equal_weight(period="15y", option="month_end", interval=12, start=None):
    """
        Legacy direct-fetch sample.
        외부 provider(yfinance) 기준 reference 예시로 유지한다.
    """
    tickers = ['VIG','SCHD','DGRO','GLD']
    engine = (
        _build_price_only_engine(
            tickers,
            option=option,
            period=period,
        )
        .filter_by_period()
        .align_dates()
        .slice(start=start)
        .drop_columns(["High","Low","Open","Volume"])
    )
    
    strategy = EqualWeightStrategy(
        start_balance=10000,
        rebalance_interval=interval
    )

    df = engine.run(strategy).round_columns().round_columns(cols=["Return", "Total Return"], decimals=3).result
    return df


def get_equal_weight_from_db(
    option="month_end",
    interval=12,
    start=None,
    end=None,
    timeframe="1d",
    tickers=None,
):
    """
        DB-backed runtime sample.
        MySQL price history와 loader/engine 경로를 검증하는 기준 예시다.
    """
    if tickers is None:
        tickers = ['VIG', 'SCHD', 'DGRO', 'GLD']

    engine = (
        _build_price_only_engine(
            tickers,
            option=option,
            start=start,
            end=end,
            timeframe=timeframe,
            from_db=True,
        )
        .filter_by_period()
        .align_dates()
        .slice(start=start, end=end)
        .drop_columns(["High","Low","Open","Volume"])
    )

    strategy = EqualWeightStrategy(
        start_balance=10000,
        rebalance_interval=interval
    )

    df = engine.run(strategy).round_columns().round_columns(cols=["Return", "Total Return"], decimals=3).result
    return df


def get_gtaa3(
    period="15y",
    option="month_end",
    top=3,
    interval=GTAA_DEFAULT_SIGNAL_INTERVAL,
    start=None,
    score_lookback_months=None,
    score_return_columns=None,
    score_weights=None,
    trend_filter_window=GTAA_DEFAULT_TREND_FILTER_WINDOW,
    risk_off_mode=GTAA_DEFAULT_RISK_OFF_MODE,
    defensive_tickers=None,
    market_regime_enabled=False,
    market_regime_window=STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    market_regime_benchmark=STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    crash_guardrail_enabled=GTAA_DEFAULT_CRASH_GUARDRAIL_ENABLED,
    crash_guardrail_drawdown_threshold=GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD,
    crash_guardrail_lookback_months=GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS,
):
    """
        Legacy direct-fetch sample.
    """
    tickers = GTAA_DEFAULT_TICKERS
    effective_score_lookback_months = _normalize_gtaa_score_lookback_months(
        score_lookback_months=score_lookback_months,
        score_return_columns=score_return_columns,
    )
    effective_score_return_columns = tuple(
        _score_return_col_from_months(months) for months in effective_score_lookback_months
    )
    effective_score_weights = dict(GTAA_DEFAULT_SCORE_WEIGHTS if score_weights is None else score_weights)
    effective_defensive_tickers = _normalize_symbol_list(
        defensive_tickers if defensive_tickers is not None else GTAA_DEFAULT_DEFENSIVE_TICKERS
    )

    engine = (
        _build_price_only_engine(
            tickers,
            option=option,
            period=period,
        )
        .add_ma(trend_filter_window)
        .filter_by_period()
        .add_interval_returns(effective_score_lookback_months)
        .align_dates()
        .slice(start=start)
        .add_avg_score(return_cols=effective_score_return_columns, weights=effective_score_weights)
        .drop_columns(["High","Low","Open","Volume", *effective_score_return_columns])
        .interval(interval)
    )

    risk_overlay_df = None
    if market_regime_enabled or crash_guardrail_enabled:
        risk_overlay_df = _build_gtaa_risk_overlay_df(
            market_regime_benchmark,
            option=option,
            start=start,
            timeframe="1d",
            from_db=False,
            market_regime_enabled=market_regime_enabled,
            market_regime_window=market_regime_window,
            crash_guardrail_enabled=crash_guardrail_enabled,
            crash_guardrail_lookback_months=crash_guardrail_lookback_months,
        )

    strategy = GTAA3Strategy(
        start_balance=10000,
        top=top,
        filter_ma=f"MA{trend_filter_window}",
        score_col="Avg Score",
        risk_off_mode=risk_off_mode,
        defensive_tickers=effective_defensive_tickers,
        risk_overlay_df=risk_overlay_df,
        market_regime_enabled=market_regime_enabled,
        market_regime_window=market_regime_window,
        market_regime_benchmark=market_regime_benchmark,
        crash_guardrail_enabled=crash_guardrail_enabled,
        crash_guardrail_drawdown_threshold=crash_guardrail_drawdown_threshold,
    )

    df = engine.run(strategy).round_columns().round_columns(cols=["Return", "Total Return"], decimals=3).result
    return df


def get_gtaa3_from_db(
    option="month_end",
    top=3,
    interval=GTAA_DEFAULT_SIGNAL_INTERVAL,
    min_price=0.0,
    score_lookback_months=None,
    score_return_columns=None,
    score_weights=None,
    trend_filter_window=GTAA_DEFAULT_TREND_FILTER_WINDOW,
    risk_off_mode=GTAA_DEFAULT_RISK_OFF_MODE,
    defensive_tickers=None,
    market_regime_enabled=False,
    market_regime_window=STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    market_regime_benchmark=STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    crash_guardrail_enabled=GTAA_DEFAULT_CRASH_GUARDRAIL_ENABLED,
    crash_guardrail_drawdown_threshold=GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD,
    crash_guardrail_lookback_months=GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS,
    benchmark_ticker=STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    underperformance_guardrail_enabled=STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    underperformance_guardrail_window_months=STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    underperformance_guardrail_threshold=STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    drawdown_guardrail_enabled=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
    drawdown_guardrail_window_months=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    drawdown_guardrail_strategy_threshold=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
    drawdown_guardrail_gap_threshold=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
    start=None,
    end=None,
    timeframe="1d",
    tickers=None,
):
    if tickers is None:
        tickers = GTAA_DEFAULT_TICKERS
    benchmark_ticker = str(benchmark_ticker or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK).strip().upper()
    effective_score_lookback_months = _normalize_gtaa_score_lookback_months(
        score_lookback_months=score_lookback_months,
        score_return_columns=score_return_columns,
    )
    effective_score_return_columns = tuple(
        _score_return_col_from_months(months) for months in effective_score_lookback_months
    )
    effective_score_weights = dict(GTAA_DEFAULT_SCORE_WEIGHTS if score_weights is None else score_weights)
    effective_defensive_tickers = _normalize_symbol_list(
        defensive_tickers if defensive_tickers is not None else GTAA_DEFAULT_DEFENSIVE_TICKERS
    )

    engine = (
        _build_price_only_engine(
            tickers,
            option=option,
            start=start,
            end=end,
            timeframe=timeframe,
            from_db=True,
            history_buffer_years=3,
        )
        .add_ma(trend_filter_window)
        .filter_by_period()
        .add_interval_returns(effective_score_lookback_months)
        .align_dates()
        .slice(start=start, end=end)
        .add_avg_score(return_cols=effective_score_return_columns, weights=effective_score_weights)
        .drop_columns(["High","Low","Open","Volume", *effective_score_return_columns])
        .interval(interval)
    )

    risk_overlay_df = None
    if market_regime_enabled or crash_guardrail_enabled:
        risk_overlay_df = _build_gtaa_risk_overlay_df(
            market_regime_benchmark,
            option=option,
            start=start,
            end=end,
            timeframe=timeframe,
            from_db=True,
            market_regime_enabled=market_regime_enabled,
            market_regime_window=market_regime_window,
            crash_guardrail_enabled=crash_guardrail_enabled,
            crash_guardrail_lookback_months=crash_guardrail_lookback_months,
        )

    guardrail_benchmark_df = None
    if underperformance_guardrail_enabled or drawdown_guardrail_enabled:
        guardrail_benchmark_df = _build_underperformance_guardrail_df(
            benchmark_ticker,
            option=option,
            start=start,
            end=end,
            timeframe=timeframe,
            from_db=True,
        )

    strategy = GTAA3Strategy(
        start_balance=10000,
        top=top,
        filter_ma=f"MA{trend_filter_window}",
        min_price=min_price,
        score_col="Avg Score",
        risk_off_mode=risk_off_mode,
        defensive_tickers=effective_defensive_tickers,
        risk_overlay_df=risk_overlay_df,
        market_regime_enabled=market_regime_enabled,
        market_regime_window=market_regime_window,
        market_regime_benchmark=market_regime_benchmark,
        crash_guardrail_enabled=crash_guardrail_enabled,
        crash_guardrail_drawdown_threshold=crash_guardrail_drawdown_threshold,
        underperformance_guardrail_enabled=underperformance_guardrail_enabled,
        underperformance_guardrail_window_months=underperformance_guardrail_window_months,
        underperformance_guardrail_threshold=underperformance_guardrail_threshold,
        underperformance_guardrail_benchmark=benchmark_ticker,
        underperformance_guardrail_df=guardrail_benchmark_df if underperformance_guardrail_enabled else None,
        drawdown_guardrail_enabled=drawdown_guardrail_enabled,
        drawdown_guardrail_window_months=drawdown_guardrail_window_months,
        drawdown_guardrail_strategy_threshold=drawdown_guardrail_strategy_threshold,
        drawdown_guardrail_gap_threshold=drawdown_guardrail_gap_threshold,
        drawdown_guardrail_benchmark=benchmark_ticker,
        drawdown_guardrail_df=guardrail_benchmark_df if drawdown_guardrail_enabled else None,
    )

    df = engine.run(strategy).round_columns().round_columns(cols=["Return", "Total Return"], decimals=3).result
    return df


def get_global_relative_strength_from_db(
    option="month_end",
    top=GLOBAL_RELATIVE_STRENGTH_DEFAULT_TOP,
    interval=GLOBAL_RELATIVE_STRENGTH_DEFAULT_SIGNAL_INTERVAL,
    min_price=0.0,
    score_lookback_months=None,
    score_return_columns=None,
    score_weights=None,
    trend_filter_window=GLOBAL_RELATIVE_STRENGTH_DEFAULT_TREND_FILTER_WINDOW,
    cash_ticker=GLOBAL_RELATIVE_STRENGTH_DEFAULT_CASH_TICKER,
    start=None,
    end=None,
    timeframe="1d",
    tickers=None,
):
    if tickers is None:
        tickers = GLOBAL_RELATIVE_STRENGTH_DEFAULT_TICKERS

    risky_tickers = _normalize_symbol_list(tickers)
    effective_cash_ticker = str(cash_ticker or "").strip().upper() or None
    engine_tickers = list(risky_tickers)
    if effective_cash_ticker and effective_cash_ticker not in engine_tickers:
        engine_tickers.append(effective_cash_ticker)

    effective_score_lookback_months = _normalize_gtaa_score_lookback_months(
        score_lookback_months=score_lookback_months,
        score_return_columns=score_return_columns,
    )
    effective_score_return_columns = tuple(
        _score_return_col_from_months(months) for months in effective_score_lookback_months
    )
    effective_score_weights = (
        {column: 1.0 for column in effective_score_return_columns}
        if score_weights is None
        else dict(score_weights)
    )

    engine = (
        _build_price_only_engine(
            engine_tickers,
            option=option,
            start=start,
            end=end,
            timeframe=timeframe,
            from_db=True,
            history_buffer_years=3,
        )
        .add_ma(trend_filter_window)
        .filter_by_period()
        .add_interval_returns(effective_score_lookback_months)
    )
    engine.dfs, excluded_tickers = _filter_global_relative_strength_usable_dfs(
        engine.dfs,
        risky_tickers=risky_tickers,
        cash_ticker=effective_cash_ticker,
    )
    engine = (
        engine.align_dates()
        .slice(start=start, end=end)
        .add_avg_score(return_cols=effective_score_return_columns, weights=effective_score_weights)
        .drop_columns(["High", "Low", "Open", "Volume", *effective_score_return_columns])
        .interval(interval)
    )

    strategy = GlobalRelativeStrengthStrategy(
        start_balance=10000,
        top=top,
        score_col="Avg Score",
        filter_ma=f"MA{trend_filter_window}",
        rebalance_interval=interval,
        cash_ticker=effective_cash_ticker,
        min_price=min_price,
    )

    df = (
        engine.run(strategy)
        .round_columns(cols=["Cash", "Total Balance", "End Balance", "Next Balance"], decimals=1)
        .round_columns(cols=["Total Return"], decimals=3)
        .result
    )
    effective_tickers = [ticker for ticker in risky_tickers if ticker in engine.dfs]
    df.attrs["requested_tickers"] = list(risky_tickers)
    df.attrs["effective_tickers"] = effective_tickers
    df.attrs["excluded_tickers"] = excluded_tickers
    return df


def get_risk_parity_trend(period="15y", option="month_end", rebalance_interval=1, vol_window=6, start=None):
    """
        Legacy direct-fetch sample.
    """
    tickers = ['SPY','TLT','GLD','IEF','LQD']  # 예시

    engine = (
        _build_price_only_engine(
            tickers,
            option=option,
            period=period,
        )
        .add_ma(200)              # ✅ filter_ma="MA200"을 쓰기 위함
        .filter_by_period()
        .align_dates()
        .slice(start=start)
        .drop_columns(["High","Low","Open","Volume"])
    )

    strategy = RiskParityTrendStrategy(
        start_balance=10000,
        rebalance_interval=rebalance_interval,  # 월말 데이터면 1=매월 리밸런싱
        vol_window=vol_window,                  # 최근 n개월 변동성
        filter_ma="MA200",
    )

    df = engine.run(strategy).round_columns(
        cols=["Cash","Total Balance","End Balance","Next Balance"],
        decimals=1
    ).result

    return df


def get_risk_parity_trend_from_db(
    option="month_end",
    rebalance_interval=1,
    vol_window=6,
    min_price=0.0,
    benchmark_ticker=STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    underperformance_guardrail_enabled=STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    underperformance_guardrail_window_months=STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    underperformance_guardrail_threshold=STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    drawdown_guardrail_enabled=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
    drawdown_guardrail_window_months=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    drawdown_guardrail_strategy_threshold=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
    drawdown_guardrail_gap_threshold=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
    start=None,
    end=None,
    timeframe="1d",
    tickers=None,
):
    if tickers is None:
        tickers = ['SPY','TLT','GLD','IEF','LQD']
    benchmark_ticker = str(benchmark_ticker or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK).strip().upper()

    engine = (
        _build_price_only_engine(
            tickers,
            option=option,
            start=start,
            end=end,
            timeframe=timeframe,
            from_db=True,
            history_buffer_years=2,
        )
        .add_ma(200)
        .filter_by_period()
        .align_dates()
        .slice(start=start, end=end)
        .drop_columns(["High","Low","Open","Volume"])
    )

    guardrail_benchmark_df = None
    if underperformance_guardrail_enabled or drawdown_guardrail_enabled:
        guardrail_benchmark_df = _build_underperformance_guardrail_df(
            benchmark_ticker,
            option=option,
            start=start,
            end=end,
            timeframe=timeframe,
            from_db=True,
        )

    strategy = RiskParityTrendStrategy(
        start_balance=10000,
        rebalance_interval=rebalance_interval,
        vol_window=vol_window,
        filter_ma="MA200",
        min_price=min_price,
        underperformance_guardrail_enabled=underperformance_guardrail_enabled,
        underperformance_guardrail_window_months=underperformance_guardrail_window_months,
        underperformance_guardrail_threshold=underperformance_guardrail_threshold,
        underperformance_guardrail_benchmark=benchmark_ticker,
        underperformance_guardrail_df=guardrail_benchmark_df if underperformance_guardrail_enabled else None,
        drawdown_guardrail_enabled=drawdown_guardrail_enabled,
        drawdown_guardrail_window_months=drawdown_guardrail_window_months,
        drawdown_guardrail_strategy_threshold=drawdown_guardrail_strategy_threshold,
        drawdown_guardrail_gap_threshold=drawdown_guardrail_gap_threshold,
        drawdown_guardrail_benchmark=benchmark_ticker,
        drawdown_guardrail_df=guardrail_benchmark_df if drawdown_guardrail_enabled else None,
    )

    df = engine.run(strategy).round_columns(
        cols=["Cash","Total Balance","End Balance","Next Balance"],
        decimals=1
    ).result

    return df


def get_dual_momentum(period="15y", option="month_end", top=1, rebalance_interval=1, start=None):
    """
        Legacy direct-fetch sample.
    """
    tickers = ["QQQ", "SPY", "IWM", "SOXX", "BIL"]

    engine = (
        _build_price_only_engine(
            tickers,
            option=option,
            period=period,
        )
        .add_ma(200)
        .filter_by_period()
        .add_interval_returns([12])   # ✅ 12MReturn 생성
        .align_dates()
        .slice(start=start)
        .drop_columns(["High","Low","Open","Volume"])
    )

    strategy = DualMomentumStrategy(
        start_balance=10000,
        top=top,                  # ✅ 가장 강한 n개에 집중
        lookback_col="12MReturn",
        filter_ma="MA200",
        rebalance_interval=rebalance_interval,  # 월 1회 리밸런싱(월말 데이터 기준)
        cash_ticker="BIL",         # ✅ 현금이 아니라 단기채로 현금 수익 반영
    )

    df = engine.run(strategy).round_columns().round_columns(cols=["Total Return"], decimals=3).result
    return df


def get_dual_momentum_from_db(
    option="month_end",
    top=1,
    rebalance_interval=1,
    min_price=0.0,
    benchmark_ticker=STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    underperformance_guardrail_enabled=STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    underperformance_guardrail_window_months=STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    underperformance_guardrail_threshold=STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    drawdown_guardrail_enabled=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
    drawdown_guardrail_window_months=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    drawdown_guardrail_strategy_threshold=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
    drawdown_guardrail_gap_threshold=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
    start=None,
    end=None,
    timeframe="1d",
    tickers=None,
):
    if tickers is None:
        tickers = ["QQQ", "SPY", "IWM", "SOXX", "BIL"]
    benchmark_ticker = str(benchmark_ticker or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK).strip().upper()

    engine = (
        _build_price_only_engine(
            tickers,
            option=option,
            start=start,
            end=end,
            timeframe=timeframe,
            from_db=True,
            history_buffer_years=3,
        )
        .add_ma(200)
        .filter_by_period()
        .add_interval_returns([12])
        .align_dates()
        .slice(start=start, end=end)
        .drop_columns(["High","Low","Open","Volume"])
    )

    guardrail_benchmark_df = None
    if underperformance_guardrail_enabled or drawdown_guardrail_enabled:
        guardrail_benchmark_df = _build_underperformance_guardrail_df(
            benchmark_ticker,
            option=option,
            start=start,
            end=end,
            timeframe=timeframe,
            from_db=True,
        )

    strategy = DualMomentumStrategy(
        start_balance=10000,
        top=top,
        lookback_col="12MReturn",
        filter_ma="MA200",
        rebalance_interval=rebalance_interval,
        cash_ticker="BIL",
        min_price=min_price,
        underperformance_guardrail_enabled=underperformance_guardrail_enabled,
        underperformance_guardrail_window_months=underperformance_guardrail_window_months,
        underperformance_guardrail_threshold=underperformance_guardrail_threshold,
        underperformance_guardrail_benchmark=benchmark_ticker,
        underperformance_guardrail_df=guardrail_benchmark_df if underperformance_guardrail_enabled else None,
        drawdown_guardrail_enabled=drawdown_guardrail_enabled,
        drawdown_guardrail_window_months=drawdown_guardrail_window_months,
        drawdown_guardrail_strategy_threshold=drawdown_guardrail_strategy_threshold,
        drawdown_guardrail_gap_threshold=drawdown_guardrail_gap_threshold,
        drawdown_guardrail_benchmark=benchmark_ticker,
        drawdown_guardrail_df=guardrail_benchmark_df if drawdown_guardrail_enabled else None,
    )

    df = engine.run(strategy).round_columns().round_columns(cols=["Total Return"], decimals=3).result
    return df


def get_quality_snapshot_from_db(
    *,
    start=None,
    end=None,
    timeframe="1d",
    option="month_end",
    tickers=None,
    factor_freq="annual",
    quality_factors=None,
    top_n=2,
    rebalance_interval=1,
    snapshot_mode="broad_research",
):
    if snapshot_mode != "broad_research":
        raise ValueError("first-pass quality snapshot sample currently supports only 'broad_research' mode.")

    if tickers is None:
        tickers = ["AAPL", "MSFT", "GOOG"]
    if quality_factors is None:
        quality_factors = ["roe", "gross_margin", "operating_margin", "debt_ratio"]

    price_dfs = _build_snapshot_strategy_price_dfs(
        tickers,
        option=option,
        start=start,
        end=end,
        timeframe=timeframe,
        from_db=True,
    )

    rebalance_dates = pd.to_datetime(next(iter(price_dfs.values()))["Date"]).tolist()
    snapshot_by_date = {}
    for rebalance_date in rebalance_dates:
        snapshot = load_factor_snapshot(
            quality_factors,
            symbols=tickers,
            as_of_date=pd.Timestamp(rebalance_date).strftime("%Y-%m-%d"),
            freq=factor_freq,
        )
        snapshot_by_date[pd.Timestamp(rebalance_date).normalize()] = snapshot

    df = quality_snapshot_equal_weight(
        price_dfs,
        snapshot_by_date,
        start_balance=10000,
        quality_factors=quality_factors,
        top_n=top_n,
        lower_is_better_factors=["debt_ratio"],
        rebalance_interval=rebalance_interval,
    )

    df = (
        round_columns(df, cols=["Cash", "Total Balance", "End Balance", "Next Balance"], decimals=1)
        .pipe(round_columns, cols=["Total Return", "Selected Score"], decimals=3)
    )
    return df


def get_statement_quality_snapshot_from_db(
    *,
    start=None,
    end=None,
    timeframe="1d",
    option="month_end",
    tickers=None,
    statement_freq="annual",
    quality_factors=None,
    top_n=2,
    rebalance_interval=1,
):
    """
    strict statement snapshot 기반 quality strategy prototype.

    현재는 sample-universe feasibility 확인용 경로이며,
    public UI 기본 전략이 아니라 statement-driven quality 가능성을 검증하는 목적이다.
    """
    if tickers is None:
        tickers = ["AAPL", "MSFT", "GOOG"]
    if quality_factors is None:
        quality_factors = QUALITY_STRICT_DEFAULT_FACTORS.copy()

    price_dfs = _build_snapshot_strategy_price_dfs(
        tickers,
        option=option,
        start=start,
        end=end,
        timeframe=timeframe,
        from_db=True,
    )

    rebalance_dates = pd.to_datetime(next(iter(price_dfs.values()))["Date"]).tolist()
    snapshot_by_date = {}
    for rebalance_date in rebalance_dates:
        quality_snapshot = load_statement_quality_snapshot_strict(
            quality_factors,
            symbols=tickers,
            as_of_date=pd.Timestamp(rebalance_date).strftime("%Y-%m-%d"),
            freq=statement_freq,
        )
        snapshot_by_date[pd.Timestamp(rebalance_date).normalize()] = quality_snapshot

    df = quality_snapshot_equal_weight(
        price_dfs,
        snapshot_by_date,
        start_balance=10000,
        quality_factors=quality_factors,
        top_n=top_n,
        lower_is_better_factors=["debt_ratio", "debt_to_assets", "net_debt_to_equity"],
        rebalance_interval=rebalance_interval,
    )

    df = (
        round_columns(df, cols=["Cash", "Total Balance", "End Balance", "Next Balance"], decimals=1)
        .pipe(round_columns, cols=["Total Return", "Selected Score"], decimals=3)
    )
    return df


def _build_shadow_factor_snapshot_map(
    factor_history: pd.DataFrame,
    *,
    rebalance_dates: list[pd.Timestamp],
    factor_names: list[str],
) -> dict[pd.Timestamp, pd.DataFrame]:
    if factor_history is None or factor_history.empty:
        return {pd.Timestamp(d).normalize(): pd.DataFrame() for d in rebalance_dates}

    working = factor_history.copy()
    working["symbol"] = working["symbol"].astype(str).str.upper()
    working["period_end"] = pd.to_datetime(working["period_end"], errors="coerce")
    working["fundamental_available_at"] = pd.to_datetime(
        working["fundamental_available_at"], errors="coerce"
    )
    if "fundamental_accession_no" in working.columns:
        working["fundamental_accession_no"] = (
            working["fundamental_accession_no"].fillna("").astype(str)
        )

    working = working[
        working["symbol"].notna()
        & working["period_end"].notna()
        & working["fundamental_available_at"].notna()
    ].copy()
    if working.empty:
        return {pd.Timestamp(d).normalize(): pd.DataFrame() for d in rebalance_dates}

    sort_cols = ["symbol", "fundamental_available_at", "period_end", "fundamental_accession_no"]
    working = working.sort_values(sort_cols)
    keep_cols = [
        "symbol",
        "freq",
        "period_end",
        "fundamental_available_at",
    ] + [name for name in factor_names if name in working.columns]

    snapshot_by_date: dict[pd.Timestamp, pd.DataFrame] = {}
    for rebalance_date in rebalance_dates:
        as_of_ts = pd.Timestamp(rebalance_date)
        eligible = working[working["fundamental_available_at"] <= as_of_ts]
        if eligible.empty:
            snapshot_by_date[as_of_ts.normalize()] = pd.DataFrame(columns=keep_cols + ["as_of_date"])
            continue

        snapshot = eligible.groupby("symbol", as_index=False).tail(1).reset_index(drop=True)
        snapshot = snapshot[keep_cols].copy()
        snapshot["as_of_date"] = as_of_ts.normalize()
        snapshot_by_date[as_of_ts.normalize()] = snapshot

    return snapshot_by_date


def _normalize_symbol_list(symbols) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for raw in symbols or []:
        symbol = str(raw).strip().upper()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        normalized.append(symbol)
    return normalized


def _filter_global_relative_strength_usable_dfs(
    dfs: dict[str, pd.DataFrame],
    *,
    risky_tickers: list[str],
    cash_ticker: str | None,
) -> tuple[dict[str, pd.DataFrame], list[str]]:
    """
    Keep Global Relative Strength from failing on tickers that cannot produce
    MA/relative-strength inputs for the selected DB window.

    Risky assets with empty transformed data are excluded and surfaced through
    result metadata. The cash proxy is not silently excluded because cash return
    handling depends on it explicitly.
    """
    filtered: dict[str, pd.DataFrame] = {}
    excluded_tickers: list[str] = []
    cash_symbol = str(cash_ticker or "").strip().upper() or None

    for ticker, df in dfs.items():
        symbol = str(ticker).strip().upper()
        if df is None or df.empty:
            if cash_symbol and symbol == cash_symbol:
                raise ValueError(
                    f"Global Relative Strength cash ticker `{symbol}` has insufficient price history "
                    "after MA/relative-strength warmup. Refresh DB price data or choose another cash ticker."
                )
            excluded_tickers.append(symbol)
            continue
        filtered[symbol] = df

    effective_risky_tickers = [ticker for ticker in risky_tickers if ticker in filtered]
    if not effective_risky_tickers:
        raise ValueError(
            "Global Relative Strength has no usable risky tickers after MA/relative-strength warmup. "
            "Refresh DB price data or choose a universe with enough historical coverage."
        )

    required_tickers = list(effective_risky_tickers)
    if cash_symbol:
        required_tickers.append(cash_symbol)
    missing_required = [ticker for ticker in required_tickers if ticker not in filtered]
    if missing_required:
        raise ValueError(
            "Global Relative Strength is missing required transformed price data for: "
            + ", ".join(missing_required)
        )

    date_sets = []
    coverage_rows = []
    for ticker in required_tickers:
        ticker_df = filtered[ticker]
        dates = pd.to_datetime(ticker_df["Date"], errors="coerce").dropna()
        date_sets.append(set(dates.tolist()))
        coverage_rows.append(
            f"{ticker}={len(dates)} rows"
        )

    common_dates = set.intersection(*date_sets) if date_sets else set()
    if not common_dates:
        raise ValueError(
            "Global Relative Strength cannot find common rebalance dates after MA/relative-strength warmup. "
            "Coverage: "
            + ", ".join(coverage_rows)
        )

    return filtered, excluded_tickers


def _clone_price_df_map(price_dfs: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    return {symbol: df.copy(deep=True) for symbol, df in price_dfs.items()}


@lru_cache(maxsize=12)
def _cached_snapshot_strategy_price_dfs(
    symbols_key: tuple[str, ...],
    option: str,
    start: str | None,
    end: str | None,
    timeframe: str,
    trend_filter_window: int | None,
) -> dict[str, pd.DataFrame]:
    return _build_snapshot_strategy_price_dfs(
        list(symbols_key),
        option=option,
        start=start,
        end=end,
        timeframe=timeframe,
        from_db=True,
        trend_filter_window=trend_filter_window,
    )


def _get_cached_snapshot_strategy_price_dfs(
    *,
    symbols,
    option: str,
    start: str | None,
    end: str | None,
    timeframe: str,
    trend_filter_window: int | None,
) -> dict[str, pd.DataFrame]:
    symbols_key = tuple(_normalize_symbol_list(symbols))
    return _clone_price_df_map(
        _cached_snapshot_strategy_price_dfs(
            symbols_key,
            option,
            start,
            end,
            timeframe,
            trend_filter_window,
        )
    )


@lru_cache(maxsize=12)
def _cached_snapshot_strategy_price_first_dates(
    symbols_key: tuple[str, ...],
    option: str,
    start: str | None,
    end: str | None,
    timeframe: str,
    trend_filter_window: int | None,
    min_history_months: int,
) -> dict[str, pd.Timestamp | None]:
    history_buffer_years = max(
        2 if trend_filter_window else 0,
        int(np.ceil(float(max(min_history_months, 0)) / 12.0)),
    )
    engine = _build_price_only_engine(
        list(symbols_key),
        option=option,
        start=start,
        end=end,
        timeframe=timeframe,
        from_db=True,
        history_buffer_years=history_buffer_years,
    )
    if trend_filter_window:
        engine = engine.add_ma(trend_filter_window)

    engine = engine.filter_by_period()
    first_dates: dict[str, pd.Timestamp | None] = {}
    for symbol, df in engine.dfs.items():
        working = df.copy()
        working["Date"] = pd.to_datetime(working["Date"], errors="coerce")
        working["Close"] = pd.to_numeric(working.get("Close"), errors="coerce")
        valid = working.dropna(subset=["Date", "Close"])
        first_dates[str(symbol).strip().upper()] = (
            pd.Timestamp(valid["Date"].iloc[0]).normalize() if not valid.empty else None
        )
    return first_dates


def _get_cached_snapshot_strategy_price_first_dates(
    *,
    symbols,
    option: str,
    start: str | None,
    end: str | None,
    timeframe: str,
    trend_filter_window: int | None,
    min_history_months: int,
) -> dict[str, pd.Timestamp | None]:
    symbols_key = tuple(_normalize_symbol_list(symbols))
    return dict(
        _cached_snapshot_strategy_price_first_dates(
            symbols_key,
            option,
            start,
            end,
            timeframe,
            trend_filter_window,
            int(min_history_months),
        )
    )


@lru_cache(maxsize=12)
def _cached_snapshot_strategy_avg_dollar_volume_20d(
    symbols_key: tuple[str, ...],
    start: str | None,
    end: str | None,
    timeframe: str,
    lookback_days: int,
) -> dict[str, dict[pd.Timestamp, float]]:
    if lookback_days <= 0:
        return {}

    history_start = _history_start_with_buffer(
        start,
        days=max(int(lookback_days) * 5, 60),
    )
    history = load_price_history(
        symbols=list(symbols_key),
        start=history_start,
        end=end,
        timeframe=timeframe,
    )
    if history.empty:
        return {}

    working = history.copy()
    working["symbol"] = working["symbol"].astype(str).str.strip().str.upper()
    working["date"] = pd.to_datetime(working["date"], errors="coerce")
    working["close"] = pd.to_numeric(working["close"], errors="coerce")
    working["volume"] = pd.to_numeric(working["volume"], errors="coerce")
    working = working.dropna(subset=["symbol", "date", "close", "volume"]).sort_values(["symbol", "date"])
    if working.empty:
        return {}

    result: dict[str, dict[pd.Timestamp, float]] = {}
    for symbol, group in working.groupby("symbol", sort=False):
        symbol_df = group[["date", "close", "volume"]].copy()
        symbol_df["dollar_volume"] = symbol_df["close"] * symbol_df["volume"]
        symbol_df["avg_dollar_volume_20d"] = (
            symbol_df["dollar_volume"]
            .rolling(window=int(lookback_days), min_periods=int(lookback_days))
            .mean()
        )
        valid = symbol_df.dropna(subset=["avg_dollar_volume_20d"])
        result[str(symbol)] = {
            pd.Timestamp(row["date"]).normalize(): float(row["avg_dollar_volume_20d"])
            for _, row in valid.iterrows()
        }
    return result


def _get_cached_snapshot_strategy_avg_dollar_volume_20d(
    *,
    symbols,
    start: str | None,
    end: str | None,
    timeframe: str,
    lookback_days: int = STRICT_INVESTABILITY_DEFAULT_LIQUIDITY_LOOKBACK_DAYS,
) -> dict[str, dict[pd.Timestamp, float]]:
    symbols_key = tuple(_normalize_symbol_list(symbols))
    cached = _cached_snapshot_strategy_avg_dollar_volume_20d(
        symbols_key,
        start,
        end,
        timeframe,
        int(lookback_days),
    )
    return {
        str(symbol): dict(per_date)
        for symbol, per_date in cached.items()
    }


@lru_cache(maxsize=12)
def _cached_statement_factors_shadow(
    symbols_key: tuple[str, ...],
    freq: str,
    end: str | None,
) -> pd.DataFrame:
    factor_history = load_statement_factors_shadow(
        symbols=list(symbols_key),
        freq=freq,
        end=end,
    )
    if factor_history is None:
        return pd.DataFrame()
    return factor_history.copy(deep=True)


def _get_cached_statement_factors_shadow(
    *,
    symbols,
    freq: str,
    end: str | None,
) -> pd.DataFrame:
    symbols_key = tuple(_normalize_symbol_list(symbols))
    return _cached_statement_factors_shadow(symbols_key, freq, end).copy(deep=True)


@lru_cache(maxsize=12)
def _cached_statement_fundamentals_shadow(
    symbols_key: tuple[str, ...],
    freq: str,
    end: str | None,
) -> pd.DataFrame:
    statement_shadow = load_statement_fundamentals_shadow(
        symbols=list(symbols_key),
        freq=freq,
        end=end,
    )
    if statement_shadow is None:
        return pd.DataFrame()
    return statement_shadow.copy(deep=True)


def _get_cached_statement_fundamentals_shadow(
    *,
    symbols,
    freq: str,
    end: str | None,
) -> pd.DataFrame:
    symbols_key = tuple(_normalize_symbol_list(symbols))
    return _cached_statement_fundamentals_shadow(symbols_key, freq, end).copy(deep=True)


@lru_cache(maxsize=12)
def _cached_asset_profile_status_summary(
    symbols_key: tuple[str, ...],
) -> pd.DataFrame:
    summary = load_asset_profile_status_summary(list(symbols_key))
    if summary is None:
        return pd.DataFrame()
    return summary.copy(deep=True)


def _get_cached_asset_profile_status_summary(
    *,
    symbols,
) -> pd.DataFrame:
    symbols_key = tuple(_normalize_symbol_list(symbols))
    return _cached_asset_profile_status_summary(symbols_key).copy(deep=True)


def _build_dynamic_pit_membership_map(
    *,
    price_dfs: dict[str, pd.DataFrame],
    statement_shadow: pd.DataFrame,
    rebalance_dates: list[pd.Timestamp],
    target_size: int,
    requested_tickers: list[str],
    statement_freq: str = "annual",
    input_candidate_count: int | None = None,
    asset_profile_summary: pd.DataFrame | None = None,
) -> tuple[dict[pd.Timestamp, list[str]], dict[str, object], list[dict[str, object]], list[dict[str, object]]]:
    if target_size <= 0:
        raise ValueError("target_size must be positive for dynamic PIT universe construction.")

    candidate_tickers = _normalize_symbol_list(price_dfs.keys())
    if not candidate_tickers:
        raise ValueError("price_dfs is empty for dynamic PIT universe construction.")

    input_candidate_count = int(input_candidate_count or len(candidate_tickers))

    if statement_shadow is None or statement_shadow.empty:
        empty_map = {pd.Timestamp(date).normalize(): [] for date in rebalance_dates}
        return empty_map, {
            "contract": HISTORICAL_DYNAMIC_PIT_UNIVERSE,
            "statement_freq": statement_freq,
            "requested_count": len(requested_tickers),
            "input_candidate_count": input_candidate_count,
            "candidate_pool_count": len(candidate_tickers),
            "target_size": int(target_size),
            "membership_dates": len(rebalance_dates),
            "first_membership_count": 0,
            "last_membership_count": 0,
            "min_membership_count": 0,
            "max_membership_count": 0,
            "avg_membership_count": 0.0,
            "avg_turnover_count": 0.0,
            "avg_turnover_pct": 0.0,
            "statement_ready_count": 0,
            "per_date_rows": [],
        }, [], []

    price_rows: list[pd.DataFrame] = []
    for symbol, df in price_dfs.items():
        working_price = df[["Date", "Close"]].copy()
        working_price["Date"] = pd.to_datetime(working_price["Date"], errors="coerce").dt.normalize()
        working_price["Close"] = pd.to_numeric(working_price["Close"], errors="coerce")
        working_price["symbol"] = str(symbol).strip().upper()
        price_rows.append(working_price.dropna(subset=["Date", "Close"]))

    price_panel = pd.concat(price_rows, ignore_index=True) if price_rows else pd.DataFrame()
    if price_panel.empty:
        empty_map = {pd.Timestamp(date).normalize(): [] for date in rebalance_dates}
        return empty_map, {
            "contract": HISTORICAL_DYNAMIC_PIT_UNIVERSE,
            "statement_freq": statement_freq,
            "requested_count": len(requested_tickers),
            "input_candidate_count": input_candidate_count,
            "candidate_pool_count": len(candidate_tickers),
            "target_size": int(target_size),
            "membership_dates": len(rebalance_dates),
            "first_membership_count": 0,
            "last_membership_count": 0,
            "min_membership_count": 0,
            "max_membership_count": 0,
            "avg_membership_count": 0.0,
            "avg_turnover_count": 0.0,
            "avg_turnover_pct": 0.0,
            "statement_ready_count": 0,
            "per_date_rows": [],
        }, [], []

    price_by_date = {
        snapshot_date: group[["symbol", "Close"]].copy()
        for snapshot_date, group in price_panel.groupby("Date", sort=True)
    }
    price_window_df = (
        price_panel.groupby("symbol", as_index=False)
        .agg(
            first_price_date=("Date", "min"),
            last_price_date=("Date", "max"),
            price_row_count=("Date", "count"),
        )
        .sort_values("symbol")
        .reset_index(drop=True)
    )
    price_window_map = {
        row["symbol"]: row for row in price_window_df.to_dict(orient="records")
    }

    if asset_profile_summary is None:
        asset_profile_summary = load_asset_profile_status_summary(candidate_tickers)
    profile_map: dict[str, dict[str, object]] = {}
    if asset_profile_summary is not None and not asset_profile_summary.empty:
        profile_df = asset_profile_summary.copy()
        profile_df["symbol"] = profile_df["symbol"].astype(str).str.upper()
        if "delisted_at" in profile_df.columns:
            profile_df["delisted_at"] = pd.to_datetime(profile_df["delisted_at"], errors="coerce")
        profile_map = {
            row["symbol"]: row
            for row in profile_df.to_dict(orient="records")
        }

    candidate_status_rows: list[dict[str, object]] = []
    for symbol in candidate_tickers:
        price_row = price_window_map.get(symbol, {})
        profile_row = profile_map.get(symbol, {})
        first_price_date = pd.to_datetime(price_row.get("first_price_date"), errors="coerce")
        last_price_date = pd.to_datetime(price_row.get("last_price_date"), errors="coerce")
        delisted_at = pd.to_datetime(profile_row.get("delisted_at"), errors="coerce")
        candidate_status_rows.append(
            {
                "symbol": symbol,
                "first_price_date": first_price_date.strftime("%Y-%m-%d") if pd.notna(first_price_date) else None,
                "last_price_date": last_price_date.strftime("%Y-%m-%d") if pd.notna(last_price_date) else None,
                "price_row_count": int(price_row.get("price_row_count") or 0),
                "profile_status": profile_row.get("status"),
                "profile_delisted_at": delisted_at.strftime("%Y-%m-%d") if pd.notna(delisted_at) else None,
                "profile_error": profile_row.get("error_msg"),
            }
        )

    working = statement_shadow.copy()
    working["symbol"] = working["symbol"].astype(str).str.upper()
    working["period_end"] = pd.to_datetime(working["period_end"], errors="coerce")
    working["latest_available_at"] = pd.to_datetime(working["latest_available_at"], errors="coerce")
    working["shares_outstanding"] = pd.to_numeric(working["shares_outstanding"], errors="coerce")
    if "latest_accession_no" in working.columns:
        working["latest_accession_no"] = working["latest_accession_no"].fillna("").astype(str)
    else:
        working["latest_accession_no"] = ""

    working = working[
        working["symbol"].notna()
        & working["period_end"].notna()
        & working["latest_available_at"].notna()
        & working["shares_outstanding"].notna()
        & (working["shares_outstanding"] > 0)
    ].copy()

    if working.empty:
        empty_map = {pd.Timestamp(date).normalize(): [] for date in rebalance_dates}
        return empty_map, {
            "contract": HISTORICAL_DYNAMIC_PIT_UNIVERSE,
            "statement_freq": statement_freq,
            "requested_count": len(requested_tickers),
            "input_candidate_count": input_candidate_count,
            "candidate_pool_count": len(candidate_tickers),
            "target_size": int(target_size),
            "membership_dates": len(rebalance_dates),
            "first_membership_count": 0,
            "last_membership_count": 0,
            "min_membership_count": 0,
            "max_membership_count": 0,
            "avg_membership_count": 0.0,
            "avg_turnover_count": 0.0,
            "avg_turnover_pct": 0.0,
            "statement_ready_count": 0,
            "per_date_rows": [],
        }, [], candidate_status_rows

    sort_cols = ["symbol", "latest_available_at", "period_end", "latest_accession_no"]
    working = working.sort_values(sort_cols)

    membership_map: dict[pd.Timestamp, list[str]] = {}
    per_date_rows: list[dict[str, object]] = []
    snapshot_rows: list[dict[str, object]] = []
    membership_counts: list[int] = []
    turnover_counts: list[int] = []
    prev_members: set[str] = set()

    for rebalance_date in rebalance_dates:
        as_of_ts = pd.Timestamp(rebalance_date).normalize()
        pre_listing_excluded_count = int(
            sum(
                1
                for row in candidate_status_rows
                if row.get("first_price_date")
                and pd.to_datetime(row["first_price_date"], errors="coerce") > as_of_ts
            )
        )
        post_last_price_excluded_count = int(
            sum(
                1
                for row in candidate_status_rows
                if row.get("last_price_date")
                and pd.to_datetime(row["last_price_date"], errors="coerce") < as_of_ts
            )
        )
        continuity_ready_count = int(
            sum(
                1
                for row in candidate_status_rows
                if row.get("first_price_date")
                and row.get("last_price_date")
                and pd.to_datetime(row["first_price_date"], errors="coerce") <= as_of_ts <= pd.to_datetime(row["last_price_date"], errors="coerce")
            )
        )
        asset_profile_delisted_count = int(
            sum(
                1
                for row in candidate_status_rows
                if row.get("profile_delisted_at")
                and pd.to_datetime(row["profile_delisted_at"], errors="coerce") <= as_of_ts
            )
        )
        asset_profile_issue_count = int(
            sum(
                1
                for row in candidate_status_rows
                if str(row.get("profile_status") or "").lower() in {"not_found", "error"}
            )
        )
        eligible_shadow = working[working["latest_available_at"] <= as_of_ts]
        if eligible_shadow.empty:
            membership_map[as_of_ts] = []
            per_date_rows.append(
                {
                    "date": as_of_ts.strftime("%Y-%m-%d"),
                    "membership_count": 0,
                    "rankable_count": 0,
                    "statement_ready_count": 0,
                    "continuity_ready_count": continuity_ready_count,
                    "pre_listing_excluded_count": pre_listing_excluded_count,
                    "post_last_price_excluded_count": post_last_price_excluded_count,
                    "asset_profile_delisted_count": asset_profile_delisted_count,
                    "asset_profile_issue_count": asset_profile_issue_count,
                    "turnover_count": 0,
                }
            )
            snapshot_rows.append(
                {
                    "date": as_of_ts.strftime("%Y-%m-%d"),
                    "members": [],
                    "membership_count": 0,
                    "rankable_count": 0,
                    "statement_ready_count": 0,
                }
            )
            membership_counts.append(0)
            turnover_counts.append(0)
            prev_members = set()
            continue

        latest_shadow = eligible_shadow.groupby("symbol", as_index=False).tail(1).reset_index(drop=True)
        price_snapshot = price_by_date.get(as_of_ts)
        if price_snapshot is None or price_snapshot.empty:
            membership_map[as_of_ts] = []
            per_date_rows.append(
                {
                    "date": as_of_ts.strftime("%Y-%m-%d"),
                    "membership_count": 0,
                    "rankable_count": 0,
                    "statement_ready_count": int(latest_shadow["symbol"].nunique()),
                    "continuity_ready_count": continuity_ready_count,
                    "pre_listing_excluded_count": pre_listing_excluded_count,
                    "post_last_price_excluded_count": post_last_price_excluded_count,
                    "asset_profile_delisted_count": asset_profile_delisted_count,
                    "asset_profile_issue_count": asset_profile_issue_count,
                    "turnover_count": 0,
                }
            )
            snapshot_rows.append(
                {
                    "date": as_of_ts.strftime("%Y-%m-%d"),
                    "members": [],
                    "membership_count": 0,
                    "rankable_count": 0,
                    "statement_ready_count": int(latest_shadow["symbol"].nunique()),
                }
            )
            membership_counts.append(0)
            turnover_counts.append(0)
            prev_members = set()
            continue

        rankable = latest_shadow.merge(price_snapshot, on="symbol", how="inner")
        rankable["approx_market_cap"] = rankable["shares_outstanding"] * rankable["Close"]
        rankable = rankable[pd.to_numeric(rankable["approx_market_cap"], errors="coerce").notna()].copy()
        rankable = rankable[rankable["approx_market_cap"] > 0].copy()
        rankable = rankable.sort_values(["approx_market_cap", "symbol"], ascending=[False, True]).reset_index(drop=True)

        members = rankable.head(min(target_size, len(rankable)))["symbol"].astype(str).tolist()
        membership_map[as_of_ts] = members

        current_members = set(members)
        turnover_count = 0 if not prev_members else len(current_members.symmetric_difference(prev_members))
        prev_members = current_members

        membership_counts.append(len(members))
        turnover_counts.append(turnover_count)
        per_date_rows.append(
            {
                "date": as_of_ts.strftime("%Y-%m-%d"),
                "membership_count": len(members),
                "rankable_count": int(rankable["symbol"].nunique()),
                "statement_ready_count": int(latest_shadow["symbol"].nunique()),
                "continuity_ready_count": continuity_ready_count,
                "pre_listing_excluded_count": pre_listing_excluded_count,
                "post_last_price_excluded_count": post_last_price_excluded_count,
                "asset_profile_delisted_count": asset_profile_delisted_count,
                "asset_profile_issue_count": asset_profile_issue_count,
                "turnover_count": turnover_count,
            }
        )
        snapshot_rows.append(
            {
                "date": as_of_ts.strftime("%Y-%m-%d"),
                "members": members,
                "membership_count": len(members),
                "rankable_count": int(rankable["symbol"].nunique()),
                "statement_ready_count": int(latest_shadow["symbol"].nunique()),
            }
        )

    avg_membership_count = float(sum(membership_counts) / len(membership_counts)) if membership_counts else 0.0
    avg_turnover_count = (
        float(sum(turnover_counts[1:]) / max(1, len(turnover_counts) - 1))
        if len(turnover_counts) > 1
        else 0.0
    )

    summary = {
        "contract": HISTORICAL_DYNAMIC_PIT_UNIVERSE,
        "statement_freq": statement_freq,
        "requested_count": len(requested_tickers),
        "input_candidate_count": input_candidate_count,
        "candidate_pool_count": len(candidate_tickers),
        "target_size": int(target_size),
        "membership_dates": len(rebalance_dates),
        "first_membership_count": int(membership_counts[0]) if membership_counts else 0,
        "last_membership_count": int(membership_counts[-1]) if membership_counts else 0,
        "min_membership_count": int(min(membership_counts)) if membership_counts else 0,
        "max_membership_count": int(max(membership_counts)) if membership_counts else 0,
        "avg_membership_count": round(avg_membership_count, 2),
        "avg_turnover_count": round(avg_turnover_count, 2),
        "avg_turnover_pct": round((avg_turnover_count / target_size) if target_size else 0.0, 4),
        "statement_ready_count": int(working["symbol"].nunique()),
        "price_window_start": price_window_df["first_price_date"].min().strftime("%Y-%m-%d") if not price_window_df.empty else None,
        "price_window_end": price_window_df["last_price_date"].max().strftime("%Y-%m-%d") if not price_window_df.empty else None,
        "profile_active_count": int(sum(1 for row in candidate_status_rows if str(row.get("profile_status") or "").lower() == "active")),
        "profile_delisted_count": int(sum(1 for row in candidate_status_rows if str(row.get("profile_status") or "").lower() == "delisted")),
        "profile_issue_count": int(sum(1 for row in candidate_status_rows if str(row.get("profile_status") or "").lower() in {"not_found", "error"})),
        "per_date_rows": per_date_rows[:120],
    }
    return membership_map, summary, snapshot_rows, candidate_status_rows


def _apply_universe_membership_to_snapshot_map(
    snapshot_by_date: dict[pd.Timestamp, pd.DataFrame],
    membership_map: dict[pd.Timestamp, list[str]],
) -> dict[pd.Timestamp, pd.DataFrame]:
    filtered_map: dict[pd.Timestamp, pd.DataFrame] = {}
    for snapshot_date, snapshot_df in snapshot_by_date.items():
        allowed = set(membership_map.get(pd.Timestamp(snapshot_date).normalize(), []))
        if snapshot_df is None or snapshot_df.empty or not allowed:
            filtered_map[pd.Timestamp(snapshot_date).normalize()] = snapshot_df.iloc[0:0].copy() if isinstance(snapshot_df, pd.DataFrame) else pd.DataFrame()
            continue
        filtered_map[pd.Timestamp(snapshot_date).normalize()] = (
            snapshot_df[snapshot_df["symbol"].astype(str).str.upper().isin(allowed)].copy().reset_index(drop=True)
        )
    return filtered_map


def _resolve_guardrail_reference_ticker(
    benchmark_ticker: str | None,
    guardrail_reference_ticker: str | None,
) -> str:
    return str(
        guardrail_reference_ticker
        or benchmark_ticker
        or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK
    ).strip().upper()


def _run_statement_shadow_snapshot_from_db(
    *,
    start=None,
    end=None,
    timeframe="1d",
    option="month_end",
    tickers=None,
    statement_freq="annual",
    factor_names: list[str],
    top_n=2,
    rebalance_interval=1,
    min_price: float = 0.0,
    min_history_months: int = STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
    min_avg_dollar_volume_20d_m: float = STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
    lower_is_better_factors: list[str] | None = None,
    trend_filter_enabled=False,
    trend_filter_window=STRICT_TREND_FILTER_DEFAULT_WINDOW,
    weighting_mode: str = STRICT_DEFAULT_WEIGHTING_MODE,
    rejected_slot_fill_enabled: bool = STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
    partial_cash_retention_enabled: bool = STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
    risk_off_mode: str = STRICT_DEFAULT_RISK_OFF_MODE,
    defensive_tickers=None,
    market_regime_enabled=False,
    market_regime_window=STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    market_regime_benchmark=STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    benchmark_ticker=STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    guardrail_reference_ticker=None,
    underperformance_guardrail_enabled=STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    underperformance_guardrail_window_months=STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    underperformance_guardrail_threshold=STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    drawdown_guardrail_enabled=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
    drawdown_guardrail_window_months=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    drawdown_guardrail_strategy_threshold=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
    drawdown_guardrail_gap_threshold=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
    universe_contract: str = STATIC_MANAGED_RESEARCH_UNIVERSE,
    dynamic_candidate_tickers=None,
    dynamic_target_size: int | None = None,
    return_details: bool = False,
):
    requested_tickers = _normalize_symbol_list(
        tickers if tickers is not None else ["AAPL", "MSFT", "GOOG"]
    )
    if not requested_tickers:
        raise ValueError("At least one ticker is required for statement shadow snapshot execution.")

    candidate_tickers = requested_tickers
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        candidate_tickers = _normalize_symbol_list(dynamic_candidate_tickers or requested_tickers)
        if not candidate_tickers:
            candidate_tickers = requested_tickers

    if risk_off_mode not in {STRICT_RISK_OFF_MODE_CASH, STRICT_RISK_OFF_MODE_DEFENSIVE}:
        raise ValueError(
            "risk_off_mode must be one of "
            f"{{'{STRICT_RISK_OFF_MODE_CASH}', '{STRICT_RISK_OFF_MODE_DEFENSIVE}'}}."
        )
    if weighting_mode not in {STRICT_WEIGHTING_MODE_EQUAL, STRICT_WEIGHTING_MODE_RANK_TAPERED}:
        raise ValueError(
            "weighting_mode must be one of "
            f"{{'{STRICT_WEIGHTING_MODE_EQUAL}', '{STRICT_WEIGHTING_MODE_RANK_TAPERED}'}}."
        )

    effective_guardrail_reference_ticker = _resolve_guardrail_reference_ticker(
        benchmark_ticker,
        guardrail_reference_ticker,
    )

    effective_defensive_tickers = _normalize_symbol_list(
        defensive_tickers if defensive_tickers is not None else STRICT_DEFAULT_DEFENSIVE_TICKERS
    )
    if risk_off_mode != STRICT_RISK_OFF_MODE_DEFENSIVE:
        effective_defensive_tickers = []

    price_symbols = _normalize_symbol_list([*candidate_tickers, *effective_defensive_tickers])

    candidate_price_dfs = _get_cached_snapshot_strategy_price_dfs(
        symbols=candidate_tickers,
        option=option,
        start=start,
        end=end,
        timeframe=timeframe,
        trend_filter_window=(trend_filter_window if trend_filter_enabled else None),
    )
    price_dfs = dict(candidate_price_dfs)
    if effective_defensive_tickers:
        defensive_price_dfs = _get_cached_snapshot_strategy_price_dfs(
            symbols=effective_defensive_tickers,
            option=option,
            start=start,
            end=end,
            timeframe=timeframe,
            trend_filter_window=None,
        )
        price_dfs.update(defensive_price_dfs)
    first_valid_price_dates = _get_cached_snapshot_strategy_price_first_dates(
        symbols=price_symbols,
        option=option,
        start=start,
        end=end,
        timeframe=timeframe,
        trend_filter_window=(trend_filter_window if trend_filter_enabled else None),
        min_history_months=int(min_history_months or 0),
    )
    avg_dollar_volume_20d_by_date: dict[str, dict[pd.Timestamp, float]] = {}
    if float(min_avg_dollar_volume_20d_m or 0.0) > 0.0:
        avg_dollar_volume_20d_by_date = _get_cached_snapshot_strategy_avg_dollar_volume_20d(
            symbols=candidate_tickers,
            start=start,
            end=end,
            timeframe=timeframe,
        )

    rebalance_dates = pd.to_datetime(next(iter(candidate_price_dfs.values()))["Date"]).tolist()
    factor_history = _get_cached_statement_factors_shadow(
        symbols=list(candidate_price_dfs.keys()),
        freq=statement_freq,
        end=end,
    )
    snapshot_by_date = _build_shadow_factor_snapshot_map(
        factor_history,
        rebalance_dates=rebalance_dates,
        factor_names=factor_names,
    )

    universe_debug: dict[str, object] = {
        "contract": universe_contract,
        "requested_count": len(requested_tickers),
        "candidate_pool_count": len(candidate_price_dfs),
        "target_size": len(requested_tickers),
        "membership_dates": len(rebalance_dates),
    }
    membership_count_map = {
        pd.Timestamp(snapshot_date).normalize(): len(requested_tickers)
        for snapshot_date in rebalance_dates
    }

    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        statement_shadow = _get_cached_statement_fundamentals_shadow(
            symbols=list(price_dfs.keys()),
            freq=statement_freq,
            end=end,
        )
        asset_profile_summary = _get_cached_asset_profile_status_summary(
            symbols=list(price_dfs.keys())
        )
        membership_map, universe_debug, universe_snapshot_rows, candidate_status_rows = _build_dynamic_pit_membership_map(
            price_dfs=candidate_price_dfs,
            statement_shadow=statement_shadow,
            rebalance_dates=rebalance_dates,
            target_size=int(dynamic_target_size or len(requested_tickers)),
            requested_tickers=requested_tickers,
            statement_freq=statement_freq,
            input_candidate_count=len(candidate_tickers),
            asset_profile_summary=asset_profile_summary,
        )
        snapshot_by_date = _apply_universe_membership_to_snapshot_map(snapshot_by_date, membership_map)
        membership_count_map = {
            membership_date: len(members)
            for membership_date, members in membership_map.items()
        }
    else:
        universe_snapshot_rows = []
        candidate_status_rows = []

    market_regime_df = None
    if market_regime_enabled:
        market_regime_df = _build_market_regime_overlay_df(
            market_regime_benchmark,
            option=option,
            start=start,
            end=end,
            timeframe=timeframe,
            from_db=True,
            market_regime_window=market_regime_window,
        )

    guardrail_benchmark_df = None
    if underperformance_guardrail_enabled or drawdown_guardrail_enabled:
        guardrail_benchmark_df = _build_underperformance_guardrail_df(
            effective_guardrail_reference_ticker,
            option=option,
            start=start,
            end=end,
            timeframe=timeframe,
            from_db=True,
        )

    df = quality_snapshot_equal_weight(
        price_dfs,
        snapshot_by_date,
        start_balance=10000,
        quality_factors=factor_names,
        top_n=top_n,
        min_price=min_price,
        min_history_months=min_history_months,
        min_avg_dollar_volume_20d_m=min_avg_dollar_volume_20d_m,
        candidate_tickers=list(candidate_price_dfs.keys()),
        first_valid_price_dates=first_valid_price_dates,
        avg_dollar_volume_20d_by_date=avg_dollar_volume_20d_by_date,
        lower_is_better_factors=lower_is_better_factors,
        rebalance_interval=rebalance_interval,
        trend_filter_enabled=trend_filter_enabled,
        trend_filter_window=trend_filter_window,
        weighting_mode=weighting_mode,
        rejected_slot_fill_enabled=rejected_slot_fill_enabled,
        partial_cash_retention_enabled=partial_cash_retention_enabled,
        risk_off_mode=risk_off_mode,
        defensive_tickers=effective_defensive_tickers,
        market_regime_enabled=market_regime_enabled,
        market_regime_window=market_regime_window,
        market_regime_benchmark=market_regime_benchmark,
        market_regime_df=market_regime_df,
        underperformance_guardrail_enabled=underperformance_guardrail_enabled,
        underperformance_guardrail_window_months=underperformance_guardrail_window_months,
        underperformance_guardrail_threshold=underperformance_guardrail_threshold,
        underperformance_guardrail_benchmark=effective_guardrail_reference_ticker,
        underperformance_guardrail_df=guardrail_benchmark_df if underperformance_guardrail_enabled else None,
        drawdown_guardrail_enabled=drawdown_guardrail_enabled,
        drawdown_guardrail_window_months=drawdown_guardrail_window_months,
        drawdown_guardrail_strategy_threshold=drawdown_guardrail_strategy_threshold,
        drawdown_guardrail_gap_threshold=drawdown_guardrail_gap_threshold,
        drawdown_guardrail_benchmark=effective_guardrail_reference_ticker,
        drawdown_guardrail_df=guardrail_benchmark_df if drawdown_guardrail_enabled else None,
    )

    count_series = pd.to_datetime(df["Date"], errors="coerce").dt.normalize().map(membership_count_map).fillna(0).astype(int)
    df["Universe Membership Count"] = count_series
    df["Universe Contract"] = universe_contract

    df = (
        round_columns(df, cols=["Cash", "Total Balance", "End Balance", "Next Balance"], decimals=1)
        .pipe(round_columns, cols=["Total Return", "Selected Score"], decimals=3)
    )

    if return_details:
        return {
            "result_df": df,
            "universe_debug": universe_debug,
            "candidate_tickers": list(price_dfs.keys()),
            "universe_snapshot_rows": universe_snapshot_rows,
            "candidate_status_rows": candidate_status_rows,
        }
    return df


def get_statement_quality_snapshot_shadow_from_db(
    *,
    start=None,
    end=None,
    timeframe="1d",
    option="month_end",
    tickers=None,
    statement_freq="annual",
    quality_factors=None,
    top_n=2,
    rebalance_interval=1,
    min_price: float = 0.0,
    min_history_months: int = STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
    min_avg_dollar_volume_20d_m: float = STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
    trend_filter_enabled=False,
    trend_filter_window=STRICT_TREND_FILTER_DEFAULT_WINDOW,
    weighting_mode: str = STRICT_DEFAULT_WEIGHTING_MODE,
    rejected_slot_handling_mode: str | None = None,
    rejected_slot_fill_enabled: bool = STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
    partial_cash_retention_enabled: bool = STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
    risk_off_mode: str = STRICT_DEFAULT_RISK_OFF_MODE,
    defensive_tickers=None,
    market_regime_enabled=False,
    market_regime_window=STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    market_regime_benchmark=STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    benchmark_ticker=STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    guardrail_reference_ticker=None,
    underperformance_guardrail_enabled=STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    underperformance_guardrail_window_months=STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    underperformance_guardrail_threshold=STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    drawdown_guardrail_enabled=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
    drawdown_guardrail_window_months=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    drawdown_guardrail_strategy_threshold=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
    drawdown_guardrail_gap_threshold=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
    universe_contract: str = STATIC_MANAGED_RESEARCH_UNIVERSE,
    dynamic_candidate_tickers=None,
    dynamic_target_size: int | None = None,
    return_details: bool = False,
):
    if quality_factors is None:
        quality_factors = QUALITY_STRICT_DEFAULT_FACTORS.copy()
    rejected_slot_handling_mode = resolve_strict_rejection_handling_mode(
        rejected_slot_handling_mode,
        rejected_slot_fill_enabled=rejected_slot_fill_enabled,
        partial_cash_retention_enabled=partial_cash_retention_enabled,
    )
    rejected_slot_fill_enabled, partial_cash_retention_enabled = strict_rejection_handling_mode_to_flags(
        rejected_slot_handling_mode
    )

    return _run_statement_shadow_snapshot_from_db(
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        tickers=tickers,
        statement_freq=statement_freq,
        factor_names=quality_factors,
        top_n=top_n,
        min_price=min_price,
        min_history_months=min_history_months,
        min_avg_dollar_volume_20d_m=min_avg_dollar_volume_20d_m,
        lower_is_better_factors=["debt_ratio", "debt_to_assets", "net_debt_to_equity"],
        rebalance_interval=rebalance_interval,
        trend_filter_enabled=trend_filter_enabled,
        trend_filter_window=trend_filter_window,
        weighting_mode=weighting_mode,
        rejected_slot_fill_enabled=rejected_slot_fill_enabled,
        partial_cash_retention_enabled=partial_cash_retention_enabled,
        risk_off_mode=risk_off_mode,
        defensive_tickers=defensive_tickers,
        market_regime_enabled=market_regime_enabled,
        market_regime_window=market_regime_window,
        market_regime_benchmark=market_regime_benchmark,
        benchmark_ticker=benchmark_ticker,
        guardrail_reference_ticker=guardrail_reference_ticker,
        underperformance_guardrail_enabled=underperformance_guardrail_enabled,
        underperformance_guardrail_window_months=underperformance_guardrail_window_months,
        underperformance_guardrail_threshold=underperformance_guardrail_threshold,
        drawdown_guardrail_enabled=drawdown_guardrail_enabled,
        drawdown_guardrail_window_months=drawdown_guardrail_window_months,
        drawdown_guardrail_strategy_threshold=drawdown_guardrail_strategy_threshold,
        drawdown_guardrail_gap_threshold=drawdown_guardrail_gap_threshold,
        universe_contract=universe_contract,
        dynamic_candidate_tickers=dynamic_candidate_tickers,
        dynamic_target_size=dynamic_target_size,
        return_details=return_details,
    )


def get_statement_value_snapshot_shadow_from_db(
    *,
    start=None,
    end=None,
    timeframe="1d",
    option="month_end",
    tickers=None,
    statement_freq="annual",
    value_factors=None,
    top_n=10,
    rebalance_interval=1,
    min_price: float = 0.0,
    min_history_months: int = STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
    min_avg_dollar_volume_20d_m: float = STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
    trend_filter_enabled=False,
    trend_filter_window=STRICT_TREND_FILTER_DEFAULT_WINDOW,
    weighting_mode: str = STRICT_DEFAULT_WEIGHTING_MODE,
    rejected_slot_handling_mode: str | None = None,
    rejected_slot_fill_enabled: bool = STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
    partial_cash_retention_enabled: bool = STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
    risk_off_mode: str = STRICT_DEFAULT_RISK_OFF_MODE,
    defensive_tickers=None,
    market_regime_enabled=False,
    market_regime_window=STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    market_regime_benchmark=STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    benchmark_ticker=STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    guardrail_reference_ticker=None,
    underperformance_guardrail_enabled=STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    underperformance_guardrail_window_months=STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    underperformance_guardrail_threshold=STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    drawdown_guardrail_enabled=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
    drawdown_guardrail_window_months=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    drawdown_guardrail_strategy_threshold=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
    drawdown_guardrail_gap_threshold=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
    universe_contract: str = STATIC_MANAGED_RESEARCH_UNIVERSE,
    dynamic_candidate_tickers=None,
    dynamic_target_size: int | None = None,
    return_details: bool = False,
):
    if value_factors is None:
        value_factors = VALUE_STRICT_DEFAULT_FACTORS.copy()
    rejected_slot_handling_mode = resolve_strict_rejection_handling_mode(
        rejected_slot_handling_mode,
        rejected_slot_fill_enabled=rejected_slot_fill_enabled,
        partial_cash_retention_enabled=partial_cash_retention_enabled,
    )
    rejected_slot_fill_enabled, partial_cash_retention_enabled = strict_rejection_handling_mode_to_flags(
        rejected_slot_handling_mode
    )

    return _run_statement_shadow_snapshot_from_db(
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        tickers=tickers,
        statement_freq=statement_freq,
        factor_names=value_factors,
        top_n=top_n,
        min_price=min_price,
        min_history_months=min_history_months,
        min_avg_dollar_volume_20d_m=min_avg_dollar_volume_20d_m,
        rebalance_interval=rebalance_interval,
        lower_is_better_factors=["per", "pbr", "psr", "pcr", "pfcr", "ev_ebit", "por"],
        trend_filter_enabled=trend_filter_enabled,
        trend_filter_window=trend_filter_window,
        weighting_mode=weighting_mode,
        rejected_slot_fill_enabled=rejected_slot_fill_enabled,
        partial_cash_retention_enabled=partial_cash_retention_enabled,
        risk_off_mode=risk_off_mode,
        defensive_tickers=defensive_tickers,
        market_regime_enabled=market_regime_enabled,
        market_regime_window=market_regime_window,
        market_regime_benchmark=market_regime_benchmark,
        benchmark_ticker=benchmark_ticker,
        guardrail_reference_ticker=guardrail_reference_ticker,
        underperformance_guardrail_enabled=underperformance_guardrail_enabled,
        underperformance_guardrail_window_months=underperformance_guardrail_window_months,
        underperformance_guardrail_threshold=underperformance_guardrail_threshold,
        drawdown_guardrail_enabled=drawdown_guardrail_enabled,
        drawdown_guardrail_window_months=drawdown_guardrail_window_months,
        drawdown_guardrail_strategy_threshold=drawdown_guardrail_strategy_threshold,
        drawdown_guardrail_gap_threshold=drawdown_guardrail_gap_threshold,
        universe_contract=universe_contract,
        dynamic_candidate_tickers=dynamic_candidate_tickers,
        dynamic_target_size=dynamic_target_size,
        return_details=return_details,
    )


def get_statement_quality_value_snapshot_shadow_from_db(
    *,
    start=None,
    end=None,
    timeframe="1d",
    option="month_end",
    tickers=None,
    statement_freq="annual",
    quality_factors=None,
    value_factors=None,
    top_n=10,
    rebalance_interval=1,
    min_price: float = 0.0,
    min_history_months: int = STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
    min_avg_dollar_volume_20d_m: float = STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
    trend_filter_enabled=False,
    trend_filter_window=STRICT_TREND_FILTER_DEFAULT_WINDOW,
    weighting_mode: str = STRICT_DEFAULT_WEIGHTING_MODE,
    rejected_slot_handling_mode: str | None = None,
    rejected_slot_fill_enabled: bool = STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
    partial_cash_retention_enabled: bool = STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
    risk_off_mode: str = STRICT_DEFAULT_RISK_OFF_MODE,
    defensive_tickers=None,
    market_regime_enabled=False,
    market_regime_window=STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    market_regime_benchmark=STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    benchmark_ticker=STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    guardrail_reference_ticker=None,
    underperformance_guardrail_enabled=STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    underperformance_guardrail_window_months=STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    underperformance_guardrail_threshold=STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    drawdown_guardrail_enabled=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
    drawdown_guardrail_window_months=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    drawdown_guardrail_strategy_threshold=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
    drawdown_guardrail_gap_threshold=STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
    universe_contract: str = STATIC_MANAGED_RESEARCH_UNIVERSE,
    dynamic_candidate_tickers=None,
    dynamic_target_size: int | None = None,
    return_details: bool = False,
):
    if quality_factors is None:
        quality_factors = QUALITY_STRICT_DEFAULT_FACTORS.copy()
    if value_factors is None:
        value_factors = VALUE_STRICT_DEFAULT_FACTORS.copy()
    rejected_slot_handling_mode = resolve_strict_rejection_handling_mode(
        rejected_slot_handling_mode,
        rejected_slot_fill_enabled=rejected_slot_fill_enabled,
        partial_cash_retention_enabled=partial_cash_retention_enabled,
    )
    rejected_slot_fill_enabled, partial_cash_retention_enabled = strict_rejection_handling_mode_to_flags(
        rejected_slot_handling_mode
    )

    combined_factors = []
    for factor_name in [*quality_factors, *value_factors]:
        normalized_name = str(factor_name).strip()
        if normalized_name and normalized_name not in combined_factors:
            combined_factors.append(normalized_name)

    return _run_statement_shadow_snapshot_from_db(
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        tickers=tickers,
        statement_freq=statement_freq,
        factor_names=combined_factors,
        top_n=top_n,
        min_price=min_price,
        min_history_months=min_history_months,
        min_avg_dollar_volume_20d_m=min_avg_dollar_volume_20d_m,
        rebalance_interval=rebalance_interval,
        lower_is_better_factors=[
            "per",
            "pbr",
            "psr",
            "pcr",
            "pfcr",
            "ev_ebit",
            "por",
            "debt_ratio",
            "debt_to_assets",
            "net_debt_to_equity",
        ],
        trend_filter_enabled=trend_filter_enabled,
        trend_filter_window=trend_filter_window,
        weighting_mode=weighting_mode,
        rejected_slot_fill_enabled=rejected_slot_fill_enabled,
        partial_cash_retention_enabled=partial_cash_retention_enabled,
        risk_off_mode=risk_off_mode,
        defensive_tickers=defensive_tickers,
        market_regime_enabled=market_regime_enabled,
        market_regime_window=market_regime_window,
        market_regime_benchmark=market_regime_benchmark,
        benchmark_ticker=benchmark_ticker,
        guardrail_reference_ticker=guardrail_reference_ticker,
        underperformance_guardrail_enabled=underperformance_guardrail_enabled,
        underperformance_guardrail_window_months=underperformance_guardrail_window_months,
        underperformance_guardrail_threshold=underperformance_guardrail_threshold,
        drawdown_guardrail_enabled=drawdown_guardrail_enabled,
        drawdown_guardrail_window_months=drawdown_guardrail_window_months,
        drawdown_guardrail_strategy_threshold=drawdown_guardrail_strategy_threshold,
        drawdown_guardrail_gap_threshold=drawdown_guardrail_gap_threshold,
        universe_contract=universe_contract,
        dynamic_candidate_tickers=dynamic_candidate_tickers,
        dynamic_target_size=dynamic_target_size,
        return_details=return_details,
    )


def portfolio_sample():
    """
        Legacy direct-fetch portfolio sample.
        provider 기준 reference output 비교용으로 유지한다.
    """
    period = "15y"
    option = "month_end"
    start = "2016-01-01"
    freq = "M"

    equal = get_equal_weight(period=period, option=option, start=start)
    gtaa3 = get_gtaa3(period=period, option=option, start=start)
    risk = get_risk_parity_trend(period=period, option=option, start=start)
    dual = get_dual_momentum(period=period, option=option, start=start)
    
    # combo = make_monthly_weighted_portfolio(
    #     dfs=[equal, gtaa3],
    #     ratios=[0.5, 0.5],
    #     names=['Equal', 'GTAA3'],
    #     date_policy="intersection"
    # )

    results = {
        "Equal Weight": equal,
        "GTAA": gtaa3,
        "Risk Parity" : risk,
        "Dual Momentum" : dual,
        # "Equal(50)+GTAA(50)" : combo
    }

    display(results['GTAA'].tail())
    plot_equity_curves(results, "Equity Curve Comparison")
    for key, df in results.items():
        display(portfolio_performance_summary(df, key, freq))


def portfolio_sample_from_db(start=None, end=None, timeframe="1d"):
    """
        DB-backed portfolio sample.
        loader/runtime/product path 검증용 기준 포트폴리오 샘플이다.
    """
    option = "month_end"
    freq = "M"

    equal = get_equal_weight_from_db(start=start, end=end, timeframe=timeframe, option=option)
    gtaa3 = get_gtaa3_from_db(start=start, end=end, timeframe=timeframe, option=option)
    risk = get_risk_parity_trend_from_db(start=start, end=end, timeframe=timeframe, option=option)
    dual = get_dual_momentum_from_db(start=start, end=end, timeframe=timeframe, option=option)

    results = {
        "Equal Weight": equal,
        "GTAA": gtaa3,
        "Risk Parity" : risk,
        "Dual Momentum" : dual,
    }

    display(results['GTAA'].tail())
    plot_equity_curves(results, "Equity Curve Comparison (DB)")
    for key, df in results.items():
        display(portfolio_performance_summary(df, key, freq))



def asset_profiles_sample():
    """
        기업정보 로드
    """
    fails = collect_and_store_asset_profiles(
        kinds= ["etf"],
        chunk_size=50,      # 처음엔 20~50 추천
        sleep=0.5,          # rate limit 방지
        max_retry=3,
        host="localhost",
        user="root",
        password="1234",
        port=3306,
        save_fail_csv=True,
        csv_dir="csv",
    )

    db = MySQLClient("localhost", "root", "1234", 3306)
    db.use_db("finance_meta")

    # 테이블 생성 (없으면 생성)
    db.execute(NYSE_SCHEMAS["asset_profile"])

    # 스키마 동기화 (누락된 컬럼 자동 추가)
    sync_table_schema(db, "nyse_asset_profile", NYSE_SCHEMAS["asset_profile"], "finance_meta")



def fundamentals_sample(freq="annual"):
    """
        재무재표 로드 샘플
    """

    symbols = load_symbols_from_asset_profile("stock", on_filter=True)

    upsert_fundamentals(symbols, freq=freq)
    # upsert_fundamentals(symbols[:5], freq="quarterly")

    upsert_factors(symbols, freq=freq)
    # upsert_factors(symbols, freq="quarterly")


def financial_statement_source_sample(symbol="AAPL"):
    """
        EDGAR 상세 재무제표 원천 fact / filing 메타 구조 확인용 샘플
    """
    return inspect_financial_statement_source(symbol)


def financial_statements_sample(symbols=None, freq="annual"):
    """
        상세 재무제표 DB 적재 샘플
    """
    if symbols is None:
        symbols = ["AAPL", "MSFT", "JPM"]

    return upsert_financial_statements(symbols=symbols, freq=freq, period=freq)
    """
        DB-backed runtime sample.
    """
    """
        DB-backed runtime sample.
    """
    """
        DB-backed runtime sample.
    """
