# Overview Market Movers Quality V5 Plan

## Goal

Market Movers 5차는 Coverage/Data Quality UX를 정리해 사용자가 현재 결과를 얼마나 신뢰해도 되는지, 어떤 coverage/period가 stale/partial/missing/no-universe인지, 무엇을 갱신해야 하는지 덜 헷갈리게 만든다.

## 이걸 하는 이유?

1~4차로 Market Movers는 변동종목 작업대, 탐색 모드, 선택 종목 조사, sector breadth 흐름을 갖췄다. 하지만 missing quote, stale snapshot, Nasdaq no-universe 같은 상태는 여전히 raw diagnostics 중심으로 읽힐 수 있어, 실제 사용자는 “현재 표를 봐도 되는가”와 “무엇을 눌러야 하는가”를 빠르게 판단하기 어렵다.

## Scope

- Existing snapshot/read model만 사용해 coverage trust read model을 추가한다.
- 상태 언어는 Good / Stale / Partial / Needs Refresh / No Universe / Missing Quotes 범위로 맞춘다.
- Missing diagnostics는 grouped summary를 먼저 보여주고 raw table은 collapsed expander에 둔다.
- Nasdaq no-universe는 Symbol Directory current snapshot 경계와 기존 Overview action facade refresh를 보여준다.
- 새 provider, DB schema, UI direct fetch, trade signal, validation gate, operations monitoring signal은 추가하지 않는다.

## Stop Condition

- 5차 구현, 검증, Browser QA screenshot, coherent commit까지 완료한다.
- 최종 보고 후 멈추고, 1~5차를 모두 이어서 확장하지 않는다.
