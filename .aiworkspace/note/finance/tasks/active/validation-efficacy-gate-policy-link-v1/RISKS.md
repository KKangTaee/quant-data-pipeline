# Risks

- Some existing saved validation rows do not include `validation_efficacy_audit`; the evidence packet fallback should still build one from compact validation data.
- If the fallback audit returns `NEEDS_INPUT` for old rows, selected-route may be stricter than legacy behavior. That is intentional for new selected decisions but should be visible in the gate policy.
- This task gates the audit route, but it does not collect missing PIT / survivorship / provider evidence. Data Coverage Hardening is still needed for stronger proof.
