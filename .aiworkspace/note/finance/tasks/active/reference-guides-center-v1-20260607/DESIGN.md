# Design

## Target UX

```text
Reference > Guides
  -> Reference Center landing
     -> task cards
     -> current product flow map
     -> quick status / concept lookup
     -> troubleshooting playbooks
  -> Portfolio Selection Journey
     -> existing route selector
     -> 1~4 stage timeline
     -> flow / checkpoints / decision gates / drawer
```

## File Boundary

| File | Role |
|---|---|
| `app/services/reference_guides_catalog.py` | Streamlit-free guide catalog for task cards, journeys, concepts, records, troubleshooting. |
| `app/web/reference_guides.py` | Streamlit rendering, layout state, GraphViz fallback, current portfolio guide components. |
| `tests/test_reference_guides_catalog.py` | Catalog contract tests. |
| `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md` | Durable Reference Guide flow summary after implementation. |

## Data Model Direction

- Use plain dict/list rows to stay consistent with existing Streamlit dataframe rendering.
- Catalog functions must be importable without importing Streamlit.
- Stable keys are required for task cards and journeys so later contextual links can target them.

## Rendering Direction

- Use compact operational cards instead of a marketing hero.
- Keep 8px radius and restrained colors.
- Do not nest cards inside cards.
- Use tabs or segmented control for Reference modes:
  - `Reference Center`
  - `Portfolio Selection Journey`
- Keep runtime/git snapshot in compact chips and `System status` expander.
