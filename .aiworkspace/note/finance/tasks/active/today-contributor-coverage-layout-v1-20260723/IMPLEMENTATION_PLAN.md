# Today Contributor Coverage / Review Layout V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Show every computable Today portfolio contributor in deterministic impact order and keep review items compactly top-aligned.

**Architecture:** Python remains the owner of contributor completeness, numeric filtering, tone, and deterministic ordering. React derives an explicit coverage label from the selected display contributor count and `active_item_count`, retains the existing cards, and fixes only the review section's internal grid alignment. The payload versions, DB calculations, live-island boundary, and provider cadence remain unchanged.

**Tech Stack:** Python 3.12, unittest, React 18, TypeScript, Vitest SSR, Vite, Streamlit custom component, CSS Grid.

## Global Constraints

- Preserve every numeric contribution, including zero; never fabricate a missing contribution as zero.
- Sort contributors by descending absolute contribution and then ascending symbol.
- Use `positive`, `negative`, and `neutral` tone for positive, negative, and zero values.
- Use `전체 N개 · 영향 큰 순` only when contributor count equals active item count; otherwise use `기여 계산 N/M개 · 영향 큰 순`.
- Keep desktop two-column and phone one-column contributor cards.
- Keep outer detail panels equal height while review text aligns at the top with an 8px gap.
- Do not change performance calculations, DB schema/writes, provider collection, Today fragment behavior, or schema versions.
- Preserve unrelated dirty registry, run-history, screenshot, and local files.

---

### Task 1: Complete Contributor Projection

**Files:**
- Modify: `tests/test_today_home.py`
- Modify: `app/services/today.py`

**Interfaces:**
- Consumes: Portfolio Monitoring workspace `active_group.item_rows`, `active_group.metrics.contribution_by_item`, optional live overlay `contributors`.
- Produces: `project_today_portfolio(workspace, portfolio_live=None) -> dict[str, Any]` with complete deterministic contributor arrays and three-value tone.

- [x] **Step 1: Write failing EOD completeness and zero-tone tests**

Add a focused test beside existing Today contributor projection tests:

```python
def test_contributors_keep_all_numeric_rows_in_absolute_impact_order(self) -> None:
    inputs = self._complete_inputs()
    active = inputs["portfolio"]["active_group"]
    active["active_item_count"] = 5
    active["item_rows"] = [
        {"monitoring_item_id": "amd", "source_ref": "AMD", "total_return": 3.64},
        {"monitoring_item_id": "tem", "source_ref": "TEM", "total_return": -0.24},
        {"monitoring_item_id": "rklb", "source_ref": "RKLB", "total_return": -0.05},
        {"monitoring_item_id": "soxx", "source_ref": "SOXX", "total_return": -0.07},
        {"monitoring_item_id": "qqq", "source_ref": "QQQ", "total_return": 0.0},
    ]
    active["metrics"]["contribution_by_item"] = {
        "amd": 12136.60,
        "tem": -462.00,
        "rklb": -440.00,
        "soxx": -265.08,
        "qqq": 0.0,
    }

    model = self._builder()(**inputs)

    self.assertEqual(
        [row["symbol"] for row in model["portfolio"]["contributors"]],
        ["AMD", "TEM", "RKLB", "SOXX", "QQQ"],
    )
    self.assertEqual(model["portfolio"]["contributors"][-1]["tone"], "neutral")
```

- [x] **Step 2: Run the EOD test and confirm RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_today_home.TodayHomeReadModelTests.test_contributors_keep_all_numeric_rows_in_absolute_impact_order -v
```

Expected: FAIL because the current projection drops zero and slices positive/negative rows to two each.

- [x] **Step 3: Write failing live ordering test**

Add a focused public projector test:

```python
def test_live_contributors_use_the_same_absolute_impact_order(self) -> None:
    inputs = self._complete_inputs()
    inputs["portfolio_live"] = {
        "status": "LIVE_READY",
        "contributors": [
            {"symbol": "QQQ", "contribution_value": 0.0, "total_return": 0.0},
            {"symbol": "AMD", "contribution_value": 120.0, "total_return": 0.2},
            {"symbol": "SOXX", "contribution_value": -30.0, "total_return": -0.1},
        ],
    }

    model = self._builder()(**inputs)

    self.assertEqual(
        [row["symbol"] for row in model["portfolio"]["live"]["contributors"]],
        ["AMD", "SOXX", "QQQ"],
    )
    self.assertEqual(model["portfolio"]["live"]["contributors"][-1]["tone"], "neutral")
```

- [x] **Step 4: Run the live test and confirm RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_today_home.TodayHomeReadModelTests.test_live_contributors_use_the_same_absolute_impact_order -v
```

Expected: FAIL because live contributors retain input order and classify zero as negative.

- [x] **Step 5: Implement one shared sort/tone policy**

Add helpers near portfolio projection functions:

```python
def _contributor_tone(value: float) -> str:
    if value > 0:
        return "positive"
    if value < 0:
        return "negative"
    return "neutral"


def _sort_contributors(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            -abs(float(row["contribution_value"])),
            str(row.get("symbol") or ""),
        ),
    )
```

In `_project_portfolio`, skip only `None`, keep zero, use `_contributor_tone`, delete positive/negative slicing, and return `_sort_contributors(contribution_rows)`.

In `_project_live_portfolio`, use `_contributor_tone(value)` for every numeric row and return `_sort_contributors(contributors)`.

- [x] **Step 6: Run focused and Today Python tests**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_today_home.TodayHomeReadModelTests.test_contributors_keep_all_numeric_rows_in_absolute_impact_order \
  tests.test_today_home.TodayHomeReadModelTests.test_live_contributors_use_the_same_absolute_impact_order \
  tests.test_today_home -v
```

Expected: all Today tests PASS.

- [x] **Step 7: Commit Task 1**

```bash
git add app/services/today.py tests/test_today_home.py
git commit -m "수정: Today 종목 기여 전체 투영"
```

---

### Task 2: Coverage Copy And Compact Review Layout

**Files:**
- Modify: `app/web/streamlit_components/today_workbench/src/types.ts`
- Modify: `app/web/streamlit_components/today_workbench/src/TodayPortfolioPanel.tsx`
- Modify: `app/web/streamlit_components/today_workbench/src/style.css`
- Modify: `app/web/streamlit_components/today_workbench/src/view.test.tsx`
- Modify: `app/web/today_page.py`
- Modify: `tests/test_today_home.py`
- Rebuild: `app/web/streamlit_components/today_workbench/component_static/`

**Interfaces:**
- Consumes: `TodayPortfolio.active_item_count`, `displayPortfolio(portfolio).contributors`, three-value contributor tone.
- Produces: visible contributor coverage copy, all contributor cards, and `today-review-section` compact layout.

- [x] **Step 1: Write failing React full/partial coverage tests**

Add SSR assertions to `view.test.tsx` using a five-contributor portfolio payload:

```tsx
it("shows every contributor with explicit full coverage copy", () => {
  const portfolio = {
    ...payload.portfolio,
    active_item_count: 5,
    contributors: [
      { symbol: "AMD", contribution_value: 12136, total_return: 3.64, tone: "positive" as const },
      { symbol: "TEM", contribution_value: -462, total_return: -0.24, tone: "negative" as const },
      { symbol: "RKLB", contribution_value: -440, total_return: -0.05, tone: "negative" as const },
      { symbol: "SOXX", contribution_value: -265, total_return: -0.07, tone: "negative" as const },
      { symbol: "QQQ", contribution_value: 0, total_return: 0, tone: "neutral" as const },
    ],
  };
  const html = renderToStaticMarkup(
    <TodayPortfolioPanel portfolio={portfolio} viewportWidth={1200} />,
  );
  expect(html).toContain("전체 5개 · 영향 큰 순");
  for (const symbol of ["AMD", "TEM", "RKLB", "SOXX", "QQQ"]) {
    expect(html).toContain(symbol);
  }
});

it("discloses partial contributor coverage", () => {
  const portfolio = {
    ...payload.portfolio,
    active_item_count: 5,
    contributors: [
      { symbol: "AMD", contribution_value: 12136, total_return: 3.64, tone: "positive" as const },
      { symbol: "TEM", contribution_value: -462, total_return: -0.24, tone: "negative" as const },
      { symbol: "RKLB", contribution_value: -440, total_return: -0.05, tone: "negative" as const },
    ],
  };
  const html = renderToStaticMarkup(
    <TodayPortfolioPanel portfolio={portfolio} viewportWidth={1200} />,
  );
  expect(html).toContain("기여 계산 3/5개 · 영향 큰 순");
});
```

- [x] **Step 2: Run React tests and confirm RED**

Run:

```bash
cd app/web/streamlit_components/today_workbench
npm test -- --run src/view.test.tsx
```

Expected: FAIL because the dynamic coverage copy does not exist.

- [x] **Step 3: Write failing source/CSS contract test**

Replace the obsolete top/bottom assertion in `TodayHomePageContractTests.test_today_page_reuses_overview_visual_tokens_and_read_only_loaders` with:

```python
self.assertNotIn("기여 상위 2 · 하위 2", react_source)
self.assertIn("contributorCoverageLabel", react_source)
self.assertIn('className="today-review-section"', react_source)
review_rule = css_source.split(".today-review-list {", 1)[1].split("}", 1)[0]
self.assertIn("align-content: start", review_rule)
self.assertIn("grid-auto-rows: max-content", review_rule)
```

- [x] **Step 4: Run Python contract test and confirm RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_today_home.TodayHomePageContractTests.test_today_page_reuses_overview_visual_tokens_and_read_only_loaders -v
```

Expected: FAIL because old copy remains and compact review CSS is absent.

- [x] **Step 5: Implement coverage copy and neutral tone**

In `types.ts`, widen `PortfolioContributor.tone`:

```ts
tone: "positive" | "negative" | "neutral";
```

In `TodayPortfolioPanel.tsx`, compute:

```ts
const contributorCount = display.contributors.length;
const contributorCoverageLabel = contributorCount === portfolio.active_item_count
  ? `전체 ${contributorCount}개 · 영향 큰 순`
  : `기여 계산 ${contributorCount}/${portfolio.active_item_count}개 · 영향 큰 순`;
```

Replace the fixed header copy with `contributorCoverageLabel`. Map tone to `is-positive`, `is-negative`, or `is-neutral`. Add `className="today-review-section"` to the review section.

In `build_today_html`, derive the same coverage copy from the fallback portfolio's contributor count and `active_item_count` and replace `기여 상위 2 · 하위 2`. Update `test_today_html_preserves_b_layout_order_and_escapes_market_copy` to expect `기여 계산 1/2개 · 영향 큰 순` for its fixture.

- [x] **Step 6: Implement compact review CSS**

Use:

```css
.today-review-section { align-content: start; }
.today-review-list {
  display: grid;
  grid-auto-rows: max-content;
  align-content: start;
  gap: 8px;
}
.today-review-list p {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 7px;
  margin: 0;
  color: #607486;
  font-size: 11px;
  line-height: 1.45;
}
.today-contributor-section .is-neutral { color: #607486; }
```

- [x] **Step 7: Run focused React/Python tests**

Run:

```bash
cd app/web/streamlit_components/today_workbench
npm test -- --run src/view.test.tsx
npm run typecheck
cd ../../../..
.venv/bin/python -m unittest tests.test_today_home -v
```

Expected: all focused tests PASS.

- [x] **Step 8: Build and commit Task 2**

```bash
cd app/web/streamlit_components/today_workbench
npm run build
cd ../../../..
git add app/web/streamlit_components/today_workbench app/web/today_page.py tests/test_today_home.py
git commit -m "개선: Today 종목 기여와 우선 확인 배치 정리"
```

---

### Task 3: Browser QA And Documentation Closeout

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/today-contributor-coverage-layout-v1-20260723/{IMPLEMENTATION_PLAN.md,STATUS.md,NOTES.md,RUNS.md,RISKS.md}`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Create generated, do not commit: `today-contributor-coverage-layout-v1-qa.png`

**Interfaces:**
- Consumes: production component build and actual default portfolio DB state.
- Produces: verified actual UI and durable task handoff.

- [x] **Step 1: Run full relevant regressions**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_today_home \
  tests.test_portfolio_monitoring_intraday_refresh \
  tests.test_portfolio_monitoring_valuation -v
cd app/web/streamlit_components/today_workbench
npm test
npm run typecheck
npm run build
cd ../../../..
.venv/bin/python -m py_compile app/services/today.py app/web/today_page.py
git diff --check
```

Expected: zero failures and exit code 0.

- [x] **Step 2: Run actual Browser QA**

Start a fresh Streamlit server and verify:

- actual symbols appear in impact order: AMD, TEM, RKLB, SOXX, QQQ;
- header says `전체 5개 · 영향 큰 순`;
- review rows are top-aligned with consistent spacing;
- 1280, 760, and 420px have zero top/frame horizontal overflow;
- browser console has zero errors;
- save `today-contributor-coverage-layout-v1-qa.png` without staging it.

- [x] **Step 3: Synchronize task and durable docs**

Record the root cause, complete contributor policy, review-grid fix, test counts, Browser QA, and any remaining risk. Keep root handoff entries to 3–5 lines and do not stage registries, run history, screenshots, or local artifacts.

- [x] **Step 4: Apply verification-before-completion and commit docs**

Run final fresh verification, then:

```bash
git add .aiworkspace/note/finance/docs/INDEX.md \
  .aiworkspace/note/finance/docs/ROADMAP.md \
  .aiworkspace/note/finance/tasks/active/today-contributor-coverage-layout-v1-20260723 \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git diff --cached --check
git commit -m "문서: Today 종목 기여 표시 개선 정리"
```
