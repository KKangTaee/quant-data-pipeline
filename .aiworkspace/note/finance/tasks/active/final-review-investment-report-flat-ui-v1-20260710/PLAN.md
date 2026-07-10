# Final Review Investment Report Flat UI V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Final Review 투자 검토서를 박스 중첩형 카드 화면이 아니라 한 장의 판단서처럼 읽히는 flat decision surface로 정리한다.

**Architecture:** Python `backtest_evidence_read_model` remains the owner of scoring, gate policy, route decision, save guidance, and handoff payloads. React `final_review_investment_report` only reshapes the existing report payload into a flatter first-read layout and keeps lower evidence behind detail sections. No registry, saved JSONL, provider fetch, score, gate, or persistence behavior changes.

**Tech Stack:** Python unittest source contracts, React / TypeScript Streamlit component, CSS, Vite build, Streamlit Browser QA.

---

## 이걸 하는 이유?

현재 투자 검토서는 Streamlit section 안에 React report box가 있고, 그 안에 다시 cards / grids / bordered panels가 반복된다. 사용자는 Monitoring 후보 여부, 왜 후보인지, 무엇을 확인해야 하는지보다 박스 구조와 technical badge를 먼저 보게 된다. 이번 작업은 상용 투자 앱에서 흔한 scan-first 구조처럼 first-read는 판단, lower-read는 근거 검산으로 분리한다.

## Scope

- React component layout flattening
- CSS card nesting cleanup
- First-read meta strip / decision brief / evidence rows
- Scorecard, Level2, handoff, improvement, review disposition detail disclosure
- Focused source contract tests, React build, py_compile, Browser QA

## Out Of Scope

- Python score / gate / route / handoff calculation changes
- Final Review save behavior changes
- Registry / saved JSONL / run history writes
- Provider / DB fetch changes
- Live approval, broker order, account sync, auto rebalance

### Task 1: RED UI Structure Contract

**Files:**
- Modify: `tests/test_service_contracts.py`

- [x] Add failing source contract tests requiring `meta-strip`, `decision-brief`, row-based evidence, and detail disclosure classes.
- [x] Require old first-read card-grid classes to be absent from the React source and build source.
- [x] Run focused unittest and confirm it fails before React/CSS changes.

### Task 2: React Flat Report Structure

**Files:**
- Modify: `app/web/components/final_review_investment_report/frontend/src/FinalReviewInvestmentReport.tsx`

- [x] Replace fact cards with a compact meta strip.
- [x] Replace decision summary card grid with two-column decision brief.
- [x] Replace strength / watch card lists with capped evidence rows.
- [x] Move scorecard, Level2, handoff, improvement, and review disposition into lower detail disclosures.

### Task 3: CSS Flat Visual System

**Files:**
- Modify: `app/web/components/final_review_investment_report/frontend/src/style.css`

- [x] Remove nested card/panel visual grammar from the first-read report.
- [x] Use a single report accent, flat separators, row lines, chips, and compact details.
- [x] Preserve responsive one-column behavior on small screens.
- [x] Run `npm run build` and focused source contract tests.

### Task 4: QA / Docs / Commit

**Files:**
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Update task `STATUS.md` / `RUNS.md`

- [x] Run focused Python tests, py_compile, npm build, and diff check.
- [x] Run Browser QA and capture one generated screenshot without committing it.
- [x] Stage only source / docs / task records / built component assets.
- [x] Commit with a coherent Korean message.
