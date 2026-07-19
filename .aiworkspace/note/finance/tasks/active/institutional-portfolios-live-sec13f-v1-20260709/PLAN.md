# Institutional Portfolios Live SEC 13F V1 Plan

## 이걸 하는 이유?

`Workspace > Institutional Portfolios`는 이미 React visual workbench 형태를 갖췄지만, 로컬 DB에 SEC 13F 테이블 / row가 없으면 preview sample로만 보인다. 사용자가 원하는 것은 수집 job 화면이 아니라 이미 수집된 투자 대가 / 기관의 13F 포트폴리오를 탐색하는 실제 제품 화면이다.

이 작업은 SEC 공식 Form 13F dataset을 primary source로 삼고, 수동 최신화는 보조 액션으로 유지하면서 `Ingestion -> DB -> Loader -> Service read model -> UI` 경계를 제품 사용 흐름에 맞게 연결한다.

## Scope

- 1차: read model / DB schema / UI contract TDD
- 2차: SEC 공식 13F ingestion 안정화
- 3차: 수동 최신화 / refresh status 관리
- 4차: React workbench live DB data 연결 보강
- 5차: reverse lookup / quarter change / sector exposure 보강
- 6차: docs / runbook / focused tests / Browser QA / commit

## Non-goals

- Dataroma / WhaleWisdom / Fintel scraping 구현
- broker order, live trading, auto rebalance, approval workflow 연결
- 13F 보고 변화를 실시간 매수 / 매도 추천으로 표현
- full holdings나 provider raw response를 JSONL registry에 저장

## Done Criteria

- SEC 13F official dataset ingestion이 schema init, idempotent write, refresh status 기록을 제공한다.
- Institutional Portfolios page의 첫 화면은 portfolio explorer이며 refresh는 보조 액션으로 남는다.
- DB live data가 있으면 preview가 아니라 manager / filing / holdings / changes / exposure / reverse lookup을 표시한다.
- DB가 비어 있거나 table이 없으면 preview/sample임을 명확히 표시하고 다음 행동을 안내한다.
- focused Python tests, py_compile, React 변경 시 npm build, git diff --check, UI/engine boundary check, Browser QA screenshot을 수행한다.
