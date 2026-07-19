# Futures Macro Ribbon / Asset Status / V4 Runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the 60-day regime colors self-explanatory, clarify that asset-card future badges inherit the overall horizon status, and restore the compatible V4 ten-year snapshot in `sub-dev`.

**Architecture:** React remains a presentation-only consumer of the existing Python payload. The ribbon legend is static UI metadata matching existing CSS regime tokens; asset cards retain `observation_status` and horizon-owned `five_day_status` / `twenty_day_status` but label the latter as overall outlook status. Snapshot restoration uses the existing materializer and stored daily OHLCV without changing prediction logic or schema.

**Tech Stack:** Python 3.12 `unittest`, React 18, TypeScript, Vite, Streamlit custom component, MySQL persisted compact snapshot.

## Global Constraints

- Modify only the `sub-dev` worktree.
- Do not change model features, probabilities, Brier / calibration / path gates, or outcome thresholds.
- Do not add family-specific forecast validation.
- Do not modify the DB schema or snapshot unique key in this task.
- Use stored recent maximum ten-year futures daily OHLCV; do not require a provider fetch for restoration.
- Preserve `OBSERVED/PARTIAL/UNAVAILABLE` for current facts and `VERIFIED/PROVISIONAL/UNAVAILABLE` for future distributions.
- Do not stage generated screenshots or unrelated untracked files.

---

### Task 1: Visible 60-Day Regime Legend

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/PatternRibbonSection.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/style.css`

**Interfaces:**
- Consumes: existing `RibbonPayload` and CSS classes `regime-risk_seeking`, `regime-defensive`, `regime-inflation_rate_pressure`, `regime-mixed`, `transition-transition_attempt`.
- Produces: a visible, text-labelled legend and `과거 → 최근` direction copy without changing payload shape.

- [ ] **Step 1: Write the failing source contract**

Add to `OverviewAutomationContractTests`:

```python
def test_futures_macro_ribbon_has_visible_regime_legend(self) -> None:
    root = Path("app/web/streamlit_components/futures_macro_workbench/src")
    ribbon = (root / "PatternRibbonSection.tsx").read_text(encoding="utf-8")
    style = (root / "style.css").read_text(encoding="utf-8")

    for label in ("위험선호", "방어", "물가·금리 부담", "혼재", "전환 시도"):
        self.assertIn(label, ribbon)
    self.assertIn("과거 → 최근", ribbon)
    for class_name in (
        "legend-risk_seeking",
        "legend-defensive",
        "legend-inflation_rate_pressure",
        "legend-mixed",
        "legend-transition",
    ):
        self.assertIn(class_name, style)
```

- [ ] **Step 2: Run RED**

Run:

```bash
.venv/bin/python -m unittest -v tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_ribbon_has_visible_regime_legend
```

Expected: FAIL because the legend labels and CSS classes do not exist.

- [ ] **Step 3: Implement the minimal legend**

In `PatternRibbonSection.tsx`, add below the ribbon cells:

```tsx
<div className="fm-workbench__ribbon-legend" aria-label="최근 60거래일 체제 색상 범례">
  <small>과거 → 최근</small>
  <span className="legend-risk_seeking"><i />위험선호</span>
  <span className="legend-defensive"><i />방어</span>
  <span className="legend-inflation_rate_pressure"><i />물가·금리 부담</span>
  <span className="legend-mixed"><i />혼재</span>
  <span className="legend-transition"><i />전환 시도</span>
</div>
```

In `style.css`, add compact flex wrapping and matching swatches. `legend-transition i` uses the same repeating diagonal gradient as transition cells.

- [ ] **Step 4: Run GREEN**

Run the Task 1 test again. Expected: PASS.

- [ ] **Step 5: Commit Task 1**

```bash
git add tests/test_service_contracts.py app/web/streamlit_components/futures_macro_workbench/src/PatternRibbonSection.tsx app/web/streamlit_components/futures_macro_workbench/src/style.css
git commit -m "선물 매크로 60일 체제 범례 추가"
```

### Task 2: Clarify Asset Current And Overall Outlook Status

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/AssetPathwaysSection.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/style.css`

**Interfaces:**
- Consumes: `AssetPathwayPayload.observation_status` and `outlook.five_day_status` / `outlook.twenty_day_status`.
- Produces: current observation badge in the card header and future badges labelled `전체 전망 · <status>`.

- [ ] **Step 1: Extend the failing source contract**

Add these assertions to `test_futures_macro_react_separates_observation_and_outlook_statuses`:

```python
self.assertIn("OBSERVATION_LABEL[item.observation_status]", assets)
self.assertIn("전체 전망 ·", assets)
self.assertIn("item.outlook.five_day_status", assets)
self.assertIn("item.outlook.twenty_day_status", assets)
self.assertNotIn("<b>{item.estimate_status}</b>", assets)
```

- [ ] **Step 2: Run RED**

Run:

```bash
.venv/bin/python -m unittest -v tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_react_separates_observation_and_outlook_statuses
```

Expected: FAIL on missing `전체 전망 ·` copy.

- [ ] **Step 3: Implement minimal copy clarification**

Keep the existing header and replace each future status text node with:

```tsx
<b className={`estimate-${item.outlook.five_day_status.toLowerCase()}`}>
  전체 전망 · {item.outlook.five_day_status}
</b>
```

Use the equivalent `twenty_day_status` for 20D. Add wrapping styles so the label remains readable at 420px.

- [ ] **Step 4: Run GREEN and focused payload regression**

```bash
.venv/bin/python -m unittest -v \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_react_separates_observation_and_outlook_statuses \
  tests.test_service_contracts.FuturesMacroThermometerContractTests.test_futures_macro_v2_payload_separates_current_and_future_horizons
```

Expected: 2 tests PASS.

- [ ] **Step 5: Commit Task 2**

```bash
git add tests/test_service_contracts.py app/web/streamlit_components/futures_macro_workbench/src/AssetPathwaysSection.tsx app/web/streamlit_components/futures_macro_workbench/src/style.css
git commit -m "선물 매크로 자산 전망 상태 의미 명확화"
```

### Task 3: Build Production Component And Restore V4 Snapshot

**Files:**
- Modify mechanically: `app/web/streamlit_components/futures_macro_workbench/component_static/`
- Read / execute: `app/services/futures_macro_snapshot.py`
- Read: `finance/loaders/futures_macro_snapshot.py`

**Interfaces:**
- Consumes: stored `finance_price.futures_ohlcv` and `materialize_overview_futures_macro_snapshot(force=True)`.
- Produces: production bundle with the new UI and one compatible `overview_current` V4 snapshot row.

- [ ] **Step 1: Run focused pre-build contracts**

```bash
.venv/bin/python -m unittest -v \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_ribbon_has_visible_regime_legend \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_react_separates_observation_and_outlook_statuses
```

Expected: 2 tests PASS.

- [ ] **Step 2: Build the production component**

```bash
npm run build --prefix app/web/streamlit_components/futures_macro_workbench
```

Expected: Vite exits 0 and writes hashed assets under `component_static/assets/`.

- [ ] **Step 3: Force V4 materialization from stored daily rows**

```bash
.venv/bin/python - <<'PY'
from app.services.futures_macro_snapshot import materialize_overview_futures_macro_snapshot
print(materialize_overview_futures_macro_snapshot(force=True))
PY
```

Expected: `status=materialized`, source marker `2026-07-17`, snapshot status `READY`. No provider collector is invoked.

- [ ] **Step 4: Verify persisted and UI payload contracts**

Run a read-only script that asserts:

```python
assert row["algorithm_version"] == "pattern_outlook_v4_conservative_status_10y"
assert payload["hero"]["observation_status"] == "OBSERVED"
assert [item["estimate_status"] for item in payload["horizons"] if item["kind"] == "conditional_outlook"] == ["PROVISIONAL", "PROVISIONAL"]
assert all(item["observation_status"] == "OBSERVED" for item in payload["asset_pathways"])
```

- [ ] **Step 5: Commit the production bundle**

```bash
git add app/web/streamlit_components/futures_macro_workbench/component_static
git commit -m "선물 매크로 범례 production bundle 갱신"
```

### Task 4: Browser QA, Documentation, And Final Verification

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718/RISKS.md`
- Modify if current-state pointer is stale: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify if durable interpretation changed: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

**Interfaces:**
- Consumes: built static component and compatible V4 snapshot.
- Produces: actual desktop/mobile QA evidence and durable closeout record.

- [ ] **Step 1: Start a fresh `sub-dev` QA server**

Use a free port and `--server.fileWatcherType none`. Do not stop or modify other worktree processes.

- [ ] **Step 2: Verify desktop behavior**

Confirm:

- visible legend has five text-labelled entries and `과거 → 최근`;
- card headers show `관측 완료`;
- next 5D and 20D rows show `전체 전망 · PROVISIONAL`;
- ribbon has 60 cells and hover/focus title still includes date, regime, transition;
- browser console errors are zero.

- [ ] **Step 3: Verify 420px behavior**

Confirm document and workbench have no horizontal overflow, legend wraps without clipping, and future badges remain readable.

- [ ] **Step 4: Save one generated QA screenshot**

Save outside the repository under `/Users/taeho/.codex/visualizations/2026/07/19/futures-macro-ribbon-status/`. Do not stage it.

- [ ] **Step 5: Update the smallest durable doc set**

Record the UI clarification, V4 restoration, actual statuses, QA evidence, and residual shared-worktree overwrite risk. Do not describe versioned schema protection as implemented.

- [ ] **Step 6: Run final verification**

```bash
.venv/bin/python -m unittest -v \
  tests.test_futures_macro_pattern \
  tests.test_futures_macro_pattern_validation \
  tests.test_futures_macro_snapshot \
  tests.test_service_contracts.FuturesMacroThermometerContractTests \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_ribbon_has_visible_regime_legend \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_react_separates_observation_and_outlook_statuses
npm run build --prefix app/web/streamlit_components/futures_macro_workbench
.venv/bin/python -m py_compile app/web/overview/futures_macro_helpers.py app/services/futures_macro_snapshot.py
git diff --check
```

Expected: all focused tests and build pass; compile and diff check exit 0.

- [ ] **Step 7: Commit closeout documentation**

```bash
git add .aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718/STATUS.md .aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718/RUNS.md .aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718/RISKS.md .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "선물 매크로 범례와 V4 복구 마무리"
```
