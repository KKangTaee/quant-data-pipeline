# PIT Universe Snapshot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a monthly point-in-time U.S. large-cap universe snapshot layer and wire strict Quality / Value backtests to use it instead of replaying today's Top-N universe through history.

**Architecture:** Add DB schema and pure builder helpers under the data layer, then expose read contracts through loaders and strict-factor runtime. Backtest UI keeps the current static and approximate dynamic paths but adds a clearly named PIT monthly snapshot contract.

**Tech Stack:** Python, pandas, MySQL schema helpers, Streamlit Backtest UI, unittest contract tests.

---

### Task 1: Schema And Loader Contract

**Files:**
- Modify: `finance/data/db/schema.py`
- Create: `finance/data/pit_universe.py`
- Modify: `finance/loaders/universe.py`
- Test: `tests/test_service_contracts.py`

- [ ] **Step 1: Write failing tests** for `PIT_UNIVERSE_SCHEMAS`, `build_equity_universe_snapshot_payload`, and PIT membership loader normalization.
- [ ] **Step 2: Run focused tests** and confirm imports fail because the module / schema do not exist.
- [ ] **Step 3: Add schema definitions and pure payload builder** with no DB writes yet.
- [ ] **Step 4: Add read helper shape in `finance/loaders/universe.py`.**
- [ ] **Step 5: Run focused tests and commit.**

### Task 2: Monthly Snapshot Builder

**Files:**
- Modify: `finance/data/pit_universe.py`
- Test: `tests/test_service_contracts.py`

- [ ] **Step 1: Write failing tests** proving two month-end snapshots can rank different symbols using as-of price and latest-known shares.
- [ ] **Step 2: Add month-end snapshot generation helper** using price rows, statement shadow shares, asset profile, and lifecycle evidence.
- [ ] **Step 3: Add idempotent upsert helper** for snapshot and member rows.
- [ ] **Step 4: Run focused tests and commit.**

### Task 3: Strict Quality / Value Runtime Contract

**Files:**
- Modify: `finance/sample.py`
- Modify: `app/runtime/backtest/runners/strict_factor.py`
- Test: `tests/test_service_contracts.py`

- [ ] **Step 1: Write failing tests** for `PIT_MONTHLY_SNAPSHOT_UNIVERSE` membership map application.
- [ ] **Step 2: Add sample runtime support** that filters rebalance snapshots by prebuilt PIT membership.
- [ ] **Step 3: Add strict runner metadata** for PIT snapshot status, member count, and missing snapshot warnings.
- [ ] **Step 4: Run focused tests and commit.**

### Task 4: Backtest UI And Data Trust Surface

**Files:**
- Modify: `app/web/backtest_common.py`
- Modify: `app/web/backtest_single_forms/strict_factor.py`
- Modify: `app/web/backtest_result_display.py`
- Test: `tests/test_service_contracts.py`

- [ ] **Step 1: Write failing tests** that UI labels distinguish Static, Approx Dynamic PIT, and PIT Monthly Snapshot.
- [ ] **Step 2: Add `PIT Monthly Snapshot Universe` contract option** and user-facing guidance.
- [ ] **Step 3: Render PIT universe data-trust summary** without presenting current Top-N as historical coverage.
- [ ] **Step 4: Run focused tests and commit.**

### Task 5: Documentation And QA

**Files:**
- Modify: `.aiworkspace/note/finance/docs/data/README.md`
- Modify: `.aiworkspace/note/finance/docs/data/TABLE_SEMANTICS.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/STRATEGY_IMPLEMENTATION_FLOW.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Modify: `.aiworkspace/note/finance/tasks/active/backtest-pit-universe-v1-20260707/*`

- [ ] **Step 1: Update durable docs** with implemented PIT universe contract and limits.
- [ ] **Step 2: Run compile, focused tests, diff check, and Browser QA if UI changed.**
- [ ] **Step 3: Commit documentation and QA closeout.**
