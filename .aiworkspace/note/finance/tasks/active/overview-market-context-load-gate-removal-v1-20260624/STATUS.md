# Overview Market Context Load Gate Removal V1 Status

## 2026-06-24

- User rejected the extra `시장 맥락 불러오기` step and asked to restore the previous immediate Market Context behavior.
- Removed the Overview Market Context lazy-load gate from the render path.
- Kept the internal `st.pills` text-tab underline selector, so tab switching remains in the current browser tab and no tab anchors are rendered.
- Root-cause measurement completed: cold `load_overview_macro_context_cockpit` took about 15.8s in local timing, mostly from futures macro validation, sector leadership, market movers, and historical analog reads.
- Current status: implementation, load-path analysis, tests, and Browser QA complete.
