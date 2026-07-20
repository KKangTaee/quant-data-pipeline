# Market Movers Approved Redesign Recommendation

Status: Phase 3 Read Model Complete; Phase 4 React Shell Ready
Decision Date: 2026-07-20
Last Updated: 2026-07-20

## 이걸 하는 이유?

현재 `Workspace > Overview > 변동 종목`은 수집, ranking, sector breadth, missing 진단, 선택 종목 조사를 한 개의 긴 화면에 같은 비중으로 노출한다. 필요한 기능은 많지만 사용자가 첫 화면에서 `무엇이 움직였고, 그 움직임이 시장에 얼마나 퍼졌는가?`를 빠르게 끝내기 어렵다.

이번 개편은 기능을 추가로 쌓는 작업이 아니다. 아래 세 판단을 하나의 연결된 흐름으로 만드는 작업이다.

1. 움직인 종목을 찾는다.
2. 개별 움직임인지 sector / industry 확산인지 확인한다.
3. 선택 종목의 가격, 재무, 뉴스·공시 근거를 조사한다.

## Approved Product Direction

사용자는 세 가지 IA 후보 중 `A안: 결정형 워크벤치`를 승인했다.

- 첫 viewport의 primary job은 `움직인 종목 발견 + 시장 확산 확인`이다.
- ranking, breadth context, 선택 종목 quick research는 하나의 React shell에서 selected state를 공유한다.
- 수집 상태는 raw job dashboard가 아니라 compact trust line과 복구 action으로 제공한다.
- sector / industry 흐름은 정적 상승 순위가 아니라 확산, 상대강도, 지속성으로 설명한다.
- 미래 흐름은 확정 예측이 아니라 검증 gate를 통과한 조건부 역사 분포로만 제공한다.
- 선택 종목 조사는 가격·모멘텀, 재무, 뉴스·공시로 분리한다.
- 재무 탭의 보고 주기와 재무 factor는 서로 다른 control group이다.

## Success Criteria

개편 후 사용자는 첫 viewport에서 다음 질문에 답할 수 있어야 한다.

- 선택 coverage와 기간에서 어떤 종목이 가장 크게 움직였는가?
- 그 움직임은 sector / industry 구성 종목에 넓게 퍼졌는가?
- 선택 종목은 해당 group의 bellwether인가, 개별 예외인가?
- 현재 데이터가 최신이며 계산에 포함된 표본은 몇 개인가?
- 더 조사할 가치가 있다면 가격·재무·이벤트 중 어디를 먼저 볼 것인가?

완료 조건은 status, row, job 수를 더 많이 보여주는 것이 아니다. 사용자가 더 적은 scroll과 화면 전환으로 위 판단을 끝내는 것이다.

## Information Architecture

### 1. Command And Trust Line

상단은 아래 control만 유지한다.

- coverage: S&P 500 / Top 1000 / Top 2000 / 준비된 universe
- period: 일 / 주 / 월
- ranking intent: 상승률 / 하락률 / 거래량 / 이상 거래량
- compact trust: 유효 종목 수, 전체 종목 수, 계산 기준 시각, freshness
- stale 또는 partial일 때만 primary action 1개

sector는 ranking intent가 아니라 오른쪽 breadth context의 group mode로 이동한다. 이로써 sector row를 선택했는데 Top Gainers symbol로 fallback하던 현재 handoff를 제거한다.

### 2. First Viewport Workbench

desktop 기본 비율은 ranking 약 60~65%, breadth context 약 35~40%다.

#### Ranking Board

- rank, symbol, company, canonical sector, movement reason, primary metric, volume context를 compact row로 표시한다.
- row 선택은 즉시 selected symbol을 바꾸며 page navigation을 요구하지 않는다.
- ranking context와 selected symbol은 quick research까지 유지한다.

#### Breadth Context

- `Sector | Industry`를 독립 전환한다.
- 시장 상승 종목 비중과 선택 group의 상승 종목 비중을 표시한다.
- group별 equal-weight return, cap-weight return, relative strength, breadth change를 제공한다.
- group 선택 시 market-cap Top 3 bellwether를 표시한다.
- 정적 순위보다 `확산하며 강화`, `좁게 상승`, `약화`, `반전 관찰`처럼 evidence-based state를 먼저 보여준다.

#### Quick Research

- selected symbol, price, selected-period return, volume multiple, group breadth, bellwether rank를 표시한다.
- 큰 financial / metadata surface를 첫 viewport에 모두 펼치지 않는다.
- `상세 조사 열기`로 아래 detail section을 확장한다.

### 3. Selected Stock Research

상세 조사는 같은 shell 안에서 ranking과 breadth context를 잃지 않는 expandable section으로 둔다.

- 가격·모멘텀
- 재무
- 뉴스·공시

metadata 수집 action보다 현재 저장 근거가 먼저 보인다. 뉴스·SEC·statement gap action은 해당 tab의 supporting action으로 둔다.

## Visual Contract

Market Context, Futures Macro, Sentiment와 같은 Overview visual rhythm을 따른다.

- 한 개의 React shell
- compact hero / command line
- current evidence first
- 필요한 section만 divider로 구분
- raw method, source, operations evidence는 disclosure로 하향
- 같은 freshness 정보를 여러 panel에서 반복하지 않음
- metric card를 반복하기보다 ranking row, chart, breadth mark를 주인공으로 사용

desktop selected research의 chart/readout 기본 비율은 약 70/30이다. 재무 factor control을 추가하더라도 chart 면적을 줄이지 않는다. 좁은 화면에서만 readout을 chart 아래로 이동한다.

## Collection And Missing-Data Contract

### Complete

- 전체 universe가 계산 가능하다.
- `valid / total`, basis timestamp, freshness를 compact line으로 표시한다.

daily ranking은 한 계산 안에서 intraday와 EOD를 섞지 않는다. latest accepted intraday snapshot이 있으면 이를 사용하고, freshness 기준을 넘으면 stale로 표시한다. EOD fallback이 필요하면 basis를 `EOD`로 명시하며 조용히 전환하지 않는다.

### Partial

- 분석 가능한 종목으로 ranking과 breadth를 계속 계산한다.
- 누락값을 0 return, 0 volume, 0 market cap으로 대체하지 않는다.
- metric별 유효 분모와 제외 수를 표시한다.
- raw missing rows 대신 원인별 compact summary와 `누락 재수집`을 제공한다.

### Blocked

- universe 자체가 없거나 계산 basis가 없으면 ranking과 breadth를 만들지 않는다.
- 이전 결과를 현재 결과처럼 재사용하지 않는다.
- `universe 설정`, `가격 이력 준비`처럼 원인에 맞는 다음 행동을 제공한다.

### User-Facing Failure Taxonomy

- 갱신 필요
- 기간 이력 부족
- quote 누락
- 종목 식별 확인 필요
- provider 반복 gap
- universe 준비 필요

raw run status, saved rows, elapsed job log는 기본 surface에 표시하지 않는다.

## Sector And Industry Contract

### Canonical Sector

filter와 grouping 전에 provider raw label을 canonical 11 sector로 정규화한다. filter options와 breadth group은 같은 canonical value를 사용한다.

### Sector Bellwether Top 3

- 최신 profile market cap 기준 Top 3다.
- positive-return leader와 별도 contract로 둔다.
- market cap missing 종목은 순위에서 제외하고 cap coverage를 표시한다.
- 각 bellwether에 1D / 5D / 21D return과 sector 대비 상대수익을 연결한다.
- 선택 universe의 equity issuer만 포함하고 ETF, ETN, fund는 제외한다. ADR은 선택 universe에 실제 포함되고 issuer-level market cap evidence가 있을 때 유지한다.

### Industry

- 최소 group size 기본값은 5개다.
- `Unknown`은 별도 group으로 격리한다.
- 기본 화면은 상위 industry만 노출하고 sector 선택에서 drilldown한다.
- raw provider label alias와 taxonomy version을 장기적으로 관리한다.
- sparse group과 single-name concentration을 명시한다.

첫 release는 provider industry label을 trim / case normalization하고 명시적 alias table을 적용한 stable display key를 사용한다. GICS와 동등한 taxonomy라고 표방하지 않는다.

## Flow And Outlook Contract

### Level 1: Current Flow

sector와 industry 모두 아래 current-state evidence를 제공할 수 있다.

- breadth level과 이전 window 대비 변화
- market 대비 relative strength
- equal-weight / cap-weight divergence
- leader persistence
- large-cap concentration
- daily / weekly / monthly direction

Level 1은 forecast가 아니라 현재 상태와 다음 관찰 조건이다.

### Level 2: Sector Conditional Outlook

sector만 우선 제공한다.

- 유사 breadth + relative-strength state의 과거 episode
- 향후 5D / 20D / 60D sector proxy vs SPY 분포
- median, range, positive rate, sample count, drawdown
- independent episode spacing과 walk-forward validation

최소 표본과 OOS publication gate를 통과하지 못하면 수치를 숨긴다. UI 문구는 `상승한다`가 아니라 `유사 국면에서 관측된 조건부 분포`다.

### Industry Outlook Hold

과거 시점 industry taxonomy와 membership이 확보되기 전에는 industry conditional outlook을 제공하지 않는다. current taxonomy를 과거에 소급 적용해 survivorship / classification drift를 만들지 않는다.

## Price And Momentum Research

하나의 primary chart가 아래 선택을 소유한다.

- range: 1M / 3M / 6M / 1Y
- adjusted price
- normalized benchmark comparison
- optional MA20 / MA50
- aligned volume

readout은 selected range return, benchmark excess return, moving-average distance, max drawdown, volatility를 제공한다. 지표를 장식용으로 늘리지 않는다.

## Financial Research Contract

### Independent Control Groups

`보고 주기`와 `재무 factor`는 같은 segmented control에 섞지 않는다.

#### 보고 주기

- 분기
- 연간

single-select이며 chart의 time basis만 바꾼다.

#### 재무 Factor

한 번에 하나의 factor만 선택한다. 단위가 다른 지표를 같은 axis에 겹치지 않는다.

| Group | Factors | Unit / basis |
| --- | --- | --- |
| 손익 | 매출, 영업이익, 순이익 | statement currency |
| 손익 | 희석 EPS | reported GAAP currency per share |
| 수익성 | 영업이익률, 순이익률 | percent |
| 수익성 | ROE | TTM net income / average equity |
| 안정성 | 유동비율 | current assets / current liabilities |
| 안정성 | 부채비율 | total liabilities / equity |

factor group control은 chart 위에 두되 이전 승인 시안의 넓은 graph 크기와 70/30 chart/readout 비율을 유지한다.

### EPS And PER

- 분기 EPS는 provider / filing의 reported diluted EPS다.
- current TTM EPS는 네 개 연속 분기의 diluted EPS 합이 모두 있을 때만 계산한다.
- current PER는 latest accepted price / current TTM EPS다.
- 네 분기 중 하나라도 없으면 current TTM EPS와 PER는 unavailable이다.
- historical PER는 period-end price와 그 시점에 이용 가능했던 contemporaneous TTM EPS가 준비될 때만 제공한다.
- 현재 price를 과거 period EPS에 반복 적용한 기존 PER series는 제거한다.

### Events And Source Boundary

- 뉴스와 SEC는 title, source, publish / filing date, DB reflected time을 구분한다.
- UI가 provider에 직접 fetch하지 않는다.
- `Ingestion -> DB -> Loader -> UI` 경계를 유지한다.
- session-only metadata는 persisted evidence처럼 표시하지 않는다.

## Component Architecture

현재 `app/services/overview/market_movers.py`와 `app/web/overview/market_movers_helpers.py`는 각각 약 3,700줄과 4,500줄이다. 새 기능을 계속 추가하지 않고 public facade를 유지한 채 내부 역할을 분리한다.

### Service Read Models

- `app/services/overview/market_movers_read_model.py`: period / ranking / coverage / valid denominator
- `app/services/overview/market_movers_group_flow.py`: canonical sector, industry taxonomy, breadth, bellwether Top 3
- `app/services/overview/market_movers_outlook.py`: Level 1 current flow와 gated Level 2 distribution
- `app/services/overview/market_mover_research.py`: price, momentum, financial, event evidence
- `app/services/overview/market_movers_readiness.py`: complete / partial / blocked와 typed gap

기존 `app/services/overview/market_movers.py` public function은 facade로 유지한다.

### Web And React

- `app/web/overview/market_movers.py`: tab orchestration만 소유
- `app/web/overview/market_movers_payloads.py`: DB-backed read model을 component payload로 조합
- `app/web/overview/market_movers_actions.py`: session selected state와 bounded action dispatch
- 기존 `app/web/overview/market_movers_helpers.py`: 기존 import를 위한 facade와 단계적 migration
- React shell: presentation state와 사용자 interaction 소유
- React child components: `MarketMoversCommandLine`, `RankingBoard`, `BreadthContext`, `QuickResearch`, `StockResearchTabs`, `FinancialFactorChart`

기존 separate Streamlit ranking, sector iframe, investigation surface를 한 shell로 통합한다.

## Data Flow

```text
Ingestion / Refresh Job
        -> DB
        -> Loader / Service Read Models
        -> Streamlit Payload Adapter
        -> One React Shell
        -> user selection / bounded action event
        -> Streamlit Action Dispatch
        -> Job -> DB -> rerun
```

React는 계산 source of truth가 아니다. ranking, group state, financial factor, outlook gate는 Python service가 계산하고 React는 선택과 표현만 담당한다.

## Error Handling

- partial data는 local section degradation으로 처리한다.
- ranking row가 없어도 group context가 있으면 가능한 section은 유지한다.
- group market cap coverage가 부족하면 bellwether 순위를 숨기고 이유를 표시한다.
- financial factor source가 없으면 해당 button을 disabled / unavailable로 표시한다.
- conditional outlook gate가 실패하면 forecast number를 보내지 않는다.
- refresh 실패는 마지막 성공 결과를 current로 위장하지 않고 basis와 failure를 분리한다.
- component payload schema mismatch는 fallback empty state와 method disclosure로 처리한다.

## Verification Contract

### Python Unit And Contract Tests

- raw 17 label -> canonical 11 sector mapping
- canonical filter와 breadth membership 일치
- daily / weekly / monthly ranking basis
- missing row exclusion과 metric별 denominator
- limited-history와 provider gap 분류
- sector / industry minimum group size와 Unknown isolation
- latest market-cap Top 3와 cap coverage
- flow state classification
- conditional outlook sample / OOS suppression
- reported diluted EPS, four-quarter TTM EPS, current PER
- historical PER suppression
- financial factor units와 unavailable state

### React Tests

- ranking row -> selected quick research handoff
- Sector / Industry switch
- complete / partial / blocked rendering
- report period와 financial factor의 independent state
- one-factor-at-a-time chart selection
- unavailable factor control
- detail tab state와 responsive stacking

### Browser QA

- desktop one-shell hierarchy
- narrow layout no overflow
- ranking selection interaction
- group selection과 Top 3 visibility
- financial period / factor switching
- chart 약 70% / readout 약 30% desktop balance
- stale / partial / blocked examples
- 최종 사용자 QA screenshot 1장 이상

## Non-Goals

- broker order, live approval, auto rebalance
- buy / sell recommendation
- provider direct UI fetch
- raw job / saved row operations dashboard
- unvalidated sector probability
- PIT taxonomy 없는 industry forecast
- historical market-cap reconstruction

## Implementation Roadmap

전체 roadmap은 5차다.

| 차수 | 목적 | 완료 조건 | Current status |
| --- | --- | --- | --- |
| 1차 | 현행 감사와 correctness contract | stale, taxonomy, PER, handoff 문제 확정 | 완료 |
| 2차 | IA와 visual / interaction contract | A안, data state, outlook, stock research, architecture 승인 | 완료 |
| 3차 | data / read-model hardening | canonical filter, typed gaps, Top 3, industry, financial contract test | 미착수 |
| 4차 | one-shell React implementation | ranking / breadth / research 통합과 responsive QA | 미착수 |
| 5차 | sector conditional outlook와 closeout QA | OOS gate, publication suppression, full Browser QA | 미착수 |

다음 implementation plan은 3차만 상세화한다. 4차와 5차는 3차 payload contract와 검증 결과를 확인한 뒤 별도 계획으로 진행한다.

## Risks And Mitigations

| Risk | Mitigation |
| --- | --- |
| current sector membership을 historical membership처럼 사용 | Level 1 current flow와 Level 2 sector proxy를 분리하고 industry outlook 보류 |
| market cap missing으로 Top 3 왜곡 | positive cap coverage 공개, 부족하면 bellwether 숨김 |
| annual / quarterly duration 혼동 | report period independent control과 basis label |
| 서로 다른 factor 단위 혼합 | one factor / one axis 원칙 |
| operations UI가 다시 첫 화면을 점유 | trust line + primary action 1개, raw result disclosure |
| giant helper / service에 새 logic 집중 | public facade 유지 + bounded read model extraction |
| conditional distribution이 추천처럼 보임 | median과 range, sample, drawdown, OOS status를 함께 표시하고 gate 실패 시 suppression |

## Decision Record

- Primary job: `움직인 종목 발견 + 시장 확산 확인`
- Chosen IA: `A안 결정형 워크벤치`
- Research location: same-shell expandable section
- Group modes: Sector and Industry
- Sector bellwether: latest profile market cap Top 3
- Sector outlook: current flow + gated historical conditional distribution
- Industry outlook: current flow only until PIT taxonomy readiness
- Financial controls: report period and factor separated
- Financial chart: single factor, unit-specific axis, previous large chart retained
- Historical PER: removed until PIT-correct series exists
