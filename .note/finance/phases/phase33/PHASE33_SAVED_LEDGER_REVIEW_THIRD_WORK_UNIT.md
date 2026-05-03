# Phase 33 Saved Ledger Review Third Work Unit

## 목적

세 번째 작업은 저장된 `Paper Portfolio Tracking Ledger` record를 다시 읽고 확인하는 review surface를 만드는 것이다.

## 쉽게 말하면

저장 버튼을 눌러 장부에 남긴 paper tracking 조건을
다시 화면에서 열어 source, 비중, benchmark, review cadence, trigger가 맞는지 확인할 수 있게 한다.

## 왜 필요한가

- paper tracking ledger는 Phase 34 final selection의 입력이므로 저장 후 재확인이 가능해야 한다.
- 저장만 되고 화면에서 다시 읽을 수 없으면 사용자가 어떤 조건으로 관찰을 시작했는지 확인하기 어렵다.
- 후보 / proposal registry와 별도 저장소를 쓰기 때문에 ledger record가 어느 source에서 왔는지 명확히 보여야 한다.

## 구현 내용

- `Backtest > Portfolio Proposal`에 `저장된 Paper Tracking Ledger 확인` section을 추가했다.
- 저장된 ledger 목록에서 `ledger_id`, source, status, benchmark, review cadence, weight total, Phase34 handoff route를 요약한다.
- 선택한 ledger detail에서 target component, review trigger, raw JSON을 확인할 수 있게 했다.
- 저장된 ledger review는 current candidate, Pre-Live, Portfolio Proposal registry를 수정하지 않는다.

## 완료 기준

- ledger가 저장된 뒤 Portfolio Proposal 화면에서 목록으로 다시 보인다.
- 선택한 record의 source와 target weights가 저장 당시 조건과 일치하게 읽힌다.
- review trigger와 operator note가 detail에서 확인된다.

## 이번 작업에서 하지 않는 것

- paper 기간 수익률을 자동 계산하지 않는다.
- 최종 선정 / 보류 / 거절 decision을 저장하지 않는다.
- live approval이나 주문 지시를 만들지 않는다.
