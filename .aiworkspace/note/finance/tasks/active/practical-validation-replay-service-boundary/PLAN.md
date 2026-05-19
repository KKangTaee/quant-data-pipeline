# Practical Validation Replay Service Boundary Plan

Created: 2026-05-20

## 이걸 하는 이유?

Practical Validation 화면은 재검증 방식 선택, 실행 버튼, 결과 표시를 맡으면 충분하다.
기존 strategy runtime으로 source를 다시 실행할 기간을 계산하고 실제 replay를 만드는 로직은 UI보다 service / engine 경계에 가까우므로,
다음 UI 프레임워크로 바꿔도 재사용 가능하도록 service layer로 옮긴다.

## Scope

- `app/web/backtest_practical_validation_replay.py`를 service module로 이동
- `app/web/backtest_practical_validation.py`의 replay import를 service module로 변경
- replay plan contract를 `tests/test_service_contracts.py`에 추가
- 관련 project map / script map / flow 문서 갱신

## Out Of Scope

- replay runtime 로직 자체 변경
- strategy runner / DB loader 변경
- replay 결과 UI layout 변경
- `app.services -> app.web.runtime` transitional import debt 제거

## Exit Criteria

- Practical Validation UI는 replay helper를 `app.services`에서 import한다.
- replay service import가 Streamlit을 로드하지 않는다.
- focused service contract tests, compile, boundary lint가 통과한다.
