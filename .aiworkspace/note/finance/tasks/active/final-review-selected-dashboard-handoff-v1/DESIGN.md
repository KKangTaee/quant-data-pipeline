# Design

## User Flow

1. 사용자는 Final Review에서 최종 판단을 저장한다.
2. Saved Decision Review에서 선정된 row가 Selected Portfolio Dashboard 대상으로 잡혔는지 확인한다.
3. 선정 row가 없거나 component / target weight / source contract 문제로 dashboard 연결이 막히면 같은 화면에서 이유를 본다.
4. 연결 가능한 row는 Operations > Selected Portfolio Dashboard에서 recheck / readiness / provider / timeline / allocation evidence를 이어서 본다.

## Runtime Contract

`build_selected_dashboard_handoff_review(final_decision_rows)`는 Final Decision V2 rows를 입력으로 받는다.

- final decision count / selected count / dashboard row count를 요약한다.
- selected route row만 dashboard row로 변환한다.
- dashboard row의 operation status를 기준으로 monitorable / blocked 수를 만든다.
- no final decision / no selected decision / blocked / ready route를 반환한다.
- table rows와 checklist rows를 UI가 그대로 표시할 수 있게 만든다.
- execution boundary는 read-only이며 approval / order / rebalance / auto-write를 모두 false로 둔다.

## UI Placement

- `Backtest > Final Review`
  - Saved Decision Review 안에 `Selected Dashboard Handoff`를 표시한다.
  - 저장된 판단 ledger보다 먼저 연결 상태와 대상 row를 요약한다.
- `Operations > Selected Portfolio Dashboard`
  - summary card 아래에 `Final Review Handoff`를 표시한다.
  - selected row가 없을 때도 이 handoff block을 먼저 보여준 뒤 empty state를 보여준다.

## Tradeoff

- handoff는 기존 gate와 continuity check를 대체하지 않는다.
- 여기서 재검증을 다시 하면 Final Review와 Selected Dashboard의 책임이 겹치므로, 이 레이어는 "연결 가능성 / 대상 row / 다음 행동"만 담당한다.
