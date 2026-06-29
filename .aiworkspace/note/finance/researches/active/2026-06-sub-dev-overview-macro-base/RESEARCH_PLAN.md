# Sub Dev Overview Macro Data Visualization Base Research Plan

Status: Active
Last Updated: 2026-06-08

## Why This Work Exists

Define how the sub-dev worktree should audit and improve Overview, Ingestion, and Operations data analysis / visualization surfaces before future implementation sessions.

이 리서치는 지침 변경이 아니다. 현재 `sub-dev` 세션을 어떤 방식으로 활용하면 좋은지, 그리고 Overview / Ingestion / Operations 쪽 데이터 분석과 시각화 개선을 어느 순서로 검토하면 좋은지 정리하는 베이스 문서다.

## Research Questions

| Question | Decision this supports |
| --- | --- |
| What exists in the current finance project? | Identify real product strengths, gaps, and constraints. |
| What do comparable products or patterns show? | Separate durable patterns from copied features. |
| Which opportunities are worth considering? | Build a narrow, evidence-backed candidate list. |
| What should happen next? | Distinguish immediate build candidates from roadmap options and parking-lot ideas. |

## Scope

Include:

- current Overview / Ingestion / Operations product audit
- macro / market context / data-health visualization benchmark
- recurring UI / workflow / data-evidence patterns
- future feature candidates for separate implementation sessions

Exclude:

- direct code implementation
- durable roadmap or AGENTS.md changes without user approval
- changes owned by `main-dev` or `backtest-dev`
- live trading, broker order, broker account sync, auto rebalance, or automatic investment recommendation

## Method

1. Audit local product structure and workflow.
2. Research current external benchmarks from primary sources.
3. Extract reusable patterns and conflicts with project boundaries.
4. Score feature candidates by impact, effort, risk, confidence, and fit.
5. Write a recommendation with immediate, next, later, and parking-lot scope.

## Tentative Development Roadmap

| Stage | Purpose | Likely files / screens | Completion condition | Connection to next stage |
| --- | --- | --- | --- | --- |
| 1차. Overview Macro Context Cockpit | 현재 Overview가 가진 futures / sentiment / events / data health를 첫 화면에서 시장 상태와 신뢰도 중심으로 읽게 한다. | `app/web/overview_dashboard.py`, `app/web/overview_dashboard_helpers.py`, `app/services/*overview*`, `app/services/futures_macro_thermometer.py` | 새 데이터 수집 없이 summary-first market context가 보이고, context-only boundary가 유지된다. | 2차에서 stale / missing 상태를 Ingestion action으로 연결한다. |
| 2차. Data Health -> Ingestion Handoff | Overview Data Health와 Ingestion 실행 콘솔 사이의 refresh 우선순위 / 이동 경로를 분명하게 만든다. | `app/web/overview_dashboard.py`, `app/web/ingestion_console.py`, `app/jobs/overview_actions.py`, `app/services/overview_market_intelligence.py` | 사용자가 어떤 데이터가 오래됐고 어떤 수집을 실행해야 하는지 바로 알 수 있다. | 3차에서 시각화와 분석 depth를 늘린다. |
| 3차. Market Breadth / Macro Visualization | heatmap, breadth, calendar quality lane, macro regime explanation을 추가해 분석 밀도를 높인다. | Overview UI / services, possible chart helpers | 새 visualization이 DB-backed이고 source / freshness / coverage를 숨기지 않는다. | 4차에서 retention / provider hardening 정책을 결정한다. |
| 4차. Source Retention / Provider Hardening | Why It Moved compact metadata retention, futures provider hardening, macro source policy를 별도 승인 단위로 검토한다. | DB schema / collectors / loaders only after approval | 저장 정책, freshness, replay, provider terms가 명확하다. | 승인된 항목만 phase / task로 전환한다. |

이번 리서치는 위 roadmap 중 1차~4차 후보를 정리하는 단계이며, 실제 구현은 하지 않는다.

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
