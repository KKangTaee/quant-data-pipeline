# Design

## Placement

Live / Deployment Readiness는 우선 `Operations > Selected Portfolio Dashboard` 내부 tab으로 둔다.

이유:

- selected row를 기준으로만 의미가 있으므로 Selected Dashboard picker / source contract / recheck evidence를 재사용한다.
- 현재 범위는 read-only preflight라 별도 top-level page를 만들면 live approval 화면처럼 오해될 수 있다.
- 나중에 실제 approval / account / order workflow가 생기면 별도 Operations page로 승격할 수 있다.

## Read Models

- `build_selected_portfolio_open_issue_followup`: selected row의 `open_review_items`와 review trigger를 compact follow-up table로 변환한다.
- `build_selected_portfolio_deployment_readiness_preflight`: `deployment_readiness_policy_snapshot`, recheck preflight, provider evidence, continuity, review signals, allocation boundary를 read-only rows로 묶는다.

## UI

Portfolio Monitoring tabs에 아래를 추가한다.

- `Open Issues`: Final Review에서 selection은 허용했지만 Dashboard / Live Readiness에서 이어서 봐야 할 항목.
- `Deployment Readiness`: 실제 자금 투입 전 확인해야 할 blocker / review / data gap을 read-only로 표시.

## Boundary

모든 row는 read-only다. 화면에 live approval / broker order / auto rebalance action을 만들지 않는다.
