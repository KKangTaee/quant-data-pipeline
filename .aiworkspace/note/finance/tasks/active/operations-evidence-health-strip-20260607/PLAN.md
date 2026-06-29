# Operations Evidence Health Strip 2026-06-07

## 이걸 하는 이유?

Operations Overview V2 3차는 Portfolio Monitoring Status summary 아래에서 운영 근거의 건강 상태를 한 줄로 확인하게 만드는 작업이다.

## Scope

- `Operations > Operations Overview`에 evidence health mini strip을 추가한다.
- mini strip은 이미 로드된 selected dashboard / monitoring portfolio setup / run history payload만 읽는다.
- scenario freshness, selected evidence readiness, open review, system run health를 compact하게 표시한다.
- Today action queue, Portfolio Monitoring / System Data Health lane, disabled live-trading boundary는 유지한다.

## Out Of Scope

- Provider / holdings / exposure DB evidence를 Overview 입구에서 새로 조회하지 않는다.
- Today review queue 재정렬.
- Portfolio Monitoring scenario execution UX 변경.
- Archive data/helper 삭제.
- Broker sync, order, live approval, auto rebalance.

## Development Steps

1. RED: Operations Overview read model에 `evidence_health` 계약을 추가하고, 화면 source에서 evidence strip이 queue보다 먼저 렌더되는 테스트를 작성한다.
2. GREEN: `app/web/operations_overview.py`에서 Streamlit-free evidence health builder와 renderer를 구현한다.
3. Docs: Operations Overview V2 3차 상태를 roadmap / product map / flow docs / task logs에 반영한다.
4. QA: focused unittest, py_compile, diff check, UI boundary/hygiene check, Browser QA를 실행한다.
5. Commit: generated artifact와 local `.DS_Store`는 제외하고 coherent implementation unit으로 커밋한다.
