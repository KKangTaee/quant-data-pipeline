# Data Provenance / PIT Evidence Contract Risks

## Open Risks

- The first contract may not cover every future factor/fundamental evidence path; this slice focuses on active Practical Validation / Final Review evidence.
- Macro PIT safety remains limited because ALFRED-style vintage data is not implemented.
- Provider holdings / exposure as-of dates may be current snapshots relative to the decision date; they should not be described as historical truth.
- Portfolio Monitoring saved snapshot provenance is likely a follow-up because this slice first stabilizes validation / Final Review read models.
- Full `tests.test_service_contracts` currently has one unrelated date-sensitive futures macro thermometer failure because the fixture's latest candle is 2026-06-02 and the current session date is 2026-06-09.

## Mitigations

- Use explicit `decision_effect.treat_as_pass` and risk fields so stale / proxy / current-only rows cannot silently become pass.
- Keep docs clear that no raw/full rows move to workflow JSONL.
- Use focused service tests around stale/provider/current lifecycle/runtime evidence.
- Keep the provenance contract neutral for sparse legacy packet stubs so older saved/evidence fixtures do not become false selected-route blockers.
