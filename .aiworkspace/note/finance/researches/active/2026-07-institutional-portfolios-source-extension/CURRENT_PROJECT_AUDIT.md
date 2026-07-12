# Institutional Portfolios Source Extension Audit

Status: Active
Last checked: 2026-07-12

## Current Local Findings

- OHLCV chart data is DB-backed, not fetched directly by the Institutional Portfolios React UI.
- Read path: `app/services/institutional_portfolios.py` calls `finance.loaders.price.load_price_history`, which reads `finance_price.nyse_price_history` through `finance.data.data.load_ohlcv_many_mysql`.
- Collection path: the UI event `collect_price_history` is handled in `app/web/institutional_portfolios.py` and calls `app.jobs.ingestion_jobs.run_collect_ohlcv`, which delegates to `finance.data.data.store_ohlcv_to_mysql`.
- Provider for the existing OHLCV collector is `yfinance`, stored into `finance_price.nyse_price_history`.
- Local DB check on 2026-07-12: `nyse_price_history` had 20,324,601 daily rows across 12,019 symbols, with latest date 2026-07-10.
- Local SEC 13F DB is populated: `institutional_13f_refresh_status` latest report period is 2026-03-31, with 3,845,308 rows written in the latest dataset refresh.

## Manager / Guru Split

- There are not two separate source models for "institutional portfolio" and "guru portfolio".
- All portfolios are SEC Form 13F filers in `finance_meta.institutional_13f_manager`, `institutional_13f_filing`, and `institutional_13f_holding`.
- "Guru" is currently a curated display/watchlist layer on top of the same manager table.
- The hardcoded rail only seeds Berkshire Hathaway, Pershing Square, Appaloosa, and Baupost.
- `institutional_13f_manager_watchlist` exists but currently has zero local rows, and the active loader searches only `manager_name` / `CIK`.

## Coverage Issues Found

- Duquesne Family Office LLC exists locally as CIK `0001536411`, latest report period 2026-03-31, but is not in the curated rail.
- Search by investor name such as "Druckenmiller" will not match unless an alias/watchlist layer maps it to `Duquesne Family Office LLC`.
- Latest manager holding rows with mapped price coverage were low in the local DB:
  - Berkshire Hathaway: 102 holdings, 43 mapped to price rows after report period.
  - Pershing Square: 11 holdings, 4 mapped.
  - Appaloosa: 31 holdings, 13 mapped.
  - Baupost: 22 holdings, 5 mapped.
  - Duquesne: 73 holdings, 19 mapped.
- CUSIP-symbol mapping quality needs hardening. Some rows show multiple or incorrect symbols for the same CUSIP because the current enrichment uses asset-profile issuer-name matching rather than a true security master.

## Implication

"가격 데이터 없음" usually means the selected 13F holding did not resolve to a safe ticker with at least two stored OHLCV rows after the report period. It does not mean the 13F holding itself is absent.
