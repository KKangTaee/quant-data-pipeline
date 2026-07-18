# Futures Macro Net Direction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. This session executes inline and does not delegate to subagents.

**Goal:** 조건부 점선을 날짜별 중앙값의 지그재그 연결이 아니라 `현재 → 선택 horizon 말일 중앙 위치`의 한 방향 예상 순이동으로 표시한다.

**Architecture:** 서비스와 payload의 stepwise 통계는 보존하고 React의 SVG 표현만 terminal 중심으로 바꾼다. 공통 chart bound도 실제로 보이는 세 관측 anchor와 두 horizon terminal/range만 사용해 숨겨진 중간 median이 배율을 바꾸지 않게 한다.

**Tech Stack:** React 18, TypeScript 5.7, inline SVG, Vite 6, Python `unittest`, Streamlit component bridge.

## Global Constraints

- 조건부 점선은 현재점과 selected terminal만 직접 연결한다.
- 중간 `forecastPoints.map`으로 SVG 경로를 만들지 않는다.
- legend는 `5일 예상 순이동` / `20일 예상 순이동`이다.
- 우측 설명은 중간 일별 경로가 아님을 명시한다.
- terminal circle, 고정 9-unit 방향 marker, 말일 q25~q75 음영 range는 유지한다.
- `관측만 / 5D / 20D`의 세 관측 anchor SVG 좌표는 동일해야 한다.
- 공통 scale은 anchors와 두 horizon terminal/range만 포함한다.
- probability, episode, validation, service, payload, DB/provider/schema를 변경하지 않는다.
- unrelated research path와 `.superpowers/`는 수정하거나 stage하지 않는다.

---

### Task 1: Terminal-Only Net Direction

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/PatternMapSection.tsx`
- Rebuild: `app/web/streamlit_components/futures_macro_workbench/component_static/`

**Interfaces:**
- Consumes: `latest: AnchorPoint | undefined`, selected `conditionalPath.terminal`, and the final `conditionalPath.points` row for the range bounds.
- Produces: one `<line className="fm-pattern-map__conditional-path">` from current to terminal, terminal-only common scale, net-direction copy.

- [ ] **Step 1: Write the failing source contract**

Add next to the existing Pattern Map contracts:

```python
def test_futures_macro_pattern_map_renders_terminal_net_direction_without_stepwise_zigzag(self) -> None:
    pattern_map = Path(
        "app/web/streamlit_components/futures_macro_workbench/src/PatternMapSection.tsx"
    ).read_text(encoding="utf-8")

    self.assertIn('className="fm-pattern-map__conditional-path"', pattern_map)
    self.assertIn("x1={sx(latest.x)}", pattern_map)
    self.assertIn("y1={sy(latest.y)}", pattern_map)
    self.assertIn("x2={sx(terminal.x)}", pattern_map)
    self.assertIn("y2={sy(terminal.y)}", pattern_map)
    self.assertNotIn("const forecastPolyline", pattern_map)
    self.assertNotIn("...forecastPoints.map((point) => `${sx(point.x)},${sy(point.y)}`)", pattern_map)
    self.assertNotIn("const scaleForecastPoints", pattern_map)
    self.assertNotIn("...scaleForecastPoints.map", pattern_map)
    self.assertIn("일 예상 순이동", pattern_map)
    self.assertIn("중간 일별 경로가 아닙니다", pattern_map)
```

Update `test_futures_macro_pattern_map_keeps_observed_anchors_on_one_shared_scale` so it requires terminal-only scale inputs:

```python
self.assertNotIn("const scaleForecastPoints", pattern_map)
self.assertIn(
    "...scaleTerminalPoints.flatMap((point) => [point.x, point.lower_x, point.upper_x])",
    pattern_map,
)
self.assertIn(
    "...scaleTerminalPoints.flatMap((point) => [point.y, point.lower_y, point.upper_y])",
    pattern_map,
)
```

- [ ] **Step 2: Run RED**

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_renders_terminal_net_direction_without_stepwise_zigzag -v
```

Expected: FAIL because the component still builds `forecastPolyline` from every step and uses `scaleForecastPoints`.

- [ ] **Step 3: Implement the minimal terminal-only renderer**

Remove `scaleForecastPoints` and every scale input that maps it. Keep `scaleTerminalPoints` and build the bounds as:

```typescript
const xValues = [
  ...anchors.map((point) => point.x),
  ...scaleTerminalPoints.flatMap((point) => [point.x, point.lower_x, point.upper_x]),
];
const yValues = [
  ...anchors.map((point) => point.y),
  ...scaleTerminalPoints.flatMap((point) => [point.y, point.lower_y, point.upper_y]),
];
```

Remove `forecastPolyline`. Change the legend to:

```typescript
const forecastLegend = selectedDays ? `${selectedDays}일 예상 순이동` : "예상 순이동";
```

Replace the forecast polyline with:

```tsx
{showForecast && latest && terminal ? (
  <line
    className="fm-pattern-map__conditional-path"
    data-forecast-horizon={selectedHorizon}
    x1={sx(latest.x)}
    y1={sy(latest.y)}
    x2={sx(terminal.x)}
    y2={sy(terminal.y)}
  />
) : null}
```

Change the right-side explanation to:

```tsx
<p>{conditionalPath?.episode_count ? `독립 표본 ${conditionalPath.episode_count}개 · ` : ""}점선은 과거 유사 흐름의 시작점에서 말일 중앙 위치까지의 예상 순이동이며, 중간 일별 경로가 아닙니다.</p>
```

- [ ] **Step 4: Run GREEN and focused regressions**

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_renders_terminal_net_direction_without_stepwise_zigzag \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_uses_observed_anchors_and_conditional_branches \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_uses_one_terminal_range_and_readable_copy \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_uses_fixed_midline_direction_markers \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_keeps_observed_anchors_on_one_shared_scale -v
npm --prefix app/web/streamlit_components/futures_macro_workbench run build
git diff --check
```

Expected: 5 contracts pass, Vite exits 0, production bundle is rebuilt.

- [ ] **Step 5: Commit the implementation unit**

```bash
git add tests/test_service_contracts.py \
  app/web/streamlit_components/futures_macro_workbench/src/PatternMapSection.tsx \
  app/web/streamlit_components/futures_macro_workbench/component_static
git commit -m "선물 매크로 예상 경로를 순이동으로 단순화"
```

---

### Task 2: Actual Browser QA And Documentation Closeout

**Files:**
- Modify: active task `STATUS.md`, `RUNS.md`, `NOTES.md`, `RISKS.md`, this plan.
- Modify: `.aiworkspace/note/finance/docs/flows/README.md`.
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md` only if its path description is stale.
- Modify: root handoff logs with one concise user-facing decision/milestone.

**Interfaces:**
- Consumes: built React bundle and actual stored futures snapshot.
- Produces: exact current-to-terminal SVG equality, stable observed anchors, responsive evidence, one unstaged screenshot.

- [ ] **Step 1: Run actual Browser QA**

Run the app on port `8512` and verify:

```text
5D conditional line count == 1
20D conditional line count == 1
forecast line start == current anchor center
forecast line end == selected terminal center
5D uncertainty step == 5
20D uncertainty step == 20
observed anchors == 5D anchors == 20D anchors
observed forecast layers == 0
420px clientWidth == scrollWidth
console errors == 0
```

Save an unstaged screenshot to:

```text
/Users/taeho/.codex/visualizations/2026/07/18/019f730e-7ff9-7720-b5c6-359d96ca1a4d/futures-macro-net-direction-qa.png
```

- [ ] **Step 2: Synchronize the smallest durable docs**

Record that the dashed line is terminal net movement rather than a connected daily median route. Preserve detailed coordinates and commands in task docs; keep root logs to 3~5 lines.

- [ ] **Step 3: Run fresh closeout verification**

```bash
.venv/bin/python -m unittest tests.test_futures_macro_pattern tests.test_futures_macro_pattern_validation
.venv/bin/python -m unittest tests.test_service_contracts.FuturesMacroThermometerContractTests
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_renders_terminal_net_direction_without_stepwise_zigzag \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_uses_observed_anchors_and_conditional_branches \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_uses_one_terminal_range_and_readable_copy \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_uses_fixed_midline_direction_markers \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_keeps_observed_anchors_on_one_shared_scale
npm --prefix app/web/streamlit_components/futures_macro_workbench run build
.venv/bin/python -m py_compile app/web/overview/futures_macro_helpers.py
test -s /Users/taeho/.codex/visualizations/2026/07/18/019f730e-7ff9-7720-b5c6-359d96ca1a4d/futures-macro-net-direction-qa.png
git diff --check
git status --short
```

- [ ] **Step 4: Commit docs and closeout**

Stage only the active task and smallest durable docs, then commit:

```bash
git commit -m "선물 매크로 예상 순이동 QA와 문서 정리"
```

## Completion Checklist

- [ ] Task 1: terminal-only expected net direction implemented with RED/GREEN evidence.
- [ ] Task 2: actual SVG endpoint QA, stable-anchor QA, responsive QA, docs, and closeout complete.

## Roadmap State

- 1차 net-direction design: complete (`e3ca4d25`).
- 2차 terminal-only TDD implementation: pending.
- 3차 actual Browser QA / docs closeout: pending.
