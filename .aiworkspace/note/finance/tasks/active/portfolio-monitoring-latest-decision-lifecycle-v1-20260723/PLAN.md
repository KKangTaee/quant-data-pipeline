# Portfolio Monitoring Latest Decision Lifecycle V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 후보별 최신 Final Review 판단만 Portfolio Monitoring의 현재 전략 자격으로 인정하고, 판단이 바뀐 기존 항목은 삭제하지 않은 채 실행 잠금과 재확인/종료 행동을 제공한다.

**Architecture:** 새 Streamlit-free lifecycle service가 append-only Final Review row를 canonical subject로 묶고 최신 row를 결정한다. Catalog, Selected Strategy replay adapter, Monitoring read model이 같은 projection을 재사용하고 React는 Python이 전달한 잠금 상태와 행동만 표시한다.

**Tech Stack:** Python 3.12, dataclass, Streamlit, React 18, TypeScript 5.7, Vitest, pytest, append-only JSONL registry, existing MySQL Portfolio Monitoring repository.

## Global Constraints

- `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl` row를 삭제하거나 재작성하지 않는다.
- `selection_source_id -> source_type/source_id -> decision_id` 순서로 subject identity를 만든다.
- 최신 non-select 판단은 기존 Monitoring item만 잠그며 다른 정상 item의 계산은 계속한다.
- Portfolio Monitoring에서 Final Review 판단을 override하거나 waiver를 저장하지 않는다.
- 계속 추적하려면 Final Review가 새 `SELECT_FOR_PRACTICAL_PORTFOLIO` 판단을 기록해야 한다.
- 추적 종료는 기존 idempotent `end_item` command를 재사용한다.
- 사용자 registry, saved setup, run history, generated QA artifact를 stage하지 않는다.
- broker order, account sync, live approval, auto rebalance를 추가하지 않는다.

---

### Task 1: 최신 Final Review 판단 lifecycle service

**Files:**
- Create: `app/services/portfolio_monitoring/decision_lifecycle.py`
- Modify: `app/services/portfolio_monitoring/__init__.py`
- Create: `tests/test_portfolio_monitoring_decision_lifecycle.py`

**Interfaces:**
- Consumes: append-only `Iterable[Mapping[str, Any]]` Final Review rows.
- Produces: `decision_subject_key(row) -> str`, `latest_final_decision_rows(rows) -> list[dict[str, Any]]`, `resolve_monitoring_decision(rows, requested_decision_id) -> MonitoringDecisionLifecycle`.
- `MonitoringDecisionLifecycle.to_projection()`은 catalog/replay/read model/React가 공유할 JSON-safe 상태를 반환한다.

- [ ] **Step 1: subject identity와 최신 row 결정을 고정하는 실패 테스트 작성**

```python
from app.services.portfolio_monitoring.decision_lifecycle import (
    decision_subject_key,
    latest_final_decision_rows,
    resolve_monitoring_decision,
)


def _row(decision_id: str, *, updated_at: str, route: str, selected: bool, selection_source_id: str = "selection-a"):
    return {
        "decision_id": decision_id,
        "updated_at": updated_at,
        "decision_route": route,
        "monitoring_candidate": selected,
        "source_type": "practical_validation_result",
        "source_id": f"validation-{decision_id}",
        "selection_source_id": selection_source_id,
    }


def test_latest_non_select_supersedes_old_selected_without_deleting_history():
    rows = [
        _row("old-selected", updated_at="2026-07-22T10:00:00", route="SELECT_FOR_PRACTICAL_PORTFOLIO", selected=True),
        _row("new-hold", updated_at="2026-07-23T10:00:00", route="HOLD_FOR_MORE_PAPER_TRACKING", selected=False),
    ]
    lifecycle = resolve_monitoring_decision(rows, "old-selected")
    assert lifecycle.state == "TRACKING_ELIGIBILITY_CHANGED"
    assert lifecycle.locked is True
    assert lifecycle.effective_decision_id == "new-hold"
    assert lifecycle.requested_row["decision_id"] == "old-selected"
    assert lifecycle.effective_row["decision_id"] == "new-hold"


def test_new_selected_decision_reactivates_existing_subject():
    rows = [
        _row("old-selected", updated_at="2026-07-21T10:00:00", route="SELECT_FOR_PRACTICAL_PORTFOLIO", selected=True),
        _row("hold", updated_at="2026-07-22T10:00:00", route="HOLD_FOR_MORE_PAPER_TRACKING", selected=False),
        _row("new-selected", updated_at="2026-07-23T10:00:00", route="SELECT_FOR_PRACTICAL_PORTFOLIO", selected=True),
    ]
    lifecycle = resolve_monitoring_decision(rows, "old-selected")
    assert lifecycle.state == "SUPERSEDED_SELECTED"
    assert lifecycle.locked is False
    assert lifecycle.effective_decision_id == "new-selected"


def test_identity_falls_back_without_collapsing_unrelated_legacy_rows():
    assert decision_subject_key({"decision_id": "a", "source_type": "validation", "source_id": "same"}) == "source:validation:same"
    assert decision_subject_key({"decision_id": "b"}) == "decision:b"
```

- [ ] **Step 2: 실패 상태 확인**

Run: `.venv/bin/python -m pytest tests/test_portfolio_monitoring_decision_lifecycle.py -q`

Expected: FAIL with `ModuleNotFoundError: app.services.portfolio_monitoring.decision_lifecycle`.

- [ ] **Step 3: 최소 lifecycle service 구현**

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class MonitoringDecisionLifecycle:
    state: str
    locked: bool
    subject_key: str
    requested_decision_id: str
    effective_decision_id: str | None
    latest_route: str | None
    latest_route_label: str
    latest_source_id: str | None
    message: str
    requested_row: dict[str, Any] | None
    effective_row: dict[str, Any] | None

    def to_projection(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "locked": self.locked,
            "subject_key": self.subject_key,
            "requested_decision_id": self.requested_decision_id,
            "effective_decision_id": self.effective_decision_id,
            "latest_route": self.latest_route,
            "latest_route_label": self.latest_route_label,
            "latest_source_id": self.latest_source_id,
            "message": self.message,
        }


def decision_subject_key(row: Mapping[str, Any]) -> str:
    selection_source_id = str(row.get("selection_source_id") or "").strip()
    if selection_source_id:
        return f"selection:{selection_source_id}"
    source_type = str(row.get("source_type") or "").strip()
    source_id = str(row.get("source_id") or "").strip()
    if source_type and source_id:
        return f"source:{source_type}:{source_id}"
    return f"decision:{str(row.get('decision_id') or '').strip()}"


ROUTE_LABELS = {
    "SELECT_FOR_PRACTICAL_PORTFOLIO": "계속 추적",
    "HOLD_FOR_MORE_PAPER_TRACKING": "관찰 후 재검토",
    "REJECT_FOR_PRACTICAL_USE": "추적 대상에서 제외",
    "RE_REVIEW_REQUIRED": "Level2로 돌려보내기",
}


def _decision_order(row: Mapping[str, Any]) -> tuple[str, str, str]:
    return (
        str(row.get("updated_at") or ""),
        str(row.get("created_at") or ""),
        str(row.get("decision_id") or ""),
    )


def latest_final_decision_rows(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for source in rows:
        row = dict(source or {})
        key = decision_subject_key(row)
        if key not in latest or _decision_order(row) > _decision_order(latest[key]):
            latest[key] = row
    return sorted(latest.values(), key=_decision_order, reverse=True)


def resolve_monitoring_decision(
    rows: Iterable[Mapping[str, Any]],
    requested_decision_id: str,
) -> MonitoringDecisionLifecycle:
    normalized = [dict(row or {}) for row in rows]
    clean_id = str(requested_decision_id or "").strip()
    requested = next(
        (row for row in normalized if str(row.get("decision_id") or "").strip() == clean_id),
        None,
    )
    if requested is None:
        return MonitoringDecisionLifecycle(
            state="DECISION_NOT_FOUND",
            locked=True,
            subject_key=f"decision:{clean_id}",
            requested_decision_id=clean_id,
            effective_decision_id=None,
            latest_route=None,
            latest_route_label="판단 기록 없음",
            latest_source_id=None,
            message="Final Review 판단 기록을 찾을 수 없습니다.",
            requested_row=None,
            effective_row=None,
        )
    subject_key = decision_subject_key(requested)
    subject_rows = [row for row in normalized if decision_subject_key(row) == subject_key]
    effective = max(subject_rows, key=_decision_order)
    effective_id = str(effective.get("decision_id") or "").strip()
    route = str(effective.get("decision_route") or "").strip()
    selected = effective.get("monitoring_candidate") is True
    if not selected:
        state = "TRACKING_ELIGIBILITY_CHANGED"
        message = f"최신 Final Review 판단이 {ROUTE_LABELS.get(route, route or '선택 해제')}로 변경되어 새 계산을 잠갔습니다."
    elif effective_id == clean_id:
        state = "CURRENT_SELECTED"
        message = "현재 Final Review 계속 추적 판단과 일치합니다."
    else:
        state = "SUPERSEDED_SELECTED"
        message = "더 최신의 계속 추적 판단을 적용합니다."
    return MonitoringDecisionLifecycle(
        state=state,
        locked=not selected,
        subject_key=subject_key,
        requested_decision_id=clean_id,
        effective_decision_id=effective_id,
        latest_route=route or None,
        latest_route_label=ROUTE_LABELS.get(route, route or "판단 미지정"),
        latest_source_id=str(effective.get("source_id") or "").strip() or None,
        message=message,
        requested_row=requested,
        effective_row=effective,
    )
```

- [ ] **Step 4: service 테스트와 compile 통과 확인**

Run:

```bash
.venv/bin/python -m pytest tests/test_portfolio_monitoring_decision_lifecycle.py -q
.venv/bin/python -m py_compile app/services/portfolio_monitoring/decision_lifecycle.py app/services/portfolio_monitoring/__init__.py
```

Expected: tests PASS and compile exits 0.

- [ ] **Step 5: Task 1 커밋**

```bash
git add app/services/portfolio_monitoring/decision_lifecycle.py app/services/portfolio_monitoring/__init__.py tests/test_portfolio_monitoring_decision_lifecycle.py
git commit -m "기능: Monitoring 최신 판단 계약 추가"
```

---

### Task 2: 신규 catalog와 기존 selected-strategy replay 연결

**Files:**
- Modify: `app/services/portfolio_monitoring/catalog.py:147-196`
- Modify: `app/services/portfolio_monitoring/selected_strategy.py:31-140`
- Modify: `tests/test_portfolio_monitoring_catalog.py:118-181`
- Modify: `tests/test_portfolio_monitoring_selected_strategy.py:20-126`

**Interfaces:**
- Consumes: Task 1의 `latest_final_decision_rows`, `resolve_monitoring_decision`.
- Produces: 신규 catalog에는 subject별 latest selected row만 존재하고, adapter는 기존 decision ID를 latest effective row로 해석한다.
- `SelectedStrategyReadiness.decision_lifecycle`은 Task 3 read model이 소비한다.

- [ ] **Step 1: catalog가 과거 selected를 숨기는 실패 테스트 작성**

```python
def test_catalog_uses_only_latest_decision_per_selection_source(self) -> None:
    rows = catalog.list_monitoring_candidates(decision_loader=lambda: [
        {"decision_id": "latest-hold", "selection_source_id": "selection-a", "updated_at": "2026-07-23T10:00:00", "decision_route": "HOLD_FOR_MORE_PAPER_TRACKING", "monitoring_candidate": False},
        {"decision_id": "old-selected", "selection_source_id": "selection-a", "updated_at": "2026-07-22T10:00:00", "decision_route": "SELECT_FOR_PRACTICAL_PORTFOLIO", "monitoring_candidate": True},
    ])
    self.assertEqual(rows, [])
```

- [ ] **Step 2: adapter 잠금·재활성화 실패 테스트 작성**

```python
def test_newer_hold_locks_existing_selected_strategy(self) -> None:
    selected = _load_selected_strategy()
    adapter = selected.SelectedStrategyReplayAdapter(decision_loader=lambda: [
        {"decision_id": "new-hold", "selection_source_id": "selection-a", "updated_at": "2026-07-23", "decision_route": "HOLD_FOR_MORE_PAPER_TRACKING", "monitoring_candidate": False},
        {"decision_id": "old-selected", "selection_source_id": "selection-a", "updated_at": "2026-07-22", "decision_route": "SELECT_FOR_PRACTICAL_PORTFOLIO", "monitoring_candidate": True, "selected_components": [{"registry_id": "candidate-a", "target_weight": 100.0}]},
    ])
    contract = adapter.load_candidate_contract("old-selected")
    self.assertEqual(contract.readiness.status, "BLOCKED")
    self.assertEqual(contract.readiness.decision_lifecycle["state"], "TRACKING_ELIGIBILITY_CHANGED")
    self.assertEqual(contract.decision_row["decision_id"], "new-hold")


def test_newer_selected_row_reactivates_old_monitoring_reference(self) -> None:
    selected = _load_selected_strategy()
    adapter = selected.SelectedStrategyReplayAdapter(decision_loader=lambda: [
        {"decision_id": "new-selected", "selection_source_id": "selection-a", "updated_at": "2026-07-23", "decision_route": "SELECT_FOR_PRACTICAL_PORTFOLIO", "monitoring_candidate": True, "selected_components": [{"registry_id": "candidate-new", "target_weight": 100.0}]},
        {"decision_id": "old-selected", "selection_source_id": "selection-a", "updated_at": "2026-07-22", "decision_route": "SELECT_FOR_PRACTICAL_PORTFOLIO", "monitoring_candidate": True, "selected_components": [{"registry_id": "candidate-old", "target_weight": 100.0}]},
    ])
    contract = adapter.load_candidate_contract("old-selected")
    self.assertEqual(contract.readiness.status, "READY")
    self.assertEqual(contract.decision_row["decision_id"], "new-selected")
    self.assertEqual(contract.readiness.source_dates["effective_decision_id"], "new-selected")
```

- [ ] **Step 3: RED 확인**

Run: `.venv/bin/python -m pytest tests/test_portfolio_monitoring_catalog.py tests/test_portfolio_monitoring_selected_strategy.py -q`

Expected: old catalog row remains and adapter resolves the old row, so new assertions FAIL.

- [ ] **Step 4: catalog와 adapter에 공통 lifecycle 적용**

```python
# catalog.py
for source in latest_final_decision_rows(load()):
    row = dict(source or {})
    decision_id = str(row.get("decision_id") or "").strip()
    if row.get("monitoring_candidate") is not True or not decision_id:
        continue


# selected_strategy.py
@dataclass(frozen=True)
class SelectedStrategyReadiness:
    status: str
    blockers: tuple[str, ...]
    source_dates: dict[str, str | None]
    decision_lifecycle: dict[str, Any] = field(default_factory=dict)


rows = [dict(row) for row in self._decision_loader()]
lifecycle = resolve_monitoring_decision(rows, clean_id)
row = dict(lifecycle.effective_row or {})
projection = lifecycle.to_projection()
```

For a locked lifecycle return `BLOCKED` with `lifecycle.message`; for a selected lifecycle use the effective latest row. Carry the same projection and `requested_decision_id/effective_decision_id` into every READY/REVIEW/error readiness constructor.

- [ ] **Step 5: focused GREEN 확인**

Run: `.venv/bin/python -m pytest tests/test_portfolio_monitoring_decision_lifecycle.py tests/test_portfolio_monitoring_catalog.py tests/test_portfolio_monitoring_selected_strategy.py -q`

Expected: all focused tests PASS.

- [ ] **Step 6: Task 2 커밋**

```bash
git add app/services/portfolio_monitoring/catalog.py app/services/portfolio_monitoring/selected_strategy.py tests/test_portfolio_monitoring_catalog.py tests/test_portfolio_monitoring_selected_strategy.py
git commit -m "기능: Monitoring 전략을 최신 판단으로 해석"
```

---

### Task 3: item-local 실행 잠금과 재확인 UI 연결

**Files:**
- Modify: `app/services/portfolio_monitoring/read_model.py:309-488`
- Modify: `app/web/final_selected_portfolio_dashboard.py:339-381, 589-640, 4431-4475`
- Modify: `app/web/streamlit_app.py:20-32, 188-225`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/contracts.ts:79-108, 298-314`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.ts`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.test.ts`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx:650-705, 850-910`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css`
- Modify: `tests/test_portfolio_monitoring_read_model.py`
- Modify: `tests/test_portfolio_monitoring_page.py`
- Modify: `tests/test_portfolio_monitoring_component.py`

**Interfaces:**
- Consumes: `SelectedStrategyReadiness.decision_lifecycle`.
- Produces: `ItemRow.decision_lifecycle`, React event `review_latest_decision`, Python-owned Final Review navigation.
- Existing `end_item` remains the only tracking-stop mutation.

- [ ] **Step 1: item-local lifecycle 실패 테스트 작성**

```python
def test_selected_strategy_failure_projects_decision_lifecycle_without_removing_item(self) -> None:
    readiness = SelectedStrategyReadiness(
        status="BLOCKED",
        blockers=("최신 Final Review 판단이 관찰 후 재검토로 변경되었습니다.",),
        source_dates={},
        decision_lifecycle={
            "state": "TRACKING_ELIGIBILITY_CHANGED",
            "locked": True,
            "latest_route": "HOLD_FOR_MORE_PAPER_TRACKING",
            "latest_source_id": "validation-new-hold",
        },
    )
    result = align_group_value_lanes(
        [_selected_strategy_item("item-strategy", "old-selected")],
        {"item-strategy": SelectedStrategyReplayError(readiness)},
    )
    self.assertEqual(result.status, "PARTIAL")
    self.assertEqual(result.item_rows[0]["source_type"], "selected_strategy")
    self.assertTrue(result.item_rows[0]["decision_lifecycle"]["locked"])
```

- [ ] **Step 2: React presentation과 event 실패 테스트 작성**

```typescript
it("presents a locked latest-decision lifecycle", () => {
  const view = decisionLifecyclePresentation({
    ...activeGroup.item_rows[0],
    source_type: "selected_strategy",
    decision_lifecycle: {
      state: "TRACKING_ELIGIBILITY_CHANGED",
      locked: true,
      latest_route: "HOLD_FOR_MORE_PAPER_TRACKING",
      latest_route_label: "관찰 후 재검토",
      latest_source_id: "validation-new-hold",
      message: "최신 판단이 변경되어 새 계산을 잠갔습니다.",
    },
  });
  expect(view.locked).toBe(true);
  expect(view.label).toBe("추적 자격 변경");
  expect(view.actionLabel).toBe("최신 판단 재확인");
});
```

Python component contract test must assert `추적 자격 변경`, `최신 판단 재확인`, and `id: "review_latest_decision"` exist together.

- [ ] **Step 3: Python page dispatch 실패 테스트 작성**

```python
def test_dispatches_latest_decision_review_navigation(self) -> None:
    services = self._services()
    services.review_latest_decision = lambda event: services.calls.append(("review_latest_decision", event)) or None
    event = {"id": "review_latest_decision", "monitoring_item_id": "item-strategy"}
    result = page._dispatch_portfolio_monitoring_event(event, services)
    self.assertIsNone(result)
    self.assertIn(("review_latest_decision", event), services.calls)
```

Add a default-service test with a fake selected item and latest non-select row. Assert it sets `backtest_requested_panel == "Final Review"`, sets `final_review_active_decision_brief_source_id`, and calls the configured Backtest Page without registry writes.

- [ ] **Step 4: RED 확인**

Run:

```bash
.venv/bin/python -m pytest tests/test_portfolio_monitoring_read_model.py tests/test_portfolio_monitoring_page.py tests/test_portfolio_monitoring_component.py -q
npm --prefix app/web/streamlit_components/portfolio_monitoring_workbench test
```

Expected: lifecycle fields, helper, event union, and dispatch callback are absent so tests FAIL.

- [ ] **Step 5: Python read model lifecycle projection 구현**

```python
def _decision_lifecycle_from_lane(value: ItemValueLane | BaseException | None) -> dict[str, Any]:
    readiness = value.readiness if isinstance(value, ItemValueLane) else getattr(value, "readiness", None)
    return dict(getattr(readiness, "decision_lifecycle", {}) or {})


item_row = {
    "monitoring_item_id": item.monitoring_item_id,
    "source_type": item.source_type,
    "instrument_kind": item.instrument_kind,
    "source_ref": item.source_ref,
    "status": item.status,
    "lane_status": valid_lanes[item.monitoring_item_id].status if item.monitoring_item_id in valid_lanes else "failed",
    "decision_lifecycle": _decision_lifecycle_from_lane(lanes.get(item.monitoring_item_id)),
    "failure": failures.get(item.monitoring_item_id),
}
```

Preserve all existing numeric fields in the actual item-row projection.

- [ ] **Step 6: Python-owned Final Review route 구현**

```python
_PORTFOLIO_MONITORING_PAGE_TARGETS: dict[str, object] = {}


def configure_portfolio_monitoring_page_targets(page_targets: dict[str, object]) -> None:
    _PORTFOLIO_MONITORING_PAGE_TARGETS.clear()
    target = dict(page_targets or {}).get("backtest")
    if target is not None:
        _PORTFOLIO_MONITORING_PAGE_TARGETS["backtest"] = target
```

Extend `PortfolioMonitoringPageServices` with `review_latest_decision: Callable[[dict[str, Any]], dict[str, Any] | None]`. The default callback resolves the item server-side, requires selected strategy, loads latest lifecycle, sets Backtest Final Review session hints, and calls `st.switch_page(configured_backtest_page)`. Configure `{"backtest": backtest_page}` in `streamlit_app.py`.

- [ ] **Step 7: React locked card와 event 구현**

```typescript
export type DecisionLifecycleProjection = {
  state: "CURRENT_SELECTED" | "SUPERSEDED_SELECTED" | "TRACKING_ELIGIBILITY_CHANGED" | "DECISION_NOT_FOUND" | string;
  locked: boolean;
  latest_route: string | null;
  latest_route_label?: string | null;
  latest_source_id: string | null;
  message: string;
};
```

Add `decision_lifecycle` to `ItemRow` and `{id: "review_latest_decision"; monitoring_item_id: string; nonce: string}` to the event union. Render the dedicated warning card only when locked. The review button sends only `monitoring_item_id`; it must not send a trusted route or source ID.

- [ ] **Step 8: focused Python/React GREEN 확인**

Run:

```bash
.venv/bin/python -m pytest tests/test_portfolio_monitoring_decision_lifecycle.py tests/test_portfolio_monitoring_catalog.py tests/test_portfolio_monitoring_selected_strategy.py tests/test_portfolio_monitoring_read_model.py tests/test_portfolio_monitoring_page.py tests/test_portfolio_monitoring_component.py -q
npm --prefix app/web/streamlit_components/portfolio_monitoring_workbench test
npm --prefix app/web/streamlit_components/portfolio_monitoring_workbench run typecheck
npm --prefix app/web/streamlit_components/portfolio_monitoring_workbench run build
```

Expected: all focused tests, Vitest, typecheck, and Vite build PASS.

- [ ] **Step 9: Task 3 커밋**

```bash
git add app/services/portfolio_monitoring/read_model.py app/web/final_selected_portfolio_dashboard.py app/web/streamlit_app.py app/web/streamlit_components/portfolio_monitoring_workbench/src tests/test_portfolio_monitoring_read_model.py tests/test_portfolio_monitoring_page.py tests/test_portfolio_monitoring_component.py
git commit -m "개선: Monitoring 추적 자격 변경 행동 연결"
```

---

### Task 4: 전체 회귀, actual QA, durable docs closeout

**Files:**
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

**Interfaces:**
- Consumes: Tasks 1-3 implementation and tests.
- Produces: verified implementation, one uncommitted QA screenshot, durable stage/storage/lifecycle documentation.

- [ ] **Step 1: Portfolio Monitoring 전체 Python 회귀 실행**

Run:

```bash
.venv/bin/python -m pytest tests/test_portfolio_monitoring_decision_lifecycle.py tests/test_portfolio_monitoring_catalog.py tests/test_portfolio_monitoring_selected_strategy.py tests/test_portfolio_monitoring_read_model.py tests/test_portfolio_monitoring_page.py tests/test_portfolio_monitoring_component.py tests/test_portfolio_monitoring_commands.py tests/test_portfolio_monitoring_schema.py tests/test_service_contracts.py -q
```

Expected: all selected tests PASS; only existing third-party deprecation warnings are allowed.

- [ ] **Step 2: compile/build/diff 검증**

Run:

```bash
.venv/bin/python -m py_compile app/services/portfolio_monitoring/decision_lifecycle.py app/services/portfolio_monitoring/catalog.py app/services/portfolio_monitoring/selected_strategy.py app/services/portfolio_monitoring/read_model.py app/web/final_selected_portfolio_dashboard.py app/web/streamlit_app.py
npm --prefix app/web/streamlit_components/portfolio_monitoring_workbench test
npm --prefix app/web/streamlit_components/portfolio_monitoring_workbench run typecheck
npm --prefix app/web/streamlit_components/portfolio_monitoring_workbench run build
git diff --check
```

Expected: every command exits 0.

- [ ] **Step 3: actual registry read-only 검증**

Use the production loader without writing rows. Confirm current six selected decisions remain six latest selected subjects, then pass a synthetic in-memory old-selected/latest-hold pair to the lifecycle service and verify catalog count 0 plus `TRACKING_ELIGIBILITY_CHANGED` lock. Do not append the synthetic pair to a registry.

- [ ] **Step 4: Browser QA**

Start the current worktree Streamlit app on an unused port. Verify current actual Portfolio Monitoring opens, selected strategies remain visible, item detail and `추적 종료` still work, and desktop/760px layouts have no horizontal overflow. Because the actual registry has no superseded subject, verify the locked-state DOM through automated component contract tests rather than mutating registry data. Save one representative screenshot as `portfolio-monitoring-latest-decision-lifecycle-v1-qa.png` and keep it uncommitted.

- [ ] **Step 5: finance durable docs 동기화**

Document these exact durable rules:

- Final Review remains append-only.
- Portfolio Monitoring current eligibility is latest-per-subject, not any historical selected row.
- Existing item is preserved but replay-locked after latest non-select judgment.
- Continue requires Final Review re-selection; stop uses existing `end_item`.
- requested/effective decision provenance is preserved.

Update task status to `4/4 complete`, record commands/results in `RUNS.md`, residual QA gaps in `RISKS.md`, and keep root logs to 3-5 lines.

- [ ] **Step 6: protected-artifact stage audit**

Run:

```bash
git diff --check
git status --short
git diff --name-only
```

Expected: registry JSONL, saved setup, run history, `.superpowers/`, and PNG artifacts are not staged.

- [ ] **Step 7: closeout commit**

```bash
git add .aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md .aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md .aiworkspace/note/finance/docs/INDEX.md .aiworkspace/note/finance/docs/ROADMAP.md .aiworkspace/note/finance/tasks/active/portfolio-monitoring-latest-decision-lifecycle-v1-20260723 .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "문서: Monitoring 최신 판단 수명주기 정리"
```

## Self-Review Result

- Spec coverage: latest identity, new catalog filter, existing-item preservation, replay lock, Final Review recheck, existing end action, re-selection unlock, protected artifacts, QA/docs are each owned by Tasks 1-4.
- Placeholder scan: no deferred implementation marker or ambiguous handler name remains.
- Type consistency: `MonitoringDecisionLifecycle.to_projection()` feeds `SelectedStrategyReadiness.decision_lifecycle`, Python `ItemRow.decision_lifecycle`, TypeScript `DecisionLifecycleProjection`, and the `review_latest_decision` event consistently.
- Scope: one lifecycle service plus its three existing consumers; no schema migration, registry rewrite, local waiver, or trading behavior is included.
