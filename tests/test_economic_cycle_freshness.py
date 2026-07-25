from datetime import date, datetime


def test_latest_refresh_date_uses_previous_friday_on_weekend() -> None:
    from app.services.overview.economic_cycle_freshness import (
        latest_economic_cycle_refresh_date,
    )

    assert latest_economic_cycle_refresh_date(date(2026, 7, 24)) == date(2026, 7, 24)
    assert latest_economic_cycle_refresh_date(date(2026, 7, 25)) == date(2026, 7, 24)
    assert latest_economic_cycle_refresh_date(datetime(2026, 7, 26, 9, 0)) == date(
        2026, 7, 24
    )


def test_stale_intramonth_exposes_manual_action() -> None:
    from app.services.overview.economic_cycle_freshness import (
        build_economic_cycle_freshness,
    )

    result = build_economic_cycle_freshness(
        {"as_of_date": "2026-07-21"},
        today=date(2026, 7, 25),
    )

    assert result["status"] == "REFRESH_AVAILABLE"
    assert result["persisted_as_of_date"] == "2026-07-21"
    assert result["target_as_of_date"] == "2026-07-24"
    assert result["refresh_required"] is True
    assert result["action"] == {
        "id": "refresh_economic_cycle_data",
        "label": "최신 데이터로 다시 계산",
        "enabled": True,
    }


def test_current_intramonth_hides_manual_action() -> None:
    from app.services.overview.economic_cycle_freshness import (
        build_economic_cycle_freshness,
    )

    result = build_economic_cycle_freshness(
        {"as_of_date": "2026-07-24"},
        today=date(2026, 7, 25),
    )

    assert result["status"] == "READY"
    assert result["refresh_required"] is False
    assert "action" not in result


def test_missing_and_read_error_remain_actionable() -> None:
    from app.services.overview.economic_cycle_freshness import (
        build_economic_cycle_freshness,
    )

    missing = build_economic_cycle_freshness(None, today=date(2026, 7, 25))
    failed = build_economic_cycle_freshness(
        None,
        today=date(2026, 7, 25),
        read_error=True,
    )

    assert missing["status"] == "MISSING"
    assert failed["status"] == "ERROR"
    assert missing["action"]["id"] == "refresh_economic_cycle_data"
    assert failed["action"]["id"] == "refresh_economic_cycle_data"
