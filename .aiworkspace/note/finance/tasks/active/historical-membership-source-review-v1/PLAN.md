# Historical Membership Source Review V1 Plan

Status: Active
Created: 2026-05-28

## 이걸 하는 이유?

Phase 8의 핵심 약점은 symbol lifecycle evidence가 아직 불완전하다는 점이다.
SEC Form 25는 official delisting evidence지만 complete historical membership source가 아니고, current listing snapshot은 survivorship PASS 근거가 아니다.

이 task는 바로 crawler를 추가하기 전에 무료 / 공식 source 중 어떤 것을 실제 DB ingestion 대상으로 삼을 수 있는지 확인한다.

## Scope

포함한다.

- 무료 / 공식 source 후보 조사
- source별 coverage, 접근성, historical depth, event type, ingestion feasibility 정리
- Phase 8 다음 구현 task 추천
- 문서 / roadmap / phase task board 업데이트

포함하지 않는다.

- 새 collector 구현
- DB schema 변경
- 새 JSONL registry
- user memo / preset persistence
- live approval / broker order / auto rebalance

## Done Criteria

- source 후보별 사용 가능 여부가 정리된다.
- 바로 구현할 수 있는 무료 / 공식 ingestion slice가 결정된다.
- 유료 / 승인형 source는 parking lot으로 분리된다.
- Phase 8 task board가 다음 구현 순서를 반영한다.
