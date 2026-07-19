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

## 2026-07-16 Task 3 — UI Disclosure

- RED: React contract failed because provenance types, marker, badge and disclosure copy were absent.
- GREEN: source marker, neutral badge, known-rule formula and TTM derived-input notice are present without `추정값` copy.
- Regression: Market Context/turnaround 71/71 PASS.
- Build: Vite 6.4.3 transformed 171 modules and emitted production bundle successfully.
- Static: hashed JS/CSS assets were replaced by the new product build; no screenshot/temp artifact was staged.

## 2026-07-16 Task 4 — Actual, Regression, Browser QA And Closeout

- Actual MRNA DB-only: turnaround `READY`, statement basis `2026-03-31`; 2023-Q4 revenue `2.811B`, cost `0.929B`, GP `1.882B`, operating income `0.006B`.
- Provenance: 2023-Q4 revenue is `FILING_DERIVED/fy_minus_q1_q2_q3` with FY/Q1/Q2/Q3 operands across both allowlisted revenue concepts. Gross profit is `FILING_DERIVED/revenue_minus_cost`.
- Continuity: 2024-Q1~Q3 TTM revenue is `5.153B`, `5.050B`, `5.081B`; TTM GP margin is `22.43%`, `33.05%`, `67.45%`; TTM operating margin is `-99.73%`, `-91.78%`, `-53.00%`.
- Direct/derived audit: actual AAPL and RIVN retain both direct rows and filing-derived rows; latest AAPL 2026-Q1 has no source-quarter derived metric, while its TTM disclosure correctly includes earlier derived inputs. No direct fact is relabeled solely because it sits in a derived TTM window.
- Focused final regression: turnaround/PER/Market Context 112/112 PASS; target `py_compile` PASS.
- Production build: Vite 6.4.3 transformed 171 modules and emitted `index-CeD8Ovhi.js` / `index-edHDWO--.css` after the final TTM-value visibility guard.
- Isolated repository regression: 1,107 tests, 1,103 PASS, 4 existing unrelated failures. Failures remain the same Practical Validation source contracts 2, Market Movers rows-written contract 1, and Sentiment source-token contract 1.
- Browser QA: actual MRNA desktop inspector selected 2023-Q4 and showed `2.81B`, `6M`, TTM GP `31.5%`, TTM operating `-61.9%`, and `FY 6.85B − Q1 1.86B − Q2 344M − Q3 1.83B`.
- Responsive QA: 420px outer/component horizontal overflow were both 0; marker/badge/formula remained readable and no browser console errors were recorded.
- Closeout review RED/GREEN: added `activeTtmValueAvailable` contract so the TTM notice is rendered only when the corresponding TTM number is finite; source contract and final production build pass.
- Screenshot: `/Users/taeho/.codex/attachments/mrna-turnaround-derived-qa.png` is a generated QA artifact and was not staged.
