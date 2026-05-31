# Decision Dossier Continuity Operations V1 Design

Status: Complete
Created: 2026-05-29

## Source Contract

`selected_decision_source_consistency_v1`은 Selected Dashboard 운영 surface가 읽는 기준 decision source를 compact하게 전달한다.

계약 필드:

- `decision_id`
- `decision_route`
- `selected_practical_portfolio`
- `source_type`
- `source_id`
- `source_title`
- `selection_source_id`
- `validation_id`
- `source_identity`
- `durable_source`
- `registry_file`
- `session_evidence_sources`
- `execution_boundary`

`durable_source`는 `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2`로 고정한다.
`session_evidence_sources`는 Performance Recheck, drift check, alert preview처럼 현재 session에서만 읽는 evidence를 표시한다.

## Surface Behavior

| Surface | Behavior |
| --- | --- |
| Timeline | current selected decision row와 optional session evidence를 읽고 source contract를 포함한다 |
| Continuity | timeline source contract가 현재 selected decision row와 맞는지 확인하고 mismatch를 `BLOCKED`로 표시한다 |
| Review Signals | recheck / drift session evidence source를 contract에 표시하되 저장하지 않는다 |
| Decision Dossier | Final Decision V2 row와 optional session timeline source contract를 markdown에 표시한다 |

## Read-Only Boundary

계약의 execution boundary는 아래 동작을 모두 `False`로 고정한다.

- `db_write`
- `registry_write`
- `monitoring_log_auto_write`
- `report_auto_write`
- `live_approval`
- `order_instruction`
- `auto_rebalance`

이 계약은 저장 대상이 아니라 source identity와 운영 경계를 표시하는 read model metadata다.
