# Decision Dossier Report V1 Design

Status: Active
Created: 2026-05-28

## Design Summary

Decision Dossier는 persistence가 아니라 read model이다.

```text
Final Review decision row
  + optional Selected Dashboard monitoring timeline
    -> decision_dossier_v1
    -> markdown export string
    -> Final Review / Selected Dashboard UI
```

## Data Shape

Service helper는 아래 compact dict를 반환한다.

- `schema_version`
- `decision`
- `operator`
- `components`
- `evidence_checks`
- `gate_policy`
- `monitoring_timeline`
- `markdown`
- `execution_boundary`

## Storage Boundary

- Dossier 자체는 저장하지 않는다.
- Dossier markdown은 `st.download_button`으로 사용자가 내려받을 수 있는 export text다.
- 자동 report file write는 하지 않는다.
- Future report persistence가 필요하면 `docs/data/STORAGE_GOVERNANCE.md` 기준으로 별도 task에서 승인한다.

## UI Boundary

- Final Review saved record는 저장된 final decision row 기준 dossier를 보여준다.
- Selected Dashboard는 현재 selected row와 session-state monitoring timeline을 포함한 dossier를 보여준다.
- Dossier는 투자 승인, 주문 지시, 자동 리밸런싱을 만들지 않는다.
