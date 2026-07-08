# Backtest Handoff Entry Gate Queue V1

## 이걸 하는 이유?

`2차 실전성 검증 Handoff`가 `진입 준비도 5.0 / 10`과 `Promotion review`를 함께 보여주면서, 사용자가 2차로 보낼 수 있는데도 1차에서 덜 통과한 것처럼 읽혔다. 1차 Backtest Analysis에서 확인할 source 등록 기준과 2차 Practical Validation에서 확인할 review queue를 화면에서 분리한다.

## 범위

- `app/web/backtest_result_display.py`: Handoff state를 1차 진입 기준 / 먼저 해결 blocker / 2차 확인 큐 중심으로 재구성한다.
- `app/web/components/backtest_handoff_action/`: React Handoff card props에서 readiness score를 제거하고 entry cards를 표시한다.
- `tests/test_service_contracts.py`: hold 후보가 1차 blocker가 아니라 2차 review queue로 표시되는 계약을 검증한다.
- `docs/flows/`: Backtest / Portfolio Selection flow 문서의 Handoff 의미를 갱신한다.

## 완료 조건

- Handoff card에 `진입 준비도 5.0 / 10`이 노출되지 않는다.
- `promotion_decision=hold`는 1차 source 등록 blocker가 아니라 2차 확인 큐로 전달된다.
- React card 안의 버튼은 기존처럼 Practical Validation current selection source 등록만 수행한다.
- registry / saved setup / strategy runtime / gate threshold는 변경하지 않는다.
