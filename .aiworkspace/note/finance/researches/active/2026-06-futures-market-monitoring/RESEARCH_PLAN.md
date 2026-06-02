# Futures Market Monitoring Research Plan

## Why This Work Exists

선물장 OHLCV와 개장 전 급변 신호를 Overview/운영툴에서 read-only로 확인하기 위한 데이터 소스, 수집 cadence, 차트 UX, 구현 경계를 조사한다.

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
