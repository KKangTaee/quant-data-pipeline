# Overview Market Context US Stock Valuation V1 Design

Status: Approved in Conversation — Written Spec Review Requested
Last Updated: 2026-07-14

## 이걸 하는 이유?

Nasdaq-100 가치평가를 무료·무계정 QQQ proxy로 재구성하려면 과거 구성종목, 상장폐지·합병 종목, 구성종목별 월말 가격과 filing-aware EPS를 함께 복원해야 한다. 현재 구조는 과거 QQQ SEC holdings를 보유하지만 상장폐지 EOD와 일부 foreign issuer EPS를 무료 원천만으로 완전히 닫지 못한다. 사용자는 Nasdaq의 높은 변동성과 proxy 데이터 한계를 고려할 때 이 적정가 기능의 우선순위가 낮다고 판단했다.

미국 개별주식은 선택 기업 하나의 가격과 SEC 공시만 사용하므로 과거 index membership과 portfolio coverage 문제가 사라진다. 현재 프로젝트에는 미국 주식 가격, SEC detailed statement, ticker/CIK lifecycle, FOMC SEP history, S&P/Nasdaq 가치평가 React surface가 이미 있다. 이 자산을 재사용해 더 직접적이고 설명 가능한 상대가치 평가 흐름을 만든다.

## Decision Summary

- `S&P 500 | Nasdaq-100` 선택을 `S&P 500 | 미국 개별주식`으로 바꾼다.
- 미국 개별주식 화면 상단에 기업명·티커 검색을 둔다.
- 검색은 DB의 current listing/CIK evidence만 읽고 외부 provider를 호출하지 않는다.
- 선택 기업의 기존 DB 가격과 SEC 분기 실적으로 월별 point-in-time TTM EPS와 PER를 bounded 계산한다.
- Graph 1은 기존 60개월 log(PER) 구간과 36개월 민감도 표현을 유지한다.
- Graph 2는 FOMC GDP·PCE만 기업 EPS에 직접 대입하지 않고, `FOMC 거시 기준 + 기업 초과 EPS 성장률` 하이브리드를 사용한다.
- 부족한 price/SEC raw data는 사용자가 선택 기업 전용 action을 눌렀을 때만 동기 수집한다.
- 적자·상장기간 부족·PER 부적합은 collection failure와 구분하며 값을 합성하지 않는다.
- 기존 Nasdaq DB·collector·historical data는 삭제하지 않고 user-facing selector/action 연결만 제거한다.

## Approaches Considered

### A. FOMC + 기업 초과 EPS 성장 하이브리드 — Selected

FOMC SEP의 실질 GDP와 PCE를 현재 거시 기준으로 두고, 기업이 과거 거시 전망 대비 기록한 TTM EPS 초과성장 분포를 더한다. 경기 환경과 기업별 실적 특성을 모두 반영하며, 같은 거시 성장률을 모든 기업에 적용하는 문제를 피한다.

### B. FOMC GDP + PCE만 직접 적용 — Rejected

현재 지수 시나리오와 구현 재사용성이 가장 높다. 그러나 SEP는 미국 경제 전체의 GDP·물가 전망이며 기업별 매출 구성, 해외 노출, 마진, 희석, 자사주 매입, 업황을 설명하지 않는다. NVDA와 성숙 소비재 기업에 같은 EPS 성장률을 적용하는 결과가 되어 개별주 화면의 핵심 가치를 훼손한다.

### C. 기업의 최근 EPS 성장만 적용 — Rejected

기업 특성은 반영하지만 경기 변화와 현재 FOMC 전망을 무시한다. 최근 일회성 이익 급증·감소를 미래 성장률로 그대로 연장할 위험도 크다.

### D. 애널리스트 consensus EPS — Deferred

기업별 forward EPS에는 적합하지만 안정적인 장기 history, 계정, license, revision provenance가 필요하다. 무료·무계정 V1 범위에서는 사용하지 않는다.

## User Flow

```text
Market Context
  -> 미국 개별주식 선택
  -> 기업명 또는 티커 검색
  -> current common-stock 후보 선택
  -> DB 가격·SEC EPS readiness 확인
      -> READY: Graph 1·2 표시
      -> COLLECTABLE: 가치평가 자료 수집 action
          -> 선택 symbol 가격 수집
          -> 선택 CIK SEC 재무제표 수집
          -> cache clear + rerun
          -> READY 또는 정확한 잔여 상태
      -> NOT_APPLICABLE: 적자/상장기간/PER 부적합 이유 표시
      -> ERROR: 기존 자료 유지 + 오류 안내
```

검색만으로 외부 데이터를 호출하지 않는다. 수집은 사용자의 명시 action에서만 실행하며, 현재 Nasdaq repair에서 사용한 synchronous wait, progress, nonce 중복 방지 패턴을 재사용한다.

## Search Universe

V1 검색 대상은 DB에서 current active listing으로 확인되고 SEC CIK를 연결할 수 있는 NYSE, Nasdaq, NYSE American 보통주다.

- 포함: operating-company common stock
- 제외: ETF, mutual fund, preferred stock, warrant, unit, right
- ADR/foreign issuer: USD/share diluted EPS와 거래 증권 단위가 검증될 때만 READY
- REIT 등 PER가 핵심 평가 지표가 아닌 유형: 결과를 숨기지는 않되 evidence limitation을 명시하고 향후 P/FFO 확장 대상으로 둔다
- delisted/inactive symbol: V1 검색 기본값에서 제외

## Monthly Point-In-Time TTM EPS

기업은 월별 EPS를 발표하지 않는다. 월별 series는 월말까지 실제 공개된 최신 분기 실적을 carry-forward해 만든다.

```text
TTM diluted EPS at month M
  = latest four discrete diluted-EPS quarters
    whose filing available_at <= month-end M

monthly P/E at month M
  = positive month-end raw close / positive TTM diluted EPS at month M
```

- EPS는 분기 filing 이후에만 갱신되는 계단형 series다.
- filing 사이 월은 같은 TTM EPS를 유지하며 EPS를 월별 보간하지 않는다.
- 10-K FY fact에서 Q4를 역산할 때 true fiscal year-end만 사용한다.
- comparative FY fact를 별도 Q4로 오인하지 않는다.
- diluted EPS와 raw price의 per-share 단위를 일치시킨다.
- split 구간의 price return/비교에는 cumulative split factor를 반영한다.
- 현재 TTM EPS가 0 이하이면 current P/E와 가격 시나리오를 계산하지 않는다.

기존 `derive_filing_aware_ttm_eps()`의 comparative FY 처리와 raw-close drift 문제는 shared correctness prerequisite다. 이 오류를 수정하고 real-like regression fixture로 고정하기 전에는 개별주 valuation을 READY로 승격하지 않는다.

## Graph 1 — Recent Five-Year Multiple Regime

- 최근 60개월의 complete, finite, positive monthly P/E가 필요하다.
- log(P/E)의 중심과 ±1σ, ±2σ anchor를 계산한다.
- current price와 latest filing-aware TTM EPS로 current provisional P/E를 표시한다.
- 최근 36개월 분포를 sensitivity로 계산해 3년·5년 판정 차이를 표시한다.
- 60개월 중 음수 EPS나 price/filing gap이 있으면 missing month를 다른 달로 대체하지 않는다.
- current EPS가 음수이면 `PER로 평가할 수 없는 적자 상태`를 표시한다.

Graph 1은 `절대 내재가치`가 아니라 `선택 기업 자신의 최근 역사 대비 상대적 멀티플 위치`다.

## Graph 2 — Macro-Anchored Company EPS Scenario

### Inputs

- latest positive filing-aware TTM diluted EPS
- latest applicable FOMC SEP real GDP median
- latest applicable FOMC SEP PCE inflation median
- latest 60-month P/E distribution anchors
- at least 8 distinct quarterly TTM EPS year-over-year growth observations from the recent three years
- the SEP vintage that was available at each historical quarterly EPS observation

`real GDP + PCE`는 정확한 nominal GDP 산식이 아니라 현재 제품에서 사용하는 nominal-demand proxy다. PCE는 미국 소비자가 구매하는 상품·서비스의 가격지표이며 기업별 profit forecast가 아니라는 한계를 화면에 명시한다.

References:

- Federal Reserve SEP: https://www.federalreserve.gov/faqs/summary-economic-projections-sep.htm
- BEA PCE Price Index: https://www.bea.gov/data/personal-consumption-expenditures-price-index

### Company Excess Growth

각 distinct quarterly TTM observation에서 다음을 계산한다.

```text
company_yoy_growth_q
  = TTM_EPS_q / TTM_EPS_q-4 - 1

macro_baseline_q
  = applicable SEP real_GDP_q + applicable SEP PCE_q

company_excess_growth_q
  = company_yoy_growth_q - macro_baseline_q
```

positive-to-positive EPS 비교만 성장 분포에 사용한다. 적자에서 흑자로 전환한 무한대성 성장률이나 흑자에서 적자로 전환한 비율은 percentile 입력에서 제외하고 별도 regime evidence로 남긴다.

최근 3년 excess observations는 Tukey fence(`Q1 - 1.5*IQR`, `Q3 + 1.5*IQR`)로 clip한 뒤 P25/P50/P75를 계산한다. 자료를 삭제하지 않고 extreme influence만 제한한다.

### Current Scenarios

```text
current_macro = latest SEP real GDP + latest SEP PCE

conservative_growth = current_macro + P25(company_excess_growth)
baseline_growth     = current_macro + P50(company_excess_growth)
optimistic_growth   = current_macro + P75(company_excess_growth)

projected_EPS_s = current_TTM_EPS * (1 + growth_s)
```

예상 EPS가 0 이하가 되는 scenario는 price를 계산하지 않고 downside-invalid evidence로 표시한다.

```text
conservative_price = conservative_projected_EPS * minus_1_sigma_PE
baseline_price     = baseline_projected_EPS     * center_PE
optimistic_price   = optimistic_projected_EPS   * plus_1_sigma_PE
```

보수·기준·낙관 가격은 analyst target이 아니라 `macro-anchored reconstructed scenario`다. Graph 2 title/copy에서 `적정가`보다 `상대가치 시나리오`를 우선하며 공식 목표가격·매매 신호로 표현하지 않는다.

## Historical 1Y / 3Y / 5Y Scenario

- 각 historical month는 그 월말까지 공개된 SEC filing과 당시 사용 가능했던 SEP vintage만 사용한다.
- future filing, future ticker mapping, future SEP를 소급하지 않는다.
- 각 월의 60개월 rolling P/E anchor와 당시 latest TTM EPS/excess-growth distribution을 다시 계산한다.
- 1/3/5년 visible history는 각각 12/36/60개 monthly slot을 유지한다. 모든 slot이 계산 가능하면 `READY`, 두 개 이상의 계산 가능한 point가 있으면 `PARTIAL`, 그보다 적으면 `INSUFFICIENT_HISTORY`다.
- `PARTIAL`은 계산 가능한 월만 원래 시간축 위치에 표시한다. non-positive TTM EPS, rolling warmup, filing/SEP 근거 부족 등 계산 불가 월은 명시적 gap으로 남기고 앞뒤 point를 연결하거나 보간하지 않는다.
- UI는 `계산 가능 개월/선택 개월`, 누락 개월 수, 누락 사유를 함께 표시해 shorter series를 완전한 3년/5년 이력처럼 오인하지 않게 한다.
- 5년 visible history의 최대 warmup은 기존과 같이 119개월 monthly P/E history이며, selected issuer EPS history도 같은 시작 범위를 충족해야 한다.
- 신규 상장 등 구조적으로 main 60개월 P/E 자체를 만들 수 없으면 기존 `NOT_APPLICABLE` 계약을 유지한다. 현재 main screen이 READY인 종목의 historical option만 `PARTIAL` 표시 대상이다.

## Readiness Contract

### NOT_SELECTED

- 아직 기업을 선택하지 않았다.
- 검색 안내만 표시하고 valuation 계산이나 수집을 실행하지 않는다.

### READY

- current listing/CIK identity가 확정됐다.
- current price와 positive TTM diluted EPS가 있다.
- Graph 1에는 최근 60개월 complete positive P/E가 있다.
- Graph 2에는 최소 8개 distinct quarterly positive-to-positive TTM EPS YoY observation과 applicable SEP evidence가 있다.

### COLLECTABLE

- identity는 확정됐지만 DB price 또는 SEC filing raw data가 부족하다.
- selected-symbol action으로 보강할 수 있다.
- missing price/EPS range와 requested collection scope를 표시한다.

### NOT_APPLICABLE

- current TTM EPS가 0 이하이다.
- 상장기간이 선택 기간보다 짧고 외부 수집으로 해결할 수 없다.
- ETF/fund/preferred/warrant 등 V1 instrument 범위가 아니다.
- ADR ratio/unit 불일치 등으로 per-share identity를 검증할 수 없다.
- 수집 버튼을 표시하지 않고 이유와 가능한 대체 지표 방향만 설명한다.

### ERROR

- DB query, calculation, schema contract 또는 action execution 오류다.
- 자동 재수집하지 않으며 기존 S&P model과 마지막 저장 화면을 보존한다.

## Architecture And Ownership

```text
MarketContextValuation.tsx
  -> instrument = sp500 | us_stock
  -> selected stock search event/state
  -> market_context_helpers.py
  -> market_context_valuation.py combined read model
  -> us_stock_valuation.py service
  -> finance/loaders/us_stock_valuation.py
       -> finance_meta.nyse_symbol_lifecycle
       -> finance_price.nyse_price_history
       -> finance_fundamental.nyse_financial_statement_values
       -> finance_meta.fomc_sep_projection
  -> finance/data/us_stock_valuation.py pure bounded calculation
  -> JSON-safe valuation model
  -> React graph or actionable state
```

Probable owners:

- Modify: `app/services/overview/market_context_valuation.py`
- Add: `app/services/overview/us_stock_valuation.py`
- Add: `finance/loaders/us_stock_valuation.py`
- Add: `finance/data/us_stock_valuation.py`
- Modify: `app/jobs/ingestion_jobs.py`
- Modify: `app/jobs/overview_actions.py`
- Modify: `app/web/overview/market_context_helpers.py`
- Modify: `app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx`
- Modify: component CSS/types/tests and focused Python tests

### No New Valuation Table In V1

모든 미국 종목을 미리 materialize하지 않는다. 선택된 한 symbol에 대해 loader가 최대 119개월 valuation window의 price/SEP raw rows와, 첫 observation의 four-quarter TTM을 만들기 위한 최대 18개월 추가 statement lookback을 읽는다. pure calculator는 이 bounded input으로 monthly model을 만든다.

- search/render는 DB read-only다.
- remote fetch는 explicit collection action에서만 발생한다.
- one-symbol bounded calculation으로 precompute/storage 복잡도를 피한다.
- statement lookback은 valuation observation으로 노출하지 않고 첫 월의 filing-aware TTM 구성에만 사용한다.
- actual performance가 기준을 넘을 때만 후속 cache/materialized table을 검토한다.

## Collection Action

`COLLECTABLE` 상태에서만 `가치평가 자료 수집` action을 제공한다.

1. selected symbol/CIK와 missing range를 preflight한다.
2. canonical OHLCV collector로 필요한 price range만 수집한다.
3. canonical SEC detailed-statement collector로 selected CIK를 수집한다.
4. 성공 raw rows를 기존 DB business key로 저장한다.
5. read-model cache를 clear하고 rerun한다.
6. READY, remaining COLLECTABLE, 또는 NOT_APPLICABLE 상태를 다시 계산한다.

부분 성공 row는 보존하고 재실행은 이미 충족된 범위를 제외한다. collection 자체가 경제적 적자나 listing age를 해결할 수 있다고 표시하지 않는다.

## React Surface

- top selector: `S&P 500 | 미국 개별주식`
- stock selector 안에서 기업명·ticker 검색
- selection summary: ticker, company name, exchange, latest price date, EPS basis date
- Graph 1: 기존 chart visual grammar 재사용
- Graph 2: metrics를 `현재 TTM EPS / FOMC 거시 기준 / 기업 초과성장 / 예상 EPS`로 일반화
- history selector: 1년 / 3년 / 5년
- evidence details: price, SEC filing, SEP vintage, formula, limitations
- Nasdaq-specific coverage copy/action/result 제거
- S&P screen/output은 변경하지 않는다.

## Five-Stage Implementation Roadmap

### 1차 — Calculation Correctness

- comparative FY -> false Q4 regression
- true fiscal year-end Q4 derivation
- split-neutral price/EPS unit contract
- monthly TTM carry-forward and no-look-ahead fixtures

Completion: real-like AAPL/AMZN/NVDA statement fixtures and split fixture pass without changing S&P READY output.

### 2차 — US Stock Valuation Engine

- selected-symbol loaders
- monthly PIT TTM EPS/P-E calculator
- Graph 1 log multiple regime
- macro-anchored excess growth and Graph 2 scenarios
- readiness classifier

Completion: pure/service tests cover READY, negative EPS, short listing, missing data, outlier growth.

### 3차 — Search And Collection

- current common-stock search
- selected identity/CIK handoff
- exact missing-range preflight
- synchronous selected-symbol price/SEC action
- resume/idempotency/result contract

Completion: search never fetches remotely; explicit action persists raw data and rerun narrows the gap.

### 4차 — Nasdaq-To-Stock UI Replacement

- combined instrument contract `nasdaq100 -> us_stock`
- ticker/company search UI
- generic Graph 1/2 copy and stock evidence
- NOT_SELECTED/COLLECTABLE/NOT_APPLICABLE/ERROR states
- 1/3/5 history and pending/retry UX

Completion: S&P remains byte-contract compatible at the service boundary and stock UI renders without Nasdaq copy.

### 5차 — Actual QA, Docs, Commit

- actual DB AAPL/NVDA/META/TSLA smoke
- negative EPS, recent IPO, split, missing SEC case
- focused/full regression and React build
- desktop/420px Browser QA, console/overflow
- task/docs/root handoff sync
- coherent implementation commit

Completion: evidence-backed READY/non-READY behavior, screenshot outside repo, unrelated untracked folder untouched.

## Test Strategy

### Pure Calculation

- no future filing is used before `available_at`
- reported Q plus true FY-derived Q4 creates exactly four discrete quarters
- comparative FY rows do not create duplicate Q4
- EPS carries forward between filings without interpolation
- split does not create artificial P/E discontinuity
- negative/zero EPS never produces P/E or log value
- Tukey clipping and P25/P50/P75 scenario outputs are deterministic
- insufficient distinct quarterly observations blocks Graph 2 only

### Loader / Service

- symbol search excludes non-common instruments and inactive symbols
- selected identity maps ticker/name/exchange/CIK deterministically
- query window is bounded and parameterized
- missing price versus missing filing is distinguished
- S&P isolated builder remains available if stock builder fails
- schema is JSON-safe and contains explicit source/basis dates

### Action

- search and render paths make no provider call
- explicit action passes one symbol/CIK and exact missing range
- partial success persists and retry is idempotent
- NOT_APPLICABLE never exposes a misleading collection action

### UI / Browser

- selector contains S&P 500 and 미국 개별주식 only
- empty search, READY, COLLECTABLE, NOT_APPLICABLE, ERROR render correctly
- stock labels replace SPX/QQQ hardcoding
- keyboard search, selection, pending, retry, responsive layout
- S&P desktop/mobile output and console remain regression-free

## Success Criteria

- 사용자는 기업명 또는 ticker로 current U.S. common stock을 선택할 수 있다.
- 선택 기업은 월별 보간이 아닌 quarterly filing-aware TTM EPS carry-forward로 monthly P/E를 계산한다.
- Graph 1은 60 complete positive months가 있을 때만 상대 멀티플 구간을 표시한다.
- Graph 2는 FOMC macro와 기업의 historical excess EPS growth를 분리·결합해 보수/기준/낙관 scenario를 표시한다.
- 결과는 공식 목표가격·내재가치·매매 신호로 표현되지 않는다.
- missing raw data와 intrinsic NOT_APPLICABLE을 구분한다.
- 검색/탭 진입은 read-only이고 remote collection은 명시 action에서만 실행된다.
- 기존 S&P 500 valuation은 회귀하지 않는다.
- 기존 Nasdaq raw DB와 collector는 삭제하지 않는다.
- unrelated untracked files와 generated artifacts는 stage/commit하지 않는다.

## Out Of Scope

- analyst consensus EPS provider
- DCF, dividend discount, residual-income valuation
- P/S, EV/EBITDA, P/FCF, REIT P/FFO fallback
- ETF/fund valuation
- delisted company search
- broker order, target-price alert, auto trading
- background queue/daemon
- all-U.S.-stocks precomputation
- existing Nasdaq raw data/schema destructive cleanup

## 2026-07-15 Comparative-Quarter Correctness Repair Addendum

### 이걸 하는 이유?

AMD actual DB 진단에서 raw 가격·SEC EPS·SEP evidence는 충분했지만 후속 10-Q의 전년도 comparative quarter가 원 공시 quarter를 대체했다. Provider `fiscal_year`는 filing context일 수 있는데 resolver가 이를 actual fiscal-period identity로 사용하면서 FY-derived Q4가 후속 filing마다 바뀌었다. 그 결과 AMD의 최근 3년 growth observation이 7개로 축소되고, Graph 1이 READY인데도 전체 화면이 NOT_APPLICABLE로 차단됐다.

### Approved Repair Contract

- DB schema와 raw statement rows는 변경하거나 재수집하지 않는다.
- Direct Q/FY fact는 `report_date == period_end`를 primary proof로 사용한다. `report_date`가 없는 legacy row만 `available_at - period_end` 0~180일 fallback을 허용한다.
- Later filing의 comparative Q/FY fact는 원 공시 period identity를 덮어쓰거나 다른 fiscal year의 Q1/Q2/Q3로 참여하지 않는다.
- Split이 fiscal year 중간에 있으면 Q1/Q2/Q3와 FY fact를 해당 valuation month-end의 동일 share basis로 먼저 정규화한 뒤 Q4를 `FY - Q1 - Q2 - Q3`로 계산한다.
- Future split과 future filing은 해당 month-end 이전 값에 소급하지 않는다.
- 10-Q/A·10-K/A처럼 실제 amendment/restatement가 같은 primary period를 갱신하면 그 `available_at` 이후에만 반영한다.
- Main screen readiness는 Graph 1의 valid P/E readiness를 소유한다. Growth observation이 8개 미만이면 Graph 2만 BLOCKED하며 Graph 1을 숨기거나 `PER 방식으로 평가 불가`로 표현하지 않는다.
- `NOT_APPLICABLE`은 current non-positive TTM EPS, structurally short listing, unsupported instrument, unverified ADR unit처럼 실제 P/E 적용 불가 사유에만 사용한다.

### No-Distortion Invariants

- AMD-like later comparative Q fixture에서 true FY-derived Q4는 later filing 때문에 변하지 않는다.
- NVDA-like in-year split fixture에서 FY와 Q1/Q2/Q3가 common share basis로 정규화된 뒤 Q4와 TTM이 정확히 FY total과 일치한다.
- AAPL/NVDA 비달력 fiscal year, standard-calendar AMD/MSFT/META/TSLA, negative TTM, amendment available-at를 실제/fixture 회귀로 확인한다.
- 기존 S&P read model과 retained Nasdaq backend contract는 회귀시키지 않는다.

## 2026-07-15 Partial Historical Display Addendum

### 이걸 하는 이유?

현재 AAPL 5년은 `42/60`, AMD 3년은 `33/36`, AMD 5년은 `39/60`개의 point-in-time 상대가치 point를 실제 DB 근거로 계산할 수 있다. 기존 all-or-nothing history status와 React gate는 한 달이라도 부족하면 계산 가능한 나머지 point까지 전부 숨긴다. 이는 no-look-ahead 정확성 요구가 아니라 표시 정책의 문제다.

### Approved Display Contract

- 변경 대상은 미국 개별주식의 historical 1/3/5-year option이다. S&P 500 history service와 표시 계약은 바꾸지 않는다.
- `calculate_historical_stock_scenario()`는 선택 기간의 월별 slot과 각 slot의 `AVAILABLE/MISSING` 상태, `slot_index`, reason code를 반환한다.
- `READY`는 모든 slot이 계산 가능할 때, `PARTIAL`은 두 개 이상의 slot이 계산 가능하지만 일부가 없을 때, `INSUFFICIENT_HISTORY`는 계산 가능한 point가 두 개 미만일 때 사용한다.
- `series`는 기존 consumer 호환을 위해 계산 가능한 point만 유지하고, `timeline`은 선택 기간의 모든 월과 명시적 gap을 보존한다.
- `NON_POSITIVE_EPS`, `INSUFFICIENT_ROLLING_PER_WARMUP`, `INSUFFICIENT_PIT_EVIDENCE`, `PRICE_MISSING`을 최소 gap reason으로 구분한다.
- React는 original monthly slot 위치를 x축으로 사용하고, 상대가치 band/baseline/actual path를 연속된 AVAILABLE segment별로 따로 그린다. gap 양쪽을 하나의 path로 연결하지 않는다.
- PARTIAL banner에는 `계산 가능 N/M개월`, 누락 개월 수, `결측 월은 연결·보간하지 않음`을 표시한다.
- historical gap은 collection CTA를 새로 만들지 않는다. 과거 SEP backfill과 적자기업 대체 valuation은 후속 차수다.

### No-Distortion Invariants

- AMD-like 3년 fixture의 첫 3개월 non-positive TTM EPS는 빈 slot으로 남고 나머지 `33/36`개월만 표시된다.
- AAPL-like 초기 PIT evidence gap은 원래 시간축 앞부분의 빈 구간으로 남고 사용 가능한 point가 왼쪽으로 압축되지 않는다.
- interior gap 앞뒤의 band/line을 연결하지 않는다.
- `available_at`, positive EPS/P-E, 60개월 rolling log(P/E), applicable SEP vintage 계산식은 변경하지 않는다.
