from __future__ import annotations

from typing import Any

import pytest


def test_daily_loader_selects_finalization_columns() -> None:
    from app.services.futures_macro_daily_loader import (
        load_futures_macro_daily_rows,
    )

    captured: list[str] = []

    def query(_database: str, sql: str, _params: list[Any]) -> list[dict[str, Any]]:
        captured.append(sql)
        return []

    load_futures_macro_daily_rows(query, symbols=("ES=F",), lookback_days=30)

    assert len(captured) == 1
    assert "final_open" in captured[0]
    assert "finalization_basis" in captured[0]
    assert "finalized_at" in captured[0]


def test_daily_loader_retries_unknown_columns_with_null_projection() -> None:
    from app.services.futures_macro_daily_loader import (
        load_futures_macro_daily_rows,
    )

    captured: list[str] = []

    def query(_database: str, sql: str, _params: list[Any]) -> list[dict[str, Any]]:
        captured.append(sql)
        if len(captured) == 1:
            raise RuntimeError("Unknown column 'final_open' in 'field list'")
        return [{"provider_symbol": "ES=F", "final_open": None}]

    rows = load_futures_macro_daily_rows(
        query,
        symbols=("ES=F",),
        lookback_days=30,
    )

    assert rows == [{"provider_symbol": "ES=F", "final_open": None}]
    assert len(captured) == 2
    assert "NULL AS final_open" in captured[1]
    assert "NULL AS finalized_at" in captured[1]


def test_daily_loader_does_not_mask_non_schema_errors() -> None:
    from app.services.futures_macro_daily_loader import (
        load_futures_macro_daily_rows,
    )

    def query(_database: str, _sql: str, _params: list[Any]) -> list[dict[str, Any]]:
        raise RuntimeError("connection refused")

    with pytest.raises(RuntimeError, match="connection refused"):
        load_futures_macro_daily_rows(
            query,
            symbols=("ES=F",),
            lookback_days=30,
        )
