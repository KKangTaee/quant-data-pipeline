# Selected Provider Evidence Staleness Contract V1 Notes

Status: Complete
Created: 2026-05-29

## Notes

- This task intentionally keeps provider collection out of the dashboard.
- The existing provider context remains the read source; the selected dashboard runtime now applies a stricter selected-monitoring policy on top of it.
- `Macro Context` remains outside the required selected provider areas; the required selected provider areas are operability, holdings, and exposure.
- The provider symbol source now shares the selected recheck contract priority where possible: Final Review embedded contract, Current Candidate Registry fallback, then selected component fallback as review.
