from __future__ import annotations


def test_catalog_has_independent_required_groups() -> None:
    from finance.inflation_policy_catalog import get_inflation_policy_catalog

    catalog = get_inflation_policy_catalog()
    ids = {item.series_id for item in catalog}

    assert len(ids) == len(catalog)
    assert {"PCEPI", "PCEPILFE", "CPIAUCSL", "CPILFESL"} <= ids
    assert {"UNRATE", "PAYEMS", "ICSA", "INDPRO", "PCEC96"} <= ids
    assert {"FEDFUNDS", "DGS2", "DGS10", "DFII10", "T10YIE"} <= ids
    assert {item.group for item in catalog} >= {
        "inflation",
        "labor_cost",
        "activity",
        "policy",
        "rates",
    }


def test_catalog_locks_release_policy_and_model_roles() -> None:
    from finance.inflation_policy_catalog import get_inflation_policy_catalog

    by_id = {item.series_id: item for item in get_inflation_policy_catalog()}

    assert by_id["PCEPI"].release_policy == "OFFICIAL_0830_ET"
    assert by_id["PCEPILFE"].required_for == ("inflation", "policy")
    assert by_id["DGS10"].release_policy == "END_OF_DAY_ET"
    assert by_id["DGS10"].required_for == ("rates", "reverse")
    assert by_id["DFII10"].transform == "level"


def test_catalog_collection_uses_generic_fred_boundary(monkeypatch) -> None:
    import finance.inflation_policy_catalog as catalog_module

    spec = catalog_module.InflationPolicySeriesSpec(
        series_id="PCEPILFE",
        group="inflation",
        frequency="monthly",
        transform="index_mom_q4q4",
        required_for=("inflation", "policy"),
        release_policy="OFFICIAL_0830_ET",
    )
    calls: list[tuple[str, object]] = []

    monkeypatch.setattr(
        catalog_module,
        "fetch_fred_vintages",
        lambda series_id, **_kwargs: [
            {
                "date": "2026-06-01",
                "realtime_start": "2026-07-30",
                "realtime_end": "9999-12-31",
                "value": "126.4",
            }
        ],
    )

    def capture_upsert(rows, *, db):
        calls.append((rows[0]["series_id"], db))
        return len(rows)

    monkeypatch.setattr(catalog_module, "upsert_fred_vintage_rows", capture_upsert)
    monkeypatch.setattr(catalog_module, "sync_table_schema", lambda *_args: None)

    class DB:
        def use_db(self, name: str) -> None:
            calls.append(("database", name))

        def execute(self, sql: str) -> None:
            calls.append(("schema", "macro_series_vintage_observation" in sql))

        def close(self) -> None:
            calls.append(("closed", True))

    db = DB()
    result = catalog_module.collect_inflation_policy_vintages(
        catalog=[spec],
        api_key="x" * 32,
        db_factory=lambda *_args: db,
    )

    assert result["status"] == "success"
    assert result["stored"] == 1
    assert result["coverage"] == {"PCEPILFE": 1}
    assert ("PCEPILFE", db) in calls

