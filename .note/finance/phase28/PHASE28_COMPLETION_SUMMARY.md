# Phase 28 Completion Summary

## 목적

이 문서는 Phase 28 `Strategy Family Parity And Cadence Completion`를 closeout 시점에 정리하기 위한 문서다.

현재는 Phase 28 active 상태의 진행 summary다.
사용자 QA 단계가 되면 실제 완료 내용과 checklist 기준으로 다시 갱신한다.

## 진행 상태

- `active`

## 검증 상태

- `not_ready_for_qa`

## 이번 phase에서 현재까지 완료 / 진행한 것

### 1. Strategy Capability Snapshot 첫 구현

- `Backtest > Single Strategy`에서 선택한 strategy의 지원 범위를 볼 수 있게 했다.
- `Backtest > Compare & Portfolio Builder`에서 선택한 각 strategy box 안에도 같은 snapshot을 추가했다.

쉽게 말하면:

- 사용자가 전략을 실행하기 전에 이 전략이 annual인지, quarterly prototype인지, price-only ETF 전략인지 먼저 확인할 수 있다.

### 2. annual / quarterly / GRS 차이 설명

- strict annual은 가장 성숙한 Real-Money / Guardrail surface로 설명했다.
- strict quarterly prototype은 Data Trust와 Portfolio Handling은 지원하지만, Real-Money promotion / Guardrail 판단은 아직 annual 중심이라고 설명했다.
- Global Relative Strength는 재무제표 전략이 아니라 price-only ETF relative strength 전략으로 설명했다.

쉽게 말하면:

- 기능이 없는 것처럼 보이는 부분이 버그인지, 아직 의도적으로 남겨둔 차이인지 구분하기 쉬워졌다.

### 3. History Replay / Load Parity Snapshot 추가

- `Backtest > History > Selected History Run`에서 선택한 저장 기록의 재실행 / form 복원 관련 설정을 표로 볼 수 있게 했다.
- 새 history record는 결과 실제 기간, price freshness, excluded ticker, malformed price row, guardrail reference ticker를 더 보존한다.
- annual strict, quarterly prototype, GRS, GTAA, 기타 ETF 전략별로 어떤 값이 history에 남아야 하는지 구분해서 보여준다.

쉽게 말하면:

- 예전 백테스트를 다시 열기 전에 “이 기록으로 무엇이 복원되고 무엇은 빠질 수 있는지”를 먼저 확인할 수 있다.

## 아직 남아 있는 것

- saved portfolio replay parity 점검
- Data Trust Summary를 compare / saved replay에 어디까지 확장할지 결정
- Real-Money / Guardrail parity 범위 결정
- 사용자 manual UI validation

## closeout 판단

아직 closeout 상태가 아니다.

현재는 Phase 28의 첫 번째 / 두 번째 구현 단위를 완료한 상태이며,
saved portfolio replay parity와 남은 확장 범위를 더 본 뒤 사용자 QA 단계로 넘길지 판단한다.
