# Overview Market Context U.S. Economic Cycle V1 Risks

Last Updated: 2026-07-16

| Risk | Impact | Mitigation / Decision |
|---|---|---|
| Missing or exposed `FRED_API_KEY` | Collection cannot run safely; a chat-pasted key must be treated as exposed | Fail closed without the environment variable; never persist credentials; rotate the issued key after this run |
| Uneven official vintage depth | Forecast-context history is shorter than revised chart history | Preserve official intervals only. BAMLH0A0HYM2 begins 2023-07 in the vintage API; no revised CSV backfill |
| Large ANFCI revision ledger | Initial bootstrap has 1,014,042 ANFCI rows | Long-form 50,000-row pages, 60-second timeout, 16MB safe UPSERT statements, page-wise persistence |
| Sparse recovery/recession samples | Horizon publication gate may fail | Per-horizon `LIMITED`; preserve threshold and reason code |
| Later revisions leak into replay | Inflated historical accuracy | Real-time interval table, strict as-of loader, adversarial revision tests |
| Full-sample scaling/calibration leak | Miscalibrated probabilities | Expanding median/MAD and rolling-origin out-of-fold calibration |
| Financial variables dominate current label | User model meaning is lost | Labels and h0 feature allowlist use activity/labor only |
| UI looks like deterministic forecast | False confidence | Show all four probabilities, dotted forecast markers, caveat, LIMITED state |
| Large raw payload enters Streamlit | Slow and coupled UI | Persist compact snapshots; service truncates evidence/history |
| Existing valuation navigation regresses | Breaks current Market Context use | Optional selector-hidden compatibility contract and focused regression/Browser QA |
| Actual model underperforms baseline | No trustworthy forecast | Do not publish numeric horizon; document evidence gap without lowering gate |

## Closeout Gaps

- Actual probability publication is still blocked. h0 has 192 origins but ECE `0.1694` and complete-feature ratio `0.7402`; h1/h2 have only 104/103 origins and underperform at least one approved baseline criterion.
- A later research task may investigate longer licensed PIT sources, horizon-specific coverage measurement, and stronger forecast-safe calibration. It must not lower the locked thresholds merely to force `READY`.
- One unrelated existing Sentiment source-contract assertion still expects a literal `payload.summary.metrics.map` string that the current Sentiment component does not contain. No Sentiment code was changed in this task.
