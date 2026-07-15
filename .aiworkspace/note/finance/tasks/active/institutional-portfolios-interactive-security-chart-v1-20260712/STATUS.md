# Institutional Portfolios Interactive Security Chart V1 Status

Status: Completed
Started: 2026-07-12
Completed: 2026-07-12

## Progress

- 2026-07-12: TDD RED로 selected-security chart payload가 OHLCV field를 포함하지 않는 점과 React가 아직 old mini line chart를 호출하는 점을 확인했다.
- 2026-07-12: service price frame / daily-weekly-monthly point builder를 OHLCV-aware payload로 확장했다.
- 2026-07-12: React selected-security chart를 `InteractiveSecurityChart`로 교체하고, 라인 / 캔들 toggle, hover tooltip, crosshair, high-low dotted guide, range slider, pan button을 추가했다.
- 2026-07-12: Browser QA에서 AAPL selected-security chart stage, range slider, high-low guide, hover tooltip/crosshair/dot이 생성되는 것을 확인했다.

## Current Verification

- `tests.test_institutional_portfolios`: passing.
- `py_compile`: passing for touched Python files.
- `npm run build`: passing for Institutional Portfolios workbench.
- Browser QA: current `http://localhost:8527/institutional-portfolios` had no `8527` console errors; screenshot saved as local generated artifact and excluded from commit.

## Boundary

- UI는 service payload만 읽고 외부 provider를 호출하지 않는다.
- 차트는 저장 가격 DB 기준이며 13F 보고 이후 실제 거래나 매수 / 매도 신호가 아니다.
