# Phase 23 Test Checklist

## 목적

이 checklist는 `Phase 23`에서 quarterly / alternate cadence 기능이 제품 기능으로 읽히는지 확인하기 위한 문서다.

이번 checklist의 중심은 투자 성과가 좋은지 판단하는 것이 아니다.
quarterly 실행 경로가 사용자가 다시 찾고, 실행하고, 비교하고, 저장/재실행할 수 있는 형태인지 확인하는 것이다.

## 사용 방법

- 아래 항목은 사용자가 직접 `[ ]`를 `[x]`로 바꾸며 확인한다.
- 특별한 사유가 없으면, 모든 주요 체크 항목이 완료된 뒤 다음 major phase로 넘어간다.
- 일부 항목을 나중으로 미루면 그 이유를 closeout 또는 handoff 문서에 짧게 남긴다.

## 추천 실행 순서

1. Phase 23 plan과 first work-unit 문서에서 이번 phase의 범위가 이해되는지 확인한다.
2. `Backtest > Single Strategy`에서 quarterly strict family UI를 확인한다.
3. quarterly 전략을 compare / history / load/replay 흐름에서 다시 확인한다.
4. representative smoke report와 closeout 문서가 같은 결론을 말하는지 확인한다.

## 1. Phase 23 범위 이해 확인

- 확인 위치:
  - `.note/finance/phase23/PHASE23_QUARTERLY_AND_ALTERNATE_CADENCE_PRODUCTIONIZATION_PLAN.md`
  - `.note/finance/phase23/PHASE23_QUARTERLY_PRODUCTIONIZATION_FRAME_FIRST_WORK_UNIT.md`
- 체크 항목:
  - [x] Phase 23이 투자 분석이 아니라 quarterly / alternate cadence 제품화 단계라는 점이 이해되는지
  - [x] `prototype`, `research-only`, `productionization`, `cadence`의 뜻이 문서 안에서 어렵지 않게 읽히는지
  - [x] 현재 quarterly 기능에서 이미 되는 것과 아직 보강해야 할 것이 구분되어 있는지

## 2. quarterly single strategy UI 확인

- 확인 위치:
  - `Backtest > Single Strategy`
  - `Quality Snapshot (Strict Quarterly Prototype)`
  - `Value Snapshot (Strict Quarterly Prototype)`
  - `Quality + Value Snapshot (Strict Quarterly Prototype)`
- 체크 항목:
  - [x] quarterly 전략 이름과 설명이 현재 상태를 과장하지 않고 보여주는지
  - [x] 사용자가 어떤 cadence를 실행하는지 바로 알 수 있는지
  - [x] `Portfolio Handling & Defensive Rules` 안에서 `Weighting Contract`, `Rejected Slot Handling Contract`, `Risk-Off Contract`가 보이는지
  - [x] annual strict와 다른 입력 또는 제한이 있으면 화면에서 이유를 이해할 수 있는지
  - [ ] factor timing / PIT / coverage 관련 경고가 너무 기술적으로만 보이지 않는지

## 3. compare / history / load-replay 흐름 확인

- 확인 위치:
  - Compare 실행: `Backtest > Compare & Portfolio Builder`
  - compare history 확인: `Backtest > History > Run Kind Filter = strategy_compare > Selected History Run`
  - single history 확인: `Backtest > History > Run Kind Filter = single_strategy > Selected History Run`
  - saved portfolio 확인: `Backtest > Compare & Portfolio Builder > Saved Portfolios > Inspect Saved Portfolio`

용어 기준:

- `history run`: `Backtest > History`에 저장된 과거 실행 기록 1건이다.
- `saved compare context`: compare 실행 기록에 저장된 전략별 설정이다. `History > Saved Input & Context > Context`에서 본다.
- `saved portfolio context`: 저장 포트폴리오에 들어 있는 compare 설정과 weight 설정이다. `Saved Portfolios > Inspect Saved Portfolio > Compare Context`에서 본다.
- `quarterly portfolio handling contract`: quarterly 전략 박스 안의 `Portfolio Handling & Defensive Rules`에 있는 `Rejected Slot Handling`, `Weighting`, `Risk-Off / Defensive Tickers` 설정 묶음이다.
- `Load Into Form`: history 기록의 입력값만 `Single Strategy` form으로 다시 채우는 버튼이다. 누른 뒤에는 직접 다시 실행해야 최신 결과가 갱신된다.
- `Run Again`: history 기록의 payload를 즉시 다시 실행하는 버튼이다.
- `Replay Saved Portfolio`: `Saved Portfolios`에서 저장된 compare와 weighted portfolio를 한 번에 다시 실행하는 버튼이다. `Run Again`과 다른 기능이다.

- 체크 항목:
  - [x] quarterly 전략을 compare에 넣었을 때 strategy / period / key override가 자연스럽게 보이는지
  - [x] compare 화면에서 quarterly `Overlay`, `Portfolio Handling & Defensive Rules`가 하위 접기 그룹으로 보이고, 그 안에서 `Weighting`, `Rejected Slot Handling`, `Risk-Off` 값을 선택할 수 있는지
  - [ ] `Backtest > History`에서 quarterly compare 기록을 선택했을 때 `Saved Input & Context > Context`의 전략별 override 표에 `Rejected Slot Handling`, `Weighting`, `Risk-Off` 값이 남아 있는지
  - [ ] `Saved Portfolios > Inspect Saved Portfolio > Compare Context`에서 저장된 포트폴리오의 quarterly 전략 override에 `Rejected Slot Handling`, `Weighting`, `Risk-Off` 값이 남아 있는지
  - [ ] `Backtest > History`에서 single-strategy quarterly 기록을 선택했을 때 `strategy_key`나 전략 이름이 `Strict Quarterly Prototype`으로 보이고 annual처럼 보이지 않는지
  - [ ] `Load Into Form`을 눌렀을 때 `Single Strategy`로 이동하고, `Quality / Value / Quality + Value Variant`가 quarterly로 유지되는지
  - [ ] `Load Into Form` 후 `Portfolio Handling & Defensive Rules`의 `Rejected Slot Handling`, `Weighting`, `Risk-Off / Defensive Tickers` 값이 저장 기록과 동일하게 복원되는지
  - [ ] `Run Again`은 history 기록을 즉시 다시 실행하고 최신 single-strategy 결과로 이동하는 동작으로 이해되는지
  - [ ] `Load Into Form` 후 `Back To History`를 누르면 `History` panel로 돌아가는지
  - [ ] `Saved Portfolios > Replay Saved Portfolio`를 실행했을 때 `Compare Results`와 `Weighted Portfolio Result`가 다시 표시되고, quarterly contract 값이 오류 없이 유지되는지

## 4. representative validation 확인

- 확인 위치:
  - `.note/finance/backtest_reports/phase23/`
  - Phase 23 closeout 문서
  - `.note/finance/backtest_reports/phase23/PHASE23_QUARTERLY_CONTRACT_SMOKE_VALIDATION_FIRST_PASS.md`
- 체크 항목:
  - [ ] representative quarterly smoke run 결과가 문서화되어 있는지
  - [ ] 결과 해석이 투자 추천이 아니라 기능 검증으로 쓰였는지
  - [ ] smoke report에서 `Weighting`, `Rejected Slot Handling`, `Risk-Off`, `Defensive Tickers` meta가 보존된다고 설명하는지
  - [ ] third work-unit 문서에서 history / saved replay contract roundtrip이 코드 레벨로 확인되었다고 설명하는지
  - [ ] 실패하거나 보류한 항목이 있다면 다음 phase 또는 backlog로 명확히 남아 있는지

## 5. 문서와 closeout 확인

- 확인 문서:
  - `.note/finance/phase23/PHASE23_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/phase23/PHASE23_COMPLETION_SUMMARY.md`
  - `.note/finance/phase23/PHASE23_NEXT_PHASE_PREPARATION.md`
  - `.note/finance/MASTER_PHASE_ROADMAP.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`
- 체크 항목:
  - [ ] Phase 23 상태가 실제 구현/검수 상태와 맞는지
  - [ ] 새 문서가 index에서 바로 찾히는지
  - [ ] 다음 단계로 넘어가기 위한 설명이 충분한지

## 한 줄 판단 기준

Phase 23 checklist는 quarterly 성과가 좋은지보다,
quarterly / alternate cadence 기능이 제품 안에서 다시 찾고 재현할 수 있는 백테스트 기능이 되었는지를 확인한다.
