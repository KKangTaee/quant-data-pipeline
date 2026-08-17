# Institutional Holdings Content-First UI V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix sequential manager selection and replace the Institutional Holdings dark studio rail with the approved Market Research + Today content-first shell without changing 13F data semantics.

**Architecture:** Streamlit remains the authority for selected CIK, local-only freshness decisions and explicit refresh commands. React replaces the persistent rail/drawer with a light page header, native disclosure-based manager picker, horizontal destination tabs and a content-first canvas; existing portfolio, quarter review, holdings, security and popularity bodies remain intact.

**Tech Stack:** Python 3, Streamlit session state, React 18, TypeScript 5, CSS, Vitest, Vite, pytest, local MySQL-backed 13F services.

## Global Constraints

- Page entry performs only the existing local due calculation; SEC/EDGAR access begins only after an explicit refresh click.
- Do not change SEC ingestion, amendment resolution, quarter-review math, performance-proxy definitions, provider boundaries or database schema.
- Preserve all five destinations: `포트폴리오 맥락 / 분기 리뷰 / 전체 보유 / 종목 상세 / 기관 보유 랭킹`.
- Explicit manager selection outranks a prior search query and clears that query before the next render.
- Remove the dark persistent rail, mobile drawer/scrim and full-height left active line.
- Active tabs use text contrast, subtle tint and a short bottom underline; selected manager is also identified by text/check, not color alone.
- The manager picker list owns its overflow; page/iframe horizontal overflow is forbidden except inside the horizontal tabs scroller.
- Keep manager selection loading local to the manager control and preserve the current portfolio body until the selected payload is acknowledged.
- Generated screenshots, `.superpowers/`, run history and unrelated registry changes must not be staged.

---

## File Structure

- Modify `app/web/institutional_portfolios.py`: clear active manager search when handling an explicit manager selection.
- Modify `tests/test_institutional_portfolios.py`: add state regression tests and replace old rail/drawer source contracts with content-first contracts.
- Modify `app/web/streamlit_components/institutional_portfolios_workbench/src/InstitutionalStudioShell.tsx`: own the light content-first shell and horizontal destination navigation.
- Modify `app/web/streamlit_components/institutional_portfolios_workbench/src/InstitutionalPortfoliosWorkbench.tsx`: own manager disclosure/search/results, pending selection, freshness control and next-check shortcut.
- Modify `app/web/streamlit_components/institutional_portfolios_workbench/src/workbenchState.ts`: remove obsolete manager drag helpers only.
- Modify `app/web/streamlit_components/institutional_portfolios_workbench/src/workbenchState.test.ts`: remove obsolete drag tests and retain canonical destination tests.
- Modify `app/web/streamlit_components/institutional_portfolios_workbench/src/style.css`: own header, controls, picker, tabs, canvas and responsive contracts.
- Regenerate `app/web/streamlit_components/institutional_portfolios_workbench/component_static/`: production Vite artifact.
- Modify `.aiworkspace/note/finance/docs/flows/INSTITUTIONAL_PORTFOLIOS_FLOW.md`: align the durable user flow after verified implementation.
- Modify this task's `STATUS.md`, `RUNS.md`, `RISKS.md` and active task pointers during closeout.

---

### Task 1: Make Explicit Manager Selection Win Over Search State

**Files:**
- Modify: `tests/test_institutional_portfolios.py:1760-1810`
- Modify: `app/web/institutional_portfolios.py:483-505`

**Interfaces:**
- Consumes: `_handle_workbench_event(event: dict[str, Any] | None) -> None` and Streamlit session keys `institutional_portfolios_manager_search`, `institutional_portfolios_selected_cik`.
- Produces: one atomic selection transition in which a valid `select_manager` event clears the search query, stores the requested CIK, resets dependent transient state and calls `st.rerun()` exactly once.

- [x] **Step 1: Write the failing state regression**

Add this test beside `test_manager_search_event_updates_existing_manager_query_state_on_submit`:

```python
def test_select_manager_event_clears_search_and_keeps_requested_cik(self) -> None:
    import app.web.institutional_portfolios as page

    class FakeStreamlit:
        def __init__(self) -> None:
            self.session_state: dict[str, object] = {
                "institutional_portfolios_manager_search": "Bill Ackman",
                "institutional_portfolios_selected_cik": "0001336528",
            }
            self.rerun_count = 0

        def rerun(self) -> None:
            self.rerun_count += 1

    original_streamlit = page.st
    original_loader = page.load_institutional_portfolio_model
    fake_streamlit = FakeStreamlit()
    try:
        page.st = fake_streamlit
        page.load_institutional_portfolio_model = lambda _cik: {"status": "ok", "model": {}}
        page._handle_workbench_event(
            {"id": "select_manager", "cik": "0001656456", "nonce": "select-david-tepper"}
        )
    finally:
        page.st = original_streamlit
        page.load_institutional_portfolio_model = original_loader

    self.assertEqual(fake_streamlit.session_state["institutional_portfolios_manager_search"], "")
    self.assertEqual(fake_streamlit.session_state["institutional_portfolios_selected_cik"], "0001656456")
    self.assertEqual(fake_streamlit.rerun_count, 1)
```

Add a second test with the same fake Streamlit but a loader returning
`{"status": "error", "message": "db unavailable"}`. Assert the selected CIK remains
`0001336528`, the search stays `Bill Ackman`,
`institutional_portfolios_manager_selection_error` contains the bounded user message, and rerun
count is one.

- [x] **Step 2: Run the regression and confirm the root cause**

```bash
.venv/bin/python -m pytest tests/test_institutional_portfolios.py -k "select_manager_event_clears_search" -q
```

Expected: FAIL because `institutional_portfolios_manager_search` remains `Bill Ackman`.

- [x] **Step 3: Implement the minimal event-state fix**

Replace the `select_manager` branch with this contract, preserving the existing dependent-state resets:

```python
if event_name == "select_manager":
    cik = str(payload.get("cik") or "")
    selected_cik = str(st.session_state.get("institutional_portfolios_selected_cik") or "")
    active_search = str(st.session_state.get("institutional_portfolios_manager_search") or "")
    if cik and (cik != selected_cik or active_search):
        portfolio_result = load_institutional_portfolio_model(cik)
        if portfolio_result.get("status") != "ok":
            st.session_state["institutional_portfolios_manager_selection_error"] = (
                "선택한 기관 포트폴리오를 불러오지 못했습니다. 현재 기관 화면을 유지합니다."
            )
            st.rerun()
            return
        st.session_state["institutional_portfolios_manager_search"] = ""
        st.session_state["institutional_portfolios_selected_cik"] = cik
        st.session_state["institutional_portfolios_manager_selection_error"] = ""
        st.session_state["institutional_interest_query"] = ""
        st.session_state["institutional_interest_query_needs_load"] = False
        st.session_state["institutional_interest_model_cache"] = {}
        st.session_state["institutional_popularity_needs_load"] = False
        st.session_state["institutional_price_refresh_result"] = {}
        st.rerun()
```

- [x] **Step 4: Run focused state and resolver tests**

```bash
.venv/bin/python -m pytest tests/test_institutional_portfolios.py -k "select_manager_event_clears_search or select_manager_load_failure or manager_search_event_updates or selected_manager_resolver" -q
```

Expected: all selected tests pass.

- [x] **Step 5: Commit the reliable selection transition**

```bash
git add app/web/institutional_portfolios.py tests/test_institutional_portfolios.py
git commit -m "수정: 기관 검색 후 대가 선택 전환 복구"
```

---

### Task 2: Replace the Studio Rail With the Content-First Shell

**Files:**
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/src/InstitutionalStudioShell.tsx:1-128`
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/src/InstitutionalPortfoliosWorkbench.tsx:969-1084,1269-1362,1394-1530,1750-1815`
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/src/workbenchState.ts:45-80`
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/src/workbenchState.test.ts:1-110`
- Test: `tests/test_institutional_portfolios.py:1430-1560`

**Interfaces:**
- Consumes: `STUDIO_DESTINATIONS`, `studioDestination(view)`, `StudioView`, workbench `payload`, `switchView(view)` and existing Streamlit events.
- Produces: `InstitutionalStudioShell` props `activeView`, `managerName`, `periodLabel`, `isPreview`, `onViewChange`, `managerControl`, `freshnessControl`, `children`; no drawer props or rail slot.

- [x] **Step 1: Replace the old shell source-contract test with a failing content-first contract**

Update the existing studio shell contract test so it asserts:

```python
self.assertIn('className="ip-institutional-page-header"', shell_source)
self.assertIn('className="ip-institutional-controls"', shell_source)
self.assertIn('className="ip-institutional-tabs"', shell_source)
self.assertIn('role="tablist"', shell_source)
self.assertIn('aria-selected={item.id === activeView}', shell_source)
self.assertIn("STUDIO_DESTINATIONS.map", shell_source)
self.assertNotIn('className="ip-studio-rail"', shell_source)
self.assertNotIn('className="ip-studio-mobile-bar"', shell_source)
self.assertNotIn("drawerOpen", shell_source)
self.assertNotIn("ip-studio-scrim", shell_source)
```

Also add source assertions for the workbench manager control:

```python
self.assertIn('className="ip-manager-picker"', component_source)
self.assertIn('className="ip-manager-picker__panel"', component_source)
self.assertIn('className="ip-manager-option__check"', component_source)
self.assertIn('className="ip-institutional-next-check"', component_source)
self.assertNotIn("handleManagerRailPointerDown", component_source)
self.assertNotIn("suppressManagerClickRef", component_source)
```

- [x] **Step 2: Run the source-contract test and verify failure**

```bash
.venv/bin/python -m pytest tests/test_institutional_portfolios.py -k "content_first_shell" -q
```

Expected: FAIL because the current shell still contains the dark rail, drawer and scrim.

- [x] **Step 3: Rewrite `InstitutionalStudioShell` around content slots**

Use this prop and DOM shape; keep destination labels sourced from `STUDIO_DESTINATIONS`:

```tsx
type Props = {
  activeView: StudioView;
  managerName: string;
  periodLabel: string;
  isPreview: boolean;
  onViewChange: (view: StudioView) => void;
  managerControl: React.ReactNode;
  freshnessControl: React.ReactNode;
  children: React.ReactNode;
};

export function InstitutionalStudioShell({
  activeView,
  managerName,
  periodLabel,
  isPreview,
  onViewChange,
  managerControl,
  freshnessControl,
  children,
}: Props) {
  const activeDestination = studioDestination(activeView);
  return (
    <div className="ip-institutional-shell">
      <header className="ip-institutional-page-header">
        <div>
          <span>RESEARCH / INSTITUTIONAL HOLDINGS</span>
          <h1>기관 보유 분석</h1>
          <p>지연 공시 기반 리서치 · 실시간 매수·매도 신호가 아닙니다.</p>
        </div>
        <div className="ip-institutional-page-header__state">
          <span className={isPreview ? "is-preview" : ""}>{isPreview ? "Preview" : periodLabel}</span>
          <strong>{managerName}</strong>
        </div>
      </header>
      <section className="ip-institutional-controls">
        {managerControl}
        {freshnessControl}
      </section>
      <nav className="ip-institutional-tabs" aria-label="기관 보유 리서치 목적지" role="tablist">
        {STUDIO_DESTINATIONS.map((item) => (
          <button
            key={item.id}
            type="button"
            role="tab"
            aria-selected={item.id === activeView}
            className={item.id === activeView ? "is-active" : ""}
            onClick={() => onViewChange(item.id)}
          >
            <strong>{item.label}</strong>
            <small>{item.description}</small>
          </button>
        ))}
      </nav>
      <section className="ip-institutional-canvas" aria-label={activeDestination.label}>
        {children}
      </section>
    </div>
  );
}
```

- [x] **Step 4: Convert the workbench manager rail into a native disclosure picker**

Make these state changes:

```tsx
const managerPickerRef = useRef<HTMLDetailsElement | null>(null);
// Remove studioDrawerOpen, managerRailRef, managerRailScrollRef,
// managerRailDragRef and suppressManagerClickRef.
```

In `handleManagerSelect`, close the disclosure and keep the existing transient resets:

```tsx
managerPickerRef.current?.removeAttribute("open");
setManagerSearch("");
setPendingAction({ kind: "manager", cik: item.cik, label: `${item.manager_name} 포트폴리오 불러오는 중` });
sendEvent({ id: "select_manager", cik: item.cik });
```

Pass a `managerControl` slot with this semantic structure:

```tsx
<details ref={managerPickerRef} className="ip-manager-picker">
  <summary>
    <span>선택 기관</span>
    <strong>{payload.hero.manager_name}</strong>
    <small>기관 변경</small>
  </summary>
  <div className="ip-manager-picker__panel">
    <form className="ip-manager-search" onSubmit={submitManagerSearch}>
      <label htmlFor="ip-manager-search-input">기관 / 투자 대가 검색</label>
      <div>
        <input
          id="ip-manager-search-input"
          type="search"
          value={managerSearch}
          placeholder="Berkshire, Pershing Square"
          onChange={(event) => setManagerSearch(event.target.value)}
        />
        <button type="submit" disabled={pendingAction?.kind === "manager_search"} aria-label="기관 검색">→</button>
      </div>
    </form>
    <div className="ip-manager-options" role="listbox" aria-label="기관 및 투자 대가 검색 결과">
      {payload.manager_picker.items.map((item) => (
        <button
          key={item.cik || item.manager_name}
          type="button"
          role="option"
          aria-selected={item.selected}
          className={`ip-manager-option ${item.selected ? "is-selected" : ""}`}
          disabled={pendingAction?.kind === "manager" && pendingAction.cik === item.cik}
          onClick={() => handleManagerSelect(item)}
        >
          <span><strong>{item.watchlist_label || item.manager_name}</strong><small>{item.manager_name} · {item.latest_report_period}</small></span>
          <span className="ip-manager-option__check" aria-hidden="true">{item.selected ? "✓" : ""}</span>
        </button>
      ))}
    </div>
    {payload.manager_picker.selection_error ? (
      <div className="ip-manager-picker__error" role="alert">{payload.manager_picker.selection_error}</div>
    ) : null}
  </div>
</details>
```

Extend the local `manager_picker` payload type with `selection_error?: string`. After
`build_institutional_workbench_payload(...)` returns, expose the bounded server state with:

```python
payload.setdefault("manager_picker", {})["selection_error"] = str(
    st.session_state.get("institutional_portfolios_manager_selection_error") or ""
)
```

Preserve the existing explicit empty/results status blocks inside the panel. Only the incoming
manager option is disabled; destination tabs and the current body remain interactive. Remove
`setStudioDrawerOpen(false)` from manager search and refresh handlers because the drawer state no
longer exists.

Keep manager pending feedback inside the manager control and exclude it from the global loading
banner:

```tsx
{pendingAction?.kind === "manager" ? (
  <span className="ip-manager-picker__pending" role="status">{pendingAction.label}</span>
) : null}

{pendingAction && pendingAction.kind !== "manager" ? (
  <div className="ip-loading-banner" role="status" aria-live="polite">
    <span className="ip-spinner" aria-hidden="true" />
    <strong>
      {pendingAction.kind === "manager_search"
        ? "기관 검색 중"
        : pendingAction.kind === "interest"
          ? "종목 상세 불러오는 중"
          : pendingAction.kind === "popularity"
            ? "기관 보유 랭킹 불러오는 중"
            : pendingAction.kind === "price"
              ? "가격 데이터 수집 중"
              : "13F 데이터 갱신 중"}
    </strong>
    <em>{pendingAction.label}</em>
  </div>
) : null}
```

- [x] **Step 5: Move freshness and explicit refresh into the second control slot**

```tsx
<section className={`ip-data-context ${payload.freshness?.is_stale ? "is-stale" : ""}`}>
  <div><span>데이터 기준</span><strong>{payload.freshness?.latest_report_period || "수집 필요"}</strong></div>
  <small>다음 확인 {payload.refresh_action?.next_due_date || "-"}</small>
  {payload.refresh_action?.visible ? (
    <button type="button" onClick={submitInstitutionalRefresh} disabled={pendingAction?.kind === "institutional_refresh"}>
      {payload.refresh_action.label}
    </button>
  ) : null}
</section>
```

Preserve current/partial/result copy without raw exception or job-row output. Do not add a network availability probe on page entry.

- [x] **Step 6: Add the overview-only next-check shortcut**

Immediately after the context hero, render:

```tsx
{activeView === "overview" ? (
  <button
    type="button"
    className="ip-institutional-next-check"
    onClick={() => switchView(payload.quarter_review?.available ? "quarter_review" : "holdings")}
  >
    <span>다음 확인</span>
    <strong>{payload.quarter_review?.available ? "분기 리뷰에서 보유 변화와 성과 보기" : "전체 보유 종목 살펴보기"}</strong>
    <span aria-hidden="true">→</span>
  </button>
) : null}
```

- [x] **Step 7: Remove obsolete drag helpers and tests**

Delete `managerDragScrollTop` and `managerDragExceededThreshold` from `workbenchState.ts`, remove their imports and the `manager rail drag scrolling` test block. Preserve destination and query tests unchanged.

- [x] **Step 8: Run React unit and type checks**

```bash
npm test
npm run typecheck
```

Run in `app/web/streamlit_components/institutional_portfolios_workbench`. Expected: all Vitest tests pass and TypeScript reports no errors.

- [x] **Step 9: Commit the semantic shell transition**

```bash
git add app/web/streamlit_components/institutional_portfolios_workbench/src \
  tests/test_institutional_portfolios.py
git commit -m "기능: 기관 보유 content-first shell 전환"
```

---

### Task 3: Align Visual Tokens, Responsive Behavior and Runtime Bundle

**Files:**
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/src/style.css:2080-3058`
- Modify: `tests/test_institutional_portfolios.py:1430-1560,1620-1640`
- Regenerate: `app/web/streamlit_components/institutional_portfolios_workbench/component_static/index.html`
- Regenerate: `app/web/streamlit_components/institutional_portfolios_workbench/component_static/assets/*`

**Interfaces:**
- Consumes: Task 2 selectors `.ip-institutional-shell`, `.ip-institutional-page-header`, `.ip-institutional-controls`, `.ip-manager-picker`, `.ip-manager-options`, `.ip-institutional-tabs`, `.ip-institutional-canvas`, `.ip-institutional-next-check`.
- Produces: light content-first desktop/tablet/mobile layout and tracked Vite bundle with the same selector contract.

- [x] **Step 1: Add failing CSS and runtime contract assertions**

Assert source CSS contains the new structural rules and excludes the old active line/drawer rules:

```python
self.assertIn(".ip-institutional-shell", style_source)
self.assertIn(".ip-institutional-page-header", style_source)
self.assertIn(".ip-institutional-controls", style_source)
self.assertIn(".ip-manager-options", style_source)
self.assertIn(".ip-institutional-tabs", style_source)
self.assertIn("overflow-x: auto;", _css_rule(style_source, ".ip-institutional-tabs"))
self.assertIn("min-height: 44px;", _css_rule(style_source, ".ip-institutional-tabs button"))
self.assertIn("::after", style_source)
self.assertNotIn(".ip-studio--drawer-open .ip-studio-rail", style_source)
self.assertNotIn("box-shadow: inset 3px 0 0 #75b9ee;", style_source)
```

After build, assert runtime CSS/JS contain `ip-institutional-page-header`, `ip-manager-picker`, `ip-institutional-tabs`, `다음 확인` and no `ip-studio-mobile-bar`.

- [x] **Step 2: Run the CSS contract and verify it fails**

```bash
.venv/bin/python -m pytest tests/test_institutional_portfolios.py -k "content_first or tracked_workbench_bundle" -q
```

Expected: FAIL until source CSS and production bundle are updated.

- [x] **Step 3: Implement the content-first visual contract**

Use these base rules, extending them only for existing child panels:

```css
.ip-institutional-shell {
  min-width: 0;
  padding: 22px;
  border: 1px solid #dce4ee;
  border-radius: 20px;
  background: #f4f7fa;
  box-shadow: 0 18px 48px rgba(15, 23, 42, 0.08);
}

.ip-institutional-page-header,
.ip-institutional-controls {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(280px, 0.75fr);
  gap: 14px;
}

.ip-manager-picker,
.ip-data-context {
  position: relative;
  min-width: 0;
  border: 1px solid #dfe7f0;
  border-radius: 14px;
  background: #ffffff;
}

.ip-manager-options {
  display: grid;
  gap: 5px;
  max-height: 320px;
  overflow-y: auto;
}

.ip-institutional-tabs {
  display: flex;
  gap: 6px;
  margin-top: 14px;
  overflow-x: auto;
  border-bottom: 1px solid #dce4ee;
}

.ip-institutional-tabs button {
  position: relative;
  flex: 0 0 auto;
  min-height: 44px;
  border: 0;
  color: #66788c;
  background: transparent;
}

.ip-institutional-tabs button.is-active {
  color: #173d5d;
  background: #edf4f9;
}

.ip-institutional-tabs button.is-active::after {
  position: absolute;
  right: 14px;
  bottom: 0;
  left: 14px;
  height: 3px;
  border-radius: 999px;
  background: #2f78ad;
  content: "";
}

.ip-institutional-next-check {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  width: 100%;
  min-height: 52px;
  margin: 14px 0;
  border: 1px solid #cdddea;
  border-radius: 12px;
  color: #25445f;
  background: #eaf2f8;
}
```

At `max-width: 980px`, change both header/control grids to one column. At `max-width: 720px`, reduce shell padding to `12px`, preserve `44px` controls, and keep only `.ip-institutional-tabs` horizontally scrollable. Remove rules owned only by `.ip-studio-rail`, `.ip-studio-mobile-bar`, `.ip-studio-scrim`, `.ip-studio--drawer-open` and the full-height manager active shadow.

- [x] **Step 4: Run React tests and typecheck before build**

```bash
npm test
npm run typecheck
```

Expected: PASS.

- [x] **Step 5: Build the tracked component bundle**

```bash
npm run build
```

Run all npm commands in `app/web/streamlit_components/institutional_portfolios_workbench`. Expected: Vite replaces `component_static` with one current CSS and one current JS asset referenced by `component_static/index.html`.

- [x] **Step 6: Run focused Python and runtime-contract tests**

```bash
.venv/bin/python -m pytest tests/test_institutional_portfolios.py -q
git diff --check
```

Expected: focused suite passes and `git diff --check` emits no output.

- [x] **Step 7: Commit styling and production bundle**

```bash
git add app/web/streamlit_components/institutional_portfolios_workbench/src/style.css \
  app/web/streamlit_components/institutional_portfolios_workbench/component_static \
  tests/test_institutional_portfolios.py
git commit -m "디자인: 기관 보유 Research UI 정렬"
```

---

### Task 4: Actual Browser QA and Durable Closeout

**Files:**
- Modify: `.aiworkspace/note/finance/docs/flows/INSTITUTIONAL_PORTFOLIOS_FLOW.md:45-65`
- Modify: `.aiworkspace/note/finance/tasks/active/institutional-holdings-content-first-ui-v1-20260817/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/institutional-holdings-content-first-ui-v1-20260817/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/institutional-holdings-content-first-ui-v1-20260817/RISKS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/README.md`
- Modify: `.aiworkspace/note/finance/tasks/active/STATUS_MANIFEST.md`
- Modify if state changes: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Generate but do not stage: `institutional-holdings-content-first-ui-v1-qa.png`

**Interfaces:**
- Consumes: built local Streamlit app, actual MySQL 13F data and completed Tasks 1-3.
- Produces: evidence that sequential manager selection, five destinations, refresh semantics and responsive layout work in the actual app.

- [x] **Step 1: Start the local app on a dedicated QA port**

```bash
uv run streamlit run app/web/streamlit_app.py --server.port 8511 --server.headless true
```

Expected: Streamlit reports `http://localhost:8511` and remains running for QA.

- [x] **Step 2: Verify desktop manager switching and state agreement**

In Browser QA:

1. Open `Research > Institutional Holdings`.
2. Search `Bill Ackman` and select `Bill Ackman`.
3. Open the manager picker and select `David Tepper`.
4. Select `Warren Buffett`.
5. After every choice confirm selected check, page-header manager, hero manager and portfolio body identify the same manager.
6. Confirm the search input is cleared after selection and no global button lock remains.

Expected: all three transitions complete on the first selection and no state reverts to Bill Ackman.

- [x] **Step 3: Verify destinations and explicit refresh boundary**

Click all five horizontal tabs and confirm the correct existing body appears. Return to overview and use `다음 확인`; it must route to `분기 리뷰` when available. Confirm no SEC request occurs merely by opening the page, and a refresh button appears only when the existing local due/partial contract says it is visible.

- [x] **Step 4: Verify desktop and narrow-mobile layouts**

At both widths confirm:

- header and controls stack without clipping;
- manager list scrolls inside its picker;
- destination tabs scroll horizontally;
- selected tab has a short bottom marker and no left vertical line;
- interactive controls are at least 44px high;
- page and component `scrollWidth <= clientWidth` outside the tabs scroller.

- [x] **Step 5: Capture one final QA screenshot**

Save the approved desktop overview after a successful manager transition as:

```text
/Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev/institutional-holdings-content-first-ui-v1-qa.png
```

Do not stage the screenshot.

- [x] **Step 6: Update durable flow and task records**

Document that manager selection clears search, the page uses a content-first header/control/tab/canvas order, active tabs use a short bottom marker and mobile uses stacked controls plus horizontally scrollable tabs instead of a drawer. Record exact automated commands and Browser QA outcomes in `RUNS.md`; set `RISKS.md` to no open blocker only if all evidence passed.

- [x] **Step 7: Run final verification**

```bash
.venv/bin/python -m pytest tests/test_institutional_portfolios.py -q
npm test
npm run typecheck
npm run build
git diff --check
git status --short
```

Run the npm commands in `app/web/streamlit_components/institutional_portfolios_workbench`.

Expected: all focused tests/typecheck/build pass; status shows only intended code/docs/static assets plus pre-existing unrelated user artifacts.

- [x] **Step 8: Commit closeout documentation**

```bash
git add .aiworkspace/note/finance/docs/flows/INSTITUTIONAL_PORTFOLIOS_FLOW.md \
  .aiworkspace/note/finance/tasks/active/README.md \
  .aiworkspace/note/finance/tasks/active/STATUS_MANIFEST.md \
  .aiworkspace/note/finance/tasks/active/institutional-holdings-content-first-ui-v1-20260817
git commit -m "완료: 기관 보유 content-first UI 개선"
```

If `ROADMAP.md` requires a state change, add it explicitly. Otherwise record `canonical roadmap change 없음` in `RUNS.md`.
