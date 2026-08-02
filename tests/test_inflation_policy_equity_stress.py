from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import pytest


def _next_year_eps_rows(
    *,
    release_date: str,
    target_year: int,
    quarterly_values: tuple[float, float, float, float],
    basis: str = "operating",
) -> list[dict[str, object]]:
    return [
        {
            "period_end": f"{target_year}-{month_day}",
            "period_type": "quarterly",
            "earnings_basis": basis,
            "value_status": "estimate",
            "eps": value,
            "source": "sp_dow_jones_index_earnings",
            "source_ref": "official-workbook.xlsx",
            "source_release_date": release_date,
            "collected_at": f"{release_date}T12:05:00Z",
        }
        for month_day, value in zip(
            ("03-31", "06-30", "09-30", "12-31"),
            quarterly_values,
            strict=True,
        )
    ]


def _yield_rows(*dates: str) -> list[dict[str, object]]:
    offsets = {"DGS2": -0.75, "DGS10": 0.0, "DFII10": -2.15, "T10YIE": -2.0}
    rows: list[dict[str, object]] = []
    for index, observed in enumerate(dates):
        base = 4.0 + index * 0.05
        for series_id, offset in offsets.items():
            rows.append(
                {
                    "series_id": series_id,
                    "observation_date": observed,
                    "released_at": f"{observed}T23:59:00Z",
                    "value": base + offset,
                }
            )
    return rows


def test_equity_bundle_excludes_rows_not_known_at_cutoff() -> None:
    from finance.loaders.inflation_policy import load_inflation_policy_equity_bundle

    eps_rows = _next_year_eps_rows(
        release_date="2025-03-15", target_year=2026, quarterly_values=(20, 25, 25, 30)
    ) + _next_year_eps_rows(
        release_date="2025-06-15", target_year=2026, quarterly_values=(25, 30, 30, 35)
    )
    price_rows = [
        {"symbol": "^GSPC", "Date": "2025-03-31", "Close": 4000.0},
        {"symbol": "^GSPC", "Date": "2025-06-02", "Close": 4200.0},
    ]
    yield_rows = _yield_rows("2025-03-31", "2025-06-02")

    def query(database: str, sql: str, _params: tuple[object, ...]):
        if database == "finance_price":
            return price_rows
        if "sp500_index_earnings" in sql:
            return eps_rows
        if "macro_series_vintage_observation" in sql:
            return yield_rows
        raise AssertionError(sql)

    bundle = load_inflation_policy_equity_bundle(
        as_of_at="2025-05-31T23:59:59Z",
        history_start="2025-01-01",
        query_fn=query,
    )

    assert len(bundle.eps_rows) == 4
    assert {row["source_release_date"] for row in bundle.eps_rows} == {"2025-03-15"}
    assert [row["Date"] for row in bundle.price_rows] == ["2025-03-31"]
    assert all(str(row["observation_date"]) <= "2025-05-31" for row in bundle.yield_rows)
    assert bundle.coverage["official_eps_vintage_status"] == "READY"


def test_panel_uses_only_eps_vintage_released_before_origin() -> None:
    from finance.inflation_policy_equity_stress import build_equity_calibration_panel

    prices = [
        {"Date": "2025-03-31", "Close": 4000.0},
        {"Date": "2025-04-30", "Close": 4050.0},
        {"Date": "2025-05-30", "Close": 4100.0},
    ]
    eps = _next_year_eps_rows(
        release_date="2025-03-15", target_year=2026, quarterly_values=(20, 25, 25, 30)
    ) + _next_year_eps_rows(
        release_date="2025-06-15", target_year=2026, quarterly_values=(25, 30, 30, 35)
    )

    panel = build_equity_calibration_panel(
        price_rows=prices,
        eps_rows=eps,
        yield_rows=_yield_rows("2025-03-31", "2025-04-30", "2025-05-30"),
        as_of_at="2025-05-31T23:59:59Z",
    )

    assert panel.iloc[-1]["origin_date"] == "2025-05-30"
    assert panel.iloc[-1]["eps_source_release_date"] == "2025-03-15"
    assert panel.iloc[-1]["forward_eps"] == pytest.approx(100.0)
    assert panel.iloc[-1]["forward_multiple"] == pytest.approx(41.0)


def test_panel_preserves_year_end_eps_times_multiple_identity() -> None:
    from finance.inflation_policy_equity_stress import build_equity_calibration_panel

    prices = [
        {"Date": "2025-06-30", "Close": 4000.0},
        {"Date": "2025-12-31", "Close": 3600.0},
    ]
    eps = _next_year_eps_rows(
        release_date="2025-06-15", target_year=2026, quarterly_values=(50, 50, 50, 50)
    ) + _next_year_eps_rows(
        release_date="2025-12-15", target_year=2026, quarterly_values=(45, 45, 45, 45)
    )

    panel = build_equity_calibration_panel(
        price_rows=prices,
        eps_rows=eps,
        yield_rows=_yield_rows("2025-06-30", "2025-12-31"),
        as_of_at="2026-01-02T00:00:00Z",
    )
    june = panel.loc[panel["origin_date"] == "2025-06-30"].iloc[0]

    assert june["forward_eps"] == pytest.approx(200.0)
    assert june["forward_multiple"] == pytest.approx(20.0)
    assert june["future_forward_eps"] == pytest.approx(180.0)
    assert june["future_forward_multiple"] == pytest.approx(20.0)
    assert june["future_index_level"] == pytest.approx(
        june["future_forward_eps"] * june["future_forward_multiple"]
    )
    assert june["eps_change_pct"] == pytest.approx(-10.0)
    assert june["multiple_change_pct"] == pytest.approx(0.0)
    assert june["index_change_pct"] == pytest.approx(-10.0)
    assert june["months_to_year_end"] == 6


def test_panel_does_not_substitute_trailing_eps_for_missing_next_year_quarter() -> None:
    from finance.inflation_policy_equity_stress import build_equity_calibration_panel

    incomplete = _next_year_eps_rows(
        release_date="2025-03-15", target_year=2026, quarterly_values=(20, 25, 25, 30)
    )[:3]
    incomplete.append(
        {
            "period_end": "2024-12-31",
            "period_type": "ttm",
            "earnings_basis": "as_reported",
            "value_status": "actual",
            "eps": 250.0,
            "source_release_date": "2025-03-15",
        }
    )

    panel = build_equity_calibration_panel(
        price_rows=[{"Date": "2025-03-31", "Close": 4000.0}],
        eps_rows=incomplete,
        yield_rows=_yield_rows("2025-03-31"),
        as_of_at=datetime(2025, 4, 1, tzinfo=timezone.utc),
    )

    assert panel.empty


def test_panel_returns_explicit_columns_when_inputs_are_empty() -> None:
    from finance.inflation_policy_equity_stress import build_equity_calibration_panel

    panel = build_equity_calibration_panel(
        price_rows=[], eps_rows=[], yield_rows=[], as_of_at="2025-05-31T23:59:59Z"
    )

    assert isinstance(panel, pd.DataFrame)
    assert panel.empty
    assert {"origin_date", "forward_eps", "forward_multiple"}.issubset(panel.columns)
