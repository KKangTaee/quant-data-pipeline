# Risks

- Free provider endpoints can rate-limit or omit quote rows, especially for Top1000 / Top2000. Use `safe` profile first if provider pressure becomes visible.
- US market-hours guard does not yet include a full US exchange holiday calendar; holiday runs are skipped only if outside weekday market hours.
- This task adds the CLI runner but does not install a user-level launchd / cron schedule automatically.
- `market_data_issue` has no automatic resolve lifecycle yet; occurrence counts show repeated evidence, not a current official security status.
