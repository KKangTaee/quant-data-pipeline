# Market Interest News SEC Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Separate selected-symbol market-interest news rows from SEC filing catalyst rows so SEC forms do not look like news articles.

**Architecture:** `app/services/overview/market_interest.py` remains the Streamlit-free read-model owner and will expose separate `news_catalysts` and `sec_filing_catalysts` evidence sections. `app/web/overview/market_movers_helpers.py` will render those sections as two visible tables under the selected-symbol `시장 관심` panel, while source links remain a lower disclosure layer.

**Tech Stack:** Python, pandas, Streamlit, focused unittest contract tests in `tests/test_service_contracts.py`.

---

### Task 1: Contract Tests For Separate News And SEC Evidence

**Files:**
- Modify: `tests/test_service_contracts.py`

- [x] **Step 1: Write the failing tests**

Add service contract expectations that `build_market_interest_read_model` returns separate `news_catalysts` and `sec_filing_catalysts` sections, keeps Korean news in the news section, and labels Form 144 as a proposed sale notice rather than a news title.

- [x] **Step 2: Run the focused tests to verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_service_contracts.py -k 'market_interest' -q
```

Expected: fail because the current read model only returns `news_sec`.

### Task 2: Service Read Model Split

**Files:**
- Modify: `app/services/overview/market_interest.py`
- Test: `tests/test_service_contracts.py`

- [x] **Step 1: Implement minimal read-model split**

Create separate helpers for news rows and SEC filing rows. Keep `schema_version` compatible unless a test requires a visible version bump. Add conservative SEC form labels for common forms:

```text
144 -> SEC Form 144 · 제한/지배주식 매각 예정 통지
8-K -> SEC Form 8-K · 주요 이벤트 공시
10-Q -> SEC Form 10-Q · 분기 보고서
10-K -> SEC Form 10-K · 연간 보고서
4 -> SEC Form 4 · 내부자 거래 보고
```

Do not add scoring, recommendations, buy/sell signals, or article/filing body storage.

- [x] **Step 2: Run focused tests to verify GREEN**

Run:

```bash
.venv/bin/python -m pytest tests/test_service_contracts.py -k 'market_interest' -q
```

Expected: pass.

### Task 3: Streamlit Renderer Separation

**Files:**
- Modify: `app/web/overview/market_movers_helpers.py`
- Test: `tests/test_service_contracts.py`

- [x] **Step 1: Render two tables**

Replace the combined `뉴스/공시 촉매` table with:

```text
뉴스 리스트
SEC 공시 촉매
```

News table columns: `Region`, `Title`, `Source`, `Published At`, `Snippet`, `Open`.
SEC table columns: `Form`, `Title`, `Source`, `Published At`, `Open`.

- [x] **Step 2: Update renderer contract tests**

Assert that renderer source contains `뉴스 리스트`, `SEC 공시 촉매`, `news_catalysts`, and `sec_filing_catalysts`.

- [x] **Step 3: Run focused tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_service_contracts.py -k 'market_interest or market_movers_selected_investigation' -q
```

Expected: pass.

### Task 4: Docs, QA, And Commit

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/overview-market-interest-news-sec-split-20260709/*.md`
- Modify if needed: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

- [x] **Step 1: Update task and durable docs**

Record that the Market Interest panel now separates news evidence from SEC issuer filing clues, while 13F remains a delayed institutional context section.

- [x] **Step 2: Run verification**

Run:

```bash
.venv/bin/python -m py_compile app/services/overview/market_interest.py app/web/overview/market_movers_helpers.py
.venv/bin/python -m pytest tests/test_service_contracts.py -k 'market_interest or market_movers_selected_investigation' -q
git diff --check
```

- [x] **Step 3: Browser QA**

Run the Finance Streamlit app and capture one generated screenshot showing separate `뉴스 리스트` and `SEC 공시 촉매` sections. Do not commit the screenshot.

- [ ] **Step 4: Commit**

Stage only source, tests, and docs for this change. Do not stage generated PNGs or unrelated untracked research bundles. Commit with a Korean message.
