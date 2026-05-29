# Construction Risk Source Map V1 Risks

Status: Complete
Created: 2026-05-29

## Residual Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Provider holdings / exposure coverage can be partial | Construction risk can be under-estimated | 11-2 must keep partial or missing provider evidence as `REVIEW` or `NEEDS_INPUT`, not `PASS` |
| Ticker proxy exposure can overstate certainty | Proxy-only source can look stronger than it is | 11-2 must expose source strength and limitations |
| Risk contribution is proxy-based | It can miss covariance-level contribution | 11-3 should label it as proxy and preserve source strength |
| Component role metadata is not first-class | Weight discipline can become arbitrary | 11-4 should decide role source before gate enforcement |
| Construction gate can duplicate provider / robustness gates | User can see repeated blockers | 11-5 should reuse evidence rows but make ownership clear |
