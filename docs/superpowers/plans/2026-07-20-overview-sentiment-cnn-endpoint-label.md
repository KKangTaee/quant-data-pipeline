# Overview Sentiment CNN Endpoint Label Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the duplicated always-visible CNN endpoint text without removing the endpoint marker, header latest value, or hover detail.

**Architecture:** Keep the existing chart data and interaction contracts. Change only the CNN latest-point SVG group so it renders the circle without the adjacent text, and lock that boundary with the existing React source contract.

**Tech Stack:** React 18, TypeScript 5, Vite 6, Python `unittest` source contracts.

## Global Constraints

- Keep the CNN final-point circle.
- Keep chart-header latest state, value, and date.
- Keep hover guide, focus dots, and tooltip.
- Do not change AAII charts, dimensions, data, colors, or aligned periods.

---

### Task 1: Remove The CNN Inline Endpoint Text

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/web/streamlit_components/sentiment_workbench/src/SentimentHistorySection.tsx`
- Rebuild: `app/web/streamlit_components/sentiment_workbench/component_static/`

**Interfaces:**
- Consumes: the existing `latestPoint` and `sentiment-workbench__chart-latest-point` group.
- Produces: the same endpoint group with a circle only.

- [x] **Step 1: Write the failing React source contract**

Add these assertions to `test_sentiment_history_uses_one_shared_aligned_domain_for_both_panels`:

```python
self.assertIn('className="sentiment-workbench__chart-latest-point"', history)
self.assertIn("<circle cx={xForTimestamp(latestPoint.timestamp", history)
self.assertNotIn("{displayValue(latestPoint.numericValue)} ·", history)
```

- [x] **Step 2: Run the focused contract and confirm RED**

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_history_uses_one_shared_aligned_domain_for_both_panels
```

Expected: one failure because the inline value expression still exists.

- [x] **Step 3: Remove only the SVG text element**

Keep:

```tsx
<g className="sentiment-workbench__chart-latest-point" aria-hidden="true">
  <circle cx={xForTimestamp(latestPoint.timestamp, chartTimeExtent)} cy={yForValue(latestPoint.numericValue, domain)} fill={chartSeriesColor(latestPoint.series, mode)} r={4.5} />
</g>
```

- [x] **Step 4: Run GREEN verification and production build**

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests
npm run build --prefix app/web/streamlit_components/sentiment_workbench
git diff --check
```

Expected: `184` tests pass, Vite build succeeds, and diff check is clean.

- [x] **Step 5: Record and commit the follow-up**

Append the RED/GREEN/build result to the active task `RUNS.md`, stage only the source contract, component source/static build, plan, and task note, then commit with a Korean message.
