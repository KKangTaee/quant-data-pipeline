# Phase 33 Ledger Draft Save UI Second Work Unit

## 목적

두 번째 작업은 `Backtest > Portfolio Proposal`의 Validation Pack 아래에서
paper ledger 초안을 확인하고 명시적으로 저장할 수 있게 만드는 것이다.

## 쉽게 말하면

Phase 32 handoff가 "paper ledger 준비 가능"이라고 읽히면,
사용자가 시작일, benchmark, review cadence, trigger를 확인한 뒤
`Save Paper Tracking Ledger`를 눌러 장부에 남기는 단계다.

## 왜 필요한가

- Validation Pack을 여는 것만으로 저장되면 안 된다.
- paper tracking은 실제 돈을 넣는 것이 아니지만, 나중에 Phase34가 읽을 관찰 조건이므로 명시 저장이 필요하다.
- 작성 중 proposal은 durable source가 아니므로, proposal draft 저장 전에는 paper ledger 저장을 막아야 한다.

## 구현 내용

- `app/web/backtest_portfolio_proposal.py`
  - Validation Pack 아래 `Paper Tracking Ledger Draft`를 추가했다.
  - `Ledger ID`, `Paper Status`, `Tracking Start Date`, `Review Cadence`, `Tracking Benchmark`, `Review Triggers`, `Operator Note` 입력을 추가했다.
  - `Save Paper Tracking Ledger` 버튼으로만 저장되게 했다.
  - 작성 중 proposal은 preview는 가능하지만 `Persisted Source` check가 실패해 저장되지 않게 했다.

- `app/web/backtest_portfolio_proposal_helpers.py`
  - paper ledger save evaluation을 추가했다.
  - duplicate ledger id, source persistence, Phase33 handoff, target weight, tracking rules, review triggers를 저장 전 check로 계산한다.

## 완료 기준

- 단일 후보 direct path와 저장 proposal validation detail에서 paper ledger 저장 UI가 보인다.
- 작성 중 proposal은 proposal draft를 먼저 저장해야 paper ledger 저장이 가능하다.
- preview를 열어도 자동 저장되지 않는다.
