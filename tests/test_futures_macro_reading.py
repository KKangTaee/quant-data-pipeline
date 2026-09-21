import copy

import pytest


def window(es=0.18, nq=0.42, zn=-0.26, dollar=0.31, status="AVAILABLE", **values):
    return {
        "status": status,
        "returns_pct": {"ES=F": es, "NQ=F": nq, "ZN=F": zn, **values},
        "dollar_proxy_pct": dollar,
        "missing_symbols": [],
        "end_utc": "2026-09-21T07:00:00+00:00",
    }


def test_pressure_and_rising_equities_keep_counter_evidence():
    from app.services.futures_macro_reading import build_futures_macro_change_reading

    r = build_futures_macro_change_reading(window())
    assert "부담" in r["headline"] and "상승" in r["headline"]
    assert "국채" in " ".join(r["observation_facts"])
    assert "상승" in " ".join(r["counter_evidence"])
    assert len(r["condition_results"]) == 2
    assert "확률" not in r["headline"]


@pytest.mark.parametrize("status", ["PARTIAL", "STALE", "UNAVAILABLE"])
def test_incomplete_or_stale_data_withholds_combined_interpretation(status):
    from app.services.futures_macro_reading import build_futures_macro_change_reading

    r = build_futures_macro_change_reading(window(status=status))
    assert "보류" in r["headline"]
    assert "부담 조합" not in r["interpretation"]


def test_relief_and_falling_equities_are_not_called_support():
    from app.services.futures_macro_reading import build_futures_macro_change_reading

    r = build_futures_macro_change_reading(window(es=-1, nq=-2, zn=0.1, dollar=-0.3))
    assert "엇갈" in r["headline"]
    assert "하락" in " ".join(r["counter_evidence"])


def test_neutral_display_does_not_generate_direction_and_absent_breadth_is_not_invented():
    from app.services.futures_macro_reading import build_futures_macro_change_reading

    r = build_futures_macro_change_reading(
        window(es=0.001, nq=-0.001, zn=0.004, dollar=0.004)
    )
    assert all("상승" not in s and "하락" not in s for s in r["observation_facts"])
    assert "네 지수" not in r["headline"]


def test_giveback_requires_same_cutoff_and_positive_since_close():
    from app.services.futures_macro_reading import build_futures_macro_change_reading

    current = window(es=-0.2, nq=-0.4)
    other = window(es=0.3, nq=0.5)
    r = build_futures_macro_change_reading(current, companion_window=other)
    assert "상승분 일부 반납" in " ".join(r["observation_facts"])
    other["end_utc"] = "2026-09-21T06:00:00+00:00"
    r = build_futures_macro_change_reading(current, companion_window=other)
    assert "반납" not in " ".join(r["observation_facts"])


def test_read_model_identity_changes_for_corrections_missing_and_rule_version():
    from app.services.overview.futures_macro import (
        build_futures_macro_intraday_read_model,
    )

    snapshot = {
        "calendar_quality": "CONFIRMED",
        "windows": {"since_close": window(), "last_hour": window()},
    }

    def build(s, **kw):
        return build_futures_macro_intraday_read_model(
            window_snapshot=s,
            cycle_snapshot={"as_of_date": "2026-08-31", "observed_phase": "expansion"},
            **kw,
        )

    a = build(snapshot)
    corrected = copy.deepcopy(snapshot)
    corrected["windows"]["since_close"]["returns_pct"]["ES=F"] = 0.99
    missing = copy.deepcopy(snapshot)
    missing["windows"]["last_hour"]["missing_symbols"] = ["6J=F"]
    assert (
        len(
            {
                a["input_identity"],
                build(corrected)["input_identity"],
                build(missing)["input_identity"],
                build(snapshot, rule_version="next")["input_identity"],
            }
        )
        == 4
    )
    assert a["schema_version"] == "futures_macro_intraday_workbench_v2"
    assert a["research"]["status"] == "NOT_VALIDATED"
    assert len(a["windows"]["since_close"]["prices"]) == 6
    assert a["cycle_background"]["as_of_date"] == "2026-08-31"
