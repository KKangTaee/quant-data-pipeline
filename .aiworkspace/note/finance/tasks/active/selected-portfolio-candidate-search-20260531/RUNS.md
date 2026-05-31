# Runs

| Time | Command / Check | Outcome |
|---|---|---|
| 2026-05-31 | `git status --short` | Existing dirty tree observed before this task: run history, `.DS_Store`, Practical Validation / Final Review QA screenshots, and untracked V2 source/result registries. |
| 2026-05-31 | Registry line counts | `PORTFOLIO_SELECTION_SOURCES=1`, `PRACTICAL_VALIDATION_RESULTS=2`, `FINAL_PORTFOLIO_SELECTION_DECISIONS=2`, `SAVED_PORTFOLIOS=2`. |
| 2026-05-31 | Runtime V2 registry / dashboard check | `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl` is the dashboard source. It currently has 0 rows; dashboard read model returns 0 selected rows and `HANDOFF_NO_FINAL_DECISION`. |
| 2026-05-31 | Existing Practical Validation rows selected-route dry run | Latest GTAA Clean-6 row is Final Review eligible and evidence route is `READY_FOR_FINAL_DECISION`, but investability packet is `INVESTABILITY_PACKET_BLOCKED` with `select_allowed=False`; older GTAA row is blocked for Final Review. No save. |
| 2026-05-31 | Saved portfolio replay dry run | Both saved mixes replayed without registry writes. `EW Growth/Commodity 30 + GTAA Clean-6 70` actual replay `PASS` / period coverage `PASS`; `GTAA SPY Low-MDD 60 + EW Growth/Sector/Gold 40` actual replay `REVIEW` / period coverage `REVIEW`. Both selected-route gates blocked. |
| 2026-05-31 | Legacy Final Review option scan | 13 options checked: 1 eligible Practical Validation result, 8 current candidates, 4 portfolio proposals. `selected_route_pass_count=0`. Dominant blockers: Risk Contribution, Backtest Realism, Construction Risk, Data Coverage, Provider / Look-through, Validation Efficacy. |
| 2026-05-31 | Safety boundary | No live approval, order instruction, auto rebalance, broker/account connection, registry rewrite, or final selection append was executed. |
