# Overview Structure Split V2-V5 Risks

- Legacy helper internals remain large. The safe strategy is to move active ownership boundaries first, then retire legacy helpers only when tests no longer depend on them.
- After V2, tab modules own orchestration but still call many `legacy_dashboard.py` helpers. V3/V4 should reduce those dependencies through component and service import surfaces before deleting helper code.
