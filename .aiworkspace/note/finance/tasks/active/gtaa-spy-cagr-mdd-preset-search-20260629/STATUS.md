# Status

Status: Complete

## 완료

- 기존 `GTAA SPY Low-MDD Style Top-3`는 최신 runtime 기준 성과 조건은 통과하지만, 기본 20M ADV 필터에서는 `liquidity_policy_status=watch`로 `production_candidate`에 머문다는 점을 확인했다.
- 제한 sweep 결과, `GTAA SPY Low-MDD Style Top-2 ADV20` 후보가 성과 조건과 현재 1차 promotion gate를 모두 통과했다.
- GTAA runtime / strategy path에 `Min Avg Dollar Volume 20D` evidence를 연결해 liquidity clean coverage가 실제 policy 판단에 반영되도록 했다.
- `GTAA SPY Low-MDD Style Top-2 ADV20` preset을 추가하고, 선택 시 `top=2`, `interval=4`, `Score=1M/6M`, `MA200`, `cash_only`, `Benchmark=SPY`, `Min ADV20D=20M`이 자동 적용되도록 했다.

## 대표 후보

| 항목 | 값 |
|---|---|
| Preset | `GTAA SPY Low-MDD Style Top-2 ADV20` |
| Universe | `QQQ, SOXX, MTUM, QUAL, USMV, IAU, IEF, TLT` |
| Settings | `top=2`, `interval=4`, `Score=1M/6M`, `MA200`, `cash_only`, `Min ADV20D=20M`, `Benchmark=SPY` |
| Result window | `2016-01-29` to `2026-02-27` |
| CAGR / MDD / Sharpe | `24.078108%` / `-9.990100%` / `3.373899` |
| SPY CAGR / MDD / Sharpe | `13.363791%` / `-20.610791%` / `2.214603` |
| Promotion | `real_money_candidate` |
| Shortlist / Deployment | `paper_probation` / `small_capital_ready` |
| Policy status | benchmark / validation / liquidity / guardrail / ETF operability all `normal` |

## 남은 일

- 3차 Practical Validation / Final Review 연결은 사용자가 원할 때 별도 진행한다.
