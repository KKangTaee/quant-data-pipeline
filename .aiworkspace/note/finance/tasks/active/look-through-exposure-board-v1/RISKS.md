# Look-through Exposure Board V1 Risks

Status: Complete
Created: 2026-05-28

## Risks

| Risk | Mitigation |
|---|---|
| UI accidentally implies live approval or trade readiness | Use Final Review / 실전 검토 wording only; keep live approval disabled language |
| JSONL grows with full holdings rows | Store only compact top rows and summary in validation payload |
| Board hides stale / partial provider data | Reuse provenance / freshness fields and surface them in summary rows |
| ETF-of-ETF requires deeper recursive look-through | Keep V1 explicitly 1차 holdings / exposure board and document limitation |

## Residual Risk

- Browser smoke can confirm page load and stage navigation, but live board rows only appear when a selected source has provider holdings / exposure evidence.
