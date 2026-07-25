# Risks

- canonical cleanup은 authoritative XLS capture에만 허용해야 한다.
- immutable PIT rows를 canonical cleanup 대상으로 포함하면 안 된다.
- cleanup과 UPSERT가 한 transaction이 아니면 중간 실패 시 AAII recent window가 비어 보일 수 있다.
- official workbook fetch가 성공하기 전에 기존 canonical rows를 삭제하면 안 된다.

## Closed

- complete/aligned XLS capture에만 canonical reconciliation을 허용했다.
- outer AAII source, success coverage, official workbook provenance, four-series alignment, ISO weekly cadence가 모두 맞을 때만 cleanup을 실행한다. 중간 주차 누락, source mismatch, partial, non-official capture 회귀를 추가했다.
- reconciliation과 UPSERT를 기존 source transaction 안에 배치하고 failure rollback을 회귀로 고정했다.
- actual full backfill은 workbook fetch 완료 뒤 transaction을 시작했고 immutable counts를 전후 비교했다.

## Remaining

- AAII upstream workbook/date methodology가 바뀌면 complete/aligned gate와 source metadata를 다시 검토해야 한다.
- 현재 worktree의 repository-wide suite는 비관련 Backtest/Overview/Portfolio contract 실패가 다수 남아 green이 아니다. 이번 변경의 focused PIT/service/React 계약은 통과했지만, 전체 suite green을 이 task의 완료 사실로 주장하지 않는다.
