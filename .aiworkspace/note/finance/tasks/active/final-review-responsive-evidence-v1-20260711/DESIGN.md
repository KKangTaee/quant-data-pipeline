# Design

- `.fr-invest-report__review-impact > div`를 header first child에만 적용한다.
- `.fr-invest-report__review-trace-list`는 명시적인 `minmax(0, 1fr)` 단일 열을 소유한다.
- trace section / paragraph / details에 `min-width: 0`, `overflow-wrap`, `word-break`를 적용한다.
- compact breakpoint에서는 header badge를 다음 행으로 내리고, mobile에서는 관측 / 판단 근거 label과 value를 세로로 쌓는다.
