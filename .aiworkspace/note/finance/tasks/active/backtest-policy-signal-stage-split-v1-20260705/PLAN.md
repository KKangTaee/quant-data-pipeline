# Backtest Policy Signal Stage Split V1

## 이걸 하는 이유?

Backtest Analysis의 `검증 기준 상세`가 1차에서 확인할 항목과 Practical Validation에서 확인할 review 항목을 같은 보드에 섞어 보여주면서, 사용자가 지금 화면에서 끝내야 할 판단을 읽기 어려웠다.

## 범위

- `app/services/backtest_handoff_readiness.py`: policy signal row에 1차 표시 / 2차 전달 stage와 설명 필드를 추가한다.
- `app/web/backtest_result_display.py`: Backtest Analysis의 Policy Signals 보드를 1차 확정 항목 중심으로 렌더링한다.
- `app/web/components/backtest_policy_signal_board/`: 1차 기준 보드용 React custom component를 추가한다.
- `app/web/backtest_practical_validation/page.py`: 2차 review queue 카드가 확인할 내용을 같이 표시하게 한다.
- `tests/test_service_contracts.py`: stage 분리와 React component 연결 계약을 검증한다.

## 완료 조건

- Backtest Analysis는 1차에서 통과 / 차단 여부를 확인할 수 있는 항목만 자세히 보여준다.
- 2차 review 항목은 Backtest Analysis에서 count / group handoff만 보이고, Practical Validation에서 상세 확인한다.
- React component는 UI-only이며 Python service가 gate math와 persistence를 계속 소유한다.
- Python compile, focused service contract tests, component build, Browser QA를 통과한다.
