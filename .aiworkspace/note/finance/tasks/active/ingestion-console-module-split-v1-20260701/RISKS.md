# Risks

- Existing worktree has unrelated modified Overview / loader / test files. This task stages only ingestion module split files and task docs.
- The legacy `app.web.ingestion_console` import path must remain available until all internal callers and tests migrate.
- `app/jobs/ingestion_jobs.py` still owns the domain job wrappers. This round split only shared common helpers; future work can split price / statements / providers / macro / events / lifecycle job modules.
- `app/web/ingestion/sections.py` uses runtime page-helper binding to keep behavior unchanged while moving large section bodies. Future cleanup can replace that compatibility bridge with explicit card/helper modules.
