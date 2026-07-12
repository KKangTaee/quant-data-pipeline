# Institutional Portfolios Two-Tier Tabs V1 Design

## Direction

현재 `ip-view-tabs--grouped`는 한 줄 안에서 작은 라벨과 탭 버튼을 섞는다. 이 구조는 "구분"은 생겼지만 탭 hierarchy가 시각적으로 확실하지 않다.

개선 방향은 별도 navigation block 안에서 상위 탭과 하위 탭을 분리하는 것이다.

- `activeView`는 그대로 유지한다.
- `activeWorkspaceSection`은 `activeView`에서 파생한다.
- 상위 `포트폴리오` 클릭은 `overview`, 상위 `종목 분석` 클릭은 `security`로 이동한다.
- 하위 탭은 현재 상위 영역에 해당하는 버튼만 보여준다.

## Files

- `app/web/streamlit_components/institutional_portfolios_workbench/src/InstitutionalPortfoliosWorkbench.tsx`
  - `WorkspaceSection` type, derived active section, top-level switch helper, two-tier nav markup.
- `app/web/streamlit_components/institutional_portfolios_workbench/src/style.css`
  - old grouped tab styles replaced with primary / secondary tab styles.
- `tests/test_institutional_portfolios.py`
  - source contract for two-tier tabs.

## Boundary

No Python service, loader, ingestion, DB schema, provider, trading, recommendation, broker, or auto-rebalance behavior changes.
