# Economic Cycle Display Window Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 경제사이클 계산과 저장 데이터는 유지하고 Cycle Map을 최근 12개월, Regime Ribbon을 최근 60개월로 단순화한다.

**Architecture:** Overview service가 화면용 history를 최대 60개월로 제한하고 React가 그중 최근 12개월만 Cycle Map에 사용한다. Forecast horizon과 상태 계약은 변경하지 않는다.

**Tech Stack:** Python 3, pytest, React 18, TypeScript, Vite, Streamlit component.

## Global Constraints

- DB snapshot, artifact, replay history를 삭제하거나 다시 계산하지 않는다.
- 현재/+1M/+2M forecast와 `VERIFIED | PROVISIONAL | UNAVAILABLE` 계약을 유지한다.
- 결측 월과 결측 horizon 사이에는 경로를 연결하지 않는다.
- desktop과 420px에서 가로 overflow가 없어야 한다.

---

### Task 1: Reduce service and chart windows

**Files:**
- Modify: `tests/test_economic_cycle_service.py`
- Modify: `tests/test_market_context_economic_cycle.py`
- Modify: `app/services/overview/economic_cycle.py`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`

**Interfaces:**
- Consumes: persisted economic-cycle history rows
- Produces: 최대 60개 history row와 최근 12개월 Cycle Map

- [ ] **Step 1: Write failing tests**

Service test는 140개 row 입력에서 60개만 반환하는지 검증한다. React source contract는 `payload.history.slice(-12)`, `실선은 최근 12개월`, `최근 5년 + 2개월 전망`을 요구한다.

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
uv run --with pytest python -m pytest tests/test_economic_cycle_service.py -k truncates -q
uv run --with pytest python -m pytest tests/test_market_context_economic_cycle.py -k component -q
```

Expected: 기존 121개월/18개월 계약 때문에 실패한다.

- [ ] **Step 3: Implement minimal changes**

`_history()`는 정렬된 row의 마지막 60개를 반환한다. DB history 조회 시작일은 종료일 기준 59개월 전으로 변경한다. `QuadrantChart`는 `payload.history.slice(-12)`를 사용하고 section copy와 ribbon copy를 새 기간에 맞춘다.

- [ ] **Step 4: Run focused tests and build**

Run:

```bash
uv run --with pytest python -m pytest tests/test_economic_cycle_service.py tests/test_market_context_economic_cycle.py tests/test_market_context_valuation.py -q
npm run build
```

Expected: all tests pass and Vite exits 0.

### Task 2: QA and documentation closeout

**Files:**
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/data/TABLE_SEMANTICS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-market-context-economic-cycle-provisional-hybrid-v2-20260716/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-market-context-economic-cycle-provisional-hybrid-v2-20260716/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-market-context-economic-cycle-provisional-hybrid-v2-20260716/STATUS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

**Interfaces:**
- Consumes: completed display-window implementation
- Produces: durable 12/60-month documentation and QA evidence

- [ ] **Step 1: Run Browser QA**

At `http://localhost:8502/`, verify the 12-month/5-year copy, visible forecast path, ribbon cell count 62, no browser error, and 420px horizontal overflow <= 1px.

- [ ] **Step 2: Synchronize documentation**

Replace user-facing 121-month ribbon/read-model descriptions with 60-month display descriptions while explicitly preserving full DB history and model artifacts.

- [ ] **Step 3: Run final verification**

Run:

```bash
uv run --with pytest python -m pytest tests/test_economic_cycle_features.py tests/test_economic_cycle_labels.py tests/test_economic_cycle_model.py tests/test_economic_cycle_pipeline.py tests/test_economic_cycle_results.py tests/test_economic_cycle_service.py tests/test_economic_cycle_validation.py tests/test_economic_cycle_vintages.py tests/test_market_context_economic_cycle.py tests/test_market_context_valuation.py -q
.venv/bin/python -m py_compile app/services/overview/economic_cycle.py
git diff --check
```

Expected: tests pass, compile exits 0, and diff check exits 0.

- [ ] **Step 4: Commit**

Stage only scoped code, built component, test, plan, and finance documentation files. Preserve unrelated untracked research and `.superpowers/`.
