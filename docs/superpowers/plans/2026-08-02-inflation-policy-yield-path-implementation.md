# Inflation Policy Yield Path Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the approved U.S. Core PCE → FOMC policy → Treasury yield resistance → conditional asset-stress workflow, while creating a separately gated raw-data recession model.

**Architecture:** Deliver the approved design as five independently reviewable implementation plans. Data and point-in-time storage land first; probabilistic engines consume only those DB contracts; the workbench reads persisted snapshots and runs DB-only reverse scenarios; equity stress and recession remain separate extensions with their own publication gates.

**Tech Stack:** Python 3.12, pandas, NumPy, MySQL, Streamlit, React 18, TypeScript 5.7, Vite 6, pytest-style tests.

## Global Constraints

- Never use existing economic-cycle probabilities, factors, snapshots, labels, or artifacts as an input, fallback, training label, or verification target.
- Preserve `Ingestion -> DB -> Loader -> Service -> UI`; no provider call from Streamlit or React rendering.
- Store `observation_date`, `released_at`, `collected_at`, and calculation `as_of_at` separately and reject observations released after the cutoff.
- Store SEP distributions anonymously; never create or infer a participant-level mapping between rate dots and inflation projections.
- Calculate SEP Core PCE as index-based `Q4/Q4`, not by adding monthly percentages or using December year-over-year.
- Treat 4.7%, 3.5%, 0.4–0.5%, and S&P 500 6,400 as dated/user scenarios, never global constants or deterministic triggers.
- A 10-year yield breakout alone cannot become an inflation confirmation; breakeven, real yield, term premium, and Core PCE evidence must be evaluated separately.
- Exact probabilities appear only for `READY` artifacts; `LIMITED`, `NOT_AVAILABLE`, and `FAILED` never reuse a last-good value as current.
- Preserve user-owned dirty-worktree changes and generated artifacts; stage only files named by the active task.
- Use Korean commit messages and one coherent commit per independently testable task.

---

## Plan Set And Dependency Order

| Order | Plan | Working deliverable | Hard gate before next plan |
| ---: | --- | --- | --- |
| 1 | [Data Pipeline](./2026-08-02-inflation-policy-data-pipeline-implementation.md) | Official SEP/FOMC/PCE/rates/term-premium data with strict as-of loaders | Parser fixtures, schema, PIT cutoff, real-source smoke |
| 2 | [Core Engines](./2026-08-02-inflation-policy-core-engines-implementation.md) | Core PCE, policy, resistance, forward/reverse probability artifacts | Rolling-origin baselines, calibration, 2026 replay |
| 3 | [Workbench](./2026-08-02-inflation-policy-workbench-implementation.md) | DB-only forward/reverse user workflow | Python contracts, React build, desktop/mobile Browser QA |
| 4 | [Equity Stress](./2026-08-02-inflation-policy-equity-stress-implementation.md) | EPS × multiple conditional S&P 500 range and AI EPS assumption | PIT event study and non-causal copy checks |
| 5 | [Recession Risk](./2026-08-02-recession-risk-engine-implementation.md) | New raw-data 0/3/6/12-month recession-risk model | Independent validation; no existing-cycle import |

## Master Execution Tasks

### Task 1: Execute the point-in-time data foundation

**Files:**
- Follow: `docs/superpowers/plans/2026-08-02-inflation-policy-data-pipeline-implementation.md`
- Track: `.aiworkspace/note/finance/phases/active/inflation-policy-yield-path/`

**Interfaces:**
- Consumes: approved design `docs/superpowers/specs/2026-08-02-inflation-policy-yield-path-design.md`
- Produces: `InflationPolicyDataBundle` loaders and durable raw/result schemas used by every later plan.

- [ ] **Step 1: Run the complete data-pipeline plan task-by-task**

Use the tests and commits in the data-pipeline plan without combining commits.

- [ ] **Step 2: Run the phase gate**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_inflation_policy_schema.py \
  tests/test_fred_vintages.py \
  tests/test_fomc_policy_data.py \
  tests/test_inflation_policy_loaders.py \
  tests/test_inflation_policy_refresh.py -q
```

Expected: all tests pass; the 2026-07-29 14:00 ET fixture excludes the 2026-07-30 Core PCE release.

- [ ] **Step 3: Review the data contract before model work**

Confirm the stored June 2026 SEP fixture contains six participants in the 2–3 hike path, four in the Core PCE 3.5–3.6 bin, and no `participant_id` column or generated mapping.

### Task 2: Execute the Core PCE, policy, and yield engines

**Files:**
- Follow: `docs/superpowers/plans/2026-08-02-inflation-policy-core-engines-implementation.md`

**Interfaces:**
- Consumes: `InflationPolicyDataBundle`, persisted SEP/decision distributions, market-series as-of frames.
- Produces: versioned `inflation_policy_model_artifact`, `inflation_policy_snapshot`, and resistance snapshots.

- [ ] **Step 1: Run the complete core-engine plan task-by-task**

Keep the PCE, FOMC, resistance, simulation, and validation commits independently reviewable.

- [ ] **Step 2: Run the engine phase gate**

Run:

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_*.py tests/test_yield_resistance.py -q
```

Expected: all tests pass; probability simplexes sum to 1; the 2026 index-path examples reproduce 3.17%, 3.50%, and the one-shock ranges from the approved design.

- [ ] **Step 3: Inspect publication decisions**

Run the core plan's 2026 replay command and confirm failed or under-sampled components publish `LIMITED`/`NOT_AVAILABLE`, never fabricated exact probabilities.

### Task 3: Execute the decision workbench

**Files:**
- Follow: `docs/superpowers/plans/2026-08-02-inflation-policy-workbench-implementation.md`

**Interfaces:**
- Consumes: stored snapshots, resistance definitions, model artifacts, DB-only reverse-scenario service.
- Produces: `경기 국면 | 물가·정책 경로` inner workflow with forward, preparation, policy, resistance, reverse, and evidence views.

- [ ] **Step 1: Run the complete workbench plan task-by-task**

Do not add a run/row/status operations panel; quality metadata remains supporting evidence.

- [ ] **Step 2: Run Python and React gates**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_inflation_policy_service.py \
  tests/test_market_context_inflation_policy.py \
  tests/test_inflation_policy_commands.py -q
npm --prefix app/web/streamlit_components/economic_cycle_workbench run build
```

Expected: tests and build pass; tracked `component_static` is regenerated.

- [ ] **Step 3: Complete Browser QA**

Verify desktop and 420px widths, forward/reverse switching, saved custom criteria, unavailable states, no horizontal overflow, and zero console/page errors. Save one generated screenshot outside the commit.

### Task 4: Execute conditional S&P 500 stress

**Files:**
- Follow: `docs/superpowers/plans/2026-08-02-inflation-policy-equity-stress-implementation.md`

**Interfaces:**
- Consumes: yield simulation paths and stored S&P 500 actual/estimate EPS vintages.
- Produces: conditional index distribution, target-level reverse decomposition, and explicit user AI EPS uplift assumption.

- [ ] **Step 1: Run the complete equity-stress plan task-by-task**

Keep AI profitability as an explicit EPS assumption unless stored earnings revisions provide measured evidence.

- [ ] **Step 2: Run the equity phase gate**

Run:

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_equity_stress.py tests/test_inflation_policy_service.py -q
npm --prefix app/web/streamlit_components/economic_cycle_workbench run build
```

Expected: all tests and build pass; 6,400 is accepted only as a user target, not emitted as a hard-coded forecast.

### Task 5: Execute the independently gated recession model

**Files:**
- Follow: `docs/superpowers/plans/2026-08-02-recession-risk-engine-implementation.md`

**Interfaces:**
- Consumes: raw point-in-time labor, income, consumption, production, sales, curve, spread, and financial-condition observations.
- Produces: separate 0/3/6/12-month five-state recession-risk snapshots.

- [ ] **Step 1: Run the complete recession plan task-by-task**

Do not import an existing economic-cycle package from any `finance/recession_risk/` module.

- [ ] **Step 2: Run the independent phase gate**

Run:

```bash
.venv/bin/python -m pytest tests/test_recession_risk_*.py tests/test_inflation_policy_service.py -q
! rg -n "finance\.economic_cycle|economic_cycle_snapshot|economic_cycle_model_artifact" \
  finance/recession_risk app/services/overview/recession_risk.py
```

Expected: tests pass and `rg` returns no matches. If the validation artifact is not `READY`, the UI remains `NOT_AVAILABLE`.

### Task 6: Close the full phase

**Files:**
- Modify: `.aiworkspace/note/finance/phases/active/inflation-policy-yield-path/STATUS.md`
- Modify: `.aiworkspace/note/finance/phases/active/inflation-policy-yield-path/TASKS.md`
- Modify: `.aiworkspace/note/finance/phases/active/inflation-policy-yield-path/INTEGRATION.md`
- Modify only when ownership changed: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify only when product direction changed: `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md`
- Modify only when baseline/priority changed: `.aiworkspace/note/finance/docs/ROADMAP.md`

**Interfaces:**
- Consumes: verified outputs and QA evidence from Tasks 1–5.
- Produces: durable finance documentation and a truthful phase state.

- [ ] **Step 1: Use `finance-doc-sync` to classify durable changes**

Record focused data/architecture/flow/runbook changes and explicitly record `canonical doc change 없음` for canonical files whose owned facts did not change.

- [ ] **Step 2: Run the full verification matrix**

Run:

```bash
git diff --check
.venv/bin/python -m pytest tests/test_inflation_policy_*.py tests/test_yield_resistance.py tests/test_recession_risk_*.py -q
npm --prefix app/web/streamlit_components/economic_cycle_workbench run build
git status --short
```

Expected: all tests/builds pass; only intentional source, test, tracked static, and finance documentation files are staged.

- [ ] **Step 3: Mark the phase accurately**

Use `State: complete` only if all six roadmap completion criteria are met. Otherwise keep `State: active` or `verification_only` and list the exact remaining gate.

- [ ] **Step 4: Commit closeout documentation**

```bash
git add .aiworkspace/note/finance/phases/active/inflation-policy-yield-path \
  .aiworkspace/note/finance/docs/PROJECT_MAP.md \
  .aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md \
  .aiworkspace/note/finance/docs/ROADMAP.md
git commit -m "인플레이션 정책 경로 개발 단계 정리"
```
