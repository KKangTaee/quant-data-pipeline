# Phase 13 Docs / Runbook Alignment V1 Notes

Status: Complete
Created: 2026-05-30

## Notes

- `BACKTEST_UI_FLOW.md` still had several current-flow references to `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`; those were aligned to `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl`.
- `GLOSSARY.md` described Final Review using the legacy decision file; current definitions now mention V2 and identify V1 only as legacy history.
- `STORAGE_GOVERNANCE.md` already had the main storage model but needed Phase 13 audit notes about runtime-defined files and local absence before first write.
- A new runbook is justified because closeout QA commands and generated artifact exclusions repeat across phases.
