# STATUS - Finance Documentation System Rebuild

Status: In Progress
Last Updated: 2026-05-13

## Goal

Notion Codex 문서 운영 가이드에 맞춰 `.note/finance/`를 장기 지식, phase 기록, task 기록, agent 운영 팁으로 재구성한다.

## Current Status

- 마이그레이션 기준 PLAN 작성 완료
- 1차 새 구조 생성 완료
- 2차 `AGENTS.md` 축약 완료
- backtest report 1차 구조 이동 진행 완료
- backtest report 2차 validation 흡수 진행 완료
- backtest report 3차 legacy archive 제거 완료
- `data_architecture/`를 `docs/data/`로 마이그레이션 완료
- `code_analysis/`를 `docs/architecture`, `docs/flows`, `docs/runbooks`, active Practical Validation task 문서로 마이그레이션 완료
- Reference > Guides / Glossary 앱 참조 경로를 새 docs 구조 기준으로 1차 정리 완료
- legacy root / operations / research / support 문서의 2차 흡수 기준 확정 완료
- 기존 문서 삭제는 아직 하지 않음
- `AGENTS.md` 재작성 완료

## Done

- [x] `.note/finance/tasks/active/doc-system-rebuild/PLAN.md` 생성
- [x] 기존 `.note/finance` inventory 확인
- [x] 새 `.note/finance/docs/` skeleton 생성
- [x] 새 `.note/finance/phases/active`, `phases/done` skeleton 생성
- [x] 새 `.note/finance/tasks/active`, `tasks/done` skeleton 생성
- [x] 새 `.note/finance/agent/` skeleton 생성
- [x] 최소 장기 지식 문서 초안 작성
- [x] `AGENTS.md`를 새 read order / work mode 기준으로 축약
- [x] 기존 `.note/finance/backtest_reports/`를 `.note/finance/reports/backtests/`로 1차 이동
- [x] 새 report README / INDEX / TEMPLATE / LEGACY_MIGRATION 작성
- [x] legacy `phase23`, `phase24` validation report를 `validation/runtime`, `validation/ui_replay`로 흡수
- [x] legacy `phase13`~`phase22` report를 `runs/`, `candidates/`, `validation/`으로 분류하고 archive 제거
- [x] legacy `data_architecture/` 상세 문서를 `docs/data/`로 흡수하고 폴더 제거
- [x] legacy `code_analysis/` 문서를 새 docs/task 구조로 흡수하고 폴더 제거
- [x] `Reference > Guides` 문서 경로와 `Reference > Glossary` 읽기 경로를 새 docs 구조로 전환
- [x] legacy root / operations / research / support 문서의 남길 정보와 삭제 후보를 정리
- [x] Practical Validation static stress window JSON을 `docs/data/`로 이동하고 runtime path 갱신

## Next

- [x] 1차 결과를 사용자에게 확인받기
- [x] 2차 작업에서 `AGENTS.md`를 새 read order 기준으로 축약하기
- [x] 2차 작업에서 남은 legacy root / operations / research / support 문서 중 새 docs로 흡수할 내용 확정하기
- [ ] 3차 작업에서 나머지 기존 문서 tree 삭제와 검증 진행하기

## Current Boundary

현재까지 아래는 하지 않았다.

- operations / research / root markdown 등 남은 legacy tree 삭제
- strategy hub/log와 raw run report 간 중복 해석 삭제 판단
- registry / saved JSONL 수정
- Reference / Glossary 이외 finance 기능 코드 수정
