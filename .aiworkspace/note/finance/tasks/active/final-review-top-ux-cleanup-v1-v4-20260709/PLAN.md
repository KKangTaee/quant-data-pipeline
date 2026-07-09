# Final Review Top UX Cleanup V1-V4 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Final Review 상단을 안내 문구 중심에서 후보 현황, 선택 가능성, 다음 행동 중심으로 정리하고 sentiment timing 검토는 별도 리서치 경계로 분리한다.

**Architecture:** Python service/read-model boundary는 유지하고, Final Review Streamlit page는 이미 계산된 candidate board, validation, sentiment overlay payload를 표시만 한다. React investment report는 변경하지 않고, 새 provider fetch / DB write / registry rewrite / saved setup write는 추가하지 않는다.

**Tech Stack:** Python Streamlit UI, existing service contract tests in `tests/test_service_contracts.py`, finance task docs.

---

## 이걸 하는 이유?

현재 Final Review 상단은 caption, Reference help, Decision Desk 설명, 1~5 flow card, market sentiment overlay가 같은 역할의 안내를 반복한다. 사용자가 실제로 끝내야 하는 일은 `Practical Validation Gate를 통과한 후보 중 무엇을 모니터링 후보로 저장할지 판단`하는 것인데, 첫 화면이 가이드/진단 중심으로 보여 판단 대상과 다음 행동이 흐려진다.

## 전체 범위

- 1차: Final Review 상단 안내 축소와 top summary contract 추가.
- 2차: `모니터링 후보 선별` command center를 후보 현황 / 사용 가능성 / hidden reason 중심으로 재작성하고 1~5 flow card 제거.
- 3차: 시장심리 overlay를 compact context로 낮추고 상세 evidence는 접힌 detail로 유지.
- 4차: sentiment timing / rebalance 활용은 구현하지 않고 별도 리서치 후보와 제품 경계로 문서화.

## 유지할 경계

- Final Review는 live approval, broker order, auto rebalance가 아니다.
- Sentiment는 context-only이며 selected-route gate, Candidate Board priority, 저장 가능 여부, Portfolio Monitoring signal에 영향을 주지 않는다.
- React investment report는 presentation-only 경계를 유지한다.
- `.aiworkspace/note/finance/registries/`, `.aiworkspace/note/finance/saved/`, run history, generated QA artifact는 stage하지 않는다.

## 1차 - 상단 안내 축소

**Files:**
- Modify: `app/web/backtest_final_review/page.py`
- Modify: `tests/test_service_contracts.py`
- Create/update: task `STATUS.md`, `RUNS.md`, `NOTES.md`, `RISKS.md`

- [x] **Step 1: Write failing test**
  - Add a test that requires a Streamlit-free top summary model with short purpose copy, destination, and excluded long guide copy.
- [x] **Step 2: Verify RED**
  - Run the focused test and confirm it fails because the helper does not exist.
- [x] **Step 3: Implement minimal helper and render usage**
  - Add `_build_final_review_top_summary(...)` and replace the long top caption with concise text.
- [x] **Step 4: QA**
  - Run focused test, py_compile, diff check.
- [x] **Step 5: Commit**
  - Commit only tracked code/task-doc files for 1차.

## 2차 - 후보선별 command center 재구성

**Files:**
- Modify: `app/web/backtest_final_review/page.py`
- Modify: `tests/test_service_contracts.py`
- Update: task docs

- [x] **Step 1: Write failing test**
  - Require command center copy/model to expose available candidate count, hidden count, saved selection count, dashboard count, and no 1~5 card guide.
- [x] **Step 2: Verify RED**
  - Run the focused test and confirm missing helper/output.
- [x] **Step 3: Implement minimal command summary and remove flow card render**
  - Add `_build_final_review_decision_desk_model(...)`.
  - Use the model in `render_fr_command_center`.
  - Remove `render_fr_flow([...])` from top-level Final Review render.
- [x] **Step 4: QA**
  - Run focused test, py_compile, diff check.
- [x] **Step 5: Commit**
  - Commit 2차 code/task-doc changes.

## 3차 - 시장심리 compact context

**Files:**
- Modify: `app/web/backtest_final_review/page.py`
- Modify: `tests/test_service_contracts.py`
- Update: task docs

- [x] **Step 1: Write failing test**
  - Require Final Review sentiment display model to be compact, context-only, and to route detailed sentiment review to Overview Sentiment.
- [x] **Step 2: Verify RED**
  - Run the focused test and confirm missing helper/output.
- [x] **Step 3: Implement compact overlay**
  - Add `_build_final_review_sentiment_display_model(...)`.
  - Change `_render_market_sentiment_context_overlay()` to render one compact panel and keep evidence rows collapsed.
- [x] **Step 4: QA**
  - Run focused test, existing sentiment context tests, py_compile, diff check.
- [x] **Step 5: Commit**
  - Commit 3차 code/task-doc changes.

## 4차 - timing / rebalance 리서치 경계 문서화

**Files:**
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Update: task docs

- [x] **Step 1: Write failing documentation drift test**
  - Add a source/doc contract assertion that Final Review sentiment timing remains research-only and context-only.
- [x] **Step 2: Verify RED**
  - Run focused test and confirm the doc text is missing.
- [x] **Step 3: Update smallest durable docs**
  - Document that Final Review shows compact sentiment context only.
  - Document that timing/rebalance use requires separate research with look-ahead-safe validation.
- [x] **Step 4: QA**
  - Run focused docs/source test, py_compile, `git diff --check`, and relevant finance doc listing.
- [x] **Step 5: Commit**
  - Commit 4차 docs/task changes.

## Final QA

- Run focused Final Review service tests.
- Run React investment report contract test.
- Run `py_compile` for changed Python files.
- Run `git diff --check`.
- Run Browser QA because Final Review UI layout changed.
- Leave generated QA screenshot untracked.
