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
  - [PHASE20_CURRENT_CHAPTER_TODO.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase20/PHASE20_CURRENT_CHAPTER_TODO.md)
- current candidate summary:
  - [CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md)
- historical full archive:
  - [WORK_PROGRESS_ARCHIVE_20260413.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/archive/WORK_PROGRESS_ARCHIVE_20260413.md)

## Entries

### 2026-04-16
- User-facing Phase 20 checklist confirmation is now complete.
- Closed:
  - `PHASE20_CURRENT_CHAPTER_TODO.md` -> `phase complete / manual_validation_completed`
  - `PHASE20_COMPLETION_SUMMARY.md` -> reflects checklist completion
  - `PHASE20_CANDIDATE_CONSOLIDATION_AND_OPERATOR_WORKFLOW_HARDENING_PLAN.md` -> status synced to completion
- Meaning:
  - current candidate -> compare -> weighted -> saved -> replay/load-back workflow is now considered closed at the manual validation level

### 2026-04-16
- Phase 20 saved-portfolio QA exposed one real replay bug and one lingering UX gap.
- Fixed:
  - `Replay Saved Portfolio` could fail when stored compare overrides still contained legacy keys such as `factor_freq`
    that the current strict-annual runtime wrappers no longer accept
  - compare replay now filters unsupported kwargs against the current runner signature before execution
- Clarified:
  - `Save This Weighted Portfolio` now explains what `Portfolio Name` and `Description` are for
  - `Portfolio Name` starts from the current source label or strategy combination so the saved name reads less like an empty form
  - the saved-portfolio re-entry button now reads as `Load Saved Setup Into Compare`
    so it feels more like "restore settings" than "edit this record in place"

### 2026-04-15
- Applied a Phase 20 QA-driven UX clarification pass to `Current Candidate Re-entry`.
- Added:
  - clearer explanation that current candidate re-entry fills the compare form rather than running compare immediately
  - clearer explanation for `Load Current Anchors` and `Load Lower-MDD Near Misses`
  - registry-source explanation that the list is curated from `CURRENT_CANDIDATE_REGISTRY.jsonl`, not auto-filled by every run
  - a `What Changed In Compare` summary card that shows selected strategies, period, and key overrides after load

### 2026-04-15
- Fixed a strict-annual shadow sample parity bug found during manual backtest validation.
- Cause:
  - strict annual runtime wrappers started passing `rejected_slot_handling_mode`
    to the shadow DB sample entrypoints,
    but the three shadow helpers in `finance/sample.py`
    still only accepted the older boolean pair.
- Applied the fix to:
  - quality strict annual shadow path
  - value strict annual shadow path
  - quality+value strict annual shadow path
- Result:
  - the shadow sample entrypoints now accept the explicit rejected-slot handling contract
    and normalize it back into legacy flags before execution.

### 2026-04-15
- Continued Phase 20 through practical closeout.
- Added the second operator-workflow hardening unit:
  - compare source context now carries into weighted portfolio and saved portfolio flows
  - `Current Compare Bundle` summary now explains what the current compare run came from
  - saved portfolio actions and detail tabs were renamed/expanded to make next actions clearer
- Synced:
  - Phase 20 closeout docs
  - roadmap / doc index
  - finance analysis
  - current candidate registry guide
- Current reading:
  - Phase 20 is now `practical closeout / manual_validation_pending`
  - main remaining step is the user-facing checklist

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

### 2026-04-15
- Started the first real Phase 20 implementation unit.
- Added a `Current Candidate Re-entry` surface inside `Compare & Portfolio Builder`.
- Current anchors and lower-MDD near-misses can now be sent back into compare without manually rebuilding the full strict annual contract.
- Synced:
  - Phase 20 first work-unit document
  - phase TODO board
  - roadmap / doc index
  - finance comprehensive analysis
- Validation:
  - `py_compile`
  - `.venv` import smoke
  - current candidate registry helper smoke
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
- Follow-up review:
  - examined a possible first slice for filling trend-rejected raw top-N slots with next-ranked eligible names
  - safest candidate insertion point is still the strict annual rebalancing block in `finance/strategy.py`
  - this redesign should be treated as a separate interpretation lane from `partial cash retention` and `rank_tapered`, not as a cosmetic tweak to either one

### 2026-04-14
- Opened Phase 18 as `Larger Structural Redesign`.
- Implemented first slice:
  - strict annual `Fill Rejected Slots With Next Ranked Names`
- Wired through:
  - `finance.strategy.quality_snapshot_equal_weight(...)`
  - strict annual DB-backed sample/runtime wrappers
  - strict annual single / compare forms
  - history / rerun / interpretation surface
- New durable result/meta fields:
  - `Rejected Slot Fill Enabled`
  - `Rejected Slot Fill Active`
  - `Rejected Slot Fill Ticker`
  - `Rejected Slot Fill Count`
  - `rejected_slot_fill_enabled`
- Representative rerun first pass:
  - `Value` trend-on probe:
    - cash drag와 downside 개선 방향은 확인됐지만
      still `hold / blocked`
    - meaningful redesign reference로는 남지만
      current practical anchor replacement는 아니었다
  - `Quality + Value` trend-on probe:
    - `CAGR`, `MDD`, cash share improved
    - but still `hold / blocked`
- Durable takeaway:
  - next-ranked eligible fill is a meaningful larger-redesign lane
  - first pass does not replace the current practical anchors
  - next follow-up should stay in Phase 18 rather than reopening bounded tweak work

### 2026-04-14
- Re-ran Phase 18 `next-ranked eligible fill` around the actual `Value` practical anchor.
- Scope:
  - `base + psr`, `Top N = 12~16`
  - `base + psr + pfcr`, `Top N = 12~16`
  - `Trend Filter = on`, `rejected_slot_fill_enabled = on`
- Result:
  - no same-gate lower-MDD rescue was found
  - all anchor-near candidates remained `hold / blocked`
  - best lower-MDD near-miss was:
    - `base + psr + pfcr`, `Top N = 13`
    - `24.47% / -24.89% / hold / blocked`
- Durable takeaway:
  - Phase 18 first slice should be kept as a meaningful redesign reference,
    not as a rescued replacement candidate
  - next work should shift to Phase 18 second-slice prioritization

### 2026-04-14
- User direction changed Phase 18 from rerun-first to implementation-first.
- Current rule:
  - broader deep backtest / wider rescue search is paused
  - new implementation slices should be followed only by
    compile / import smoke and minimal representative validation
- Synced:
  - Phase 18 plan
  - current board
  - roadmap
  - finance doc index
- Durable takeaway:
  - next active work is not another broad rerun cycle
  - it is selecting and implementing the Phase 18 second slice first

### 2026-04-14
- Rebased the upper roadmap from current `Phase 18` status through a new `Phase 25` draft.
- Current reading:
  - `Phase 18~21`
    - implementation / operator / automation backlog
  - `Phase 22`
    - integrated deep backtest validation restart
  - `Phase 23~25`
    - portfolio candidate / new strategy / pre-live operator workflow expansion
- Synced:
  - master roadmap
  - roadmap rebase draft
  - finance doc index
- Durable takeaway:
  - current discussion point is no longer just the next slice,
    but whether this `Phase 19~25` sequence matches the user's desired long-term direction

### 2026-04-14
- Rewrote the `Phase 19~25` roadmap explanation in plainer language.
- Focus:
  - what each future phase means
  - why it should happen
  - why the proposed order is natural
- Synced:
  - `MASTER_PHASE_ROADMAP.md`
  - `ROADMAP_REBASE_PHASE18_TO_PHASE25_20260414.md`
- Durable takeaway:
  - the roadmap now reads less like a phase title list
    and more like an execution narrative the user can review before deciding direction

### 2026-04-14
- Started `Phase 19` in implementation-first mode.
- First slice:
  - strict annual `Rejected Slot Handling Contract`
  - replaces the operator-facing two-checkbox reading with one explicit handling mode
- Implemented:
  - new explicit mode constants/helpers in `finance.sample`
  - runtime compatibility bridge in `app/web/runtime/backtest.py`
  - single / compare / history / prefill sync in `app/web/pages/backtest.py`
- Validation:
  - `python3 -m py_compile finance/sample.py app/web/runtime/backtest.py app/web/pages/backtest.py`
  - `.venv/bin/python` import smoke for the same modules
- Synced:
  - phase19 kickoff docs
  - roadmap
  - finance doc index
  - finance comprehensive analysis
- Durable takeaway:
  - Phase 19 first slice favors contract clarity and legacy compatibility over broad rerun coverage

### 2026-04-14
- Completed `Phase 19` second slice for history / interpretation cleanup.
- Changed:
  - strict annual selection history now preserves rejected-slot fill / cash-retention execution details for interpretation
  - interpretation summary now shows `Rejected Slot Handling`, `Filled Events`, `Cash-Retained Events`
  - history table hides internal booleans and shows operator-facing contract language instead
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python` import smoke for `app.web.pages.backtest`
- Synced:
  - phase19 TODO/doc
  - finance comprehensive analysis
  - finance doc index
- Durable takeaway:
  - Phase 19 now covers not only form/runtime contract clarity but also history/interpretation readability for the same handling semantics

### 2026-04-14
- Completed `Phase 19` third slice for risk-off / weighting interpretation cleanup.
- Changed:
  - strict annual selection history now shows `Weighting Contract`, `Risk-Off Contract`, `Risk-Off Reasons`
  - interpretation summary now shows `Weighting Contract`, `Risk-Off Contract`, `Defensive Sleeve Activations`
  - row-level interpretation now distinguishes
    - full cash risk-off
    - defensive sleeve rotation
    - final weighting contract
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python` import smoke for `app.web.pages.backtest`
- Synced:
  - phase19 TODO/doc
  - finance comprehensive analysis
  - finance doc index
- Durable takeaway:
  - Phase 19 interpretation cleanup now covers the three main structural contract lanes:
    rejected-slot handling, weighting, and risk-off

### 2026-04-14
- Closed out `Phase 19` at practical closeout / manual_validation_pending.
- Added:
  - `PHASE19_COMPLETION_SUMMARY.md`
  - `PHASE19_NEXT_PHASE_PREPARATION.md`
  - `PHASE19_TEST_CHECKLIST.md`
- Synced:
  - `PHASE19_CURRENT_CHAPTER_TODO.md`
  - `MASTER_PHASE_ROADMAP.md`
  - `FINANCE_DOC_INDEX.md`
- Durable takeaway:
  - Phase 19 is now handed off as a documentation/contract stabilization phase with manual UI validation still pending

### 2026-04-14
- Rewrote the `Phase 19` kickoff plan in much plainer language.
- Focus:
  - what this phase is doing
  - why it is needed before deep backtest resumes
  - what difficult terms like `contract`, `slice`, `payload`, `minimal validation` mean
- Synced:
  - `PHASE19_STRUCTURAL_CONTRACT_EXPANSION_PLAN.md`
  - `FINANCE_TERM_GLOSSARY.md`
- Durable takeaway:
  - the Phase 19 plan now reads as an operator-facing explanation, not just an internal engineering memo

### 2026-04-14
- Updated future phase-plan writing guidance.
- Changed:
  - `AGENTS.md` now requires new or heavily rewritten phase plan docs to include
    - `쉽게 말하면`
    - `왜 필요한가`
    - `이 phase가 끝나면 좋은 점`
  - `Phase 19` kickoff doc now explains the current priority-item jargon inline
- Durable takeaway:
  - future phase plans should be readable as orientation documents, not just compressed planning notes

### 2026-04-14
- Finalized the `Phase 19` kickoff document into a template-style operator-friendly plan.
- Added:
  - `.note/finance/PHASE_PLAN_TEMPLATE.md`
- Synced:
  - `AGENTS.md`
  - `FINANCE_DOC_INDEX.md`
  - `PHASE19_CURRENT_CHAPTER_TODO.md`
- Durable takeaway:
  - future phase plan documents now have a reusable default shape instead of being rewritten ad hoc each time

### 2026-04-14
- Tightened `Phase 19` strict annual contract UX based on checklist feedback.
- Changed:
  - `Weighting Contract`, `Risk-Off Contract`, `Rejected Slot Handling Contract` now use clearer section titles and labels in strict annual single/compare forms
  - each contract now shows a plain-language "current selection" explanation
  - `Defensive Sleeve Tickers` now explains that it is only used for `Defensive Sleeve Preference` during full risk-off
- Synced:
  - `PHASE19_TEST_CHECKLIST.md`
  - `PHASE19_CURRENT_CHAPTER_TODO.md`
  - `FINANCE_TERM_GLOSSARY.md`
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md`
  - `FINANCE_DOC_INDEX.md`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python` import smoke for `app.web.pages.backtest`
  - finance refinement hygiene script
- Durable takeaway:
  - Phase 19 contract language is now easier to find and read from the form itself, not only from history or docs

### 2026-04-14
- Standardized future phase test checklist workflow.
- Changed:
  - `AGENTS.md` now requires user-facing phase test checklists to prefer Markdown task checkboxes like `[ ]`
  - new `.note/finance/PHASE_TEST_CHECKLIST_TEMPLATE.md` added as the default checklist template
  - active `PHASE19_TEST_CHECKLIST.md` converted to checkbox-style verification items
- Durable takeaway:
  - future phase handoffs now have a clearer "user checks items directly, then we move on" workflow

### 2026-04-14
- Refined strict annual contract help text based on live Phase 19 checklist feedback.
- Changed:
  - `Rejected Slot Handling Contract` tooltip now explains each option as separate bullet-style items instead of one long sentence
  - `Risk-Off Contract` tooltip now explains what `portfolio-wide risk-off` means in plain Korean
  - overlay contract intro now states that `Weighting Contract`, `Rejected Slot Handling Contract`, and `Risk-Off Contract` are always-on handling rules, not enable/disable toggles
- Synced:
  - `PHASE19_TEST_CHECKLIST.md`
  - `FINANCE_TERM_GLOSSARY.md`
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python` import smoke for `app.web.pages.backtest`
  - finance refinement hygiene script
- Durable takeaway:
  - contract UI now answers both "what does this option mean?" and "is this always active?" directly from the form

### 2026-04-14
- Reorganized strict annual advanced inputs into separate overlay and handling sections.
- Changed:
  - single / compare strict annual forms now split
    - `Overlay`
    - `Portfolio Handling & Defensive Rules`
  - `Trend Filter` / `Market Regime` stay in `Overlay`
  - `Rejected Slot Handling Contract` / `Weighting Contract` / `Risk-Off Contract` / `Defensive Sleeve Tickers` move into `Portfolio Handling & Defensive Rules`
- Durable takeaway:
  - overlay trigger logic and post-overlay portfolio handling are now easier to distinguish from the form structure itself

### 2026-04-14
- Simplified strict annual handling-contract captions after live UX feedback.
- Changed:
  - removed repetitive `위치:` phrasing from contract captions
  - rewrote `Rejected Slot Handling Contract`, `Risk-Off Contract`, `Weighting Contract` captions around
    - what situation each contract handles
    - easy plain-language summary
    - how it differs from neighboring contracts
  - portfolio handling intro now uses bullet-style role summary instead of compressed inline prose
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python` import smoke for `app.web.pages.backtest`
- Durable takeaway:
  - the form now explains contract purpose directly, without relying on repeated location hints

### 2026-04-14
- Clarified strict annual `Risk-Off Contract` wording after additional UX feedback.
- Changed:
  - replaced vague `보수 모드` / `full risk-off` phrasing in strict annual form help with
    - "factor 포트폴리오 전체를 멈추고 현금 또는 방어 ETF로 전환"
    - "포트폴리오 전체를 쉬어야 할 때"
  - aligned `Risk-Off Contract`, `Defensive Sleeve Tickers`, overlay intro, and interpretation summary around the same plain-language meaning
  - synced glossary/comprehensive analysis wording to the same concept
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python` import smoke for `app.web.pages.backtest`
  - finance refinement hygiene script
- Durable takeaway:
  - users can now read `Risk-Off Contract` as a portfolio-wide transition rule without having to infer what `보수 모드` means

### 2026-04-14
- Tightened History / Selection History UX after Phase 19 checklist confusion.
- Changed:
  - `Backtest > History` now explains that a `history run` means one saved backtest record
  - selected history record drilldown now uses clearer labels like `Selected History Run`, `Saved Run Summary`, `Saved Input & Context`
  - strict annual history drilldown now explicitly says detailed `Selection History` / `Interpretation Summary` are checked after `Run Again` or `Load Into Form`
  - latest result selection tabs now read
    - `Selection History Table`
    - `Interpretation Summary`
    - `Selection Frequency`
  - `Selection History Table` now states that the `Interpretation` column is the row-level explanation
  - `Interpretation Summary` now states which contract / event fields should be checked first
- Synced:
  - `FINANCE_TERM_GLOSSARY.md`
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python` import smoke for `app.web.pages.backtest`
  - finance refinement hygiene script
- Durable takeaway:
  - users can now find the correct history surface faster and distinguish saved-record review from live selection-history drilldown

### 2026-04-14
- Fixed confusing `History` action flow for strict annual records.
- Changed:
  - `Run Again` from `Backtest > History` now reruns immediately, then moves the UI to `Single Strategy` so the refreshed `Latest Backtest Run` is visible right away
  - `Load Into Form` still moves to `Single Strategy`, but now clearly says it only loads inputs and does not refresh results until the user runs the form
  - added `Back To History` shortcut after `Load Into Form` so the user is not left without an obvious way back
  - updated history warning copy to reference `Selection History Table` / `Interpretation Summary` with current labels
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python` import smoke for `app.web.pages.backtest`
  - finance refinement hygiene script
- Durable takeaway:
  - history actions now better match user expectation: rerun shows refreshed results, while load-into-form is explicitly framed as input prefill only

### 2026-04-15
- Refined Phase 19 closeout docs to better match the user's actual checklist progress and reading flow.
- Changed:
  - `PHASE19_CURRENT_CHAPTER_TODO.md` now marks manual UI validation as `in_progress` instead of `pending`
  - `PHASE19_COMPLETION_SUMMARY.md` now explains completed work in plainer language under `쉽게 말하면`
  - `PHASE_PLAN_TEMPLATE.md` now uses `작업 단위` language instead of `slice`
  - `AGENTS.md` now explicitly prefers plain-language work-unit labels in future phase plan documents
  - `PHASE19_STRUCTURAL_CONTRACT_EXPANSION_PLAN.md` was aligned to the same `작업 단위` wording
- Validation:
  - finance refinement hygiene script
- Durable takeaway:
  - phase plan and closeout docs now better match user-facing review flow and avoid internal jargon where it is not helpful

### 2026-04-15
- Phase 19 manual checklist gate is now treated as completed.
- Changed:
  - `PHASE19_CURRENT_CHAPTER_TODO.md` now marks manual UI validation actual run as `completed`
  - `PHASE19_COMPLETION_SUMMARY.md` now reflects `manual_validation_completed`
- Durable takeaway:
  - Phase 19 can now be treated as fully closed from a user-verification standpoint, and the next phase discussion can proceed without leaving the validation gate ambiguous

### 2026-04-15
- Opened Phase 20 as the next active workstream after Phase 19 closeout.
- Changed:
  - created `PHASE20_CANDIDATE_CONSOLIDATION_AND_OPERATOR_WORKFLOW_HARDENING_PLAN.md`
  - created `PHASE20_CURRENT_CHAPTER_TODO.md`
  - created `PHASE20_OPERATOR_WORKFLOW_INVENTORY_FIRST_PASS.md`
  - updated `MASTER_PHASE_ROADMAP.md` phase20 status to `in_progress`
  - synced `FINANCE_DOC_INDEX.md`
- Durable takeaway:
  - the project is now treating candidate reuse, compare-to-portfolio flow, and saved-portfolio re-entry as the main active operator workflow problem

### 2026-04-15
- Completed a practical Phase 21 automation/persistence baseline in one work unit.
- Changed:
  - added `bootstrap_finance_phase_bundle.py` to open a new phase document bundle from the repo templates
  - added `manage_current_candidate_registry.py` and seeded `.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl`
  - updated `check_finance_refinement_hygiene.py` so candidate-facing doc work can also review the machine-readable candidate registry
  - created `PHASE21` kickoff, work-unit, closeout, next-phase, and checklist documents
  - synced `AGENTS.md`, plugin/skill docs, roadmap, doc index, registry guide, runtime artifact guidance, and finance comprehensive analysis
- Validation:
  - `python3 -m py_compile plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
  - `python3 plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate`
  - `python3 plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py --phase 99 --title "Automation Smoke Example" --dry-run`
  - finance refinement hygiene script
- Durable takeaway:
  - the repo now has a reusable automation baseline for phase kickoff and current-candidate persistence, which lowers repeated setup cost before later deep validation phases

### 2026-04-15
- Phase 20 QA feedback led to another compare-surface UX cleanup.
- Changed:
  - moved current candidate re-entry out of the space between the compare title and the main `Strategies` control
  - kept strategy selection as the first visible compare action
  - reorganized the current candidate helper into a secondary expander with a smaller `What This Does` explanation block
  - synced `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import importlib; import app.web.pages.backtest"`
  - finance refinement hygiene script
- Durable takeaway:
  - compare now reads as a primary strategy-selection surface first, while current candidate re-entry behaves like a supporting shortcut instead of competing for top-of-screen attention

### 2026-04-15
- Phase 20 QA also surfaced excessive divider usage inside `Compare & Portfolio Builder`.
- Changed:
  - removed top-level dividers between compare results, weighted portfolio builder, and saved portfolios
  - clarified in the saved-portfolio caption that this area is the next step after compare and weighted builder, not a separate top-level workflow
  - synced `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - finance refinement hygiene script
- Durable takeaway:
  - the compare page now relies on section headings instead of repeated horizontal lines, and saved portfolios remains in the same tab because it still behaves like the final step of the same operator workflow

### 2026-04-15
- Phase 20 QA found that current candidate re-entry button labels still read too much like internal jargon.
- Changed:
  - renamed `Load Current Anchors` to `Load Recommended Candidates`
  - renamed `Load Lower-MDD Near Misses` to `Load Lower-MDD Alternatives`
  - renamed the custom picker expander to `Pick Specific Candidates Manually`
  - added one-line explanations under each quick action so users can tell why there are two buttons and when to use each
  - synced `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - finance refinement hygiene script
- Durable takeaway:
  - current candidate re-entry now explains “대표 후보 불러오기 / 더 낮은 MDD 대안 불러오기 / 직접 선택” in plain language instead of forcing users to decode internal portfolio-search terms

### 2026-04-15
- Phase 20 QA still found the current candidate re-entry block hard to scan as one mixed section.
- Changed:
  - split the surface into `Quick Bundles` and `Pick Manually` tabs
  - kept the two quick-load buttons together in the first tab
  - moved the candidate table and manual picker into the second tab
  - added an explicit note that this list does not auto-populate from new backtest runs or Markdown docs; it reads active rows from `CURRENT_CANDIDATE_REGISTRY.jsonl`
  - synced `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - finance refinement hygiene script
- Durable takeaway:
  - current candidate re-entry now reads as two clearer modes: quick bundle load vs manual pick, and the registry source rule is visible in the UI instead of only in supporting docs

### 2026-04-15
- Phase 20 QA then pointed out that the post-load `What Changed In Compare` card still felt too abstract.
- Changed:
  - changed the card title/phrasing so it reads as a form-update guide instead of an internal status block
  - replaced `Source`, `Label`, `Period` wording with more direct phrases about how the bundle was loaded and what period was auto-filled
  - added a short “where to check” section and a clearer next-step instruction
  - synced `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - finance refinement hygiene script
- Durable takeaway:
  - the compare prefill confirmation card now explains the loaded bundle in task-oriented language instead of assuming the user already understands source/label terminology

### 2026-04-15
- Phase 20 QA also asked whether the compare prefill summary was drifting from the actual candidate settings.
- Changed:
  - checked the current-candidate registry -> compare prefill override mapping for top N, benchmark, trend filter, market regime, weighting, risk-off, and universe contract
  - confirmed the current code maps those core fields consistently for the active candidate rows
  - expanded the `Compare Form Updated` table to show `Weighting Contract` and `Risk-Off Contract` alongside `Trend Filter` and `Market Regime`
  - synced `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `.venv/bin/python` registry-to-prefill smoke check for current candidate rows
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - finance refinement hygiene script
- Durable takeaway:
  - the current candidate compare prefill path does not appear to be silently loosening key strict-annual settings, and the confirmation table now exposes more of the actual loaded contract

### 2026-04-15
- Phase 20 QA then pointed out that compare `Strategy-Specific Advanced Inputs` still split family selection from the actual selected snapshot settings.
- Changed:
  - turned `Quality Family`, `Value Family`, `Quality + Value Family` into `Quality`, `Value`, `Quality + Value`
  - kept the variant selector at the top of each family section
  - rendered the selected variant's actual settings directly inside the same family expander instead of in a separate snapshot expander lower in the form
  - synced `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - finance refinement hygiene script
- Durable takeaway:
  - compare advanced inputs now read more like GTAA and other strategies: choose the family variant once, then adjust that variant immediately in the same section

### 2026-04-15
- Phase 20 QA also asked for a clearer explanation of `Candidate Universe Equal-Weight` inside strict annual `Benchmark Contract`.
- Changed:
  - rewrote the `Benchmark Contract` tooltip in plain language so the two options read as
    "compare to one benchmark ETF" vs "compare to a simple equal-weight portfolio built from the same candidate universe"
  - expanded the selected-state caption for `Candidate Universe Equal-Weight` so the user can understand the meaning without opening glossary docs
  - added a dedicated glossary entry for `Candidate Universe Equal-Weight`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - finance refinement hygiene script
- Durable takeaway:
  - strict annual benchmark choice is now easier to read as an operator decision: external ETF reference vs simple equal-weight baseline from the same candidate pool

### 2026-04-15
- Phase 20 QA then found that `Candidate Universe Equal-Weight / SPY` still looked like a single mixed benchmark label in compare summaries.
- Changed:
  - split compare prefill summary output into `Benchmark Contract` and `Benchmark Ticker / Reference`
  - changed current candidate registry contract summary so equal-weight cases read as
    `Benchmark Candidate Equal-Weight | Reference Ticker SPY`
    instead of an ambiguous slash-joined label
  - added an explanatory caption in the compare update card when equal-weight benchmark contract is active
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - finance refinement hygiene script
- Durable takeaway:
  - the UI now shows that equal-weight benchmark and SPY are not the same object: one is the benchmark contract, the other can remain a separate reference ticker

### 2026-04-15
- Phase 20 QA asked to make the strict-annual input field itself reflect that distinction too.
- Changed:
  - initially tried contract-dependent field naming, but this was not reliable inside the current submit-based Streamlit form
  - switched to a more robust fixed label: `Benchmark / Guardrail / Reference Ticker`
  - added a plain-language caption explaining how to read the field under each benchmark contract
  - kept prefill summary lines using `Reference Ticker` wording for equal-weight cases
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - finance refinement hygiene script
- Durable takeaway:
  - in the current form architecture, a stable neutral field label plus contract-dependent explanation is less confusing than trying to live-swap the field name

### 2026-04-15
- Phase 20 QA then confirmed that the neutral single-field approach still felt indirect in practice.
- Changed:
  - separated strict-annual `Real-Money Contract` into two explicit inputs:
    - `Benchmark Ticker`
    - `Guardrail / Reference Ticker`
  - kept `Comparison Baseline` and `Guardrail / Reference` as separate concepts in the form so the user can read
    "what do we compare against?" and "what does the guardrail watch?" independently
  - propagated the same split through single strategy, compare prefill, history/meta, runtime bundle input params, and shadow sample entrypoints
  - updated compare summary copy so equal-weight benchmark rows explain the split using the new two-column wording
- Validation:
  - `python3 -m py_compile finance/sample.py app/web/runtime/backtest.py app/web/pages/backtest.py`
  - `.venv/bin/python -c "import finance.sample; import app.web.runtime.backtest; import app.web.pages.backtest"`
- Reviewed:
  - `FINANCE_DOC_INDEX.md`는 새 durable 문서가 추가된 턴이 아니라서 이번 작업 단위에서는 별도 갱신이 필요하지 않다고 판단
- Durable takeaway:
  - the final UX model is no longer "one ticker field with two meanings"; benchmark baseline and guardrail reference are now first-class separate inputs

### 2026-04-15
- Phase 20 QA then asked for one more UX pass: when `Ticker Benchmark` is chosen, `Guardrail / Reference Ticker` should feel optional, and when `Candidate Universe Equal-Weight` is chosen, `Benchmark Ticker` should stop looking required.
- Changed:
  - `Ticker Benchmark` mode now shows:
    - `Benchmark Ticker`
    - `Guardrail / Reference Ticker (Optional)`
    with copy that says leaving the guardrail field blank means "same as benchmark"
  - `Candidate Universe Equal-Weight` mode now hides the benchmark ticker input and explains that the benchmark curve is auto-built from the candidate universe
  - compare/prefill/history summaries now display `Same as Benchmark Ticker` when no separate guardrail ticker was explicitly set
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
- Durable takeaway:
  - the operator now reads benchmark baseline and guardrail reference as separate decisions, with the optional/same-as-benchmark case made explicit in the UI

### 2026-04-15
- Phase 20 QA then reported that trying to make fields hide/show based on `Benchmark Contract` still felt awkward in practice.
- Changed:
  - confirmed the root cause was the current `st.form` structure: changing a widget inside the form does not immediately rerun the section
  - removed the experimental layout-refresh button approach
  - returned to a simpler UX where `Benchmark Contract`, `Benchmark Ticker`, and `Guardrail / Reference Ticker (Optional)` are always visible together
  - rewrote the captions so the user can understand:
    - `Ticker Benchmark`: benchmark ticker is the direct comparison baseline
    - `Candidate Universe Equal-Weight`: benchmark ticker is not used for the equal-weight baseline itself
    - `Guardrail / Reference Ticker (Optional)`: tied to underperformance / drawdown guardrails regardless of benchmark contract
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
- Durable takeaway:
  - within the current form architecture, "always visible + clearer explanation" is less frustrating than contract-dependent hide/show

### 2026-04-15
- Phase 20 QA then pushed one step further: `Guardrail / Reference Ticker` should not live in `Real-Money Contract` at all because it conceptually belongs to guardrails, not benchmark comparison.
- Changed:
  - moved `Guardrail / Reference Ticker (Optional)` out of `Real-Money Contract` and into the `Guardrails` expander
  - kept `Benchmark Contract` and `Benchmark Ticker` inside `Real-Money Contract`
  - updated the copy so the screen now reads as:
    - `Real-Money Contract` = comparison baseline
    - `Guardrails` = underperformance / drawdown stop rules plus their reference ticker
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
- Durable takeaway:
  - the benchmark baseline and the guardrail reference now live in the same places as their actual behavioral meaning, which is much easier to understand in the UI

### 2026-04-15
- Phase 20 QA then pointed out that `Compare Form Updated` should hide values that are not actually used by the loaded contract.
- Changed:
  - when `Benchmark Contract = Candidate Universe Equal-Weight`, the compare summary now leaves `Benchmark Ticker` blank
  - when both underperformance and drawdown guardrails are off, the compare summary now leaves `Guardrail / Reference Ticker` blank
  - kept `Same as Benchmark Ticker` only for cases where a guardrail is on but no separate reference ticker was explicitly entered
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
- Durable takeaway:
  - the compare summary is now closer to a true "active settings" view: unused values stay empty instead of looking meaningful

### 2026-04-15
- Phase 20 QA then hit a follow-up compare strict-annual runtime error after the `Guardrail / Reference Ticker` field was moved into `Guardrails`.
- Changed:
  - removed one stale `guardrail_reference_ticker` assignment that still lived in the compare `Quality Snapshot (Strict Annual)` path
  - kept the compare strict-annual guardrail reference flow fully inside the `Guardrails` expander, matching the single-strategy path
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - `python3 plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
- Durable takeaway:
  - the compare strict-annual UI now uses the same guardrail-reference ownership model as the single-strategy UI, so the late `NameError` regression is removed.

### 2026-04-16
- Phase 20 QA then pointed out that the information block above `Weighted Portfolio Builder` still read like an internal context card instead of an operator-friendly "what am I combining?" view.
- Changed:
  - rewrote the builder intro copy in plain language so the section reads as "compare에서 본 전략을 어떤 비중으로 섞는 단계"
  - replaced the old `Current Compare Bundle` style card with a clearer `What You Are Combining` summary
  - the summary now shows:
    - where this compare result came from
    - which period is being combined
    - how many strategies are in scope
    - a compact strategy table with `Strategy / Period / CAGR / MDD / Promotion`
  - kept saved-portfolio re-entry weights visible only when they actually exist, as context rather than as the main headline
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - `python3 plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
- Durable takeaway:
  - weighted-builder context now starts from "what we are combining" instead of "what internal compare bundle object exists," which is easier to read during QA and normal operator use.

### 2026-04-16
- Phase 20 QA then requested that divider placement in `Compare & Portfolio Builder` match the visual grouping more naturally.
- Changed:
  - removed the divider directly under `Quick Re-entry From Current Candidates`
  - added a divider between `Strategy Comparison` and `Weighted Portfolio Builder`
  - added a divider between `Weighted Portfolio Builder` and `Saved Portfolios`
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py`
  - `.venv/bin/python -c "import app.web.pages.backtest"`
  - `python3 plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
- Durable takeaway:
  - dividers now separate the three main operator stages instead of splitting the compare entry tools from the compare form.

### 2026-04-16
- Phase 20 QA then showed that the checklist itself had started lagging behind the renamed UI labels.
- Changed:
  - updated `PHASE20_TEST_CHECKLIST.md` to use current on-screen names first
  - added an old-name -> current-UI-name mapping block
  - made each section more explicit about where the tester should look on screen
  - aligned the weighted/saved divider checks with the current layout
- Durable takeaway:
  - once UI wording starts changing during QA, the checklist should follow the current labels quickly or it stops being a good test guide.
