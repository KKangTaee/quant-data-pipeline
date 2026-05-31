# Real-Money Promotion Route Absorption V1 Risks

## Known Risks

- Internal metadata still uses `shortlist_status`, `shortlist_next_step`, and `shortlist_rationale` for compatibility. The user-facing Real-Money screen maps those values to Promotion route wording.
- Runtime metadata / saved historical records can still contain old internal field names. This task intentionally did not migrate stored records or change the calculation contract.
- Existing tests may assert old UI strings if such tests are added later.
