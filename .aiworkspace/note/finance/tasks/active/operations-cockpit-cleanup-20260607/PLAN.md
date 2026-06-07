# Operations Cockpit Cleanup 2026-06-07

## 이걸 하는 이유?

Operations Overview V2의 1차 작업은 사용자 화면에서 archive / development-history 흔적을 걷어내고, Operations를 선정 이후 portfolio monitoring과 system/data health를 확인하는 cockpit으로 읽히게 만드는 것이다.

## Scope

- `Operations > Operations Overview` 사용자-facing copy와 섹션 위계를 정리한다.
- Archive / development-history expander, decision table, roadmap copy를 운영 화면에서 제거한다.
- Portfolio Monitoring / System Data Health primary lane과 disabled live-trading boundary는 유지한다.
- Registry / saved JSONL, archive data, hidden compatibility helper는 수정하지 않는다.

## Out Of Scope

- Portfolio-first status summary V2 지표 확장.
- Evidence health mini strip.
- Today review queue 재정렬.
- Archive data/helper 삭제.
- Broker sync, order, live approval, auto rebalance.

## Development Steps

1. RED: Operations Overview read model과 render source가 archive / development-history artifact를 노출하지 않는 테스트를 추가한다.
2. GREEN: `app/web/operations_overview.py`에서 stage roadmap / surface audit user-facing model과 renderer를 제거하고 caption을 운영 cockpit 중심으로 정리한다.
3. Docs: Operations Overview 책임 설명에서 removed archive decision 중심 문구를 cleanup 이후 상태로 정렬한다.
4. QA: focused unittest, py_compile, diff check, UI boundary/hygiene check, Browser QA를 실행한다.
5. Commit: generated artifact와 local `.DS_Store`는 제외하고 coherent implementation unit으로 커밋한다.
