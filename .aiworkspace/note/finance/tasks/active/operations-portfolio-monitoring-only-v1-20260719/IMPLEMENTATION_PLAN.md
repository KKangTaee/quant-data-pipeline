# Operations Portfolio Monitoring Only V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Operations에서 중복 `Operations Overview`와 사용하지 않는 `System / Data Health`를 제거하고 `Portfolio Monitoring`만 사용자-facing Operations 화면으로 남긴다.

**Architecture:** `app/web/streamlit_app.py`의 page graph를 단순화하고 두 전용 Streamlit 모듈을 삭제한다. 수집 실행 결과·history·log·failure CSV는 기존 `app/web/ingestion/` records section이 계속 소유하며, Portfolio Monitoring Python/React 계약과 저장 데이터는 변경하지 않는다.

**Tech Stack:** Python 3, Streamlit `st.navigation`, unittest, React/Vite Portfolio Monitoring regression, Markdown finance docs, in-app Browser QA.

## Global Constraints

- `Operations` group에는 `Portfolio Monitoring`만 남긴다.
- `/selected-portfolio-dashboard` route는 유지하고 `/operations`, `/ops-review` alias는 만들지 않는다.
- `app/web/operations_overview.py`와 `app/web/ops_review.py`는 숨겨 두지 않고 삭제한다.
- `Workspace > Ingestion > 실행 기록 / 결과`의 result, history, log, failure CSV 기능을 보존한다.
- Portfolio Monitoring에 run count, raw status table, log viewer, artifact path 패널을 추가하지 않는다.
- DB schema, registry, saved JSONL, run history, log, CSV, artifact 원본을 재작성하거나 삭제하지 않는다.
- Portfolio Monitoring의 DB-only loader/service, common-basis 계산, React visual hierarchy를 변경하지 않는다.
- historical task/research 기록은 일괄 치환하지 않고 current code, durable docs, Reference catalog만 정렬한다.
- 사용자 소유 untracked QA 이미지와 `.superpowers/`는 stage하지 않는다.

---

### Task 1: Portfolio Monitoring-only Navigation Contract

**Files:**

- Modify: `tests/test_service_contracts.py`
- Modify: `tests/test_portfolio_monitoring_page.py`
- Modify: `app/web/streamlit_app.py`
- Delete: `app/web/operations_overview.py`
- Delete: `app/web/ops_review.py`

**Interfaces:**

- Consumes: `render_final_selected_portfolio_dashboard_page()` and the existing `/selected-portfolio-dashboard` route.
- Produces: `"Operations": [selected_portfolio_dashboard_page]` with no Overview/Health imports or wrappers.
- Preserves: `app/web/ingestion/page.py::_render_ingestion_records_section()` and its four child renderers.

- [x] **Step 1: Write the failing navigation test**

Remove the `build_operations_overview_model` tests and replace the old navigation assertion with:

```python
def test_operations_navigation_contains_only_portfolio_monitoring(self) -> None:
    source = Path("app/web/streamlit_app.py").read_text(encoding="utf-8")
    operations_block = source.split('"Operations": [', 1)[1].split("],", 1)[0]

    self.assertIn("selected_portfolio_dashboard_page", operations_block)
    self.assertNotIn("operations_overview_page", operations_block)
    self.assertNotIn("ops_review_page", operations_block)
    self.assertNotIn("app.web.operations_overview", source)
    self.assertNotIn("app.web.ops_review", source)

def test_ingestion_records_preserve_run_log_and_failure_review(self) -> None:
    source = Path("app/web/ingestion/page.py").read_text(encoding="utf-8")

    self.assertIn("def _render_ingestion_records_section", source)
    self.assertIn("_render_recent_results()", source)
    self.assertIn("_render_persistent_run_history()", source)
    self.assertIn("_render_recent_logs()", source)
    self.assertIn("_render_failure_csv_preview()", source)
```

Delete `test_operations_summary_prefers_new_group_and_value_metrics_and_keeps_navigation` from `tests/test_portfolio_monitoring_page.py`; it tests the removed landing model.

- [x] **Step 2: Run RED verification**

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_navigation_contains_only_portfolio_monitoring \
  tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_ingestion_records_preserve_run_log_and_failure_review
```

Expected: the navigation test fails because both old pages/imports still exist; the Ingestion preservation test passes.

- [x] **Step 3: Remove the two pages and modules**

In `app/web/streamlit_app.py`, remove both imports, `LOG_DIR`, `CSV_DIR`, `_render_ops_review_page()`, both obsolete `st.Page` definitions, and the Overview `page_targets`. Replace the Operations block with:

```python
"Operations": [
    selected_portfolio_dashboard_page,
],
```

Keep the existing Portfolio Monitoring page definition and `/selected-portfolio-dashboard` route unchanged. Delete the complete files `app/web/operations_overview.py` and `app/web/ops_review.py`. Do not delete job history/artifact modules or stored files.

- [x] **Step 4: Run GREEN verification**

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_operations_navigation_contains_only_portfolio_monitoring \
  tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests.test_ingestion_records_preserve_run_log_and_failure_review \
  tests.test_portfolio_monitoring_page
.venv/bin/python -m py_compile app/web/streamlit_app.py app/web/ingestion/page.py
git diff --check
```

Expected: all tests pass, compile exits `0`, and diff check is clean.

- [x] **Step 5: Commit Task 1**

```bash
git add app/web/streamlit_app.py app/web/operations_overview.py app/web/ops_review.py tests/test_service_contracts.py tests/test_portfolio_monitoring_page.py
git commit -m "Operations를 포트폴리오 모니터링으로 단순화"
```

### Task 2: Current Reference And Product Flow Alignment

**Files:**

- Modify: `tests/test_reference_guides_catalog.py`
- Modify: `tests/test_reference_contextual_help.py`
- Modify: `tests/test_service_contracts.py`
- Modify: `app/services/reference_contextual_help.py`
- Modify: `app/services/reference_glossary_catalog.py`
- Modify: `app/services/reference_guides_catalog.py`
- Modify: `app/services/overview/ia.py`
- Modify: `app/services/overview/market_context.py`
- Modify: `app/web/backtest_candidate_library.py`
- Modify: `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/SYSTEM_BOUNDARIES.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/PORTFOLIO_MONITORING_REACT_COMMAND_CENTER.md`
- Modify: `.aiworkspace/note/finance/docs/flows/README.md`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/data/DATA_FLOW_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md`
- Modify: `.aiworkspace/note/finance/docs/runbooks/README.md`
- Delete: `.aiworkspace/note/finance/docs/runbooks/OPERATIONS_OVERVIEW_QA.md`

**Interfaces:**

- Consumes: `Workspace > Ingestion > 실행 기록 / 결과` as the only run/log/failure destination.
- Produces: current Reference/docs with `Operations > Portfolio Monitoring` as the only Operations destination.

- [x] **Step 1: Write failing current-reference tests**

Use these assertions in `tests/test_reference_guides_catalog.py`:

```python
self.assertEqual(data_freshness["owner_screen"], "Workspace > Ingestion > 실행 기록 / 결과")
self.assertNotIn("System / Data Health", str(catalog))
self.assertEqual(
    data_failures["UI가 최신 수집 결과를 못 읽음"]["owner_screen"],
    "Workspace > Ingestion > 실행 기록 / 결과",
)
```

Use these assertions in `tests/test_reference_contextual_help.py`:

```python
self.assertGreaterEqual(
    surface_keys,
    {"backtest_analysis", "practical_validation", "final_review", "portfolio_monitoring"},
)
self.assertNotIn("operations_console", surface_keys)
self.assertGreaterEqual(report["metrics"]["surface_count"], 4)
```

Change the Overview IA contract in `tests/test_service_contracts.py` to:

```python
self.assertEqual(data_section["owner"], "Workspace > Ingestion > 실행 기록 / 결과")
self.assertNotIn("System / Data Health", str(model))
```

- [x] **Step 2: Run RED verification**

```bash
.venv/bin/python -m unittest \
  tests.test_reference_guides_catalog \
  tests.test_reference_contextual_help \
  tests.test_service_contracts.OverviewAutomationContractTests.test_overview_ia_closeout_model_demotes_ops_surfaces_from_primary_tabs
```

Expected: failures show the old health destination and `operations_console` key.

- [x] **Step 3: Align current service-owned destinations**

Delete the complete `surface_key == "operations_console"` catalog item. Replace current destinations containing `System / Data Health` with `Workspace > Ingestion > 실행 기록 / 결과` in the listed Reference/Overview services. Use this exact Data Trust copy:

```text
Workspace > Ingestion > 실행 기록 / 결과에서 source 상태와 실패 원인을 확인합니다.
```

Do not add fields, panels, or collection behavior.

In the hidden compatibility `app/web/backtest_candidate_library.py`, replace the obsolete Operations Console positioning sentence with:

```text
현재 주 workflow에서는 이 화면을 primary monitoring이 아니라 archive / recovery 도구로 취급합니다.
```

- [x] **Step 4: Run reference GREEN verification**

Run the Step 2 command again. Expected: all tests pass and contextual-help drift remains `PASS`.

- [x] **Step 5: Align durable current-state documentation**

- Remove the two deleted script rows and current route descriptions.
- Define Operations as Portfolio Monitoring only.
- Route collection failure/history/log review to `Workspace > Ingestion > 실행 기록 / 결과`.
- Remove Operations Console from the main user flow so Final Review leads directly to Portfolio Monitoring.
- Delete `docs/runbooks/OPERATIONS_OVERVIEW_QA.md` and its runbook index entries.
- Keep only an explicitly labeled superseded/history note in ROADMAP; do not rewrite historical tasks, research, or old root-log milestones.

- [x] **Step 6: Verify references and commit Task 2**

```bash
rg -n -S "Operations Overview|Operations Console|System / Data Health|ops-review|/operations" \
  app .aiworkspace/note/finance/docs \
  --glob '!**/component_static/**'
.venv/bin/python -m unittest tests.test_reference_guides_catalog tests.test_reference_contextual_help
.venv/bin/python -m py_compile \
  app/services/reference_contextual_help.py \
  app/services/reference_glossary_catalog.py \
  app/services/reference_guides_catalog.py \
  app/services/overview/ia.py \
  app/services/overview/market_context.py
git diff --check
```

Expected: no current code reference remains; docs contain at most a labeled superseded ROADMAP note; tests/compile/diff check pass.

```bash
git add app/services tests/test_reference_guides_catalog.py tests/test_reference_contextual_help.py tests/test_service_contracts.py .aiworkspace/note/finance/docs
git commit -m "Operations 현재 문서와 안내 경로 정리"
```

### Task 3: Full Verification, Browser QA, And Closeout

**Files:**

- Modify: task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Create locally only: `operations-portfolio-monitoring-only-qa.png`

**Interfaces:**

- Consumes: Task 1 page graph and Task 2 reference alignment.
- Produces: verified `3/3차` closeout with a non-committed QA screenshot.

- [x] **Step 1: Run focused Python and React regressions**

```bash
.venv/bin/python -m unittest \
  tests.test_portfolio_monitoring_page \
  tests.test_reference_guides_catalog \
  tests.test_reference_contextual_help \
  tests.test_service_contracts.SelectedPortfolioMonitoringTimelineContractTests
```

In `app/web/streamlit_components/portfolio_monitoring_workbench` run:

```bash
npm test -- --run
npm run typecheck
npm run build
```

Expected: Python/Vitest pass and typecheck/build exit `0`.

- [x] **Step 2: Run static policy checks**

```bash
.venv/bin/python -m py_compile app/web/streamlit_app.py app/web/ingestion/page.py app/web/final_selected_portfolio_dashboard.py
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py
git diff --check
git status --short
```

Expected: all checks pass; only scoped changes and pre-existing untracked artifacts remain.

- [x] **Step 3: Perform Browser QA**

Start Streamlit on port `8524`, then verify:

1. Operations contains only Portfolio Monitoring.
2. It opens `/selected-portfolio-dashboard` without a routing dialog.
3. no Overview/Health item is visible.
4. Portfolio Monitoring keeps its current React one-shell layout.
5. Ingestion `실행 기록 / 결과` still exposes recent result, history, logs, and failure CSV.

Save `/Users/taeho/Project/quant-data-pipeline-worktrees/main-dev/operations-portfolio-monitoring-only-qa.png` and do not stage it.

- [x] **Step 4: Close task docs and commit**

Record exact test counts and Browser QA result, set task status to `Complete`, roadmap to `3/3차`, and add 3–5 concise handoff lines to each root log. Run `git diff --check` and `git status --short`, then commit scoped docs as:

```bash
git commit -m "Operations 포트폴리오 모니터링 전환 완료"
```

## Final Stop Condition

Operations에는 Portfolio Monitoring만 보이고, Ingestion 기록 기능은 보존되며, 제거된 두 surface의 current code/reference가 남지 않고, Python/React/static checks와 actual Browser QA가 모두 통과해야 전체 `3/3차 완료`로 표시한다.
