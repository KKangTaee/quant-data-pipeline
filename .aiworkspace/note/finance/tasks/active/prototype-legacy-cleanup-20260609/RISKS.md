# Prototype Legacy Cleanup / Removal Risks

## Open Risks

- Historical task / phase logs still mention Candidate Review / Portfolio Proposal. Current-flow docs were cleaned, but old work records should not be rewritten wholesale.
- Remaining runtime helpers for candidate/proposal/paper registries are compatibility surfaces only. Future current workflow changes should not re-import deleted UI/helper modules or present these registries as required stages.
- Overview helper cleanup removed legacy candidate/proposal snapshot helpers; verification should continue to include Overview market/context snapshot imports when related work touches this file.
- Candidate Library archive still reads old current/pre-live candidate records. That is acceptable only while clearly labeled Archive / Recovery.

## Deferred

- Renaming `final_selected_portfolio_dashboard.py`.
- Moving legacy registries to a different path.
- Deleting `app/runtime/portfolio_proposal.py`, `app/runtime/paper_portfolio_ledger.py`, or old candidate registry helpers. These need a separate archive / recovery compatibility audit.
