# Phase 32 Stress Result Contract Second Work Unit

## 목적

두 번째 작업은 Phase 32가 읽을 stress / sensitivity 결과 row의 모양을 고정하는 것이다.

## 쉽게 말하면

실제 stress runner를 바로 만들기 전에,
"나중에 기간 분할, 최근 구간, benchmark 변경, parameter sensitivity 결과가 들어오면 어떤 표로 읽을 것인가"를 먼저 정한다.

## 왜 필요한가

- 결과 row 계약이 없으면 UI, 저장소, Phase 33 handoff가 서로 다른 언어를 쓰게 된다.
- stress 검증은 단일 숫자가 아니라 scenario / input status / result status / 다음 행동을 함께 읽어야 한다.
- 현재 phase에서 full engine sweep을 만들지 않아도, 사용자는 어떤 검증이 남았는지 같은 표로 볼 수 있어야 한다.

## 구현 내용

- `app/web/backtest_portfolio_proposal_helpers.py`에 `phase32_stress_summary_v1` 계약을 추가했다.
- stress row는 다음 값을 기본으로 갖는다.
  - `Stress ID`
  - `Category`
  - `Scenario`
  - `Input Status`
  - `Result Status`
  - `Baseline`
  - `Expected Check`
  - `Judgment`
  - `Decision Use`
  - `Next Action`
- `Result Status = NOT_RUN`은 아직 실제 stress runner가 실행되지 않았다는 뜻으로 고정했다.

## 이번 작업에서 하지 않는 것

- 기간 분할 백테스트를 실제로 실행하지 않는다.
- benchmark 변경 backtest를 자동 실행하지 않는다.
- parameter sweep 결과를 새 registry에 저장하지 않는다.

## 완료 기준

- robustness validation result 안에 `stress_result_contract`가 포함된다.
- UI에서 contract와 stress summary row를 같은 schema로 읽을 수 있다.
- 사용자가 `NOT_RUN`을 실패가 아니라 "아직 실행 전" 상태로 이해할 수 있다.
