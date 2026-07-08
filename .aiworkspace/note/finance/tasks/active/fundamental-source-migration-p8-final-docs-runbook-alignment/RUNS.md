# Runs

## Verification

- `git diff --check`
  - Result: passed.
- `find .aiworkspace/note/finance/docs -maxdepth 3 -type f | sort`
  - Result: passed; docs tree listed successfully.
- `rg -n "production financial statement source|canonical financial statement source|legacy broad yfinance|EDGAR annual" .aiworkspace/note/finance/docs .aiworkspace/note/finance/tasks/active/fundamental-source-migration-p8-final-docs-runbook-alignment`
  - Result: passed; source-policy terms are present in durable docs and the closeout task.

## QA Notes

- This phase is documentation/runbook alignment only. Browser QA was not repeated because no UI code changed after Phase 7.
