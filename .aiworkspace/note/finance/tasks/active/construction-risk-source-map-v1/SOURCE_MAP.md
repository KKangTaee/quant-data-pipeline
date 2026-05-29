# Construction Risk Source Map V1

Status: Complete
Created: 2026-05-29

## Summary

현재 프로젝트에는 Phase 11의 1차 구현에 필요한 재료가 이미 있다.

핵심 gap은 data 부재보다 ownership 부재다. concentration / overlap / exposure는 Practical Validation diagnostics와 provider look-through board에 존재하지만, Final Review selected-route에서 독립적인 construction risk gate로 드러나지 않는다. correlation / risk contribution과 drop-one / weight tilt도 Robustness Lab에 존재하지만 construction risk contract로 분리되어 있지 않다.

따라서 다음 구현은 새 저장 기능이 아니라 기존 compact evidence를 읽는 `Construction Risk Audit` read model부터 시작한다.

## Current Evidence Sources

| Evidence Area | Current Source | Existing Strength | Gap | Candidate Owner |
| --- | --- | --- | --- | --- |
| Selection source / target weights | `app/services/backtest_practical_validation_diagnostics.py` `build_practical_validation_result()` active components and `Target weight total` input check | source id, active component count, target weight total hard blocker already exist | role / weight discipline은 아직 total 100%와 max weight 중심이고, component role 근거가 first-class가 아님 | 11-4 role / weight discipline |
| Component concentration | `build_practical_validation_result()` concentration diagnostic uses max component weight, duplicate benchmark count, proxy flag exposure | 현재 Practical Validation domain `concentration_overlap_exposure`가 있음 | provider holdings가 없으면 proxy PASS를 REVIEW로 내리지만 construction risk gate group은 별도 없음 | 11-2 concentration / overlap / exposure |
| Ticker / proxy exposure | `_build_exposure_summary()` and `PRIMARY_TICKER_BUCKETS` / sector / leveraged / inverse ticker sets | holdings 없이도 rough asset / theme / leverage exposure를 산출 | ticker token 기반이라 PASS 근거로는 약함. provider coverage 없으면 proxy로만 표시해야 함 | 11-2 fallback evidence |
| DB asset exposure look-through | `app/services/backtest_practical_validation_provider_context.py` `_build_exposure_context()` | ETF exposure snapshot을 target weight 기준 asset bucket으로 합산 | 1차 ETF exposure 기준이며 ETF-of-ETF 2차 underlying expansion은 후속 | 11-2 strong evidence path |
| DB holdings overlap | `backtest_practical_validation_provider_context.py` `_build_holdings_context()` | top holding weight, top overlap weight, overlap count, holdings coverage 계산 | full holdings는 DB에 있고 validation에는 compact top rows만 있음. issuer / sector overlap은 아직 분리되지 않음 | 11-2 strong evidence path |
| Look-through board | `_build_look_through_board()` | holdings coverage, exposure coverage, top holding, top overlap, dominant asset, unknown exposure를 compact board로 제공 | provider coverage board이지 construction risk audit / gate group이 아님 | 11-2 read model input |
| Correlation / risk contribution | `app/services/backtest_practical_validation_stress_sensitivity.py` `_correlation_risk_evidence()` | component monthly return matrix, average / max correlation, volatility-weighted risk contribution proxy 계산 | raw matrix는 저장하지 않음. source strength와 selected-route severity가 construction risk로 분리되지 않음 | 11-3 risk contribution contract |
| Drop-one dependency | `_sensitivity_rows()` drop-one scenarios and `_sensitivity_interpretation_result()` component dependency row | 특정 component 제거 시 CAGR / MDD delta를 compact row로 제공 | Robustness evidence로 표시되며 component role / concentration 판단과 연결이 약함 | 11-3 and 11-4 |
| Weight tilt dependency | `_sensitivity_rows()` mix weight +5%p scenarios | 비중이 약간 바뀔 때 결과가 얼마나 흔들리는지 계산 | weight discipline 기준과 drift / rebalance policy로 연결되지 않음 | 11-4 |
| Final Review selected-route gate | `app/services/backtest_evidence_read_model.py` `GATE_POLICY_DOMAIN_GROUPS` | current domains route to provider coverage or stress robustness | `construction_risk` group이 없어서 구성 리스크가 provider / robustness 하위 신호로 흩어짐 | 11-5 gate policy |

## Stage Ownership

| Stage | Current Role | Construction Risk Gap |
| --- | --- | --- |
| Backtest Analysis / Compare | candidate source, components, target weights, benchmark, replay contract 제공 | component role과 intended risk budget이 구조화되어 있지 않음 |
| Practical Validation | asset allocation, concentration / overlap / exposure, correlation / risk contribution diagnostics 계산 | construction risk audit으로 독립 요약되지 않음 |
| Provider Context / Look-through Board | DB holdings / exposure / operability / macro snapshot을 compact board로 제공 | provider coverage board이므로 selected-route construction risk severity가 별도 없음 |
| Robustness Lab | stress, rolling, sensitivity, overfit, drop-one, weight tilt evidence 제공 | construction dependency와 role discipline이 robustness bucket에 섞여 있음 |
| Final Review | evidence packet and gate policy로 selected-route 가능 여부 판단 | construction risk가 `provider_coverage` / `stress_robustness`로 흩어져 있어 의사결정 근거가 약함 |
| Selected Portfolio Dashboard | 선택된 후보의 monitoring / recheck / provider evidence를 read-only로 표시 | selected 이후에도 construction risk summary를 tracking view로 유지하는 contract가 아직 없음 |

## Gap Audit

| Gap | Severity | Reason | Recommended Fix |
| --- | --- | --- | --- |
| Construction risk group이 gate policy에 없음 | High | 구성 리스크 non-PASS가 provider / robustness 하위 근거로만 보이면 Final Review에서 약하게 보일 수 있음 | 11-5에서 `construction_risk` gate group 또는 동등한 group route를 추가 |
| Concentration / overlap / exposure evidence가 domain diagnostic과 look-through board에 분산 | High | 사용자는 top holding, overlap, dominant asset, unknown exposure를 한 화면 판단으로 봐야 함 | 11-2에서 read-only `Construction Risk Audit` row model로 통합 |
| Provider coverage 없는 경우 proxy PASS가 과신될 수 있음 | High | ticker / bucket proxy는 실전투자 PASS 근거로 부족 | 11-2에서 proxy-only 상태는 PASS가 아니라 REVIEW 또는 NEEDS_INPUT으로 명시 |
| Risk contribution이 volatility proxy 수준 | Medium | covariance / marginal contribution이 아니라 weight * vol 기반 proxy라 정밀 risk budget으로 보기 어려움 | 11-3에서 source strength와 limitation을 표시하고, 필요 시 covariance-based follow-up으로 분리 |
| Drop-one / weight tilt가 role / weight discipline과 분리됨 | Medium | 특정 component 의존성이 커도 역할 근거로 연결되지 않을 수 있음 | 11-4에서 component role, profile threshold, sensitivity row를 연결 |
| ETF-of-ETF 2차 look-through 없음 | Medium | 일부 ETF 내부 중복 노출을 과소평가할 수 있음 | 11-2에서는 limitation으로 남기고, 필요 시 DB provider expansion task로 별도 분리 |
| issuer / sector overlap이 holdings top overlap보다 좁음 | Medium | 같은 issuer / sector factor 집중을 놓칠 수 있음 | 11-2 V1은 holdings / asset bucket 중심, V2 후보로 issuer / sector grouping 정의 |

## Recommended Task Order

1. `concentration-overlap-exposure-contract-v1`
   - 기존 active components, `_build_exposure_summary()`, provider `look_through_board`를 읽어 concentration / overlap / exposure rows를 만든다.
   - full holdings 저장 없이 compact board rows만 사용한다.
   - provider holdings / exposure coverage가 없으면 `PASS`로 올리지 않는다.

2. `correlation-risk-contribution-contract-v1`
   - `_correlation_risk_evidence()`를 construction risk 관점으로 감싼다.
   - average / max correlation, max risk contribution, component count, monthly return rows, source strength를 표시한다.
   - missing component return matrix는 `NEEDS_INPUT` 또는 `REVIEW`로 둔다.

3. `component-role-weight-discipline-v1`
   - component role source가 어디에 있어야 하는지 확정한다.
   - max weight, hedge / diversifier / growth role, drop-one dependency, weight tilt sensitivity를 profile-aware row로 연결한다.

4. `construction-risk-gate-policy-v1`
   - Final Review selected-route gate에서 construction risk non-PASS가 명확히 blocker 또는 review-required로 표시되게 한다.
   - provider coverage / stress robustness와 중복될 경우 source row는 공유하되 group label은 construction risk로 보여준다.

## Storage Boundary

- 새 JSONL registry는 만들지 않는다.
- user memo, preset, comment, time log 저장은 만들지 않는다.
- full holdings, raw provider response, full return matrix, covariance matrix는 workflow artifact로 저장하지 않는다.
- raw provider / holdings / exposure는 DB 또는 loader boundary에 둔다.
- Practical Validation / Final Review에는 compact evidence rows, coverage, metric, status만 둔다.

## Test Scope For Next Implementation

For 11-2:

- provider look-through board PASS / REVIEW / NOT_RUN coverage 조합
- provider holdings missing이면 concentration audit이 PASS가 되지 않는지
- top holding or top overlap threshold 초과 시 REVIEW가 되는지
- unknown exposure가 있는 경우 REVIEW evidence row가 생기는지
- ticker proxy fallback은 source strength가 proxy로 표시되는지
- selected-route gate 연결은 11-5까지 보류하되, 11-2 contract는 gate-ready status를 제공하는지

Suggested checks:

- `.venv/bin/python -m py_compile app/services/backtest_practical_validation_diagnostics.py app/services/backtest_practical_validation_provider_context.py app/services/backtest_evidence_read_model.py`
- `.venv/bin/python -m unittest tests.test_service_contracts`
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
- `git diff --check`
