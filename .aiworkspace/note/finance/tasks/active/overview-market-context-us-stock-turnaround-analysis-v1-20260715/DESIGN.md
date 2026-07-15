# Overview Market Context US Stock Turnaround Analysis V1 Design

Status: Approved Direction — Written Spec Review Requested
Last Updated: 2026-07-15

## 이걸 하는 이유?

현재 미국 개별주식 상대가치 화면은 positive TTM diluted EPS와 최소 60개월 positive P/E 이력이 있는 기업을 대상으로 한다. 이 계약은 P/E 왜곡을 막는 데는 맞지만, 적자에서 흑자로 전환 중인 기업은 검색할 수 있어도 `NOT_APPLICABLE` 안내 외에는 사업 개선과 현금 생존 가능성을 판단할 근거가 없다.

전환기업은 단일 EPS 양전보다 매출, 매출총이익, 영업손실, 영업현금흐름, FCF, 현금 runway, 부채, 이자 부담, 희석을 순서와 함께 읽어야 한다. V1은 현재 선택된 한 종목의 저장된 SEC detailed statement와 가격/프로필 자료만 읽어, P/E를 강제로 만들지 않고 전환 근거와 현재 적용 가능한 가치평가 프레임을 보여준다.

## Decision Summary

- Market Context 최상위 selector는 `S&P 500 | 미국 개별주식`을 유지한다.
- 미국 개별주식에서 한 종목을 선택한 뒤 내부 분석 selector를 `PER 상대가치 | 전환 분석`으로 추가한다.
- `PER 상대가치`는 현재 구현과 계산 계약을 유지한다.
- current TTM EPS가 0 이하이거나 P/E history가 준비되지 않은 종목은 `전환 분석`을 기본 화면으로 연다.
- 전환 분석은 분기 재무제표를 월별로 보간하지 않는다. 최근 `8분기 | 12분기 | 20분기`를 원래 분기 위치에 표시한다.
- 핵심 그래프는 `영업 전환`과 `현금 전환` 두 개다. 현금 runway, 부채/이자, 희석은 별도 risk evidence로 둔다.
- 전환 단계와 재무곤경 위험은 한 점수로 합치지 않는다. operating milestone과 survival risk overlay를 분리한다.
- EV/Sales 등 수치는 freshness와 분모 품질이 검증된 경우에만 표시한다. 불완전한 입력으로 target price나 고평가/저평가 결론을 만들지 않는다.
- 검색과 화면 진입은 DB read-only다. 외부 수집은 선택 종목의 명시 action에서만 동기 실행한다.
- V1은 선택된 한 기업의 분석이다. 미국 전체 전환기업 순위/스크리너는 별도 V2 범위다.

## Approaches Considered

### A. 미국 개별주식 내부 분석 selector — Selected

```text
[S&P 500] [미국 개별주식]

기업 검색 / 선택
[PER 상대가치] [전환 분석]
```

기업 identity와 검색을 공유하면서 P/E와 비-P/E 질문을 분리한다. S&P 500 화면에는 새 상태나 payload를 요구하지 않는다.

### B. 한 화면에서 상태에 따라 완전 자동 교체 — Rejected

처음 진입은 간단하지만 흑자 전환 후 과거 회복 근거를 다시 보기 어렵고, 사용자가 어떤 분석 계약을 보고 있는지 불명확해진다.

### C. Market Context 최상위 세 번째 selector — Rejected

기업 검색과 선택이 중복되고, `전환기업`을 별도 instrument처럼 보이게 한다. 실제로는 같은 미국 개별주식에 대한 다른 분석 방법이다.

## Scope Boundary

### V1

- 현재 검색/선택된 미국 보통주 한 종목
- stored SEC 10-Q/10-K detailed statement의 filing-aware discrete-quarter reconstruction
- 8/12/20분기 영업·현금 전환 근거
- operating milestone, P/E handoff readiness, survival/dilution risk overlay
- freshness가 검증된 current stage-appropriate valuation multiple/yield
- selected-symbol raw data collection/resume

### Later Scope

- 미국 전체 종목 전환 후보 screen/ranking
- sector/industry peer cohort와 peer-relative percentile
- historical enterprise-value snapshot materialization
- normalized-margin DCF와 공식 target price
- 은행/보험사 전용 자본·건전성 valuation
- REIT P/FFO, 자원기업 NAV, 바이오 pipeline valuation

V1 화면은 선택 종목을 분석하지만 시장 전체에서 후보를 찾아주는 screener로 표현하지 않는다.

## Evidence Model: Milestones And Risk Overlays

전환 단계는 항상 같은 순서로 일어난다는 보장이 없다. 예를 들어 순이익이 일회성 요인으로 양전해도 OCF가 음수일 수 있다. 따라서 rail은 자동으로 앞 단계를 모두 통과시키는 funnel이 아니라, 독립 milestone의 확인 상태를 보여준다.

### Operating Milestones

1. `LOSS_BASELINE`
   - current TTM EPS가 0 이하이고 아래 개선 milestone이 확인되지 않는다.
2. `OPERATING_IMPROVEMENT`
   - 매출 방향, 매출총이익률, 영업이익률 세 evidence 중 둘 이상이 개선된다.
3. `CASH_FLOW_TURN`
   - 최근 두 개 quarterly observation의 TTM OCF가 연속 양수다.
   - TTM FCF 양전은 별도 `FCF_CONFIRMED` evidence로 표시한다.
4. `EARNINGS_TURN`
   - 최근 3개 discrete quarter 중 2개 이상의 diluted EPS가 양수지만 current TTM EPS는 아직 0 이하다.
5. `PER_CANDIDATE`
   - current TTM EPS가 양수지만 four consecutive quarterly TTM EPS 또는 60개월 positive P/E 이력이 준비되지 않았다.
6. `PER_READY`
   - 최근 4개 quarterly TTM EPS가 모두 양수이고 기존 PER service의 Graph 1이 `READY`다.

Headline은 `PER_READY > PER_CANDIDATE > EARNINGS_TURN > CASH_FLOW_TURN > OPERATING_IMPROVEMENT > LOSS_BASELINE` 우선순위로 정하되, 낮은 단계의 미확인 항목을 자동 통과로 표시하지 않는다. `EARNINGS_TURN`인데 OCF가 음수면 `현금 전환 미확인`을 바로 옆에 둔다.

### Exact Improvement Rules

- 계산에는 최소 8개 discrete quarter가 필요하다. 8개 미만이면 stage를 확정하지 않고 section readiness를 낮춘다.
- `revenue_direction`:
  - current TTM revenue YoY가 양수이거나,
  - 음수지만 직전 quarterly TTM revenue YoY보다 최소 1.0 percentage point 개선된다.
- `gross_margin_improvement`:
  - current TTM gross profit가 양수이고,
  - current TTM gross margin이 prior-year TTM보다 최소 1.0 percentage point 높다.
- `operating_margin_improvement`:
  - 최근 3개 same-quarter YoY operating-margin delta 중 2개 이상이 `+1.0 percentage point` 이상이고,
  - current TTM operating margin도 prior-year TTM보다 최소 1.0 percentage point 높다.
- `burn_improving`은 current TTM OCF/FCF가 prior-year TTM보다 개선됐다는 evidence다. 음수 현금흐름을 양전으로 표시하지 않는다.
- 1.0 percentage point는 작은 rounding fluctuation으로 milestone이 바뀌는 것을 줄이는 V1 materiality floor다. universal investment threshold로 표현하지 않고 raw delta를 함께 표시한다.

### Survival And Capital Risk Overlays

Operating milestone과 별개로 아래를 계산한다.

- `CASH_RUNWAY_HIGH_RISK`: negative TTM FCF 기준 mechanical runway가 4분기 미만
- `CASH_RUNWAY_WATCH`: 4분기 이상 8분기 미만
- `DILUTION_WATCH`: split-neutral diluted weighted-average shares YoY가 5% 이상
- `DILUTION_HIGH_RISK`: split-neutral diluted weighted-average shares YoY가 10% 이상
- `DEBT_SERVICE_HIGH_RISK`: positive TTM operating income일 때 interest coverage가 1.0x 미만
- `DEBT_SERVICE_WATCH`: interest coverage가 1.0x 이상 2.0x 미만
- TTM operating income이 0 이하이면 interest coverage를 유효한 양수 ratio로 만들지 않고 `NOT_MEANINGFUL`로 둔다.
- net debt가 양수이고 TTM OCF가 0 이하이면 `NET_DEBT_WITH_NEGATIVE_OCF`를 표시한다.

```text
mechanical runway quarters
  = 4 * (cash + eligible short-term investments) / abs(TTM FCF)
```

runway는 committed credit line, restricted cash, 미래 증자, burn 변화가 없는 단순 현재속도 기준이다. 예측치나 생존 보장으로 표현하지 않는다.

## Filing-Aware Discrete-Quarter Contract

SEC XBRL duration fact는 3개월, 6개월 누적, 9개월 누적, FY가 섞인다. raw `period_type=Q`를 독립 분기값으로 바로 사용하지 않는다.

### Resolver Rules

1. 해당 filing의 primary fiscal period와 report date를 우선한다. later filing의 comparative fact가 원래 quarter를 덮어쓰지 못한다.
2. 약 3개월 duration은 direct quarter 후보로 사용한다.
3. 6개월 YTD는 같은 fiscal year의 Q1 YTD를 뺀 뒤 Q2를 만든다.
4. 9개월 YTD는 같은 fiscal year의 H1 YTD를 뺀 뒤 Q3를 만든다.
5. FY는 true fiscal year-end에서 Q1+Q2+Q3를 뺀 뒤 Q4를 만든다.
6. 파생 quarter의 `available_at`은 모든 operand 중 가장 늦은 시점이다.
7. 서로 다른 concept family, unit, fiscal year, share basis를 섞지 않는다.
8. direct quarter와 derived quarter가 모두 있으면 primary filing의 direct quarter를 우선한다.
9. instant fact는 해당 period end에 대해 cutoff까지 공개된 primary filing 값을 사용한다.
10. every derived row는 operand accession/concept/period와 derivation rule을 provenance에 남긴다.

SEC는 XBRL fact가 `instant` 또는 `duration` period를 가지며, quarterly duration과 first-nine-month YTD context가 존재한다고 설명한다. V1 resolver는 calendar frame을 그대로 신뢰하지 않고 issuer fiscal period와 filing provenance를 보존한다.

### Canonical Metric Families

- revenue: `RevenueFromContractWithCustomerExcludingAssessedTax`, `Revenues`, `SalesRevenueNet`
- gross profit: `GrossProfit`; 없으면 동일 quarter revenue minus cost-of-revenue
- operating income: `OperatingIncomeLoss`
- net income: `NetIncomeLoss`, `ProfitLoss`
- diluted EPS: 현재 검증된 diluted/basic-and-diluted family
- OCF: `NetCashProvidedByUsedInOperatingActivities`
- CapEx: `PaymentsToAcquirePropertyPlantAndEquipment`; cash outflow를 positive CapEx magnitude로 정규화
- FCF proxy: TTM OCF minus TTM CapEx
- cash: cash and cash-equivalent family
- short-term investments: eligible current short-term investment family; restricted cash는 합산하지 않음
- debt: direct total debt를 우선하고, 없을 때 current/non-current debt component를 중복 없이 합산
- interest expense: debt/interest expense family
- diluted shares: weighted-average diluted shares; price/per-share 비교와 dilution trend에는 PIT split normalization 적용
- D&A: explicit depreciation/depletion/amortization duration family가 완전할 때만 사용

Gross profit derivation은 revenue와 cost가 같은 issuer, fiscal quarter, unit, filing snapshot에 있을 때만 허용한다. tag가 없다는 이유로 다른 분기나 다른 filing 값을 가져오지 않는다.

## Quarterly And TTM Calculations

분기별 chart point는 filing `available_at` 기준으로 생성한다.

```text
TTM metric at quarter q
  = sum(latest four discrete quarters available at q.available_at)

TTM gross margin
  = sum(TTM gross profit) / sum(TTM revenue)

TTM operating margin
  = sum(TTM operating income) / sum(TTM revenue)

FCF proxy
  = TTM OCF - TTM CapEx
```

- ratio를 4개 분기 평균하지 않는다. TTM numerator와 denominator를 먼저 합산한다.
- YoY는 same-quarter 또는 quarterly TTM과 q-4를 비교한다.
- future filing, later restatement, future split을 과거 point에 소급하지 않는다.
- missing quarter는 다른 quarter로 대체하거나 interpolation하지 않는다.
- negative/zero denominator는 multiple이나 yield를 만들지 않는다.

## Cash-Flow Quality Boundary

Reported OCF는 working-capital 변동과 stock-based compensation의 영향을 받을 수 있다. V1은 OCF 양수 한 번만으로 cash-flow turn을 확정하지 않고 두 consecutive quarterly TTM observation을 요구한다.

- OCF와 FCF를 별도 표시한다.
- net income 개선과 OCF 개선이 동시에 나타나는지 evidence row로 비교한다.
- SBC 또는 working-capital component가 canonical하게 완전하지 않으면 normalized OCF를 합성하지 않는다.
- `reported OCF 기준이며 working-capital/SBC normalization은 완전하지 않음`을 limitation으로 표시한다.
- 향후 normalized cash-conversion 연구는 별도 범위다.

## Stage-Appropriate Valuation Router

V1은 공식 fair value나 peer-relative cheap/expensive 판정을 만들지 않는다. 입력이 검증되면 현재 적용 가능한 multiple/yield와 그 이유만 보여준다.

### Value Basis Gate

Current enterprise/equity value input은 다음을 모두 만족해야 한다.

- stored `nyse_asset_profile.market_cap`의 `last_collected_at`이 latest price basis로부터 7 calendar days 이내
- market cap, cash, debt, denominator의 currency가 USD
- latest cash/debt statement basis date와 accession이 존재
- cash, short-term investments, debt component가 중복 합산되지 않음
- market cap과 latest statement basis date를 화면에 각각 노출

하나라도 실패하면 numeric multiple을 숨기고 `INPUT_STALE`, `COMPONENT_MISSING`, `UNIT_UNVERIFIED` 중 정확한 이유를 표시한다. stale profile은 explicit selected-symbol collection으로만 갱신한다.

```text
enterprise value
  = current market cap + total debt - cash - eligible short-term investments
```

### Method Priority

1. current PER service `READY`: `P/E 상대가치` handoff
2. positive TTM FCF: `FCF yield` and `P/FCF`
3. positive TTM OCF: `OCF yield` and `P/OCF`
4. positive TTM EBITDA proxy with complete D&A: `EV/EBITDA`
5. positive TTM gross profit: `EV/Gross Profit`
6. positive TTM revenue: `EV/Sales`
7. none: survival/liquidity evidence only

US GAAP OCF는 interest cash flow를 operating에 포함하므로 `EV/OCF`를 사용하지 않는다. enterprise-value numerator와 equity cash-flow denominator를 섞지 않고, OCF/FCF는 market-cap 기반 price multiple/yield로 표시한다.

Financial institutions, REIT, commodity NAV, biotech pipeline처럼 일반 operating-company multiple이 부적합한 유형은 operational trend만 표시하고 valuation router를 `SECTOR_METHOD_UNSUPPORTED`로 둔다.

## User Flow

```text
Market Context
  -> 미국 개별주식
  -> 기업명 또는 ticker 검색
  -> current common-stock 선택
  -> selected-symbol DB evidence load
      -> PER READY: 기본 `PER 상대가치`
      -> PER not ready/non-positive EPS: 기본 `전환 분석`
  -> 내부 selector로 두 분석을 명시적으로 전환
  -> 전환 분석
      -> milestone rail
      -> Graph 1 영업 전환
      -> Graph 2 현금 전환
      -> runway/debt/dilution risk
      -> 현재 적용 가능한 valuation frame
      -> 산식·원자료·한계
  -> raw gap일 때만 `분석 자료 수집`
      -> profile/price/SEC selected-symbol sync collection
      -> DB persist
      -> cache clear + rerun
```

새 symbol을 선택하면 sub-analysis는 service의 `recommended_analysis`로 초기화한다. 같은 symbol 안에서 사용자가 선택한 탭은 session state로 유지한다.

## React Surface

```text
[S&P 500] [미국 개별주식]

기업명·티커 검색
선택 종목: Rivian Automotive · RIVN · Nasdaq

[PER 상대가치 · 적용 전] [전환 분석]

전환 단계
매출/GP 개선  영업손실 축소  OCF 양전  FCF 양전  EPS 양전  PER READY
     확인          확인         미확인      미확인     미확인      미확인

현재 headline: OPERATING IMPROVEMENT
보조 경고: 현금 전환 미확인 · 희석 위험 확인 필요

그래프 1 · 영업 전환                 [8분기] [12분기] [20분기]
  위: quarterly revenue YoY bars
  아래: TTM gross margin / operating margin lines + 0% axis

그래프 2 · 현금 전환
  TTM OCF / TTM FCF bars + 0 axis
  hover: raw quarter, TTM, filing available_at

생존·자본 위험
  현금 runway | 순부채/이자 | 희석주식 증가

현재 적용 가능한 가치평가 프레임
  EV/Sales 적용 가능 / EV 입력 기준일 / P/E 적용 전
```

### Chart Rules

- Graph 1과 Graph 2는 같은 quarterly x-axis와 8/12/20-quarter selector를 공유한다.
- 서로 다른 scale의 revenue growth와 margins를 한 plot에 겹치지 않고 stacked plot으로 둔다.
- OCF/FCF는 quarterly observation의 TTM 값으로 seasonality를 줄이고 raw quarter는 inspector에 둔다.
- missing quarter는 x-axis slot을 유지하고 line/bar를 연결하지 않는다.
- 0 기준선을 항상 표시한다.
- loss value를 red styling으로 표현할 수 있지만 red/green만으로 의미를 전달하지 않는다.
- 420px에서는 charts가 가로 스크롤 없이 세로로 쌓이고 risk cards가 한 열로 내려간다.

## Readiness Contract

### NOT_SELECTED

- 기업 선택 전이다.
- 검색만 표시하고 turnaround loader를 실행하지 않는다.

### READY

- 최소 8개 discrete quarter의 core operating/cash evidence가 있다.
- current milestone과 risk overlay를 계산할 수 있다.

### PARTIAL

- stage를 읽을 core evidence는 있지만 gross-profit, interest, D&A, short-term investments 등 일부 section이 없다.
- 계산 가능한 chart point만 원래 분기 위치에 표시하고 누락 section을 명시한다.

### COLLECTABLE

- current identity/CIK는 확정됐고 selected-symbol SEC/profile collection으로 해결 가능한 raw gap이 있다.
- exact missing concepts/range/scope와 collection action을 표시한다.

### NOT_APPLICABLE

- ETF/fund/preferred/warrant, unverified ADR share unit, unsupported non-operating instrument다.
- negative earnings 자체는 turnaround 분석의 NOT_APPLICABLE 이유가 아니다.

### ERROR

- DB query/schema/calculation contract 오류다.
- 자동 provider retry를 실행하지 않고 기존 PER/S&P 모델을 격리한다.

각 section은 `READY/PARTIAL/BLOCKED`를 별도로 가질 수 있다. D&A가 없어 EV/EBITDA가 막혀도 영업/현금 chart 전체를 숨기지 않는다.

## Architecture And Ownership

```text
MarketContextValuation.tsx
  -> shared U.S. stock search / selection
  -> PER relative valuation | turnaround analysis
  -> market_context_helpers.py
  -> market_context_valuation.py
       -> existing us_stock_valuation.py
       -> new us_stock_turnaround.py service
            -> finance/loaders/us_stock_turnaround.py
                 -> finance_fundamental.nyse_financial_statement_values
                 -> finance_meta.nyse_asset_profile / symbol lifecycle
                 -> finance_price.nyse_price_history
            -> finance/data/us_stock_turnaround.py
                 -> filing-aware discrete-quarter resolver
                 -> TTM metrics / milestones / risks / valuation router
  -> JSON-safe payload
  -> React charts/cards
```

Expected owners:

- Add: `finance/data/us_stock_turnaround.py`
- Add: `finance/loaders/us_stock_turnaround.py`
- Add: `app/services/overview/us_stock_turnaround.py`
- Modify: `app/services/overview/market_context_valuation.py`
- Modify: `app/web/overview/market_context_helpers.py`
- Modify: `app/jobs/overview_actions.py`
- Modify only if collection scope requires it: `app/jobs/ingestion_jobs.py`
- Split/add focused React files under `app/web/streamlit_components/market_context_valuation/src/`
- Add focused pure/loader/service/event/UI contract tests

V1은 새 turnaround materialization table을 만들지 않는다. 한 symbol의 최대 24 raw quarter-equivalent lookback과 필요한 comparative/FY rows를 bounded read하고 read-time 계산한다. 20 visible quarters에 q-4/TTM warmup이 필요하므로 loader는 최대 7 fiscal years의 relevant concepts만 읽는다.

## Collection Contract

- 화면 진입, search, tab switch는 DB read-only다.
- `분석 자료 수집`은 selected symbol과 CIK가 일치할 때만 실행한다.
- preflight scopes: `asset_profile`, `prices`, `sec_statements`.
- SEC collection은 EPS만이 아니라 detailed statement raw ledger 전체를 저장하므로 turnaround concept gap도 같은 selected-CIK action으로 보강한다.
- profile freshness가 7일을 넘었지만 charts는 준비된 경우, charts는 계속 보이고 valuation multiple만 COLLECTABLE/BLOCKED다.
- partial success는 저장하고 retry는 이미 충족된 scope를 제외한다.
- 경제적 적자, negative denominator, sector-method unsupported를 collection으로 해결 가능하다고 표시하지 않는다.

## Actual DB Feasibility Evidence

2026-07-15 read-only audit에서 다음 raw duration coverage를 확인했다.

- RIVN: revenue/gross profit/operating income/OCF/CapEx 약 16 distinct quarters
- PLTR: gross profit/operating income/OCF/CapEx 약 19 distinct quarters
- LCID: operating income/net income 약 18 quarters, OCF 약 17 quarters, CapEx 약 15 quarters
- LCID의 direct `GrossProfit`은 최근 coverage가 거의 없어 revenue minus cost fallback이 필요하다.
- AAPL/AMD는 50개 안팎의 duration-quarter evidence가 있어 profitable-company regression fixture로 사용할 수 있다.
- current asset-profile market cap은 symbol별 수집일이 달라 freshness gate 없이 EV 계산에 사용하면 안 된다.

이 audit은 row 존재만 증명한다. 실제 discrete quarter 완전성은 resolver와 concept-family tests를 통과한 뒤에만 READY로 승격한다.

## Five-Stage Implementation Roadmap

### 1차 — 분기 계산 정확도

- cumulative H1/9M to Q2/Q3 resolver
- true FY to Q4 resolver
- comparative fact non-overwrite
- instant/duration separation
- split-neutral diluted-share trend
- available_at no-look-ahead real-like fixtures

Completion: LCID/RIVN/PLTR/AAPL-like fixtures가 fake quarter, future filing, future split 없이 discrete quarter와 TTM을 만든다.

### 2차 — 전환 분석 엔진

- canonical concept families
- TTM revenue/margins/OCF/FCF/EPS
- milestone classifier and independent risk overlays
- cash runway/debt/interest/dilution evidence
- stage-appropriate valuation router and input freshness gates
- section readiness

Completion: loss baseline, operating improvement, cash turn, earnings turn, PER candidate/ready, stale EV, missing metric cases를 pure tests로 고정한다.

### 3차 — Loader, Service, Collection

- selected-symbol bounded loader
- shared identity/search handoff
- read-only turnaround service
- exact missing-concept/profile freshness preflight
- selected profile/price/SEC synchronous collection and resume
- combined S&P/PER/turnaround failure isolation

Completion: render/search/tab switch는 provider call 0회이고 explicit action만 DB raw evidence를 갱신한다.

### 4차 — 내부 탭과 UI

- `PER 상대가치 | 전환 분석` selector
- recommended default routing
- milestone rail and risk overlays
- Graph 1/2 with 8/12/20-quarter selector
- valuation method card and exact blocked reason
- desktop/420px responsive and accessibility

Completion: negative EPS 회사는 P/E 수치를 노출하지 않고 전환 분석으로 진입하며 S&P/PER 화면은 회귀하지 않는다.

### 5차 — Actual QA, Docs, Commit

- RIVN, LCID, PLTR transition cases
- AMD/AAPL profitable/PER handoff regression
- missing gross-profit, stale profile, dilution, debt/interest, split cases
- focused/full regression and React production build
- desktop/420px Browser QA, console errors, horizontal overflow
- active task/docs/root handoff alignment
- distinct Korean commits and final coherent closeout

Completion: fresh verification evidence와 Browser screenshot 1장을 최종 보고에 포함하고 generated artifact는 commit하지 않는다.

## Test Strategy

### Resolver

- direct Q, H1-Q1, 9M-H1, FY-Q1-Q2-Q3 produce exactly one discrete quarter each
- later comparative facts never change original quarter provenance
- derived available_at is max operand availability
- concept/unit/fiscal-year mismatch blocks derivation
- future restatement and future split do not change a historical point
- missing operand remains missing

### Calculation

- TTM margins use summed numerator/denominator
- 1.0pp materiality floor and 2-of-3 operating rule are deterministic
- negative OCF is burn improvement, never cash-flow turn
- cash-flow turn needs two consecutive positive TTM OCF observations
- quarterly profit turn does not imply positive TTM EPS
- negative/zero denominator produces no multiple
- runway, dilution, interest, net-debt overlays are independent of headline stage

### Loader / Service

- one symbol and bounded date/concept predicates
- no DB write or provider call on search/render/tab switch
- section PARTIAL does not blank complete charts
- stale market cap blocks numeric EV only
- non-positive EPS routes to turnaround rather than whole-stock NOT_APPLICABLE
- S&P and existing PER payloads remain isolated

### Action

- selected symbol/CIK mismatch fails before provider execution
- exact scopes call profile/price/SEC collectors once
- partial success persists and retry narrows scopes
- intrinsic limitation never exposes collection action

### UI / Browser

- internal selector is shown only for a selected U.S. stock
- default route follows recommended analysis
- PER tab never renders negative P/E
- charts preserve gaps and 0 axes
- 8/12/20-quarter selector changes visible slots, not metric definitions
- keyboard selection, labels, color-independent statuses, desktop/420px no overflow
- S&P and current PER graphs/copy remain unchanged

## Success Criteria

- 적자기업을 선택하면 P/E 숫자 대신 실제 quarterly filing evidence 기반 전환 분석이 기본 표시된다.
- cumulative SEC facts를 독립 quarter로 오인하지 않는다.
- 미래 filing/restatement/split을 과거 point에 소급하지 않는다.
- 영업 개선과 distress/dilution risk를 한 점수로 뭉개지 않는다.
- OCF/FCF, EPS, valuation denominator의 negative/zero 상태를 유효한 multiple로 바꾸지 않는다.
- numeric EV multiple은 fresh market cap과 complete cash/debt/denominator가 있을 때만 표시된다.
- UI가 provider를 직접 호출하지 않는다.
- 기존 S&P 500 valuation과 미국 개별주 PER 상대가치가 회귀하지 않는다.
- missing quarter를 합성·대체·연결하지 않는다.

## Out Of Scope

- all-U.S.-stock turnaround screener/ranking
- peer-relative fair multiple and price target
- analyst estimates/consensus
- normalized OCF using incomplete working-capital/SBC facts
- automatic DCF and normalized cyclical margin forecast
- bank/insurer, REIT, biotech, commodity-specialized valuation
- broker action, buy/sell signal, auto trading
- new turnaround materialization table

## Research Basis

- [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces): company facts, units, quarterly/annual/instant XBRL periods and API boundary
- [SEC EDGAR XBRL Guide](https://www.sec.gov/files/edgar/filer-information/specifications/xbrl-guide-2025-07-10.pdf): instant/duration contexts and first-nine-month YTD period handling
- [Aswath Damodaran — Valuing Firms with Negative Earnings](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/Inv4ed.htm): negative earnings, normalization, cyclical/troubled-firm valuation boundary
- [Aswath Damodaran — Valuation Multiples First Principles](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/papers.html): numerator/denominator consistency and relative-multiple discipline
- [Piotroski (2000), Value Investing: The Use of Historical Financial Statement Information](https://ideas.repec.org/a/bla/joares/v38y2000ip1-41.html): profitability, cash flow, leverage/liquidity, and operating-efficiency evidence as separate signals
- [Dechow & Dichev, The Quality of Accruals and Earnings](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=277231): working-capital accrual estimation error and cash-flow/earnings quality boundary

이 근거들은 V1 threshold가 보편적 투자 법칙임을 증명하지 않는다. V1은 연구가 지지하는 signal families를 deterministic evidence contract로 구현하고, raw values와 한계를 함께 노출한다.
