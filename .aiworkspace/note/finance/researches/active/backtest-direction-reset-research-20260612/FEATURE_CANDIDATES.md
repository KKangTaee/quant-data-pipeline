# Feature Candidates

Status: Active
Last Updated: 2026-06-12 KST

Scoring: 1 low, 5 high. Priority starts from `impact + fit + confidence - effort - risk`, then adjusted for whether the candidate reduces product confusion or data correctness risk.

## Summary

The next build should not be "add the next strategy panel." The highest-fit candidates make Backtest Analysis clearer by strengthening compact handoff contracts, replay semantics, and strategy maturity labels while keeping validation/review/monitoring responsibilities downstream.

## Candidate Matrix

| Candidate | Bucket | Impact | Effort | Risk | Confidence | Strategic Fit | Owner Area |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Backtest Result Handoff Contract | Now | 5 | 3 | 2 | 4 | 5 | Backtest web/service |
| Strategy Maturity Ruleset As Compact Read Model | Now | 5 | 2 | 2 | 4 | 5 | Backtest service / Reference |
| Replay Semantics Cleanup For History / Saved Setup | Next | 4 | 3 | 3 | 4 | 5 | Backtest runtime/service/web |
| ETF Evidence Expansion Sequence | Next | 4 | 3 | 3 | 4 | 4 | Backtest runtime/service + reports |
| Strict Annual + ETF Sleeve Validation Handoff | Next | 5 | 4 | 3 | 4 | 5 | Backtest web + Practical Validation |
| Risk-On Momentum Governance Design | Later | 5 | 4 | 5 | 4 | 4 | Strategy + validation + monitoring |
| Strict Quarterly Prototype Maturation Gate | Later | 4 | 4 | 5 | 3 | 4 | Strategy/runtime + validation |
| New Strategy Discovery / Optimizer / Marketplace | Parking Lot | 3 | 5 | 5 | 2 | 1 | Out of current scope |
| Live Broker / Auto Rebalance Integration | Parking Lot | 2 | 5 | 5 | 1 | 0 | Out of product boundary |

## Candidates

### Backtest Result Handoff Contract

- Bucket: Now
- Problem: Backtest Analysis can produce good-looking results, but the product does not yet have one compact, consistent post-result signal that says what can happen next.
- User workflow change: After a run or saved replay, the user sees a concise handoff strip: result reproducibility, maturity label, warnings/data trust, Practical Validation eligibility, and missing gate reason.
- Evidence:
  - Audit: 4C made the screen execution-first, while 5A/5B improved runtime metadata without new panels.
  - Benchmarks: QuantConnect separates result/report/history and supports OOS policy; Portfolio123 warns against CAGR-only promotion.
- Required code/data/doc areas:
  - Future implementation only: `app/services/backtest_result_read_model.py`, `app/web/backtest_result_display.py`, `app/web/backtest_compare.py`, `app/web/backtest_single_strategy.py`, possibly Reference docs.
  - No registry/saved/run_history rewrite.
- Dependencies:
  - Strategy maturity ruleset.
  - Existing result bundle metadata and warnings.
- Risks:
  - Could become another panel if overbuilt.
  - Could imply validation if copy is loose.
- Validation idea:
  - Streamlit-free service tests for handoff labels.
  - Browser QA that default Backtest Analysis remains execution-first.
- Owner skill:
  - Future approved scope: `finance-backtest-web-workflow`.
- Priority rationale:
  - Highest fit because it solves the product confusion without adding a new workflow stage.

### Strategy Maturity Ruleset As Compact Read Model

- Bucket: Now
- Problem: Strategy maturity exists in 3A services/docs, but the default screen should not become a maturity dashboard.
- User workflow change: Strategy options or result summaries can show one compact maturity label and gate reason. Full maturity details move to Reference/report or remain hidden.
- Evidence:
  - Audit: `app/services/backtest_strategy_evidence_inventory.py` already encodes useful strategy rows.
  - Benchmarks: Portfolio123 and QuantConnect both reinforce explicit maturity/robustness gates.
- Required code/data/doc areas:
  - Future implementation only: strategy catalog/read model, Reference help/report location, result display copy.
- Dependencies:
  - Human approval of label set:
    - Candidate-ready source
    - Runtime-hardened / evidence needed
    - Research lane
    - Prototype
    - Legacy / compatibility
- Risks:
  - Too many labels can distract.
  - Label drift if strategy catalog changes without tests.
- Validation idea:
  - Catalog coverage test.
  - Snapshot test for listed strategy groups.
- Owner skill:
  - Future approved scope: `finance-backtest-web-workflow`; if runtime labels require strategy metadata, pair with `finance-strategy-implementation`.
- Priority rationale:
  - Small enough for 1차 and directly reduces over-promotion risk.

### Replay Semantics Cleanup For History / Saved Setup

- Bucket: Next
- Problem: History replay and saved portfolio replay are powerful, but users can mistake "replayable" for "validated."
- User workflow change: History and saved setup surfaces consistently say whether the record is a replayable setup, validation source, or selected monitoring record.
- Evidence:
  - Audit: Candidate Library replay supports ETF + strict annual, not quarterly/Risk-On candidate lifecycle.
  - Benchmarks: QuantConnect history/report split and IBKR custom report save/rerun patterns separate saved artifact from approval.
- Required code/data/doc areas:
  - Future implementation only: `app/web/backtest_history*.py`, `app/services/backtest_saved_portfolio_replay.py`, `app/runtime/candidate_library.py`, Reference guide copy.
- Dependencies:
  - Handoff contract terms.
  - Decision on whether to keep Candidate Library as support/archive rather than primary route.
- Risks:
  - Could touch broad UI surface.
  - Must not rewrite JSONL.
- Validation idea:
  - Existing replay tests plus browser QA for history/saved copy.
- Owner skill:
  - `finance-backtest-web-workflow`.
- Priority rationale:
  - Important after the first contract is accepted.

### ETF Evidence Expansion Sequence

- Bucket: Next
- Problem: GRS, Risk Parity, and Dual Momentum now have stronger runtime/result contracts, but durable current anchors and ETF evidence reports lag behind GTAA.
- User workflow change: These strategies get current anchor / near miss / not-ready reason / required evidence as report/reference work before any promotion.
- Evidence:
  - Audit: 5A/5B preserved useful result metadata; current evidence depth remains thin.
  - Benchmarks: Koyfin ETF caveats show why ETF holdings/exposure evidence needs explicit limitations.
- Required code/data/doc areas:
  - Future implementation only: strategy report hub, possibly existing ETF evidence expansion read model, no new default panel.
- Dependencies:
  - Decide first strategy order:
    - GRS first because 5A is fresh.
    - Or Risk Parity / Dual Momentum first because 5B just exposed contracts.
- Risks:
  - May slide back into panel/workbench growth.
  - Provider evidence can be overstated.
- Validation idea:
  - Report/source verification, no JSONL writes, optional focused runtime smoke if user approves.
- Owner skill:
  - `finance-strategy-implementation` for runtime smoke, `finance-backtest-web-workflow` only if UI handoff changes.
- Priority rationale:
  - Strong next step after 1차 clarifies handoff.

### Strict Annual + ETF Sleeve Validation Handoff

- Bucket: Next
- Problem: Strict Annual 3종 plus GTAA/EW are the best candidate-ready group, but they need a clean bridge into Practical Validation without reading as final approval.
- User workflow change: User can pick a strict annual core plus ETF sleeve, then see what Practical Validation must verify: PIT, provider/liquidity, concentration, role/weight, drawdown, cost/turnover.
- Evidence:
  - Audit: strict annual + GTAA/EW are the evidence-mature group.
  - Benchmarks: Koyfin sleeves and IBKR reporting patterns support role/exposure/benchmark framing.
- Required code/data/doc areas:
  - Future implementation only: Backtest mix source handoff, Practical Validation source builder, component role / weight audit, Reference guidance.
- Dependencies:
  - Handoff contract accepted first.
  - No change to validation gate semantics without approval.
- Risks:
  - Could turn into portfolio recommendation if wording is careless.
  - Might touch Practical Validation, so blast radius is larger.
- Validation idea:
  - Service tests for source traits/role metadata, Browser QA across Backtest -> Practical Validation.
- Owner skill:
  - `finance-backtest-web-workflow`; possible `finance-doc-sync` only after implementation approval.
- Priority rationale:
  - High value, but should follow 1차 clarity work.

### Risk-On Momentum Governance Design

- Bucket: Later
- Problem: Risk-On Momentum has rich daily swing research evidence but no approved Practical Validation / Final Review / Portfolio Monitoring governance.
- User workflow change: It remains a research lane until daily swing evidence modules, selected-route rules, artifact policy, and monitoring cadence are designed.
- Evidence:
  - Audit: current code has explicit governance deferred board.
  - Benchmarks: QuantConnect research notebook split supports separation between research diagnostics and deployable workflow.
- Required code/data/doc areas:
  - Future design only at first: Risk-On runtime, generated artifact policy, Practical Validation module planner, Final Review gate, Portfolio Monitoring daily review policy.
- Dependencies:
  - User approval of whether Risk-On belongs in this cycle at all.
- Risks:
  - Highest product-boundary risk because daily signals can be mistaken for trading signals.
  - Survivorship/universe assumptions need explicit review.
- Validation idea:
  - No implementation until a separate governance design is approved.
- Owner skill:
  - `finance-strategy-implementation` + `finance-backtest-web-workflow`, after approval.
- Priority rationale:
  - Important but not immediate.

### Strict Quarterly Prototype Maturation Gate

- Bucket: Later
- Problem: Quarterly prototypes execute, but runtime success does not prove candidate readiness.
- User workflow change: Quarterly variants keep prototype labels until PIT quarterly evidence, filing lag, replay parity, validation compatibility, and report/current anchor gates pass.
- Evidence:
  - Audit: history helpers already label quarterly as deferred prototype.
  - Benchmarks: Portfolio123 robustness guidance and QuantConnect OOS holdout argue for strict gates.
- Required code/data/doc areas:
  - Future implementation only: strict runtime, history/saved replay, Candidate Library policy, Practical Validation source fit, strategy report.
- Dependencies:
  - Explicit user decision to do prototype maturation.
- Risks:
  - High over-promotion risk if recent performance is attractive.
  - PIT / filing lag complexity can invalidate naive comparisons.
- Validation idea:
  - TDD around quarterly metadata and replay parity before UI changes.
- Owner skill:
  - `finance-strategy-implementation`.
- Priority rationale:
  - Defer until after handoff/replay semantics are fixed.

## Parking Lot

- New Backtest Analysis evidence/governance/workbench panels.
- Direct provider / FRED fetch from UI.
- Registry / saved JSONL cleanup or rewrite as part of direction research.
- Live broker order, account sync, auto rebalance.
- Strategy marketplace / community ranking.
- New strategy discovery engine or optimizer.
- AI-generated investment recommendation.

## Rejected Ideas

| Idea | Why Rejected For Now |
| --- | --- |
| Continue directly into 5C Strict Quarterly Prototype | Quarterly needs a maturity gate first; immediate formalization would repeat the "execution means readiness" mistake. |
| Promote Risk-On Momentum to monitoring | Daily swing governance, artifact policy, and survivorship assumptions are not ready. |
| Bring 3A~4B panels back to default | Conflicts with the 4C reset and benchmark-backed task-first pattern. |
| Treat saved replay as validation | Saved replay proves reproducibility, not Practical Validation pass. |
