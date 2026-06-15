# UI Patterns

Status: Draft
Last Updated: 2026-06-15

## Summary

The core answer to the user's question is: no, cards are not required. The current card habit came from accumulated Streamlit rendering patterns and repeated feature additions, not from a true product need. Better benchmark-aligned options are monitor/tape rows, narrative brief with evidence rail, or heatmap/timeline board.

## Pattern Catalog

### Pattern A: Market Brief Tape

- Seen in: Bloomberg monitor idea, Koyfin custom/market dashboards.
- User problem: user wants the answer and the supporting facts quickly without visually equal card blocks.
- Interaction shape: one headline, one status strip, then dense rows: movement, breadth, macro, events, data state, analog.
- Data required: existing Market Context read model.
- Why it matters: highest scanability, lowest implementation risk.
- Fit for this project: High.
- Risks: can feel too plain if no small chart / sparkline / color encoding is added.

### Pattern B: Narrative + Evidence Rail

- Seen in: analyst note / dashboard hybrid, OpenBB linked context concept.
- User problem: user wants to read "what happened, why it matters, what to check next" in a natural order.
- Interaction shape: main left narrative with numbered market story; right slim rail for data trust, events, sentiment, source confidence.
- Data required: existing brief rows and interpretation cues.
- Why it matters: good for "market context" as explanation, not just metrics.
- Fit for this project: High.
- Risks: less dashboard-like; can become text-heavy if not edited tightly.

### Pattern C: Heatmap + Timeline Board

- Seen in: TradingView heatmaps and economic calendar.
- User problem: user wants true visual scanning of breadth / sector pressure / event timing.
- Interaction shape: sector heatmap first, event timeline second, selected-detail rows below.
- Data required: sector leadership snapshot, event calendar snapshot, data freshness, optional sparklines.
- Why it matters: this is the most "visual" option without relying on cards.
- Fit for this project: Medium-high.
- Risks: more implementation and QA work; local data coverage gaps become more visible.

## Patterns That Conflict With Current Boundaries

- Trade alerts, order tickets, auto rebalance.
- AI catalyst labels or price prediction copy.
- Direct provider fetch inside Streamlit render.
- Full user-customized workspace before stable taxonomy.

## Patterns That Should Remain Internal / Ops Only

- Raw job result tables.
- DB row counts as the main surface.
- Provider failure artifact details.
- Debug-only run-history diagnostics.

## Candidate Questions For Feature Opportunity

- Which direction should become the next Market Context UX pass: A tape, B narrative/rail, or C heatmap/timeline?
- Should we keep historical analog visible by default, or make it a row/detail under the chosen layout?
- How much visual color encoding is desirable before it starts to feel like a trading signal?
