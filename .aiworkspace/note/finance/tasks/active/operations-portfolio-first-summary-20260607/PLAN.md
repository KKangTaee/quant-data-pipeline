# Operations Portfolio First Summary 2026-06-07

## 이걸 하는 이유?

Operations Overview V2 2차는 운영자가 `Operations Console`에 들어왔을 때 archive / 개발 이력이 아니라 현재 portfolio monitoring 상태를 먼저 판단하게 만드는 작업이다.

## Scope

- `Operations > Operations Overview` 상단에 portfolio-first status summary를 추가한다.
- 저장된 selected dashboard / dashboard portfolio setup에서 계산 가능한 stale scenario, blocked / missing / open review, target snapshot, next review 기준을 표시한다.
- Today action queue, Portfolio Monitoring / System Data Health lane, disabled live boundary는 유지한다.
- Registry / saved JSONL은 읽기만 하고 재작성하지 않는다.

## Out Of Scope

- Evidence health mini strip 상세화.
- Today review queue 재정렬.
- Portfolio Monitoring 화면 자체의 scenario execution UX 변경.
- Archive data/helper 삭제.
- Broker sync, order, live approval, auto rebalance.

## Development Steps

1. RED: Operations Overview read model에 `portfolio_summary` 계약을 추가하고, 화면 source에서 summary가 queue보다 먼저 렌더되는 테스트를 작성한다.
2. GREEN: `app/web/operations_overview.py`에서 Streamlit-free portfolio summary builder와 renderer를 구현한다.
3. Docs: Operations Overview V2 2차 상태를 roadmap / product map / flow docs / task logs에 반영한다.
4. QA: focused unittest, py_compile, diff check, UI boundary/hygiene check, Browser QA를 실행한다.
5. Commit: generated artifact와 local `.DS_Store`는 제외하고 coherent implementation unit으로 커밋한다.
