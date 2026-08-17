# Finance Documentation Flow Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align current finance documentation and Reference Center surface labels with the post-merge product flow while preserving retained history and compatibility names.

**Architecture:** Use the current app navigation as the user-facing source of truth and keep old `Overview`, `Ingestion`, and `Selected Portfolio Dashboard` terms only when they describe code modules, URLs, saved file names, job prefixes, old task history, or explicit compatibility. Update durable docs by ownership area instead of broad search-and-replace.

**Tech Stack:** Markdown documentation under `.aiworkspace/note/finance/docs/`, Python service/test files for Reference Center label contracts, `rg`, `git diff --check`, `py_compile`, and focused `pytest`.

## Global Constraints

- Current top navigation is `Research / Portfolio / Data / Help`.
- Current top-level surfaces are `Today`, `Market Research`, `Institutional Holdings`, `Portfolio Lab`, `Portfolio Monitoring`, `Data Operations`, `Reference Center`.
- Current Market Research views are `경기 국면`, `물가·정책`, `선물 매크로`, `심리`, `일정`, `S&P 500`, `변동 종목`, `개별 종목`.
- Route labels in current user-facing docs should use `Research > Market Research`, `Research > Institutional Holdings`, `Portfolio > Portfolio Lab`, `Portfolio > Portfolio Monitoring`, `Data > Data Operations`, and `Help > Reference Center`.
- Keep internal / compatibility identifiers such as `/overview`, `app/web/overview/*`, `overview_tab`, `app/jobs/overview_actions.py`, `app/web/ingestion_console.py`, `/selected-portfolio-dashboard`, `app/web/final_selected_portfolio_dashboard.py`, and `SELECTED_DASHBOARD_PORTFOLIOS.jsonl`.
- Do not bulk-edit retained task / phase history, registries, saved setup, generated screenshots, run history, or local artifacts.
- `docs/INDEX.md` is only for document discovery and canonical paths.
- `docs/ROADMAP.md` is only for current baseline, state, approved scope, and priority; do not add completed-task chronology.
- If Reference Center labels change, update tests in the same task and run the focused test file.

---

## Current Label Map

| Old user-facing label in current docs | New user-facing label | Keep old label when it means |
|---|---|---|
| `Workspace > Overview` | `Research > Market Research` | `/overview`, `app/web/overview/*`, Overview action/service/module prefix, old task history |
| `Workspace > Overview > Market Context` | `Research > Market Research > 시장 환경 > 경기 국면` or `Research > Market Research > 지수 가치평가 > S&P 500` depending context | old component/service names and retained history |
| `Workspace > Overview > Market Movers` | `Research > Market Research > 종목 리서치 > 변동 종목` | old service/job names and retained history |
| `Workspace > Overview > Sentiment` | `Research > Market Research > 시장 환경 > 심리` | old service/job names and retained history |
| `Workspace > Overview > Futures Macro` | `Research > Market Research > 시장 환경 > 선물 매크로` | old service/job names and retained history |
| `Workspace > Overview > Events` | `Research > Market Research > 시장 환경 > 일정` | old service/job names and retained history |
| `Workspace > Ingestion` | `Data > Data Operations` | `app/web/ingestion_console.py`, ingestion module names, old task history |
| `Workspace > Institutional Portfolios` | `Research > Institutional Holdings` | Python module names such as `institutional_portfolios` and old task history |
| `Operations > Portfolio Monitoring` | `Portfolio > Portfolio Monitoring` | old task history only |
| `Selected Portfolio Dashboard` | `Portfolio Monitoring` | implementation file names, saved JSONL names, migration docs, compatibility explanation |

## Task 1: Architecture Surface Vocabulary

**Files:**
- Modify: `.aiworkspace/note/finance/docs/architecture/README.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/SYSTEM_BOUNDARIES.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md`

**Interfaces:**
- Consumes: Current label map above and code ownership from `.aiworkspace/note/finance/docs/PROJECT_MAP.md`.
- Produces: Architecture docs that distinguish current product routes from internal compatibility names.

- [ ] **Step 1: Inspect stale architecture labels**

Run:

```bash
rg -n "Workspace > Overview|Workspace > Ingestion|Workspace > Institutional Portfolios|Operations > Portfolio Monitoring|Current primary tabs|Data Health|Futures Monitor|Sector / Industry" .aiworkspace/note/finance/docs/architecture -g '*.md'
```

Expected: Matches identify current-route text that needs targeted editing plus compatibility references that should stay.

- [ ] **Step 2: Update `architecture/README.md` current surface notes**

Replace the old `Workspace > Overview` current primary-tab bullet with a Market Research 3-family / 8-view summary. Keep the rule that `Futures Monitor` and `Sector / Industry` are not current primary surfaces.

- [ ] **Step 3: Update `SYSTEM_BOUNDARIES.md` product surface headings**

Rename current boundary sections to `Data > Data Operations`, `Research > Market Research`, `Research > Institutional Holdings`, and `Portfolio > Portfolio Monitoring`. Keep internal module references such as `Overview refresh buttons` only when they describe `app/jobs/overview_actions.py`.

- [ ] **Step 4: Update `DATA_DB_PIPELINE_FLOW.md` current-route rows**

Change user-facing surface rows and descriptions to current names. Use phrases like `Research > Market Research (internal Overview services)` when the row describes code still owned by `app/services/overview/*`.

- [ ] **Step 5: Verify architecture docs**

Run:

```bash
rg -n "Workspace > Overview|Workspace > Ingestion|Workspace > Institutional Portfolios|Operations > Portfolio Monitoring" .aiworkspace/note/finance/docs/architecture -g '*.md'
```

Expected: Remaining matches are compatibility or history explanations, not current route headings.

## Task 2: Data Docs Route Alignment

**Files:**
- Modify: `.aiworkspace/note/finance/docs/data/README.md`
- Modify: `.aiworkspace/note/finance/docs/data/DATA_FLOW_MAP.md`
- Modify if current-route text is stale: `.aiworkspace/note/finance/docs/data/STORAGE_GOVERNANCE.md`
- Modify if current-route text is stale: `.aiworkspace/note/finance/docs/data/TABLE_SEMANTICS.md`

**Interfaces:**
- Consumes: Architecture wording from Task 1.
- Produces: Data docs that route users to current surfaces without renaming DB tables, loaders, or code modules.

- [ ] **Step 1: Inspect stale data-doc labels**

Run:

```bash
rg -n "Workspace > Overview|Workspace > Ingestion|Operations > Portfolio Monitoring|Selected Portfolio Dashboard|Data Health" .aiworkspace/note/finance/docs/data -g '*.md'
```

Expected: Matches identify data-flow arrows and explanatory bullets that still use old user-facing paths.

- [ ] **Step 2: Update `DATA_FLOW_MAP.md` flow arrows**

Change current product arrows from old route labels to current route labels. Keep DB table names and loader names unchanged. For example, `Workspace > Overview > Market Movers` becomes `Research > Market Research > 종목 리서치 > 변동 종목` when describing where the user reads the data.

- [ ] **Step 3: Update data README / governance summaries**

Only edit lines that would mislead a reader about current navigation. Keep terms such as `Overview local run history` if they name a generated artifact or code path.

- [ ] **Step 4: Verify data docs**

Run:

```bash
rg -n "Workspace > Overview|Workspace > Ingestion|Operations > Portfolio Monitoring" .aiworkspace/note/finance/docs/data -g '*.md'
```

Expected: Remaining matches are explicitly internal, compatibility, or legacy notes.

## Task 3: Flow Docs Route Cleanup

**Files:**
- Modify: `.aiworkspace/note/finance/docs/flows/README.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify if needed: `.aiworkspace/note/finance/docs/flows/INSTITUTIONAL_PORTFOLIOS_FLOW.md`

**Interfaces:**
- Consumes: Current label map and Project Map route ownership.
- Produces: User-flow docs that describe current navigation while preserving legacy implementation names.

- [ ] **Step 1: Inspect flow-doc stale labels**

Run:

```bash
rg -n "Workspace > Overview|Workspace > Ingestion|Operations > Portfolio Monitoring|Selected Portfolio Dashboard|Futures Monitor|Sector / Industry|Data Health" .aiworkspace/note/finance/docs/flows -g '*.md'
```

Expected: Matches identify current-flow sentences, compatibility notes, and old task-history remnants embedded in flow docs.

- [ ] **Step 2: Update `flows/README.md` main flow**

Replace `Market Context / Market Movers / Portfolio Monitoring 기존 화면` with current `Market Research / Portfolio Monitoring` wording. Keep the note that soft-removed standalone tabs are not primary navigation.

- [ ] **Step 3: Update portfolio-selection monitoring route**

In `PORTFOLIO_SELECTION_FLOW.md`, replace current-route references to `Operations > Portfolio Monitoring` with `Portfolio > Portfolio Monitoring`. Preserve `Selected Portfolio Dashboard` only for legacy implementation file / saved setup explanation.

- [ ] **Step 4: Update `BACKTEST_UI_FLOW.md` high-value current sections**

Update route labels in the 핵심 파일 table, Practical Validation / Final Review guidance, Reference Center route table, and Portfolio Monitoring sections. Do not rewrite old redesign sections unless the text is presented as current behavior.

- [ ] **Step 5: Verify flow docs**

Run:

```bash
rg -n "Operations > Portfolio Monitoring|Workspace > Overview|Workspace > Ingestion" .aiworkspace/note/finance/docs/flows -g '*.md'
```

Expected: Remaining matches are compatibility notes or retained historical context, not current route instructions.

## Task 4: Runbook Current-Route Refresh

**Files:**
- Modify: `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md`
- Modify: `.aiworkspace/note/finance/docs/runbooks/EDGAR_FINANCIAL_STATEMENT_REFRESH.md`
- Modify: `.aiworkspace/note/finance/docs/runbooks/AUTOMATION_SCRIPTS.md`
- Modify if needed: `.aiworkspace/note/finance/docs/runbooks/PORTFOLIO_MONITORING_MIGRATION_AND_QA.md`
- Modify if needed: `.aiworkspace/note/finance/docs/runbooks/README.md`

**Interfaces:**
- Consumes: Current route labels from Tasks 1-3.
- Produces: Operating steps that tell users where to click today while preserving old CLI/module names.

- [ ] **Step 1: Inspect runbook stale labels**

Run:

```bash
rg -n "Workspace > Overview|Workspace > Ingestion|Operations > Portfolio Monitoring|Overview scheduled|Overview Market" .aiworkspace/note/finance/docs/runbooks -g '*.md'
```

Expected: Matches identify route instructions and CLI/module names.

- [ ] **Step 2: Update user action steps**

Change click paths such as `Workspace > Ingestion` to `Data > Data Operations` and `Workspace > Overview > Sentiment` to `Research > Market Research > 시장 환경 > 심리`.

- [ ] **Step 3: Preserve CLI/module names**

Keep names such as `overview_automation.py`, `overview_actions.py`, and `OVERVIEW_MARKET_INTELLIGENCE.md` when they identify code, jobs, files, or runbook filenames.

- [ ] **Step 4: Verify runbook docs**

Run:

```bash
rg -n "Workspace > Overview|Workspace > Ingestion|Operations > Portfolio Monitoring" .aiworkspace/note/finance/docs/runbooks -g '*.md'
```

Expected: Remaining matches are explicit compatibility explanations or old code/job names, not user click paths.

## Task 5: Reference Center Surface Label Contract

**Files:**
- Modify: `app/services/reference_center.py`
- Modify: `tests/test_reference_center.py`

**Interfaces:**
- Consumes: Current app labels from `app/web/streamlit_app.py`.
- Produces: Reference Center catalog and drift tests aligned with current product labels.

- [ ] **Step 1: Update required surface label sets**

Change required surfaces from `Overview`, `Institutional Portfolios`, and `Ingestion` to `Market Research`, `Institutional Holdings`, and `Data Operations`. Keep stage labels `Backtest Analysis`, `Practical Validation`, `Final Review`, and `Portfolio Monitoring`.

- [ ] **Step 2: Update catalog copy**

Replace user-facing `related_surfaces`, `category`, `meaning`, and `next_action` text that says `Overview`, `Institutional Portfolios`, or `Ingestion` with current labels. Keep keywords such as `overview` and `ingestion` only as search aliases when they help users find old terminology.

- [ ] **Step 3: Update tests**

Mirror the same required surface label set in `tests/test_reference_center.py`. Keep forbidden labels protecting removed or internal surfaces.

- [ ] **Step 4: Verify Reference Center contract**

Run:

```bash
.venv/bin/python -m py_compile app/services/reference_center.py app/web/reference_center.py
.venv/bin/python -m pytest tests/test_reference_center.py -q
```

Expected: `py_compile` succeeds and Reference Center tests pass.

## Task 6: Roadmap / Index / Project Map Sanity Pass

**Files:**
- Modify only if needed: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify only if needed: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify only if needed: `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md`
- Modify only if needed: `.aiworkspace/note/finance/docs/INDEX.md`

**Interfaces:**
- Consumes: Completed cleanup diffs from Tasks 1-5.
- Produces: Confirmation that top-level canonical docs remain aligned without becoming task chronology.

- [ ] **Step 1: Re-read top-level docs**

Run:

```bash
rg -n "Workspace > Overview|Workspace > Ingestion|Operations > Portfolio Monitoring|Overview|Ingestion|Market Research|Data Operations|Portfolio Monitoring" .aiworkspace/note/finance/docs/INDEX.md .aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md .aiworkspace/note/finance/docs/ROADMAP.md .aiworkspace/note/finance/docs/PROJECT_MAP.md
```

Expected: Current baseline docs use current labels for user-facing route descriptions.

- [ ] **Step 2: Update only actual drift**

Edit top-level docs only if they now contradict the code or the cleaned focused docs. Do not add completed task lists, detailed migration history, or speculative follow-ups.

- [ ] **Step 3: Record no-change decisions**

If `INDEX.md`, `PRODUCT_DIRECTION.md`, `ROADMAP.md`, or `PROJECT_MAP.md` do not need edits, record that in this task's `NOTES.md` or `STATUS.md`.

## Task 7: Final Validation, Task Closeout, And Commit

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/post-completion-doc-flow-diagnosis-20260817/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/post-completion-doc-flow-diagnosis-20260817/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/post-completion-doc-flow-diagnosis-20260817/NOTES.md`
- Modify if risk changes: `.aiworkspace/note/finance/tasks/active/post-completion-doc-flow-diagnosis-20260817/RISKS.md`

**Interfaces:**
- Consumes: All edited docs and focused test results.
- Produces: A coherent documentation refresh commit with generated artifacts unstaged.

- [ ] **Step 1: Run stale-label final scan**

Run:

```bash
rg -n "Workspace > Overview|Workspace > Ingestion|Operations > Portfolio Monitoring|Selected Portfolio Dashboard|Futures Monitor|Sector / Industry|Data Health" .aiworkspace/note/finance/docs app/services/reference_center.py tests/test_reference_center.py -g '*.md' -g '*.py'
```

Expected: Remaining matches are intentional compatibility, internal code names, forbidden-label guard tests, or retained history called out in task notes.

- [ ] **Step 2: Run conflict and whitespace checks**

Run:

```bash
rg -n "^(<<<<<<<|=======|>>>>>>>)" .aiworkspace/note/finance app tests
git diff --check
```

Expected: No conflict markers and no whitespace errors.

- [ ] **Step 3: Run focused code validation if Task 5 changed code**

Run:

```bash
.venv/bin/python -m py_compile app/services/reference_center.py app/web/reference_center.py
.venv/bin/python -m pytest tests/test_reference_center.py -q
```

Expected: Compile and tests pass.

- [ ] **Step 4: Update task docs**

Record edited document groups, validation commands, remaining intentional legacy terms, and any no-change decisions in `STATUS.md`, `RUNS.md`, `NOTES.md`, and `RISKS.md`.

- [ ] **Step 5: Inspect final status**

Run:

```bash
git status --short
```

Expected: Only intended documentation / Reference Center files are modified or added; QA screenshots remain unstaged.

- [ ] **Step 6: Commit coherent refresh**

Run:

```bash
git add .aiworkspace/note/finance/docs .aiworkspace/note/finance/tasks/active/post-completion-doc-flow-diagnosis-20260817 app/services/reference_center.py tests/test_reference_center.py
git commit -m "문서 플로우 최신화"
```

Expected: Commit succeeds and excludes generated screenshots, registries, saved setup, run history, and local artifacts.

## Self-Review

- Spec coverage: The plan covers tab-by-tab docs, current code flow docs, stale label cleanup, Reference Center label contract, validation, and closeout records.
- Placeholder scan: No red-flag placeholder steps remain.
- Type / label consistency: Current labels match `app/web/streamlit_app.py`; internal compatibility names are preserved only where the plan says to keep them.
