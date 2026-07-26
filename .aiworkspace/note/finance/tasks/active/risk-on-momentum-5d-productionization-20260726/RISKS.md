# Risk-On Momentum 5D Productionization Risks

State: complete
Last Updated: 2026-07-26

## Resolved In This Task

| Risk | Required Handling |
|---|---|
| Hot-path rewrite changes D+1 timing or trade ordering | Full result / trade / scanner / metrics parity test PASS |
| Reduced default random count weakens research evidence | Standard / Deep 분리와 actual intensity / iteration meta 기록 완료 |
| Reused prepared data leaks state between variants | Immutable prepared object와 independent RNG / portfolio state contract PASS |
| Generic Practical Validation misreads daily swing | Daily Swing 전용 module과 compact evidence 구현 |
| Raw artifact path is mistaken for durable evidence | compact metadata/count만 handoff하고 raw rows는 generated artifact에 유지 |
| Production label enables an unsafe CTA | missing evidence fail-closed, Final Review selected-route policy 연결 |
| Monitoring is mistaken for trading automation | manual review / stale / no-order / no-rebalance policy 구현 |
| 60-second target is not reached | actual DB 2년 Standard `21.247s`로 충족 |

## Remaining Explicit Limitations

- Top1000/S&P500 current membership을 과거 날짜에도 적용하므로 historical PIT membership과 delisting coverage는 미검증이다. 제품은 이를 `REVIEW`로 표시하며 사실처럼 숨기지 않는다.
- broader combined suite의 current-date market sentiment overlay 2건은 이번 변경 파일 밖의 expectation drift다.
- `.venv`에 `pytest`가 없어 pytest-only settings test module은 직접 실행하지 못했다. 동일 schema와 payload는 unittest service contract로 검증했다.
