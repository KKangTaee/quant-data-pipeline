# Economic Cycle Rate Unit Copy Implementation Plan

> 현재 세션의 inline execution으로 구현하고 검증한다. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 채권·금리 카드의 현재 수익률과 bp 변화량을 직관적인 한국어 단위로 표시한다.

**Architecture:** 기존 `MovementMetric.level_unit`을 그대로 사용하고 React 표시 함수만 추가한다. 서비스 계산과 payload schema는 변경하지 않는다.

**Tech Stack:** Python pytest source-contract test, React 18, TypeScript, Vite

## Global Constraints

- 현재 수익률 수준만 `연 n.nn%`로 현지화한다.
- 금리차 수준과 변화량은 `bp`를 유지한다.
- 다른 자산의 가격 변화율 UI는 변경하지 않는다.

---

### Task 1: 금리 단위 문구 수정

**Files:**
- Modify: `tests/test_market_context_economic_cycle.py`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`
- Regenerate: `app/web/streamlit_components/economic_cycle_workbench/component_static/`

**Interfaces:**
- Consumes: `MovementMetric.current_value`, `MovementMetric.level_unit`
- Produces: `formatMovementLevel(value, unit): string`

- [ ] **Step 1: 실패하는 source-contract 테스트 작성**

```python
assert "formatMovementLevel" in source
assert 'unit === "percent" ? `연 ${value.toFixed(2)}%`' in source
assert "현재 값은 최신 저장 관측치이며, 금리 변화는 bp 기준입니다." in source
assert "row.current_value.toFixed(2)} {row.level_unit" not in source
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `uv run --with pytest python -m pytest tests/test_market_context_economic_cycle.py::test_cycle_component_formats_rate_levels_and_explains_basis_points -q`

Expected: `formatMovementLevel`이 없어 assertion failure가 발생한다.

- [ ] **Step 3: 최소 구현**

```tsx
const formatMovementLevel = (value: number | null, unit?: string | null) => {
  if (value == null) return "-";
  if (unit === "percent") return `연 ${value.toFixed(2)}%`;
  return `${value.toFixed(2)} ${unit || ""}`.trim();
};
```

`CurrentMovementBlock`의 제목 아래에 bp 설명을 추가하고, 현재 값을 위 함수로 표시한다.

- [ ] **Step 4: 테스트와 번들 검증**

Run: `uv run --with pytest python -m pytest tests/test_market_context_economic_cycle.py -q`

Expected: focused test file 전체 통과.

Run: `npm --prefix app/web/streamlit_components/economic_cycle_workbench run build`

Expected: Vite build exit code 0.

- [ ] **Step 5: 브라우저 QA와 커밋**

- 2년·10년 수익률이 `연 n.nn%`로 표시되는지 확인한다.
- 금리차와 변화량이 `bp`로 유지되는지 확인한다.
- 관련 파일만 커밋한다.
