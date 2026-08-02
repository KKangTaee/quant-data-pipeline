# Inflation Policy Workbench Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let a user inspect the forward inflation/policy/yield path, prepare for the next Core PCE release, save a dynamic yield criterion, and reverse a target yield into conditional policy and PCE paths.

**Architecture:** Add an independent DB-only service payload under the existing economic-cycle component shell. React owns local navigation and form drafts; Streamlit/Python owns saved-criterion commands and bounded reverse calculations using stored artifacts. The existing cycle screen remains behaviorally unchanged and is not used to calculate the new view.

**Tech Stack:** Python 3.12, Streamlit components, React 18, TypeScript 5.7, Vite 6, Vitest, pytest-style service/bridge tests, in-app Browser QA.

## Global Constraints

- Inner navigation is `경기 국면 | 물가·정책 경로`; existing cycle is the default to preserve current behavior.
- The new service may attach to the same transport payload but cannot call `build_economic_cycle_read_model` or consume its output.
- The first new screen shows conclusions and next conditions, not job counts, saved rows, or raw statuses.
- React sends explicit commands; it never writes DB state or computes canonical model probabilities.
- Reverse calculation is DB-only and uses the exact persisted model artifact/version from the selected snapshot.
- Automatic and user criteria must remain visually and semantically distinct.
- `LIMITED`, `NOT_AVAILABLE`, and stale data have user-readable states; last-good data carries its historical timestamp and is not labeled current.

---

## File Structure

### Create

- `app/services/overview/inflation_policy.py`: JSON-safe DB-only read model.
- `app/services/overview/inflation_policy_commands.py`: save-criterion and reverse-scenario command handlers.
- `app/web/streamlit_components/economic_cycle_workbench/src/inflationPolicyTypes.ts`
- `app/web/streamlit_components/economic_cycle_workbench/src/InflationPolicyWorkbench.tsx`
- `app/web/streamlit_components/economic_cycle_workbench/src/InflationStatePanel.tsx`
- `app/web/streamlit_components/economic_cycle_workbench/src/PolicyPathPanel.tsx`
- `app/web/streamlit_components/economic_cycle_workbench/src/YieldResistancePanel.tsx`
- `app/web/streamlit_components/economic_cycle_workbench/src/ReverseScenarioPanel.tsx`
- `app/web/streamlit_components/economic_cycle_workbench/src/InflationEvidencePanel.tsx`
- `app/web/streamlit_components/economic_cycle_workbench/src/InflationPolicyWorkbench.test.tsx`
- `tests/test_inflation_policy_service.py`
- `tests/test_inflation_policy_commands.py`
- `tests/test_market_context_inflation_policy.py`

### Modify

- `finance/loaders/inflation_policy.py`: add strict DB readers for saved resistance definitions and exact model artifacts.
- `tests/test_inflation_policy_loaders.py`: cover PIT cutoff, active-user filtering, and exact artifact identity.
- `app/web/overview/market_context_helpers.py:58-175`: attach independent payload, handle explicit commands, and add fallback.
- `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`: add inner selector and render independent child.
- `app/web/streamlit_components/economic_cycle_workbench/src/style.css`: add responsive decision-workbench styles.
- `app/web/streamlit_components/economic_cycle_workbench/package.json`: add test script and Vitest/testing dependencies.
- `app/web/streamlit_components/economic_cycle_workbench/package-lock.json`
- `app/web/streamlit_components/economic_cycle_workbench/component_static/`: rebuild tracked output.
- `tests/test_market_context_economic_cycle.py`: preserve existing routing and add DB-only source guard.
- `.aiworkspace/note/finance/tasks/active/inflation-policy-workbench/`: create task records.
- `.aiworkspace/note/finance/phases/active/inflation-policy-yield-path/{TASKS,STATUS,RISKS}.md`

## Stable Service Contract

```python
def build_inflation_policy_read_model(
    *,
    as_of_at: str | datetime | None = None,
    snapshot_loader: Callable[..., Mapping[str, object] | None] | None = None,
    definitions_loader: Callable[..., Sequence[Mapping[str, object]]] | None = None,
) -> dict[str, object]: ...

def save_user_resistance_definition(command: Mapping[str, object]) -> dict[str, object]: ...
def run_reverse_scenario_command(command: Mapping[str, object]) -> dict[str, object]: ...
```

Read-model top-level keys, in order:

```python
[
    "schema_version", "publication_status", "as_of_at", "model_version",
    "headline", "inflation", "policy", "rates", "reverse_scenario",
    "equity_stress", "recession", "evidence", "freshness", "warnings",
]
```

### Task 1: Build the independent Overview read model

**Files:**
- Modify: `finance/loaders/inflation_policy.py`
- Modify: `tests/test_inflation_policy_loaders.py`
- Create: `app/services/overview/inflation_policy.py`
- Create: `tests/test_inflation_policy_service.py`
- Create: `.aiworkspace/note/finance/tasks/active/inflation-policy-workbench/{PLAN,DESIGN,STATUS,NOTES,RUNS,RISKS}.md`

**Interfaces:**
- Consumes: `load_latest_inflation_policy_snapshot`, `load_yield_resistance_definitions`.
- Produces: `inflation_policy_v1` JSON-safe read model.

- [x] **Step 0: Add the missing DB-only loader contracts with TDD**

Add `load_yield_resistance_definitions(as_of_at=..., include_inactive=False)` and
`load_inflation_policy_model_artifact(model_version=..., trained_cutoff_at=...)`.
Definitions must exclude future `known_at`/`saved_at` rows and inactive USER rows by
default. Artifact lookup must require both exact identity fields and fail closed with
`None`; it must never select a different cutoff for the same version.

- [x] **Step 1: Write the failing ready-payload test**

```python
def test_ready_read_model_keeps_forward_reverse_and_quality_separate() -> None:
    model = build_inflation_policy_read_model(
        snapshot_loader=lambda **_: ready_snapshot_fixture(),
        definitions_loader=lambda **_: [automatic_zone_fixture(), user_zone_fixture()],
    )
    assert list(model) == [
        "schema_version", "publication_status", "as_of_at", "model_version",
        "headline", "inflation", "policy", "rates", "reverse_scenario",
        "equity_stress", "recession", "evidence", "freshness", "warnings",
    ]
    assert model["schema_version"] == "inflation_policy_v1"
    assert sum(model["inflation"]["state_probabilities"].values()) == pytest.approx(1.0)
    assert {item["owner"] for item in model["rates"]["resistance_zones"]} == {"AUTO", "USER"}
    json.dumps(model, allow_nan=False)
```

- [x] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_service.py -q
```

Expected: FAIL on missing service.

- [x] **Step 3: Implement strict snapshot adaptation**

Decode only expected JSON fields, normalize simplexes, preserve null optional components, and translate publication reasons into Korean. If the snapshot is missing, return `NOT_AVAILABLE` with empty typed sections. If schema/probability validation fails, return `FAILED`; never call a provider or model fit function.

- [x] **Step 4: Add source-boundary assertions**

```python
def test_service_is_db_only_and_cycle_independent() -> None:
    source = Path("app/services/overview/inflation_policy.py").read_text()
    assert "finance.data." not in source
    assert "requests" not in source and "urlopen" not in source
    assert "economic_cycle" not in source
```

- [x] **Step 5: Run tests and commit**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_service.py -q
git add app/services/overview/inflation_policy.py tests/test_inflation_policy_service.py \
  .aiworkspace/note/finance/tasks/active/inflation-policy-workbench
git commit -m "물가 정책 경로 조회 모델 추가"
```

### Task 2: Add saved-criterion and reverse-scenario commands

**Files:**
- Create: `app/services/overview/inflation_policy_commands.py`
- Create: `tests/test_inflation_policy_commands.py`

**Interfaces:**
- Consumes: stored definitions, exact snapshot/artifact, `reverse_condition_paths`.
- Produces the command functions in the stable interface.

- [x] **Step 1: Write failing command validation tests**

```python
def test_save_command_cannot_claim_auto_owner() -> None:
    with pytest.raises(ValueError, match="USER"):
        save_user_resistance_definition({
            "owner": "AUTO", "instrument": "DGS10", "lower_pct": 4.68,
            "upper_pct": 4.75, "buffer_pct": 0.05,
        })

def test_reverse_command_uses_exact_snapshot_model_version() -> None:
    result = run_reverse_scenario_command(
        reverse_command_fixture(),
        snapshot_loader=lambda **_: {"model_version": "inflation-policy-v1", "as_of_at": "2026-08-02T00:00:00Z"},
        artifact_loader=exact_artifact_loader,
        scenario_runner=reverse_runner_spy,
    )
    assert result["model_version"] == "inflation-policy-v1"
```

- [x] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_commands.py -q
```

Expected: FAIL on missing commands.

- [x] **Step 3: Implement save validation**

Allow only `USER`, instruments `DGS2|DGS10|DFII10|T10YIE|T10Y2Y|ACMTP10`, finite ordered bounds, non-negative buffer, lookbacks from `63|252|504`, and confirmation window/count within `1..20`. Generate a stable UUID, persist through the result store, and return compact definition/read-model data.

- [x] **Step 4: Implement bounded reverse execution**

Require target condition `REACH|CONFIRMED|HOLD`, horizon not before snapshot as-of, target width at most 200bp, and exact artifact match. Run only stored-data simulation with a maximum 50,000 paths and return `NOT_AVAILABLE` when effective sample size is below the model threshold.

- [x] **Step 5: Run tests and commit**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_commands.py tests/test_inflation_policy_simulation.py -q
git add app/services/overview/inflation_policy_commands.py tests/test_inflation_policy_commands.py
git commit -m "금리 기준 저장과 역산 명령 추가"
```

### Task 3: Attach the independent payload and command bridge

**Files:**
- Modify: `app/web/overview/market_context_helpers.py:58-175`
- Modify: `tests/test_market_context_economic_cycle.py`
- Create: `tests/test_market_context_inflation_policy.py`

**Interfaces:**
- Consumes: both independent read-model builders and explicit commands.
- Produces: optional `payload["inflation_policy"]` and event IDs `save_yield_criterion`, `run_reverse_scenario`.

- [x] **Step 1: Write failing payload-isolation tests**

```python
def test_cycle_transport_attaches_independent_inflation_policy_payload() -> None:
    payload = load_market_context_cycle_transport(
        cycle_builder=lambda: {"schema_version": "economic_cycle_v2"},
        inflation_policy_builder=lambda: {"schema_version": "inflation_policy_v1"},
    )
    assert payload["schema_version"] == "economic_cycle_v2"
    assert payload["inflation_policy"]["schema_version"] == "inflation_policy_v1"

def test_inflation_command_never_triggers_provider_refresh() -> None:
    result = handle_inflation_policy_event(
        {"id": "run_reverse_scenario", "nonce": "r1", "payload": reverse_command_fixture()},
        command_runner=Mock(return_value={"publication_status": "READY"}),
        provider_refresh=Mock(side_effect=AssertionError("provider must not run")),
    )
    assert result is True
```

- [x] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_market_context_inflation_policy.py tests/test_market_context_economic_cycle.py -q
```

Expected: new tests fail; existing cycle tests pass.

- [x] **Step 3: Implement cached independent composition**

Create `load_inflation_policy_model()` with the same 300-second DB-only cache. `load_economic_cycle_model()` remains cycle-only; `render_economic_cycle()` composes the two JSON-safe dictionaries immediately before transport so neither service calls the other.

- [x] **Step 4: Implement once-only command events**

Use nonce tokens separate from `ECONOMIC_CYCLE_EVENT_KEY`. Save command results in session state, clear only the inflation-policy cache on success, and rerun. Provider refresh remains bound only to the existing explicit refresh event.

- [x] **Step 5: Add fallback rendering**

When the React build is missing, add a small `st.segmented_control` and render Core PCE state, policy path, nearest zone, and unavailable reason. Reverse/save forms remain React-only; the fallback must not compute probabilities.

- [x] **Step 6: Run tests and commit**

```bash
.venv/bin/python -m pytest tests/test_market_context_inflation_policy.py tests/test_market_context_economic_cycle.py -q
git add app/web/overview/market_context_helpers.py tests/test_market_context_inflation_policy.py tests/test_market_context_economic_cycle.py
git commit -m "경제 사이클 화면에 물가 정책 경로 연결"
```

### Task 4: Add React types, test harness, and inner navigation

**Files:**
- Create: `app/web/streamlit_components/economic_cycle_workbench/src/inflationPolicyTypes.ts`
- Create: `app/web/streamlit_components/economic_cycle_workbench/src/InflationPolicyWorkbench.tsx`
- Create: `app/web/streamlit_components/economic_cycle_workbench/src/InflationPolicyWorkbench.test.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/package.json`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/package-lock.json`

**Interfaces:**
- Consumes: `InflationPolicyPayload`.
- Produces:

```ts
export type InflationPolicyCommand =
  | { id: "save_yield_criterion"; nonce: string; payload: SaveCriterionPayload }
  | { id: "run_reverse_scenario"; nonce: string; payload: ReverseScenarioPayload };

export type InflationPolicyWorkbenchProps = {
  payload: InflationPolicyPayload;
  onCommand: (command: InflationPolicyCommand) => void;
};
```

- [x] **Step 1: Add Vitest dependencies and failing navigation test**

Add script `"test": "vitest run"` and dev dependencies `vitest`, `jsdom`, `@testing-library/react`, `@testing-library/jest-dom`.

```tsx
it("keeps 경기 국면 as default and opens 물가·정책 경로 explicitly", async () => {
  render(<ConnectedShell payload={combinedPayloadFixture()} />);
  expect(screen.getByRole("heading", { name: /현재와 앞으로 1·2개월/ })).toBeInTheDocument();
  await userEvent.click(screen.getByRole("button", { name: "물가·정책 경로" }));
  expect(screen.getByRole("heading", { name: /연말 Core PCE 경로/ })).toBeInTheDocument();
});
```

- [x] **Step 2: Run the test to verify it fails**

```bash
npm --prefix app/web/streamlit_components/economic_cycle_workbench test
```

Expected: FAIL on missing types/component/navigation.

- [x] **Step 3: Implement typed payload and selector**

Add optional `inflation_policy?: InflationPolicyPayload` to the existing transport type. Render an accessible two-button tablist above both screens. Hide the new tab only when the property is absent; show it with `NOT_AVAILABLE` content when the property exists but data is unavailable.

- [x] **Step 4: Implement command transport**

Convert child commands to `Streamlit.setComponentValue({ event: command })` and keep the existing refresh event unchanged. Generate nonce from command type plus `Date.now()` only at click submission, not during render.

- [x] **Step 5: Run tests/build and commit**

```bash
npm --prefix app/web/streamlit_components/economic_cycle_workbench test
npm --prefix app/web/streamlit_components/economic_cycle_workbench run build
git add app/web/streamlit_components/economic_cycle_workbench/src \
  app/web/streamlit_components/economic_cycle_workbench/package.json \
  app/web/streamlit_components/economic_cycle_workbench/package-lock.json
git commit -m "물가 정책 경로 화면 선택기 추가"
```

### Task 5: Build forward decision panels

**Files:**
- Create: `app/web/streamlit_components/economic_cycle_workbench/src/InflationStatePanel.tsx`
- Create: `app/web/streamlit_components/economic_cycle_workbench/src/PolicyPathPanel.tsx`
- Create: `app/web/streamlit_components/economic_cycle_workbench/src/YieldResistancePanel.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/InflationPolicyWorkbench.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/InflationPolicyWorkbench.test.tsx`

**Interfaces:**
- Consumes: inflation, policy, rates sections.
- Produces: conclusion → five states → next-release preparation → policy → rates flow.

- [x] **Step 1: Write failing content-priority tests**

Test five state labels and 100% total, 3.4/3.5/3.6 thresholds, next-print rows 0.1–0.5, policy net-move bins, automatic/user zone badges, and no visible strings matching `저장 rows|실행 job|실패 job`.

- [x] **Step 2: Run tests to verify they fail**

```bash
npm --prefix app/web/streamlit_components/economic_cycle_workbench test
```

Expected: FAIL on missing panels.

- [x] **Step 3: Implement the decision hierarchy**

Top summary shows Q4Q4 median/range, dominant inflation state, next-meeting path, nearest DGS10 zone/state, and one next condition. Five-state bars retain every probability. The preparation table shows each hypothetical next print and posterior delta without action recommendations.

- [x] **Step 4: Implement rate-driver and confirmation copy**

Show separate policy/term-premium and real/breakeven lenses, driver label, and `미확인|혼합|인플레이션 확인`. If ACM is unavailable, label the missing lens and do not infer a term-premium value.

- [x] **Step 5: Run tests and commit**

```bash
npm --prefix app/web/streamlit_components/economic_cycle_workbench test
git add app/web/streamlit_components/economic_cycle_workbench/src
git commit -m "물가 정책 순방향 판단 패널 추가"
```

### Task 6: Build reverse scenario and custom criterion workflow

**Files:**
- Create: `app/web/streamlit_components/economic_cycle_workbench/src/ReverseScenarioPanel.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/YieldResistancePanel.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/InflationPolicyWorkbench.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/InflationPolicyWorkbench.test.tsx`

**Interfaces:**
- Consumes: zones and optional command results.
- Produces: validated `save_yield_criterion` and `run_reverse_scenario` events.

- [x] **Step 1: Write failing form/event tests**

```tsx
it("submits a conditional target instead of a required hike scalar", async () => {
  const onCommand = vi.fn();
  render(<InflationPolicyWorkbench payload={readyPayload()} onCommand={onCommand} />);
  await userEvent.selectOptions(screen.getByLabelText("금리 종류"), "DGS10");
  await userEvent.type(screen.getByLabelText("구간 하단"), "4.68");
  await userEvent.type(screen.getByLabelText("구간 상단"), "4.75");
  await userEvent.click(screen.getByRole("button", { name: "필요 경로 역산" }));
  expect(onCommand.mock.calls[0][0].id).toBe("run_reverse_scenario");
  expect(onCommand.mock.calls[0][0].payload).not.toHaveProperty("required_hike_count");
});
```

Test invalid bounds disable submit, automatic criteria cannot be edited, and save emits owner `USER`.

- [x] **Step 2: Run tests to verify they fail**

```bash
npm --prefix app/web/streamlit_components/economic_cycle_workbench test
```

Expected: FAIL on missing workflow.

- [x] **Step 3: Implement criterion save form**

Initialize from an automatic zone but label it `사용자 기준으로 복사`. Accept name, bounds, buffer, confirmation count/window, breakeven confirmation, and term-premium exclusion. On save, show pending state until Python returns the saved criterion.

- [x] **Step 4: Implement reverse result presentation**

Show conditional policy distribution, Q4Q4 quantiles, required remaining monthly PCE quantiles, next-print sensitivity, matched path count/effective sample size, and explicit `조건부분포` copy. `NOT_AVAILABLE` shows the reason and suggests widening the zone/horizon, not a guessed value.

- [x] **Step 5: Run tests and commit**

```bash
npm --prefix app/web/streamlit_components/economic_cycle_workbench test
git add app/web/streamlit_components/economic_cycle_workbench/src
git commit -m "금리 목표 역산과 사용자 기준 저장 화면 추가"
```

### Task 7: Add evidence, replay, responsive styles, and QA

**Files:**
- Create: `app/web/streamlit_components/economic_cycle_workbench/src/InflationEvidencePanel.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/InflationPolicyWorkbench.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/style.css`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/component_static/`
- Modify: `.aiworkspace/note/finance/tasks/active/inflation-policy-workbench/{STATUS,NOTES,RUNS,RISKS}.md`
- Modify: `.aiworkspace/note/finance/phases/active/inflation-policy-yield-path/{TASKS,STATUS,RISKS}.md`
- Modify: `.aiworkspace/note/finance/docs/flows/README.md`

**Interfaces:**
- Consumes: evidence, freshness, warnings, replay timestamps.
- Produces: completed responsive workbench and durable flow documentation.

- [x] **Step 1: Write failing evidence/unavailable tests**

Test observation/release/collection/as-of timestamps, model/state/zone versions, warnings, historical last-good labeling, `NOT_AVAILABLE` recession, and no numeric probability when publication status is not `READY`.

- [x] **Step 2: Implement evidence and replay disclosure**

Keep methodology collapsed by default. Show top evidence with observation/release dates and whether it supports inflation, policy, or yield confirmation. Historical results must begin with `과거 기준` and the original as-of time.

- [x] **Step 3: Implement responsive styles**

Desktop uses a 12-column grid with conclusion and preparation first. At `max-width: 720px`, use one column in the same semantic order. Ensure long model/reason strings wrap and form controls have 44px minimum hit height.

- [x] **Step 4: Run automated verification**

```bash
.venv/bin/python -m pytest tests/test_inflation_policy_service.py tests/test_inflation_policy_commands.py tests/test_market_context_inflation_policy.py tests/test_market_context_economic_cycle.py -q
npm --prefix app/web/streamlit_components/economic_cycle_workbench test
npm --prefix app/web/streamlit_components/economic_cycle_workbench run build
git diff --check
```

Expected: all tests/builds pass.

- [x] **Step 5: Run Browser QA**

Open Market Research > 경제 사이클, select 물가·정책 경로, and verify at desktop and 420px: forward content, next-print table, policy, zones, criterion form, reverse result, unavailable states, keyboard tab order, no horizontal overflow, and zero console/page errors. Save one screenshot as a generated artifact outside the commit.

- [x] **Step 6: Use `finance-doc-sync`, update state, and commit**

Set the workbench task complete only with automated and Browser QA evidence; keep phase active for equity/recession.

```bash
git add app/web/streamlit_components/economic_cycle_workbench/src \
  app/web/streamlit_components/economic_cycle_workbench/package.json \
  app/web/streamlit_components/economic_cycle_workbench/package-lock.json \
  app/web/streamlit_components/economic_cycle_workbench/component_static \
  .aiworkspace/note/finance/tasks/active/inflation-policy-workbench \
  .aiworkspace/note/finance/phases/active/inflation-policy-yield-path \
  .aiworkspace/note/finance/docs/flows/README.md
git commit -m "물가 정책 경로 워크벤치 검증 완료"
```
