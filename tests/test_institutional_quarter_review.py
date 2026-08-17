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
            {"cusip": "037833100", "holding_symbol": "AAPL", "issuer_name": "APPLE INC", "title_of_class": "COM", "amount_type": "SH", "reported_value": 60, "put_call": None},
            {"cusip": "999999999", "holding_symbol": None, "issuer_name": "UNMAPPED", "title_of_class": "COM", "amount_type": "SH", "reported_value": 40, "put_call": None},
        ]
    )
    prices = pd.DataFrame(
        [
            {"symbol": "AAPL", "date": "2026-03-31", "close": 100, "adj_close": 100},
            {"symbol": "AAPL", "date": "2026-06-30", "close": 110, "adj_close": 110},
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
        [{"cusip": "037833100", "holding_symbol": "AAPL", "title_of_class": "COM", "amount_type": "SH", "reported_value": 100, "put_call": None}]
    )
    prices = pd.DataFrame(
        [
            {"symbol": "AAPL", "date": "2026-04-01", "close": 50, "adj_close": 100},
            {"symbol": "AAPL", "date": "2026-06-29", "close": 120, "adj_close": 120},
            {"symbol": "AAPL", "date": "2026-07-01", "close": 999, "adj_close": 999},
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


def test_price_proxy_excludes_non_common_instruments_and_requires_adjusted_prices() -> None:
    from app.services.institutional_quarter_review import build_institutional_price_proxy

    holdings = pd.DataFrame(
        [
            {"cusip": "037833100", "holding_symbol": "AAPL", "title_of_class": "COM", "amount_type": "SH", "reported_value": 60},
            {"cusip": "DEBT00001", "holding_symbol": "AAPL", "title_of_class": "NOTE", "amount_type": "PRN", "reported_value": 30},
            {"cusip": "RAWONLY01", "holding_symbol": "RAW", "title_of_class": "COM", "amount_type": "SH", "reported_value": 10},
        ]
    )
    prices = pd.DataFrame(
        [
            {"symbol": "AAPL", "date": "2026-03-31", "close": 100, "adj_close": 50},
            {"symbol": "AAPL", "date": "2026-06-30", "close": 50, "adj_close": 55},
            {"symbol": "RAW", "date": "2026-03-31", "close": 100, "adj_close": None},
            {"symbol": "RAW", "date": "2026-06-30", "close": 110, "adj_close": None},
        ]
    )

    proxy = build_institutional_price_proxy(
        holdings,
        prices,
        start_date="2026-03-31",
        end_date="2026-06-30",
        proxy_id="quarter_holdings_proxy",
    )

    assert proxy["covered_sleeve_return_pct"] == 10.0
    assert proxy["coverage_weight_pct"] == 60.0
    assert {row["reason"] for row in proxy["missing_positions"]} == {
        "non_common_instrument",
        "adjusted_price_unavailable",
    }
    assert proxy["price_basis"] == "adjusted_close_total_return_when_available"


def test_price_proxy_orders_and_caps_sign_specific_contributors_and_omits_zero() -> None:
    from app.services.institutional_quarter_review import build_institutional_price_proxy

    positions = [
        ("POS1", "POS000001", 10, 110),
        ("POS2", "POS000002", 10, 120),
        ("POS3", "POS000003", 10, 130),
        ("POS4", "POS000004", 10, 140),
        ("POS5", "POS000005", 10, 150),
        ("POS6", "POS000006", 10, 160),
        ("NEG1", "NEG000001", 5, 90),
        ("NEG2", "NEG000002", 5, 80),
        ("NEG3", "NEG000003", 5, 70),
        ("NEG4", "NEG000004", 5, 60),
        ("NEG5", "NEG000005", 5, 50),
        ("NEG6", "NEG000006", 5, 40),
        ("ZERO", "ZERO00001", 10, 100),
    ]
    holdings = pd.DataFrame(
        [
            {
                "cusip": cusip,
                "holding_symbol": symbol,
                "title_of_class": "COM",
                "amount_type": "SH",
                "reported_value": reported_value,
            }
            for symbol, cusip, reported_value, _ in positions
        ]
    )
    prices = pd.DataFrame(
        [
            {"symbol": symbol, "date": date, "adj_close": adj_close}
            for symbol, _, _, end_price in positions
            for date, adj_close in (("2026-03-31", 100), ("2026-06-30", end_price))
        ]
    )

    proxy = build_institutional_price_proxy(
        holdings,
        prices,
        start_date="2026-03-31",
        end_date="2026-06-30",
        proxy_id="quarter_holdings_proxy",
    )

    pos6 = next(row for row in proxy["rows"] if row["holding_symbol"] == "POS6")
    assert (pos6["weight_pct"], pos6["return_pct"], pos6["contribution_pct"]) == (10.0, 60.0, 6.0)
    assert [(row["holding_symbol"], row["contribution_pct"]) for row in proxy["top_contributors"]] == [
        ("POS6", 6.0),
        ("POS5", 5.0),
        ("POS4", 4.0),
        ("POS3", 3.0),
        ("POS2", 2.0),
    ]
    assert [(row["holding_symbol"], row["contribution_pct"]) for row in proxy["top_detractors"]] == [
        ("NEG6", -3.0),
        ("NEG5", -2.5),
        ("NEG4", -2.0),
        ("NEG3", -1.5),
        ("NEG2", -1.0),
    ]
    assert "ZERO" not in {row["holding_symbol"] for row in proxy["top_contributors"]}
    assert "ZERO" not in {row["holding_symbol"] for row in proxy["top_detractors"]}


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
                    "amount_type": "SH",
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
                    "amount_type": "SH",
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
            {"symbol": "AAPL", "date": "2026-03-31", "close": 100, "adj_close": 100},
            {"symbol": "AAPL", "date": "2026-05-15", "close": 105, "adj_close": 105},
            {"symbol": "AAPL", "date": "2026-06-30", "close": 110, "adj_close": 110},
            {"symbol": "AAPL", "date": "2026-08-14", "close": 126, "adj_close": 126},
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
                    "title_of_class": "COM",
                    "amount_type": "SH",
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


def test_quarter_review_loader_exposes_all_saved_transitions_with_one_price_load(monkeypatch) -> None:
    service = importlib.import_module("app.services.institutional_quarter_review")

    def effective(period: str, filing_date: str, symbol: str) -> dict:
        return {
            "available": True,
            "manager": {"cik": "0001067983", "manager_name": "Berkshire"},
            "filing": {"period_of_report": period, "filing_date": filing_date},
            "holdings": pd.DataFrame(
                [{"cusip": symbol, "holding_symbol": symbol, "title_of_class": "COM", "amount_type": "SH", "reported_value": 100, "shares_or_principal_amount": 10}]
            ),
            "source_accessions": [period],
        }

    history = [
        effective("2026-06-30", "2026-08-14", "AAPL"),
        effective("2026-03-31", "2026-05-15", "MSFT"),
        effective("2025-12-31", "2026-02-16", "IBM"),
    ]
    calls: list[dict] = []
    monkeypatch.setattr(service, "load_institutional_13f_effective_history", lambda *_args, **_kwargs: history)
    monkeypatch.setattr(service, "load_price_history", lambda **kwargs: calls.append(kwargs) or pd.DataFrame())

    review = service.load_institutional_quarter_review_model("0001067983")

    assert len(review["transitions"]) == 2
    assert [row["transition"]["current_report_period"] for row in review["transitions"]] == [
        "2026-06-30",
        "2026-03-31",
    ]
    assert calls == [
        {
            "symbols": ["IBM", "MSFT"],
            "start": "2025-12-31",
            "end": "2026-08-14",
            "timeframe": "1d",
        }
    ]


def test_workbench_v3_payload_carries_python_owned_quarter_review() -> None:
    from app.services.institutional_portfolios import build_institutional_workbench_payload

    review = {
        "available": True,
        "change_summary": {"NEW": 0, "ADD": 0, "KEEP": 1, "REDUCE": 0, "DROP": 0},
        "changes": [{"cusip": "037833100", "change_type": "KEEP"}],
        "proxies": {
            "quarter_holdings_proxy": {"status": "READY", "covered_sleeve_return_pct": 10.0},
            "public_follow_proxy": {"status": "LIMITED", "covered_sleeve_return_pct": 8.0},
        },
    }
    refresh_action = {
        "action_id": "refresh_institutional_13f",
        "visible": True,
        "status": "due",
        "target_report_period": "2026-06-30",
    }

    payload = build_institutional_workbench_payload(
        model={"summary": {}, "holdings": [], "changes": [], "sector_exposure": []},
        managers=[],
        selected_cik="0001067983",
        interest_model=None,
        quarter_review=review,
        refresh_action=refresh_action,
    )

    assert payload["schema_version"] == "institutional_portfolios_workbench_v3"
    assert payload["refresh_action"] == refresh_action
    assert payload["quarter_review"] == review
    assert payload["quarter_review"]["change_summary"]["KEEP"] == 1
