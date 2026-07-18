# Institutional Portfolios Hero Layout Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Institutional Portfolios hero의 보고 근거, manager search, freshness 영역을 하나의 좌우 grid와 수직 기준선으로 정렬한다.

**Architecture:** React에는 데이터 의미를 바꾸지 않는 freshness label wrapper와 snapshot class만 추가한다. CSS는 hero와 controls가 공유하는 단일 column custom property를 사용하고, basis와 freshness 내부 row semantics를 명시한다.

**Tech Stack:** React 18, TypeScript, CSS Grid, Vitest, Python pytest source/runtime contract, Vite, Streamlit Browser QA.

## Global Constraints

- hero와 controls는 같은 `minmax(0, 1.45fr) minmax(320px, 0.75fr)` column contract를 사용한다.
- hero와 controls의 desktop gap은 같은 값 `18px`을 사용한다.
- `보고 기준 분기 | 제출일`은 첫 행 2열, `DB snapshot`과 `SEC 원문 열기`는 각각 전체 폭이다.
- 왼쪽 `기관 / 투자 대가 검색`과 오른쪽 `데이터 기준` label은 같은 typography와 bottom gap을 사용한다.
- controls는 `align-items: start`를 사용한다.
- freshness 첫 행은 action / report period, 둘째 행은 collected time 전체 폭이다.
- 980px 이하 1열 전환, 420px no-overflow contract를 유지한다.
- payload, event, manager search behavior, refresh action, chart, holdings explorer는 변경하지 않는다.
- tracked `component_static`은 검증된 Vite output으로 갱신한다.

---

### Task 1: Shared Hero Grid And Metadata Alignment

**Files:**
- Modify: `tests/test_institutional_portfolios.py`
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/src/InstitutionalPortfoliosWorkbench.tsx`
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/src/style.css`
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/component_static/index.html`
- Replace generated hashes under: `app/web/streamlit_components/institutional_portfolios_workbench/component_static/assets/`
- Modify: `.aiworkspace/note/finance/tasks/active/institutional-portfolios-context-first-redesign-v1-20260718/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/institutional-portfolios-context-first-redesign-v1-20260718/STATUS.md`

**Interfaces:**
- Consumes: existing `payload.hero`, `payload.freshness`, `payload.refresh_action` and `handleRefreshOpen`.
- Produces: layout-only classes `ip-context-basis__snapshot`, `ip-freshness-block`, `ip-context-control-label`; no event or payload change.

- [ ] **Step 1: Write the failing source/runtime layout contract**

Add to `InstitutionalPortfoliosNavigationTests`:

```python
def test_context_hero_basis_and_controls_share_alignment_contract(self) -> None:
    component_source = _component_source()
    style_source = _component_style_source()

    self.assertIn('className="ip-context-basis__snapshot"', component_source)
    self.assertIn('className="ip-freshness-block"', component_source)
    self.assertIn('className="ip-context-control-label">데이터 기준</span>', component_source)
    self.assertIn("--ip-context-columns: minmax(0, 1.45fr) minmax(320px, 0.75fr);", style_source)
    self.assertIn("grid-template-columns: var(--ip-context-columns);", style_source)
    self.assertIn(".ip-context-basis__snapshot", style_source)
    self.assertIn('grid-template-areas: "action period" "time time";', style_source)
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
uv run --with pytest pytest -q tests/test_institutional_portfolios.py::InstitutionalPortfoliosNavigationTests::test_context_hero_basis_and_controls_share_alignment_contract
```

Expected: FAIL because the wrapper/classes/shared grid token do not exist.

- [ ] **Step 3: Add semantic React wrappers without changing data/events**

Change the basis snapshot and freshness rendering to this structure:

```tsx
<div className="ip-context-basis__snapshot">
  <span>DB snapshot</span>
  <strong>{payload.freshness?.last_collected_at || payload.data_state.as_of_label}</strong>
</div>

<div className="ip-freshness-block">
  <span className="ip-context-control-label">데이터 기준</span>
  <div className={`ip-freshness ${payload.freshness?.is_stale ? "ip-freshness--stale" : ""}`}>
    <button type="button" className="ip-freshness__action" onClick={handleRefreshOpen}>...</button>
    <strong>...</strong>
    <em>...</em>
  </div>
</div>
```

- [ ] **Step 4: Implement the shared grid and internal row CSS**

Use one column source and explicit grid areas:

```css
.ip-hero {
  --ip-context-columns: minmax(0, 1.45fr) minmax(320px, 0.75fr);
}

.ip-context-hero__grid,
.ip-context-controls {
  grid-template-columns: var(--ip-context-columns);
  gap: 18px;
}

.ip-context-basis__snapshot,
.ip-context-basis .ip-source-link {
  grid-column: 1 / -1;
}

.ip-context-controls {
  align-items: start;
}

.ip-manager-search > label,
.ip-context-control-label {
  display: block;
  min-height: 18px;
  margin-bottom: 6px;
  color: #334155;
  font-size: 12px;
  font-weight: 800;
  line-height: 18px;
}

.ip-freshness {
  grid-template-columns: minmax(0, 1fr) auto;
  grid-template-areas: "action period" "time time";
}

.ip-freshness__action { grid-area: action; }
.ip-freshness strong { grid-area: period; }
.ip-freshness em {
  grid-area: time;
  white-space: normal;
}
```

Keep existing responsive selectors and explicitly change freshness to one-column areas at `720px` or below.

- [ ] **Step 5: Run focused and full automated GREEN checks**

Run:

```bash
uv run --with pytest pytest -q tests/test_institutional_portfolios.py::InstitutionalPortfoliosNavigationTests::test_context_hero_basis_and_controls_share_alignment_contract
uv run --with pytest pytest -q tests/test_institutional_portfolios.py
npm test -- --reporter=verbose
npm run typecheck
npm run build
git diff --check
```

Expected: Python/Vitest/typecheck/build PASS and no diff whitespace errors.

- [ ] **Step 6: Verify the tracked runtime contract**

Confirm `component_static/index.html` points to the new hash and the built CSS contains `--ip-context-columns`, `ip-freshness-block`, and no `slice(0,80)` runtime path.

- [ ] **Step 7: Perform desktop and 420px Browser QA**

Start the local Streamlit app on a separate port and verify actual Appaloosa/Berkshire data.

Desktop assertions:

```text
abs(contextCopy.left - managerSwitcher.left) <= 1px
abs(contextBasis.left - freshnessBlock.left) <= 1px
abs(contextBasis.right - freshnessBlock.right) <= 1px
abs(managerSearchInput.top - freshnessPanel.top) <= 1px
snapshot spans both basis columns with no empty sibling cell
freshness collected-time scrollWidth <= clientWidth
```

420px assertions:

```text
hero and controls compute one column
page scrollWidth == clientWidth
component scrollWidth == clientWidth
freshness action, period, time remain readable
```

Save one final screenshot under `.playwright-mcp/institutional-portfolios-hero-layout-alignment-final.png` and do not stage it.

- [ ] **Step 8: Record verified closeout and commit**

Update task `RUNS.md` and `STATUS.md` with exact checks and screenshot path, then commit:

```bash
git add tests/test_institutional_portfolios.py \
  app/web/streamlit_components/institutional_portfolios_workbench/src/InstitutionalPortfoliosWorkbench.tsx \
  app/web/streamlit_components/institutional_portfolios_workbench/src/style.css \
  app/web/streamlit_components/institutional_portfolios_workbench/component_static \
  .aiworkspace/note/finance/tasks/active/institutional-portfolios-context-first-redesign-v1-20260718/RUNS.md \
  .aiworkspace/note/finance/tasks/active/institutional-portfolios-context-first-redesign-v1-20260718/STATUS.md
git commit -m "기관 포트폴리오 히어로 열 정렬 보완"
```
