# Institutional Portfolios React Workbench V1 Plan

Status: Active
Started: 2026-07-09

## 이걸 하는 이유?

기존 `Workspace > Institutional Portfolios` V1은 SEC 13F ingestion / DB / loader 경계는 만들었지만, 사용자 기대였던 "대가 / 기관 포트폴리오를 시각적으로 탐색하는 화면"이 아니라 DB 조회와 수집 안내가 먼저 보이는 Streamlit table surface에 가까웠다.

이번 작업은 같은 13F source / caveat / read-only boundary를 유지하면서 첫 화면을 기관 선택, 포트폴리오 도넛, 상위 보유, 분기 변화, 종목별 보유기관 drill-down 중심의 제품형 React workbench로 바꾼다.

## Roadmap

1차: React workbench skeleton / payload contract 테스트
- 화면 / 파일 범위: `tests/test_institutional_portfolios.py`, `app/web/streamlit_components/institutional_portfolios_workbench/`
- 완료 조건: visual payload contract와 component bridge 테스트가 먼저 실패하고, component skeleton이 빌드 가능한 상태가 된다.

2차: Python read model v2
- 화면 / 파일 범위: `app/services/institutional_portfolios.py`
- 완료 조건: manager summary, donut segments, top holdings, change boards, sector bars, preview state, caveats를 React payload로 제공한다.

3차: Streamlit shell 교체
- 화면 / 파일 범위: `app/web/institutional_portfolios.py`, React component bridge
- 완료 조건: page가 ingestion-first table layout이 아니라 React component를 첫 화면으로 렌더링하고, 표는 fallback / lower detail로 내려간다.

4차: DB empty / preview experience
- 화면 / 파일 범위: service payload, page fallback copy, component empty state
- 완료 조건: DB가 비어도 "수집 job 안내"가 주인공이 아니라 명확히 표시된 preview / setup 안내가 제품형 화면으로 보인다.

5차: Holdings click -> Institutional Interest drill-down
- 화면 / 파일 범위: React event contract, Streamlit session state, reverse lookup service
- 완료 조건: 보유 종목 클릭 시 같은 화면에서 해당 종목 보유 주요 기관 / 대가를 볼 수 있다.

6차: Docs / QA / commit
- 화면 / 파일 범위: task docs, durable docs where needed, tests, Browser QA
- 완료 조건: focused tests, npm build, py_compile, git diff check, UI/engine boundary, Browser QA screenshot, commit 완료.

## Non Goals

- 새 provider / paid API integration
- live trading, broker order, auto rebalance, portfolio approval
- Dataroma / WhaleWisdom scraping
- 13F data를 실시간 매수 / 매도 신호로 표현
- complete security master 수준 CUSIP-symbol mapping
