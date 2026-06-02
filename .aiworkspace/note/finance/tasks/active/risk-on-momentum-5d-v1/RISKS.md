# Risk-On Momentum 5D V1 Risks

## Residual Risks

- Full active-stock universe beyond Top2000 is intentionally deferred because daily scanner runtime can be heavy.
- Futures macro history starts around 2021-06-01 in the local DB; earlier backtest dates will run with macro filter unavailable unless macro filtering is disabled or the date has enough futures history.
- Financial-statement coverage is narrower than price coverage, so the financial hard-exclude must distinguish true risk evidence from missing statement coverage.
- Compare mode can execute the strategy, but detailed strategy-specific compare controls are intentionally not expanded in V1.
- Practical Validation / Candidate Library replay support for this stock swing strategy remains a follow-up if the strategy is promoted beyond research backtest use.

## Closed QA Risks

- Browser QA initially found that placing `Universe Mode` inside `st.form` prevented the Manual ticker input from rerendering immediately. The control is now outside the form, and Browser QA confirmed immediate Manual input rendering.
