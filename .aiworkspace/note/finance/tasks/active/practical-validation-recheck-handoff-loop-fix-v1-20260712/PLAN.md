# Practical Validation Recheck Handoff Loop Fix V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Subagent dispatch is disabled for this workspace session. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 데이터 보강 후 새 Flow 2 재검증과 validation 저장을 거치지 않고 기존 Final Review 검토서로 되돌아가는 반복을 차단한다.

**Architecture:** 두 provider collection UI 경로를 하나의 Streamlit completion helper로 합쳐 replay state를 강제로 초기화한다. Final Review는 append-only registry에서 source별 최신 validation만 사용하고, save-and-move session handoff가 새 validation stable key를 선택·확정한다.

**Tech Stack:** Python 3.12, Streamlit, unittest, append-only JSONL registry, React presentation component.

## Global Constraints

- Final Review는 live approval, broker order, account sync, auto rebalance가 아니다.
- provider fetch, replay, Gate, 저장은 Python service/page boundary가 소유한다.
- React는 presentation과 intent만 담당한다.
- 기존 registry / saved JSONL row는 재작성하거나 삭제하지 않는다.
- run history와 generated QA artifact는 stage하거나 commit하지 않는다.

---

### Task 1: 수집 후 replay 강제 초기화

**Files:**
- Modify: `app/web/backtest_practical_validation/page.py`
- Test: `tests/test_service_contracts.py`

**Interfaces:**
- Produces: `_complete_provider_gap_collection(validation_result: dict[str, Any], results: list[dict[str, Any]], *, origin: str) -> None`
- Preserves: `run_provider_gap_collection(validation_result)` as the only provider execution boundary.

- [x] Write a failing test that patches Streamlit session state and proves both collection entry paths call one completion helper which clears `practical_validation_recheck_<source>_*` keys.
- [x] Run the focused test and confirm it fails because the Final Review handoff path leaves replay state intact.
- [x] Implement the shared completion helper and route both buttons through it.
- [x] Run Practical Validation and BacktestRuntime focused tests.
- [x] Commit with `Practical Validation 수집 후 재검증을 강제`.

### Task 2: Level2 완료 순서와 저장 방어

**Files:**
- Modify: `app/services/backtest_practical_validation_workspace.py`
- Modify: `app/web/backtest_practical_validation/page.py`
- Test: `tests/test_service_contracts.py`

**Interfaces:**
- Produces: `build_practical_validation_recovery_progress(*, collection_completed: bool, replay_completed: bool, can_save_and_move: bool, blocking: bool) -> dict[str, Any]`
- Consumes: provider collection session marker, current replay result, `final_review_gate`.

- [x] Write failing service tests for collected/recheck-pending, replay-blocked, and save-ready states.
- [x] Run tests and confirm the progress contract is absent.
- [x] Implement the pure progress read model and compact Level2 action sequence.
- [x] Add a page-level defense that refuses save-and-move without current replay evidence.
- [x] Run focused tests, py_compile, and `git diff --check`.
- [x] Commit with `Practical Validation 보강 완료 순서를 명확화`.

### Task 3: 새 validation 자동 연결과 구형 row 분리

**Files:**
- Modify: `app/web/backtest_final_review_helpers.py`
- Modify: `app/web/backtest_final_review/page.py`
- Modify: `app/web/backtest_practical_validation/page.py`
- Test: `tests/test_service_contracts.py`

**Interfaces:**
- Produces: `_latest_practical_validation_rows_by_source(rows: list[dict[str, Any]]) -> list[dict[str, Any]]`
- Produces stable selected key: `practical_validation_result:<validation_id>`.

- [x] Write failing tests proving latest row wins per `selection_source_id` and a latest blocked row prevents fallback to an older eligible row.
- [x] Write a failing handoff test proving save-and-move sets the new validation selector and confirmed key.
- [x] Implement latest-row selection before eligibility filtering.
- [x] Set new stable key in Final Review session state after successful save-and-move.
- [x] Run Final Review / Practical Validation / BacktestRuntime focused tests.
- [x] Commit with `Final Review를 최신 재검증 결과로 연결`.

### Task 4: Browser QA와 문서 closeout

**Files:**
- Modify task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Modify: `.aiworkspace/note/finance/tasks/active/README.md`
- Modify: `.aiworkspace/note/finance/tasks/active/STATUS_MANIFEST.md`

- [x] Run focused service / contract tests.
- [x] Run React production build.
- [x] Run target Python `py_compile` and `git diff --check`.
- [x] Browser QA the exact legacy recovery -> collection -> replay -> save -> new Final Review path without executing a real provider collection unless the existing local state safely permits it. 실제 provider 수집은 실행하지 않았고 custom component rerun 자동화 한계는 RISKS에 남겼다.
- [x] Verify compact viewport has no horizontal overflow and save remains disabled before replay.
- [x] Keep registry / saved / run history / screenshots unstaged.
- [x] Sync durable docs and commit with `Practical Validation 재검증 handoff QA와 문서 동기화`.
