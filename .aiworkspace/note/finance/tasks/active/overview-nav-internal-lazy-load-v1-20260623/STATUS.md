# Overview Nav Internal Lazy Load V1 Status

## 2026-06-23

- User reported that the previous custom tab behaved like link navigation / new-window navigation instead of an in-browser tab switch.
- Root cause identified: previous nav rendered `<a href="?overview_tab=...">` anchors inside custom HTML.
- Startup load root cause identified: default Market Context immediately calls `load_overview_macro_context_cockpit`, which loads movers, sector leadership, futures macro, sentiment, events, collection ops, and historical analog.
- User supplied the final tab visual target: plain text tabs with a thin baseline and red active underline.
- Implementation status: internal `st.pills` selector is in place, anchor rendering is removed, and the default Market Context body is deferred behind `시장 맥락 불러오기`.
- Browser QA status: PASS. Fresh entry renders the lazy gate before the heavy Market Context body. Market Movers switching stays in the same browser tab and URL.
- Current status: implementation, Browser QA, and final verification complete.

## Roadmap Position

- 1차: remove unclear Overview primary tabs: completed in `overview-primary-tab-soft-remove-v1-20260623`.
- 2차: visual nav polish: completed but anchor implementation was wrong in `overview-primary-nav-pill-v1-20260623`.
- 2차 follow-up: this task fixes nav behavior and first-load lazy gating.
- 3차 candidate: Market Context old source label absorption remains optional.
