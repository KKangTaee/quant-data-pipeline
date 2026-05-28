# Phase 8 Investability Data Evidence Expansion Risks

Status: Active
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

## Open Questions

- Which free / official source should supply historical membership or ticker action events after Form 25?
- Should future computed snapshot coverage be allowed to make survivorship PASS, and under what source contract?
- How should old ticker -> new ticker mapping affect backtest replay symbols?

## Source Review Result

- No free / official complete historical membership source was selected in this review.
- The next implementation source is Nasdaq public Symbol Directory current files.
- SEC current ticker / exchange and Submissions metadata remain supporting identity / CIK sources.

## Symbol Directory Ingestion Result

- Public Symbol Directory ingestion is implemented.
- It improves current listing snapshot coverage but does not by itself satisfy historical survivorship PASS.
- Repeated snapshots and SEC cross-check remain separate follow-up tasks.
