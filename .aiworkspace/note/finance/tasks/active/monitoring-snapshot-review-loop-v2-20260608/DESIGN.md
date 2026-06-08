# Monitoring Snapshot / Review Loop V2 Design

Status: Active
Last Updated: 2026-06-08

## Intake Classification

- Type: focused multi-step code implementation task.
- Primary owner: `finance-backtest-web-workflow`.
- Closeout owner: `finance-doc-sync`.
- Phase: no new phase. Current roadmap has no active phase, and this is an approved feature candidate implementation rather than phase management.

## Current Boundary Read

`Operations > Portfolio Monitoring` already owns explicit scenario update, performance recheck, selected strategy details, review signal policy, open issues, provider evidence, optional allocation drift check, and Decision Dossier read-only display.

Current docs say scenario results are session state unless the user explicitly saves a monitoring check record. `SELECTED_PORTFOLIO_MONITORING_LOG.jsonl` exists as the optional append-only registry target, while `saved/SELECTED_DASHBOARD_PORTFOLIOS.jsonl` remains reusable setup only.

## Proposed Data Shape

Monitoring snapshot rows should be compact and source-traceable:

- `monitoring_snapshot_id`
- `recorded_at`
- `record_type`: `MONITORING_SNAPSHOT` or `REVIEW_RECORD`
- `dashboard_portfolio_id`, `dashboard_portfolio_name`
- `selected_decision_ids`
- `scenario_signature`
- `scenario_snapshot`: compact portfolio metrics, benchmark delta, return / drawdown, target snapshot date, strategy summaries
- `drift_snapshot`: compact drift status / max drift / rows count / source
- `provider_freshness_snapshot`: compact status / stale symbols / missing coverage / evidence source
- `review_signal_snapshot`: status / route / primary reason
- `open_issue_snapshot`: issue count / top issues / next action
- `operator_note`
- `next_review_date`
- `no_live_boundary`

The row should not include full holdings, full macro series, raw provider response, raw price curves, or broker/account information.

## Implementation Direction

1. Add read / append helpers in `app/runtime/portfolio_selection_v2.py` for selected monitoring log rows.
2. Add pure helpers in `app/runtime/final_selected_portfolios.py` to build compact snapshot rows and compare latest / previous / current scenario.
3. Add focused service contract tests before implementation.
4. Wire `app/web/final_selected_portfolio_dashboard.py` after the portfolio-wide scenario result so the user can explicitly save or record a review.
5. Keep UI form separate from scenario update. No automatic append on replay success.
6. Update durable docs only after code behavior is verified.

## Risk Controls

- Use a caller-provided path in tests to avoid writing real registry files.
- Limit compact evidence with top issue / status summaries.
- Keep no-live copy near the save action and history comparison.
- Do not stage existing modified saved setup or generated QA artifacts.
