# Phase 34 Decision Evidence Pack Second Work Unit

## 목적

두 번째 작업은 저장된 Paper Portfolio Tracking Ledger row를
최종 선정 판단에 사용할 `Decision Evidence Pack`으로 읽는 기준을 구현하는 것이다.

## 쉽게 말하면

paper ledger가 있다고 바로 최종 후보로 고르는 것이 아니라,
그 ledger가 최종 판단에 충분한 근거를 갖고 있는지 다시 확인한다.

## 2026-05-03 보정 후 현재 해석

이 문서는 Phase34 두 번째 작업의 첫 구현 기준을 기록한다.
현재 main flow에서는 별도 paper ledger row가 필수 입력이 아니며,
`Backtest > Final Review`가 단일 후보 또는 saved proposal을 source로 선택한 뒤
validation / robustness / inline paper observation 기준을 하나의 evidence pack으로 묶는다.
기존 paper ledger 기반 helper는 compatibility / 운영 artifact를 읽는 기준으로 남긴다.

## 왜 필요한가

- paper ledger는 "관찰 대상으로 등록했다"는 기록이다.
- 최종 선정은 source, target weight, tracking rule, validation / robustness snapshot, review trigger가 함께 맞아야 한다.
- selected route가 live approval처럼 오해되지 않으려면 실행 경계도 evidence 안에서 계속 확인해야 한다.

## 구현 내용

- `_build_final_selection_decision_evidence_pack` helper 추가
- evidence route 추가
  - `READY_FOR_FINAL_DECISION`
  - `FINAL_DECISION_NEEDS_REVIEW`
  - `FINAL_DECISION_BLOCKED`
- 확인 기준 추가
  - paper ledger source
  - Phase34 handoff
  - paper status
  - target component / target weight 합계
  - tracking start / benchmark / cadence
  - review trigger
  - Phase31 / Phase32 snapshot blocker
  - live approval / order instruction boundary

## 완료 기준

- 저장된 paper ledger row 하나로 evidence route, score, blocker, review item, suggested decision route가 계산된다.
- `SELECT_FOR_PRACTICAL_PORTFOLIO`는 evidence가 준비됐을 때만 자연스럽게 추천된다.
- evidence pack은 다른 registry를 수정하지 않는다.
