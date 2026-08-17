# Risks

## Open Risks

- Retained task records intentionally preserve historical names. A blind replacement of `Workspace > Overview`, `Operations`, `Selected Portfolio Dashboard`, or `Futures Monitor` would damage audit history.
- Some legacy labels are code compatibility contracts rather than current navigation. They should stay if tests or old saved payload replay need them.
- Generated QA screenshots are unrelated local artifacts and must remain unstaged unless explicitly requested.
- Reference Center label cleanup is a code contract change, because `tests/test_reference_center.py` currently asserts the older surface names. Handle it separately from pure doc text refresh.
- `Overview` remains a module, URL, job, and registry naming prefix in several places. User-facing docs can say `Market Research`, but code-owner docs may need both: current route first, legacy/internal name in parentheses.
- `Portfolio Monitoring` still uses `/selected-portfolio-dashboard`, `final_selected_portfolio_dashboard.py`, and `SELECTED_DASHBOARD_PORTFOLIOS.jsonl`. Do not rename files or persisted saved setup during documentation cleanup.

## Closeout Notes

- 2026-08-17 cleanup intentionally did not rename route keys, module paths, URL slugs, JSONL file names, registries, saved setup files, or completed task history.
- Lowercase `overview` / `ingestion` search aliases may remain in Reference Center keywords to preserve search discoverability for old vocabulary.
- If future product navigation actually renames `/overview`, `/ingestion`, or `/selected-portfolio-dashboard`, open a separate migration task with URL compatibility, deep-link, saved payload, and doc-link repair checks.
