# Recommendation

Status: Active
Last Updated: 2026-06-12 KST

## Recommended Direction

Backtest Analysis should remain an execution / comparison / candidate-source workspace. The next approved work should strengthen compact handoff and maturity contracts, not add another evidence panel.

## One-Line Recommendation

Approve only a narrow 1차 `Backtest Result Handoff Contract` next: preserve execution-first Backtest Analysis, add compact maturity/handoff language, and defer quarterly/Risk-On promotion until separate gates exist.

The reset direction:

1. Keep 4C execution-first layout.
2. Keep 5A/5B runtime/result bundle hardening pattern.
3. Convert broad strategy maturity / governance concepts into compact labels, Reference/report guidance, or downstream gates.
4. Treat history and saved replay as reproducibility, not validation.
5. Defer strict quarterly formalization and Risk-On downstream promotion until separate maturity/governance gates are approved.

## Decision Scope

- Immediate next build candidate: `1차 Backtest Result Handoff Contract + compact maturity labels`.
- Needs human approval before execution: Any source code change, task/phase opening, roadmap doc update, Practical Validation behavior change, Final Review behavior change, Monitoring behavior change.
- Longer roadmap option: ETF evidence expansion, strict annual + ETF sleeve validation handoff, replay semantics cleanup.
- Not approved / parking lot: new panels, live broker/order/auto rebalance, direct provider/FRED fetch, strategy marketplace, new optimizer/discovery engine.

## Existing 3A~5B Work Classification

| Work | Keep / Hold / Rework / Discard Candidate | Reason |
| --- | --- | --- |
| 3A Strategy Evidence Inventory / Direction Panel | Keep as source material; rework placement | The maturity model is useful, but should not be default Backtest Analysis weight. Move toward compact read model / Reference / report. |
| 3B Strict Annual + GTAA / EW Bridge | Keep as source material; rework as downstream handoff | Good first evidence-mature group, but should lead to Practical Validation gate, not imply approval. |
| 3C Risk-On Governance | Keep as warning model; hold downstream promotion | Correctly says governance deferred. Do not promote Risk-On without separate design. |
| 3D ETF Evidence Expansion | Keep as source material; hold default UI | Good evidence gap framing. Use later for GRS / Risk Parity / Dual Momentum report/evidence expansion. |
| 4A ETF Current Anchor Workbench | Hold / reference only | Useful for internal readiness checks, but too heavy for primary screen. |
| 4B ETF Rerun Matrix Workbench | Hold / reference only | Session-only design is safe, but matrix experimentation should not become default product flow. |
| 4C Direction Reset | Keep | Correctly restored execution-first Backtest Analysis. |
| 5A GRS Runtime Contract | Keep | Right pattern: better runtime/replay/result metadata without new panels. |
| 5B Risk Parity / Dual Momentum Runtime Contract | Keep | Right pattern: interpretable result contracts without expanding UI. |
| 5C Strict Quarterly Prototype | Defer | Needs maturity gates before formalization; not the immediate next step. |

No existing work needs immediate physical deletion in this research recommendation. The discard candidate is the direction of default-screen panel growth, not necessarily the files themselves.

## Tentative Development Roadmap

This roadmap is a recommendation for approval, not an implementation plan.

### 1차. Backtest Result Handoff Contract

- Purpose: Make every run/replay result answer "what can I safely do next?" without adding a new panel.
- Screens / code / docs scope:
  - Likely future code: result read model and result display surfaces.
  - Likely docs: active task docs only if approved; durable docs after implementation.
  - No `docs/ROADMAP.md` update before approval.
- What not to do:
  - No Practical Validation behavior change.
  - No registry/saved/run_history rewrite.
  - No new Backtest Analysis workbench.
- Completion condition:
  - A compact handoff label distinguishes Run Result, Replayable Setup, Validation Source, and Monitoring Record.
  - Strategy maturity label and missing gate reason are visible where needed.
  - Default Backtest Analysis remains execution-first.
- Connection to next phase:
  - Enables replay semantics cleanup and validation handoff without re-litigating labels.
- Needed verification:
  - Streamlit-free read-model tests.
  - Browser QA default view and result view.
  - `git diff --check`.
- Risk / tradeoff:
  - Too much detail recreates panel sprawl. Keep it a strip/badge/read model.

### 2차. Replay Semantics Cleanup

- Purpose: Make History Replay and Saved Portfolio Replay consistently read as reproducibility, not validation.
- Screens / code / docs scope:
  - Backtest Run History, saved replay, Candidate Library support/archive wording.
  - Existing JSONL read paths only.
- What not to do:
  - No JSONL rewrite.
  - No candidate promotion.
  - No support expansion for quarterly/Risk-On without separate approval.
- Completion condition:
  - History and saved setup labels agree with the 1차 handoff contract.
  - Quarterly and Risk-On remain deferred/prototype/research where appropriate.
- Connection to next phase:
  - Reduces confusion before any ETF or strict annual validation bridge work.
- Needed verification:
  - Replay/load parity tests where available.
  - Browser QA for history/saved surfaces.
- Risk / tradeoff:
  - Touches multiple UI surfaces. Keep copy and read model changes narrow.

### 3차. ETF Evidence Expansion Sequence

- Purpose: Use 5A/5B runtime metadata to build durable evidence for GRS, Risk Parity, and Dual Momentum without adding default panels.
- Screens / code / docs scope:
  - Strategy reports / backtest reports / optional hidden reference read model.
  - Runtime smoke only if approved.
- What not to do:
  - No current-candidate registry write by default.
  - No provider direct fetch from UI.
  - No new ETF strategy.
- Completion condition:
  - Each target ETF strategy has current anchor, near miss, not-ready reason, required evidence, and provider/cost/benchmark caveats.
- Connection to next phase:
  - Prepares an evidence-backed Practical Validation source discussion.
- Needed verification:
  - Source/report verification.
  - Optional focused runtime smoke.
- Risk / tradeoff:
  - ETF evidence can overstate holdings history. Follow Koyfin-style caveat discipline.

### 4차. Strict Annual + ETF Sleeve Validation Handoff

- Purpose: Let the first evidence-mature group move toward Practical Validation as a portfolio construction candidate, not a winner-only ranking.
- Screens / code / docs scope:
  - Backtest mix handoff, Practical Validation source traits, component role/weight evidence.
- What not to do:
  - No Final Review auto-selection.
  - No monitoring scenario creation.
  - No live approval.
- Completion condition:
  - Strict annual core + GTAA/EW sleeve source clearly states role, weight, known weakness, and validation evidence required.
- Connection to next phase:
  - Opens a user-approved validation bridge if evidence is sufficient.
- Needed verification:
  - Service tests for source traits and role metadata.
  - Browser QA through Backtest -> Practical Validation.
- Risk / tradeoff:
  - Can sound like portfolio advice if copy is careless. Keep it candidate-source and validation-first.

### 5차. Prototype / Research Lane Decisions

- Purpose: Decide separately whether to mature strict quarterly prototypes or design Risk-On governance.
- Screens / code / docs scope:
  - Either quarterly PIT/replay maturation or Risk-On daily swing governance design, not both by default.
- What not to do:
  - No quarterly label removal until gates pass.
  - No Risk-On monitoring signal.
  - No generated artifact promotion into registries without compact evidence policy.
- Completion condition:
  - User chooses one path and approves a dedicated task.
- Connection to next phase:
  - Only after 1차~4차 make core Backtest handoff stable.
- Needed verification:
  - Depends on chosen path; likely TDD before UI.
- Risk / tradeoff:
  - Highest over-promotion risk. Good performance is not evidence maturity.

## What To Build First

If the user approves, start with 1차 only:

`Backtest Result Handoff Contract + compact strategy maturity label`.

Why:

- It directly addresses the product-direction mistake.
- It preserves 4C.
- It leverages 5A/5B.
- It creates the language needed before replay, ETF expansion, quarterly maturation, or Risk-On governance.

## What To Defer

- 5C Strict Quarterly Prototype formalization.
- Risk-On Momentum Practical Validation / Final Review / Monitoring integration.
- New Backtest Analysis panels.
- Direct provider/FRED fetching.
- Roadmap/phase/task plan updates before user approval.
- Registry / saved JSONL / generated artifact cleanup.
- Live trading, broker order, account sync, auto rebalance.

## Required Decisions

Before the next implementation session, the user should approve or reject:

1. Is 1차 `Backtest Result Handoff Contract` the next build scope?
2. Should maturity labels appear on strategy selection, result summaries, or only result summaries?
3. Should 3A~4B references stay hidden in Backtest Analysis for now, or should a later cleanup move them toward Reference / reports?
4. After 1차, which Next track should come first: replay semantics, ETF evidence expansion, or strict annual + ETF sleeve validation handoff?
5. Should strict quarterly prototype and Risk-On governance remain out of the next cycle?

## Proposed Next Handoff

If approved, the next session should start with:

```text
Read .aiworkspace/note/finance/researches/active/backtest-direction-reset-research-20260612/RECOMMENDATION.md.
Open a 1차 task for Backtest Result Handoff Contract only.
Do not change Practical Validation, Final Review, Monitoring, registry/saved JSONL, or docs/ROADMAP.md without separate approval.
```

## Evidence Summary

- Local audit supports keeping 4C and 5A/5B.
- Benchmark research supports separating run result, diagnostics, history/report, validation, and monitoring.
- Strategy maturity model supports strict annual + GTAA/EW as the first candidate-ready group, ETF 5A/5B strategies as evidence-expansion next, Risk-On as research lane, and quarterly as prototype.

## Risks And Unknowns

- Portfolio Visualizer evidence is limited by public access / 403 in direct terminal fetch; use as high-level pattern only.
- Current branch has pre-existing dirty files outside this research bundle; this recommendation does not rely on editing them.
- Any future UI change needs Browser QA because the main product risk is screen weight, not just code correctness.

## Final Recommendation

Close this research pass as a reset, not as approval to build. The next user decision should be whether to open a 1차 implementation task for the compact handoff contract only. Everything else remains Next / Later / Parking Lot until explicitly approved.
