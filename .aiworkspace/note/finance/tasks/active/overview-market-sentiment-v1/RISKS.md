# Overview Market Sentiment V1 Risks

| Risk | Impact | Mitigation |
|---|---|---|
| CNN internal JSON endpoint changes or blocks requests | Fear & Greed collection partial / failed | Keep source failure in job result and UI stale/missing state |
| AAII bot protection blocks default Python HTML access | AAII collection partial / failed | Use official HTML table with browser-like document headers and `curl_cffi` browser impersonation; expose failure instead of fabricating values |
| Sentiment interpreted as trading signal | Misleading user flow | UI copy and docs keep market-context-only boundary |
| Interpretation copy feels too decisive | User may read context as forecast / approval | Keep phase language contextual, include driver split and next-check targets, and leave Practical Validation / live trading boundaries unchanged |

## Resolved During QA

- Browser QA found Altair v6 rejects `cornerRadiusRight`; fixed to the existing project pattern `cornerRadiusEnd`.
- Initial AAII backend request returned `Pardon Our Interruption`; using `curl_cffi` with official page request headers now stores AAII rows in smoke.
