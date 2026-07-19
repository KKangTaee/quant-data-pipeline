# Current Project Audit

Status: Discovery
Last Updated: 2026-07-19

## Summary

요청한 Portfolio Monitoring 전면 개편은 구현 가능하다. 현재 저장소에는 Final Review 통과
후보 필터, 사용자 monitoring portfolio 저장, 전략 slot별 시작일·가상 투자금, DB-backed
performance replay, 그룹 합산 현재가치·손익·수익률·CAGR·MDD·value curve 계산이 이미 있다.

가장 큰 결손은 계산 엔진보다 제품 모델과 UI 경계다. 현재 화면은 약 3,425줄의 Streamlit
renderer와 약 5,350줄의 read model에 기능이 누적되어 있고, 직접 미국 주식·ETF를 monitoring
item으로 등록하는 계약, 시작일 종가 기준 수량 계약, 최대 10개 제한, 규칙 기반 portfolio
diagnosis, portfolio exposure와 macro state의 결합 read model은 아직 없다.

## Current Product Promise

현재 제품은 Backtest Analysis에서 후보를 만들고, Practical Validation과 Final Review를 거친
`monitoring_candidate`만 Operations에서 사후 관찰하는 evidence-first research workspace다.
Portfolio Monitoring은 live approval, broker order, account sync, auto rebalance가 아니다.

## Current Workflow

```text
Backtest Analysis
  -> Practical Validation
  -> Final Review monitoring_candidate
  -> FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl
  -> SELECTED_DASHBOARD_PORTFOLIOS.jsonl
  -> Operations > Portfolio Monitoring
```

현재 monitoring portfolio는 Final Review decision을 strategy slot으로 담는다. slot은 start,
optional end/latest, initial capital, memo를 저장한다. 사용자가 명시적으로 scenario update를
실행하면 기존 strategy replay contract와 DB price history를 사용해 개별 및 그룹 성과를 계산한다.

## Implemented Capabilities

| Area | Implemented fact | Reuse potential |
| --- | --- | --- |
| Candidate boundary | v3 `monitoring_candidate == true`를 authoritative filter로 사용 | 높음 |
| Portfolio groups | 사용자 portfolio create/update/name/description/soft-delete | 높음 |
| Strategy slots | selected decision add/remove, start/end/latest, initial capital, memo | 높음 |
| Scenario replay | selected strategy runtime replay와 latest DB market date 사용 | 높음 |
| Group result | invested capital, current value, P&L, return, CAGR, MDD, value curve, strategy rows | 높음 |
| Monitoring evidence | freshness, provider evidence, continuity, recheck comparison, review signals | 부분 재사용 |
| Direct securities | 미국 주식·ETF를 독립 monitoring item으로 등록 | 미구현 |
| Share-at-start input | 시작일 종가 기준 수량 산정 및 저장 | 미구현 |
| Portfolio diagnosis | concentration/trend/drawdown/exposure/macro 규칙 엔진 | 미구현 |
| React UI | Overview와 Futures Macro는 React custom workbench 사용 | 패턴 재사용 가능 |

## Surface Role Classification

| Surface | Role | Implication |
| --- | --- | --- |
| Portfolio Monitoring | user-facing product surface | React 전면 개편 우선 대상 |
| Operations Console | mixed/support surface | portfolio summary handoff만 동기화 |
| System / Data Health | internal/ops console | Streamlit 유지 가능 |
| Final Review | user-facing decision surface | monitoring candidate handoff 계약 보존 |
| Overview Market Context/Futures Macro | user-facing context surface | 시각 언어와 compact DB snapshot 재사용 |

## Architecture And Ownership

| Boundary | Current owner |
| --- | --- |
| Monitoring UI | `app/web/final_selected_portfolio_dashboard.py` |
| Table/UI helpers | `app/web/final_selected_portfolio_dashboard_helpers.py` |
| Portfolio persistence/read models | `app/runtime/backtest/read_models/final_selected_portfolios.py` |
| Saved setup | `.aiworkspace/note/finance/saved/SELECTED_DASHBOARD_PORTFOLIOS.jsonl` |
| Final Review source | `.aiworkspace/note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl` |
| Price history | `finance_price.nyse_price_history` via `finance/loaders/price.py` |
| Stock/ETF universe | `finance_meta.nyse_stock`, `nyse_etf`, `nyse_asset_profile` |
| Economic cycle | `app/services/overview/economic_cycle.py` compact DB-backed read model |
| Futures macro | `app/services/futures_macro_snapshot.py` materialized compact snapshot |
| React patterns | `app/web/streamlit_components/*_workbench/` |

## Feasibility Findings

### Portfolio groups and editable names

이미 구현되어 있다. 첫 진입 시 default group을 자동 생성하는 정책과 이름 중복/삭제 후 default
복구 정책만 추가 설계하면 된다.

### Direct U.S. stock and ETF registration

구현 가능하다. stock과 ETF universe, asset profile, DB price loader가 존재한다. 다만 현재 검색
helper는 common stock 중심이므로 stock/ETF 통합 검색 service와 instrument identity contract가
필요하다. UI에서 provider를 직접 조회하지 않고 DB에 없는 가격은 Ingestion handoff로 처리해야 한다.

### Dollar and share input

구현 가능하다. `fixed_notional`은 입력 금액을 시작일 종가로 나누어 fractional units를 계산한다.
`fixed_shares`는 사용자가 수량을 입력하고 시작일 종가를 곱해 초기 투자금으로 확정한다.
Final Review portfolio strategy는 내부 구성 종목과 리밸런싱이 있으므로 `fixed_shares`를 지원하지
않고 `fixed_notional`만 허용하는 것이 타당하다.

시작일이 휴장일이면 이후 첫 거래일을 effective start로 쓰고, 원래 요청일과 실제 체결 기준일을
둘 다 표시해야 한다. 가격은 split/dividend 의미를 명확히 하기 위해 성과곡선에는 adjusted close,
수량 원가 표시에는 당시 raw close를 분리하는 계약 검토가 필요하다.

### Group and item performance

이미 strategy replay 기반 그룹 합산이 존재한다. direct security는 buy-and-hold value curve를 같은
canonical daily value curve 계약으로 변환하면 합산할 수 있다. 서로 다른 시작일은 해당 item 시작
전에는 현금으로 두는 방식이 가장 설명 가능하다.

### Strength and weakness diagnosis

AI를 매번 호출하지 않는 deterministic rule engine이 더 적합하다. 다음 계층으로 분리할 수 있다.

1. exposure facts: asset class, sector/theme, single-name/strategy concentration, overlap
2. behavior facts: 1/3/6개월 return, 50/200일선, realized volatility, drawdown, contribution
3. portfolio rules: concentration, correlation cluster, downside contribution, diversification benefit
4. context rules: economic cycle/futures macro와 현재 exposure의 조건부 일치·충돌
5. message templates: 사실, 기준, 의미, 다음 확인 조건을 조합

이 구조는 test 가능하고 설명 가능하며, 매일 AI 비용이나 문구 변동이 없다. AI는 후속에서 이미
계산된 fact를 요약하는 optional layer로만 둘 수 있다.

### Probabilistic macro risk signal

조건부로 가능하다. 현재 경제 사이클 모델은 1·2개월 horizon probability와 publication status를,
Futures Macro는 family score, regime/transition, historical pattern validation과 5D/20D conditional
path를 제공한다. 이를 portfolio exposure와 결합해 `현재 관찰 위험도` 또는 `조건부 취약도`를
계산할 수 있다.

다만 `포트폴리오 손실 확률`로 바로 표현하면 안 된다. 먼저 과거 as-of portfolio exposure와 macro
snapshot을 사용한 out-of-sample calibration이 필요하다. 검증 전에는 `위험 관찰: 낮음/보통/높음`,
coverage, confidence, 근거와 변화 조건으로 표시하고, 검증을 통과한 뒤에만 확률을 공개해야 한다.

## Weak Points And Product Friction

- 현재 Streamlit UI와 read model이 너무 크고 한 화면에 관리·진단·감사 기능이 누적됐다.
- 직접 등록 security와 selected strategy가 하나의 item contract로 통합되어 있지 않다.
- monitoring scenario 결과가 session 중심이라 지속적인 일별 관찰 이력 계약이 약하다.
- sector/asset exposure는 stock profile과 ETF holdings coverage에 따라 부분적일 수 있다.
- selected strategy 내부의 시점별 holdings가 없으면 정확한 현재 exposure 대신 target/latest snapshot만 사용한다.
- 진단 문구의 threshold, severity, cooldown, 중복 억제, data freshness 정책이 없다.

## Data And Validation Risks

- direct security start price와 성과 계산에서 raw close/adjusted close 의미를 혼동할 위험
- start date 이후 상장, 거래정지, ticker change, delisting 처리
- 서로 다른 시작일/달력/결측 가격을 합산할 때 임의 forward-fill 위험
- ETF holdings snapshot의 불완전성과 look-through 중복 계산
- Final Review 전략의 최신 holdings/exposure가 historical PIT가 아닐 가능성
- macro probability를 portfolio loss probability처럼 과대 해석할 위험
- survivorship bias가 있는 current stock/ETF universe를 과거 등록 검증에 사용하는 위험

## Tentative Roadmap

| 차수 | 목적 | 주요 범위 | 완료 조건 | 다음 연결 |
| --- | --- | --- | --- | --- |
| 1차 | 제품·데이터 계약 확정 | item/group schema, default group, start/amount/share 의미, React 경계 | 승인된 설계와 contract tests 목록 | 2차 서비스 분리 |
| 2차 | monitoring service foundation | persistence migration, stock/ETF search, canonical value curve, max 10 | Streamlit 없이 group/item CRUD와 계산 검증 | 3차 React shell |
| 3차 | React portfolio workbench | group selector, item builder, KPI, aggregate chart, item detail | desktop/mobile one-shell과 fallback QA | 4차 진단 |
| 4차 | 규칙 기반 강점·약점 | exposure/behavior/portfolio rules와 근거형 메시지 | deterministic fixtures와 severity 설명 가능 | 5차 macro 결합 |
| 5차 | macro risk context | cycle/futures snapshot 결합, coverage/confidence, 변화 조건 | probability 미공개 관찰 신호와 as-of 검증 | 6차 calibration |
| 6차 | 확률 calibration 및 운영화 | historical replay/OOS calibration, snapshot history/cadence | publication gate 통과 시에만 probability 공개 | 운영 closeout |

## Resolved Design Decisions

1. 기존 Operations route와 Streamlit bridge는 유지하되 visible product UI는 React one-shell로 교체한다.
2. direct U.S. stock/ETF는 Final Review 통과 요건 없이 monitoring-only item으로 허용하되 시작일 DB 가격이 필요하다.
3. group/item lifecycle은 DB에 저장하고 기존 saved JSONL은 비파괴 import/provenance source로 보존한다.
4. stock sector와 ETF/strategy look-through는 coverage를 명시한다. 부족한 exposure는 추정하지 않고 confidence를 낮춘다.
5. V1은 virtual scenario이며 backdated 구성 변경은 version/fingerprint와 함께 group history를 재계산한다.

## Implications For Further Research

- 외부 portfolio tracking 제품의 group/item builder와 risk explanation 패턴 비교
- probabilistic portfolio risk 표현의 calibration/publication 기준 조사
- 독립 React/API를 선택할 경우 기존 UI platform research의 service contract/API 단계 재검토
