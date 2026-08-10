# Overview Futures Macro Intraday Nowcast V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 거래 중에는 저장된 latest closed 5m bar로 1D / 5D / 20D 현재 관측을 잠정 재계산하고, 완료 일봉 기반 미래 5D 검증과 immutable history는 그대로 보존한다.

**Architecture:** 수동 refresh가 daily overlap 뒤 pending session을 probe하고 bounded `2d/5m`을 한 번만 수집한다. 신규 Streamlit-free service가 DB의 completed daily rows와 stored 5m rows로 provisional observation을 만들며, persisted completed snapshot은 forecast evidence로 그대로 둔다. Python payload가 장중/확정/검증 의미를 결정하고 React는 이를 표시한다.

**Tech Stack:** Python 3.12, pandas, PyMySQL, pytest, Streamlit, React 18, TypeScript 5, Vite 6.

## Global Constraints

- UI에서 provider를 직접 호출하지 않고 `Ingestion -> DB -> Service -> UI` 경계를 유지한다.
- 장중 synthetic row와 provisional pattern을 `futures_macro_snapshot`, `futures_macro_forecast_history`, registry 또는 saved JSONL에 저장하지 않는다.
- 미래 5D publication status와 historical validation은 마지막 완료 일봉만 사용한다.
- family score는 `SCORE_DEFINITIONS` member가 모두 현재 aggregate를 가질 때만 계산한다.
- 적격 full-member family가 6개면 `INTRADAY_READY`, 4~5개면 `INTRADAY_PARTIAL`, 4개 미만이면 completed fallback이다.
- common cutoff freshness가 30분을 초과하면 completed fallback이다.
- family weight, signal threshold, completed finalization 17/17 atomic gate와 DB schema는 바꾸지 않는다.
- 기본 제품 화면에 run/job/row 진단 패널을 추가하지 않는다.
- generated screenshot, run history, registry/saved JSONL과 unrelated dirty-tree 변경은 stage하지 않는다.

---

## File Structure

| File | Responsibility |
|---|---|
| `app/services/futures_macro_intraday.py` | stored 5m eligibility, complete-family common cutoff, synthetic current daily row, provisional pattern과 DB-only loader |
| `app/jobs/futures_macro_daily_finalization.py` | latest pending-session probe와 pre-collected 5m result reuse |
| `app/jobs/overview_actions.py` | one-time bounded 2d/5m collection orchestration |
| `app/web/overview/futures_macro_helpers.py` | completed snapshot + provisional observation payload, semantic copy와 action label |
| `app/web/streamlit_components/futures_macro_workbench/src/MacroContextSection.tsx` | 장중 잠정/확정/fallback header facts |
| `app/web/streamlit_components/futures_macro_workbench/src/ShortHorizonDecisionSection.tsx` | 1D/5D/20D current observation cards |
| `app/web/streamlit_components/futures_macro_workbench/src/ForecastValidationGate.tsx` | completed-as-of 미래 5D 검증 gate |
| `app/web/streamlit_components/futures_macro_workbench/src/FamilyDirectionSection.tsx` | family별 의미가 드러나는 상태 matrix |
| `app/web/streamlit_components/futures_macro_workbench/src/style.css` | desktop/mobile current-vs-forecast hierarchy |
| `tests/test_futures_macro_intraday.py` | intraday service correctness and fail-closed boundaries |
| `tests/test_overview_futures_macro_refresh.py` | one-time collection/finalization orchestration |
| `tests/test_overview_futures_macro_short_horizon.py` | payload/React source contract |

---

### Task 1: Stored 5m Intraday Observation Service

**Files:**
- Create: `app/services/futures_macro_intraday.py`
- Create: `tests/test_futures_macro_intraday.py`

**Interfaces:**
- Consumes: `SCORE_DEFINITIONS`, `PATTERN_FEATURE_SUFFIXES`, `build_pattern_feature_frame()`, `build_current_pattern_snapshot()`, `normalize_futures_macro_daily_candles()`, `select_completed_futures_daily_rows()`, `futures_session_window_utc()`.
- Produces: `build_futures_macro_intraday_observation(*, daily_rows, intraday_rows, evaluation_time, completed_pattern, selected_symbols, freshness_limit_minutes) -> dict[str, Any]` and `load_overview_futures_macro_intraday_observation(*, completed_pattern, evaluation_time, daily_rows_loader, intraday_rows_loader, query_fn) -> dict[str, Any]`.

- [ ] **Step 1: Write failing aggregate eligibility tests**

Create fixtures with 5m bar timestamps interpreted as interval starts and assert only closed bars are used, complete families remain eligible, missing-member families are unavailable, and common cutoff is the earliest latest bar across eligible family members.

```python
def test_intraday_observation_uses_common_closed_bar_cutoff() -> None:
    evaluation = datetime(2026, 8, 10, 15, 17, tzinfo=timezone.utc)
    rows = _intraday_rows(
        evaluation=evaluation,
        lag_by_symbol={"ES=F": 10, "NQ=F": 5},
    )

    result = build_futures_macro_intraday_observation(
        daily_rows=_completed_daily_rows(),
        intraday_rows=rows,
        evaluation_time=evaluation,
        completed_pattern=_completed_pattern(),
    )

    assert result["observation_mode"] == "INTRADAY_PROVISIONAL"
    assert result["status"] == "INTRADAY_READY"
    assert result["observed_at_utc"] == "2026-08-10T15:10:00+00:00"
    assert result["freshness_minutes"] == 7.0
    assert result["pattern"]["as_of_date"] == "2026-08-10"
```

```python
def test_missing_member_suppresses_only_affected_families() -> None:
    rows = [row for row in _intraday_rows() if row["provider_symbol"] != "GC=F"]
    result = build_futures_macro_intraday_observation(
        daily_rows=_completed_daily_rows(),
        intraday_rows=rows,
        evaluation_time=EVALUATION,
        completed_pattern=_completed_pattern(),
    )

    assert result["status"] == "INTRADAY_PARTIAL"
    assert result["pattern"]["families"]["safe_haven"]["status"] == "UNAVAILABLE"
    assert result["pattern"]["families"]["risk_on"]["status"] == "READY"
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_futures_macro_intraday.py -q
```

Expected: collection fails because `app.services.futures_macro_intraday` does not exist.

- [ ] **Step 3: Implement closed-bar, family coverage and common-cutoff primitives**

Create these public constants and functions:

```python
INTRADAY_BAR_MINUTES = 5
INTRADAY_FRESHNESS_LIMIT_MINUTES = 30
INTRADAY_MIN_FAMILIES = 4

def build_futures_macro_intraday_observation(
    *,
    daily_rows: Sequence[dict[str, Any]],
    intraday_rows: Sequence[dict[str, Any]],
    evaluation_time: datetime,
    completed_pattern: Mapping[str, Any] | None = None,
    selected_symbols: Sequence[str] = DEFAULT_CORE_FUTURES_SYMBOLS,
    freshness_limit_minutes: int = INTRADAY_FRESHNESS_LIMIT_MINUTES,
) -> dict[str, Any]:
    """Build a non-persistent current observation from completed daily and stored 5m rows."""
```

Implementation rules:

```python
closed_before = evaluation_utc
eligible = [
    row for row in session_rows
    if timestamp(row["candle_time_utc"]) + timedelta(minutes=5) <= closed_before
]
complete_families = {
    family: definition
    for family, definition in FAMILY_DEFINITIONS.items()
    if set(definition.members).issubset(latest_by_symbol)
}
common_bar_start = min(
    latest_by_symbol[symbol]
    for definition in complete_families.values()
    for symbol in definition.members
)
observed_at = common_bar_start + timedelta(minutes=5)
```

Aggregate every eligible family member only through `common_bar_start`. Build synthetic daily rows with `candle_time_utc=session_date 00:00:00`, session OHLCV and `collected_at=evaluation_time`. Normalize completed rows plus synthetic rows, calculate the pattern feature frame, and set every latest-row `PATTERN_FEATURE_SUFFIXES` column to `pd.NA` for incomplete families before calling `build_current_pattern_snapshot()`.

Return the exact provenance contract:

```python
{
    "status": "INTRADAY_READY" | "INTRADAY_PARTIAL" | "COMPLETED_FALLBACK",
    "observation_mode": "INTRADAY_PROVISIONAL" | "COMPLETED",
    "pattern": provisional_or_completed_pattern,
    "session_date": pending_session_or_none,
    "completed_as_of_date": latest_final_session,
    "observed_at_utc": iso_or_none,
    "observed_at_et": iso_or_none,
    "freshness_minutes": float_or_none,
    "available_family_count": int,
    "required_family_count": 6,
    "fallback_reason": str_or_none,
}
```

- [ ] **Step 4: Add stale, insufficient-family, non-trading and Sunday tests**

```python
def test_stale_common_cutoff_falls_back_to_completed_pattern() -> None:
    result = build_futures_macro_intraday_observation(
        daily_rows=_completed_daily_rows(),
        intraday_rows=_intraday_rows(common_age_minutes=31),
        evaluation_time=EVALUATION,
        completed_pattern=_completed_pattern(),
    )
    assert result["observation_mode"] == "COMPLETED"
    assert result["fallback_reason"] == "intraday_data_stale"
    assert result["pattern"] == _completed_pattern()


def test_three_complete_families_fall_back_without_partial_headline() -> None:
    rows = _intraday_rows(
        available_symbols=_symbols_for_families(
            "risk_on", "rate_pressure", "dollar_pressure"
        )
    )
    result = build_futures_macro_intraday_observation(
        daily_rows=_completed_daily_rows(),
        intraday_rows=rows,
        evaluation_time=EVALUATION,
        completed_pattern=_completed_pattern(),
    )
    assert result["status"] == "COMPLETED_FALLBACK"
    assert result["fallback_reason"] == "insufficient_intraday_family_coverage"
```

Add a Sunday 18:00 ET fixture whose provider daily label resolves to Monday and assert `session_date` is Monday. Add a no-pending fixture and assert no intraday loader call.

- [ ] **Step 5: Implement the DB-only loader**

```python
def load_overview_futures_macro_intraday_observation(
    *,
    completed_pattern: Mapping[str, Any] | None,
    evaluation_time: datetime | None = None,
    daily_rows_loader: Callable[..., list[dict[str, Any]]] = load_futures_macro_daily_rows,
    intraday_rows_loader: Callable[..., list[dict[str, Any]]] = load_stored_futures_intraday_rows,
    query_fn: QueryFn = _default_query,
) -> dict[str, Any]:
    """Load DB rows only and delegate provisional calculation to the pure builder."""
```

Load 420 days of daily rows, resolve completed/pending state, and query only the pending session exact window for 5m rows. Do not make a provider request or write any row.

- [ ] **Step 6: Run Task 1 tests and commit**

```bash
.venv/bin/python -m pytest tests/test_futures_macro_intraday.py tests/test_futures_macro_sessions.py -q
git add app/services/futures_macro_intraday.py tests/test_futures_macro_intraday.py
git commit -m "기능: 선물 매크로 장중 잠정 관측 계산"
```

Expected: focused tests pass; only existing dependency warnings may remain.

---

### Task 2: One-Time Intraday Refresh And Finalization Reuse

**Files:**
- Modify: `app/jobs/futures_macro_daily_finalization.py`
- Modify: `app/jobs/overview_actions.py`
- Modify: `tests/test_overview_futures_macro_refresh.py`

**Interfaces:**
- Consumes: Task 1 DB storage contract; existing `run_collect_futures_ohlcv()` and finalization primitives.
- Produces: `probe_pending_futures_daily_session(*, symbols, evaluation_time, daily_rows_loader) -> dict[str, Any]`; optional `intraday_collection_result` input on `run_pending_futures_daily_finalization()`; `details.intraday_refresh` in the overview job result.

- [ ] **Step 1: Write failing orchestration tests**

```python
def test_active_session_collects_five_minute_rows_once_before_materialization() -> None:
    calls: list[tuple[str, str]] = []
    result = run_overview_futures_daily_ohlcv(
        coverage_loader=lambda symbols: _coverage(),
        collect_runner=lambda **kw: calls.append((kw["period"], kw["interval"]))
        or _collection_result(list(kw["symbols"])),
        session_probe=lambda **kw: {
            "status": "pending", "session_date": "2026-08-10"
        },
        finalization_runner=lambda **kw: {
            "status": "not_due", "session_date": "2026-08-10",
            "symbols_required": 17, "symbols_finalized": 0,
            "missing_symbols": [], "reason": "settlement_cutoff_not_reached",
        },
        materialize_fn=lambda: {"status": "reused_pending"},
    )
    assert calls == [("1y", "1d"), ("2d", "5m")]
    assert result["details"]["intraday_refresh"]["status"] == "success"
```

Add a post-cutoff test asserting the same collection result object reaches finalization and the
finalization runner does not call its own collector. Add a no-pending test asserting no 5m call.

- [ ] **Step 2: Run orchestration tests and verify RED**

```bash
.venv/bin/python -m pytest tests/test_overview_futures_macro_refresh.py -q
```

Expected: failure because `session_probe` and `intraday_collection_result` contracts do not exist.

- [ ] **Step 3: Extract a reusable pending-session probe**

```python
def probe_pending_futures_daily_session(
    *,
    symbols: Sequence[str],
    evaluation_time: datetime,
    daily_rows_loader: Callable[[Sequence[str]], list[dict[str, Any]]] = load_latest_futures_daily_rows,
) -> dict[str, Any]:
    """Return one normalized latest-session state for refresh orchestration."""
```

Return `pending`, `completed`, `incomplete` or `error` with session date and missing symbols. Make
`run_pending_futures_daily_finalization()` use the same resolver helper so probe and finalization cannot
disagree about Sunday labels, explicit finalization or coverage.

- [ ] **Step 4: Accept pre-collected 5m results in finalization**

Extend the signature:

```python
def run_pending_futures_daily_finalization(
    *,
    symbols: Sequence[str],
    evaluation_time: datetime,
    collect_runner: Callable[..., dict[str, Any]],
    intraday_collection_result: dict[str, Any] | None = None,
    daily_rows_loader: Callable[[Sequence[str]], list[dict[str, Any]]] = load_latest_futures_daily_rows,
    intraday_rows_loader: Callable[..., list[dict[str, Any]]] = load_stored_futures_intraday_rows,
    writer: Callable[..., int] = write_futures_daily_finalization,
) -> FinalizationResult:
```

When `intraday_collection_result` is present, validate status/rows/failures exactly as the current
locally collected result and skip `collect_runner`. Preserve all existing early returns and 17/17
atomic write behavior.

- [ ] **Step 5: Orchestrate one bounded collection in Overview**

Add `session_probe` injection to `run_overview_futures_daily_ohlcv()`. After daily groups:

```python
probe = session_probe(symbols=selected, evaluation_time=evaluated_at)
intraday_result = None
if probe["status"] == "pending":
    intraday_result = collect_runner(
        symbols=selected,
        period="2d",
        interval="5m",
        cadence_mode="manual_macro_intraday_nowcast",
        max_symbols=len(selected),
        batch_size=len(selected),
        sleep_sec=0.0,
        materialize_snapshot=False,
    )
finalization = finalize(
    symbols=selected,
    evaluation_time=evaluated_at,
    collect_runner=collect_runner,
    intraday_collection_result=intraday_result,
)
```

Attach a compact `details.intraday_refresh` backend result. Do not render it as a new UI panel.

- [ ] **Step 6: Run Task 2 tests and commit**

```bash
.venv/bin/python -m pytest tests/test_overview_futures_macro_refresh.py tests/test_futures_macro_sessions.py -q
git add app/jobs/futures_macro_daily_finalization.py app/jobs/overview_actions.py tests/test_overview_futures_macro_refresh.py
git commit -m "기능: 선물 장중 갱신과 일봉 확정 수집 통합"
```

---

### Task 3: Python Product Payload And User Meaning

**Files:**
- Modify: `app/web/overview/futures_macro_helpers.py`
- Modify: `tests/test_overview_futures_macro_short_horizon.py`

**Interfaces:**
- Consumes: Task 1 `load_overview_futures_macro_intraday_observation()` and the existing completed materialized snapshot.
- Produces: `futures_macro_react_workbench_v5`, `observation` provenance, 1D/5D/20D current cards, and a separate completed-as-of future gate.

- [ ] **Step 1: Write failing payload tests**

```python
def test_intraday_payload_uses_provisional_pattern_but_completed_forecast() -> None:
    payload = build_futures_macro_react_workbench_payload(
        _macro(),
        pattern_outlook=_outlook("NO_EDGE"),
        current_observation=_intraday_observation(),
    )
    assert payload["schema_version"] == "futures_macro_react_workbench_v5"
    assert payload["hero"]["observation_mode"] == "INTRADAY_PROVISIONAL"
    assert payload["hero"]["as_of_date"] == "2026-08-10"
    assert payload["hero"]["completed_as_of_date"] == "2026-08-07"
    assert payload["short_horizon_decision"]["future_five_day_validation"]["reference_date"] == "2026-08-07"
    assert payload["short_horizon_decision"]["future_five_day_validation"]["title"] == "기본 빈도 대비 예측력 확인 안 됨"
```

```python
def test_current_observation_cards_are_one_five_twenty_days() -> None:
    cards = _intraday_payload()["short_horizon_decision"]["observation_cards"]
    assert [card["key"] for card in cards] == ["1D", "5D", "20D"]
    assert cards[2]["title"] == "20D · 기존 배경과의 관계"
```

Add assertions for semantic family labels such as `금리 부담 완화` and for completed/stale fallback
provenance.

- [ ] **Step 2: Run payload tests and verify RED**

```bash
.venv/bin/python -m pytest tests/test_overview_futures_macro_short_horizon.py -q
```

Expected: failures for missing `current_observation`, v5 schema and observation-card fields.

- [ ] **Step 3: Integrate the DB-only current observation at render time**

In `_render_futures_macro_panel()`, load provisional observation only after the completed materialized
snapshot is available:

```python
current_observation = load_overview_futures_macro_intraday_observation(
    completed_pattern=dict(pattern_outlook.get("current_pattern") or {}),
    evaluation_time=datetime.now(timezone.utc),
)
payload = build_futures_macro_react_workbench_payload(
    macro,
    pattern_outlook=pattern_outlook,
    snapshot_metadata=snapshot_metadata,
    current_observation=current_observation,
)
```

The loader failure path returns a completed fallback payload and must not block page render.

- [ ] **Step 4: Build v5 observation and validation payloads**

Extend `build_futures_macro_react_workbench_payload()` with:

```python
current_observation: dict[str, Any] | None = None
```

Choose the provisional pattern only when mode is `INTRADAY_PROVISIONAL`; keep
`pattern_outlook.horizons` untouched. Add hero provenance and replace the duplicated window rail/step
contract with:

```python
"observation_cards": [
    {"key": "1D", "title": "1D · 지금 새로 생긴 변화", "summary": one_day_summary},
    {"key": "5D", "title": "5D · 현재 단기 방향", "summary": five_day_summary},
    {"key": "20D", "title": "20D · 기존 배경과의 관계", "summary": twenty_day_summary},
]
```

Add `reference_date`, `episode_count`, `evaluation_count`, `model_brier`, `baseline_brier` and
`use_policy` to `future_five_day_validation`. For `NO_EDGE`, return:

```python
{
    "title": "기본 빈도 대비 예측력 확인 안 됨",
    "detail": "표본은 충분하지만 단순 기준보다 정확하지 않았습니다.",
    "use_policy": "현재 흐름을 미래 5거래일 방향으로 연장하지 않습니다.",
}
```

- [ ] **Step 5: Add family-semantic labels and action copy**

Replace the generic direction label lookup with family-specific mappings. Preserve tones and numeric
values. Rename action/button and spinner from `일봉 갱신` to `최신 데이터 갱신`; describe daily +
pending-session 5m behavior without exposing backend row/job diagnostics.

- [ ] **Step 6: Run Task 3 tests and commit**

```bash
.venv/bin/python -m pytest tests/test_overview_futures_macro_short_horizon.py tests/test_futures_macro_intraday.py -q
.venv/bin/python -m py_compile app/services/futures_macro_intraday.py app/web/overview/futures_macro_helpers.py
git add app/web/overview/futures_macro_helpers.py tests/test_overview_futures_macro_short_horizon.py
git commit -m "UI: 선물 매크로 장중 관측과 미래 검증 분리"
```

---

### Task 4: React Current Observation And Forecast Gate

**Files:**
- Create: `app/web/streamlit_components/futures_macro_workbench/src/ForecastValidationGate.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/FuturesMacroWorkbench.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/contracts.ts`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/MacroContextSection.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/ShortHorizonDecisionSection.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/FamilyDirectionSection.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/style.css`
- Modify generated bundle: `app/web/streamlit_components/futures_macro_workbench/component_static/`
- Test: `tests/test_overview_futures_macro_short_horizon.py`

**Interfaces:**
- Consumes: Task 3 v5 payload only.
- Produces: visually separate current observation and completed forecast gate with responsive layout.

- [ ] **Step 1: Add failing React source-contract assertions**

Assert the workbench imports and renders `ForecastValidationGate` after `ShortHorizonDecisionSection`,
the short-horizon section maps `decision.observation_cards`, and the old
`decision.observation_windows` rail is absent.

```python
assert "<ForecastValidationGate" in workbench
assert "decision.observation_cards.map" in short_horizon
assert "decision.observation_windows.map" not in short_horizon
assert "최근 완료 일봉" in forecast_gate
```

- [ ] **Step 2: Run contract test and verify RED**

```bash
.venv/bin/python -m pytest tests/test_overview_futures_macro_short_horizon.py -q
```

- [ ] **Step 3: Update TypeScript contracts and header**

Define exact discriminated values:

```typescript
export type ObservationMode = "INTRADAY_PROVISIONAL" | "COMPLETED";
export type ObservationCard = { key: "1D" | "5D" | "20D"; title: string; summary: string };
```

Add `observation_mode`, `observed_at_et`, `completed_as_of_date`, `freshness_minutes` and
`fallback_reason` to the hero/session contract. In `MacroContextSection`, show `장중 잠정` and
latest completed 5m time as primary facts for intraday mode; show `확정` and completed date otherwise.

- [ ] **Step 4: Render current observation and completed forecast separately**

`ShortHorizonDecisionSection` renders only the three current observation cards. Create
`ForecastValidationGate` with the question `현재 흐름을 향후 5거래일로 연장할 수 있는가?`,
completed reference date, status title/detail/use-policy, and compact sample/performance evidence.

- [ ] **Step 5: Update matrix and responsive CSS**

Keep the 4-core + 2-confirmation hierarchy, widen semantic direction pills without horizontal page
overflow, and stack observation cards plus forecast gate at 760px. Preserve visible focus styles and
button disabled state.

- [ ] **Step 6: Build production bundle and run tests**

```bash
cd app/web/streamlit_components/futures_macro_workbench
npm run build
cd ../../../..
.venv/bin/python -m pytest tests/test_overview_futures_macro_short_horizon.py -q
```

Expected: Vite build succeeds and source/bundle contracts pass.

- [ ] **Step 7: Commit Task 4**

```bash
git add app/web/streamlit_components/futures_macro_workbench/src \
  app/web/streamlit_components/futures_macro_workbench/component_static \
  tests/test_overview_futures_macro_short_horizon.py
git commit -m "UI: 선물 매크로 현재 관측과 검증 게이트 개편"
```

---

### Task 5: Integration Verification, Browser QA And Durable Docs

**Files:**
- Modify: `.aiworkspace/note/finance/docs/flows/README.md`
- Modify: `.aiworkspace/note/finance/docs/data/DATA_FLOW_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/data/TABLE_SEMANTICS.md`
- Modify if ownership changed: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Generated untracked QA screenshot: `futures-macro-intraday-nowcast-v1-qa.png`

**Interfaces:**
- Consumes: Tasks 1-4 completed behavior.
- Produces: verified implementation, canonical documentation and closeout evidence.

- [ ] **Step 1: Run focused and adjacent Python verification**

```bash
.venv/bin/python -m pytest \
  tests/test_futures_macro_intraday.py \
  tests/test_overview_futures_macro_refresh.py \
  tests/test_futures_macro_sessions.py \
  tests/test_futures_macro_pattern_validation.py \
  tests/test_futures_macro_snapshot.py \
  tests/test_overview_futures_macro_short_horizon.py -q
.venv/bin/python -m py_compile \
  app/services/futures_macro_intraday.py \
  app/jobs/futures_macro_daily_finalization.py \
  app/jobs/overview_actions.py \
  app/web/overview/futures_macro_helpers.py
```

- [ ] **Step 2: Verify no provisional persistence path**

Search the implementation and tests:

```bash
rg -n "INTRADAY_PROVISIONAL|persist_futures_macro_snapshot_bundle|futures_macro_forecast_history" \
  app/services/futures_macro_intraday.py app/web/overview/futures_macro_helpers.py tests/test_futures_macro_intraday.py
```

Expected: intraday service has no persistence import/call; tests explicitly assert completed forecast
payload remains unchanged.

- [ ] **Step 3: Run actual refresh and read-only DB verification**

During an active session, run the existing explicit Overview refresh path once. Confirm 17-symbol 5m
collection, `INTRADAY_READY` or documented `INTRADAY_PARTIAL`, common cutoff freshness and unchanged
completed snapshot date before settlement. After cutoff, only claim final advancement if actual 17/17
finalization succeeds.

- [ ] **Step 4: Perform Browser QA**

Open `/overview?overview_tab=futures-macro` and verify:

- desktop and 420px widths
- `장중 잠정` with latest completed 5m time and last completed date, or an honest fallback notice
- current cards ordered 1D / 5D / 20D
- future gate separated and completed-date labeled
- semantic family pills readable without horizontal overflow
- refresh action usable and no duplicate dispatch
- console warning/error count 0

Capture one screenshot at:

```text
/Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev/futures-macro-intraday-nowcast-v1-qa.png
```

Do not stage the screenshot.

- [ ] **Step 5: Synchronize durable documentation**

Update the futures macro flow to state that active-session current observation is a DB-backed 5m
provisional nowcast, while completed snapshot/history and future validation stay EOD-only. Record the
no-schema-change storage contract and exact fallback/freshness semantics. Update `PROJECT_MAP.md` only
if the new service ownership is durable enough to appear in the change-type map.

- [ ] **Step 6: Close task records and final verification**

Set `STATUS.md` to `State: complete` only after tests, build and Browser QA pass. Record commands and
outcomes in `RUNS.md`, discoveries in `NOTES.md`, and only remaining genuine risks in `RISKS.md`.

```bash
git diff --check
git status --short
```

- [ ] **Step 7: Commit closeout**

```bash
git add .aiworkspace/note/finance/docs \
  .aiworkspace/note/finance/tasks/active/overview-futures-macro-intraday-nowcast-v1-20260811
git commit -m "문서: 선물 매크로 장중 관측 흐름 정렬"
```

Do not stage unrelated registry, run history, research bundle, screenshots or existing user files.

---

## Self-Review Result

- Spec coverage: current observation, completed fallback, future validation, storage, refresh,
  error handling, React UX, responsive QA and docs each map to Tasks 1-5.
- Scope: one feature path; provider migration, automatic refresh and intraday forecast remain excluded.
- Type consistency: Python `observation_mode` values match TypeScript `ObservationMode`; v5 payload is
  introduced in Task 3 and consumed in Task 4.
- Persistence consistency: only raw 5m collector writes; Task 1 service and Task 3 payload remain
  read-only, and completed materialization remains Task 2's existing path.
