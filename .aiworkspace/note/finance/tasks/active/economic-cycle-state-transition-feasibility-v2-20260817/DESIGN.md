# Design

Canonical design:

- `docs/superpowers/specs/2026-08-17-economic-cycle-state-transition-feasibility-design.md`

핵심 경계는 current state와 transition forecast의 분리다. current state는 RTDSM
confirmed phase가 소유하고, forecast는 core-only와 policy/inflation/rates/credit
extended model을 독립 검증한다. market price는 coverage를 통과할 때만 shadow block에
들어가며 fiscal input은 승인된 PIT source가 없으면 `NOT_TESTABLE`로 남긴다.

1~3차는 read-only experiment이며 production DB writer, Overview service와 React UI를
호출하지 않는다.
