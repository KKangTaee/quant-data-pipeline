# Inflation Policy Core Engines Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce calibrated Core PCE, FOMC policy, dynamic Treasury resistance, and forward/reverse conditional-path artifacts from the strict point-in-time data bundle.

**Architecture:** Implement a new `finance/inflation_policy/` package with no dependency on existing economic-cycle modules. The inflation engine combines an interpretable bridge and a regularized statistical forecast; the policy engine combines reaction-function, anonymous SEP, historical-decision, and optional market priors; yield resistance and scenario simulation are separate components joined only in the materialization pipeline.

**Tech Stack:** Python 3.12, pandas, NumPy, standard-library math/dataclasses, deterministic seeded bootstrap, MySQL result stores, pytest-style tests.

## Global Constraints

- No import path beginning `finance.economic_cycle` is allowed under `finance/inflation_policy/`.
- Core PCE source of truth is index level; monthly rates and `Q4/Q4` are derived.
- A one-month 0.4–0.5% print updates a distribution; it never returns a direct hike boolean.
- Rate-dot and Core PCE distributions remain marginal distributions; no participant joint is synthesized.
- DGS10 decomposition uses two separate lenses: policy/term-premium and real-yield/breakeven. Never sum both lenses together.
- Pivot highs become usable on their confirmation date, not their historical pivot date.
- Forward and reverse results are conditional distributions; exact probabilities require `READY` validation.

---

## File Structure

### Create

- `finance/inflation_policy/__init__.py`: narrow public exports.
- `finance/inflation_policy/contracts.py`: enums and immutable artifacts/results.
- `finance/inflation_policy/probability.py`: simplex, empirical quantiles, seeded bootstrap, and score utilities.
- `finance/inflation_policy/pce_path.py`: index math, scenario paths, five-state mapping.
- `finance/inflation_policy/panel.py`: point-in-time feature and target panels.
- `finance/inflation_policy/inflation_model.py`: bridge/statistical ensemble and monthly distributions.
- `finance/inflation_policy/policy_model.py`: next-meeting/year-end policy ensemble.
- `finance/inflation_policy/resistance.py`: dynamic zone discovery and state transitions.
- `finance/inflation_policy/yield_model.py`: conditional yield paths and driver lenses.
- `finance/inflation_policy/simulation.py`: forward generation and reverse reweighting.
- `finance/inflation_policy/validation.py`: rolling-origin metrics and publication gates.
- `finance/inflation_policy/pipeline.py`: train, validate, materialize, and persist.
- `tests/test_inflation_policy_contracts.py`
- `tests/test_inflation_policy_pce_path.py`
- `tests/test_inflation_policy_panel.py`
- `tests/test_inflation_policy_inflation_model.py`
- `tests/test_inflation_policy_policy_model.py`
- `tests/test_yield_resistance.py`
- `tests/test_inflation_policy_yield_model.py`
- `tests/test_inflation_policy_simulation.py`
- `tests/test_inflation_policy_validation.py`
- `tests/test_inflation_policy_pipeline.py`

### Modify

- `pyproject.toml:10-32`: declare NumPy as a direct dependency.
- `uv.lock`: regenerate after dependency declaration.
- `.aiworkspace/note/finance/tasks/active/inflation-policy-core-engines/`: create task records.
- `.aiworkspace/note/finance/phases/active/inflation-policy-yield-path/{TASKS,STATUS,RISKS}.md`

## Stable Domain Interfaces

```python
INFLATION_STATES = (
    "rapid_disinflation",
    "gradual_disinflation",
    "sticky",
    "reacceleration",
    "shock_reacceleration",
)
POLICY_ACTIONS = ("CUT", "HOLD", "HIKE")
RESISTANCE_STATES = ("APPROACH", "ATTEMPT", "CONFIRMED", "HOLD", "FAILED")
PUBLICATION_STATES = ("READY", "LIMITED", "NOT_AVAILABLE", "FAILED")

@dataclass(frozen=True)
class InflationForecast:
    as_of_at: str
    monthly_path_quantiles: tuple[dict[str, object], ...]
    q4q4_quantiles: dict[str, float]
    state_probabilities: dict[str, float]
    threshold_probabilities: dict[str, float]
    publication_status: str
    reason_codes: tuple[str, ...]

@dataclass(frozen=True)
class PolicyForecast:
    next_meeting_probabilities: dict[str, float]
    year_end_target_probabilities: dict[str, float]
    net_move_probabilities: dict[str, float]
    publication_status: str
    reason_codes: tuple[str, ...]

@dataclass(frozen=True)
class ReverseScenarioResult:
    target: dict[str, object]
    matched_path_count: int
    effective_sample_size: float
    conditional_policy_probabilities: dict[str, float]
    conditional_q4q4_quantiles: dict[str, float]
    required_remaining_mom_quantiles: dict[str, float]
    publication_status: str
    reason_codes: tuple[str, ...]
```

### Task 1: Add independent contracts and probability primitives

**Files:**
- Create: `finance/inflation_policy/__init__.py`
- Create: `finance/inflation_policy/contracts.py`
- Create: `finance/inflation_policy/probability.py`
- Create: `tests/test_inflation_policy_contracts.py`
- Modify: `pyproject.toml:10-32`
- Modify: `uv.lock`
- Create: `.aiworkspace/note/finance/tasks/active/inflation-policy-core-engines/{PLAN,DESIGN,STATUS,NOTES,RUNS,RISKS}.md`

**Interfaces:**
- Consumes: Python mappings/sequences only.
- Produces the stable dataclasses above plus:

```python
def normalize_simplex(values: Mapping[str, float], *, exact_keys: Sequence[str]) -> dict[str, float]: ...
def weighted_quantiles(values: Sequence[float], weights: Sequence[float], quantiles: Sequence[float]) -> dict[str, float]: ...
def effective_sample_size(weights: Sequence[float]) -> float: ...
```

- [ ] **Step 1: Write failing contract tests**

```python
def test_probability_simplex_rejects_wrong_keys_and_negative_mass() -> None:
    with pytest.raises(ValueError, match="exact keys"):
        normalize_simplex({"CUT": 0.5, "HOLD": 0.5}, exact_keys=POLICY_ACTIONS)
    with pytest.raises(ValueError, match="non-negative"):
        normalize_simplex({"CUT": -0.1, "HOLD": 0.6, "HIKE": 0.5}, exact_keys=POLICY_ACTIONS)

def test_core_package_does_not_import_existing_cycle() -> None:
    sources = "\n".join(path.read_text() for path in Path("finance/inflation_policy").glob("*.py"))
    assert "finance.economic_cycle" not in sources
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_contracts.py -q
```

Expected: FAIL on missing package.

- [ ] **Step 3: Implement immutable contracts and numerical guards**

All dataclass constructors validate finite numbers, exact probability keys, probability sum within `1e-9`, and recognized publication states. `weighted_quantiles` sorts values and cumulative normalized weights; zero total weight raises `ValueError`.

- [ ] **Step 4: Declare NumPy directly and lock**

Add `"numpy>=2.0.0"` to project dependencies and run:

```bash
uv lock
```

Expected: lock succeeds without changing the Python floor.

- [ ] **Step 5: Run tests and commit**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_contracts.py -q
git add finance/inflation_policy pyproject.toml uv.lock tests/test_inflation_policy_contracts.py \
  .aiworkspace/note/finance/tasks/active/inflation-policy-core-engines
git commit -m "인플레이션 정책 모델 계약 추가"
```

### Task 2: Implement Core PCE index-path and scenario math

**Files:**
- Create: `finance/inflation_policy/pce_path.py`
- Create: `tests/test_inflation_policy_pce_path.py`

**Interfaces:**
- Produces:

```python
def monthly_pct_changes(index_values: Sequence[float]) -> tuple[float, ...]: ...
def extend_index_path(last_index: float, monthly_pct: Sequence[float]) -> tuple[float, ...]: ...
def q4q4_from_monthly_index(index_by_month: Mapping[str, float], *, target_year: int) -> float: ...
def solve_constant_remaining_mom(index_by_month: Mapping[str, float], *, target_year: int, target_q4q4: float) -> float: ...
def complete_constant_path(index_by_month: Mapping[str, float], *, target_year: int, remaining_mom: float) -> dict[str, float]: ...
def one_shock_paths(index_by_month: Mapping[str, float], *, target_year: int, shock_mom: float, other_mom: float) -> tuple[float, ...]: ...
def classify_q4q4_states(samples: Sequence[float], *, boundaries: Sequence[float]) -> dict[str, float]: ...
def apply_next_print_scenario(samples: np.ndarray, *, next_mom_pct: float) -> np.ndarray: ...
```

- [ ] **Step 1: Write the exact 2026 failing tests**

```python
PREV_Q4 = {"2025-10": 127.243, "2025-11": 127.469, "2025-12": 127.886}
KNOWN = {**PREV_Q4, "2026-06": 130.266}

@pytest.mark.parametrize(("mom", "expected"), [(0.20, 3.1689), (0.264, 3.4989), (0.30, 3.6849)])
def test_constant_remaining_path_matches_2026_examples(mom: float, expected: float) -> None:
    path = complete_constant_path(KNOWN, target_year=2026, remaining_mom=mom)
    assert q4q4_from_monthly_index(path, target_year=2026) == pytest.approx(expected, abs=1e-4)

def test_one_point_four_print_is_not_a_fixed_three_point_five_outcome() -> None:
    outcomes = one_shock_paths(KNOWN, target_year=2026, shock_mom=0.4, other_mom=0.2)
    assert min(outcomes) == pytest.approx(3.2377, abs=1e-4)
    assert max(outcomes) == pytest.approx(3.3748, abs=1e-4)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_pce_path.py -q
```

Expected: FAIL on missing module.

- [ ] **Step 3: Implement index recursion and root solving**

Use multiplicative index recursion and bisection over `[-2.0, 2.0]` monthly percent with tolerance `1e-8`. Require all three prior-Q4 months and reject gaps in target Q4 rather than interpolating them.

- [ ] **Step 4: Implement versioned five-state mapping**

Accept four increasing boundaries; map sample mass to the five approved states. The June 2026 state-definition fixture uses `(2.9, 3.1, 3.5, 3.9)` but the function receives boundaries and contains no 2026 constant.

- [ ] **Step 5: Run tests and commit**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_pce_path.py tests/test_inflation_policy_contracts.py -q
git add finance/inflation_policy/pce_path.py tests/test_inflation_policy_pce_path.py
git commit -m "Core PCE 연말 경로 계산 추가"
```

### Task 3: Build the point-in-time feature and target panel

**Files:**
- Create: `finance/inflation_policy/panel.py`
- Create: `tests/test_inflation_policy_panel.py`

**Interfaces:**
- Consumes: `InflationPolicyDataBundle`.
- Produces:

```python
def build_inflation_training_panel(bundle: InflationPolicyDataBundle, *, origins: Sequence[str]) -> pd.DataFrame: ...
def build_policy_training_panel(bundle: InflationPolicyDataBundle, *, meetings: Sequence[str]) -> pd.DataFrame: ...
def build_yield_training_panel(bundle: InflationPolicyDataBundle, *, origins: Sequence[str]) -> pd.DataFrame: ...
```

- [ ] **Step 1: Write failing release-cutoff and target-separation tests**

```python
def test_panel_never_uses_release_after_origin() -> None:
    panel = build_inflation_training_panel(bundle_with_next_day_pce(), origins=["2026-07-29T18:00:00+00:00"])
    assert panel.loc[0, "latest_core_pce_observation"] == "2026-05-01"
    assert panel.loc[0, "excluded_future_release_count"] == 1

def test_policy_target_comes_from_decision_not_sep() -> None:
    panel = build_policy_training_panel(policy_fixture_bundle(), meetings=["2026-07-29"])
    assert panel.loc[0, "target_action"] == "HOLD"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_panel.py -q
```

Expected: FAIL on missing panel builder.

- [ ] **Step 3: Implement feature transformations**

Inflation features: Core PCE lags, CPI/Core CPI bridge, trimmed mean, wage/ULC/PPI, breadth, expectations. Policy features: inflation features plus unemployment/payrolls/claims/production/consumption and anonymous SEP bins. Yield features: DGS2, DGS10, DFII10, T10YIE, curve, ACM, daily/21/63-day changes. Fit scaling parameters using rows strictly before each validation origin.

- [ ] **Step 4: Implement targets without circular labels**

Inflation targets are future Core PCE monthly rates/index Q4Q4; policy targets are actual FOMC decisions/target bands; yield targets are future DGS10 paths and zone states. Do not use inflation state labels as policy targets or yield breakout as an inflation target.

- [ ] **Step 5: Run tests and commit**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_panel.py tests/test_inflation_policy_loaders.py -q
git add finance/inflation_policy/panel.py tests/test_inflation_policy_panel.py
git commit -m "인플레이션 정책 PIT 학습 패널 추가"
```

### Task 4: Fit and forecast the hybrid Core PCE model

**Files:**
- Create: `finance/inflation_policy/inflation_model.py`
- Create: `tests/test_inflation_policy_inflation_model.py`

**Interfaces:**
- Produces:

```python
@dataclass(frozen=True)
class InflationModelArtifact:
    model_version: str
    feature_names: tuple[str, ...]
    bridge_weights: tuple[float, ...]
    ridge_coefficients: tuple[float, ...]
    component_weights: dict[str, float]
    residuals: tuple[float, ...]
    state_boundaries: tuple[float, float, float, float]
    trained_through: str
    publication_status: str
    reason_codes: tuple[str, ...]

def fit_inflation_model(panel: pd.DataFrame, *, ridge_alpha: float = 1.0) -> InflationModelArtifact: ...
def forecast_core_pce(artifact: InflationModelArtifact, feature_row: Mapping[str, object], known_index: Mapping[str, float], *, sample_count: int = 10000, random_seed: int = 20260802) -> InflationForecast: ...
```

- [ ] **Step 1: Write failing ensemble tests**

Test deterministic seed, component weights summing to 1, residual uncertainty widening multiple-month paths, and threshold keys `3.4`, `3.5`, `3.6` derived from supplied thresholds rather than constants.

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_inflation_model.py -q
```

Expected: FAIL on missing model.

- [ ] **Step 3: Implement bridge and ridge components**

Bridge prediction uses Core PCE lags plus CPI/component features with explicit documented weights. Ridge solves `(XᵀX + αI)β = Xᵀy` with intercept unpenalized. Reject singular/non-finite panels with `LIMITED` rather than silently dropping all rows.

- [ ] **Step 4: Implement empirical residual simulation**

Sample centered rolling-origin residuals with a fixed RNG, recursively extend monthly index levels, calculate Q4/Q4, state probabilities, threshold probabilities, and next-print scenario posterior. Inflate residual scale by stored calibration ratio when interval coverage is too narrow.

- [ ] **Step 5: Run tests and commit**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_inflation_model.py tests/test_inflation_policy_pce_path.py -q
git add finance/inflation_policy/inflation_model.py tests/test_inflation_policy_inflation_model.py
git commit -m "혼합형 Core PCE 확률 모델 추가"
```

### Task 5: Fit and forecast the FOMC policy ensemble

**Files:**
- Create: `finance/inflation_policy/policy_model.py`
- Create: `tests/test_inflation_policy_policy_model.py`

**Interfaces:**
- Produces:

```python
@dataclass(frozen=True)
class PolicyModelArtifact:
    reaction_rule_parameters: dict[str, float]
    class_statistics: dict[str, dict[str, float]]
    component_weights: dict[str, float]
    calibration_temperature: float
    trained_through: str
    publication_status: str
    reason_codes: tuple[str, ...]

def sep_rate_prior(rows: Sequence[Mapping[str, object]], *, current_midpoint: float, meeting_count_remaining: int) -> dict[str, float]: ...
def fit_policy_model(panel: pd.DataFrame) -> PolicyModelArtifact: ...
def forecast_policy_path(artifact: PolicyModelArtifact, feature_row: Mapping[str, object], *, sep_rows: Sequence[Mapping[str, object]], optional_market_prior: Mapping[str, float] | None = None) -> PolicyForecast: ...
```

- [ ] **Step 1: Write failing prior and anonymity tests**

```python
def test_june_sep_prior_counts_two_and_three_hikes_without_joint_mapping() -> None:
    prior = sep_rate_prior(june_2026_rate_dots(), current_midpoint=3.625, meeting_count_remaining=4)
    assert prior["TWO_HIKES"] == pytest.approx(5 / 18)
    assert prior["THREE_HIKES"] == pytest.approx(1 / 18)

def test_one_high_pce_print_never_returns_direct_hike_boolean() -> None:
    result = forecast_policy_path(ready_artifact(), feature_row_with_core_pce_mom(0.5), sep_rows=[])
    assert isinstance(result.next_meeting_probabilities, dict)
    assert set(result.next_meeting_probabilities) == {"CUT", "HOLD", "HIKE"}
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_policy_model.py -q
```

Expected: FAIL on missing policy model.

- [ ] **Step 3: Implement the four components**

Reaction component uses inflation gap/momentum/breadth, real policy rate, unemployment/payroll/claims, and growth. SEP component uses only marginal rate-dot counts and aggregate macro distributions. Statistical component uses historical decision-class likelihoods. Optional market prior is included only when fresh/valid; otherwise the other component weights renormalize.

- [ ] **Step 4: Implement next-meeting and year-end outputs**

Return `CUT|HOLD|HIKE`, target midpoint bins, and net move bins from the same simulated meeting paths. Validate that the implied final target midpoint matches each net-move bin; inconsistent paths become `FAILED`.

- [ ] **Step 5: Run tests and commit**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_policy_model.py tests/test_fomc_policy_data.py -q
git add finance/inflation_policy/policy_model.py tests/test_inflation_policy_policy_model.py
git commit -m "FOMC 정책 경로 확률 모델 추가"
```

### Task 6: Detect point-in-time dynamic resistance zones

**Files:**
- Create: `finance/inflation_policy/resistance.py`
- Create: `tests/test_yield_resistance.py`

**Interfaces:**
- Produces:

```python
@dataclass(frozen=True)
class ResistanceZone:
    instrument: str
    known_at: str
    lower_pct: float
    upper_pct: float
    buffer_pct: float
    lookbacks: tuple[int, ...]
    touch_count: int
    strength: float

def detect_pivot_highs(series: pd.Series, *, left: int = 3, right: int = 3) -> tuple[dict[str, object], ...]: ...
def cluster_resistance_zones(series: pd.Series, pivots: Sequence[Mapping[str, object]], *, lookbacks: Sequence[int] = (63, 252, 504)) -> tuple[ResistanceZone, ...]: ...
def classify_breakout_state(series: pd.Series, zone: ResistanceZone, *, confirmation_count: int = 3, confirmation_window: int = 5) -> str: ...
```

- [ ] **Step 1: Write failing future-knowledge and 4.7-zone tests**

```python
def test_pivot_is_known_only_after_right_window() -> None:
    pivots = detect_pivot_highs(sample_yields(), left=2, right=2)
    assert pivots[0]["known_at"] == add_trading_rows(pivots[0]["pivot_at"], 2)

def test_nearby_highs_form_a_zone_not_a_global_constant() -> None:
    zones = cluster_resistance_zones(dgs10_2025_2026_fixture(), detected_pivots())
    assert any(zone.lower_pct < 4.70 < zone.upper_pct for zone in zones)
    assert "4.7" not in Path("finance/inflation_policy/resistance.py").read_text()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_yield_resistance.py -q
```

Expected: FAIL on missing module.

- [ ] **Step 3: Implement pivots, adaptive tolerance, and strength**

Tolerance is `max(0.05 percentage point, median absolute daily move over 63 rows)`. Strength combines touch count, rejection distance, recency decay, and 63/252/504-day confluence; Treasury yields have no volume input.

- [ ] **Step 4: Implement state transitions**

`CONFIRMED` requires 3 of 5 closes above `upper + buffer` or an eligible weekly close. `HOLD` requires the configured persistence rows; `FAILED` requires close back below the zone after an attempt/confirmation. Historical replay uses only rows through each as-of date.

- [ ] **Step 5: Run tests and commit**

```bash
.venv/bin/python -m pytest tests/test_yield_resistance.py -q
git add finance/inflation_policy/resistance.py tests/test_yield_resistance.py
git commit -m "국채금리 동적 저항선 엔진 추가"
```

### Task 7: Model yield drivers and forward/reverse scenarios

**Files:**
- Create: `finance/inflation_policy/yield_model.py`
- Create: `finance/inflation_policy/simulation.py`
- Create: `tests/test_inflation_policy_yield_model.py`
- Create: `tests/test_inflation_policy_simulation.py`

**Interfaces:**
- Produces:

```python
def classify_yield_driver(*, dgs10_change: float, dgs2_change: float, dfii10_change: float, breakeven_change: float, term_premium_change: float | None) -> dict[str, object]: ...
def fit_yield_path_model(panel: pd.DataFrame) -> YieldPathArtifact: ...
def simulate_forward_paths(inflation: InflationForecast, policy: PolicyForecast, yield_artifact: YieldPathArtifact, zones: Sequence[ResistanceZone], *, sample_count: int = 10000, random_seed: int = 20260802) -> ForwardScenarioResult: ...
def reverse_condition_paths(forward: ForwardScenarioResult, *, instrument: str, target_lower: float, target_upper: float, condition: str, horizon_date: str, minimum_effective_sample_size: float = 100.0) -> ReverseScenarioResult: ...
```

- [ ] **Step 1: Write failing driver and no-double-count tests**

Test inflation-led, real-rate-led, term-premium-led, mixed classifications and assert the returned decomposition contains separate `policy_term_premium_lens` and `real_breakeven_lens` without a combined component sum.

- [ ] **Step 2: Write failing reverse-scenario tests**

```python
def test_reverse_scenario_returns_conditional_distribution_not_required_hike_scalar() -> None:
    result = reverse_condition_paths(forward_fixture(), instrument="DGS10", target_lower=4.68, target_upper=4.75, condition="HOLD", horizon_date="2026-12-31")
    assert set(result.conditional_policy_probabilities) >= {"HOLD", "ONE_HIKE", "TWO_HIKES", "THREE_PLUS_HIKES"}
    assert not hasattr(result, "required_hike_count")

def test_too_few_matching_paths_is_not_available() -> None:
    result = reverse_condition_paths(sparse_forward_fixture(), instrument="DGS10", target_lower=6.0, target_upper=6.1, condition="HOLD", horizon_date="2026-12-31")
    assert result.publication_status == "NOT_AVAILABLE"
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_yield_model.py tests/test_inflation_policy_simulation.py -q
```

Expected: FAIL on missing modules.

- [ ] **Step 4: Implement conditional yield simulation**

Use empirical residual bootstrap around fitted DGS2/DGS10/DFII10/T10YIE/ACM relationships. Sample policy and inflation paths jointly through shared scenario rows; do not add 25bp to DGS10 per hike. Evaluate zone `APPROACH|ATTEMPT|CONFIRMED|HOLD|FAILED` on each simulated path.

Fit ACM effects only on origins whose ACM release was actually stored by that date. If historical ACM coverage is below the validation gate, train the yield path without ACM, mark the term-premium driver `LIMITED`, and never reconstruct past ACM from today's workbook.

- [ ] **Step 5: Implement reverse likelihood reweighting**

Weight paths by target-zone/condition likelihood, normalize weights, calculate effective sample size, and summarize policy bins, Q4Q4 quantiles, and remaining-MoM quantiles. Below the effective-sample threshold, return `NOT_AVAILABLE` with `INSUFFICIENT_MATCHED_PATHS`.

- [ ] **Step 6: Run tests and commit**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_yield_model.py tests/test_inflation_policy_simulation.py tests/test_yield_resistance.py -q
git add finance/inflation_policy/yield_model.py finance/inflation_policy/simulation.py \
  tests/test_inflation_policy_yield_model.py tests/test_inflation_policy_simulation.py
git commit -m "국채금리 순방향 역산 시나리오 추가"
```

### Task 8: Add rolling-origin validation and publication gates

**Files:**
- Create: `finance/inflation_policy/validation.py`
- Create: `tests/test_inflation_policy_validation.py`

**Interfaces:**
- Produces:

```python
def calculate_distribution_metrics(samples: Sequence[Sequence[float]], targets: Sequence[float]) -> dict[str, float]: ...
def calculate_classification_metrics(probabilities: Sequence[Mapping[str, float]], targets: Sequence[str], *, classes: Sequence[str]) -> dict[str, float]: ...
def rolling_origin_validate_inflation(panel: pd.DataFrame, *, minimum_train_rows: int = 120) -> ValidationReport: ...
def rolling_origin_validate_policy(panel: pd.DataFrame, *, minimum_train_meetings: int = 40) -> ValidationReport: ...
def rolling_origin_validate_resistance(panel: pd.DataFrame, *, minimum_confirmed_events: int = 30) -> ValidationReport: ...
def decide_publication(component: str, report: ValidationReport) -> PublicationDecision: ...
```

- [ ] **Step 1: Write failing metric and gate tests**

Test CRPS/MAE/coverage, Brier/log loss/ECE, baseline comparison, invalid probability rejection, training rows ending before target, and `LIMITED` when the best baseline beats the model.

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_validation.py -q
```

Expected: FAIL on missing validation module.

- [ ] **Step 3: Implement chronological validation**

Inflation baselines: carry-forward, rolling mean, latest SEP. Policy baselines: hold, prior decision, latest SEP, optional market. Resistance baseline: rolling high plus fixed 5bp buffer. Report recent-subperiod metrics separately and never random-shuffle origins.

- [ ] **Step 4: Implement publication decisions**

`READY` requires complete PIT metadata, finite/simplex outputs, minimum sample/event counts, model distribution/classification score no worse than the best baseline, and acceptable interval/reliability calibration recorded in the artifact. Missing optional ACM cannot fail inflation/policy but limits driver classification.

- [ ] **Step 5: Run tests and commit**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_validation.py tests/test_inflation_policy_contracts.py -q
git add finance/inflation_policy/validation.py tests/test_inflation_policy_validation.py
git commit -m "인플레이션 정책 확률 공개 게이트 추가"
```

### Task 9: Materialize and replay the integrated snapshot

**Files:**
- Create: `finance/inflation_policy/pipeline.py`
- Create: `tests/test_inflation_policy_pipeline.py`
- Modify: `.aiworkspace/note/finance/tasks/active/inflation-policy-core-engines/{STATUS,NOTES,RUNS,RISKS}.md`
- Modify: `.aiworkspace/note/finance/phases/active/inflation-policy-yield-path/{TASKS,STATUS,RISKS}.md`

**Interfaces:**
- Consumes: data bundle, model components, validators, result stores.
- Produces:

```python
def train_inflation_policy_artifacts(*, train_through: str, data_loader: Callable[..., InflationPolicyDataBundle] = load_inflation_policy_data_bundle) -> dict[str, object]: ...
def materialize_inflation_policy_snapshot(*, as_of_at: str, model_version: str | None = None, run_kind: str = "current") -> dict[str, object]: ...
def replay_inflation_policy_snapshot(*, as_of_at: str, model_version: str) -> dict[str, object]: ...
def main(argv: Sequence[str] | None = None) -> int: ...
```

- [ ] **Step 1: Write failing no-write-on-failure and replay tests**

```python
def test_failed_component_does_not_publish_current_snapshot() -> None:
    saved = []
    result = materialize_inflation_policy_snapshot(
        as_of_at="2026-07-29T18:00:00+00:00",
        components=component_fixture(policy_status="FAILED"),
        snapshot_saver=saved.append,
    )
    assert result["publication_status"] == "FAILED"
    assert saved == []

def test_replay_uses_then_known_zone_and_data() -> None:
    result = replay_inflation_policy_snapshot(as_of_at="2026-06-17T18:00:00+00:00", model_version="inflation-policy-v1")
    assert result["freshness"]["max_released_at"] <= result["as_of_at"]
    assert result["rates"]["zones"][0]["known_at"] <= result["as_of_at"]
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_pipeline.py -q
```

Expected: FAIL on missing pipeline.

- [ ] **Step 3: Implement training and atomic materialization**

Train each artifact through the declared cutoff, validate, save the artifact, then materialize only from exact-version `READY|LIMITED` artifacts. Build one JSON-safe snapshot with inflation, policy, rates, default reverse scenario, evidence, freshness, and warnings. A schema/probability failure prevents snapshot write.

Add an `argparse` entry point for `--as-of-at`, `--model-version`, and `--run-kind`; print compact JSON and return non-zero for `FAILED`.

- [ ] **Step 4: Run the 2026 replay evidence check**

```bash
.venv/bin/python -m finance.inflation_policy.pipeline \
  --as-of-at 2026-07-30T12:31:00+00:00 \
  --run-kind historical_replay
```

Expected: output uses June Core PCE released July 30, shows Q4Q4 thresholds 3.4/3.5/3.6, and does not claim a participant-level SEP mapping.

- [ ] **Step 5: Run the complete engine suite**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_*.py tests/test_yield_resistance.py -q
! rg -n "finance\.economic_cycle|economic_cycle_snapshot|economic_cycle_model_artifact" finance/inflation_policy
```

Expected: tests pass and `rg` returns no matches.

- [ ] **Step 6: Update task/phase records and commit**

Record metrics and any `LIMITED` gates without declaring them passed. Set core-engine task `State: complete` only when the focused suite and replay succeed; keep the phase active for the workbench.

```bash
git add finance/inflation_policy/pipeline.py tests/test_inflation_policy_pipeline.py \
  .aiworkspace/note/finance/tasks/active/inflation-policy-core-engines \
  .aiworkspace/note/finance/phases/active/inflation-policy-yield-path
git commit -m "인플레이션 정책 통합 스냅샷 추가"
```
