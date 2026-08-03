from __future__ import annotations

import importlib
import math

import pytest


def test_fomc_cutoff_excludes_next_day_pce_and_null_release_rows() -> None:
    from finance.loaders.inflation_policy import load_inflation_policy_data_bundle

    captured_sql: list[str] = []

    def query(_database: str, sql: str, _params: tuple[object, ...]):
        captured_sql.append(sql)
        if "fomc_sep_distribution" in sql:
            return [
                {
                    "released_at": "2026-06-17 18:00:00",
                    "target_period": "2026",
                    "variable_name": "core_pce",
                    "distribution_kind": "HISTOGRAM",
                    "bin_label": "3.5-3.6",
                    "participant_count": 4,
                }
            ]
        if "fomc_policy_decision" in sql:
            return [
                {
                    "meeting_date": "2026-07-29",
                    "released_at": "2026-07-29 18:00:00",
                    "target_lower_after_pct": 3.5,
                    "target_upper_after_pct": 3.75,
                }
            ]
        if "series_id = 'ACMTP10'" in sql:
            return []
        if "macro_series_vintage_observation" in sql:
            return [
                {
                    "series_id": "PCEPILFE",
                    "observation_date": "2026-06-01",
                    "realtime_start": "2026-07-20",
                    "released_at": "2026-07-29 17:00:00",
                    "collected_at": "2026-07-29 17:01:00",
                    "value": 126.0,
                },
                {
                    "series_id": "PCEPILFE",
                    "observation_date": "2026-06-01",
                    "realtime_start": "2026-07-29",
                    "released_at": "2026-07-29 17:30:00",
                    "collected_at": "2026-07-29 17:31:00",
                    "value": 127.0,
                },
                {
                    "series_id": "PCEPILFE",
                    "observation_date": "2026-07-01",
                    "realtime_start": "2026-07-30",
                    "released_at": "2026-07-30 12:30:00",
                    "collected_at": "2026-07-30 12:31:00",
                    "value": 128.0,
                },
                {
                    "series_id": "PCEPI",
                    "observation_date": "2026-06-01",
                    "realtime_start": "2026-07-29",
                    "released_at": None,
                    "collected_at": "2026-07-29 12:00:00",
                    "value": 125.0,
                },
            ]
        return []

    bundle = load_inflation_policy_data_bundle(
        as_of_at="2026-07-29T18:00:00+00:00",
        history_start="2025-01-01",
        query_fn=query,
    )

    assert [(row["series_id"], row["value"]) for row in bundle.macro_rows] == [
        ("PCEPILFE", 127.0)
    ]
    assert len(bundle.sep_rows) == 1
    assert len(bundle.decision_rows) == 1
    assert bundle.term_premium_rows == ()
    assert bundle.coverage["term_premium_status"] == "NOT_AVAILABLE"
    raw_sql = [sql for sql in captured_sql if "inflation_policy_snapshot" not in sql]
    assert raw_sql
    assert all("released_at <= %s" in sql for sql in raw_sql)
    assert all("economic_cycle" not in sql for sql in captured_sql)


def test_latest_eligible_acm_collection_vintage_is_selected() -> None:
    from finance.loaders.inflation_policy import load_inflation_policy_data_bundle

    def query(_database: str, sql: str, _params: tuple[object, ...]):
        if "series_id = 'ACMTP10'" not in sql:
            return []
        return [
            {
                "series_id": "ACMTP10",
                "observation_date": "2026-07-28",
                "realtime_start": "2026-08-01",
                "released_at": "2026-08-01 12:00:00",
                "collected_at": "2026-08-01 12:00:00",
                "value": 0.71,
            },
            {
                "series_id": "ACMTP10",
                "observation_date": "2026-07-28",
                "realtime_start": "2026-08-02",
                "released_at": "2026-08-02 03:00:00",
                "collected_at": "2026-08-02 03:00:00",
                "value": 0.78,
            },
            {
                "series_id": "ACMTP10",
                "observation_date": "2026-07-28",
                "realtime_start": "2026-08-03",
                "released_at": "2026-08-03 03:00:00",
                "collected_at": "2026-08-03 03:00:00",
                "value": 0.82,
            },
        ]

    bundle = load_inflation_policy_data_bundle(
        as_of_at="2026-08-02T03:15:00+00:00",
        history_start="2026-01-01",
        query_fn=query,
    )

    assert len(bundle.term_premium_rows) == 1
    assert bundle.term_premium_rows[0]["value"] == 0.78
    assert bundle.coverage["term_premium_status"] == "LIMITED"


def test_spf_probability_loader_is_release_cutoff_safe_and_keeps_full_bins() -> None:
    from finance.loaders.inflation_policy import load_inflation_policy_data_bundle

    captured: list[tuple[str, tuple[object, ...]]] = []

    def query(_database: str, sql: str, params: tuple[object, ...]):
        if "spf_core_pce_probability" not in sql:
            return []
        captured.append((sql, params))
        return [
            {
                "survey_year": 2026,
                "survey_quarter": 2,
                "target_year": 2026,
                "bin_number": bin_number,
                "bin_label": str(bin_number),
                "mean_probability_pct": 10.0,
                "released_at": "2026-05-16 03:59:59.999999",
            }
            for bin_number in range(1, 11)
        ] + [
            {
                "survey_year": 2026,
                "survey_quarter": 3,
                "target_year": 2026,
                "bin_number": 1,
                "bin_label": ">=4.0",
                "mean_probability_pct": 100.0,
                "released_at": "2026-08-14 04:00:00",
            }
        ]

    bundle = load_inflation_policy_data_bundle(
        as_of_at="2026-08-03T03:15:00+00:00",
        history_start="2015-01-01",
        query_fn=query,
    )

    assert len(bundle.spf_rows) == 10
    assert {row["survey_quarter"] for row in bundle.spf_rows} == {2}
    assert bundle.coverage["spf_core_pce_status"] == "READY"
    assert captured and "released_at <= %s" in captured[0][0]


def test_training_vintage_loader_preserves_all_then_known_versions() -> None:
    from finance.loaders.inflation_policy import (
        load_inflation_policy_training_vintages,
    )

    captured: list[tuple[str, tuple[object, ...]]] = []

    def query(_database: str, sql: str, params: tuple[object, ...]):
        captured.append((sql, params))
        return [
            {
                "series_id": "PCEPILFE",
                "observation_date": "2026-04-01",
                "released_at": "2026-05-28 12:30:00",
                "realtime_start": "2026-05-28",
                "value": 129.6,
            },
            {
                "series_id": "PCEPILFE",
                "observation_date": "2026-04-01",
                "released_at": "2026-06-25 12:30:00",
                "realtime_start": "2026-06-25",
                "value": 129.7,
            },
            {
                "series_id": "PCEPILFE",
                "observation_date": "2026-05-01",
                "released_at": "2026-07-30 12:30:00",
                "realtime_start": "2026-07-30",
                "value": 130.2,
            },
        ]

    rows = load_inflation_policy_training_vintages(
        as_of_at="2026-07-29T18:00:00+00:00",
        history_start="2025-01-01",
        series_ids=("PCEPILFE",),
        query_fn=query,
    )

    assert [row["value"] for row in rows] == [129.6, 129.7]
    assert len(captured) == 1
    assert "released_at <= %s" in captured[0][0]
    assert "ROW_NUMBER" not in captured[0][0]


def test_invalid_snapshot_json_performs_no_database_write() -> None:
    module = importlib.import_module("finance.data.inflation_policy_results")
    opened = 0

    def factory(*_args, **_kwargs):
        nonlocal opened
        opened += 1
        raise AssertionError("invalid payload must fail before DB connection")

    row = {
        "as_of_at": "2026-08-02T03:15:00+00:00",
        "model_version": "inflation-policy-v1",
        "run_kind": "current",
        "publication_status": "LIMITED",
        "inflation_json": {"probability": math.nan},
        "policy_json": {},
        "rates_json": {},
        "reverse_json": {},
        "evidence_json": [],
        "freshness_json": {},
        "warnings_json": [],
    }

    with pytest.raises(ValueError, match="finite"):
        module.save_inflation_policy_snapshot(row, db_factory=factory)
    assert opened == 0


def test_valid_snapshot_uses_exact_business_key_upsert(monkeypatch) -> None:
    module = importlib.import_module("finance.data.inflation_policy_results")
    captured: dict[str, object] = {}
    monkeypatch.setattr(module, "sync_table_schema", lambda *_args: None)

    class DB:
        def use_db(self, _database: str) -> None:
            pass

        def execute(self, _schema: str) -> None:
            pass

        def executemany(self, sql: str, values: list[dict[str, object]]) -> None:
            captured["sql"] = sql
            captured["values"] = values

        def close(self) -> None:
            pass

    row = {
        "as_of_at": "2026-08-02T03:15:00+00:00",
        "model_version": "inflation-policy-v1",
        "run_kind": "current",
        "publication_status": "LIMITED",
        "inflation_json": {"states": [0.1, 0.2, 0.4, 0.2, 0.1]},
        "policy_json": {"hold": 0.6},
        "rates_json": {},
        "reverse_json": {},
        "evidence_json": [],
        "freshness_json": {},
        "warnings_json": ["ACM_LIMITED"],
    }

    module.save_inflation_policy_snapshot(row, db_factory=lambda *_args: DB())

    assert "ON DUPLICATE KEY UPDATE" in str(captured["sql"])
    assert "as_of_at" in str(captured["sql"])
    stored = captured["values"]
    assert isinstance(stored, list)
    assert stored[0]["inflation_json"] == '{"states":[0.1,0.2,0.4,0.2,0.1]}'


def test_latest_snapshot_respects_requested_as_of() -> None:
    from finance.loaders.inflation_policy import load_latest_inflation_policy_snapshot

    rows = [
        {
            "as_of_at": "2026-08-01 12:00:00",
            "model_version": "v1",
            "publication_status": "READY",
        },
        {
            "as_of_at": "2026-08-03 12:00:00",
            "model_version": "v2",
            "publication_status": "READY",
        },
    ]
    captured: list[str] = []

    def query(_database: str, sql: str, _params: tuple[object, ...]):
        captured.append(sql)
        return rows

    selected = load_latest_inflation_policy_snapshot(
        as_of_at="2026-08-02T00:00:00+00:00",
        query_fn=query,
    )

    assert selected is not None
    assert selected["model_version"] == "v1"
    assert "as_of_at <= %s" in captured[0]


def test_resistance_definitions_exclude_future_and_inactive_user_rows() -> None:
    from finance.loaders.inflation_policy import load_yield_resistance_definitions

    captured: list[tuple[str, tuple[object, ...]]] = []
    rows = [
        {
            "definition_id": "auto-known",
            "owner": "AUTO",
            "instrument": "DGS10",
            "known_at": "2026-07-29 12:00:00",
            "saved_at": "2026-07-29 12:01:00",
            "is_active": 1,
        },
        {
            "definition_id": "user-known",
            "owner": "USER",
            "instrument": "DGS10",
            "known_at": "2026-07-29 12:00:00",
            "saved_at": "2026-07-30 09:00:00",
            "is_active": 1,
        },
        {
            "definition_id": "user-inactive",
            "owner": "USER",
            "instrument": "DGS10",
            "known_at": "2026-07-20 12:00:00",
            "saved_at": "2026-07-20 12:01:00",
            "is_active": 0,
        },
        {
            "definition_id": "future-auto",
            "owner": "AUTO",
            "instrument": "DGS10",
            "known_at": "2026-08-03 12:00:00",
            "saved_at": "2026-08-03 12:01:00",
            "is_active": 1,
        },
    ]

    def query(_database: str, sql: str, params: tuple[object, ...]):
        captured.append((sql, params))
        return rows

    selected = load_yield_resistance_definitions(
        as_of_at="2026-08-02T00:00:00+00:00",
        query_fn=query,
    )

    assert [row["definition_id"] for row in selected] == [
        "auto-known",
        "user-known",
    ]
    assert "known_at <= %s" in captured[0][0]
    assert "saved_at <= %s" in captured[0][0]


def test_model_artifact_loader_requires_exact_version_cutoff_and_component() -> None:
    from finance.loaders.inflation_policy import load_inflation_policy_model_artifact

    rows = [
        {
            "model_version": "inflation-policy-hybrid-v1",
            "trained_cutoff_at": "2026-07-28 18:00:00",
            "component": "core_pce_hybrid",
        },
        {
            "model_version": "inflation-policy-hybrid-v1",
            "trained_cutoff_at": "2026-07-29 18:00:00",
            "component": "core_pce_momentum",
        },
        {
            "model_version": "inflation-policy-hybrid-v1",
            "trained_cutoff_at": "2026-07-29 18:00:00",
            "component": "core_pce_hybrid",
        },
    ]
    captured: list[tuple[str, tuple[object, ...]]] = []

    def query(_database: str, sql: str, params: tuple[object, ...]):
        captured.append((sql, params))
        return rows

    selected = load_inflation_policy_model_artifact(
        model_version="inflation-policy-hybrid-v1",
        trained_cutoff_at="2026-07-29T18:00:00+00:00",
        component="core_pce_hybrid",
        query_fn=query,
    )

    assert selected is not None
    assert selected["trained_cutoff_at"] == "2026-07-29 18:00:00"
    assert selected["component"] == "core_pce_hybrid"
    assert "model_version = %s" in captured[0][0]
    assert "trained_cutoff_at = %s" in captured[0][0]
    assert "component = %s" in captured[0][0]


def test_model_artifact_loader_fails_closed_when_exact_identity_is_missing() -> None:
    from finance.loaders.inflation_policy import load_inflation_policy_model_artifact

    selected = load_inflation_policy_model_artifact(
        model_version="inflation-policy-hybrid-v1",
        trained_cutoff_at="2026-07-29T18:00:00+00:00",
        component="core_pce_hybrid",
        query_fn=lambda *_args: [
            {
                "model_version": "inflation-policy-hybrid-v1",
                "trained_cutoff_at": "2026-07-28 18:00:00",
                "component": "core_pce_hybrid",
            }
        ],
    )

    assert selected is None


def test_optional_resistance_table_absence_returns_empty_definitions(monkeypatch) -> None:
    from finance.loaders import inflation_policy as module

    class MissingTableDB:
        def use_db(self, _database: str) -> None:
            pass

        def query(self, _sql: str, _params: tuple[object, ...]):
            raise RuntimeError(
                "Table 'finance_meta.yield_resistance_definition' doesn't exist"
            )

        def close(self) -> None:
            pass

    monkeypatch.setattr(module, "MySQLClient", lambda *_args: MissingTableDB())

    assert module.load_yield_resistance_definitions(
        as_of_at="2026-08-02T00:00:00+00:00"
    ) == ()


def test_result_store_exports_all_approved_persistence_boundaries() -> None:
    module = importlib.import_module("finance.data.inflation_policy_results")

    assert callable(module.save_inflation_policy_model_artifact)
    assert callable(module.save_inflation_policy_snapshot)
    assert callable(module.save_yield_resistance_definition)
    assert callable(module.save_yield_resistance_snapshot)
