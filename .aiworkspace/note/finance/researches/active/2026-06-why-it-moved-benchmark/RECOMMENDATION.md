# Why It Moved V1.6 Recommendation

Status: Active
Last Updated: 2026-06-04

## Recommendation Summary

Do a `Why It Moved V1.6 UX Pass` before adding more data providers.

The benchmark pattern is consistent: stock investigation pages are not primarily link launchers. They start with identity and movement context, then separate evidence by source type: news, documents / filings, financials / earnings, ratings / analyst context, and external research tools. For this project, only the first three are safe for V1.6 because automatic judgement, AI summary, body collection, ratings, and storage are explicitly out of scope.

## V1.6 Product Goal

Turn `Why It Moved` from a prototype-like metadata/link panel into a manual investigation board.

It should help the user answer:

- Which selected mover am I investigating?
- How large was the move relative to the previous period?
- Did compact metadata lookup run?
- Which source lanes returned leads?
- Which lanes failed or returned nothing?
- Where can I open external research if the compact metadata is not enough?

It should not answer:

- What was the true cause?
- Is this bullish or bearish?
- Should I buy or sell?
- What does the article / filing body say?

## V1.6 Implementation Scope

Code files:

- `app/web/overview_dashboard.py`
- `app/services/overview_market_intelligence.py` only if a small Streamlit-free status/read-model helper is needed
- `tests/test_service_contracts.py`

Documentation files:

- `.aiworkspace/note/finance/tasks/active/overview-market-movers-second-pass/STATUS.md`
- `.aiworkspace/note/finance/tasks/active/overview-market-movers-second-pass/NOTES.md`
- `.aiworkspace/note/finance/tasks/active/overview-market-movers-second-pass/RUNS.md`
- `.aiworkspace/note/finance/tasks/active/overview-market-movers-second-pass/RISKS.md`
- `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md`
- `.aiworkspace/note/finance/docs/ROADMAP.md`
- root handoff logs only 3-5 lines if implementation is completed

Out of scope:

- DB schema change
- registry / saved JSONL write
- article body collection
- filing body collection
- AI summary
- sentiment analysis
- automatic catalyst classification
- Korean news scraping
- broker / order / alert automation

## Step-by-Step Guideline

### Step 1: Keep Service Boundary Intact

- Preserve `fetch_market_mover_compact_metadata` as selected-ticker, button-triggered, session-only.
- Preserve status values:
  - `NOT_REQUESTED`
  - `OK`
  - `PARTIAL`
  - `FAILED`
  - `NO_METADATA`
- If adding helper logic, keep it Streamlit-free in `app/services/overview_market_intelligence.py`.

### Step 2: Rebuild Panel Layout

In `app/web/overview_dashboard.py`, restructure `_render_market_mover_why_it_moved_panel` into this visible order:

1. title and boundary caption
2. ticker selector
3. movement summary header
4. metadata status strip
5. fetch compact metadata button
6. investigation leads sections

Use compact sections instead of a large raw fact grid.

### Step 3: Add Movement Summary Header

Render the selected mover as a single scan-first header with grouped facts:

- Identity: Symbol, Name, Sector, Industry, Market Cap
- Context: Period, Coverage, Rank Type, Rank
- Movement: Return %, Previous Return %, Momentum Delta, Volume, Dollar Volume

Avoid recommendation copy. Momentum delta is context only.

### Step 4: Add Metadata Status Strip

Before the metadata tables, show:

- Lookup status
- News row count or failure
- SEC row count or failure
- Fetched at timestamp if available
- Storage boundary: `Session-only`

Expected behavior:

- `NOT_REQUESTED`: neutral info
- `OK`: success
- `PARTIAL`: warning
- `FAILED`: error
- `NO_METADATA`: warning / empty state

### Step 5: Rename And Group Metadata

Rename `Compact Metadata` to `Investigation Leads`.

Use either tabs or stacked sections:

- `News Metadata`
- `SEC Filings`
- `External Searches`

Keep URL cells clickable with `Open`.

### Step 6: Improve SEC Filing Readability

- Keep columns compact: `Form`, `Filing Date`, `Title`, `Open`.
- Sort or visually prioritize likely relevant forms:
  - `8-K`
  - `10-Q`
  - `10-K`
  - `S-1`
  - `S-3`
  - `S-8`
  - `4`
  - others
- Add a small optional helper text that these are filing metadata leads, not parsed filing conclusions.

### Step 7: Keep External Searches Secondary

- Keep `External searches` collapsed by default.
- Preserve current rows:
  - Yahoo Finance
  - Google News
  - SEC Company Search
  - Investor Relations / Earnings Search
  - Google News KR
  - Naver News
- Keep `Open` next to `Source`.
- Do not reintroduce primary link buttons.

### Step 8: Test First

Add focused tests before implementation:

- Status strip helper returns expected labels/counts for `OK`, `PARTIAL`, `FAILED`, `NO_METADATA`, `NOT_REQUESTED`.
- External searches table keeps clickable URL config.
- If SEC priority helper is added, it sorts form types deterministically.
- Existing compact metadata tests still pass.

### Step 9: Verify

Run:

```bash
uv run python -m py_compile app/services/overview_market_intelligence.py app/web/overview_dashboard.py
uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests
uv run python -m unittest tests.test_service_contracts
uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
git diff --check
```

Browser QA:

- Open `http://localhost:8525/` or restart Streamlit if needed.
- Verify Why It Moved renders.
- Verify external searches are collapsed by default.
- Verify fetch button is still the only external metadata lookup trigger.
- Verify no Research Link button grid returns.
- Save screenshot, but do not commit it.

## Suggested Future Versions

### V1.7 Metadata Quality

- Provider-specific empty/failure message inside each lane.
- More compact table columns.
- SEC form priority and form hints.
- News source/domain visibility.

### V1.8 Korean Source Policy

- Decide whether Korean metadata fetch is worth adding.
- If yes, define provider, credential, quota, terms, body exclusion, session-only/storage policy.
- Until then, keep Korean sources outbound-only.

### V2 Storage

- Only consider DB-backed compact metadata after retention, freshness, replay, provider throttling, and schema policy are approved.

## New Session Paste Request

```text
작업 위치:
- worktree: /Users/taeho/Project/quant-data-pipeline-worktrees/main-dev
- 관련 active task: .aiworkspace/note/finance/tasks/active/overview-market-movers-second-pass/
- benchmark research: .aiworkspace/note/finance/researches/active/2026-06-why-it-moved-benchmark/

요청:
Overview > Market Movers > Why It Moved V1.6 UX Pass를 구현해줘.

진행 원칙:
- AGENTS.md 기준으로 finance-task-intake부터 진행한다.
- Overview / Market Movers 관련 문서 경계를 확인한다.
- benchmark research의 BENCHMARKS.md, UI_PATTERNS.md, RECOMMENDATION.md를 먼저 읽고 구현한다.
- 이 작업은 automatic catalyst classifier가 아니라 manual investigation board UX 개선이다.
- DB schema 변경 금지.
- registry / saved JSONL 저장 금지.
- article body / filing body 수집 금지.
- AI summary / sentiment analysis / automatic cause judgement 금지.
- selectbox 변경만으로 외부 조회 금지.
- compact metadata fetch는 버튼 기반, 선택 ticker 1개, session-only를 유지한다.
- unrelated dirty files와 generated artifacts는 건드리지 않는다.

구현 목표:
- 현재 Why It Moved의 prototype-like fact grid / raw metadata layout을 investigation board로 재구성한다.
- 화면 순서는 title/boundary caption -> ticker selector -> movement summary header -> metadata status strip -> Fetch compact metadata button -> Investigation Leads sections로 정리한다.
- movement summary header에는 Symbol, Name, Sector, Industry, Market Cap, Period, Coverage, Rank Type, Rank, Return %, Previous Return %, Momentum Delta, Volume, Dollar Volume을 compact하게 보여준다.
- metadata status strip에는 Lookup status, News row count/failure, SEC row count/failure, fetched_at, Session-only boundary를 표시한다.
- `PARTIAL`은 warning 상태로 보여주고 complete success처럼 보이면 안 된다.
- `Compact Metadata` 명칭은 `Investigation Leads`로 바꾼다.
- Investigation Leads는 News Metadata / SEC Filings / External Searches로 나눈다.
- 모든 URL은 clickable `Open` link로 유지한다.
- External Searches는 collapsed by default이고 primary link button grid를 다시 만들지 않는다.
- Korean Google News / Naver News는 outbound external search row로 유지한다.
- SEC filings는 form/date/title/open 중심으로 compact하게 표시하고, 가능하면 8-K, 10-Q, 10-K, S-1, S-3, S-8, 4, others 순으로 우선순위를 둔다.

TDD:
- service/UI helper contract test를 먼저 작성하고 red 확인한다.
- PARTIAL / FAILED / NO_METADATA / NOT_REQUESTED status strip contract를 테스트한다.
- clickable URL column config와 External Searches collapsed-table contract를 테스트한다.
- SEC form priority helper를 만들 경우 deterministic sort를 테스트한다.

검증:
- uv run python -m py_compile app/services/overview_market_intelligence.py app/web/overview_dashboard.py
- uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests
- uv run python -m unittest tests.test_service_contracts
- uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
- git diff --check
- Browser QA screenshot 생성. screenshot은 커밋하지 않는다.

문서:
- active task STATUS / NOTES / RUNS / RISKS 갱신.
- .aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md에 V1.6 사용자 흐름 반영.
- ROADMAP row 업데이트.
- root handoff logs는 3~5줄 핵심만 업데이트.

커밋:
- generated artifact, run_history, local screenshot, .DS_Store, unrelated dirty files는 stage하지 않는다.
- coherent commit을 만들고 commit message는 한국어로 작성한다.
```
