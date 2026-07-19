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
    months: int = 120,
    *,
    query_fn: QueryFn | None = None,
) -> pd.DataFrame:
    """Load five display years plus the rolling-multiple warmup from finance_meta."""
    limit = max(1, int(months))
    rows = _query_meta(
        """
        SELECT observation_month, spx_level, trailing_eps, trailing_pe, cape,
               data_quality, source, source_ref, source_version, collected_at
        FROM sp500_monthly_valuation
        WHERE spx_level > 0
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
          AND source_release_date <= CURRENT_DATE()
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


def load_sp500_actual_eps_history(
    *,
    quarter_count: int = 8,
    end_date: object = None,
    query_fn: QueryFn | None = None,
) -> dict[str, Any]:
    """Return strict current/prior TTM growth from eight actual S&P quarters."""
    limit = max(8, int(quarter_count))
    if end_date is None:
        end_clause = (
            "AND period_end <= CURRENT_DATE() "
            "AND source_release_date <= CURRENT_DATE()"
        )
        params: tuple[Any, ...] = ()
    else:
        end_clause = "AND period_end <= %s AND source_release_date <= %s"
        as_of_date = str(end_date)[:10]
        params = (as_of_date, as_of_date)
    rows = _query_meta(
        f"""
        SELECT period_end, eps, source, source_ref, source_release_date, collected_at
        FROM sp500_index_earnings
        WHERE period_type = 'quarterly'
          AND earnings_basis = 'as_reported'
          AND value_status = 'actual'
          AND eps > 0
          {end_clause}
        ORDER BY period_end DESC, source_release_date DESC
        """,
        params,
        query_fn=query_fn,
    )
    frame = pd.DataFrame(rows)
    if frame.empty:
        return {
            "status": "INSUFFICIENT_HISTORY",
            "quarter_count": 0,
            "current_ttm_eps": None,
            "prior_ttm_eps": None,
            "growth_pct": None,
            "latest_period_end": None,
            "latest_release_date": None,
            "quarters": [],
            "source_basis": "S&P official actual as-reported EPS",
        }
    frame["period_end"] = pd.to_datetime(frame["period_end"], errors="coerce")
    if "source_release_date" in frame:
        frame["source_release_date"] = pd.to_datetime(
            frame["source_release_date"], errors="coerce"
        )
    else:
        frame["source_release_date"] = pd.NaT
    frame["eps"] = pd.to_numeric(frame["eps"], errors="coerce")
    frame = (
        frame.dropna(subset=["period_end", "eps"])
        .sort_values(["period_end", "source_release_date"], ascending=False)
        .drop_duplicates("period_end", keep="first")
        .head(limit)
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
    result: dict[str, Any] = {
        "status": "INSUFFICIENT_HISTORY",
        "quarter_count": len(quarters),
        "current_ttm_eps": None,
        "prior_ttm_eps": None,
        "growth_pct": None,
        "latest_period_end": quarters[0]["period_end"] if quarters else None,
        "latest_release_date": (
            quarters[0]["source_release_date"] if quarters else None
        ),
        "quarters": quarters,
        "source_basis": "S&P official actual as-reported EPS",
    }
    if len(quarters) < 8:
        return result
    current_ttm = sum(row["eps"] for row in quarters[:4])
    prior_ttm = sum(row["eps"] for row in quarters[4:8])
    growth = (current_ttm / prior_ttm - 1.0) * 100.0 if prior_ttm > 0 else None
    return {
        **result,
        "status": "READY" if growth is not None else "INSUFFICIENT_HISTORY",
        "current_ttm_eps": current_ttm,
        "prior_ttm_eps": prior_ttm,
        "growth_pct": growth,
    }


def load_latest_shiller_ttm_eps(
    *,
    query_fn: QueryFn | None = None,
) -> dict[str, Any]:
    """Load the latest positive Shiller interpolated TTM EPS observation."""
    rows = _query_meta(
        """
        SELECT observation_month, trailing_eps, data_quality, source, source_ref,
               source_version, collected_at
        FROM sp500_monthly_valuation
        WHERE trailing_eps > 0
          AND source = %s
        ORDER BY observation_month DESC
        LIMIT 1
        """,
        ("robert_shiller_irrational_exuberance",),
        query_fn=query_fn,
    )
    frame = pd.DataFrame(rows)
    if frame.empty:
        return {
            "status": "INSUFFICIENT_HISTORY",
            "current_ttm_eps": None,
            "eps_source": "Robert Shiller TTM EPS",
            "eps_source_quality": "interpolated_ttm_proxy",
            "eps_basis_date": None,
            "fallback_reason": None,
        }
    row = frame.iloc[0]
    basis_date = pd.to_datetime(row.get("observation_month"), errors="coerce")
    eps = pd.to_numeric(row.get("trailing_eps"), errors="coerce")
    if pd.isna(basis_date) or pd.isna(eps) or float(eps) <= 0:
        return {
            "status": "INSUFFICIENT_HISTORY",
            "current_ttm_eps": None,
            "eps_source": "Robert Shiller TTM EPS",
            "eps_source_quality": "interpolated_ttm_proxy",
            "eps_basis_date": None,
            "fallback_reason": None,
        }
    return {
        "status": "READY",
        "current_ttm_eps": float(eps),
        "ttm_eps": float(eps),
        "eps_source": "Robert Shiller TTM EPS",
        "eps_source_quality": "interpolated_ttm_proxy",
        "eps_basis_date": pd.Timestamp(basis_date).strftime("%Y-%m-%d"),
        "fallback_reason": None,
        "value_status": "interpolated",
        "basis": "sp500_four_quarter_total_interpolated",
        "source": row.get("source"),
        "source_ref": row.get("source_ref"),
        "data_quality": row.get("data_quality") or "interpolated",
    }


def resolve_sp500_ttm_eps(
    *,
    official_evidence: dict[str, Any] | None = None,
    shiller_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Prefer official actual EPS and fall back transparently to Shiller TTM EPS."""
    official = (
        dict(official_evidence)
        if official_evidence is not None
        else load_latest_sp500_ttm_actual_eps()
    )
    official_eps = float(official.get("ttm_eps") or 0)
    if (
        official.get("status") == "READY"
        and official.get("value_status") == "actual"
        and official_eps > 0
    ):
        return {
            **official,
            "current_ttm_eps": official_eps,
            "eps_source": "S&P 공식 실제 EPS",
            "eps_source_quality": "official_actual",
            "eps_basis_date": official.get("latest_period_end"),
            "fallback_reason": None,
        }

    shiller = (
        dict(shiller_evidence)
        if shiller_evidence is not None
        else load_latest_shiller_ttm_eps()
    )
    shiller_eps = float(shiller.get("current_ttm_eps") or shiller.get("ttm_eps") or 0)
    if shiller.get("status") == "READY" and shiller_eps > 0:
        return {
            **shiller,
            "current_ttm_eps": shiller_eps,
            "ttm_eps": shiller_eps,
            "eps_source": "Robert Shiller TTM EPS",
            "eps_source_quality": "interpolated_ttm_proxy",
            "fallback_reason": (
                "S&P 공식 actual EPS가 완료된 4개 분기 기준으로 준비되지 않아 "
                "Robert Shiller TTM EPS를 사용합니다."
            ),
            "official_evidence": official,
        }

    return {
        "status": "INSUFFICIENT_HISTORY",
        "current_ttm_eps": None,
        "ttm_eps": None,
        "eps_source": None,
        "eps_source_quality": "unavailable",
        "eps_basis_date": None,
        "fallback_reason": (
            "S&P 공식 actual EPS와 Robert Shiller TTM EPS가 모두 준비되지 않았습니다."
        ),
        "official_evidence": official,
        "shiller_evidence": shiller,
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


def load_fomc_sep_projection_history(
    *,
    query_fn: QueryFn | None = None,
) -> pd.DataFrame:
    """Load all stored GDP/PCE SEP release vintages for PIT reconstruction."""
    rows = _query_meta(
        """
        SELECT release_date, target_year, variable_name, statistic_name,
               value_pct, source, source_ref, collected_at
        FROM fomc_sep_projection
        ORDER BY release_date, target_year, variable_name, statistic_name
        """,
        (),
        query_fn=query_fn,
    )
    frame = pd.DataFrame(rows)
    if not frame.empty:
        frame["release_date"] = pd.to_datetime(frame["release_date"], errors="coerce")
    return frame
