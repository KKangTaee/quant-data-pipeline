# Backtest Second Stage Visibility V1

## 이걸 하는 이유?

Backtest Analysis의 Data Trust / Handoff 영역이 2차 Practical Validation에서 확인해야 할 review focus를 1차 화면의 상세 검토 목록처럼 보여 주고 있었다. 사용자는 1차에서 이미 끝난 기준과 2차에서 이어 확인할 기준을 명확히 구분해야 한다.

## 범위

- `app/web/backtest_result_display.py`: Data Trust warning 표시와 Handoff / Policy Signal handoff 문구를 정리한다.
- `tests/test_service_contracts.py`: `meta["warnings"]`가 1차 상세 issue card로 펼쳐지지 않고 2차 전달 count로 남는지 검증한다.
- `.aiworkspace/note/finance/docs/flows/`: Backtest / Portfolio Selection flow에서 1차와 2차 표시 위치를 갱신한다.

## 완료 조건

- Backtest Analysis Data Trust는 가격 기준, 계산 기준일, 제외 종목, 결측 row 같은 1차 data readability만 상세 표시한다.
- `meta["warnings"]` 기반 실전성 review focus는 Backtest Analysis에서 개수 / 위치 안내만 남기고 상세 row로 펼치지 않는다.
- Practical Validation `Backtest에서 넘어온 2차 확인 항목`은 기존처럼 상세 review queue를 받는다.
- source registration, registry / saved setup, strategy runtime, gate threshold는 변경하지 않는다.
