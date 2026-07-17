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

## `nyse_symbol_lifecycle`

역할:

- symbol lifecycle, historical universe membership, delisting evidence를 저장한다.
- Data Coverage Audit의 `Universe / listing evidence`와 `Survivorship / delisting control` row가 이 table의 compact loader summary를 읽는다.

성격:

- lifecycle evidence table이다.
- `source_type=current_listing_snapshot` row는 NYSE 현재 listing을 반복 관찰하기 위한 partial `event_type=listing_observed` evidence다.
- `source=nasdaq_symdir_nasdaqlisted` 또는 `nasdaq_symdir_otherlisted` row도 Nasdaq Symbol Directory current snapshot에서 온 partial `listing_observed` evidence다.
- `source=sec_company_tickers_exchange` row는 SEC current CIK / ticker / exchange association에서 온 partial `listing_observed` identity evidence다.
- `source=computed_snapshot_lifecycle` row는 existing current snapshot rows에서 계산한 repeated observation window이며 partial `historical_membership` evidence다.
- `source_type=delisting_feed` row는 SEC Form 25 같은 delisting source에서 온 actual `event_type=delisting` evidence를 담을 수 있다.
- `source_type=historical_listing`, `delisting_feed`, `computed_from_snapshots` row가 requested backtest period를 덮고 `coverage_status=actual`일 때만 survivorship control PASS 근거가 된다.
- Phase 8부터 `event_type`, `event_date`, `related_symbol`, `related_cik`를 사용할 수 있다.
  이 필드는 ticker change / merger / delisting / membership event를 source-neutral하게 읽기 위한 nullable event semantics다.
- Backtest Symbol Resolver V1부터 `event_type=ticker_change` row는 `related_symbol`을 resolved ticker 후보로 읽을 수 있다.
  `resolution_status=candidate`는 Factor Readiness가 보여주는 검토 후보, `resolution_status=active`는 user-approved repair로서 가격 수집 ticker만 resolved symbol로 바꾸는 근거다.
  `confidence`는 identity 후보 점수이며, `evidence_json`은 `source_quality`, `review_note`, `evidence_factors`, `recommended_action` 같은 compact source evidence를 보존할 수 있다.
  Active repair를 읽은 price refresh plan은 `source_range`, `resolved_range`, `split_status`를 metadata-only PIT split contract로 노출할 수 있지만, source universe symbol을 자동 rewrite하거나 실제 old/new ticker price series stitching을 수행한다는 뜻은 아니다.
- `finance/data/nyse_db.py`는 기존 NYSE listing CSV 적재 시 current snapshot row를 idempotent하게 UPSERT할 수 있다.
- `finance/data/symbol_directory.py`는 Nasdaq public Symbol Directory current files를 idempotent하게 UPSERT할 수 있다.
- `finance/data/sec_company_tickers.py`는 SEC current CIK / ticker / exchange association을 idempotent하게 UPSERT할 수 있다.
- `finance/data/sec_delisting.py`는 SEC EDGAR Form 25 / 25-NSE filing metadata를 idempotent하게 UPSERT할 수 있다.

주의:

- current listing snapshot만으로 과거 backtest 기간의 universe membership을 증명할 수 없다.
- Form 25는 delisting / withdrawal evidence이며, Form 25 부재는 active listing proof가 아니다.
- Form 25만으로 first listing date와 complete historical membership을 알 수 없으므로, full survivorship control에는 별도 historical listing source가 필요할 수 있다.
- repeated current snapshot은 관찰 구간 요약일 뿐이고, missing snapshot을 delisting이나 inactive proof로 해석하지 않는다.
- table이 생겼다고 survivorship bias가 자동 제거되는 것은 아니다. 과거 delisting / historical membership source를 실제로 적재해야 PASS 근거가 된다.
- workflow JSONL에는 full lifecycle row를 저장하지 않고 compact audit evidence만 남긴다.

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

## `equity_universe_snapshot`, `equity_universe_member`

역할:

- Quality / Value strict annual and quarterly family가 현재 Top-N을 과거 전체 기간에 고정하지 않도록, 월말 기준 prebuilt equity universe membership을 저장한다.
- `equity_universe_snapshot`은 `universe_code`, `as_of_date`, target size, source basis, method version 같은 snapshot header를 저장한다.
- `equity_universe_member`는 snapshot별 symbol, rank, included 여부, approximate market cap, latest price / shares evidence, liquidity proxy, exclusion reason을 저장한다.

성격:

- derived PIT-like universe snapshot이다.
- V1 source basis는 DB `nyse_price_history`의 월말 가격과 statement shadow / available shares evidence, 그리고 `nyse_asset_profile`의 current profile filter다.
- UPSERT key는 stable snapshot code / date / symbol 조합이며, 같은 기준을 다시 빌드해도 같은 snapshot을 갱신하는 idempotent path다.
- strict factor runtime은 `finance/loaders/universe.py::load_pit_universe_membership_snapshots`를 통해 included member만 읽고, 각 rebalance date는 가장 가까운 이전 월말 snapshot membership에 매핑된다.

주의:

- S&P 500 / Russell 같은 공식 historical index membership이 아니다.
- free/provider DB 기반 근사 PIT이며, shares evidence가 latest-known 또는 shadow fallback이면 완전한 filing-time float-adjusted market cap truth가 아니다.
- monthly snapshot table이 비어 있거나 requested period를 덮지 않으면 `PIT Monthly Snapshot Universe` 계약은 실행 전에 막혀야 한다.
- 이 table은 survivorship risk를 줄이는 장치지만, delisting / ticker change / official historical membership source를 완전히 대체하지 않는다.

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

## `market_universe_member`

역할:

- Overview Market Movers에서 쓰는 관리형 universe membership을 저장한다.
- 초기 구현은 S&P 500 current constituents를 `universe_code=SP500`으로 저장한다.

성격:

- current universe snapshot table이다.
- source는 Wikipedia S&P 500 constituents table이며, ticker는 Yahoo Finance 호환을 위해 `.`을 `-`로 정규화한다.
- Top1000 / Top2000 coverage는 이 table이 아니라 `market_liquidity_universe_member` materialized membership을 사용한다.

주의:

- historical S&P 500 membership이나 point-in-time constituent truth가 아니다.
- 상장폐지 / 편입변경의 과거 재현이 필요한 backtest universe로 바로 쓰면 survivorship bias가 생길 수 있다.

## `market_liquidity_universe_member`

역할:

- Market Movers Top1000 / Top2000 current membership을 저장한다.
- `nyse_symbol_lifecycle` / `nyse_stock` 등 listing source에서 후보 ticker를 읽고, `nyse_price_history`의 최근 거래일 row가 있는 후보만 ranking 대상으로 삼는다.
- ranking 기준은 최근 20거래일 `close * volume` 평균 거래대금이다.

성격:

- materialized current universe snapshot table이다.
- `rank_position`, `avg_dollar_volume`, `lookback_trading_days`, `as_of_date`, `ranking_source`, `price_source`, `listing_source`를 함께 저장해 UI와 snapshot refresh가 같은 membership을 재사용하게 한다.
- Top1000 / Top2000은 더 이상 `nyse_asset_profile.market_cap` snapshot으로 순위를 정하지 않는다. `nyse_asset_profile`은 회사명, sector, industry 같은 보조 metadata join에만 사용한다.
- listing source fallback이 비어 있으면 legacy profile fallback으로 자동 대체하지 않는다. 이 경우 universe 기준 갱신 결과가 실패 / 확인 필요 상태로 남아 listing source 갱신을 먼저 요구한다.

주의:

- 이 table은 "가장 큰 기업" 순위가 아니라 "최근 거래대금이 큰 종목" 순위다.
- 신규 상장 ticker는 current listing source에 들어오고, 이후 `nyse_price_history`에 최신 EOD 가격 / 거래량 row가 저장되어야 포함될 수 있다.
- 최신 거래일 price row가 없는 ticker는 ranking 가능한 후보에서 제외된다. 이는 stale listing, provider 누락, delisted ticker, 거래 정지 가능성을 모두 포함하는 보수적 처리다.
- current snapshot이므로 historical point-in-time membership이나 survivorship control PASS 근거가 아니다.

## `market_symbol_alias`

역할:

- Market Movers daily snapshot에서 old ticker가 더 이상 Yahoo quote row를 반환하지 않을 때 replacement ticker 후보와 적용 상태를 저장한다.
- `SATS -> ECHO`, `VSCO -> VSXY` 같은 ticker-change repair를 반복 조사 없이 재사용하게 한다.

성격:

- alias mapping / repair state table이다.
- `status=candidate` row는 자동 탐지 또는 화면 read-model이 제안한 후보이며, quote lookup에는 아직 적용하지 않는다.
- `status=active` row는 사용자가 `티커 변경 복구 적용` action으로 승인한 alias이며, 이후 `market_intraday_snapshot` 수집에서 source universe symbol의 quote lookup symbol을 바꾼다.
- `evidence_json`은 official 확인, search / quote verification 같은 compact 근거를 담는다. Full external page나 provider raw response를 저장하는 테이블이 아니다.

주의:

- 이 table은 universe membership 자체를 교체하지 않는다. 예를 들어 Top1000 universe row는 `SATS`로 남을 수 있고, quote lookup만 `ECHO`를 사용한다.
- ticker change 후보는 provider/search evidence 기반 운영 복구 힌트이며, corporate action의 최종 official master가 아니다.
- active alias 적용 후에도 `일중 스냅샷 갱신`을 다시 실행해야 `market_intraday_snapshot` missing row가 실제 가격 row로 대체된다.

## `market_intraday_snapshot`

역할:

- Overview Market Movers의 daily view에서 전일 종가 대비 최신 intraday 가격 수익률을 coverage별로 저장한다.
- 현재 coverage는 `SP500`, `TOP1000`, `TOP2000`, `NASDAQ`이다.

성격:

- provider snapshot table이다.
- 기본 source는 yfinance 세션을 통한 Yahoo quote batch이고, 실패 시 yfinance 5m OHLCV fallback을 사용할 수 있다.
- `previous_close`, `latest_price`, `return_pct`, `provider_status`, `error_msg`를 함께 저장한다.
- `quote_symbol`은 실제 provider quote 조회에 사용한 ticker다. ticker-change repair가 적용되면 `symbol`은 universe member ticker를 유지하고 `quote_symbol`만 replacement ticker가 될 수 있다.
- UI는 정상 render 때 provider를 직접 호출하지 않고 이 table의 최신 snapshot을 읽는다.
- `TOP1000` / `TOP2000`은 `market_liquidity_universe_member`의 active membership을 기본 universe로 읽어 저장한다.

주의:

- 무료 provider 기반이므로 지연, rate limit, ticker별 missing이 발생할 수 있다.
- `provider_status != ok` row는 missing diagnostics로 노출하고 ranking에는 쓰지 않는다.
- Market Movers quote gap diagnosis는 이 table의 missing row를 대상으로 추가 evidence를 조회해 job result로 보여주고, 반복 추적용으로 `market_data_issue`에도 누적 저장한다.
- `TOP1000` / `TOP2000` 일중 스냅샷 갱신은 이미 materialize된 liquidity universe를 읽는다. Universe 기준 자체를 바꾸려면 Market Movers의 `유니버스 기준 갱신`을 먼저 실행한다.
- active ticker alias가 있으면 quote lookup은 alias를 사용하지만 ranking / display symbol은 universe symbol을 유지한다. Source ref에 `alias_symbol=<ticker>`가 남는다.

## `market_data_issue`

역할:

- Overview Market Movers에서 반복되는 quote gap / coverage issue를 symbol / universe 단위로 누적 추적한다.
- `issue_type=quote_gap`은 일중 quote 누락을, `issue_type=limited_price_history`는 full-window EOD 수집 뒤에도 provider 가용 이력이 period 최소 row보다 짧은 상태를 나타낸다.

성격:

- 운영 issue tracking table이다.
- `issue_key`는 `universe_code`, `symbol`, `issue_type` 조합에서 만든 내부 business key다.
- 같은 symbol / universe에서 다시 진단되면 `occurrence_count`를 증가시키고 최신 diagnosis, confidence, evidence, recommended action을 갱신한다.
- `raw_payload_json`에는 마지막 진단 row의 compact evidence를 저장한다.
- `limited_price_history`는 first/latest date, 현재/필요 row count만 근거로 저장하며 상장일이나 기업 이벤트 원인을 단정하지 않는다.

주의:

- 이 table은 투자 신호나 official corporate action fact가 아니다.
- `possible_stale_universe`도 상장폐지 / 거래정지 확정 판정이 아니라 profile / price evidence가 약하다는 운영 힌트다.
- issue가 사라졌다는 자동 resolve lifecycle은 아직 없다. 현재는 반복 발생을 빠르게 알아보는 목적이다.
- limited-history issue가 남아 있어도 현재 `nyse_price_history` row count가 period threshold를 충족하면 Market Movers preflight는 정상 계산 경로를 우선한다.

## `market_event_calendar`

역할:

- Overview Events 탭에서 보여줄 시장 이벤트 calendar row를 저장한다.
- FOMC, earnings, 기타 macro / market schedule collector가 같은 table contract를 재사용한다.

성격:

- provider snapshot table이다.
- `event_date`, `event_type`, `event_family`, `event_subtype`, `event_time_label`, `event_datetime_utc`, `universe_scope`, `source_authority`, `symbol`, `title`, `source`, `source_type`, `validation_status`, `event_status`, `source_url`, `confidence`, `collected_at`, `raw_payload_json`을 공통 컬럼으로 둔다.
- `event_key`는 반복 수집이 같은 event row를 UPSERT하도록 만든 내부 business key다.
- UI는 정상 render 때 외부 페이지를 직접 파싱하지 않고 이 table을 읽는다.
- `event_family`는 `central_bank`, `macro`, `earnings`, `fixed_income`, `market_structure`, `corporate_action`, `other` 같은 표시/필터용 대분류다.
- `event_subtype`은 `cpi`, `ppi`, `employment`, `gdp`, `fomc_meeting`, `options_expiration`, `index_rebalance`, `earnings`처럼 source-neutral detail을 담는다.
- `universe_scope`는 `official_macro`, `all_us`, `sp500`, `nasdaq100`, `portfolio`, `watchlist`, `latest_movers`, `major_cap` 등 이벤트가 적용되는 universe를 나타낸다.
- `source_authority`는 `official`, `issuer_confirmed`, `provider_estimate`, `cross_checked`, `not_confirmed`, `conflict`, `unknown`으로 읽는다. `cross_checked`는 여전히 official confirmation이 아니다.
- FOMC row의 `source`는 `federal_reserve_fomc_calendar`, `event_type`은 `FOMC_MEETING`이다.
- FOMC meeting range는 정책 결정일 기준으로 마지막 날을 `event_date`로 저장한다. 예: `June 16-17*`는 `2026-06-17`로 저장한다.
- Macro row는 공식 release schedule에서 온 event timing metadata다.
- BLS source row는 `source=bureau_labor_statistics_release_schedule`이며 CPI / PPI / Employment Situation / JOLTS / ECI를 각각 `MACRO_CPI`, `MACRO_PPI`, `MACRO_EMPLOYMENT`, `MACRO_JOLTS`, `MACRO_ECI`로 저장한다.
- BLS 자동 요청이 차단되면 사용자가 내려받은 공식 `.ics` 파일을 Ingestion에서 import할 수 있고, 이 row는 같은 source와 `raw_payload_json.import_method=official_ics_file`로 저장된다.
- BEA source row는 `source=bureau_economic_analysis_release_schedule`이며 national GDP / Personal Income and Outlays releases를 `MACRO_GDP`, `MACRO_PCE`로 저장한다.
- Census source row는 `source=census_economic_indicators_calendar`이며 retail sales, durable goods, housing, construction, and trade indicator releases를 macro subtype으로 저장할 수 있다.
- ISM source row는 `source=ism_report_calendar`이며 Manufacturing / Services PMI releases를 `MACRO_ISM_MANUFACTURING_PMI`, `MACRO_ISM_SERVICES_PMI`로 저장한다.
- TreasuryDirect source row는 `source=treasurydirect_auction_calendar`, `event_family=fixed_income`, `event_type=TREASURY_AUCTION`으로 저장한다.
- Official macro/fixed-income rows may populate `event_time_label` and `event_datetime_utc` when the source provides an ET release time.
- Earnings row의 primary `source`는 `yfinance_calendar`, `event_type`은 `EARNINGS`, `source_type`은 `provider_estimate`이다.
- Earnings row는 manual symbol list, latest S&P 500 movers, 또는 S&P 500 / Top1000 / Top2000 low-frequency batch에서 파생된 bounded symbol set을 대상으로 한다.
- Nasdaq earnings calendar는 같은 symbol/date를 확인하는 alternate free provider cross-check로만 사용한다. `validation_status=cross_checked`는 official row를 뜻하지 않는다.
- 날짜가 변경된 같은 symbol/source의 이전 active earnings estimate는 `event_status=superseded`로 남긴다.
- 요청 ticker 중 저장 row가 없는 symbol의 missing / failure reason은 `market_event_calendar`에 별도 row로 쓰지 않고 job result의 `symbol_diagnostics`와 generated failure CSV에 남긴다.
- Overview read model은 `Validation`, `Freshness`, `Quality Action`을 계산해 estimate-only / not-confirmed / stale row의 다음 조치를 표시한다.
- Overview read model은 legacy row에 taxonomy column이 비어 있어도 `event_type`, `source_type`, `validation_status`, `source`에서 `Event Family`, `Event Subtype`, `Universe Scope`, `Source Authority`를 보수적으로 추론한다.

주의:

- calendar row는 수집 시점의 provider snapshot이며 완전한 point-in-time historical event truth가 아니다.
- FOMC의 `*` 표시는 Summary of Economic Projections 관련 meeting 의미이며 `raw_payload_json.has_summary_of_economic_projections`에 보존한다.
- BLS schedule page는 공식 source지만 자동 요청이 HTTP 403으로 차단될 수 있다. 이 경우 macro collector는 가능한 source만 저장하고 partial failure를 job result에 남기며, BLS `.ics` import fallback으로 CPI / PPI / Jobs row를 보강한다.
- earnings free source는 provider별 coverage / delay / 누락 가능성이 크므로 yfinance-only row는 `confidence=0.65`, Nasdaq cross-checked row는 `confidence=0.75`를 사용한다.
- S&P 500 / Nasdaq-100 / portfolio / watchlist earnings coverage는 후속 collector 확장 대상이다. 이 table schema는 먼저 그 coverage를 받을 수 있게 확장되었지만, row가 저장되기 전까지 coverage가 존재한다는 뜻은 아니다.
- `symbol_diagnostics.reason`의 주요 값은 `no_provider_earnings_date`, `outside_window`, `provider_error`다. 이는 수집 운영 진단이며 event calendar fact row는 아니다.
- generic company IR official parser는 아직 없다. 공식 source가 필요한 ticker는 후속 symbol-specific parser나 manual verification이 필요하다.
- `raw_payload_json`은 UI 표시용 source of truth가 아니라 diagnostics와 후속 collector 개선을 위한 compact evidence다.

## `institutional_13f_manager`, `institutional_13f_filing`, `institutional_13f_holding`, `institutional_13f_cusip_symbol_map`, `institutional_13f_manager_watchlist`, `institutional_13f_refresh_status`

역할:

- `Workspace > Institutional Portfolios`가 투자 대가 / 기관별 SEC Form 13F portfolio를 탐색할 때 쓰는 delayed regulatory holdings ledger다.
- `institutional_13f_manager`는 manager / filer identity와 latest filing pointer를 저장한다.
- `institutional_13f_filing`은 accession, report period, filing date, amendment flag, source data set, source link를 저장한다.
- `institutional_13f_holding`은 13F information table row를 저장한다.
- `institutional_13f_cusip_symbol_map`은 CUSIP 기반 display symbol 보조 mapping을 저장한다. 완전한 security master가 아니므로 service read model은 ambiguous mapping을 차트 / 가격 성과용 ticker로 쓰지 않는다.
- `institutional_13f_manager_watchlist`는 Berkshire Hathaway, Pershing Square, Appaloosa, Baupost, Duquesne 같은 화면 rail seed metadata와 투자자 alias 검색 metadata를 저장할 수 있다. 저장 row가 없으면 service seed watchlist를 fallback으로 사용한다.
- `institutional_13f_refresh_status`는 마지막 SEC dataset 수집 결과, 최신 보고분기 / filing date, row counts, stale reason을 저장한다.

성격:

- official SEC Form 13F quarterly data set에서 온 filing / holdings ledger다.
- 반복 수집은 source dataset / accession / CUSIP / row identity 기준 UPSERT로 idempotent하게 동작한다.
- 화면은 최신 filing과 직전 filing을 비교해 신규 보고, 증가, 감소, 전량 매도 후보를 만든다.
- sector / industry exposure는 row에 있는 field 또는 CUSIP-symbol mapping / conservative asset profile name-match enrichment를 사용하며, 없으면 `Unmapped`로 표시한다.
- refresh status는 product freshness metadata이며 full source row를 대체하지 않는다.

주의:

- 13F는 quarter-end 이후 최대 45일 늦게 제출될 수 있으므로 실시간 보유나 "지금 사고 있다" 근거가 아니다.
- 13F는 주로 reportable long positions를 보여주며 shorts, cash, derivatives, hedges, non-13F securities, full trading intent를 완전히 보여주지 않는다.
- amendment, confidential treatment, filer error, SEC extraction issue가 있을 수 있으므로 원문 filing / source link를 함께 확인해야 한다.
- `period_of_report`와 `filing_date` / SEC acceptance timing을 구분해야 하며, backtest에 쓰려면 filing availability 기준 PIT 처리가 별도로 필요하다.
- CUSIP-symbol mapping은 완전한 security master가 아니며 ticker change, share class, ADR, delisting, CUSIP reuse / change를 완전히 해결하지 않는다.
- asset profile name-match enrichment는 issuer name이 고유하게 매칭될 때만 보수적으로 저장하는 display helper다. 충돌하거나 불명확한 회사명은 mapping하지 않는다.
- 이 table의 reported change는 추천, 매수 / 매도 신호, Practical Validation PASS / BLOCKER, Final Review selection, monitoring signal, broker order, auto rebalance를 만들지 않는다.

## `futures_instrument`, `futures_ohlcv`, `futures_market_monitor_run`

역할:

- `Workspace > Overview > Futures Macro`에서 주요 선물 daily macro context와 lazy historical validation을 만들고, 보조 stored-candle chart / diagnostics에서 1m OHLCV 상태를 read-only로 표시하기 위한 데이터 경계다.
- `futures_instrument`는 watchlist preset / display metadata를 저장한다.
- `futures_ohlcv`는 provider symbol / interval / candle time 기준 OHLCV row를 저장한다. 1m row는 stored-candle chart / diagnostics에, 1d row는 Futures Macro의 현재 점수 / 해석과 point-in-time historical validation에 사용된다.
- `futures_market_monitor_run`은 수집 run별 status, failed symbols, latest candle time, diagnostics를 저장한다.

성격:

- provider snapshot / price ledger 성격이다.
- 1차 MVP source는 `yfinance`이며, exchange-grade realtime feed가 아니다.
- UI는 정상 render 때 provider를 직접 호출하지 않고 `futures_ohlcv`와 run diagnostics를 읽는다.
- 반복 수집은 `(provider_symbol, interval_code, candle_time_utc, source)` 기준 UPSERT로 idempotent하게 동작한다.
- yfinance `1d / 1m` 요청이 일부 futures symbol에서 빈 응답 또는 지나치게 희소한 응답을 줄 수 있어, collector는 해당 symbol만 `2d / 1m`으로 한 번 보강 수집한다. 희소 응답이 회복되면 초기 sparse rows를 같은 symbol의 fallback rows로 대체한 뒤 같은 `futures_ohlcv` UPSERT key로 저장하고, 초기 row 수 / 회복 symbol / 실패 symbol은 `fallback_retries` diagnostics로 남긴다.
- 일봉 macro 해석은 `today_return / rolling_60d_volatility` 표준화 움직임과 252거래일 위치를 사용하며, 채권선물 / FX 선물은 경제적 해석 방향으로 변환해 점수화한다.
- Historical validation은 저장된 daily futures row를 날짜별로 `date <= validation_date` 조건에서 재계산하고, 1D / 5D / 20D forward return과 비교해 과거 일관성, directional sample size, hit rate, false-positive rate, threshold sensitivity, score-forward-return relationship을 요약한다. `Max Adverse`는 해당 forward window의 endpoint가 아니라 window 안의 adverse path move 기준이다.
- Mixed scenario는 risk-on / risk-off 방향으로 강제 분류하지 않는다. 이 경우 현재 scenario history는 occurrence count를 보여주고 directional hit rate는 N/A로 표시한다.
- 비교 target은 futures row가 있으면 futures 자체를 우선 사용하고, 부족하면 `nyse_price_history`의 ETF proxy(`SPY`, `QQQ`, `IWM`, `TLT`, `GLD`, `UUP`)를 labeled fallback으로만 사용한다.

주의:

- 선물 거래 시간은 상품 / 거래소 / 휴장일별로 다르므로 NYSE cash session 상태와 동일하게 해석하지 않는다.
- 무료 provider 기반이라 지연, 누락, rate limit, symbol coverage 변화가 발생할 수 있다.
- `Stale`, `Missing`, `Partial` 상태는 pass가 아니라 provider freshness / coverage gap이다.
- Macro Thermometer는 시장 해석 보조 기능이며 정규장 방향 예측이나 투자 판단 자동화가 아니다.
- Historical validation은 과거 일관성 평가이며 예측 보장이 아니다.
- yfinance continuous futures는 실제 roll / 만기 구조와 다를 수 있고, ETF proxy target은 futures 자체 검증이 아니다.
- 이 table은 투자 신호, 주문, live approval, auto rebalance를 만들지 않는다.

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
- `data-provenance-coverage-v1` 이후 Practical Validation provider context는 `source`, `source_type`, `coverage_status`, `as_of_date`, `collected_at`을 compact provenance로 요약한다.
- `look-through-exposure-board-v1` 이후 Practical Validation provider context는 `etf_holdings_snapshot` / `etf_exposure_snapshot`을 compact look-through board로 접어 asset bucket, top holdings, overlap, ETF별 coverage를 보여준다.
- provider snapshot freshness가 오래됐으면 충분한 coverage라도 `REVIEW`로 남긴다.

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
- QQQ SEC N-PORT/N-30B-2 row는 `cusip`, `isin`, `lei`, `issuer_cik`, `filing_date`, `accession_no`, `holding_snapshot_quality`을 optional evidence로 저장한다. `annual_anchor` / `quarterly_anchor` / `current_issuer_snapshot`은 같은 정밀도의 PIT truth가 아니다.

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
- Practical Validation result JSONL에는 source mix / coverage status weight / stale symbol 같은 compact provenance만 저장하고 full holdings / exposure row는 저장하지 않는다.
- Look-through board도 compact summary / top rows만 저장하며 full holdings / exposure source-of-truth는 이 table들과 DB loader다.

## `macro_series_observation`

역할:

- Practical Validation V2의 market-context 진단에 쓸 macro / sentiment proxy observation 저장
- VIX, yield curve, credit spread, CNN Fear & Greed, AAII sentiment 같은 series를 long-form으로 보존

성격:

- provider snapshot table이다.
- P2-4 초기 구현은 FRED `VIXCLS`, `T10Y3M`, `BAA10Y`를 수집한다.
- Overview Market Sentiment V1 이후 CNN score / component score와 AAII bullish / neutral / bearish / bull-bear spread도 같은 long-form table에 저장한다.
- `series_id`, `observation_date`, `source`가 business key다.
- API key가 있으면 FRED API, 없으면 FRED official CSV download를 사용한다.

주의:

- macro / sentiment는 trade signal, PASS / BLOCKER, monitoring signal이 아니라 기준일의 시장 환경 설명 자료다.
- FRED value는 observation date 기준 데이터이며, 실제 발표 / 수정 vintage point-in-time truth와는 구분해야 한다.
- Practical Validation result JSONL에는 full series를 저장하지 않고 compact snapshot / staleness만 저장하는 방향이다.
- Practical Validation result JSONL에는 source mode / observation range / stale series 같은 compact macro provenance만 저장한다.

## `macro_series_vintage_observation`, `economic_cycle_model_artifact`, `economic_cycle_snapshot`

역할:

- `macro_series_vintage_observation`은 미국 경제 사이클 17개 지표의 발표 당시 값과 이후 revision interval을 raw ledger로 보존한다.
- `economic_cycle_model_artifact`는 model version, `trained_through`, horizon별 parameter·temperature calibration·rolling-origin metric·publication gate를 보존한다.
- `economic_cycle_snapshot`은 current 또는 historical replay가 만든 compact 네 국면 확률, evidence, source date, 제한 사유를 저장하며 Overview read model의 source-of-truth다.

성격과 business key:

- raw vintage key는 `(series_id, observation_date, realtime_start, source)`다. `realtime_end`와 수집 metadata는 같은 key 재수집 때 갱신되며 누락값 row도 `coverage_status=MISSING_VALUE`로 보존한다.
- artifact key는 `(model_version, trained_through)`다. validation metadata가 완전하지 않으면 approved artifact로 승격하지 않으며 기존 latest-good row를 덮지 않는다.
- snapshot key는 `(as_of_date, model_version, run_kind)`다. `run_kind`는 current materialization과 historical replay를 분리하고, 재실행은 같은 business key를 UPSERT한다.

PIT / publication 계약:

- historical origin은 `realtime_start <= origin <= realtime_end`인 version 중 최신 eligible row 하나만 읽는다. 이후 발표·수정값은 관측일이 과거여도 사용할 수 없다.
- feature scaling은 expanding history만, calibration/validation은 rolling-origin out-of-fold만 사용한다. retrospective label은 activity/labor와 해당 origin에 eligible한 `USREC`만 사용한다.
- 각 h0/h1/h2 horizon은 독립적으로 `READY/LIMITED`를 판정한다. 유효한 LIMITED 확률은 reason evidence와 함께 snapshot에 보존하고 UI에서 `잠정 모델 추정`으로 표시한다. READY는 `검증된 모델 추정`이며 phase support·parameter·입력이 불완전한 horizon만 numeric probabilities를 비우고 `판단 불가`로 둔다.
- raw full series, model parameter, 121개월 replay snapshot은 DB에 남고 UI service는 최근 최대 60개월 compact history/evidence만 읽는다. UI render 중 provider fetch, fit, materialization, DB write를 실행하지 않는다.

주의:

- 이 경로는 FRED `series/vintagedates`와 observations API의 long-form `output_type=1`, `FRED_API_KEY`를 요구한다. provider의 요청당 2,000 vintage-date 제한은 실제 vintage date 경계로 분할하며, revised-latest CSV fallback은 historical vintage 증거가 아니므로 허용하지 않는다.
- 국면은 data-defined macro regime이며 NBER 공식 판정, 자산 수익률 예측, 매수·매도 지시가 아니다.

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
- loader source contract에서는 `financial_source=legacy_broad_yfinance`, `financial_source_mode=legacy_broad_summary`로 표시한다.

성격:

- yfinance statement 기반 broad coverage layer
- factor 계산용 중간 table
- strict raw accounting ledger가 아니다
- direct / derived / inferred source metadata를 함께 추적할 수 있다

주의:

- `period_end` 중심이므로 filing-time PIT source로 바로 쓰면 look-ahead risk가 있다.
- filing metadata가 없으므로 source contract alias의 `available_at`, `form_type`, `accession_no`는 비어 있을 수 있다.
- 새 기능의 canonical financial statement source로 추가 사용하지 않는다. 기존 run/history compatibility 또는 explicit fallback label이 있을 때만 사용한다.
- Phase 7 source migration부터 active Ingestion UI에서는 이 table을 채우는 broad financial statement collection card를 제공하지 않는다.

## `nyse_fundamentals_statement`

역할:

- statement ledger 기반 fundamentals shadow
- loader source contract에서는 `financial_source=sec_edgar_statement_shadow`, `financial_source_mode=statement_shadow`로 표시한다.

성격:

- `nyse_financial_statement_values`에서 usable raw rows를 읽어 재구성한 shadow table
- public broad table을 대체하지 않고 비교 / 검증 / strict strategy runtime 용도로 유지한다
- 현재 의미는 각 `period_end`에 대한 earliest usable filing snapshot에 가깝다

주의:

- schema column 이름에 `latest_*`가 남아 있어도, 현재 해석은 period_end별 earliest usable snapshot 쪽으로 읽는다.
- `shares_outstanding`은 statement-derived를 우선하고, 없으면 broad fallback을 사용할 수 있다.
- loader는 `latest_available_at`, `latest_form_type`, `latest_accession_no`를 공통 alias인 `available_at`, `form_type`, `accession_no`로도 노출한다.
- annual은 EDGAR-first migration의 primary source 후보지만, quarterly는 10-K/FY flow-value policy가 고정되기 전까지 blocked/prototype으로 읽는다.
- Phase 3 source migration부터 새 quarterly shadow 생성은 `10-K` / `10-K/A` filing의 full-year flow metrics를 분기 flow로 저장하지 않고 flow column을 비운다. balance sheet instant 항목은 남을 수 있으므로 flow와 instant 해석을 분리한다.
- Phase 3 source migration부터 loader는 quarterly 소비 경로에서 `10-Q` / `10-Q/A` row만 반환한다. 기존 `10-K` / `10-K/A` quarterly row가 table에 남아 있어도 usable quarterly financial row로 보지 않는다.

## `nyse_factors`

역할:

- broad fundamentals와 as-of price를 이용한 derived factor table
- loader source contract에서는 `financial_source=legacy_broad_yfinance`, `financial_source_mode=legacy_broad_factor`로 표시한다.

성격:

- broad research / prototype strategy input 후보
- strict PIT factor store가 아니다
- price attachment metadata와 timing 의미를 함께 저장한다

주의:

- `period_end` 기준 as-of price matching은 유용하지만, filing availability 기준과는 다를 수 있다.
- current workflows should prefer statement annual factor paths. This table remains a legacy broad compatibility layer until decommissioned.
- Phase 7 source migration부터 active Ingestion UI에서는 이 table을 계산하는 broad factor card를 제공하지 않는다. saved/history replay와 explicit broad comparison compatibility는 유지한다.

## `nyse_factors_statement`

역할:

- statement fundamentals shadow와 as-of price를 이용한 derived factor shadow
- loader source contract에서는 `financial_source=sec_edgar_statement_shadow`, `financial_source_mode=statement_factor_shadow`로 표시한다.

성격:

- quality / accounting 계열 strict strategy에 더 적합한 factor layer
- `fundamental_available_at`, `fundamental_accession_no` 같은 metadata를 포함한다
- `Quality Snapshot (Strict Annual)`, `Value Snapshot (Strict Annual)` public fast runtime source로 사용된다

주의:

- shares fallback이 없거나 부족한 row에서는 valuation 계열 factor가 `NULL`일 수 있다.
- loader는 `fundamental_available_at`, `fundamental_accession_no`, joined `latest_form_type`을 공통 alias인 `available_at`, `accession_no`, `form_type`으로도 노출한다.
- annual strict strategies can treat this as the EDGAR-first factor path. Quarterly prototype rows stay non-canonical; Phase 3 source migration gates quarterly factor reads to `10-Q` / `10-Q/A` rows only.

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
- raw value ledger는 10-K/FY fact를 보존할 수 있다. 다만 shadow fundamentals / factors 소비 경로는 full-year flow fact를 quarterly flow metric처럼 쓰지 않도록 별도 policy를 적용한다.
- provider의 `fiscal_year` / `fiscal_period`는 filing context일 수 있으므로, row identity는 `period_end`와 `accession_no`를 우선한다.
- `periods=0` ingestion은 source가 가진 usable history를 최대한 적재하는 의미다.

## `nyse_financial_statement_labels`

역할:

- concept summary와 operator-facing label helper

성격:

- UI / 해석 보조 layer
- strict loader의 source of truth가 아니다.
- 실제 statement value 판단은 `nyse_financial_statement_values`를 중심으로 읽는다.

## `sp500_monthly_valuation`

역할:

- Shiller 월별 SPX price와 interpolated EPS, 계산 가능한 월의 후행 PER/CAPE를 저장한다. EPS 발표가 늦은 최신 월은 price-only row로도 보존한다.
- `observation_month + source` unique key로 재수집을 idempotent UPSERT한다.

주의:

- EPS가 있는 월은 `data_quality=interpolated`, EPS 미발표 price-only 월은 `data_quality=missing`이다. 어느 쪽도 strict historical release timing proof가 아니다.
- 60개월 log(PER) 상대평가, 36개월 민감도, 12개월 reconstructed actual-SPX 비교에 사용한다. 표준편차 band는 신뢰구간이 아니다.
- Market Context graph 2는 공식 actual 4분기 TTM이 없을 때 이 table의 최신 양수 `trailing_eps`를 `interpolated_ttm_proxy`로 선택한다. UI는 이를 S&P 공식 EPS나 애널리스트 컨센서스로 표시하지 않는다.

## `nasdaq100_monthly_valuation`

역할:

- QQQ holdings weight, 구성종목 filing-aware actual diluted EPS, DB EOD를 결합한 monthly QQQ EPS/PER proxy와 coverage evidence를 저장한다.
- `(observation_month, proxy_symbol, source)` key로 READY와 BLOCKED 월을 모두 repeat-safe UPSERT한다.

주의:

- `reconstructed_actual`은 weighted EPS/price coverage 95% 이상인 월만 허용한다. `blocked`는 pass가 아니며 값이 없어도 삭제하지 않는다.
- diluted EPS는 `EarningsPerShareDiluted`, IFRS `DilutedEarningsLossPerShare`, 또는 issuer가 basic/diluted를 동일값으로 공시한 `EarningsPerShareBasicAndDiluted` actual만 허용한다. 별도 basic EPS, FY-only annual proxy, 추정 EPS는 fallback으로 사용하지 않는다.
- QQQ proxy는 공식 Nasdaq-100 index-level P/E/EPS가 아니다. acquired/delisted EOD, ADR/foreign unit, share class가 불명확한 weight는 coverage에 포함하지 않는다.
- 2026-07-13 coverage repair QA는 최근 60개월을 60 READY / 0 BLOCKED로 materialize했다. 이는 local stored-source 검증 결과이며 무료 원천 gap이 남는 환경에서 gate를 우회한다는 뜻이 아니다.

## 미국 개별주식 read-time valuation contract

역할:

- V1은 새 materialization table을 만들지 않는다. 선택된 한 종목의 bounded `nyse_price_history`, `nyse_financial_statement_values`, `fomc_sep_projection` row를 읽어 월말 PIT TTM EPS/PER와 상대가치 시나리오를 계산한다.
- quarterly/FY duration fact는 해당 filing의 primary period만 discrete-period 후보로 사용한다. `report_date == period_end`가 우선 증거이고, report date가 없는 legacy row만 최초 공시로 볼 수 있는 180일 이내 availability fallback을 허용한다.

주의:

- later filing의 prior-year comparative Q/FY fact는 새 quarter identity가 아니며 기존 분기나 FY-derived Q4를 덮어쓰지 않는다.
- split이 있는 회계연도는 raw Q/FY fact를 각 관측 월말 share basis로 먼저 정규화한 뒤 `FY - Q1 - Q2 - Q3`를 계산한다. split effective date 이전 월에는 future split을 적용하지 않는다.
- 월별 EPS를 만들거나 보간하지 않는다. `available_at <= month_end`인 최신 four discrete quarters만 carry-forward하며 positive TTM EPS와 positive month-end price에서만 PER를 계산한다.
- Graph 1의 60개월 positive P/E readiness와 Graph 2의 최소 8개 positive-to-positive TTM EPS 성장 관측은 독립 상태다. 성장 이력 부족은 Graph 2만 BLOCKED하며 계산 가능한 Graph 1을 NOT_APPLICABLE로 낮추지 않는다.

## 미국 개별주식 read-time turnaround contract

역할:

- 새 table을 만들지 않고 선택 종목의 bounded `nyse_financial_statement_values`, `nyse_asset_profile`, `nyse_price_history`, lifecycle identity를 읽어 quarterly operating/cash 전환, survival risk, valuation readiness를 계산한다.
- duration fact와 instant fact는 별도 query/계산 경계다. duration은 direct Q를 우선하고 compatible same-concept/unit/fiscal-year `H1-Q1`, `9M-H1`, `FY-Q1-Q2-Q3`를 먼저 discrete quarter로 복원한다. Missing Q4만 explicit metric concept family 안에서 같은 symbol/fiscal year/unit 및 primary-period/PIT 조건의 FY/Q1/Q2/Q3를 결합할 수 있다.
- revenue, gross profit, operating/net income, OCF, CapEx, FCF proxy, diluted EPS/share를 gap-preserving quarter timeline과 TTM으로 만든다. direct gross profit이 없으면 같은 filing/quarter/unit의 revenue-cost만 fallback으로 허용한다.

주의:

- later comparative fact는 primary quarter를 덮지 못하고 derived quarter의 `available_at`은 operand 중 가장 늦은 공개일이다. direct/exact Q4가 family fallback보다 우선하며 allowlist 밖 concept, 다른 unit/year/symbol, future filing은 결합하지 않는다. missing operand/quarter는 다른 기간으로 대체하거나 보간하지 않는다.
- timeline은 metric별 `source_kind`, rule, operands와 `derived_metrics`, `ttm_derived_metrics`를 read-time payload에 포함한다. `FILING_DERIVED`는 확정 공시의 산술 결과이며 forecast/estimate가 아니다.
- milestone은 sequential pass chain이 아니다. operating improvement, two-consecutive positive TTM OCF, earnings turn, PER handoff를 독립 evidence로 표시한다. runway, debt/interest, split-neutral dilution도 milestone과 별도 risk overlay다.
- numeric valuation은 market cap/price/statement basis가 7일 이내로 정렬되고 USD/unit/sector/denominator 조건을 충족할 때만 허용한다. P/E handoff, P/FCF, P/OCF, EV/EBITDA, EV/Gross Profit, EV/Sales 순서를 사용하며 target price나 매매 신호가 아니다.
- 검색·선택·분석 전환은 provider call 0회다. raw gap 수집은 SEC CIK를 확인한 selected symbol의 explicit action만 가능하다. CIK가 없으면 `BLOCKED/CIK_MISSING`으로 수집을 막되 저장 facts로 만든 READY 분석은 유지한다.

## `sp500_index_earnings`

역할:

- S&P index EPS를 `period_end`, `period_type`, `earnings_basis`, `value_status`, `source_release_date`로 보존한다.
- 동일 period라도 release vintage가 다르면 별도 row로 유지한다.

주의:

- Market Context TTM actual은 최신 네 개의 distinct `quarterly + as_reported + actual` row만 합산한다.
- Economic Cycle의 실제 EPS 경로는 서로 다른 완료 분기 8개가 있어야 current/prior TTM과 전년 대비 변화를 계산한다. 이 경로에는 Shiller proxy를 넣지 않는다.
- `estimate` 또는 `mixed` row는 actual 부족을 채우는 fallback이 아니다.
- Ingestion importer는 공식 `QUARTERLY DATA` 제목과 `QUARTER END`, `OPERATING EARNINGS PER SHR`, `AS REPORTED EARNINGS PER SHR` 다단 머리글을 함께 검증한다. 공식 시트에서 값이 있는 완료 분기는 actual로 읽고 빈 최신 분기는 저장하지 않는다. normalized 호환 파일은 explicit status column을 요구한다.
- 모든 read-as-of는 `period_end`뿐 아니라 `source_release_date`도 기준일 이하인 release vintage만 사용한다. 같은 분기 여러 vintage 중 당시 알려진 최신 row를 선택한다.

## `fomc_sep_projection`

역할:

- Federal Reserve SEP real GDP / PCE inflation을 `release_date`, `target_year`, `statistic_name`별로 저장한다.
- median과 central-tendency lower/upper endpoint를 분리해 보존한다.

주의:

- 새 SEP는 새 release vintage로 저장하며 이전 release를 덮어쓰지 않는다.
- bounded history collector는 2025-06 이후 공식 release 중 DB에 없는 vintage만 가져오고, daily latest collector가 이후 release를 보존한다.
- 월별 reconstruction은 월중 발표 vintage를 다음 달부터 적용하고 관측 월 calendar year의 target row를 선택한다. 최신 EOD 지점은 기준일 이전 최신 release를 적용한다.
- central-tendency endpoint 조합은 sensitivity scenario이지 participant joint distribution이나 confidence interval이 아니다.
- latest SPX 기준일보다 release가 180일 넘게 오래되면 UI scenario는 `STALE_SEP`로 차단한다.
