# Portfolio Monitoring React Command Center V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Operations > Portfolio Monitoring을 DB-backed group/item lifecycle, 공통 가치곡선, 근거형 진단, macro risk observation을 갖는 React one-shell로 전환한다.

**Architecture:** 기존 Streamlit navigation route는 유지하되 화면은 thin Python component bridge가 `portfolio_monitoring_workspace_v1` projection을 React에 전달한다. 새 `app/services/portfolio_monitoring/` package가 command validation, persistence, catalog, valuation, exposure, diagnosis, macro context, read model을 소유하고, 기존 Final Review runtime은 selected-strategy replay compatibility adapter로만 사용한다.

**Tech Stack:** Python 3, pandas, PyMySQL/MySQL (`finance_meta`, `finance_price`), Streamlit custom components, React 18, TypeScript, Vite, Vitest, pytest/unittest, Browser QA.

## Global Constraints

- 사용자-facing route는 `Operations > Portfolio Monitoring`과 `selected-portfolio-dashboard`를 유지한다.
- UI/provider direct fetch를 금지하고 `Ingestion -> DB -> Loader -> Service -> UI`만 허용한다.
- `.aiworkspace/note/finance/registries/*.jsonl`과 `.aiworkspace/note/finance/saved/SELECTED_DASHBOARD_PORTFOLIOS.jsonl`을 재작성·삭제하지 않는다.
- direct security의 수량 입력은 정수 `>= 1`만 허용한다. fixed notional은 fractional virtual units를 허용한다.
- selected strategy는 fixed notional만 허용한다.
- active item은 group당 최대 10개이며 ended item은 한도에서 제외한다.
- missing start price는 등록 blocker다. requested date 이후 첫 usable session을 effective date로 사용한다.
- item start 전과 tracking end 후 자금은 0% cash lane으로 group value에 포함한다.
- group KPI는 active item의 latest common basis date를 사용하며 다른 날짜 값을 섞지 않는다.
- React는 effective date, valuation, MDD/CAGR, diagnosis severity/confidence를 계산하지 않는다.
- 화면은 주문, broker sync, live approval, 실제 계좌 cash flow, auto rebalance를 만들지 않는다.
- 각 태스크는 red test 확인 후 최소 구현, focused verification, `git diff --check`, coherent 한국어 commit 순서로 닫는다.
- 각 user-facing stage(3차, 4차, 5차, 6차)는 Browser QA screenshot을 task RUNS에 경로로 기록하되 생성물은 stage하지 않는다.

---

## 1차 — Contract And Storage Foundation

### Task 1: DB schema와 versioned domain identity를 고정한다

**Files:**

- Modify: `finance/data/db/schema.py`
- Create: `app/services/portfolio_monitoring/__init__.py`
- Create: `app/services/portfolio_monitoring/schemas.py`
- Create: `tests/test_portfolio_monitoring_schema.py`

**Interfaces:**

- `PORTFOLIO_MONITORING_SCHEMAS: dict[str, str]`
- `SourceType`, `InstrumentKind`, `FundingMode`, `ItemStatus`, `CommandStatus`
- `AddMonitoringItemInput`, `MonitoringCommandInput`
- `validate_add_item_input(value) -> AddMonitoringItemInput`
- `build_request_fingerprint(payload) -> str`

- [x] Write failing schema tests asserting `monitoring_portfolio_group`, `monitoring_portfolio_item`, and `monitoring_portfolio_command`, their unique/index keys, optimistic `version`, lifecycle dates, source/funding enums, and command idempotency fields.
- [x] Write failing domain tests for integer-share rejection (`1.5`, `0`), selected-strategy share rejection, positive notional validation, and stable key-order-independent SHA-256 request fingerprint.
- [x] Run `./.venv/bin/python -m unittest tests.test_portfolio_monitoring_schema` and confirm failure because the package/constant does not exist.
- [x] Add the three `finance_meta` CREATE TABLE contracts and minimal immutable dataclass/enum validation implementation. Use this shape as the public input boundary:

```python
@dataclass(frozen=True)
class AddMonitoringItemInput:
    portfolio_group_id: str
    source_type: SourceType
    source_ref: str
    instrument_kind: InstrumentKind
    requested_start_date: date
    funding_mode: FundingMode
    input_notional: Decimal | None = None
    input_shares: int | None = None
```

- [x] Run `./.venv/bin/python -m unittest tests.test_portfolio_monitoring_schema`, `./.venv/bin/python -m py_compile finance/data/db/schema.py app/services/portfolio_monitoring/schemas.py`, and `git diff --check`.
- [x] Commit as `포트폴리오 모니터링 저장 계약 추가`.

### Task 2: repository transaction과 idempotent command executor를 구현한다

**Files:**

- Create: `app/services/portfolio_monitoring/persistence.py`
- Create: `app/services/portfolio_monitoring/commands.py`
- Create: `tests/test_portfolio_monitoring_commands.py`

**Interfaces:**

- `MonitoringRepository` protocol
- `MySQLMonitoringRepository(db_factory: Callable[[], MySQLClient])`
- `ensure_schema()`, `get_or_create_default_group()`, `list_groups()`, `list_items()`
- `execute_create_group`, `execute_rename_group`, `execute_add_item`, `execute_end_item`
- `CommandResult(status, command_id, target_id, replayed, message)`

- [x] Write fake-repository tests for one default group only, unique non-empty names, rename version conflict, same command ID replay, same command ID/different fingerprint rejection, active duplicate source rejection, and active 10/10 rejection.
- [x] Run `./.venv/bin/python -m unittest tests.test_portfolio_monitoring_commands` and confirm import/behavior failures.
- [x] Implement repository methods with injected `MySQLClient`, explicit `begin/commit/rollback`, parameterized SQL, soft lifecycle fields, and `monitoring_portfolio_command` lookup before mutation.
- [x] Implement commands as server-owned validation. The executor boundary must remain:

```python
def execute_add_item(
    repository: MonitoringRepository,
    command: MonitoringCommandInput,
    item: AddMonitoringItemInput,
    *,
    resolve_entry: Callable[[AddMonitoringItemInput], EntryResolution],
) -> CommandResult:
    validated = validate_add_item_input(item)
    entry = resolve_entry(validated)
    return _persist_add_item(repository, command, validated, entry)
```

- [x] Run `./.venv/bin/python -m unittest tests.test_portfolio_monitoring_commands`, `./.venv/bin/python -m py_compile app/services/portfolio_monitoring/persistence.py app/services/portfolio_monitoring/commands.py`, and `git diff --check`.
- [x] Commit as `포트폴리오 모니터링 명령 경계 구현`.

### Task 3: legacy saved setup을 비파괴 dry-run/import 계약으로 연결한다

**Files:**

- Modify: `app/services/portfolio_monitoring/persistence.py`
- Create: `tests/fixtures/selected_dashboard_portfolios_legacy.jsonl`
- Create: `tests/test_portfolio_monitoring_legacy_import.py`

**Interfaces:**

- `build_legacy_import_plan(path, final_candidates) -> LegacyImportPlan`
- `import_legacy_portfolios(repository, plan, command_id) -> LegacyImportResult`
- provenance keys: `legacy_portfolio_id`, `legacy_slot_id`, `legacy_decision_id`, `legacy_source_fingerprint`

**Minimal implementation shape:**

```python
plan = build_legacy_import_plan(path, final_candidates)
return plan if not apply else _apply_legacy_import(repository, plan, command_id)
```

- [x] Add a fixture with two legacy groups, one valid strategy slot, one missing Final Review decision, and one duplicate source row. Test that dry-run writes nothing and reports exact create/skip/block counts.
- [x] Add import tests proving source file bytes are unchanged, a second import is a no-op, valid strategy slots retain start/notional provenance, and missing decisions block only their item rather than deleting the group.
- [x] Run `./.venv/bin/python -m unittest tests.test_portfolio_monitoring_legacy_import` and confirm missing API failures.
- [x] Implement deterministic source hashing and an explicit read-only plan / separate apply boundary. Import through normal idempotent command/repository paths; never call the legacy JSONL writer.
- [x] Run `./.venv/bin/python -m unittest tests.test_portfolio_monitoring_legacy_import`, then `git diff --check`, and record fixture/source checksum verification in task `RUNS.md`.
- [x] Commit as `기존 모니터링 설정 비파괴 이관 추가`.

**1차 완료 게이트:** schema/command/import tests pass; production DB migration is not run automatically; legacy file checksum is unchanged. This stage does not yet render React or calculate portfolio performance.

---

## 2차 — Monitoring Service Foundation

### Task 4: direct security와 Final Review candidate 통합 catalog를 만든다

**Files:**

- Create: `app/services/portfolio_monitoring/catalog.py`
- Create: `tests/test_portfolio_monitoring_catalog.py`

**Interfaces:**

- `CatalogItem(source_type, source_ref, instrument_kind, label, metadata, readiness)`
- `search_direct_securities(query, *, db_factory, limit=20)`
- `list_monitoring_candidates(*, decision_loader=load_current_final_selection_decisions)`
- `search_monitoring_catalog(query: str, source_type: SourceType, *, db_factory, decision_loader, limit: int = 20)`

**Minimal implementation shape:**

```python
return [CatalogItem(source_type="direct_security", source_ref=row["symbol"], instrument_kind=row["kind"], label=row["name"], metadata={}, readiness="READY") for row in rows]
```

- [x] Write failing tests that union `nyse_stock` and `nyse_etf` without losing kind identity, search symbol/name case-insensitively, cap results, and exclude inactive/unknown rows when lifecycle says unavailable.
- [x] Write Final Review adapter tests proving only `monitoring_candidate is True` rows are exposed and `decision_id` is the authoritative `source_ref`.
- [x] Run `./.venv/bin/python -m unittest tests.test_portfolio_monitoring_catalog` and confirm failure.
- [x] Implement DB-only parameterized search and a pure candidate projector; do not call providers or mutate registries.
- [x] Run `./.venv/bin/python -m unittest tests.test_portfolio_monitoring_catalog`, `./.venv/bin/python -m py_compile app/services/portfolio_monitoring/catalog.py`, and `git diff --check`.
- [x] Commit as `포트폴리오 모니터링 종목 카탈로그 구현`.

### Task 5: direct-security event ledger와 entry resolution을 구현한다

**Files:**

- Create: `app/services/portfolio_monitoring/valuation.py`
- Create: `tests/test_portfolio_monitoring_valuation.py`

**Interfaces:**

- `resolve_direct_security_entry(history, requested_date, funding_mode, value) -> EntryResolution`
- `build_direct_security_value_lane(item, history) -> ItemValueLane`
- `CorporateActionReview(status, total_return_gap, max_session_gap, reasons)`

**Minimal implementation shape:**

```python
total_value = effective_units * raw_close + accumulated_dividend_cash
```

- [x] Write failing tests for weekend/holiday later-first-session resolution, no-later-price blocker, fixed-notional fractional units, integer shares, split-adjusted effective units, cash dividends without reinvestment, and zero-price rejection.
- [x] Add cross-check tests for end return gap `> 0.50%p` or one-session gap `> 1.00%p` becoming `data_review`, while exactly-on-threshold remains valid.
- [x] Run `./.venv/bin/python -m unittest tests.test_portfolio_monitoring_valuation` and confirm missing implementation failures.
- [x] Implement raw-close primary ledger ordered by date. Keep output columns explicit:

```python
date, effective_units, market_value, dividend_cash, total_value,
raw_return_index, adjusted_return_index, data_status
```

- [x] Run `./.venv/bin/python -m unittest tests.test_portfolio_monitoring_valuation`, `./.venv/bin/python -m py_compile app/services/portfolio_monitoring/valuation.py`, and `git diff --check`.
- [x] Commit as `직접 종목 가치 추적 원장 구현`.

### Task 6: selected-strategy lane을 legacy replay adapter로 분리한다

**Files:**

- Create: `app/services/portfolio_monitoring/selected_strategy.py`
- Modify: `app/services/portfolio_monitoring/valuation.py`
- Create: `tests/test_portfolio_monitoring_selected_strategy.py`

**Interfaces:**

- `SelectedStrategyReplayAdapter`
- `load_candidate_contract(decision_id) -> SelectedStrategyContract`
- `build_value_lane(item, end_date=None) -> ItemValueLane`
- `SelectedStrategyReadiness(status, blockers, source_dates)`

**Minimal implementation shape:**

```python
normalized = replay_curve["value"] / replay_curve["value"].iloc[0]
return ItemValueLane(curve=normalized * item.initial_capital, readiness=readiness)
```

- [x] Write failing adapter tests with an injected Final Review row/replay function for valid normalized curve, missing decision, missing replay contract, replay failure, and share-mode rejection.
- [x] Run `./.venv/bin/python -m unittest tests.test_portfolio_monitoring_selected_strategy` and confirm failures.
- [x] Wrap the smallest reusable functions from `app/runtime/backtest/read_models/final_selected_portfolios.py`; do not move or rewrite the entire monolith in this task.
- [x] Scale the normalized strategy curve by fixed notional and return explicit readiness/source provenance. No monitoring-level synthetic shares.
- [x] Run `./.venv/bin/python -m unittest tests.test_portfolio_monitoring_selected_strategy`, `./.venv/bin/python -m py_compile app/services/portfolio_monitoring/selected_strategy.py app/services/portfolio_monitoring/valuation.py`, and `git diff --check`.
- [x] Commit as `선정 전략 모니터링 재생 어댑터 분리`.

### Task 7: staggered start/end cash와 common-basis group KPI를 계산한다

**Files:**

- Modify: `app/services/portfolio_monitoring/valuation.py`
- Create: `app/services/portfolio_monitoring/read_model.py`
- Create: `tests/test_portfolio_monitoring_read_model.py`

**Interfaces:**

- `align_group_value_lanes(items, lanes) -> GroupValueResult`
- `calculate_group_metrics(group_curve, invested_capital, basis_date) -> GroupMetrics`
- `build_portfolio_monitoring_workspace(repository, *, active_group_id=None, catalog_query="", generated_at=None) -> dict[str, object]`
- schema version: `portfolio_monitoring_workspace_v1`

**Minimal implementation shape:**

```python
basis_date = min(lane.latest_usable_date for lane in active_lanes)
current_value = sum(lane.value_at(basis_date) for lane in all_lanes)
```

- [x] Write failing tests for pre-start planned cash, post-end exit cash, ended items excluded from active limit but retained in history, two staggered starts, one stale active item moving the common basis date backward, and a failed lane producing explicit `PARTIAL` rather than silent exclusion.
- [x] Test invested capital/current value/P&L/total return, daily-curve MDD, actual-day CAGR, `<365` short-window marker, total contribution, and downside contribution.
- [x] Run `./.venv/bin/python -m unittest tests.test_portfolio_monitoring_read_model` and confirm failures.
- [x] Implement alignment without interpolation. Projection top-level keys must be `schema_version`, `generated_at`, `groups`, `active_group`, `catalog`, `commands`, `method`, and `boundaries`.
- [x] Run `./.venv/bin/python -m unittest tests.test_portfolio_monitoring_catalog tests.test_portfolio_monitoring_valuation tests.test_portfolio_monitoring_selected_strategy tests.test_portfolio_monitoring_read_model`, `./.venv/bin/python -m py_compile app/services/portfolio_monitoring/valuation.py app/services/portfolio_monitoring/read_model.py`, and `git diff --check`.
- [x] Commit as `포트폴리오 공통 가치곡선과 KPI 구현`.

**2차 완료 게이트:** direct stock/ETF and selected-strategy lanes produce one versioned workspace projection; all lifecycle and metric tests pass. This stage still keeps the legacy visible UI.

---

## 3차 — React Portfolio Command Center

### Task 8: Python component bridge와 React package skeleton을 만든다

**Files:**

- Create: `app/web/portfolio_monitoring_react_component.py`
- Create: `app/web/streamlit_components/portfolio_monitoring_workbench/package.json`
- Create: `app/web/streamlit_components/portfolio_monitoring_workbench/package-lock.json`
- Create: `app/web/streamlit_components/portfolio_monitoring_workbench/tsconfig.json`
- Create: `app/web/streamlit_components/portfolio_monitoring_workbench/vite.config.ts`
- Create: `app/web/streamlit_components/portfolio_monitoring_workbench/index.html`
- Create: `app/web/streamlit_components/portfolio_monitoring_workbench/src/main.tsx`
- Create: `app/web/streamlit_components/portfolio_monitoring_workbench/src/contracts.ts`
- Create: `tests/test_portfolio_monitoring_component.py`

**Interfaces:**

- `portfolio_monitoring_react_component_available(build_dir=None)`
- `render_portfolio_monitoring_workbench(payload, key="portfolio_monitoring_workbench") -> dict | None`
- client return: `{ event: PortfolioMonitoringEvent | null }`

**Minimal implementation shape:**

```python
value = component(payload=_json_safe_payload(payload), key=key, default={"event": None})
return value if isinstance(value, dict) else None
```

- [x] Write failing Python tests for build availability, JSON-safe Decimal/date/pandas/non-finite serialization, stable component name, and missing-build `None` behavior.
- [x] Run `./.venv/bin/python -m unittest tests.test_portfolio_monitoring_component` and confirm import failure.
- [x] Implement the adapter using the established Institutional Portfolios `_json_safe_payload` pattern and scaffold the Vite package with relative asset paths and `component_static` output.
- [x] Add TypeScript contract types mirroring the Python workspace and event envelope; run `npm install` only inside this new package to generate the lockfile.
- [x] Run `./.venv/bin/python -m unittest tests.test_portfolio_monitoring_component`, then `cd app/web/streamlit_components/portfolio_monitoring_workbench && npm run typecheck && npm run build`; return to repo root and run `git diff --check`.
- [x] Commit as `포트폴리오 모니터링 React 브리지 추가` including tracked `component_static` output, excluding `node_modules`.

### Task 9: group rail, command band, KPI, chart, item detail shell을 구현한다

**Files:**

- Create: `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.ts`
- Create: `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.test.ts`
- Create: `app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx`
- Create: `app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/main.tsx`

**Interfaces:**

- `selectActiveGroup`, `selectItem`, `buildGroupChartSeries`, `formatMetric`
- UI event types: `create_group`, `rename_group`, `select_group`, `select_item`

**Minimal implementation shape:**

```tsx
<PortfolioMonitoringWorkbench workspace={payload} onEvent={Streamlit.setComponentValue} />
```

- [ ] Write failing Vitest cases for default/selected group resolution, ended item retention, common-basis banner, chart series gaps, and Korean short-window CAGR label.
- [ ] Run `npm test -- --run` in the component directory and confirm failures.
- [ ] Implement Portfolio-first shell order: group rail -> command band -> KPI strip -> full-width value chart -> item/contribution list -> selected detail -> method/boundary.
- [ ] Match Overview/Market Context color, spacing, evidence hierarchy, focus ring, and 1440/760/420 responsive layout; keep raw audit tables out of first read.
- [ ] Run `npm test -- --run`, `npm run typecheck`, `npm run build`, and `git diff --check`.
- [ ] Commit as `포트폴리오 모니터링 Command Center 셸 구현`.

### Task 10: Context Drawer와 command lifecycle을 구현한다

**Files:**

- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/contracts.ts`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.ts`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.test.ts`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css`

**Interfaces:**

- three-step draft: `source -> start/funding -> review`
- events: `search_catalog`, `add_item`, `end_item`
- command state: `idle | pending | success | error`

**Minimal implementation shape:**

```ts
emit({ type: "add_item", command_id: draft.commandId, payload: buildAddItemPayload(draft) });
```

- [ ] Write failing tests for direct/strategy switch, amount/share mode visibility, integer-share client validation, selected-strategy notional-only behavior, missing-price disabled review, duplicate/max-10 disabled state, and mobile full-width sheet state.
- [ ] Run `cd app/web/streamlit_components/portfolio_monitoring_workbench && npm test -- --run` and confirm failure.
- [ ] Implement drawer with server-projected readiness/messages, requested/effective date display, `10/10` capacity, confirmation for tracking end, keyboard close/focus return, and one emitted event per submit.
- [ ] Ensure client command IDs remain stable across Streamlit rerun retry until a server result is received.
- [ ] Run `npm test -- --run`, `npm run typecheck`, `npm run build`, and `git diff --check`.
- [ ] Commit as `포트폴리오 종목 등록 드로어 구현`.

### Task 11: Streamlit page를 thin event bridge로 cut over하고 Operations summary를 맞춘다

**Files:**

- Modify: `app/web/final_selected_portfolio_dashboard.py`
- Modify: `app/web/operations_overview.py`
- Modify: `app/web/streamlit_app.py`
- Modify: `tests/test_portfolio_monitoring_component.py`
- Create: `tests/test_portfolio_monitoring_page.py`
- Modify: `tests/test_component_static_distribution.py`

**Interfaces:**

- `render_final_selected_portfolio_dashboard_page()` remains public route entry
- `_dispatch_portfolio_monitoring_event(event, services) -> CommandResult`
- fallback model: active group summary + build/recovery guidance only

**Minimal implementation shape:**

```python
event = render_portfolio_monitoring_workbench(workspace)
if event and event.get("event"):
    _dispatch_portfolio_monitoring_event(event["event"], services)
```

- [ ] Write failing page-source/behavior tests proving the route calls one read-model builder, mounts one React component, dispatches one server command, and reruns after a mutating success. Assert the full legacy dashboard renderer is not invoked as fallback.
- [ ] Add static distribution tests for the new component assets and Operations summary tests using new group/item metrics while preserving page target navigation.
- [ ] Run `./.venv/bin/python -m pytest tests/test_portfolio_monitoring_component.py tests/test_portfolio_monitoring_page.py tests/test_component_static_distribution.py -q` and confirm failures.
- [ ] Replace the page body with load -> render -> dispatch -> rerun. Keep legacy helpers callable for compatibility tests but remove them from the normal render path. Missing component shows read-only active summary and recovery instructions only.
- [ ] Build assets, start the local app, and perform Browser QA at 1440px, 760px, and 420px for group switching, rename, direct item draft, strategy draft, and item detail. Save one screenshot path in `RUNS.md` without staging it.
- [ ] Run `./.venv/bin/python -m pytest tests/test_portfolio_monitoring_component.py tests/test_portfolio_monitoring_page.py tests/test_component_static_distribution.py -q`, then `cd app/web/streamlit_components/portfolio_monitoring_workbench && npm test -- --run && npm run typecheck && npm run build`; return to repo root, run `git diff --check`, and commit as `포트폴리오 모니터링 React 화면 전환`.

**3차 완료 게이트:** the visible Portfolio Monitoring product is React one-shell; create/rename/add/end events round-trip through Python; fallback is read-only; browser layouts pass. Strength/weakness and macro sections remain explicit “coming in next stage” slots, not fabricated signals.

---

## 4차 — Strength And Weakness Diagnosis

### Task 12: portfolio exposure를 normalized facts로 투영한다

**Files:**

- Create: `app/services/portfolio_monitoring/exposure.py`
- Create: `tests/test_portfolio_monitoring_exposure.py`

**Interfaces:**

- `build_direct_stock_exposure(item, asset_profile)`
- `build_etf_exposure(item, holdings_snapshot, exposure_snapshot)`
- `build_selected_strategy_exposure(item, target_snapshot)`
- `aggregate_group_exposure(items) -> ExposureResult`

**Minimal implementation shape:**

```python
coverage_ratio = covered_weight / total_weight if total_weight else 0.0
return ExposureResult(buckets=buckets, coverage_ratio=coverage_ratio, uncovered_weight=uncovered_weight)
```

- [ ] Write failing tests for direct sector/industry, ETF look-through priority, ETF top-level fallback, strategy target weights, overlapping-symbol aggregation, and weights that do not sum to 100%.
- [ ] Assert missing look-through lowers coverage and never invents sector/asset weights.
- [ ] Run `./.venv/bin/python -m pytest tests/test_portfolio_monitoring_exposure.py -q` and confirm failure.
- [ ] Implement source-dated facts with `covered_weight`, `uncovered_weight`, `coverage_ratio`, and provenance on every exposure bucket.
- [ ] Run `./.venv/bin/python -m pytest tests/test_portfolio_monitoring_exposure.py -q`, `./.venv/bin/python -m py_compile app/services/portfolio_monitoring/exposure.py`, and `git diff --check`.
- [ ] Commit as `포트폴리오 노출 정규화 구현`.

### Task 13: behavior facts와 versioned deterministic policy를 구현한다

**Files:**

- Create: `app/services/portfolio_monitoring/diagnosis.py`
- Create: `tests/test_portfolio_monitoring_diagnosis.py`

**Interfaces:**

- `DIAGNOSIS_POLICY_VERSION = "portfolio_monitoring_policy_v1"`
- `build_behavior_facts(group, lanes) -> BehaviorFacts`
- `evaluate_portfolio_rules(exposure, behavior, overrides=None) -> list[DiagnosisFact]`

**Minimal implementation shape:**

```python
threshold = overrides.get(rule_id, DEFAULT_POLICIES[rule_id]) if overrides else DEFAULT_POLICIES[rule_id]
return _evaluate_rule(rule_id, measured_value, threshold)
```

- [ ] Write failing fact tests for 21/63/126-session return, 50D/200D distance, consecutive-below-200D sessions, drawdown/MDD, volatility, 63D pairwise correlation cluster, total contribution, and downside contribution.
- [ ] Write boundary tests for every approved watch/high threshold, including equality behavior and a Final Review stored threshold override with provenance.
- [ ] Run `./.venv/bin/python -m pytest tests/test_portfolio_monitoring_diagnosis.py -q` and confirm failure.
- [ ] Implement pure calculation and policy catalog. Keep thresholds in Python constants/config objects, never React.
- [ ] Run `./.venv/bin/python -m pytest tests/test_portfolio_monitoring_diagnosis.py -q`, `./.venv/bin/python -m py_compile app/services/portfolio_monitoring/diagnosis.py`, and `git diff --check`.
- [ ] Commit as `포트폴리오 강점 취약점 판정 정책 구현`.

### Task 14: diagnosis priority/dedup/confidence와 React evidence UI를 연결한다

**Files:**

- Modify: `app/services/portfolio_monitoring/diagnosis.py`
- Modify: `app/services/portfolio_monitoring/read_model.py`
- Modify: `tests/test_portfolio_monitoring_diagnosis.py`
- Modify: `tests/test_portfolio_monitoring_read_model.py`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/contracts.ts`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.test.ts`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx`

**Interfaces:**

- `project_diagnoses(facts, coverage) -> DiagnosisProjection`
- row fields: `rule_id`, `policy_version`, `classification`, `severity`, `persistence`, `affected_weight`, `contribution`, `measured_fact`, `threshold`, `source_dates`, `coverage`, `confidence`, `meaning`, `change_condition`, `next_check`

**Minimal implementation shape:**

```python
top_three = [row for row in ranked_rows if row.confidence != "LOW"][:3]
return DiagnosisProjection(top_three=top_three, all_rows=ranked_rows)
```

- [ ] Write failing tests for same-root dedup, HIGH/MEDIUM/LOW coverage bands, LOW exclusion from top three, stable priority ordering, strength/weakness/data-gap separation, and a maximum of three first-read rows.
- [ ] Add React tests proving top-three render, full evidence disclosure, measured fact/threshold/change condition visibility, and no buy/sell or target-weight instruction text.
- [ ] Run `./.venv/bin/python -m pytest tests/test_portfolio_monitoring_diagnosis.py tests/test_portfolio_monitoring_read_model.py -q` and `cd app/web/streamlit_components/portfolio_monitoring_workbench && npm test -- --run`; confirm failure in both suites.
- [ ] Implement message templates and read-model projection; render “지금 확인할 변화”, “강점”, “취약점”, and “데이터 부족” as distinct evidence sections.
- [ ] Run `./.venv/bin/python -m pytest tests/test_portfolio_monitoring_exposure.py tests/test_portfolio_monitoring_diagnosis.py tests/test_portfolio_monitoring_read_model.py -q`, then `cd app/web/streamlit_components/portfolio_monitoring_workbench && npm test -- --run && npm run typecheck && npm run build`; return to repo root, capture the Browser QA screenshot, and run `git diff --check`.
- [ ] Commit as `포트폴리오 근거형 진단 화면 연결`.

**4차 완료 게이트:** exposure and behavior fixtures produce explainable strengths/weaknesses with measured facts, thresholds, coverage, confidence, and change conditions. No macro context changes severity yet.

---

## 5차 — Macro Risk Observation

### Task 15: persisted macro snapshots를 portfolio-safe compact context로 변환한다

**Files:**

- Create: `app/services/portfolio_monitoring/macro_context.py`
- Create: `tests/test_portfolio_monitoring_macro_context.py`

**Interfaces:**

- `load_portfolio_macro_context(*, cycle_loader, futures_loader, asset_context_loader, as_of_date=None)`
- `MacroContext(status, as_of_dates, publication, family_scores, pathways, coverage, warnings)`

**Minimal implementation shape:**

```python
return MacroContext(status=status, as_of_dates=source_dates, publication=publication, family_scores=scores, pathways=pathways, coverage=coverage, warnings=warnings)
```

- [ ] Write failing tests for economic cycle current/+1M/+2M extraction, Futures Macro risk-on/growth/rate/dollar/safe-haven/inflation scores, 5D/20D outlook, and gold/dollar/WTI/copper/rates/S&P pathways.
- [ ] Test missing, stale, LIMITED, PROVISIONAL, malformed snapshot, and mismatched as-of dates. Assert loaders are read-only and no calculation/materialization function is called.
- [ ] Run `./.venv/bin/python -m pytest tests/test_portfolio_monitoring_macro_context.py -q` and confirm failure.
- [ ] Implement adapters over `build_economic_cycle_read_model`, `load_overview_futures_macro_materialized_snapshot`, and existing Overview materialized asset context. Return source freshness and publication status explicitly.
- [ ] Run `./.venv/bin/python -m pytest tests/test_portfolio_monitoring_macro_context.py -q`, `./.venv/bin/python -m py_compile app/services/portfolio_monitoring/macro_context.py`, and `git diff --check`.
- [ ] Commit as `포트폴리오 매크로 컨텍스트 어댑터 구현`.

### Task 16: exposure-context match와 confidence/severity cap을 구현한다

**Files:**

- Modify: `app/services/portfolio_monitoring/macro_context.py`
- Modify: `app/services/portfolio_monitoring/diagnosis.py`
- Modify: `tests/test_portfolio_monitoring_macro_context.py`
- Modify: `tests/test_portfolio_monitoring_diagnosis.py`

**Interfaces:**

- `evaluate_macro_observations(exposure, behavior, macro) -> list[MacroObservation]`
- observation state: `low | medium | high`
- `apply_macro_confidence_cap(observation) -> MacroObservation`

**Minimal implementation shape:**

```python
if observation.publication in {"LIMITED", "PROVISIONAL"} and observation.severity == "HIGH":
    return replace(observation, severity="MEDIUM")
```

- [ ] Write failing fixtures for tech+risk-off/NQ weakness, gold+63D weakness+real-yield adversity, duration+rate pressure, and cyclical+activity weakening+growth weakness.
- [ ] Assert exposure trigger absence yields no alert, LIMITED/PROVISIONAL cannot alone create HIGH severity, LOW confidence stays out of top three, and outputs never contain loss probability.
- [ ] Run `./.venv/bin/python -m pytest tests/test_portfolio_monitoring_macro_context.py tests/test_portfolio_monitoring_diagnosis.py -q` and confirm failure.
- [ ] Implement rule IDs, source dates, matched conditions, affected weight, coverage/confidence, current observation, and change condition; deduplicate against portfolio-only rows sharing the same root exposure.
- [ ] Run `./.venv/bin/python -m pytest tests/test_portfolio_monitoring_macro_context.py tests/test_portfolio_monitoring_diagnosis.py -q`, `./.venv/bin/python -m py_compile app/services/portfolio_monitoring/macro_context.py app/services/portfolio_monitoring/diagnosis.py`, and `git diff --check`.
- [ ] Commit as `포트폴리오 매크로 위험 관찰 규칙 구현`.

### Task 17: Macro Risk Observation UI와 Operations handoff를 닫는다

**Files:**

- Modify: `app/services/portfolio_monitoring/read_model.py`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/contracts.ts`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.test.ts`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css`
- Modify: `app/web/operations_overview.py`
- Modify: `tests/test_portfolio_monitoring_page.py`

**Interfaces:**

- workspace keys: `macro_observation`, `now_to_review`, `source_health`
- Operations summary reads active group status, basis date, top review count, and macro coverage without showing run/job diagnostics as the primary value.

**Minimal implementation shape:**

```tsx
<MacroObservationSection observation={workspace.macro_observation} sourceHealth={workspace.source_health} />
```

- [ ] Write failing Python/React tests for low/medium/high observation cards, READY/LIMITED source chips, change-condition disclosure, stale warning, and probability copy absence.
- [ ] Run `./.venv/bin/python -m pytest tests/test_portfolio_monitoring_page.py tests/test_portfolio_monitoring_read_model.py tests/test_portfolio_monitoring_macro_context.py -q` and `cd app/web/streamlit_components/portfolio_monitoring_workbench && npm test -- --run`; confirm failure in both suites.
- [ ] Render the macro section below strengths/weaknesses and before item list; keep coverage/freshness visible but subordinate to portfolio meaning and next check.
- [ ] Update Operations Overview’s Portfolio Monitoring summary to link into the active group workflow and preserve existing System/Data Health boundary.
- [ ] Run `./.venv/bin/python -m pytest tests/test_portfolio_monitoring_macro_context.py tests/test_portfolio_monitoring_diagnosis.py tests/test_portfolio_monitoring_read_model.py tests/test_portfolio_monitoring_page.py -q`, then `cd app/web/streamlit_components/portfolio_monitoring_workbench && npm test -- --run && npm run typecheck && npm run build`; return to repo root, capture desktop/mobile Browser QA, and run `git diff --check`.
- [ ] Commit as `포트폴리오 매크로 위험 관찰 화면 연결`.

**5차 완료 게이트:** current macro observations are evidence-backed and confidence-capped; the UI shows no uncalibrated probability or action instruction.

---

## 6차 — Calibration And Operational History

### Task 18: diagnosis snapshot과 calibration artifact persistence를 추가한다

**Files:**

- Modify: `finance/data/db/schema.py`
- Modify: `app/services/portfolio_monitoring/schemas.py`
- Create: `app/services/portfolio_monitoring/history.py`
- Create: `tests/test_portfolio_monitoring_history.py`

**Interfaces:**

- new schema rows: `monitoring_diagnosis_snapshot`, `monitoring_risk_calibration_artifact`
- `capture_diagnosis_snapshot(group_id, as_of_date, workspace, repository)`
- `load_diagnosis_history(group_id, start_date, end_date)`
- unique identity: `(portfolio_group_id, as_of_date, config_fingerprint, policy_version)`

**Minimal implementation shape:**

```python
identity = (group_id, as_of_date, workspace["config_fingerprint"], workspace["diagnosis"]["policy_version"])
repository.insert_snapshot_if_absent(identity, compact_snapshot)
```

- [ ] Write failing schema/history tests for immutable as-of inputs, config fingerprint, policy/macro versions, source dates, observations, subsequent 21/63-session outcomes, and idempotent recapture.
- [ ] Run `./.venv/bin/python -m pytest tests/test_portfolio_monitoring_history.py -q` and confirm failure.
- [ ] Add append/idempotent snapshot persistence without copying raw price/macro series into JSON. Store compact feature/evidence/outcome identity only.
- [ ] Implement read APIs with publication-time fields needed to reject look-ahead rows.
- [ ] Run `./.venv/bin/python -m pytest tests/test_portfolio_monitoring_history.py -q`, `./.venv/bin/python -m py_compile app/services/portfolio_monitoring/history.py`, and `git diff --check`.
- [ ] Commit as `포트폴리오 진단 이력 저장 계약 추가`.

### Task 19: historical as-of replay와 probability publication gate를 구현한다

**Files:**

- Create: `app/services/portfolio_monitoring/calibration.py`
- Create: `tests/test_portfolio_monitoring_calibration.py`

**Interfaces:**

- `build_historical_replay(samples, *, split_dates, embargo_sessions) -> ReplayResult`
- `calibrate_risk_probability(train_rows, validation_rows) -> CalibrationArtifact`
- `evaluate_publication_gate(artifact) -> PublicationDecision`
- gate status: `SUPPRESSED | LIMITED | READY`

**Minimal implementation shape:**

```python
if eligible_count < 250 or positive_count < 50 or brier > baseline_brier * 0.95:
    return PublicationDecision(status="SUPPRESSED", reasons=reasons)
```

- [ ] Write failing tests that reject future-revised macro vintages, non-PIT exposures, overlapping train/validation horizons, and insufficient samples.
- [ ] Add tests for time-ordered OOS split, embargo, naive unconditional baseline, Brier score, reliability buckets, confidence intervals, and reproducible algorithm/data fingerprints.
- [ ] Define and test the publication gate: at least 250 eligible observations, at least 50 positive outcomes, OOS Brier score at least 5% better than the naive baseline, maximum reliability-bin absolute error `<= 0.10`, and no publication-integrity blocker. Otherwise status is SUPPRESSED/LIMITED.
- [ ] Run `./.venv/bin/python -m pytest tests/test_portfolio_monitoring_calibration.py -q` and confirm failure.
- [ ] Implement the minimal deterministic calibrator and gate. Probability output is inaccessible unless status is `READY`; observation rows remain available.
- [ ] Run `./.venv/bin/python -m pytest tests/test_portfolio_monitoring_calibration.py -q`, `./.venv/bin/python -m py_compile app/services/portfolio_monitoring/calibration.py`, and `git diff --check`.
- [ ] Commit as `포트폴리오 위험 확률 검증 게이트 구현`.

### Task 20: qualified probability와 diagnosis history UI를 조건부로 노출한다

**Files:**

- Modify: `app/services/portfolio_monitoring/read_model.py`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/contracts.ts`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.test.ts`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css`
- Modify: `tests/test_portfolio_monitoring_read_model.py`

**Interfaces:**

- `risk_calibration.publication_status`
- READY-only fields: `probability`, `horizon_sessions`, `event_definition`, `sample_size`, `brier_score`, `baseline_brier`, `limitations`
- history rows: `as_of_date`, `observation_state`, `severity`, `confidence`, `resolved_at`, `outcome`

**Minimal implementation shape:**

```python
probability = artifact.probability if artifact.publication_status == "READY" else None
return {"publication_status": artifact.publication_status, "probability": probability}
```

- [ ] Write failing tests proving SUPPRESSED/LIMITED projections omit probability entirely, READY includes all qualification metadata, and stale artifacts are suppressed when policy/data fingerprints differ.
- [ ] Write React tests for observation-only fallback, qualified probability label, sample/score/limitation disclosure, and history persistence/cooldown timeline.
- [ ] Run `./.venv/bin/python -m pytest tests/test_portfolio_monitoring_read_model.py tests/test_portfolio_monitoring_calibration.py -q` and `cd app/web/streamlit_components/portfolio_monitoring_workbench && npm test -- --run`; confirm failure in both suites.
- [ ] Implement conditional read-model and disclosure UI; never phrase probability as expected return or buy/sell advice.
- [ ] Run `./.venv/bin/python -m pytest tests/test_portfolio_monitoring_read_model.py tests/test_portfolio_monitoring_history.py tests/test_portfolio_monitoring_calibration.py -q`, then `cd app/web/streamlit_components/portfolio_monitoring_workbench && npm test -- --run && npm run typecheck && npm run build`; return to repo root, capture the Browser QA screenshot, and run `git diff --check`.
- [ ] Commit as `검증된 위험 확률과 진단 이력 화면 연결`.

### Task 21: full regression, durable docs sync, migration/runbook closeout을 수행한다

**Files:**

- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Create: `.aiworkspace/note/finance/docs/architecture/PORTFOLIO_MONITORING_REACT_COMMAND_CENTER.md`
- Create: `.aiworkspace/note/finance/docs/data/PORTFOLIO_MONITORING_DATA_CONTRACT.md`
- Create: `.aiworkspace/note/finance/docs/runbooks/PORTFOLIO_MONITORING_MIGRATION_AND_QA.md`
- Modify: `.aiworkspace/note/finance/tasks/active/portfolio-monitoring-react-command-center-v1-20260719/{STATUS.md,RUNS.md,RISKS.md}`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Create: `tests/test_portfolio_monitoring_docs.py`

**Interfaces:** documentation must describe route ownership, DB tables, legacy import/cutover, valuation semantics, diagnosis policy/version, macro confidence, calibration gate, rollback/fallback, and no-live-trading boundary.

**Minimal implementation shape:**

```python
def test_portfolio_monitoring_docs_name_canonical_owners_and_boundaries() -> None:
    assert "portfolio_monitoring_workspace_v1" in architecture_doc
    assert "broker order" in data_contract
```

- [ ] Before editing durable docs, use `finance-doc-sync` and `finance-runbook-maintainer`; write `tests/test_portfolio_monitoring_docs.py` for every required ownership/boundary phrase.
- [ ] Run `./.venv/bin/python -m pytest tests/test_portfolio_monitoring_docs.py -q` and confirm failure because the durable documents do not exist yet.
- [ ] Run the complete focused Python suite:

```bash
./.venv/bin/python -m pytest \
  tests/test_portfolio_monitoring_schema.py \
  tests/test_portfolio_monitoring_commands.py \
  tests/test_portfolio_monitoring_legacy_import.py \
  tests/test_portfolio_monitoring_catalog.py \
  tests/test_portfolio_monitoring_valuation.py \
  tests/test_portfolio_monitoring_selected_strategy.py \
  tests/test_portfolio_monitoring_read_model.py \
  tests/test_portfolio_monitoring_component.py \
  tests/test_portfolio_monitoring_page.py \
  tests/test_portfolio_monitoring_exposure.py \
  tests/test_portfolio_monitoring_diagnosis.py \
  tests/test_portfolio_monitoring_macro_context.py \
  tests/test_portfolio_monitoring_history.py \
  tests/test_portfolio_monitoring_calibration.py \
  tests/test_portfolio_monitoring_docs.py -q
```

- [ ] Run component `npm test -- --run`, `npm run typecheck`, `npm run build`; then run relevant existing regression tests for Final Review handoff, Operations route, economic cycle, Futures Macro snapshot, and component static distribution.
- [ ] Execute the migration runbook against a safe test DB first, verify legacy dry-run/apply counts and checksum preservation, then perform final Browser QA for one direct stock, one ETF, one selected strategy, staggered start, tracking end to cash, stale common basis, diagnosis, macro observation, and probability suppression/qualification fixture.
- [ ] Update durable docs and concise root handoff logs. Use `superpowers:verification-before-completion` for final evidence review; run `git status --short`, `git diff --check`, and verify screenshots/generated artifacts are not staged.
- [ ] Commit as `포트폴리오 모니터링 React 전면 개편 문서화` and move the task/research records to their done location only after all six stage gates pass.

**6차 완료 게이트:** probability is suppressed unless the explicit OOS publication gate passes; history is reproducible and PIT-safe; migration/rollback and Browser QA are documented; durable docs match production ownership.

---

## End-to-End Acceptance Checklist

- [ ] 첫 진입에서 default group exactly one이 보인다.
- [ ] group 생성·선택·rename이 idempotent command로 동작한다.
- [ ] direct U.S. stock/ETF와 `monitoring_candidate=True` selected strategy를 검색·추가할 수 있다.
- [ ] fixed notional과 direct-security integer shares가 정확히 분리된다.
- [ ] missing price, duplicate, max 10, invalid shares가 write 전에 차단된다.
- [ ] staggered start, pre-start cash, dividend cash, split, tracking-end cash가 group curve와 KPI에 반영된다.
- [ ] invested/current/P&L/return/MDD/CAGR/contribution/downside contribution이 common basis date로 표시된다.
- [ ] group chart 아래에서 각 item/strategy result와 근거를 선택해 본다.
- [ ] strengths/weaknesses/top-three rows가 measured fact, threshold, coverage, confidence, change condition을 포함한다.
- [ ] macro signal은 exposure-context observation이며 calibration 전 loss probability를 표시하지 않는다.
- [ ] calibration gate 통과 전 probability는 payload와 UI에서 모두 제거된다.
- [ ] legacy saved JSONL과 Final Review registry가 byte-for-byte 보존된다.
- [ ] React missing/error fallback은 read-only이며 legacy mutation UI를 다시 열지 않는다.
- [ ] 1440px, 760px, 420px Browser QA와 keyboard/focus/overflow 검증이 통과한다.
- [ ] Operations Console은 실제 monitoring workflow로 연결되며 run/job/row 진단을 주인공으로 만들지 않는다.

## Execution Boundary

- 전체 구현 완료 기준은 `6/6차`다.
- 각 차수는 독립적으로 검증·커밋할 수 있지만, 이전 차수 gate가 통과해야 다음 차수로 진행한다.
- 3차까지 완료하면 React 기반 핵심 tracking product를 사용할 수 있다.
- 4차와 5차는 deterministic diagnosis와 macro observation을 추가한다.
- 6차 probability는 연구 결과가 gate를 통과할 때만 공개하며, gate 실패는 구현 실패가 아니라 정상적인 suppression 결과다.
