# Plan

## Purpose

Market Movers Redesign V2 6차는 Coverage/Data Quality UX를 compact trust strip과 empty state hint 중심으로 정리한다.

## Scope

- 기존 `build_market_movers_coverage_trust_model`을 유지한다.
- 메인 화면에는 현재 결과 신뢰도, 핵심 수치, 다음 action을 compact strip으로 표시한다.
- grouped/raw diagnostics는 `Coverage trust detail` expander 안에 둔다.
- NASDAQ No Universe empty state에는 현재 trust hint를 함께 보여준다.
- 새 provider, 새 DB schema, run/job dashboard, operations monitoring signal은 추가하지 않는다.

## Completion Criteria

- SP500 Daily/Weekly에서 compact data trust strip이 보인다.
- NASDAQ No Universe에서 empty state가 신뢰 상태와 다음 action을 분명히 보여준다.
- raw diagnostics는 expander 내부에 남는다.
- 좁은 화면에서 trust strip과 empty state가 깨지지 않는다.
- 공통 검증, Browser QA, coherent commit을 완료한다.
