# Overview Market Context Turnaround Stage Semantics Fix V1 Notes

Last Updated: 2026-07-16

## Decisions

- 6개 요소 rail 컨셉과 independent milestone 계약은 유지한다.
- threshold를 낮추지 않고 상태 표현만 실제 의미에 맞춘다.
- already-positive company는 transition NOT_MET과 시각적으로 구분한다.
- PER 상대 고평가/저평가는 operating milestone과 독립이다.
- 새 schema, provider fetch, 자동 수집, 진단 panel은 추가하지 않는다.

## Root Cause

- DB AAPL EPS unit: `USD per share`
- turnaround duration allowlist: `USD`, `USD/share`, `USD/shares`, `shares`
- query boundary에서 EPS rows 0건이 되어 current TTM EPS와 PER readiness가 null/NOT_MET으로 내려갔다.
