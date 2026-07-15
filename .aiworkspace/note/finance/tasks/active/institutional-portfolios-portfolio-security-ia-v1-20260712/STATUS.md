# Institutional Portfolios Portfolio / Security IA V1 Status

Status: Completed
Started: 2026-07-12
Completed: 2026-07-12

## Progress

- 2026-07-12: 사용자가 `요약 / 전체 보유`는 기관 포트폴리오 탭이고 `보유 기관 조회 / 기관 보유 랭킹`은 티커 / 기업 카테고리라 같은 1차 탭에 두는 것이 어색하다고 지적했다.
- 2026-07-12: TDD RED로 React workbench가 아직 `interest` view와 flat tab list를 사용하는 것을 확인했다.
- 2026-07-12: 1차 탭을 `포트폴리오` 그룹과 `종목 분석` 그룹으로 분리하고, `보유 기관 조회` 탭을 `종목 상세`로 바꿨다.
- 2026-07-12: 포트폴리오 비중 / 성과 / 전체 보유 row click은 `종목 분석 > 종목 상세`로 이동하게 했다.
- 2026-07-12: Browser QA에서 grouped tabs, old `보유 기관 조회` tab 제거, AAPL drilldown의 `종목 상세` active 상태와 chart 표시를 확인했다.

## Current Verification

- `tests.test_institutional_portfolios`: passing.
- `py_compile`: passing for touched Python files.
- `npm run build`: passing for Institutional Portfolios workbench.
- `git diff --check`: passing.
- Browser QA: current `http://localhost:8528/institutional-portfolios` had no `8528` console errors; screenshots saved as local generated artifacts and excluded from commit.

## Boundary

- React UI / copy / CSS IA 변경만 수행했다.
- DB schema, ingestion, provider, trading / recommendation semantics는 변경하지 않았다.
