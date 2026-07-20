# Market Movers Performance And Research V2 Implementation Plan

**Goal:** Market Movers의 cold entry와 Top Rank 선택 지연을 제거하고, 갱신 상태·breadth·가격 hover·10년 재무·뉴스/공시 근거를 하나의 빠른 decision workflow로 완성한다.

**Architecture:** Python payload를 current breadth key와 selected research/evidence 단위로 분리하고, React는 필요한 key를 event로 요청한다. 기존 ingestion/job handler를 재사용하며 UI render에서 provider를 자동 호출하지 않는다.

## Task 1 — Lazy breadth and selected research boundary

- [x] payload/service regression tests를 RED로 추가한다.
- [x] 현재 breadth 조합만 load하고 loaded context를 session/cache에서 재사용한다.
- [x] breadth request event와 symbol-only research event를 분리한다.
- [x] group/research cache TTL을 10분으로 늘리고 manual refresh에서 session breadth를 무효화한다.
- [x] cold load/click timing을 Browser QA에서 재측정한다.

## Task 2 — Header freshness, manual actions, breadth toolbar, return tones

- [x] payload/React source contract를 RED로 추가한다.
- [x] 네 timestamp 의미와 existing manual action을 decision shell에 렌더링한다.
- [x] breadth controls를 labeled single toolbar로 변경한다.
- [x] positive/negative/neutral return tone helper를 적용한다.
- [x] React focused tests/build를 실행한다.

## Task 3 — Price hover and 10-year financial chart

- [x] financial limit/hover/chart-mode regression tests를 RED로 추가한다.
- [x] annual 10 / quarterly 40 limit을 적용한다.
- [x] pointer/focus hover guide, dot, tooltip을 구현한다.
- [x] factor-specific default와 bar/line toggle을 구현한다.
- [x] ResizeObserver frame-height sync를 적용한다.

## Task 4 — News and SEC evidence

- [x] selected evidence payload/action tests를 RED로 추가한다.
- [x] DB filing ledger를 compact SEC evidence로 변환한다.
- [x] existing manual news metadata session/action을 one-shell에 연결한다.
- [x] empty/loading/source boundary를 UI에 표시한다.

## Task 5 — Verification, Browser QA, docs, review

- [x] focused Python tests와 TypeScript/Vite build를 실행한다.
- [x] cold entry, Top Rank, breadth switch, price hover, financial chart, events action을 Browser QA한다.
- [x] desktop/narrow screenshot 1장을 생성하고 commit에서 제외한다.
- [x] independent code review의 Critical/Important issue를 처리한다.
- [x] task docs와 durable docs/root logs를 동기화한다.
- [x] 사용자 artifact를 제외하고 coherent commit을 만든다.
