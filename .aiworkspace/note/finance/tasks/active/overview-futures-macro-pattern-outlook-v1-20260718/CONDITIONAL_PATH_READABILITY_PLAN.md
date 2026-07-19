# Futures Macro Conditional Path Readability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. This session does not delegate to subagents.

**Goal:** 경험적 5D / 20D 계산은 유지하면서 겹치는 세 uncertainty box와 endpoint arrow를, 선택 horizon 말일의 단일 음영 박스와 고정 크기 mid-line direction marker로 교체한다.

**Architecture:** `PatternMapSection.tsx`만 기존 `conditional_path.points`를 선택 horizon에 맞게 해석하며 서비스·payload 계산은 바꾸지 않는다. terminal point 하나가 예상 위치와 도착 범위를 소유하고, 화면 좌표 helper가 관측·예상 선의 endpoint에서 떨어진 direction segment를 계산한다. CSS는 기존 Market Context형 4분면 색상을 유지하고 단일 range를 가장 뒤 레이어에 낮은 opacity로 렌더링한다.

**Tech Stack:** React 18, TypeScript 5.7, inline SVG, CSS, Vite 6, Python `unittest`, Streamlit component bridge.

## Global Constraints

- `app/services/futures_macro_pattern_validation.py`와 `app/web/overview/futures_macro_helpers.py`의 통계·payload 계약을 변경하지 않는다.
- 5D는 step 5, 20D는 step 20 terminal bounds 하나만 렌더링한다.
- current radius는 `10`, terminal radius는 `8`, direction marker는 `markerUnits="userSpaceOnUse"`의 고정 `9` units다.
- arrow는 endpoint circle 위가 아니라 선 중간의 별도 direction segment에 둔다.
- terminal copy는 `5일 후 예상 위치` / `20일 후 예상 위치`다.
- legend는 `관측 이동`, `1~5일 예상 이동` / `1~20일 예상 이동`, `5일 후 도착 범위` / `20일 후 도착 범위`다.
- detailed episode count와 q25~q75 계산은 그래프 label에 추가하지 않는다.
- probability rows, episode count, `PROVISIONAL` / `VERIFIED` / `UNAVAILABLE`, actual-future caveat는 우측 reading에 유지한다.
- `UNAVAILABLE`이면 conditional line, direction arrow, terminal, range를 모두 숨긴다.
- fixed categorical targets, price target, trade signal, DB/provider/schema 변경을 추가하지 않는다.
- unrelated untracked research와 `.superpowers/`는 수정하거나 stage하지 않는다.

## File Structure

- `tests/test_service_contracts.py`: terminal-only range, readable copy, fixed direction marker source contracts.
- `app/web/streamlit_components/futures_macro_workbench/src/PatternMapSection.tsx`: selected terminal range, dynamic labels, screen-space direction segments, separated current/terminal labels.
- `app/web/streamlit_components/futures_macro_workbench/src/style.css`: single shaded range and compact direction/point styling.
- `app/web/streamlit_components/futures_macro_workbench/component_static/`: Vite production bundle.
- Active task docs plus smallest durable Futures Macro flow/project-map/root handoff set: actual QA and semantic closeout.

---

### Task 1: Terminal-Only Range And Readable Forecast Copy

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/PatternMapSection.tsx`

**Interfaces:**
- Consumes: selected `HorizonCard.conditional_path.points` and its terminal point.
- Produces: one `.fm-pattern-map__uncertainty` rect with the terminal step, dynamic expected-position/route/range labels.

- [x] **Step 1: Write the terminal-range RED contract**

Add a focused contract beside the existing Futures Macro pattern-map contract:

```python
def test_futures_macro_pattern_map_uses_one_terminal_range_and_readable_copy(self) -> None:
    pattern_map = Path(
        "app/web/streamlit_components/futures_macro_workbench/src/PatternMapSection.tsx"
    ).read_text(encoding="utf-8")

    self.assertIn("const uncertaintyStep = forecastPoints.at(-1)", pattern_map)
    self.assertNotIn("midpointStep", pattern_map)
    self.assertNotIn("uncertaintySteps", pattern_map)
    self.assertEqual(pattern_map.count('className="fm-pattern-map__uncertainty"'), 1)
    self.assertIn("data-forecast-step={uncertaintyStep.step}", pattern_map)
    self.assertIn("일 후 예상 위치", pattern_map)
    self.assertIn("일 예상 이동", pattern_map)
    self.assertIn("일 후 도착 범위", pattern_map)
    self.assertNotIn("유사 패턴 중앙 위치", pattern_map)
    self.assertIn("실제 미래 경로를 보장하지 않습니다", pattern_map)
```

Update the older pattern-map contract to expect `일 후 예상 위치` instead of `유사 패턴 중앙 위치`.

- [x] **Step 2: Run the terminal-range RED test**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_uses_one_terminal_range_and_readable_copy -v
```

Expected: FAIL because the source still selects `1 / midpoint / terminal`, renders through `uncertaintySteps.map`, and uses `유사 패턴 중앙 위치`.

- [x] **Step 3: Replace three range checkpoints with the terminal point**

In `PatternMapSection.tsx`, replace midpoint/checkpoint selection with:

```typescript
const uncertaintyStep = forecastPoints.at(-1);
const selectedDays = selectedHorizon === "observed"
  ? undefined
  : Number.parseInt(selectedHorizon, 10);
const expectedPositionLabel = selectedDays ? `${selectedDays}일 후 예상 위치` : "";
const forecastLegend = selectedDays ? `1~${selectedDays}일 예상 이동` : "예상 이동";
const rangeLegend = selectedDays ? `${selectedDays}일 후 도착 범위` : "도착 범위";
```

Render exactly one range before the path layers:

```tsx
{showForecast && uncertaintyStep ? (
  <rect
    className="fm-pattern-map__uncertainty"
    data-forecast-step={uncertaintyStep.step}
    x={sx(uncertaintyStep.lower_x)}
    y={sy(uncertaintyStep.upper_y)}
    width={Math.max(2, sx(uncertaintyStep.upper_x) - sx(uncertaintyStep.lower_x))}
    height={Math.max(2, sy(uncertaintyStep.lower_y) - sy(uncertaintyStep.upper_y))}
    rx="10"
  >
    <title>{selectedDays}일 후 · {conditionalPath?.band_label}</title>
  </rect>
) : null}
```

Change terminal and legend copy:

```tsx
<text
  className="fm-pattern-map__terminal-label"
  x={sx(conditionalPath.terminal.x)}
  y={sy(conditionalPath.terminal.y) - 14}
  textAnchor="middle"
>
  {expectedPositionLabel}
</text>

<span className="observed">관측 이동</span>
<span className="forecast">{forecastLegend}</span>
<span className="uncertainty">{rangeLegend}</span>
```

Change the right reading caveat to:

```tsx
<p>
  {conditionalPath?.episode_count ? `독립 표본 ${conditionalPath.episode_count}개 · ` : ""}
  점선은 과거 유사 흐름 기반 예상 이동이며 실제 미래 경로를 보장하지 않습니다.
</p>
```

- [x] **Step 4: Run terminal-range GREEN and core map regression**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_uses_one_terminal_range_and_readable_copy \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_uses_observed_anchors_and_conditional_branches -v
```

Expected: 2 tests pass. `git diff --check` exits 0.

- [x] **Step 5: Commit the terminal-only range unit**

```bash
git add tests/test_service_contracts.py \
  app/web/streamlit_components/futures_macro_workbench/src/PatternMapSection.tsx
git commit -m "선물 매크로 말일 예상 범위 단순화"
```

---

### Task 2: Fixed Mid-Line Direction Markers And Label Geometry

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/PatternMapSection.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/style.css`
- Rebuild: `app/web/streamlit_components/futures_macro_workbench/component_static/`

**Interfaces:**
- Consumes: observed anchor screen coordinates, current screen coordinate, terminal screen coordinate.
- Produces: `directionSegment(start, end, options) -> ScreenSegment | undefined`, one observed and one forecast mid-line arrow, separated labels.

- [x] **Step 1: Write the fixed-marker RED contract**

Add:

```python
def test_futures_macro_pattern_map_uses_fixed_midline_direction_markers(self) -> None:
    source_root = Path("app/web/streamlit_components/futures_macro_workbench/src")
    pattern_map = (source_root / "PatternMapSection.tsx").read_text(encoding="utf-8")
    style = (source_root / "style.css").read_text(encoding="utf-8")

    self.assertIn("function directionSegment", pattern_map)
    self.assertGreaterEqual(pattern_map.count('markerUnits="userSpaceOnUse"'), 2)
    self.assertGreaterEqual(pattern_map.count('markerWidth="9"'), 2)
    self.assertIn('data-direction="observed"', pattern_map)
    self.assertIn('data-direction="forecast"', pattern_map)
    self.assertNotIn('markerEnd="url(#fm-observed-arrow)"', pattern_map)
    self.assertIn('r={point.anchorLabel === "현재" ? 10 : 7.5}', pattern_map)
    self.assertIn('r="8"', pattern_map)
    self.assertIn("fm-pattern-map__leader", pattern_map)
    self.assertIn("fm-pattern-map__direction", style)
```

- [x] **Step 2: Run the fixed-marker RED test**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_uses_fixed_midline_direction_markers -v
```

Expected: FAIL because the observed arrow remains an endpoint marker and no screen-space segment helper exists.

- [x] **Step 3: Add the screen-space direction helper**

Add near the component helpers:

```typescript
type ScreenPoint = { x: number; y: number };
type ScreenSegment = { x1: number; y1: number; x2: number; y2: number };

function directionSegment(
  start: ScreenPoint | undefined,
  end: ScreenPoint | undefined,
  { startInset, endInset, length }: { startInset: number; endInset: number; length: number },
): ScreenSegment | undefined {
  if (!start || !end) return undefined;
  const dx = end.x - start.x;
  const dy = end.y - start.y;
  const distance = Math.hypot(dx, dy);
  const available = distance - startInset - endInset;
  if (!Number.isFinite(distance) || distance <= 0 || available <= 4) return undefined;
  const unitX = dx / distance;
  const unitY = dy / distance;
  const segmentLength = Math.min(length, available);
  const centerDistance = startInset + available * 0.55;
  const firstDistance = centerDistance - segmentLength / 2;
  const secondDistance = centerDistance + segmentLength / 2;
  return {
    x1: start.x + unitX * firstDistance,
    y1: start.y + unitY * firstDistance,
    x2: start.x + unitX * secondDistance,
    y2: start.y + unitY * secondDistance,
  };
}
```

Build direction inputs inside the component:

```typescript
const screenPoint = (point: { x: number; y: number } | undefined): ScreenPoint | undefined => (
  point ? { x: sx(point.x), y: sy(point.y) } : undefined
);
const terminal = conditionalPath?.terminal || undefined;
const observedDirection = directionSegment(
  screenPoint(anchors.at(-2)),
  screenPoint(latest),
  { startInset: 10, endInset: 14, length: 18 },
);
const forecastDirection = directionSegment(
  screenPoint(latest),
  screenPoint(terminal),
  { startInset: 13, endInset: 11, length: 12 },
);
```

- [x] **Step 4: Replace endpoint arrow and render fixed markers**

Replace `<defs>` with two fixed markers:

```tsx
<marker id="fm-observed-direction-arrow" markerUnits="userSpaceOnUse" viewBox="0 0 9 9" refX="8" refY="4.5" markerWidth="9" markerHeight="9" orient="auto">
  <path d="M 0 0 L 9 4.5 L 0 9 z" />
</marker>
<marker id="fm-forecast-direction-arrow" markerUnits="userSpaceOnUse" viewBox="0 0 9 9" refX="8" refY="4.5" markerWidth="9" markerHeight="9" orient="auto">
  <path d="M 0 0 L 9 4.5 L 0 9 z" />
</marker>
```

Remove `markerEnd` from the observed polyline and render direction segments after both polylines but before circles:

```tsx
{observedDirection ? (
  <line
    className="fm-pattern-map__direction is-observed"
    data-direction="observed"
    {...observedDirection}
    markerEnd="url(#fm-observed-direction-arrow)"
  />
) : null}
{showForecast && forecastDirection ? (
  <line
    className="fm-pattern-map__direction is-forecast"
    data-direction="forecast"
    {...forecastDirection}
    markerEnd="url(#fm-forecast-direction-arrow)"
  />
) : null}
```

- [x] **Step 5: Separate current and terminal labels**

Use `r={point.anchorLabel === "현재" ? 10 : 7.5}`. For the current anchor render a down-left leader and the short `현재` label; keep dates/regime in `<title>`:

```tsx
{point.anchorLabel === "현재" ? (
  <>
    <line className="fm-pattern-map__leader" x1={sx(point.x) - 7} y1={sy(point.y) + 7} x2={sx(point.x) - 35} y2={sy(point.y) + 30} />
    <text x={sx(point.x) - 40} y={sy(point.y) + 36} textAnchor="end">현재</text>
  </>
) : (
  <text x={sx(point.x)} y={sy(point.y) - 14} textAnchor="middle">{point.anchorLabel}</text>
)}
```

For the terminal render `r="8"`, an up-right leader, and `expectedPositionLabel`:

```tsx
<line className="fm-pattern-map__leader" x1={sx(terminal.x) + 6} y1={sy(terminal.y) - 6} x2={sx(terminal.x) + 40} y2={sy(terminal.y) - 36} />
<text className="fm-pattern-map__terminal-label" x={sx(terminal.x) + 46} y={sy(terminal.y) - 40} textAnchor="start">
  {expectedPositionLabel}
</text>
```

- [x] **Step 6: Apply the approved CSS**

Replace the active path styles with:

```css
.fm-pattern-map__observed { fill: none; stroke: #264f68; stroke-linecap: round; stroke-linejoin: round; stroke-width: 3.4; }
#fm-observed-direction-arrow path { fill: #264f68; }
#fm-forecast-direction-arrow path { fill: #397da8; }
.fm-pattern-map__direction { fill: none; stroke-width: 2.5; }
.fm-pattern-map__direction.is-observed { stroke: #264f68; }
.fm-pattern-map__direction.is-forecast { stroke: #397da8; }
.fm-pattern-map__anchor circle { fill: #fff; stroke: #264f68; stroke-width: 2.6; }
.fm-pattern-map__anchor.is-current circle { fill: #264f68; stroke: #fff; stroke-width: 3; }
.fm-pattern-map__uncertainty { fill: rgba(111, 167, 202, 0.1); stroke: rgba(57, 125, 168, 0.62); stroke-dasharray: 5 5; stroke-width: 1.6; }
.fm-pattern-map__conditional-path { fill: none; stroke: #397da8; stroke-dasharray: 7 7; stroke-linecap: round; stroke-linejoin: round; stroke-width: 3.2; }
.fm-pattern-map__terminal circle { fill: #e5f0f6; stroke: #397da8; stroke-width: 2.6; }
.fm-pattern-map__leader { stroke: #718397; stroke-width: 1.2; }
.fm-pattern-map__terminal-label { fill: #397da8; font-size: 12px; font-weight: 800; paint-order: stroke; stroke: #fff; stroke-width: 4px; }
```

- [x] **Step 7: Run GREEN, build, and commit**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_uses_one_terminal_range_and_readable_copy \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_uses_fixed_midline_direction_markers \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_uses_observed_anchors_and_conditional_branches -v
npm --prefix app/web/streamlit_components/futures_macro_workbench run build
git diff --check
git add tests/test_service_contracts.py \
  app/web/streamlit_components/futures_macro_workbench/src \
  app/web/streamlit_components/futures_macro_workbench/component_static
git commit -m "선물 매크로 예상 경로 방향 표시 개선"
```

Expected: three selected contracts pass, Vite exits 0, and the static bundle contains the new copy/styles.

---

### Task 3: Actual Browser QA, Documentation Sync, And Closeout

**Files:**
- Modify: active task `STATUS.md`, `RUNS.md`, `NOTES.md`, `RISKS.md`, this plan.
- Modify: `.aiworkspace/note/finance/docs/flows/README.md`.
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`.
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`.
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md` when the approved interpretation needs durable handoff.

**Interfaces:**
- Consumes: built component and actual stored futures snapshot.
- Produces: verified 5D / 20D/observed DOM counts, responsive screenshot, durable semantic record.

- [x] **Step 1: Run complete focused verification**

```bash
.venv/bin/python -m unittest tests.test_futures_macro_pattern tests.test_futures_macro_pattern_validation
.venv/bin/python -m unittest tests.test_service_contracts.FuturesMacroThermometerContractTests
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_react_v2_renders_market_context_reading_order \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_react_v2_has_responsive_probability_and_unavailable_contract \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_uses_observed_anchors_and_conditional_branches \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_uses_one_terminal_range_and_readable_copy \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_uses_fixed_midline_direction_markers \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_react_copy_avoids_trade_and_causal_claims
npm --prefix app/web/streamlit_components/futures_macro_workbench run build
.venv/bin/python -m py_compile app/web/overview/futures_macro_helpers.py
git diff --check
```

Expected: all selected Futures Macro contracts pass. Record the known unrelated Sentiment source-string failure only if the full Overview class is run and still fails.

- [x] **Step 2: Start actual app and perform Browser QA**

Start:

```bash
.venv/bin/python -m streamlit run app/web/streamlit_app.py \
  --server.port 8512 \
  --server.headless true \
  --server.runOnSave false \
  --server.fileWatcherType none
```

At desktop verify:

- `관측만`: uncertainty rect 0, conditional path 0, forecast direction 0, terminal 0.
- `다음 5D`: uncertainty rect 1 with `data-forecast-step="5"`, conditional path 1, forecast direction 1, terminal 1, `5일 후 예상 위치` visible.
- `다음 20D`: uncertainty rect 1 with `data-forecast-step="20"`, conditional path 1, forecast direction 1, terminal 1, `20일 후 예상 위치` visible.
- observed direction remains 1 in every state.
- current/terminal/arrow bounding boxes do not overlap materially; labels do not cover either circle.
- right probability values and `PROVISIONAL` state remain unchanged.

At 420px verify root `clientWidth == scrollWidth`, controls wrap, and graph labels are not clipped. Confirm console errors 0.

Save one unstaged screenshot under:

```text
/Users/taeho/.codex/visualizations/2026/07/18/019f730e-7ff9-7720-b5c6-359d96ca1a4d/futures-macro-single-range-qa.png
```

- [x] **Step 3: Synchronize durable docs**

Use `finance-doc-sync` and update only stale statements:

- flow: replace `1일·중간·말일 가운데 50% 범위` with one selected-horizon terminal arrival range.
- project map: replace `three sparse middle-50% ranges` with one terminal range.
- task docs: record marker geometry, actual DOM counts, screenshot, and any remaining statistical caveat.
- root logs: 3~5 lines describing the approved user interpretation and completion.

- [x] **Step 4: Re-run fresh verification and commit closeout**

```bash
.venv/bin/python -m unittest tests.test_futures_macro_pattern tests.test_futures_macro_pattern_validation
.venv/bin/python -m unittest tests.test_service_contracts.FuturesMacroThermometerContractTests
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_uses_observed_anchors_and_conditional_branches \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_uses_one_terminal_range_and_readable_copy \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_uses_fixed_midline_direction_markers
npm --prefix app/web/streamlit_components/futures_macro_workbench run build
.venv/bin/python -m py_compile app/web/overview/futures_macro_helpers.py
git diff --check
git status --short
git add .aiworkspace/note/finance/docs/flows/README.md \
  .aiworkspace/note/finance/docs/PROJECT_MAP.md \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md \
  .aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718
git commit -m "선물 매크로 예상 경로 가독성 검증과 문서 정리"
```

Expected: verification passes before commit; screenshot and unrelated untracked paths remain unstaged.

## Completion Checklist

- [x] Task 1: terminal-only range and readable forecast copy.
- [x] Task 2: fixed mid-line direction markers and label geometry.
- [x] Task 3: actual Browser QA, docs sync, and closeout.

## Roadmap State

- 1차 overlap root-cause analysis: complete.
- 2차 visual alternatives and A안 selection: complete.
- 3차 written design: complete (`43fd5cd9`).
- 4차 TDD implementation: complete (`ef6d1973`, `3ed91a05`).
- 5차 actual QA / docs closeout: complete.
