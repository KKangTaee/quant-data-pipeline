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


def test_sep_participant_total_uses_current_release_not_prior_note() -> None:
    from finance.data.fomc_policy import parse_fomc_sep_distributions

    page = FIXTURE.read_text().replace(
        "<p>Eighteen participants submitted information",
        "<p>Nineteen participants submitted information in conjunction with the March 17–18, 2026, meeting.</p>\n"
        "<p>Eighteen participants submitted information",
    )

    rows = parse_fomc_sep_distributions(
        page,
        source_url=SOURCE_URL,
        released_at="2026-06-17T18:00:00+00:00",
        collected_at="2026-06-17T18:05:00+00:00",
    )
    assert sum(
        int(row["participant_count"])
        for row in rows
        if row["distribution_kind"] == "DOT" and row["target_period"] == "2026"
    ) == 18


def test_sep_summary_accepts_release_specific_year_headers() -> None:
    from finance.data.fomc_policy import parse_fomc_sep_distributions

    page = FIXTURE.read_text().replace(
        "<th>2026</th><th>2027</th><th>2028</th><th>Longer run</th>",
        "<th>2021</th><th>2022</th><th>2023</th><th>Longer run</th>",
        3,
    )
    rows = parse_fomc_sep_distributions(
        page,
        source_url=SOURCE_URL,
        released_at="2026-06-17T18:00:00+00:00",
        collected_at="2026-06-17T18:05:00+00:00",
    )

    assert any(
        row["distribution_kind"] == "SUMMARY"
        and row["target_period"] == "2021"
        for row in rows
    )


def test_historical_advance_release_heading_is_treated_as_table_one() -> None:
    from finance.data.fomc_policy import parse_fomc_sep_distributions

    page = FIXTURE.read_text().replace(
        "Table 1. Economic projections of Federal Reserve Board members and Federal Reserve Bank presidents, June 2026",
        "Advance release of table 1 of the Summary of Economic Projections to be released with the FOMC minutes",
    )

    rows = parse_fomc_sep_distributions(
        page,
        source_url=SOURCE_URL,
        released_at="2026-06-17T18:00:00+00:00",
        collected_at="2026-06-17T18:05:00+00:00",
    )

    assert any(
        row["distribution_kind"] == "SUMMARY"
        and row["variable_name"] == "core_pce"
        for row in rows
    )


def test_sep_histogram_accepts_new_horizon_with_one_current_column() -> None:
    from bs4 import BeautifulSoup
    from finance.data.fomc_policy import _parse_histogram

    table = BeautifulSoup(
        """
        <table><thead>
          <tr><th>Percent Range</th><th colspan="2">2025</th><th colspan="2">2026</th>
              <th colspan="2">2027</th><th>2028</th><th colspan="2">Longer Run</th></tr>
          <tr><th>June projections</th><th>September projections</th>
              <th>June projections</th><th>September projections</th>
              <th>June projections</th><th>September projections</th>
              <th>September projections</th>
              <th>June projections</th><th>September projections</th></tr>
        </thead><tbody>
          <tr><th>2.1-2.2</th><td>1</td><td>2</td><td>3</td><td>4</td>
              <td>5</td><td>6</td><td>7</td><td>8</td><td>9</td></tr>
        </tbody></table>
        """,
        "html.parser",
    ).find("table")
    rows = _parse_histogram(
        "Figure 3.A. Distribution of participants' projections for real GDP",
        table,
        release_month="September",
        source_url="https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20250917.htm",
        released_at="2025-09-17T18:00:00+00:00",
        collected_at="2025-09-17T18:05:00+00:00",
    )

    counts = {row["target_period"]: row["participant_count"] for row in rows}
    assert counts == {
        "2025": 2,
        "2026": 4,
        "2027": 6,
        "2028": 7,
        "longer_run": 9,
    }


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


def test_historical_sep_table_heading_can_precede_data_container() -> None:
    from bs4 import BeautifulSoup
    from finance.data.fomc_policy import _table_containers

    soup = BeautifulSoup(
        """
        <h5 class="tablehead">Figure 2. FOMC participants' assessments</h5>
        <div class="data-table"><table><tbody><tr><td>row</td></tr></tbody></table></div>
        """,
        "html.parser",
    )

    containers = _table_containers(soup)

    assert len(containers) == 1
    assert containers[0][0].startswith("Figure 2.")


def test_historical_statement_discovery_uses_only_exact_statement_links() -> None:
    from finance.data.fomc_policy import discover_fomc_statement_urls

    page = """
      <div class="panel">
        <h5>September 20-21 Meeting - 2016</h5>
        <p><a href="/newsevents/pressreleases/monetary20160921a.htm">Statement</a></p>
        <p><a href="/newsevents/pressreleases/monetary20160921b.htm">Implementation Note</a></p>
        <p><a href="/newsevents/pressreleases/monetary20160827a.htm">Statement on Longer-Run Goals</a></p>
      </div>
      <div class="panel">
        <h5>August 27 (notation vote) - 2016</h5>
        <p><a href="/newsevents/pressreleases/monetary20160827a.htm">Statement</a></p>
      </div>
    """

    assert discover_fomc_statement_urls(page) == [
        "https://www.federalreserve.gov/newsevents/pressreleases/monetary20160921a.htm"
    ]


def test_historical_collector_skips_explicit_nonmeeting_statement_but_fails_on_unknown_rate_syntax(
    monkeypatch,
) -> None:
    module = importlib.import_module("finance.data.fomc_policy")
    calendar_url = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
    historical_url = "https://www.federalreserve.gov/monetarypolicy/fomchistorical2020.htm"
    nonrate_url = (
        "https://www.federalreserve.gov/newsevents/pressreleases/"
        "monetary20200323a.htm"
    )
    unsupported_rate_url = (
        "https://www.federalreserve.gov/newsevents/pressreleases/"
        "monetary20200429a.htm"
    )
    current_url = (
        "https://www.federalreserve.gov/newsevents/pressreleases/"
        "monetary20210127a.htm"
    )
    pages = {
        calendar_url: f'<a href="{current_url}">Statement</a>',
        historical_url: f"""
          <div class="panel">
            <h5>March 23 (notation vote) - 2020</h5>
            <p><a href="{nonrate_url}">Statement</a></p>
          </div>
          <div class="panel">
            <h5>April 28-29 Meeting - 2020</h5>
            <p><a href="{unsupported_rate_url}">Statement</a></p>
          </div>
        """,
        unsupported_rate_url: """
          <p>For release at 2:00 p.m. EDT</p>
          <p>The Committee used an unsupported policy-rate wording.</p>
          <p>Voting for the monetary policy action were A. One and B. Two.</p>
        """,
    }
    fetched: list[str] = []

    def fetch_html(url: str) -> str:
        fetched.append(url)
        return pages[url]

    monkeypatch.setattr(module, "sync_table_schema", lambda *_args, **_kwargs: None)

    class DB:
        def use_db(self, _database: str) -> None:
            pass

        def execute(self, _sql: str) -> None:
            pass

        def executemany(self, _sql: str, _values: list[dict[str, object]]) -> None:
            pass

    with pytest.raises(ValueError, match="target range was not found"):
        module.collect_and_store_fomc_policy_history(
            calendar_url=calendar_url,
            connection=DB(),
            fetch_html=fetch_html,
            collected_at="2026-08-03T03:15:00+00:00",
            historical_start_year=2020,
        )

    assert nonrate_url not in fetched
    assert unsupported_rate_url in fetched


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
        historical_start_year=None,
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


def test_old_vote_format_and_nonbreaking_hyphen_are_supported() -> None:
    from finance.data.fomc_policy import parse_fomc_policy_decision

    html = """
      <p>In support of its goals, the Committee decided to maintain the target range
      for the federal funds rate at 3‑1/2 to 3‑3/4 percent.</p>
      <p>Voting for the monetary policy action were A. One; B. Two; and C. Three.
      Voting against this action were D. Four and E. Five, who preferred to lower
      the target range for the federal funds rate by 1/4 percentage point at this meeting.</p>
    """
    row = parse_fomc_policy_decision(
        html,
        source_url="https://www.federalreserve.gov/newsevents/pressreleases/monetary20260128a.htm",
        released_at="2026-01-28T19:00:00+00:00",
        prior_range=None,
        collected_at="2026-01-28T19:05:00+00:00",
    )

    assert row["vote_for_count"] == 3
    assert row["vote_against_count"] == 2
    assert {item["preferred_action"] for item in json.loads(row["dissents_json"])} == {
        "CUT_25"
    }


def test_historical_fomc_vote_and_target_range_dissents_are_supported() -> None:
    from finance.data.fomc_policy import parse_fomc_policy_decision

    html = """
      <p>The Committee decided to maintain the target range for the federal funds rate
      at 1/4 to 1/2 percent.</p>
      <p>Voting for the FOMC monetary policy action were: Janet L. Yellen, Chair;
      William C. Dudley, Vice Chairman; and Lael Brainard. Voting against the action
      were: Esther L. George, Loretta J. Mester, and Eric Rosengren, each of whom
      preferred at this meeting to raise the target range for the federal funds rate
      to 1/2 to 3/4 percent.</p>
    """

    row = parse_fomc_policy_decision(
        html,
        source_url=(
            "https://www.federalreserve.gov/newsevents/pressreleases/"
            "monetary20160921a.htm"
        ),
        released_at="2016-09-21T18:00:00+00:00",
        prior_range=(0.25, 0.50),
        collected_at="2026-08-03T03:15:00+00:00",
    )

    assert row["vote_for_count"] == 3
    assert row["vote_against_count"] == 3
    assert {item["preferred_action"] for item in json.loads(row["dissents_json"])} == {
        "HIKE_25"
    }


def test_historical_sep_release_clock_falls_back_to_official_release_page(
    monkeypatch,
) -> None:
    module = importlib.import_module("finance.data.fomc_policy")
    calendar_url = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
    historical_url = "https://www.federalreserve.gov/monetarypolicy/fomchistorical2016.htm"
    projection_url = (
        "https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20160615.htm"
    )
    release_url = (
        "https://www.federalreserve.gov/newsevents/pressreleases/"
        "monetary20160615b.htm"
    )
    current_calendar = '<a href="/newsevents/pressreleases/monetary20170201a.htm">Statement</a>'
    historical_page = """
      <h5>June 14-15 Meeting - 2016</h5>
      <a href="/newsevents/pressreleases/monetary20160615a.htm">Statement</a>
      <a href="/monetarypolicy/files/FOMC20160615SEPcompilation.pdf">
        SEP: Individual Projections
      </a>
    """
    projection_page = FIXTURE.read_text().replace(
        "<p>For release at 2:00 p.m., EDT, June 17, 2026</p>",
        "",
    )
    release_page = '<p>For release at 2:00 p.m. EDT</p>'
    pages = {
        calendar_url: current_calendar,
        historical_url: historical_page,
        projection_url: projection_page,
        release_url: release_page,
    }
    fetched: list[str] = []

    def fetch_html(url: str) -> str:
        fetched.append(url)
        return pages[url]

    monkeypatch.setattr(module, "sync_table_schema", lambda *_args, **_kwargs: None)

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
    result = module.collect_and_store_fomc_sep_distributions(
        calendar_url=calendar_url,
        connection=db,
        fetch_html=fetch_html,
        collected_at="2026-08-03T03:15:00+00:00",
        historical_start_year=2016,
    )

    assert result["releases"] == 1
    assert {row["released_at"] for row in db.rows} == {
        "2016-06-15 18:00:00.000000"
    }
    assert fetched == [
        calendar_url,
        historical_url,
        projection_url,
        release_url,
    ]


def test_mixed_dissent_groups_preserve_distinct_explicit_preferences() -> None:
    from finance.data.fomc_policy import parse_fomc_policy_decision

    html = """
      <p>The Committee decided to maintain the target range for the federal funds rate
      at 3‑1/2 to 3‑3/4 percent.</p>
      <p>Voting for the monetary policy action were A. One; and B. Two.
      Voting against this action were C. Three, who preferred to lower the target range
      by 1/4 percentage point at this meeting; and D. Four and E. Five, who supported
      maintaining the target range but did not support inclusion of an easing bias.</p>
    """
    row = parse_fomc_policy_decision(
        html,
        source_url="https://www.federalreserve.gov/newsevents/pressreleases/monetary20260429a.htm",
        released_at="2026-04-29T18:00:00+00:00",
        prior_range=(3.5, 3.75),
        collected_at="2026-04-29T18:05:00+00:00",
    )

    actions = [item["preferred_action"] for item in json.loads(row["dissents_json"])]
    assert actions == ["CUT_25", "HOLD_NO_EASING_BIAS", "HOLD_NO_EASING_BIAS"]


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
        historical_start_year=None,
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


def test_calendar_statement_discovery_excludes_non_rate_notation_vote() -> None:
    from finance.data.fomc_policy import discover_fomc_statement_urls

    html = """
      <div class="row fomc-meeting">
        <div>July</div><div>28-29</div>
        <div><strong>Statement:</strong><br>
          <a href="/monetarypolicy/files/monetary20250729a1.pdf">PDF</a> |
          <a href="/newsevents/pressreleases/monetary20250729a.htm">HTML</a>
        </div>
      </div>
      <div class="row fomc-meeting fomc-meeting--shaded">
        <div>August</div><div>22 (notation vote)</div>
        <div><a href="/newsevents/pressreleases/monetary20250822a.htm">
          Statement on Longer-Run Goals and Monetary Policy Strategy
        </a></div>
      </div>
    """

    assert discover_fomc_statement_urls(html) == [
        "https://www.federalreserve.gov/newsevents/pressreleases/monetary20250729a.htm"
    ]


@pytest.mark.parametrize(
    ("decision_text", "expected_range"),
    (
        (
            "raise the target range for the federal funds rate to 1/4 to 1/2 percent",
            (0.25, 0.50),
        ),
        (
            "lower the target range for the federal funds rate by 1/2 percentage point, "
            "to 4-3/4 to 5 percent",
            (4.75, 5.00),
        ),
    ),
)
def test_rate_change_statement_parses_final_target_range(
    decision_text: str,
    expected_range: tuple[float, float],
) -> None:
    from finance.data.fomc_policy import parse_fomc_policy_decision

    html = f"""
      <p>The Committee decided to {decision_text}.</p>
      <p>Voting for the monetary policy action were A. One; B. Two; and C. Three.</p>
    """
    row = parse_fomc_policy_decision(
        html,
        source_url=(
            "https://www.federalreserve.gov/newsevents/pressreleases/"
            "monetary20220316a.htm"
        ),
        released_at="2022-03-16T18:00:00+00:00",
        prior_range=(0.0, 0.25),
        collected_at="2026-08-03T13:30:00+00:00",
    )

    assert (
        row["target_lower_after_pct"],
        row["target_upper_after_pct"],
    ) == expected_range
