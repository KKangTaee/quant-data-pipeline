# Phase 24 Completion Summary

## 목적

이 문서는 `Phase 24 New Strategy Expansion And Research Implementation Bridge`를 closeout 기준으로 정리하기 위한 문서다.

현재는 사용자 manual QA까지 끝난 최종 closeout 문서다.
`PHASE24_TEST_CHECKLIST.md`의 주요 항목이 모두 `[x]` 처리되었으므로
Phase 24는 `phase complete / manual_validation_completed`로 닫는다.

## 현재 상태

- `phase complete / manual_validation_completed`

Phase 24는 기능 구현과 사용자 QA 기준을 모두 통과했다.
첫 신규 전략 후보 선정, core/runtime smoke validation,
UI / compare / history / saved replay 연결, QA 중 발견된 데이터 품질 경고 처리까지 완료했다.

## 이번 phase에서 완료해야 할 것

### 1. research-to-implementation bridge 정의

- `quant-research` 전략 문서를 finance 구현 후보로 고르는 기준을 만든다.

쉽게 말하면:

- 연구 문서가 많아도, 지금 codebase에 바로 붙일 수 있는 전략과 나중에 해야 하는 전략을 나눈다.

### 2. first new family implementation

- 첫 신규 전략 family를 strategy / sample / runtime / UI까지 최소 제품 경로에 붙인다.

쉽게 말하면:

- 새 전략 하나를 실제로 실행 가능한 기능으로 넣어 본다.

### 3. representative validation과 checklist handoff

- 대표 DB-backed smoke run과 manual checklist를 남긴다.

쉽게 말하면:

- 이 전략이 좋은 투자 전략인지가 아니라,
  제품 안에서 다시 찾고 재실행할 수 있는지 확인한다.

## 지금까지 완료된 것

- 첫 구현 후보를 `Global Relative Strength`로 선정했다.
- 선정 이유를 `PHASE24_RESEARCH_TO_IMPLEMENTATION_BRIDGE_FIRST_WORK_UNIT.md`에 기록했다.
- `finance.strategy`에 core simulation과 strategy class를 추가했다.
- `finance.sample`에 DB-backed helper와 기본 universe / score / trend filter 설정을 추가했다.
- `app.web.runtime.backtest`에 DB-backed runtime wrapper를 추가했다.
- compile / import / synthetic smoke / DB-backed smoke validation을 통과했다.
- smoke 결과를 `.note/finance/backtest_reports/phase24/PHASE24_GLOBAL_RELATIVE_STRENGTH_CORE_RUNTIME_SMOKE_VALIDATION.md`에 기록했다.
- `Backtest > Single Strategy`에서 `Global Relative Strength`를 선택하고 실행할 수 있게 했다.
- `Backtest > Compare & Portfolio Builder`에서 같은 전략을 compare에 넣을 수 있게 했다.
- history record와 payload에 `cash_ticker`, `research_source`, cadence 값이 보존되도록 했다.
- `Load Into Form`, `Run Again`, saved portfolio replay에서 새 전략 설정이 유지되도록 연결했다.
- UI / replay smoke 결과를 `.note/finance/backtest_reports/phase24/PHASE24_GLOBAL_RELATIVE_STRENGTH_UI_REPLAY_SMOKE_VALIDATION.md`에 기록했다.
- future 신규 전략 작업에서도 web product path를 빠뜨리지 않도록
  `finance-strategy-implementation` skill guidance를 보강했다.
- 사용자 QA 중 `Global Relative Strength` 기본 preset에서 `EEM` 이력 부족과
  `IWM` 결측 가격 행이 발견되었다.
- `EEM`처럼 warmup 이후 비는 risky ticker는 실행을 중단하지 않고
  `excluded_tickers`와 한국어 주의사항에 남긴다.
- `IWM`처럼 원본 가격 행에 결측이 있는 경우는 조용히 보정하지 않고,
  공통 리밸런싱 날짜가 보수적으로 제한되게 둔다.
- 결측 가격 행은 `malformed_price_rows` metadata와 결과 주의사항에 노출한다.
- `Real-Money 검증 신호`와 `Pre-Live 운영 점검`이 섞여 보이지 않도록
  Guides / Glossary / Phase 25 handoff 문서를 정리했다.
- 사용자가 `PHASE24_TEST_CHECKLIST.md`의 주요 항목을 모두 확인했다.

## 아직 남아 있는 것

- Phase 25에서 다룰 Pre-Live 운영 점검 체계 설계
- 추가 신규 전략 family 구현 후보 검토
- quarterly real-money / guardrail parity는 별도 후속 phase 또는 backlog에서 판단

## closeout 판단

Phase 24는 `phase complete / manual_validation_completed` 상태로 닫는다.

쉽게 말하면:

- 새 전략은 이제 화면에서 고르고 다시 열 수 있다.
- 데이터 품질 문제가 있으면 결과를 억지로 늘리지 않고 경고로 드러낸다.
- 사용자가 checklist QA를 완료했으므로 Phase 25로 넘어갈 수 있다.
