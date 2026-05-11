# Practical Validation V2 Provider Connector Plan

## 목적

이 문서는 Practical Validation V2 P2에서 사용할 provider / DB / loader connector의 상세 설계 문서다.
상위 실행 계획은 `PRACTICAL_VALIDATION_V2_P2_CONNECTOR_AND_STRESS_PLAN.md`를 기준으로 하고,
이 문서는 특히 아래 세 영역을 다룬다.

1. Cost / Liquidity / ETF Operability connector
2. ETF holdings / sector look-through connector
3. Macro / Sentiment connector

## 쉽게 말하면

Practical Validation은 지금도 가격과 거래량으로 "대략 거래 가능한가"를 볼 수 있다.
하지만 최종 후보를 실전 후보로 검토하려면 ETF 자체의 비용, 규모, 스프레드, 보유종목,
시장 환경 데이터를 별도로 읽어야 한다.

이 문서는 그 데이터를 어디에 저장하고, 어떤 loader로 읽고,
Practical Validation 화면에서 어떻게 `PASS / REVIEW / BLOCKED / NOT_RUN` 근거로 바꿀지 정한다.

중요한 전제:

- 이 문서의 목적은 provider 수집 플랫폼 자체를 크게 만드는 것이 아니다.
- P2의 목적은 12개 Practical Validation 진단 중 아직 proxy / `NOT_RUN` / 설명 부족으로 남은 항목을 정상화하는 것이다.
- provider 수집, DB schema, loader는 그 정상화를 위한 구현 수단이다.

P2에서 provider connector가 직접 보강하는 진단은 아래와 같다.

| 검증 번호 | 검증 항목 | provider connector 역할 |
|---:|---|---|
| 2 | Asset Allocation Fit | holdings / exposure로 ticker proxy 보강 |
| 3 | Concentration / Overlap / Exposure | holdings overlap / top concentration 계산 |
| 5 | Regime / Macro Suitability | FRED macro snapshot 제공 |
| 6 | Sentiment / Risk-On-Off Overlay | VIX / spread / yield curve context 제공 |
| 9 | Leveraged / Inverse ETF Suitability | leverage / inverse / daily objective 상품 정보 제공 |
| 10 | Operability / Cost / Liquidity | expense ratio, AUM, spread, premium/discount, ADV 제공 |

Stress / sensitivity 해석은 이 provider context를 보조 evidence로 사용할 수 있지만,
전체 stress engine 자체는 이 문서가 아니라 P2 실행 계획 문서에서 다룬다.

## 현재 있는 데이터

| 데이터 | 위치 | 현재 쓸 수 있는 것 | 한계 |
|---|---|---|---|
| ETF / stock universe | `finance_meta.nyse_stock`, `finance_meta.nyse_etf` | symbol list | ETF 상세 비용 / holdings 없음 |
| Asset profile | `finance_meta.nyse_asset_profile` | `kind`, `quote_type`, `fund_family`, `total_assets`, `bid`, `ask`, `status` | 실제 coverage가 낮고 expense ratio / holdings / NAV / premium-discount 없음 |
| Price history | `finance_price.nyse_price_history` | OHLCV, volume, ADV / dollar volume proxy | spread, NAV, expense, holdings는 알 수 없음 |
| Runtime meta | `app/web/runtime/backtest.py` result meta | transaction cost bps, liquidity policy, ETF operability status | Practical Validation provider snapshot과 직접 결합되어 있지 않음 |
| Practical Validation result | `PRACTICAL_VALIDATION_RESULTS.jsonl` | compact evidence / diagnostics summary | full raw provider data 저장 위치가 아님 |

현재 DB 확인 기준:

- `nyse_price_history`는 넓은 가격 / 거래량 coverage를 갖는다.
- `nyse_asset_profile`은 ETF row는 많지만 `total_assets`, `bid`, `ask` coverage가 낮다.
- holdings, macro, sentiment 전용 table은 아직 없다.

## 문서 관리 원칙

P2 provider 개발 문서는 더 쪼개지지 않는다.
이 문서가 provider 데이터의 수집, 저장, 로딩, Practical Validation 연결 경계를 함께 관리한다.

| 문서 | 맡는 범위 |
|---|---|
| `PRACTICAL_VALIDATION_V2_P2_CONNECTOR_AND_STRESS_PLAN.md` | P2 전체 작업 순서와 사용자-facing 진단 목표 |
| `PRACTICAL_VALIDATION_V2_PROVIDER_CONNECTOR_PLAN.md` | provider 데이터 수집 / DB schema / loader / adapter / 저장 경계 |

새 문서를 만들기보다 이 문서 안의 작은 section을 갱신한다.
단, 실제 DB table이 추가되면 `DATA_DB_PIPELINE_FLOW.md`와 data architecture 문서에는 table 의미만 별도로 반영한다.

## Provider Source Decision

P2 provider connector는 화면에서 외부 사이트를 직접 호출하지 않는다.
수집은 `finance/data/*` ingestion layer에서 수행하고, 결과를 MySQL에 저장한 뒤,
Practical Validation과 Dashboard는 `finance/loaders/*`를 통해 DB snapshot만 읽는다.

```text
공식 API / 공식 CSV / 공식 XLSX / yfinance fallback
  -> finance/data/* collector
  -> finance_meta / finance_price DB table
  -> finance/loaders/* read path
  -> app/web/backtest_practical_validation*.py
```

### Source 우선순위

| 데이터 | 1차 source | fallback / bridge | 저장/해석 기준 |
|---|---|---|---|
| ETF 비용 / 규모 / spread / premium-discount | ETF 발행사 공식 fund page 또는 공식 CSV / XLSX / API. 우선 대상은 iShares / BlackRock, SSGA / SPDR, Invesco | `nyse_asset_profile`의 `total_assets`, `bid`, `ask`와 `nyse_price_history`의 ADV / dollar volume proxy | 공식 provider 값은 `actual`, DB 가격/거래량 계산값은 `proxy`, yfinance profile 값은 `bridge`로 구분 |
| ETF holdings | 발행사 공식 holdings download. iShares는 AOR / IEF / TLT CSV endpoint를 우선 구현하고, SSGA는 SPY / GLD / BIL daily holdings XLSX를 우선 확인한다 | holdings가 없으면 full holdings를 추정하지 않고 ticker bucket proxy 또는 `NOT_RUN` | row 단위 holdings는 DB에 저장하고 JSONL에는 coverage / top exposure summary만 저장 |
| ETF exposure / look-through | holdings snapshot에서 sector / asset class / country exposure를 집계 | holdings coverage가 없으면 기존 ticker bucket proxy | ETF-of-ETF 구조인 AOR은 1차 holdings와 가능한 2차 underlying ETF expansion을 구분 |
| Macro series | FRED API `series/observations` | FRED CSV download. 외부 HTML crawling은 사용하지 않는 방향 | `series_id`, `observation_date`, `source` 기준 long-form 저장 |
| Sentiment proxy | FRED 기반 VIX / credit spread / yield curve + 기존 DB 가격 momentum / drawdown | Fear & Greed 같은 composite index는 안정 source 확인 전 optional | sentiment는 trade signal이 아니라 market context overlay로만 사용 |

### 초기 구현 대상

초기 source map은 현재 Practical Validation과 Selected Portfolio Dashboard에서 자주 쓰는 ETF부터 작게 시작한다.

| ticker | 우선 source | 메모 |
|---|---|---|
| `AOR`, `IEF`, `TLT` | iShares / BlackRock 공식 CSV | holdings CSV 응답 확인 완료. AOR은 ETF-of-ETF look-through가 중요 |
| `SPY` | SSGA / SPDR 공식 fund page + daily holdings XLSX | AUM, expense ratio, premium-discount, median spread, holdings download 확인 대상 |
| `GLD`, `BIL` | SSGA / SPDR 공식 fund page + holdings XLSX | SPDR adapter로 묶어서 구현 가능 |
| `QQQ` | Invesco 공식 page / holdings Excel 또는 API endpoint | endpoint 안정성 확인 후 adapter 구현. 불안정하면 `provider_pending`으로 표시 |
| macro 기본 series | FRED | `VIXCLS`, `T10Y3M`, `BAA10Y`를 1차 후보로 사용 |

`yfinance`는 계속 사용하되, 공식 provider가 없는 field의 임시 bridge로만 취급한다.
특히 expense ratio, median bid-ask spread, holdings의 canonical source로 두지 않는다.

## 데이터 수집 구현 계획

이 section은 ETF holdings, macro series, sentiment series를 먼저 수집해야 할 때의 구현 기준이다.
P2 개발은 UI 표시나 diagnostics 해석보다 먼저 provider source map, DB schema, collector, UPSERT 저장을 만든다.
데이터가 DB에 없으면 Practical Validation은 해당 domain을 `NOT_RUN` 또는 `REVIEW`로 표시한다.

### 개발 시작 순서

1. provider source map과 ticker-to-provider adapter mapping을 정의한다.
2. `finance/data/db/schema.py`에 provider snapshot / holdings / macro table을 추가한다.
3. `finance/data/etf_provider.py`와 `finance/data/macro.py`에서 수집 / normalize / UPSERT를 구현한다.
4. `finance/loaders/*`에서 최신 snapshot과 기준일 snapshot을 읽는다.
5. `app/web/backtest_practical_validation_connectors.py`가 loader 결과를 Practical Validation evidence로 변환한다.
6. UI와 diagnostics는 마지막에 연결한다.

### 1. ETF Holdings 수집

목표:

- ETF 내부 보유종목과 sector / asset class exposure를 DB에 저장한다.
- Practical Validation은 이 데이터를 읽어 ticker proxy 대신 holdings look-through를 사용한다.

권장 파일:

| 파일 | 역할 |
|---|---|
| `finance/data/etf_provider.py` | ETF holdings / exposure 수집과 DB 저장 |
| `finance/loaders/provider.py` | holdings snapshot과 exposure snapshot read path |
| `app/web/backtest_practical_validation_connectors.py` | loader 결과를 Practical Validation evidence로 변환 |

수집 함수 후보:

```python
collect_and_store_etf_holdings(
    symbols: list[str],
    *,
    as_of_date: str | None = None,
    provider: str = "configured_provider",
    refresh_mode: str = "upsert",
) -> dict
```

저장 대상:

- `finance_meta.etf_holdings_snapshot`
- optional aggregate: `finance_meta.etf_exposure_snapshot`

수집 / 저장 규칙:

- `fund_symbol`, `as_of_date`, `source`, `holding_id`를 business key로 사용한다.
- holdings provider가 `holding_id`를 주지 않으면 `holding_symbol + holding_name` 기반 fallback key를 만든다.
- coverage가 없거나 provider가 실패한 ETF는 실패 row 요약만 남기고, full raw response는 저장하지 않는다.
- Practical Validation result JSONL에는 holdings row 전체가 아니라 coverage와 top exposure summary만 저장한다.

검증:

- holdings가 있는 ETF는 top holdings / sector exposure가 loader에서 반환된다.
- holdings가 없는 ETF는 `NOT_RUN` 또는 `REVIEW`로 남고 ticker bucket proxy fallback이 유지된다.

### 2. Macro Series 수집

목표:

- Practical Validation의 market-context 진단에 쓸 macro series를 long-form DB table에 저장한다.

1차 series 후보:

| series | 용도 |
|---|---|
| `VIX` 또는 VIX-equivalent | volatility / risk-off context |
| `T10Y3M` | yield curve inversion / recession risk context |
| credit spread series | credit stress / liquidity stress context |

권장 파일:

| 파일 | 역할 |
|---|---|
| `finance/data/macro.py` | macro / market-context series 수집과 DB 저장 |
| `finance/loaders/provider.py` 또는 `finance/loaders/macro.py` | macro snapshot read path |
| `app/web/backtest_practical_validation_connectors.py` | validation date 기준 macro evidence 생성 |

수집 함수 후보:

```python
collect_and_store_macro_series(
    series_ids: list[str],
    *,
    start: str | None = None,
    end: str | None = None,
    provider: str = "fred",
) -> dict
```

저장 대상:

- `finance_meta.macro_series_observation`

수집 / 저장 규칙:

- `series_id`, `observation_date`, `source`를 business key로 사용한다.
- release lag가 있는 series는 `release_lag_days` 또는 source note를 남긴다.
- API key가 필요하면 hardcode하지 않고 환경변수 / config 경계로 둔다.
- 실패 series는 summary로 반환하고, Practical Validation에서는 해당 series를 `NOT_RUN`으로 표시한다.

검증:

- 지정 기간의 macro row count가 확인된다.
- `load_macro_snapshot(as_of_date=...)`가 validation date 근처 관측값과 staleness를 반환한다.

### 3. Sentiment Series 수집

목표:

- 1차에서는 별도 감성지수를 무리하게 붙이지 않고, 재현 가능한 market-context series를 sentiment overlay로 사용한다.

1차 범위:

- VIX level / change
- credit spread widening / narrowing
- yield curve spread

후속 optional:

- Fear & Greed 같은 composite index
- put / call ratio
- market breadth

수집 방식:

- 1차는 `macro_series_observation` table을 공유한다.
- `category`를 `volatility`, `credit_spread`, `yield_curve`, `sentiment_proxy`처럼 구분한다.
- 안정적인 provider와 재현성이 확인되기 전까지 별도 `sentiment_series_observation` table은 만들지 않는다.

Practical Validation 해석:

- sentiment는 trade signal이 아니다.
- `PASS / REVIEW / NOT_RUN`은 시장 분위기 확인 상태이지 매수 / 매도 판단이 아니다.
- benchmark price-action proxy는 macro / sentiment series가 없을 때만 fallback으로 둔다.

## Connector 설계 원칙

| 원칙 | 내용 |
|---|---|
| UI에서 remote fetch 금지 | Streamlit 화면은 provider API를 직접 호출하지 않고 DB / loader 결과만 읽는다 |
| source와 as-of date 저장 | provider 값은 언제, 어디서 온 값인지 남긴다 |
| proxy와 actual 분리 | price / volume proxy와 provider snapshot을 같은 것으로 취급하지 않는다 |
| missing은 `NOT_RUN` | 데이터가 없으면 통과가 아니라 미실행 / 확인 필요 상태다 |
| full raw data JSONL 저장 금지 | holdings row, macro series, full dataframe은 DB에 두고 validation row에는 compact summary만 저장 |
| idempotent write | 같은 symbol / as_of_date / source는 UPSERT 또는 canonical refresh로 반복 수집 가능해야 한다 |
| no live approval | connector 결과는 Final Review evidence이지 주문 지시가 아니다 |

## 데이터 모델 제안

### 1. ETF Operability Snapshot

권장 table:

```text
finance_meta.etf_operability_snapshot
```

역할:

- ETF별 비용 / 유동성 / 운용성 snapshot을 저장한다.
- `nyse_asset_profile`의 기본 profile을 대체하지 않고, 실전 운용성 전용 snapshot으로 둔다.

주요 column 후보:

| 컬럼 | 의미 |
|---|---|
| `symbol` | ETF ticker |
| `as_of_date` | provider 기준 snapshot 날짜 |
| `source` | provider 이름 |
| `source_ref` | provider page / endpoint / note |
| `fund_family` | issuer / fund family |
| `category` | provider category |
| `expense_ratio` | 총보수 또는 expense ratio |
| `total_assets` | AUM / net assets |
| `nav` | NAV |
| `market_price` | market price |
| `premium_discount_pct` | market price vs NAV 차이 |
| `bid` | bid |
| `ask` | ask |
| `bid_ask_spread_pct` | bid / ask 기반 spread |
| `median_bid_ask_spread_pct` | provider disclosure 기반 median spread |
| `avg_daily_volume` | 평균 거래량 |
| `avg_daily_dollar_volume` | 평균 거래대금 |
| `turnover_ratio` | ETF portfolio turnover 또는 provider turnover |
| `inception_date` | 상장 / 설정일 |
| `leverage_factor` | 1x, 2x, 3x 등 |
| `is_inverse` | inverse 여부 |
| `has_daily_objective` | daily objective 상품 여부 |
| `coverage_status` | `actual`, `partial`, `proxy`, `missing`, `error` |
| `missing_fields_json` | 부족한 field 요약 |
| `collected_at` | 수집 시각 |
| `error_msg` | 오류 메시지 |

권장 unique key:

```text
(symbol, as_of_date, source)
```

### 2. ETF Holdings Snapshot

권장 table:

```text
finance_meta.etf_holdings_snapshot
```

역할:

- ETF 내부 보유종목 row를 저장한다.
- holdings-level overlap, top holding concentration, sector look-through의 원천이다.

주요 column 후보:

| 컬럼 | 의미 |
|---|---|
| `fund_symbol` | ETF ticker |
| `as_of_date` | holdings 기준일 |
| `source` | provider 이름 |
| `holding_symbol` | 보유종목 ticker. 없을 수 있음 |
| `holding_name` | 보유종목 이름 |
| `holding_id` | CUSIP / ISIN / provider id |
| `weight_pct` | ETF 내 비중 |
| `shares` | 보유 수량 |
| `market_value` | 보유 평가액 |
| `sector` | sector |
| `asset_class` | equity / bond / cash / commodity 등 |
| `country` | country |
| `currency` | currency |
| `collected_at` | 수집 시각 |

권장 unique key:

```text
(fund_symbol, as_of_date, source, holding_id)
```

`holding_id`가 없으면 provider별 fallback key가 필요하다.

### 3. ETF Exposure Snapshot

권장 table:

```text
finance_meta.etf_exposure_snapshot
```

역할:

- holdings row를 매번 읽지 않고 aggregated exposure를 빠르게 읽기 위한 optional table이다.

주요 column 후보:

| 컬럼 | 의미 |
|---|---|
| `fund_symbol` | ETF ticker |
| `as_of_date` | exposure 기준일 |
| `source` | provider 이름 |
| `exposure_type` | `sector`, `asset_class`, `country`, `issuer`, `duration_bucket` 등 |
| `exposure_name` | exposure label |
| `weight_pct` | exposure weight |
| `collected_at` | 수집 시각 |

권장 unique key:

```text
(fund_symbol, as_of_date, source, exposure_type, exposure_name)
```

### 4. Macro Series Observation

권장 table:

```text
finance_meta.macro_series_observation
```

역할:

- FRED 또는 안정 provider에서 가져온 market-context series를 long-form으로 저장한다.

주요 column 후보:

| 컬럼 | 의미 |
|---|---|
| `series_id` | 예: `VIX`, `T10Y3M`, `BAA10Y` |
| `observation_date` | 관측일 |
| `value` | 값 |
| `source` | provider |
| `series_name` | 표시 이름 |
| `category` | `volatility`, `yield_curve`, `credit_spread`, `recession` 등 |
| `frequency` | daily / weekly / monthly |
| `release_lag_days` | release lag가 있으면 기록 |
| `collected_at` | 수집 시각 |
| `error_msg` | 오류 메시지 |

권장 unique key:

```text
(series_id, observation_date, source)
```

## Loader 계약

권장 신규 loader module:

```text
finance/loaders/provider.py
```

또는 책임이 커지면 아래처럼 분리한다.

```text
finance/loaders/etf_provider.py
finance/loaders/macro.py
```

### `load_etf_operability_snapshot`

목적:

- symbol list와 기준일을 받아 ETF operability snapshot을 반환한다.
- snapshot table이 없거나 coverage가 없으면 빈 DataFrame 또는 status summary를 안정적으로 반환한다.

예상 signature:

```python
def load_etf_operability_snapshot(
    symbols: list[str] | str,
    *,
    as_of_date: str | None = None,
    latest: bool = True,
) -> pd.DataFrame:
    ...
```

출력 최소 columns:

```text
symbol
as_of_date
source
expense_ratio
total_assets
bid_ask_spread_pct
median_bid_ask_spread_pct
avg_daily_dollar_volume
premium_discount_pct
coverage_status
missing_fields
```

### `load_etf_holdings_snapshot`

목적:

- ETF holdings를 기준일 또는 latest 기준으로 반환한다.

예상 signature:

```python
def load_etf_holdings_snapshot(
    symbols: list[str] | str,
    *,
    as_of_date: str | None = None,
    latest: bool = True,
) -> pd.DataFrame:
    ...
```

출력 최소 columns:

```text
fund_symbol
as_of_date
source
holding_symbol
holding_name
holding_id
weight_pct
sector
asset_class
country
```

### `load_etf_exposure_snapshot`

목적:

- holdings를 이미 집계한 exposure를 읽는다.

예상 signature:

```python
def load_etf_exposure_snapshot(
    symbols: list[str] | str,
    *,
    as_of_date: str | None = None,
    exposure_type: str | None = None,
    latest: bool = True,
) -> pd.DataFrame:
    ...
```

### `load_macro_snapshot`

목적:

- validation 기준일 또는 recheck end 기준으로 가장 가까운 macro context를 반환한다.

예상 signature:

```python
def load_macro_snapshot(
    series_ids: list[str] | None = None,
    *,
    as_of_date: str | None = None,
    lookback_days: int = 10,
) -> pd.DataFrame:
    ...
```

출력 최소 columns:

```text
series_id
series_name
observation_date
value
source
category
status
staleness_days
```

## Practical Validation adapter

권장 신규 app helper:

```text
app/web/backtest_practical_validation_connectors.py
```

역할:

- finance loader output을 Practical Validation diagnostics가 읽기 쉬운 context로 변환한다.
- diagnostics helper가 DB query나 provider detail을 직접 알지 않게 한다.

권장 함수:

```python
def build_provider_context(
    source: dict,
    active_components: list[dict],
    *,
    validation_end: str | None = None,
) -> dict:
    ...
```

반환 구조 예:

```json
{
  "coverage": {
    "operability": "actual | partial | proxy | not_run",
    "holdings": "actual | partial | not_run",
    "macro": "actual | proxy | not_run"
  },
  "operability_rows": [],
  "holdings_exposure_rows": [],
  "macro_rows": [],
  "warnings": [],
  "not_run_reasons": []
}
```

## Diagnostics 반영 방식

| Practical Validation domain | connector 사용 |
|---|---|
| `2. Asset Allocation Fit` | holdings / exposure snapshot이 있으면 holdings-based exposure 우선, 없으면 ticker proxy |
| `3. Concentration / Overlap / Exposure` | holdings overlap / top holding concentration 우선, 없으면 component weight / sector ticker proxy |
| `5. Regime / Macro Suitability` | macro snapshot 우선, 없으면 benchmark price-action proxy |
| `6. Sentiment / Risk-On-Off Overlay` | VIX / credit spread / yield curve context 우선, 없으면 benchmark risk-on/off proxy |
| `9. Leveraged / Inverse ETF Suitability` | leverage / inverse / daily objective provider field 우선, 없으면 ticker proxy |
| `10. Operability / Cost / Liquidity` | ETF operability snapshot 우선, price / volume proxy fallback |

상태 규칙:

| 상황 | 상태 |
|---|---|
| actual provider data가 충분하고 threshold 위반 없음 | `PASS` |
| provider data 일부만 있고 핵심 field가 빠짐 | `REVIEW` |
| connector 자체가 없거나 table이 비어 있음 | `NOT_RUN` |
| 가격 부재, 거래 불가, 상장 폐지, execution boundary 위반 | `BLOCKED` 후보 |
| proxy만 있음 | 일반적으로 `REVIEW`, 단순 보조 metric은 `PASS` 가능하되 origin을 `db_price_proxy`로 표시 |

## JSONL 저장 규칙

`PRACTICAL_VALIDATION_RESULTS.jsonl`에는 compact evidence만 저장한다.

저장 가능:

- provider coverage summary
- per ticker compact operability row
- holdings exposure summary
- macro snapshot summary
- stress interpretation summary
- not-run reason
- source / as_of_date / staleness

저장하지 않음:

- full holdings table
- full macro time series
- full price dataframe
- full provider raw response
- temporary CSV path
- run_history raw rows

권장 optional field:

```json
{
  "provider_coverage": {
    "schema_version": 1,
    "as_of_date": "2026-05-05",
    "operability": {
      "status": "partial",
      "actual_count": 4,
      "proxy_count": 2,
      "not_run_count": 1
    },
    "holdings": {
      "status": "not_run",
      "reason": "holdings connector not configured"
    },
    "macro": {
      "status": "actual",
      "series_count": 3,
      "stale_count": 0
    }
  }
}
```

## Provider data path 첫 구현 단위

이 문서 기준의 첫 구현은 화면 연결이 아니라 provider data collection foundation이다.
기존 `nyse_asset_profile`과 `nyse_price_history` bridge는 fallback으로 유지하되,
P2의 주 작업은 공식 provider / macro source에서 데이터를 수집해 DB에 저장하는 것이다.

첫 구현 범위:

1. provider source map과 adapter mapping 추가
2. `etf_operability_snapshot`, `etf_holdings_snapshot`, `macro_series_observation` schema 추가
3. iShares / SSGA / Invesco / FRED 수집 adapter 골격 추가
4. iShares AOR / IEF / TLT holdings CSV와 FRED 기본 series부터 수집 / UPSERT
5. SSGA SPY / GLD / BIL, Invesco QQQ는 endpoint 안정성 확인 후 같은 adapter 구조로 확장
6. 수집 결과 row count, coverage status, failed symbols summary를 반환
7. 이후 loader와 Practical Validation provider context를 연결

## 후속 구현 단위

1. ETF operability official / bridge data를 같은 coverage summary로 읽는 loader 추가
2. ETF holdings snapshot loader와 exposure aggregation 추가
3. macro snapshot loader와 sentiment proxy context 추가
4. Practical Validation provider coverage UI 연결
5. Practical Validation macro / sentiment / operability domain 연결
6. stress interpretation에서 macro snapshot과 stress window를 연결

## 검증 기준

- [ ] provider table이 없어도 loader와 UI가 실패하지 않는다.
- [ ] 수집기는 같은 symbol / as_of_date / source 기준으로 반복 실행 가능하다.
- [ ] 수집 결과에 `source`, `source_ref`, `as_of_date`, `collected_at`, `coverage_status`가 남는다.
- [ ] coverage가 낮은 ETF는 `REVIEW` 또는 `NOT_RUN`으로 보인다.
- [ ] proxy data는 `provider_snapshot`처럼 표시되지 않는다.
- [ ] `nyse_asset_profile` 기존 reader와 runtime ETF operability path가 깨지지 않는다.
- [ ] Practical Validation result row는 compact evidence만 저장한다.
- [ ] Final Review에서 provider coverage gap을 판단 근거로 볼 수 있다.
- [ ] 새 table이 추가되면 `DATA_DB_PIPELINE_FLOW.md`와 data architecture 문서를 갱신한다.

## 남은 결정

| 결정 | 기본 방향 |
|---|---|
| dedicated table을 바로 만들지 여부 | P2 첫 구현에서 dedicated snapshot table을 추가한다. bridge loader는 fallback |
| provider source | 공식 issuer / FRED 우선. yfinance는 bridge / fallback |
| API key 필요 여부 | hardcoded credential 금지. env / config 경계 필요 |
| holdings refresh cadence | provider와 source license 확인 후 결정 |
| macro observation staleness | series별 frequency에 맞춰 stale threshold 분리 |
| threshold | runtime Real-Money policy와 충돌하지 않게 같은 기준 또는 inherited 기준 사용 |

## 결론

Provider connector는 "좋은 전략을 찾는 기능"이 아니라,
이미 선택된 후보가 실제 ETF 상품과 시장 context 측면에서 검토 가능한 evidence를 갖췄는지 확인하는 데이터 경계다.

따라서 첫 구현은 작게 시작한다.
하지만 시작점은 UI가 아니라 데이터 수집이다.
공식 provider / FRED 데이터를 ingestion에서 DB에 저장하고,
기존 `nyse_asset_profile`과 `nyse_price_history`는 coverage가 비는 영역의 bridge / fallback으로만 사용한다.
