# Status

Status: Complete
Updated: 2026-07-23
Roadmap: 3/3 complete

## Completed

- 전체 symbol source가 `nyse_stock` / `nyse_etf` current master를 읽는 것을 확인했다.
- 기존 NYSE official API collector와 CSV DB writer가 Ingestion에 연결되지 않은 것을 확인했다.
- DB snapshot 2026-05-31과 2026-07-23 NYSE current 목록을 비교했다.
- 사용자가 주식+ETF 통합 action과 독립 Ingestion placement를 승인했다.
- NYSE stock·ETF snapshot을 먼저 모두 검증한 뒤 current master와 lifecycle을 한 transaction으로
  저장하는 atomic refresh를 구현했다.
- Ingestion `일상 운영 / 검증 데이터` 첫 action에 `주식·ETF 종목 목록 최신화`를 배치하고,
  결과를 기준일·현재·추가·제외와 다음 행동 중심으로 compact하게 표시했다.
- 실제 refresh로 stock `6,738→6,770(+158/-126)`, ETF `5,232→5,537(+372/-67)`을
  반영했고 `nyse_price_history` 20,341,708행이 유지됨을 확인했다.
- focused 19개 테스트, lifecycle 회귀, compile/diff check와 desktop/mobile Browser QA를 통과했다.

## Current

- 전체 3/3차가 완료되었다.

## Next

- scheduler/cron 자동화는 별도 승인 범위로 남긴다.
- 사용자는 목록 최신화가 끝난 뒤 필요한 가격 source를 선택해 별도 수집한다.
