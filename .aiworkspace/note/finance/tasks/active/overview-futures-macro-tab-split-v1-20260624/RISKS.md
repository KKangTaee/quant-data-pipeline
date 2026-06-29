# Overview Futures Macro Tab Split V1 Risks

## Open Risks

- Browser QA passed for the tab split. A small delay can still come from market movers / group leadership DB reads, but the measured default cockpit path is now about 0.522s locally.
- Existing tests heavily asserted old Market Context macro rows; focused contract updates now distinguish intentional light cockpit behavior from accidental regression.
- DB query rewrite changes read path only. Contract verifies query shape; local runtime should still be watched for index plan drift on large data.
