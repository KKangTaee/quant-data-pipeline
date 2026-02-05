from .strategy import Strategy
from .display import (
    round_columns
)
from .data.data import (
    get_ohlcv
)
from .transform import (
    add_avg_score,
    add_ma,
    filter_ohlcv,
    select_rows_by_interval_with_ends,
    slice_ohlcv,
    align_dfs_by_date_intersection,
    drop_columns,
    add_interval_returns
)

class BacktestEngine:

    def __init__(self, tickers, period, option):
        self.tickers = tickers
        self.period = period
        self.option = option
        self.dfs = None
        self.result = None

    # =====================
    # Data
    # =====================
    def load_ohlcv(self):
        self.dfs = get_ohlcv(self.tickers, period=self.period)
        return self

    # =====================
    # Transform
    # =====================
    def add_ma(self, windows):
        self.dfs = add_ma(self.dfs, windows)
        return self

    def filter_by_period(self):
        self.dfs = filter_ohlcv(self.dfs, self.option)
        return self

    def align_dates(self):
        self.dfs = align_dfs_by_date_intersection(self.dfs)
        return self

    def slice(self, start=None, end=None):
        self.dfs = slice_ohlcv(self.dfs, start, end)
        return self

    def drop_columns(self, cols):
        self.dfs = drop_columns(self.dfs, cols)
        return self

    def add_interval_returns(self, intervals):
        self.dfs = add_interval_returns(self.dfs, intervals)
        return self

    def add_avg_score(self):
        self.dfs = add_avg_score(self.dfs)
        return self

    def interval(self, interval):
        self.dfs = select_rows_by_interval_with_ends(self.dfs, interval)
        return self

    # =====================
    # Strategy
    # =====================
    def run(self, strategy: Strategy):
        if self.dfs is None:
            raise ValueError("데이터가 로드되지 않았습니다.")
        self.result = strategy.run(self.dfs)
        return self

    # =====================
    # Display
    # =====================
    def round_columns(self, cols:list=["Close","Next Balance","End Balance","Total Balance"], decimals=1):
        self.result = round_columns(
            self.result,
            cols,
            decimals
        )
        return self