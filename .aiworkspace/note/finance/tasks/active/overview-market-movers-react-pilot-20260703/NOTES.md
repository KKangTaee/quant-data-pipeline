# Notes

## Phase 0 Contract

- `build_market_movers_react_workbench_payload` packages the existing unified summary model, current controls, and action descriptors into a JSON-serializable payload for the future React component.
- `market_movers_react_action_plan` maps React action ids to existing Python handler names and required parameters. It is intentionally a plan layer first; execution remains in later phases.
- Daily actions differ from EOD period actions because Daily uses quote snapshots while Weekly / Monthly / Yearly use EOD price history.
