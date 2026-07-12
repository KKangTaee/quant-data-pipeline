# Finance Data Map

Status: Active
Last Verified: 2026-07-08

## Purpose

이 폴더는 finance 프로젝트의 데이터 흐름, DB 구조, table 의미, 데이터 품질 / PIT 주의사항을 관리한다.

상위 제품 / 코드 지도는 `docs/PROJECT_MAP.md`에 두고, DB와 데이터 의미의 상세 기준은 이 폴더에서 관리한다.

## Read Order

| 상황 | 먼저 볼 문서 |
|---|---|
| 데이터가 어디서 와서 어디로 저장되는지 확인 | [DATA_FLOW_MAP.md](./DATA_FLOW_MAP.md) |
| DB / JSONL / saved setup / run artifact 저장 경계 확인 | [STORAGE_GOVERNANCE.md](./STORAGE_GOVERNANCE.md) |
| UI / service / runtime / loader / storage 경계가 헷갈릴 때 | [System Boundaries](../architecture/SYSTEM_BOUNDARIES.md) |
| DB와 table 목록을 빠르게 확인 | [DB_SCHEMA_MAP.md](./DB_SCHEMA_MAP.md) |
| table별 source / derived / shadow / provider snapshot 의미 확인 | [TABLE_SEMANTICS.md](./TABLE_SEMANTICS.md) |
| PIT, look-ahead, survivorship, stale data 위험 확인 | [DATA_QUALITY_AND_PIT_NOTES.md](./DATA_QUALITY_AND_PIT_NOTES.md) |

## Database Groups

| DB | Role |
|---|---|
| `finance_meta` | universe, asset profile, ETF provider snapshot, macro / sentiment context, event calendar, market data issue |
| `finance_price` | OHLCV / dividend / split price history, intraday snapshot, futures OHLCV |
| `finance_fundamental` | fundamentals, financial statements, derived factors |

## Key Tables

| Table | Meaning |
|---|---|
| `nyse_stock` | NYSE stock listing master |
| `nyse_etf` | NYSE ETF listing master |
| `nyse_symbol_lifecycle` | symbol lifecycle / historical universe / delisting evidence table. SEC Form 25 collector가 official delisting evidence를 저장할 수 있다 |
| `nyse_asset_profile` | stock / ETF profile and bridge metadata |
| `equity_universe_snapshot` | Quality / Value strict family가 읽는 prebuilt monthly PIT-like equity universe snapshot header. V1은 DB price와 latest-known statement shares 기반 근사 market-cap universe다 |
| `equity_universe_member` | monthly equity universe snapshot별 included / excluded member, rank, approximate market cap, liquidity / exclusion evidence |
| `nyse_price_history` | OHLCV price ledger |
| `market_universe_member` | Overview market intelligence current universe membership |
| `market_liquidity_universe_member` | Market Movers Top1000 / Top2000 current membership materialized from recent average dollar volume |
| `market_symbol_alias` | Market Movers ticker-change repair alias store. Quote-missing old tickers can be detected as candidates, then explicitly applied as active aliases for future intraday quote lookup |
| `market_intraday_snapshot` | Overview daily market movers and sector/group leadership intraday previous-close snapshot for S&P 500 / Top1000 / Top2000 / Nasdaq-listed current snapshot coverage. Current UI reads this through Market Movers / Market Context, not a standalone Sector / Industry primary tab |
| `market_data_issue` | Overview quote gap 같은 반복 market data issue를 symbol / universe 단위로 누적 추적 |
| `market_event_calendar` | Overview Events calendar snapshot for FOMC, macro releases, earnings, market-structure events, fixed-income calendar events, and corporate-action candidates. Rows use normalized taxonomy fields such as `event_family`, `event_subtype`, `universe_scope`, and `source_authority`; macro/FOMC/Treasury rows are official schedule context, while earnings rows remain provider estimates unless issuer/official confirmation is stored. |
| `sp500_monthly_valuation` | Shiller monthly price/EPS-derived trailing P/E and CAPE history. `data_quality=interpolated`; descriptive 60m/36m valuation zones only, not strict PIT signal history. |
| `sp500_index_earnings` | S&P index EPS by period/basis/status/release vintage. Four distinct completed `quarterly + as_reported + actual` rows are the preferred graph 2 EPS source; their absence no longer blocks the graph because the loader can select the latest Shiller TTM proxy. |
| `fomc_sep_projection` | Federal Reserve SEP GDP/PCE values stored by release vintage, target year, and statistic. New releases append by `release_date`; prior vintages are not overwritten. |
| `futures_instrument` | Overview futures watchlist preset / display metadata for yfinance pilot futures symbols |
| `futures_ohlcv` | Overview futures 1m / daily OHLCV candle ledger for selected futures symbols. 1m rows support stored-candle chart / diagnostics; daily rows feed Futures Macro current scores and point-in-time historical validation |
| `futures_market_monitor_run` | Futures OHLCV collection run diagnostics, latest candle, failed symbols, and provider status |
| `etf_provider_source_map` | ETF별 issuer endpoint / parser mapping cache |
| `etf_operability_snapshot` | ETF 비용, 규모, 유동성, spread, NAV 관련 snapshot |
| `etf_holdings_snapshot` | ETF holdings row snapshot |
| `etf_exposure_snapshot` | holdings 또는 provider aggregate 기반 exposure summary |
| `macro_series_observation` | FRED VIX / yield curve / credit spread observation plus Overview CNN Fear & Greed / AAII sentiment context series |
| `nyse_financial_statement_filings` | EDGAR filing-level metadata ledger |
| `nyse_financial_statement_values` | EDGAR filing / concept / period raw fact ledger |
| `nyse_fundamentals_statement` | EDGAR statement ledger 기반 canonical financial statement shadow |
| `nyse_factors_statement` | EDGAR statement shadow 기반 canonical strict annual factor source |
| `nyse_fundamentals` | legacy broad yfinance compatibility fundamentals summary |
| `nyse_factors` | legacy broad yfinance compatibility factor table |
| `practical_validation_stress_windows_v1.json` | Practical Validation static stress window reference data. JSON reference file이며 DB table은 아님 |

## Financial Statement Source Contract

- Canonical financial statement source path: `EDGAR -> nyse_financial_statement_* raw ledger -> nyse_fundamentals_statement -> nyse_factors_statement`.
- Legacy compatibility path: `yfinance financial statements -> nyse_fundamentals -> nyse_factors`.
- New Market Movers annual financial snapshots and strict annual factor backtests should prefer the EDGAR statement shadow path.
- The legacy broad path remains for saved/history replay and explicit broad comparison only. It is not a production financial statement source.
- Quarterly consumer paths must not treat `10-K` / FY full-year flow values as quarterly values. Quarterly reads are gated to `10-Q` / `10-Q/A` rows.
- Market Movers 기본 지표 can compare `nyse_financial_statement_filings` latest 10-Q / 10-K report dates with statement shadow `period_end` to show whether a filed statement is not yet reflected. When the UI offers selected-symbol collection from the SEC filing tab, it must route through `app/jobs/overview_actions.py` to the existing Ingestion EDGAR statement refresh job rather than fetching directly during render.

## JSONL Boundaries

| File / Folder | Meaning | Policy |
|---|---|---|
| `.aiworkspace/note/finance/registries/` | workflow decision / source registry | 보존 대상. 명시 요청 없이 재작성하지 않음. 새 파일 추가 전 [Storage Governance](./STORAGE_GOVERNANCE.md) checklist 확인 |
| `.aiworkspace/note/finance/saved/` | reusable saved portfolio setup | 사용자가 명시적으로 저장한 setup. validation / final decision evidence가 아님. `SELECTED_DASHBOARD_PORTFOLIOS.jsonl`은 dashboard portfolio setup |
| `.aiworkspace/note/finance/run_history/` | local run history | 장기 문서 아님. 투자 판단 source-of-truth가 아니며 보통 커밋하지 않음 |
| `.aiworkspace/note/finance/run_artifacts/` | local runtime artifact | 장기 문서 아님. 보통 커밋하지 않음 |

앱 코드는 이 위치들을 `app/workspace_paths.py`의 canonical path 상수로 읽는다.
새 registry / saved / run-history helper를 만들 때는 `.note/finance` 경로를 직접 만들지 않는다.
runtime-defined JSONL 파일은 첫 workflow write 전에는 로컬에 없을 수 있으며, 파일 부재 자체는 저장 경계 drift가 아니다.

## Data Integrity Rules

- 백테스트와 validation에서는 point-in-time, look-ahead, survivorship risk를 항상 고려한다.
- provider field는 안정적이거나 완전하다고 가정하지 않는다.
- Market Movers Top1000 / Top2000은 `nyse_asset_profile.market_cap` 순위가 아니라 `nyse_price_history`의 최근 20거래일 평균 거래대금 기준이다. 따라서 "가장 큰 기업" 순위가 아니라 "최근 거래대금이 큰 종목" 순위이며, current listing source와 최신 EOD 가격 row가 모두 필요하다.
- Market Movers ticker-change repair는 `market_symbol_alias`에 candidate / active alias를 저장한다. Active alias는 quote lookup symbol만 바꾸며, universe membership symbol 자체를 자동 변경하지 않는다.
- official row가 partial이면 DB bridge와 병합하되 source origin을 숨기지 않는다.
- Practical Validation JSONL에는 compact evidence와 reason만 저장하고, full provider raw data는 DB에 둔다.
- CNN / AAII sentiment, futures macro thermometer, Why It Moved metadata는 market context / investigation evidence이며 자동 trade signal, validation approval, monitoring signal로 저장하지 않는다.
- Market Movers `시장 관심`은 selected-symbol investigation evidence only다. V2는 existing selected-symbol news / Korean news / SEC metadata fetchers를 사용자 버튼 클릭 시 세션 전용으로 호출하고, analyst / target-change pages와 SEC 13F references는 source disclosure 또는 delayed context로 다룬다. Article body, analyst report body, filing body, commercial source content, or 13F holdings rows를 저장하지 않는다.
- 13F는 official SEC source 후보지만 분기 지연 자료이며 quarter-end 이후 최대 45일 늦게 제출될 수 있다. 숏 포지션, 파생, 헤지, 실시간 거래 의도는 완전히 보여주지 않으며, reliable selected-symbol lookup은 CUSIP-symbol mapping / quarter comparison design 승인 후 별도 DB ingestion으로 다룬다.
- 새 JSONL registry는 기본적으로 만들지 않고, stage handoff나 명시적 reusable setup이 아닌 저장은 피한다.
- static stress window JSON은 투자 신호가 아니라 재현 가능한 검증 preset이다.
- Operations > Portfolio Monitoring read model은 monitoring log 자동 저장, live approval, broker order, account sync, auto rebalance를 수행하지 않는다. legacy `Selected Portfolio Dashboard` file/helper 이름은 남아 있지만 사용자 portfolio setup은 saved state로만 관리한다.

## Code Flow 문서와의 차이

- `docs/data/`는 데이터가 어떤 의미를 갖고 어디에 저장되는지 보는 data / DB 의미 문서다.
- `docs/architecture/`는 코드를 어떻게 따라가고 수정할지 보는 개발자 flow 문서다.
- layer ownership이나 product-surface 경계는 [System Boundaries](../architecture/SYSTEM_BOUNDARIES.md)를 먼저 본다.

예를 들어 새 loader 함수를 고칠 때는 `docs/architecture/DATA_DB_PIPELINE_FLOW.md`를 먼저 보고, 그 loader가 읽는 table의 의미를 확인할 때는 이 폴더의 [TABLE_SEMANTICS.md](./TABLE_SEMANTICS.md)를 본다.

## 갱신해야 하는 경우

- 새 DB table / column이 추가될 때
- table의 source / derived / shadow / convenience 성격이 바뀔 때
- ingestion source가 바뀔 때
- loader가 source of truth를 바꿀 때
- PIT 기준, filing timing, period_end 의미가 바뀔 때
- provider coverage, stale data, survivorship risk 해석이 바뀔 때
- financial statement canonical source, legacy compatibility status, or quarterly PIT policy가 바뀔 때

## 갱신하지 않아도 되는 경우

- 단순 UI 문구 변경
- 일회성 backtest 결과
- phase status 변경
- 코드 내부 리팩터링이 table 의미나 데이터 흐름을 바꾸지 않는 경우

## Source Of Truth

schema의 실제 정의는 코드가 기준이다.

- `finance/data/db/schema.py`

이 폴더는 schema SQL을 그대로 복제하는 곳이 아니라, 사람과 agent가 데이터 의미를 빠르게 이해하도록 돕는 해석 지도다.
