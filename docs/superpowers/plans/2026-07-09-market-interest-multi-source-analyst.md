# Market Interest Multi-Source Analyst Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade Overview > Market Movers > 시장 관심 > 애널리스트 관심 from link-only guidance into a selected-symbol, button-triggered, session-only analyst evidence panel.

**Architecture:** Keep the service read model in `app/services/overview/market_interest.py` and the Streamlit renderer in `app/web/overview/market_movers_helpers.py`. Use yfinance as the first structured personal-research source, while Nasdaq / WSJ / Yahoo / MarketWatch remain source-attributed cross-check cards and original links unless explicit licensed/API access is approved.

**Tech Stack:** Python 3.12, pandas, yfinance, Streamlit, unittest service-contract tests.

---

### Task 1: Plan And Task Record

**Files:**
- Create: `.aiworkspace/note/finance/tasks/active/overview-market-interest-analyst-multisource-20260709/PLAN.md`
- Create: `.aiworkspace/note/finance/tasks/active/overview-market-interest-analyst-multisource-20260709/STATUS.md`
- Create: `.aiworkspace/note/finance/tasks/active/overview-market-interest-analyst-multisource-20260709/RUNS.md`
- Create: `.aiworkspace/note/finance/tasks/active/overview-market-interest-analyst-multisource-20260709/RISKS.md`

- [ ] **Step 1: Record scope**

Write task docs that state: selected symbol only, explicit button only, no DB schema change, no article/report body storage, no score/recommendation, yfinance structured source first, Nasdaq/WSJ/MarketWatch cross-check links first.

### Task 2: Analyst Evidence Service Contract

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/services/overview/market_interest.py`

- [ ] **Step 1: Write failing test for yfinance normalization**

Add a test that injects fake yfinance-like data and expects:
- `fetch_yfinance_analyst_interest_metadata("AAPL")` returns action rows with firm, action, from/to grade, target change, prior/current target, and Yahoo source URL.
- target and recommendation rows are normalized.
- no durable body text is stored.

- [ ] **Step 2: Run focused test and confirm RED**

Run:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_interest_fetches_yfinance_analyst_metadata_with_session_only_rows
```

Expected: failure because the fetch/normalization function does not exist yet.

- [ ] **Step 3: Implement minimal service**

Add `fetch_yfinance_analyst_interest_metadata`, helpers for numeric/date formatting, and source links for Yahoo Finance, MarketWatch, WSJ Markets, and Nasdaq Analyst Research.

- [ ] **Step 4: Run focused test and confirm GREEN**

Run the same focused unittest. Expected: pass.

### Task 3: Read Model Integration

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/services/overview/market_interest.py`

- [ ] **Step 1: Write failing test for market-interest read model**

Add a test where metadata contains `analyst_interest` rows and expects:
- summary `analyst_interest.state` is `애널리스트 2건`.
- analyst section `provider_status` is `SESSION_READY`.
- source comparison rows include Yahoo, MarketWatch, WSJ Markets, Nasdaq.
- boundary text still avoids scores and buy/sell signal wording.

- [ ] **Step 2: Run focused test and confirm RED**

Run:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_interest_read_model_embeds_structured_analyst_rows_and_source_cards
```

Expected: failure because the read model still marks analyst source disconnected.

- [ ] **Step 3: Integrate metadata into read model**

Update analyst summary and section rows while preserving existing news / SEC / 13F behavior.

- [ ] **Step 4: Run focused test and confirm GREEN**

Run the same focused unittest. Expected: pass.

### Task 4: UI Rendering

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/web/overview/market_movers_helpers.py`

- [ ] **Step 1: Write failing UI source contract test**

Assert the renderer includes analyst action table labels, target summary, recommendation distribution, multi-source cross-check, and no longer renders the FMP/Finnhub-only disconnected info as the main analyst state.

- [ ] **Step 2: Run focused test and confirm RED**

Run:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_interest_renderer_shows_structured_analyst_evidence_and_source_cards
```

Expected: failure because the renderer still shows disconnected-only analyst copy.

- [ ] **Step 3: Render analyst rows**

Render analyst action rows, target rows, recommendation distribution, and source comparison rows under `애널리스트 관심`.

- [ ] **Step 4: Run focused test and confirm GREEN**

Run the same focused unittest. Expected: pass.

### Task 5: Button Flow Integration

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/web/overview/market_movers_helpers.py`

- [ ] **Step 1: Write failing source contract test**

Assert `_fetch_market_mover_market_interest_metadata` calls `fetch_yfinance_analyst_interest_metadata` and stores the result inside the selected-symbol market-interest session model.

- [ ] **Step 2: Run focused test and confirm RED**

Run:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_mover_market_interest_fetch_includes_yfinance_analyst_metadata
```

Expected: failure because the button flow only fetches news and SEC metadata.

- [ ] **Step 3: Wire button flow**

Call yfinance analyst metadata fetch inside the existing `시장 관심 근거 확인` path and merge it into metadata as `analyst_interest`.

- [ ] **Step 4: Run focused test and confirm GREEN**

Run the same focused unittest. Expected: pass.

### Task 6: Verification And Commit

**Files:**
- Modify: active task docs
- Modify: root handoff logs only if durable milestone needs handoff

- [ ] **Step 1: Run verification**

Run:

```bash
.venv/bin/python -m py_compile app/services/overview/market_interest.py app/web/overview/market_movers_helpers.py
.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests
git diff --check
```

- [ ] **Step 2: Browser QA**

Start or reuse the Streamlit app, open Overview > Market Movers, select a symbol, click `시장 관심 근거 확인`, and capture one screenshot outside tracked files.

- [ ] **Step 3: Doc sync**

Update the task `STATUS.md`, `RUNS.md`, `RISKS.md`, and concise root logs if needed.

- [ ] **Step 4: Commit**

Stage only code, tests, task docs, and this plan. Do not stage QA screenshots or generated artifacts.

Commit:

```bash
git commit -m "Market Movers 애널리스트 관심 구조화 단서 추가"
```

---

## Self-Review

- Spec coverage: selected-symbol button flow, yfinance structured source, multi-source cross-check cards, no DB storage, no recommendation/score, focused QA, and commit are covered.
- Placeholder scan: no TBD/TODO placeholders remain.
- Type consistency: metadata key is `analyst_interest`; read model section id remains `analyst_interest`; UI renderer consumes the same section fields.
