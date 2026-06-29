# Runs

| Date | Command / Action | Result |
|---|---|---|
| 2026-06-29 | Read docs: `INDEX.md`, `ROADMAP.md`, `PROJECT_MAP.md`, `BACKTEST_RUNTIME_FLOW.md`, `BACKTEST_UI_FLOW.md`, `STRATEGY_IMPLEMENTATION_FLOW.md` | Confirmed Backtest runtime / UI / strategy boundaries. |
| 2026-06-29 | Search GTAA reports and preset code | Found prior `GTAA SPY Low-MDD Style Top-3` candidate and current preset registration. |
| 2026-06-29 | Existing candidate replay | `CAGR=19.4609%`, `MDD=-11.0297%`, SPY `13.3638%/-15.9042%`, but `promotion=production_candidate` at ADV20 because liquidity clean coverage was `88.10%`. |
| 2026-06-29 | Subagent limited sweep | Found stronger low-MDD candidates, but current pre-fix runtime lacked liquidity evidence and returned `hold` for all. |
| 2026-06-29 | Added failing tests for GTAA liquidity evidence and execution dispatch | RED: `gtaa3()` did not accept ADV filter and execution dispatch did not pass it. |
| 2026-06-29 | Implemented GTAA liquidity evidence path | Tests passed. |
| 2026-06-29 | Final representative replay | `GTAA SPY Low-MDD Style Top-2 ADV20`: `24.078108% / -9.990100%`, `promotion=real_money_candidate`, `deployment=small_capital_ready`. |
