# Post-Merge Docs Alignment 2026-06-07 Plan

## 이걸 하는 이유?

master 병합 후 여러 worktree의 구현 결과와 문서가 함께 들어오면서, 현재 제품 흐름과 완료 이력, active 상태, 저장 경계가 한 문서 안에서 섞여 읽히는 문제가 생겼다.

이번 1차 작업은 코드 동작을 바꾸지 않고, 현재 브랜치가 실제로 제공하는 기능과 다음 개발 판단 위치를 durable docs에서 빠르게 파악할 수 있게 정리한다.

## Scope

- Update durable project docs around current product direction, roadmap, index, project map, architecture / flow / data entry docs.
- Record merge-state analysis and closeout in this task folder.
- Keep root handoff logs short.

## Out Of Scope

- Code behavior changes.
- Registry / saved JSONL rewrite.
- Deleting or migrating untracked legacy `.note/` artifacts.
- Moving 168 retained task folders or 11 retained phase boards out of `active/`.
- UI/UX behavior changes.

## Tentative Roadmap

| 차수 | 목적 | 완료 조건 |
|---|---|---|
| 1차 | 현재 문서 지도 정리 | durable docs가 현재 merged product flow, completed surfaces, active scope, boundaries를 일관되게 설명 |
| 2차 | active/done 보관 체계 정리 | retained task / phase boards를 archive / done / active 의미에 맞게 이동할지 사용자가 승인 |
| 3차 | 후속 개발 scope 선택 | Overview V2, Risk-On governance, monitoring hardening, UI platform split 같은 후보 중 다음 phase/task 선정 |

## Files

- `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md`
- `.aiworkspace/note/finance/docs/INDEX.md`
- `.aiworkspace/note/finance/docs/ROADMAP.md`
- `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- `.aiworkspace/note/finance/docs/architecture/README.md`
- `.aiworkspace/note/finance/docs/flows/README.md`
- `.aiworkspace/note/finance/docs/data/README.md`
- `.aiworkspace/note/finance/tasks/active/README.md`
- `.aiworkspace/note/finance/phases/active/README.md`
- `.aiworkspace/note/finance/WORK_PROGRESS.md`
- `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
