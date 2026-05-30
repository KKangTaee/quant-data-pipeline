# Notes

- Trend Groups should preserve user intent inside the Sector / Industry tab. Switching between Sector and Industry can use separate remembered selections.
- Line trend remains useful for exact path, but heatmap and latest-delta views should make rise/fall direction easier to scan.
- Positive Group Detail should reuse Market Movers bar semantics: sector-colored positive bars, danger red for negative values, and high-contrast previous-return markers with halo.
- Trend Groups are remembered by `Group` mode (`sector` / `industry`) instead of coverage / period / top-N / min-symbol controls. Invalid selections are filtered when the current universe no longer has that group.
- `Latest Delta` compares the latest selected trend window against the immediately previous trend window, so it is a directional acceleration/deceleration hint, not a forward prediction.
- Streamlit warned when session state was set while also passing `default` to the multiselect. The final implementation only passes `default` on first widget creation and otherwise lets the widget key own state.
- Heatmap readability is better with compact horizons: Daily 1M, Weekly 3M, Monthly 12M. Daily 3M was too dense for the current chart cell size.
