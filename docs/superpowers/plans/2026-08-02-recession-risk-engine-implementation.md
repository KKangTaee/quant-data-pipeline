# Recession Risk Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a new raw-data U.S. five-state recession-risk model for current, 3-, 6-, and 12-month horizons without reusing the existing economic-cycle model or probabilities.

**Architecture:** Create a separate `finance/recession_risk/` package, separate artifact/snapshot schemas, and strict point-in-time panels from labor, income, consumption, production, sales, curve, spread, and financial-condition observations. NBER/USREC dates are ex-post evaluation anchors; exact probabilities remain unavailable until rare-event and calibration gates pass.

**Tech Stack:** Python 3.12, pandas, NumPy, MySQL, existing generic macro-vintage loader contract, React/TypeScript, pytest, Vitest, Browser QA.

## Global Constraints

- No `finance.economic_cycle*`, `economic_cycle_snapshot`, `economic_cycle_model_artifact`, or existing cycle probability may be imported, queried, copied, or used as a label.
- Use only raw point-in-time observations whose `released_at <= as_of_at`.
- NBER/USREC is a historical label/evaluation anchor, not a current official declaration in UI copy.
- Horizons are `0`, `3`, `6`, and `12` months; each has independent metrics/publication status.
- Recession status cannot change inflation/policy/equity outputs unless its artifact is independently `READY` and the consuming model version explicitly records the dependency.
- If validation is insufficient, publish `NOT_AVAILABLE` or `LIMITED`, never the old cycle result.

---

## File Structure

### Create

- `finance/recession_risk/__init__.py`
- `finance/recession_risk/contracts.py`
- `finance/recession_risk/catalog.py`
- `finance/recession_risk/labels.py`
- `finance/recession_risk/panel.py`
- `finance/recession_risk/model.py`
- `finance/recession_risk/validation.py`
- `finance/recession_risk/pipeline.py`
- `finance/data/recession_risk_results.py`
- `finance/loaders/recession_risk.py`
- `app/services/overview/recession_risk.py`
- `app/web/streamlit_components/economic_cycle_workbench/src/RecessionRiskPanel.tsx`
- `tests/test_recession_risk_schema.py`
- `tests/test_recession_risk_catalog.py`
- `tests/test_recession_risk_labels.py`
- `tests/test_recession_risk_panel.py`
- `tests/test_recession_risk_model.py`
- `tests/test_recession_risk_validation.py`
- `tests/test_recession_risk_pipeline.py`
- `tests/test_recession_risk_service.py`

### Modify

- `finance/data/db/schema.py`: add `RECESSION_RISK_SCHEMAS` without modifying economic-cycle schemas.
- `app/services/overview/inflation_policy.py`: attach the independently built recession section.
- `app/web/streamlit_components/economic_cycle_workbench/src/inflationPolicyTypes.ts`
- `app/web/streamlit_components/economic_cycle_workbench/src/InflationPolicyWorkbench.tsx`
- `app/web/streamlit_components/economic_cycle_workbench/src/InflationPolicyWorkbench.test.tsx`
- `.aiworkspace/note/finance/tasks/active/recession-risk-engine/`
- `.aiworkspace/note/finance/phases/active/inflation-policy-yield-path/{TASKS,STATUS,RISKS,INTEGRATION}.md`

## Stable Interfaces

```python
RECESSION_STATES = (
    "expansion",
    "growth_slowdown",
    "recession_boundary",
    "recession",
    "recovery_transition",
)
RECESSION_HORIZONS = (0, 3, 6, 12)

@dataclass(frozen=True)
class RecessionHorizonForecast:
    horizon_months: int
    state_probabilities: dict[str, float] | None
    dominant_state: str | None
    publication_status: str
    reason_codes: tuple[str, ...]

@dataclass(frozen=True)
class RecessionRiskSnapshot:
    as_of_at: str
    model_version: str
    horizons: tuple[RecessionHorizonForecast, ...]
    top_evidence: tuple[dict[str, object], ...]
    freshness: dict[str, object]
    publication_status: str
```

### Task 1: Add separate schema, catalog, and result boundaries

**Files:**
- Modify: `finance/data/db/schema.py`
- Create: `finance/recession_risk/__init__.py`
- Create: `finance/recession_risk/contracts.py`
- Create: `finance/recession_risk/catalog.py`
- Create: `finance/data/recession_risk_results.py`
- Create: `finance/loaders/recession_risk.py`
- Create: `tests/test_recession_risk_schema.py`
- Create: `tests/test_recession_risk_catalog.py`
- Create: `.aiworkspace/note/finance/tasks/active/recession-risk-engine/{PLAN,DESIGN,STATUS,NOTES,RUNS,RISKS}.md`

**Interfaces:**
- Consumes: `macro_series_vintage_observation` and generic DB client.
- Produces `RECESSION_RISK_SCHEMAS` with `recession_risk_model_artifact` and `recession_risk_snapshot`, plus:

```python
def get_recession_risk_catalog() -> tuple[RecessionSeriesSpec, ...]: ...
def get_recession_model_features() -> tuple[RecessionSeriesSpec, ...]: ...
```

- [ ] **Step 1: Write failing schema and import-guard tests**

```python
def test_recession_schema_is_separate() -> None:
    from finance.data.db.schema import RECESSION_RISK_SCHEMAS
    assert set(RECESSION_RISK_SCHEMAS) == {
        "recession_risk_model_artifact", "recession_risk_snapshot"
    }
    assert all("economic_cycle" not in sql for sql in RECESSION_RISK_SCHEMAS.values())

def test_recession_package_has_no_existing_cycle_import() -> None:
    source = "\n".join(path.read_text() for path in Path("finance/recession_risk").glob("*.py"))
    assert "finance.economic_cycle" not in source
```

- [ ] **Step 2: Write the failing catalog test**

```python
def test_catalog_uses_raw_activity_labor_and_financial_series() -> None:
    ids = {item.series_id for item in get_recession_risk_catalog()}
    assert {"UNRATE", "PAYEMS", "ICSA", "AWHMAN", "TEMPHELPS"} <= ids
    assert {"INDPRO", "W875RX1", "PCEC96", "CMRMTSPL"} <= ids
    assert {"T10Y3M", "BAMLH0A0HYM2", "ANFCI"} <= ids
    assert "USREC" not in {item.series_id for item in get_recession_model_features()}
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_recession_risk_schema.py tests/test_recession_risk_catalog.py -q
```

Expected: FAIL on missing schemas/package.

- [ ] **Step 4: Implement contracts, schemas, catalog, and stores**

Artifact key: model version, trained cutoff, horizon. Snapshot key: as-of, model version, run kind. Both store validation/publication reasons. Catalog metadata defines frequency, transform, group, direction, minimum history, and required horizons without importing the existing catalog.

- [ ] **Step 5: Implement strict raw/result loaders**

Raw loader selects release-eligible latest vintages for catalog series. Result loader reads only recession tables. Neither SQL string may contain `economic_cycle`.

- [ ] **Step 6: Run tests and commit**

```bash
.venv/bin/python -m pytest tests/test_recession_risk_schema.py tests/test_recession_risk_catalog.py -q
git add finance/data/db/schema.py finance/recession_risk finance/data/recession_risk_results.py \
  finance/loaders/recession_risk.py tests/test_recession_risk_schema.py \
  tests/test_recession_risk_catalog.py .aiworkspace/note/finance/tasks/active/recession-risk-engine
git commit -m "신규 침체 위험 데이터 계약 추가"
```

### Task 2: Generate transparent five-state historical labels

**Files:**
- Create: `finance/recession_risk/labels.py`
- Create: `tests/test_recession_risk_labels.py`

**Interfaces:**
- Consumes: historical raw coincident indicators and ex-post `USREC` anchor.
- Produces:

```python
def build_recession_state_labels(
    coincident_panel: pd.DataFrame,
    usrec: pd.Series,
    *, boundary_months: int = 3,
    recovery_months: int = 6,
) -> pd.Series: ...
```

- [ ] **Step 1: Write failing state-order tests**

```python
def test_nber_windows_define_boundary_recession_and_recovery() -> None:
    labels = build_recession_state_labels(coincident_fixture(), usrec_fixture(), boundary_months=3, recovery_months=6)
    assert list(labels.loc["2007-10":"2007-12"].unique()) == ["recession_boundary"]
    assert set(labels.loc["2008-01":"2009-06"]) == {"recession"}
    assert set(labels.loc["2009-07":"2009-12"]) == {"recovery_transition"}
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_recession_risk_labels.py -q
```

Expected: FAIL on missing label builder.

- [ ] **Step 3: Implement exact label precedence**

Precedence is: `recession` where USREC=1; `recovery_transition` for six months after a 1→0 transition; `recession_boundary` for three months before a 0→1 transition; among remaining months `growth_slowdown` when at least two of four coincident 6-month momentum measures are negative, otherwise `expansion`. Require INDPRO, W875RX1, PAYEMS, and CMRMTSPL/PCEC96; missing breadth yields null label.

- [ ] **Step 4: Document ex-post versus real-time meaning in code**

Docstring states labels are historical supervised targets and not inputs/current official declarations. The current model sees raw features only.

- [ ] **Step 5: Run tests and commit**

```bash
.venv/bin/python -m pytest tests/test_recession_risk_labels.py -q
git add finance/recession_risk/labels.py tests/test_recession_risk_labels.py
git commit -m "침체 위험 다섯 상태 학습 라벨 추가"
```

### Task 3: Build the PIT panel and direct-horizon model

**Files:**
- Create: `finance/recession_risk/panel.py`
- Create: `finance/recession_risk/model.py`
- Create: `tests/test_recession_risk_panel.py`
- Create: `tests/test_recession_risk_model.py`

**Interfaces:**
- Produces:

```python
def build_recession_training_panel(*, raw_rows: Sequence[Mapping[str, object]], labels: pd.Series, origins: Sequence[str]) -> pd.DataFrame: ...

@dataclass(frozen=True)
class RecessionRiskArtifact:
    horizon_months: int
    feature_names: tuple[str, ...]
    rule_weights: dict[str, float]
    class_means: dict[str, dict[str, float]]
    class_variances: dict[str, dict[str, float]]
    calibration_temperature: float
    trained_through: str
    publication_status: str
    reason_codes: tuple[str, ...]

def fit_recession_risk_model(panel: pd.DataFrame, *, horizon_months: int) -> RecessionRiskArtifact: ...
def predict_recession_state_probabilities(artifact: RecessionRiskArtifact, feature_row: Mapping[str, object]) -> dict[str, float]: ...
```

- [ ] **Step 1: Write failing PIT and horizon tests**

Test next-release exclusion, transform/scaler fitted through origin only, targets shifted exactly 0/3/6/12 months, and each probability row has the five exact keys summing to 1.

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_recession_risk_panel.py tests/test_recession_risk_model.py -q
```

Expected: FAIL on missing panel/model.

- [ ] **Step 3: Implement transparent features**

Labor: unemployment gap/change, payroll breadth/change, claims, hours, temporary help. Activity: production, real income, consumption, sales momentum/breadth. Financial: curve, high-yield spread, ANFCI. Track source release date, staleness, and missingness per origin.

- [ ] **Step 4: Implement hybrid direct-horizon model**

Blend a transparent rule score with diagonal-Gaussian class likelihoods; estimate component weight and temperature on prior rolling origins. Fit each horizon independently and return `LIMITED` when a state has insufficient support.

- [ ] **Step 5: Run tests and commit**

```bash
.venv/bin/python -m pytest tests/test_recession_risk_panel.py tests/test_recession_risk_model.py -q
git add finance/recession_risk/panel.py finance/recession_risk/model.py \
  tests/test_recession_risk_panel.py tests/test_recession_risk_model.py
git commit -m "침체 위험 PIT 모델 추가"
```

### Task 4: Add rare-event validation and publication gates

**Files:**
- Create: `finance/recession_risk/validation.py`
- Create: `tests/test_recession_risk_validation.py`

**Interfaces:**
- Produces:

```python
def rolling_origin_validate_recession(panel: pd.DataFrame, *, horizons: Sequence[int] = RECESSION_HORIZONS, minimum_train_rows: int = 180) -> RecessionValidationReport: ...
def decide_recession_publication(report: RecessionValidationReport, *, horizon_months: int) -> PublicationDecision: ...
```

- [ ] **Step 1: Write failing event-metric tests**

Test Brier, log loss, PR-AUC, reliability, event recall, false-alarm episodes, lead/lag, persistence baseline, curve baseline, Sahm-style baseline, and separate horizon gates.

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_recession_risk_validation.py -q
```

Expected: FAIL on missing validation.

- [ ] **Step 3: Implement chronological event evaluation**

Group consecutive alerts into one event, match to distinct NBER recessions, and count unmatched alert episodes as false alarms. Compute PR-AUC because recession months are rare; do not rely on accuracy or AUROC alone.

- [ ] **Step 4: Implement independent gates**

`READY` requires at least 180 origins, three distinct recession episodes, finite/simplex probabilities, Brier/log loss no worse than the best simple baseline, calibrated reliability, and non-zero event recall. A horizon failing any condition publishes `LIMITED`; no horizon inherits another horizon's status.

- [ ] **Step 5: Run tests and commit**

```bash
.venv/bin/python -m pytest tests/test_recession_risk_validation.py tests/test_recession_risk_model.py -q
git add finance/recession_risk/validation.py tests/test_recession_risk_validation.py
git commit -m "침체 위험 확률 검증 게이트 추가"
```

### Task 5: Materialize snapshots and build the independent service

**Files:**
- Create: `finance/recession_risk/pipeline.py`
- Create: `app/services/overview/recession_risk.py`
- Create: `tests/test_recession_risk_pipeline.py`
- Create: `tests/test_recession_risk_service.py`
- Modify: `app/services/overview/inflation_policy.py`

**Interfaces:**
- Produces:

```python
def train_recession_risk_artifacts(*, train_through: str) -> dict[int, RecessionRiskArtifact]: ...
def materialize_recession_risk_snapshot(*, as_of_at: str, model_version: str | None = None) -> dict[str, object]: ...
def build_recession_risk_read_model(*, as_of_at: str | None = None, snapshot_loader: Callable[..., Mapping[str, object] | None] | None = None) -> dict[str, object]: ...
```

- [ ] **Step 1: Write failing unavailable-before-ready tests**

```python
def test_unvalidated_recession_does_not_publish_probabilities() -> None:
    model = build_recession_risk_read_model(snapshot_loader=lambda **_: limited_snapshot_fixture())
    assert model["publication_status"] == "NOT_AVAILABLE"
    assert all(item["state_probabilities"] is None for item in model["horizons"])

def test_inflation_service_does_not_substitute_cycle_probabilities() -> None:
    model = build_inflation_policy_read_model(snapshot_loader=macro_snapshot_loader, recession_builder=lambda **_: unavailable_recession_model())
    assert model["recession"]["publication_status"] == "NOT_AVAILABLE"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_recession_risk_pipeline.py tests/test_recession_risk_service.py tests/test_inflation_policy_service.py -q
```

Expected: FAIL on missing pipeline/service.

- [ ] **Step 3: Implement artifact/snapshot materialization**

Train/validate/save each horizon, then write one snapshot only after JSON/simplex validation. Preserve horizon statuses. If none are ready, top-level status is `NOT_AVAILABLE`; stored validation evidence remains accessible without numeric probabilities.

- [ ] **Step 4: Implement independent read model and composition**

Service keys: schema version, status, as-of, model version, horizons, evidence, freshness, warnings, NBER disclaimer. The inflation-policy service calls this independent builder only to attach display data; it never passes cycle payloads or uses recession output to recompute current macro probabilities.

- [ ] **Step 5: Run tests and commit**

```bash
.venv/bin/python -m pytest tests/test_recession_risk_pipeline.py tests/test_recession_risk_service.py tests/test_inflation_policy_service.py -q
git add finance/recession_risk/pipeline.py app/services/overview/recession_risk.py \
  app/services/overview/inflation_policy.py tests/test_recession_risk_pipeline.py \
  tests/test_recession_risk_service.py
git commit -m "침체 위험 스냅샷과 조회 모델 추가"
```

### Task 6: Add the UI, verify independence, and close the phase

**Files:**
- Create: `app/web/streamlit_components/economic_cycle_workbench/src/RecessionRiskPanel.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/inflationPolicyTypes.ts`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/InflationPolicyWorkbench.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/InflationPolicyWorkbench.test.tsx`
- Modify: `.aiworkspace/note/finance/tasks/active/recession-risk-engine/{STATUS,NOTES,RUNS,RISKS}.md`
- Modify: `.aiworkspace/note/finance/phases/active/inflation-policy-yield-path/{TASKS,STATUS,RISKS,INTEGRATION}.md`
- Modify: `.aiworkspace/note/finance/docs/flows/README.md`
- Modify: `.aiworkspace/note/finance/docs/data/DB_SCHEMA_MAP.md`

**Interfaces:**
- Consumes: independent recession read model.
- Produces: five-state/horizon panel or explicit unavailable state.

- [ ] **Step 1: Write failing React state tests**

Test state labels `확장|성장 둔화|침체 경계|침체|회복 전환`, horizons `현재|3개월|6개월|12개월`, NBER disclaimer, and no probability text when unavailable.

- [ ] **Step 2: Implement the panel**

Place recession after equity stress. Show all five probabilities only for each `READY` horizon, top evidence and release dates, and the copy `모델 추정이며 NBER 공식 판정이 아닙니다.` For unavailable status show the validation reason, not the old cycle view.

- [ ] **Step 3: Run complete automated verification**

```bash
.venv/bin/python -m pytest tests/test_recession_risk_*.py tests/test_inflation_policy_service.py -q
npm --prefix app/web/streamlit_components/economic_cycle_workbench test
npm --prefix app/web/streamlit_components/economic_cycle_workbench run build
! rg -n "finance\.economic_cycle|economic_cycle_snapshot|economic_cycle_model_artifact" \
  finance/recession_risk finance/data/recession_risk_results.py \
  finance/loaders/recession_risk.py app/services/overview/recession_risk.py
git diff --check
```

Expected: tests/build pass and `rg` returns no matches.

- [ ] **Step 4: Run Browser QA**

Verify ready and unavailable fixtures, all horizons, mobile layout, disclaimer, no stale cycle substitution, no overflow, and zero console/page errors. Save one generated screenshot outside the commit.

- [ ] **Step 5: Use `finance-doc-sync` and close states truthfully**

Set recession task complete only with independent validation/QA evidence. Mark the parent phase `State: complete` only if data, core engines, workbench, equity, and recession completion criteria are all satisfied; otherwise use `active` or `verification_only` with the exact remaining gate.

- [ ] **Step 6: Commit**

```bash
git add app/web/streamlit_components/economic_cycle_workbench/src/RecessionRiskPanel.tsx \
  app/web/streamlit_components/economic_cycle_workbench/src/inflationPolicyTypes.ts \
  app/web/streamlit_components/economic_cycle_workbench/src/InflationPolicyWorkbench.tsx \
  app/web/streamlit_components/economic_cycle_workbench/src/InflationPolicyWorkbench.test.tsx \
  app/web/streamlit_components/economic_cycle_workbench/component_static \
  .aiworkspace/note/finance/tasks/active/recession-risk-engine \
  .aiworkspace/note/finance/phases/active/inflation-policy-yield-path \
  .aiworkspace/note/finance/docs/flows/README.md \
  .aiworkspace/note/finance/docs/data/DB_SCHEMA_MAP.md
git commit -m "신규 침체 위험 기능 검증 완료"
```
