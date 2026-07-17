# Economic Cycle Evidence Linkage Copy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 사이클맵의 현재점과 미래 점선에 연결되는 근거를 Evidence 패널 문구만으로 구분하게 한다.

**Architecture:** 기존 React 컴포넌트의 데이터 분기와 레이아웃은 유지한다. 소스 계약 테스트로 사용자 문구를 고정한 뒤 제목과 부제를 교체하고 Vite 정적 번들을 재생성한다.

**Tech Stack:** Python pytest source-contract test, React 18, TypeScript, Vite

## Global Constraints

- 모델 입력, 확률, 좌표 계산, payload schema는 변경하지 않는다.
- 화면 구조와 스타일은 변경하지 않는다.
- 현재 근거와 미래 추가 근거의 역할만 더 명시적으로 표현한다.

---

### Task 1: Evidence 역할 문구 명확화

**Files:**
- Modify: `tests/test_market_context_economic_cycle.py`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`
- Regenerate: `app/web/streamlit_components/economic_cycle_workbench/component_static/`

**Interfaces:**
- Consumes: 기존 `realEvidence`와 `forecastEvidence` 배열
- Produces: 현재점 입력과 미래 추가 입력을 구분하는 Evidence 패널 문구

- [x] **Step 1: 문구 계약 테스트 작성**

`test_cycle_component_source_contract_covers_full_reading_flow`에 다음 문자열을 요구한다.

```python
for token in (
    "현재와 전망의 판단 근거",
    "현재 위치의 근거",
    "현재점에 반영되는 생산·소비와 고용·소득",
    "1·2개월 전망에 추가되는 근거",
    "현재 근거에 더해 미래 확률을 조정하는 금융·선행 여건과 물가·정책",
):
    assert token in source
```

- [x] **Step 2: 실패 확인**

Run: `.venv/bin/python -m pytest tests/test_market_context_economic_cycle.py::test_cycle_component_source_contract_covers_full_reading_flow -q`

Expected: 새 문구가 아직 없어 assertion failure가 발생한다.

- [x] **Step 3: React 문구 최소 수정**

Evidence 패널을 다음 문구로 렌더링한다.

```tsx
<h3 id="evidence-title">현재와 전망의 판단 근거</h3>
<EvidenceGroup title="현재 위치의 근거" subtitle="현재점에 반영되는 생산·소비와 고용·소득" rows={realEvidence} />
<EvidenceGroup title="1·2개월 전망에 추가되는 근거" subtitle="현재 근거에 더해 미래 확률을 조정하는 금융·선행 여건과 물가·정책" rows={forecastEvidence} />
```

- [x] **Step 4: 테스트와 빌드 확인**

Run: `.venv/bin/python -m pytest tests/test_market_context_economic_cycle.py -q`

Expected: 모든 테스트가 통과한다.

Run: `npm run build`

Working directory: `app/web/streamlit_components/economic_cycle_workbench`

Expected: Vite build가 exit code 0으로 완료되고 `component_static/`이 갱신된다.

- [x] **Step 5: 브라우저 QA와 커밋**

`http://localhost:8501/`의 경제 사이클 탭에서 새 제목·부제가 표시되고 잘림이나 겹침이 없는지 확인한다. 관련 파일만 stage해 `경제사이클 근거 역할 문구 명확화`로 커밋한다.
