# Risks

- Some existing result bundles may lack enough metadata to prove PIT correctness. The correct first behavior is to surface the gap, not infer safety.
- This task improves evidence visibility, but does not fully solve survivorship bias or PIT data lineage across all strategy families.
- The current audit is visible in the investability packet but does not yet hard-gate selected-route policy. A later task can decide whether specific `Validation Efficacy` statuses should become blocking policy groups.
- Existing saved validation rows will not have `validation_efficacy_audit` unless they are regenerated or passed through a read-model fallback.
