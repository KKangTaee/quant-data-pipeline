# U.S. Economic Cycle Regime Forecast Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Use `finance-db-pipeline` for 1차 data work, `superpowers:test-driven-development` throughout code work, the in-app Browser skill for 4차/5차 UI QA, `finance-doc-sync` for 5차 closeout, and `superpowers:verification-before-completion` before every completion claim.

**Goal:** 사용자가 공부한 회복·확장·둔화·침체 4단계 경제 사이클을 미국 point-in-time 데이터로 판정하고, 현재·1개월 후·2개월 후의 4국면 확률과 근거를 `Workspace > Overview > 시장 맥락`에서 이해할 수 있게 제공한다.

**Architecture:** FRED/ALFRED vintage 관측을 별도 raw table에 멱등 저장하고, as-of loader가 당시 공개된 값만 월별 feature panel로 만든다. 실물·고용 기반 retrospective label과 해석 가능한 대각 Gaussian 분류기, 제약 transition prior, horizon별 temperature calibration을 rolling-origin으로 검증한 뒤 승인된 model artifact와 월별 snapshot만 DB에 materialize한다. Overview service는 compact DB read model만 만들고 React component는 확률·cycle clock·근거·10년 regime ribbon을 렌더링한다.

**Tech Stack:** Python 3.12, pandas, Python standard-library `math`/`statistics`, MySQL schema/UPSERT, pytest, Streamlit component bridge, React 19, TypeScript, Vite.

## Global Constraints

- Authoritative design: `docs/superpowers/specs/2026-07-16-us-economic-cycle-regime-forecast-design.md`.
- Target geography is the United States. The public phase vocabulary is exactly `회복 / 확장 / 둔화 / 침체`.
- Every current, +1M, and +2M result carries all four probabilities; probabilities must be finite, bounded in `[0, 1]`, and sum to one within `1e-9`.
- Current-phase labels are created only from real activity and labor evidence with `USREC` as the recession anchor. Rates, credit, dollar, gold, commodities, inflation, and policy never create retrospective labels.
- Financial-leading and inflation-policy factors may alter +1M/+2M forecast probabilities and appear as context evidence; they do not override the current real-economy phase.
- Training, validation, replay, and UI evidence must be vintage-aware. A value is eligible only when its real-time interval contains the forecast origin. Revised latest CSV values must never silently substitute for missing vintages.
- Historical replay must fit/use the artifact available at that historical origin. Applying the latest fitted artifact backward is look-ahead and is forbidden.
- The UI never calls FRED or another provider. Preserve `Ingestion -> DB -> Loader -> Model/Pipeline -> Service -> UI`.
- Numeric probabilities are published only for horizons that pass rolling-origin validation. A failed horizon is `LIMITED`; do not display fabricated percentages or a confident phase label.
- V1 is an explanatory macro context feature, not an official recession declaration, investment recommendation, market-timing signal, broker action, or auto-rebalance input.
- No visible run/job/row diagnostic panel and no unattended scheduler are added in this task. Collection and materialization are backend jobs documented in the runbook.
- Existing `macro_series_observation`, valuation services, S&P 500, and U.S. individual-stock behavior remain compatible.
- Use TDD: write and run the focused failing test before implementation, then the focused passing test, then the broader regression command.
- Do not stage generated Browser QA screenshots, run history, `.superpowers/`, or `.aiworkspace/note/finance/researches/active/2026-07-market-interest-free-source-benchmark/`.

## Exact V1 Indicator Catalog

| Role | Factor | Series | Monthly signal |
|---|---|---|---|
| phase + forecast | activity | `INDPRO` | 6-month annualized log change |
| phase + forecast | activity | `W875RX1` | 6-month annualized log change |
| phase + forecast | activity | `RRSFS` | 6-month annualized log change |
| phase + forecast | activity | `CFNAI` | 3-month mean level |
| phase + forecast | labor_income | `PAYEMS` | 3-month annualized log change |
| phase + forecast | labor_income | `UNRATE` | negative 3-month percentage-point change |
| phase + forecast | labor_income | `ICSA` | negative 3-month log change of monthly mean |
| phase + forecast | labor_income | `AWHMAN` | 3-month level change |
| forecast only | financial_leading | `PERMIT` | 6-month annualized log change |
| forecast only | financial_leading | `USALOLITOAASTSAM` | level minus 100 plus 3-month change |
| forecast only | financial_leading | `T10Y3M` | monthly mean level |
| forecast only | financial_leading | `BAMLH0A0HYM2` | negative monthly mean level |
| forecast only | financial_leading | `ANFCI` | negative level |
| forecast context | inflation_policy | `PCEPILFE` | 3-month annualized log change minus 2% |
| forecast context | inflation_policy | `T10YIE` | monthly mean level minus 2% |
| forecast context | inflation_policy | `FEDFUNDS` | 3-month level change |
| label anchor only | recession_anchor | `USREC` | monthly recession flag |

ADS and WEI are intentionally outside the V1 core because they require separate official-source connector and vintage contracts. Dollar, gold, and commodity prices remain visible market context in existing Overview surfaces and are not inputs to the V1 phase label or forecast.

## Stable Domain Contracts

```python
PHASES = ("recovery", "expansion", "slowdown", "recession")
HORIZONS = (0, 1, 2)

@dataclass(frozen=True)
class HorizonProbability:
    horizon_months: int
    probabilities: dict[str, float]
    dominant_phase: str
    confidence: float
    publication_status: str  # READY | LIMITED

@dataclass(frozen=True)
class CycleSnapshot:
    as_of_date: date
    model_version: str
    status: str  # READY | LIMITED | ERROR
    horizons: tuple[HorizonProbability, ...]
    factor_contributions: tuple[dict[str, object], ...]
    top_evidence: tuple[dict[str, object], ...]
    warnings: tuple[str, ...]
```

The persisted snapshot stores the same information as JSON-safe primitives. Python enum-like strings and React discriminated unions must use the exact values above.

## File Responsibility Map

- Modify `finance/data/db/schema.py`: register three new economic-cycle schemas and business keys without changing the existing macro table.
- Create `finance/data/economic_cycle_vintages.py`: official FRED/ALFRED vintage request, pagination, normalization, and idempotent raw UPSERT.
- Create `finance/data/economic_cycle_results.py`: model artifact and monthly snapshot UPSERT helpers.
- Create `finance/loaders/economic_cycle.py`: strict as-of vintage reads plus artifact/snapshot/history reads.
- Create `finance/economic_cycle_catalog.py`: immutable catalog, role, aggregation, transform, direction, and minimum-history metadata.
- Create `finance/economic_cycle_features.py`: monthly as-of panel, transforms, expanding robust scaling, factor scores, coverage/freshness.
- Create `finance/economic_cycle_labels.py`: real-economy retrospective phase labels and recession override.
- Create `finance/economic_cycle_model.py`: horizon-specific Gaussian likelihoods, constrained transition prior, probability blending, calibration, and explanations.
- Create `finance/economic_cycle_validation.py`: rolling-origin predictions, baselines, metrics, and publication gates.
- Create `finance/economic_cycle_pipeline.py`: train, validate, persist artifact, current materialization, and ten-year historical replay orchestration.
- Create `finance/economic_cycle_interpretation.py`: conditional rate/equity/gold-dollar/commodity context derived from phase probabilities and factor evidence without trading instructions.
- Modify `app/jobs/ingestion_jobs.py`: explicit vintage collection and model materialization runners only.
- Create `app/services/overview/economic_cycle.py`: compact DB-only Overview read model.
- Modify `app/services/overview/market_context_valuation.py`: expose valuation instrument without forcing the existing internal selector.
- Modify `app/web/overview/market_context.py`: route the three same-level context choices.
- Modify `app/web/overview/market_context_helpers.py`: selector/session orchestration and DB-only render path.
- Modify `app/web/overview/market_context_react_component.py`: optional instrument-selector bridge for the existing valuation component.
- Create `app/web/overview/economic_cycle_react_component.py`: Streamlit bridge for the cycle component.
- Create `app/web/streamlit_components/economic_cycle_workbench/`: React/Vite cycle visualization.
- Modify `app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx`: hide the internal valuation selector when Python owns the same-level choice.
- Modify `app/web/streamlit_components/market_context_valuation/src/style.css`: only the selector-hidden compatibility rule if needed.
- Create/modify the focused tests listed in each task below.
- Update active task documents, data/architecture/flow/runbook docs, indexes, and root handoff logs in 5차.

---

## 1차 — Vintage 데이터 의미·저장 계약

### Task 1: Lock catalog and raw vintage schema

**Files:**
- Create: `finance/economic_cycle_catalog.py`
- Modify: `finance/data/db/schema.py`
- Create: `tests/test_economic_cycle_vintages.py`

**Interfaces:**
- `get_economic_cycle_catalog() -> tuple[IndicatorSpec, ...]` produces exactly the 17 rows in the catalog table above.
- `macro_series_vintage_observation` consumes normalized vintage rows and preserves every revision interval.
- Business key: `(series_id, observation_date, realtime_start, source)`.

```python
@dataclass(frozen=True)
class IndicatorSpec:
    series_id: str
    factor: str
    role: str
    frequency: str
    aggregation: str
    transform: str
    direction: int
    minimum_history_months: int
```

- [ ] **Step 1 RED:** Assert the catalog has unique series IDs, exactly one `label_anchor`, and no financial/inflation series with role `phase`.
- [ ] **Step 2 RED:** Assert `PROVIDER_SCHEMAS` exposes `macro_series_vintage_observation` with `realtime_start`, `realtime_end`, `source_mode`, `factor_group`, `release_lag_days`, and `missing_fields_json`.
- [ ] **Step 3 RED:** Assert the unique key and indexes are exactly `(series_id, observation_date, realtime_start, source)`, `(series_id, realtime_start, observation_date)`, and `(factor_group, observation_date)`.
- [ ] **Step 4 Verify RED:** Run `.venv/bin/python -m pytest tests/test_economic_cycle_vintages.py -k 'catalog or schema' -q`; expect module/schema failures.
- [ ] **Step 5 GREEN:** Implement the immutable catalog and add the schema group. Use `DATE` for observation/realtime dates, `DECIMAL(24,10)` for values, bounded `VARCHAR` metadata, and `TEXT` for serialized missing fields.
- [ ] **Step 6 Verify GREEN:** Re-run the focused tests and `.venv/bin/python -m pytest tests/test_schema_contracts.py -q` if that file exists; otherwise run the repository schema-focused test selected by `rg -l 'PROVIDER_SCHEMAS' tests`.

### Task 2: Collect and UPSERT official vintages

**Files:**
- Create: `finance/data/economic_cycle_vintages.py`
- Modify: `tests/test_economic_cycle_vintages.py`

**Interfaces:**
- `fetch_fred_vintages(series_id, *, api_key, session=None, limit=100_000) -> list[dict[str, object]]` calls official `series/observations` with long-form `output_type=1`, JSON pagination, and explicit real-time bounds. It first reads `series/vintagedates` and partitions requests at the provider's 2,000-vintage-date limit.
- `normalize_fred_vintage_rows(spec, payload_rows, *, collected_at) -> list[dict[str, object]]` produces schema rows.
- `upsert_economic_cycle_vintages(rows, *, connection=None) -> int` uses the business key above.
- `collect_economic_cycle_vintages(*, series_ids=None, api_key=None, connection=None) -> dict[str, object]` fails closed without a key.

```python
params = {
    "series_id": series_id,
    "api_key": api_key,
    "file_type": "json",
    "output_type": 1,
    "limit": limit,
    "offset": offset,
}
```

- [ ] **Step 1 RED:** Parse a two-page fixture with overlapping observations and assert all distinct real-time versions survive in deterministic date order.
- [ ] **Step 2 RED:** Assert `.` and non-finite values become `value=None` with `coverage_status='MISSING_VALUE'`, never zero.
- [ ] **Step 3 RED:** Assert `FRED_API_KEY` absence raises a domain error before HTTP or DB access; revised CSV fallback is forbidden.
- [ ] **Step 4 RED:** Run the same normalized rows twice through an injected writer and assert one business row per key with updated collection metadata.
- [ ] **Step 5 RED:** Assert `release_lag_days = realtime_start - observation_date` and negative lag is retained with a warning rather than silently clamped.
- [ ] **Step 6 Verify RED:** Run `.venv/bin/python -m pytest tests/test_economic_cycle_vintages.py -k 'fetch or normalize or upsert or api_key' -q`.
- [ ] **Step 7 GREEN:** Implement bounded retries using the repository HTTP conventions, explicit timeout, pagination, normalization, and MySQL `ON DUPLICATE KEY UPDATE` for non-key fields.
- [ ] **Step 8 Verify GREEN:** Re-run all vintage tests.

### Task 3: Strict as-of vintage loader

**Files:**
- Create: `finance/loaders/economic_cycle.py`
- Modify: `tests/test_economic_cycle_vintages.py`

**Interfaces:**
- `load_economic_cycle_vintages(series_ids, *, start_date, end_date, as_of_date, query_fn=None) -> list[dict[str, object]]` returns one eligible version per `(series_id, observation_date)`.
- Eligibility: `realtime_start <= as_of_date <= realtime_end`; open-ended `9999-12-31` is valid.
- `load_economic_cycle_series_coverage(*, as_of_date, query_fn=None) -> dict[str, object]` returns compact coverage/freshness, not raw rows for UI.

```sql
ROW_NUMBER() OVER (
  PARTITION BY series_id, observation_date
  ORDER BY realtime_start DESC, updated_at DESC
) AS version_rank
```

- [ ] **Step 1 RED:** Use a revised payroll fixture and assert a 2020 forecast origin reads the then-current value while a 2022 origin reads the later revision.
- [ ] **Step 2 RED:** Assert an observation with `realtime_start` one day after the origin is absent even when its observation date is earlier.
- [ ] **Step 3 RED:** Assert duplicate stored retries choose the deterministic latest `updated_at` but never cross the real-time interval.
- [ ] **Step 4 RED:** Assert loader SQL is parameterized and bounded by requested series/date/origin.
- [ ] **Step 5 Verify RED:** Run `.venv/bin/python -m pytest tests/test_economic_cycle_vintages.py -k 'as_of or unreleased or revision' -q`.
- [ ] **Step 6 GREEN:** Implement the query seam and JSON/date normalization; do not import Streamlit or provider code.
- [ ] **Step 7 Verify GREEN:** Run `.venv/bin/python -m pytest tests/test_economic_cycle_vintages.py -q`.
- [ ] **Step 8 Commit:** Commit schema/catalog/collector/loader/tests as `경제 사이클 vintage 데이터 경계 추가`.

**1차 완료 조건:** raw revisions are preserved, repeated collection is idempotent, and tests prove a historical origin cannot see a later release or revision.

---

## 2차 — 현재 국면 엔진과 과거 history

### Task 4: Build leakage-safe monthly features

**Files:**
- Create: `finance/economic_cycle_features.py`
- Create: `tests/test_economic_cycle_features.py`

**Interfaces:**
- `build_monthly_feature_panel(vintage_rows, catalog, *, forecast_origins) -> pd.DataFrame` produces one row per month-end origin.
- `fit_expanding_robust_scale(values, *, minimum_history=60) -> list[float | None]` uses only prior/current observations.
- `calculate_factor_scores(panel) -> pd.DataFrame` produces `activity_score`, `labor_income_score`, `financial_leading_score`, `inflation_policy_score`, per-factor availability counts, total coverage, and stale flags.

```python
def robust_z(history: pd.Series, current: float) -> float | None:
    median = float(history.median())
    mad = float((history - median).abs().median())
    if not math.isfinite(mad) or mad <= 1e-12:
        return None
    return max(-4.0, min(4.0, (current - median) / (1.4826 * mad)))
```

- [ ] **Step 1 RED:** Assert each exact transform/aggregation in the catalog with hand-calculated fixtures, including daily/weekly monthly means and month-end levels.
- [ ] **Step 2 RED:** Append extreme future values and assert every earlier standardized value and factor score is byte-for-byte unchanged.
- [ ] **Step 3 RED:** Assert the expanding scale is missing before 60 valid months and clamps finite scores to `[-4, 4]`.
- [ ] **Step 4 RED:** Assert a factor needs at least two available indicators and a row needs at least 75% catalog coverage; otherwise its readiness is `LIMITED`.
- [ ] **Step 5 RED:** Assert stale thresholds are frequency-aware: daily/weekly 45 days, monthly 75 days, and CFNAI/quarter-like slow release 100 days.
- [ ] **Step 6 Verify RED:** Run `.venv/bin/python -m pytest tests/test_economic_cycle_features.py -q`.
- [ ] **Step 7 GREEN:** Implement deterministic monthly alignment, transformation, expanding scaling, equal-weight available factor scores, and explicit missingness.
- [ ] **Step 8 Verify GREEN:** Re-run feature tests.

### Task 5: Create retrospective real-economy labels

**Files:**
- Create: `finance/economic_cycle_labels.py`
- Create: `tests/test_economic_cycle_labels.py`

**Interfaces:**
- `build_retrospective_phase_labels(feature_panel, *, label_as_of_date=None) -> pd.Series` consumes only activity/labor scores and the `USREC` value eligible at each label origin.
- `label_phase(activity_level, labor_level, activity_momentum, labor_momentum, recession_flag) -> str` returns one of `PHASES`.

```python
level = 0.5 * activity_level + 0.5 * labor_level
momentum = 0.5 * activity_momentum + 0.5 * labor_momentum
if recession_flag >= 0.5:
    return "recession"
if level < 0 and momentum >= 0:
    return "recovery"
if level >= 0 and momentum >= 0:
    return "expansion"
if level >= 0 and momentum < 0:
    return "slowdown"
return "recession"
```

- [ ] **Step 1 RED:** Cover all four quadrants plus the `USREC` recession override.
- [ ] **Step 2 RED:** Mutate financial-leading and inflation-policy columns and assert labels do not change.
- [ ] **Step 3 RED:** Assert labels are missing when activity or labor factor readiness is missing; do not forward-fill a phase.
- [ ] **Step 4 RED:** Assert a later NBER/USREC revision cannot rewrite labels passed to a historical-origin fit; final retrospective labels may be used as evaluation truth but never as training input before their target date.
- [ ] **Step 5 RED:** Assert the level/momentum tie-break is deterministic at exact zero and phase vocabulary is stable.
- [ ] **Step 6 Verify RED:** Run `.venv/bin/python -m pytest tests/test_economic_cycle_labels.py -q`.
- [ ] **Step 7 GREEN:** Implement the label contract and label metadata containing component scores, recession override, eligible vintage date, and reason code.
- [ ] **Step 8 Verify GREEN:** Re-run labels and feature tests together.

### Task 6: Fit interpretable current-phase model

**Files:**
- Create: `finance/economic_cycle_model.py`
- Create: `tests/test_economic_cycle_model.py`

**Interfaces:**
- `fit_horizon_model(features, labels, *, horizon_months, minimum_variance=0.05) -> HorizonModelArtifact`.
- `predict_phase_probabilities(artifact, feature_row, *, transition_prior=None, temperature=1.0) -> dict[str, float]`.
- For horizon `0`, permitted model features are only `activity_score`, `labor_income_score`, and their three-month momentum.

```python
log_score = math.log(max(class_prior, 1e-12))
for name in artifact.feature_names:
    variance = max(artifact.variances[phase][name], artifact.minimum_variance)
    delta = float(row[name]) - artifact.means[phase][name]
    log_score += -0.5 * (math.log(2.0 * math.pi * variance) + delta * delta / variance)
```

- [ ] **Step 1 RED:** Fit a four-cluster synthetic fixture and assert the expected dominant phase for each cluster.
- [ ] **Step 2 RED:** Assert horizon 0 rejects artifacts containing financial or inflation feature names.
- [ ] **Step 3 RED:** Assert absent phase training data yields `LIMITED`, not zero-probability or divide-by-zero.
- [ ] **Step 4 RED:** Assert all returned probabilities satisfy the simplex and remain finite with constant features through variance regularization.
- [ ] **Step 5 RED:** Assert explanation contributions are the per-feature log-likelihood difference between the winning phase and runner-up and sum to the reported log-odds difference within tolerance.
- [ ] **Step 6 Verify RED:** Run `.venv/bin/python -m pytest tests/test_economic_cycle_model.py -k 'fit or current or probability or explanation' -q`.
- [ ] **Step 7 GREEN:** Implement serializable dataclasses, diagonal Gaussian fitting, stable log-sum-exp softmax, strict feature allowlist, and contribution evidence.
- [ ] **Step 8 Verify GREEN:** Re-run focused model tests.

### Task 7: Persist model artifact and monthly snapshots

**Files:**
- Modify: `finance/data/db/schema.py`
- Create: `finance/data/economic_cycle_results.py`
- Modify: `finance/loaders/economic_cycle.py`
- Create: `tests/test_economic_cycle_results.py`

**Interfaces:**
- `economic_cycle_model_artifact` business key: `(model_version, trained_through)`.
- `economic_cycle_snapshot` business key: `(as_of_date, model_version, run_kind)` where run kind is `historical_replay | current`.
- `nber_recession` is a separately labeled latest official chronology reference for ribbon shading; it never changes the origin-specific model probability or training feature set.
- `upsert_cycle_model_artifact`, `upsert_cycle_snapshots`, `load_latest_approved_cycle_artifact`, `load_cycle_snapshot`, and `load_cycle_history` use compact serialized fields.

```python
snapshot_row = {
    "as_of_date": snapshot.as_of_date,
    "model_version": snapshot.model_version,
    "run_kind": run_kind,
    "training_cutoff_date": training_cutoff,
    "data_cutoff_date": data_cutoff,
    "status": snapshot.status,
    "nber_recession": bool(nber_recession),
    "probabilities_json": json.dumps(probabilities, sort_keys=True),
    "forecast_path_json": json.dumps(forecast_path, sort_keys=True),
    "factor_contributions_json": json.dumps(contributions, sort_keys=True),
    "top_evidence_json": json.dumps(evidence, sort_keys=True),
    "warnings_json": json.dumps(warnings, sort_keys=True),
}
```

- [ ] **Step 1 RED:** Assert both schemas, unique keys, `(as_of_date, status)` history index, and publication metadata fields.
- [ ] **Step 2 RED:** Assert artifact/snapshot serializers round-trip exact phase/horizon/status vocabulary.
- [ ] **Step 3 RED:** Assert repeated UPSERT updates metrics/evidence without creating a second business row.
- [ ] **Step 4 RED:** Assert the current loader chooses only an approved artifact and the ten-year history query is date-bounded and ascending.
- [ ] **Step 5 Verify RED:** Run `.venv/bin/python -m pytest tests/test_economic_cycle_results.py -q`.
- [ ] **Step 6 GREEN:** Add schema dictionaries, idempotent writers, and DB-only readers. Store JSON as canonical sorted UTF-8 text for repository compatibility.
- [ ] **Step 7 Verify GREEN:** Re-run result, schema, and loader tests.
- [ ] **Step 8 Commit:** Commit feature/label/current model/result persistence as `경제 사이클 현재 국면 엔진 추가`.

**2차 완료 조건:** one historical forecast origin produces a reproducible current-phase distribution and evidence using only its vintage data, and compact monthly snapshots can be replayed for the ribbon.

---

## 3차 — +1M/+2M 예측·검증·publication gate

### Task 8: Constrained transition prior and direct horizon models

**Files:**
- Modify: `finance/economic_cycle_model.py`
- Modify: `tests/test_economic_cycle_model.py`

**Interfaces:**
- `estimate_transition_matrix(labels, *, alpha_same=3.0, alpha_next=2.0, alpha_other=0.5) -> dict[str, dict[str, float]]`.
- `fit_forecast_models(feature_panel, labels) -> dict[int, HorizonModelArtifact]` shifts target labels directly by 1 and 2 months.
- Forecast feature allowlist: current real-economy level/momentum plus `financial_leading_score` and `inflation_policy_score`; horizon 0 rules remain unchanged.
- `blend_likelihood_and_transition(likelihood, prior, *, likelihood_weight=0.7) -> dict[str, float]` combines in log space.

```python
NEXT_PHASE = {
    "recovery": "expansion",
    "expansion": "slowdown",
    "slowdown": "recession",
    "recession": "recovery",
}
```

- [ ] **Step 1 RED:** Assert every transition row sums to one, has no zero entries, and gives same/next state a larger prior than a skipped state before evidence.
- [ ] **Step 2 RED:** Use a feature shock fixture where direct +2M targets differ from repeated +1M transitions; assert the +2M artifact uses shifted labels, not matrix squaring alone.
- [ ] **Step 3 RED:** Assert current phase remains unchanged when only financial context changes, while +1M/+2M probabilities may change.
- [ ] **Step 4 RED:** Assert blend output remains a probability simplex for tiny likelihoods and priors.
- [ ] **Step 5 Verify RED:** Run `.venv/bin/python -m pytest tests/test_economic_cycle_model.py -k 'transition or horizon or blend or financial' -q`.
- [ ] **Step 6 GREEN:** Implement transition smoothing, direct horizon targets, forecast feature allowlist, and log-space blending.
- [ ] **Step 7 Verify GREEN:** Run all model tests.

### Task 9: Horizon-specific probability calibration

**Files:**
- Modify: `finance/economic_cycle_model.py`
- Modify: `tests/test_economic_cycle_model.py`

**Interfaces:**
- `fit_temperature(probability_rows, target_labels, *, grid=None) -> float` minimizes multiclass log loss on out-of-fold predictions.
- Default deterministic grid is `0.50, 0.55, ..., 3.00`; choose the smaller temperature on ties.
- `apply_temperature(probabilities, temperature) -> dict[str, float]` preserves order and simplex.

```python
DEFAULT_TEMPERATURE_GRID = tuple(round(0.50 + 0.05 * i, 2) for i in range(51))
```

- [ ] **Step 1 RED:** Assert an overconfident wrong fixture selects temperature greater than 1 and improves or equals log loss.
- [ ] **Step 2 RED:** Assert already calibrated probabilities choose a deterministic grid value and never inspect in-sample fit predictions.
- [ ] **Step 3 RED:** Assert separate h0/h1/h2 fixtures can yield different temperatures stored in their artifacts.
- [ ] **Step 4 RED:** Assert calibration maintains exact phase keys and finite simplex.
- [ ] **Step 5 Verify RED:** Run `.venv/bin/python -m pytest tests/test_economic_cycle_model.py -k temperature -q`.
- [ ] **Step 6 GREEN:** Implement stable temperature scaling over log probabilities and serialize the horizon-specific value.
- [ ] **Step 7 Verify GREEN:** Re-run all model tests.

### Task 10: Rolling-origin validation and publication gates

**Files:**
- Create: `finance/economic_cycle_validation.py`
- Create: `tests/test_economic_cycle_validation.py`

**Interfaces:**
- `run_rolling_origin_validation(panel, labels, *, initial_train_months=120) -> ValidationReport` retrains at each origin and emits out-of-fold h0/h1/h2 rows.
- Baselines: current-phase persistence and empirical historical-transition probabilities, both trained only through each origin.
- Metrics per horizon: multiclass Brier score, log loss, accuracy, expected calibration error with 10 fixed confidence bins, phase support, episode support, and coverage.
- `evaluate_publication_gate(report, horizon) -> PublicationDecision`.

```python
READY_GATE = {
    "minimum_origins": 120,
    "minimum_recession_episodes": 2,
    "minimum_targets_per_phase": 12,
    "minimum_complete_feature_ratio": 0.75,
    "maximum_ece": 0.12,
}
```

- [ ] **Step 1 RED:** Assert every validation prediction is generated by an artifact whose latest training target is strictly before the forecast origin; h1/h2 training pairs are included only when their shifted target month is also before the origin.
- [ ] **Step 2 RED:** Assert final retrospective labels used for scoring are never passed to the per-origin fit; the fit receives only the label vintages eligible by that origin.
- [ ] **Step 3 RED:** Hand-calculate Brier/log-loss/accuracy/ECE on a four-row fixture.
- [ ] **Step 4 RED:** Assert both baselines are forecast-origin safe and evaluated on the identical target rows.
- [ ] **Step 5 RED:** Assert `READY` requires all count/coverage/ECE gates and model Brier plus log loss no worse than the better baseline for that horizon.
- [ ] **Step 6 RED:** Assert insufficient recession episodes, rare phase support, non-finite probabilities, or baseline underperformance returns `LIMITED` with stable reason codes.
- [ ] **Step 7 RED:** Assert gates are horizon-specific: h0 can be READY while h1 or h2 remains LIMITED.
- [ ] **Step 8 Verify RED:** Run `.venv/bin/python -m pytest tests/test_economic_cycle_validation.py -q`.
- [ ] **Step 9 GREEN:** Implement expanding rolling origins, origin-eligible training labels, separately held evaluation truth, metrics, baseline comparisons, recession episode counting, and stable decisions.
- [ ] **Step 10 Verify GREEN:** Re-run validation plus model tests.

### Task 11: Training and materialization pipeline/jobs

**Files:**
- Create: `finance/economic_cycle_pipeline.py`
- Modify: `app/jobs/ingestion_jobs.py`
- Create: `tests/test_economic_cycle_pipeline.py`

**Interfaces:**
- `train_validate_economic_cycle_model(*, trained_through, loader=None, writer=None) -> dict[str, object]` persists an artifact only after validation report creation.
- `materialize_economic_cycle_snapshot(*, as_of_date, model_version=None, run_kind='current', loader=None, writer=None) -> CycleSnapshot`.
- `replay_economic_cycle_history(*, start_date, end_date, cadence='month_end', ...) -> dict[str, object]` fits/persists an origin-specific artifact whose training targets precede that origin, then uses the same as-of prediction path for each month.
- Jobs: `run_collect_economic_cycle_vintages(...)` and `run_materialize_economic_cycle(...)` return the repository `JobResult` contract.

```python
for origin in month_end_origins(start_date, end_date):
    vintage_rows = loader.load_for_origin(origin)
    artifact = fit_origin_artifact(training_targets_before=origin)
    writer.upsert_artifact(artifact)
    snapshot = predict_with_artifact(vintage_rows, artifact, origin)
    writer.upsert_snapshot(snapshot, run_kind="historical_replay")
```

- [ ] **Step 1 RED:** Assert training writes no approved artifact when any required gate metadata is missing; a partially approved artifact records per-horizon status.
- [ ] **Step 2 RED:** Assert materialization hides numeric probability fields for LIMITED horizons while preserving reason/warning evidence.
- [ ] **Step 3 RED:** Assert ten-year replay calls the strict as-of loader once per origin, persists an artifact with `trained_through < origin`, never reads the latest current artifact for a past origin, and is idempotent on rerun.
- [ ] **Step 4 RED:** Assert collection job delegates to the canonical collector, materialization job performs no provider call, and neither registers an unattended schedule.
- [ ] **Step 5 RED:** Assert errors preserve the latest approved artifact/snapshot rather than overwriting it with an ERROR row under the same business key.
- [ ] **Step 6 Verify RED:** Run `.venv/bin/python -m pytest tests/test_economic_cycle_pipeline.py -q`.
- [ ] **Step 7 GREEN:** Implement orchestration with injected seams, explicit cutoff dates, approval status, deterministic model version hash, and compact job details.
- [ ] **Step 8 Verify GREEN:** Run `.venv/bin/python -m pytest tests/test_economic_cycle_vintages.py tests/test_economic_cycle_features.py tests/test_economic_cycle_labels.py tests/test_economic_cycle_model.py tests/test_economic_cycle_validation.py tests/test_economic_cycle_results.py tests/test_economic_cycle_pipeline.py -q`.
- [ ] **Step 9 Commit:** Commit forecast/calibration/validation/pipeline/jobs as `경제 사이클 1개월 2개월 예측 검증 추가`.

**3차 완료 조건:** h0/h1/h2 are separately calibrated and gated by rolling-origin evidence; history/current runs are reproducible and a failed horizon cannot leak an ungated percentage into persistence.

---

## 4차 — Overview service와 시각화

### Task 12: Compact DB-only Overview service

**Files:**
- Create: `app/services/overview/economic_cycle.py`
- Create: `finance/economic_cycle_interpretation.py`
- Create: `tests/test_economic_cycle_service.py`
- Modify: `tests/test_service_contracts.py`

**Interfaces:**
- `build_economic_cycle_read_model(*, as_of_date=None, snapshot_loader=None, history_loader=None) -> dict[str, object]`.
- Stable top-level keys: `schema_version`, `status`, `as_of_date`, `model_version`, `headline`, `horizons`, `cycle_clock`, `evidence`, `market_implications`, `history`, `sources`, `limitations`.
- `history` is at most 121 month-end points and contains `date`, `phase`, `probabilities`, `status`, and a separate `nber_recession` flag.
- `build_market_implications(horizons, evidence) -> list[dict[str, object]]` produces conditional rate/equity/gold-dollar/commodity context and always sets `is_directional_forecast=False`.

```python
{
    "schema_version": "economic_cycle_v1",
    "status": "READY",
    "horizons": [
        {"horizon_months": 0, "label": "현재", "probabilities": {...}},
        {"horizon_months": 1, "label": "1개월 후", "probabilities": {...}},
        {"horizon_months": 2, "label": "2개월 후", "probabilities": {...}},
    ],
}
```

- [ ] **Step 1 RED:** Assert READY maps all three horizons, four probabilities, expected transition, evidence direction, source dates, separate model/NBER history, and ten-year history into JSON-safe primitives.
- [ ] **Step 2 RED:** Assert horizon-level LIMITED removes numeric percentages only for that horizon and retains a Korean reason.
- [ ] **Step 3 RED:** Assert no snapshot returns `LIMITED/NOT_MATERIALIZED`, DB/schema failures return stable `ERROR`, and neither path imports/calls the collector.
- [ ] **Step 4 RED:** Assert the service truncates oversized evidence/history and sorts months ascending without recalculating the model.
- [ ] **Step 5 RED:** Assert market implications cover rates, equities, gold/dollar, and commodities as conditional context, never as target price, buy/sell, or directional return prediction.
- [ ] **Step 6 RED:** Cover stable reason codes `NOT_COLLECTED`, `STALE`, `VINTAGE_GAP`, `VALIDATION_FAILED`, `PARTIAL_FACTORS`, and `READ_ERROR`.
- [ ] **Step 7 RED:** Extend the service boundary test so Market Context may import this service but the React/UI modules may not import `finance.data.economic_cycle_vintages`.
- [ ] **Step 8 Verify RED:** Run `.venv/bin/python -m pytest tests/test_economic_cycle_service.py tests/test_service_contracts.py -k 'economic_cycle or market_context' -q`.
- [ ] **Step 9 GREEN:** Implement the pure interpretation/read-model adapters and concise Korean caveats; no fetch, model fit, DB write, session mutation, or Streamlit import.
- [ ] **Step 10 Verify GREEN:** Re-run service tests.

### Task 13: Same-level Market Context selector and event bridge

**Files:**
- Modify: `app/web/overview/market_context.py`
- Modify: `app/web/overview/market_context_helpers.py`
- Modify: `app/services/overview/market_context_valuation.py`
- Modify: `app/web/overview/market_context_react_component.py`
- Create: `app/web/overview/economic_cycle_react_component.py`
- Create: `tests/test_market_context_economic_cycle.py`
- Modify: `tests/test_market_context_valuation.py`

**Interfaces:**
- Visible selector order is exactly `경제 사이클 | S&P 500 | 미국 개별주식`; default is `경제 사이클`.
- Session key: `overview_market_context_mode`; legacy/unknown values fall back to `economic_cycle`.
- The existing valuation payload accepts `default_instrument='sp500'|'us_stock'` and `show_instrument_selector=False` without changing default legacy callers.

```python
MODE_TO_INSTRUMENT = {
    "sp500": "sp500",
    "us_stock": "us_stock",
}
```

- [ ] **Step 1 RED:** Assert selector labels/order/default and unknown-value fallback.
- [ ] **Step 2 RED:** Assert `economic_cycle` renders only the cycle component and does not build either valuation read model.
- [ ] **Step 3 RED:** Assert each valuation choice builds only its selected instrument, passes `show_instrument_selector=False`, and preserves U.S.-stock search/collection events.
- [ ] **Step 4 RED:** Assert the cycle render path is DB-only and has no action event that can run collection/materialization.
- [ ] **Step 5 RED:** Assert existing callers without new args still get the current two-instrument valuation payload and internal selector.
- [ ] **Step 6 Verify RED:** Run `.venv/bin/python -m pytest tests/test_market_context_economic_cycle.py tests/test_market_context_valuation.py -q`.
- [ ] **Step 7 GREEN:** Add the Streamlit-level selector and two separate component bridges. Key valuation components by selected instrument so state cannot bleed across modes.
- [ ] **Step 8 Verify GREEN:** Re-run focused Overview tests.

### Task 14: Probability header, cycle clock, evidence, and regime ribbon

**Files:**
- Create: `app/web/streamlit_components/economic_cycle_workbench/package.json`
- Create: `app/web/streamlit_components/economic_cycle_workbench/tsconfig.json`
- Create: `app/web/streamlit_components/economic_cycle_workbench/vite.config.ts`
- Create: `app/web/streamlit_components/economic_cycle_workbench/index.html`
- Create: `app/web/streamlit_components/economic_cycle_workbench/src/main.tsx`
- Create: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`
- Create: `app/web/streamlit_components/economic_cycle_workbench/src/style.css`
- Modify: `app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx`
- Modify: `app/web/streamlit_components/market_context_valuation/src/style.css`
- Modify: `tests/test_market_context_economic_cycle.py`

**Interfaces:**
- React consumes `economic_cycle_v1` only and emits no provider/model/persistence event.
- Header: three horizon cards with four probability bars and dominant phase.
- Cycle clock: circular ordered phases with the last 18 months of model path as a solid trace and dotted +1/+2 markers; it is explanatory, not a forced deterministic path.
- Evidence: real-economy drivers first, forecast-context evidence second, with `강화 / 약화 / 중립` and source basis.
- Market implications: conditional rates/equities/gold-dollar/commodities context, explicitly separated from forecasts and actions.
- Ribbon: 10-year monthly model phase color band, separately styled NBER recession shading, hover/tap replay detail, LIMITED hatch, and current marker.
- Method/quality disclosure: data cutoff, model version, validation state, warnings, and methodology link after the main reading flow.

```ts
type Phase = "recovery" | "expansion" | "slowdown" | "recession"
type PublicationStatus = "READY" | "LIMITED"

type Horizon = {
  horizon_months: 0 | 1 | 2
  probabilities: Record<Phase, number> | null
  dominant_phase: Phase | null
  publication_status: PublicationStatus
  reason?: string
}
```

- [ ] **Step 1 RED:** Add source-contract assertions for the exact phase order, three horizon labels, probability bar semantics, 18-month solid clock trace, evidence/market-implication grouping, model-vs-NBER ribbon, methodology disclosure, and limitation copy.
- [ ] **Step 2 RED:** Assert READY never renders one phase without the other three probabilities; LIMITED never formats a fake `0%`.
- [ ] **Step 3 RED:** Assert there is no `fetch(`, Axios, job/run button, trading CTA, or automatic refresh loop in the component source.
- [ ] **Step 4 RED:** Assert the valuation component honors `show_instrument_selector=false` while preserving the legacy default.
- [ ] **Step 5 Verify RED:** Run `.venv/bin/python -m pytest tests/test_market_context_economic_cycle.py tests/test_market_context_valuation.py -q`.
- [ ] **Step 6 GREEN:** Build semantic HTML/SVG/CSS with keyboard-focusable horizon/evidence/ribbon details, Korean labels, and color plus text/pattern redundancy.
- [ ] **Step 7 GREEN:** Add responsive breakpoints so horizon cards stack and the clock/ribbon remain readable at 420px without horizontal scroll.
- [ ] **Step 8 Build:** Run `npm install` once only if lockfile/bootstrap is absent, then `npm run build` in `app/web/streamlit_components/economic_cycle_workbench`; run `npm run build` in `app/web/streamlit_components/market_context_valuation` after its compatibility change.
- [ ] **Step 9 Verify GREEN:** Re-run focused Python tests and inspect generated static asset references.
- [ ] **Step 10 Commit:** Commit service/selector/components/static/tests as `시장 맥락 경제 사이클 시각화 추가`.

**4차 완료 조건:** the user can select the cycle beside S&P 500/U.S. stock, read current/+1M/+2M uncertainty and evidence, and scan ten years of history without seeing an operational console or causing a provider call.

---

## 5차 — Actual data QA, regression, durable docs, closeout

### Task 15: Bootstrap actual vintages and verify publication behavior

**Files:**
- No source modification unless a verified defect is found and handled with a new RED test.
- Update: `.aiworkspace/note/finance/tasks/active/overview-market-context-us-economic-cycle-v1-20260716/RUNS.md`
- Update: `.aiworkspace/note/finance/tasks/active/overview-market-context-us-economic-cycle-v1-20260716/RISKS.md`

**Interfaces:**
- Environment input: `FRED_API_KEY`.
- Persistent outputs: vintage rows, one validation artifact, current snapshot, and up to 121 monthly replay snapshots.

- [ ] **Step 1 Schema:** Run the repository schema sync path and verify the three new tables plus their unique/index contracts.
- [ ] **Step 2 Collect:** Run the explicit vintage collection job for the locked catalog; record per-series counts/date ranges without copying credentials or raw payloads into docs.
- [ ] **Step 3 Train/validate:** Run training through the latest fully available month and record h0/h1/h2 origin counts, phase support, recession episodes, Brier, log loss, ECE, baselines, and gate decisions.
- [ ] **Step 4 Materialize:** Only approved horizons publish numeric probabilities. Create current plus ten-year month-end replay snapshots and rerun once to prove idempotence.
- [ ] **Step 5 Failure branch:** If actual data cannot meet a gate, retain `LIMITED`, record the exact reason and coverage gap, and do not weaken thresholds or hand-edit artifact status.
- [ ] **Step 6 Data audit:** Sample at least one payroll and one recession-era origin; compare stored eligible vintage dates against the official FRED/ALFRED response metadata.

### Task 16: Focused, regression, and Browser QA

**Files:**
- Update test files only when a newly discovered defect first has a failing regression test.
- Store QA screenshot outside staged files.

- [ ] **Step 1 Focused Python:** Run `.venv/bin/python -m pytest tests/test_economic_cycle_vintages.py tests/test_economic_cycle_features.py tests/test_economic_cycle_labels.py tests/test_economic_cycle_model.py tests/test_economic_cycle_validation.py tests/test_economic_cycle_results.py tests/test_economic_cycle_pipeline.py tests/test_economic_cycle_service.py tests/test_market_context_economic_cycle.py tests/test_market_context_valuation.py -q`.
- [ ] **Step 2 Boundary regression:** Run `.venv/bin/python -m pytest tests/test_service_contracts.py -k 'overview or market_context' -q`.
- [ ] **Step 3 Compile:** Run `.venv/bin/python -m py_compile finance/economic_cycle_catalog.py finance/economic_cycle_features.py finance/economic_cycle_labels.py finance/economic_cycle_model.py finance/economic_cycle_validation.py finance/economic_cycle_pipeline.py finance/economic_cycle_interpretation.py finance/data/economic_cycle_vintages.py finance/data/economic_cycle_results.py finance/loaders/economic_cycle.py app/services/overview/economic_cycle.py app/web/overview/economic_cycle_react_component.py`.
- [ ] **Step 4 Frontend:** Run both component `npm run build` commands from Task 14.
- [ ] **Step 5 Diff:** Run `git diff --check` and `git status --short`; confirm unrelated research and `.superpowers/` remain unstaged.
- [ ] **Step 6 Browser desktop:** Open the existing local app, select `경제 사이클`, verify all four probabilities for READY horizons, cycle clock, evidence ordering, ribbon hover, source dates, and zero new console errors.
- [ ] **Step 7 Browser 420px:** Verify selector/cards/clock/ribbon/evidence have `document.documentElement.scrollWidth - clientWidth == 0`, keyboard focus is visible, and LIMITED copy is readable.
- [ ] **Step 8 Regression navigation:** Switch to `S&P 500` and `미국 개별주식`; verify their established read/search/collection behaviors and no nested duplicate selector.
- [ ] **Step 9 Evidence:** Save one QA screenshot outside git staging and attach its absolute path in final handoff.

### Task 17: Durable documentation and task closeout

**Files:**
- Modify: `.aiworkspace/note/finance/docs/data/README.md`
- Modify: `.aiworkspace/note/finance/docs/data/DB_SCHEMA_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/data/TABLE_SEMANTICS.md`
- Modify: `.aiworkspace/note/finance/docs/data/DATA_FLOW_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/data/DATA_QUALITY_AND_PIT_NOTES.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/tasks/active/STATUS_MANIFEST.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-market-context-us-economic-cycle-v1-20260716/{PLAN,DESIGN,STATUS,NOTES,RUNS,RISKS}.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

- [ ] **Step 1 Data docs:** Document all three tables, business keys, revision interval meaning, as-of selection, retention, UPSERT, and artifact/snapshot compactness.
- [ ] **Step 2 Architecture docs:** Document collector -> raw vintage DB -> as-of loader -> feature/label/model/validation -> approved artifact/snapshot -> service -> UI and the no-direct-fetch boundary.
- [ ] **Step 3 Runbook:** Add key setup, manual collection, training/materialization, validation-gate interpretation, idempotent replay, and failure recovery without exposing an app diagnostic panel.
- [ ] **Step 4 Product/task docs:** Record final 1차~5차 status, actual gate metrics, remaining limitations, QA commands, screenshot path, and next optional expansion (ADS/WEI connector research only if separately approved).
- [ ] **Step 5 Pointer sync:** Mark no task complete until code, actual gate behavior, Browser QA, durable docs, and clean staged diff all agree.
- [ ] **Step 6 Verify docs:** Run `rg -n 'macro_series_vintage_observation|economic_cycle_model_artifact|economic_cycle_snapshot' .aiworkspace/note/finance/docs` and verify canonical links resolve.
- [ ] **Step 7 Final verification:** Re-run `git diff --check`, the focused suite, and `git status --short` immediately before completion.
- [ ] **Step 8 Commit:** Commit QA/docs/closeout as `경제 사이클 예측 기능 검증과 문서 정렬`.

**5차 완료 조건:** actual data either satisfies each horizon gate or is honestly LIMITED; desktop/mobile Browser QA passes; S&P/U.S.-stock regressions pass; and durable docs precisely describe the point-in-time and publication boundaries.

## End-to-End Acceptance Checklist

- [ ] A historical origin cannot read a later release or revision.
- [ ] The current label is invariant to financial/inflation input changes.
- [ ] +1M/+2M targets are direct horizons with constrained transitions, not deterministic clock advancement.
- [ ] Every published horizon shows four calibrated probabilities summing to one.
- [ ] Every unpublished horizon is visibly LIMITED with no fake numeric probability.
- [ ] Rolling-origin metrics beat or equal the better approved baseline and meet count/coverage/ECE gates.
- [ ] The cycle UI reads only persisted compact snapshots and emits no provider/model job action.
- [ ] The three same-level Market Context choices work without nested duplicate navigation.
- [ ] Ten-year ribbon uses monthly historical replay snapshots from the same as-of path.
- [ ] Model phases and official NBER recession shading remain visually and semantically separate.
- [ ] Market implications are conditional context for rates/equities/gold-dollar/commodities, never directional return or trading instructions.
- [ ] S&P 500 and U.S.-stock valuation tests/build/navigation remain green.
- [ ] Data, architecture, runbook, roadmap, active task, and root handoff docs are synchronized.

## Implementation Handoff

Implementation begins at Task 1 and stops at each stage completion checkpoint for review. Use small coherent Korean commits listed above. If actual validation fails, the correct outcome is a tested `LIMITED` product state and a documented evidence gap, not a relaxed threshold.

## Primary Implementation Source

- [FRED API: Series Observations](https://fred.stlouisfed.org/docs/api/fred/series_observations.html) — official parameters for real-time bounds, vintage output modes, JSON pagination, and API-key authentication used by Task 2.
