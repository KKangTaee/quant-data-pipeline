# Non-GTAA Final Selection Candidate Search 2026-05-31

## Goal

GTAA가 아닌 전략군으로 Backtest Analysis -> Practical Validation -> Final Review selected-route gate까지 통과해 `SELECT_FOR_PRACTICAL_PORTFOLIO` 저장과 Selected Portfolio Dashboard 노출이 가능한 최종 포트폴리오 후보를 찾는다.

## 이걸 하는 이유?

다음 workflow 개편 검증에는 이미 3단계 Final Review까지 통과해 Dashboard에서 읽을 수 있는 실제 selected portfolio row가 필요하다. 기존 GTAA 중심 후보는 selected-route gate에서 차단됐으므로 비-GTAA 전략군을 별도로 탐색한다.

## Scope

- GTAA를 제외한 Compare / Backtest 전략군을 우선 탐색한다.
- 후보는 기존 DB와 runtime을 사용해 생성하고, gate 통과 전까지 registry write를 하지 않는다.
- Practical Validation required gate를 통과한 후보만 Final Review selected-route 평가 대상으로 본다.
- selected-route gate가 `select_allowed=True`일 때만 `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl`에 `SELECT_FOR_PRACTICAL_PORTFOLIO` row를 append한다.
- 저장 후 Selected Portfolio Dashboard read model에서 노출 여부를 확인한다.

## Out Of Scope

- live approval, 주문, 자동 리밸런싱, broker/account 연동.
- strategy logic 변경.
- provider / DB ingestion 신규 실행.
- gate 우회, 임의 waiver, registry rewrite.
