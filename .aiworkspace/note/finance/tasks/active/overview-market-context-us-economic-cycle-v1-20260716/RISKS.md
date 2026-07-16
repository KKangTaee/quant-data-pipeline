# Overview Market Context U.S. Economic Cycle V1 Risks

Last Updated: 2026-07-16

| Risk | Impact | Mitigation / Decision |
|---|---|---|
| Missing `FRED_API_KEY` | Realized locally: actual vintage/bootstrap/model metrics cannot run | Schema/UI/failure path completed; collection fails explicitly; `LIMITED/NOT_MATERIALIZED` with no numbers; never use revised CSV as training substitute |
| Sparse recovery/recession samples | Horizon publication gate may fail | Per-horizon `LIMITED`; preserve threshold and reason code |
| Later revisions leak into replay | Inflated historical accuracy | Real-time interval table, strict as-of loader, adversarial revision tests |
| Full-sample scaling/calibration leak | Miscalibrated probabilities | Expanding median/MAD and rolling-origin out-of-fold calibration |
| Financial variables dominate current label | User model meaning is lost | Labels and h0 feature allowlist use activity/labor only |
| UI looks like deterministic forecast | False confidence | Show all four probabilities, dotted forecast markers, caveat, LIMITED state |
| Large raw payload enters Streamlit | Slow and coupled UI | Persist compact snapshots; service truncates evidence/history |
| Existing valuation navigation regresses | Breaks current Market Context use | Optional selector-hidden compatibility contract and focused regression/Browser QA |
| Actual model underperforms baseline | No trustworthy forecast | Do not publish numeric horizon; document evidence gap without lowering gate |

## Closeout Gaps

- Actual h0/h1/h2 origin counts, phase support, recession episodes, Brier/log loss/ECE and baseline comparisons are unknown until a valid `FRED_API_KEY` is configured and official vintages are collected.
- Payroll/recession-era official metadata spot checks and ten-year replay idempotence were not run against live rows because the tables are empty. Fixture/adversarial tests cover the contracts; runbook follow-up owns live evidence.
- One unrelated existing Sentiment source-contract assertion still expects a literal `payload.summary.metrics.map` string that the current Sentiment component does not contain. No Sentiment code was changed in this task.
