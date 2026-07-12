# Design

## Problem

현재 Practical Validation은 수집 가능한 provider gap이 `REVIEW`이면 `READY_WITH_REVIEW`로 Final Review 이동을 허용한다. Final Review는 최신 코드로 같은 저장 evidence의 collection plan을 다시 계산해 보강 패널을 표시하므로, 해결 가능한 2단계 작업이 3단계 사용자 부담으로 되돌아온다.

## Decision

- 실행 가능한 필수 provider gap은 Practical Validation 승격 전 blocker다.
- 수집으로 해결되지 않는 제한만 residual REVIEW로 Final Review에 전달한다.
- 수집 성공은 검증 성공이 아니며, Flow 2 재검증과 새 결과 저장이 완료돼야 새 Final Review 후보가 된다.
- Final Review의 데이터 보강 action은 현재 정상 흐름이 아니라 legacy / stale 저장 결과 복구용이다.

## Stage Ownership

| Stage | Owns | Does not own |
|---|---|---|
| Practical Validation | provider plan, explicit collection, recheck, Gate, validation save | 최종 선택 사유 |
| Final Review | residual limitation acceptance, select/hold/reject/re-review, Monitoring condition | provider fetch, Practical Validation recomputation |
| Portfolio Monitoring | selected candidate follow-up and freshness observation | live approval, broker order, auto rebalance |

## Tradeoff

모든 수집 가능 gap을 무조건 blocker로 만들면 provider 장애가 승격을 영구 차단할 수 있다. 따라서 이번 v1은 기존 Python plan이 실제 실행 가능하다고 판정한 항목만 blocker로 사용하고, 수집 실패는 Practical Validation에서 실패 근거와 재시도 / source mapping 상태로 남긴다.
