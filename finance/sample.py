from IPython.display import display
from .engine import BacktestEngine
from .strategy import (
    EqualWeightStrategy,
    GTAA3Strategy
)

from .performance import(
    portfolio_performance_summary
)

from .visualize import(
    plot_equity_curves
)

from finance.data.asset_profile import(
    collect_and_store_asset_profiles
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


def run_sample():
    """
        쉽계 사용하기 위해 미리만들어 놓음
    """
    period = "15y"
    option = "month_end"
    start = "2015-12-01"
    freq = "M"

    results = {
        "Equal Weight": get_equal_weight(period=period, option=option, start=start),
        "GTAA": get_gtaa3(period=period, option=option, start=start),
    }

    display(results['GTAA'])
    plot_equity_curves(results, "Equity Curve Comparison")
    for key, df in results.items():
        display(portfolio_performance_summary(df, key, freq))



def load_sample():
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


