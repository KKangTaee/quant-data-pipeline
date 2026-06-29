# Risks

Status: Active
Last Updated: 2026-06-08

## Product Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Research output is mistaken for approved roadmap | High | Keep this bundle as evidence and recommendation only; create task / phase only after user approval. |
| Overview context is mistaken for investment signal | High | Preserve `Context Is Not Approval` copy and avoid PASS / BLOCKER / signal language. |
| `sub-dev` scope overlaps `main-dev` or `backtest-dev` | Medium | Keep this branch focused on Overview / Ingestion / Operations data analysis and visualization unless scope is re-approved. |
| Candidate Ops IA cleanup changes workflow expectations | Medium | Ask approval before moving, renaming, or demoting `Candidate Ops`. |
| Too many dashboards reduce clarity | Medium | Start with a narrow cockpit that summarizes existing read models before adding customization. |

## Technical Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Large `overview_dashboard.py` grows harder to maintain | Medium | Put new read-model logic in services/helpers and keep UI components focused. |
| New UI accidentally fetches providers during render | High | Route all refresh through `app/jobs/overview_actions.py` or Ingestion jobs. |
| Freshness states collapse into a single success label | High | Keep `Missing`, `Stale`, `Partial`, `Failed`, `Due`, and `OK` distinct. |
| yfinance futures are over-trusted | High | Keep provider caveats visible and do not present futures as exchange-grade. |
| Macro data is used without release / vintage caution | High | Add a source catalog and keep macro context out of validation pass logic unless PIT semantics are handled. |
| Session-only `Why It Moved` metadata becomes expected history | Medium | Do not add persistence until storage / freshness / provider policy is approved. |

## Research Gaps

| Gap | Why it matters | Follow-up |
| --- | --- | --- |
| No live Browser QA was performed | This research changed docs only, not UI. | Browser QA is required in the future implementation session. |
| No DB content snapshot was queried | Current local DB freshness could change the priority of Data Health targets. | Run app / DB smoke in the implementation task if UI priorities depend on current data. |
| External benchmark evidence is mostly official docs / product copy | Product pages may omit limitations. | Re-check current docs and, where needed, screenshots / trial behavior before copying any detailed workflow. |
| Future frontend platform choice remains open | Some heatmap / dashboard patterns may exceed Streamlit ergonomics. | Keep first implementation Streamlit-compatible; defer platform migration to approved UI platform research. |
| Source retention for compact metadata is undecided | Durable `Why It Moved` storage could affect DB schema and provider terms. | Open a separate policy research / task before V2 storage. |

## Verification Notes

- This bundle should pass the product research bundle checker.
- `git diff --check` should be run after documentation edits.
- No code tests are required for this research-only change unless helper scripts fail.
