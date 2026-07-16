# U.S. Economic Cycle Provisional Hybrid Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 검증 기준을 유지하면서 계산 가능한 LIMITED 결과를 잠정 추정으로 공개하고 경제사이클 화면을 승인된 2×2 혼합형으로 교체한다.

**Architecture:** Pipeline은 artifact가 존재하는 모든 horizon의 확률을 계산·저장하고 publication status는 별도로 보존한다. Overview service는 확률 유효성과 publication status로 `PROVISIONAL | VERIFIED | UNAVAILABLE`를 만들며, React는 이 계약으로 horizon 카드, 2×2 경로, ribbon을 그린다.

**Tech Stack:** Python 3, pandas, MySQL compact snapshot, pytest, React 18, TypeScript, Vite, Streamlit component.

## Global Constraints

- Point-in-time vintage와 rolling-origin validation threshold를 변경하지 않는다.
- UI는 DB-only read model이며 provider/model/persistence action을 만들지 않는다.
- NBER 공식 판정, 수익률 예측, 매매 지시로 표현하지 않는다.
- 기존 Market Context valuation mode와 responsive contract를 보존한다.

---

### Task 1: Persist provisional probabilities

**Files:**
- Modify: `tests/test_economic_cycle_pipeline.py`
- Modify: `finance/economic_cycle_pipeline.py`

**Interfaces:**
- Consumes: `HorizonModelArtifact`, `_predict_horizon(...)`
- Produces: LIMITED horizon에도 유효한 `HorizonProbability.probabilities`, `dominant_phase`, `confidence`

- [ ] **Step 1: Write the failing test**

`test_materialization_persists_provisional_probabilities_for_limited_horizons`에서 h1/h2 `LIMITED` artifact가 확률과 dominant phase를 보존하고 publication status만 `LIMITED`인지 검증한다.

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_pipeline.py -k provisional -q`

Expected: LIMITED horizon probabilities are `None`.

- [ ] **Step 3: Write minimal implementation**

`materialize_economic_cycle_snapshot`은 artifact가 없을 때만 확률을 비우고, artifact가 있으면 status와 무관하게 `_predict_horizon`을 실행한다. h0 provisional dominant phase도 h1/h2 transition prior에 사용한다.

- [ ] **Step 4: Run focused tests**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_pipeline.py tests/test_economic_cycle_results.py -q`

Expected: all pass.

### Task 2: Expose three-state read model

**Files:**
- Modify: `tests/test_economic_cycle_service.py`
- Modify: `app/services/overview/economic_cycle.py`

**Interfaces:**
- Consumes: persisted probabilities and `publication_status`
- Produces: horizon/history `estimate_status`, readable verification labels, provisional paths

- [ ] **Step 1: Write failing service tests**

Add assertions that valid LIMITED probabilities become `PROVISIONAL`, READY probabilities become `VERIFIED`, and missing/invalid probabilities become `UNAVAILABLE`.

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_service.py -k 'provisional or unavailable or ready' -q`

Expected: missing `estimate_status` or hidden LIMITED probabilities.

- [ ] **Step 3: Implement minimal service mapping**

Parse valid probabilities regardless of publication status. Derive:

```python
estimate_status = (
    "VERIFIED" if status == "READY"
    else "PROVISIONAL" if probabilities is not None
    else "UNAVAILABLE"
)
```

History uses the same rule. Headline uses the dominant phase for provisional current results.

- [ ] **Step 4: Run service tests**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_service.py -q`

Expected: all pass.

### Task 3: Replace circular clock with hybrid quadrant

**Files:**
- Modify: `tests/test_market_context_economic_cycle.py`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/style.css`

**Interfaces:**
- Consumes: horizon/history probabilities and `estimate_status`
- Produces: horizon badges, 2×2 probability coordinates, observed solid path, forecast dotted path, provisional hatch

- [ ] **Step 1: Write failing source contract tests**

Require `estimate_status`, `cycle-quadrant`, `observed-path`, `forecast-path`, `잠정 모델 추정`, `검증된 모델 추정`, and remove the circular `clock-ring` contract.

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_market_context_economic_cycle.py -k 'component' -q`

Expected: hybrid quadrant tokens missing.

- [ ] **Step 3: Implement the React view**

Add `probabilityCoordinate`, `QuadrantChart`, three-state horizon cards, and provisional/verified badges. Keep evidence, conditional market context, method disclosure, and responsive stacking.

- [ ] **Step 4: Build component**

Run: `npm run build`

Workdir: `app/web/streamlit_components/economic_cycle_workbench`

Expected: Vite build exits 0 and rewrites `component_static`.

- [ ] **Step 5: Run UI contracts**

Run: `.venv/bin/python -m pytest tests/test_market_context_economic_cycle.py tests/test_market_context_valuation.py -q`

Expected: all pass.

### Task 4: Refresh actual snapshots and browser QA

**Files:**
- No tracked code file required.
- Generated screenshot: outside git.

**Interfaces:**
- Consumes: stored artifacts and PIT data
- Produces: refreshed current/historical compact snapshots

- [ ] **Step 1: Rematerialize stored origins**

Load stored current/history artifact rows, prime one PIT panel, and rerun `materialize_economic_cycle_snapshot` with each origin-specific artifact. Do not retrain or relax gates.

- [ ] **Step 2: Verify actual read model**

Run a DB-backed read-model summary and confirm current has three numeric horizon distributions, `PROVISIONAL` status, and non-empty recent history path.

- [ ] **Step 3: Browser QA**

Open `http://localhost:8502/`, verify desktop and 420px layout, exact selector regression, visible 2×2 path, probability cards, status badges, ribbon, no console errors, and capture one screenshot outside git.

### Task 5: Documentation, full verification, commit

**Files:**
- Create: `.aiworkspace/note/finance/tasks/active/overview-market-context-economic-cycle-provisional-hybrid-v2-20260716/*`
- Modify: relevant finance INDEX/ROADMAP/flow/data/root handoff docs only where behavior changed.

- [ ] **Step 1: Update task and durable docs**

Record the three-state meaning, provisional persistence/read-model boundary, hybrid visualization, actual refresh result, and QA evidence.

- [ ] **Step 2: Run full focused verification**

Run:

```bash
.venv/bin/python -m pytest tests/test_economic_cycle_vintages.py tests/test_economic_cycle_features.py tests/test_economic_cycle_labels.py tests/test_economic_cycle_model.py tests/test_economic_cycle_validation.py tests/test_economic_cycle_results.py tests/test_economic_cycle_pipeline.py tests/test_economic_cycle_service.py tests/test_market_context_economic_cycle.py tests/test_market_context_valuation.py -q
.venv/bin/python -m py_compile finance/economic_cycle_pipeline.py app/services/overview/economic_cycle.py
git diff --check
git status --short
```

Expected: tests pass, compile exits 0, diff check exits 0, only scoped files plus pre-existing user files are present.

- [ ] **Step 3: Commit coherent implementation**

Stage only scoped implementation and documentation files. Do not stage generated screenshots, registry/saved files, `.superpowers/`, or the unrelated market-interest research folder.
