# Market Movers Hybrid Visual System V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 기존 Market Movers selected-state와 data contract를 유지하면서 A안 통합 리포트형 visual system을 React one-shell에 적용한다.

**Architecture:** `MarketMoversDecisionWorkbench`만 presentation refactor 대상으로 삼는다. 기존 `market_movers_decision_workbench_v1` payload와 Streamlit event를 그대로 소비하며, React에 payload-derived `MarketPulse`를 추가하고 CSS를 unified surface/card hierarchy로 교체한다. Python service, DB loader, ranking/financial 계산은 변경하지 않는다.

**Tech Stack:** React 18, TypeScript 5.7, CSS, Vite 6, Streamlit custom component, pytest source contracts, in-app Browser QA.

## Global Constraints

- outer surface는 `20px` radius, `1px solid #d8e4ea`, `linear-gradient(145deg, #f8fbfd 0%, #f2f7f9 62%, #eef5f7 100%)`를 사용한다.
- primary accent는 `#397fb7`, trust accent는 `#2f7f73`, positive는 `#19765f`, negative는 `#b9554c`, warning은 `#9a6a22`로 제한한다.
- 기존 teal top border와 purple decorative accent를 제거한다.
- desktop `>= 900px`에서 ranking/breadth `1.62fr / 1fr`, chart/readout `7fr / 3fr`을 유지한다.
- `set_control`, `select_symbol`, payload schema version과 Python session-state key를 변경하지 않는다.
- conditional outlook, prediction, DB/service/read-model 변경을 포함하지 않는다.
- generated QA image, `.superpowers/`, registry/saved/run-history artifact를 stage하지 않는다.

## File Structure

- `tests/test_overview_market_movers_decision_ui.py`: A안 DOM/CSS/event/responsive source contracts.
- `app/web/streamlit_components/market_movers_workbench/src/MarketMoversWorkbench.tsx`: hierarchy, payload-derived pulse, tab accessibility.
- `app/web/streamlit_components/market_movers_workbench/src/style.css`: visual tokens, surface/card hierarchy, responsive/focus rules.
- `app/web/streamlit_components/market_movers_workbench/component_static/`: Vite-generated canonical build; 직접 편집하지 않는다.
- `.aiworkspace/note/finance/tasks/active/market-movers-hybrid-visual-system-v1-20260720/`: 상세 실행 근거.
- `.aiworkspace/note/finance/docs/{INDEX,ROADMAP,PROJECT_MAP}.md`와 root handoff logs: 완료된 durable current-state.

---

### Task 1: Unified Surface And Command Hierarchy

**Files:**
- Modify: `tests/test_overview_market_movers_decision_ui.py:270-301`
- Modify: `app/web/streamlit_components/market_movers_workbench/src/MarketMoversWorkbench.tsx:484-523`
- Modify: `app/web/streamlit_components/market_movers_workbench/src/style.css:1-140`

**Interfaces:**
- Consumes: `MarketMoversDecisionWorkbenchPayload.command_line`, `.trust`; `onControl(control, value)`.
- Produces: `.mm-decision__surface-header`, `.mm-decision__command-band`; 기존 control event path는 유지한다.

- [x] **Step 1: Write the failing visual-foundation source contract**

```python
def test_decision_shell_uses_approved_hybrid_visual_foundation() -> None:
    from pathlib import Path

    source = Path(
        "app/web/streamlit_components/market_movers_workbench/src/MarketMoversWorkbench.tsx"
    ).read_text(encoding="utf-8")
    style = Path(
        "app/web/streamlit_components/market_movers_workbench/src/style.css"
    ).read_text(encoding="utf-8")
    decision_style = style[: style.index(".mm-workbench {")]

    assert 'className="mm-decision__surface-header"' in source
    assert '<h1>변동 종목</h1>' in source
    assert 'className="mm-decision__command-band"' in source
    assert "--mm-accent: #397fb7;" in decision_style
    assert "--mm-trust: #2f7f73;" in decision_style
    assert "border-radius: 20px;" in decision_style
    assert "border: 1px solid #d8e4ea;" in decision_style
    assert "linear-gradient(145deg, #f8fbfd 0%, #f2f7f9 62%, #eef5f7 100%)" in decision_style
    assert "border-top: 4px solid" not in decision_style
```

- [x] **Step 2: Run the new test and verify RED**

```bash
.venv/bin/python -m pytest tests/test_overview_market_movers_decision_ui.py::test_decision_shell_uses_approved_hybrid_visual_foundation -q
```

Expected: FAIL because the classes, `h1`, approved tokens, radius and gradient are absent.

- [x] **Step 3: Implement the approved hero and command-band DOM**

`MarketMoversCommandLine`의 기존 `select` mapping을 보존하고 다음 hierarchy로 감싼다.

```tsx
<header className="mm-decision__command">
  <div className="mm-decision__surface-header">
    <div className="mm-decision__hero-copy">
      <div className="mm-decision__eyebrow">MARKET MOVERS</div>
      <h1>변동 종목</h1>
      <p>무엇이 움직였는지 찾고, 시장 확산을 확인한 뒤, 선택 종목의 저장 근거를 조사합니다.</p>
    </div>
    <div className={`mm-decision__trust mm-decision__trust--${trustState.toLowerCase()}`}>
      <span>자료 상태</span><strong>{trustState}</strong><small>랭킹 가능 {denominator}</small>
    </div>
  </div>
  <section className="mm-decision__command-band" aria-label="변동 종목 탐색 조건">
    <div className="mm-decision__controls">
      {payload.command_line.controls.map((control) => (
        <label className="mm-decision__control" key={control.id}>
          <span>{control.label}</span>
          <select disabled={control.disabled} onChange={(event) => onControl(control, event.target.value)} value={control.value}>
            {control.options.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
          </select>
        </label>
      ))}
    </div>
  </section>
</header>
```

- [x] **Step 4: Implement the approved foundation CSS**

```css
.mm-decision {
  --mm-accent: #397fb7;
  --mm-trust: #2f7f73;
  --mm-positive: #19765f;
  --mm-negative: #b9554c;
  --mm-warning: #9a6a22;
  --mm-ink: #203c50;
  --mm-ink-secondary: #456377;
  --mm-muted: #748793;
  --mm-line: #d8e4ea;
  --mm-card-line: #cddde5;
  background: linear-gradient(145deg, #f8fbfd 0%, #f2f7f9 62%, #eef5f7 100%);
  border: 1px solid #d8e4ea;
  border-radius: 20px;
  box-shadow: 0 18px 45px rgba(30, 56, 75, 0.07);
  color: var(--mm-ink);
  padding: 28px;
}

.mm-decision__surface-header { display: flex; gap: 28px; justify-content: space-between; }
.mm-decision__surface-header h1 { font-size: clamp(1.7rem, 2.8vw, 2.35rem); letter-spacing: -0.045em; margin: 6px 0 0; }
.mm-decision__command { border-bottom: 0; padding-bottom: 0; }
.mm-decision__command-band { background: rgba(255, 255, 255, 0.72); border: 1px solid var(--mm-card-line); border-radius: 14px; margin-top: 20px; padding: 10px; }
.mm-decision__controls { display: grid; gap: 0; grid-template-columns: 1.2fr 0.9fr 1.15fr 0.75fr; margin-top: 0; }
.mm-decision__control { gap: 6px; padding: 2px 12px; }
.mm-decision__control + .mm-decision__control { border-left: 1px solid var(--mm-line); }
.mm-decision__control select { background-color: transparent; border-color: transparent; border-radius: 8px; color: var(--mm-ink); }
```

- [x] **Step 5: Run focused tests and verify GREEN**

```bash
.venv/bin/python -m pytest \
  tests/test_overview_market_movers_decision_ui.py::test_decision_shell_uses_approved_hybrid_visual_foundation \
  tests/test_overview_market_movers_decision_ui.py::test_decision_react_shell_owns_ranking_breadth_and_selected_research -q
```

Expected: `2 passed`.

- [x] **Step 6: Commit Task 1**

```bash
git add tests/test_overview_market_movers_decision_ui.py app/web/streamlit_components/market_movers_workbench/src/MarketMoversWorkbench.tsx app/web/streamlit_components/market_movers_workbench/src/style.css
git commit -m "변동 종목 통합 리포트 surface를 적용"
```

---

### Task 2: Market Pulse And Unified Decision Cards

**Files:**
- Modify: `tests/test_overview_market_movers_decision_ui.py:270-326`
- Modify: `app/web/streamlit_components/market_movers_workbench/src/MarketMoversWorkbench.tsx:468-683,944-979`
- Modify: `app/web/streamlit_components/market_movers_workbench/src/style.css:135-441`

**Interfaces:**
- Consumes: `payload.ranking`, `payload.group_context.sector[period].flow`, `payload.trust.state`.
- Produces: `MarketPulse({ payload })`, `.mm-decision__pulse`, unified ranking/breadth cards.

- [x] **Step 1: Write the failing pulse/card contract**

```python
def test_decision_shell_connects_market_pulse_to_unified_decision_cards() -> None:
    from pathlib import Path

    source = Path("app/web/streamlit_components/market_movers_workbench/src/MarketMoversWorkbench.tsx").read_text(encoding="utf-8")
    style = Path("app/web/streamlit_components/market_movers_workbench/src/style.css").read_text(encoding="utf-8")
    decision_style = style[: style.index(".mm-workbench {")]

    assert "function MarketPulse" in source
    assert '<section className="mm-decision__pulse"' in source
    assert '<MarketPulse payload={payload} />' in source
    assert 'className="mm-decision__pulse-item"' in source
    assert "border-radius: 16px;" in decision_style
    assert "grid-template-columns: minmax(0, 1.62fr) minmax(320px, 1fr);" in decision_style
    assert "#7c3aed" not in decision_style
    assert 'id: "set_control"' in source
    assert 'id: "select_symbol"' in source
```

- [x] **Step 2: Run the new test and verify RED**

```bash
.venv/bin/python -m pytest tests/test_overview_market_movers_decision_ui.py::test_decision_shell_connects_market_pulse_to_unified_decision_cards -q
```

Expected: FAIL because pulse DOM/CSS is absent and purple remains.

- [x] **Step 3: Add the payload-derived MarketPulse component**

```tsx
const PERIOD_LABELS: Record<string, string> = { daily: "일간", weekly: "주간", monthly: "월간" };

function MarketPulse({ payload }: { payload: MarketMoversDecisionWorkbenchPayload }) {
  const period = payload.ranking.period;
  const leadingSector = (payload.group_context.sector?.[period]?.flow || [])[0];
  const items = [
    { label: "관측 기준", value: `${PERIOD_LABELS[period] || period} · ${payload.ranking.label}` },
    { label: "표시 종목", value: `${payload.ranking.rows.length.toLocaleString()}개` },
    leadingSector ? { label: "선도 섹터", value: textValue(leadingSector, "group", "Group"), detail: formatSignedPercent(numberValue(leadingSector, "relative_strength_pp")) } : null,
    { label: "자료 상태", value: String(payload.trust.state || "UNKNOWN") },
  ].filter(Boolean) as Array<{ label: string; value: string; detail?: string }>;

  return <section className="mm-decision__pulse" aria-label="현재 시장 관측 요약">
    {items.map((item) => <div className="mm-decision__pulse-item" key={item.label}>
      <small>{item.label}</small><strong>{item.value}</strong>{item.detail ? <span>{item.detail}</span> : null}
    </div>)}
  </section>;
}
```

`MarketMoversDecisionWorkbench`에서 command line 다음에 `<MarketPulse payload={payload} />`를 렌더한다.

- [x] **Step 4: Unify ranking and breadth card styling**

```css
.mm-decision__pulse { background: var(--mm-line); border: 1px solid var(--mm-line); border-radius: 13px; display: grid; gap: 1px; grid-template-columns: repeat(4, minmax(0, 1fr)); margin-top: 14px; overflow: hidden; }
.mm-decision__pulse-item { background: rgba(255, 255, 255, 0.78); display: grid; gap: 3px; min-width: 0; padding: 12px 14px; }
.mm-decision__pulse-item small, .mm-decision__pulse-item span { color: var(--mm-muted); font-size: 0.68rem; }
.mm-decision__pulse-item strong { color: var(--mm-ink); font-size: 0.88rem; }
.mm-decision__workbench { gap: 14px; grid-template-columns: minmax(0, 1.62fr) minmax(320px, 1fr); margin-top: 14px; }
.mm-decision__ranking, .mm-decision__breadth { background: rgba(255, 255, 255, 0.88); border: 1px solid var(--mm-card-line); border-radius: 16px; box-shadow: 0 10px 28px rgba(33, 53, 72, 0.04); min-width: 0; overflow: hidden; }
.mm-decision__flow-list > button.is-selected { background: color-mix(in srgb, var(--mm-accent) 8%, #ffffff); box-shadow: inset 3px 0 var(--mm-accent); }
.mm-decision__flow-track i { background: var(--mm-accent); }
.mm-decision__group-detail > div:first-child > span { color: var(--mm-accent); }
```

ranking row의 inline semantic colors를 `#b9554c`와 `#19765f`로 교체하고 selection rail은 `var(--mm-accent)`로 분리한다.

- [x] **Step 5: Run pulse/card interaction tests**

```bash
.venv/bin/python -m pytest \
  tests/test_overview_market_movers_decision_ui.py::test_decision_shell_connects_market_pulse_to_unified_decision_cards \
  tests/test_overview_market_movers_decision_ui.py::test_decision_react_shell_owns_ranking_breadth_and_selected_research \
  tests/test_overview_market_movers_decision_ui.py::test_decision_shell_selection_event_updates_symbol_once -q
```

Expected: `3 passed`.

- [x] **Step 6: Commit Task 2**

```bash
git add tests/test_overview_market_movers_decision_ui.py app/web/streamlit_components/market_movers_workbench/src/MarketMoversWorkbench.tsx app/web/streamlit_components/market_movers_workbench/src/style.css
git commit -m "변동 종목 시장 pulse와 결정 카드를 통일"
```

---

### Task 3: Selected Research, Responsive Hierarchy, And Accessibility

**Files:**
- Modify: `tests/test_overview_market_movers_decision_ui.py:303-326`
- Modify: `app/web/streamlit_components/market_movers_workbench/src/MarketMoversWorkbench.tsx:689-938`
- Modify: `app/web/streamlit_components/market_movers_workbench/src/style.css:442-719,1717-1805`

**Interfaces:**
- Consumes: existing `QuickResearch`, `StockResearchTabs`, `FinancialFactorChart` props and local state.
- Produces: active-blue-underline research tabs, stable 70/30 chart, focus-visible and 900/600 responsive contracts.

- [x] **Step 1: Write the failing research/responsive/accessibility contract**

```python
def test_decision_research_uses_report_family_tabs_and_responsive_focus_contract() -> None:
    from pathlib import Path

    source = Path("app/web/streamlit_components/market_movers_workbench/src/MarketMoversWorkbench.tsx").read_text(encoding="utf-8")
    style = Path("app/web/streamlit_components/market_movers_workbench/src/style.css").read_text(encoding="utf-8")
    decision_style = style[: style.index(".mm-workbench {")]

    assert 'aria-selected={tab === id}' in source
    assert 'aria-controls={`mm-decision-panel-${id}`}' in source
    assert 'id={`mm-decision-tab-${id}`}' in source
    assert "border-bottom: 2px solid transparent;" in decision_style
    assert "border-bottom-color: var(--mm-accent);" in decision_style
    assert ".mm-decision button:focus-visible" in decision_style
    assert ".mm-decision select:focus-visible" in decision_style
    assert "outline: 2px solid rgba(57, 127, 183, 0.35);" in decision_style
    assert "@media (max-width: 900px)" in style
    assert "@media (max-width: 600px)" in style
    assert "grid-template-columns: minmax(0, 7fr) minmax(220px, 3fr);" in decision_style
    assert "payload.ranking.empty_reason" in source
    assert 'className="mm-decision__empty"' in source
    assert "mm-decision__trust--${trustState.toLowerCase()}" in source
```

- [x] **Step 2: Run the new test and verify RED**

```bash
.venv/bin/python -m pytest tests/test_overview_market_movers_decision_ui.py::test_decision_research_uses_report_family_tabs_and_responsive_focus_contract -q
```

Expected: FAIL because tab ARIA linkage, underline pattern, focus-visible and 600px breakpoint are absent.

- [x] **Step 3: Add tab selection and panel linkage semantics**

```tsx
<button
  aria-controls={`mm-decision-panel-${id}`}
  aria-selected={tab === id}
  className={tab === id ? "is-active" : ""}
  id={`mm-decision-tab-${id}`}
  key={id}
  onClick={() => setTab(id)}
  role="tab"
  type="button"
>{label}</button>
```

기존 conditional tab content는 아래 wrapper 안에 둔다.

```tsx
<div aria-labelledby={`mm-decision-tab-${tab}`} id={`mm-decision-panel-${tab}`} role="tabpanel">
  {!research ? (
    <div className="mm-decision__research-loading">선택 종목의 저장 근거를 불러오는 중입니다.</div>
  ) : tab === "price" ? (
    <PriceMomentumChart research={research} />
  ) : tab === "financial" ? (
    <FinancialFactorChart controls={payload.selection.financial_controls} research={research} />
  ) : (
    <div className="mm-decision__events-panel">
      <strong>뉴스·공시 근거</strong>
      <p>현재 저장된 재무제표 반영 상태와 선택 종목의 뉴스·SEC 조사 action을 같은 symbol에 연결합니다.</p>
    </div>
  )}
</div>
```

- [x] **Step 4: Apply selected-evidence card, underline tab and focus CSS**

```css
.mm-decision__quick, .mm-decision__research { background: rgba(255, 255, 255, 0.88); border: 1px solid var(--mm-card-line); border-radius: 16px; box-shadow: 0 10px 28px rgba(33, 53, 72, 0.04); overflow: hidden; }
.mm-decision__quick { grid-template-columns: minmax(200px, 1.2fr) minmax(300px, 1.5fr) auto; margin-top: 14px; }
.mm-decision__quick > button { background: var(--mm-accent); border-color: var(--mm-accent); border-radius: 10px; }
.mm-decision__tabs { gap: 18px; }
.mm-decision__tabs button { background: transparent; border: 0; border-bottom: 2px solid transparent; color: var(--mm-muted); padding: 8px 2px 6px; }
.mm-decision__tabs button.is-active { background: transparent; border-bottom-color: var(--mm-accent); color: var(--mm-ink); }
.mm-decision button:focus-visible, .mm-decision select:focus-visible { outline: 2px solid rgba(57, 127, 183, 0.35); outline-offset: 2px; }
.mm-decision__chart-layout { grid-template-columns: minmax(0, 7fr) minmax(220px, 3fr); min-height: 320px; }
```

- [x] **Step 5: Implement the exact responsive hierarchy**

```css
@media (max-width: 900px) {
  .mm-decision { padding: 22px; }
  .mm-decision__workbench { grid-template-columns: minmax(0, 1fr); }
  .mm-decision__controls, .mm-decision__pulse { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .mm-decision__quick { grid-template-columns: minmax(0, 1fr) auto; }
}

@media (max-width: 600px) {
  .mm-decision { border-radius: 16px; padding: 16px; }
  .mm-decision__surface-header, .mm-decision__research-head { align-items: flex-start; flex-direction: column; }
  .mm-decision__controls, .mm-decision__pulse, .mm-decision__quick, .mm-decision__chart-layout, .mm-decision__financial-control-row { grid-template-columns: minmax(0, 1fr); }
  .mm-decision__control + .mm-decision__control { border-left: 0; border-top: 1px solid var(--mm-line); }
  .mm-decision__rank-row { grid-template-columns: 24px minmax(0, 1fr) minmax(72px, auto); }
  .mm-decision__rank-sector, .mm-decision__rank-volume { display: none; }
  .mm-decision__chart-readout { border-left: 0; border-top: 1px solid var(--mm-line); grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
```

기존 760px decision rules는 새 900/600 hierarchy와 충돌하지 않도록 제거하고 legacy `.mm-workbench` rules만 남긴다.

- [x] **Step 6: Run research and regression tests**

```bash
.venv/bin/python -m pytest \
  tests/test_overview_market_movers_decision_ui.py::test_decision_research_uses_report_family_tabs_and_responsive_focus_contract \
  tests/test_overview_market_movers_decision_ui.py::test_decision_research_keeps_financial_period_and_factor_controls_separate \
  tests/test_overview_market_movers_decision_ui.py::test_decision_shell_selected_symbol_and_financial_controls_are_independent -q
```

Expected: `3 passed`.

- [x] **Step 7: Commit Task 3**

```bash
git add tests/test_overview_market_movers_decision_ui.py app/web/streamlit_components/market_movers_workbench/src/MarketMoversWorkbench.tsx app/web/streamlit_components/market_movers_workbench/src/style.css
git commit -m "변동 종목 조사 surface와 반응형 구조를 정리"
```

---

### Task 4: Production Build, Actual Browser QA, And Closeout

**Files:**
- Replace via build: `app/web/streamlit_components/market_movers_workbench/component_static/index.html`
- Replace via build: `app/web/streamlit_components/market_movers_workbench/component_static/assets/index-*.css`
- Replace via build: `app/web/streamlit_components/market_movers_workbench/component_static/assets/index-*.js`
- Modify: `.aiworkspace/note/finance/tasks/active/market-movers-hybrid-visual-system-v1-20260720/{STATUS,NOTES,RUNS,RISKS}.md`
- Modify: `.aiworkspace/note/finance/{WORK_PROGRESS,QUESTION_AND_ANALYSIS_LOG}.md`
- Modify: `.aiworkspace/note/finance/docs/{INDEX,ROADMAP,PROJECT_MAP}.md`
- Create local-only: `market-movers-hybrid-visual-system-v1-desktop-qa.png`

**Interfaces:**
- Consumes: source implementation from Tasks 1–3.
- Produces: canonical component build, actual QA evidence, durable docs state; no new runtime API.

- [x] **Step 1: Build the canonical production component**

From `app/web/streamlit_components/market_movers_workbench` run:

```bash
npm run build
```

Expected: Vite exits 0 and writes `component_static/index.html` plus hashed CSS/JS assets.

- [x] **Step 2: Run focused Market Movers regression**

```bash
.venv/bin/python -m pytest tests/test_overview_market_movers_decision_ui.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k 'market_mover or market_movers'
```

Expected: the decision UI file reports `11 passed`; the service subset reports `126 passed`. Unrelated Practical Validation/Final Review/Sentiment tests are not selected.

- [x] **Step 3: Verify compiled static entry and repository hygiene**

```bash
.venv/bin/python -m pytest tests/test_service_contracts.py::OverviewMarketIntelligenceServiceContractTests::test_market_movers_react_component_scaffold_keeps_streamlit_fallback -q
git diff --check
git status --short
```

Expected: scaffold test passes, diff check exits 0, and status contains only intended files plus pre-existing user artifacts.

- [ ] **Step 4: Run actual in-app Browser interaction QA**

Open `http://localhost:8530/`, choose `Overview > 변동 종목`, and verify:

1. outer surface matches Market Context/Futures Macro family;
2. four command controls remain usable;
3. ranking row updates selected research;
4. sector→industry and 일→월 switches work;
5. detail research and price→financial tabs work;
6. 분기→연간, 재무 영역, factor remain independent;
7. console error count is 0.

At actual desktop width, `693px`, `420px`, and `353px`, evaluate:

```js
({
  clientWidth: document.documentElement.clientWidth,
  scrollWidth: document.documentElement.scrollWidth,
  overflowFree: document.documentElement.scrollWidth === document.documentElement.clientWidth,
})
```

Expected: `overflowFree === true` at every width. Desktop retains approximately 62/38; below 900px the decision grid stacks.

- [x] **Step 5: Capture one local QA screenshot**

Save the final desktop screenshot to:

```text
/Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev/market-movers-hybrid-visual-system-v1-desktop-qa.png
```

Do not stage it.

- [x] **Step 6: Update closeout documents with exact evidence**

`STATUS.md` must contain:

```markdown
Status: Complete

- 이번 visual task: `3/3차 완료`
- 기존 Market Movers 기능 roadmap: `4/5차`
- conditional outlook/OOS publication gate는 별도 남은 5차다.
```

`RUNS.md`에는 actual pass counts, Vite transformed module count, QA widths/overflow values and console error count를 기록한다. Root logs에는 3–5줄 milestone만 추가한다. `docs/INDEX.md`, `ROADMAP.md`, `PROJECT_MAP.md`에는 hybrid integrated report surface라는 durable current-state만 반영한다.

- [x] **Step 7: Verify docs and stage only intended files**

```bash
task_dir='.aiworkspace/note/finance/tasks/active/market-movers-hybrid-visual-system-v1-20260720'
rg -n '3/3차|4/5차|conditional outlook|MarketMoversDecisionWorkbench' "$task_dir" .aiworkspace/note/finance/docs/INDEX.md .aiworkspace/note/finance/docs/ROADMAP.md .aiworkspace/note/finance/docs/PROJECT_MAP.md .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git diff --check
```

Expected: roadmap positions are present and diff check exits 0.

```bash
git add app/web/streamlit_components/market_movers_workbench/component_static .aiworkspace/note/finance/tasks/active/market-movers-hybrid-visual-system-v1-20260720 .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md .aiworkspace/note/finance/docs/INDEX.md .aiworkspace/note/finance/docs/ROADMAP.md .aiworkspace/note/finance/docs/PROJECT_MAP.md
```

- [x] **Step 8: Commit Task 4**

```bash
git commit -m "변동 종목 혼합형 UI를 검증하고 마감"
```

## Final Verification Checklist

- [x] three new source contracts pass
- [x] complete `tests/test_overview_market_movers_decision_ui.py` passes
- [x] Market Movers service subset passes
- [x] Vite production build exits 0 and canonical assets are tracked
- [ ] desktop/693px/420px/353px actual Browser QA has no horizontal overflow
- [ ] actual interactions and financial grouping remain functional
- [ ] Browser console error count is 0
- [x] screenshot and pre-existing user artifacts remain unstaged
- [x] visual task is `3/3차`, overall Market Movers remains `4/5차`
