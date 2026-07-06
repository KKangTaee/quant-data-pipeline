# Notes

Status: Completed
Date: 2026-07-06

## Decisions

- `selected_route_preflight` still blocks Final Review movement when selected-route policy predicts a deterministic storage gap, but it is not counted as a Flow 4 validation category.
- `stress_robustness` missing evidence is not pass. It is `REVIEW` by default, so users see it as a Final Review check rather than a universal blocker.
- `construction_risk` is not meaningful as a universal blocker for single non-ETF factor sources. It now applies to ETF-like or weighted mix candidates.
- sentiment risk-on/off overlay remains useful context, but it does not decide macro gate status.

## Follow-Up Candidates

- Split `validation_efficacy` row ownership further so duplicated source / replay / benchmark / provider rows do not double-count blockers.
- Consider row-level category summaries for Data Coverage and Backtest Realism instead of module-level category cards.
- Browser QA confirmed the category-first Flow 4 structure; a later visual polish pass can still refine card density.
