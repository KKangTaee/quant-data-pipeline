# Institutional Portfolios Manager Rail Visibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Institutional Portfolios manager rail이 desktop / tablet / mobile에서 부분 카드와 강제 말줄임 없이 완전한 카드 단위로 보이게 한다.

**Architecture:** 기존 React `tablist -> button` markup, manager payload, selection event, scroll-position ref는 유지한다. Source CSS가 rail을 single-row horizontal grid로 배치하고 breakpoint별 4 / 3 / 1 card width, mandatory scroll snap, natural text wrapping, effective scrollbar spacing을 소유하며 tracked Vite bundle과 source/runtime contract test가 이를 보호한다.

**Tech Stack:** React 18, TypeScript, CSS Grid, CSS Scroll Snap, Vite 6, Vitest 4, Python `unittest` / pytest wrapper, Streamlit custom component, in-app Browser QA.

## Global Constraints

- Desktop `> 980px`는 완전한 카드 4개, tablet `721px–980px`는 3개, mobile `<= 720px`는 1개를 보여준다.
- rail 경계에 다음 카드가 부분 노출되거나 scroll 정착 위치가 카드 중간에 머물지 않는다.
- alias, SEC filer name, report period의 강제 `nowrap + ellipsis`를 제거하고 카드 안에서 자연스럽게 줄바꿈한다.
- native horizontal scrollbar와 기존 `managerRailRef` scroll-position 보존은 유지한다.
- manager 검색, CIK 선택, pending / disabled state, payload, DB / provider / ingestion은 변경하지 않는다.
- user-owned root PNG와 `.playwright-mcp/` screenshot은 stage하거나 commit하지 않는다.

## File Structure

- Modify: `tests/test_institutional_portfolios.py`
  - manager rail source CSS와 tracked runtime CSS의 complete-card / wrapping / spacing 계약을 보호한다.
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/src/style.css`
  - breakpoint별 card width, horizontal grid, snap, text wrapping, effective scrollbar spacing을 소유한다.
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/component_static/index.html`
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/component_static/assets/*`
  - Vite build가 생성한 tracked runtime을 갱신한다.
- Modify: `.aiworkspace/note/finance/tasks/active/institutional-portfolios-context-first-redesign-v1-20260718/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/institutional-portfolios-context-first-redesign-v1-20260718/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/institutional-portfolios-context-first-redesign-v1-20260718/RISKS.md`
  - actual Browser QA, 완료 상태, 남은 위험을 기록한다.

---

### Task 1: Add A Failing Complete-Card Rail Contract

**Files:**
- Modify: `tests/test_institutional_portfolios.py` inside `InstitutionalPortfoliosNavigationTests`

**Interfaces:**
- Consumes: `_component_style_source() -> str`, `_css_rule(style_source: str, *selectors: str) -> str`.
- Produces: `test_manager_rail_shows_complete_cards_and_wraps_labels`, a source/runtime presentation regression.

- [ ] **Step 1: Add the failing test after the hero alignment contract**

```python
def test_manager_rail_shows_complete_cards_and_wraps_labels(self) -> None:
    style_source = _component_style_source()
    rail_rule = _css_rule(style_source, ".ip-manager-rail")
    favorites_rule = _css_rule(style_source, ".ip-manager-favorites")
    compact_card_rule = _css_rule(style_source, ".ip-manager-favorites .ip-manager-tab")
    text_rule = _css_rule(style_source, ".ip-manager-tab strong", ".ip-manager-tab span")
    tablet_style = style_source[
        style_source.index("@media (max-width: 980px) {") : style_source.index("@media (max-width: 720px) {")
    ]
    mobile_style = style_source[
        style_source.index("@media (max-width: 720px) {") : style_source.index("@media (max-width: 420px) {")
    ]
    tablet_rail_rule = _css_rule(tablet_style, ".ip-manager-rail")
    mobile_rail_rule = _css_rule(mobile_style, ".ip-manager-rail")

    for declaration in (
        "display: grid;",
        "grid-auto-flow: column;",
        "grid-auto-columns: var(--ip-manager-card-width);",
        "align-items: stretch;",
        "--ip-manager-card-width: calc((100% - 24px) / 4);",
        "scroll-snap-type: x mandatory;",
    ):
        self.assertIn(declaration, rail_rule)
    self.assertIn("margin: 0 0 12px;", favorites_rule)
    self.assertIn("padding-bottom: 10px;", favorites_rule)
    self.assertIn("min-width: 0;", compact_card_rule)
    self.assertIn("width: 100%;", compact_card_rule)
    self.assertIn("height: auto;", compact_card_rule)
    self.assertIn("scroll-snap-align: start;", compact_card_rule)
    self.assertIn("scroll-snap-stop: always;", compact_card_rule)
    for declaration in (
        "overflow: visible;",
        "text-overflow: clip;",
        "white-space: normal;",
        "overflow-wrap: anywhere;",
    ):
        self.assertIn(declaration, text_rule)
    self.assertIn("--ip-manager-card-width: calc((100% - 16px) / 3);", tablet_rail_rule)
    self.assertIn("--ip-manager-card-width: 100%;", mobile_rail_rule)

    build_dir = Path("app/web/streamlit_components/institutional_portfolios_workbench/component_static")
    index_source = (build_dir / "index.html").read_text(encoding="utf-8")
    css_paths = re.findall(r'href="\./(assets/[^"]+\.css)"', index_source)
    self.assertEqual(len(css_paths), 1)
    runtime_css = (build_dir / css_paths[0]).read_text(encoding="utf-8")
    runtime_rail_rule = _css_rule(runtime_css, ".ip-manager-rail")
    runtime_favorites_rule = _css_rule(runtime_css, ".ip-manager-favorites")
    runtime_card_rule = _css_rule(runtime_css, ".ip-manager-favorites .ip-manager-tab")
    runtime_text_rule = _css_rule(runtime_css, ".ip-manager-tab strong", ".ip-manager-tab span")
    runtime_tablet_style = runtime_css[
        runtime_css.index("@media(max-width:980px){") : runtime_css.index("@media(max-width:720px){")
    ]
    runtime_mobile_style = runtime_css[
        runtime_css.index("@media(max-width:720px){") : runtime_css.index("@media(max-width:420px){")
    ]
    runtime_tablet_rule = _css_rule(runtime_tablet_style, ".ip-manager-rail")
    runtime_mobile_rule = _css_rule(runtime_mobile_style, ".ip-manager-rail")

    self.assertIn("display:grid", runtime_rail_rule)
    self.assertIn("grid-auto-flow:column", runtime_rail_rule)
    self.assertIn("grid-auto-columns:var(--ip-manager-card-width)", runtime_rail_rule)
    self.assertIn("align-items:stretch", runtime_rail_rule)
    self.assertIn("--ip-manager-card-width:calc((100% - 24px)/4)", runtime_rail_rule)
    self.assertIn("scroll-snap-type:x mandatory", runtime_rail_rule)
    self.assertIn("margin:0 0 12px", runtime_favorites_rule)
    self.assertIn("padding-bottom:10px", runtime_favorites_rule)
    self.assertIn("scroll-snap-align:start", runtime_card_rule)
    self.assertIn("scroll-snap-stop:always", runtime_card_rule)
    self.assertIn("white-space:normal", runtime_text_rule)
    self.assertIn("overflow-wrap:anywhere", runtime_text_rule)
    self.assertIn("--ip-manager-card-width:calc((100% - 16px)/3)", runtime_tablet_rule)
    self.assertIn("--ip-manager-card-width:100%", runtime_mobile_rule)
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
uv run --with pytest pytest -q tests/test_institutional_portfolios.py::InstitutionalPortfoliosNavigationTests::test_manager_rail_shows_complete_cards_and_wraps_labels
```

Expected: FAIL because `.ip-manager-rail` still contains `display: flex` and the complete-card declarations are absent.

---

### Task 2: Implement The Source CSS Contract

**Files:**
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/src/style.css:80-98`
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/src/style.css:203-209`
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/src/style.css` inside `@media (max-width: 980px)` and `@media (max-width: 720px)`
- Test: `tests/test_institutional_portfolios.py`

**Interfaces:**
- Consumes: existing `.ip-manager-rail`, `.ip-manager-favorites`, `.ip-manager-tab` selectors and 8px gap.
- Produces: exact source CSS contract protected by Task 1; React markup and events remain unchanged.

- [ ] **Step 1: Replace flex sizing with the desktop complete-card grid**

```css
.ip-manager-rail {
  --ip-manager-card-width: calc((100% - 24px) / 4);
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: var(--ip-manager-card-width);
  align-items: stretch;
  gap: 8px;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
}

.ip-manager-favorites {
  min-width: 0;
  margin: 0 0 12px;
  padding-bottom: 10px;
}

.ip-manager-favorites .ip-manager-tab {
  min-width: 0;
  width: 100%;
  height: auto;
  min-height: 64px;
  padding: 8px 10px;
  scroll-snap-align: start;
  scroll-snap-stop: always;
}
```

- [ ] **Step 2: Replace forced single-line clipping with natural wrapping**

```css
.ip-manager-tab strong,
.ip-manager-tab span {
  display: block;
  overflow: visible;
  text-overflow: clip;
  white-space: normal;
  overflow-wrap: anywhere;
}
```

- [ ] **Step 3: Add tablet and mobile card-width overrides**

Inside `@media (max-width: 980px)`:

```css
.ip-manager-rail {
  --ip-manager-card-width: calc((100% - 16px) / 3);
}
```

Inside `@media (max-width: 720px)`:

```css
.ip-manager-rail {
  --ip-manager-card-width: 100%;
}
```

- [ ] **Step 4: Run the focused test and confirm the expected intermediate failure**

Run:

```bash
uv run --with pytest pytest -q tests/test_institutional_portfolios.py::InstitutionalPortfoliosNavigationTests::test_manager_rail_shows_complete_cards_and_wraps_labels
```

Expected: source assertions pass, but runtime CSS assertions still FAIL because `component_static` has not been rebuilt.

- [ ] **Step 5: Build the tracked component runtime**

Run:

```bash
npm --prefix app/web/streamlit_components/institutional_portfolios_workbench run build
```

Expected: Vite exits 0, transforms the existing component modules, and writes a new hashed CSS asset plus updated `component_static/index.html`.

- [ ] **Step 6: Run the focused test and verify GREEN**

Run:

```bash
uv run --with pytest pytest -q tests/test_institutional_portfolios.py::InstitutionalPortfoliosNavigationTests::test_manager_rail_shows_complete_cards_and_wraps_labels
```

Expected: `1 passed`.

- [ ] **Step 7: Run frontend and complete focused regressions**

```bash
npm --prefix app/web/streamlit_components/institutional_portfolios_workbench test -- --reporter=verbose
npm --prefix app/web/streamlit_components/institutional_portfolios_workbench run typecheck
uv run --with pytest pytest -q tests/test_institutional_portfolios.py
git diff --check
```

Expected: Vitest passes, TypeScript exits 0, institutional portfolio suite passes, and `git diff --check` prints nothing.

- [ ] **Step 8: Commit the CSS, regression, and tracked runtime together**

```bash
git add tests/test_institutional_portfolios.py \
  app/web/streamlit_components/institutional_portfolios_workbench/src/style.css \
  app/web/streamlit_components/institutional_portfolios_workbench/component_static/index.html \
  app/web/streamlit_components/institutional_portfolios_workbench/component_static/assets
git commit -m "기관 포트폴리오 카드 레일 잘림 수정"
```

---

### Task 3: Verify Actual Desktop, Tablet, Mobile Behavior

**Files:**
- Generated only: `.playwright-mcp/institutional-portfolios-manager-rail-visibility-final.png`

**Interfaces:**
- Consumes: actual Institutional Portfolios Streamlit page and the built tracked component.
- Produces: measured evidence for 4 / 3 / 1 complete cards, wrapping, snap, selection, and no overflow.

- [ ] **Step 1: Start a separate local Streamlit server on an unused port**

First confirm port `8527` is unused. Then run:

```bash
.venv/bin/python -m streamlit run app/web/streamlit_app.py \
  --server.port 8527 \
  --server.headless true \
  --server.runOnSave false \
  --server.fileWatcherType none
```

Expected: the dedicated server reports `http://localhost:8527`. If the port is already occupied, choose another explicit unused port and record it in `RUNS.md`; do not stop or reuse the existing process.

- [ ] **Step 2: Measure desktop behavior**

At a desktop viewport matching the reported screenshot:

- rail client width equals `4 * card width + 3 * 8px` within 1px rounding tolerance;
- exactly four cards have a non-zero intersection with the rail viewport at `scrollLeft == 0`;
- the fifth card starts at or beyond the rail right edge and has zero visible intersection;
- Berkshire, Pershing, and Appaloosa filer names use `white-space: normal` and have `scrollWidth <= clientWidth`;
- the scrollbar has effective bottom spacing and no card overlaps it.

- [ ] **Step 3: Measure tablet and 420px mobile behavior**

- At `721px–980px`, verify the rail equation `3 * card width + 2 * 8px == rail width` within 1px.
- At `420px`, verify one card width equals the rail client width within 1px.
- At both widths, page and iframe `scrollWidth == clientWidth`.

- [ ] **Step 4: Verify scroll snap and manager selection**

Scroll the rail horizontally and wait for layout settlement. Confirm `scrollLeft` aligns to `N * (card width + 8px)` within 1px, then select a newly visible manager and verify the hero CIK / manager name updates without console errors.

- [ ] **Step 5: Capture final screenshot and shut down QA resources**

Save one final screenshot as `.playwright-mcp/institutional-portfolios-manager-rail-visibility-final.png`, reset viewport overrides, close/finalize the QA tab, and stop only the dedicated server started in Step 1. Do not stage the screenshot.

---

### Task 4: Close Documentation And Final Verification

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/institutional-portfolios-context-first-redesign-v1-20260718/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/institutional-portfolios-context-first-redesign-v1-20260718/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/institutional-portfolios-context-first-redesign-v1-20260718/RISKS.md`

**Interfaces:**
- Consumes: exact automated outputs and Browser QA measurements from Tasks 2–3.
- Produces: concise durable handoff for the completed layout follow-up.

- [ ] **Step 1: Record exact results**

Append one dated manager-rail follow-up entry to `RUNS.md` containing:

- RED failure reason;
- focused and full test counts;
- Vitest, typecheck, Vite build, and diff-check outcomes;
- desktop / tablet / 420px card-count equations;
- scroll snap, selection, no-overflow, console results;
- ignored screenshot path.

- [ ] **Step 2: Update status and risks without reopening unrelated scope**

Add a `STATUS.md` progress line and current-step paragraph stating the approved closeout follow-up is complete. Move the manager-rail clipping risk to closed in `RISKS.md`; keep historical filing backfill, verified security master, and full-payload serialization unchanged.

- [ ] **Step 3: Run final verification from the committed implementation state**

```bash
uv run --with pytest pytest -q tests/test_institutional_portfolios.py
npm --prefix app/web/streamlit_components/institutional_portfolios_workbench test -- --reporter=verbose
npm --prefix app/web/streamlit_components/institutional_portfolios_workbench run typecheck
npm --prefix app/web/streamlit_components/institutional_portfolios_workbench run build
git diff --check
git status --short
```

Expected: all checks pass; only intended documentation changes and pre-existing user-owned PNG files remain unstaged.

- [ ] **Step 4: Commit documentation closeout**

```bash
git add \
  .aiworkspace/note/finance/tasks/active/institutional-portfolios-context-first-redesign-v1-20260718/STATUS.md \
  .aiworkspace/note/finance/tasks/active/institutional-portfolios-context-first-redesign-v1-20260718/RUNS.md \
  .aiworkspace/note/finance/tasks/active/institutional-portfolios-context-first-redesign-v1-20260718/RISKS.md
git commit -m "기관 포트폴리오 카드 레일 QA 정리"
```

- [ ] **Step 5: Inspect final history and handoff state**

```bash
git log -4 --oneline
git status --short
```

Expected: design, plan, implementation, and QA commits are visible; user-owned untracked PNG files remain untouched.
