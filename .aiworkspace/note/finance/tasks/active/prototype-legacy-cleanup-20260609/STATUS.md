# Prototype Legacy Cleanup / Removal Status

Status: Complete
Last Updated: 2026-06-12

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
- 5C import graph audit classified the remaining Candidate Review / Portfolio Proposal UI/helper modules as deletable after extracting current handoff behavior.
- Added current Practical Validation handoff helpers in `app/services/backtest_practical_validation_source.py` and `app/web/backtest_practical_validation_handoff.py`.
- Removed current Backtest result/history/compare/final-review dependencies on legacy Candidate Review / Portfolio Proposal helpers.
- Deleted legacy Candidate Review / Portfolio Proposal UI/helper modules and removed unused Overview candidate/proposal snapshot helpers.
- Preserved registry / saved JSONL and runtime archive compatibility helpers without rewrite.

## Current Step

5C 4차 docs sync / verification / Browser QA completed and committed as `7e3c9c3a`.

## Next Action

- No immediate 5C action remains.
- Leave generated screenshot, run history, saved JSONL, and `.DS_Store` unstaged.
- Future cleanup such as `final_selected_portfolio_dashboard.py` rename or runtime registry helper deletion needs a separate archive / recovery compatibility audit.
