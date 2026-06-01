# Plan

## 이걸 하는 이유?

Selected Portfolio Dashboard의 1~3번 흐름은 기능적으로 맞지만 카드 높이, 삭제 위치, 전략 구성 표 / 폼 반복, 모니터 시나리오 의미가 상용 운영 UI처럼 정돈되어 보이지 않는다.

이번 task는 저장 경계나 monitoring logic을 바꾸지 않고, 사용자가 바로 이해하고 테스트할 수 있도록 portfolio-first 화면 계층을 제품형 UI로 다듬는다.

## Scope

- `1. 나의 포트폴리오`: fixed-height portfolio shelf, active state, delete action relocation.
- `2. 포트폴리오 상세 / 전략 구성`: selected portfolio command band, compact strategy add panel, strategy board cards/rows.
- `3. 모니터 시나리오`: portfolio-wide scenario cockpit wording, partial-run state, strategy result summary and rebalance details.

## Out Of Scope

- `4. Monitoring Signals`, continuity, provider evidence, deployment readiness, allocation evidence redesign.
- DB schema, Final Review decision rows, saved setup file rewrite, provider fetch, broker/account/order/live approval/auto rebalance.

## Stop Condition

- Browser QA shows the 1~3 flow with fixed portfolio cards, less visual clutter in strategy setup, and an explicit portfolio-level scenario interpretation.
- Existing service contracts and syntax checks pass.
