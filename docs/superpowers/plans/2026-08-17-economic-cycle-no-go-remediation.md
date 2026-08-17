# Economic Cycle NO_GO Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair current-state continuity and validate task-specific transition pressure and unrestricted destination models without lowering publication gates.

**Architecture:** A bounded backward-only RTDSM lag resolver prevents one missing observation from invalidating six subsequent states. Required macro drivers use long-history BAA10Y instead of truncated BAML/late ANFCI, then pressure and destination are validated with separate feature contracts while preserving chronological episode folds.

**Tech Stack:** Python 3, pandas, NumPy, MySQL read loaders, pytest

## Global Constraints

- No future observation, revised-history substitution, or value interpolation.
- Keep the two-release confirmed state and unrestricted four-destination target.
- Do not lower coverage, calibration, support, or paired-skill thresholds.
- Do not modify production persistence, Overview UI, or asset-pathway contracts before GO.

---

### Task 1: RTDSM bounded lag continuity

**Files:**
- Modify: `finance/economic_cycle_realtime_history.py`
- Test: `tests/test_economic_cycle_realtime_history.py`

**Interfaces:**
- Consumes: RTDSM vintage `pd.Series` indexed by monthly `Period`.
- Produces: transform value plus whether a one-month backward lag fallback was used.

- [ ] **Step 1: Write the failing continuity test**

Create a RUC series where the exact 3M month is absent but the 4M observation exists. Assert the
3M-normalized signal is finite, no future value is read, and the resulting panel origin is `LIMITED`.

- [ ] **Step 2: Run the focused test and verify failure**

Run: `PYTHONPATH=. .venv/bin/python -m pytest -q tests/test_economic_cycle_realtime_history.py`
Expected: the new origin is `UNAVAILABLE` before implementation.

- [ ] **Step 3: Implement bounded backward lag resolution**

Resolve exact lag first, then only `target_period - 1`. Annualized log transforms use the actual lag;
level change uses `signal * target_lag / actual_lag`. Return a fallback flag and include it in panel
quality so the origin becomes `LIMITED`, never silently `READY`.

- [ ] **Step 4: Run continuity and core-state regression tests**

Run: `PYTHONPATH=. .venv/bin/python -m pytest -q tests/test_economic_cycle_realtime_history.py tests/test_economic_cycle_core_state.py tests/test_economic_cycle_confirmed_state.py`
Expected: all pass.

### Task 2: Long-history credit and compact task datasets

**Files:**
- Modify: `finance/economic_cycle_transition_dataset.py`
- Modify: `finance/economic_cycle_transition_drivers.py`
- Modify: `finance/economic_cycle_state_transition_experiment.py`
- Test: `tests/test_economic_cycle_transition_dataset.py`
- Test: `tests/test_economic_cycle_transition_drivers.py`
- Test: `tests/test_economic_cycle_state_transition_experiment.py`

**Interfaces:**
- Produces: `restrict_transition_dataset_features(dataset, feature_names)` with recalculated eligibility and episode weights.
- Produces: BAA10Y level/delta features from stored observation-date rows.
- Produces: required pressure feature contract with five directional drivers.

- [ ] **Step 1: Write failing dataset and BAA10Y tests**

Assert compact feature restriction ignores missing discarded columns, recalculates episode weights,
BAA10Y produces monthly level/delta, and BAML/ANFCI no longer block required coverage.

- [ ] **Step 2: Run focused tests and verify failure**

Run: `PYTHONPATH=. .venv/bin/python -m pytest -q tests/test_economic_cycle_transition_dataset.py tests/test_economic_cycle_transition_drivers.py`
Expected: missing helper/constants/features fail.

- [ ] **Step 3: Implement compact dataset and required driver contract**

Add compact core constants/helper, add BAA10Y market-like feature extraction, load BAA10Y through the
existing DB-only asset market-series loader, and keep BAML/ANFCI outside required intersection.

- [ ] **Step 4: Run focused regression tests**

Run: `PYTHONPATH=. .venv/bin/python -m pytest -q tests/test_economic_cycle_transition_dataset.py tests/test_economic_cycle_transition_drivers.py tests/test_economic_cycle_state_transition_experiment.py`
Expected: all pass.

### Task 3: Task-specific publication decision

**Files:**
- Modify: `finance/economic_cycle_transition_comparison.py`
- Modify: `finance/economic_cycle_state_transition_experiment.py`
- Test: `tests/test_economic_cycle_transition_comparison.py`
- Test: `tests/test_economic_cycle_state_transition_experiment.py`

**Interfaces:**
- Pressure publication: extended directional model READY plus positive common-origin skill over compact core.
- Destination publication: compact-core destination READY.
- Final report: GO only when both independent task contracts pass.

- [ ] **Step 1: Write failing task-routing tests**

Create reports where pressure improves but extended destination does not. Assert GO when compact-core
destination is READY; assert NO_GO/LIMITED_GO when either required task fails.

- [ ] **Step 2: Run focused tests and verify failure**

Run: `PYTHONPATH=. .venv/bin/python -m pytest -q tests/test_economic_cycle_transition_comparison.py tests/test_economic_cycle_state_transition_experiment.py`
Expected: old same-model destination requirement fails the new contract.

- [ ] **Step 3: Implement task-specific routing**

Compare pressure on common origins only, route compact-core destination decision separately, and build
reason codes solely from the task that owns each publication decision.

- [ ] **Step 4: Run all economic-cycle tests**

Run: `PYTHONPATH=. .venv/bin/python -m pytest -q tests/test_economic_cycle*.py`
Expected: all pass.

### Task 4: Actual DB revalidation and documentation

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-no-go-remediation-v1-20260817/{STATUS,NOTES,RUNS,RISKS}.md`
- Modify only if canonical meaning changes: `.aiworkspace/note/finance/docs/{ROADMAP,PROJECT_MAP}.md`
- Modify only if data contract changes durably: `.aiworkspace/note/finance/docs/data/README.md`

**Interfaces:**
- Consumes: `run_state_transition_feasibility('2026-07-31')`.
- Produces: exact GO/LIMITED_GO/NO_GO evidence and the phase-4 stop/continue decision.

- [ ] **Step 1: Run exact current feasibility**

Record current confirmed phase availability, driver support, task decisions, paired pressure skill,
calibration, and reason codes.

- [ ] **Step 2: Run static verification**

Run: `PYTHONPATH=. .venv/bin/python -m py_compile finance/economic_cycle_*.py`
Run: `git diff --check`
Expected: both succeed.

- [ ] **Step 3: Apply the stop condition**

Only final GO may open phase 4. LIMITED_GO or NO_GO leaves production persistence/service/UI untouched
and records the exact remaining failure.

- [ ] **Step 4: Commit the coherent 1~3 remediation unit**

Stage only owned source, tests, plan, and task/durable docs. Preserve unrelated registries, run history,
screenshots, and run artifacts.
