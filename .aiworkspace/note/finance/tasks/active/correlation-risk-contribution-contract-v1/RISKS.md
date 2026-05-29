# Correlation / Risk Contribution Contract V1 Risks

Status: Complete
Created: 2026-05-29

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| DB price proxy curves look stronger than runtime replay | 실제 전략 path와 다른 risk estimate를 과신 | source strength를 표시하고 proxy / mixed source는 REVIEW로 둔다 |
| Volatility contribution proxy is mistaken for full risk budget | covariance contribution을 계산한 것처럼 오해 | row evidence와 limitation에 proxy임을 명시 |
| Missing component curves pass through | 구성 리스크 판단이 비어도 선정 가능해 보임 | missing matrix / NOT_RUN dependency는 `NEEDS_INPUT`으로 고정 |

## Residual

- V1 is a proxy contract. Full covariance / marginal contribution optimization remains out of scope.
- Selected-route gate policy enforcement remains Phase 11 task 11-5.
