# Design

## Direction

```text
app/services/reference_contextual_help.py
  -> Streamlit-free surface help catalog
  -> lookup helpers

app/web/reference_contextual_help.py
  -> small Streamlit expander renderer
  -> Reference / Glossary links only

owner screens
  -> render_reference_contextual_help("surface_key")
```

## First Surface Set

- `backtest_analysis`
- `practical_validation`
- `final_review`
- `operations_console`
- `portfolio_monitoring`

## Data Shape

Each contextual help item has:

- `surface_key`
- `surface`
- `title`
- `summary`
- `guide_focus`
- `glossary_terms`
- `next_checks`
- `boundaries`
- `links`

## Boundary

This is a read-only navigation / explanation feature.
It must not execute jobs, mutate session registry state, write saved setup, trigger provider fetch, or alter validation / selected-route gate decisions.
