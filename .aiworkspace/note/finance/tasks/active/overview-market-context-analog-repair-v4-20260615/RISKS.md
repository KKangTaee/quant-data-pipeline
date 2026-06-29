# Risks

- `run_collect_ohlcv` still depends on the existing provider path and network / provider availability. V4 makes the repair action reachable; it does not guarantee provider success.
- CSV upload is not implemented in this pass. If provider collection remains insufficient, a separate upload/import flow can be designed.
- Historical analog remains sample-sensitive. Low sample counts, sector ETF proxy simplification, survivorship / PIT limits, and macro/event conditioning gaps are still visible caveats.
- The source confidence strip summarizes only the currently loaded source confidence model; it does not replace detailed Data Health investigation.
- Generated QA screenshots and Playwright artifacts are local artifacts and should not be staged unless explicitly requested.
