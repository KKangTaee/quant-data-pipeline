# Notes

- This task is intentionally a DB read model, not a data collection workflow.
- Symbol freshness should include both replay universe tickers and benchmark tickers because benchmark spread is part of selected recheck evidence.
- Status policy: lag <= 2 calendar days is `PASS`, lag <= 5 is `WATCH`, larger lag is `STALE`, absent rows are `MISSING`.
