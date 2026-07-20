# Portfolio Monitoring Reference Help Removal V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Portfolio Monitoring의 중복 contextual Reference panel과 전용 설정을 제거하고, 도움말 source-of-truth를 기존 Reference Center로 단일화한다.

**Architecture:** Portfolio Monitoring page는 React Command Center부터 바로 렌더링한다. Shared contextual-help service에서는 Portfolio Monitoring 전용 row만 제거하고, Reference Center의 모니터링 journey/scenario/stale playbook과 owner destination은 그대로 유지한다. 자동 계약은 “contextual entry 없음 + canonical Reference item 존재”를 동시에 검증한다.

**Tech Stack:** Python 3, Streamlit, unittest, React/Vite regression, Markdown finance docs, in-app Browser QA.

## Global Constraints

- `journey.monitoring`, `concept.monitoring_scenario`, `playbook.monitoring_scenario_stale`는 삭제하거나 변경하지 않는다.
- 위 세 Reference item의 `destination="portfolio_monitoring"`을 유지한다.
- 다른 contextual-help surface와 shared renderer는 변경하지 않는다.
- Portfolio Monitoring data/read model/command/DB/diagnosis/position event 계약은 변경하지 않는다.
- 새 대체 help CTA, 배너, 진단 패널을 만들지 않는다.
- generated QA screenshot은 stage하지 않는다.

---

### Task 1: Portfolio Monitoring contextual entry 제거

**Files:**
- Modify: `tests/test_reference_contextual_help.py:8-112`
- Modify: `app/services/reference_contextual_help.py:154-181`
- Modify: `app/web/final_selected_portfolio_dashboard.py:12,96,4354`

**Interfaces:**
- Consumes: `get_reference_contextual_help(surface_key: str) -> dict[str, Any] | None`
- Preserves: `get_reference_item(item_id: str) -> dict[str, Any] | None`
- Produces: `get_reference_contextual_help("portfolio_monitoring") is None` and a Portfolio Monitoring page source without `render_reference_contextual_help`

- [ ] **Step 1: Write the failing ownership test**

In `tests/test_reference_contextual_help.py`, remove `portfolio_monitoring` from `REQUIRED_CONTEXTUAL_SURFACES` and `OWNER_CALL_SITES`. Replace the Portfolio Monitoring defensive-copy test with a remaining surface and add this focused contract:

```python
    def test_contextual_help_lookup_returns_defensive_copy(self) -> None:
        from app.services.reference_contextual_help import get_reference_contextual_help

        help_item = get_reference_contextual_help("final_review")
        self.assertIsNotNone(help_item)
        assert help_item is not None
        self.assertEqual(help_item["surface"], "Final Review")
        self.assertIn("concept.selected_route_gate", help_item["reference_item_ids"])

        help_item["reference_item_ids"].append("mutated")
        fresh_item = get_reference_contextual_help("final_review")
        assert fresh_item is not None
        self.assertNotIn("mutated", fresh_item["reference_item_ids"])

    def test_portfolio_monitoring_help_is_owned_only_by_reference_center(self) -> None:
        from app.services.reference_center import get_reference_item
        from app.services.reference_contextual_help import get_reference_contextual_help

        self.assertIsNone(get_reference_contextual_help("portfolio_monitoring"))
        for item_id in (
            "journey.monitoring",
            "concept.monitoring_scenario",
            "playbook.monitoring_scenario_stale",
        ):
            item = get_reference_item(item_id)
            self.assertIsNotNone(item)
            assert item is not None
            self.assertEqual(item["destination"], "portfolio_monitoring")

        page_source = Path("app/web/final_selected_portfolio_dashboard.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("render_reference_contextual_help", page_source)
```

Change the drift assertion from the old surface count to the exact current contract:

```python
        self.assertEqual(
            report["metrics"]["surface_count"],
            len(REQUIRED_CONTEXTUAL_SURFACES),
        )
        self.assertGreaterEqual(report["metrics"]["reference_item_count"], 6)
```

- [ ] **Step 2: Run the focused RED test**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_reference_contextual_help.ReferenceContextualHelpContractTests.test_portfolio_monitoring_help_is_owned_only_by_reference_center -v
```

Expected: FAIL because the contextual catalog still returns the Portfolio Monitoring row and the page still imports/calls the renderer.

- [ ] **Step 3: Remove the Portfolio Monitoring contextual catalog row**

Delete only the dictionary at current lines 154-181 whose identity begins as follows from `REFERENCE_CONTEXTUAL_HELP`:

```python
    {
        "surface_key": "portfolio_monitoring",
        "surface": "Portfolio Monitoring",
        "title": "모니터링 시나리오가 stale이거나 비어 있을 때",
```

After deletion, the existing `final_review` row must be the last catalog entry. Verify this exact invariant in the GREEN test run:

```python
from app.services.reference_contextual_help import REFERENCE_CONTEXTUAL_HELP

assert REFERENCE_CONTEXTUAL_HELP[-1]["surface_key"] == "final_review"
```

- [ ] **Step 4: Remove both duplicate imports and the page call**

Delete both occurrences of:

```python
from app.web.reference_contextual_help import render_reference_contextual_help
```

Remove this line from `render_final_selected_portfolio_dashboard_page()`:

```python
    render_reference_contextual_help("portfolio_monitoring", expanded=False)
```

The function must begin its real workflow directly:

```python
def render_final_selected_portfolio_dashboard_page(
    *,
    services: PortfolioMonitoringPageServices | Any | None = None,
) -> None:
    """Render load -> React -> dispatch -> rerun with no legacy normal path."""

    runtime = services or _default_portfolio_monitoring_services()
```

- [ ] **Step 5: Run GREEN contract and page regression**

```bash
.venv/bin/python -m unittest tests.test_reference_contextual_help -v
.venv/bin/python -m unittest tests.test_reference_center -q
.venv/bin/python -m unittest tests.test_portfolio_monitoring_page -q
.venv/bin/python -m py_compile \
  app/services/reference_contextual_help.py \
  app/web/final_selected_portfolio_dashboard.py
git diff --check
```

Expected: contextual-help tests report the exact six-surface contract; Reference Center and Portfolio Monitoring page tests pass; compile and diff check exit 0.

- [ ] **Step 6: Review the scoped diff**

```bash
git diff -- \
  tests/test_reference_contextual_help.py \
  app/services/reference_contextual_help.py \
  app/web/final_selected_portfolio_dashboard.py
```

Confirm all of the following: no Portfolio Monitoring contextual row/import/call remains; canonical Reference Center code was not edited; the other six contextual surfaces are unchanged.

- [ ] **Step 7: Commit Task 1**

```bash
git add \
  tests/test_reference_contextual_help.py \
  app/services/reference_contextual_help.py \
  app/web/final_selected_portfolio_dashboard.py
git commit -m "개선: 포트폴리오 모니터링 도움말 패널 제거"
```

---

### Task 2: Browser QA와 durable documentation closeout

**Files:**
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md:79-80,133`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md:28,248-258`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/tasks/active/portfolio-monitoring-reference-help-removal-v1-20260721/{DESIGN,PLAN,STATUS,NOTES,RUNS,RISKS}.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Generate only: `portfolio-monitoring-reference-help-removal-qa.png`

**Interfaces:**
- Verifies: Portfolio Monitoring opens directly into its Command Center
- Verifies: canonical Reference monitoring items and `portfolio_monitoring` destination remain reachable
- Produces: durable current-state docs and task closeout without generated artifact commits

- [ ] **Step 1: Run the full proportional automation suite**

```bash
.venv/bin/python -m unittest \
  tests/test_reference_center.py \
  tests/test_reference_center_component.py \
  tests/test_reference_contextual_help.py -q
.venv/bin/python -m unittest discover -s tests -p 'test_portfolio_monitoring_*.py' -q
.venv/bin/python -m py_compile \
  app/services/reference_center.py \
  app/services/reference_contextual_help.py \
  app/web/reference_contextual_help.py \
  app/web/final_selected_portfolio_dashboard.py
cd app/web/streamlit_components/reference_center_workbench
npm test -- --run
npm run typecheck
npm run build
cd ../portfolio_monitoring_workbench
npm test -- --run
npm run typecheck
npm run build
cd ../../../..
git diff --check
```

Expected: all Python/React tests pass, both components typecheck/build, compile and diff check exit 0. Record exact counts in `RUNS.md`.

- [ ] **Step 2: Start the actual app for Browser QA**

Use an available local port and record it:

```bash
.venv/bin/python -m streamlit run app/web/streamlit_app.py \
  --server.headless true \
  --server.port 8517
```

Keep the session alive only for QA and stop it cleanly afterward.

- [ ] **Step 3: Verify Portfolio Monitoring first-read at desktop and mobile**

Using the in-app Browser and visible navigation:

1. open `Operations > Portfolio Monitoring`;
2. desktop: `Reference help · Portfolio Monitoring` is absent;
3. desktop: `PORTFOLIO COMMAND CENTER` and the group/KPI or empty state are the first product content;
4. desktop: page/browser console error count is zero;
5. 420px: the help panel remains absent and horizontal overflow is zero;
6. save one desktop screenshot as `portfolio-monitoring-reference-help-removal-qa.png` and do not stage it.

Expected DOM assertions:

```text
body does not contain: Reference help · Portfolio Monitoring
body contains: PORTFOLIO COMMAND CENTER
documentElement.scrollWidth <= documentElement.clientWidth
console error count == 0
```

- [ ] **Step 4: Verify canonical Reference preservation**

Navigate to the Reference page and verify these exact stable deep links or equivalent visible search results:

```text
/reference?item=journey.monitoring
/reference?item=concept.monitoring_scenario
/reference?item=playbook.monitoring_scenario_stale
```

For each item, verify its title opens and its owner action still targets Portfolio Monitoring. Do not mutate portfolio, registry, saved setup, or Reference data during QA.

- [ ] **Step 5: Synchronize durable docs and task state**

Apply these exact current-state changes:

```markdown
# PROJECT_MAP.md
- contextual help service: six surfaces, ending at Final Review
- Portfolio Monitoring owner row: remove "contextual Reference help entry point"

# BACKTEST_UI_FLOW.md
- "7개 주요 workflow 화면" -> "6개 주요 workflow 화면"
- "다음 7개 화면" -> "다음 6개 화면"
- remove only the Operations > Portfolio Monitoring contextual-help table row
- retain the Reference catalog and Portfolio Monitoring owner destination explanation
```

Update active task docs with 1차/2차 completion, exact test counts, desktop/mobile Browser assertions, canonical Reference preservation, and unverified gaps. Add one concise milestone to `WORK_PROGRESS.md`, one durable decision to `QUESTION_AND_ANALYSIS_LOG.md`, and a latest completed task pointer to `docs/INDEX.md`/`docs/ROADMAP.md`.

- [ ] **Step 6: Run final hygiene and commit Task 2**

```bash
.venv/bin/python -m unittest tests.test_reference_contextual_help -q
.venv/bin/python -m unittest tests.test_reference_center tests.test_reference_center_component -q
.venv/bin/python -m unittest discover -s tests -p 'test_portfolio_monitoring_*.py' -q
.venv/bin/python -m unittest tests.test_portfolio_monitoring_docs -q
git diff --check
git status --short
```

Expected: all tests pass; only intended docs are tracked changes; the QA screenshot and pre-existing local artifacts remain untracked.

```bash
git add \
  .aiworkspace/note/finance/docs/PROJECT_MAP.md \
  .aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md \
  .aiworkspace/note/finance/docs/INDEX.md \
  .aiworkspace/note/finance/docs/ROADMAP.md \
  .aiworkspace/note/finance/tasks/active/portfolio-monitoring-reference-help-removal-v1-20260721 \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "문서: 포트폴리오 모니터링 도움말 소유권 정리"
```

## Plan Self-Review

- Spec coverage: contextual call/config removal, canonical Reference preservation, other-surface isolation, contract update, Browser QA and docs closeout are mapped to Tasks 1-2.
- Placeholder scan: no placeholder marker, vague error-handling, or unspecified test step remains.
- Type/name consistency: all tasks use existing `get_reference_contextual_help`, `get_reference_item`, `render_final_selected_portfolio_dashboard_page` names and exact stable Reference IDs.
- Scope: no Reference catalog content rewrite, new CTA, Portfolio Monitoring domain change, or unrelated contextual-help audit is included.
