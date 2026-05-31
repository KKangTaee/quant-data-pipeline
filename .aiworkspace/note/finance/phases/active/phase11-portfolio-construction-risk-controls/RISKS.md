# Phase 11 Portfolio Construction Risk Controls Risks

Status: Complete
Created: 2026-05-29

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Component weights look diversified but risk contribution is concentrated | 실전 포트폴리오가 한 risk source에 과도하게 의존 | 완료: `risk_contribution_audit_v1`에서 correlation / volatility contribution proxy를 별도 row로 표시 |
| Holdings overlap is missing or partial | ETF 여러 개가 같은 top holdings에 중복 노출될 수 있음 | DB provider holdings / exposure source map 후 coverage 부족을 `REVIEW` 또는 `NEEDS_INPUT`으로 표시 |
| Construction gate duplicates earlier validation gates | 같은 blocker를 여러 이름으로 반복 표시 | 완료: 11-5에서 construction risk, risk contribution, component role / weight를 first-class gate groups로 분리 |
| Profile thresholds are arbitrary | 방어형 / 성장형 / 전술형 기준이 사용자 기대와 충돌 | 완료: `component_role_weight_audit_v1`에서 profile-aware max weight와 role concentration line을 표시 |
| Storage sprawl returns | raw holdings / matrix / memo-like 저장이 늘어남 | compact evidence read model 우선, raw data는 DB / runtime boundary로 제한 |
| User confuses construction gate with live trading approval | 검증 화면이 주문 승인처럼 보일 수 있음 | Final Review / Selected Dashboard는 live approval, order, rebalance가 아님을 유지 |

## Residual Unknowns After 11-1

- holdings / exposure snapshot coverage는 후보마다 달라질 수 있으므로 11-2에서 partial / missing provider evidence를 `PASS`로 올리지 않아야 한다.
- current concentration / exposure proxy는 fallback으로만 써야 하며, source strength를 row에 표시해야 한다.
- 11-2는 완료됐고, provider missing / partial evidence는 `CONSTRUCTION_RISK_NEEDS_INPUT` 또는 `CONSTRUCTION_RISK_REVIEW`로 남긴다.
- component curve가 없는 후보는 11-3 risk contribution에서 `NEEDS_INPUT` 또는 `REVIEW`로 남긴다.
- component role metadata는 11-4에서 existing `proposal_role` / `weight_reason` source를 읽는 read-only contract로 분리했다.
- 11-5에서 Final Review gate group ownership을 `construction_risk`, `risk_contribution`, `component_role_weight`로 명확히 했다.
- 11-6 integrated QA / closeout에서 전체 검증과 phase 종료 기록을 정리했다.

## Residual After Closeout

- Phase 11 does not implement a full optimizer, issuer / sector taxonomy engine, covariance model, or broker-grade construction platform.
- Construction risk thresholds are compact evidence heuristics and may need profile-specific tuning.
- Provider holdings / exposure and component return matrix quality still depend on DB-backed source availability.
- Next hardening target is Phase 12 selected monitoring / recheck operations.
