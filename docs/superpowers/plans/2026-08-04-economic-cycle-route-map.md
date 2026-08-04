# Economic Cycle Route Map Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the overlapping four-quadrant checkpoint chart with a four-phase cycle route that emphasizes the current observed phase and its structural adjacent direction without presenting a forecast.

**Architecture:** Keep the existing `cycle_map.points`, `observed_state`, and `transition_monitor` payloads. Add pure React view helpers for route transition state and compact history copy, then render a fixed four-node SVG route while leaving the transition panel, 12-month ribbon, and asset checkpoint surface unchanged.

**Tech Stack:** React 18, TypeScript, Vitest, Vite, SVG, CSS, Streamlit custom component, pytest source-contract tests.

## Global Constraints

- The phase order is exactly `recovery -> expansion -> slowdown -> contraction -> recovery`.
- The route arrow is structural direction evidence, never a probability forecast.
- `WATCH` uses a dashed current-to-adjacent arc; `CONFIRMED` uses a solid anchor-to-target arc; `MAINTAIN` has no arc.
- Remove 6M / 3M / 1M / current point labels and all level/momentum axes from the map.
- Keep the full `cycle_map.points` payload for history summary and the 12-month ribbon.
- Preserve `market_implications`, `MarketImplicationCard`, asset copy/order/CSS, and the `자산별 확인 포인트` surface.
- Do not add provider calls, service fields, persistence, jobs, or operational diagnostics.

---

### Task 1: Add route-state and history-summary helpers

**Files:**
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx:453-558`
- Test: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.test.tsx:5-190`

**Interfaces:**
- Consumes: `TransitionMonitor | null`, `Phase | null`, and `CyclePoint[]`.
- Produces: `resolveCycleRouteTransition(monitor, currentPhase): CycleRouteTransition | null` and `summarizeCycleRouteHistory(points): string`.

- [x] **Step 1: Write failing helper tests**

Add imports and assertions equivalent to:

```tsx
expect(resolveCycleRouteTransition(payload.transition_monitor, "contraction")).toEqual({
  from: "contraction",
  to: "recovery",
  status: "WATCH",
});

expect(summarizeCycleRouteHistory(payload.cycle_map.points)).toBe(
  "최근 6개월 · 위축 유지",
);

const changed = payload.cycle_map.points.map((point, index) => ({
  ...point,
  phase: index < 4 ? "recovery" as const : "contraction" as const,
}));
expect(summarizeCycleRouteHistory(changed)).toBe(
  "최근 6개월 · 회복에서 위축으로 변화",
);
```

Also test that `MAINTAIN` returns `null` and `CONFIRMED` returns the monitor anchor/target pair.

- [x] **Step 2: Run Vitest and verify RED**

Run: `npm test -- --run EconomicCycleWorkbench.test.tsx`

Working directory: `app/web/streamlit_components/economic_cycle_workbench`

Expected: imports fail because `resolveCycleRouteTransition` and `summarizeCycleRouteHistory` do not exist.

- [x] **Step 3: Implement minimal pure helpers**

Add the following exact public shape:

```tsx
export type CycleRouteTransition = {
  from: Phase;
  to: Phase;
  status: "WATCH" | "CONFIRMED";
};

export function resolveCycleRouteTransition(
  monitor: TransitionMonitor | null | undefined,
  currentPhase: Phase | null | undefined,
): CycleRouteTransition | null {
  if (!monitor || monitor.status === "MAINTAIN") return null;
  if (monitor.status === "CONFIRMED") {
    const from = monitor.anchor_phase;
    const to = monitor.target_phase;
    return from && to && from !== to ? { from, to, status: "CONFIRMED" } : null;
  }
  const to = resolveMapDirectionPhase(monitor, currentPhase);
  return currentPhase && to && currentPhase !== to
    ? { from: currentPhase, to, status: "WATCH" }
    : null;
}
```

Implement `summarizeCycleRouteHistory()` with `selectCycleMapCheckpoints()`:

```tsx
export function summarizeCycleRouteHistory(points: CyclePoint[]): string {
  const checkpoints = selectCycleMapCheckpoints(points);
  if (!checkpoints.length) return "과거 이력 부족";
  const prefix = points.length >= 7 ? "최근 6개월" : "조회 가능한 기간";
  const first = checkpoints[0].phase;
  const current = checkpoints[checkpoints.length - 1].phase;
  if (checkpoints.every((point) => point.phase === current)) {
    return `${prefix} · ${PHASE_LABEL[current]} 유지`;
  }
  if (first === current) return `${prefix} · ${PHASE_LABEL[current]} 국면 내 변동`;
  return `${prefix} · ${PHASE_LABEL[first]}에서 ${PHASE_LABEL[current]}으로 변화`;
}
```

- [x] **Step 4: Run focused Vitest and verify GREEN**

Run: `npm test -- --run EconomicCycleWorkbench.test.tsx`

Expected: all helper and existing component tests pass.

- [x] **Step 5: Commit the helper unit**

Stage only the React source and test, then commit:

```text
기능: 경제사이클 순환 경로 상태 모델 추가
```

### Task 2: Replace the quadrant with the cycle route map

**Files:**
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx:307,453-558,652-742`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/style.css:144-185,498`
- Test: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.test.tsx:132-190`
- Test: `tests/test_market_context_economic_cycle.py:317-340,552-565`
- Regenerate: `app/web/streamlit_components/economic_cycle_workbench/component_static/`

**Interfaces:**
- Consumes: Task 1 helpers, `payload.observed_state`, `payload.transition_monitor`, and `payload.cycle_map.points`.
- Produces: `CycleRouteMap({ payload })` with four fixed phase nodes, one current node, optional route arc, and one history-summary line.

- [x] **Step 1: Replace old render assertions with failing route assertions**

Assert the rendered markup contains:

```tsx
expect(html).toContain("순환 경로로 본 현재 위치");
expect(html.match(/class="cycle-route-node/g)).toHaveLength(4);
expect(html).toContain("현재 관측 위축");
expect(html).toContain("위축 → 회복 방향 관찰 · 예측 아님");
expect(html).toContain("최근 6개월 · 위축 유지");
expect(html).not.toContain('class="cycle-quadrant"');
expect(html).not.toContain("6개월 전");
expect(html).not.toContain("성장 레벨 →");
```

Render a `MAINTAIN` fixture and assert that it has no `cycle-route-direction` path.
Retain the existing five asset block order assertions.

- [x] **Step 2: Update the Python source-contract test and verify RED**

Replace quadrant-specific assertions with route contracts:

```python
assert 'className="cycle-route-map"' in source
assert "summarizeCycleRouteHistory(payload.cycle_map.points)" in source
assert "cycle-route-direction" in source
assert 'className="cycle-quadrant"' not in source
assert "actualCoordinate" not in source
```

Run:

```text
.venv/bin/python -m pytest tests/test_market_context_economic_cycle.py -q
```

Expected: source-contract failures because the quadrant still exists.

- [x] **Step 3: Implement `CycleRouteMap` and remove dead quadrant helpers**

Use fixed nodes:

```tsx
const CYCLE_ROUTE_NODES: Record<Phase, { x: number; y: number; labelX: number; labelY: number }> = {
  recovery: { x: 70, y: 70, labelX: 70, labelY: 34 },
  expansion: { x: 250, y: 70, labelX: 250, labelY: 34 },
  slowdown: { x: 250, y: 250, labelX: 250, labelY: 286 },
  contraction: { x: 70, y: 250, labelX: 70, labelY: 286 },
};

const CYCLE_ROUTE_ARCS: Record<string, string> = {
  "recovery:expansion": "M70 70 C118 25 202 25 250 70",
  "expansion:slowdown": "M250 70 C295 118 295 202 250 250",
  "slowdown:contraction": "M250 250 C202 295 118 295 70 250",
  "contraction:recovery": "M70 250 C25 202 25 118 70 70",
};
```

Render one neutral circular/rounded route track, four phase nodes in the fixed order, the current node label, central current phase/duration, optional route arc with arrowhead, status copy, and the history summary. `WATCH` uses the dashed class and `CONFIRMED` the solid class.

Remove now-unused `PlotPoint`, `actualCoordinate`, `projectActualCoordinate`, `PHASE_COORDINATE_CENTER`, `monthDistance`, `pressureArrowEnd`, `pointList`, `cyclePointLabel`, `CyclePointTooltip`, and `splitPointSegments` plus their tests and CSS.

- [x] **Step 4: Implement responsive route CSS**

Add scoped classes for:

```text
.cycle-route-map
.cycle-route-track
.cycle-route-direction
.route-watch
.route-confirmed
.cycle-route-node
.cycle-route-node-current
.cycle-route-node-next
.cycle-route-center
.cycle-route-history
.cycle-route-status
```

Use the existing phase colors and ensure the SVG width is `min(100%, 440px)`. On narrow screens keep the SVG within 340px and let the existing `.cycle-layout` stack the route and transition panels.

- [x] **Step 5: Run React and Python tests, then build**

Run from the component directory:

```text
npm test -- --run
npm run build
```

Run from the repository root:

```text
.venv/bin/python -m pytest tests/test_market_context_economic_cycle.py -q
```

Expected: React tests, Python source contracts, TypeScript transform, and Vite production build all pass.

- [x] **Step 6: Review frozen asset boundary**

Run a scoped diff search and confirm no diff hunk changes `MarketImplicationCard`, `MarketImplicationBody`, `market_implications`, asset ordering, or asset CSS. Do not stage registries, run history, generated QA images, or `.superpowers/`.

- [x] **Step 7: Commit the route-map implementation**

Stage the React source/test/CSS, Python contract test, and rebuilt component assets, then commit:

```text
개선: 경제사이클 순환 경로 지도 적용
```

### Task 3: Integrated verification and closeout

**Files:**
- Create: `.aiworkspace/note/finance/tasks/active/economic-cycle-route-map-20260804/PLAN.md`
- Create: `.aiworkspace/note/finance/tasks/active/economic-cycle-route-map-20260804/DESIGN.md`
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-route-map-20260804/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-route-map-20260804/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-route-map-20260804/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-route-map-20260804/RISKS.md`

**Interfaces:**
- Consumes: the committed route-map component and production bundle.
- Produces: reproducible verification evidence, one generated Browser QA screenshot, and a complete task status.

- [x] **Step 1: Run the full focused verification suite**

Run:

```text
.venv/bin/python -m pytest tests/test_economic_cycle_observed_state_v1.py tests/test_economic_cycle_freshness.py tests/test_economic_cycle_service.py tests/test_economic_cycle_refresh.py tests/test_market_context_economic_cycle.py -q
```

Run from the component directory:

```text
npm test -- --run
npm run build
```

Expected: all focused Python and React tests pass and the production bundle is current.

- [x] **Step 2: Run static checks**

Run separately:

```text
.venv/bin/python -m py_compile app/services/overview/economic_cycle.py app/services/overview/economic_cycle_freshness.py finance/economic_cycle_observed_state.py
git diff --check
```

Expected: both commands exit 0.

- [x] **Step 3: Perform Browser QA**

Restart the local Streamlit server only after the final build. Verify the live route at:

```text
http://localhost:8503/overview?view=economic-cycle&overview_tab=economic-cycle
```

Check the four nodes, current contraction, dashed contraction-to-recovery arc, non-forecast copy, compact history summary, unchanged transition panel, unchanged 12-month ribbon, and unchanged asset checkpoint section. Capture one screenshot outside the staged source set.

- [x] **Step 4: Close task documentation**

Record exact commands/results, remaining semantic trade-off, Browser QA screenshot path, code-review outcome, and `canonical doc change 없음` unless product or ownership boundaries changed. Set `STATUS.md` to `State: complete` only after all checks pass.

- [x] **Step 5: Commit closeout docs**

Stage only the task directory and plan checkbox updates, then commit:

```text
문서: 경제사이클 순환 경로 지도 검증 정리
```
