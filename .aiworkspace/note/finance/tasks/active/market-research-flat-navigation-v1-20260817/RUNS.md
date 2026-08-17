# Runs

- Baseline Python: `54 passed` across focused navigation/economic-cycle tests.
- TDD RED: six navigation failures for missing `inflation-policy`/old label; bridge `TypeError`; two React failures for the nested tablist and ignored selected view; two CSS contract failures for the mobile 2-column grid.
- TDD GREEN: navigation `26 passed`; economic bridge focused `2 passed`; navigation Vitest `5 passed`; economic-cycle Vitest `41 passed`.
- Missing inflation payload regression: the selected 물가·정책 surface now stays in place and shows its own unavailable state instead of falling back to 경기 국면.
- Typecheck: both modified React components exited 0.
- Production build: market navigation and economic-cycle Vite bundles exited 0.
- Focused combined Python verification: `56 passed`, three upstream edgartools deprecation warnings.
- Overview integration contract class: `201 passed`, three upstream edgartools deprecation warnings; stale 7-view, direct renderer and mobile 2-column assertions were updated for the flat 8-view contract.
- Browser QA: `economic-cycle` and `inflation-policy` URL transitions opened the matching body; 360px rail was 51px high and scroll-contained; 736px fit without horizontal overflow; console warning/error list was empty.
- Generated QA screenshot: `market-research-flat-navigation-mobile-qa.png` (unstaged artifact).
- Finance refinement hygiene: passed; the pre-existing registry and generated run history remained unstaged.
- Independent staged-diff review: fixed the mobile direct-route active-tab visibility gap with overflow-aware `scrollIntoView`, and corrected the remaining canonical 7-view documentation reference to 8-view.
- Mobile desktop-parity follow-up RED: Streamlit/React CSS contracts and the no-force-scroll React test failed against the mobile-only swipe rail.
- Mobile desktop-parity follow-up GREEN: mobile-only family/view overrides and overflow correction were removed; navigation Vitest, typecheck and production build passed.
- 360px Browser QA: family grid retained desktop `max-content` columns and 26px gap; view rail retained desktop 999px pill, 7px gap and `flex-wrap: wrap`; page and rail scroll width matched client width; browser warnings/errors were empty.
- Generated follow-up QA screenshot: `market-research-mobile-desktop-parity-qa.png` (unstaged artifact).
