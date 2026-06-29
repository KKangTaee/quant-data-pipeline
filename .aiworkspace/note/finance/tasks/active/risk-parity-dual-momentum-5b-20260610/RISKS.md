# Risk Parity / Dual Momentum 5B Risks

## Open Risks

- Dual Momentum now keeps trend-rejected top-N slots in cash proxy instead of reweighting survivors to 100%; this is an intentional contract hardening and can change historical Dual Momentum performance.
- Selection History must reuse existing tabs and avoid creating another Backtest Analysis panel.
- Runtime meta summaries must stay compact and must not fetch provider / FRED data or write registries.
- `run_history`, `registries`, `saved`, and generated artifacts must remain unstaged unless explicitly requested.

## Remaining Follow-Up

- Practical Validation / Final Review / Monitoring should keep treating these diagnostics as source evidence only until a separate approved task changes downstream gate behavior.
