# Futures Monitor Workbench Layout V1 Plan

## 이걸 하는 이유?

기존 Futures Monitor 개선은 한글화와 중복 제거에는 도움이 됐지만, 화면은 여전히 form controls + card grid처럼 보인다. 사용자는 “현재 선물/매크로 상태를 어떻게 읽고 무엇을 확인해야 하는가”를 한 화면에서 끝내야 한다.

이번 작업은 benchmark research 결과를 코드로 옮겨, `Workspace > Overview > Futures Monitor`를 compact market workbench로 재구성한다.

## 전체 개발 흐름

### 1차: Contract와 작업 범위 고정

- 목적: context bar, market brief, weekly lane의 표시 계약을 테스트로 고정한다.
- 파일 범위: `tests/test_service_contracts.py`, `app/web/overview_dashboard.py`.
- 완료 조건: 새 helper contract가 없어서 실패하는 RED 테스트를 확인한다.

### 2차: Context Bar / Refresh Strip / Watch Strip

- 목적: 기존 command center를 workbench context bar로 바꿔 관찰 범위, 시간/봉/차트 범위, 데이터 상태, 갱신 행동을 한 줄 흐름으로 읽게 한다. 큰 multiselect는 접힌 편집 영역으로 낮추고, 기본 화면에는 compact watch strip을 둔다.
- 파일 범위: `app/web/overview_dashboard.py`, `app/web/overview_ui_components.py`.
- 완료 조건: provider run rows / latest candle detail은 default surface에 나오지 않고, 선택 심볼의 단기 상태는 watch strip에서만 읽힌다.

### 3차: Market Brief Hero

- 목적: Macro Context를 카드 나열이 아니라 `오늘 기준 시장 해석` 중심 hero로 만든다.
- 파일 범위: `app/web/overview_dashboard.py`, `app/web/overview_ui_components.py`.
- 완료 조건: 시나리오, 한 줄 해석, 근거 강도/과거 점검/유사 구간/자료 기준이 hero 안에서 함께 읽힌다.

### 4차: Weekly Flow Lane

- 목적: 최근 1주 흐름을 반복 카드가 아니라 dominant driver + support / temper lane으로 보여준다.
- 파일 범위: `app/web/overview_dashboard.py`, `app/web/overview_ui_components.py`.
- 완료 조건: 가장 큰 1주 변화와 오늘 해석을 지지/완화하는 항목이 구분된다.

### 5차: Chart Workspace Alignment

- 목적: 차트 영역을 하단 부록이 아니라 “이 차트에서 확인할 것”이 있는 linked workspace로 정렬한다.
- 파일 범위: `app/web/overview_dashboard.py`, `app/web/overview_ui_components.py`.
- 완료 조건: Live Chart section header가 chart question을 설명하고 symbol-level state만 유지한다.

### 6차: QA / 문서 / 커밋

- 목적: focused tests, compile, Browser QA, docs sync, commit.
- 파일 범위: task docs, root logs, flow docs if needed.
- 완료 조건: screenshot artifact는 커밋하지 않고, 코드/테스트/task docs만 commit한다.

## Non-goals

- 새 DB schema, provider, loader, registry / saved write 없음.
- live trading, broker order, recommendation signal, validation gate, monitoring signal 없음.
- Watch rail 완전 교체는 이번 V1에서 제외한다. 대신 기본 화면은 compact watch strip으로 읽고, 기존 multiselect는 접힌 edit control로 유지한다.
- React / Next.js 전환은 제외한다.

## Verification Plan

- RED/GREEN helper tests:
  - `test_futures_workbench_context_bar_items_compactly_summarize_controls`
  - `test_futures_market_brief_model_places_scenario_and_support_together`
  - `test_futures_weekly_flow_model_ranks_driver_and_supports`
  - `test_futures_watch_strip_items_show_symbol_state_without_provider_run`
- Focused:
  - `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests tests.test_service_contracts.FuturesMacroThermometerContractTests tests.test_service_contracts.FuturesMarketMonitoringContractTests`
- Compile:
  - `uv run python -m py_compile app/web/overview_dashboard.py app/web/overview_ui_components.py tests/test_service_contracts.py`
- Hygiene:
  - `git diff --check`
- Browser QA:
  - Streamlit app on local port, `Workspace > Overview > Futures Monitor` full-page screenshot.
