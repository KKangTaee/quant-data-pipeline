# Notes

- Backtest Realism Audit already exists as a read-only audit from `backtest-realism-hardening-v1`.
- The policy link should not create a new persistence layer. It only changes selected-route interpretation.
- `NEEDS_INPUT` and `BLOCKED` should block selected-route because missing transaction cost / turnover / liquidity evidence is not investment-ready.
- `REVIEW` should force hold / re-review before selection, not silently pass.
