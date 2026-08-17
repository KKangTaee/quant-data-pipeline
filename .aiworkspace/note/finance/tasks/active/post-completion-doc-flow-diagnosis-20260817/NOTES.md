# Notes

## Initial Findings

- Current top navigation: `Research / Portfolio / Data / Help`.
- Current top-level surfaces: `Today`, `Market Research`, `Institutional Holdings`, `Portfolio Lab`, `Portfolio Monitoring`, `Data Operations`, `Reference Center`.
- Market Research current views: `경기 국면`, `물가·정책`, `선물 매크로`, `심리`, `일정`, `S&P 500`, `변동 종목`, `개별 종목`.
- `OVERVIEW_DEEP_TAB_OPTIONS` still exists as a legacy fallback contract, but current Market Research navigation uses `MARKET_RESEARCH_VIEW_OPTIONS`.
- `Workspace > Overview` and old Overview tab names still appear in retained task records and some durable docs. They need classification before editing because some are historical or compatibility references.

## Tab / Surface Diagnosis

| Surface | Current route / grouping | Code owner | Diagnosis |
|---|---|---|---|
| Today | `Research > Today`, `/today` | `app/web/today_page.py`; `app/services/today.py`; Today React workbench | Current navigation target wiring is aligned. Today still deep-links to Market Research through the legacy `overview_tab` query parameter for compatibility. |
| Market Research | `Research > Market Research`, `/overview` | `app/web/overview/page.py`, `app/web/overview/navigation.py`, `app/services/overview/*`, view workbenches | Code baseline is 3-family / 8-view. Durable docs still contain many current-behavior statements using `Workspace > Overview`, `Market Context`, and `Market Movers` as route names. |
| Institutional Holdings | `Research > Institutional Holdings`, `/institutional-portfolios` | `app/web/institutional_portfolios.py`, `app/services/institutional_*`, `finance/loaders/institutional_13f.py` | Current route and Project Map are aligned. Reference Center service still uses `Institutional Portfolios` as the surface label, while app navigation uses `Institutional Holdings`. |
| Portfolio Lab | `Portfolio > Portfolio Lab`, `/backtest` | `app/web/backtest_page.py`, `app/web/backtest_workflow_shell.py`, stage modules / services | Current 3-stage shell remains `Backtest Analysis -> Practical Validation -> Final Review`. Docs are mostly aligned, but some old backtest flow docs still route selected monitoring to `Operations > Portfolio Monitoring`. |
| Portfolio Monitoring | `Portfolio > Portfolio Monitoring`, `/selected-portfolio-dashboard` | `app/web/final_selected_portfolio_dashboard.py`, `app/services/portfolio_monitoring/*`, `app/runtime/backtest/read_models/final_selected_portfolios.py` | User-facing route is now Portfolio group. Legacy file names and saved JSONL names intentionally keep `Selected Dashboard`. Canonical docs should describe current route as `Portfolio > Portfolio Monitoring`, not `Operations > Portfolio Monitoring`, except when explaining legacy names. |
| Data Operations | `Data > Data Operations`, `/ingestion` | `app/web/ingestion_console.py` compatibility facade, `app/web/ingestion/*`, `app/jobs/ingestion_jobs.py`, `app/services/ingestion_diagnostics.py` | Code has a five-section purpose-first workbench: `데이터 준비`, `공식 파일`, `문제 복구`, `실행 이력`, `고급 도구`. Several durable docs still say `Workspace > Ingestion`; runbook steps should be updated to current user-facing route while preserving compatibility module names. |
| Reference Center | `Help > Reference Center`, `/reference` | `app/web/reference_center.py`, `app/services/reference_center.py`, React bridge | Page shell is current and merged. Service/test copy still defines required surfaces as `Overview`, `Institutional Portfolios`, `Ingestion`, etc.; this is a code-contract drift candidate if product labels should match the current top nav. |

## Must Fix Candidates

- `docs/architecture/README.md`: `Current Surface Notes` still says `Workspace > Overview` current primary tabs are `Market Context`, `Market Movers`, `Futures Macro`, `Sentiment`, `Events`. Current code is `Research > Market Research` with 3-family / 8-view.
- `docs/architecture/SYSTEM_BOUNDARIES.md`: product surface sections still use `Workspace > Ingestion`, `Workspace > Overview`, `Workspace > Institutional Portfolios`, `Operations > Portfolio Monitoring`. These are current-boundary sections, so they should use current route names and mention old names only as legacy compatibility.
- `docs/architecture/DATA_DB_PIPELINE_FLOW.md` and `docs/data/DATA_FLOW_MAP.md`: data flow text repeatedly routes current Market Research / Data Operations evidence through `Workspace > Overview` and `Workspace > Ingestion`.
- `docs/flows/PORTFOLIO_SELECTION_FLOW.md` and `docs/flows/BACKTEST_UI_FLOW.md`: current monitoring flow still says `Operations > Portfolio Monitoring`; app navigation now places this under `Portfolio > Portfolio Monitoring`.
- `docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md` and `docs/runbooks/EDGAR_FINANCIAL_STATEMENT_REFRESH.md`: operational steps still tell the user to open `Workspace > Overview` / `Workspace > Ingestion`; these should become `Research > Market Research` / `Data > Data Operations`.
- `app/services/reference_center.py` and `tests/test_reference_center.py`: Reference Center visible surface labels and drift test still use old labels. If the intended product copy is the top-nav vocabulary, this needs code + tests, not only docs.

## Candidate Cleanup

- `docs/flows/README.md`: main user flow still says Today opens `Market Context / Market Movers / Portfolio Monitoring 기존 화면`; the current first-hop wording should be `Market Research` and `Portfolio Monitoring`.
- `docs/data/README.md`, `docs/data/STORAGE_GOVERNANCE.md`, `docs/data/TABLE_SEMANTICS.md`, `docs/architecture/SCRIPT_STRUCTURE_MAP.md`, `docs/architecture/PORTFOLIO_MONITORING_REACT_COMMAND_CENTER.md`, and `docs/GLOSSARY.md` contain old labels. Some are probably explanatory compatibility references, but current-route sections need targeted review.
- `docs/runbooks/AUTOMATION_SCRIPTS.md`: `Overview` scheduled-refresh naming may remain valid for CLI/module names, but user-facing troubleshooting should point to `Market Research` and `Data Operations`.

## Intentional Retained History / Compatibility

- Completed task records in `tasks/active/README.md` and old `STATUS_MANIFEST.md` sections preserve historical routes and should not be bulk-edited.
- Code module and URL compatibility names such as `/overview`, `app/web/overview/*`, `OVERVIEW_DEEP_TAB_OPTIONS`, `overview_tab`, and `app/web/ingestion_console.py` are retained contracts unless a separate migration is approved.
- `app/web/final_selected_portfolio_dashboard.py` and `.aiworkspace/note/finance/saved/SELECTED_DASHBOARD_PORTFOLIOS.jsonl` keep legacy names intentionally while user-facing navigation says `Portfolio Monitoring`.
- `Futures Monitor`, `Sector / Industry`, `Data Health`, and old `Candidate Ops` should remain only where explicitly described as soft-removed, fallback, old task history, or retained backend.

## Open Questions

- Resolved 2026-08-17: durable docs that describe current behavior now use current user-facing routes. Retained task history, compatibility module names, URL slugs, CLI names, and saved setup file names were not renamed.
- Resolved 2026-08-17: canonical docs now describe monitoring as `Portfolio > Portfolio Monitoring`; legacy `/selected-portfolio-dashboard`, `final_selected_portfolio_dashboard.py`, and selected-dashboard saved setup names remain compatibility contracts.
- Resolved 2026-08-17: Reference Center user-facing surface labels were migrated to `Market Research / Data Operations / Institutional Holdings` in both service payload and tests while keeping internal destination keys.

## 3차 Cleanup Result

- Architecture docs now describe current screen boundaries with `Research > Market Research`, `Data > Data Operations`, `Research > Institutional Holdings`, and `Portfolio > Portfolio Monitoring` first. Internal `overview_*` modules are mentioned only as compatibility / owner names.
- Data docs now route market movers, futures macro, sentiment, EDGAR, listing refresh, and Portfolio Monitoring evidence through current screen names.
- Flow docs now separate current Portfolio / Data navigation from hidden compatibility pages for old Backtest Run History and Candidate Library.
- Runbooks now give user steps with current Market Research / Data Operations / Portfolio Monitoring paths. `OVERVIEW_MARKET_INTELLIGENCE.md` was retitled as a Market Research runbook while preserving the filename and internal CLI/module names.
- Reference Center catalog and drift tests now assert the current surface vocabulary. Lowercase legacy search keywords such as `overview` and `ingestion` remain as search aliases, not visible surface labels.
- Top-level docs did not need structure changes. Roadmap received only three stale `Overview` user-facing wording fixes; Product Direction / Project Map / Index already matched the current navigation baseline.
