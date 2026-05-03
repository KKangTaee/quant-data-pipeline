# Phase 32 Robustness Input Preview First Work Unit

## 목적

Phase 32의 첫 번째 작업은 실제 stress sweep을 실행하기 전에,
후보나 Portfolio Proposal이 robustness 검증을 실행할 수 있는 입력을 갖고 있는지 확인하는 preview를 만드는 것이다.

## 쉽게 말하면

좋은 성과 숫자를 바로 믿지 않고,
"이 결과를 다시 흔들어볼 만큼 기간, 설정, benchmark, 비교 근거가 남아 있는가"를 먼저 확인한다.

## 왜 필요한가

- 기간 정보가 없으면 최근 구간 / 기간 분할 stress를 만들 수 없다.
- contract snapshot이 없으면 parameter sensitivity를 재현하기 어렵다.
- benchmark나 compare evidence가 없으면 결과가 무엇보다 좋은지 판단하기 어렵다.
- 이 입력들이 부족한 상태에서 stress 결과 UI를 만들면, 이후 Phase 33 / Phase 34 판단도 흔들린다.

## 구현 대상

- `app/web/backtest_portfolio_proposal_helpers.py`
  - Phase 31 validation input에 robustness용 snapshot을 추가한다.
  - robustness route / score / blockers / input gaps / suggested sweeps를 계산한다.
- `app/web/backtest_portfolio_proposal.py`
  - Validation Pack 아래에 `Robustness / Stress Validation Preview`를 표시한다.

## route 기준

| Route | 의미 |
|---|---|
| `READY_FOR_STRESS_SWEEP` | 기간 / 성과 / 설정 / benchmark snapshot이 있어 stress 검증 실행 후보로 볼 수 있다 |
| `NEEDS_ROBUSTNESS_INPUT_REVIEW` | stress 실행 전 compare evidence, benchmark, 기간 길이 같은 입력 gap을 더 확인해야 한다 |
| `BLOCKED_FOR_ROBUSTNESS` | Phase 31 hard blocker, 성과 snapshot 누락, 기간 누락, contract 누락처럼 stress 검증 전에 반드시 해결해야 할 항목이 있다 |

## 이번 작업에서 하지 않는 것

- 기간 분할 백테스트를 실제로 다시 실행하지 않는다.
- parameter sensitivity engine을 아직 붙이지 않는다.
- live approval / 최종 투자 선정 / 주문 지시는 만들지 않는다.
- 새 robustness registry를 만들지 않는다.

## 완료 기준

- `Backtest > Portfolio Proposal`의 단일 후보 / 작성 중 proposal / 저장 proposal Validation Pack에서 robustness preview가 보인다.
- component별 기간, CAGR, MDD, benchmark, contract summary, compare evidence 여부가 보인다.
- suggested sweep이 다음 작업 안내로 읽힌다.
- helper smoke와 py_compile이 통과한다.
