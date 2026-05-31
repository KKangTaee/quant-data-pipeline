# Storage Governance Audit V1 Notes

Status: Complete
Created: 2026-05-28

## Observations

- The current V2 product chain is intentionally compact and should be protected.
- Candidate Review, Portfolio Proposal, Paper Ledger, and Final Review V1 registries are still present because older screens and helpers read them.
- `CANDIDATE_REVIEW_NOTES.jsonl` is the clearest user memo storage risk. It should not become a required main-flow step.
- `SAVED_PORTFOLIOS.jsonl` is a reusable setup store, not a registry. Its update/delete behavior rewrites the file, so it is not append-only.
- `BACKTEST_RUN_HISTORY.jsonl` includes wide execution metadata and dynamic universe artifacts. This is useful for replay/debug but too broad to be treated as an investment decision record.
- Existing boundary lint already blocks staged registry / saved / run-history JSONL through `.aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`.

## Storage Direction

- Keep a small number of product workflow JSONL files only where a later stage must read them.
- Prefer compact snapshots over repeated full payload storage.
- Do not put raw provider / holdings / macro series into workflow JSONL.
- Preserve existing user data and legacy registries; deprecate by reducing new dependencies, not by deleting files.
- Treat reports under `.aiworkspace/note/finance/reports/backtests/` as human-readable evidence, not as registry replacements.

## Follow-Up Candidates

- Add a small storage governance lint that flags new `*.jsonl` path constants outside approved runtime modules.
- Plan a compatibility migration for `SAVED_PORTFOLIOS.jsonl` only after confirming replay users and current saved setup expectations.
- Remove main-flow UI dependence on legacy candidate/proposal registries only after a separate UX approval.
