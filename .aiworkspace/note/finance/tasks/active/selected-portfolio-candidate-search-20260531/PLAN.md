# Selected Portfolio Candidate Search 2026-05-31

## Goal

기존 DB, saved portfolio, workflow registry를 활용해 Backtest Analysis -> Practical Validation -> Final Review -> Selected Portfolio Dashboard 흐름을 실제로 통과하는 포트폴리오 후보를 찾고, selected-route gate를 통과한 후보만 `SELECT_FOR_PRACTICAL_PORTFOLIO`로 저장한다.

## 이걸 하는 이유?

Final Review가 selection-only save 정책으로 정리된 뒤, 실제 후보가 Practical Validation gate와 Final Review selected-route gate를 통과해 Operations dashboard까지 노출되는지 운영 흐름 기준으로 확인해야 한다.

## Scope

- 기존 `PORTFOLIO_SELECTION_SOURCES`, `PRACTICAL_VALIDATION_RESULTS`, saved portfolios, final decision registry를 읽어 후보군을 재검토한다.
- 필요하면 Backtest runtime / Practical Validation service를 사용해 후보를 새로 생성 또는 재검증한다.
- Practical Validation 필수 gate 통과 후보만 Final Review 대상으로 본다.
- Final Review selected-route gate 통과 후보만 정식 선정 저장한다.
- 저장 뒤 `Operations > Selected Portfolio Dashboard` read model과 Browser QA로 노출 여부를 확인한다.

## Out Of Scope

- live approval, 주문, 자동 리밸런싱, broker/account 연동.
- registry rewrite / cleanup.
- UX 구조 변경 또는 코드 변경.

## Stop Condition

- 선정 저장 후보 목록, dashboard 노출 후보 목록, 통과 / 탈락 사유, 다음 확인 항목을 정리한다.
- 저장 후보가 없으면 gate별 blocker와 보강 필요 데이터를 정리한다.
