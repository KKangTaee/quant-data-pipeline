# Risks

- BLS `.ics` field formatting may drift. Parser tests should cover folded lines, date-only and date-time `DTSTART`, and the target release titles.
- Manual import depends on the user downloading the official file in a browser when backend fetch is blocked.
- No fake sample event was written to the live DB during verification; end-to-end DB write should be confirmed with a real BLS `.ics` file when available.
