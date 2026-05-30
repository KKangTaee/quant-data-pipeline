# Notes

- This is the third and final high-level hardening axis after Events / Earnings quality and Events calendar UX.
- Keep refresh manual; the UI should make stale state visible and reload DB read models on a timer, not auto-collect provider data.
- `Status Check` now means DB read-model reload for the selected daily coverage. It does not call the provider collector.
- `Update Daily Snapshot` remains the only Overview Market Movers control that collects provider quotes.
- The refresh bar lives inside the timed fragment so stale / due indicators can change without a manual full-page reload.
