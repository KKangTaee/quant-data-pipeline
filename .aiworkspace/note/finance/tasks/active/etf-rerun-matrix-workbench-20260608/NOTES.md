# ETF Rerun Matrix Workbench 4B Notes

## Design Notes

- 4A current-anchor workbench reads existing artifacts only; 4B adds optional matrix execution but keeps the output session-local.
- Runtime functions already exist for the three ETF strategies, so no strategy logic change is needed.
- Direct runtime calls are acceptable for session-only matrix execution as long as the UI does not append run history or create downstream workflow artifacts.
