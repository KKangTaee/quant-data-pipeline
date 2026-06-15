# Risks

Status: Draft
Last Updated: 2026-06-15

## Research Risks

- Public product pages may be marketing-heavy; treat layout conclusions as pattern evidence, not proof of exact implementation.
- TradingView-style heatmap can make weak local sector ETF coverage more obvious.
- Highly visual layouts can accidentally imply trade signals if color and copy are too aggressive.
- Streamlit can support the first pass, but true linked widgets / customizable workspace patterns may push toward future frontend platform work.

## Product Boundary Risks

- Do not turn market context into Practical Validation PASS / BLOCKER.
- Do not make data refresh diagnostics the hero surface.
- Do not introduce provider fetch, schema changes, registry writes, saved setup writes, broker actions, or auto rebalance.
