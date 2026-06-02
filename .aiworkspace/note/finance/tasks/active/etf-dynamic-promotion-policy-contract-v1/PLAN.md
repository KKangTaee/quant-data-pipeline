# ETF Dynamic Promotion Policy Contract V1

## Goal

GRS / GTAA / Risk Parity / Dual Momentum 같은 ETF 동적 전략의 Backtest Analysis source contract에 promotion policy metadata가 자연스럽게 포함되도록 고친다.

## 이걸 하는 이유?

Fresh 실행 결과가 충분하고 `net_cagr_spread`가 계산되어도 `promotion_min_net_cagr_spread` 같은 policy threshold가 source contract에 없으면 Backtest Realism Audit의 `Net performance policy`가 `REVIEW`로 남고, Practical Validation selected-route preflight / Final Review selected-route gate가 차단된다. Gate를 완화하지 않고 source contract를 올바르게 완성해야 한다.

## Scope

- ETF 동적 전략 runtime 기본 promotion policy 필드 보강
- Single Backtest execution dispatch, Compare defaults / override, Practical Validation replay 경로에서 같은 필드 보존 확인
- Backtest Realism / Final Review selected-route gate는 완화하지 않음
- 기존 registry / saved row migration 없음
- live approval, broker/account, order, auto rebalance 변경 없음

## Stop Condition

- Fresh GRS Liquid Macro Top2 실행 meta/source contract에 `promotion_min_net_cagr_spread` 포함
- Practical Validation replay PASS와 selected-route preflight `select_ready` 확인
- Final Review selected-route policy `select_allowed=True` / Ready 확인
- turnover/net cost proof 부족 회귀 후보는 여전히 blocked 확인
- focused compile / service tests 통과 또는 미실행 사유 기록
