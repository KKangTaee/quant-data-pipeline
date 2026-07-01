from __future__ import annotations

import app.runtime.backtest.real_money as _real_money
import app.runtime.backtest.runners.price_common as _price_common
import app.runtime.backtest.runners.risk_on_momentum as _risk_on_momentum
import app.runtime.backtest.runners.strict_factor as _strict_factor
from app.runtime.backtest.common import BacktestDataError, BacktestInputError
from app.runtime.backtest.result_bundle import build_backtest_result_bundle
from app.runtime.backtest.runners.dual_momentum import run_dual_momentum_backtest_from_db
from app.runtime.backtest.runners.equal_weight import run_equal_weight_backtest_from_db
from app.runtime.backtest.runners.global_relative_strength import run_global_relative_strength_backtest_from_db
from app.runtime.backtest.runners.gtaa import run_gtaa_backtest_from_db
from app.runtime.backtest.runners.risk_parity_trend import run_risk_parity_trend_backtest_from_db


for _module in (_real_money, _risk_on_momentum, _strict_factor, _price_common):
    for _name in dir(_module):
        if not _name.startswith("__"):
            globals()[_name] = getattr(_module, _name)


__all__ = [name for name in globals() if not name.startswith("__")]
