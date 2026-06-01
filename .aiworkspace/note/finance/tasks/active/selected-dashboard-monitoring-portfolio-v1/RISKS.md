# Risks

- Alternative comparison can become expensive if every selected candidate replay is run automatically; first pass should keep comparison session-triggered and scoped to selected strategies in the current dashboard portfolio.
- Some Final Review selected rows may not have replay contracts, so scenario rows must show `NEEDS_INPUT` rather than pass silently.
- Soft delete keeps auditability but requires UI filters to hide deleted portfolios by default.
- Current worktree has no fresh selected Final Decision V2 row, so Browser QA could verify the new portfolio creation surface and empty-state path only. Strategy add / scenario / transition comparison paths are covered by service contracts and existing recheck contracts, but should be manually rechecked once a selected row exists.
