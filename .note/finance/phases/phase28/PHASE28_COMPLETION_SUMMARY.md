# Phase 28 Completion Summary

## 목적

이 문서는 Phase 28 `Strategy Family Parity And Cadence Completion`를 closeout 시점에 정리하기 위한 문서다.

현재는 Phase 28 complete 상태의 closeout summary다.
사용자 QA까지 완료되었으므로 Phase 29 handoff 기준으로 사용한다.

## 진행 상태

- `complete`

## 검증 상태

- `manual_qa_completed`

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

### 4. Saved Portfolio Replay / Load Parity Snapshot 추가

- `Backtest > Compare & Portfolio Builder > Saved Portfolios`에서 저장 포트폴리오를 선택하면 replay / load 가능성을 표로 볼 수 있게 했다.
- compare 공용 입력, 전략 목록, weight/date alignment, strategy override map, 전략별 핵심 override 저장 상태를 보여준다.
- `Strategy Override Summary` 접힘 영역으로 저장된 strategy-specific 설정을 한 번 더 요약한다.

쉽게 말하면:

- 저장 포트폴리오를 다시 실행하기 전에 “이 저장본이 같은 전략과 같은 weight로 다시 열릴 수 있는가”를 먼저 확인할 수 있다.

### 5. Compare / Weighted Data Trust 확장

- `Strategy Comparison`에 `Data Trust` 탭을 추가했다.
- `Weighted Portfolio Result`에 `Component Data Trust` 탭을 추가했다.
- compare / weighted / saved replay history context에도 전략별 data trust rows를 남긴다.

쉽게 말하면:

- 여러 전략을 비교하거나 섞기 전에, 각 전략이 실제로 어떤 데이터 기간과 품질 조건에서 계산됐는지 먼저 확인할 수 있다.

### 6. Real-Money / Guardrail parity 결정

- `Strategy Comparison`에 `Real-Money / Guardrail` 탭을 추가했다.
- `History Real-Money / Guardrail Scope` 표를 추가했다.
- `Saved Portfolio Real-Money / Guardrail Scope` 표를 추가했다.
- quarterly prototype에는 annual strict 수준의 실전 검증 surface를 억지로 붙이지 않는다고 결정했다.

쉽게 말하면:

- annual strict, quarterly prototype, ETF 전략군이 각각 어떤 실전 검증 범위로 읽혀야 하는지 한 표에서 구분할 수 있다.

## 아직 남아 있는 것

- Phase 28 범위 안에서는 없음

## closeout 판단

Phase 28은 종료 상태다.

현재는 Phase 28의 첫 번째 / 두 번째 / 세 번째 구현 단위를 완료한 상태이며,
네 번째 Data Trust 확장 단위까지 완료했다.
다섯 번째 Real-Money / Guardrail parity 범위 결정도 완료했다.
사용자 checklist QA도 완료했다.

다음 단계는 Phase 29 `Candidate Review And Recommendation Workflow`다.
