# Notes

Last Updated: 2026-07-20

## Confirmed Facts

- `_filter_sector`는 현재 raw label exact match를 사용한다.
- `load_market_mover_sector_options`는 raw provider label을 노출한다.
- 기존 `ticker_leader_rows`는 positive return leader이며 market-cap Top 3가 아니다.
- `nyse_asset_profile`에는 `kind`, `quote_type`, `sector`, `industry`, `market_cap`이 있다.
- `nyse_fundamentals_statement`에는 revenue, operating income, net income, balance-sheet fields가 있지만 diluted EPS column은 없다.
- PIT `nyse_financial_statement_values`와 turnaround quarterly-series logic에는 reported diluted EPS concept resolution이 있다.
- 기존 research snapshot은 latest price를 모든 financial trend row에 적용해 historical PER를 만든다.

## Plan Choice

표준 statement shadow에 synthetic diluted EPS column을 억지로 추가하지 않는다. current TTM valuation만 existing PIT filing ledger를 통해 계산하고, coverage가 없으면 unavailable로 둔다.
