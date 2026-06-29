# Risks

Status: Active
Last Updated: 2026-06-29 KST

## Product Risks

- Removing guide text can accidentally hide important boundaries. Mitigation: keep boundaries in Reference/docs and use compact action-linked warnings only where needed.
- Making Practical Validation handoff more permissive can admit weak candidates. Mitigation: hard-block only source-contract failures, but preserve review warnings and let Practical Validation gate decide.
- Strategy maturity chips can drift from actual runtime support. Mitigation: centralize mapping in Streamlit-free service and test it.
- Removing `전략 개발 참고` from default view can reduce discoverability for internal research. Mitigation: keep research docs/reports and optional non-default route if approved.

## Data / Validation Risks

- Point-in-time and filing lag assumptions remain especially important for strict annual / quarterly factor strategies.
- Strict quarterly must remain prototype until replay / PIT / validation compatibility is explicitly approved.
- Risk-On Momentum must remain research lane until daily swing governance exists.
- Price freshness warning must not be hidden by UI simplification.
- Provider / FRED direct fetch must stay out of Backtest Analysis.

## Implementation Risks

- `backtest_result_display.py` is large and shared by Single Strategy, Compare, saved replay, and history contexts. Phase 2 should use small read-model helpers and focused tests.
- Existing tests may assert Reference guide visibility. If so, update tests to match approved product decision.
- Browser QA needs an available DB/sample state. If a real run cannot be produced, use existing session/history payload where possible and report the gap.

## Open Questions

1. Should `전략 개발 참고` be physically removed from Backtest Analysis in 1차, or only made developer-only / Reference-only first?
2. Should `promotion_decision=hold` block Practical Validation handoff, or merely show "보낼 수 있지만 확인 필요"?
3. Should strict quarterly prototype be hard-blocked from Practical Validation until a dedicated maturation task?
4. Should Risk-On Momentum 5D be entirely blocked from Practical Validation, or allowed only through a future daily swing validation module?
5. Is the next implementation session approved for only 1차, or can it continue to 2차 after QA?
