# Practical Validation Required Taxonomy Audit Risks

## Open Risks

1. Backward compatibility risk:
   - Existing validation result rows and Final Review evidence may use old `validation_efficacy` route names.
   - Mitigation: keep old route constants and internal ids during first refactor, change row ownership and visible labels first.

2. Gate policy regression risk:
   - Removing duplicate `validation_efficacy` rows could accidentally stop blocking missing runtime replay or data coverage.
   - Mitigation: owner modules must block those failures directly before removing duplicate rows.

3. UI mismatch risk:
   - Flow 4 currently has category labels that are close to the proposed taxonomy but not identical.
   - Mitigation: update UI labels only after service ownership tests pass.

4. Over-strict validation risk:
   - If every method-strength item becomes a universal blocker, Practical Validation can become unusably strict.
   - Mitigation: keep walk-forward / OOS / regime severity profile-aware. Some method gaps can be `REVIEW` rather than universal `NEEDS_INPUT`.

5. Portfolio construction scope risk:
   - Merging construction risk, risk contribution, and role/weight into one visible group can hide important weighted mix details.
   - Mitigation: keep them as sub-checks under one group, not as deleted checks.
