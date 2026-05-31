# Phase 8 Investability Data Evidence Expansion Risks

Status: Complete
Created: 2026-05-28

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Form 25 interpreted as complete historical membership | False survivorship PASS | Keep Form 25 as delisting event only; no first listing proof |
| Current listing snapshot interpreted as historical universe | Look-ahead / survivorship bias | Keep source type partial and audit REVIEW |
| Free source coverage is incomplete | Phase 8 may not fully solve lifecycle evidence | Surface coverage gaps as REVIEW / NEEDS_INPUT |
| Schema grows without source contract | Hard-to-maintain table semantics | Add only event fields needed for source-normalized rows |
| New ingestion creates storage sprawl | User concern regression | DB only for evidence data; no memo / preset JSONL |
| Nasdaq Daily List is paid / approval based | Strongest action source is not available under free-source-first constraint | Park it; use public current Symbol Directory snapshot path first |
| Current snapshot absence is over-interpreted | False delisting / inactive evidence | Treat current snapshots as partial `listing_observed`; repeated snapshot diff needs separate conservative policy |
| Computed row treated as actual history | False survivorship PASS | Store Phase 8-5 computed rows as partial and require `coverage_status=actual` for PASS |
| Audit scoring hides weak evidence type | Operator may over-trust partial evidence | Split current snapshot / SEC identity / computed partial / actual / delisting metrics |

## Open Questions

- Which free / official source should supply historical membership or ticker action events after Form 25?
- Should future computed snapshot coverage ever be marked `actual`, and what archive / continuity contract would justify that?
- How should old ticker -> new ticker mapping affect backtest replay symbols?

## Carry Forward

- These open questions move to Phase 9+ planning, not Phase 8 implementation.
- Phase 9 should focus on cost / slippage / turnover / liquidity realism before reopening corporate-action source expansion.

## Source Review Result

- No free / official complete historical membership source was selected in this review.
- The next implementation source is Nasdaq public Symbol Directory current files.
- SEC current ticker / exchange and Submissions metadata remain supporting identity / CIK sources.

## Symbol Directory Ingestion Result

- Public Symbol Directory ingestion is implemented.
- It improves current listing snapshot coverage but does not by itself satisfy historical survivorship PASS.
- Repeated snapshots and SEC cross-check remain separate follow-up tasks.

## SEC Cross-Check Result

- SEC current CIK / ticker / exchange ingestion is implemented.
- It improves identity evidence but does not prove historical membership or ticker actions.
- SEC file differences from exchange files should remain REVIEW evidence until a future scoring policy is defined.

## Computed Snapshot Lifecycle Result

- Computed snapshot lifecycle ingestion is implemented.
- It summarizes repeated current snapshot observation windows as partial `computed_from_snapshots` evidence.
- Data Coverage Audit now requires `coverage_status=actual` before lifecycle evidence can make survivorship PASS.

## Lifecycle Audit Scoring Result

- Data Coverage Audit lifecycle evidence scoring is refined.
- Audit metrics now separate actual coverage, actual non-covering rows, current snapshot symbols, SEC identity cross-check symbols, computed partial symbols, and delisting actual symbols.
- Survivorship REVIEW evidence now names the partial evidence classes instead of collapsing everything into generic current listing evidence.
