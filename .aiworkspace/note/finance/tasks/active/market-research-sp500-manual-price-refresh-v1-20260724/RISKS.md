# Market Research S&P 500 Manual Price Refresh V1 Risks

Status: Completed
Last Updated: 2026-07-24

## Remaining Product Limits

- 수동 action만 제공하므로 사용자가 S&P 500 화면에 진입하지 않으면 DB 가격은 자동으로 갱신되지 않는다. 이는 승인된 manual-only 제품 경계다.
- 무료 provider가 최신 완료 장 row를 지연하거나 누락하면 button 실행 후에도 stale 상태가 유지될 수 있다. 이 경우 기존 평가를 보존하고 재시도한다.
- Shiller 월간, SEP release, official EPS의 발표 주기와 확보 경로는 가격 action과 별도이며 이 기능이 최신화하지 않는다.

## Resolved Risks

- `^GSPC`와 `SPY` freshness는 postcondition에서 분리되어 SPX 성공/실패를 왜곡하지 않는다.
- component event nonce와 one-shot reflection 계약으로 rerun 중복 실행을 방지했다.
- 성공 시 두 valuation cache를 명시적으로 clear하며, 실패 시 기존 latest-good cache를 유지한다.

## Explicitly Deferred

- macOS LaunchAgent / LaunchDaemon
- cron / external scheduler
- Shiller monthly freshness action
- SEP release freshness action
- official S&P Index Earnings acquisition automation
