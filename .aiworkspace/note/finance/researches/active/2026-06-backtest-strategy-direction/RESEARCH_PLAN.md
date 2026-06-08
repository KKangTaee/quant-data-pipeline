# Backtest Strategy Direction Research Plan

Status: Active
Last Verified: 2026-06-08

## Why This Work Exists

Backtest 전략군의 현재 성숙도, 장단점, 약점, 다음 개발 우선순위를 정리하고 3차 구현 세션으로 넘길 handoff를 만든다.

## Session Roadmap

| 차수 | 상태 | 목적 | 산출물 | 다음 차수와의 연결 |
| --- | --- | --- | --- | --- |
| 1차 | Complete | 현재 Backtest 전략군, 제품 연결 범위, 대표 장단점 파악 | 채팅 분석과 local source map | 2차 문서화의 원재료 |
| 2차 | Current | 전략 방향성, 약점 matrix, 우선순위, 다음 세션 개발 guide 고정 | 이 research bundle | 3차 구현 scope 승인 / 새 세션 handoff |
| 3차 | Deferred to new session | 승인된 1개 개발 scope 구현 | task / phase docs, code, tests, docs sync | 구현 완료 후 통합 / QA |

이번 2차에서 하지 않는 일:

- strategy code, runtime, Streamlit UI 수정
- registry / saved setup / run history / generated artifact rewrite
- `docs/ROADMAP.md` 확정 변경
- live approval, broker order, auto rebalance, account sync 설계

## Research Questions

| Question | Decision this supports |
| --- | --- |
| 현재 Backtest에 어떤 전략이 있는가? | 실제 개발 가능한 전략 family와 연구용 / 후보용 경계를 구분한다. |
| 각 전략의 강점과 약점은 무엇인가? | 다음 개발이 성과 chase가 아니라 evidence gap 보강이 되게 한다. |
| 어떤 전략을 먼저 제품 흐름으로 고정해야 하는가? | 3차 구현 세션의 첫 scope를 좁힌다. |
| 무엇을 새 세션으로 넘겨야 하는가? | 구현 세션이 분석을 반복하지 않고 바로 task를 열 수 있게 한다. |

## Scope

Include:

- current Backtest strategy inventory
- strategy maturity and workflow connection map
- internal benchmark evidence from existing strategy reports
- weakness matrix and improvement direction
- feature candidates and next-session handoff

Exclude:

- direct implementation
- roadmap changes without human approval
- live trading, broker order, or auto rebalance unless the product boundary changes
- external commercial product benchmark research; this can be opened later if the user wants a broader market comparison

## Method

1. Audit local product structure and workflow.
2. Compare current strategies against existing internal strategy reports.
3. Separate implemented facts from product-direction hypotheses.
4. Score feature candidates by impact, effort, risk, confidence, and fit.
5. Write a recommendation with immediate, next, later, and parking-lot scope.

## Outputs

| File | Role |
| --- | --- |
| `CURRENT_PROJECT_AUDIT.md` | Current finance product facts, strengths, weaknesses, boundaries. |
| `STRATEGY_INVENTORY.md` | Strategy list, execution path, maturity, current evidence state. |
| `WEAKNESS_MATRIX.md` | Strategy-specific strengths, weaknesses, risks, and improvement guide. |
| `BENCHMARKS.md` | Internal benchmark / strategy report baseline with evidence labels. |
| `UI_PATTERNS.md` | Recurring workflow and interface patterns. |
| `FEATURE_CANDIDATES.md` | Candidate features and prioritization. |
| `RECOMMENDATION.md` | Final recommendation and handoff. |
| `NEXT_SESSION_HANDOFF.md` | Ready-to-use 3차 implementation session start guide. |
| `SOURCES.md` | Local and web sources with access dates. |
| `RISKS.md` | Open questions, evidence limits, and follow-up risks. |
