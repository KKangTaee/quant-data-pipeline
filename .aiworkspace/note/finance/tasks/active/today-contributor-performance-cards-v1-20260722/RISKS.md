# Today Contributor Performance Cards V1 Risks

## Resolved

- contribution과 item return의 단위·tone을 독립 field/label로 분리했다.
- group item return은 공통 `basis_date`의 exact `flow_adjusted_index - 1`만 사용해 미래 관측이나 이전 non-null 값이 공통 기준일로 오표기되는 위험을 닫았다.
- selected-position은 `lane.latest_usable_date`의 exact row만 사용해 trailing-null에서 이전 return을 재사용하던 회귀를 닫았다.
- 추가매수·일부매도 종목의 단순 current/initial fallback은 계속 금지했다.
- shared Portfolio Monitoring item row는 additive field만 추가했으며 focused page regression을 통과했다.
- `기여 상위 2 · 하위 2` scope note와 기준일 footer를 React/fallback에 함께 표시했다.
- contribution 부호를 React/fallback 모두 `+$…` / `-$…`로 고정하고 평가액 formatter는 유지했다.
- 1280/760/420 actual Browser QA에서 responsive layout, overflow, clipping, console 위험을 닫았다.

## Remaining Gaps

- 승인된 V1 범위의 미해결 위험은 없다. 전체 종목 탐색과 Portfolio Monitoring 본 화면 개편은 의도적으로 out of scope다.
