# Market Research Editorial Navigation V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current card-and-panel Market Research header with the approved Editorial Tabs layout while preserving the existing 3-family/7-view React/Python navigation contract.

**Architecture:** Keep `navigation.py`, the custom-component wrapper, payload schema, event envelope, query/session synchronization, and Streamlit fallback unchanged. Change only the React presentation markup needed for the editorial header and the component stylesheet, rebuild canonical static assets, and verify the existing route/state boundary end to end.

**Tech Stack:** React 18, TypeScript, Vite 6, Vitest, Testing Library, Streamlit custom components, pytest, Playwright Browser QA.

## Global Constraints

- Preserve all three family IDs, all seven canonical view IDs, labels, family defaults, and `select_view` event payloads.
- Preserve Python ownership of URL, session, legacy slug normalization, changed-view rerun, fallback, and selected renderer.
- Desktop title is exactly `30px`; at `max-width: 480px` it is exactly `26px`.
- Desktop family navigation is text plus a 2px active underline with no card fill, radius, or family description row.
- The local view group has no outer border, radius, or background; only the active view uses a filled pill.
- Desktop navigation uses full iframe/page content width rather than `min(100%, 820px)`.
- At `max-width: 480px`, family remains three equal columns with full labels and views remain two equal columns.
- Preserve actual `<h1>`, `aria-label`, `aria-pressed`, `aria-current`, focus-visible, reduced-motion, dark theme, and overflow contracts.
- Do not modify module bodies, data/services/loaders/providers/DB, drawer/sticky behavior, or other Finance pages.
- Do not stage registry JSONL, research bundles, run history, `.superpowers/`, or generated QA images.

---

### Task 1: Convert the React markup to an editorial header and semantic family tabs

**Files:**

- Modify: `app/web/streamlit_components/market_research_navigation/src/MarketResearchNavigation.test.tsx:54-59`
- Modify: `app/web/streamlit_components/market_research_navigation/src/MarketResearchNavigation.tsx:46-65`

**Interfaces:**

- Consumes: existing `MarketResearchNavigationPayload`, `active_family`, `active_view`, family descriptions, and `Streamlit.setComponentValue` event bridge.
- Produces: `.mr-navigation__heading` wrapper; family buttons whose accessible name is `${family.label}: ${family.description}` but whose visible content is only `family.label`.
- Preserves: `select_view` event `{ event: { id: "select_view", view, nonce } }` and existing view buttons.

- [ ] **Step 1: Run the existing React baseline**

Run:

```bash
npm test --prefix app/web/streamlit_components/market_research_navigation
```

Expected: `4 passed`.

- [ ] **Step 2: Write the failing editorial markup test**

Replace the first test in `MarketResearchNavigation.test.tsx` with:

```tsx
it("renders an editorial heading and label-only family tabs with selected states", () => {
  const { container } = render(<MarketResearchNavigation {...props(payload)} />);

  expect(screen.getByRole("heading", { name: "Market Research", level: 1 })).toBeInTheDocument();
  expect(container.querySelector(".mr-navigation__heading")).toBeInTheDocument();
  expect(screen.queryByText("경제·매크로·심리·일정")).not.toBeInTheDocument();
  expect(
    screen.getByRole("button", { name: "시장 환경: 경제·매크로·심리·일정" }),
  ).toHaveAttribute("aria-pressed", "true");
  expect(screen.getByRole("button", { name: "경제 사이클" })).toHaveAttribute(
    "aria-current",
    "page",
  );
});
```

- [ ] **Step 3: Run the new test and verify RED**

Run:

```bash
npm test --prefix app/web/streamlit_components/market_research_navigation -- --run MarketResearchNavigation.test.tsx
```

Expected: FAIL because `.mr-navigation__heading` does not exist and the family description is still visible.

- [ ] **Step 4: Implement the minimal editorial markup**

Replace the header and family navigation block in `MarketResearchNavigation.tsx` with:

```tsx
<header className="mr-navigation__header">
  <div className="mr-navigation__heading">
    <span>{payload.eyebrow}</span>
    <h1>{payload.title}</h1>
  </div>
  <p>{payload.description}</p>
</header>
<nav className="mr-navigation__families" aria-label="리서치 목적">
  {payload.families.map((family) => (
    <button
      type="button"
      key={family.id}
      aria-label={`${family.label}: ${family.description}`}
      aria-pressed={family.id === activeFamily.id}
      onClick={() => {
        if (family.id !== activeFamily.id) emit(family.views[0]?.id ?? "");
      }}
    >
      <strong>{family.label}</strong>
    </button>
  ))}
</nav>
```

Do not change the `emit` function or `.mr-navigation__views` JSX.

- [ ] **Step 5: Run React tests and typecheck**

Run:

```bash
npm test --prefix app/web/streamlit_components/market_research_navigation
npm run typecheck --prefix app/web/streamlit_components/market_research_navigation
```

Expected: `4 passed`; TypeScript exits `0`.

- [ ] **Step 6: Commit the markup unit**

```bash
git add app/web/streamlit_components/market_research_navigation/src/MarketResearchNavigation.tsx app/web/streamlit_components/market_research_navigation/src/MarketResearchNavigation.test.tsx
git commit -m "기능: Market Research editorial header 구조 적용"
```

---

### Task 2: Replace card/panel chrome with the approved responsive Editorial Tabs CSS

**Files:**

- Modify: `tests/test_market_research_navigation.py`
- Replace: `app/web/streamlit_components/market_research_navigation/src/style.css`
- Rebuild: `app/web/streamlit_components/market_research_navigation/component_static/`

**Interfaces:**

- Consumes: Task 1 classes `.mr-navigation__header`, `.mr-navigation__heading`, `.mr-navigation__families`, `.mr-navigation__views` and existing aria state selectors.
- Produces: full-width editorial family divider/underline, unframed view row, active filled view pill, 30px/26px title contract, mobile 3-column/2-column layout.
- Preserves: `is-dark`, focus-visible, empty state, ResizeObserver-driven iframe height, and no horizontal overflow.

- [ ] **Step 1: Add the failing CSS contract test**

Append to `tests/test_market_research_navigation.py`:

```python
def test_market_research_react_css_uses_editorial_tabs_without_container_chrome():
    css = Path(
        "app/web/streamlit_components/market_research_navigation/src/style.css"
    ).read_text(encoding="utf-8")

    family_block = css.split(".mr-navigation__families button {", 1)[1].split("}", 1)[0]
    view_block = css.split(".mr-navigation__views {", 1)[1].split("}", 1)[0]

    assert ".mr-navigation__heading" in css
    assert "font-size: 30px" in css
    assert "font-size: 26px" in css
    assert "width: min(100%, 820px)" not in css
    assert "border-bottom: 2px solid transparent" in family_block
    assert "border-radius" not in family_block
    assert "background: transparent" in family_block
    assert 'button[aria-pressed="true"]' in css
    assert "border-bottom-color" in css
    assert "border:" not in view_block
    assert "border-radius:" not in view_block
    assert "background:" not in view_block
    assert "grid-template-columns: repeat(3, minmax(0, 1fr))" in css
    assert "grid-template-columns: repeat(2, minmax(0, 1fr))" in css
```

- [ ] **Step 2: Run the CSS contract and verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_market_research_navigation.py::test_market_research_react_css_uses_editorial_tabs_without_container_chrome -q
```

Expected: FAIL because the current CSS has no heading wrapper rule, uses the 820px width limit, family card radius/fill, and view container chrome.

- [ ] **Step 3: Replace `style.css` with the approved implementation**

Use this complete stylesheet:

```css
:root {
  background: transparent;
  font-family: Inter, Pretendard, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-synthesis: none;
}

* { box-sizing: border-box; }
html, body, #root { width: 100%; min-height: 100%; margin: 0; }
body { overflow-x: hidden; background: transparent; }
button { font: inherit; }

.mr-navigation {
  --ink: #1d3042;
  --muted: #6c7e8e;
  --line: #dce5eb;
  --active: #718ca0;
  --active-ink: #ffffff;
  display: grid;
  width: 100%;
  gap: 0;
  padding: 2px 2px 10px;
  color: var(--ink);
  overflow-x: hidden;
}

.mr-navigation.is-dark {
  --ink: #f4f7fa;
  --muted: #a5b0bb;
  --line: #2c333c;
  --active: #9bb4c5;
  --active-ink: #101820;
}

.mr-navigation__header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 32px;
  width: 100%;
  padding: 4px 0 15px;
}

.mr-navigation__heading { display: grid; min-width: 0; gap: 6px; }
.mr-navigation__heading span { color: #6d8799; font-size: 10px; font-weight: 800; letter-spacing: .14em; }
.mr-navigation__heading h1 { margin: 0; font-size: 30px; line-height: 1.08; letter-spacing: -.045em; }
.mr-navigation__header p {
  max-width: 360px;
  margin: 0;
  color: var(--muted);
  font-size: 13px;
  line-height: 1.5;
  text-align: right;
}

.mr-navigation__families {
  display: grid;
  width: 100%;
  grid-template-columns: repeat(3, max-content);
  gap: 26px;
  border-bottom: 1px solid var(--line);
}

.mr-navigation__families button {
  min-width: 0;
  min-height: 44px;
  margin: 0 0 -1px;
  padding: 12px 1px 10px;
  border: 0;
  border-bottom: 2px solid transparent;
  color: var(--muted);
  background: transparent;
  text-align: left;
  cursor: pointer;
  transition: color 150ms ease, border-color 150ms ease;
}

.mr-navigation__families button:hover { color: var(--ink); }
.mr-navigation__families button[aria-pressed="true"] {
  border-bottom-color: var(--active);
  color: var(--ink);
}
.mr-navigation__families strong { font-size: 13px; font-weight: 750; }

.mr-navigation__views {
  display: flex;
  width: 100%;
  flex-wrap: wrap;
  gap: 7px;
  padding: 10px 0 12px;
}

.mr-navigation__views button {
  min-height: 34px;
  padding: 7px 12px;
  border: 1px solid transparent;
  border-radius: 999px;
  color: var(--muted);
  background: transparent;
  cursor: pointer;
  transition: 150ms ease;
}

.mr-navigation__views button:hover { color: var(--ink); background: color-mix(in srgb, var(--active) 10%, transparent); }
.mr-navigation__views button[aria-current="page"] {
  border-color: var(--active);
  color: var(--active-ink);
  background: var(--active);
  font-weight: 750;
}
.mr-navigation button:focus-visible { outline: 2px solid #7aa6c4; outline-offset: 2px; }
.mr-navigation-empty { padding: 16px; color: #6c7e8e; font-size: 13px; }

@media (max-width: 760px) {
  .mr-navigation__header { gap: 20px; }
  .mr-navigation__header p { max-width: 300px; }
  .mr-navigation__families { gap: 18px; }
}

@media (max-width: 480px) {
  .mr-navigation { padding-bottom: 8px; }
  .mr-navigation__header { display: grid; gap: 7px; padding: 2px 0 11px; }
  .mr-navigation__heading { gap: 5px; }
  .mr-navigation__heading h1 { font-size: 26px; }
  .mr-navigation__header p { max-width: none; font-size: 12px; text-align: left; }
  .mr-navigation__families { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0; }
  .mr-navigation__families button {
    min-height: 44px;
    padding: 10px 4px 9px;
    text-align: center;
    white-space: nowrap;
  }
  .mr-navigation__families strong { font-size: 12px; }
  .mr-navigation__views { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 6px; }
  .mr-navigation__views button { width: 100%; }
  .mr-navigation__views button:only-child { grid-column: 1 / -1; }
}

@media (prefers-reduced-motion: reduce) {
  .mr-navigation button { transition: none; }
}
```

- [ ] **Step 4: Run the CSS contract, React tests, and typecheck**

Run:

```bash
.venv/bin/python -m pytest tests/test_market_research_navigation.py::test_market_research_react_css_uses_editorial_tabs_without_container_chrome -q
npm test --prefix app/web/streamlit_components/market_research_navigation
npm run typecheck --prefix app/web/streamlit_components/market_research_navigation
```

Expected: Python `1 passed`; React `4 passed`; TypeScript exits `0`.

- [ ] **Step 5: Rebuild canonical static assets**

Run:

```bash
npm run build --prefix app/web/streamlit_components/market_research_navigation
```

Expected: Vite exits `0`; `component_static/index.html` references the newly hashed CSS/JS assets and obsolete generated asset files are removed by Vite empty-out-dir behavior.

- [ ] **Step 6: Run the full scoped automated regression**

Run:

```bash
.venv/bin/python -m pytest tests/test_market_research_navigation.py tests/test_today_home.py tests/test_service_contracts.py::OverviewAutomationContractTests::test_market_research_selector_uses_two_level_internal_widgets -q
npm test --prefix app/web/streamlit_components/market_research_navigation
npm run typecheck --prefix app/web/streamlit_components/market_research_navigation
npm run build --prefix app/web/streamlit_components/market_research_navigation
.venv/bin/python -m py_compile app/web/overview/navigation.py app/web/overview/page.py app/web/overview/market_research_navigation_react_component.py
git diff --check
```

Expected: Python `55 passed, 2 subtests passed`; React `4 passed`; typecheck/build/py_compile/diff check exit `0`.

- [ ] **Step 7: Commit the editorial stylesheet unit**

```bash
git add tests/test_market_research_navigation.py app/web/streamlit_components/market_research_navigation/src/style.css app/web/streamlit_components/market_research_navigation/component_static
git commit -m "디자인: Market Research Editorial Tabs 적용"
```

---

### Task 3: Complete actual Browser QA and durable documentation closeout

**Files:**

- Modify: `.aiworkspace/note/finance/tasks/active/market-research-editorial-navigation-v2-20260722/PLAN.md`
- Modify: `.aiworkspace/note/finance/tasks/active/market-research-editorial-navigation-v2-20260722/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/market-research-editorial-navigation-v2-20260722/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/market-research-editorial-navigation-v2-20260722/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/market-research-editorial-navigation-v2-20260722/RISKS.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/flows/README.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Generate but do not stage: `market-research-editorial-navigation-v2-qa.png`

**Interfaces:**

- Consumes: Task 2 production static bundle served through the existing Streamlit wrapper.
- Produces: verified responsive Editorial Tabs surface and durable current-state documentation.
- Preserves: all unrelated dirty registry, research, run-history, `.superpowers/`, and QA artifacts.

- [ ] **Step 1: Start the production-like Streamlit app**

Run:

```bash
.venv/bin/streamlit run app/web/streamlit_app.py --server.port 8533 --server.headless true --server.runOnSave false
```

Expected: server listens on `http://localhost:8533` without a Python exception.

- [ ] **Step 2: Verify desktop 1280px actual behavior**

Open:

```text
http://localhost:8533/overview?overview_tab=economic-cycle
```

At `1280x900`, verify:

- header title is compact and description is right-aligned on the same row;
- family controls are text tabs with one neutral divider and one active underline;
- no family card fill/radius or family description is visible;
- view group has no outer border/background and only `경제 사이클` is a filled pill;
- navigation right edge aligns with the module content axis;
- iframe/page horizontal overflow is exactly `0`;
- focus-visible is clearly visible on a non-active family and view.

- [ ] **Step 3: Verify all family/view routes and state synchronization**

Click in order and verify URL, active family, active view, and selected module after every click:

```text
시장 환경 -> 경제 사이클 -> 선물 매크로 -> 심리 -> 일정
지수 가치평가 -> S&P 500
종목 리서치 -> 변동 종목 -> 개별 종목
```

Expected canonical query slugs:

```text
economic-cycle, futures-macro, sentiment, events, sp500, market-movers, us-stock
```

- [ ] **Step 4: Verify 760px and 420px responsive behavior**

At `760x900`, verify header copy and three family tabs fit without clipping and page/frame overflow is `0`.

At `420x900`, verify:

- title is `26px` and description moves below it, left-aligned;
- full `시장 환경`, `지수 가치평가`, `종목 리서치` labels remain in three equal columns;
- views use two equal columns and a single view spans both columns;
- no text, focus ring, iframe, or page is clipped; overflow is `0`.

- [ ] **Step 5: Check browser console and save QA evidence**

Expected: no error originating from `market_research_navigation` JS/CSS/component rendering. Record any pre-existing relative `/overview/_stcore/*` direct-route 404 separately rather than treating it as this component's error.

Save the final `1280x900` screenshot as:

```text
/Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev/market-research-editorial-navigation-v2-qa.png
```

Do not stage the screenshot.

- [ ] **Step 6: Update task and durable docs with the exact completed state**

Use these durable statements consistently:

```text
Market Research Editorial Navigation V2는 전체 3/3차를 완료했다.
상단은 compact 30px/26px header, full-width family underline tabs, unframed local view row, active filled view pill을 사용한다.
3-family/7-view, Python URL/session/legacy normalization, changed-view rerun, lazy renderer와 Streamlit fallback은 변경하지 않았다.
1280·760·420px에서 full family labels, 3-column/2-column responsive layout, focus, frame/page overflow 0을 actual Browser QA로 확인했다.
```

Set task `PLAN.md`, `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md` to complete with the exact fresh test counts and any remaining external baseline failures. Update `INDEX.md`, `ROADMAP.md`, `PROJECT_MAP.md`, `flows/README.md`, `WORK_PROGRESS.md`, and `QUESTION_AND_ANALYSIS_LOG.md` only where V1 card/panel wording would otherwise be stale.

- [ ] **Step 7: Run final fresh verification**

Run:

```bash
.venv/bin/python -m pytest tests/test_market_research_navigation.py tests/test_today_home.py tests/test_service_contracts.py::OverviewAutomationContractTests::test_market_research_selector_uses_two_level_internal_widgets -q
npm test --prefix app/web/streamlit_components/market_research_navigation
npm run typecheck --prefix app/web/streamlit_components/market_research_navigation
npm run build --prefix app/web/streamlit_components/market_research_navigation
.venv/bin/python -m py_compile app/web/overview/navigation.py app/web/overview/page.py app/web/overview/market_research_navigation_react_component.py
git diff --check
git status --short
```

Expected: scoped Python/React/typecheck/build/py_compile/diff checks pass. `git status --short` shows only intended doc changes plus preserved unrelated user artifacts and the unstaged QA screenshot.

- [ ] **Step 8: Commit closeout documentation**

```bash
git add .aiworkspace/note/finance/tasks/active/market-research-editorial-navigation-v2-20260722 .aiworkspace/note/finance/docs/INDEX.md .aiworkspace/note/finance/docs/ROADMAP.md .aiworkspace/note/finance/docs/PROJECT_MAP.md .aiworkspace/note/finance/docs/flows/README.md .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git diff --cached --check
git commit -m "문서: Market Research Editorial Tabs 완료 기록"
```

- [ ] **Step 9: Confirm clean ownership boundary**

Run:

```bash
git status --short
git log -5 --oneline
```

Expected: no uncommitted implementation or task-doc changes; registry/research/run-history/`.superpowers/`/generated screenshots remain untouched and unstaged.
