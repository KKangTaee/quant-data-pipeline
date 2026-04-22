# Phase 28 Test Checklist

## 목적

이 checklist는 Phase 28에서 추가한 `Strategy Capability Snapshot`이
사용자가 전략 family별 차이를 이해하는 데 도움이 되는지 확인하기 위한 문서다.

현재는 Phase 28 implementation complete 상태의 QA checklist다.
이 문서의 주요 항목을 확인한 뒤 Phase 28 manual QA 완료 여부를 판단한다.

## 사용 방법

- 아래 항목은 사용자가 직접 `[ ]`를 `[x]`로 바꾸며 확인한다.
- 특별한 사유가 없으면, 모든 주요 체크 항목이 완료된 뒤 다음 major phase로 넘어간다.
- checklist에는 별도 `용어 기준` 섹션을 만들지 않는다.
- 용어 설명이 필요하면 각 체크 항목 안에 `어디서 무엇을 어떻게 확인하는지`를 직접 적는다.

## 1. Single Strategy capability snapshot 확인

- 확인 위치:
  - `Backtest > Single Strategy`
- 체크 항목:
  - [ ] `Strategy`를 `Global Relative Strength`로 선택했을 때 `Strategy Capability Snapshot` 접힘 영역이 보이는지
  - [ ] snapshot 안에서 GRS가 `price-only ETF relative strength family`로 설명되는지
  - [ ] `Strategy`를 `Quality`, `Value`, `Quality + Value` 중 하나로 선택한 뒤 `Variant`를 `Strict Annual`로 두면 annual strict 설명이 보이는지
  - [ ] `Variant`를 `Strict Quarterly Prototype`으로 바꾸면 quarterly prototype 설명으로 바뀌는지
  - [ ] annual strict와 quarterly prototype의 Real-Money / Guardrail 차이가 읽히는지

## 2. Compare strategy box capability snapshot 확인

- 확인 위치:
  - `Backtest > Compare & Portfolio Builder > Strategies`
- 체크 항목:
  - [ ] `Quality`, `Value`, `Quality + Value`, `Global Relative Strength`를 선택했을 때 각 전략 박스 안에 `Strategy Capability Snapshot`이 보이는지
  - [ ] compare 안에서 `Quality Variant`, `Value Variant`, `Quality + Value Variant`를 바꾸면 snapshot 설명이 해당 variant 기준으로 읽히는지
  - [ ] `Equal Weight`, `GTAA`, `Risk Parity Trend`, `Dual Momentum`도 각각 지원 범위가 간단히 설명되는지
  - [ ] snapshot 표가 너무 길거나 방해되지 않고, 필요할 때 접어서 확인할 수 있는지

## 3. History replay / load parity 확인

- 확인 위치:
  - `Backtest > History`
  - 저장 기록 1개 선택
  - `Selected History Run` 아래의 `History Replay / Load Parity Snapshot`
- 체크 항목:
  - [ ] strict annual history record를 선택했을 때 `전략과 실행 기간`, `Universe / Ticker`, `Statement cadence / factor`, `Portfolio Handling`, `Real-Money / Guardrail` 행이 보이는지
  - [ ] strict quarterly prototype history record를 선택했을 때 quarterly가 annual strict와 같은 Real-Money / Guardrail 완성 상태로 보이지 않는지
  - [ ] `Global Relative Strength` history record를 선택했을 때 score, cash, trend, ETF real-money 입력이 별도 행으로 보이는지
  - [ ] `저장 상태` 열의 `저장됨`, `누락 가능`, `없음 또는 미사용`, `prototype 범위` 표현이 이해되는지
  - [ ] `Load Into Form` 또는 `Run Again`을 누르기 전에 어떤 값이 복원될지 대략 판단할 수 있는지

## 4. History record 추가 보존값 확인

- 확인 위치:
  - `Backtest > History > Selected History Run > Saved Input & Context`
  - `Backtest > History > Selected History Run > Raw Record`
- 체크 항목:
  - [ ] 새로 실행한 history record에 `actual_result_start`, `actual_result_end`, `result_rows`가 보이는지
  - [ ] price freshness가 있는 전략에서는 `price_freshness` 또는 관련 상태가 history record에서 확인되는지
  - [ ] strict annual guardrail 설정을 사용한 record에서 `guardrail_reference_ticker`가 사라지지 않는지
  - [ ] GRS처럼 excluded ticker나 malformed price row가 있을 수 있는 전략에서 해당 정보가 history record에 남는지

## 5. Saved Portfolio replay / load parity 확인

- 확인 위치:
  - `Backtest > Compare & Portfolio Builder`
  - `Saved Portfolios`
  - 저장 포트폴리오 1개 선택
  - `Saved Portfolio Replay / Load Parity Snapshot`
- 체크 항목:
  - [ ] 저장 포트폴리오를 선택했을 때 `Saved Portfolio Replay / Load Parity Snapshot`이 보이는지
  - [ ] `Compare 공용 입력`, `전략 목록`, `Weight / Date Alignment`, `Strategy Override Map` 행이 보이는지
  - [ ] 전략별 행에서 annual strict / quarterly prototype / GRS / GTAA 등의 핵심 override가 저장되어 있는지 읽을 수 있는지
  - [ ] `Strategy Override Summary`를 열었을 때 strategy별 variant, top/interval, universe, cadence, overlay/handling, benchmark/guardrail 요약이 보이는지
  - [ ] `Load Saved Setup Into Compare`를 누르기 전에 어떤 값이 다시 채워질지 대략 판단할 수 있는지
  - [ ] `Replay Saved Portfolio`가 저장된 전략 목록과 weight/date alignment를 기준으로 재실행되는 흐름으로 이해되는지

## 6. Compare / weighted Data Trust 확인

- 확인 위치:
  - `Backtest > Compare & Portfolio Builder`
  - 전략 2개 이상 선택 후 `Run Strategy Comparison`
  - `Strategy Comparison > Data Trust`
  - `Weighted Portfolio Result > Component Data Trust`
  - `Backtest > History > Selected History Run > Saved Input & Context`
- 체크 항목:
  - [ ] compare 결과에 `Data Trust` 탭이 보이는지
  - [ ] `Compare Data Trust Snapshot`에서 strategy별 `Requested End`, `Actual Result End`, `Result Rows`가 보이는지
  - [ ] price freshness가 있는 전략은 `Common Latest Price`, `Newest Latest Price`, `Latest-Date Spread`가 보이는지
  - [ ] excluded ticker 또는 malformed row가 있는 경우 `Data Quality Details Across Strategies`에서 세부 정보가 보이는지
  - [ ] weighted portfolio 결과에 `Component Data Trust` 탭이 보이는지
  - [ ] saved portfolio replay 후 History record에서 component별 data trust rows가 다시 보이는지
  - [ ] 이 표가 성과 비교표가 아니라 데이터 조건 확인표라는 점이 이해되는지

## 7. Real-Money / Guardrail parity 확인

- 확인 위치:
  - `Backtest > Compare & Portfolio Builder`
  - 전략 2개 이상 선택 후 `Run Strategy Comparison`
  - `Strategy Comparison > Real-Money / Guardrail`
  - `Backtest > History > Selected History Run > History Real-Money / Guardrail Scope`
  - `Backtest > Compare & Portfolio Builder > Saved Portfolios > Saved Portfolio Real-Money / Guardrail Scope`
- 체크 항목:
  - [ ] compare 결과에 `Real-Money / Guardrail` 탭이 보이는지
  - [ ] annual strict 전략이 `Full strict equity Real-Money surface`로 표시되는지
  - [ ] strict quarterly prototype이 `Deferred` 또는 prototype 범위로 표시되어 annual strict와 같은 실전 검증 완료 상태로 보이지 않는지
  - [ ] `Global Relative Strength`가 ETF operability / cost / benchmark first pass로 표시되고, dedicated ETF underperformance/drawdown guardrail은 아직 없음으로 읽히는지
  - [ ] `GTAA`, `Risk Parity Trend`, `Dual Momentum`은 ETF Real-Money / ETF guardrail first pass로 구분되는지
  - [ ] saved portfolio를 다시 열기 전에 strategy별 Real-Money / Guardrail 범위를 확인할 수 있는지
  - [ ] history record에서 annual / quarterly / ETF first-pass 차이가 자연스럽게 읽히는지

## 8. Phase 28 작업 의도 확인

- 확인 위치:
  - `.note/finance/phase28/PHASE28_STRATEGY_FAMILY_PARITY_AND_CADENCE_COMPLETION_PLAN.md`
  - `.note/finance/phase28/PHASE28_STRATEGY_CAPABILITY_SNAPSHOT_FIRST_WORK_UNIT.md`
  - `.note/finance/phase28/PHASE28_HISTORY_REPLAY_PARITY_SECOND_WORK_UNIT.md`
  - `.note/finance/phase28/PHASE28_SAVED_PORTFOLIO_REPLAY_PARITY_THIRD_WORK_UNIT.md`
  - `.note/finance/phase28/PHASE28_COMPARE_AND_WEIGHTED_DATA_TRUST_FOURTH_WORK_UNIT.md`
  - `.note/finance/phase28/PHASE28_REAL_MONEY_GUARDRAIL_PARITY_FIFTH_WORK_UNIT.md`
- 체크 항목:
  - [ ] Phase 28이 새 전략 추가가 아니라 strategy family 차이 정리 phase라는 점이 이해되는지
  - [ ] `Parity`가 모든 전략을 똑같이 만드는 뜻이 아니라, 차이를 헷갈리지 않게 맞추는 뜻으로 읽히는지
  - [ ] quarterly prototype이 annual strict와 같은 실전 검증 수준으로 오해되지 않는지
  - [ ] GRS가 재무제표 전략이 아니라 price-only ETF 전략이라는 점이 문서와 UI에서 일관되게 보이는지
  - [ ] history replay / load parity가 투자 분석이 아니라 재실행 / 복원 QA라는 점이 이해되는지
  - [ ] saved portfolio replay / load parity도 투자 분석이 아니라 compare + weighted portfolio 재현 QA라는 점이 이해되는지
  - [ ] compare / weighted Data Trust도 투자 분석이 아니라 데이터 조건 확인 QA라는 점이 이해되는지
  - [ ] Real-Money / Guardrail parity도 모든 전략을 똑같이 만드는 작업이 아니라 전략별 검증 범위를 구분하는 작업이라는 점이 이해되는지

## 9. 문서와 closeout 확인

- 확인 문서:
  - `.note/finance/phase28/PHASE28_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/phase28/PHASE28_COMPLETION_SUMMARY.md`
  - `.note/finance/phase28/PHASE28_NEXT_PHASE_PREPARATION.md`
  - `.note/finance/MASTER_PHASE_ROADMAP.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`
- 체크 항목:
  - [ ] Phase 28 상태가 현재 구현 상태와 맞는지
  - [ ] 새 문서가 index에서 바로 찾히는지
  - [ ] 다음 작업 후보가 Phase 29 candidate review workflow 쪽으로 자연스럽게 이어지는지

## 한 줄 판단 기준

이번 checklist는
**새 기능이 많이 붙었는가**가 아니라,
**전략별로 이미 붙어 있는 기능과 아직 덜 붙은 기능을 사용자가 헷갈리지 않고 읽을 수 있는가**
를 확인하는 문서다.
