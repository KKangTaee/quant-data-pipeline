# Overview Market Context Load Gate Removal V1 Plan

## 이걸 하는 이유?

`overview-nav-internal-lazy-load-v1-20260623`에서 첫 Overview 진입 시간을 줄이기 위해 `Market Context` 본문 앞에 `시장 맥락 불러오기` gate를 넣었다.
하지만 사용자는 Overview의 기본 화면이 전처럼 곧바로 시장 맥락을 보여주길 기대했고, 버튼은 실제 사용 흐름을 한 단계 더 막는 장애물이 됐다.

## Scope

- Remove the `Market Context` explicit load gate and button.
- Keep the internal text-tab underline navigation and no-anchor switching behavior.
- Preserve current primary tabs: `Market Context`, `Market Movers`, `Sentiment`, `Events`.
- Measure what `Market Context` loads on entry and record the slow components.

## Out Of Scope

- Optimizing or changing the underlying data loaders in this pass.
- Provider / schema / DB / registry / saved JSONL changes.
- Trading signal, recommendation, validation gate, monitoring signal, broker order, or auto rebalance semantics.
