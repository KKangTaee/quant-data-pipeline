# Economic Cycle Current Transition Guidance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 현재 정식 월말 국면에서 다음에 확인할 인접 국면과 실제 조건 값을 전환 패널의 primary 판단 흐름으로 표시한다.

**Architecture:** 저장된 transition state machine은 유지하고 `app/services/overview/economic_cycle.py`가 snapshot/history를 DB-only로 읽어 `current_transition` presentation contract를 파생한다. React는 이 contract를 primary로 사용하고 기존 anchor/target은 secondary reference로만 표시한다.

**Tech Stack:** Python 3.12, pytest, React 19, TypeScript, Vitest, Vite, Streamlit custom component

## Global Constraints

- 미래 확률과 전환 시점을 만들지 않는다.
- `finance/economic_cycle_observed_state.py`의 state machine과 threshold를 변경하지 않는다.
- 자산별 확인 포인트와 Data Freshness layout/order를 변경하지 않는다.
- UI render path에서 provider fetch나 DB write를 실행하지 않는다.
- `MET`, `UNMET`, `UNAVAILABLE`은 각각 `충족`, `미충족`, `자료 부족`으로 표시한다.

---

### Task 1: Current Transition Read Model

**Files:**
- Modify: `app/services/overview/economic_cycle.py`
- Test: `tests/test_economic_cycle_service.py`

**Interfaces:**
- Consumes: persisted `observed_state_json`, `transition_monitor_json`, recent historical replay rows
- Produces: `transition_monitor.current_transition: {from_phase, from_phase_label, target_phase, target_phase_label, status, status_label, conditions_met, conditions_total, conditions}`

- [ ] **Step 1: Write the failing service test**

Add a literal snapshot/history fixture where observed phase is `contraction`, anchor is `recovery`, target is `expansion`, and `non_adjacent_observation=true`. Assert that `current_transition` is `contraction → recovery`, not `recovery → expansion`, and that the three condition labels contain literal current values and Korean thresholds.

- [ ] **Step 2: Run the test to verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_economic_cycle_service.py::test_non_adjacent_transition_builds_current_observation_guidance -q
```

Expected: FAIL because `current_transition` is absent.

- [ ] **Step 3: Implement the minimal read-model helper**

Add pure helpers that select the display path, find the previous observed row, choose level versus momentum by target phase, and build three normalized display conditions. Call the helper from `_transition_monitor` after normalizing the persisted monitor.

- [ ] **Step 4: Verify service GREEN and existing service regression**

Run:

```bash
.venv/bin/python -m pytest tests/test_economic_cycle_service.py -q
```

Expected: all tests pass.

- [ ] **Step 5: Commit the service contract**

```bash
git add app/services/overview/economic_cycle.py tests/test_economic_cycle_service.py
git commit -m "기능: 현재 관측 기준 전환 안내 추가"
```

### Task 2: Transition Panel Information Hierarchy

**Files:**
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/style.css`
- Test: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.test.tsx`
- Build output: `app/web/streamlit_components/economic_cycle_workbench/component_static/`

**Interfaces:**
- Consumes: `TransitionMonitor.current_transition` from Task 1, existing observed state, recent change rows, intramonth change
- Produces: primary current diagnosis summary, current path conditions, secondary anchor reference

- [ ] **Step 1: Write failing React behavior tests**

Extend the fixture with literal `current_transition` values. Assert the rendered panel contains `위축 → 회복 확인 조건`, `미충족`, actual value labels, and `이전 모델 기준 · 보조 정보`, while the primary condition heading does not contain `회복 → 확장 확인 조건`.

- [ ] **Step 2: Run Vitest to verify RED**

Run:

```bash
cd app/web/streamlit_components/economic_cycle_workbench
npm test -- --run
```

Expected: FAIL because the current panel still renders anchor-based conditions.

- [ ] **Step 3: Implement the approved panel**

Update TypeScript types and `TransitionPanel` to render four compact summary items, `current_transition` condition rows, an optional intramonth strip, and a secondary anchor reference only when it differs from the primary path. Pass `recent_changes` and `intramonth_change` into the panel.

- [ ] **Step 4: Add responsive styles**

Add focused classes for summary grid, condition rows, status tones, provisional strip, and secondary anchor. At 760px stack summary/condition content without changing asset card CSS.

- [ ] **Step 5: Verify React, TypeScript, and production build**

Run:

```bash
cd app/web/streamlit_components/economic_cycle_workbench
npm test -- --run
npx tsc --noEmit
npm run build
```

Expected: 12+ tests pass, TypeScript exits 0, Vite build exits 0.

- [ ] **Step 6: Commit the UI**

```bash
git add app/web/streamlit_components/economic_cycle_workbench/src app/web/streamlit_components/economic_cycle_workbench/component_static
git commit -m "UI: 경제사이클 현재 전환 판단 흐름 정리"
```

### Task 3: Integration QA And Documentation

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-current-transition-guidance-v1-20260810/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-current-transition-guidance-v1-20260810/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-current-transition-guidance-v1-20260810/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-current-transition-guidance-v1-20260810/RISKS.md`
- Inspect: `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md`
- Inspect: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`

**Interfaces:**
- Consumes: committed service/UI behavior
- Produces: verified task closeout and only change-triggered durable documentation

- [ ] **Step 1: Run focused Python regression**

```bash
.venv/bin/python -m pytest tests/test_economic_cycle_service.py tests/test_market_context_economic_cycle.py -q
```

- [ ] **Step 2: Verify actual DB read model**

Call `build_economic_cycle_read_model()` read-only and assert the actual current path is `contraction → recovery`, condition count is 0/3, and persisted anchor remains `recovery` as secondary evidence.

- [ ] **Step 3: Run Browser QA**

Inspect the local Economic Cycle page at desktop and 420px. Confirm primary current path/condition values, secondary anchor, unchanged asset cards, no horizontal overflow, and console error/warning 0.

- [ ] **Step 4: Sync task and durable docs**

Record RED/GREEN commands, actual payload, Browser QA, and remaining limitations. Update canonical docs only if product promise, ownership boundary, roadmap state, or durable data meaning changed.

- [ ] **Step 5: Final verification and commit**

```bash
git diff --check
git status --short
git add .aiworkspace/note/finance/tasks/active/economic-cycle-current-transition-guidance-v1-20260810
git commit -m "문서: 경제사이클 현재 전환 UI 검증 정리"
```
