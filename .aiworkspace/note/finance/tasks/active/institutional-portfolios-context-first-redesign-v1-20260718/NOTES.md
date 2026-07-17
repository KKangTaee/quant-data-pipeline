# Institutional Portfolios Context-First Redesign V1 Notes

## Decisions

- Default protagonist: selected manager portfolio context.
- Manager discovery: secondary switcher / search.
- Preserve: allocation donut, interactive price chart, portfolio/security two-tier semantics, SEC source and caveats.
- Change: dashboard-first ordering to context-first reading flow.
- Correct before polish: silent holdings truncation, direct security search, mapping coverage visibility, previous-quarter state.
- Do not add a run/job/row diagnostic panel as the improvement output.

## Actual Evidence Checked On 2026-07-18

| Manager | Logical Holdings | Mapped Count | Mapped Weight | Hidden After Current UI 80 Cut | Previous Filing |
|---|---:|---:|---:|---:|---|
| Berkshire | 29 | 19 | 98.6% | 0 | none |
| Pershing | 11 | 4 | 33.4% | 0 | none |
| Appaloosa | 31 | 6 | 30.0% | 0 | none |
| Baupost | 22 | 3 | 24.2% | 0 | none |
| Duquesne | 70 | 5 | 6.7% | 0 | none |
| Bridgewater | 993 | 86 | 21.0% | 913 | none |
| Third Point | 33 | 7 | 29.5% | 0 | none |
| Tiger Global | 54 | 7 | 42.3% | 0 | none |

Bridgewater current top 80 rows represent 73.5% of reported value, so both count visibility and value coverage must be shown.

## Code Facts

- manager search result limit: 24.
- allocation top list visible: 6.
- performance row visible: 8.
- change group visible: 5 per group.
- sector visible: 8.
- full holdings React visible: first 80 only, without visible truncation explanation.
- primary React surface has no direct ticker / issuer / CUSIP input; the old Streamlit reverse lookup remains inside fallback detail.

## Product Boundary

- Institutional Portfolios remains a user-facing read-only research surface.
- 13F delay, no shorts / cash / full derivatives / hedge structure, confidential treatment, amendments, and mapping limitations stay visible.
- Context summary is descriptive evidence, not portfolio quality scoring or recommendation.
