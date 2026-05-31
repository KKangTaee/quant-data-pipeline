# Construction Risk Source Map V1 Design

Status: Complete
Created: 2026-05-29

## Design Position

Phase 11은 기존 evidence를 더 많이 저장하는 phase가 아니다.

V1 방향은 다음이다.

- DB 또는 runtime 계산 영역에 raw data를 둔다.
- Practical Validation / Final Review에는 compact row, status, coverage, blocker / review reason만 노출한다.
- `NOT_RUN`은 pass가 아니며, coverage가 부족한 경우 construction risk audit에서는 `NEEDS_INPUT` 또는 `REVIEW`로 승격한다.
- 기존 provider look-through board와 robustness sensitivity evidence를 construction risk 관점으로 재사용한다.

## Source Ownership

| Ownership | Source |
| --- | --- |
| Selection source and target weights | `build_practical_validation_result()` active components |
| Ticker / proxy exposure | `_build_exposure_summary()` |
| DB holdings / exposure look-through | `build_provider_context()` and `_build_look_through_board()` |
| Holdings overlap metrics | `_build_holdings_context()` |
| Asset bucket exposure metrics | `_build_exposure_context()` |
| Correlation / risk contribution proxy | `_correlation_risk_evidence()` |
| Drop-one / weight tilt dependency | `_sensitivity_rows()` and `_sensitivity_interpretation_result()` |
| Selected-route policy | `build_investability_gate_policy()` group mapping |

## Next Contract Shape

11-2 should introduce a read-only construction risk audit contract, starting with concentration / overlap / exposure.

Candidate contract fields:

- `schema_version`
- `status`
- `summary`
- `coverage`
- `rows`
- `metrics`
- `limitations`
- `source_strength`
- `next_action`

This contract should read existing validation/provider evidence first. It should not create a new workflow registry or store full raw holdings.
