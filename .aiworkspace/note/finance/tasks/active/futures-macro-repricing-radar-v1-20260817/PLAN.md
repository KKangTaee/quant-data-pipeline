# Futures Macro Repricing Radar V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 선물 매크로 기본 화면에서 향후 5거래일 예측 게이트를 제거하고, 현재 1D·5D·20D 움직임을 유력 해석·반대 근거·조건부 시나리오로 연결하는 시장 재가격화 레이더를 제공한다.

**Architecture:** Python helper가 기존 저장 snapshot의 여섯 family 관측을 읽어 가장 강한 5D core 축과 독립 core 정렬을 결정적으로 분류한다. React는 새 `market_repricing` payload를 표시하며 forecast publication 상태·Brier·확률은 기본 화면에서 읽지 않는다. 기존 daily-only validation, immutable forecast history와 DB schema는 호환성·shadow research를 위해 보존한다.

**Tech Stack:** Python 3.12, pytest, React 18, TypeScript, Streamlit custom component, CSS

## Global Constraints

- 기본 화면에서 `현재 흐름을 향후 5거래일로 연장할 수 있는가?`와 forecast gate를 렌더링하지 않는다.
- 결과 문장은 자유 생성이 아니라 family 값과 `SIGNAL_Z_THRESHOLD`에서 결정적으로 생성한다.
- 장중 잠정 관측과 마지막 완료 일봉 fallback 계약을 유지한다.
- 확률 예측, 선물곡선, SOFR, 옵션, 포지셔닝과 provider 변경은 범위 밖이다.
- family 중복을 독립 확인으로 과장하지 않고 core 4개만 정렬 강도에 사용한다.
- React와 Streamlit은 DB/provider 계산을 소유하지 않는다.

---

## 이걸 하는 이유?

현재 화면은 투자자가 원하는 `무엇이 움직이고 어떤 거시 해석이 가능한가`보다 검증되지 않은 미래 5D publication gate를 크게 보여준다. 현재 데이터는 연속선물 가격 흐름이므로 정확한 5D 수익 방향보다 시장 재가격화, 교차자산 정렬과 조건부 시나리오를 설명하는 데 적합하다. 이번 작업은 제품 약속을 데이터가 실제로 답할 수 있는 질문에 맞춘다.

### Task 1: Payload contract and deterministic radar narrative

**Files:**
- Modify: `tests/test_overview_futures_macro_short_horizon.py`
- Modify: `tests/test_futures_macro_v2_integration.py`
- Modify: `app/web/overview/futures_macro_helpers.py`

**Interfaces:**
- Consumes: current pattern `families[*].one_day/five_day/twenty_day`, `SIGNAL_Z_THRESHOLD`
- Produces: `short_horizon_decision.market_repricing` with `status`, `confidence_label`, `headline`, `interpretation`, `supporting_evidence`, `counter_evidence`, `conditional_scenario`

- [ ] **Step 1: Write failing payload tests**

  Add literal expectations that schema V7 omits `future_five_day_validation`, selects the strongest material core family, separates supporting and counter evidence, and returns continuation/invalidation/sensitive-asset fields. Add low-signal and unavailable cases.

- [ ] **Step 2: Run the focused test and verify RED**

  Run: `.venv/bin/python -m pytest tests/test_overview_futures_macro_short_horizon.py -q`

  Expected: failures for V7 and missing `market_repricing` contract.

- [ ] **Step 3: Implement the minimal deterministic helper**

  Add family basis, risk-alignment and sensitive-asset mappings. Select the largest absolute material 5D core value; classify other core rows by normalized risk alignment; use confirmations only as supporting/counter context. Return `LOW_SIGNAL` when no core crosses the threshold and `UNAVAILABLE` when no finite core values exist.

- [ ] **Step 4: Run payload tests and verify GREEN**

  Run: `.venv/bin/python -m pytest tests/test_overview_futures_macro_short_horizon.py tests/test_futures_macro_v2_integration.py -q`

  Expected: all selected tests pass.

### Task 2: React market-repricing surface and forecast removal

**Files:**
- Create: `app/web/streamlit_components/futures_macro_workbench/src/MarketRepricingSection.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/FuturesMacroWorkbench.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/ShortHorizonDecisionSection.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/MethodDisclosure.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/style.css`
- Delete: `app/web/streamlit_components/futures_macro_workbench/src/ForecastValidationGate.tsx`
- Modify: `tests/test_overview_futures_macro_short_horizon.py`
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- Consumes: `ShortHorizonDecisionPayload.market_repricing`
- Produces: visible order `hero -> observation flow -> market repricing -> family evidence -> regime history -> observational method -> trace`

- [ ] **Step 1: Write failing React source-contract tests**

  Assert that `ForecastValidationGate` no longer exists or renders, `MarketRepricingSection` follows the observation flow, the title is `시장 재가격화 흐름`, and methodology does not display Brier or provisional forecast probability.

- [ ] **Step 2: Run source-contract tests and verify RED**

  Run: `.venv/bin/python -m pytest tests/test_overview_futures_macro_short_horizon.py tests/test_service_contracts.py -q`

  Expected: failures identifying the old forecast import/render and missing radar component.

- [ ] **Step 3: Implement the React surface and responsive CSS**

  Render three cards for `유력한 해석`, `반대 근거`, `조건부 시나리오`; display `지속 조건`, `무효화 조건`, and sensitive-asset chips. Remove forecast gate CSS and turn method disclosure into observation/source/coverage evidence only.

- [ ] **Step 4: Build and verify GREEN**

  Run: `npm run build` in `app/web/streamlit_components/futures_macro_workbench`

  Run: `.venv/bin/python -m pytest tests/test_overview_futures_macro_short_horizon.py tests/test_service_contracts.py -q`

  Expected: build exit 0 and all selected tests pass.

### Task 3: Actual DB QA and durable documentation

**Files:**
- Modify: `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/flows/README.md`
- Modify: `.aiworkspace/note/finance/docs/data/DATA_FLOW_MAP.md`
- Modify: task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`

**Interfaces:**
- Consumes: production V7 payload and built component
- Produces: current product contract and QA evidence

- [ ] **Step 1: Verify an actual stored snapshot**

  Build the workbench payload from `load_overview_futures_macro_materialized_snapshot()` and inspect the radar headline, evidence arrays and absence of the future gate field.

- [ ] **Step 2: Run focused and integration verification**

  Run Python compilation, Futures Macro focused suites, React production build and `git diff --check`.

- [ ] **Step 3: Run Browser QA**

  Open `/overview?overview_tab=futures-macro`, verify desktop and narrow layout, absence of forecast gate, current/fallback provenance, market interpretation cards, no overflow and no console errors. Save one generated screenshot without staging it.

- [ ] **Step 4: Sync owning docs and task closeout**

  Describe Futures Macro as an observational market-repricing radar. State that forecast artifacts remain backend-only and are not a primary product promise.

- [ ] **Step 5: Commit the coherent implementation**

  Stage only the task-owned source, tests, built bundle and durable docs. Exclude registry, run history, unrelated research and QA artifacts.

## Stop Condition

- Actual payload cannot produce a deterministic interpretation without adding new provider data.
- Removing the default forecast surface requires deleting DB forecast history or changing validation thresholds.
- Existing user-owned changes overlap a task-owned file.

Any stop condition requires reporting the conflict before expanding scope.
