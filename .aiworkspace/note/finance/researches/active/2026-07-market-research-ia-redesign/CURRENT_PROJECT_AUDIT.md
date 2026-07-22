# Market Research IA Current Project Audit

Status: Draft For User Review
Last Updated: 2026-07-22

## Summary

`Research > Market Research`는 상위 navigation에서 이미 기존 `Overview`의 역할을 벗어났지만, 화면 내부는 여전히 최초 진입 대시보드 시절의 `Overview` 제목, 공통 장 세션 banner, 다섯 개 동급 탭을 유지한다. 신규 `Today`가 경제사이클, S&P 500, 선물 매크로, 심리, 일정의 compact summary를 소유하므로 Market Research는 같은 정보를 다시 요약하기보다 사용자가 선택한 근거를 깊게 조사하는 workspace로 재정의하는 편이 적합하다.

## Current Surface

- App navigation title: `Market Research`
- Page title and help label: `Overview`
- Common header: description, Reference contextual help, U.S. market session banner
- Primary selector: `Market Context | Market Movers | Futures Macro | Sentiment | Events`
- Nested selector under Market Context: `Economic Cycle | S&P 500 | U.S. Stock`

## Implemented Strengths

- 각 module은 DB-backed read model과 기존 deep link를 보유한다.
- Economic Cycle, S&P 500, Market Movers, Futures Macro, Sentiment, Events가 독립적인 실제 사용자 가치와 충분한 깊이를 갖는다.
- source, freshness, partial state를 숨기지 않고 context를 trade signal로 승격하지 않는다.
- Today가 기존 read model을 compact하게 조합하므로 Market Research가 overview summary를 계속 소유할 필요가 없어졌다.

## UX And Workflow Friction

1. **이름과 역할 불일치**: 상위 navigation은 Market Research인데 page heading과 contextual help는 Overview다.
2. **Today와 역할 중복**: 경제사이클, S&P 500, 선물, 심리, 일정을 다시 한 entry surface에 나열한다.
3. **서로 다른 질문을 동급 tab으로 배치**: 시장 환경, 종목 탐색, macro evidence, sentiment, calendar가 같은 hierarchy에 있다.
4. **시장과 종목 level 혼합**: Market Context 안에 시장 수준 경제사이클/S&P 500과 security-level 미국 개별주식이 함께 있고, Market Movers는 다시 sibling tab이다.
5. **상단 vertical cost**: title, caption, Reference help, full market-session banner, bilingual five-tab nav가 실제 module 시작 전에 반복된다.
6. **중복 heading**: page/tab heading과 React workbench hero가 `변동 종목`, `선물 매크로`, `시장 심리` 같은 이름을 반복한다.
7. **공통 정보의 문맥 부적합**: 장 open/close 정보는 Market Movers에는 유용하지만 Economic Cycle, Sentiment, Events 전체에 공통으로 필요한 정보는 아니다.
8. **긴 workbench와 navigation의 결합 부족**: Economic Cycle처럼 긴 화면에서 현재 연구 목적과 다른 module로 이동하는 구조가 desktop 중심의 긴 bilingual tab row에 의존한다.

## Surface Role Classification

| Surface | Current role | Recommended role |
| --- | --- | --- |
| Today | First-read market and representative portfolio summary | 유지 |
| Economic Cycle / Futures / Sentiment / Events | Market-level evidence workbench | `시장 환경` research family |
| S&P 500 | Broad-index valuation workbench | `시장 가치평가` research family |
| Market Movers / U.S. Stock | Security discovery and analysis | `종목 리서치` family 또는 별도 Stock Research page |
| Market session banner | Global common header | Movers/Futures 문맥의 compact metadata로 제한 |
| Reference contextual help | Global top block | 제거하고 module methodology / Reference Center로 통합 |

## Design Implications

- 새 summary cockpit을 Market Research 상단에 추가하지 않는다. Today가 이미 이 역할을 소유한다.
- page heading은 `Market Research`로 정렬하고, 한 줄 purpose만 둔다.
- 공통 장 session banner와 공통 freshness roll-up은 제거한다. 기준일·자료상태·refresh action은 active module이 소유한다.
- 다섯 개 source-name tab 대신 사용 목적 기반 2-level navigation을 우선 검토한다.
- query parameter와 기존 module renderer는 compatibility boundary로 보존한다.
- live trading, validation gate, monitoring signal, provider fetch-on-render는 범위 밖이다.

## Open Decision

종목 조사(`Market Movers`, `U.S. Stock`)를 동일 Market Research page의 `종목 리서치` family로 둘지, 상위 `Stock Research` page로 분리할지가 이번 개편의 가장 큰 IA 결정이다.
