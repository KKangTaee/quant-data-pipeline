from __future__ import annotations

import importlib

import pytest


def _bea_payload() -> dict[str, object]:
    rows: list[dict[str, str]] = []
    definitions = [
        ("1", "Personal consumption expenditures", "120.000", "120.360"),
        ("2", "Goods", "100.000", "100.400"),
        ("3", "Services", "110.000", "110.220"),
        (
            "22",
            "Personal consumption expenditures excluding food and energy",
            "118.000",
            "118.354",
        ),
        ("30", "Housing and utilities", "105.000", "105.525"),
        ("31", "Health care", "95.000", "95.095"),
    ]
    for line_number, description, may_value, june_value in definitions:
        for period, value in (("2026M05", may_value), ("2026M06", june_value)):
            rows.append(
                {
                    "TableName": "T20804",
                    "LineNumber": line_number,
                    "LineDescription": description,
                    "TimePeriod": period,
                    "CL_UNIT": "Index numbers, 2017=100",
                    "UNIT_MULT": "0",
                    "DataValue": value,
                }
            )
    return {"BEAAPI": {"Results": {"Data": rows}}}


def test_bea_component_normalization_preserves_release_and_line_identity() -> None:
    from finance.data.bea_pce_components import normalize_bea_pce_components

    rows = normalize_bea_pce_components(
        _bea_payload(),
        released_at="2026-07-30T12:30:00+00:00",
        collected_at="2026-07-30T12:35:00+00:00",
    )

    assert len(rows) == 12
    assert {row["source"] for row in rows} == {"bea_nipa_t20804"}
    assert {row["series_id"] for row in rows} >= {
        "BEA_PCE_1",
        "BEA_PCE_2",
        "BEA_PCE_3",
        "BEA_PCE_22",
    }
    assert {row["component_role"] for row in rows} >= {
        "headline",
        "goods",
        "services",
        "core",
        "detail",
    }
    assert all(row["released_at"] == "2026-07-30T12:30:00+00:00" for row in rows)


def test_component_breadth_uses_month_over_month_index_changes() -> None:
    from finance.data.bea_pce_components import (
        calculate_component_breadth,
        normalize_bea_pce_components,
    )

    rows = normalize_bea_pce_components(
        _bea_payload(),
        released_at="2026-07-30T12:30:00+00:00",
        collected_at="2026-07-30T12:35:00+00:00",
    )
    result = calculate_component_breadth(rows, threshold_pct=0.3)

    assert result["status"] == "READY"
    assert result["as_of_month"] == "2026-06-01"
    assert result["component_count"] == 4
    assert result["above_threshold_count"] == 2
    assert result["share_above_threshold"] == pytest.approx(0.5)
    assert result["aggregate_mom_pct"]["headline"] == pytest.approx(0.3)
    assert result["aggregate_mom_pct"]["core"] == pytest.approx(0.3)


def test_component_breadth_fails_closed_without_required_aggregates() -> None:
    from finance.data.bea_pce_components import calculate_component_breadth

    result = calculate_component_breadth(
        [
            {
                "series_id": "BEA_PCE_30",
                "component_role": "detail",
                "observation_date": "2026-05-01",
                "value": 100.0,
            },
            {
                "series_id": "BEA_PCE_30",
                "component_role": "detail",
                "observation_date": "2026-06-01",
                "value": 100.4,
            },
        ]
    )

    assert result["status"] == "NOT_AVAILABLE"
    assert result["reason"] == "missing_required_aggregates"
    assert set(result["missing_roles"]) == {"headline", "goods", "services", "core"}


def test_component_breadth_fails_closed_when_aggregates_have_one_month() -> None:
    from finance.data.bea_pce_components import calculate_component_breadth

    rows = [
        {
            "series_id": f"BEA_PCE_{index}",
            "component_role": role,
            "observation_date": "2026-06-01",
            "value": 100.0 + index,
        }
        for index, role in enumerate(
            ("headline", "goods", "services", "core"),
            start=1,
        )
    ]

    result = calculate_component_breadth(rows)

    assert result["status"] == "NOT_AVAILABLE"
    assert result["reason"] == "insufficient_required_history"
    assert set(result["missing_roles"]) == {"headline", "goods", "services", "core"}


def test_bea_component_store_uses_shared_vintage_table(monkeypatch) -> None:
    bea_module = importlib.import_module("finance.data.bea_pce_components")

    calls: list[tuple[str, object]] = []
    monkeypatch.setattr(bea_module, "sync_table_schema", lambda *_args: None)

    def capture(rows, *, db):
        calls.append((rows[0]["source"], db))
        return len(rows)

    monkeypatch.setattr(bea_module, "upsert_fred_vintage_rows", capture)

    class DB:
        def use_db(self, name: str) -> None:
            calls.append(("database", name))

        def execute(self, sql: str) -> None:
            calls.append(("schema", "macro_series_vintage_observation" in sql))

        def close(self) -> None:
            calls.append(("closed", True))

    db = DB()
    result = bea_module.store_bea_pce_components(
        _bea_payload(),
        released_at="2026-07-30T12:30:00+00:00",
        collected_at="2026-07-30T12:35:00+00:00",
        db_factory=lambda *_args: db,
    )

    assert result == {"status": "success", "stored": 12, "source": "bea_nipa_t20804"}
    assert ("bea_nipa_t20804", db) in calls


def test_bea_current_collection_uses_actual_collection_time(monkeypatch) -> None:
    bea_module = importlib.import_module("finance.data.bea_pce_components")
    captured: list[dict[str, object]] = []
    monkeypatch.setattr(bea_module, "sync_table_schema", lambda *_args: None)
    monkeypatch.setattr(
        bea_module,
        "upsert_fred_vintage_rows",
        lambda rows, *, db: captured.extend(rows) or len(rows),
    )

    class DB:
        def use_db(self, _name: str) -> None:
            pass

        def execute(self, _sql: str) -> None:
            pass

        def close(self) -> None:
            pass

    result = bea_module.collect_and_store_bea_pce_components(
        api_key="test-key",
        collected_at="2026-08-02T03:15:00+00:00",
        payload_fetcher=lambda _key: _bea_payload(),
        db_factory=lambda *_args: DB(),
    )

    assert result["status"] == "success"
    assert result["stored"] == 12
    assert {row["released_at"] for row in captured} == {
        "2026-08-02T03:15:00+00:00"
    }
