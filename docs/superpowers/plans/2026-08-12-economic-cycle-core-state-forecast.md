# Economic Cycle Core State And Transition Forecast Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build one long-history point-in-time core state, two episode-safe transition models, and a chronological publication gate; connect persistence/service/UI only when actual data passes.

**Architecture:** Keep canonical state, episode dataset, model fitting, and validation in four independent finance modules. Reuse the source-isolated RTDSM DB loader, treat NBER as semantic audit only, and keep the recent eight-indicator panel as a non-model corroboration layer. Research execution is side-effect free until all publication gates pass.

**Tech Stack:** Python 3.12, pandas, NumPy, MySQL loaders already in the repository, pytest, existing Streamlit-free service and React/Vitest workbench if publication is allowed.

## Global Constraints

- Use the same RTDSM core-state definition for every historical and current origin.
- Do not require parity with the old eight-indicator phase label.
- Do not use NBER chronology as a four-class label or model feature.
- Do not use random row splits; hold out complete phase episodes chronologically.
- Normalize monthly training weights so each phase episode has total weight one.
- Do not add scikit-learn or another machine-learning dependency.
- Do not publish fallback, heuristic, or uncalibrated probabilities.
- Do not modify asset checkpoint calculations, payload fields, markup, or styling.
- Stop forecast fitting when the core-state gate fails.
- Stop persistence/service/UI probability work when either model gate fails.

---

### Task 1: Canonical Core Feature Panel And Semantic Gate

**Files:**
- Create: `finance/economic_cycle_core_state.py`
- Modify: `finance/economic_cycle_realtime_history.py`
- Test: `tests/test_economic_cycle_core_state.py`
- Test: `tests/test_economic_cycle_realtime_history.py`

**Interfaces:**
- Consumes: `build_rtdsm_monthly_panel(vintage_rows, forecast_origins, minimum_history_months=60, vintage_lag_months=0)` and `build_rtdsm_observed_history(panel)`.
- Produces: `build_core_feature_panel(panel: pd.DataFrame) -> pd.DataFrame`, `CoreStateGate`, `CoreStateAuditReport`, and `evaluate_core_state_gate(core_panel, core_history, revised_history, nber_months, sample_report, gate=DEFAULT_CORE_STATE_GATE) -> CoreStateAuditReport`.

- [ ] **Step 1: Write a failing vintage-lag test**

Add a test proving that `vintage_lag_months=1` selects the version known one month-end later while still restricting observations to the original forecast origin.

```python
revised = build_rtdsm_monthly_panel(
    _vintage_rows(),
    forecast_origins=["2020-01-31"],
    minimum_history_months=2,
    vintage_lag_months=1,
)
assert revised.loc[0, "EMPLOY_signal"] > realtime.loc[0, "EMPLOY_signal"]
assert revised.loc[0, "EMPLOY_latest_observation_date"] == "2020-01-01"
```

- [ ] **Step 2: Verify the lag test fails for the missing keyword**

Run: `.venv/bin/python -m pytest -q tests/test_economic_cycle_realtime_history.py -k vintage_lag`

Expected: FAIL because `build_rtdsm_monthly_panel()` does not accept `vintage_lag_months`.

- [ ] **Step 3: Implement lagged vintage selection without observation look-ahead**

Selection timestamp is `forecast_origin + MonthEnd(vintage_lag_months)`; the signal observation cutoff remains `forecast_origin.to_period("M")`. Staleness remains measured against the original forecast origin.

- [ ] **Step 4: Write failing core-panel and audit tests**

Cover:

```python
panel = build_core_feature_panel(rtdsm_panel)
assert {"level", "momentum", "level_change_1m", "momentum_change_6m", "phase_duration"} <= set(panel)

report = evaluate_core_state_gate(
    panel,
    history,
    revised_history,
    nber_months={"2001-03-31": True, "2001-04-30": True},
    sample_report=_passing_sample_report(),
    gate=_permissive_gate(),
)
assert report.status == "READY"
```

Add separate assertions for reason codes: `PHASE_OCCUPANCY`, `ONE_MONTH_EPISODES`, `REVISION_PHASE_INSTABILITY`, `REVISION_SIDE_INSTABILITY`, `NBER_RECESSION_SEMANTICS`, `NBER_PEAK_CAPTURE`, `NBER_TROUGH_CAPTURE`, and `SAMPLE_GATE_FAILED`.

- [ ] **Step 5: Verify the core-state tests fail because the module is absent**

Run: `.venv/bin/python -m pytest -q tests/test_economic_cycle_core_state.py`

Expected: FAIL on missing `finance.economic_cycle_core_state`.

- [ ] **Step 6: Implement the minimal core panel and audit**

`build_core_feature_panel()` copies the source panel and adds finite values only:

```python
raw_level = 0.5 * activity_score + 0.5 * labor_income_score
level = raw_level.rolling(3, min_periods=3).mean()
momentum = level.diff(3)
dispersion = (activity_score - labor_income_score).abs()
breadth = (IPT_z.ge(0) + H_z.ge(0) + EMPLOY_z.ge(0) + RUC_z.ge(0)) / 4
```

Add one/three/six-release differences, raw phase, and contiguous raw phase duration. Audit NBER peaks on `False -> True` and troughs on `True -> False`; do not pass NBER fields into the core panel.

- [ ] **Step 7: Run the focused Task 1 tests**

Run: `.venv/bin/python -m pytest -q tests/test_economic_cycle_realtime_history.py tests/test_economic_cycle_core_state.py`

Expected: PASS.

- [ ] **Step 8: Commit Task 1**

```bash
git add finance/economic_cycle_realtime_history.py finance/economic_cycle_core_state.py tests/test_economic_cycle_realtime_history.py tests/test_economic_cycle_core_state.py
git commit -m "모델: 경제사이클 장기 핵심 국면 gate 구현"
```

### Task 2: Episode-Normalized Transition Dataset

**Files:**
- Create: `finance/economic_cycle_transition_dataset.py`
- Test: `tests/test_economic_cycle_transition_dataset.py`

**Interfaces:**
- Consumes: canonical core feature panel and raw `ObservedStateResult` history.
- Produces: `TransitionDataset(feature_names: tuple[str, ...], rows: pd.DataFrame)` and `build_transition_dataset(panel, history, pressure_horizon_releases=3) -> TransitionDataset`.

- [ ] **Step 1: Write failing tests for confirmed episodes and unrestricted destinations**

Use a phase sequence containing `contraction -> slowdown`, `slowdown -> expansion`, and `expansion -> recovery`. Assert that no fixed next-phase rule removes any event.

```python
dataset = build_transition_dataset(panel, history, pressure_horizon_releases=3)
assert set(dataset.rows["destination_target"].dropna()) == {
    "slowdown", "expansion", "recovery"
}
```

- [ ] **Step 2: Write failing tests for pressure labels and known-at dates**

For an event confirmed at index 6, indices 3, 4, and 5 must have `pressure_target=1`; index 2 must have zero. Every row must have `target_known_at >= forecast_origin`, and validation may only train on rows with `target_known_at < scoring origin`.

- [ ] **Step 3: Write a failing episode-weight test**

```python
weight_sums = dataset.rows.groupby("episode_id")["episode_weight"].sum()
assert all(math.isclose(value, 1.0) for value in weight_sums)
```

- [ ] **Step 4: Verify all Task 2 tests fail because the module is absent**

Run: `.venv/bin/python -m pytest -q tests/test_economic_cycle_transition_dataset.py`

Expected: FAIL on missing module.

- [ ] **Step 5: Implement confirmed phase episodes and targets**

Anchor the first usable phase. Switch the confirmed phase only on the second consecutive observation of a candidate. Rows after the last event keep pressure labels only where the three-release window is fully observed; destination labels without a known future event remain null and are excluded from destination fitting.

The fixed feature tuple is:

```python
CORE_FORECAST_FEATURES = (
    "IPT_z", "H_z", "EMPLOY_z", "RUC_z",
    "activity_score", "labor_income_score", "level", "momentum",
    "level_change_1m", "level_change_3m", "level_change_6m",
    "momentum_change_1m", "momentum_change_3m", "momentum_change_6m",
    "activity_labor_dispersion", "positive_breadth", "phase_duration",
)
```

Add one-hot current phase columns inside the returned feature tuple. Drop rows with non-finite required features from model eligibility but retain them with `eligible=False` for audit counts.

- [ ] **Step 6: Run Task 2 tests**

Run: `.venv/bin/python -m pytest -q tests/test_economic_cycle_transition_dataset.py`

Expected: PASS.

- [ ] **Step 7: Commit Task 2**

```bash
git add finance/economic_cycle_transition_dataset.py tests/test_economic_cycle_transition_dataset.py
git commit -m "모델: 경제사이클 episode 전환 dataset 구현"
```

### Task 3: Deterministic Weighted Logistic Models

**Files:**
- Create: `finance/economic_cycle_transition_model.py`
- Test: `tests/test_economic_cycle_transition_model.py`

**Interfaces:**
- Produces: `TransitionModelArtifact`, `fit_binary_logit()`, `fit_multinomial_logit()`, `predict_binary_probability()`, `predict_destination_probabilities()`, `fit_platt_scaler()`, and `fit_multiclass_temperature()`.
- Uses only NumPy arrays derived from finite pandas rows; no external ML package.

- [ ] **Step 1: Write failing binary model tests**

Assert weighted separable data ranks the positive example above the negative one, repeated fitting is byte-equivalent after serialization, and missing features raise `ModelNotReadyError`.

- [ ] **Step 2: Write failing multinomial tests**

Use four synthetic clusters and assert the predicted distribution contains exactly `recovery/expansion/slowdown/contraction`, is finite, sums to one, and excludes the supplied current phase after conditional renormalization.

- [ ] **Step 3: Write failing calibration tests**

Overconfident wrong binary predictions must produce a Platt slope/intercept that do not worsen log loss. Overconfident wrong multiclass predictions must choose a temperature above one and not worsen log loss.

- [ ] **Step 4: Verify Task 3 tests fail because the module is absent**

Run: `.venv/bin/python -m pytest -q tests/test_economic_cycle_transition_model.py`

Expected: FAIL on missing module.

- [ ] **Step 5: Implement finite weighted optimization**

Standardize each feature with weighted training mean and scale. Use a deterministic fixed iteration cap, gradient-norm tolerance, clipped logits, L2 coefficient penalty, and backtracking step reduction when weighted loss increases. Intercepts are not regularized. Return `LIMITED` with reason codes instead of a publishable artifact when classes or finite support are missing.

Artifacts store tuples/dicts only:

```python
@dataclass(frozen=True)
class TransitionModelArtifact:
    task: str
    feature_names: tuple[str, ...]
    classes: tuple[str, ...]
    means: dict[str, float]
    scales: dict[str, float]
    coefficients: dict[str, dict[str, float]]
    intercepts: dict[str, float]
    l2: float
    calibration: dict[str, float]
    publication_status: str
    reason_codes: tuple[str, ...]
```

- [ ] **Step 6: Run Task 3 tests**

Run: `.venv/bin/python -m pytest -q tests/test_economic_cycle_transition_model.py`

Expected: PASS with no optimization warnings.

- [ ] **Step 7: Commit Task 3**

```bash
git add finance/economic_cycle_transition_model.py tests/test_economic_cycle_transition_model.py
git commit -m "모델: 경제사이클 전환 확률 엔진 구현"
```

### Task 4: Chronological Episode Validation And Baselines

**Files:**
- Create: `finance/economic_cycle_transition_validation.py`
- Test: `tests/test_economic_cycle_transition_validation.py`

**Interfaces:**
- Consumes: `TransitionDataset` and Task 3 fit/predict functions.
- Produces: `TransitionValidationReport`, `TransitionPublicationDecision`, `run_transition_validation(dataset, initial_training_events=40)`, and `evaluate_transition_publication_gate(report)`.

- [ ] **Step 1: Write a failing leakage test**

For every prediction record assert:

```python
assert prediction.training_target_known_through < prediction.forecast_origin
assert prediction.training_episode_max < prediction.scoring_episode_id
```

- [ ] **Step 2: Write failing baseline-alignment tests**

The model, expanding global rate, phase-duration hazard, phase-conditioned destination frequency, and fixed-cycle destination must score the exact same OOS targets and weights.

- [ ] **Step 3: Write failing metric and gate tests**

Hand-check weighted binary and multiclass Brier/log loss/ECE. Create report fixtures that independently trigger:

- `INSUFFICIENT_PRESSURE_EVENTS`
- `PRESSURE_BASELINE_UNDERPERFORMANCE`
- `PRESSURE_CALIBRATION_ERROR`
- `INSUFFICIENT_DESTINATION_EVENTS`
- `INSUFFICIENT_DESTINATION_SUPPORT`
- `DESTINATION_BASELINE_UNDERPERFORMANCE`
- `DESTINATION_CALIBRATION_ERROR`
- `INVALID_PROBABILITIES`

The 2% skill requirement is `model_metric <= best_baseline_metric * 0.98` for both Brier and log loss.

- [ ] **Step 4: Verify Task 4 tests fail because the module is absent**

Run: `.venv/bin/python -m pytest -q tests/test_economic_cycle_transition_validation.py`

Expected: FAIL on missing module.

- [ ] **Step 5: Implement expanding episode folds**

Start scoring after 40 confirmed events. For each scoring episode, train only on rows whose target is known before its first origin. Select L2 from `(0.01, 0.1, 1.0, 10.0)` using the last 20% of eligible training episodes; refit the selected value on the full eligible training prefix. Fit calibration only on prior OOF rows, never on the current scoring episode.

- [ ] **Step 6: Implement baselines, metrics, and decisions**

Use Laplace smoothing for all baselines so no target gets zero probability. Return every support count, final-25% destination count, metric, baseline, calibration value, and reason code in the report.

- [ ] **Step 7: Run Task 4 tests**

Run: `.venv/bin/python -m pytest -q tests/test_economic_cycle_transition_validation.py`

Expected: PASS.

- [ ] **Step 8: Commit Task 4**

```bash
git add finance/economic_cycle_transition_validation.py tests/test_economic_cycle_transition_validation.py
git commit -m "검증: 경제사이클 episode OOS gate 구현"
```

### Task 5: Actual DB Experiment Orchestrator And Decision Checkpoint

**Files:**
- Create: `finance/economic_cycle_transition_experiment.py`
- Test: `tests/test_economic_cycle_transition_experiment.py`
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-core-state-forecast-v1-20260812/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-core-state-forecast-v1-20260812/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-core-state-forecast-v1-20260812/RISKS.md`

**Interfaces:**
- Produces: `run_transition_experiment(as_of_date, rtdsm_loader=..., nber_loader=...) -> TransitionExperimentReport`.
- The report includes source counts, `CoreStateAuditReport`, transition sample report, validation report when allowed, and combined `READY/NO_GO_CORE_STATE/NO_GO_MODEL`.

- [ ] **Step 1: Write failing orchestration tests**

Assert core-state failure does not call the supplied validation spy. Assert core-state pass calls validation once. Assert `NO_GO_MODEL` is returned when either model gate is limited. No writer is accepted by this research function.

- [ ] **Step 2: Verify orchestration tests fail**

Run: `.venv/bin/python -m pytest -q tests/test_economic_cycle_transition_experiment.py`

Expected: FAIL on missing module.

- [ ] **Step 3: Implement DB-only orchestration with injection seams**

Default loaders read the four RTDSM series from `macro_series_vintage_observation` and latest-revised `USREC` chronology from the existing economic-cycle loader. Build realtime and three-release-revised panels from identical origins. Do not write an artifact or snapshot.

- [ ] **Step 4: Run all new unit tests**

Run all five new test modules with `.venv/bin/python -m pytest -q`.

Expected: PASS.

- [ ] **Step 5: Run the actual DB experiment once**

```python
from finance.economic_cycle_transition_experiment import run_transition_experiment
report = run_transition_experiment("2026-07-31")
print(report.to_dict())
```

Record exact state-gate, event, OOS, baseline, calibration, and decision values in task `RUNS.md`.

- [ ] **Step 6: Apply the mandatory checkpoint**

- If status is `NO_GO_CORE_STATE`, stop Tasks 6 and 7. Keep current production phase/model/UI unchanged.
- If status is `NO_GO_MODEL`, allow only core-state documentation and a later separately reviewed current-state migration; do not persist or display probabilities.
- If status is `READY`, continue to Task 6.

- [ ] **Step 7: Commit Task 5**

```bash
git add finance/economic_cycle_transition_experiment.py tests/test_economic_cycle_transition_experiment.py .aiworkspace/note/finance/tasks/active/economic-cycle-core-state-forecast-v1-20260812
git commit -m "실험: 경제사이클 핵심 국면과 예측 gate 실행"
```

### Task 6: READY-Only Persistence And Current Materialization

**Conditional:** Execute only when Task 5 combined status is `READY`.

**Files:**
- Modify: `finance/data/economic_cycle_results.py`
- Modify: `finance/loaders/economic_cycle.py`
- Create: `finance/economic_cycle_transition_pipeline.py`
- Test: `tests/test_economic_cycle_results.py`
- Create: `tests/test_economic_cycle_transition_pipeline.py`

- [ ] **Step 1: Write failing persistence boundary tests**

Assert `LIMITED`/No-Go reports raise before writer invocation. Assert READY serialization preserves finite coefficients, calibration, core-state report, baseline metrics, and exact destination keys.

- [ ] **Step 2: Verify tests fail for missing pipeline**

Run the new pipeline and existing results tests.

- [ ] **Step 3: Implement new-version artifact and snapshot materialization**

Use the existing tables and keys; do not add a schema. Store destination and pressure payloads in existing JSON fields under `economic_cycle_transition_core_v1`. Preserve the current old snapshot until the READY write succeeds.

- [ ] **Step 4: Run Task 6 tests and actual materialization**

Run focused tests, materialize one `current` snapshot, and read it back through the DB loader.

- [ ] **Step 5: Commit Task 6**

```bash
git add finance/data/economic_cycle_results.py finance/loaders/economic_cycle.py finance/economic_cycle_transition_pipeline.py tests/test_economic_cycle_results.py tests/test_economic_cycle_transition_pipeline.py
git commit -m "파이프라인: 검증된 경제사이클 전환 snapshot 연결"
```

### Task 7: READY-Only Service And React Presentation

**Conditional:** Execute only when Task 5 and Task 6 are READY and actual snapshot readback passes.

**Files:**
- Modify: `app/services/overview/economic_cycle.py`
- Modify: `tests/test_economic_cycle_service.py`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.test.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/style.css`

- [ ] **Step 1: Write failing service contract tests**

Assert READY payload normalization, probability simplex, Korean copy defining the three-release window, and fail-closed omission on LIMITED snapshots. Snapshot source date and model version remain visible.

- [ ] **Step 2: Verify service tests fail**

Run the economic-cycle service tests filtered to `transition_outlook`.

- [ ] **Step 3: Implement the minimal service contract**

Add `transition_outlook` with pressure, destination paths, evidence, invalidation, and corroboration. Do not modify `build_market_implications()` or its returned items.

- [ ] **Step 4: Write and verify failing React tests**

Test current core phase, transition-pressure explanation, primary/alternative destinations, support/contradiction rows, and the unchanged `자산별 확인 포인트` cards.

- [ ] **Step 5: Implement presentation and responsive styling**

Replace only the current route/transition card region. Keep asset component calls and asset CSS selectors unchanged.

- [ ] **Step 6: Run Python, React, and production build verification**

Run the full economic-cycle service tests, component Vitest suite, and Vite production build.

- [ ] **Step 7: Run actual Browser QA and capture one screenshot**

Verify desktop and narrow layout, Data Freshness behavior, transition copy, and unchanged asset cards. Keep the screenshot untracked.

- [ ] **Step 8: Commit Task 7**

```bash
git add app/services/overview/economic_cycle.py tests/test_economic_cycle_service.py app/web/streamlit_components/economic_cycle_workbench/src app/web/streamlit_components/economic_cycle_workbench/component_static
git commit -m "UI: 검증된 경제사이클 전환 경로 표시"
```

### Task 8: Regression, Documentation, And Closeout

**Files:**
- Modify only canonical docs whose current facts changed.
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/researches/active/2026-08-economic-cycle-independent-reaudit/RECOMMENDATION.md`
- Modify: task `STATUS.md`, `NOTES.md`, `RUNS.md`, and `RISKS.md`.

- [ ] **Step 1: Run focused economic-cycle regression**

Run all `tests/test_economic_cycle*.py`, `tests/test_market_context_economic_cycle.py`, and new transition tests. Record the exact count.

- [ ] **Step 2: Run static checks**

Run `py_compile` on every new module and `git diff --check`.

- [ ] **Step 3: Synchronize only changed canonical facts**

Record `READY`, `NO_GO_CORE_STATE`, or `NO_GO_MODEL`. Do not claim a forecast exists when the gate stopped before persistence/UI. Preserve user registry, run history, generated artifacts, and existing QA images.

- [ ] **Step 4: Commit closeout documentation**

Commit only the changed canonical, research, and task documents.

- [ ] **Step 5: Report whole-roadmap position**

State which of the four implementation stages completed, the stopping gate if any, actual model/baseline metrics, commits, and whether the product UI changed.
