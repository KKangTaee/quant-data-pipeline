# Design

Status: Completed
Last Verified: 2026-06-07

## Module Boundary

`app/web/backtest_compare.py` remains the Portfolio Mix Builder orchestration owner.
It still owns:

- Compare strategy selection and strategy-specific input forms
- execution service calls
- saved portfolio replay service calls
- weighted portfolio bundle creation
- Practical Validation handoff session state
- registry / run history handoff calls

`app/web/backtest_compare_components.py` owns Streamlit visual shell helpers:

- `render_portfolio_mix_builder_css`
- `render_portfolio_mix_flow_strip`
- `render_portfolio_mix_section_head`
- `render_component_result_overview_cards`
- small HTML escaping / status chip helpers used by those components

## Data Flow

```text
app/web/backtest_compare.py
  -> build rows / decide state / call services
  -> app/web/backtest_compare_components.py
  -> Streamlit visual shell render
```

No source payload or registry schema changes are introduced by this split.

## Compatibility Contract

The public page entrypoint remains:

- `render_compare_portfolio_workspace`

Existing session-state names stay unchanged:

- `backtest_compare_bundles`
- `backtest_weighted_bundle`
- `backtest_compare_source_context`
- `backtest_compare_workspace_mode`

## Relationship To Earlier Work

7차 split closed Ingestion Streamlit boundaries.
8차 split closed runtime large-file slices.
9차 starts the remaining Backtest Compare Streamlit file split, beginning with visual shell extraction.
