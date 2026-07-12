# Risks

- React action wiring can duplicate saves on rerun if nonce consumption is missing.
- Flow3 CTA copy must not imply final approval, live trading, broker order, or auto rebalance.
- Component build output must be regenerated after React changes.
- Fresh Browser QA must use a newly started Streamlit process because existing QA servers run with `runOnSave=false` and can show stale Flow5 UI.
