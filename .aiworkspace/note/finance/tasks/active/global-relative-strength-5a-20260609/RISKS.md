# Global Relative Strength 5A Risks

## Open Risks

- Changing interval semantics can alter historical GRS performance for `interval > 1`; this is intentional because the previous path could compound cadence. The focused TDD test fixes the new contract.
- Excluding risky tickers after preflight must not make cash proxy optional. 5A keeps cash proxy and ticker benchmark as blocking preflight checks.
- Benchmark contract changes must not create provider fetches or registry writes. 5A only preserves runtime metadata and passes the contract into existing real-money hardening.
- UI changes must stay within existing result display / copy; no new workbench or evidence panel should be added. 5A only reuses existing Selection History and copy.

## Remaining Follow-Up

- Future ETF strategy hardening can apply the same cash / benchmark / concentration contract review to Risk Parity Trend and Dual Momentum, but that is outside 5A.
