# Overview Futures Macro Probabilistic State Outlook V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan.

**Goal:** 완료된 선물 session의 동일 정의 상태 `S(t)`를 기준으로 실제 30-session trail과 검증된 5D/20D 확률·terminal region을 제공하고, baseline 우위가 없으면 `NO_EDGE`를 공개한다.

**Architecture:** `raw daily futures -> completed-session normalization -> canonical state/target -> momentum candidate + PIT macro/event soft conditioning -> nested rolling-origin validation -> immutable forecast history + current read model -> React observed/forecast surface` 경계를 유지한다. UI는 DB에 저장된 compact snapshot만 읽고 provider나 모델 builder를 직접 호출하지 않는다.

**Tech Stack:** Python 3.12, pandas, MySQL/PyMySQL, unittest/pytest-compatible tests, React 18, TypeScript 5.7, Vite 6, Streamlit custom component.

## Global Constraints

- 관측, historical origin, target, realized outcome은 하나의 `state_from_feature_row()`를 재사용한다.
- 가장 최근 raw candle이 아니라 가장 최근 `FINAL` canonical session이 current state다.
- macro는 `economic_cycle_snapshot.run_kind='historical_replay'` 저장 row만 사용한다. 과거 origin에 현재 macro row를 복사하지 않는다.
- event는 official stored schedule이며 `collected_at <= origin known-at cutoff`인 row만 과거 origin에 사용한다. consensus/actual surprise 방향은 만들지 않는다.
- 5D와 20D는 독립적으로 candidate/status를 선택한다.
- probability, coordinate, vector publication status를 분리한다. coordinate가 `VERIFIED`가 아니면 marker/region/vector를 모두 숨긴다.
- 당일 재실행 때 input/model identity가 같으면 history insert는 idempotent해야 한다.
- implementation 중 게이트 임계값을 실제 결과에 맞춰 완화하지 않는다. 변경이 필요하면 별도 설계 승인을 받는다.
- 각 task는 RED -> GREEN -> focused regression -> commit 순서로 수행한다.

---

## 1차 — Data / Target Contract

### Task 1: Completed futures session resolver

**Files:**

- Create: `app/services/futures_macro_sessions.py`
- Modify: `app/services/futures_macro_validation.py:62-87`
- Modify: `app/services/futures_macro_pattern_validation.py:994-1040`
- Test: `tests/test_futures_macro_sessions.py`
- Test: `tests/test_futures_macro_pattern_validation.py`

**Contract:**

```python
@dataclass(frozen=True)
class FuturesDailySession:
    provider_symbol: str
    raw_candle_date: str
    session_date: str | None
    status: Literal["FINAL", "IN_PROGRESS", "UNKNOWN"]
    reason: str

@dataclass(frozen=True)
class CompletedFuturesInput:
    rows: list[dict[str, object]]
    latest_final_session: str | None
    pending_session: str | None
    excluded_unknown_rows: int

def resolve_futures_daily_session(
    provider_symbol: str,
    candle_time_utc: object,
    collected_at: object,
    evaluation_time: datetime,
) -> FuturesDailySession: ...

def select_completed_futures_daily_rows(
    rows: Sequence[dict[str, object]],
    *, evaluation_time: datetime,
) -> CompletedFuturesInput: ...
```

Canonical policy is versioned as `futures_daily_session_v1`:

- timezone 없는 timestamp는 UTC provider timestamp로 해석한다.
- Sunday provider label은 다음 Monday trade date로 mapping한다.
- Monday–Friday label은 그 날짜를 유지한다.
- Saturday 또는 parse 불가 label은 `UNKNOWN`으로 제외한다.
- New York 평가일보다 이전 session은 `FINAL`이다.
- 동일 session은 `18:15 America/New_York` 이후에만 `FINAL`, 이전은 `IN_PROGRESS`다.
- 중복 `(provider_symbol, canonical session_date)`는 raw `candle_time_utc`, `collected_at` 내림차순 첫 row를 유지한다.
- 반환 row에 canonical `Date`와 `raw_candle_time_utc`를 모두 보존한다.

**Step 1 — RED:** Friday final, Sunday-to-Monday, Monday cutoff 전/후, Saturday unknown, canonical duplicate collapse test를 작성한다.

```bash
.venv/bin/python -m unittest tests.test_futures_macro_sessions -v
```

Expected: `app.services.futures_macro_sessions` import failure.

**Step 2 — GREEN:** `datetime`, `time`, `zoneinfo.ZoneInfo`로 resolver를 구현한다. provider 호출과 제3자 calendar dependency는 추가하지 않는다.

**Step 3 — Wire raw evidence:** `_load_validation_futures_rows()` SQL에 `collected_at`를 추가한다. Outlook loader에서 candle normalization 전 resolver를 호출하고 다음 metadata를 붙인다.

```python
"session": {
    "resolver_version": FUTURES_DAILY_SESSION_VERSION,
    "latest_final_session": completed.latest_final_session,
    "pending_session": completed.pending_session,
    "status": "PENDING_SESSION_FINALIZATION" if completed.pending_session else "OBSERVED",
}
```

**Step 4 — Regression:**

```bash
.venv/bin/python -m unittest tests.test_futures_macro_sessions tests.test_futures_macro_pattern_validation -v
```

Expected: pass.

**Step 5 — Commit:**

```bash
git add app/services/futures_macro_sessions.py app/services/futures_macro_validation.py app/services/futures_macro_pattern_validation.py tests/test_futures_macro_sessions.py tests/test_futures_macro_pattern_validation.py
git commit -m "선물 일봉 완료 세션 계약 추가"
```

### Task 2: One canonical state function and same-state targets

**Files:**

- Modify: `app/services/futures_macro_pattern.py:136-476`
- Modify: `app/services/futures_macro_pattern_validation.py:193-344`
- Test: `tests/test_futures_macro_pattern.py`
- Test: `tests/test_futures_macro_pattern_validation.py`

**Contract:**

```python
PATTERN_STATE_SCHEMA_VERSION = "futures_macro_state_v2"
OBSERVED_TRAIL_SESSIONS = 30

def state_from_feature_row(state_date: object, row: pd.Series) -> dict[str, object]:
    """Return the only canonical coordinate/regime/transition state shape."""

def build_pattern_state_frame(feature_frame: pd.DataFrame) -> pd.DataFrame:
    """Return one state row per canonical completed session."""

def build_same_state_target_frame(
    feature_frame: pd.DataFrame,
    *, horizons: Sequence[int] = (5, 20),
) -> pd.DataFrame: ...
```

Target frame columns:

```text
origin_date, terminal_date, horizon,
origin_x, origin_y, terminal_x, terminal_y, delta_x, delta_y,
terminal_regime, terminal_transition,
terminal_<family>__5d_z for all six families
```

`terminal_date = state_frame.index[position + horizon]`이며 calendar-day 연산을 하지 않는다. `build_current_pattern_snapshot()`의 모든 path point는 `state_from_feature_row()`를 사용하고 default `path_limit=30`이다. Ribbon은 별도로 60 rows를 유지할 수 있다.

**Step 1 — RED:** path/direct state 동일성, future row append 불변성, 5D row spacing, delta identity, 30 consecutive observed points를 test한다.

```bash
.venv/bin/python -m unittest tests.test_futures_macro_pattern tests.test_futures_macro_pattern_validation -v
```

Expected: 신규 function 부재와 old forward-return target 때문에 fail.

**Step 2 — GREEN:** feature formula는 바꾸지 않고 state 생성만 추출한다. V1 `build_forward_coordinate_frame()`/forward regime caller를 same-state target으로 이동한다.

**Step 3 — Fixed-cutoff regression:** supplied incident의 2026-07-17/2026-07-20 cutoff fixture를 추가하고 later rows append 후 2026-07-17 state가 동일한지 확인한다.

**Step 4 — Regression and commit:**

```bash
.venv/bin/python -m unittest tests.test_futures_macro_pattern tests.test_futures_macro_pattern_validation -v
git add app/services/futures_macro_pattern.py app/services/futures_macro_pattern_validation.py tests/test_futures_macro_pattern.py tests/test_futures_macro_pattern_validation.py
git commit -m "관측과 전망의 선물 매크로 상태 정의 통일"
```

---

## 2차 — Momentum Baseline / Macro Hybrid Validation

### Task 3: PIT macro and official event context frames

**Files:**

- Create: `finance/loaders/market_events.py`
- Create: `app/services/futures_macro_context.py`
- Modify: `finance/loaders/economic_cycle.py:366-410`
- Test: `tests/test_futures_macro_context.py`
- Test: `tests/test_economic_cycle_results.py`

**DB-only loader contracts:**

```python
def load_cycle_history(
    *, start_date: str | date, end_date: str | date,
    known_at_date: str | date | None = None,
    query_fn: QueryFn | None = None,
) -> list[dict[str, object]]: ...

def load_official_macro_event_history(
    *, start_date: str | date, end_date: str | date,
    known_at: datetime,
    query_fn: QueryFn | None = None,
) -> list[dict[str, object]]: ...
```

`load_cycle_history()`는 `historical_replay`만 읽고 `data_cutoff_date <= as_of_date <= known_at_date`를 Python에서 다시 검증한다. Event loader는 official source/authority, non-superseded, `collected_at <= known_at`을 모두 요구한다. `collected_at`이 없으면 과거에 알려졌다고 간주하지 않는다.

**Context frame contract:**

```python
MACRO_CONTEXT_COLUMNS = (
    "cycle_risk_balance", "cycle_entropy",
    "activity_contribution", "labor_income_contribution",
    "financial_leading_contribution", "inflation_policy_contribution",
)
EVENT_CONTEXT_COLUMNS = (
    "event_count_5d", "event_count_20d",
    "has_fomc_5d", "has_inflation_5d",
    "has_labor_5d", "has_growth_20d",
)

def build_futures_macro_context_frame(
    session_dates: pd.DatetimeIndex,
    *, cycle_rows: Sequence[dict[str, object]],
    event_rows: Sequence[dict[str, object]],
) -> pd.DataFrame: ...
```

- `cycle_risk_balance = P(recovery)+P(expansion)-P(slowdown)-P(recession)`.
- `cycle_entropy`는 four-class normalized entropy `[0,1]`이다.
- contribution은 `factor_contributions_json`을 파싱해 four exact factor prefix별로 합산한다.
- 각 session은 `data_cutoff_date <= session_date`인 최신 cycle replay를 backward as-of join한다. 첫 snapshot 이전은 fill하지 않는다.
- event 5D/20D window는 canonical session index를 사용하고, current terminal 밖에서만 7/28 calendar-day bound를 사용한다.
- inflation=CPI/PPI/PCE, labor=Employment/JOLTS/ECI, growth=GDP/Retail Sales/Durable Goods/Housing로 고정한다.

**Step 1 — RED:** later-vintage exclusion, missing-known-at exclusion, backward join, later-collected event exclusion, empty-context behavior test를 추가한다.

```bash
.venv/bin/python -m unittest tests.test_futures_macro_context tests.test_economic_cycle_results -v
```

Expected: imports/functions missing.

**Step 2 — GREEN:** DB-only loaders와 pure context builder를 구현한다. Parsing error는 missing context/reason으로 남기고 zero로 대체하지 않는다.

**Step 3 — Regression and commit:**

```bash
.venv/bin/python -m unittest tests.test_futures_macro_context tests.test_economic_cycle_results -v
git add finance/loaders/market_events.py app/services/futures_macro_context.py finance/loaders/economic_cycle.py tests/test_futures_macro_context.py tests/test_economic_cycle_results.py
git commit -m "선물 매크로 PIT 컨텍스트 계약 추가"
```

### Task 4: Reduced momentum predictors and weighted analog candidates

**Files:**

- Create: `app/services/futures_macro_outlook_model.py`
- Test: `tests/test_futures_macro_outlook_model.py`

**Candidate contract:**

```python
@dataclass(frozen=True)
class OutlookCandidate:
    key: str
    lambda_macro: float
    lambda_event: float

CANDIDATES = (
    OutlookCandidate("M1_MOMENTUM", 0.0, 0.0),
    OutlookCandidate("M2A_LIGHT", 0.25, 0.25),
    OutlookCandidate("M2B_BALANCED", 0.50, 0.50),
    OutlookCandidate("M2C_MACRO_SENSITIVE", 1.00, 0.50),
)
TEMPERATURE_GRID = (0.5, 1.0, 2.0)
```

16 momentum predictors를 outer result를 보기 전에 고정한다.

```text
state_x, state_y,
impulse_x, impulse_y,
slope_x, slope_y,
long_x, long_y,
persistence_x, persistence_y,
breadth_x, breadth_y,
volatility_x, volatility_y,
conflict_flag, coverage_ratio
```

Train-only median/IQR로 momentum/macro/event distance block을 각각 scale한다. Missing macro/event인 origin에서 M2는 unavailable이지만 M1은 유지한다.

```python
combined = momentum + candidate.lambda_macro * macro + candidate.lambda_event * event
weight = math.exp(-combined / temperature)
```

Episode는 `origin_position <= forecast_position - horizon - 1`, minimum spacing=`horizon`, maximum=120, minimum=30을 적용한다.

**Step 1 — RED:** exact predictor projection, future-row immunity, overlap purge, spacing, monotonic distance, weight, M2-unavailable/M1-valid test를 작성한다.

```bash
.venv/bin/python -m unittest tests.test_futures_macro_outlook_model -v
```

Expected: module missing.

**Step 2 — GREEN:** pure frame/ranking function만 구현하고 DB/publication status는 넣지 않는다.

**Step 3 — Regression and commit:**

```bash
.venv/bin/python -m unittest tests.test_futures_macro_outlook_model -v
git add app/services/futures_macro_outlook_model.py tests/test_futures_macro_outlook_model.py
git commit -m "선물 매크로 가중 유사 구간 모델 추가"
```

### Task 5: Nested rolling-origin selection and honest publication gates

**Files:**

- Modify: `app/services/futures_macro_pattern_validation.py:345-1040`
- Modify: `app/services/futures_macro_outlook_model.py`
- Test: `tests/test_futures_macro_pattern_validation.py`
- Test: `tests/test_futures_macro_outlook_model.py`

**Baselines:**

- `B0_UNCONDITIONAL`: train-only terminal regime frequency + absolute terminal-state distribution.
- `B1_PERSISTENCE`: current regime probability 1.0 + current coordinate terminal center.
- M1/M2: weighted analog outcomes.

**Nested evaluation:**

- outer minimum train 756 sessions, test 63, purge horizon;
- inner minimum train 504 sessions, test 63, purge horizon;
- candidate+temperature는 inner mean multiclass Brier로 선택한다.
- tie시 complexity `B0, B1, M1, M2a, M2b, M2c`, 그 다음 lower temperature 순이다.
- outer fold는 inner에서 선택된 설정만 평가한다.
- test outcome은 `horizon` rows 간격으로 sampling한다.
- paired moving-block bootstrap: block=`horizon`, samples=2,000, seed=`20260720`.

**Probability gate:**

```text
UNAVAILABLE: current independent analog <30 or no outer prediction
PROVISIONAL: calculable but <60 evaluations or any verification gate misses
NO_EDGE: >=60 evaluations and selected candidate fails to beat best B0/B1 Brier
VERIFIED: >=60 evaluations; Brier/log loss beat both B0/B1;
          calibration <=0.10; fold improvement >=0.60;
          paired-bootstrap 90% Brier-improvement lower bound >0
```

**Coordinate gate:**

```text
UNAVAILABLE: terminal samples <30
PROVISIONAL: calculable but verification gate misses without conclusive no-edge
NO_EDGE: >=60 evaluations and median error fails best zero/persistence/unconditional baseline
VERIFIED: >=60 evaluations; median error beats all coordinate baselines;
          joint coverage 50%=0.40..0.60 and 80%=0.70..0.90;
          80% region sharper than unconditional; >=3 folds;
          paired-bootstrap 90% error-improvement lower bound >0
```

Vector는 coordinate `VERIFIED`, weighted 80% displacement interval의 최소 한 축이 zero를 배제, median displacement norm `>=0.35`를 모두 만족할 때만 `VERIFIED`다.

Terminal region은 weighted bivariate covariance ellipse로 50%/80% joint region을 만든다. Payload fields는 `mass`, `center_x`, `center_y`, `radius_major`, `radius_minor`, `rotation_deg`이다. Publication은 rolling-origin empirical joint coverage로 검증하며 old independent x/y rectangle는 제거한다.

**Step 1 — RED:** synthetic M1 win, macro-only M2 win, all lose=`NO_EDGE`, probability-only pass, coordinate pass/vector zero-including test를 작성한다.

```bash
.venv/bin/python -m unittest tests.test_futures_macro_outlook_model tests.test_futures_macro_pattern_validation -v
```

Expected: status/candidate/region assertions fail against V1.

**Step 2 — GREEN:** V1 forward-return coordinate/path와 single `estimate_status`를 V2 target/candidate/separate gate로 대체한다. Raw compact metrics는 `method`에 남긴다.

```python
PATTERN_ALGORITHM_VERSION = "pattern_outlook_v5_same_state_nested_hybrid"
PATTERN_OUTLOOK_SCHEMA_VERSION = "futures_macro_pattern_outlook_v2"
```

**Step 3 — Regression and commit:**

```bash
.venv/bin/python -m unittest tests.test_futures_macro_pattern tests.test_futures_macro_sessions tests.test_futures_macro_context tests.test_futures_macro_outlook_model tests.test_futures_macro_pattern_validation -v
git add app/services/futures_macro_pattern_validation.py app/services/futures_macro_outlook_model.py tests/test_futures_macro_pattern_validation.py tests/test_futures_macro_outlook_model.py
git commit -m "5D 20D 선물 매크로 전망 시간순 검증 개편"
```

---

## 3차 — Persistence / UI / Actual QA

### Task 6: Immutable forecast history and final-session materialization

**Files:**

- Modify: `finance/data/db/schema.py:653-674`
- Modify: `finance/data/futures_macro_snapshot.py`
- Modify: `finance/loaders/futures_macro_snapshot.py`
- Modify: `app/services/futures_macro_snapshot.py`
- Modify: `app/jobs/ingestion_jobs.py:1187-1235`
- Test: `tests/test_futures_macro_snapshot.py`
- Test: `tests/test_service_contracts.py`

**Schema:** Current table에 `input_fingerprint CHAR(64)`, `session_status VARCHAR(32)`를 추가한다. History table은 다음으로 고정한다.

```sql
CREATE TABLE IF NOT EXISTS futures_macro_forecast_history (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  forecast_identity CHAR(64) NOT NULL,
  as_of_date DATE NOT NULL,
  source_marker VARCHAR(64) NOT NULL,
  input_fingerprint CHAR(64) NOT NULL,
  schema_version VARCHAR(64) NOT NULL,
  feature_schema_version VARCHAR(64) NOT NULL,
  algorithm_version VARCHAR(128) NOT NULL,
  selected_models_json LONGTEXT NOT NULL,
  status_json LONGTEXT NOT NULL,
  forecast_json LONGTEXT NOT NULL,
  known_at TIMESTAMP NOT NULL,
  materialized_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_futures_macro_forecast_identity (forecast_identity),
  KEY ix_futures_macro_forecast_as_of (as_of_date, algorithm_version)
);
```

`input_fingerprint`는 final per-symbol OHLCV through as-of, cycle replay identities, eligible event keys, resolver version, feature schema version의 canonical JSON SHA-256이다. `materialized_at`은 포함하지 않는다. `forecast_identity = sha256(as_of|input_fingerprint|schema_version|algorithm_version)`다.

```python
def persist_futures_macro_snapshot_bundle(
    current_row: dict[str, object],
    history_row: dict[str, object],
    *, connection: Any = None,
) -> dict[str, int]: ...
```

하나의 explicit transaction에서 history를 idempotent insert한 뒤 incoming final as-of가 기존보다 같거나 새로울 때만 current를 UPSERT한다. 오류시 둘 다 rollback하므로 latest-good current가 남고 ingestion은 partial success다.

**Step 1 — RED:** schema keys, deterministic fingerprint, idempotent history, older-current rejection, pending-session reuse, rollback test를 작성한다.

```bash
.venv/bin/python -m unittest tests.test_futures_macro_snapshot -v
```

Expected: new schema/function assertions fail.

**Step 2 — GREEN:** compact snapshot을 `futures_macro_snapshot_v2`로 올리고 completed rows/context로 한 번만 계산한 뒤 bundle을 저장한다. `_compatible_row()`는 raw max date 대신 schema/algorithm/input fingerprint를 비교한다.

**Step 3 — Regression and commit:**

```bash
.venv/bin/python -m unittest tests.test_futures_macro_snapshot -v
.venv/bin/python -m pytest tests/test_service_contracts.py -k futures_macro -q
git add finance/data/db/schema.py finance/data/futures_macro_snapshot.py finance/loaders/futures_macro_snapshot.py app/services/futures_macro_snapshot.py app/jobs/ingestion_jobs.py tests/test_futures_macro_snapshot.py tests/test_service_contracts.py
git commit -m "선물 매크로 전망 이력과 최신 스냅샷 원자적 저장"
```

### Task 7: V3 UI payload with separate publication surfaces

**Files:**

- Modify: `app/web/overview/futures_macro_helpers.py:730-1095`
- Modify: `tests/test_service_contracts.py:27034-27220`

Payload version은 `futures_macro_react_workbench_v3`이다.

```python
{
    "selected_candidate": "M1_MOMENTUM" | "M2A_LIGHT" | "M2B_BALANCED" | "M2C_MACRO_SENSITIVE" | None,
    "probability_status": "VERIFIED" | "PROVISIONAL" | "NO_EDGE" | "UNAVAILABLE",
    "coordinate_status": "VERIFIED" | "PROVISIONAL" | "NO_EDGE" | "UNAVAILABLE",
    "vector_status": "VERIFIED" | "PROVISIONAL" | "NO_EDGE" | "UNAVAILABLE",
    "probabilities": [...],
    "disclosure_probabilities": [...],
    "terminal_regions": [...],
    "direction_vector": {...} | None,
    "macro_adjustment": {"used": bool, "candidate": str | None, "reason": str},
}
```

Python bridge에서 publication suppression을 강제한다.

- primary `probabilities`는 probability `VERIFIED`에서만 존재한다.
- provisional numeric은 `disclosure_probabilities`로만 보낸다.
- `NO_EDGE`는 primary/disclosure conditional numeric을 모두 비운다.
- `terminal_regions`는 coordinate `VERIFIED`에서만 존재한다.
- `direction_vector`는 vector `VERIFIED`에서만 존재한다.
- observed path와 fixed domain `{x:[-2.5,2.5], y:[-2.5,2.5]}`를 전달한다.
- `session_evidence`는 final as-of/pending session만 사용자 근거로 전달하며 run diagnostics panel을 만들지 않는다.

**Step 1 — RED:** verified/provisional/no-edge fixture와 forbidden-field suppression test를 추가한다.

```bash
.venv/bin/python -m pytest tests/test_service_contracts.py -k futures_macro -q
```

Expected: V2 payload/status assumptions fail.

**Step 2 — GREEN:** helper에서 model 계산을 하지 않고 V3 bridge만 구현한다.

**Step 3 — Regression and commit:**

```bash
.venv/bin/python -m pytest tests/test_service_contracts.py -k futures_macro -q
git add app/web/overview/futures_macro_helpers.py tests/test_service_contracts.py
git commit -m "선물 매크로 확률 전망 UI 계약 분리"
```

### Task 8: React observed trail and gated terminal regions

**Files:**

- Modify: `app/web/streamlit_components/futures_macro_workbench/src/FuturesMacroWorkbench.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/PatternHorizonSection.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/PatternMapSection.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/MethodDisclosure.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/style.css`
- Generated, not committed: `app/web/streamlit_components/futures_macro_workbench/component_static/*`
- Test: `tests/test_service_contracts.py`

**Rendering contract:**

- dynamic `xBound/yBound`를 제거하고 `DOMAIN_MIN=-2.5`, `DOMAIN_MAX=2.5`를 세 selector에 공통 적용한다.
- observed 30 points를 하나의 trail로 렌더링하고 age에 따라 opacity를 높인다. 20/5/current marker는 보조 anchor이며 exact date를 포함한다.
- screen coordinate만 clip하고 raw coordinate는 `<title>`에 보존한다. Outlier는 boundary triangle `is-clipped`으로 표시한다.
- coordinate `VERIFIED`이면 80% ellipse를 먼저, 50% ellipse를 나중에 SVG transform으로 렌더링한다.
- `direction_vector`가 실제 payload에 있을 때만 vector를 렌더링한다.
- `PROVISIONAL` first surface는 `검증 중 · 확정 우위 없음`, numeric은 Method disclosure에만 보인다.
- `NO_EDGE`는 `baseline 대비 예측 우위 없음`과 함께 probability row/forecast geometry를 모두 숨긴다.
- 5D/20D card에 selected candidate와 macro conditioning 사용 여부를 명시한다.

**Step 1 — RED:** fixed domain, full trail, exact dates, ellipse, separate statuses, old conditional-line absence source-contract test를 작성한다.

```bash
.venv/bin/python -m pytest tests/test_service_contracts.py -k 'futures_macro and (pattern_map or react)' -q
```

Expected: fail against current component.

**Step 2 — GREEN:** TypeScript types/components를 V3에 맞추고 calculation/selection은 server-owned로 두어라.

**Step 3 — Type/build verification:** component directory에서 실행한다.

```bash
npm run build
```

Expected: TypeScript/Vite exit 0. `component_static`은 기존 deployment 계약상 tracked bundle update가 필요한지 `git status`로 확인한 뒤 필요한 경우에만 stage한다.

**Step 4 — Regression and commit:**

```bash
.venv/bin/python -m pytest tests/test_service_contracts.py -k futures_macro -q
git add app/web/streamlit_components/futures_macro_workbench/src tests/test_service_contracts.py
git commit -m "선물 매크로 실제 경로와 검증 전망 화면 개편"
```

### Task 9: Integration, fixed-cutoff replay, Browser QA, and docs sync

**Files:**

- Create: `tests/test_futures_macro_v2_integration.py`
- Modify: this task's `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Modify as warranted: `.aiworkspace/note/finance/docs/architecture/OVERVIEW_ARCHITECTURE.md`
- Modify as warranted: `.aiworkspace/note/finance/docs/flows/OVERVIEW.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Generated, not committed: one Browser QA PNG

**Step 1 — Integration test:** fixed-cutoff fixture를 `raw -> resolver -> candles -> state -> target/model -> compact payload`에 통과시켜 다음을 검증한다.

- 2026-07-20 replay에서 2026-07-17 state는 불변이다.
- Sunday→Monday row는 cutoff 전에 publish하지 않는다.
- observed 30 rows는 actual dates를 유지한다.
- non-verified coordinate는 forbidden UI geometry를 만들지 않는다.
- same fingerprint/model run은 same forecast identity다.

```bash
.venv/bin/python -m unittest tests.test_futures_macro_v2_integration -v
```

**Step 2 — Focused full verification:**

```bash
.venv/bin/python -m unittest tests.test_futures_macro_sessions tests.test_futures_macro_pattern tests.test_futures_macro_context tests.test_futures_macro_outlook_model tests.test_futures_macro_pattern_validation tests.test_futures_macro_snapshot tests.test_futures_macro_v2_integration -v
.venv/bin/python -m pytest tests/test_service_contracts.py -k futures_macro -q
git diff --check
```

Expected: all pass, no whitespace errors.

**Step 3 — Actual materialization:** configured local DB에서 existing daily futures refresh/materializer를 실행하고 final/pending session, horizon candidate, three statuses, B0/B1/M1/M2 metrics, history/current identity를 `RUNS.md`에 남긴다. Output이 `NO_EDGE`면 gate를 낮추지 말고 suppression을 검증한다. Historical replay/event known-at coverage가 부족하면 M2=`UNAVAILABLE`로 남기고 M1/B0/B1을 검증한다.

**Step 4 — Browser QA:** 저장소 local Streamlit runbook을 사용해 desktop/420px에서 다음을 확인한다.

- trail이 three-point triangle이 아닌 dated daily movement이다.
- observed/5D/20D selector가 axis를 바꾸지 않는다.
- `NO_EDGE`/`PROVISIONAL`에 terminal geometry가 없다.
- `VERIFIED` geometry가 자연적으로 발생한 경우 server payload와 일치한다.
- final/pending evidence가 diagnostics panel이 아니면서 이해 가능하다.

스크린샷 1장은 generated artifact로 두고 사용자 요청 없이 commit하지 않는다.

**Step 5 — Documentation sync:** `finance-doc-sync`을 사용한다. 안정된 session/state/publication contract만 architecture/flow docs로 승격하고 measured candidate result/troubleshooting은 active task에 남긴다.

**Step 6 — Final verification and commit:**

```bash
git status --short
git diff --check
git diff --stat
```

Unrelated untracked research/PNG가 변경되지 않았는지 확인한 뒤 Task 9 files만 stage하고 commit한다.

```bash
git commit -m "선물 매크로 확률 전망 V2 검증과 문서 정렬"
```

## Final Acceptance Matrix

| Requirement | Evidence |
|---|---|
| completed session only | resolver tests + pending-session QA |
| same state definition | direct state/target equality tests |
| no historical rewrite | append-future + 7/17→7/20 replay |
| momentum is baseline | B0/B1/M1/M2 shared-fold metrics |
| macro is not forced | no-context tests + actual selected candidate |
| no edge is publishable | `NO_EDGE` payload/UI suppression tests |
| coordinate independently gated | probability-only synthetic test |
| fixed comparable chart | React contract + desktop/mobile QA |
| reproducible forecast | fingerprint/history idempotency tests |
| DB-only UI | service contract forbids UI calculate/fetch |

## Plan Self-Review

- Spec coverage: approved DESIGN의 모든 section이 Tasks 1–9와 acceptance matrix에 mapping된다.
- Placeholder scan: `TBD`, `TODO`, 가상 file, 미확정 게이트가 없다.
- Type consistency: service/React의 forecast status는 `VERIFIED`, `PROVISIONAL`, `NO_EDGE`, `UNAVAILABLE`; observation session status는 별도다.
- Safety: schema/data deletion, registry rewrite, UI provider fetch, outer-test 결과 기반 gate tuning은 허용하지 않는다.
- Scope: Economic Cycle publication, consensus surprise, trading signal, Futures Monitor intraday UI는 변경하지 않는다.
