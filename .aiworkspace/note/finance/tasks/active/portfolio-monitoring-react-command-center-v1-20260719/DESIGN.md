# Portfolio Monitoring React Command Center V1 Design

Status: Approved In Conversation / Written Spec Pending Review
Last Updated: 2026-07-19

## 이걸 하는 이유?

`Operations > Portfolio Monitoring`의 원래 목적은 Backtest Analysis에서 후보를 만들고,
Practical Validation과 Final Review를 통과한 대상만 선정 이후 계속 추적하는 것이었다.
현재 프로토타입은 Final Review selected 후보, 사용자 monitoring portfolio, 전략 slot,
DB-backed replay, 그룹 수익률·CAGR·MDD·value curve를 계산할 수 있다.

하지만 실제 화면은 약 3,425줄의 Streamlit renderer와 약 5,350줄의 read model에
관리·재실행·진단·감사 기능이 누적되어 있다. 사용자가 실제로 끝내려는 일인
`그룹 만들기 -> 항목 등록 -> 전체 성과 확인 -> 개별 원인 확인 -> 위험 변화 판단`보다
run/status/table 중심의 운영 정보가 앞선다. 직접 미국 주식·ETF를 등록하는 계약,
시작일 종가 기준 정수 수량, 서로 다른 시작일의 현금 처리, 항목 추적 종료 이후의
그룹 이력, deterministic 강점·약점·매크로 진단도 아직 없다.

이번 개편은 기존 계산 패널을 보기 좋게 재배치하는 일이 아니다. 사용자가 선정 이후
포트폴리오를 실제로 구성하고 지속적으로 판단하는 user-facing product surface를
Overview / Market Context와 같은 React one-shell로 다시 만든다.

## Approved Product Goal

Portfolio Monitoring의 중심 질문을 다음으로 고정한다.

> 내가 추적하기로 한 자산과 검증 포트폴리오의 현재 성과는 어떠하며, 무엇이 강점이고 무엇을 다시 확인해야 하는가?

사용자는 하나의 Command Center에서 다음을 끝낼 수 있어야 한다.

1. 기본 포트폴리오 또는 추가 그룹을 선택한다.
2. 미국 주식·ETF 또는 Final Review 통과 포트폴리오를 최대 10개 등록한다.
3. 시작일과 금액 또는 정수 수량 기준을 확인하고 저장한다.
4. 그룹 투자금, 현재 가치, 수익률, CAGR, MDD와 통합 가치곡선을 본다.
5. 각 항목의 성과, 그룹 기여도, 가격·전략 상세를 연다.
6. 집중도·추세·drawdown·매크로 조건에서 나온 강점·취약점과 변화 조건을 본다.

이 화면은 live approval, broker account, 실제 주문, 자동 리밸런싱을 만들지 않는다.

## Approved Scope And Decisions

| 영역 | 승인 결정 |
|---|---|
| React 범위 | 기존 Operations route를 유지하고 내부의 Streamlit product UI를 React one-shell로 교체 |
| 기준 디자인 | Overview / Market Context와 Futures Macro의 Python read model + React presentation 패턴 |
| 첫 화면 | Portfolio-first Command Center |
| 그룹 | 첫 진입 시 기본 그룹 1개 자동 생성, 추가와 이름 변경 지원 |
| 항목 제한 | 그룹당 최대 10개, backend와 React 양쪽에서 검증 |
| 직접 항목 | 미국 주식과 ETF를 DB catalog에서 검색 |
| 전략 항목 | Final Review `monitoring_candidate == true`만 선택 |
| missing data | 시작일 가격이 DB에 없으면 등록하지 않고 `데이터 준비 필요` 표시 |
| 추가 UX | 우측 Context Drawer, 모바일은 full-width sheet |
| 금액 입력 | 정확한 dollar notional, direct security는 virtual fractional units 허용 |
| 수량 입력 | 직접 주식·ETF만 지원, 1주 이상 정수만 허용 |
| 전략 입력 | fixed notional만 지원 |
| 휴장일 | 요청일 이후 첫 거래일을 effective start로 사용하고 두 날짜를 모두 표시 |
| 다른 시작일 | 시작 전 배정금은 그룹 현금으로 유지 |
| 추적 종료 | 과거에서 삭제하지 않고 종료일 평가금액을 현금으로 전환 |
| 배당 | stored dividend event를 현금으로 누적하고 자동 재투자하지 않음 |
| 분할 | stored split event 기준으로 보유 수량 조정 |
| 진단 | 계층형 deterministic rule engine, AI 필수 호출 없음 |
| 확률 | 초기 미공개, historical as-of OOS calibration과 publication gate 이후만 공개 |

## Considered Product And Diagnosis Approaches

### Approach A. Threshold Alerts Only

집중도, 최근 수익률, 이동평균, MDD 같은 개별 임계값만 표시한다.

- 장점: 빠르고 단순하다.
- 단점: 같은 원인의 경고가 중복되고 포트폴리오 전체 구조와 매크로 관계가 약하다.
- 결정: 채택하지 않는다.

### Approach B. Layered Deterministic Diagnosis

노출 사실, 가격·성과, 포트폴리오 구조, 매크로 조건, 근거형 안내문을 분리한다.

- 장점: 재현 가능하고 테스트 가능하며 AI 비용과 문구 변동이 없다.
- 장점: coverage, confidence, source date를 판정과 함께 공개할 수 있다.
- 장점: 확률 모델이 준비되기 전에도 안전한 현재 관찰 신호를 제공한다.
- 단점: exposure adapter와 versioned policy가 필요하다.
- 결정: 채택한다.

### Approach C. Predictive Probability First

현재 포트폴리오의 하락 가능성을 처음부터 확률로 표시한다.

- 장점: 사용자에게 직관적인 숫자를 제공한다.
- 단점: historical point-in-time exposure, survivorship-safe replay, OOS calibration이 없으면
  거짓 정밀도를 만든다.
- 결정: 6차 publication gate 이후의 선택 기능으로 미룬다.

## Target User Flow

### 1. First Entry And Group Rail

사용자 monitoring group이 없으면 `기본 포트폴리오`를 하나 생성한다. 기본 그룹은
빈 상태에서도 선택되어 있어야 하고 첫 행동은 `항목 추가`다.

상단 group rail은 다음 정보를 보여준다.

- 그룹 이름
- 등록 항목 수 `n / 10`
- 현재 상태 `정상 / 확인 필요 / 데이터 부족`
- active group marker
- `+ 포트폴리오`

그룹 이름은 active group command band에서 변경한다. V1에서 그룹 삭제는 primary action으로
두지 않는다. 잘못 만든 추가 그룹의 soft-delete는 management disclosure에서 제공하되,
기본 그룹은 삭제할 수 없다.

### V1 Virtual Scenario Semantics

V1 group은 broker/account cash-flow ledger가 아니라 현재 사용자가 구성한 가상 monitoring
scenario다. 항목을 과거 effective start로 새로 등록하면 현재 configuration 기준으로 group
history를 다시 계산한다.

- active item 최대 10개이며 ended item은 limit에 포함하지 않는다.
- group read model은 `configuration_version`과 `configuration_fingerprint`를 표시한다.
- backdated add/rename/end 뒤에는 `현재 구성으로 재계산됨`과 recalculated timestamp를 표시한다.
- 과거의 실제 입출금이나 실현손익을 주장하지 않는다.
- actual cash contribution/withdrawal과 money-weighted return은 live-account boundary가 정해진
  별도 후속 범위다.

### 2. Context Drawer Item Builder

`+ 항목 추가`를 누르면 현재 Command Center 위에 우측 Drawer가 열린다. 사용자는
기존 그룹 성과 맥락을 잃지 않는다. 760px 이하에서는 drawer를 full-width sheet로 전환한다.

Drawer는 세 단계다.

```text
1. 대상 선택
2. 투자 기준
3. 등록 전 확인
```

#### Direct U.S. Stock / ETF

- `finance_meta.nyse_stock`, `nyse_etf`, `nyse_asset_profile` 기반 symbol/name 검색
- instrument kind, name, exchange, price coverage, latest price date 표시
- 요청 시작일 이후 usable daily close가 있을 때만 선택 가능
- 데이터가 없으면 저장 CTA를 비활성화하고 missing range와 Ingestion handoff를 표시
- UI나 React에서 provider를 직접 호출하지 않음

#### Final Review Portfolio

- explicit `monitoring_candidate == true`가 있으면 authoritative filter로 사용
- legacy selected-route row는 compatibility adapter에서만 지원
- source title, decision date, strategy/components, Final Review monitoring condition 표시
- same decision이 active item으로 이미 존재하면 중복 등록 차단

#### Investment Inputs

| source | mode | contract |
|---|---|---|
| stock / ETF | fixed notional | dollar amount / effective start raw close로 fractional virtual units 산출 |
| stock / ETF | fixed shares | 1 이상 정수 shares, effective start raw close와 곱해 initial capital 산출 |
| monitoring candidate | fixed notional | selected strategy runtime value curve에 initial capital 적용 |
| monitoring candidate | fixed shares | 지원하지 않음 |

등록 전 확인 화면은 다음을 고정한다.

- requested start date
- effective start date
- start close와 price source
- funding mode
- input notional 또는 integer shares
- computed initial capital
- source identity와 duplicate check
- data readiness와 common caveat

### 3. Command Center First Read

active group의 first-read 순서는 다음과 같다.

1. group identity와 item count
2. 계획 투자금, 현재 가치, 손익, 총 수익률, CAGR, MDD
3. group value curve
4. 지금 확인할 변화 최대 3개
5. 현재 강점과 현재 취약점
6. 구성 항목과 contribution
7. 선택한 항목 상세
8. method / source / boundary disclosure

run count, saved row count, raw status table, registry path는 first-read KPI가 아니다.

### 4. Individual Item Detail

group chart 아래의 item row를 선택하면 동일 React shell 안에서 detail section을 연다.

공통 정보:

- source identity
- requested/effective start
- initial capital와 current value
- return, short-window annualized marker/CAGR, MDD
- group profit/loss contribution와 downside contribution
- item value curve
- data basis date와 coverage

direct security 추가 정보:

- current shares, split adjustments, accumulated cash dividends
- 1/3/6개월 return
- 50D / 200D moving average position과 persistence
- stock sector 또는 ETF exposure coverage

selected strategy 추가 정보:

- Final Review decision identity와 selected reason
- latest target snapshot와 component contribution
- existing recheck/freshness/provider evidence 중 사용자 판단에 필요한 요약
- raw audit detail은 secondary disclosure

### 5. Tracking End

`항목 제거`는 과거 row 삭제나 broker sell action이 아니다. 사용자 확인 뒤 item에
tracking end event를 기록한다.

- direct security: effective end date의 split-adjusted shares × raw close + accumulated cash dividend
- selected strategy: effective end date의 latest usable strategy value
- 종료 평가금액은 이후 group cash lane으로 유지
- contribution history는 종료일까지 보존
- 같은 source를 나중에 다시 등록하면 새 item identity와 새 start contract를 만든다

## Architecture Boundary

```text
Operations route / thin Streamlit bridge
  -> Portfolio Monitoring React workbench
       -> user intent event
  -> app/services/portfolio_monitoring/*
       -> finance/loaders/price.py
       -> monitoring persistence adapter
       -> Final Review read adapter
       -> Overview compact macro snapshots
  -> versioned portfolio_monitoring_workspace_v1 read model
  -> React render
```

### React Ownership

- group/item selection intent
- drawer draft state
- search query intent와 result presentation
- create/rename/add/end confirmation intent
- chart hover/focus, selected item, disclosure state
- Python projection rendering

React는 다음을 계산하지 않는다.

- effective trading date
- price readiness
- duplicate/max-item validation
- return/CAGR/MDD
- exposure coverage
- diagnosis severity/confidence
- macro risk state

### Python Service Ownership

새 package를 둔다.

```text
app/services/portfolio_monitoring/
  catalog.py
  commands.py
  persistence.py
  valuation.py
  exposure.py
  diagnosis.py
  macro_context.py
  read_model.py
  schemas.py
```

- `catalog.py`: DB stock/ETF와 monitoring candidate search projection
- `commands.py`: idempotent create/rename/add/end command validation
- `persistence.py`: DB repository와 legacy JSONL import adapter
- `valuation.py`: direct security/selected strategy daily value lane과 group aggregation
- `exposure.py`: stock profile, ETF holdings, strategy target exposure normalization
- `diagnosis.py`: versioned deterministic policy와 message projection
- `macro_context.py`: economic cycle/futures macro/materialized asset context adapter
- `read_model.py`: React에 전달할 immutable workspace projection
- `schemas.py`: versioned command/read model identity와 JSON-safe validation

기존 `app/runtime/backtest/read_models/final_selected_portfolios.py`는 legacy selected strategy
replay와 compatibility helper를 제공하되 새 group/item persistence와 product read model owner가
아니다. 현재 3,425줄 Streamlit page는 thin component mount와 fallback error 안내로 축소한다.

### Streamlit Bridge

Streamlit은 route와 component bridge만 소유한다.

1. service read model load
2. React component render
3. one event receive
4. server-side command validation/execute
5. result notice와 fresh projection rerun

각 command는 client command ID를 받아 같은 event 재전송 시 중복 row를 만들지 않는다.
React build가 없으면 full legacy dashboard를 다시 렌더링하지 않고 build/error/recovery 안내와
read-only active group summary만 표시한다.

## Persistence Model

장기 monitoring lifecycle은 기존 mutable saved JSONL row보다 DB가 적합하다. 신규 table은
`finance_meta`에 둔다.

### `monitoring_portfolio_group`

주요 field:

- `portfolio_group_id`
- `name`
- `is_default`
- `status`
- `created_at`, `updated_at`, `deleted_at`
- optimistic concurrency용 `version`

### `monitoring_portfolio_item`

주요 field:

- `monitoring_item_id`, `portfolio_group_id`
- `source_type`: `direct_security | selected_strategy`
- `source_ref`: symbol 또는 Final Review decision ID
- `instrument_kind`: `stock | etf | strategy`
- `requested_start_date`, `effective_start_date`
- `funding_mode`: `fixed_notional | fixed_shares`
- `input_notional`, `input_shares`
- `entry_close`, `initial_capital`
- `tracking_end_requested_date`, `tracking_end_effective_date`, `exit_value`
- `status`: `active | ended | data_review`
- `metadata_json`
- `created_at`, `updated_at`

### `monitoring_portfolio_command`

command idempotency와 audit를 위해 다음을 기록한다.

- `command_id`
- `command_type`
- `target_id`
- `request_fingerprint`
- `status`
- `result_ref`
- `created_at`

raw price, full ETF holdings, full macro series, strategy result curve는 이 table JSON에 복제하지
않는다. 원천 DB와 service read model에서 읽는다.

### Legacy Preservation

`.aiworkspace/note/finance/saved/SELECTED_DASHBOARD_PORTFOLIOS.jsonl`은 삭제하거나 재작성하지
않는다. idempotent importer가 legacy portfolio와 strategy slot을 새 group/item row로 복사한다.

- 기존 ID는 `metadata_json.legacy_*` provenance로 보존
- import marker와 source fingerprint로 중복 import 차단
- import 전후 group/item count와 missing decision을 report
- cutover 검증이 끝나기 전까지 legacy read adapter 유지
- 자동 destructive cleanup 없음

## Valuation Contract

### Effective Start

requested date가 거래일이 아니거나 해당 symbol price가 없으면 이후 첫 usable daily row를 찾는다.
행이 없으면 registration blocker다. 상장 전 날짜, delisted/no-data, ticker resolution issue를
0 가격이나 이전 가격으로 보간하지 않는다.

### Direct Security Lane

entry 기준은 raw close다.

```text
fixed_notional units = input_notional / entry_close
fixed_shares units = integer input_shares
initial_capital = units * entry_close
```

daily lane은 stored event를 날짜순으로 적용한다.

- split: effective units를 split factor로 조정
- dividend: 해당 시점 effective units × stored dividend를 cash bucket에 누적
- market value: effective units × raw close
- item total value: market value + accumulated dividend cash

stored `adj_close` normalized curve는 cross-check로 계산하되 primary current value를 대체하지
않는다. raw/split/dividend event와 adjusted-return gap이 tolerance를 넘으면 item을
`data_review`로 표시한다. V1 tolerance는 end total-return absolute gap `0.50%p` 또는
single-session continuity gap `1.00%p` 중 하나를 넘는 경우다. split/dividend source gap이
확인되면 raw ledger 값을 조용히 보정하지 않는다.

### Selected Strategy Lane

Final Review source가 참조하는 replay contract로 effective start 이후 strategy value curve를
만든다. fixed notional을 normalized strategy curve에 적용한다. strategy 내부 holdings와
리밸런싱은 strategy runtime이 소유하며 monitoring layer가 shares를 만들지 않는다.

### Cash Before Start And After End

group planned capital은 모든 item initial capital의 합이다.

- earliest group date부터 item effective start 전까지 initial capital은 cash
- tracking end 이후 exit value는 cash
- V1 cash return은 0%이며 별도 yield를 합성하지 않음
- cash는 group value와 allocation에 포함하고 `대기 현금 / 종료 현금`을 구분

### Common Basis Date And Alignment

group KPI는 active item 모두가 usable value를 갖는 최신 공통 날짜를 사용한다.

- 서로 다른 최신 날짜를 섞어 `현재 가치`를 만들지 않음
- missing session은 exchange calendar와 source coverage를 확인
- 임의 interpolation 없음
- start 전과 end 후 cash lane은 모든 날짜에 usable value를 제공
- 하나의 active item이 stale하면 group basis date와 warning에 반영

### Metrics

- invested capital: item initial capital 합
- current value: common basis date의 item total value와 cash 합
- P&L: current value - invested capital
- total return: current value / invested capital - 1
- MDD: daily group value curve 기준
- CAGR: actual day count annualization, 365일 미만은 `단기 구간 연환산` marker와 day count 표시
- contribution: item value change / group initial capital
- downside contribution: group negative-return sessions에서 item 손실 기여

## Layered Diagnosis Contract

### 1. Exposure Facts

- direct stock: `nyse_asset_profile` sector/industry
- ETF: provider holdings/exposure snapshot 우선, 없으면 top-level ETF category만 사용
- selected strategy: latest target snapshot과 component symbols/weights
- unavailable look-through는 추정하지 않고 coverage gap으로 남김
- overlapping look-through symbol은 group effective exposure에서 합산

### 2. Behavior Facts

- 21/63/126 session return
- 50D/200D moving average distance와 consecutive-below sessions
- current drawdown, MDD, realized volatility
- 63-session pairwise correlation과 cluster weight
- total/downside contribution

### 3. V1 Policy Defaults

정책은 Python versioned catalog로 소유하고 React에 hard-code하지 않는다.

| rule | watch | high/re-review |
|---|---|---|
| single item concentration | group weight >= 25% | >= 40% |
| sector/asset exposure concentration | effective exposure >= 35% | >= 50% |
| 200D trend break | close below 200D for >= 5 sessions | >= 20 sessions or distance <= -10% |
| current drawdown | <= -10% | <= -15% |
| correlation cluster | 63D correlation >= 0.80 and cluster weight >= 40% | cluster weight >= 60% |
| downside contribution | one item >= 35% of group downside | >= 50% |
| recent weakness | 63D return <= -10% | <= -20% |

Final Review에 더 보수적인 explicit monitoring threshold가 저장되어 있으면 해당 strategy에는
그 threshold를 우선하고 policy provenance를 표시한다.

### 4. Macro Context Matching

재사용 source:

- economic cycle current/+1M/+2M status와 publication status
- Futures Macro risk-on/growth/rate/dollar/safe-haven/inflation family score
- materialized 5D/20D current regime/conditional outlook
- Overview asset pathways의 gold, dollar, WTI, copper, rates, S&P context

macro rule은 portfolio loss probability가 아니라 exposure-context match다.

예:

- tech exposure >= 35% + Futures risk-on <= -20 또는 NQ persistent weakness
- gold exposure >= 25% + gold 63D weakness + real-yield adverse pathway
- duration exposure >= 25% + rate pressure >= 20
- cyclical exposure >= 35% + economic activity weakening + growth score <= -20

### 5. Coverage And Confidence

| confidence | contract |
|---|---|
| HIGH | exposure coverage >= 90%, price current, macro publication READY |
| MEDIUM | coverage >= 70% 또는 economic cycle LIMITED / 일부 context provisional |
| LOW | coverage < 70%, stale source, 핵심 look-through missing |

LOW confidence signal은 `지금 확인할 변화` 상위 3개에 올리지 않는다. 대신 데이터 부족으로
분리한다. LIMITED/PROVISIONAL macro context는 severity를 단독으로 HIGH로 올릴 수 없다.

### 6. Message And Priority

각 diagnosis row는 다음을 포함한다.

- `rule_id`, `policy_version`
- strength/weakness/data-gap classification
- severity와 persistence
- affected weight와 contribution
- measured fact와 threshold
- source dates와 coverage/confidence
- portfolio meaning
- change condition / next check

priority는 severity, affected weight, persistence, confidence를 결합하되 같은 root exposure와
market condition에서 파생된 row는 하나로 합친다. first-read는 최대 3개만 표시하고 전체 row는
근거 disclosure에 둔다.

문구는 `개선 필요`만 단독으로 쓰지 않는다. 반드시 무엇이, 어느 기준을, 얼마나 벗어났고,
어떤 값이 바뀌면 다시 판단할지를 포함한다. 매수·매도 수량이나 목표 비중을 지시하지 않는다.

## React Command Center Information Architecture

```text
Portfolio Monitoring
  Group Rail / + Portfolio
  Active Group Command Band / rename / + item
  KPI strip
  Group value chart
  Now To Review (max 3)
  Strengths / Weaknesses
  Macro Risk Observation
  Item List + Contribution
  Selected Item Detail
  Method / Source / Boundary
```

시각 언어는 다음을 재사용한다.

- Overview 경제사이클의 status -> evidence -> change condition hierarchy
- Market Context의 integrated chart와 source/basis disclosure
- Futures Macro의 coverage/status/provisional distinction
- Institutional Portfolios의 full-width chart와 selected detail pattern

React는 현재 화면의 수십 개 table/expander를 그대로 복제하지 않는다. continuity, provider,
preflight, audit는 사용자 질문에 직접 필요한 요약만 item detail/method disclosure로 투영한다.

## Error And Recovery Contract

| error kind | visible behavior | write behavior |
|---|---|---|
| group absent | default group creation CTA/automatic idempotent create | one default row only |
| max items | `10/10`과 add disabled | no write |
| duplicate item | existing active item 안내 | no write |
| invalid shares | integer >= 1 안내 | no write |
| missing start price | `데이터 준비 필요`, missing range | no write |
| stale after registration | common basis date 후퇴, source warning | item preserved |
| one item valuation error | group `PARTIAL`, failed item explicit | silent exclusion 금지 |
| command retry | existing command result replay | duplicate row 금지 |
| React component missing | read-only error/recovery summary | no fallback mutation |
| legacy import mismatch | import report and blocked cutover | legacy file preserved |
| diagnosis coverage LOW | 판단 불가/data gap | alert fabrication 금지 |

## Verification Contract

### Python TDD

- default group idempotency
- group rename/version conflict
- max 10 and duplicate source
- stock/ETF combined search and kind identity
- monitoring candidate authoritative filter
- weekend/holiday effective start
- fixed notional fractional units
- fixed shares integer validation
- split and cash dividend ledger
- pre-start and post-end cash lane
- staggered-start group aggregation
- common basis date and stale isolation
- short-window CAGR marker and MDD
- legacy import idempotency and preservation
- diagnosis thresholds, root dedup, confidence cap
- macro LIMITED/PROVISIONAL severity cap

### React Verification

- TypeScript typecheck
- production build
- group rail selection
- Context Drawer three-step flow
- direct/strategy source switch
- missing-price disabled state
- amount vs integer-share form
- command pending/success/error lifecycle
- full-width group chart and item detail
- top-three diagnosis and evidence disclosure
- 1440px, 760px, 420px overflow and focus/keyboard QA

### Integration / Browser QA

- actual existing legacy monitoring portfolios imported without source loss
- actual monitoring candidate search
- one direct stock and one ETF registration fixture
- one selected strategy group with staggered start
- item tracking end to cash
- stale item common-basis behavior
- Overview visual comparison
- Operations Console summary handoff
- screenshot at each user-facing stage closeout

Protected registry, saved JSONL, run history, `.superpowers/`, screenshots, and generated artifacts are
not staged unless explicitly requested.

## Six-Stage Roadmap

### 1차. Contract And Storage Foundation

목적:
- group/item/command schema와 valuation semantics를 코드 계약으로 고정한다.

주요 범위:
- `finance/data/db/schema.py`
- `app/services/portfolio_monitoring/schemas.py`
- persistence contract tests
- legacy import dry-run report

완료 조건:
- DB schema, command identity, start/end/cash/dividend/split rules가 Streamlit 없이 검증된다.

다음 연결:
- 2차 service implementation의 stable boundary가 된다.

### 2차. Monitoring Service Foundation

목적:
- 그룹과 항목을 만들고 공통 가치곡선과 KPI를 계산한다.

주요 범위:
- catalog/commands/persistence/valuation/read_model
- stock/ETF search
- Final Review candidate adapter
- legacy non-destructive import

완료 조건:
- 최대 10개, 두 funding mode, staggered start, tracking end, group KPI를 pure tests로 통과한다.

다음 연결:
- 3차 React가 하나의 versioned read model만 읽는다.

### 3차. React Portfolio Command Center

목적:
- 기존 Streamlit product UI를 Portfolio-first React one-shell로 교체한다.

주요 범위:
- `app/web/streamlit_components/portfolio_monitoring_workbench/`
- thin Python component adapter
- `app/web/final_selected_portfolio_dashboard.py` cutover
- Operations summary compatibility

완료 조건:
- group rail, Context Drawer, KPI, group chart, item list/detail이 desktop/mobile에서 동작한다.

다음 연결:
- 4차 diagnosis를 같은 shell에 추가한다.

### 4차. Strength And Weakness Diagnosis

목적:
- exposure/behavior/portfolio rules를 근거형 강점·취약점으로 투영한다.

주요 범위:
- exposure adapter
- versioned diagnosis policy
- top-three/root dedup
- coverage/confidence

완료 조건:
- concentration, trend, drawdown, correlation, contribution fixture가 설명 가능한 row를 만든다.

다음 연결:
- 5차 macro context match의 portfolio side가 완성된다.

### 5차. Macro Risk Observation

목적:
- 경제사이클, Futures Macro, asset pathways를 portfolio exposure와 결합한다.

주요 범위:
- compact snapshot adapters
- context match policy
- low/medium/high observation state
- source/freshness/coverage disclosure

완료 조건:
- unvalidated loss probability 없이 current observation과 change condition을 표시한다.

다음 연결:
- 6차 historical calibration 후보와 snapshot history를 만든다.

### 6차. Calibration And Operational History

목적:
- macro-conditioned risk가 확률로 공개 가능한지 historical as-of 검증한다.

주요 범위:
- historical exposure/macro replay
- OOS calibration and baseline comparison
- publication gate
- diagnosis snapshot history와 persistence/cooldown

완료 조건:
- gate 통과 전 probability suppression, 통과 후 calibrated probability와 limitations가 검증된다.

다음 연결:
- 장기 운영 closeout과 durable docs 승격을 수행한다.

## Non-Goals

- broker account sync
- live holdings import
- actual account contribution/withdrawal ledger와 money-weighted return
- buy/sell order generation
- automatic rebalance
- AI-generated daily advice as a required dependency
- UI/provider direct fetch
- missing price/macro synthesis
- current universe로 historical survivorship를 숨기는 backfill
- legacy JSONL deletion
- Operations System/Data Health의 React migration

## Documentation And Handoff

- discovery audit: `.aiworkspace/note/finance/researches/active/2026-07-portfolio-monitoring-react-redesign/`
- implementation task: `.aiworkspace/note/finance/tasks/active/portfolio-monitoring-react-command-center-v1-20260719/`
- durable flow updates after implementation: `docs/flows/BACKTEST_UI_FLOW.md`,
  `docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- durable architecture/data updates after implementation: `docs/architecture/`, `docs/data/`
- root logs remain 3~5 line pointers, not detailed implementation history
