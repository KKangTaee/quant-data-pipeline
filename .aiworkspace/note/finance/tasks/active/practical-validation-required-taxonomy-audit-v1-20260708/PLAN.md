# Practical Validation Required Taxonomy Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Practical Validation의 1차 필수 검증을 중복 없는 owner-based taxonomy로 재정의하기 위한 audit / design 기준을 만든다.

**Architecture:** 이번 task는 코드 변경 전 설계 산출물이다. 현재 module planner, audit services, Flow 4 category read model을 조사해 `check_id -> owner_module` 기준을 고정하고, 다음 task에서 service / gate / UI 리팩터링을 실행한다.

**Tech Stack:** Python service modules, Streamlit Practical Validation UI, `.aiworkspace` finance task docs, focused unittest contract tests.

---

## 이걸 하는 이유?

현재 `validation_efficacy`가 source contract, latest replay, benchmark parity, provider freshness, PIT, survivorship, robustness를 다시 읽고 있다. 이 때문에 사용자는 같은 문제가 여러 모듈에서 반복되는 것처럼 보고, 개발 측면에서는 gate가 어느 모듈의 실패를 기준으로 차단되는지 흐려진다.

목표는 `검증 항목 1개 = 소유 모듈 1개` 원칙으로 1차 필수 검증을 다시 구성하는 것이다.

## Scope

- 포함:
  - 현재 Practical Validation required / conditional module inventory 정리.
  - audit row별 중복 소유권 판정.
  - 새 1차 필수 검증 taxonomy / owner matrix 정의.
  - 다음 코드 리팩터링 단계별 계획 작성.
- 제외:
  - 이번 task에서 Python service code 변경.
  - gate threshold 변경.
  - registry / saved JSONL rewrite.
  - provider ingestion 실행.
  - Streamlit / React UI 변경.

## Tentative Roadmap

1. 1차: 현재 검증 row inventory와 owner matrix 문서화. 이 task.
2. 2차: service taxonomy registry 추가 및 `validation_efficacy` 중복 row 제거 테스트 작성.
3. 3차: module planner / board registry / workspace category가 새 owner matrix를 읽도록 리팩터링.
4. 4차: Flow 3 / Flow 4 표시 문구를 새 taxonomy에 맞춰 정리.
5. 5차: Final Review selected-route gate policy 회귀 테스트 보강.
6. 6차: Browser QA, durable docs sync, commit closeout.

## Task 1: Current Inventory

**Files:**
- Read: `app/services/backtest_practical_validation_modules.py`
- Read: `app/services/backtest_validation_efficacy.py`
- Read: `app/services/backtest_data_coverage_audit.py`
- Read: `app/services/backtest_realism_audit.py`
- Read: `app/services/backtest_construction_risk_audit.py`
- Read: `app/services/backtest_risk_contribution_audit.py`
- Read: `app/services/backtest_component_role_weight_audit.py`
- Write: `DESIGN.md`

- [x] List existing required modules and the rows they consume.
- [x] Mark duplicated rows and current owner conflicts.
- [x] Identify conditional / reference rows that should not be universal hard blockers.

## Task 2: New Owner Matrix

**Files:**
- Write: `DESIGN.md`
- Write: `NOTES.md`
- Write: `RISKS.md`

- [x] Define new required module groups.
- [x] Assign each check to one owner module.
- [x] Define dependency behavior for checks that need upstream evidence.
- [x] Separate validation module, conditional evidence, downstream reference, and Final Review handoff preview.

## Task 3: Implementation Handoff

**Files:**
- Write: `STATUS.md`
- Write: `RUNS.md`
- Update: `.aiworkspace/note/finance/tasks/active/README.md`
- Update: `.aiworkspace/note/finance/tasks/active/STATUS_MANIFEST.md`
- Update: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Update: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

- [x] Record completed audit result and next code task.
- [x] Run documentation verification commands.
- [x] Commit this task as a coherent design/audit unit.
