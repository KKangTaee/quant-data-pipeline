# Notes

## 2026-07-12 Initial Diagnosis

- 현재 저장된 6개 validation은 모두 `READY_WITH_REVIEW`, `can_save_and_move=true`다.
- 6개 모두 operability stale symbol을 포함하지만 Gate는 REVIEW를 blocker로 해석하지 않는다.
- Final Review read model은 최신 collection plan을 다시 계산하므로 저장 Gate와 현재 보강 가능 상태 사이에 drift가 보인다.

## 2026-07-12 Pre-Final Enrichment Contract

- 승격 blocker는 공식·검증된 operability source, 검증된 holdings/exposure source, 필요한 macro collector처럼 실제 해결 가능성이 확인된 plan만 사용한다.
- source map discovery와 bridge-only target은 실행 가능성 탐색 단계이므로 v1의 강제 blocker에서 제외한다.
- 기존 module 판정은 보존하고 wrapper가 synthetic `pre_final_data_enrichment` NEEDS_INPUT blocker를 합성한다.

## 2026-07-12 Practical Validation Completion Flow

- Flow 3은 pre-final enrichment blocker를 일반 `보강 필요`와 구분해 `데이터 보강 후 재검증 필요`로 표시한다.
- Flow 4의 필수 보강 action은 기존 Python collector만 실행하고, 완료 즉시 해당 source의 current replay state를 초기화한다.
- 수집 결과는 검증 결과가 아니므로 사용자가 Flow 2 재검증을 완료하기 전에는 Final Review 이동이 계속 비활성화된다.

## 2026-07-12 Final Review Recovery Modes

- 새 validation의 stored pre-final Gate가 blocking이면 Final Review eligibility를 방어적으로 거부한다.
- pre-final Gate 계약이 없는 기존 row는 현재 coverage로 plan을 재계산하고 `legacy_recovery`로 표시한다.
- 저장 당시 non-blocking이었지만 이후 자료가 다시 오래지면 `stale_recovery`, 현재 필수 보강이 없으면 `hidden`이다.
- legacy row의 구형 stored provider plan을 신뢰하지 않고 현재 coverage에서 다시 계산한다. 새 validation 생성 중에는 wrapper가 방금 계산한 provider plan을 명시적으로 전달한다.

## 2026-07-12 Read-Only Recovery Guard

- legacy / stale recovery 후보는 과거 점수와 근거를 열람할 수 있지만 recommendation, Decision Desk, Monitoring handoff는 현재 선택 가능 상태로 표시하지 않는다.
- recovery가 필요한 동안 Final Decision Action의 모든 route 저장을 비활성화하고 `RE_REVIEW_REQUIRED`를 기본 route로 제시한다.
- Flow 3 category 자체가 통과여도 pre-final enrichment Gate가 blocking이면 first-read 요약은 `필수 데이터 보강 후 재검증 필요`로 덮어써서 상충 문구를 제거한다.
