from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest


class _Response:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, object]:
        return self._payload


def test_release_policies_use_verified_new_york_clock_and_dst() -> None:
    from finance.data.fred_vintages import resolve_released_at

    assert (
        resolve_released_at("2026-07-30", release_policy="OFFICIAL_0830_ET")
        == "2026-07-30T12:30:00+00:00"
    )
    assert (
        resolve_released_at("2026-01-30", release_policy="OFFICIAL_1000_ET")
        == "2026-01-30T15:00:00+00:00"
    )


def test_unknown_intraday_release_uses_conservative_end_of_day() -> None:
    from finance.data.fred_vintages import resolve_released_at

    assert (
        resolve_released_at("2026-07-30", release_policy="END_OF_DAY_ET")
        == "2026-07-31T03:59:59.999999+00:00"
    )


def test_unknown_release_policy_fails_closed() -> None:
    from finance.data.fred_vintages import FredVintageError, resolve_released_at

    with pytest.raises(FredVintageError, match="release policy"):
        resolve_released_at("2026-07-30", release_policy="MIDNIGHT")


def test_realtime_windows_honor_explicit_chunk_size_and_lower_bound() -> None:
    from finance.data.fred_vintages import build_realtime_windows

    assert build_realtime_windows(
        ["2026-01-05", "2026-01-10", "2026-01-20"],
        lower_bound="2026-01-01",
        chunk_size=2,
    ) == [
        ("2026-01-01", "2026-01-19"),
        ("2026-01-20", "9999-12-31"),
    ]


def test_fetch_fred_vintages_preserves_incremental_realtime_start() -> None:
    from finance.data.fred_vintages import fetch_fred_vintages

    class Session:
        def __init__(self) -> None:
            self.requests: list[tuple[str, dict[str, object]]] = []

        def get(
            self, url: str, *, params: dict[str, object], timeout: int
        ) -> _Response:
            assert timeout == 60
            self.requests.append((url, dict(params)))
            if url.endswith("/series/vintagedates"):
                return _Response({"count": 1, "vintage_dates": ["2026-07-03"]})
            return _Response(
                {
                    "count": 1,
                    "observations": [
                        {
                            "date": "2026-06-01",
                            "realtime_start": "2026-07-03",
                            "realtime_end": "9999-12-31",
                            "value": "159000",
                        }
                    ],
                }
            )

    session = Session()
    rows = fetch_fred_vintages(
        "PAYEMS",
        api_key="x" * 32,
        session=session,
        realtime_start="2026-07-03",
    )

    assert len(rows) == 1
    assert session.requests[0][1]["realtime_start"] == "2026-07-03"
    assert session.requests[1][1]["realtime_start"] == "2026-07-03"


def test_normalization_attaches_release_time_without_cycle_dependency() -> None:
    from finance.data.fred_vintages import normalize_fred_vintage_rows

    spec = SimpleNamespace(
        series_id="PCEPILFE",
        group="inflation",
        frequency="monthly",
        release_policy="OFFICIAL_0830_ET",
    )
    rows = normalize_fred_vintage_rows(
        spec,
        [
            {
                "date": "2026-06-01",
                "realtime_start": "2026-07-30",
                "realtime_end": "9999-12-31",
                "value": "126.4",
            }
        ],
        collected_at=datetime(2026, 7, 30, 13, 0, tzinfo=timezone.utc),
    )

    assert rows[0]["factor_group"] == "inflation"
    assert rows[0]["released_at"] == "2026-07-30T12:30:00+00:00"
    assert rows[0]["collected_at"] == "2026-07-30 13:00:00"


def test_generic_upsert_persists_released_at_and_is_idempotent_sql() -> None:
    from finance.data.fred_vintages import upsert_fred_vintage_rows

    captured: dict[str, object] = {}

    class DB:
        def executemany(
            self, sql: str, values: list[dict[str, object]]
        ) -> None:
            captured["sql"] = sql
            captured["values"] = values

    rows = [
        {
            "series_id": "PCEPILFE",
            "observation_date": "2026-06-01",
            "realtime_start": "2026-07-30",
            "realtime_end": "9999-12-31",
            "released_at": "2026-07-30T12:30:00+00:00",
            "source": "fred",
            "source_type": "official",
            "source_mode": "fred_output_type_1_realtime_intervals",
            "source_ref": "https://fred.stlouisfed.org/series/PCEPILFE",
            "series_name": "PCEPILFE",
            "factor_group": "inflation",
            "frequency": "monthly",
            "units": None,
            "value": 126.4,
            "release_lag_days": 59,
            "coverage_status": "actual",
            "missing_fields_json": "[]",
            "collected_at": "2026-07-30 13:00:00",
            "error_msg": None,
        }
    ]

    assert upsert_fred_vintage_rows(rows, db=DB()) == 1
    assert "released_at" in str(captured["sql"])
    assert "ON DUPLICATE KEY UPDATE" in str(captured["sql"])
    stored = captured["values"]
    assert isinstance(stored, list)
    assert stored[0]["series_id"] == "PCEPILFE"
    assert stored[0]["released_at"] == "2026-07-30 12:30:00.000000"
