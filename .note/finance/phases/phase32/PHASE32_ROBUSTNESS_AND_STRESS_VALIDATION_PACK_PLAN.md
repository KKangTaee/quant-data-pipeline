# Phase 32 Robustness And Stress Validation Pack Plan

## 이 문서는 무엇인가

Phase 32에서 만들 `Robustness And Stress Validation Pack`의 목적, 범위, 작업 단위를 정리하는 계획 문서다.

## 목적

- Phase 31에서 구조적으로 검토 가능한 후보나 Portfolio Proposal을 받아, 결과가 특정 기간 / benchmark / parameter에만 의존한 것인지 검증한다.
- 먼저 저장된 candidate / Pre-Live / proposal snapshot이 robustness 검증을 실행할 만큼 충분한지 확인하는 입력 pack을 만든다.
- 이후 기간 분할, 최근 구간, benchmark 변경, parameter sensitivity 같은 stress 결과를 한 화면에서 읽을 수 있게 확장한다.

## 쉽게 말하면

Phase 31이 "이 포트폴리오 구조가 말이 되는가"를 봤다면,
Phase 32는 "이 결과가 조건이 조금 바뀌어도 버티는가"를 보는 단계다.

처음부터 최종 투자 승인 버튼을 만들지 않는다.
먼저 실전 검토 전에 다시 흔들어볼 입력과 stress 질문을 정리한다.

## 왜 필요한가

- 좋은 CAGR / MDD 하나만으로는 실전 포트폴리오 후보라고 보기 어렵다.
- 특정 기간, 특정 benchmark, 특정 parameter 조합에서만 좋은 결과가 나왔을 수 있다.
- Phase 31 Validation Pack은 구조 위험과 다음 단계 안내를 제공하지만, 실제 robustness / stress 검증 결과는 아직 없다.

## 이 phase가 끝나면 좋은 점

- 사용자는 후보나 proposal이 robustness 검증을 실행할 준비가 되었는지 먼저 확인할 수 있다.
- period split, recent-window, benchmark sensitivity, parameter sensitivity 같은 검증 항목을 같은 언어로 읽을 수 있다.
- Phase 33 paper portfolio tracking이나 Phase 34 final selection으로 넘길 때 "왜 이 후보가 아직 부족한지"를 더 명확히 설명할 수 있다.

## 이 phase에서 다루는 대상

- `Backtest > Portfolio Proposal`의 단일 후보 / 작성 중 proposal / 저장 proposal Validation Pack
- current candidate registry row의 `period`, `contract`, `result`, `review_context.compare_readiness_evaluation`
- Pre-Live record의 `settings_snapshot`, `result_snapshot`, `tracking_plan`
- Portfolio Proposal registry row의 `candidate_refs`, `evidence_snapshot`

## 현재 구현 우선순위

1. Robustness input preview
   - 쉽게 말하면: stress 검증을 바로 실행하기 전에, 필요한 기간 / 설정 / benchmark / 성과 snapshot이 있는지 본다.
   - 왜 먼저 하는가: 입력 계약이 없으면 stress 결과를 저장하거나 비교하는 기준도 흔들린다.
   - 기대 효과: `READY_FOR_STRESS_SWEEP`, `NEEDS_ROBUSTNESS_INPUT_REVIEW`, `BLOCKED_FOR_ROBUSTNESS`로 다음 행동을 구분할 수 있다.
2. Stress / sensitivity summary surface
   - 쉽게 말하면: 기간 분할, 최근 구간, benchmark 변경, parameter sensitivity 결과를 한 표로 읽는다.
   - 왜 필요한가: 단일 full-period 성과가 우연인지, 여러 조건에서도 버티는지 봐야 한다.
   - 기대 효과: 후보를 paper tracking으로 넘길지, 보강할지, 차단할지 판단하기 쉬워진다.
3. Robustness blocker / next action
   - 쉽게 말하면: stress 결과가 나쁠 때 무엇을 고쳐야 하는지 알려준다.
   - 왜 필요한가: 숫자만 보여주면 사용자가 다음 행동을 정하기 어렵다.
   - 기대 효과: Phase 33 / Phase 34로 넘어가는 기준이 더 명확해진다.

## 현재 구현 결과

- Phase 32는 `implementation_complete / manual_qa_pending` 상태다.
- 첫 번째 작업으로 robustness 입력 preview와 stress 실행 후보 판정을 구현했다.
- 두 번째 작업으로 `phase32_stress_summary_v1` stress / sensitivity result contract를 정의했다.
- 세 번째 작업으로 `Stress / Sensitivity Summary` table을 Validation Pack 안에 추가했다.
- 네 번째 작업으로 `Phase 33 Handoff` route panel과 paper ledger 준비 기준 table을 추가했다.
- 실제 period split backtest, benchmark sensitivity runner, parameter sweep engine, paper ledger 저장은 Phase 32 범위 밖이며 후속 phase에서 다룬다.

## 이 문서에서 자주 쓰는 용어

- `Robustness`: 기간이나 조건이 조금 바뀌어도 후보의 성격이 유지되는지 보는 검증이다.
- `Stress`: 불리한 기간, 최근 구간, benchmark 변경, parameter 변경처럼 후보를 흔들어보는 검증이다.
- `Sensitivity`: parameter나 비중이 조금 바뀌었을 때 결과가 얼마나 민감하게 흔들리는지 보는 검증이다.
- `Stress Sweep`: 여러 stress 조건을 묶어서 실행하거나 요약하는 작업이다.
- `Input Gap`: stress 검증을 하기 전에 필요한 기간 / 설정 / benchmark / 성과 snapshot이 부족한 상태다.

## 이번 phase의 운영 원칙

- live approval, 주문 지시, 최종 투자 추천은 만들지 않는다.
- 처음에는 read-only preview와 summary surface로 시작한다.
- 저장된 후보 / proposal snapshot을 먼저 읽고, 새 registry는 필요성이 분명해질 때만 검토한다.
- Phase 30 QA pending 상태는 Phase 32 진행과 별도로 유지한다.
- Phase 32는 Phase 33 paper ledger와 Phase 34 final decision pack의 입력 품질을 높이는 중간 검증 단계다.

## 이번 phase의 주요 작업 단위

### 첫 번째 작업. Robustness 입력 preview와 stress 실행 후보 판정

- Phase 31 validation input에서 period, contract, benchmark, CAGR / MDD, compare evidence를 읽는다.
- `Robustness / Stress Validation Preview`를 Validation Pack 아래에 표시한다.
- route는 `READY_FOR_STRESS_SWEEP`, `NEEDS_ROBUSTNESS_INPUT_REVIEW`, `BLOCKED_FOR_ROBUSTNESS`로 나눈다.

### 두 번째 작업. Stress / sensitivity result contract 정의

- period split, recent window, benchmark sensitivity, parameter sensitivity 결과를 어떤 row 형태로 저장 / 표시할지 정의한다.
- 아직 full engine sweep을 붙이지 않더라도, UI가 읽을 result schema를 먼저 고정한다.

### 세 번째 작업. 후보 / proposal별 stress summary surface 추가

- 저장 proposal 또는 단일 후보에서 stress summary table을 확인할 수 있게 한다.
- stress 결과가 없을 때는 "아직 실행 전"으로 읽히게 하고, 다음 실행 안내를 보여준다.

### 네 번째 작업. Phase 33 handoff 정리

- robustness 결과가 paper portfolio tracking으로 넘어갈 수 있는지, 보강 검증이 필요한지, 차단해야 하는지 요약한다.
- Phase 33에서 실제 paper ledger를 만들 때 필요한 입력을 정리한다.

## 다음에 확인할 것

- 첫 번째 작업에서 robustness preview가 단일 후보 / 작성 중 proposal / 저장 proposal 모두에 붙는지 확인한다.
- suggested sweep 문구가 실제 다음 행동으로 읽히는지 확인한다.
- Phase32가 live approval이나 최종 선정으로 오해되지 않는지 확인한다.

## 한 줄 정리

Phase 32는 후보나 proposal이 실전 후보로 보이기 전에, 기간 / benchmark / parameter 변화에도 버티는지 검증하는 robustness / stress 단계다.
