from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

import pandas as pd

from finance.data.nasdaq100_valuation import derive_filing_aware_ttm_eps


def split_factor_between(
    price_rows: Iterable[Mapping[str, Any]],
    *,
    after: str | pd.Timestamp,
    through: str | pd.Timestamp,
) -> float:
    """Return only splits known after a fact and through the valuation cutoff."""
    frame = pd.DataFrame([dict(row) for row in price_rows])
    if frame.empty or not {"date", "stock_splits"}.issubset(frame.columns):
        return 1.0
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame["stock_splits"] = pd.to_numeric(frame["stock_splits"], errors="coerce")
    start = pd.to_datetime(after, errors="coerce")
    end = pd.to_datetime(through, errors="coerce")
    if pd.isna(start) or pd.isna(end):
        return 1.0
    events = frame.loc[
        frame["date"].notna()
        & (frame["date"] > pd.Timestamp(start))
        & (frame["date"] <= pd.Timestamp(end))
        & frame["stock_splits"].notna()
        & (frame["stock_splits"] > 0),
        "stock_splits",
    ]
    if events.empty:
        return 1.0
    return float(events.product())


def _price_frame(price_rows: list[dict[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame(price_rows)
    if frame.empty or not {"date", "close"}.issubset(frame.columns):
        return pd.DataFrame(columns=["symbol", "date", "close", "stock_splits"])
    if "symbol" not in frame:
        frame["symbol"] = None
    if "stock_splits" not in frame:
        frame["stock_splits"] = 0.0
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
    frame["stock_splits"] = pd.to_numeric(frame["stock_splits"], errors="coerce").fillna(0.0)
    return (
        frame.dropna(subset=["date"])
        .sort_values(["symbol", "date"], na_position="first")
        .drop_duplicates(["symbol", "date"], keep="last")
        .reset_index(drop=True)
    )


def build_monthly_pit_valuation(
    statement_rows: Iterable[Mapping[str, Any]],
    price_rows: Iterable[Mapping[str, Any]],
    *,
    start_month: str,
    end_month: str,
) -> list[dict[str, Any]]:
    """Build explicit calendar-month rows without interpolating price or EPS."""
    statements = [dict(row) for row in statement_rows]
    prices = [dict(row) for row in price_rows]
    price_frame = _price_frame(prices)
    start = pd.Timestamp(start_month).to_period("M").to_timestamp()
    end = pd.Timestamp(end_month).to_period("M").to_timestamp()
    symbols = {
        str(row.get("symbol") or "").strip().upper()
        for row in statements + prices
        if str(row.get("symbol") or "").strip()
    }
    symbol = sorted(symbols)[0] if symbols else ""
    rows: list[dict[str, Any]] = []

    for month in pd.date_range(start, end, freq="MS"):
        month_end = month + pd.offsets.MonthEnd(0)
        month_prices = price_frame.loc[
            (price_frame["date"] >= month)
            & (price_frame["date"] <= month_end)
            & price_frame["close"].notna()
            & (price_frame["close"] > 0)
        ]
        if symbol:
            month_prices = month_prices.loc[
                month_prices["symbol"].astype(str).str.upper() == symbol
            ]
        price_row = month_prices.iloc[-1] if not month_prices.empty else None
        price = float(price_row["close"]) if price_row is not None else None
        price_basis_date = (
            pd.Timestamp(price_row["date"]).strftime("%Y-%m-%d")
            if price_row is not None
            else None
        )

        resolved = derive_filing_aware_ttm_eps(
            statements,
            as_of_date=month_end.strftime("%Y-%m-%d"),
        )
        evidence = resolved.get(symbol) if symbol else None
        quarters = list((evidence or {}).get("quarters") or [])
        adjusted_quarters: list[dict[str, Any]] = []
        for quarter in quarters:
            factor = split_factor_between(
                prices,
                after=str(quarter["available_at"]),
                through=month_end,
            )
            adjusted_quarters.append(
                {
                    **quarter,
                    "raw_eps": float(quarter["eps"]),
                    "eps": float(quarter["eps"]) / factor,
                    "split_factor": factor,
                }
            )
        ttm_eps = (
            sum(float(quarter["eps"]) for quarter in adjusted_quarters)
            if len(adjusted_quarters) == 4
            else None
        )
        eps_basis_date = (
            max(str(quarter["available_at"]) for quarter in adjusted_quarters)
            if adjusted_quarters
            else None
        )
        split_factor = (
            max(float(quarter["split_factor"]) for quarter in adjusted_quarters)
            if adjusted_quarters
            else 1.0
        )

        if price is None:
            quality = "missing_price"
        elif ttm_eps is None:
            quality = "insufficient_eps"
        elif ttm_eps <= 0:
            quality = "non_positive_eps"
        else:
            quality = "complete"
        trailing_pe = (
            price / ttm_eps
            if price is not None and ttm_eps is not None and ttm_eps > 0
            else None
        )
        rows.append(
            {
                "symbol": symbol or None,
                "month": month.strftime("%Y-%m-%d"),
                "price": price,
                "price_basis_date": price_basis_date,
                "ttm_eps": ttm_eps,
                "eps_basis_date": eps_basis_date,
                "trailing_pe": trailing_pe,
                "quarter_ends": [str(quarter["period_end"]) for quarter in adjusted_quarters],
                "quarters": adjusted_quarters,
                "split_factor": split_factor,
                "quality": quality,
            }
        )
    return rows
