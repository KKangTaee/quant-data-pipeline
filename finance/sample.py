from math import comb
from IPython.display import display
from .engine import BacktestEngine
from .strategy import (
    EqualWeightStrategy,
    GTAA3Strategy,
    RiskParityTrendStrategy,
    DualMomentumStrategy
)

from .performance import(
    portfolio_performance_summary,
    make_monthly_weighted_portfolio,
)

from .visualize import(
    plot_equity_curves
)

from finance.data.asset_profile import(
    collect_and_store_asset_profiles,
    load_symbols_from_asset_profile
)

from .data.fundamentals import(
    upsert_fundamentals
)

from .data.factors import(
    upsert_factors
)
from .data.financial_statements import (
    inspect_financial_statement_source,
    upsert_financial_statements,
)

from finance.data.db.schema import sync_table_schema, NYSE_SCHEMAS
from finance.data.db.mysql import MySQLClient

def get_equal_weight(period="15y", option="month_end", interval=12, start=None):
    # tickers = ["GLD", "SPY", "SHY", "TLT"]
    tickers = ['VIG','SCHD','DGRO','GLD']
    engine = (
        BacktestEngine(tickers, period=period, option=option)
        .load_ohlcv()
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
        DB에 적재된 OHLCV를 사용한 균등 전략 샘플
    """
    if tickers is None:
        tickers = ['VIG', 'SCHD', 'DGRO', 'GLD']

    engine = (
        BacktestEngine(tickers, period="15y", option=option)
        .load_ohlcv_from_db(start=start, end=end, timeframe=timeframe)
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


def get_gtaa3(period="15y", option="month_end", top=3, start=None):
    tickers = ['SPY','IWD','IWM','IWN','MTUM','EFA','TLT','IEF','LQD','DBC','VNQ','GLD']

    engine = (
        BacktestEngine(tickers, period=period, option=option)
        .load_ohlcv()
        .add_ma(200)
        .filter_by_period()
        .add_interval_returns([1,3,6,12])
        .align_dates()
        .slice(start=start)
        .add_avg_score()
        .drop_columns(["High","Low","Open","Volume","1MReturn","3MReturn","6MReturn","12MReturn"])
        .interval(2)
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
    start=None,
    end=None,
    timeframe="1d",
    tickers=None,
):
    if tickers is None:
        tickers = ['SPY','IWD','IWM','IWN','MTUM','EFA','TLT','IEF','LQD','DBC','VNQ','GLD']

    engine = (
        BacktestEngine(tickers, period="db", option=option)
        .load_ohlcv_from_db(start=start, end=end, timeframe=timeframe)
        .add_ma(200)
        .filter_by_period()
        .add_interval_returns([1,3,6,12])
        .align_dates()
        .slice(start=start, end=end)
        .add_avg_score()
        .drop_columns(["High","Low","Open","Volume","1MReturn","3MReturn","6MReturn","12MReturn"])
        .interval(2)
    )

    strategy = GTAA3Strategy(
        start_balance=10000,
        top=top,
        filter_ma="MA200"
    )

    df = engine.run(strategy).round_columns().round_columns(cols=["Return", "Total Return"], decimals=3).result
    return df


def get_risk_parity_trend(period="15y", option="month_end", start=None):
    tickers = ['SPY','TLT','GLD','IEF','LQD']  # 예시

    engine = (
        BacktestEngine(tickers, period=period, option=option)
        .load_ohlcv()
        .add_ma(200)              # ✅ filter_ma="MA200"을 쓰기 위함
        .filter_by_period()
        .align_dates()
        .slice(start=start)
        .drop_columns(["High","Low","Open","Volume"])
    )

    strategy = RiskParityTrendStrategy(
        start_balance=10000,
        rebalance_interval=1,  # 월말 데이터면 1=매월 리밸런싱
        vol_window=6,          # 최근 6개월 변동성
        filter_ma="MA200",
    )

    df = engine.run(strategy).round_columns(
        cols=["Cash","Total Balance","End Balance","Next Balance"],
        decimals=1
    ).result

    return df


def get_risk_parity_trend_from_db(
    option="month_end",
    start=None,
    end=None,
    timeframe="1d",
    tickers=None,
):
    if tickers is None:
        tickers = ['SPY','TLT','GLD','IEF','LQD']

    engine = (
        BacktestEngine(tickers, period="db", option=option)
        .load_ohlcv_from_db(start=start, end=end, timeframe=timeframe)
        .add_ma(200)
        .filter_by_period()
        .align_dates()
        .slice(start=start, end=end)
        .drop_columns(["High","Low","Open","Volume"])
    )

    strategy = RiskParityTrendStrategy(
        start_balance=10000,
        rebalance_interval=1,
        vol_window=6,
        filter_ma="MA200",
    )

    df = engine.run(strategy).round_columns(
        cols=["Cash","Total Balance","End Balance","Next Balance"],
        decimals=1
    ).result

    return df


def get_dual_momentum(period="15y", option="month_end", start=None):
    # 공격형: 주식/테크 승자추종 + 하락시 현금(BIL) 회피
    tickers = ["QQQ", "SPY", "IWM", "SOXX", "BIL"]

    engine = (
        BacktestEngine(tickers, period=period, option=option)
        .load_ohlcv()
        .add_ma(200)
        .filter_by_period()
        .add_interval_returns([12])   # ✅ 12MReturn 생성
        .align_dates()
        .slice(start=start)
        .drop_columns(["High","Low","Open","Volume"])
    )

    strategy = DualMomentumStrategy(
        start_balance=10000,
        top=1,                    # ✅ 가장 강한 1개에 집중(공격적)
        lookback_col="12MReturn",
        filter_ma="MA200",
        rebalance_interval=1,      # 월 1회 리밸런싱(월말 데이터 기준)
        cash_ticker="BIL",         # ✅ 현금이 아니라 단기채로 현금 수익 반영
    )

    df = engine.run(strategy).round_columns().round_columns(cols=["Total Return"], decimals=3).result
    return df


def get_dual_momentum_from_db(
    option="month_end",
    start=None,
    end=None,
    timeframe="1d",
    tickers=None,
):
    if tickers is None:
        tickers = ["QQQ", "SPY", "IWM", "SOXX", "BIL"]

    engine = (
        BacktestEngine(tickers, period="db", option=option)
        .load_ohlcv_from_db(start=start, end=end, timeframe=timeframe)
        .add_ma(200)
        .filter_by_period()
        .add_interval_returns([12])
        .align_dates()
        .slice(start=start, end=end)
        .drop_columns(["High","Low","Open","Volume"])
    )

    strategy = DualMomentumStrategy(
        start_balance=10000,
        top=1,
        lookback_col="12MReturn",
        filter_ma="MA200",
        rebalance_interval=1,
        cash_ticker="BIL",
    )

    df = engine.run(strategy).round_columns().round_columns(cols=["Total Return"], decimals=3).result
    return df


def portfolio_sample():
    """
        쉽계 사용하기 위해 미리만들어 놓음
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
        DB 기반 전략 샘플 포트폴리오
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
