# Finance Data Map

Status: Active
Last Verified: 2026-05-12

## Purpose

이 폴더는 finance 프로젝트의 데이터 흐름, DB 구조, table 의미, 데이터 품질 / PIT 주의사항을 관리한다.

상위 제품 / 코드 지도는 `docs/PROJECT_MAP.md`에 두고, DB와 데이터 의미의 상세 기준은 이 폴더에서 관리한다.

## Read Order

| 상황 | 먼저 볼 문서 |
|---|---|
| 데이터가 어디서 와서 어디로 저장되는지 확인 | [DATA_FLOW_MAP.md](./DATA_FLOW_MAP.md) |
| DB와 table 목록을 빠르게 확인 | [DB_SCHEMA_MAP.md](./DB_SCHEMA_MAP.md) |
| table별 source / derived / shadow / provider snapshot 의미 확인 | [TABLE_SEMANTICS.md](./TABLE_SEMANTICS.md) |
| PIT, look-ahead, survivorship, stale data 위험 확인 | [DATA_QUALITY_AND_PIT_NOTES.md](./DATA_QUALITY_AND_PIT_NOTES.md) |

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
| `practical_validation_stress_windows_v1.json` | Practical Validation static stress window reference data. JSON reference file이며 DB table은 아님 |

## JSONL Boundaries

| File / Folder | Meaning | Policy |
|---|---|---|
| `.aiworkspace/note/finance/registries/` | workflow decision / source registry | 보존 대상. 명시 요청 없이 재작성하지 않음 |
| `.aiworkspace/note/finance/saved/` | reusable saved portfolio setup | 보존 대상 |
| `.aiworkspace/note/finance/run_history/` | local run history | 장기 문서 아님. 보통 커밋하지 않음 |
| `.aiworkspace/note/finance/run_artifacts/` | local runtime artifact | 장기 문서 아님. 보통 커밋하지 않음 |

## Data Integrity Rules

- 백테스트와 validation에서는 point-in-time, look-ahead, survivorship risk를 항상 고려한다.
- provider field는 안정적이거나 완전하다고 가정하지 않는다.
- official row가 partial이면 DB bridge와 병합하되 source origin을 숨기지 않는다.
- Practical Validation JSONL에는 compact evidence와 reason만 저장하고, full provider raw data는 DB에 둔다.
- static stress window JSON은 투자 신호가 아니라 재현 가능한 검증 preset이다.

## Code Flow 문서와의 차이

- `docs/data/`는 데이터가 어떤 의미를 갖고 어디에 저장되는지 보는 data / DB 의미 문서다.
- `docs/architecture/`는 코드를 어떻게 따라가고 수정할지 보는 개발자 flow 문서다.

예를 들어 새 loader 함수를 고칠 때는 `docs/architecture/DATA_DB_PIPELINE_FLOW.md`를 먼저 보고, 그 loader가 읽는 table의 의미를 확인할 때는 이 폴더의 [TABLE_SEMANTICS.md](./TABLE_SEMANTICS.md)를 본다.

## 갱신해야 하는 경우

- 새 DB table / column이 추가될 때
- table의 source / derived / shadow / convenience 성격이 바뀔 때
- ingestion source가 바뀔 때
- loader가 source of truth를 바꿀 때
- PIT 기준, filing timing, period_end 의미가 바뀔 때
- provider coverage, stale data, survivorship risk 해석이 바뀔 때

## 갱신하지 않아도 되는 경우

- 단순 UI 문구 변경
- 일회성 backtest 결과
- phase status 변경
- 코드 내부 리팩터링이 table 의미나 데이터 흐름을 바꾸지 않는 경우

## Source Of Truth

schema의 실제 정의는 코드가 기준이다.

- `finance/data/db/schema.py`

이 폴더는 schema SQL을 그대로 복제하는 곳이 아니라, 사람과 agent가 데이터 의미를 빠르게 이해하도록 돕는 해석 지도다.
