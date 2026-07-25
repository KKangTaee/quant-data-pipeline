# Institutional Holdings React Parity V1 Design

Status: Draft For User Review
Last Updated: 2026-07-25

## Product Intent

사용자는 `Institutional Holdings`에서 다음 질문을 한 흐름으로 끝내야 한다.

1. 지금 어떤 기관의 어느 보고 분기를 보고 있는가.
2. 이 기관의 포트폴리오는 어디에 집중되어 있고 자료 연결 범위는 어느 정도인가.
3. 전체 보유에서 원하는 종목을 어떻게 찾는가.
4. 특정 종목은 선택 기관에서 어느 위치이며 어떤 기관들이 함께 보유하는가.
5. 이 판단이 13F 지연, mapping, 저장 가격 coverage에 의해 어디까지 제한되는가.

기존 기능과 데이터 의미는 유지한다. 이번 개편의 핵심은 이 질문에 답하는 정상 화면을 React가 전부 소유하고, Today / Market Research와 같은 제품 언어로 읽히게 만드는 것이다.

## Existing Product Pattern To Reuse

### Today

- `render_today_page()`는 visible Streamlit title을 만들지 않는다.
- Python이 DB-backed read-model을 만들고 React component에 payload를 전달한다.
- React가 page hero, evidence, portfolio, next action을 렌더링한다.
- server data가 바뀔 수 있는 portfolio island만 `st.fragment`로 격리하고, 시계와 local presentation은 React state에 둔다.

### Market Research

- React가 page title, family navigation, local view navigation을 렌더링한다.
- Python은 URL / session normalization과 선택 module lazy dispatch를 소유한다.
- 각 복잡한 module은 자기 React workbench와 payload / event boundary를 가진다.

### Institutional Holdings Target

- Today의 `React-owned normal surface + thin Python adapter`를 기본 pattern으로 사용한다.
- Market Research의 `page header -> primary family -> local view -> selected module` hierarchy를 navigation pattern으로 사용한다.
- Holdings는 periodic live data가 아니므로 Today의 15초 fragment를 복제하지 않는다. manager selection, security search, refresh, price collection 같은 explicit event만 server boundary를 넘는다.

## Screen Ownership

### React Owns On The Normal Path

- page eyebrow, `Institutional Holdings` title, purpose copy.
- selected manager context hero.
- manager search and favorite / result switcher.
- primary / secondary workspace navigation.
- data basis, SEC source, freshness, refresh action and refresh result.
- allocation, change comparison, coverage, sector exposure, assumed performance.
- complete holdings explorer.
- security search, selected-security context, price chart, holder list and popularity.
- source caveats and contextual help entry.
- loading, empty, unavailable, stale and error presentation.

### Streamlit Owns Behind The Surface

- `st.Page` route and app-level navigation.
- session state used for selected manager / server-loaded security result.
- service / loader calls and JSON-safe payload assembly.
- explicit SEC refresh and price collection execution.
- React component event handling and app rerun.
- React bundle unavailable or fatal data unavailable fallback.

### Normal Path Must Not Render

- `st.title("Institutional Portfolios")`.
- the current long `st.caption`.
- default contextual-help expander before the workbench.
- default SEC refresh expander below / above the workbench.
- `Detailed filings / table fallback` after a healthy React render.
- runtime / build diagnostics in the user-facing first read.

Fallback content remains available only when the React bundle or required payload cannot render.

## Target Information Architecture

```text
Institutional Holdings React page
  -> Page header
       -> purpose
       -> compact help / source status
  -> Research navigation
       -> 기관 포트폴리오
            -> 포트폴리오 맥락
            -> 전체 보유
       -> 종목 리서치
            -> 종목 상세
            -> 기관 보유 랭킹
  -> Selected manager module
       -> manager switcher
       -> manager context hero
       -> selected view body
  -> Data basis / caveats disclosure
```

Page header와 selected manager hero는 같은 제목을 반복하지 않는다.

- page header: 제품 목적과 현재 surface identity.
- manager hero: 선택 기관 이름, 분기, 집중도, coverage, SEC source.

## Page Header

- eyebrow: `INSTITUTIONAL RESEARCH`.
- title: `Institutional Holdings`.
- purpose copy: delayed SEC 13F를 이용해 기관 포트폴리오와 종목 보유 맥락을 탐색한다는 한 문장.
- right-side status:
  - report period.
  - saved snapshot state.
  - delayed-data label.
- compact actions:
  - `도움말`.
  - `자료 기준`.

Today hero와 동일한 blue-gray gradient, rounded surface, restrained shadow를 사용한다. 데이터 상태는 의미가 있을 때만 semantic amber / blue로 표시하며 saturated cobalt를 page-wide accent로 사용하지 않는다.

## Research Navigation

Market Research의 two-tier grammar를 재사용한다.

### Primary

- `기관 포트폴리오`.
- `종목 리서치`.

얇은 underline family navigation을 사용한다. 현재의 black segmented control은 제거한다.

### Secondary

- 기관 포트폴리오: `포트폴리오 맥락 | 전체 보유`.
- 종목 리서치: `종목 상세 | 기관 보유 랭킹`.

muted blue pill navigation을 사용한다. 현재의 red underline secondary navigation은 제거한다.

Navigation click은 React local state다. server data가 필요한 security search나 popularity load만 event를 보낸다.

## Manager Switcher

기존 검색과 모든 manager 접근 기능을 유지하되 page hero와 경쟁하지 않게 한다.

- selected manager는 manager context hero의 headline으로 표시한다.
- switcher는 hero 위 또는 바로 아래의 compact command row에 둔다.
- 기본 curated manager는 compact horizontal chips / cards로 유지한다.
- manager search는 explicit submit이다.
- 검색 결과 수, 0건, pending selection state를 유지한다.
- generic search result가 curated list와 섞여 first-read를 밀어내지 않게 한다.
- desktop은 한 줄, tablet은 줄바꿈 가능한 bounded row, mobile은 한 개 selected summary + horizontal result rail을 사용한다.

Manager selection은 server event다. pending label과 현재 화면을 유지한 뒤 새 payload가 도착하면 selected manager context만 갱신한다.

## Selected Manager Context Hero

사용자가 첫 viewport에서 선택 기관과 핵심 맥락을 읽을 수 있어야 한다.

- manager name.
- report period / filing date / DB snapshot.
- deterministic context summary.
- top-5 concentration.
- largest mapped sector.
- count / reported-value mapping coverage.
- comparison availability.
- SEC source action.

기존의 긴 summary 문장은 desktop에서 최대 readable width를 제한하고, mobile에서는 핵심 문장과 supporting facts를 분리한다. metadata card를 여러 겹 쌓지 않고 Today / Market Research module hero처럼 한 surface 안에서 hierarchy를 만든다.

## Portfolio Views

### 포트폴리오 맥락

기존 reading order를 유지한다.

1. allocation donut + top holdings + Other.
2. previous filing이 있을 때만 quarter comparison.
3. ticker / price coverage와 sector exposure.
4. report-date hold-constant assumed performance.

각 section은 17~21px rounded surface, blue-gray border, restrained shadow, consistent section eyebrow를 사용한다. coverage metric과 sector bars는 같은 evidence family로 읽히되 별도 의미를 유지한다.

### 전체 보유

- full logical row set.
- ticker / issuer / CUSIP search.
- mapped / unresolved / sector filter.
- current sort choices.
- fixed 50-row page and visible range.
- mapped row security drilldown.
- unresolved row mapping limitation.

기능과 pagination contract는 변경하지 않는다. toolbar와 table/card density만 최신 surface grammar로 정리한다.

## Security Research Views

### 종목 상세

- explicit ticker / issuer / CUSIP search.
- selected institution position.
- saved price chart with current line / candle and daily / weekly / monthly interactions.
- price-coverage / mapping states.
- latest-filing holder list.

chart interaction은 React local state다. DB price collection만 explicit server event다.

### 기관 보유 랭킹

- existing lazy load contract를 유지한다.
- rank list가 security search를 대체하지 않는다.
- selected report period와 delayed filing caveat를 함께 표시한다.

## Refresh, Help And Caveats

### SEC Refresh

기존 기능을 삭제하지 않고 React-owned disclosure로 옮긴다.

- default first-read에는 compact `최신 13F 자료 갱신` action만 보인다.
- disclosure를 열면 dataset label / URL과 current freshness를 확인할 수 있다.
- explicit submit에서 기존 Python refresh handler를 호출한다.
- pending / success / partial / failed result는 React payload로 돌아와 같은 disclosure에 표시한다.
- run count, saved rows, raw job table을 primary improvement surface로 추가하지 않는다.

### Help And Data Basis

- page header의 compact help action은 React disclosure 또는 current contextual Reference handoff event를 연다.
- SEC delay, missing shorts/cash/hedges, amendments, mapping limits는 bottom disclosure에 유지한다.
- caveat는 삭제하지 않지만 첫 화면의 title과 manager context 사이를 막지 않는다.

## Component Boundary

현재 단일 `InstitutionalPortfoliosWorkbench.tsx`를 다음 책임 단위로 분리한다. 실제 파일명은 implementation plan에서 repository naming과 test ergonomics를 확인해 확정한다.

- `InstitutionalHoldingsPage`: payload validation, top-level composition, server event envelope.
- `InstitutionalPageHeader`: page identity, global status, help / basis actions.
- `InstitutionalNavigation`: primary / secondary local navigation.
- `ManagerSwitcher`: selected manager, curated rail, explicit search, pending state.
- `ManagerContextHero`: manager summary, report basis, SEC source.
- `PortfolioAllocation`: donut and top holdings drilldown.
- `PortfolioEvidence`: comparison, coverage, sector, assumed performance composition.
- `HoldingsExplorer`: client search / filter / sort / pagination.
- `SecurityResearch`: explicit search and selected security composition.
- `SecurityPriceChart`: chart style / frequency / viewport local state.
- `HolderRanking`: holder list and lazy popularity.
- `InstitutionalDisclosures`: refresh, help, caveats and fallback-adjacent notices.
- `workbenchState`: pure navigation, paging, pending-event and payload-reconciliation helpers.

Component split은 시각 개편에 필요한 범위로 제한한다. service / loader / DB logic를 React 파일로 옮기지 않는다.

## State And Event Contract

### React Local State

- active primary / secondary view.
- holdings search / filter / sort / page.
- chart mode / frequency / pan / hover.
- disclosure open state.
- manager rail scroll.
- immediately available mapped holding preview.

### Python / Streamlit State

- selected manager CIK after confirmed server event.
- submitted manager search result.
- submitted security search result and holder model.
- popularity lazy-load result.
- SEC refresh execution / result.
- price collection execution / result.

### Event Envelope

모든 server event는 stable `id`, required payload, unique `nonce`를 가진다.

- `select_manager`.
- `manager_search`.
- `security_search`.
- `load_popularity`.
- `collect_price`.
- `refresh_sec_13f`.
- `open_reference`.

Local view navigation은 event envelope를 만들지 않는다.

## Loading And Error Handling

- initial data unavailable: React preview / unavailable shell if a valid payload can be built.
- React bundle unavailable: Streamlit fallback.
- manager / security / refresh pending: current context를 지우지 않고 action-scoped pending state 표시.
- zero search result: live selected manager context 유지.
- stale payload response: query / event identity가 current pending intent와 일치할 때만 완료 처리.
- mapped / unresolved / ambiguous / no-price state를 구분한다.
- error는 technical exception text보다 사용자가 할 수 있는 다음 행동을 먼저 표시한다.

## Visual System

Today / Market Research 계열 token을 institutional scope에서 재사용한다.

- font: `Inter, Pretendard, system-ui`.
- ink: blue-gray hierarchy.
- muted text: medium slate.
- surface: white / very light blue-gray.
- line: low-contrast blue-gray.
- hero: subtle blue-gray / cool-neutral gradient.
- radius:
  - hero 21~23px.
  - primary panels 17~21px.
  - inner cards 12~14px.
  - chips / local navigation 999px.
- shadow: Today 수준의 low-opacity shadow.
- semantic colors:
  - green / red는 수익·방향 의미에만 사용.
  - amber는 delayed / limited / stale.
  - blue는 selected / informational state.

Sector color는 category distinction을 위해 유지할 수 있지만 page chrome과 navigation accent로 확장하지 않는다.

## Responsive Contract

### Desktop

- content-width aligned page header, navigation, manager hero and view body.
- manager context and report basis는 balanced two-column.
- portfolio evidence는 의미에 맞는 asymmetric grid.

### Tablet

- page header status와 manager context basis를 자연스럽게 stack.
- primary / secondary navigation은 readable width를 유지하고 불필요한 horizontal overflow를 만들지 않는다.

### 420px

- page title은 한 줄 또는 의도된 compact two-line 안에서 끝난다.
- selected manager name과 context summary가 첫 viewport 안에 등장한다.
- manager search와 report basis는 single column.
- primary navigation은 2-column family, secondary navigation은 2-column pills.
- metric / evidence / holding rows는 meaning-preserving stack으로 전환한다.
- document와 component 모두 horizontal overflow가 없어야 한다.

## Accessibility

- navigation에 `nav`, tab / current semantics를 유지한다.
- search label과 button accessible name을 유지한다.
- pending state는 `aria-live`로 알린다.
- color만으로 mapping / return / availability 상태를 구분하지 않는다.
- focus-visible outline을 shared token으로 통일한다.
- prefers-reduced-motion에서 non-essential transition을 제거한다.

## Verification Contract

### Automated

- payload schema and JSON-safe conversion.
- event normalization and stale-event reconciliation.
- local navigation does not emit server events.
- manager / security explicit submit event.
- holdings search / filter / sort / pagination.
- mapped / unresolved security behavior.
- React typecheck and production build.
- focused Python compile / tests.

### Actual Browser

- Berkshire desktop first-read.
- Bridgewater complete holdings paging and unresolved row.
- mapped AAPL security detail and chart controls.
- manager switch and zero-result search.
- SEC refresh disclosure open / cancel or bounded test path.
- Reference / caveat disclosure.
- 1280px / 760px / 420px.
- horizontal overflow 0.
- console error / warning review.

Generated screenshots remain ignored unless the user explicitly asks to commit them.

## Success Criteria

- healthy React path에 visible Streamlit title / caption / expander / fallback table이 없다.
- Today / Market Research와 같은 page shell, typography, surface and navigation hierarchy로 읽힌다.
- selected manager identity와 core context가 mobile initial viewport에 나타난다.
- 기존 manager / portfolio / holdings / security / chart / ranking / refresh 기능이 유지된다.
- local interactions do not trigger unnecessary full-app reruns.
- explicit server events preserve current context until replacement payload arrives.
- 13F delay, mapping and price coverage limitations remain visible but do not dominate the first read.

## Tradeoffs

- Streamlit custom component iframe과 server event rerun은 유지된다. standalone SPA의 route / fetch independence는 이번 범위가 아니다.
- React-owned refresh disclosure는 event / payload contract를 보강해야 하지만 visible Streamlit expander를 유지하는 것보다 product consistency가 높다.
- component split은 변경 파일 수를 늘리지만 1,747-line TSX와 2,102-line CSS를 그대로 polish하는 것보다 회귀 위치를 좁힌다.
- manager rail을 compact하게 낮추면 동시에 보이는 manager 수는 줄 수 있으나 검색과 전체 접근은 유지되고 selected-manager context의 우선순위가 명확해진다.

## Explicit Non-Goals

- 13F를 현재 보유 또는 매매 의도로 표현하지 않는다.
- recommendation, scoring, broker or approval workflow를 추가하지 않는다.
- data refresh result를 run / job / row diagnostic dashboard로 만들지 않는다.
- price / filing / mapping gaps를 합성하거나 숨기지 않는다.
