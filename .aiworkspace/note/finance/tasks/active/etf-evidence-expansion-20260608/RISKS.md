# Risks

Status: Completed
Last Verified: 2026-06-08

## Open Risks

| Risk | Mitigation |
|---|---|
| ETF evidence panel is mistaken for current-candidate creation | Keep storage boundary explicit and avoid registry writes. |
| GRS / Risk Parity / Dual Momentum are promoted to GTAA maturity too early | Keep maturity as evidence-expansion / low-evidence until current anchor evidence exists. |
| Provider / cost evidence is treated as present without data | List required evidence as future workflow, not as pass status. |
| UI becomes another generic guide | Tie rows to concrete current anchor, near miss, not-ready reason, and next workflow. |

## Remaining Risk

- The panel is intentionally read-only; ETF current-anchor evidence, rerun matrix, and provider / cost evidence remain future implementation work.
