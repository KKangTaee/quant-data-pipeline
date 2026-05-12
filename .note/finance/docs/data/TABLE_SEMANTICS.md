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

## `etf_provider_source_map`

역할:

- ETF별 공식 provider endpoint와 parser mapping을 저장한다.
- Practical Validation의 Provider Data Gaps가 "수집 가능한 부족 데이터"와 "아직 connector mapping이 필요한 데이터"를 구분할 때 사용한다.
- `etf_operability_snapshot`, `etf_holdings_snapshot`, `etf_exposure_snapshot` 수집기가 static ticker map보다 먼저 참조하는 verified source cache다.

성격:

- connector metadata table이다.
- 원천은 `nyse_etf`, `nyse_asset_profile`, issuer 공식 product list / 다운로드 endpoint 검증이다.
- `source_status=verified`인 row만 실제 수집 가능 mapping으로 읽는다.
- `failed`, `unsupported`, `missing` row는 자동 수집 불가 사유를 남기는 운영 metadata다.

주의:

- 이 table은 holdings나 operability data 자체를 저장하지 않는다. 어디서 어떻게 수집할지를 저장한다.
- current provider endpoint 검증 cache이므로 과거 특정 시점의 provider URL truth가 아니다.
- 운용사 사이트 구조가 바뀌면 discovery를 다시 실행하거나 adapter를 보강해야 한다.

## `etf_operability_snapshot`

역할:

- Practical Validation V2의 ETF 운용성 / 비용 / 유동성 진단에 쓸 snapshot 저장
- ETF별 AUM / bid-ask spread / 평균 거래량 / 평균 거래대금 / market price 같은 bridge/proxy evidence 보존
- official issuer provider 수집 결과를 같은 table에 `source`별로 저장

성격:

- provider snapshot table이다.
- P2-2A 구현은 `db_bridge` source row를 저장한다.
- `db_bridge` row는 `nyse_price_history`에서 계산한 ADV / dollar volume proxy와
  `nyse_asset_profile`의 total assets / bid / ask bridge를 합친 것이다.
- `coverage_status`가 `bridge` 또는 `proxy`면 actual provider data로 해석하지 않는다.
- P2-2B 구현은 iShares / SSGA / Invesco official page row를 `source_type=official`로 저장한다.
- official row의 `actual`은 핵심 operability field 묶음이 3개 이상 확인됐다는 뜻이고,
  `partial`은 일부 field만 확인됐다는 뜻이다.

주의:

- source map discovery가 verified row를 만든 ETF는 static map 밖이어도 official coverage를 수집할 수 있다.
- Invesco QQQ는 현재 expense ratio / inception만 있어 `partial`로 저장된다.
- current snapshot이므로 historical point-in-time ETF 운용성 truth로 바로 해석하면 안 된다.
- Practical Validation result JSONL에는 full row를 저장하지 않고 compact evidence / coverage status만 저장하는 방향이다.

## `etf_holdings_snapshot`

역할:

- Practical Validation V2의 ETF 구성 / concentration / overlap 진단에 쓸 holdings row 저장
- ETF별 보유종목, 비중, sector, asset class, country, currency field를 provider snapshot으로 보존

성격:

- provider snapshot table이다.
- P2-3 초기 구현은 iShares holdings CSV, SSGA daily holdings XLSX, Invesco holdings API를 official source로 사용한다.
- `weight_pct`는 decimal fraction이 아니라 provider가 표시하는 percent point다. 예: `34.13`은 34.13%다.
- 반복 수집은 기본적으로 fund / as_of_date / source 범위를 canonical refresh한다.

주의:

- current snapshot이므로 과거 특정 시점의 holdings truth로 바로 해석하면 안 된다.
- `AOR`은 현재 1차 ETF holdings만 저장한다. Aggregate Underlying 2차 look-through는 후속이다.
- `GLD`, `IAU`는 금 현물 ETF 특성상 row-level stock holdings 대신 `commodity_gold` 100% gold row를 저장한다.

## `etf_exposure_snapshot`

역할:

- holdings row를 asset class / sector / country / currency 등으로 집계한 summary 저장
- 일부 provider가 별도 aggregate exposure를 제공하면 `derived_from=provider_aggregate`로 저장

성격:

- derived summary table이다.
- `derived_from=etf_holdings_snapshot`이면 저장된 holdings row에서 계산한 값이다.
- `derived_from=provider_aggregate`이면 SSGA sector breakdown, Invesco weighted sector API처럼 provider가 제공한 aggregate다.

주의:

- exposure는 원천 holdings coverage와 provider aggregate coverage에 의존한다.
- sector가 없는 holdings source는 asset class / currency exposure만 만들 수 있다.
- Practical Validation result JSONL에는 full exposure table이 아니라 compact summary만 저장하는 방향이다.

## `macro_series_observation`

역할:

- Practical Validation V2의 market-context 진단에 쓸 macro / sentiment proxy observation 저장
- VIX, yield curve, credit spread 같은 series를 long-form으로 보존

성격:

- provider snapshot table이다.
- P2-4 초기 구현은 FRED `VIXCLS`, `T10Y3M`, `BAA10Y`를 수집한다.
- `series_id`, `observation_date`, `source`가 business key다.
- API key가 있으면 FRED API, 없으면 FRED official CSV download를 사용한다.

주의:

- macro / sentiment는 trade signal이 아니라 validation 기준일의 시장 환경 설명 자료다.
- FRED value는 observation date 기준 데이터이며, 실제 발표 / 수정 vintage point-in-time truth와는 구분해야 한다.
- Practical Validation result JSONL에는 full series를 저장하지 않고 compact snapshot / staleness만 저장하는 방향이다.

## `nyse_price_history`

역할:

- 가격 기반 backtest의 핵심 price ledger

성격:

- stock과 ETF를 함께 저장하는 공용 price fact table
- OHLCV, dividend, split 정보를 저장한다
- asset type 해석은 `nyse_stock`, `nyse_etf`, `nyse_asset_profile`과 함께 본다

주의:

- price missing row, stale date, provider no-data는 strategy result 기간에 직접 영향을 줄 수 있다.
- date alignment 정책은 `docs/architecture/BACKTEST_RUNTIME_FLOW.md`를 같이 본다.

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
