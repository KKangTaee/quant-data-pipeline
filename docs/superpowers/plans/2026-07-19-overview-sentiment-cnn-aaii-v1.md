# Overview Sentiment CNN·AAII 균형 개선 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** CNN 시장 행동과 AAII 개인투자자 인식을 합성점수 없이 동등한 두 축으로 보여주고, 일치·엇갈림 판정과 단위별 분리 그래프를 제공한다.

**Architecture:** `app/services/overview/sentiment.py`가 모든 방향·문구·근거를 deterministic read-model로 만들고, `app/web/overview/sentiment_helpers.py`가 `sentiment_react_workbench_v2` payload로 변환한다. React workbench는 판정을 재계산하지 않고 두 source card, cross-read, 통합 evidence, 세 개의 단위별 chart를 표현한다. 기존 DB loader와 refresh/reload Python dispatch boundary는 유지한다.

**Tech Stack:** Python 3, pandas, unittest service contracts, React 18, TypeScript 5, Vite 6, Streamlit custom component, CSS, in-app Browser QA.

## Global Constraints

- CNN은 `시장 행동 심리`, AAII는 `개인투자자 인식 심리`로 표현한다.
- CNN과 AAII를 하나의 숫자로 합성하지 않는다.
- CNN 구성요소는 CNN headline의 내부 근거이며 세 번째 독립 투표가 아니다.
- AAII 방향은 Bull-Bear Spread `+10pp / -10pp` 경계를 사용한다.
- spread 결측은 `neutral`이 아니라 `unavailable/판정 보류`다.
- CNN 일간, AAII 응답 주간, AAII Spread pp를 하나의 y축에 섞지 않는다.
- 신규 데이터, DB schema, ingestion job, 1주·1개월 확률 예측을 추가하지 않는다.
- raw row와 refresh 세부는 첫 화면의 주인공으로 만들지 않는다.
- 기존 refresh/reload action id와 `python_dispatch_only` boundary를 유지한다.
- 420px viewport에서 workbench horizontal overflow가 없어야 한다.

---

### Task 1: CNN·AAII 두 축과 교차 판정 read-model

**Files:**
- Modify: `tests/test_service_contracts.py:22028-22405`
- Modify: `app/services/overview/sentiment.py:431-833`

**Interfaces:**
- Consumes: `coverage`, normalized sentiment `component_rows`, normalized `history_rows` from the existing snapshot loader.
- Produces: `_aaii_direction(spread: float | None) -> str`, `_build_sentiment_axes(coverage, rows, component_rows, history_rows) -> dict[str, dict[str, Any]]`, `_build_sentiment_cross_read(market_behavior, investor_survey) -> dict[str, Any]`, and `analysis["axes"]`, `analysis["cross_read"]`, `analysis["watch_conditions"]`.

- [ ] **Step 1: Add failing AAII direction boundary tests**

Add focused tests to `OverviewMarketIntelligenceServiceContractTests`:

```python
def test_aaii_direction_uses_spread_without_bearish_gate(self) -> None:
    from app.services.overview.sentiment import _aaii_direction

    self.assertEqual(_aaii_direction(spread=12.0), "optimistic")
    self.assertEqual(_aaii_direction(spread=10.0), "optimistic")
    self.assertEqual(_aaii_direction(spread=-10.0), "pessimistic")
    self.assertEqual(_aaii_direction(spread=4.0), "neutral")
    self.assertEqual(_aaii_direction(spread=None), "unavailable")
```

- [ ] **Step 2: Run the boundary test and confirm RED**

Run:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_aaii_direction_uses_spread_without_bearish_gate -v
```

Expected: FAIL because the current helper requires `bearish` and returns CNN-style `greed/fear` values.

- [ ] **Step 3: Implement the minimal AAII direction rule**

Replace the old helper with:

```python
def _aaii_direction(*, spread: float | None) -> str:
    if spread is None:
        return "unavailable"
    if spread >= 10:
        return "optimistic"
    if spread <= -10:
        return "pessimistic"
    return "neutral"
```

Update callers to pass only `spread`.

- [ ] **Step 4: Run the boundary test and confirm GREEN**

Run the command from Step 2. Expected: `OK`, 1 test passed.

- [ ] **Step 5: Add failing two-axis and cross-read tests**

Create test fixtures with CNN 37.1, AAII Bullish 44.9, Neutral 22.2, Bearish 32.9, Spread +12.0 and assert:

```python
analysis = snapshot["analysis"]
self.assertEqual(analysis["axes"]["market_behavior"]["direction"], "fear")
self.assertEqual(analysis["axes"]["investor_survey"]["direction"], "optimistic")
self.assertEqual(analysis["cross_read"]["status"], "뚜렷한 엇갈림")
self.assertIn("시장 행동은 공포", analysis["cross_read"]["headline"])
self.assertIn("개인투자자 설문은 낙관", analysis["cross_read"]["headline"])
self.assertEqual(
    analysis["axes"]["investor_survey"]["long_term_comparison"]["bearish"]["difference_pp"],
    2.4,
)
self.assertNotIn("component_direction", analysis["cross_read"])
```

Add table cases for `greed/optimistic`, `fear/pessimistic`, `neutral/neutral`, one-neutral, and one-source-unavailable.

- [ ] **Step 6: Run the new cross-read tests and confirm RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_two_axis_cross_read_marks_cnn_fear_aaii_optimistic_as_divergent \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_cross_read_matrix_handles_alignment_neutral_and_missing \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_axes_include_aaii_long_term_comparison_and_history \
  -v
```

Expected: FAIL because `axes` and `cross_read` do not exist and the old divergence counts CNN components as a third direction.

- [ ] **Step 7: Implement axis builders and cross-read matrix**

Add focused helpers with these contracts:

```python
def _build_sentiment_axes(
    *,
    coverage: dict[str, Any],
    rows: pd.DataFrame | None,
    component_rows: list[dict[str, Any]],
    history_rows: pd.DataFrame | None,
) -> dict[str, dict[str, Any]]:
    cnn_score = _safe_float(coverage.get("cnn_score"))
    cnn_bucket = _sentiment_score_bucket(cnn_score)
    aaii_spread = _safe_float(coverage.get("aaii_bull_bear_spread"))
    aaii_direction = _aaii_direction(spread=aaii_spread)
    return {
        "market_behavior": _build_cnn_axis(
            cnn_score=cnn_score,
            cnn_bucket=cnn_bucket,
            component_rows=component_rows,
            history_rows=history_rows,
        ),
        "investor_survey": _build_aaii_axis(
            rows=rows,
            spread=aaii_spread,
            direction=aaii_direction,
            history_rows=history_rows,
        ),
    }

def _build_sentiment_cross_read(
    *,
    market_behavior: dict[str, Any],
    investor_survey: dict[str, Any],
) -> dict[str, Any]:
    if not market_behavior["available"] or not investor_survey["available"]:
        return _single_axis_cross_read(market_behavior, investor_survey)
    pair = (market_behavior["direction"], investor_survey["direction"])
    return _CROSS_READ_RESULTS[pair]
```

Implement `_build_cnn_axis`, `_build_aaii_axis`, `_single_axis_cross_read`, and the complete `_CROSS_READ_RESULTS` mapping in the same service module. Each axis must return `label`, `direction`, `direction_label`, `tone`, `current`, `previous`, `change`, `range`, `detail`, and `available`. The AAII axis additionally returns `responses`, `spread`, and `long_term_comparison`; the CNN axis returns `component_balance` and `components_support`.

Cross-read must map `greed ↔ optimistic` and `fear ↔ pessimistic`, return `status`, `tone`, `headline`, `meaning`, and `confidence_note`, and return `한 축만 확인 가능` if either axis is unavailable.

- [ ] **Step 8: Replace phase copy and watch conditions with two-axis output**

Make `_build_market_sentiment_analysis()` source its `phase`, `phase_label`, `headline`, and `summary` from cross-read. Add condition dictionaries such as:

```python
{
    "label": "CNN 행동 심리",
    "condition": "CNN Fear & Greed가 현재 구간을 벗어나 중립권으로 회복하는지 확인합니다.",
    "basis": "일간 관측",
    "tone": "warning",
}
```

The condition text must be based on current direction and must not state a probability or price forecast.

- [ ] **Step 9: Run focused service regression**

Run all sentiment snapshot tests in `OverviewMarketIntelligenceServiceContractTests`. Expected: all selected tests pass; update old assertions that intentionally encoded the three-axis divergence or old AAII condition.

- [ ] **Step 10: Commit Task 1**

```bash
git add app/services/overview/sentiment.py tests/test_service_contracts.py
git commit -m "Overview 심리 두 축 판정 정리"
```

---

### Task 2: React v2 payload와 단위별 chart series

**Files:**
- Modify: `tests/test_service_contracts.py:22406-22611`
- Modify: `app/web/overview/sentiment_helpers.py:260-500`

**Interfaces:**
- Consumes: Task 1 `analysis["axes"]`, `analysis["cross_read"]`, `analysis["watch_conditions"]`, normalized snapshot DataFrames.
- Produces: `sentiment_react_workbench_v2` with `summary`, `axes`, `cross_read`, `evidence`, `charts`, `watch_conditions`, `raw_evidence`, and unchanged `command`/`action_boundary`.

- [ ] **Step 1: Rewrite the payload contract test first**

Assert the exact v2 shape:

```python
self.assertEqual(payload["schema_version"], "sentiment_react_workbench_v2")
self.assertEqual(set(payload["axes"]), {"market_behavior", "investor_survey"})
self.assertEqual(payload["axes"]["market_behavior"]["label"], "시장 행동")
self.assertEqual(payload["axes"]["investor_survey"]["label"], "개인투자자 설문")
self.assertEqual(payload["cross_read"]["status"], "뚜렷한 엇갈림")
self.assertEqual(payload["charts"]["cnn"]["unit"], "score_0_100")
self.assertEqual(payload["charts"]["aaii_responses"]["unit"], "percent")
self.assertEqual(payload["charts"]["aaii_spread"]["unit"], "percentage_point")
self.assertEqual([action["id"] for action in payload["command"]["actions"]], ["refresh", "reload"])
```

Also assert every CNN chart point has only `CNN Fear & Greed`, AAII response points only have the three AAII response series, and spread points only have `AAII Bull-Bear Spread`.

- [ ] **Step 2: Run payload test and confirm RED**

Expected: FAIL on schema version and missing `axes`/separated chart keys.

- [ ] **Step 3: Implement the v2 payload**

Refactor `build_sentiment_react_workbench_payload()` to produce:

```python
{
    "schema_version": "sentiment_react_workbench_v2",
    "component": "SentimentWorkbench",
    "action_boundary": "python_dispatch_only",
    "summary": {**cross_read, "latest_observation_date": latest_date},
    "axes": analysis["axes"],
    "cross_read": analysis["cross_read"],
    "evidence": {
        "cnn_components": merged_component_rows,
        "aaii_comparison": aaii_comparison_rows,
    },
    "charts": {
        "cnn": {"unit": "score_0_100", "series": cnn_points},
        "aaii_responses": {"unit": "percent", "series": response_points},
        "aaii_spread": {"unit": "percentage_point", "series": spread_points},
    },
    "watch_conditions": analysis["watch_conditions"],
    "raw_evidence": {
        "warnings": warnings,
        "sentiment_rows": raw_rows,
        "component_rows": component_rows,
        "history_rows": history_rows,
    },
    "command": existing_command,
}
```

Merge component latest/previous/change fields by `series` so React renders each CNN component once.

- [ ] **Step 4: Run payload test and focused service regression**

Expected: v2 payload test and all sentiment service tests pass.

- [ ] **Step 5: Commit Task 2**

```bash
git add app/web/overview/sentiment_helpers.py tests/test_service_contracts.py
git commit -m "Overview 심리 v2 payload 구성"
```

---

### Task 3: 두 축 workbench와 중복 없는 evidence UI

**Files:**
- Modify: `tests/test_service_contracts.py:8498-8810`
- Modify: `app/web/streamlit_components/sentiment_workbench/src/SentimentWorkbench.tsx:1-640`
- Modify: `app/web/streamlit_components/sentiment_workbench/src/style.css`

**Interfaces:**
- Consumes: Task 2 `SentimentWorkbenchPayload` v2.
- Produces: hero, symmetric axis cards, cross-read panel, one CNN evidence list, one AAII comparison list, watch conditions, and collapsed raw disclosure.

- [ ] **Step 1: Add failing React source-contract tests**

Replace old string tests that require duplicate CNN sections with assertions for:

```python
self.assertIn('payload.schema_version === "sentiment_react_workbench_v2"', react_source)
self.assertIn("payload.axes.market_behavior", react_source)
self.assertIn("payload.axes.investor_survey", react_source)
self.assertIn("시장 행동", react_source)
self.assertIn("개인투자자 설문", react_source)
self.assertIn("현재 판정", react_source)
self.assertIn("다음 확인 조건", react_source)
self.assertEqual(react_source.count("payload.evidence.cnn_components.map"), 1)
self.assertIn("payload.evidence.aaii_comparison.map", react_source)
self.assertIn("<details", react_source)
self.assertNotIn("payload.drivers.lanes.map", react_source)
self.assertNotIn("payload.component_explanations.map", react_source)
```

- [ ] **Step 2: Run the React source tests and confirm RED**

Expected: FAIL because the current component uses v1, driver lanes, component explanations, and always-visible raw tables.

- [ ] **Step 3: Define exact v2 TypeScript types**

Add `SentimentAxis`, `CrossRead`, `CnnEvidence`, `AaiiComparison`, `ChartPanel`, and `WatchCondition` interfaces matching Task 2 keys. The root payload must use literal `schema_version: "sentiment_react_workbench_v2"`.

- [ ] **Step 4: Implement the first visual structure**

Render in this order:

```tsx
<section className="sentiment-workbench">
  <Hero summary={payload.summary} command={payload.command} />
  <section className="sentiment-workbench__axis-grid">
    <SentimentAxisCard axis={payload.axes.market_behavior} />
    <SentimentAxisCard axis={payload.axes.investor_survey} />
  </section>
  <CrossReadPanel crossRead={payload.cross_read} />
  <EvidenceSection evidence={payload.evidence} />
  <ChartSection charts={payload.charts} />
  <WatchConditions rows={payload.watch_conditions} />
  <RawEvidenceDisclosure rows={payload.raw_evidence} />
</section>
```

AAII card must render Bullish/Neutral/Bearish and long-term differences. CNN card must render component distribution but not the full seven component rows.

- [ ] **Step 5: Add layout CSS and responsive rule**

Use a 2-column axis grid and switch to one column at `max-width: 760px`. Keep visual hierarchy aligned with Market Context/Futures Macro: compact eyebrow, strong headline, muted explanation, bordered evidence surfaces, and no job-count hero.

- [ ] **Step 6: Run React source tests and production build**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_summary_surface_prioritizes_state_and_freshness \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_driver_surface_groups_cnn_and_aaii_without_next_checks \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_context_surface_shows_recent_range_and_divergence \
  -v
cd app/web/streamlit_components/sentiment_workbench && npm run build
```

Expected: selected tests pass and Vite exits 0.

- [ ] **Step 7: Commit Task 3**

```bash
git add tests/test_service_contracts.py app/web/streamlit_components/sentiment_workbench/src app/web/streamlit_components/sentiment_workbench/component_static
git commit -m "Overview 심리 두 축 UI 구성"
```

---

### Task 4: 실제 날짜 기반 분리 그래프

**Files:**
- Modify: `tests/test_service_contracts.py:8783-8810`
- Modify: `app/web/streamlit_components/sentiment_workbench/src/SentimentWorkbench.tsx`
- Modify: `app/web/streamlit_components/sentiment_workbench/src/style.css`

**Interfaces:**
- Consumes: Task 2 `charts.cnn`, `charts.aaii_responses`, `charts.aaii_spread`.
- Produces: three accessible chart tabs, timestamp x-scale, fixed CNN/AAII response scales, and zero/+10/-10 guides for spread.

- [ ] **Step 1: Add failing graph source-contract tests**

Assert:

```python
self.assertIn('type ChartTab = "cnn" | "aaii_responses" | "aaii_spread"', react_source)
self.assertIn("Date.parse", react_source)
self.assertIn('aria-label="심리 근거 그래프"', react_source)
self.assertIn("CNN 행동", react_source)
self.assertIn("AAII 응답", react_source)
self.assertIn("AAII Spread", react_source)
self.assertIn("spreadGuideValues", react_source)
self.assertNotIn("historyDates.indexOf", react_source)
```

- [ ] **Step 2: Run graph test and confirm RED**

Expected: FAIL because current chart has two tabs, shared dynamic y-scale, and ordinal date indices.

- [ ] **Step 3: Implement shared chart geometry with timestamp x-scale**

Create pure frontend helpers:

```ts
function dateExtent(points: ChartPoint[]): [number, number] {
  const values = points.map((point) => Date.parse(point.date)).filter(Number.isFinite);
  const minimum = values.length ? Math.min(...values) : 0;
  const maximum = values.length ? Math.max(...values) : minimum;
  return [minimum, maximum];
}

function xForTimestamp(date: string, minTs: number, maxTs: number, width: number): number {
  const timestamp = Date.parse(date);
  return maxTs === minTs ? width / 2 : ((timestamp - minTs) / (maxTs - minTs)) * width;
}

function yForValue(value: number, min: number, max: number, height: number): number {
  return max === min ? height / 2 : (1 - (value - min) / (max - min)) * height;
}
```

CNN uses `[0, 100]`, AAII responses use `[0, 100]`, and spread derives a symmetric extent including `-10`, `0`, `10`. A single observation must render as a point without division by zero.

- [ ] **Step 4: Implement the three graph panels**

- CNN: background bands and labels for fear/neutral/greed.
- AAII responses: three colored lines with percent labels.
- AAII spread: emphasized zero line and dashed ±10pp guides.
- All tabs: `role=tab`, `aria-selected`, associated panel id, readable latest-value summary outside SVG.

- [ ] **Step 5: Run graph test, all React source tests, and build**

Expected: all sentiment React source tests pass and Vite build exits 0.

- [ ] **Step 6: Commit Task 4**

```bash
git add tests/test_service_contracts.py app/web/streamlit_components/sentiment_workbench/src app/web/streamlit_components/sentiment_workbench/component_static
git commit -m "Overview 심리 그래프 단위별 분리"
```

---

### Task 5: UI 선택 checkpoint와 Browser QA

**Files:**
- Modify after user visual feedback only: `app/web/streamlit_components/sentiment_workbench/src/SentimentWorkbench.tsx`
- Modify after user visual feedback only: `app/web/streamlit_components/sentiment_workbench/src/style.css`
- Regenerate after accepted visual change: `app/web/streamlit_components/sentiment_workbench/component_static/`

**Interfaces:**
- Consumes: working Task 1-4 implementation with current stored CNN/AAII data.
- Produces: user-reviewed visual hierarchy and desktop/mobile QA evidence.

- [ ] **Step 1: Start the existing Finance Streamlit app and open Overview > 심리**

Run the documented headless QA server command on an unused explicit port:

```bash
.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8508 --server.headless true --server.runOnSave false --server.fileWatcherType none
```

If port 8508 is already occupied, inspect the owner and choose one explicit free port between 8509 and 8518. Do not stop an unrelated process, add a new run script, or add a diagnostic panel.

- [ ] **Step 2: Capture the first desktop UI checkpoint**

Capture a screenshot showing hero, both source cards, cross-read, and the first chart. Send it to the user during the task and explicitly ask whether to keep or adjust:

- two source cards' information density
- cross-read emphasis
- graph tab placement

Do not present a synthetic score option because it is outside the approved design.

- [ ] **Step 3: Apply only the selected visual adjustment**

If the user requests a change, modify layout/copy/CSS only within the approved v2 contract. If the request changes source weighting, prediction scope, or data providers, stop and return to design approval.

- [ ] **Step 4: Run desktop and 420px Browser QA**

Verify:

- both source cards have equal visual weight
- cross-read headline matches current CNN/AAII directions
- each chart tab uses the correct unit and source cadence
- raw evidence is collapsed by default
- 420px outer and component scroll widths equal client widths
- no console errors

- [ ] **Step 5: Rebuild and run focused regression after visual changes**

Expected: Vite build exits 0 and all focused sentiment tests pass.

- [ ] **Step 6: Commit Task 5**

```bash
git add app/web/streamlit_components/sentiment_workbench/src app/web/streamlit_components/sentiment_workbench/component_static tests/test_service_contracts.py
git commit -m "Overview 심리 UI 시각 검수 반영"
```

---

### Task 6: 문서 정렬과 최종 검증

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1-20260719/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1-20260719/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1-20260719/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1-20260719/RISKS.md`
- Modify if durable flow changed: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

**Interfaces:**
- Consumes: verified implementation and Browser QA evidence.
- Produces: task closeout, root handoff pointer, and clear roadmap state showing only 1/4 complete.

- [ ] **Step 1: Run fresh final verification**

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_snapshot_summarizes_cnn_and_aaii_context \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_snapshot_adds_range_divergence_and_component_history \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_react_payload_uses_existing_snapshot_fields \
  -v
cd app/web/streamlit_components/sentiment_workbench && npm run build
cd /Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev
git diff --check
git status --short
```

Also run every newly added sentiment test by exact name. Record pass counts and any unexecuted checks.

- [ ] **Step 2: Apply `finance-doc-sync` closeout**

Update task docs with exact commands, pass counts, screenshot path, current roadmap state `1/4차 완료`, remaining 2-4차, and the next continuation location. Keep root logs to 3-5 lines and do not copy implementation transcripts.

- [ ] **Step 3: Review the final diff**

Confirm no unrelated untracked research bundle, `.superpowers/`, or prior QA PNG is staged. Confirm no DB/ingestion/registry/saved files changed.

- [ ] **Step 4: Commit closeout docs**

```bash
git add .aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1-20260719 .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "Overview 심리 1차 개선 기록 정리"
```

- [ ] **Step 5: Finish the development branch workflow**

Invoke `superpowers:finishing-a-development-branch`, report verified results, show the accepted QA screenshot, and state that 2-4차 remain.
