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

## Implemented Meaning

- turnaround duration reader는 canonical `USD per share`와 기존 compatibility unit을 함께 허용한다.
- backend milestone status/threshold는 유지하고, operating evidence에 현재 margin·최근 YoY delta·최근 threshold 충족 횟수를 추가했다.
- `ESTABLISHED`는 React display state일 뿐 backend milestone이나 history status로 저장하지 않는다.
- AAPL의 expected rail은 revenue/GP `MET`, operating `ESTABLISHED`, OCF `MET`, FCF `MET`, EPS `ESTABLISHED`, PER `MET`다.
- RIVN처럼 음수 TTM EPS인 종목은 `EPS 양전 신호`와 `PER 적용 가능`이 독립적인 미확인 상태로 남는다.
