# Investable Workflow Gap Analysis Research Plan

Last Updated: 2026-06-08

## Why This Work Exists

현재 Backtest -> Practical Validation -> Final Review -> Selected Dashboard 흐름을 기준으로 실전 투자 가능성 판단에 부족한 약점과 상용 제품 대비 개선 방향을 정리한다.

2026-06-08 refresh는 기존 Phase 0 연구를 새로 승인된 roadmap으로 바꾸기 위한 작업이 아니다.
현재 `main-dev` 세션이 제품 방향 리서치 세션으로 어떻게 활용될지 정리하고,
`backtest-dev`의 전략 심층 분석 / 개선 작업과 분리된 제품 흐름 감사, 벤치마크, 개발 후보 선별 기준을 갱신하기 위한 baseline이다.

## Research Questions

| Question | Decision this supports |
| --- | --- |
| What exists in the current finance project? | Identify real product strengths, gaps, and constraints. |
| What do comparable products or patterns show? | Separate durable patterns from copied features. |
| Which opportunities are worth considering? | Build a narrow, evidence-backed candidate list. |
| What should happen next? | Distinguish immediate build candidates from roadmap options and parking-lot ideas. |

## Scope

Include:

- current finance project audit
- comparable product, service, framework, or workflow benchmarks
- recurring UI/workflow/data/evidence patterns
- feature candidates and recommendation

Exclude:

- direct implementation
- roadmap changes without human approval
- live trading, broker order, or auto rebalance unless the product boundary changes

## Method

1. Audit local product structure and workflow.
2. Research current external benchmarks from primary sources.
3. Extract reusable patterns and conflicts with project boundaries.
4. Score feature candidates by impact, effort, risk, confidence, and fit.
5. Write a recommendation with immediate, next, later, and parking-lot scope.

## Outputs

| File | Role |
| --- | --- |
| `CURRENT_PROJECT_AUDIT.md` | Current finance product facts, strengths, weaknesses, boundaries. |
| `BENCHMARKS.md` | External benchmark notes with evidence labels. |
| `UI_PATTERNS.md` | Recurring workflow and interface patterns. |
| `FEATURE_CANDIDATES.md` | Candidate features and prioritization. |
| `RECOMMENDATION.md` | Final recommendation and handoff. |
| `SOURCES.md` | Local and web sources with access dates. |
| `RISKS.md` | Open questions, evidence limits, and follow-up risks. |
