# Practical Validation Pre-Final Enrichment Gate V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Subagent dispatch is disabled for this workspace session.

**Goal:** 수집 가능하고 Final Review 판단에 중요한 외부 데이터 gap을 Practical Validation에서 보강·재검증한 뒤에만 Final Review로 승격하고, Final Review에는 수집으로 해결되지 않는 잔여 판단만 남긴다.

**Architecture:** Python service가 provider collection plan을 `승격 전 필수 보강`과 `잔여 제한`으로 분류하고 Practical Validation Gate가 이 계약을 소비한다. Streamlit은 기존 Python collector를 명시적 사용자 action으로 실행하며, Final Review React는 새 검증을 실행하지 않고 legacy/stale 저장 결과에만 복구 intent를 표시한다.

**Tech Stack:** Python 3.12, Streamlit, React/TypeScript, Vite, unittest, append-only JSONL registry.

## Global Constraints

- Final Review는 live approval, broker order, auto rebalance가 아니다.
- React는 표시와 navigation intent만 담당하고 수집·검증·Gate·저장은 Python service boundary가 소유한다.
- provider fetch는 Practical Validation에서만 실행한다.
- 수집 후 기존 저장 validation과 검토서를 자동 갱신하지 않고 Flow 2 재검증과 새 validation 저장을 요구한다.
- 기간 밖 stress, 미구현 검증, historical survivorship source, 세금·계좌 판단은 일괄 수집 대상으로 취급하지 않는다.
- registry / saved JSONL / run history / generated QA artifact는 stage하거나 commit하지 않는다.

---

### Task 1: 승격 전 필수 데이터 보강 계약

**Files:**
- Modify: `app/services/backtest_practical_validation.py`
- Test: `tests/test_service_contracts.py`

**Interfaces:**
- Consumes: `build_provider_gap_collection_plan(validation_result: dict[str, Any]) -> dict[str, Any]`
- Produces: `build_pre_final_enrichment_gate(validation_result: dict[str, Any]) -> dict[str, Any]`
- Produces fields: `required`, `blocking`, `item_count`, `symbol_count`, `items`, `reason`, `next_action`

- [ ] **Step 1: Write failing contract tests**

```python
def test_collectable_stale_operability_blocks_pre_final_enrichment_gate():
    gate = build_pre_final_enrichment_gate({
        "provider_coverage": {"coverage": {"operability": {
            "missing_symbols": [],
            "provenance": {"stale_symbols": ["TLT"]},
        }}},
    })
    self.assertTrue(gate["required"])
    self.assertTrue(gate["blocking"])
    self.assertEqual(gate["items"][0]["category"], "operability")

def test_non_collectable_review_does_not_block_pre_final_enrichment_gate():
    gate = build_pre_final_enrichment_gate({"provider_coverage": {"coverage": {}}})
    self.assertFalse(gate["required"])
    self.assertFalse(gate["blocking"])
```

- [ ] **Step 2: Run tests and confirm failure**

Run: `.venv/bin/python -m unittest tests.test_service_contracts.ProviderGapCollectionServiceContractTests`

Expected: FAIL because `build_pre_final_enrichment_gate` does not exist.

- [ ] **Step 3: Implement the service contract and module Gate input**

```python
def build_pre_final_enrichment_gate(validation_result: dict[str, Any]) -> dict[str, Any]:
    plan = build_provider_gap_collection_plan(validation_result)
    items = []
    if plan["operability_official"] or plan["operability_bridge"]:
        items.append({"category": "operability", "symbols": list(plan["operability_bridge"])})
    if plan["holdings_exposure"]:
        items.append({"category": "holdings_exposure", "symbols": list(plan["holdings_exposure"])})
    if plan["source_map_discovery"]:
        items.append({"category": "source_map_discovery", "symbols": list(plan["source_map_discovery"])})
    if plan["macro"]:
        items.append({"category": "macro", "symbols": ["VIXCLS", "T10Y3M", "BAA10Y"]})
    unique_symbols = {symbol for item in items for symbol in item["symbols"]}
    return {
        "required": bool(items),
        "blocking": bool(items),
        "item_count": len(items),
        "symbol_count": len(unique_symbols),
        "items": items,
        "reason": "현재 수집 가능한 필수 외부 데이터가 남아 있습니다." if items else "승격 전 필수 데이터 보강이 없습니다.",
        "next_action": "데이터를 보강한 뒤 Flow 2 재검증을 실행합니다." if items else "Final Review 판단을 이어갑니다.",
    }
```

`build_practical_validation_result(...)` wrapper는 diagnostics 결과에 provider plan을 추가한 뒤 blocking이면 synthetic required module `pre_final_data_enrichment`와 Final Review Gate blocker를 추가하고 `can_save_and_move=false`로 갱신한다.

- [ ] **Step 4: Run focused tests**

Run: `.venv/bin/python -m unittest tests.test_service_contracts.ProviderGapCollectionServiceContractTests tests.test_service_contracts.PracticalValidationServiceContractTests tests.test_service_contracts.PracticalValidationDiagnosticsServiceContractTests`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/services/backtest_practical_validation.py tests/test_service_contracts.py .aiworkspace/note/finance/tasks/active/practical-validation-pre-final-enrichment-gate-v1-20260712
git commit -m "Practical Validation 승격 전 데이터 보강 계약 추가"
```

### Task 2: Practical Validation 보강·재검증 완료 흐름

**Files:**
- Modify: `app/services/backtest_practical_validation.py`
- Modify: `app/services/backtest_practical_validation_workspace.py`
- Modify: `app/web/backtest_practical_validation/page.py`
- Test: `tests/test_service_contracts.py`

**Interfaces:**
- Consumes: `pre_final_enrichment_gate`
- Produces: Gate-disabled Flow 3 action and Flow 4 `필수 데이터 보강` action
- Preserves: `run_provider_gap_collection(validation_result)` as the only provider execution boundary

- [ ] **Step 1: Write failing page/service contract tests**

```python
def test_collectable_pre_final_gap_disables_save_and_move():
    self.assertFalse(result["final_review_gate"]["can_save_and_move"])
    self.assertEqual(result["final_review_gate"]["route"], "BLOCKED_FOR_FINAL_REVIEW")

def test_practical_validation_copy_requires_enrichment_then_flow2_recheck():
    self.assertIn("필수 데이터 보강", page_source)
    self.assertIn("Flow 2 재검증", page_source)
```

- [ ] **Step 2: Run tests and confirm failure**

Run: `.venv/bin/python -m unittest tests.test_service_contracts.PracticalValidationServiceContractTests tests.test_service_contracts.PracticalValidationDiagnosticsServiceContractTests tests.test_service_contracts.BacktestRuntimeContractTests`

Expected: FAIL because collectable REVIEW currently remains movable.

- [ ] **Step 3: Implement Gate and user action flow**

Flow 3 explains that Final Review movement is disabled until enrichment and recheck. Flow 4 shows only executable items, runs the existing collector after explicit click, clears current replay state, and directs the user to Flow 2. Collection success alone never changes the saved validation.

- [ ] **Step 4: Run focused tests, py_compile, diff check**

Run: `.venv/bin/python -m unittest tests.test_service_contracts.PracticalValidationServiceContractTests tests.test_service_contracts.PracticalValidationDiagnosticsServiceContractTests tests.test_service_contracts.ProviderGapCollectionServiceContractTests tests.test_service_contracts.BacktestRuntimeContractTests`

Run: `.venv/bin/python -m py_compile app/services/backtest_practical_validation.py app/services/backtest_practical_validation_workspace.py app/web/backtest_practical_validation/page.py`

Run: `git diff --check`

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add app/services/backtest_practical_validation.py app/services/backtest_practical_validation_workspace.py app/web/backtest_practical_validation/page.py tests/test_service_contracts.py
git commit -m "Practical Validation 데이터 보강 후 재검증 흐름 정리"
```

### Task 3: Final Review 잔여 판단과 legacy 복구 경로

**Files:**
- Modify: `app/services/backtest_evidence_read_model.py`
- Modify: `app/web/backtest_final_review_helpers.py`
- Modify: `app/web/backtest_final_review/page.py`
- Modify: `app/web/components/final_review_investment_report/frontend/src/FinalReviewInvestmentReport.tsx`
- Modify: `app/web/components/final_review_investment_report/frontend/src/style.css`
- Test: `tests/test_service_contracts.py`

**Interfaces:**
- Consumes: stored validation Gate plus current `build_pre_final_enrichment_gate(...)`
- Produces: `data_enrichment_action.mode` values `hidden`, `legacy_recovery`, `stale_recovery`
- Final Review eligible current validations must have no blocking pre-final enrichment gate.

- [ ] **Step 1: Write failing eligibility and React contract tests**

```python
def test_current_collectable_validation_is_not_final_review_eligible():
    self.assertFalse(_is_final_review_eligible_validation_result(validation))

def test_legacy_saved_validation_exposes_recovery_not_normal_guidance():
    action = report["level2_review_disposition"]["data_enrichment_action"]
    self.assertEqual(action["mode"], "legacy_recovery")
    self.assertIn("최신 기준을 충족하지 않습니다", action["title"])
```

- [ ] **Step 2: Run tests and confirm failure**

Run: `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests tests.test_service_contracts.BacktestRuntimeContractTests`

Expected: FAIL because Final Review currently treats the panel as normal guidance and eligibility only reads stored `can_save_and_move`.

- [ ] **Step 3: Implement recovery-only presentation**

Newly evaluated validations with blocking enrichment are excluded from Final Review. Already saved legacy rows remain inspectable only through an explicit recovery state; the card uses warning language and routes to Practical Validation without provider fetch. Non-collectable residual REVIEW items remain visible as Final Review decisions or Monitoring conditions.

- [ ] **Step 4: Build and run focused checks**

Run: `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests tests.test_service_contracts.BacktestRuntimeContractTests`

Run: `npm --prefix app/web/components/final_review_investment_report/frontend run build`

Run: `.venv/bin/python -m py_compile app/services/backtest_evidence_read_model.py app/web/backtest_final_review_helpers.py app/web/backtest_final_review/page.py`

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add app/services/backtest_evidence_read_model.py app/web/backtest_final_review_helpers.py app/web/backtest_final_review/page.py app/web/components/final_review_investment_report/frontend tests/test_service_contracts.py
git commit -m "Final Review 데이터 보강을 복구 경로로 제한"
```

### Task 4: QA, current candidate compatibility, docs sync

**Files:**
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Modify: `.aiworkspace/note/finance/tasks/active/README.md`
- Modify: `.aiworkspace/note/finance/tasks/active/STATUS_MANIFEST.md`
- Modify: task `STATUS.md`, `RUNS.md`, `NOTES.md`, `RISKS.md`

- [ ] **Step 1: Run full focused verification**

Run: `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests tests.test_service_contracts.ProviderGapCollectionServiceContractTests tests.test_service_contracts.PracticalValidationServiceContractTests tests.test_service_contracts.PracticalValidationDiagnosticsServiceContractTests tests.test_service_contracts.BacktestRuntimeContractTests`

Run: `npm --prefix app/web/components/final_review_investment_report/frontend run build`

Run: `.venv/bin/python -m py_compile app/services/backtest_evidence_read_model.py app/services/backtest_practical_validation.py app/services/backtest_practical_validation_workspace.py app/web/backtest_practical_validation/page.py app/web/backtest_final_review/page.py app/web/backtest_final_review_helpers.py`

Run: `git diff --check`

Expected: all PASS; external dependency warnings may remain but no failures.

- [ ] **Step 2: Browser QA**

Verify Practical Validation collectable gap blocks movement, collection returns to Flow 2 recheck, Final Review normal candidate has no enrichment panel, legacy/stale candidate shows recovery language, candidate switching stale guard still works, and no horizontal overflow at compact width.

- [ ] **Step 3: Verify artifact safety**

Run: `git status --short`

Expected: registry / saved JSONL / run history / QA screenshot are unstaged.

- [ ] **Step 4: Sync durable docs and close task**

Record the new stage ownership: Practical Validation resolves executable required gaps; Final Review accepts only non-collectable residual limits and exposes legacy recovery when necessary.

- [ ] **Step 5: Commit**

```bash
git add .aiworkspace/note/finance/docs .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md .aiworkspace/note/finance/tasks/active/practical-validation-pre-final-enrichment-gate-v1-20260712
git commit -m "Practical Validation 선제 보강 Gate QA와 문서 동기화"
```
