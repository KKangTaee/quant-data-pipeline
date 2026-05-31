# Allocation Drift Evidence Boundary V1 Design

Status: Complete
Created: 2026-05-29

## Design

`selected_allocation_drift_evidence_boundary_v1`은 Actual Allocation의 세 evidence를 하나의 boundary read model로 묶는다.

| Evidence | Meaning |
| --- | --- |
| Current weight input source | 수동 입력 또는 session 입력으로만 현재 비중을 계산한다 |
| Drift evidence | target weight 대비 current weight drift를 계산한다 |
| Alert preview evidence | drift 결과를 Review Signals 관점으로만 번역한다 |
| Storage boundary | DB / registry / monitoring log / raw input / alert 저장이 모두 꺼져 있는지 확인한다 |
| Execution boundary | account / broker / approval / order / auto rebalance가 모두 꺼져 있는지 확인한다 |

## Route Mapping

| Route | Meaning |
| --- | --- |
| `ALLOCATION_DRIFT_BOUNDARY_OPTIONAL` | allocation check가 실행되지 않은 선택 상태 |
| `ALLOCATION_DRIFT_BOUNDARY_READY` | drift / alert evidence가 read-only 경계 안에서 정상 |
| `ALLOCATION_DRIFT_BOUNDARY_WATCH` | drift가 관찰 기준을 넘었지만 주문이 아니라 수동 관찰 신호 |
| `ALLOCATION_DRIFT_BOUNDARY_NEEDS_INPUT` | 현재 배분 입력이 부족하거나 불완전함 |
| `ALLOCATION_DRIFT_BOUNDARY_BREACHED` | drift가 재검토 기준을 넘었지만 자동 리밸런싱이 아님 |
| `ALLOCATION_DRIFT_BOUNDARY_BLOCKED` | 저장 / 실행 경계 위반 |

## Storage / Execution Boundary

Boundary false fields:

- `db_write`
- `registry_write`
- `monitoring_log_auto_write`
- `input_persistence`
- `alert_persistence`
- `account_connection`
- `broker_sync`
- `live_approval`
- `order_instruction`
- `auto_rebalance`

Selected Dashboard 버튼은 현재 session의 Review Signals에만 반영한다.
입력값, alert record, monitoring log, 주문은 저장하지 않는다.
