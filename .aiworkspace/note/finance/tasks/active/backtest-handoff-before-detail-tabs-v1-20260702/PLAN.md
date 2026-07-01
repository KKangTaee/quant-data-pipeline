# Plan

## 이걸 하는 이유?

Run Backtest 직후 결과 화면에서 상세 결과 탭을 모두 지난 뒤에 `2차 실전성 검증 Handoff`가 나오면, 사용자가 다음 행동을 늦게 발견한다.
핵심 성과와 데이터 기준을 확인한 직후 바로 "이 결과를 2차 검증으로 보낼 수 있는가"를 판단하고, 상세 탭은 이후 근거 확인으로 읽는 편이 흐름이 자연스럽다.

## Scope

- `app/web/backtest_result_display.py`
  - latest run 렌더 순서를 `결과 헤더 -> 데이터 기준 요약 -> 2차 실전성 검증 Handoff -> 상세 결과 탭`으로 변경한다.
- `tests/test_service_contracts.py`
  - latest run 화면 순서 계약을 새 흐름으로 고정한다.
- `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
  - durable Backtest UI flow 문서를 현재 기준으로 갱신한다.

## Non-Scope

- Handoff scoring / gate rule, Practical Validation registry write, result bundle schema, strategy runtime, Data Trust 계산 모델은 변경하지 않는다.
