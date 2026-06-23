# Futures Monitor Dedup UX V1 Design

## Current Duplication

- Live 1m freshness appears in the command center, live signal cards, warning, state count chip, and each chart card.
- Top move appears in the command center and live signal cards.
- Provider run status / rows appears in the command center, live signal cards, and diagnostics.
- Macro scenario appears in both the signal strip and hero.
- Macro scores appear in the hero evidence line, score chip lane, and evidence-reading cards.
- Historical validation appears in the Macro signal strip and again in the evidence expander.

## Ownership Model

| Information | Default Owner | Secondary Location |
|---|---|---|
| selected group / symbol count / refresh mode | command center | controls only |
| live freshness / action needed | command center | symbol card local state |
| provider run rows / latest candle | diagnostics | not default surface |
| top move | command center | not live summary card |
| macro scenario | hero | not signal-card duplicate |
| evidence strength / validation summary | compact support strip | detailed expander |
| macro score chips | score lane | evidence cards explain per-symbol meaning |
| symbol-level stale age | chart card header | not repeated as live status cards |

## UI Direction

The default page should read:

1. Controls.
2. Compact command center: watch set, data state / next action, top move.
3. Macro Context: current interpretation, compact support facts, recent 1-week backdrop, score chips.
4. Evidence expander: interpretation cards first, raw tables after.
5. Live chart section: section header, optional stale alert, chart cards.
6. Diagnostics expander: provider run / raw rows.

## Test Direction

Use Streamlit-free helper functions where possible:

- `_futures_command_summary_items(snapshot, ...)` should not include provider rows in default items.
- `_futures_live_summary_line(snapshot, ...)` should summarize chart context without repeating top move / provider run.
- `_macro_support_items(macro)` should exclude scenario because the hero owns it.

The tests protect the information ownership model without needing full Streamlit rendering.
