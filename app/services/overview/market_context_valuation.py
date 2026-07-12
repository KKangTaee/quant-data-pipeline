from __future__ import annotations

from typing import Any, Callable

from app.services.overview.nasdaq100_valuation import build_nasdaq100_valuation_read_model
from app.services.overview.sp500_valuation import build_sp500_valuation_read_model


SP500_INSTRUMENT = {
    "id": "sp500", "label": "S&P 500", "proxy_symbol": "SPX / SPY",
    "price_label": "SPX 지수", "multiple_label": "후행 PER", "method_label": "지수 직접 기준",
}


def _isolated(builder: Callable[[], dict[str, Any]], instrument: dict[str, Any]) -> dict[str, Any]:
    try:
        model = dict(builder())
        model.setdefault("instrument", dict(instrument))
        return model
    except Exception as exc:
        return {
            "status": "ERROR",
            "instrument": dict(instrument),
            "reason": f"{type(exc).__name__}: {exc}",
            "multiple_regime": {"status": "ERROR", "series": []},
            "earnings_scenario": {"status": "ERROR"},
            "index_scenario": {"status": "ERROR", "history_options": {}},
            "sources": [], "limitations": [],
        }


def build_market_context_valuation_read_model() -> dict[str, Any]:
    """Load each instrument independently so one provider gap cannot blank the other."""
    return {
        "schema_version": "market_context_valuation_v2",
        "default_instrument": "sp500",
        "instruments": {
            "sp500": _isolated(build_sp500_valuation_read_model, SP500_INSTRUMENT),
            "nasdaq100": _isolated(build_nasdaq100_valuation_read_model, {
                "id": "nasdaq100", "label": "Nasdaq-100", "proxy_symbol": "QQQ",
                "price_label": "QQQ 가격", "multiple_label": "재구성 후행 PER", "method_label": "QQQ 보유종목 기반",
            }),
        },
    }
