# Portfolio Monitoring React Command Center V1 Risks

## Residual Risks

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

7. Current actual macro coverage
   - Economic cycle and six asset pathways are available, but a compatible persisted Futures Macro snapshot was missing in closeout smoke.
   - Mitigation: UI remains `LIMITED`/observation-only and does not fabricate probability or direction.

8. Production content QA boundary
   - Production schema contains only the default empty group; no synthetic stock/ETF/strategy was inserted into user data.
   - Mitigation: direct/ETF/strategy, staggered start/end cash, corporate action, stale common basis and calibration cases are covered by deterministic fixtures; populated actual QA begins when the user registers real items.

## Closed Gates

- Current DB has stock/ETF universe and daily price loaders.
- Final Review monitoring candidates and selected strategy replay exist.
- Overview economic cycle and Futures Macro compact DB-backed payloads exist.
- React custom workbench pattern is established in the repository.
- Production five-table migration and exactly-one default group are verified.
- Legacy source checksum is preserved; apply idempotency is verified only in isolated QA DB.
- 1440/760/420 Browser QA and full focused/linked regressions pass.
