# Storage Governance Audit V1 Risks

Status: Complete
Created: 2026-05-28

## Remaining Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Legacy registry screens still exist | Users may still see older storage routes | Keep docs explicit and avoid adding new dependencies to legacy helpers. |
| `SAVED_PORTFOLIOS.jsonl` rewrites on update/delete | It does not follow append-only registry semantics | Treat as saved setup compatibility; migrate only in a separate task. |
| Future developer adds another JSONL for convenience | Storage sprawl returns | Require storage classification before adding persistence; consider follow-up lint. |
| Raw provider data leaks into workflow JSONL | Registries become heavy and hard to validate | Keep raw/full evidence in DB and store compact summaries only. |
| Optional monitoring becomes automatic log spam | Selected Dashboard becomes noisy | Monitoring snapshots remain explicit user action unless a later automation policy is approved. |
