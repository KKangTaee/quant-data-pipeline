# Notes

## 2026-07-12 Initial Diagnosis

- 현재 저장된 6개 validation은 모두 `READY_WITH_REVIEW`, `can_save_and_move=true`다.
- 6개 모두 operability stale symbol을 포함하지만 Gate는 REVIEW를 blocker로 해석하지 않는다.
- Final Review read model은 최신 collection plan을 다시 계산하므로 저장 Gate와 현재 보강 가능 상태 사이에 drift가 보인다.

## 2026-07-12 Pre-Final Enrichment Contract

- 승격 blocker는 공식·검증된 operability source, 검증된 holdings/exposure source, 필요한 macro collector처럼 실제 해결 가능성이 확인된 plan만 사용한다.
- source map discovery와 bridge-only target은 실행 가능성 탐색 단계이므로 v1의 강제 blocker에서 제외한다.
- 기존 module 판정은 보존하고 wrapper가 synthetic `pre_final_data_enrichment` NEEDS_INPUT blocker를 합성한다.
