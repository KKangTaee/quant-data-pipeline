# Risks

- Existing worktree has unrelated modified Overview / loader / test files. This task stages only ingestion module split files and task docs.
- The legacy `app.web.ingestion_console` import path must remain available until all internal callers and tests migrate.
