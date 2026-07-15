# Institutional Portfolios Selection Loading V1 Plan

## 이걸 하는 이유?

사용자가 `Workspace > Institutional Portfolios`의 manager rail을 클릭할 때 처음에는 포트폴리오가 바뀌지만 이후 브라우저 탭이 계속 로딩되는 것처럼 보이고 화면이 바뀌지 않는 문제가 있다. 이 화면은 수집 job 화면이 아니라 저장된 SEC 13F 포트폴리오 탐색 화면이므로, 클릭은 빠르게 선택 상태를 바꾸고 로딩 여부를 명확히 보여줘야 한다.

## 단계

1. 진단: 클릭 이벤트, selected manager fallback, reverse lookup 재실행 병목을 분리한다.
2. TDD: watchlist manager가 manager search 결과에 없어도 선택 가능한 회귀 테스트와 event 재처리 방지 테스트를 추가한다.
3. 선택/이벤트 구현: selected CIK resolver를 watchlist 포함 경로로 바꾸고, custom component 이벤트를 처리 후 소비/ack한다.
4. UX 구현: 클릭 즉시 loading/pending 상태를 보여주고 Runtime / Build를 Institutional Portfolios 기본 화면에서 제거한다.
5. 성능 구현: manager 변경 때 reverse lookup을 불필요하게 재실행하지 않고, reverse lookup SQL의 매번 전체 holdings 집계를 제거한다.
6. QA / 문서 / 커밋: focused tests, py_compile, React build, Browser 반복 클릭 QA, docs sync 후 커밋한다.

## 범위

- 포함: `app/web/institutional_portfolios.py`, `app/services/institutional_portfolios.py`, `finance/loaders/institutional_13f.py`, React workbench, focused tests, task/root docs.
- 제외: 새 SEC 수집 provider, Dataroma / WhaleWisdom / Fintel scraping, broker / live trading / auto rebalance.
