# Phase 3. Quarterly Correctness Gate Status

## 2026-06-30

- Added `finance.financial_source_policy` with quarterly safe form filtering and unsafe flow sanitization helpers.
- Connected `build_fundamentals_history_from_statement_values()` so quarterly `10-K` / `10-K/A` records clear flow columns and keep balance sheet instant values separate.
- Updated statement fundamentals loader to return only `10-Q` / `10-Q/A` quarterly rows.
- Updated statement factors loader to join `nyse_fundamentals_statement` for `latest_form_type`, expose `form_type`, and apply the same quarterly gate.
- Updated data docs to clarify this phase is a policy-layer gate, not a destructive table cleanup.

## Browser QA

- Not applicable for this phase. No UI surface was changed.
