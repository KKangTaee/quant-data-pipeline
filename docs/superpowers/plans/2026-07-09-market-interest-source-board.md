# Market Interest Analyst Source Board Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans when continuing this plan. Track each checkbox as work is completed.

**Goal:** Make Overview > Market Movers > 시장 관심 > 애널리스트 관심 clearly show which analyst sources are structured session metadata and which are external original-page cross-checks.

**Architecture:** Keep selected-symbol-only investigation in `app/services/overview/market_interest.py` and rendering in `app/web/overview/market_movers_helpers.py`. Do not add crawlers, DB storage, scoring, or recommendation signals in this pass.

**Tech Stack:** Python, pandas, Streamlit, unittest service-contract tests.

---

### Task 1: Task Record

**Files:**
- Create: `.aiworkspace/note/finance/tasks/active/overview-market-interest-source-board-20260709/PLAN.md`
- Create: `.aiworkspace/note/finance/tasks/active/overview-market-interest-source-board-20260709/STATUS.md`
- Create: `.aiworkspace/note/finance/tasks/active/overview-market-interest-source-board-20260709/RUNS.md`
- Create: `.aiworkspace/note/finance/tasks/active/overview-market-interest-source-board-20260709/RISKS.md`

- [x] Record the accepted scope: visible source-status board, no new automatic scraping, selected symbol only, explicit button only.

### Task 2: Read Model Source Cards

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/services/overview/market_interest.py`

- [x] Add a failing contract test that expects analyst `source_cards` for Yahoo/yfinance, MarketWatch, WSJ, and Nasdaq.
- [x] Implement source-card construction with conservative statuses: `구조화 조회됨`, `구조화 단서 없음`, `조회 실패`, and `원문 교차확인`.
- [x] Run the focused service-contract test until it passes.

### Task 3: Streamlit Source Board

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/web/overview/market_movers_helpers.py`

- [x] Add a failing renderer contract test that expects a visible `출처별 확인 상태` board and no `공개 페이지 교차확인` expander as the primary UI.
- [x] Render analyst source cards above action/target/distribution tables.
- [x] Keep full source disclosure available without presenting it as the main analyst evidence.
- [x] Run the focused renderer test until it passes.

### Task 4: Verification And Commit

**Files:**
- Update task docs and root handoff logs if needed.

- [x] Run `py_compile`, focused service-contract tests, and `git diff --check`.
- [x] Run Browser QA and capture one screenshot outside tracked files.
- [x] Stage only code, tests, task docs, plan docs, and handoff logs.
- [x] Commit with a coherent Korean message.
