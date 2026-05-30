# Practical Validation Required Module Polish V1 Notes

Status: Implementation complete
Created: 2026-05-30

## Decisions

- Keep all eight required modules.
- Treat `Benchmark / Comparator Parity` as the user-facing label while preserving the existing `Benchmark parity` input check key.
- Do not make advanced parameter perturbation a hard requirement inside `Stress / Robustness`.
- Add display-level gate effect fields instead of changing registry schema or adding persistence.
- `Gate Effect` values are display/read-model fields: `Blocks Final Review`, `Final Review review`, `Reference only`, `Not applicable`, or `Ready`.

## Dirty Tree Context

- Existing local generated changes remain in `BACKTEST_RUN_HISTORY.jsonl`, `PORTFOLIO_SELECTION_SOURCES.jsonl`, `finance/.DS_Store`, and the previous Browser QA screenshot.
- They are not part of this implementation.
