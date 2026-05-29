# Phase 11 Portfolio Construction Risk Controls Design

Status: Active
Created: 2026-05-29

## Design Principle

Phase 11은 "좋은 component를 조합했는가?"가 아니라 "조합 결과가 실전 포트폴리오로 볼 만큼 분산 / 역할 / 위험기여가 타당한가?"를 확인한다.

기본 방향은 다음이다.

- raw holdings / full return matrix는 DB 또는 runtime 계산 영역에 둔다.
- workflow JSONL에는 compact evidence, row status, blocker / review reason만 남긴다.
- component score를 다시 합산해 후보를 자동 선택하지 않는다.
- Final Review selected-route gate는 construction risk gap을 pass처럼 숨기지 않는다.

## Evidence Layers

| Layer | Purpose | Initial Source |
| --- | --- | --- |
| Source map | 현재 concentration / overlap / correlation / risk contribution evidence가 어디에 있는지 확인 | Complete: Practical Validation diagnostics, provider context, look-through board, robustness lab, final review gate |
| Concentration contract | component weight, asset bucket, sector / theme, top holding concentration 확인 | Complete: `construction_risk_audit_v1` |
| Overlap contract | ETF 내부 top holding / issuer / exposure overlap 확인 | Complete: `construction_risk_audit_v1` provider holdings compact metrics |
| Risk contribution contract | component return correlation, volatility contribution, drop-one dependency 확인 | Complete: `risk_contribution_audit_v1` |
| Role / weight discipline | hedge / diversifier / growth role과 profile-aware max weight 확인 | proposal source, validation profile, component metadata |
| Gate policy | selected-route 가능 여부에 construction risk gap 반영 | investability packet / selected-route gate |

## 11-1 Source Map Result

11-1 found that Phase 11 can start from existing evidence rather than new persistence.

Reusable sources:

- `build_practical_validation_result()` already emits `concentration_overlap_exposure` and `correlation_diversification_risk_contribution` diagnostics.
- `_build_look_through_board()` already emits holdings coverage, exposure coverage, top holding, top overlap, dominant asset, and unknown exposure.
- `_correlation_risk_evidence()` already emits average / max correlation and risk contribution proxy.
- `_sensitivity_rows()` already emits drop-one and +5%p weight tilt dependency evidence.

Main gaps:

- `construction_risk` is not a first-class Final Review gate group yet.
- Concentration / overlap / exposure evidence is split between Practical Validation diagnostics and provider look-through board.
- Proxy-only source can look too strong unless source strength and provider coverage are explicit.
- Component role / weight discipline has no first-class metadata source yet.

Implementation order remains 11-4 role / weight discipline, then 11-5 gate policy.

## 11-2 Contract Result

11-2 added `app/services/backtest_construction_risk_audit.py`.

The new audit reads existing compact evidence:

- active component count, target weight total, max component weight
- provider look-through board status
- holdings coverage and exposure coverage
- top holding weight and top overlap weight
- dominant asset bucket and unknown exposure

The audit exposes:

- `CONSTRUCTION_RISK_READY`
- `CONSTRUCTION_RISK_REVIEW`
- `CONSTRUCTION_RISK_NEEDS_INPUT`
- `CONSTRUCTION_RISK_BLOCKED`

Provider holdings / exposure absence is not treated as PASS. The contract is displayed in Practical Validation and Final Review, preserved in final decision snapshots, and kept out of selected-route gate enforcement until 11-5.

## 11-3 Contract Result

11-3 added `app/services/backtest_risk_contribution_audit.py`.

The new audit reads existing compact evidence:

- component return matrix coverage from component curve evidence and correlation diagnostic monthly rows
- pairwise average / max correlation
- max risk contribution proxy
- Robustness Lab `Component dependency` drop-one row
- read-only storage / execution boundary

The audit exposes:

- `RISK_CONTRIBUTION_READY`
- `RISK_CONTRIBUTION_REVIEW`
- `RISK_CONTRIBUTION_NEEDS_INPUT`
- `RISK_CONTRIBUTION_BLOCKED`

Missing component matrix or missing drop-one dependency is not treated as PASS. DB price proxy or mixed component curve source is displayed as source strength and remains `REVIEW`. The contract is displayed in Practical Validation and Final Review, preserved in final decision snapshots and evidence rows, and kept out of selected-route gate enforcement until 11-5.

## Route Semantics

| State | Meaning |
| --- | --- |
| `PASS` | 충분한 coverage와 source를 바탕으로 construction risk가 profile 기준을 만족 |
| `REVIEW` | evidence는 있으나 coverage, profile fit, role proof, sensitivity가 부족 |
| `NEEDS_INPUT` | holdings / exposure / return matrix / role source가 없어 판단 불가 |
| `BLOCKED` | concentration, overlap, or risk contribution이 selected-route 판단을 막는 수준 |

`NOT_RUN`은 pass가 아니다. 실행하지 못한 검증은 `NEEDS_INPUT` 또는 `REVIEW`로 남긴다.

## Candidate Implementation Boundaries

초기 구현 후보는 아래 경계 안에서 다룬다.

- `app/services/backtest_practical_validation_diagnostics.py`: current diagnostic source and row ownership 확인
- `app/services/backtest_practical_validation_provider_context.py`: provider holdings / exposure compact context 확인
- `app/services/backtest_practical_validation_stress_sensitivity.py`: correlation / risk contribution proxy and drop-one sensitivity reuse 확인
- `app/services/backtest_evidence_read_model.py`: Final Review gate policy 연결 후보
- `finance/loaders/provider.py`: holdings / exposure source 확인 후보
- `tests/test_service_contracts.py`: service contract 고정

11-3 result: correlation / risk contribution contract is complete. Next code change should start with component role / weight discipline source ownership and compact row semantics.

## Data Boundary

- full holdings, full exposure rows, raw provider response는 workflow JSONL에 저장하지 않는다.
- component return matrix나 covariance matrix를 raw artifact로 저장하지 않는다.
- 필요한 raw / series data는 DB 또는 runtime 계산 영역에 두고 service가 compact summary를 제공한다.
- Practical Validation JSONL에는 기존 흐름이 허용하는 compact evidence만 둔다.
- user memo, preset, approval, order, auto rebalance 성격의 저장은 추가하지 않는다.

## User Flow Target

사용자는 기존 흐름을 유지한다.

```text
Backtest Analysis
  -> Practical Validation
  -> Final Review
  -> Selected Portfolio Dashboard
```

Phase 11이 끝나면 Practical Validation과 Final Review에서 "이 포트폴리오는 성과 / 검증은 좋아도 구성상 특정 exposure나 risk source에 너무 몰려 있어 보류해야 한다"는 결론을 더 명확히 볼 수 있어야 한다.
