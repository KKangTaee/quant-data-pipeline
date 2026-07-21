# Portfolio Monitoring Initial Setting Correction V1 Runs

- 2026-07-21: INDEX, ROADMAP, PROJECT_MAP, script/UI/selection flow와 Position Events V1 task/data/architecture docs를 확인했다.
- 2026-07-21: schemas, command, persistence, position projection, valuation, read model, Streamlit bridge와 React position editor의 current start-date boundary를 확인했다.
- 2026-07-21: 사용자가 append-only 초기 설정 정정 권장안을 승인했다.
- 2026-07-21: 사용자가 written design을 승인했다.
- 2026-07-21: 초기 계약 저장/projection, command/valuation, Streamlit/React, migration/QA/docs의 4-task detailed TDD plan을 작성했다.
- 2026-07-21: schema/input/projection RED를 확인한 뒤 position-event optional dates, legacy fallback과 idempotent column upgrade를 구현했다.
- 2026-07-21: command/valuation RED를 확인한 뒤 locked DB entry resolver, 과거 거래·invalid sell rollback, corrected individual/group valuation을 구현했다.
- 2026-07-21: Streamlit/React RED를 확인한 뒤 DB-only initial-entry lookup, editor recovery, `최초 설정 정정` date/quantity form과 변경 전/후 preview/save gating을 구현했다.
- 2026-07-21: 운영 `ensure_schema()` 첫 실행은 `requested_start_date`, `effective_start_date` ALTER 2건만 수행했고 두 번째 실행은 ALTER 0건이었다. group/item/command/event row count는 전후 `1/5/8/0`, registry/saved combined SHA-256은 `4647c914be900f7d3b147931d5f15c3bc3d27f67abc0690826e1497053cf52a3`으로 동일했다.
- 2026-07-21: focused 및 full Portfolio Monitoring Python 회귀 156개, React 2 files/32개, TypeScript typecheck, Vite production build, py_compile, `git diff --check`를 통과했다.
- 2026-07-21: actual `http://localhost:8502/selected-portfolio-dashboard`에서 Command Center/실데이터 로딩, 420px outer overflow 0, console error 0을 확인했다. QA screenshot: `/Users/taeho/Project/quant-data-pipeline-worktrees/main-dev/portfolio-monitoring-initial-setting-correction-qa.png` (generated, unstaged).
- 2026-07-21: actual Browser session의 Streamlit component iframe에서 종목 선택 event가 server session으로 round-trip되지 않아 정정 dialog 저장 click은 실행하지 않았다. 날짜·수량 lookup/payload/recovery/save/revaluation은 Python/React 자동화 회귀로 검증했다.
- 2026-07-21: closeout fresh verification은 Portfolio Monitoring Python 156개, docs 4개, React 32개, typecheck, production build, finance refinement hygiene와 `git diff --check`를 통과했다. 전역 UI/Engine boundary check는 이번 diff 밖의 기존 `app/services/backtest_workflow_shell.py:6 -> app.web.backtest_workflow_routes` import 1건 때문에 실패했다.
