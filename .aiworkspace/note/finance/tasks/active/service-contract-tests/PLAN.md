# Service Contract Tests Plan

Created: 2026-05-20

## 이걸 하는 이유?

UI와 engine/service 경계를 분리해도, UI가 기대하는 반환 payload 형태가 흔들리면 다음 작업자가 다시 UI 내부 구현에 의존하게 된다.
이번 작업은 DB나 Streamlit 화면을 실행하지 않고도 service boundary의 핵심 contract를 검증하는 작은 회귀 테스트를 추가한다.

## Scope

- `app/services/backtest_practical_validation.py`의 Practical Validation / Final Review handoff contract 검증
- `app/services/backtest_evidence_read_model.py`의 Final Review status / table / evidence row contract 검증
- Streamlit import가 service import 과정에서 끌려오지 않는지 검증
- 실행 가능한 focused unittest 명령을 runbook에 남김

## Out Of Scope

- 실제 provider / DB / strategy runtime 실행
- Streamlit 화면 interaction 테스트
- pytest 도입 또는 test framework 전환
- service-to-`app.web` transitional import 제거

## Exit Criteria

- 표준 `unittest` 기반 service contract 테스트가 통과한다.
- UI / engine boundary lint가 계속 통과한다.
- task 문서, runbook, root handoff log가 현재 검증 명령을 가리킨다.
