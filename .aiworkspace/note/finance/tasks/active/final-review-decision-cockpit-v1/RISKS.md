# Final Review Decision Cockpit V1 Risks

Status: Active
Created: 2026-05-31

## Risks

| Risk | Mitigation |
| --- | --- |
| Candidate Board duplicates packet logic and drifts from save gate | Build board rows from the same investability packet and selected-route gate helpers used by Final Review save evaluation. |
| UI becomes heavier | Put cockpit summary first and keep detailed evidence in existing sections / expanders. |
| New wording sounds like live approval | Keep explicit no-live-approval / no-order copy and disabled order button. |
| Existing generated registry / screenshot artifacts pollute commit | Do not stage run history, registries, screenshots, `.DS_Store`, or other generated artifacts. |

## Residual

- Candidate Board currently compares Final Review eligible candidates only. Blocked Practical Validation results remain hidden from the candidate picker by design.
- This slice does not implement structured waiver UI / persistence; selected-route blocker behavior remains strict.
- Browser QA used existing local Practical Validation registry rows and did not create new decision records.
