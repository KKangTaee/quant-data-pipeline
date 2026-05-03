# Phase 34 Final Decision UI Third Work Unit

## 목적

세 번째 작업은 사용자가 Final Selection Decision을 명시적으로 저장할 수 있는 UI를 추가하는 것이다.
첫 구현은 `Backtest > Portfolio Proposal` 안에서 시작했지만, 2026-05-03 UX 보정 이후 현재 main UI는 `Backtest > Final Review`다.

## 쉽게 말하면

저장된 paper ledger를 고른 뒤,
"선정 / 보류 / 거절 / 재검토" 중 하나를 사람이 직접 선택하고 사유를 남기는 화면을 만든다.

## 2026-05-03 보정 후 현재 해석

이 문서는 세 번째 작업의 첫 구현 기준이다.
사용자가 반복 저장 UX 문제를 제기한 뒤 main UI는 `Backtest > Final Review`로 이동했다.
현재 Portfolio Proposal 탭은 proposal draft 작성 / 저장에 집중하고,
Final Review 탭에서 단일 후보 또는 saved proposal을 선택해 `최종 검토 결과 기록`으로 판단을 남긴다.

## 왜 필요한가

- 최종 판단은 자동으로 저장되면 안 된다.
- 같은 evidence라도 사용자의 제약 조건이나 운영 판단에 따라 보류 / 거절 / 재검토가 될 수 있다.
- 저장 전 blocker가 보이면 어떤 값을 보강해야 하는지 바로 보여야 한다.

## 구현 내용

- `Backtest > Final Review`에 final decision pack 추가
- `Decision ID`, `Decision Route`, `Operator Reason`, `Operator Constraints`, `Operator Next Action` 입력 추가
- `최종 검토 결과 기록` 버튼 추가
- 저장 전 검증 helper 추가
  - decision id 누락 / 중복
  - source candidate / proposal 연결
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
- current candidate, Pre-Live, Portfolio Proposal registry를 덮어쓰지 않는다.
