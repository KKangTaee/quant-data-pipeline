# Overview Market Context Turnaround Stage Semantics Fix V1 Risks

Last Updated: 2026-07-16

## Guarded Risks

1. EPS unit fix could change multiple issuers at once; query-spy and actual AAPL plus negative-EPS fixtures must cover it.
2. `이미 양수`를 transition MET으로 저장하면 history semantics가 왜곡된다; UI-local display state로만 둔다.
3. profitable-but-flat operating margin must not look like a loss or data failure.
4. copy change must preserve color-independent status text and 420px layout.
5. existing S&P/PER payload and selected-analysis switch must not regress.

## Open Until Implementation

- actual negative-EPS company Browser QA symbol selection
- repository-wide unrelated existing test failures classification
