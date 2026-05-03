# Phase 34 Final Decision UI Third Work Unit

## 목적

세 번째 작업은 `Backtest > Portfolio Proposal`에서 사용자가 Final Selection Decision을 명시적으로 저장할 수 있는 UI를 추가하는 것이다.

## 쉽게 말하면

저장된 paper ledger를 고른 뒤,
"선정 / 보류 / 거절 / 재검토" 중 하나를 사람이 직접 선택하고 사유를 남기는 화면을 만든다.

## 왜 필요한가

- 최종 판단은 자동으로 저장되면 안 된다.
- 같은 evidence라도 사용자의 제약 조건이나 운영 판단에 따라 보류 / 거절 / 재검토가 될 수 있다.
- 저장 전 blocker가 보이면 어떤 값을 보강해야 하는지 바로 보여야 한다.

## 구현 내용

- 저장된 `Paper Tracking Ledger` detail 아래에 `Final Selection Decision Pack` 추가
- `Decision ID`, `Decision Route`, `Operator Reason`, `Operator Constraints`, `Operator Next Action` 입력 추가
- `Save Final Selection Decision` 버튼 추가
- 저장 전 검증 helper 추가
  - decision id 누락 / 중복
  - source paper ledger 연결
  - route 유효성
  - operator reason 입력
  - selected route의 evidence readiness
- 저장 runtime 추가
  - `app/web/runtime/final_selection_decisions.py`
  - `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`

## 완료 기준

- button을 누르기 전에는 final decision row가 저장되지 않는다.
- 저장 성공 후 success notice가 보인다.
- 저장 row에는 live approval과 order instruction이 `false`로 남는다.
- current candidate, Pre-Live, Portfolio Proposal, Paper Ledger registry를 덮어쓰지 않는다.
