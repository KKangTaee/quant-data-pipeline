# Plan

## 이걸 하는 이유?

Earnings dates are estimates and can move. If the same symbol later receives a different provider estimate, the old row should not remain indistinguishable from the current estimate.

## Scope

- `market_event_calendar`에 lifecycle columns를 추가한다.
- 새 earnings row 수집 후 같은 symbol/source의 이전 active earnings row를 `superseded`로 표시한다.
- 오래된 active provider estimate는 `stale` 상태로 표시할 수 있는 cleanup helper를 추가한다.
- Overview read model은 superseded row를 기본 목록에서 제외한다.

## Done Criteria

- 이전 earnings estimate row가 새 estimate에 의해 superseded 처리된다.
- stale estimate cleanup이 idempotent하게 동작한다.
- Overview Events에서 current row 중심으로 보인다.
