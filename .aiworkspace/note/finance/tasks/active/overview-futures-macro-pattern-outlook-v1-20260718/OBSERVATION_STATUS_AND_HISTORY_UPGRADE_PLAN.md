# Futures Macro Observation Status And History Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Separate completed current observations from conditional forecast confidence, backfill ten years of core futures daily data, and re-evaluate unchanged 5D / 20D publication gates from the persisted snapshot.

**Architecture:** The Python payload becomes explicit about two different state domains: `observation_status` for stored current facts and `estimate_status` for future distributions. One shared ten-year history constant drives provider collection, validation lookback, materialization, and UI copy; the daily ingestion job remains the only expensive refresh boundary and Overview remains a persisted-snapshot read path.

**Tech Stack:** Python 3.12, pandas, MySQL, yfinance, Streamlit component bridge, React 18, TypeScript, Vite, unittest.

## Global Constraints

- Current observation states are exactly `OBSERVED | PARTIAL | UNAVAILABLE`.
- Future estimate states remain exactly `VERIFIED | PROVISIONAL | UNAVAILABLE`.
- Provider daily history request is exactly `10y / 1d` for all 17 core futures symbols.
- Publication gates remain unchanged: 30 minimum episodes, 60 verified episodes, Brier baseline improvement, calibration error `<= 0.10`, fold improvement ratio `>= 0.60`, path median error baseline improvement, middle-50% coverage `0.35~0.65`, and at least two evaluated folds.
- Do not interpolate missing provider history, force status promotion, lower a gate, or add a separate forecast refresh button.
- Overview first entry and reload must continue reading one compatible persisted snapshot without provider fetch or pattern calculation.
- 5차 model changes are outside this plan; they require the actual Task 4 failure report as a new design input.

---

### Task 1: Split current observation status in the Python payload

**Files:**
- Modify: `app/web/overview/futures_macro_helpers.py`
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- Consumes: current pattern dictionaries with `status=READY | PARTIAL | other`.
- Produces: `_pattern_observation_status(pattern: dict[str, Any]) -> str`, hero `observation_status`, current horizon `observation_status`, and asset `observation_status` plus independent future horizon status fields.

- [ ] **Step 1: Write failing payload tests**

Extend `FuturesMacroThermometerContractTests.test_futures_macro_v2_payload_separates_current_and_future_horizons` with these assertions:

```python
current, five_day, twenty_day = payload["horizons"]
self.assertEqual(payload["hero"]["observation_status"], "OBSERVED")
self.assertEqual(current["observation_status"], "OBSERVED")
self.assertNotIn("estimate_status", current)
self.assertEqual(five_day["estimate_status"], "PROVISIONAL")
self.assertEqual(twenty_day["estimate_status"], "PROVISIONAL")
for pathway in payload["asset_pathways"]:
    self.assertEqual(pathway["observation_status"], "OBSERVED")
    self.assertEqual(pathway["outlook"]["five_day_status"], "PROVISIONAL")
    self.assertEqual(pathway["outlook"]["twenty_day_status"], "PROVISIONAL")
    self.assertNotIn("estimate_status", pathway)
```

Add a focused mapping test:

```python
def test_futures_macro_observation_status_distinguishes_ready_partial_and_missing(self) -> None:
    from app.web.overview.futures_macro_helpers import _pattern_observation_status

    self.assertEqual(_pattern_observation_status({"status": "READY"}), "OBSERVED")
    self.assertEqual(_pattern_observation_status({"status": "PARTIAL"}), "PARTIAL")
    self.assertEqual(_pattern_observation_status({"status": "UNAVAILABLE"}), "UNAVAILABLE")
    self.assertEqual(_pattern_observation_status({}), "UNAVAILABLE")
```

- [ ] **Step 2: Run tests and confirm RED**

Run:

```bash
.venv/bin/python -m unittest -v \
  tests.test_service_contracts.FuturesMacroThermometerContractTests.test_futures_macro_v2_payload_separates_current_and_future_horizons \
  tests.test_service_contracts.FuturesMacroThermometerContractTests.test_futures_macro_observation_status_distinguishes_ready_partial_and_missing
```

Expected: failures because `observation_status` and `_pattern_observation_status` do not exist and the current card still contains `estimate_status`.

- [ ] **Step 3: Implement the minimal status split**

Add the shared mapping and use it in hero, current horizon, and asset cards:

```python
def _pattern_observation_status(pattern: dict[str, Any]) -> str:
    status = str(pattern.get("status") or "UNAVAILABLE")
    if status == "READY":
        return "OBSERVED"
    if status in {"PARTIAL", "LIMITED"}:
        return "PARTIAL"
    return "UNAVAILABLE"
```

For asset outlooks, preserve horizon-specific statuses:

```python
"outlook": {
    "five_day": _pathway_outlook_label(five_day, pathway_key),
    "five_day_status": str(five_day.get("estimate_status") or "UNAVAILABLE"),
    "twenty_day": _pathway_outlook_label(twenty_day, pathway_key),
    "twenty_day_status": str(twenty_day.get("estimate_status") or "UNAVAILABLE"),
},
"observation_status": _pattern_observation_status(pattern),
```

Remove the card-wide minimum future status and do not add a compatibility `estimate_status` to current observations.

- [ ] **Step 4: Run focused and neighboring tests and confirm GREEN**

Run:

```bash
.venv/bin/python -m unittest -v \
  tests.test_service_contracts.FuturesMacroThermometerContractTests.test_futures_macro_v2_payload_separates_current_and_future_horizons \
  tests.test_service_contracts.FuturesMacroThermometerContractTests.test_futures_macro_observation_status_distinguishes_ready_partial_and_missing \
  tests.test_service_contracts.FuturesMacroThermometerContractTests.test_futures_macro_v2_payload_hides_unavailable_probabilities
```

Expected: three tests pass.

- [ ] **Step 5: Commit Task 1**

```bash
git add app/web/overview/futures_macro_helpers.py tests/test_service_contracts.py
git commit -m "선물 매크로 현재 관측 상태를 전망과 분리"
```

---

### Task 2: Render observation and horizon statuses independently in React

**Files:**
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/FuturesMacroWorkbench.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/MacroContextSection.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/PatternHorizonSection.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/AssetPathwaysSection.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/style.css`
- Modify: `tests/test_service_contracts.py`
- Rebuild: `app/web/streamlit_components/futures_macro_workbench/component_static/`

**Interfaces:**
- Consumes: Task 1 payload fields.
- Produces: typed observation badges and separate 5D / 20D estimate badges without changing probability or path geometry.

- [ ] **Step 1: Write failing React source-contract tests**

Add this test to `OverviewAutomationContractTests`:

```python
def test_futures_macro_react_separates_observation_and_outlook_statuses(self) -> None:
    root = Path("app/web/streamlit_components/futures_macro_workbench/src")
    types = (root / "FuturesMacroWorkbench.tsx").read_text(encoding="utf-8")
    context = (root / "MacroContextSection.tsx").read_text(encoding="utf-8")
    horizons = (root / "PatternHorizonSection.tsx").read_text(encoding="utf-8")
    assets = (root / "AssetPathwaysSection.tsx").read_text(encoding="utf-8")

    self.assertIn('type ObservationStatus = "OBSERVED" | "PARTIAL" | "UNAVAILABLE"', types)
    self.assertIn("observation_status", context)
    self.assertIn("관측 완료", context)
    self.assertIn('item.kind === "observation"', horizons)
    self.assertIn("five_day_status", assets)
    self.assertIn("twenty_day_status", assets)
    self.assertNotIn("item.estimate_status.toLowerCase()", assets)
```

- [ ] **Step 2: Run the source-contract test and confirm RED**

Run:

```bash
.venv/bin/python -m unittest -v \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_react_separates_observation_and_outlook_statuses
```

Expected: failure because the existing React types and asset card use one `EstimateStatus`.

- [ ] **Step 3: Implement discriminated status types and display labels**

Define:

```typescript
export type ObservationStatus = "OBSERVED" | "PARTIAL" | "UNAVAILABLE";
export type EstimateStatus = "VERIFIED" | "PROVISIONAL" | "UNAVAILABLE";
export const OBSERVATION_LABEL: Record<ObservationStatus, string> = {
  OBSERVED: "관측 완료",
  PARTIAL: "일부 관측",
  UNAVAILABLE: "관측 불가",
};
```

Make `HorizonCard` a discriminated union so observation cards contain only
`observation_status` and future cards contain only `estimate_status`. Update the hero to read
`observation_status`. Update asset payload typing to include `observation_status`,
`five_day_status`, and `twenty_day_status`.

Render asset outlook rows with separate status badges:

```tsx
<span>다음 5D <strong>{item.outlook.five_day}</strong><b>{item.outlook.five_day_status}</b></span>
<span>다음 20D <strong>{item.outlook.twenty_day}</strong><b>{item.outlook.twenty_day_status}</b></span>
```

Add `observation-*` and compact outlook badge rules in `style.css`; keep text visible so color is not the only signal.

- [ ] **Step 4: Run source tests and production build**

Run:

```bash
.venv/bin/python -m unittest -v \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_react_separates_observation_and_outlook_statuses \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_react_v2_renders_market_context_reading_order \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_react_v2_has_responsive_probability_and_unavailable_contract
cd app/web/streamlit_components/futures_macro_workbench && npm run build
```

Expected: three tests pass and Vite exits 0.

- [ ] **Step 5: Commit Task 2**

```bash
git add app/web/streamlit_components/futures_macro_workbench tests/test_service_contracts.py
git commit -m "선물 매크로 관측과 전망 배지를 독립 표시"
```

---

### Task 3: Use one ten-year daily-history contract

**Files:**
- Modify: `finance/data/futures_market.py`
- Modify: `app/jobs/overview_actions.py`
- Modify: `app/services/futures_macro_snapshot.py`
- Modify: `app/services/futures_macro_pattern_validation.py`
- Modify: `app/web/overview/futures_macro_helpers.py`
- Modify: `tests/test_futures_macro_snapshot.py`
- Modify: `tests/test_futures_macro_pattern_validation.py`
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- Produces: `FUTURES_MACRO_HISTORY_YEARS = 10`, `FUTURES_MACRO_DAILY_PERIOD = "10y"`, and a new pattern algorithm version.
- Preserves: existing collector, UPSERT, source-marker cache, and publication-gate functions.

- [ ] **Step 1: Write failing ten-year contract tests**

Add a daily action test that patches `overview_actions.run_collect_futures_ohlcv` and asserts:

```python
self.assertEqual(kwargs["period"], "10y")
self.assertEqual(kwargs["interval"], "1d")
self.assertEqual(tuple(kwargs["symbols"]), DEFAULT_CORE_FUTURES_SYMBOLS)
```

Add a materializer test whose `outlook_builder` records the requested years and assert it is `10`.
Update the algorithm-version test to expect `pattern_outlook_v3_empirical_path_10y`.

Add a source guard that verifies the gate constants remain:

```python
self.assertEqual(MIN_INDEPENDENT_EPISODES, 30)
self.assertEqual(VERIFIED_EPISODES, 60)
```

- [ ] **Step 2: Run the focused tests and confirm RED**

Run:

```bash
.venv/bin/python -m unittest -v \
  tests.test_service_contracts.OverviewAutomationContractTests.test_overview_futures_daily_refresh_requests_ten_years \
  tests.test_futures_macro_snapshot.FuturesMacroSnapshotServiceTests.test_default_materializer_builds_ten_year_outlook \
  tests.test_futures_macro_pattern_validation.FuturesMacroPatternPublicationTests.test_snapshot_publishes_empirical_path_algorithm_version
```

Expected: failures showing `5y`, `years=5`, and the previous algorithm version.

- [ ] **Step 3: Implement shared history constants and version invalidation**

In `finance/data/futures_market.py` add:

```python
FUTURES_MACRO_HISTORY_YEARS = 10
FUTURES_MACRO_DAILY_PERIOD = f"{FUTURES_MACRO_HISTORY_YEARS}y"
```

Use those constants in the Overview daily collector, materializer default builder, pattern loader default,
and command / trace copy. Change:

```python
PATTERN_ALGORITHM_VERSION = "pattern_outlook_v3_empirical_path_10y"
```

Do not modify any publication threshold or status function.

- [ ] **Step 4: Run all pattern, snapshot, and focused contract tests**

Run:

```bash
.venv/bin/python -m unittest -v \
  tests.test_futures_macro_pattern \
  tests.test_futures_macro_pattern_validation \
  tests.test_futures_macro_snapshot \
  tests.test_service_contracts.OverviewAutomationContractTests.test_overview_futures_daily_refresh_requests_ten_years \
  tests.test_service_contracts.FuturesMacroThermometerContractTests.test_futures_macro_v2_payload_separates_current_and_future_horizons
```

Expected: all selected tests pass with unchanged publication-boundary cases.

- [ ] **Step 5: Commit Task 3**

```bash
git add finance/data/futures_market.py app/jobs/overview_actions.py \
  app/services/futures_macro_snapshot.py app/services/futures_macro_pattern_validation.py \
  app/web/overview/futures_macro_helpers.py tests/test_futures_macro_snapshot.py \
  tests/test_futures_macro_pattern_validation.py tests/test_service_contracts.py
git commit -m "선물 매크로 일봉 검증 범위를 10년으로 확장"
```

---

### Task 4: Backfill actual daily data and re-evaluate unchanged gates

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718/RISKS.md`

**Interfaces:**
- Consumes: Task 3 `run_overview_futures_daily_ohlcv()` and persisted materializer.
- Produces: actual per-symbol coverage, compatible compact snapshot, and a gate-by-gate comparison report.

- [ ] **Step 1: Record the pre-backfill baseline**

Run a read-only query grouped by the 17 core symbols and record first date, latest date, row count, and missing symbols.
Record the current 5D / 20D episode counts and probability / path metrics from the persisted snapshot.

- [ ] **Step 2: Run the approved existing daily refresh**

Run:

```bash
.venv/bin/python - <<'PY'
from app.jobs.overview_actions import run_overview_futures_daily_ohlcv
print(run_overview_futures_daily_ohlcv())
PY
```

Expected: the existing job reports `10y / 1d` collection and materialized or partially materialized snapshot details. Preserve the prior snapshot if ingestion or materialization fails.

- [ ] **Step 3: Verify post-backfill DB coverage and snapshot compatibility**

Query the same per-symbol coverage and load `load_overview_futures_macro_materialized_snapshot()` in a fresh Python process.
Confirm the row uses `pattern_outlook_v3_empirical_path_10y`, has a current observation, and includes 5D / 20D horizons.

- [ ] **Step 4: Produce the unchanged-gate report**

For each horizon record:

```text
episodes
Brier vs baseline Brier
calibration error
fold improvement ratio
path median error vs baseline median error
middle-50% coverage
evaluated folds
probability status
path status
final estimate status
edge label
```

Classify every threshold as pass or fail without altering code. Add remaining failures to `RISKS.md` as the only eligible inputs to a future 5차 model design.

- [ ] **Step 5: Commit Task 4 evidence**

```bash
git add .aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718/RUNS.md \
  .aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718/NOTES.md \
  .aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718/RISKS.md
git commit -m "선물 매크로 10년 백필 검증 결과 기록"
```

---

### Task 5: Browser QA, full verification, and durable documentation sync

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718/RUNS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Modify only if stale: `.aiworkspace/note/finance/docs/architecture/overview-market-intelligence.md`
- Generate but do not stage: one desktop / mobile QA screenshot under `/Users/taeho/.codex/visualizations/`

**Interfaces:**
- Consumes: Tasks 1–4 code, built component, and actual compatible snapshot.
- Produces: verified user-facing workflow and concise durable handoff.

- [ ] **Step 1: Run the complete focused verification suite**

Run:

```bash
.venv/bin/python -m unittest -v \
  tests.test_futures_macro_pattern \
  tests.test_futures_macro_pattern_validation \
  tests.test_futures_macro_snapshot
.venv/bin/python -m unittest -v \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_react_v2_renders_market_context_reading_order \
  tests.test_service_contracts.OverviewAutomationContractTests.test_futures_macro_react_separates_observation_and_outlook_statuses \
  tests.test_service_contracts.OverviewAutomationContractTests.test_overview_futures_daily_refresh_requests_ten_years \
  tests.test_service_contracts.FuturesMacroThermometerContractTests.test_futures_macro_v2_payload_separates_current_and_future_horizons \
  tests.test_service_contracts.FuturesMacroThermometerContractTests.test_futures_macro_v2_payload_hides_unavailable_probabilities
.venv/bin/python -m py_compile \
  app/jobs/overview_actions.py \
  app/services/futures_macro_snapshot.py \
  app/services/futures_macro_pattern_validation.py \
  app/web/overview/futures_macro_helpers.py \
  finance/data/futures_market.py
git diff --check
```

Expected: every command exits 0.

- [ ] **Step 2: Run actual Browser QA**

Open Overview > Futures Macro from a fresh app process and verify:

1. Hero says `관측 완료`, not `PROVISIONAL`.
2. Current horizon says `관측 완료` and future horizons retain their own statuses.
3. Every asset card displays current status plus independent 5D and 20D statuses.
4. Observed graph anchors do not move when switching 5D / 20D.
5. Method and calculation trace disclosures open without clipping.
6. Desktop and 420px have no document-level horizontal overflow.
7. Browser console has zero errors.

Save one representative screenshot outside the repository and record its absolute path in `STATUS.md`.

- [ ] **Step 3: Synchronize task and durable docs**

Use `finance-doc-sync` to record:

- why current observation is not a forecast confidence state;
- that daily refresh requests ten years and first entry still reads a compact snapshot;
- actual gate results and any remaining 5차 candidate failures;
- roadmap state `1~4차 complete`, `5차 conditional/not started`.

Keep raw command output in `RUNS.md`; keep root handoff logs to 3–5 lines.

- [ ] **Step 4: Run final repository checks and commit closeout**

Run:

```bash
git status --short
git diff --check
git diff --stat HEAD
```

Verify the unrelated research folder and `.superpowers/` remain untracked and unstaged. Then commit only the closeout documents:

```bash
git add .aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718/STATUS.md \
  .aiworkspace/note/finance/tasks/active/overview-futures-macro-pattern-outlook-v1-20260718/RUNS.md \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "선물 매크로 관측 상태와 10년 검증 마무리"
```

If the architecture doc changed, include only that exact file in the same closeout commit.

## Plan Completion Check

- Every design requirement maps to Tasks 1–5.
- Current and future status types are never collapsed into one card-wide field.
- Ten-year history changes are isolated from publication-gate logic.
- Actual model improvement is intentionally excluded until the unchanged-gate report exists.
- No separate refresh button, provider fetch on tab entry, new DB table, or raw OHLCV browser payload is introduced.
