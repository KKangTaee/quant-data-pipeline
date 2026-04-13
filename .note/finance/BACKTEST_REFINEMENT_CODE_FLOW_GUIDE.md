# Backtest Refinement Code Flow Guide

## 목적

이 문서는 현재 프로젝트에서
백테스트 실행, 후보 refinement, 결과 문서화가
**어떤 파일 흐름으로 이어지는지**를 빠르게 다시 잡기 위한 안내 문서다.

새로운 탐색을 다시 시작할 때:

- 어디서 UI가 시작되는지
- 어디서 runtime이 실행되는지
- 어디서 real-money 해석이 붙는지
- 어떤 문서를 같이 갱신해야 하는지

를 한 번에 보게 하는 것이 목적이다.

## 1. UI 진입점

- [streamlit_app.py](/Users/taeho/Project/quant-data-pipeline/app/web/streamlit_app.py)
  - Finance Console 메인 entry
  - `Backtest`, `Ops Review`, `Guides`, `Glossary` 같은 상위 navigation을 연결한다
- [backtest.py](/Users/taeho/Project/quant-data-pipeline/app/web/pages/backtest.py)
  - 실제 전략 입력 form과 결과 화면을 담당한다
  - strict annual / ETF family별 form 렌더링
  - `Real-Money`, `History`, `Compare`, `Execution Context` 같은 결과 surface 렌더링

## 2. runtime 실행층

- [backtest.py](/Users/taeho/Project/quant-data-pipeline/app/web/runtime/backtest.py)
  - UI payload를 실제 backtest 실행 함수로 바꾸는 runtime adapter다
  - 여기서:
    - date validation
    - DB 로딩
    - strategy family별 `run_*_backtest_from_db(...)`
    - `Real-Money Contract`
    - `promotion / shortlist / deployment`
    를 만든다

strict annual family 핵심 함수:

- `run_quality_snapshot_strict_annual_backtest_from_db(...)`
- `run_value_snapshot_strict_annual_backtest_from_db(...)`
- `run_quality_value_snapshot_strict_annual_backtest_from_db(...)`

real-money 해석 핵심 구간:

- `_build_real_money_validation_surface(...)`
- `_apply_real_money_hardening(...)`
- `build_backtest_result_bundle(...)`

## 3. finance 패키지 실행층

- [engine.py](/Users/taeho/Project/quant-data-pipeline/finance/engine.py)
  - backtest orchestration
- [strategy.py](/Users/taeho/Project/quant-data-pipeline/finance/strategy.py)
  - 실제 전략 시뮬레이션 로직
  - ETF 전략 class와 strict annual transform 결과를 받는 strategy behavior가 여기에 있다
- [performance.py](/Users/taeho/Project/quant-data-pipeline/finance/performance.py)
  - `CAGR`, `Sharpe`, `MDD` 등 성과 계산
- [display.py](/Users/taeho/Project/quant-data-pipeline/finance/display.py)
  - 결과를 표면에 맞게 보여주기 위한 가공

## 4. strict annual refinement를 다시 할 때 보는 순서

1. 전략 허브를 먼저 연다
   - `Value`, `Quality`, `Quality + Value`
2. current best practical point를 anchor로 잡는다
3. bounded search를 정한다
   - `Top N`
   - one-factor addition / replacement
   - benchmark / overlay
4. runtime 함수로 representative rerun을 확인한다
5. exact hit인지, lower-MDD weaker-gate near-miss인지 구분한다
6. 문서를 동기화한다

## 5. 문서 흐름

전략 refinement 결과를 남길 때는 보통 아래 순서로 간다.

1. active phase 문서
   - 예: [PHASE17_CURRENT_CHAPTER_TODO.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase17/PHASE17_CURRENT_CHAPTER_TODO.md)
2. phase raw report
   - 예: `PHASE16_*_FIRST_PASS.md`
3. strategy hub
   - 예: [VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL.md)
4. one-pager
   - strongest / downside-improved / replacement current candidate
5. strategy backtest log
   - 실행 기록 누적
6. current candidate summary
   - 현재 추천 anchor 한 장 요약
7. root concise logs
   - [WORK_PROGRESS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/WORK_PROGRESS.md)
   - [QUESTION_AND_ANALYSIS_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/QUESTION_AND_ANALYSIS_LOG.md)

## 6. compare / weighted / saved portfolio 해석

- `Compare`는 여러 전략의 개별 후보를 나란히 보는 연구용 표면이다.
- `Weighted Portfolio`는 compare 결과를 월별 composite로 합치는 포트폴리오 합성 표면이다.
- `Saved Portfolio`는 compare + weights + date policy를 저장해 rerun할 수 있게 만든 재현용 연구 아티팩트다.
- 이 셋은 실전 후보의 `promotion / shortlist / deployment` semantics를 새로 부여하는 계층이 아니라,
  이미 선택된 후보를 더 잘 비교하고 묶는 operator bridge로 읽는 것이 맞다.

## 7. 지금 다시 볼 때 가장 중요한 문서

- [CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md)
  - 지금 어떤 후보를 기준점으로 삼아야 하는지
- [PHASE17_CURRENT_CHAPTER_TODO.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase17/PHASE17_CURRENT_CHAPTER_TODO.md)
  - 지금 active structural refinement가 어디까지 왔는지
- [VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL.md)
- [QUALITY_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL.md)
- [QUALITY_VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL.md)

## 8. Phase 17에서 보는 구조 레버

Phase 17부터는 bounded `Top N` / one-factor tweak을 반복하기보다
아래 구조 레버를 먼저 본다.

- partial overlay rejection을
  `survivor reweighting`으로 둘지
  `cash retention`으로 바꿀지
- risk-off를
  `cash only`로 둘지
  defensive sleeve로 바꿀지
- equal-weight top-N을
  concentration-aware weighting으로 바꿀지

그리고 `Compare / Weighted Portfolio / Saved Portfolio`는
즉시 새 `promotion / shortlist / deployment`를 만드는 계층이 아니라,
first slice가 이미 구현된 레버는 `partial cash retention`이고,
다음 active question은 이것이 strongest/current anchor에서 실제로 same-gate lower-MDD rescue로 이어지는지 representative rerun으로 다시 확인하는 것이다.
이미 살아 있는 후보를 비교하고 묶는 operator bridge로 읽는다.

## 한 줄 요약

이 프로젝트의 backtest refinement 흐름은:

- `streamlit_app.py`
- `pages/backtest.py`
- `runtime/backtest.py`
- `finance/engine.py` / `finance/strategy.py`
- 결과 문서 5종

순서로 이어진다고 이해하면 가장 빠르다.
