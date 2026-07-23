# Today Portfolio Intraday Auto Refresh V1 Risks

- 실제 정규장 OPEN의 provider snapshot 저장 → live metric/dashed point 변화 → stable iframe 유지 Browser QA는 현재 시장이 CLOSED라 남아 있다. deterministic Python/React fixture는 통과했다.
- EOD retry 횟수는 process memory에서 최대 6회다. process restart 시 attempt count는 초기화되지만 DB daily freshness가 이미 confirmed면 재시도하지 않는다.
- 무료 quote/daily provider의 delay·rate limit은 남는다. symbol error snapshot, 600초 stale, EOD fallback과 bounded retry로 사용자 의미를 보수적으로 유지한다.
- 기존 `MarketIntelligenceIngestionContractTests`의 AAII parser/header 2개 오류는 이 기능 이전 baseline이며 Today collector와 무관하다.
