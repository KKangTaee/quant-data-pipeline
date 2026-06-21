# Overview Market Context Macro Clarity V14 Notes

## Decisions

- `Sector ETF vs SPY relative strength` is the broad analog basis and should not be presented as a Macro 추가 조건.
- GLD and rate-pressure futures are the only current hard Macro 추가 조건.
- T10Y3M, VIXCLS, and BAA10Y should be shown as current macro backdrop/reference state, not hidden as developer-style preview labels.
- Events and sentiment remain annotation/deferred until separate historical conditioning criteria are approved.
- Macro conditioned rows are the same distribution calculation as the broad rows, but over a narrower anchor set.

## Discoveries

- Current live payload narrows broad 81 anchors to GLD-context 37 anchors, then GLD + rate-pressure futures 6 anchors.
- Current live macro backdrop values: T10Y3M 0.76 positive, VIXCLS 21.51 watch, BAA10Y 1.51 contained.
- The old `Macro 조건 포함 핵심 자산` table was not a better prediction table. It was the same forward-return distribution calculation over the narrowed conditioned anchor set.
- The useful user-facing result is the broad-vs-conditioned delta, for example XLY 20D broad +1.6% versus conditioned -7.2% in the live payload.
