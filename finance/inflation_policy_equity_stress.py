"""Point-in-time S&P 500 EPS and multiple stress analysis."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from datetime import date, datetime, timezone

import pandas as pd


PANEL_COLUMNS = (
    "origin_date",
    "eps_source_release_date",
    "target_eps_year",
    "current_index_level",
    "forward_eps",
    "forward_multiple",
    "measured_next_year_eps_revision_pct",
    "months_to_year_end",
    "dgs2_pct",
    "dgs10_pct",
    "real_yield_10y_pct",
    "breakeven_10y_pct",
    "policy_repricing_bp",
    "dgs10_change_bp",
    "real_yield_change_bp",
    "breakeven_change_bp",
    "future_index_level",
    "future_forward_eps",
    "future_forward_multiple",
    "eps_change_pct",
    "multiple_change_pct",
    "index_change_pct",
)


def _timestamp(value: object, *, field: str) -> pd.Timestamp:
    try:
        parsed = pd.Timestamp(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field}: {value!r}") from exc
    if pd.isna(parsed):
        raise ValueError(f"Invalid {field}: {value!r}")
    if parsed.tzinfo is not None:
        parsed = parsed.tz_convert("UTC").tz_localize(None)
    return parsed.normalize()


def _finite(value: object, *, field: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be finite") from exc
    if not math.isfinite(parsed):
        raise ValueError(f"{field} must be finite")
    return parsed


def _price_frame(
    rows: Sequence[Mapping[str, object]], *, as_of: pd.Timestamp
) -> pd.DataFrame:
    normalized: list[dict[str, object]] = []
    for raw in rows:
        date_value = raw.get("Date", raw.get("date", raw.get("observation_date")))
        close_value = raw.get("Close", raw.get("close", raw.get("spx_level")))
        try:
            observed = _timestamp(date_value, field="price date")
            close = _finite(close_value, field="index close")
        except ValueError:
            continue
        if observed > as_of or close <= 0.0:
            continue
        normalized.append({"date": observed, "close": close})
    if not normalized:
        return pd.DataFrame(columns=("date", "close", "month"))
    frame = pd.DataFrame(normalized).sort_values("date")
    frame["month"] = frame["date"].dt.to_period("M")
    return frame.drop_duplicates("date", keep="last").reset_index(drop=True)


def _eps_frame(
    rows: Sequence[Mapping[str, object]], *, as_of: pd.Timestamp
) -> pd.DataFrame:
    normalized: list[dict[str, object]] = []
    for raw in rows:
        if str(raw.get("period_type") or "quarterly").lower() != "quarterly":
            continue
        basis = str(raw.get("earnings_basis") or "").lower()
        if basis not in {"operating", "as_reported"}:
            continue
        status = str(raw.get("value_status") or "estimate").lower()
        if status not in {"actual", "estimate", "mixed"}:
            continue
        try:
            period_end = _timestamp(raw.get("period_end"), field="period_end")
            released = _timestamp(
                raw.get("source_release_date"), field="source_release_date"
            )
            eps = _finite(raw.get("eps"), field="EPS")
        except ValueError:
            continue
        if released > as_of or eps <= 0.0:
            continue
        normalized.append(
            {
                "period_end": period_end,
                "released": released,
                "basis": basis,
                "status": status,
                "eps": eps,
            }
        )
    return pd.DataFrame(normalized)


def _forward_eps_at(
    eps: pd.DataFrame,
    *,
    cutoff: pd.Timestamp,
    target_year: int,
) -> tuple[float, pd.Timestamp, dict[pd.Timestamp, float]] | None:
    if eps.empty:
        return None
    eligible = eps.loc[
        (eps["released"] <= cutoff) & (eps["period_end"].dt.year == target_year)
    ].copy()
    if eligible.empty:
        return None
    expected_periods = {
        pd.Timestamp(date(target_year, month, day))
        for month, day in ((3, 31), (6, 30), (9, 30), (12, 31))
    }
    status_rank = {"estimate": 0, "mixed": 1, "actual": 2}
    eligible["status_rank"] = eligible["status"].map(status_rank).fillna(-1)
    for basis in ("operating", "as_reported"):
        basis_rows = eligible.loc[eligible["basis"] == basis].sort_values(
            ["period_end", "released", "status_rank"]
        )
        if basis_rows.empty:
            continue
        selected = basis_rows.drop_duplicates("period_end", keep="last")
        selected = selected.loc[selected["period_end"].isin(expected_periods)]
        if set(selected["period_end"]) != expected_periods:
            continue
        values = {
            pd.Timestamp(row.period_end): float(row.eps)
            for row in selected.itertuples()
        }
        return (
            float(sum(values.values())),
            pd.Timestamp(selected["released"].max()),
            values,
        )
    return None


def _measured_revision(
    eps: pd.DataFrame,
    *,
    selected: tuple[float, pd.Timestamp, dict[pd.Timestamp, float]],
    target_year: int,
) -> float | None:
    current_value, release, _values = selected
    prior = _forward_eps_at(
        eps,
        cutoff=release - pd.Timedelta(days=1),
        target_year=target_year,
    )
    if prior is None or prior[0] <= 0.0:
        return None
    return (current_value / prior[0] - 1.0) * 100.0


def _yield_series(
    rows: Sequence[Mapping[str, object]], *, as_of: pd.Timestamp
) -> dict[str, pd.DataFrame]:
    by_series: dict[str, list[dict[str, object]]] = {}
    for raw in rows:
        series_id = str(raw.get("series_id") or "").upper()
        if series_id not in {"DGS2", "DGS10", "DFII10", "T10YIE"}:
            continue
        try:
            observed = _timestamp(raw.get("observation_date"), field="yield date")
            released = _timestamp(raw.get("released_at") or observed, field="released_at")
            value = _finite(raw.get("value"), field=series_id)
        except ValueError:
            continue
        if observed > as_of or released > as_of:
            continue
        by_series.setdefault(series_id, []).append(
            {"date": observed, "released": released, "value": value}
        )
    result: dict[str, pd.DataFrame] = {}
    for series_id, values in by_series.items():
        frame = pd.DataFrame(values).sort_values(["date", "released"])
        result[series_id] = frame.drop_duplicates("date", keep="last").reset_index(
            drop=True
        )
    return result


def _yield_at(
    series: dict[str, pd.DataFrame], *, origin: pd.Timestamp
) -> dict[str, float | None]:
    levels: dict[str, float | None] = {}
    changes: dict[str, float | None] = {}
    for series_id in ("DGS2", "DGS10", "DFII10", "T10YIE"):
        frame = series.get(series_id)
        eligible = frame.loc[frame["date"] <= origin] if frame is not None else None
        if eligible is None or eligible.empty:
            levels[series_id] = None
            changes[series_id] = None
            continue
        levels[series_id] = float(eligible.iloc[-1]["value"])
        prior_index = max(0, len(eligible) - 22)
        changes[series_id] = (
            float(eligible.iloc[-1]["value"] - eligible.iloc[prior_index]["value"])
            * 100.0
        )
    return {
        "dgs2_pct": levels["DGS2"],
        "dgs10_pct": levels["DGS10"],
        "real_yield_10y_pct": levels["DFII10"],
        "breakeven_10y_pct": levels["T10YIE"],
        "policy_repricing_bp": changes["DGS2"],
        "dgs10_change_bp": changes["DGS10"],
        "real_yield_change_bp": changes["DFII10"],
        "breakeven_change_bp": changes["T10YIE"],
    }


def _pct_change(future: float | None, current: float) -> float | None:
    if future is None or current <= 0.0:
        return None
    return (future / current - 1.0) * 100.0


def build_equity_calibration_panel(
    *,
    price_rows: Sequence[Mapping[str, object]],
    eps_rows: Sequence[Mapping[str, object]],
    yield_rows: Sequence[Mapping[str, object]],
    as_of_at: str | datetime,
) -> pd.DataFrame:
    """Build monthly origins without exposing later EPS releases to their features."""

    as_of = _timestamp(as_of_at, field="as_of_at")
    prices = _price_frame(price_rows, as_of=as_of)
    eps = _eps_frame(eps_rows, as_of=as_of)
    if prices.empty or eps.empty:
        return pd.DataFrame(columns=PANEL_COLUMNS)
    month_ends = prices.sort_values("date").drop_duplicates("month", keep="last")
    yields = _yield_series(yield_rows, as_of=as_of)
    rows: list[dict[str, object]] = []
    for price in month_ends.itertuples():
        origin = pd.Timestamp(price.date)
        target_year = origin.year + 1
        current_eps = _forward_eps_at(eps, cutoff=origin, target_year=target_year)
        if current_eps is None:
            continue
        current_eps_value, eps_release, _current_quarters = current_eps
        current_index = float(price.close)
        current_multiple = current_index / current_eps_value
        year_prices = prices.loc[prices["date"].dt.year == origin.year]
        endpoint_row = year_prices.iloc[-1] if not year_prices.empty else None
        year_complete = as_of.date() > date(origin.year, 12, 31)
        endpoint_date = (
            pd.Timestamp(endpoint_row["date"])
            if endpoint_row is not None and year_complete
            else None
        )
        future_index = (
            float(endpoint_row["close"])
            if endpoint_row is not None and year_complete and endpoint_date >= origin
            else None
        )
        future_eps_record = (
            _forward_eps_at(eps, cutoff=endpoint_date, target_year=target_year)
            if endpoint_date is not None
            else None
        )
        future_eps = future_eps_record[0] if future_eps_record else None
        future_multiple = (
            future_index / future_eps
            if future_index is not None and future_eps is not None and future_eps > 0.0
            else None
        )
        rows.append(
            {
                "origin_date": origin.strftime("%Y-%m-%d"),
                "eps_source_release_date": eps_release.strftime("%Y-%m-%d"),
                "target_eps_year": target_year,
                "current_index_level": current_index,
                "forward_eps": current_eps_value,
                "forward_multiple": current_multiple,
                "measured_next_year_eps_revision_pct": _measured_revision(
                    eps, selected=current_eps, target_year=target_year
                ),
                "months_to_year_end": 12 - origin.month,
                **_yield_at(yields, origin=origin),
                "future_index_level": future_index,
                "future_forward_eps": future_eps,
                "future_forward_multiple": future_multiple,
                "eps_change_pct": _pct_change(future_eps, current_eps_value),
                "multiple_change_pct": _pct_change(
                    future_multiple, current_multiple
                ),
                "index_change_pct": _pct_change(future_index, current_index),
            }
        )
    return pd.DataFrame(rows, columns=PANEL_COLUMNS)
