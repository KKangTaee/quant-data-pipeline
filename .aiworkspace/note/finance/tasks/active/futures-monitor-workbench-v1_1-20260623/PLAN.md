# Futures Monitor Workbench V1.1 Plan

## 이걸 하는 이유?

Workbench Layout V1 made `Workspace > Overview > Futures Monitor` read more like a market workbench, but the lower Macro evidence / validation / refresh area still feels partly prototype-like.

이번 작업은 새 기능을 추가하지 않고, 이미 저장된 futures 1분봉 / 1D OHLCV, Macro score, validation read model을 더 제품형 흐름으로 읽게 만든다. 기본 사용자는 `현재 상태 -> 현재 근거 -> 과거 점검 -> 자료 관리 -> 원본 표` 순서로 읽고, 상세 사용자는 접힌 원본 표에서 계산 근거를 확인한다.

## 전체 개발 흐름

### 1차: Task / Contract 고정

- 목적: V1.1 범위와 non-goal을 task docs에 고정하고, production code 전 focused failing tests를 추가한다.
- 파일 범위: `tests/test_service_contracts.py`, task docs.
- 완료 조건: guide-like title / old refresh split / table-first validation을 잡는 RED 테스트를 확인한다.
- 다음 차수 연결: RED가 구현 범위를 제한한다.

### 2차: 자료 갱신 Module 통합

- 목적: 상단 `1분봉 갱신`, 하단 `갱신 설정`, disclosure 내부 `일봉 매크로 데이터 갱신`을 하나의 `자료 갱신` module로 묶는다.
- 파일 범위: `app/web/overview_dashboard.py`, `app/web/overview_ui_components.py`.
- 완료 조건: module 안에서 `실시간 차트 자료`와 `매크로 일봉 자료`가 구분되고, context bar는 버튼 문구가 아니라 상태를 요약한다.
- 다음 차수 연결: 갱신 행동이 분석 흐름에서 분리되어 evidence 영역이 현재 해석 중심으로 읽힌다.

### 3차: 현재 근거 상태

- 목적: `근거를 어떻게 읽을까` guide wording을 `현재 근거 상태`로 바꾸고 strong / weak / conflicting / missing을 count와 상태형 empty label로 제공한다.
- 파일 범위: `app/services/futures_macro_thermometer.py`, `app/web/overview_dashboard.py`.
- 완료 조건: 근거 항목이 score label, symbol, z-score, 영향 강도, 현재 의미 문장으로 렌더링된다.
- 다음 차수 연결: 과거 점검 요약이 현재 근거 뒤에 자연스럽게 온다.

### 4차: 과거 점검 Summary-first

- 목적: 현재 scenario 기준의 validation summary를 먼저 보여주고 raw scenario table은 접힌 상세로 낮춘다.
- 파일 범위: `app/services/futures_macro_validation.py`, `app/web/overview_dashboard.py`.
- 완료 조건: 현재 scenario, 발생 횟수/5D sample, PIT 날짜 수, history span, hit-rate 적용 여부, confidence 영향 문장이 제공된다.
- 다음 차수 연결: raw tables는 상세 분석자의 확인 영역으로 재정렬한다.

### 5차: Disclosure / 중복 노출 QA

- 목적: `근거 해석 / 원본 데이터` 안을 `현재 근거 상태 -> 과거 점검 요약 -> 자료 관리 -> 원본 표` 순서로 정리한다.
- 파일 범위: `app/web/overview_dashboard.py`, `app/web/overview_ui_components.py`.
- 완료 조건: context bar는 상태 요약, refresh module은 action, watch strip은 symbol-level 상태, evidence disclosure는 macro 근거와 validation summary, raw disclosure는 원본 표를 소유한다.
- 다음 차수 연결: Browser QA에서 반복 문구와 화면 위계를 확인한다.

### 6차: 검증 / 문서 / 커밋

- 목적: focused tests, compile, diff check, Browser QA screenshot, docs sync, coherent commit.
- 파일 범위: task docs, `docs/flows/README.md`, root handoff logs if needed.
- 완료 조건: generated screenshot / `.DS_Store` / `.superpowers/` / run history는 stage하지 않고 관련 코드, tests, docs만 commit한다.

## Non-goals

- provider / schema / DB / registry / saved JSONL 변경 없음.
- UI render 중 외부 provider direct fetch 없음.
- trading signal, 매수/매도 추천, validation gate, monitoring signal, broker order, auto rebalance semantics 없음.
- 표 제거 없음. 기본 흐름에서는 summary-first로 낮추고 raw tables는 disclosure에 보존한다.

## Verification Plan

- RED/GREEN focused tests:
  - evidence reading current-state contract
  - current scenario validation summary contract
  - unified refresh module contract
  - context bar status-only next action contract
- Focused suite:
  - `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests tests.test_service_contracts.FuturesMacroThermometerContractTests tests.test_service_contracts.FuturesMarketMonitoringContractTests`
- Compile:
  - `uv run python -m py_compile app/web/overview_dashboard.py app/web/overview_ui_components.py app/services/futures_macro_thermometer.py app/services/futures_macro_validation.py tests/test_service_contracts.py`
- Hygiene:
  - `git diff --check`
- Browser QA:
  - local Streamlit, `Workspace > Overview > Futures Monitor`, screenshot artifact not staged.
