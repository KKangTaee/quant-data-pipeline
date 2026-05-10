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

## 첫 구현 단위

첫 구현은 ETF operability bridge가 가장 좋다.

이유:

- 현재 `nyse_asset_profile`에 이미 `total_assets`, `bid`, `ask` field가 있다.
- `nyse_price_history`에 volume이 있어 ADV proxy를 만들 수 있다.
- runtime `backtest.py`도 이미 ETF operability policy를 일부 계산하므로 개념이 낯설지 않다.
- coverage 부족을 `Provider Coverage`로 보여주는 것만으로도 현재 Practical Validation의 설명력이 올라간다.

첫 구현 범위:

1. loader contract 추가
2. `nyse_asset_profile` + price history ADV bridge
3. provider coverage context 생성
4. Practical Validation `Operability / Cost / Liquidity`에 actual / proxy / missing 구분 표시
5. full provider schema는 확장 가능하게 optional field로 설계

## 후속 구현 단위

1. ETF operability dedicated snapshot table 추가
2. ETF holdings snapshot table + loader 추가
3. holdings exposure aggregation 추가
4. macro series observation table + loader 추가
5. Practical Validation macro / sentiment domain 연결
6. stress interpretation에서 macro snapshot과 stress window를 연결

## 검증 기준

- [ ] provider table이 없어도 loader와 UI가 실패하지 않는다.
- [ ] coverage가 낮은 ETF는 `REVIEW` 또는 `NOT_RUN`으로 보인다.
- [ ] proxy data는 `provider_snapshot`처럼 표시되지 않는다.
- [ ] `nyse_asset_profile` 기존 reader와 runtime ETF operability path가 깨지지 않는다.
- [ ] Practical Validation result row는 compact evidence만 저장한다.
- [ ] Final Review에서 provider coverage gap을 판단 근거로 볼 수 있다.
- [ ] 새 table이 추가되면 `DATA_DB_PIPELINE_FLOW.md`와 data architecture 문서를 갱신한다.

## 남은 결정

| 결정 | 기본 방향 |
|---|---|
| dedicated table을 바로 만들지 여부 | 첫 구현은 bridge loader로 시작하고, 이후 table 추가 |
| provider source | 안정성 / 재현성 / field coverage 확인 후 고정 |
| API key 필요 여부 | hardcoded credential 금지. env / config 경계 필요 |
| holdings refresh cadence | provider와 source license 확인 후 결정 |
| macro observation staleness | series별 frequency에 맞춰 stale threshold 분리 |
| threshold | runtime Real-Money policy와 충돌하지 않게 같은 기준 또는 inherited 기준 사용 |

## 결론

Provider connector는 "좋은 전략을 찾는 기능"이 아니라,
이미 선택된 후보가 실제 ETF 상품과 시장 context 측면에서 검토 가능한 evidence를 갖췄는지 확인하는 데이터 경계다.

따라서 첫 구현은 작게 시작한다.
기존 `nyse_asset_profile`과 `nyse_price_history`로 operability bridge를 만들고,
그 다음 dedicated provider snapshot table, holdings, macro series로 확장한다.
