# Phase 32 Stress Summary Surface Third Work Unit

## 목적

세 번째 작업은 단일 후보, 작성 중 proposal, 저장 proposal의 Validation Pack 안에서 stress / sensitivity summary를 한 표로 확인하게 만드는 것이다.

## 쉽게 말하면

후보가 "좋아 보인다"에서 멈추지 않고,
앞으로 어떤 방식으로 다시 흔들어봐야 하는지 표로 보여준다.

## 왜 필요한가

- robustness preview만 있으면 입력 준비 여부는 알 수 있지만, 실제로 어떤 stress 질문이 남았는지 한눈에 보기 어렵다.
- period split, recent window, benchmark sensitivity, parameter sensitivity, weight sensitivity, leave-one-out을 같은 row 언어로 읽어야 다음 단계가 자연스럽다.
- stress 결과가 아직 없어도 `NOT_RUN`으로 보이면 사용자가 "실행 전" 상태를 명확히 이해할 수 있다.

## 구현 내용

- `Backtest > Portfolio Proposal`의 Validation Pack 안에 `Stress / Sensitivity Summary` table을 추가했다.
- summary row는 기본 6개 scenario를 가진다.
  - period split
  - recent window
  - benchmark sensitivity
  - parameter sensitivity
  - weight sensitivity
  - leave-one-out
- 단일 후보에는 portfolio-only stress가 `NOT_APPLICABLE`로 표시될 수 있다.
- 저장 proposal validation 요약 표에도 robustness / Phase33 handoff column을 추가했다.

## 이번 작업에서 하지 않는 것

- stress 결과를 과거 backtest run history에서 자동 매칭하지 않는다.
- 새 stress registry를 만들지 않는다.
- UI에서 stress 실행 버튼을 만들지 않는다.

## 완료 기준

- 단일 후보 / 작성 중 proposal / 저장 proposal에서 stress summary table이 보인다.
- `Input Status`와 `Result Status`가 구분되어 보인다.
- summary table이 live approval이나 최종 투자 선정으로 오해되지 않는다.
