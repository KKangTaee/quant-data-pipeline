# Overview Market Interest Evidence V1 Notes

## 2026-07-08 Context Read

- Existing Market Movers selected-symbol fragment lives in `app/web/overview/market_movers_helpers.py`.
- Existing visual component body lives in `app/web/overview/components/market_movers.py`.
- Existing Why It Moved metadata and selected-symbol research snapshot live in `app/services/overview/why_it_moved.py`.
- Existing selected-symbol EDGAR statement refresh facade lives in `app/jobs/overview_actions.py`.
- Existing research recommends source categories: official durable source, session-only public lead, external research link.

## Design Decision

V1 will not add 13F DB schema. It will show SEC 13F as an official durable candidate with caveats and source links, because selected-symbol 13F lookup needs CUSIP-symbol mapping and quarter comparison design.

## 2026-07-08 Implementation Notes

- Added `app/services/overview/market_interest.py` as a Streamlit-free read model for selected-symbol market-interest evidence.
- Market Movers selected-symbol investigation now has a manual `시장 관심 근거 확인` action and `시장 관심` tab.
- Analyst / target-change sources stay outbound links or session-only leads. Existing news / SEC metadata feeds the conservative `뉴스/공시 촉매` status when the user has already fetched it.
- 13F is shown as delayed institutional context with official SEC links and caveats, not as current institutional buying or a recommendation.
