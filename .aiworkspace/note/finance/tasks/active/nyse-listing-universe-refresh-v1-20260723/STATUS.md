# Status

Status: Design checkpoint
Updated: 2026-07-23
Roadmap: 1/3 complete

## Completed

- 전체 symbol source가 `nyse_stock` / `nyse_etf` current master를 읽는 것을 확인했다.
- 기존 NYSE official API collector와 CSV DB writer가 Ingestion에 연결되지 않은 것을 확인했다.
- DB snapshot 2026-05-31과 2026-07-23 NYSE current 목록을 비교했다.
- 사용자가 주식+ETF 통합 action과 독립 Ingestion placement를 승인했다.

## Current

- 승인 설계를 task 문서로 고정하고 written-spec review를 기다린다.

## Next

- 구현 계획을 TDD 단위로 작성한다.
- universe refresh core의 실패 테스트부터 시작한다.
