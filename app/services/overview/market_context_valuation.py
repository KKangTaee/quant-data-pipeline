from __future__ import annotations

from typing import Any, Callable

from app.services.overview.sp500_valuation import build_sp500_valuation_read_model
from app.services.overview.us_stock_valuation import build_us_stock_valuation_read_model


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


def build_market_context_valuation_read_model(
    *,
    selected_symbol: str | None = None,
    search_query: str | None = None,
) -> dict[str, Any]:
    """Load each instrument independently so one provider gap cannot blank the other."""
    return {
        "schema_version": "market_context_valuation_v3",
        "default_instrument": "sp500",
        "instruments": {
            "sp500": _isolated(build_sp500_valuation_read_model, SP500_INSTRUMENT),
            "us_stock": _isolated(
                lambda: build_us_stock_valuation_read_model(
                    selected_symbol=selected_symbol,
                    search_query=search_query,
                ),
                {
                    "id": "us_stock",
                    "label": "미국 개별주식",
                    "proxy_symbol": None,
                    "price_label": "선택 종목 주가",
                    "multiple_label": "후행 PER",
                    "method_label": "기업 자체 이력 기반",
                },
            ),
        },
    }
