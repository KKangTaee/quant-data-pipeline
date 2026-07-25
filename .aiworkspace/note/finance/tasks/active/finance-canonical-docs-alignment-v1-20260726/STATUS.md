# Finance Canonical Docs Alignment V1 Status

Status: Implementation In Progress — 3/4
Started: 2026-07-26

## Completed

- INDEX, Product Direction, Project Map, Roadmap과 실제 navigation을 대조했다.
- 문서 길이, task link, old navigation, current state drift를 계량했다.
- local link는 유효하지만 정보구조와 상태 소유권이 섞였음을 확인했다.
- 사용자와 `A · 역할 분리형 전면 정리` 및 INDEX 포함 범위를 합의했다.
- 네 문서의 책임, 읽기 흐름, 정보 보존과 검증 계약을 `DESIGN.md`에 기록했다.
- 상세 implementation plan을 5개 독립 task로 확정했다.
- INDEX의 124개 task link 중심 rolling history를 제거하고 stable document router로 재작성했다.
- INDEX local link, section, line-count와 work-pointer contract를 검증했다.

## Current Step

전체 roadmap `3/4차` 진행 중. 구현 task `3/4` 완료.

INDEX, Product Direction과 Project Map 개편을 완료했고 Roadmap 개편을 진행한다.

## Next Action

Roadmap을 개편한 뒤 cross-document closeout을 수행한다.

## Scope Boundary

- canonical docs 이외의 architecture / flow / data 본문은 이번 task에서 전면 재작성하지 않는다.
- 제품 code, DB, registry, saved setup, run history와 generated artifact를 변경하지 않는다.
