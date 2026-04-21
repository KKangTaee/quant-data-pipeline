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
  - [PHASE25_CURRENT_CHAPTER_TODO.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase25/PHASE25_CURRENT_CHAPTER_TODO.md)
- current candidate summary:
  - [CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md)
- historical full archive:
  - [WORK_PROGRESS_ARCHIVE_20260413.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/archive/WORK_PROGRESS_ARCHIVE_20260413.md)

## Entries

### 2026-04-20
- Reorganized section 3 of `FINANCE_COMPREHENSIVE_ANALYSIS.md` so current architecture and phase history are separated.
- Changed:
  - renamed section 3 to `현재 시스템 구조와 phase별 구현 히스토리`
  - added `3-1. 현재 시스템 구조` as the current architecture reading path
  - added `3-2. Phase별 구현 히스토리` as a grouped phase timeline from Phase 1~25
  - moved the previous mixed chronological narrative under `3-3. 상세 구현 메모`
  - changed the old `Phase 14 Practical Closeout` UI status sentence to read as a historical note rather than current state
- Durable takeaway:
  - The comprehensive analysis now keeps deep implementation notes but no longer asks users to read mixed phase history as the current architecture explanation.

### 2026-04-20
- Added a user-facing entry layer to `FINANCE_COMPREHENSIVE_ANALYSIS.md` without removing the deep technical context.
- Changed:
  - clarified the document's three roles: readable system map, agent deep reference, and durable implementation context
  - added a quick reading guide by purpose
  - added a one-page current system summary across data collection, persistence, loader/runtime, strategy engine, web UI, and review/pre-live layers
  - added reading rules so older implementation notes are preserved as history while current state is checked against roadmap/work logs
- Durable takeaway:
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md` remains the deep system reference, but it now has a clearer human-readable entry point.

### 2026-04-20
- Refined the `FINANCE_DOC_INDEX.md` earlier-phase section after user feedback.
- Changed:
  - replaced the single long `Earlier Phase Detail` table with one subsection per phase for Phase 1~18
  - added managed documents where relevant, including plan, TODO, work unit, checklist, completion, next-phase prep, decisions, gates, and validation notes
  - kept the scope controlled by listing representative managed documents instead of every historical file
- Durable takeaway:
  - Both recent and earlier phases are now navigable by phase, while the index still avoids becoming a full archive dump.

### 2026-04-20
- Reorganized `FINANCE_DOC_INDEX.md` as a navigation-first finance document map.
- Changed:
  - reduced the index from a long explanatory list into a shorter phase-oriented guide
  - added a "지금 먼저 볼 문서" section for Phase 25 active work
  - split top-level docs, operating files, backtest reports, recent phases, earlier phases, support track, data/runtime references, research references, and archives
  - moved detailed backtest result lookup guidance toward `backtest_reports/BACKTEST_REPORT_INDEX.md`
- Durable takeaway:
  - `FINANCE_DOC_INDEX.md` should now act as a document map, not another long explanation document.

### 2026-04-20
- Closed `Phase 24` and opened `Phase 25`.
- Changed:
  - accepted the completed `PHASE24_TEST_CHECKLIST.md` manual QA state
  - marked `PHASE24_CURRENT_CHAPTER_TODO.md`, `PHASE24_COMPLETION_SUMMARY.md`, and `PHASE24_NEXT_PHASE_PREPARATION.md` as Phase 24 closeout / Phase 25 handoff documents
  - bootstrapped the Phase 25 document bundle
  - rewrote the Phase 25 plan, TODO, checklist, completion draft, next-phase draft, and first work-unit note around `Pre-Live Operating System And Deployment Readiness`
  - fixed the Phase 25 boundary as `Real-Money 검증 신호 = per-run diagnostic signal` and `Pre-Live 운영 점검 = paper / watchlist / hold / re-review operating process`
  - synced `MASTER_PHASE_ROADMAP.md`, `FINANCE_DOC_INDEX.md`, and durable analysis logs
- Durable takeaway:
  - Phase 24 is closed as a completed new-strategy implementation bridge, and Phase 25 is now active as a pre-live operating-system development phase, not a live trading or investment approval phase.

### 2026-04-20
- Clarified the Phase 25 boundary between existing Real-Money validation and future pre-live operation workflow.
- Decision:
  - `Real-Money 검증 신호` = per-backtest diagnostic surface for transaction cost, benchmark, drawdown, liquidity, ETF operability, promotion status
  - `Pre-Live 운영 점검` = Phase 25 workflow for paper tracking, watchlist, hold/review decisions, monitoring notes, and re-collection/re-validation actions
- Updated:
  - `Reference > Guides > 테스트에서 상용화 후보 검토까지 사용하는 흐름`
  - `FINANCE_TERM_GLOSSARY.md`
  - `PHASE24_NEXT_PHASE_PREPARATION.md`
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md`
  - `QUESTION_AND_ANALYSIS_LOG.md`

### 2026-04-20
- Corrected the `Global Relative Strength` malformed price-row handling policy after user QA feedback.
- Decision:
  - do not silently remove or repair a malformed price row to extend the backtest result window
  - keep the conservative common rebalance-date behavior so `IWM`'s `2026-03-17` missing close naturally limits the run to the last clean common rebalance date
  - surface the issue through `malformed_price_rows` metadata and a Korean warning so the operator can inspect or re-collect the source price row
- Validation expectation:
  - the same `2016-01-01 -> 2026-04-20` default run should end at `2026-02-27` until the malformed `IWM` source row is fixed or re-collected
- Documentation hygiene:
  - reviewed index impact; no new durable document was added, so `FINANCE_DOC_INDEX.md` did not need a structural update

### 2026-04-20
- Fixed a follow-up Phase 24 QA issue where `Global Relative Strength` stopped at `2026-02-27` even when the selected end date was `2026-04-20`.
- Root cause:
  - `IWM` had one DB row on `2026-03-17` with empty OHLC values
  - `add_ma` treated that empty `Close` inside the rolling window as invalid and dropped all later MA rows until the rolling window recovered
  - month-end alignment therefore lost March/April common dates and the result stopped at February
- Implemented:
  - `add_ma` now removes rows with missing price values before calculating moving averages
  - Global Relative Strength now records those removed malformed rows in `malformed_price_rows` metadata and result warnings
  - real-money warning strings shown under "이번 실행에서 같이 봐야 할 주의사항" were translated to Korean-oriented copy
- Validation:
  - `.venv` default `Global Relative Strength` runtime smoke for `2016-01-01 -> 2026-04-20` now ends at `2026-04-17`, the latest available DB trading date
  - the same smoke surfaces `IWM 1건(2026-03-17)` as a malformed price-row warning
  - `.venv/bin/python -m py_compile finance/transform.py app/web/runtime/backtest.py finance/sample.py`
- Documentation hygiene:
  - reviewed index impact; no new durable document was added, so `FINANCE_DOC_INDEX.md` did not need a structural update

### 2026-04-20
- Fixed a Phase 24 QA issue in `Global Relative Strength` single-strategy execution.
- Root cause:
  - default preset included `EEM`, but the current DB only had recent `EEM` price rows
  - after `MA200` and 12-month relative-strength warmup, `EEM` became an empty transformed series
  - strict date intersection then failed with `공통 Date가 없습니다.`
- Implemented:
  - DB-backed Global Relative Strength now excludes risky tickers that have insufficient transformed price history
  - excluded tickers are preserved in result metadata as `excluded_tickers`
  - UI/runtime warnings explain that the ticker was excluded and that DB price data should be refreshed before interpreting the result
- Validation:
  - `.venv` default preset runtime smoke now succeeds with `EEM` excluded
  - compact custom universe runtime smoke still succeeds with no excluded tickers
  - `.venv/bin/python -m py_compile finance/sample.py app/web/runtime/backtest.py`

### 2026-04-20
- Continued Phase 24 with the UI / replay integration pass for `Global Relative Strength`.
- Implemented:
  - strategy catalog registration for single and compare strategy selectors
  - `Backtest > Single Strategy` form with universe, cash ticker, top, interval, score horizons, trend filter, and ETF real-money contract inputs
  - `Compare & Portfolio Builder` strategy-specific box and compare runner override support
  - history payload / load-into-form / run-again roundtrip for `cash_ticker`, cadence, score, and trend settings
  - saved portfolio replay override preservation for the new strategy
- Validation:
  - `python3 -m py_compile app/web/backtest_strategy_catalog.py app/web/runtime/backtest.py app/web/runtime/history.py app/web/pages/backtest.py`
  - `.venv` catalog/history smoke
  - `.venv` DB-backed runtime smoke
  - `.venv` compare runner smoke
- Status:
  - Phase 24 is now `practical_closeout / manual_validation_pending`.
  - Next step is user QA via `PHASE24_TEST_CHECKLIST.md`.
- Guidance sync:
  - refreshed `finance-strategy-implementation` skill guidance so future user-facing strategy additions include catalog / single UI / compare / history / saved replay handoff checks.

### 2026-04-19
- Continued Phase 23 implementation with the first quarterly contract parity pass.
- Implemented:
  - quarterly single-strategy UI now shows `Portfolio Handling & Defensive Rules`
  - quarterly payloads now carry weighting, rejected-slot handling, risk-off, and defensive ticker contract values
  - quarterly compare forms now expose the same portfolio handling contract controls
  - quarterly history load-into-form restores the same contract values
  - quarterly runtime wrappers accept and pass these contracts to the DB-backed strict statement shadow execution path
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py app/web/runtime/backtest.py finance/sample.py`
  - `.venv` import/signature smoke for the three quarterly strict prototype runners

### 2026-04-19
- Opened `Phase 23 Quarterly And Alternate Cadence Productionization`.
- Created and rewrote the Phase 23 plan / TODO / checklist / completion / next-phase documents so the phase is clearly framed as product development, not investment analysis.
- Added the first work-unit document:
  - `.note/finance/phase23/PHASE23_QUARTERLY_PRODUCTIONIZATION_FRAME_FIRST_WORK_UNIT.md`
- Current reading:
  - quarterly strict family already has execution paths
  - Phase 23 will harden UI, payload, compare/history/replay, and representative validation before Phase 24 new strategy expansion

### 2026-04-18
- Started a user-requested GTAA investable portfolio search outside the current presets.
- Used sub-agents for:
  - GTAA runtime / promotion metadata path discovery
  - conservative ETF universe exploration
  - offensive ETF universe exploration
- Re-ran the strongest ideas in the main environment with `.venv/bin/python` and current DB-backed `run_gtaa_backtest_from_db`.
- Result:
  - compact ETF sleeves produced `real_money_candidate` GTAA candidates without relaxing ETF AUM/spread gates
  - broader high-CAGR universes were rejected because current ETF operability/profile coverage pushed them back to `hold`
  - saved the durable report at `.note/finance/backtest_reports/strategies/GTAA_REAL_MONEY_CANDIDATE_SEARCH_20260418.md`
  - appended the result to the GTAA strategy log and candidate registry

### 2026-04-16
- Split the roadmap tail into two clearer roles:
  - `현재 위치` now behaves like a status board
  - `지금부터의 큰 흐름` now behaves like a next-step guide
- Removed:
  - duplicated reading-order guidance that overlapped between the two sections
- Result:
  - the roadmap reads more like a single coherent document and less like two overlapping summaries

### 2026-04-16
- Reworked the roadmap summary section that used to read as a special `Phase 18~25 Draft Big Picture`.
- Changed it into:
  - `다음 단계 한눈에 보기 (Phase 18 ~ 25)`
  - a quick-reading summary that clearly says it does not replace the actual phase descriptions above
- Result:
  - the roadmap now feels less like it has a second special roadmap embedded inside it
  - `Phase 18 ~ 25` is easier to read as a continuation of the same master roadmap

### 2026-04-16
- Clarified roadmap semantics after user review:
  - `Phase 18` is still in-progress from a backlog perspective
  - `Phase 19` and `Phase 20` are fully manual-validation completed
  - `Phase 5 first chapter` was a historical chapter label, not a hidden active second chapter
  - `support track` remains a parallel tooling lane, not a main finance phase
- Updated the roadmap so these distinctions read more directly.

### 2026-04-16
- Refreshed `MASTER_PHASE_ROADMAP.md` after the user pointed out that the reading order had become awkward.
- Reordered:
  - `Phase 6` and `Phase 16` back into their natural chronological positions
  - `현재 위치` / `Phase 18~25 Draft Big Picture` / `앞으로의 운영 방식` into a cleaner tail structure
- Synced:
  - `Phase 19` status now reads as `phase complete / manual_validation_completed`
  - active pointer now follows `Phase 21` as the next main phase board
- Result:
  - the roadmap now reads as a real phase sequence again instead of a mix of historical notes and later inserts

### 2026-04-16
- Rebased the roadmap after the user pointed out that the old `Phase 21` was not really product work.
- Applied:
  - previous `Research Automation And Experiment Persistence` work is now treated as a support track, not a main finance phase
  - the main roadmap was redesigned so the new `Phase 21` is `Integrated Deep Backtest Validation`
  - new `Phase 21` plan / TODO / checklist / next-phase docs now reflect deep validation instead of agent/plugin setup
- Result:
  - the project phase sequence is back on the product path:
    validation -> portfolio-level construction -> quarterly productionization -> new strategy expansion -> pre-live readiness

### 2026-04-16
- Reviewed Phase 21 QA documents after Phase 20 workflow naming/validation changes.
- Outcome:
  - `PHASE21_TEST_CHECKLIST.md` itself did not need major target changes because it validates scripts, registry, and docs rather than Phase 20 UI buttons
  - added one explicit note so future QA readers know the Phase 20 button rename is not the core Phase 21 test target
  - updated `PHASE21_NEXT_PHASE_PREPARATION.md` so it no longer assumes Phase 20 operator workflow is still the main open question

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
  - `operations/RUNTIME_ARTIFACT_HYGIENE.md`
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
  - `support_tracks/ROADMAP_REBASE_PHASE18_TO_PHASE25_20260414.md`
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

### 2026-04-16
- Closed `Phase 18` as `practical_closeout / manual_validation_pending` instead of keeping the remaining structural backlog open as an active blocker.
- Changed:
  - created `PHASE18_COMPLETION_SUMMARY.md`
  - created `PHASE18_NEXT_PHASE_PREPARATION.md`
  - created `PHASE18_TEST_CHECKLIST.md`
  - updated `PHASE18_CURRENT_CHAPTER_TODO.md` so the remaining second-slice idea is now treated as deferred backlog rather than current active work
  - updated `PHASE18_LARGER_STRUCTURAL_REDESIGN_PLAN.md` so the current phase reading points toward closeout and handoff
- Durable takeaway:
  - `Phase 18` already produced meaningful redesign evidence, but not anchor replacement evidence, so the right next step is closeout plus handoff rather than one more structural slice.

### 2026-04-16
- Started the new main `Phase 21` reading as `in_progress` and aligned the top-level roadmap/doc index to that state.
- Changed:
  - updated `PHASE21_INTEGRATED_DEEP_BACKTEST_VALIDATION_PLAN.md` to explicitly treat `Phase 18` remaining structural ideas as future options
  - updated `PHASE21_CURRENT_CHAPTER_TODO.md` to reflect kickoff progress and the `Phase 18` closeout decision
  - synced `MASTER_PHASE_ROADMAP.md` and `FINANCE_DOC_INDEX.md` so they now read as:
    - `Phase 18` = practical closeout / manual validation pending
    - `Phase 21` = in progress
- Durable takeaway:
  - the main track is now clearer: we are not opening more structural redesign first, we are validating the current annual-strict candidates and portfolio bridge in one shared frame.

### 2026-04-16
- Continued `Phase 21` with the first real work unit: validation frame definition.
- Changed:
  - created `PHASE21_VALIDATION_FRAME_DEFINITION_FIRST_WORK_UNIT.md`
  - fixed the common rerun frame to:
    - `2016-01-01 ~ 2026-04-01`
    - `US Statement Coverage 100`
    - `Historical Dynamic PIT Universe`
  - fixed the family rerun packs to the current registry-backed candidates:
    - `Value` current anchor / lower-MDD near-miss
    - `Quality` current anchor / cleaner alternative
    - `Quality + Value` current anchor / lower-MDD weaker-gate alternative
  - fixed the representative bridge frame to:
    - `Load Recommended Candidates`
    - near-equal weighted bundle
    - representative saved portfolio replay
  - fixed phase21 report and strategy-log naming rules before actual reruns
- Durable takeaway:
  - `Phase 21` is now in a true execution-ready state: the next step is no longer "define the frame" but "run the pack."

### 2026-04-16
- Ran the first actual `Phase 21` rerun pack for `Value`.
- Changed:
  - reran:
    - current anchor `Top N = 14 + psr`
    - lower-MDD alternative `Top N = 14 + psr + pfcr`
  - confirmed in the shared `Phase 21` frame that:
    - current anchor stays `real_money_candidate / paper_probation / review_required`
    - lower-MDD alternative still remains `production_candidate / watchlist / review_required`
  - created `backtest_reports/phase21/PHASE21_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md`
  - created `backtest_reports/phase21/README.md`
  - synced `VALUE_STRICT_ANNUAL.md`, `VALUE_STRICT_ANNUAL_BACKTEST_LOG.md`, `CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md`, phase21 TODO, and the report indexes
- Durable takeaway:
  - `Value` does not need a candidate replacement right now; the current anchor remains the practical reference point even in the integrated validation frame.

### 2026-04-16
- Ran the second actual `Phase 21` rerun pack for `Quality`.
- Changed:
  - reran:
    - current anchor `capital_discipline + LQD + trend on + regime off + Top N 12`
    - cleaner alternative `capital_discipline + SPY + trend on + regime off + Top N 12`
  - confirmed in the shared `Phase 21` frame that:
    - current anchor still remains the practical reference point
    - cleaner alternative still remains a comparison-only surface rather than a replacement
  - created `backtest_reports/phase21/PHASE21_QUALITY_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md`
  - synced `QUALITY_STRICT_ANNUAL.md`, `QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md`, `CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md`, phase21 TODO, and the report indexes
- Durable takeaway:
  - `Quality` also does not need a candidate replacement right now; the `LQD` anchor remains the practical point, and the `SPY` version remains useful mainly as a cleaner comparison surface.

### 2026-04-17
- Ran the third actual `Phase 21` rerun pack for `Quality + Value`.
- Changed:
  - reran:
    - current strongest point `operating_margin + pcr + por + per + Top N 10`
    - lower-MDD alternative with the same factor set and `Top N 9`
  - confirmed in the shared `Phase 21` frame that:
    - current strongest point remains `real_money_candidate / small_capital_trial / review_required`
    - `Top N 9` has stronger raw metrics but still drops to `production_candidate / watchlist / review_required`
  - created `backtest_reports/phase21/PHASE21_QUALITY_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md`
  - synced `QUALITY_VALUE_STRICT_ANNUAL.md`, `QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md`, `CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md`, phase21 TODO, and the report indexes
- Durable takeaway:
  - `Quality + Value` remains the strongest blended representative anchor, but the very attractive `Top N 9` alternative still needs weaker-gate handling before it can replace the anchor.

### 2026-04-17
- Ran the `Phase 21` representative portfolio bridge validation.
- Changed:
  - rebuilt the `Load Recommended Candidates` source bundle from:
    - `Value` current anchor
    - `Quality` current anchor
    - `Quality + Value` current anchor
  - built the representative weighted portfolio with:
    - `33 / 33 / 34`
    - `Date Alignment = intersection`
  - validated saved portfolio replay by reconstructing the saved compare context and portfolio context
  - created `backtest_reports/phase21/PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md`
  - updated Phase 21 completion / next-phase docs and candidate summary
- Durable takeaway:
  - the portfolio bridge is reproducible and meaningful enough for Phase 22 portfolio-level candidate construction, but portfolio-level promotion semantics still need to be designed before treating it as a production candidate.

### 2026-04-17
- Refined `Phase 21` QA wording after checklist review.
- Changed:
  - added `Validation Frame` to the shared finance glossary
  - rewrote the Phase 21 plan wording around deferred Phase 18 structural backlog, current anchors, and lower-MDD rescue candidates in plainer language
  - updated the Phase 21 checklist so validation frame verification points directly to the glossary
- Durable takeaway:
  - Phase 21 manual QA should now read as a user-facing validation guide rather than an internal shorthand memo.

### 2026-04-17
- Clarified where to verify `Phase 21` family-level integrated rerun results during manual QA.
- Changed:
  - expanded `PHASE21_TEST_CHECKLIST.md` section 2 with direct links to the phase21 archive, the three family rerun reports, and the strategy hub / backtest log documents
  - recorded the clarification in the Phase 21 TODO board
- Durable takeaway:
  - family-level rerun QA should start from `.note/finance/backtest_reports/phase21/README.md`, then inspect the `Value`, `Quality`, and `Quality + Value` rerun reports.

### 2026-04-17
- Refined `Phase 21` manual QA decision guidance and annual strict backtest log readability.
- Changed:
  - added 유지 / 교체 / 보류 판단 기준 to `PHASE21_TEST_CHECKLIST.md`
  - standardized the three annual strict backtest logs to read newest-first and end with a compact recent decision summary table
  - moved misplaced `2026-04-14` concentration-aware weighting entries in `Value` and `Quality + Value` logs back into date order
  - updated the shared backtest log template and indexes so future logs follow the same pattern
- Durable takeaway:
  - manual QA should use report interpretation plus gate status, not raw CAGR/MDD alone, when checking whether a candidate is maintained, replaced, or deferred.

### 2026-04-17
- Clarified `Phase 21` portfolio bridge validation locations during manual QA.
- Changed:
  - updated `PHASE21_TEST_CHECKLIST.md` section 3 to point to `PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md` as the official rerun report
  - separated the document report from the UI verification path:
    - `Weighted Portfolio Builder`
    - `Weighted Portfolio Result`
    - `Saved Portfolios`
    - `Replay Saved Portfolio`
  - recorded the clarification in the Phase 21 TODO board
- Durable takeaway:
  - `weighted portfolio / saved portfolio rerun report` should be read as the Phase 21 Markdown report, while the Streamlit UI is the optional replay/visual verification path.

### 2026-04-17
- Rewrote the `Phase 21` portfolio bridge validation report for readability.
- Changed:
  - restructured `PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md` around:
    - what the document is
    - the conclusion first
    - plain-language terms
    - why the three annual strict strategies were used
    - validation flow
    - weighted / saved replay results
    - what the result does and does not prove
    - Phase 22 questions
  - clarified that `FIRST_PASS` means first validation, not final portfolio recommendation
  - synced the Phase 21 archive README, report index, finance doc index, and TODO board
- Durable takeaway:
  - the portfolio bridge report should now read as a workflow validation report rather than an AI-looking result dump.

### 2026-04-17
- Aligned the `Phase 21` manual checklist with the rewritten portfolio bridge report.
- Changed:
  - updated `PHASE21_TEST_CHECKLIST.md` section 3 so QA follows the new report flow:
    - conclusion first
    - why the three strategies were grouped
    - validation flow
    - what the result does and does not prove
    - Phase 22 questions
  - recorded the checklist alignment in the Phase 21 TODO board
- Durable takeaway:
  - portfolio bridge QA now checks whether the report is clearly framed as workflow validation, not as final portfolio winner selection.

### 2026-04-17
- Reorganized the full `Phase 21` test checklist for readability.
- Changed:
  - rewrote `PHASE21_TEST_CHECKLIST.md` around a consistent structure:
    - what to verify
    - where to verify it
    - concrete checkbox items
  - converted scattered location notes into tables for validation frame, family reruns, portfolio bridge, and closeout
  - kept existing user QA checkmarks while making section 3 less noisy and easier to follow
  - synced the Phase 21 TODO board and finance doc index
- Durable takeaway:
  - Phase 21 QA should now be executable from top to bottom without asking where each evidence item lives.

### 2026-04-17
- Closed `Phase 21` after user checklist completion and opened `Phase 22`.
- Changed:
  - marked `PHASE21_CURRENT_CHAPTER_TODO.md` and `PHASE21_COMPLETION_SUMMARY.md` as `phase_complete / manual_validation_completed`
  - created the `Phase 22 Portfolio-Level Candidate Construction` phase bundle with the repo-local bootstrap helper
  - rewrote the Phase 22 plan from template text into a plain-language kickoff document
  - created `PHASE22_PORTFOLIO_LEVEL_CANDIDATE_SEMANTICS_FIRST_WORK_UNIT.md`
  - added `Portfolio-Level Candidate`, `Portfolio Bridge`, `Saved Portfolio Replay`, and `Date Alignment` to the shared glossary
  - synced `MASTER_PHASE_ROADMAP.md` and `FINANCE_DOC_INDEX.md`
- Durable takeaway:
  - Phase 22 is now active, and the immediate next work is to turn the Phase 21 `33 / 33 / 34` portfolio bridge into a controlled baseline portfolio candidate pack rather than treating it as a final winner.

### 2026-04-17
- Completed the first `Phase 22` baseline portfolio candidate pack report.
- Changed:
  - created `backtest_reports/phase22/README.md`
  - created `backtest_reports/phase22/PHASE22_BASELINE_PORTFOLIO_CANDIDATE_PACK_FIRST_PASS.md`
  - clarified that the `Phase 21` `33 / 33 / 34` label is a near-equal shorthand, while the saved definition is `[33.33, 33.33, 33.33]` normalized to equal thirds
  - fixed the baseline portfolio status as `baseline_candidate / portfolio_watchlist / not_deployment_ready`
  - reviewed `CURRENT_CANDIDATE_REGISTRY.jsonl`; validation passes, but no append was made because portfolio-level candidate registry semantics are not defined yet
  - synced Phase 22 TODO/checklist, roadmap, finance doc index, backtest report index, and current practical candidate summary
- Durable takeaway:
  - `phase22_annual_strict_equal_third_baseline_v1` is now the first portfolio-level baseline candidate pack, but not a final portfolio winner.

### 2026-04-17
- Completed the second `Phase 22` benchmark / guardrail / weight-scope work unit.
- Changed:
  - created `PHASE22_PORTFOLIO_BENCHMARK_GUARDRAIL_AND_WEIGHT_SCOPE_SECOND_WORK_UNIT.md`
  - set the primary portfolio benchmark to `phase22_annual_strict_equal_third_baseline_v1`
  - kept `SPY` as market context rather than the Phase 22 primary gate
  - clarified that component benchmarks remain component-level quality checks, not portfolio-level benchmarks
  - defined portfolio-level guardrail as report-level warning, not an actual trading rule
  - narrowed next weight alternatives to `25 / 25 / 50` and `40 / 40 / 20`
  - added `Portfolio-Level Benchmark`, `Portfolio-Level Guardrail`, and `Weight Alternative` to the glossary
  - synced Phase 22 TODO/checklist, roadmap, finance doc index, and backtest report index
- Durable takeaway:
  - the next actual validation step is no longer open-ended; rerun only the two scoped weight alternatives against the equal-third baseline.

### 2026-04-17
- Completed the `Phase 22` weight alternative first-pass rerun.
- Changed:
  - reran the saved portfolio compare context for `Value / Quality / Quality + Value` strict annual anchors
  - compared official equal-third baseline `[33.33, 33.33, 33.33]` against `25 / 25 / 50` and `40 / 40 / 20`
  - created `PHASE22_WEIGHT_ALTERNATIVE_RERUN_FIRST_PASS.md`
  - reconciled the earlier `33 / 33 / 34` Phase 21 near-equal metric with the Phase 22 official equal-third baseline metric
  - updated the Phase 22 TODO, checklist, completion summary, next-phase prep, roadmap, finance doc index, and backtest report index
- Durable takeaway:
  - `25 / 25 / 50` improves raw return but creates `Quality + Value` concentration, while `40 / 40 / 20` lowers drawdown only slightly while giving up CAGR; equal-third remains the Phase 22 primary portfolio baseline.

### 2026-04-17
- Prepared `Phase 22` for manual validation.
- Changed:
  - marked the Phase 22 TODO board as `manual_validation_ready`
  - finalized the Phase 22 checklist around portfolio candidate semantics, baseline report, saved replay, benchmark / guardrail policy, and weight alternative rerun
  - synced the completion summary, next-phase preparation, roadmap, and finance doc index with the manual QA handoff state
- Durable takeaway:
  - Phase 22 implementation/reporting work is ready for user checklist QA; the next decision is closeout vs one more diversified-component portfolio check.

### 2026-04-18
- Polished the `Phase 22` plan and checklist entry point during manual QA.
- Changed:
  - rewrote `PHASE22_PORTFOLIO_LEVEL_CANDIDATE_CONSTRUCTION_PLAN.md` around purpose, necessity, minimum candidate conditions, actual execution order, and checklist usage
  - removed the duplicated feel between `목적` and `쉽게 말하면` by combining the explanation into `목적: 쉽게 말하면`
  - updated `PHASE22_TEST_CHECKLIST.md` section 1 so the user can see exactly which document sections to read and what each checkbox means
  - synced the Phase 22 TODO board and finance doc index
- Durable takeaway:
  - Phase 22 QA should now start from a clearer orientation document, not a phase memo that expects prior chat context.

### 2026-04-18
- Clarified the `Phase 22` development-validation boundary during manual QA.
- Changed:
  - updated the Phase 22 plan to state that the phase is not selecting a live investment portfolio
  - clarified that `Value / Quality / Quality + Value` are representative fixtures for portfolio workflow validation, not a final recommended allocation
  - clarified that the equal-third baseline is a development-validation comparison baseline, not an investment benchmark
  - updated the Phase 22 baseline report and checklist with the same boundary
- Durable takeaway:
  - Phase 22 should be read as portfolio-construction workflow validation for the quant program, not as final portfolio research or live-deployment approval.

### 2026-04-18
- Refreshed the master roadmap after the user identified phase drift risk.
- Changed:
  - added a product development direction section to `MASTER_PHASE_ROADMAP.md`
  - fixed the default roadmap stance as development-first, not investment-analysis-first
  - clarified that user-requested backtests / analysis can still be run during QA, but should be recorded as explicit analysis rather than phase direction drift
  - realigned `Phase 23~25` toward quarterly / alternate cadence productionization, new strategy implementation bridge, and validation / pre-live scaffolding
  - synced Phase 22 next-phase prep, completion summary, TODO, checklist, doc index, and glossary terms
- Durable takeaway:
  - After Phase 22 QA, the default next move is to close the portfolio workflow development-validation phase and return to core product implementation, starting with quarterly / alternate cadence productionization.

### 2026-04-19
- Closed `Phase 22` after user checklist completion.
- Changed:
  - accepted the completed `PHASE22_TEST_CHECKLIST.md` manual QA state
  - marked `PHASE22_CURRENT_CHAPTER_TODO.md` and `PHASE22_COMPLETION_SUMMARY.md` as `phase complete / manual_validation_completed`
  - refreshed `PHASE22_NEXT_PHASE_PREPARATION.md` so it reads as a Phase 23 handoff rather than a pending QA draft
  - synced `MASTER_PHASE_ROADMAP.md` and `FINANCE_DOC_INDEX.md`
- Durable takeaway:
  - Phase 22 is now closed as portfolio workflow development validation, not as investment portfolio approval. The next default main phase is `Phase 23 Quarterly And Alternate Cadence Productionization`.

### 2026-04-19
- Advanced `Phase 23` representative quarterly smoke validation.
- Changed:
  - ran DB-backed smoke runs for `Quality / Value / Quality + Value` strict quarterly prototypes with `AAPL / MSFT / GOOG`, 2021-01-01~2024-12-31, and non-default portfolio handling contracts
  - found that common result bundle meta did not preserve `weighting_mode`, `rejected_slot_handling_mode`, `rejected_slot_fill_enabled`, and `partial_cash_retention_enabled`
  - fixed `build_backtest_result_bundle()` so portfolio handling contract meta is preserved for history / load-into-form workflows
  - created `PHASE23_QUARTERLY_CONTRACT_SMOKE_VALIDATION_FIRST_PASS.md`
  - synced Phase 23 TODO, completion summary, checklist, finance analysis, and backtest report index
- Durable takeaway:
  - quarterly strict family now passes DB-backed smoke validation for portfolio handling contract delivery and meta preservation; remaining Phase 23 validation is UI-level history / saved replay confirmation.

### 2026-04-19
- Prepared `Phase 23` for manual validation.
- Changed:
  - added quarterly portfolio handling contract fields to persisted backtest history records
  - updated history payload rebuild so `Run Again` and `Load Into Form` preserve `weighting_mode`, `rejected_slot_handling_mode`, and related flags
  - updated saved portfolio strategy overrides so `Replay Saved Portfolio` preserves quarterly rejected-slot handling semantics
  - verified result bundle meta -> history record -> history payload -> saved portfolio override roundtrip with a representative quarterly smoke bundle
  - created `PHASE23_HISTORY_AND_SAVED_REPLAY_CONTRACT_ROUNDTRIP_THIRD_WORK_UNIT.md`
  - synced Phase 23 TODO, checklist, completion summary, next-phase prep, roadmap, finance analysis, and doc index
- Durable takeaway:
  - Phase 23 code-level work is now manual-validation-ready; the remaining gate is user UI QA through `PHASE23_TEST_CHECKLIST.md`.

### 2026-04-19
- Refined `Phase 23` compare QA UX after user checklist feedback.
- Changed:
  - confirmed the Compare variant refresh issue came from `Variant` selectboxes living inside `st.form()`
  - moved `Quality / Value / Quality + Value` compare variant selectors outside the form into a dedicated `Strategy Variants` section
  - kept `Advanced Inputs > Strategy-Specific Advanced Inputs` as the detailed settings area for the currently selected variant
  - avoided the previously rejected Apply/Refresh button pattern
  - rewrote unclear Phase 23 checklist items around concrete screen locations: `Data Requirements`, `Statement Shadow Coverage Preview`, `Universe Contract`, and `Strategy Variants`
  - created `PHASE23_COMPARE_VARIANT_IMMEDIATE_REFRESH_FOURTH_WORK_UNIT.md`
- Durable takeaway:
  - Annual / Quarterly changes in Compare should now immediately refresh the lower advanced option UI without extra buttons, and the checklist is more directly testable.

### 2026-04-19
- Flattened the `Phase 23` compare input layout after follow-up UX feedback.
- Changed:
  - removed the compare `st.form()` wrapper and `Advanced Inputs` expander from the compare configuration area
  - moved `Start Date`, `End Date`, `Timeframe`, and `Option` into a shared `Compare Period & Shared Inputs` section
  - moved Annual / Quarterly variant selectors into each `Quality / Value / Quality + Value` strategy box
  - replaced strategy-level expanders with border boxes while keeping lower `Overlay`, `Portfolio Handling`, real-money, and guardrail expanders intact
  - kept a single `Run Strategy Comparison` action button and avoided the rejected Apply / Refresh pattern
  - synced the Phase 23 checklist, fourth work-unit note, TODO board, completion summary, next-phase prep, roadmap, doc index, finance analysis, and question log
- Durable takeaway:
  - Compare QA should now read as common execution inputs first, then one visible box per selected strategy, with variant selection and settings in the same box.

### 2026-04-19
- Tightened `Phase 23` compare/history QA details after checklist feedback.
- Changed:
  - wrapped strict quarterly compare `Trend Filter` and `Market Regime` inputs inside the same `Overlay` expander used by annual strict compare paths
  - kept `Portfolio Handling & Defensive Rules` as the adjacent lower expander for quarterly rejected-slot, weighting, and risk-off settings
  - changed `Back To History` after `Load Into Form` to use a panel-switch callback so the History panel is requested before the radio widget renders
  - rewrote Phase 23 checklist section 3 to explain where to verify saved compare context, saved portfolio context, history run, load-into-form, run-again, and replay saved portfolio
- Durable takeaway:
  - Quarterly compare QA now has the same top-level section rhythm as annual strict, and the checklist distinguishes history rerun from saved portfolio replay.

### 2026-04-19
- Refined the finance phase checklist writing rule after Phase 23 QA feedback.
- Changed:
  - removed the standalone `용어 기준` block from `PHASE23_TEST_CHECKLIST.md`
  - moved the relevant screen paths directly into each section 3 checkbox
  - updated `PHASE_TEST_CHECKLIST_TEMPLATE.md` so future checklists avoid separate glossary-like blocks and instead write exact UI paths inside checklist items
  - updated `FINANCE_DOC_INDEX.md` so the checklist-template entry mentions the same location-first rule
  - synced `PHASE23_CURRENT_CHAPTER_TODO.md` with the checklist wording cleanup
- Durable takeaway:
  - Future finance checklists should be action/location-first: each checkbox should say where to go and what to verify.

### 2026-04-20
- Closed `Phase 23` and opened `Phase 24`.
- Changed:
  - accepted the user's Phase 23 completion signal and marked the remaining checklist item complete
  - updated `PHASE23_CURRENT_CHAPTER_TODO.md`, `PHASE23_COMPLETION_SUMMARY.md`, and `PHASE23_NEXT_PHASE_PREPARATION.md` to `phase complete / manual_validation_completed`
  - bootstrapped `phase24` docs from the finance phase bundle helper
  - rewrote the Phase 24 plan, TODO, checklist, completion draft, next-phase draft, and first work-unit note for the new strategy expansion / research-to-implementation bridge
  - selected `Global Relative-Strength Allocation With Trend Safety Net` as the first implementation candidate because it is price-only, ETF-based, monthly, and compatible with the current DB-backed strategy infrastructure
  - synced `MASTER_PHASE_ROADMAP.md` and `FINANCE_DOC_INDEX.md`
- Durable takeaway:
  - Phase 24 is now active as a development phase for adding a new strategy family, not as an investment-performance analysis phase.

### 2026-04-20
- Ran a user-requested `GTAA` expanded-universe follow-up.
- Changed:
  - re-tested the existing compact `SPY / QQQ / GLD / IEF` `Top = 2` candidate through the latest DB date `2026-04-17`
  - added `TLT` to form a clean 6 ETF core: `SPY / QQQ / GLD / IEF / LQD / TLT`
  - found a new expanded `Top = 1`, `Interval = 8`, `1M / 3M / 6M` candidate with `21.50% CAGR`, `-6.49% MDD`, and `real_money_candidate / paper_probation / paper_only`
  - confirmed the same 6 ETF core with `Top = 2`, `Interval = 4`, `1M / 3M / 6M` remains `production_candidate / watchlist / watchlist_only`
  - documented the result in `GTAA_EXPANDED_UNIVERSE_FOLLOWUP_20260420.md` and synced the GTAA strategy hub, backtest log, report index, current candidate summary, and candidate registry
- Durable takeaway:
  - ticker breadth improved the aggressive GTAA paper candidate, but the balanced 2-holding representative remains the compact `SPY / QQQ / GLD / IEF` candidate until expanded `Top = 2` validation improves.

### 2026-04-20
- Advanced `Phase 24` first new strategy implementation.
- Changed:
  - added `Global Relative Strength` core simulation in `finance.strategy`
  - added DB-backed helper/defaults in `finance.sample`
  - added web runtime wrapper `run_global_relative_strength_backtest_from_db`
  - verified targeted `py_compile`, synthetic strategy smoke, runtime import smoke, and DB-backed smoke run
  - created `PHASE24_GLOBAL_RELATIVE_STRENGTH_CORE_RUNTIME_SMOKE_VALIDATION.md`
  - synced Phase 24 TODO, completion draft, next-phase prep, roadmap, doc index, backtest report index, and finance analysis
- Durable takeaway:
  - `Global Relative Strength` is now implemented at core/runtime level, but it is not yet exposed in `Backtest` UI, compare, history, or saved replay.

### 2026-04-20
- Reorganized the `FINANCE_COMPREHENSIVE_ANALYSIS.md` detailed implementation memo governance.
- Changed:
  - clarified that `3-3. 상세 구현 메모` is a legacy archive, not the current source of truth
  - added a management policy for where future current-state, phase, backtest, glossary, candidate, and workflow records should live
  - added a short future-record template with date, phase, category, affected area, source, and re-review condition
  - added a topic index so the long legacy memo can be searched without treating every old note as current behavior
- Durable takeaway:
  - Future finance implementation notes should not be appended indefinitely to `3-3`; new details should be routed to the correct canonical document and only summarized in the comprehensive analysis when they affect current system behavior.

### 2026-04-20
- Established the first finance code analysis documentation system.
- Changed:
  - created `.note/finance/code_analysis/` as the developer-facing place for durable code flow documents
  - added flow docs for backtest runtime, data/DB pipeline, web backtest UI, strategy implementation, and automation scripts
  - updated `FINANCE_COMPREHENSIVE_ANALYSIS.md` so it remains the high-level map and points detailed code flow readers to `code_analysis/`
  - updated `FINANCE_DOC_INDEX.md`, `AGENTS.md`, and the active `finance-doc-sync` skill guidance to include the new code analysis update rule
- Durable takeaway:
  - Future code changes should update `code_analysis/` only when the durable code flow changes; small copy edits, one-off results, and phase status updates should stay out of those developer flow documents.

### 2026-04-20
- Slimmed `FINANCE_COMPREHENSIVE_ANALYSIS.md` now that `code_analysis/` exists.
- Changed:
  - reduced section 4 from detailed file-by-file code notes to a concise system layer table
  - reduced section 12 from long strategy/contract implementation history to a compact code entrypoint map
  - reduced section 18 to a short automation baseline table
  - moved durable strategy contract and runtime interpretation details into `code_analysis/STRATEGY_IMPLEMENTATION_FLOW.md` and `code_analysis/BACKTEST_RUNTIME_FLOW.md`
- Durable takeaway:
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md` should now stay as the high-level map, while detailed developer flow should live under `.note/finance/code_analysis/`.

### 2026-04-20
- Established the first finance data architecture documentation system.
- Changed:
  - created `.note/finance/data_architecture/` as the place for data flow, DB schema map, table semantics, and PIT/data-quality notes
  - moved the detailed meaning of sections 5~7 out of `FINANCE_COMPREHENSIVE_ANALYSIS.md` into dedicated data architecture documents
  - reduced `FINANCE_COMPREHENSIVE_ANALYSIS.md` sections 5~7 to high-level flow, DB, and table-semantics summaries
  - updated `FINANCE_DOC_INDEX.md`, `AGENTS.md`, and the active `finance-doc-sync` skill guidance to include the new data architecture update rule
- Durable takeaway:
  - Future DB/table/source-of-truth or PIT/data-quality meaning changes should update `data_architecture/`, while the comprehensive analysis should keep only the top-level data map.

### 2026-04-20
- Refreshed `FINANCE_COMPREHENSIVE_ANALYSIS.md` sections 8~18 using the current finance documentation set.
- Changed:
  - updated sections 8~9 from older ETF/sample-strategy framing to the current product / strategy / portfolio / pre-live layer view
  - condensed sections 10~11 into current limitation and data-quality summaries that point to `data_architecture/`
  - rewrote section 12 as a code entrypoint map that points to `code_analysis/`
  - updated sections 13~18 to reflect the current development boundary, Phase 25 pre-live direction, future data priorities, and automation / persistence baseline
- Durable takeaway:
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md` now acts as a high-level orientation map for the current product, while detailed code, DB, phase, and result records are delegated to their canonical sub-documents.

### 2026-04-20
- Tightened the update policy for `FINANCE_COMPREHENSIVE_ANALYSIS.md`.
- Changed:
  - updated `AGENTS.md` so `FINANCE_COMPREHENSIVE_ANALYSIS.md` is reviewed after finance changes but updated only when the high-level current-state map changes
  - updated `FINANCE_COMPREHENSIVE_ANALYSIS.md` and `FINANCE_DOC_INDEX.md` to state that one-off results, phase progress, detailed call flows, and table-level semantics belong in the specialized docs
  - updated the active `finance-doc-sync` skill with the same rule
- Durable takeaway:
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md` should show the big picture of the current system, not absorb every implementation detail or experiment record.

### 2026-04-20
- Split the legacy detailed implementation memo out of `FINANCE_COMPREHENSIVE_ANALYSIS.md`.
- Changed:
  - moved the long former `3-3. 상세 구현 메모` into `.note/finance/archive/FINANCE_COMPREHENSIVE_ANALYSIS_LEGACY_IMPLEMENTATION_NOTES_20260420.md`
  - replaced the root `3-3` section with a short archive pointer and future record-routing rule
  - updated `FINANCE_DOC_INDEX.md` and `.note/finance/archive/README.md` so the archive is discoverable
- Durable takeaway:
  - `FINANCE_COMPREHENSIVE_ANALYSIS.md` is now much closer to a current-state map, while legacy implementation history remains preserved but out of the main reading path.

### 2026-04-20
- Clarified the finance product goal versus current phase boundary.
- Changed:
  - updated `FINANCE_COMPREHENSIVE_ANALYSIS.md` so the project goal is not described as merely data collection and backtesting
  - clarified that the long-term target is an evidence-based investment candidate recommendation and portfolio construction proposal program
  - updated `MASTER_PHASE_ROADMAP.md`, `AGENTS.md`, and the active `finance-doc-sync` skill to separate final product target from near-term development / validation phase execution
- Durable takeaway:
  - Strong backtest results are not automatic live recommendations, but the product being built is intended to support investment candidate and portfolio proposal workflows after sufficient validation.

### 2026-04-21
- Organized loose root finance Markdown documents into purpose-specific folders.
- Changed:
  - moved operations / runtime / registry / ingestion reference docs under `.note/finance/operations/`
  - moved daily market update notes under `.note/finance/operations/daily_market_update/`
  - moved research reference docs under `.note/finance/research/`
  - moved support-track discussion docs under `.note/finance/support_tracks/`
  - moved the legacy backtest refinement flow guide under `.note/finance/code_analysis/`
  - updated `FINANCE_DOC_INDEX.md`, active links, and added folder README files
- Durable takeaway:
  - `.note/finance/` root should now stay focused on top-level maps, active logs, glossary, and templates.

### 2026-04-21
- Standardized phase status terminology for finance roadmap/index documents.
- Changed:
  - added a `Phase 상태값 읽는 법` section to `FINANCE_DOC_INDEX.md`
  - initially normalized recent phase status labels to underscore-based canonical values such as `phase_complete / manual_validation_completed`
  - aligned the `MASTER_PHASE_ROADMAP.md` current-position status summary with the same labels
  - added `Phase Status` to `FINANCE_TERM_GLOSSARY.md`
  - updated `AGENTS.md` and the active `finance-doc-sync` skill so future phase indexes use the same status vocabulary
- Durable takeaway:
  - This was immediately refined into the split-column progress / validation model below, because that is easier to read than one combined status string.

### 2026-04-21
- Refined the phase status model to split progress status from validation status.
- Changed:
  - updated `FINANCE_DOC_INDEX.md` so the phase quick map now has separate `진행 상태`, `검증 상태`, and `다음 확인` columns
  - updated `MASTER_PHASE_ROADMAP.md` current-position summary to the same split-column model
  - updated `FINANCE_TERM_GLOSSARY.md`, `AGENTS.md`, and the active `finance-doc-sync` skill to prefer split phase status labels
  - clarified that `first_chapter_completed` is legacy partial-completion wording, not a signal to introduce a formal chapter hierarchy
- Durable takeaway:
  - Future phase management should stay phase-based, not chapter-based, and should separate work progress from QA/validation status.

### 2026-04-21
- Advanced Phase 25 from boundary definition into Pre-Live candidate record persistence.
- Changed:
  - added `plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py`
  - defined `.note/finance/PRE_LIVE_CANDIDATE_REGISTRY.jsonl` as the append-only Pre-Live operating-state registry
  - added `.note/finance/operations/PRE_LIVE_CANDIDATE_REGISTRY_GUIDE.md`
  - added `PHASE25_PRE_LIVE_CANDIDATE_RECORD_CONTRACT_SECOND_WORK_UNIT.md`
  - updated Phase 25 plan, TODO, checklist, completion draft, next-phase draft, roadmap, doc index, comprehensive analysis, automation guide, AGENTS, and active finance-doc-sync guidance
- Validation:
  - `py_compile` passed for the new pre-live registry helper and hygiene helper
  - `manage_pre_live_candidate_registry.py validate` passes with an empty registry
  - `manage_current_candidate_registry.py validate` still passes for existing current candidate records
- Durable takeaway:
  - `CURRENT_CANDIDATE_REGISTRY.jsonl` defines the candidate; `PRE_LIVE_CANDIDATE_REGISTRY.jsonl` records how that candidate is handled before live use.

### 2026-04-21
- Advanced Phase 25 into the operator review workflow work unit.
- Changed:
  - added `PHASE25_OPERATOR_REVIEW_WORKFLOW_THIRD_WORK_UNIT.md`
  - extended `manage_pre_live_candidate_registry.py` with `draft-from-current <registry_id>`
  - mapped current candidate Real-Money signals into default Pre-Live statuses:
    `paper_probation -> paper_tracking`, `watchlist -> watchlist`, blockers -> `hold`, reject/fail signals -> `reject`, otherwise `re_review`
  - kept the workflow safe by making draft output the default and requiring `--append` for actual registry writes
  - updated Phase 25 TODO, checklist, completion draft, next-phase draft, operations guide, automation guide, doc index, comprehensive analysis, AGENTS, and active finance-doc-sync guidance
- Validation:
  - `py_compile` passed for `manage_pre_live_candidate_registry.py`
  - `draft-from-current value_current_anchor_top14_psr` outputs a valid `paper_tracking` draft
  - `draft-from-current value_lower_mdd_near_miss_pfcr` outputs a valid `watchlist` draft
- Durable takeaway:
  - Phase 25 now has a helper/report-based entry point for converting current candidates into Pre-Live operating drafts, without automatically approving or saving anything.

### 2026-04-21
- Added the Phase 25 Pre-Live Review UI entry point.
- Changed:
  - added `Pre-Live Review` as a fourth Backtest panel
  - added a current-candidate-to-Pre-Live review UI in `app/web/pages/backtest.py`
  - users can select a current candidate, review Real-Money signals, choose a Pre-Live status, edit operator reason / next action / review date, inspect the JSON draft, and save explicitly
  - saved active records are shown in the same panel's `Pre-Live Registry` tab
  - added `PHASE25_PRE_LIVE_REVIEW_UI_FOURTH_WORK_UNIT.md`
  - updated Phase 25 TODO, checklist, completion/next docs, roadmap, doc index, comprehensive analysis, Pre-Live guide, and web UI flow docs
- Validation:
  - `python3 -m py_compile app/web/pages/backtest.py` passed
  - `.venv/bin/python` import of `app.web.pages.backtest` passed
- Durable takeaway:
  - Phase 25 implementation is now ready for user manual QA. The UI still does not enable live trading; it only records pre-live operating state.

### 2026-04-21
- Clarified the Phase 25 Real-Money vs Pre-Live boundary after user QA feedback.
- Changed:
  - updated the first Phase 25 work-unit document so Pre-Live is not described as status labels only
  - defined the Pre-Live "next action record" as an action package:
    `operator_reason`, `next_action`, `review_date`, `tracking_plan.cadence`, `tracking_plan.stop_condition`, `tracking_plan.success_condition`, and supporting docs
  - updated the Phase 25 plan, Pre-Live registry guide, glossary, and checklist to say that status alone is not the distinguishing feature
- Durable takeaway:
  - `pre_live_status` can resemble Real-Money promotion / shortlist labels. The actual Pre-Live distinction is the recorded operating plan for what to check next, when to review, and when to stop or advance.

### 2026-04-21
- Closed Phase 25 after user manual QA completion.
- Changed:
  - updated Phase 25 TODO, completion summary, next-phase preparation, and checklist to `complete / manual_qa_completed`
  - synced `MASTER_PHASE_ROADMAP.md`, `FINANCE_DOC_INDEX.md`, and `FINANCE_COMPREHENSIVE_ANALYSIS.md`
  - recorded that no additional `AGENTS.md` or skill guidance change was needed at closeout because Pre-Live registry and QA closeout rules were already reflected
- Validation:
  - Phase 25 checklist was completed by the user before closeout
- Durable takeaway:
  - Phase 25 is closed as a Pre-Live operating-record workflow, not as live trading or automatic investment approval.

### 2026-04-21
- Opened Phase 26 and documented the Phase 26~30 roadmap direction.
- Changed:
  - created the Phase 26 document bundle for `Foundation Stabilization And Backlog Rebase`
  - added the first Phase 26 work-unit document for phase status and backlog rebase
  - updated `MASTER_PHASE_ROADMAP.md` with Phase 26~30:
    Phase 26 foundation stabilization, Phase 27 data integrity, Phase 28 strategy family parity, Phase 29 candidate review workflow, Phase 30 portfolio proposal / pre-live monitoring
  - updated `FINANCE_DOC_INDEX.md`, `FINANCE_COMPREHENSIVE_ANALYSIS.md`, and `FINANCE_TERM_GLOSSARY.md`
- Durable takeaway:
  - Live Readiness / Final Approval is intentionally deferred until after Phase 30. Phase 26 starts by stabilizing backlog and foundation gaps before new product expansion.

### 2026-04-21
- Completed Phase 26 implementation handoff.
- Changed:
  - added `PHASE26_BACKLOG_REBASE_AND_FOUNDATION_GAP_MAP.md`
  - reclassified Phase 8, 9, 12~15, and 18 as `complete / superseded_by_later_phase`
  - separated Phase 27 data integrity, Phase 28 strategy parity, Phase 29 candidate review, and Phase 30 portfolio proposal inputs
  - updated roadmap, doc index, glossary, comprehensive analysis, AGENTS, and active finance-doc-sync guidance for the new validation label
  - finalized the Phase 26 checklist for user QA
- Validation:
  - documentation consistency and hygiene checks are the relevant checks for this document-only phase
- Durable takeaway:
  - No old pending phase is an immediate blocker before Phase 27. Old pending checklists are now historical references or later-phase inputs, not active QA gates.
