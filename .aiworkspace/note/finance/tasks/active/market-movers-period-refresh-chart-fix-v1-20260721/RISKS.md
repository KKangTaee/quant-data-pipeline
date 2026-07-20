# Risks

- Bounded overlap reduces each symbol's requested history, but provider fetch still covers the full selected universe. The actual S&P 500 weekly refresh took 138.11 seconds for 503 symbols, so the user can still perceive a long blocking action.
- Monthly bounded behavior is covered by calendar-boundary and service contract tests; a second 503-symbol live Monthly provider run was not performed.
- Browser automation confirmed the financial scroller has a 2,260px content width inside a 702px viewport and the pointer-drag handlers remain in the built component. The automation backend did not change `scrollLeft` with its synthetic drag gesture, so physical mouse drag remains a small manual QA gap.
- New listings remain eligible for shorter periods when their first stored price precedes that period's required start; they are excluded only from periods whose start predates their first stored price.
- Sector conditional outlook remains out of this task and must not be published without historical/OOS evidence.
