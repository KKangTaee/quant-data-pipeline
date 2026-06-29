# Futures Monitor UX/UI V3 Plan

## 이걸 하는 이유?

`Workspace > Overview > Futures Monitor`는 1m 선물 차트, 1D Macro Thermometer, historical validation 근거를 이미 갖고 있지만, 현재 화면은 영어 라벨과 표 중심 evidence 때문에 사용자가 "오늘 시장을 어떻게 읽어야 하는지"를 바로 파악하기 어렵다.

이번 작업은 Futures Monitor를 read-only 시장 맥락 화면으로 유지하면서, 상단 제어 / macro 해석 / evidence / 원본 표의 위계를 재정리한다.

## 전체 개발 흐름

### 1차: 상단 제어와 갱신 UX 정리

- 목적: `Watch Group`, `Symbols`, `Window`, `Chart`, `Charts`, `Data Actions`를 한글 중심의 작업 흐름으로 바꾼다.
- 화면 / 파일 범위: `app/web/overview_dashboard.py`, 필요 시 `app/web/overview_ui_components.py`.
- 완료 조건: 사용자가 관찰 그룹, 선택 선물, 차트 범위, 데이터 갱신 방식을 한글 라벨로 이해한다.
- 다음 차수 연결: 정리된 상단 상태가 Macro Context와 Live Chart의 기준 정보로 이어진다.

### 2차: Macro Context 해석 강화

- 목적: 오늘 기준 해석에 더해 최근 1주 흐름을 추가하고, confidence를 예측 확률이 아닌 근거 품질로 표시한다.
- 화면 / 파일 범위: `app/services/futures_macro_thermometer.py`, `app/web/overview_dashboard.py`, `tests/test_service_contracts.py`.
- 완료 조건: read model이 `weekly_context`와 해석형 evidence payload를 제공하고, UI가 오늘 / 최근 1주 / 주의점을 먼저 보여준다.
- 다음 차수 연결: evidence 섹션에서 왜 그렇게 해석했는지 풀어준다.

### 3차: Macro Evidence & Data 재구성

- 목적: raw table을 기본 해석보다 낮추고, 각 근거 그룹이 무슨 뜻인지 설명한다.
- 화면 / 파일 범위: `app/services/futures_macro_thermometer.py`, `app/web/overview_dashboard.py`.
- 완료 조건: `강한 근거`, `약한 근거`, `충돌 근거`, `자료 부족`을 한글 설명과 함께 보여주고, 원본 표는 evidence panel 하단으로 내려간다.
- 다음 차수 연결: QA에서 실제 레이아웃과 텍스트 밀도를 검증한다.

### 4차: QA / 문서 정렬 / closeout

- 목적: UI가 데스크톱에서 깨지지 않는지 확인하고, durable docs / task logs를 맞춘다.
- 화면 / 파일 범위: task docs, 필요 시 `docs/PROJECT_MAP.md`, `docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md`, root handoff logs.
- 완료 조건: compile / focused tests / Browser QA / diff check를 실행하고 남은 리스크를 기록한다.

## Non-goals

- 새 DB schema 추가 없음.
- provider를 yfinance 외 다른 realtime source로 바꾸지 않음.
- trade signal, validation gate, approval, order, broker/account sync, auto rebalance를 만들지 않음.
- registry / saved JSONL을 쓰거나 정리하지 않음.

## Verification Plan

- 서비스 read model TDD: `tests/test_service_contracts.py::FuturesMacroThermometerContractTests`
- Python compile: `app/services/futures_macro_thermometer.py`, `app/web/overview_dashboard.py`, `app/web/overview_ui_components.py`
- UI QA: Streamlit app + Browser screenshot
- Hygiene: `git diff --check`, `git status --short`
