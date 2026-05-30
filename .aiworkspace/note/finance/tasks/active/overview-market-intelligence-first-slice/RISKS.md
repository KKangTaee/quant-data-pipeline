# Risks

| Risk | Handling |
| --- | --- |
| Sparse latest raw DB date | Service chooses effective date by minimum usable price rows. |
| Missing prices inside selected universe | Show returnable count and missing count. |
| Slow Overview load | Query only selected universe and selected dates. |
| User expects calendar ingestion in first slice | Keep Events tab as next-slice placeholder and document follow-up. |
