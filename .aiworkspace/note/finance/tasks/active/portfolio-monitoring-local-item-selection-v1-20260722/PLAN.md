# Portfolio Monitoring 로컬 종목 선택 구현 계획

## 목표

종목·전략 결과에서 항목을 선택할 때 Streamlit 전체 rerun 없이 개별 추적 결과만 즉시
바꾸고, 데이터 변경 command의 기존 서버 재실행 경계는 보존한다.

## Task 1. Python item detail projection

**Files**

- Modify: `tests/test_portfolio_monitoring_read_model.py`
- Modify: `app/services/portfolio_monitoring/read_model.py`

1. 두 항목 workspace의 `item_details`와 항목별 position/chart를 기대하는 실패 테스트를 쓴다.
2. 테스트가 새 field 부재로 실패하는지 확인한다.
3. lane 재계산 없이 항목별 position을 투영하고, configured loader로 항목별 차트를 제한해
   만드는 최소 구현을 추가한다.
4. loader 미설정과 한 항목 오류 격리를 검증한다.

## Task 2. React local detail selection

**Files**

- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/contracts.ts`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.ts`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.test.ts`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx`
- Modify: `tests/test_portfolio_monitoring_component.py`

1. item detail 선택과 legacy fallback의 실패 테스트를 쓴다.
2. workspace 계약과 순수 선택 helper를 추가한다.
3. `chooseItem`에서 서버 emit을 제거하고 선택된 position/chart를 helper 결과로 렌더링한다.
4. source contract로 `select_item` event 미발행을 고정한다.

## Task 3. 회귀와 Browser QA

**Files**

- Modify: active task `STATUS.md`, `RUNS.md`, `RISKS.md`
- Modify: 관련 durable flow/architecture 문서와 root handoff log

1. 관련 Python 전체 테스트, React test/typecheck/build, `git diff --check`를 실행한다.
2. Streamlit을 실행하고 브라우저에서 두 종목 선택 전후 scroll 위치, 선택 제목, 차트 전환을
   확인한다.
3. QA 화면 1장을 generated artifact로 남긴다.
4. 구현과 문서를 coherent commit으로 만든다.

