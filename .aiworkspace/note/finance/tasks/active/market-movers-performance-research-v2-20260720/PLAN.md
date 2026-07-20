# Market Movers Performance And Research V2 Implementation Plan

**Goal:** Market Movers의 cold entry와 Top Rank 선택 지연을 제거하고, 갱신 상태·breadth·가격 hover·10년 재무·뉴스/공시 근거를 하나의 빠른 decision workflow로 완성한다.

**Architecture:** Python payload를 current breadth key와 selected research/evidence 단위로 분리하고, React는 필요한 key를 event로 요청한다. 기존 ingestion/job handler를 재사용하며 UI render에서 provider를 자동 호출하지 않는다.

## Task 1 — Lazy breadth and selected research boundary

- [ ] payload/service regression tests를 RED로 추가한다.
- [ ] 현재 breadth 조합만 load하고 loaded context를 session/cache에서 재사용한다.
- [ ] breadth request event와 symbol-only research event를 분리한다.
- [ ] 공통 date-window cache와 적절한 TTL을 적용한다.
- [ ] cold load/click timing을 재측정한다.

## Task 2 — Header freshness, manual actions, breadth toolbar, return tones

- [ ] payload/React source contract를 RED로 추가한다.
- [ ] 네 timestamp 의미와 existing manual action을 decision shell에 렌더링한다.
- [ ] breadth controls를 labeled single toolbar로 변경한다.
- [ ] positive/negative/neutral return tone helper를 적용한다.
- [ ] React focused tests/build를 실행한다.

## Task 3 — Price hover and 10-year financial chart

- [ ] financial limit/hover/chart-mode regression tests를 RED로 추가한다.
- [ ] annual 10 / quarterly 40 limit을 적용한다.
- [ ] pointer/focus hover guide, dot, tooltip을 구현한다.
- [ ] factor-specific default와 bar/line toggle을 구현한다.
- [ ] ResizeObserver frame-height sync를 적용한다.

## Task 4 — News and SEC evidence

- [ ] selected evidence payload/action tests를 RED로 추가한다.
- [ ] DB filing ledger를 compact SEC evidence로 변환한다.
- [ ] existing manual news metadata session/action을 one-shell에 연결한다.
- [ ] empty/loading/source boundary를 UI에 표시한다.

## Task 5 — Verification, Browser QA, docs, review

- [ ] focused Python tests와 TypeScript/Vite build를 실행한다.
- [ ] cold entry, Top Rank, breadth switch, price hover, financial chart, events action을 Browser QA한다.
- [ ] desktop/narrow screenshot 1장을 생성하고 commit에서 제외한다.
- [ ] independent code review의 Critical/Important issue를 처리한다.
- [ ] task docs와 durable docs/root logs를 동기화한다.
- [ ] 사용자 artifact를 제외하고 coherent commit을 만든다.

