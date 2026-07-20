# Portfolio Monitoring Position Events V1 Risks

## Open Implementation Risks

- transaction-aware item unit index와 group-level flow-neutral aggregation이 기존 no-event KPI를 바꾸지 않도록 별도 regression fixture가 필요하다.
- 같은 날 여러 거래는 root에 고정된 `event_order`를 지켜야 하며 replace/void 후 전체 후속 이벤트 재검증이 필요하다.
- split day와 transaction day가 겹칠 때 승인된 split-first 순서를 테스트로 고정해야 한다.
- 거래 시각을 입력하지 않으므로 daily Modified Dietz는 모든 같은 날 flow에 고정 `0.5` 가중치를 사용한다. UI와 문서에서 이를 actual intraday return으로 표현하면 안 된다.
- actual execution price와 DB close 차이는 정상 입력일 수 있으므로 자동 보정하지 않고 reference로만 표시해야 한다.
- 초기 수량 정정으로 최초 자본이 바뀌면 group contribution과 historical KPI가 의도대로 전 구간 재계산되어야 한다.

## Boundaries

- full sell, tax lot/FIFO, realized-vs-unrealized cost-basis reporting, group cash account, cross-item transfer는 V1 범위가 아니다.
- Browser QA screenshot은 generated artifact로 유지하고 명시 요청 없이는 commit하지 않는다.
