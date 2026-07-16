# Overview Market Context U.S. Economic Cycle V1 Risks

Last Updated: 2026-07-16

| Risk | Impact | Mitigation / Decision |
|---|---|---|
| Missing `FRED_API_KEY` | Actual vintage bootstrap cannot run | Fail explicitly; continue fixture implementation; never use revised CSV as training substitute |
| Sparse recovery/recession samples | Horizon publication gate may fail | Per-horizon `LIMITED`; preserve threshold and reason code |
| Later revisions leak into replay | Inflated historical accuracy | Real-time interval table, strict as-of loader, adversarial revision tests |
| Full-sample scaling/calibration leak | Miscalibrated probabilities | Expanding median/MAD and rolling-origin out-of-fold calibration |
| Financial variables dominate current label | User model meaning is lost | Labels and h0 feature allowlist use activity/labor only |
| UI looks like deterministic forecast | False confidence | Show all four probabilities, dotted forecast markers, caveat, LIMITED state |
| Large raw payload enters Streamlit | Slow and coupled UI | Persist compact snapshots; service truncates evidence/history |
| Existing valuation navigation regresses | Breaks current Market Context use | Optional selector-hidden compatibility contract and focused regression/Browser QA |
| Actual model underperforms baseline | No trustworthy forecast | Do not publish numeric horizon; document evidence gap without lowering gate |
