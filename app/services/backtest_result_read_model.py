from __future__ import annotations

from typing import Any

import pandas as pd


def data_trust_status_label(status: str | None) -> str:
    normalized = str(status or "").strip().lower()
    if normalized == "ok":
        return "OK"
    if normalized == "warning":
        return "Warning"
    if normalized == "error":
        return "Error"
    return "-"


def build_strategy_data_trust_rows(bundles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for bundle in bundles:
        meta = dict(bundle.get("meta") or {})
        result_df = bundle.get("result_df")
        price_freshness = dict(meta.get("price_freshness") or {})
        freshness_details = dict(price_freshness.get("details") or {})
        excluded_tickers = list(meta.get("excluded_tickers") or [])
        malformed_price_rows = list(meta.get("malformed_price_rows") or [])
        warnings = list(meta.get("warnings") or [])

        requested_end = meta.get("end") or meta.get("requested_end") or meta.get("input_end")
        actual_end = meta.get("actual_result_end")
        if not actual_end and isinstance(result_df, pd.DataFrame) and not result_df.empty and "Date" in result_df.columns:
            actual_end = str(pd.to_datetime(result_df["Date"], errors="coerce").max().date())
        actual_end_ts = pd.to_datetime(actual_end, errors="coerce")
        requested_end_ts = pd.to_datetime(requested_end, errors="coerce")
        result_period_shortened = (
            pd.notna(actual_end_ts)
            and pd.notna(requested_end_ts)
            and actual_end_ts.date() < requested_end_ts.date()
        )
        issue_count = len(excluded_tickers) + len(malformed_price_rows) + len(warnings)
        freshness_status = str(price_freshness.get("status") or "").strip().lower()

        if freshness_status in {"warning", "error"}:
            interpretation = "가격 최신성 확인 필요"
        elif excluded_tickers or malformed_price_rows:
            interpretation = "제외/결측 ticker 확인 필요"
        elif result_period_shortened:
            interpretation = "실제 결과 종료일이 요청 종료일보다 짧음"
        elif issue_count == 0:
            interpretation = "눈에 띄는 데이터 이슈 없음"
        else:
            interpretation = "주의사항 확인 필요"

        rows.append(
            {
                "Strategy": bundle.get("strategy_name") or meta.get("strategy_name") or "-",
                "Requested End": requested_end or "-",
                "Actual Result End": actual_end or "-",
                "Result Rows": meta.get("result_rows", len(result_df) if isinstance(result_df, pd.DataFrame) else "-"),
                "Price Freshness": data_trust_status_label(freshness_status),
                "Common Latest Price": freshness_details.get("common_latest_date") or "-",
                "Newest Latest Price": freshness_details.get("newest_latest_date") or "-",
                "Latest-Date Spread": (
                    f"{freshness_details.get('spread_days')}d"
                    if freshness_details.get("spread_days") is not None
                    else "-"
                ),
                "Excluded Tickers": len(excluded_tickers),
                "Malformed Tickers": len(malformed_price_rows),
                "Warnings": len(warnings),
                "Interpretation": interpretation,
            }
        )
    return rows


def build_monthly_component_balance_views(
    bundles: list[dict[str, Any]],
    *,
    strategy_names: list[str],
    weights: list[float],
    date_policy: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    monthly_balances = []
    for bundle, strategy_name in zip(bundles, strategy_names):
        result_df = bundle["result_df"].copy()
        result_df["Date"] = pd.to_datetime(result_df["Date"])
        result_df["_month"] = result_df["Date"].dt.to_period("M")
        monthly_df = result_df.groupby("_month", as_index=False).agg(TotalBalance=("Total Balance", "mean"))
        monthly_df["Date"] = monthly_df["_month"].dt.to_timestamp("M")
        monthly_df = monthly_df.drop(columns=["_month"]).set_index("Date").sort_index()
        monthly_balances.append(monthly_df.rename(columns={"TotalBalance": strategy_name}))

    join_how = "outer" if date_policy == "union" else "inner"
    balance_wide = pd.concat(monthly_balances, axis=1, join=join_how).sort_index()

    normalized_weights = pd.Series(weights, index=strategy_names, dtype=float)
    normalized_weights = normalized_weights / normalized_weights.sum()

    weight_frame = balance_wide.notna().mul(normalized_weights, axis=1)
    denominator = weight_frame.sum(axis=1).replace(0, pd.NA)
    contribution_amount = balance_wide.mul(normalized_weights, axis=1).div(denominator, axis=0)
    contribution_share = contribution_amount.div(contribution_amount.sum(axis=1), axis=0)

    return contribution_amount, contribution_share


__all__ = [
    "build_monthly_component_balance_views",
    "build_strategy_data_trust_rows",
    "data_trust_status_label",
]
