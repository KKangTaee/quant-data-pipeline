# Finance Canonical Docs Alignment V1 Plan

Status: Design Review
Started: 2026-07-26

## 이걸 하는 이유?

`INDEX.md`, `PRODUCT_DIRECTION.md`, `PROJECT_MAP.md`, `ROADMAP.md`는 사람과 AI가
프로젝트를 이해할 때 가장 먼저 읽는 문서다. 현재는 최신 제품 정보와 과거 완료
작업 이력이 섞여 있어, 실제 화면·코드·다음 결정이 문서 안에서 빠르게 드러나지
않는다.

이번 작업은 네 문서의 역할을 다시 분리하고 현재 구현과 정렬해, 처음 읽는 사람이
제품 목적부터 현재 상태와 구현 위치까지 예측 가능한 순서로 이해하게 만든다.

## Roadmap

- [x] 1차: 현재 문서, navigation, active state와 최근 완료 작업 drift 진단
- [x] 2차: 네 canonical 문서의 역할과 정보구조 설계
- [ ] 3차: 사용자 설계 문서 검토와 구현 계획 확정
- [ ] 4차: 네 문서 개편, 교차 검증, root handoff와 commit

## Scope

- `.aiworkspace/note/finance/docs/INDEX.md`
- `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md`
- `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- `.aiworkspace/note/finance/docs/ROADMAP.md`
- 이 task의 계획·설계·상태·실행·위험 기록
- 완료 시 root handoff log

## Out Of Scope

- 제품 code, UI, DB schema와 runtime 동작 변경
- `registries/`, `saved/`, `run_history/` 수정
- task / phase 폴더의 물리적 archive migration
- 상세 architecture / flow / data / runbook 본문의 전면 재작성
- 과거 완료 task 기록 삭제

## Stop Condition

- 네 문서가 서로 다른 질문에 답하고 같은 내용을 장황하게 복제하지 않는다.
- current `Research / Portfolio / Data / Help`와 7개 top-level surface가 일치한다.
- 실제 현재 상태와 다음 승인 후보가 과거 완료 이력보다 먼저 보인다.
- local link, 주요 code path, 문서 역할과 stale navigation 검증이 통과한다.
