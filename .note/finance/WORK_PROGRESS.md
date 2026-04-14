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
  - [PHASE17_CURRENT_CHAPTER_TODO.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase17/PHASE17_CURRENT_CHAPTER_TODO.md)
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

### 2026-04-14
- Opened Phase 17 as a structural downside-improvement phase.
- Synced:
  - phase kickoff plan
  - current board
  - structural lever inventory first pass
  - candidate consolidation fit review first pass
  - code-flow guide
  - repo-local refinement skill reference
- Current reading:
  - immediate main track:
    - strict annual structural downside levers
  - secondary/supporting track:
    - weighted portfolio / saved portfolio as operator bridge
- Current first-slice recommendation:
  - `partial cash retention` before broader defensive-sleeve or weighting redesign

### 2026-04-14
- Clarified near-term development order before Phase 17 implementation.
- Current order:
  - first:
    - existing core strategy structural refinement
  - second:
    - candidate consolidation / operator bridge cleanup
  - later:
    - new strategy or wider expansion work
- Durable takeaway:
  - new strategy work is still planned,
    but it is intentionally behind the current `Value / Quality + Value` structural downside-improvement track

### 2026-04-14
- Implemented the first Phase 17 structural lever slice:
  - strict annual `partial cash retention`
- Wired through:
  - `finance.strategy.quality_snapshot_equal_weight(...)`
  - strict annual DB-backed sample/runtime wrappers
  - strict annual single / compare forms
  - selection interpretation / warnings / input params
- Current rule:
  - applies only when `Trend Filter` partially rejects raw selected names
  - does not replace full-cash `market regime` / guardrail risk-off behavior
- Verification:
  - `py_compile` passed
  - synthetic smoke confirmed
    - `off` = survivor reweighting
    - `on` = rejected slots retained as cash
  - representative DB-backed rerun is still gated by local shadow-factor data availability

### 2026-04-14
- Ran the first Phase 17 representative rerun on real current anchors.
- Cases:
  - `Value` current practical anchor:
    - `Top N = 14 + psr`
    - `Trend Filter = on`
    - `cash retention off/on`
  - `Quality + Value` strongest practical point:
    - strongest factor set
    - `Trend Filter = on`
    - `cash retention off/on`
- Result:
  - `partial cash retention` worked and materially lowered `MDD` in both families
  - but both cases still stayed `hold / blocked`
  - main pattern:
    - downside improved strongly
    - cash share rose materially
    - return drag remained too large for practical gate rescue
- Updated:
  - Phase 17 representative rerun report
  - strategy hubs
  - strategy backtest logs
  - current candidate summary
- Next priority:
  - `defensive sleeve risk-off` over another cash-only follow-up

### 2026-04-14
- Implemented the second Phase 17 structural lever slice:
  - strict annual `defensive sleeve risk-off`
- Wired through:
  - `finance.strategy.quality_snapshot_equal_weight(...)`
  - strict annual DB-backed sample/runtime wrappers
  - strict annual single / compare forms
  - warning / meta / interpretation surface
- Important correction:
  - defensive sleeve ticker was separated from strict annual candidate-universe filtering
  - this removed the false `Liquidity Excluded Count` inflation that appeared in the first rerun
- Representative rerun result after the correction:
  - `Value` current anchor:
    - gate unchanged
    - `MDD` slightly worse
  - `Quality + Value` current strongest point:
    - gate unchanged
    - `MDD` slightly worse
- Durable takeaway:
  - `defensive sleeve risk-off` is now implemented and verifiable
  - but it did not produce a same-gate lower-MDD rescue on the current anchors
  - next structural lever priority moves to `concentration-aware weighting`

### 2026-04-14
- Reviewed strict annual reuse points for `concentration-aware weighting`.
- Key finding:
  - no existing rank-based taper/capped position-weight contract was found in the strict annual family
  - the safest first slice remains the `quality_snapshot_equal_weight(...)` rebalancing block after top-N selection
- Reusable runtime contract:
  - keep `strategy_key` / `snapshot_mode` / `snapshot_source` / `factor_freq` / `universe_contract` / dynamic universe fields aligned with the current strict annual wrappers

### 2026-04-14
- Implemented the third Phase 17 structural lever slice:
  - strict annual `concentration-aware weighting`
- Wired through:
  - `finance.strategy.quality_snapshot_equal_weight(...)`
  - strict annual DB-backed sample/runtime wrappers
  - strict annual single / compare forms
  - warning / meta / interpretation surface
- Current contract:
  - `equal_weight`
  - `rank_tapered`
- Representative rerun result:
  - `Value` current anchor:
    - gate unchanged
    - `MDD` worse
    - `Rolling Review` also weakened
  - `Quality + Value` current strongest point:
    - gate unchanged
    - `CAGR` higher
    - but `MDD` worse
- Durable takeaway:
  - `concentration-aware weighting` is now implemented and verifiable
  - but it did not produce a same-gate lower-MDD rescue on the current anchors
  - next active question moves to
    Phase 17 closeout vs next structural lever reprioritization

### 2026-04-14
- Closed Phase 17 as a structural downside-improvement phase.
- Practical closeout reading:
  - `partial cash retention`
  - `defensive sleeve risk-off`
  - `concentration-aware weighting`
  first three slices are now implemented and representative-rerun verified
- Common conclusion:
  - no same-gate lower-MDD exact rescue was found for
    current `Value` / `Quality + Value` anchors
  - current practical anchors remain unchanged
- Synced:
  - Phase 17 completion summary
  - next-phase preparation
  - manual test checklist
  - roadmap / finance doc index
