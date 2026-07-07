# Backtest Factor Readiness Panel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make strict Quality / Value factor strategy setup show one concise readiness decision and enforce a five-year maximum backtest window.

**Architecture:** Keep Streamlit strategy selection and forms as the owner of inputs. Add a Streamlit-free read model in `app/web/backtest_common.py`, render it with a UI-only React component, then reuse the same helper from Single Strategy and Portfolio Mix Builder strict annual blocks.

**Tech Stack:** Python, Streamlit, unittest service contracts, React + Vite Streamlit component.

---

### Task 1: Readiness Read Model

**Files:**
- Modify: `app/web/backtest_common.py`
- Modify: `tests/test_service_contracts.py`

- [ ] Write failing tests for `build_strict_factor_readiness_panel_model`.
- [ ] Run the focused tests and confirm failure.
- [ ] Implement the read model with base-universe, price, statement, and next-action groups.
- [ ] Run focused tests and commit.

### Task 2: React Component

**Files:**
- Create: `app/web/components/backtest_factor_readiness_panel/`
- Modify: `tests/test_service_contracts.py`

- [ ] Write failing component contract test.
- [ ] Add component wrapper, frontend, styles, and Vite config.
- [ ] Build frontend and run component contract.
- [ ] Commit.

### Task 3: Single Strategy Wiring

**Files:**
- Modify: `app/web/backtest_common.py`
- Modify: `app/web/backtest_single_forms/strict_factor.py`
- Modify: `tests/test_service_contracts.py`

- [ ] Write failing tests that annual strict forms call the new panel.
- [ ] Replace scattered annual strict preset/preflight rendering with the shared panel.
- [ ] Run focused tests and commit.

### Task 4: Five-Year Window Guard

**Files:**
- Modify: `app/web/backtest_common.py`
- Modify: `app/web/backtest_single_forms/strict_factor.py`
- Modify: `tests/test_service_contracts.py`

- [ ] Write failing tests for five-year validation.
- [ ] Add helper and apply it to annual strict forms.
- [ ] Run focused tests and commit.

### Task 5: Compare Builder, Docs, QA

**Files:**
- Modify: `app/web/backtest_compare/page.py`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: task logs

- [ ] Write failing tests that Portfolio Mix Builder strict annual blocks use the same readiness helper and five-year guard.
- [ ] Wire compare strict annual blocks.
- [ ] Run Python tests, React build, `git diff --check`, and browser QA.
- [ ] Update docs and commit.

