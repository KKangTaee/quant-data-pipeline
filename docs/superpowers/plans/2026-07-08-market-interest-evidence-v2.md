# Market Interest Evidence V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the Market Movers selected-symbol `시장 관심` panel from a link hub into a user-readable evidence panel that combines session news, Korean news, SEC filing metadata, analyst-source readiness, delayed 13F context, and source links without recommendation or signal semantics.

**Architecture:** Keep `app/services/overview/market_interest.py` as the Streamlit-free read model. The Market Movers helper remains the UI/session orchestration layer and reuses existing `why_it_moved` metadata fetchers for news, Korean news, and issuer SEC filing metadata. No DB schema, 13F ingestion, article body, analyst report body, filing body, broker/trading connection, or provider API-key integration is added in this pass.

**Tech Stack:** Python 3.12, pandas, Streamlit, existing `tests/test_service_contracts.py` service contracts, Browser QA with the Finance Streamlit app.

---

## File Structure

- Modify `app/services/overview/market_interest.py`
  - Own V2 read model shape, evidence sections, conservative summary states, source groups, and disabled analyst provider readiness.
- Modify `app/web/overview/market_movers_helpers.py`
  - Orchestrate selected-symbol metadata fetch for the Market Interest action.
  - Render one `시장 관심` tab with evidence sections and lower source-link disclosure.
  - Remove redundant `뉴스`, `SEC 공시`, and `외부 검색` tabs from the selected-symbol clue tabs.
- Modify `tests/test_service_contracts.py`
  - Add RED/GREEN tests for the V2 read model, action fetch behavior, and tab consolidation.
- Add/update `.aiworkspace/note/finance/tasks/active/overview-market-interest-evidence-v2-20260708/*`
  - Track plan/status/runs/risks/notes for this follow-up.
- Update durable docs at closeout:
  - `.aiworkspace/note/finance/docs/ROADMAP.md`
  - `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
  - `.aiworkspace/note/finance/docs/data/README.md`
  - `.aiworkspace/note/finance/WORK_PROGRESS.md`
  - `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

## Task 1: V2 Read Model With Evidence Sections

**Files:**
- Modify: `app/services/overview/market_interest.py`
- Test: `tests/test_service_contracts.py`

- [ ] **Step 1: Write failing service tests**

Add tests to `OverviewMarketIntelligenceServiceContractTests`:

```python
def test_market_interest_v2_builds_evidence_sections_from_existing_metadata(self) -> None:
    from app.services.overview.market_interest import build_market_interest_read_model

    metadata = {
        "status": "OK",
        "news": pd.DataFrame(
            [{"Title": "US headline", "Source": "Desk", "Published At": "2026-07-08", "URL": "https://example.com/us"}]
        ),
        "korean_news": pd.DataFrame(
            [
                {
                    "Title": "한국 뉴스",
                    "Source": "Google News KR",
                    "Published At": "2026-07-08",
                    "Snippet": "한국어 메타데이터",
                    "URL": "https://example.com/kr",
                }
            ]
        ),
        "sec_filings": pd.DataFrame(
            [{"Form": "8-K", "Filing Date": "2026-07-07", "Title": "Current report", "URL": "https://sec.gov/8k"}]
        ),
    }

    model = build_market_interest_read_model(mover={"Symbol": "NET", "Name": "Cloudflare Inc"}, metadata=metadata)

    self.assertEqual(model["schema_version"], "market_interest_evidence_v2")
    summaries = {item["id"]: item for item in model["summary_items"]}
    self.assertEqual(summaries["news_sec"]["state"], "뉴스 2건 / 공시 1건")
    self.assertEqual(summaries["analyst_interest"]["state"], "구조화 소스 미연결")
    self.assertEqual(summaries["institutional_context"]["state"], "13F 지연 자료")
    sections = {section["id"]: section for section in model["evidence_sections"]}
    self.assertEqual(len(sections["news_sec"]["rows"]), 3)
    self.assertEqual(sections["news_sec"]["rows"][1]["Region"], "KR")
    self.assertEqual(sections["news_sec"]["rows"][2]["Kind"], "SEC Filing")
    self.assertTrue(model["source_disclosure"]["rows"])
    self.assertNotIn("기관이 지금 사고", str(model))
```

- [ ] **Step 2: Run RED test**

Run:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_interest_v2_builds_evidence_sections_from_existing_metadata
```

Expected: FAIL because `schema_version` and `evidence_sections` are not V2 yet.

- [ ] **Step 3: Implement V2 read model**

Update `build_market_interest_read_model` to:

- Return `schema_version: market_interest_evidence_v2`.
- Build `summary_items` with these states:
  - `analyst_interest`: `구조화 소스 미연결`
  - `news_sec`: `뉴스 {news_count}건 / 공시 {sec_count}건` when any evidence exists, otherwise `조회 전`
  - `institutional_context`: `13F 지연 자료`
  - `sources`: `출처 {link_count}개`
- Add `evidence_sections`:
  - `analyst_interest`: rows are empty until API-key source is approved, but include `provider_status`.
  - `news_sec`: rows from `news`, `korean_news`, and `sec_filings`.
  - `institutional_context`: 13F caveat rows and official links.
- Add `source_disclosure` with grouped source links.

- [ ] **Step 4: Run GREEN test**

Run the same unittest command.

Expected: PASS.

## Task 2: Market Interest Action Fetches News/Korean News/SEC Metadata

**Files:**
- Modify: `app/web/overview/market_movers_helpers.py`
- Test: `tests/test_service_contracts.py`

- [ ] **Step 1: Write failing action test**

Add a test that patches `fetch_market_mover_news_metadata`, `fetch_market_mover_sec_metadata`, `merge_market_mover_metadata`, and `st`.

Expected behavior:

- React event `fetch_market_interest` calls both existing fetchers for selected symbol.
- It merges news metadata and SEC metadata.
- It stores both `metadata_key` and `metadata_key__market_interest`.
- It does not call any new provider or DB path.

- [ ] **Step 2: Run RED test**

Run:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_mover_market_interest_react_event_fetches_existing_metadata_before_building_model
```

Expected: FAIL because current action only builds from already-stored metadata.

- [ ] **Step 3: Implement action fetch behavior**

Update `_dispatch_market_mover_investigation_react_event` and Streamlit fallback button path so `fetch_market_interest`:

1. Calls `fetch_market_mover_news_metadata(symbol, name=identity.get("Name"), max_news=3, max_korean_news=3)`.
2. Merges result into current session metadata.
3. Calls `fetch_market_mover_sec_metadata(symbol, max_filings=3)`.
4. Merges result into current session metadata.
5. Stores merged metadata under `metadata_key`.
6. Builds and stores `build_market_interest_read_model(..., metadata=metadata)`.
7. Reruns.

- [ ] **Step 4: Run GREEN test**

Run the same unittest command.

Expected: PASS.

## Task 3: Consolidate Selected-Symbol Tabs

**Files:**
- Modify: `app/web/overview/market_movers_helpers.py`
- Test: `tests/test_service_contracts.py`

- [ ] **Step 1: Write failing UI source contract test**

Add/update tests to assert:

- Selected-symbol clue tabs are exactly `["기본 지표", "시장 관심"]`.
- There is no separate selected-symbol `뉴스`, `SEC 공시`, or `외부 검색` tab.
- `뉴스/공시 촉매`, `애널리스트 관심`, `기관 보유 배경`, and `출처/원문 링크` appear in the `시장 관심` renderer.

- [ ] **Step 2: Run RED test**

Run:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_market_movers_redesign_v2_phase5_uses_investigation_pane tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_movers_selected_investigation_consolidates_market_interest_tabs
```

Expected: FAIL while old tabs remain.

- [ ] **Step 3: Implement tab consolidation**

Update `_render_market_mover_selected_investigation_fragment`:

```python
clue_tabs = st.tabs(["기본 지표", "시장 관심"])
with clue_tabs[0]:
    render_market_mover_research_snapshot(research_model)
with clue_tabs[1]:
    _render_market_mover_market_interest(market_interest_model, requested=market_interest_requested)
```

Remove duplicated inline render blocks for old `뉴스`, `SEC 공시`, and `외부 검색` tabs from this selected-symbol fragment.

- [ ] **Step 4: Run GREEN test**

Run the same unittest command.

Expected: PASS.

## Task 4: Render Evidence Sections Instead Of Link Tables

**Files:**
- Modify: `app/web/overview/market_movers_helpers.py`
- Test: `tests/test_service_contracts.py`

- [ ] **Step 1: Write failing renderer source contract test**

Assert `_render_market_mover_market_interest` renders:

- summary cards with non-duplicative states
- `애널리스트 관심`
- `뉴스/공시 촉매`
- `기관 보유 배경 · 13F 지연 자료`
- `출처/원문 링크`

Assert it does not render `원문 확인` as a primary summary item label.

- [ ] **Step 2: Run RED test**

Run the renderer/source contract test.

Expected: FAIL because V1 renderer still exposes `원문 확인` as primary section/card.

- [ ] **Step 3: Implement evidence section renderer**

Update `_render_market_mover_market_interest` so it:

- Uses `evidence_sections` from the model.
- For analyst section, shows provider status and a clear disabled message: `FMP/Finnhub 같은 구조화 analyst source는 API key/약관 승인 후 연결합니다.`
- For news/SEC section, renders a combined table with `Kind`, `Region`, `Title`, `Source`, `Published At`, `Open`.
- For institutional section, renders 13F caveat first, then official/source links.
- Renders source disclosure in an expander titled `출처/원문 링크`.

- [ ] **Step 4: Run GREEN test**

Run the renderer/source contract test.

Expected: PASS.

## Task 5: Docs, QA, Browser QA, Commit

**Files:**
- Modify docs listed above.

- [ ] **Step 1: Update task docs**

Create/update:

- `.aiworkspace/note/finance/tasks/active/overview-market-interest-evidence-v2-20260708/PLAN.md`
- `STATUS.md`
- `NOTES.md`
- `RUNS.md`
- `RISKS.md`

- [ ] **Step 2: Run focused verification**

Run:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests tests.test_service_contracts.OverviewAutomationContractTests.test_market_movers_redesign_v2_phase5_uses_investigation_pane tests.test_service_contracts.OverviewAutomationContractTests.test_market_mover_investigation_react_payload_hides_statement_action_when_current
.venv/bin/python -m py_compile app/services/overview/market_interest.py app/web/overview/market_movers_helpers.py
git diff --check
```

Expected: all commands exit 0.

- [ ] **Step 3: Browser QA**

Run Streamlit locally, open `Overview > Market Movers`, click `시장 관심 근거 확인`, and verify:

- Only two selected-symbol clue tabs: `기본 지표`, `시장 관심`.
- `시장 관심` tab shows news/Korean news/SEC rows after click.
- `출처/원문 링크` is lower disclosure, not a primary tab.
- Screenshot is saved locally and not committed.

- [ ] **Step 4: Update durable docs**

Update roadmap/project/data docs and root logs to say Market Interest V2 consolidates selected-symbol news/SEC/source links under the Market Interest evidence panel and keeps 13F as delayed source context only.

- [ ] **Step 5: Commit**

Stage only code/tests/task docs/durable docs/plan. Do not stage generated screenshots or unrelated untracked research bundle.

Commit:

```bash
git commit -m "Market Movers 시장 관심 근거 패널 개선"
```

---

## Self-Review

- Spec coverage: Covers 1차 UI IA, 2차 existing metadata fetch, 3차 analyst source readiness, 4차 13F separation, 5차 source-link disclosure.
- Scope check: Does not implement FMP/Finnhub, Naver API key source, or 13F DB ingestion because those require credentials/source-policy approval.
- Placeholder scan: No TODO/TBD placeholders remain.
- Type consistency: V2 model uses dict/list rows for UI-friendly rendering while source links remain DataFrame-compatible only inside the service boundary when needed.
