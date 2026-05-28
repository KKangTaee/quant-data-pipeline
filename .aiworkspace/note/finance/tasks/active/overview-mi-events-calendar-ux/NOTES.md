# Notes

- This is the second high-level hardening axis after earnings data quality.
- Keep the screen operational and compact; avoid turning Overview into a marketing-style page.
- `Importance` is a deterministic display label: FOMC / Macro = High, Earnings = Medium, unknown event families = Low.
- `Focus=Needs Review` is driven by `Quality Action != No action`, so source / validation work remains separate from market impact interpretation.
- The UI keeps DB-first behavior: all refresh buttons still call job wrappers, and Events rendering only reads stored rows.
