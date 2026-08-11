# Design

Approved target: [Next-transition forecast feasibility design](../../../../../../docs/superpowers/specs/2026-08-11-economic-cycle-forecast-feasibility-design.md)

Implementation plan: [Next-transition feasibility plan](../../../../../../docs/superpowers/plans/2026-08-12-economic-cycle-next-transition-feasibility.md)

Runtime observed-state와 분리된 순수 research module이 history를 입력받아 모든
destination의 confirmed transition event와 sample gate report를 계산한다. runtime
DB/service/UI는 gate가 통과되기 전까지 변경하지 않는다.
