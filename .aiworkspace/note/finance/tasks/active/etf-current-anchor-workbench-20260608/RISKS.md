# Risks

Status: Completed
Last Verified: 2026-06-08

## Open Risks

| Risk | Mitigation |
|---|---|
| Workbench is mistaken for current-candidate promotion | Keep storage boundary explicit and avoid registry writes. |
| Local run history is stale or uncommitted | Display latest run evidence as local evidence and show missing/stale evidence gaps. |
| Missing provider / cost / benchmark fields are treated as pass | Represent missing fields as evidence gaps and use review-required status. |
| 4A scope expands into rerun matrix execution | Keep rerun matrix as 4B follow-up after approval. |

## Remaining Risk

- The workbench is artifact-backed but read-only. ETF rerun matrix execution, strategy hub/report updates, provider snapshot collection, and current candidate promotion remain future 4B+ work.
