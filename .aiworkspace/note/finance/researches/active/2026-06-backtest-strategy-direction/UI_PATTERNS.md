# UI And Workflow Patterns

Status: Active
Last Verified: 2026-06-08

## Product Goal

Backtest 화면은 "전략 실행"보다 "후보 source 생성과 evidence handoff"를 중심으로 읽혀야 한다.
사용자는 전략별 성숙도, 데이터 신뢰도, validation gap, monitoring readiness를 혼동하지 않아야 한다.

## Pattern 1. Strategy Maturity Snapshot

각 전략에는 다음 상태를 한 줄로 보여주는 maturity snapshot이 필요하다.

- Runtime execution
- Compare / saved replay
- Candidate Library replay
- Practical Validation compatibility
- Final Review gate evidence
- Portfolio Monitoring policy

현재 이미 `Strategy Capability Snapshot` 취지가 docs에 남아 있지만, direction 관점에서는 strategy inventory와 연결된 durable 기준표가 더 필요하다.

## Pattern 2. Evidence-First Strategy Detail

전략 상세는 수익률 숫자보다 아래 순서로 읽혀야 한다.

1. strategy family / intended role
2. data contract and PIT / survivorship assumption
3. current candidate anchor or lack of anchor
4. known weakness
5. required next evidence
6. allowed next workflow action

이 구조는 `runs successfully`와 `ready for Final Review`를 분리한다.

## Pattern 3. Bridge View For Portfolio Construction

현재 후보가 단일 전략 winner인지, portfolio sleeve인지 구분해야 한다.

- Equal Weight는 alpha engine보다 exposure sleeve다.
- GTAA는 tactical / defensive ETF component다.
- strict annual candidates는 equity return engine이다.
- Quality + Value는 blended factor anchor다.

따라서 다음 UI / report는 단일 성과표만 보여주기보다 "component role / weight / evidence gap"을 함께 보여줘야 한다.

## Pattern 4. Research Lane Isolation

Risk-On Momentum 5D는 daily swing research lane으로 유지하고, 다음 세 가지가 설계되기 전까지 monitoring signal로 승격하지 않는다.

- Daily Swing Practical Validation module
- Final Review selected-route rule
- Portfolio Monitoring daily signal / review cadence policy

## Pattern Conflicts With Current Boundaries

| Pattern | Conflict | Handling |
| --- | --- | --- |
| Strategy maturity snapshot | 너무 많은 status가 UI를 복잡하게 만들 수 있음 | 2차 문서에서는 기준만 고정하고, 3차 구현은 한 화면 / 한 table로 좁힌다 |
| Evidence-first detail | 사용자는 CAGR / MDD를 먼저 보고 싶어 할 수 있음 | 성과 수치는 유지하되, gate / data trust / weakness와 함께 보여준다 |
| Portfolio bridge view | weighted portfolio replay와 Practical Validation source가 섞일 수 있음 | saved mix replay, component result, validation handoff를 분리한다 |
| Research lane isolation | Risk-On Momentum을 빨리 monitoring에 붙이고 싶은 유혹 | 별도 governance 승인 전까지 context / research evidence로만 둔다 |
