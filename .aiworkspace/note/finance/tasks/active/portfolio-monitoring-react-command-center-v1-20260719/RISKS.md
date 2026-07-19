# Portfolio Monitoring React Command Center V1 Risks

## Active Risks

1. Historical exposure coverage
   - ETF holdings and selected strategy target snapshots may be current/latest rather than full PIT history.
   - Mitigation: V1 current diagnosis labels coverage; probability publication waits for historical replay.

2. Corporate action data quality
   - Stored dividends/splits may be partial or corrected later.
   - Mitigation: adjusted-close cross-check and explicit `data_review` state.

3. Common basis date lag
   - One stale active item can move the whole group basis date backward.
   - Mitigation: show affected item and missing range; never mix dates silently.

4. Legacy import mismatch
   - Existing strategy slots can reference missing or legacy Final Review decisions.
   - Mitigation: non-destructive dry run, provenance, blocked cutover for missing references.

5. Monolithic compatibility code
   - Existing Portfolio Monitoring runtime/read model is large and tightly coupled.
   - Mitigation: extract new package by contract; do not rewrite all legacy behavior in one change.

6. Probability overstatement
   - Macro context can be mistaken for predicted portfolio loss.
   - Mitigation: suppress probability until OOS publication gate; show observation/coverage/confidence first.

## Not Blocked

- Current DB has stock/ETF universe and daily price loaders.
- Final Review monitoring candidates and selected strategy replay exist.
- Overview economic cycle and Futures Macro compact DB-backed payloads exist.
- React custom workbench pattern is established in the repository.
