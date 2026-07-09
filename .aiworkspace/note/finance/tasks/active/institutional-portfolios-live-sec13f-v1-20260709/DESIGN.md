# Institutional Portfolios Live SEC 13F V1 Design

## Source Boundary

- Primary source: SEC official Form 13F data set ZIP.
- Secondary helper: EDGAR submissions API for source filing links / per-CIK discovery later.
- Benchmark only: Dataroma, WhaleWisdom, Fintel. Scraping is not assumed; paid / licensed APIs are optional future provider adapters.

## Data Flow

```text
SEC Form 13F official dataset ZIP
  -> finance/data/institutional_13f.py
  -> finance_meta.institutional_13f_manager / filing / holding / mapping / refresh status
  -> finance/loaders/institutional_13f.py
  -> app/services/institutional_portfolios.py
  -> app/web/institutional_portfolios.py
  -> React workbench
```

## UI Flow

- Manager rail / watchlist first.
- Hero shows manager, report period, filing date, total reported 13F value, holding count, source freshness.
- Allocation, top holdings, reported change board, sector exposure, holdings detail, source links, and reverse lookup are primary.
- Manual refresh is a secondary action / drawer, not the page protagonist.
- Caveats remain visible: 13F is delayed, incomplete for shorts / cash / derivatives / hedge structure, and not a trading signal.

## Schema Direction

- Keep existing source tables as ledger tables.
- Add refresh status as operational state for the product page.
- Add watchlist seed contract for manager rail.
- Keep holding deltas as a service-level derived view for this iteration unless repeated query cost requires persistence later.

