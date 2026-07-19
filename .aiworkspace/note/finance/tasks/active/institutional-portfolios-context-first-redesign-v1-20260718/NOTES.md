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

## Superseded Code Facts

- manager search result limit: 24.
- allocation top list visible: 6.
- performance row visible: 8.
- change group visible: 5 per group.
- sector visible: 8.
- full holdings React visible: first 80 only, without visible truncation explanation.
- primary React surface has no direct ticker / issuer / CUSIP input; the old Streamlit reverse lookup remains inside fallback detail.

위 항목은 1차 audit 당시 사실이다. 현재 v2는 전체 holdings row를 client-side 50개 page로 탐색하고, ticker / issuer / CUSIP 직접 검색을 primary React surface에서 제공한다.

## Verified V2 Behavior

- `institutional_portfolios_workbench_v2`가 context summary, count / weight / performance coverage, full holdings explorer, explicit security search를 제공한다.
- comparison은 `previous_report_period`가 있을 때만 가능하며, 없으면 change groups는 빈 dict다.
- unresolved row는 issuer / CUSIP / mapping badge를 유지하고 가격 차트 / 가격 수집 action을 열지 않는다.
- mapped row 또는 직접 종목 검색은 기존 DB-backed OHLCV chart와 holder list로 연결된다.
- Streamlit은 manager / security / popularity / price event만 처리하고 React local search / filter / sort / page state는 iframe 내부 상태다.

## Actual DB QA On 2026-07-18

| Manager | Total / Explorer Rows | Mapped | Unmapped | Mapped Weight | Performance Coverage | Comparison |
|---|---:|---:|---:|---:|---:|---|
| Berkshire | 29 / 29 | 19 | 10 | 98.6072% | 98.6073% | unavailable |
| Bridgewater | 993 / 993 | 86 | 907 | 21.0227% | 21.0228% | unavailable |
| Duquesne | 70 / 70 | 5 | 65 | 6.6579% | 6.6579% | unavailable |

## Product Boundary

- Institutional Portfolios remains a user-facing read-only research surface.
- 13F delay, no shorts / cash / full derivatives / hedge structure, confidential treatment, amendments, and mapping limitations stay visible.
- Context summary is descriptive evidence, not portfolio quality scoring or recommendation.
