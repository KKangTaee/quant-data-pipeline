# Status

## 2026-07-05

- V1 complete.
- `build_policy_signal_inventory()` row에 `plain_explanation`, `checked_items`를 추가했다.
- React `BacktestPolicySignalBoard`를 1차 category board와 click help UI로 개편했다.
- Backtest Analysis React board는 2차 review queue 상세 list를 렌더링하지 않고 `secondStageCount` / handoff notice만 표시한다.
- Practical Validation source snapshot이 새 설명 필드를 보존하도록 compact key를 확장했다.
- Browser QA에서 Equal Weight 실행 후 `검증 신호 · Policy Signals` 탭의 새 category board와 `Liquidity Policy` help expand를 확인했다.
- QA screenshot: `backtest-policy-signal-help-board-v1-qa.png`
