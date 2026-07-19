# US Economic Cycle Regime Forecast Research Plan

Status: Approved for Implementation Planning
Last Updated: 2026-07-16

## Why This Work Exists

Validate a four-phase U.S. economic-cycle model, probabilistic one- and two-month transition forecasts, and a Market Context visualization design grounded in official real-time data and academic research.

## Research Questions

| Question | Decision this supports |
| --- | --- |
| How should the user's four phases be defined without confusing market prices with the real economy? | Establish the product's phase semantics and evidence hierarchy. |
| Which indicators can identify the current phase in real time? | Select coincident, leading, inflation/policy, and financial-condition evidence. |
| How should one- and two-month forecasts be generated and validated? | Choose an interpretable probabilistic model and a rolling vintage backtest. |
| How should past, present, and future be shown in Market Context? | Choose a visual hierarchy that makes phase, trajectory, uncertainty, and evidence readable. |
| What exists in the current finance project? | Identify code, DB, ingestion, and UI strengths, gaps, and constraints. |

## Scope

Include:

- current finance project audit
- academic business-cycle and nowcasting methods
- current official U.S. indicator and real-time data products
- comparable visualization and evidence patterns
- recurring UI/workflow/data/evidence patterns
- feature candidates and recommendation

Exclude:

- direct implementation
- roadmap changes without human approval
- an uncalibrated numerical forecast presented as a result
- live trading, broker order, or auto rebalance unless the product boundary changes

## Method

1. Audit local product structure and workflow.
2. Separate real-economy cycle evidence from market-implied context in the study note.
3. Research current primary sources and academic methods.
4. Extract reusable data, modeling, validation, and visual patterns.
5. Score feature candidates by impact, effort, risk, confidence, and fit.
6. Write a recommendation with immediate, next, later, and parking-lot scope.

## Outputs

| File | Role |
| --- | --- |
| `CURRENT_PROJECT_AUDIT.md` | Current finance product facts, strengths, weaknesses, boundaries. |
| `BENCHMARKS.md` | Academic and official benchmark notes with evidence labels. |
| `UI_PATTERNS.md` | Recurring workflow and interface patterns. |
| `FEATURE_CANDIDATES.md` | Candidate features and prioritization. |
| `RECOMMENDATION.md` | Final recommendation and handoff. |
| `SOURCES.md` | Local and web sources with access dates. |
| `RISKS.md` | Open questions, evidence limits, and follow-up risks. |

## Approval Result

The user approved the hybrid factor/transition/calibration engine, the clock+ribbon C layout, the point-in-time validation contract, and the five-stage delivery roadmap on 2026-07-16. The implementation boundary is recorded in `docs/superpowers/specs/2026-07-16-us-economic-cycle-regime-forecast-design.md`; no implementation is part of this research bundle.
