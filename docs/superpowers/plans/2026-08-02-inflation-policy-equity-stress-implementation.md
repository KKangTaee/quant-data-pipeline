# Inflation Policy Equity Stress Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert inflation-policy-yield paths into a conditional year-end S&P 500 level distribution using stored next-year EPS vintages, valuation-multiple responses, and an explicit user AI-profitability EPS assumption.

**Architecture:** Calibrate EPS and forward-multiple changes on point-in-time monthly/event panels, then apply them to each macro simulation path. Measured next-year EPS revisions and user AI uplift remain separate fields; the service presents associations and conditional ranges, never a deterministic index target or causal claim.

**Tech Stack:** Python 3.12, pandas, NumPy, existing S&P 500 valuation/EPS loaders, inflation-policy simulation artifacts, React/TypeScript, pytest, Vitest, Browser QA.

## Global Constraints

- S&P 500 6,400 is accepted only as a user target scenario; it cannot appear as a constant in model code.
- `Index level = forward EPS × forward multiple` remains an identity; the distributions of both inputs are visible.
- AI profitability is a user EPS uplift assumption unless a stored EPS revision is measured. Label the two separately.
- Do not claim rate changes caused an equity move; event-study output is conditional association.
- Do not emit buy/sell, target-price, or portfolio-allocation instructions.
- Equity failure cannot change inflation, policy, yield, or recession probabilities.
- The official `sp500_index_earnings` release vintages and stored joint macro paths are hard gates. Shiller trailing EPS or current revised data cannot fill either gap.
- Historical labels use the same calendar-year-end horizon as the workbench; `months_to_year_end` remains an explicit feature.

---

## File Structure

### Create

- `finance/inflation_policy_equity_stress.py`: PIT calibration and conditional index simulation.
- `tests/test_inflation_policy_equity_stress.py`
- `app/web/streamlit_components/economic_cycle_workbench/src/EquityStressPanel.tsx`

### Modify

- `finance/loaders/inflation_policy.py`: load official EPS vintages and stored S&P 500 prices through a DB-only boundary.
- `finance/data/db/schema.py`: add the independent `equity_json` snapshot field.
- `finance/data/inflation_policy_results.py`: validate and persist `equity_json`.
- `finance/inflation_policy_pipeline.py`: attach independently gated equity stress.
- `app/services/overview/inflation_policy.py`: adapt equity section without affecting other sections.
- `app/services/overview/inflation_policy_commands.py`: accept bounded equity target/AI uplift reverse scenarios.
- `app/web/streamlit_components/economic_cycle_workbench/src/inflationPolicyTypes.ts`
- `app/web/streamlit_components/economic_cycle_workbench/src/InflationPolicyWorkbench.tsx`
- `app/web/streamlit_components/economic_cycle_workbench/src/ReverseScenarioPanel.tsx`
- `app/web/streamlit_components/economic_cycle_workbench/src/InflationPolicyWorkbench.test.tsx`
- `.aiworkspace/note/finance/tasks/active/inflation-policy-equity-stress/`
- `.aiworkspace/note/finance/phases/active/inflation-policy-yield-path/{TASKS,STATUS,RISKS}.md`

## Stable Interfaces

```python
@dataclass(frozen=True)
class EquityStressResult:
    as_of_at: str
    index_quantiles: dict[str, float]
    eps_quantiles: dict[str, float]
    multiple_quantiles: dict[str, float]
    threshold_probabilities: dict[str, float]
    measured_next_year_eps_revision_pct: float | None
    user_ai_eps_uplift_pct: float
    publication_status: str
    reason_codes: tuple[str, ...]

def build_equity_calibration_panel(*, price_rows: Sequence[Mapping[str, object]], eps_rows: Sequence[Mapping[str, object]], yield_rows: Sequence[Mapping[str, object]], as_of_at: str) -> pd.DataFrame: ...
def fit_equity_stress_model(panel: pd.DataFrame) -> EquityStressArtifact: ...
def simulate_equity_stress(artifact: EquityStressArtifact, forward_paths: Sequence[SimulationPath], *, current_index: float, forward_eps: float, user_ai_eps_uplift_pct: float = 0.0, target_levels: Sequence[float] = ()) -> EquityStressResult: ...
```

### Task 1: Build the DB-only PIT EPS and multiple panel

**Files:**
- Modify: `finance/loaders/inflation_policy.py`
- Create: `finance/inflation_policy_equity_stress.py`
- Create: `tests/test_inflation_policy_equity_stress.py`
- Create: `.aiworkspace/note/finance/tasks/active/inflation-policy-equity-stress/{PLAN,DESIGN,STATUS,NOTES,RUNS,RISKS}.md`

**Interfaces:**
- Consumes: `sp500_index_earnings`, monthly valuation rows, stored yield observations.
- Produces: one row per PIT origin with current index, forward EPS known then, measured revision, forward multiple, real yield, DGS10, breakeven, and future outcomes.

- [x] **Step 1: Write failing look-ahead tests**

```python
def test_eps_estimate_released_after_origin_is_excluded() -> None:
    panel = build_equity_calibration_panel(
        price_rows=price_fixture(),
        eps_rows=eps_fixture_with_next_release(),
        yield_rows=yield_fixture(),
        as_of_at="2026-06-17T18:00:00+00:00",
    )
    assert panel.iloc[-1]["eps_source_release_date"] <= "2026-06-17"
    assert panel.iloc[-1]["forward_eps"] == pytest.approx(known_eps_before_sep())
```

- [x] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_equity_stress.py -q
```

Expected: FAIL on missing module/panel builder.

- [x] **Step 3: Implement as-of matching**

Select the latest EPS release at or before each monthly origin for the four quarters of the next calendar year, calculate revision only between two releases both known at the origin, and align index/yield by latest prior trading day. The label is the same-year December endpoint and keeps `months_to_year_end` explicit. Missing next-year EPS yields `NOT_AVAILABLE`, not trailing-EPS substitution.

- [x] **Step 4: Run tests and commit**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_equity_stress.py tests/test_sp500_valuation.py -q
git add finance/loaders/inflation_policy.py finance/inflation_policy_equity_stress.py \
  tests/test_inflation_policy_equity_stress.py \
  .aiworkspace/note/finance/tasks/active/inflation-policy-equity-stress
git commit -m "주식 스트레스 PIT 패널 추가"
```

### Task 2: Fit and validate conditional EPS/multiple responses

**Files:**
- Modify: `finance/inflation_policy_equity_stress.py`
- Modify: `tests/test_inflation_policy_equity_stress.py`

**Interfaces:**
- Produces:

```python
@dataclass(frozen=True)
class EquityStressArtifact:
    model_version: str
    eps_response: dict[str, float]
    multiple_response: dict[str, float]
    joint_residuals: tuple[tuple[float, float], ...]
    validation_metrics: dict[str, float]
    trained_through: str
    publication_status: str
    reason_codes: tuple[str, ...]

def rolling_origin_validate_equity_stress(panel: pd.DataFrame, *, minimum_origins: int = 60) -> ValidationReport: ...
```

- [ ] **Step 1: Write failing identity, residual, and gate tests**

Test every simulated index equals EPS × multiple, joint residual sampling preserves EPS/multiple correlation, no random split, and a model worse than constant EPS/multiple baseline becomes `LIMITED`.

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_equity_stress.py -q
```

Expected: FAIL on missing fit/validation behavior.

- [ ] **Step 3: Implement conditional response calibration**

Fit regularized changes in next-year EPS and forward multiple against inflation state, policy repricing, DGS10/real-yield/breakeven changes, and recession input only when the recession component is independently `READY`. Resample paired EPS/multiple residuals so the joint relationship is retained.

- [ ] **Step 4: Implement chronological validation**

Compare index-distribution error/coverage against constant EPS, constant multiple, and historical unconditional-change baselines. Store event windows as associations with pre-event expectations; do not assign causal coefficients in copy or artifact names.

- [ ] **Step 5: Run tests and commit**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_equity_stress.py -q
git add finance/inflation_policy_equity_stress.py tests/test_inflation_policy_equity_stress.py
git commit -m "조건부 주식 스트레스 모델 추가"
```

### Task 3: Add AI EPS assumption and target-level reverse decomposition

**Files:**
- Modify: `finance/inflation_policy_equity_stress.py`
- Modify: `app/services/overview/inflation_policy_commands.py`
- Modify: `tests/test_inflation_policy_equity_stress.py`
- Modify: `tests/test_inflation_policy_commands.py`

**Interfaces:**
- Consumes: measured next-year EPS revision and user `user_ai_eps_uplift_pct`.
- Produces: target-level probability and required EPS/multiple combinations.

- [ ] **Step 1: Write failing separation and no-hardcode tests**

```python
def test_measured_revision_and_ai_assumption_are_separate() -> None:
    result = simulate_equity_stress(
        ready_equity_artifact(), forward_paths_fixture(),
        current_index=6800.0, forward_eps=300.0,
        user_ai_eps_uplift_pct=5.0, target_levels=[6400.0],
    )
    assert result.user_ai_eps_uplift_pct == 5.0
    assert result.measured_next_year_eps_revision_pct == pytest.approx(measured_revision_fixture())
    assert "6400" not in Path("finance/inflation_policy_equity_stress.py").read_text()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_equity_stress.py tests/test_inflation_policy_commands.py -q
```

Expected: FAIL on missing fields/command support.

- [ ] **Step 3: Implement bounded scenario inputs**

Allow AI uplift from `-30%` to `+50%` and positive target levels. Apply uplift only to forward EPS, leave measured revision unchanged, and return target probability plus weighted EPS/multiple quantiles among matching paths. Label result `USER_ASSUMPTION`.

- [ ] **Step 4: Run tests and commit**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_equity_stress.py tests/test_inflation_policy_commands.py -q
git add finance/inflation_policy_equity_stress.py app/services/overview/inflation_policy_commands.py \
  tests/test_inflation_policy_equity_stress.py tests/test_inflation_policy_commands.py
git commit -m "AI EPS 가정과 지수 역산 시나리오 추가"
```

### Task 4: Integrate the independently gated result and UI

**Files:**
- Modify: `finance/inflation_policy_pipeline.py`
- Modify: `finance/data/db/schema.py`
- Modify: `finance/data/inflation_policy_results.py`
- Modify: `app/services/overview/inflation_policy.py`
- Create: `app/web/streamlit_components/economic_cycle_workbench/src/EquityStressPanel.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/inflationPolicyTypes.ts`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/InflationPolicyWorkbench.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/ReverseScenarioPanel.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/InflationPolicyWorkbench.test.tsx`

**Interfaces:**
- Consumes: `EquityStressResult` or null.
- Produces: a conditional equity card and reverse target form without altering other probability sections.

- [ ] **Step 1: Write failing service/UI isolation tests**

Test equity `FAILED` maps to an unavailable equity section while inflation/policy/rates remain unchanged. React test checks `측정된 EPS 수정` and `사용자 AI 수익화 가정` labels and conditional-association disclosure.

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_pipeline.py tests/test_inflation_policy_service.py -q
npm --prefix app/web/streamlit_components/economic_cycle_workbench test
```

Expected: FAIL on missing integration.

- [ ] **Step 3: Integrate pipeline/service**

Fit/materialize equity after macro forward paths. Store equity in the independent `equity_json` snapshot field; an equity exception records unavailable equity and still permits the macro snapshot when its own gates pass.

- [ ] **Step 4: Implement the panel**

Show index range, EPS range, multiple range, user target probability, and assumption provenance. Use `조건부 스트레스` and `연관 분석`; exclude `목표가`, `매수`, `매도`.

- [ ] **Step 5: Run tests/build and commit**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_equity_stress.py tests/test_inflation_policy_pipeline.py tests/test_inflation_policy_service.py -q
npm --prefix app/web/streamlit_components/economic_cycle_workbench test
npm --prefix app/web/streamlit_components/economic_cycle_workbench run build
git add finance/inflation_policy_pipeline.py app/services/overview/inflation_policy.py \
  app/web/streamlit_components/economic_cycle_workbench/src/EquityStressPanel.tsx \
  app/web/streamlit_components/economic_cycle_workbench/src/inflationPolicyTypes.ts \
  app/web/streamlit_components/economic_cycle_workbench/src/InflationPolicyWorkbench.tsx \
  app/web/streamlit_components/economic_cycle_workbench/src/ReverseScenarioPanel.tsx \
  app/web/streamlit_components/economic_cycle_workbench/src/InflationPolicyWorkbench.test.tsx \
  app/web/streamlit_components/economic_cycle_workbench/component_static
git commit -m "주식시장 조건부 스트레스 화면 연결"
```

### Task 5: Complete validation, Browser QA, and documentation

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/inflation-policy-equity-stress/{STATUS,NOTES,RUNS,RISKS}.md`
- Modify: `.aiworkspace/note/finance/phases/active/inflation-policy-yield-path/{TASKS,STATUS,RISKS}.md`
- Modify: `.aiworkspace/note/finance/docs/flows/README.md`

**Interfaces:**
- Consumes: verified equity engine/service/UI.
- Produces: truthful phase-five handoff.

- [ ] **Step 1: Run complete automated verification**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_equity_stress.py tests/test_inflation_policy_commands.py tests/test_inflation_policy_pipeline.py tests/test_inflation_policy_service.py -q
npm --prefix app/web/streamlit_components/economic_cycle_workbench test
npm --prefix app/web/streamlit_components/economic_cycle_workbench run build
git diff --check
```

Expected: all pass.

- [ ] **Step 2: Run Browser QA**

Verify default/no-AI assumption, positive/negative uplift, user target 6,400, unavailable EPS, mobile wrapping, and zero console/page errors. Capture one generated screenshot outside the commit.

- [ ] **Step 3: Use `finance-doc-sync`, update states, and commit**

Keep phase active for the recession plan. Record equity validation status; do not mark a `LIMITED` artifact as successful probability validation.

```bash
git add .aiworkspace/note/finance/tasks/active/inflation-policy-equity-stress \
  .aiworkspace/note/finance/phases/active/inflation-policy-yield-path \
  .aiworkspace/note/finance/docs/flows/README.md
git commit -m "주식 스트레스 단계 검증 기록"
```
