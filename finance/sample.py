"""
Sample and smoke-test entrypoints for the finance package.

Path split:
- legacy direct-fetch functions:
  provider-backed reference samples that read OHLCV directly from yfinance
- `*_from_db` functions:
  DB-backed runtime samples that validate the loader/engine/strategy path
"""

from math import comb
from IPython.display import display
import pandas as pd
from .engine import BacktestEngine
from .strategy import (
    EqualWeightStrategy,
    GTAA3Strategy,
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
    load_factor_snapshot,
    load_statement_factor_snapshot_shadow,
    load_statement_factors_shadow,
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
    engine = (
        _build_price_only_engine(
            tickers,
            option=option,
            start=start,
            end=end,
            timeframe=timeframe,
            from_db=from_db,
        )
        .filter_by_period()
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


def get_gtaa3(period="15y", option="month_end", top=3, interval=2, start=None):
    """
        Legacy direct-fetch sample.
    """
    tickers = ['SPY','IWD','IWM','IWN','MTUM','EFA','TLT','IEF','LQD','DBC','VNQ','GLD']

    engine = (
        _build_price_only_engine(
            tickers,
            option=option,
            period=period,
        )
        .add_ma(200)
        .filter_by_period()
        .add_interval_returns([1,3,6,12])
        .align_dates()
        .slice(start=start)
        .add_avg_score()
        .drop_columns(["High","Low","Open","Volume","1MReturn","3MReturn","6MReturn","12MReturn"])
        .interval(interval)
    )

    strategy = GTAA3Strategy(
        start_balance=10000,
        top=top,
        filter_ma="MA200"
    )

    df = engine.run(strategy).round_columns().round_columns(cols=["Return", "Total Return"], decimals=3).result
    return df


def get_gtaa3_from_db(
    option="month_end",
    top=3,
    interval=2,
    start=None,
    end=None,
    timeframe="1d",
    tickers=None,
):
    if tickers is None:
        tickers = ['SPY','IWD','IWM','IWN','MTUM','EFA','TLT','IEF','LQD','DBC','VNQ','GLD']

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
        .add_interval_returns([1,3,6,12])
        .align_dates()
        .slice(start=start, end=end)
        .add_avg_score()
        .drop_columns(["High","Low","Open","Volume","1MReturn","3MReturn","6MReturn","12MReturn"])
        .interval(interval)
    )

    strategy = GTAA3Strategy(
        start_balance=10000,
        top=top,
        filter_ma="MA200"
    )

    df = engine.run(strategy).round_columns().round_columns(cols=["Return", "Total Return"], decimals=3).result
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
    start=None,
    end=None,
    timeframe="1d",
    tickers=None,
):
    if tickers is None:
        tickers = ['SPY','TLT','GLD','IEF','LQD']

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

    strategy = RiskParityTrendStrategy(
        start_balance=10000,
        rebalance_interval=rebalance_interval,
        vol_window=vol_window,
        filter_ma="MA200",
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
    start=None,
    end=None,
    timeframe="1d",
    tickers=None,
):
    if tickers is None:
        tickers = ["QQQ", "SPY", "IWM", "SOXX", "BIL"]

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

    strategy = DualMomentumStrategy(
        start_balance=10000,
        top=top,
        lookback_col="12MReturn",
        filter_ma="MA200",
        rebalance_interval=rebalance_interval,
        cash_ticker="BIL",
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
):
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
    factor_history = load_statement_factors_shadow(
        symbols=tickers,
        freq=statement_freq,
        end=end,
    )
    snapshot_by_date = _build_shadow_factor_snapshot_map(
        factor_history,
        rebalance_dates=rebalance_dates,
        factor_names=quality_factors,
    )

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
):
    if tickers is None:
        tickers = ["AAPL", "MSFT", "GOOG"]
    if value_factors is None:
        value_factors = VALUE_STRICT_DEFAULT_FACTORS.copy()

    price_dfs = _build_snapshot_strategy_price_dfs(
        tickers,
        option=option,
        start=start,
        end=end,
        timeframe=timeframe,
        from_db=True,
    )

    rebalance_dates = pd.to_datetime(next(iter(price_dfs.values()))["Date"]).tolist()
    factor_history = load_statement_factors_shadow(
        symbols=tickers,
        freq=statement_freq,
        end=end,
    )
    snapshot_by_date = _build_shadow_factor_snapshot_map(
        factor_history,
        rebalance_dates=rebalance_dates,
        factor_names=value_factors,
    )

    df = quality_snapshot_equal_weight(
        price_dfs,
        snapshot_by_date,
        start_balance=10000,
        quality_factors=value_factors,
        top_n=top_n,
        lower_is_better_factors=["per", "pbr", "psr", "pcr", "pfcr", "ev_ebit", "por"],
        rebalance_interval=rebalance_interval,
    )

    df = (
        round_columns(df, cols=["Cash", "Total Balance", "End Balance", "Next Balance"], decimals=1)
        .pipe(round_columns, cols=["Total Return", "Selected Score"], decimals=3)
    )
    return df


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
):
    if tickers is None:
        tickers = ["AAPL", "MSFT", "GOOG"]
    if quality_factors is None:
        quality_factors = QUALITY_STRICT_DEFAULT_FACTORS.copy()
    if value_factors is None:
        value_factors = VALUE_STRICT_DEFAULT_FACTORS.copy()

    combined_factors = []
    for factor_name in [*quality_factors, *value_factors]:
        normalized_name = str(factor_name).strip()
        if normalized_name and normalized_name not in combined_factors:
            combined_factors.append(normalized_name)

    price_dfs = _build_snapshot_strategy_price_dfs(
        tickers,
        option=option,
        start=start,
        end=end,
        timeframe=timeframe,
        from_db=True,
    )

    rebalance_dates = pd.to_datetime(next(iter(price_dfs.values()))["Date"]).tolist()
    factor_history = load_statement_factors_shadow(
        symbols=tickers,
        freq=statement_freq,
        end=end,
    )
    snapshot_by_date = _build_shadow_factor_snapshot_map(
        factor_history,
        rebalance_dates=rebalance_dates,
        factor_names=combined_factors,
    )

    df = quality_snapshot_equal_weight(
        price_dfs,
        snapshot_by_date,
        start_balance=10000,
        quality_factors=combined_factors,
        top_n=top_n,
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
        rebalance_interval=rebalance_interval,
    )

    df = (
        round_columns(df, cols=["Cash", "Total Balance", "End Balance", "Next Balance"], decimals=1)
        .pipe(round_columns, cols=["Total Return", "Selected Score"], decimals=3)
    )
    return df


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
