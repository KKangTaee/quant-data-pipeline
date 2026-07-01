# Backtest Final Boundary Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish the Backtest refactor by turning the current large Backtest scripts into package-based UI, service, runtime, store, read-model, and strategy-runner boundaries while preserving existing product behavior.

**Architecture:** Convert same-name files such as `app/runtime/backtest.py`, `app/web/backtest_compare.py`, `app/web/backtest_practical_validation.py`, and `app/web/backtest_final_review.py` into packages with `__init__.py` compatibility exports. Move implementation bodies into focused modules only after import-compatibility tests exist, and commit after each V stage passes QA.

**Tech Stack:** Python, Streamlit, pandas, unittest/pytest, finance strategy runtime, JSONL workflow registries.

---

## Current Baseline After V1

V1 already created the first boundary helpers, but the structure is still transitional.

```text
app/web/
  backtest_page.py
  backtest_state.py
  backtest_formatters.py
  backtest_analysis.py
  backtest_single_strategy.py
  backtest_single_forms.py
  backtest_compare.py
  backtest_practical_validation.py
  backtest_final_review.py

app/services/
  backtest_single_payload.py
  backtest_portfolio_mix_readiness.py
  backtest_validation_status_policy.py
  backtest_final_review_policy.py
  backtest_practical_validation_*.py

app/runtime/
  backtest.py
  backtest_result_bundle.py
  backtest_runner_catalog.py
  backtest_real_money.py
  backtest_strict.py
  backtest_risk_on_momentum.py
  history.py
  candidate_registry.py
  portfolio_selection_v2.py
  portfolio_store.py
  candidate_library.py
  final_selected_portfolios.py
```

Problems to finish:

- `app/runtime/backtest.py` still mixes public facade, shared helpers, and price strategy runners.
- `app/web/backtest_single_forms.py`, `backtest_compare.py`, `backtest_practical_validation.py`, and `backtest_final_review.py` are still broad UI modules.
- JSONL stores and replay/read models exist, but they are not grouped by role.
- `backtest_runner_catalog.py` is metadata-only and does not yet fully protect dispatch ownership.

## Final Target Structure

```text
app/web/
  backtest_page.py
  backtest_state.py
  backtest_formatters.py
  backtest_presets.py
  backtest_inputs.py

  backtest_analysis.py
  backtest_single_strategy.py

  backtest_single_forms/
    __init__.py
    equal_weight.py
    gtaa.py
    global_relative_strength.py
    risk_parity.py
    dual_momentum.py
    risk_on_momentum.py
    strict_factor.py

  backtest_compare/
    __init__.py
    page.py
    execution_panel.py
    saved_replay_panel.py
    weight_builder.py
    handoff_panel.py
    components.py

  backtest_practical_validation/
    __init__.py
    page.py
    source_summary.py
    replay_panel.py
    evidence_boards.py
    provider_actions.py
    components.py

  backtest_final_review/
    __init__.py
    page.py
    candidate_board.py
    decision_cockpit.py
    evidence_appendix.py
    handoff_panel.py
    components.py

app/services/
  backtest_execution.py
  backtest_compare_execution.py
  backtest_compare_catalog.py
  backtest_single_payload.py
  backtest_portfolio_mix_readiness.py
  backtest_validation_status_policy.py
  backtest_final_review_policy.py
  backtest_practical_validation_*.py
  backtest_evidence_read_model.py
  backtest_weighted_portfolio.py
  backtest_saved_portfolio_replay.py

app/runtime/backtest/
  __init__.py
  facade.py
  common.py
  result_bundle.py
  runner_catalog.py
  real_money.py

  runners/
    __init__.py
    equal_weight.py
    gtaa.py
    global_relative_strength.py
    risk_parity_trend.py
    dual_momentum.py
    risk_on_momentum.py
    strict_factor.py

  stores/
    __init__.py
    run_history.py
    candidate_registry.py
    portfolio_selection.py
    portfolio_store.py
    portfolio_proposal.py
    final_selection_decisions.py
    paper_portfolio_ledger.py

  read_models/
    __init__.py
    candidate_library.py
    final_selected_portfolios.py

finance/
  engine.py
  strategy.py
  transform.py
  performance.py
  sample.py
  swing.py
  indicators.py
  swing_macro.py
  swing_analysis.py
```

Compatibility rule:

- `from app.runtime.backtest import run_gtaa_backtest_from_db` must continue to work through `app/runtime/backtest/__init__.py`.
- UI imports such as `from app.web.backtest_compare import render_compare_portfolio_workspace` must continue to work through `app/web/backtest_compare/__init__.py`.
- Internal imports should gradually move to the new explicit package paths.

## Execution Closeout

Status: Completed on 2026-07-01.

- V2 through V7 were completed as separate development / QA / commit stages.
- V8 aligned durable docs, restored legacy runtime monkeypatch compatibility through package runner hooks, ran full focused QA, and completed Browser QA.
- Generated QA screenshots remain local artifacts and are not part of the commit scope.

---

## V2: Runtime Package Foundation

**Purpose:** Convert `app/runtime/backtest.py` from a file into a package without changing behavior.

**Before:**

```text
app/runtime/backtest.py
```

**After:**

```text
app/runtime/backtest/
  __init__.py
  facade.py
  common.py
```

**Files:**

- Move: `app/runtime/backtest.py` -> `app/runtime/backtest/facade.py`
- Create: `app/runtime/backtest/__init__.py`
- Create: `app/runtime/backtest/common.py`
- Modify: `app/runtime/backtest_strict.py`
- Modify: `app/runtime/backtest_risk_on_momentum.py`
- Modify: `app/runtime/backtest_real_money.py`
- Modify: `tests/test_backtest_refactor_boundaries.py`

**Steps:**

- [ ] Add import-compatibility tests for `app.runtime.backtest`, `BacktestInputError`, `BacktestDataError`, and all public `run_*_backtest_from_db` names.
- [ ] Move `BacktestInputError`, `BacktestDataError`, and shared date/input helpers into `app/runtime/backtest/common.py`.
- [ ] Convert the file to a package by moving the existing implementation body to `app/runtime/backtest/facade.py`.
- [ ] Re-export all existing public names from `app/runtime/backtest/__init__.py`.
- [ ] Update sibling runtime modules to import shared errors/helpers from `app.runtime.backtest.common` where that avoids circular imports.
- [ ] Run QA:

```bash
.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries
.venv/bin/python -m unittest tests.test_service_contracts
.venv/bin/python -m py_compile app/runtime/backtest/__init__.py app/runtime/backtest/facade.py app/runtime/backtest/common.py app/runtime/backtest_strict.py app/runtime/backtest_risk_on_momentum.py app/runtime/backtest_real_money.py
git diff --check
```

- [ ] Commit: `backtest V2 runtime 패키지 foundation 정리`

**Completion condition:** `app.runtime.backtest` remains import-compatible, but it is now a package.

---

## V3: Runtime Result, Catalog, And Strategy Runner Split

**Purpose:** Move runtime support modules and all strategy runners into `app/runtime/backtest/`.

**Before:**

```text
app/runtime/backtest_result_bundle.py
app/runtime/backtest_runner_catalog.py
app/runtime/backtest_real_money.py
app/runtime/backtest_strict.py
app/runtime/backtest_risk_on_momentum.py
app/runtime/backtest/facade.py  # still contains price runners
```

**After:**

```text
app/runtime/backtest/
  result_bundle.py
  runner_catalog.py
  real_money.py
  runners/
    equal_weight.py
    gtaa.py
    global_relative_strength.py
    risk_parity_trend.py
    dual_momentum.py
    risk_on_momentum.py
    strict_factor.py
```

**Files:**

- Move: `app/runtime/backtest_result_bundle.py` -> `app/runtime/backtest/result_bundle.py`
- Move: `app/runtime/backtest_runner_catalog.py` -> `app/runtime/backtest/runner_catalog.py`
- Move: `app/runtime/backtest_real_money.py` -> `app/runtime/backtest/real_money.py`
- Move: `app/runtime/backtest_strict.py` -> `app/runtime/backtest/runners/strict_factor.py`
- Move: `app/runtime/backtest_risk_on_momentum.py` -> `app/runtime/backtest/runners/risk_on_momentum.py`
- Create: `app/runtime/backtest/runners/equal_weight.py`
- Create: `app/runtime/backtest/runners/gtaa.py`
- Create: `app/runtime/backtest/runners/global_relative_strength.py`
- Create: `app/runtime/backtest/runners/risk_parity_trend.py`
- Create: `app/runtime/backtest/runners/dual_momentum.py`
- Modify: `app/runtime/backtest/facade.py`
- Modify: `app/runtime/backtest/__init__.py`
- Modify: `app/services/backtest_execution.py`
- Modify: `app/services/backtest_compare_catalog.py`
- Modify: `tests/test_backtest_refactor_boundaries.py`

**Steps:**

- [ ] Add tests that every catalog entry has `strategy_key`, `display_name`, `runtime_module`, `runner_name`, and resolves to a callable.
- [ ] Move `build_backtest_result_bundle` to `app.runtime.backtest.result_bundle`.
- [ ] Move real-money / guardrail helpers to `app.runtime.backtest.real_money`.
- [ ] Move strict and risk-on momentum runners into `app.runtime.backtest.runners`.
- [ ] Extract price-only ETF runners from `facade.py` into one runner module per strategy.
- [ ] Make `facade.py` and `__init__.py` re-export the old public names.
- [ ] Update service imports to use `app.runtime.backtest.runner_catalog` and package runner metadata.
- [ ] Run QA:

```bash
.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries
.venv/bin/python -m unittest tests.test_service_contracts
find app/runtime/backtest app/services -name "*.py" -print | sort | xargs .venv/bin/python -m py_compile
git diff --check
```

- [ ] Commit: `backtest V3 runtime runner 패키지 분리`

**Completion condition:** The runtime package owns facade, catalog, result bundle, real-money helper, and all DB-backed strategy runners.

---

## V4: Runtime Stores And Read Models

**Purpose:** Group JSONL persistence and replay/read-model code by role.

**Before:**

```text
app/runtime/history.py
app/runtime/candidate_registry.py
app/runtime/portfolio_selection_v2.py
app/runtime/portfolio_store.py
app/runtime/portfolio_proposal.py
app/runtime/final_selection_decisions.py
app/runtime/paper_portfolio_ledger.py
app/runtime/candidate_library.py
app/runtime/final_selected_portfolios.py
```

**After:**

```text
app/runtime/backtest/stores/
app/runtime/backtest/read_models/
```

**Files:**

- Move: `app/runtime/history.py` -> `app/runtime/backtest/stores/run_history.py`
- Move: `app/runtime/candidate_registry.py` -> `app/runtime/backtest/stores/candidate_registry.py`
- Move: `app/runtime/portfolio_selection_v2.py` -> `app/runtime/backtest/stores/portfolio_selection.py`
- Move: `app/runtime/portfolio_store.py` -> `app/runtime/backtest/stores/portfolio_store.py`
- Move: `app/runtime/portfolio_proposal.py` -> `app/runtime/backtest/stores/portfolio_proposal.py`
- Move: `app/runtime/final_selection_decisions.py` -> `app/runtime/backtest/stores/final_selection_decisions.py`
- Move: `app/runtime/paper_portfolio_ledger.py` -> `app/runtime/backtest/stores/paper_portfolio_ledger.py`
- Move: `app/runtime/candidate_library.py` -> `app/runtime/backtest/read_models/candidate_library.py`
- Move: `app/runtime/final_selected_portfolios.py` -> `app/runtime/backtest/read_models/final_selected_portfolios.py`
- Modify: all imports under `app/web/`, `app/services/`, and tests that reference the old paths.

**Steps:**

- [ ] Add tests that store modules do not import Streamlit or finance strategy engine modules.
- [ ] Add tests that read-model modules do not append workflow registry rows.
- [ ] Move store modules and preserve their public function names.
- [ ] Move read-model modules and update UI/service imports.
- [ ] Do not rewrite or compact existing JSONL registry files.
- [ ] Run QA:

```bash
.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries
.venv/bin/python -m unittest tests.test_service_contracts
find app/runtime/backtest/stores app/runtime/backtest/read_models app/services app/web -name "*.py" -print | sort | xargs .venv/bin/python -m py_compile
git diff --check
```

- [ ] Commit: `backtest V4 stores read-model 패키지 정리`

**Completion condition:** Stores append/load records only; read models build screen/replay payloads only.

---

## V5: Single Strategy UI Package Split

**Purpose:** Split Backtest Analysis single strategy forms and shared input helpers.

**Before:**

```text
app/web/backtest_common.py
app/web/backtest_single_forms.py
```

**After:**

```text
app/web/backtest_presets.py
app/web/backtest_inputs.py
app/web/backtest_single_forms/
  __init__.py
  equal_weight.py
  gtaa.py
  global_relative_strength.py
  risk_parity.py
  dual_momentum.py
  risk_on_momentum.py
  strict_factor.py
```

**Files:**

- Create: `app/web/backtest_presets.py`
- Create: `app/web/backtest_inputs.py`
- Move/split: `app/web/backtest_single_forms.py` -> `app/web/backtest_single_forms/*.py`
- Modify: `app/web/backtest_single_strategy.py`
- Modify: `app/web/backtest_single_runner.py`
- Modify: `tests/test_backtest_refactor_boundaries.py`

**Steps:**

- [ ] Add tests that `app.web.backtest_single_forms` still exports the same form functions used by `backtest_single_strategy.py`.
- [ ] Move preset constants and reusable input widgets out of `backtest_common.py` into focused modules.
- [ ] Split each strategy form into a matching module.
- [ ] Keep `app/web/backtest_single_forms/__init__.py` as the compatibility export surface.
- [ ] Run QA:

```bash
.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries
.venv/bin/python -m py_compile app/web/backtest_presets.py app/web/backtest_inputs.py app/web/backtest_single_strategy.py app/web/backtest_single_runner.py
find app/web/backtest_single_forms -name "*.py" -print | sort | xargs .venv/bin/python -m py_compile
git diff --check
```

- [ ] Commit: `backtest V5 single strategy UI 패키지 분리`

**Completion condition:** Adding or editing a strategy form no longer requires touching one large form script.

---

## V6: Portfolio Mix Builder UI Package Split

**Purpose:** Convert `app/web/backtest_compare.py` into a package and split execution, saved replay, weight builder, and handoff panels.

**Before:**

```text
app/web/backtest_compare.py
app/web/backtest_compare_components.py
```

**After:**

```text
app/web/backtest_compare/
  __init__.py
  page.py
  execution_panel.py
  saved_replay_panel.py
  weight_builder.py
  handoff_panel.py
  components.py
```

**Files:**

- Move: `app/web/backtest_compare.py` -> `app/web/backtest_compare/page.py`
- Move: `app/web/backtest_compare_components.py` -> `app/web/backtest_compare/components.py`
- Create: `app/web/backtest_compare/__init__.py`
- Create/split: `execution_panel.py`, `saved_replay_panel.py`, `weight_builder.py`, `handoff_panel.py`
- Modify: `app/web/backtest_page.py`
- Modify: `app/web/backtest_analysis.py`
- Modify: `app/web/backtest_candidate_review.py`
- Modify: tests that import private compare helpers.

**Steps:**

- [ ] Add compatibility tests for `render_compare_portfolio_workspace`, `_build_weighted_mix_candidate_readiness_evaluation`, and `_bundle_to_saved_strategy_override`.
- [ ] Convert the file to a package using `__init__.py` re-exports.
- [ ] Move pure weight-builder logic to `weight_builder.py`.
- [ ] Move saved replay UI orchestration to `saved_replay_panel.py`.
- [ ] Move candidate handoff/prefill helpers to `handoff_panel.py`.
- [ ] Run QA:

```bash
.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries
.venv/bin/python -m unittest tests.test_service_contracts
find app/web/backtest_compare app/web -maxdepth 2 -name "*.py" -print | sort | xargs .venv/bin/python -m py_compile
git diff --check
```

- [ ] Commit: `backtest V6 portfolio mix UI 패키지 분리`

**Completion condition:** Portfolio Mix Builder is navigable through the same public import but internally split by user workflow.

---

## V7: Practical Validation And Final Review UI Package Split

**Purpose:** Convert the two largest downstream Backtest stages into packages whose pages render service-owned decisions.

**Before:**

```text
app/web/backtest_practical_validation.py
app/web/backtest_practical_validation_components.py
app/web/backtest_final_review.py
app/web/backtest_final_review_components.py
```

**After:**

```text
app/web/backtest_practical_validation/
  __init__.py
  page.py
  source_summary.py
  replay_panel.py
  evidence_boards.py
  provider_actions.py
  components.py

app/web/backtest_final_review/
  __init__.py
  page.py
  candidate_board.py
  decision_cockpit.py
  evidence_appendix.py
  handoff_panel.py
  components.py
```

**Files:**

- Move/split: `app/web/backtest_practical_validation.py`
- Move: `app/web/backtest_practical_validation_components.py` -> `app/web/backtest_practical_validation/components.py`
- Move/split: `app/web/backtest_final_review.py`
- Move: `app/web/backtest_final_review_components.py` -> `app/web/backtest_final_review/components.py`
- Modify: `app/web/backtest_page.py`
- Modify: `app/services/backtest_validation_status_policy.py`
- Modify: `app/services/backtest_final_review_policy.py`
- Modify: `tests/test_backtest_refactor_boundaries.py`

**Steps:**

- [ ] Add compatibility tests for `render_practical_validation_workspace` and `render_final_review_workspace`.
- [ ] Add source tests that UI packages do not define validation status rank tables or selected-route policy tables.
- [ ] Move Practical Validation source summary, replay, evidence boards, and provider action UI into separate modules.
- [ ] Move Final Review candidate board, decision cockpit, evidence appendix, and handoff UI into separate modules.
- [ ] Keep validation and final-route decisions in `app/services`.
- [ ] Run QA:

```bash
.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries
.venv/bin/python -m unittest tests.test_service_contracts
find app/web/backtest_practical_validation app/web/backtest_final_review app/services -name "*.py" -print | sort | xargs .venv/bin/python -m py_compile
git diff --check
```

- [ ] Commit: `backtest V7 validation final-review UI 패키지 분리`

**Completion condition:** Practical Validation and Final Review pages are page shells plus panels; service modules own the decisions.

---

## V8: Documentation, Import Cleanup, Full QA, Browser QA

**Purpose:** Remove stale references, update durable docs, and verify the final Backtest structure end to end.

**Files:**

- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/BACKTEST_RUNTIME_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/STRATEGY_IMPLEMENTATION_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Modify: active task status/run/risk notes for this refactor

**Steps:**

- [x] Run `rg` for old module paths and update internal imports to final package paths.
- [x] Delete only obsolete compatibility shim files that are no longer imported by app/tests/docs.
- [x] Update durable docs with the final structure and import compatibility policy.
- [x] Run full focused QA:

```bash
git status --short
git diff --check
.venv/bin/python -m unittest tests.test_backtest_refactor_boundaries
.venv/bin/python -m unittest tests.test_service_contracts
.venv/bin/python -m unittest tests.test_global_relative_strength_strategy
.venv/bin/python -m unittest tests.test_etf_runtime_strategy_contracts
find app/runtime/backtest app/services app/web -name "*.py" -print | sort | xargs .venv/bin/python -m py_compile
```

- [x] Run Browser QA for Backtest first entry, Single Strategy, Portfolio Mix Builder, Practical Validation, and Final Review.
- [x] Save one QA screenshot as generated artifact and do not stage it unless explicitly requested.
- [x] Commit: `backtest V8 최종 구조 문서화 및 QA`

**Completion condition:** Code, tests, docs, and browser QA agree on the final package structure.

---

## Execution Cadence

```text
V2 개발 -> QA -> commit
V3 개발 -> QA -> commit
V4 개발 -> QA -> commit
V5 개발 -> QA -> commit
V6 개발 -> QA -> commit
V7 개발 -> QA -> commit
V8 문서/전체 QA -> commit
```

Do not mark the refactor complete before V8. If a stage changes strategy math, validation thresholds, registry row format, or visible product behavior, stop and split that behavior change into a separate approved task.

## Non-Goals

- Do not rewrite JSONL registry data.
- Do not change strategy math.
- Do not change validation pass/fail thresholds.
- Do not turn Final Review or Portfolio Monitoring into live approval, broker order, or auto rebalance.
- Do not stage generated QA screenshots or local run artifacts unless explicitly requested.
