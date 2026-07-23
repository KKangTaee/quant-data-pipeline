# Futures Macro Confirmation Matrix Follow-up Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 확인 신호 두 행을 `신호 | 최근 1D | 최근 5D | 최근 20D` 열이 명시된 별도 미니 매트릭스로 표시한다.

**Architecture:** Python payload와 family 계산은 그대로 두고 React presentation만 바꾼다. 기존 `DirectionCell`과 `DirectionRow`를 재사용하고 `DirectionHeaders`를 label-configurable하게 만들어 core와 confirmation의 기간 표기를 각각 유지한다.

**Tech Stack:** React 18, TypeScript 5, CSS, Vite 6, pytest source-contract tests, Codex in-app Browser QA.

## Global Constraints

- core 4와 confirmation 2 의미 경계와 순서를 유지한다.
- confirmation 기간 헤더는 정확히 `최근 1D`, `최근 5D`, `최근 20D`를 사용한다.
- Python payload/schema/model/DB/refresh 계약은 변경하지 않는다.
- desktop과 420px 모두 가로 overflow가 없어야 한다.
- generated QA screenshot과 기존 unrelated dirty files는 stage하지 않는다.

---

### Task 1: Confirmation mini-matrix presentation

**Files:**
- Modify: `tests/test_overview_futures_macro_short_horizon.py`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/FamilyDirectionSection.tsx`
- Modify: `app/web/streamlit_components/futures_macro_workbench/src/style.css`
- Modify: `app/web/streamlit_components/futures_macro_workbench/component_static/`

**Interfaces:**
- Consumes: existing `FamilyDirectionRow[]` in `confirmationSignals`.
- Produces: a presentation-only confirmation matrix using existing `DirectionCell` and `DirectionRow`; no payload changes.

- [x] **Step 1: Write the failing source-contract test**

Add a focused assertion:

```python
def test_confirmation_signals_use_explicit_recent_window_headers() -> None:
    family = Path(
        "app/web/streamlit_components/futures_macro_workbench/src/"
        "FamilyDirectionSection.tsx"
    ).read_text(encoding="utf-8")

    assert 'firstLabel="신호"' in family
    assert 'oneDayLabel="최근 1D"' in family
    assert 'fiveDayLabel="최근 5D"' in family
    assert 'twentyDayLabel="최근 20D"' in family
    assert "최근 1D · 5D · 20D" not in family
```

- [x] **Step 2: Run RED**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_overview_futures_macro_short_horizon.py \
  -q -k confirmation_signals_use_explicit_recent_window_headers
```

Expected: FAIL because confirmation still uses cards and the ambiguous footer.

- [x] **Step 3: Implement configurable headers and confirmation rows**

Change `DirectionHeaders` to accept explicit labels:

```tsx
function DirectionHeaders({
  firstLabel = "방향축",
  oneDayLabel = "1D",
  fiveDayLabel = "5D",
  twentyDayLabel = "20D",
}: {
  firstLabel?: string;
  oneDayLabel?: string;
  fiveDayLabel?: string;
  twentyDayLabel?: string;
}) {
  return (
    <div className="fm-workbench__direction-headers">
      <span>{firstLabel}</span>
      <span>{oneDayLabel}</span>
      <span>{fiveDayLabel}</span>
      <span>{twentyDayLabel}</span>
    </div>
  );
}
```

Replace the two confirmation cards with:

```tsx
<div className="fm-workbench__confirmation-block">
  <div className="fm-workbench__confirmation-intro">
    <div><span>Confirmation</span><h4>확인 신호</h4></div>
    <p>{confirmationSummary}</p>
  </div>
  <div className="fm-workbench__confirmation-matrix">
    <DirectionHeaders
      firstLabel="신호"
      oneDayLabel="최근 1D"
      fiveDayLabel="최근 5D"
      twentyDayLabel="최근 20D"
    />
    {confirmationSignals.map((row) => <DirectionRow key={row.key} row={row} />)}
  </div>
</div>
```

Remove `.fm-workbench__confirmation-grid` card rules. Style the block as one bordered, low-emphasis matrix and keep the existing <=760px direction grid sizing.

- [x] **Step 4: Run GREEN and build**

Run:

```bash
.venv/bin/python -m pytest tests/test_overview_futures_macro_short_horizon.py -q
npm --prefix app/web/streamlit_components/futures_macro_workbench run build
git diff --check
```

Expected: all tests and build PASS.

- [x] **Step 5: Actual Browser QA**

At `http://localhost:8501/overview?overview_tab=futures-macro`, verify:

- confirmation has one header row and two signal rows;
- values align under recent 1D/5D/20D;
- desktop and 420px have zero horizontal overflow;
- browser console warning/error list is empty.

- [x] **Step 6: Closeout and commit**

Update the active task `STATUS.md` and `RUNS.md` with this follow-up and QA evidence, then commit only:

```bash
git add \
  app/web/streamlit_components/futures_macro_workbench/src/FamilyDirectionSection.tsx \
  app/web/streamlit_components/futures_macro_workbench/src/style.css \
  app/web/streamlit_components/futures_macro_workbench/component_static \
  tests/test_overview_futures_macro_short_horizon.py \
  .aiworkspace/note/finance/tasks/active/overview-futures-macro-short-horizon-v1-20260723
git commit -m "선물 매크로 확인 신호 기간 정렬 개선"
```

## Self-review

- Spec coverage: explicit confirmation window headers, separate hierarchy, responsive QA, and no payload change are all covered.
- Placeholder scan: no incomplete implementation instruction remains.
- Type consistency: `DirectionHeaders` props are optional strings and all call sites use the exact names shown above.
- Scope: one React component, CSS, its static bundle, focused test, and task closeout only.
