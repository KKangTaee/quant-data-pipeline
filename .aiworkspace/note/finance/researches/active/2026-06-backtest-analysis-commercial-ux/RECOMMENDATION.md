# Recommendation

Status: Active
Last Updated: 2026-06-29 KST

## Recommended Direction

Backtest Analysis should be rebuilt around a compact commercial workbench:

```text
1. Choose and run a strategy or mix
2. Read a summary-first result
3. Send a supported candidate source to Practical Validation
4. Keep deep evidence, reference, and raw diagnostics out of the default path
```

This is a correction to the earlier strategy-panel-heavy direction.
The useful information from 3A~5B should be preserved, but not as default Backtest Analysis panels.

## Immediate Next Build

Approve a narrow 1차 implementation:

**Backtest Analysis cleanup + Latest Run summary-first handoff redesign**

This includes:

- remove `Backtest 사용 안내` from the top and replace it with a compact stage/action header.
- remove `Reference help - Backtest > Backtest Analysis` from Backtest Analysis.
- remove or relocate `전략 개발 참고` panels from the default Backtest Analysis render path.
- simplify Latest Backtest Run into one overview and detail tabs.
- replace Candidate Readiness score with Validation Handoff Eligibility.

This does not include:

- Practical Validation module redesign.
- Final Review / Monitoring behavior change.
- registry / saved JSONL rewrite.
- strategy logic rewrite.
- direct provider/FRED fetching.
- live approval, broker order, auto rebalance.

## Tentative Development Roadmap

### 1차. Backtest Analysis Default Surface Cleanup

- Purpose: remove manual/reference gravity from the first screen.
- Files likely touched:
  - `app/web/pages/backtest.py`
  - `app/web/backtest_analysis.py`
  - maybe `app/web/backtest_ui_components.py`
- User-visible change:
  - top usage guide disappears.
  - Backtest Analysis shows only Single Strategy / Portfolio Mix Builder and core candidate workflow.
  - Reference help no longer appears in Backtest Analysis.
- Completion condition:
  - first viewport is action-oriented.
  - no new guide expander is introduced.
  - 3-stage flow remains clear.
- Not in this phase:
  - Latest Run deep redesign.
  - strategy runtime changes.

### 2차. Latest Backtest Run Summary-First Redesign

- Purpose: compress result interpretation and make next action obvious.
- Files likely touched:
  - `app/web/backtest_result_display.py`
  - `app/services/backtest_result_read_model.py`
  - tests for read model / helper policy
- User-visible change:
  - one `Run Overview` section replaces A/B/C/D checkpoint strip and repeated badge/card layers.
  - Data Trust becomes compact status plus details disclosure.
  - performance summary and chart become the main body.
  - raw meta/result table stay in details.
- Completion condition:
  - user can answer: "Is this result usable, what is the data state, what next?"
- Not in this phase:
  - changing Practical Validation internals.

### 3차. Validation Handoff Eligibility Policy

- Purpose: separate "can send to validation" from "looks strong".
- Files likely touched:
  - `app/web/backtest_result_display.py`
  - `app/services/backtest_result_read_model.py` or a new Streamlit-free helper
  - possibly Practical Validation handoff service if source eligibility needs clearer contract
- User-visible change:
  - `검증으로 보낼 수 있음`
  - `보낼 수 있지만 확인 필요`
  - `아직 보낼 수 없음`
  - one reason and one next action.
- Hard blockers:
  - missing result bundle / empty rows
  - unsupported downstream path
  - missing source/replay contract
- Review signals:
  - price freshness warning
  - promotion hold / caution
  - provider / liquidity / benchmark caveats
- Completion condition:
  - warnings are not hidden, but they do not impersonate final approval gates.

### 4차. Strategy Maturity Chips

- Purpose: keep strategy maturity visible without reopening strategy inventory panels.
- Files likely touched:
  - `app/services/backtest_strategy_catalog.py` or a focused maturity service
  - `app/web/backtest_single_strategy.py`
  - `app/web/backtest_result_display.py`
- User-visible change:
  - strategy selector/result overview shows compact label:
    - `후보 source`
    - `근거 보강 필요`
    - `Research lane`
    - `Prototype`
    - `Baseline / sleeve`
- Completion condition:
  - quarterly and Risk-On are unmistakably not standard downstream-ready.

### 5차. Portfolio Mix Builder Commercial Workbench

- Purpose: improve the other half of Backtest Analysis after Single Strategy/result flow is stable.
- Files likely touched:
  - `app/web/backtest_compare.py`
  - `app/web/backtest_compare_components.py`
  - compare services
- User-visible change:
  - model-portfolio-like component/weight/result/handoff flow.
  - less raw table-first display.
- Completion condition:
  - mix candidate creation is understandable without reading a guide.

### 6차. Strategy Runtime / Contract Audit

- Purpose: verify each strategy's execution path and metadata contract before deeper strategy improvements.
- Files likely touched:
  - tests
  - strategy/runtime docs or research notes
  - maybe runtime helpers if audit finds bug
- User-visible change:
  - not necessarily UI; confidence and future safety.
- Completion condition:
  - strategy matrix says which strategies are executable, replayable, validation-compatible, and still prototype/research.

## What To Build First

Build 1차 only in the next implementation session.

Reason:

- It directly addresses the user's most visible complaint.
- It removes the guide/reference anti-pattern before redesigning deeper result logic.
- It has small blast radius and clear Browser QA.
- It prevents the implementation session from starting with a new panel.

## Required Decisions Before Implementation

1. Confirm that Backtest Analysis should remove in-screen Reference help entirely.
2. Confirm that `전략 개발 참고` panels should be removed from default Backtest Analysis and moved to Reference/research/report rather than polished in place.
3. Confirm that 1차 should not touch Practical Validation / Final Review / Monitoring.
4. Confirm whether implementation session should stop after 1차 or continue to 2차 if 1차 QA passes.

## Proposed Next Handoff

Use `DEVELOPMENT_GUIDELINES.md` to start a new implementation session.

Do not treat this research as implementation approval by itself.
The implementation request should explicitly say: "이번 요청은 개발 진행 승인이다" and name which phase is approved.
