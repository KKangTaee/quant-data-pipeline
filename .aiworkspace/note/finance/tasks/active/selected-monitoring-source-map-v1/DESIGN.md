# Selected Monitoring Source Map V1 Design

Status: Complete
Created: 2026-05-29

## Design Decision

12-1은 코드 구현 없이 완료한다.

Phase 12는 새 monitoring registry나 자동 저장을 추가할 필요가 없다.
현재 dashboard는 이미 read-only monitoring evidence를 갖고 있으므로, 먼저 source ownership과 policy owner를 재정렬하는 방식이 맞다.

## Source Ownership Result

| Source Class | Owner | Notes |
| --- | --- | --- |
| Canonical selected decision | `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl` via `load_final_selection_decisions_v2()` | Selected Dashboard source-of-truth |
| Replay contract | Current Candidate Registry via `build_candidate_replay_payload()` today | 12-2에서 final decision embedded contract fallback 여부 검토 |
| Price freshness | `finance.loaders.price.load_price_freshness_summary()` | DB read-only; no OHLCV ingestion from UI |
| Provider evidence | `build_provider_context()` | DB provider snapshot read-only; no provider collection from dashboard |
| Latest recheck / drift / alert | Streamlit session state | Session-only evidence; not durable monitoring record |
| Dossier export | `build_decision_dossier()` | Read-only markdown download; no report file auto-write |

## Next Implementation Boundary

12-2 should not change Final Review save shape unless the source map proves embedded replay contract is already present and can be safely reused.
If new compact fields are needed later, they should be added to the existing final decision row contract only after a specific implementation task justifies which later stage reads them.

No task in Phase 12 should create a new monitoring registry or automatic append path.
