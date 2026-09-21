from datetime import datetime, timedelta, timezone

import pytest

UTC = timezone.utc
CORE = ("ES=F", "NQ=F", "ZN=F", "6E=F", "6J=F", "6B=F", "6A=F", "6C=F")


def raw(symbol, end, close=100):
    return {
        "provider_symbol": symbol,
        "candle_time_utc": end - timedelta(minutes=5),
        "close": close,
    }


def market_rows(end):
    anchor = datetime(2026, 9, 18, 20, tzinfo=UTC)
    return [
        raw(s, t, v)
        for s in CORE
        for t, v in ((anchor, 100), (end - timedelta(hours=1), 100), (end, 101))
    ]


def calendar():
    return {
        "calendar_quality": "CONFIRMED",
        "schedule": [
            {"day_kind": "TRADING_DAY", "close_at_utc": "2026-09-18T20:00:00+00:00"},
            {"day_kind": "TRADING_DAY", "close_at_utc": "2026-09-21T20:00:00+00:00"},
        ],
    }


def test_open_bar_and_conflicting_duplicate_are_excluded():
    from app.services.futures_macro_windows import normalize_closed_bars

    end = datetime(2026, 9, 21, 7, tzinfo=UTC)
    rows = [
        raw("ES=F", end, 100),
        raw("ES=F", end, 102),
        raw("ES=F", end, 100),
        raw("NQ=F", end, 100),
        raw("ZN=F", end + timedelta(minutes=5), 100),
    ]
    result = normalize_closed_bars(rows, evaluation_time=end)
    assert [(r["provider_symbol"], r["close"]) for r in result] == [("NQ=F", 100)]


@pytest.mark.parametrize("bad", [0, -1, float("nan"), float("inf"), None])
def test_bad_price_cannot_become_a_return(bad):
    from app.services.futures_macro_windows import build_window_returns

    start = datetime(2026, 9, 21, 6, tzinfo=UTC)
    end = start + timedelta(hours=1)
    rows = [
        {"provider_symbol": "ES=F", "bar_end_utc": start, "close": bad},
        {"provider_symbol": "ES=F", "bar_end_utc": end, "close": 100},
    ]
    assert (
        build_window_returns(rows, symbols=["ES=F"], start_utc=start, end_utc=end)[
            "returns_pct"
        ]["ES=F"]
        is None
    )


def test_missing_endpoint_is_not_filled_and_exact_return_is_used():
    from app.services.futures_macro_windows import build_window_returns

    start = datetime(2026, 9, 21, 6, tzinfo=UTC)
    end = start + timedelta(hours=1)
    rows = [
        {"provider_symbol": "ES=F", "bar_end_utc": start, "close": 100},
        {"provider_symbol": "ES=F", "bar_end_utc": end, "close": 100.25},
        {"provider_symbol": "NQ=F", "bar_end_utc": start, "close": 100},
        {
            "provider_symbol": "NQ=F",
            "bar_end_utc": end - timedelta(minutes=5),
            "close": 105,
        },
    ]
    result = build_window_returns(
        rows, symbols=["ES=F", "NQ=F"], start_utc=start, end_utc=end
    )
    assert result["returns_pct"]["ES=F"] == pytest.approx(0.25)
    assert result["returns_pct"]["NQ=F"] is None
    assert result["missing_symbols"] == ["NQ=F"]


def test_monday_uses_friday_cash_close_and_hour_is_not_a_forecast():
    from app.services.futures_macro_windows import build_futures_macro_window_snapshot

    end = datetime(2026, 9, 21, 7, tzinfo=UTC)
    result = build_futures_macro_window_snapshot(
        rows=market_rows(end), evaluation_time=end, calendar=calendar()
    )
    assert result["windows"]["since_close"]["start_utc"] == "2026-09-18T20:00:00+00:00"
    assert result["windows"]["last_hour"]["start_utc"] == "2026-09-21T06:00:00+00:00"
    assert result["windows"]["last_hour"]["dollar_proxy_pct"] == pytest.approx(-1)
    assert result["windows"]["last_hour"]["returns_pct"]["ES=F"] == pytest.approx(1)


def test_one_missing_currency_does_not_reweight_dollar_or_hide_equities():
    from app.services.futures_macro_windows import build_futures_macro_window_snapshot

    end = datetime(2026, 9, 21, 7, tzinfo=UTC)
    rows = [r for r in market_rows(end) if r["provider_symbol"] != "6J=F"]
    result = build_futures_macro_window_snapshot(
        rows=rows, evaluation_time=end, calendar=calendar()
    )["windows"]["last_hour"]
    assert result["status"] == "PARTIAL"
    assert result["dollar_proxy_pct"] is None
    assert result["returns_pct"]["ES=F"] == pytest.approx(1)
    assert "6J=F" in result["missing_symbols"]


def test_common_cutoff_is_an_intersection_not_min_latest_with_forward_fill():
    from app.services.futures_macro_windows import build_futures_macro_window_snapshot

    end = datetime(2026, 9, 21, 7, tzinfo=UTC)
    rows = market_rows(end)
    rows = [
        r
        for r in rows
        if not (
            r["provider_symbol"] == "6J=F"
            and r["candle_time_utc"] == end - timedelta(minutes=5)
        )
    ]
    rows.append(raw("6J=F", end - timedelta(minutes=5), 105))
    result = build_futures_macro_window_snapshot(
        rows=rows, evaluation_time=end, calendar=calendar()
    )
    assert result["windows"]["last_hour"]["status"] == "STALE"
    assert result["windows"]["last_hour"]["end_utc"] == "2026-09-21T06:00:00+00:00"


def test_unknown_calendar_only_disables_close_window():
    from app.services.futures_macro_windows import build_futures_macro_window_snapshot

    end = datetime(2026, 9, 21, 7, tzinfo=UTC)
    result = build_futures_macro_window_snapshot(
        rows=market_rows(end), evaluation_time=end, calendar={}
    )
    assert result["windows"]["since_close"]["status"] == "UNAVAILABLE"
    assert result["windows"]["last_hour"]["status"] == "AVAILABLE"


def test_closed_weekend_is_not_stale_but_old_weekend_data_is():
    from app.services.futures_macro_windows import build_futures_macro_window_snapshot

    end = datetime(2026, 9, 18, 21, tzinfo=UTC)
    now = datetime(2026, 9, 19, 12, tzinfo=UTC)
    result = build_futures_macro_window_snapshot(
        rows=market_rows(end), evaluation_time=now, calendar=calendar()
    )
    assert result["windows"]["last_hour"]["status"] == "MARKET_CLOSED"
    old = [
        dict(r, candle_time_utc=r["candle_time_utc"] - timedelta(days=7))
        for r in market_rows(end)
    ]
    result = build_futures_macro_window_snapshot(
        rows=old, evaluation_time=now, calendar=calendar()
    )
    assert result["windows"]["last_hour"]["status"] == "STALE"


@pytest.mark.parametrize(
    "now,holidays,early,want",
    [
        ("2026-03-09T12:00:00+00:00", [], [], "2026-03-06T21:00:00+00:00"),
        ("2026-03-10T12:00:00+00:00", [], [], "2026-03-09T20:00:00+00:00"),
        (
            "2026-09-08T12:00:00+00:00",
            [{"Date": "2026-09-07"}],
            [],
            "2026-09-04T20:00:00+00:00",
        ),
        (
            "2026-11-27T20:00:00+00:00",
            [{"Date": "2026-11-26"}],
            [{"Date": "2026-11-27", "Event Time": "13:00"}],
            "2026-11-27T18:00:00+00:00",
        ),
    ],
)
def test_cash_calendar_anchor_handles_dst_holiday_and_early_close(
    now, holidays, early, want
):
    from app.services.futures_macro_windows import (
        build_cash_session_calendar,
        previous_cash_close,
    )

    instant = datetime.fromisoformat(now)
    # Full-year official coverage is explicit; no holiday-in-lookback heuristic.
    schedule = build_cash_session_calendar(
        evaluation_time=instant,
        holiday_rows=holidays,
        early_close_rows=early,
        calendar_statuses={"holiday": "OK", "early_close": "OK"},
        covered_years={2026},
    )
    assert previous_cash_close(instant, schedule).isoformat() == want


def test_loader_preserves_time_bounds_and_filters_provider():
    from finance.loaders.futures import load_futures_intraday_rows

    captured = []
    start = datetime(2026, 9, 21, 6, 15, tzinfo=UTC)
    end = start + timedelta(hours=1)
    load_futures_intraday_rows(
        ["ES=F"],
        start_utc=start,
        end_utc=end,
        query_fn=lambda db, sql, params: captured.append((sql, params)) or [],
    )
    sql, params = captured[0]
    assert "source = %s" in sql and params[1] == "yfinance"
    assert params[-2].minute == 15 and params[-2].tzinfo is None


def test_missing_calendar_does_not_request_price_backfill():
    from app.services.futures_macro_windows import build_futures_macro_window_snapshot

    end = datetime(2026, 9, 21, 7, tzinfo=UTC)
    r = build_futures_macro_window_snapshot(
        rows=market_rows(end), evaluation_time=end, calendar={}
    )
    assert r["windows"]["since_close"]["missing_symbols"] == []
