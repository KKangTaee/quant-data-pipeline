# Final Review Decision Workspace Redesign Research Plan

Status: Design Approved — implementation plan pending user review
Last Updated: 2026-07-16

## Why This Work Exists

Final Review가 Level2 검증 계약과 투자 후보의 최종 판단을 혼합하는 문제를 진단하고, Workspace Overview 시장 맥락 수준의 명확한 질문·해석·근거·행동 구조로 재설계한다.

## Research Questions

| Question | Decision this supports |
| --- | --- |
| What exists in the current finance project? | Identify real product strengths, gaps, and constraints. |
| What do comparable products or patterns show? | Separate durable patterns from copied features. |
| Which opportunities are worth considering? | Build a narrow, evidence-backed candidate list. |
| What should happen next? | Distinguish immediate build candidates from roadmap options and parking-lot ideas. |

Final Review 전용 질문:

| Question | Decision this supports |
| --- | --- |
| Final Review가 사용자의 어떤 결정을 끝내야 하는가? | 화면의 단일 primary question과 저장 route를 고정한다. |
| 포트폴리오 자체의 강점과 약점은 어떤 관측값에서 만들어지는가? | 검증 준비도와 투자 특성을 분리한 read model을 정의한다. |
| Level2 종결 근거 중 무엇을 Final Review에 다시 보여줘야 하는가? | stage ownership과 disclosure 깊이를 정한다. |
| Overview > 시장 맥락의 성공 패턴을 어디까지 재사용할 수 있는가? | Streamlit shell과 React report의 정보·시각 체계를 통일한다. |

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
- Final Review에서 provider fetch, replay, DB ingestion 또는 Level2 재검증 실행
- 승인 전 구현 및 기존 roadmap 변경

## Method

1. Audit local product structure and workflow.
2. Compare the running Final Review with the internal `Overview > 시장 맥락` reference surface.
3. Confirm the primary user decision and product boundary with the user.
4. Compare two or three information-architecture approaches and their trade-offs.
5. Research external benchmarks only where the internal evidence cannot settle a design choice.
6. Write the approved recommendation, phased build scope, and acceptance criteria.

## Outputs

| File | Role |
| --- | --- |
| `CURRENT_PROJECT_AUDIT.md` | Current finance product facts, strengths, weaknesses, boundaries. |
| `BENCHMARKS.md` | Internal/external benchmark notes with evidence labels. |
| `UI_PATTERNS.md` | Recurring workflow and interface patterns. |
| `FEATURE_CANDIDATES.md` | Candidate features and prioritization. |
| `RECOMMENDATION.md` | Final recommendation and handoff. |
| `SOURCES.md` | Local and web sources with access dates. |
| `RISKS.md` | Open questions, evidence limits, and follow-up risks. |
