from __future__ import annotations

from typing import Any, Callable

from app.services.overview.sp500_valuation import build_sp500_valuation_read_model
from app.services.overview.us_stock_freshness import build_us_stock_data_freshness
from app.services.overview.us_stock_turnaround import (
    build_us_stock_turnaround_read_model,
)
from app.services.overview.us_stock_valuation import build_us_stock_valuation_read_model

SP500_INSTRUMENT = {
    "id": "sp500",
    "label": "S&P 500",
    "proxy_symbol": "SPX / SPY",
    "price_label": "SPX 지수",
    "multiple_label": "후행 PER",
    "method_label": "지수 직접 기준",
}


def _isolated(
    builder: Callable[[], dict[str, Any]], instrument: dict[str, Any]
) -> dict[str, Any]:
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
            "sources": [],
            "limitations": [],
        }


def build_market_context_valuation_read_model(
    *,
    selected_symbol: str | None = None,
    search_query: str | None = None,
    default_instrument: str | None = None,
    show_instrument_selector: bool = True,
) -> dict[str, Any]:
    """Load each instrument independently so one provider gap cannot blank the other."""
    if default_instrument not in {None, "sp500", "us_stock"}:
        raise ValueError(f"Unsupported default instrument: {default_instrument}")
    selected_ids = (
        ("sp500", "us_stock") if default_instrument is None else (default_instrument,)
    )
    instruments: dict[str, dict[str, Any]] = {}
    if "sp500" in selected_ids:
        instruments["sp500"] = _isolated(
            build_sp500_valuation_read_model, SP500_INSTRUMENT
        )
    if "us_stock" in selected_ids:
        stock_per = _isolated(
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
        )
        try:
            turnaround = dict(
                build_us_stock_turnaround_read_model(
                    selected_symbol=selected_symbol,
                    per_model=stock_per,
                )
            )
        except Exception as exc:
            turnaround = {
                "schema_version": "us_stock_turnaround_v1",
                "status": "ERROR",
                "reason": f"{type(exc).__name__}: {exc}",
                "selection": None,
                "series": {"status": "BLOCKED", "timeline": [], "series": []},
                "sections": {},
            }
        multiple = dict(stock_per.get("multiple_regime") or {})
        current_pe = multiple.get("current_pe")
        per_ready = (
            str(multiple.get("status") or "") == "READY"
            and isinstance(current_pe, (int, float))
            and float(current_pe) > 0
        )
        instruments["us_stock"] = {
            **stock_per,
            "turnaround_analysis": turnaround,
            "data_freshness": build_us_stock_data_freshness(
                selected_symbol or "",
                per_model=stock_per,
                turnaround_model=turnaround,
            ),
            "recommended_analysis": (
                "per" if per_ready else "turnaround" if selected_symbol else None
            ),
        }
    return {
        "schema_version": "market_context_valuation_v5",
        "default_instrument": default_instrument or "sp500",
        "show_instrument_selector": bool(show_instrument_selector),
        "instruments": instruments,
    }
