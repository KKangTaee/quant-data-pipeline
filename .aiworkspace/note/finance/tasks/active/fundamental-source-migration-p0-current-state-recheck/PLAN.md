# Fundamental Source Migration P0 Current-State Recheck

## 이걸 하는 이유?

재무제표 canonical source를 EDGAR statement path로 옮기기 전에, 현재 worktree와 local DB 상태가 리서치 산출물의 전제와 어긋나지 않는지 확인한다. 이 확인이 끝나야 source contract freeze와 구현 phase를 안전하게 시작할 수 있다.

## Scope

- current branch / dirty files 확인
- financial statement source usage 검색
- broad yfinance table, EDGAR statement shadow table, raw statement ledger coverage 확인
- quarterly statement shadow의 `10-K` / `10-K/A` 혼입 여부 확인

## Non-Scope

- 코드 변경
- DB row 수정 또는 backfill
- yfinance package 제거
- table drop

## Completion Criteria

- recheck 명령 결과를 `RUNS.md`에 남긴다.
- research 결론과 달라 migration 순서를 바꿀 차이가 있으면 `RISKS.md`에 blocker로 기록한다.
- blocker가 없으면 다음 phase인 source contract freeze로 넘어간다.
