# Backtest Analysis Direction Reset 4C Plan

## Why

3A~4B added several evidence / governance / workbench panels at the top of Backtest Analysis. They are useful as strategy development references, but they are not the core purpose of this branch.

The branch purpose is to improve backtest strategies, mature prototypes, and support new strategy development when needed. Backtest Analysis should therefore open with actual strategy execution, comparison, and candidate creation rather than a stack of evidence panels.

## Scope

- Reorder Backtest Analysis so Single Strategy / Portfolio Mix Builder remains the default working flow.
- Move Reference help and 3A~4B evidence / governance panels behind an explicit strategy development reference control.
- Keep advanced panels available for strategy development review, but hidden from the basic flow by default.
- Add a Streamlit-free read model that classifies the reference panels and records their default placement.
- Convert new / wrapper user-facing copy to Korean-first wording. Existing English titles may remain as secondary labels.

## Out Of Scope

- Strategy runtime behavior changes
- DB schema changes
- registry / saved JSONL / run history rewrite
- generated artifact commits
- provider / FRED direct fetch
- current-candidate promotion implementation
- Practical Validation / Final Review / Portfolio Monitoring behavior changes

## Completion Criteria

- Focused tests prove the research/reference board is Streamlit-free, hidden by default, and classifies all seven items.
- Backtest Analysis renders execution / comparison mode before reference/evidence panels.
- Browser QA confirms the default screen no longer starts with the evidence panel stack.
- Durable docs reflect that evidence panels are advanced strategy development references, not the default Backtest Analysis flow.
