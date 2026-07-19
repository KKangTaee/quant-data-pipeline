# Futures Macro Stable Coordinate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. This session executes inline and does not delegate to subagents.

**Goal:** `관측만 / 다음 5D / 다음 20D` 전환에서 세 관측 anchor의 SVG 좌표를 고정하고 선택 horizon의 예측 경로·말일 도착점·도착 범위만 변경한다.

**Architecture:** `PatternMapSection.tsx`가 selected card와 별개로 사용 가능한 5D / 20D conditional path를 모두 수집해 하나의 scale input을 만든다. 공통 bound는 두 median path와 실제로 보이는 두 terminal q25~q75 range만 포함하며, 제거된 중간 step q25~q75는 제외한다. 서비스·payload·확률 계산은 변경하지 않는다.

**Tech Stack:** React 18, TypeScript 5.7, inline SVG, Vite 6, Python `unittest`, Streamlit component bridge.

## Global Constraints

- `20D 전 / 5D 전 / 현재`의 `cx / cy`는 세 horizon state에서 완전히 동일해야 한다.
- 두 horizon의 step별 median path와 말일 terminal range가 공통 bound에 포함되어야 한다.
- 숨겨진 중간 step q25/q75는 공통 bound에 포함하지 않는다.
- selected horizon은 forecast polyline, terminal, terminal range, legend, 우측 확률만 변경한다.
- `UNAVAILABLE` conditional path는 공통 bound와 forecast layer에서 제외한다.
- probability, episode, validation, service, payload, DB/provider/schema를 변경하지 않는다.
- unrelated research path와 `.superpowers/`는 수정하거나 stage하지 않는다.

---

### Task 1: Shared Visible-Data Scale

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/PatternMapSection.tsx`
- Rebuild: `app/web/streamlit_components/futures_macro_workbench/component_static/`

**Interfaces:**
- Consumes: `horizons: HorizonCard[]`, `conditional_path.points`, `conditional_path.terminal`.
- Produces: `scalePaths`, `scaleForecastPoints`, `scaleTerminalPoints`, and selected-horizon-independent `xBound / yBound`.

- [x] **Step 1: Write the shared-scale RED contract**

Add beside the current Pattern Map contracts:

```python
def test_futures_macro_pattern_map_keeps_observed_anchors_on_one_shared_scale(self) -> None:
    pattern_map = Path(
        "app/web/streamlit_components/futures_macro_workbench/src/PatternMapSection.tsx"
    ).read_text(encoding="utf-8")

    self.assertIn("const scalePaths = horizons.flatMap", pattern_map)
    self.assertIn("const scaleForecastPoints = scalePaths.flatMap", pattern_map)
    self.assertIn("const scaleTerminalPoints = scalePaths.flatMap", pattern_map)
    self.assertIn("...scaleForecastPoints.map((point) => point.x)", pattern_map)
    self.assertIn("...scaleTerminalPoints.flatMap((point) => [point.lower_x, point.upper_x])", pattern_map)
    self.assertIn("...scaleForecastPoints.map((point) => point.y)", pattern_map)
    self.assertIn("...scaleTerminalPoints.flatMap((point) => [point.lower_y, point.upper_y])", pattern_map)
    self.assertNotIn(
        "...forecastPoints.flatMap((point) => [point.x, point.lower_x, point.upper_x])",
        pattern_map,
    )
```

- [x] **Step 2: Run RED**

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_keeps_observed_anchors_on_one_shared_scale -v
```

Expected: FAIL because selected `forecastPoints` still owns the bound.

- [x] **Step 3: Implement the shared visible-data scale**

Immediately after selected `forecastPoints`, add:

```typescript
const scalePaths = horizons.flatMap((item) => (
  item.kind === "conditional_outlook"
    && item.conditional_path
    && item.conditional_path.status !== "UNAVAILABLE"
    ? [item.conditional_path]
    : []
));
const scaleForecastPoints = scalePaths.flatMap((path) => path.points || []);
const scaleTerminalPoints = scalePaths.flatMap((path) => (
  path.terminal ? [path.terminal] : []
));
```

Replace selected-horizon scale inputs with:

```typescript
const xValues = [
  ...anchors.map((point) => point.x),
  ...scaleForecastPoints.map((point) => point.x),
  ...scaleTerminalPoints.flatMap((point) => [point.lower_x, point.upper_x]),
];
const yValues = [
  ...anchors.map((point) => point.y),
  ...scaleForecastPoints.map((point) => point.y),
  ...scaleTerminalPoints.flatMap((point) => [point.lower_y, point.upper_y]),
];
```

- [x] **Step 4: Run GREEN and focused regressions**

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_keeps_observed_anchors_on_one_shared_scale \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_uses_observed_anchors_and_conditional_branches \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_uses_one_terminal_range_and_readable_copy \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_uses_fixed_midline_direction_markers -v
npm --prefix app/web/streamlit_components/futures_macro_workbench run build
git diff --check
```

Expected: 4 contracts pass, Vite exits 0, production bundle is rebuilt.

- [x] **Step 5: Commit the implementation unit**

```bash
git add tests/test_service_contracts.py \
  app/web/streamlit_components/futures_macro_workbench/src/PatternMapSection.tsx \
  app/web/streamlit_components/futures_macro_workbench/component_static
git commit -m "선물 매크로 관측 좌표계 고정"
```

---

### Task 2: Actual Coordinate QA And Documentation Closeout

**Files:**
- Modify: active task `STATUS.md`, `RUNS.md`, `NOTES.md`, this plan.
- Modify: `.aiworkspace/note/finance/docs/flows/README.md`.
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md` only if its scale description would otherwise be incomplete.
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`, `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md` with concise handoff only.

**Interfaces:**
- Consumes: built React bundle and actual stored futures snapshot.
- Produces: exact observed anchor coordinate equality across three states and one QA screenshot.

- [x] **Step 1: Run focused verification**

```bash
.venv/bin/python -m unittest tests.test_futures_macro_pattern tests.test_futures_macro_pattern_validation
.venv/bin/python -m unittest tests.test_service_contracts.FuturesMacroThermometerContractTests
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_keeps_observed_anchors_on_one_shared_scale \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_uses_observed_anchors_and_conditional_branches \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_uses_one_terminal_range_and_readable_copy \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_pattern_map_uses_fixed_midline_direction_markers
npm --prefix app/web/streamlit_components/futures_macro_workbench run build
.venv/bin/python -m py_compile app/web/overview/futures_macro_helpers.py
git diff --check
```

- [x] **Step 2: Perform actual Browser QA**

Run the app on port `8512`. In the Futures Macro frame collect `cx / cy` for the three `.fm-pattern-map__anchor circle` elements after selecting `관측만`, `다음 5D`, and `다음 20D`.

Expected:

```text
observed anchors == 5D anchors == 20D anchors
5D uncertainty step == 5
20D uncertainty step == 20
5D forecast polyline points != 20D forecast polyline points
5D terminal cx/cy != 20D terminal cx/cy
420px clientWidth == scrollWidth
console errors == 0
```

Save an unstaged screenshot to:

```text
/Users/taeho/.codex/visualizations/2026/07/18/019f730e-7ff9-7720-b5c6-359d96ca1a4d/futures-macro-stable-coordinate-qa.png
```

- [x] **Step 3: Synchronize durable docs**

Record that the chart uses one shared visible-data coordinate system and that hidden intermediate q25/q75 no longer drives scale. Keep detailed commands and measured coordinates in task docs; keep root logs to 3~5 lines.

- [x] **Step 4: Run fresh closeout verification and commit**

Repeat the selected tests, Vite build, py_compile, screenshot existence, `git diff --check`, and `git status --short`. Stage only the active task and smallest durable doc set, then commit:

```bash
git commit -m "선물 매크로 관측 좌표 QA와 문서 정리"
```

## Completion Checklist

- [x] Task 1: shared visible-data scale implemented with RED/GREEN evidence.
- [x] Task 2: actual anchor equality QA, responsive QA, docs, and closeout complete.

## Roadmap State

- 1차 root-cause / stable-scale design: complete (`abac1da9`).
- 2차 shared-scale TDD implementation: complete (`766dada9`).
- 3차 actual Browser QA / docs closeout: complete.
