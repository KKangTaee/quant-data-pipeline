# Overview Sentiment Period Metric UI Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove decorative source top borders and make each 1W·1M metric's observed change the primary value while keeping the shared latest value as secondary context.

**Architecture:** Keep the existing service and `period_changes` payload unchanged. Update only the period metric React markup and CSS presentation, protect the hierarchy with source-contract regressions, regenerate the checked-in Vite bundle, and verify the actual Streamlit screen.

**Tech Stack:** React, TypeScript, CSS, Vite, Python `unittest`, Streamlit Browser QA.

## Global Constraints

- Do not change sentiment service calculations, observation lags, dates, payload schema, or outlook publication gate.
- Do not add a provider, DB schema, ingestion path, estimator, or probability.
- Use identical neutral surfaces for CNN and AAII metric boxes.
- Use source color only in a small circular marker beside the source name.
- Show `metric.change` as the primary number and `metric.end_value` as `현재 …` secondary context.
- Preserve the source-specific `start_value → end_value` date range, state label, unavailable state, and relationship summary.
- Do not stage registry, saved portfolio, run history, `.superpowers/`, or unrelated QA artifacts.

---

### Task 1: Lock The Period Metric Visual Contract

**Files:**
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- Consumes: `SentimentPeriodChangeSection.tsx` source and `style.css` source.
- Produces: regression requirements for `.sentiment-workbench__period-change-primary`, `.sentiment-workbench__period-current`, and source marker CSS.

- [x] **Step 1: Write the failing React source assertions**

Extend `test_sentiment_react_period_cards_watch_paths_and_detail_disclosure` to require:

```python
self.assertIn("sentiment-workbench__period-change-primary", period_change_source)
self.assertIn("기간 변화", period_change_source)
self.assertIn("sentiment-workbench__period-current", period_change_source)
self.assertIn("현재", period_change_source)
```

- [x] **Step 2: Write the failing CSS assertions**

Extend `test_sentiment_react_redesign_css_uses_balanced_surfaces_and_mobile_stack` so the CNN and AAII source rules must not contain `border-top`, and require a circular `header span::before` marker with both existing source colors.

- [x] **Step 3: Run the two focused tests and confirm RED**

Run:

```bash
.venv/bin/python -m unittest -v \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_period_cards_watch_paths_and_detail_disclosure \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_redesign_css_uses_balanced_surfaces_and_mobile_stack
```

Expected: failures because change-primary/current markup and source marker CSS do not exist and source-specific `border-top` still exists.

### Task 2: Implement The Approved Visual Hierarchy

**Files:**
- Modify: `app/web/streamlit_components/sentiment_workbench/src/SentimentPeriodChangeSection.tsx`
- Modify: `app/web/streamlit_components/sentiment_workbench/src/style.css`

**Interfaces:**
- Consumes: existing `PeriodChangeMetric.change`, `end_value`, `unit_label`, `end_state`, and `metricRange(metric)`.
- Produces: change-primary/current-secondary metric markup with unchanged payload and unavailable behavior.

- [x] **Step 1: Render change as the primary value**

For available metrics, render this hierarchy:

```tsx
<div className="sentiment-workbench__period-value">
  <div className="sentiment-workbench__period-change-primary">
    <span>기간 변화</span>
    <strong>{signedValue(metric.change, metric.unit_label)}</strong>
  </div>
  <div className="sentiment-workbench__period-current">
    <span>현재</span>
    <b>{displayValue(metric.end_value, metric.unit_label)}</b>
  </div>
</div>
```

Keep the unavailable branch and `metricRange(metric)` unchanged.

- [x] **Step 2: Replace source top borders with label markers**

Remove the two source-specific `border-top` declarations. Make the source label `inline-flex` and add a `7px` circular `::before` marker; keep `#b58a6a` for CNN and `#5aa99d` for AAII.

- [x] **Step 3: Style primary change and secondary current values**

Use the existing up/down colors on `.sentiment-workbench__period-change-primary strong`, keep the current value neutral and smaller, and retain responsive wrapping without adding a new card border treatment.

- [x] **Step 4: Run the focused tests and confirm GREEN**

Run the Task 1 command. Expected: `Ran 2 tests ... OK`.

### Task 3: Build, QA, Document, And Commit

**Files:**
- Regenerate: `app/web/streamlit_components/sentiment_workbench/component_static/`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1-20260719/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1-20260719/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1-20260719/STATUS.md`

**Interfaces:**
- Consumes: updated React/CSS source.
- Produces: checked-in production bundle, QA evidence, and task closeout record.

- [x] **Step 1: Regenerate the production bundle**

Run:

```bash
cd app/web/streamlit_components/sentiment_workbench
npm run build
```

Expected: Vite build completes successfully and `component_static/index.html` points to the new hashed assets.

- [x] **Step 2: Run sentiment regression and syntax checks**

Run the two focused tests, the existing sentiment-name regression excluding the three recorded baseline failures, `python -m py_compile` for changed Python test dependencies if needed, and `git diff --check`.

- [x] **Step 3: Run actual Streamlit Browser QA**

Open `/overview?overview_tab=sentiment` and verify:

- CNN·AAII metric boxes have no colored top border.
- Each source name has one small colored marker.
- 1W CNN primary is `+15.5pt` and 1M CNN primary is `+25.4pt` on the current DB snapshot.
- shared current value appears as secondary `현재 66.3pt`.
- date ranges, status labels, relationship summary, desktop layout, 420px stacking, overflow, and console errors remain correct.

Save `overview-sentiment-period-metric-ui-polish-qa.png` as an untracked generated artifact.

- [x] **Step 4: Align task documentation**

Record the normal shared-endpoint interpretation, change-first hierarchy, marker design, verification commands, and any remaining baseline failures. Do not modify ROADMAP, PRODUCT_DIRECTION, PROJECT_MAP, or durable flow docs because product behavior and ownership do not change.

- [x] **Step 5: Stage and commit only this polish unit**

Stage the plan, test, React/CSS, generated bundle, and three task documents by exact path. Commit with:

```bash
git commit -m "심리 기간 카드 변화량 중심 UI 개선"
```
