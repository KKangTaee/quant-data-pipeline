# Prototype Legacy Cleanup / Removal Status

Status: Complete
Last Updated: 2026-06-09

## Progress

- Read current docs and research handoff: `INDEX`, `ROADMAP`, `PROJECT_MAP`, `BACKTEST_UI_FLOW`, `PORTFOLIO_SELECTION_FLOW`, `SYSTEM_BOUNDARIES`, `SCRIPT_STRUCTURE_MAP`, recommendation, feature candidates.
- Confirmed current workflow target is `Backtest Analysis -> Practical Validation -> Final Review -> Operations > Portfolio Monitoring`.
- Found legacy primary exposure in `app/web/pages/backtest.py` direct Candidate Review / Portfolio Proposal dispatch and route target acceptance.
- Found Overview primary `Candidate Ops` tab still loads old current/pre-live/proposal registries and points users toward Candidate Review / Portfolio Proposal.
- Added focused service-contract regression tests for legacy route removal, Overview primary tab cleanup, and Archive: Backtest Runs Practical Validation handoff.
- Removed Candidate Review / Portfolio Proposal from Backtest primary route targets and page-shell direct dispatch.
- Removed Overview primary `Candidate Ops` tab and stopped default Overview render from loading the old candidate/proposal snapshot.
- Changed Archive: Backtest Runs handoff from legacy candidate draft queue to current Practical Validation source handoff.
- Updated Portfolio Monitoring copy in Final Review / selected portfolio read models and durable flow / architecture / glossary docs.

## Current Step

3차 docs sync / verification / Browser QA completed.

## Next Action

- Commit the coherent cleanup unit.
- Leave generated screenshot, run history, saved JSONL, and `.DS_Store` unstaged.
