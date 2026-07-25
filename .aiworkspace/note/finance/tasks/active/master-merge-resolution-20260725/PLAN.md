# Master Merge Resolution 2026-07-25 Plan

## 이걸 하는 이유?

`codex/main-dev`의 Economic Cycle 개선과 `master`의 Market Research 헤더·Sentiment·
Institutional Holdings·Futures Macro 변경이 같은 문서 포인터, action import, Vite
production bundle을 수정해 병합이 중단됐다. 양쪽 제품 계약을 잃지 않고 검증 가능한
단일 상태로 복구해야 이후 main worktree 통합을 계속할 수 있다.

## Goal

- 충돌 파일에서 양쪽의 독립 기능과 완료 이력을 보존한다.
- 공통 문서의 current/latest 의미와 읽기 순서를 일관되게 유지한다.
- Economic Cycle source를 합친 뒤 production bundle을 다시 만들어 해시 참조를 맞춘다.
- 관련 Python·React 회귀와 Git 무결성 검사를 통과한 병합 커밋을 만든다.

## Roadmap

- [x] 1차: 충돌·브랜치 의도·무관 산출물 분류
- [x] 2차: 문서·Python·React source 및 static bundle 충돌 해결
- [x] 3차: focused 검증, handoff 기록, 병합 커밋

## Scope

- 충돌 상태인 finance root/docs 문서
- `app/jobs/overview_actions.py`
- `app/web/streamlit_components/economic_cycle_workbench/`
- 이 통합 task의 기록

## Out Of Scope

- 제품 UX 재설계
- registry, saved setup, run history, QA 이미지 정리
- 병합과 무관한 기존 broad-suite failure 수정

## Stop Condition

충돌 경로가 0개이고, conflict marker·diff whitespace·focused Python·Economic Cycle
production build 검증이 통과하며, 병합 관련 파일만 coherent하게 stage되어 merge commit이
생성되면 종료한다.
