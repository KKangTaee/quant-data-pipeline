# Final Review Pass Candidate Search 20260601

## Goal

Final Review selected-route를 통과하는 fresh portfolio / strategy 후보를 다시 탐색한다.

## 이걸 하는 이유?

ETF dynamic promotion policy source contract가 보강됐으므로 이전에 `promotion_min_net_cagr_spread` 누락으로 막혔던 후보가 현재 gate에서 통과하는지 확인해야 한다. 탐색 결과는 실제 투자 승인이나 주문이 아니라 Final Review selected-route readiness 확인이다.

## Scope

- Backtest Analysis runtime fresh 실행 결과를 사용한다.
- Practical Validation stored-period replay와 selected-route preflight를 확인한다.
- Final Review investability packet과 selected-route gate readiness를 확인한다.
- Registry / saved row migration이나 append는 하지 않는다.
- live approval, broker/account, order, auto rebalance는 범위 밖이다.

## Stop Condition

- 최소 1개 통과 후보를 확인하거나, 주요 후보군이 왜 막히는지 요약한다.
- 실행 기간, universe, 핵심 성과, replay / preflight / Final Review gate 결과를 기록한다.
- 생성/변경된 local artifact를 커밋하지 않는다.
