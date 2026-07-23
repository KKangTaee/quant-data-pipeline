# Market Research S&P 500 Manual Price Refresh V1 Risks

Status: Active
Last Updated: 2026-07-24

## Open Risks

- 수동 action만 제공하므로 사용자가 S&P 500 화면에 진입하지 않으면 DB 가격은 자동으로 갱신되지 않는다.
- 무료 provider가 최신 완료 장 row를 지연하거나 누락하면 button 실행 후에도 stale 상태가 유지될 수 있다.
- `^GSPC`와 `SPY` 중 하나만 갱신될 수 있으므로 SPX freshness와 same-date SPY conversion readiness를 분리해야 한다.
- Streamlit component event가 rerun에서 중복 소비되지 않도록 nonce 계약을 유지해야 한다.
- 현재 valuation cache TTL은 300초이므로 action 성공 시 명시적 cache clear가 필요하다.

## Explicitly Deferred

- macOS LaunchAgent / LaunchDaemon
- cron / external scheduler
- Shiller monthly freshness action
- SEP release freshness action
- official S&P Index Earnings acquisition automation
