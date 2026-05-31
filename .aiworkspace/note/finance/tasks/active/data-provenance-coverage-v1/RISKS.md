# Data Provenance Coverage V1 Risks

Status: Complete
Created: 2026-05-28

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Freshness threshold is too strict for issuer data | Useful candidates may become REVIEW too often | Use REVIEW, not BLOCK, and document threshold as policy default. |
| Compact provenance becomes too verbose | Practical Validation JSONL grows again | Store symbol-level compact rows only, not full holdings / macro data. |
| Source type and coverage status are confused | Official partial data may look like complete truth | Keep both source mix and coverage status weights. |
| UI fetches provider data directly | Data boundary is broken | Keep all logic in service read model using loaders only. |
