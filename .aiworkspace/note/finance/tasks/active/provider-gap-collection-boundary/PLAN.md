# Provider Gap Collection Boundary Plan

Created: 2026-05-20

## 이걸 하는 이유?

Practical Validation 화면은 provider gap을 보여주고 버튼을 제공해야 하지만,
어떤 ETF / macro 데이터를 수집할지 결정하고 ingestion job을 순서대로 실행하는 책임까지 UI 파일에 있으면 UI와 engine/service 경계가 다시 흐려진다.
이번 작업은 provider gap collection 계획과 실행을 service boundary로 옮겨, UI는 표시와 session state 반영만 맡게 한다.

## Scope

- `app/web/backtest_practical_validation.py`의 provider gap plan / source map lookup / ingestion job orchestration을 service로 이동
- `app/services/backtest_practical_validation.py`에 UI-neutral provider gap row / plan / run contract 추가
- 기존 버튼, session state key, run history append behavior 유지
- service contract test에 provider gap plan / run orchestration 검증 추가

## Out Of Scope

- ETF provider connector 자체 수정
- DB schema / loader 변경
- provider gap UI layout 개편
- `app.services -> app.web` transitional import 제거

## Exit Criteria

- Practical Validation UI에서 provider gap section이 service function을 호출한다.
- provider gap collection service는 Streamlit import 없이 동작한다.
- focused unittest, py_compile, UI-engine boundary lint가 통과한다.
