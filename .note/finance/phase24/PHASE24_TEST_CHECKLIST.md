# Phase 24 Test Checklist

## 목적

이 checklist는 `Phase 24`에서 신규 전략 확장 경로가 제품 기능으로 읽히는지 확인하기 위한 문서다.

이번 checklist의 중심은 새 전략의 투자 성과가 좋은지 판단하는 것이 아니다.
research note에서 온 신규 전략이 single 실행, compare, history, saved replay 흐름에서 다시 찾고 재현될 수 있는지 확인하는 것이다.

## 사용 방법

- 아래 항목은 사용자가 직접 `[ ]`를 `[x]`로 바꾸며 확인한다.
- 특별한 사유가 없으면, 모든 주요 체크 항목이 완료된 뒤 다음 major phase로 넘어간다.
- 일부 항목을 나중으로 미루면 그 이유를 closeout 또는 handoff 문서에 짧게 남긴다.
- 별도 `용어 기준` 섹션을 만들지 않고, 각 체크 항목 안에 확인 위치를 직접 적는다.
- 현재 `Global Relative Strength`는 core/runtime smoke와
  UI / compare / history / saved replay 연결까지 완료된 상태다.
- 아래 항목은 실제 Streamlit 화면에서 확인한다.

## 추천 실행 순서

1. Phase 24 plan과 first work-unit 문서에서 이번 phase의 범위가 이해되는지 확인한다.
2. 첫 신규 전략이 왜 선택되었는지 확인한다.
3. `Backtest > Single Strategy`에서 신규 전략 실행 UI를 확인한다.
4. compare / history / saved replay 흐름에서 신규 전략 설정이 유지되는지 확인한다.
5. representative smoke report와 closeout 문서가 같은 결론을 말하는지 확인한다.

## 1. Phase 24 범위 이해 확인

- 확인 위치:
  - `.note/finance/phase24/PHASE24_NEW_STRATEGY_EXPANSION_AND_RESEARCH_IMPLEMENTATION_BRIDGE_PLAN.md`
  - `.note/finance/phase24/PHASE24_RESEARCH_TO_IMPLEMENTATION_BRIDGE_FIRST_WORK_UNIT.md`
  - `.note/finance/phase24/PHASE24_UI_AND_REPLAY_INTEGRATION_SECOND_WORK_UNIT.md`
- 체크 항목:
  - [ ] `Phase 24 plan`에서 이번 phase가 투자 분석이 아니라 신규 전략 구현 경로를 만드는 단계라는 점이 이해되는지
  - [ ] `Phase 24 first work-unit`에서 첫 구현 후보를 고른 기준이 이해되는지
  - [ ] `Phase 24 first work-unit`에서 지금 구현하지 않는 전략들이 왜 제외되었는지 이해되는지
  - [ ] `Phase 24 second work-unit`에서 신규 전략을 UI / compare / history / saved replay에 연결한 이유가 이해되는지

## 2. 신규 전략 single strategy UI 확인

- 확인 위치:
  - `Backtest > Single Strategy`
  - `Strategy = Global Relative Strength`
- 체크 항목:
  - [x] `Backtest > Single Strategy > Strategy = Global Relative Strength`에서 전략 이름과 설명이 research note와 자연스럽게 연결되는지
  - [x] 같은 화면에서 `Universe Mode`, `Preset` 또는 `Tickers` 입력이 보이는지
  - [x] `Advanced Inputs` 안에서 `Cash / Defensive Ticker`, `Top Assets`, `Signal Interval`, `Score Horizons`, `Trend Filter Window`가 보이는지
  - [x] `Advanced Inputs > Real-Money Contract`에서 ETF 가격 / 거래비용 / benchmark / ETF operability 기준을 확인할 수 있는지
  - [x] `Run Global Relative Strength Backtest`를 실행했을 때 결과가 오류 없이 표시되는지
  - [ ] 기본 preset 실행 중 특정 ETF의 가격 이력이 부족하면 결과 warning 또는 `Meta`의 `excluded_tickers`에 해당 티커가 표시되고, 남은 ETF 묶음으로 실행이 계속되는지
  - [x] 실행 결과의 `Meta` 또는 runtime metadata에서 `strategy_key = global_relative_strength`, `cash_ticker = BIL`이 보이는지

## 3. compare / history / saved replay 흐름 확인

- 확인 위치:
  - `Backtest > Compare & Portfolio Builder`
  - `Backtest > History`
  - `Backtest > Compare & Portfolio Builder > Saved Portfolios`
- 체크 항목:
  - [ ] `Backtest > Compare & Portfolio Builder > Strategies`에서 첫 신규 전략을 compare에 넣을 수 있는지
  - [ ] `Strategy-Specific Advanced Inputs > Global Relative Strength` box에서 universe, cash ticker, top assets, signal interval, score horizons, trend filter, real-money contract가 보이는지
  - [ ] `Run Compare`를 실행했을 때 `Global Relative Strength` 결과가 다른 전략 결과와 함께 표시되는지
  - [ ] `Backtest > History > Run Kind Filter = single_strategy > Selected History Run`에서 신규 전략 실행 기록이 `Global Relative Strength`로 보이는지
  - [ ] `Selected History Run > Load Into Form`을 눌렀을 때 `Single Strategy` 화면의 `Strategy = Global Relative Strength`로 이동하고, universe / cash ticker / score horizon / trend filter 값이 복원되는지
  - [ ] `Selected History Run > Run Again`을 눌렀을 때 신규 전략이 즉시 다시 실행되는지
  - [ ] `Backtest > Compare & Portfolio Builder > Save This Weighted Portfolio`에서 신규 전략이 포함된 compare 결과를 저장할 수 있는지
  - [ ] `Backtest > Compare & Portfolio Builder > Saved Portfolios > Replay Saved Portfolio`에서 신규 전략이 포함된 saved portfolio가 오류 없이 replay되는지

## 4. representative validation 확인

- 확인 위치:
  - `.note/finance/backtest_reports/phase24/`
  - `.note/finance/phase24/PHASE24_COMPLETION_SUMMARY.md`
- 체크 항목:
  - [ ] `.note/finance/backtest_reports/phase24/PHASE24_GLOBAL_RELATIVE_STRENGTH_CORE_RUNTIME_SMOKE_VALIDATION.md`에서 대표 smoke run 결과가 문서화되어 있는지
  - [ ] `.note/finance/backtest_reports/phase24/PHASE24_GLOBAL_RELATIVE_STRENGTH_UI_REPLAY_SMOKE_VALIDATION.md`에서 UI / compare / history / replay 연결 검증이 문서화되어 있는지
  - [ ] smoke report가 투자 추천이 아니라 기능 검증으로 쓰였는지
  - [ ] 실패하거나 보류한 항목이 있다면 다음 작업 또는 backlog로 명확히 남아 있는지

## 5. 문서와 closeout 확인

- 확인 문서:
  - `.note/finance/phase24/PHASE24_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/phase24/PHASE24_COMPLETION_SUMMARY.md`
  - `.note/finance/phase24/PHASE24_NEXT_PHASE_PREPARATION.md`
  - `.note/finance/MASTER_PHASE_ROADMAP.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`
- 체크 항목:
  - [ ] Phase 24 상태가 실제 구현/검수 상태와 맞는지
  - [ ] 새 문서가 index에서 바로 찾히는지
  - [ ] 다음 단계로 넘어가기 위한 설명이 충분한지

## 한 줄 판단 기준

Phase 24 checklist는 새 전략의 성과가 좋은지보다,
새 전략을 제품 안에 반복 가능한 백테스트 기능으로 추가할 수 있는지를 확인한다.
