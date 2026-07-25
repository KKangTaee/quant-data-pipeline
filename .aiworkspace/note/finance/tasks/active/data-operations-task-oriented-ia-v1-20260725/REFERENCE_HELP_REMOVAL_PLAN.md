# Data Operations Reference Help Removal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the redundant `Reference help · Ingestion` panel from the top of Data Operations without changing the canonical Reference Center or any ingestion behavior.

**Architecture:** Keep the Reference catalog and destination unchanged. Add a source contract that forbids the contextual renderer in the Data Operations page, then remove only the renderer import and call from the page shell.

**Tech Stack:** Python 3.12, Streamlit, unittest, existing Finance Console Reference contracts.

## Global Constraints

- Preserve the canonical Reference Center and Ingestion catalog item.
- Preserve all Data Operations sections, actions, forms, collectors, DB, loaders, and explicit execution.
- Do not stage registry, run-history, research, `.superpowers`, or generated QA artifacts.
- Verify desktop and 420px mobile first-screen flow.

---

### Task 1: Remove The Contextual Panel

**Files:**
- Modify: `tests/test_data_operations_workflows.py`
- Modify: `tests/test_reference_contextual_help.py`
- Modify: `app/web/ingestion/page.py`
- Modify: `.aiworkspace/note/finance/tasks/active/data-operations-task-oriented-ia-v1-20260725/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/data-operations-task-oriented-ia-v1-20260725/RUNS.md`

**Interfaces:**
- Consumes: `render_ingestion_page(*, runtime_marker: str, loaded_at: datetime, git_sha: str | None) -> None`
- Produces: Data Operations title, caption, section navigation, and body without a contextual Reference renderer.
- Produces: a catalog-only surface contract for Market Research and Data Operations while preserving all six Reference help catalog entries.

- [x] **Step 1: Write the failing source-contract test**

```python
def test_data_operations_page_does_not_render_contextual_reference_help(self) -> None:
    page_source = Path("app/web/ingestion/page.py").read_text(encoding="utf-8")

    self.assertNotIn(
        "from app.web.reference_contextual_help import render_reference_contextual_help",
        page_source,
    )
    self.assertNotIn('render_reference_contextual_help("ingestion"', page_source)
```

- [x] **Step 2: Run the test and verify RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_data_operations_workflows.DataOperationsPageContractTest.test_data_operations_page_does_not_render_contextual_reference_help
```

Expected: FAIL because `page.py` still imports and calls the contextual renderer.

- [x] **Step 3: Remove the import and renderer call**

Delete only:

```python
from app.web.reference_contextual_help import render_reference_contextual_help
```

and:

```python
render_reference_contextual_help("ingestion", expanded=False)
```

- [x] **Step 4: Run focused regression tests**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_data_operations_workflows \
  tests.test_ingestion_module_split_contracts \
  tests.test_service_contracts.BoundaryContractHardeningTests
```

Expected: 60 tests pass.

- [x] **Step 5: Run Browser QA**

- 1280×720: title and caption are followed directly by the five-section navigation.
- 420×900: no `Reference help` text and no horizontal document overflow.
- Do not run a collector action.

- [x] **Step 6: Update closeout notes and commit**

```bash
git add \
  app/web/ingestion/page.py \
  tests/test_data_operations_workflows.py \
  .aiworkspace/note/finance/tasks/active/data-operations-task-oriented-ia-v1-20260725/REFERENCE_HELP_REMOVAL_PLAN.md \
  .aiworkspace/note/finance/tasks/active/data-operations-task-oriented-ia-v1-20260725/STATUS.md \
  .aiworkspace/note/finance/tasks/active/data-operations-task-oriented-ia-v1-20260725/RUNS.md
git commit -m "개선: Data Operations 상단 도움말 제거"
```
