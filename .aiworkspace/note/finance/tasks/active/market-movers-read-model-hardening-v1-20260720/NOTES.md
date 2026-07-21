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

## Implemented Contracts

- sector option/filter/grouping은 canonical 11-sector와 `Unknown`을 공유한다.
- `market_movers_collection_readiness_v1`은 return/volume/market-cap 분모를 분리하고 `COMPLETE/PARTIAL/BLOCKED`와 결과 공개 여부를 결정한다.
- `market_movers_group_flow_v1`은 current breadth/relative-strength/concentration 상태와 market-cap bellwether Top 3를 return leader와 분리한다.
- industry는 stable display key와 minimum group size를 사용하며 historical taxonomy로 표방하지 않는다.
- `market_mover_research_snapshot_v2`는 annual/quarterly factor series와 current valuation을 분리한다. historical PER와 net-income/shares synthetic EPS는 제거했다.
- `market_movers_decision_payload_v1`은 DataFrame/Timestamp/numpy scalar를 JSON-safe 값으로 변환하고 sector/industry × daily/weekly/monthly를 고정한다.

## Commits

- `df4fcab2` canonical sector
- `81e01fe8` collection readiness
- `037b9813` group flow / bellwethers
- `a9f2c17b` financial factors / PER correction
- `80cf4914` decision payload
- `4841c599` JSON scalar fallback hardening
