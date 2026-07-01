# Backtest Latest Run Cleanup V1

## 이걸 하는 이유?

Run Backtest 직후 화면이 실행 전 payload summary와 결과 해석 guide를 먼저 보여주면서, 사용자가 실제 결과 metric / chart / 근거 탭으로 바로 들어가기 어렵다.

## Scope

- `Execution Summary`와 `Developer Payload` 기본 노출 제거
- `Latest Backtest Run` 상단의 checkpoint / availability guide 제거
- `Selection History`, `Dynamic Universe`, `Policy Signal Meta`는 조건부 결과 근거 탭으로 유지
- Strategy runtime, result bundle, run history, registry / saved persistence는 변경하지 않음

## Completion Criteria

- Run Backtest 직후 결과 화면이 `Data Trust Summary -> metrics -> next action -> tabs` 흐름으로 읽힌다.
- Guide card / payload preview가 기본 결과 화면에 보이지 않는다.
- Focused contract, py_compile, UI QA를 통과한다.
