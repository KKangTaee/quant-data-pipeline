# Streamlit Ingestion Console Split Notes

## Decisions

- 7차는 every-large-file split이 아니라 7A Ingestion Console split으로 scoped down.
- `streamlit_app.py` keeps the runtime marker source so Overview, Ops, Guides, Glossary still share one process identity.
- Ingestion receives runtime context through `render_ingestion_page(...)` instead of reading shell globals.
- The split is behavior-preserving; deeper diagnostic service extraction is deliberately deferred.

## Observations

- Before split, `streamlit_app.py` mixed top navigation, glossary, Ingestion job guides, job scheduling, diagnostics, and result/history artifact rendering.
- After split, `streamlit_app.py` is 376 lines and `app/web/ingestion_console.py` is the focused Ingestion UI boundary.
- This prepares a cleaner follow-up path for moving read-only diagnostics into service/job facades without touching top-level navigation.
