# Overview Market Movers Modes V2 Risks

- Relative volume depends on stored 1d EOD volume history. Sparse or missing history correctly produces `INSUFFICIENT_DATA`, but this can make the mode empty for some coverages.
- Weekly/monthly relative volume uses average daily volume for the selected period against the prior 10 stored EOD volume rows. It is a scan context metric, not a statistically normalized signal.
- Sector Leaders in 2차 is a compact mode view. Broader sector breadth/heatmap interpretation remains 4차.
- NASDAQ coverage may still be empty or stale depending on local DB state. 5차 will make trust/data quality language more systematic.
- `pytest` is not installed in this local environment, so the exact requested pytest command could not run. Equivalent `unittest -k` fallback passed for the same related contracts.
