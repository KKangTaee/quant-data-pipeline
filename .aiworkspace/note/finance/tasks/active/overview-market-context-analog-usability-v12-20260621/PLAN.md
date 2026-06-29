# Overview Market Context Analog Usability V12 Plan

Status: Active
Date: 2026-06-21

## Why

`Workspace > Overview > Market Context`의 `참고: 과거 유사 맥락`은 사용자가 원하는 분석 값은 갖췄지만, 실제 사용 흐름에서는 세 가지 문제가 남았다.

1. 선택 기준일보다 `실제 계산 기준일`이 오래된 경우에도 현재 `필요 자료 보강`으로 해결되는지 명확하지 않고, 실제로 stale common daily price basis는 보강 액션으로 연결되지 않는다.
2. 기준 / 조건 / 표본 설명이 wide bar, method grid, summary strip에서 반복되어 완성된 분석 화면이 아니라 prototype payload처럼 보인다.
3. 핵심 / 보조 자산 통계가 표 중심으로만 보여서 사용자가 먼저 읽어야 할 자산별 5D / 20D / 60D 결과와 시장 배경 차이를 빠르게 파악하기 어렵다.

## Scope

### 1차: 실제 계산 기준일 보강 액션

- `as_of_alignment.is_aligned == False`이고 common price basis가 요청 기준일보다 이른 경우, 제한 symbols를 대상으로 `overview_historical_analog_ohlcv` repair action을 만든다.
- 기존 부족 row coverage repair action은 유지한다.
- UI의 repair copy는 `부족 가격 이력`과 `가격 기준 최신화`를 구분한다.

### 2차: 기준 / 조건 / 표본 중복 제거

- `요청 기준일`, `실제 계산 기준일`, `기준 섹터`, `ETF proxy`, `패턴 기간`, `표본 / 자료 기간`을 모두 같은 무게로 나열하지 않는다.
- 핵심 basis는 `계산 기준`, `기준 자산`, `유사 조건`, `표본`으로 압축한다.
- replay / as-of boundary 같은 개발자 성격의 경계 설명은 접힌 상세로 내린다.

### 3차: 결과 해석 UI 개선

- 핵심 자산은 표보다 먼저 5D / 20D / 60D 비교 matrix로 보여준다.
- 보조 자산은 상세 표가 아니라 배경 요약으로 먼저 보여준다.
- 기존 full statistic table은 `상세 통계` disclosure에 남긴다.

## Non-Goals

- 새 provider / DB schema / loader 경로 추가 없음.
- UI render 중 직접 provider / FRED / yfinance fetch 없음.
- FRED / events / sentiment hard conditioning 추가 없음.
- registry / saved JSONL write 없음.
- Backtest / Practical Validation / Final Review / Operations core logic 연결 없음.
- 예측 / 추천 / 매수 / 매도 / 신호 / PASS / BLOCKER 의미 추가 없음.

## Verification

- `uv run python -m py_compile app/services/overview_market_context_analog.py app/web/overview_ui_components.py app/web/overview_dashboard.py`
- `uv run --with pytest python -m pytest tests/test_service_contracts.py -q`
- `uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true`
- Browser QA: `Workspace > Overview > Market Context`, latest / selected as-of, 5D / 20D / monthly pattern window, repair action, matrix, collapsed detail table.

