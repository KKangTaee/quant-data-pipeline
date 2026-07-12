# Final Review Investment Report IA V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Final Review `투자 검토서`를 중복 안내가 아니라 monitoring 후보 판단, 선택 이유, 강점 / 확인 지점, 실제 해석 중심으로 읽히게 한다.

**Architecture:** Python `backtest_evidence_read_model` keeps all judgment, scoring, and report payload generation. React `final_review_investment_report` remains presentation-only and reorganizes existing / enriched payload into a clearer first-read layout. Registry, saved JSONL, run history, provider fetch, persistence, live approval, order, and auto rebalance boundaries do not change.

**Tech Stack:** Python service contract tests, React / TypeScript Streamlit component, Vite build, Streamlit Browser QA.

---

### Task 1: RED Contract

**Files:**
- Modify: `tests/test_service_contracts.py`

- [x] Add failing service contract tests that require a consolidated `decision_summary`, concrete strength rows, filtered interpretation cards, and React source structure that does not expose the old `다음 행동` / `판단 저장 전 메모` first-read blocks.
- [x] Run the focused tests and confirm they fail for missing payload / old React labels.

### Task 2: Read Model Enrichment

**Files:**
- Modify: `app/services/backtest_evidence_read_model.py`

- [x] Add helper payloads derived from existing scorecard, gate policy, strengths, weaknesses, and monitoring conditions only.
- [x] Keep score / gate / save / handoff semantics unchanged.
- [x] Run the focused service tests and confirm they pass.

### Task 3: React IA

**Files:**
- Modify: `app/web/components/final_review_investment_report/frontend/src/FinalReviewInvestmentReport.tsx`
- Modify: `app/web/components/final_review_investment_report/frontend/src/style.css`

- [x] Replace the old top summary / selection rationale / required memo duplication with a hero, decision-summary grid, compact strength / watch layout, and actual interpretation cards.
- [x] Remove first-read guide cards when the service does not provide actual interpreted content.
- [x] Run `npm run build`.

### Task 4: QA / Docs / Commit

**Files:**
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Update task `STATUS.md` / `RUNS.md`

- [x] Run focused Python tests, py_compile, npm build, and diff check.
- [x] Run Browser QA and capture one generated screenshot without committing it.
- [x] Stage only source / docs / task records, not generated QA images or run history.
- [x] Commit with a coherent Korean message.
