from __future__ import annotations

import pandas as pd

from app.services.overview.market_mover_research import (
    build_current_ttm_valuation,
    build_financial_factor_series,
)


def _reported_eps_row(year: int, quarter: int, eps: float | None) -> dict[str, object]:
    return {
        "fiscal_year": year,
        "fiscal_quarter": quarter,
        "period_end": f"{year}-{quarter * 3:02d}-28",
        "diluted_eps": eps,
        "metric_provenance": (
            {"diluted_eps": {"source_kind": "REPORTED"}}
            if eps is not None
            else {}
        ),
    }


def test_financial_factor_series_separates_period_and_factor() -> None:
    rows = [
        {
            "period_end": "2024-12-31",
            "total_revenue": 80.0,
            "operating_income": 8.0,
            "net_income": 6.0,
            "current_assets": 60.0,
            "current_liabilities": 30.0,
            "total_liabilities": 70.0,
            "shareholders_equity": 50.0,
        },
        {
            "period_end": "2025-12-31",
            "total_revenue": 100.0,
            "operating_income": 15.0,
            "net_income": 10.0,
            "current_assets": 80.0,
            "current_liabilities": 40.0,
            "total_liabilities": 90.0,
            "shareholders_equity": 60.0,
        },
    ]

    series = build_financial_factor_series(rows, freq="annual")

    operating_margin = series["factors"]["operating_margin"]["points"][-1]
    assert series["freq"] == "annual"
    assert operating_margin["value"] == 15.0
    assert series["factors"]["current_ratio"]["points"][-1]["value"] == 2.0
    assert series["factors"]["debt_ratio"]["points"][-1]["value"] == 150.0
    assert round(series["factors"]["roe"]["points"][-1]["value"], 2) == 18.18


def test_current_ttm_per_requires_four_consecutive_reported_quarters() -> None:
    rows = [
        _reported_eps_row(2025, 1, 1.0),
        _reported_eps_row(2025, 2, 1.2),
        _reported_eps_row(2025, 3, 1.3),
        _reported_eps_row(2025, 4, 1.5),
    ]

    value = build_current_ttm_valuation(
        rows,
        latest_price=100.0,
        latest_price_date="2026-01-02",
    )

    assert value["status"] == "OK"
    assert value["ttm_diluted_eps"] == 5.0
    assert value["current_per"] == 20.0


def test_current_ttm_per_is_unavailable_when_one_quarter_is_missing() -> None:
    rows = [
        _reported_eps_row(2025, 1, 1.0),
        _reported_eps_row(2025, 2, None),
        _reported_eps_row(2025, 3, 1.3),
        _reported_eps_row(2025, 4, 1.5),
    ]

    value = build_current_ttm_valuation(
        rows,
        latest_price=100.0,
        latest_price_date="2026-01-02",
    )

    assert value["status"] == "UNAVAILABLE"
    assert value["reason_code"] == "INCOMPLETE_REPORTED_DILUTED_EPS"
    assert value["current_per"] is None


def test_diluted_eps_factor_excludes_filing_derived_quarters() -> None:
    rows = [
        _reported_eps_row(2025, 1, 1.0),
        {
            **_reported_eps_row(2025, 2, 1.2),
            "metric_provenance": {
                "diluted_eps": {"source_kind": "FILING_DERIVED"}
            },
        },
    ]

    series = build_financial_factor_series(rows, freq="quarterly")

    assert series["factors"]["diluted_eps"]["available_count"] == 1
    assert series["factors"]["diluted_eps"]["excluded_count"] == 1


def test_research_snapshot_exposes_v2_factors_without_historical_per() -> None:
    from app.services.overview.why_it_moved import build_market_mover_research_snapshot

    annual_rows = pd.DataFrame(
        [
            {
                "period_end": "2024-12-31",
                "available_at": "2025-02-20",
                "form_type": "10-K",
                "total_revenue": 80.0,
                "operating_income": 8.0,
                "net_income": 6.0,
                "shareholders_equity": 50.0,
            },
            {
                "period_end": "2025-12-31",
                "available_at": "2026-02-20",
                "form_type": "10-K",
                "total_revenue": 100.0,
                "operating_income": 15.0,
                "net_income": 10.0,
                "shareholders_equity": 60.0,
            },
        ]
    )
    quarterly_rows = pd.DataFrame(
        [
            {
                "period_end": "2026-03-31",
                "available_at": "2026-05-01",
                "form_type": "10-Q",
                "total_revenue": 30.0,
                "operating_income": 5.0,
                "net_income": 3.0,
                "shareholders_equity": 62.0,
            }
        ]
    )

    def statement_loader(**kwargs: object) -> pd.DataFrame:
        return annual_rows if kwargs["freq"] == "annual" else quarterly_rows

    model = build_market_mover_research_snapshot(
        mover={"Symbol": "AAA", "Market Cap": 5_500_000_000},
        as_of_date="2026-06-30",
        price_history_loader=lambda **_: pd.DataFrame(
            [
                {"date": "2026-01-02", "adj_close": 100.0},
                {"date": "2026-06-30", "adj_close": 120.0},
            ]
        ),
        statement_fundamentals_loader=statement_loader,
        fundamental_snapshot_loader=lambda **_: pd.DataFrame(),
        statement_filings_loader=lambda **_: pd.DataFrame(),
        quarterly_eps_loader=lambda **_: {
            "series": {
                "timeline": [
                    _reported_eps_row(2025, 3, 0.5),
                    _reported_eps_row(2025, 4, 0.6),
                    _reported_eps_row(2026, 1, 0.7),
                    _reported_eps_row(2026, 2, 0.8),
                ]
            }
        },
    )

    assert model["schema_version"] == "market_mover_research_snapshot_v2"
    assert model["financial_factor_series"]["annual"]["freq"] == "annual"
    assert model["current_valuation"]["ttm_diluted_eps"] == 2.6
    assert round(model["current_valuation"]["current_per"], 2) == 46.15
    assert all("per" not in row for row in model["financial_trends"]["annual"])
    assert model["ytd_return"]["series"] == [
        {"date": "2026-01-02", "price": 100.0, "normalized_return_pct": 0.0},
        {"date": "2026-06-30", "price": 120.0, "normalized_return_pct": 20.0},
    ]


def test_research_snapshot_keeps_up_to_ten_years_of_financial_history() -> None:
    from app.services.overview.why_it_moved import build_market_mover_research_snapshot

    annual_rows = pd.DataFrame(
        [
            {
                "period_end": f"{year}-12-31",
                "available_at": f"{year + 1}-02-20",
                "form_type": "10-K",
                "total_revenue": float(year),
                "operating_income": float(year) / 10,
                "net_income": float(year) / 20,
            }
            for year in range(2014, 2026)
        ]
    )
    quarter_ends = pd.date_range("2015-03-31", periods=44, freq="QE")
    quarterly_rows = pd.DataFrame(
        [
            {
                "period_end": period,
                "available_at": period + pd.Timedelta(days=40),
                "form_type": "10-Q",
                "total_revenue": float(index + 1),
                "operating_income": float(index + 1) / 10,
                "net_income": float(index + 1) / 20,
            }
            for index, period in enumerate(quarter_ends)
        ]
    )

    model = build_market_mover_research_snapshot(
        mover={"Symbol": "AAA", "Market Cap": 5_500_000_000},
        as_of_date="2026-06-30",
        price_history_loader=lambda **_: pd.DataFrame(
            [
                {"date": "2026-01-02", "adj_close": 100.0},
                {"date": "2026-06-30", "adj_close": 120.0},
            ]
        ),
        statement_fundamentals_loader=lambda **kwargs: annual_rows if kwargs["freq"] == "annual" else quarterly_rows,
        fundamental_snapshot_loader=lambda **_: pd.DataFrame(),
        statement_filings_loader=lambda **_: pd.DataFrame(),
        quarterly_eps_loader=lambda **_: {"series": {"timeline": []}},
    )

    assert len(model["financial_trends"]["annual"]) == 10
    assert len(model["financial_trends"]["quarterly"]) == 40
    assert len(model["financial_factor_series"]["annual"]["factors"]["revenue"]["points"]) == 10
    assert len(model["financial_factor_series"]["quarterly"]["factors"]["revenue"]["points"]) == 40


def test_research_snapshot_exposes_compact_db_filing_evidence() -> None:
    from app.services.overview.why_it_moved import build_market_mover_research_snapshot

    filings = pd.DataFrame(
        [
            {
                "symbol": "AAA",
                "accession_no": f"000-aaa-{index}",
                "form_type": form_type,
                "filing_date": filing_date,
                "accepted_at": f"{filing_date} 12:00:00",
                "available_at": f"{filing_date} 12:00:00",
                "report_date": report_date,
            }
            for index, (form_type, filing_date, report_date) in enumerate(
                [
                    ("10-Q", "2026-05-01", "2026-03-31"),
                    ("10-K", "2026-02-20", "2025-12-31"),
                    ("10-Q", "2025-11-01", "2025-09-30"),
                ]
            )
        ]
    )
    filings = pd.concat(
        [
            filings,
            pd.DataFrame(
                [
                    {
                        "symbol": "AAA",
                        "accession_no": "000-aaa-future",
                        "form_type": "10-Q",
                        "filing_date": None,
                        "accepted_at": None,
                        "available_at": None,
                        "report_date": "2026-09-30",
                    }
                ]
            ),
        ],
        ignore_index=True,
    )

    model = build_market_mover_research_snapshot(
        mover={"Symbol": "AAA", "Market Cap": 5_500_000_000},
        as_of_date="2026-06-30",
        price_history_loader=lambda **_: pd.DataFrame(
            [
                {"date": "2026-01-02", "adj_close": 100.0},
                {"date": "2026-06-30", "adj_close": 120.0},
            ]
        ),
        statement_fundamentals_loader=lambda **_: pd.DataFrame(),
        fundamental_snapshot_loader=lambda **_: pd.DataFrame(),
        statement_filings_loader=lambda **_: filings,
        quarterly_eps_loader=lambda **_: {"series": {"timeline": []}},
    )

    evidence = model["filing_evidence"]
    assert evidence["source"] == "finance_fundamental.nyse_financial_statement_filings"
    assert [row["form_type"] for row in evidence["rows"]] == ["10-Q", "10-K", "10-Q"]
    assert evidence["rows"][0]["report_date"] == "2026-03-31"
    assert evidence["rows"][0]["url"].startswith("https://www.sec.gov/edgar/browse/")
