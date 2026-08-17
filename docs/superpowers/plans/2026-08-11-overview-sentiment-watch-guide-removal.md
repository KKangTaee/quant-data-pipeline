# Overview Sentiment Watch Guide Removal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the non-functional Watch guide from Market Research sentiment while preserving the backend payload contract and the period-change/evidence workflow.

**Architecture:** Treat this as a React presentation cleanup. Remove the unused Watch component, root render/import, and dedicated CSS; retain `SentimentWorkbenchPayload.watch_conditions` and Python service generation for compatibility. Protect the new section order and absence contract with source regressions, regenerate the checked-in Vite bundle, and verify the actual Streamlit surface.

**Tech Stack:** React, TypeScript, CSS, Vite, Python `unittest`, Streamlit Browser QA.

## Global Constraints

- Remove only the Watch guide from the sentiment React presentation.
- Keep Python `watch_conditions` calculation, payload schema, and service tests unchanged.
- Keep period-change calculations, CNN/AAII state, outlook publication gate, and detail disclosure unchanged.
- The visible order after removal is Hero -> current evidence -> history -> period changes -> detail disclosure.
- Do not stage registry JSONL, saved portfolios, run history, `.superpowers/`, or generated QA screenshots.

---

### Task 1: Remove The Watch Guide From The Sentiment Surface

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/web/streamlit_components/sentiment_workbench/src/SentimentWorkbench.tsx`
- Delete: `app/web/streamlit_components/sentiment_workbench/src/WatchConditionsSection.tsx`
- Modify: `app/web/streamlit_components/sentiment_workbench/src/style.css`

**Interfaces:**
- Consumes: existing `SentimentWorkbenchPayload.watch_conditions` compatibility field without rendering it.
- Produces: a sentiment root whose final visible sections are `SentimentPeriodChangeSection` followed by `SentimentEvidenceDisclosure`.

- [x] **Step 1: Write the failing absence and order regressions**

Update the existing sentiment React source-contract tests to require:

```python
self.assertFalse((source_root / "WatchConditionsSection.tsx").exists())
self.assertNotIn('from "./WatchConditionsSection"', root_source)
self.assertNotIn("<WatchConditionsSection", root_source)
self.assertNotIn("다음 확인 조건", all_source)
self.assertLess(
    root_source.index("<SentimentPeriodChangeSection"),
    root_source.index("<SentimentEvidenceDisclosure"),
)
self.assertNotIn(".sentiment-workbench__watch-grid", style)
```

Keep backend tests for `_build_sentiment_watch_conditions` and payload keys unchanged.

- [x] **Step 2: Run the focused tests and confirm RED**

Run:

```bash
.venv/bin/python -m unittest -v \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_period_cards_and_detail_disclosure_without_watch_guide \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_redesign_css_uses_balanced_surfaces_and_mobile_stack \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_driver_surface_groups_cnn_and_aaii_without_next_checks
```

Expected: failures because the Watch file, root import/render, copy, and CSS still exist.

- [x] **Step 3: Remove the Watch presentation code**

In `SentimentWorkbench.tsx`, delete:

```tsx
import WatchConditionsSection from "./WatchConditionsSection";
```

and:

```tsx
<WatchConditionsSection watchConditions={payload.watch_conditions} />
```

Delete `WatchConditionsSection.tsx`. In `style.css`, remove the Watch article from the shared surface selector, remove all `.sentiment-workbench__watch-grid` rules, and remove it from the `max-width: 760px` combined grid selector.

- [x] **Step 4: Run the focused tests and confirm GREEN**

Run the Step 2 command. Expected: `Ran 3 tests ... OK`.

### Task 2: Build, QA, Document, And Commit

**Files:**
- Regenerate: `app/web/streamlit_components/sentiment_workbench/component_static/`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1-20260719/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1-20260719/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1-20260719/STATUS.md`

**Interfaces:**
- Consumes: Watch-free React source.
- Produces: checked-in production bundle, actual-screen QA evidence, and aligned task closeout.

- [x] **Step 1: Regenerate the production bundle**

Run:

```bash
cd app/web/streamlit_components/sentiment_workbench
npm run build
```

Expected: Vite build succeeds and `component_static/index.html` references existing new hashed assets.

- [x] **Step 2: Run regression and syntax checks**

Run the focused tests, the existing sentiment-name regression with the three recorded baseline failures matched by exact test ID, bundle-reference existence check, and `git diff --check`.

- [x] **Step 3: Run actual Streamlit Browser QA**

Verify at `/overview?overview_tab=sentiment`:

- `기간별 심리 변화` is followed directly by `상세 근거와 원본 데이터`.
- `WATCH`, `다음 확인 조건`, `정렬 확인`, `설문 반전`, and `관계 지속` are absent.
- 1W/1M values and period relationships remain visible.
- desktop and 420px layouts have no horizontal overflow and browser warnings remain zero.

Save the screenshot as `overview-sentiment-watch-guide-removal-qa.png` and keep it untracked.

- [x] **Step 4: Align task documentation**

Record that the guide-only Watch section was removed, the backend compatibility payload remains, and product/service ownership did not change. Do not update ROADMAP, PRODUCT_DIRECTION, PROJECT_MAP, or durable flow docs.

- [x] **Step 5: Stage and commit only this cleanup**

Stage the plan, React/CSS deletion, tests, generated bundle, and task docs by exact path. Commit with:

```bash
git commit -m "심리 Watch 가이드 UI 제거"
```
