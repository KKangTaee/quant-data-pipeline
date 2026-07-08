# Practical Validation Flow4 Final Review Handoff V1

Status: Active
Date: 2026-07-08

## Purpose

Flow 4 `검증 기준 상세`가 Final Review에서 해석할 REVIEW 항목까지 카테고리별 상세 검증처럼 보여, 사용자가 Practical Validation에서 고쳐야 할 문제와 Final Review에서 판단할 참고 항목을 혼동하는 문제를 줄인다.

## Scope

- Practical Validation workspace read model에서 REVIEW 항목을 `Final Review 참고`로 별도 집계한다.
- Flow 4 main board는 `통과 / 보강 후 재검증 / 실전 사용 어려움` 중심으로 보여준다.
- Final Review 참고 항목은 상세 목록이 아니라 작은 handoff 요약으로만 표시한다.
- Final Review / registry / saved JSONL / provider ingestion / gate threshold는 변경하지 않는다.

## Completion Criteria

- REVIEW만 남은 후보는 Practical Validation main outcome에서 보강 필요로 보이지 않는다.
- Flow 4 카테고리 카드의 `남은 문제`와 기술 상세에는 Final Review 판단 항목 목록이 나오지 않는다.
- Final Review 참고 항목 수는 작은 handoff summary로 유지된다.
- 관련 unit tests, compile, UI QA를 완료한다.
