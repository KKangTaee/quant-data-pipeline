# Notes

- BLS schedule pages are official sources but can reject automated requests. The collector should surface provider blocking as a failed job instead of silently writing stale data.
- BEA full release schedule is readable as an HTML table and includes national GDP rows.
- This task should not introduce a new event table; the existing market event calendar schema already has enough metadata.
- Macro rows use `MACRO_CPI`, `MACRO_PPI`, `MACRO_EMPLOYMENT`, and `MACRO_GDP` event types. Overview's `Macro` filter maps to the `MACRO_%` prefix.
- `raw_payload_json` normalization now converts pandas / JSON `NaN` values to `null` before MySQL JSON writes.
- Data Health marks Macro Calendar `Due` when only a subset of the four macro event families is present.
