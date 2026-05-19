# Practical Validation Service Boundary Plan

Status: Complete
Created: 2026-05-20

## 이걸 하는 이유?

Practical Validation은 현재 화면 렌더, 검증 profile 입력, runtime recheck, provider gap 보강, result 저장, Final Review 이동 준비가 한 흐름에 붙어 있다.
UI와 engine 책임을 분리하려면 먼저 Streamlit 없이 호출 가능한 Practical Validation application service를 만들고, 화면은 입력 / 버튼 / session state만 맡도록 줄여야 한다.

이 task는 Practical Validation 전체를 한 번에 재작성하지 않고, result 생성 / 저장 / Final Review handoff contract부터 service boundary로 옮기는 첫 단계다.

## Scope

포함:

- Streamlit-free Practical Validation service module 생성
- Practical Validation result 생성 호출을 service boundary로 감싸기
- Practical Validation result 저장을 service가 담당
- Final Review handoff payload / notice 생성은 service가 담당하고, Streamlit session state 반영은 UI가 담당
- Backtest Analysis / Compare / Candidate Review에서 Practical Validation source로 보내는 handoff contract도 service가 담당
- 기존 `PASS / REVIEW / BLOCKED / NOT_RUN` 의미와 registry append 경로 유지

제외:

- 12개 diagnostic 계산식 변경
- provider / macro loader fetch path 변경
- provider gap 수집 버튼의 job orchestration 분리
- Final Review 화면 구조 변경
- registry JSONL schema 변경

## Done Criteria

- 새 service module이 Streamlit을 import하지 않는다.
- `app/web/backtest_practical_validation_helpers.py`가 Streamlit session state를 직접 만지지 않는다.
- `app/web/backtest_practical_validation.py`는 저장 / handoff domain contract를 service에 위임하고 session state 반영만 수행한다.
- `NOT_RUN` 상태와 blocked handoff disable 조건이 유지된다.
- compile / import smoke / no-Streamlit check가 통과한다.
