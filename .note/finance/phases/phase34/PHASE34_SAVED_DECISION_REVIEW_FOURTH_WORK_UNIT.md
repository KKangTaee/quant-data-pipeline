# Phase 34 Saved Decision Review Fourth Work Unit

## 목적

네 번째 작업은 저장된 Final Selection Decision을 다시 읽고,
Phase 35 `Post-Selection Operating Guide`가 이어받을 handoff를 정리하는 것이다.

## 쉽게 말하면

최종 판단을 저장하고 끝내지 않고,
나중에 다시 열어서 어떤 paper ledger와 component를 근거로 선정 / 보류 / 거절 / 재검토했는지 확인할 수 있게 한다.

## 왜 필요한가

- 최종 후보 선정은 이후 운영 기준의 출발점이다.
- Phase35는 선정된 후보만 운영 가이드로 넘겨야 한다.
- 보류 / 거절 / 재검토 기록도 왜 Phase35로 가지 않았는지 남겨야 한다.

## 구현 내용

- 저장된 final decision summary table 추가
- `Review Final Selection Decision` selectbox 추가
- selected components table 추가
- Phase35 handoff route 추가
  - `READY_FOR_POST_SELECTION_OPERATING_GUIDE`
  - `WAIT_FOR_MORE_PAPER_TRACKING`
  - `NO_PHASE35_HANDOFF`
  - `RE_REVIEW_BEFORE_OPERATING_GUIDE`
- Phase35 handoff requirements와 raw JSON 확인 expander 추가
- operations guide와 code analysis 문서 갱신

## 완료 기준

- 저장된 decision row를 UI에서 다시 읽을 수 있다.
- source paper ledger와 selected components가 연결되어 보인다.
- Phase35가 읽을 selected route와 next action이 분명하다.
- live approval / broker order / 자동매매와 분리된 경계가 문서와 UI에 남는다.
