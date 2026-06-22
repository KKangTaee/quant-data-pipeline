# Design

## Source Confidence

- Replace the long ledger feel with a compact status board.
- Keep direct brief sources separate from reference / management sources.
- Show each source row as:
  - source name and status
  - data basis
  - where it is used
  - refresh judgment
- Keep boundary copy but lower it below the workflow.

## Refresh Assist

- If `refresh_plan.items` is empty:
  - show a compact no-action state
  - omit the disabled `현재 보강 없음` button
  - keep `전체 Market Context 자료 보강` as a secondary fallback
- If refresh items exist:
  - show the action rows first
  - keep `현재 이슈만 보강` as the main action
  - show excluded items as muted notes

## Boundary

This is a renderer / copy / CSS change only. Existing action ids and refresh functions stay unchanged.
