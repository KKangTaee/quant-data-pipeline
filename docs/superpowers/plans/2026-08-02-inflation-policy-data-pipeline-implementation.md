# Inflation Policy Data Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Persist official SEP, FOMC, inflation, labor, Treasury, and term-premium data with exact point-in-time cutoffs and expose one DB-only loader bundle for the forecasting engines.

**Architecture:** Extract the generic FRED vintage adapter from the economic-cycle-specific orchestrator, add an inflation-policy schema family, and build focused official-source collectors. Loaders select only records whose `released_at <= as_of_at`; existing valuation SEP storage remains unchanged for compatibility.

**Tech Stack:** Python 3.12, pandas, MySQL, Federal Reserve accessible HTML, FRED/ALFRED API, BEA NIPA API, New York Fed ACM workbook, pytest-style tests.

## Global Constraints

- Do not read or write `economic_cycle_snapshot` or `economic_cycle_model_artifact` in this plan.
- Preserve the existing `fomc_sep_projection` schema and its S&P 500 valuation consumers.
- Add exact or conservative `released_at`; unknown intraday times resolve to 23:59:59 America/New_York, never midnight.
- SEP parser stores current-release distribution counts only and never creates `participant_id`.
- A partial collector failure writes no forecast snapshot; previously stored raw rows remain recoverable.
- New UI diagnostics are outside this plan.

---

## File Structure

### Create

- `finance/data/fred_vintages.py`: source-neutral FRED/ALFRED vintage fetch, normalize, release-time resolution, and UPSERT primitives.
- `finance/inflation_policy_catalog.py`: immutable inflation, policy, labor, growth, and rates series metadata.
- `finance/data/fomc_policy.py`: SEP distribution and policy-decision discovery, parsing, and persistence.
- `finance/data/bea_pce_components.py`: BEA monthly PCE component/breadth ingestion.
- `finance/data/nyfed_term_premium.py`: official ACM workbook discovery and normalization.
- `finance/data/inflation_policy_results.py`: model, snapshot, resistance definition, and resistance snapshot persistence.
- `finance/loaders/inflation_policy.py`: strict as-of raw and result readers.
- `app/jobs/inflation_policy_refresh.py`: bounded backend refresh orchestration.
- `tests/fixtures/fomc_sep_20260617_excerpt.html`
- `tests/fixtures/fomc_statement_20260729_excerpt.html`
- `tests/fixtures/acm_term_premium_excerpt.csv`
- `tests/test_inflation_policy_schema.py`
- `tests/test_fred_vintages.py`
- `tests/test_inflation_policy_catalog.py`
- `tests/test_fomc_policy_data.py`
- `tests/test_bea_pce_components.py`
- `tests/test_nyfed_term_premium.py`
- `tests/test_inflation_policy_loaders.py`
- `tests/test_inflation_policy_refresh.py`

### Modify

- `finance/data/db/schema.py:979-1068`: add `released_at` to macro vintages and add `INFLATION_POLICY_SCHEMAS` after `ECONOMIC_CYCLE_SCHEMAS`.
- `finance/data/economic_cycle_vintages.py:1-710`: import/re-export generic FRED functions while retaining only cycle catalog orchestration.
- `tests/test_economic_cycle_vintages.py`: retain compatibility coverage after extraction.
- `app/jobs/ingestion_jobs.py:45-65,470-560`: register the backend refresh action and table evidence.
- `app/jobs/overview_automation.py:220-290`: register standard/safe/broad scheduled refresh; exclude `browser_safe`.
- `.aiworkspace/note/finance/phases/active/inflation-policy-yield-path/`: create phase tracking with `State: active`.
- `.aiworkspace/note/finance/tasks/active/inflation-policy-data-pipeline/`: create task tracking with `State: active`.

## Stable Interfaces

```python
@dataclass(frozen=True)
class InflationPolicySeriesSpec:
    series_id: str
    group: str
    frequency: str
    transform: str
    required_for: tuple[str, ...]
    release_policy: str

@dataclass(frozen=True)
class InflationPolicyDataBundle:
    as_of_at: str
    macro_rows: tuple[dict[str, object], ...]
    sep_rows: tuple[dict[str, object], ...]
    decision_rows: tuple[dict[str, object], ...]
    term_premium_rows: tuple[dict[str, object], ...]
    coverage: dict[str, object]

def load_inflation_policy_data_bundle(
    *, as_of_at: str | datetime, history_start: str | date
) -> InflationPolicyDataBundle: ...
```

### Task 1: Add the inflation-policy schema family

**Files:**
- Modify: `finance/data/db/schema.py:979-1068`
- Create: `tests/test_inflation_policy_schema.py`
- Create: `.aiworkspace/note/finance/phases/active/inflation-policy-yield-path/{PLAN,DESIGN,TASKS,STATUS,RISKS,INTEGRATION}.md`
- Create: `.aiworkspace/note/finance/tasks/active/inflation-policy-data-pipeline/{PLAN,DESIGN,STATUS,NOTES,RUNS,RISKS}.md`

**Interfaces:**
- Consumes: `sync_table_schema(db, table_name, create_table_sql, db_name)`.
- Produces: `INFLATION_POLICY_SCHEMAS` with six tables and nullable `macro_series_vintage_observation.released_at`.

- [ ] **Step 1: Write the failing schema contract test**

```python
def test_inflation_policy_schema_keeps_release_and_identity_boundaries() -> None:
    from finance.data.db.schema import INFLATION_POLICY_SCHEMAS, PROVIDER_SCHEMAS

    vintage = " ".join(PROVIDER_SCHEMAS["macro_series_vintage_observation"].split())
    assert "released_at DATETIME(6) NULL" in vintage
    assert set(INFLATION_POLICY_SCHEMAS) == {
        "fomc_sep_distribution",
        "fomc_policy_decision",
        "inflation_policy_model_artifact",
        "inflation_policy_snapshot",
        "yield_resistance_definition",
        "yield_resistance_snapshot",
    }
    sep = " ".join(INFLATION_POLICY_SCHEMAS["fomc_sep_distribution"].split())
    assert "participant_id" not in sep
    assert "released_at DATETIME(6) NOT NULL" in sep
    assert "participant_count SMALLINT NOT NULL" in sep
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_schema.py -q
```

Expected: FAIL because `INFLATION_POLICY_SCHEMAS` and `released_at` do not exist.

- [ ] **Step 3: Add the exact schema contracts**

Use these business keys and payloads:

| Table | Business key | Required payload |
| --- | --- | --- |
| `fomc_sep_distribution` | release time, target period, variable, kind, bin | meeting/release time, target period, variable, `SUMMARY|HISTOGRAM|DOT`, bin label/value/bounds, participant count, source, parser version |
| `fomc_policy_decision` | meeting date | before/after range, release time, vote counts, dissents JSON, statement hash/source, parser version |
| `inflation_policy_model_artifact` | model version, trained cutoff, component | feature/state versions, parameters, validation, publication status/reasons |
| `inflation_policy_snapshot` | as-of, model version, run kind | inflation/policy/rates/reverse/evidence/freshness/warnings JSON and publication status |
| `yield_resistance_definition` | definition id | `AUTO|USER`, instrument, lookbacks, zone, buffer, confirmation profile, algorithm version, active flag |
| `yield_resistance_snapshot` | definition id, as-of | current value, distance, state, strength, probabilities, driver, quality/evidence JSON |

Use `DATETIME(6)` for release/cutoff timestamps, `DECIMAL(10,4)` for rate/PCE values, and indexes beginning with `released_at` or `as_of_at` for PIT reads.

- [ ] **Step 4: Create phase/task records**

Write `State: active`, link the approved spec and this plan, list all six roadmap stages, and record the pre-existing dirty worktree as an integration risk. Do not copy the full spec into task notes.

- [ ] **Step 5: Run schema tests and diff check**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_schema.py tests/test_economic_cycle_vintages.py -q
git diff --check
```

Expected: PASS; existing cycle schema tests remain unchanged.

- [ ] **Step 6: Commit**

```bash
git add finance/data/db/schema.py tests/test_inflation_policy_schema.py \
  .aiworkspace/note/finance/phases/active/inflation-policy-yield-path \
  .aiworkspace/note/finance/tasks/active/inflation-policy-data-pipeline
git commit -m "인플레이션 정책 데이터 스키마 추가"
```

### Task 2: Extract the generic FRED vintage adapter

**Files:**
- Create: `finance/data/fred_vintages.py`
- Modify: `finance/data/economic_cycle_vintages.py:1-710`
- Create: `tests/test_fred_vintages.py`
- Modify: `tests/test_economic_cycle_vintages.py`

**Interfaces:**
- Consumes: FRED `series/vintagedates`, `series/observations`, `PROVIDER_SCHEMAS`.
- Produces:

```python
def fetch_fred_vintage_dates(series_id: str, *, api_key: str, session: object, realtime_start: str = "1776-07-04") -> list[str]: ...
def build_realtime_windows(vintage_dates: Sequence[str], *, lower_bound: str | None = None, chunk_size: int = 2000) -> list[tuple[str, str]]: ...
def fetch_fred_vintages(series_id: str, *, api_key: str, session: object, realtime_start: str = "1776-07-04", limit: int = 100000) -> list[dict[str, object]]: ...
def resolve_released_at(realtime_start: str, *, release_policy: str) -> str: ...
def upsert_fred_vintage_rows(rows: Sequence[Mapping[str, object]], *, db: MySQLClient) -> int: ...
```

- [ ] **Step 1: Add source-neutral failing tests**

Copy pagination, 2,000-vintage window splitting, and open-interval tests, then add:

```python
def test_unknown_intraday_release_uses_conservative_end_of_day() -> None:
    from finance.data.fred_vintages import resolve_released_at
    assert resolve_released_at(
        "2026-07-30", release_policy="END_OF_DAY_ET"
    ) == "2026-07-31T03:59:59.999999+00:00"
```

- [ ] **Step 2: Run both test modules to verify the new module fails**

```bash
.venv/bin/python -m pytest tests/test_fred_vintages.py tests/test_economic_cycle_vintages.py -q
```

Expected: new tests fail on missing module; existing tests pass.

- [ ] **Step 3: Move only generic functions and preserve imports**

Move HTTP paging, realtime-window construction, row normalization, incremental-boundary lookup, and UPSERT primitives into `fred_vintages.py`. In `economic_cycle_vintages.py`, import the same public names so existing callers keep their signatures. Keep cycle catalog and cycle-specific coverage orchestration in the old module.

- [ ] **Step 4: Implement exact release policies**

```python
RELEASE_POLICIES = {
    "OFFICIAL_0830_ET": time(8, 30),
    "OFFICIAL_1000_ET": time(10, 0),
    "END_OF_DAY_ET": time(23, 59, 59, 999999),
}
```

Convert `America/New_York` to UTC with `zoneinfo.ZoneInfo`; reject unknown policies rather than defaulting to midnight.

- [ ] **Step 5: Run compatibility tests**

```bash
.venv/bin/python -m pytest tests/test_fred_vintages.py tests/test_economic_cycle_vintages.py tests/test_economic_cycle_refresh.py -q
```

Expected: PASS; old function imports and collection behavior remain compatible.

- [ ] **Step 6: Commit**

```bash
git add finance/data/fred_vintages.py finance/data/economic_cycle_vintages.py \
  tests/test_fred_vintages.py tests/test_economic_cycle_vintages.py
git commit -m "FRED 빈티지 수집 경계 공통화"
```

### Task 3: Add the series catalog and PCE component collection

**Files:**
- Create: `finance/inflation_policy_catalog.py`
- Create: `tests/test_inflation_policy_catalog.py`
- Create: `finance/data/bea_pce_components.py`
- Create: `tests/test_bea_pce_components.py`

**Interfaces:**
- Consumes: generic FRED adapter and BEA NIPA `T20804` monthly table.
- Produces:

```python
def get_inflation_policy_catalog() -> tuple[InflationPolicySeriesSpec, ...]: ...
def collect_inflation_policy_vintages(
    *,
    catalog: Sequence[InflationPolicySeriesSpec] | None = None,
    api_key: str | None = None,
    db_factory: object = MySQLClient,
) -> dict[str, object]: ...
```

- [ ] **Step 1: Write the failing catalog contract**

```python
def test_catalog_has_independent_required_groups() -> None:
    from finance.inflation_policy_catalog import get_inflation_policy_catalog
    ids = {item.series_id for item in get_inflation_policy_catalog()}
    assert {"PCEPI", "PCEPILFE", "CPIAUCSL", "CPILFESL"} <= ids
    assert {"UNRATE", "PAYEMS", "ICSA", "INDPRO", "PCEC96"} <= ids
    assert {"FEDFUNDS", "DGS2", "DGS10", "DFII10", "T10YIE"} <= ids
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_catalog.py tests/test_bea_pce_components.py -q
```

Expected: FAIL on missing modules.

- [ ] **Step 3: Implement the immutable catalog**

```python
CORE_SERIES = (
    "PCEPI", "PCEPILFE", "CPIAUCSL", "CPILFESL",
    "PCETRIM12M159SFRBDAL", "CES0500000003", "ECIWAG", "ULCNFB",
    "PPIACO", "MICH", "UNRATE", "PAYEMS", "ICSA", "AWHMAN",
    "TEMPHELPS", "INDPRO", "W875RX1", "PCEC96", "CMRMTSPL",
    "FEDFUNDS", "DGS2", "DGS10", "DFII10", "T10YIE", "T10Y2Y",
    "BAMLH0A0HYM2",
)
```

Assign verified BEA/BLS release clocks `OFFICIAL_0830_ET`; daily market series and series without a verified clock use `END_OF_DAY_ET`. Do not import `finance.economic_cycle_catalog`.

- [ ] **Step 4: Implement BEA component normalization**

```python
def normalize_bea_pce_components(payload: Mapping[str, object], *, released_at: str, collected_at: str) -> list[dict[str, object]]: ...
def calculate_component_breadth(rows: Sequence[Mapping[str, object]], *, threshold_pct: float = 0.3) -> dict[str, float]: ...
```

Accept monthly NIPA `T20804` rows, retain goods/services/core/addenda identities, and keep release vintages separate. Require at least goods, services, headline, and core lines before returning `READY` breadth.

Persist normalized component rows in `macro_series_vintage_observation` with stable `BEA_PCE_<line_number>` series IDs, `source="bea_nipa_t20804"`, and the actual collection release time. Do not backfill today's revised component table as though it were known at historical origins; origins before the first stored release receive missing breadth.

- [ ] **Step 5: Implement catalog collection**

Iterate catalog specs through `fetch_fred_vintages`, attach metadata/resolved release time, and UPSERT by the macro-vintage business key. Return per-series coverage; do not write a forecast snapshot.

- [ ] **Step 6: Run focused tests and commit**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_catalog.py tests/test_fred_vintages.py tests/test_bea_pce_components.py -q
git add finance/inflation_policy_catalog.py finance/data/bea_pce_components.py \
  tests/test_inflation_policy_catalog.py tests/test_bea_pce_components.py
git commit -m "인플레이션 정책 원자료 카탈로그 추가"
```

### Task 4: Parse and persist anonymous SEP distributions

**Files:**
- Create: `finance/data/fomc_policy.py`
- Create: `tests/fixtures/fomc_sep_20260617_excerpt.html`
- Create: `tests/test_fomc_policy_data.py`

**Interfaces:**
- Consumes: Federal Reserve accessible projection HTML.
- Produces:

```python
def discover_fomc_projection_urls(calendar_html: str) -> list[str]: ...
def parse_fomc_sep_distributions(html: str, *, source_url: str, released_at: str, collected_at: str) -> list[dict[str, object]]: ...
def collect_and_store_fomc_sep_distributions(*, calendar_url: str, db_factory: object = MySQLClient) -> dict[str, object]: ...
```

- [ ] **Step 1: Save the minimal official fixture and write the failing parser test**

The fixture includes Table 1, Figure 2 exact rate dots, Figure 3.D Core PCE, and Figure 3.E rate histograms.

```python
def test_june_2026_sep_counts_stay_anonymous() -> None:
    rows = parse_fomc_sep_distributions(
        FIXTURE.read_text(),
        source_url="https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20260617.htm",
        released_at="2026-06-17T18:00:00+00:00",
        collected_at="2026-06-17T18:05:00+00:00",
    )
    rate = {(r["bin_value_pct"], r["participant_count"]) for r in rows if r["variable_name"] == "federal_funds_rate" and r["distribution_kind"] == "DOT" and r["target_period"] == "2026"}
    assert {(4.125, 5), (4.375, 1), (3.625, 8)} <= rate
    core = [r for r in rows if r["variable_name"] == "core_pce" and r["bin_label"] == "3.5-3.6" and r["target_period"] == "2026"]
    assert core[0]["participant_count"] == 4
    assert all("participant_id" not in row for row in rows)
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
.venv/bin/python -m pytest tests/test_fomc_policy_data.py::test_june_2026_sep_counts_stay_anonymous -q
```

Expected: FAIL on missing parser.

- [ ] **Step 3: Implement heading-scoped table parsing**

Select tables by normalized heading/caption, not fixed index. Select the current release-month column (`June projections` on the June page); prior projections come from their own dated page. Normalize blank cells only inside a recognized distribution and validate participant totals against the page note.

- [ ] **Step 4: Add idempotent persistence**

UPSERT the exact release/target/variable/kind/bin key. Reject a release if an identified distribution has inconsistent totals; never add a participant-level identifier.

- [ ] **Step 5: Run parser, schema, and existing valuation SEP tests**

```bash
.venv/bin/python -m pytest tests/test_fomc_policy_data.py tests/test_inflation_policy_schema.py tests/test_sp500_valuation.py -q
```

Expected: PASS; existing `fomc_sep_projection` consumers remain intact.

- [ ] **Step 6: Commit**

```bash
git add finance/data/fomc_policy.py tests/fixtures/fomc_sep_20260617_excerpt.html tests/test_fomc_policy_data.py
git commit -m "FOMC 점도표와 물가 분포 수집 추가"
```

### Task 5: Parse and persist FOMC policy decisions

**Files:**
- Modify: `finance/data/fomc_policy.py`
- Create: `tests/fixtures/fomc_statement_20260729_excerpt.html`
- Modify: `tests/test_fomc_policy_data.py`

**Interfaces:**
- Produces:

```python
def discover_fomc_statement_urls(calendar_html: str) -> list[str]: ...
def parse_fomc_policy_decision(html: str, *, source_url: str, released_at: str, prior_range: tuple[float, float] | None, collected_at: str) -> dict[str, object]: ...
def collect_and_store_fomc_policy_history(*, calendar_url: str, db_factory: object = MySQLClient) -> dict[str, object]: ...
```

- [ ] **Step 1: Write the failing July decision test**

```python
def test_july_2026_hold_and_three_hike_dissents_are_preserved() -> None:
    row = parse_fomc_policy_decision(
        STATEMENT_FIXTURE.read_text(),
        source_url="https://www.federalreserve.gov/newsevents/pressreleases/monetary20260729a.htm",
        released_at="2026-07-29T18:00:00+00:00",
        prior_range=(3.50, 3.75),
        collected_at="2026-07-29T18:02:00+00:00",
    )
    assert (row["target_lower_after_pct"], row["target_upper_after_pct"]) == (3.50, 3.75)
    assert row["vote_for_count"] == 9
    assert row["vote_against_count"] == 3
    assert {d["preferred_action"] for d in json.loads(row["dissents_json"])} == {"HIKE_25"}
```

- [ ] **Step 2: Run the focused test to verify it fails**

```bash
.venv/bin/python -m pytest tests/test_fomc_policy_data.py::test_july_2026_hold_and_three_hike_dissents_are_preserved -q
```

Expected: FAIL on missing decision parser.

- [ ] **Step 3: Implement text, vote, and chronology parsing**

Parse the target range from the policy paragraph and vote/dissent preference from the voting paragraph. Preserve statement hash/source, not an inferred sentiment score. Collect oldest to newest so the prior range is known; if missing, store null prior bounds with `PARTIAL` coverage rather than reading a future decision.

- [ ] **Step 4: Run all FOMC tests and commit**

```bash
.venv/bin/python -m pytest tests/test_fomc_policy_data.py -q
git add finance/data/fomc_policy.py tests/fixtures/fomc_statement_20260729_excerpt.html tests/test_fomc_policy_data.py
git commit -m "FOMC 결정과 반대표 이력 수집 추가"
```

### Task 6: Collect New York Fed ACM term premium

**Files:**
- Create: `finance/data/nyfed_term_premium.py`
- Create: `tests/fixtures/acm_term_premium_excerpt.csv`
- Create: `tests/test_nyfed_term_premium.py`

**Interfaces:**
- Produces:

```python
def discover_acm_download_url(page_html: str) -> str: ...
def normalize_acm_term_premium(frame: pd.DataFrame, *, collected_at: str, source_ref: str) -> list[dict[str, object]]: ...
def collect_and_store_acm_term_premium(*, page_url: str, db_factory: object = MySQLClient) -> dict[str, object]: ...
```

- [ ] **Step 1: Write failing discovery and normalization tests**

Test relative-to-absolute official URLs, `DATE` plus the 10-year ACM column normalized to `ACMTP10`, and missing values skipped without forward filling.

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_nyfed_term_premium.py -q
```

Expected: FAIL on missing module.

- [ ] **Step 3: Implement discovery, normalization, and persistence**

Store in `macro_series_vintage_observation` with `source="new_york_fed_acm"`, `factor_group="rates"`, `released_at=collected_at`, and collection date as realtime start. Do not fabricate historical release vintages for workbook rows.

Because the current workbook is not a historical publication archive, ACM rows collected today are ineligible for earlier replay origins. Until accumulated stored vintages satisfy validation coverage, term-premium history remains `LIMITED` and the driver lens reports that limitation.

- [ ] **Step 4: Run tests and commit**

```bash
.venv/bin/python -m pytest tests/test_nyfed_term_premium.py tests/test_inflation_policy_schema.py -q
git add finance/data/nyfed_term_premium.py tests/fixtures/acm_term_premium_excerpt.csv tests/test_nyfed_term_premium.py
git commit -m "뉴욕 연은 기간 프리미엄 수집 추가"
```

### Task 7: Add result persistence and strict as-of loaders

**Files:**
- Create: `finance/data/inflation_policy_results.py`
- Create: `finance/loaders/inflation_policy.py`
- Create: `tests/test_inflation_policy_loaders.py`

**Interfaces:**
- Produces:

```python
def save_inflation_policy_model_artifact(row: Mapping[str, object], *, db_factory: object = MySQLClient) -> None: ...
def save_inflation_policy_snapshot(row: Mapping[str, object], *, db_factory: object = MySQLClient) -> None: ...
def save_yield_resistance_definition(row: Mapping[str, object], *, db_factory: object = MySQLClient) -> str: ...
def save_yield_resistance_snapshot(row: Mapping[str, object], *, db_factory: object = MySQLClient) -> None: ...
def load_inflation_policy_data_bundle(*, as_of_at: str | datetime, history_start: str | date, query_fn: QueryFn | None = None) -> InflationPolicyDataBundle: ...
def load_latest_inflation_policy_snapshot(*, as_of_at: str | datetime | None = None, query_fn: QueryFn | None = None) -> dict[str, object] | None: ...
```

- [ ] **Step 1: Write the failing PIT tests**

```python
def test_fomc_cutoff_excludes_next_day_pce() -> None:
    bundle = load_inflation_policy_data_bundle(
        as_of_at="2026-07-29T18:00:00+00:00",
        history_start="2025-01-01",
        query_fn=query_with_release_rows(),
    )
    assert all(str(row["released_at"]) <= "2026-07-29 18:00:00" for row in bundle.macro_rows)
```

Also test latest eligible vintage selection, optional null ACM, finite JSON validation, and absence of economic-cycle table names in loader SQL.

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_loaders.py -q
```

Expected: FAIL on missing loader/store.

- [ ] **Step 3: Implement strict loaders**

Every raw SQL path includes `released_at <= %s`. Rank by `released_at DESC, realtime_start DESC, collected_at DESC`. Null release time is ineligible for the new model; do not fall back to `realtime_start`.

- [ ] **Step 4: Implement idempotent result stores**

Validate JSON and finite numbers before opening a transaction. UPSERT only the exact artifact/snapshot business key; invalid payloads perform no write.

- [ ] **Step 5: Run tests and commit**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_loaders.py tests/test_inflation_policy_schema.py -q
git add finance/data/inflation_policy_results.py finance/loaders/inflation_policy.py tests/test_inflation_policy_loaders.py
git commit -m "인플레이션 정책 PIT 로더와 저장소 추가"
```

### Task 8: Add backend refresh orchestration and automation

**Files:**
- Create: `app/jobs/inflation_policy_refresh.py`
- Modify: `app/jobs/ingestion_jobs.py:45-65,470-560`
- Modify: `app/jobs/overview_automation.py:220-290`
- Create: `tests/test_inflation_policy_refresh.py`

**Interfaces:**
- Produces:

```python
def run_inflation_policy_raw_refresh(
    *,
    as_of_at: str | None = None,
    collectors: Mapping[str, Callable[[], Mapping[str, object]]] | None = None,
) -> dict[str, object]: ...
def main(argv: Sequence[str] | None = None) -> int: ...
```

- [ ] **Step 1: Write the failing orchestration test**

```python
def test_partial_required_source_failure_blocks_materialization() -> None:
    result = run_inflation_policy_raw_refresh(
        collectors={
            "macro_vintages": lambda: {"status": "success", "rows": 100},
            "sep": lambda: {"status": "failed", "rows": 0},
            "decisions": lambda: {"status": "success", "rows": 20},
            "term_premium": lambda: {"status": "success", "rows": 500},
        },
    )
    assert result["status"] == "failed"
    assert result["failed_sources"] == ["sep"]
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_refresh.py -q
```

Expected: FAIL on missing runner.

- [ ] **Step 3: Implement backend-only orchestration**

Run schema ensure, macro/BEA, SEP, decisions, and ACM in named steps. SEP, decisions, Core PCE, DGS2, DGS10, DFII10, and T10YIE are required; ACM and BEA detail degrade explicitly. Return compact run-history evidence without adding a product diagnostics panel.

- [ ] **Step 4: Register ingestion and scheduler**

Register one Data Operations action and a weekday 24-hour automation for `safe`, `standard`, `broad`; exclude `browser_safe`. Require `FRED_API_KEY`; missing `BEA_API_KEY` marks breadth `NOT_AVAILABLE`.

Add an `argparse` entry point accepting `--as-of-at`, print one compact JSON result, and return exit code 0 only for `success|partial_success`.

- [ ] **Step 5: Run job tests and commit**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_refresh.py tests/test_ingestion_module_split_contracts.py tests/test_overview_futures_macro_refresh.py -q
git add app/jobs/inflation_policy_refresh.py app/jobs/ingestion_jobs.py app/jobs/overview_automation.py tests/test_inflation_policy_refresh.py
git commit -m "인플레이션 정책 원자료 갱신 작업 추가"
```

### Task 9: Run real-source smoke and close the data task

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/inflation-policy-data-pipeline/{STATUS,NOTES,RUNS,RISKS}.md`
- Modify: `.aiworkspace/note/finance/phases/active/inflation-policy-yield-path/{TASKS,STATUS,RISKS}.md`
- Modify: `.aiworkspace/note/finance/docs/data/DB_SCHEMA_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md`
- Create: `.aiworkspace/note/finance/docs/runbooks/INFLATION_POLICY_DATA_REFRESH.md`

**Interfaces:**
- Consumes: complete Tasks 1–8.
- Produces: verified actual 2026 rows and a durable handoff to the core-engine plan.

- [ ] **Step 1: Run the focused suite**

```bash
.venv/bin/python -m pytest \
  tests/test_inflation_policy_schema.py \
  tests/test_fred_vintages.py \
  tests/test_inflation_policy_catalog.py \
  tests/test_fomc_policy_data.py \
  tests/test_bea_pce_components.py \
  tests/test_nyfed_term_premium.py \
  tests/test_inflation_policy_loaders.py \
  tests/test_inflation_policy_refresh.py -q
```

Expected: all tests pass.

- [ ] **Step 2: Run one actual collection smoke**

```bash
.venv/bin/python -m app.jobs.inflation_policy_refresh --as-of-at 2026-08-02T12:00:00+09:00
```

Expected: compact JSON reports source status/counts; raw responses stay in DB/artifact storage, not task docs.

- [ ] **Step 3: Query exact 2026 evidence**

Verify June rate dots `(3.375:1, 3.625:8, 3.875:3, 4.125:5, 4.375:1)`, Core PCE `3.5-3.6:4`, July hold vote `9-3`, and a July 29 18:00 UTC bundle excluding the July 30 PCE release.

- [ ] **Step 4: Use `finance-doc-sync` and update states**

Set the data task to `State: complete` only if tests and actual smoke succeed. Keep the phase `State: active` and point `TASKS.md` to the core-engine plan.

- [ ] **Step 5: Commit documentation**

```bash
git add .aiworkspace/note/finance/tasks/active/inflation-policy-data-pipeline \
  .aiworkspace/note/finance/phases/active/inflation-policy-yield-path \
  .aiworkspace/note/finance/docs/data/DB_SCHEMA_MAP.md \
  .aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md \
  .aiworkspace/note/finance/docs/runbooks/INFLATION_POLICY_DATA_REFRESH.md
git commit -m "인플레이션 정책 데이터 기반 검증 기록"
```
