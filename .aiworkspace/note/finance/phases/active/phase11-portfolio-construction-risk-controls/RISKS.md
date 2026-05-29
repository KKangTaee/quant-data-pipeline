# Phase 11 Portfolio Construction Risk Controls Risks

Status: Active
Created: 2026-05-29

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Component weights look diversified but risk contribution is concentrated | 실전 포트폴리오가 한 risk source에 과도하게 의존 | correlation / volatility contribution evidence를 별도 contract로 분리 |
| Holdings overlap is missing or partial | ETF 여러 개가 같은 top holdings에 중복 노출될 수 있음 | DB provider holdings / exposure source map 후 coverage 부족을 `REVIEW` 또는 `NEEDS_INPUT`으로 표시 |
| Construction gate duplicates earlier validation gates | 같은 blocker를 여러 이름으로 반복 표시 | 11-1 source map에서 stage ownership과 source-of-truth를 먼저 정리 |
| Profile thresholds are arbitrary | 방어형 / 성장형 / 전술형 기준이 사용자 기대와 충돌 | profile-aware threshold를 문서화하고 service contract로 고정 |
| Storage sprawl returns | raw holdings / matrix / memo-like 저장이 늘어남 | compact evidence read model 우선, raw data는 DB / runtime boundary로 제한 |
| User confuses construction gate with live trading approval | 검증 화면이 주문 승인처럼 보일 수 있음 | Final Review / Selected Dashboard는 live approval, order, rebalance가 아님을 유지 |

## Residual Unknowns For 11-1

- 현재 source별 component curve가 모든 후보 유형에서 risk contribution 계산에 충분한지 확인이 필요하다.
- holdings / exposure snapshot coverage가 construction risk audit PASS 후보로 쓰기에 충분한지 확인이 필요하다.
- current Practical Diagnostics의 concentration / correlation proxy와 Phase 11 신규 contract의 ownership 분리가 필요하다.
