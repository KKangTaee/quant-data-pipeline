# Institutional Holdings Hybrid Quarter Review V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended when explicitly authorized) or superpowers:executing-plans to implement this plan
> task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Institutional Holdings가 로컬 13F 제출 일정으로 갱신 필요성을 판단하고,
사용자 클릭 시 EDGAR 개별 filing과 SEC bulk dataset을 hybrid로 반영한 뒤 이전 분기의
두 성과 proxy와 `NEW / ADD / KEEP / REDUCE / DROP`을 보여주게 한다.

**Architecture:** 탭 render는 DB와 순수 calendar helper만 읽는다. Explicit refresh
command가 bulk dataset을 먼저 발견하고 아직 없으면 curated watchlist의 EDGAR filing을
manager별 transaction으로 적재한다. Loader는 amendment-aware effective quarter를 만들고,
focused service가 가격 coverage와 두 performance window를 계산해 Python-owned v3 payload로
React Studio의 freshness action과 `분기 리뷰` destination에 전달한다.

**Tech Stack:** Python 3, pandas, standard-library `urllib` / `html.parser` /
`xml.etree.ElementTree`, PyMySQL, MySQL, Streamlit, React 18, TypeScript, Vitest, Vite.

## Global Constraints

- 탭 진입과 normal render에서는 SEC/EDGAR 외부 요청을 만들지 않는다.
- 외부 discovery, download와 DB write는 `업데이트 확인 및 갱신` explicit click 이후에만
  실행한다.
- UI는 provider를 직접 호출하지 않고 `job -> finance/data -> DB -> loader/service -> UI`
  경계를 유지한다.
- Raw filing과 holding은 accession ledger로 보존하고 같은 accession 재실행은 idempotent다.
- Incomplete filing, unknown amendment와 empty information table은 latest portfolio를
  승격하지 않는다.
- Performance는 actual fund NAV가 아니라 reported-long-holdings proxy다.
- Missing price/identifier weight를 0% return으로 대체하지 않는다.
- Registry JSONL, saved portfolio, run history와 generated QA artifact는 stage하지 않는다.
- Browser/UI 변경 완료 주장 전 actual desktop/mobile QA와 screenshot 1장을 남긴다.

---

## 이걸 하는 이유?

현재 Institutional Holdings의 `is_stale`은 마지막 bulk 적재 성공 여부만 나타내고
공식적으로 다음 분기 제출일이 지났는지 판단하지 않는다. React의 갱신 폼도 이전
dataset URL을 기본값으로 보여주므로 사용자가 같은 대형 ZIP을 다시 적재할 수 있다.
새 filing은 EDGAR에 먼저 공개되고 bulk ZIP은 월말 이후에 나오므로, bulk-only 갱신은
대가 포트폴리오가 공개된 시점과 제품 반영 시점 사이에 불필요한 공백을 만든다.

이 계획은 최신성 판단을 저빈도 로컬 일정으로 단순화하고, 실제 update는 명시적 클릭에
한정한다. 새 분기가 들어온 뒤에는 이전 보고분의 다음 분기 price 결과와 공개 후 추종
가능 결과를 분리해 look-ahead 의미를 숨기지 않는다.

## 전체 Roadmap

| 차수 | 목적 | 완료 조건 |
|---|---|---|
| 1차 | local due decision | 외부 요청 없이 current/due/partial action을 결정 |
| 2차 | hybrid SEC ingestion | bulk-first, EDGAR fallback, per-manager idempotent write |
| 3차 | historical review | amendment-aware two-quarter bundle, changes, two proxies |
| 4차 | React product flow | conditional action과 `분기 리뷰`를 v3 workbench에 연결 |
| 5차 | actual QA/docs | SEC/DB/browser evidence와 durable docs closeout |

---

### Task 1: Local Form 13F Due Decision

**Files:**

- Create: `app/services/institutional_13f_refresh.py`
- Create: `tests/test_institutional_13f_refresh.py`
- Modify: `app/services/institutional_portfolios.py`

**Interfaces:**

- Produces: `form_13f_due_date(report_period: str | date) -> date`
- Produces: `latest_due_report_period(as_of_date: str | date) -> str | None`
- Produces: `build_institutional_refresh_action(*, as_of_date, manager_periods,
  expected_ciks, last_result=None) -> dict[str, Any]`
- Consumes later: Task 5 injects the returned action into the workbench payload.

- [x] **Step 1: Write failing calendar and action tests**

```python
from app.services.institutional_13f_refresh import (
    build_institutional_refresh_action,
    form_13f_due_date,
    latest_due_report_period,
)


def test_2026_deadlines_roll_weekend_and_federal_holiday() -> None:
    assert form_13f_due_date("2026-03-31").isoformat() == "2026-05-15"
    assert form_13f_due_date("2026-06-30").isoformat() == "2026-08-14"
    assert form_13f_due_date("2026-09-30").isoformat() == "2026-11-16"
    assert form_13f_due_date("2026-12-31").isoformat() == "2027-02-16"


def test_refresh_action_is_local_only_and_targets_latest_due_quarter() -> None:
    action = build_institutional_refresh_action(
        as_of_date="2026-08-17",
        manager_periods={"0001067983": "2026-03-31", "0001350694": "2026-06-30"},
        expected_ciks=["0001067983", "0001350694"],
    )
    assert action["target_report_period"] == "2026-06-30"
    assert action["visible"] is True
    assert action["completed_managers"] == 1
    assert action["expected_managers"] == 2
    assert action["action_id"] == "refresh_institutional_13f"
```

- [x] **Step 2: Run the focused tests and confirm RED**

Run: `.venv/bin/python -m pytest tests/test_institutional_13f_refresh.py -q`

Expected: import failure for `app.services.institutional_13f_refresh`.

- [x] **Step 3: Implement the pure calendar/action service**

Use `pandas.tseries.holiday.USFederalHolidayCalendar` and
`CustomBusinessDay(calendar=USFederalHolidayCalendar())`. Normalize every report period to a real
calendar quarter end, add 45 days, and roll forward only when the result is not a business day.

The action payload must use this exact shape:

```python
{
    "action_id": "refresh_institutional_13f",
    "visible": True,
    "status": "due" | "partial" | "current" | "not_ready",
    "target_report_period": "2026-06-30",
    "target_quarter_label": "2026년 2분기",
    "label": "2026년 2분기 업데이트 확인 및 갱신",
    "description": "버튼을 누르면 SEC 공개 자료를 확인한 뒤 가능한 기관을 갱신합니다.",
    "completed_managers": 1,
    "expected_managers": 2,
    "pending_ciks": ["0001067983"],
    "next_due_date": "2026-11-16",
}
```

Before the first due quarter, return `status="not_ready"`, `visible=False`, and no target. When
all expected managers are on or beyond the latest due period, return `status="current"` and
`visible=False`.

- [x] **Step 4: Add service composition coverage without network mocks**

Update `build_institutional_workbench_payload` to accept `refresh_action: dict | None` rather than
always constructing a hardcoded bulk URL action. Add a test that passes the pure action and asserts
the identical dict appears in the payload. The test must not patch `urllib`, proving payload build
does not perform discovery.

- [x] **Step 5: Run Task 1 tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_institutional_13f_refresh.py -q
.venv/bin/python -m pytest tests/test_institutional_portfolios.py -q
```

Expected: all tests pass; legacy payload assertions are updated from hardcoded URL fields to the
new conditional action contract.

- [x] **Step 6: Commit Task 1**

```bash
git add app/services/institutional_13f_refresh.py app/services/institutional_portfolios.py \
  tests/test_institutional_13f_refresh.py tests/test_institutional_portfolios.py
git commit -m "기능: 13F 로컬 제출일 갱신 판단 추가"
```

---

### Task 2: Official Bulk Dataset Discovery

**Files:**

- Modify: `finance/data/institutional_13f.py`
- Modify: `tests/test_institutional_13f_refresh.py`

**Interfaces:**

- Produces: `parse_sec_13f_dataset_candidates(html: str, *, base_url: str) -> list[dict]`
- Produces: `select_sec_13f_dataset_candidate(candidates, *, report_period: str) -> dict | None`
- Produces: `discover_sec_13f_dataset_candidate(report_period, *, user_agent=None,
  timeout=15.0) -> dict | None`
- Consumes: Task 5 hybrid job calls discovery only after the explicit event.

- [x] **Step 1: Add RED tests with an inline SEC listing fixture**

```python
def test_bulk_listing_selects_dataset_whose_window_contains_due_date() -> None:
    html = """
    <table>
      <tr><td><a href="/files/01mar2026-31may2026_form13f.zip">2026 March April May 13F</a></td></tr>
      <tr><td><a href="/files/01jun2026-31aug2026_form13f.zip">2026 June July August 13F</a></td></tr>
    </table>
    """
    candidates = parse_sec_13f_dataset_candidates(html, base_url="https://www.sec.gov/data")
    selected = select_sec_13f_dataset_candidate(candidates, report_period="2026-06-30")
    assert selected["dataset_url"] == "https://www.sec.gov/files/01jun2026-31aug2026_form13f.zip"
    assert selected["window_end"] == "2026-08-31"
```

Also assert malformed labels, non-ZIP anchors and the March-May dataset for a June report period
are rejected.

- [x] **Step 2: Run the candidate tests and confirm RED**

Run: `.venv/bin/python -m pytest tests/test_institutional_13f_refresh.py -q`

Expected: missing parser/select functions.

- [x] **Step 3: Implement standard-library HTML parsing**

Use a small `HTMLParser` subclass that captures anchor text and `href`. Parse the official
filename range `DDmonYYYY-DDmonYYYY_form13f.zip`; do not infer from display text alone. Resolve
relative URLs with `urllib.parse.urljoin`.

`select_sec_13f_dataset_candidate` computes the target filing due date through Task 1 and selects
the narrow candidate whose inclusive filename window contains that date. If no such published
candidate exists, return `None`.

- [x] **Step 4: Implement bounded network discovery**

`discover_sec_13f_dataset_candidate` downloads only `SEC_13F_DATASETS_PAGE` with the existing SEC
User-Agent resolver, `Accept-Encoding`, and a 15-second default timeout. Convert HTTP/URL errors
to `RuntimeError` messages containing the source page and status/reason, without swallowing 403 or
429 semantics.

- [x] **Step 5: Prove discovery is not called from page render**

Add a source-boundary test:

```python
page_source = Path("app/web/institutional_portfolios.py").read_text()
render_source = page_source[page_source.index("def render_institutional_portfolios_page("):]
assert "discover_sec_13f_dataset_candidate" not in render_source
```

- [x] **Step 6: Run Task 2 tests and commit**

```bash
.venv/bin/python -m pytest tests/test_institutional_13f_refresh.py -q
.venv/bin/python -m py_compile finance/data/institutional_13f.py
git add finance/data/institutional_13f.py tests/test_institutional_13f_refresh.py
git commit -m "기능: SEC 13F 통합 데이터셋 발견 추가"
```

---

### Task 3: Individual EDGAR Filing Parser And Transactional Persistence

**Files:**

- Create: `finance/data/institutional_13f_edgar.py`
- Modify: `finance/data/institutional_13f.py`
- Modify: `tests/test_institutional_13f_refresh.py`

**Interfaces:**

- Produces: `find_sec_13f_submission(payload, *, cik, report_period) -> list[dict]`
- Produces: `normalize_sec_13f_xml_documents(*, primary_xml, information_xml,
  accession_number, filing_date, source_ref, collected_at=None) -> dict[str, list[dict]]`
- Produces: `collect_and_store_sec_13f_watchlist(*, ciks, report_period, user_agent=None,
  request_timeout=30.0, request_sleep=0.11, ...) -> dict[str, Any]`
- Extracts from existing collector: `store_normalized_sec_13f_rows(db, normalized,
  *, source_ref) -> dict[str, int]`
- Consumes: Task 5 hybrid job.

- [x] **Step 1: Write submissions and XML parser tests**

Use namespace-bearing inline fixtures for one base `13F-HR`, one `13F-HR/A` restatement and one
`13F-NT`. Assert:

```python
filings = find_sec_13f_submission(payload, cik="0001067983", report_period="2026-06-30")
assert filings[0]["accession_number"] == "0001193125-26-352200"
assert filings[0]["submission_type"] == "13F-HR"

normalized = normalize_sec_13f_xml_documents(
    primary_xml=PRIMARY_XML,
    information_xml=INFORMATION_XML,
    accession_number="0001193125-26-352200",
    filing_date="2026-08-14",
    source_ref="https://www.sec.gov/Archives/edgar/data/.../",
    collected_at="2026-08-17 00:00:00",
)
assert normalized["filings"][0]["period_of_report"] == "2026-06-30"
assert normalized["holdings"][0]["cusip"] == "037833100"
assert normalized["holdings"][0]["infotable_sk"] == 1
```

The NT fixture must return filing metadata with no holdings. The watchlist collector labels that
manager `notice_only` from the submission type and must not fabricate an empty portfolio.

- [x] **Step 2: Run parser tests and confirm RED**

Run: `.venv/bin/python -m pytest tests/test_institutional_13f_refresh.py -q`

Expected: missing EDGAR module/functions.

- [x] **Step 3: Implement EDGAR discovery and document selection**

Fetch `https://data.sec.gov/submissions/CIK{cik10}.json`, filter recent rows by exact report date
and `13F-HR`, `13F-HR/A`, or `13F-NT`, then fetch the accession directory `index.json` to identify
the primary XML and information-table XML. Do not trust an XSL wrapper as raw XML. Resolve archive
URLs from normalized CIK and accession without dashes.

Use `ElementTree` local-name helpers so namespace prefixes do not matter. Preserve amendment
flags/type, report type, totals, voting authority and the existing normalized row keys. Assign
`infotable_sk` from 1-based document order, matching the SEC flattened-table row order contract.

- [x] **Step 4: Extract reusable persistence from the bulk collector**

Move the existing manager/filing/holding/mapping upserts behind:

```python
def store_normalized_sec_13f_rows(
    db: MySQLClient,
    normalized: dict[str, list[dict[str, Any]]],
    *,
    source_ref: str | None,
) -> dict[str, int]:
    ...
```

Keep `collect_and_store_sec_13f_dataset` behavior and output backward-compatible. Add a regression
test proving the bulk collector still reports managers/filings/holdings/mapping counts.

- [x] **Step 5: Implement one transaction per manager**

For every requested CIK:

1. discover exact target-period filings;
2. normalize the base and all published amendments in filing-date/accession order;
3. `db.begin()`;
4. store all normalized rows;
5. promote the manager only when a base holdings filing or unambiguous restatement has rows;
6. `db.commit()`; on any exception `db.rollback()` and mark only that manager failed.

Return:

```python
{
    "source": "sec_edgar_watchlist_13f",
    "report_period": "2026-06-30",
    "expected_managers": 12,
    "updated_managers": 8,
    "already_current_managers": 1,
    "notice_only_managers": 0,
    "not_filed_managers": 2,
    "failed_managers": 1,
    "manager_results": [{"cik": "...", "status": "updated", "accessions": ["..."]}],
    "rows_written": 1234,
}
```

- [x] **Step 6: Test transaction isolation and replay**

Use a fake DB with `begin/commit/rollback/execute/executemany/query`. Assert a second identical
accession uses UPSERT and reports `already_current` or the same stable row counts without creating
new logical holdings. Force the second manager parser to fail and assert the first manager commits
while the second rolls back.

- [x] **Step 7: Run Task 3 verification and commit**

```bash
.venv/bin/python -m pytest tests/test_institutional_13f_refresh.py -q
.venv/bin/python -m pytest tests/test_institutional_portfolios.py -q
.venv/bin/python -m py_compile finance/data/institutional_13f.py finance/data/institutional_13f_edgar.py
git add finance/data/institutional_13f.py finance/data/institutional_13f_edgar.py \
  tests/test_institutional_13f_refresh.py tests/test_institutional_portfolios.py
git commit -m "기능: 관심 기관 EDGAR 13F 개별 수집 추가"
```

---

### Task 4: Amendment-Aware Effective Quarter Loader

**Files:**

- Modify: `finance/loaders/institutional_13f.py`
- Modify: `tests/test_institutional_13f_refresh.py`
- Modify: `tests/test_institutional_portfolios.py`

**Interfaces:**

- Produces: `resolve_effective_13f_quarter(filings, holdings_by_accession) -> dict[str, Any]`
- Produces: `load_institutional_13f_effective_quarter(cik, report_period=None, ...) -> dict`
- Produces: `load_institutional_13f_effective_history(cik, *, limit=8, ...) -> list[dict]`
- Changes: `load_institutional_13f_portfolio_bundle` uses the latest two effective quarters.
- Consumes: Task 6 quarter-review service.

- [x] **Step 1: Add RED resolver tests**

```python
def test_effective_quarter_restatement_replaces_and_addition_extends() -> None:
    resolved = resolve_effective_13f_quarter(
        filings=[BASE, RESTATEMENT, ADDITION],
        holdings_by_accession={
            BASE["accession_number"]: pd.DataFrame([APPLE_10, BAC_20]),
            RESTATEMENT["accession_number"]: pd.DataFrame([APPLE_12]),
            ADDITION["accession_number"]: pd.DataFrame([COCA_COLA_5]),
        },
    )
    assert resolved["source_accessions"] == [RESTATEMENT["accession_number"], ADDITION["accession_number"]]
    assert set(resolved["holdings"]["cusip"]) == {"037833100", "191216100"}
    assert resolved["warning"] == ""
```

Add cases for additive amendment without a base, unknown amendment type, and one-quarter history.
Unknown chains must return `available=False` rather than choosing the newest accession.

- [x] **Step 2: Run focused loader tests and confirm RED**

Run: `.venv/bin/python -m pytest tests/test_institutional_13f_refresh.py -q`

- [x] **Step 3: Implement pure effective-quarter resolution**

Sort by filing date and accession. Use the latest accepted base as the starting table; a
`RESTATEMENT` resets it; `NEW HOLDINGS` appends. Preserve `source_accessions`, latest filing date,
base report period, amendment warning and `available`.

Do not deduplicate different discretion rows prematurely. The later service aggregates by the
approved position identity.

- [x] **Step 4: Add DB history readers**

Query distinct report periods for the CIK, load every filing and its holdings for each requested
period, and pass the chain through the pure resolver. Avoid N+1 connections by using one DB
connection inside each history load. Keep the public result:

```python
{
    "available": True,
    "manager": {"cik": "...", "manager_name": "..."},
    "filing": {"period_of_report": "2026-06-30", "filing_date": "2026-08-14"},
    "holdings": pd.DataFrame(...),
    "source_accessions": ["..."],
    "warning": "",
}
```

- [x] **Step 5: Migrate the portfolio bundle safely**

Make `load_institutional_13f_portfolio_bundle` return its existing keys plus
`latest_effective`/`previous_effective`. Populate legacy `latest_filing`, `latest_holdings`,
`previous_filing`, and `previous_holdings` from the resolver so current callers remain compatible.

Update tests that previously assumed the latest accession alone owns the full portfolio.

- [x] **Step 6: Run Task 4 verification and commit**

```bash
.venv/bin/python -m pytest tests/test_institutional_13f_refresh.py -q
.venv/bin/python -m pytest tests/test_institutional_portfolios.py -q
.venv/bin/python -m py_compile finance/loaders/institutional_13f.py
git add finance/loaders/institutional_13f.py tests/test_institutional_13f_refresh.py \
  tests/test_institutional_portfolios.py
git commit -m "기능: 13F 수정공시 유효 분기 해석 추가"
```

---

### Task 5: Hybrid Refresh Job And Explicit Streamlit Event

**Files:**

- Modify: `app/jobs/ingestion_jobs.py`
- Modify: `app/web/institutional_portfolios.py`
- Modify: `app/services/institutional_portfolios.py`
- Modify: `tests/test_institutional_13f_refresh.py`
- Modify: `tests/test_institutional_portfolios.py`

**Interfaces:**

- Produces: `run_refresh_institutional_13f_hybrid(*, report_period, ciks,
  user_agent=None, progress_callback=None,
  discovery=discover_sec_13f_dataset_candidate,
  bulk_collector=collect_and_store_sec_13f_dataset,
  watchlist_collector=collect_and_store_sec_13f_watchlist) -> JobResult`
- Produces event: `{id: "refresh_institutional_13f", report_period: "YYYY-MM-DD"}`
- Consumes: Task 1 action, Task 2 bulk discovery, Task 3 individual collector.

- [x] **Step 1: Write RED orchestration tests**

Test these exact branches with injected callables:

1. bulk candidate exists -> bulk collector called, EDGAR collector not called;
2. bulk candidate absent -> watchlist collector called;
3. discovery error -> failed JobResult, no collector called;
4. individual partial result -> JobResult `status="partial"` and manager counts preserved.

```python
result = run_refresh_institutional_13f_hybrid(
    report_period="2026-06-30",
    ciks=["0001067983"],
    discovery=lambda *_a, **_k: None,
    watchlist_collector=lambda **_k: {"updated_managers": 1, "failed_managers": 0, "rows_written": 29},
)
assert result["status"] == "success"
assert result["details"]["refresh_mode"] == "individual_edgar"
```

- [x] **Step 2: Run orchestration tests and confirm RED**

Run: `.venv/bin/python -m pytest tests/test_institutional_13f_refresh.py -q`

- [x] **Step 3: Implement bulk-first job orchestration**

Reuse `_build_result` and progress events. Validate the report period is a quarter end. Bulk mode
passes the discovered URL/label into `collect_and_store_sec_13f_dataset`; fallback mode calls the
watchlist collector with only curated CIKs. Map results to `success`, `partial`, `no_update`, or
`failed` without calling both sources in one run.

- [x] **Step 4: Replace the normal React event boundary**

Add handling in `_handle_workbench_event`:

```python
if event_name == "refresh_institutional_13f":
    report_period = str(payload.get("report_period") or "").strip()
    result = run_refresh_institutional_13f_hybrid(
        report_period=report_period,
        ciks=[row["cik"] for row in INSTITUTIONAL_MANAGER_WATCHLIST],
    )
    st.session_state["institutional_13f_refresh_result"] = result
    clear manager/popularity/security caches
    st.rerun()
```

Do not accept dataset URL/local path from the React event. Keep the old direct bulk runner only in
Data Operations and the existing non-React fallback recovery path; do not render those inputs in
the healthy React workflow.

- [x] **Step 5: Build the due action from local manager periods**

During page composition, read the watchlist managers already loaded from DB, create the
`manager_periods` mapping, call Task 1's pure action, and pass it to the payload. No network mock
should be required by the page render test.

- [x] **Step 6: Run Task 5 tests and commit**

```bash
.venv/bin/python -m pytest tests/test_institutional_13f_refresh.py -q
.venv/bin/python -m pytest tests/test_institutional_portfolios.py -q
.venv/bin/python -m py_compile app/jobs/ingestion_jobs.py app/web/institutional_portfolios.py \
  app/services/institutional_portfolios.py
git add app/jobs/ingestion_jobs.py app/web/institutional_portfolios.py \
  app/services/institutional_portfolios.py tests/test_institutional_13f_refresh.py \
  tests/test_institutional_portfolios.py
git commit -m "기능: 13F 하이브리드 수동 갱신 연결"
```

---

### Task 6: Position Changes And Two Performance Proxies

**Files:**

- Create: `app/services/institutional_quarter_review.py`
- Create: `tests/test_institutional_quarter_review.py`
- Modify: `app/services/institutional_portfolios.py`

**Interfaces:**

- Produces: `build_institutional_position_changes(previous_holdings,
  current_holdings) -> list[dict]`
- Produces: `build_institutional_price_proxy(holdings, price_history, *, start_date,
  end_date, proxy_id) -> dict`
- Produces: `build_institutional_quarter_review(*, previous_effective,
  current_effective, price_history) -> dict`
- Produces: `load_institutional_quarter_review_model(cik) -> dict`
- Consumes: Task 4 effective history and `load_price_history`.

- [ ] **Step 1: Write failing change-label tests**

Build previous/current frames with unchanged market value but changed shares and with changed market
value but unchanged shares. Assert labels follow shares/principal only:

```python
labels = {row["cusip"]: row["change_type"] for row in changes}
assert labels == {
    "NEWCUSIP1": "NEW",
    "ADDCUSIP1": "ADD",
    "KEEPCUSI1": "KEEP",
    "REDCUSIP1": "REDUCE",
    "DROPCUSI1": "DROP",
}
```

Include put/call and amount type in identity and assert missing amounts become `NOT_COMPARABLE`.

- [ ] **Step 2: Write failing proxy tests**

Use two holdings with 60/40 starting weights, only the first covered by prices. Assert:

```python
assert proxy["coverage_weight_pct"] == 60.0
assert proxy["status"] == "LIMITED"
assert proxy["covered_sleeve_return_pct"] == 10.0
assert proxy["missing_weight_pct"] == 40.0
```

Add READY at 80%, NOT_AVAILABLE below 50%, first close on/after start, last close on/before end,
and option exclusion. Missing positions must not appear as zero-return contributions.

- [ ] **Step 3: Run review tests and confirm RED**

Run: `.venv/bin/python -m pytest tests/test_institutional_quarter_review.py -q`

- [ ] **Step 4: Implement deterministic position aggregation and labels**

Aggregate raw filing rows by `(cusip, title_of_class, normalized put_call, amount_type)` and sum
reported value/share amount only when evidence is numeric. Preserve issuer, symbol, sector, mapping
status and prior/current weights. Sort output by previous weight then current weight descending.

- [ ] **Step 5: Implement price proxy and contribution**

Use previous-quarter reported values for weights. Include only mapped common-stock rows without a
put/call marker. Return covered-sleeve return, coverage, missing reasons, symbol rows, contribution
leaders and detractors. The contribution for a covered symbol is
`reported_weight_pct * symbol_return_pct / 100`; the aggregate covered-sleeve return divides the
sum of contributions by covered weight, never by 100 when coverage is partial.

- [ ] **Step 6: Compose both approved windows**

`build_institutional_quarter_review` uses:

- `quarter_holdings_proxy`: previous report period -> current report period
- `public_follow_proxy`: previous filing date -> current filing date

If fewer than two effective quarters exist, return `available=False` and
`reason="비교할 이전 보고 분기가 저장되어 있지 않습니다."` with empty changes/proxies.

- [ ] **Step 7: Add DB-backed loader service**

`load_institutional_quarter_review_model` loads the latest two effective quarters, collects previous
holding mapped symbols, reads one combined daily price range from DB, and calls the pure builder.
It does not fetch missing OHLCV automatically.

- [ ] **Step 8: Run Task 6 verification and commit**

```bash
.venv/bin/python -m pytest tests/test_institutional_quarter_review.py -q
.venv/bin/python -m pytest tests/test_institutional_portfolios.py -q
.venv/bin/python -m py_compile app/services/institutional_quarter_review.py \
  app/services/institutional_portfolios.py
git add app/services/institutional_quarter_review.py app/services/institutional_portfolios.py \
  tests/test_institutional_quarter_review.py tests/test_institutional_portfolios.py
git commit -m "기능: 13F 분기 변화와 두 성과 proxy 추가"
```

---

### Task 7: Python Workbench V3 Contract

**Files:**

- Modify: `app/services/institutional_portfolios.py`
- Modify: `app/web/institutional_portfolios.py`
- Modify: `tests/test_institutional_portfolios.py`

**Interfaces:**

- Changes schema version: `institutional_portfolios_workbench_v3`
- Adds payload: `quarter_review`
- Adds refresh action states from Task 1 and result states from Task 5.
- Consumes: Task 6 `load_institutional_quarter_review_model`.

- [ ] **Step 1: Add RED payload contract tests**

Assert the payload contains:

```python
assert payload["schema_version"] == "institutional_portfolios_workbench_v3"
assert payload["refresh_action"]["visible"] is True
assert payload["quarter_review"]["available"] is True
assert payload["quarter_review"]["proxies"]["quarter_holdings_proxy"]["status"] == "READY"
assert payload["quarter_review"]["change_summary"]["KEEP"] == 1
```

Also test one-quarter empty state, partial refresh result and current state with no primary action.

- [ ] **Step 2: Run focused tests and confirm RED**

Run: `.venv/bin/python -m pytest tests/test_institutional_portfolios.py -q`

- [ ] **Step 3: Extend payload builder without duplicating calculations**

Add `quarter_review: dict | None` and `refresh_action: dict | None` parameters. The builder formats
labels and presentation rows but does not recalculate returns or change types. Remove default bulk
dataset label/URL from the healthy payload.

- [ ] **Step 4: Load review once per selected manager render**

After the portfolio model succeeds, call `load_institutional_quarter_review_model(selected_cik)` and
pass its model into the workbench payload. On review loader failure, keep the main portfolio live
and provide `quarter_review.available=False` with a concise reason and technical detail outside the
primary UI.

- [ ] **Step 5: Update preview/fallback contracts**

Preview returns v3 with invisible/not-ready refresh action and unavailable quarter review. Fallback
Streamlit copy must not expose the old hardcoded URL as the normal action; link users to Data
Operations for advanced URL/local ZIP recovery.

- [ ] **Step 6: Run Task 7 verification and commit**

```bash
.venv/bin/python -m pytest tests/test_institutional_portfolios.py -q
.venv/bin/python -m pytest tests/test_institutional_13f_refresh.py \
  tests/test_institutional_quarter_review.py -q
git add app/services/institutional_portfolios.py app/web/institutional_portfolios.py \
  tests/test_institutional_portfolios.py
git commit -m "기능: Institutional Holdings v3 분기 리뷰 계약 연결"
```

---

### Task 8: React Refresh Action And Quarter Review Destination

**Files:**

- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/src/workbenchState.ts`
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/src/workbenchState.test.ts`
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/src/InstitutionalStudioShell.tsx`
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/src/InstitutionalPortfoliosWorkbench.tsx`
- Create: `app/web/streamlit_components/institutional_portfolios_workbench/src/QuarterReviewPanel.tsx`
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/src/style.css`
- Regenerate: `app/web/streamlit_components/institutional_portfolios_workbench/component_static/`
- Modify: `tests/test_institutional_portfolios.py`

**Interfaces:**

- Adds `StudioView = ... | "quarter_review"`
- Sends `{id: "refresh_institutional_13f", report_period: string}`
- Renders Python-owned `quarter_review`; React performs filters/sorting only.

- [ ] **Step 1: Write RED navigation/state tests**

Update the canonical destination expectation to:

```typescript
expect(STUDIO_DESTINATIONS.map((item) => item.id)).toEqual([
  "overview", "quarter_review", "holdings", "security", "popularity",
]);
expect(studioDestination("quarter_review").label).toBe("분기 리뷰");
```

Add a pure filter helper test for change type and symbol/issuer query if the review table needs
client-side filtering.

- [ ] **Step 2: Run React tests and confirm RED**

Run: `npm test` in the component directory.

- [ ] **Step 3: Update TypeScript v3 types and event state**

Change `WORKBENCH_SCHEMA_VERSION` to `institutional_portfolios_workbench_v3`. Remove local state for
dataset label/URL/local path/User-Agent from the healthy React path. Add pending action kind
`institutional_refresh` and submit exactly the target report period supplied by Python.

- [ ] **Step 4: Replace the data panel form with conditional action**

Render:

- current: latest report period + next due date, no button;
- due: target quarter message + primary `업데이트 확인 및 갱신`;
- partial: completed/expected manager count + retry button;
- result: success/partial/no-update/failure copy without raw job rows as the page protagonist.

Keep source freshness/caveats in the disclosure. Advanced URL/local ZIP inputs remain only in Data
Operations.

- [ ] **Step 5: Implement the quarter review surface**

Create the focused `QuarterReviewPanel.tsx` and render:

- transition/report dates;
- two proxy cards with return, coverage status and missing weight;
- five change summary filters plus `NOT_COMPARABLE` supporting state;
- contribution leaders/detractors;
- change table with previous/current shares, weights, symbol return and contribution;
- explicit delayed-long-holdings proxy caveat.

Do not calculate return or change labels in React.

- [ ] **Step 6: Add responsive styling**

At desktop use two proxy cards and a compact change summary row. At <=980px stack the cards and
retain the studio drawer. At <=720px make the change table horizontally scroll inside its own
container without causing page-level overflow. Buttons must remain at least 44px high.

- [ ] **Step 7: Run React verification and regenerate tracked bundle**

```bash
npm test
npm run typecheck
npm run build
```

Expected: Vitest pass, TypeScript pass, Vite rebuilds `component_static` with v3 contract.

- [ ] **Step 8: Run Python bundle/source contract tests and commit**

```bash
.venv/bin/python -m pytest tests/test_institutional_portfolios.py -q
git add app/web/streamlit_components/institutional_portfolios_workbench/src \
  app/web/streamlit_components/institutional_portfolios_workbench/component_static \
  tests/test_institutional_portfolios.py
git commit -m "기능: 기관 13F 분기 리뷰 화면 추가"
```

---

### Task 9: Actual SEC/DB/Browser Verification And Documentation Closeout

**Files:**

- Modify: `.aiworkspace/note/finance/docs/flows/INSTITUTIONAL_PORTFOLIOS_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/data/README.md`
- Modify: `.aiworkspace/note/finance/docs/runbooks/INSTITUTIONAL_13F_DATASET.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md` only if implemented ownership differs
- Modify: `.aiworkspace/note/finance/tasks/active/institutional-holdings-hybrid-quarter-review-v1-20260817/{STATUS,NOTES,RUNS,RISKS}.md`
- Modify: `.aiworkspace/note/finance/tasks/active/{README,STATUS_MANIFEST}.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md` because active product baseline/state changes
- Create generated, untracked: `institutional-holdings-hybrid-quarter-review-v1-qa.png`

**Interfaces:**

- Consumes every prior task.
- Produces verified task state and durable source/data/user-flow ownership.

- [ ] **Step 1: Run all focused automated tests**

```bash
.venv/bin/python -m pytest tests/test_institutional_13f_refresh.py \
  tests/test_institutional_quarter_review.py tests/test_institutional_portfolios.py -q
.venv/bin/python -m py_compile finance/data/institutional_13f.py \
  finance/data/institutional_13f_edgar.py finance/loaders/institutional_13f.py \
  app/services/institutional_13f_refresh.py app/services/institutional_quarter_review.py \
  app/services/institutional_portfolios.py app/jobs/ingestion_jobs.py \
  app/web/institutional_portfolios.py
(cd app/web/streamlit_components/institutional_portfolios_workbench && npm test)
(cd app/web/streamlit_components/institutional_portfolios_workbench && npm run typecheck)
(cd app/web/streamlit_components/institutional_portfolios_workbench && npm run build)
git diff --check
```

- [ ] **Step 2: Run bounded live SEC discovery/parser smoke**

With a descriptive `SEC_USER_AGENT`, discover the target Q2 bulk candidate. If bulk remains
unpublished, fetch one approved watchlist CIK submission/index/XML and normalize without writing.
Record URLs, accession, report period, row count, duration and any SEC access limit in `RUNS.md`.

Do not repeatedly download the full bulk ZIP.

- [ ] **Step 3: Run actual MySQL replay**

Use the already public Q2 watchlist filings to run the explicit hybrid job against local MySQL.
Verify:

- at least Berkshire, Bridgewater and Duquesne resolve to report period `2026-06-30` when SEC
  access succeeds;
- a second run is idempotent;
- latest and previous effective quarters both load;
- position changes do not treat market-value-only differences as ADD/REDUCE;
- both performance proxies report coverage and never fabricate missing returns.

If live SEC access or DB is unavailable, keep the task active and record the exact remaining gap;
do not claim actual verification.

- [ ] **Step 4: Run actual Browser QA**

Start the current app and verify at 1280px, 760px and 420px:

1. current state has no primary refresh button;
2. due/partial state shows the correct target quarter action;
3. click triggers one server event and preserves the stored portfolio during loading/failure;
4. successful refresh updates report period and quarter review;
5. `분기 리뷰` shows both proxies, coverage, change filters and table;
6. one-quarter unavailable state explains the missing comparison;
7. no page-level horizontal overflow or browser console error/warning.

Save one final desktop screenshot outside Git and attach it in the final response.

- [ ] **Step 5: Apply `finance-doc-sync`**

Update durable docs only for implemented facts:

- flow: local due -> explicit hybrid refresh -> review;
- architecture: bulk discovery, individual EDGAR parser and effective-quarter loader;
- data: raw accession ledger, amendment composition and proxy coverage meaning;
- runbook: normal button workflow, advanced URL/local ZIP recovery, SEC User-Agent and retries;
- Roadmap: active task to complete and Institutional Holdings baseline.

Record `canonical doc change 없음` for any listed canonical document whose owned facts did not
change.

- [ ] **Step 6: Run documentation and Git checks**

```bash
git diff --check
git status --short
rg -n "State:|전체.*차|Next Action" \
  .aiworkspace/note/finance/tasks/active/institutional-holdings-hybrid-quarter-review-v1-20260817
```

Confirm registry JSONL, run history, local artifacts and unrelated dirty files are unstaged.

- [ ] **Step 7: Request final code review**

Apply `superpowers:requesting-code-review` to the complete diff. Resolve correctness, regression,
data integrity, missing validation, scope and documentation findings before closeout.

- [ ] **Step 8: Commit closeout**

```bash
git add app/jobs/ingestion_jobs.py app/services/institutional_13f_refresh.py \
  app/services/institutional_portfolios.py app/services/institutional_quarter_review.py \
  app/web/institutional_portfolios.py \
  app/web/streamlit_components/institutional_portfolios_workbench/src \
  app/web/streamlit_components/institutional_portfolios_workbench/component_static \
  finance/data/institutional_13f.py finance/data/institutional_13f_edgar.py \
  finance/loaders/institutional_13f.py tests/test_institutional_13f_refresh.py \
  tests/test_institutional_portfolios.py tests/test_institutional_quarter_review.py \
  .aiworkspace/note/finance/docs/flows/INSTITUTIONAL_PORTFOLIOS_FLOW.md \
  .aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md \
  .aiworkspace/note/finance/docs/data/README.md \
  .aiworkspace/note/finance/docs/runbooks/INSTITUTIONAL_13F_DATASET.md \
  .aiworkspace/note/finance/docs/PROJECT_MAP.md .aiworkspace/note/finance/docs/ROADMAP.md \
  .aiworkspace/note/finance/tasks/active/institutional-holdings-hybrid-quarter-review-v1-20260817 \
  .aiworkspace/note/finance/tasks/active/README.md \
  .aiworkspace/note/finance/tasks/active/STATUS_MANIFEST.md
git commit -m "완료: 기관 13F 하이브리드 분기 리뷰"
```

Do not include the Browser screenshot, registry JSONL, run history or unrelated user files.

## Plan Self-Review Checklist

- [x] Every approved spec requirement maps to a numbered task.
- [x] Function names and payload keys are consistent across producers and consumers.
- [x] No step requires an automatic page-entry external request.
- [x] Bulk and individual ingestion remain idempotent and preserve raw source evidence.
- [x] Amendment, partial filing, missing price and identifier ambiguity fail closed.
- [x] Both approved performance windows and all approved change labels have deterministic tests.
- [x] React only presents Python-owned financial calculations.
- [x] Actual SEC/DB/Browser evidence is required before `State: complete`.
