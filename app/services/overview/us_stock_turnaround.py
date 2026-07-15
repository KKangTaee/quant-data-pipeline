from __future__ import annotations

import math
from collections.abc import Mapping
from datetime import date, datetime
from typing import Any

import pandas as pd

from finance.data.us_stock_turnaround import build_turnaround_analysis
from finance.loaders.us_stock_turnaround import (
    build_us_stock_turnaround_collection_plan,
    load_us_stock_turnaround_inputs,
)


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, (pd.Timestamp, datetime, date)):
        return value.isoformat()[:10]
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if hasattr(value, "item"):
        return _json_safe(value.item())
    return str(value)


def _empty(status: str, reason: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema_version": "us_stock_turnaround_v1",
        "status": status,
        "selection": None,
        "series": {"status": "BLOCKED", "timeline": [], "series": []},
        "milestones": {"status": "BLOCKED", "items": {}},
        "risks": {"status": "BLOCKED"},
        "valuation": {"status": "BLOCKED", "multiple": None},
        "sections": {},
        "sources": [],
        "limitations": [],
    }
    if reason:
        result["reason"] = reason
    return result


def _collection_action(plan: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": "collect_us_stock_turnaround",
        "label": "분석 자료 수집",
        "detail": "선택한 한 종목의 누락 profile, 가격, SEC 재무제표만 동기 수집합니다.",
        "symbol": plan.get("symbol"),
        "cik": dict(plan.get("identity") or {}).get("cik"),
        "scopes": list(plan.get("scopes") or []),
        "missing_ranges": dict(plan.get("missing_ranges") or {}),
        "missing_concepts": list(plan.get("missing_concepts") or []),
        "enabled": True,
    }


def build_us_stock_turnaround_read_model(
    *,
    selected_symbol: str | None,
    loaded_inputs: Mapping[str, Any] | None = None,
    per_model: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a JSON-safe, DB-only turnaround model for one selected stock."""
    symbol = str(selected_symbol or "").strip().upper()
    if not symbol:
        return _empty("NOT_SELECTED")
    try:
        inputs = dict(loaded_inputs or load_us_stock_turnaround_inputs(symbol))
        identity = inputs.get("identity")
        if not isinstance(identity, Mapping) or str(identity.get("symbol") or "").strip().upper() != symbol:
            return _empty("ERROR", "선택 ticker와 DB identity가 일치하지 않습니다.")
        per_multiple = dict((per_model or {}).get("multiple_regime") or {})
        per_status = str(per_multiple.get("status") or (per_model or {}).get("status") or "BLOCKED")
        window = dict(inputs.get("window") or {})
        analysis = build_turnaround_analysis(
            statement_rows=inputs.get("statement_rows") or [],
            price_rows=inputs.get("price_rows") or [],
            profile=dict(inputs.get("profile") or {}),
            latest_price=inputs.get("latest_price"),
            per_status=per_status,
            as_of_date=str(window.get("as_of_date") or pd.Timestamp.now().strftime("%Y-%m-%d")),
        )
        plan = build_us_stock_turnaround_collection_plan(symbol, loaded_inputs={**inputs, "analysis": analysis})
        if plan.get("status") in {"ERROR", "NOT_APPLICABLE"}:
            status = str(plan["status"])
        elif plan.get("status") == "COLLECTABLE":
            status = "COLLECTABLE"
        else:
            status = str(analysis.get("status") or "PARTIAL")
        model = {
            "schema_version": "us_stock_turnaround_v1",
            "status": status,
            "selection": dict(identity),
            **analysis,
            "status": status,
            "coverage": dict(inputs.get("coverage") or {}),
            "collection_plan": plan,
            "sources": [
                "finance_fundamental.nyse_financial_statement_values",
                "finance_price.nyse_price_history",
                "finance_meta.nyse_asset_profile",
            ],
            "limitations": [
                "target price, peer fair multiple, buy/sell signal을 제공하지 않습니다.",
                "누락 분기는 연결하거나 보간하지 않습니다.",
            ],
        }
        if plan.get("status") == "COLLECTABLE":
            model["collection_action"] = _collection_action(plan)
        return _json_safe(model)
    except Exception as exc:
        return _empty("ERROR", f"{type(exc).__name__}: {exc}")
