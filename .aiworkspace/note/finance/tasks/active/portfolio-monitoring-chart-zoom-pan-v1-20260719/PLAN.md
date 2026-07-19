# Portfolio Monitoring Chart Zoom / Pan V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 선택한 direct 미국 주식·ETF 가격 차트에서 커서 기준 wheel zoom, 수평 drag pan, 명시적 zoom/reset controls를 제공한다.

**Architecture:** 기존 `selected_item_market_chart` 최대 120개 row를 그대로 받아 React가 inclusive `{startIndex, endIndex}` viewport만 관리한다. Pure helper가 zoom anchor와 pan clamp를 계산하고, `MarketPriceChart`는 visible rows만 SVG로 다시 그린다. Python, DB, loader와 Operations summary read 계약은 변경하지 않는다.

**Tech Stack:** React 18, TypeScript 5.7, SVG, Vitest 4, Vite 6, Python unittest static component contract, Streamlit custom component

## Global Constraints

- zoom/pan 적용 범위는 선택 direct stock/ETF의 `MarketPriceChart`뿐이다.
- 종합 가치곡선과 selected strategy 가치곡선은 현재 동작을 유지한다.
- 기존 최대 120개 DB-only OHLCV projection을 재사용하며 zoom/pan은 Python rerun이나 추가 DB/provider read를 만들지 않는다.
- line/candle은 같은 viewport를 공유하고 최소 표시 범위는 15거래일이다.
- desktop은 cursor-anchored wheel zoom과 horizontal pointer drag를 제공한다.
- 420px mobile은 touch drag/pinch 없이 `− / + / 전체 보기` controls만 제공하고 `touch-action: pan-y`를 유지한다.
- 선택 item, row count, first date 또는 last date가 바뀌면 full viewport로 reset한다.
- drag threshold는 수평 4px이며 drag 중 tooltip을 숨긴다.
- wheel zoom-in은 `round(visibleCount * 0.8)`, zoom-out은 `round(visibleCount * 1.25)`다.
- drag right는 이전 날짜가 보이도록 viewport index를 감소시킨다.
- registry, saved JSONL, run history와 generated QA artifact는 commit하지 않는다.

---

### Task 1: Market Chart Viewport Pure Helpers

**Files:**
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.ts:289-325`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.test.ts:1-25,140-175`

**Interfaces:**
- Consumes: `rowCount: number`, inclusive `MarketChartViewport`, pointer anchor ratio, drag pixel delta와 plot width
- Produces: `MIN_MARKET_CHART_VISIBLE_ROWS`, `MarketChartViewport`, `buildFullMarketChartViewport`, `normalizeMarketChartViewport`, `zoomMarketChartViewport`, `panMarketChartViewport`

- [ ] **Step 1: Add failing viewport tests and imports**

Add these imports to `workbenchState.test.ts`:

```ts
  buildFullMarketChartViewport,
  normalizeMarketChartViewport,
  panMarketChartViewport,
  zoomMarketChartViewport,
```

Append these tests inside `describe("selected item market chart", ...)`:

```ts
  it("builds and normalizes an inclusive market chart viewport", () => {
    expect(buildFullMarketChartViewport(120)).toEqual({ startIndex: 0, endIndex: 119 });
    expect(normalizeMarketChartViewport({ startIndex: -20, endIndex: 200 }, 120)).toEqual({
      startIndex: 0,
      endIndex: 119,
    });
    expect(buildFullMarketChartViewport(0)).toEqual({ startIndex: 0, endIndex: 0 });
  });

  it("zooms around left center and right pointer anchors", () => {
    const full = buildFullMarketChartViewport(120);
    expect(zoomMarketChartViewport(full, 120, 0, "in")).toEqual({ startIndex: 0, endIndex: 95 });
    expect(zoomMarketChartViewport(full, 120, 0.5, "in")).toEqual({ startIndex: 12, endIndex: 107 });
    expect(zoomMarketChartViewport(full, 120, 1, "in")).toEqual({ startIndex: 24, endIndex: 119 });
  });

  it("clamps repeated zoom to 15 rows and back to the full range", () => {
    let viewport = buildFullMarketChartViewport(120);
    for (let index = 0; index < 20; index += 1) {
      viewport = zoomMarketChartViewport(viewport, 120, 0.5, "in");
    }
    expect(viewport.endIndex - viewport.startIndex + 1).toBe(15);
    for (let index = 0; index < 20; index += 1) {
      viewport = zoomMarketChartViewport(viewport, 120, 0.5, "out");
    }
    expect(viewport).toEqual({ startIndex: 0, endIndex: 119 });
  });

  it("pans by visible-row distance and clamps both data edges", () => {
    const viewport = { startIndex: 40, endIndex: 69 };
    expect(panMarketChartViewport(viewport, 120, 100, 300)).toEqual({ startIndex: 30, endIndex: 59 });
    expect(panMarketChartViewport(viewport, 120, -100, 300)).toEqual({ startIndex: 50, endIndex: 79 });
    expect(panMarketChartViewport(viewport, 120, 10000, 300)).toEqual({ startIndex: 0, endIndex: 29 });
    expect(panMarketChartViewport(viewport, 120, -10000, 300)).toEqual({ startIndex: 90, endIndex: 119 });
    expect(panMarketChartViewport(buildFullMarketChartViewport(120), 120, 100, 300)).toEqual({
      startIndex: 0,
      endIndex: 119,
    });
  });
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
cd app/web/streamlit_components/portfolio_monitoring_workbench
npx vitest run src/workbenchState.test.ts
```

Expected: FAIL because the four viewport helpers are not exported from `workbenchState.ts`.

- [ ] **Step 3: Implement the viewport type, normalization, zoom and pan**

Add immediately after `nearestMarketChartRowIndex` in `workbenchState.ts`:

```ts
export const MIN_MARKET_CHART_VISIBLE_ROWS = 15;

export type MarketChartViewport = {
  startIndex: number;
  endIndex: number;
};

function safeMarketChartRowCount(rowCount: number) {
  return Math.max(Math.floor(Number.isFinite(rowCount) ? rowCount : 0), 1);
}

export function buildFullMarketChartViewport(rowCount: number): MarketChartViewport {
  const safeRowCount = safeMarketChartRowCount(rowCount);
  return { startIndex: 0, endIndex: safeRowCount - 1 };
}

export function normalizeMarketChartViewport(
  viewport: MarketChartViewport,
  rowCount: number,
  minimumVisible = MIN_MARKET_CHART_VISIBLE_ROWS,
): MarketChartViewport {
  const safeRowCount = safeMarketChartRowCount(rowCount);
  const minimumCount = Math.min(
    Math.max(Math.floor(Number.isFinite(minimumVisible) ? minimumVisible : 1), 1),
    safeRowCount,
  );
  const requestedStart = Number.isFinite(viewport.startIndex) ? Math.floor(viewport.startIndex) : 0;
  const requestedEnd = Number.isFinite(viewport.endIndex) ? Math.floor(viewport.endIndex) : requestedStart;
  const requestedCount = Math.max(requestedEnd - requestedStart + 1, minimumCount);
  const visibleCount = Math.min(requestedCount, safeRowCount);
  const startIndex = Math.min(Math.max(requestedStart, 0), safeRowCount - visibleCount);
  return { startIndex, endIndex: startIndex + visibleCount - 1 };
}

export function zoomMarketChartViewport(
  viewport: MarketChartViewport,
  rowCount: number,
  anchorRatio: number,
  direction: "in" | "out",
  minimumVisible = MIN_MARKET_CHART_VISIBLE_ROWS,
): MarketChartViewport {
  const normalized = normalizeMarketChartViewport(viewport, rowCount, minimumVisible);
  const safeRowCount = safeMarketChartRowCount(rowCount);
  const visibleCount = normalized.endIndex - normalized.startIndex + 1;
  const minimumCount = Math.min(
    Math.max(Math.floor(Number.isFinite(minimumVisible) ? minimumVisible : 1), 1),
    safeRowCount,
  );
  const targetCount = direction === "in"
    ? Math.max(minimumCount, Math.round(visibleCount * 0.8))
    : Math.min(safeRowCount, Math.round(visibleCount * 1.25));
  if (targetCount === visibleCount) return normalized;
  const ratio = Number.isFinite(anchorRatio) ? Math.min(Math.max(anchorRatio, 0), 1) : 0.5;
  const anchorIndex = normalized.startIndex + ratio * Math.max(visibleCount - 1, 0);
  const targetStart = Math.round(anchorIndex - ratio * Math.max(targetCount - 1, 0));
  return normalizeMarketChartViewport(
    { startIndex: targetStart, endIndex: targetStart + targetCount - 1 },
    safeRowCount,
    targetCount,
  );
}

export function panMarketChartViewport(
  viewport: MarketChartViewport,
  rowCount: number,
  deltaX: number,
  plotWidth: number,
): MarketChartViewport {
  const normalized = normalizeMarketChartViewport(viewport, rowCount);
  if (!Number.isFinite(deltaX) || !Number.isFinite(plotWidth) || plotWidth <= 0) return normalized;
  const visibleCount = normalized.endIndex - normalized.startIndex + 1;
  const rowDelta = Math.round((deltaX / plotWidth) * visibleCount);
  return normalizeMarketChartViewport({
    startIndex: normalized.startIndex - rowDelta,
    endIndex: normalized.endIndex - rowDelta,
  }, rowCount, visibleCount);
}
```

- [ ] **Step 4: Run focused and complete React tests**

Run:

```bash
cd app/web/streamlit_components/portfolio_monitoring_workbench
npx vitest run src/workbenchState.test.ts
npm run typecheck
```

Expected: one test file PASS with 24 tests total; TypeScript reports no errors.

- [ ] **Step 5: Commit Task 1**

```bash
git add app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.ts \
  app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.test.ts
git commit -m "포트폴리오 차트 viewport 계산 추가"
```

---

### Task 2: Direct Security Zoom / Pan Interaction UI

**Files:**
- Modify: `tests/test_portfolio_monitoring_component.py:35-62`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx:1-25,202-340`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css:184-213,329-334`
- Rebuild: `app/web/streamlit_components/portfolio_monitoring_workbench/component_static/`

**Interfaces:**
- Consumes: Task 1의 `MarketChartViewport`와 full/zoom/pan helpers, 기존 `SelectedItemMarketChart.rows`
- Produces: visible-row SVG renderer, pointer wheel/drag handlers, `− / + / 전체 보기` controls, range label과 drag state CSS

- [ ] **Step 1: Add a failing Python source contract**

Add to `PortfolioMonitoringComponentTests`:

```python
    def test_market_chart_exposes_client_side_zoom_pan_controls(self) -> None:
        source = Path(
            "app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx"
        ).read_text(encoding="utf-8")
        styles = Path(
            "app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css"
        ).read_text(encoding="utf-8")

        self.assertIn("zoomMarketChartViewport", source)
        self.assertIn("panMarketChartViewport", source)
        self.assertIn("onWheel={handleWheel}", source)
        self.assertIn("onDoubleClick={resetViewport}", source)
        self.assertIn('aria-label="가격 차트 확대"', source)
        self.assertIn('aria-label="가격 차트 축소"', source)
        self.assertIn("전체 보기", source)
        self.assertIn('event.pointerType === "touch"', source)
        self.assertIn(".pm-market-hit-area.is-draggable", styles)
        self.assertIn("touch-action: pan-y;", styles)
```

- [ ] **Step 2: Run the static contract and verify RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_portfolio_monitoring_component.PortfolioMonitoringComponentTests.test_market_chart_exposes_client_side_zoom_pan_controls -v
```

Expected: FAIL because zoom/pan source strings and controls do not exist.

- [ ] **Step 3: Import viewport helpers and declare drag state**

Add these imports from `workbenchState` in `PortfolioMonitoringWorkbench.tsx`:

```ts
  buildFullMarketChartViewport,
  MIN_MARKET_CHART_VISIBLE_ROWS,
  panMarketChartViewport,
  zoomMarketChartViewport,
```

Add this type above `MarketPriceChart`:

```ts
type MarketChartDrag = {
  pointerId: number;
  startClientX: number;
  plotWidth: number;
  startViewport: { startIndex: number; endIndex: number };
  didDrag: boolean;
};
```

- [ ] **Step 4: Add viewport state, reset key and visible-row rendering**

At the start of `MarketPriceChart`, rename the full projection rows to `allRows` and add the state and
effects below. Preserve the existing mode reset on `monitoring_item_id`:

```ts
  const allRows = projection.rows;
  const viewportKey = `${projection.monitoring_item_id ?? "none"}:${allRows.length}:${allRows[0]?.date ?? ""}:${allRows[allRows.length - 1]?.date ?? ""}`;
  const [viewport, setViewport] = useState(() => buildFullMarketChartViewport(allRows.length));
  const [isDragging, setIsDragging] = useState(false);
  const dragRef = useRef<MarketChartDrag | null>(null);

  useEffect(() => {
    setViewport(buildFullMarketChartViewport(allRows.length));
    setActiveIndex(null);
    setIsDragging(false);
    dragRef.current = null;
  }, [viewportKey]);
```

Change the existing non-READY condition to `!allRows.length`. After that return, declare the visible
rows as the local `rows` value so the existing bounds/path/candle/volume/date/tooltip renderer
automatically uses only the viewport:

```ts
  const rows = allRows.slice(viewport.startIndex, viewport.endIndex + 1);
  const bounds = buildMarketChartBounds(rows);
  const visibleCount = rows.length;
  const isFullViewport = visibleCount >= allRows.length;
  const canZoomIn = visibleCount > Math.min(MIN_MARKET_CHART_VISIBLE_ROWS, allRows.length);
  const rangeLabel = `${compactDate(rows[0]?.date ?? null)}–${compactDate(rows[rows.length - 1]?.date ?? null)} · ${visibleCount}거래일`;
```

Remove the old duplicate `const rows = projection.rows` and `const bounds = buildMarketChartBounds(rows)`
lines. `activeIndex` remains a visible-row index. Keep the existing x/y calculations, `rows` references
and tooltip content unchanged.

- [ ] **Step 5: Implement explicit zoom/reset functions and wheel anchor**

Add inside `MarketPriceChart` after plot dimensions are known:

```ts
  const resetViewport = () => {
    setViewport(buildFullMarketChartViewport(allRows.length));
    setActiveIndex(null);
  };

  const zoomAt = (direction: "in" | "out", anchorRatio = 0.5) => {
    setViewport((current) => zoomMarketChartViewport(current, allRows.length, anchorRatio, direction));
    setActiveIndex(null);
  };

  const handleWheel = (event: React.WheelEvent<SVGRectElement>) => {
    event.preventDefault();
    const svg = event.currentTarget.ownerSVGElement;
    if (!svg) return;
    const rect = svg.getBoundingClientRect();
    if (!rect.width) return;
    const pointerX = ((event.clientX - rect.left) / rect.width) * width;
    const anchorRatio = (pointerX - inset.left) / plotWidth;
    zoomAt(event.deltaY < 0 ? "in" : "out", anchorRatio);
  };
```

- [ ] **Step 6: Implement 4px pointer drag with capture and hover recovery**

Add these handlers inside `MarketPriceChart`:

```ts
  const handlePointerDown = (event: React.PointerEvent<SVGRectElement>) => {
    if (event.pointerType === "touch" || isFullViewport) return;
    const svg = event.currentTarget.ownerSVGElement;
    if (!svg) return;
    const rect = svg.getBoundingClientRect();
    if (!rect.width) return;
    dragRef.current = {
      pointerId: event.pointerId,
      startClientX: event.clientX,
      plotWidth: rect.width * (plotWidth / width),
      startViewport: viewport,
      didDrag: false,
    };
    event.currentTarget.setPointerCapture(event.pointerId);
  };

  const handlePointerMove = (event: React.PointerEvent<SVGRectElement>) => {
    const drag = dragRef.current;
    if (!drag || drag.pointerId !== event.pointerId) {
      if (!isDragging && event.pointerType !== "touch") updateActive(event);
      return;
    }
    const deltaX = event.clientX - drag.startClientX;
    if (!drag.didDrag && Math.abs(deltaX) < 4) {
      updateActive(event);
      return;
    }
    drag.didDrag = true;
    setIsDragging(true);
    setActiveIndex(null);
    setViewport(panMarketChartViewport(drag.startViewport, allRows.length, deltaX, drag.plotWidth));
  };

  const finishPointerDrag = (event: React.PointerEvent<SVGRectElement>) => {
    const drag = dragRef.current;
    if (drag?.pointerId === event.pointerId && event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
    dragRef.current = null;
    setIsDragging(false);
    if (!drag?.didDrag && event.pointerType !== "touch") updateActive(event);
  };
```

Attach these props to the existing hit area and remove its direct `onPointerMove={updateActive}`:

```tsx
            className={`pm-market-hit-area ${!isFullViewport ? "is-draggable" : ""} ${isDragging ? "is-dragging" : ""}`}
            onWheel={handleWheel}
            onDoubleClick={resetViewport}
            onPointerDown={handlePointerDown}
            onPointerMove={handlePointerMove}
            onPointerUp={finishPointerDrag}
            onPointerCancel={finishPointerDrag}
```

Keep `onPointerLeave`, focus, blur and ArrowLeft/ArrowRight handlers, but use `visibleRows.length` in their bounds.

- [ ] **Step 7: Add the range label and explicit controls without increasing chart height**

Replace the right side of the chart header with this toolbar while retaining the existing line/candle buttons:

```tsx
        <div className="pm-market-toolbar">
          <span className="pm-market-range">{rangeLabel}</span>
          <div className="pm-market-zoom-controls" role="group" aria-label="가격 차트 범위">
            <button type="button" aria-label="가격 차트 축소" disabled={isFullViewport} onClick={() => zoomAt("out")}>−</button>
            <button type="button" aria-label="가격 차트 확대" disabled={!canZoomIn} onClick={() => zoomAt("in")}>+</button>
            <button type="button" disabled={isFullViewport} onClick={resetViewport}>전체 보기</button>
          </div>
          <div className="pm-chart-mode-switch" role="group" aria-label="가격 차트 방식">
            <button type="button" className={mode === "line" ? "is-active" : ""} onClick={() => setMode("line")}>라인</button>
            <button type="button" className={mode === "candle" ? "is-active" : ""} onClick={() => setMode("candle")}>캔들</button>
          </div>
        </div>
```

- [ ] **Step 8: Style the toolbar, controls and cursor states**

Add to `style.css` next to existing market-chart styles:

```css
.pm-market-toolbar { display: flex; align-items: center; justify-content: flex-end; gap: 7px; flex-wrap: wrap; }
.pm-market-range { color: #738795 !important; font-size: 9px !important; font-weight: 800 !important; letter-spacing: 0 !important; }
.pm-market-zoom-controls { display: inline-flex; gap: 2px; padding: 3px; border: 1px solid #d5e1e8; border-radius: 9px; background: #f7fafb; }
.pm-market-zoom-controls button { min-width: 28px; padding: 6px 7px; border: 0; border-radius: 7px; color: #45667d; background: transparent; cursor: pointer; font-size: 10px; font-weight: 850; }
.pm-market-zoom-controls button:last-child { min-width: 58px; }
.pm-market-zoom-controls button:hover:not(:disabled) { color: #246fa9; background: #e9f2f8; }
.pm-market-zoom-controls button:disabled { cursor: default; opacity: .42; }
.pm-market-hit-area.is-draggable { cursor: grab; }
.pm-market-hit-area.is-dragging { cursor: grabbing; }
```

Add inside `@media (max-width: 420px)`:

```css
  .pm-market-chart-section > header { align-items: flex-start; flex-direction: column; }
  .pm-market-toolbar { width: 100%; justify-content: space-between; }
  .pm-market-range { flex-basis: 100%; }
  .pm-market-zoom-controls button { min-width: 34px; min-height: 32px; }
```

Do not change `.pm-market-hit-area { touch-action: pan-y; }`.

- [ ] **Step 9: Run React, Python contract, typecheck and build**

Run:

```bash
cd app/web/streamlit_components/portfolio_monitoring_workbench
npm test
npm run typecheck
npm run build
cd ../../../..
.venv/bin/python -m unittest tests.test_portfolio_monitoring_component -v
git diff --check
```

Expected: Vitest 24 tests PASS, typecheck PASS, Vite writes `component_static`, Python component tests 11 PASS, diff-check PASS.

- [ ] **Step 10: Commit Task 2**

```bash
git add tests/test_portfolio_monitoring_component.py \
  app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx \
  app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css \
  app/web/streamlit_components/portfolio_monitoring_workbench/component_static
git commit -m "포트폴리오 종목 차트 줌과 이동 추가"
```

---

### Task 3: Integration QA And Durable Closeout

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/portfolio-monitoring-chart-zoom-pan-v1-20260719/DESIGN.md`
- Modify: `.aiworkspace/note/finance/tasks/active/portfolio-monitoring-chart-zoom-pan-v1-20260719/PLAN.md`
- Modify: `.aiworkspace/note/finance/tasks/active/portfolio-monitoring-chart-zoom-pan-v1-20260719/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/portfolio-monitoring-chart-zoom-pan-v1-20260719/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/portfolio-monitoring-chart-zoom-pan-v1-20260719/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/portfolio-monitoring-chart-zoom-pan-v1-20260719/RISKS.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/PORTFOLIO_MONITORING_REACT_COMMAND_CENTER.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Create local only: `portfolio-monitoring-chart-zoom-pan-qa.png`

**Interfaces:**
- Consumes: Tasks 1-2의 viewport helpers와 production React bundle
- Produces: verified desktop/mobile behavior, durable architecture/task handoff, generated QA screenshot

- [ ] **Step 1: Run the complete focused regression before Browser QA**

Run:

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_portfolio_monitoring_*.py' -v
cd app/web/streamlit_components/portfolio_monitoring_workbench
npm test
npm run typecheck
npm run build
cd ../../../..
git diff --check
```

Expected: Portfolio Monitoring Python 101 tests PASS, Vitest 24 tests PASS, typecheck/build/diff-check PASS.

- [ ] **Step 2: Perform desktop Browser QA against the production bundle**

Open `Operations > Portfolio Monitoring`, choose a direct stock/ETF with a READY price chart, and verify in this order:

1. Hover shows the original OHLCV tooltip.
2. Wheel up at the left, center and right keeps that date neighborhood anchored while reducing the range label count.
3. A horizontal drag shorter than 4px does not move the viewport.
4. Drag right reveals earlier dates; drag left reveals later dates; both clamp at the available edges.
5. Tooltip is hidden during drag and returns after pointer release.
6. Switching line → candle → line preserves range label and viewport.
7. Double-click and `전체 보기` both restore all 120 available sessions.
8. Group value hover and selected strategy value-only chart remain unchanged.

If the actual DB has no active direct item, use the existing local deterministic component harness with the rebuilt production bundle and record that limitation in `RISKS.md`.

- [ ] **Step 3: Perform 420px Browser QA**

Set viewport to `420×900` and verify:

1. Range label, `− / + / 전체 보기`, line/candle controls wrap without overlap.
2. `+` zooms and `−` zooms out; `전체 보기` restores full range.
3. Vertical page scroll remains available over the chart.
4. Touch drag/pinch behavior is absent.
5. `document.documentElement.scrollWidth === document.documentElement.clientWidth`.

Save one desktop candle-mode screenshot with an expanded range and visible OHLCV tooltip as
`portfolio-monitoring-chart-zoom-pan-qa.png`. Do not stage it.

- [ ] **Step 4: Synchronize task, canonical and root handoff documentation**

Apply these exact status outcomes after QA:

```markdown
- Current: client-side zoom/pan 구현, 통합 검증과 Browser QA 완료
- Roadmap: 3/3차 완료
- Next: 없음. 120거래일 초과 history, mobile pinch/touch pan, 기간 selector는 별도 승인 범위다.
```

Record in durable docs:

- direct security chart owns a client-only viewport over the existing maximum 120 stored daily rows;
- wheel/drag never trigger Python rerun or DB/provider read;
- selected strategy and group value charts remain non-zoomable;
- mobile V1 is explicit-controls-only;
- actual test counts, Browser viewport sizes, console/overflow result and any fixture limitation.

- [ ] **Step 5: Re-run final verification after documentation changes**

Run:

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_portfolio_monitoring_*.py' -v
cd app/web/streamlit_components/portfolio_monitoring_workbench
npm test
npm run typecheck
npm run build
cd ../../../..
git diff --check
git status --short
```

Expected: Python 101 tests PASS, Vitest 24 tests PASS, typecheck/build/diff-check PASS. Status contains only intended tracked docs/code/build changes plus pre-existing untracked/generated artifacts.

- [ ] **Step 6: Stage only closeout documents and commit**

```bash
git add .aiworkspace/note/finance/tasks/active/portfolio-monitoring-chart-zoom-pan-v1-20260719 \
  .aiworkspace/note/finance/docs/architecture/PORTFOLIO_MONITORING_REACT_COMMAND_CENTER.md \
  .aiworkspace/note/finance/docs/ROADMAP.md \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git diff --cached --check
git diff --cached --name-only
git commit -m "포트폴리오 차트 줌 작업 기록 정리"
```

Confirm the staged name list excludes `.aiworkspace/note/finance/registries/`, `.aiworkspace/note/finance/saved/`, run history, `.superpowers/` and PNG files before committing.
