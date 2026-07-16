from __future__ import annotations

import importlib
import importlib.util
import json
import math
import re
from datetime import date, datetime, timedelta, timezone
from unittest.mock import patch


def _load_catalog_module():
    spec = importlib.util.find_spec("finance.economic_cycle_catalog")
    assert spec is not None, "economic cycle catalog module must exist"
    return importlib.import_module("finance.economic_cycle_catalog")


def _load_vintage_module():
    spec = importlib.util.find_spec("finance.data.economic_cycle_vintages")
    assert spec is not None, "economic cycle vintage collector module must exist"
    return importlib.import_module("finance.data.economic_cycle_vintages")


def _load_vintage_loader_module():
    spec = importlib.util.find_spec("finance.loaders.economic_cycle")
    assert spec is not None, "economic cycle vintage loader module must exist"
    return importlib.import_module("finance.loaders.economic_cycle")


def test_economic_cycle_catalog_locks_roles_and_unique_series() -> None:
    module = _load_catalog_module()

    catalog = module.get_economic_cycle_catalog()
    series_ids = [item.series_id for item in catalog]

    assert len(catalog) == 17
    assert len(series_ids) == len(set(series_ids))
    assert sum(item.role == "label_anchor" for item in catalog) == 1
    assert {item.series_id for item in catalog} == {
        "INDPRO",
        "W875RX1",
        "RRSFS",
        "CFNAI",
        "PAYEMS",
        "UNRATE",
        "ICSA",
        "AWHMAN",
        "PERMIT",
        "USALOLITOAASTSAM",
        "T10Y3M",
        "BAMLH0A0HYM2",
        "ANFCI",
        "PCEPILFE",
        "T10YIE",
        "FEDFUNDS",
        "USREC",
    }
    assert all(
        item.role != "phase_forecast"
        for item in catalog
        if item.factor in {"financial_leading", "inflation_policy"}
    )


def test_macro_vintage_schema_preserves_revision_interval_fields() -> None:
    from finance.data.db.schema import PROVIDER_SCHEMAS

    sql = PROVIDER_SCHEMAS["macro_series_vintage_observation"]

    for column in (
        "series_id",
        "observation_date",
        "realtime_start",
        "realtime_end",
        "source_mode",
        "factor_group",
        "release_lag_days",
        "missing_fields_json",
    ):
        assert re.search(rf"\b{column}\b", sql)
    assert "DECIMAL(24,10)" in sql


def test_macro_vintage_schema_locks_business_key_and_access_indexes() -> None:
    from finance.data.db.schema import PROVIDER_SCHEMAS

    compact_sql = " ".join(
        PROVIDER_SCHEMAS["macro_series_vintage_observation"].split()
    )

    assert (
        "UNIQUE KEY uk_series_observation_realtime_source "
        "(series_id, observation_date, realtime_start, source)"
    ) in compact_sql
    assert (
        "KEY ix_series_realtime_observation "
        "(series_id, realtime_start, observation_date)"
    ) in compact_sql
    assert "KEY ix_factor_observation (factor_group, observation_date)" in compact_sql


class _Response:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, object]:
        return self._payload


class _PagedSession:
    def __init__(self) -> None:
        self.urls: list[str] = []
        self.params: list[dict[str, object]] = []

    def get(self, url: str, *, params: dict[str, object], timeout: int):
        assert timeout == 20
        self.urls.append(url)
        self.params.append(dict(params))
        if url.endswith("/series/vintagedates"):
            return _Response(
                {
                    "count": 3,
                    "vintage_dates": [
                        "2020-02-01",
                        "2020-04-01",
                        "2020-05-01",
                    ],
                }
            )
        offset = int(params["offset"])
        pages = {
            0: {
                "count": 3,
                "observations": [
                    {
                        "date": "2020-01-01",
                        "realtime_start": "2020-02-01",
                        "realtime_end": "2020-03-31",
                        "value": "100.0",
                    },
                    {
                        "date": "2020-01-01",
                        "realtime_start": "2020-04-01",
                        "realtime_end": "9999-12-31",
                        "value": "101.0",
                    },
                ],
            },
            2: {
                "count": 3,
                "observations": [
                    {
                        "date": "2020-02-01",
                        "realtime_start": "2020-03-01",
                        "realtime_end": "9999-12-31",
                        "value": "102.0",
                    }
                ],
            },
        }
        return _Response(pages[offset])


def test_fetch_fred_vintages_paginates_and_preserves_versions() -> None:
    module = _load_vintage_module()
    session = _PagedSession()

    rows = module.fetch_fred_vintages(
        "PAYEMS", api_key="x" * 32, session=session, limit=2
    )

    assert len(rows) == 3
    observation_params = [
        params
        for url, params in zip(session.urls, session.params)
        if url.endswith("/series/observations")
    ]
    assert [params["offset"] for params in observation_params] == [0, 2]
    assert all(params["output_type"] == 1 for params in observation_params)
    assert all(
        params["realtime_start"] == "1776-07-04"
        for params in observation_params
    )
    assert all(
        params["realtime_end"] == "9999-12-31"
        for params in observation_params
    )
    assert [row["realtime_start"] for row in rows[:2]] == [
        "2020-02-01",
        "2020-04-01",
    ]


def test_fetch_fred_vintages_splits_more_than_2000_vintage_dates() -> None:
    module = _load_vintage_module()
    first = date(2018, 1, 1)
    vintage_dates = [
        (first + timedelta(days=offset)).isoformat() for offset in range(2001)
    ]

    class Session:
        def __init__(self) -> None:
            self.observation_params: list[dict[str, object]] = []

        def get(self, url: str, *, params: dict[str, object], timeout: int):
            assert timeout == 20
            if url.endswith("/series/vintagedates"):
                return _Response(
                    {"count": len(vintage_dates), "vintage_dates": vintage_dates}
                )
            self.observation_params.append(dict(params))
            return _Response({"count": 0, "observations": []})

    session = Session()
    assert (
        module.fetch_fred_vintages(
            "T10Y3M", api_key="x" * 32, session=session, limit=2
        )
        == []
    )

    assert len(session.observation_params) == 2
    first_window, second_window = session.observation_params
    assert first_window["realtime_start"] == "1776-07-04"
    assert first_window["realtime_end"] == (
        date.fromisoformat(vintage_dates[2000]) - timedelta(days=1)
    ).isoformat()
    assert second_window["realtime_start"] == vintage_dates[2000]
    assert second_window["realtime_end"] == "9999-12-31"
    assert all(item["output_type"] == 1 for item in session.observation_params)


def test_session_http_failure_does_not_expose_api_key() -> None:
    module = _load_vintage_module()
    secret = "sensitive-test-key"

    class Response:
        status_code = 403

        def raise_for_status(self) -> None:
            raise RuntimeError(f"request failed with api_key={secret}")

    class Session:
        def get(self, *_args, **_kwargs):
            return Response()

    try:
        module.fetch_fred_vintage_dates(
            "PAYEMS",
            api_key=secret,
            session=Session(),
        )
    except module.EconomicCycleVintageError as exc:
        assert secret not in str(exc)
        assert "403" in str(exc)
    else:
        raise AssertionError("provider error must fail the vintage request")


def test_collect_vintages_upserts_each_page_without_accumulating_all_rows() -> None:
    module = _load_vintage_module()
    session = _PagedSession()

    class Connection:
        def __init__(self) -> None:
            self.batch_sizes: list[int] = []

        def executemany(self, _sql: str, values: list[dict[str, object]]) -> None:
            self.batch_sizes.append(len(values))

    connection = Connection()
    summary = module.collect_economic_cycle_vintages(
        series_ids=["PAYEMS"],
        api_key="x" * 32,
        connection=connection,
        session=session,
        page_size=2,
    )

    assert summary["stored"] == 3
    assert connection.batch_sizes == [2, 1]


def test_collect_vintages_reuses_one_owned_database_connection() -> None:
    module = _load_vintage_module()
    session = _PagedSession()

    class Connection:
        def __init__(self) -> None:
            self.batch_sizes: list[int] = []
            self.databases: list[str] = []
            self.closed = False

        def use_db(self, database: str) -> None:
            self.databases.append(database)

        def execute(self, _sql: str) -> None:
            return None

        def executemany(self, _sql: str, values: list[dict[str, object]]) -> None:
            self.batch_sizes.append(len(values))

        def close(self) -> None:
            self.closed = True

    connection = Connection()
    with (
        patch.object(module, "MySQLClient", return_value=connection) as client,
        patch.object(module, "sync_table_schema") as sync_schema,
    ):
        summary = module.collect_economic_cycle_vintages(
            series_ids=["PAYEMS"],
            api_key="x" * 32,
            session=session,
            page_size=2,
        )

    assert summary["stored"] == 3
    assert connection.batch_sizes == [2, 1]
    assert connection.databases == ["finance_meta"]
    assert connection.closed is True
    client.assert_called_once_with("localhost", "root", "1234", 3306)
    sync_schema.assert_called_once()


def test_upsert_uses_larger_safe_statement_for_mysql_connection() -> None:
    catalog = _load_catalog_module()
    module = _load_vintage_module()
    rows = module.normalize_fred_vintage_rows(
        catalog.get_indicator_spec("PAYEMS"),
        [
            {
                "date": "2020-01-01",
                "realtime_start": "2020-02-01",
                "realtime_end": "9999-12-31",
                "value": "100",
            }
        ],
        collected_at=datetime(2026, 7, 16, tzinfo=timezone.utc),
    )

    class Cursor:
        def __init__(self) -> None:
            self.max_stmt_length = 1_024_000
            self.batch_size = 0

        def __enter__(self):
            return self

        def __exit__(self, *_args) -> None:
            return None

        def executemany(self, _sql: str, values: list[dict[str, object]]) -> None:
            self.batch_size = len(values)

    cursor = Cursor()

    class RawConnection:
        def cursor(self):
            return cursor

    class Connection:
        conn = RawConnection()

        def executemany(self, *_args) -> None:
            raise AssertionError("raw MySQL cursor should own the optimized batch")

    stored = module.upsert_economic_cycle_vintages(rows, connection=Connection())

    assert stored == 1
    assert cursor.batch_size == 1
    assert cursor.max_stmt_length == 16 * 1024 * 1024


def test_normalize_fred_vintage_rows_keeps_missing_values_explicit() -> None:
    catalog = _load_catalog_module()
    module = _load_vintage_module()
    spec = catalog.get_indicator_spec("PAYEMS")
    collected_at = datetime(2026, 7, 16, tzinfo=timezone.utc)

    rows = module.normalize_fred_vintage_rows(
        spec,
        [
            {
                "date": "2020-01-01",
                "realtime_start": "2020-02-07",
                "realtime_end": "9999-12-31",
                "value": ".",
            },
            {
                "date": "2020-02-01",
                "realtime_start": "2020-03-06",
                "realtime_end": "9999-12-31",
                "value": math.inf,
            },
        ],
        collected_at=collected_at,
    )

    assert [row["value"] for row in rows] == [None, None]
    assert {row["coverage_status"] for row in rows} == {"missing"}
    assert all(json.loads(row["missing_fields_json"]) == ["value"] for row in rows)
    assert all(row["collected_at"] == "2026-07-16 00:00:00" for row in rows)


def test_collect_vintages_fails_before_http_or_db_without_api_key() -> None:
    module = _load_vintage_module()
    calls: list[str] = []

    class Connection:
        def executemany(self, *_args, **_kwargs):
            calls.append("db")

    with patch.dict("os.environ", {}, clear=True):
        try:
            module.collect_economic_cycle_vintages(
                series_ids=["PAYEMS"], api_key=None, connection=Connection()
            )
        except module.EconomicCycleVintageError as exc:
            assert "FRED_API_KEY" in str(exc)
        else:
            raise AssertionError("missing API key must fail closed")

    assert calls == []


def test_upsert_vintages_uses_stable_business_key_on_retries() -> None:
    catalog = _load_catalog_module()
    module = _load_vintage_module()
    spec = catalog.get_indicator_spec("PAYEMS")
    rows = module.normalize_fred_vintage_rows(
        spec,
        [
            {
                "date": "2020-01-01",
                "realtime_start": "2020-02-01",
                "realtime_end": "2020-03-31",
                "value": "100",
            },
            {
                "date": "2020-01-01",
                "realtime_start": "2020-04-01",
                "realtime_end": "9999-12-31",
                "value": "101",
            },
        ],
        collected_at=datetime(2026, 7, 16, tzinfo=timezone.utc),
    )

    class Connection:
        def __init__(self) -> None:
            self.rows: dict[tuple[object, ...], dict[str, object]] = {}
            self.sql = ""

        def executemany(self, sql: str, values: list[dict[str, object]]) -> None:
            self.sql = sql
            for row in values:
                key = (
                    row["series_id"],
                    row["observation_date"],
                    row["realtime_start"],
                    row["source"],
                )
                self.rows[key] = dict(row)

    connection = Connection()
    assert module.upsert_economic_cycle_vintages(rows, connection=connection) == 2
    assert module.upsert_economic_cycle_vintages(rows, connection=connection) == 2
    assert len(connection.rows) == 2
    assert "ON DUPLICATE KEY UPDATE" in connection.sql


def test_normalize_vintage_retains_negative_release_lag_warning() -> None:
    catalog = _load_catalog_module()
    module = _load_vintage_module()

    row = module.normalize_fred_vintage_rows(
        catalog.get_indicator_spec("PAYEMS"),
        [
            {
                "date": "2020-02-01",
                "realtime_start": "2020-01-31",
                "realtime_end": "9999-12-31",
                "value": "1",
            }
        ],
        collected_at=datetime(2026, 7, 16, tzinfo=timezone.utc),
    )[0]

    assert row["release_lag_days"] == -1
    assert row["coverage_status"] == "partial"
    assert row["error_msg"] == "negative_release_lag"


def _revision_fixture() -> list[dict[str, object]]:
    return [
        {
            "series_id": "PAYEMS",
            "observation_date": "2020-01-01",
            "realtime_start": "2020-02-01",
            "realtime_end": "2021-12-31",
            "source": "fred",
            "factor_group": "labor_income",
            "frequency": "monthly",
            "value": 100.0,
            "coverage_status": "actual",
            "updated_at": "2020-02-01 10:00:00",
        },
        {
            "series_id": "PAYEMS",
            "observation_date": "2020-01-01",
            "realtime_start": "2022-01-01",
            "realtime_end": "9999-12-31",
            "source": "fred",
            "factor_group": "labor_income",
            "frequency": "monthly",
            "value": 110.0,
            "coverage_status": "actual",
            "updated_at": "2022-01-01 10:00:00",
        },
    ]


def test_as_of_loader_selects_revision_eligible_at_each_origin() -> None:
    module = _load_vintage_loader_module()
    fixture = _revision_fixture()

    def query_fn(_database: str, _sql: str, _params: tuple[object, ...]):
        return fixture

    early = module.load_economic_cycle_vintages(
        ["PAYEMS"],
        start_date="2020-01-01",
        end_date="2020-01-31",
        as_of_date="2020-06-30",
        query_fn=query_fn,
    )
    late = module.load_economic_cycle_vintages(
        ["PAYEMS"],
        start_date="2020-01-01",
        end_date="2020-01-31",
        as_of_date="2022-06-30",
        query_fn=query_fn,
    )

    assert [row["value"] for row in early] == [100.0]
    assert [row["value"] for row in late] == [110.0]


def test_as_of_loader_excludes_unreleased_observation() -> None:
    module = _load_vintage_loader_module()

    def query_fn(_database: str, _sql: str, _params: tuple[object, ...]):
        return [
            {
                **_revision_fixture()[0],
                "observation_date": "2020-05-01",
                "realtime_start": "2020-07-01",
                "realtime_end": "9999-12-31",
            }
        ]

    rows = module.load_economic_cycle_vintages(
        ["PAYEMS"],
        start_date="2020-01-01",
        end_date="2020-05-31",
        as_of_date="2020-06-30",
        query_fn=query_fn,
    )

    assert rows == []


def test_as_of_loader_uses_latest_retry_inside_same_revision_interval() -> None:
    module = _load_vintage_loader_module()
    older = _revision_fixture()[0]
    newer = {
        **older,
        "value": 101.0,
        "updated_at": "2020-02-02 10:00:00",
    }

    rows = module.load_economic_cycle_vintages(
        ["PAYEMS"],
        start_date="2020-01-01",
        end_date="2020-01-31",
        as_of_date="2020-06-30",
        query_fn=lambda *_args: [older, newer],
    )

    assert [row["value"] for row in rows] == [101.0]


def test_as_of_loader_query_is_parameterized_and_bounded() -> None:
    module = _load_vintage_loader_module()
    captured: dict[str, object] = {}

    def query_fn(database: str, sql: str, params: tuple[object, ...]):
        captured.update(database=database, sql=sql, params=params)
        return []

    rows = module.load_economic_cycle_vintages(
        ["PAYEMS", "INDPRO"],
        start_date="2019-01-01",
        end_date="2020-01-31",
        as_of_date="2020-02-29",
        query_fn=query_fn,
    )

    assert rows == []
    assert captured["database"] == "finance_meta"
    sql = str(captured["sql"])
    assert "ROW_NUMBER() OVER" in sql
    assert "realtime_start <= %s" in sql
    assert "realtime_end >= %s" in sql
    assert "PAYEMS" not in sql and "2020-02-29" not in sql
    assert tuple(captured["params"]) == (
        "PAYEMS",
        "INDPRO",
        "2019-01-01",
        "2020-01-31",
        "2020-02-29",
        "2020-02-29",
    )


def test_history_loader_returns_all_intervals_that_can_affect_requested_origins() -> None:
    module = _load_vintage_loader_module()
    captured: dict[str, object] = {}
    fixture = _revision_fixture() + [
        {
            **_revision_fixture()[0],
            "series_id": "INDPRO",
            "observation_date": "2021-01-01",
            "realtime_start": "2021-02-01",
            "realtime_end": "9999-12-31",
        },
        {
            **_revision_fixture()[0],
            "observation_date": "2018-01-01",
            "realtime_start": "2018-02-01",
            "realtime_end": "2018-12-31",
        },
    ]

    def query_fn(database: str, sql: str, params: tuple[object, ...]):
        captured.update(database=database, sql=sql, params=params)
        return fixture

    rows = module.load_economic_cycle_vintage_history(
        ["PAYEMS"],
        start_date="2019-01-01",
        end_date="2020-12-31",
        as_of_date="2022-06-30",
        query_fn=query_fn,
    )

    assert [row["value"] for row in rows] == [100.0, 110.0]
    assert captured["database"] == "finance_meta"
    sql = str(captured["sql"])
    assert "ROW_NUMBER() OVER" not in sql
    assert "realtime_start <= %s" in sql
    assert "realtime_end >= %s" in sql
    assert "PAYEMS" not in sql and "2022-06-30" not in sql
    assert tuple(captured["params"]) == (
        "PAYEMS",
        "2019-01-01",
        "2020-12-31",
        "2022-06-30",
        "2019-01-01",
    )
