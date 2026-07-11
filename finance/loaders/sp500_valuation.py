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


def load_sp500_monthly_valuation(
    months: int = 72,
    *,
    query_fn: QueryFn | None = None,
) -> pd.DataFrame:
    """Load the latest monthly Shiller price/EPS observations from finance_meta."""
    limit = max(1, int(months))
    rows = _query_meta(
        """
        SELECT observation_month, spx_level, trailing_eps, trailing_pe, cape,
               data_quality, source, source_ref, source_version, collected_at
        FROM sp500_monthly_valuation
        WHERE trailing_pe > 0 AND spx_level > 0 AND trailing_eps > 0
        ORDER BY observation_month DESC
        LIMIT %s
        """,
        (limit,),
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


def load_latest_sp500_ttm_actual_eps(
    *,
    query_fn: QueryFn | None = None,
) -> dict[str, Any]:
    """Sum the latest four distinct completed actual As-Reported EPS quarters."""
    rows = _query_meta(
        """
        SELECT period_end, eps, source, source_ref, source_release_date, collected_at
        FROM sp500_index_earnings
        WHERE period_type = 'quarterly'
          AND earnings_basis = 'as_reported'
          AND value_status = 'actual'
          AND eps > 0
          AND period_end <= CURRENT_DATE()
        ORDER BY period_end DESC, source_release_date DESC
        """,
        (),
        query_fn=query_fn,
    )
    frame = pd.DataFrame(rows)
    if frame.empty:
        return {
            "status": "INSUFFICIENT_HISTORY",
            "quarter_count": 0,
            "ttm_eps": None,
            "value_status": "actual",
            "basis": "as_reported",
            "quarters": [],
        }
    frame["period_end"] = pd.to_datetime(frame["period_end"], errors="coerce")
    frame["source_release_date"] = pd.to_datetime(
        frame.get("source_release_date"), errors="coerce"
    )
    frame["eps"] = pd.to_numeric(frame["eps"], errors="coerce")
    frame = (
        frame.dropna(subset=["period_end", "eps"])
        .sort_values(["period_end", "source_release_date"], ascending=False)
        .drop_duplicates("period_end", keep="first")
        .head(4)
    )
    quarters = [
        {
            "period_end": row.period_end.strftime("%Y-%m-%d"),
            "eps": float(row.eps),
            "source_release_date": (
                row.source_release_date.strftime("%Y-%m-%d")
                if not pd.isna(row.source_release_date)
                else None
            ),
        }
        for row in frame.itertuples()
    ]
    count = len(quarters)
    return {
        "status": "READY" if count == 4 else "INSUFFICIENT_HISTORY",
        "quarter_count": count,
        "ttm_eps": sum(row["eps"] for row in quarters) if count == 4 else None,
        "value_status": "actual",
        "basis": "as_reported",
        "quarters": quarters,
        "latest_period_end": quarters[0]["period_end"] if quarters else None,
        "latest_release_date": quarters[0]["source_release_date"] if quarters else None,
    }


def load_latest_fomc_sep_projection(
    *,
    query_fn: QueryFn | None = None,
) -> pd.DataFrame:
    """Load GDP/PCE observations belonging to the latest stored SEP vintage."""
    rows = _query_meta(
        """
        SELECT release_date, target_year, variable_name, statistic_name,
               value_pct, source, source_ref, collected_at
        FROM fomc_sep_projection
        WHERE release_date = (SELECT MAX(release_date) FROM fomc_sep_projection)
        ORDER BY target_year, variable_name, statistic_name
        """,
        (),
        query_fn=query_fn,
    )
    frame = pd.DataFrame(rows)
    if not frame.empty:
        frame["release_date"] = pd.to_datetime(frame["release_date"], errors="coerce")
    return frame
