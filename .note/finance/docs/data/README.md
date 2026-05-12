# Finance Data Map

Status: Active
Last Verified: 2026-05-12

## Database Groups

| DB | Role |
|---|---|
| `finance_meta` | universe, asset profile, ETF provider snapshot, macro context |
| `finance_price` | OHLCV / dividend / split price history |
| `finance_fundamental` | fundamentals, financial statements, derived factors |

## Key Tables

| Table | Meaning |
|---|---|
| `nyse_stock` | NYSE stock listing master |
| `nyse_etf` | NYSE ETF listing master |
| `nyse_asset_profile` | stock / ETF profile and bridge metadata |
| `nyse_price_history` | OHLCV price ledger |
| `etf_provider_source_map` | ETF별 issuer endpoint / parser mapping cache |
| `etf_operability_snapshot` | ETF 비용, 규모, 유동성, spread, NAV 관련 snapshot |
| `etf_holdings_snapshot` | ETF holdings row snapshot |
| `etf_exposure_snapshot` | holdings 또는 provider aggregate 기반 exposure summary |
| `macro_series_observation` | FRED VIX / yield curve / credit spread observation |

## JSONL Boundaries

| File / Folder | Meaning | Policy |
|---|---|---|
| `.note/finance/registries/` | workflow decision / source registry | 보존 대상. 명시 요청 없이 재작성하지 않음 |
| `.note/finance/saved/` | reusable saved portfolio setup | 보존 대상 |
| `.note/finance/run_history/` | local run history | 장기 문서 아님. 보통 커밋하지 않음 |
| `.note/finance/run_artifacts/` | local runtime artifact | 장기 문서 아님. 보통 커밋하지 않음 |

## Data Integrity Rules

- 백테스트와 validation에서는 point-in-time, look-ahead, survivorship risk를 항상 고려한다.
- provider field는 안정적이거나 완전하다고 가정하지 않는다.
- official row가 partial이면 DB bridge와 병합하되 source origin을 숨기지 않는다.
- Practical Validation JSONL에는 compact evidence와 reason만 저장하고, full provider raw data는 DB에 둔다.
