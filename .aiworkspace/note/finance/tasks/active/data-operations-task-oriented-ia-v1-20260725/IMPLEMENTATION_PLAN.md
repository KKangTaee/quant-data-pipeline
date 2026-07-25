# Data Operations Task-Oriented IA V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Replace the collector-first Ingestion landing page with a task-oriented Data Operations surface while preserving all existing ingestion actions, explicit execution, progress, artifacts, and compatibility dispatch.

**Architecture:** Add a pure workflow catalog that maps every active action to a consumer purpose, then render five explicit Data Operations views from a thin page shell. Existing operational/manual forms remain the single execution implementation and are reached through an action-focus handoff; history gets a separate compact renderer that filters to Data Operations actions and never exposes raw logs, failure CSV contents, full JSON, or absolute artifact paths.

**Tech Stack:** Python 3.12, Streamlit, unittest, existing ingestion registry/dispatcher/run-history contracts.

## Global Constraints

- Preserve `Ingestion -> DB -> Loader -> UI`; no provider fetch is added to render code.
- Preserve all 30 active actions and 4 compatibility actions.
- No DB schema, collector, provider, registry JSONL, or saved JSONL changes.
- Every write remains an explicit user click.
- No automatic multi-step execution, scheduler, background queue, live approval, broker order, or auto rebalance.
- Current snapshot and PIT evidence must remain semantically distinct.
- Do not add a raw run/job/row status dashboard.
- Do not stage existing registry, run-history, research, `.superpowers`, or QA image artifacts.

---

### Task 1: Pure Workflow Catalog

**Files:**
- Create: `app/web/ingestion/workflows.py`
- Modify: `app/web/ingestion/registry.py`
- Test: `tests/test_data_operations_workflows.py`

**Interfaces:**
- Consumes: `INGESTION_ACTION_REGISTRY`, `_active_ingestion_actions()`, `_compatibility_ingestion_actions()`.
- Produces:
  - `DATA_OPERATIONS_SECTION_PREPARATION`
  - `DATA_OPERATIONS_SECTION_IMPORTS`
  - `DATA_OPERATIONS_SECTION_RECOVERY`
  - `DATA_OPERATIONS_SECTION_HISTORY`
  - `DATA_OPERATIONS_SECTION_ADVANCED`
  - `DATA_OPERATIONS_SECTIONS: tuple[str, ...]`
  - `DATA_OPERATIONS_WORKFLOWS: tuple[dict[str, object], ...]`
  - `ACTION_WORKFLOW_OWNERSHIP: dict[str, tuple[str, ...]]`
  - `workflow_for_id(workflow_id: str) -> dict[str, object]`
  - `action_definition(action: str) -> dict[str, object]`
  - `validate_workflow_inventory() -> dict[str, object]`

- [x] **Step 1: Write the failing workflow inventory tests**

```python
class DataOperationsWorkflowContractTest(unittest.TestCase):
    def test_active_actions_are_owned_without_promoting_compatibility_actions(self) -> None:
        from app.web.ingestion.registry import active_ingestion_actions, compatibility_ingestion_actions
        from app.web.ingestion.workflows import ACTION_WORKFLOW_OWNERSHIP, validate_workflow_inventory

        result = validate_workflow_inventory()

        self.assertEqual(set(ACTION_WORKFLOW_OWNERSHIP), set(active_ingestion_actions()))
        self.assertEqual(result["active_action_count"], 30)
        self.assertEqual(result["unowned_actions"], ())
        self.assertEqual(result["unknown_actions"], ())
        self.assertTrue(set(compatibility_ingestion_actions()).isdisjoint(ACTION_WORKFLOW_OWNERSHIP))

    def test_shared_actions_keep_one_registry_identity(self) -> None:
        from app.web.ingestion.workflows import ACTION_WORKFLOW_OWNERSHIP

        self.assertEqual(
            ACTION_WORKFLOW_OWNERSHIP["daily_market_update"],
            ("market_research", "portfolio_lab"),
        )
        self.assertEqual(
            ACTION_WORKFLOW_OWNERSHIP["metadata_refresh"],
            ("market_research", "portfolio_lab"),
        )
```

- [x] **Step 2: Run tests and verify RED**

Run:

```bash
.venv/bin/python -m unittest tests.test_data_operations_workflows
```

Expected: import failure because `app.web.ingestion.workflows` does not exist.

- [x] **Step 3: Implement the pure catalog**

Use literal workflow definitions with these action ids:

```python
DATA_OPERATIONS_WORKFLOWS = (
    {
        "id": "market_research",
        "title": "Market Research 데이터 준비",
        "actions": (
            "refresh_nyse_listing_universe",
            "daily_market_update",
            "metadata_refresh",
            "collect_futures_ohlcv",
            "collect_market_sentiment",
            "collect_fomc_calendar",
            "collect_macro_calendar",
            "collect_market_structure_calendar",
            "collect_earnings_calendar",
        ),
    },
    {
        "id": "portfolio_lab",
        "title": "Portfolio Lab 데이터 준비",
        "actions": (
            "daily_market_update",
            "extended_statement_refresh",
            "metadata_refresh",
        ),
    },
    {
        "id": "institutional_holdings",
        "title": "Institutional Holdings 데이터 준비",
        "actions": (
            "collect_sec_13f_dataset",
            "collect_sec_13f_identifier_mappings",
        ),
    },
    {
        "id": "practical_validation",
        "title": "Practical Validation 데이터 보강",
        "actions": (
            "discover_etf_provider_source_map",
            "collect_etf_operability_provider",
            "collect_etf_holdings_exposure",
            "collect_macro_market_context",
            "collect_sec_form25_delistings",
            "collect_symbol_directory_snapshots",
            "collect_sec_company_ticker_crosscheck",
            "collect_computed_snapshot_lifecycle",
        ),
    },
)
```

Add official-import ownership for:

```python
("import_sp500_index_earnings_xlsx", "import_bls_macro_calendar_ics")
```

Add recovery ownership for the four diagnostic and four manual actions. Derive `ACTION_WORKFLOW_OWNERSHIP` once and validate it against `_active_ingestion_actions()`.

- [x] **Step 4: Run tests and verify GREEN**

```bash
.venv/bin/python -m unittest tests.test_data_operations_workflows tests.test_ingestion_module_split_contracts
```

Expected: all tests pass.

- [x] **Step 5: Commit Task 1**

```bash
git add app/web/ingestion/workflows.py app/web/ingestion/registry.py tests/test_data_operations_workflows.py
git commit -m "기능: Data Operations workflow catalog 추가"
```

---

### Task 2: Navigation State And Purpose Cards

**Files:**
- Create: `app/web/ingestion/navigation.py`
- Create: `app/web/ingestion/views/__init__.py`
- Create: `app/web/ingestion/views/preparation.py`
- Modify: `app/web/ingestion/page.py`
- Modify: `app/web/ingestion/styles.py`
- Test: `tests/test_data_operations_workflows.py`

**Interfaces:**
- Consumes: `DATA_OPERATIONS_SECTIONS`, `DATA_OPERATIONS_WORKFLOWS`, `_job_title()`, Streamlit session state.
- Produces:
  - `select_data_operations_section() -> str`
  - `select_data_operations_workflow() -> str | None`
  - `focus_data_operations_action(action: str) -> None`
  - `consume_focused_data_operations_action() -> str | None`
  - `render_preparation_view(*, on_action_focus: Callable[[str], None]) -> None`

- [x] **Step 1: Write failing state-transition tests**

Use a real dict as the state boundary:

```python
def test_action_focus_moves_to_advanced_without_losing_action() -> None:
    from app.web.ingestion.navigation import apply_action_focus
    from app.web.ingestion.workflows import DATA_OPERATIONS_SECTION_ADVANCED

    state: dict[str, object] = {}
    apply_action_focus(state, "collect_sec_13f_dataset")

    assert state["data_operations_section_choice"] == DATA_OPERATIONS_SECTION_ADVANCED
    assert state["data_operations_focused_action"] == "collect_sec_13f_dataset"
```

Add one test that rejects an unknown action with `KeyError`.

- [x] **Step 2: Run tests and verify RED**

```bash
.venv/bin/python -m unittest tests.test_data_operations_workflows
```

Expected: import failure because `navigation.py` does not exist.

- [x] **Step 3: Implement navigation state helpers**

`apply_action_focus(state, action)` must validate with `action_definition(action)` before mutating:

```python
def apply_action_focus(state: MutableMapping[str, object], action: str) -> None:
    action_definition(action)
    state["data_operations_section_choice"] = DATA_OPERATIONS_SECTION_ADVANCED
    state["data_operations_focused_action"] = action
```

Streamlit wrappers delegate to the pure function and call `st.rerun()` only from button callbacks.

- [x] **Step 4: Implement preparation cards**

Each card shows title, purpose, included data, cadence, and one `열기` button. Once selected, render the workflow's ordered steps with `_job_title(action)`, purpose, caveat, and `설정 열기`. Do not render runtime/build, raw counts, or a health dashboard.

- [x] **Step 5: Add responsive styles**

Add scoped classes:

```css
.data-ops-purpose-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; }
.data-ops-purpose-card { min-width:0; border:1px solid var(--secondary-background-color); border-radius:14px; padding:16px; }
@media (max-width: 640px) {
  .data-ops-purpose-grid { grid-template-columns:1fr; }
}
```

- [x] **Step 6: Run tests and verify GREEN**

```bash
.venv/bin/python -m unittest tests.test_data_operations_workflows tests.test_ingestion_module_split_contracts
.venv/bin/python -m py_compile app/web/ingestion/navigation.py app/web/ingestion/views/preparation.py app/web/ingestion/page.py
```

- [x] **Step 7: Commit Task 2**

```bash
git add app/web/ingestion/navigation.py app/web/ingestion/views/__init__.py app/web/ingestion/views/preparation.py app/web/ingestion/page.py app/web/ingestion/styles.py tests/test_data_operations_workflows.py
git commit -m "기능: Data Operations 목적별 준비 화면 추가"
```

---

### Task 3: Official Import, Recovery, And Advanced Views

**Files:**
- Create: `app/web/ingestion/views/imports.py`
- Create: `app/web/ingestion/views/recovery.py`
- Create: `app/web/ingestion/views/advanced.py`
- Modify: `app/web/ingestion/page.py`
- Modify: `app/web/ingestion/sections.py`
- Test: `tests/test_data_operations_workflows.py`
- Test: `tests/test_ingestion_module_split_contracts.py`

**Interfaces:**
- Consumes: workflow catalog, `render_operational_section()`, `render_manual_section()`, focused action state.
- Produces:
  - `render_imports_view(on_action_focus: Callable[[str], None]) -> None`
  - `render_recovery_view(on_action_focus: Callable[[str], None]) -> None`
  - `render_advanced_view(*, focused_action: str | None) -> Any`
  - `section_for_action(action: str) -> str`

- [x] **Step 1: Write failing routing tests**

```python
def test_official_import_and_recovery_actions_route_to_expected_legacy_section() -> None:
    from app.web.ingestion.views.advanced import section_for_action
    from app.web.ingestion.registry import INGESTION_COLLECTION_MANUAL, INGESTION_COLLECTION_OPERATIONAL

    assert section_for_action("import_sp500_index_earnings_xlsx") == INGESTION_COLLECTION_OPERATIONAL
    assert section_for_action("diagnose_price_stale") == INGESTION_COLLECTION_MANUAL
```

Add a test that unknown/compatibility-only actions raise `KeyError`.

- [x] **Step 2: Run tests and verify RED**

```bash
.venv/bin/python -m unittest tests.test_data_operations_workflows
```

Expected: import failure because the view modules do not exist.

- [x] **Step 3: Implement official import view**

Render only:

- `S&P 500 실제 EPS 등록`
- `BLS 공식 일정 가져오기`

Each item explains when to use it and calls `on_action_focus(action)`. It must not duplicate upload widgets or dispatcher calls.

- [x] **Step 4: Implement recovery view**

Render the four diagnostic actions first and the four manual write actions under `직접 복구 도구`. Each action calls the same focus handoff. State clearly that diagnosis is read-only and manual write actions remain explicit.

- [x] **Step 5: Implement advanced view**

Select operational/manual legacy form group from the focused action's registry section. Show one compact banner:

```text
선택한 작업: <user-facing title>
아래 고급 설정에서 범위와 preflight를 확인한 뒤 실행하세요.
```

Reuse existing `render_operational_section()` / `render_manual_section()` without duplicating action forms. Add `focused_action: str | None = None` parameters so the existing expander matching that action can open by default where practical; form behavior remains unchanged.

- [x] **Step 6: Run tests and verify GREEN**

```bash
.venv/bin/python -m unittest tests.test_data_operations_workflows tests.test_ingestion_module_split_contracts
.venv/bin/python -m py_compile app/web/ingestion/views/imports.py app/web/ingestion/views/recovery.py app/web/ingestion/views/advanced.py app/web/ingestion/sections.py
```

- [x] **Step 7: Commit Task 3**

```bash
git add app/web/ingestion/views/imports.py app/web/ingestion/views/recovery.py app/web/ingestion/views/advanced.py app/web/ingestion/page.py app/web/ingestion/sections.py tests/test_data_operations_workflows.py tests/test_ingestion_module_split_contracts.py
git commit -m "기능: Data Operations 가져오기와 복구 흐름 분리"
```

---

### Task 4: Compact Data Activity History

**Files:**
- Create: `app/web/ingestion/views/history.py`
- Modify: `app/web/ingestion/results.py`
- Modify: `app/web/ingestion/page.py`
- Test: `tests/test_data_operations_workflows.py`

**Interfaces:**
- Consumes: `load_run_history(limit: int)`, `_job_title()`, `ACTION_WORKFLOW_OWNERSHIP`.
- Produces:
  - `filter_data_operations_history(records: Sequence[dict[str, Any]]) -> list[dict[str, Any]]`
  - `build_data_activity_row(record: dict[str, Any]) -> dict[str, str]`
  - `render_history_view() -> None`

- [x] **Step 1: Write failing behavior tests**

```python
def test_history_filters_non_data_jobs_and_never_returns_raw_paths() -> None:
    from app.web.ingestion.views.history import build_data_activity_row, filter_data_operations_history

    records = [
        {"job_name": "daily_market_update", "status": "success", "started_at": "2026-07-26 00:00:00", "details": {"result_artifacts": {"json_path": "/tmp/private.json"}}},
        {"job_name": "portfolio_monitoring_price_refresh", "status": "success", "started_at": "2026-07-26 00:01:00"},
    ]

    filtered = filter_data_operations_history(records)
    row = build_data_activity_row(filtered[0])

    assert [item["job_name"] for item in filtered] == ["daily_market_update"]
    assert "json_path" not in row
    assert "/tmp/private.json" not in " ".join(row.values())
```

Add literal assertions for partial-success label and next-action copy.

- [x] **Step 2: Run tests and verify RED**

```bash
.venv/bin/python -m unittest tests.test_data_operations_workflows
```

Expected: import failure because `views/history.py` does not exist.

- [x] **Step 3: Implement pure history filtering and rows**

Only known active/compatibility action ids pass the filter. Use compact fields:

```python
{
    "실행 시각": "...",
    "작업": "...",
    "목적": "...",
    "상태": "...",
    "요청 범위": "...",
    "결과": "...",
    "다음 행동": "...",
}
```

Never copy `details`, log paths, failure CSV paths, full params, or artifact paths into the row.

- [x] **Step 4: Implement the history view**

Render a compact dataframe plus a selected record summary. Do not call:

- `_render_recent_results`
- `_render_recent_logs`
- `_render_failure_csv_preview`
- `_render_result_summary` when it exposes full JSON/artifacts

- [x] **Step 5: Run tests and verify GREEN**

```bash
.venv/bin/python -m unittest tests.test_data_operations_workflows
.venv/bin/python -m py_compile app/web/ingestion/views/history.py app/web/ingestion/results.py
```

- [x] **Step 6: Commit Task 4**

```bash
git add app/web/ingestion/views/history.py app/web/ingestion/results.py app/web/ingestion/page.py tests/test_data_operations_workflows.py
git commit -m "개선: Data Operations 실행 이력 간소화"
```

---

### Task 5: Replace The Legacy Landing Shell

**Files:**
- Modify: `app/web/ingestion/page.py`
- Modify: `app/web/ingestion/styles.py`
- Modify: `app/web/ingestion_console.py`
- Modify: `tests/test_ingestion_module_split_contracts.py`
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- Consumes: five explicit view renderers and navigation state.
- Produces: `render_ingestion_console()` as a thin Data Operations view dispatcher.

- [x] **Step 1: Replace obsolete source-string tests with behavior contracts**

Remove tests that require:

- the old three collection-section labels
- `_render_recent_logs()`
- `_render_failure_csv_preview()`
- old selected-section dispatch

Add import/contract tests for the five new view renderers and pure navigation behavior. Name each test after the user-visible break it catches.

- [x] **Step 2: Run focused tests and verify RED**

```bash
.venv/bin/python -m unittest tests.test_data_operations_workflows tests.test_ingestion_module_split_contracts
```

Expected: failures because the legacy landing shell still renders the old selector and clutter.

- [x] **Step 3: Implement the thin dispatcher**

`render_ingestion_console()` must:

1. render running banner
2. apply prefill notice
3. render five-section selector
4. dispatch one explicit view
5. execute scheduled job with the selected view's progress callback

It must not render runtime/build, the static workflow overview, the old common recent-result card, or the old `작업 영역` copy.

- [x] **Step 4: Align page identity**

Change:

```python
st.title("Ingestion")
```

to:

```python
st.title("Data Operations")
st.caption("Research와 Portfolio workflow가 읽는 데이터를 준비하고, 필요한 경우 누락 범위를 복구합니다.")
```

Keep the public compatibility facade and runtime metadata passed into run records.

- [x] **Step 5: Run focused and regression tests**

```bash
.venv/bin/python -m unittest tests.test_data_operations_workflows tests.test_ingestion_module_split_contracts
.venv/bin/python -m unittest \
  tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_console_module_owns_render_entrypoint \
  tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_console_delegates_read_only_diagnostics_to_service_facade \
  tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_ui_removes_legacy_broad_collection_cards_but_keeps_compatibility_actions \
  tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_running_jobs_preserve_section_and_show_elapsed_time \
  tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_progress_callback_allowlist_covers_stage_jobs_without_symbol_threshold
.venv/bin/python -m py_compile app/web/ingestion/*.py app/web/ingestion/views/*.py app/web/ingestion_console.py
git diff --check
```

- [x] **Step 6: Commit Task 5**

```bash
git add app/web/ingestion app/web/ingestion_console.py tests/test_data_operations_workflows.py tests/test_ingestion_module_split_contracts.py tests/test_service_contracts.py
git commit -m "개편: Data Operations 목적 중심 화면 전환"
```

---

### Task 6: Browser QA And Documentation Closeout

**Files:**
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/docs/flows/README.md`
- Modify: `.aiworkspace/note/finance/tasks/active/data-operations-task-oriented-ia-v1-20260725/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/data-operations-task-oriented-ia-v1-20260725/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/data-operations-task-oriented-ia-v1-20260725/RISKS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

**Interfaces:**
- Consumes: final implemented Data Operations behavior and Browser QA evidence.
- Produces: durable docs aligned to the new five-section workflow.

- [x] **Step 1: Run automated verification**

```bash
.venv/bin/python -m unittest tests.test_data_operations_workflows tests.test_ingestion_module_split_contracts
.venv/bin/python -m py_compile app/web/ingestion/*.py app/web/ingestion/views/*.py app/web/ingestion_console.py
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
git diff --check
```

- [x] **Step 2: Run Browser QA**

At `http://localhost:8501/ingestion` verify:

- desktop 1280x720 first viewport shows Data Operations and purpose entries
- mobile 420x900 first viewport reaches purpose entries
- five sections are reachable
- Market Research and Institutional Holdings steps route to Advanced
- recovery diagnosis route preserves manual section
- history excludes `portfolio_monitoring_price_refresh`
- raw log, failure CSV, full JSON, and absolute paths are absent
- horizontal overflow is 0
- console errors are 0

Save one generated QA screenshot outside the commit.

- [x] **Step 3: Apply finance-doc-sync**

Update the smallest durable doc set:

- product direction: task-oriented Data Operations role
- project map: new workflow/navigation/view modules
- flow README: consumer preparation routes
- roadmap/index: 3차 completion and 4차 durable execution candidate
- active task status/runs/risks
- root logs: 3–5 line handoff only

- [x] **Step 4: Run final verification**

```bash
git diff --check
.venv/bin/python -m unittest tests.test_data_operations_workflows tests.test_ingestion_module_split_contracts
git status --short
```

- [x] **Step 5: Commit Task 6**

```bash
git add .aiworkspace/note/finance/docs .aiworkspace/note/finance/tasks/active/data-operations-task-oriented-ia-v1-20260725 .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "문서: Data Operations 목적형 workflow 정렬"
```

Do not stage generated QA screenshots or unrelated local artifacts.
