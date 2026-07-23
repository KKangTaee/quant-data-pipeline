# Portfolio Monitoring Initial Correction Local Preview V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 최초 설정 정정의 날짜·수량 편집은 local state로 유지하고, 사용자가 `변경값 확인`을 누를 때만 DB 적용일·종가·투자금 preview를 조회한다.

**Architecture:** 기존 Python `lookup_initial_position_entry` event와 correction command는 유지한다. React `PositionLedgerPanel`은 draft 변경과 preview request를 분리하고, pure state helper가 현재 draft에 preview 조회가 가능한지와 기존 preview가 일치하는지를 판정한다. Streamlit rerun은 명시적 preview request와 최종 저장에서만 발생한다.

**Tech Stack:** React 18, TypeScript, Vitest, Streamlit custom component, Python unittest, Vite.

## Global Constraints

- 날짜·수량 `onChange`는 Python event를 emit하지 않는다.
- `변경값 확인`은 유효한 날짜와 1주 이상의 정수 수량일 때만 event를 emit한다.
- 기존 preview가 현재 날짜·수량과 다르면 저장할 수 없다.
- `lookup_initial_position_entry`, `correct_initial_quantity`, DB schema와 valuation 계약은 변경하지 않는다.
- 매수·매도 거래일 종가 조회 UX는 이번 범위에서 변경하지 않는다.
- 사용자 기존 registry/run-history/generated artifact는 stage하지 않는다.

---

### Task 1: Preview readiness pure contract

**Files:**
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/positionEditorState.ts`
- Test: `app/web/streamlit_components/portfolio_monitoring_workbench/src/positionEditorState.test.ts`

**Interfaces:**
- Consumes: `PositionEditorDraft`, `InitialPositionEntryProjection`의 status/item/date/quantity.
- Produces: `canRequestInitialEntryPreview(draft) -> boolean`, `matchesInitialEntryPreview(draft, projection, monitoringItemId) -> boolean`.

- [x] **Step 1: Write failing helper tests**

```ts
it("requires an explicit valid correction preview request", () => {
  expect(canRequestInitialEntryPreview({ ...correction, tradeDate: "" })).toBe(false);
  expect(canRequestInitialEntryPreview({ ...correction, quantity: "1.5" })).toBe(false);
  expect(canRequestInitialEntryPreview(correction)).toBe(true);
});

it("invalidates a preview when the local date or quantity changes", () => {
  expect(matchesInitialEntryPreview(correction, ready, "item-amd")).toBe(true);
  expect(matchesInitialEntryPreview({ ...correction, tradeDate: "2026-06-29" }, ready, "item-amd")).toBe(false);
  expect(matchesInitialEntryPreview({ ...correction, quantity: "41" }, ready, "item-amd")).toBe(false);
});
```

- [x] **Step 2: Run the focused test and verify RED**

Run: `npm test -- --run src/positionEditorState.test.ts`

Expected: FAIL because both helper exports do not exist.

- [x] **Step 3: Implement the minimal pure helpers**

```ts
export function canRequestInitialEntryPreview(draft: PositionEditorDraft): boolean {
  const quantity = Number(draft.quantity);
  return draft.mode === "correct_initial"
    && Boolean(draft.tradeDate)
    && Number.isInteger(quantity)
    && quantity >= 1;
}

export function matchesInitialEntryPreview(
  draft: PositionEditorDraft,
  projection: InitialPositionEntryProjection | null | undefined,
  monitoringItemId: string,
): boolean {
  return canRequestInitialEntryPreview(draft)
    && projection?.status === "READY"
    && projection.monitoring_item_id === monitoringItemId
    && projection.requested_start_date === draft.tradeDate
    && projection.quantity === Number(draft.quantity);
}
```

- [x] **Step 4: Run the focused test and verify GREEN**

Run: `npm test -- --run src/positionEditorState.test.ts`

Expected: all focused tests pass.

### Task 2: Explicit preview action in the editor

**Files:**
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/PositionLedgerPanel.tsx`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css`
- Test: `tests/test_portfolio_monitoring_component.py`

**Interfaces:**
- Consumes: Task 1 readiness helpers and existing `lookup_initial_position_entry` event.
- Produces: local-only date/quantity changes and a visible `변경값 확인` button that emits exactly one lookup event.

- [x] **Step 1: Write failing source-contract tests**

```python
def test_initial_correction_keeps_date_and_quantity_local_until_preview_action(self):
    source = POSITION_LEDGER_SOURCE.read_text()
    self.assertIn("변경값 확인", source)
    self.assertIn("requestInitialEntryPreview", source)
    self.assertNotIn(
        'onChange={(event) => requestInitialEntry(changeTradeDate(draft, event.target.value))}',
        source,
    )
    self.assertNotIn(
        'if (draft.mode === "correct_initial") requestInitialEntry(next)',
        source,
    )
```

- [x] **Step 2: Run the Python component test and verify RED**

Run: `.venv/bin/python -m unittest tests.test_portfolio_monitoring_component`

Expected: FAIL because the explicit preview action is absent and onChange still emits.

- [x] **Step 3: Implement local input and explicit request**

```tsx
const requestInitialEntryPreview = () => {
  if (!draft || !canRequestInitialEntryPreview(draft)) return;
  emit({
    id: "lookup_initial_position_entry",
    monitoring_item_id: itemId,
    requested_start_date: draft.tradeDate,
    quantity: Number(draft.quantity),
    position_editor_state: buildPositionEditorRecovery(draft),
  });
};

<input type="date" value={draft.tradeDate}
  onChange={(event) => setDraft(changeTradeDate(draft, event.target.value))} />
<input type="number" value={draft.quantity}
  onChange={(event) => setDraft({ ...draft, quantity: event.target.value })} />
<button type="button" onClick={requestInitialEntryPreview}
  disabled={!canRequestInitialEntryPreview(draft)}>변경값 확인</button>
```

Use `matchesInitialEntryPreview` for `initialEntryReady`. Hide or disable the preview action when the matching READY projection is current, and keep final save disabled through the existing validation until the current draft is confirmed.

- [x] **Step 4: Verify the focused Python and React tests**

Run:

```bash
.venv/bin/python -m unittest tests.test_portfolio_monitoring_component
cd app/web/streamlit_components/portfolio_monitoring_workbench
npm test -- --run
```

Expected: Python component contracts and all React tests pass.

### Task 3: Regression, build, actual Browser QA, and closeout

**Files:**
- Modify generated build: `app/web/streamlit_components/portfolio_monitoring_workbench/component_static/`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Modify task: `STATUS.md`, add `NOTES.md`, `RUNS.md`, `RISKS.md`

**Interfaces:**
- Consumes: completed Tasks 1-2.
- Produces: verified component bundle, durable workflow handoff, generated QA screenshot, coherent commit.

- [x] **Step 1: Run full focused regression and production build**

Run:

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_portfolio_monitoring*.py'
.venv/bin/python -m py_compile app/web/final_selected_portfolio_dashboard.py
cd app/web/streamlit_components/portfolio_monitoring_workbench
npm run typecheck
npm test -- --run
npm run build
cd ../../../..
git diff --check
```

Expected: all tests, typecheck, build, compile, and whitespace checks pass.

- [x] **Step 2: Run actual Browser QA**

Open `Portfolio > Portfolio Monitoring`, select an eligible direct-stock fixed-shares item, open `최초 설정 정정`, move the date picker to another month, and confirm the dialog stays open without page rerun. Select a date and change quantity; confirm no server refresh occurs. Click `변경값 확인` once; confirm the editor recovers with matching applied date/close/capital and save becomes enabled. Do not submit the correction during QA unless using a disposable item.

- [x] **Step 3: Synchronize durable docs and task records**

Record the local-input/explicit-preview boundary, actual QA result, test commands, and the unchanged correction persistence/valuation contract. Keep generated screenshot and user registry/run history untracked.

- [x] **Step 4: Commit the implementation**

Stage only implementation, tests, task docs, durable docs, and component static build. Commit with Korean message `수정: 최초 설정 정정 달력 rerun 방지`.
