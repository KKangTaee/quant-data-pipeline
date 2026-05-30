# Status

- 2026-05-30: Task opened after user approved the Market Movers second-pass guideline.
- 2026-05-30: Implemented service read-model fields for volume, dollar volume, previous return, and momentum delta.
- 2026-05-30: Implemented selected-coverage browser auto refresh job routing for S&P 500 / Top1000 / Top2000.
- 2026-05-30: Implemented Return Rank / Volume Rank / Sector Pulse chart tabs with sector-colored positive bars and negative danger bars.
- 2026-05-30: Updated runbook, roadmap, root handoff logs, and service contract tests.
- 2026-05-30: Reworked Volume Rank to use a dedicated `volume_rows` read model: daily uses current-day volume / dollar volume, while weekly / monthly / yearly expose average daily and total period volume metrics.
- 2026-05-30: Reduced non-daily Top1000 / Top2000 render overhead by limiting latest-price diagnostics to missing rows and forcing the symbol / timeframe / date index for point and volume reads.
