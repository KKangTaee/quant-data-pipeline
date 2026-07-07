# Backtest Post-Run Factor Readiness V1

## 이걸 하는 이유?

Quality / Value strict 전략의 사전 Factor Readiness는 현재 preset 후보군을 기준으로 읽기 때문에, PIT Monthly universe처럼 실행 기간별 구성 종목이 달라지는 흐름에서는 실제 백테스트에 사용될 데이터 문제를 정확히 말하기 어렵다.

이번 작업은 `Universe 기준`을 먼저 고르게 하고, Factor Readiness의 주 판단을 실행 전 전체 후보군 검증이 아니라 실행 후 실제 사용 기간 / 티커 기반 점검으로 옮긴다.

## 차수

1. Universe 기준을 Preset 바로 아래로 올리고, 실행 전 readiness는 Preview로 낮춘다.
2. strict runtime 결과 meta에서 실제 사용 데이터 기준 readiness를 만들 수 있는 helper를 추가한다.
3. 결과 화면에 post-run Factor Readiness panel을 연결하고, 데이터 보강 action을 실제 문제 티커 기준으로 실행한다.
4. QA / 문서 동기화 / commit.

## 범위

- `app/web/backtest_single_forms/strict_factor.py`
- `app/web/backtest_common.py`
- `app/web/backtest_result_display.py`
- `tests/test_service_contracts.py`
- Backtest UI flow 문서 / root handoff log

## 완료 조건

- Quality / Value strict form에서 `Universe 기준`이 Preset 하단에 먼저 보인다.
- 실행 전 Factor Readiness는 pre-run preview로 표시되어 “실제 실행 가능 coverage 보장”처럼 보이지 않는다.
- 실행 후 결과 화면은 실제 runtime meta를 기준으로 가격 / statement 문제와 티커를 정리한다.
- 기존 Factor Readiness React UI를 재사용하거나 같은 contract에 맞는 화면으로 표시한다.
- focused unittest, py_compile, 가능하면 Browser QA를 수행한다.
