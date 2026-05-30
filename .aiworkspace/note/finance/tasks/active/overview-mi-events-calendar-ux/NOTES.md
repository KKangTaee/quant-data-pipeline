# Notes

- This is the second high-level hardening axis after earnings data quality.
- Keep the screen operational and compact; avoid turning Overview into a marketing-style page.
- `Importance` is a deterministic display label: FOMC / Macro = High, Earnings = Medium, unknown event families = Low.
- `Focus=Needs Review` is driven by `Quality Action != No action`, so source / validation work remains separate from market impact interpretation.
- The UI keeps DB-first behavior: all refresh buttons still call job wrappers, and Events rendering only reads stored rows.
- The Calendar tab now starts with a true month grid, but keeps the existing stacked count chart and date-group list below it for dense scanning.
- The grid intentionally summarizes each day to the first three events plus a `+N more` marker; the detailed rows remain in the list and Table tab.
