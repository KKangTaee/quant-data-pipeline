# Today Live Island Rerun Isolation V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Today의 15초 전체 화면 fragment와 1초 top-level React 갱신을 제거하고, 미국 정규장 OPEN 또는 종가 전환 대기 중에만 대표 포트폴리오 영역을 독립적으로 갱신한다.

**Architecture:** 최초 app run은 전체 `today_home_v4`를 한 번 구성해 context/actions shell을 렌더링한다. 포트폴리오는 최소 `today_portfolio_island_v1` payload와 별도 stable key를 사용하며 conditional fragment가 portfolio DB/coordinator 경계만 읽는다. 시계는 `MarketSessionClock` child의 local state가 소유하고 phase 변화 때만 Python에 event를 한 번 보낸다.

**Tech Stack:** Python 3.12, Streamlit fragment/custom component, React 18, TypeScript, Vite/Vitest, unittest, existing MySQL-backed services.

## Global Constraints

- provider cadence 300초와 quote freshness 600초를 유지한다.
- 프리마켓·애프터마켓, 별도 API, SSE, WebSocket, browser provider fetch를 추가하지 않는다.
- OPEN 또는 EOD `waiting/running` 상태만 15초 portfolio heartbeat를 가진다.
- PRE_OPEN, HOLIDAY, WEEKEND, STALE, CLOSED+confirmed/exhausted에는 periodic fragment가 없어야 한다.
- 1초 clock state는 session child만 갱신하며 portfolio/chart를 구독시키지 않는다.
- heartbeat는 broad Today market loader를 다시 호출하지 않는다.
- spinner, skeleton, loading overlay를 추가하지 않는다.
- historical EOD curve와 DB 의미는 변경하지 않는다.
- 기존 dirty registry/run-history/generated artifacts는 stage하지 않는다.

## File Responsibility Map

- `app/services/today.py`: portfolio-only public projection.
- `app/web/today_page.py`: static shell, island state, conditional fragment, phase event.
- `app/web/today_react_component.py`: allowlisted view API.
- `app/web/streamlit_components/today_workbench/src/MarketSessionClock.tsx`: 유일한 1초 timer.
- `app/web/streamlit_components/today_workbench/src/TodayPortfolioPanel.tsx`: portfolio/chart subtree.
- `app/web/streamlit_components/today_workbench/src/TodayWorkbench.tsx`: context/portfolio/actions/full routing.
- `tests/test_today_home.py`와 React tests: runtime/view isolation regression.

---

## 1/2차 — 전체 Rerun 제거와 렌더 격리

### Task 1: Portfolio Projection, Heartbeat Policy, React View Split

**Files:**
- Modify: `app/services/today.py`
- Modify: `app/web/today_page.py`
- Create: `app/web/streamlit_components/today_workbench/src/MarketSessionClock.tsx`
- Create: `app/web/streamlit_components/today_workbench/src/TodayPortfolioPanel.tsx`
- Create: `app/web/streamlit_components/today_workbench/src/view.test.tsx`
- Modify: `app/web/streamlit_components/today_workbench/src/TodayWorkbench.tsx`
- Modify: `app/web/streamlit_components/today_workbench/src/types.ts`
- Modify: `app/web/streamlit_components/today_workbench/src/style.css`
- Modify: `tests/test_today_home.py`

**Interfaces:**
- `project_today_portfolio(workspace, *, portfolio_live=None) -> dict[str, Any]`.
- `should_run_today_portfolio_heartbeat(session, coordinator_state) -> bool`.
- `TodayWorkbenchView = "full" | "context" | "portfolio" | "actions"`.
- `TodayPortfolioIslandPayload = {schema_version: "today_portfolio_island_v1"; portfolio: TodayPortfolio}`.

- [x] **Step 1: Write failing Python projector and policy tests**

```python
def test_public_portfolio_projector_matches_full_today_portfolio(self):
    from app.services.today import build_today_read_model, project_today_portfolio
    inputs = self._complete_inputs()
    self.assertEqual(
        project_today_portfolio(inputs["portfolio"]),
        build_today_read_model(**inputs)["portfolio"],
    )

def test_heartbeat_runs_only_for_open_or_active_eod_handoff(self):
    from app.web.today_page import should_run_today_portfolio_heartbeat
    from app.web.today_intraday_auto_refresh import CoordinatorSnapshot
    state = lambda value: CoordinatorSnapshot("idle", None, value, 0, ())
    self.assertTrue(should_run_today_portfolio_heartbeat(
        self._regular_session("OPEN", allowed=True), state("not_applicable")
    ))
    self.assertTrue(should_run_today_portfolio_heartbeat(
        self._regular_session("CLOSED", allowed=False), state("waiting")
    ))
    for phase, eod in [("PRE_OPEN", "not_applicable"), ("HOLIDAY", "not_applicable"),
                       ("WEEKEND", "not_applicable"), ("STALE", "not_applicable"),
                       ("CLOSED", "confirmed"), ("CLOSED", "exhausted")]:
        self.assertFalse(should_run_today_portfolio_heartbeat(
            self._regular_session(phase, allowed=False), state(eod)
        ))
```

- [x] **Step 2: Run Python tests and confirm RED**

```bash
.venv/bin/python -m unittest \
  tests.test_today_home.TodayHomeReadModelTests.test_public_portfolio_projector_matches_full_today_portfolio \
  tests.test_today_home.TodayHomePageContractTests.test_heartbeat_runs_only_for_open_or_active_eod_handoff -v
```

Expected: both public function imports fail.

- [x] **Step 3: Implement minimal projector and policy**

```python
def project_today_portfolio(workspace: Any, *, portfolio_live: Any | None = None) -> dict[str, Any]:
    """Project only the portfolio branch for lightweight Today refreshes."""
    portfolio = _project_portfolio(workspace)
    portfolio["live"] = _project_live_portfolio(portfolio_live)
    return portfolio

def should_run_today_portfolio_heartbeat(session, coordinator_state) -> bool:
    if session.phase == "OPEN" and session.collection_allowed:
        return True
    return session.phase == "CLOSED" and coordinator_state.eod_state in {"waiting", "running"}
```

Make `build_today_read_model` call the public projector so full/island schemas cannot drift.

- [x] **Step 4: Write failing React split-view and timer-isolation tests**

```tsx
it("keeps portfolio markup out of context", () => {
  const markup = renderToStaticMarkup(
    <TodayContextView payload={completeTodayPayload} onPhaseChange={() => undefined} />,
  );
  expect(markup).toContain("오늘의 시장 판단");
  expect(markup).not.toContain("REPRESENTATIVE PORTFOLIO");
});

it("keeps market and actions out of portfolio", () => {
  const markup = renderToStaticMarkup(
    <TodayPortfolioPanel portfolio={completeTodayPayload.portfolio} viewportWidth={960} />,
  );
  expect(markup).toContain("REPRESENTATIVE PORTFOLIO");
  expect(markup).not.toContain("오늘의 시장 판단");
  expect(markup).not.toContain("NEXT ACTION");
});
```

```python
def test_clock_timer_is_isolated_from_portfolio_and_workbench(self):
    root = Path("app/web/streamlit_components/today_workbench/src")
    self.assertNotIn("setInterval", (root / "TodayWorkbench.tsx").read_text())
    self.assertNotIn("setInterval", (root / "TodayPortfolioPanel.tsx").read_text())
    self.assertIn("setInterval", (root / "MarketSessionClock.tsx").read_text())
```

- [x] **Step 5: Run React/source tests and confirm RED**

```bash
cd app/web/streamlit_components/today_workbench
npm test -- src/view.test.tsx
cd ../../../../..
.venv/bin/python -m unittest \
  tests.test_today_home.TodayHomePageContractTests.test_clock_timer_is_isolated_from_portfolio_and_workbench -v
```

Expected: new components are missing and the timer remains in `TodayWorkbench`.

- [x] **Step 6: Extract the exact existing JSX**

Create `MarketSessionClock` with the only timer and phase ref:

```tsx
const [nowMs, setNowMs] = useState(() => Date.now());
const phaseRef = useRef<MarketSessionPhase | null>(null);
const resolved = resolveMarketSession(marketSession, nowMs);
useEffect(() => {
  const timer = window.setInterval(() => setNowMs(Date.now()), 1000);
  return () => window.clearInterval(timer);
}, []);
```

Move the existing four market-session cells unchanged into that component. Move the entire existing `today-portfolio-panel` section into `TodayPortfolioPanel`, which receives only `portfolio` and `viewportWidth`. Export `TodayContextView` and `TodayActionsView`; route four explicit views and retain `full` as compatibility composition.

- [x] **Step 7: Preserve split iframe spacing**

```css
.today-workbench.view-context { padding-bottom: 0; }
.today-workbench.view-portfolio { padding-block: 0; }
.today-workbench.view-actions { padding-top: 0; }
```

- [x] **Step 8: Run regressions, build, and commit Task 1**

```bash
.venv/bin/python -m unittest tests.test_today_home.TodayHomeReadModelTests \
  tests.test_today_home.TodayHomePageContractTests.test_heartbeat_runs_only_for_open_or_active_eod_handoff \
  tests.test_today_home.TodayHomePageContractTests.test_clock_timer_is_isolated_from_portfolio_and_workbench -v
cd app/web/streamlit_components/today_workbench
npm test
npm run typecheck
npm run build
cd ../../../../..
git add app/services/today.py app/web/today_page.py \
  app/web/streamlit_components/today_workbench tests/test_today_home.py
git commit -m "기능: Today 정적 화면과 포트폴리오 렌더 분리"
```

---

## 2/2차 — Portfolio Live Island와 Conditional Heartbeat

### Task 2: Minimal Island State, Conditional Fragment, Phase Event

**Files:**
- Modify: `app/web/today_react_component.py`
- Modify: `app/web/today_page.py`
- Modify: `app/web/streamlit_components/today_workbench/src/types.ts`
- Modify: `app/web/streamlit_components/today_workbench/src/MarketSessionClock.tsx`
- Modify: `app/web/streamlit_components/today_workbench/src/TodayWorkbench.tsx`
- Modify: `app/web/streamlit_components/today_workbench/src/presentation.ts`
- Modify: `app/web/streamlit_components/today_workbench/src/presentation.test.ts`
- Modify: `tests/test_today_home.py`

**Interfaces:**
- `render_today_workbench(payload, *, view="full", key="today_workbench")`.
- `TodayPortfolioIslandState(payload, session, coordinator_state, heartbeat_enabled)`.
- `load_today_portfolio_island_state(*, market_session, generated_at=None, context=None, coordinator=None)`.
- `marketPhaseTransition(previous, current) -> event | null`.

- [ ] **Step 1: Write failing wrapper, loader, and fragment-scope tests**

```python
def test_component_passes_explicit_view_and_key(self):
    component = MagicMock(return_value={"event": None})
    with patch.object(react_component, "_declare_today_component", return_value=component):
        react_component.render_today_workbench(
            {"schema_version": "today_portfolio_island_v1", "portfolio": {}},
            view="portfolio", key="today_portfolio_island",
        )
    self.assertEqual(component.call_args.kwargs["view"], "portfolio")

def test_island_loader_never_loads_broad_market_model(self):
    with patch.object(page, "load_today_read_model", side_effect=AssertionError("broad reload")):
        state = page.load_today_portfolio_island_state(
            market_session=self._confirmed_open_schedule(),
            generated_at=datetime(2026, 7, 22, 14, 0, tzinfo=timezone.utc),
            context=self._runtime_context(), coordinator=self._idle_coordinator(),
        )
    self.assertEqual(state.payload["schema_version"], "today_portfolio_island_v1")

def test_periodic_fragment_is_scoped_to_portfolio_only(self):
    source = Path("app/web/today_page.py").read_text()
    self.assertNotIn("def _render_today_dynamic_fragment", source)
    self.assertIn("def _render_today_portfolio_fragment", source)
    self.assertIn('key="today_context_shell"', source)
    self.assertIn('key="today_portfolio_island"', source)
    self.assertIn('key="today_action_shell"', source)
```

- [ ] **Step 2: Write failing one-shot phase transition tests**

```ts
it("emits only when phase changes", () => {
  expect(marketPhaseTransition(null, "PRE_OPEN")).toBeNull();
  expect(marketPhaseTransition("PRE_OPEN", "PRE_OPEN")).toBeNull();
  expect(marketPhaseTransition("PRE_OPEN", "OPEN")).toEqual({
    id: "market_phase_changed", phase: "OPEN",
  });
});
```

```python
def test_phase_event_is_allowlisted_without_navigation(self):
    event = page._normalize_today_event({"event": {"id": "market_phase_changed", "phase": "OPEN"}})
    self.assertEqual(event, {"id": "market_phase_changed", "phase": "OPEN"})
    with patch.object(page.st, "switch_page") as switch_page:
        page._handle_today_component_value({"event": event}, {})
    switch_page.assert_not_called()
```

- [ ] **Step 3: Run all new tests and confirm RED**

```bash
.venv/bin/python -m unittest \
  tests.test_today_home.TodayHomePageContractTests.test_component_passes_explicit_view_and_key \
  tests.test_today_home.TodayHomePageContractTests.test_island_loader_never_loads_broad_market_model \
  tests.test_today_home.TodayHomePageContractTests.test_periodic_fragment_is_scoped_to_portfolio_only \
  tests.test_today_home.TodayHomePageContractTests.test_phase_event_is_allowlisted_without_navigation -v
cd app/web/streamlit_components/today_workbench
npm test -- src/presentation.test.ts
```

- [ ] **Step 4: Implement wrapper and island state**

```python
_TODAY_COMPONENT_VIEWS = {"full", "context", "portfolio", "actions"}

@dataclass(frozen=True)
class TodayPortfolioIslandState:
    payload: dict[str, Any]
    session: RegularSessionState
    coordinator_state: CoordinatorSnapshot
    heartbeat_enabled: bool
```

The wrapper rejects unknown views and passes `view` to the component. The island loader moves the existing scope/session/coordinator/latest quote/EOD waiting block out of `_render_today_dynamic_body`; it starts with `project_today_portfolio(context.workspace)` and never calls `load_today_read_model`.

- [ ] **Step 5: Replace whole-page fragment with conditional island**

```python
def _render_today_portfolio_fragment(*, market_session, initial_state):
    run_every = 15 if initial_state.heartbeat_enabled else None
    @st.fragment(run_every=run_every)
    def portfolio_fragment():
        state = load_today_portfolio_island_state(market_session=market_session)
        value = render_today_workbench(
            state.payload, view="portfolio", key="today_portfolio_island"
        )
        _handle_today_component_value(value, {})
        if initial_state.heartbeat_enabled and not state.heartbeat_enabled:
            st.rerun(scope="app")
    portfolio_fragment()
```

`render_today_page` loads the broad model once, renders context, invokes the island, and renders actions. CLOSED confirmed uses `run_every=None`. React fallback remains a one-piece render.

- [ ] **Step 6: Implement phase transition helper and allowlist**

```ts
export function marketPhaseTransition(previous, current) {
  if (previous == null || previous === current) return null;
  return { id: "market_phase_changed" as const, phase: current };
}
```

`MarketSessionClock` uses its phase ref and sends `Streamlit.setComponentValue` only for the returned transition. Python accepts only known phases and performs no navigation; the component event supplies the one app run needed to activate/deactivate the conditional fragment.

- [ ] **Step 7: Run full regressions, rebuild, and commit Task 2**

```bash
.venv/bin/python -m unittest tests.test_today_home \
  tests.test_portfolio_monitoring_intraday_refresh \
  tests.test_portfolio_monitoring_price_refresh tests.test_nyse_calendar -v
cd app/web/streamlit_components/today_workbench
npm test
npm run typecheck
npm run build
cd ../../../../..
git add app/web/today_page.py app/web/today_react_component.py \
  app/web/streamlit_components/today_workbench tests/test_today_home.py
git commit -m "수정: Today 자동 갱신을 포트폴리오 영역으로 제한"
```

### Task 3: Browser QA, Docs, Closeout

**Files:**
- Modify: `.aiworkspace/note/finance/docs/flows/TODAY_PORTFOLIO_INTRADAY_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: active task docs and root handoff logs
- Create generated: `today-live-island-rerun-isolation-v1-qa.png` (uncommitted)

- [ ] **Step 1: Run final verification**

```bash
.venv/bin/python -m unittest tests.test_today_home \
  tests.test_portfolio_monitoring_intraday_refresh \
  tests.test_portfolio_monitoring_price_refresh \
  tests.test_portfolio_monitoring_valuation \
  tests.test_portfolio_monitoring_position_events tests.test_nyse_calendar -v
cd app/web/streamlit_components/today_workbench
npm test
npm run typecheck
npm run build
cd ../../../../..
.venv/bin/python -m py_compile app/services/today.py app/web/today_page.py app/web/today_react_component.py
git diff --check
```

- [ ] **Step 2: Run actual CLOSED Browser QA**

Observe canonical `main-dev` for at least 20 seconds. Countdown must change, periodic Streamlit run count must be zero, context/portfolio/actions order and chart path must remain stable, console errors must be zero, and horizontal overflow must be zero at 1280/760/420px.

- [ ] **Step 3: Run controlled OPEN/island QA**

Verify OPEN creates the 15-second portfolio fragment, a DB-backed quote changes only portfolio metrics/live point, static shell identity and scroll state remain stable, and confirmed EOD produces one activation run then no periodic fragment. Separate deterministic evidence from unavailable real-clock OPEN evidence.

- [ ] **Step 4: Synchronize docs and commit**

Canonical flow to record:

```text
initial app run -> static Today context/actions
local 1s MarketSessionClock -> no Python run
OPEN/EOD-active 15s portfolio fragment -> portfolio DB/coordinator only
provider collection -> 300s unchanged
phase transition -> one app activation run
CLOSED confirmed -> no periodic fragment
```

Set status to `2/2 Implemented`, update concise root logs, review only intended files, and commit with `문서: Today 부분 갱신 작업 마감`. Never stage registry JSONL, run history, `.superpowers`, or QA images.

- [ ] **Step 5: Apply verification-before-completion**

Re-run the final Python suite, React tests/typecheck/build, `py_compile`, `git diff --check`, and status inspection after the last edit. Report roadmap `2/2`, actual CLOSED evidence, actual/fixture OPEN evidence separately, and unrelated dirty files separately.

## Plan Self-Review Result

- Spec coverage: static shell, clock isolation, minimal island payload, conditional heartbeat, phase transition, EOD shutdown, regression, Browser QA, and docs map to Tasks 1–3.
- Placeholder scan: no `TBD`, `TODO`, unnamed error handling, or deferred implementation step remains.
- Type consistency: `TodayPortfolioIslandPayload`, `TodayWorkbenchView`, `TodayPortfolioIslandState`, `CoordinatorSnapshot`, and `RegularSessionState` are introduced before use.
- Scope check: DB schema, cadence, provider, pre/after-market, API, SSE, WebSocket, and unrelated redesign remain excluded.
