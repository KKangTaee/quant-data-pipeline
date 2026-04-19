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
  - [ ] quarterly 전략 이름과 설명이 현재 상태를 과장하지 않고 보여주는지
  - [ ] 사용자가 어떤 cadence를 실행하는지 바로 알 수 있는지
  - [ ] `Portfolio Handling & Defensive Rules` 안에서 `Weighting Contract`, `Rejected Slot Handling Contract`, `Risk-Off Contract`가 보이는지
  - [ ] quarterly 화면 상단의 `Data Requirements`에서 quarterly가 아직 real-money promotion 대상이 아니라 제품화 검증 중인 경로라는 점이 이해되는지
  - [ ] quarterly `Advanced Inputs`에는 현재 `Overlay`와 `Portfolio Handling & Defensive Rules`가 있고, annual strict의 `Real-Money Contract` / `Guardrails`는 아직 붙지 않았다는 점이 자연스럽게 읽히는지
  - [ ] `Statement Shadow Coverage Preview`가 universe 선택 아래에 보이고, quarterly statement coverage가 부족하면 일부 종목/초기 구간이 제외될 수 있다는 뜻으로 이해되는지
  - [ ] `Advanced Inputs > Universe Contract`에서 `Historical Dynamic PIT Universe` 설명을 읽었을 때, 리밸런싱 날짜마다 당시 사용 가능한 모집군을 다시 계산한다는 뜻이 이해되는지

## 3. compare / history / load-replay 흐름 확인

- 확인 위치:
  - `Backtest > Compare & Portfolio Builder`
  - `Backtest > History`
  - saved portfolio 또는 replay 관련 화면
- 체크 항목:
  - [ ] `Compare Period & Shared Inputs`에서 `Start Date`, `End Date`, `Timeframe`, `Option`이 한 곳에 모여 있어 공용 실행 입력으로 이해되는지
  - [ ] `Strategy Variants`라는 별도 상단 섹션이 보이지 않고, `Quality`, `Value`, `Quality + Value` variant 선택이 각 전략 박스 안에 들어가 있는지
  - [ ] `Strategy-Specific Advanced Inputs` 아래에서 각 전략이 접기/펼치기 expander가 아니라 border box로 구분되어 보이는지
  - [ ] 각 전략 박스 안에서 Annual / Quarterly variant를 바꾸면 별도 버튼 없이 같은 박스 안의 세부 입력이 즉시 바뀌는지
  - [ ] 전략 박스 안의 `Overlay`, `Portfolio Handling & Defensive Rules`, `Real-Money Contract`, `Guardrails` 같은 하위 그룹은 기존처럼 접기/펼치기로 유지되는지
  - [ ] quarterly 전략을 compare에 넣었을 때 strategy / period / key override가 자연스럽게 보이는지
  - [ ] compare 화면에서도 quarterly `Weighting`, `Rejected Slot Handling`, `Risk-Off` 값이 보이고 선택 가능한지
  - [ ] quarterly variant에서는 `Overlay`, `Portfolio Handling & Defensive Rules` 중심으로 보이고, 아직 annual-only인 `Real-Money Contract` / `Guardrails`가 억지로 표시되지 않는지
  - [ ] saved compare / saved portfolio context에서 quarterly `Rejected Slot Handling`과 `Weighting` 값이 빠지지 않는지
  - [ ] history run을 다시 열었을 때 quarterly 설정이 사라지거나 annual처럼 오해되지 않는지
  - [ ] load-into-form 또는 rerun 흐름에서 quarterly cadence가 유지되는지
  - [ ] load-into-form 후 quarterly portfolio handling contract 값이 form에 복원되는지
  - [ ] saved replay를 실행했을 때 quarterly contract 값이 유지되고, 오류 없이 compare / weighted result로 이어지는지

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
