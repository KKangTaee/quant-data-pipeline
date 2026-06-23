# Futures Monitor Dedup UX V1 Plan

## 이걸 하는 이유?

`Workspace > Overview > Futures Monitor` V3는 한글화와 해석 순서를 개선했지만, 같은 상태 / 수치가 command center, Macro Context, Live Chart, warning, diagnostics에 반복되어 사용자가 같은 정보를 여러 번 읽게 된다.

이번 작업은 새 지표를 추가하지 않고, 기본 화면의 정보 소유권을 나눠 중복 노출을 줄인다.

## 전체 개발 흐름

### 1차: 기본 화면 정보 소유권 고정

- 목적: `freshness`, `top move`, `provider run`, `macro scenario`, `score`, `historical validation`이 어느 섹션에서만 기본 노출되는지 정한다.
- 파일 범위: `tests/test_service_contracts.py`, `app/web/overview_dashboard.py`.
- 완료 조건: UI helper contract가 command center / live chart / macro context의 기본 요약 역할을 분리한다.

### 2차: 상단 command center 축소

- 목적: 상단은 선택 범위, 상태, 다음 행동만 보여주고 rows / latest candle / full detail은 낮춘다.
- 파일 범위: `app/web/overview_dashboard.py`.
- 완료 조건: 상단이 `개장 전 핵심 · 6개`, `오래됨 · 갱신 필요`, `수동 확인` 같은 의사결정용 summary만 보여준다.

### 3차: Macro Context 중복 통합

- 목적: `시나리오` 카드와 hero의 중복을 줄이고, score / confidence / validation은 보조 근거로 정리한다.
- 파일 범위: `app/web/overview_dashboard.py`, 필요 시 CSS.
- 완료 조건: Macro 기본 화면은 `오늘 기준 해석 -> 근거 강도 / 과거 점검 -> 최근 1주 흐름 -> score chips` 순서로 읽힌다.

### 4차: Live Chart 상태 카드 제거 / 흡수

- 목적: Live Chart 위 4개 상태 카드를 제거하거나 한 줄 상태로 흡수해 command center와 겹치지 않게 한다.
- 파일 범위: `app/web/overview_dashboard.py`, `app/web/overview_ui_components.py`.
- 완료 조건: live chart section은 chart와 symbol-level state만 담당하고, provider run details는 diagnostics에만 남는다.

### 5차: QA / 문서 / 커밋

- 목적: compile, focused tests, Browser QA로 기본 화면 반복 노출이 줄었는지 확인하고 task / root logs를 정리한다.
- 파일 범위: task docs, 필요 시 runbook/root logs.
- 완료 조건: generated QA screenshot은 커밋하지 않고, 코드 / docs / task record만 commit한다.

## Non-goals

- 새 DB schema, provider, loader, registry / saved JSONL write 없음.
- 새 macro 계산, 예측 score, trading signal, validation gate, monitoring signal 없음.
- diagnostics를 삭제하지 않는다. 기본 화면에서 낮출 뿐이다.

## Verification Plan

- RED/GREEN: `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.<new-tests>`
- Focused: `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests tests.test_service_contracts.FuturesMacroThermometerContractTests tests.test_service_contracts.FuturesMarketMonitoringContractTests`
- Compile: `uv run python -m py_compile app/web/overview_dashboard.py tests/test_service_contracts.py`
- Browser QA: Streamlit app + Futures Monitor screenshot
- Hygiene: `git diff --check`, `git status --short`
