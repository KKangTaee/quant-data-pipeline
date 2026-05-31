# Storage Governance Audit V1 Plan

Status: Complete
Created: 2026-05-28
Owner: main-dev + finance-doc-sync

## 이걸 하는 이유?

현재 Backtest -> Practical Validation -> Final Review -> Selected Portfolio Dashboard 흐름은 간결해졌지만, 과거 개발 과정에서 만들어진 JSONL 저장 지점이 여전히 많이 남아 있다.

이번 task의 목적은 바로 registry를 삭제하거나 rewrite하는 것이 아니라, 어떤 저장은 제품 흐름에 필요한 source-of-truth이고 어떤 저장은 legacy compatibility / local artifact / explicit saved setup인지 먼저 분류하는 것이다. 이 기준이 있어야 다음 개발에서 의미 없는 사용자 메모 저장, 중복 JSONL, raw data JSONL 보관이 다시 늘어나는 일을 막을 수 있다.

## Scope

- 현재 코드의 JSONL write / artifact write 지점 전수 감사
- main portfolio selection V2 source chain과 legacy registry 경계 분리
- `docs/data`에 장기 storage governance 기준 추가
- registry / saved / run history README 동기화
- phase / roadmap / root handoff log 업데이트

## Out Of Scope

- registry JSONL 삭제, rewrite, migration
- 새 JSONL registry 추가
- DB schema 변경
- UI 화면 변경
- provider / macro / holdings 수집 구현
- 사용자 메모 저장 기능 추가

## Completion Criteria

- JSONL 저장 지점별 keep / optional / legacy / local artifact / DB-only 분류가 문서화된다.
- 새 persistence 추가 전 확인해야 하는 checklist가 장기 문서에 남는다.
- Phase 0 task board에서 `storage-governance-audit-v1`가 완료로 표시된다.
- `git diff --check`가 통과한다.
