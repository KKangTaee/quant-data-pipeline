# Market Research IA Redesign V1 Design

Status: Approved Direction; Written Spec Review Pending
Last Updated: 2026-07-22

## Problem

상위 navigation은 `Research > Market Research`로 바뀌었지만 내부 page는 기존 최초 진입 `Overview` 구조를 유지한다.

```text
Overview title
  -> Reference help
  -> U.S. market session banner
  -> Market Context | Market Movers | Futures Macro | Sentiment | Events
     -> Market Context 안에서 Economic Cycle | S&P 500 | U.S. Stock
```

이 구조는 Today가 소유하는 summary와 중복되고, market-level evidence와 security-level research를 서로 다른 depth에 혼합한다.

## Confirmed Product Role

- `Today`: 오늘의 시장 판단과 대표 포트폴리오를 compact하게 읽는 first-read surface
- `Market Research`: Today에서 발견한 근거를 시장 환경, 지수 가치, 종목 단위로 깊게 조사하는 read-oriented workspace
- `Data Operations`: 수집 run, history, log, failure와 DB write를 소유
- Market Research evidence는 trade signal, validation PASS/BLOCKER, monitoring signal이 아니다.

## Information Architecture

```text
Market Research
  시장 환경
    경제 사이클
    선물 매크로
    시장 심리
    일정
  지수 가치평가
    S&P 500
  종목 리서치
    변동 종목
    미국 개별주식
```

### Primary Selector

- labels: `시장 환경 | 지수 가치평가 | 종목 리서치`
- compact segmented surface를 사용한다.
- 기존 다섯 개 bilingual underline tab을 대체한다.
- family는 active view에서 파생하며 별도의 persistent data record를 만들지 않는다.

### Secondary Selector

- 시장 환경: `경제 사이클 | 선물 매크로 | 심리 | 일정`
- 지수 가치평가: secondary selector 없이 S&P 500을 바로 연다.
- 종목 리서치: `변동 종목 | 개별 종목`
- visible label은 한국어를 사용한다. English module name은 page copy, accessibility label, internal identifier에만 둔다.

## Page Shell

기본 상단은 다음만 표시한다.

```text
MARKET RESEARCH
Market Research
Today에서 확인한 시장 판단을 환경·가치평가·종목 근거로 확장합니다.

[시장 환경] [지수 가치평가] [종목 리서치]
[선택 family의 secondary selector]
```

다음은 page-global surface에서 제거한다.

- `Overview` title/caption
- `Reference help · Overview` contextual expander
- 모든 module 앞에 반복되는 full-width U.S. market session banner
- 공통 freshness score 또는 source count
- run/job/row diagnostic summary

## Common Information Ownership

단일 공통 기준일은 만들지 않는다. Economic Cycle, S&P 500, futures, sentiment, event의 실제 기준일과 freshness 의미가 다르기 때문이다.

| Information | Owner |
| --- | --- |
| 기준일, 자료 제한, publication status | active module workbench |
| 장 open/close/session | Market Movers, 필요 시 Futures Macro의 compact context |
| refresh action | 현재 action을 제공하는 active module |
| methodology/read guide | module disclosure 또는 Reference Center |
| raw run result/history/log/failure | Data Operations |

기존 module이 이미 제공하는 상태·refresh action은 보존하되 page header로 끌어올리지 않는다.

## Canonical View And Compatibility Contract

canonical route는 계속 `/overview`를 사용한다. 새 상위 page 또는 URL migration은 만들지 않는다.

`overview_tab`은 module-level canonical view를 표현하도록 확장한다.

| Canonical slug | Family | Renderer |
| --- | --- | --- |
| `economic-cycle` | 시장 환경 | `render_economic_cycle` |
| `futures-macro` | 시장 환경 | `render_futures_macro_tab` |
| `sentiment` | 시장 환경 | `render_sentiment_tab` |
| `events` | 시장 환경 | `render_events_tab` |
| `sp500` | 지수 가치평가 | `render_market_context_valuation(default_instrument="sp500")` |
| `market-movers` | 종목 리서치 | `render_market_movers_tab` |
| `us-stock` | 종목 리서치 | `render_market_context_valuation(default_instrument="us_stock")` |

Legacy input은 다음처럼 계속 수용한다.

- `market-context`: 기존 `overview_market_context_mode`가 유효하면 해당 view, 아니면 `economic-cycle`
- `market-movers`, `futures-macro`, `sentiment`, `events`: 같은 canonical view로 변환
- invalid/missing: `economic-cycle`

Today의 기존 `market-context`와 `market-movers` CTA는 회귀 없이 동작해야 한다. 새 link를 생성할 때는 module-level canonical slug를 사용한다.

## Navigation State

`app/web/overview/navigation.py`가 다음 pure contract를 소유한다.

- slug normalization
- legacy label/slug mapping
- view -> family mapping
- family -> default view mapping
- query/session/widget seed precedence
- primary/secondary selector state

Renderer dispatch는 canonical view 하나만 입력받는다. 기존 `render_market_context_tab()`은 V1에서 legacy caller용 compatibility adapter로 유지하되 새 page primary dispatch에서는 호출하지 않는다.

### Query And Widget Precedence

- URL query가 이전에 적용한 slug와 다르면 query가 최우선이다. Today 또는 external deep link가 같은 browser session의 기존 widget state를 이겨야 하기 때문이다.
- query를 적용한 뒤 applied-query token을 session에 기록한다.
- 사용자가 primary/secondary selector를 바꾸면 widget selection을 canonical view로 변환하고 session과 `overview_tab` query를 함께 갱신한다.
- query가 없으면 valid widget state, valid session view, `economic-cycle` 순으로 복구한다.
- invalid legacy/widget/session 값은 삭제하지 않고 무시하며 canonical default만 렌더링한다.

## Stock Research Handoff

### User Flow

```text
종목 리서치 > 변동 종목
  -> 종목 선택
  -> Why It Moved / 저장 근거 확인
  -> `개별 종목 분석` action
  -> 종목 리서치 > 개별 종목
  -> 같은 symbol의 PER 상대가치 또는 전환 분석
```

### State Contract

- source symbol: current Market Movers selection
  - `overview_market_movers_selected_symbol_<coverage>`
- destination symbol: existing U.S. Stock selection
  - `overview_us_stock_valuation_selected_symbol`
- destination view: `overview_tab=us-stock`

handoff action은 symbol을 trim/uppercase하고 event symbol이 현재 `overview_market_movers_selected_symbol_<coverage>` 및 current decision payload의 selected ranking row와 모두 일치할 때만 destination에 반영한다. remote fetch, registry write, 자동 refresh는 실행하지 않는다. destination의 기존 DB-backed read model이 profile/statement availability를 판정하고, 필요한 경우에만 명시적 `최신 데이터로 다시 계산` action을 제공한다.

Market Movers decision workbench에 `개별 종목 분석` button과 allow-listed `open_us_stock_research` event를 추가한다. event는 `{id: "open_us_stock_research", symbol}` 최소 payload를 사용하며 Python이 최종 validation과 route state를 소유한다.

## Component And File Ownership

| Area | Owner |
| --- | --- |
| page title, purpose, top-level render order | `app/web/overview/page.py` |
| family/view normalization and selector UI | `app/web/overview/navigation.py` |
| Economic Cycle / S&P / U.S. Stock compatibility adapter | `app/web/overview/market_context.py` |
| selected-stock read model and destination symbol | `app/web/overview/market_context_helpers.py` |
| mover selection and handoff event | `app/web/overview/market_movers_helpers.py`, `app/web/streamlit_components/market_movers_workbench/src/MarketMoversWorkbench.tsx` |
| app page title and `/overview` route | `app/web/streamlit_app.py` retained |
| contract tests | focused navigation, Today, service/UI boundary tests |

기존 module body, service, loader, DB schema는 변경하지 않는다.

## Duplicate Heading Rule

- page shell은 `Market Research`만 표시한다.
- selector 아래 Streamlit `### 시장 맥락`, `### 변동 종목`, `### 선물 매크로`, `### 시장 심리 컨텍스트`, `### Events`가 React hero와 같은 제목을 반복하면 제거한다.
- module의 목적 설명이 React hero에 없을 때만 한 줄 section description을 유지한다.
- fallback renderer에서는 동일한 heading hierarchy를 보존한다.

## Responsive Design

- desktop: primary selector 3 columns, secondary selector intrinsic-width row
- 760px: primary selector 3 columns 유지, secondary selector wrap 허용
- 420px: primary selector는 짧은 한국어 label의 3 equal columns, secondary selector는 2-column wrap
- horizontal scroll에 의존하지 않는다.
- selected state는 color만이 아니라 background/border/font weight로 구분한다.
- sticky navigation은 V1 필수 범위가 아니다. Streamlit container/iframe 경계를 실제 QA한 뒤 별도 후속으로 판단한다.

## Error And Empty States

- invalid query/session view: `economic-cycle`로 복구
- active module render failure: 다른 family로 자동 이동하지 않고 해당 module의 기존 fallback/empty state 표시
- handoff symbol invalid/unavailable: 현재 mover 화면을 유지하고 짧은 사용자 안내 표시
- module data stale/missing: 기존 module 의미를 유지하고 global status로 정상화하지 않음
- React build unavailable: 기존 Streamlit fallback 유지

## Verification Contract

### Automated

- canonical slug, family/view mapping, legacy normalization pure tests
- query > widget > session seed precedence tests
- all seven render dispatch paths
- Today `market-context` and `market-movers` CTA regression
- existing `/overview` and Reference destination continuity
- valid/invalid Market Movers symbol handoff tests
- no remote fetch/write-on-navigation boundary
- `py_compile`, `git diff --check`

### Browser QA

- actual DB-backed `/overview`
- default `economic-cycle`
- seven module views and both selector levels
- legacy `overview_tab` deep links
- Today -> Market Research / Market Movers
- Market Movers -> same-symbol U.S. Stock handoff
- desktop, 760px, 420px
- horizontal overflow, duplicate heading, selector selected state, console warning/error
- final QA screenshot 1장, generated artifact로 commit하지 않음

## Tradeoffs

- 한 page를 유지하므로 상위 navigation 증가와 route migration 위험을 피하지만 2-level selector가 생긴다.
- Market/Stock Research 완전 분리보다 변경 위험이 작고 실제 사용 후 page split 필요성을 다시 평가할 수 있다.
- 전역 session/freshness summary를 제거하면 첫 화면 정보량은 줄지만 잘못된 공통 기준일과 Today 중복을 피한다.
- sticky local navigation을 미루므로 긴 Economic Cycle 화면에서 module 전환은 맨 위에서 수행한다. V1 안정성 이후 실제 필요성을 판단한다.

## Approval Boundary

이 문서는 사용자가 승인한 `3개 목적형 그룹` 방향을 구현 가능한 계약으로 고정한다. 사용자가 written spec을 검토한 뒤에만 별도 implementation plan을 작성하고 code work를 시작한다.
