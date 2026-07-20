# Runs

## 2026-07-20

- group snapshot DB timing: sector daily 0.660s, weekly 1.991s, monthly 8.474s; industry daily 0.467s, weekly 1.726s, monthly 8.674s.
- actual Browser cold entry: 약 46초까지 재현.
- selected research DB timing: TER 0.862s, COHR 0.855s.
- monthly sector query profiling: total 8.206s / 9 queries; market-date aggregation 8.062s.
- 사용자 승인: 이전 권장안 전체 + 현재/갱신 시각 + manual refresh + semantic return color.
- Task 1 RED: lazy breadth/reuse와 request event 테스트 `2 failed` 확인.
- Task 1 GREEN: focused event tests `3 passed`; 전체 decision UI tests `12 passed`.
- Python compile 통과; Vite production build `170 modules transformed`.
- Task 2 RED: timing/action payload와 grouped breadth/return tone source contract `2 failed` 확인.
- Task 2 GREEN: focused tests `2 passed`; 전체 decision UI tests `14 passed`.
- Task 2 Vite production build `170 modules transformed`.
