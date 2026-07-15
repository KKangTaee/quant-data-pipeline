# Overview Market Context US Stock Freshness Refresh V1 Risks

Last Updated: 2026-07-15

## Open Risks

1. Provider market cap may expose collection time but not an authoritative market-cap basis date.
2. Holiday/early-close handling must not be duplicated or drift from existing backtest freshness semantics.
3. A single action must preserve successful profile/price writes when SEC identity remains missing.
4. Refresh must not imply that structural short listing or negative EPS becomes PER-ready.
5. Existing PER/turnaround legacy action contracts and S&P payload must not regress.
6. The UI must not add a run/job/row diagnostic panel in place of the requested workflow action.
