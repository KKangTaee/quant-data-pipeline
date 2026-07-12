from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pandas as pd

from finance.data.db.mysql import MySQLClient


QueryFn = Callable[[str, tuple[Any, ...]], list[dict[str, Any]]]
DB_META = "finance_meta"


def _query_meta(
    sql: str,
    params: tuple[Any, ...],
    *,
    query_fn: QueryFn | None,
) -> list[dict[str, Any]]:
    if query_fn is not None:
        return list(query_fn(sql, params))
    db = MySQLClient("localhost", "root", "1234", 3306)
    try:
        db.use_db(DB_META)
        return db.query(sql, params)
    finally:
        db.close()


def load_nasdaq100_monthly_valuation(
    months: int = 120,
    *,
    proxy_symbol: str = "QQQ",
    query_fn: QueryFn | None = None,
) -> pd.DataFrame:
    """Load monthly QQQ proxy history, including coverage-blocked observations."""
    limit = max(1, int(months))
    symbol = str(proxy_symbol or "QQQ").strip().upper()
    rows = _query_meta(
        """
        SELECT observation_month, proxy_symbol, qqq_price,
               reconstructed_ttm_eps, trailing_pe, earnings_yield,
               coverage_weight_pct, unmapped_weight_pct,
               holding_snapshot_date, holding_snapshot_quality,
               earnings_available_through, price_basis_date, data_quality,
               source, source_ref, collected_at, error_msg
        FROM nasdaq100_monthly_valuation
        WHERE proxy_symbol = %s
        ORDER BY observation_month DESC
        LIMIT %s
        """,
        (symbol, limit),
        query_fn=query_fn,
    )
    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame
    frame["observation_month"] = pd.to_datetime(
        frame["observation_month"], errors="coerce"
    )
    return frame.dropna(subset=["observation_month"]).sort_values(
        "observation_month"
    ).reset_index(drop=True)


def load_latest_nasdaq100_ttm_proxy(
    *,
    proxy_symbol: str = "QQQ",
    query_fn: QueryFn | None = None,
) -> dict[str, Any]:
    """Return the latest reconstruction plus the evidence behind a blocked gate."""
    symbol = str(proxy_symbol or "QQQ").strip().upper()
    rows = _query_meta(
        """
        SELECT observation_month, proxy_symbol, qqq_price,
               reconstructed_ttm_eps, trailing_pe, earnings_yield,
               coverage_weight_pct, unmapped_weight_pct,
               holding_snapshot_date, holding_snapshot_quality,
               earnings_available_through, price_basis_date, data_quality,
               source, source_ref, collected_at, error_msg
        FROM nasdaq100_monthly_valuation
        WHERE proxy_symbol = %s
        ORDER BY observation_month DESC
        LIMIT 1
        """,
        (symbol,),
        query_fn=query_fn,
    )
    if not rows:
        return {
            "status": "INSUFFICIENT_HISTORY",
            "proxy_symbol": symbol,
            "current_ttm_eps": None,
            "coverage_weight_pct": None,
            "unmapped_weight_pct": None,
            "error_code": "NO_MONTHLY_VALUATION",
        }
    row = dict(rows[0])
    quality = str(row.get("data_quality") or "").lower()
    value = pd.to_numeric(row.get("reconstructed_ttm_eps"), errors="coerce")
    ready = quality == "reconstructed_actual" and not pd.isna(value)
    return {
        **row,
        "status": "READY" if ready else "BLOCKED",
        "current_ttm_eps": float(value) if ready else None,
        "ttm_eps": float(value) if ready else None,
        "error_code": row.get("error_msg") or (None if ready else "INSUFFICIENT_EARNINGS_COVERAGE"),
        "eps_source": "QQQ SEC holdings + constituent SEC actual diluted EPS",
        "eps_source_quality": quality or "blocked",
        "eps_basis_date": row.get("earnings_available_through"),
    }
