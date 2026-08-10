# Master Merge Resolution Plan

## 이걸 하는 이유?

`codex/main-dev`의 최신 경제 사이클 v3 개선과 `master`의 독립 물가·정책 경로를
한쪽 손실 없이 통합해야 다음 개발이 하나의 기준선에서 이어질 수 있다.

## Scope

- 충돌한 Python, React, npm build output과 finance 문서를 수동 통합한다.
- 양쪽의 독립 ingestion/job, DB, service와 UI 계약을 보존한다.
- local run history, registry 수정, QA 이미지와 run artifact는 병합 commit에서 제외한다.

## Stop Condition

- unresolved conflict와 conflict marker가 0건이다.
- Python focused tests, React tests/typecheck/build와 diff 검증이 통과한다.
- canonical docs와 task/phase state가 통합 코드와 일치하고 merge commit이 완료된다.
