# Overview Market Context Turnaround Stage Semantics Fix V1 Runs

Last Updated: 2026-07-16

## Diagnosis

- `build_market_context_valuation_read_model(selected_symbol="AAPL")` read-only actual: PER READY/current P/E `39.324x`; turnaround `CASH_FLOW_TURN`, EPS null, PER_READY NOT_MET.
- DB read-only EPS audit: latest AAPL diluted EPS `2.84`, unit `USD per share`, period end `2025-12-27`, available `2026-01-30`.
- Runtime-only allowlist hypothesis test: TTM EPS `7.90`, headline `PER_READY`, PER_CANDIDATE/PER_READY MET.
- No provider call, DB write, registry append, source edit, or generated artifact was produced during diagnosis.
