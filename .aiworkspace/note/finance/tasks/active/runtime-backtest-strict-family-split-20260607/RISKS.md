# Risks

Status: Completed
Last Verified: 2026-06-07

## Residual Risks

- DB-backed strict strategy smoke was not run during the initial split because this refactor is intended to preserve wrapper behavior and avoid generating runtime artifacts.
- `app/runtime/backtest.py` still re-exports several helper/constants for compatibility. Later cleanup should only remove these after caller search and a compatibility decision.
- 7B Ingestion diagnostic facade remains unfinished. This is not a runtime blocker, but it should stay visible in the roadmap.
- Strict quarterly prototype semantics are unchanged. This task does not make quarterly prototypes equivalent to annual strict real-money / guardrail parity.

## Do Not Infer

- This split does not approve live trading, broker order execution, account sync, or auto rebalance.
- This split does not change point-in-time factor assumptions, survivorship risk, provider coverage, or result scoring.
