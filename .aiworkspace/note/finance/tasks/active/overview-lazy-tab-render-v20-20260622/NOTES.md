# Notes

- `st.tabs` eagerly runs all tab bodies, which is the main cause of initial Overview load feeling heavy.
- Timed cold-ish checks showed large costs around Market Context aggregate, Sector / Industry leadership, Market Movers, and futures macro snapshot.
- The desired behavior is not to remove work, but to run it when the user opens the corresponding tab.
- The selector keeps `Market Context` as fallback for missing / unknown session state so first entry stays focused on the market context surface.
- The top-level render function still renders the market-session banner before the selected deep tab. This banner is intentionally kept global because it gives the user the current market-session basis for the whole Overview screen.
