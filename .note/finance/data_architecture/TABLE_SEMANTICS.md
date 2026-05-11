# Table Semantics

## 목적

이 문서는 주요 table이 어떤 의미를 갖는지 설명한다.
schema column 전체를 복제하지 않고, table의 source / derived / shadow / convenience 성격을 구분하는 데 집중한다.

## `nyse_stock`, `nyse_etf`

역할:

- 전체 universe의 listing master

성격:

- 상대적으로 정적인 master data
- source는 NYSE listing 수집 경로
- 완전한 historical listing membership table은 아니다

## `nyse_asset_profile`

역할:

- universe filtering
- sector / industry / country 분류
- stock / ETF current profile 저장
- ETF current-operability overlay에 필요한 AUM / bid-ask snapshot 저장

성격:

- current profile snapshot에 가깝다.
- `status`, `is_spac`, country filter 등은 유용하지만 완전한 point-in-time truth는 아니다.
- ETF AUM / bid-ask field는 current-operability 판단에 쓰이며, strict annual stock strategy의 PIT liquidity 판단과는 다른 층위다.

## `etf_operability_snapshot`

역할:

- Practical Validation V2의 ETF 운용성 / 비용 / 유동성 진단에 쓸 snapshot 저장
- ETF별 AUM / bid-ask spread / 평균 거래량 / 평균 거래대금 / market price 같은 bridge/proxy evidence 보존
- 후속 official issuer provider 수집 결과를 같은 table에 `source`별로 저장할 수 있는 경계 제공

성격:

- provider snapshot table이다.
- 현재 P2-2A 구현은 official provider actual row가 아니라 `db_bridge` source row를 저장한다.
- `db_bridge` row는 `nyse_price_history`에서 계산한 ADV / dollar volume proxy와
  `nyse_asset_profile`의 total assets / bid / ask bridge를 합친 것이다.
- `coverage_status`가 `bridge` 또는 `proxy`면 actual provider data로 해석하지 않는다.

주의:

- expense ratio, NAV, premium / discount, official leveraged / inverse metadata는 아직 actual source가 아니다.
- current snapshot이므로 historical point-in-time ETF 운용성 truth로 바로 해석하면 안 된다.
- Practical Validation result JSONL에는 full row를 저장하지 않고 compact evidence / coverage status만 저장하는 방향이다.

## `nyse_price_history`

역할:

- 가격 기반 backtest의 핵심 price ledger

성격:

- stock과 ETF를 함께 저장하는 공용 price fact table
- OHLCV, dividend, split 정보를 저장한다
- asset type 해석은 `nyse_stock`, `nyse_etf`, `nyse_asset_profile`과 함께 본다

주의:

- price missing row, stale date, provider no-data는 strategy result 기간에 직접 영향을 줄 수 있다.
- date alignment 정책은 `code_analysis/BACKTEST_RUNTIME_FLOW.md`를 같이 본다.

## `nyse_fundamentals`

역할:

- provider-normalized broad fundamentals summary

성격:

- yfinance statement 기반 broad coverage layer
- factor 계산용 중간 table
- strict raw accounting ledger가 아니다
- direct / derived / inferred source metadata를 함께 추적할 수 있다

주의:

- `period_end` 중심이므로 filing-time PIT source로 바로 쓰면 look-ahead risk가 있다.

## `nyse_fundamentals_statement`

역할:

- statement ledger 기반 fundamentals shadow

성격:

- `nyse_financial_statement_values`에서 usable raw rows를 읽어 재구성한 shadow table
- public broad table을 대체하지 않고 비교 / 검증 / strict strategy runtime 용도로 유지한다
- 현재 의미는 각 `period_end`에 대한 earliest usable filing snapshot에 가깝다

주의:

- schema column 이름에 `latest_*`가 남아 있어도, 현재 해석은 period_end별 earliest usable snapshot 쪽으로 읽는다.
- `shares_outstanding`은 statement-derived를 우선하고, 없으면 broad fallback을 사용할 수 있다.

## `nyse_factors`

역할:

- broad fundamentals와 as-of price를 이용한 derived factor table

성격:

- broad research / prototype strategy input 후보
- strict PIT factor store가 아니다
- price attachment metadata와 timing 의미를 함께 저장한다

주의:

- `period_end` 기준 as-of price matching은 유용하지만, filing availability 기준과는 다를 수 있다.

## `nyse_factors_statement`

역할:

- statement fundamentals shadow와 as-of price를 이용한 derived factor shadow

성격:

- quality / accounting 계열 strict strategy에 더 적합한 factor layer
- `fundamental_available_at`, `fundamental_accession_no` 같은 metadata를 포함한다
- `Quality Snapshot (Strict Annual)`, `Value Snapshot (Strict Annual)` public fast runtime source로 사용된다

주의:

- shares fallback이 없거나 부족한 row에서는 valuation 계열 factor가 `NULL`일 수 있다.

## `nyse_financial_statement_filings`

역할:

- filing 단위 공시 metadata ledger

성격:

- 사람이 filing source를 inspect할 수 있게 하는 ledger
- `accession_no`, `filing_date`, `accepted_at`, `available_at`, `report_date` 중심으로 본다

## `nyse_financial_statement_values`

역할:

- filing / concept / period 단위 상세 재무 계정 저장

성격:

- long-format raw fact ledger
- actual `period_end`와 공시 가능 시점을 함께 보존한다
- PIT-friendly raw row는 `accession_no`, `unit`, `available_at`가 있는 row를 우선 취급한다
- custom factor engine의 원재료가 될 수 있다

주의:

- quarterly path는 `10-Q`, `10-Q/A`, `10-K`, `10-K/A`를 함께 받을 수 있다.
- DB 저장 단계에서 synthetic Q4를 만들지 않는다.
- provider의 `fiscal_year` / `fiscal_period`는 filing context일 수 있으므로, row identity는 `period_end`와 `accession_no`를 우선한다.
- `periods=0` ingestion은 source가 가진 usable history를 최대한 적재하는 의미다.

## `nyse_financial_statement_labels`

역할:

- concept summary와 operator-facing label helper

성격:

- UI / 해석 보조 layer
- strict loader의 source of truth가 아니다.
- 실제 statement value 판단은 `nyse_financial_statement_values`를 중심으로 읽는다.
