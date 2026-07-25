# Institutional Studio Rail Interaction Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Institutional Holdings research rail의 선택 상태를 flat editorial 표현으로 바꾸고 기관 목록을 더 긴 grab-to-scroll 영역으로 만든다.

**Architecture:** 드래그 좌표 계산과 threshold 판정은 `workbenchState.ts`의 순수 함수로 분리해 Vitest로 보호한다. `InstitutionalPortfoliosWorkbench.tsx`는 pointer capture와 click suppression만 조정하고, `style.css`는 flat active state·360px viewport·hidden scrollbar·grab cursor를 소유한다. Python payload, Streamlit event, DB loader와 기관 순서는 변경하지 않는다.

**Tech Stack:** React 18, TypeScript 5.7, Pointer Events, Vitest 4, Vite 6, Streamlit custom component

## Global Constraints

- 선택 탐색 항목에 둥근 active card, 외곽선, 왼쪽 inset bar를 사용하지 않는다.
- 선택 상태는 번호·제목 대비와 제목 아래 짧은 수평 직선으로 표현한다.
- 기관 목록은 순서 재배치가 아니라 vertical grab-to-scroll로 동작한다.
- desktop manager viewport는 `360px`를 기본 최대 높이로 사용한다.
- scrollbar는 시각적으로 숨기되 wheel, trackpad, touch, keyboard scrolling을 유지한다.
- drag threshold 이후 이어지는 click은 기관 선택을 실행하지 않는다.
- 터치의 native scrolling을 방해하지 않는다.
- registry, saved portfolio, run history와 생성된 QA artifact는 커밋하지 않는다.

---

### Task 1: Drag Math Contract

**Files:**
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/src/workbenchState.ts`
- Test: `app/web/streamlit_components/institutional_portfolios_workbench/src/workbenchState.test.ts`

**Interfaces:**
- Produces: `managerDragScrollTop(startScrollTop: number, startClientY: number, currentClientY: number): number`
- Produces: `managerDragExceededThreshold(startClientY: number, currentClientY: number, threshold?: number): boolean`

- [ ] **Step 1: Write failing tests for vertical scroll delta and threshold**

Add imports and these behavior tests:

```ts
describe("manager rail drag scrolling", () => {
  it("moves scrollTop opposite to the pointer delta and never below zero", () => {
    expect(managerDragScrollTop(120, 300, 240)).toBe(180);
    expect(managerDragScrollTop(20, 100, 150)).toBe(0);
  });

  it("suppresses selection only after the pointer crosses the drag threshold", () => {
    expect(managerDragExceededThreshold(100, 104)).toBe(false);
    expect(managerDragExceededThreshold(100, 107)).toBe(true);
  });
});
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
cd app/web/streamlit_components/institutional_portfolios_workbench
npm test -- --run src/workbenchState.test.ts
```

Expected: FAIL because the two drag helpers are not exported.

- [ ] **Step 3: Implement the minimal pure helpers**

Add:

```ts
export function managerDragScrollTop(
  startScrollTop: number,
  startClientY: number,
  currentClientY: number
) {
  return Math.max(0, startScrollTop - (currentClientY - startClientY));
}

export function managerDragExceededThreshold(
  startClientY: number,
  currentClientY: number,
  threshold = 6
) {
  return Math.abs(currentClientY - startClientY) >= threshold;
}
```

- [ ] **Step 4: Run the focused test and verify GREEN**

Run the same test command.

Expected: all `workbenchState.test.ts` tests PASS.

- [ ] **Step 5: Commit the drag math contract**

```bash
git add app/web/streamlit_components/institutional_portfolios_workbench/src/workbenchState.ts \
  app/web/streamlit_components/institutional_portfolios_workbench/src/workbenchState.test.ts
git commit -m "기관 목록 드래그 계산 계약 추가"
```

### Task 2: Pointer Interaction And Flat Active State

**Files:**
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/src/InstitutionalPortfoliosWorkbench.tsx`
- Modify: `app/web/streamlit_components/institutional_portfolios_workbench/src/style.css`
- Rebuild: `app/web/streamlit_components/institutional_portfolios_workbench/component_static/`

**Interfaces:**
- Consumes: `managerDragScrollTop(...)`, `managerDragExceededThreshold(...)`
- Keeps: existing `handleManagerSelect(item: ManagerItem)` Streamlit event boundary

- [ ] **Step 1: Add pointer drag state without changing manager data**

Add refs for `{ pointerId, startClientY, startScrollTop, dragged }`, pointer handlers that ignore non-primary mouse buttons and touch pointers, and a click-capture handler that prevents selection after a threshold-crossing drag. Pointer down must call `setPointerCapture`; the move handler sets `data-dragging="true"` after the threshold and assigns:

```ts
rail.scrollTop = managerDragScrollTop(
  drag.startScrollTop,
  drag.startClientY,
  event.clientY
);
```

The end/cancel handler must release capture when held and clear the visual dragging state. The suppression flag must be consumed once by `onClickCapture`. Replace the existing vertical-list rerun preservation from `scrollLeft` to `scrollTop` in both the selection handler and payload effect.

- [ ] **Step 2: Make the manager region keyboard-scrollable and connect handlers**

Use:

```tsx
<div
  className="ip-manager-favorites ip-manager-rail"
  aria-label="기관 및 투자 대가 목록. 마우스로 잡아 위아래로 이동할 수 있습니다."
  tabIndex={0}
  ref={managerRailRef}
  onPointerDown={handleManagerRailPointerDown}
  onPointerMove={handleManagerRailPointerMove}
  onPointerUp={handleManagerRailPointerEnd}
  onPointerCancel={handleManagerRailPointerEnd}
  onClickCapture={handleManagerRailClickCapture}
>
```

Do not change child button order or `handleManagerSelect`.

- [ ] **Step 3: Replace the selected navigation card with flat editorial styling**

Update `.ip-studio-nav button` to use `border-radius: 0`, no active border/background, and a pseudo-element on the active title span:

```css
.ip-studio-nav__active {
  border-color: transparent !important;
  box-shadow: none;
  background: transparent !important;
}

.ip-studio-nav__active em {
  color: #75b9ee;
}

.ip-studio-nav__active strong {
  color: #ffffff;
}

.ip-studio-nav__active > span::after {
  display: block;
  width: 28px;
  height: 2px;
  margin-top: 7px;
  background: #75b9ee;
  content: "";
}
```

Keep hover as a subtle non-selected background without rounded card semantics.

- [ ] **Step 4: Expand and visually hide the manager scrollbar**

Set the desktop manager list to `max-height: 360px`, `cursor: grab`, `scrollbar-width: none`, and hide the WebKit scrollbar. Use `cursor: grabbing` plus `user-select: none` only while `data-dragging="true"`. Keep `overflow-y: auto`, keyboard focus styling and native touch behavior.

- [ ] **Step 5: Run React verification**

Run:

```bash
cd app/web/streamlit_components/institutional_portfolios_workbench
npm test -- --run
npm run typecheck
npm run build
```

Expected: all tests PASS, TypeScript exits 0, Vite writes the production `component_static` bundle.

- [ ] **Step 6: Run Python boundary regression**

Run:

```bash
.venv/bin/python -m unittest tests.test_institutional_portfolios
.venv/bin/python -m py_compile app/services/institutional_portfolios.py app/web/institutional_portfolios.py
```

Expected: 58 Python tests PASS and py_compile exits 0.

- [ ] **Step 7: Commit the UI interaction**

Stage only the React source and rebuilt institutional component assets:

```bash
git add app/web/streamlit_components/institutional_portfolios_workbench/src \
  app/web/streamlit_components/institutional_portfolios_workbench/component_static
git commit -m "기관 보유 rail 선택과 드래그 탐색 개선"
```

### Task 3: Actual Browser QA And Durable Closeout

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/institutional-holdings-react-parity-v1-20260725/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/institutional-holdings-react-parity-v1-20260725/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/institutional-holdings-react-parity-v1-20260725/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/institutional-holdings-react-parity-v1-20260725/RISKS.md`
- Modify only if durable behavior changed materially: `.aiworkspace/note/finance/docs/flows/INSTITUTIONAL_PORTFOLIOS_FLOW.md`
- Create generated QA screenshot without staging it: `institutional-holdings-rail-drag-polish-qa.png`

**Interfaces:**
- Consumes: rebuilt `institutional_portfolios_workbench_v2` static bundle
- Produces: verified interaction evidence and concise task closeout

- [ ] **Step 1: Start the local Streamlit app and open Institutional Holdings**

Run:

```bash
.venv/bin/streamlit run app/web/streamlit_app.py --server.port 8502
```

Open `http://localhost:8502`, select `Research > Institutional Holdings`, and use the actual DB-backed manager list.

- [ ] **Step 2: Verify desktop flat active state and list geometry**

At 1280px confirm:

- selected navigation has no rounded card, left inset bar or active border
- selected number/title and short horizontal line are visible
- manager viewport shows more rows than the previous 250px region
- native scrollbar is not visible
- no horizontal overflow

- [ ] **Step 3: Verify mouse drag and selection safety**

Drag the manager list vertically, confirm `scrollTop` changes, release, and confirm the item under the release point was not selected. Then click a manager without dragging and confirm the correct manager payload loads. Verify wheel/trackpad scrolling remains available.

- [ ] **Step 4: Verify responsive drawer**

At 760px and 420px confirm the drawer opens/closes, manager list remains usable, native touch-compatible vertical scrolling is not blocked, and the active destination remains readable.

- [ ] **Step 5: Inspect browser console and capture QA**

Confirm zero new errors/warnings and save one screenshot to `institutional-holdings-rail-drag-polish-qa.png`. Do not stage the image.

- [ ] **Step 6: Update the active task closeout**

Record the exact React/Python test counts, viewport results, manager click result, drag result, console result and any residual risk in the active task docs. Update the durable flow only if the verified behavior changes future ownership/interaction guidance.

- [ ] **Step 7: Run final verification and commit docs**

Run:

```bash
git diff --check
git status --short
```

Confirm registry JSONL, saved portfolios, run history and generated screenshots remain unstaged. Commit only closeout docs:

```bash
git add .aiworkspace/note/finance/tasks/active/institutional-holdings-react-parity-v1-20260725
git commit -m "기관 보유 rail 상호작용 QA 기록"
```
