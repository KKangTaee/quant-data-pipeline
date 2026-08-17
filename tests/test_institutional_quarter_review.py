from __future__ import annotations

import pandas as pd
import importlib


def test_position_changes_use_reported_amount_not_market_value() -> None:
    from app.services.institutional_quarter_review import build_institutional_position_changes

    previous = pd.DataFrame(
        [
            {"cusip": "ADDCUSIP1", "title_of_class": "COM", "shares_or_principal_amount": 10, "reported_value": 100},
            {"cusip": "KEEPCUSI1", "title_of_class": "COM", "shares_or_principal_amount": 10, "reported_value": 100},
            {"cusip": "REDCUSIP1", "title_of_class": "COM", "shares_or_principal_amount": 10, "reported_value": 100},
            {"cusip": "DROPCUSI1", "title_of_class": "COM", "shares_or_principal_amount": 10, "reported_value": 100},
            {"cusip": "MISSING01", "title_of_class": "COM", "shares_or_principal_amount": None, "reported_value": 100},
        ]
    )
    current = pd.DataFrame(
        [
            {"cusip": "NEWCUSIP1", "title_of_class": "COM", "shares_or_principal_amount": 5, "reported_value": 50},
            {"cusip": "ADDCUSIP1", "title_of_class": "COM", "shares_or_principal_amount": 12, "reported_value": 80},
            {"cusip": "KEEPCUSI1", "title_of_class": "COM", "shares_or_principal_amount": 10, "reported_value": 180},
            {"cusip": "REDCUSIP1", "title_of_class": "COM", "shares_or_principal_amount": 8, "reported_value": 120},
            {"cusip": "MISSING01", "title_of_class": "COM", "shares_or_principal_amount": None, "reported_value": 120},
        ]
    )

    changes = build_institutional_position_changes(previous, current)
    labels = {row["cusip"]: row["change_type"] for row in changes}

    assert labels == {
        "ADDCUSIP1": "ADD",
        "DROPCUSI1": "DROP",
        "KEEPCUSI1": "KEEP",
        "MISSING01": "NOT_COMPARABLE",
        "NEWCUSIP1": "NEW",
        "REDCUSIP1": "REDUCE",
    }


def test_position_identity_keeps_put_call_and_amount_type_separate() -> None:
    from app.services.institutional_quarter_review import build_institutional_position_changes

    previous = pd.DataFrame(
        [
            {"cusip": "037833100", "title_of_class": "COM", "put_call": None, "amount_type": "SH", "shares_or_principal_amount": 10},
            {"cusip": "037833100", "title_of_class": "COM", "put_call": "CALL", "amount_type": "SH", "shares_or_principal_amount": 2},
        ]
    )
    current = pd.DataFrame(
        [
            {"cusip": "037833100", "title_of_class": "COM", "put_call": None, "amount_type": "SH", "shares_or_principal_amount": 10},
        ]
    )

    changes = build_institutional_position_changes(previous, current)

    assert [(row["put_call"], row["change_type"]) for row in changes] == [("CALL", "DROP"), ("", "KEEP")]


def test_price_proxy_reports_covered_sleeve_without_zero_filling_missing_weight() -> None:
    from app.services.institutional_quarter_review import build_institutional_price_proxy

    holdings = pd.DataFrame(
        [
            {"cusip": "037833100", "holding_symbol": "AAPL", "issuer_name": "APPLE INC", "reported_value": 60, "put_call": None},
            {"cusip": "999999999", "holding_symbol": None, "issuer_name": "UNMAPPED", "reported_value": 40, "put_call": None},
        ]
    )
    prices = pd.DataFrame(
        [
            {"symbol": "AAPL", "date": "2026-03-31", "close": 100},
            {"symbol": "AAPL", "date": "2026-06-30", "close": 110},
        ]
    )

    proxy = build_institutional_price_proxy(
        holdings,
        prices,
        start_date="2026-03-31",
        end_date="2026-06-30",
        proxy_id="quarter_holdings_proxy",
    )

    assert proxy["coverage_weight_pct"] == 60.0
    assert proxy["missing_weight_pct"] == 40.0
    assert proxy["status"] == "LIMITED"
    assert proxy["covered_sleeve_return_pct"] == 10.0
    assert proxy["rows"][0]["contribution_pct"] == 6.0
    assert proxy["missing_positions"][0]["reason"] == "unmapped_identifier"


def test_price_proxy_uses_first_close_after_start_and_last_close_before_end() -> None:
    from app.services.institutional_quarter_review import build_institutional_price_proxy

    holdings = pd.DataFrame(
        [{"cusip": "037833100", "holding_symbol": "AAPL", "reported_value": 100, "put_call": None}]
    )
    prices = pd.DataFrame(
        [
            {"symbol": "AAPL", "date": "2026-04-01", "close": 100},
            {"symbol": "AAPL", "date": "2026-06-29", "close": 120},
            {"symbol": "AAPL", "date": "2026-07-01", "close": 999},
        ]
    )

    proxy = build_institutional_price_proxy(
        holdings,
        prices,
        start_date="2026-03-31",
        end_date="2026-06-30",
        proxy_id="quarter_holdings_proxy",
    )

    assert proxy["status"] == "READY"
    assert proxy["covered_sleeve_return_pct"] == 20.0
    assert proxy["rows"][0]["start_date"] == "2026-04-01"
    assert proxy["rows"][0]["end_date"] == "2026-06-29"


def test_quarter_review_builds_both_approved_performance_windows() -> None:
    from app.services.institutional_quarter_review import build_institutional_quarter_review

    previous = {
        "available": True,
        "filing": {"period_of_report": "2026-03-31", "filing_date": "2026-05-15"},
        "holdings": pd.DataFrame(
            [
                {
                    "cusip": "037833100",
                    "title_of_class": "COM",
                    "shares_or_principal_amount": 10,
                    "reported_value": 100,
                    "holding_symbol": "AAPL",
                }
            ]
        ),
        "source_accessions": ["q1"],
    }
    current = {
        "available": True,
        "manager": {"cik": "0001067983", "manager_name": "BERKSHIRE HATHAWAY INC"},
        "filing": {"period_of_report": "2026-06-30", "filing_date": "2026-08-14"},
        "holdings": pd.DataFrame(
            [
                {
                    "cusip": "037833100",
                    "title_of_class": "COM",
                    "shares_or_principal_amount": 12,
                    "reported_value": 120,
                    "holding_symbol": "AAPL",
                }
            ]
        ),
        "source_accessions": ["q2"],
    }
    prices = pd.DataFrame(
        [
            {"symbol": "AAPL", "date": "2026-03-31", "close": 100},
            {"symbol": "AAPL", "date": "2026-05-15", "close": 105},
            {"symbol": "AAPL", "date": "2026-06-30", "close": 110},
            {"symbol": "AAPL", "date": "2026-08-14", "close": 126},
        ]
    )

    review = build_institutional_quarter_review(
        previous_effective=previous,
        current_effective=current,
        price_history=prices,
    )

    assert review["available"] is True
    assert review["transition"]["previous_report_period"] == "2026-03-31"
    assert review["change_summary"]["ADD"] == 1
    assert review["proxies"]["quarter_holdings_proxy"]["covered_sleeve_return_pct"] == 10.0
    assert review["proxies"]["public_follow_proxy"]["covered_sleeve_return_pct"] == 20.0
    assert review["changes"][0]["symbol_return_pct"] == 10.0


def test_quarter_review_requires_two_effective_quarters() -> None:
    from app.services.institutional_quarter_review import build_institutional_quarter_review

    review = build_institutional_quarter_review(
        previous_effective=None,
        current_effective={"available": True, "filing": {}, "holdings": pd.DataFrame()},
        price_history=pd.DataFrame(),
    )

    assert review["available"] is False
    assert "이전 보고 분기" in review["reason"]
    assert review["changes"] == []


def test_quarter_review_loader_reads_one_combined_price_window_without_fetching(monkeypatch) -> None:
    service = importlib.import_module("app.services.institutional_quarter_review")
    previous = {
        "available": True,
        "filing": {"period_of_report": "2026-03-31", "filing_date": "2026-05-15"},
        "holdings": pd.DataFrame(
            [
                {
                    "cusip": "037833100",
                    "holding_symbol": "AAPL",
                    "reported_value": 100,
                    "shares_or_principal_amount": 10,
                }
            ]
        ),
        "source_accessions": ["q1"],
    }
    current = {
        "available": True,
        "manager": {"cik": "0001067983", "manager_name": "BERKSHIRE HATHAWAY INC"},
        "filing": {"period_of_report": "2026-06-30", "filing_date": "2026-08-14"},
        "holdings": previous["holdings"].copy(),
        "source_accessions": ["q2"],
    }
    calls: list[dict] = []
    monkeypatch.setattr(
        service,
        "load_institutional_13f_effective_history",
        lambda *_args, **_kwargs: [current, previous],
    )
    monkeypatch.setattr(
        service,
        "load_price_history",
        lambda **kwargs: calls.append(kwargs) or pd.DataFrame(),
    )

    review = service.load_institutional_quarter_review_model("0001067983")

    assert review["available"] is True
    assert calls == [
        {
            "symbols": ["AAPL"],
            "start": "2026-03-31",
            "end": "2026-08-14",
            "timeframe": "1d",
        }
    ]
