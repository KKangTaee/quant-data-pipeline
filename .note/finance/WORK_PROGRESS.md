# Finance Work Progress

## Purpose
This file is the current, concise implementation log for `finance` package work.

Keep here:
- current active workstream
- recent major milestones
- durable handoff notes

Detailed historical logs were archived on `2026-04-13`.

## Active Pointers

- current phase board:
  - [PHASE16_CURRENT_CHAPTER_TODO.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase16/PHASE16_CURRENT_CHAPTER_TODO.md)
- current candidate summary:
  - [CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md)
- historical full archive:
  - [WORK_PROGRESS_ARCHIVE_20260413.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/archive/WORK_PROGRESS_ARCHIVE_20260413.md)

## Entries

### 2026-04-13
- Compressed the root work log into a concise active-context version.
- Moved the previous full log to:
  - `.note/finance/archive/WORK_PROGRESS_ARCHIVE_20260413.md`
- Added a one-page current-candidate summary and code-flow/operator docs so future backtest refinement work can restart faster.

### 2026-04-13
- Continued Phase 16 as a downside-focused practical refinement track for both `Value` and `Quality + Value`.
- Confirmed `Value` current best practical point still remains:
  - `Top N = 14 + psr`
  - `CAGR = 28.13%`
  - `MDD = -24.55%`
  - `real_money_candidate / paper_probation / review_required`
- Confirmed the most useful lower-MDD `Value` near-miss:
  - `+ pfcr`
  - `CAGR = 27.22%`
  - `MDD = -21.16%`
  - but `production_candidate / watchlist`

### 2026-04-13
- Confirmed new `Quality + Value` current strongest practical point:
  - `net_margin -> operating_margin`
  - `ocf_yield -> pcr`
  - `operating_income_yield -> por`
  - `Top N = 10`
  - `Candidate Universe Equal-Weight`
  - `CAGR = 31.82%`
  - `MDD = -26.63%`
  - `real_money_candidate / small_capital_trial / review_required`

### 2026-04-13
- Added repo-local Codex workflow support artifacts:
  - current candidate summary
  - backtest refinement code-flow guide
  - runtime artifact hygiene guide
  - repo-local plugin scaffold:
    - `plugins/quant-finance-workflow`
  - repo-local skill draft:
    - `finance-backtest-candidate-refinement`
  - first practical plugin script:
    - `plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`

### 2026-04-13
- Promoted the finance refinement hygiene script into an explicit operating rule.
- Synced:
  - `AGENTS.md`
  - `RUNTIME_ARTIFACT_HYGIENE.md`
- Default usage points are now:
  - after meaningful refinement/doc-sync units
  - before commit
  - before phase closeout

### 2026-04-13
- Closed Phase 16 as a bounded downside-refinement phase.
- `Value`:
  - current best practical point remains `Top N = 14 + psr`
  - `28.13% / -24.55% / real_money_candidate / paper_probation / review_required`
  - lower-MDD near-miss `+ pfcr` improved `MDD` to `-21.16%` but only reached `production_candidate / watchlist`
- `Quality + Value`:
  - current strongest practical point remains
    `operating_margin + pcr + por + per + Top N 10 + Candidate Universe Equal-Weight`
  - `31.82% / -26.63% / real_money_candidate / small_capital_trial / review_required`
  - lower-MDD alternatives existed, but all weakened gate quality
- Synced:
  - Phase 16 closeout docs
  - strategy hubs / backtest logs
  - roadmap / doc indexes

### 2026-04-14
- Clarified compare / weighted portfolio / saved portfolio workflow semantics.
- Current reading:
  - `Compare` = research surface for side-by-side strategy inspection
  - `Weighted Portfolio` = monthly composite of compared strategies
  - `Saved Portfolio` = replayable research artifact for compare -> builder -> rerun
- Durable note:
  - weighted bundles do not create new real-money / promotion / shortlist / deployment semantics on their own
  - Phase 17 should document them as operator bridges, not as independent candidate gates
