# Futures Macro Short-Horizon V1 Implementation Plan

> **For Codex:** Execute this plan task by task with red-green-refactor discipline. Do not stage unrelated registry, research, run-history, `.superpowers/`, or QA image changes.

**Goal:** 선물 매크로 첫 화면을 `최근 1거래일 새 충격 -> 최근 5거래일 단기 방향 -> 향후 5거래일 검증 결론`으로 재구성하고, routine 일봉 갱신의 10년 반복 수집과 불변 입력의 전체 전망 재계산을 제거한다.

**Architecture:** Python adapter가 stored snapshot의 6개 family를 `핵심 4 + 확인 2`와 사용자 판단 문구로 변환하고 React는 이를 그대로 렌더링한다. 일봉 수집은 DB coverage를 기준으로 1년 routine overlap과 종목별 10년 bootstrap을 분리한다. Materializer는 completed-session 입력을 먼저 준비해 fingerprint를 비교하고, 호환 snapshot과 입력이 같을 때 macro/outlook builder 호출 전에 종료한다.

**Tech Stack:** Python 3, pandas, MySQL loader/UPSERT, Streamlit custom component, React 18, TypeScript 5, Vite 6, unittest/pytest source-contract tests, Codex in-app Browser QA.

## Non-negotiable contracts

- 6개 family 산식, 가중치, 상태 threshold, publication gate는 바꾸지 않는다.
- backend의 5D/20D outlook, immutable forecast history, completed-session resolver는 유지한다.
- React 또는 Streamlit render 단계에서 provider/DB 계산을 새로 실행하지 않는다.
- `NO_EDGE`는 오류나 반대 방향이 아니라 baseline 대비 추가 정확도 부재로 표시한다.
- routine refresh 중 실패한 symbol의 기존 DB rows와 latest-good snapshot을 삭제하거나 덮어쓰지 않는다.
- 60D ribbon은 secondary history로 유지한다. 향후 20D 카드와 2D map만 default render에서 제외한다.
- stage timing은 job result와 task run evidence에만 남기며 첫 화면에 운영 진단 패널을 추가하지 않는다.

---

## Task 1: Python short-horizon decision payload

**Files:**

- Create: `tests/test_overview_futures_macro_short_horizon.py`
- Modify: `app/web/overview/futures_macro_helpers.py`
- Modify: `tests/test_service_contracts.py`
- Modify: `tests/test_futures_macro_v2_integration.py`

### Step 1: Write failing payload contract tests

Add fixtures with all six stored families and 5D outlook states, then add these tests:

```python
def test_short_horizon_payload_orders_core_four_and_confirmation_two():
    payload = build_futures_macro_react_workbench_payload(
        macro_fixture(), pattern_outlook=outlook_fixture("NO_EDGE")
    )
    decision = payload["short_horizon_decision"]
    assert [row["key"] for row in decision["core_directions"]] == [
        "risk_on", "rate_pressure", "dollar_pressure", "inflation_pressure"
    ]
    assert [row["key"] for row in decision["confirmation_signals"]] == [
        "growth", "safe_haven"
    ]
    assert decision["observation_windows"] == [
        {"key": "1D", "label": "최근 1거래일", "role": "새 충격"},
        {"key": "5D", "label": "최근 5거래일", "role": "단기 방향"},
        {"key": "20D", "label": "최근 20거래일", "role": "배경 흐름"},
    ]


def test_no_edge_copy_explains_baseline_without_exposing_internal_label():
    validation = payload_for_status("NO_EDGE")["short_horizon_decision"][
        "future_five_day_validation"
    ]
    assert validation["title"] == "방향 예측 근거 부족"
    assert validation["detail"] == (
        "유사 국면 모델이 평소 5거래일 결과 빈도보다 정확하지 않음"
    )
    assert validation["status"] == "NO_EDGE"


def test_calculation_scope_is_derived_from_collection_and_score_members():
    scope = payload["short_horizon_decision"]["calculation_scope"]
    assert scope["collected_count"] == 17
    assert scope["direct_family_input_count"] == 15
    assert scope["available_family_count"] == 6
    assert scope["required_family_count"] == 6
    assert scope["shared_context_symbols"] == ["DX-Y.NYB"]
    assert scope["raw_observation_symbols"] == ["SI=F"]
```

Also assert:

- the direction rows contain Python-derived `one_day`, `five_day`, and `twenty_day` display states;
- a negative `risk_on` plus negative `safe_haven` does not produce a simple defensive-confirmed conclusion;
- `VERIFIED`, `PROVISIONAL`, and `UNAVAILABLE` use the approved copy;
- schema version is `futures_macro_react_workbench_v4`;
- existing 5D/20D backend horizons remain in the compatibility payload, but only 5D is referenced by `future_five_day_validation`.

Run:

```bash
.venv/bin/python -m pytest tests/test_overview_futures_macro_short_horizon.py -q
```

Expected: FAIL because `short_horizon_decision` and schema v4 do not exist.

### Step 2: Implement deterministic Python adapters

In `futures_macro_helpers.py` add explicit immutable mappings:

```python
PATTERN_CORE_FAMILY_DEFINITIONS = (
    ("risk_on", "주가지수 위험선호"),
    ("rate_pressure", "채권·금리 압력"),
    ("dollar_pressure", "달러 압력"),
    ("inflation_pressure", "원자재·물가 압력"),
)
PATTERN_CONFIRMATION_FAMILY_DEFINITIONS = (
    ("growth", "경기민감 성장"),
    ("safe_haven", "안전자산 선호"),
)
FUTURES_MACRO_SHARED_CONTEXT_SYMBOLS = ("DX-Y.NYB",)
FUTURES_MACRO_RAW_OBSERVATION_SYMBOLS = ("SI=F",)
```

Implement small pure helpers with explicit dict-in/dict-out signatures:

- `_pattern_family_direction_row(families, family_key, label)`
- `_pattern_core_alignment_summary(core_rows)`
- `_pattern_confirmation_summary(core_rows, confirmation_rows)`
- `_future_five_day_validation_payload(pattern_outlook)`
- `_futures_macro_calculation_scope(macro, pattern)`
- `_short_horizon_decision_payload(macro, pattern, pattern_outlook)`

The family row must classify existing numeric values with the existing threshold semantics and carry no React-side market inference. Derive the direct family input set from the union of `definition.members` for `definition in SCORE_DEFINITIONS`. Use actual `coverage.symbol_count` when present and fall back to `len(DEFAULT_CORE_FUTURES_SYMBOLS)`; do not hardcode 17/15.

Update `build_futures_macro_react_workbench_payload` to return schema v4 and the new block while retaining legacy backend evidence fields required by Method/trace and integration compatibility.

### Step 3: Run focused tests and update old assertions

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_overview_futures_macro_short_horizon.py \
  tests/test_futures_macro_v2_integration.py \
  tests/test_service_contracts.py -q -k 'futures_macro_v3 or futures_macro_v4 or short_horizon'
```

Expected: PASS after replacing v3-only UI assertions with the v4 decision contract; do not weaken 5D `NO_EDGE` probability suppression assertions.

### Step 4: Commit the payload unit

```bash
git add app/web/overview/futures_macro_helpers.py \
  tests/test_overview_futures_macro_short_horizon.py \
  tests/test_futures_macro_v2_integration.py \
  tests/test_service_contracts.py
git commit -m "선물 매크로 단기 판단 payload 추가"
```

---

## Task 2: React primary reading flow and family hierarchy

**Files:**

- Create: `app/web/streamlit_components/futures_macro_workbench/src/ShortHorizonDecisionSection.tsx`
- Create: `app/web/streamlit_components/futures_macro_workbench/src/FamilyDirectionSection.tsx`
- Create: `app/web/streamlit_components/futures_macro_workbench/src/CalculationScopeSection.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/FuturesMacroWorkbench.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/MacroContextSection.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/PatternRibbonSection.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/style.css`
- Modify: `tests/test_overview_futures_macro_short_horizon.py`
- Generate: `app/web/streamlit_components/futures_macro_workbench/component_static/index.html`
- Generate: `app/web/streamlit_components/futures_macro_workbench/component_static/assets/*`

### Step 1: Add failing source/render-boundary tests

Add source-contract tests that assert:

```python
assert "ShortHorizonDecisionSection" in workbench_source
assert "FamilyDirectionSection" in workbench_source
assert "CalculationScopeSection" in workbench_source
assert "<PatternHorizonSection" not in default_render
assert "<PatternMapSection" not in default_render
assert "<AssetPathwaysSection" not in default_render
assert "<PatternRibbonSection" in default_render
assert "최근 20거래일" in decision_source
assert "20D는 미래 예측이 아닙니다" not in all_component_source
```

Also assert the primary DOM order is context -> short-horizon steps -> core/confirmation matrix -> change conditions/scope -> ribbon -> method/trace.

Run:

```bash
.venv/bin/python -m pytest tests/test_overview_futures_macro_short_horizon.py -q -k react
```

Expected: FAIL because the new sections do not exist.

### Step 2: Implement the new component types and render order

In `FuturesMacroWorkbench.tsx` add exact TypeScript types for:

- `ObservationWindow`
- `FamilyDirectionRow`
- `FutureFiveDayValidation`
- `CalculationScope`
- `ShortHorizonDecisionPayload`

Change `schema_version` to the v4 literal. Default render becomes:

```tsx
<MacroContextSection
  command={payload.command}
  hero={payload.hero}
  onAction={emitAction}
  pendingActionId={pendingActionId}
  sessionEvidence={payload.session_evidence}
/>
<ShortHorizonDecisionSection decision={payload.short_horizon_decision} />
<FamilyDirectionSection
  coreDirections={payload.short_horizon_decision.core_directions}
  confirmationSignals={payload.short_horizon_decision.confirmation_signals}
/>
<CalculationScopeSection
  changeConditions={payload.short_horizon_decision.change_conditions}
  scope={payload.short_horizon_decision.calculation_scope}
/>
<PatternRibbonSection ribbon={payload.ribbon} />
<MethodDisclosure
  boundaryNote={payload.boundary_note}
  horizons={payload.horizons}
  method={payload.method}
  onToggle={syncFrameHeightSoon}
/>
<CalculationTraceDisclosure
  trace={payload.calculation_trace}
  onToggle={syncFrameHeightSoon}
/>
```

Remove only the default imports/render calls for the old three horizon cards, 2D map, current-evidence side panel, and repeated asset pathways. Keep their backend-compatible payload fields and source files in this unit so no storage/model deletion is coupled to the visual change.

### Step 3: Style desktop and narrow layouts

Add CSS with these visual rules:

- three numbered decision steps read left-to-right on desktop and vertically at <= 720px;
- observation chips say `최근 1거래일 / 최근 5거래일 / 최근 20거래일` with role labels;
- core four rows are one primary matrix with aligned 1/5/20 columns;
- confirmation two are visually subordinate cards, not a fifth/sixth core axis;
- future 5D validation status uses semantic class from internal status but approved Korean copy;
- calculation scope is secondary and compact;
- ribbon heading is `최근 체제 이력` and remains below the decision surface;
- 420px width has no fixed-width overflow, clipped labels, or tiny tap targets.

### Step 4: Build and verify the canonical bundle

Run:

```bash
cd app/web/streamlit_components/futures_macro_workbench
npm run build
cd /Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev
.venv/bin/python -m pytest tests/test_overview_futures_macro_short_horizon.py -q
git diff --check
```

Expected: TypeScript build and Python source contracts PASS. Confirm old hashed assets removed by Vite are only this component's generated bundle changes.

### Step 5: Commit the UI unit

```bash
git add app/web/streamlit_components/futures_macro_workbench/src \
  app/web/streamlit_components/futures_macro_workbench/component_static \
  tests/test_overview_futures_macro_short_horizon.py
git commit -m "선물 매크로 단기 판단 화면 개편"
```

---

## Task 3: Routine one-year overlap and per-symbol bootstrap

**Files:**

- Create: `tests/test_overview_futures_macro_refresh.py`
- Modify: `finance/data/futures_market.py`
- Modify: `finance/loaders/futures.py`
- Modify: `finance/loaders/__init__.py`
- Modify: `app/jobs/ingestion_jobs.py`
- Modify: `app/jobs/overview_actions.py`
- Modify: `app/web/overview/futures_macro_helpers.py`
- Modify: `tests/test_futures_macro_snapshot.py`

### Step 1: Write failing refresh-plan tests

Create isolated tests with injected coverage and job runners:

```python
def test_complete_core_symbols_use_one_year_overlap():
    plan = build_futures_macro_daily_refresh_plan(coverage=complete_coverage())
    assert plan["routine_symbols"] == list(DEFAULT_CORE_FUTURES_SYMBOLS)
    assert plan["bootstrap_symbols"] == []
    assert plan["routine_period"] == "1y"


def test_only_deficient_symbol_gets_ten_year_bootstrap():
    plan = build_futures_macro_daily_refresh_plan(
        coverage=coverage_with_deficient("SI=F")
    )
    assert plan["bootstrap_symbols"] == ["SI=F"]
    assert "SI=F" not in plan["routine_symbols"]
    assert plan["bootstrap_period"] == "10y"


def test_split_collection_materializes_once_after_both_groups():
    requested_periods = []
    materialized = []

    def collect_runner(**kwargs):
        requested_periods.append(kwargs["period"])
        return successful_collection_result(kwargs["symbols"])

    result = run_overview_futures_daily_ohlcv(
        coverage_loader=lambda symbols: coverage_with_deficient("SI=F"),
        collect_runner=collect_runner,
        materialize_fn=lambda: materialized.append(True) or {"status": "materialized"},
    )
    assert requested_periods == ["1y", "10y"]
    assert materialized == [True]
    assert result["details"]["futures_macro_snapshot"]["status"] == "materialized"
```

Also test that a failed bootstrap symbol does not remove successful routine evidence and yields partial success with the latest-good snapshot preserved.

Run:

```bash
.venv/bin/python -m pytest tests/test_overview_futures_macro_refresh.py -q
```

Expected: FAIL because coverage loader, planner, and injectable orchestrator do not exist.

### Step 2: Add compact DB coverage loader

In `finance/loaders/futures.py`, implement an injectable-query loader returning one row per requested symbol:

```python
def load_futures_daily_coverage(
    symbols: Sequence[str], *, query_fn: QueryFn | None = None
) -> list[dict[str, object]]:
    """Return stored 1D row count/min/max per symbol without loading OHLCV history."""
```

The SQL must filter `interval_code = '1d'` and use `COUNT(*)`, `MIN(candle_time_utc)`, and `MAX(candle_time_utc)` grouped by provider symbol. Export it through `finance/loaders/__init__.py`.

### Step 3: Add explicit routine/bootstrap constants and planner

In `finance/data/futures_market.py` add:

```python
FUTURES_MACRO_ROUTINE_DAILY_PERIOD = "1y"
FUTURES_MACRO_BOOTSTRAP_DAILY_PERIOD = FUTURES_MACRO_DAILY_PERIOD
```

In `overview_actions.py`, implement `build_futures_macro_daily_refresh_plan(coverage, *, symbols=DEFAULT_CORE_FUTURES_SYMBOLS)`. A symbol is bootstrap-deficient when no daily rows exist or its stored history is below the model's documented minimum. The threshold must be named and tied to the pattern-validation minimum, not an unexplained literal in the function body.

Update the command detail copy from “10년을 다시 수집” to “최근 1년 overlap을 갱신하고, 이력이 부족한 종목만 장기 보강” without adding a new primary repair button.

### Step 4: Orchestrate split collection and one materialization

Add `materialize_snapshot: bool = True` to `run_collect_futures_ohlcv`. When false, it returns the collection result without calling `attach_futures_macro_materialization`.

Refactor `run_overview_futures_daily_ohlcv` so it:

1. loads compact coverage;
2. collects routine symbols with `1y/1d` and bootstrap symbols with `10y/1d`, both with materialization disabled;
3. combines counts, failed symbols, messages, and collection stage durations into one `JobResult`;
4. calls `attach_futures_macro_materialization` once if any daily rows were written;
5. keeps partial failures as `partial_success` and never deletes old rows.

Use injected `coverage_loader`, `collect_runner`, and `materialize_fn` defaults so tests do not hit provider or DB.

In `collect_and_store_futures_ohlcv`, record backend-only `download_normalize_duration_sec` and `upsert_duration_sec` diagnostics with `perf_counter`. Preserve existing batch diagnostics. The combined Overview job must expose collection-group duration plus these low-level timings under `details`, not in the Futures Macro first-screen payload.

### Step 5: Run refresh and ingestion regressions

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_overview_futures_macro_refresh.py \
  tests/test_futures_macro_snapshot.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k 'overview_actions or futures_daily or futures_macro'
```

Expected: PASS; existing intraday and direct ingestion callers retain their default materialization behavior.

### Step 6: Commit the refresh unit

```bash
git add finance/data/futures_market.py finance/loaders/futures.py \
  finance/loaders/__init__.py app/jobs/ingestion_jobs.py \
  app/jobs/overview_actions.py app/web/overview/futures_macro_helpers.py \
  tests/test_overview_futures_macro_refresh.py tests/test_futures_macro_snapshot.py \
  tests/test_service_contracts.py
git commit -m "선물 일봉 갱신을 증분 수집으로 전환"
```

---

## Task 4: Pre-materialization fingerprint fast path

**Files:**

- Modify: `app/services/futures_macro_pattern_validation.py`
- Modify: `app/services/futures_macro_snapshot.py`
- Modify: `app/jobs/ingestion_jobs.py`
- Modify: `tests/test_futures_macro_pattern_validation.py`
- Modify: `tests/test_futures_macro_snapshot.py`
- Modify: `tests/test_futures_macro_v2_integration.py`

### Step 1: Write failing builder-skip tests

Add tests that prove call order rather than only final status:

```python
def test_unchanged_probe_reuses_before_macro_and_outlook_builders():
    result = materialize_overview_futures_macro_snapshot(
        marker_fn=lambda: "new raw marker",
        load_fn=lambda: compatible_row(input_fingerprint="a" * 64),
        input_probe_fn=lambda: completed_probe(input_fingerprint="a" * 64),
        macro_builder=lambda: fail("macro builder must be skipped"),
        outlook_builder=lambda: fail("outlook builder must be skipped"),
    )
    assert result["status"] == "reused"


The same test module must include complete implementations for these three cases:

- changed probe calls both builders and persists exactly one current/history bundle;
- matching fingerprint with an incompatible algorithm calls both builders and replaces the incompatible row;
- matching forecast input with changed pending-session evidence refreshes only the pending evidence without nested validation.
```

Also assert the probe fingerprint excludes collection timestamps/run ids but changes for provider symbol, completed session time, or any OHLCV value.

Run:

```bash
.venv/bin/python -m pytest tests/test_futures_macro_snapshot.py -q -k 'probe or builder or fingerprint'
```

Expected: FAIL because materialization currently calls both builders before comparing fingerprints.

### Step 2: Split input preparation from expensive outlook evaluation

In `futures_macro_pattern_validation.py`, extract the current pre-model work into two internal/publicly testable units:

```python
def prepare_overview_futures_macro_pattern_inputs(
    *,
    query_fn: QueryFn | None = None,
    symbols: Sequence[str] | None = None,
    years: int = FUTURES_MACRO_HISTORY_YEARS,
    evaluation_time: datetime | None = None,
) -> dict[str, Any]:
    """Load completed daily rows and PIT context once, then return fingerprinted inputs."""


def build_overview_futures_macro_pattern_outlook_from_inputs(
    prepared: dict[str, Any]
) -> dict[str, Any]:
    """Run nested validation from already prepared inputs."""
```

The prepared bundle contains completed rows, candles, features, current pattern, cycle/event rows, context frame, session evidence, input evidence, and the existing `_input_fingerprint`. Preserve the same canonical fields and PIT `known_at` behavior.

Make `load_overview_futures_macro_pattern_outlook` delegate to prepare -> build so existing callers retain the same output schema and cache contract.

### Step 3: Move compatibility decision before builders

Add `input_probe_fn` to `materialize_overview_futures_macro_snapshot`. Default it to the new prepare function. The control flow becomes:

```text
marker/read existing
  -> prepare completed-session inputs + fingerprint
  -> compatible unchanged final session? return reused
  -> same forecast but new pending-session evidence? update only required evidence
  -> otherwise build macro + build outlook from prepared inputs + persist
```

The default outlook builder must consume the prepared bundle so changed inputs are not loaded twice. Keep no-argument injected builders supported for unit tests. For an unchanged forecast with new pending-session evidence, patch only the stored compact session evidence and do not invoke nested validation. Return `input_compare_duration_sec` and `materialization_duration_sec` in materialization result; aggregate them into backend job details only.

Do not use raw source marker alone as equality because UPSERT collection timestamps can move without changing model inputs.

### Step 4: Run model, snapshot, and integration regressions

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_futures_macro_pattern_validation.py \
  tests/test_futures_macro_snapshot.py \
  tests/test_futures_macro_v2_integration.py -q
```

Expected: PASS with exact existing publication status, suppression, completed-session, and forecast identity behavior.

### Step 5: Commit the fast-path unit

```bash
git add app/services/futures_macro_pattern_validation.py \
  app/services/futures_macro_snapshot.py app/jobs/ingestion_jobs.py \
  tests/test_futures_macro_pattern_validation.py \
  tests/test_futures_macro_snapshot.py tests/test_futures_macro_v2_integration.py
git commit -m "선물 매크로 불변 입력 재계산 생략"
```

---

## Task 5: Integrated verification, actual performance, Browser QA, and docs

**Files:**

- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-futures-macro-short-horizon-v1-20260723/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-futures-macro-short-horizon-v1-20260723/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-futures-macro-short-horizon-v1-20260723/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-futures-macro-short-horizon-v1-20260723/RISKS.md`
- Generate, do not stage: one Futures Macro desktop QA screenshot

### Step 1: Run static and focused suites

```bash
git diff --check
.venv/bin/python -m py_compile \
  app/web/overview/futures_macro_helpers.py \
  app/jobs/overview_actions.py \
  app/jobs/ingestion_jobs.py \
  app/services/futures_macro_pattern_validation.py \
  app/services/futures_macro_snapshot.py \
  finance/data/futures_market.py \
  finance/loaders/futures.py
.venv/bin/python -m pytest \
  tests/test_overview_futures_macro_short_horizon.py \
  tests/test_overview_futures_macro_refresh.py \
  tests/test_futures_macro_snapshot.py \
  tests/test_futures_macro_pattern_validation.py \
  tests/test_futures_macro_v2_integration.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k futures_macro
npm --prefix app/web/streamlit_components/futures_macro_workbench run build
```

Expected: all commands PASS. If the full service-contract subset exposes unrelated pre-existing failures, record the exact test and prove it is pre-existing before proceeding.

### Step 2: Measure actual refresh behavior

Against the local stored dataset, execute and record in `RUNS.md`:

- refresh plan: routine/bootstrap symbol counts and requested periods;
- provider rows returned and rows UPSERTed;
- collection duration;
- input comparison duration;
- unchanged-input materialization status and duration;
- changed-session rebuild duration when safely reproducible.

Completion evidence must show that a normal complete-coverage run no longer requests `10y/1d` for all 17 symbols and that an unchanged completed-session input never calls nested outlook evaluation. Do not promise a fixed seconds target unless the actual local run supports it.

### Step 3: Run actual Browser QA

Use the in-app Browser against `http://localhost:49190/`:

1. Open Market Research -> Futures Macro.
2. Confirm the actual stored snapshot renders the approved three-step flow.
3. Confirm core 4 and confirmation 2 are visually distinct and all six are present.
4. Confirm `NO_EDGE` shows `방향 예측 근거 부족` and the baseline explanation.
5. Confirm no future 20D card or 2D map appears in default view.
6. Confirm `최근 체제 이력` ribbon remains secondary.
7. Confirm refresh/reload actions remain usable and no console error occurs.
8. Repeat at 420px viewport and check horizontal overflow/focus/tap targets.
9. Save one representative desktop screenshot outside the commit.

### Step 4: Synchronize durable and task documentation

Update `PROJECT_MAP.md` with the v4 payload/UI and routine/fast-path ownership. Update the Overview runbook with routine versus bootstrap behavior and what `NO_EDGE` means. Keep root handoff logs to 3–5 concise lines and put commands/timings in the task `RUNS.md`.

Set task status to complete only after automated, actual performance, and Browser QA evidence is recorded. Leave any unreproduced changed-session measurement in `RISKS.md` rather than claiming it passed.

### Step 5: Review the complete diff

```bash
git status --short
git diff --stat
git diff --check
git diff -- app/web/overview/futures_macro_helpers.py \
  app/jobs/overview_actions.py app/jobs/ingestion_jobs.py \
  app/services/futures_macro_pattern_validation.py \
  app/services/futures_macro_snapshot.py \
  finance/data/futures_market.py finance/loaders/futures.py
```

Verify unrelated dirty files are absent from the staged set.

### Step 6: Commit the closeout unit

```bash
git add .aiworkspace/note/finance/docs/PROJECT_MAP.md \
  .aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md \
  .aiworkspace/note/finance/tasks/active/overview-futures-macro-short-horizon-v1-20260723
git commit -m "선물 매크로 단기 판단 개선 검증 정리"
```

## Final completion gate

The feature is complete only when all are true:

- v4 Python payload tests and TypeScript build pass;
- default UI follows the approved 1D -> 5D -> future 5D flow;
- all six families appear as core 4 + confirmation 2 from stored values;
- normal complete-coverage refresh uses 1y overlap, not all-symbol 10y;
- only deficient symbols use 10y bootstrap;
- unchanged completed-session input exits before macro/outlook builders;
- changed/incompatible input still rebuilds and persists exactly once;
- `NO_EDGE` suppression and latest-good/PIT contracts pass regressions;
- desktop and 420px Browser QA pass with one screenshot;
- actual timings and remaining gaps are recorded;
- documentation is synchronized and unrelated dirty files remain untouched.
