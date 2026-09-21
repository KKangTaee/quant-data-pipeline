from datetime import datetime, timedelta, timezone

import pytest

from tests.test_futures_macro_reading import window
from tests.test_futures_macro_windows import CORE, calendar, market_rows, raw


def test_unchanged_since_close_uses_same_anchor_and_real_previous_values():
    from app.services.futures_macro_reading import build_futures_macro_change_reading
    from app.services.futures_macro_windows import build_futures_macro_window_snapshot

    end = datetime(2026, 9, 21, 7, tzinfo=timezone.utc)
    rows = market_rows(end)
    for row in rows:
        if row["candle_time_utc"] == end - timedelta(hours=1, minutes=5):
            row["close"] = 100.5
    w = build_futures_macro_window_snapshot(
        rows=rows, evaluation_time=end, calendar=calendar()
    )["windows"]["since_close"]
    c = build_futures_macro_change_reading(w)["condition_results"][0]
    assert c["comparison"]["status"] == "UNCHANGED"
    assert c["comparison"]["previous_start_utc"] == w["start_utc"]
    assert c["comparison"]["previous_end_utc"] == "2026-09-21T06:00:00+00:00"
    assert c["comparison"]["previous_evidence"][0]["return_pct"] == pytest.approx(0.5)


@pytest.mark.parametrize(
    "start,end",
    [
        ("2026-09-21T05:00:00+00:00", "2026-09-21T08:00:00+00:00"),
        ("2026-09-21T04:00:00+00:00", "2026-09-21T06:00:00+00:00"),
    ],
)
def test_comparison_rejects_future_or_different_duration(start, end):
    from app.services.futures_macro_reading import build_futures_macro_change_reading

    w = dict(window(), start_utc="2026-09-21T06:00:00+00:00")
    w["previous_window"] = dict(window(), start_utc=start, end_utc=end)
    assert (
        build_futures_macro_change_reading(w)["condition_results"][0]["comparison"][
            "status"
        ]
        == "UNAVAILABLE"
    )


def test_invalid_current_window_never_displays_zero_as_observed_direction():
    from app.services.futures_macro_reading import build_futures_macro_change_reading

    r = build_futures_macro_change_reading(window(status="UNAVAILABLE", es=0, nq=0))
    assert all(
        e["return_pct"] is None for c in r["condition_results"] for e in c["evidence"]
    )
    assert r["observation_facts"] == []


@pytest.mark.parametrize(
    "old_pair,new_pair", [((1, -1), (-1, 1)), ((1, 0), (-1, 0)), ((1, 0), (0, 1))]
)
def test_same_equity_category_with_changed_component_directions_is_a_change(
    old_pair, new_pair
):
    from app.services.futures_macro_reading import build_futures_macro_change_reading

    w = dict(
        window(es=new_pair[0], nq=new_pair[1]), start_utc="2026-09-21T06:00:00+00:00"
    )
    w["previous_window"] = dict(
        window(es=old_pair[0], nq=old_pair[1]),
        start_utc="2026-09-21T05:00:00+00:00",
        end_utc="2026-09-21T06:00:00+00:00",
    )
    comparison = build_futures_macro_change_reading(w)["condition_results"][0][
        "comparison"
    ]
    assert comparison["status"] == "CHANGED"
    assert "S&P 500" in comparison["summary"] and "→" in comparison["summary"]
    assert "같은 조합" not in comparison["summary"]


@pytest.mark.parametrize(
    "es,nq,want",
    [
        (1, 2, "aligned_up"),
        (-1, -2, "aligned_down"),
        (1, -1, "divergent"),
        (1, 0, "one_flat"),
        (0, 0, "flat"),
        (None, 1, "missing"),
    ],
)
def test_equity_case_is_derived_from_actual_pair(es, nq, want):
    from app.services.futures_macro_reading import build_futures_macro_change_reading

    r = build_futures_macro_change_reading(window(es=es, nq=nq))
    c = r["condition_results"][0]
    assert c["case"] == want and len(c["evidence"]) == 2
    assert [e["return_pct"] for e in c["evidence"]] == [es, nq]
    assert c["explanation"] and c["verdict"]


@pytest.mark.parametrize(
    "zn,usd,want",
    [
        (-1, 1, "pressure"),
        (1, -1, "relief"),
        (1, 1, "rates_relief_dollar_pressure"),
        (-1, -1, "rates_pressure_dollar_relief"),
        (1, 0, "rates_relief"),
        (-1, 0, "rates_pressure"),
        (0, 1, "dollar_pressure"),
        (0, -1, "dollar_relief"),
        (0, 0, "neutral"),
        (1, None, "missing"),
    ],
)
def test_all_macro_direction_combinations_have_specific_cases(zn, usd, want):
    from app.services.futures_macro_reading import build_futures_macro_change_reading

    c = build_futures_macro_change_reading(window(zn=zn, dollar=usd))[
        "condition_results"
    ][1]
    assert c["case"] == want
    assert [e["return_pct"] for e in c["evidence"]] == [zn, usd]
    assert "단정하기 어렵습니다" not in c["explanation"]


def test_opposing_rates_and_dollar_explains_both_while_equities_rise():
    from app.services.futures_macro_reading import build_futures_macro_change_reading

    r = build_futures_macro_change_reading(window(zn=0.2, dollar=0.1))
    assert "상승" in r["headline"] and "엇갈" in r["headline"]
    assert "국채" in r["interpretation"] and "달러" in r["interpretation"]
    assert "단정하기 어렵습니다" not in r["interpretation"]


def test_prior_case_comparison_uses_real_nonoverlapping_hour_and_distinguishes_change():
    from app.services.futures_macro_reading import build_futures_macro_change_reading
    from app.services.futures_macro_windows import build_futures_macro_window_snapshot

    now = datetime(2026, 9, 21, 7, tzinfo=timezone.utc)
    rows = market_rows(now) + [raw(s, now - timedelta(hours=2), 102) for s in CORE]
    w = build_futures_macro_window_snapshot(
        rows=rows, evaluation_time=now, calendar=calendar()
    )["windows"]["last_hour"]
    prior = w["previous_window"]
    assert prior["start_utc"] == "2026-09-21T05:00:00+00:00"
    assert prior["end_utc"] == "2026-09-21T06:00:00+00:00"
    c = build_futures_macro_change_reading(w)["condition_results"][0]
    assert (
        c["case"] == "aligned_up" and c["comparison"]["previous_case"] == "aligned_down"
    )
    assert c["comparison"]["status"] == "CHANGED"


def test_missing_previous_data_never_becomes_maintained_condition():
    from app.services.futures_macro_reading import build_futures_macro_change_reading

    c = build_futures_macro_change_reading(window())["condition_results"][0]
    assert c["comparison"]["status"] == "UNAVAILABLE"


@pytest.mark.parametrize("status", ["STALE", "UNAVAILABLE"])
def test_stale_snapshot_does_not_publish_current_verdict(status):
    from app.services.futures_macro_reading import build_futures_macro_change_reading

    r = build_futures_macro_change_reading(window(status=status))
    assert all(c["case"] == "unavailable" for c in r["condition_results"])


def test_currency_gap_does_not_invent_dollar_or_hide_valid_equity_pair():
    from app.services.futures_macro_reading import build_futures_macro_change_reading

    w = window(status="PARTIAL", dollar=None)
    w["missing_symbols"] = ["6J=F"]
    c = build_futures_macro_change_reading(w)["condition_results"]
    assert c[0]["case"] == "aligned_up" and c[1]["case"] == "missing"


def test_since_close_previous_comparison_does_not_cross_new_cash_anchor():
    from app.services.futures_macro_windows import build_futures_macro_window_snapshot

    end = datetime(2026, 9, 21, 20, 30, tzinfo=timezone.utc)
    rows = [
        raw(s, t, 100)
        for s in CORE
        for t in (
            end,
            end - timedelta(hours=1),
            end - timedelta(hours=2),
            end - timedelta(minutes=30),
        )
    ]
    w = build_futures_macro_window_snapshot(
        rows=rows, evaluation_time=end, calendar=calendar()
    )["windows"]["since_close"]
    assert w["previous_window"]["status"] == "UNAVAILABLE"


def test_price_cards_name_futures_and_exact_observation_basis():
    from app.services.overview.futures_macro import (
        build_futures_macro_intraday_read_model,
    )

    p = build_futures_macro_intraday_read_model(
        window_snapshot={
            "evaluated_at_utc": "2026-09-21T07:12:00+00:00",
            "windows": {
                "since_close": dict(window(), start_utc="2026-09-18T20:00:00+00:00"),
                "last_hour": dict(window(), start_utc="2026-09-21T06:00:00+00:00"),
            },
        },
        cycle_snapshot={},
    )
    w = p["windows"]["last_hour"]
    assert w["time_context"]["observation_age_minutes"] == 12
    assert w["time_context"]["basis"] == "latest_completed_bar"
    assert "선물" in w["prices"][0]["label"]
    assert w["prices"][0]["source_symbols"] == ["ES=F"]
    assert w["prices"][3]["instrument_kind"] == "custom_proxy"
