# Market Movers Current Project Audit

Status: Active
Last Updated: 2026-07-20

## Summary

`Workspace > Overview > Market Movers`는 현재 필요한 기능 대부분을 이미 보유하지만, 사용자용 시장 탐색 화면과 수집/진단 콘솔이 한 개의 긴 세로 화면에 결합된 mixed/transitional surface다.

현재 흐름은 다음 순서다.

1. coverage / period / sector / Top N / ranking mode 선택
2. snapshot freshness와 수집/갱신 action 확인
3. 상위 종목 ranking board 탐색
4. 11개 canonical sector breadth 확인
5. missing row 진단 확인
6. ranking 종목 선택 후 뉴스/SEC/시장 관심/재무제표 수집
7. 기본 재무 지표와 장기 bar chart 확인

각 단계의 목적 자체는 타당하다. 그러나 모든 단계가 큰 기본 surface로 연속 노출되어 첫 화면의 질문과 다음 행동이 명확하지 않다. 또한 섹터 화면은 현재 기간의 상승·하락과 확산만 보여주고, 리더십의 변화·지속·약화·rotation을 설명하지 않는다. 선택 종목 기본 지표의 PER chart는 역사적 valuation처럼 보이지만 현재 가격을 과거 기간 EPS에 반복 적용하므로 계산 의미를 먼저 수정해야 한다.

이번 감사 결론은 다음과 같다.

- UI는 `수집 화면 + ranking + sector board + investigation workspace`의 연결이 아니라 하나의 scan-first React shell로 재구성할 필요가 있다.
- 수집 실패는 하나의 `failed` 상태가 아니라 stale, quote gap, limited history, alias, listing/profile gap, empty upstream universe로 구분해야 한다.
- sector / industry data는 현재 DB와 service로 상당 부분 구현 가능하다. 다만 보이는 화면에는 sector current breadth만 연결돼 있다.
- 섹터 전망은 확정 예측보다 `현재 상태 -> 지속/약화 조건 -> 과거 유사 구간의 조건부 분포` 순서로 단계화해야 한다.
- industry는 Top 2000에서 140개 label을 식별하지만 127개 종목은 industry가 `Unknown`이다. 분류 가능성은 충분하나 taxonomy 정리와 최소 표본 규칙이 필요하다.

## Current Product Promise

Market Movers가 현재 제공하는 제품 가치는 다음과 같다.

- 선택 coverage 안에서 저장된 가격 기준으로 큰 움직임을 빠르게 찾는다.
- 상승/하락/거래량/이상 거래량/섹터 리더십 관점으로 ranking을 바꾼다.
- 개별 종목 움직임이 sector 전체 확산인지 일부 종목 집중인지 구분한다.
- 선택 종목의 수동 조사 시작점을 제공한다.
- stale 또는 missing 자료가 있는 경우 원인을 확인하고 bounded refresh를 실행한다.

명시적 비목표는 live trading, broker order, 자동 추천, validation gate, Final Review decision, monitoring signal이다.

## Implemented Capabilities

| Area | Current capability | Current limitation |
| --- | --- | --- |
| Coverage | S&P 500, Top 1000, Top 2000, Nasdaq current snapshot | Nasdaq는 current Symbol Directory snapshot이 없으면 전체가 `NO_UNIVERSE`다. |
| Period | Daily, Weekly, Monthly, Yearly | Daily는 intraday snapshot, 나머지는 daily EOD row에서 파생한다. coverage마다 기준 시점이 다르다. |
| Ranking | 상승, 하락, 거래량, 이상 거래량, 섹터 | sector mode에서 investigation은 sector row가 아니라 Top Gainers fallback을 사용한다. |
| Sector breadth | canonical 11개 sector, 상승/하락 종목 수, 상승 비중, equal/cap-weight return, top gainer/loser | 한 시점/한 기간의 정적 순위이며 변화율, 지속성, benchmark-relative strength, rotation을 직접 보여주지 않는다. |
| Industry backend | `build_group_leadership_snapshot(group_by="industry")`와 historical trend rows | current Market Movers UI에 연결되지 않았다. |
| Group trend backend | daily 21개, weekly 13개, monthly 12개 non-overlapping historical windows | 화면에서 사용하지 않으며 미래 확률/검증은 제공하지 않는다. |
| Group symbol leaders | positive group 안에서 종목별 return rank와 momentum delta | 사용자가 요청한 sector별 시총 Top 3가 아니라 상승 수익률 순이다. |
| Investigation | 선택 종목 identity, movement, volume, sector/industry, 뉴스, SEC, 시장 관심, statement collection | 화면 크기가 크고 ranking/sector 맥락과 한 화면에서 경쟁한다. metadata action이 기본 분석보다 먼저 보인다. |
| Fundamentals | market cap, YTD, annual/quarterly financial snapshot, net income, EPS, current ratio, FCF | PER trend의 price basis가 period-matched가 아니며 annual/quarterly 비교 의미가 불명확하다. |
| Trust / refresh | freshness, returnable count, missing diagnostics, quote diagnosis, alias repair, universe refresh, EOD history refresh | 사용자 질문보다 ops action이 상단에서 강하게 보이며 상태 용어와 action 수가 많다. |

## Surface Role Classification

| Surface | Role | Assessment |
| --- | --- | --- |
| Header / filters / ranking | User-facing product surface | 가장 중요한 scan surface다. 첫 viewport의 주인공이어야 한다. |
| Freshness / grouped missing summary | User-facing supporting evidence | compact trust strip으로 유지할 가치가 있다. |
| Universe refresh / EOD refresh / quote-gap diagnosis / alias repair | Internal/ops console | 사용자 행동으로 연결될 수 있지만 기본 market board와 분리하거나 progressive disclosure로 낮춰야 한다. |
| Sector breadth | User-facing product surface | 정적 sector 순위에서 rotation / persistence 해석으로 확장할 가치가 크다. |
| Investigation pane | User-facing research surface | ranking 선택과 즉시 연결되는 split pane 또는 drawer가 적합하다. |
| Raw missing rows / run results | Internal/ops console | 기본 화면에서 숨기고 원인별 해결 경로가 필요할 때만 연다. |

## Current UI And Workflow Diagnosis

### 1. One screen owns four different jobs

현재 화면은 아래 네 과업을 동시에 크게 노출한다.

- data refresh / coverage management
- market ranking scan
- sector breadth interpretation
- selected-symbol research

ranking board는 Top 20 전체를 긴 list로 표시하고, 이어서 11개 sector lane이 모두 노출되며, 그 아래에 다시 대형 investigation workspace와 재무 chart가 온다. 화면 순서는 논리적이지만 각 section의 면적과 강조도가 비슷해 사용자가 어디에서 판단을 끝내야 하는지 알기 어렵다.

### 2. Visual system is fragmented

현재 visible path는 React top workbench, Streamlit ranking board, 별도 React sector breadth iframe, Streamlit + React investigation pane이 결합돼 있다. Market Context, Futures Macro, Sentiment처럼 한 component shell 안에서 section rhythm과 evidence disclosure를 통제하는 구조가 아니다.

결과적으로 다음 불일치가 생긴다.

- dark market UI와 light ranking/investigation surface가 번갈아 등장한다.
- section header, border, spacing, typography hierarchy가 surface마다 다르다.
- 같은 freshness/evidence 개념이 상단 trust, refresh companion, missing diagnostics, investigation status로 반복된다.

### 3. Collection controls dominate the product question

상단에는 5개 filter 외에 refresh mode, intraday/EOD refresh, universe refresh, reload action이 보인다. 사용자의 첫 질문은 `무엇이 움직였고 그 움직임은 얼마나 넓은가?`인데, 실제 첫 viewport는 `무엇을 갱신할 것인가?`도 같은 비중으로 묻는다.

수집 action은 필요하지만 다음 원칙이 적합하다.

- freshness가 충분하면 한 줄 basis로 축소
- stale이면 primary data action 1개만 노출
- raw job/result는 별도 operations disclosure로 이동
- refresh가 끝나면 ranking과 sector interpretation으로 즉시 복귀

### 4. Ranking and investigation connection is partial

상승/하락/거래량/이상 거래량 mode는 selected symbol investigation과 연결된다. 그러나 `섹터` ranking mode의 row는 symbol이 아니므로 investigation candidate가 current sector leader가 아니라 Top Gainers fallback으로 바뀐다.

따라서 사용자가 sector mode에서 특정 sector를 선택해 `그 sector의 대표 종목과 움직임`으로 이어지는 흐름은 현재 구현되지 않았다.

### 5. Sector filter taxonomy and sector breadth taxonomy disagree

S&P 500 현재 universe는 raw sector label 17개를 filter에 노출하지만 breadth는 alias를 합쳐 canonical 11개를 사용한다.

중복 예시는 다음과 같다.

- `Financials` / `Financial Services`
- `Materials` / `Basic Materials`
- `Information Technology` / `Technology`
- `Consumer Discretionary` / `Consumer Cyclical`
- `Consumer Staples` / `Consumer Defensive`
- `Health Care` / `Healthcare`

filter는 raw exact match를 사용하므로 alias 중 하나를 선택하면 같은 canonical sector의 일부 종목만 남는다. UI label 중복 문제가 아니라 실제 filtered universe가 분할되는 correctness 문제다.

## Current Data Evidence

2026-07-20 local DB read-only audit 결과다.

| Coverage | Daily | Weekly | Monthly | Important finding |
| --- | --- | --- | --- | --- |
| S&P 500 | 503 / 503, intraday, basis `2026-07-19 00:06`, stale 1407m | 502 / 503, EOD `2026-07-07` | 502 / 503, EOD `2026-07-07` | `HONA`는 start/end price가 없어 weekly/monthly에서 제외된다. |
| Top 1000 | 1000 / 1000, intraday `2026-07-16 22:35` | 1000 / 1000, EOD `2026-07-07` | 1000 / 1000, EOD `2026-07-07` | 반환율은 100%지만 current date 기준 stale다. |
| Top 2000 | 1982 / 2000, intraday `2026-07-07 15:01` | 2000 / 2000, EOD `2026-07-07` | 2000 / 2000, EOD `2026-07-07` | Daily 18개는 `missing intraday snapshot row`다. |
| Nasdaq current | 0 / 0, `NO_UNIVERSE` | 0 / 0, `NO_UNIVERSE` | 0 / 0, `NO_UNIVERSE` | Nasdaq Symbol Directory current listing snapshot이 DB에 없다. |

EOD refresh preflight는 S&P 500, Top 1000, Top 2000 모두 `2026-07-08~2026-07-21` 보강을 `due`로 판정했다. weekly/monthly 결과가 100% returnable이어도 최신 market context라고 볼 수 없다는 뜻이다.

## Collection Failure Taxonomy

현재 `missing_count`와 `failed_count`는 대부분 같은 숫자로 취급되지만 사용자 관점의 해결법은 다르다.

| State | Meaning | Recommended product behavior |
| --- | --- | --- |
| Stale snapshot | 데이터는 있으나 최신 trading basis가 아님 | ranking 위에 compact warning과 1개 refresh CTA를 표시하고 stale ranking임을 명시한다. |
| Missing quote row | universe member지만 intraday snapshot에 row가 없음 | bounded retry 후 반복 시 quote-gap diagnosis로 이동한다. |
| Limited price history | 신규 상장 등으로 선택 기간 start/end price가 없음 | 수집 실패가 아니라 `해당 기간 이력 미충족`으로 분리하고 shorter available window를 표시한다. |
| Ticker alias/change | symbol change 가능성이 있음 | 검증된 alias 후보만 repair하고 original symbol evidence를 남긴다. |
| Listing/profile uncertainty | active/profile evidence가 불완전함 | ranking에서 조용히 제거하지 말고 별도 excluded count와 evidence reason을 표시한다. |
| Provider unsupported/repeated gap | 동일 symbol이 반복 실패 | retry loop 대신 holdout 상태와 alternative source 검토 대상으로 전환한다. |
| Empty upstream universe | Nasdaq current snapshot 자체가 없음 | 개별 종목 실패가 아니라 upstream universe dependency로 설명한다. |

`수집 성공/실패` 하나로 묶기보다 `사용 가능`, `갱신 필요`, `기간 이력 부족`, `종목 확인 필요`, `유니버스 준비 필요`로 사용자 언어를 분리해야 한다.

## Sector And Industry Feasibility

### Sector

현재 backend는 다음 자료를 이미 계산한다.

- equal-weight return
- market-cap-weighted return
- positive symbol share
- cap-vs-equal gap
- top 3 positive-return concentration
- top gainer / loser
- daily / weekly / monthly historical group windows

따라서 `어느 sector가 높다`를 넘어서 아래 상태를 계산할 수 있다.

- broad advance / narrow advance
- strengthening / weakening breadth
- large-cap-led / broad participation
- new leader / persistent leader / fading leader
- sector relative strength versus SPY
- previous-window momentum delta

현재 service가 가진 `trend_rows`를 visible read model로 연결하면 정적 순위보다 먼저 rotation과 persistence를 설명할 수 있다.

### Sector market-cap Top 3

구현 가능하다. 현재 universe row에 sector와 market cap이 있으며 S&P 500은 503개 중 484개, Top 1000은 1000개 중 949개, Top 2000은 2000개 중 1877개가 positive market cap을 가진다.

단, 현재 `ticker_leader_rows`는 시총 순이 아니라 positive return 순이다. 새 contract는 다음을 분리해야 한다.

- `Sector Leaders`: sector return 기여/수익률 기준
- `Sector Bellwethers`: 최신 profile market cap 기준 Top 3
- 각 bellwether의 1D / 5D / 21D return과 sector 대비 초과수익
- market cap freshness와 missing-cap coverage

### Industry

Top 2000에서 140개 industry label을 식별했고 127개 종목은 `Unknown`이다. 현재 `build_group_leadership_snapshot(group_by="industry")`는 이미 작동하며 daily/weekly/monthly ranking과 historical trend row를 생성한다.

UI 연결 전 필요한 규칙은 다음과 같다.

- 최소 group size 기본 5개
- `Unknown` 별도 격리
- 상위 industry만 기본 노출하고 sector 안에서 drilldown
- raw provider industry label alias와 장기 taxonomy version 관리
- 소규모 industry의 한 종목 편향 표시
- equal-weight와 cap-weight divergence 표시

## Can The Product Show Where Sectors May Go Next?

가능하지만 `향후 예측`을 한 단계로 구현하면 안 된다.

### Level 1: current state and watch conditions

현재 저장 자료만으로 가장 신뢰성 있게 만들 수 있다.

- 현재 leadership, breadth, concentration, relative strength
- 직전 1D/5D/21D 대비 강화/약화
- 다음 관찰에서 유지돼야 할 조건
- leader sector의 bellwether Top 3 확인

이는 전망이라기보다 `현재 흐름의 지속 조건`이다.

### Level 2: historical conditional outlook

기존 opt-in `overview_market_context_analog.py`는 leading sector를 ETF proxy로 매핑하고 5D/20D/60D forward distribution을 계산하는 기반을 가진다. 이를 sector별로 확장하면 다음을 제공할 수 있다.

- 비슷한 relative-strength + breadth 상태의 과거 표본
- 다음 5D/20D sector ETF vs SPY median excess return
- positive rate, drawdown, sample count
- walk-forward validation / calibration 상태

표본 부족 시 숫자를 숨기고 provisional/unavailable로 처리해야 한다.

### Level 3: macro-conditioned sector outlook

경제사이클, 금리, 달러, 유가, credit, sentiment 조건을 추가할 수 있지만 표본이 빠르게 줄고 설명 복잡도가 커진다. Level 2의 out-of-sample 검증을 통과한 뒤에만 진행하는 것이 적절하다.

Industry-level future outlook은 현재 sector보다 위험하다. historical constituent taxonomy와 point-in-time sector/industry membership이 저장돼 있지 않아 survivorship와 classification drift가 생길 수 있다. 먼저 current trend/persistence까지만 제공하고, PIT taxonomy 계약 이후 conditional outlook을 검토해야 한다.

## Selected Symbol Investigation Diagnosis

### Strengths

- ranking symbol과 identity/movement/sector/industry가 연결된다.
- 뉴스와 SEC metadata는 사용자 action 뒤 세션 전용으로 유지된다.
- statement collection gap을 EDGAR filing과 DB reflected period로 비교한다.
- source boundary와 non-signal boundary가 명시돼 있다.

### Weak Points

1. 조사 action이 기본 해석보다 먼저 보인다.
2. ranking basis, research as-of, YTD latest price, filing period가 서로 다른데 한눈에 구분되지 않는다.
3. metric bar chart가 길고 horizontal scroll이 필요하며 핵심 변화점과 comparability를 설명하지 않는다.
4. annual과 quarterly 값을 나란히 보여주지만 duration difference를 충분히 설명하지 않는다.
5. 현재 PER trend는 과거 각 period EPS에 동일한 latest price를 적용한다.

마지막 항목은 UI polish 이전의 correctness 문제다. 현재 계산은 다음 형태다.

```text
period EPS = period net income / period shares
displayed PER = latest price / period EPS
```

따라서 historical PER chart가 아니다. 특히 quarterly EPS를 그대로 분모로 사용한 PER와 annual EPS 기반 PER는 비교 가능한 valuation series가 아니다.

개선 시에는 다음 중 하나를 명시적으로 선택해야 한다.

- period-end price / contemporaneous TTM EPS 기반 historical PER
- current price / historical TTM EPS 기반 `현재 가격 기준 역산 배수`로 이름 변경
- PER chart 제거 후 PIT TTM EPS, revenue/net income/FCF, margin, liquidity의 comparable trend만 먼저 제공

## Recommended Information Architecture

한 개의 React shell 안에서 다음 순서를 권고한다.

### First viewport: market scan

- coverage + period
- compact basis/freshness line
- ranking intent tabs
- Top list와 선택 종목 quick detail의 split view
- stale일 때만 1개 primary refresh CTA

### Second section: market breadth and rotation

- `Sector | Industry` switch
- 1D / 5D / 21D matrix 또는 small multiples
- leader / strengthening / fading / reversing state
- selected group의 market-cap bellwether Top 3
- current state와 next watch conditions

### Investigation drawer or detail route

- 선택 종목 quick chart와 ranking context
- price/volume/relative volume
- financial snapshot
- news / SEC / market interest actions
- raw source and collection evidence disclosure

Raw missing rows, job results, alias repair, statement collection logs는 기본 surface가 아니라 data operations disclosure로 둔다.

## Priority Findings

| Priority | Finding | Why it matters |
| --- | --- | --- |
| P0 | Historical PER chart semantics are incorrect/ambiguous. | 사용자가 valuation trend로 오해할 수 있다. |
| P0 | Weekly/monthly EOD basis is `2026-07-07` while current date is `2026-07-20`. | returnable 100%가 current market coverage를 의미하지 않는다. |
| P1 | Four jobs share one long page with equal visual weight. | scan speed와 다음 행동의 명확성이 떨어진다. |
| P1 | Raw sector filter has 17 labels while breadth uses canonical 11. | 같은 sector가 filter에서 분할되는 correctness issue다. |
| P1 | Sector breadth is descriptive, not rotational or persistence-aware. | 사용자가 `그래서 이 흐름이 강화되는가?`에 답을 얻지 못한다. |
| P1 | Sector mode does not connect to sector-specific investigation. | ranking-to-research handoff가 끊긴다. |
| P1 | Failure states are collapsed into missing/failed counts. | 신규 상장과 provider gap에 같은 retry action을 유도한다. |
| P2 | Industry backend exists but is not visible. | 이미 구현된 product value가 사용자에게 전달되지 않는다. |
| P2 | React/Streamlit/iframe visual systems are fragmented. | 유사 Overview tabs와 제품 완성도가 맞지 않는다. |

## Recommended Development Sequence

### 1차: diagnosis and correctness contract

- 이번 문서로 완료
- PER semantics, sector canonical filter, stale/limited-history taxonomy를 구현 전 계약으로 확정

### 2차: information architecture and visual contract

- one-shell layout, first viewport, section ownership, selected-state handoff 설계
- Market Context / Futures Macro / Sentiment와 shared visual rhythm 정렬

### 3차: data/read-model hardening

- canonical sector filtering
- typed collection gaps
- sector market-cap Top 3
- visible industry leadership + minimum sample / Unknown rules
- comparable financial metric contract

### 4차: React implementation

- scan-first ranking + split detail
- sector/industry rotation section
- investigation drawer/detail
- operations disclosure 분리

### 5차: conditional outlook and QA

- sector ETF historical conditional outlook
- walk-forward publication gate
- browser QA and responsive verification
- industry outlook은 PIT taxonomy readiness 이후 별도 판단

## Code And Data Ownership

| Responsibility | Owner |
| --- | --- |
| Tab orchestration | `app/web/overview/market_movers.py` |
| Streamlit glue / actions / selected state | `app/web/overview/market_movers_helpers.py` |
| Main React workbench | `app/web/streamlit_components/market_movers_workbench/` |
| Ranking / coverage / sector / industry service | `app/services/overview/market_movers.py` |
| Selected-symbol research service | `app/services/overview/why_it_moved.py` |
| Overview refresh facade | `app/jobs/overview_actions.py` |
| Shared Overview components | `app/web/overview/components/market_movers.py` |
| Historical sector analog | `app/services/overview_market_context_analog.py` |
| Asset profile source | `finance/data/asset_profile.py` |
| DB price loader | `finance/loaders/price.py` |

## Data And Validation Risks

- EOD freshness and intraday freshness are different contracts and must not share one generic `data ready` interpretation.
- current universe/profile sector membership is not a full PIT historical classification dataset.
- market cap is latest profile data, not historical period market cap.
- industry groups can be sparse and provider taxonomy can drift.
- newly listed symbols should not be penalized as collection failures for windows before listing.
- current selected-symbol financial snapshot uses statement availability dates, but valuation chart price matching is not PIT-correct.
- conditional outlook requires independent episode spacing, walk-forward testing, minimum sample, and publication gating.
- sector/industry output remains context-only and must not become a trade recommendation or validation gate.

## Open Questions For The Next Design Step

- 첫 viewport의 primary question을 `오늘 무엇이 움직였나`로 고정할지, `어느 그룹이 주도하나`까지 함께 둘지
- Daily를 현재 session snapshot으로 볼지, closed session에서는 last completed close로 자동 전환할지
- sector outlook의 first release를 watch-condition only로 할지 historical conditional distribution까지 포함할지
- sector별 market-cap Top 3에 ADR/foreign listing/ETF를 포함할지
- industry label을 provider raw taxonomy로 유지할지 canonical mapping layer를 추가할지
- investigation을 same-page drawer로 둘지 symbol detail route로 분리할지

## Benchmark Handoff Questions

- 시장 board에서 ranking과 selected detail을 한 viewport에 두는 최적 밀도는 무엇인가?
- sector rotation을 heatmap, rank slope, matrix, small multiples 중 어떤 pattern으로 표현해야 가장 빨리 읽히는가?
- data freshness action을 product surface에서 어느 정도까지 보이고 operations console로 넘기는가?
- conditional outlook의 sample count와 validation state를 추천처럼 보이지 않게 표현하는 UI pattern은 무엇인가?
