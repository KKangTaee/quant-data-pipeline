from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest


FIXTURE = Path(__file__).parent / "fixtures" / "fomc_sep_20260617_excerpt.html"
STATEMENT_FIXTURE = (
    Path(__file__).parent / "fixtures" / "fomc_statement_20260729_excerpt.html"
)
SOURCE_URL = "https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20260617.htm"
STATEMENT_URL = (
    "https://www.federalreserve.gov/newsevents/pressreleases/monetary20260729a.htm"
)


def _parse_fixture() -> list[dict[str, object]]:
    from finance.data.fomc_policy import parse_fomc_sep_distributions

    return parse_fomc_sep_distributions(
        FIXTURE.read_text(),
        source_url=SOURCE_URL,
        released_at="2026-06-17T18:00:00+00:00",
        collected_at="2026-06-17T18:05:00+00:00",
    )


def test_june_2026_sep_counts_stay_anonymous() -> None:
    rows = _parse_fixture()

    rate = {
        (row["bin_value_pct"], row["participant_count"])
        for row in rows
        if row["variable_name"] == "federal_funds_rate"
        and row["distribution_kind"] == "DOT"
        and row["target_period"] == "2026"
    }
    assert {(4.125, 5), (4.375, 1), (3.625, 8), (3.875, 3), (3.375, 1)} <= rate

    core = [
        row
        for row in rows
        if row["variable_name"] == "core_pce"
        and row["distribution_kind"] == "HISTOGRAM"
        and row["bin_label"] == "3.5-3.6"
        and row["target_period"] == "2026"
    ]
    assert core[0]["participant_count"] == 4
    assert all("participant_id" not in row for row in rows)


def test_sep_parser_preserves_summary_and_current_release_histogram() -> None:
    rows = _parse_fixture()

    core_median = next(
        row
        for row in rows
        if row["variable_name"] == "core_pce"
        and row["distribution_kind"] == "SUMMARY"
        and row["target_period"] == "2026"
        and row["bin_label"] == "median"
    )
    assert core_median["bin_value_pct"] == 3.3

    rate_hist = {
        row["bin_label"]: row["participant_count"]
        for row in rows
        if row["variable_name"] == "federal_funds_rate"
        and row["distribution_kind"] == "HISTOGRAM"
        and row["target_period"] == "2026"
    }
    assert rate_hist["4.13-4.37"] == 5
    assert sum(rate_hist.values()) == 18


def test_sep_parser_rejects_inconsistent_current_participant_total() -> None:
    from finance.data.fomc_policy import parse_fomc_sep_distributions

    broken = FIXTURE.read_text().replace(
        "<tr><th>3.5- 3.6</th><td></td><td>4</td>",
        "<tr><th>3.5- 3.6</th><td></td><td>3</td>",
        1,
    )

    with pytest.raises(ValueError, match="participant total"):
        parse_fomc_sep_distributions(
            broken,
            source_url=SOURCE_URL,
            released_at="2026-06-17T18:00:00+00:00",
            collected_at="2026-06-17T18:05:00+00:00",
        )


def test_projection_url_discovery_uses_official_accessible_pages() -> None:
    from finance.data.fomc_policy import discover_fomc_projection_urls

    calendar = """
      <a href="/monetarypolicy/fomcprojtabl20260617.htm">Accessible SEP</a>
      <a href="/monetarypolicy/files/fomcprojtabl20260617.pdf">PDF</a>
      <a href="/monetarypolicy/fomcprojtabl20260318.htm">Earlier SEP</a>
    """

    assert discover_fomc_projection_urls(calendar) == [
        "https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20260318.htm",
        "https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20260617.htm",
    ]


def test_sep_upsert_uses_release_distribution_business_key() -> None:
    from finance.data.fomc_policy import upsert_fomc_sep_distributions

    captured: dict[str, object] = {}

    class DB:
        def executemany(self, sql: str, values: list[dict[str, object]]) -> None:
            captured["sql"] = sql
            captured["values"] = values

    rows = _parse_fixture()
    assert upsert_fomc_sep_distributions(rows, db=DB()) == len(rows)
    assert "ON DUPLICATE KEY UPDATE" in str(captured["sql"])
    assert "released_at" in str(captured["sql"])
    assert captured["values"] == rows


def test_collect_and_store_sep_discovers_release_and_syncs_schema(monkeypatch) -> None:
    module = importlib.import_module("finance.data.fomc_policy")

    calendar_url = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
    calendar = f'<a href="{SOURCE_URL}">June projections</a>'
    page = FIXTURE.read_text()
    fetched: list[str] = []
    synced: list[tuple[str, str]] = []

    def fetch_html(url: str) -> str:
        fetched.append(url)
        return calendar if url == calendar_url else page

    monkeypatch.setattr(
        module,
        "sync_table_schema",
        lambda _db, table, _schema, database: synced.append((table, database)),
        raising=False,
    )

    class DB:
        def __init__(self) -> None:
            self.database = ""
            self.schemas: list[str] = []
            self.rows: list[dict[str, object]] = []

        def use_db(self, database: str) -> None:
            self.database = database

        def execute(self, sql: str) -> None:
            self.schemas.append(sql)

        def executemany(self, _sql: str, values: list[dict[str, object]]) -> None:
            self.rows.extend(values)

    db = DB()
    result = module.collect_and_store_fomc_sep_distributions(
        calendar_url=calendar_url,
        connection=db,
        fetch_html=fetch_html,
        collected_at="2026-06-17T18:05:00+00:00",
    )

    assert fetched == [calendar_url, SOURCE_URL]
    assert result == {"releases": 1, "stored": len(db.rows)}
    assert db.database == "finance_meta"
    assert synced == [("fomc_sep_distribution", "finance_meta")]
    assert {row["released_at"] for row in db.rows} == {"2026-06-17 18:00:00.000000"}


def test_july_2026_hold_and_three_hike_dissents_are_preserved() -> None:
    from finance.data.fomc_policy import parse_fomc_policy_decision

    row = parse_fomc_policy_decision(
        STATEMENT_FIXTURE.read_text(),
        source_url=STATEMENT_URL,
        released_at="2026-07-29T18:00:00+00:00",
        prior_range=(3.50, 3.75),
        collected_at="2026-07-29T18:02:00+00:00",
    )

    assert (row["target_lower_after_pct"], row["target_upper_after_pct"]) == (
        3.50,
        3.75,
    )
    assert row["target_lower_before_pct"] == 3.50
    assert row["target_upper_before_pct"] == 3.75
    assert row["vote_total_count"] == 12
    assert row["vote_for_count"] == 9
    assert row["vote_against_count"] == 3
    dissents = json.loads(str(row["dissents_json"]))
    assert {item["preferred_action"] for item in dissents} == {"HIKE_25"}
    assert {item["member_name"] for item in dissents} == {
        "Beth M. Hammack",
        "Neel Kashkari",
        "Lorie K. Logan",
    }
    assert row["coverage_status"] == "READY"


def test_decision_without_prior_range_is_partial_not_future_filled() -> None:
    from finance.data.fomc_policy import parse_fomc_policy_decision

    row = parse_fomc_policy_decision(
        STATEMENT_FIXTURE.read_text(),
        source_url=STATEMENT_URL,
        released_at="2026-07-29T18:00:00+00:00",
        prior_range=None,
        collected_at="2026-07-29T18:02:00+00:00",
    )

    assert row["target_lower_before_pct"] is None
    assert row["target_upper_before_pct"] is None
    assert row["coverage_status"] == "PARTIAL"


def test_policy_history_collects_oldest_first_without_future_fill(monkeypatch) -> None:
    module = importlib.import_module("finance.data.fomc_policy")
    calendar_url = "https://www.federalreserve.gov/newsevents/pressreleases/2026-press-fomc.htm"
    june_url = (
        "https://www.federalreserve.gov/newsevents/pressreleases/monetary20260617a.htm"
    )
    calendar = f'<a href="{STATEMENT_URL}">July</a><a href="{june_url}">June</a>'
    july_page = STATEMENT_FIXTURE.read_text()
    june_page = (
        july_page.replace("July 29, 2026", "June 17, 2026")
        .replace("9 – 3 vote", "12 – 0 vote")
        .replace(
            '<p>Voting against the monetary policy action were Beth M. Hammack, Neel Kashkari, and Lorie K. Logan, who preferred to raise the target range for the federal funds rate by 1/4 percentage point at this meeting.</p>',
            "",
        )
    )
    fetched: list[str] = []
    synced: list[tuple[str, str]] = []

    def fetch_html(url: str) -> str:
        fetched.append(url)
        if url == calendar_url:
            return calendar
        return june_page if url == june_url else july_page

    monkeypatch.setattr(
        module,
        "sync_table_schema",
        lambda _db, table, _schema, database: synced.append((table, database)),
    )

    class DB:
        def __init__(self) -> None:
            self.rows: list[dict[str, object]] = []

        def use_db(self, _database: str) -> None:
            pass

        def execute(self, _sql: str) -> None:
            pass

        def executemany(self, _sql: str, values: list[dict[str, object]]) -> None:
            self.rows.extend(values)

    db = DB()
    result = module.collect_and_store_fomc_policy_history(
        calendar_url=calendar_url,
        connection=db,
        fetch_html=fetch_html,
        collected_at="2026-07-29T18:02:00+00:00",
    )

    assert fetched == [calendar_url, june_url, STATEMENT_URL]
    assert result == {"meetings": 2, "stored": 2}
    assert synced == [("fomc_policy_decision", "finance_meta")]
    assert db.rows[0]["meeting_date"] == "2026-06-17"
    assert db.rows[0]["coverage_status"] == "PARTIAL"
    assert db.rows[1]["meeting_date"] == "2026-07-29"
    assert db.rows[1]["target_lower_before_pct"] == 3.50
    assert db.rows[1]["target_upper_before_pct"] == 3.75
    assert db.rows[1]["coverage_status"] == "READY"
