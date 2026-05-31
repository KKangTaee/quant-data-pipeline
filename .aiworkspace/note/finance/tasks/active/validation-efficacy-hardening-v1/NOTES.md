# Notes

- P3 closeout completed selected monitoring connectivity. This task starts the next hardening layer.
- The audit should operate on existing compact evidence and never require raw provider rows in JSONL.
- The audit should be conservative: unknown or missing evidence is `NEEDS_INPUT` / `REVIEW`, not pass.
- `validation_efficacy_audit_v1` is a read model, not a new workflow registry.
- Survivorship / universe evidence is deliberately conservative. If explicit historical universe / delisting evidence is not attached, the row remains `REVIEW`.
- PIT / look-ahead audit is based on runtime replay, period coverage, and curve provenance. It improves visibility but does not prove every strategy family is strict PIT.
- Provider evidence remains current-as-of validation evidence. Stale, unknown, or `NOT_RUN` freshness is not promoted to pass.
