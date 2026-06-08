# Robustness Experiment Registry Risks

## Open Risks

- Run-set id derivation must be deterministic enough for citation, but should not imply an append-only persistent registry unless a future task explicitly adds one.
- Existing Practical Validation result snapshots may not have every field; the read model needs tolerant fallbacks.
- If Final Review treats run-set presence as PASS, it could weaken validation. The run-set must preserve `NOT_RUN` / `REVIEW` / `BLOCKED` as non-pass evidence.
- Browser QA was limited by current local state: Final Review rendered saved records, but current gate-passed candidates did not necessarily include a freshly generated run-set snapshot. Service contracts cover the run-set read model and packet snapshot behavior.
