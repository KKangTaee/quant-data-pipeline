# Today Contributor Performance Cards V1 Risks

## Resolved

- contribution과 item return의 단위·tone을 독립 field/label로 분리했다.
- 추가매수·일부매도 종목은 마지막 유효 `flow_adjusted_index - 1`만 사용하고 단순 current/initial fallback을 금지했다.
- shared Portfolio Monitoring item row는 additive field만 추가했으며 focused page regression을 통과했다.
- `기여 상위 2 · 하위 2` scope note와 기준일 footer를 React/fallback에 함께 표시했다.
- 1280/760/420 actual Browser QA에서 responsive layout, overflow, clipping, console 위험을 닫았다.

## Remaining Gaps

- 승인된 V1 범위의 미해결 위험은 없다. 전체 종목 탐색과 Portfolio Monitoring 본 화면 개편은 의도적으로 out of scope다.
