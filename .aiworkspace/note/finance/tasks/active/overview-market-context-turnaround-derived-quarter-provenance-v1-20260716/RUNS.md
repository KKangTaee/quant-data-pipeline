# Runs

## 2026-07-16 Diagnosis

- actual MRNA DB-only read model: turnaround `READY`, statement basis `2026-03-31`.
- timeline inspection: 2023-Q4 revenue/GP/TTM margin missing, operating income `+6M` present.
- raw statement inspection: FY2023 revenue `6.848B`, cost `4.693B`, operating income `-4.239B` present.
- resolver inspection: revenue Q1/Q2 and Q3/FY use two allowlisted concept names; exact concept grouping prevents Q4 derivation.
- UI inspection: `contiguousTurnaroundSegments` intentionally breaks non-finite slots; screen copy states no interpolation.

No production code or tests changed during diagnosis/design.

## 2026-07-16 Task 1 — Mixed-concept Q4

- Baseline: turnaround/PER/Market Context 104 tests PASS.
- RED: `test_resolver_derives_q4_across_allowlisted_revenue_concepts` failed with `StopIteration`; Q4 was absent.
- GREEN: the same test passed with revenue Q4 `2.811B`, available-at `2024-02-23`, and both revenue concepts in operands.
- Guards: direct Q4 precedence, explicit allowlist, future FY cutoff all PASS.
- Regression: resolver 9/9 and `tests.test_us_stock_turnaround` 40/40 PASS; target `py_compile` and `git diff --check` exit 0.

## 2026-07-16 Task 2 — Provenance

- RED: MRNA series and direct-only series failed with missing `metric_provenance` / `derived_metrics` keys.
- GREEN: MRNA Q4 revenue `2.811B`, GP `1.882B`, operating income `0.006B`; revenue/GP are `FILING_DERIVED`.
- TTM: 2024-Q1 carries revenue/GP in `ttm_derived_metrics`; direct-only fixture lists remain empty.
- Service: nested operands survive recursive JSON-safe conversion and `json.dumps`.
- Regression: turnaround/Market Context 70/70 PASS; target `py_compile` and `git diff --check` exit 0.
