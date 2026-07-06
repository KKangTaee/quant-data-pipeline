# Backtest Strategy Form Cleanup V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Keep the existing Streamlit strategy selector and strategy-specific form switching, remove the overbuilt Strategy Detail panel, and clean up the per-strategy input surfaces, especially strict Quality / Value preset and preflight areas.

**Architecture:** The Strategy dropdown, Single Strategy form dispatch, and Portfolio Mix Builder component boxes remain Streamlit-owned. React is retained only where it already has a narrow role, such as Price Freshness Preflight and handoff action cards. The cleanup focuses on form text, grouping, helper contracts, and cross-surface consistency without changing strategy runtime or registry semantics.

**Tech Stack:** Python Streamlit, focused `unittest` service-contract tests, Selenium Browser QA for layout verification.

---

### Task 1: Remove Active Strategy Detail Panel

**Files:**
- Modify: `app/web/backtest_single_strategy.py`
- Delete or disconnect: `app/services/backtest_strategy_detail.py`
- Delete or disconnect: `app/web/components/backtest_strategy_detail_panel/`
- Modify: `tests/test_service_contracts.py`
- Modify docs that made the panel a durable active flow.

- [x] **Step 1: Write failing tests**

Add a contract test that asserts the active Single Strategy workspace does not import or render `backtest_strategy_detail_panel`, and that no active service/component file for the overbuilt panel remains in the expected active path.

- [x] **Step 2: Verify RED**

Run the focused test and confirm it fails because the active UI still imports and renders the panel.

- [x] **Step 3: Remove active render path**

Remove `build_backtest_strategy_detail_model`, `render_backtest_strategy_detail_panel`, `_render_strategy_detail_panel`, and related helper usage from `app/web/backtest_single_strategy.py`.

- [x] **Step 4: Remove stale panel contract**

Remove the read-model / React panel tests and delete stale active panel files if they are no longer used.

- [x] **Step 5: Verify and commit**

Run focused tests, `py_compile`, and commit the correction. Keep the Price Freshness Preflight component and its tests.

### Task 2: Strict Preset / Form Surface Helper Cleanup

**Files:**
- Modify: `app/web/backtest_common.py`
- Modify: `tests/test_service_contracts.py`

- [ ] **Step 1: Add helper contract tests**

Add tests for strict preset basis model copy and display model shape: source basis, not-S&P caveat, loaded/target count, refresh guidance, and staged preset warning.

- [ ] **Step 2: Implement compact display model**

Create or adjust Streamlit-free helper output so the UI can render `현재 기준`, `주의`, and `업데이트 방법` without long mixed-language captions.

- [ ] **Step 3: Update renderer**

Change `_render_strict_preset_status_note` to use concise grouped copy. Do not add new data fetches.

- [ ] **Step 4: Verify and commit**

Run focused helper tests and `py_compile app/web/backtest_common.py`.

### Task 3: Quality / Value Strict Single Strategy Forms

**Files:**
- Modify: `app/web/backtest_single_forms/strict_factor.py`
- Modify: `tests/test_service_contracts.py`

- [ ] **Step 1: Add static form contract tests**

Assert strict annual and quarterly forms keep `Price Freshness Preflight`, keep statement coverage preview where relevant, avoid the removed Strategy Detail panel, and expose concise helper calls around preset/preflight.

- [ ] **Step 2: Clean strict annual form surface**

Reduce top guide noise, keep required data requirements collapsed, render preset explanation compactly, keep price preflight immediately before date/top-N inputs, and keep advanced contracts collapsed.

- [ ] **Step 3: Clean strict quarterly prototype form surface**

Make prototype status clear without making the page feel like a research memo. Keep coverage preview and quarterly caveats, but group them as pre-run checks.

- [ ] **Step 4: Browser QA and commit**

Use Browser QA on Quality Strict Annual and Value Strict Quarterly Prototype. Commit the single-strategy strict form cleanup.

### Task 4: Equal Weight / ETF-Like Form Consistency

**Files:**
- Modify if needed: `app/web/backtest_single_forms/equal_weight.py`
- Modify if needed: `app/web/backtest_single_forms/gtaa.py`, `global_relative_strength.py`, `risk_parity.py`, `dual_momentum.py`
- Modify: `tests/test_service_contracts.py`

- [ ] **Step 1: Add form consistency checks**

Add static tests that simple ETF-like forms do not depend on the removed Strategy Detail panel and keep advanced / promotion / guardrail controls collapsed.

- [ ] **Step 2: Adjust only visible copy if needed**

Keep the existing layout and remove only confusing or redundant captions. Do not add new panels.

- [ ] **Step 3: Browser QA and commit**

Verify Equal Weight and GTAA still render as existing form-first flows.

### Task 5: Portfolio Mix Builder Impact / Docs Closeout

**Files:**
- Modify if needed: `app/web/backtest_compare/page.py`
- Modify durable docs and root logs.

- [ ] **Step 1: Check Portfolio Mix Builder strict sections**

Ensure compare mode stays Streamlit-owned and does not rely on the removed Strategy Detail panel. Apply compact strict preset copy if the same helper is used.

- [ ] **Step 2: Browser QA**

Verify Portfolio Mix Builder can show a strict Quality/Value component settings section without the removed panel.

- [ ] **Step 3: Docs sync**

Update project map, script structure map, Backtest UI flow, roadmap/index, root handoff logs, and this task status.

- [ ] **Step 4: Final verification and commit**

Run focused tests, `py_compile`, `git diff --check`, and commit documentation / closeout.
