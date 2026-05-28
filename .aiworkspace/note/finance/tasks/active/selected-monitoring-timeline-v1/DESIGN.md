# Selected Monitoring Timeline V1 Design

Status: Active
Created: 2026-05-28

## Design Summary

Selected Monitoring Timeline은 persistence가 아니라 read model이다.

```text
Final Review selected row
  + latest Performance Recheck session result
  + latest Actual Allocation / drift session result
  + optional drift alert preview
    -> selected_monitoring_timeline
    -> Operations > Selected Portfolio Dashboard
```

## Data Shape

Runtime helper는 아래 compact dict를 반환한다.

- `schema_version`
- `timeline_status`
- `timeline_label`
- `conclusion`
- `rows`
- `metrics`
- `execution_boundary`

Timeline row는 event / status / signal / evidence / next action을 가진다.

## Storage Boundary

- Timeline 자체는 저장하지 않는다.
- Performance Recheck와 drift check는 session state read model로만 반영한다.
- `SELECTED_PORTFOLIO_MONITORING_LOG.jsonl`는 후속 명시 저장 정책이 승인될 때만 쓴다.

## UI Boundary

- Timeline은 Selected Dashboard의 첫 monitoring tab으로 둔다.
- Review Signals는 기존 trigger board로 유지한다.
- Timeline은 주문, 승인, 자동 리밸런싱을 만들지 않는다.
