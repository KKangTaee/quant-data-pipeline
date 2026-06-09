# Prototype Legacy Cleanup / Removal Risks

## Open Risks

- Candidate Review / Portfolio Proposal modules may still be imported indirectly by helper flows or old registry recovery paths. Deleting files now needs a broader import graph and registry consumer proof.
- Overview helper cleanup should avoid breaking market mover / sentiment / events data. This task removes the primary Candidate Ops tab and stops default legacy registry loads, but does not yet delete all unused helper functions.
- Candidate Library archive still reads old current/pre-live candidate records. That is acceptable only while clearly labeled Archive / Recovery.
- Historical task / phase logs still mention Candidate Review / Portfolio Proposal. Current-flow docs were cleaned, but old work records should not be rewritten wholesale.

## Deferred

- Physical deletion of old Candidate Review / Portfolio Proposal modules.
- Physical deletion of unused Overview candidate/proposal helper functions after import/use audit.
- Renaming `final_selected_portfolio_dashboard.py`.
- Moving legacy registries to a different path.
