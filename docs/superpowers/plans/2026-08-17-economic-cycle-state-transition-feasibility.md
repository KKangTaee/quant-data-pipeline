# Economic Cycle State And Transition Feasibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 현재 국면을 2-release confirmed state로 안정화하고, 정책·물가·금리·신용·시장기대 driver가 다음 국면 전환의 pressure와 destination을 실제 Point-in-Time 역사에서 예측할 수 있는지 read-only로 판정한다.

**Architecture:** RTDSM raw history를 한 번만 confirmed-state frame으로 바꾸고 state audit와 transition target이 같은 frame을 사용한다. 기존 deterministic chronological validation을 core-only, required extended driver, optional market shadow dataset에 각각 실행하고 paired common-origin skill까지 확인한 뒤 `GO / LIMITED_GO / NO_GO`를 반환한다. Production DB writer, Overview service와 React UI는 호출하지 않는다.

**Tech Stack:** Python 3, pandas, NumPy, MySQL read-only loaders, pytest, Markdown task/research records

## Global Constraints

- 모든 macro 값은 `known_at <= forecast_origin`을 만족한다.
- 최초 official phase와 이후 transition은 동일 raw candidate가 2 usable release 연속일 때 두 번째 release에서만 확정한다.
- missing release는 candidate streak를 끊고 transition을 소급하지 않는다.
- fixed `recovery -> expansion -> slowdown -> contraction` 순서를 target이나 model constraint로 사용하지 않는다.
- actual 결과를 본 뒤 target, feature group, confirmation count와 publication threshold를 변경하지 않는다.
- 1~3차는 read-only이며 provider fetch, DB write, production snapshot, service, React와 자산별 확인 포인트를 변경하지 않는다.
- Fiscal driver는 현재 승인된 long PIT source가 없으면 `NOT_TESTABLE`로 보고하고 heuristic flag를 만들지 않는다.

---

### Task 1: Canonical Two-Release Confirmed State

**Files:**
- Create: `finance/economic_cycle_confirmed_state.py`
- Create: `tests/test_economic_cycle_confirmed_state.py`
- Modify: `finance/economic_cycle_transition_dataset.py`
- Modify: `tests/test_economic_cycle_transition_dataset.py`

**Interfaces:**
- Consumes: `Sequence[ObservedStateResult]` raw RTDSM history
- Produces: `build_confirmed_state_frame(history, confirmation_releases=2) -> pandas.DataFrame`
- Produces: `build_confirmed_observed_history(state_frame) -> tuple[ObservedStateResult, ...]`
- Produces: `build_transition_dataset(..., confirmed_state_frame: pandas.DataFrame | None = None) -> TransitionDataset`

- [ ] **Step 1: Write the failing bootstrap and transition tests**

```python
def test_bootstrap_requires_two_matching_usable_releases() -> None:
    history = _history(("recovery", "expansion", "expansion"))
    rows = build_confirmed_state_frame(history).set_index("forecast_origin")
    assert pd.isna(rows.loc[pd.Timestamp("2000-01-31"), "confirmed_phase"])
    assert pd.isna(rows.loc[pd.Timestamp("2000-02-29"), "confirmed_phase"])
    assert rows.loc[pd.Timestamp("2000-03-31"), "confirmed_phase"] == "expansion"
    assert rows.loc[pd.Timestamp("2000-03-31"), "confirmed_transition_to"] is None

def test_gap_resets_candidate_and_non_adjacent_transition_is_not_backdated() -> None:
    history = _history(("contraction", "contraction", "slowdown", None, "slowdown", "slowdown"))
    rows = build_confirmed_state_frame(history).set_index("forecast_origin")
    assert rows.loc[pd.Timestamp("2000-03-31"), "candidate_streak"] == 1
    assert rows.loc[pd.Timestamp("2000-04-30"), "candidate_streak"] == 0
    assert rows.loc[pd.Timestamp("2000-05-31"), "confirmed_phase"] == "contraction"
    assert rows.loc[pd.Timestamp("2000-06-30"), "confirmed_phase"] == "slowdown"
```

- [ ] **Step 2: Run the new tests and verify RED**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_confirmed_state.py -q`

Expected: FAIL because `finance.economic_cycle_confirmed_state` does not exist.

- [ ] **Step 3: Implement the confirmed-state frame and history adapter**

```python
@dataclass(frozen=True)
class ConfirmedStateColumns:
    raw_phase: str = "raw_phase"
    confirmed_phase: str = "confirmed_phase"
    candidate_phase: str = "candidate_phase"
    candidate_streak: str = "candidate_streak"

def build_confirmed_state_frame(
    history: Sequence[ObservedStateResult], *, confirmation_releases: int = 2
) -> pd.DataFrame:
    """Confirm bootstrap and every unrestricted destination without backdating."""
```

The frame must contain `forecast_origin`, `data_status`, `raw_phase`,
`confirmed_phase`, `candidate_phase`, `candidate_streak`, `episode_id`,
`phase_duration`, `confirmed_transition_from`, and `confirmed_transition_to`.

- [ ] **Step 4: Run confirmed-state tests and verify GREEN**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_confirmed_state.py -q`

Expected: PASS.

- [ ] **Step 5: Write a failing dataset test proving no second confirmation pass**

```python
def test_dataset_consumes_supplied_confirmed_frame_without_second_confirmation() -> None:
    panel, history = _fixture(("recovery", "recovery", "expansion", "expansion", "expansion"))
    state = build_confirmed_state_frame(history)
    rows = build_transition_dataset(panel, history, confirmed_state_frame=state).rows
    transition = rows.loc[rows["confirmed_transition_to"] == "expansion"].iloc[0]
    assert transition["forecast_origin"] == pd.Timestamp("2000-04-30")
```

- [ ] **Step 6: Run the dataset test and verify RED**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_transition_dataset.py::test_dataset_consumes_supplied_confirmed_frame_without_second_confirmation -q`

Expected: FAIL because `confirmed_state_frame` is not accepted.

- [ ] **Step 7: Connect the canonical frame to the dataset**

Remove the private duplicate confirmation logic from the active path. Existing callers without
`confirmed_state_frame` build it once from `history`; v2 callers pass the audited frame directly.

- [ ] **Step 8: Run Task 1 regression tests**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_confirmed_state.py tests/test_economic_cycle_transition_dataset.py tests/test_economic_cycle_core_state.py -q`

Expected: PASS.

- [ ] **Step 9: Commit Task 1**

```bash
git add finance/economic_cycle_confirmed_state.py finance/economic_cycle_transition_dataset.py tests/test_economic_cycle_confirmed_state.py tests/test_economic_cycle_transition_dataset.py
git commit -m "모델: 경제사이클 2회 확인 공식 국면 구현"
```

### Task 2: Point-In-Time Transition Driver Panel

**Files:**
- Create: `finance/economic_cycle_transition_drivers.py`
- Create: `tests/test_economic_cycle_transition_drivers.py`

**Interfaces:**
- Consumes: ALFRED rows with `series_id`, `observation_date`, `released_at`, `value`
- Consumes: stored market rows with `provider_symbol` or `series_id`, observation timestamp and value
- Produces: `build_transition_driver_panel(vintage_rows, forecast_origins, market_rows=()) -> pandas.DataFrame`
- Produces: `extend_transition_dataset(base, feature_panel, feature_names) -> TransitionDataset`
- Produces: `audit_transition_driver_coverage(dataset, state_frame, required_features) -> DriverCoverageReport`

- [ ] **Step 1: Write failing PIT and transform tests**

```python
def test_driver_panel_uses_only_releases_known_at_each_origin() -> None:
    rows = [
        _vintage("DGS2", "2000-01-31", "2000-02-01T00:00:00Z", 5.0),
        _vintage("DGS2", "2000-01-31", "2000-04-01T00:00:00Z", 9.0),
        _vintage("DGS2", "2000-02-29", "2000-03-01T00:00:00Z", 4.0),
    ]
    panel = build_transition_driver_panel(rows, pd.to_datetime(["2000-02-29", "2000-04-30"]))
    assert panel.loc[0, "DGS2_level"] == 5.0
    assert panel.loc[1, "DGS2_level"] == 4.0

def test_core_pce_and_curve_features_are_contextual_not_single_sign_rules() -> None:
    panel = build_transition_driver_panel(_complete_rows(), _origins())
    assert {"PCEPILFE_3m_ann", "PCEPILFE_gap_2pct", "yield_curve_10y2y"} <= set(panel)
```

- [ ] **Step 2: Run driver tests and verify RED**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_transition_drivers.py -q`

Expected: FAIL because the driver module does not exist.

- [ ] **Step 3: Implement normalized monthly PIT feature generation**

```python
REQUIRED_DRIVER_SERIES = (
    "FEDFUNDS", "DGS2", "DFII10", "PCEPILFE", "T10YIE",
    "DGS10", "BAMLH0A0HYM2", "ANFCI", "PERMIT",
)

REQUIRED_DRIVER_FEATURES = (
    "FEDFUNDS_level", "FEDFUNDS_delta_3m",
    "DGS2_level", "DGS2_delta_3m",
    "DFII10_level", "DFII10_delta_3m",
    "PCEPILFE_3m_ann", "PCEPILFE_gap_2pct",
    "T10YIE_level", "T10YIE_delta_3m",
    "DGS10_level", "DGS10_delta_3m",
    "yield_curve_10y2y", "yield_curve_delta_3m",
    "BAMLH0A0HYM2_level", "BAMLH0A0HYM2_delta_3m",
    "ANFCI_level", "ANFCI_delta_3m",
    "PERMIT_change_6m_pct",
)
```

Daily observations are reduced to the latest known monthly observation. Level series receive
1/3/6-month deltas. PCE receives annualized 3-month log change and a 2% gap; permits receive
6-month percent change; the curve is `DGS10 - DGS2`.

- [ ] **Step 4: Run PIT feature tests and verify GREEN**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_transition_drivers.py -q`

Expected: the PIT and transform tests pass.

- [ ] **Step 5: Write failing dataset extension and coverage tests**

```python
def test_extended_dataset_keeps_core_rows_and_marks_missing_driver_rows_ineligible() -> None:
    extended = extend_transition_dataset(base_dataset, driver_panel, ("DGS2_level",))
    assert len(extended.rows) == len(base_dataset.rows)
    assert extended.rows.loc[0, "ineligible_reason"] == "MISSING_DRIVER_FEATURE"

def test_driver_coverage_counts_unique_transition_episodes() -> None:
    report = audit_transition_driver_coverage(extended, state_frame, ("DGS2_level",), gate=_small_gate())
    assert report.independent_transitions == 2
    assert report.status == "DRIVER_READY"
```

- [ ] **Step 6: Run extension tests and verify RED**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_transition_drivers.py -q`

Expected: FAIL because extension and audit functions are missing.

- [ ] **Step 7: Implement extension, episode weights and coverage report**

```python
@dataclass(frozen=True)
class DriverCoverageGate:
    minimum_usable_origins: int = 180
    minimum_independent_transitions: int = 48
    minimum_destination_events: int = 8
    minimum_holdout_destination_events: int = 2

@dataclass(frozen=True)
class DriverCoverageReport:
    status: str
    reason_codes: tuple[str, ...]
    usable_origins: int
    independent_transitions: int
    destination_counts: dict[str, int]
    holdout_destination_counts: dict[str, int]
    series_coverage: dict[str, dict[str, object]]
```

Recompute episode weights only over rows eligible for the selected model variant. Do not drop
audit rows and do not fill missing feature values.

- [ ] **Step 8: Run Task 2 tests**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_transition_drivers.py tests/test_economic_cycle_transition_dataset.py -q`

Expected: PASS.

- [ ] **Step 9: Commit Task 2**

```bash
git add finance/economic_cycle_transition_drivers.py tests/test_economic_cycle_transition_drivers.py
git commit -m "모델: 경제사이클 전환 PIT driver 패널 구현"
```

### Task 3: Variant And Paired Validation Decisions

**Files:**
- Create: `finance/economic_cycle_transition_comparison.py`
- Create: `tests/test_economic_cycle_transition_comparison.py`

**Interfaces:**
- Consumes: `TransitionValidationReport` for core and extended datasets
- Produces: `evaluate_task_gates(report) -> TransitionTaskDecision`
- Produces: `compare_common_origin_skill(core, extended) -> PairedSkillReport`

- [ ] **Step 1: Write failing task-specific gate tests**

```python
def test_task_gate_can_publish_pressure_without_destination() -> None:
    decision = evaluate_task_gates(_report(pressure_ready=True, destination_ready=False))
    assert decision.pressure_status == "READY"
    assert decision.destination_status == "LIMITED"
    assert decision.combined_status == "LIMITED"
```

- [ ] **Step 2: Run the task-gate test and verify RED**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_transition_comparison.py -q`

Expected: FAIL because the comparison module does not exist.

- [ ] **Step 3: Implement pressure and destination decisions using existing thresholds**

```python
@dataclass(frozen=True)
class TransitionTaskDecision:
    pressure_status: str
    pressure_reason_codes: tuple[str, ...]
    destination_status: str
    destination_reason_codes: tuple[str, ...]
    combined_status: str
```

Use the existing 2% baseline skill, ECE 0.10/0.12, event support and probability validity
contracts without changing thresholds.

- [ ] **Step 4: Run the task-gate tests and verify GREEN**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_transition_comparison.py -q`

Expected: task-specific decision tests pass.

- [ ] **Step 5: Write failing paired common-origin tests**

```python
def test_paired_skill_requires_both_pressure_and_destination_mean_improvement() -> None:
    report = compare_common_origin_skill(_core_report(), _extended_report())
    assert report.pressure_mean_relative_skill > 0
    assert report.destination_mean_relative_skill < 0
    assert report.status == "LIMITED"
```

- [ ] **Step 6: Run the paired test and verify RED**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_transition_comparison.py -q`

Expected: FAIL because paired comparison is missing.

- [ ] **Step 7: Implement common-origin metric pairing**

```python
@dataclass(frozen=True)
class PairedSkillReport:
    status: str
    reason_codes: tuple[str, ...]
    pressure_common_origins: int
    destination_common_origins: int
    pressure_mean_relative_skill: float
    destination_mean_relative_skill: float
```

Match predictions by `(scoring_episode_id, forecast_origin)`, calculate weighted Brier/log loss
for both variants on the same records, and average the two relative improvements per task.

- [ ] **Step 8: Run Task 3 tests**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_transition_comparison.py tests/test_economic_cycle_transition_validation.py -q`

Expected: PASS.

- [ ] **Step 9: Commit Task 3**

```bash
git add finance/economic_cycle_transition_comparison.py tests/test_economic_cycle_transition_comparison.py
git commit -m "검증: 경제사이클 모델별 공통구간 skill 비교"
```

### Task 4: Read-Only State And Transition Experiment

**Files:**
- Create: `finance/economic_cycle_state_transition_experiment.py`
- Create: `tests/test_economic_cycle_state_transition_experiment.py`

**Interfaces:**
- Consumes: RTDSM/NBER loaders, `load_inflation_policy_training_vintages`, stored market loaders
- Produces: `run_state_transition_feasibility(as_of_date, **injected_dependencies) -> StateTransitionFeasibilityReport`

- [ ] **Step 1: Write failing stop-boundary tests**

```python
def test_state_failure_stops_before_driver_and_model_work() -> None:
    report = run_state_transition_feasibility("2026-07-31", **_deps(state="NO_GO"))
    assert report.status == "NO_GO"
    assert report.core_validation is None
    assert report.extended_validation is None
    assert _calls == ["state"]

def test_driver_failure_runs_state_but_stops_before_model_fit() -> None:
    report = run_state_transition_feasibility("2026-07-31", **_deps(driver="SHADOW_ONLY"))
    assert report.status == "NO_GO"
    assert report.extended_validation is None
```

- [ ] **Step 2: Run experiment tests and verify RED**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_state_transition_experiment.py -q`

Expected: FAIL because the v2 experiment module does not exist.

- [ ] **Step 3: Implement staged orchestration and JSON-safe report**

```python
@dataclass(frozen=True)
class StateTransitionFeasibilityReport:
    status: str
    reason_codes: tuple[str, ...]
    as_of_date: str
    state_report: CoreStateAuditReport
    driver_report: DriverCoverageReport | None
    fiscal_status: str
    core_validation: TransitionValidationReport | None
    extended_validation: TransitionValidationReport | None
    shadow_validation: TransitionValidationReport | None
    core_decision: TransitionTaskDecision | None
    extended_decision: TransitionTaskDecision | None
    paired_skill: PairedSkillReport | None
```

The function accepts no writer. It builds raw and 3-release-revised RTDSM panels, confirms each
history once, evaluates confirmed sample/core state, loads required drivers only after state READY,
then runs core and extended validation only after `DRIVER_READY`.

- [ ] **Step 4: Run stop-boundary tests and verify GREEN**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_state_transition_experiment.py -q`

Expected: stop-boundary tests pass.

- [ ] **Step 5: Write failing GO/LIMITED_GO/NO_GO decision tests**

```python
def test_extended_ready_and_paired_ready_returns_go() -> None:
    report = run_state_transition_feasibility("2026-07-31", **_deps(all_ready=True))
    assert report.status == "GO"

def test_only_one_extended_task_ready_returns_limited_go() -> None:
    report = run_state_transition_feasibility("2026-07-31", **_deps(pressure_only=True))
    assert report.status == "LIMITED_GO"
```

- [ ] **Step 6: Run decision tests and verify RED**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_state_transition_experiment.py -q`

Expected: FAIL until final decision logic is present.

- [ ] **Step 7: Implement final decision and optional market shadow isolation**

`GO` requires confirmed state READY, `DRIVER_READY`, extended pressure+destination READY and paired
skill READY. Exactly one extended task READY becomes `LIMITED_GO`; state/driver failure or neither
task READY becomes `NO_GO`. Shadow market output never upgrades the final decision.

- [ ] **Step 8: Run Task 4 tests and current research regression**

Run: `.venv/bin/python -m pytest tests/test_economic_cycle_state_transition_experiment.py tests/test_economic_cycle_transition_experiment.py tests/test_economic_cycle_transition_validation.py -q`

Expected: PASS.

- [ ] **Step 9: Commit Task 4**

```bash
git add finance/economic_cycle_state_transition_experiment.py tests/test_economic_cycle_state_transition_experiment.py
git commit -m "실험: 경제사이클 상태·확장 전환 feasibility 연결"
```

### Task 5: Actual DB Run, Decision Record And Closeout

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-state-transition-feasibility-v2-20260817/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-state-transition-feasibility-v2-20260817/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-state-transition-feasibility-v2-20260817/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/economic-cycle-state-transition-feasibility-v2-20260817/RISKS.md`
- Modify: `.aiworkspace/note/finance/researches/active/2026-08-economic-cycle-independent-reaudit/RECOMMENDATION.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify only if implemented boundary changed: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`

**Interfaces:**
- Consumes: local MySQL stored RTDSM, macro vintage and market rows through read-only loaders
- Produces: actual `StateTransitionFeasibilityReport.to_dict()` evidence and user-facing GO decision

- [ ] **Step 1: Run the actual read-only experiment**

Run:

```bash
.venv/bin/python - <<'PY'
import json
from finance.economic_cycle_state_transition_experiment import run_state_transition_feasibility
report = run_state_transition_feasibility("2026-07-31")
print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2, default=str))
PY
```

Expected: one JSON-safe report with state, driver, core/extended/shadow and final decision; no DB write.

- [ ] **Step 2: Record exact counts, metrics and stop reason**

Update task `RUNS.md` with commands and metrics, `NOTES.md` with the interpretation, `RISKS.md` with
remaining evidence gaps, and `STATUS.md` with `State: complete` only when all 1~3차 acceptance
conditions have been evaluated.

- [ ] **Step 3: Align research recommendation and roadmap**

Record the actual `GO / LIMITED_GO / NO_GO`, what 4·5차 may implement, and that production UI/assets
were unchanged. Update Project Map only if a new durable research ownership boundary was implemented.

- [ ] **Step 4: Run focused and full economic-cycle verification**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_economic_cycle_confirmed_state.py \
  tests/test_economic_cycle_transition_dataset.py \
  tests/test_economic_cycle_transition_drivers.py \
  tests/test_economic_cycle_transition_comparison.py \
  tests/test_economic_cycle_state_transition_experiment.py \
  tests/test_economic_cycle_core_state.py \
  tests/test_economic_cycle_transition_validation.py \
  tests/test_economic_cycle_transition_experiment.py -q
git diff --check
git diff --name-only HEAD~4..HEAD -- app/services/overview app/web finance/economic_cycle_asset_pathways.py finance/loaders/economic_cycle_assets.py
```

Expected: tests pass, no whitespace errors, and the production/UI/asset command prints no paths.

- [ ] **Step 5: Commit Task 5**

```bash
git add .aiworkspace/note/finance/tasks/active/economic-cycle-state-transition-feasibility-v2-20260817 .aiworkspace/note/finance/researches/active/2026-08-economic-cycle-independent-reaudit/RECOMMENDATION.md .aiworkspace/note/finance/docs/ROADMAP.md .aiworkspace/note/finance/docs/PROJECT_MAP.md
git commit -m "문서: 경제사이클 1~3차 실제 판정 정렬"
```
