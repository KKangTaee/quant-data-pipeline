# Runs

## 2026-07-17 Planning

- Confirmed EIA official XLS URLs and workbook shape for `WCESTUS1`, `WCRFPUS2`, `WRPUPUS2`.
- Confirmed existing FRED, futures, S&P price, and S&P actual EPS storage/read boundaries.
- No product code changed during design and planning.

## 2026-07-17 Implementation

- Baseline: focused Economic Cycle suite `87 passed`.
- TDD로 EIA 수집/저장, DB-only 자산 loader, 혼합 빈도 판정기, 채권·금리, S&P 500, 원자재, service/UI 연결을 Task 1~8 순서로 구현했다.
- Actual collection: T10YIE·EIA 3계열 `8,049` rows, `^GSPC`·SPY `5,026` rows, CL/HG/GC/DX futures `10,055` rows를 저장했다.
- 최신 actual 기준: T10YIE `2026-07-16`, EIA 3계열 `2026-07-10`, DGS/DFII/VIX/BAA `2026-07-15`, futures `2026-07-17`, `^GSPC` `2026-07-16`.
- 공식 actual S&P EPS 완료 분기는 `0`개라 EPS 경로는 `UNAVAILABLE`로 독립 격리했다.
- Focused regression `104 passed`, 기존 edgartools deprecation warning 3건만 남았다.
- Component-local `npx tsc --noEmit`, `npm run build` 통과.
- Browser QA: stale Streamlit process를 재시작한 뒤 채권 `SUFFICIENT`, S&P 500 `PARTIAL`, 원자재 `PARTIAL` actual render, hover/focus 상세, desktop 2열, mobile 1열·가로 overflow 0을 확인했다.
- Browser에서 발견한 채권 현재 움직임 3열 압축은 implication card 내부 1열 규칙으로 보정하고 source-contract test와 production build를 재통과했다.
