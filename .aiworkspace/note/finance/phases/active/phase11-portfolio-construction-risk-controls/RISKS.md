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

## Residual Unknowns After 11-1

- holdings / exposure snapshot coverage는 후보마다 달라질 수 있으므로 11-2에서 partial / missing provider evidence를 `PASS`로 올리지 않아야 한다.
- current concentration / exposure proxy는 fallback으로만 써야 하며, source strength를 row에 표시해야 한다.
- 11-2는 완료됐고, provider missing / partial evidence는 `CONSTRUCTION_RISK_NEEDS_INPUT` 또는 `CONSTRUCTION_RISK_REVIEW`로 남긴다.
- component curve가 없는 후보는 11-3 risk contribution에서 `NEEDS_INPUT` 또는 `REVIEW`로 남겨야 한다.
- component role metadata의 canonical source는 아직 없으므로 11-4에서 먼저 결정해야 한다.
- Final Review gate group은 11-5까지 `provider_coverage` / `stress_robustness`에 흩어져 있으므로 construction risk ownership을 명확히 해야 한다.
