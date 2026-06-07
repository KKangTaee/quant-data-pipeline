# Overview Market Sentiment V1 Risks

| Risk | Impact | Mitigation |
|---|---|---|
| CNN internal JSON endpoint changes or blocks requests | Fear & Greed collection partial / failed | Keep source failure in job result and UI stale/missing state |
| AAII bot protection blocks default Python HTML access | AAII collection partial / failed | Use official HTML table with browser-like document headers and `curl_cffi` browser impersonation; expose failure instead of fabricating values |
| Sentiment interpreted as trading signal | Misleading user flow | UI copy and docs keep market-context-only boundary |
| Interpretation copy feels too decisive | User may read context as forecast / approval | Keep phase language contextual, include driver split and next-check targets, and leave Practical Validation / live trading boundaries unchanged |
| Practical Validation overlay is mistaken for a gate module | User may think risk-off blocks a candidate or risk-on approves one | Render as a separate context overlay, not a numbered validation step; service output uses `context_only`, `gate_effect=none`, and `registry_write=false` |
| Downstream overlay is mistaken for selected-route or monitoring signal input | User may think Final Review / Portfolio Monitoring sentiment changes save readiness or scenario signals | Surface overlay below/near command context only, and keep service boundary `saved_setup_write=false`, `monitoring_signal=false`, `registry_write=false`, `gate_effect=none` |

## Resolved During QA

- Browser QA found Altair v6 rejects `cornerRadiusRight`; fixed to the existing project pattern `cornerRadiusEnd`.
- Initial AAII backend request returned `Pardon Our Interruption`; using `curl_cffi` with official page request headers now stores AAII rows in smoke.
