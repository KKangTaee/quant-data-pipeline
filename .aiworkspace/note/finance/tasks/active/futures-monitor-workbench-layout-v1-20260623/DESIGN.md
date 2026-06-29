# Futures Monitor Workbench Layout V1 Design

## Target Reading Flow

```text
Controls / edit inputs
  -> Workbench context bar
  -> Compact watch strip
  -> Market brief hero
  -> Weekly flow lane + score heat chips
  -> Evidence disclosure
  -> Chart workspace
  -> Provider diagnostics disclosure
```

## UI Ownership

| Area | Owns | Does Not Own |
|---|---|---|
| Context bar | selected group, symbol count, timeframe, candle interval, chart scope, data freshness, refresh action hint | provider rows, latest candle timestamp, raw run payload |
| Watch strip | selected symbols, contract title, 15m/60m move, symbol-level stale state | symbol picker, provider run status, raw rows |
| Market brief hero | scenario, one-sentence explanation, support metrics, evidence summary | raw score table, per-symbol daily rows |
| Weekly flow lane | dominant 1-week driver, support/temper grouping | complete raw weekly row table |
| Chart workspace | chart question, chartable count, symbol-level stale state | macro scenario, provider run result |
| Disclosures | evidence reading, raw tables, provider diagnostics | primary first-screen summary |

## Layout Choice

V1 stays in Streamlit and does not replace the multiselect with a fully interactive watch rail. Instead, it lowers the multiselect into a collapsed edit area and renders a read-only compact watch strip from the same stored snapshot.

## Acceptance Criteria

- Default surface reads as a coherent workbench, not a form followed by cards.
- Refresh details do not cover the market brief as a large floating popover.
- Symbol selection is not a large default multiselect; the default surface shows a compact watch strip.
- Macro Context starts with a market brief hero.
- Weekly flow shows ranking and interpretation, not equal-weight repeated cards.
- Chart workspace answers what the user should inspect in the charts.
