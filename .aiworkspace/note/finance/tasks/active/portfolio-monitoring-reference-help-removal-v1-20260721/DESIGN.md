# Portfolio Monitoring Reference Help Removal V1 Design

Status: User-approved direction; written-spec review pending
Date: 2026-07-21

## Problem

`Operations > Portfolio Monitoring`은 페이지 시작에서 `render_reference_contextual_help("portfolio_monitoring")`를 먼저 호출한다. 이 때문에 실제 포트폴리오 확인 업무보다 큰 Streamlit expander가 앞에 나타난다.

패널의 내용은 별도 Reference Center에 이미 canonical item으로 존재한다.

- `journey.monitoring`: 선정 후 모니터링 흐름
- `concept.monitoring_scenario`: Portfolio Monitoring Scenario
- `playbook.monitoring_scenario_stale`: stale 시나리오 해결

따라서 이 패널은 고유 정보를 제공하지 않고 Reference Center 내용을 현재 업무 화면에 다시 복제한다.

## Considered Approaches

### A. Portfolio Monitoring contextual panel과 전용 설정 제거

- Portfolio Monitoring은 React Command Center부터 바로 시작한다.
- 위 세 canonical Reference item은 유지한다.
- 사용자는 상단 `Reference`에서 검색·journey·관련 항목으로 같은 안내를 확인한다.
- 장점: 중복과 첫 화면 방해를 함께 없애고 정보 source-of-truth를 하나로 유지한다.
- 단점: Portfolio Monitoring 안의 one-click deep link는 사라진다.
- 결정: 사용자 승인으로 채택한다.

### B. 한 줄 Reference 링크만 유지

- 전체 expander 대신 짧은 링크를 둔다.
- 화면 차지는 줄지만 같은 화면에 중복 entry가 남는다.
- 결정: 채택하지 않는다.

### C. 패널을 화면 하단으로 이동

- 첫 화면 방해는 줄지만 중복 설정과 renderer가 계속 남는다.
- 결정: 채택하지 않는다.

## Selected Design

### 1. Portfolio Monitoring surface cleanup

`app/web/final_selected_portfolio_dashboard.py`에서 `render_reference_contextual_help`의 중복 import와 `portfolio_monitoring` 호출을 제거한다. 페이지는 바로 workspace load와 React Command Center 렌더링으로 진입한다.

### 2. Contextual catalog cleanup

`app/services/reference_contextual_help.py`의 `surface_key="portfolio_monitoring"` row를 삭제한다. dead configuration을 남기지 않으며 `get_reference_contextual_help("portfolio_monitoring")`는 `None`을 반환한다.

다른 화면의 shared contextual helper와 catalog row는 이번 범위에서 변경하지 않는다.

### 3. Canonical Reference preservation

`app/services/reference_center.py`의 다음 item은 변경하지 않는다.

- `journey.monitoring`
- `concept.monitoring_scenario`
- `playbook.monitoring_scenario_stale`

이 item들의 `destination="portfolio_monitoring"`도 유지하므로 Reference에서 owner 화면으로 이동하는 경로는 보존된다. 새로운 링크나 대체 패널은 추가하지 않는다.

### 4. Contract and documentation alignment

contextual-help test의 required surface와 owner call-site에서 Portfolio Monitoring을 제거하고, catalog drift 기대값을 7개에서 6개로 맞춘다. defensive-copy test는 남아 있는 surface를 사용하도록 바꾼다.

durable flow/project map에서 Portfolio Monitoring을 contextual help 소유 화면으로 설명하는 문구를 제거한다. Reference Center 자체가 선정 후 모니터링 도움말을 소유한다는 설명은 유지한다.

## User Flow After Change

1. 사용자가 `Operations > Portfolio Monitoring`을 연다.
2. 별도 도움말 expander 없이 Portfolio Monitoring Command Center가 바로 시작한다.
3. 개념·stale 해결 안내가 필요하면 상단 `Reference`에서 `모니터링`, `scenario`, `stale`을 검색한다.
4. Reference의 owner 이동 action은 기존처럼 Portfolio Monitoring으로 돌아온다.

## Scope And Boundaries

- Portfolio Monitoring 데이터, command, 진단, 차트, position event, DB 계약은 변경하지 않는다.
- Reference Center catalog item, 검색, deep link, owner destination은 변경하지 않는다.
- 다른 여섯 contextual help surface는 변경하지 않는다.
- 새 도움말 CTA, 배너, 진단 패널을 추가하지 않는다.

## Implementation Roadmap

### 1차: 호출·전용 설정·계약 제거

- Portfolio Monitoring renderer call/import 제거
- Portfolio Monitoring contextual catalog row 제거
- focused RED→GREEN contract tests
- 완료 조건: Portfolio Monitoring source와 contextual catalog에 전용 help entry가 없고 canonical Reference 세 item은 유지됨

### 2차: Browser QA와 문서 closeout

- actual/isolated Portfolio Monitoring 첫 화면에서 help expander 미노출 확인
- Command Center 정상 렌더와 console/horizontal overflow 확인
- Reference 검색에서 세 canonical item 유지 확인
- durable docs/task/root log 동기화와 commit
- 완료 조건: 화면 제거와 정보 보존을 자동·Browser 검증으로 모두 확인

## Expected Files

- `app/web/final_selected_portfolio_dashboard.py`
- `app/services/reference_contextual_help.py`
- `tests/test_reference_contextual_help.py`
- `tests/test_portfolio_monitoring_page.py` 또는 focused source-contract test
- `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- active task docs와 root handoff logs

