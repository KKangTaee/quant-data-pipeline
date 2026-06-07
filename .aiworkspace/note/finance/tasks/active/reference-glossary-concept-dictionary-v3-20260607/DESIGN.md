# Design

## Current State

- `Reference > Guides` uses `app/services/reference_guides_catalog.py`.
- `Reference > Glossary` is rendered inside `app/web/streamlit_app.py` and reads `.aiworkspace/note/finance/docs/GLOSSARY.md` directly.
- Guides concept rows and Glossary markdown sections can drift because they are separate sources.

## Direction

```text
app/services/reference_glossary_catalog.py
  -> curated concept dictionary
  -> markdown glossary section parser
  -> shared search helper

app/services/reference_guides_catalog.py
  -> imports curated concept dictionary

app/web/reference_guides.py
  -> renders shared concept rows

app/web/streamlit_app.py
  -> renders curated concepts + markdown glossary sections
```

## Data Shape

Each curated concept row has:

- `term`
- `category`
- `plain_meaning`
- `owner_screen`
- `progress_implication`
- `where_to_fix`
- `source`
- `keywords`

## Boundary

This remains a read-only reference feature. It does not modify markdown docs, registries, saved setup, run history, DB tables, or provider data.
