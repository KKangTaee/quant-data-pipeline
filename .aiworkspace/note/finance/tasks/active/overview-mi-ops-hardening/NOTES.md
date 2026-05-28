# Notes

- This task should prefer read-model hardening over schema work.
- Existing persisted source tables already contain enough freshness metadata for first-pass ops status.
- `WEB_APP_RUN_HISTORY.jsonl` is local/generated, so code may write to it but the file itself should not be committed.
- Overview refresh buttons now append their job result to local run history so the Data Health tab can show last success / issue / processed / failed metrics after the next user-triggered run.
- The ops read model has a fallback query for older `market_event_calendar` DBs that do not yet have `event_status`. This keeps FOMC / Earnings health visible while the local schema catches up.
- Data Health intentionally does not call yfinance, Nasdaq, Fed, or other remote providers. It reads stored DB freshness plus local run history only.
