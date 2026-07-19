# Economic Cycle Monthly Signal Guide Implementation Plan

> 현재 세션의 inline execution으로 순서대로 구현하고 검증한다. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** 경제 사이클 하단에 월별 국면 신호의 의미와 보수적인 대응 순서를 다시 볼 수 있는 기본 닫힘 가이드를 추가한다.

**Architecture:** 기존 React 컴포넌트 안에 정적 `MonthlySignalGuide`를 추가하고 네이티브 `details/summary`로 접힘 상태를 관리한다. 모델 payload와 서비스는 건드리지 않으며 source-contract 테스트와 Vite build로 정적 컴포넌트 계약을 검증한다.

**Tech Stack:** Python pytest source-contract test, React 18, TypeScript, CSS, Vite

## Global Constraints

- 모델 입력, 확률, 좌표 계산, payload schema는 변경하지 않는다.
- 기본 상태는 닫힘이며 현재 국면 자동 강조를 추가하지 않는다.
- 투자 추천, 목표 비중, 수익률 예측, `매수`, `매도`, `주문` 문구를 추가하지 않는다.
- 국면별 구분은 좌측 선이 아니라 카드 전체의 연한 배경으로 처리한다.

---

### Task 1: 월별 신호 가이드 추가

**Files:**
- Modify: `tests/test_market_context_economic_cycle.py`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/style.css`
- Regenerate: `app/web/streamlit_components/economic_cycle_workbench/component_static/`

**Interfaces:**
- Consumes: 없음. 정적 교육용 안내만 사용한다.
- Produces: `MonthlySignalGuide(): JSX.Element`

- [x] **Step 1: 실패하는 source-contract 테스트 작성**

다음 계약을 새 테스트에 추가한다.

```python
assert '<details className="cycle-usage-guide">' in source
assert "월별 사이클 신호 활용법" in source
assert "한 달 신호" in source
assert "같은 방향이 여러 달" in source
assert "실물·금융·가격" in source
for token in ("회복 신호", "확장 신호", "둔화 신호", "침체 신호"):
    assert token in source
for token in ("침체 → 회복", "회복 → 확장", "확장 → 둔화", "둔화 → 침체"):
    assert token in source
assert ".cycle-guide-phase-grid" in css
assert ".cycle-guide-transition-grid" in css
assert "border-left" not in css[css.index(".cycle-usage-guide"):]
```

- [x] **Step 2: 테스트 실패 확인**

Run: `uv run --with pytest python -m pytest tests/test_market_context_economic_cycle.py::test_cycle_component_has_collapsed_monthly_signal_usage_guide -q`

Expected: `cycle-usage-guide`가 없어 assertion failure가 발생한다.

- [x] **Step 3: React 구조와 문구 구현**

`MonthlySignalGuide`는 다음 구조를 만든다.

```tsx
<details className="cycle-usage-guide">
  <summary>
    <div><span>Reading guide</span><strong>월별 사이클 신호 활용법</strong></div>
    <small>관찰 → 준비 → 조정 검토</small>
  </summary>
  <div className="cycle-guide-body">
    <div className="cycle-guide-steps">...</div>
    <div className="cycle-guide-phase-grid">...</div>
    <div className="cycle-guide-transition-grid">...</div>
    <p className="cycle-guide-boundary">...</p>
  </div>
</details>
```

`EconomicCycleWorkbench`에서 `market-implications` 다음과 `method-disclosure` 앞에 렌더링한다.

- [x] **Step 4: 연한 블록 배경과 반응형 CSS 구현**

- expander는 기존 패널과 같은 흰 배경·둥근 테두리를 사용한다.
- 회복·확장·둔화·침체 카드는 각각 연한 파랑·초록·주황·빨강 배경을 사용한다.
- 760px 이하에서 3열·2열 그리드를 모두 1열로 바꾼다.
- summary와 카드 본문은 줄바꿈을 허용한다.

- [x] **Step 5: 테스트와 정적 빌드 확인**

Run: `uv run --with pytest python -m pytest tests/test_market_context_economic_cycle.py -q`

Expected: focused test file이 모두 통과한다.

Run: `npm --prefix app/web/streamlit_components/economic_cycle_workbench run build`

Expected: Vite build가 exit code 0으로 완료되고 `component_static/`이 갱신된다.

- [x] **Step 6: 브라우저 QA와 커밋**

- 데스크톱에서 기본 닫힘, 펼침 내용, 가로 넘침 부재를 확인한다.
- 모바일 viewport에서 1열 재배치와 summary 줄바꿈을 확인한다.
- QA 스크린샷은 generated artifact로 남기고 커밋하지 않는다.
- 관련 파일만 stage해 `경제사이클 월별 신호 활용 가이드 추가`로 커밋한다.
