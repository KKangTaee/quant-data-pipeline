# Construction Risk Gate Policy V1 Notes

## 2026-05-29

- The selected-route policy now owns construction risk explicitly instead of leaving the evidence split across `provider_coverage` and `stress_robustness`.
- Construction risk gaps are treated like other investability gates: `REVIEW` blocks selection until hold / re-review, and `NEEDS_INPUT` / `BLOCKED` blocks selected-route.
- Existing concentration / correlation diagnostic findings now merge into the construction-specific groups instead of staying in generic provider / stress groups.
- The task did not add persistence. It only changes the read model and tests.
