# Today Home React Workbench V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Today page's primary `st.markdown` renderer with a Market Context-style React workbench whose evidence risk labels and daily-close portfolio performance chart are explicit and readable.

**Architecture:** Python remains the sole owner of persisted data loading, source semantics, risk presentation labels, portfolio curve calculations, and navigation targets. A new typed React/Vite Streamlit component owns visual hierarchy, responsive layout, SVG coordinates, hover/focus interaction, and emits only allow-listed navigation events; `today_page.py` adapts those events and retains a compact read-only fallback.

**Tech Stack:** Python 3.12, Streamlit multipage API, `streamlit.components.v1`, React 18, TypeScript 5.7, Vite 6, Vitest 4, SVG, pytest/unittest.

**Execution Result:** Complete on 2026-07-22. All five tasks and browser QA were executed inline. The browser review added one evidence-based correction: an all-positive/all-negative Y domain now stops at the 0% baseline instead of inventing an opposite-sign padded range.

## Global Constraints

- Preserve `Ingestion -> DB -> Loader -> UI`; Today render must not fetch providers.
- Today render must not create a portfolio group or write registry, saved setup, monitoring log, order, or rebalance state.
- Keep existing page paths and the three approved action destinations.
- React is the primary renderer; the Python HTML path is fallback only.
- Evidence cards use no left status border; color is always paired with `지지 신호 / 중립 신호 / 주의 신호 / 자료 제한·엇갈림` text.
- Typography tokens are fixed at metadata 10px, helper/axis 11px, body/badge 12px, evidence title 13px, section/metric 15px, portfolio title 18px, hero title 26px.
- Portfolio chart means `daily`, `stored_close`, `aggregation=none`, `intraday=false`, with at most the latest 60 actual observations and no synthetic rows.
- X uses actual date spacing; Y uses `cumulative_return = unit_value - 1`; tooltip adds total portfolio value only as a secondary unit.
- Do not stage `.aiworkspace/note/finance/registries/`, `saved/`, `run_history/`, `.superpowers/`, or generated QA images.

---

## File Structure

- Modify `app/services/today.py`: schema V2, evidence presentation projection, recent-observation return dates, chart rows and metadata.
- Create `app/web/today_react_component.py`: component availability, declaration, safe payload call.
- Modify `app/web/today_page.py`: React primary render, allow-listed event normalization and `st.switch_page`, compact fallback.
- Create `app/web/streamlit_components/today_workbench/src/types.ts`: exact payload/event types.
- Create `app/web/streamlit_components/today_workbench/src/presentation.ts`: pure chart/tick/format helpers.
- Create `app/web/streamlit_components/today_workbench/src/presentation.test.ts`: Vitest behavior tests.
- Create `app/web/streamlit_components/today_workbench/src/TodayPortfolioChart.tsx`: SVG performance chart.
- Create `app/web/streamlit_components/today_workbench/src/TodayWorkbench.tsx`: approved A layout and navigation events.
- Create `app/web/streamlit_components/today_workbench/src/main.tsx`: React root.
- Create `app/web/streamlit_components/today_workbench/src/style.css`: Market Context visual system and responsive rules.
- Create component package/config/build files under `app/web/streamlit_components/today_workbench/`.
- Modify `tests/test_today_home.py`: service, wrapper, renderer, route and source-contract regression tests.
- Modify durable finance docs and task logs only after implementation verification.

---

### Task 1: Today V2 Evidence And Portfolio Contract

**Files:**
- Modify: `tests/test_today_home.py`
- Modify: `app/services/today.py`

**Interfaces:**
- Consumes: existing `build_today_read_model(...) -> dict[str, object]` inputs and Portfolio Monitoring group curve rows.
- Produces: `today_home_v2` payload with evidence presentation fields, `portfolio.metrics.latest_observation_return`, return dates, `portfolio.curve`, and `portfolio.curve_metadata`.

- [x] **Step 1: Write failing evidence-presentation tests**

Add focused tests that call `build_today_read_model` using the existing fixture builder and assert the exact source-specific rules:

```python
def test_market_evidence_projects_explicit_signal_risk_and_quality_labels(self) -> None:
    inputs = self._complete_inputs()
    inputs["economic_cycle"]["headline"]["phase"] = "recovery"
    inputs["futures_macro"]["macro"]["summary"]["tone"] = "mixed"
    inputs["sentiment"]["coverage"]["stale_count"] = 1
    model = self._builder()(**inputs)
    rows = {row["key"]: row for row in model["market"]["evidence"]}
    self.assertEqual(rows["economic_cycle"]["signal_level"], "support")
    self.assertEqual(rows["economic_cycle"]["risk_label"], "위험도 낮음")
    self.assertEqual(rows["sp500"]["signal_level"], "watch")
    self.assertEqual(rows["sp500"]["risk_label"], "위험도 높음")
    self.assertEqual(rows["futures_macro"]["signal_level"], "neutral")
    self.assertEqual(rows["sentiment"]["data_quality_label"], "자료 제한")
```

Add the unavailable case explicitly:

```python
def test_unavailable_evidence_never_fabricates_low_or_high_risk(self) -> None:
    inputs = self._complete_inputs()
    inputs["economic_cycle"] = {"status": "UNAVAILABLE"}
    model = self._builder()(**inputs)
    row = next(item for item in model["market"]["evidence"] if item["key"] == "economic_cycle")
    self.assertEqual(row["signal_level"], "limited")
    self.assertEqual(row["risk_label"], "판단 제한")
    self.assertNotIn(row["risk_label"], {"위험도 낮음", "위험도 높음"})
```

- [x] **Step 2: Run the evidence test and verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_today_home.py -k 'signal_risk or unavailable_evidence' -q
```

Expected: FAIL because `signal_level`, `risk_label`, and `data_quality_label` do not exist.

- [x] **Step 3: Implement deterministic Python-owned presentation mapping**

Add constants and a pure helper in `app/services/today.py`:

```python
_SIGNAL_LABELS = {
    "support": ("지지 신호", "위험도 낮음"),
    "neutral": ("중립 신호", "위험도 중간"),
    "watch": ("주의 신호", "위험도 높음"),
    "limited": ("자료 제한", "판단 제한"),
}

def _evidence_presentation(
    *,
    key: str,
    status: str,
    tone: str,
    semantic_code: str = "",
    data_limited: bool = False,
) -> dict[str, str]:
    if status == "UNAVAILABLE":
        level = "limited"
    elif key == "economic_cycle":
        level = {
            "RECOVERY": "support",
            "EXPANSION": "support",
            "SLOWDOWN": "watch",
            "RECESSION": "watch",
        }.get(semantic_code.upper(), "neutral")
    elif key == "sp500":
        level = {
            "VERY_HIGH": "watch",
            "HIGH": "watch",
            "MID": "neutral",
            "NEUTRAL": "neutral",
            "LOW": "support",
            "VERY_LOW": "support",
        }.get(semantic_code.upper(), "limited")
    else:
        normalized_tone = tone.strip().lower()
        if normalized_tone in {"positive", "support"}:
            level = "support"
        elif normalized_tone in {"warning", "negative", "danger", "burden"}:
            level = "watch"
        elif normalized_tone in {"neutral", "mixed"}:
            level = "neutral"
        else:
            level = "limited"
    signal_label, risk_label = _SIGNAL_LABELS[level]
    return {
        "signal_level": level,
        "signal_label": signal_label,
        "risk_label": risk_label,
        "data_quality_label": "자료 제한" if data_limited else "자료 확인",
    }
```

Call the helper inside all four evidence projection functions. Pass `headline.phase` for Economic Cycle, `multiple_regime.bucket` for S&P, canonical tone for Futures/Sentiment, and set `data_limited` when status is partial, provisional, stale, or missing.

- [x] **Step 4: Run evidence tests and verify GREEN**

Run:

```bash
.venv/bin/python -m pytest tests/test_today_home.py -k 'evidence or market' -q
```

Expected: all selected tests PASS.

- [x] **Step 5: Write failing portfolio curve-semantics tests**

Add a group curve fixture containing dates, `unit_value`, and `total_value`, then assert:

```python
def test_portfolio_curve_identifies_daily_stored_close_and_exact_return_dates(self) -> None:
    inputs = self._complete_inputs()
    inputs["portfolio"]["active_group"]["curve"] = [
        {"date": "2026-07-17", "unit_value": 1.00, "total_value": 10000},
        {"date": "2026-07-18", "unit_value": 1.02, "total_value": 10200},
        {"date": "2026-07-21", "unit_value": 1.0812, "total_value": 10812},
    ]
    model = self._builder()(**inputs)
    portfolio = model["portfolio"]
    self.assertEqual(model["schema_version"], "today_home_v2")
    self.assertEqual(portfolio["metrics"]["latest_observation_return"], 0.06)
    self.assertEqual(portfolio["metrics"]["return_from_date"], "2026-07-18")
    self.assertEqual(portfolio["metrics"]["return_to_date"], "2026-07-21")
    self.assertEqual(portfolio["curve"][0]["cumulative_return"], 0.0)
    self.assertEqual(portfolio["curve"][-1]["total_value"], 10812.0)
    self.assertEqual(portfolio["curve_metadata"], {
        "interval": "daily",
        "price_basis": "stored_close",
        "aggregation": "none",
        "intraday": False,
        "observation_count": 3,
        "start_date": "2026-07-17",
        "end_date": "2026-07-21",
    })
```

Use `assertAlmostEqual(..., places=10)` for floating-point return values. Update the existing complete-input assertion from `today_home_v1` to `today_home_v2` and from `metrics.day_return` to `metrics.latest_observation_return`; assert its existing dates are `2026-07-18` and `2026-07-21`.

- [x] **Step 6: Run the curve test and verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_today_home.py -k 'curve_identifies_daily' -q
```

Expected: FAIL because V1 exposes `{date, value}` and `day_return` without dates or metadata.

- [x] **Step 7: Implement the V2 curve projection**

Replace `_daily_return` and `_portfolio_curve` with one projection that sorts/filters the last 60 valid rows and returns exact metadata:

```python
def _portfolio_curve_projection(curve: Any) -> dict[str, Any]:
    projected: list[dict[str, Any]] = []
    for row in _records(curve):
        on_date = _date_text(row.get("date"))
        unit_value = _safe_float(row.get("unit_value"))
        if on_date is None or unit_value is None:
            continue
        projected.append({
            "date": on_date,
            "unit_value": unit_value,
            "total_value": _safe_float(row.get("total_value")),
            "cumulative_return": unit_value - 1.0,
        })
    projected = sorted(projected, key=lambda row: row["date"])[-60:]
    latest_return = None
    return_from_date = None
    return_to_date = None
    if len(projected) >= 2 and projected[-2]["unit_value"] != 0:
        latest_return = projected[-1]["unit_value"] / projected[-2]["unit_value"] - 1.0
        return_from_date = projected[-2]["date"]
        return_to_date = projected[-1]["date"]
    return {
        "rows": projected,
        "latest_observation_return": latest_return,
        "return_from_date": return_from_date,
        "return_to_date": return_to_date,
        "metadata": {
            "interval": "daily",
            "price_basis": "stored_close",
            "aggregation": "none",
            "intraday": False,
            "observation_count": len(projected),
            "start_date": projected[0]["date"] if projected else None,
            "end_date": projected[-1]["date"] if projected else None,
        },
    }
```

Set `TODAY_SCHEMA_VERSION = "today_home_v2"`; project the new metric/date fields and metadata without retaining the ambiguous `day_return` UI contract.

- [x] **Step 8: Run all Today service tests and commit**

Run:

```bash
.venv/bin/python -m pytest tests/test_today_home.py -q
.venv/bin/python -m py_compile app/services/today.py
git diff --check
```

Expected: all Today tests PASS, compile exits 0, diff check is silent.

Commit only the service unit:

```bash
git add app/services/today.py tests/test_today_home.py
git commit -m "개선: Today 근거와 성과곡선 의미 명시"
```

---

### Task 2: Typed Chart Presentation Package

**Files:**
- Create: `app/web/streamlit_components/today_workbench/package.json`
- Create: `app/web/streamlit_components/today_workbench/tsconfig.json`
- Create: `app/web/streamlit_components/today_workbench/vite.config.ts`
- Create: `app/web/streamlit_components/today_workbench/index.html`
- Create: `app/web/streamlit_components/today_workbench/src/types.ts`
- Create: `app/web/streamlit_components/today_workbench/src/presentation.test.ts`
- Create: `app/web/streamlit_components/today_workbench/src/presentation.ts`

**Interfaces:**
- Consumes: V2 curve rows and metadata from Task 1.
- Produces: `buildChartSeries`, `buildDateTicks`, `buildPercentTicks`, `chartDomains`, `pointCoordinates`, and shared payload types used by the React UI.

- [x] **Step 1: Create package/config and exact TypeScript contracts**

Use React 18/Vite 6/Vitest 4 versions aligned with `portfolio_monitoring_workbench`. `package.json` must contain:

```json
{
  "name": "today-workbench-component",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite --host 0.0.0.0",
    "build": "vite build --outDir component_static",
    "test": "vitest run",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "@vitejs/plugin-react": "^4.3.4",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "streamlit-component-lib": "^2.0.0",
    "typescript": "^5.7.3",
    "vite": "^6.0.7"
  },
  "devDependencies": {
    "@types/react": "^18.3.31",
    "@types/react-dom": "^18.3.7",
    "vitest": "^4.1.10"
  }
}
```

In `types.ts`, define the Python-matching contract explicitly:

```ts
export type SignalLevel = "support" | "neutral" | "watch" | "limited";

export type EvidenceRow = {
  key: string;
  label: string;
  status: "READY" | "PARTIAL" | "UNAVAILABLE";
  title: string;
  detail: string;
  as_of_date: string | null;
  signal_level: SignalLevel;
  signal_label: string;
  risk_label: string;
  data_quality_label: string;
};

export type PortfolioCurveRow = {
  date: string;
  unit_value: number;
  total_value: number | null;
  cumulative_return: number;
};

export type CurveMetadata = {
  interval: "daily";
  price_basis: "stored_close";
  aggregation: "none";
  intraday: false;
  observation_count: number;
  start_date: string | null;
  end_date: string | null;
};

export type TodayPayload = {
  schema_version: "today_home_v2";
  header: Record<string, string | number | null>;
  market: {
    status: string;
    tone: string;
    headline: string;
    summary: string;
    evidence: EvidenceRow[];
    next_event: Record<string, string | number | null> | null;
    watch_items: string[];
  };
  portfolio: {
    status: string;
    name: string;
    basis_date: string | null;
    summary: string;
    metrics: {
      current_value: number | null;
      latest_observation_return: number | null;
      return_from_date: string | null;
      return_to_date: string | null;
      total_return: number | null;
    };
    curve: PortfolioCurveRow[];
    curve_metadata: CurveMetadata;
    contributors: Array<{ symbol: string; value: number; tone: string }>;
    review_items: Array<{ severity: string; meaning: string }>;
    active_item_count: number;
  };
};

export type TodayEventId =
  | "open_market_research"
  | "open_stock_research"
  | "open_portfolio_monitoring";
```

Run `npm install` in the component directory to generate the lockfile; do not use workspace-global dependencies.

- [x] **Step 2: Write failing pure presentation tests**

Create Vitest cases that prove date spacing, tick limits, percent domain, and missing total values:

```ts
it("uses elapsed calendar time for x coordinates", () => {
  const series = buildChartSeries([
    { date: "2026-07-18", unit_value: 1, total_value: 10000, cumulative_return: 0 },
    { date: "2026-07-21", unit_value: 1.06, total_value: 10600, cumulative_return: .06 },
    { date: "2026-07-22", unit_value: 1.07, total_value: 10700, cumulative_return: .07 },
  ]);
  const domain = chartDomains(series);
  const saturday = pointCoordinates(series[0], domain, { width: 400, height: 200, left: 50, right: 20, top: 20, bottom: 30 });
  const monday = pointCoordinates(series[1], domain, { width: 400, height: 200, left: 50, right: 20, top: 20, bottom: 30 });
  const tuesday = pointCoordinates(series[2], domain, { width: 400, height: 200, left: 50, right: 20, top: 20, bottom: 30 });
  expect(monday.x - saturday.x).toBeCloseTo(3 * (tuesday.x - monday.x));
});

it("keeps responsive date ticks within the requested count", () => {
  const series = buildChartSeries(Array.from({ length: 9 }, (_, index) => ({
    date: `2026-07-${String(index + 10).padStart(2, "0")}`,
    unit_value: 1 + index / 100,
    total_value: 10000 + index * 100,
    cumulative_return: index / 100,
  })));
  expect(buildDateTicks(series, 5)).toHaveLength(5);
  expect(buildDateTicks(series, 3)).toHaveLength(3);
  expect(buildDateTicks(series, 3)[0].date).toBe(series[0].date);
  expect(buildDateTicks(series, 3).at(-1)?.date).toBe(series.at(-1)?.date);
});

it("includes zero in the percent domain and keeps missing tooltip value", () => {
  const series = buildChartSeries([
    { date: "2026-07-18", unit_value: .98, total_value: null, cumulative_return: -.02 },
    { date: "2026-07-21", unit_value: 1.03, total_value: 10300, cumulative_return: .03 },
  ]);
  const domain = chartDomains(series);
  expect(domain.low).toBeLessThanOrEqual(0);
  expect(domain.high).toBeGreaterThanOrEqual(0);
  expect(buildPercentTicks(domain, 5).some((value) => Math.abs(value) < 1e-12)).toBe(true);
  expect(series[0].total_value).toBeNull();
});
```

- [x] **Step 3: Run Vitest and verify RED**

Run:

```bash
cd app/web/streamlit_components/today_workbench
npm test -- --reporter=verbose
```

Expected: FAIL because `presentation.ts` exports do not exist.

- [x] **Step 4: Implement pure presentation helpers**

Implement date parsing with `Date.parse(date + "T00:00:00Z")`, reject non-finite return values, preserve actual rows, and calculate padded percent domains. `pointCoordinates` must use epoch-time ratio for X and return ratio for Y. `buildDateTicks` must always retain range ends and choose interior targets by elapsed time, not row index.

Use this public shape:

```ts
export type ChartPoint = PortfolioCurveRow & { timestamp: number };
export type ChartDomain = { minTime: number; maxTime: number; low: number; high: number };
export type ChartInsets = { width: number; height: number; left: number; right: number; top: number; bottom: number };

export function buildChartSeries(rows: PortfolioCurveRow[]): ChartPoint[];
export function buildDateTicks(series: ChartPoint[], maxTicks: number): ChartPoint[];
export function buildPercentTicks(domain: ChartDomain, maxTicks?: number): number[];
export function chartDomains(series: ChartPoint[]): ChartDomain;
export function pointCoordinates(point: ChartPoint, domain: ChartDomain, box: ChartInsets): { x: number; y: number };
```

- [x] **Step 5: Verify package helpers and commit**

Run:

```bash
cd app/web/streamlit_components/today_workbench
npm test -- --reporter=verbose
npm run typecheck
```

Expected: Vitest PASS and TypeScript exits 0.

Commit:

```bash
git add app/web/streamlit_components/today_workbench/package.json \
  app/web/streamlit_components/today_workbench/package-lock.json \
  app/web/streamlit_components/today_workbench/tsconfig.json \
  app/web/streamlit_components/today_workbench/vite.config.ts \
  app/web/streamlit_components/today_workbench/index.html \
  app/web/streamlit_components/today_workbench/src/types.ts \
  app/web/streamlit_components/today_workbench/src/presentation.ts \
  app/web/streamlit_components/today_workbench/src/presentation.test.ts
git commit -m "개선: Today React 차트 좌표 계약 추가"
```

---

### Task 3: Approved React Workbench UI

**Files:**
- Modify: `tests/test_today_home.py`
- Create: `app/web/streamlit_components/today_workbench/src/TodayPortfolioChart.tsx`
- Create: `app/web/streamlit_components/today_workbench/src/TodayWorkbench.tsx`
- Create: `app/web/streamlit_components/today_workbench/src/main.tsx`
- Create: `app/web/streamlit_components/today_workbench/src/style.css`
- Create: `app/web/streamlit_components/today_workbench/component_static/**`

**Interfaces:**
- Consumes: `TodayPayload` and presentation helpers from Task 2.
- Produces: one Streamlit-connected component that emits `{event: {id: TodayEventId}}` and builds to canonical static assets.

- [x] **Step 1: Write failing React source/style contract tests**

In `tests/test_today_home.py`, add a test reading the future TSX/CSS files and asserting the approved copy/classes:

```python
def test_today_react_source_uses_explicit_risk_labels_and_chart_semantics(self) -> None:
    root = Path("app/web/streamlit_components/today_workbench/src")
    workbench = (root / "TodayWorkbench.tsx").read_text(encoding="utf-8")
    chart = (root / "TodayPortfolioChart.tsx").read_text(encoding="utf-8")
    styles = (root / "style.css").read_text(encoding="utf-8")
    self.assertIn("signal_label", workbench)
    self.assertIn("risk_label", workbench)
    self.assertNotIn("border-left", styles)
    self.assertIn("일별 종가 기반 누적 수익률", chart)
    self.assertIn("장중 아님", chart)
    self.assertIn("Y축 · 누적 수익률 (%)", chart)
    self.assertIn("X축 · 저장 관측일", chart)
    self.assertIn("total_value", chart)
    self.assertIn("font-size: 26px", styles)
```

- [x] **Step 2: Run source contract and verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_today_home.py -k 'react_source' -q
```

Expected: FAIL with missing TSX/CSS files.

- [x] **Step 3: Implement `TodayPortfolioChart.tsx`**

Use a 960×310 SVG with insets `{top: 44, right: 28, bottom: 44, left: 78}`. Render percent grid/tick text from `buildPercentTicks`, exact date ticks from `buildDateTicks`, an area and line path from date-linear coordinates, zero line when in-domain, pointer hit area, keyboard-focusable points, and a collision-aware tooltip containing:

```text
YYYY.MM.DD · 저장 종가
누적 +N.NN%
평가액 $N,NNN
```

For fewer than two points, render `성과 추이를 표시할 관측치가 부족합니다.` plus metadata chips. Never label the line as a candlestick, day candle, weekly series, or intraday series.

- [x] **Step 4: Implement `TodayWorkbench.tsx`, `main.tsx`, and approved CSS**

The component section order must be:

```tsx
<main className="today-workbench">
  <TodayHero />
  <section className="today-context-grid">
    <EvidencePanel />
    <EventsPanel />
  </section>
  <PortfolioPanel />
  <ActionRail />
</main>
```

Evidence cards must use neutral `.today-evidence-card` borders, `.signal-{signal_level}` text pills, explicit `risk_label`, and `data_quality_label`. Do not use any source-specific left border. Action buttons call:

```ts
Streamlit.setComponentValue({ event: { id } });
```

Call `Streamlit.setFrameHeight()` after render and when payload/layout changes. Apply the exact typography tokens and responsive 760px/460px rules from the design spec.

- [x] **Step 5: Verify RED becomes GREEN and build static assets**

Run:

```bash
.venv/bin/python -m pytest tests/test_today_home.py -k 'react_source' -q
cd app/web/streamlit_components/today_workbench
npm test -- --reporter=verbose
npm run typecheck
npm run build
test -f component_static/index.html
```

Expected: Python contract PASS, Vitest PASS, typecheck/build exit 0, static index exists.

- [x] **Step 6: Commit the React UI unit**

```bash
git add tests/test_today_home.py app/web/streamlit_components/today_workbench
git commit -m "개선: Today Market Context React 워크벤치 구현"
```

---

### Task 4: Streamlit Wrapper, Event Routing, And Fallback

**Files:**
- Modify: `tests/test_today_home.py`
- Create: `app/web/today_react_component.py`
- Modify: `app/web/today_page.py`

**Interfaces:**
- Consumes: built React component and `TodayPayload`.
- Produces: `today_react_component_available`, `render_today_workbench`, `normalize_today_event`, and React-primary `render_today_page`.

- [x] **Step 1: Write failing wrapper availability/render tests**

Use temporary directories and a fake declared component:

```python
def test_today_component_availability_requires_built_index(self) -> None:
    with tempfile.TemporaryDirectory() as directory:
        build = Path(directory)
        self.assertFalse(today_react_component_available(build))
        (build / "index.html").write_text("<html></html>", encoding="utf-8")
        self.assertTrue(today_react_component_available(build))

def test_today_component_returns_allowlisted_event_envelope(self) -> None:
    component._today_component = lambda **kwargs: {"event": {"id": "open_market_research"}}
    self.assertEqual(
        render_today_workbench({"schema_version": "today_home_v2"}),
        {"event": {"id": "open_market_research"}},
    )
```

- [x] **Step 2: Run wrapper tests and verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_today_home.py -k 'component_availability or component_returns' -q
```

Expected: FAIL because `app.web.today_react_component` does not exist.

- [x] **Step 3: Implement the Python component wrapper**

Follow existing wrapper ownership:

```python
TODAY_REACT_COMPONENT_NAME = "today_workbench"
TODAY_REACT_COMPONENT_ROOT = Path(__file__).resolve().parent / "streamlit_components" / "today_workbench"
TODAY_REACT_BUILD_DIR = TODAY_REACT_COMPONENT_ROOT / "component_static"

def today_react_component_available(build_dir: Path | None = None) -> bool:
    target = Path(build_dir) if build_dir is not None else TODAY_REACT_BUILD_DIR
    return (target / "index.html").exists()

def render_today_workbench(payload: dict[str, Any], *, key: str = "today_workbench") -> dict[str, Any] | None:
    component = _declare_today_component()
    if component is None:
        return None
    value = component(payload=payload, key=key, default={"event": None})
    return value if isinstance(value, dict) else None
```

- [x] **Step 4: Write failing React-primary and event-routing tests**

Test these behaviors separately:

1. available component: `render_today_workbench(model)` called and fallback `st.markdown` not called.
2. unavailable component: compact fallback called and `st.error`/caption explain React build absence.
3. `open_market_research`: `st.switch_page(target, query_params={OVERVIEW_DEEP_TAB_QUERY_PARAM: "market-context"})`.
4. `open_stock_research`: same with `market-movers`.
5. `open_portfolio_monitoring`: switch with no query params.
6. unknown event: warning, no navigation.

Normalize only these IDs:

```python
TODAY_EVENT_IDS = {
    "open_market_research",
    "open_stock_research",
    "open_portfolio_monitoring",
}
```

- [x] **Step 5: Run integration tests and verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_today_home.py -k 'react_primary or routes_react_event or unknown_today_event' -q
```

Expected: FAIL because V1 always calls `st.markdown` and page links.

- [x] **Step 6: Implement React-primary rendering and route adapter**

`render_today_page` must load once, render React when build is available, normalize the returned event, and call `st.switch_page` using configured Page targets. Keep `build_today_html` only in `_render_today_fallback(model)`. Do not render both React and fallback in one successful request.

Use an exact route table:

```python
_TODAY_EVENT_ROUTES = {
    "open_market_research": ("market_research", {OVERVIEW_DEEP_TAB_QUERY_PARAM: "market-context"}),
    "open_stock_research": ("stock_research", {OVERVIEW_DEEP_TAB_QUERY_PARAM: "market-movers"}),
    "open_portfolio_monitoring": ("portfolio_monitoring", None),
}
```

- [x] **Step 7: Verify integration and commit**

Run:

```bash
.venv/bin/python -m pytest tests/test_today_home.py -q
.venv/bin/python -m pytest tests/test_institutional_portfolios.py tests/test_reference_center.py tests/test_reference_contextual_help.py tests/test_portfolio_monitoring_page.py tests/test_portfolio_monitoring_read_model.py -q
.venv/bin/python -m py_compile app/web/today_react_component.py app/web/today_page.py app/services/today.py
git diff --check
```

Expected: all tests PASS, compile exits 0, diff check silent.

Commit:

```bash
git add app/web/today_react_component.py app/web/today_page.py tests/test_today_home.py
git commit -m "개선: Today React 기본 렌더러와 이동 연결"
```

---

### Task 5: Browser QA, Durable Docs, And Final Review

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/today-home-react-workbench-v2-20260722/{PLAN,STATUS,NOTES,RUNS,RISKS}.md`
- Modify as required by `finance-doc-sync`: `.aiworkspace/note/finance/docs/INDEX.md`, `ROADMAP.md`, `PROJECT_MAP.md`, relevant architecture/flow docs, root handoff logs.
- Generated but do not stage: `today-home-react-workbench-v2-browser-qa.png`.

**Interfaces:**
- Consumes: completed production implementation.
- Produces: actual-browser evidence, aligned docs, final coherent commit/review handoff.

- [x] **Step 1: Run the full focused automated verification**

```bash
.venv/bin/python -m pytest tests/test_today_home.py tests/test_institutional_portfolios.py tests/test_reference_center.py tests/test_reference_contextual_help.py tests/test_portfolio_monitoring_page.py tests/test_portfolio_monitoring_read_model.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py::SelectedPortfolioMonitoringTimelineContractTests::test_portfolio_navigation_contains_lab_and_monitoring_only -q
.venv/bin/python -m py_compile app/services/today.py app/web/today_react_component.py app/web/today_page.py app/web/final_selected_portfolio_dashboard.py app/web/streamlit_app.py
cd app/web/streamlit_components/today_workbench && npm test -- --reporter=verbose && npm run typecheck && npm run build
git diff --check
```

Expected: zero failures, zero type/build errors, silent diff check.

- [x] **Step 2: Perform actual Browser QA**

Start the Streamlit app using the repository's existing app command and verify root `/` at 1280px, 760px, and 420px:

- React component iframe/workbench is visible as the primary renderer.
- hero/evidence/events/portfolio/actions retain approved order.
- evidence cards have no left status line and show text labels plus colors.
- computed font sizes match fixed tokens.
- chart header states daily/stored close/latest observation/intraday false.
- X date ticks and Y percent ticks are readable without overlap.
- hover/focus tooltip shows exact date, cumulative return, and total value.
- latest-observation return shows exact from/to dates.
- all three action routes work.
- horizontal overflow is zero and console has no errors.

Capture one full-page screenshot named `today-home-react-workbench-v2-browser-qa.png`; keep it untracked.

- [x] **Step 3: Review implementation against the written spec**

Compare every section of `DESIGN.md` with the diff. Reject the closeout if React is not primary, if chart metadata is missing, if UI infers risk labels, or if any render path writes/fetches. Record exact evidence and any gaps in task `RUNS.md`/`RISKS.md`.

- [x] **Step 4: Invoke `finance-doc-sync` and update durable docs**

Update long-lived docs only with verified final behavior: Today is a React workbench, evidence labels are Python-owned projections, and the portfolio chart is daily stored-close cumulative return. Keep detailed commands/screenshots in task docs, not root logs.

- [x] **Step 5: Final staging safety check and coherent commit**

Stage only intended code, static build, tests, and docs. Before commit:

```bash
git diff --cached --name-status
git diff --cached --check
git diff --cached --name-only | rg '(^|/)(registries|saved|run_history)/|\.png$|^\.superpowers/' && exit 1 || true
```

Commit:

```bash
git commit -m "개선: Today React 시장 판단 워크벤치 완성"
```

- [x] **Step 6: Apply verification-before-completion**

Run fresh tests/build/diff checks after the final content change, inspect `git show --stat HEAD`, and report actual counts, Browser QA viewports, screenshot path, final roadmap `4/4`, remaining risks, and commit hashes without claiming unrun verification.
