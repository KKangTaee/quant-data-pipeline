# Overview Nav Internal Lazy Load V1 Plan

## 이걸 하는 이유?

직전 `Overview Primary Nav Pill V1`은 디자인을 개선하려고 HTML anchor 기반 pill nav를 만들었지만, 탭 전환이 Streamlit 내부 상태가 아니라 링크 이동처럼 동작했다.
또한 앱 최초 진입 시 기본 `Market Context` 본문이 즉시 무거운 cockpit read model을 로드해 첫 화면이 늦게 뜬다.

## Scope

- Replace anchor-based Overview primary nav with a Streamlit internal single-selection pill widget.
- Keep the four primary tabs: `Market Context`, `Market Movers`, `Sentiment`, `Events`.
- Add a first-visit lazy load gate so default `Market Context` does not load its heavy body until the user runs it.
- Keep direct query-param read support for existing links, but do not render navigation anchors.

## Out Of Scope

- Provider / schema / DB / registry / saved JSONL changes.
- Physical deletion of old Futures / sector helper code.
- New data-health diagnostic panel.
- Trading signal, recommendation, validation gate, monitoring signal, broker order, or auto rebalance semantics.
